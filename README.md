# Linguistic Features of Local Geometry in Language Models

**Lucia Domenichelli · Iuri Macocco · Dominique Brunato · Felice Dell’Orletta · Marco Baroni**

Code, released measurements, paper results, and an interactive excerpt explorer for *Linguistic Features of Local Geometry in Language Models*.

The study asks how the linguistic form of an excerpt relates to the local intrinsic dimension of its language-model representation. It measures pointwise ID with ESS, MLE, and a local adaptation of FCI in Pythia-6.9B, Qwen2.5-7B, and Apertus-8B, and relates those measurements to 43 Profiling-UD descriptors and three recorded frequency controls. The current manuscript uses random forests for the prediction analyses.

## Explore the texts and results

The static site in [`docs/`](docs/) includes:

- **1,994 original evaluation excerpts**, each joined to its released feature vector by a verified text SHA-256;
- **46 features**, with definitions, units, and missing values preserved;
- **27 measured settings**: three models × three depths × three ID estimators;
- text and source filters, within-setting ID percentiles, two-excerpt comparisons, a selectable feature/ID scatterplot, CSV export, and shareable excerpt URLs;
- **all 7 figures and 16 tables from the current manuscript**, with full captions and downloadable PNG/PDF, CSV, and original table TeX;
- the earlier reproduction bundle and its additional geometry, neighbourhood, feature-family, source, lexical, and perplexity analyses.

To preview the committed site, Python’s standard library is enough:

```bash
make serve
# Open http://localhost:8765
```

The site works entirely in the browser. It displays saved measurements; it does not run a language model or predict ID for new text. Percentiles use all available aligned observations within each model/layer/estimator before filtering. The measured evaluation set has 2,000 queries; the browser includes the 1,994 with aligned linguistic profiles. One early-layer Pythia FCI measurement is unavailable and remains null.

GitHub Pages deployment is prepared in [`.github/workflows/pages.yml`](.github/workflows/pages.yml). See [PUBLISHING.md](PUBLISHING.md) for the repository name and activation steps. The local site is not evidence of an online deployment.

## Current paper and earlier reproduction bundle

Start with the [current manuscript result index](paper/current/README.md). [`paper/current/manifest.json`](paper/current/manifest.json) records the manuscript digest, captions, labels, table cells, figure sources, and content hashes. CSVs in that directory transcribe the displayed, rounded table cells. Their accompanying TeX preserves the exact table source, including formatting. They are not a new high-precision analysis run.

The material imported from `local-geometry-reproduction` is preserved in its original structure: [figures](paper/FIGURES.md), [tables](paper/TABLES.md), and [artifact map](paper/ARTIFACTS.md). Its six numbered figures and seventeen numbered tables have **their own earlier numbering**, plus additional experiment artifacts. This archive includes Ridge and logistic baselines, which are additional comparisons rather than methods claimed for the current manuscript. Original higher-precision CSVs and reference outputs are retained.

![Pointwise ID study pipeline](paper/current/figures/pipeline.png)

## Install and rebuild

Python 3.10+ and the pinned analysis requirements support the numeric checks, archived artifact build, and site-data build:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-analysis.txt
make PYTHON=.venv/bin/python paper
make PYTHON=.venv/bin/python site
make PYTHON=.venv/bin/python check
```

`make paper` rebuilds the **earlier reproducible artifact bundle** under `results/paper/`; it does not overwrite the current-manuscript snapshot. `make site` regenerates the explorer from the released Parquet tables and packaged excerpts, then checks all site downloads and both result manifests. It requires no original working directories or model weights. The committed static site can be served without installing analysis packages.

To refit the downstream models and compare against the earlier recorded reference results:

```bash
make PYTHON=.venv/bin/python analysis
make PYTHON=.venv/bin/python verify
# Also refit the alternative-estimator and additional ablation comparisons:
make PYTHON=.venv/bin/python analysis-extended
```

These commands retain the original archive’s Ridge/logistic comparisons alongside its forests. They take substantially longer than building the site. The [reproduction guide](REPRODUCIBILITY.md) distinguishes rebuilt artifacts, downstream refits, and fresh representation/ID computation.

## Data and interpretation

The main settings are `k=1000`, 15,000 disjoint reference excerpts, and early/intermediate/late layers 2/16/31 for Pythia and Apertus, and 2/14/27 for Qwen. Configurations, checkpoint revisions, feature definitions, and reconstruction boundaries are documented in [DATA.md](DATA.md), [configs/paper.yaml](configs/paper.yaml), and [configs/checkpoints.yaml](configs/checkpoints.yaml).

The three released frequency controls are **shared Pythia-tokenizer proxies**, not independently recomputed model-specific features. Lexical density is stored as a fraction and displayed as a percentage; the other percentage features retain their recorded scale. The explorer uses raw recorded feature values, with no imputation. Median imputation in prediction analyses remains local to the training fold. Associations do not establish causality, and pointwise ID is a property of a representation and its reference neighbourhood rather than an intrinsic linguistic-complexity score of a text.

The full pipeline in `src/full_pipeline/` requires separately acquired corpus data, model weights, parser resources, and substantial compute. Raw corpus shards, hidden states, neighbour arrays, and model caches are not included.

## Repository map

| Path | Contents |
|---|---|
| `docs/` | GitHub Pages site, browser data, and downloadable results |
| `paper/current/` | Current manuscript’s 7 figures and 16 table grids / TeX snippets |
| `paper/figures/`, `paper/tables/` | Original reproduction artifacts and additional analyses |
| `data/explorer/` | Verified excerpts and source categories for the interactive browser |
| `data/derived/` | Numeric feature, geometry, checkpoint, and neighbourhood tables |
| `data/paper/` | Archived numeric summaries for rebuilding artifacts |
| `results/reference/` | Recorded downstream outputs for reproduction checks |
| `scripts/`, `src/full_pipeline/` | Build, validation, analysis, and full-pipeline code |
| `configs/`, `tests/` | Experiment settings and integrity / regression checks |

No code license has been added. Third-party excerpts retain their source terms; see [DATA.md](DATA.md#interactive-excerpt-release). Citation metadata is in [CITATION.cff](CITATION.cff); no publication venue or DOI is asserted.
