# Opal-Bench leaderboard

Lower ratios mean lower error. Each ratio compares a method's MSE with MID. The scorer averages log ratios over draws, then cell lines within each lab, then labs, and exponentiates the result. Each lab has equal weight.

Rank intervals are 95% bootstrap intervals from 2,000 replicates with seed 0. Development resamples labs; the test and fresh tracks resample labs, then cell lines. "Units better than MID" counts labs on development and cell lines on test and fresh.

## Where the rows come from

- Unmarked methods are built-in baselines you can re-score with `opal-bench-score fewshot`.
- ¹ marks Opal v1 rows. Re-score them with `--opal-v1 DIR` and the public growth checkpoint.
- ² marks the official Opal v1 API with MID fallback. It abstains on 85–99% of pairs and needs the separate Opal package.
- ³ marks cross-lab learners from the original run. Each had the same tuning budget, grouped four-fold cross-validation over training labs and a few-shot ridge head on [1, lo, hi, lo·hi, f] for FS_* methods. Their per-draw rows are published; their training code isn't included here.

## Method names

ADD = sa + sb. MIN = min(sa, sb). MID = ½(ADD + MIN). FS_LIN5_lam fits a ridge with λ = 0.1 to the k target pairs, using [1, lo, hi, lo+hi, lo·hi, |hi−lo|].

v1F uses frozen Opal v1 weights; v1R refits that architecture to the k calibration pairs; v1O calls the official API. LIN5x, GBM and MLP use singles, STRING and paralog features. EMB_* uses frozen GenePT, Geneformer or scGPT embeddings, while GRAPH uses GEARS-style STRING propagation. NET_ATT is an 844,801-parameter set-attention meta-learner; NET_MLP is a 582,657-parameter residual MLP.

The first tables cover all 22 labs. Shipped-data tables appear separately below. Rebuild the full leaderboard tables from the published error rows with `opal-bench-score table leaderboard/rows.csv.gz`.

## Main track: few-shot held-out lab

### Development: 18 labs, nested leave-one-lab-out, 20 draws

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–3] | 0.609 | 0/18 |
| GBM ³ | 1.086 | 2 [1–6] | 0.255 | 10/18 |
| MIN | 1.135 | 3 [1–5] | 0.127 | 8/18 |
| v1O ² | 1.196 | 4 [2–6] | 0.000 | 2/18 |
| ADD | 1.389 | 5 [2–11] | 0.004 | 3/18 |
| v1F ¹ | 1.495 | 6 [2–12] | 0.005 | 6/18 |
| LIN5x ³ | 1.564 | 7 [4–8] | 0.000 | 6/18 |
| EMB_Geneformer ³ | 1.792 | 8 [7–10] | 0.000 | 4/18 |
| EMB_scGPT ³ | 1.840 | 9 [7–10] | 0.000 | 4/18 |
| EMB_GenePT ³ | 1.935 | 10 [8–12] | 0.000 | 2/18 |
| GRAPH ³ | 1.965 | 11 [9–12] | 0.000 | 2/18 |
| MLP ³ | 2.080 | 12 [6–12] | 0.000 | 2/18 |

