# Current manuscript results

Figures and tables from the current paper. [Earlier results and supporting analyses](../TABLES.md) are available separately.

## Tables

- **Table 1** — Spearman correlations between excerpt perplexity and ESS-estimated pointwise ID. [CSV](tables/perplexity-ess-correlations.csv)
- **Table 2** — ESS-estimated pointwise ID regression with linguistic features, ablations, and baselines. [CSV](tables/main-results.csv)
- **Table 3** — Most predictive features for ESS-estimated pointwise ID regression. [CSV](tables/top-features.csv)
- **Table 4** — Stable ALE directions for recurring predictors of ESS-estimated pointwise ID. [CSV](tables/feature-direction.csv)
- **Table 5** — ESS-estimated pointwise ID regression across seven Apertus checkpoints. [CSV](tables/apertus-checkpoint-ess-importance.csv)
- **Table 6** — Pointwise ID regression and feature-ablation controls for FCI and MLE. [CSV](tables/alternative-estimator-ablation.csv)
- **Table 7** — Most predictive features for FCI- and MLE-estimated pointwise ID regression. [CSV](tables/alternative-estimator-importance.csv)
- **Table 8** — Sensitivity of Profiling-UD regression to neighbourhood size and layer in Pythia and Qwen. [CSV](tables/k-layer-sensitivity.csv)
- **Table 9** — Stability of held-out permutation-importance rankings for ESS-estimated pointwise ID. [CSV](tables/importance-sensitivity.csv)
- **Table 10** — Pointwise ID distributions across the Pile evaluation splits for Pythia, using k=1000 and n_ref=15,000. [CSV](tables/pile-split-id-robustness.csv)
- **Table 11** — Most predictive features for random forest classification of the lowest and highest ESS-estimated pointwise ID quintiles. [CSV](tables/ess-classification-features.csv)
- **Table 12** — Representative excerpts illustrating the recurring feature directions identified by ALE. [CSV](tables/mann-whitney.csv)
- **Table 13** — Classification performance of Profiling-UD, matched lexical baselines, and log perplexity on main_set. [CSV](tables/lexical-classification.csv)
- **Table 14** — Regression performance of Profiling-UD, matched lexical baselines, and log perplexity on main_set. [CSV](tables/lexical-regression.csv)
- **Table 15** — ESS-estimated pointwise ID regression across five Pythia checkpoints. [CSV](tables/pythia-feature.csv)
- **Table 16** — Inventory of the 46 predictors used in the pointwise ID analyses. [CSV](tables/retained-profiling-ud-features.csv)

## Figures

- **Figure 1** — Study pipeline linking an excerpt's linguistic profile to the pointwise ID of its language-model representation. ID is estimated relative to a disjoint reference set and predicted from linguistic features. The illustration is schematic. [PNG](figures/pipeline.png) · [PDF](figures/pipeline.pdf)
- **Figure 2** — Mean ESS-estimated pointwise ID (±1σ, where σ is the standard deviation across excerpts) across approximately matched relative depths in Pythia, Qwen, and Apertus. [PNG](figures/ess-profile.png) · [PDF](figures/ess-profile.pdf)
- **Figure 3** — Sensitivity of ESS-estimated pointwise ID to reference-set size for Pythia at layer 16. Each curve shows the median estimate obtained with a different neighbourhood size k. [PNG](figures/reference-plateau.png) · [PDF](figures/reference-plateau.pdf)
- **Figure 4** — Stability of Pythia-6.9B ESS-estimated pointwise ID rankings under reference-set resampling at layer 16 and k=1000. At each reference-set size, points show the ten pairwise Spearman correlations between rankings obtained from five independently sampled reference subsets; the line shows their mean. [PNG](figures/ess-reference-stability.png) · [PDF](figures/ess-reference-stability.pdf)
- **Figure 5** — Median ID estimates from ESS, FCI, and MLE on a synthetic Gaussian cloud with true intrinsic dimension D=100 and n_ref=15,000, across neighbourhood sizes. The dashed horizontal line marks the true dimension. [PNG](figures/estimators.png) · [PDF](figures/estimators.pdf)
- **Figure 6** — Mean pointwise ID (±1σ, where σ is the standard deviation across excerpts) estimated with ESS, FCI, and MLE across approximately matched relative depths in Pythia, Qwen, and Apertus. [PNG](figures/scores-on-layers.png) · [PDF](figures/scores-on-layers.pdf)
- **Figure 7** — Mean ESS-estimated pointwise ID (±1σ, where σ is the standard deviation across excerpts) at early, intermediate, and late layers across Pythia and Apertus pretraining checkpoints. The x-axes report approximate cumulative training tokens (B: billion; T: trillion). Checkpoints are equally spaced within each model; the two training trajectories are not temporally aligned. [PNG](figures/ess-checkpoints.png) · [PDF](figures/ess-checkpoints.pdf)
