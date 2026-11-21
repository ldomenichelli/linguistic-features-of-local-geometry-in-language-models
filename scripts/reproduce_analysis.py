#!/usr/bin/env python3
"""Reproduce the paper's deterministic CPU prediction analyses.

The script joins public, non-text linguistic predictors to pointwise intrinsic-
dimension targets by ``query_index``.  Every preprocessing operation is fitted
inside a training fold.  Outputs contain row identifiers only for auditing out-
of-fold coverage; identifiers are never supplied to a model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import warnings
from collections import OrderedDict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEED = 42
N_SPLITS = 5
RIDGE_ALPHA = 1.0
RF_TREES = 300
RF_MIN_SAMPLES_LEAF = 2
RF_N_JOBS = -1
LOW_QUANTILE = 0.20
HIGH_QUANTILE = 0.80
LOGISTIC_MAX_ITER = 3000

FREQUENCY_FEATURES = (
    "min_frequency_class",
    "median_frequency_class",
    "max_frequency_class",
)
RAW_SURFACE_FEATURES = (
    "n_sentences",
    "n_tokens",
    "tokens_per_sent",
    "char_per_tok",
)
FEATURE_SET_ORDER = ("full", "no_frequency", "no_raw")

FEATURE_REQUIRED_COLUMNS = ("query_index", "text_sha256")
MAIN_REQUIRED_COLUMNS = ("model_key", "layer", "query_index")
CHECKPOINT_REQUIRED_COLUMNS = (
    "model_family",
    "checkpoint",
    "model_revision",
    "layer",
    "query_index",
)

RAW_TEXT_COLUMN_NAMES = frozenset(
    {
        "text",
        "raw_text",
        "clean_text",
        "sentence",
        "excerpt",
        "prompt",
        "content",
        "document",
    }
)
TARGET_COLUMN_NAMES = frozenset(
    {
        "pointwise_id",
        "pointwise_mle",
        "pointwise_mle_id",
        "pointwise_ess",
        "pointwise_fci_id",
        "ess",
        "mle",
        "fci",
    }
)
ALLOWED_FEATURE_IDENTIFIERS = frozenset(FEATURE_REQUIRED_COLUMNS)
KNOWN_IDENTITY_COLUMN_NAMES = frozenset(
    {
        "id",
        "index",
        "row_id",
        "row_index",
        "line_index",
        "source_id",
        "source_index",
        "query_id",
        "query_source_index",
        "document_id",
        "sentence_id",
        "text_id",
    }
)

MAIN_TARGETS = OrderedDict(
    (
        ("MLE", "pointwise_mle"),
        ("ESS", "pointwise_ess"),
        ("FCI", "pointwise_fci_id"),
    )
)


@dataclass(frozen=True)
class AnalysisConfig:
    """Fixed analysis settings; overrides are intended only for unit tests."""

    n_splits: int = N_SPLITS
    seed: int = SEED
    ridge_alpha: float = RIDGE_ALPHA
    rf_trees: int = RF_TREES
    rf_min_samples_leaf: int = RF_MIN_SAMPLES_LEAF
    rf_n_jobs: int = RF_N_JOBS
    low_quantile: float = LOW_QUANTILE
    high_quantile: float = HIGH_QUANTILE
    logistic_max_iter: int = LOGISTIC_MAX_ITER


@dataclass(frozen=True)
class BundlePaths:
    features: Path
    main_targets: Path
    checkpoint_targets: Path


@dataclass
class LoadedBundle:
    features: pd.DataFrame
    main_targets: pd.DataFrame
    checkpoint_targets: pd.DataFrame | None
    feature_sets: OrderedDict[str, tuple[str, ...]]
    main_target_sources: dict[str, str]
    checkpoint_target_source: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/derived"),
        help="Directory containing the three derived parquet files.",
    )
    parser.add_argument("--features", type=Path, default=None)
    parser.add_argument("--main-targets", type=Path, default=None)
    parser.add_argument("--checkpoint-targets", type=Path, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/generated"),
    )
    parser.add_argument(
        "--skip-checkpoints",
        action="store_true",
        help="Run only the main-model analyses.",
    )
    parser.add_argument(
        "--require-checkpoints",
        action="store_true",
        help="Fail rather than warn if checkpoint_targets.parquet is absent.",
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help=(
            "Run MLE/ESS/FCI with every feature set and every checkpoint ablation. "
            "The default reproduces the compact paper-core ESS tables and full-feature "
            "checkpoint trajectory."
        ),
    )
    args = parser.parse_args()
    if args.skip_checkpoints and args.require_checkpoints:
        parser.error("--skip-checkpoints and --require-checkpoints are incompatible.")
    return args


def resolve_bundle_paths(args: argparse.Namespace) -> BundlePaths:
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


def _duplicate_columns(dataframe: pd.DataFrame) -> list[str]:
    return sorted(
        {str(column) for column in dataframe.columns[dataframe.columns.duplicated()].tolist()}
    )


def _raw_text_columns(columns: Iterable[object]) -> list[str]:
    found: list[str] = []
    for column in columns:
        name = str(column)
        lowered = name.casefold()
        is_text_hash = lowered == "text_sha256"
        if (
            lowered in RAW_TEXT_COLUMN_NAMES
            or lowered.endswith("_text")
            or lowered.startswith("text_")
        ) and not is_text_hash:
            found.append(name)
    return sorted(found)


def _looks_like_identity_column(column: object) -> bool:
    name = str(column).casefold()
    if name in ALLOWED_FEATURE_IDENTIFIERS:
        return False
    return (
        name in KNOWN_IDENTITY_COLUMN_NAMES
        or name.endswith("_sha256")
        or name.endswith("_index")
        or name.endswith("_id")
    )


def _require_columns(dataframe: pd.DataFrame, required: Sequence[str], label: str) -> None:
    missing = [column for column in required if column not in dataframe.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def _validate_no_duplicate_columns(dataframe: pd.DataFrame, label: str) -> None:
    duplicate = _duplicate_columns(dataframe)
    if duplicate:
        raise ValueError(f"{label} has duplicate columns: {', '.join(duplicate)}")


def _validate_no_raw_text(dataframe: pd.DataFrame, label: str) -> None:
    raw_text = _raw_text_columns(dataframe.columns)
    if raw_text:
        raise ValueError(
            f"{label} contains prohibited raw-text columns: {', '.join(raw_text)}"
        )


def _validate_sha256(series: pd.Series, label: str) -> None:
    if bool(series.isna().any()):
        raise ValueError(f"{label}.text_sha256 contains missing values.")
    valid = series.astype(str).str.fullmatch(r"[0-9a-fA-F]{64}", na=False)
    if not bool(valid.all()):
        count = int((~valid).sum())
        raise ValueError(
            f"{label}.text_sha256 has {count} value(s) that are not 64 hexadecimal characters."
        )


def validate_features(dataframe: pd.DataFrame) -> list[str]:
    """Validate the public feature table and return predictor columns."""

    label = "features.parquet"
    _validate_no_duplicate_columns(dataframe, label)
    _require_columns(dataframe, FEATURE_REQUIRED_COLUMNS, label)
    _validate_no_raw_text(dataframe, label)
    _validate_sha256(dataframe["text_sha256"], label)

    if bool(dataframe["query_index"].isna().any()):
        raise ValueError(f"{label}.query_index contains missing values.")
    if bool(dataframe["query_index"].duplicated().any()):
        raise ValueError(f"{label}.query_index must contain exactly one row per query.")

    leaked_targets = sorted(
        column
        for column in dataframe.columns
        if str(column).casefold() in TARGET_COLUMN_NAMES
    )
    if leaked_targets:
        raise ValueError(
            f"{label} contains target leakage columns: {', '.join(map(str, leaked_targets))}"
        )

    unexpected_identity = sorted(
        str(column)
        for column in dataframe.columns
        if _looks_like_identity_column(column)
    )
    if unexpected_identity:
        raise ValueError(
            f"{label} contains unsupported identity columns: "
            f"{', '.join(unexpected_identity)}"
        )

    predictors = [
        str(column)
        for column in dataframe.columns
        if str(column) not in ALLOWED_FEATURE_IDENTIFIERS
    ]
    if not predictors:
        raise ValueError(f"{label} contains no numeric predictors.")

    non_numeric = [
        column
        for column in predictors
        if not (is_numeric_dtype(dataframe[column]) or is_bool_dtype(dataframe[column]))
    ]
    if non_numeric:
        raise ValueError(
            f"{label} predictors must all be numeric; found: {', '.join(non_numeric)}"
        )

    all_missing = [column for column in predictors if bool(dataframe[column].isna().all())]
    if all_missing:
        raise ValueError(
            f"{label} has all-missing predictors that cannot be median-imputed: "
            f"{', '.join(all_missing)}"
        )

    numeric = dataframe.loc[:, predictors].astype(float)
    infinite = np.isinf(numeric.to_numpy()).any(axis=0)
    infinite_columns = [
        column for column, has_infinite in zip(predictors, infinite) if bool(has_infinite)
    ]
    if infinite_columns:
        raise ValueError(
            f"{label} contains infinite predictor values: {', '.join(infinite_columns)}"
        )
    return predictors


def build_feature_sets(
    predictors: Sequence[str], *, warn_missing: bool = True
) -> OrderedDict[str, tuple[str, ...]]:
    """Build the three preregistered feature sets from exact paper column names."""

    predictor_set = set(predictors)
    missing_frequency = sorted(set(FREQUENCY_FEATURES) - predictor_set)
    missing_raw = sorted(set(RAW_SURFACE_FEATURES) - predictor_set)
    if warn_missing and missing_frequency:
        warnings.warn(
            "Frequency ablation columns absent from features.parquet: "
            + ", ".join(missing_frequency),
            stacklevel=2,
        )
    if warn_missing and missing_raw:
        warnings.warn(
            "Raw/surface ablation columns absent from features.parquet: "
            + ", ".join(missing_raw),
            stacklevel=2,
        )

    feature_sets: OrderedDict[str, tuple[str, ...]] = OrderedDict()
    feature_sets["full"] = tuple(predictors)
    feature_sets["no_frequency"] = tuple(
        column for column in predictors if column not in FREQUENCY_FEATURES
    )
    feature_sets["no_raw"] = tuple(
        column for column in predictors if column not in RAW_SURFACE_FEATURES
    )
    empty = [name for name, columns in feature_sets.items() if not columns]
    if empty:
        raise ValueError(f"Feature ablation produced empty set(s): {', '.join(empty)}")
    return feature_sets


def _validate_group_keys(
    dataframe: pd.DataFrame, columns: Sequence[str], label: str
) -> None:
    missing_counts = {
        column: int(dataframe[column].isna().sum())
        for column in columns
        if bool(dataframe[column].isna().any())
    }
    if missing_counts:
        details = ", ".join(f"{key}={value}" for key, value in missing_counts.items())
        raise ValueError(f"{label} has missing grouping identifiers: {details}")


def _coerce_numeric_target(dataframe: pd.DataFrame, column: str, label: str) -> None:
    try:
        values = pd.to_numeric(dataframe[column], errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}.{column} must be numeric.") from exc
    infinite = np.isinf(values.dropna().astype(float).to_numpy())
    if bool(infinite.any()):
        raise ValueError(f"{label}.{column} contains infinite values.")
    dataframe[column] = values


def validate_main_targets(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Validate and canonicalize main-model target columns."""

    label = "main_targets.parquet"
    dataframe = dataframe.copy()
    _validate_no_duplicate_columns(dataframe, label)
    _require_columns(dataframe, MAIN_REQUIRED_COLUMNS, label)
    _validate_no_raw_text(dataframe, label)
    _validate_group_keys(dataframe, MAIN_REQUIRED_COLUMNS, label)

    key_columns = list(MAIN_REQUIRED_COLUMNS)
    if bool(dataframe.duplicated(key_columns).any()):
        raise ValueError(
            f"{label} must have one row per model_key/layer/query_index combination."
        )

    mle_aliases = ("pointwise_mle", "pointwise_mle_id", "pointwise_id")
    present_mle_aliases = [
        column for column in mle_aliases if column in dataframe.columns
    ]
    if not present_mle_aliases:
        raise ValueError(
            f"{label} requires pointwise_mle or a supported legacy alias "
            "(pointwise_mle_id or pointwise_id)."
        )
    mle_source = present_mle_aliases[0]
    reference = pd.to_numeric(dataframe[mle_source], errors="coerce")
    for other in present_mle_aliases[1:]:
        values = pd.to_numeric(dataframe[other], errors="coerce")
        comparable = reference.notna() & values.notna()
        if bool(comparable.any()) and not np.allclose(
            reference[comparable].to_numpy(dtype=float),
            values[comparable].to_numpy(dtype=float),
            rtol=1e-10,
            atol=1e-12,
        ):
            raise ValueError(
                f"{label} has disagreeing MLE alias columns: "
                f"{mle_source} and {other}."
            )
    if mle_source != "pointwise_mle":
        dataframe["pointwise_mle"] = dataframe[mle_source]

    _require_columns(dataframe, ("pointwise_ess", "pointwise_fci_id"), label)
    for column in MAIN_TARGETS.values():
        _coerce_numeric_target(dataframe, column, label)

    sources = {
        "MLE": mle_source,
        "ESS": "pointwise_ess",
        "FCI": "pointwise_fci_id",
    }
    return dataframe, sources


