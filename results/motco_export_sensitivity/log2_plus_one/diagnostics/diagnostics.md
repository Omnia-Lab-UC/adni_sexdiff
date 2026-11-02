# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of the export variant `log2_plus_one` (`EXPORT_VARIANTS`, change `adni-scale-variants`: the primary's settings on an export whose scale differs; not the primary) covariate-adjusted trajectory analysis (`results/motco_export_sensitivity/log2_plus_one/analysis`, cv-selected rank 8, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of this export variant (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_0 | 7.268 | `phase` | covariates.csv | 1501 | -0.551 | n/a | raw |
| pls_3 | 3.338 | `phase` | covariates.csv | 1501 | -0.492 | n/a | raw |
| pls_1 | 3.916 | `male` | metadata.csv | 1501 | -0.413 | -0.402 | raw+partial |
| pls_4 | 2.315 | `statin` | covariates.csv | 1501 | -0.319 | n/a | raw |
| pls_0 | 7.268 | `statin` | covariates.csv | 1501 | -0.300 | n/a | raw |

Block principal components (by |rho|):

| block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| p180 | pc1 | 0.415 | `phase` | covariates.csv | 1501 | -0.755 | n/a | raw |
| p180 | pc2 | 0.070 | `male` | metadata.csv | 1501 | 0.400 | 0.401 | raw+partial |
| p180 | pc2 | 0.070 | `phase` | covariates.csv | 1501 | -0.394 | n/a | raw |
| nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.374 | -0.361 | raw+partial |
| p180 | pc1 | 0.415 | `male` | metadata.csv | 1501 | -0.190 | -0.346 | partial |

## Components

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 7.268 | 0.597 | 0.403 | 2 | 0 | `phase` | -0.551 |
| pls_1 | 3.916 | 0.647 | 0.353 | 1 | 1 | `male` | -0.413 |
| pls_2 | 5.654 | 0.564 | 0.436 | 0 | 0 | `male` | 0.219 |
| pls_3 | 3.338 | 0.761 | 0.239 | 1 | 0 | `phase` | -0.492 |
| pls_4 | 2.315 | 0.723 | 0.277 | 1 | 0 | `statin` | -0.319 |
| pls_5 | 3.343 | 0.527 | 0.473 | 0 | 0 | `phase` | -0.290 |
| pls_6 | 1.973 | 0.722 | 0.278 | 0 | 0 | `phase` | 0.132 |
| pls_7 | 1.986 | 0.684 | 0.316 | 0 | 0 | `age` | 0.165 |

## Correlations of the latent components

Component score SD: pls_0 7.268, pls_1 3.916, pls_2 5.654, pls_3 3.338, pls_4 2.315, pls_5 3.343, pls_6 1.973, pls_7 1.986. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design | pls_4 rho | pls_4 rho \| design | pls_5 rho | pls_5 rho \| design | pls_6 rho | pls_6 rho \| design | pls_7 rho | pls_7 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1501 | 0.061 | n/a | -0.182 | n/a | -0.099 | n/a | 0.079 | n/a | -0.053 | n/a | 0.136 | n/a | 0.044 | n/a | 0.165 | n/a |
| `education` | covariates.csv | 1501 | -0.113 | n/a | 0.087 | n/a | -0.010 | n/a | 0.091 | n/a | 0.031 | n/a | -0.106 | n/a | 0.069 | n/a | 0.041 | n/a |
| `apoe4` | covariates.csv | 1501 | 0.051 | n/a | -0.097 | n/a | -0.069 | n/a | -0.120 | n/a | -0.074 | n/a | -0.106 | n/a | -0.054 | n/a | 0.033 | n/a |
| `phase` | covariates.csv | 1501 | -0.551* | n/a | 0.266 | n/a | 0.142 | n/a | -0.492* | n/a | 0.288 | n/a | -0.290 | n/a | 0.132 | n/a | 0.006 | n/a |
| `statin` | covariates.csv | 1501 | -0.300* | n/a | -0.029 | n/a | 0.090 | n/a | 0.012 | n/a | -0.319* | n/a | 0.200 | n/a | -0.042 | n/a | -0.064 | n/a |
| `stage` | metadata.csv | 1501 | 0.115 | 0.082 | -0.175 | -0.123 | -0.076 | -0.044 | -0.155 | -0.172 | -0.175 | -0.158 | -0.062 | -0.066 | -0.048 | -0.016 | 0.101 | 0.094 |
| `male` | metadata.csv | 1501 | -0.168 | -0.201 | -0.413* | -0.402* | 0.219 | 0.237 | 0.176 | 0.145 | -0.181 | -0.141 | -0.181 | -0.229 | 0.069 | 0.069 | 0.094 | 0.075 |
| `dx_bl` | cohort.csv | 1501 | 0.171 | 0.078 | -0.207 | -0.126 | -0.117 | -0.072 | -0.090 | -0.164 | -0.187 | -0.135 | -0.024 | -0.062 | -0.065 | -0.017 | 0.106 | 0.096 |

