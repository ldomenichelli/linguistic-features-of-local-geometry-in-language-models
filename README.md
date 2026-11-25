# Linguistic Features of Local Geometry in Language Models

**Lucia Domenichelli · Iuri Macocco · Dominique Brunato · Felice Dell’Orletta · Marco Baroni**

Code, released measurements, paper results, and an interactive excerpt explorer for *Linguistic Features of Local Geometry in Language Models*.

The study asks how the linguistic form of an excerpt relates to the local intrinsic dimension of its language-model representation. It measures pointwise ID with ESS, MLE, and a local adaptation of FCI in Pythia-6.9B, Qwen2.5-7B, and Apertus-8B, and relates those measurements to 43 Profiling-UD descriptors and three recorded frequency controls. The current manuscript uses random forests for the prediction analyses.

## Explore the texts and results

Browse 2,000 excerpts, compare results across language models, and download figures, tables, and data on the [project website](https://ldomenichelli.github.io/linguistic-features-of-local-geometry-in-language-models/).

## Paper results

Find the [current figures and tables](paper/current/README.md) and [earlier supporting analyses](paper/README.md). The included PDF is an earlier version of the paper.

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

`make paper` rebuilds the **earlier reproducible artifact bundle** under `results/paper/`; it does not overwrite the current-manuscript snapshot. `make site` regenerates the explorer from the released Parquet tables and packaged excerpts, then checks all site downloads and both result manifests. It requires no original working directories or model weights. The static HTML/JS can be served without analysis packages. Run `make site` once to prepare the PDF, numeric result downloads, and repository source browser before sharing the complete site.

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
| `paper/current/` | Current manuscript’s 7 figures and 16 CSV table grids |
| `paper/figures/`, `paper/tables/` | Original reproduction artifacts and additional analyses |
| `data/explorer/` | Verified excerpts and source categories for the interactive browser |
| `data/derived/` | Numeric feature, geometry, checkpoint, and neighbourhood tables |
| `data/paper/` | Archived numeric summaries for rebuilding artifacts |
| `results/reference/` | Recorded downstream outputs for reproduction checks |
| `scripts/`, `src/full_pipeline/` | Build, validation, analysis, and full-pipeline code |
| `configs/`, `tests/` | Experiment settings and integrity / regression checks |

The browser code is in `docs/`; [SITE.md](SITE.md) documents the website build and updates. No code license has been added. Third-party excerpts retain their source terms; see [DATA.md](DATA.md#interactive-excerpt-release). Citation metadata is in [CITATION.cff](CITATION.cff); no publication venue or DOI is asserted.
