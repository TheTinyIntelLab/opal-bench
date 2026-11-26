<div align="center">
  <img src="images/logo.png" width="160" alt="Opal logo" />
  <h1>Opal-Bench</h1>
  <p>Predict combinatorial CRISPR growth in a lab you have never seen.</p>
</div>

<div align="center">
  <a href="https://thetinyintelligencelab.vercel.app/"><img src="images/lab_badge.svg" alt="The Tiny Intelligence Lab" /></a>
  <a href="LICENSE"><img src="images/license_badge.svg" alt="Code license: MIT" /></a>
  <a href="DATA_LICENSES.md"><img src="images/data_badge.svg" alt="Data: per-source licenses" /></a>
</div>

<p align="center">
  <a href="#how-it-works">Benchmark</a> &middot;
  <a href="#install">Quick start</a> &middot;
  <a href="#results">Results</a> &middot;
  <a href="#submit-a-method">Submit a method</a> &middot;
  <a href="#data-and-reproduction">Data</a> &middot;
  <a href="https://huggingface.co/datasets/TheTinyIntelLab/opal-bench">Hugging Face</a> &middot;
  <a href="#citation">Citation</a>
</p>

Opal-Bench measures how well you can predict pair growth in a CRISPR screen your method hasn't seen. You get the screen's single-gene scores and at most k measured pairs, then predict the rest. Entire labs are held out, so pairs from the target lab can't leak into training through a random split.

The full benchmark covers 22 labs and 411,098 lab-level pairs across CRISPRi, Cas9, paired Cas9, Cas12a and CHyMErA. You can score the 17 shipped labs with NumPy and pandas on a CPU. Five restricted labs are excluded from the source data, but their aggregate evaluation rows remain in the leaderboard.

## How it works

Train on the allowed labs, then use the target screen's singles and k calibration pairs to predict its unmeasured pairs. Each method gets the same calibration draws, and the scorer excludes those pairs from evaluation.

<img src="images/benchmark_overview.svg" width="100%" alt="Other labs provide training pairs. Target singles and k measured pairs calibrate a method, which predicts the remaining target pairs. Scoring compares MSE against MID and averages over labs." />

| Track | Evaluation units | Allowed training | Measured pairs, k | Draws |
| --- | --- | --- | --- | --- |
| Development | 18 labs | Other development labs, nested leave-one-lab-out | 0, 10, 20, 50 | 20 |
| Locked test | 4 labs, 31 cell lines | 18 development labs | 0, 10, 20, 50 | 20 |
| Fresh SHEN26 | 2 cell lines | Every lab in the benchmark table | 0, 5, 20 | 50 |

At k = 0 there is one draw and the whole unit is scored. The main metric is **MSE / MSE(MID)**, geometrically averaged over labs after averaging log ratios over draws and cell lines within each lab. Lower is better; MID is 1. Rank intervals use 2,000 bootstrap replicates over labs, then cell lines where applicable.

For each screen, convert counts to CPM, compute log2 fold change, center on controls or singles, then divide by c = −(the fifth percentile of single-gene log fold changes), floored at 0.1. In these units ADD = sa + sb, MIN = min(sa, sb), and MID = ½(ADD + MIN).

Auxiliary tasks measure zero-shot held-out-lab prediction (`a`), 20-pair calibration (`a_fs20`), held-out genes (`b`), strong-negative-interaction AUROC (`c`) and between-lab reproducibility (`d`). The [full leaderboard](leaderboard/LEADERBOARD.md) includes every track.

### Supplemental tracks

- **Unseen genes.** Score growth MSE on test pairs with exactly one, exactly two, or at least one gene absent from the allowed training pairs and the current draw's calibration pairs. Each draw is evaluated against its own gene roster. Target singles are still available at prediction time. The K562 API entry includes the checkpoint's labeled training genes in its roster and omits its source lab from unseen-gene scoring. Submitters must declare any external training on labeled pair data before entering this track.
- **Top-5% hits.** Rank measured and predicted interactions by pair growth minus additive growth. The bottom 5% are the synergistic tail and the top 5% are the buffering tail, each rounded up to a whole number of pairs. Sort ties by pair key, take the first ranks for synergy and last ranks for buffering. Report precision and recall for both tails. They have the same value here because the predicted and measured sets have the same size. These are rank-based screen labels.
- **Uncertainty.** An adapter can return `opal_bench.fewshot.Prediction(point, lower, upper)` with a 90% prediction interval per row. Score the fraction of outcomes inside the inclusive bounds and mean interval width in normalized growth units. Compare width alongside coverage against the 90% target. With `--baseline-intervals`, the benchmark also reports empirical residual intervals for every rerunnable baseline with enough calibration pairs. The fixed rules and K562 API use the k calibration residuals. The ridge deterministically reserves half of k for residuals and use the other half to fit the interval center. The radius is the absolute residual at rank `ceil(0.90 * (m + 1))`, with ranks starting at one and `m` equal to the number of held-out calibration pairs. At least nine residuals are needed for a finite target-screen band. With `--training-intervals`, a baseline without enough target calibration pairs uses the largest eligible training screen, breaking ties by lab name and excluding any screen that supplied its frozen checkpoint. The benchmark uses a deterministic draw of k source pairs to fit adaptive baselines, then takes the same residual quantile on the remaining source pairs. Fixed baselines use the entire source screen for residuals. The radius is applied to the original target prediction, and those results carry `interval_source: training_screen`. Point scores retain the original calibration procedure. Training-screen intervals measure transfer and make no nominal coverage guarantee on a new screen.
- **Rolling prospective.** Register a dated, frozen submission to be scored only on later screen releases. The [prospective protocol](PROSPECTIVE.md) defines the freeze, eligibility and reporting rules.

