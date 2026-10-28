# MOTCO trajectory analysis: ADNI serum metabolomics, sex × stage — `stage`-conditioned latent-adjustment arm

MOTCO 0.10.0; n = 1501; groups Female vs Male (`sex`); stages CN → MCI → AD (`stage`); blocks p180 (133 features, identity), nmr (165 features, identity); orientation `net_displacement`; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1; latent adjustment: `stage` (the sensitivity arm `latent_stage`, `LATENT_SENSITIVITY_ARM` of `adni-latent-sensitivity`: the latent basis is fitted on the features with the covariates regressed out within stage and the raw features are measured in it; read beside the primary, never replacing it).

## Statistics

| statistic | observed | p (RRPP) | rejected | null mean | null sd | null q95 | note |
|---|---:|---:|:---:|---:|---:|---:|---|
| delta | 1.55786 | 0.0568 | no | 0.648911 | 0.496943 | 1.60501 |  |
| angle | 14.2407 | 0.7244 | no | 21.3608 | 10.5721 | 41.2466 | degrees, endpoint stages CN and AD; CV-selected rank 4 (rank floor 2); pooled relative eigengap 0.878123 |
| shape | 0.179861 | 0.6402 | no | 0.241913 | 0.129156 | 0.475997 |  |

Reading, under the rules below:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. In the arm this non-rejection is weaker than the primary's (arm rule 5).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the arm this non-rejection is weaker than the primary's (arm rule 5).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the arm this non-rejection is weaker than the primary's (arm rule 5).

## Cell sizes

| group | stage CN | stage MCI | stage AD | total |
|---|---:|---:|---:|---:|
| Female | 237 | 310 | 125 | 672 |
| Male | 223 | 448 | 158 | 829 |

## Latent space

- PLS-DA rank: 4 (`cv`); rank floor 2
- pooled relative eigengap of the stage-mean configuration: 0.878123 (permutation null q05 / q50 / q95: 0.632903 / 0.875739 / 0.975946)
- cv_mean_auroc: 0.580311
- CV: cv2_splits 4, cv1_splits 3, n_repeats 5 (5 completed), max_components 20, rank floor 2, random_state 1203
- blocks: p180 (133 features, identity), nmr (165 features, identity); features are z-scored by MOTCO (pooled per-feature scalers)

## Latent adjustment

- conditioning: `stage` (`covariate_latent_adjustment`, `LATENT_SENSITIVITY_ARM`): the basis is fitted on the pooled-standardized features with the covariates regressed out given the intercept and the stage indicators, per CV training set and on the full sample; the raw features are projected onto it; the trajectory model, LS-means and RRPP are the primary's
- covariates residualized (in order): `age`, `education`, `apoe4`, `phase`, `statin`
- residualization design columns: 8 (stage[1] = MCI, stage[2] = AD, age, education, apoe4[1], apoe4[2], phase[ADNI2GO], statin[1])
- samples 1501; residual df 1492 (n − 1 − 2 stage indicator(s) − 6 design column(s)); smallest CV training df 741
- feature scale: `pooled_standardized`
- feature R² of the covariates given the intercept and the stage indicators (the share of each feature's variance the residualization removed): q05 / q25 / q50 / q75 / q95 0.015 / 0.034 / 0.116 / 0.258 / 0.486; mean 0.166; fraction above 0.5 0.047

## Covariates

- entered (in order, additively): `age` (numeric), `education` (numeric), `apoe4` (categorical), `phase` (categorical), `statin` (categorical)
- design columns: 6 (age, education, apoe4[1], apoe4[2], phase[ADNI2GO], statin[1])
- reference levels: `apoe4` 0, `phase` ADNI1, `statin` 0
- missing policy: `error`; dropped participants: 0
- LS-means evaluated at the reference row (`pooled_mean`); no sex × covariate or stage × covariate term:

| design column | reference value |
|---|---:|
| age | 73.703 |
| education | 15.9274 |
| apoe4[1] | 0.361093 |
| apoe4[2] | 0.0992672 |
| phase[ADNI2GO] | 0.544304 |
| statin[1] | 0.469021 |

## Export context

- feature rule (`EXPORT_FEATURE_RULE`): units `log2(x + floor)`, MOTCO transform `identity`; kept / cleaned columns: p180 133 / 133, nmr 165 / 245; joint features 298
- block shares (unweighted in MOTCO): p180 0.446, nmr 0.554
- p180 run offset (`phase`, ADNI1 against ADNI2GO, recorded by export and not corrected): p180 median |d| 1.12, |d| > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73; nmr median |d| 0.21, |d| > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13
- `phase` enters as a covariate of the stage means (above) and, in this arm, is among the covariates regressed out of the features within stage before the basis is fitted; the primary's latent space is built without it

## Reading rules

Binding for every reader of this result (`READING_RULES`, written before the first run):

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