#### k = 10

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_ATT ³ | 0.549 | 1 [1–3] | 0.842 | 17/18 |
| NET_MLP ³ | 0.586 | 2 [2–6] | 0.004 | 16/18 |
| v1R ¹ | 0.607 | 3 [1–10] | 0.145 | 15/18 |
| FS_LIN5x ³ | 0.660 | 4 [3–6] | 0.002 | 13/18 |
| FS_LIN5_lam | 0.661 | 5 [2–7] | 0.007 | 12/18 |
| FS_GBM ³ | 0.670 | 6 [3–6] | 0.000 | 13/18 |
| FS_EMB_Geneformer ³ | 0.710 | 7 [6–8] | 0.000 | 12/18 |
| FS_GRAPH ³ | 0.715 | 8 [7–11] | 0.000 | 12/18 |
| FS_EMB_GenePT ³ | 0.722 | 9 [7–11] | 0.000 | 12/18 |
| FS_EMB_scGPT ³ | 0.727 | 10 [7–11] | 0.000 | 12/18 |
| FS_MLP ³ | 0.752 | 11 [7–12] | 0.000 | 13/18 |
| MID | 1.000 | 12 [11–14] | 0.000 | 0/18 |
| MIN | 1.135 | 13 [12–15] | 0.000 | 8/18 |
| v1O ² | 1.196 | 14 [13–15] | 0.000 | 2/18 |
| ADD | 1.388 | 15 [13–16] | 0.000 | 3/18 |
| v1F ¹ | 1.496 | 16 [13–16] | 0.000 | 6/18 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_ATT ³ | 0.472 | 1 [1–4] | 0.804 | 18/18 |
| v1R ¹ | 0.504 | 2 [1–8] | 0.118 | 17/18 |
| NET_MLP ³ | 0.505 | 3 [2–7] | 0.002 | 17/18 |
| FS_LIN5_lam | 0.507 | 4 [1–6] | 0.075 | 16/18 |
| FS_LIN5x ³ | 0.513 | 5 [2–6] | 0.000 | 16/18 |
| FS_GBM ³ | 0.523 | 6 [2–6] | 0.000 | 16/18 |
| FS_EMB_Geneformer ³ | 0.562 | 7 [7–9] | 0.000 | 15/18 |
| FS_GRAPH ³ | 0.564 | 8 [6–9] | 0.000 | 15/18 |
| FS_EMB_scGPT ³ | 0.569 | 9 [7–9] | 0.000 | 15/18 |
| FS_EMB_GenePT ³ | 0.590 | 10 [10–11] | 0.000 | 13/18 |
| FS_MLP ³ | 0.605 | 11 [10–11] | 0.000 | 12/18 |
| MID | 1.000 | 12 [12–13] | 0.000 | 0/18 |
| MIN | 1.135 | 13 [12–15] | 0.000 | 8/18 |
| v1O ² | 1.197 | 14 [13–15] | 0.000 | 2/18 |
| ADD | 1.388 | 15 [13–16] | 0.000 | 3/18 |
| v1F ¹ | 1.496 | 16 [13–16] | 0.000 | 6/18 |

#### k = 50

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_ATT ³ | 0.410 | 1 [1–10] | 0.717 | 18/18 |
| FS_LIN5_lam | 0.427 | 2 [1–5] | 0.168 | 18/18 |
| v1R ¹ | 0.429 | 3 [1–11] | 0.075 | 18/18 |
| FS_GBM ³ | 0.431 | 4 [2–11] | 0.006 | 18/18 |
| FS_MLP ³ | 0.433 | 5 [2–9] | 0.023 | 18/18 |
| FS_LIN5x ³ | 0.433 | 6 [3–8] | 0.002 | 17/18 |
| FS_GRAPH ³ | 0.435 | 7 [2–10] | 0.008 | 17/18 |
| FS_EMB_GenePT ³ | 0.436 | 8 [3–11] | 0.001 | 17/18 |
| NET_MLP ³ | 0.438 | 9 [2–11] | 0.001 | 18/18 |
| FS_EMB_Geneformer ³ | 0.438 | 10 [6–11] | 0.000 | 17/18 |
| FS_EMB_scGPT ³ | 0.438 | 11 [4–11] | 0.000 | 17/18 |
| MID | 1.000 | 12 [12–14] | 0.000 | 0/18 |
| MIN | 1.134 | 13 [12–15] | 0.000 | 8/18 |
| v1O ² | 1.196 | 14 [13–15] | 0.000 | 2/18 |
| ADD | 1.389 | 15 [13–16] | 0.000 | 3/18 |
| v1F ¹ | 1.495 | 16 [13–16] | 0.000 | 6/18 |

### Locked test: 4 labs, 31 cell lines, 20 draws

These labs were never used to choose or tune any few-shot method. They were used in earlier zero-shot pilots, so the test is unused for this task but not pristine.

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–4] | 0.373 | 0/31 |
| GBM ³ | 1.083 | 2 [1–3] | 0.077 | 15/31 |
| MIN | 1.172 | 3 [1–6] | 0.275 | 24/31 |
| ADD | 1.265 | 4 [1–12] | 0.262 | 1/31 |
| v1O ² | 1.473 | 5 [4–9] | 0.000 | 0/31 |
| LIN5x ³ | 1.604 | 6 [4–9] | 0.000 | 11/31 |
| v1F ¹ | 1.658 | 7 [2–12] | 0.013 | 5/31 |
| GRAPH ³ | 1.811 | 8 [5–9] | 0.000 | 11/31 |
| EMB_Geneformer ³ | 1.889 | 9 [6–11] | 0.000 | 8/31 |
| EMB_scGPT ³ | 1.951 | 10 [8–11] | 0.000 | 4/31 |
| EMB_GenePT ³ | 1.993 | 11 [6–12] | 0.000 | 11/31 |
| MLP ³ | 2.121 | 12 [4–12] | 0.000 | 3/31 |

