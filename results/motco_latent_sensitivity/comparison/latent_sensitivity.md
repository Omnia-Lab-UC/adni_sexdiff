# MOTCO latent-adjustment sensitivity: ADNI serum metabolomics, sex × stage

The primary analysis (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`) beside its predeclared sensitivity arm `latent_stage` (`LATENT_SENSITIVITY_ARM`, change `adni-latent-sensitivity`: `covariate_latent_adjustment` = `stage`, the same five covariates, every other setting the primary's; `results/motco_latent_sensitivity/analysis`, `result.json` sha256 `f24e0e7417af6faa8a54ea46cd275aba221c5c94a5c7978f4f583de0a9fb3f70`). MOTCO 0.10.0; n = 1501; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1. The primary row comes first and its status is the result; the arm is read beside it and never replaces it (arm rule 1). A status that differs is basis dependence, not a result of the arm (arm rule 2). Every value below is read from the two `result.json` records.

## Statistics

| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---:|---:|:---:|---:|---:|---:|---|
| delta | primary | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | same |
| delta | latent_stage | 1.55786 | 0.0568 | no | 0.648911 | 0.496943 | 1.60501 | same |
| angle | primary | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | same |
| angle | latent_stage | 14.2407 | 0.7244 | no | 21.3608 | 10.5721 | 41.2466 | same |
| shape | primary | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | same |
| shape | latent_stage | 0.179861 | 0.6402 | no | 0.241913 | 0.129156 | 0.475997 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, arm rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); latent_stage rank 4 (floor 2, eigengap 0.878123); the ranks differ, which is reported, not ranked as better or worse (arm rule 3).

Status per statistic:

- `delta`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

## Latent space

| quantity | primary | latent_stage |
|---|---:|---:|
| PLS-DA rank (selection) | 8 (`cv`) | 4 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 | 2 |
| cv_mean_auroc | 0.599514 | 0.580311 |
| CV repeats completed | 5 | 5 |
| pooled relative eigengap | 0.74399 | 0.878123 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 | 0.632903 / 0.875739 / 0.975946 |

The two analyses share the export, the covariates and their design, the cells, the CV folds (stratified on the stage, as the primary's), the seed and the permutations; they differ only in the latent basis and the CV-selected rank (arm rule 2).

## Latent adjustment of the arm

- conditioning: `stage` (`covariate_latent_adjustment`): the basis is fitted on the pooled-standardized features with the covariates regressed out given the intercept and the stage indicators, per CV training set and on the full sample; the raw features are projected onto it; the trajectory model, LS-means and RRPP are the primary's
- covariates residualized (in order): `age`, `education`, `apoe4`, `phase`, `statin`
- residualization design columns: 8 (stage[1] = MCI, stage[2] = AD, age, education, apoe4[1], apoe4[2], phase[ADNI2GO], statin[1])
- samples 1501; residual df 1492 (n − 1 − 2 stage indicator(s) − 6 design column(s)); smallest CV training df 741
- feature scale: `pooled_standardized`
- feature R² of the covariates given the intercept and the stage indicators (the share of each feature's variance the residualization removed; arm rule 6): q05 / q25 / q50 / q75 / q95 0.015 / 0.034 / 0.116 / 0.258 / 0.486; mean 0.166; fraction above 0.5 0.047

## Covariates residualized by the arm

Each covariate's relation to the stage effect (`LATENT_SENSITIVITY_COVARIATE_ROLES`, decided before any run; no statistic or threshold is computed for it and nothing changes because of it). Residualizing a covariate that mediates the stage effect removes real stage signal, and no data can tell a confounder from a mediator (arm rule 7).

| covariate | role | variable | justification |
|---|---|---|---|
| `age` | pre-disease | age at baseline | precedes disease: it can confound the stage effect but cannot be downstream of it |
| `education` | pre-disease | years of schooling, completed before enrolment | precedes disease: it can confound the stage effect but cannot be downstream of it |
| `apoe4` | pre-disease | germline APOE e4 genotype (allele count) | precedes disease: it can confound the stage effect but cannot be downstream of it |
| `phase` | design | the assay run and enrolment protocol (p180 kits ADNI-1 against ADNI-GO/2) | tied to stage composition by design (SMC and EMCI exist only in ADNI-GO/2), not caused by stage |
| `statin` | mediator candidate | HMG-CoA reductase inhibitor use on the screening medication row | a treatment that may follow diagnosis: prescribing differs with cognitive status; it stays in the arm because the arm was predeclared with the five covariates, and the reading carries the limitation |

The mediator candidate is `statin`: a treatment that may follow diagnosis, so the arm's basis may have removed stage signal that runs through treatment (arm rule 7). It stays in the arm because the arm was predeclared with the five covariates.

Per sex × stage cell of the analysis cohort, copied from `cohort_manifest.json` (`descriptives`, set `intersection`), not recomputed: n, age and education mean (sd), and counts per level of `apoe4` (0 / 1 / 2), `phase` (ADNI1 / ADNI2GO) and `statin` (0 / 1).

| sex | stage | n | age mean (sd) | education mean (sd) | apoe4 0 / 1 / 2 | phase ADNI1 / ADNI2GO | statin 0 / 1 |
|---|---|---:|---:|---:|---:|---:|---:|
| Female | CN | 237 | 73.47 (5.50884) | 15.7384 (2.70575) | 168 / 66 / 3 | 94 / 143 | 145 / 92 |
| Female | MCI | 310 | 71.9277 (7.81451) | 15.4548 (2.74768) | 158 / 117 / 35 | 117 / 193 | 175 / 135 |
| Female | AD | 125 | 73.5624 (7.88453) | 14.464 (2.72546) | 46 / 58 / 21 | 72 / 53 | 76 / 49 |
| Male | CN | 223 | 74.8197 (5.99741) | 17.0897 (2.5874) | 163 / 53 / 7 | 98 / 125 | 113 / 110 |
| Male | MCI | 448 | 73.9257 (7.39195) | 16.2299 (2.83132) | 222 / 178 / 48 | 221 / 227 | 213 / 235 |
| Male | AD | 158 | 75.4392 (7.73803) | 15.7975 (3.06565) | 53 / 70 / 35 | 82 / 76 | 75 / 83 |

## MOTCO's latent-adjustment decisions

Measured at one design (n = 80, the SEA-AD MTG structure, 498 features, eight covariates in nine design columns), none at this one; the arm carries no Type I or power claim of its own (arm rule 8).

- `adopt_stage` (`../MOTCO/docs/reports/latent-adjustment-type-i-2026-10-20.md`): the `stage`-conditioned adjustment holds Type I at the validated design under conditions this change meets: the case study's own proposal justifies the covariate set (`LATENT_SENSITIVITY_COVARIATE_ROLES`), `group_stage` is not used, the record's `latent_adjustment` and `covariates` blocks are reported beside the results, no categorical level is rare enough to drop out of a CV training set, and the earlier binding statements stand; `angle` held the 0.0706 bound by 0.004 (0.067).
- `candidate_fails` (`../MOTCO/docs/reports/latent-adjustment-power-2026-10-20.md`): the adjustment loses `shape` power with a covariate-aligned nuisance axis (0.243 against 0.428) and small-magnitude `delta` power without one (0.400 against 0.520 at e = 0.1), so it is a sensitivity read beside the covariate-blind primary, never a replacement of it.

## Findings

- the arm's CV-selected rank 4 differs from the primary's 8: reported beside angle, not ranked as better or worse (arm rule 3)

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
