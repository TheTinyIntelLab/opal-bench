# What did not work

These results record experiments that failed their stated criteria. Every registration was hash-stamped before scoring; corrections were added as errata rather than edits. Confirmation n used the 100 · (1 − 0.025/n) percentile, following the registered Bonferroni-type schedule.

## No target pairs: MID remains the reference to beat

On the locked test at k = 0, every learner loses to MID. Errors range from 1.08× MID for gradient boosting to 2.12× for the MLP; foundation-model embeddings score 1.89–1.99×. On development labs, the range is 1.09–2.08×.

A rule-anchored zero-shot model also failed. It learned a per-lab mixing weight between min and additive, with atlas, STRING and paralog corrections, but scored 1.25× MID and was rejected.

## More features and larger models did not establish a clear advantage

Frozen GenePT, Geneformer and scGPT embeddings, and GEARS-style STRING propagation, each received a few-shot head. At k = 10 and 20, they performed worse than a six-coefficient ridge fitted only to the target pairs on both development labs and the locked test. At locked-test k = 20, their ratios were 0.50–0.53 against the ridge's 0.460.

The 582,657- and 844,801-parameter networks scored 0.424 and 0.425 on that test. Their rank intervals overlap, so the leaderboard doesn't separate them cleanly.

## Screen transfer and pair selection failed

ATLAS adds half a pair's mean cross-lab interaction to MID. That raised held-out-lab MSE to 1.29× MID, although it improved strong-negative ranking, with AUROC 0.795 against 0.708. Bayesian D-optimal selection, stratification by singles and atlas-uncertainty selection each performed worse than random calibration-pair selection on development labs.

Across 93 lab pairs, the interaction term y − additive had median between-lab Spearman correlation 0.21, with interval [0.13, 0.28]. A method has to transfer across sources that often disagree about the target itself.

## Registered experiments

There were 25 registrations and 18 confirmations; 3 confirmations passed. The rows below preserve the recorded questions, hash prefixes and outcomes.

| # | Pilot | Stage | Registration sha256 (prefix) | Question | Outcome |
|---|---|---|---|---|---|
| 1 | 1 | dev | a4891082 | K562→Jurkat residual transfer, singles only | FAIL |
| 2 | 1b | dev | eaf8c414 | same, fixed penalty | FAIL |
| 3 | 2 | dev | 0eb0db35 | pooled 7-parameter rule, leave-one-lab-out | FAIL (73% worse than min) |
| 4 | 3c | dev | 944dcc31 | singles-feature rule selection | FAIL |
| 5 | 3a | dev | 6276b58f | 25/50 target labels to mix rules | FAIL |
| 6 | 3b | dev | ebd3ee19 | new Ito lines, MLP + residual | FAIL |
| 7 | 4 | dev | 358b5b0d | empirical-Bayes shrinkage of carried-over interactions | FAIL |
| 8 | 5 | dev | 62e772c6 | EB-N / EB-SEL on Shen 2017 | FAIL |
| 9 | 6 | conf #1, #2 | bf4efa7b | ATLAS-MID on Dede + CHyMErA; cross-lab ρ > 0 in every line | **#1 PASS**; #2 FAIL |
| 10 | 7 | conf #3 | 665367cf | ATLAS-MID on SPIDR | FAIL (MID 1.91× better) |
| 11 | 8 | conf #4 | c74da6f3 | ATLAS-MID in in4mer, AbbVie, SLC | FAIL |
| 12 | 8 | conf #5 | c74da6f3 | CRISPRi follows min (Du 2017) | **PASS** (min 0.466× MID's error) |
| 13 | 8 | conf #6 | c74da6f3 | atlas improves SL AUROC | FAIL |
| 14 | 9 | conf #7 | 1cc1c8e8 | ATLAS-MID beats 7 baselines in Klingbeil 2024 | FAIL |
| 15 | 9 | conf #8 | 1cc1c8e8 | Klingbeil between-lab ρ < within-lab ρ | FAIL |
| 16 | 9 | conf #9 | 1cc1c8e8 | Klingbeil between-lab ρ < K562 replicate ceiling | **PASS** (Δ 0.265, lower bound 0.028) |
| 17 | 9 | conf #10 | 1cc1c8e8 | same-cell overlap raises agreement by < 0.10 | FAIL (inconclusive) |
| 18 | 10 | conf #11 | 880ba658 | per-line rescoring (gRES) raises between-lab ρ (Burgold 2025) | FAIL |
| 19 | 10 | conf #12 | 880ba658 | STRING-linked pairs agree better across labs | FAIL (direction held in 9/10 labs) |
| 20 | 10 | conf #13 | 880ba658 | paralog identity → more negative interaction | FAIL |
| 21 | 11 | conf #14 | 05eecacc | lead 1 sign test (SCHEMATIC, Han) | FAIL (low power) |
| 22 | 11 | conf #15 | 05eecacc | lead 1 pooled | FAIL (well powered; T −0.007) |
| 23 | 11 | conf #16 | 05eecacc | lead 1 pooled incl. Burgold | FAIL |
| 24 | 12 | conf #17 | a52e3857 | foundation-model embedding SGC-MLP ranks singles-free interactions in new screens | FAIL (Δρ +0.006, p 0.068, well powered) |
| 25 | 12 | conf #18 | a52e3857 | same, STRING ≥ 700 pairs | FAIL |

## Exploratory experiments

These experiments weren't registered and should be read separately from the confirmation table.

- E9 tested prior-based, graph-kNN, ridge and embedding predictors. Each lost to MID and min in leave-one-lab-out evaluation, at 1.26–1.61× MID MSE.
- E10 removed the parameter cap and tested LightGBM, a 137k-parameter MLP, SGC-GNN and ridge on frozen GenePT, Geneformer V2-104M and scGPT embeddings. Each lost to MID and min, at 1.18–2.79× MID.
- E10b found a small singles-free interaction-ranking signal, with median correlation 0.026, carried entirely by paralog and STRING pairs.
- E10c found that gene-feature classifiers lost to the zero-fit additive − min rule on strong negative interactions in 12–13/19 labs. On held-out genes, gene-feature models were 1.31–1.41× worse than an in-lab five-parameter linear rule, so their random-split gains didn't carry over to unseen genes.
- E10d rank-averaged the rule and a gene classifier. It didn't beat both inputs.

## What the supplemental scores test

The earlier held-out-gene pilot measured transfer within a lab. The supplemental track tests transfer to genes missing from the allowed cross-lab training roster and the current calibration draw.

On the shipped locked-test screen at k = 20, the six-coefficient ridge places more measured buffering hits in its top 5% than MID does. On fresh SHEN26 at the same budget, it places fewer. The [supplemental leaderboard](leaderboard/LEADERBOARD.md#supplemental-tracks) gives both tails and their settings. Low-budget uncertainty results use an allowed training screen to estimate the interval radius, so coverage on the target measures how well that radius transfers. The [prospective protocol](PROSPECTIVE.md) requires a frozen entry and a later eligible screen release.

### Shipped embedding baselines

At k = 20 on SHEN26, each of the nine embedding heads had higher growth error than the singles-only ridge. The test uses pinned representations with a common 39-coefficient ridge head. The [few-shot comparison](leaderboard/shipped-fewshot.json) records the ratios.

The shipped `Opal-v1-API-K562` run abstained on every fresh SHEN26 pair, so its predictions there reduce to MID. Its measured results use the pinned K562 source checkpoint and the benchmark's MID fallback. [API baseline](README.md#official-opal-v1-api)
