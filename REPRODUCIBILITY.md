# Reproducing the experiments

This guide describes the preserved `local-geometry-reproduction` archive and its original numbering, including additional Ridge and logistic comparisons. The current random-forest manuscript has 7 figures and 16 tables; its transcribed result snapshot and mapping are in [paper/current/README.md](paper/current/README.md). The snapshot is not silently regenerated from older numbered tables.

To rebuild the interactive browser from the packaged evaluation excerpts and released numeric tables, run `make site`. To check its text hashes, every feature/score join, percentiles, all current table grids, figure hashes, and download links, run `make check-site`. To preview the committed site without analysis dependencies, run `make serve`.

The repository supports a fast paper build, a complete downstream refit from sanitized numeric data, and a compute-intensive rebuild of the geometric measurements. Choose the boundary that matches the question you want to check.

## 1. Rebuild the paper artifacts

After installing `requirements-analysis.txt`, run:

```bash
make PYTHON=.venv/bin/python paper
```

This writes six numbered figures, seventeen numbered CSV tables, three additional experiment figures, seven additional tables, and rendered Markdown indexes to `results/paper/`. Figures 1, 2, 3, 4, and 5 use archived numeric summaries; Figure 6 is summarized from the public checkpoint target table. The table builder combines the archived result files in `data/paper/` with the published aggregate values that could not safely or exactly be reconstructed.

The committed versions in `paper/` remain unchanged. Small visual differences are expected across Matplotlib and font-library versions. `make check-paper` checks that every expected artifact exists, that every table has the expected shape, and that the rebuilt table values agree with the committed CSVs.

The builder also writes `results/paper/paper_value_comparison.csv`. It compares the paper-era means behind Figures 1 and 5 with fresh means from `main_targets.parquet`, making the known Apertus difference visible rather than silently replacing either result.

## 2. Rerun the downstream models

The main analysis joins rows by `query_index`; identifiers and text hashes are never supplied to an estimator. All imputation and scaling are fitted inside the training fold.

```bash
make PYTHON=.venv/bin/python analysis
make PYTHON=.venv/bin/python verify
```

The default run fits:

- ESS Ridge and random-forest regression with the full and no-frequency feature sets;
- balanced logistic and random-forest classification of the bottom and top ESS quintiles; and
- full-feature ESS random-forest and Ridge regression across the retained Pythia and Apertus checkpoints.

The extended run adds all MLE, ESS, and FCI regressions with the full, no-frequency, and no-raw feature sets:

```bash
make PYTHON=.venv/bin/python analysis-extended
```

The fixed protocol is:

| Component | Setting |
|---|---|
| Fold assignment | five-fold shuffled `KFold`, seed 42 |
| Ridge | `alpha=1`; fold-local median imputation and standardization |
| Random forest | 300 trees; `min_samples_leaf=2`; seed 42 |
| Low/high labels | values at or below the 20th percentile and at or above the 80th percentile; middle rows excluded |
| Logistic regression | L2, balanced classes, at most 3,000 iterations |
| Classification forest | balanced subsample classes; otherwise the same forest settings |

The analysis writes fold scores, out-of-fold predictions, summaries, plots, and a machine-readable run manifest under `results/generated/`. Verification checks schema, fold coverage, the feature ablations, absence of leaked identifiers, and numerical agreement with the reference ESS results.

### Permutation importance and ALE

The paper's feature rankings were computed on held-out folds. For every fitted forest, each feature was shuffled eight times in the test fold. Regression importance is the decrease in held-out R²; classification importance is the decrease in held-out ROC-AUC. The tables report the mean across repeats and folds.

The cross-fitted one-dimensional ALE analysis used:

- ten initial bins defined by training-fold quantiles;
- adaptive merging until a bin had at least 15 held-out rows;
- effects expressed in training-target standard-deviation units;
- the contrast between the 10th and 90th feature percentiles;
- 1,000 bin-stratified held-out-row bootstrap replicates; and
- a stable direction only when the interval excluded zero, all five fold curves were available, and at least four folds agreed in sign.

The complete retained main and checkpoint aggregates are in `data/paper/main_rf_permutation_ale.csv`, `data/paper/ess_no_frequency_permutation_ale.csv`, and the two checkpoint permutation files. Tables 3–5, 7, and 16 are assembled from them by `scripts/build_paper_artifacts.py`.

