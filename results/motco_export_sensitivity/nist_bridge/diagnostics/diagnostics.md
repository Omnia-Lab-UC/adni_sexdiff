# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of the export variant `nist_bridge` (`EXPORT_VARIANTS`, change `adni-nist-bridge`: the primary's settings on an export whose p180 run handling differs; not the primary) covariate-adjusted trajectory analysis (`results/motco_export_sensitivity/nist_bridge/analysis`, cv-selected rank 6, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of this export variant (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_1 | 4.156 | `male` | metadata.csv | 1501 | -0.411 | -0.397 | raw+partial |

Block principal components (by |rho|):

| block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| p180 | pc2 | 0.087 | `phase` | covariates.csv | 1501 | -0.593 | n/a | raw |
| nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.383 | -0.371 | raw+partial |
| p180 | pc1 | 0.309 | `male` | metadata.csv | 1501 | -0.362 | -0.365 | raw+partial |
| p180 | pc1 | 0.309 | `statin` | covariates.csv | 1501 | -0.306 | n/a | raw |
| p180 | pc2 | 0.087 | `male` | metadata.csv | 1501 | 0.292 | 0.303 | partial |

## Components

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 6.268 | 0.416 | 0.584 | 0 | 0 | `phase` | 0.290 |
| pls_1 | 4.156 | 0.718 | 0.282 | 1 | 1 | `male` | -0.411 |
| pls_2 | 6.175 | 0.660 | 0.340 | 0 | 0 | `male` | -0.286 |
| pls_3 | 2.787 | 0.729 | 0.271 | 0 | 0 | `statin` | -0.243 |
| pls_4 | 2.097 | 0.678 | 0.322 | 0 | 0 | `male` | -0.237 |
| pls_5 | 2.137 | 0.713 | 0.287 | 0 | 0 | `male` | -0.152 |

## Correlations of the latent components

Component score SD: pls_0 6.268, pls_1 4.156, pls_2 6.175, pls_3 2.787, pls_4 2.097, pls_5 2.137. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design | pls_4 rho | pls_4 rho \| design | pls_5 rho | pls_5 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1501 | -0.006 | n/a | -0.193 | n/a | 0.070 | n/a | -0.017 | n/a | 0.116 | n/a | -0.044 | n/a |
| `education` | covariates.csv | 1501 | 0.121 | n/a | 0.086 | n/a | -0.013 | n/a | 0.130 | n/a | -0.086 | n/a | -0.080 | n/a |
| `apoe4` | covariates.csv | 1501 | -0.054 | n/a | -0.116 | n/a | 0.093 | n/a | -0.086 | n/a | -0.140 | n/a | 0.070 | n/a |
| `phase` | covariates.csv | 1501 | 0.290 | n/a | 0.264 | n/a | -0.126 | n/a | -0.016 | n/a | -0.024 | n/a | -0.001 | n/a |
| `statin` | covariates.csv | 1501 | 0.260 | n/a | -0.065 | n/a | -0.227 | n/a | -0.243 | n/a | -0.011 | n/a | -0.074 | n/a |
| `stage` | metadata.csv | 1501 | -0.120 | -0.093 | -0.187 | -0.128 | 0.121 | 0.085 | -0.178 | -0.146 | -0.152 | -0.135 | 0.025 | -0.007 |
| `male` | metadata.csv | 1501 | 0.065 | 0.033 | -0.411* | -0.397* | -0.286 | -0.290 | 0.141 | 0.149 | -0.237 | -0.232 | -0.152 | -0.127 |
| `dx_bl` | cohort.csv | 1501 | -0.138 | -0.081 | -0.218 | -0.130 | 0.153 | 0.108 | -0.159 | -0.132 | -0.130 | -0.117 | 0.038 | 0.005 |

`*` marks |rho| ≥ 0.3.

## Block principal components

