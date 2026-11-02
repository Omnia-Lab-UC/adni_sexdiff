# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of the export variant `raw_scale` (`EXPORT_VARIANTS`, change `adni-scale-variants`: the primary's settings on an export whose scale differs; not the primary) covariate-adjusted trajectory analysis (`results/motco_export_sensitivity/raw_scale/analysis`, cv-selected rank 7, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of this export variant (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_0 | 7.207 | `phase` | covariates.csv | 1501 | -0.530 | n/a | raw |
| pls_3 | 3.275 | `phase` | covariates.csv | 1501 | -0.464 | n/a | raw |
| pls_5 | 3.381 | `phase` | covariates.csv | 1501 | -0.431 | n/a | raw |
| pls_1 | 3.849 | `male` | metadata.csv | 1501 | -0.391 | -0.377 | raw+partial |
| pls_0 | 7.207 | `statin` | covariates.csv | 1501 | -0.307 | n/a | raw |

Block principal components (by |rho|):

| block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| p180 | pc1 | 0.407 | `phase` | covariates.csv | 1501 | -0.755 | n/a | raw |
| p180 | pc2 | 0.070 | `phase` | covariates.csv | 1501 | -0.406 | n/a | raw |
| p180 | pc2 | 0.070 | `male` | metadata.csv | 1501 | 0.374 | 0.374 | raw+partial |
| nmr | pc2 | 0.246 | `male` | metadata.csv | 1501 | -0.371 | -0.358 | raw+partial |
| p180 | pc1 | 0.407 | `male` | metadata.csv | 1501 | -0.191 | -0.345 | partial |

## Components

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 7.207 | 0.567 | 0.433 | 2 | 0 | `phase` | -0.530 |
| pls_1 | 3.849 | 0.644 | 0.356 | 1 | 1 | `male` | -0.391 |
| pls_2 | 5.692 | 0.512 | 0.488 | 0 | 0 | `male` | 0.253 |
| pls_3 | 3.275 | 0.747 | 0.253 | 1 | 0 | `phase` | -0.464 |
| pls_4 | 2.074 | 0.691 | 0.309 | 0 | 0 | `male` | -0.243 |
| pls_5 | 3.381 | 0.553 | 0.447 | 1 | 0 | `phase` | -0.431 |
| pls_6 | 2.178 | 0.716 | 0.284 | 0 | 0 | `phase` | 0.090 |

## Correlations of the latent components

Component score SD: pls_0 7.207, pls_1 3.849, pls_2 5.692, pls_3 3.275, pls_4 2.074, pls_5 3.381, pls_6 2.178. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design | pls_4 rho | pls_4 rho \| design | pls_5 rho | pls_5 rho \| design | pls_6 rho | pls_6 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1501 | 0.057 | n/a | -0.190 | n/a | -0.096 | n/a | 0.060 | n/a | -0.026 | n/a | 0.142 | n/a | 0.048 | n/a |
| `education` | covariates.csv | 1501 | -0.112 | n/a | 0.081 | n/a | -0.009 | n/a | 0.095 | n/a | -0.012 | n/a | -0.121 | n/a | 0.062 | n/a |
| `apoe4` | covariates.csv | 1501 | 0.051 | n/a | -0.099 | n/a | -0.057 | n/a | -0.113 | n/a | -0.094 | n/a | -0.068 | n/a | -0.069 | n/a |
| `phase` | covariates.csv | 1501 | -0.530* | n/a | 0.271 | n/a | 0.149 | n/a | -0.464* | n/a | 0.179 | n/a | -0.431* | n/a | 0.090 | n/a |
| `statin` | covariates.csv | 1501 | -0.307* | n/a | -0.009 | n/a | 0.088 | n/a | -0.003 | n/a | -0.226 | n/a | 0.296 | n/a | -0.012 | n/a |
| `stage` | metadata.csv | 1501 | 0.113 | 0.079 | -0.178 | -0.125 | -0.062 | -0.032 | -0.152 | -0.163 | -0.175 | -0.155 | 0.000 | -0.019 | -0.058 | -0.023 |
| `male` | metadata.csv | 1501 | -0.168 | -0.196 | -0.391* | -0.377* | 0.253 | 0.271 | 0.186 | 0.157 | -0.243 | -0.203 | -0.086 | -0.163 | 0.047 | 0.041 |
| `dx_bl` | cohort.csv | 1501 | 0.166 | 0.074 | -0.212 | -0.129 | -0.103 | -0.060 | -0.092 | -0.156 | -0.177 | -0.135 | 0.047 | -0.024 | -0.069 | -0.023 |

`*` marks |rho| ≥ 0.3.

## Block principal components

### p180 (133 features; variance share pc1 0.407, pc2 0.070, pc3 0.059; pc1 against `phase`: Spearman -0.755 here, |Pearson| 0.723 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | 0.123 | n/a | 0.090 | n/a | 0.169 | n/a |
| `education` | 1501 | -0.081 | n/a | -0.064 | n/a | -0.026 | n/a |
| `apoe4` | 1501 | 0.009 | n/a | -0.021 | n/a | 0.022 | n/a |
| `phase` | 1501 | -0.755* | n/a | -0.406* | n/a | 0.037 | n/a |
| `statin` | 1501 | -0.188 | n/a | 0.255 | n/a | 0.079 | n/a |
| `stage` | 1501 | 0.069 | 0.025 | 0.009 | -0.014 | 0.060 | 0.048 |
| `male` | 1501 | -0.191 | -0.345* | 0.374* | 0.374* | 0.209 | 0.191 |
| `dx_bl` | 1501 | 0.156 | 0.031 | 0.042 | -0.032 | 0.064 | 0.054 |

