#!/usr/bin/env python3
"""Run the compute-heavy representation and pointwise-geometry pipeline.

This wrapper keeps every path explicit, records a content-addressed run
configuration, and reuses only outputs produced with exactly that
configuration.  It intentionally does not download or redistribute Pile text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = REPO_ROOT / "src" / "full_pipeline"
MUTABLE_REVISIONS = {"main", "master", "latest", "dev", "develop"}


def csv_ints(value: str) -> str:
    """Normalize a comma/space-separated integer list."""
    parts = [part for part in value.replace(",", " ").split() if part]
    if not parts:
        raise argparse.ArgumentTypeError("expected at least one integer")
    try:
        normalized = [str(int(part)) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated integers") from exc
    if any(int(part) <= 0 for part in normalized):
        raise argparse.ArgumentTypeError("all values must be positive")
    return ",".join(normalized)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True, help="Hugging Face model identifier")
    parser.add_argument("--revision", required=True, help="Immutable model commit or tag")
    parser.add_argument("--seen-file", type=Path, required=True)
    parser.add_argument("--unseen-file", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--layers", type=csv_ints, required=True)
    parser.add_argument("--dtype", choices=("float32", "float16", "bfloat16"), default="float16")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reference-size", type=int, default=15_000)
    parser.add_argument("--k", type=int, default=1_000)
    parser.add_argument("--seen-count", type=int, default=17_000)
    parser.add_argument("--query-count", type=int, default=2_000)
    parser.add_argument("--extract-batch-size", type=int, default=1)
    parser.add_argument("--mle-chunk-size", type=int, default=128)
    parser.add_argument("--fci-chunk-size", type=int, default=32)
    parser.add_argument("--device", default=None, help="Explicit torch device, for example cuda:0")
    parser.add_argument("--device-map-auto", action="store_true")
    parser.add_argument("--skip-lm-head", action="store_true")
    parser.add_argument(
        "--allow-mutable-revision",
        action="store_true",
        help="Allow a branch name such as main; discouraged because the run is not immutable.",
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=("extract", "mle_ess", "fci", "materialize"),
        default=("extract", "mle_ess", "fci", "materialize"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for name in (
        "seed",
        "reference_size",
        "k",
        "seen_count",
        "query_count",
        "extract_batch_size",
        "mle_chunk_size",
        "fci_chunk_size",
    ):
        if getattr(args, name) <= 0 and name != "seed":
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.seen_count < args.reference_size + args.query_count:
        parser.error("--seen-count must be at least reference-size + query-count")
    if args.k >= args.reference_size:
        parser.error("--k must be smaller than --reference-size")
    if args.revision.lower() in MUTABLE_REVISIONS and not args.allow_mutable_revision:
        parser.error(
            "the requested revision is mutable; provide an immutable commit/tag or "
            "pass --allow-mutable-revision to acknowledge the provenance limitation"
        )
    return args


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: Sequence[str], *, dry_run: bool) -> None:
    rendered = subprocess.list2cmdline([str(item) for item in command])
    print(f"+ {rendered}", flush=True)
    if not dry_run:
        subprocess.run([str(item) for item in command], check=True, cwd=REPO_ROOT)


def require_file(path: Path, description: str, *, dry_run: bool) -> None:
    if dry_run:
        return
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"missing {description}: {path}")


def main() -> None:
    args = parse_args()
    seen_file = args.seen_file.expanduser().resolve()
    unseen_file = args.unseen_file.expanduser().resolve()
    output_root = args.output_root.expanduser().resolve()
    require_file(seen_file, "seen JSONL", dry_run=args.dry_run)
    require_file(unseen_file, "unseen JSONL", dry_run=args.dry_run)

    reps_dir = output_root / "representations"
    mle_dir = output_root / "mle_ess"
    fci_dir = output_root / "fci"
    sentence_dir = output_root / "sentence_level"
    config_path = output_root / "run_config.json"
    config = {
        "schema_version": 1,
        "model_name": args.model_name,
        "revision": args.revision,
        "layers": [int(value) for value in args.layers.split(",")],
        "dtype": args.dtype,
        "seed": args.seed,
        "reference_size": args.reference_size,
        "k": args.k,
        "seen_count": args.seen_count,
        "query_count": args.query_count,
        "seen_sha256": None if args.dry_run else sha256_file(seen_file),
        "unseen_sha256": None if args.dry_run else sha256_file(unseen_file),
        "endpoint_pooling": "final_non_padding_token",
        "fci_backend": "pyfci_local",
        "pyfci_random_seed": args.seed,
    }
    canonical = json.dumps(config, indent=2, sort_keys=True) + "\n"
    if not args.dry_run:
        output_root.mkdir(parents=True, exist_ok=True)
        if config_path.exists() and config_path.read_text(encoding="utf-8") != canonical:
            raise RuntimeError(
                f"{output_root} contains outputs for a different configuration; "
                "choose a new --output-root"
            )
        config_path.write_text(canonical, encoding="utf-8")

    python = sys.executable
    if "extract" in args.stages:
        command = [
            python,
            PIPELINE_DIR / "extract_last_token_representations.py",
            "--model_name",
            args.model_name,
            "--revision",
            args.revision,
            "--seen_file",
            seen_file,
            "--unseen_file",
            unseen_file,
            "--seen_target_sentences",
            str(args.seen_count),
            "--unseen_target_sentences",
            str(args.query_count),
            "--batch_size",
            str(args.extract_batch_size),
            "--dtype",
            args.dtype,
            "--seed",
            str(args.seed),
            "--layers",
            args.layers,
            "--output_dir",
            reps_dir,
            "--save_combined_pt",
        ]
        if args.device is not None:
            command.extend(("--device", args.device))
        if args.device_map_auto:
            command.append("--device_map_auto")
            command.extend(("--offload_folder", output_root / "offload"))
        if args.skip_lm_head:
            command.append("--skip_lm_head")
        run(command, dry_run=args.dry_run)

    seen_pt = reps_dir / "seen_last_token_reps.pt"
    unseen_pt = reps_dir / "unseen_last_token_reps.pt"
    if any(stage in args.stages for stage in ("mle_ess", "fci", "materialize")):
        require_file(seen_pt, "seen representations", dry_run=args.dry_run)
        require_file(unseen_pt, "unseen representations", dry_run=args.dry_run)

    if "mle_ess" in args.stages:
        run(
            [
                python,
                PIPELINE_DIR / "compute_pointwise_mle_ess.py",
                "--seen_pt",
                seen_pt,
                "--unseen_pt",
                unseen_pt,
                "--output_dir",
                mle_dir,
                "--reference_count",
                str(args.reference_size),
                "--eval_known_count",
                str(args.query_count),
                "--eval_unknown_count",
                str(args.query_count),
                "--reference_sizes",
                str(args.reference_size),
                "--k_values",
                str(args.k),
                "--layers",
                args.layers,
                "--seed",
                str(args.seed),
                "--chunk_size",
                str(args.mle_chunk_size),
                "--unseen_output_name",
                "eval_unknown",
                "--include_ess",
                "--save_combined_pt",
            ],
            dry_run=args.dry_run,
        )

    reference_setup = mle_dir / "combined_pointwise_mle.pt"
    if any(stage in args.stages for stage in ("fci", "materialize")):
        require_file(reference_setup, "MLE/ESS reference setup", dry_run=args.dry_run)

    if "fci" in args.stages:
        run(
            [
                python,
                PIPELINE_DIR / "compute_pointwise_fci.py",
                "--seen_pt",
                seen_pt,
                "--unseen_pt",
                unseen_pt,
                "--output_dir",
                fci_dir,
                "--reference_count",
                str(args.reference_size),
                "--eval_known_count",
                str(args.query_count),
                "--reference_sizes",
                str(args.reference_size),
                "--k_values",
                str(args.k),
                "--layers",
                args.layers,
                "--seed",
                str(args.seed),
                "--chunk_size",
                str(args.fci_chunk_size),
                "--reuse_reference_setup_pt",
                reference_setup,
                "--fci_backend",
                "pyfci_local",
                "--pyfci_random_seed",
                str(args.seed),
                "--save_combined_pt",
            ],
            dry_run=args.dry_run,
        )

    known_mle = mle_dir / "eval_known_pointwise_mle_long.parquet"
    unknown_mle = mle_dir / "eval_unknown_pointwise_mle_long.parquet"
    known_fci = fci_dir / "eval_known_pointwise_fci_long.parquet"
    unknown_fci = fci_dir / "eval_unknown_pointwise_fci_long.parquet"
    if "materialize" in args.stages:
        for path, label in (
            (known_mle, "known MLE/ESS table"),
            (unknown_mle, "unknown MLE/ESS table"),
            (known_fci, "known FCI table"),
            (unknown_fci, "unknown FCI table"),
        ):
            require_file(path, label, dry_run=args.dry_run)
        run(
            [
                python,
                PIPELINE_DIR / "materialize_sentence_metrics.py",
                "--mle_ess_known_long",
                known_mle,
                "--mle_ess_unknown_long",
                unknown_mle,
                "--fci_known_long",
                known_fci,
                "--fci_unknown_long",
                unknown_fci,
                "--output_dir",
                sentence_dir,
                "--known_prefix",
                "eval_known",
                "--unknown_prefix",
                "eval_unknown",
                "--layers",
                args.layers,
                "--k_values",
                str(args.k),
                "--ref_size",
                str(args.reference_size),
                "--overwrite",
            ],
            dry_run=args.dry_run,
        )
    print(f"Pipeline outputs: {output_root}")


if __name__ == "__main__":
    main()