def _find_checkpoint_target_column(dataframe: pd.DataFrame) -> str:
    candidates = ("pointwise_ess", "ESS", "ess")
    present = [column for column in candidates if column in dataframe.columns]
    if not present:
        raise ValueError(
            "checkpoint_targets.parquet requires one ESS column: pointwise_ess, ESS, or ess."
        )
    source = present[0]
    if len(present) > 1:
        reference = pd.to_numeric(dataframe[source], errors="coerce")
        for other in present[1:]:
            values = pd.to_numeric(dataframe[other], errors="coerce")
            comparable = reference.notna() & values.notna()
            if bool(comparable.any()) and not np.allclose(
                reference[comparable].to_numpy(dtype=float),
                values[comparable].to_numpy(dtype=float),
                rtol=1e-10,
                atol=1e-12,
            ):
                raise ValueError(
                    "checkpoint_targets.parquet has disagreeing ESS alias columns."
                )
    return source


def validate_checkpoint_targets(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, str]:
    """Validate and canonicalize checkpoint ESS targets."""

    label = "checkpoint_targets.parquet"
    dataframe = dataframe.copy()
    _validate_no_duplicate_columns(dataframe, label)
    _require_columns(dataframe, CHECKPOINT_REQUIRED_COLUMNS, label)
    _validate_no_raw_text(dataframe, label)
    _validate_group_keys(dataframe, CHECKPOINT_REQUIRED_COLUMNS, label)

    order_columns = [
        "checkpoint_order",
        "training_step",
        "training_tokens_billion",
    ]
    _require_columns(dataframe, order_columns, label)
    for column in order_columns:
        if bool(dataframe[column].isna().any()):
            raise ValueError(f"{label}.{column} contains missing values.")
        try:
            dataframe[column] = pd.to_numeric(dataframe[column], errors="raise")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label}.{column} must be numeric.") from exc

    key_columns = [
        "model_family",
        "checkpoint",
        "model_revision",
        "layer",
        "query_index",
    ]
    if bool(dataframe.duplicated(key_columns).any()):
        raise ValueError(
            f"{label} must have one row per family/checkpoint/revision/layer/query_index."
        )

    metadata_keys = ["model_family", "checkpoint", "model_revision", "layer"]
    for column in order_columns:
        counts = dataframe.groupby(metadata_keys, dropna=False)[column].nunique(dropna=False)
        if bool((counts > 1).any()):
            raise ValueError(
                f"{label}.{column} is not constant within a checkpoint/layer group."
            )

    source = _find_checkpoint_target_column(dataframe)
    if source != "pointwise_ess":
        dataframe["pointwise_ess"] = dataframe[source]
    _coerce_numeric_target(dataframe, "pointwise_ess", label)
    return dataframe, source


