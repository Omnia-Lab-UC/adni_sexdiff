# MOTCO export sensitivity: ADNI serum metabolomics, sex × stage — `raw_scale`

The primary analysis (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`) beside the export variant `raw_scale` (`EXPORT_VARIANTS`, change `adni-scale-variants`: both blocks on the raw scale: every kept cell the cleaned concentration as metabo_adni leaves it, in its platform's unit, with no log and no offset (SCALE_VARIANT_RULE); MOTCO's transform identity and its z-scoring; the membership, the participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied; every other export and analysis setting the primary's; `results/motco_export_sensitivity/raw_scale/analysis`, whose `result.json` carries MOTCO's runtime, so its hash is in `export_sensitivity_manifest.json`). MOTCO 0.10.0; n = 1501; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1. The primary row comes first and its status is the result; the variant is read beside it and never replaces it (scale rule 1). A status that differs is dependence on the scale of both blocks, not a result of the variant (scale rule 2). Every value below is read from the two `result.json` records and the variant's export manifest.

## Statistics

| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---:|---:|:---:|---:|---:|---:|---|
| delta | primary | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | same |
| delta | raw_scale | 1.14656 | 0.1182 | no | 0.59083 | 0.449413 | 1.46843 | same |
| angle | primary | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | same |
| angle | raw_scale | 21.9324 | 0.5027 | no | 23.1961 | 8.8407 | 39.5132 | same |
| shape | primary | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | same |
| shape | raw_scale | 0.146317 | 0.6188 | no | 0.188187 | 0.0982987 | 0.368602 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, scale rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); raw_scale rank 7 (floor 2, eigengap 0.642078); the ranks differ, which is reported, not ranked (scale rule 3).

Status per statistic:

- `delta`: same (primary not rejected, raw_scale not rejected). Both are non-rejections; the variant's is no more informative than the primary's (scale rule 6), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, raw_scale not rejected). Both are non-rejections; the variant's is no more informative than the primary's (scale rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, raw_scale not rejected). Both are non-rejections; the variant's is no more informative than the primary's (scale rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

Reading of the variant's statistics, as its `summary.md` prints it:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. In the variant this non-rejection is no more informative than the primary's (scale rule 6).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (scale rule 6).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (scale rule 6).

## Latent space

| quantity | primary | raw_scale |
|---|---:|---:|
| PLS-DA rank (selection) | 8 (`cv`) | 7 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 | 2 |
| cv_mean_auroc | 0.599514 | 0.590378 |
| CV repeats completed | 5 | 5 |
| pooled relative eigengap | 0.74399 | 0.642078 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 | 0.392084 / 0.640432 / 0.807678 |

The two analyses share the cleaned tables, the participants, the membership of both blocks, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations; they differ only in the scale of both blocks (scale rule 2).

## Export variant

- variant: `raw_scale` (`EXPORT_VARIANTS`, change `adni-scale-variants`): both blocks on the raw scale: every kept cell the cleaned concentration as metabo_adni leaves it, in its platform's unit, with no log and no offset (SCALE_VARIANT_RULE); MOTCO's transform identity and its z-scoring; the membership, the participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the membership of both blocks, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- scale (hook `scale`, `SCALE_VARIANT_RULE`): every kept cell of both blocks on `x` in place of the rule's `log2(x + floor)`, with no offset; the primary's membership; the rule's floor computed, gated and recorded per metabolite (the feature tables' `floor`), not applied
- p180 block shape and numerical rank: primary (`log2(x + floor)`) |skew| > 1 for 1 metabolite(s), largest |z| > 8 for 0, numerical rank 133 of 133; variant (`x`) |skew| > 1 for 46 metabolite(s), largest |z| > 8 for 12, numerical rank 133 of 133
- nmr block shape and numerical rank: primary (`log2(x + floor)`) |skew| > 1 for 3 metabolite(s), largest |z| > 8 for 1, numerical rank 165 of 165; variant (`x`) |skew| > 1 for 43 metabolite(s), largest |z| > 8 for 4, numerical rank 104 of 165
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 1.08, |d| > 0.5 for 108 and > 1 for 76 metabolite(s), |corr(PC1, phase)| 0.72, |corr(PC2, phase)| 0.40
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.19, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.06

## Findings

- the variant raw_scale's CV-selected rank 7 differs from the primary's 8: reported beside angle, not ranked (scale rule 3)

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
