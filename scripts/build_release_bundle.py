#!/usr/bin/env python3
"""Build the privacy-safe, text-free data bundle used by the analyses.

This is a release-maintainer utility. It reads the large internal experiment
tree supplied with ``--source-root`` and emits only compact derived tables.
Input text is used in memory to validate row alignment and to compute SHA-256
fingerprints; text and provenance paths are never written to the release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


BUNDLE_VERSION = 1
LAYERS_BY_MODEL = {
    "pythia": (2, 16, 31),
    "qwen": (2, 14, 27),
    "apertus": (2, 16, 31),
}
EXPECTED_QUERY_INDICES = frozenset(range(2_000))
FORBIDDEN_OUTPUT_COLUMNS = frozenset(
    {
        "identifier",
        "recovered_text",
        "text",
        "source_file",
        "source_kind",
        "line_index",
        "query_source_index",
        "reference_setup_signature",
        "query_selection_signature",
        "split_setup_signature",
        "model_name",
        "label",
        "label_name",
        "sample_kind",
    }
)


@dataclass(frozen=True)
class Artifact:
    """One input artifact, identified publicly only by a neutral logical ID."""

    logical_id: str
    relative_path: str
    model_family: str | None = None
    layer: int | None = None
    checkpoint: str | None = None
    checkpoint_order: int | None = None
    training_step: int | None = None
    training_tokens_billion: float | None = None
    expected_revision: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        required=True,
        type=Path,
        help="Root of the internal experiment tree (never recorded in outputs).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Release repository root (default: parent of this script directory).",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parquet_path(directory: str, layer: int, prefix: str = "") -> str:
    filename = (
        f"{prefix}eval_known_layer{layer}_k1000_ref15000_sentence_level.parquet"
    )
    return f"{directory}/{filename}"


def input_artifacts() -> tuple[Artifact, list[Artifact], list[Artifact]]:
    """Return feature, main-model, and checkpoint artifact specifications."""

    feature = Artifact(
        logical_id="features.profiling-ud-frequency",
        relative_path="outputs/eval_known_feature60_plus_frequency_for_predict.tsv",
    )

    main: list[Artifact] = []
    main_specs = (
        (
            "pythia",
            "outputs_6.9/seen_unseen_pythia69b_mle_ess_fci_k1000_ref15000_layers2_16_31_sentence_level",
            "main",
        ),
        (
            "qwen",
            "qwen_results/outputs/local_seen_unseen_qwen2p5_7b_mle_ess_pyfci_ref15000_k1000_layers2_14_27_sentence_level",
            "main",
        ),
        (
            "apertus",
            "apertus_results/outputs/apertus8b_checkpoints/step2627139-tokens15T/sentence_level",
            "96982d7c559fab9c2b19b6934ad28499c5c341e9",
        ),
    )
    for family, directory, revision in main_specs:
        for layer in LAYERS_BY_MODEL[family]:
            main.append(
                Artifact(
                    logical_id=f"main.{family}.layer-{layer}",
                    relative_path=parquet_path(directory, layer),
                    model_family=family,
                    layer=layer,
                    expected_revision=revision,
                )
            )

    checkpoints: list[Artifact] = []
    pythia_specs = (
        (
            "step-000512",
            0,
            512,
            1.1,
            "step512",
            "outputs_6.9_checkpoints/pythia_checkpoint_k1000_selected_layers/sentence_level",
            "step_512_",
        ),
        (
            "step-008000",
            1,
            8_000,
            16.8,
            "step8000",
            "outputs_6.9_checkpoints/pythia_checkpoint_k1000_selected_layers/sentence_level",
            "step_8000_",
        ),
        (
            "step-021000",
            2,
            21_000,
            44.0,
            "step21000",
            "outputs_6.9_checkpoints/pythia69b_deduped_step21000/selected_k1000/sentence_level",
            "",
        ),
        (
            "step-055000",
            3,
            55_000,
            115.0,
            "step55000",
            "outputs_6.9_checkpoints/pythia69b_deduped_step55000/selected_k1000/sentence_level",
            "",
        ),
        (
            "final-main",
            4,
            143_000,
            300.0,
            "main",
            "outputs_6.9/seen_unseen_pythia69b_mle_ess_fci_k1000_ref15000_layers2_16_31_sentence_level",
            "",
        ),
    )
    for checkpoint, order, step, tokens, revision, directory, prefix in pythia_specs:
        for layer in LAYERS_BY_MODEL["pythia"]:
            suffix = "_with_pyfci" if step in {512, 8_000} else ""
            path = parquet_path(directory, layer, prefix=prefix)
            if suffix:
                path = path.removesuffix(".parquet") + suffix + ".parquet"
            checkpoints.append(
                Artifact(
                    logical_id=f"checkpoint.pythia.{checkpoint}.layer-{layer}",
                    relative_path=path,
                    model_family="pythia",
                    layer=layer,
                    checkpoint=checkpoint,
                    checkpoint_order=order,
                    training_step=step,
                    training_tokens_billion=tokens,
                    expected_revision=revision,
                )
            )

    apertus_specs = (
        (
            "tokens-000210b",
            0,
            50_000,
            210.0,
            "step50000-tokens210B",
            "4d1413654b70c14a00c6c3179fc227b5d155ce9e",
        ),
        (
            "tokens-000420b",
            1,
            100_000,
            420.0,
            "step100000-tokens420B",
            "f559808126bff0db3188ffb2dcc13e5c9423cac5",
        ),
        (
            "tokens-000840b",
            2,
            200_000,
            840.0,
            "step200000-tokens840B",
            "3294c7d4da373758a57636ef53ea300d9d6e2ffa",
        ),
        (
            "tokens-001680b",
            3,
            400_000,
            1_680.0,
            "step400000-tokens1680B",
            "f946ef40c610484827fbeaab30efe873d0590e70",
        ),
        (
            "tokens-003570b",
            4,
            850_000,
            3_570.0,
            "step850000-tokens3570B",
            "ffefc2452dad49c3f7e88af5fb4d8e9e75bf4e97",
        ),
        (
            "tokens-007232b",
            5,
            1_700_000,
            7_232.0,
            "step1700000-tokens7232B",
            "4cd1cd1ff73cbae8bff0b7da149b0a6108d69602",
        ),
        (
            "tokens-015000b",
            6,
            2_627_139,
            15_000.0,
            "step2627139-tokens15T",
            "96982d7c559fab9c2b19b6934ad28499c5c341e9",
        ),
    )
    for checkpoint, order, step, tokens, dirname, revision in apertus_specs:
        directory = (
            "apertus_results/outputs/apertus8b_checkpoints/"
            f"{dirname}/sentence_level"
        )
        for layer in LAYERS_BY_MODEL["apertus"]:
            checkpoints.append(
                Artifact(
                    logical_id=f"checkpoint.apertus.{checkpoint}.layer-{layer}",
                    relative_path=parquet_path(directory, layer),
                    model_family="apertus",
                    layer=layer,
                    checkpoint=checkpoint,
                    checkpoint_order=order,
                    training_step=step,
                    training_tokens_billion=tokens,
                    expected_revision=revision,
                )
            )

    return feature, main, checkpoints


def require_input_files(source_root: Path, artifacts: Iterable[Artifact]) -> None:
    missing = [item.logical_id for item in artifacts if not (source_root / item.relative_path).is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing required logical artifacts: " + ", ".join(sorted(missing))
        )


def require_columns(frame: pd.DataFrame, required: set[str], logical_id: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{logical_id}: missing columns {sorted(missing)}")


def validate_query_table(frame: pd.DataFrame, logical_id: str) -> None:
    if len(frame) != len(EXPECTED_QUERY_INDICES):
        raise ValueError(f"{logical_id}: expected 2000 rows, found {len(frame)}")
    query_index = pd.to_numeric(frame["query_index"], errors="raise").astype("int64")
    if query_index.duplicated().any():
        raise ValueError(f"{logical_id}: duplicate query_index values")
    if frozenset(query_index.tolist()) != EXPECTED_QUERY_INDICES:
        raise ValueError(f"{logical_id}: query_index is not exactly 0..1999")


def read_features(path: Path) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    raw = pd.read_csv(path, sep="\t")
    metadata_columns = {"identifier", "recovered_row_index", "recovered_text"}
    require_columns(raw, metadata_columns, "features.profiling-ud-frequency")
    predictor_columns = [column for column in raw.columns if column not in metadata_columns]
    if len(predictor_columns) != 46:
        raise ValueError(f"Expected 46 predictors, found {len(predictor_columns)}")
    non_numeric = [
        column
        for column in predictor_columns
        if not (
            pd.api.types.is_numeric_dtype(raw[column])
            or pd.api.types.is_bool_dtype(raw[column])
        )
    ]
    if non_numeric:
        raise TypeError(f"Non-numeric predictor columns: {non_numeric}")

    query_index = pd.to_numeric(raw["recovered_row_index"], errors="raise").astype("int64")
    if query_index.duplicated().any():
        raise ValueError("Feature query_index contains duplicates")
    if not set(query_index.tolist()).issubset(EXPECTED_QUERY_INDICES):
        raise ValueError("Feature query_index is outside 0..1999")
    if raw["recovered_text"].isna().any():
        raise ValueError("Feature input has missing alignment text")

    alignment_text = pd.Series(
        raw["recovered_text"].astype(str).to_numpy(),
        index=query_index.to_numpy(),
        name="alignment_text",
    ).sort_index()
    release = raw[predictor_columns].copy()
    release.insert(0, "text_sha256", raw["recovered_text"].astype(str).map(text_fingerprint))
    release.insert(0, "query_index", query_index)
    release = release.sort_values("query_index", kind="stable").reset_index(drop=True)
    if release.isna().any().any():
        raise ValueError("Feature release table contains missing values")
    stats = {
        "rows": int(len(release)),
        "predictors": len(predictor_columns),
        "query_index_min": int(release["query_index"].min()),
        "query_index_max": int(release["query_index"].max()),
        "unique_query_indices": int(release["query_index"].nunique()),
        "text_fingerprints": int(release["text_sha256"].nunique()),
    }
    return release, alignment_text, stats


def read_target(
    path: Path,
    artifact: Artifact,
    alignment_text: pd.Series,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = pd.read_parquet(path)
    required = {
        "query_index",
        "text",
        "reference_size",
        "k",
        "pointwise_id",
        "pointwise_ess",
        "pointwise_fci_id",
        "revision",
    }
    require_columns(raw, required, artifact.logical_id)
    validate_query_table(raw, artifact.logical_id)

    revisions = raw["revision"].dropna().astype(str).unique().tolist()
    if revisions != [artifact.expected_revision]:
        raise ValueError(
            f"{artifact.logical_id}: revision {revisions!r} does not match expected revision"
        )
    if raw["reference_size"].nunique() != 1 or int(raw["reference_size"].iloc[0]) != 15_000:
        raise ValueError(f"{artifact.logical_id}: expected reference_size=15000")
    if raw["k"].nunique() != 1 or int(raw["k"].iloc[0]) != 1_000:
        raise ValueError(f"{artifact.logical_id}: expected k=1000")

    by_query = raw.set_index("query_index", verify_integrity=True)
    aligned = by_query.loc[alignment_text.index, "text"].astype(str)
    mismatches = int((aligned.to_numpy() != alignment_text.to_numpy()).sum())
    if mismatches:
        raise ValueError(f"{artifact.logical_id}: {mismatches} feature/target text mismatches")

    metric_columns = ("pointwise_id", "pointwise_ess", "pointwise_fci_id")
    for column in metric_columns:
        raw[column] = pd.to_numeric(raw[column], errors="raise").astype("float64")
    release = raw[
        [
            "query_index",
            "revision",
            "reference_size",
            "k",
            "pointwise_id",
            "pointwise_ess",
            "pointwise_fci_id",
        ]
    ].copy()
    release = release.rename(
        columns={"revision": "model_revision", "pointwise_id": "pointwise_mle"}
    )
    release["query_index"] = pd.to_numeric(release["query_index"]).astype("int64")
    release["reference_size"] = pd.to_numeric(release["reference_size"]).astype("int64")
    release["k"] = pd.to_numeric(release["k"]).astype("int64")
    release = release.sort_values("query_index", kind="stable").reset_index(drop=True)
    null_metrics = {
        column.replace("pointwise_id", "pointwise_mle"): int(raw[column].isna().sum())
        for column in metric_columns
    }
    return release, {
        "rows": int(len(release)),
        "aligned_feature_rows": int(len(alignment_text)),
        "alignment_mismatches": mismatches,
        "null_metrics": null_metrics,
    }


def build_main_targets(
    source_root: Path,
    artifacts: Iterable[Artifact],
    alignment_text: pd.Series,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    pieces: list[pd.DataFrame] = []
    artifact_stats: dict[str, Any] = {}
    for artifact in artifacts:
        frame, stats = read_target(source_root / artifact.relative_path, artifact, alignment_text)
        frame.insert(0, "layer", int(artifact.layer))
        frame.insert(0, "model_key", str(artifact.model_family))
        pieces.append(frame)
        artifact_stats[artifact.logical_id] = stats
    release = pd.concat(pieces, ignore_index=True)
    release = release.sort_values(
        ["model_key", "layer", "query_index"], kind="stable"
    ).reset_index(drop=True)
    keys = ["model_key", "layer", "query_index"]
    if release.duplicated(keys).any():
        raise ValueError("Main targets contain duplicate composite keys")
    expected_rows = sum(len(LAYERS_BY_MODEL[key]) for key in LAYERS_BY_MODEL) * 2_000
    if len(release) != expected_rows:
        raise ValueError(f"Expected {expected_rows} main-target rows, found {len(release)}")
    return release, artifact_stats


def build_checkpoint_targets(
    source_root: Path,
    artifacts: Iterable[Artifact],
    alignment_text: pd.Series,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    pieces: list[pd.DataFrame] = []
    artifact_stats: dict[str, Any] = {}
    for artifact in artifacts:
        frame, stats = read_target(source_root / artifact.relative_path, artifact, alignment_text)
        frame.insert(0, "layer", int(artifact.layer))
        frame.insert(
            0,
            "training_tokens_billion",
            pd.array(
                [artifact.training_tokens_billion] * len(frame),
                dtype="Float64",
            ),
        )
        frame.insert(0, "training_step", int(artifact.training_step))
        frame.insert(0, "checkpoint_order", int(artifact.checkpoint_order))
        frame.insert(0, "checkpoint", str(artifact.checkpoint))
        frame.insert(0, "model_family", str(artifact.model_family))
        pieces.append(frame)
        artifact_stats[artifact.logical_id] = stats
    release = pd.concat(pieces, ignore_index=True)
    release["training_tokens_billion"] = pd.array(
        release["training_tokens_billion"], dtype="Float64"
    )
    release = release.sort_values(
        ["model_family", "checkpoint_order", "layer", "query_index"],
        kind="stable",
    ).reset_index(drop=True)
    keys = ["model_family", "checkpoint", "layer", "query_index"]
    if release.duplicated(keys).any():
        raise ValueError("Checkpoint targets contain duplicate composite keys")
    expected_rows = (5 * 3 * 2_000) + (7 * 3 * 2_000)
    if len(release) != expected_rows:
        raise ValueError(f"Expected {expected_rows} checkpoint rows, found {len(release)}")
    return release, artifact_stats


def parquet_schema(frame: pd.DataFrame) -> list[dict[str, str]]:
    return [{"name": str(name), "dtype": str(dtype)} for name, dtype in frame.dtypes.items()]


def validate_release_frame(frame: pd.DataFrame, name: str) -> None:
    forbidden = FORBIDDEN_OUTPUT_COLUMNS.intersection(frame.columns)
    if forbidden:
        raise ValueError(f"{name}: forbidden columns in release: {sorted(forbidden)}")
    for column in frame.select_dtypes(include=["object", "string"]).columns:
        values = frame[column].dropna().astype(str)
        # A filesystem path or address has no legitimate role in these outputs.
        suspicious = values.str.contains(r"(?:^[/\\]|@)", regex=True)
        if suspicious.any():
            raise ValueError(f"{name}: suspicious string value in {column}")
    if "text_sha256" in frame:
        valid_hash = frame["text_sha256"].astype(str).str.fullmatch(r"[0-9a-f]{64}")
        if not valid_hash.all():
            raise ValueError(f"{name}: malformed text SHA-256 fingerprint")


def to_parquet(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False, engine="pyarrow", compression="zstd")


def serialize_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def main() -> None:
    args = parse_args()
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    derived_dir = output_root / "data" / "derived"
    config_dir = output_root / "configs"
    derived_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    feature_artifact, main_artifacts, checkpoint_artifacts = input_artifacts()
    # Physical files reused in two analyses are checksummed once under the
    # main-table logical ID to keep the public inventory compact.
    all_artifacts = [feature_artifact, *main_artifacts, *checkpoint_artifacts]
    require_input_files(source_root, all_artifacts)

    features, alignment_text, feature_stats = read_features(
        source_root / feature_artifact.relative_path
    )
    main_targets, main_stats = build_main_targets(
        source_root, main_artifacts, alignment_text
    )
    checkpoint_targets, checkpoint_stats = build_checkpoint_targets(
        source_root, checkpoint_artifacts, alignment_text
    )

    tables = {
        "features.parquet": features,
        "main_targets.parquet": main_targets,
        "checkpoint_targets.parquet": checkpoint_targets,
    }
    for name, frame in tables.items():
        validate_release_frame(frame, name)
        to_parquet(frame, derived_dir / name)

    # Checksum every distinct physical input while exposing only a neutral ID.
    seen_paths: dict[str, str] = {}
    source_records: list[dict[str, Any]] = []
    for artifact in all_artifacts:
        path_key = artifact.relative_path
        if path_key in seen_paths:
            continue
        checksum = sha256_file(source_root / artifact.relative_path)
        seen_paths[path_key] = artifact.logical_id
        source_records.append(
            {
                "logical_id": artifact.logical_id,
                "sha256": checksum,
            }
        )
    source_records.sort(key=lambda record: record["logical_id"])
    checksum_lines = [
        f"{record['sha256']}  {record['logical_id']}" for record in source_records
    ]
    (config_dir / "artifacts.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )

    output_records: list[dict[str, Any]] = []
    for name, frame in tables.items():
        output_path = derived_dir / name
        output_records.append(
            {
                "file": name,
                "rows": int(len(frame)),
                "columns": int(len(frame.columns)),
                "schema": parquet_schema(frame),
                "sha256": sha256_file(output_path),
            }
        )

    validation = {
        "status": "passed",
        "feature_alignment": feature_stats,
        "main_targets": {
            "rows": int(len(main_targets)),
            "unique_keys": int(
                main_targets[["model_key", "layer", "query_index"]]
                .drop_duplicates()
                .shape[0]
            ),
            "models": sorted(main_targets["model_key"].unique().tolist()),
            "artifact_checks": main_stats,
        },
        "checkpoint_targets": {
            "rows": int(len(checkpoint_targets)),
            "unique_keys": int(
                checkpoint_targets[
                    ["model_family", "checkpoint", "layer", "query_index"]
                ]
                .drop_duplicates()
                .shape[0]
            ),
            "checkpoints_by_family": {
                family: int(
                    checkpoint_targets.loc[
                        checkpoint_targets["model_family"].eq(family), "checkpoint"
                    ].nunique()
                )
                for family in sorted(checkpoint_targets["model_family"].unique())
            },
            "artifact_checks": checkpoint_stats,
        },
        "privacy": {
            "raw_text_columns": 0,
            "provenance_path_columns": 0,
            "personal_identifiers": 0,
            "text_representations": "sha256-only-in-feature-table",
        },
    }
    (derived_dir / "VALIDATION.json").write_text(
        serialize_json(validation), encoding="utf-8"
    )

    manifest = {
        "bundle_version": BUNDLE_VERSION,
        "purpose": "Compact, text-free inputs for deterministic reproduction of reported analyses.",
        "transformation": [
            "Retain all numeric and Boolean profiling predictors and rename the stable row key to query_index.",
            "Replace each feature-row text value with its lowercase hexadecimal SHA-256 fingerprint.",
            "Validate target alignment against text in memory, then retain only neutral setup fields and pointwise estimates.",
            "Use three final models, five reported Pythia checkpoints, and seven reported Apertus checkpoints.",
            "Exclude text, source locations, dataset line numbers, original identifiers, runtime paths, and execution logs.",
        ],
        "source_artifacts": source_records,
        "outputs": output_records,
        "validation_report": "VALIDATION.json",
        "source_checksum_file": "../../configs/artifacts.sha256",
    }
    (derived_dir / "MANIFEST.json").write_text(
        serialize_json(manifest), encoding="utf-8"
    )

    print("Release bundle built and validated")
    for record in output_records:
        print(
            f"  {record['file']}: {record['rows']} rows, "
            f"{record['columns']} columns, sha256={record['sha256']}"
        )
    print(f"  source artifacts checksummed: {len(source_records)}")


if __name__ == "__main__":
    main()