def _read_parquet(path: Path, label: str) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    try:
        return pd.read_parquet(path)
    except Exception as exc:  # pragma: no cover - backend-specific details
        raise RuntimeError(f"Could not read {label}: {path}") from exc


def load_bundle(
    paths: BundlePaths,
    *,
    skip_checkpoints: bool = False,
    require_checkpoints: bool = False,
) -> LoadedBundle:
    """Load, validate, and normalize the derived public analysis bundle."""

    features = _read_parquet(paths.features, "features.parquet")
    predictors = validate_features(features)
    feature_sets = build_feature_sets(predictors)

    main_raw = _read_parquet(paths.main_targets, "main_targets.parquet")
    main_targets, main_sources = validate_main_targets(main_raw)
    _validate_target_coverage(
        features,
        main_targets,
        "main_targets.parquet",
        group_columns=("model_key", "layer"),
    )

    checkpoint_targets: pd.DataFrame | None = None
    checkpoint_source: str | None = None
    if not skip_checkpoints:
        if paths.checkpoint_targets.is_file():
            checkpoint_raw = _read_parquet(
                paths.checkpoint_targets, "checkpoint_targets.parquet"
            )
            checkpoint_targets, checkpoint_source = validate_checkpoint_targets(
                checkpoint_raw
            )
            _validate_target_coverage(
                features,
                checkpoint_targets,
                "checkpoint_targets.parquet",
                group_columns=(
                    "model_family",
                    "checkpoint",
                    "model_revision",
                    "layer",
                ),
            )
        elif require_checkpoints:
            raise FileNotFoundError(
                f"Missing checkpoint_targets.parquet: {paths.checkpoint_targets}"
            )
        else:
            warnings.warn(
                "checkpoint_targets.parquet is absent; checkpoint analyses will be skipped.",
                stacklevel=2,
            )

    return LoadedBundle(
        features=features,
        main_targets=main_targets,
        checkpoint_targets=checkpoint_targets,
        feature_sets=feature_sets,
        main_target_sources=main_sources,
        checkpoint_target_source=checkpoint_source,
    )


def _validate_target_coverage(
    features: pd.DataFrame,
    targets: pd.DataFrame,
    label: str,
    *,
    group_columns: Sequence[str],
) -> None:
    """Require every profiled row in every target group; extra targets are allowed."""

    feature_ids = pd.Index(features["query_index"])
    for key, group in _stable_group_items(targets, group_columns):
        target_ids = pd.Index(group["query_index"])
        missing = feature_ids.difference(target_ids)
        if len(missing):
            preview = ", ".join(map(str, missing[:5].tolist()))
            context = ", ".join(
                f"{column}={value}" for column, value in zip(group_columns, key)
            )
            raise ValueError(
                f"{label} group ({context}) is missing {len(missing)} profiled "
                "query_index value(s)"
                + (f": {preview}" if preview else ".")
            )


