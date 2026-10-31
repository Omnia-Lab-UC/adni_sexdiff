# MOTCO trajectory analysis: ADNI serum metabolomics, sex × stage — export variant `nmr_all_columns`

MOTCO 0.10.0; n = 1501; groups Female vs Male (`sex`); stages CN → MCI → AD (`stage`); blocks p180 (133 features, identity), nmr (245 features, identity); orientation `net_displacement`; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1; latent adjustment: none, as the primary's; export variant `nmr_all_columns` (`EXPORT_VARIANTS`, change `adni-nmr-all-columns`: every cleaned NMR column enters the block (245): the 165 concentrations of EXPORT_FEATURE_RULE and its 80 derived columns (72 percentages, 4 ratios, the degree of unsaturation, 3 sizes), each on the rule's scale, log2(x + floor) with its own 5 % floor over the exported participants; the p180 block, the participants, the metadata and the covariates the primary's; every other export and analysis setting the primary's; read beside the primary, never replacing it).

## Statistics

| statistic | observed | p (RRPP) | rejected | null mean | null sd | null q95 | note |
|---|---:|---:|:---:|---:|---:|---:|---|
| delta | 1.53173 | 0.0447 | yes | 0.608253 | 0.462622 | 1.49652 |  |
| angle | 15.9469 | 0.6815 | no | 19.9159 | 7.13512 | 32.9005 | degrees, endpoint stages CN and AD; CV-selected rank 7 (rank floor 2); pooled relative eigengap 0.724248 |
| shape | 0.0369556 | 0.9533 | no | 0.155629 | 0.0816776 | 0.30457 |  |

Reading, under the rules below:

- `delta` is rejected: evidence that the sexes' trajectories differ, not specifically that they differ in size (reading rule 4). In the variant, a rejection the primary does not make is dependence on the NMR feature membership, not a result of the variant, and is read beside the variant's rank and null summary (membership rules 2 and 6).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (membership rule 6).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (membership rule 6).

## Cell sizes

| group | stage CN | stage MCI | stage AD | total |
|---|---:|---:|---:|---:|
| Female | 237 | 310 | 125 | 672 |
| Male | 223 | 448 | 158 | 829 |

## Latent space

- PLS-DA rank: 7 (`cv`); rank floor 2
- pooled relative eigengap of the stage-mean configuration: 0.724248 (permutation null q05 / q50 / q95: 0.541156 / 0.718467 / 0.842332)
- cv_mean_auroc: 0.608111
- CV: cv2_splits 4, cv1_splits 3, n_repeats 5 (5 completed), max_components 20, rank floor 2, random_state 1203
- blocks: p180 (133 features, identity), nmr (245 features, identity); features are z-scored by MOTCO (pooled per-feature scalers)

## Export variant

- variant: `nmr_all_columns` (`EXPORT_VARIANTS`, change `adni-nmr-all-columns`): every cleaned NMR column enters the block (245): the 165 concentrations of EXPORT_FEATURE_RULE and its 80 derived columns (72 percentages, 4 ratios, the degree of unsaturation, 3 sizes), each on the rule's scale, log2(x + floor) with its own 5 % floor over the exported participants; the p180 block, the participants, the metadata and the covariates the primary's
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the p180 block, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- nmr membership (hook `membership`): 245 of 245 cleaned column(s), the 165 `EXPORT_FEATURE_RULE` keeps and the derived ones it excludes (percentage 72, ratio 4, degree 1, size 3), each on the rule's scale with its own floor; the rule's columns equal the primary `nmr.csv`'s, column for column and cell for cell: yes
- joint features 378; block shares (unweighted in MOTCO): p180 0.352, nmr 0.648
- nmr block shape on the rule's scale: |skew| > 1 for 24 column(s), largest |z| > 8 for 9
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.20, |d| > 0.5 for 5 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.15, |corr(PC2, phase)| 0.01

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

- feature rule (`EXPORT_FEATURE_RULE`): units `log2(x + floor)`, MOTCO transform `identity`; kept / cleaned columns: p180 133 / 133, nmr 245 / 245; joint features 378
- block shares (unweighted in MOTCO): p180 0.352, nmr 0.648
- run offset of this export (`phase`, ADNI1 against ADNI2GO; the variant `nmr_all_columns` changes the NMR block's membership and the primary's offset is beside it above): p180 median |d| 1.12, |d| > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73; nmr median |d| 0.20, |d| > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.15
- `phase` enters as a covariate of the stage means (above), as in the primary; the variant changes the NMR membership only (membership rule 2) and `phase` carries the run difference, as in the primary

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
