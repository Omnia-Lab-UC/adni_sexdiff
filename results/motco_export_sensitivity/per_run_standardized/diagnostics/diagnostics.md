# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of the export variant `per_run_standardized` (`EXPORT_VARIANTS`, change `adni-nist-bridge`: the primary's settings on an export whose p180 run handling differs; not the primary) covariate-adjusted trajectory analysis (`results/motco_export_sensitivity/per_run_standardized/analysis`, cv-selected rank 4, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of this export variant (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_1 | 3.941 | `male` | metadata.csv | 1501 | -0.414 | -0.400 | raw+partial |
| pls_3 | 2.808 | `statin` | covariates.csv | 1501 | -0.317 | n/a | raw |

Block principal components (by |rho|):

| block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| p180 | pc1 | 0.307 | `male` | metadata.csv | 1501 | -0.392 | -0.373 | raw+partial |
| nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.383 | -0.371 | raw+partial |
| p180 | pc1 | 0.307 | `statin` | covariates.csv | 1501 | -0.318 | n/a | raw |

## Components

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 6.159 | 0.333 | 0.667 | 0 | 0 | `statin` | 0.239 |
| pls_1 | 3.941 | 0.698 | 0.302 | 1 | 1 | `male` | -0.414 |
| pls_2 | 6.278 | 0.682 | 0.318 | 0 | 0 | `male` | -0.278 |
| pls_3 | 2.808 | 0.710 | 0.290 | 1 | 0 | `statin` | -0.317 |

## Correlations of the latent components

Component score SD: pls_0 6.159, pls_1 3.941, pls_2 6.278, pls_3 2.808. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1501 | 0.031 | n/a | -0.140 | n/a | 0.033 | n/a | -0.047 | n/a |
| `education` | covariates.csv | 1501 | 0.109 | n/a | 0.054 | n/a | -0.005 | n/a | 0.116 | n/a |
| `apoe4` | covariates.csv | 1501 | -0.053 | n/a | -0.127 | n/a | 0.102 | n/a | -0.067 | n/a |
| `phase` | covariates.csv | 1501 | 0.156 | n/a | 0.062 | n/a | 0.006 | n/a | 0.084 | n/a |
| `statin` | covariates.csv | 1501 | 0.239 | n/a | -0.035 | n/a | -0.275 | n/a | -0.317* | n/a |
| `stage` | metadata.csv | 1501 | -0.111 | -0.088 | -0.177 | -0.130 | 0.133 | 0.108 | -0.189 | -0.163 |
| `male` | metadata.csv | 1501 | 0.026 | -0.017 | -0.414* | -0.400* | -0.278 | -0.269 | 0.056 | 0.083 |
| `dx_bl` | cohort.csv | 1501 | -0.112 | -0.074 | -0.184 | -0.132 | 0.146 | 0.127 | -0.177 | -0.144 |

`*` marks |rho| ≥ 0.3.

## Block principal components

### p180 (133 features; variance share pc1 0.307, pc2 0.068, pc3 0.064; pc1 against `phase`: Spearman 0.005 here, |Pearson| 0.000 recorded by export)

| variable | n | pc1 rho | pc1 rho \| design | pc2 rho | pc2 rho \| design | pc3 rho | pc3 rho \| design |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age` | 1501 | -0.039 | n/a | 0.035 | n/a | 0.181 | n/a |
| `education` | 1501 | 0.015 | n/a | -0.061 | n/a | -0.011 | n/a |
| `apoe4` | 1501 | -0.029 | n/a | -0.031 | n/a | 0.039 | n/a |
| `phase` | 1501 | 0.005 | n/a | -0.002 | n/a | 0.003 | n/a |
| `statin` | 1501 | -0.318* | n/a | 0.186 | n/a | 0.008 | n/a |
| `stage` | 1501 | 0.010 | 0.023 | 0.004 | 0.012 | 0.061 | 0.038 |
| `male` | 1501 | -0.392* | -0.373* | 0.218 | 0.207 | 0.155 | 0.138 |
| `dx_bl` | 1501 | 0.012 | 0.031 | -0.012 | -0.009 | 0.078 | 0.056 |

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
| net_displacement_Female | pls_0 | -1.775 | 3.149 | 16.95 | 0.186 |
| net_displacement_Female | pls_1 | -1.259 | 1.586 | 16.95 | 0.094 |
| net_displacement_Female | pls_2 | 3.122 | 9.747 | 16.95 | 0.575 |
| net_displacement_Female | pls_3 | -1.573 | 2.473 | 16.95 | 0.146 |
| net_displacement_Male | pls_0 | -0.8521 | 0.7261 | 8.883 | 0.082 |
| net_displacement_Male | pls_1 | -1.327 | 1.761 | 8.883 | 0.198 |
| net_displacement_Male | pls_2 | 2.206 | 4.866 | 8.883 | 0.548 |
| net_displacement_Male | pls_3 | -1.237 | 1.53 | 8.883 | 0.172 |
| sex_difference_by_stage | pls_0 | n/a | 0.7436 | 79.92 | 0.009 |
| sex_difference_by_stage | pls_1 | n/a | 33.12 | 79.92 | 0.414 |
| sex_difference_by_stage | pls_2 | n/a | 45.03 | 79.92 | 0.563 |
| sex_difference_by_stage | pls_3 | n/a | 1.035 | 79.92 | 0.013 |
| sex_difference_centred | pls_0 | n/a | 0.6857 | 1.457 | 0.471 |
| sex_difference_centred | pls_1 | n/a | 0.1479 | 1.457 | 0.102 |
| sex_difference_centred | pls_2 | n/a | 0.5543 | 1.457 | 0.381 |
| sex_difference_centred | pls_3 | n/a | 0.06878 | 1.457 | 0.047 |

## Analysis read

- directory: `results/motco_export_sensitivity/per_run_standardized/analysis`
- rank: 4 (`cv`)
- latent adjustment: none
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- export variant: `per_run_standardized` (`EXPORT_VARIANTS`): a component of the variant that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics and is never grounds to adopt the variant (variant rule 7)

## Findings

- pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.41; partial -0.40)
- pls_3: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): statin (-0.32; partial n/a)
- the analysis read is not the primary (directory results/motco_export_sensitivity/per_run_standardized/analysis, latent adjustment None, export variant 'per_run_standardized'): the primary's rank and the row counts are not expected; the rank-independent counts are

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
