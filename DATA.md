# Data guide

The numeric reproduction archive contains two compact data layers; the interactive release adds verified evaluation excerpts as described below. `data/derived/` holds the sentence-level numeric inputs for refitting the downstream models. `data/paper/` holds small summaries from experiments whose raw text, representations, or full sweep outputs cannot be redistributed.

## Sentence-level analysis bundle

| File | Purpose |
|---|---|
| `features.parquet` | query index, one-way text digest, and 46 linguistic predictors |
| `main_targets.parquet` | MLE, ESS, and FCI for 3 models × 3 layers × 2,000 queries |
| `checkpoint_targets.parquet` | sentence-level checkpoint trajectories for Pythia and Apertus |

The analysis uses a 2,000-query evaluation split. The target tables keep all 2,000 query indices so that aggregate geometry plots do not silently change sample size.

`data/derived/MANIFEST.json` records each schema and SHA-256 digest. `VALIDATION.json` records alignment, uniqueness, null, and privacy checks performed when the bundle was built. The builder is kept in `scripts/build_release_bundle.py`.

Identifiers serve only to join and audit rows:

- `query_index` is the stable position within the prepared evaluation split;
- `text_sha256` is a one-way digest used to confirm text alignment; and
- model, layer, checkpoint, revision, `k`, and reference-size fields describe the target measurement.

The analysis code explicitly excludes identifiers and hashes from the predictor matrix.

## Paper-level summaries

`data/paper/` contains the values needed by `scripts/build_paper_artifacts.py`:

| Input | Used for |
|---|---|
| `figure_01_05_pointwise_id_summary.csv` | paper-era means and standard deviations in Figures 1 and 5 |
| `figure_02_reference_size_summary.csv` | Figure 2 reference-size sweep |
| `figure_03_reference_resampling_pairs.csv` | Figure 3 seed-pair agreement |
| `figure_04_gaussian_calibration_summary.csv` | Figure 4 synthetic calibration |
| `perplexity_correlations.csv` | Table 1 |
| `main_rf_permutation_ale.csv` | main Pythia/Qwen entries in Tables 3 and 7 |
| `ess_no_frequency_permutation_ale.csv` | ALE and importance data behind Table 4 |
| `apertus_checkpoint_permutation.csv` | Tables 3, 5, and 7 |
| `neighbourhood_layer_sensitivity.csv` | Table 8 |
| `tfidf_classification.csv` | Table 14 |
| `tfidf_regression.csv` | Table 15 |
| `pythia_checkpoint_permutation.csv` | Table 16 |
| `published_tables/` | aggregates whose exact safe source table was not retained |

These are numeric result records, not substitutes for raw examples or hidden states. The precise role of each file is listed in [`paper/artifacts.csv`](paper/artifacts.csv).

## Source corpus

The experiment started from two decompressed members of The Pile:

| Role | Upstream member | Expected local path |
|---|---|---|
| seen/training source | `train/00.jsonl.zst` | `data/raw/pile/train/00.jsonl` |
| unseen/test source | `test.jsonl.zst` | `data/raw/pile/test.jsonl` |

The upstream project is <https://github.com/EleutherAI/the-pile>. Download locations and access conditions can change; acquire the corpus independently and follow the terms of its constituent sources.

The historical decompressed inputs had these SHA-256 digests:

| Input | SHA-256 |
|---|---|
| `train/00.jsonl` | `133538a67030fc5acfb291bb940d1c821e0b6086c68e7a5e3c667ad1f03061dc` |
| `test.jsonl` | `f87cb69612a54c672cb5afb0f3221ec15c05fae1f34798ae8973561a4b6074da` |

After preparation, the two JSONL files used by the study had these digests:

| Prepared split | SHA-256 |
|---|---|
| seen excerpts | `aa68c72954efcec7a66d30f0071ec42a00bec901a8f26937008b7ab6e9f9b071` |
| unseen excerpts | `147c14d6e318228e09ab6983693f5cd94f1279a0b91670831f0814bb865f3aae` |

The hashes allow an independently acquired copy to be checked without placing the source corpus in this repository. The compressed-download hashes were not retained.

## Excerpt preparation and split

`src/full_pipeline/prepare_pile_excerpts.py` implements the recorded filtering and truncation logic:

- at least 6 word-like items;
- at most 100 Pythia-tokenizer tokens;
- truncation at the last period boundary inside that budget;
- whitespace normalization; and
- filters for email addresses, code-like passages, number-heavy passages, and low letter density.

With seed 42, 17,000 eligible training excerpts and 2,000 eligible test excerpts were selected. The first group was divided into a 15,000-item reference manifold and a disjoint 2,000-item main evaluation set. The test excerpts formed the extra evaluation set used for the split-robustness check.

Raw and prepared JSONL belongs in ignored `data/raw/` and `data/interim/` directories. The preparation metadata keeps the original line index locally, but those source indices are not part of the public analysis bundle.

## Linguistic predictors

