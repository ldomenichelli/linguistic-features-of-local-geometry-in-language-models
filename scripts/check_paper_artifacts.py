#!/usr/bin/env python3
"""Check that the complete paper artifact set can be rebuilt consistently."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd


TABLE_SHAPES = {
    1: (9, 6),
    2: (9, 8),
    3: (9, 12),
    4: (7, 10),
    5: (21, 13),
    6: (18, 9),
    7: (18, 13),
    8: (36, 8),
    9: (6, 8),
    10: (9, 7),
    11: (9, 6),
    12: (45, 5),
    13: (7, 6),
    14: (27, 8),
    15: (27, 8),
    16: (15, 13),
    17: (46, 3),
}
UNIX_HOME_PREFIX = "/" + "home" + "/"
WINDOWS_HOME_PREFIX = r"[A-Za-z]:\\" + "Users" + r"\\"
PERSONAL_PATH = re.compile(
    rf"(?:{re.escape(UNIX_HOME_PREFIX)}|{WINDOWS_HOME_PREFIX})"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--committed-dir", type=Path, default=Path("paper"))
    parser.add_argument("--generated-dir", type=Path, default=Path("results/paper"))
    parser.add_argument("--derived-dir", type=Path, default=Path("data/derived"))
    return parser.parse_args()


def require(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing paper artifact: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"Empty paper artifact: {path}")


def check_binary(path: Path, signature: bytes) -> None:
    require(path)
    with path.open("rb") as handle:
        observed = handle.read(len(signature))
    if observed != signature:
        raise ValueError(f"Unexpected file signature for {path}")


def check_tables(committed_dir: Path, generated_dir: Path) -> None:
    for number, expected_shape in TABLE_SHAPES.items():
        filename = f"table_{number:02d}.csv"
        committed_path = committed_dir / "tables" / filename
        generated_path = generated_dir / "tables" / filename
        require(committed_path)
        require(generated_path)
        committed = pd.read_csv(committed_path)
        generated = pd.read_csv(generated_path)
        if committed.shape != expected_shape:
            raise ValueError(
                f"{committed_path} has shape {committed.shape}; expected {expected_shape}"
            )
        pd.testing.assert_frame_equal(
            committed,
            generated,
            check_dtype=False,
            check_exact=False,
            rtol=1e-9,
            atol=1e-11,
        )


def check_figures(committed_dir: Path, generated_dir: Path) -> None:
    for number in range(1, 7):
        for root in (committed_dir, generated_dir):
            check_binary(root / "figures" / f"figure_{number:02d}.png", b"\x89PNG\r\n\x1a\n")
            check_binary(root / "figures" / f"figure_{number:02d}.pdf", b"%PDF-")


def check_index_links(committed_dir: Path) -> None:
    for filename in ("README.md", "FIGURES.md", "TABLES.md", "ARTIFACTS.md"):
        require(committed_dir / filename)
    figure_index = (committed_dir / "FIGURES.md").read_text(encoding="utf-8")
    table_index = (committed_dir / "TABLES.md").read_text(encoding="utf-8")
    for number in range(1, 7):
        for suffix in ("png", "pdf"):
            relative = f"figures/figure_{number:02d}.{suffix}"
            if relative not in figure_index:
                raise ValueError(f"FIGURES.md does not link {relative}")
    for number in range(1, 18):
        relative = f"tables/table_{number:02d}.csv"
        if relative not in table_index:
            raise ValueError(f"TABLES.md does not link {relative}")


def check_manifest(committed_dir: Path) -> None:
    path = committed_dir / "artifacts.csv"
    require(path)
    artifacts = pd.read_csv(path)
    if not artifacts.kind.isin(["figure", "table", "experiment"]).all():
        raise ValueError(f"{path} has an unknown artifact kind")
    experiments = artifacts.loc[artifacts.kind.eq("experiment")]
    if experiments.number.notna().any() or experiments.title.duplicated().any():
        raise ValueError(f"{path} requires unnumbered experiments with unique titles")
    artifacts = artifacts.loc[artifacts.kind.isin(["figure", "table"])]
    if len(artifacts) != 23:
        raise ValueError(f"{path} must contain 23 numbered artifacts, found {len(artifacts)}")
    counts = artifacts.groupby("kind")["number"].nunique().to_dict()
    if counts != {"figure": 6, "table": 17}:
        raise ValueError(f"Unexpected artifact counts: {counts}")
    if bool(artifacts.duplicated(["kind", "number"]).any()):
        raise ValueError(f"{path} has duplicate figure/table numbers")


def check_feature_inventory(committed_dir: Path, derived_dir: Path) -> None:
    features = pd.read_parquet(derived_dir / "features.parquet")
    expected = set(features.columns) - {"query_index", "text_sha256"}
    inventory = pd.read_csv(committed_dir / "tables" / "table_17.csv")
    observed = set(inventory["feature"].astype(str))
    if observed != expected:
        raise ValueError(
            "Table 17 does not match features.parquet: "
            f"missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )


def check_table_13_values(committed_dir: Path, derived_dir: Path) -> None:
    aliases = {
        "upos_PROPN": "upos_dist_PROPN",
        "upos_NOUN": "upos_dist_NOUN",
        "dep_nsubj": "dep_dist_nsubj",
        "verbal_root": "verbal_root_perc",
        "upos_PRON": "upos_dist_PRON",
    }
    features = pd.read_parquet(derived_dir / "features.parquet").set_index("query_index")
    targets = pd.read_parquet(derived_dir / "main_targets.parquet")
    targets = targets.loc[
        targets["model_key"].eq("pythia") & targets["layer"].eq(16)
    ].set_index("query_index")
    examples = pd.read_csv(committed_dir / "tables" / "table_13.csv")
    if bool(examples["query_index"].duplicated().any()):
        raise ValueError("Table 13 has duplicate query indices")
    for row in examples.itertuples(index=False):
        feature = aliases.get(str(row.feature), str(row.feature))
        displayed_feature = float(str(row.feature_value).removesuffix("%"))
        actual_feature = float(features.at[int(row.query_index), feature])
        actual_ess = float(targets.at[int(row.query_index), "pointwise_ess"])
        if not np.isclose(actual_feature, displayed_feature, atol=0.051, rtol=0):
            raise ValueError(f"Table 13 feature value mismatch at query {row.query_index}")
        if not np.isclose(actual_ess, float(row.ess_id), atol=0.006, rtol=0):
            raise ValueError(f"Table 13 ESS value mismatch at query {row.query_index}")


def check_text_for_paths(paths: list[Path]) -> None:
    leaking = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if PERSONAL_PATH.search(text):
            leaking.append(str(path))
    if leaking:
        raise ValueError("Personal absolute paths found in: " + ", ".join(leaking))


def main() -> None:
    args = parse_args()
    check_tables(args.committed_dir, args.generated_dir)
    check_figures(args.committed_dir, args.generated_dir)
    check_index_links(args.committed_dir)
    check_manifest(args.committed_dir)
    check_feature_inventory(args.committed_dir, args.derived_dir)
    check_table_13_values(args.committed_dir, args.derived_dir)
    text_paths = list(args.committed_dir.glob("*.md"))
    text_paths += list((args.committed_dir / "tables").glob("*.csv"))
    text_paths.append(args.committed_dir / "artifacts.csv")
    check_text_for_paths(text_paths)
    print("Paper artifacts OK: 6 figures, 17 tables, and matching rebuilt values")


if __name__ == "__main__":
    main()
