#!/usr/bin/env python3
"""Materialize matched sentence-level MLE/ESS/FCI parquet files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_LAYERS = "2,16,31"
DEFAULT_K_VALUES = "1000"
DEFAULT_REF_SIZE = 15_000


def parse_int_list(value: str) -> list[int]:
    items = [item.strip() for item in str(value).replace(",", " ").split() if item.strip()]
    if not items:
        raise ValueError("Expected at least one integer.")
    return [int(item) for item in items]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mle_ess_known_long", type=Path, required=True)
    parser.add_argument("--mle_ess_unknown_long", type=Path, required=True)
    parser.add_argument("--fci_known_long", type=Path, required=True)
    parser.add_argument("--fci_unknown_long", type=Path, required=True)
    parser.add_argument("--output_dir", type=Path, required=True)
    parser.add_argument("--known_prefix", default="eval_known")
    parser.add_argument("--unknown_prefix", default="eval_unknown_1")
    parser.add_argument("--layers", default=DEFAULT_LAYERS)
    parser.add_argument("--k_values", default=DEFAULT_K_VALUES)
    parser.add_argument("--ref_size", type=int, default=DEFAULT_REF_SIZE)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_required(path: Path, *, required: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    dataframe = pd.read_parquet(path)
    missing = sorted(required - set(dataframe.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")
    return dataframe


def filter_layer_k_ref(dataframe: pd.DataFrame, *, layer: int, k_value: int, ref_size: int) -> pd.DataFrame:
    layer_idx = int(layer) - 1
    layer_name = f"layer_{int(layer)}"
    if "layer_name" in dataframe.columns and bool((dataframe["layer_name"].astype(str) == layer_name).any()):
        layer_mask = dataframe["layer_name"].astype(str) == layer_name
    else:
        layer_mask = pd.to_numeric(dataframe["layer_idx"], errors="raise") == layer_idx

    subset = dataframe.loc[
        layer_mask
        & (pd.to_numeric(dataframe["k"], errors="raise") == int(k_value))
        & (pd.to_numeric(dataframe["reference_size"], errors="raise") == int(ref_size))
    ].copy()
    return subset


def sort_sentence_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    sort_columns = [column for column in ("query_index", "query_source_index", "line_index") if column in dataframe.columns]
    if sort_columns:
        dataframe = dataframe.sort_values(sort_columns, kind="stable")
    return dataframe.reset_index(drop=True)


def materialize_split(
    *,
    mle_ess_df: pd.DataFrame,
    fci_df: pd.DataFrame,
    output_dir: Path,
    file_prefix: str,
    layers: list[int],
    k_values: list[int],
    ref_size: int,
    overwrite: bool,
) -> None:
    for layer in layers:
        for k_value in k_values:
            out_path = output_dir / f"{file_prefix}_layer{layer}_k{k_value}_ref{ref_size}_sentence_level.parquet"
            if out_path.exists() and not overwrite:
                print(f"skip existing {out_path}")
                continue

            metric_subset = filter_layer_k_ref(
                mle_ess_df,
                layer=int(layer),
                k_value=int(k_value),
                ref_size=int(ref_size),
            )
            fci_subset = filter_layer_k_ref(
                fci_df,
                layer=int(layer),
                k_value=int(k_value),
                ref_size=int(ref_size),
            )
            if metric_subset.empty:
                raise ValueError(f"No MLE/ESS rows found for {file_prefix}, layer={layer}, k={k_value}")
            if fci_subset.empty:
                raise ValueError(f"No FCI rows found for {file_prefix}, layer={layer}, k={k_value}")

            metric_subset = sort_sentence_rows(metric_subset)
            fci_subset = sort_sentence_rows(fci_subset)
            merge_keys = [
                column
                for column in ("query_index", "text", "layer_idx", "reference_size", "k")
                if column in metric_subset.columns and column in fci_subset.columns
            ]
            if not merge_keys:
                raise ValueError("No common merge keys found between MLE/ESS and FCI tables.")

            fci_columns = [*merge_keys, "pointwise_fci_id"]
            merged = metric_subset.merge(
                fci_subset.loc[:, fci_columns],
                on=merge_keys,
                how="inner",
                validate="one_to_one",
            )
            if len(merged) != len(metric_subset) or len(merged) != len(fci_subset):
                metric_kind = (
                    sorted(metric_subset["sample_kind"].dropna().astype(str).unique().tolist())
                    if "sample_kind" in metric_subset.columns
                    else []
                )
                fci_kind = (
                    sorted(fci_subset["sample_kind"].dropna().astype(str).unique().tolist())
                    if "sample_kind" in fci_subset.columns
                    else []
                )
                metric_text = set(metric_subset["text"].astype(str)) if "text" in metric_subset.columns else set()
                fci_text = set(fci_subset["text"].astype(str)) if "text" in fci_subset.columns else set()
                raise ValueError(
                    f"Unexpected merge size for {file_prefix}, layer={layer}, k={k_value}: "
                    f"mle_ess={len(metric_subset)}, fci={len(fci_subset)}, merged={len(merged)}. "
                    f"metric_sample_kind={metric_kind}, fci_sample_kind={fci_kind}, "
                    f"text_overlap={len(metric_text & fci_text)}"
                )

            merged = sort_sentence_rows(merged)
            merged.to_parquet(out_path, index=False)
            print(f"wrote {out_path} rows={len(merged)}")


def main() -> None:
    args = parse_args()
    layers = parse_int_list(args.layers)
    k_values = parse_int_list(args.k_values)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metric_required = {"layer_idx", "reference_size", "k", "text", "pointwise_id", "pointwise_ess"}
    fci_required = {"layer_idx", "reference_size", "k", "text", "pointwise_fci_id"}

    known_metric = load_required(args.mle_ess_known_long, required=metric_required)
    unknown_metric = load_required(args.mle_ess_unknown_long, required=metric_required)
    known_fci = load_required(args.fci_known_long, required=fci_required)
    unknown_fci = load_required(args.fci_unknown_long, required=fci_required)

    materialize_split(
        mle_ess_df=known_metric,
        fci_df=known_fci,
        output_dir=args.output_dir,
        file_prefix=str(args.known_prefix),
        layers=layers,
        k_values=k_values,
        ref_size=int(args.ref_size),
        overwrite=bool(args.overwrite),
    )
    materialize_split(
        mle_ess_df=unknown_metric,
        fci_df=unknown_fci,
        output_dir=args.output_dir,
        file_prefix=str(args.unknown_prefix),
        layers=layers,
        k_values=k_values,
        ref_size=int(args.ref_size),
        overwrite=bool(args.overwrite),
    )


if __name__ == "__main__":
    main()