#### k = 10

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| v1R ¹ | 0.493 | 1 [1–3] | 0.677 | 29/31 |
| NET_ATT ³ | 0.515 | 2 [1–3] | 0.236 | 30/31 |
| NET_MLP ³ | 0.517 | 3 [1–3] | 0.082 | 30/31 |
| FS_LIN5x ³ | 0.670 | 4 [4–6] | 0.000 | 22/31 |
| FS_LIN5_lam | 0.674 | 5 [4–9] | 0.000 | 24/31 |
| FS_GBM ³ | 0.720 | 6 [6–10] | 0.000 | 20/31 |
| FS_GRAPH ³ | 0.745 | 7 [6–9] | 0.000 | 18/31 |
| FS_EMB_scGPT ³ | 0.758 | 8 [4–12] | 0.000 | 18/31 |
| FS_EMB_GenePT ³ | 0.767 | 9 [7–11] | 0.000 | 18/31 |
| FS_EMB_Geneformer ³ | 0.769 | 10 [8–12] | 0.000 | 18/31 |
| FS_MLP ³ | 0.836 | 11 [11–13] | 0.000 | 17/31 |
| MID | 1.000 | 12 [6–13] | 0.000 | 0/31 |
| MIN | 1.172 | 13 [12–16] | 0.000 | 24/31 |
| ADD | 1.265 | 14 [2–16] | 0.004 | 1/31 |
| v1O ² | 1.473 | 15 [14–16] | 0.000 | 0/31 |
| v1F ¹ | 1.658 | 16 [10–16] | 0.001 | 5/31 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_MLP ³ | 0.424 | 1 [1–3] | 0.343 | 30/31 |
| NET_ATT ³ | 0.425 | 2 [1–4] | 0.386 | 30/31 |
| v1R ¹ | 0.435 | 3 [1–4] | 0.268 | 30/31 |
| FS_LIN5x ³ | 0.456 | 4 [3–4] | 0.000 | 28/31 |
| FS_LIN5_lam | 0.460 | 5 [4–5] | 0.000 | 28/31 |
| FS_GBM ³ | 0.499 | 6 [6–8] | 0.000 | 28/31 |
| FS_GRAPH ³ | 0.504 | 7 [6–8] | 0.000 | 29/31 |
| FS_EMB_Geneformer ³ | 0.511 | 8 [7–10] | 0.000 | 28/31 |
| FS_EMB_GenePT ³ | 0.513 | 9 [8–10] | 0.000 | 28/31 |
| FS_EMB_scGPT ³ | 0.514 | 10 [8–11] | 0.000 | 28/31 |
| FS_MLP ³ | 0.529 | 11 [10–12] | 0.000 | 28/31 |
| MID | 1.000 | 12 [12–13] | 0.000 | 0/31 |
| MIN | 1.172 | 13 [12–16] | 0.000 | 24/31 |
| ADD | 1.265 | 14 [6–16] | 0.004 | 1/31 |
| v1O ² | 1.473 | 15 [14–16] | 0.000 | 0/31 |
| v1F ¹ | 1.658 | 16 [13–16] | 0.000 | 5/31 |

