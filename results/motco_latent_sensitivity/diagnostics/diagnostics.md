# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage

Descriptive measurement-space diagnostics of the `stage`-conditioned latent-adjustment sensitivity arm `latent_stage` (`LATENT_SENSITIVITY_ARM`, change `adni-latent-sensitivity`; not the primary) covariate-adjusted trajectory analysis (`results/motco_latent_sensitivity/analysis`, cv-selected rank 4, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables (`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the 6 design columns of the record (the Spearman correlation of the OLS residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first 3 principal components of each z-scored block, the share of the sex × stage geometry along each component and the block composition of each component. Rows with |rho| ≥ 0.3 are flagged and listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis correlated with a variable is a finding about the measurement space of this arm (the primary stays primary), not a reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and the primary analysis stays primary under the reading rules below.

## Flagged correlations

Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.

Latent components (by |rho|):

| component | sd | variable | source | n | rho | rho \| design | flag |
|---|---:|---|---|---:|---:|---:|---|
| pls_1 | 3.583 | `male` | metadata.csv | 1501 | -0.477 | -0.458 | raw+partial |
| pls_2 | 6.797 | `phase` | covariates.csv | 1501 | 0.416 | n/a | raw |
| pls_2 | 6.797 | `statin` | covariates.csv | 1501 | 0.334 | n/a | raw |

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
| pls_0 | 6.298 | 0.254 | 0.746 | 0 | 0 | `phase` | 0.241 |
| pls_1 | 3.583 | 0.573 | 0.427 | 1 | 1 | `male` | -0.477 |
| pls_2 | 6.797 | 0.676 | 0.324 | 2 | 0 | `phase` | 0.416 |
| pls_3 | 2.453 | 0.768 | 0.232 | 0 | 0 | `statin` | -0.185 |

## Correlations of the latent components

Component score SD: pls_0 6.298, pls_1 3.583, pls_2 6.797, pls_3 2.453. Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). Variables in declared order; `n` is the pairwise-complete count.

| variable | source | n | pls_0 rho | pls_0 rho \| design | pls_1 rho | pls_1 rho \| design | pls_2 rho | pls_2 rho \| design | pls_3 rho | pls_3 rho \| design |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `age` | covariates.csv | 1501 | -0.005 | n/a | -0.197 | n/a | -0.099 | n/a | -0.029 | n/a |
| `education` | covariates.csv | 1501 | 0.095 | n/a | -0.019 | n/a | 0.037 | n/a | 0.072 | n/a |
| `apoe4` | covariates.csv | 1501 | -0.022 | n/a | -0.063 | n/a | -0.063 | n/a | -0.023 | n/a |
| `phase` | covariates.csv | 1501 | 0.241 | n/a | 0.215 | n/a | 0.416* | n/a | -0.155 | n/a |
| `statin` | covariates.csv | 1501 | 0.173 | n/a | 0.063 | n/a | 0.334* | n/a | -0.185 | n/a |
| `stage` | metadata.csv | 1501 | -0.088 | -0.072 | -0.139 | -0.110 | -0.140 | -0.107 | -0.172 | -0.178 |
| `male` | metadata.csv | 1501 | -0.094 | -0.125 | -0.477* | -0.458* | 0.198 | 0.234 | -0.023 | -0.025 |
| `dx_bl` | cohort.csv | 1501 | -0.097 | -0.054 | -0.168 | -0.114 | -0.193 | -0.118 | -0.135 | -0.163 |

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
| net_displacement_Female | pls_0 | -1.128 | 1.273 | 11.46 | 0.111 |
| net_displacement_Female | pls_1 | -0.6928 | 0.4799 | 11.46 | 0.042 |
| net_displacement_Female | pls_2 | -2.76 | 7.617 | 11.46 | 0.665 |
| net_displacement_Female | pls_3 | -1.444 | 2.085 | 11.46 | 0.182 |
| net_displacement_Male | pls_0 | -0.4412 | 0.1947 | 4.692 | 0.041 |
| net_displacement_Male | pls_1 | -0.8416 | 0.7082 | 4.692 | 0.151 |
| net_displacement_Male | pls_2 | -1.613 | 2.602 | 4.692 | 0.555 |
| net_displacement_Male | pls_3 | -1.09 | 1.187 | 4.692 | 0.253 |
| sex_difference_by_stage | pls_0 | n/a | 8.459 | 76.19 | 0.111 |
| sex_difference_by_stage | pls_1 | n/a | 34.11 | 76.19 | 0.448 |
| sex_difference_by_stage | pls_2 | n/a | 33.55 | 76.19 | 0.440 |
| sex_difference_by_stage | pls_3 | n/a | 0.06833 | 76.19 | 0.001 |
| sex_difference_centred | pls_0 | n/a | 0.5238 | 1.436 | 0.365 |
| sex_difference_centred | pls_1 | n/a | 0.04012 | 1.436 | 0.028 |
| sex_difference_centred | pls_2 | n/a | 0.8096 | 1.436 | 0.564 |
| sex_difference_centred | pls_3 | n/a | 0.06277 | 1.436 | 0.044 |

## Analysis read

- directory: `results/motco_latent_sensitivity/analysis`
- rank: 4 (`cv`)
- latent adjustment: stage
- n_jobs: 1
- primary: no (the primary rank and row counts are not expected)
- arm: `latent_stage` (`LATENT_SENSITIVITY_ARM`): a component of the arm that tracks a variable here is a measurement-space finding about the arm; it never reinterprets either analysis' statistics and is never grounds to adopt the arm (arm rule 9)

## Findings

- pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.48; partial -0.46)
- pls_2: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (0.42; partial n/a), statin (0.33; partial n/a)
- the analysis read is not the primary (directory results/motco_latent_sensitivity/analysis, latent adjustment 'stage'): the primary's rank and the row counts are not expected; the rank-independent counts are

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

## Reading rules of the arm

Binding for every reader of the arm (`LATENT_SENSITIVITY_READING_RULES`, decided by `adni-latent-sensitivity` before any run), after `READING_RULES`:

1. The arm is read beside the primary and never replaces it. MOTCO's power comparison returned `candidate_fails` for `stage` conditioning, which excludes the latent adjustment as a replacement of the covariate-blind primary.
2. The primary and the arm share the export, the covariates and their design, the cells, the CV folds, the seed and the permutations. They differ only in the latent basis and the CV-selected rank: the arm's basis is fitted on the features with the five covariates regressed out within stage, and the raw features are measured in it. A rejection status that differs is basis dependence, not a result of the arm.
3. The arm's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked as better or worse.
4. An `angle` rejection that appears only in the arm is read against MOTCO's controls, and is not evidence of an orientation difference on its own: the translation control rejected `angle` at 0.085–0.092 under `stage` conditioning, against the 0.0706 bound (the covariate-blind basis was above it too, at 0.076–0.086); under the Type I check, `angle` held the bound by only 0.004 (0.067 against 0.0706).
5. A `delta` or `shape` non-rejection in the arm is weaker than the primary's. MOTCO measured lost `shape` power with a covariate-aligned nuisance axis (0.243 against 0.428) and lost small-magnitude `delta` power without one (0.400 against 0.520 at e = 0.1). Reading rules 3 and 4 hold in the arm.
6. The arm's `latent_adjustment` block and its covariate block are reported beside its results. The `latent_adjustment` block holds the conditioning, the design columns, the residual df, the smallest CV training df and the feature R² summary; `feature_r2` states how much feature variance the residualization removed.
7. Residualizing a covariate that mediates the stage effect removes real stage signal, and no data can tell a confounder from a mediator. `age`, `education` and `apoe4` precede disease, and `phase` is the assay run and protocol (`LATENT_SENSITIVITY_COVARIATE_ROLES`). `statin` may follow diagnosis, so the arm's basis may have removed stage signal that runs through treatment.
8. MOTCO's latent-adjustment operating characteristics were measured at one design: n = 80, the SEA-AD MTG structure, 498 features, eight covariates in nine design columns, covariates confounded with group × stage far beyond this design's. None was measured at this design (n = 1501, 298 metabolites, six design columns), and the arm carries no Type I or power claim of its own.
9. A component of the arm that tracks a variable in its axis diagnostic is a measurement-space finding about the arm. It never reinterprets either analysis' statistics and is never grounds to adopt the arm.