`*` marks |rho| ≥ 0.3.

## Block principal components

### p180 (133 features; variance share pc1 0.415, pc2 0.070, pc3 0.060; pc1 against `phase`: Spearman -0.755 here, |Pearson| 0.731 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | 0.123 | n/a | 0.095 | n/a | 0.170 | n/a |
| `education` | 1501 | -0.081 | n/a | -0.060 | n/a | -0.021 | n/a |
| `apoe4` | 1501 | 0.009 | n/a | -0.022 | n/a | 0.023 | n/a |
| `phase` | 1501 | -0.755* | n/a | -0.394* | n/a | 0.048 | n/a |
| `statin` | 1501 | -0.187 | n/a | 0.261 | n/a | 0.075 | n/a |
| `stage` | 1501 | 0.071 | 0.026 | 0.011 | -0.008 | 0.057 | 0.047 |
| `male` | 1501 | -0.190 | -0.346* | 0.400* | 0.401* | 0.202 | 0.185 |
| `dx_bl` | 1501 | 0.159 | 0.033 | 0.044 | -0.025 | 0.061 | 0.053 |

### nmr (165 features; variance share pc1 0.437, pc2 0.247, pc3 0.093; pc1 against `phase`: Spearman -0.128 here, |Pearson| 0.133 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | -0.073 | n/a | -0.048 | n/a | 0.036 | n/a |
| `education` | 1501 | -0.089 | n/a | 0.046 | n/a | -0.018 | n/a |
| `apoe4` | 1501 | 0.020 | n/a | 0.036 | n/a | -0.090 | n/a |
| `phase` | 1501 | -0.128 | n/a | 0.064 | n/a | 0.073 | n/a |
| `statin` | 1501 | -0.257 | n/a | -0.240 | n/a | 0.227 | n/a |
| `stage` | 1501 | 0.044 | 0.030 | -0.009 | -0.012 | -0.045 | -0.014 |
| `male` | 1501 | -0.192 | -0.149 | -0.374* | -0.361* | -0.238 | -0.264 |
| `dx_bl` | 1501 | 0.043 | 0.017 | 0.002 | 0.011 | -0.056 | -0.019 |

## Geometry shares

Share of the squared length of each vector of the trajectory geometry (from `stage_means.csv`) that lies along each component: each sex's net displacement (last stage minus first, what `angle` reads), the per-stage sex-difference vectors (Female minus Male) and the stage-centred ones. `value` is the signed component of a single vector (the net displacements), empty for the summed quantities.

| quantity | component | value | along | total | share |
|---|---|---:|---:|---:|---:|
| net_displacement_Female | pls_0 | 2.067 | 4.273 | 14.52 | 0.294 |
| net_displacement_Female | pls_1 | -1.024 | 1.049 | 14.52 | 0.072 |
| net_displacement_Female | pls_2 | -1.579 | 2.494 | 14.52 | 0.172 |
| net_displacement_Female | pls_3 | -2.221 | 4.935 | 14.52 | 0.340 |
| net_displacement_Female | pls_4 | -0.939 | 0.8816 | 14.52 | 0.061 |
| net_displacement_Female | pls_5 | -0.3396 | 0.1153 | 14.52 | 0.008 |
| net_displacement_Female | pls_6 | -0.1813 | 0.03285 | 14.52 | 0.002 |
| net_displacement_Female | pls_7 | 0.8621 | 0.7433 | 14.52 | 0.051 |
| net_displacement_Male | pls_0 | 0.9997 | 0.9994 | 7.487 | 0.133 |
| net_displacement_Male | pls_1 | -1.279 | 1.636 | 7.487 | 0.218 |
| net_displacement_Male | pls_2 | -1.443 | 2.083 | 7.487 | 0.278 |
| net_displacement_Male | pls_3 | -1.238 | 1.533 | 7.487 | 0.205 |
| net_displacement_Male | pls_4 | -0.8272 | 0.6842 | 7.487 | 0.091 |
| net_displacement_Male | pls_5 | -0.3768 | 0.1419 | 7.487 | 0.019 |
| net_displacement_Male | pls_6 | -0.4315 | 0.1862 | 7.487 | 0.025 |
| net_displacement_Male | pls_7 | 0.4735 | 0.2242 | 7.487 | 0.030 |
| sex_difference_by_stage | pls_0 | n/a | 21.8 | 92.68 | 0.235 |
| sex_difference_by_stage | pls_1 | n/a | 31.39 | 92.68 | 0.339 |
| sex_difference_by_stage | pls_2 | n/a | 28.18 | 92.68 | 0.304 |
| sex_difference_by_stage | pls_3 | n/a | 3.576 | 92.68 | 0.039 |
| sex_difference_by_stage | pls_4 | n/a | 1.044 | 92.68 | 0.011 |
| sex_difference_by_stage | pls_5 | n/a | 6.142 | 92.68 | 0.066 |
| sex_difference_by_stage | pls_6 | n/a | 0.3012 | 92.68 | 0.003 |
| sex_difference_by_stage | pls_7 | n/a | 0.2408 | 92.68 | 0.003 |
| sex_difference_centred | pls_0 | n/a | 0.5759 | 1.87 | 0.308 |
| sex_difference_centred | pls_1 | n/a | 0.1688 | 1.87 | 0.090 |
| sex_difference_centred | pls_2 | n/a | 0.1832 | 1.87 | 0.098 |
| sex_difference_centred | pls_3 | n/a | 0.4989 | 1.87 | 0.267 |
| sex_difference_centred | pls_4 | n/a | 0.008587 | 1.87 | 0.005 |
| sex_difference_centred | pls_5 | n/a | 0.08489 | 1.87 | 0.045 |
| sex_difference_centred | pls_6 | n/a | 0.2646 | 1.87 | 0.141 |
| sex_difference_centred | pls_7 | n/a | 0.08511 | 1.87 | 0.046 |