Supplemental metrics use only non-calibration pairs and average draws within a cell line, then cell lines within a lab, then labs. An empty unseen cohort is omitted from that cohort's mean. Run `opal-bench-score tracks` to score the shipped development, locked-test and fresh splits at each supported budget.

## Install

Use Python 3.10 or newer. From this checkout:

```bash
python -m venv .venv
# Activate the environment for your shell, then:
python -m pip install -e ".[test]"
python -X utf8 -m pytest -q
opal-bench-score --help
```

The package is `Opal-Bench`; its Python import is `opal_bench`. Tests reproduce shipped baseline rows, the published leaderboard tables and tasks on the 17 shipped labs. The optional Opal re-score needs a separate growth bundle. A full test run takes about two minutes on one CPU.

```bash
opal-bench-score fewshot                        # Shipped dev, test and fresh baselines
opal-bench-score tasks                          # Auxiliary tasks on shipped data
opal-bench-score tracks --split test --budget 20 --baseline-intervals --training-intervals # Supplemental locked-test scores
opal-bench-score table leaderboard/rows.csv.gz  # Tables from the published rows
```

## Results

On the locked test, a six-coefficient ridge fitted to 20 target pairs comes close to the larger networks, with overlapping bootstrap rank intervals.

<img src="images/label_budget.svg" width="100%" alt="Six-coefficient ridge and official Opal K562 API scores across shipped calibration budgets." />

### Locked test, k = 20

| Method | MSE / MID | Rank [95% CI] |
| --- | ---: | ---: |
| NET_MLP | 0.424 | 1 [1–3] |
| NET_ATT | 0.425 | 2 [1–4] |
| Cross-lab ridge (FS_LIN5x) | 0.456 | 4 [3–4] |
| Six-coefficient ridge (FS_LIN5_lam) | 0.460 | 5 [4–5] |
| MID | 1.000 | 12 [12–13] |

<img src="images/locked_test.svg" width="100%" alt="The displayed locked-test methods at k = 20, with MSE ratios and bootstrap rank intervals. The small ridge and the largest networks have overlapping rank intervals." />

The figures use the published per-draw rows, including aggregate results for the five restricted labs. You can re-score the built-in rules and few-shot ridge here. The [leaderboard](leaderboard/LEADERBOARD.md) records method provenance and the measured parameter counts, peak RAM and CPU seconds for reproducible baselines on the shipped data. It also shows the two exact network parameter counts recorded in the original run. Historical methods with missing run artifacts are listed with their published scores.

### What did not transfer

With no target pairs, every tested learner loses to MID on the locked test. Foundation-model and graph features don't beat the singles-only few-shot ridge, and choosing calibration pairs actively performs worse than choosing them at random. On fresh SHEN26 at k = 20, the small ridge scores 1.046 against MID at 1.000. [Negative results](NEGATIVE_RESULTS.md) records the experiments behind these comparisons.

## Submit a method

Expose a factory that receives allowed training pairs and returns a predictor. Both predictor inputs contain singles, pair identifiers and any published covariates. Only calibration pairs carry outcomes. Return one finite point estimate per evaluation row, a `Prediction` with interval bounds, or `None` to abstain at an unsupported budget.

```python
import numpy as np


def make_method(train):
    def predict(cal, ev):
        return np.minimum(ev.sa, ev.sb).to_numpy()  # Example: MIN baseline
    return predict
```

```bash
opal-bench-score fewshot --method mypackage.mymodule:make_method --name MYMODEL --rows my_rows.csv.gz
```

Tune only by nested leave-one-lab-out on the allowed training labs. Use no target pair outcomes beyond the k calibration pairs, and never tune on the locked test or SHEN26. Calibration draws are fixed by the published md5 seeds; do not change splits, seeds, k grids or the metric.