def _make_estimator(name: str, config: AnalysisConfig) -> Pipeline:
    if name == "Ridge":
        return Pipeline(
            steps=(
                ("median_imputer", SimpleImputer(strategy="median")),
                ("standard_scaler", StandardScaler()),
                ("regressor", Ridge(alpha=config.ridge_alpha)),
            )
        )
    if name == "RandomForest":
        return Pipeline(
            steps=(
                ("median_imputer", SimpleImputer(strategy="median")),
                (
                    "regressor",
                    RandomForestRegressor(
                        n_estimators=config.rf_trees,
                        min_samples_leaf=config.rf_min_samples_leaf,
                        random_state=config.seed,
                        n_jobs=config.rf_n_jobs,
                    ),
                ),
            )
        )
    raise ValueError(f"Unknown estimator: {name}")


def _make_classifier(name: str, config: AnalysisConfig) -> Pipeline:
    if name == "LogisticRegression":
        return Pipeline(
            steps=(
                ("median_imputer", SimpleImputer(strategy="median")),
                ("standard_scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=config.logistic_max_iter,
                        random_state=config.seed,
                    ),
                ),
            )
        )
    if name == "RandomForestClassifier":
        return Pipeline(
            steps=(
                ("median_imputer", SimpleImputer(strategy="median")),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=config.rf_trees,
                        min_samples_leaf=config.rf_min_samples_leaf,
                        class_weight="balanced_subsample",
                        random_state=config.seed,
                        n_jobs=config.rf_n_jobs,
                    ),
                ),
            )
        )
    raise ValueError(f"Unknown classifier: {name}")


def _stable_group_items(
    dataframe: pd.DataFrame, group_columns: Sequence[str]
) -> list[tuple[tuple[object, ...], pd.DataFrame]]:
    grouped = dataframe.groupby(list(group_columns), sort=False, dropna=False)
    items: list[tuple[tuple[object, ...], pd.DataFrame]] = []
    for key, group in grouped:
        key_tuple = key if isinstance(key, tuple) else (key,)
        items.append((key_tuple, group))
    return sorted(items, key=lambda item: tuple(str(value) for value in item[0]))