## Analysis read

- directory: `results/motco_export_sensitivity/log2_plus_one/analysis`
- rank: 8 (`cv`)
- latent adjustment: none
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- export variant: `log2_plus_one` (`EXPORT_VARIANTS`): a component of the variant that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics and is never grounds to adopt the variant (scale rule 7)

## Findings

- pls_0: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.55; partial n/a), statin (-0.30; partial n/a)
- pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.41; partial -0.40)
- pls_3: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.49; partial n/a)
- pls_4: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): statin (-0.32; partial n/a)
- the analysis read is not the primary (directory results/motco_export_sensitivity/log2_plus_one/analysis, latent adjustment None, export variant 'log2_plus_one'): the primary's rank and the row counts are not expected; the rank-independent counts are

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

## Reading rules of the scale variants

Binding for every reader of a scale variant (`SCALE_VARIANT_READING_RULES`, decided by `adni-scale-variants` before any run), after `READING_RULES`:

1. A scale variant is read beside the primary and never replaces it. No result of a scale variant changes a constant (the scale of `EXPORT_FEATURE_RULE` included), reruns the primary or adopts a variant.
2. A scale variant shares with the primary the cleaned tables, the participants, the membership of both blocks (133 p180 metabolites, 165 NMR concentrations), the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the scale of the cell values of both blocks. Every scale is a monotone function of the concentration, so each participant's rank on each feature is the primary's; what changes is the spacing of the values, which MOTCO's z-scoring passes to the basis and the statistics. A rejection status that differs is dependence on the scale, not a result of the variant.
3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
4. `log2_plus_one` and `glog` keep the log and change its offset. The primary's offset is the metabolite's 5 % quantile (floor over median: p180 median 0.60, NMR 0.65), which compresses the lowest values of every metabolite alike. `log2_plus_one` is the transform of the 2022 study (doi:10.3389/fradi.2022.782864): its offset is 1 in each platform's unit (p180 µM, NMR mostly mmol/L), so an abundant metabolite gets nearly `log2(x)` and a scarce one a nearly linear scale (median below 1: 46 of 133 p180 metabolites, 129 of 165 NMR concentrations). It is not a reproduction of that study, whose membership, winsorizing, outlier removal and medication residuals differ, and no agreement or disagreement with it is read from the variant. `glog` is the generalized log with λ a tenth of the metabolite's smallest positive value: `log2(x)` within 0.004 bits on every positive cell, a zero cell 4.3 bits below the smallest positive value (41 NMR cells in 3 metabolites), and no compression of the low values, so it carries left tails (|skew| > 1 for 6 p180 and 25 NMR metabolites, a largest |z| above 8 for 6 and 13).
5. `raw_scale` takes the cleaned concentrations with no log. MOTCO z-scores each feature, so the right tails of the concentration distributions carry leverage (|skew| > 1 for 46 p180 and 43 NMR metabolites, a largest |z| above 8 for 12 and 4, against 1 and 3, 0 and 1 on the rule's scale), and the NMR block loses numerical rank (104 of 165; the joint matrix 237 of 298): the lipoprotein measures are exact sums of their components on the concentration scale, a relation the log breaks. A difference reflects those tails and that geometry, never evidence that one scale measures what another does not.
6. A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in a variant is dependence on the scale, read beside the variant's rank and null summary.
7. The variant's export manifest records the shape counts of each block on its scale, the numerical rank of each block, the run offset per block and the offset of each metabolite (the feature tables). They are reported beside the results. The run offset barely moves with the scale (p180 median |d| 1.08 to 1.13 against the primary's 1.12). A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.
8. A scale variant is read against the primary only, never against another scale variant, another export variant, an arm or a rank. No sentence reads it against another sensitivity, and a difference between two scale variants is not evidence for either.