#### k = 50

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_MLP ³ | 0.381 | 1 [1–3] | 0.370 | 31/31 |
| NET_ATT ³ | 0.381 | 2 [1–4] | 0.360 | 31/31 |
| v1R ¹ | 0.388 | 3 [1–11] | 0.269 | 31/31 |
| FS_LIN5_lam | 0.393 | 4 [3–5] | 0.000 | 31/31 |
| FS_LIN5x ³ | 0.410 | 5 [3–5] | 0.000 | 29/31 |
| FS_GRAPH ³ | 0.416 | 6 [4–11] | 0.000 | 28/31 |
| FS_EMB_scGPT ³ | 0.417 | 7 [6–9] | 0.000 | 28/31 |
| FS_EMB_GenePT ³ | 0.418 | 8 [6–9] | 0.000 | 28/31 |
| FS_EMB_Geneformer ³ | 0.419 | 9 [7–10] | 0.000 | 28/31 |
| FS_GBM ³ | 0.419 | 10 [6–11] | 0.000 | 28/31 |
| FS_MLP ³ | 0.420 | 11 [9–11] | 0.000 | 29/31 |
| MID | 1.000 | 12 [12–13] | 0.000 | 0/31 |
| MIN | 1.172 | 13 [12–16] | 0.000 | 24/31 |
| ADD | 1.265 | 14 [12–16] | 0.001 | 1/31 |
| v1O ² | 1.473 | 15 [14–16] | 0.000 | 0/31 |
| v1F ¹ | 1.658 | 16 [13–16] | 0.000 | 5/31 |

### Fresh screen: SHEN26, 2 cell lines, 50 draws

This 2026 screen was never used during development and is not one of the 22 labs.

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–1] | 1.000 | 0/2 |
| ADD | 1.028 | 2 [2–2] | 0.000 | 0/2 |
| v1O ² | 1.081 | 3 [3–3] | 0.000 | 0/2 |
| MIN | 1.177 | 4 [4–4] | 0.000 | 0/2 |
| v1F ¹ | 1.189 | 5 [5–5] | 0.000 | 0/2 |

#### k = 5

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–2] | 0.745 | 0/2 |
| ADD | 1.028 | 2 [2–3] | 0.000 | 0/2 |
| v1R ¹ | 1.054 | 3 [1–4] | 0.255 | 1/2 |
| v1O ² | 1.081 | 4 [3–4] | 0.000 | 0/2 |
| MIN | 1.177 | 5 [5–6] | 0.000 | 0/2 |
| v1F ¹ | 1.189 | 6 [6–7] | 0.000 | 0/2 |
| FS_LIN5_lam | 1.350 | 7 [5–7] | 0.000 | 0/2 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| v1R ¹ | 0.941 | 1 [1–1] | 1.000 | 2/2 |
| MID | 1.000 | 2 [2–3] | 0.000 | 0/2 |
| ADD | 1.029 | 3 [3–4] | 0.000 | 0/2 |
| FS_LIN5_lam | 1.046 | 4 [2–5] | 0.000 | 1/2 |
| v1O ² | 1.081 | 5 [4–5] | 0.000 | 0/2 |
| MIN | 1.177 | 6 [6–6] | 0.000 | 0/2 |
| v1F ¹ | 1.189 | 7 [7–7] | 0.000 | 0/2 |

## Zero-shot and auxiliary tasks (22 labs)

### Task a: held-out lab (LOLO), zero-shot pair-score MSE
22 labs, 411,098 pairs. Ratios < 1 favour the method. CI = lab bootstrap.

| method | geo-mean MSE | vs MID (best fixed rule): ratio [95% CI] wins | vs MIN: ratio [95% CI] wins |
|---|---|---|---|
| MID | 0.0727 | 1.000 [1.000, 1.000] 0/22 | 0.863 [0.652, 1.132] 12/22 |
| BEST_RULE | 0.0727 | 1.000 [1.000, 1.000] 0/22 | 0.863 [0.652, 1.132] 12/22 |
| MIN | 0.0843 | 1.159 [0.883, 1.533] 10/22 | 1.000 [1.000, 1.000] 0/22 |
| ATLAS | 0.0936 | 1.286 [1.097, 1.572] 5/22 | 1.110 [0.835, 1.474] 12/22 |
| ADD | 0.0990 | 1.361 [1.086, 1.729] 4/22 | 1.174 [0.727, 1.897] 7/22 |
| LIN5 | 0.1175 | 1.616 [1.195, 2.262] 7/22 | 1.394 [1.008, 1.953] 11/22 |

### Task a_fs20: held-out lab, few-shot track (20 calibration pairs per lab; scored on the rest)

