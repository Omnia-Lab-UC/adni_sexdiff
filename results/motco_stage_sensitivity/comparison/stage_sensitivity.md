# MOTCO stage sensitivity: ADNI serum metabolomics, sex × stage — CN / LMCI / AD arm `cn_lmci_ad`

The primary analysis (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`) beside the CN / LMCI / AD arm `cn_lmci_ad` (`STAGE_SENSITIVITY_ARM`, change `adni-stage-sensitivity`: the primary export's rows of the participants whose `DX.bl` is CN, LMCI or AD, staged by `STAGE_RULE`'s map (CN → CN, LMCI → MCI, AD → AD), SMC and EMCI dropped; every other export and analysis setting the primary's; `results/motco_stage_sensitivity/analysis`, whose `result.json` carries MOTCO's runtime, so its hash is in `stage_sensitivity_manifest.json`). MOTCO 0.10.0; n = 1501 (primary) and 1130 (arm); 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1. The primary row comes first and its status is the result; the arm is read beside it and never replaces it (stage-arm rule 1). A status that differs is dependence on the stage definition and the sample, not a result of the arm (stage-arm rule 2). Every value below is read from the two `result.json` records and the arm's export manifest.

## Statistics

| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---:|---:|:---:|---:|---:|---:|---|
| delta | primary | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | same |
| delta | cn_lmci_ad | 0.882188 | 0.188 | no | 0.532328 | 0.4092 | 1.31619 | same |
| angle | primary | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | same |
| angle | cn_lmci_ad | 20.7602 | 0.5702 | no | 23.362 | 8.70311 | 39.0413 | same |
| shape | primary | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | same |
| shape | cn_lmci_ad | 0.0251113 | 0.9853 | no | 0.188005 | 0.0982976 | 0.365394 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, stage-arm rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); cn_lmci_ad rank 6 (floor 2, eigengap 0.863574); the ranks differ, which is reported, not ranked (stage-arm rule 3).

Status per statistic:

- `delta`: same (primary not rejected, cn_lmci_ad not rejected). Both are non-rejections; the arm's is no more informative than the primary's (stage-arm rule 6), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, cn_lmci_ad not rejected). Both are non-rejections; the arm's is no more informative than the primary's (stage-arm rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, cn_lmci_ad not rejected). Both are non-rejections; the arm's is no more informative than the primary's (stage-arm rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

Reading of the arm's statistics, as its `summary.md` prints it:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. In the CN / LMCI / AD arm this non-rejection is no more informative than the primary's (stage-arm rule 6).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the CN / LMCI / AD arm this non-rejection is no more informative than the primary's (stage-arm rule 6).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the CN / LMCI / AD arm this non-rejection is no more informative than the primary's (stage-arm rule 6).

## Latent space

| quantity | primary | cn_lmci_ad |
|---|---:|---:|
| participants | 1501 | 1130 |
| PLS-DA rank (selection) | 8 (`cv`) | 6 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 | 2 |
| cv_mean_auroc | 0.599514 | 0.616134 |
| CV repeats completed | 5 | 5 |
| pooled relative eigengap | 0.74399 | 0.863574 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 | 0.637366 / 0.828369 / 0.944751 |

The two analyses share the primary export's cells of the kept participants, the covariates and their coding and every setting; they differ in the participants (SMC and EMCI dropped), and so in their z-scoring, CV folds, latent basis, rank, covariate reference row and permutation draws (stage-arm rule 2).

## Arm

- arm: `cn_lmci_ad` (`STAGE_SENSITIVITY_ARM`, change `adni-stage-sensitivity`): the primary export's rows of the participants whose `DX.bl` is CN, LMCI or AD, staged by `STAGE_RULE`'s map (CN → CN, LMCI → MCI, AD → AD), SMC and EMCI dropped
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`): the arm's rows are its rows, every cell unchanged, so the floors are the primary's (`features_nmr.csv` sha256 `d4495f6aae38985460a118582e8e3250f9c56b8e27fc38d64bedc5b14514b9ee`, `features_p180.csv` sha256 `7793776534d580f9a49e0ad95e0d8f6ecef3b5a7ff3c02f64dd07c905f4bb5ee`); rows equal to the primary's: p180.csv yes, nmr.csv yes, metadata.csv yes, covariates.csv yes
- participants: 1130 of the primary's 1501; dropped: SMC 96, EMCI 275

Exported participants by `dx_bl` (`STAGE_RULE` maps it onto the stage):

| `dx_bl` | stage | in the arm | Female | Male | total |
|---|---|:---:|---:|---:|---:|
| CN | CN | yes | 183 | 181 | 364 |
| SMC | CN | no | 54 | 42 | 96 |
| EMCI | MCI | no | 123 | 152 | 275 |
| LMCI | MCI | yes | 187 | 296 | 483 |
| AD | AD | yes | 125 | 158 | 283 |

Sex × stage cells:

| sex | CN primary | MCI primary | AD primary | CN arm | MCI arm | AD arm |
|---|---:|---:|---:|---:|---:|---:|
| Female | 237 | 310 | 125 | 183 | 187 | 125 |
| Male | 223 | 448 | 158 | 181 | 296 | 158 |

Runs within each stage (`phase`):

| stage | ADNI1 primary | ADNI2GO primary | ADNI1 arm | ADNI2GO arm |
|---|---:|---:|---:|---:|
| CN | 192 | 268 | 192 | 172 |
| MCI | 338 | 420 | 338 | 145 |
| AD | 154 | 129 | 154 | 129 |

Covariate levels:

| covariate | level | primary | arm |
|---|---|---:|---:|
| `apoe4` | 0 | 810 | 589 |
| `apoe4` | 1 | 542 | 413 |
| `apoe4` | 2 | 149 | 128 |
| `phase` | ADNI1 | 684 | 684 |
| `phase` | ADNI2GO | 817 | 446 |
| `statin` | 0 | 797 | 603 |
| `statin` | 1 | 704 | 527 |

- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; arm median |d| 1.10, |d| > 0.5 for 107 and > 1 for 77 metabolite(s), |corr(PC1, phase)| 0.71, |corr(PC2, phase)| 0.42
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; arm median |d| 0.26, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.15, |corr(PC2, phase)| 0.11

## Findings

- the arm cn_lmci_ad's CV-selected rank 6 differs from the primary's 8: reported beside angle, not ranked (stage-arm rule 3)

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