### Auxiliary experiments

The artifact map gives the exact public input for every result. In brief:

- reference-size and resampling plots use the archived numeric sweep summaries for Figures 2 and 3;
- the Gaussian calibration in Figure 4 uses dimension 100, 15,000 reference points, 100 queries, and `k ∈ {10, 100, 500, 1000, 2000, 3000}`;
- Table 8 uses the archived multi-layer, multi-`k` regression grid for Pythia and Qwen;
- Tables 14 and 15 use fold-local 46-term TF-IDF representations, with the most-frequent and 1–5% document-frequency vocabularies fitted only on training folds; and
- checkpoint tables use the same 46 predictors, five folds, forest settings, and held-out permutation procedure as the main models.

See [`paper/ARTIFACTS.md`](paper/ARTIFACTS.md) for the result-by-result status and [`configs/paper.yaml`](configs/paper.yaml) for the complete settings.

## 3. Regenerate representations and pointwise ID

This path starts before the public Parquet boundary. It requires independently acquired Pile shards, model weights, a UD parser, GPU storage for hidden states, and substantial nearest-neighbour and FCI computation.

Install the full recorded environment:

```bash
python3 -m venv .venv-full
.venv-full/bin/python -m pip install --upgrade pip
.venv-full/bin/python -m pip install -r requirements-full.txt
```

Place the decompressed Pile members at the paths described in [DATA.md](DATA.md), verify their hashes, and prepare the excerpts:

```bash
.venv-full/bin/python src/full_pipeline/prepare_pile_excerpts.py
```

The pipeline then performs these stages:

1. select the 15,000-reference and 2,000-query splits;
2. extract last-token hidden states at the configured layers;
3. compute nearest-neighbour distances;
4. estimate pointwise MLE and ESS;
5. run the local pyFCI adaptation; and
6. materialize sentence-level target tables.

`scripts/run_full_pipeline.py` connects those stages. Inspect the exact command before starting a large run:

```bash
.venv-full/bin/python scripts/run_full_pipeline.py --help
```

For example, this prints and validates the pinned Apertus 15T plan without launching it:

```bash
.venv-full/bin/python scripts/run_full_pipeline.py \
  --model-name swiss-ai/Apertus-8B-2509 \
  --revision 96982d7c559fab9c2b19b6934ad28499c5c341e9 \
  --seen-file data/interim/seen_excerpts.jsonl \
  --unseen-file data/interim/unseen_excerpts.jsonl \
  --output-root artifacts/apertus-15t \
  --layers 2,16,31 \
  --seed 42 \
  --reference-size 15000 \
  --k 1000 \
  --seen-count 17000 \
  --query-count 2000 \
  --dtype bfloat16 \
  --device cuda:0 \
  --dry-run
```

Remove `--dry-run` only after checking data access, revisions, free storage, and GPU memory. The output is expected to vary slightly across CUDA kernels, nearest-neighbour tie ordering, and pyFCI Monte Carlo execution.

## 4. Geometry, feature-family, and source-control experiments

`make paper` also rebuilds three descriptive figures and seven tables for neighbourhood locality, all-layer small-Pythia geometry, layer/k regression sensitivity, grouped permutation importance, family ablations, source/TF-IDF controls, and perplexity-only Ridge baselines. They appear in the regular [figure](paper/FIGURES.md) and [table](paper/TABLES.md) indexes. Archived perplexity correlations and earlier neighbour diagnostics are included as numeric grids. The [artifact map](paper/ARTIFACTS.md#geometry-and-control-experiments) documents coverage, methods, and interpretation limits.

```bash
make PYTHON=.venv/bin/python check-experiments
```

This validates the imported files and rebuilds no models. It independently calculates paired source/TF-IDF R² from out-of-fold predictions and locality means from query-level measurements. It is also included in `make check`.

For a concrete pipeline example, take one evaluation excerpt and compute its last-token representation at a selected model layer. Find its k nearest neighbours within the separate 15,000-excerpt reference set, and estimate its pointwise ID from that neighbourhood. Compute the excerpt's linguistic feature vector independently. Repeating this for all evaluation excerpts yields the feature/ID regression table. During cross-validation, fit preprocessing and the predictor on training queries and score held-out queries; the reference set is disjoint from all evaluation queries. ID estimation is the measurement stage; relating these per-excerpt measurements to linguistic profiles is the analysis stage.
