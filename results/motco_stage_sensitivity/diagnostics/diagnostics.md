# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of the CN / LMCI / AD arm `cn_lmci_ad` (`STAGE_SENSITIVITY_ARM`, change `adni-stage-sensitivity`: the primary's settings on the primary export's rows of the participants whose `DX.bl` is CN, LMCI or AD; not the primary) covariate-adjusted trajectory analysis (`results/motco_stage_sensitivity/analysis`, cv-selected rank 6, n = 1130): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of this arm (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_0 | 7.304 | `phase` | covariates.csv | 1130 | -0.728 | n/a | raw |
| pls_1 | 5.806 | `male` | metadata.csv | 1130 | -0.470 | -0.455 | raw+partial |
| pls_1 | 5.806 | `phase` | covariates.csv | 1130 | 0.458 | n/a | raw |
| pls_4 | 4.079 | `statin` | covariates.csv | 1130 | 0.308 | n/a | raw |

Block principal components (by |rho|):

| block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| p180 | pc1 | 0.410 | `phase` | covariates.csv | 1130 | -0.732 | n/a | raw |
| p180 | pc2 | 0.074 | `phase` | covariates.csv | 1130 | -0.430 | n/a | raw |
| p180 | pc2 | 0.074 | `male` | metadata.csv | 1130 | 0.392 | 0.395 | raw+partial |
| nmr | pc2 | 0.247 | `male` | metadata.csv | 1130 | -0.387 | -0.373 | raw+partial |
| p180 | pc1 | 0.410 | `male` | metadata.csv | 1130 | -0.206 | -0.362 | partial |

## Components

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 7.304 | 0.780 | 0.220 | 1 | 0 | `phase` | -0.728 |
| pls_1 | 5.806 | 0.495 | 0.505 | 2 | 1 | `male` | -0.470 |
| pls_2 | 2.996 | 0.671 | 0.329 | 0 | 0 | `statin` | 0.234 |
| pls_3 | 4.018 | 0.648 | 0.352 | 0 | 0 | `male` | 0.245 |
| pls_4 | 4.079 | 0.684 | 0.316 | 1 | 0 | `statin` | 0.308 |
| pls_5 | 2.262 | 0.644 | 0.356 | 0 | 0 | `stage` | -0.183 |

## Correlations of the latent components

Component score SD: pls_0 7.304, pls_1 5.806, pls_2 2.996, pls_3 4.018, pls_4 4.079, pls_5 2.262. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design | pls_4 rho | pls_4 rho \| design | pls_5 rho | pls_5 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1130 | 0.065 | n/a | -0.161 | n/a | -0.012 | n/a | -0.090 | n/a | 0.042 | n/a | 0.105 | n/a |
| `education` | covariates.csv | 1130 | -0.116 | n/a | -0.008 | n/a | 0.075 | n/a | 0.027 | n/a | -0.139 | n/a | -0.043 | n/a |
| `apoe4` | covariates.csv | 1130 | 0.015 | n/a | 0.005 | n/a | -0.171 | n/a | -0.084 | n/a | 0.076 | n/a | -0.165 | n/a |
| `phase` | covariates.csv | 1130 | -0.728* | n/a | 0.458* | n/a | -0.228 | n/a | 0.059 | n/a | -0.097 | n/a | 0.015 | n/a |
| `statin` | covariates.csv | 1130 | -0.229 | n/a | -0.162 | n/a | 0.234 | n/a | 0.030 | n/a | 0.308* | n/a | -0.058 | n/a |
| `stage` | metadata.csv | 1130 | 0.065 | 0.060 | -0.045 | -0.047 | -0.213 | -0.178 | -0.152 | -0.124 | 0.182 | 0.143 | -0.183 | -0.147 |
| `male` | metadata.csv | 1130 | -0.093 | -0.165 | -0.470* | -0.455* | -0.102 | -0.162 | 0.245 | 0.252 | 0.064 | 0.043 | -0.173 | -0.170 |
| `dx_bl` | cohort.csv | 1130 | 0.065 | 0.073 | -0.045 | -0.045 | -0.213 | -0.184 | -0.152 | -0.119 | 0.182 | 0.134 | -0.183 | -0.141 |

`*` marks |rho| ≥ 0.3.

## Block principal components

### p180 (133 features; variance share pc1 0.410, pc2 0.074, pc3 0.061; pc1 against `phase`: Spearman -0.732 here, |Pearson| 0.712 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1130 | 0.078 | n/a | 0.075 | n/a | 0.171 | n/a |
| `education` | 1130 | -0.086 | n/a | -0.049 | n/a | -0.052 | n/a |
| `apoe4` | 1130 | -0.023 | n/a | -0.024 | n/a | 0.031 | n/a |
| `phase` | 1130 | -0.732* | n/a | -0.430* | n/a | 0.018 | n/a |
| `statin` | 1130 | -0.199 | n/a | 0.273 | n/a | 0.081 | n/a |
| `stage` | 1130 | 0.034 | 0.024 | -0.021 | -0.028 | 0.072 | 0.050 |
| `male` | 1130 | -0.206 | -0.362* | 0.392* | 0.395* | 0.200 | 0.185 |
| `dx_bl` | 1130 | 0.034 | 0.031 | -0.021 | -0.030 | 0.072 | 0.056 |

