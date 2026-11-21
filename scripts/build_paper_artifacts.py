#!/usr/bin/env python3
"""Rebuild the paper figures and tables from the compact repository data.

The sentence-level Parquet files are used whenever they contain the required
measurements.  Experiments that depended on unredistributed text or large
representation arrays are rerendered from their archived numeric summaries.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from build_experiment_artifacts import build_experiment_artifacts
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator


MODEL_ORDER = ("Pythia-6.9B", "Qwen2.5-7B", "Apertus-8B")
MODEL_NAMES = {
    "pythia": "Pythia-6.9B",
    "qwen": "Qwen2.5-7B",
    "apertus": "Apertus-8B",
}
MODEL_LAYERS = {
    "Pythia-6.9B": (32, (2, 16, 31)),
    "Qwen2.5-7B": (28, (2, 14, 27)),
    "Apertus-8B": (32, (2, 16, 31)),
}
ESTIMATOR_COLUMNS = {
    "MLE": "pointwise_mle",
    "ESS": "pointwise_ess",
    "FCI": "pointwise_fci_id",
}
COLORS = {
    "MLE": "#E76F51",
    "ESS": "#0072B2",
    "FCI": "#009E73",
    2: "#0072B2",
    16: "#D55E00",
    31: "#009E73",
}

TABLE_CAPTIONS = {
    1: "Spearman correlations between excerpt perplexity and ESS pointwise ID. All nine correlations have p < 0.05.",
    2: "ESS pointwise-ID regression and feature ablations. Values are mean five-fold cross-validated R² for random forest and Ridge; no-frequency removes three frequency summaries and no-raw removes four surface descriptors.",
    3: "Five largest ESS random-forest permutation importances. Importance is the mean decrease in held-out R² over eight shuffles and five folds.",
    4: "Depth-specific cross-fitted ALE effects for recurring ESS predictors. Directions count models with a stable sign; contrasts are median 10th-to-90th-percentile effects in target-SD units.",
    5: "ESS random-forest regression across seven Apertus checkpoints. Scores are mean five-fold R²; importance is the mean held-out R² decrease over eight shuffles and five folds.",
    6: "MLE and FCI pointwise-ID regression and feature ablations. Values are mean five-fold cross-validated R² for random forest and Ridge.",
    7: "Five largest held-out random-forest permutation importances for MLE and FCI, averaged over eight shuffles and five folds.",
    8: "Neighbourhood- and adjacent-layer sensitivity for Pythia and Qwen. Values are mean five-fold random-forest R² using the same 46 predictors; the separate k = 1000 ESS results appear in Table 2.",
    9: "Stability of held-out ESS importance rankings. Recurrence counts top-five appearances across five alternative k values; overlap columns report median top-five intersections.",
    10: "Pythia pointwise-ID distributions in the main and extra Pile evaluation splits at k = 1000 and reference size 15,000. The final column is the absolute pooled-SD standardized mean difference.",
    11: "Classification of the lowest and highest ESS quintiles. Values are mean five-fold ROC-AUC and fold SD for random forest and logistic regression.",
    12: "Five largest random-forest permutation importances for low/high ESS classification. Importance is the mean held-out ROC-AUC decrease over eight shuffles and five folds.",
    13: "Representative excerpts for recurring ALE directions. Examples illustrate associations and do not isolate a feature from correlated properties.",
    14: "Classification performance of Profiling-UD and matched 46-term lexical baselines. Values are mean five-fold ROC-AUC for distinguishing the bottom and top 20% of each pointwise-ID distribution.",
    15: "Regression performance of Profiling-UD and matched 46-term lexical baselines. Values are mean five-fold cross-validated R².",
    16: "ESS pointwise-ID regression across five Pythia checkpoints. Scores are mean five-fold random-forest R²; importances are mean held-out R² decreases over eight shuffles and five folds.",
    17: "The 43 Profiling-UD descriptors and three frequency summaries used by the downstream analyses.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived-dir", type=Path, default=Path("data/derived"))
    parser.add_argument("--paper-data-dir", type=Path, default=Path("data/paper"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/paper"))
    return parser.parse_args()


def paper_style() -> None:
    plt.rcParams.update(
        {
            "axes.edgecolor": "#374151",
            "axes.labelcolor": "#111827",
            "axes.linewidth": 0.8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "grid.color": "#E5E7EB",
            "grid.linewidth": 0.7,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "xtick.color": "#111827",
            "ytick.color": "#111827",
        }
    )


def save_figure(figure: plt.Figure, output_dir: Path, number: int) -> None:
    for suffix in ("png", "pdf"):
        figure.savefig(
            output_dir / f"figure_{number:02d}.{suffix}",
            dpi=300 if suffix == "png" else None,
            bbox_inches="tight",
            facecolor="white",
            metadata={"Creator": "Linguistic Features of Local Geometry"},
        )
    plt.close(figure)


def main_summary(main_targets: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model_key, model_name in MODEL_NAMES.items():
        total_layers, selected_layers = MODEL_LAYERS[model_name]
        for depth_order, layer in enumerate(selected_layers):
            group = main_targets.loc[
                main_targets["model_key"].eq(model_key)
                & main_targets["layer"].eq(layer)
            ]
            if group.empty:
                raise ValueError(f"Missing main targets for {model_key}, layer {layer}")
            for estimator, column in ESTIMATOR_COLUMNS.items():
                values = pd.to_numeric(group[column], errors="coerce").dropna()
                rows.append(
                    {
                        "model": model_name,
                        "model_order": MODEL_ORDER.index(model_name),
                        "layer": layer,
                        "total_layers": total_layers,
                        "relative_depth": layer / total_layers,
                        "depth_order": depth_order,
                        "estimator": estimator,
                        "n": len(values),
                        "mean": values.mean(),
                        "sd": values.std(ddof=1),
                    }
                )
    return pd.DataFrame(rows)


def build_figure_1(summary: pd.DataFrame, output_dir: Path) -> None:
    data = summary.loc[summary["estimator"].eq("ESS")]
    maximum = float((data["mean"] + data["sd"]).max())
    figure, axes = plt.subplots(1, 3, figsize=(7.15, 2.75), sharey=True)
    for axis, model in zip(axes, MODEL_ORDER, strict=True):
        panel = data.loc[data["model"].eq(model)].sort_values("depth_order")
        total_layers, selected_layers = MODEL_LAYERS[model]
        axis.errorbar(
            panel["relative_depth"],
            panel["mean"],
            yerr=panel["sd"],
            color=COLORS["ESS"],
            marker="o",
            markersize=4.8,
            markeredgecolor="white",
            markeredgewidth=0.55,
            linewidth=1.7,
            elinewidth=0.9,
            capsize=2.2,
            capthick=0.8,
            zorder=3,
        )
        axis.text(0.96, 0.95, model, transform=axis.transAxes, ha="right", va="top")
        axis.set_xticks(
            [layer / total_layers for layer in selected_layers],
            labels=[str(layer) for layer in selected_layers],
        )
        axis.set_xlim(0.0, 1.03)
        axis.set_ylim(0.0, maximum * 1.08)
        axis.grid(True, axis="y")
        axis.yaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=4))
    figure.supxlabel("Layer (matched relative depth)", x=0.535, y=0.055)
    figure.supylabel("Mean ESS pointwise ID", x=0.012, y=0.50)
    figure.subplots_adjust(left=0.085, right=0.995, bottom=0.22, top=0.94, wspace=0.14)
    save_figure(figure, output_dir, 1)


def build_figure_2(paper_data_dir: Path, output_dir: Path) -> None:
    data = pd.read_csv(paper_data_dir / "figure_02_reference_size_summary.csv")
    figure, axis = plt.subplots(figsize=(5.4, 3.35))
    palette = {50: "#0072B2", 100: "#009E73", 500: "#E69F00", 1000: "#D55E00"}
    for k, group in data.groupby("k", sort=True):
        group = group.sort_values("reference_size")
        axis.plot(
            group["reference_size"],
            group["ess_median"],
            marker="o",
            markersize=4,
            linewidth=1.6,
            label=f"k = {int(k)}",
            color=palette[int(k)],
        )
    axis.set_xlabel("Reference-set size")
    axis.set_ylabel("Median ESS pointwise ID")
    axis.grid(True)
    axis.legend(ncol=2)
    figure.tight_layout()
    save_figure(figure, output_dir, 2)


def build_figure_3(paper_data_dir: Path, output_dir: Path) -> None:
    data = pd.read_csv(paper_data_dir / "figure_03_reference_resampling_pairs.csv")
    data = data.loc[
        data["metric"].eq("ess")
        & data["k"].eq(1000)
        & data["layer_name"].astype(str).eq("layer_16")
    ].copy()
    sizes = sorted(data["reference_size"].unique())
    positions = {value: index for index, value in enumerate(sizes)}
    rng = np.random.default_rng(42)
    figure, axis = plt.subplots(figsize=(5.2, 3.25))
    for size in sizes:
        values = data.loc[data["reference_size"].eq(size), "spearman_rho"].to_numpy()
        x = positions[size] + rng.uniform(-0.11, 0.11, size=len(values))
        axis.scatter(x, values, s=18, color="#4C72B0", alpha=0.40, linewidths=0)
    means = data.groupby("reference_size")["spearman_rho"].mean().reindex(sizes)
    axis.plot(range(len(sizes)), means, color="#1F4E79", marker="o", linewidth=1.7)
    axis.axhline(0.90, color="#666666", linestyle="--", linewidth=0.9)
    axis.set_xticks(range(len(sizes)), labels=[str(int(value)) for value in sizes])
    axis.set_ylim(0.975, 1.0)
    axis.set_xlabel("Reference-set size")
    axis.set_ylabel("Pairwise Spearman $\\rho$")
    axis.grid(True)
    figure.tight_layout()
    save_figure(figure, output_dir, 3)


def build_figure_4(paper_data_dir: Path, output_dir: Path) -> None:
    data = pd.read_csv(paper_data_dir / "figure_04_gaussian_calibration_summary.csv")
    figure, axis = plt.subplots(figsize=(6.4, 4.0))
    markers = {"MLE": "s", "ESS": "o", "FCI": "D"}
    for estimator, column in (
        ("MLE", "mle_median"),
        ("ESS", "ess_median"),
        ("FCI", "fci_median"),
    ):
        axis.plot(
            data["k"],
            data[column],
            color=COLORS[estimator],
            marker=markers[estimator],
            markersize=6,
            linewidth=2.1,
            label=estimator,
        )
    true_dimension = int(data["dim"].iloc[0])
    axis.axhline(
        true_dimension,
        color="#CC3311",
        linestyle=(0, (5, 3)),
        linewidth=1.6,
        label=f"True ID = {true_dimension}",
    )
    axis.set_xscale("log")
    axis.set_xticks(data["k"], labels=[str(int(value)) for value in data["k"]], rotation=25)
    axis.set_xlabel("Neighbourhood size k")
    axis.set_ylabel("Median estimated ID")
    axis.grid(True)
    axis.legend()
    figure.tight_layout()
    save_figure(figure, output_dir, 4)


def build_figure_5(summary: pd.DataFrame, output_dir: Path) -> None:
    figure, axes = plt.subplots(1, 3, figsize=(9.1, 3.25), sharey=True)
    markers = {"MLE": "s", "ESS": "o", "FCI": "D"}
    for axis, model in zip(axes, MODEL_ORDER, strict=True):
        panel = summary.loc[summary["model"].eq(model)]
        layers = MODEL_LAYERS[model][1]
        for estimator in ("ESS", "FCI", "MLE"):
            values = panel.loc[panel["estimator"].eq(estimator)].sort_values("depth_order")
            axis.errorbar(
                range(3),
                values["mean"],
                yerr=values["sd"],
                marker=markers[estimator],
                color=COLORS[estimator],
                linewidth=1.6,
                elinewidth=0.8,
                capsize=2,
                markersize=4.5,
                label=estimator,
            )
        axis.set_xticks(range(3), labels=[str(layer) for layer in layers])
        axis.set_title(model)
        axis.set_xlabel("Layer")
        axis.grid(True, axis="y")
    axes[0].set_ylabel("Mean pointwise ID")
    axes[-1].legend(loc="upper right")
    figure.tight_layout()
    save_figure(figure, output_dir, 5)


def build_figure_6(checkpoints: pd.DataFrame, output_dir: Path) -> None:
    summary = (
        checkpoints.groupby(
            ["model_family", "checkpoint", "checkpoint_order", "training_tokens_billion", "layer"],
            as_index=False,
        )["pointwise_ess"]
        .agg(["mean", "std"])
        .reset_index()
    )
    figure, axes = plt.subplots(1, 2, figsize=(8.1, 3.35), sharey=True)
    labels = {
        "pythia": ("Pythia-6.9B", ["1.1B", "16.8B", "44B", "115B", "300B"]),
        "apertus": ("Apertus-8B", ["210B", "420B", "840B", "1.68T", "3.57T", "7.23T", "15T"]),
    }
    for axis, family in zip(axes, ("pythia", "apertus"), strict=True):
        panel = summary.loc[summary["model_family"].eq(family)].copy()
        title, tick_labels = labels[family]
        for layer in (2, 16, 31):
            values = panel.loc[panel["layer"].eq(layer)].sort_values("checkpoint_order")
            axis.errorbar(
                values["checkpoint_order"],
                values["mean"],
                yerr=values["std"],
                color=COLORS[layer],
                marker="o",
                linewidth=1.5,
                elinewidth=0.7,
                capsize=1.8,
                markersize=3.8,
                label=f"Layer {layer}",
            )
        axis.set_xticks(range(len(tick_labels)), labels=tick_labels, rotation=25)
        axis.set_title(title)
        axis.set_xlabel("Cumulative training tokens")
        axis.grid(True, axis="y")
    axes[0].set_ylabel("Mean pointwise ID")
    axes[-1].legend(loc="upper right")
    figure.tight_layout()
    save_figure(figure, output_dir, 6)


def clean_feature_name(value: object) -> str:
    name = str(value)
    if name.startswith("upos_dist_"):
        return "upos_" + name.removeprefix("upos_dist_")
    if name.startswith("dep_dist_"):
        return "dep_" + name.removeprefix("dep_dist_")
    if name == "verbal_root_perc":
        return "verbal_root"
    return name


def model_rank() -> dict[str, int]:
    return {model: index for index, model in enumerate(MODEL_ORDER)}


def add_wide_ranks(
    row: dict[str, object],
    source: pd.Series,
    estimator: str,
    *,
    score_column: str,
) -> dict[str, object]:
    row["r2"] = float(source[score_column])
    for rank in range(1, 6):
        row[f"rank_{rank}_feature"] = clean_feature_name(
            source[f"{estimator} rank {rank} feature"]
        )
        row[f"rank_{rank}_importance"] = float(
            source[f"{estimator} rank {rank} permutation importance"]
        )
    return row


def top_five_from_long(data: pd.DataFrame, target: str) -> pd.DataFrame:
    subset = data.loc[
        data["target"].eq(target) & data["model"].isin(MODEL_ORDER[:2])
    ].copy()
    subset = subset.loc[subset["selected_top5"].astype(bool)]
    records: list[dict[str, object]] = []
    for (model, layer), group in subset.groupby(["model", "layer"], sort=False):
        group = group.sort_values("permutation_rank")
        row: dict[str, object] = {"model": model, "layer": int(layer)}
        for _, item in group.iterrows():
            rank = int(item["permutation_rank"])
            row[f"rank_{rank}_feature"] = clean_feature_name(item["feature"])
            row[f"rank_{rank}_importance"] = float(item["permutation_importance_mean"])
        records.append(row)
    return pd.DataFrame(records)


def build_tables(paper_data_dir: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    correlations = pd.read_csv(paper_data_dir / "perplexity_correlations.csv")
    table_1 = correlations.loc[
        correlations["metric"].eq("ESS"),
        ["model", "relative_depth", "layer", "spearman_rho", "spearman_p", "n"],
    ].copy()
    table_1["depth"] = table_1["relative_depth"].replace(
        {"middle": "Intermediate", "second-to-last": "Late", "early": "Early"}
    )
    table_1["model_order"] = table_1["model"].map(model_rank())
    table_1 = table_1.sort_values(["model_order", "layer"])[
        ["model", "depth", "layer", "spearman_rho", "spearman_p", "n"]
    ]
    written.append(write_csv(table_1, output_dir / "table_01.csv"))

    for number in (2, 4, 6, 9, 10, 11, 12, 13, 17):
        source = paper_data_dir / "published_tables" / f"table_{number:02d}.csv"
        destination = output_dir / source.name
        shutil.copyfile(source, destination)
        written.append(destination)

    main_importance = pd.read_csv(paper_data_dir / "main_rf_permutation_ale.csv")
    apertus = pd.read_csv(paper_data_dir / "apertus_checkpoint_permutation.csv")
    apertus_final = apertus.loc[apertus["Checkpoint"].eq("15T")]

    table_3 = top_five_from_long(main_importance, "ESS")
    aperture_rows: list[dict[str, object]] = []
    for _, source in apertus_final.sort_values("Layer").iterrows():
        aperture_rows.append(
            add_wide_ranks(
                {"model": "Apertus-8B", "layer": int(source["Layer"])},
                source,
                "ESS",
                score_column="ESS R2",
            )
        )
    table_3 = pd.concat([table_3, pd.DataFrame(aperture_rows)], ignore_index=True)
    table_3 = table_3.drop(columns="r2")
    table_3["model_order"] = table_3["model"].map(model_rank())
    table_3 = table_3.sort_values(["model_order", "layer"]).drop(columns="model_order")
    written.append(write_csv(table_3, output_dir / "table_03.csv"))

    table_5_rows: list[dict[str, object]] = []
    for _, source in apertus.iterrows():
        table_5_rows.append(
            add_wide_ranks(
                {"checkpoint": source["Checkpoint"], "layer": int(source["Layer"])},
                source,
                "ESS",
                score_column="ESS R2",
            )
        )
    table_5 = pd.DataFrame(table_5_rows)
    written.append(write_csv(table_5, output_dir / "table_05.csv"))

    table_7_parts: list[pd.DataFrame] = []
    for source_target, output_target in (("pyFCI", "FCI"), ("MLE", "MLE")):
        part = top_five_from_long(main_importance, source_target)
        part.insert(0, "estimator", output_target)
        table_7_parts.append(part)
        aperture_rows = []
        checkpoint_prefix = "pyFCI" if source_target == "pyFCI" else "MLE"
        score_column = f"{checkpoint_prefix} R2"
        for _, source in apertus_final.sort_values("Layer").iterrows():
            aperture_rows.append(
                add_wide_ranks(
                    {
                        "estimator": output_target,
                        "model": "Apertus-8B",
                        "layer": int(source["Layer"]),
                    },
                    source,
                    checkpoint_prefix,
                    score_column=score_column,
                )
            )
        table_7_parts.append(pd.DataFrame(aperture_rows))
    table_7 = pd.concat(table_7_parts, ignore_index=True)
    table_7 = table_7.drop(columns="r2")
    table_7["estimator_order"] = table_7["estimator"].map({"FCI": 0, "MLE": 1})
    table_7["model_order"] = table_7["model"].map(model_rank())
    table_7 = table_7.sort_values(
        ["estimator_order", "model_order", "layer"]
    ).drop(columns=["estimator_order", "model_order"])
    written.append(write_csv(table_7, output_dir / "table_07.csv"))

    sensitivity = pd.read_csv(paper_data_dir / "neighbourhood_layer_sensitivity.csv")
    sensitivity["appendix_model"] = sensitivity["appendix_model"].replace(
        {"Pythia-6.9B-deduped": "Pythia-6.9B"}
    )
    selected_layers = {
        "Pythia-6.9B": {1, 2, 16, 17, 31, 32},
        "Qwen2.5-7B": {1, 2, 14, 15, 27, 28},
    }
    selected_k = [10, 100, 500, 2000, 3000]
    sensitivity = sensitivity.loc[
        sensitivity["task"].eq("regression")
        & sensitivity["k"].isin(selected_k)
        & sensitivity.apply(
            lambda row: int(row["layer"])
            in selected_layers.get(str(row["appendix_model"]), set()),
            axis=1,
        )
    ].copy()
    sensitivity["target"] = sensitivity["target_family"].replace({"pyFCI": "FCI"})
    table_8 = sensitivity.pivot_table(
        index=["appendix_model", "target", "layer"],
        columns="k",
        values="metric_r2_mean",
        aggfunc="first",
    ).reset_index()
    table_8 = table_8.rename(columns={"appendix_model": "model", **{k: f"k_{k}" for k in selected_k}})
    table_8["model_order"] = table_8["model"].map(model_rank())
    table_8["target_order"] = table_8["target"].map({"ESS": 0, "FCI": 1, "MLE": 2})
    table_8 = table_8.sort_values(["model_order", "target_order", "layer"]).drop(
        columns=["model_order", "target_order"]
    )
    written.append(write_csv(table_8, output_dir / "table_08.csv"))

    classification = pd.read_csv(paper_data_dir / "tfidf_classification.csv")
    table_14 = classification[
        [
            "architecture",
            "target_label",
            "layer",
            "profiling_ud_rf_roc_auc",
            "frequent_logistic_roc_auc",
            "frequent_rf_roc_auc",
            "band_logistic_roc_auc",
            "band_rf_roc_auc",
        ]
    ].rename(columns={"architecture": "model", "target_label": "target"})
    table_14["target"] = table_14["target"].replace({"pyFCI": "FCI"})
    table_14["model_order"] = table_14["model"].map(model_rank())
    table_14["target_order"] = table_14["target"].map({"ESS": 0, "FCI": 1, "MLE": 2})
    table_14 = table_14.sort_values(["model_order", "target_order", "layer"]).drop(
        columns=["model_order", "target_order"]
    )
    written.append(write_csv(table_14, output_dir / "table_14.csv"))

    regression = pd.read_csv(paper_data_dir / "tfidf_regression.csv")
    table_15 = regression.rename(columns={"architecture": "model", "target_label": "target"})
    table_15["target"] = table_15["target"].replace({"pyFCI": "FCI"})
    table_15["model_order"] = table_15["model"].map(model_rank())
    table_15["target_order"] = table_15["target"].map({"ESS": 0, "FCI": 1, "MLE": 2})
    table_15 = table_15.sort_values(["model_order", "target_order", "layer"]).drop(
        columns=["model_order", "target_order"]
    )
    written.append(write_csv(table_15, output_dir / "table_15.csv"))

    pythia = pd.read_csv(paper_data_dir / "pythia_checkpoint_permutation.csv")
    pythia = pythia.loc[~pythia["Checkpoint"].eq("step 0")]
    table_16_rows: list[dict[str, object]] = []
    for _, source in pythia.iterrows():
        table_16_rows.append(
            add_wide_ranks(
                {"checkpoint": source["Checkpoint"], "layer": int(source["Layer"])},
                source,
                "ESS",
                score_column="ESS R2",
            )
        )
    written.append(write_csv(pd.DataFrame(table_16_rows), output_dir / "table_16.csv"))

    expected = {f"table_{number:02d}.csv" for number in range(1, 18)}
    observed = {path.name for path in output_dir.glob("table_*.csv")}
    if observed != expected:
        raise ValueError(f"Table set mismatch: expected {sorted(expected)}, found {sorted(observed)}")
    return written


def write_csv(dataframe: pd.DataFrame, path: Path) -> Path:
    dataframe.to_csv(path, index=False, float_format="%.10g", lineterminator="\n")
    return path


def markdown_value(value: object) -> str:
    if pd.isna(value):
        return "—"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.6g}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def ranked_feature_text(row: pd.Series) -> str:
    values = []
    for rank in range(1, 6):
        feature = row[f"rank_{rank}_feature"]
        importance = float(row[f"rank_{rank}_importance"])
        values.append(f"{feature} ({importance:.4f})")
    return "; ".join(values)


def markdown_table(number: int, dataframe: pd.DataFrame) -> pd.DataFrame:
    """Use a compact, paper-like view while leaving the CSV fully structured."""

    if number in {3, 5, 7, 16}:
        identity_columns = {
            3: ["model", "layer"],
            5: ["checkpoint", "layer", "r2"],
            7: ["estimator", "model", "layer"],
            16: ["checkpoint", "layer", "r2"],
        }[number]
        compact = dataframe.loc[:, identity_columns].copy()
        compact["five largest held-out importances"] = dataframe.apply(
            ranked_feature_text, axis=1
        )
        return compact
    if number == 12:
        rows = []
        for (model, layer), group in dataframe.groupby(["model", "layer"], sort=False):
            group = group.sort_values("rank")
            features = "; ".join(
                f"{row.feature} ({float(row.mean_delta_roc_auc):.4f})"
                for row in group.itertuples(index=False)
            )
            rows.append(
                {
                    "model": model,
                    "layer": layer,
                    "five largest held-out importances": features,
                }
            )
        return pd.DataFrame(rows)
    return dataframe


def markdown_heading(column: object) -> str:
    heading = str(column).replace("_", " ")
    replacements = {
        "r2": "R²",
        "roc auc": "ROC-AUC",
        "sd": "SD",
        "ess": "ESS",
        "mle": "MLE",
        "fci": "FCI",
        "rf": "RF",
        "tfidf": "TF-IDF",
    }
    words = [replacements.get(word.casefold(), word) for word in heading.split()]
    result = " ".join(words)
    return result[:1].upper() + result[1:]


def dataframe_markdown(dataframe: pd.DataFrame) -> str:
    columns = [markdown_heading(column) for column in dataframe.columns]
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = [
        "| " + " | ".join(markdown_value(value) for value in row) + " |"
        for row in dataframe.itertuples(index=False, name=None)
    ]
    return "\n".join([header, divider, *rows])


def write_table_index(table_dir: Path, output_path: Path) -> None:
    sections = [
        "# Tables",
        "",
        "These are the machine-readable values displayed in the paper. Decimal places follow the available archived outputs; the manuscript may show fewer digits.",
        "",
    ]
    for number in range(1, 18):
        filename = f"table_{number:02d}.csv"
        data = pd.read_csv(table_dir / filename)
        display = markdown_table(number, data)
        sections.extend(
            [
                f"## Table {number}",
                "",
                TABLE_CAPTIONS[number],
                "",
                f"[Download the CSV](tables/{filename})",
                "",
                dataframe_markdown(display),
                "",
            ]
        )
        if number == 13:
            sections.extend(
                [
                    "> Table 13 contains short third-party corpus excerpts reproduced for scholarly context. No rights in those excerpts are granted by this repository.",
                    "",
                ]
            )
    output_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")


def write_figure_index(output_path: Path) -> None:
    captions = {
        1: "Mean ESS pointwise ID (±1 SD) across approximately matched relative depths in Pythia, Qwen, and Apertus. This uses the paper-era aggregate; see the artifact map for the pinned Apertus comparison.",
        2: "Sensitivity of median Pythia ESS pointwise ID to reference-set size for four neighbourhood sizes. The archived rows identify layer 12 although the manuscript caption says layer 16.",
        3: "Reference-resampling stability for Pythia layer 16 at k = 1000. Points are pairwise correlations among five sampled reference sets.",
        4: "Gaussian synthetic calibration in D = 100 with 15,000 reference points and 100 queries.",
        5: "Mean pointwise ID (±1 SD) across depth for ESS, FCI, and MLE in all three models.",
        6: "Mean ESS pointwise ID (±1 SD) across Pythia and Apertus training checkpoints.",
    }
    sections = [
        "# Figures",
        "",
        "The repository keeps a browser-friendly PNG and a vector PDF for every numbered paper figure.",
        "",
    ]
    for number in range(1, 7):
        sections.extend(
            [
                f"## Figure {number}",
                "",
                captions[number],
                "",
                f"[PDF](figures/figure_{number:02d}.pdf) · [PNG](figures/figure_{number:02d}.png)",
                "",
                f"![Figure {number}](figures/figure_{number:02d}.png)",
                "",
            ]
        )
    output_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")


def require_files(paths: Iterable[Path]) -> None:
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing paper inputs: " + ", ".join(missing))


def main() -> None:
    args = parse_args()
    required = [
        args.derived_dir / "main_targets.parquet",
        args.derived_dir / "checkpoint_targets.parquet",
        args.paper_data_dir / "figure_01_05_pointwise_id_summary.csv",
        args.paper_data_dir / "figure_02_reference_size_summary.csv",
        args.paper_data_dir / "figure_03_reference_resampling_pairs.csv",
        args.paper_data_dir / "figure_04_gaussian_calibration_summary.csv",
    ]
    require_files(required)
    figure_dir = args.output_dir / "figures"
    table_dir = args.output_dir / "tables"
    figure_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    paper_style()
    checkpoints = pd.read_parquet(args.derived_dir / "checkpoint_targets.parquet")
    summary = pd.read_csv(args.paper_data_dir / "figure_01_05_pointwise_id_summary.csv")
    summary = summary.rename(columns={"standard_deviation": "sd"})
    summary["estimator"] = summary["estimator"].replace({"pyFCI": "FCI"})
    derived_summary = main_summary(
        pd.read_parquet(args.derived_dir / "main_targets.parquet")
    )
    comparison = summary.merge(
        derived_summary,
        on=["model", "layer", "estimator"],
        suffixes=("_paper", "_bundle"),
    )
    comparison["mean_delta_bundle_minus_paper"] = (
        comparison["mean_bundle"] - comparison["mean_paper"]
    )
    comparison["sd_delta_bundle_minus_paper"] = (
        comparison["sd_bundle"] - comparison["sd_paper"]
    )
    write_csv(
        comparison[
            [
                "model",
                "layer",
                "estimator",
                "mean_paper",
                "mean_bundle",
                "mean_delta_bundle_minus_paper",
                "sd_paper",
                "sd_bundle",
                "sd_delta_bundle_minus_paper",
            ]
        ],
        args.output_dir / "paper_value_comparison.csv",
    )
    build_figure_1(summary, figure_dir)
    build_figure_2(args.paper_data_dir, figure_dir)
    build_figure_3(args.paper_data_dir, figure_dir)
    build_figure_4(args.paper_data_dir, figure_dir)
    build_figure_5(summary, figure_dir)
    build_figure_6(checkpoints, figure_dir)
    build_tables(args.paper_data_dir, table_dir)
    write_figure_index(args.output_dir / "FIGURES.md")
    write_table_index(table_dir, args.output_dir / "TABLES.md")
    build_experiment_artifacts(args.paper_data_dir, args.output_dir, dataframe_markdown)
    print(f"Wrote six numbered figures, seventeen numbered tables, and geometry/control artifacts to {args.output_dir}")


if __name__ == "__main__":
    main()