def cross_validate_regression(
    dataframe: pd.DataFrame,
    *,
    predictors: Sequence[str],
    target_column: str,
    target_name: str,
    feature_set: str,
    context: Mapping[str, object],
    config: AnalysisConfig,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Run fixed-fold Ridge and RF and return fold scores plus OOF predictions."""

    prohibited_predictors = [
        column
        for column in predictors
        if (
            str(column) in ALLOWED_FEATURE_IDENTIFIERS
            or _looks_like_identity_column(column)
            or str(column).casefold() in TARGET_COLUMN_NAMES
            or bool(_raw_text_columns((column,)))
        )
    ]
    if prohibited_predictors:
        raise ValueError(
            "Model matrix contains prohibited identity/text/target columns: "
            + ", ".join(map(str, prohibited_predictors))
        )

    columns = ["query_index", target_column, *predictors]
    work = dataframe.loc[:, columns].copy()
    target_values = pd.to_numeric(work[target_column], errors="coerce")
    finite_target = target_values.notna() & np.isfinite(target_values.astype(float))
    work = work.loc[finite_target].copy()
    work[target_column] = target_values.loc[finite_target].astype(float)
    work = work.sort_values("query_index", kind="stable").reset_index(drop=True)

    minimum_rows = 2 * config.n_splits
    if len(work) < minimum_rows:
        context_text = ", ".join(f"{key}={value}" for key, value in context.items())
        raise ValueError(
            f"Need at least {minimum_rows} finite rows for {target_name} ({context_text}); "
            f"found {len(work)}."
        )

    x_values = work.loc[:, list(predictors)]
    y_values = work[target_column].to_numpy(dtype=float)
    query_indices = work["query_index"].to_numpy()
    splitter = KFold(
        n_splits=config.n_splits,
        shuffle=True,
        random_state=config.seed,
    )
    folds = list(splitter.split(x_values))

    scores: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    for estimator_name in ("Ridge", "RandomForest"):
        for fold_index, (train_index, test_index) in enumerate(folds, start=1):
            estimator = _make_estimator(estimator_name, config)
            estimator.fit(x_values.iloc[train_index], y_values[train_index])
            predicted = np.asarray(
                estimator.predict(x_values.iloc[test_index]), dtype=float
            )
            observed = y_values[test_index]
            residual = predicted - observed

            score_row: dict[str, object] = dict(context)
            score_row.update(
                {
                    "target": target_name,
                    "target_column": target_column,
                    "feature_set": feature_set,
                    "estimator": estimator_name,
                    "fold": fold_index,
                    "n_samples": len(work),
                    "n_train": len(train_index),
                    "n_test": len(test_index),
                    "n_features": len(predictors),
                    "r2": float(r2_score(observed, predicted)),
                    "mae": float(mean_absolute_error(observed, predicted)),
                    "rmse": float(math.sqrt(float(np.mean(np.square(residual))))),
                }
            )
            scores.append(score_row)

            for local_index, row_index in enumerate(test_index):
                prediction_row: dict[str, object] = dict(context)
                prediction_row.update(
                    {
                        "target": target_name,
                        "target_column": target_column,
                        "feature_set": feature_set,
                        "estimator": estimator_name,
                        "fold": fold_index,
                        "query_index": query_indices[row_index],
                        "y_true": float(observed[local_index]),
                        "y_pred": float(predicted[local_index]),
                    }
                )
                predictions.append(prediction_row)
    return scores, predictions


def low_high_ess_labels(
    values: pd.Series, config: AnalysisConfig
) -> tuple[pd.Series, float, float]:
    """Label the inclusive bottom/top ESS quantiles exactly as in the paper."""

    numeric = pd.to_numeric(values, errors="coerce")
    finite = numeric.notna() & np.isfinite(numeric.astype(float))
    low_threshold = float(numeric.loc[finite].quantile(config.low_quantile))
    high_threshold = float(numeric.loc[finite].quantile(config.high_quantile))
    labels = pd.Series(pd.NA, index=numeric.index, dtype="object")
    labels.loc[finite & (numeric <= low_threshold)] = "low"
    labels.loc[finite & (numeric >= high_threshold)] = "high"
    return labels, low_threshold, high_threshold


def cross_validate_ess_classification(
    dataframe: pd.DataFrame,
    *,
    predictors: Sequence[str],
    feature_set: str,
    context: Mapping[str, object],
    config: AnalysisConfig,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Run the paper's bottom/top-quintile ESS classification task."""

    prohibited_predictors = [
        column
        for column in predictors
        if (
            str(column) in ALLOWED_FEATURE_IDENTIFIERS
            or _looks_like_identity_column(column)
            or str(column).casefold() in TARGET_COLUMN_NAMES
            or bool(_raw_text_columns((column,)))
        )
    ]
    if prohibited_predictors:
        raise ValueError(
            "Classification matrix contains prohibited identity/text/target columns: "
            + ", ".join(map(str, prohibited_predictors))
        )

    columns = ["query_index", "pointwise_ess", *predictors]
    work = dataframe.loc[:, columns].copy()
    work = work.sort_values("query_index", kind="stable").reset_index(drop=True)
    labels, low_threshold, high_threshold = low_high_ess_labels(
        work["pointwise_ess"], config
    )
    selected = labels.notna()
    work = work.loc[selected].reset_index(drop=True)
    labels = labels.loc[selected].reset_index(drop=True)
    encoded = pd.Categorical(labels.astype(str), categories=["low", "high"]).codes
    if set(encoded.tolist()) != {0, 1}:
        raise ValueError("ESS classification requires both low and high classes.")

    class_counts = pd.Series(encoded).value_counts()
    if int(class_counts.min()) < config.n_splits:
        raise ValueError(
            "ESS classification needs at least "
            f"{config.n_splits} examples per class; got {class_counts.to_dict()}."
        )

    x_values = work.loc[:, list(predictors)]
    query_indices = work["query_index"].to_numpy()
    splitter = StratifiedKFold(
        n_splits=config.n_splits,
        shuffle=True,
        random_state=config.seed,
    )
    folds = list(splitter.split(x_values, encoded))
    scores: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []

    for classifier_name in ("LogisticRegression", "RandomForestClassifier"):
        for fold_index, (train_index, test_index) in enumerate(folds, start=1):
            classifier = _make_classifier(classifier_name, config)
            classifier.fit(x_values.iloc[train_index], encoded[train_index])
            probabilities = np.asarray(
                classifier.predict_proba(x_values.iloc[test_index]), dtype=float
            )[:, 1]
            observed = encoded[test_index]
            auc = float(roc_auc_score(observed, probabilities))
            score_row: dict[str, object] = dict(context)
            score_row.update(
                {
                    "target": "ESS low vs. high",
                    "target_column": "pointwise_ess",
                    "feature_set": feature_set,
                    "classifier": classifier_name,
                    "fold": fold_index,
                    "n_samples": len(work),
                    "n_train": len(train_index),
                    "n_test": len(test_index),
                    "n_features": len(predictors),
                    "low_threshold": low_threshold,
                    "high_threshold": high_threshold,
                    "roc_auc": auc,
                }
            )
            scores.append(score_row)
            for local_index, row_index in enumerate(test_index):
                prediction_row: dict[str, object] = dict(context)
                prediction_row.update(
                    {
                        "target": "ESS low vs. high",
                        "target_column": "pointwise_ess",
                        "feature_set": feature_set,
                        "classifier": classifier_name,
                        "fold": fold_index,
                        "query_index": query_indices[row_index],
                        "class_label": int(observed[local_index]),
                        "probability_high": float(probabilities[local_index]),
                    }
                )
                predictions.append(prediction_row)
    return scores, predictions


def _join_group_to_features(
    group: pd.DataFrame,
    features: pd.DataFrame,
    predictors: Sequence[str],
) -> pd.DataFrame:
    feature_columns = ["query_index", *predictors]
    joined = group.merge(
        features.loc[:, feature_columns],
        on="query_index",
        how="inner",
        validate="one_to_one",
        sort=False,
    )
    if len(joined) != len(features):
        raise ValueError(
            "Target-to-feature alignment did not retain every profiled query: "
            f"expected {len(features)}, found {len(joined)}."
        )
    return joined


def run_main_analyses(
    bundle: LoadedBundle,
    config: AnalysisConfig,
    *,
    target_names: Sequence[str] = tuple(MAIN_TARGETS),
    feature_set_names: Sequence[str] = FEATURE_SET_ORDER,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scores: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    all_predictors = bundle.feature_sets["full"]

    for key, group in _stable_group_items(
        bundle.main_targets, ("model_key", "layer")
    ):
        model_key, layer = key
        joined = _join_group_to_features(group, bundle.features, all_predictors)
        context = OrderedDict((("model_key", model_key), ("layer", layer)))
        for target_name in target_names:
            target_column = MAIN_TARGETS[target_name]
            for feature_set in feature_set_names:
                predictors = bundle.feature_sets[feature_set]
                fold_scores, oof = cross_validate_regression(
                    joined,
                    predictors=predictors,
                    target_column=target_column,
                    target_name=target_name,
                    feature_set=feature_set,
                    context=context,
                    config=config,
                )
                scores.extend(fold_scores)
                predictions.extend(oof)
    return pd.DataFrame(scores), pd.DataFrame(predictions)


def run_main_ess_classification(
    bundle: LoadedBundle,
    config: AnalysisConfig,
    *,
    feature_set_names: Sequence[str] = FEATURE_SET_ORDER,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scores: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    all_predictors = bundle.feature_sets["full"]

    for key, group in _stable_group_items(
        bundle.main_targets, ("model_key", "layer")
    ):
        model_key, layer = key
        joined = _join_group_to_features(group, bundle.features, all_predictors)
        context = OrderedDict((("model_key", model_key), ("layer", layer)))
        for feature_set in feature_set_names:
            predictors = bundle.feature_sets[feature_set]
            fold_scores, oof = cross_validate_ess_classification(
                joined,
                predictors=predictors,
                feature_set=feature_set,
                context=context,
                config=config,
            )
            scores.extend(fold_scores)
            predictions.extend(oof)
    return pd.DataFrame(scores), pd.DataFrame(predictions)


def _checkpoint_context_columns(dataframe: pd.DataFrame) -> tuple[str, ...]:
    return (
        "model_family",
        "checkpoint",
        "checkpoint_order",
        "training_step",
        "training_tokens_billion",
        "model_revision",
        "layer",
    )


def run_checkpoint_analyses(
    bundle: LoadedBundle,
    config: AnalysisConfig,
    *,
    feature_set_names: Sequence[str] = FEATURE_SET_ORDER,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if bundle.checkpoint_targets is None:
        return pd.DataFrame(), pd.DataFrame()

    scores: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    all_predictors = bundle.feature_sets["full"]
    group_columns = _checkpoint_context_columns(bundle.checkpoint_targets)
    for key, group in _stable_group_items(bundle.checkpoint_targets, group_columns):
        context = OrderedDict(zip(group_columns, key))
        joined = _join_group_to_features(group, bundle.features, all_predictors)
        for feature_set in feature_set_names:
            predictors = bundle.feature_sets[feature_set]
            fold_scores, oof = cross_validate_regression(
                joined,
                predictors=predictors,
                target_column="pointwise_ess",
                target_name="ESS",
                feature_set=feature_set,
                context=context,
                config=config,
            )
            scores.extend(fold_scores)
            predictions.extend(oof)
    return pd.DataFrame(scores), pd.DataFrame(predictions)


def summarize_scores(scores: pd.DataFrame, context_columns: Sequence[str]) -> pd.DataFrame:
    group_columns = [
        *context_columns,
        "target",
        "target_column",
        "feature_set",
        "estimator",
        "n_samples",
        "n_features",
    ]
    summary = (
        scores.groupby(group_columns, sort=False, dropna=False)
        .agg(
            r2_mean=("r2", "mean"),
            r2_sd=("r2", lambda values: float(np.std(values, ddof=0))),
            mae_mean=("mae", "mean"),
            mae_sd=("mae", lambda values: float(np.std(values, ddof=0))),
            rmse_mean=("rmse", "mean"),
            rmse_sd=("rmse", lambda values: float(np.std(values, ddof=0))),
            folds=("fold", "nunique"),
        )
        .reset_index()
    )
    return summary


def summarize_classification_scores(
    scores: pd.DataFrame, context_columns: Sequence[str]
) -> pd.DataFrame:
    group_columns = [
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
    return (
        scores.groupby(group_columns, sort=False, dropna=False)
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_sd=(
                "roc_auc",
                lambda values: float(np.std(values, ddof=0)),
            ),
            folds=("fold", "nunique"),
        )
        .reset_index()
    )


def build_paper_ess_summary(
    regression_summary: pd.DataFrame,
    classification_summary: pd.DataFrame,
    *,
    k_value: int,
) -> pd.DataFrame:
    """Create one compact row per model/layer/feature set for reference checks."""

    keys = ["model_key", "layer", "feature_set"]
    regression = regression_summary.loc[
        regression_summary["target"] == "ESS",
        [*keys, "estimator", "r2_mean", "n_samples"],
    ].copy()
    regression_scores = regression.pivot(
        index=keys, columns="estimator", values="r2_mean"
    ).rename(columns={"Ridge": "ridge_r2", "RandomForest": "rf_r2"})
    regression_n = regression.groupby(keys, sort=False)["n_samples"].first().rename(
        "n_regression"
    )

    classification = classification_summary.loc[
        :, [*keys, "classifier", "roc_auc_mean", "n_samples"]
    ].copy()
    classification_scores = classification.pivot(
        index=keys, columns="classifier", values="roc_auc_mean"
    ).rename(
        columns={
            "LogisticRegression": "logreg_auc",
            "RandomForestClassifier": "rf_auc",
        }
    )
    classification_n = classification.groupby(keys, sort=False)["n_samples"].first().rename(
        "n_classification"
    )
    compact = pd.concat(
        (regression_scores, classification_scores, regression_n, classification_n),
        axis=1,
    ).reset_index()
    compact.insert(2, "k", int(k_value))
    columns = [
        "model_key",
        "layer",
        "k",
        "feature_set",
        "ridge_r2",
        "rf_r2",
        "logreg_auc",
        "rf_auc",
        "n_regression",
        "n_classification",
    ]
    return compact.loc[:, columns]


def feature_manifest(bundle: LoadedBundle) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for position, feature in enumerate(bundle.feature_sets["full"], start=1):
        if feature in FREQUENCY_FEATURES:
            family = "frequency"
        elif feature in RAW_SURFACE_FEATURES:
            family = "raw_surface"
        else:
            family = "linguistic"
        rows.append(
            {
                "feature": feature,
                "position": position,
                "family": family,
                "in_full": True,
                "in_no_frequency": feature in bundle.feature_sets["no_frequency"],
                "in_no_raw": feature in bundle.feature_sets["no_raw"],
            }
        )
    return pd.DataFrame(rows)


def _sort_frame(dataframe: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe
    usable = [column for column in columns if column in dataframe.columns]
    return dataframe.sort_values(usable, kind="stable").reset_index(drop=True)


def _write_csv(dataframe: pd.DataFrame, path: Path) -> None:
    dataframe.to_csv(
        path,
        index=False,
        float_format="%.12g",
        lineterminator="\n",
    )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plot_main(summary: pd.DataFrame, output_path: Path) -> None:
    targets = [target for target in MAIN_TARGETS if target in set(summary["target"])]
    if not targets:
        return
    groups = (
        summary.loc[:, ["model_key", "layer"]]
        .drop_duplicates()
        .sort_values(["model_key", "layer"], kind="stable")
        .reset_index(drop=True)
    )
    group_labels = [
        f"{row.model_key}\nL{row.layer}" for row in groups.itertuples(index=False)
    ]
    group_positions = {
        (str(row.model_key), str(row.layer)): index
        for index, row in enumerate(groups.itertuples(index=False))
    }
    styles = {
        ("full", "Ridge"): ("#4c78a8", "-", "o"),
        ("full", "RandomForest"): ("#f58518", "-", "o"),
        ("no_frequency", "Ridge"): ("#4c78a8", "--", "s"),
        ("no_frequency", "RandomForest"): ("#f58518", "--", "s"),
        ("no_raw", "Ridge"): ("#54a24b", ":", "^"),
        ("no_raw", "RandomForest"): ("#e45756", ":", "^"),
    }

    figure, axes = plt.subplots(
        1,
        len(targets),
        figsize=(max(7.5, 3.6 * len(targets)), 3.8),
        sharey=False,
        squeeze=False,
    )
    for axis, target in zip(axes[0], targets):
        target_data = summary.loc[summary["target"] == target]
        for feature_set in FEATURE_SET_ORDER:
            for estimator in ("Ridge", "RandomForest"):
                subset = target_data.loc[
                    (target_data["feature_set"] == feature_set)
                    & (target_data["estimator"] == estimator)
                ].copy()
                if subset.empty:
                    continue
                subset["x"] = [
                    group_positions[(str(model), str(layer))]
                    for model, layer in zip(subset["model_key"], subset["layer"])
                ]
                subset = subset.sort_values("x", kind="stable")
                color, line_style, marker = styles[(feature_set, estimator)]
                axis.plot(
                    subset["x"],
                    subset["r2_mean"],
                    label=f"{estimator} / {feature_set}",
                    color=color,
                    linestyle=line_style,
                    marker=marker,
                    markersize=3.2,
                    linewidth=1.1,
                )
        axis.axhline(0.0, color="0.65", linewidth=0.7)
        axis.set_title(target)
        axis.set_xticks(range(len(group_labels)), group_labels, rotation=45, ha="right")
        axis.set_ylabel("Mean held-out $R^2$")
        axis.grid(axis="y", color="0.9", linewidth=0.6)
    handles, labels = axes[0][0].get_legend_handles_labels()
    figure.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=3,
        fontsize=7,
    )
    figure.suptitle("Five-fold pointwise-ID prediction", fontsize=11)
    figure.tight_layout(rect=(0, 0.15, 1, 0.95))
    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
        metadata={"Software": "local-geometry-reproduction"},
    )
    plt.close(figure)


def _plot_ess_classification(summary: pd.DataFrame, output_path: Path) -> None:
    if summary.empty:
        return
    groups = (
        summary.loc[:, ["model_key", "layer"]]
        .drop_duplicates()
        .sort_values(["model_key", "layer"], kind="stable")
        .reset_index(drop=True)
    )
    labels = [
        f"{row.model_key}\nL{row.layer}" for row in groups.itertuples(index=False)
    ]
    positions = {
        (str(row.model_key), str(row.layer)): index
        for index, row in enumerate(groups.itertuples(index=False))
    }
    styles = {
        ("full", "LogisticRegression"): ("#4c78a8", "-", "o"),
        ("full", "RandomForestClassifier"): ("#f58518", "-", "o"),
        ("no_frequency", "LogisticRegression"): ("#4c78a8", "--", "s"),
        ("no_frequency", "RandomForestClassifier"): ("#f58518", "--", "s"),
        ("no_raw", "LogisticRegression"): ("#54a24b", ":", "^"),
        ("no_raw", "RandomForestClassifier"): ("#e45756", ":", "^"),
    }
    figure, axis = plt.subplots(figsize=(8.2, 3.8))
    for feature_set in FEATURE_SET_ORDER:
        for classifier in ("LogisticRegression", "RandomForestClassifier"):
            subset = summary.loc[
                (summary["feature_set"] == feature_set)
                & (summary["classifier"] == classifier)
            ].copy()
            if subset.empty:
                continue
            subset["x"] = [
                positions[(str(model), str(layer))]
                for model, layer in zip(subset["model_key"], subset["layer"])
            ]
            subset = subset.sort_values("x", kind="stable")
            color, line_style, marker = styles[(feature_set, classifier)]
            display = "Logistic" if classifier == "LogisticRegression" else "RF"
            axis.plot(
                subset["x"],
                subset["roc_auc_mean"],
                label=f"{display} / {feature_set}",
                color=color,
                linestyle=line_style,
                marker=marker,
                markersize=3.2,
                linewidth=1.1,
            )
    axis.axhline(0.5, color="0.65", linewidth=0.7)
    axis.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    axis.set_ylabel("Mean held-out ROC–AUC")
    axis.set_title("Bottom-versus-top ESS quintile classification")
    axis.grid(axis="y", color="0.9", linewidth=0.6)
    axis.legend(ncol=3, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, -0.48))
    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
        metadata={"Software": "local-geometry-reproduction"},
    )
    plt.close(figure)


def _plot_checkpoints(summary: pd.DataFrame, output_path: Path) -> None:
    if summary.empty:
        return
    plotted = summary.loc[summary["feature_set"] == "full"].copy()
    families = sorted(plotted["model_family"].astype(str).unique())
    if not families:
        return
    x_column = "training_tokens_billion"
    figure, axes = plt.subplots(
        1,
        len(families),
        figsize=(max(5.0, 4.4 * len(families)), 3.7),
        sharey=True,
        squeeze=False,
    )
    colors = plt.get_cmap("tab10")
    for axis, family in zip(axes[0], families):
        family_data = plotted.loc[plotted["model_family"].astype(str) == family]
        layers = sorted(family_data["layer"].unique(), key=str)
        for layer_index, layer in enumerate(layers):
            for estimator, line_style in (("Ridge", "--"), ("RandomForest", "-")):
                subset = family_data.loc[
                    (family_data["layer"] == layer)
                    & (family_data["estimator"] == estimator)
                ].sort_values(x_column, kind="stable")
                if subset.empty:
                    continue
                axis.plot(
                    subset[x_column],
                    subset["r2_mean"],
                    color=colors(layer_index % 10),
                    linestyle=line_style,
                    marker="o",
                    markersize=3,
                    linewidth=1.1,
                    label=f"L{layer} / {estimator}",
                )
        axis.axhline(0.0, color="0.65", linewidth=0.7)
        axis.set_title(family)
        axis.set_xlabel("Training tokens (billions)")
        axis.grid(axis="y", color="0.9", linewidth=0.6)
        axis.legend(fontsize=7, frameon=False)
    axes[0][0].set_ylabel("Mean held-out ESS $R^2$")
    figure.suptitle("Checkpoint ESS prediction (full features)", fontsize=11)
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
        metadata={"Software": "local-geometry-reproduction"},
    )
    plt.close(figure)


