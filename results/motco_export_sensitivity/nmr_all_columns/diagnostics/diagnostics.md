# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of the export variant `nmr_all_columns` (`EXPORT_VARIANTS`, change `adni-nmr-all-columns`: the primary's settings on an export whose NMR block membership differs; not the primary) covariate-adjusted trajectory analysis (`results/motco_export_sensitivity/nmr_all_columns/analysis`, cv-selected rank 7, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of this export variant (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_4 | 3.445 | `phase` | covariates.csv | 1501 | -0.565 | n/a | raw |
| pls_0 | 7.534 | `phase` | covariates.csv | 1501 | 0.516 | n/a | raw |
| pls_1 | 4.326 | `male` | metadata.csv | 1501 | -0.422 | -0.407 | raw+partial |
| pls_0 | 7.534 | `statin` | covariates.csv | 1501 | 0.335 | n/a | raw |
| pls_5 | 3.045 | `phase` | covariates.csv | 1501 | 0.303 | n/a | raw |

Block principal components (by |rho|):

| block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| p180 | pc1 | 0.418 | `phase` | covariates.csv | 1501 | -0.757 | n/a | raw |
| p180 | pc2 | 0.071 | `phase` | covariates.csv | 1501 | -0.400 | n/a | raw |
| p180 | pc2 | 0.071 | `male` | metadata.csv | 1501 | 0.390 | 0.391 | raw+partial |
| nmr | pc2 | 0.264 | `statin` | covariates.csv | 1501 | -0.387 | n/a | raw |
| nmr | pc3 | 0.113 | `male` | metadata.csv | 1501 | -0.336 | -0.348 | raw+partial |
| nmr | pc2 | 0.264 | `male` | metadata.csv | 1501 | -0.325 | -0.306 | raw+partial |
| p180 | pc1 | 0.418 | `male` | metadata.csv | 1501 | -0.190 | -0.347 | partial |

## Components

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 7.534 | 0.464 | 0.536 | 2 | 0 | `phase` | 0.516 |
| pls_1 | 4.326 | 0.530 | 0.470 | 1 | 1 | `male` | -0.422 |
| pls_2 | 5.655 | 0.503 | 0.497 | 0 | 0 | `male` | 0.212 |
| pls_3 | 4.726 | 0.550 | 0.450 | 0 | 0 | `statin` | -0.198 |
| pls_4 | 3.445 | 0.622 | 0.378 | 1 | 0 | `phase` | -0.565 |
| pls_5 | 3.045 | 0.605 | 0.395 | 1 | 0 | `phase` | 0.303 |
| pls_6 | 2.377 | 0.465 | 0.535 | 0 | 0 | `phase` | 0.264 |

## Correlations of the latent components

Component score SD: pls_0 7.534, pls_1 4.326, pls_2 5.655, pls_3 4.726, pls_4 3.445, pls_5 3.045, pls_6 2.377. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design | pls_4 rho | pls_4 rho \| design | pls_5 rho | pls_5 rho \| design | pls_6 rho | pls_6 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1501 | -0.050 | n/a | -0.167 | n/a | -0.126 | n/a | -0.088 | n/a | 0.154 | n/a | -0.070 | n/a | 0.014 | n/a |
| `education` | covariates.csv | 1501 | 0.115 | n/a | 0.079 | n/a | 0.002 | n/a | 0.132 | n/a | -0.006 | n/a | -0.002 | n/a | 0.041 | n/a |
| `apoe4` | covariates.csv | 1501 | -0.058 | n/a | -0.096 | n/a | -0.083 | n/a | -0.062 | n/a | -0.152 | n/a | -0.055 | n/a | -0.075 | n/a |
| `phase` | covariates.csv | 1501 | 0.516* | n/a | 0.216 | n/a | 0.181 | n/a | -0.039 | n/a | -0.565* | n/a | 0.303* | n/a | 0.264 | n/a |
| `statin` | covariates.csv | 1501 | 0.335* | n/a | -0.040 | n/a | 0.075 | n/a | -0.198 | n/a | 0.097 | n/a | -0.261 | n/a | -0.194 | n/a |
| `stage` | metadata.csv | 1501 | -0.122 | -0.091 | -0.171 | -0.120 | -0.101 | -0.063 | -0.158 | -0.133 | -0.143 | -0.176 | -0.150 | -0.139 | -0.042 | -0.001 |
| `male` | metadata.csv | 1501 | 0.138 | 0.155 | -0.422* | -0.407* | 0.212 | 0.237 | 0.091 | 0.098 | 0.042 | -0.022 | -0.211 | -0.171 | 0.005 | 0.044 |
| `dx_bl` | cohort.csv | 1501 | -0.174 | -0.086 | -0.197 | -0.121 | -0.147 | -0.090 | -0.144 | -0.122 | -0.068 | -0.168 | -0.159 | -0.111 | -0.079 | -0.001 |