### nmr (165 features; variance share pc1 0.438, pc2 0.247, pc3 0.087; pc1 against `phase`: Spearman -0.146 here, |Pearson| 0.152 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1130 | -0.079 | n/a | -0.028 | n/a | 0.041 | n/a |
| `education` | 1130 | -0.094 | n/a | 0.051 | n/a | -0.023 | n/a |
| `apoe4` | 1130 | 0.040 | n/a | 0.022 | n/a | -0.097 | n/a |
| `phase` | 1130 | -0.146 | n/a | 0.112 | n/a | 0.068 | n/a |
| `statin` | 1130 | -0.246 | n/a | -0.252 | n/a | 0.238 | n/a |
| `stage` | 1130 | 0.032 | 0.014 | 0.002 | 0.003 | -0.044 | -0.020 |
| `male` | 1130 | -0.197 | -0.162 | -0.387* | -0.373* | -0.238 | -0.268 |
| `dx_bl` | 1130 | 0.032 | 0.022 | 0.002 | 0.008 | -0.044 | -0.025 |

## Geometry shares

Share of the squared length of each vector of the trajectory geometry (from `stage_means.csv`) that lies along each component: each sex's net displacement (last stage minus first, what `angle` reads), the per-stage sex-difference vectors (Female minus Male) and the stage-centred ones. `value` is the signed component of a single vector (the net displacements), empty for the summed quantities.

| quantity | component | value | along | total | share |
|---|---|---:|---:|---:|---:|
| net_displacement_Female | pls_0 | 1.191 | 1.418 | 11.99 | 0.118 |
| net_displacement_Female | pls_1 | 0.4526 | 0.2049 | 11.99 | 0.017 |
| net_displacement_Female | pls_2 | -1.525 | 2.326 | 11.99 | 0.194 |
| net_displacement_Female | pls_3 | -1.913 | 3.658 | 11.99 | 0.305 |
| net_displacement_Female | pls_4 | 1.891 | 3.575 | 11.99 | 0.298 |
| net_displacement_Female | pls_5 | -0.9003 | 0.8105 | 11.99 | 0.068 |
| net_displacement_Male | pls_0 | 0.6196 | 0.3839 | 7.043 | 0.055 |
| net_displacement_Male | pls_1 | -0.5401 | 0.2917 | 7.043 | 0.041 |
| net_displacement_Male | pls_2 | -1.186 | 1.406 | 7.043 | 0.200 |
| net_displacement_Male | pls_3 | -1.559 | 2.43 | 7.043 | 0.345 |
| net_displacement_Male | pls_4 | 1.35 | 1.822 | 7.043 | 0.259 |
| net_displacement_Male | pls_5 | -0.8424 | 0.7097 | 7.043 | 0.101 |
| sex_difference_by_stage | pls_0 | n/a | 9.326 | 108.1 | 0.086 |
| sex_difference_by_stage | pls_1 | n/a | 75.62 | 108.1 | 0.700 |
| sex_difference_by_stage | pls_2 | n/a | 2.542 | 108.1 | 0.024 |
| sex_difference_by_stage | pls_3 | n/a | 17.96 | 108.1 | 0.166 |
| sex_difference_by_stage | pls_4 | n/a | 0.5542 | 108.1 | 0.005 |
| sex_difference_by_stage | pls_5 | n/a | 2.103 | 108.1 | 0.019 |
| sex_difference_centred | pls_0 | n/a | 0.1935 | 1.387 | 0.139 |
| sex_difference_centred | pls_1 | n/a | 0.4952 | 1.387 | 0.357 |
| sex_difference_centred | pls_2 | n/a | 0.131 | 1.387 | 0.094 |
| sex_difference_centred | pls_3 | n/a | 0.2438 | 1.387 | 0.176 |
| sex_difference_centred | pls_4 | n/a | 0.1622 | 1.387 | 0.117 |
| sex_difference_centred | pls_5 | n/a | 0.1614 | 1.387 | 0.116 |

## Analysis read

- directory: `results/motco_stage_sensitivity/analysis`
- rank: 6 (`cv`)
- latent adjustment: none
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- CN / LMCI / AD arm: `cn_lmci_ad` (`STAGE_SENSITIVITY_ARM`): a component of the arm that tracks a variable here is a measurement-space finding about the arm and never grounds to adopt it; in the arm `dx_bl` orders the participants as `stage` does, so their correlations coincide (stage-arm rule 7)

## Findings

