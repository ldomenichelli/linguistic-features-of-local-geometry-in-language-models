# Where the paper results come from

There are three useful meanings of “reproduce” in this project.

1. **Rebuild the paper artifact.** `make paper` recreates every numbered plot and table from the compact files in this repository. This is quick and does not require model weights.
2. **Rerun the downstream experiment.** `make analysis` refits the main ESS models from the sentence-level numeric feature and target tables. `make analysis-extended` adds MLE, FCI, and all three feature sets.
3. **Regenerate the measurements.** The scripts in `src/full_pipeline/` start from independently acquired Pile data and model weights, extract hidden states, and recompute pointwise ID. This is the expensive path and requires GPUs, large intermediate arrays, and third-party data that cannot be copied into this repository.

The `reproduction_level` column in [`artifacts.csv`](artifacts.csv) uses four labels:

| Label | Meaning |
|---|---|
| `bundle_recomputation` | The experiment can be rerun from the sentence-level numeric Parquet files. |
| `archived_numeric_rerender` | The plot can be rebuilt from a compact archived numeric summary; the large upstream arrays are omitted. |
| `archived_result_assembly` | Fold-level or experiment-level outputs are included and assembled into the paper table. |
| `published_value_record` | The exact aggregate was not retained in a safe distributable form, so the paper values and full method are preserved. |

## Figures

| Figure | What it shows | Public rebuild input | Status |
|---:|---|---|---|
| 1 | Mean ESS across matched depths | `figure_01_05_pointwise_id_summary.csv` | Rerendered from the paper-era summary. |
| 2 | Reference-size plateau | `figure_02_reference_size_summary.csv` | Rerendered from the archived sweep summary. |
| 3 | Reference-resampling stability | `figure_03_reference_resampling_pairs.csv` | Rerendered from all 40 ESS seed-pair comparisons. |
| 4 | Gaussian calibration | `figure_04_gaussian_calibration_summary.csv` | Rerendered from a fully synthetic experiment. |
| 5 | ESS, FCI, and MLE depth profiles | `figure_01_05_pointwise_id_summary.csv` | Rerendered from the paper-era summary. |
| 6 | Pythia and Apertus checkpoint trajectories | `checkpoint_targets.parquet` | Recomputed directly from the public sentence-level targets. |

The manuscript exports for Figures 1–3 and 6 are committed under `paper/figures/`. The exact final export commands for Figures 4 and 5 were not retained, so their committed PNGs and vector PDFs are clean rerenders from the archived paper values. The builder reproduces those files directly.

## Tables

Tables 2, 6, and 11 correspond most directly to the public downstream analysis. Tables 3, 4, 5, 7, and 16 use archived permutation-importance or ALE summaries because recomputing all folds and shuffles is substantially slower. Tables 8–10 and 14–15 depend on alternative neighbourhoods, the extra Pile split, or fold-local word vocabularies; their compact numeric results are preserved even though the raw text and representation arrays are not.

Tables 12 and 13 need special care. The exact completed classification-importance aggregate behind Table 12 was not retained, so its paper values are preserved together with the recorded five-fold, eight-shuffle procedure. Table 13 includes the seven paper excerpts and their query indices; the numeric feature and ESS values can be checked against the public bundle, but the excerpts themselves are third-party text.

## Two paper-era discrepancies

The repository records these rather than silently rewriting either the manuscript or the results:

- The manuscript calls Figure 2 a Pythia layer-16 experiment. The exact plotted artifact, filename, and archived rows all identify layer 12. No corresponding layer-16 plateau artifact was found.
- The paper-era Apertus values used in Figures 1 and 5, and in part of Table 11, do not exactly match a fresh calculation from the pinned 15T Apertus targets in the public bundle. `make paper` writes `results/paper/paper_value_comparison.csv` so that the Figure 1/5 differences are explicit.

These discrepancies do not affect the availability of the reported artifacts, but they limit a claim of bit-for-bit upstream regeneration. The paper-facing files keep the published values; the downstream workflow reports what the pinned public bundle produces.

## Geometry and control experiments

These experiments use the same `data/paper/`, `data/derived/`, `results/reference/`, and `paper/{tables,figures}/` layout as the numbered results. `make paper` also builds their descriptive, unnumbered tables and figures. They are archived numeric rerenders and result assemblies; adding them does not rerun the upstream experiments or change the numbered manuscript artifacts.