| method | geo-mean MSE | vs FS_BEST_RULE: ratio [95% CI] wins | vs MID (best fixed rule): ratio [95% CI] wins |
|---|---|---|---|
| FS_LIN5 | 0.0432 | 0.758 [0.596, 0.953] 15/22 | 0.594 [0.436, 0.801] 18/22 |
| FS_BEST_RULE | 0.0570 | 1.000 [1.000, 1.000] 0/22 | 0.784 [0.665, 0.910] 11/22 |
| MID | 0.0728 | 1.276 [1.099, 1.504] 4/22 | 1.000 [1.000, 1.000] 0/22 |
| BEST_RULE | 0.0728 | 1.276 [1.099, 1.504] 4/22 | 1.000 [1.000, 1.000] 0/22 |
| MIN | 0.0844 | 1.480 [1.140, 2.004] 2/22 | 1.160 [0.884, 1.533] 10/22 |
| ATLAS | 0.0935 | 1.640 [1.339, 2.063] 5/22 | 1.285 [1.093, 1.575] 5/22 |
| ADD | 0.0990 | 1.736 [1.349, 2.361] 1/22 | 1.360 [1.086, 1.727] 4/22 |
| LIN5 | 0.1176 | 2.063 [1.400, 3.138] 5/22 | 1.616 [1.195, 2.262] 7/22 |

### Task b: held-out genes within lab (both genes unseen in-lab), MSE
18 labs with >= 1,000 pairs, 81,885 test pairs.

| method | geo-mean MSE | vs LIN5: ratio [95% CI] wins | vs MID (best fixed rule): ratio [95% CI] wins |
|---|---|---|---|
| LIN5 | 0.0306 | 1.000 [1.000, 1.000] 0/18 | 0.383 [0.286, 0.511] 18/18 |
| BEST_RULE | 0.0585 | 1.914 [1.553, 2.407] 0/18 | 0.733 [0.608, 0.870] 10/18 |
| MID | 0.0798 | 2.611 [1.957, 3.501] 0/18 | 1.000 [1.000, 1.000] 0/18 |
| MIN | 0.0946 | 3.096 [2.277, 4.382] 0/18 | 1.185 [0.867, 1.662] 8/18 |
| ATLAS | 0.1002 | 3.281 [2.401, 4.475] 0/18 | 1.256 [1.091, 1.516] 3/18 |
| ADD | 0.1061 | 3.474 [2.292, 5.578] 0/18 | 1.330 [1.000, 1.786] 4/18 |

### Task c: strong negative interaction (robust z of gA <= -2), per-lab AUROC

| method | median AUROC [95% CI] | wins vs rule | median ΔAUROC vs rule |
|---|---|---|---|
| ATLAS | 0.795 [0.675, 0.852] | 13/22 | +0.000 |
| BEST_RULE | 0.709 [0.583, 0.814] | 10/22 | +0.000 |
| RULE_ADD_MINUS_MIN | 0.708 [0.583, 0.814] | 0/22 | +0.000 |
| LIN5 | 0.621 [0.521, 0.747] | 4/22 | -0.055 |

### Task d: cross-lab reproducibility (descriptive)
93 lab pairs with >= 20 shared pairs. Median between-lab Spearman rho of gA = 0.211 (lab-bootstrap 95% CI 0.128 to 0.280). rho vs log(overlap): -0.052.

| lab | median rho with other labs |
|---|---|
| HARLE25 | 0.509 |
| NAJM18 | 0.327 |
| TANG22 | 0.280 |
| DEDE20 | 0.279 |
| IN4MER24 | 0.274 |
| THOMPSON21 | 0.264 |
| BURGOLD25 | 0.263 |
| KLINGBEIL24 | 0.239 |
| DU17 | 0.235 |
| PARRISH21 | 0.226 |
| SPIDR25 | 0.215 |
| CHYMERA20 | 0.196 |
| ITO21 | 0.174 |
| HORLBECK18 | 0.162 |
| WONG16 | 0.138 |
| SCHEMATIC25 | 0.119 |
| ABBVIE25 | 0.110 |
| HAN17 | 0.077 |
| SHEN17 | 0.077 |
| ZHAO18 | 0.058 |
| SLC25 | -0.017 |
| DIEHL21 | -0.240 |

## Shipped data only: 17 labs, reproduced by `pytest`

These are the numbers anyone can regenerate from this repo alone. dev here is the 16 shipped dev labs, and test is BURGOLD25, the only shipped test lab.

### dev: 16 labs, 16 units

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–2] | 0.850 | 0/16 |
| MIN | 1.199 | 2 [1–3] | 0.139 | 7/16 |
| ADD | 1.357 | 3 [2–3] | 0.011 | 3/16 |

