# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of forced rank 12 of the rank sweep `forced_rank_ladder` (`RANK_SENSITIVITY_LADDER`, change `adni-rank-sensitivity`: the primary's analysis with `forced_components` = 12; PLS-DA components are nested, so its components `pls_0` to `pls_7` are the primary's, with the primary's correlations; not the primary) covariate-adjusted trajectory analysis (`results/motco_rank_sensitivity/rank_12`, forced rank 12, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of the rank sweep at rank 12 (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_0 | 7.334 | `phase` | covariates.csv | 1501 | 0.542 | n/a | raw |
| pls_3 | 3.472 | `phase` | covariates.csv | 1501 | -0.535 | n/a | raw |
| pls_1 | 3.901 | `male` | metadata.csv | 1501 | -0.405 | -0.396 | raw+partial |
| pls_4 | 2.54 | `statin` | covariates.csv | 1501 | -0.357 | n/a | raw |
| pls_4 | 2.54 | `phase` | covariates.csv | 1501 | 0.324 | n/a | raw |

Block principal components (by |rho|):

| block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| p180 | pc1 | 0.418 | `phase` | covariates.csv | 1501 | -0.757 | n/a | raw |
| p180 | pc2 | 0.071 | `phase` | covariates.csv | 1501 | -0.400 | n/a | raw |
| p180 | pc2 | 0.071 | `male` | metadata.csv | 1501 | 0.390 | 0.391 | raw+partial |
| nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.383 | -0.371 | raw+partial |
| p180 | pc1 | 0.418 | `male` | metadata.csv | 1501 | -0.190 | -0.347 | partial |

## Components

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 7.334 | 0.567 | 0.433 | 1 | 0 | `phase` | 0.542 |
| pls_1 | 3.901 | 0.635 | 0.365 | 1 | 1 | `male` | -0.405 |
| pls_2 | 5.566 | 0.599 | 0.401 | 0 | 0 | `male` | -0.219 |
| pls_3 | 3.472 | 0.739 | 0.261 | 1 | 0 | `phase` | -0.535 |
| pls_4 | 2.54 | 0.701 | 0.299 | 2 | 0 | `statin` | -0.357 |
| pls_5 | 2.944 | 0.558 | 0.442 | 0 | 0 | `male` | -0.253 |
| pls_6 | 1.906 | 0.685 | 0.315 | 0 | 0 | `phase` | 0.130 |
| pls_7 | 1.995 | 0.665 | 0.335 | 0 | 0 | `age` | 0.188 |
| pls_8 | 1.444 | 0.800 | 0.200 | 0 | 0 | `stage` | -0.127 |
| pls_9 | 1.873 | 0.723 | 0.277 | 0 | 0 | `statin` | 0.130 |
| pls_10 | 1.594 | 0.701 | 0.299 | 0 | 0 | `age` | -0.081 |
| pls_11 | 1.141 | 0.644 | 0.356 | 0 | 0 | `statin` | 0.140 |

## Correlations of the latent components