| Experiment | Public input | Paper artifact or supporting result |
|---|---|---|
| Neighbourhood scale and composition, three models | `data/paper/neighbourhood_locality_summary.csv`; `data/derived/neighbourhood_locality_metrics.parquet` | [k=1000 table](tables/neighbourhood_locality_k1000.csv), [outer-shell table](tables/neighbourhood_outer_shell.csv), [scale figure](figures/neighbourhood_locality.pdf), [rank-band figure](figures/neighbourhood_lexical_shells.pdf) |
| Earlier small-Pythia distance/composition diagnostics | `data/paper/pythia_small_k_{distance_profile_summary,composition_summary,stability_summary}.csv` | Full numeric summaries, including split, layer, metric, and neighbourhood labels |
| Every-layer small-Pythia geometry | `data/paper/pythia_small_all_layer_id.csv` | [All-layer figure](figures/pythia_small_all_layers.pdf), MLE and ESS, reference size 15,000, k=1000 |
| Layer and neighbourhood prediction sensitivity | `data/paper/layer_neighbourhood_regression.csv` | [Full-feature Ridge/RF table](tables/layer_neighbourhood_regression.csv) |
| Grouped permutation importance | `data/paper/grouped_permutation_importance.csv` | [Grouped-importance table](tables/grouped_permutation.csv) |
| Feature-family ablations | `data/paper/feature_family_ablations.csv` | [Family-ablation table](tables/feature_family_ablation.csv) |
| Source and TF-IDF controls | `data/paper/source_tfidf_{word,word_char}_nonlinear_incremental_effects.csv` | [Paired incremental results](tables/source_tfidf_incremental.csv); out-of-fold predictions, fold scores and tuning records under `results/reference/source_tfidf_*` |
| Perplexity-only Ridge baseline | `data/paper/perplexity_only_ridge.csv` | [Ridge baseline table](tables/perplexity_only_ridge.csv), MLE and ESS, with run/split/fold labels |
| Perplexity and geometry across layers and k | `data/paper/perplexity_ess_layer_neighbourhood.csv` | Full archived ESS correlation grid, alongside the main-model correlations in Table 1 |

### Neighbourhood locality

The three-model audit uses 500 uniformly sampled queries (seed 20260916), the original disjoint 15,000-reference sets, nine model/layer settings, and k in {100, 500, 1000, 2000, 3000}. Relative radius divides the kth-neighbour distance by the query's median distance to all references. TF-IDF is fitted on reference excerpts only; the lexical baseline is matched to each neighbourhood's source composition. Separate rank bands prevent the closest neighbours from dominating cumulative averages. Intervals use 2,000 paired query bootstrap resamples, conditional on the fixed references. Parameters and selected query positions are in `configs/neighbourhood_locality.json`.

At k=1000, median relative radius ranges from 0.765 to 0.903. Same-source fractions range from 36.2% to 63.5%, versus 19.5% under random sampling. Lexical enrichment remains positive for ranks 501–1000 in all nine settings. These observations characterize the neighbourhood scale and retained lexical/source structure; they do not establish semantic homogeneity, local flatness, or an optimal k. Estimator stability alone does not establish locality.

The validation table and `neighbourhood_locality_apertus_layer16_mle_precision.csv` preserve the numerical audit. Six Apertus layer-16 query/setting pairs have reconstructed MLE relative errors above 1%, reaching 18.82%; direct float64 distance checks support the audit calculation. Large representation offsets affect float32 distance arithmetic. The audit does not recompute ESS or replace the archived MLE regression results. Top-1000 neighbour overlap with CPU float32 distances is at least 99.8%; archived GPU neighbour identities were not retained.

### Coverage and correlated feature families

The small-Pythia ID summaries include all 24 transformer layers. `layer_idx` is zero-based, while `layer_name` retains the original one-based name. This is an all-layer geometric analysis, not a claim that a linguistic regression was fitted at every layer.

The imported prediction grid covers Pythia-1.4B layers 1, 2, 12, 13, 23, 24; Pythia-6.9B layers 1, 2, 16, 17, 31, 32; Qwen layers 1–6, 14, 15, 27, 28; and Apertus layers 2, 16, 31. Available k and estimators vary by setting. The larger Pythia/Qwen historical grids contain k=10, 100, 500, 2000, 3000; their main k=1000 results remain in the existing main-model tables. Small-Pythia regression includes k=10, 100, 500, 1000, while its retained grouped importance and family ablations cover k=500, 1000. Apertus family analyses use k=1000 and the historical final-model run, not a refit on the pinned public 15T bundle.

