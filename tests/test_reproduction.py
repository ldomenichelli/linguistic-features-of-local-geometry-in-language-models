from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from reproduce_analysis import (  # noqa: E402
    FREQUENCY_FEATURES,
    RAW_SURFACE_FEATURES,
    AnalysisConfig,
    BundlePaths,
    _join_group_to_features,
    build_feature_sets,
    cross_validate_ess_classification,
    cross_validate_regression,
    load_bundle,
    run_analysis,
    validate_checkpoint_targets,
    validate_features,
    validate_main_targets,
)


def text_digest(index: int) -> str:
    return hashlib.sha256(f"synthetic-{index}".encode("utf-8")).hexdigest()


def synthetic_features(n_rows: int = 30) -> pd.DataFrame:
    index = np.arange(n_rows)
    data: dict[str, object] = {
        "query_index": index,
        "text_sha256": [text_digest(int(value)) for value in index],
        "linguistic_a": np.sin(index / 3.0),
        "linguistic_b": np.cos(index / 5.0),
        "min_frequency_class": (index % 4).astype(float),
        "median_frequency_class": (index % 7).astype(float),
        "max_frequency_class": (index % 11).astype(float),
        "n_sentences": (index % 3 + 1).astype(float),
        "n_tokens": (index + 6).astype(float),
        "tokens_per_sent": (index + 6) / (index % 3 + 1),
        "char_per_tok": 4.0 + index / 100.0,
    }
    frame = pd.DataFrame(data)
    frame.loc[1, "linguistic_a"] = np.nan
    return frame


def synthetic_main_targets(query_indices: np.ndarray) -> pd.DataFrame:
    index = np.asarray(query_indices, dtype=float)
    return pd.DataFrame(
        {
            "model_key": "toy",
            "layer": 2,
            "query_index": query_indices,
            "model_revision": "revision-a",
            "reference_size": 100,
            "k": 10,
            "pointwise_mle": 2.0 + 0.1 * index + np.sin(index),
            "pointwise_ess": 8.0 + 0.3 * index + np.cos(index / 2.0),
            "pointwise_fci_id": 4.0 + 0.2 * index + np.sin(index / 4.0),
        }
    )


class SchemaAndPrivacyTests(unittest.TestCase):
    def test_exact_feature_families_and_identity_exclusion(self) -> None:
        features = synthetic_features()
        predictors = validate_features(features)
        feature_sets = build_feature_sets(predictors, warn_missing=False)

        self.assertNotIn("query_index", feature_sets["full"])
        self.assertNotIn("text_sha256", feature_sets["full"])
        self.assertEqual(
            set(feature_sets["full"]) - set(feature_sets["no_frequency"]),
            set(FREQUENCY_FEATURES),
        )
        self.assertEqual(
            set(feature_sets["full"]) - set(feature_sets["no_raw"]),
            set(RAW_SURFACE_FEATURES),
        )

    def test_raw_text_is_rejected(self) -> None:
        features = synthetic_features()
        features["text"] = [f"raw sentence {index}" for index in range(len(features))]
        with self.assertRaisesRegex(ValueError, "raw-text"):
            validate_features(features)

    def test_extra_identity_and_target_leakage_are_rejected(self) -> None:
        for column in ("row_id", "pointwise_ess"):
            with self.subTest(column=column):
                features = synthetic_features()
                features[column] = np.arange(len(features), dtype=float)
                with self.assertRaises(ValueError):
                    validate_features(features)

    def test_main_schema_prefers_canonical_mle_and_accepts_legacy_alias(self) -> None:
        targets = synthetic_main_targets(np.arange(30))
        canonical, sources = validate_main_targets(targets)
        self.assertIn("pointwise_mle", canonical)
        self.assertEqual(sources["MLE"], "pointwise_mle")

        legacy = targets.rename(columns={"pointwise_mle": "pointwise_id"})
        normalized, sources = validate_main_targets(legacy)
        self.assertIn("pointwise_mle", normalized)
        self.assertEqual(sources["MLE"], "pointwise_id")

    def test_checkpoint_schema_uses_release_metadata(self) -> None:
        index = np.arange(30)
        checkpoint = pd.DataFrame(
            {
                "model_family": "toy-family",
                "checkpoint": "step-a",
                "checkpoint_order": 0,
                "training_step": 100,
                "training_tokens_billion": 1.5,
                "model_revision": "revision-a",
                "layer": 2,
                "query_index": index,
                "ESS": 2.0 + index / 10.0,
            }
        )
        normalized, source = validate_checkpoint_targets(checkpoint)
        self.assertEqual(source, "ESS")
        self.assertIn("pointwise_ess", normalized)

    def test_target_extras_are_dropped_not_treated_as_missing_features(self) -> None:
        features = synthetic_features(24)
        targets = synthetic_main_targets(np.arange(30))
        predictors = validate_features(features)
        joined = _join_group_to_features(targets, features, predictors)
        self.assertEqual(len(joined), 24)
        self.assertEqual(set(joined["query_index"]), set(features["query_index"]))


