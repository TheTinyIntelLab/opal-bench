---
license: other
license_name: per-source
license_link: DATA_LICENSES.md
pretty_name: Opal-Bench
language:
- en
tags:
- biology
- genomics
- crispr
- genetic-interactions
- synthetic-lethality
- benchmark
- few-shot
task_categories:
- tabular-regression
size_categories:
- 100K<n<1M
configs:
- config_name: pairs
  data_files:
  - split: train
    path: data/redistributable/bench_pairs.csv.gz
- config_name: priors
  data_files:
  - split: train
    path: data/redistributable/bench_priors.csv.gz
- config_name: test_units
  data_files:
  - split: test
    path: data/redistributable/test_units.csv.gz
- config_name: fresh_shen26
  data_files:
  - split: test
    path: data/fresh/SHEN26.csv.gz
- config_name: leaderboard_rows
  data_files:
  - split: train
    path: leaderboard/rows.csv.gz
---
# Opal-Bench

Predict combinatorial CRISPR pair growth from single-gene scores and a small set of measured pairs in a new screen. Opal-Bench is a benchmark from The Tiny Intelligence Lab. The [GitHub repository](https://github.com/TheTinyIntelLab/opal-bench) contains the scorer, tests and full leaderboard.

## Choose a configuration

| Config | File | Rows | What |
|---|---|---|---|
| pairs | data/redistributable/bench_pairs.csv.gz | 334,669 | 17 labs; lab-level means. Columns: lab, key (geneA\|geneB, alphabetical), a, b, sa, sb (single-gene scores), y (pair score), n_lines |
| priors | data/redistributable/bench_priors.csv.gz | 328,777 | STRING v12 combined score, Ensembl paralog identity (%) |
| test_units | data/redistributable/test_units.csv.gz | 16,940 | cell-line rows of the shipped locked-test lab (BURGOLD25, HT-29) |
| fresh_shen26 | data/fresh/SHEN26.csv.gz | 1,530 | Shen et al. 2026: 765 paralog pairs × HCT116 and GM12878, plus scale_c and priors |
| leaderboard_rows | leaderboard/rows.csv.gz | 49,038 | per-draw MSE of every leaderboard method on all 22 labs |

The `by_source/` directory also has one file for each shipped lab. The `train` and `test` names above are dataset-loader split names; the benchmark's development and locked-test assignments are defined separately by lab.

## How the scores were made

Each screen starts with published counts or phenotype tables, never raw reads. Counts become CPM and then log2 fold changes. Scores are centered on control constructs, or on singles when there aren't enough controls. Each cell line is divided by c = −(the fifth percentile of single-gene log fold changes), floored at 0.1. Lab-level tables average the normalized cell-line scores.

In these units, the additive prediction is sa + sb. The scorer compares each method's MSE with MID and gives every lab equal weight. See the GitHub README for the metric and calibration seeds.

## Benchmark splits

- Development uses 18 labs with nested leave-one-lab-out evaluation, so each target lab is excluded from training.
- The locked test uses BURGOLD25, HAN17, KLINGBEIL24 and SCHEMATIC25 at cell-line level, covering 31 lines.
- Fresh SHEN26 covers two cell lines and was never used during development.

The locked-test labs appeared in earlier zero-shot pilots, but weren't used to develop or tune a few-shot method. Their held-out status applies to the few-shot task, not to every earlier research experiment.

## Source licenses

Each source keeps its own terms, listed in [DATA_LICENSES.md](DATA_LICENSES.md). Ten SLKB-derived labs use GPL-3.0-or-later terms. The remaining shipped sources use CC BY 4.0, CC0 or GEO public-data terms.

ABBVIE25, KLINGBEIL24, SCHEMATIC25, DU17 and HAN17 aren't included because their licenses restrict or don't clearly allow redistribution. Their per-draw MSE summaries are in the leaderboard, but their source tables and raw-source preprocessing scripts aren't bundled.

## Limits of the data

Lab-level means hide differences between cell lines. Gene symbols are kept as published, and library designs differ substantially across sources, including paralog-focused, random and functional gene sets. A model that does well on one source may fail on another.

The main benchmark labs were used at some point in the research behind Opal-Bench. SHEN26 is the fresh check. Don't use its outcomes or locked-test outcomes to tune a method.

## Citation

Prakash, A. V. (2026). Opal-Bench: a held-out-lab benchmark for combinatorial CRISPR growth prediction. The Tiny Intelligence Lab.

Please also cite the original sources you use.