Component score SD: pls_0 7.334, pls_1 3.901, pls_2 5.566, pls_3 3.472, pls_4 2.54, pls_5 2.944, pls_6 1.906, pls_7 1.995, pls_8 1.444, pls_9 1.873, pls_10 1.594, pls_11 1.141. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design | pls_4 rho | pls_4 rho \| design | pls_5 rho | pls_5 rho \| design | pls_6 rho | pls_6 rho \| design | pls_7 rho | pls_7 rho \| design | pls_8 rho | pls_8 rho \| design | pls_9 rho | pls_9 rho \| design | pls_10 rho | pls_10 rho \| design | pls_11 rho | pls_11 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1501 | -0.061 | n/a | -0.186 | n/a | 0.106 | n/a | 0.105 | n/a | -0.058 | n/a | 0.107 | n/a | 0.032 | n/a | 0.188 | n/a | 0.103 | n/a | 0.061 | n/a | -0.081 | n/a | 0.019 | n/a |
| `education` | covariates.csv | 1501 | 0.120 | n/a | 0.097 | n/a | -0.003 | n/a | 0.080 | n/a | 0.056 | n/a | -0.104 | n/a | 0.061 | n/a | 0.028 | n/a | 0.067 | n/a | -0.067 | n/a | 0.044 | n/a | 0.005 | n/a |
| `apoe4` | covariates.csv | 1501 | -0.050 | n/a | -0.095 | n/a | 0.085 | n/a | -0.124 | n/a | -0.069 | n/a | -0.122 | n/a | -0.054 | n/a | 0.024 | n/a | -0.009 | n/a | 0.002 | n/a | 0.043 | n/a | -0.080 | n/a |
| `phase` | covariates.csv | 1501 | 0.542* | n/a | 0.259 | n/a | -0.157 | n/a | -0.535* | n/a | 0.324* | n/a | -0.170 | n/a | 0.130 | n/a | 0.019 | n/a | 0.044 | n/a | 0.037 | n/a | -0.044 | n/a | -0.001 | n/a |
| `statin` | covariates.csv | 1501 | 0.292 | n/a | -0.038 | n/a | -0.117 | n/a | 0.020 | n/a | -0.357* | n/a | 0.151 | n/a | -0.022 | n/a | -0.028 | n/a | 0.077 | n/a | 0.130 | n/a | 0.064 | n/a | 0.140 | n/a |
| `stage` | metadata.csv | 1501 | -0.117 | -0.085 | -0.177 | -0.124 | 0.099 | 0.060 | -0.154 | -0.182 | -0.179 | -0.165 | -0.099 | -0.089 | -0.027 | 0.005 | 0.090 | 0.086 | -0.127 | -0.124 | 0.090 | 0.087 | -0.068 | -0.078 | -0.105 | -0.088 |
| `male` | metadata.csv | 1501 | 0.158 | 0.185 | -0.405* | -0.396* | -0.219 | -0.236 | 0.170 | 0.139 | -0.127 | -0.082 | -0.253 | -0.274 | 0.086 | 0.086 | 0.060 | 0.039 | 0.083 | 0.053 | 0.062 | 0.056 | 0.067 | 0.057 | -0.120 | -0.129 |
| `dx_bl` | cohort.csv | 1501 | -0.170 | -0.079 | -0.206 | -0.125 | 0.141 | 0.088 | -0.083 | -0.172 | -0.194 | -0.139 | -0.072 | -0.082 | -0.051 | -0.002 | 0.095 | 0.087 | -0.110 | -0.114 | 0.079 | 0.081 | -0.049 | -0.071 | -0.114 | -0.095 |

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

### nmr (165 features; variance share pc1 0.438, pc2 0.247, pc3 0.085; pc1 against `phase`: Spearman -0.130 here, |Pearson| 0.135 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | -0.071 | n/a | -0.048 | n/a | 0.037 | n/a |
| `education` | 1501 | -0.091 | n/a | 0.046 | n/a | -0.029 | n/a |
| `apoe4` | 1501 | 0.020 | n/a | 0.037 | n/a | -0.102 | n/a |
| `phase` | 1501 | -0.130 | n/a | 0.069 | n/a | 0.056 | n/a |
| `statin` | 1501 | -0.255 | n/a | -0.239 | n/a | 0.260 | n/a |
| `stage` | 1501 | 0.049 | 0.034 | -0.011 | -0.015 | -0.040 | -0.008 |
| `male` | 1501 | -0.184 | -0.143 | -0.383* | -0.371* | -0.227 | -0.257 |
| `dx_bl` | 1501 | 0.047 | 0.020 | 0.001 | 0.009 | -0.054 | -0.016 |

## Geometry shares

Share of the squared length of each vector of the trajectory geometry (from `stage_means.csv`) that lies along each component: each sex's net displacement (last stage minus first, what `angle` reads), the per-stage sex-difference vectors (Female minus Male) and the stage-centred ones. `value` is the signed component of a single vector (the net displacements), empty for the summed quantities.

