# MOTCO trajectory analysis: ADNI serum metabolomics, sex × stage — export variant `glog`

MOTCO 0.10.0; n = 1501; groups Female vs Male (`sex`); stages CN → MCI → AD (`stage`); blocks p180 (133 features, identity), nmr (165 features, identity); orientation `net_displacement`; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1; latent adjustment: none, as the primary's; export variant `glog` (`EXPORT_VARIANTS`, change `adni-scale-variants`: both blocks on the generalized log log2((x + sqrt(x² + λ²)) / 2), λ per metabolite its smallest positive value over the exported participants divided by 10 (SCALE_VARIANT_RULE); the membership, the participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied; every other export and analysis setting the primary's; read beside the primary, never replacing it).

## Statistics

| statistic | observed | p (RRPP) | rejected | null mean | null sd | null q95 | note |
|---|---:|---:|:---:|---:|---:|---:|---|
| delta | 0.866381 | 0.2127 | no | 0.554318 | 0.424536 | 1.37917 |  |
| angle | 14.8403 | 0.7251 | no | 20.0932 | 7.78637 | 34.6898 | degrees, endpoint stages CN and AD; CV-selected rank 7 (rank floor 2); pooled relative eigengap 0.771284 |
| shape | 0.0967987 | 0.7625 | no | 0.166509 | 0.0885219 | 0.32886 |  |

Reading, under the rules below:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. In the variant this non-rejection is no more informative than the primary's (scale rule 6).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (scale rule 6).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (scale rule 6).

## Cell sizes

| group | stage CN | stage MCI | stage AD | total |
|---|---:|---:|---:|---:|
| Female | 237 | 310 | 125 | 672 |
| Male | 223 | 448 | 158 | 829 |

## Latent space

- PLS-DA rank: 7 (`cv`); rank floor 2
- pooled relative eigengap of the stage-mean configuration: 0.771284 (permutation null q05 / q50 / q95: 0.567676 / 0.75973 / 0.874489)
- cv_mean_auroc: 0.603179
- CV: cv2_splits 4, cv1_splits 3, n_repeats 5 (5 completed), max_components 20, rank floor 2, random_state 1203
- blocks: p180 (133 features, identity), nmr (165 features, identity); features are z-scored by MOTCO (pooled per-feature scalers)

## Export variant

- variant: `glog` (`EXPORT_VARIANTS`, change `adni-scale-variants`): both blocks on the generalized log log2((x + sqrt(x² + λ²)) / 2), λ per metabolite its smallest positive value over the exported participants divided by 10 (SCALE_VARIANT_RULE); the membership, the participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the membership of both blocks, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- scale (hook `scale`, `SCALE_VARIANT_RULE`): every kept cell of both blocks on `log2((x + sqrt(x² + λ²)) / 2)` in place of the rule's `log2(x + floor)`, λ per metabolite its smallest positive value over the exported participants divided by 10 (the feature tables' `offset`), so a zero cell lands at `log2(λ / 2)`; the primary's membership; the rule's floor computed, gated and recorded per metabolite (the feature tables' `floor`), not applied
- λ over the metabolite's median, q05 / q25 / q50 / q75 / q95: p180 0.00499 / 0.0254 / 0.0335 / 0.0394 / 0.0493; nmr 0.0001 / 0.00893 / 0.035 / 0.0477 / 0.0596
- p180 block shape and numerical rank: primary (`log2(x + floor)`) |skew| > 1 for 1 metabolite(s), largest |z| > 8 for 0, numerical rank 133 of 133; variant (`log2((x + sqrt(x² + λ²)) / 2)`) |skew| > 1 for 6 metabolite(s), largest |z| > 8 for 6, numerical rank 133 of 133
- nmr block shape and numerical rank: primary (`log2(x + floor)`) |skew| > 1 for 3 metabolite(s), largest |z| > 8 for 1, numerical rank 165 of 165; variant (`log2((x + sqrt(x² + λ²)) / 2)`) |skew| > 1 for 25 metabolite(s), largest |z| > 8 for 13, numerical rank 165 of 165
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 1.13, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.08

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

- feature rule (`EXPORT_FEATURE_RULE`, its scale replaced by the variant's, `SCALE_VARIANT_RULE`; the rule's floors recorded, not applied): units `log2((x + sqrt(x² + λ²)) / 2)`, MOTCO transform `identity`; kept / cleaned columns: p180 133 / 133, nmr 165 / 245; joint features 298
- block shares (unweighted in MOTCO): p180 0.446, nmr 0.554
- run offset of this export (`phase`, ADNI1 against ADNI2GO; the variant `glog` changes the scale of both blocks and the primary's offset is beside it above): p180 median |d| 1.13, |d| > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73; nmr median |d| 0.21, |d| > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13
- `phase` enters as a covariate of the stage means (above), as in the primary; the variant changes the scale of both blocks only (scale rule 2) and `phase` carries the run difference, as in the primary

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
