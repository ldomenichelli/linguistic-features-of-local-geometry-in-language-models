#!/usr/bin/env python3
"""Check imported hashes, cohort coverage, and numeric experiment artifacts."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from build_experiment_artifacts import FIGURES, build_tables

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "configs/experiment_results_manifest.json").read_text())
    for entry in manifest["outputs"]:
        path = ROOT / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], path
        if "rows" in entry:
            frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
            assert len(frame) == entry["rows"] and list(frame.columns) == entry["columns"], path
            assert not {"text", "recovered_text", "source_file", "source_dir", "identifier"} & set(frame), path

    for variant in ("word", "word_char"):
        predictions = pd.read_parquet(ROOT / f"results/reference/source_tfidf_{variant}_oof_predictions.parquet")
        effects = pd.read_csv(ROOT / f"data/paper/source_tfidf_{variant}_nonlinear_incremental_effects.csv")
        assert len(effects) == 9
        assert not predictions.duplicated(["model_key", "layer", "query_index"]).any()
        cohorts = []
        for row in effects.itertuples():
            group = predictions.loc[predictions.model_key.eq(row.model_key) & predictions.layer.eq(row.layer)]
            assert len(group) == row.n_rows == 1866
            assert set(group.outer_fold) == set(range(5))
            baseline = r2_score(group.target_value, group.prediction_lexical_source)
            augmented = r2_score(group.target_value, group.prediction_lexical_source_plus_rf)
            np.testing.assert_allclose([baseline, augmented, augmented - baseline],
                                       [row.baseline_r2_oof, row.augmented_r2_oof, row.delta_r2_oof], atol=1e-12)
            cohorts.append(set(group.query_index))
        assert all(cohort == cohorts[0] for cohort in cohorts)

    summary = pd.read_csv(ROOT / "data/paper/neighbourhood_locality_summary.csv")
    queries = pd.read_parquet(ROOT / "data/derived/neighbourhood_locality_metrics.parquet")
    keys = ["model", "layer", "kind", "rank_start", "k"]
    means = queries.groupby(keys)[["same_source", "tfidf_source_matched_gain"]].mean().reset_index()
    merged = summary.merge(means, on=keys, validate="one_to_one")
    assert len(merged) == len(summary) == 90
    for metric in ("same_source", "tfidf_source_matched_gain"):
        np.testing.assert_allclose(merged[metric], merged[metric + "_mean"], atol=1e-12)
    assert queries.groupby(keys).size().eq(500).all()
    small = pd.read_csv(ROOT / "data/paper/pythia_small_all_layer_id.csv")
    for estimator in ("MLE", "ESS"):
        subset = small.loc[small.estimator.eq(estimator) & small.k.eq(1000) & small.reference_size.eq(15000)]
        assert set(subset.layer_idx) == set(range(24))

    ridge = pd.read_csv(ROOT / "data/paper/perplexity_only_ridge.csv")
    assert len(ridge) == 100
    assert ridge.model.eq("ridge").all() and ridge.features.eq("log_perplexity").all()
    assert set(ridge.target) == {"mle", "ess"}
    for split in ("eval_known", "eval_unknown"):
        group = ridge.loc[ridge.run_id.eq("all_layers_3fold") & ridge.split_name.eq(split)]
        assert len(group) == 48 and group.n_splits.eq(3).all()
        assert set(group.layer_name) == {f"layer_{i}" for i in range(1, 25)}
    extra = ridge.loc[ridge.run_id.eq("eval_known_layer24_5fold")]
    assert len(extra) == 2 and extra.n_splits.eq(5).all()

    for name, expected in build_tables(ROOT / "data/paper").items():
        for directory in (ROOT / "paper", ROOT / "results/paper"):
            actual = pd.read_csv(directory / "tables" / f"{name}.csv")
            pd.testing.assert_frame_equal(actual.reset_index(drop=True), expected.reset_index(drop=True),
                                          check_dtype=False, atol=1e-11, rtol=1e-9)
    for name in FIGURES:
        for directory in (ROOT / "paper", ROOT / "results/paper"):
            for suffix, signature in [("png", b"\x89PNG\r\n\x1a\n"), ("pdf", b"%PDF-")]:
                assert (directory / "figures" / f"{name}.{suffix}").read_bytes().startswith(signature)
    print(f"Experiment checks passed: {len(manifest['outputs'])} imports, 18 OOF comparisons, 90 locality settings, 24 layers.")


if __name__ == "__main__":
    main()
