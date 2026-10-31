# MOTCO export sensitivity: ADNI serum metabolomics, sex × stage — `nmr_all_columns`

The primary analysis (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`) beside the export variant `nmr_all_columns` (`EXPORT_VARIANTS`, change `adni-nmr-all-columns`: every cleaned NMR column enters the block (245): the 165 concentrations of EXPORT_FEATURE_RULE and its 80 derived columns (72 percentages, 4 ratios, the degree of unsaturation, 3 sizes), each on the rule's scale, log2(x + floor) with its own 5 % floor over the exported participants; the p180 block, the participants, the metadata and the covariates the primary's; every other export and analysis setting the primary's; `results/motco_export_sensitivity/nmr_all_columns/analysis`, whose `result.json` carries MOTCO's runtime, so its hash is in `export_sensitivity_manifest.json`). MOTCO 0.10.0; n = 1501; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1. The primary row comes first and its status is the result; the variant is read beside it and never replaces it (membership rule 1). A status that differs is dependence on the NMR feature membership, not a result of the variant (membership rule 2). Every value below is read from the two `result.json` records and the variant's export manifest.

## Statistics

| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---:|---:|:---:|---:|---:|---:|---|
| delta | primary | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | differs (feature-membership dependence) |
| delta | nmr_all_columns | 1.53173 | 0.0447 | yes | 0.608253 | 0.462622 | 1.49652 | differs (feature-membership dependence) |
| angle | primary | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | same |
| angle | nmr_all_columns | 15.9469 | 0.6815 | no | 19.9159 | 7.13512 | 32.9005 | same |
| shape | primary | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | same |
| shape | nmr_all_columns | 0.0369556 | 0.9533 | no | 0.155629 | 0.0816776 | 0.30457 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, membership rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); nmr_all_columns rank 7 (floor 2, eigengap 0.724248); the ranks differ, which is reported, not ranked (membership rule 3).

Status per statistic:

- `delta`: differs (feature-membership dependence) (primary not rejected, nmr_all_columns rejected). The variant rejects where the primary does not: dependence on the NMR feature membership, not a result of the variant, read beside the variant's rank and null summary; the primary's non-rejection stays the result (membership rules 2 and 6).
- `angle`: same (primary not rejected, nmr_all_columns not rejected). Both are non-rejections; the variant's is no more informative than the primary's (membership rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, nmr_all_columns not rejected). Both are non-rejections; the variant's is no more informative than the primary's (membership rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

Reading of the variant's statistics, as its `summary.md` prints it:

- `delta` is rejected: evidence that the sexes' trajectories differ, not specifically that they differ in size (reading rule 4). In the variant, a rejection the primary does not make is dependence on the NMR feature membership, not a result of the variant, and is read beside the variant's rank and null summary (membership rules 2 and 6).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (membership rule 6).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (membership rule 6).

## Latent space

| quantity | primary | nmr_all_columns |
|---|---:|---:|
| PLS-DA rank (selection) | 8 (`cv`) | 7 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 | 2 |
| cv_mean_auroc | 0.599514 | 0.608111 |
| CV repeats completed | 5 | 5 |
| pooled relative eigengap | 0.74399 | 0.724248 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 | 0.541156 / 0.718467 / 0.842332 |

The two analyses share the cleaned tables, the participants, the p180 block, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations; they differ only in the NMR block's membership (membership rule 2).

## Export variant

- variant: `nmr_all_columns` (`EXPORT_VARIANTS`, change `adni-nmr-all-columns`): every cleaned NMR column enters the block (245): the 165 concentrations of EXPORT_FEATURE_RULE and its 80 derived columns (72 percentages, 4 ratios, the degree of unsaturation, 3 sizes), each on the rule's scale, log2(x + floor) with its own 5 % floor over the exported participants; the p180 block, the participants, the metadata and the covariates the primary's
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the p180 block, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- nmr membership (hook `membership`): 245 of 245 cleaned column(s), the 165 `EXPORT_FEATURE_RULE` keeps and the derived ones it excludes (percentage 72, ratio 4, degree 1, size 3), each on the rule's scale with its own floor; the rule's columns equal the primary `nmr.csv`'s, column for column and cell for cell: yes
- joint features 378; block shares (unweighted in MOTCO): p180 0.352, nmr 0.648
- nmr block shape on the rule's scale: |skew| > 1 for 24 column(s), largest |z| > 8 for 9
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.20, |d| > 0.5 for 5 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.15, |corr(PC2, phase)| 0.01

## Findings

- the variant nmr_all_columns's CV-selected rank 7 differs from the primary's 8: reported beside angle, not ranked (membership rule 3)
- delta: the variant nmr_all_columns's status (rejected) differs from the primary's (not rejected) at α = 0.05: dependence on the NMR feature membership, not a result of the variant; the primary's status stays the result (membership rules 2 and 6)

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
