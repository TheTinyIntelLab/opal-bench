# Opal-Bench leaderboard

Lower ratios mean lower error. Each ratio compares a method's MSE with MID. The scorer averages log ratios over draws, then cell lines within each lab, then labs, and exponentiates the result. Each lab has equal weight.

Rank intervals are 95% bootstrap intervals from 2,000 replicates with seed 0. Development resamples labs; the test and fresh tracks resample labs, then cell lines. "Units better than MID" counts labs on development and cell lines on test and fresh.

## Where the rows come from

- Unmarked methods are built-in baselines you can re-score with `opal-bench-score fewshot`.
- ³ marks cross-lab learners from the original run. Each had the same tuning budget, grouped four-fold cross-validation over training labs and a few-shot ridge head on [1, lo, hi, lo·hi, f] for FS_* methods. Their per-draw rows are published; their training code isn't included here.

## Measured baseline footprint

The few-shot footprint covers one end-to-end pass over shipped dev, locked test and fresh splits at each supported budget. Each auxiliary row covers one pass of its named task on the shipped data. Each method ran in a fresh CPU process with one BLAS thread on Windows 10 build 19045, Intel Core i7-14700K, Python 3.14.0, NumPy 2.3.5 and pandas 2.3.3. CPU seconds measure process user plus system time during imports, data loading, fitting or calibration, prediction and error computation. Peak RAM is the process peak working set in MiB. Both include scorer overhead.

Params count the fitted numeric prediction coefficients or lookup values in a single predictor, at the largest fit if the count varies. The count excludes normalizers, fixed formulas and discrete choices between fixed rules.

The measured `Opal-v1-API-K562` entry uses the official API and the pinned public checkpoint. Its footprint includes loading the growth bundle. The original cross-lab training pipelines are needed to reproduce the remaining entries. The two network parameter counts come from the original run.

Reproduce the footprint JSON with `python -X utf8 tools/measure_footprint.py --opal-v1 DIR --out leaderboard/footprint.json`. On Windows the profiling tool uses `psutil` for the peak working set. The Opal v1 runs used the public growth bundle's `horlbeck_K562` checkpoint and schema. Pass `--embedding-heads` with the locally supplied banks to include the embedding heads. Their measurements include bank loading, any projection and interval generation. Their parameter counts describe the fitted head, and the precomputed embeddings are inputs. Timings and RAM vary by host and run.

### Few-shot

| Method | Params | Peak RAM (MiB) | CPU seconds |
|---|---|---|---|
| ADD | 0 | 379.13 | 9.516 |
| FS_LIN5_lam | 6 | 382.43 | 10.891 |
| MID | 0 | 381.38 | 8.047 |
| MIN | 0 | 380.61 | 7.875 |
| Opal-v1-API-K562 | 91,809 | 590.55 | 19.812 |
| GenePT-ridge | 39 | 489.02 | 50.047 |
| ESM2-ridge | 39 | 463.56 | 47.938 |
| Geneformer-v2-ridge | 39 | 467.43 | 47.953 |
| scGPT-human-ridge | 39 | 465.33 | 49.000 |
| scGPT-pancancer-ridge | 39 | 464.61 | 49.062 |
| GeneCompass-ridge | 39 | 464.89 | 45.734 |
| UCE-33L-ridge | 39 | 464.86 | 43.188 |
| scFoundation-ridge | 39 | 464.82 | 43.141 |
| scPRINT-ridge | 39 | 465.19 | 40.812 |

| Method | Params (recorded) |
|---|---|
| NET_ATT | 844,801 |
| NET_MLP | 582,657 |

The historical run recorded parameter counts for these two networks.

Only historical scores are available for `EMB_GenePT`, `EMB_Geneformer`, `EMB_scGPT`, `FS_EMB_GenePT`, `FS_EMB_Geneformer`, `FS_EMB_scGPT`, `FS_GBM`, `FS_GRAPH`, `FS_LIN5x`, `FS_MLP`, `GBM`, `GRAPH`, `LIN5x`, `MLP`.

### Auxiliary baselines

| Task | Method | Params | Peak RAM (MiB) | CPU seconds |
|---|---|---|---|---|
| a | ADD | 0 | 258.85 | 1.594 |
| a | MIN | 0 | 257.90 | 1.516 |
| a | MID | 0 | 258.62 | 1.516 |
| a | LIN5 | 6 | 258.74 | 2.859 |
| a | BEST_RULE | 0 | 259.10 | 2.969 |
| a | ATLAS | 328,752 | 258.65 | 10.297 |
| a_fs20 | ADD | 0 | 258.91 | 2.328 |
| a_fs20 | MIN | 0 | 257.67 | 2.312 |
| a_fs20 | MID | 0 | 258.98 | 2.141 |
| a_fs20 | LIN5 | 6 | 259.24 | 2.812 |
| a_fs20 | BEST_RULE | 0 | 258.75 | 2.406 |
| a_fs20 | ATLAS | 328,752 | 258.15 | 7.359 |
| a_fs20 | FS_BEST_RULE | 0 | 221.41 | 1.594 |
| a_fs20 | FS_LIN5 | 6 | 222.36 | 1.562 |
| b | ADD | 0 | 213.79 | 1.562 |
| b | MIN | 0 | 212.61 | 1.531 |
| b | MID | 0 | 213.68 | 1.641 |
| b | LIN5 | 6 | 214.01 | 1.578 |
| b | BEST_RULE | 0 | 212.43 | 1.609 |
| b | ATLAS | 328,448 | 283.30 | 23.797 |
| c | RULE_ADD_MINUS_MIN | 0 | 189.91 | 0.656 |
| c | LIN5 | 6 | 260.17 | 1.703 |
| c | BEST_RULE | 0 | 259.18 | 1.500 |
| c | ATLAS | 328,752 | 258.03 | 6.344 |

## Method names