### p180 (133 features; variance share pc1 0.309, pc2 0.087, pc3 0.062; pc1 against `phase`: Spearman -0.210 here, |Pearson| 0.215 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | 0.006 | n/a | 0.185 | n/a | 0.165 | n/a |
| `education` | 1501 | -0.012 | n/a | -0.107 | n/a | 0.006 | n/a |
| `apoe4` | 1501 | -0.021 | n/a | 0.007 | n/a | 0.049 | n/a |
| `phase` | 1501 | -0.210 | n/a | -0.593* | n/a | 0.024 | n/a |
| `statin` | 1501 | -0.306* | n/a | 0.198 | n/a | -0.041 | n/a |
| `stage` | 1501 | 0.029 | 0.024 | 0.068 | 0.025 | 0.057 | 0.033 |
| `male` | 1501 | -0.362* | -0.365* | 0.292 | 0.303* | 0.105 | 0.090 |
| `dx_bl` | 1501 | 0.056 | 0.031 | 0.125 | 0.004 | 0.074 | 0.054 |

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
| net_displacement_Female | pls_0 | -1.924 | 3.7 | 15.51 | 0.239 |
| net_displacement_Female | pls_1 | -1.254 | 1.571 | 15.51 | 0.101 |
| net_displacement_Female | pls_2 | 2.686 | 7.217 | 15.51 | 0.465 |
| net_displacement_Female | pls_3 | -1.614 | 2.606 | 15.51 | 0.168 |
| net_displacement_Female | pls_4 | -0.6281 | 0.3945 | 15.51 | 0.025 |
| net_displacement_Female | pls_5 | 0.1383 | 0.01914 | 15.51 | 0.001 |
| net_displacement_Male | pls_0 | -0.9567 | 0.9153 | 8.398 | 0.109 |
| net_displacement_Male | pls_1 | -1.366 | 1.866 | 8.398 | 0.222 |
| net_displacement_Male | pls_2 | 1.941 | 3.769 | 8.398 | 0.449 |
| net_displacement_Male | pls_3 | -1.172 | 1.375 | 8.398 | 0.164 |
| net_displacement_Male | pls_4 | -0.6091 | 0.371 | 8.398 | 0.044 |
| net_displacement_Male | pls_5 | 0.3188 | 0.1016 | 8.398 | 0.012 |
| sex_difference_by_stage | pls_0 | n/a | 1.427 | 91.68 | 0.016 |
| sex_difference_by_stage | pls_1 | n/a | 33.69 | 91.68 | 0.368 |
| sex_difference_by_stage | pls_2 | n/a | 49.92 | 91.68 | 0.545 |
| sex_difference_by_stage | pls_3 | n/a | 2.92 | 91.68 | 0.032 |
| sex_difference_by_stage | pls_4 | n/a | 2.91 | 91.68 | 0.032 |
| sex_difference_by_stage | pls_5 | n/a | 0.8071 | 91.68 | 0.009 |
| sex_difference_centred | pls_0 | n/a | 0.605 | 1.593 | 0.380 |
| sex_difference_centred | pls_1 | n/a | 0.09287 | 1.593 | 0.058 |
| sex_difference_centred | pls_2 | n/a | 0.4964 | 1.593 | 0.312 |
| sex_difference_centred | pls_3 | n/a | 0.09967 | 1.593 | 0.063 |
| sex_difference_centred | pls_4 | n/a | 0.05366 | 1.593 | 0.034 |
| sex_difference_centred | pls_5 | n/a | 0.2449 | 1.593 | 0.154 |

## Analysis read

- directory: `results/motco_export_sensitivity/nist_bridge/analysis`
- rank: 6 (`cv`)
- latent adjustment: none
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- export variant: `nist_bridge` (`EXPORT_VARIANTS`): a component of the variant that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics and is never grounds to adopt the variant (variant rule 7)

## Findings

- pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.41; partial -0.40)
- the analysis read is not the primary (directory results/motco_export_sensitivity/nist_bridge/analysis, latent adjustment None, export variant 'nist_bridge'): the primary's rank and the row counts are not expected; the rank-independent counts are

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

## Reading rules of the export variants

Binding for every reader of an export variant (`EXPORT_VARIANT_READING_RULES`, decided by `adni-nist-bridge` before any run), after `READING_RULES`:

1. A variant is read beside the primary and never replaces it. No variant result changes a constant, reruns the primary or adopts a variant.
2. A variant shares with the primary the cleaned tables, the participants, the NMR block, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the p180 values. A rejection status that differs is dependence on the handling of the p180 run, not a result of the variant.
3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
4. `nist_bridge` removes the part of the run offset that NIST SRM 1950 carries, between-run calibration. It assumes the run acts as one factor per metabolite, the same in plasma (NIST) and serum (participants). It leaves what NIST cannot see: a shift common to most metabolites, sample-handling differences between the protocols (the largest residuals are aspartate and glutamate) and the seven unbridged metabolites. `phase` stays a covariate of the stage means and carries what remains.
5. `per_run_standardized` removes each p180 metabolite's whole difference in mean and spread between the runs, whatever its source: calibration, sample handling, and the stage-composition difference the runs carry, since SMC and EMCI were enrolled only in ADNI-GO/2. A difference between it and `nist_bridge` is read as the part of the run difference that is not calibration, never as evidence for either variant.
6. A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in a variant is dependence on the run handling and is read beside the variant's rank and null summary.
7. The variant's export manifest records the run offset per block, and for `nist_bridge` the factor per metabolite; both are reported beside the results. A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.
