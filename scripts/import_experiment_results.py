#!/usr/bin/env python3
"""Import archived experiment results into the ordinary public result layout.

Run with --source-root pointing at the original study. Source files are retained.
Only numeric results and experiment labels are exported; raw excerpts, personal
paths and text-bearing model inputs are excluded. No experiments are refitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

ROOTS = {
    "pythia-1.4b": "outputs",
    "pythia-6.9b": "outputs_6.9",
    "qwen-2.5-7b": "qwen_results/outputs",
    "apertus-8b": "apertus_results/outputs",
}
DROP_COLUMNS = {
    "source_dir", "source_file", "source_path", "error_message", "text",
    "recovered_text", "identifier", "uid", "line_index", "query_source_index",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean(frame):
    frame = frame.drop(columns=list(DROP_COLUMNS), errors="ignore").copy()
    for col in frame.select_dtypes(include=["object", "string"]):
        if frame[col].astype(str).str.contains(r"/(?:home|Users)/", regex=True).any():
            raise ValueError(f"Personal path in output column {col}")
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    sources, outputs = [], []
    source_ids = set()

    def record(path, logical_id):
        if logical_id not in source_ids:
            sources.append({"logical_id": logical_id, "sha256": sha256(path)})
            source_ids.add(logical_id)

    def read(relative, logical_id):
        path = args.source_root / relative
        record(path, logical_id)
        return clean(pd.read_csv(path))

    def write(frame, relative):
        frame = clean(frame)
        path = args.output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".parquet":
            frame.to_parquet(path, index=False)
        else:
            frame.to_csv(path, index=False)
        outputs.append({"path": relative, "rows": len(frame), "columns": list(frame.columns),
                        "sha256": sha256(path)})

    def write_config(relative, logical_id, keys, name):
        path = args.source_root / relative
        record(path, logical_id)
        original = json.loads(path.read_text())
        config = {key: original[key] for key in keys}
        if "args" in config:
            config["args"] = {key: value for key, value in config["args"].items()
                              if key not in {"output_dir", "force", "render_only", "n_jobs"}}
        payload = json.dumps(config, indent=2) + "\n"
        if re.search(r"/(?:home|Users)/", payload):
            raise ValueError(f"Personal path in {logical_id}")
        destination = args.output_root / "configs" / name
        destination.write_text(payload)
        outputs.append({"path": str(destination.relative_to(args.output_root)), "sha256": sha256(destination)})

    collected = {"layer_neighbourhood_regression": [], "grouped_permutation_importance": [],
                 "feature_family_ablations": []}
    filenames = {
        "layer_neighbourhood_regression": "profiling_ud_to_id_predictive_results.csv",
        "grouped_permutation_importance": "grouped_permutation_importance_summary.csv",
        "feature_family_ablations": "ablation_summary.csv",
    }
    pattern = re.compile(r"profiling_ud_to_(id|ess|fci_pyfci)(?:_qwen2p5_7b|_apertus8b_2509)?_eval_known_layer(\d+)_k(\d+)_ref(\d+)_feature60_plus_frequency$")
    for model, root in ROOTS.items():
        for directory in sorted((args.source_root / root).glob("profiling_ud_to_*")):
            match = pattern.fullmatch(directory.name)
            if not match:
                continue
            run, layer, k, ref = match.groups()
            setting = f"{model}.{run}.layer-{layer}.k-{k}.ref-{ref}"
            for experiment, filename in filenames.items():
                path = directory / filename
                if not path.is_file() or path.stat().st_size < 5:
                    continue
                frame = read(path.relative_to(args.source_root), f"{experiment}.{setting}")
                if experiment == "layer_neighbourhood_regression":
                    frame = frame.loc[frame.task_type.eq("regression")].copy()
                elif experiment == "feature_family_ablations":
                    frame = frame.loc[frame.ablation_kind.eq("drop_family")].copy()
                if frame.empty:
                    continue
                for col, value in reversed(list({"model_key": model, "run_kind": run,
                        "layer": int(layer), "k": int(k), "reference_size": int(ref),
                        "split": "eval_known"}.items())):
                    if col in frame:
                        observed = frame[col].dropna()
                        if not observed.eq(value).all():
                            raise ValueError(f"Conflicting {col} metadata in {setting}")
                        frame = frame.drop(columns=col)
                    frame.insert(0, col, value)
                collected[experiment].append(frame)
    for experiment, frames in collected.items():
        if not frames:
            raise ValueError(f"No archived results found for {experiment}")
        write(pd.concat(frames, ignore_index=True), f"data/paper/{experiment}.csv")

    locality = "outputs/neighborhood_locality_quick_20260916"
    write_config(f"{locality}/manifest.json", "neighbourhood_locality.parameters",
                 ["seed", "n_query", "ks", "distance", "tfidf", "bootstrap", "selected_query_positions"],
                 "neighbourhood_locality.json")
    for name in ["summary", "validation", "apertus_layer16_mle_precision"]:
        write(read(f"{locality}/{name}.csv", f"neighbourhood_locality.{name}"),
              f"data/paper/neighbourhood_locality_{name}.csv")
    path = args.source_root / locality / "per_query_metrics.parquet"
    record(path, "neighbourhood_locality.per_query_metrics")
    write(pd.read_parquet(path), "data/derived/neighbourhood_locality_metrics.parquet")
    for name in ["distance_profile_summary", "composition_summary", "stability_summary"]:
        write(read(f"outputs/small_k_neighbor_diagnostics/{name}.csv", f"pythia_small_k.{name}"),
              f"data/paper/pythia_small_k_{name}.csv")

    # Preserve the zero-based layer index AND the original layer name.
    path = args.source_root / "outputs/local_seen_unseen_100_mle_ess_aligned/eval_known_pointwise_mle_long.parquet"
    record(path, "pythia-1.4b.all_layer_id")
    keys = ["model_name", "revision", "layer_idx", "layer_name", "reference_size", "k"]
    frame = pd.read_parquet(path, columns=keys + ["pointwise_id", "pointwise_ess"])
    rows = []
    for metric, estimator in [("pointwise_id", "MLE"), ("pointwise_ess", "ESS")]:
        summary = frame.groupby(keys, dropna=False)[metric].agg(["count", "mean", "std", "median"]).reset_index()
        summary["estimator"] = estimator
        rows.append(summary)
    write(pd.concat(rows, ignore_index=True), "data/paper/pythia_small_all_layer_id.csv")

    write(read("outputs/eval_known_perplexity_ess_correlations_all_models/perplexity_ess_correlations_by_model_layer_k.csv",
               "perplexity.ess_all_model_layer_k"), "data/paper/perplexity_ess_layer_neighbourhood.csv")
    perplexity_ridge = []
    for run_id, directory in [
        ("all_layers_3fold", "perplexity_mle_ess_tasks_ref15000_k1000_linear"),
        ("eval_known_layer24_5fold", "perplexity_mle_ess_tasks_eval_known_layer24_ref15000_k1000"),
    ]:
        root = f"outputs/{directory}"
        frame = read(f"{root}/perplexity_regression_results.csv", f"perplexity_ridge.{run_id}")
        frame = frame.loc[frame.model.eq("ridge") & frame.features.eq("log_perplexity")].copy()
        if frame.empty:
            raise ValueError(f"No perplexity-only Ridge results for {run_id}")
        frame.insert(0, "run_id", run_id)
        frame.insert(1, "model_key", "pythia-1.4b")
        if "split_name" not in frame:
            frame["split_name"] = "eval_known"
        perplexity_ridge.append(frame)
        write_config(f"{root}/config_used.json", f"perplexity_ridge.{run_id}.parameters",
                     ["aggregate_level", "features", "group_cols", "k", "reference_size", "n_splits",
                      "n_modeling_rows", "targets"], f"perplexity_ridge_{run_id}.json")
    write(pd.concat(perplexity_ridge, ignore_index=True), "data/paper/perplexity_only_ridge.csv")
    for variant, directory in [
        ("word", "three_model_final_ess_nonlinear_nuisance_control_no_frequency"),
        ("word_char", "three_model_final_ess_nonlinear_nuisance_control_word_char_no_frequency"),
    ]:
        root = f"outputs_6.9/{directory}"
        write_config(f"{root}/config.json", f"source_tfidf_{variant}.parameters",
                     ["args", "baseline_alpha_grid", "baseline_numeric_columns", "baseline_other_blocks",
                      "common_exact_period_rows", "excluded_shared_frequency_columns", "interval", "k",
                      "morphosyntax_columns", "reference_size", "residual_targets", "rf_grid", "target", "validation"],
                     f"source_tfidf_{variant}.json")
        for name in ["nonlinear_incremental_effects", "outer_fold_metrics", "baseline_alpha_tuning", "nonlinear_tuning_choices"]:
            destination = "data/paper" if name == "nonlinear_incremental_effects" else "results/reference"
            write(read(f"{root}/{name}.csv", f"source_tfidf_{variant}.{name}"),
                  f"{destination}/source_tfidf_{variant}_{name}.csv")
        path = args.source_root / root / "oof_predictions.parquet"
        record(path, f"source_tfidf_{variant}.oof_predictions")
        frame = pd.read_parquet(path)
        # Explicitly omit any source excerpts; retain cohort IDs and predictions.
        frame = clean(frame)
        write(frame, f"results/reference/source_tfidf_{variant}_oof_predictions.parquet")

    manifest = {"version": 1, "mode": "archived_numeric_results", "sources": sources, "outputs": outputs,
                "notes": ["No source files were deleted.", "Raw excerpts and personal paths are excluded.",
                          "Run-kind labels distinguish legacy ID, ESS-only and pyFCI runs; they must not be pooled as independent replicates.",
                          "These historical grids are separate from the pinned main-model bundle."]}
    path = args.output_root / "configs/experiment_results_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Imported {len(outputs)} result tables from {len(sources)} source artifacts.")


if __name__ == "__main__":
    main()
