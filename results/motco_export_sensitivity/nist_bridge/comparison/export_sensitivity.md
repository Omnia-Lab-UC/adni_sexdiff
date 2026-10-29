# MOTCO export sensitivity: ADNI serum metabolomics, sex × stage — `nist_bridge`

The primary analysis (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`) beside the export variant `nist_bridge` (`EXPORT_VARIANTS`, change `adni-nist-bridge`: every cleaned p180 concentration of a participant whose run in p180_runs.csv is ADNI2GO multiplied by 2^b of its metabolite under NIST_BRIDGE_RULE before the floors; EXPORT_FEATURE_RULE then unchanged, its floors recomputed over the exported participants; every other export and analysis setting the primary's; `results/motco_export_sensitivity/nist_bridge/analysis`, whose `result.json` carries MOTCO's runtime, so its hash is in `export_sensitivity_manifest.json`). MOTCO 0.10.0; n = 1501; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1. The primary row comes first and its status is the result; the variant is read beside it and never replaces it (variant rule 1). A status that differs is dependence on the handling of the p180 run, not a result of the variant (variant rule 2). Every value below is read from the two `result.json` records and the variant's export manifest.

## Statistics

| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---:|---:|:---:|---:|---:|---:|---|
| delta | primary | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | same |
| delta | nist_bridge | 1.08274 | 0.1366 | no | 0.578207 | 0.440758 | 1.42918 | same |
| angle | primary | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | same |
| angle | nist_bridge | 13.6961 | 0.7569 | no | 19.7572 | 8.11592 | 35.0172 | same |
| shape | primary | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | same |
| shape | nist_bridge | 0.0619491 | 0.9048 | no | 0.177528 | 0.0949426 | 0.352329 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, variant rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); nist_bridge rank 6 (floor 2, eigengap 0.795928); the ranks differ, which is reported, not ranked (variant rule 3).

Status per statistic:

- `delta`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

Reading of the variant's statistics, as its `summary.md` prints it:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. In the variant this non-rejection is no more informative than the primary's (variant rule 6).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (variant rule 6).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). In the variant this non-rejection is no more informative than the primary's (variant rule 6).

## Latent space

| quantity | primary | nist_bridge |
|---|---:|---:|
| PLS-DA rank (selection) | 8 (`cv`) | 6 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 | 2 |
| cv_mean_auroc | 0.599514 | 0.598348 |
| CV repeats completed | 5 | 5 |
| pooled relative eigengap | 0.74399 | 0.795928 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 | 0.590906 / 0.784286 / 0.892094 |

The two analyses share the cleaned tables, the participants, the NMR block, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations; they differ only in the p180 values (variant rule 2).

## Export variant

- variant: `nist_bridge` (`EXPORT_VARIANTS`, change `adni-nist-bridge`): every cleaned p180 concentration of a participant whose run in p180_runs.csv is ADNI2GO multiplied by 2^b of its metabolite under NIST_BRIDGE_RULE before the floors; EXPORT_FEATURE_RULE then unchanged, its floors recomputed over the exported participants
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the NMR block, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- NIST SRM 1950 bridge (`NIST_BRIDGE_RULE`): 133 p180 metabolite(s), bridged FIA 102, UPLC 24, not bridged 7 (factor 1: `C0`, `C10.2`, `C12`, `C14.1.OH`, `C6..C4.1.DC.`, `Serotonin`, `Spermidine`); no NIST column: none
- log2 factor b over the bridged metabolites (ADNI1 minus ADNI2GO; ADNI2GO concentrations multiplied by 2^b): q05 / q25 / q50 / q75 / q95 -0.109 / +0.110 / +0.311 / +0.401 / +0.603; median |b| 0.321; b > 0 for 108
- bridge table `bridge/nist_bridge.csv` (sha256 `bcfcf7460a6fb049f89cbe2f39b4c009d1214074fa7e4ab24a3b037b76b87fd3`): per metabolite the replicates, valid replicates, ISTD flags, run means and plate-clustered SEs, b and whether it is bridged
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 0.29, |d| > 0.5 for 35 and > 1 for 8 metabolite(s), |corr(PC1, phase)| 0.22, |corr(PC2, phase)| 0.58
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07

## Findings

- the variant nist_bridge's CV-selected rank 6 differs from the primary's 8: reported beside angle, not ranked (variant rule 3)

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
