# Tables

These are the machine-readable values displayed in the paper. Decimal places follow the available archived outputs; the manuscript may show fewer digits.

## Table 1

Spearman correlations between excerpt perplexity and ESS pointwise ID. All nine correlations have p < 0.05.

[Download the CSV](tables/table_01.csv)

| Model | Depth | Layer | Spearman rho | Spearman p | N |
| --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | Early | 2 | 0.0880112 | 8.10849e-05 | 2000 |
| Pythia-6.9B | Intermediate | 16 | 0.373436 | 3.28909e-67 | 2000 |
| Pythia-6.9B | Late | 31 | 0.298728 | 1.6571e-42 | 2000 |
| Qwen2.5-7B | Early | 2 | 0.0947862 | 2.17736e-05 | 2000 |
| Qwen2.5-7B | Intermediate | 14 | 0.489602 | 4.56102e-121 | 2000 |
| Qwen2.5-7B | Late | 27 | 0.347562 | 7.12612e-58 | 2000 |
| Apertus-8B | Early | 2 | -0.0968356 | 1.43714e-05 | 2000 |
| Apertus-8B | Intermediate | 16 | 0.158515 | 1.00598e-12 | 2000 |
| Apertus-8B | Late | 31 | 0.12394 | 2.68625e-08 | 2000 |

## Table 2

ESS pointwise-ID regression and feature ablations. Values are mean five-fold cross-validated R² for random forest and Ridge; no-frequency removes three frequency summaries and no-raw removes four surface descriptors.

[Download the CSV](tables/table_02.csv)

| Model | Layer | Full RF R² | Full ridge R² | No frequency RF R² | No frequency ridge R² | No raw RF R² | No raw ridge R² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | 2 | 0.256 | 0.172 | 0.254 | 0.168 | 0.215 | 0.109 |
| Pythia-6.9B | 16 | 0.505 | 0.37 | 0.504 | 0.37 | 0.476 | 0.351 |
| Pythia-6.9B | 31 | 0.263 | 0.154 | 0.262 | 0.156 | 0.257 | 0.154 |
| Qwen2.5-7B | 2 | 0.246 | 0.184 | 0.244 | 0.174 | 0.199 | 0.11 |
| Qwen2.5-7B | 14 | 0.547 | 0.455 | 0.547 | 0.455 | 0.527 | 0.433 |
| Qwen2.5-7B | 27 | 0.432 | 0.25 | 0.43 | 0.246 | 0.419 | 0.244 |
| Apertus-8B | 2 | 0.27 | 0.2 | 0.271 | 0.194 | 0.206 | 0.092 |
| Apertus-8B | 16 | 0.439 | 0.352 | 0.439 | 0.348 | 0.416 | 0.332 |
| Apertus-8B | 31 | 0.311 | 0.175 | 0.307 | 0.17 | 0.291 | 0.162 |

## Table 3

Five largest ESS random-forest permutation importances. Importance is the mean decrease in held-out R² over eight shuffles and five folds.

[Download the CSV](tables/table_03.csv)

| Model | Layer | Five largest held-out importances |
| --- | --- | --- |
| Pythia-6.9B | 2 | n_tokens (0.1594); upos_PROPN (0.0410); upos_PUNCT (0.0333); dep_nsubj (0.0204); char_per_tok (0.0180) |
| Pythia-6.9B | 16 | upos_NOUN (0.1488); char_per_tok (0.0907); upos_PRON (0.0744); upos_PROPN (0.0673); verbal_root (0.0445) |
| Pythia-6.9B | 31 | upos_NOUN (0.0747); upos_PROPN (0.0606); verbal_root (0.0399); upos_PRON (0.0316); dep_nsubj (0.0196) |
| Qwen2.5-7B | 2 | n_tokens (0.1625); verbal_root (0.0418); upos_PUNCT (0.0331); char_per_tok (0.0186); upos_NUM (0.0150) |
| Qwen2.5-7B | 14 | char_per_tok (0.1360); upos_PRON (0.1074); dep_nsubj (0.0532); upos_PROPN (0.0426); upos_NOUN (0.0303) |
| Qwen2.5-7B | 27 | verbal_root (0.1327); upos_NOUN (0.1254); upos_PROPN (0.1227); dep_nsubj (0.0287); char_per_tok (0.0273) |
| Apertus-8B | 2 | n_tokens (0.1989); verbal_root (0.0324); n_sentences (0.0192); upos_PUNCT (0.0116); char_per_tok (0.0098) |
| Apertus-8B | 16 | upos_NOUN (0.1367); dep_nsubj (0.0541); char_per_tok (0.0385); upos_PROPN (0.0369); verbal_root (0.0321) |
| Apertus-8B | 31 | upos_PROPN (0.1481); dep_nsubj (0.0549); n_tokens (0.0400); verbal_root (0.0339); upos_PRON (0.0255) |

## Table 4

Depth-specific cross-fitted ALE effects for recurring ESS predictors. Directions count models with a stable sign; contrasts are median 10th-to-90th-percentile effects in target-SD units.

[Download the CSV](tables/table_04.csv)

| Feature | Early direction | Early models | Early median d10 90 | Middle direction | Middle models | Middle median d10 90 | Late direction | Late models | Late median d10 90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| upos_PROPN | increasing | 1/3 | 0.176 | increasing | 3/3 | 0.133 | increasing | 3/3 | 0.307 |
| char_per_tok | mixed: 2 increasing / 1 decreasing | 3/3 | 0.075 | decreasing | 3/3 | -0.422 | decreasing | 1/3 | -0.12 |
| upos_NOUN | not selected | 0/3 | — | decreasing | 3/3 | -0.491 | decreasing | 2/3 | -0.367 |
| dep_nsubj | increasing | 1/3 | 0.178 | increasing | 2/3 | 0.327 | increasing | 3/3 | 0.126 |
| verbal_root | increasing | 2/3 | 0.192 | increasing | 2/3 | 0.114 | increasing | 3/3 | 0.129 |
| n_tokens | increasing | 3/3 | 0.454 | not selected | 0/3 | — | increasing | 1/3 | 0.147 |
| upos_PRON | not selected | 0/3 | — | increasing | 2/3 | 0.305 | increasing | 2/3 | 0.119 |

## Table 5

ESS random-forest regression across seven Apertus checkpoints. Scores are mean five-fold R²; importance is the mean held-out R² decrease over eight shuffles and five folds.

[Download the CSV](tables/table_05.csv)

| Checkpoint | Layer | R² | Five largest held-out importances |
| --- | --- | --- | --- |
| 210B | 2 | 0.417349 | n_tokens (0.2550); n_sentences (0.1134); char_per_tok (0.0256); dep_nsubj (0.0226); upos_PUNCT (0.0184) |
| 210B | 16 | 0.446365 | upos_NOUN (0.1290); upos_PROPN (0.0905); char_per_tok (0.0503); verbal_root (0.0469); upos_PRON (0.0462) |
| 210B | 31 | 0.361506 | upos_PROPN (0.1736); dep_nsubj (0.0586); verbal_root (0.0585); upos_PRON (0.0397); upos_NOUN (0.0217) |
| 420B | 2 | 0.251527 | n_tokens (0.1875); n_sentences (0.0433); upos_PUNCT (0.0328); lexical_density (0.0077); char_per_tok (0.0075) |
| 420B | 16 | 0.431042 | upos_NOUN (0.1116); upos_PROPN (0.0709); verbal_root (0.0538); char_per_tok (0.0407); dep_nsubj (0.0390) |
| 420B | 31 | 0.346489 | upos_PROPN (0.1830); verbal_root (0.0660); dep_nsubj (0.0500); n_tokens (0.0267); char_per_tok (0.0229) |
| 840B | 2 | 0.27373 | n_tokens (0.2114); upos_PUNCT (0.0432); n_sentences (0.0357); char_per_tok (0.0140); upos_PRON (0.0104) |
| 840B | 16 | 0.408493 | upos_NOUN (0.1193); upos_PROPN (0.0664); verbal_root (0.0425); dep_nsubj (0.0421); char_per_tok (0.0381) |
| 840B | 31 | 0.314598 | upos_PROPN (0.1711); verbal_root (0.0462); dep_nsubj (0.0344); n_tokens (0.0311); upos_PRON (0.0288) |
| 1.68T | 2 | 0.358626 | n_sentences (0.1408); n_tokens (0.1251); dep_nsubj (0.0288); char_per_tok (0.0245); upos_PUNCT (0.0173) |
| 1.68T | 16 | 0.427531 | upos_NOUN (0.1179); upos_PROPN (0.0708); verbal_root (0.0574); char_per_tok (0.0458); upos_PRON (0.0449) |
| 1.68T | 31 | 0.348945 | upos_PROPN (0.1692); verbal_root (0.0623); dep_nsubj (0.0553); upos_PRON (0.0315); char_per_tok (0.0278) |
| 3.57T | 2 | 0.35727 | n_tokens (0.2196); n_sentences (0.0516); dep_nsubj (0.0234); upos_PUNCT (0.0195); char_per_tok (0.0180) |
| 3.57T | 16 | 0.440554 | upos_NOUN (0.1451); upos_PROPN (0.0654); verbal_root (0.0498); upos_PRON (0.0393); dep_nsubj (0.0349) |
| 3.57T | 31 | 0.354054 | upos_PROPN (0.1760); verbal_root (0.0580); dep_nsubj (0.0438); upos_NOUN (0.0295); n_tokens (0.0243) |
| 7.232T | 2 | 0.284768 | n_tokens (0.1914); upos_PUNCT (0.0252); n_sentences (0.0236); dep_nsubj (0.0149); upos_NOUN (0.0104) |
| 7.232T | 16 | 0.43639 | upos_NOUN (0.1392); verbal_root (0.0749); upos_PROPN (0.0523); dep_nsubj (0.0332); char_per_tok (0.0319) |
| 7.232T | 31 | 0.339313 | upos_PROPN (0.1340); verbal_root (0.0612); dep_nsubj (0.0559); upos_NOUN (0.0331); n_tokens (0.0285) |
| 15T | 2 | 0.269622 | n_tokens (0.1989); verbal_root (0.0324); n_sentences (0.0192); upos_PUNCT (0.0116); char_per_tok (0.0098) |
| 15T | 16 | 0.438959 | upos_NOUN (0.1367); dep_nsubj (0.0541); char_per_tok (0.0385); upos_PROPN (0.0369); verbal_root (0.0321) |
| 15T | 31 | 0.310956 | upos_PROPN (0.1481); dep_nsubj (0.0549); n_tokens (0.0400); verbal_root (0.0339); upos_PRON (0.0255) |

## Table 6

MLE and FCI pointwise-ID regression and feature ablations. Values are mean five-fold cross-validated R² for random forest and Ridge.

[Download the CSV](tables/table_06.csv)

| Estimator | Model | Layer | Full RF R² | Full ridge R² | No frequency RF R² | No frequency ridge R² | No raw RF R² | No raw ridge R² |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FCI | Pythia-6.9B | 2 | 0.259 | 0.16 | 0.257 | 0.16 | 0.213 | 0.11 |
| FCI | Pythia-6.9B | 16 | 0.424 | 0.297 | 0.423 | 0.298 | 0.396 | 0.28 |
| FCI | Pythia-6.9B | 31 | 0.208 | 0.104 | 0.207 | 0.105 | 0.201 | 0.104 |
| FCI | Qwen2.5-7B | 2 | 0.204 | 0.156 | 0.203 | 0.148 | 0.168 | 0.097 |
| FCI | Qwen2.5-7B | 14 | 0.482 | 0.414 | 0.481 | 0.412 | 0.464 | 0.391 |
| FCI | Qwen2.5-7B | 27 | 0.359 | 0.204 | 0.358 | 0.2 | 0.344 | 0.198 |
| FCI | Apertus-8B | 2 | 0.253 | 0.183 | 0.253 | 0.178 | 0.194 | 0.083 |
| FCI | Apertus-8B | 16 | 0.421 | 0.334 | 0.421 | 0.327 | 0.404 | 0.315 |
| FCI | Apertus-8B | 31 | 0.286 | 0.162 | 0.284 | 0.155 | 0.266 | 0.154 |
| MLE | Pythia-6.9B | 2 | 0.127 | 0.093 | 0.128 | 0.094 | 0.122 | 0.086 |
| MLE | Pythia-6.9B | 16 | 0.259 | 0.195 | 0.26 | 0.196 | 0.224 | 0.182 |
| MLE | Pythia-6.9B | 31 | 0.213 | 0.073 | 0.212 | 0.066 | 0.194 | 0.063 |
| MLE | Qwen2.5-7B | 2 | 0.049 | 0.022 | 0.049 | 0.015 | 0.033 | 0.022 |
| MLE | Qwen2.5-7B | 14 | 0.239 | 0.154 | 0.239 | 0.159 | 0.228 | 0.151 |
| MLE | Qwen2.5-7B | 27 | 0.159 | 0.079 | 0.153 | 0.07 | 0.144 | 0.071 |
| MLE | Apertus-8B | 2 | 0.079 | 0.075 | 0.08 | 0.078 | 0.062 | 0.058 |
| MLE | Apertus-8B | 16 | 0.268 | 0.184 | 0.267 | 0.181 | 0.247 | 0.166 |
| MLE | Apertus-8B | 31 | 0.101 | 0.072 | 0.097 | 0.066 | 0.088 | 0.072 |

## Table 7

Five largest held-out random-forest permutation importances for MLE and FCI, averaged over eight shuffles and five folds.

[Download the CSV](tables/table_07.csv)

| Estimator | Model | Layer | Five largest held-out importances |
| --- | --- | --- | --- |
| FCI | Pythia-6.9B | 2 | n_tokens (0.1283); upos_PROPN (0.0750); dep_nsubj (0.0239); char_per_tok (0.0201); upos_PRON (0.0171) |
| FCI | Pythia-6.9B | 16 | upos_NOUN (0.1431); char_per_tok (0.0791); upos_PROPN (0.0656); verbal_root (0.0420); upos_PRON (0.0348) |
| FCI | Pythia-6.9B | 31 | upos_PROPN (0.0928); upos_NOUN (0.0713); verbal_root (0.0339); upos_PRON (0.0219); upos_ADV (0.0175) |
| FCI | Qwen2.5-7B | 2 | n_tokens (0.1283); verbal_root (0.0533); upos_PUNCT (0.0188); char_per_tok (0.0180); upos_NUM (0.0151) |
| FCI | Qwen2.5-7B | 14 | char_per_tok (0.1520); upos_PRON (0.0648); upos_PROPN (0.0583); dep_nsubj (0.0465); upos_NOUN (0.0351) |
| FCI | Qwen2.5-7B | 27 | upos_PROPN (0.1543); verbal_root (0.1391); upos_NOUN (0.0620); char_per_tok (0.0307); upos_ADJ (0.0145) |
| FCI | Apertus-8B | 2 | n_tokens (0.2146); verbal_root (0.0318); n_sentences (0.0116); upos_PUNCT (0.0101); char_per_tok (0.0083) |
| FCI | Apertus-8B | 16 | upos_NOUN (0.1130); upos_PROPN (0.0469); verbal_root (0.0440); dep_nsubj (0.0413); char_per_tok (0.0405) |
| FCI | Apertus-8B | 31 | upos_PROPN (0.1876); dep_nsubj (0.0510); verbal_root (0.0342); n_tokens (0.0330); upos_PRON (0.0298) |
| MLE | Pythia-6.9B | 2 | upos_PROPN (0.0906); upos_PUNCT (0.0402); upos_NOUN (0.0262); dep_nsubj (0.0219); upos_NUM (0.0173) |
| MLE | Pythia-6.9B | 16 | upos_NOUN (0.0833); subj_pre (0.0700); char_per_tok (0.0577); upos_PROPN (0.0225); dep_nsubj (0.0144) |
| MLE | Pythia-6.9B | 31 | upos_PROPN (0.0786); char_per_tok (0.0431); dep_nsubj (0.0334); upos_ADJ (0.0248); verbal_root (0.0247) |
| MLE | Qwen2.5-7B | 2 | n_tokens (0.0410); upos_PROPN (0.0271); verbal_root (0.0215); char_per_tok (0.0186); upos_ADJ (0.0108) |
| MLE | Qwen2.5-7B | 14 | char_per_tok (0.0915); dep_nsubj (0.0383); upos_PROPN (0.0292); dep_compound (0.0205); upos_NOUN (0.0175) |
| MLE | Qwen2.5-7B | 27 | upos_PROPN (0.1274); char_per_tok (0.0343); dep_nsubj (0.0243); verbal_root (0.0180); upos_PRON (0.0166) |
| MLE | Apertus-8B | 2 | n_tokens (0.0860); upos_PROPN (0.0656); upos_NOUN (0.0385); upos_PUNCT (0.0201); upos_NUM (0.0168) |
| MLE | Apertus-8B | 16 | upos_NOUN (0.0482); char_per_tok (0.0432); dep_nsubj (0.0326); upos_PROPN (0.0248); n_tokens (0.0211) |
| MLE | Apertus-8B | 31 | upos_PROPN (0.1244); char_per_tok (0.0316); dep_nsubj (0.0265); median_frequency_class (0.0212); n_tokens (0.0195) |

## Table 8

Neighbourhood- and adjacent-layer sensitivity for Pythia and Qwen. Values are mean five-fold random-forest R² using the same 46 predictors; the separate k = 1000 ESS results appear in Table 2.

[Download the CSV](tables/table_08.csv)

| Model | Target | Layer | K 10 | K 100 | K 500 | K 2000 | K 3000 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | ESS | 1 | 0.142391 | 0.184906 | 0.200416 | 0.258182 | 0.299172 |
| Pythia-6.9B | ESS | 2 | 0.16666 | 0.183582 | 0.203745 | 0.374432 | 0.490582 |
| Pythia-6.9B | ESS | 16 | 0.171278 | 0.327198 | 0.457416 | 0.506708 | 0.515455 |
| Pythia-6.9B | ESS | 17 | 0.159001 | 0.312183 | 0.438301 | 0.502413 | 0.49746 |
| Pythia-6.9B | ESS | 31 | 0.0760489 | 0.110913 | 0.230361 | 0.248211 | 0.243579 |
| Pythia-6.9B | ESS | 32 | 0.0969853 | 0.233827 | 0.351232 | 0.456491 | 0.506163 |
| Pythia-6.9B | FCI | 1 | 0.0556729 | 0.178768 | 0.183649 | 0.235419 | 0.346988 |
| Pythia-6.9B | FCI | 2 | 0.0594382 | 0.163461 | 0.182672 | 0.381437 | 0.494763 |
| Pythia-6.9B | FCI | 16 | 0.0678856 | 0.298903 | 0.396712 | 0.41657 | 0.433977 |
| Pythia-6.9B | FCI | 17 | 0.0637037 | 0.294824 | 0.395231 | 0.390121 | 0.421269 |
| Pythia-6.9B | FCI | 31 | 0.0171932 | 0.0430123 | 0.197554 | 0.214123 | 0.245301 |
| Pythia-6.9B | FCI | 32 | 0.0361238 | 0.204966 | 0.334058 | 0.455178 | 0.503216 |
| Pythia-6.9B | MLE | 1 | 0.0237507 | 0.0866581 | 0.0623959 | 0.0689835 | 0.0711085 |
| Pythia-6.9B | MLE | 2 | 0.0223926 | 0.0709007 | 0.0986539 | 0.147641 | 0.146919 |
| Pythia-6.9B | MLE | 16 | 0.0578521 | 0.168313 | 0.246845 | 0.267795 | 0.265433 |
| Pythia-6.9B | MLE | 17 | 0.054739 | 0.164924 | 0.238988 | 0.254219 | 0.255055 |
| Pythia-6.9B | MLE | 31 | -0.00294844 | 0.0881715 | 0.194874 | 0.205096 | 0.176327 |
| Pythia-6.9B | MLE | 32 | 0.000134306 | 0.0506947 | 0.136185 | 0.230461 | 0.229161 |
| Qwen2.5-7B | ESS | 1 | 0.111673 | 0.150241 | 0.145886 | 0.164958 | 0.172648 |
| Qwen2.5-7B | ESS | 2 | 0.123876 | 0.218847 | 0.209854 | 0.322851 | 0.399057 |
| Qwen2.5-7B | ESS | 14 | 0.172655 | 0.324537 | 0.451361 | 0.582263 | 0.609049 |
| Qwen2.5-7B | ESS | 15 | 0.177668 | 0.322236 | 0.426215 | 0.572921 | 0.611731 |
| Qwen2.5-7B | ESS | 27 | 0.135551 | 0.248826 | 0.395755 | 0.470323 | 0.522867 |
| Qwen2.5-7B | ESS | 28 | 0.0727174 | 0.1599 | 0.199556 | 0.378088 | 0.409684 |
| Qwen2.5-7B | FCI | 1 | 0.0187126 | 0.142392 | 0.129251 | 0.179206 | 0.192262 |
| Qwen2.5-7B | FCI | 2 | 0.0091417 | 0.189396 | 0.176245 | 0.319845 | 0.364726 |
| Qwen2.5-7B | FCI | 14 | 0.0652527 | 0.29387 | 0.407286 | 0.495643 | 0.510134 |
| Qwen2.5-7B | FCI | 15 | 0.074857 | 0.291229 | 0.388553 | 0.482923 | 0.473706 |
| Qwen2.5-7B | FCI | 27 | 0.0481223 | 0.201689 | 0.314014 | 0.407078 | 0.435334 |
| Qwen2.5-7B | FCI | 28 | 0.00211169 | 0.137493 | 0.180167 | 0.359066 | 0.383003 |
| Qwen2.5-7B | MLE | 1 | 0.0207663 | 0.070068 | 0.0306018 | -0.00187518 | -0.00507853 |
| Qwen2.5-7B | MLE | 2 | 0.0357874 | 0.0932756 | 0.0506518 | 0.0584189 | 0.0681558 |
| Qwen2.5-7B | MLE | 14 | 0.05589 | 0.187804 | 0.228069 | 0.27076 | 0.292249 |
| Qwen2.5-7B | MLE | 15 | 0.0704857 | 0.165211 | 0.221598 | 0.258465 | 0.275663 |
| Qwen2.5-7B | MLE | 27 | 0.00882643 | 0.0859525 | 0.133298 | 0.178082 | 0.163737 |
| Qwen2.5-7B | MLE | 28 | -0.0108509 | 0.0481528 | 0.127528 | 0.270171 | 0.282346 |

## Table 9

Stability of held-out ESS importance rankings. Recurrence counts top-five appearances across five alternative k values; overlap columns report median top-five intersections.

[Download the CSV](tables/table_09.csv)

| Model | Depth | Main layer | Adjacent layer | Main top three | Main feature recurrence | Median k overlap | Adjacent overlap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | Early | 2 | 1 | n_tokens (0.159); upos_PROPN (0.041); upos_PUNCT (0.033) | n_tokens (5/5); upos_PROPN (5/5); upos_PUNCT (3/5) | 3/5 | 4/5 |
| Pythia-6.9B | Middle | 16 | 17 | upos_NOUN (0.149); char_per_tok (0.091); upos_PRON (0.074) | upos_NOUN (5/5); char_per_tok (4/5); upos_PRON (5/5) | 4/5 | 5/5 |
| Pythia-6.9B | Late | 31 | 32 | upos_NOUN (0.075); upos_PROPN (0.061); verbal_root (0.040) | upos_NOUN (5/5); upos_PROPN (3/5); verbal_root (2/5) | 3/5 | 3/5 |
| Qwen2.5-7B | Early | 2 | 1 | n_tokens (0.163); verbal_root (0.042); upos_PUNCT (0.033) | n_tokens (5/5); verbal_root (3/5); upos_PUNCT (3/5) | 3/5 | 3/5 |
| Qwen2.5-7B | Middle | 14 | 15 | char_per_tok (0.136); upos_PRON (0.107); dep_nsubj (0.053) | char_per_tok (4/5); upos_PRON (5/5); dep_nsubj (3/5) | 4/5 | 5/5 |
| Qwen2.5-7B | Late | 27 | 28 | verbal_root (0.133); upos_NOUN (0.125); upos_PROPN (0.123) | verbal_root (4/5); upos_NOUN (5/5); upos_PROPN (3/5) | 4/5 | 3/5 |

## Table 10

Pythia pointwise-ID distributions in the main and extra Pile evaluation splits at k = 1000 and reference size 15,000. The final column is the absolute pooled-SD standardized mean difference.

[Download the CSV](tables/table_10.csv)

| Layer | Estimator | Main mean | Main SD | Extra mean | Extra SD | Absolute standardized mean difference |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | ESS | 38.3 | 12.61 | 38.25 | 12.72 | 0.004 |
| 2 | FCI | 40.6 | 13.27 | 40.25 | 13.43 | 0.026 |
| 2 | MLE | 17.46 | 7 | 17.12 | 7.11 | 0.049 |
| 16 | ESS | 108.11 | 42.84 | 107.75 | 42.66 | 0.008 |
| 16 | FCI | 135.29 | 60.21 | 134.99 | 59.7 | 0.005 |
| 16 | MLE | 27.41 | 14.7 | 27.22 | 14.29 | 0.014 |
| 31 | ESS | 77.06 | 23.8 | 76.82 | 23.65 | 0.01 |
| 31 | FCI | 97.27 | 30.64 | 97.2 | 30.64 | 0.002 |
| 31 | MLE | 21.29 | 7.61 | 21.23 | 7.82 | 0.007 |

## Table 11

Classification of the lowest and highest ESS quintiles. Values are mean five-fold ROC-AUC and fold SD for random forest and logistic regression.

[Download the CSV](tables/table_11.csv)

| Model | Layer | RF roc auc mean | RF roc auc fold SD | Logistic roc auc mean | Logistic roc auc fold SD |
| --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | 2 | 0.892 | 0.027 | 0.834 | 0.026 |
| Pythia-6.9B | 16 | 0.958 | 0.006 | 0.942 | 0.004 |
| Pythia-6.9B | 31 | 0.848 | 0.038 | 0.782 | 0.032 |
| Qwen2.5-7B | 2 | 0.844 | 0.017 | 0.803 | 0.038 |
| Qwen2.5-7B | 14 | 0.976 | 0.009 | 0.97 | 0.005 |
| Qwen2.5-7B | 27 | 0.931 | 0.015 | 0.885 | 0.02 |
| Apertus-8B | 2 | 0.874 | 0.025 | 0.827 | 0.042 |
| Apertus-8B | 16 | 0.955 | 0.009 | 0.936 | 0.009 |
| Apertus-8B | 31 | 0.885 | 0.018 | 0.817 | 0.034 |

## Table 12

Five largest random-forest permutation importances for low/high ESS classification. Importance is the mean held-out ROC-AUC decrease over eight shuffles and five folds.

[Download the CSV](tables/table_12.csv)

| Model | Layer | Five largest held-out importances |
| --- | --- | --- |
| Pythia-6.9B | 2 | n_tokens (0.0703); upos_PROPN (0.0152); dep_nsubj (0.0152); upos_PART (0.0123); upos_PRON (0.0088) |
| Pythia-6.9B | 16 | char_per_tok (0.0189); upos_NOUN (0.0148); upos_PROPN (0.0092); upos_PRON (0.0047); dep_nsubj (0.0040) |
| Pythia-6.9B | 31 | upos_PROPN (0.0236); upos_NOUN (0.0146); upos_PRON (0.0136); upos_ADV (0.0113); dep_nsubj (0.0051) |
| Qwen2.5-7B | 2 | n_tokens (0.0541); upos_PUNCT (0.0118); n_sentences (0.0113); verbal_root (0.0098); char_per_tok (0.0052) |
| Qwen2.5-7B | 14 | char_per_tok (0.0182); upos_PRON (0.0146); dep_nsubj (0.0063); upos_NOUN (0.0057); dep_obj (0.0020) |
| Qwen2.5-7B | 27 | verbal_root (0.0662); upos_PROPN (0.0348); upos_NOUN (0.0277); char_per_tok (0.0138); dep_nsubj (0.0044) |
| Apertus-8B | 2 | n_tokens (0.0434); n_sentences (0.0288); verbal_root (0.0089); char_per_tok (0.0075); upos_NOUN (0.0069) |
| Apertus-8B | 16 | upos_NOUN (0.0182); char_per_tok (0.0132); dep_nsubj (0.0112); upos_PRON (0.0088); n_tokens (0.0059) |
| Apertus-8B | 31 | upos_PROPN (0.0506); upos_NOUN (0.0170); dep_nsubj (0.0164); n_tokens (0.0132); verbal_root (0.0062) |

## Table 13

Representative excerpts for recurring ALE directions. Examples illustrate associations and do not isolate a feature from correlated properties.

[Download the CSV](tables/table_13.csv)

| Query index | Feature | Association | Feature value | ESS id | Representative excerpt |
| --- | --- | --- | --- | --- | --- |
| 1140 | upos_PROPN | high to high ID | 19.5% | 179.52 | Any piece about New York City has a heavyweight champion to contend with—E.B. White’s Here Is New York—but André Aciman’s Shadow Cities comes out swinging. |
| 723 | char_per_tok | high to low ID | 9.75 | 43.78 | Plasma levels of trimethoprim and sulfonamide after administration of trimethoprim-sulfamethoxazole and administration of trimethoprim-sulfamethoxazole and trimethoprim-sulfamoxole. |
| 1189 | upos_NOUN | high to low ID | 48.0% | 50.74 | Determination of tricarboxylic acid cycle acids and other related substances in cultured mammalian cells by gradient ion-exchange chromatography with suppressed conductivity detection. |
| 630 | dep_nsubj | high to high ID | 14.3% | 209.19 | Mine, too, I’ve felt that there is more to the Yithians than most other mythos races... they’re not just purely malicious or uncaring as so many seem to be. |
| 154 | verbal_root | high to high ID | 100% | 186.82 | When I heard that Children Of Bodom was putting out a new record, I was both excited and hesitant at the same time. |
| 1777 | n_tokens | high to high ID | 98 | 195.39 | We hear it from you all the time and we feel it too: community is what we do best. We bring together a diverse group of creative people who are living lives they love and YOU are part of that. You connect, share, motivate, and inspire each other. You are movers & shakers. You are the ones who burn the midnight oil and wake up at the crack of dawn. You save your money to invest in your future. You load up trucks and package delicate things. |
| 722 | upos_PRON | high to high ID | 16.7% | 198.89 | In other news: I’ve re-discovered my love for Bismuth. |

> Table 13 contains short third-party corpus excerpts reproduced for scholarly context. No rights in those excerpts are granted by this repository.

## Table 14

Classification performance of Profiling-UD and matched 46-term lexical baselines. Values are mean five-fold ROC-AUC for distinguishing the bottom and top 20% of each pointwise-ID distribution.

[Download the CSV](tables/table_14.csv)

| Model | Target | Layer | Profiling ud RF roc auc | Frequent logistic roc auc | Frequent RF roc auc | Band logistic roc auc | Band RF roc auc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | ESS | 2 | 0.892232 | 0.815376 | 0.822095 | 0.753605 | 0.746973 |
| Pythia-6.9B | ESS | 16 | 0.957925 | 0.908819 | 0.911076 | 0.859769 | 0.854879 |
| Pythia-6.9B | ESS | 31 | 0.847735 | 0.762111 | 0.767513 | 0.744512 | 0.730188 |
| Pythia-6.9B | FCI | 2 | 0.881458 | 0.811573 | 0.82443 | 0.767892 | 0.753689 |
| Pythia-6.9B | FCI | 16 | 0.950252 | 0.875899 | 0.880065 | 0.819515 | 0.801214 |
| Pythia-6.9B | FCI | 31 | 0.79967 | 0.687823 | 0.686006 | 0.713875 | 0.679581 |
| Pythia-6.9B | MLE | 2 | 0.847954 | 0.73589 | 0.749114 | 0.748518 | 0.74531 |
| Pythia-6.9B | MLE | 16 | 0.899757 | 0.777263 | 0.794195 | 0.73147 | 0.723373 |
| Pythia-6.9B | MLE | 31 | 0.837877 | 0.737923 | 0.788013 | 0.72619 | 0.718234 |
| Qwen2.5-7B | ESS | 2 | 0.844145 | 0.757847 | 0.75421 | 0.628583 | 0.608553 |
| Qwen2.5-7B | ESS | 14 | 0.976233 | 0.933598 | 0.926347 | 0.87308 | 0.865358 |
| Qwen2.5-7B | ESS | 27 | 0.930998 | 0.833024 | 0.830775 | 0.765836 | 0.764149 |
| Qwen2.5-7B | FCI | 2 | 0.823532 | 0.73558 | 0.736547 | 0.640538 | 0.655139 |
| Qwen2.5-7B | FCI | 14 | 0.965703 | 0.919165 | 0.908551 | 0.865384 | 0.866615 |
| Qwen2.5-7B | FCI | 27 | 0.924974 | 0.816727 | 0.819752 | 0.731479 | 0.705079 |
| Qwen2.5-7B | MLE | 2 | 0.762052 | 0.656504 | 0.655811 | 0.616642 | 0.621815 |
| Qwen2.5-7B | MLE | 14 | 0.876662 | 0.784799 | 0.798212 | 0.757447 | 0.741468 |
| Qwen2.5-7B | MLE | 27 | 0.860032 | 0.744376 | 0.782448 | 0.755419 | 0.743047 |
| Apertus-8B | ESS | 2 | 0.873815 | 0.787951 | 0.808185 | 0.662011 | 0.660824 |
| Apertus-8B | ESS | 16 | 0.954977 | 0.898092 | 0.902104 | 0.827533 | 0.815709 |
| Apertus-8B | ESS | 31 | 0.885486 | 0.795046 | 0.784487 | 0.746147 | 0.751509 |
| Apertus-8B | FCI | 2 | 0.865862 | 0.767065 | 0.794423 | 0.66972 | 0.666278 |
| Apertus-8B | FCI | 16 | 0.924425 | 0.865136 | 0.877806 | 0.791466 | 0.772343 |
| Apertus-8B | FCI | 31 | 0.871087 | 0.743476 | 0.752917 | 0.723527 | 0.725415 |
| Apertus-8B | MLE | 2 | 0.848678 | 0.633595 | 0.651267 | 0.665613 | 0.651879 |
| Apertus-8B | MLE | 16 | 0.9057 | 0.824769 | 0.832457 | 0.777276 | 0.773904 |
| Apertus-8B | MLE | 31 | 0.872901 | 0.748392 | 0.765909 | 0.764087 | 0.75987 |

## Table 15

Regression performance of Profiling-UD and matched 46-term lexical baselines. Values are mean five-fold cross-validated R².

[Download the CSV](tables/table_15.csv)

| Model | Target | Layer | Profiling ud RF R² | Frequent ridge R² | Frequent RF R² | Band ridge R² | Band RF R² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | ESS | 2 | 0.255604 | 0.169061 | 0.153899 | 0.10081 | 0.0677835 |
| Pythia-6.9B | ESS | 16 | 0.505404 | 0.267652 | 0.273527 | 0.250847 | 0.220822 |
| Pythia-6.9B | ESS | 31 | 0.26343 | 0.141701 | 0.134744 | 0.137813 | 0.103691 |
| Pythia-6.9B | FCI | 2 | 0.259316 | 0.151793 | 0.138691 | 0.0998209 | 0.0718938 |
| Pythia-6.9B | FCI | 16 | 0.423666 | 0.196325 | 0.192022 | 0.199 | 0.154952 |
| Pythia-6.9B | FCI | 31 | 0.207663 | 0.0848453 | 0.0772818 | 0.0956003 | 0.0495777 |
| Pythia-6.9B | MLE | 2 | 0.127172 | -0.00532173 | 0.00670022 | 0.0729565 | -0.00426045 |
| Pythia-6.9B | MLE | 16 | 0.25872 | 0.0615821 | 0.0716785 | 0.101453 | 0.0725316 |
| Pythia-6.9B | MLE | 31 | 0.213313 | 0.0720128 | 0.103021 | 0.0812861 | 0.0402238 |
| Qwen2.5-7B | ESS | 2 | 0.245715 | 0.120301 | 0.0977783 | 0.0420466 | -0.0174991 |
| Qwen2.5-7B | ESS | 14 | 0.546617 | 0.326653 | 0.323204 | 0.302137 | 0.268936 |
| Qwen2.5-7B | ESS | 27 | 0.432108 | 0.233995 | 0.239282 | 0.224686 | 0.179661 |
| Qwen2.5-7B | FCI | 2 | 0.204394 | 0.0966143 | 0.0702831 | 0.0267845 | -0.0317289 |
| Qwen2.5-7B | FCI | 14 | 0.481613 | 0.29363 | 0.294488 | 0.271501 | 0.222481 |
| Qwen2.5-7B | FCI | 27 | 0.359037 | 0.159072 | 0.162167 | 0.166922 | 0.127757 |
| Qwen2.5-7B | MLE | 2 | 0.0494738 | -0.00933561 | -0.044421 | 0.000147833 | -0.07443 |
| Qwen2.5-7B | MLE | 14 | 0.239229 | 0.0837508 | 0.0834779 | 0.100027 | 0.0545344 |
| Qwen2.5-7B | MLE | 27 | 0.158917 | 0.0702364 | 0.145108 | 0.0683092 | 0.0254876 |
| Apertus-8B | ESS | 2 | 0.33173 | 0.145283 | 0.160937 | 0.031485 | -0.0269749 |
| Apertus-8B | ESS | 16 | 0.441467 | 0.244656 | 0.237333 | 0.206322 | 0.170668 |
| Apertus-8B | ESS | 31 | 0.342569 | 0.177839 | 0.172203 | 0.14924 | 0.112115 |
| Apertus-8B | FCI | 2 | 0.33226 | 0.143087 | 0.160944 | 0.0250454 | -0.0305327 |
| Apertus-8B | FCI | 16 | 0.402551 | 0.222886 | 0.216959 | 0.193635 | 0.155186 |
| Apertus-8B | FCI | 31 | 0.303409 | 0.151305 | 0.137891 | 0.125441 | 0.0919602 |
| Apertus-8B | MLE | 2 | 0.130949 | -0.00839696 | -0.0344158 | 0.00341968 | -0.0392801 |
| Apertus-8B | MLE | 16 | 0.271528 | 0.117662 | 0.116544 | 0.13273 | 0.0955747 |
| Apertus-8B | MLE | 31 | 0.137916 | 0.046939 | 0.0794498 | 0.0686951 | 0.0286937 |

## Table 16

ESS pointwise-ID regression across five Pythia checkpoints. Scores are mean five-fold random-forest R²; importances are mean held-out R² decreases over eight shuffles and five folds.

[Download the CSV](tables/table_16.csv)

| Checkpoint | Layer | R² | Five largest held-out importances |
| --- | --- | --- | --- |
| step 512 | 2 | 0.14618 | upos_PUNCT (0.0808); upos_PRON (0.0271); median_frequency_class (0.0211); char_per_tok (0.0207); verbal_root (0.0144) |
| step 512 | 16 | 0.197301 | char_per_tok (0.0673); upos_PUNCT (0.0353); upos_DET (0.0236); upos_PRON (0.0181); aux_tense_dist_Pres (0.0154) |
| step 512 | 31 | 0.182908 | char_per_tok (0.0371); upos_PUNCT (0.0279); upos_DET (0.0215); upos_NUM (0.0213); upos_ADJ (0.0192) |
| step 8000 | 2 | 0.167443 | upos_PUNCT (0.1102); upos_PROPN (0.0589); upos_PART (0.0130); tokens_per_sent (0.0127); upos_DET (0.0106) |
| step 8000 | 16 | 0.478662 | n_sentences (0.5838); upos_PROPN (0.0435); char_per_tok (0.0397); upos_NOUN (0.0386); dep_nsubj (0.0385) |
| step 8000 | 31 | 0.396367 | n_sentences (0.4769); verbal_root (0.0584); upos_PROPN (0.0447); dep_nsubj (0.0331); upos_NOUN (0.0239) |
| step 21000 | 2 | 0.19925 | upos_PUNCT (0.0711); n_tokens (0.0706); upos_PROPN (0.0426); upos_NOUN (0.0212); upos_NUM (0.0124) |
| step 21000 | 16 | 0.522108 | char_per_tok (0.1209); upos_PRON (0.0986); upos_PROPN (0.0839); upos_NOUN (0.0717); verbal_root (0.0377) |
| step 21000 | 31 | 0.291352 | verbal_root (0.0615); upos_PROPN (0.0591); upos_PRON (0.0429); upos_NOUN (0.0380); dep_nsubj (0.0350) |
| step 55000 | 2 | 0.183619 | n_tokens (0.0595); upos_PUNCT (0.0515); upos_NOUN (0.0213); upos_PROPN (0.0180); char_per_tok (0.0128) |
| step 55000 | 16 | 0.523251 | upos_NOUN (0.1764); char_per_tok (0.0834); upos_PRON (0.0741); upos_PROPN (0.0584); verbal_root (0.0542) |
| step 55000 | 31 | 0.283546 | verbal_root (0.0817); upos_NOUN (0.0705); upos_PROPN (0.0523); upos_PRON (0.0312); upos_ADV (0.0185) |
| final/main | 2 | 0.255604 | n_tokens (0.1517); upos_PROPN (0.0402); upos_PUNCT (0.0323); char_per_tok (0.0180); dep_nsubj (0.0165) |
| final/main | 16 | 0.505404 | upos_NOUN (0.1449); char_per_tok (0.0876); upos_PRON (0.0737); upos_PROPN (0.0656); verbal_root (0.0453) |
| final/main | 31 | 0.26343 | upos_NOUN (0.0736); upos_PROPN (0.0624); verbal_root (0.0399); upos_PRON (0.0315); dep_nsubj (0.0211) |

## Table 17

The 43 Profiling-UD descriptors and three frequency summaries used by the downstream analyses.

[Download the CSV](tables/table_17.csv)

| Family | Feature | Definition |
| --- | --- | --- |
| Surface and lexical composition | n_sentences | Number of sentences detected by the UD parser. |
| Surface and lexical composition | n_tokens | Number of UD word tokens, distinct from the number of language-model subword tokens. |
| Surface and lexical composition | tokens_per_sent | Mean number of UD word tokens per parser-detected sentence. |
| Surface and lexical composition | char_per_tok | Mean number of characters per non-punctuation UD token. |
| Dependency-tree geometry | avg_links_len | Mean absolute head-dependent distance in UD tokens, excluding punctuation dependencies. |
| Dependency-tree geometry | max_links_len | Maximum head-dependent distance, using the same dependency filtering. |
| Dependency-tree geometry | avg_max_depth | Mean maximum root-to-leaf dependency-tree depth across parser-detected sentences. |
| Clausal and verbal-predicate structure | avg_prepositional_chain_len | Mean depth of recursively embedded prepositional or adpositional modifier chains. |
| Clausal and verbal-predicate structure | avg_subordinate_chain_len | Mean depth of recursively embedded subordinate-clause chains. |
| Clausal and verbal-predicate structure | avg_token_per_clause | Mean number of UD tokens per clause. |
| Clausal and verbal-predicate structure | avg_verb_edges | Mean number of eligible dependency links attached to each verbal head, excluding punctuation and copular links. |
| Clausal and verbal-predicate structure | subordinate_proposition_dist | Percentage of clauses classified as subordinate rather than main clauses. |
| Clausal and verbal-predicate structure | verbal_root_perc | Percentage of parser-detected sentences whose dependency root is tagged as VERB. |
| Linear order | subj_pre | Percentage of subject dependents preceding their governing verbal head. |
| Linear order | obj_post | Percentage of core-object dependents following their governing verbal head. |
| Linear order | subordinate_post | Percentage of subordinate-clause heads following their governing head. |
| Dependency-relation distributions | dep_dist_compound | Percentage of UD dependency relations labelled compound. |
| Dependency-relation distributions | dep_dist_nmod | Percentage of UD dependency relations labelled nominal modifier. |
| Dependency-relation distributions | dep_dist_nsubj | Percentage of UD dependency relations labelled nominal subject. |
| Dependency-relation distributions | dep_dist_obj | Percentage of UD dependency relations labelled core object. |
| Dependency-relation distributions | dep_dist_obl | Percentage of UD dependency relations labelled oblique nominal. |
| Morphosyntactic information | upos_dist_ADJ | Percentage of UD tokens tagged ADJ. |
| Morphosyntactic information | upos_dist_ADP | Percentage of UD tokens tagged ADP. |
| Morphosyntactic information | upos_dist_ADV | Percentage of UD tokens tagged ADV. |
| Morphosyntactic information | upos_dist_AUX | Percentage of UD tokens tagged AUX. |
| Morphosyntactic information | upos_dist_CCONJ | Percentage of UD tokens tagged CCONJ. |
| Morphosyntactic information | upos_dist_DET | Percentage of UD tokens tagged DET. |
| Morphosyntactic information | upos_dist_NOUN | Percentage of UD tokens tagged NOUN. |
| Morphosyntactic information | upos_dist_NUM | Percentage of UD tokens tagged NUM. |
| Morphosyntactic information | upos_dist_PART | Percentage of UD tokens tagged PART. |
| Morphosyntactic information | upos_dist_PRON | Percentage of UD tokens tagged PRON. |
| Morphosyntactic information | upos_dist_PROPN | Percentage of UD tokens tagged PROPN. |
| Morphosyntactic information | upos_dist_PUNCT | Percentage of UD tokens tagged PUNCT. |
| Morphosyntactic information | upos_dist_VERB | Percentage of UD tokens tagged VERB. |
| Morphosyntactic information | lexical_density | Percentage of word tokens assigned a content-word UPOS tag: NOUN, VERB, ADJ, or ADV. |
| Auxiliary morphology | aux_mood_dist_Ind | Among tokens tagged AUX: percentage marked Mood=Ind. |
| Auxiliary morphology | aux_num_pers_dist_Sing+3 | Among tokens tagged AUX: percentage jointly marked Number=Sing and Person=3. |
| Auxiliary morphology | aux_tense_dist_Pres | Among tokens tagged AUX: percentage marked Tense=Pres. |
| Lexical-verb morphology | verbs_form_dist_Inf | Percentage of VERB tokens marked as infinitives. |
| Lexical-verb morphology | verbs_form_dist_Part | Percentage of VERB tokens marked as participles. |
| Lexical-verb morphology | verbs_mood_dist_Ind | Percentage of VERB tokens marked for indicative mood. |
| Lexical-verb morphology | verbs_tense_dist_Past | Percentage of VERB tokens marked for past tense. |
| Lexical-verb morphology | verbs_tense_dist_Pres | Percentage of VERB tokens marked for present tense. |
| Tokenizer frequency controls | median_frequency_class | Median frequency class across model tokens in the input. |
| Tokenizer frequency controls | max_frequency_class | Largest frequency class in the input, corresponding to its rarest token under the frequency table. |
| Tokenizer frequency controls | min_frequency_class | Smallest frequency class in the input, corresponding to its most frequent token under the frequency table. |

## Geometry and control experiments

These tables retain the archived settings; experiment methods and coverage are documented in the repository’s `paper/ARTIFACTS.md`.

### Neighbourhood radius and composition at k = 1000

500 queries per setting; k=1000. Relative radius is the kth-neighbour distance divided by the query's median reference distance. Brackets show the interquartile range; composition and cosine values are means.

[Download the CSV](tables/neighbourhood_locality_k1000.csv)

| Model | Layer | Median radius | Relative radius [IQR] | Same source | Random same source | TF-IDF cosine | Random cosine | Source entropy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | 2 | 7.98019 | 0.799803 [0.774713, 0.833043] | 0.517854 | 0.194938 | 0.0359685 | 0.0241911 | 0.385811 |
| Pythia-6.9B | 16 | 98.2334 | 0.903129 [0.881369, 0.920151] | 0.635242 | 0.194938 | 0.0334302 | 0.0241911 | 0.293377 |
| Pythia-6.9B | 31 | 250.421 | 0.877891 [0.853911, 0.897019] | 0.586558 | 0.194938 | 0.0344754 | 0.0241911 | 0.338007 |
| Qwen2.5-7B | 2 | 4.87024 | 0.818774 [0.791537, 0.852857] | 0.462344 | 0.194938 | 0.0334132 | 0.0241911 | 0.45204 |
| Qwen2.5-7B | 14 | 52.5348 | 0.887615 [0.867788, 0.909993] | 0.612462 | 0.194938 | 0.0336196 | 0.0241911 | 0.325057 |
| Qwen2.5-7B | 27 | 365.172 | 0.887716 [0.868098, 0.905466] | 0.622728 | 0.194938 | 0.0364301 | 0.0241911 | 0.306021 |
| Apertus-8B | 2 | 4.108 | 0.764601 [0.722233, 0.81082] | 0.36176 | 0.194938 | 0.0303924 | 0.0241911 | 0.536739 |
| Apertus-8B | 16 | 1028.16 | 0.885685 [0.860769, 0.907119] | 0.59029 | 0.194938 | 0.033227 | 0.0241911 | 0.350801 |
| Apertus-8B | 31 | 13812 | 0.866305 [0.84326, 0.889065] | 0.593002 | 0.194938 | 0.0355176 | 0.0241911 | 0.33599 |

### Lexical enrichment for neighbour ranks 501–1000

Neighbours ranked 501–1000. Lexical gain is relative to the source-composition-matched random baseline; brackets show the paired 95% query-bootstrap interval.

[Download the CSV](tables/neighbourhood_outer_shell.csv)

| Model | Layer | Same source | TF-IDF cosine | Source-matched random cosine | Gain [95% CI] |
| --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | 2 | 0.476016 | 0.0331826 | 0.0281898 | 0.00499278 [0.00467264, 0.00532674] |
| Pythia-6.9B | 16 | 0.58498 | 0.0306018 | 0.0287531 | 0.00184875 [0.00164242, 0.00205569] |
| Pythia-6.9B | 31 | 0.53488 | 0.0310415 | 0.0285962 | 0.00244536 [0.00216696, 0.00271768] |
| Qwen2.5-7B | 2 | 0.415728 | 0.0315704 | 0.0273858 | 0.00418456 [0.00391398, 0.00447216] |
| Qwen2.5-7B | 14 | 0.553652 | 0.0310786 | 0.0285253 | 0.00255329 [0.00235619, 0.00274745] |
| Qwen2.5-7B | 27 | 0.576868 | 0.0328463 | 0.0292091 | 0.00363713 [0.00335155, 0.0039382] |
| Apertus-8B | 2 | 0.308784 | 0.0286497 | 0.0260981 | 0.00255155 [0.00230866, 0.00280539] |
| Apertus-8B | 16 | 0.539188 | 0.0308085 | 0.0286262 | 0.00218232 [0.00199466, 0.00237389] |
| Apertus-8B | 31 | 0.547132 | 0.0325735 | 0.0289751 | 0.00359844 [0.00334315, 0.00386536] |

### Incremental nonsurface prediction beyond source and lexical controls

Matched cohort of 1,866 period-final excerpts. Scores are pooled out-of-fold R². Both unadjusted and familywise 95% intervals are shown; word and word-plus-character baselines remain separate.

[Download the CSV](tables/source_tfidf_incremental.csv)

#### Word TF-IDF

| Model | Layer | Baseline R² | Augmented R² | Delta R² | Delta [95% CI] | Delta [familywise 95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | 2 | 0.526377 | 0.532772 | 0.00639546 | 0.00639546 [0.00143822, 0.0110754] | 0.00639546 [-3.17805e-05, 0.012922] |
| Pythia-6.9B | 16 | 0.703284 | 0.712832 | 0.0095482 | 0.0095482 [0.00484354, 0.014578] | 0.0095482 [0.00269103, 0.0165887] |
| Pythia-6.9B | 31 | 0.453525 | 0.462794 | 0.00926914 | 0.00926914 [0.00207164, 0.0163686] | 0.00926914 [-0.0017197, 0.0192169] |
| Qwen2.5-7B | 2 | 0.409305 | 0.419403 | 0.0100977 | 0.0100977 [0.00438688, 0.0158429] | 0.0100977 [0.00158775, 0.0175847] |
| Qwen2.5-7B | 14 | 0.648593 | 0.656989 | 0.00839574 | 0.00839574 [0.00353639, 0.0133775] | 0.00839574 [0.00187483, 0.0153061] |
| Qwen2.5-7B | 27 | 0.710382 | 0.713901 | 0.0035187 | 0.0035187 [0.000958062, 0.00581889] | 0.0035187 [-0.000168882, 0.00702857] |
| Apertus-8B (15T) | 2 | 0.33079 | 0.342 | 0.0112098 | 0.0112098 [0.00353756, 0.0191032] | 0.0112098 [-0.000492609, 0.0214335] |
| Apertus-8B (15T) | 16 | 0.587572 | 0.596696 | 0.00912385 | 0.00912385 [0.00210588, 0.0156177] | 0.00912385 [-0.00114883, 0.0189671] |
| Apertus-8B (15T) | 31 | 0.485245 | 0.490462 | 0.00521716 | 0.00521716 [0.000729963, 0.00974309] | 0.00521716 [-0.0011858, 0.0113893] |

#### Word and character TF-IDF

| Model | Layer | Baseline R² | Augmented R² | Delta R² | Delta [95% CI] | Delta [familywise 95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| Pythia-6.9B | 2 | 0.506477 | 0.511899 | 0.00542145 | 0.00542145 [0.00112368, 0.00960894] | 0.00542145 [-0.000421836, 0.0112199] |
| Pythia-6.9B | 16 | 0.704077 | 0.71844 | 0.0143628 | 0.0143628 [0.00798372, 0.0208596] | 0.0143628 [0.00545348, 0.0236443] |
| Pythia-6.9B | 31 | 0.460906 | 0.466265 | 0.00535975 | 0.00535975 [-0.000855359, 0.0113592] | 0.00535975 [-0.00363235, 0.013598] |
| Qwen2.5-7B | 2 | 0.39124 | 0.399267 | 0.00802705 | 0.00802705 [0.00154238, 0.0145572] | 0.00802705 [-0.00172978, 0.0178209] |
| Qwen2.5-7B | 14 | 0.648427 | 0.661856 | 0.0134289 | 0.0134289 [0.00738261, 0.0193597] | 0.0134289 [0.00603183, 0.0220344] |
| Qwen2.5-7B | 27 | 0.71803 | 0.721148 | 0.00311803 | 0.00311803 [0.000313149, 0.00563068] | 0.00311803 [-0.000881507, 0.00677668] |
| Apertus-8B (15T) | 2 | 0.323198 | 0.339291 | 0.0160931 | 0.0160931 [0.00677549, 0.0251188] | 0.0160931 [0.0023477, 0.0291489] |
| Apertus-8B (15T) | 16 | 0.600547 | 0.610997 | 0.0104505 | 0.0104505 [0.00283364, 0.0174547] | 0.0104505 [-0.000995702, 0.0203914] |
| Apertus-8B (15T) | 31 | 0.497646 | 0.502411 | 0.0047644 | 0.0047644 [0.000595913, 0.00896326] | 0.0047644 [-0.00112617, 0.0107931] |

### Feature-family ablations across available model/layer/k settings

Held-out score decrease after refitting without each feature family. All archived settings and all nine families are displayed. Positive values indicate worse performance after removal; negative values are retained. Scores are R² for regression and ROC-AUC for low/high classification. Full feature-set, split, and reference-size labels remain in the CSV.

[Download the CSV](tables/feature_family_ablation.csv)

Family columns: Surface = `raw_text`; Frequency = `lexical_frequency`; UPOS = `upos_distribution`; Lexical = `lexical`; Predicate = `verbal_predicate_structure`; Tree = `parse_tree_structure`; Relations = `syntactic_relations`; Subordination = `subordination`; Verb edges = `verbal_edge_structure`.

#### Pythia-1.4B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.00639284 | 0.00633049 | 0.0296856 | 0.00043244 | 0.00419409 | 0.00353825 | 0.0045887 | 0.00179578 | 0.00115233 |
| 1 | 1000 | 0.00625034 | 0.00403459 | 0.0243947 | 0.00239013 | 0.000868591 | 0.00222203 | 0.00399995 | 2.521e-05 | -0.00241873 |
| 2 | 500 | 0.0310139 | 0.00289811 | 0.00877967 | 0.00290701 | 0.00294914 | -0.00721422 | -6.90551e-05 | -8.59588e-05 | -0.0019757 |
| 2 | 1000 | 0.02887 | -7.71401e-05 | 0.0254821 | 0.0088863 | 0.00241456 | -0.0065642 | 0.00470876 | -0.00358442 | -0.00231628 |
| 12 | 500 | 0.0352097 | 0.000126571 | 0.0179493 | -0.000749094 | 0.00297917 | -0.000901129 | 0.00743069 | 0.00087506 | -0.00335917 |
| 12 | 1000 | 0.0284883 | -0.00163784 | 0.00941884 | 0.00268555 | 0.00498166 | -0.000451443 | 0.00172516 | 0.00244056 | -0.00110085 |
| 13 | 500 | 0.0359447 | -0.000403291 | 0.0233851 | 0.000728324 | 0.00839472 | 0.000646728 | 0.00688567 | 0.00180427 | -9.4294e-05 |
| 13 | 1000 | 0.032949 | -0.00181329 | 0.0143291 | 0.00122757 | 0.00867867 | -0.00195723 | 0.0057037 | -0.000598306 | -0.00196262 |
| 23 | 500 | 0.021226 | 0.000862262 | 0.0419073 | 0.00257151 | 0.0102489 | -0.00195546 | 0.0109441 | -9.4173e-06 | 0.000931901 |
| 23 | 1000 | 0.0132156 | 0.00229819 | 0.0310839 | -0.00195528 | 0.0289416 | -0.00249515 | 0.00844417 | -0.00137817 | -0.000930606 |
| 24 | 500 | 0.00151593 | 0.00132252 | 0.0237128 | -0.00715628 | -3.0876e-05 | -0.00937063 | -0.000597531 | -0.00190689 | -0.00087882 |
| 24 | 1000 | 0.0100357 | 0.00944349 | 0.0446248 | -0.000274179 | 0.0104587 | -0.0067913 | 0.00959771 | -5.9314e-05 | 0.00188867 |

#### Pythia-1.4B · ESS · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.0140581 | 0.000594798 | 0.0362781 | -0.00275693 | -0.00206553 | -0.005389 | -0.00470512 | -0.00209513 | -0.00317036 |
| 1 | 1000 | 0.0118191 | 0.00179851 | 0.0328706 | -0.00354495 | -0.000724395 | -0.00634952 | -0.00736421 | 9.36942e-05 | 0.000183949 |
| 2 | 500 | 0.0473238 | 0.00367218 | 0.023664 | 0.0027551 | -0.0006048 | 0.00235259 | -0.000896441 | 0.000727247 | -0.000531021 |
| 2 | 1000 | 0.0667405 | 0.0020999 | 0.0347057 | 0.000493405 | 0.00201621 | 0.0021294 | 0.000875989 | 0.00207782 | -0.000327613 |
| 12 | 500 | 0.0201155 | 7.8791e-05 | 0.0461494 | 0.000335416 | 0.0243829 | -0.00302887 | 0.0058221 | -0.002372 | -0.00198911 |
| 12 | 1000 | 0.032629 | 0.00209241 | 0.0532069 | -0.00128188 | 0.0316365 | 7.49558e-05 | 0.00838791 | -5.57085e-05 | 0.00186734 |
| 13 | 500 | 0.0198086 | 0.00297012 | 0.0441177 | 0.000875784 | 0.0211071 | -0.000671911 | 0.0105044 | -0.000368176 | 0.00210756 |
| 13 | 1000 | 0.0323812 | 0.00190515 | 0.0742822 | -0.000544741 | 0.0274701 | 0.00060156 | 0.013203 | -7.6574e-05 | -0.000523039 |
| 23 | 500 | 0.00852672 | 0.00134499 | 0.0500672 | -0.00346489 | 0.0168797 | 0.000779249 | 0.00476648 | -0.000171691 | 0.000367172 |
| 23 | 1000 | 0.00901114 | 0.00136697 | 0.0640952 | -0.00252819 | 0.0229673 | 0.00086348 | 0.0106445 | -0.000356735 | 0.00149453 |
| 24 | 500 | 0.00625023 | 0.00212689 | 0.0655701 | -0.000655641 | 0.014739 | -0.000602056 | 0.00591922 | 0.000355199 | 0.00235626 |
| 24 | 1000 | 0.00757464 | 0.00213573 | 0.0904614 | -0.00194867 | 0.026908 | -0.000888281 | 0.00706527 | 0.000553101 | 0.000327841 |

#### Pythia-1.4B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.00229312 | 0.00199684 | 0.0348924 | -0.00404628 | -0.00403204 | -0.00786669 | -0.00667326 | -0.0010716 | -0.000435522 |
| 1 | 1000 | 0.000530459 | 0.000759098 | 0.0147128 | -0.00516574 | 0.00118078 | -0.0127587 | -0.00209573 | -0.000832674 | -0.00085087 |
| 2 | 500 | 0.0375131 | 0.00838608 | 0.0219984 | -0.00141258 | 0.00227017 | 0.00188964 | 0.00978916 | 0.000599288 | 0.00584335 |
| 2 | 1000 | 0.0345083 | 0.00429826 | 0.0218544 | 0.000622627 | 0.00481131 | 0.00540071 | 0.000608782 | 2.37342e-06 | -0.00321638 |
| 12 | 500 | 0.0107587 | -0.00122191 | 0.0146412 | 0.00125949 | 0.00799328 | 0.00234968 | 0.00995649 | 0.00367761 | 0.00322785 |
| 12 | 1000 | 0.0103667 | 0.00297706 | 0.015896 | 3.36234e-05 | 0.0257255 | 0.00373576 | 0.0082144 | 0.00258861 | 0.00134138 |
| 13 | 500 | 0.010195 | 0.00273101 | 0.0199043 | 0.000375396 | 0.0114929 | 0.00178362 | 0.00797983 | 0.00174446 | 0.000743275 |
| 13 | 1000 | 0.0103188 | -0.00236432 | 0.00842563 | -0.00554272 | 0.0283074 | -0.000333465 | 0.00356646 | 0.000780063 | 0.000778085 |
| 23 | 500 | 0.0114992 | 0.0013216 | 0.0348782 | 0.00486788 | 0.0236246 | 0.00299604 | 0.00901978 | -0.000666535 | 0.00230024 |
| 23 | 1000 | 0.0138588 | 0.0041428 | 0.0309529 | 0.00195688 | 0.0223659 | -0.00364597 | 0.000282437 | -0.00469146 | -0.00204628 |
| 24 | 500 | 0.0109727 | 0.00368552 | 0.0390819 | -0.00360483 | 0.0164264 | -0.000179193 | 0.00468869 | 0.000258703 | -0.00326938 |
| 24 | 1000 | 0.0106507 | 0.00392089 | 0.0352737 | -0.00139755 | 0.0142413 | 0.00166456 | 0.00733742 | 0.000315665 | -0.000599288 |

#### Pythia-1.4B · ESS_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.0272749 | 0.00192366 | 0.0283307 | 0.00116139 | 0.00251424 | -0.00439241 | 0.00100475 | -0.000946203 | -3.79747e-05 |
| 1 | 1000 | 0.0229043 | -0.000617484 | 0.016142 | -0.00325079 | -0.00271084 | -0.00181329 | 0.000411788 | 0.00132872 | 0.000285206 |
| 2 | 500 | 0.0306737 | 0.00141456 | 0.01739 | -0.00015625 | -0.000758703 | -0.00132793 | 0.00249723 | 0.000113133 | -6.40823e-05 |
| 2 | 1000 | 0.0312136 | -0.003464 | 0.0135174 | -0.00333742 | -0.00549328 | -0.00523576 | -0.00639043 | -0.00396796 | -0.00381487 |
| 12 | 500 | 0.00398576 | -0.00220609 | 0.00685483 | -0.00124763 | -0.000870253 | -0.001464 | 0.00318394 | -0.00060087 | 0.000380934 |
| 12 | 1000 | 0.00284573 | -0.00134454 | 0.0142453 | -0.00109691 | 0.00153718 | -0.000628165 | -0.000756725 | -0.000914953 | -0.00115665 |
| 13 | 500 | 0.00269976 | -0.00160759 | 0.0101234 | -0.000368671 | 0.000109573 | -0.000854035 | 0.00563805 | 3.16456e-06 | -0.000487737 |
| 13 | 1000 | 0.00240229 | -0.00144858 | 0.0150202 | -0.00377413 | -0.00384415 | -0.00305736 | 0.00187025 | -0.0027765 | -0.00113766 |
| 23 | 500 | 0.00847271 | 0.0046879 | 0.0259122 | 0.00201187 | 0.00624328 | 0.00158149 | 0.00472033 | 0.000921282 | 0.00016337 |
| 23 | 1000 | 0.00762025 | 0.0046697 | 0.0365131 | 0.00201859 | 0.000827532 | 0.00489913 | -0.00299802 | 0.0029913 | 0.0053481 |
| 24 | 500 | 0.00527373 | -0.000956487 | 0.0447848 | -0.00414834 | 0.00205854 | -0.00189715 | 0.00546796 | -0.00302967 | 5.9731e-05 |
| 24 | 1000 | 0.00883663 | 0.00342247 | 0.0456163 | 0.000999604 | 0.0105047 | 0.00232437 | 0.010591 | 0.00279786 | -0.00102136 |

#### Pythia-6.9B · ESS · RF · ess run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.000806362 | 0.00232 | 0.0378084 | -0.00213904 | -0.000877071 | 0.000317734 | -0.000510871 | 0.00102998 | 0.000239417 |
| 1 | 100 | 0.0176822 | 0.00101306 | 0.0373653 | -0.00171147 | -0.00225476 | -0.00484014 | 0.00422252 | 0.000121267 | -0.000883214 |
| 1 | 500 | 0.0267152 | 0.000638289 | 0.0234932 | -0.00180412 | 0.000439517 | 0.00281583 | -0.00599624 | -0.00134923 | -0.00330868 |
| 1 | 2000 | 0.0610804 | 0.00340309 | 0.0290326 | 8.80786e-05 | 0.00597218 | 0.0038801 | -1.61415e-05 | 0.000709698 | -0.00222586 |
| 1 | 3000 | 0.0707877 | 0.00192251 | 0.034177 | -0.00292125 | 0.00241822 | -0.00025222 | 0.00236611 | -0.000799397 | -0.00443357 |
| 2 | 10 | 0.0037842 | 0.00470995 | 0.0402321 | -0.000793334 | 0.00152486 | 0.000955646 | -0.000844981 | 0.000935642 | 0.000427089 |
| 2 | 100 | 0.0259799 | 0.00260365 | 0.0262844 | 0.000317011 | -0.00286519 | 0.000325254 | 0.00130967 | -0.000358574 | -0.000441606 |
| 2 | 500 | 0.0287317 | 0.00422341 | 0.0294031 | -0.000902233 | -0.00320081 | 0.00128732 | 0.00206237 | 0.00225165 | -0.000684 |
| 2 | 2000 | 0.0706056 | 0.00094141 | 0.0563426 | -0.000872161 | 0.0083253 | -0.00252008 | -0.000278969 | 0.000870044 | -0.000805551 |
| 2 | 3000 | 0.0932576 | 0.000554521 | 0.0674357 | 0.000306109 | 0.00701836 | 0.000451286 | 0.00238069 | 0.000168181 | -0.000901636 |
| 16 | 10 | 0.00181172 | 3.52427e-05 | 0.0324342 | -0.000112858 | 0.000217879 | -0.00116533 | 0.00377674 | 0.00100675 | 0.00915507 |
| 16 | 100 | 0.00746654 | -0.000655302 | 0.0358806 | 0.0017198 | 0.0172051 | 0.00295857 | 0.0133757 | 0.00232856 | -0.000471071 |
| 16 | 500 | 0.0268107 | -8.43199e-05 | 0.0484285 | 0.000460197 | 0.0291541 | -0.000714785 | 0.00815125 | 0.00260192 | -0.000176034 |
| 16 | 2000 | 0.0200694 | 0.00114163 | 0.0574807 | -0.00229322 | 0.0580205 | -0.00227215 | 0.00854704 | 0.000497445 | -0.000615872 |
| 16 | 3000 | 0.022412 | 0.00160032 | 0.0534536 | -0.00110494 | 0.0748008 | -0.0035088 | 0.00613708 | 0.000258175 | -0.00190403 |
| 17 | 10 | 0.00425664 | 0.0016457 | 0.0202407 | 0.000463206 | 0.00116305 | 0.00373552 | 0.00748183 | 0.00344473 | 0.0042343 |
| 17 | 100 | 0.00828065 | 0.00103318 | 0.0287211 | 0.000216524 | 0.0135838 | 0.000911798 | 0.0107767 | 0.00176957 | -0.00167748 |
| 17 | 500 | 0.0223534 | 0.000489826 | 0.0481495 | 0.000652752 | 0.0272898 | 5.01291e-05 | 0.00560093 | 0.000355753 | -0.000657963 |
| 17 | 2000 | 0.0246414 | 0.00220602 | 0.0628462 | -0.000330228 | 0.0613814 | -0.00197797 | 0.0103223 | 0.000674853 | -0.000454502 |
| 17 | 3000 | 0.0219081 | 0.00107987 | 0.0567867 | -0.00159313 | 0.06831 | -0.00276975 | 0.00570666 | -0.00128801 | -0.00141955 |
| 31 | 10 | 0.00261664 | 0.00344746 | 0.0111729 | -0.00239016 | 0.0144679 | -0.00336031 | 0.009704 | 0.00339637 | -0.000565108 |
| 31 | 100 | 0.012551 | 0.00339534 | 0.0315751 | -0.00227094 | 0.0134316 | -0.000550243 | 0.00180899 | 0.00208267 | -0.00327597 |
| 31 | 500 | 0.00431531 | 0.00245732 | 0.0610134 | -0.00112701 | 0.0120823 | -0.00184067 | 0.000589766 | 0.000839627 | -0.00225478 |
| 31 | 2000 | 0.00114086 | -0.00258112 | 0.059102 | -0.00078804 | 0.0293922 | 0.000770614 | 0.00600656 | -0.00017192 | -0.00246902 |
| 31 | 3000 | 0.0038629 | -0.000113443 | 0.0569297 | 0.000764637 | 0.0408132 | -0.000638224 | 0.00492247 | 0.00134566 | 0.00294894 |
| 32 | 10 | 0.00190385 | 0.00189624 | 0.038517 | -0.00159736 | -0.000325718 | 0.000749193 | -0.00422626 | 0.000342056 | -0.000290836 |
| 32 | 100 | 0.00425258 | 0.00437059 | 0.0389281 | 0.00115543 | -0.00212064 | -0.00152384 | 0.00592033 | 0.00329784 | -0.00134176 |
| 32 | 500 | 0.01405 | 0.00343573 | 0.0751509 | -0.000411468 | 0.00881276 | -3.2744e-05 | 0.00979301 | 0.00126765 | -0.00127847 |
| 32 | 2000 | 0.00764226 | 0.000497657 | 0.0850585 | -0.00300126 | 0.0455903 | -0.00320218 | 0.0136107 | -0.000435472 | -0.000712765 |
| 32 | 3000 | 0.00393176 | 0.00291245 | 0.0885401 | -0.000327533 | 0.060153 | -0.00505065 | 0.0195105 | 0.000708359 | -0.000196564 |

#### Pythia-6.9B · ESS_LOW_VS_HIGH · RF · ess run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.0115237 | 0.00170016 | 0.0270459 | 0.000389636 | 0.00154153 | 0.00259454 | 0.000400316 | -0.00729035 | 0.00671005 |
| 1 | 100 | 0.0259134 | -0.00492642 | 0.0331028 | -0.00180301 | -0.000414953 | -0.00424486 | -0.00400475 | -0.00267959 | -0.00540625 |
| 1 | 500 | 0.0255621 | 0.00237104 | 0.0277211 | -0.000223892 | 0.000318434 | 0.00019106 | 0.000626187 | 0.00105973 | 0.00121479 |
| 1 | 2000 | 0.0283809 | -0.00238449 | 0.0214498 | -0.00106092 | -0.00153441 | -0.00414478 | -0.00345293 | -0.0033568 | -0.000548655 |
| 1 | 3000 | 0.0367373 | 0.00384929 | 0.0173679 | 0.00235087 | -0.000140427 | -0.00255973 | 0.00213568 | -0.000226661 | -0.000282832 |
| 2 | 10 | 0.00329114 | -0.0017591 | 0.0415316 | 0.00140981 | 7.27848e-05 | 0.00409059 | -0.00449881 | -0.00341891 | -0.00383544 |
| 2 | 100 | 0.0135756 | 0.00241179 | 0.0200119 | -0.00317959 | -0.00232832 | -0.00426345 | 0.00174367 | -0.00389755 | -0.00539794 |
| 2 | 500 | 0.0170257 | 0.00714201 | 0.0116167 | 0.000975475 | -0.00208821 | -0.00237302 | 0.00570293 | 0.000903877 | 0.000954114 |
| 2 | 2000 | 0.038835 | -0.00021875 | 0.0234134 | -0.000696598 | -0.00217998 | -0.000653481 | 0.00339873 | 0.00047587 | -0.00435918 |
| 2 | 3000 | 0.0336958 | -0.00144383 | 0.0257884 | -0.00236195 | -0.00293513 | -0.000868275 | 0.00137421 | 0.000844146 | -0.00171203 |
| 16 | 10 | 0.000626187 | 0.00304391 | 0.0187441 | -0.00158544 | -0.000765823 | 0.00203244 | 0.00250356 | -0.000431962 | 0.00122468 |
| 16 | 100 | 0.00574011 | 0.000321598 | 0.0234268 | -8.70253e-06 | 0.000103639 | -0.000433149 | -0.00088212 | 0.00288805 | 0.00181883 |
| 16 | 500 | 0.00459494 | -0.00251741 | 0.0179193 | -0.00053125 | -0.00134731 | -0.00191614 | -0.00185562 | 0.000953323 | -0.000185127 |
| 16 | 2000 | 0.00778956 | 0.00119066 | 0.0145324 | 0.000108782 | 0.0320396 | -6.28956e-05 | 0.000649525 | -9.21677e-05 | -0.00133149 |
| 16 | 3000 | 0.00820688 | -0.0015182 | 0.0150526 | -0.000733386 | 0.0358612 | -0.000414953 | 0.00113924 | 0.00144066 | -0.00166891 |
| 17 | 10 | 0.000232595 | 0.0032856 | 0.0160289 | -0.00581487 | 0.000581092 | 4.74684e-06 | 0.000606408 | 0.00371242 | 0.000766614 |
| 17 | 100 | -0.00205261 | -0.000120649 | 0.0198904 | -0.000243671 | 0.000240902 | -0.0013932 | 0.0044015 | -2.8481e-05 | -0.00163133 |
| 17 | 500 | 0.00777492 | 0.000911392 | 0.0200894 | 0.000314478 | 0.000101661 | -0.000410601 | 0.00162302 | 0.000196203 | 9.69146e-05 |
| 17 | 2000 | 0.00419937 | -0.00217128 | 0.0161942 | -0.00394739 | 0.0262777 | -0.00405498 | -0.00127334 | -0.00257397 | -0.00406369 |
| 17 | 3000 | 0.00785997 | 0.00195609 | 0.0209549 | -0.000509889 | 0.0360233 | -0.000265427 | 0.00198339 | 0.000165348 | 0.000186709 |
| 31 | 10 | -0.0015803 | 0.00207555 | 0.0229624 | -0.00987342 | -0.00894937 | -0.00131052 | -0.00552334 | -0.00239043 | -0.0076341 |
| 31 | 100 | 0.00721875 | 0.00356764 | 0.0322504 | 0.00246044 | 0.00424921 | 0.00139399 | -0.000249604 | 0.00423932 | 0.00145016 |
| 31 | 500 | -0.00204351 | -0.00541218 | 0.0360645 | -0.00270293 | 0.00316297 | 0.00171084 | 0.00274169 | 0.00282911 | -0.00192603 |
| 31 | 2000 | 4.19304e-05 | -0.00209929 | 0.0291772 | -0.00303165 | 0.0057413 | -0.000370253 | -0.000859177 | -0.000990902 | -0.00365665 |
| 31 | 3000 | 0.00184691 | -0.00149248 | 0.0231661 | -0.00268908 | 0.0265051 | -0.00436076 | 0.00569343 | 0.00251978 | -0.00155657 |
| 32 | 10 | 0.00207002 | 0.00148497 | 0.0405787 | -0.00174881 | -0.00253085 | 0.00626978 | 0.00840744 | 0.00371005 | 0.00113212 |
| 32 | 100 | 0.00927334 | 0.00459652 | 0.0330063 | 0.00216733 | 0.00486076 | 0.00456052 | 0.0028659 | 0.00335403 | 0.00404628 |
| 32 | 500 | 0.00659375 | 0.00437975 | 0.034589 | -4.39082e-05 | 0.00363212 | 0.00103244 | 0.0114304 | 0.00309375 | 0.000987342 |
| 32 | 2000 | 0.00210918 | -0.00314161 | 0.0514525 | -0.00163212 | 0.0197935 | -0.0022235 | 0.00248734 | -0.000493671 | -0.00253797 |
| 32 | 3000 | 0.00447983 | 0.00096875 | 0.0577057 | 0.00120214 | 0.0197275 | 0.000259889 | 0.00559098 | 0.00118987 | 0.00175 |

#### Pythia-6.9B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.0157828 | -0.00117829 | 0.00623693 | 0.00141002 | 0.00738641 | -0.0034005 | 0.00338783 | 0.0010376 | 0.00314288 |
| 1 | 100 | 0.00685598 | 0.00407002 | 0.0191269 | -0.00194429 | -0.00145035 | -0.00296864 | 0.00328294 | -0.00397397 | 0.000548064 |
| 1 | 500 | 0.00989053 | 0.00267664 | 0.0267275 | -0.00214604 | -0.00330268 | -0.00597964 | -0.00247865 | -0.0022896 | -0.00631656 |
| 1 | 2000 | 0.0132882 | -0.000143068 | 0.0369777 | 0.00235302 | -0.00254786 | -0.00593529 | 0.00231133 | 0.00116121 | 0.000738274 |
| 1 | 3000 | 0.00338053 | 0.00318796 | 0.0352189 | -0.0025291 | -0.00326345 | -0.00457777 | 0.000543962 | 0.0020448 | -0.00164235 |
| 2 | 10 | 0.00384827 | 0.00270267 | 0.0134866 | 0.00191311 | 0.0014105 | -0.00566867 | 0.000736348 | -0.000350668 | -0.00266929 |
| 2 | 100 | 0.000642723 | 0.00503367 | 0.0238404 | -0.000687366 | -0.00115913 | 0.0025383 | -0.00358647 | 0.000379893 | 0.0022174 |
| 2 | 500 | 0.019962 | 6.73273e-05 | 0.0345177 | 0.00795902 | 0.00490705 | -6.28609e-05 | 0.0107643 | -0.000974958 | -0.00106167 |
| 2 | 2000 | -0.00115331 | 0.00127987 | 0.0613451 | 0.00376711 | -0.000638128 | -0.00318212 | 0.0116771 | 0.000664253 | 0.00156525 |
| 2 | 3000 | -0.0010927 | 0.00202925 | 0.0697365 | 0.00177464 | 0.00500344 | -0.00220781 | 0.0096529 | 0.00285752 | -0.00272678 |
| 16 | 10 | 0.00370306 | -0.000569023 | 0.0231852 | -0.000287871 | 0.00451559 | 0.00314305 | 0.00286662 | -7.13874e-06 | 3.57442e-06 |
| 16 | 100 | 0.00416385 | -0.000328698 | 0.0168996 | 0.00525736 | 0.00777805 | -0.000778544 | 0.00168273 | -0.000546687 | -0.000669743 |
| 16 | 500 | 0.0470443 | -0.00127861 | 0.0322552 | 0.00541446 | 0.00785909 | -0.00147423 | 0.00796905 | 0.000957617 | 0.00122291 |
| 16 | 2000 | 0.0263459 | -0.000718252 | 0.0112737 | 0.00706948 | 0.00734092 | 0.00026209 | 0.0124703 | 0.000755688 | 0.000700685 |
| 16 | 3000 | 0.0230741 | -0.000557849 | 0.0141163 | 0.0050106 | 0.00685665 | 0.00151237 | 0.00822595 | 0.00019311 | -0.00070705 |
| 17 | 10 | 0.0058085 | 0.00448016 | 0.01016 | -0.00203313 | 0.0014498 | 0.00383066 | -0.00581523 | -0.000656827 | -0.0037554 |
| 17 | 100 | 0.0105521 | 0.000552462 | 0.0206321 | 0.00782595 | 0.0070835 | -0.00148203 | 0.00222132 | -0.000400199 | 0.00172386 |
| 17 | 500 | 0.0450666 | -0.00113569 | 0.0311358 | 0.00163964 | 0.0150359 | -0.00105883 | 0.00685129 | 0.00132768 | -0.00128718 |
| 17 | 2000 | 0.0281046 | -0.000228194 | 0.00855664 | 0.00643535 | 0.0106778 | 0.000959633 | 0.0135152 | 0.00384027 | 0.00152002 |
| 17 | 3000 | 0.0276885 | -0.00138279 | 0.00906693 | 0.00359155 | 0.00910323 | 0.00224176 | 0.00921037 | 0.000116288 | 0.00127233 |
| 31 | 100 | 0.0126962 | -0.000203976 | 0.0157513 | -0.0028472 | 0.0046601 | -0.00547011 | -0.00137896 | -0.00114802 | -0.00464739 |
| 31 | 500 | 0.0273368 | 0.00152916 | 0.039569 | -0.00276688 | 0.0149107 | -0.00525472 | 0.00695759 | 0.00145659 | -0.00160538 |
| 31 | 2000 | 0.0119724 | 0.000462251 | 0.0233364 | -0.00100049 | 0.0428285 | -0.00194908 | 0.00957973 | 0.000232699 | 0.000794603 |
| 31 | 3000 | 0.0105391 | 0.000212342 | 0.0258793 | -0.000397887 | 0.0306856 | 0.000444317 | -0.0016644 | -0.000247889 | -0.000144601 |
| 32 | 10 | 0.00177706 | -0.00139384 | 0.00247876 | -0.00240197 | 0.0110913 | -0.00474092 | -0.000640532 | -0.00112189 | -0.0032417 |
| 32 | 100 | 0.00358634 | 9.57167e-05 | 0.0184747 | -0.00233353 | 0.00356089 | -0.00624415 | 0.00337573 | 0.00526639 | -0.00134435 |
| 32 | 500 | 0.0091107 | -0.000131703 | 0.0327124 | -0.0036973 | 0.00799994 | -0.00962181 | 0.00901065 | 0.000196557 | -0.00283944 |
| 32 | 2000 | 0.00418427 | 0.00295103 | 0.0439835 | -0.000154089 | 0.00733681 | -0.00156771 | 0.00882191 | 0.000739949 | -0.00131415 |
| 32 | 3000 | 0.00552617 | -0.000887492 | 0.0562144 | 0.00166166 | 0.0037186 | -0.00202123 | 0.00882796 | 0.00370857 | -0.000596089 |

#### Pythia-6.9B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | -0.000138845 | -0.000799446 | 0.0273655 | 0.0035269 | 0.0153979 | 0.0156808 | -0.000448576 | 0.0111776 | 0.00986432 |
| 1 | 100 | 0.0139339 | -0.00231052 | 0.0366214 | -0.00741456 | -0.0147733 | -0.00579351 | -0.00799407 | -0.00690348 | -0.0067504 |
| 1 | 500 | 0.0124818 | 0.00272824 | 0.0228176 | -0.00547706 | -0.00120688 | -0.0054015 | -0.00411076 | -0.00433742 | -0.00238924 |
| 1 | 2000 | 0.0264142 | -0.00737104 | 0.0330154 | -0.00515704 | -0.00116851 | -0.00642998 | -0.00939201 | -0.00442128 | -0.00826741 |
| 1 | 3000 | 0.0207227 | 0.000433544 | 0.0268232 | -0.00601187 | 0.00131804 | -0.000950949 | -0.00342405 | -0.000632516 | -0.00944976 |
| 2 | 10 | 0.0144759 | 0.00721994 | 0.0188386 | 0.00657793 | -0.00400712 | 0.00472785 | 0.00621519 | 0.00604391 | 0.00695767 |
| 2 | 100 | 0.0164838 | 0.00287698 | 0.0201432 | -0.00284652 | 0.00658663 | 0.00470847 | -0.00400356 | 0.00152809 | -0.00189597 |
| 2 | 500 | 0.017267 | 0.00840585 | 0.0540827 | 0.00434533 | 0.00694897 | 0.000779668 | 0.00768908 | 0.00382555 | 0.00327769 |
| 2 | 2000 | 0.0100336 | 0.00281448 | 0.0405815 | 0.000967168 | 0.00482358 | 0.00257397 | 0.00854589 | 0.00478283 | 0.000884494 |
| 2 | 3000 | 0.00823141 | -5.22152e-05 | 0.0339549 | 0.000596519 | 0.00167642 | 0.00608663 | 0.00266891 | 0.00269778 | -0.000153877 |
| 16 | 10 | -0.00368394 | -0.00962737 | 0.0182033 | -0.00295807 | 1.81962e-05 | -0.00174011 | -0.00316851 | -0.00414597 | 0.000782041 |
| 16 | 100 | 0.00335601 | -0.00366851 | 0.0122749 | -0.00163331 | 0.00495253 | 0.000941851 | 0.00354193 | 0.00321677 | -4.43038e-05 |
| 16 | 500 | 0.00847627 | 0.00168354 | 0.0213588 | -0.000318829 | 0.0114284 | 0.00225 | 0.00413212 | 0.00463449 | 0.00176266 |
| 16 | 2000 | 0.0142658 | 0.000651503 | 0.00773695 | 0.000851266 | 0.0187536 | 0.000515823 | 0.00544541 | 0.000549842 | -1.66139e-05 |
| 16 | 3000 | 0.0113291 | -0.00117801 | 0.0088394 | -0.00096519 | 0.0198125 | -0.00168236 | -0.00299921 | 0.000329114 | -0.000420095 |
| 17 | 10 | 0.000860364 | 0.00326384 | 0.0122294 | 0.00588449 | 0.00467484 | -0.00230419 | 0.00838964 | 0.00275672 | 0.00066337 |
| 17 | 100 | 0.00769304 | 0.00154707 | 0.00922745 | 0.00086788 | 0.00126305 | 3.32278e-05 | 0.0102638 | 0.00340981 | 0.00217168 |
| 17 | 500 | 0.00787184 | 0.00186748 | 0.0233457 | 3.16456e-05 | 0.0122433 | 0.00344383 | 0.00176582 | 3.79747e-05 | -0.0017678 |
| 17 | 2000 | 0.00737579 | -0.00256013 | 0.00608782 | -0.00233347 | 0.0203892 | -0.00414478 | -0.0032678 | 0.000341772 | -0.00228125 |
| 17 | 3000 | 0.00810047 | 0.000390823 | 0.011731 | -0.00138726 | 0.0153252 | -0.00506685 | -0.000238528 | -0.00127373 | 0.000839003 |
| 31 | 10 | 0.00754628 | 0.00569383 | 0.00265348 | -0.0116171 | -0.00240625 | -0.00414636 | -0.00197666 | -0.0024913 | 0.0020087 |
| 31 | 100 | 0.0205736 | 0.00331962 | 0.0293422 | -0.0027057 | 0.0114403 | 0.00378521 | 0.00135047 | 0.00268631 | 0.00156883 |
| 31 | 500 | 0.015835 | -0.00101345 | 0.0284213 | -0.00348616 | 0.00743354 | -0.00550712 | -0.00751859 | -0.00444185 | -0.00741653 |
| 31 | 2000 | 0.00206052 | 0.000495253 | 0.0285977 | -0.00776899 | 0.0226646 | -0.000143592 | 0.00507951 | -0.00147152 | -0.00268434 |
| 31 | 3000 | 0.0155653 | 0.00379351 | 0.0253267 | -0.000704905 | 0.0295672 | -0.000516614 | 0.00893631 | 0.00415229 | -0.00152176 |
| 32 | 10 | 0.00223576 | -0.00292168 | 0.0159047 | -0.0108394 | -0.00161709 | -0.00480973 | 0.00941812 | -0.00277215 | -0.0055265 |
| 32 | 100 | 0.00589122 | -0.00185403 | 0.039608 | -0.00248576 | 0.00476226 | 0.000795491 | 0.00456725 | -0.00226543 | -0.00113172 |
| 32 | 500 | 0.0150977 | 0.0014731 | 0.0340969 | 0.00387263 | 0.0165309 | 2.37342e-06 | 0.0038038 | 0.00397073 | -0.000201345 |
| 32 | 2000 | 0.0113038 | 0.00570451 | 0.0143248 | 0.000749209 | 0.00340625 | -0.00186313 | 0.00359415 | 0.000785601 | -0.000348892 |
| 32 | 3000 | 0.0140518 | 0.00426582 | 0.0132449 | -0.000550237 | 0.00993078 | -0.00058307 | 0.00452492 | 0.00102017 | 3.83703e-05 |

#### Pythia-6.9B · MLE · RIDGE · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31 | 10 | 8.59013e-05 | 0.00293101 | 0.000800008 | -0.00106221 | -0.00760697 | -0.00262031 | -0.00761059 | -0.00154022 | -0.000475159 |

#### Qwen2.5-7B · FCI · RF · fci_pyfci run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.000403237 | 0.000549746 | 0.014134 | -0.000494812 | 0.00021547 | 0.01189 | 0.00284473 | 0.000620611 | 0.00132036 |
| 1 | 100 | 0.00353145 | 0.00305288 | 0.0393698 | -0.000214082 | 2.42969e-06 | -0.00222171 | 0.00116952 | 8.11406e-05 | 0.000295445 |
| 1 | 500 | 0.00019799 | -0.000624835 | 0.030723 | -0.00354867 | -0.00148257 | -0.00478213 | -0.00465527 | -0.00211421 | -0.00179818 |
| 1 | 2000 | 0.00728561 | -0.000509613 | 0.0268209 | -0.00206234 | 0.0192467 | -0.00186848 | 0.0107519 | -0.000782035 | 0.000269586 |
| 1 | 3000 | 0.0136013 | 0.000295846 | -0.0017793 | -0.00190306 | 0.0104166 | -0.000935426 | 0.00914887 | -0.00180038 | -0.0007807 |
| 2 | 100 | 0.0188978 | 0.000971257 | 0.0412396 | -0.000793418 | -0.00131669 | 0.00171068 | 0.00317743 | 0.00356158 | -0.000232336 |
| 2 | 500 | 0.0265688 | 0.00330305 | 0.0277322 | -0.000111709 | 0.00300785 | -0.000586708 | -5.08992e-05 | -0.000683938 | -0.000409416 |
| 2 | 2000 | 0.0713526 | 0.00130864 | 0.0202362 | 0.0005267 | 0.0468675 | -0.00213156 | 0.00669702 | -0.000902214 | 1.98542e-05 |
| 2 | 3000 | 0.0903737 | 0.00658883 | 0.0103298 | 0.000179585 | 0.0373601 | -0.0015648 | 0.000682484 | -0.000660488 | -0.000908589 |
| 3 | 10 | 0.0143409 | 0.00024346 | 0.014582 | -0.0013689 | 0.000839801 | 0.00521609 | 0.00166486 | -0.00113137 | -0.0021439 |
| 3 | 100 | 0.0104081 | 0.00290551 | 0.0302303 | -0.00139478 | -0.00090162 | -0.000700743 | 0.000787605 | 0.00307194 | -0.000614139 |
| 3 | 500 | 0.00162401 | -0.00224994 | 0.0364625 | -0.000354001 | -0.00303151 | 0.000351433 | 0.00622188 | 0.00219397 | 0.000416353 |
| 3 | 2000 | 0.0233349 | 0.00266087 | 0.0647772 | 0.00343119 | 0.0568319 | 0.00286552 | 0.0117195 | 0.00205601 | 0.00258208 |
| 3 | 3000 | 0.0322575 | 0.00433386 | 0.084008 | 0.00131681 | 0.0820482 | 0.000659741 | 0.0167835 | 0.00207512 | 0.000775812 |
| 4 | 100 | 0.00812847 | 0.00121888 | 0.0216352 | 0.00214651 | 0.00519472 | 0.00377494 | 0.00254626 | 0.00401799 | 0.00244094 |
| 4 | 500 | 0.00395255 | -0.00121112 | 0.0346056 | 0.00170845 | 0.010276 | 0.00374486 | 0.00422223 | 0.00175509 | -0.000474169 |
| 4 | 2000 | 0.021759 | -0.000309607 | 0.0482953 | -0.00101943 | 0.0888204 | 0.00256926 | 0.00808869 | -0.00115929 | 0.000725493 |
| 4 | 3000 | 0.0317382 | 0.00350355 | 0.0326673 | 0.00130986 | 0.0660208 | -0.00185433 | 0.00205911 | -0.000368461 | -0.000305997 |
| 5 | 100 | 0.00313821 | 0.00253766 | 0.0208331 | 0.000914135 | 0.015122 | 0.00132053 | 0.0106336 | 0.00376952 | 0.00100862 |
| 5 | 500 | 0.00909772 | -0.00123674 | 0.0417866 | -0.00234651 | 0.018052 | -0.00199419 | 0.00109488 | 0.000465545 | 0.00366861 |
| 5 | 2000 | 0.0107404 | -0.000149014 | 0.0063583 | -0.00195137 | 0.0552825 | -0.00333679 | 0.0110397 | -0.00180194 | -0.00192553 |
| 5 | 3000 | 0.0177617 | -1.97369e-05 | -0.00639764 | -0.00104059 | 0.0421748 | -0.00366973 | 0.00375143 | -0.0049168 | -0.00110525 |
| 6 | 10 | 0.00791671 | -0.000654514 | 0.0145222 | 0.00140069 | 0.000787188 | -0.00149813 | -0.00204327 | -0.000339023 | 0.00268176 |
| 6 | 100 | 0.00545102 | 0.00142371 | 0.0422277 | 0.00123234 | 0.00463576 | -0.00122653 | 0.00952606 | -0.000908856 | 0.00324997 |
| 6 | 500 | 0.00918889 | -0.000798778 | 0.0638331 | -0.000863947 | 0.0107142 | -0.00254087 | 0.00395036 | 0.000577056 | -0.000317649 |
| 6 | 2000 | 0.0197225 | 0.000839704 | 0.0567368 | -0.00268068 | 0.0617943 | -0.00175594 | 0.00318501 | 0.000620224 | 0.000676 |
| 6 | 3000 | 0.0252567 | 0.00155912 | 0.0534045 | 0.00010322 | 0.063338 | -0.00195315 | 0.00410594 | 0.000214819 | -0.000870872 |
| 14 | 10 | 0.0113299 | -0.005404 | 0.0050772 | 0.000517245 | 0.00709836 | 0.000216444 | 0.00115376 | 0.000637838 | -0.00413004 |
| 14 | 100 | 0.0119964 | 0.000396916 | 0.0157768 | 0.000228586 | 0.00326523 | -0.00261471 | 0.000675982 | -0.000478333 | 0.004418 |
| 14 | 500 | 0.0204828 | 0.00214588 | 0.0358453 | -0.000373892 | 0.0022518 | -0.00103462 | 0.0053728 | 0.000859733 | 0.00105482 |
| 14 | 2000 | 0.0219285 | 0.00285565 | 0.0573484 | -0.00119242 | 0.0220668 | -0.000785117 | 0.00498214 | -0.000645903 | -0.000908166 |
| 14 | 3000 | 0.019575 | 0.00181814 | 0.0613172 | -0.00234404 | 0.0268377 | -0.00139732 | 0.00673402 | -0.000908888 | -0.00118887 |
| 15 | 100 | 0.00229315 | -0.00162447 | 0.0205318 | -0.00264472 | 0.00245787 | 0.00279529 | -0.00100828 | 0.000218535 | -0.000346165 |
| 15 | 500 | 0.02109 | -0.00112942 | 0.0335446 | 0.00013108 | 0.00564614 | 0.000283502 | 0.00584266 | 0.000979785 | 0.000995295 |
| 15 | 2000 | 0.0149323 | 0.00111562 | 0.0781049 | 0.000586822 | 0.0166581 | 0.00217484 | 0.00627239 | 0.00133163 | 0.000387508 |
| 15 | 3000 | 0.0221029 | 0.00242022 | 0.0555113 | 0.000655904 | 0.0323549 | 0.00177024 | 0.00499539 | -0.000182035 | 0.00125009 |
| 27 | 100 | 0.01442 | 0.00600927 | 0.0219798 | 0.000251588 | 0.0135067 | 0.000865469 | 0.00797533 | 0.000948483 | 0.00102516 |
| 27 | 500 | 0.00867502 | -0.000855266 | 0.0480555 | -0.00225544 | 0.0508185 | -0.00353394 | -0.00173506 | 0.000596719 | -0.000850197 |
| 27 | 2000 | 0.0096549 | 0.000552374 | 0.0892733 | 0.00318551 | 0.0676022 | -0.000203942 | 0.00410037 | 0.000842469 | -0.000375836 |
| 27 | 3000 | 0.0136287 | -0.00136091 | 0.0551633 | -1.68595e-06 | 0.0997666 | -0.00263051 | 0.00323611 | 0.00315457 | -0.000363662 |
| 28 | 10 | 0.00241543 | 0.00278299 | 0.00437213 | -0.00503177 | 0.0130222 | -0.00194262 | 0.0142115 | -0.001848 | -0.000302589 |
| 28 | 100 | 0.00813588 | 0.000323769 | 0.0170861 | 8.73178e-05 | 0.0152857 | -0.00187031 | 0.001261 | -0.000363159 | -0.00161505 |
| 28 | 500 | 0.00565955 | 0.00518537 | 0.0398912 | -0.000849036 | 0.0258768 | -0.0018202 | -0.00460346 | 0.00150451 | -0.000485458 |
| 28 | 2000 | 0.0089021 | 0.00525125 | 0.058662 | 0.0025737 | 0.052914 | 0.00175513 | 0.00402217 | 0.000551036 | 0.000440372 |
| 28 | 3000 | 0.00459015 | 0.00357385 | 0.0563253 | 0.000777231 | 0.0534811 | 0.00171436 | 0.00446625 | 0.00204942 | -0.00119402 |

#### Qwen2.5-7B · FCI_LOW_VS_HIGH · RF · fci_pyfci run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 100 | 0.00954391 | -0.000306566 | 0.0116381 | -0.000677611 | 0.000315269 | -0.00707358 | -0.0062496 | 0.00103956 | 0.000474684 |
| 1 | 500 | 0.00508505 | 0.0032409 | 0.024998 | -0.00197983 | 0.00290823 | 0.00623853 | 0.00713489 | 0.00449446 | 0.00253718 |
| 1 | 2000 | 0.0096693 | 0.00130261 | 0.0192184 | 0.00341021 | 0.0125024 | 0.000397152 | 0.00460562 | -0.000235364 | -0.00107991 |
| 1 | 3000 | 0.0124715 | 0.00097587 | 0.0161685 | 0.000877769 | 0.0125645 | -0.000106804 | 0.0048481 | -0.000727848 | 0.00103797 |
| 2 | 10 | 0.016252 | 0.00287975 | 0.0382484 | -0.00366891 | -0.00526305 | 0.00490902 | -0.000384494 | -0.00271321 | -0.00128165 |
| 2 | 100 | 0.0210352 | -0.00322785 | 0.03968 | -0.00500672 | -0.00717682 | -0.0042765 | -0.00686788 | -0.00332041 | -0.00139992 |
| 2 | 500 | 0.0342848 | 0.00235759 | 0.0193058 | -0.000417722 | 0.00947191 | 0.00152888 | -0.000573576 | 0.00194699 | 0.00345728 |
| 2 | 2000 | 0.0263176 | -0.00153006 | 0.00717919 | 0.000578718 | 0.0202144 | -0.00103877 | -0.0045178 | -0.00413014 | -0.00418987 |
| 2 | 3000 | 0.0379723 | 0.00252413 | 0.00926424 | -0.00198853 | 0.016932 | 0.00292168 | -0.00164161 | 0.00014913 | -0.000346915 |
| 3 | 10 | 0.0235728 | 0.00505854 | 0.0261428 | 0.00206566 | -0.00341812 | 0.0100186 | -0.000739715 | 0.000700949 | -0.000394778 |
| 3 | 100 | 0.0217638 | 0.00354272 | 0.0261475 | 0.00449248 | 0.00126978 | 0.00504193 | 0.00303679 | 0.00527057 | 0.000271756 |
| 3 | 500 | 0.0140981 | -0.00336076 | 0.03271 | -0.00270491 | -0.00104233 | -0.00421479 | 0.0020091 | -0.00338528 | -2.17563e-05 |
| 3 | 2000 | 0.00691653 | 0.00165388 | 0.0412682 | -0.00251503 | 0.0242124 | 0.000651899 | 0.0066432 | 0.00147824 | -0.00176899 |
| 3 | 3000 | 0.0146863 | -0.000443038 | 0.0238066 | -0.00562104 | 0.0242464 | -0.00172508 | 0.00722745 | -0.00301028 | -0.00264003 |
| 4 | 10 | 0.000478639 | -0.00617089 | 0.0131883 | -0.0016432 | 0.00195965 | 0.00113805 | -0.00737619 | 0.0026784 | -0.00303441 |
| 4 | 100 | 0.00972389 | 0.000121044 | 0.0220997 | 0.00587184 | 0.0179949 | 0.00172073 | -0.00275435 | 0.00412144 | 0.0011879 |
| 4 | 500 | 0.00122152 | -0.00015269 | 0.040485 | -0.00306922 | 0.00178283 | -0.0055803 | 0.00156487 | 0.00827373 | -0.00141297 |
| 4 | 2000 | 0.0181472 | 0.00296123 | 0.0367911 | -0.00236353 | 0.0374363 | 0.000758703 | 0.00423418 | 0.00128362 | -0.000240506 |
| 4 | 3000 | 0.0100902 | 0.00016693 | 0.0328718 | -0.00334138 | 0.0357346 | -0.00278204 | 0.00618315 | -0.00350514 | -0.00021875 |
| 5 | 100 | 0.00752373 | 0.0017947 | 0.0173782 | 0.00543908 | 0.0133026 | 0.000648734 | 0.00092682 | 0.00538291 | 0.00401464 |
| 5 | 500 | 0.00701741 | 0.00278639 | 0.0260898 | 0.00236867 | 0.00186116 | -0.000625396 | 0.00134573 | 0.00262658 | 0.0038932 |
| 5 | 2000 | 0.00999525 | 0.00357358 | 0.0221131 | -9.96835e-05 | 0.0254976 | -0.000621044 | 0.00551661 | 0.00113845 | 0.00161709 |
| 5 | 3000 | 0.0133232 | 0.00134929 | 0.0141867 | 0.000437104 | 0.0257971 | 0.000507516 | 0.00599051 | -0.000575554 | 0.00163726 |
| 6 | 10 | -0.000420095 | -0.00445491 | 0.0264268 | -0.000803797 | -0.00551424 | -0.00145886 | 0.00097231 | 0.00359612 | 0.00215111 |
| 6 | 100 | 0.00335483 | 0.00167247 | 0.0263406 | 0.00137025 | 0.00472864 | -0.000197389 | 0.000399525 | 0.00292286 | 0.00232199 |
| 6 | 500 | 0.0025356 | -0.000113528 | 0.0341301 | -0.0013485 | -0.00250593 | 6.88291e-05 | -0.000801028 | -0.00243869 | 0.000757516 |
| 6 | 2000 | 0.00847191 | 0.00262975 | 0.0300439 | -0.000373418 | 0.0384015 | -0.00116021 | 0.00126266 | 0.00176978 | 0.000260285 |
| 6 | 3000 | 0.00781171 | 0.000700158 | 0.0159138 | -0.000619066 | 0.0271384 | 0.000300237 | 0.0046432 | -0.000147547 | -0.000870649 |
| 14 | 10 | -0.00214122 | -8.34652e-05 | 0.0184719 | 3.56013e-06 | -0.00101424 | 0.002839 | 0.000497627 | 0.000780459 | -0.000929984 |
| 14 | 100 | 0.00619778 | 0.00118434 | 0.0111119 | -0.00165229 | 0.000240111 | -0.00192919 | 0.000505142 | -0.000755934 | -0.00166377 |
| 14 | 500 | 0.00881487 | -0.000214399 | 0.00914755 | 0.000765032 | 0.0016337 | 0.00157674 | 0.00243275 | 0.00193157 | 0.00173101 |
| 14 | 2000 | 0.00695965 | 0.00242089 | 0.0210886 | 0.00204628 | 0.00352967 | 0.00211353 | 0.00168671 | 0.00155182 | 0.00170688 |
| 14 | 3000 | 0.0072231 | -0.000212025 | 0.0134078 | -0.000410601 | 0.00473536 | 9.61234e-05 | -9.88924e-05 | 0.000850079 | 0.00120134 |
| 15 | 10 | 0.00519264 | 0.00182002 | 0.0149213 | 0.00385008 | 0.00446915 | -0.000387658 | 0.00417761 | 0.00137777 | 0.00345965 |
| 15 | 100 | 0.00379945 | 0.0015621 | 0.0117492 | 0.000375791 | 0.0032587 | -0.00083663 | 0.0025712 | -0.00132358 | -0.00216416 |
| 15 | 500 | 0.0026871 | -0.000342563 | 0.00352532 | -0.00234019 | 0.000997231 | -0.00113449 | 0.00113014 | 0.000888054 | 0.00165585 |
| 15 | 2000 | 0.0064818 | 0.00210878 | 0.0252627 | -0.000471915 | 0.00176226 | 0.00157674 | 0.00151582 | 0.00271203 | 0.00136036 |
| 15 | 3000 | 0.00460166 | 0.000193038 | 0.0209308 | 0.000500791 | 0.00736946 | -4.94462e-05 | 0.000618671 | 0.000898339 | 0.00107437 |
| 27 | 10 | 0.00134889 | -0.00170926 | 0.0205502 | -0.000565269 | 0.00275514 | 0.00288291 | 0.00356725 | 0.00214082 | 0.00334335 |
| 27 | 100 | 0.00973339 | 0.00183544 | 0.0190044 | 0.0010534 | 0.0151638 | -0.00137619 | -0.00053481 | 0.00432793 | 0.00395411 |
| 27 | 500 | 0.00374644 | 0.00180301 | 0.0327294 | 0.000340585 | 0.0312623 | -0.000963212 | 0.00359652 | 0.00257002 | -0.000125791 |
| 27 | 2000 | 0.00663924 | 0.00247073 | 0.0447646 | -0.000566851 | 0.0321879 | -0.00478916 | 0.00286392 | 0.00172231 | -0.00281329 |
| 27 | 3000 | 0.00845016 | 0.00235641 | 0.031288 | 0.00115388 | 0.0345455 | 0.000355222 | 0.00934929 | 0.00241851 | 0.00253758 |
| 28 | 10 | 0.00504312 | -0.000779668 | 0.00325831 | 0.00219581 | 0.032589 | -0.00175 | 0.00672547 | 0.00714201 | 0.0060004 |
| 28 | 100 | 0.0142741 | 0.00339676 | 0.0171859 | -0.00248101 | 0.0100597 | 0.000239715 | -0.00133228 | 0.00250435 | -0.00195767 |
| 28 | 500 | 0.00604509 | 0.00780578 | 0.0240672 | 0.00435127 | 0.0181867 | 0.00254866 | 0.00515941 | 0.00510403 | 0.00123853 |
| 28 | 2000 | 0.00103521 | 0.0071159 | 0.0404134 | 0.0036519 | 0.0180142 | 0.00257081 | 2.41297e-05 | 0.00178679 | 0.0028212 |
| 28 | 3000 | 0.00105498 | 0.00570214 | 0.0414359 | 0.00171677 | 0.0204533 | -0.00418275 | -0.00122389 | 0.00181566 | 0.000992484 |

#### Qwen2.5-7B · FCI · RIDGE · fci_pyfci run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 10 | 0.00406429 | -0.00196907 | 0.0201298 | -0.000247939 | -0.00494694 | -0.00211898 | 0.00448282 | 0.000166009 | -0.00106563 |
| 4 | 10 | 0.00627626 | -0.00228353 | -0.000474403 | -0.00043494 | 0.00569131 | -0.00121203 | -0.00661149 | -0.000556949 | -0.00049343 |
| 5 | 10 | 0.00323402 | -0.00354542 | 0.00576641 | 9.16336e-05 | -0.00640069 | -0.00326806 | -0.00533694 | -0.00162694 | -2.17272e-07 |
| 15 | 10 | 0.00516552 | 0.00150627 | 0.0115091 | 0.00374281 | -0.00398783 | -0.00174003 | -0.00692063 | -0.00116315 | -0.00081965 |
| 27 | 10 | -0.00030973 | -0.00341891 | -0.000737849 | -0.00144398 | -0.00909103 | -0.00182907 | 0.00357407 | 0.000199707 | 0.00195543 |

#### Qwen2.5-7B · FCI_LOW_VS_HIGH · LOGREG · fci_pyfci run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.00864873 | 0.000589399 | 0.0293631 | -0.000255142 | 0.00359375 | -0.00747073 | -0.00506448 | 0.00256013 | -0.0019822 |
| 5 | 10 | 0.0122876 | -0.00119858 | 0.023665 | 0.00163568 | -0.00952334 | -0.004911 | -0.0020621 | 0.00158426 | 0.000705696 |

#### Qwen2.5-7B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | -0.00441473 | -0.000154866 | 0.00844501 | -0.00560253 | -0.00530968 | 0.00245373 | 0.00507303 | 0.000704726 | -0.00101285 |
| 1 | 100 | 0.00484383 | 0.00248106 | 0.0354335 | 0.00184764 | -0.00260236 | -0.00539014 | 0.00170356 | 0.000662979 | 0.000244298 |
| 2 | 10 | 0.0146121 | 0.00105821 | 0.0109185 | -0.00188596 | 0.00650286 | -0.00334884 | -0.00112952 | 0.00750217 | -0.000137899 |
| 2 | 100 | 0.00771141 | 0.00108196 | 0.0137934 | 0.00131968 | 0.00397958 | -0.0014889 | -0.000236458 | 0.00468193 | 0.000994262 |
| 2 | 500 | 0.0147034 | 0.00310114 | -0.0177373 | 0.00772998 | 0.0106709 | -0.000933804 | 0.00508547 | -0.000527579 | 0.000283409 |
| 2 | 2000 | 0.0024511 | -0.000703354 | 0.0118092 | -0.000435391 | -0.00584882 | -0.00314544 | 0.00366547 | -0.00345878 | -0.00304543 |
| 2 | 3000 | 2.98192e-05 | -0.000482485 | 0.0319344 | 0.0012621 | 0.00104108 | 0.000828244 | 0.00349039 | 0.0024323 | -6.27447e-05 |
| 3 | 100 | 0.000434315 | 0.00174023 | 0.0144446 | 0.00244655 | 0.00899461 | -0.000515197 | 0.000925289 | 0.004992 | 0.000533082 |
| 3 | 500 | 0.00275264 | -0.000652384 | 0.00898394 | 0.00612804 | 0.00145075 | -0.00131688 | 0.00904907 | -0.000422796 | 0.00138135 |
| 4 | 100 | 0.000312268 | -0.00143341 | 0.00754355 | 0.000934624 | 0.0154733 | 0.00507348 | 0.00502339 | 0.000824894 | -0.000642457 |
| 4 | 500 | 0.00771728 | -0.00314462 | 0.0232469 | 0.00453339 | 0.00444074 | 0.00504107 | -0.00455572 | 0.00322175 | 0.0010061 |
| 5 | 100 | 0.0134836 | -0.00136774 | 0.0155373 | 0.00137482 | 0.00761635 | -0.00319264 | 0.00768486 | 0.000185053 | -0.00156256 |
| 5 | 500 | 0.0217549 | 0.00236375 | 0.0398163 | -0.00209391 | -0.00234427 | 0.00185972 | 0.00201951 | 0.00416358 | -5.06244e-05 |
| 6 | 10 | 0.00212018 | -0.00181559 | 0.00339788 | -0.00115643 | 0.0111973 | -0.00156267 | -9.83378e-06 | 0.00101653 | 0.000708487 |
| 6 | 100 | 0.00474365 | 0.000857519 | 0.0257004 | 0.00318058 | 0.0148299 | 0.00242304 | 0.00713173 | 0.00542942 | 0.00130301 |
| 6 | 500 | 0.0214122 | -0.000972895 | 0.0585391 | -0.00505025 | -0.00206416 | 0.00282953 | 0.0015236 | 0.0013283 | -0.000294862 |
| 6 | 2000 | 0.0182973 | -0.00172409 | 0.0369376 | -0.000178962 | -0.0103743 | 0.00262361 | 0.00264942 | 0.00320001 | -0.000659027 |
| 14 | 10 | -0.00176005 | 0.00310183 | 0.0152662 | -0.00321925 | 0.00759091 | -0.00220459 | -0.00287133 | -0.000166095 | 0.00188602 |
| 14 | 100 | 0.020469 | 0.000714425 | 0.0259539 | 0.00671907 | 0.0149245 | 0.00205017 | 0.0155722 | 0.000905564 | 0.00010819 |
| 14 | 500 | 0.0130336 | 0.00040036 | 0.0124067 | 0.00261878 | 0.0178147 | -8.96236e-05 | 0.00657704 | 0.00268457 | -0.000124601 |
| 14 | 2000 | 0.0136615 | -0.000937207 | 0.0179271 | 0.0027096 | 0.0182574 | 0.000370928 | 0.0186895 | 0.0019829 | -0.000576008 |
| 14 | 3000 | 0.0100586 | 0.00028151 | 0.022822 | 0.00159677 | 0.0119317 | 0.00121503 | 0.0294634 | 0.00179315 | -0.00105541 |
| 15 | 10 | 0.0011113 | 0.00438231 | 0.0122597 | 0.00156965 | 0.00890118 | 0.00372329 | 0.000742222 | -0.00077883 | 0.00632713 |
| 15 | 100 | 0.0118966 | -0.00293379 | 0.012135 | 0.000321704 | 0.00707903 | -0.00146606 | 0.00959337 | -0.00209342 | -0.000128494 |
| 15 | 500 | 0.018413 | 0.000906404 | 0.0182259 | 0.000791371 | 0.0157937 | -0.00211543 | 0.0101142 | 0.00367467 | 0.000231177 |
| 15 | 2000 | 0.0051419 | -9.88132e-05 | 0.0219929 | 0.000682327 | 0.0133004 | -0.00104983 | 0.0188735 | 0.00167561 | -0.00090992 |
| 15 | 3000 | 0.00684561 | -0.00139122 | 0.0210016 | 0.00140258 | 0.00867049 | -0.0027055 | 0.0302324 | 0.00294175 | -0.000713635 |
| 27 | 10 | 0.0096305 | 0.0037332 | 0.00301131 | 0.00407644 | 0.00943134 | 0.00408217 | 0.0191006 | 0.000970956 | 0.00207205 |
| 27 | 100 | 0.0143209 | 0.00274313 | 0.0167519 | -0.000581089 | -0.00149008 | -0.000681612 | 0.0169397 | 0.0014278 | 0.00387064 |
| 27 | 500 | 0.0218963 | 0.00312568 | 0.0298971 | 0.00501369 | 0.0159174 | 0.001273 | 0.0124968 | 0.00279615 | 0.0028232 |
| 27 | 2000 | 0.0139333 | 0.00695871 | 0.00655678 | -7.3632e-05 | 0.0194567 | -0.00521865 | 0.00240644 | -0.000972122 | 0.000325355 |
| 27 | 3000 | 0.0113692 | 0.0077736 | -0.00925559 | 0.00179153 | 0.0123003 | -0.00350322 | -0.00559522 | -0.00351024 | 0.00118475 |
| 28 | 100 | 0.0127946 | 0.00676492 | 0.0191452 | -0.00128525 | -0.00190558 | 0.00147436 | -0.00474272 | 0.000230474 | 0.000119364 |
| 28 | 500 | 0.0115232 | -0.000992371 | 0.0148813 | 0.0009011 | 0.00960107 | -0.0037805 | 0.00705309 | 0.00200995 | -0.00370642 |
| 28 | 2000 | 0.0138821 | -0.000721138 | 0.0124318 | 0.00282706 | 0.0223849 | -0.00208176 | 0.0180476 | 0.00128458 | -0.00247297 |
| 28 | 3000 | 0.0201881 | 0.00240107 | 0.0208589 | 0.00503307 | 0.0118324 | 0.00221728 | 0.0201216 | 0.000339086 | 0.000436692 |

#### Qwen2.5-7B · ESS · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | -0.000252698 | -0.000322009 | 0.0623131 | 0.000270096 | 0.00485183 | 0.00197789 | -0.0024955 | 0.00306542 | 0.00138395 |
| 1 | 100 | -0.00193573 | 0.000322887 | 0.0370577 | -0.00242288 | -0.000871659 | 0.000217748 | -0.00181465 | -0.0019247 | -0.000161025 |
| 1 | 500 | 0.00107768 | 0.00148462 | 0.0405418 | -0.00157206 | 0.00244722 | -0.000301463 | 0.000443778 | 0.00220037 | 0.000340961 |
| 1 | 2000 | 0.0110399 | 0.00175731 | 0.0327043 | -0.00125845 | 0.00836429 | -0.000704312 | 0.00202368 | 0.0006431 | 0.00265686 |
| 1 | 3000 | 0.00686225 | 0.00223453 | 0.0149873 | -0.00086381 | 0.00821046 | -0.00194757 | 0.0035174 | -1.66725e-06 | 0.000466977 |
| 2 | 10 | 0.0139906 | -0.00291938 | 0.0270682 | 0.000124437 | 0.000677614 | 0.00244097 | -0.000681819 | -0.000195957 | -0.00110895 |
| 2 | 100 | 0.0172895 | -0.00123129 | 0.0393421 | 0.000956681 | 0.0016329 | 0.00130143 | -0.00040843 | 0.00191176 | 8.86258e-05 |
| 2 | 500 | 0.0260146 | 0.000408879 | 0.0290763 | 0.000561795 | 0.00518301 | -0.000490946 | -0.00215041 | 0.000833678 | -0.00118292 |
| 2 | 2000 | 0.0653949 | -0.000202803 | 0.0171014 | 0.000674484 | 0.0399456 | -0.00293702 | 0.00594783 | -0.000261702 | 0.00087602 |
| 2 | 3000 | 0.0959359 | 0.00336334 | 0.0115772 | -0.000105976 | 0.0475807 | -0.00236256 | 0.0107903 | 0.00062194 | 0.00121772 |
| 3 | 10 | 0.00817293 | 0.000221923 | 0.0297086 | -0.000528057 | 0.00438446 | 0.00468564 | -0.00257097 | 0.00143229 | 0.000928085 |
| 3 | 100 | 0.0136631 | 0.00220798 | 0.0353581 | 0.00185538 | 0.00500482 | 0.00222752 | 0.00108525 | 0.00300646 | -0.00130107 |
| 3 | 500 | 0.00596007 | 0.00215075 | 0.0428103 | 0.00202385 | 0.00217861 | 0.00310283 | 0.00353 | 0.0016912 | -0.000730825 |
| 3 | 2000 | 0.0162523 | 0.0027656 | 0.0468552 | 0.000718619 | 0.0372416 | -0.000214948 | -0.00276681 | 0.00304446 | 0.001532 |
| 3 | 3000 | 0.0264584 | 0.0014913 | 0.0819148 | -0.000393675 | 0.0664482 | -0.00162641 | 0.0128249 | -0.000421365 | -0.00156811 |
| 4 | 10 | 0.00122016 | 0.000938531 | 0.0189141 | 0.000285845 | 0.00945074 | 0.000259778 | 0.00473812 | 0.0045066 | 0.00487704 |
| 4 | 100 | 0.00529859 | -0.000124174 | 0.0238856 | 0.00216275 | 0.00396057 | -0.00113731 | 0.000911996 | 0.0056802 | -0.000512536 |
| 4 | 500 | 0.00194493 | 0.000664121 | 0.034271 | 0.000269166 | 0.00708575 | 0.00157614 | 0.000528553 | 0.00263572 | -0.000187762 |
| 4 | 2000 | 0.00933489 | 0.00264853 | 0.0531148 | -0.00128284 | 0.0848738 | -0.00348873 | 0.00845765 | 0.00184268 | -0.000769677 |
| 4 | 3000 | 0.0157876 | 0.00665838 | 0.0418978 | -0.00179273 | 0.0849753 | -0.00302225 | 0.00746503 | -0.00125507 | 0.000322638 |
| 5 | 10 | 0.00577347 | 0.00222312 | 0.0177398 | 0.000650769 | 0.00201984 | 0.00309716 | 0.000894457 | 0.00327261 | 0.00682048 |
| 5 | 100 | 0.0016318 | 0.000387907 | 0.0221247 | 0.000917049 | 0.00892563 | -0.00155698 | 0.0111884 | 0.00208911 | 0.00394439 |
| 5 | 500 | 0.00694706 | 0.000869855 | 0.0398613 | 0.000148255 | 0.0181122 | -0.00173464 | 0.00418441 | 0.00139104 | 0.00212082 |
| 5 | 2000 | 0.0164586 | 0.00121553 | 0.032957 | -0.000679891 | 0.0639204 | -0.00461948 | 0.00700094 | 0.00304446 | 7.89306e-06 |
| 5 | 3000 | 0.0152944 | 0.00045906 | 0.0181111 | -0.000158581 | 0.0601101 | -0.00372171 | 0.00706827 | -0.000147568 | -0.000646978 |
| 6 | 10 | -0.0033839 | 0.000766474 | 0.0455718 | -0.00146428 | 0.0027449 | 0.000896726 | 0.00733067 | 0.00226578 | -0.00124411 |
| 6 | 100 | 0.00265067 | 0.000928218 | 0.0320831 | -0.00251096 | 0.00713561 | 0.000795795 | 0.0075169 | -0.0010708 | -0.000818183 |
| 6 | 500 | 0.00601542 | -0.00083909 | 0.0664401 | -0.00366317 | 0.00657976 | -0.00335853 | 0.00942285 | 0.000924619 | 0.00204864 |
| 6 | 2000 | 0.0212121 | 0.00130465 | 0.0750323 | -0.00179297 | 0.0455354 | -0.00222883 | 0.00528476 | -0.000683264 | 0.00191332 |
| 6 | 3000 | 0.0277056 | 0.00370161 | 0.0730742 | -0.000399903 | 0.0488417 | -0.00149825 | 0.00746465 | 0.000844726 | 0.00116075 |
| 14 | 10 | 0.00134402 | 0.000301384 | 0.0226254 | 0.00177339 | 0.00106235 | -0.000595201 | 0.00411645 | -0.00125497 | 1.56614e-05 |
| 14 | 100 | 0.00486122 | -0.00102021 | 0.029695 | 0.000184128 | 0.00333303 | 0.00166176 | 0.00473988 | -0.00043638 | 0.00014535 |
| 14 | 500 | 0.0202396 | 0.00130541 | 0.0399402 | -0.000512394 | 0.00381282 | -0.00140745 | 0.0096427 | 0.00134961 | 0.00444954 |
| 14 | 2000 | 0.028117 | 0.000164139 | 0.0687889 | -0.00198871 | 0.0208415 | -0.0013531 | 0.00306126 | -0.000789449 | -0.00188856 |
| 14 | 3000 | 0.0324664 | 0.00100864 | 0.0714976 | -0.000767835 | 0.0244049 | -0.00200702 | 0.00467902 | 0.000198418 | -0.00115994 |
| 15 | 10 | -0.000317935 | 0.00140677 | 0.0225917 | -0.00233896 | 0.00321143 | -0.00222667 | -0.00370958 | -0.0015744 | -0.00244926 |
| 15 | 100 | 0.00868299 | 0.00121643 | 0.0259265 | 0.000469734 | 0.00215136 | 0.000404964 | 0.00808612 | -0.000427785 | 0.00279706 |
| 15 | 500 | 0.0153364 | 0.000636991 | 0.0356399 | -0.00131822 | 0.0001389 | -0.00116531 | 0.00726287 | 0.000415274 | 0.00183608 |
| 15 | 2000 | 0.0215125 | 0.000258831 | 0.0869365 | 0.00081911 | 0.0132175 | 0.00188921 | 0.00473357 | -0.000452974 | -0.0010136 |
| 15 | 3000 | 0.0280602 | 0.000173013 | 0.089449 | -0.00037213 | 0.025359 | 3.24281e-05 | 0.00812264 | -0.00105083 | -0.000746967 |
| 27 | 10 | 0.000818004 | 0.0035971 | 0.0277764 | -0.00178263 | 0.00454759 | 0.00526576 | -0.00535904 | -0.000139612 | 0.00279026 |
| 27 | 100 | 0.00915804 | 0.00711223 | 0.0225261 | 0.0021605 | 0.012235 | 0.00263141 | 0.00910917 | 0.000295618 | 0.00265639 |
| 27 | 500 | 0.00881429 | 0.00159212 | 0.0610261 | 0.00177177 | 0.0593086 | -0.00126886 | 0.00204245 | 0.000985096 | 0.00320073 |
| 27 | 2000 | 0.00674438 | -6.83204e-05 | 0.0970637 | 0.000843014 | 0.0793666 | -0.00149886 | 0.00202 | -0.00093457 | -0.000914231 |
| 27 | 3000 | 0.0108409 | 0.0016484 | 0.102588 | 0.0035056 | 0.102486 | -0.000976807 | 0.010754 | 0.00348552 | 0.000352751 |
| 28 | 10 | -0.000381781 | 0.0019886 | 0.0117528 | -0.000416231 | 0.0062463 | -0.00322269 | -4.47999e-06 | 0.00122745 | -0.00213446 |
| 28 | 100 | -8.65703e-05 | 0.00532437 | 0.0238438 | 0.0015127 | 0.00976899 | -0.00221852 | 0.00108381 | -0.00220874 | 5.74325e-05 |
| 28 | 500 | -0.000116382 | 0.000858912 | 0.036756 | 0.000879787 | 0.0166158 | -0.00383375 | -0.00806605 | -0.00121785 | -0.000536887 |
| 28 | 2000 | 0.00576236 | 0.00170093 | 0.067606 | 0.000392927 | 0.0469389 | -0.00218095 | -0.000431726 | 0.00323919 | -0.00131607 |
| 28 | 3000 | 0.000178892 | 0.00163249 | 0.0729504 | -0.000151042 | 0.0551011 | -0.00354757 | 8.91872e-05 | -0.00113994 | -0.00130798 |

#### Qwen2.5-7B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | -0.00335799 | -0.00527492 | 0.0548461 | -0.00895767 | -0.00210601 | 0.00649763 | -0.00323259 | 0.000623418 | -0.00415902 |
| 1 | 100 | 0.00808544 | 0.00472903 | 0.0479039 | 0.000922073 | 0.00258267 | 0.000846915 | 0.00165111 | 0.00678165 | -0.00225554 |
| 1 | 500 | 0.0147065 | -0.00664913 | 0.0300158 | -0.00702136 | -0.00627176 | -0.00389359 | -0.000841772 | -0.00931448 | -0.00808742 |
| 1 | 2000 | 0.0161527 | -0.000759098 | 0.0205182 | -0.00186076 | 0.00556487 | -0.00277373 | -0.00392801 | -0.00455934 | -0.00918078 |
| 1 | 3000 | 0.0287615 | 0.00842445 | 0.021409 | 0.00166179 | 0.00288568 | -1.10759e-05 | 0.00290744 | 0.00117405 | -0.00322231 |
| 2 | 10 | 0.0216669 | -0.000351661 | 0.034182 | 0.0035178 | -0.00300712 | -0.00182832 | 0.00539359 | 0.00274684 | 0.00148418 |
| 2 | 100 | 0.0187168 | -0.00239913 | 0.0140368 | -0.00153441 | 0.00372271 | -0.00205222 | -0.00279312 | 0.00857951 | -0.00427729 |
| 2 | 500 | 0.0193877 | 0.00546835 | 0.0112987 | -0.0015004 | 0.0100376 | -0.00267603 | -0.000162579 | 0.00010087 | -0.00191535 |
| 2 | 2000 | 0.0235392 | 0.00356408 | 0.0204854 | 0.000528085 | 0.0119225 | 0.00389913 | 0.00773853 | 0.00542682 | 0.00511946 |
| 2 | 3000 | 0.0170146 | -0.00334217 | 0.0272563 | -0.00280696 | -0.00135878 | 0.00959256 | 0.00313884 | 0.00103481 | 0.00094106 |
| 3 | 10 | 0.00271559 | 0.00323774 | 0.0345969 | -0.003214 | -0.000338608 | -0.000863528 | -0.00327294 | -0.00700475 | -0.00425831 |
| 3 | 100 | 0.00418078 | -0.00202334 | 0.0289494 | -0.00280854 | 0.0147021 | 0.000988924 | 0.0016515 | 0.000947389 | 0.00278244 |
| 3 | 500 | 0.0133983 | 0.00484217 | 0.0416709 | 0.0050629 | 0.0148746 | 0.00255024 | 0.00432516 | 0.00414399 | 0.00381725 |
| 3 | 2000 | 0.0153323 | -0.00102373 | 0.00968078 | -0.000630142 | 0.0198453 | 7.91139e-07 | 0.00375158 | 0.00231013 | -0.00166891 |
| 3 | 3000 | 0.0117025 | 0.00150198 | 0.0208912 | -0.000165744 | 0.00993987 | 0.000662975 | 0.00291218 | 0.00257476 | 0.00214003 |
| 4 | 10 | 0.000210047 | -0.00240941 | 0.0175661 | -0.00627176 | 0.00499486 | -0.000459652 | 0.000304589 | -8.58386e-05 | -0.00258307 |
| 4 | 100 | 0.00115269 | -0.00794739 | 0.00141614 | -0.00348536 | -0.00489359 | -0.00662263 | -0.00126108 | -0.00204589 | -0.0116831 |
| 4 | 500 | 0.00914122 | 0.00168671 | 0.0271638 | -0.00372706 | 0.0305716 | -0.00706725 | 0.00448339 | 0.00587896 | 0.00261986 |
| 4 | 2000 | 0.00432793 | 0.000569225 | 0.0189775 | -0.00144343 | 0.00583821 | -0.00520609 | 0.000440269 | -0.002625 | -0.00253204 |
| 4 | 3000 | 0.00613252 | -0.000369858 | 0.0282282 | -0.0013837 | 0.00784256 | 0.00114399 | 0.0055894 | 0.00356685 | 0.00333861 |
| 5 | 10 | -0.00536551 | -0.00766653 | 0.0067682 | 0.00212421 | 0.00222271 | -0.00316258 | -0.00557397 | -0.00893275 | 0.00415309 |
| 5 | 100 | 0.00332951 | -0.00505419 | 0.00274011 | 0.00896598 | 0.0131294 | -0.00430498 | 0.0107472 | 0.00427927 | -0.000951741 |
| 5 | 500 | -0.00281052 | -0.00216258 | 0.0335609 | -0.00527809 | 0.0137441 | -0.000861551 | -0.00287144 | 0.00223813 | -0.00107041 |
| 5 | 2000 | 0.006714 | 0.00107872 | 0.021748 | -0.000131329 | 0.0101436 | -0.00299604 | 0.00548892 | -0.00303441 | 0.00299288 |
| 5 | 3000 | 0.0114984 | 0.00103521 | 0.0220843 | 0.0026693 | 0.00894422 | 0.00234612 | 0.00517801 | 0.00379905 | 0.00180934 |
| 6 | 10 | 0.00716297 | 0.00718513 | 0.0113323 | 0.00485759 | 0.0102769 | 0.00480617 | 0.0037769 | 0.00414794 | 0.00588528 |
| 6 | 100 | 0.00597547 | 0.00245926 | 0.0103141 | 0.00118671 | 0.00892405 | 0.00209454 | 0.0125194 | 0.00132318 | 0.003625 |
| 6 | 500 | 0.00956606 | 0.00149684 | 0.0336594 | 0.000130934 | 0.0167725 | 0.000229035 | 0.00827769 | 0.00516297 | 0.00251384 |
| 6 | 2000 | 0.00512698 | -0.00141614 | 0.0191301 | -0.00646559 | 0.0124339 | -0.000508307 | -0.000176028 | -0.0042409 | 0.00133228 |
| 6 | 3000 | 0.0161317 | 0.000827927 | 0.00919027 | 0.00174407 | 0.0138817 | -0.000797864 | 0.00504826 | 0.00607476 | 0.000532041 |
| 14 | 10 | -0.00325316 | 0.00317682 | 0.0210233 | 0.00364122 | 0.00727492 | -0.00106922 | -0.000899525 | -0.00227967 | 0.00489003 |
| 14 | 100 | 0.00297508 | 0.000754747 | 0.00699367 | 0.00447587 | 0.00660364 | -0.000963608 | 0.00404589 | 0.00053837 | 0.000934335 |
| 14 | 500 | 0.00785127 | -0.000901108 | 0.00650712 | -0.00307793 | 0.00785918 | -0.00143671 | 0.00382437 | 0.0024553 | -0.00394146 |
| 14 | 2000 | 0.0100356 | -0.000965585 | 0.0104929 | -0.00117128 | 0.0108414 | 0.00203046 | 0.0070894 | 0.00212302 | 0.000151503 |
| 14 | 3000 | 0.010129 | 0.00175554 | 0.0118608 | 0.00235799 | 0.0140922 | -0.00112579 | 0.00559771 | 0.00349051 | 0.000564873 |
| 15 | 10 | -0.0018121 | 0.00765309 | 0.0210775 | 0.00267168 | 0.00419976 | 0.0074644 | -0.000548259 | 0.00112737 | 0.012657 |
| 15 | 100 | 0.0027587 | -0.000890427 | 0.00125316 | -0.000174842 | 0.00125672 | -0.00522706 | 0.00551424 | -0.000907041 | 0.000212025 |
| 15 | 500 | 0.00906883 | -0.000742484 | 0.0203489 | -0.00372033 | 0.0066784 | 0.00165902 | 0.00454668 | 0.000122627 | -0.00100514 |
| 15 | 2000 | 0.0110059 | 4.31171e-05 | 0.0174941 | 0.00157753 | 0.0145285 | 0.001375 | 0.0100854 | 0.00372785 | 0.00394264 |
| 15 | 3000 | 0.00877848 | -0.00156646 | 0.0109292 | -0.000251978 | 0.0126748 | -0.00308307 | 0.00392722 | 0.00112935 | 0.000818829 |
| 27 | 10 | 0.00753402 | 0.0114873 | 0.00863568 | 0.00347073 | 0.0109066 | 0.00799842 | 0.00202927 | 0.00491218 | 0.00854747 |
| 27 | 100 | 0.0144035 | 0.00819976 | 0.0124482 | -0.00335008 | -0.000214003 | 0.00124723 | 0.00406764 | 0.00932239 | 0.00509771 |
| 27 | 500 | 0.0127567 | 0.00400119 | 0.0473877 | 0.00138766 | 0.0164157 | -0.00108307 | -0.000824763 | 0.00314597 | -0.00275158 |
| 27 | 2000 | 0.0057587 | -0.00348853 | 0.0246317 | -0.00666337 | 0.0177191 | -0.00218473 | -0.000589794 | 6.44778e-05 | -0.00688133 |
| 27 | 3000 | 0.00711986 | -0.00212065 | 0.0197397 | -0.000860364 | 0.0175538 | -0.00300475 | 0.00206962 | 0.000424446 | -0.00220767 |
| 28 | 10 | 0.0153465 | 0.0132002 | 0.0216772 | 0.0116784 | 0.00911788 | 0.00319858 | 0.00893434 | 0.00967128 | 0.0158869 |
| 28 | 100 | 0.0166456 | 0.00477927 | 0.0177563 | 0.00108979 | 0.00492682 | -0.00142009 | -0.000833861 | -0.0030712 | -0.00445688 |
| 28 | 500 | 0.0127892 | 0.00489597 | 0.0382832 | 0.00221638 | 0.021178 | 0.0070265 | 0.0105665 | 0.00475435 | 0.00255696 |
| 28 | 2000 | 0.00820886 | 0.00270609 | 0.0269771 | 0.00188924 | 0.0272496 | 0.00281566 | 0.00812856 | 0.00378362 | 0.00378797 |
| 28 | 3000 | 0.00492998 | 0.000365902 | 0.0158291 | -0.00049288 | 0.0201744 | -0.000288766 | 0.00488647 | 0.000766614 | -0.00126424 |

#### Qwen2.5-7B · ESS_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | -0.00178521 | 0.00514597 | 0.0372243 | -0.00457476 | 0.0103999 | 0.00838014 | -0.000354826 | 0.00602453 | 0.00421361 |
| 1 | 100 | 0.00710483 | 0.00285364 | 0.0350989 | 0.00264201 | 0.00653877 | 0.00404509 | 0.00181566 | 0.00420411 | 0.00240309 |
| 1 | 500 | 0.0125111 | 0.00239359 | 0.0141725 | 0.000396361 | 0.0026693 | -0.0062235 | 0.00225356 | -0.00555538 | 0.000396756 |
| 1 | 2000 | 0.01493 | -0.000142405 | 0.010693 | -0.00524684 | 0.00986709 | -0.00254153 | -5.4193e-05 | -0.00170965 | -0.0040004 |
| 1 | 3000 | 0.0103002 | 0.00385364 | 0.0213018 | -0.00412421 | 0.00795847 | 0.00120293 | -0.002125 | -0.000568434 | -0.00120332 |
| 2 | 10 | 0.0130878 | -0.00408742 | 0.0331123 | 0.00181013 | -0.002375 | 0.0015803 | -0.00162896 | 0.0066784 | -0.00248339 |
| 2 | 100 | 0.0235107 | 0.000688687 | 0.0339015 | 0.00494502 | -0.00082318 | 9.33544e-05 | 0.00209375 | 0.00546559 | -0.00120411 |
| 2 | 500 | 0.0312112 | -0.00332595 | 0.0196155 | -0.00290229 | -0.00138133 | -0.00587381 | -0.00152571 | 0.000691851 | -0.00259335 |
| 2 | 2000 | 0.0337294 | 0.00378758 | 0.0147915 | 0.00363528 | 0.0155878 | 0.00210562 | 0.00240744 | 0.00378718 | 0.00639715 |
| 2 | 3000 | 0.0316412 | 0.0035981 | 0.0146286 | 0.00206566 | 0.0111626 | 0.000495649 | 0.00163172 | 0.00123101 | -0.000143196 |
| 3 | 10 | 0.00172627 | -0.00253046 | 0.0117191 | -0.00172824 | -0.00245055 | 0.00617603 | -0.00444897 | 0.00448062 | -0.00220174 |
| 3 | 100 | 0.0242975 | -0.00119858 | 0.03371 | -0.00132081 | -0.00149328 | -0.00247389 | -0.00202809 | 0.00649328 | 0.00499248 |
| 3 | 500 | 0.00825989 | 0.000473101 | 0.0398042 | 0.00184533 | 0.00321717 | 0.00328125 | -0.000213608 | 0.00477967 | 0.00041337 |
| 3 | 2000 | 0.00838568 | -9.0981e-06 | 0.0266737 | -0.00178679 | 0.0166309 | -0.00485799 | 0.00189161 | 7.91139e-05 | -0.00115665 |
| 3 | 3000 | 0.00646321 | 0.00197706 | 0.0331796 | -0.00243275 | 0.0214442 | -0.00110047 | -0.00304589 | -0.000286392 | -0.00108188 |
| 4 | 10 | 0.00832555 | 0.000195807 | 0.0255728 | -0.000640823 | 0.0107607 | -0.000914953 | -0.00231843 | 0.00727611 | -0.00725672 |
| 4 | 100 | 0.0071966 | 0.000461234 | 0.0239976 | 0.00317326 | 0.00174407 | 0.00037144 | 0.0100289 | 0.0088129 | 0.000437104 |
| 4 | 500 | 0.00416851 | 0.00342168 | 0.047483 | -0.00401464 | 0.00153362 | 0.000284415 | -0.00124842 | 0.00706052 | -0.00119818 |
| 4 | 2000 | 0.00742128 | 0.00215467 | 0.0329672 | -0.00182753 | 0.0351377 | -0.00203046 | 0.000323972 | -0.000397152 | 0.000854035 |
| 4 | 3000 | 0.0083572 | 4.46994e-05 | 0.0273995 | -0.00245134 | 0.0277061 | -0.00147824 | -0.00153085 | -0.00159335 | -0.00164161 |
| 5 | 10 | 0.00224525 | -0.00536313 | 0.0126634 | 0.000426424 | -0.000231804 | 0.00154351 | -0.0028303 | -0.000296282 | -0.00142682 |
| 5 | 100 | -0.00267642 | -0.00404193 | 0.0223085 | -0.00106487 | -0.00162777 | -0.00571084 | -0.00284415 | -0.00587816 | -0.000902294 |
| 5 | 500 | 0.00150396 | 9.0981e-06 | 0.0157801 | 0.00068038 | 0.004089 | -0.00150831 | -0.00151266 | 0.00128758 | -0.000960047 |
| 5 | 2000 | 0.0104391 | 1.54272e-05 | 0.0208295 | -0.000456487 | 0.0343244 | -0.000903877 | 0.00324763 | -0.00218908 | -0.000548259 |
| 5 | 3000 | 0.00822706 | -0.000883703 | 0.0153944 | 3.48101e-05 | 0.0294055 | 6.32911e-05 | 0.000270174 | -0.00242247 | -0.00179628 |
| 6 | 10 | -0.00415625 | -0.00252927 | 0.0243192 | -0.0016606 | -0.00111234 | -0.000490902 | 0.00908584 | -0.00146796 | -0.000297468 |
| 6 | 100 | 0.00104945 | 2.13608e-05 | 0.0213038 | 0.0039822 | 0.00200079 | -0.00219304 | -0.000196203 | 0.00106764 | 0.000687104 |
| 6 | 500 | 0.0044288 | -0.000810522 | 0.0333418 | -0.000807753 | -0.00174051 | -0.0038129 | -0.000849288 | 0.00135799 | -0.00109652 |
| 6 | 2000 | 0.00978323 | -0.00209889 | 0.0239233 | -0.00116139 | 0.0133414 | -0.00116812 | -0.000161788 | -0.000288766 | -0.000399921 |
| 6 | 3000 | 0.0107725 | -0.00126068 | 0.0159632 | -0.0010712 | 0.00791535 | -0.00116021 | 0.00105657 | -0.000136867 | -0.00135483 |
| 14 | 10 | 0.00770451 | 0.00843117 | 0.0290775 | 0.00660206 | 0.00237223 | 0.00897468 | 0.00693157 | 0.00685206 | 0.00517563 |
| 14 | 100 | 0.00437263 | 0.000908228 | 0.0113746 | 0.00071519 | -0.00207397 | -0.000196598 | -0.00053481 | -0.000880142 | -0.000208465 |
| 14 | 500 | 0.00736234 | 0.000630142 | 0.0071693 | 3.32278e-05 | 0.000814478 | 0.000192642 | 0.000308149 | -0.000613528 | 0.0011254 |
| 14 | 2000 | 0.0037856 | 2.45253e-05 | 0.0173339 | -0.000820016 | -0.000945411 | -0.000192247 | 0.000804589 | -0.00044462 | -0.000287184 |
| 14 | 3000 | 0.00423101 | 5.85443e-05 | 0.0089553 | -0.000567642 | 0.000850079 | 0.000124209 | 0.000501978 | 0.000349288 | 0.000440665 |
| 15 | 10 | 0.000134494 | 0.000744858 | 0.0198592 | 0.00142128 | 0.000358782 | 0.0012409 | 0.00410799 | 0.000549842 | 0.00121835 |
| 15 | 100 | 0.00293473 | 0.00034731 | 0.0106392 | 0.00219581 | -0.00387263 | -0.00126305 | 0.00169106 | -0.000345728 | -0.00219502 |
| 15 | 500 | 0.00312698 | -0.00267801 | 0.0064371 | -0.00371677 | -0.0035625 | -0.00279589 | 0.0035178 | -0.00172983 | -0.00163133 |
| 15 | 2000 | 0.00675237 | 0.00116179 | 0.0152445 | 0.000411392 | 0.000690665 | 0.00210918 | 0.00284256 | 0.00123299 | 0.00145134 |
| 15 | 3000 | 0.00607555 | 0.000723497 | 0.0124407 | 0.00056606 | 0.00125989 | 0.00065981 | 0.00170095 | 0.00116693 | 0.00106804 |
| 27 | 10 | 0.00511076 | -0.000765032 | 0.0131555 | -0.00150237 | 0.00668908 | 0.00182951 | 0.0110941 | 0.0004375 | 0.00343434 |
| 27 | 100 | -0.00168315 | 0.00395609 | 0.0120827 | -0.00147191 | -0.00208742 | 0.00256566 | 0.00193552 | -0.00335285 | 0.00368908 |
| 27 | 500 | 0.00788093 | 0.00644027 | 0.0329743 | -0.000392801 | 0.0209996 | 0.000695016 | 0.00238884 | 0.00326147 | 0.0016879 |
| 27 | 2000 | 0.00809573 | -0.000363133 | 0.0426764 | 0.00222666 | 0.0359996 | 0.00146756 | 0.00649565 | 0.00321123 | 0.0013038 |
| 27 | 3000 | 0.0105566 | 0.00162896 | 0.0329415 | 0.00147112 | 0.0362563 | 0.00189597 | 0.00585364 | 0.00311907 | 0.00161669 |
| 28 | 100 | 0.013765 | -0.00101978 | 0.011193 | -0.0057856 | 0.0127623 | -0.00760562 | 0.00519541 | 0.00152729 | -0.000169699 |
| 28 | 500 | 0.00331171 | -0.0028129 | 0.0227144 | -0.00135918 | 0.0149917 | -0.00119502 | -0.00573101 | -0.00330815 | -0.00396915 |
| 28 | 2000 | 0.0039822 | -0.000753956 | 0.0456495 | 0.00151226 | 0.0125665 | -0.00214241 | 0.000391218 | 0.000490111 | -0.00139161 |
| 28 | 3000 | 0.00539122 | 0.00139122 | 0.0453912 | 0.00116733 | 0.0173936 | 0.000488924 | 0.00511709 | 0.00290783 | 0.00307872 |

#### Qwen2.5-7B · MLE · RIDGE · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.000937063 | 0.0169447 | 0.00870661 | -0.00125037 | -0.00317274 | -0.00318464 | -0.00603374 | -0.0032057 | -0.0013223 |
| 1 | 2000 | 0.00258286 | 0.0154847 | 0.00798261 | -0.00110247 | -0.0107017 | -0.00260995 | -0.0075537 | -3.47536e-05 | -0.0042877 |
| 1 | 3000 | 7.13757e-05 | 0.0105107 | 0.0131431 | -0.000742574 | -0.0121045 | -0.00285557 | -0.00706568 | 0.000315547 | -0.00459998 |
| 3 | 10 | -0.000799483 | -0.00135446 | 0.00641186 | -2.29881e-05 | -0.00543728 | -0.00394764 | -0.00525469 | -0.00168927 | -0.00394608 |
| 3 | 2000 | -0.0043881 | -0.00377887 | 0.0299108 | -0.000120876 | 0.00300473 | 0.00233443 | 0.00669568 | -0.000314579 | -0.00137873 |
| 3 | 3000 | -0.00318241 | -0.00327095 | 0.0374642 | -0.000495277 | -0.00116351 | 0.00369961 | 0.00832883 | -0.00106525 | -0.00136026 |
| 4 | 10 | -0.00786242 | -0.00412404 | -0.0020571 | -0.000539106 | -0.00922747 | -0.000640816 | -0.00922966 | 0.0025938 | -0.00325971 |
| 4 | 2000 | -0.00189073 | -0.00542463 | 0.039861 | -0.000906266 | 0.00512603 | 0.00461592 | 0.0195009 | -0.000853631 | 3.18289e-05 |
| 4 | 3000 | -0.00107669 | -0.00271291 | 0.0483001 | -0.00103576 | 0.0039816 | 0.00551106 | 0.0196994 | -0.0012775 | 7.44502e-05 |
| 5 | 10 | -0.0052318 | -0.00493655 | -0.00633683 | -0.000662236 | -0.0107547 | -0.0011478 | -0.00359562 | -0.00032891 | -0.00233666 |
| 5 | 2000 | -0.000578431 | -0.00158839 | 0.0368561 | -0.000510194 | 0.0130305 | 0.00367301 | 0.0177684 | -0.000888324 | 0.000439819 |
| 5 | 3000 | 0.000572599 | 0.000478545 | 0.0413655 | -0.000886352 | 0.0114364 | 0.00459963 | 0.0174577 | -0.00123787 | 0.000575476 |
| 6 | 3000 | -0.00054689 | -0.00185359 | 0.0445147 | -5.11955e-05 | 0.0159529 | 0.00262025 | 0.0189344 | -0.00134642 | -8.17893e-05 |
| 28 | 10 | -0.000700271 | 0.000266686 | -0.00944592 | 8.10849e-05 | -0.0109588 | -0.00203534 | -0.00579366 | -0.00346282 | 0.00132423 |

#### Qwen2.5-7B · ESS_LOW_VS_HIGH · LOGREG · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 10 | 0.00527809 | -0.00308861 | -0.0104846 | -0.000126582 | 0.0380581 | -0.00219937 | -0.00294937 | -0.00224565 | 0.00496203 |

#### Apertus-8B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.0395616 | -0.00161441 | 0.0180394 | -0.00203138 | -0.00274822 | -0.00146658 | 0.00741457 | 0.00517302 | 0.000475655 |
| 16 | 1000 | 0.037482 | 0.000138904 | 0.0341321 | -0.00113336 | 0.0163172 | -0.00529475 | 0.0180247 | 0.001516 | -0.000304768 |
| 31 | 1000 | 0.0227724 | 0.00182995 | 0.0166303 | -0.00176849 | 0.00831932 | 0.00089947 | 0.0105539 | -0.000534725 | 0.000962415 |

#### Apertus-8B · ESS · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.0929364 | -0.000729376 | 0.0118039 | -0.000383945 | 0.00139917 | 0.00526828 | 0.00359416 | -0.00103661 | 0.00103685 |
| 16 | 1000 | 0.0405929 | -0.000813047 | 0.0511928 | -0.000810999 | 0.00899229 | -0.00104208 | 0.00686482 | 0.00156056 | -0.00350118 |
| 31 | 1000 | 0.0447337 | 0.0029661 | 0.0506988 | -0.00128525 | 0.028824 | -0.000781096 | 0.0162864 | -0.00238012 | -0.00135843 |

#### Apertus-8B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.0308006 | -0.000526108 | 0.031322 | 0.00173536 | -1.22627e-05 | 0.00202373 | 0.00201899 | -0.000370649 | -0.000287975 |
| 16 | 1000 | 0.0168991 | -0.00127848 | 0.0267108 | -0.00219066 | 0.00392682 | -0.00158821 | 0.0080538 | -0.00080182 | -0.000473497 |
| 31 | 1000 | 0.0165518 | -0.00202729 | 0.042854 | -0.0013216 | 0.00875514 | -0.00451938 | 0.00471479 | -0.00845055 | -0.00478006 |

#### Apertus-8B · ESS_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.0408481 | 0.0022678 | 0.0144217 | 0.00217366 | 0.000893987 | 0.00317326 | 0.00262381 | 0.00360127 | 0.00216535 |
| 16 | 1000 | 0.00979351 | -0.000530063 | 0.0128695 | 0.000119066 | 0.000345332 | -0.000469146 | 0.00300712 | -6.36867e-05 | -0.000630934 |
| 31 | 1000 | 0.0151926 | 0.00143434 | 0.0461503 | 0.00265071 | 0.000888054 | -0.00233109 | 0.0072765 | -0.000177611 | -0.000419304 |

### Grouped held-out permutation importance across available settings

Mean held-out score decrease when all features in a family are shuffled together. All archived settings and all nine families are displayed. Scores are R² for regression and ROC-AUC for low/high classification; fold variability and family sizes are in the CSV.

[Download the CSV](tables/grouped_permutation.csv)

Family columns: Surface = `raw_text`; Frequency = `lexical_frequency`; UPOS = `upos_distribution`; Lexical = `lexical`; Predicate = `verbal_predicate_structure`; Tree = `parse_tree_structure`; Relations = `syntactic_relations`; Subordination = `subordination`; Verb edges = `verbal_edge_structure`.

#### Pythia-1.4B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.0195289 | 0.00445632 | 0.096876 | 0.000569627 | 0.00830649 | 0.00509709 | 0.0170153 | 0.000887878 | 0.00093621 |
| 1 | 1000 | 0.017936 | 0.00133917 | 0.0721433 | 0.00262598 | 0.00696693 | 0.0036481 | 0.020248 | 0.00114522 | 0.00233705 |
| 2 | 500 | 0.105905 | 0.00313956 | 0.0382502 | 0.00299251 | 0.00672353 | 0.000808886 | 0.00852743 | 0.00129488 | 0.00225645 |
| 2 | 1000 | 0.111411 | 0.00143633 | 0.104144 | 0.0110801 | 0.0173546 | 0.00345956 | 0.0257834 | 0.000382194 | 0.000294351 |
| 12 | 500 | 0.120233 | -0.000173467 | 0.102563 | 0.0116022 | 0.0233022 | 0.00811156 | 0.0479224 | 0.00777482 | 0.000146197 |
| 12 | 1000 | 0.0992687 | -0.00128302 | 0.111927 | 0.0109865 | 0.033002 | 0.00822081 | 0.0617782 | 0.0117621 | 0.00208879 |
| 13 | 500 | 0.109971 | 8.95764e-05 | 0.117413 | 0.00715259 | 0.0279551 | 0.00900985 | 0.0496803 | 0.00773686 | 0.00115662 |
| 13 | 1000 | 0.0960553 | 0.000598204 | 0.133315 | 0.0076071 | 0.0346848 | 0.00871647 | 0.0634534 | 0.00705814 | 0.00262314 |
| 23 | 500 | 0.0798271 | 0.00172291 | 0.14409 | 0.00291555 | 0.0309198 | 0.00378791 | 0.045255 | 0.00533318 | 0.00157728 |
| 23 | 1000 | 0.060292 | 0.00258176 | 0.189018 | 0.00271016 | 0.0621548 | 0.00565404 | 0.0453497 | 0.00530956 | 0.00477826 |
| 24 | 500 | 0.0200792 | 0.00389473 | 0.170215 | -0.00140214 | 0.0230209 | 0.00779667 | 0.0355529 | 0.0037319 | 0.00513395 |
| 24 | 1000 | 0.0339637 | 0.0103229 | 0.281049 | -0.000154233 | 0.0419308 | 0.00674891 | 0.0415273 | 0.00369156 | 0.00470077 |

#### Pythia-1.4B · ESS · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.0991898 | 0.00550388 | 0.146738 | 0.000993744 | 0.00524351 | 0.00539647 | 0.0168669 | 0.0022518 | -0.00020301 |
| 1 | 1000 | 0.0957833 | 0.00533977 | 0.142945 | 0.00164694 | 0.00748656 | 0.00539396 | 0.0196181 | 0.00032461 | -0.000847606 |
| 2 | 500 | 0.247595 | 0.00366989 | 0.10527 | 0.00138922 | 0.00354214 | 0.00666804 | 0.0147547 | 0.00264234 | 0.000769002 |
| 2 | 1000 | 0.281736 | 0.00265723 | 0.111914 | 0.00191147 | 0.00916106 | 0.00717135 | 0.0221898 | 0.00145716 | 0.00163979 |
| 12 | 500 | 0.0879544 | 0.00351381 | 0.225498 | 0.002135 | 0.0539376 | 0.00403492 | 0.0884889 | 0.00528365 | 0.00890062 |
| 12 | 1000 | 0.0947753 | 0.00463392 | 0.331282 | 0.0013888 | 0.0658156 | 0.00458749 | 0.0950127 | 0.00471577 | 0.00601872 |
| 13 | 500 | 0.105929 | 0.00484159 | 0.216243 | 0.00222144 | 0.0460907 | 0.00486732 | 0.103339 | 0.00460095 | 0.0112243 |
| 13 | 1000 | 0.110402 | 0.0046906 | 0.393195 | 0.00110366 | 0.0535599 | 0.00499107 | 0.0908815 | 0.00398868 | 0.00491678 |
| 23 | 500 | 0.0273293 | 0.00680376 | 0.206821 | 0.000991951 | 0.04499 | 0.00578285 | 0.0423343 | 0.00221778 | 0.00174424 |
| 23 | 1000 | 0.0312402 | 0.00319929 | 0.22092 | 0.00140309 | 0.0641691 | 0.00637145 | 0.0491696 | 0.00295944 | 0.00764783 |
| 24 | 500 | 0.0276393 | 0.00448272 | 0.29306 | 0.00166873 | 0.049069 | 0.00674293 | 0.0609624 | 0.00351747 | 0.00590138 |
| 24 | 1000 | 0.0289467 | 0.00397429 | 0.392204 | 0.000125396 | 0.0789463 | 0.00695253 | 0.0514167 | 0.00344197 | 0.0025775 |

#### Pythia-1.4B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.0179384 | 0.00198388 | 0.101156 | 0.000159612 | 0.00650287 | -0.000315121 | 0.00939597 | -0.000624011 | 0.00392746 |
| 1 | 1000 | 0.0134108 | 0.00336585 | 0.0927644 | 0.000843107 | 0.01118 | -0.00131922 | 0.0243409 | -0.000546282 | 0.00101147 |
| 2 | 500 | 0.0706367 | 0.00161709 | 0.0604973 | -0.00149995 | 0.00796479 | 0.00353155 | 0.0173627 | 0.00122276 | -0.000335394 |
| 2 | 1000 | 0.0871769 | 0.000899773 | 0.124475 | 0.000253956 | 0.00912436 | 0.00482471 | 0.010224 | 0.00199412 | -0.000595431 |
| 12 | 500 | 0.0275597 | 0.000374901 | 0.114443 | -0.000308693 | 0.024194 | 0.00723185 | 0.0295921 | 0.00610488 | 8.74703e-05 |
| 12 | 1000 | 0.0261089 | 0.00337688 | 0.120731 | 0.00177279 | 0.0467186 | 0.00461279 | 0.0293967 | 0.00384518 | 0.00261427 |
| 13 | 500 | 0.0277308 | 0.000490803 | 0.128307 | -0.000710344 | 0.0255637 | 0.00331873 | 0.037489 | 0.00268473 | 0.000534513 |
| 13 | 1000 | 0.0245965 | 0.000779866 | 0.149589 | 0.00153807 | 0.048684 | 0.00545792 | 0.0245799 | 0.00496821 | 0.000776899 |
| 23 | 500 | 0.0277416 | 0.00343023 | 0.175919 | 0.00329796 | 0.0348857 | 0.00545955 | 0.0237802 | 0.00402774 | 0.00237139 |
| 23 | 1000 | 0.0215577 | 0.00396301 | 0.153549 | 0.00198289 | 0.05609 | 0.000880291 | 0.0219127 | 0.00263875 | 0.00104134 |
| 24 | 500 | 0.018053 | 0.00185933 | 0.212759 | -0.000637015 | 0.0311033 | 0.00352764 | 0.0146017 | 0.00160132 | -0.000259197 |
| 24 | 1000 | 0.0196887 | 0.0023304 | 0.217727 | 0.00166446 | 0.0443065 | 0.00264379 | 0.0197411 | 0.00367761 | -0.000339102 |

#### Pythia-1.4B · ESS_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.107772 | 0.000686462 | 0.0859776 | 0.000680578 | 0.00884667 | 0.00444482 | 0.0119963 | 0.00144853 | 0.000905953 |
| 1 | 1000 | 0.0935084 | 0.00127077 | 0.0672065 | 0.00145481 | 0.00651815 | 0.00600915 | 0.0131185 | 0.00185245 | 0.000991742 |
| 2 | 500 | 0.141843 | 0.00053486 | 0.0615634 | 0.000817049 | 0.00396203 | 0.00282076 | 0.0129508 | 0.00168893 | -0.00144581 |
| 2 | 1000 | 0.153662 | -0.000311066 | 0.0564767 | 0.000141762 | -0.000449763 | -0.000762312 | 0.0114396 | 0.000306319 | 0.000219591 |
| 12 | 500 | 0.012817 | -0.000752275 | 0.0752864 | 0.000869215 | 0.00232956 | 0.000199417 | 0.0269518 | 0.00285769 | 0.000746193 |
| 12 | 1000 | 0.0139273 | -4.17326e-05 | 0.099613 | 0.000150613 | 0.00396222 | 0.000332081 | 0.0265069 | 0.000288716 | 0.000519877 |
| 13 | 500 | 0.00990882 | -0.000706685 | 0.0757136 | -0.0004821 | -0.000816208 | 0.000374852 | 0.0283862 | 0.000132417 | -0.000359771 |
| 13 | 1000 | 0.01267 | -0.000755489 | 0.129896 | -0.000253362 | 0.00121761 | 0.000575455 | 0.0200115 | -3.76286e-05 | 0.00113494 |
| 23 | 500 | 0.0121197 | 0.00562564 | 0.109771 | 0.00132387 | 0.00563276 | 0.00488499 | 0.0214132 | 0.00293958 | 0.000902443 |
| 23 | 1000 | 0.014709 | 0.00212604 | 0.116774 | 0.00316856 | 0.00474377 | 0.00667677 | 0.015615 | 0.00304589 | 0.00151909 |
| 24 | 500 | 0.0126254 | 0.00166856 | 0.147863 | -0.00120975 | 0.00909845 | 0.00196455 | 0.0334166 | 0.00087411 | 0.000727898 |
| 24 | 1000 | 0.0150357 | 0.000594492 | 0.207242 | -3.60957e-05 | 0.0145498 | 0.00317351 | 0.0337127 | 0.00119437 | 0.000422023 |

#### Pythia-6.9B · ESS · RF · ess run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.0350688 | 0.00246346 | 0.164029 | 0.000205297 | 0.00190745 | 0.00169861 | 0.00771822 | 0.00301337 | 0.00188273 |
| 1 | 100 | 0.0978457 | 0.00416201 | 0.160057 | 0.00210709 | 0.00336631 | 0.00447715 | 0.0167768 | 0.00133927 | -0.00063251 |
| 1 | 500 | 0.155056 | 0.0029478 | 0.133334 | 0.00460946 | 0.000983565 | 0.00505112 | 0.0135036 | -0.000498903 | -0.000634392 |
| 1 | 2000 | 0.247793 | 0.0035027 | 0.111062 | 0.00498545 | 0.0045053 | 0.00283875 | 0.0204962 | 0.00139962 | -0.00227575 |
| 1 | 3000 | 0.295438 | 0.00284173 | 0.128716 | 0.00729079 | 0.00418101 | 0.00164893 | 0.0244579 | 3.70806e-06 | -0.000334465 |
| 2 | 10 | 0.0221849 | 0.00622449 | 0.182333 | 0.00153956 | 0.0115367 | 0.00977033 | 0.00632686 | 0.00165662 | 0.00600903 |
| 2 | 100 | 0.0981015 | 0.00402924 | 0.150764 | 0.00210362 | 0.00395091 | 0.00460188 | 0.00966254 | 0.00392035 | -1.15083e-05 |
| 2 | 500 | 0.161882 | 0.00424793 | 0.124492 | 0.00480344 | 0.00356995 | 0.00690142 | 0.0163827 | 0.00291648 | -0.000309041 |
| 2 | 2000 | 0.268684 | 0.00273193 | 0.248222 | 0.00324806 | 0.0258369 | 0.00461773 | 0.0323456 | 0.00220122 | 0.000560329 |
| 2 | 3000 | 0.317953 | 0.00284033 | 0.339176 | 0.00390921 | 0.0201164 | 0.00466775 | 0.0356029 | 0.00296056 | 2.86867e-05 |
| 16 | 10 | 0.00139259 | -0.000508081 | 0.148708 | 1.28328e-05 | 0.00568978 | 0.00137546 | 0.0278869 | 0.0010063 | 0.0136973 |
| 16 | 100 | 0.040215 | 0.00208334 | 0.274418 | 0.00607793 | 0.033671 | 0.00441159 | 0.0588897 | 0.00354897 | 0.0103616 |
| 16 | 500 | 0.0824927 | 0.00454228 | 0.386449 | 0.00202267 | 0.0597017 | 0.00462884 | 0.0586884 | 0.00509893 | 0.0036544 |
| 16 | 2000 | 0.0640667 | 0.00558124 | 0.467092 | 0.00117447 | 0.141778 | 0.00405025 | 0.0513384 | 0.00561181 | 0.0013351 |
| 16 | 3000 | 0.066457 | 0.00451717 | 0.458236 | 0.00159151 | 0.207545 | 0.00437564 | 0.0366017 | 0.00469659 | 0.000170141 |
| 17 | 10 | 0.00705002 | 0.00305222 | 0.162473 | 1.71214e-05 | 0.00405324 | -0.000532981 | 0.0165119 | 0.00112781 | 0.0108903 |
| 17 | 100 | 0.0347562 | 0.00249916 | 0.272032 | 0.00606523 | 0.0271066 | 0.003821 | 0.0536443 | 0.0021558 | 0.0106776 |
| 17 | 500 | 0.0734572 | 0.00330324 | 0.371488 | 0.00228527 | 0.0599829 | 0.00426402 | 0.0573171 | 0.00593036 | 0.0035382 |
| 17 | 2000 | 0.0676499 | 0.00398468 | 0.474195 | 0.00198754 | 0.139393 | 0.0044257 | 0.0487674 | 0.00574672 | 0.000889913 |
| 17 | 3000 | 0.0608221 | 0.00464135 | 0.458098 | 0.000901625 | 0.183074 | 0.00269688 | 0.034697 | 0.00457821 | 6.76757e-05 |
| 31 | 10 | 0.00669617 | 0.00431391 | 0.0692898 | -0.00105948 | 0.0196986 | 0.00378813 | 0.019682 | 0.0018458 | 0.00396625 |
| 31 | 100 | 0.0263454 | 0.00827433 | 0.205674 | -0.000294172 | 0.0285929 | 0.0135159 | 0.0378587 | 0.000862884 | 0.00242237 |
| 31 | 500 | 0.0268847 | 0.00336199 | 0.258343 | -0.00256832 | 0.0373482 | 0.00686512 | 0.0374184 | 0.000921668 | -0.00109725 |
| 31 | 2000 | 0.0200263 | 0.00101253 | 0.188262 | -0.000603335 | 0.0936069 | 0.00581891 | 0.0306945 | 0.00455955 | 0.00314543 |
| 31 | 3000 | 0.0225768 | 0.000920159 | 0.151484 | 0.00194323 | 0.130093 | 0.00766753 | 0.030814 | 0.00500925 | 0.00425374 |
| 32 | 10 | 0.00898498 | 0.00332901 | 0.10727 | 0.000337842 | -4.1547e-05 | 0.00741637 | 0.00723043 | 0.00367673 | 0.00187058 |
| 32 | 100 | 0.0425077 | 0.00435169 | 0.178143 | 0.000857389 | 0.0115681 | 0.00474375 | 0.0607792 | 0.00411409 | 0.00894309 |
| 32 | 500 | 0.0503959 | 0.00544857 | 0.317214 | 0.000957907 | 0.0327275 | 0.00507597 | 0.0769205 | 0.00512416 | 0.00261885 |
| 32 | 2000 | 0.029129 | 0.00448196 | 0.411197 | 0.000815652 | 0.133079 | 0.00131003 | 0.0610541 | 0.00401932 | 0.00148751 |
| 32 | 3000 | 0.0291194 | 0.00394554 | 0.418645 | 0.000743814 | 0.182685 | -0.000261589 | 0.0750129 | 0.00862167 | 0.00113237 |

#### Pythia-6.9B · ESS_LOW_VS_HIGH · RF · ess run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.0344029 | 0.00104178 | 0.0973259 | 0.000817692 | 0.0122916 | 0.00237703 | 0.0035846 | -0.00233806 | 0.00028575 |
| 1 | 100 | 0.0917098 | -0.000684138 | 0.0921731 | -0.000666485 | 0.00939038 | 0.00354371 | 0.00242642 | 0.000707921 | -0.00142039 |
| 1 | 500 | 0.101276 | 0.0022455 | 0.0897749 | 0.000191307 | 0.00762559 | 0.00535898 | 0.00859291 | 0.000837965 | -0.00078748 |
| 1 | 2000 | 0.136383 | 0.0002098 | 0.0647298 | -8.31191e-05 | 0.00384776 | -0.000286541 | 0.00937723 | -0.000481458 | -0.00169235 |
| 1 | 3000 | 0.146791 | 0.000623566 | 0.0702155 | 0.00280113 | 0.00264176 | 0.000881329 | 0.0158085 | 8.48497e-05 | 0.000589003 |
| 2 | 10 | 0.0104325 | -0.000409662 | 0.120765 | -0.000888746 | 0.0165105 | 0.00893572 | -0.000770619 | 0.00292098 | -0.00214399 |
| 2 | 100 | 0.0444824 | 0.00231408 | 0.0979686 | -0.000316307 | 0.0041879 | 0.00252186 | 0.00189369 | 0.00340516 | 0.000341327 |
| 2 | 500 | 0.100308 | 0.00227472 | 0.0549869 | 0.000340882 | 0.00365215 | 0.0032319 | 0.0135488 | 0.00328179 | 0.00035982 |
| 2 | 2000 | 0.12413 | 0.000965338 | 0.111186 | 0.00161294 | 0.00370866 | 0.0016515 | 0.0147056 | 0.00172458 | 0.000237985 |
| 2 | 3000 | 0.127934 | 0.000192049 | 0.121174 | -0.000749604 | 0.00325742 | 0.00248259 | 0.0107159 | 0.000546282 | -0.000654866 |
| 16 | 10 | 0.00254277 | 0.00282733 | 0.116443 | 0.00295214 | 0.00316945 | 0.00403629 | 0.0121273 | 0.000304539 | 0.00212455 |
| 16 | 100 | 0.010067 | 0.000108683 | 0.105779 | 0.00224184 | 0.000576394 | -7.05103e-05 | 0.0203788 | 0.0013121 | 0.00163192 |
| 16 | 500 | 0.0216894 | 0.000223744 | 0.10618 | -0.000101513 | 0.00100984 | 0.00142459 | 0.0186299 | 0.000533129 | 0.000887905 |
| 16 | 2000 | 0.0151891 | 0.000552215 | 0.113139 | -0.00038123 | 0.0639503 | 0.00265061 | 0.0116672 | 0.00183445 | 4.35621e-05 |
| 16 | 3000 | 0.0173012 | 0.000464745 | 0.109784 | 0.00050979 | 0.0846096 | 0.00137624 | 0.00914883 | 0.00314572 | 5.58742e-06 |
| 17 | 10 | 0.00682135 | 0.00329084 | 0.119019 | 0.0010311 | 0.00477665 | 0.000833762 | 0.0166354 | 0.00410834 | 0.00408737 |
| 17 | 100 | 0.00599105 | 0.000811264 | 0.108935 | 0.00101137 | 0.00330152 | -0.0012095 | 0.0258842 | -0.000472755 | 0.00204129 |
| 17 | 500 | 0.0193642 | 0.000960789 | 0.113551 | 0.000439923 | 0.00186674 | 0.00192573 | 0.0201937 | 0.00149431 | 0.000995748 |
| 17 | 2000 | 0.0141835 | 0.000657783 | 0.130934 | -0.000331487 | 0.0649919 | 0.000836778 | 0.00957545 | 0.00144526 | -0.000404717 |
| 17 | 3000 | 0.0147779 | 0.00162975 | 0.124517 | -2.12619e-06 | 0.0936826 | -1.89873e-05 | 0.00781453 | 0.00190595 | 4.85067e-05 |
| 31 | 10 | 0.002804 | 0.00331072 | 0.0746137 | -0.00298309 | 0.00219309 | 0.00375069 | 0.0216786 | 0.00343453 | -0.000211135 |
| 31 | 100 | 0.0093303 | 0.00496489 | 0.115318 | -0.000433643 | -0.000938291 | 0.00693973 | 0.0170204 | 0.00472973 | 0.00269047 |
| 31 | 500 | 0.00488815 | 0.00112747 | 0.153815 | -0.00176221 | 0.0122495 | 0.00620303 | 0.019235 | 0.00170352 | 0.000585245 |
| 31 | 2000 | 0.0107882 | 0.00193379 | 0.112526 | 0.0013969 | 0.0268809 | 0.0086696 | 0.0189337 | 0.0087013 | 0.00129376 |
| 31 | 3000 | 0.0118277 | 0.00187035 | 0.0984563 | -0.000567445 | 0.0484669 | 0.00275583 | 0.0192444 | 0.00483895 | -0.000943137 |
| 32 | 10 | 0.00539478 | 0.000557061 | 0.0952737 | -0.00141159 | -0.000653234 | 0.00920273 | 0.0166795 | 0.00166124 | 0.000974733 |
| 32 | 100 | 0.00755716 | 0.0030622 | 0.112577 | 0.000662975 | 0.00314191 | 0.00297701 | 0.0345075 | 0.00324476 | 0.00486887 |
| 32 | 500 | 0.0135579 | 0.00233455 | 0.157246 | -0.00038301 | 0.00668918 | 0.00300519 | 0.0365855 | 0.00328105 | -0.000561264 |
| 32 | 2000 | 0.00543686 | 0.00176419 | 0.209678 | 9.50356e-05 | 0.0648605 | -0.000296628 | 0.0178046 | 0.00325959 | -4.40566e-05 |
| 32 | 3000 | 0.00472612 | 0.0027543 | 0.197478 | 0.000169106 | 0.0650361 | -0.000605568 | 0.0149356 | 0.00209237 | 0.000266021 |

#### Pythia-6.9B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.022449 | -0.000415132 | 0.0706849 | 0.00147349 | 0.00764225 | -0.00507445 | 0.00183351 | 0.00278617 | 0.00108486 |
| 1 | 100 | 0.0418572 | 0.0011677 | 0.0850396 | 0.0030393 | 0.0024751 | 0.00435295 | 0.00701693 | -8.71015e-05 | 0.00122825 |
| 1 | 500 | 0.048349 | 0.00334971 | 0.0507206 | 0.00222514 | -0.00221564 | 0.00862633 | 0.00417857 | -0.00109481 | -0.000959383 |
| 1 | 2000 | 0.0802304 | 0.00184389 | 0.146006 | 0.0102357 | 0.0138882 | 0.00638889 | 0.0223739 | 0.00545245 | 0.00130519 |
| 1 | 3000 | 0.0584196 | 0.00208309 | 0.151883 | 0.00770782 | 0.0173597 | 0.00982668 | 0.0317974 | 0.00512583 | 4.17864e-05 |
| 2 | 10 | 0.0117459 | 0.000694603 | 0.053701 | 0.00162407 | 0.00464632 | 0.00063849 | 0.00649898 | 0.00642038 | -0.00187569 |
| 2 | 100 | 0.0223179 | 0.00289058 | 0.0799261 | 0.00336927 | 0.00394512 | 5.88096e-06 | 0.00137066 | 0.00352394 | -0.000222146 |
| 2 | 500 | 0.0460334 | 0.000790521 | 0.125165 | 0.0191646 | 0.0112926 | 0.00579268 | 0.022575 | 0.00217902 | 0.0010948 |
| 2 | 2000 | 0.0262638 | 0.000958185 | 0.23837 | 0.00309609 | 0.0136315 | 0.00520528 | 0.0492897 | 0.00461752 | 0.000452898 |
| 2 | 3000 | 0.0276131 | -5.8043e-05 | 0.223001 | 0.00627711 | 0.0113267 | 0.00725346 | 0.0370944 | 0.00397853 | -0.000152152 |
| 16 | 10 | 0.00797125 | 0.000525375 | 0.109018 | 0.00758942 | 0.0176856 | 3.39924e-05 | 0.0169864 | 4.92105e-05 | 0.00442739 |
| 16 | 100 | 0.0667947 | 0.00047639 | 0.12234 | 0.017573 | 0.018108 | 0.00300327 | 0.0450273 | 0.0038632 | 0.00225751 |
| 16 | 500 | 0.103389 | 0.00033019 | 0.165072 | 0.0173354 | 0.0342976 | 0.00721199 | 0.0642539 | 0.00791853 | 0.00278631 |
| 16 | 2000 | 0.0835418 | -0.000252691 | 0.172437 | 0.0122838 | 0.0362295 | 0.00759664 | 0.119733 | 0.016039 | 0.00293406 |
| 16 | 3000 | 0.0935921 | -0.000322059 | 0.150046 | 0.00910827 | 0.0310207 | 0.00905103 | 0.12282 | 0.0204218 | 0.00236757 |
| 17 | 10 | 0.010353 | 0.0037114 | 0.0781989 | 0.00592459 | 0.01485 | 0.000969733 | 0.011387 | 0.000401378 | 0.0045221 |
| 17 | 100 | 0.0625338 | 0.000894708 | 0.118597 | 0.0127998 | 0.0179263 | 0.00213335 | 0.0455556 | 0.00303422 | 0.00264896 |
| 17 | 500 | 0.103168 | -0.000204179 | 0.157158 | 0.0177198 | 0.0379333 | 0.00795344 | 0.0564069 | 0.00633109 | 0.00143344 |
| 17 | 2000 | 0.081267 | -0.000301839 | 0.154055 | 0.00952577 | 0.0387074 | 0.00834767 | 0.107599 | 0.012519 | 0.00332806 |
| 17 | 3000 | 0.0918119 | -0.000242095 | 0.141094 | 0.00749899 | 0.0316716 | 0.0117901 | 0.122393 | 0.0179456 | 0.00219494 |
| 31 | 100 | 0.0853407 | 0.000700566 | 0.0657323 | 0.00915736 | 0.019192 | -0.000358274 | 0.0195033 | 0.00479964 | 0.00107533 |
| 31 | 500 | 0.0980947 | 0.00110602 | 0.154147 | 0.00335705 | 0.0356496 | 0.00172039 | 0.052108 | 0.00504387 | 0.00257596 |
| 31 | 2000 | 0.0449644 | 0.00284154 | 0.149081 | 0.00423356 | 0.0811686 | 0.00800009 | 0.0428748 | 0.0049204 | 0.00525423 |
| 31 | 3000 | 0.0417212 | 0.00228748 | 0.136344 | 0.00441657 | 0.0638906 | 0.00671447 | 0.0315975 | 0.00586124 | 0.00295476 |
| 32 | 10 | 0.0222411 | -0.000565468 | 0.0357973 | -0.0038319 | 0.0203988 | -0.00148271 | 0.0100232 | 0.00349394 | -6.95375e-05 |
| 32 | 100 | 0.037682 | 0.0013886 | 0.0656423 | 0.000394456 | 0.0146709 | 0.0029483 | 0.0238099 | 0.00874487 | 0.00159081 |
| 32 | 500 | 0.0316322 | 0.00100789 | 0.204323 | -0.000985726 | 0.0261728 | 0.00639004 | 0.032233 | 0.00354123 | 0.00203015 |
| 32 | 2000 | 0.0242242 | 0.0043581 | 0.310867 | 0.000708056 | 0.0456874 | 0.00344967 | 0.0481842 | 0.00567194 | 0.00237858 |
| 32 | 3000 | 0.0306303 | 0.00398703 | 0.294181 | 0.00249968 | 0.035458 | 0.00425702 | 0.038357 | 0.00555197 | 5.15831e-06 |

#### Pythia-6.9B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.0113489 | -0.00121811 | 0.0700498 | -0.0023256 | 0.0201861 | 0.00624382 | -0.00686308 | 0.0017593 | -0.000699515 |
| 1 | 100 | 0.0417603 | 0.00173344 | 0.100186 | -0.00206987 | 0.000211234 | -1.43888e-05 | 0.00457882 | -0.000481606 | -0.000394531 |
| 1 | 500 | 0.0433904 | 0.00270861 | 0.0799933 | -3.07555e-05 | 0.00135824 | 0.00514018 | 0.0104029 | -0.00158282 | -0.00187174 |
| 1 | 2000 | 0.0593081 | -0.00154114 | 0.146272 | 0.00033218 | 0.0133607 | 0.00566382 | 0.0100559 | -0.000177017 | -0.00224832 |
| 1 | 3000 | 0.0503269 | 0.000148685 | 0.144894 | 0.00235433 | 0.0169136 | 0.00531458 | 0.0150558 | -0.000436264 | 0.000702729 |
| 2 | 10 | 0.0199351 | 0.000246638 | 0.065045 | 0.000300831 | 0.00216945 | 0.00546563 | 0.00410937 | 0.0026294 | 0.00238227 |
| 2 | 100 | 0.0184158 | 0.00642731 | 0.077154 | -0.000264092 | 0.0119112 | 0.000793414 | -0.00101805 | 0.00215684 | -0.000662184 |
| 2 | 500 | 0.0272265 | 0.00450865 | 0.135799 | 0.000371094 | 0.0086426 | 0.00441332 | 0.0185964 | -0.00243804 | -0.000532931 |
| 2 | 2000 | 0.021252 | 3.80736e-06 | 0.237401 | -5.28085e-05 | 0.00966762 | 0.00322622 | 0.0139004 | 0.00147725 | -0.000455647 |
| 2 | 3000 | 0.0194676 | 0.000493819 | 0.222949 | -0.000444175 | 0.00974995 | 0.00990022 | 0.0153657 | 0.00113469 | 0.000583762 |
| 16 | 10 | 0.00406067 | 0.00129089 | 0.0926293 | 0.00460755 | 0.00820683 | 0.00187312 | 0.00956715 | -0.000318137 | 0.00261476 |
| 16 | 100 | 0.0158698 | 0.00117163 | 0.0933336 | 0.00595866 | 0.0141416 | 0.00280162 | 0.026176 | 0.00338494 | 0.00106369 |
| 16 | 500 | 0.0234701 | 0.00119887 | 0.172447 | 0.00219333 | 0.0258469 | 0.00562035 | 0.0244986 | 0.00265239 | 0.00118958 |
| 16 | 2000 | 0.0271045 | 0.00136501 | 0.129131 | 0.000337668 | 0.0345717 | 0.00298952 | 0.0178984 | 0.00883871 | 0.00143913 |
| 16 | 3000 | 0.0265838 | 0.000769432 | 0.13884 | 0.00134509 | 0.0357879 | 0.00449041 | 0.0115178 | 0.00775376 | 0.001344 |
| 17 | 10 | 0.00865358 | 0.00466668 | 0.067006 | 0.0105709 | 0.00812772 | 0.00032323 | 0.0171769 | -0.000273536 | 0.00190373 |
| 17 | 100 | 0.017979 | 0.00140417 | 0.0871819 | 0.00965744 | 0.00611427 | 0.00336328 | 0.0280814 | 0.00131156 | 0.0037007 |
| 17 | 500 | 0.0238725 | 0.00208025 | 0.145897 | 0.000359523 | 0.0288655 | 0.00368424 | 0.0235364 | 0.00388894 | 0.00153763 |
| 17 | 2000 | 0.0236633 | 0.00126854 | 0.13918 | 0.00105454 | 0.0439489 | 0.00219981 | 0.0123572 | 0.00437208 | 0.00108302 |
| 17 | 3000 | 0.0243324 | 0.000519086 | 0.134935 | -0.000188687 | 0.0293558 | 0.00417321 | 0.0110482 | 0.00623032 | 0.001705 |
| 31 | 10 | 0.0218321 | 0.010251 | 0.0636983 | -0.00215076 | 0.00408381 | 0.00131893 | 0.0152918 | 0.00126197 | 0.00162831 |
| 31 | 100 | 0.0393002 | 0.00349802 | 0.0919824 | -0.0028437 | 0.00774654 | 0.00290491 | 0.0184763 | 0.00143171 | 0.00154247 |
| 31 | 500 | 0.0424242 | 0.00111066 | 0.16863 | -0.000198873 | 0.0243657 | 0.00312391 | 0.0112665 | 0.003821 | 0.00120352 |
| 31 | 2000 | 0.0133041 | 0.00232501 | 0.0971869 | 0.00108173 | 0.0607534 | 0.00452779 | 0.0375103 | 0.00303852 | 0.00145743 |
| 31 | 3000 | 0.0332685 | 0.00343661 | 0.0860381 | 0.00260221 | 0.0685515 | 0.00208426 | 0.0192366 | 0.00836106 | 0.00041604 |
| 32 | 10 | 0.0206556 | 0.00420115 | 0.0524464 | -0.000588311 | 0.0142275 | -0.00383159 | 0.023106 | -0.00140229 | 0.00207011 |
| 32 | 100 | 0.0318656 | 0.00129089 | 0.115097 | -0.000625445 | 0.0120863 | 0.00280044 | 0.0297946 | 0.00293087 | 0.00106067 |
| 32 | 500 | 0.0298326 | 0.00391911 | 0.212111 | -0.00139023 | 0.0263546 | 0.00182852 | 0.0152587 | 0.00246074 | 0.00105503 |
| 32 | 2000 | 0.0177411 | 0.00738766 | 0.17597 | -0.000557407 | 0.0246908 | 0.000283277 | 0.0159153 | 0.00225742 | -2.46242e-05 |
| 32 | 3000 | 0.0188869 | 0.00952665 | 0.150353 | -6.58129e-05 | 0.0251756 | 0.000785552 | 0.0160768 | 0.00121267 | -0.000216871 |

#### Pythia-6.9B · MLE · RIDGE · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31 | 10 | 0.0191362 | 0.00994376 | 0.077521 | 0.0182824 | 0.0176743 | 0.00745133 | 0.013309 | 0.0012369 | 0.000283785 |

#### Qwen2.5-7B · FCI · RF · fci_pyfci run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.00905448 | 0.00121976 | 0.0429699 | 0.000239259 | 0.0155353 | 0.0146305 | 0.0133123 | 0.00301174 | 0.000468828 |
| 1 | 100 | 0.048265 | 0.00338063 | 0.132692 | 0.00160288 | 0.00856854 | 0.0103596 | 0.015719 | 0.00140764 | 0.00197562 |
| 1 | 500 | 0.0347913 | 0.00372985 | 0.107618 | 0.000946002 | 0.0135423 | 0.0135645 | 0.010814 | 0.00374974 | 0.00274925 |
| 1 | 2000 | 0.0424618 | 0.00237372 | 0.113057 | 0.000303752 | 0.083945 | 0.0145446 | 0.0287234 | 0.00604264 | 0.00210024 |
| 1 | 3000 | 0.0405308 | 0.00173689 | 0.0850377 | 0.00145941 | 0.0880101 | 0.0119858 | 0.0262322 | 0.00182075 | 0.00150448 |
| 2 | 100 | 0.130212 | 0.00039432 | 0.133508 | 0.00131663 | 0.00884976 | 0.00865226 | 0.00702684 | 0.00500184 | -0.000852488 |
| 2 | 500 | 0.143463 | 0.00456883 | 0.0928989 | 0.00152915 | 0.0142284 | 0.00278791 | 0.00477838 | 0.00410571 | 0.00142632 |
| 2 | 2000 | 0.269816 | 0.0105887 | 0.0609998 | 0.00148692 | 0.13788 | 0.00258869 | 0.0454114 | 0.0048512 | 0.00166484 |
| 2 | 3000 | 0.329265 | 0.0120336 | 0.0685345 | 0.00177452 | 0.143563 | 0.000613109 | 0.0427618 | 0.00651169 | 5.56259e-05 |
| 3 | 10 | 0.0434922 | 0.00152746 | 0.0547545 | 0.0017052 | 0.00107666 | 0.00409115 | 0.003665 | 0.00153731 | 0.000953213 |
| 3 | 100 | 0.0646515 | 0.00213386 | 0.127842 | 0.00316519 | 0.00973 | 0.00732732 | 0.0117114 | 0.00566839 | 0.000248061 |
| 3 | 500 | 0.0481947 | 0.00202651 | 0.154963 | 0.0049582 | 0.00662081 | 0.0126019 | 0.0146358 | 0.00629951 | 0.00293549 |
| 3 | 2000 | 0.0779106 | 0.00563417 | 0.268634 | 0.00228708 | 0.134323 | 0.00666753 | 0.0475182 | 0.0150203 | 0.00402481 |
| 3 | 3000 | 0.0874022 | 0.00555758 | 0.356022 | 0.000440844 | 0.218521 | 0.00621754 | 0.0593704 | 0.0142018 | 0.001249 |
| 4 | 100 | 0.0201111 | 0.000858249 | 0.0956722 | 0.00589622 | 0.0103422 | 0.00591968 | 0.00598784 | 0.00451328 | 0.00250264 |
| 4 | 500 | 0.0143756 | 0.00128842 | 0.158607 | 0.0048971 | 0.0170595 | 0.012465 | 0.0116825 | 0.00504292 | 0.00233152 |
| 4 | 2000 | 0.0698173 | 0.00394511 | 0.264993 | -0.000125351 | 0.245105 | 0.00903313 | 0.051227 | 0.0141686 | 0.00251558 |
| 4 | 3000 | 0.0839283 | 0.00779628 | 0.281997 | 0.00102358 | 0.204862 | 0.00586245 | 0.0404865 | 0.0154901 | 0.00110452 |
| 5 | 100 | 0.0254421 | 0.000556708 | 0.132472 | 0.00414318 | 0.0240766 | 0.0063119 | 0.0357162 | 0.00391019 | 0.00176899 |
| 5 | 500 | 0.0344373 | 0.00161585 | 0.253077 | 0.00141375 | 0.0414169 | 0.00326809 | 0.0581083 | 0.00317568 | 0.0185886 |
| 5 | 2000 | 0.041148 | 0.00351493 | 0.335311 | 0.000815799 | 0.18267 | 0.00518208 | 0.0427155 | 0.034682 | 0.00136832 |
| 5 | 3000 | 0.0586364 | 0.0022495 | 0.265443 | 0.0012491 | 0.179523 | 0.00797269 | 0.03448 | 0.0252629 | 0.0010702 |
| 6 | 10 | 0.013849 | -0.000122854 | 0.121353 | 0.00357321 | 0.00744021 | 0.000942473 | 0.0134446 | 0.00506141 | 0.000980716 |
| 6 | 100 | 0.0233301 | 0.000685329 | 0.206622 | 0.000582335 | 0.0144254 | 0.00562768 | 0.0428666 | 0.00332948 | 0.00191599 |
| 6 | 500 | 0.0368832 | 0.00198085 | 0.309891 | 0.000206422 | 0.0209566 | 0.0010733 | 0.0387666 | 0.00396942 | 0.00399542 |
| 6 | 2000 | 0.0639586 | 0.00582805 | 0.40621 | 0.00127804 | 0.1329 | 0.00902209 | 0.0488878 | 0.00914744 | 0.00201296 |
| 6 | 3000 | 0.086855 | 0.00598591 | 0.378341 | 0.00278609 | 0.164716 | 0.00920569 | 0.0532703 | 0.0102533 | 0.00150668 |
| 14 | 10 | 0.0227098 | 0.00415206 | 0.100834 | 0.00473668 | 0.0192784 | 0.00360237 | 0.0180257 | 0.000390867 | 0.00595021 |
| 14 | 100 | 0.0390728 | 0.000681631 | 0.200009 | 0.00253146 | 0.0101137 | 0.00229582 | 0.0483408 | 0.000738114 | 0.0130296 |
| 14 | 500 | 0.126612 | 0.00106332 | 0.144439 | 0.000682295 | 0.0104368 | 0.000621722 | 0.0804343 | 0.00499235 | 0.00307395 |
| 14 | 2000 | 0.11096 | 0.00468867 | 0.392697 | 0.000201817 | 0.0557886 | 0.00463248 | 0.0539628 | 0.00399334 | 0.000721211 |
| 14 | 3000 | 0.102162 | 0.00531512 | 0.39961 | 0.000818082 | 0.0711798 | 0.00454845 | 0.0572621 | 0.00592832 | 0.00133012 |
| 15 | 100 | 0.03048 | 0.00159956 | 0.203533 | 0.00426592 | 0.011043 | 0.00134731 | 0.0485214 | 0.000707824 | 0.010962 |
| 15 | 500 | 0.0946343 | 0.00127794 | 0.160031 | 0.00135705 | 0.01465 | 0.0043407 | 0.0940808 | 0.00280291 | 0.00593951 |
| 15 | 2000 | 0.108244 | 0.00149355 | 0.410231 | 0.00208541 | 0.0357491 | 0.0084657 | 0.0483493 | 0.00455567 | 0.00146125 |
| 15 | 3000 | 0.0952925 | 0.00520733 | 0.413207 | 0.00178313 | 0.0720084 | 0.00642588 | 0.0524461 | 0.00651782 | 0.000619315 |
| 27 | 100 | 0.0372607 | 0.00827007 | 0.0867648 | 0.00373396 | 0.0369314 | 0.00427264 | 0.0851327 | 0.00231731 | 0.00921978 |
| 27 | 500 | 0.0292508 | 0.00443277 | 0.266995 | 0.00301112 | 0.143062 | 0.00444194 | 0.0271958 | 0.00437864 | 0.00189093 |
| 27 | 2000 | 0.0405256 | 0.00360969 | 0.38715 | 0.00425467 | 0.184911 | 0.00060177 | 0.0389823 | 0.0065923 | -7.86592e-05 |
| 27 | 3000 | 0.0414046 | 0.00402112 | 0.332428 | 0.00362645 | 0.271248 | 0.00220119 | 0.0513305 | 0.0183021 | 0.0017192 |
| 28 | 10 | 0.0101569 | 0.000222653 | 0.0312622 | -0.00301455 | 0.0278399 | 0.00489137 | 0.0147068 | 0.000525666 | -0.000660002 |
| 28 | 100 | 0.0339325 | 0.00274968 | 0.0500093 | 0.00307105 | 0.0811031 | 0.00287087 | 0.011819 | 0.00195726 | 0.0031492 |
| 28 | 500 | 0.0330094 | 0.00977118 | 0.093266 | 0.00121567 | 0.0808638 | 0.00329309 | 0.0144839 | 0.0107452 | -0.000723023 |
| 28 | 2000 | 0.0482219 | 0.00676095 | 0.284245 | 0.00120429 | 0.138831 | 0.00367101 | 0.0317342 | 0.0225907 | 9.02782e-05 |
| 28 | 3000 | 0.0413134 | 0.00458251 | 0.32077 | 0.000405248 | 0.13294 | 0.00151912 | 0.0435027 | 0.0312918 | 0.000600678 |

#### Qwen2.5-7B · FCI_LOW_VS_HIGH · RF · fci_pyfci run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 100 | 0.0402881 | 0.00180943 | 0.0837521 | -0.000400415 | 0.0128914 | 0.0133176 | -0.0024774 | 0.00541822 | 0.00268414 |
| 1 | 500 | 0.035666 | 0.0012541 | 0.0680527 | -0.000313736 | 0.0126475 | 0.0184992 | 0.00927759 | 0.00363177 | 0.00225509 |
| 1 | 2000 | 0.0267059 | 0.00222775 | 0.0518278 | 0.000140724 | 0.0561445 | 0.0135315 | 0.0146664 | -0.000485018 | 0.000142207 |
| 1 | 3000 | 0.0280524 | 0.00257773 | 0.0564162 | 0.000647152 | 0.0500476 | 0.00351652 | 0.0145834 | 0.00130459 | 0.00250668 |
| 2 | 10 | 0.0211502 | -0.000904371 | 0.0780208 | -0.00212451 | -0.00325638 | 0.00137451 | 0.000905261 | -0.000382813 | 0.00146504 |
| 2 | 100 | 0.0930825 | -0.00168958 | 0.102385 | -0.000874852 | 0.0118235 | 0.00387703 | 0.0035934 | 0.00594689 | -0.00188039 |
| 2 | 500 | 0.118367 | 0.00222819 | 0.0429344 | 0.000586234 | 0.0179531 | 0.00189211 | 0.00360102 | 0.0041247 | -0.000492237 |
| 2 | 2000 | 0.104953 | 0.00114616 | 0.0318005 | 0.000916139 | 0.0662861 | 0.00261951 | 0.0159106 | 0.00138034 | 0.000674347 |
| 2 | 3000 | 0.131591 | 0.00201197 | 0.0372762 | 7.14003e-05 | 0.0643424 | 0.00101849 | 0.0109538 | 0.00234316 | -0.000600821 |
| 3 | 10 | 0.0379237 | -0.000643493 | 0.0765445 | 0.00269477 | -0.000686214 | 0.0198731 | -0.000242435 | -0.00104475 | 0.00342652 |
| 3 | 100 | 0.0723832 | -0.00113884 | 0.0887085 | 0.00123274 | 0.0125246 | 0.0041067 | 0.00274797 | 0.00642771 | -0.00205953 |
| 3 | 500 | 0.0376688 | 0.000293463 | 0.134161 | 0.00156191 | 0.00709504 | 0.00717904 | 0.0174209 | 0.00313113 | -0.000444027 |
| 3 | 2000 | 0.0175249 | 0.00296277 | 0.164658 | 0.00102729 | 0.0553033 | 0.00204292 | 0.0153243 | 0.00343577 | 0.000875989 |
| 3 | 3000 | 0.0274308 | 0.00239641 | 0.17142 | -4.06942e-05 | 0.0719214 | 0.000793612 | 0.0170317 | 0.00325475 | 0.000526849 |
| 4 | 10 | 0.00470461 | -0.00033663 | 0.067621 | -0.00108361 | 0.0315089 | 0.00996628 | -0.0036742 | 0.00229786 | -0.0011744 |
| 4 | 100 | 0.0298546 | -0.000275119 | 0.0949446 | 0.00298279 | 0.0155457 | 0.00684434 | 0.000410552 | 0.00407956 | 0.000147152 |
| 4 | 500 | 0.0117197 | -0.000507812 | 0.115073 | 0.000426276 | 0.00862767 | 0.00559509 | 0.00121287 | 0.00510567 | -0.00201142 |
| 4 | 2000 | 0.0236134 | 0.00235626 | 0.187826 | 0.000334602 | 0.0647093 | 0.00210235 | 0.0146974 | 0.00677492 | 0.000972112 |
| 4 | 3000 | 0.0234375 | 0.00159899 | 0.171055 | -0.00015625 | 0.0687464 | 0.00206339 | 0.0183979 | 0.0044774 | 0.000259049 |
| 5 | 100 | 0.0186844 | 0.00144333 | 0.0754607 | 0.00414641 | 0.0131804 | -0.000575653 | 0.0112841 | 0.00249189 | 0.0021558 |
| 5 | 500 | 0.0202442 | 0.00196128 | 0.129782 | 0.00179831 | 0.0109498 | 0.00260329 | 0.019389 | 0.00202245 | 0.00420896 |
| 5 | 2000 | 0.0150348 | 0.00127443 | 0.142074 | 0.000111007 | 0.0684988 | 0.00283475 | 0.0167243 | 0.00570718 | -0.000199763 |
| 5 | 3000 | 0.0210463 | 0.00115585 | 0.136963 | 1.52789e-05 | 0.0659137 | 0.00115981 | 0.0161184 | 0.00301113 | 0.00063306 |
| 6 | 10 | 0.00638746 | -6.96697e-05 | 0.106011 | -0.00158134 | 0.00422107 | 0.00731102 | 0.0181552 | 0.0067054 | 0.00358678 |
| 6 | 100 | 0.00894373 | 0.00106428 | 0.121544 | 0.003179 | 0.00564072 | 0.00163613 | 0.00963998 | 0.00195743 | 0.00238009 |
| 6 | 500 | 0.0134409 | -0.000704312 | 0.16554 | 0.000654322 | 0.0040626 | 0.000135631 | 0.0136597 | 0.000812549 | 0.00283164 |
| 6 | 2000 | 0.0198424 | 0.00621999 | 0.172694 | -0.000723794 | 0.0495904 | 0.00133609 | 0.0114315 | 0.00148309 | 0.000608089 |
| 6 | 3000 | 0.0171166 | 0.00202393 | 0.146468 | -0.000461481 | 0.0542405 | 0.00169996 | 0.0133699 | 0.00471064 | 0.000308792 |
| 14 | 10 | 0.000861303 | 0.00194576 | 0.0749084 | 0.00159261 | 0.00495011 | -0.00159004 | 0.00790304 | -0.000524921 | 0.00467637 |
| 14 | 100 | 0.0126707 | 0.000342613 | 0.0755569 | 0.00428244 | 0.000742682 | -0.000456735 | 0.0194468 | -0.000460987 | 0.000953076 |
| 14 | 500 | 0.0197132 | 0.00114839 | 0.078588 | 0.00098932 | 0.00246534 | 0.000692098 | 0.0204798 | 0.000715239 | 0.00149713 |
| 14 | 2000 | 0.0194436 | 0.000707723 | 0.159312 | -0.000612292 | 0.00447953 | 0.00402606 | 0.0145264 | 0.00102166 | 0.000663024 |
| 14 | 3000 | 0.0212967 | 0.000148042 | 0.142594 | 0.000183099 | 0.00638449 | 0.000231655 | 0.0099103 | 0.000144976 | 0.00112752 |
| 15 | 10 | 0.00333707 | 0.0022496 | 0.0437042 | 0.00514765 | 0.00137703 | 0.00329455 | 0.0141559 | -0.00019284 | 0.0066966 |
| 15 | 100 | 0.0128714 | 0.00103511 | 0.0881002 | 0.00392623 | 0.0037146 | -0.000443186 | 0.0203622 | 0.000908722 | 0.0018524 |
| 15 | 500 | 0.0130543 | 0.00112188 | 0.0657377 | 0.00126834 | 0.00354816 | 0.0010717 | 0.0222516 | -0.000184187 | 0.00300356 |
| 15 | 2000 | 0.0162293 | 0.00051968 | 0.154947 | 0.000222013 | 0.00294833 | 0.00168651 | 0.0147421 | 0.000589992 | -0.00035537 |
| 15 | 3000 | 0.0158599 | 0.000470283 | 0.154824 | 0.000474041 | 0.0100542 | 0.00149713 | 0.0137424 | 0.00130058 | 0.000463756 |
| 27 | 10 | 0.000370995 | 0.00205909 | 0.053507 | 0.00262075 | 0.00530988 | 0.00576058 | 0.0187691 | 0.000844343 | 0.00401711 |
| 27 | 100 | 0.0185259 | 0.00577631 | 0.0713894 | 0.00056606 | 0.0272778 | 0.00129267 | 0.0288678 | 0.00334157 | 0.0028212 |
| 27 | 500 | 0.0138505 | 0.0034913 | 0.157112 | 0.000917227 | 0.0709522 | 0.000760532 | 0.0195328 | 0.00448081 | 0.000158426 |
| 27 | 2000 | 0.00932634 | 0.00683742 | 0.193783 | -0.000257367 | 0.0804876 | 2.07674e-05 | 0.0123202 | 0.00440951 | 0.000888993 |
| 27 | 3000 | 0.0124995 | 0.000829114 | 0.158435 | -0.00107669 | 0.103487 | -0.001268 | 0.0139787 | 0.00450836 | 0.000122231 |
| 28 | 10 | 0.00251953 | -0.000829905 | 0.00515506 | -0.00488153 | 0.0471083 | 0.000317791 | 9.03877e-05 | -0.000220431 | 0.0056739 |
| 28 | 100 | 0.0439697 | 0.000586679 | 0.0427482 | 0.00202497 | 0.0434138 | 0.00561279 | 0.0155639 | 0.00108282 | 0.00467212 |
| 28 | 500 | 0.0138587 | 0.00624827 | 0.045375 | 3.04094e-05 | 0.0567761 | 0.00277784 | 0.00809721 | 0.00444853 | -0.0010269 |
| 28 | 2000 | 0.007009 | 0.00522241 | 0.137038 | 0.00241367 | 0.0441871 | 0.0026115 | 0.00458292 | 0.00131013 | -0.000751236 |
| 28 | 3000 | 0.00514122 | 0.0038345 | 0.140752 | -3.42168e-05 | 0.0631565 | 0.00285072 | 0.0083526 | 0.00590447 | 0.000852453 |

#### Qwen2.5-7B · FCI · RIDGE · fci_pyfci run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 10 | 0.016534 | -0.00166581 | 0.124724 | 0.0178254 | 0.00831171 | 0.00615401 | 0.0595739 | 0.00128142 | 0.00255276 |
| 4 | 10 | 0.0169759 | -1.2185e-05 | 0.0728331 | 0.0149452 | 0.0399755 | 0.0218953 | 0.00908045 | 0.0130361 | 4.05438e-05 |
| 5 | 10 | 0.0112134 | -0.00054645 | 0.210684 | 0.0379652 | 0.0175666 | 0.0169757 | 0.0265646 | 0.000430202 | 0.0182613 |
| 15 | 10 | 0.0256657 | 0.00532889 | 0.380024 | 0.262169 | 0.00591648 | 0.0167136 | 0.0135844 | 0.000449095 | 0.00239176 |
| 27 | 10 | 0.00790484 | 0.0124013 | 0.0607394 | 0.0216085 | 0.00906019 | 0.0260389 | 0.0262333 | 0.00727027 | 0.0115401 |

#### Qwen2.5-7B · FCI_LOW_VS_HIGH · LOGREG · fci_pyfci run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.0336773 | 0.00544843 | 0.098183 | -0.00244427 | 0.0341315 | 0.0196907 | 0.0129709 | 0.0301694 | 0.00165917 |
| 5 | 10 | 0.0457114 | 0.00298363 | 0.165261 | 0.0126072 | -0.00212737 | 0.0105894 | 0.0158255 | 0.00682526 | 0.0128459 |

#### Qwen2.5-7B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.000190599 | 0.000544484 | 0.085216 | 0.00233218 | 0.00802891 | 0.00852575 | 0.0108494 | 0.00602989 | 0.00167547 |
| 1 | 100 | 0.0173511 | 0.00255389 | 0.0976594 | -0.000798922 | 0.0029315 | 0.000179246 | 0.011368 | 0.00277699 | 0.000750634 |
| 2 | 10 | 0.043371 | 0.00130912 | 0.062205 | -0.00266015 | 0.0121532 | -0.00275169 | 0.0063064 | 0.0119297 | -0.000684789 |
| 2 | 100 | 0.0357161 | 0.000541683 | 0.0644507 | 0.000311696 | 0.0139838 | -0.000322598 | 0.0055882 | 0.00611587 | -0.000314222 |
| 2 | 500 | 0.0616921 | 0.00155442 | 0.0444161 | 0.0076554 | 0.0360227 | 0.00454938 | 0.0230761 | 0.0052905 | 0.0026051 |
| 2 | 2000 | 0.0448637 | 0.00349184 | 0.139608 | 0.00338509 | 0.00981696 | 0.0144538 | 0.0290829 | 0.0050323 | 0.000443322 |
| 2 | 3000 | 0.0311948 | 0.00148983 | 0.159567 | 0.00259513 | 0.00626056 | 0.0147059 | 0.0239569 | 0.00334139 | 0.000770129 |
| 3 | 100 | 0.00878702 | 5.61063e-05 | 0.080624 | 0.00449731 | 0.0152973 | 0.00507116 | 0.0108387 | 0.00568434 | 0.00487443 |
| 3 | 500 | 0.0206109 | 0.00248918 | 0.137675 | 0.024226 | 0.0189851 | 0.00905128 | 0.0362748 | 0.00675547 | 0.00251902 |
| 4 | 100 | 0.00603961 | 0.000201769 | 0.0794211 | 0.00446992 | 0.0199039 | 0.00658539 | 0.0188262 | 0.00432365 | 0.00775863 |
| 4 | 500 | 0.0652916 | -0.000563859 | 0.0942964 | 0.00221154 | 0.0253413 | 0.0190965 | 0.0342666 | 0.00686536 | 0.00220407 |
| 5 | 100 | 0.0352908 | 0.000211218 | 0.0826294 | 0.0102899 | 0.0162004 | 0.00108153 | 0.0302563 | 0.00440698 | 0.00487262 |
| 5 | 500 | 0.110803 | -0.00182259 | 0.139537 | 0.00504916 | 0.0505198 | 0.0105219 | 0.0373756 | 0.0119791 | 0.00303095 |
| 6 | 10 | 0.00255398 | 0.00076718 | 0.0619865 | 0.00400762 | 0.0127465 | 0.00179103 | 0.0263412 | 0.00271012 | 0.00211131 |
| 6 | 100 | 0.0216142 | 0.000657331 | 0.121771 | 0.00487371 | 0.0269026 | 0.00696484 | 0.0437175 | 0.00617017 | 0.00608688 |
| 6 | 500 | 0.0887016 | 0.000440441 | 0.171782 | 0.00702103 | 0.0555544 | 0.0161447 | 0.0443272 | 0.0101639 | 0.00426992 |
| 6 | 2000 | 0.0786176 | -0.00105216 | 0.130584 | 0.0129533 | 0.0749297 | 0.0178763 | 0.0776786 | 0.0108467 | 0.00544662 |
| 14 | 10 | 0.00126131 | 0.00864664 | 0.0753677 | 0.00556682 | 0.0148336 | 0.0027268 | 0.0108414 | 0.00118732 | 0.00441679 |
| 14 | 100 | 0.0443724 | 0.0005196 | 0.106846 | 0.00941279 | 0.0231129 | 0.00661583 | 0.0751923 | 0.00471576 | 0.00440661 |
| 14 | 500 | 0.103063 | 0.000961822 | 0.0896012 | 0.00665339 | 0.0429896 | 0.011051 | 0.0936002 | 0.0100437 | 0.00301947 |
| 14 | 2000 | 0.121736 | 0.00106788 | 0.108609 | 0.00889948 | 0.0487743 | 0.0119216 | 0.114109 | 0.00983935 | 0.00529509 |
| 14 | 3000 | 0.139112 | 0.0011808 | 0.104187 | 0.00995495 | 0.040387 | 0.013891 | 0.145591 | 0.00894593 | 0.00500451 |
| 15 | 10 | 0.00743528 | 0.00443644 | 0.0762536 | 0.00766986 | 0.0187518 | 0.00497733 | 0.00970177 | 0.00178942 | 0.0191506 |
| 15 | 100 | 0.0397664 | 0.00110269 | 0.0976728 | 0.00715398 | 0.0220979 | 0.00490271 | 0.0662273 | 0.00308798 | 0.00546393 |
| 15 | 500 | 0.104909 | 0.00175045 | 0.0947269 | 0.00543988 | 0.0469912 | 0.00983387 | 0.0856384 | 0.0118372 | 0.00335165 |
| 15 | 2000 | 0.108688 | 0.000601981 | 0.122412 | 0.00656253 | 0.0541064 | 0.0111309 | 0.121395 | 0.00915223 | 0.00426764 |
| 15 | 3000 | 0.122781 | 0.000726711 | 0.115297 | 0.00993885 | 0.0458086 | 0.0113262 | 0.148032 | 0.0114614 | 0.00576564 |
| 27 | 10 | 0.0256133 | 0.000866564 | 0.0244278 | -0.00036632 | 0.0127296 | 0.0017282 | 0.0275943 | 0.0031127 | 0.000863847 |
| 27 | 100 | 0.0444943 | 0.0013611 | 0.0607997 | 0.00196021 | 0.0100016 | 0.00370842 | 0.0432656 | 0.00501678 | 0.00588122 |
| 27 | 500 | 0.0519901 | 0.00363389 | 0.124541 | 0.00663374 | 0.0317348 | 0.0122092 | 0.0527765 | 0.00686297 | 0.00510272 |
| 27 | 2000 | 0.0440571 | 0.0121571 | 0.186459 | 0.00513362 | 0.0770704 | 0.00376625 | 0.045028 | 0.00778233 | 0.0043124 |
| 27 | 3000 | 0.0412923 | 0.0168091 | 0.178476 | 0.00673474 | 0.0721346 | 0.00430215 | 0.038994 | 0.00861278 | 0.00586881 |
| 28 | 100 | 0.0591596 | 0.00934373 | 0.0576082 | 0.0043761 | 0.00997073 | 0.00613911 | 0.00702775 | 0.00517338 | -0.00311499 |
| 28 | 500 | 0.0422354 | 0.000739995 | 0.144475 | 0.00731203 | 0.034222 | 0.00356275 | 0.0312363 | 0.0102036 | 0.00249995 |
| 28 | 2000 | 0.0521883 | 0.00180087 | 0.278649 | 0.00733441 | 0.0784909 | 0.00884822 | 0.0562381 | 0.00809293 | 0.00150123 |
| 28 | 3000 | 0.0480298 | 0.00439611 | 0.306763 | 0.00972218 | 0.0662091 | 0.0119355 | 0.0556996 | 0.00593475 | 0.00151184 |

#### Qwen2.5-7B · ESS · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.00267184 | 0.00019722 | 0.139245 | -0.00043373 | 0.0088068 | 0.0139855 | 0.0074926 | 0.00264904 | 0.00258042 |
| 1 | 100 | 0.0443876 | 0.00255106 | 0.140611 | -0.000152881 | 0.00390959 | 0.0136745 | 0.0108502 | 0.00359005 | 0.00202197 |
| 1 | 500 | 0.0433383 | 0.00254986 | 0.130133 | 0.000510558 | 0.00818379 | 0.0136582 | 0.0124319 | 0.00322934 | 0.00163261 |
| 1 | 2000 | 0.0414546 | 0.00145675 | 0.118864 | -0.000789533 | 0.05894 | 0.0149093 | 0.0145501 | 0.00370613 | 0.00148233 |
| 1 | 3000 | 0.0322678 | 0.00135952 | 0.108124 | 0.00154844 | 0.0734815 | 0.0127845 | 0.0178145 | 0.00179862 | 0.00157984 |
| 2 | 10 | 0.0313771 | -0.000251652 | 0.121778 | 0.00122273 | 0.00113521 | 0.00307658 | 0.00781617 | 0.00129051 | 0.00936496 |
| 2 | 100 | 0.150169 | 0.000613558 | 0.146282 | 0.00233248 | 0.00668731 | 0.00948086 | 0.00599385 | 0.00532244 | 0.000641654 |
| 2 | 500 | 0.177141 | 0.00319452 | 0.111028 | 0.00210979 | 0.0141941 | 0.00597695 | 0.00762686 | 0.00291957 | 0.00203867 |
| 2 | 2000 | 0.300153 | 0.00634917 | 0.0679127 | 0.00284012 | 0.123746 | 0.00223542 | 0.0368479 | 0.00372417 | 0.000476767 |
| 2 | 3000 | 0.401435 | 0.00839975 | 0.0612715 | 0.0013074 | 0.136762 | 0.000720675 | 0.0477598 | 0.00824522 | 0.00251863 |
| 3 | 10 | 0.0346122 | 0.00226107 | 0.142633 | 0.00292698 | 0.0046605 | 0.0063676 | 0.00300757 | 0.00313075 | 0.00384876 |
| 3 | 100 | 0.0843013 | 0.00376844 | 0.145417 | 0.00536272 | 0.00883974 | 0.00713204 | 0.0152197 | 0.00650333 | 0.00205506 |
| 3 | 500 | 0.0685199 | 0.00269625 | 0.166414 | 0.00510145 | 0.0135901 | 0.0121123 | 0.0134955 | 0.00787586 | 0.00275291 |
| 3 | 2000 | 0.0906038 | 0.00552548 | 0.24758 | 0.0020215 | 0.104479 | 0.0073442 | 0.0451051 | 0.0117526 | 0.00288559 |
| 3 | 3000 | 0.0969105 | 0.00427523 | 0.349389 | 0.0017609 | 0.189142 | 0.0075492 | 0.0622943 | 0.015726 | 0.00136027 |
| 4 | 10 | 0.00831687 | -0.00014424 | 0.118935 | 0.00281908 | 0.0190215 | 0.00534669 | 0.00693292 | 0.00506239 | 0.0109129 |
| 4 | 100 | 0.0196022 | 0.00174448 | 0.124729 | 0.00731653 | 0.0137932 | 0.00810512 | 0.00604097 | 0.00446424 | 0.00520611 |
| 4 | 500 | 0.00850605 | 0.00206874 | 0.174394 | 0.00721907 | 0.0161656 | 0.00874853 | 0.0128708 | 0.0046006 | 0.00522172 |
| 4 | 2000 | 0.0662012 | 0.00671438 | 0.253673 | 0.00052039 | 0.263772 | 0.00742715 | 0.0550122 | 0.0154369 | 0.00263048 |
| 4 | 3000 | 0.0731851 | 0.01207 | 0.269424 | 0.000317243 | 0.283667 | 0.00513762 | 0.0598544 | 0.0111469 | 0.00227258 |
| 5 | 10 | 0.00843358 | 0.00133266 | 0.0902694 | 0.00346314 | 0.0107388 | 0.00213085 | 0.00574696 | 0.000732285 | 0.00455045 |
| 5 | 100 | 0.02563 | 0.00144666 | 0.170526 | 0.00549775 | 0.020355 | 0.00258245 | 0.0318187 | 0.00526349 | 0.0039957 |
| 5 | 500 | 0.0350061 | 0.00140439 | 0.23197 | 0.00206983 | 0.03638 | 0.000456185 | 0.0622028 | 0.0047377 | 0.0128249 |
| 5 | 2000 | 0.048966 | 0.00336875 | 0.371679 | 0.000703821 | 0.199687 | 0.00639995 | 0.0533317 | 0.00674202 | 0.00425782 |
| 5 | 3000 | 0.0559427 | 0.00350162 | 0.364356 | 0.0008571 | 0.214805 | 0.00867911 | 0.0481043 | 0.0125939 | 0.00295115 |
| 6 | 10 | 0.00384931 | 2.4662e-05 | 0.148147 | -0.000314373 | 0.00909079 | 0.00426329 | 0.0206267 | 0.00337502 | 0.00490956 |
| 6 | 100 | 0.0175296 | 0.000729111 | 0.223699 | 0.0014805 | 0.0132274 | 0.00325863 | 0.0349372 | 0.00378185 | 0.00375711 |
| 6 | 500 | 0.0350435 | 0.000909395 | 0.362256 | 0.00143351 | 0.0249934 | 0.00222577 | 0.0481365 | 0.0032551 | 0.00868286 |
| 6 | 2000 | 0.0845544 | 0.00668531 | 0.482716 | 0.000459317 | 0.0995296 | 0.00440883 | 0.0640576 | 0.00911817 | 0.00348435 |
| 6 | 3000 | 0.103682 | 0.00694079 | 0.484891 | 6.01379e-05 | 0.117033 | 0.00724853 | 0.0649922 | 0.00878949 | 0.00237161 |
| 14 | 10 | 0.00697385 | 0.000742012 | 0.088777 | 0.00685394 | 0.0163527 | 4.70996e-07 | 0.0556871 | 0.000947984 | 0.0117131 |
| 14 | 100 | 0.0345998 | 0.00179774 | 0.214533 | 0.00361675 | 0.0121543 | 0.00123016 | 0.0542904 | 0.00223811 | 0.0156516 |
| 14 | 500 | 0.110124 | 0.000965952 | 0.195404 | 0.000642697 | 0.013237 | 0.00155236 | 0.0981281 | 0.00276957 | 0.00824339 |
| 14 | 2000 | 0.130994 | 0.00242049 | 0.428122 | 0.000462896 | 0.0519174 | 0.00438907 | 0.0677388 | 0.00334588 | 0.00103987 |
| 14 | 3000 | 0.137397 | 0.00347696 | 0.465441 | 0.000506715 | 0.062264 | 0.00465116 | 0.0735073 | 0.00642122 | 0.000795842 |
| 15 | 10 | 0.00702826 | 0.00172848 | 0.0908589 | 0.000879634 | 0.0124585 | 0.000151855 | 0.0415369 | 0.00139462 | 0.0194357 |
| 15 | 100 | 0.0285484 | 0.00327548 | 0.224922 | 0.00330122 | 0.01245 | 0.00336299 | 0.0477759 | 0.000166106 | 0.0172178 |
| 15 | 500 | 0.0852957 | 0.00120699 | 0.213667 | 0.00115533 | 0.0141266 | 0.00264611 | 0.0928152 | 0.0026999 | 0.00615149 |
| 15 | 2000 | 0.117238 | 0.000942162 | 0.480147 | 0.000786892 | 0.031167 | 0.00573551 | 0.0594734 | 0.00311647 | 0.000568603 |
| 15 | 3000 | 0.138146 | 0.00203814 | 0.524733 | 0.000305247 | 0.0578348 | 0.00525563 | 0.0627494 | 0.00391777 | 0.000506201 |
| 27 | 10 | 0.00475128 | 0.00627092 | 0.0849552 | -0.00198907 | 0.00812837 | 0.00368793 | 0.0172526 | 0.000626736 | 0.0147234 |
| 27 | 100 | 0.0280625 | 0.013376 | 0.100834 | 0.00184732 | 0.0285951 | 0.00656245 | 0.0799496 | 0.00320221 | 0.015317 |
| 27 | 500 | 0.0326911 | 0.00402457 | 0.275957 | 0.00366953 | 0.125982 | 0.00966255 | 0.0738587 | 0.00684159 | 0.016266 |
| 27 | 2000 | 0.0471125 | 0.00432019 | 0.424529 | 0.00248842 | 0.196148 | 0.0045138 | 0.039873 | 0.00644417 | 0.00130717 |
| 27 | 3000 | 0.0547287 | 0.00400198 | 0.433857 | 0.00258727 | 0.267046 | 0.00653942 | 0.0499528 | 0.0182711 | 0.00111399 |
| 28 | 10 | 0.00197337 | 0.00380634 | 0.0356766 | 0.000864677 | 0.0220331 | -0.00204834 | 0.0168123 | 0.00121973 | 0.0112689 |
| 28 | 100 | 0.0299038 | 0.00601145 | 0.0680948 | 0.00290952 | 0.0731793 | 0.0113509 | 0.0195139 | 0.00331865 | 0.0034546 |
| 28 | 500 | 0.036594 | 0.00638594 | 0.106561 | 0.00244951 | 0.108359 | 0.00670768 | 0.017906 | 0.00686623 | -0.000363373 |
| 28 | 2000 | 0.0514154 | 0.00627937 | 0.294696 | 0.00223699 | 0.128574 | 0.00266625 | 0.0380263 | 0.0323139 | 0.000539164 |
| 28 | 3000 | 0.0423537 | 0.00533856 | 0.35128 | 0.00103328 | 0.145926 | 0.000871342 | 0.0436395 | 0.0311193 | 0.00132258 |

#### Qwen2.5-7B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.000954757 | -0.000799051 | 0.111725 | -0.000548408 | 0.000118473 | 0.0125178 | 0.00370006 | 0.000162085 | 0.00198348 |
| 1 | 100 | 0.013991 | 0.000641861 | 0.137498 | -0.00157506 | 0.00905014 | -0.00382986 | 0.00209118 | 0.00304158 | 0.00208277 |
| 1 | 500 | 0.0408098 | 0.00207768 | 0.0930944 | 0.000324664 | 0.0151842 | 0.000919353 | 0.0147567 | 0.00103194 | 2.15585e-05 |
| 1 | 2000 | 0.0539041 | 0.0111909 | 0.0839929 | -0.00144136 | 0.0252395 | 0.0029109 | 0.0203246 | 0.00143987 | 0.0011693 |
| 1 | 3000 | 0.0797994 | 0.0103614 | 0.116268 | 0.00103006 | 0.0139307 | 0.00476815 | 0.0110236 | 0.00270985 | 0.00414512 |
| 2 | 10 | 0.0320275 | 0.00134889 | 0.0790387 | -0.000734227 | 0.00776019 | 0.00045357 | -0.00276503 | 0.0053753 | -0.000603244 |
| 2 | 100 | 0.0378018 | 0.000254203 | 0.0756844 | -0.000670787 | 0.0235783 | 0.00156196 | -0.00203417 | 0.0117551 | -0.00163207 |
| 2 | 500 | 0.0469597 | 0.00534157 | 0.0657823 | 0.00103377 | 0.0277129 | 0.00356112 | 0.0191796 | 0.00542291 | -0.00281082 |
| 2 | 2000 | 0.0388709 | 0.00248843 | 0.166281 | 0.00163934 | 0.0220676 | 0.014361 | 0.0194752 | 0.0064156 | 0.00103011 |
| 2 | 3000 | 0.0304699 | 0.00102111 | 0.17548 | 0.000277542 | 0.0116002 | 0.0153799 | 0.0173294 | 0.00572043 | 0.000359177 |
| 3 | 10 | 0.0165004 | 0.000362787 | 0.0939279 | 0.000115951 | 0.00845223 | -0.00107254 | -0.00350124 | 0.00175277 | -0.00161511 |
| 3 | 100 | 0.00420149 | 0.000766466 | 0.104113 | 0.00171994 | 0.0253986 | -0.00403723 | 0.00752408 | 0.00601478 | -0.000141762 |
| 3 | 500 | 0.0262525 | 0.00639038 | 0.154353 | 0.00170609 | 0.033516 | 0.00543646 | 0.0200794 | 0.00427047 | 0.00124604 |
| 3 | 2000 | 0.0235009 | 0.00147365 | 0.189531 | -0.000240309 | 0.0458622 | 0.0065669 | 0.0173543 | 0.00721756 | 0.000627522 |
| 3 | 3000 | 0.0260757 | -0.000125396 | 0.188506 | 0.000643839 | 0.0287089 | 0.00442984 | 0.0159186 | 0.00827853 | 0.00174743 |
| 4 | 10 | 0.00332906 | -0.000192593 | 0.0938752 | -1.36472e-05 | 0.00697992 | 0.00842875 | -0.00199239 | 0.00181166 | -0.0030626 |
| 4 | 100 | 0.00283144 | 0.00121939 | 0.0641476 | 0.00663405 | 0.0136273 | 0.00282991 | 0.0131716 | 0.00374634 | 0.0023218 |
| 4 | 500 | 0.00981388 | 0.00217212 | 0.126008 | -0.00146445 | 0.056292 | -0.0022589 | 0.0171766 | 0.00760082 | 0.000576889 |
| 4 | 2000 | 0.0201266 | 0.000506032 | 0.181908 | 0.000950999 | 0.0223822 | 0.00821999 | 0.0145534 | 0.00827388 | 0.00341208 |
| 4 | 3000 | 0.0186476 | 0.000470332 | 0.215725 | 0.000678056 | 0.0148661 | 0.00626998 | 0.0132471 | 0.00690017 | 0.00144556 |
| 5 | 10 | 0.00244294 | 0.00132303 | 0.0569919 | 0.00764117 | 0.00787965 | -0.00499001 | 0.00446049 | 0.00490803 | 0.00906102 |
| 5 | 100 | 0.0143672 | 0.000143987 | 0.0975911 | 0.00587999 | 0.0268176 | 0.00298976 | 0.0154621 | 0.00346292 | 3.06072e-05 |
| 5 | 500 | 0.0170383 | 0.00114601 | 0.183301 | 0.00126122 | 0.0366528 | 0.00844561 | 0.0183685 | 0.00615625 | 0.00252927 |
| 5 | 2000 | 0.0302733 | 5.19185e-06 | 0.15324 | 0.000265872 | 0.0216677 | 0.0079554 | 0.0183635 | 0.00564735 | 0.00303234 |
| 5 | 3000 | 0.0278894 | 0.000591723 | 0.159685 | 0.00140818 | 0.0190297 | 0.00875138 | 0.0139164 | 0.00679767 | 0.0028263 |
| 6 | 10 | 0.00077591 | 0.000438736 | 0.0648406 | 0.00177596 | 0.0105831 | -0.00128209 | 0.0202431 | 0.000573131 | 0.00500524 |
| 6 | 100 | 0.0106052 | 0.00108678 | 0.101905 | 0.00721133 | 0.0169645 | 0.00495995 | 0.0254 | 0.00224189 | 0.00249698 |
| 6 | 500 | 0.0309349 | 0.00102502 | 0.173913 | -0.00165719 | 0.0392107 | 0.00889923 | 0.0234728 | 0.00526315 | 0.00273813 |
| 6 | 2000 | 0.0257295 | 0.00240645 | 0.14773 | 4.45016e-05 | 0.0543041 | 0.00690175 | 0.0205207 | 0.00161264 | 0.00162777 |
| 6 | 3000 | 0.0466328 | 0.00155409 | 0.127054 | 0.000131576 | 0.0346562 | 0.00637634 | 0.0183561 | 0.00358574 | 0.00269185 |
| 14 | 10 | 0.000645273 | 0.00702937 | 0.0831025 | 0.00261353 | 0.0067904 | 0.00186921 | 0.00536476 | 0.00010621 | 0.00468078 |
| 14 | 100 | 0.01511 | 5.64181e-05 | 0.0580198 | 0.00703921 | 0.00929045 | 0.00302596 | 0.0140871 | 0.00257511 | 0.0024014 |
| 14 | 500 | 0.0312163 | -2.04213e-05 | 0.0713083 | -4.70728e-05 | 0.0185133 | 0.00331151 | 0.0376349 | 0.006768 | 0.000962273 |
| 14 | 2000 | 0.0277874 | 0.0031698 | 0.0777381 | 0.000827186 | 0.0388139 | 0.0027184 | 0.0330623 | 0.00440773 | 0.00171766 |
| 14 | 3000 | 0.0337044 | 0.000543315 | 0.0654071 | 0.001549 | 0.0341581 | 0.00341228 | 0.0211257 | 0.00187436 | 0.00145866 |
| 15 | 10 | 0.00201132 | 0.00716723 | 0.0879345 | 0.00401656 | 0.00942583 | 0.00387821 | 0.00819081 | 0.000200405 | 0.0123359 |
| 15 | 100 | 0.022396 | 0.000574763 | 0.051213 | 0.00972597 | 0.015562 | 0.00321534 | 0.0321384 | 0.00145159 | 0.00432367 |
| 15 | 500 | 0.0279999 | 0.000271855 | 0.0801271 | 0.000649921 | 0.0281007 | 0.00386887 | 0.031646 | 0.00409682 | 0.00124585 |
| 15 | 2000 | 0.0265349 | 0.00176508 | 0.0862688 | 0.000101711 | 0.0430196 | 0.00467578 | 0.0288344 | 0.005286 | 0.00162357 |
| 15 | 3000 | 0.022621 | 0.00147384 | 0.0659937 | 0.000170738 | 0.0355715 | 0.00521341 | 0.0218416 | 0.00398724 | 0.000627769 |
| 27 | 10 | 0.0137951 | 0.0141808 | 0.0477442 | 0.000853194 | 0.00868893 | 0.00416283 | 0.00731428 | 0.00250124 | 0.00436917 |
| 27 | 100 | 0.023671 | 0.00230849 | 0.0704768 | -0.003424 | 0.00490768 | 0.00285354 | 0.0340674 | 0.00281146 | -0.00137757 |
| 27 | 500 | 0.0187052 | 0.00240046 | 0.174274 | 0.000311907 | 0.0325341 | 0.00747468 | 0.0245311 | 0.00258772 | 0.00156853 |
| 27 | 2000 | 0.0189451 | 0.00280983 | 0.184187 | 0.000793463 | 0.0517645 | 0.0038348 | 0.0217127 | 0.00442306 | 0.00102888 |
| 27 | 3000 | 0.0187794 | 0.00346346 | 0.155226 | 0.000454312 | 0.0504483 | 0.00072592 | 0.0209574 | 0.00512663 | 0.000528481 |
| 28 | 10 | 0.0144249 | 0.00614606 | 0.0514898 | 0.00297458 | 0.00405993 | -0.00377106 | 0.0211558 | 0.000593305 | 0.00804262 |
| 28 | 100 | 0.0496307 | 0.00293082 | 0.0634148 | -0.00189186 | 0.0090043 | 0.0032236 | 0.020638 | 0.0065222 | 0.0011069 |
| 28 | 500 | 0.0207249 | 0.00194403 | 0.132793 | 0.000928303 | 0.0442255 | -0.00105533 | 0.019936 | 0.000521707 | -0.000533178 |
| 28 | 2000 | 0.00985334 | 0.00224782 | 0.189121 | -0.000213014 | 0.052774 | 0.000532882 | 0.0183144 | 0.00468799 | -0.000226365 |
| 28 | 3000 | 0.0117684 | 0.00280587 | 0.175741 | 3.43651e-05 | 0.0551313 | 0.0010132 | 0.017378 | 0.00277457 | 0.000648042 |

#### Qwen2.5-7B · ESS_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | 0.00569902 | -0.00221282 | 0.0881567 | -0.000134345 | 0.0166178 | 0.0256622 | 0.00222429 | 0.0148287 | 0.00296336 |
| 1 | 100 | 0.0364279 | 0.000994017 | 0.100702 | 0.00178812 | 0.0131406 | 0.020853 | 0.00544363 | 0.00884949 | 0.00205592 |
| 1 | 500 | 0.0495657 | 0.00149323 | 0.0623406 | -0.000569175 | 0.0144312 | 0.0114569 | 0.012075 | 0.002652 | 0.00109825 |
| 1 | 2000 | 0.0432553 | 0.00117247 | 0.060349 | -0.00118087 | 0.030111 | 0.00705142 | 0.0111573 | 0.0025844 | 0.000238182 |
| 1 | 3000 | 0.0295946 | 0.0037362 | 0.0725004 | -0.000868226 | 0.0419877 | 0.00613627 | 0.0107228 | 0.00267959 | 0.0010045 |
| 2 | 10 | 0.0342642 | -0.000588608 | 0.0957779 | -0.00115333 | 0.00506888 | 0.00408727 | 1.3746e-05 | 0.0043395 | 0.000158525 |
| 2 | 100 | 0.0960151 | 0.000508653 | 0.0877164 | 0.001835 | 0.0110994 | 0.00239211 | 0.00146025 | 0.00629851 | 0.000290546 |
| 2 | 500 | 0.120575 | 6.5269e-06 | 0.0594884 | -8.44541e-05 | 0.0135491 | -0.000707773 | 0.00670085 | 0.00234691 | -0.00133717 |
| 2 | 2000 | 0.124204 | 0.00218132 | 0.0476984 | 0.00203644 | 0.0431573 | -0.000195016 | 0.0124177 | 0.00218117 | 0.000907882 |
| 2 | 3000 | 0.142913 | 0.00274352 | 0.0482064 | 0.000411986 | 0.0380136 | 0.000430973 | 0.00994418 | 0.00335878 | 0.000153283 |
| 3 | 10 | 0.0229631 | -0.000542771 | 0.0571824 | -0.0018308 | 0.00558104 | 0.00781146 | -0.004772 | 0.00154272 | 0.00209429 |
| 3 | 100 | 0.0777853 | -0.000857892 | 0.0864846 | 0.000797864 | 0.00699461 | 8.25257e-05 | -0.00123136 | 0.00817553 | 0.00108109 |
| 3 | 500 | 0.033005 | 0.000686462 | 0.13472 | -3.1695e-05 | 0.00704737 | 0.00875336 | 0.00959103 | 0.00380177 | -0.000355271 |
| 3 | 2000 | 0.0261029 | 0.00285374 | 0.125733 | 0.0006696 | 0.0499531 | 0.000870649 | 0.0111637 | 0.00250232 | -0.000512807 |
| 3 | 3000 | 0.0204468 | 0.0018079 | 0.136152 | 0.000569274 | 0.0743889 | -5.63192e-05 | 0.0102412 | 0.00230592 | 0.000480222 |
| 4 | 10 | 0.0095666 | 0.0012231 | 0.0966999 | 0.00229549 | 0.01575 | 0.00406744 | 0.00338336 | 0.00407244 | 0.000230617 |
| 4 | 100 | 0.0281937 | -0.000349288 | 0.0877302 | 0.0011337 | 0.0222978 | 0.0026922 | 0.00970308 | 0.00482847 | -0.00105444 |
| 4 | 500 | 0.0106718 | 0.000606606 | 0.156366 | -0.00204969 | 0.0137944 | 0.00815111 | 0.0150203 | 0.00580938 | -0.000179094 |
| 4 | 2000 | 0.0138982 | 0.00172068 | 0.152084 | -0.000323131 | 0.0877723 | 0.00173388 | 0.0116782 | 0.00577284 | 0.00139992 |
| 4 | 3000 | 0.0163679 | 0.00251014 | 0.151406 | 0.000462767 | 0.0710059 | 0.000971272 | 0.0177867 | 0.0077098 | 0.000678352 |
| 5 | 10 | 0.0125169 | 0.00116322 | 0.0799733 | 0.00423655 | 0.0200761 | 0.0061558 | 0.0081291 | 0.00652527 | 0.00401226 |
| 5 | 100 | 0.0132833 | 0.000720481 | 0.0837242 | 0.00438721 | 0.00997908 | 0.00124461 | 0.00883856 | 0.00300257 | 0.00385191 |
| 5 | 500 | 0.0180399 | 0.000281843 | 0.1239 | 0.00214631 | 0.00963672 | 0.000659019 | 0.0128977 | 0.00200455 | 0.00249145 |
| 5 | 2000 | 0.0173577 | 0.00157155 | 0.127597 | 0.000209059 | 0.078325 | 0.000123962 | 0.0114582 | 0.0026829 | 0.000224535 |
| 5 | 3000 | 0.0187871 | 0.000716129 | 0.129463 | -0.000610018 | 0.0632669 | 0.00105993 | 0.0103743 | 0.00215803 | 0.000423507 |
| 6 | 10 | 0.00122295 | -0.00167726 | 0.0923936 | -8.05973e-06 | 0.00790867 | 0.00277517 | 0.0266159 | 0.00088568 | 0.000896657 |
| 6 | 100 | 0.00772711 | -0.00014196 | 0.116263 | 0.00741139 | 0.00827749 | 0.00698151 | 0.0143525 | 0.0018838 | 0.00530904 |
| 6 | 500 | 0.0130038 | -0.000297419 | 0.162045 | 0.00153041 | 0.00262787 | 0.00114419 | 0.0108762 | 0.000715536 | 0.00239695 |
| 6 | 2000 | 0.0251887 | 0.000877176 | 0.178593 | -0.000201444 | 0.0183387 | 0.00343414 | 0.0129243 | 0.00310295 | 0.000223052 |
| 6 | 3000 | 0.0272333 | 0.000318087 | 0.138952 | -0.000481705 | 0.0140196 | 0.0019822 | 0.0109354 | 0.00273611 | -3.96064e-05 |
| 14 | 10 | 0.00839641 | 0.000769828 | 0.0631312 | 0.00153585 | 0.00482382 | 0.000454411 | 0.0194568 | 0.00203046 | 0.00522612 |
| 14 | 100 | 0.00975766 | -0.000678254 | 0.0774026 | 0.00266802 | -0.00124738 | 0.00111209 | 0.0166635 | 0.000888845 | 0.00180241 |
| 14 | 500 | 0.0225213 | 0.000309335 | 0.062406 | 0.000210591 | 0.00147943 | -0.000142108 | 0.0191457 | -0.000104529 | 0.00176088 |
| 14 | 2000 | 0.0190903 | 0.000283525 | 0.126172 | 0.000814676 | 0.000587025 | 0.000667326 | 0.0120745 | 8.90032e-06 | 0.000710492 |
| 14 | 3000 | 0.018943 | -3.9557e-05 | 0.120338 | -5.22646e-05 | 0.00131418 | 0.000398042 | 0.0135002 | 1.55756e-05 | 0.000164705 |
| 15 | 10 | 0.00218532 | 0.000103639 | 0.0815127 | 0.00475939 | 0.00836046 | -0.000585394 | 0.0220318 | -9.55795e-05 | 0.00350242 |
| 15 | 100 | 0.00921702 | 0.00237564 | 0.087779 | 0.00363138 | -0.000360661 | 0.000710097 | 0.0163829 | 0.000848052 | 0.000486897 |
| 15 | 500 | 0.0174751 | -0.000328125 | 0.0720281 | -4.98418e-05 | 0.0025851 | 0.00166609 | 0.0255912 | 0.00115304 | 0.00237342 |
| 15 | 2000 | 0.0177191 | -3.16456e-06 | 0.161184 | 0.000139636 | 0.00170728 | 0.00139888 | 0.0173084 | 0.000187648 | 0.000407981 |
| 15 | 3000 | 0.0179946 | 0.000294205 | 0.124376 | 0.000733089 | 0.00144759 | 0.000935176 | 0.0107772 | 6.62085e-05 | 0.000400168 |
| 27 | 10 | 0.00460285 | 0.0036834 | 0.0558356 | 0.00233856 | 0.0115932 | 0.00404668 | 0.0337264 | 0.00110334 | 0.00112342 |
| 27 | 100 | 0.0091341 | 0.00487495 | 0.0530686 | 0.000343799 | 0.00861313 | 0.00994304 | 0.0246232 | 0.00179356 | 0.00848408 |
| 27 | 500 | 0.0197065 | 0.00354416 | 0.126995 | 5.75059e-05 | 0.0477427 | 0.00458673 | 0.0255911 | 0.00313059 | 0.00032585 |
| 27 | 2000 | 0.0126961 | 0.00238944 | 0.176671 | 0.000620896 | 0.108918 | 0.00147869 | 0.0161724 | 0.00637732 | 0.000407536 |
| 27 | 3000 | 0.0174988 | 0.00110023 | 0.131855 | 0.000459405 | 0.123242 | 0.00241703 | 0.0220674 | 0.00827092 | -9.40961e-05 |
| 28 | 100 | 0.0377332 | 0.00136111 | 0.0317009 | 0.000202433 | 0.0498715 | 0.00649723 | 0.0224683 | 0.002911 | 0.00735418 |
| 28 | 500 | 0.0197589 | 0.00371539 | 0.0570246 | 0.000915744 | 0.0619309 | 0.0097589 | 0.0109719 | 0.00484963 | -2.44264e-05 |
| 28 | 2000 | 0.00771845 | 0.00367667 | 0.151212 | 0.00053753 | 0.0491696 | 0.00026696 | 0.00594279 | 0.000279519 | -0.000387856 |
| 28 | 3000 | 0.00517563 | 0.00284291 | 0.167396 | 0.00028308 | 0.0549633 | -0.0017989 | 0.00552517 | 0.00183015 | -0.000787431 |

#### Qwen2.5-7B · MLE · RIDGE · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500 | 0.00767778 | 0.0663332 | 0.140253 | 0.00295063 | 0.0345953 | 0.00711247 | 0.0406172 | 0.00594011 | -0.000697032 |
| 1 | 2000 | 0.0115367 | 0.0656898 | 0.133121 | 0.00670623 | 0.0314762 | 0.00532478 | 0.0085469 | 0.0234885 | -0.000800352 |
| 1 | 3000 | 0.00783239 | 0.0433428 | 0.119084 | 0.0044861 | 0.0167101 | 0.0105078 | 0.00506423 | 0.0226581 | -0.00083777 |
| 3 | 10 | 0.0113082 | 0.00139152 | 0.1383 | 0.00629103 | 0.0163747 | 0.0098555 | 0.0476238 | 0.00159736 | 0.00314735 |
| 3 | 2000 | 0.0230452 | 0.007552 | 0.188169 | 0.0276975 | 0.03551 | 0.0271077 | 0.152657 | 0.0178654 | 0.000139363 |
| 3 | 3000 | 0.0197687 | 0.00377926 | 0.237076 | 0.00331173 | 0.0227022 | 0.0270729 | 0.175612 | 0.012761 | 0.000736529 |
| 4 | 10 | 0.0010874 | -0.00256952 | 0.112614 | 0.00944423 | 0.00850781 | 0.0199421 | 0.00666764 | 0.00852996 | 0.0084454 |
| 4 | 2000 | 0.0371916 | -0.000215008 | 0.246988 | 0.0522631 | 0.037342 | 0.0282524 | 0.26297 | 0.00108918 | 0.00181592 |
| 4 | 3000 | 0.0331824 | 0.00275395 | 0.300793 | 0.0183318 | 0.0382704 | 0.0282819 | 0.286999 | 0.001252 | 0.00221331 |
| 5 | 10 | 0.00781378 | -0.00294666 | 0.0970776 | 0.00469672 | 0.00869063 | 0.0113871 | 0.0412083 | 0.0120603 | 0.00779733 |
| 5 | 2000 | 0.0479742 | 0.00217913 | 0.230269 | 0.155037 | 0.0564827 | 0.0266615 | 0.249078 | 0.000146206 | 0.00263093 |
| 5 | 3000 | 0.0474171 | 0.00464278 | 0.213422 | 0.0811444 | 0.0569577 | 0.0275502 | 0.260031 | 0.000527767 | 0.00361991 |
| 6 | 3000 | 0.0361678 | 0.00289282 | 0.186924 | 0.0414167 | 0.0751692 | 0.0235732 | 0.242951 | 0.00152851 | 0.00131258 |
| 28 | 10 | 0.0321488 | 0.00348531 | 0.0464956 | 0.016518 | 0.00803029 | 0.0308465 | 0.007858 | 0.00189991 | 0.0137287 |

#### Qwen2.5-7B · ESS_LOW_VS_HIGH · LOGREG · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 10 | 0.017278 | 0.000761027 | 0.0207918 | 0.000653283 | 0.124028 | 0.0215376 | 0.0143839 | -0.00218216 | 0.0231407 |

#### Apertus-8B · MLE · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.219824 | -0.000975079 | 0.176632 | -0.00116584 | 0.00504275 | 0.00554489 | 0.022044 | 0.00805288 | 0.00138777 |
| 16 | 1000 | 0.130289 | 0.00156724 | 0.167763 | 0.0024823 | 0.0355986 | 0.00417999 | 0.0797083 | 0.00758413 | 0.00116041 |
| 31 | 1000 | 0.0909906 | 0.0126873 | 0.189131 | 0.00321246 | 0.0288502 | 0.00230321 | 0.0481428 | 0.00476345 | 0.00306306 |

#### Apertus-8B · ESS · RF · id run · R² decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.434395 | -0.00029113 | 0.0420456 | -0.000728771 | 0.0408354 | 0.00807502 | 0.0100423 | 0.00181826 | -0.000596306 |
| 16 | 1000 | 0.131098 | 0.00146811 | 0.301642 | 0.00119116 | 0.033021 | 0.00349465 | 0.083876 | 0.00401918 | 0.000716983 |
| 31 | 1000 | 0.123127 | 0.00425238 | 0.233252 | 0.00114528 | 0.053932 | 0.00443603 | 0.0799272 | 0.00402846 | 0.000951417 |

#### Apertus-8B · MLE_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.082678 | 0.000450949 | 0.126016 | -0.000251384 | 0.00297473 | 0.00325341 | 0.00494956 | 0.0060938 | -0.000704015 |
| 16 | 1000 | 0.0456218 | 0.000369462 | 0.13018 | 0.000728738 | 0.0139351 | 0.00221934 | 0.0281614 | 0.0034821 | 0.000591228 |
| 31 | 1000 | 0.0358178 | 0.00209251 | 0.208778 | 0.00259311 | 0.0218185 | 0.0019149 | 0.0223352 | 0.00360839 | -0.000195955 |

#### Apertus-8B · ESS_LOW_VS_HIGH · RF · id run · ROC-AUC decrease · eval_known, reference size 15000, all_existing_features

| Layer | K | Surface | Frequency | UPOS | Lexical | Predicate | Tree | Relations | Subordination | Verb edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | 0.155627 | 0.000412035 | 0.0450058 | 0.000186659 | 0.0129672 | 0.00239379 | 0.00781265 | 0.000173655 | 0.000155904 |
| 16 | 1000 | 0.0241327 | -0.000222458 | 0.118059 | 0.00247463 | 0.00379158 | 0.0017636 | 0.023556 | 0.00200074 | 0.000581833 |
| 31 | 1000 | 0.0327097 | 0.00299283 | 0.147675 | 0.000547716 | 0.0115316 | 0.000800435 | 0.040834 | 0.00206151 | -0.00034375 |

### Full-feature regression across available layers and neighbourhood sizes

All archived full-feature Ridge and random-forest regression settings. R² mean and SD are across validation folds. Historical run labels are retained; overlapping runs must not be pooled as independent replicates.

[Download the CSV](tables/layer_neighbourhood_regression.csv)

#### Pythia-1.4B · MLE · id run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1994 | 46 | 5 | 0.0308689 | 0.0185987 |
| 1 | 10 | ridge | 1994 | 46 | 5 | 0.0305992 | 0.0174458 |
| 1 | 100 | rf | 1994 | 46 | 5 | 0.0749917 | 0.0307416 |
| 1 | 100 | ridge | 1994 | 46 | 5 | 0.039251 | 0.0258152 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.0672067 | 0.0449768 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.0410625 | 0.034312 |
| 1 | 1000 | rf | 1994 | 46 | 5 | 0.0491443 | 0.0399265 |
| 1 | 1000 | ridge | 1994 | 46 | 5 | 0.023518 | 0.0380317 |
| 2 | 10 | rf | 1994 | 46 | 5 | -0.00502218 | 0.0187153 |
| 2 | 10 | ridge | 1994 | 46 | 5 | -0.00342155 | 0.0129817 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.0889082 | 0.0224473 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.0409022 | 0.00754314 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.0905606 | 0.038249 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.0665746 | 0.040998 |
| 2 | 1000 | rf | 1994 | 46 | 5 | 0.129357 | 0.0480789 |
| 2 | 1000 | ridge | 1994 | 46 | 5 | 0.088635 | 0.0650021 |
| 12 | 10 | rf | 1994 | 46 | 5 | 0.0379828 | 0.0222075 |
| 12 | 10 | ridge | 1994 | 46 | 5 | 0.0241341 | 0.0170065 |
| 12 | 100 | rf | 1994 | 46 | 5 | 0.109099 | 0.0285329 |
| 12 | 100 | ridge | 1994 | 46 | 5 | 0.052474 | 0.037447 |
| 12 | 500 | rf | 1994 | 46 | 5 | 0.169732 | 0.0212163 |
| 12 | 500 | ridge | 1994 | 46 | 5 | 0.123982 | 0.0444862 |
| 12 | 1000 | rf | 1994 | 46 | 5 | 0.175544 | 0.0320411 |
| 12 | 1000 | ridge | 1994 | 46 | 5 | 0.146211 | 0.0479965 |
| 13 | 10 | rf | 1994 | 46 | 5 | 0.0382266 | 0.0283537 |
| 13 | 10 | ridge | 1994 | 46 | 5 | 0.0192945 | 0.0222871 |
| 13 | 100 | rf | 1994 | 46 | 5 | 0.125842 | 0.0185718 |
| 13 | 100 | ridge | 1994 | 46 | 5 | 0.0684409 | 0.0384659 |
| 13 | 500 | rf | 1994 | 46 | 5 | 0.193484 | 0.0266476 |
| 13 | 500 | ridge | 1994 | 46 | 5 | 0.137409 | 0.0408147 |
| 13 | 1000 | rf | 1994 | 46 | 5 | 0.20292 | 0.0324805 |
| 13 | 1000 | ridge | 1994 | 46 | 5 | 0.159894 | 0.0460013 |
| 23 | 10 | rf | 1994 | 46 | 5 | -0.000600915 | 0.017559 |
| 23 | 10 | ridge | 1994 | 46 | 5 | -0.00834856 | 0.0276461 |
| 23 | 100 | rf | 1994 | 46 | 5 | 0.0908272 | 0.0249525 |
| 23 | 100 | ridge | 1994 | 46 | 5 | 0.0415868 | 0.0287443 |
| 23 | 500 | rf | 1994 | 46 | 5 | 0.17842 | 0.0222572 |
| 23 | 500 | ridge | 1994 | 46 | 5 | 0.0644785 | 0.0137703 |
| 23 | 1000 | rf | 1994 | 46 | 5 | 0.217149 | 0.0296354 |
| 23 | 1000 | ridge | 1994 | 46 | 5 | 0.0811358 | 0.014572 |
| 24 | 10 | rf | 1994 | 46 | 5 | -0.032289 | 0.0248961 |
| 24 | 10 | ridge | 1994 | 46 | 5 | -0.0231505 | 0.0150399 |
| 24 | 100 | rf | 1994 | 46 | 5 | 0.00735754 | 0.0351849 |
| 24 | 100 | ridge | 1994 | 46 | 5 | -0.00754311 | 0.0426584 |
| 24 | 500 | rf | 1994 | 46 | 5 | 0.0744971 | 0.0635806 |
| 24 | 500 | ridge | 1994 | 46 | 5 | 0.043302 | 0.0717706 |
| 24 | 1000 | rf | 1994 | 46 | 5 | 0.168313 | 0.0810261 |
| 24 | 1000 | ridge | 1994 | 46 | 5 | 0.11171 | 0.0791121 |

#### Pythia-1.4B · ESS · id run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1994 | 46 | 5 | 0.13195 | 0.0328613 |
| 1 | 10 | ridge | 1994 | 46 | 5 | 0.0941785 | 0.0243629 |
| 1 | 100 | rf | 1994 | 46 | 5 | 0.18228 | 0.0377014 |
| 1 | 100 | ridge | 1994 | 46 | 5 | 0.132865 | 0.0236191 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.177475 | 0.0529558 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.140378 | 0.023169 |
| 1 | 1000 | rf | 1994 | 46 | 5 | 0.178653 | 0.0509315 |
| 1 | 1000 | ridge | 1994 | 46 | 5 | 0.140764 | 0.0224805 |
| 2 | 10 | rf | 1994 | 46 | 5 | 0.127937 | 0.0266035 |
| 2 | 10 | ridge | 1994 | 46 | 5 | 0.0936682 | 0.0206939 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.174936 | 0.0285504 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.1331 | 0.0274318 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.244412 | 0.0444075 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.18553 | 0.0154294 |
| 2 | 1000 | rf | 1994 | 46 | 5 | 0.283018 | 0.050198 |
| 2 | 1000 | ridge | 1994 | 46 | 5 | 0.211015 | 0.0142012 |
| 12 | 10 | rf | 1994 | 46 | 5 | 0.141237 | 0.0219555 |
| 12 | 10 | ridge | 1994 | 46 | 5 | 0.124575 | 0.0254861 |
| 12 | 100 | rf | 1994 | 46 | 5 | 0.257897 | 0.00657335 |
| 12 | 100 | ridge | 1994 | 46 | 5 | 0.207203 | 0.0185465 |
| 12 | 500 | rf | 1994 | 46 | 5 | 0.410276 | 0.019383 |
| 12 | 500 | ridge | 1994 | 46 | 5 | 0.295719 | 0.0280595 |
| 12 | 1000 | rf | 1994 | 46 | 5 | 0.50135 | 0.0310057 |
| 12 | 1000 | ridge | 1994 | 46 | 5 | 0.370634 | 0.0424105 |
| 13 | 10 | rf | 1994 | 46 | 5 | 0.122949 | 0.0377068 |
| 13 | 10 | ridge | 1994 | 46 | 5 | 0.112926 | 0.0189395 |
| 13 | 100 | rf | 1994 | 46 | 5 | 0.271677 | 0.0196539 |
| 13 | 100 | ridge | 1994 | 46 | 5 | 0.2287 | 0.0225455 |
| 13 | 500 | rf | 1994 | 46 | 5 | 0.439906 | 0.0188395 |
| 13 | 500 | ridge | 1994 | 46 | 5 | 0.321123 | 0.0337205 |
| 13 | 1000 | rf | 1994 | 46 | 5 | 0.540538 | 0.0210339 |
| 13 | 1000 | ridge | 1994 | 46 | 5 | 0.399645 | 0.0417117 |
| 23 | 10 | rf | 1994 | 46 | 5 | 0.0606699 | 0.0204669 |
| 23 | 10 | ridge | 1994 | 46 | 5 | 0.0470182 | 0.0270652 |
| 23 | 100 | rf | 1994 | 46 | 5 | 0.147782 | 0.015061 |
| 23 | 100 | ridge | 1994 | 46 | 5 | 0.0912497 | 0.0245549 |
| 23 | 500 | rf | 1994 | 46 | 5 | 0.239692 | 0.0261258 |
| 23 | 500 | ridge | 1994 | 46 | 5 | 0.136263 | 0.0170359 |
| 23 | 1000 | rf | 1994 | 46 | 5 | 0.278881 | 0.0162822 |
| 23 | 1000 | ridge | 1994 | 46 | 5 | 0.154361 | 0.0159459 |
| 24 | 10 | rf | 1994 | 46 | 5 | 0.0804198 | 0.0430284 |
| 24 | 10 | ridge | 1994 | 46 | 5 | 0.0480603 | 0.036438 |
| 24 | 100 | rf | 1994 | 46 | 5 | 0.194612 | 0.0496937 |
| 24 | 100 | ridge | 1994 | 46 | 5 | 0.13165 | 0.0376787 |
| 24 | 500 | rf | 1994 | 46 | 5 | 0.321543 | 0.0353021 |
| 24 | 500 | ridge | 1994 | 46 | 5 | 0.219363 | 0.0343572 |
| 24 | 1000 | rf | 1994 | 46 | 5 | 0.391869 | 0.0382737 |
| 24 | 1000 | ridge | 1994 | 46 | 5 | 0.264138 | 0.032619 |

#### Pythia-6.9B · ESS · ess run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1994 | 46 | 5 | 0.142391 | 0.0627808 |
| 1 | 10 | ridge | 1994 | 46 | 5 | 0.103488 | 0.0305534 |
| 1 | 100 | rf | 1994 | 46 | 5 | 0.184906 | 0.0648045 |
| 1 | 100 | ridge | 1994 | 46 | 5 | 0.139912 | 0.0315897 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.200416 | 0.07241 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.157246 | 0.0271204 |
| 1 | 2000 | rf | 1994 | 46 | 5 | 0.258182 | 0.0666397 |
| 1 | 2000 | ridge | 1994 | 46 | 5 | 0.194493 | 0.0248965 |
| 1 | 3000 | rf | 1994 | 46 | 5 | 0.299172 | 0.0682809 |
| 1 | 3000 | ridge | 1994 | 46 | 5 | 0.230747 | 0.0260114 |
| 2 | 10 | rf | 1994 | 46 | 5 | 0.16666 | 0.0532527 |
| 2 | 10 | ridge | 1994 | 46 | 5 | 0.120339 | 0.0432035 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.183582 | 0.0433643 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.146306 | 0.0271935 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.203745 | 0.0630566 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.146833 | 0.01785 |
| 2 | 2000 | rf | 1994 | 46 | 5 | 0.374432 | 0.0394624 |
| 2 | 2000 | ridge | 1994 | 46 | 5 | 0.251386 | 0.020563 |
| 2 | 3000 | rf | 1994 | 46 | 5 | 0.490582 | 0.0295491 |
| 2 | 3000 | ridge | 1994 | 46 | 5 | 0.356212 | 0.0150802 |
| 16 | 10 | rf | 1994 | 46 | 5 | 0.171278 | 0.0265583 |
| 16 | 10 | ridge | 1994 | 46 | 5 | 0.139925 | 0.00972632 |
| 16 | 100 | rf | 1994 | 46 | 5 | 0.327198 | 0.0250462 |
| 16 | 100 | ridge | 1994 | 46 | 5 | 0.245354 | 0.0304402 |
| 16 | 500 | rf | 1994 | 46 | 5 | 0.457416 | 0.0371547 |
| 16 | 500 | ridge | 1994 | 46 | 5 | 0.330518 | 0.0409927 |
| 16 | 2000 | rf | 1994 | 46 | 5 | 0.506708 | 0.036401 |
| 16 | 2000 | ridge | 1994 | 46 | 5 | 0.349339 | 0.0411869 |
| 16 | 3000 | rf | 1994 | 46 | 5 | 0.515455 | 0.0239398 |
| 16 | 3000 | ridge | 1994 | 46 | 5 | 0.349647 | 0.0408212 |
| 17 | 10 | rf | 1994 | 46 | 5 | 0.159001 | 0.0287309 |
| 17 | 10 | ridge | 1994 | 46 | 5 | 0.129685 | 0.0133735 |
| 17 | 100 | rf | 1994 | 46 | 5 | 0.312183 | 0.0249431 |
| 17 | 100 | ridge | 1994 | 46 | 5 | 0.243037 | 0.0304867 |
| 17 | 500 | rf | 1994 | 46 | 5 | 0.438301 | 0.0424866 |
| 17 | 500 | ridge | 1994 | 46 | 5 | 0.316534 | 0.0411488 |
| 17 | 2000 | rf | 1994 | 46 | 5 | 0.502413 | 0.0360071 |
| 17 | 2000 | ridge | 1994 | 46 | 5 | 0.34879 | 0.0416655 |
| 17 | 3000 | rf | 1994 | 46 | 5 | 0.49746 | 0.0283172 |
| 17 | 3000 | ridge | 1994 | 46 | 5 | 0.339211 | 0.0414304 |
| 31 | 10 | rf | 1994 | 46 | 5 | 0.0760489 | 0.019771 |
| 31 | 10 | ridge | 1994 | 46 | 5 | 0.0320171 | 0.0193743 |
| 31 | 100 | rf | 1994 | 46 | 5 | 0.110913 | 0.0322301 |
| 31 | 100 | ridge | 1994 | 46 | 5 | 0.0548503 | 0.0251684 |
| 31 | 500 | rf | 1994 | 46 | 5 | 0.230361 | 0.0289266 |
| 31 | 500 | ridge | 1994 | 46 | 5 | 0.129362 | 0.0234104 |
| 31 | 2000 | rf | 1994 | 46 | 5 | 0.248211 | 0.0270634 |
| 31 | 2000 | ridge | 1994 | 46 | 5 | 0.134587 | 0.0356778 |
| 31 | 3000 | rf | 1994 | 46 | 5 | 0.243579 | 0.032334 |
| 31 | 3000 | ridge | 1994 | 46 | 5 | 0.133904 | 0.0419637 |
| 32 | 10 | rf | 1994 | 46 | 5 | 0.0969853 | 0.0662704 |
| 32 | 10 | ridge | 1994 | 46 | 5 | 0.0388987 | 0.0500662 |
| 32 | 100 | rf | 1994 | 46 | 5 | 0.233827 | 0.033767 |
| 32 | 100 | ridge | 1994 | 46 | 5 | 0.14714 | 0.0427193 |
| 32 | 500 | rf | 1994 | 46 | 5 | 0.351232 | 0.0147204 |
| 32 | 500 | ridge | 1994 | 46 | 5 | 0.221325 | 0.026045 |
| 32 | 2000 | rf | 1994 | 46 | 5 | 0.456491 | 0.0283488 |
| 32 | 2000 | ridge | 1994 | 46 | 5 | 0.345499 | 0.0128465 |
| 32 | 3000 | rf | 1994 | 46 | 5 | 0.506163 | 0.022885 |
| 32 | 3000 | ridge | 1994 | 46 | 5 | 0.399252 | 0.010312 |

#### Pythia-6.9B · FCI · fci_pyfci run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1993 | 46 | 5 | 0.0556729 | 0.0119217 |
| 1 | 10 | ridge | 1993 | 46 | 5 | 0.0547047 | 0.00955585 |
| 1 | 100 | rf | 1993 | 46 | 5 | 0.178768 | 0.0212681 |
| 1 | 100 | ridge | 1993 | 46 | 5 | 0.123705 | 0.0518816 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.183649 | 0.0682147 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.139192 | 0.0276466 |
| 1 | 2000 | rf | 1994 | 46 | 5 | 0.235419 | 0.0625611 |
| 1 | 2000 | ridge | 1994 | 46 | 5 | 0.178883 | 0.0244685 |
| 1 | 3000 | rf | 1994 | 46 | 5 | 0.346988 | 0.0540199 |
| 1 | 3000 | ridge | 1994 | 46 | 5 | 0.263819 | 0.025312 |
| 2 | 10 | rf | 1993 | 46 | 5 | 0.0594382 | 0.0250206 |
| 2 | 10 | ridge | 1993 | 46 | 5 | 0.0567306 | 0.0290001 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.163461 | 0.0340441 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.12505 | 0.0252349 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.182672 | 0.0583562 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.131574 | 0.0153056 |
| 2 | 2000 | rf | 1994 | 46 | 5 | 0.381437 | 0.0363347 |
| 2 | 2000 | ridge | 1994 | 46 | 5 | 0.254338 | 0.0286164 |
| 2 | 3000 | rf | 1994 | 46 | 5 | 0.494763 | 0.00982117 |
| 2 | 3000 | ridge | 1994 | 46 | 5 | 0.364647 | 0.0321387 |
| 16 | 10 | rf | 1993 | 46 | 5 | 0.0678856 | 0.0315691 |
| 16 | 10 | ridge | 1993 | 46 | 5 | 0.0627154 | 0.0211293 |
| 16 | 100 | rf | 1994 | 46 | 5 | 0.298903 | 0.034074 |
| 16 | 100 | ridge | 1994 | 46 | 5 | 0.219054 | 0.0456198 |
| 16 | 500 | rf | 1994 | 46 | 5 | 0.396712 | 0.0296868 |
| 16 | 500 | ridge | 1994 | 46 | 5 | 0.283408 | 0.045703 |
| 16 | 2000 | rf | 1994 | 46 | 5 | 0.41657 | 0.036318 |
| 16 | 2000 | ridge | 1994 | 46 | 5 | 0.266306 | 0.0356288 |
| 16 | 3000 | rf | 1994 | 46 | 5 | 0.433977 | 0.0263985 |
| 16 | 3000 | ridge | 1994 | 46 | 5 | 0.275532 | 0.0357866 |
| 17 | 10 | rf | 1993 | 46 | 5 | 0.0637037 | 0.0393075 |
| 17 | 10 | ridge | 1993 | 46 | 5 | 0.0559642 | 0.0196774 |
| 17 | 100 | rf | 1994 | 46 | 5 | 0.294824 | 0.0313721 |
| 17 | 100 | ridge | 1994 | 46 | 5 | 0.221816 | 0.0389363 |
| 17 | 500 | rf | 1994 | 46 | 5 | 0.395231 | 0.0285996 |
| 17 | 500 | ridge | 1994 | 46 | 5 | 0.263173 | 0.0389378 |
| 17 | 2000 | rf | 1994 | 46 | 5 | 0.390121 | 0.0387368 |
| 17 | 2000 | ridge | 1994 | 46 | 5 | 0.261072 | 0.033545 |
| 17 | 3000 | rf | 1994 | 46 | 5 | 0.421269 | 0.0265674 |
| 17 | 3000 | ridge | 1994 | 46 | 5 | 0.264098 | 0.034504 |
| 31 | 10 | rf | 1994 | 46 | 5 | 0.0171932 | 0.0307313 |
| 31 | 10 | ridge | 1994 | 46 | 5 | 0.0145074 | 0.0172802 |
| 31 | 100 | rf | 1994 | 46 | 5 | 0.0430123 | 0.0475755 |
| 31 | 100 | ridge | 1994 | 46 | 5 | 0.00877117 | 0.0129561 |
| 31 | 500 | rf | 1994 | 46 | 5 | 0.197554 | 0.0811654 |
| 31 | 500 | ridge | 1994 | 46 | 5 | 0.0858023 | 0.0248304 |
| 31 | 2000 | rf | 1994 | 46 | 5 | 0.214123 | 0.0291585 |
| 31 | 2000 | ridge | 1994 | 46 | 5 | 0.104001 | 0.038741 |
| 31 | 3000 | rf | 1994 | 46 | 5 | 0.245301 | 0.0124892 |
| 31 | 3000 | ridge | 1994 | 46 | 5 | 0.12674 | 0.0383804 |
| 32 | 10 | rf | 1993 | 46 | 5 | 0.0361238 | 0.0207756 |
| 32 | 10 | ridge | 1993 | 46 | 5 | 0.0186846 | 0.0245189 |
| 32 | 100 | rf | 1994 | 46 | 5 | 0.204966 | 0.0347874 |
| 32 | 100 | ridge | 1994 | 46 | 5 | 0.130105 | 0.0447449 |
| 32 | 500 | rf | 1994 | 46 | 5 | 0.334058 | 0.0246422 |
| 32 | 500 | ridge | 1994 | 46 | 5 | 0.225769 | 0.018868 |
| 32 | 2000 | rf | 1994 | 46 | 5 | 0.455178 | 0.0193194 |
| 32 | 2000 | ridge | 1994 | 46 | 5 | 0.341511 | 0.0150367 |
| 32 | 3000 | rf | 1994 | 46 | 5 | 0.503216 | 0.0055742 |
| 32 | 3000 | ridge | 1994 | 46 | 5 | 0.399648 | 0.0302831 |

#### Pythia-6.9B · MLE · id run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1994 | 46 | 5 | 0.0237507 | 0.0290025 |
| 1 | 10 | ridge | 1994 | 46 | 5 | 0.0147659 | 0.00957236 |
| 1 | 100 | rf | 1994 | 46 | 5 | 0.0866581 | 0.0425261 |
| 1 | 100 | ridge | 1994 | 46 | 5 | 0.0358017 | 0.0343468 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.0623959 | 0.0552568 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.03543 | 0.0331242 |
| 1 | 2000 | rf | 1994 | 46 | 5 | 0.0689835 | 0.0292328 |
| 1 | 2000 | ridge | 1994 | 46 | 5 | 0.038915 | 0.0228206 |
| 1 | 3000 | rf | 1994 | 46 | 5 | 0.0711085 | 0.0389503 |
| 1 | 3000 | ridge | 1994 | 46 | 5 | 0.0498583 | 0.0228257 |
| 2 | 10 | rf | 1994 | 46 | 5 | 0.0223926 | 0.0195402 |
| 2 | 10 | ridge | 1994 | 46 | 5 | 0.0212025 | 0.0101525 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.0709007 | 0.036808 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.0268546 | 0.0301679 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.0986539 | 0.0399791 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.0400808 | 0.0469067 |
| 2 | 2000 | rf | 1994 | 46 | 5 | 0.147641 | 0.0789578 |
| 2 | 2000 | ridge | 1994 | 46 | 5 | 0.121772 | 0.0565905 |
| 2 | 3000 | rf | 1994 | 46 | 5 | 0.146919 | 0.0815513 |
| 2 | 3000 | ridge | 1994 | 46 | 5 | 0.122654 | 0.0610919 |
| 16 | 10 | rf | 1994 | 46 | 5 | 0.0578521 | 0.00819628 |
| 16 | 10 | ridge | 1994 | 46 | 5 | 0.0380747 | 0.0237247 |
| 16 | 100 | rf | 1994 | 46 | 5 | 0.168313 | 0.0296972 |
| 16 | 100 | ridge | 1994 | 46 | 5 | 0.103556 | 0.0470892 |
| 16 | 500 | rf | 1994 | 46 | 5 | 0.246845 | 0.0376692 |
| 16 | 500 | ridge | 1994 | 46 | 5 | 0.176275 | 0.0536296 |
| 16 | 2000 | rf | 1994 | 46 | 5 | 0.267795 | 0.065365 |
| 16 | 2000 | ridge | 1994 | 46 | 5 | 0.205803 | 0.0597921 |
| 16 | 3000 | rf | 1994 | 46 | 5 | 0.265433 | 0.0712806 |
| 16 | 3000 | ridge | 1994 | 46 | 5 | 0.21307 | 0.0611199 |
| 17 | 10 | rf | 1994 | 46 | 5 | 0.054739 | 0.0120322 |
| 17 | 10 | ridge | 1994 | 46 | 5 | 0.0351815 | 0.0324352 |
| 17 | 100 | rf | 1994 | 46 | 5 | 0.164924 | 0.0322953 |
| 17 | 100 | ridge | 1994 | 46 | 5 | 0.100595 | 0.0500282 |
| 17 | 500 | rf | 1994 | 46 | 5 | 0.238988 | 0.0262889 |
| 17 | 500 | ridge | 1994 | 46 | 5 | 0.16967 | 0.052211 |
| 17 | 2000 | rf | 1994 | 46 | 5 | 0.254219 | 0.0604668 |
| 17 | 2000 | ridge | 1994 | 46 | 5 | 0.194916 | 0.0560814 |
| 17 | 3000 | rf | 1994 | 46 | 5 | 0.255055 | 0.0641232 |
| 17 | 3000 | ridge | 1994 | 46 | 5 | 0.204648 | 0.0574637 |
| 31 | 10 | rf | 1994 | 46 | 5 | -0.00294844 | 0.0186106 |
| 31 | 10 | ridge | 1994 | 46 | 5 | -0.00159199 | 0.0213334 |
| 31 | 100 | rf | 1994 | 46 | 5 | 0.0881715 | 0.0520862 |
| 31 | 100 | ridge | 1994 | 46 | 5 | 0.0369283 | 0.0486206 |
| 31 | 500 | rf | 1994 | 46 | 5 | 0.194874 | 0.0199954 |
| 31 | 500 | ridge | 1994 | 46 | 5 | 0.0704608 | 0.0270455 |
| 31 | 2000 | rf | 1994 | 46 | 5 | 0.205096 | 0.0216419 |
| 31 | 2000 | ridge | 1994 | 46 | 5 | 0.07127 | 0.0198478 |
| 31 | 3000 | rf | 1994 | 46 | 5 | 0.176327 | 0.0258865 |
| 31 | 3000 | ridge | 1994 | 46 | 5 | 0.0655931 | 0.0288498 |
| 32 | 10 | rf | 1994 | 46 | 5 | 0.000134306 | 0.0165354 |
| 32 | 10 | ridge | 1994 | 46 | 5 | -0.0173891 | 0.015263 |
| 32 | 100 | rf | 1994 | 46 | 5 | 0.0506947 | 0.021758 |
| 32 | 100 | ridge | 1994 | 46 | 5 | 0.00389276 | 0.048306 |
| 32 | 500 | rf | 1994 | 46 | 5 | 0.136185 | 0.067529 |
| 32 | 500 | ridge | 1994 | 46 | 5 | 0.0948995 | 0.0607472 |
| 32 | 2000 | rf | 1994 | 46 | 5 | 0.230461 | 0.0933035 |
| 32 | 2000 | ridge | 1994 | 46 | 5 | 0.187848 | 0.0592319 |
| 32 | 3000 | rf | 1994 | 46 | 5 | 0.229161 | 0.0846855 |
| 32 | 3000 | ridge | 1994 | 46 | 5 | 0.185831 | 0.054309 |

#### Qwen2.5-7B · FCI · fci_pyfci run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1992 | 46 | 5 | 0.0187126 | 0.0169255 |
| 1 | 10 | ridge | 1992 | 46 | 5 | 0.00822468 | 0.0316402 |
| 1 | 100 | rf | 1994 | 46 | 5 | 0.142392 | 0.0320554 |
| 1 | 100 | ridge | 1994 | 46 | 5 | 0.102198 | 0.0266636 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.129251 | 0.0357743 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.0985404 | 0.023848 |
| 1 | 2000 | rf | 1994 | 46 | 5 | 0.179206 | 0.0437435 |
| 1 | 2000 | ridge | 1994 | 46 | 5 | 0.119786 | 0.0290219 |
| 1 | 3000 | rf | 1994 | 46 | 5 | 0.192262 | 0.0569847 |
| 1 | 3000 | ridge | 1994 | 46 | 5 | 0.146414 | 0.0446521 |
| 2 | 10 | rf | 1994 | 46 | 5 | 0.0091417 | 0.0163511 |
| 2 | 10 | ridge | 1994 | 46 | 5 | 0.0376662 | 0.0175368 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.189396 | 0.0247124 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.144082 | 0.0165747 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.176245 | 0.0432458 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.138234 | 0.0162768 |
| 2 | 2000 | rf | 1994 | 46 | 5 | 0.319845 | 0.061479 |
| 2 | 2000 | ridge | 1994 | 46 | 5 | 0.208925 | 0.0461334 |
| 2 | 3000 | rf | 1994 | 46 | 5 | 0.364726 | 0.0506295 |
| 2 | 3000 | ridge | 1994 | 46 | 5 | 0.248253 | 0.0358148 |
| 3 | 10 | rf | 1993 | 46 | 5 | 0.0329842 | 0.0193922 |
| 3 | 10 | ridge | 1993 | 46 | 5 | 0.0267782 | 0.0141574 |
| 3 | 100 | rf | 1994 | 46 | 5 | 0.153479 | 0.0532972 |
| 3 | 100 | ridge | 1994 | 46 | 5 | 0.108432 | 0.0212705 |
| 3 | 500 | rf | 1994 | 46 | 5 | 0.148317 | 0.0417873 |
| 3 | 500 | ridge | 1994 | 46 | 5 | 0.100001 | 0.0256495 |
| 3 | 2000 | rf | 1994 | 46 | 5 | 0.363471 | 0.0110739 |
| 3 | 2000 | ridge | 1994 | 46 | 5 | 0.200011 | 0.0109674 |
| 3 | 3000 | rf | 1994 | 46 | 5 | 0.472481 | 0.0150937 |
| 3 | 3000 | ridge | 1994 | 46 | 5 | 0.296611 | 0.0177682 |
| 4 | 10 | rf | 1993 | 46 | 5 | 0.0272467 | 0.00729372 |
| 4 | 10 | ridge | 1993 | 46 | 5 | 0.0284259 | 0.0209797 |
| 4 | 100 | rf | 1994 | 46 | 5 | 0.11632 | 0.0415289 |
| 4 | 100 | ridge | 1994 | 46 | 5 | 0.0965299 | 0.0218151 |
| 4 | 500 | rf | 1994 | 46 | 5 | 0.139663 | 0.0457266 |
| 4 | 500 | ridge | 1994 | 46 | 5 | 0.103562 | 0.0295759 |
| 4 | 2000 | rf | 1994 | 46 | 5 | 0.399355 | 0.0251938 |
| 4 | 2000 | ridge | 1994 | 46 | 5 | 0.228396 | 0.0227913 |
| 4 | 3000 | rf | 1994 | 46 | 5 | 0.400345 | 0.038524 |
| 4 | 3000 | ridge | 1994 | 46 | 5 | 0.260009 | 0.0158093 |
| 5 | 10 | rf | 1993 | 46 | 5 | 0.0287701 | 0.018834 |
| 5 | 10 | ridge | 1993 | 46 | 5 | 0.0365954 | 0.0332297 |
| 5 | 100 | rf | 1994 | 46 | 5 | 0.181401 | 0.0307596 |
| 5 | 100 | ridge | 1994 | 46 | 5 | 0.14073 | 0.0408405 |
| 5 | 500 | rf | 1994 | 46 | 5 | 0.328304 | 0.0333021 |
| 5 | 500 | ridge | 1994 | 46 | 5 | 0.238302 | 0.045093 |
| 5 | 2000 | rf | 1994 | 46 | 5 | 0.4127 | 0.0183956 |
| 5 | 2000 | ridge | 1994 | 46 | 5 | 0.284764 | 0.0140703 |
| 5 | 3000 | rf | 1994 | 46 | 5 | 0.390322 | 0.0191715 |
| 5 | 3000 | ridge | 1994 | 46 | 5 | 0.279095 | 0.0140661 |
| 6 | 10 | rf | 1991 | 46 | 5 | 0.0539241 | 0.0349142 |
| 6 | 10 | ridge | 1991 | 46 | 5 | 0.0418471 | 0.0437826 |
| 6 | 100 | rf | 1994 | 46 | 5 | 0.209837 | 0.036603 |
| 6 | 100 | ridge | 1994 | 46 | 5 | 0.151229 | 0.041518 |
| 6 | 500 | rf | 1994 | 46 | 5 | 0.322181 | 0.035642 |
| 6 | 500 | ridge | 1994 | 46 | 5 | 0.23816 | 0.0512767 |
| 6 | 2000 | rf | 1994 | 46 | 5 | 0.451045 | 0.0303246 |
| 6 | 2000 | ridge | 1994 | 46 | 5 | 0.264128 | 0.0200187 |
| 6 | 3000 | rf | 1994 | 46 | 5 | 0.484614 | 0.0165507 |
| 6 | 3000 | ridge | 1994 | 46 | 5 | 0.283473 | 0.0336609 |
| 14 | 10 | rf | 1993 | 46 | 5 | 0.0652527 | 0.0149313 |
| 14 | 10 | ridge | 1993 | 46 | 5 | 0.0532728 | 0.0167146 |
| 14 | 100 | rf | 1994 | 46 | 5 | 0.29387 | 0.0380797 |
| 14 | 100 | ridge | 1994 | 46 | 5 | 0.256814 | 0.0346244 |
| 14 | 500 | rf | 1994 | 46 | 5 | 0.407286 | 0.0319214 |
| 14 | 500 | ridge | 1994 | 46 | 5 | 0.32464 | 0.0387706 |
| 14 | 2000 | rf | 1994 | 46 | 5 | 0.495643 | 0.0133031 |
| 14 | 2000 | ridge | 1994 | 46 | 5 | 0.402615 | 0.024099 |
| 14 | 3000 | rf | 1994 | 46 | 5 | 0.510134 | 0.0237817 |
| 14 | 3000 | ridge | 1994 | 46 | 5 | 0.388733 | 0.0349245 |
| 15 | 10 | rf | 1992 | 46 | 5 | 0.074857 | 0.0590618 |
| 15 | 10 | ridge | 1992 | 46 | 5 | 0.0848154 | 0.041396 |
| 15 | 100 | rf | 1994 | 46 | 5 | 0.291229 | 0.0349425 |
| 15 | 100 | ridge | 1994 | 46 | 5 | 0.260873 | 0.0292313 |
| 15 | 500 | rf | 1994 | 46 | 5 | 0.388553 | 0.0386905 |
| 15 | 500 | ridge | 1994 | 46 | 5 | 0.310977 | 0.0443777 |
| 15 | 2000 | rf | 1994 | 46 | 5 | 0.482923 | 0.0200065 |
| 15 | 2000 | ridge | 1994 | 46 | 5 | 0.381443 | 0.0303263 |
| 15 | 3000 | rf | 1994 | 46 | 5 | 0.473706 | 0.0229631 |
| 15 | 3000 | ridge | 1994 | 46 | 5 | 0.365343 | 0.0183253 |
| 27 | 10 | rf | 1993 | 46 | 5 | 0.0481223 | 0.0220242 |
| 27 | 10 | ridge | 1993 | 46 | 5 | 0.0573015 | 0.0156053 |
| 27 | 100 | rf | 1994 | 46 | 5 | 0.201689 | 0.0277051 |
| 27 | 100 | ridge | 1994 | 46 | 5 | 0.120911 | 0.0270823 |
| 27 | 500 | rf | 1994 | 46 | 5 | 0.314014 | 0.0369026 |
| 27 | 500 | ridge | 1994 | 46 | 5 | 0.164813 | 0.0323017 |
| 27 | 2000 | rf | 1994 | 46 | 5 | 0.407078 | 0.0323195 |
| 27 | 2000 | ridge | 1994 | 46 | 5 | 0.234038 | 0.0254432 |
| 27 | 3000 | rf | 1994 | 46 | 5 | 0.435334 | 0.0219192 |
| 27 | 3000 | ridge | 1994 | 46 | 5 | 0.261872 | 0.0418585 |
| 28 | 10 | rf | 1993 | 46 | 5 | 0.00211169 | 0.0246713 |
| 28 | 10 | ridge | 1993 | 46 | 5 | -0.0138597 | 0.0336847 |
| 28 | 100 | rf | 1994 | 46 | 5 | 0.137493 | 0.0373027 |
| 28 | 100 | ridge | 1994 | 46 | 5 | 0.0849473 | 0.0354562 |
| 28 | 500 | rf | 1994 | 46 | 5 | 0.180167 | 0.0205141 |
| 28 | 500 | ridge | 1994 | 46 | 5 | 0.117003 | 0.0181145 |
| 28 | 2000 | rf | 1994 | 46 | 5 | 0.359066 | 0.0404194 |
| 28 | 2000 | ridge | 1994 | 46 | 5 | 0.285325 | 0.0492841 |
| 28 | 3000 | rf | 1994 | 46 | 5 | 0.383003 | 0.0409883 |
| 28 | 3000 | ridge | 1994 | 46 | 5 | 0.312317 | 0.0435793 |

#### Qwen2.5-7B · MLE · id run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1994 | 46 | 5 | 0.0207663 | 0.0238148 |
| 1 | 10 | ridge | 1994 | 46 | 5 | 0.0134238 | 0.0143026 |
| 1 | 100 | rf | 1994 | 46 | 5 | 0.070068 | 0.0416092 |
| 1 | 100 | ridge | 1994 | 46 | 5 | 0.0448531 | 0.0287177 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.0306018 | 0.0477472 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.0331601 | 0.0338276 |
| 1 | 2000 | rf | 1994 | 46 | 5 | -0.00187518 | 0.0606474 |
| 1 | 2000 | ridge | 1994 | 46 | 5 | 0.0191469 | 0.0153579 |
| 1 | 3000 | rf | 1994 | 46 | 5 | -0.00507853 | 0.0611439 |
| 1 | 3000 | ridge | 1994 | 46 | 5 | 0.0242937 | 0.0184329 |
| 2 | 10 | rf | 1994 | 46 | 5 | 0.0357874 | 0.0200624 |
| 2 | 10 | ridge | 1994 | 46 | 5 | 0.0283919 | 0.0256214 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.0932756 | 0.0264492 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.0616049 | 0.0231295 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.0506518 | 0.0234174 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.0287939 | 0.0371752 |
| 2 | 2000 | rf | 1994 | 46 | 5 | 0.0584189 | 0.0459326 |
| 2 | 2000 | ridge | 1994 | 46 | 5 | 0.0451331 | 0.0172803 |
| 2 | 3000 | rf | 1994 | 46 | 5 | 0.0681558 | 0.0421046 |
| 2 | 3000 | ridge | 1994 | 46 | 5 | 0.0642616 | 0.0215289 |
| 3 | 10 | rf | 1994 | 46 | 5 | 0.00848443 | 0.0211183 |
| 3 | 10 | ridge | 1994 | 46 | 5 | 0.0104089 | 0.018253 |
| 3 | 100 | rf | 1994 | 46 | 5 | 0.082833 | 0.0341806 |
| 3 | 100 | ridge | 1994 | 46 | 5 | 0.0418239 | 0.0292514 |
| 3 | 500 | rf | 1994 | 46 | 5 | 0.0764248 | 0.0305151 |
| 3 | 500 | ridge | 1994 | 46 | 5 | 0.0300329 | 0.0327397 |
| 3 | 2000 | rf | 1994 | 46 | 5 | 0.0947622 | 0.0622376 |
| 3 | 2000 | ridge | 1994 | 46 | 5 | 0.101166 | 0.049834 |
| 3 | 3000 | rf | 1994 | 46 | 5 | 0.100737 | 0.0788656 |
| 3 | 3000 | ridge | 1994 | 46 | 5 | 0.118158 | 0.0589172 |
| 4 | 10 | rf | 1994 | 46 | 5 | -0.000878106 | 0.0276314 |
| 4 | 10 | ridge | 1994 | 46 | 5 | 0.000313156 | 0.0179149 |
| 4 | 100 | rf | 1994 | 46 | 5 | 0.0571284 | 0.0375521 |
| 4 | 100 | ridge | 1994 | 46 | 5 | 0.0072576 | 0.0265605 |
| 4 | 500 | rf | 1994 | 46 | 5 | 0.0604263 | 0.030432 |
| 4 | 500 | ridge | 1994 | 46 | 5 | 0.0248362 | 0.0316938 |
| 4 | 2000 | rf | 1994 | 46 | 5 | 0.127884 | 0.106539 |
| 4 | 2000 | ridge | 1994 | 46 | 5 | 0.144221 | 0.0790489 |
| 4 | 3000 | rf | 1994 | 46 | 5 | 0.139441 | 0.117066 |
| 4 | 3000 | ridge | 1994 | 46 | 5 | 0.163539 | 0.0890364 |
| 5 | 10 | rf | 1994 | 46 | 5 | -0.00212262 | 0.0400523 |
| 5 | 10 | ridge | 1994 | 46 | 5 | -0.000613839 | 0.0258105 |
| 5 | 100 | rf | 1994 | 46 | 5 | 0.078373 | 0.05086 |
| 5 | 100 | ridge | 1994 | 46 | 5 | 0.0230188 | 0.0247868 |
| 5 | 500 | rf | 1994 | 46 | 5 | 0.112404 | 0.0427656 |
| 5 | 500 | ridge | 1994 | 46 | 5 | 0.0706851 | 0.0295101 |
| 5 | 2000 | rf | 1994 | 46 | 5 | 0.137777 | 0.0869421 |
| 5 | 2000 | ridge | 1994 | 46 | 5 | 0.162232 | 0.0688242 |
| 5 | 3000 | rf | 1994 | 46 | 5 | 0.144078 | 0.0988557 |
| 5 | 3000 | ridge | 1994 | 46 | 5 | 0.178767 | 0.0799516 |
| 6 | 10 | rf | 1994 | 46 | 5 | 0.021625 | 0.0290744 |
| 6 | 10 | ridge | 1994 | 46 | 5 | 0.00610449 | 0.0373477 |
| 6 | 100 | rf | 1994 | 46 | 5 | 0.122091 | 0.0330494 |
| 6 | 100 | ridge | 1994 | 46 | 5 | 0.0439278 | 0.0189429 |
| 6 | 500 | rf | 1994 | 46 | 5 | 0.161718 | 0.0415924 |
| 6 | 500 | ridge | 1994 | 46 | 5 | 0.0842493 | 0.0281955 |
| 6 | 2000 | rf | 1994 | 46 | 5 | 0.175404 | 0.0923849 |
| 6 | 2000 | ridge | 1994 | 46 | 5 | 0.164701 | 0.0686734 |
| 6 | 3000 | rf | 1994 | 46 | 5 | 0.175688 | 0.0972273 |
| 6 | 3000 | ridge | 1994 | 46 | 5 | 0.18514 | 0.0821793 |
| 14 | 10 | rf | 1994 | 46 | 5 | 0.05589 | 0.0360003 |
| 14 | 10 | ridge | 1994 | 46 | 5 | 0.0430046 | 0.0323587 |
| 14 | 100 | rf | 1994 | 46 | 5 | 0.187804 | 0.0315583 |
| 14 | 100 | ridge | 1994 | 46 | 5 | 0.0950794 | 0.0374829 |
| 14 | 500 | rf | 1994 | 46 | 5 | 0.228069 | 0.0274706 |
| 14 | 500 | ridge | 1994 | 46 | 5 | 0.134322 | 0.0371658 |
| 14 | 2000 | rf | 1994 | 46 | 5 | 0.27076 | 0.0316689 |
| 14 | 2000 | ridge | 1994 | 46 | 5 | 0.187856 | 0.0373865 |
| 14 | 3000 | rf | 1994 | 46 | 5 | 0.292249 | 0.0442883 |
| 14 | 3000 | ridge | 1994 | 46 | 5 | 0.211518 | 0.0456716 |
| 15 | 10 | rf | 1994 | 46 | 5 | 0.0704857 | 0.0339263 |
| 15 | 10 | ridge | 1994 | 46 | 5 | 0.0536222 | 0.0220381 |
| 15 | 100 | rf | 1994 | 46 | 5 | 0.165211 | 0.0258401 |
| 15 | 100 | ridge | 1994 | 46 | 5 | 0.0881441 | 0.0391291 |
| 15 | 500 | rf | 1994 | 46 | 5 | 0.221598 | 0.0269007 |
| 15 | 500 | ridge | 1994 | 46 | 5 | 0.127611 | 0.0381212 |
| 15 | 2000 | rf | 1994 | 46 | 5 | 0.258465 | 0.0386334 |
| 15 | 2000 | ridge | 1994 | 46 | 5 | 0.183128 | 0.0442128 |
| 15 | 3000 | rf | 1994 | 46 | 5 | 0.275663 | 0.0519232 |
| 15 | 3000 | ridge | 1994 | 46 | 5 | 0.205492 | 0.0538919 |
| 27 | 10 | rf | 1994 | 46 | 5 | 0.00882643 | 0.0184892 |
| 27 | 10 | ridge | 1994 | 46 | 5 | -0.00283808 | 0.0341034 |
| 27 | 100 | rf | 1994 | 46 | 5 | 0.0859525 | 0.0132193 |
| 27 | 100 | ridge | 1994 | 46 | 5 | 0.0260772 | 0.0324067 |
| 27 | 500 | rf | 1994 | 46 | 5 | 0.133298 | 0.0218043 |
| 27 | 500 | ridge | 1994 | 46 | 5 | 0.0474294 | 0.0260734 |
| 27 | 2000 | rf | 1994 | 46 | 5 | 0.178082 | 0.040899 |
| 27 | 2000 | ridge | 1994 | 46 | 5 | 0.110043 | 0.0459318 |
| 27 | 3000 | rf | 1994 | 46 | 5 | 0.163737 | 0.0540264 |
| 27 | 3000 | ridge | 1994 | 46 | 5 | 0.117702 | 0.0511017 |
| 28 | 10 | rf | 1994 | 46 | 5 | -0.0108509 | 0.0136921 |
| 28 | 10 | ridge | 1994 | 46 | 5 | -0.0084973 | 0.0164062 |
| 28 | 100 | rf | 1994 | 46 | 5 | 0.0481528 | 0.0276549 |
| 28 | 100 | ridge | 1994 | 46 | 5 | -0.0154688 | 0.0286131 |
| 28 | 500 | rf | 1994 | 46 | 5 | 0.127528 | 0.0219517 |
| 28 | 500 | ridge | 1994 | 46 | 5 | 0.0437204 | 0.0439475 |
| 28 | 2000 | rf | 1994 | 46 | 5 | 0.270171 | 0.0483023 |
| 28 | 2000 | ridge | 1994 | 46 | 5 | 0.182695 | 0.0554887 |
| 28 | 3000 | rf | 1994 | 46 | 5 | 0.282346 | 0.0520633 |
| 28 | 3000 | ridge | 1994 | 46 | 5 | 0.189462 | 0.0488112 |

#### Qwen2.5-7B · ESS · id run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | rf | 1994 | 46 | 5 | 0.111673 | 0.0265214 |
| 1 | 10 | ridge | 1994 | 46 | 5 | 0.0647291 | 0.0123474 |
| 1 | 100 | rf | 1994 | 46 | 5 | 0.150241 | 0.0364531 |
| 1 | 100 | ridge | 1994 | 46 | 5 | 0.114305 | 0.0202363 |
| 1 | 500 | rf | 1994 | 46 | 5 | 0.145886 | 0.0336621 |
| 1 | 500 | ridge | 1994 | 46 | 5 | 0.103652 | 0.0200003 |
| 1 | 2000 | rf | 1994 | 46 | 5 | 0.164958 | 0.0389324 |
| 1 | 2000 | ridge | 1994 | 46 | 5 | 0.116069 | 0.0262732 |
| 1 | 3000 | rf | 1994 | 46 | 5 | 0.172648 | 0.0403019 |
| 1 | 3000 | ridge | 1994 | 46 | 5 | 0.129833 | 0.0274634 |
| 2 | 10 | rf | 1994 | 46 | 5 | 0.123876 | 0.0619908 |
| 2 | 10 | ridge | 1994 | 46 | 5 | 0.103393 | 0.0300905 |
| 2 | 100 | rf | 1994 | 46 | 5 | 0.218847 | 0.0294192 |
| 2 | 100 | ridge | 1994 | 46 | 5 | 0.165498 | 0.0222034 |
| 2 | 500 | rf | 1994 | 46 | 5 | 0.209854 | 0.0534914 |
| 2 | 500 | ridge | 1994 | 46 | 5 | 0.165568 | 0.0172222 |
| 2 | 2000 | rf | 1994 | 46 | 5 | 0.322851 | 0.0706786 |
| 2 | 2000 | ridge | 1994 | 46 | 5 | 0.232265 | 0.0391993 |
| 2 | 3000 | rf | 1994 | 46 | 5 | 0.399057 | 0.0735766 |
| 2 | 3000 | ridge | 1994 | 46 | 5 | 0.281812 | 0.0492015 |
| 3 | 10 | rf | 1994 | 46 | 5 | 0.149489 | 0.0606327 |
| 3 | 10 | ridge | 1994 | 46 | 5 | 0.127903 | 0.0355744 |
| 3 | 100 | rf | 1994 | 46 | 5 | 0.183544 | 0.0485451 |
| 3 | 100 | ridge | 1994 | 46 | 5 | 0.132527 | 0.0229481 |
| 3 | 500 | rf | 1994 | 46 | 5 | 0.178357 | 0.0429194 |
| 3 | 500 | ridge | 1994 | 46 | 5 | 0.116299 | 0.0215308 |
| 3 | 2000 | rf | 1994 | 46 | 5 | 0.35053 | 0.0169997 |
| 3 | 2000 | ridge | 1994 | 46 | 5 | 0.218002 | 0.0218518 |
| 3 | 3000 | rf | 1994 | 46 | 5 | 0.476318 | 0.0274182 |
| 3 | 3000 | ridge | 1994 | 46 | 5 | 0.302373 | 0.0179882 |
| 4 | 10 | rf | 1994 | 46 | 5 | 0.141617 | 0.0432932 |
| 4 | 10 | ridge | 1994 | 46 | 5 | 0.126619 | 0.0237233 |
| 4 | 100 | rf | 1994 | 46 | 5 | 0.15094 | 0.0556667 |
| 4 | 100 | ridge | 1994 | 46 | 5 | 0.129685 | 0.027228 |
| 4 | 500 | rf | 1994 | 46 | 5 | 0.162088 | 0.0495682 |
| 4 | 500 | ridge | 1994 | 46 | 5 | 0.122126 | 0.0286667 |
| 4 | 2000 | rf | 1994 | 46 | 5 | 0.399923 | 0.0286567 |
| 4 | 2000 | ridge | 1994 | 46 | 5 | 0.218543 | 0.018299 |
| 4 | 3000 | rf | 1994 | 46 | 5 | 0.447817 | 0.0269098 |
| 4 | 3000 | ridge | 1994 | 46 | 5 | 0.270915 | 0.0192467 |
| 5 | 10 | rf | 1994 | 46 | 5 | 0.131091 | 0.0152012 |
| 5 | 10 | ridge | 1994 | 46 | 5 | 0.103725 | 0.015365 |
| 5 | 100 | rf | 1994 | 46 | 5 | 0.210822 | 0.0310224 |
| 5 | 100 | ridge | 1994 | 46 | 5 | 0.169917 | 0.0364109 |
| 5 | 500 | rf | 1994 | 46 | 5 | 0.336075 | 0.0306072 |
| 5 | 500 | ridge | 1994 | 46 | 5 | 0.253563 | 0.0371901 |
| 5 | 2000 | rf | 1994 | 46 | 5 | 0.466321 | 0.0198599 |
| 5 | 2000 | ridge | 1994 | 46 | 5 | 0.307389 | 0.0272848 |
| 5 | 3000 | rf | 1994 | 46 | 5 | 0.474509 | 0.014855 |
| 5 | 3000 | ridge | 1994 | 46 | 5 | 0.324691 | 0.0256137 |
| 6 | 10 | rf | 1994 | 46 | 5 | 0.156428 | 0.0245952 |
| 6 | 10 | ridge | 1994 | 46 | 5 | 0.125405 | 0.0336485 |
| 6 | 100 | rf | 1994 | 46 | 5 | 0.240032 | 0.0391515 |
| 6 | 100 | ridge | 1994 | 46 | 5 | 0.183939 | 0.04028 |
| 6 | 500 | rf | 1994 | 46 | 5 | 0.357824 | 0.0424374 |
| 6 | 500 | ridge | 1994 | 46 | 5 | 0.271605 | 0.0502651 |
| 6 | 2000 | rf | 1994 | 46 | 5 | 0.506546 | 0.012617 |
| 6 | 2000 | ridge | 1994 | 46 | 5 | 0.322663 | 0.0271393 |
| 6 | 3000 | rf | 1994 | 46 | 5 | 0.552895 | 0.0189881 |
| 6 | 3000 | ridge | 1994 | 46 | 5 | 0.365965 | 0.0283777 |
| 14 | 10 | rf | 1994 | 46 | 5 | 0.172655 | 0.0408076 |
| 14 | 10 | ridge | 1994 | 46 | 5 | 0.137286 | 0.0285368 |
| 14 | 100 | rf | 1994 | 46 | 5 | 0.324537 | 0.0388981 |
| 14 | 100 | ridge | 1994 | 46 | 5 | 0.274828 | 0.0410563 |
| 14 | 500 | rf | 1994 | 46 | 5 | 0.451361 | 0.0325897 |
| 14 | 500 | ridge | 1994 | 46 | 5 | 0.363425 | 0.0284296 |
| 14 | 2000 | rf | 1994 | 46 | 5 | 0.582263 | 0.0117649 |
| 14 | 2000 | ridge | 1994 | 46 | 5 | 0.469226 | 0.0156918 |
| 14 | 3000 | rf | 1994 | 46 | 5 | 0.609049 | 0.012192 |
| 14 | 3000 | ridge | 1994 | 46 | 5 | 0.488719 | 0.0227364 |
| 15 | 10 | rf | 1994 | 46 | 5 | 0.177668 | 0.0300886 |
| 15 | 10 | ridge | 1994 | 46 | 5 | 0.152755 | 0.0294479 |
| 15 | 100 | rf | 1994 | 46 | 5 | 0.322236 | 0.0358357 |
| 15 | 100 | ridge | 1994 | 46 | 5 | 0.27787 | 0.035826 |
| 15 | 500 | rf | 1994 | 46 | 5 | 0.426215 | 0.0357786 |
| 15 | 500 | ridge | 1994 | 46 | 5 | 0.353722 | 0.0286449 |
| 15 | 2000 | rf | 1994 | 46 | 5 | 0.572921 | 0.0215011 |
| 15 | 2000 | ridge | 1994 | 46 | 5 | 0.460686 | 0.0236631 |
| 15 | 3000 | rf | 1994 | 46 | 5 | 0.611731 | 0.0170644 |
| 15 | 3000 | ridge | 1994 | 46 | 5 | 0.482662 | 0.0221659 |
| 27 | 10 | rf | 1994 | 46 | 5 | 0.135551 | 0.014111 |
| 27 | 10 | ridge | 1994 | 46 | 5 | 0.0936922 | 0.0135282 |
| 27 | 100 | rf | 1994 | 46 | 5 | 0.248826 | 0.0269929 |
| 27 | 100 | ridge | 1994 | 46 | 5 | 0.173943 | 0.0309821 |
| 27 | 500 | rf | 1994 | 46 | 5 | 0.395755 | 0.0285518 |
| 27 | 500 | ridge | 1994 | 46 | 5 | 0.225321 | 0.0312649 |
| 27 | 2000 | rf | 1994 | 46 | 5 | 0.470323 | 0.0305478 |
| 27 | 2000 | ridge | 1994 | 46 | 5 | 0.267787 | 0.0236218 |
| 27 | 3000 | rf | 1994 | 46 | 5 | 0.522867 | 0.0128932 |
| 27 | 3000 | ridge | 1994 | 46 | 5 | 0.305751 | 0.0245631 |
| 28 | 10 | rf | 1994 | 46 | 5 | 0.0727174 | 0.0333115 |
| 28 | 10 | ridge | 1994 | 46 | 5 | 0.0438307 | 0.0462534 |
| 28 | 100 | rf | 1994 | 46 | 5 | 0.1599 | 0.0339626 |
| 28 | 100 | ridge | 1994 | 46 | 5 | 0.103282 | 0.0321061 |
| 28 | 500 | rf | 1994 | 46 | 5 | 0.199556 | 0.0339121 |
| 28 | 500 | ridge | 1994 | 46 | 5 | 0.126267 | 0.0216526 |
| 28 | 2000 | rf | 1994 | 46 | 5 | 0.378088 | 0.0306946 |
| 28 | 2000 | ridge | 1994 | 46 | 5 | 0.296414 | 0.0395312 |
| 28 | 3000 | rf | 1994 | 46 | 5 | 0.409684 | 0.0279773 |
| 28 | 3000 | ridge | 1994 | 46 | 5 | 0.330589 | 0.0443756 |

#### Apertus-8B · FCI · fci_pyfci run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | rf | 1994 | 46 | 5 | 0.402484 | 0.0124642 |
| 2 | 1000 | ridge | 1994 | 46 | 5 | 0.328872 | 0.0294118 |

#### Apertus-8B · MLE · id run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | rf | 1994 | 46 | 5 | 0.130949 | 0.0619074 |
| 2 | 1000 | ridge | 1994 | 46 | 5 | 0.117288 | 0.0197883 |
| 16 | 1000 | rf | 1994 | 46 | 5 | 0.271528 | 0.0340207 |
| 16 | 1000 | ridge | 1994 | 46 | 5 | 0.193664 | 0.0298706 |
| 31 | 1000 | rf | 1994 | 46 | 5 | 0.137916 | 0.0395539 |
| 31 | 1000 | ridge | 1994 | 46 | 5 | 0.0760792 | 0.0173909 |

#### Apertus-8B · ESS · id run

| Layer | K | Predictor | N | Features | Folds | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1000 | rf | 1994 | 46 | 5 | 0.33173 | 0.0860943 |
| 2 | 1000 | ridge | 1994 | 46 | 5 | 0.259548 | 0.0598919 |
| 16 | 1000 | rf | 1994 | 46 | 5 | 0.441467 | 0.00741582 |
| 16 | 1000 | ridge | 1994 | 46 | 5 | 0.359697 | 0.0199667 |
| 31 | 1000 | rf | 1994 | 46 | 5 | 0.342569 | 0.0418149 |
| 31 | 1000 | ridge | 1994 | 46 | 5 | 0.198913 | 0.026989 |

### Ridge prediction of MLE and ESS from log-perplexity alone

Pythia-1.4B Ridge baselines using log-perplexity as the sole predictor. All 100 archived results are displayed. Three-fold and five-fold runs remain separate. Pooled rows repeat queries across layers and are not a held-out-query evaluation across layers.

[Download the CSV](tables/perplexity_only_ridge.csv)

#### all_layers_3fold · pooled evaluation splits and layers

| Layer | Estimator | N | Folds | R² mean | R² SD | RMSE mean | Spearman rho mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | ess | 96000 | 3 | 0.0572901 | 0.00277539 | 20.9289 | 0.267773 |
| — | mle | 96000 | 3 | 0.0216415 | 0.00152119 | 9.04383 | 0.245198 |

#### all_layers_3fold · eval_known

| Layer | Estimator | N | Folds | R² mean | R² SD | RMSE mean | Spearman rho mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| layer_1 | ess | 2000 | 3 | -0.00227584 | 0.0023149 | 14.5031 | -0.0307135 |
| layer_1 | mle | 2000 | 3 | 0.0306389 | 0.00577342 | 5.95074 | 0.240669 |
| layer_2 | ess | 2000 | 3 | 0.00556455 | 0.00415064 | 11.5719 | 0.139545 |
| layer_2 | mle | 2000 | 3 | 0.0252605 | 0.00306792 | 5.05779 | 0.197472 |
| layer_3 | ess | 2000 | 3 | -1.24552e-05 | 0.00225318 | 10.6673 | 0.11049 |
| layer_3 | mle | 2000 | 3 | 0.0259803 | 0.00569828 | 5.4035 | 0.233237 |
| layer_4 | ess | 2000 | 3 | 0.0575154 | 0.0180863 | 10.9009 | 0.311965 |
| layer_4 | mle | 2000 | 3 | 0.0244442 | 0.000569254 | 9.80967 | 0.300796 |
| layer_5 | ess | 2000 | 3 | 0.132938 | 0.0252042 | 12.2793 | 0.404565 |
| layer_5 | mle | 2000 | 3 | 0.02037 | 0.00292286 | 12.1614 | 0.323385 |
| layer_6 | ess | 2000 | 3 | 0.173979 | 0.0320268 | 15.3849 | 0.450863 |
| layer_6 | mle | 2000 | 3 | 0.0286862 | 0.00479547 | 12.0196 | 0.357599 |
| layer_7 | ess | 2000 | 3 | 0.148301 | 0.0286514 | 21.0341 | 0.404832 |
| layer_7 | mle | 2000 | 3 | 0.0246493 | 0.00525689 | 13.0877 | 0.332544 |
| layer_8 | ess | 2000 | 3 | 0.129981 | 0.0240005 | 23.6421 | 0.376383 |
| layer_8 | mle | 2000 | 3 | 0.027819 | 0.00416185 | 12.316 | 0.318547 |
| layer_9 | ess | 2000 | 3 | 0.120983 | 0.022526 | 24.373 | 0.365678 |
| layer_9 | mle | 2000 | 3 | 0.0241886 | 0.00514073 | 13.1019 | 0.305481 |
| layer_10 | ess | 2000 | 3 | 0.131095 | 0.0180898 | 24.4148 | 0.379801 |
| layer_10 | mle | 2000 | 3 | 0.0285322 | 0.00521016 | 12.6093 | 0.302431 |
| layer_11 | ess | 2000 | 3 | 0.129375 | 0.0224932 | 21.4552 | 0.382502 |
| layer_11 | mle | 2000 | 3 | 0.0297089 | 0.00617081 | 12.2827 | 0.30832 |
| layer_12 | ess | 2000 | 3 | 0.151386 | 0.0216258 | 20.6425 | 0.413543 |
| layer_12 | mle | 2000 | 3 | 0.034683 | 0.00585843 | 11.5458 | 0.320498 |
| layer_13 | ess | 2000 | 3 | 0.159349 | 0.0222371 | 18.878 | 0.42673 |
| layer_13 | mle | 2000 | 3 | 0.0446032 | 0.0100454 | 9.94747 | 0.323009 |
| layer_14 | ess | 2000 | 3 | 0.187342 | 0.0256647 | 15.9329 | 0.459076 |
| layer_14 | mle | 2000 | 3 | 0.0546947 | 0.00833479 | 7.95405 | 0.312778 |
| layer_15 | ess | 2000 | 3 | 0.168069 | 0.0300101 | 14.2285 | 0.441175 |
| layer_15 | mle | 2000 | 3 | 0.0641501 | 0.00932584 | 6.72665 | 0.312182 |
| layer_16 | ess | 2000 | 3 | 0.126382 | 0.032348 | 14.1413 | 0.380106 |
| layer_16 | mle | 2000 | 3 | 0.0622554 | 0.0121139 | 6.03405 | 0.291712 |
| layer_17 | ess | 2000 | 3 | 0.0973442 | 0.0323124 | 14.2188 | 0.338573 |
| layer_17 | mle | 2000 | 3 | 0.0692426 | 0.0148128 | 5.9458 | 0.298275 |
| layer_18 | ess | 2000 | 3 | 0.0750844 | 0.0328538 | 14.3409 | 0.30164 |
| layer_18 | mle | 2000 | 3 | 0.0564857 | 0.0132306 | 5.83109 | 0.271737 |
| layer_19 | ess | 2000 | 3 | 0.0853053 | 0.0305108 | 15.0619 | 0.314162 |
| layer_19 | mle | 2000 | 3 | 0.0607728 | 0.0160319 | 5.8015 | 0.275461 |
| layer_20 | ess | 2000 | 3 | 0.0897986 | 0.0303888 | 15.1389 | 0.320319 |
| layer_20 | mle | 2000 | 3 | 0.0615081 | 0.0155163 | 5.76866 | 0.274419 |
| layer_21 | ess | 2000 | 3 | 0.0974445 | 0.0340846 | 15.4238 | 0.332828 |
| layer_21 | mle | 2000 | 3 | 0.0614466 | 0.0165079 | 5.76828 | 0.273698 |
| layer_22 | ess | 2000 | 3 | 0.0944966 | 0.0308438 | 15.402 | 0.326547 |
| layer_22 | mle | 2000 | 3 | 0.0617925 | 0.0171153 | 5.74832 | 0.274297 |
| layer_23 | ess | 2000 | 3 | 0.0911845 | 0.0330149 | 15.6456 | 0.326731 |
| layer_23 | mle | 2000 | 3 | 0.0606063 | 0.0159253 | 5.81241 | 0.273302 |
| layer_24 | ess | 2000 | 3 | 0.0329203 | 0.0262671 | 13.7063 | 0.217188 |
| layer_24 | mle | 2000 | 3 | 0.00194829 | 0.010352 | 8.45895 | -0.0512639 |

#### all_layers_3fold · eval_unknown

| Layer | Estimator | N | Folds | R² mean | R² SD | RMSE mean | Spearman rho mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| layer_1 | ess | 2000 | 3 | -0.0019574 | 0.00321667 | 13.4882 | 0.00415224 |
| layer_1 | mle | 2000 | 3 | 0.000111971 | 0.00228912 | 5.50476 | 0.0863921 |
| layer_2 | ess | 2000 | 3 | 0.00059228 | 0.00316695 | 11.0733 | -0.00851125 |
| layer_2 | mle | 2000 | 3 | -0.00102747 | 0.00327314 | 4.45999 | 0.0386731 |
| layer_3 | ess | 2000 | 3 | -0.000412502 | 0.00228084 | 9.99276 | -0.0125979 |
| layer_3 | mle | 2000 | 3 | -0.00312311 | 0.0078977 | 4.71781 | 0.0406596 |
| layer_4 | ess | 2000 | 3 | 0.00245639 | 0.0031372 | 10.2812 | 0.123503 |
| layer_4 | mle | 2000 | 3 | 0.00403893 | 0.00986458 | 9.27017 | 0.104367 |
| layer_5 | ess | 2000 | 3 | 0.0204134 | 0.00715433 | 10.5476 | 0.2156 |
| layer_5 | mle | 2000 | 3 | 0.00172813 | 0.00410498 | 11.1259 | 0.112632 |
| layer_6 | ess | 2000 | 3 | 0.0248472 | 0.00637951 | 12.3198 | 0.222194 |
| layer_6 | mle | 2000 | 3 | 0.001318 | 0.00468101 | 10.2384 | 0.128522 |
| layer_7 | ess | 2000 | 3 | 0.0246597 | 0.00537934 | 15.7137 | 0.209738 |
| layer_7 | mle | 2000 | 3 | -0.000781216 | 0.00335583 | 10.7322 | 0.0980557 |
| layer_8 | ess | 2000 | 3 | 0.0256011 | 0.00472297 | 18.3025 | 0.211341 |
| layer_8 | mle | 2000 | 3 | -0.00403571 | 0.00144115 | 10.085 | 0.00205204 |
| layer_9 | ess | 2000 | 3 | 0.0214777 | 0.00352932 | 18.4655 | 0.193354 |
| layer_9 | mle | 2000 | 3 | -0.00279081 | 0.000663226 | 10.6148 | 0.00265385 |
| layer_10 | ess | 2000 | 3 | 0.0283919 | 0.0011135 | 18.8052 | 0.218472 |
| layer_10 | mle | 2000 | 3 | -0.00401358 | 0.00124219 | 10.1896 | 0.00307589 |
| layer_11 | ess | 2000 | 3 | 0.0343132 | 0.00446813 | 16.8648 | 0.234779 |
| layer_11 | mle | 2000 | 3 | -0.00119325 | 0.000350922 | 10.3847 | 0.0146813 |
| layer_12 | ess | 2000 | 3 | 0.0414483 | 0.000801254 | 16.7546 | 0.248068 |
| layer_12 | mle | 2000 | 3 | -0.000237437 | 0.00117158 | 9.88605 | 0.105399 |
| layer_13 | ess | 2000 | 3 | 0.0425886 | 0.00567231 | 14.4981 | 0.241573 |
| layer_13 | mle | 2000 | 3 | 1.72478e-06 | 0.000626219 | 8.11182 | 0.101552 |
| layer_14 | ess | 2000 | 3 | 0.0686254 | 0.00974062 | 13.152 | 0.2564 |
| layer_14 | mle | 2000 | 3 | 0.000364004 | 0.000760781 | 6.45636 | 0.0917941 |
| layer_15 | ess | 2000 | 3 | 0.0599683 | 0.0184393 | 12.0376 | 0.218548 |
| layer_15 | mle | 2000 | 3 | 0.0093871 | 0.0061122 | 5.60676 | 0.123885 |
| layer_16 | ess | 2000 | 3 | 0.0414485 | 0.0134228 | 12.0454 | 0.205067 |
| layer_16 | mle | 2000 | 3 | 0.0122496 | 0.00532631 | 5.16806 | 0.126729 |
| layer_17 | ess | 2000 | 3 | 0.0278047 | 0.0113196 | 12.7041 | 0.182986 |
| layer_17 | mle | 2000 | 3 | 0.0186888 | 0.0114089 | 5.27438 | 0.131125 |
| layer_18 | ess | 2000 | 3 | 0.0252869 | 0.0115402 | 12.9503 | 0.178018 |
| layer_18 | mle | 2000 | 3 | 0.0214094 | 0.0152039 | 5.10042 | 0.124765 |
| layer_19 | ess | 2000 | 3 | 0.0370729 | 0.0136768 | 14.7106 | 0.203191 |
| layer_19 | mle | 2000 | 3 | 0.0260883 | 0.021631 | 5.13669 | 0.122032 |
| layer_20 | ess | 2000 | 3 | 0.0468547 | 0.01492 | 15.1823 | 0.209431 |
| layer_20 | mle | 2000 | 3 | 0.0322667 | 0.0251981 | 5.06711 | 0.12456 |
| layer_21 | ess | 2000 | 3 | 0.052977 | 0.0162435 | 15.7118 | 0.217745 |
| layer_21 | mle | 2000 | 3 | 0.0359329 | 0.0290155 | 5.08621 | 0.1319 |
| layer_22 | ess | 2000 | 3 | 0.0482165 | 0.0153705 | 15.8718 | 0.209474 |
| layer_22 | mle | 2000 | 3 | 0.0399985 | 0.0316053 | 5.06233 | 0.134904 |
| layer_23 | ess | 2000 | 3 | 0.0509852 | 0.0156414 | 16.004 | 0.210772 |
| layer_23 | mle | 2000 | 3 | 0.0413294 | 0.0314985 | 5.11337 | 0.134861 |
| layer_24 | ess | 2000 | 3 | 0.00201477 | 0.01073 | 11.7281 | 0.0582563 |
| layer_24 | mle | 2000 | 3 | 0.1087 | 0.00857511 | 9.69673 | 0.183416 |

#### eval_known_layer24_5fold · eval_known

| Layer | Estimator | N | Folds | R² mean | R² SD | RMSE mean | Spearman rho mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| layer_24 | ess | 2000 | 5 | 0.0363385 | 0.0274777 | 13.6835 | 0.215428 |
| layer_24 | mle | 2000 | 5 | 0.00393968 | 0.00879065 | 8.45719 | -0.0541544 |