#### k = 10

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| FS_LIN5_lam | 0.660 | 1 [1–1] | 0.993 | 10/16 |
| MID | 1.000 | 2 [2–3] | 0.005 | 0/16 |
| MIN | 1.200 | 3 [2–4] | 0.000 | 7/16 |
| ADD | 1.357 | 4 [3–4] | 0.003 | 3/16 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| FS_LIN5_lam | 0.492 | 1 [1–1] | 1.000 | 14/16 |
| MID | 1.000 | 2 [2–3] | 0.000 | 0/16 |
| MIN | 1.199 | 3 [2–4] | 0.000 | 7/16 |
| ADD | 1.357 | 4 [3–4] | 0.000 | 3/16 |

#### k = 50

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| FS_LIN5_lam | 0.416 | 1 [1–1] | 1.000 | 16/16 |
| MID | 1.000 | 2 [2–3] | 0.000 | 0/16 |
| MIN | 1.198 | 3 [2–4] | 0.000 | 7/16 |
| ADD | 1.357 | 4 [3–4] | 0.000 | 3/16 |

### test: 1 labs, 1 units

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MIN | 0.633 | 1 [1–1] | 1.000 | 1/1 |
| MID | 1.000 | 2 [2–2] | 0.000 | 0/1 |
| ADD | 1.745 | 3 [3–3] | 0.000 | 0/1 |

#### k = 10

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| FS_LIN5_lam | 0.278 | 1 [1–1] | 1.000 | 1/1 |
| MIN | 0.633 | 2 [2–2] | 0.000 | 1/1 |
| MID | 1.000 | 3 [3–3] | 0.000 | 0/1 |
| ADD | 1.745 | 4 [4–4] | 0.000 | 0/1 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| FS_LIN5_lam | 0.142 | 1 [1–1] | 1.000 | 1/1 |
| MIN | 0.633 | 2 [2–2] | 0.000 | 1/1 |
| MID | 1.000 | 3 [3–3] | 0.000 | 0/1 |
| ADD | 1.745 | 4 [4–4] | 0.000 | 0/1 |

#### k = 50

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| FS_LIN5_lam | 0.122 | 1 [1–1] | 1.000 | 1/1 |
| MIN | 0.633 | 2 [2–2] | 0.000 | 1/1 |
| MID | 1.000 | 3 [3–3] | 0.000 | 0/1 |
| ADD | 1.745 | 4 [4–4] | 0.000 | 0/1 |

### fresh: 1 labs, 2 units

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–1] | 1.000 | 0/2 |
| ADD | 1.028 | 2 [2–2] | 0.000 | 0/2 |
| MIN | 1.177 | 3 [3–3] | 0.000 | 0/2 |

#### k = 5

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–1] | 1.000 | 0/2 |
| ADD | 1.028 | 2 [2–2] | 0.000 | 0/2 |
| MIN | 1.177 | 3 [3–4] | 0.000 | 0/2 |
| FS_LIN5_lam | 1.350 | 4 [3–4] | 0.000 | 0/2 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–2] | 0.773 | 0/2 |
| ADD | 1.029 | 2 [2–3] | 0.000 | 0/2 |
| FS_LIN5_lam | 1.046 | 3 [1–3] | 0.227 | 1/2 |
| MIN | 1.177 | 4 [4–4] | 0.000 | 0/2 |

### Tasks a–d on the 17 shipped labs

#### Task a: held-out lab (LOLO), zero-shot pair-score MSE
17 labs, 334,669 pairs. Ratios < 1 favour the method. CI = lab bootstrap.

| method | geo-mean MSE | vs MID (best fixed rule): ratio [95% CI] wins | vs MIN: ratio [95% CI] wins |
|---|---|---|---|
| MID | 0.0832 | 1.000 [1.000, 1.000] 0/17 | 0.866 [0.631, 1.178] 9/17 |
| BEST_RULE | 0.0832 | 1.000 [1.000, 1.000] 0/17 | 0.866 [0.631, 1.178] 9/17 |
| ATLAS | 0.0937 | 1.126 [0.891, 1.490] 9/17 | 0.975 [0.675, 1.429] 9/17 |
| MIN | 0.0961 | 1.155 [0.849, 1.584] 8/17 | 1.000 [1.000, 1.000] 0/17 |
| ADD | 0.1145 | 1.377 [1.087, 1.758] 3/17 | 1.192 [0.713, 2.040] 5/17 |
| LIN5 | 0.1527 | 1.836 [1.242, 2.892] 7/17 | 1.589 [1.076, 2.434] 8/17 |