| quantity | component | value | along | total | share |
|---|---|---:|---:|---:|---:|
| net_displacement_Female | pls_0 | -2.08 | 4.325 | 16.78 | 0.258 |
| net_displacement_Female | pls_1 | -1.08 | 1.166 | 16.78 | 0.070 |
| net_displacement_Female | pls_2 | 1.869 | 3.493 | 16.78 | 0.208 |
| net_displacement_Female | pls_3 | -2.244 | 5.037 | 16.78 | 0.300 |
| net_displacement_Female | pls_4 | -1.062 | 1.129 | 16.78 | 0.067 |
| net_displacement_Female | pls_5 | -0.5262 | 0.2768 | 16.78 | 0.016 |
| net_displacement_Female | pls_6 | -0.0401 | 0.001608 | 16.78 | 0.000 |
| net_displacement_Female | pls_7 | 0.8027 | 0.6443 | 16.78 | 0.038 |
| net_displacement_Female | pls_8 | -0.3576 | 0.1279 | 16.78 | 0.008 |
| net_displacement_Female | pls_9 | 0.5427 | 0.2946 | 16.78 | 0.018 |
| net_displacement_Female | pls_10 | -0.271 | 0.07345 | 16.78 | 0.004 |
| net_displacement_Female | pls_11 | -0.4604 | 0.212 | 16.78 | 0.013 |
| net_displacement_Male | pls_0 | -1.079 | 1.165 | 9.111 | 0.128 |
| net_displacement_Male | pls_1 | -1.292 | 1.67 | 9.111 | 0.183 |
| net_displacement_Male | pls_2 | 1.529 | 2.338 | 9.111 | 0.257 |
| net_displacement_Male | pls_3 | -1.355 | 1.837 | 9.111 | 0.202 |
| net_displacement_Male | pls_4 | -0.9931 | 0.9863 | 9.111 | 0.108 |
| net_displacement_Male | pls_5 | -0.4898 | 0.2399 | 9.111 | 0.026 |
| net_displacement_Male | pls_6 | -0.3165 | 0.1002 | 9.111 | 0.011 |
| net_displacement_Male | pls_7 | 0.4691 | 0.2201 | 9.111 | 0.024 |
| net_displacement_Male | pls_8 | -0.5822 | 0.339 | 9.111 | 0.037 |
| net_displacement_Male | pls_9 | 0.3387 | 0.1147 | 9.111 | 0.013 |
| net_displacement_Male | pls_10 | -0.2263 | 0.05123 | 9.111 | 0.006 |
| net_displacement_Male | pls_11 | -0.2213 | 0.04899 | 9.111 | 0.005 |
| sex_difference_by_stage | pls_0 | n/a | 19.06 | 89.59 | 0.213 |
| sex_difference_by_stage | pls_1 | n/a | 30.19 | 89.59 | 0.337 |
| sex_difference_by_stage | pls_2 | n/a | 27.75 | 89.59 | 0.310 |
| sex_difference_by_stage | pls_3 | n/a | 3.156 | 89.59 | 0.035 |
| sex_difference_by_stage | pls_4 | n/a | 0.4071 | 89.59 | 0.005 |
| sex_difference_by_stage | pls_5 | n/a | 7.744 | 89.59 | 0.086 |
| sex_difference_by_stage | pls_6 | n/a | 0.3219 | 89.59 | 0.004 |
| sex_difference_by_stage | pls_7 | n/a | 0.09482 | 89.59 | 0.001 |
| sex_difference_by_stage | pls_8 | n/a | 0.1218 | 89.59 | 0.001 |
| sex_difference_by_stage | pls_9 | n/a | 0.1467 | 89.59 | 0.002 |
| sex_difference_by_stage | pls_10 | n/a | 0.1943 | 89.59 | 0.002 |
| sex_difference_by_stage | pls_11 | n/a | 0.4089 | 89.59 | 0.005 |
| sex_difference_centred | pls_0 | n/a | 0.5178 | 1.892 | 0.274 |
| sex_difference_centred | pls_1 | n/a | 0.1425 | 1.892 | 0.075 |
| sex_difference_centred | pls_2 | n/a | 0.2364 | 1.892 | 0.125 |
| sex_difference_centred | pls_3 | n/a | 0.4339 | 1.892 | 0.229 |
| sex_difference_centred | pls_4 | n/a | 0.004 | 1.892 | 0.002 |
| sex_difference_centred | pls_5 | n/a | 0.08868 | 1.892 | 0.047 |
| sex_difference_centred | pls_6 | n/a | 0.221 | 1.892 | 0.117 |
| sex_difference_centred | pls_7 | n/a | 0.06617 | 1.892 | 0.035 |
| sex_difference_centred | pls_8 | n/a | 0.04374 | 1.892 | 0.023 |
| sex_difference_centred | pls_9 | n/a | 0.0929 | 1.892 | 0.049 |
| sex_difference_centred | pls_10 | n/a | 0.002907 | 1.892 | 0.002 |
| sex_difference_centred | pls_11 | n/a | 0.04203 | 1.892 | 0.022 |