### nmr (165 features; variance share pc1 0.436, pc2 0.246, pc3 0.095; pc1 against `phase`: Spearman -0.128 here, |Pearson| 0.133 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | -0.073 | n/a | -0.047 | n/a | 0.036 | n/a |
| `education` | 1501 | -0.089 | n/a | 0.046 | n/a | -0.015 | n/a |
| `apoe4` | 1501 | 0.021 | n/a | 0.036 | n/a | -0.087 | n/a |
| `phase` | 1501 | -0.128 | n/a | 0.063 | n/a | 0.074 | n/a |
| `statin` | 1501 | -0.259 | n/a | -0.239 | n/a | 0.223 | n/a |
| `stage` | 1501 | 0.044 | 0.030 | -0.009 | -0.011 | -0.045 | -0.015 |
| `male` | 1501 | -0.194 | -0.151 | -0.371* | -0.358* | -0.234 | -0.259 |
| `dx_bl` | 1501 | 0.043 | 0.017 | 0.003 | 0.011 | -0.056 | -0.019 |

## Geometry shares

Share of the squared length of each vector of the trajectory geometry (from `stage_means.csv`) that lies along each component: each sex's net displacement (last stage minus first, what `angle` reads), the per-stage sex-difference vectors (Female minus Male) and the stage-centred ones. `value` is the signed component of a single vector (the net displacements), empty for the summed quantities.

| quantity | component | value | along | total | share |
|---|---|---:|---:|---:|---:|
| net_displacement_Female | pls_0 | 2.081 | 4.331 | 13.25 | 0.327 |
| net_displacement_Female | pls_1 | -1.069 | 1.143 | 13.25 | 0.086 |
| net_displacement_Female | pls_2 | -1.475 | 2.175 | 13.25 | 0.164 |
| net_displacement_Female | pls_3 | -2.208 | 4.877 | 13.25 | 0.368 |
| net_displacement_Female | pls_4 | -0.7963 | 0.634 | 13.25 | 0.048 |
| net_displacement_Female | pls_5 | 0.0997 | 0.009939 | 13.25 | 0.001 |
| net_displacement_Female | pls_6 | -0.2827 | 0.07992 | 13.25 | 0.006 |
| net_displacement_Male | pls_0 | 0.8977 | 0.8059 | 6.217 | 0.130 |
| net_displacement_Male | pls_1 | -1.322 | 1.749 | 6.217 | 0.281 |
| net_displacement_Male | pls_2 | -1.258 | 1.584 | 6.217 | 0.255 |
| net_displacement_Male | pls_3 | -1.174 | 1.378 | 6.217 | 0.222 |
| net_displacement_Male | pls_4 | -0.6942 | 0.4819 | 6.217 | 0.078 |
| net_displacement_Male | pls_5 | 0.04033 | 0.001627 | 6.217 | 0.000 |
| net_displacement_Male | pls_6 | -0.4652 | 0.2164 | 6.217 | 0.035 |
| sex_difference_by_stage | pls_0 | n/a | 21.29 | 93.79 | 0.227 |
| sex_difference_by_stage | pls_1 | n/a | 26.47 | 93.79 | 0.282 |
| sex_difference_by_stage | pls_2 | n/a | 36.85 | 93.79 | 0.393 |
| sex_difference_by_stage | pls_3 | n/a | 3.966 | 93.79 | 0.042 |
| sex_difference_by_stage | pls_4 | n/a | 1.987 | 93.79 | 0.021 |
| sex_difference_by_stage | pls_5 | n/a | 2.927 | 93.79 | 0.031 |
| sex_difference_by_stage | pls_6 | n/a | 0.2891 | 93.79 | 0.003 |
| sex_difference_centred | pls_0 | n/a | 0.7143 | 1.998 | 0.358 |
| sex_difference_centred | pls_1 | n/a | 0.1675 | 1.998 | 0.084 |
| sex_difference_centred | pls_2 | n/a | 0.2371 | 1.998 | 0.119 |
| sex_difference_centred | pls_3 | n/a | 0.5474 | 1.998 | 0.274 |
| sex_difference_centred | pls_4 | n/a | 0.0079 | 1.998 | 0.004 |
| sex_difference_centred | pls_5 | n/a | 0.03628 | 1.998 | 0.018 |
| sex_difference_centred | pls_6 | n/a | 0.2873 | 1.998 | 0.144 |

## Analysis read

- directory: `results/motco_export_sensitivity/raw_scale/analysis`
- rank: 7 (`cv`)
- latent adjustment: none
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- export variant: `raw_scale` (`EXPORT_VARIANTS`): a component of the variant that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics and is never grounds to adopt the variant (scale rule 7)

## Findings

- pls_0: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.53; partial n/a), statin (-0.31; partial n/a)
- pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.39; partial -0.38)
- pls_3: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.46; partial n/a)
- pls_5: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.43; partial n/a)
- the analysis read is not the primary (directory results/motco_export_sensitivity/raw_scale/analysis, latent adjustment None, export variant 'raw_scale'): the primary's rank and the row counts are not expected; the rank-independent counts are

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
