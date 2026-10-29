# Spike: the CN / LMCI / AD arm (2026-10-29)

Read-only and aggregate-only (`scripts/spike_stage_arm.py`). It reads `cohort.csv`, the primary export and, for the floor comparison only, the cleaned tables, each checked against the manifest that records it. It counts the arm's participants and covariate levels, measures the run offset of each block on the arm's rows of the primary export with the export's own definition, and measures how far the floors would move if recomputed over the arm. It reads no MOTCO output and computes no sex or stage contrast of a metabolite. No participant identifier or value is written.

## Inputs

| file | sha256 | equals its record |
|---|---|---|
| `cohort_manifest.json` | `dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630` | yes |
| `cohort.csv` | `fe70cbf2e38f21ab25c9f32bfb1c503387b8eab2babf96aba7a286ea02b109ce` | yes |
| `p180.csv` | `5547356eb1761705eeee2295cfe5838e302821594b5b2675630419123861402e` | yes |
| `nmr.csv` | `a90d3eb43a86db456861e53a413f73ce8c70ec4d121eaa56e258725493114e43` | yes |
| `metadata.csv` | `9c445b7de5a50ee14c0771f2ebf57416120e46f6daa3703e48ff90308cecf221` | yes |
| `covariates.csv` | `06999e827d4f6eb6987bfa9c63bb24f9dfd4c07dfac96ce0b55500e8cd3fccfd` | yes |
| `features_p180.csv` | `7793776534d580f9a49e0ad95e0d8f6ecef3b5a7ff3c02f64dd07c905f4bb5ee` | yes |
| `features_nmr.csv` | `d4495f6aae38985460a118582e8e3250f9c56b8e27fc38d64bedc5b14514b9ee` | yes |
| `p180/P180.csv` | `33b18bd2187173179aa280ee74fc0a8f37ca2f155cdd37d4f87412631132ff9d` | yes |
| `nmr/NMR.csv` | `e711d62cf03f9da3f761fb18bfe4acb2d5fdf15fab6695fa5ed3901fa45d3159` | yes |

The 1501 rows of `cohort.csv` with both platform flags are the exported participants in export order, and their sex and stage equal `metadata.csv`.

## Participants

Exported: 1501. Dropped by the arm (`dx_bl` SMC or EMCI): 371. Kept: 1130.

| dx_bl | stage (STAGE_RULE) | Female ADNI1 | Female ADNI2GO | Male ADNI1 | Male ADNI2GO | total | in the arm |
|---|---|---|---|---|---|---|---|
| CN | CN | 94 | 89 | 98 | 83 | 364 | yes |
| SMC | CN | 0 | 54 | 0 | 42 | 96 | no |
| EMCI | MCI | 0 | 123 | 0 | 152 | 275 | no |
| LMCI | MCI | 117 | 70 | 221 | 75 | 483 | yes |
| AD | AD | 72 | 53 | 82 | 76 | 283 | yes |

Rows whose stage differs from the arm's map of `dx_bl` (CN → CN, LMCI → MCI, AD → AD): 0.

### Sex × stage cells

| sex | CN primary | MCI primary | AD primary | CN arm | MCI arm | AD arm |
|---|---|---|---|---|---|---|
| Female | 237 | 310 | 125 | 183 | 187 | 125 |
| Male | 223 | 448 | 158 | 181 | 296 | 158 |

### Phase within stage

Share of ADNI-1 participants per stage, and the `dx_bl` categories each run contributes to the stage.

| stage | set | n | ADNI1 | ADNI2GO | ADNI1 share | dx_bl in ADNI1 | dx_bl in ADNI2GO |
|---|---|---|---|---|---|---|---|
| CN | primary | 460 | 192 | 268 | 0.417 | CN | CN, SMC |
| CN | arm | 364 | 192 | 172 | 0.527 | CN | CN |
| MCI | primary | 758 | 338 | 420 | 0.446 | LMCI | EMCI, LMCI |
| MCI | arm | 483 | 338 | 145 | 0.700 | LMCI | LMCI |
| AD | primary | 283 | 154 | 129 | 0.544 | AD | AD |
| AD | arm | 283 | 154 | 129 | 0.544 | AD | AD |