To submit, open a pull request with rows covering the 22 benchmark labs and a link to your method code. Auxiliary tasks `a`–`c` accept a predictions CSV with `task,lab,key,pred`; `python -m opal_bench.template --help` describes the required rows.

The **Score a reviewed submission** GitHub Action reruns an approved adapter on the shipped data from its selected revision. In the pull request, include the adapter's import path, any pinned extra dependencies in `submissions/requirements.txt`, and the training-data declaration. A maintainer dispatches the workflow on a reviewed branch containing the importable adapter. The run summary posts the main and supplemental scores, and its artifact contains machine-readable results. For unseen-gene scoring, use only the supplied training/calibration pair outcomes, and disclose any fixed external resources. Locally, opt an eligible adapter in with `--unseen-method MYMODEL`. Adapters may skip entire budgets. An uncertainty entry must return finite, ordered bounds for every evaluation pair at an entered budget.

## Data and reproduction

The shipped lab-level table contains **334,669 pairs from 17 labs**. Source sizes vary substantially, so the metric gives each lab equal weight rather than letting the largest screen dominate.

<img src="images/data_coverage.svg" width="100%" alt="Pair counts for the 17 shipped labs. SPIDR25 and HORLBECK18 are the largest sources; BURGOLD25 is the shipped locked-test lab." />

| Path | Contents |
| --- | --- |
| `data/redistributable/bench_pairs.csv.gz` | Lab-level growth scores, gene pairs and single-gene scores |
| `data/redistributable/bench_priors.csv.gz` | STRING combined scores and Ensembl paralog identity |
| `data/redistributable/test_units.csv.gz` | 16,940 cell-line rows for BURGOLD25, HT-29 |
| `data/redistributable/by_source/` | One file for each shipped lab |
| `data/fresh/SHEN26.csv.gz` | 1,530 rows: 765 pairs across HCT116 and GM12878 |
| `leaderboard/rows.csv.gz` | 49,038 per-draw MSE rows across the published methods |

### Score the 22-lab benchmark locally

The public checkout covers 16 development labs, BURGOLD25 and fresh SHEN26. ABBVIE25, DU17, HAN17, KLINGBEIL24 and SCHEMATIC25 are excluded because their source terms restrict or don't clearly allow redistribution. Raw-source preprocessing scripts aren't bundled.

If you independently prepare compatible, normalized pair, prior and cell-line tables under the source terms, merge them with the shipped data:

```bash
python -m opal_bench.prepare --extra <dir>/bench_pairs.csv.gz --extra-priors <dir>/bench_priors.csv.gz --test-units <dir>/test_units.csv.gz
```

The scorer uses `data/full/` when it exists, and Git ignores it. [SHA256SUMS.txt](SHA256SUMS.txt) covers the shipped files.

## Limitations

The locked-test labs were used in earlier zero-shot pilots, so they were held out from few-shot development but are not pristine. SHEN26 was never used during development and provides the fresh check. Its interaction signal is small relative to noise, and model gains there are correspondingly smaller.

Lab agreement is limited: median between-lab correlation is 0.21 across the full benchmark. These scores measure pair-growth prediction under the declared data access rules; they do not establish biological discovery, causal interactions or universal transfer across screens. To our knowledge, this is the first public held-out-lab pair-growth benchmark spanning CRISPRi, Cas9, Cas12a and CHyMErA under one normalization. Related work includes SLKB (NAR 2024) and MLEC-iGeneCombo (2025).

## Foundation-model adapters

The shipped comparison covers `GenePT-ridge`, `ESM2-ridge`, `Geneformer-v2-ridge`, `scGPT-human-ridge`, `scGPT-pancancer-ridge`, `GeneCompass-ridge`, `UCE-33L-ridge`, `scFoundation-ridge`, and `scPRINT-ridge`. Each fits the same symmetric, 39-coefficient ridge to growth residuals against MID. It uses a 16-dimensional static gene representation, then adds a ridge adjustment at positive k using the assigned calibration pairs. The head reserves an eligible training lab for uncertainty calibration and keeps its labels out of the point fit. The footprint measures the head on CPU, including embedding loading, any projection and interval generation. It excludes upstream embedding generation.

