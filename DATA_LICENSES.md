# Data licenses

This audit records the source terms checked on 25 Nov 2026. It uses the Europe PMC article records, figshare and Zenodo deposits, STRING's licensing page and the Ensembl disclaimer. If an article and its deposit disagree, Opal-Bench follows the stricter terms.

"Raw" means the published counts or phenotype tables. "Derived" means the harmonized benchmark tables. The table records the redistribution decision for each source; it doesn't replace that source's license.

| Opal-Bench id | Study | Modality | Primary record | Licence found | Redistribute derived table? | In this repo |
|---|---|---|---|---|---|---|
| WONG16, SHEN17, NAJM18, ZHAO18, HORLBECK18, THOMPSON21, DIEHL21, PARRISH21, ITO21, TANG22 | 10 studies via SLKB (Gökbağ et al., NAR 2024) | Cas9 / Cas12a / CRISPRi | figshare 10.6084/m9.figshare.22902839 | **GPL-3.0+** (data deposit) | yes, GPL-3.0+ with attribution | data |
| CHYMERA20 | Gonatopoulos-Pournatzis 2020, Nat Biotechnol | Cas9 + Cas12a hybrid | GEO GSE144281 | GEO public data; NCBI places no restrictions and the submitters claim none | yes | data |
| SPIDR25 | Fielden 2025, Nature | CRISPRi | Suppl. Table 8, PMC12018271 | **CC BY 4.0** | yes | data |
| IN4MER24 | Esmaeili Anvar 2024, Nat Commun | enAsCas12a | Suppl. Data 6, PMC11055879 | **CC BY 4.0** | yes | data |
| HARLE25 | Harle 2025, Genome Biol | Cas9 | Additional file 1, PMC12445041 | **CC BY 4.0** | yes | data |
| BURGOLD25 | Burgold 2025, Nat Commun | Cas9 | Zenodo 10.5281/zenodo.17191951; PMC12808759 | **CC BY 4.0** (article and deposit) | yes | data (+ test cell line) |
| DEDE20 | Dede 2020, Genome Biol | enCas12a | figshare 13101142; PMC7558751 | CC BY 4.0 (article); CC BY + CC0 (deposit) | yes | data |
| SLC25 | Wolf 2025, Mol Syst Biol | Cas9 | Dataset EV3, PMC12130552 | **CC BY 4.0** | yes | data |
| ABBVIE25 | Cell Rep 2025 | enAsCas12a | Table S2, 10.1016/j.celrep.2025.116512 | **CC BY-NC-ND 4.0** | **no** (no derivatives) | excluded |
| KLINGBEIL24 | Klingbeil 2024, Cancer Discov | paired SpCas9 | AACR figshare 27938723; PMC11609825 | article **CC BY-NC-ND 4.0**; figshare item says CC BY → conflict, stricter applied | **no** | excluded |
| SCHEMATIC25 | Fong 2025, Nat Genet | Cas9 dual guide | Suppl. Data 1, 10.1038/s41588-024-01971-9 | publisher terms (no open licence) | **no** | excluded |
| DU17 | Du 2017, Nat Methods | CRISPRi | Suppl. Data Set 3, 10.1038/nmeth.4286 | publisher terms | **no** | excluded |
| HAN17 | Han 2017, Nat Biotechnol | Cas9 double knockout | Suppl. Table 4, 10.1038/nbt.3834 | publisher terms | **no** | excluded |
| SHEN26 (fresh) | Shen 2026, Natl Sci Rev | Cas9 dual guide | PMC13715443 (10.1093/nsr/nwag565), Table S2 raw counts, rescored | **CC BY 4.0** | yes | data/fresh |
| Pair priors | STRING v12 combined score; Ensembl Compara paralog identity | – | string-db.org licensing; Ensembl disclaimer | STRING: attribution (CC BY terms); Ensembl: no restrictions | yes | bench_priors |

## What ships here

The lab-level table contains 334,669 pairs from 17 labs. Fresh SHEN26 and the BURGOLD25 test cell-line table ship separately. Each data file keeps its source terms, including GPL-3.0-or-later requirements for the SLKB-derived files.

ABBVIE25, KLINGBEIL24, SCHEMATIC25, DU17 and HAN17 are excluded. Their raw-source preprocessing scripts aren't bundled.

`leaderboard/rows.csv.gz` contains per-draw MSE summaries for all 22 labs. Those aggregate errors aren't the underlying screen data.

The [MIT license](LICENSE) covers the original code. It doesn't change the data licenses. Cite the original sources you use and follow their terms when redistributing derived tables.
