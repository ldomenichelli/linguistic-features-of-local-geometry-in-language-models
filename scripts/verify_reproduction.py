#!/usr/bin/env python3
"""Verify bundle safety, analysis configuration, coverage, and reproducibility."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from reproduce_analysis import (
    FEATURE_SET_ORDER,
    FREQUENCY_FEATURES,
    HIGH_QUANTILE,
    LOGISTIC_MAX_ITER,
    LOW_QUANTILE,
    MAIN_TARGETS,
    N_SPLITS,
    RAW_SURFACE_FEATURES,
    RF_MIN_SAMPLES_LEAF,
    RF_N_JOBS,
    RF_TREES,
    RIDGE_ALPHA,
    SEED,
    AnalysisConfig,
    BundlePaths,
    _looks_like_identity_column,
    _raw_text_columns,
    feature_manifest,
    load_bundle,
    run_analysis,
)


MAIN_RESULT_FILES = (
    "feature_sets.csv",
    "main_fold_scores.csv",
    "main_cv_summary.csv",
    "main_oof_predictions.csv",
    "main_cv_r2.png",
    "ess_classification_fold_scores.csv",
    "ess_classification_summary.csv",
    "ess_classification_oof_predictions.csv",
    "ess_classification_auc.png",
    "paper_ess_scores.csv",
    "analysis_manifest.json",
)
CHECKPOINT_RESULT_FILES = (
    "checkpoint_fold_scores.csv",
    "checkpoint_cv_summary.csv",
    "checkpoint_oof_predictions.csv",
    "checkpoint_ess_r2.png",
)
PATH_FRAGMENT_RE = re.compile(
    r"(?:" + re.escape("/" + "home" + "/") + r"|[A-Za-z]:\\Users\\)"
)
REFERENCE_FILES = (
    "ess_full_reference.csv",
    "ess_no_frequency_reference.csv",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/derived"))
    parser.add_argument("--features", type=Path, default=None)
    parser.add_argument("--main-targets", type=Path, default=None)
    parser.add_argument("--checkpoint-targets", type=Path, default=None)
    parser.add_argument(
        "--generated-dir",
        "--results-dir",
        dest="generated_dir",
        type=Path,
        default=Path("results/generated"),
    )
    parser.add_argument(
        "--reference-dir", type=Path, default=Path("results/reference")
    )
    parser.add_argument("--rtol", type=float, default=1e-7)
    parser.add_argument("--atol", type=float, default=1e-9)
    parser.add_argument("--skip-checkpoints", action="store_true")
    parser.add_argument("--require-checkpoints", action="store_true")
    parser.add_argument(
        "--check-determinism",
        action="store_true",
        help="Rerun the fixed analysis and byte-compare all generated artifacts.",
    )
    args = parser.parse_args()
    if args.skip_checkpoints and args.require_checkpoints:
        parser.error("--skip-checkpoints and --require-checkpoints are incompatible.")
    return args


def resolve_paths(args: argparse.Namespace) -> BundlePaths:
    data_dir = Path(args.data_dir)
    return BundlePaths(
        features=Path(args.features) if args.features else data_dir / "features.parquet",
        main_targets=(
            Path(args.main_targets)
            if args.main_targets
            else data_dir / "main_targets.parquet"
        ),
        checkpoint_targets=(
            Path(args.checkpoint_targets)
            if args.checkpoint_targets
            else data_dir / "checkpoint_targets.parquet"
        ),
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_files(results_dir: Path, checkpoint_expected: bool) -> list[Path]:
    names = list(MAIN_RESULT_FILES)
    if checkpoint_expected:
        names.extend(CHECKPOINT_RESULT_FILES)
    missing = [name for name in names if not (results_dir / name).is_file()]
    if missing:
        raise ValueError("Missing generated results: " + ", ".join(missing))
    return [results_dir / name for name in names]


def verify_no_personal_paths(paths: Sequence[Path]) -> None:
    text_paths = [path for path in paths if path.suffix in {".csv", ".json"}]
    leaking: list[str] = []
    for path in text_paths:
        contents = path.read_text(encoding="utf-8")
        if PATH_FRAGMENT_RE.search(contents):
            leaking.append(path.name)
    if leaking:
        raise ValueError(
            "Generated artifacts contain personal absolute paths: " + ", ".join(leaking)
        )


def verify_manifest(
    results_dir: Path,
    *,
    expected_checkpoint: bool,
    expected_feature_sets: dict[str, tuple[str, ...]],
    extended: bool,
) -> None:
    path = results_dir / "analysis_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    expected_config = {
        "high_quantile": HIGH_QUANTILE,
        "logistic_max_iter": LOGISTIC_MAX_ITER,
        "low_quantile": LOW_QUANTILE,
        "n_splits": N_SPLITS,
        "seed": SEED,
        "ridge_alpha": RIDGE_ALPHA,
        "rf_trees": RF_TREES,
        "rf_min_samples_leaf": RF_MIN_SAMPLES_LEAF,
        "rf_n_jobs": RF_N_JOBS,
    }
    if manifest.get("config") != expected_config:
        raise ValueError(
            f"analysis_manifest.json has non-reference config: {manifest.get('config')}"
        )
    expected_mode = "extended" if extended else "paper_core"
    if manifest.get("analysis_mode") != expected_mode:
        raise ValueError("analysis_manifest.json has an inconsistent analysis mode.")
    if bool(manifest.get("checkpoint_analysis_ran")) != expected_checkpoint:
        raise ValueError("Checkpoint-analysis status disagrees with the loaded bundle.")
    expected_sets = {
        name: list(expected_feature_sets[name]) for name in FEATURE_SET_ORDER
    }
    if manifest.get("feature_sets") != expected_sets:
        raise ValueError("Manifest feature sets disagree with validated features.parquet.")
    preprocessing = manifest.get("preprocessing", {})
    if preprocessing != {
        "imputation": "training-fold median",
        "random_forest_scaling": "none",
        "ridge_scaling": "training-fold StandardScaler",
    }:
        raise ValueError("Manifest preprocessing does not match the fixed protocol.")


def verify_feature_manifest(results_dir: Path, expected: pd.DataFrame) -> None:
    observed = pd.read_csv(results_dir / "feature_sets.csv")
    pd.testing.assert_frame_equal(
        observed.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_dtype=False,
        check_like=False,
    )
    identities = [
        feature
        for feature in observed["feature"].astype(str)
        if _looks_like_identity_column(feature)
    ]
    if identities:
        raise ValueError("Model feature sets contain identifiers: " + ", ".join(identities))
    raw_text = _raw_text_columns(observed["feature"].astype(str))
    if raw_text:
        raise ValueError("Model feature sets contain raw text: " + ", ".join(raw_text))

    by_feature = observed.set_index("feature")
    for feature in FREQUENCY_FEATURES:
        if feature in by_feature.index and bool(by_feature.at[feature, "in_no_frequency"]):
            raise ValueError(f"Frequency feature was not ablated: {feature}")
    for feature in RAW_SURFACE_FEATURES:
        if feature in by_feature.index and bool(by_feature.at[feature, "in_no_raw"]):
            raise ValueError(f"Raw/surface feature was not ablated: {feature}")


def _require_result_columns(
    dataframe: pd.DataFrame, required: Sequence[str], filename: str
) -> None:
    missing = [column for column in required if column not in dataframe.columns]
    if missing:
        raise ValueError(f"{filename} is missing columns: {', '.join(missing)}")


def verify_scores(
    scores: pd.DataFrame,
    *,
    filename: str,
    context_columns: Sequence[str],
    targets: set[str],
    feature_sets: set[str],
) -> None:
    required = (
        *context_columns,
        "target",
        "target_column",
        "feature_set",
        "estimator",
        "fold",
        "n_samples",
        "n_train",
        "n_test",
        "n_features",
        "r2",
        "mae",
        "rmse",
    )
    _require_result_columns(scores, required, filename)
    if set(scores["target"].astype(str)) != targets:
        raise ValueError(f"{filename} has unexpected targets: {set(scores['target'])}")
    if set(scores["feature_set"].astype(str)) != feature_sets:
        raise ValueError(
            f"{filename} has unexpected feature sets: {set(scores['feature_set'])}"
        )
    if set(scores["estimator"].astype(str)) != {"Ridge", "RandomForest"}:
        raise ValueError(f"{filename} has unexpected estimators.")
    if set(pd.to_numeric(scores["fold"], errors="raise").astype(int)) != set(
        range(1, N_SPLITS + 1)
    ):
        raise ValueError(f"{filename} does not contain folds 1 through {N_SPLITS}.")

    grouping = [
        *context_columns,
        "target",
        "feature_set",
        "estimator",
    ]
    fold_counts = scores.groupby(grouping, dropna=False)["fold"].nunique()
    if not bool((fold_counts == N_SPLITS).all()):
        raise ValueError(f"{filename} has incomplete CV groups.")
    if not bool(
        np.isfinite(scores.loc[:, ["r2", "mae", "rmse"]].to_numpy(dtype=float)).all()
    ):
        raise ValueError(f"{filename} has non-finite metrics.")


def verify_predictions(
    predictions: pd.DataFrame,
    *,
    filename: str,
    context_columns: Sequence[str],
) -> None:
    required = (
        *context_columns,
        "target",
        "target_column",
        "feature_set",
        "estimator",
        "fold",
        "query_index",
        "y_true",
        "y_pred",
    )
    _require_result_columns(predictions, required, filename)
    unique_key = [
        *context_columns,
        "target",
        "feature_set",
        "estimator",
        "query_index",
    ]
    if bool(predictions.duplicated(unique_key).any()):
        raise ValueError(f"{filename} has duplicate out-of-fold predictions.")
    if not bool(
        np.isfinite(predictions.loc[:, ["y_true", "y_pred"]].to_numpy(dtype=float)).all()
    ):
        raise ValueError(f"{filename} has non-finite predictions.")


def verify_classification_results(
    scores: pd.DataFrame,
    summary: pd.DataFrame,
    predictions: pd.DataFrame,
    *,
    feature_sets: set[str],
) -> None:
    context_columns = ("model_key", "layer")
    score_required = (
        *context_columns,
        "target",
        "target_column",
        "feature_set",
        "classifier",
        "fold",
        "n_samples",
        "n_train",
        "n_test",
        "n_features",
        "low_threshold",
        "high_threshold",
        "roc_auc",
    )
    _require_result_columns(
        scores, score_required, "ess_classification_fold_scores.csv"
    )
    if set(scores["feature_set"].astype(str)) != feature_sets:
        raise ValueError("Classification results have unexpected feature sets.")
    expected_classifiers = {"LogisticRegression", "RandomForestClassifier"}
    if set(scores["classifier"].astype(str)) != expected_classifiers:
        raise ValueError("Classification results have unexpected classifiers.")
    if set(scores["target"].astype(str)) != {"ESS low vs. high"}:
        raise ValueError("Classification results have an unexpected target.")
    grouping = [*context_columns, "feature_set", "classifier"]
    fold_counts = scores.groupby(grouping, dropna=False)["fold"].nunique()
    if not bool((fold_counts == N_SPLITS).all()):
        raise ValueError("Classification results have incomplete CV groups.")
    auc = pd.to_numeric(scores["roc_auc"], errors="raise").to_numpy(dtype=float)
    if not bool(np.isfinite(auc).all()) or not bool(((auc >= 0.0) & (auc <= 1.0)).all()):
        raise ValueError("Classification ROC-AUC values are invalid.")

    prediction_required = (
        *context_columns,
        "target",
        "target_column",
        "feature_set",
        "classifier",
        "fold",
        "query_index",
        "class_label",
        "probability_high",
    )
    _require_result_columns(
        predictions,
        prediction_required,
        "ess_classification_oof_predictions.csv",
    )
    prediction_key = [
        *context_columns,
        "feature_set",
        "classifier",
        "query_index",
    ]
    if bool(predictions.duplicated(prediction_key).any()):
        raise ValueError("Classification OOF predictions contain duplicate rows.")
    if not set(pd.to_numeric(predictions["class_label"], errors="raise")) <= {0, 1}:
        raise ValueError("Classification OOF labels are not binary.")
    probabilities = pd.to_numeric(
        predictions["probability_high"], errors="raise"
    ).to_numpy(dtype=float)
    if not bool(np.isfinite(probabilities).all()) or not bool(
        ((probabilities >= 0.0) & (probabilities <= 1.0)).all()
    ):
        raise ValueError("Classification OOF probabilities are invalid.")

    summary_keys = [
        *context_columns,
        "target",
        "target_column",
        "feature_set",
        "classifier",
        "n_samples",
        "n_features",
        "low_threshold",
        "high_threshold",
    ]
    recomputed = (
        scores.groupby(summary_keys, sort=False, dropna=False)["roc_auc"]
        .mean()
        .rename("expected")
        .reset_index()
    )
    comparison = recomputed.merge(
        summary,
        on=summary_keys,
        how="outer",
        indicator=True,
    )
    if not bool((comparison["_merge"] == "both").all()):
        raise ValueError("Classification summary has missing or extra groups.")
    if not np.allclose(
        comparison["expected"], comparison["roc_auc_mean"], rtol=1e-9, atol=1e-11
    ):
        raise ValueError("Classification summary has incorrect mean ROC-AUC values.")


def verify_summary_means(
    scores: pd.DataFrame,
    summary: pd.DataFrame,
    *,
    context_columns: Sequence[str],
    filename: str,
) -> None:
    group_columns = [
        *context_columns,
        "target",
        "target_column",
        "feature_set",
        "estimator",
        "n_samples",
        "n_features",
    ]
    recomputed = (
        scores.groupby(group_columns, sort=False, dropna=False)
        .agg(
            r2_mean=("r2", "mean"),
            mae_mean=("mae", "mean"),
            rmse_mean=("rmse", "mean"),
        )
        .reset_index()
    )
    comparison = recomputed.merge(
        summary,
        on=group_columns,
        how="outer",
        suffixes=("_expected", "_observed"),
        indicator=True,
    )
    if not bool((comparison["_merge"] == "both").all()):
        raise ValueError(f"{filename} has missing or extra summary groups.")
    for metric in ("r2_mean", "mae_mean", "rmse_mean"):
        if not np.allclose(
            comparison[f"{metric}_expected"],
            comparison[f"{metric}_observed"],
            rtol=1e-9,
            atol=1e-11,
        ):
            raise ValueError(f"{filename} has incorrect {metric} values.")


def compare_reference_summaries(
    *,
    generated_dir: Path,
    reference_dir: Path,
    rtol: float,
    atol: float,
) -> dict[str, float]:
    """Compare compact paper-table values with committed numeric references."""

    generated_path = generated_dir / "paper_ess_scores.csv"
    generated = pd.read_csv(generated_path)
    key_columns = ["model_key", "layer", "k", "feature_set"]
    metric_columns = ["ridge_r2", "rf_r2", "logreg_auc", "rf_auc"]
    count_columns = ["n_regression", "n_classification"]
    _require_result_columns(
        generated,
        (*key_columns, *metric_columns, *count_columns),
        generated_path.name,
    )

    maxima: dict[str, float] = {}
    for filename in REFERENCE_FILES:
        path = reference_dir / filename
        if not path.is_file():
            raise ValueError(f"Missing committed reference summary: {path}")
        reference = pd.read_csv(path)
        _require_result_columns(
            reference,
            (*key_columns, *metric_columns, *count_columns),
            filename,
        )
        selected = generated.merge(
            reference.loc[:, [*key_columns]],
            on=key_columns,
            how="inner",
            validate="one_to_one",
        )
        comparison = selected.merge(
            reference,
            on=key_columns,
            how="outer",
            suffixes=("_generated", "_reference"),
            indicator=True,
            validate="one_to_one",
        )
        if len(comparison) != len(reference) or not bool(
            (comparison["_merge"] == "both").all()
        ):
            raise ValueError(f"{filename} keys do not match paper_ess_scores.csv.")

        max_delta = 0.0
        failures: list[str] = []
        for column in metric_columns:
            generated_values = comparison[f"{column}_generated"].to_numpy(dtype=float)
            reference_values = comparison[f"{column}_reference"].to_numpy(dtype=float)
            deltas = np.abs(generated_values - reference_values)
            max_delta = max(max_delta, float(np.max(deltas)))
            close = np.isclose(
                generated_values,
                reference_values,
                rtol=rtol,
                atol=atol,
            )
            if not bool(close.all()):
                failures.append(
                    f"{column} max_abs_delta={float(np.max(deltas[~close])):.6g}"
                )
        for column in count_columns:
            generated_values = pd.to_numeric(
                comparison[f"{column}_generated"], errors="raise"
            ).to_numpy(dtype=int)
            reference_values = pd.to_numeric(
                comparison[f"{column}_reference"], errors="raise"
            ).to_numpy(dtype=int)
            if not np.array_equal(generated_values, reference_values):
                failures.append(f"{column} differs")
        if failures:
            raise ValueError(
                f"{filename} differs beyond rtol={rtol:g}, atol={atol:g}: "
                + "; ".join(failures)
            )
        maxima[filename] = max_delta
    return maxima


def verify_generated_results(
    results_dir: Path, *, checkpoint_expected: bool, extended: bool
) -> list[Path]:
    paths = require_files(results_dir, checkpoint_expected)
    main_scores = pd.read_csv(results_dir / "main_fold_scores.csv")
    main_summary = pd.read_csv(results_dir / "main_cv_summary.csv")
    main_predictions = pd.read_csv(results_dir / "main_oof_predictions.csv")
    verify_scores(
        main_scores,
        filename="main_fold_scores.csv",
        context_columns=("model_key", "layer"),
        targets=set(MAIN_TARGETS) if extended else {"ESS"},
        feature_sets=set(FEATURE_SET_ORDER)
        if extended
        else {"full", "no_frequency"},
    )
    verify_predictions(
        main_predictions,
        filename="main_oof_predictions.csv",
        context_columns=("model_key", "layer"),
    )
    verify_summary_means(
        main_scores,
        main_summary,
        context_columns=("model_key", "layer"),
        filename="main_cv_summary.csv",
    )
    classification_scores = pd.read_csv(
        results_dir / "ess_classification_fold_scores.csv"
    )
    classification_summary = pd.read_csv(
        results_dir / "ess_classification_summary.csv"
    )
    classification_predictions = pd.read_csv(
        results_dir / "ess_classification_oof_predictions.csv"
    )
    verify_classification_results(
        classification_scores,
        classification_summary,
        classification_predictions,
        feature_sets=set(FEATURE_SET_ORDER)
        if extended
        else {"full", "no_frequency"},
    )

    if checkpoint_expected:
        checkpoint_scores = pd.read_csv(results_dir / "checkpoint_fold_scores.csv")
        checkpoint_summary = pd.read_csv(results_dir / "checkpoint_cv_summary.csv")
        checkpoint_predictions = pd.read_csv(
            results_dir / "checkpoint_oof_predictions.csv"
        )
        checkpoint_context = [
            "model_family",
            "checkpoint",
            "checkpoint_order",
            "training_step",
            "training_tokens_billion",
            "model_revision",
            "layer",
        ]
        verify_scores(
            checkpoint_scores,
            filename="checkpoint_fold_scores.csv",
            context_columns=checkpoint_context,
            targets={"ESS"},
            feature_sets=set(FEATURE_SET_ORDER) if extended else {"full"},
        )
        verify_predictions(
            checkpoint_predictions,
            filename="checkpoint_oof_predictions.csv",
            context_columns=checkpoint_context,
        )
        verify_summary_means(
            checkpoint_scores,
            checkpoint_summary,
            context_columns=checkpoint_context,
            filename="checkpoint_cv_summary.csv",
        )
    verify_no_personal_paths(paths)
    return paths


def verify_determinism(
    *,
    paths: BundlePaths,
    current_results: Path,
    skip_checkpoints: bool,
    require_checkpoints: bool,
    extended: bool,
) -> None:
    with tempfile.TemporaryDirectory(prefix="local_geometry_reproduction_") as raw_temp:
        rerun_dir = Path(raw_temp) / "generated"
        rerun_paths = run_analysis(
            paths=paths,
            output_dir=rerun_dir,
            skip_checkpoints=skip_checkpoints,
            require_checkpoints=require_checkpoints,
            extended=extended,
        )
        rerun_names = sorted(path.name for path in rerun_paths)
        current_names = sorted(
            path.name
            for path in current_results.iterdir()
            if path.is_file() and path.name in rerun_names
        )
        if current_names != rerun_names:
            raise ValueError(
                "Current and rerun artifact sets differ: "
                f"current={current_names}, rerun={rerun_names}"
            )
        mismatched = [
            name
            for name in rerun_names
            if file_sha256(current_results / name) != file_sha256(rerun_dir / name)
        ]
        if mismatched:
            raise ValueError(
                "Deterministic rerun differs for: " + ", ".join(mismatched)
            )


def main() -> None:
    args = parse_args()
    paths = resolve_paths(args)
    bundle = load_bundle(
        paths,
        skip_checkpoints=bool(args.skip_checkpoints),
        require_checkpoints=bool(args.require_checkpoints),
    )
    checkpoint_expected = bundle.checkpoint_targets is not None
    manifest = json.loads(
        (args.generated_dir / "analysis_manifest.json").read_text(encoding="utf-8")
    )
    mode = manifest.get("analysis_mode")
    if mode not in {"paper_core", "extended"}:
        raise ValueError(f"Unknown or missing analysis_mode in manifest: {mode!r}")
    extended = mode == "extended"
    generated_paths = verify_generated_results(
        args.generated_dir,
        checkpoint_expected=checkpoint_expected,
        extended=extended,
    )
    verify_manifest(
        args.generated_dir,
        expected_checkpoint=checkpoint_expected,
        expected_feature_sets=bundle.feature_sets,
        extended=extended,
    )
    verify_feature_manifest(args.generated_dir, feature_manifest(bundle))
    reference_deltas = compare_reference_summaries(
        generated_dir=args.generated_dir,
        reference_dir=args.reference_dir,
        rtol=float(args.rtol),
        atol=float(args.atol),
    )
    if args.check_determinism:
        verify_determinism(
            paths=paths,
            current_results=args.generated_dir,
            skip_checkpoints=bool(args.skip_checkpoints),
            require_checkpoints=bool(args.require_checkpoints),
            extended=extended,
        )

    print("OK: parquet schemas and query-index coverage")
    print("OK: no raw text or target leakage in the feature bundle")
    print("OK: identifiers and hashes are excluded from every model matrix")
    print("OK: fixed regression/classification protocols and OOF coverage")
    for filename, delta in sorted(reference_deltas.items()):
        print(f"OK: {filename} max absolute numeric delta = {delta:.3g}")
    print(f"OK: {len(generated_paths)} generated artifact(s) verified")
    if args.check_determinism:
        print("OK: byte-identical deterministic rerun")


if __name__ == "__main__":
    main()