class DeterminismTests(unittest.TestCase):
    def setUp(self) -> None:
        self.features = synthetic_features(30)
        self.predictors = build_feature_sets(
            validate_features(self.features), warn_missing=False
        )["full"]
        self.joined = _join_group_to_features(
            synthetic_main_targets(np.arange(30)),
            self.features,
            self.predictors,
        )
        self.config = AnalysisConfig(rf_trees=7, rf_n_jobs=1)
        self.context = {"model_key": "toy", "layer": 2}

    def test_regression_is_deterministic(self) -> None:
        first_scores, first_predictions = cross_validate_regression(
            self.joined,
            predictors=self.predictors,
            target_column="pointwise_ess",
            target_name="ESS",
            feature_set="full",
            context=self.context,
            config=self.config,
        )
        second_scores, second_predictions = cross_validate_regression(
            self.joined,
            predictors=self.predictors,
            target_column="pointwise_ess",
            target_name="ESS",
            feature_set="full",
            context=self.context,
            config=self.config,
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(first_scores), pd.DataFrame(second_scores), check_exact=True
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(first_predictions),
            pd.DataFrame(second_predictions),
            check_exact=True,
        )

    def test_classification_is_deterministic(self) -> None:
        first_scores, first_predictions = cross_validate_ess_classification(
            self.joined,
            predictors=self.predictors,
            feature_set="full",
            context=self.context,
            config=self.config,
        )
        second_scores, second_predictions = cross_validate_ess_classification(
            self.joined,
            predictors=self.predictors,
            feature_set="full",
            context=self.context,
            config=self.config,
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(first_scores), pd.DataFrame(second_scores), check_exact=True
        )
        pd.testing.assert_frame_equal(
            pd.DataFrame(first_predictions),
            pd.DataFrame(second_predictions),
            check_exact=True,
        )

    def test_model_helper_rejects_identity_predictor(self) -> None:
        with self.assertRaisesRegex(ValueError, "prohibited"):
            cross_validate_regression(
                self.joined,
                predictors=("query_index", *self.predictors),
                target_column="pointwise_ess",
                target_name="ESS",
                feature_set="bad",
                context=self.context,
                config=self.config,
            )


class IntegrationTests(unittest.TestCase):
    def test_analysis_writes_compact_and_auditable_outputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="geometry_test_") as raw_temp:
            root = Path(raw_temp)
            data_dir = root / "derived"
            output_dir = root / "generated"
            data_dir.mkdir()

            features = synthetic_features(30)
            targets = synthetic_main_targets(np.arange(32))
            features.to_parquet(data_dir / "features.parquet", index=False)
            targets.to_parquet(data_dir / "main_targets.parquet", index=False)
            paths = BundlePaths(
                features=data_dir / "features.parquet",
                main_targets=data_dir / "main_targets.parquet",
                checkpoint_targets=data_dir / "checkpoint_targets.parquet",
            )
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                written = run_analysis(
                    paths=paths,
                    output_dir=output_dir,
                    skip_checkpoints=True,
                    extended=True,
                    config=AnalysisConfig(rf_trees=5, rf_n_jobs=1),
                )

            names = {path.name for path in written}
            self.assertIn("paper_ess_scores.csv", names)
            self.assertIn("main_oof_predictions.csv", names)
            self.assertIn("ess_classification_oof_predictions.csv", names)
            self.assertNotIn("checkpoint_fold_scores.csv", names)

            compact = pd.read_csv(output_dir / "paper_ess_scores.csv")
            self.assertEqual(set(compact["feature_set"]), {"full", "no_frequency", "no_raw"})
            self.assertEqual(set(compact["n_regression"]), {30})
            manifest = json.loads(
                (output_dir / "analysis_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["config"]["seed"], 42)
            self.assertEqual(manifest["config"]["rf_trees"], 5)
            self.assertFalse(manifest["checkpoint_analysis_ran"])


class PaperArtifactTests(unittest.TestCase):
    def test_every_numbered_figure_and_table_is_present(self) -> None:
        for number in range(1, 7):
            for suffix in ("png", "pdf"):
                path = REPO_ROOT / "paper" / "figures" / f"figure_{number:02d}.{suffix}"
                self.assertTrue(path.is_file(), path)
                self.assertGreater(path.stat().st_size, 0)
        for number in range(1, 18):
            path = REPO_ROOT / "paper" / "tables" / f"table_{number:02d}.csv"
            self.assertTrue(path.is_file(), path)
            self.assertGreater(len(pd.read_csv(path)), 0)

    def test_feature_inventory_matches_the_public_matrix(self) -> None:
        features = pd.read_parquet(REPO_ROOT / "data" / "derived" / "features.parquet")
        inventory = pd.read_csv(REPO_ROOT / "paper" / "tables" / "table_17.csv")
        expected = set(features.columns) - {"query_index", "text_sha256"}
        self.assertEqual(set(inventory["feature"]), expected)

    def test_representative_examples_match_public_numeric_rows(self) -> None:
        aliases = {
            "upos_PROPN": "upos_dist_PROPN",
            "upos_NOUN": "upos_dist_NOUN",
            "dep_nsubj": "dep_dist_nsubj",
            "verbal_root": "verbal_root_perc",
            "upos_PRON": "upos_dist_PRON",
        }
        features = pd.read_parquet(
            REPO_ROOT / "data" / "derived" / "features.parquet"
        ).set_index("query_index")
        targets = pd.read_parquet(
            REPO_ROOT / "data" / "derived" / "main_targets.parquet"
        )
        targets = targets.loc[
            targets["model_key"].eq("pythia") & targets["layer"].eq(16)
        ].set_index("query_index")
        examples = pd.read_csv(REPO_ROOT / "paper" / "tables" / "table_13.csv")
        for row in examples.itertuples(index=False):
            column = aliases.get(row.feature, row.feature)
            shown_feature = float(str(row.feature_value).removesuffix("%"))
            self.assertAlmostEqual(
                float(features.at[row.query_index, column]), shown_feature, delta=0.051
            )
            self.assertAlmostEqual(
                float(targets.at[row.query_index, "pointwise_ess"]),
                float(row.ess_id),
                delta=0.006,
            )


if __name__ == "__main__":
    unittest.main()