def _manifest(
    bundle: LoadedBundle,
    paths: BundlePaths,
    config: AnalysisConfig,
    *,
    checkpoint_ran: bool,
    extended: bool,
) -> dict[str, object]:
    input_files: dict[str, object] = {
        "features.parquet": {
            "sha256": _file_sha256(paths.features),
            "rows": len(bundle.features),
        },
        "main_targets.parquet": {
            "sha256": _file_sha256(paths.main_targets),
            "rows": len(bundle.main_targets),
        },
    }
    if checkpoint_ran:
        input_files["checkpoint_targets.parquet"] = {
            "sha256": _file_sha256(paths.checkpoint_targets),
            "rows": len(bundle.checkpoint_targets)
            if bundle.checkpoint_targets is not None
            else 0,
        }
    return {
        "analysis": "local_geometry_cpu_reproduction",
        "analysis_mode": "extended" if extended else "paper_core",
        "config": asdict(config),
        "preprocessing": {
            "imputation": "training-fold median",
            "ridge_scaling": "training-fold StandardScaler",
            "random_forest_scaling": "none",
        },
        "feature_sets": {
            name: list(columns) for name, columns in bundle.feature_sets.items()
        },
        "main_target_sources": bundle.main_target_sources,
        "checkpoint_target_source": bundle.checkpoint_target_source,
        "checkpoint_analysis_ran": checkpoint_ran,
        "input_files": input_files,
    }


