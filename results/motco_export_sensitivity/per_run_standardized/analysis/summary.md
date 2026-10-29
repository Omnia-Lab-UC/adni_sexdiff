# MOTCO trajectory analysis: ADNI serum metabolomics, sex × stage — export variant `per_run_standardized`

MOTCO 0.10.0; n = 1501; groups Female vs Male (`sex`); stages CN → MCI → AD (`stage`); blocks p180 (133 features, identity), nmr (165 features, identity); orientation `net_displacement`; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1; latent adjustment: none, as the primary's; export variant `per_run_standardized` (`EXPORT_VARIANTS`, change `adni-nist-bridge`: the p180 values on the scale of EXPORT_FEATURE_RULE (pooled floors, log2(x + floor)), each metabolite centred and divided by its population SD within its run of p180_runs.csv; every other export and analysis setting the primary's; read beside the primary, never replacing it).

## Statistics

| statistic | observed | p (RRPP) | rejected | null mean | null sd | null q95 | note |
|---|---:|---:|:---:|---:|---:|---:|---|
| delta | 1.56843 | 0.0526 | no | 0.643575 | 0.483599 | 1.58117 |  |
| angle | 11.7506 | 0.718 | no | 17.1938 | 8.26608 | 32.7672 | degrees, endpoint stages CN and AD; CV-selected rank 4 (rank floor 2); pooled relative eigengap 0.90948 |
| shape | 0.137403 | 0.6978 | no | 0.204485 | 0.108356 | 0.404777 |  |

Reading, under the rules below:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. In the variant this non-rejection is no more informative than the primary's (variant rule 6).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (variant rule 6).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (variant rule 6).

## Cell sizes

| group | stage CN | stage MCI | stage AD | total |
|---|---:|---:|---:|---:|
| Female | 237 | 310 | 125 | 672 |
| Male | 223 | 448 | 158 | 829 |

## Latent space

- PLS-DA rank: 4 (`cv`); rank floor 2
- pooled relative eigengap of the stage-mean configuration: 0.90948 (permutation null q05 / q50 / q95: 0.725679 / 0.908248 / 0.985986)
- cv_mean_auroc: 0.599812
- CV: cv2_splits 4, cv1_splits 3, n_repeats 5 (5 completed), max_components 20, rank floor 2, random_state 1203
- blocks: p180 (133 features, identity), nmr (165 features, identity); features are z-scored by MOTCO (pooled per-feature scalers)

## Export variant

- variant: `per_run_standardized` (`EXPORT_VARIANTS`, change `adni-nist-bridge`): the p180 values on the scale of EXPORT_FEATURE_RULE (pooled floors, log2(x + floor)), each metabolite centred and divided by its population SD within its run of p180_runs.csv
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the NMR block, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 0.00, |d| > 0.5 for 0 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.00, |corr(PC2, phase)| 0.00
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07

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
- run offset of this export (`phase`, ADNI1 against ADNI2GO; the variant `per_run_standardized` handles the p180 run and the primary's offset is beside it above): p180 median |d| 0.00, |d| > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.00; nmr median |d| 0.21, |d| > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13
- `phase` enters as a covariate of the stage means (above), as in the primary; the variant changes the p180 values only (variant rule 2) and `phase` carries what remains of the run difference

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

## Reading rules of the export variants

Binding for every reader of an export variant (`EXPORT_VARIANT_READING_RULES`, decided by `adni-nist-bridge` before any run), after `READING_RULES`:

1. A variant is read beside the primary and never replaces it. No variant result changes a constant, reruns the primary or adopts a variant.
2. A variant shares with the primary the cleaned tables, the participants, the NMR block, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the p180 values. A rejection status that differs is dependence on the handling of the p180 run, not a result of the variant.
3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
4. `nist_bridge` removes the part of the run offset that NIST SRM 1950 carries, between-run calibration. It assumes the run acts as one factor per metabolite, the same in plasma (NIST) and serum (participants). It leaves what NIST cannot see: a shift common to most metabolites, sample-handling differences between the protocols (the largest residuals are aspartate and glutamate) and the seven unbridged metabolites. `phase` stays a covariate of the stage means and carries what remains.
5. `per_run_standardized` removes each p180 metabolite's whole difference in mean and spread between the runs, whatever its source: calibration, sample handling, and the stage-composition difference the runs carry, since SMC and EMCI were enrolled only in ADNI-GO/2. A difference between it and `nist_bridge` is read as the part of the run difference that is not calibration, never as evidence for either variant.
6. A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in a variant is dependence on the run handling and is read beside the variant's rank and null summary.
7. The variant's export manifest records the run offset per block, and for `nist_bridge` the factor per metabolite; both are reported beside the results. A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.