ADD = sa + sb. MIN = min(sa, sb). MID = ½(ADD + MIN). FS_LIN5_lam fits a ridge with λ = 0.1 to the k target pairs, using [1, lo, hi, lo+hi, lo·hi, |hi−lo|].

LIN5x, GBM and MLP use singles, STRING and paralog features. EMB_* uses frozen GenePT, Geneformer or scGPT embeddings, while GRAPH uses GEARS-style STRING propagation. NET_ATT is an 844,801-parameter set-attention meta-learner; NET_MLP is a 582,657-parameter residual MLP.

The first tables show published results from the 22-lab benchmark. Ranks and intervals retain their original comparison sets. Shipped-data tables appear separately below. Run `opal-bench-score table leaderboard/rows.csv.gz` to recompute ranks over the displayed methods.

## Main track: few-shot held-out lab

### Development: 18 labs, nested leave-one-lab-out, 20 draws

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–3] | 0.609 | 0/18 |
| GBM ³ | 1.086 | 2 [1–6] | 0.255 | 10/18 |
| MIN | 1.135 | 3 [1–5] | 0.127 | 8/18 |
| ADD | 1.389 | 5 [2–11] | 0.004 | 3/18 |
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
| ADD | 1.388 | 15 [13–16] | 0.000 | 3/18 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_ATT ³ | 0.472 | 1 [1–4] | 0.804 | 18/18 |
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
| ADD | 1.388 | 15 [13–16] | 0.000 | 3/18 |

#### k = 50

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_ATT ³ | 0.410 | 1 [1–10] | 0.717 | 18/18 |
| FS_LIN5_lam | 0.427 | 2 [1–5] | 0.168 | 18/18 |
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
| ADD | 1.389 | 15 [13–16] | 0.000 | 3/18 |

### Locked test: 4 labs, 31 cell lines, 20 draws

These labs were never used to choose or tune any few-shot method. They were used in earlier zero-shot pilots, so the test is unused for this task but not pristine.

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–4] | 0.373 | 0/31 |
| GBM ³ | 1.083 | 2 [1–3] | 0.077 | 15/31 |
| MIN | 1.172 | 3 [1–6] | 0.275 | 24/31 |
| ADD | 1.265 | 4 [1–12] | 0.262 | 1/31 |
| LIN5x ³ | 1.604 | 6 [4–9] | 0.000 | 11/31 |
| GRAPH ³ | 1.811 | 8 [5–9] | 0.000 | 11/31 |
| EMB_Geneformer ³ | 1.889 | 9 [6–11] | 0.000 | 8/31 |
| EMB_scGPT ³ | 1.951 | 10 [8–11] | 0.000 | 4/31 |
| EMB_GenePT ³ | 1.993 | 11 [6–12] | 0.000 | 11/31 |
| MLP ³ | 2.121 | 12 [4–12] | 0.000 | 3/31 |

#### k = 10

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
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

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_MLP ³ | 0.424 | 1 [1–3] | 0.343 | 30/31 |
| NET_ATT ³ | 0.425 | 2 [1–4] | 0.386 | 30/31 |
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

#### k = 50

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| NET_MLP ³ | 0.381 | 1 [1–3] | 0.370 | 31/31 |
| NET_ATT ³ | 0.381 | 2 [1–4] | 0.360 | 31/31 |
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

### Fresh screen: SHEN26, 2 cell lines, 50 draws

This 2026 screen was never used during development and is not one of the 22 labs.

#### k = 0

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–1] | 1.000 | 0/2 |
| ADD | 1.028 | 2 [2–2] | 0.000 | 0/2 |
| MIN | 1.177 | 4 [4–4] | 0.000 | 0/2 |

#### k = 5

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 1 [1–2] | 0.745 | 0/2 |
| ADD | 1.028 | 2 [2–3] | 0.000 | 0/2 |
| MIN | 1.177 | 5 [5–6] | 0.000 | 0/2 |
| FS_LIN5_lam | 1.350 | 7 [5–7] | 0.000 | 0/2 |

#### k = 20

| method | ratio vs MID | rank [95% CI] | P(rank 1) | units better than MID |
|---|---|---|---|---|
| MID | 1.000 | 2 [2–3] | 0.000 | 0/2 |
| ADD | 1.029 | 3 [3–4] | 0.000 | 0/2 |
| FS_LIN5_lam | 1.046 | 4 [2–5] | 0.000 | 1/2 |
| MIN | 1.177 | 6 [6–6] | 0.000 | 0/2 |

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

## Shipped few-shot comparison

