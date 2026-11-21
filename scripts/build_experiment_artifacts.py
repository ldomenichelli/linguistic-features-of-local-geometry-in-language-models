#!/usr/bin/env python3
"""Render the additional geometry experiments alongside numbered paper artifacts."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

TABLES = {
    "neighbourhood_locality_k1000": "Neighbourhood radius and composition at k = 1000",
    "neighbourhood_outer_shell": "Lexical enrichment for neighbour ranks 501–1000",
    "source_tfidf_incremental": "Incremental nonsurface prediction beyond source and lexical controls",
    "feature_family_ablation": "Feature-family ablations across available model/layer/k settings",
    "grouped_permutation": "Grouped held-out permutation importance across available settings",
    "layer_neighbourhood_regression": "Full-feature regression across available layers and neighbourhood sizes",
    "perplexity_only_ridge": "Ridge prediction of MLE and ESS from log-perplexity alone",
}
FIGURES = {
    "neighbourhood_locality": "Neighbourhood scale and composition across k",
    "neighbourhood_lexical_shells": "Lexical enrichment within separate neighbour-rank bands",
    "pythia_small_all_layers": "Pythia-1.4B ID estimates at every transformer layer",
}


def build_tables(data_dir):
    locality = pd.read_csv(data_dir / "neighbourhood_locality_summary.csv")
    main = locality.loc[locality.kind.eq("cumulative") & locality.k.eq(1000)]
    outer = locality.loc[locality.kind.eq("shell") & locality.rank_start.eq(501) & locality.k.eq(1000)]
    results = {
        "neighbourhood_locality_k1000": main[["model", "layer", "n_queries", "radius_median",
            "radius_ratio_median", "radius_ratio_q25", "radius_ratio_q75", "same_source_mean",
            "same_source_null_mean", "tfidf_cosine_mean", "tfidf_random_mean", "source_entropy_mean"]],
        "neighbourhood_outer_shell": outer[["model", "layer", "same_source_mean", "tfidf_cosine_mean",
            "tfidf_source_matched_random_mean", "tfidf_source_matched_gain_mean",
            "tfidf_source_matched_gain_ci_low", "tfidf_source_matched_gain_ci_high"]],
    }
    controls = []
    for variant in ("word", "word_char"):
        frame = pd.read_csv(data_dir / f"source_tfidf_{variant}_nonlinear_incremental_effects.csv")
        frame.insert(0, "lexical_baseline", variant)
        controls.append(frame)
    results["source_tfidf_incremental"] = pd.concat(controls, ignore_index=True)
    # Retain setting and task labels: regression R² and classification AUC must not be pooled.
    results["feature_family_ablation"] = pd.read_csv(data_dir / "feature_family_ablations.csv")
    results["grouped_permutation"] = pd.read_csv(data_dir / "grouped_permutation_importance.csv")
    results["perplexity_only_ridge"] = pd.read_csv(data_dir / "perplexity_only_ridge.csv")
    regression = pd.read_csv(data_dir / "layer_neighbourhood_regression.csv")
    results["layer_neighbourhood_regression"] = regression.loc[
        regression.feature_subset.eq("all_existing_features") & regression.model_name.isin(["rf", "ridge"]),
        ["model_key", "run_kind", "layer", "k", "reference_size", "target_name", "model_name",
         "n_rows", "n_features", "n_splits", "cv_strategy", "metric_r2_mean", "metric_r2_std", "metric_r2_oof"]]
    return results


def save(fig, directory, name):
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(directory / f"{name}.{suffix}", dpi=180)
    plt.close(fig)


def build_figures(data_dir, figure_dir):
    data = pd.read_csv(data_dir / "neighbourhood_locality_summary.csv")
    models = ["Pythia-6.9B", "Qwen2.5-7B", "Apertus-8B"]
    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    for col, model in enumerate(models):
        subset = data.loc[data.model.eq(model) & data.kind.eq("cumulative")]
        for layer, frame in subset.groupby("layer", sort=True):
            frame = frame.sort_values("k")
            x = frame.k.to_numpy()
            line, = axes[0, col].plot(x, frame.radius_ratio_median, "o-", label=f"Layer {layer}")
            color = line.get_color()
            axes[0, col].fill_between(x, frame.radius_ratio_q25, frame.radius_ratio_q75, color=color, alpha=.15)
            for row, metric, scale in [(1, "same_source_gain", 100), (2, "tfidf_source_matched_gain", 1)]:
                axes[row, col].plot(x, frame[metric + "_mean"] * scale, "o-", color=color)
                axes[row, col].fill_between(x, frame[metric + "_ci_low"] * scale,
                                            frame[metric + "_ci_high"] * scale, color=color, alpha=.15)
        axes[0, col].set_title(model)
        axes[0, col].legend(fontsize=9)
        for row in range(3):
            axes[row, col].axhline(1 if row == 0 else 0, color="black", ls=":", lw=1)
            axes[row, col].axvline(1000, color="grey", ls="--", alpha=.5)
            axes[row, col].set_xscale("log")
            ks = sorted(subset.k.unique())
            axes[row, col].set_xticks(ks, [str(k) for k in ks], rotation=45)
            axes[row, col].grid(alpha=.2)
        axes[2, col].set_xlabel("Number of neighbours k")
    axes[0, 0].set_ylabel("Relative radius (median and IQR)")
    axes[1, 0].set_ylabel("Same-source gain (percentage points; 95% CI)")
    axes[2, 0].set_ylabel("TF-IDF gain over source-matched random (95% CI)")
    save(fig, figure_dir, "neighbourhood_locality")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for col, model in enumerate(models):
        subset = data.loc[data.model.eq(model) & data.kind.eq("shell")]
        for layer, frame in subset.groupby("layer"):
            frame = frame.sort_values("rank_start")
            x = range(len(frame))
            line, = axes[col].plot(x, frame.tfidf_source_matched_gain_mean, "o-", label=f"Layer {layer}")
            axes[col].fill_between(x, frame.tfidf_source_matched_gain_ci_low,
                                  frame.tfidf_source_matched_gain_ci_high, color=line.get_color(), alpha=.15)
            axes[col].set_xticks(list(x), [f"{r.rank_start}–{r.k}" for r in frame.itertuples()], rotation=45)
        axes[col].set_title(model)
        axes[col].axhline(0, color="black", ls=":", lw=1)
        axes[col].set_xlabel("Neighbour rank band")
        axes[col].legend(fontsize=9)
    axes[0].set_ylabel("TF-IDF gain over source-matched random (95% CI)")
    save(fig, figure_dir, "neighbourhood_lexical_shells")

    data = pd.read_csv(data_dir / "pythia_small_all_layer_id.csv")
    data = data.loc[data.reference_size.eq(15000) & data.k.eq(1000)]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, estimator in zip(axes, ["MLE", "ESS"]):
        frame = data.loc[data.estimator.eq(estimator)].sort_values("layer_idx")
        ax.plot(frame.layer_idx, frame["mean"], "o-", label="Mean")
        ax.plot(frame.layer_idx, frame["median"], "s--", label="Median")
        ax.set_xlabel("Layer index (zero-based)")
        ax.set_ylabel(f"{estimator} pointwise ID")
        ax.set_title(f"Pythia-1.4B · {estimator}")
        ax.legend()
        ax.grid(alpha=.2)
    save(fig, figure_dir, "pythia_small_all_layers")


MODEL_LABELS = {
    "pythia-1.4b": "Pythia-1.4B", "pythia-6.9b": "Pythia-6.9B",
    "qwen-2.5-7b": "Qwen2.5-7B", "apertus-8b": "Apertus-8B",
}
FAMILY_LABELS = {
    "raw_text": "Surface", "lexical_frequency": "Frequency",
    "upos_distribution": "UPOS", "lexical": "Lexical",
    "verbal_predicate_structure": "Predicate", "parse_tree_structure": "Tree",
    "syntactic_relations": "Relations", "subordination": "Subordination",
    "verbal_edge_structure": "Verb edges",
}
TABLE_NOTES = {
    "neighbourhood_locality_k1000": "500 queries per setting; k=1000. Relative radius is the kth-neighbour distance divided by the query's median reference distance. Brackets show the interquartile range; composition and cosine values are means.",
    "neighbourhood_outer_shell": "Neighbours ranked 501–1000. Lexical gain is relative to the source-composition-matched random baseline; brackets show the paired 95% query-bootstrap interval.",
    "source_tfidf_incremental": "Matched cohort of 1,866 period-final excerpts. Scores are pooled out-of-fold R². Both unadjusted and familywise 95% intervals are shown; word and word-plus-character baselines remain separate.",
    "feature_family_ablation": "Held-out score decrease after refitting without each feature family. All archived settings and all nine families are displayed. Positive values indicate worse performance after removal; negative values are retained. Scores are R² for regression and ROC-AUC for low/high classification. Full feature-set, split, and reference-size labels remain in the CSV.",
    "grouped_permutation": "Mean held-out score decrease when all features in a family are shuffled together. All archived settings and all nine families are displayed. Scores are R² for regression and ROC-AUC for low/high classification; fold variability and family sizes are in the CSV.",
    "layer_neighbourhood_regression": "All archived full-feature Ridge and random-forest regression settings. R² mean and SD are across validation folds. Historical run labels are retained; overlapping runs must not be pooled as independent replicates.",
    "perplexity_only_ridge": "Pythia-1.4B Ridge baselines using log-perplexity as the sole predictor. All 100 archived results are displayed. Three-fold and five-fold runs remain separate. Pooled rows repeat queries across layers and are not a held-out-query evaluation across layers.",
}


def interval_text(frame, mean, low, high):
    return [f"{m:.6g} [{lo:.6g}, {hi:.6g}]" for m, lo, hi in zip(frame[mean], frame[low], frame[high])]


def experiment_table_views(name, frame):
    """Return readable views without averaging across settings or dropping families."""
    if name == "neighbourhood_locality_k1000":
        display = frame[["model", "layer", "radius_median", "same_source_mean", "same_source_null_mean",
                         "tfidf_cosine_mean", "tfidf_random_mean", "source_entropy_mean"]].copy()
        display.insert(3, "Relative radius [IQR]", interval_text(frame, "radius_ratio_median", "radius_ratio_q25", "radius_ratio_q75"))
        yield "", display.rename(columns={"radius_median": "Median radius", "same_source_mean": "Same source",
            "same_source_null_mean": "Random same source", "tfidf_cosine_mean": "TF-IDF cosine",
            "tfidf_random_mean": "Random cosine", "source_entropy_mean": "Source entropy"})
    elif name == "neighbourhood_outer_shell":
        display = frame[["model", "layer", "same_source_mean", "tfidf_cosine_mean", "tfidf_source_matched_random_mean"]].copy()
        display["Gain [95% CI]"] = interval_text(frame, "tfidf_source_matched_gain_mean", "tfidf_source_matched_gain_ci_low", "tfidf_source_matched_gain_ci_high")
        yield "", display.rename(columns={"same_source_mean": "Same source", "tfidf_cosine_mean": "TF-IDF cosine",
                                           "tfidf_source_matched_random_mean": "Source-matched random cosine"})
    elif name == "source_tfidf_incremental":
        for baseline, group in frame.groupby("lexical_baseline", sort=False):
            display = group[["model", "layer", "baseline_r2_oof", "augmented_r2_oof", "delta_r2_oof"]].copy()
            display["Delta [95% CI]"] = interval_text(group, "delta_r2_oof", "delta_r2_ci_low", "delta_r2_ci_high")
            display["Delta [familywise 95% CI]"] = interval_text(group, "delta_r2_oof", "delta_r2_familywise_ci_low", "delta_r2_familywise_ci_high")
            yield {"word": "Word TF-IDF", "word_char": "Word and character TF-IDF"}[baseline], display.rename(
                columns={"baseline_r2_oof": "Baseline R²", "augmented_r2_oof": "Augmented R²", "delta_r2_oof": "Delta R²"})
    elif name in {"feature_family_ablation", "grouped_permutation"}:
        family = "removed_family" if name == "feature_family_ablation" else "feature_family"
        value = "metric_drop" if name == "feature_family_ablation" else "grouped_permutation_importance_mean"
        keys = ["model_key", "run_kind", "target_name", "model_name", "task_type", "split", "reference_size", "feature_subset"]
        for key, group in frame.groupby(keys, sort=False, dropna=False):
            model, run, target, predictor, task, split, ref, subset = key
            metric = "R²" if task == "regression" else "ROC-AUC"
            heading = f"{MODEL_LABELS[model]} · {target.upper()} · {predictor.upper()} · {run} run · {metric} decrease"
            heading += f" · {split}, reference size {ref}, {subset}"
            display = group.pivot(index=["layer", "k"], columns=family, values=value)
            display = display.reindex(columns=list(FAMILY_LABELS)).rename(columns=FAMILY_LABELS).reset_index()
            yield heading, display
    elif name == "layer_neighbourhood_regression":
        for (model, run, target), group in frame.groupby(["model_key", "run_kind", "target_name"], sort=False):
            display = group.sort_values(["layer", "k", "model_name"])[
                ["layer", "k", "model_name", "n_rows", "n_features", "n_splits", "metric_r2_mean", "metric_r2_std"]]
            yield f"{MODEL_LABELS[model]} · {target.upper()} · {run} run", display.rename(columns={
                "model_name": "Predictor", "n_rows": "N", "n_features": "Features", "n_splits": "Folds",
                "metric_r2_mean": "R² mean", "metric_r2_std": "R² SD"})
    elif name == "perplexity_only_ridge":
        for (run, scope, split), group in frame.groupby(["run_id", "group_scope", "split_name"], sort=False, dropna=False):
            group = group.assign(layer_order=group.layer_name.str.extract(r"(\d+)", expand=False).astype(float))
            display = group.sort_values(["layer_order", "target"])[
                ["layer_name", "target", "n_rows", "n_splits", "r2_mean", "r2_std", "rmse_mean", "spearman_rho_mean"]]
            split_label = "pooled evaluation splits and layers" if pd.isna(split) else split
            yield f"{run} · {split_label}", display.rename(columns={
                "layer_name": "Layer", "target": "Estimator", "n_rows": "N", "n_splits": "Folds",
                "r2_mean": "R² mean", "r2_std": "R² SD", "rmse_mean": "RMSE mean", "spearman_rho_mean": "Spearman rho mean"})
    else:
        raise ValueError(f"Unknown experiment table: {name}")


def append_indexes(output_dir, render_table):
    with (output_dir / "TABLES.md").open("a") as handle:
        handle.write("\n## Geometry and control experiments\n\nThese tables retain the archived settings; experiment methods and coverage are documented in the repository’s `paper/ARTIFACTS.md`.\n\n")
        for name, title in TABLES.items():
            handle.write(f"### {title}\n\n{TABLE_NOTES[name]}\n\n[Download the CSV](tables/{name}.csv)\n\n")
            frame = pd.read_csv(output_dir / "tables" / f"{name}.csv")
            if name in {"feature_family_ablation", "grouped_permutation"}:
                handle.write("Family columns: " + "; ".join(f"{label} = `{key}`" for key, label in FAMILY_LABELS.items()) + ".\n\n")
            for heading, display in experiment_table_views(name, frame):
                if heading:
                    handle.write(f"#### {heading}\n\n")
                handle.write(render_table(display) + "\n\n")
    path = output_dir / "TABLES.md"
    path.write_text(path.read_text().rstrip() + "\n")
    with (output_dir / "FIGURES.md").open("a") as handle:
        handle.write("\n## Geometry and control experiments\n\n")
        for name, title in FIGURES.items():
            handle.write(f"### {title}\n\n[PDF](figures/{name}.pdf) · [PNG](figures/{name}.png)\n\n![{title}](figures/{name}.png)\n\n")


def build_experiment_artifacts(data_dir, output_dir, render_table):
    for name, frame in build_tables(data_dir).items():
        frame.to_csv(output_dir / "tables" / f"{name}.csv", index=False)
    build_figures(data_dir, output_dir / "figures")
    append_indexes(output_dir, render_table)