## Analysis read

- directory: `results/motco_rank_sensitivity/rank_12`
- rank: 12 (`forced`)
- latent adjustment: none
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- rank sweep: forced rank 12 of `forced_rank_ladder` (`RANK_SENSITIVITY_LADDER`); `pls_0` to `pls_7` are the primary's components (nesting) and keep its correlations; a component above the primary's rank 8 that tracks a variable, `phase` in particular, is a measurement-space finding about the higher ranks and never grounds to choose a rank (sweep rule 7)

## Findings

- pls_0: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (0.54; partial n/a)
- pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.40; partial -0.40)
- pls_3: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.53; partial n/a)
- pls_4: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): statin (-0.36; partial n/a), phase (0.32; partial n/a)
- the analysis read is not the primary (directory results/motco_rank_sensitivity/rank_12, forced rank 12 of the rank sweep): the primary's rank and row counts are not expected; the top rank's read and rows are (RANK_SENSITIVITY_EXPECTED_COUNTS), with the rank-independent counts

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

## Reading rules of the rank sweep

Binding for every reader of the rank sweep (`RANK_SENSITIVITY_READING_RULES`, decided by `adni-rank-sensitivity` before any run), after `READING_RULES`:

1. The sweep is read beside the primary and never replaces it. The primary's rank is its CV-selected rank (8). No rank of the sweep is chosen, adopted or ranked, and no sweep result changes a constant (`ANALYSIS_RANK_FLOOR` and the ladder included), reruns the primary or defines another arm.
2. Every rank is the primary's analysis with one setting changed: `forced_components`, which fixes the rank and skips MOTCO's cross-validation. The export, the covariates and their coding, the seed, the permutations and every other setting are the primary's, and at `n_jobs = 1` every rank permutes the same residual indices. A difference between ranks is a difference of measurement, not of permutation draws. A rejection status that differs from the primary's is rank dependence, not a result at that rank.
3. PLS-DA components are nested. At a forced rank at or below the primary's 8, the latent space is spanned by the primary's first components; a rank above 8 adds components the cross-validation did not select. The anchor run at rank 8 reproduces the primary's record and files exactly, so the primary row is also the sweep's row at its rank.
4. Each rank's floor, eigengap and `angle` null summary are reported beside its `angle`. The `angle` null depends on the rank, so each `angle` is read against its own null, never against the `angle` of another rank. At rank 2, the floor, `angle` and `shape` are measured in two dimensions (reading rule 2).
5. MOTCO's forced-rank evidence is its Phase 5 rank ladder (2026-09-08; MOTCO 0.6.0, n = 1200, four stages, no covariates): size held at every forced rank, and the ranks above `n_stages − 1` lost `shape` power and gained no `angle` power. No Type I or power check exists at a forced rank at this design or with covariates. A non-rejection at any rank is no more informative than the primary's (reading rule 3), and a rejection at a forced rank only is rank dependence, read beside that rank's null summary.
6. The sweep is not a test. No rule combines the ranks, picks the rank with the smallest p-value or counts the ranks that reject, and the p-values are not adjusted for multiplicity because no decision is taken from them.
7. The axis diagnostic of the top rank (12) is reported beside the sweep. Its components up to the primary's rank are the primary's, with the primary's correlations. A component above it that tracks a variable, `phase` in particular, is a measurement-space finding about the higher ranks and never grounds to choose a rank.
8. The sweep is not crossed with the latent adjustment, an export variant or the CN / LMCI / AD arm, and is read against the primary only. The CV-selected ranks of those analyses are their own selections, and no sentence reads them against the sweep.