`*` marks |rho| ≥ 0.3.

## Block principal components

### p180 (133 features; variance share pc1 0.418, pc2 0.071, pc3 0.060; pc1 against `phase`: Spearman -0.757 here, |Pearson| 0.734 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | 0.124 | n/a | 0.087 | n/a | 0.175 | n/a |
| `education` | 1501 | -0.082 | n/a | -0.058 | n/a | -0.029 | n/a |
| `apoe4` | 1501 | 0.010 | n/a | -0.023 | n/a | 0.021 | n/a |
| `phase` | 1501 | -0.757* | n/a | -0.400* | n/a | 0.023 | n/a |
| `statin` | 1501 | -0.187 | n/a | 0.258 | n/a | 0.086 | n/a |
| `stage` | 1501 | 0.071 | 0.025 | 0.008 | -0.012 | 0.056 | 0.043 |
| `male` | 1501 | -0.190 | -0.347* | 0.390* | 0.391* | 0.208 | 0.186 |
| `dx_bl` | 1501 | 0.159 | 0.032 | 0.042 | -0.029 | 0.062 | 0.049 |

### nmr (245 features; variance share pc1 0.335, pc2 0.264, pc3 0.113; pc1 against `phase`: Spearman -0.147 here, |Pearson| 0.148 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | -0.053 | n/a | -0.067 | n/a | 0.021 | n/a |
| `education` | 1501 | -0.104 | n/a | 0.013 | n/a | 0.003 | n/a |
| `apoe4` | 1501 | 0.003 | n/a | 0.055 | n/a | -0.061 | n/a |
| `phase` | 1501 | -0.147 | n/a | -0.019 | n/a | 0.127 | n/a |
| `statin` | 1501 | -0.162 | n/a | -0.387* | n/a | 0.128 | n/a |
| `stage` | 1501 | 0.042 | 0.030 | 0.021 | 0.005 | -0.050 | -0.024 |
| `male` | 1501 | -0.087 | -0.052 | -0.325* | -0.306* | -0.336* | -0.348* |
| `dx_bl` | 1501 | 0.039 | 0.011 | 0.036 | 0.024 | -0.061 | -0.021 |

## Geometry shares

Share of the squared length of each vector of the trajectory geometry (from `stage_means.csv`) that lies along each component: each sex's net displacement (last stage minus first, what `angle` reads), the per-stage sex-difference vectors (Female minus Male) and the stage-centred ones. `value` is the signed component of a single vector (the net displacements), empty for the summed quantities.

| quantity | component | value | along | total | share |
|---|---|---:|---:|---:|---:|
| net_displacement_Female | pls_0 | -2.172 | 4.719 | 20.96 | 0.225 |
| net_displacement_Female | pls_1 | -1.139 | 1.296 | 20.96 | 0.062 |
| net_displacement_Female | pls_2 | -1.988 | 3.951 | 20.96 | 0.189 |
| net_displacement_Female | pls_3 | -2.638 | 6.957 | 20.96 | 0.332 |
| net_displacement_Female | pls_4 | -1.781 | 3.173 | 20.96 | 0.151 |
| net_displacement_Female | pls_5 | -0.9292 | 0.8634 | 20.96 | 0.041 |
| net_displacement_Female | pls_6 | 0.01556 | 0.000242 | 20.96 | 0.000 |
| net_displacement_Male | pls_0 | -1.238 | 1.534 | 11.77 | 0.130 |
| net_displacement_Male | pls_1 | -1.459 | 2.129 | 11.77 | 0.181 |
| net_displacement_Male | pls_2 | -1.608 | 2.586 | 11.77 | 0.220 |
| net_displacement_Male | pls_3 | -1.692 | 2.862 | 11.77 | 0.243 |
| net_displacement_Male | pls_4 | -1.267 | 1.606 | 11.77 | 0.136 |
| net_displacement_Male | pls_5 | -0.9086 | 0.8256 | 11.77 | 0.070 |
| net_displacement_Male | pls_6 | -0.4808 | 0.2312 | 11.77 | 0.020 |
| sex_difference_by_stage | pls_0 | n/a | 13.21 | 90.44 | 0.146 |
| sex_difference_by_stage | pls_1 | n/a | 40.64 | 90.44 | 0.449 |
| sex_difference_by_stage | pls_2 | n/a | 28.93 | 90.44 | 0.320 |
| sex_difference_by_stage | pls_3 | n/a | 4.688 | 90.44 | 0.052 |
| sex_difference_by_stage | pls_4 | n/a | 0.2656 | 90.44 | 0.003 |
| sex_difference_by_stage | pls_5 | n/a | 2.455 | 90.44 | 0.027 |
| sex_difference_by_stage | pls_6 | n/a | 0.2498 | 90.44 | 0.003 |
| sex_difference_centred | pls_0 | n/a | 0.5468 | 2.275 | 0.240 |
| sex_difference_centred | pls_1 | n/a | 0.1915 | 2.275 | 0.084 |
| sex_difference_centred | pls_2 | n/a | 0.4668 | 2.275 | 0.205 |
| sex_difference_centred | pls_3 | n/a | 0.5566 | 2.275 | 0.245 |
| sex_difference_centred | pls_4 | n/a | 0.2627 | 2.275 | 0.115 |
| sex_difference_centred | pls_5 | n/a | 0.005868 | 2.275 | 0.003 |
| sex_difference_centred | pls_6 | n/a | 0.2451 | 2.275 | 0.108 |