For GenePT and ESM2, set `OPAL_BENCH_EMBEDDINGS` to the directory containing the exact archived projections at `semantic-GenePT/embedding.npz` and `semantic-ESM2/embedding.npz`. The adapters verify their hashes. The projections use resources from the [PRESAGE data release](https://doi.org/10.5281/zenodo.15587986) under CC BY-NC 4.0.

For the single-cell heads, use the [pinned Gene Embedding Hub snapshot](https://huggingface.co/datasets/BoevaLab/Gene-Embedding-Hub-dataset/tree/be4ceda18f562560c3f2253f054e2c3e5b97d31f/data). Download `data/master_gene_table.csv` and the `genes.tsv` and `embeddings.npz` files in these folders under `data/embeddings/`. The folder metadata links to each source checkpoint and its terms. Keep the files outside this checkout and set `OPAL_BENCH_GENE_HUB` to the downloaded `data` directory.

| Head | Hub folder |
| --- | --- |
| Geneformer-v2-ridge | `geneformer_v2_316m` |
| scGPT-human-ridge | `scgpt_whole_human` |
| scGPT-pancancer-ridge | `scgpt_pancancer` |
| GeneCompass-ridge | `genecompass_base_gene_token` |
| UCE-33L-ridge | `uce_33l` |
| scFoundation-ridge | `scfoundation_gene_pos` |
| scPRINT-ridge | `scprint_medium_v1_5_gene` |

The scorer verifies the bank and mapping hashes, projects each pinned matrix with a fixed seed, and standardizes the projected columns across the external bank. It joins Ensembl IDs to unique current gene symbols. A missing gene has a zero vector, and the head receives the count of mapped genes as a feature.

```bash
opal-bench-score fewshot --data data/redistributable --embedding-heads --opal-v1 DIR --json leaderboard/shipped-fewshot.json
opal-bench-score tracks --data data/redistributable --embedding-heads --opal-v1 DIR --baseline-intervals --training-intervals --historical-rows leaderboard/rows.csv.gz --json leaderboard/track-scores.json
```

Pass specific method names after `--embedding-heads` to run a subset. The [shipped few-shot comparison](leaderboard/shipped-fewshot.json) uses the built-in baselines on the same data. The original GenePT, Geneformer, scGPT and GEARS-style rows retain their published scores and refer to their original fitted adapters.

### Official Opal v1 API

`Opal-v1-API-K562` queries the official Opal v1 API with the pinned K562 growth bundle. It uses the source checkpoint's stored singles and divides its outputs by the negative fifth percentile of those singles, floored at 0.1. The benchmark uses target MID on abstentions and on the checkpoint's source screen, HORLBECK18. It also excludes that screen from the method's unseen-gene scores. The supplemental intervals are benchmark-calibrated residual bands. The API returned predictions on 849 of 213,776 non-source development rows and 57 of 16,940 shipped locked-test rows. It abstained on the 1,530 SHEN26 rows.

To reproduce the API entry, install the [Opal v1.0.0 release wheel](https://github.com/TheTinyIntelLab/opal/releases/tag/v1.0.0) and download the [pinned public growth bundle](https://huggingface.co/TheTinyIntelLab/opal-growth/tree/e8660c075632d50cb0b4ba4b59dd881eaf91ca78). Pass `--opal-v1 DIR` to either scorer. Add `--baseline-intervals --training-intervals` to `tracks` for its uncertainty scores. Pass those same Opal options to the footprint tool to measure the API entry.

## Roadmap

- **CRISPRa and CRISPRi.** Define evaluation by intervention direction so activation and repression can be compared across screens with different single-gene effects. The existing CRISPRi screens remain part of the current pair-growth benchmark.
- **Drug–gene pairs.** Define treatment, dose and cell context as part of each evaluation unit, with matching drug-only and gene-only controls.
- **Triples.** Define splits that account for observed constituent pairs and use a reference that distinguishes three-way effects from effects already explained by pairs.

These are planned extensions. This release ships no new data for them.

## Documentation and repository

- [Full leaderboard](leaderboard/LEADERBOARD.md) records results, ranks and method provenance.
- [Dataset card](DATASET_CARD.md) documents the data configurations and schemas.
- [Source licenses](DATA_LICENSES.md) records the redistribution audit for each lab.
- [Negative results](NEGATIVE_RESULTS.md) preserves unsuccessful experiments.
- `src/` contains scoring, baselines, metrics, data loading and adapters; `tests/` contains frozen numerical expectations.
- `tools/plot_readme.py` regenerates the benchmark figures. Install Matplotlib, then run `python tools/plot_readme.py`.

[Figure data](images/figure_data.json) records the plotted values and source hashes.

## License

Original code is [MIT licensed](LICENSE). Data keep their [per-source licenses](DATA_LICENSES.md), including GPL-3.0-or-later terms for the SLKB-derived labs. A code license does not override a source dataset's terms. Restricted source tables and trained checkpoints are not included.

## Citation

Use [CITATION.cff](CITATION.cff) to cite Opal-Bench, and cite the original data sources you use.

> Prakash, A. V. (2026). Opal-Bench: a held-out-lab benchmark for combinatorial CRISPR growth prediction. The Tiny Intelligence Lab.