The full matrix contains 43 Profiling-UD descriptors and 3 sentence-level frequency summaries. [`paper/tables/table_17.csv`](paper/tables/table_17.csv) defines every column.

The frequency summaries in the public bundle use a shared Pythia-tokenizer/Pile frequency proxy. The exact historical token-inventory build was not retained. The manuscript describes model-specific tokenization; the repository therefore treats the bundled values as the authoritative downstream inputs without claiming a bit-identical from-text reconstruction.

Retained CoNLL-U headers identify UDPipe 2 and model `english-ewt-ud-2.17-251125`; the headers record that model as CC BY-NC-SA. The parser model and parsed text are not distributed. The exact Profiling-UD source revision was not retained.

## Geometry targets

The target tables contain:

- pointwise maximum-likelihood ID (`pointwise_mle`);
- expected simplex skewness (`pointwise_ess`); and
- the paper's pointwise/local pyFCI adaptation (`pointwise_fci_id`).

The full-pipeline FCI module explains where this local construction differs from the published global estimator. Read its module documentation before comparing a fresh run with another FCI implementation.

## What is not included

The repository does not include:

- raw corpus shards or prepared reference/test JSONL files (the aligned browser excerpts are the exception described below);
- hidden-state tensors, neighbour arrays, or model caches;
- parser weights, token-frequency inventories, or token caches;
- logs and manifests carrying local machine paths; or
- source-level identifiers from the upstream corpus.

The original archive included seven quotations in its Table 13 (Table 12 in the current manuscript). The interactive release additionally packages the aligned evaluation excerpts below. These texts remain third-party material; no rights in them are granted here.

## Additional experiment archives

The regular `data/paper/` directory also contains layer/k regression grids, grouped permutation importance, family ablations, neighbourhood diagnostics, all-layer Pythia-1.4B ID summaries, perplexity correlations, perplexity-only Ridge baselines, and source/TF-IDF incremental comparisons. Numeric per-query locality measurements are in `data/derived/neighbourhood_locality_metrics.parquet`. The source-control cohort IDs, source categories, predictions, fold scores, and tuning results are under `results/reference/source_tfidf_*`.

These files contain no excerpt text or representation arrays. `configs/experiment_results_manifest.json` records their schemas, sizes in rows, and content hashes, along with neutral logical IDs and hashes for the original source artifacts. These archived historical runs do not replace the pinned main-model bundle. See [experiment coverage and methods](paper/ARTIFACTS.md#geometry-and-control-experiments).

## Interactive excerpt release

`data/explorer/excerpts.json` contains the 1,994 evaluation excerpts with released linguistic profiles. Each record has `query_index`, `text`, `source` (the recorded Pile component), and `text_sha256`. The initial import matched the original evaluation text, source metadata, and numeric profile digest. Every subsequent site build verifies every UTF-8 text hash against `data/derived/features.parquet` before joining any geometry targets. The source corpus is The Pile; the release adds no license to its constituent texts.

`docs/assets/explorer.json` is the portable browser payload; `explorer-index.js` holds the text/profile index; model/layer geometry and locality files load progressively as described in [SITE.md](SITE.md). Feature vectors follow the order of its 46-entry feature inventory. Measurements are indexed by model, relative depth, and estimator; each pair contains `[measured_ID, percentile]`. Missing or non-positive unavailable estimates are represented as `[null, null]`, never as zero. The retained data contain one such observation: FCI, Pythia, early layer 2, query 502. Its percentile population is 1,993; all other settings have 1,994 available aligned estimates. Percentiles are average ranks divided by the number of available observations, multiplied by 100. Search and source filters do not recompute ranks.

The original geometry tables retain all 2,000 evaluation queries. Their aggregate statistics can therefore differ from aggregates calculated over the browser’s aligned subset. Raw numeric feature values are preserved, including missing values. Lexical density alone is stored as a 0–1 proportion; the browser multiplies it by 100 for display, while CSV/JSON exports preserve its stored value. The three frequency controls are the shared Pythia-1.4B-tokenizer proxies documented in the configuration.

`paper/current/manifest.json` and `docs/assets/results-data.js` identify the current manuscript snapshot. The current table CSVs are displayed-cell grids, preserving manuscript rounding. Original table TeX is included; the earlier tidy numeric files under `paper/tables/`, `data/paper/`, and `results/reference/` remain available. Figure captions are transcribed from the supplied manuscript; original source paths and hashes are recorded for provenance, including historical small-Pythia reference-size results. No original working-directory paths are needed to build or browse the release.

## Verified locality alignment for the browser

The locality archive’s `query_position` was checked against each original model/layer’s evaluation `query_source_index` and exact text hash before joining it to `query_index`. The 500-query audit has 498 aligned profiles. `data/explorer/neighbourhood_alignment.json` records the source hashes and verification counts across nine settings. The browser retains all 16 recorded distance/composition diagnostics, five k values, and both cumulative and shell rank intervals for those excerpts. These are query-neighbourhood summaries, not token scores. Full-precision numeric downloads and descriptions of their units are in [SITE.md](SITE.md).