Nine embedding baselines use the same ridge head on distinct, pinned banks. The shipped comparison also includes the official K562 API run, `Opal-v1-API-K562`. The [few-shot comparison](shipped-fewshot.json) gives ratios against MID for each method and ships alongside the original full-data leaderboard. The [adapter documentation](../README.md#foundation-model-adapters) records the checkpoint representations and how to reproduce the comparison.

### At k = 20

| Method | Development | Locked test | Fresh SHEN26 |
|---|---:|---:|---:|
| FS_LIN5_lam | 0.492 | 0.142 | 1.046 |
| Opal-v1-API-K562 | 1.008 | 1.004 | 1.000 |
| GenePT-ridge | 1.479 | 0.399 | 2.190 |
| ESM2-ridge | 1.375 | 0.324 | 2.086 |
| Geneformer-v2-ridge | 1.452 | 0.383 | 2.065 |
| scGPT-human-ridge | 1.475 | 0.389 | 1.911 |
| scGPT-pancancer-ridge | 1.437 | 0.384 | 1.909 |
| GeneCompass-ridge | 1.529 | 0.472 | 1.956 |
| UCE-33L-ridge | 1.384 | 0.361 | 1.959 |
| scFoundation-ridge | 1.409 | 0.373 | 1.918 |
| scPRINT-ridge | 1.434 | 0.369 | 1.957 |

## Supplemental tracks

These tables cover every shipped split and calibration budget. They retain the historical model roster at each budget. A method with only published aggregate error rows is listed below the relevant supplemental table because its pair predictions can't be reconstructed from MSE.

Unseen-gene scores use the allowed training roster and the current draw's calibration roster. The official K562 API entry also counts genes with positive training degree in the checkpoint schema as seen. HORLBECK18 supplied its checkpoint training labels, so that screen is excluded from its unseen-gene scores. The point scorer uses target MID on that screen and for API abstentions.

MSE and mean interval width are in normalized growth units squared and normalized growth units, respectively. Precision, recall and interval coverage are fractions. Target-screen intervals use held-out calibration residuals. A dagger marks an interval whose radius came from an allowed training screen because the target budget was too small. The two interval sources have different assumptions about transfer, so compare coverage and width with the source in view. Point scores use the original predictors. The [track definitions](../README.md#supplemental-tracks) give the split and aggregation rules. The [unrounded scores](track-scores.json) include unseen-gene pair counts summed over draws.

Reproduce the tables with `opal-bench-score tracks --data data/redistributable --opal-v1 DIR --baseline-intervals --training-intervals --historical-rows leaderboard/rows.csv.gz`. Add `--embedding-heads` with the banks described in the [README](../README.md#foundation-model-adapters) to reproduce their rows.

### Shipped development

#### Measured pairs, k = 0

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.5755 | 0.7663 | 0.6775 | 1.0600 | 0.0628 | 0.0628 | 0.0508 | 0.0508 | 0.7359 † | 0.7963 † |
| ESM2-ridge | 4.6985 | 7.2173 | 6.2182 | 10.5745 | 0.1718 | 0.1718 | 0.3234 | 0.3234 | 0.6677 † | 0.6438 † |
| GeneCompass-ridge | 5.5579 | 8.5944 | 7.2132 | 13.2464 | 0.1677 | 0.1677 | 0.3304 | 0.3304 | 0.6474 † | 0.6227 † |
| GenePT-ridge | 5.4918 | 8.4774 | 7.1176 | 13.0647 | 0.1661 | 0.1661 | 0.2928 | 0.2928 | 0.6680 † | 0.6641 † |
| Geneformer-v2-ridge | 5.6303 | 8.7068 | 7.3027 | 13.4367 | 0.1729 | 0.1729 | 0.3339 | 0.3339 | 0.6386 † | 0.6146 † |
| MID | 1.2328 | 1.8211 | 1.6950 | 2.2388 | 0.2218 | 0.2218 | 0.4590 | 0.4590 | 0.7134 † | 0.5602 † |
| MIN | 5.2086 | 7.9727 | 7.2658 | 10.3508 | 0.2213 | 0.2213 | 0.4550 | 0.4550 | 0.6214 † | 0.4062 † |
| Opal-v1-API-K562 | 1.2365 | 1.9485 | 1.8133 | 2.3961 | 0.2207 | 0.2207 | 0.4596 | 0.4596 | 0.6869 † | 0.5284 † |
| UCE-33L-ridge | 5.7121 | 8.8399 | 7.3909 | 13.7208 | 0.2028 | 0.2028 | 0.3283 | 0.3283 | 0.6393 † | 0.6202 † |
| scFoundation-ridge | 5.5067 | 8.5108 | 7.1624 | 13.0534 | 0.1972 | 0.1972 | 0.3266 | 0.3266 | 0.6431 † | 0.6132 † |
| scGPT-human-ridge | 5.2957 | 8.1735 | 6.9264 | 12.3765 | 0.1713 | 0.1713 | 0.3187 | 0.3187 | 0.6443 † | 0.6227 † |
| scGPT-pancancer-ridge | 5.8010 | 8.9802 | 7.4924 | 13.9938 | 0.1678 | 0.1678 | 0.3246 | 0.3246 | 0.6495 † | 0.6313 † |
| scPRINT-ridge | 5.1250 | 7.8978 | 6.7323 | 11.8245 | 0.1541 | 0.1541 | 0.3319 | 0.3319 | 0.6446 † | 0.6203 † |

Historical few-shot scores only for `EMB_GenePT`, `EMB_Geneformer`, `EMB_scGPT`, `GBM`, `GRAPH`, `LIN5x`, `MLP`.

#### Measured pairs, k = 10

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.5754 | 0.7632 | 0.7049 | 1.0046 | 0.0626 | 0.0626 | 0.0510 | 0.0510 | 0.9031 | 1.9548 |
| ESM2-ridge | 1.4459 | 2.2682 | 1.6842 | 4.6733 | 0.1343 | 0.1343 | 0.2687 | 0.2687 | 0.6672 † | 0.5274 † |
| FS_LIN5_lam | 3.6461 | 6.3226 | 3.9151 | 16.3493 | 0.2299 | 0.2299 | 0.4405 | 0.4405 | 0.6567 † | 0.3574 † |
| GeneCompass-ridge | 1.2573 | 1.8957 | 1.4702 | 3.6495 | 0.1278 | 0.1278 | 0.2680 | 0.2680 | 0.6748 † | 0.5460 † |
| GenePT-ridge | 0.9347 | 1.3663 | 1.1080 | 2.4547 | 0.1209 | 0.1209 | 0.2610 | 0.2610 | 0.6682 † | 0.5428 † |
| Geneformer-v2-ridge | 0.8478 | 1.2318 | 0.9932 | 2.2330 | 0.1167 | 0.1167 | 0.2786 | 0.2786 | 0.6751 † | 0.5382 † |
| MID | 1.2330 | 1.7980 | 1.6770 | 2.3070 | 0.2224 | 0.2224 | 0.4567 | 0.4567 | 0.9026 | 2.0842 |
| MIN | 5.2088 | 7.8763 | 7.2720 | 10.4517 | 0.2223 | 0.2223 | 0.4534 | 0.4534 | 0.9047 | 3.4519 |
| Opal-v1-API-K562 | 1.2366 | 1.9237 | 1.7940 | 2.4692 | 0.2218 | 0.2218 | 0.4568 | 0.4568 | 0.9030 | 2.0907 |
| UCE-33L-ridge | 1.7438 | 2.7292 | 2.0627 | 5.5424 | 0.1269 | 0.1269 | 0.2666 | 0.2666 | 0.6704 † | 0.5452 † |
| scFoundation-ridge | 1.2247 | 1.8592 | 1.4382 | 3.5874 | 0.1393 | 0.1393 | 0.2752 | 0.2752 | 0.6778 † | 0.5306 † |
| scGPT-human-ridge | 0.7005 | 0.9893 | 0.8480 | 1.5908 | 0.1264 | 0.1264 | 0.2775 | 0.2775 | 0.6918 † | 0.5529 † |
| scGPT-pancancer-ridge | 1.0674 | 1.6400 | 1.2195 | 3.3805 | 0.1318 | 0.1318 | 0.2768 | 0.2768 | 0.6808 † | 0.5439 † |
| scPRINT-ridge | 0.9959 | 1.4829 | 1.1705 | 2.7905 | 0.1168 | 0.1168 | 0.2763 | 0.2763 | 0.6598 † | 0.5243 † |

Historical few-shot scores only for `FS_EMB_GenePT`, `FS_EMB_Geneformer`, `FS_EMB_scGPT`, `FS_GBM`, `FS_GRAPH`, `FS_LIN5x`, `FS_MLP`, `NET_ATT`, `NET_MLP`.

#### Measured pairs, k = 20

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.5755 | 0.7599 | 0.7127 | 0.9903 | 0.0627 | 0.0627 | 0.0505 | 0.0505 | 0.9062 | 1.6767 |
| ESM2-ridge | 0.7480 | 1.0015 | 0.8937 | 1.4856 | 0.1283 | 0.1283 | 0.2331 | 0.2331 | 0.9049 | 1.7505 |
| FS_LIN5_lam | 0.5542 | 0.8208 | 0.6925 | 1.4213 | 0.2416 | 0.2416 | 0.4431 | 0.4431 | 0.9018 | 1.5474 |
| GeneCompass-ridge | 0.8721 | 1.1556 | 1.0297 | 1.7580 | 0.1204 | 0.1204 | 0.2293 | 0.2293 | 0.9059 | 2.4183 |
| GenePT-ridge | 0.8303 | 1.1327 | 0.9880 | 1.8210 | 0.1122 | 0.1122 | 0.2279 | 0.2279 | 0.9087 | 1.9810 |
| Geneformer-v2-ridge | 0.7459 | 0.9948 | 0.8938 | 1.4854 | 0.1176 | 0.1176 | 0.2257 | 0.2257 | 0.9119 | 1.7894 |
| MID | 1.2329 | 1.8000 | 1.6876 | 2.3619 | 0.2220 | 0.2220 | 0.4569 | 0.4569 | 0.9053 | 1.8924 |
| MIN | 5.2089 | 7.8823 | 7.3446 | 10.5929 | 0.2216 | 0.2216 | 0.4535 | 0.4535 | 0.9087 | 3.0994 |
| Opal-v1-API-K562 | 1.2365 | 1.9259 | 1.8054 | 2.5280 | 0.2208 | 0.2208 | 0.4572 | 0.4572 | 0.9055 | 1.8942 |
| UCE-33L-ridge | 0.8088 | 1.0854 | 0.9693 | 1.6148 | 0.1225 | 0.1225 | 0.2413 | 0.2413 | 0.9081 | 1.9318 |
| scFoundation-ridge | 0.7917 | 1.0685 | 0.9398 | 1.6719 | 0.1249 | 0.1249 | 0.2307 | 0.2307 | 0.9061 | 1.9652 |
| scGPT-human-ridge | 0.9284 | 1.3057 | 1.1111 | 2.2601 | 0.1178 | 0.1178 | 0.2305 | 0.2305 | 0.9114 | 1.7816 |
| scGPT-pancancer-ridge | 0.7740 | 1.0312 | 0.9141 | 1.5860 | 0.1204 | 0.1204 | 0.2266 | 0.2266 | 0.9086 | 1.9581 |
| scPRINT-ridge | 0.7347 | 0.9827 | 0.8810 | 1.4706 | 0.1168 | 0.1168 | 0.2373 | 0.2373 | 0.9105 | 1.6691 |

Historical few-shot scores only for `FS_EMB_GenePT`, `FS_EMB_Geneformer`, `FS_EMB_scGPT`, `FS_GBM`, `FS_GRAPH`, `FS_LIN5x`, `FS_MLP`, `NET_ATT`, `NET_MLP`.

#### Measured pairs, k = 50

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.5758 | 0.7243 | 0.7072 | 0.8687 | 0.0623 | 0.0623 | 0.0503 | 0.0503 | 0.9024 | 1.4957 |
| ESM2-ridge | 0.8828 | 1.1121 | 1.0620 | 1.4425 | 0.1439 | 0.1439 | 0.2746 | 0.2746 | 0.9165 | 1.9141 |
| FS_LIN5_lam | 0.3687 | 0.5021 | 0.4755 | 0.7138 | 0.2407 | 0.2407 | 0.4591 | 0.4591 | 0.9218 | 1.4115 |
| GeneCompass-ridge | 0.9257 | 1.1040 | 1.0746 | 1.4114 | 0.1290 | 0.1290 | 0.2585 | 0.2585 | 0.9185 | 2.1185 |
| GenePT-ridge | 0.9267 | 1.1696 | 1.1233 | 1.6095 | 0.1341 | 0.1341 | 0.2815 | 0.2815 | 0.9235 | 2.1794 |
| Geneformer-v2-ridge | 0.9229 | 1.1351 | 1.0963 | 1.4055 | 0.1277 | 0.1277 | 0.2719 | 0.2719 | 0.9208 | 2.0325 |
| MID | 1.2328 | 1.7239 | 1.6470 | 2.3695 | 0.2227 | 0.2227 | 0.4543 | 0.4543 | 0.9035 | 1.8060 |
| MIN | 5.2090 | 7.4450 | 7.1164 | 10.2538 | 0.2227 | 0.2227 | 0.4513 | 0.4513 | 0.9015 | 3.0164 |
| Opal-v1-API-K562 | 1.2364 | 1.8443 | 1.7619 | 2.5362 | 0.2212 | 0.2212 | 0.4543 | 0.4543 | 0.9037 | 1.8078 |
| UCE-33L-ridge | 0.8096 | 1.0401 | 0.9771 | 1.5585 | 0.1374 | 0.1374 | 0.2899 | 0.2899 | 0.9221 | 1.9758 |
| scFoundation-ridge | 0.9542 | 1.2103 | 1.1581 | 1.6604 | 0.1395 | 0.1395 | 0.2749 | 0.2749 | 0.9211 | 1.9849 |
| scGPT-human-ridge | 0.8823 | 1.0141 | 0.9999 | 1.1998 | 0.1377 | 0.1377 | 0.2792 | 0.2792 | 0.9205 | 2.0143 |
| scGPT-pancancer-ridge | 0.9734 | 1.1260 | 1.1117 | 1.2562 | 0.1398 | 0.1398 | 0.2864 | 0.2864 | 0.9206 | 2.0747 |
| scPRINT-ridge | 0.8894 | 1.1229 | 1.0724 | 1.5725 | 0.1384 | 0.1384 | 0.2846 | 0.2846 | 0.9213 | 2.0288 |

Historical few-shot scores only for `FS_EMB_GenePT`, `FS_EMB_Geneformer`, `FS_EMB_scGPT`, `FS_GBM`, `FS_GRAPH`, `FS_LIN5x`, `FS_MLP`, `NET_ATT`, `NET_MLP`.

### Shipped locked test

#### Measured pairs, k = 0

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.9366 | 0.9305 | 0.9251 | 1.1645 | 0.0508 | 0.0508 | 0.0177 | 0.0177 | 0.0468 † | 0.7602 † |
| ESM2-ridge | 1.0512 | 1.0610 | 1.0622 | 1.0095 | 0.1039 | 0.1039 | 0.3908 | 0.3908 | 0.0136 † | 0.6165 † |
| GeneCompass-ridge | 1.1518 | 1.1281 | 1.1297 | 1.0597 | 0.1039 | 0.1039 | 0.4156 | 0.4156 | 0.0085 † | 0.6025 † |
| GenePT-ridge | 1.0280 | 1.0113 | 1.0136 | 0.9114 | 0.1145 | 0.1145 | 0.4026 | 0.4026 | 0.0143 † | 0.6137 † |
| Geneformer-v2-ridge | 1.1243 | 1.1028 | 1.1043 | 1.0366 | 0.0874 | 0.0874 | 0.4026 | 0.4026 | 0.0092 † | 0.5917 † |
| MID | 0.5368 | 0.5280 | 0.5275 | 0.5467 | 0.0531 | 0.0531 | 0.5136 | 0.5136 | 0.0749 † | 0.5565 † |
| MIN | 0.3401 | 0.3317 | 0.3354 | 0.1708 | 0.0519 | 0.0519 | 0.5124 | 0.5124 | 0.2080 † | 0.4059 † |
| Opal-v1-API-K562 | 0.5388 | 0.5280 | 0.5275 | 0.5467 | 0.0543 | 0.0543 | 0.5159 | 0.5159 | 0.0747 † | 0.5519 † |
| UCE-33L-ridge | 1.1574 | 1.1271 | 1.1303 | 0.9838 | 0.0980 | 0.0980 | 0.3943 | 0.3943 | 0.0081 † | 0.5993 † |
| scFoundation-ridge | 1.1552 | 1.1212 | 1.1240 | 0.9984 | 0.0980 | 0.0980 | 0.3896 | 0.3896 | 0.0082 † | 0.5923 † |
| scGPT-human-ridge | 1.1053 | 1.0858 | 1.0881 | 0.9882 | 0.0968 | 0.0968 | 0.3955 | 0.3955 | 0.0096 † | 0.5992 † |
| scGPT-pancancer-ridge | 1.1189 | 1.0888 | 1.0899 | 1.0417 | 0.0945 | 0.0945 | 0.3991 | 0.3991 | 0.0098 † | 0.6050 † |
| scPRINT-ridge | 1.1112 | 1.0923 | 1.0943 | 1.0063 | 0.0968 | 0.0968 | 0.4309 | 0.4309 | 0.0084 † | 0.5828 † |

Historical few-shot scores only for `EMB_GenePT`, `EMB_Geneformer`, `EMB_scGPT`, `GBM`, `GRAPH`, `LIN5x`, `MLP`.

#### Measured pairs, k = 10

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.9366 | 0.9268 | 0.9223 | 1.1639 | 0.0508 | 0.0508 | 0.0180 | 0.0180 | 0.9023 | 2.7239 |
| ESM2-ridge | 0.2390 | 0.2608 | 0.2594 | 0.3417 | 0.0717 | 0.0717 | 0.3252 | 0.3252 | 0.4212 † | 0.5268 † |
| FS_LIN5_lam | 0.1962 | 0.1864 | 0.1880 | 0.0577 | 0.0602 | 0.0602 | 0.3133 | 0.3133 | 0.4619 † | 0.3643 † |
| GeneCompass-ridge | 0.3163 | 0.3257 | 0.3230 | 0.4770 | 0.0672 | 0.0672 | 0.3194 | 0.3194 | 0.3642 † | 0.5379 † |
| GenePT-ridge | 0.2877 | 0.2919 | 0.2930 | 0.2273 | 0.0979 | 0.0979 | 0.2859 | 0.2859 | 0.3906 † | 0.5413 † |
| Geneformer-v2-ridge | 0.3466 | 0.3385 | 0.3388 | 0.3307 | 0.0677 | 0.0677 | 0.3434 | 0.3434 | 0.3344 † | 0.5348 † |
| MID | 0.5368 | 0.5276 | 0.5273 | 0.5463 | 0.0531 | 0.0531 | 0.5132 | 0.5132 | 0.9250 | 2.3923 |
| MIN | 0.3400 | 0.3342 | 0.3373 | 0.1706 | 0.0519 | 0.0519 | 0.5126 | 0.5126 | 0.9421 | 2.2752 |
| Opal-v1-API-K562 | 0.5388 | 0.5276 | 0.5273 | 0.5463 | 0.0543 | 0.0543 | 0.5162 | 0.5162 | 0.9241 | 2.3923 |
| UCE-33L-ridge | 0.2942 | 0.2731 | 0.2740 | 0.2132 | 0.0556 | 0.0556 | 0.3190 | 0.3190 | 0.3943 † | 0.5469 † |
| scFoundation-ridge | 0.3127 | 0.3010 | 0.3024 | 0.2317 | 0.0633 | 0.0633 | 0.3452 | 0.3452 | 0.3636 † | 0.5326 † |
| scGPT-human-ridge | 0.3135 | 0.3292 | 0.3246 | 0.5745 | 0.0757 | 0.0757 | 0.3468 | 0.3468 | 0.3774 † | 0.5528 † |
| scGPT-pancancer-ridge | 0.3480 | 0.3557 | 0.3541 | 0.4284 | 0.0724 | 0.0724 | 0.3335 | 0.3335 | 0.3394 † | 0.5354 † |
| scPRINT-ridge | 0.2821 | 0.2942 | 0.2900 | 0.5144 | 0.0653 | 0.0653 | 0.3554 | 0.3554 | 0.3930 † | 0.5141 † |

Historical few-shot scores only for `FS_EMB_GenePT`, `FS_EMB_Geneformer`, `FS_EMB_scGPT`, `FS_GBM`, `FS_GRAPH`, `FS_LIN5x`, `FS_MLP`, `NET_ATT`, `NET_MLP`.

#### Measured pairs, k = 20

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.9366 | 0.9217 | 0.9182 | 1.1682 | 0.0508 | 0.0508 | 0.0181 | 0.0181 | 0.9086 | 2.5491 |
| ESM2-ridge | 0.1818 | 0.1950 | 0.1943 | 0.2655 | 0.0572 | 0.0572 | 0.3675 | 0.3675 | 0.9208 | 1.8431 |
| FS_LIN5_lam | 0.0780 | 0.0739 | 0.0744 | 0.0428 | 0.0780 | 0.0780 | 0.5525 | 0.5525 | 0.9147 | 1.2579 |
| GeneCompass-ridge | 0.2580 | 0.2487 | 0.2477 | 0.3211 | 0.0573 | 0.0573 | 0.3288 | 0.3288 | 0.9197 | 2.1561 |
| GenePT-ridge | 0.2311 | 0.2310 | 0.2316 | 0.2085 | 0.0776 | 0.0776 | 0.2690 | 0.2690 | 0.9310 | 2.1095 |
| Geneformer-v2-ridge | 0.2156 | 0.2043 | 0.2046 | 0.2034 | 0.0611 | 0.0611 | 0.3655 | 0.3655 | 0.8996 | 1.8352 |
| MID | 0.5368 | 0.5274 | 0.5271 | 0.5492 | 0.0531 | 0.0531 | 0.5136 | 0.5136 | 0.8908 | 2.0214 |
| MIN | 0.3401 | 0.3380 | 0.3404 | 0.1720 | 0.0520 | 0.0520 | 0.5128 | 0.5128 | 0.9033 | 1.8810 |
| Opal-v1-API-K562 | 0.5388 | 0.5274 | 0.5271 | 0.5492 | 0.0543 | 0.0543 | 0.5164 | 0.5164 | 0.8901 | 2.0245 |
| UCE-33L-ridge | 0.2058 | 0.1937 | 0.1943 | 0.1767 | 0.0489 | 0.0489 | 0.3199 | 0.3199 | 0.8855 | 1.9295 |
| scFoundation-ridge | 0.2072 | 0.1989 | 0.2002 | 0.1123 | 0.0569 | 0.0569 | 0.3417 | 0.3417 | 0.8663 | 1.8202 |
| scGPT-human-ridge | 0.2133 | 0.2140 | 0.2130 | 0.2843 | 0.0571 | 0.0571 | 0.3521 | 0.3521 | 0.9037 | 1.9817 |
| scGPT-pancancer-ridge | 0.2139 | 0.2120 | 0.2117 | 0.2529 | 0.0681 | 0.0681 | 0.3545 | 0.3545 | 0.8880 | 1.9484 |
| scPRINT-ridge | 0.2023 | 0.2036 | 0.2027 | 0.2800 | 0.0693 | 0.0693 | 0.3391 | 0.3391 | 0.9171 | 2.0900 |

Historical few-shot scores only for `FS_EMB_GenePT`, `FS_EMB_Geneformer`, `FS_EMB_scGPT`, `FS_GBM`, `FS_GRAPH`, `FS_LIN5x`, `FS_MLP`, `NET_ATT`, `NET_MLP`.

#### Measured pairs, k = 50

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.9366 | 0.9099 | 0.9089 | 1.1744 | 0.0507 | 0.0507 | 0.0186 | 0.0186 | 0.9122 | 2.5315 |
| ESM2-ridge | 0.1580 | 0.1721 | 0.1720 | 0.1819 | 0.0608 | 0.0608 | 0.3314 | 0.3314 | 0.9258 | 1.6201 |
| FS_LIN5_lam | 0.0658 | 0.0627 | 0.0627 | 0.0487 | 0.0788 | 0.0788 | 0.5613 | 0.5613 | 0.9087 | 0.9753 |
| GeneCompass-ridge | 0.2066 | 0.1914 | 0.1911 | 0.2528 | 0.0612 | 0.0612 | 0.3298 | 0.3298 | 0.9060 | 1.8132 |
| GenePT-ridge | 0.1626 | 0.1675 | 0.1675 | 0.1744 | 0.0597 | 0.0597 | 0.3202 | 0.3202 | 0.9478 | 1.9082 |
| Geneformer-v2-ridge | 0.2003 | 0.1971 | 0.1973 | 0.1402 | 0.0533 | 0.0533 | 0.3235 | 0.3235 | 0.9320 | 1.9632 |
| MID | 0.5368 | 0.5269 | 0.5268 | 0.5538 | 0.0531 | 0.0531 | 0.5130 | 0.5130 | 0.8997 | 2.0481 |
| MIN | 0.3400 | 0.3467 | 0.3474 | 0.1750 | 0.0520 | 0.0520 | 0.5124 | 0.5124 | 0.8999 | 1.8331 |
| Opal-v1-API-K562 | 0.5388 | 0.5269 | 0.5268 | 0.5538 | 0.0543 | 0.0543 | 0.5159 | 0.5159 | 0.9022 | 2.0592 |
| UCE-33L-ridge | 0.1584 | 0.1534 | 0.1535 | 0.1241 | 0.0536 | 0.0536 | 0.3446 | 0.3446 | 0.9246 | 1.6863 |
| scFoundation-ridge | 0.1845 | 0.1829 | 0.1831 | 0.1165 | 0.0611 | 0.0611 | 0.3427 | 0.3427 | 0.9149 | 1.7314 |
| scGPT-human-ridge | 0.1877 | 0.1899 | 0.1899 | 0.1655 | 0.0647 | 0.0647 | 0.3138 | 0.3138 | 0.9355 | 1.8015 |
| scGPT-pancancer-ridge | 0.2096 | 0.2083 | 0.2083 | 0.1958 | 0.0612 | 0.0612 | 0.3055 | 0.3055 | 0.9157 | 1.6957 |
| scPRINT-ridge | 0.1798 | 0.1784 | 0.1781 | 0.2367 | 0.0713 | 0.0713 | 0.3170 | 0.3170 | 0.9058 | 1.5773 |

Historical few-shot scores only for `FS_EMB_GenePT`, `FS_EMB_Geneformer`, `FS_EMB_scGPT`, `FS_GBM`, `FS_GRAPH`, `FS_LIN5x`, `FS_MLP`, `NET_ATT`, `NET_MLP`.

### Fresh SHEN26

#### Measured pairs, k = 0

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.2529 | 0.1867 | 0.1656 | 0.2225 | 0.0385 | 0.0385 | 0.0641 | 0.0641 | 0.6183 † | 0.7602 † |
| ESM2-ridge | 0.2615 | 0.1904 | 0.1820 | 0.2045 | 0.1154 | 0.1154 | 0.1667 | 0.1667 | 0.5686 † | 0.6678 † |
| GeneCompass-ridge | 0.2686 | 0.1990 | 0.1952 | 0.2054 | 0.1282 | 0.1282 | 0.2564 | 0.2564 | 0.4817 † | 0.5634 † |
| GenePT-ridge | 0.2877 | 0.2042 | 0.1939 | 0.2218 | 0.0256 | 0.0256 | 0.1923 | 0.1923 | 0.5778 † | 0.7318 † |
| Geneformer-v2-ridge | 0.2765 | 0.1992 | 0.1959 | 0.2047 | 0.1410 | 0.1410 | 0.2308 | 0.2308 | 0.4673 † | 0.5541 † |
| MID | 0.2458 | 0.1620 | 0.1505 | 0.1813 | 0.2436 | 0.2436 | 0.2821 | 0.2821 | 0.4902 † | 0.5565 † |
| MIN | 0.2892 | 0.1777 | 0.1754 | 0.1815 | 0.2436 | 0.2436 | 0.2821 | 0.2821 | 0.3301 † | 0.4059 † |
| Opal-v1-API-K562 | 0.2458 | 0.1620 | 0.1505 | 0.1813 | 0.2436 | 0.2436 | 0.2821 | 0.2821 | 0.4869 † | 0.5519 † |
| UCE-33L-ridge | 0.2808 | 0.1995 | 0.1965 | 0.2045 | 0.1923 | 0.1923 | 0.2051 | 0.2051 | 0.4556 † | 0.5274 † |
| scFoundation-ridge | 0.2777 | 0.1984 | 0.1960 | 0.2025 | 0.1667 | 0.1667 | 0.2436 | 0.2436 | 0.4425 † | 0.4995 † |
| scGPT-human-ridge | 0.2686 | 0.1974 | 0.1844 | 0.2193 | 0.1538 | 0.1538 | 0.2308 | 0.2308 | 0.5098 † | 0.6067 † |
| scGPT-pancancer-ridge | 0.2638 | 0.1920 | 0.1835 | 0.2064 | 0.1282 | 0.1282 | 0.2308 | 0.2308 | 0.5203 † | 0.6062 † |
| scPRINT-ridge | 0.2538 | 0.1774 | 0.1654 | 0.1976 | 0.0897 | 0.0897 | 0.2179 | 0.2179 | 0.5105 † | 0.5793 † |

#### Measured pairs, k = 5

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.2528 | 0.1868 | 0.1656 | 0.2227 | 0.0392 | 0.0392 | 0.0655 | 0.0655 | 0.6185 † | 0.7602 † |
| ESM2-ridge | 0.3086 | 0.2408 | 0.2285 | 0.2617 | 0.0834 | 0.0834 | 0.1421 | 0.1421 | 0.4701 † | 0.6192 † |
| FS_LIN5_lam | 0.4145 | 0.3479 | 0.3978 | 0.2637 | 0.2142 | 0.2142 | 0.2232 | 0.2232 | 0.2537 † | 0.3022 † |
| GeneCompass-ridge | 0.2803 | 0.2147 | 0.2094 | 0.2237 | 0.0837 | 0.0837 | 0.1761 | 0.1761 | 0.4668 † | 0.5702 † |
| GenePT-ridge | 0.3277 | 0.2531 | 0.2348 | 0.2840 | 0.0384 | 0.0384 | 0.1358 | 0.1358 | 0.4746 † | 0.6394 † |
| Geneformer-v2-ridge | 0.2944 | 0.2210 | 0.2113 | 0.2374 | 0.0850 | 0.0850 | 0.1650 | 0.1650 | 0.4489 † | 0.5663 † |
| MID | 0.2457 | 0.1620 | 0.1505 | 0.1815 | 0.2384 | 0.2384 | 0.2784 | 0.2784 | 0.4905 † | 0.5565 † |
| MIN | 0.2891 | 0.1776 | 0.1753 | 0.1815 | 0.2384 | 0.2384 | 0.2784 | 0.2784 | 0.3304 † | 0.4059 † |
| Opal-v1-API-K562 | 0.2457 | 0.1620 | 0.1505 | 0.1815 | 0.2384 | 0.2384 | 0.2784 | 0.2784 | 0.4872 † | 0.5519 † |
| UCE-33L-ridge | 0.3258 | 0.2485 | 0.2470 | 0.2510 | 0.0853 | 0.0853 | 0.1505 | 0.1505 | 0.4181 † | 0.5529 † |
| scFoundation-ridge | 0.2847 | 0.2111 | 0.2074 | 0.2174 | 0.0966 | 0.0966 | 0.1700 | 0.1700 | 0.4129 † | 0.4965 † |
| scGPT-human-ridge | 0.2980 | 0.2270 | 0.2165 | 0.2446 | 0.0942 | 0.0942 | 0.1639 | 0.1639 | 0.4645 † | 0.5927 † |
| scGPT-pancancer-ridge | 0.2989 | 0.2224 | 0.2171 | 0.2312 | 0.0842 | 0.0842 | 0.1595 | 0.1595 | 0.4749 † | 0.6031 † |
| scPRINT-ridge | 0.2995 | 0.2288 | 0.2181 | 0.2470 | 0.0784 | 0.0784 | 0.1574 | 0.1574 | 0.4186 † | 0.5329 † |

#### Measured pairs, k = 20

| method | MSE | unseen MSE | one unseen MSE | both unseen MSE | synergy precision | synergy recall | buffering precision | buffering recall | 90% coverage | mean interval width |
|---|---|---|---|---|---|---|---|---|---|---|
| ADD | 0.2526 | 0.1875 | 0.1666 | 0.2228 | 0.0429 | 0.0429 | 0.0637 | 0.0637 | 0.9068 | 1.8450 |
| ESM2-ridge | 0.5381 | 0.4650 | 0.4493 | 0.4915 | 0.0789 | 0.0789 | 0.1032 | 0.1032 | 0.9082 | 2.3638 |
| FS_LIN5_lam | 0.2657 | 0.1835 | 0.1964 | 0.1619 | 0.2508 | 0.2508 | 0.2018 | 0.2018 | 0.9209 | 2.4840 |
| GeneCompass-ridge | 0.5083 | 0.4293 | 0.4257 | 0.4355 | 0.0750 | 0.0750 | 0.1074 | 0.1074 | 0.9084 | 2.3537 |
| GenePT-ridge | 0.5715 | 0.5202 | 0.4888 | 0.5730 | 0.0624 | 0.0624 | 0.1034 | 0.1034 | 0.9072 | 2.4748 |
| Geneformer-v2-ridge | 0.5382 | 0.4655 | 0.4536 | 0.4856 | 0.0511 | 0.0511 | 0.0937 | 0.0937 | 0.9048 | 2.2809 |
| MID | 0.2455 | 0.1625 | 0.1511 | 0.1816 | 0.2484 | 0.2484 | 0.2829 | 0.2829 | 0.9089 | 1.8068 |
| MIN | 0.2888 | 0.1779 | 0.1757 | 0.1817 | 0.2484 | 0.2484 | 0.2829 | 0.2829 | 0.9112 | 1.9192 |
| Opal-v1-API-K562 | 0.2455 | 0.1625 | 0.1511 | 0.1816 | 0.2484 | 0.2484 | 0.2829 | 0.2829 | 0.9089 | 1.8068 |
| UCE-33L-ridge | 0.5136 | 0.4171 | 0.4155 | 0.4195 | 0.0753 | 0.0753 | 0.1166 | 0.1166 | 0.9022 | 2.3814 |
| scFoundation-ridge | 0.4967 | 0.4142 | 0.4107 | 0.4202 | 0.0732 | 0.0732 | 0.0989 | 0.0989 | 0.9166 | 2.3907 |
| scGPT-human-ridge | 0.4992 | 0.4197 | 0.4163 | 0.4253 | 0.0824 | 0.0824 | 0.1124 | 0.1124 | 0.9116 | 2.3637 |
| scGPT-pancancer-ridge | 0.5028 | 0.4052 | 0.4049 | 0.4054 | 0.0779 | 0.0779 | 0.1055 | 0.1055 | 0.9062 | 2.2365 |
| scPRINT-ridge | 0.5045 | 0.4373 | 0.4280 | 0.4531 | 0.0803 | 0.0803 | 0.1008 | 0.1008 | 0.9171 | 2.4800 |
