# MOTCO trajectory analysis: ADNI serum metabolomics, sex × stage — forced rank 4 (rank sweep)

MOTCO 0.10.0; n = 1501; groups Female vs Male (`sex`); stages CN → MCI → AD (`stage`); blocks p180 (133 features, identity), nmr (165 features, identity); orientation `net_displacement`; 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1; latent adjustment: none, as the primary's; forced rank 4 of the rank sweep `forced_rank_ladder` (`RANK_SENSITIVITY_LADDER`, change `adni-rank-sensitivity`: `forced_components` = 4, which fixes the rank and skips MOTCO's cross-validation; every other export and analysis setting the primary's; read beside the primary, never replacing it).

## Statistics

| statistic | observed | p (RRPP) | rejected | null mean | null sd | null q95 | note |
|---|---:|---:|:---:|---:|---:|---:|---|
| delta | 1.39533 | 0.0733 | no | 0.625204 | 0.473393 | 1.54481 |  |
| angle | 15.7949 | 0.5697 | no | 18.6826 | 9.19451 | 35.8666 | degrees, endpoint stages CN and AD; forced rank 4 (rank floor 2); pooled relative eigengap 0.855065 |
| shape | 0.100385 | 0.8421 | no | 0.217059 | 0.113648 | 0.422741 |  |

Reading, under the rules below:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. At a forced rank this non-rejection is no more informative than the primary's (sweep rule 5).
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). At a forced rank this non-rejection is no more informative than the primary's (sweep rule 5).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). At a forced rank this non-rejection is no more informative than the primary's (sweep rule 5).

## Cell sizes

| group | stage CN | stage MCI | stage AD | total |
|---|---:|---:|---:|---:|
| Female | 237 | 310 | 125 | 672 |
| Male | 223 | 448 | 158 | 829 |

## Latent space

- PLS-DA rank: 4 (`forced`); rank floor 2
- pooled relative eigengap of the stage-mean configuration: 0.855065 (permutation null q05 / q50 / q95: 0.623658 / 0.85543 / 0.973595)
- cv_mean_auroc: n/a
- CV: none (MOTCO skips the cross-validation at a forced rank; 0 repeats completed)
- blocks: p180 (133 features, identity), nmr (165 features, identity); features are z-scored by MOTCO (pooled per-feature scalers)

## Rank sweep

- ladder: `forced_rank_ladder` (`RANK_SENSITIVITY_LADDER`, change `adni-rank-sensitivity`): ranks 2, 3, 4, 6, 9, 12; the one setting `forced_components`; ANALYSIS_SEED and ANALYSIS_PERMUTATIONS at every rank (the same permutation indices at n_jobs = 1)
- this rank: 4, step 3 of 6 of the ladder; the primary's rank 8 is the anchor, not a step of the ladder
- nesting (sweep rule 3): PLS-DA components are nested; at rank 4, below the primary's rank 8 (selected by its cross-validation), the latent space is spanned by the primary's first 4 components; the comparison manifest records the check of every rank's scores against the top rank's and the anchor's
- anchor (sweep rule 3): a forced run at the primary's rank 8 reproduced the primary before any rank ran: `statistics`, `p_values`, `null_summary`, `config_spectrum`, `selected_lv` equal to the primary record's, and `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv` hash to the values the primary manifest records
- loadings: `pls_loadings.csv` (MOTCO's rotations) depends on the rank and is not nested; its columns are this rank's own and are never read against another rank's

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
- `phase` enters as a covariate of the stage means (above), as in the primary; the rank sweep changes the latent rank only (sweep rule 2), and a component above the primary's rank that tracks `phase` is a measurement-space finding (sweep rule 7)

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

## Reading rules of the rank sweep

Binding for every reader of the rank sweep (`RANK_SENSITIVITY_READING_RULES`, decided by `adni-rank-sensitivity` before any run), after `READING_RULES`:

1. The sweep is read beside the primary and never replaces it. The primary's rank is its CV-selected rank (8). No rank of the sweep is chosen, adopted or ranked, and no sweep result changes a constant (`ANALYSIS_RANK_FLOOR` and the ladder included), reruns the primary or defines another arm.
2. Every rank is the primary's analysis with one setting changed: `forced_components`, which fixes the rank and skips MOTCO's cross-validation. The export, the covariates and their coding, the seed, the permutations and every other setting are the primary's, and at `n_jobs = 1` every rank permutes the same residual indices. A difference between ranks is a difference of measurement, not of permutation draws. A rejection status that differs from the primary's is rank dependence, not a result at that rank.
3. PLS-DA components are nested. At a forced rank at or below the primary's 8, the latent space is spanned by the primary's first components; a rank above 8 adds components the cross-validation did not select. The anchor run at rank 8 reproduces the primary's record and files exactly, so the primary row is also the sweep's row at its rank.
4. Each rank's floor, eigengap and `angle` null summary are reported beside its `angle`. The `angle` null depends on the rank, so each `angle` is read against its own null, never against the `angle` of another rank. At rank 2, the floor, `angle` and `shape` are measured in two dimensions (reading rule 2).
5. MOTCO's forced-rank evidence is its Phase 5 rank ladder (2026-09-08; MOTCO 0.6.0, n = 1200, four stages, no covariates): size held at every forced rank, and the ranks above `n_stages − 1` lost `shape` power and gained no `angle` power. No Type I or power check exists at a forced rank at this design or with covariates. A non-rejection at any rank is no more informative than the primary's (reading rule 3), and a rejection at a forced rank only is rank dependence, read beside that rank's null summary.
6. The sweep is not a test. No rule combines the ranks, picks the rank with the smallest p-value or counts the ranks that reject, and the p-values are not adjusted for multiplicity because no decision is taken from them.
7. The axis diagnostic of the top rank (12) is reported beside the sweep. Its components up to the primary's rank are the primary's, with the primary's correlations. A component above it that tracks a variable, `phase` in particular, is a measurement-space finding about the higher ranks and never grounds to choose a rank.
8. The sweep is not crossed with the latent adjustment, an export variant or the CN / LMCI / AD arm, and is read against the primary only. The CV-selected ranks of those analyses are their own selections, and no sentence reads them against the sweep.