def run_analysis(
    *,
    paths: BundlePaths,
    output_dir: Path,
    skip_checkpoints: bool = False,
    require_checkpoints: bool = False,
    extended: bool = False,
    config: AnalysisConfig = AnalysisConfig(),
) -> list[Path]:
    """Run the complete analysis and return paths written in deterministic order."""

    bundle = load_bundle(
        paths,
        skip_checkpoints=skip_checkpoints,
        require_checkpoints=require_checkpoints,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    features_out = output_dir / "feature_sets.csv"
    _write_csv(feature_manifest(bundle), features_out)
    written.append(features_out)

    regression_targets = tuple(MAIN_TARGETS) if extended else ("ESS",)
    main_feature_sets = FEATURE_SET_ORDER if extended else ("full", "no_frequency")
    checkpoint_feature_sets = FEATURE_SET_ORDER if extended else ("full",)

    main_scores, main_predictions = run_main_analyses(
        bundle,
        config,
        target_names=regression_targets,
        feature_set_names=main_feature_sets,
    )
    main_context = ("model_key", "layer")
    main_summary = summarize_scores(main_scores, main_context)
    main_scores = _sort_frame(
        main_scores,
        (*main_context, "target", "feature_set", "estimator", "fold"),
    )
    main_predictions = _sort_frame(
        main_predictions,
        (
            *main_context,
            "target",
            "feature_set",
            "estimator",
            "fold",
            "query_index",
        ),
    )
    main_summary = _sort_frame(
        main_summary,
        (*main_context, "target", "feature_set", "estimator"),
    )
    for filename, frame in (
        ("main_fold_scores.csv", main_scores),
        ("main_cv_summary.csv", main_summary),
        ("main_oof_predictions.csv", main_predictions),
    ):
        path = output_dir / filename
        _write_csv(frame, path)
        written.append(path)

    main_plot = output_dir / "main_cv_r2.png"
    _plot_main(main_summary, main_plot)
    written.append(main_plot)

    classification_scores, classification_predictions = run_main_ess_classification(
        bundle,
        config,
        feature_set_names=main_feature_sets,
    )
    classification_summary = summarize_classification_scores(
        classification_scores, main_context
    )
    classification_scores = _sort_frame(
        classification_scores,
        (*main_context, "feature_set", "classifier", "fold"),
    )
    classification_predictions = _sort_frame(
        classification_predictions,
        (
            *main_context,
            "feature_set",
            "classifier",
            "fold",
            "query_index",
        ),
    )
    classification_summary = _sort_frame(
        classification_summary,
        (*main_context, "feature_set", "classifier"),
    )
    for filename, frame in (
        ("ess_classification_fold_scores.csv", classification_scores),
        ("ess_classification_summary.csv", classification_summary),
        ("ess_classification_oof_predictions.csv", classification_predictions),
    ):
        path = output_dir / filename
        _write_csv(frame, path)
        written.append(path)
    classification_plot = output_dir / "ess_classification_auc.png"
    _plot_ess_classification(classification_summary, classification_plot)
    written.append(classification_plot)

    k_values = (
        pd.to_numeric(bundle.main_targets["k"], errors="raise").dropna().unique()
        if "k" in bundle.main_targets.columns
        else np.asarray([1000])
    )
    if len(k_values) != 1:
        raise ValueError(
            "main_targets.parquet must contain exactly one k value for the compact ESS table."
        )
    paper_summary = build_paper_ess_summary(
        main_summary,
        classification_summary,
        k_value=int(k_values[0]),
    )
    paper_summary = _sort_frame(
        paper_summary, ("model_key", "layer", "feature_set")
    )
    paper_summary_path = output_dir / "paper_ess_scores.csv"
    _write_csv(paper_summary, paper_summary_path)
    written.append(paper_summary_path)

    checkpoint_ran = bundle.checkpoint_targets is not None
    if checkpoint_ran:
        checkpoint_scores, checkpoint_predictions = run_checkpoint_analyses(
            bundle,
            config,
            feature_set_names=checkpoint_feature_sets,
        )
        checkpoint_context = _checkpoint_context_columns(bundle.checkpoint_targets)
        checkpoint_summary = summarize_scores(checkpoint_scores, checkpoint_context)
        checkpoint_scores = _sort_frame(
            checkpoint_scores,
            (*checkpoint_context, "feature_set", "estimator", "fold"),
        )
        checkpoint_predictions = _sort_frame(
            checkpoint_predictions,
            (
                *checkpoint_context,
                "feature_set",
                "estimator",
                "fold",
                "query_index",
            ),
        )
        checkpoint_summary = _sort_frame(
            checkpoint_summary,
            (*checkpoint_context, "feature_set", "estimator"),
        )
        for filename, frame in (
            ("checkpoint_fold_scores.csv", checkpoint_scores),
            ("checkpoint_cv_summary.csv", checkpoint_summary),
            ("checkpoint_oof_predictions.csv", checkpoint_predictions),
        ):
            path = output_dir / filename
            _write_csv(frame, path)
            written.append(path)
        checkpoint_plot = output_dir / "checkpoint_ess_r2.png"
        _plot_checkpoints(checkpoint_summary, checkpoint_plot)
        written.append(checkpoint_plot)

    manifest_path = output_dir / "analysis_manifest.json"
    manifest_path.write_text(
        json.dumps(
            _manifest(
                bundle,
                paths,
                config,
                checkpoint_ran=checkpoint_ran,
                extended=extended,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(manifest_path)
    return written


def main() -> None:
    args = parse_args()
    paths = resolve_bundle_paths(args)
    written = run_analysis(
        paths=paths,
        output_dir=args.output_dir,
        skip_checkpoints=bool(args.skip_checkpoints),
        require_checkpoints=bool(args.require_checkpoints),
        extended=bool(args.extended),
    )
    print(f"Wrote {len(written)} deterministic artifact(s) to {args.output_dir}")
    for path in written:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()