#### Task a_fs20: held-out lab, few-shot track (20 calibration pairs per lab; scored on the rest)

| method | geo-mean MSE | vs FS_BEST_RULE: ratio [95% CI] wins | vs MID (best fixed rule): ratio [95% CI] wins |
|---|---|---|---|
| FS_LIN5 | 0.0475 | 0.704 [0.531, 0.933] 13/17 | 0.571 [0.390, 0.839] 14/17 |
| FS_BEST_RULE | 0.0675 | 1.000 [1.000, 1.000] 0/17 | 0.811 [0.682, 0.953] 8/17 |
| MID | 0.0832 | 1.234 [1.050, 1.465] 4/17 | 1.000 [1.000, 1.000] 0/17 |
| BEST_RULE | 0.0832 | 1.234 [1.050, 1.465] 4/17 | 1.000 [1.000, 1.000] 0/17 |
| ATLAS | 0.0939 | 1.392 [1.046, 1.885] 8/17 | 1.128 [0.891, 1.497] 9/17 |
| MIN | 0.0962 | 1.426 [1.076, 1.970] 2/17 | 1.156 [0.848, 1.585] 8/17 |
| ADD | 0.1145 | 1.697 [1.261, 2.392] 1/17 | 1.376 [1.086, 1.757] 3/17 |
| LIN5 | 0.1528 | 2.265 [1.411, 3.874] 4/17 | 1.836 [1.242, 2.893] 6/17 |

#### Task b: held-out genes within lab (both genes unseen in-lab), MSE
13 labs with >= 1,000 pairs, 66,676 test pairs.

| method | geo-mean MSE | vs LIN5: ratio [95% CI] wins | vs MID (best fixed rule): ratio [95% CI] wins |
|---|---|---|---|
| LIN5 | 0.0363 | 1.000 [1.000, 1.000] 0/13 | 0.366 [0.244, 0.521] 13/13 |
| BEST_RULE | 0.0738 | 2.032 [1.594, 2.683] 0/13 | 0.743 [0.596, 0.904] 7/13 |
| MID | 0.0993 | 2.736 [1.920, 4.093] 0/13 | 1.000 [1.000, 1.000] 0/13 |
| ATLAS | 0.1094 | 3.012 [2.064, 4.435] 1/13 | 1.101 [0.927, 1.409] 6/13 |
| MIN | 0.1181 | 3.254 [2.227, 5.093] 0/13 | 1.189 [0.796, 1.789] 6/13 |
| ADD | 0.1329 | 3.661 [2.153, 6.693] 0/13 | 1.338 [0.962, 1.884] 3/13 |

#### Task c: strong negative interaction (robust z of gA <= -2), per-lab AUROC

| method | median AUROC [95% CI] | wins vs rule | median ΔAUROC vs rule |
|---|---|---|---|
| ATLAS | 0.808 [0.746, 0.884] | 12/17 | +0.004 |
| BEST_RULE | 0.723 [0.573, 0.823] | 9/17 | +0.000 |
| RULE_ADD_MINUS_MIN | 0.722 [0.573, 0.823] | 0/17 | +0.000 |
| LIN5 | 0.665 [0.530, 0.799] | 4/17 | -0.043 |

#### Task d: cross-lab reproducibility (descriptive)
46 lab pairs with >= 20 shared pairs. Median between-lab Spearman rho of gA = 0.261 (lab-bootstrap 95% CI 0.198 to 0.350). rho vs log(overlap): +0.025.

| lab | median rho with other labs |
|---|---|
| HARLE25 | 0.509 |
| NAJM18 | 0.421 |
| DEDE20 | 0.322 |
| BURGOLD25 | 0.313 |
| PARRISH21 | 0.293 |
| IN4MER24 | 0.280 |
| THOMPSON21 | 0.267 |
| TANG22 | 0.263 |
| SHEN17 | 0.258 |
| SPIDR25 | 0.221 |
| CHYMERA20 | 0.218 |
| ITO21 | 0.197 |
| WONG16 | 0.174 |
| HORLBECK18 | 0.158 |
| SLC25 | -0.090 |
| DIEHL21 | -0.300 |