- pls_0: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.73; partial n/a)
- pls_1: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.47; partial -0.45), phase (0.46; partial n/a)
- pls_4: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): statin (0.31; partial n/a)
- the analysis read is not the primary (directory results/motco_stage_sensitivity/analysis, latent adjustment None, stage arm 'cn_lmci_ad'): the primary's rank and the row counts are not expected; the rank-independent counts are (with the arm's participants and cells, STAGE_SENSITIVITY_EXPECTED_COUNTS)

## Reading rules

Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):

1. The primary result is the covariate-adjusted analysis on the covariate-blind basis with the five covariates; every sensitivity (latent adjustment, export variants, the CN / LMCI / AD arm, a rank sweep) is read beside it, and a rejection status that differs in an arm is dependence on that arm's setting, never a replacement of the primary.
2. The CV-selected rank, the rank floor, the record's `config_spectrum` eigengap and the `angle` null summary are reported beside `angle`. The floor defines `angle` and `shape` in at least two dimensions; it does not make them powerful.
3. `angle` and `shape` non-rejections are uninformative: MOTCO's operating characteristics were measured at n = 80 on a structural analogue (InterSIM blocks, 498 features), and no power statement exists at this design (n = 1501, 298 metabolites, six design columns). `angle` reads only the endpoint stages (CN and AD). A rejection is evidence that the trajectories differ in that respect, with Type I controlled at the validated designs.
4. A `delta` rejection is evidence of a difference between the sexes' trajectories, not specifically of a difference in size.
5. The covariate block of the record (design columns, reference row, missing policy, dropped participants) is reported beside the results. The adjustment is additive and linear on a covariate-blind basis, validated at three design columns and n = 80, and has no sex × covariate or stage × covariate term: the run offset is assumed equal in both sexes and across stages.
6. The p180 run offset (export manifest `counts.phase_offset`: median |d| 1.12, 80 of 133 metabolites above 1, PC1 correlation 0.73 with phase; NMR 0.21, 0, 0.13) and the block shares (p180 133 / 298, unweighted in MOTCO 0.10.0) are reported beside the results. A latent component that tracks phase is a reading matter for `axis-diagnostics` and the latent-adjusted arm, not an adjustment of the primary.
7. Feature membership and scale (`EXPORT_FEATURE_RULE`: 165 of 245 NMR columns, the floored log2, nothing imputed, winsorized or removed) are reported beside the results.
8. Reported runs use `n_jobs = 1`; a run at another value carries a finding and is not reported. Report numbers are pasted from the generated files and checked by `report --check`.
9. No result changes a constant. The analysis is run once at these settings; a second run at other settings is a new proposal.

## Reading rules of the CN / LMCI / AD arm

Binding for every reader of the CN / LMCI / AD arm (`STAGE_SENSITIVITY_READING_RULES`, decided by `adni-stage-sensitivity` before any run), after `READING_RULES`:

1. The arm is read beside the primary and never replaces it. No arm result changes a constant, `STAGE_RULE` or `COHORT_RULE`, reruns the primary or adopts the arm.
2. The arm's rows are the primary export's rows of the 1130 participants whose `DX.bl` is CN, LMCI or AD, with the cells unchanged (the primary's floors). The covariates, their coding and every analysis setting are the primary's. It differs in the participants: the 96 SMC and 275 EMCI participants, enrolled only in ADNI-GO/2, are dropped. Its CN is `DX.bl` CN and its MCI is LMCI. Its z-scoring, CV folds, latent basis, rank, covariate reference row and permutation draws are its own. A rejection status that differs is dependence on the stage definition and the sample, not a result of the arm.
3. The arm's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
4. In the arm each stage holds one `DX.bl` category in both runs, so the `phase` coefficient of the stage-means model is estimated from contrasts within one diagnosis. In the primary, the ADNI-GO/2 rows of CN and MCI add SMC and EMCI. The arm neither balances the runs across stages nor removes the run offset, which is measurement: the ADNI-1 share per stage is CN 0.527, MCI 0.700, AD 0.544 in the arm and 0.417, 0.446, 0.544 in the primary; the p180 median |d| is 1.10 on the arm's rows and 1.12 on the primary's, and PC1's correlation with phase 0.71 and 0.73. `phase` stays a covariate under the additive assumption of reading rule 5.
5. The arm's MCI (LMCI) is a later and narrower stage than the primary's MCI, and its CN excludes subjective memory concern. A difference that involves the middle stage is a difference of stage definition. `angle` reads only the endpoint stages: the arm's AD cells are the primary's, and its CN cells lose the SMC participants.
6. The arm holds 1130 of the 1501 participants. Its non-rejection is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in the arm is dependence on the stage definition and the sample, read beside its rank and null summary.
7. The arm's export manifest records its cells, the runs within each stage and the run offset on its rows, and they are reported beside the results with the primary's. A component of the arm that tracks a variable in its axis diagnostic is a measurement-space finding about the arm and never grounds to adopt it. In the arm, `dx_bl` orders the participants as `stage` does, so their correlations coincide.
8. The arm is not crossed with the latent adjustment or an export variant, and is read against the primary only. No sentence reads it against another sensitivity.