## Analysis read

- directory: `results/motco_export_sensitivity/nmr_all_columns/analysis`
- rank: 7 (`cv`)
- latent adjustment: none
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- export variant: `nmr_all_columns` (`EXPORT_VARIANTS`): a component of the variant that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics and is never grounds to adopt the variant (membership rule 7)

## Findings

- pls_0: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (0.52; partial n/a), statin (0.34; partial n/a)
- pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.42; partial -0.41)
- pls_4: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.56; partial n/a)
- pls_5: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (0.30; partial n/a)
- the analysis read is not the primary (directory results/motco_export_sensitivity/nmr_all_columns/analysis, latent adjustment None, export variant 'nmr_all_columns'): the primary's rank and the row counts are not expected; the rank-independent counts are (with the variant's block features, EXPORT_VARIANT_EXPECTED_COUNTS)

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

## Reading rules of the NMR membership variant

Binding for every reader of the NMR membership variant (`NMR_MEMBERSHIP_READING_RULES`, decided by `adni-nmr-all-columns` before any run), after `READING_RULES`:

1. `nmr_all_columns` is read beside the primary and never replaces it. No result of it changes a constant (`EXPORT_FEATURE_RULE` included), reruns the primary or adopts the variant.
2. The variant shares a great deal with the primary: the cleaned tables, the participants, the p180 block, the 165 NMR concentrations with their floors and cells, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the NMR block's membership. It adds the 80 columns `EXPORT_FEATURE_RULE` marks `derived`, so the joint matrix holds 378 features, and the p180 share falls from 133 / 298 (0.446) to 133 / 378 (0.352). A rejection status that differs is dependence on the feature membership, not a result of the variant.
3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
4. The 80 columns add no measurement. Each is a function of the block's concentrations: a lipid's share of its lipoprotein subclass (72 percentages), a ratio (4), the degree of unsaturation, or a particle size (3). On the rule's scale the 165 concentrations explain a median 0.998 of a derived column's variance (lowest 0.798). MOTCO z-scores every feature and weights features, not blocks, so the columns add weight to the lipoprotein directions they are computed from. On the rule's scale, 21 of them have |skew| > 1 and 8 a largest |z| above 8, mostly percentages of the large HDL and VLDL lipids. A difference reflects the weight of those directions and those tails, never evidence that the derived columns measure what the concentrations do not.
5. The 2022 study (doi:10.3389/fradi.2022.782864) used all 245 NMR columns, with `log2(x + 1)`, winsorizing, outlier removal and medication residuals. The variant changes the membership only, on the rule's scale. It is not a reproduction of that study, and no agreement or disagreement with it is read from the variant.
6. A non-rejection in the variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in the variant is dependence on the feature membership, read beside the variant's rank and null summary.
7. The variant's export manifest records the block shares, the NMR block's shape counts and the run offset per block. Its axis diagnostic records each block's loading share per component (`components.csv`). They are reported beside the results. A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.
8. The variant is read against the primary only, never against another export variant, arm or rank. No sentence reads it against another sensitivity.