Grouped permutation shuffles all columns in a family together on held-out folds; family ablation refits after removing that family. Both regression and low/high classification are retained with task, target, estimator, model, and neighbourhood labels. R² and ROC-AUC drops must not be pooled. The `run_kind` column distinguishes original joint MLE/ESS, ESS-only, and pyFCI runs; overlapping runs are not independent replicates. Effects describe model dependence on correlated feature blocks, not unique causal contributions of individual descriptors. Negative drops are retained.

### Source and lexical controls

The two matched controls use 1,866 period-final excerpts shared by all three models, three layers per model, k=1000, and 15,000 references. The baseline combines source indicators, five surface/diversity measures, three model-specific count measures, fold-local word TF-IDF (up to 10,000 terms), and final-word identity. The second variant also includes character TF-IDF. Three shared frequency summaries are excluded; the added forest uses 38 nonsurface Profiling-UD descriptors. Full parameter grids and feature lists are in `configs/source_tfidf_{word,word_char}.json`.

Five source-stratified outer folds assess generalization. Ridge penalties and forest correction settings are chosen inside the training data; the residual targets used to train the forest are themselves cross-fitted and centered. The correction-weight grid includes zero. The clean outer test folds are used for paired comparison. Apertus uses the pinned 15T revision; Pythia and Qwen use their archived `main` revisions.

For the word-only control, pooled out-of-fold R² improves by approximately 0.0035–0.0112 across the nine settings. All nine unadjusted paired 95% intervals exclude zero, but only three Bonferroni familywise intervals do. Both interval types and the character-TF-IDF sensitivity are retained. Intervals bootstrap fixed out-of-fold predictions within source and do not include refitting or tuning uncertainty. This supports a small conditional predictive contribution on the matched cohort; it does not rule out richer topic/semantic confounding or establish a causal decomposition.

### Perplexity and interpretation boundaries

The archived perplexity grid contains correlations across model revisions, layers, reference sizes, and k. Filter those labels before comparing settings; checkpoint results must not be mixed with final models. Correlation with perplexity is a relationship to model behavior, not an evaluation of a downstream application.

The perplexity-only Ridge baseline is archived in `perplexity_only_ridge.csv`. Its sole predictor is `log_perplexity`, and its targets are MLE and ESS for Pythia-1.4B. The `all_layers_3fold` run contains 96 per-layer results (24 layers × two evaluation splits × two estimators) plus two pooled results; it uses reference size 15,000 and k=1000. The separate `eval_known_layer24_5fold` run contains two results on 2,000 queries. Its archived configuration leaves reference size and k unspecified because targets were supplied as an input table; the historical directory identifies the 15,000/k=1000 setting. Those null configuration values are preserved.

The retained implementation uses training-fold standardization and Ridge with alpha=1, with shuffled KFold (default seed 42). The archived configurations omit the seed, so the default is not independent confirmation of a run-specific seed. Reported scores are fold means and standard deviations. The two pooled rows combine repeated query/layer observations under row-wise cross-validation and should not be interpreted as a held-out-query test across layers. Keep three-fold and five-fold results distinct. Configurations are in `configs/perplexity_ridge_*.json`. These are archived baselines; no incremental benefit from adding linguistic features is claimed by this table.

Likewise, held-out R² near 0.5 describes predictive performance in a particular setting. It leaves substantial unexplained variation, and these results neither exhaust semantic/discourse effects nor show that linguistic features determine local dimension.

### Provenance and verification

`configs/experiment_results_manifest.json` records source logical IDs and SHA-256 hashes, released-file hashes, schemas, and row counts. The import retains the original study files. To repeat it from a local study checkout:

```bash
python scripts/import_experiment_results.py --source-root /path/to/original-study
make paper
make check-experiments
```

The checks verify released hashes, all-layer coverage, 500-query locality coverage, agreement between query-level and aggregate locality values, paired R² from saved out-of-fold predictions, and exact table reconstruction within numeric tolerance. Re-estimating the neighbourhoods or refitting text-dependent controls requires the independently acquired source text and representation inputs; the compact archive supports verification and rerendering.