## Covariates

| covariate | set | levels | missing |
|---|---|---|---|
| age | primary | mean 73.703, sd 7.180 | 0 |
| age | arm | mean 74.450, sd 7.060 | 0 |
| education | primary | mean 15.927, sd 2.854 | 0 |
| education | arm | mean 15.842, sd 2.911 | 0 |
| apoe4 | primary | 0 810, 1 542, 2 149 | 0 |
| apoe4 | arm | 0 589, 1 413, 2 128 | 0 |
| phase | primary | ADNI1 684, ADNI2GO 817 | 0 |
| phase | arm | ADNI1 684, ADNI2GO 446 | 0 |
| statin | primary | 0 797, 1 704 | 0 |
| statin | arm | 0 603, 1 527 | 0 |

Stage-means design of the arm (6 cell indicators and the 6 covariate design columns): 12 columns, rank 12.

Per arm cell:

| sex | stage | n | apoe4 0 / 1 / 2 | phase ADNI1 / ADNI2GO | statin 0 / 1 |
|---|---|---|---|---|---|
| Female | CN | 183 | 133 / 47 / 3 | 94 / 89 | 117 / 66 |
| Female | MCI | 187 | 81 / 79 / 27 | 117 / 70 | 100 / 87 |
| Female | AD | 125 | 46 / 58 / 21 | 72 / 53 | 76 / 49 |
| Male | CN | 181 | 134 / 41 / 6 | 98 / 83 | 91 / 90 |
| Male | MCI | 296 | 142 / 118 / 36 | 221 / 75 | 144 / 152 |
| Male | AD | 158 | 53 / 70 / 35 | 82 / 76 | 75 / 83 |

## Run offset on the primary export

`_phase_offset` of `export` (ADNI1 minus ADNI2GO, pooled within-phase SD; PC correlations of the standardized block with phase) on the primary export's values: all 1501 rows (it must reproduce the export manifest's `counts.phase_offset`) and the arm's rows (the primary's floors).

| block | rows | median abs d | abs d > 0.5 | abs d > 1 | max abs d | PC1 corr | PC2 corr |
|---|---|---|---|---|---|---|---|
| p180 | primary (1501) | 1.121 | 109 | 80 | 2.876 | 0.734 | 0.398 |
| p180 | arm | 1.096 | 107 | 77 | 2.845 | 0.712 | 0.425 |
| p180 | export manifest | 1.121 | 109 | 80 | 2.876 | 0.734 | 0.398 |
| nmr | primary (1501) | 0.208 | 2 | 0 | 0.672 | 0.135 | 0.072 |
| nmr | arm | 0.256 | 2 | 0 | 0.826 | 0.152 | 0.111 |
| nmr | export manifest | 0.208 | 2 | 0 | 0.672 | 0.135 | 0.072 |

## Floors recomputed over the arm (descriptive, for the floor decision)

Per kept metabolite, the floor of `EXPORT_FEATURE_RULE` (5% quantile, linear) over the arm's participants against the primary's floor (`features_<platform>.csv`), and the largest change a recomputed floor would make to a transformed cell, `|log2(x + f_arm) − log2(x + f)|`, over the arm's cells. The arm does not use these floors.

| block | kept | median abs log2(f_arm / f) | max abs log2(f_arm / f) | floors moving > 10 % | median of the largest cell change | largest cell change |
|---|---|---|---|---|---|---|
| p180 | 133 | 0.0569 | 0.5477 | 1 | 0.0353 | 0.4503 |
| nmr | 165 | 0.0117 | 0.7178 | 4 | 0.0083 | 0.6971 |
