# MOTCO rank sensitivity: ADNI serum metabolomics, sex × stage — forced-rank ladder `forced_rank_ladder`

The primary analysis (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`, rank 8 selected by its cross-validation) beside the rank sweep `forced_rank_ladder` (`RANK_SENSITIVITY_LADDER`, change `adni-rank-sensitivity`: the primary's analysis at each forced rank 2, 3, 4, 6, 9, 12, `forced_components` set to the rank and MOTCO's cross-validation skipped; every other export and analysis setting the primary's; the ranks' `result.json` carry MOTCO's runtime, so their hashes are in `rank_sensitivity_manifest.json`). MOTCO 0.10.0; n = 1501; 9999 RRPP permutations, seed 20261027 at every rank; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`); n_jobs 1. The primary row comes first and its status is the result; the sweep is read beside it and never replaces it, and no rank is chosen, adopted or ranked (sweep rule 1). A status that differs is rank dependence, not a result at that rank (sweep rule 2). Every value below is read from the `result.json` records.

## Statistics

| statistic | analysis | rank | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---:|---:|---:|:---:|---:|---:|---:|---|
| delta | primary | 8 | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | the result |
| delta | rank_02 | 2 | 0.420321 | 0.5533 | no | 0.5673 | 0.432413 | 1.41925 | same |
| delta | rank_03 | 3 | 1.11394 | 0.1738 | no | 0.65331 | 0.496403 | 1.61969 | same |
| delta | rank_04 | 4 | 1.39533 | 0.0733 | no | 0.625204 | 0.473393 | 1.54481 | same |
| delta | rank_06 | 6 | 1.47416 | 0.0471 | yes | 0.588079 | 0.448457 | 1.4559 | differs (rank dependence) |
| delta | rank_09 | 9 | 1.09596 | 0.1075 | no | 0.544619 | 0.417074 | 1.35327 | same |
| delta | rank_12 | 12 | 1.03295 | 0.1212 | no | 0.528433 | 0.404963 | 1.31475 | same |
| angle | primary | 8 | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | the result |
| angle | rank_02 | 2 | 22.6908 | 0.2758 | no | 16.9253 | 13.7439 | 43.8281 | same |
| angle | rank_03 | 3 | 17.6075 | 0.5433 | no | 20.6092 | 11.5362 | 42.3304 | same |
| angle | rank_04 | 4 | 15.7949 | 0.5697 | no | 18.6826 | 9.19451 | 35.8666 | same |
| angle | rank_06 | 6 | 15.6791 | 0.6699 | no | 20.0422 | 8.12314 | 35.2676 | same |
| angle | rank_09 | 9 | 17.4837 | 0.6483 | no | 21.1156 | 7.47377 | 35.2639 | same |
| angle | rank_12 | 12 | 17.4224 | 0.7098 | no | 21.86 | 7.11026 | 35.2757 | same |
| shape | primary | 8 | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | the result |
| shape | rank_02 | 2 | 0.328201 | 0.4099 | no | 0.311314 | 0.174015 | 0.635071 | same |
| shape | rank_03 | 3 | 0.111223 | 0.8699 | no | 0.262765 | 0.136359 | 0.509008 | same |
| shape | rank_04 | 4 | 0.100385 | 0.8421 | no | 0.217059 | 0.113648 | 0.422741 | same |
| shape | rank_06 | 6 | 0.10303 | 0.7848 | no | 0.185851 | 0.0977856 | 0.363261 | same |
| shape | rank_09 | 9 | 0.0964967 | 0.7442 | no | 0.159265 | 0.0844137 | 0.313163 | same |
| shape | rank_12 | 12 | 0.101355 | 0.6914 | no | 0.149891 | 0.0796311 | 0.295945 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' rank, floor (2), eigengap and its own null summary (reading rule 2, sweep rule 4; the latent spaces below), never against the `angle` of another rank.

Status per statistic:

- `delta`: differs (rank dependence) at rank 6, same at ranks 2, 3, 4, 9 and 12 (primary not rejected; rank 6 rejected). A rejection at a forced rank only is rank dependence, not a result at that rank, read beside that rank's null summary; the primary's non-rejection stays the result, and no rule counts the ranks that reject (sweep rules 2, 5 and 6).
- `angle`: same at every rank (primary not rejected; ranks 2, 3, 4, 6, 9 and 12 not rejected). No forced rank rejects where the primary does not; each non-rejection is no more informative than the primary's (sweep rule 5), and none is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same at every rank (primary not rejected; ranks 2, 3, 4, 6, 9 and 12 not rejected). No forced rank rejects where the primary does not; each non-rejection is no more informative than the primary's (sweep rule 5), and none is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

Reading of each rank's statistics, as its `summary.md` prints it:

- ranks 2, 3, 4, 9 and 12: `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design. At a forced rank this non-rejection is no more informative than the primary's (sweep rule 5).
- rank 6: `delta` is rejected: evidence that the sexes' trajectories differ, not specifically that they differ in size (reading rule 4). At a forced rank, a rejection the primary does not make is rank dependence, not a result at that rank, and is read beside the rank's null summary (sweep rules 2 and 5).
- ranks 2, 3, 4, 6, 9 and 12: `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design). At a forced rank this non-rejection is no more informative than the primary's (sweep rule 5).
- ranks 2, 3, 4, 6, 9 and 12: `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design). At a forced rank this non-rejection is no more informative than the primary's (sweep rule 5).

## Latent spaces

| analysis | rank (selection) | rank floor | cv_mean_auroc | CV repeats completed | pooled relative eigengap | eigengap null q05 / q50 / q95 | `angle` null mean / sd / q95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 8 (`cv`) | 2 | 0.599514 | 5 | 0.74399 | 0.537295 / 0.733669 / 0.855842 | 20.9569 / 7.64839 / 35.4399 |
| rank_02 | 2 (`forced`) | 2 | n/a | 0 | 0.950651 | 0.669597 / 0.943226 / 0.999451 | 16.9253 / 13.7439 / 43.8281 |
| rank_03 | 3 (`forced`) | 2 | n/a | 0 | 0.79401 | 0.501316 / 0.806123 / 0.971406 | 20.6092 / 11.5362 / 42.3304 |
| rank_04 | 4 (`forced`) | 2 | n/a | 0 | 0.855065 | 0.623658 / 0.85543 / 0.973595 | 18.6826 / 9.19451 / 35.8666 |
| rank_06 | 6 (`forced`) | 2 | n/a | 0 | 0.817558 | 0.607526 / 0.813909 / 0.932891 | 20.0422 / 8.12314 / 35.2676 |
| rank_09 | 9 (`forced`) | 2 | n/a | 0 | 0.736135 | 0.536443 / 0.726856 / 0.845439 | 21.1156 / 7.47377 / 35.2639 |
| rank_12 | 12 (`forced`) | 2 | n/a | 0 | 0.703784 | 0.509229 / 0.692041 / 0.810128 | 21.86 / 7.11026 / 35.2757 |

The ranks share the primary export, the covariates and their design, the cells, the seed and the permutations; at n_jobs = 1 every rank permutes the same residual indices (sweep rule 2). They differ only in the latent rank: MOTCO skips the cross-validation at a forced rank, so `cv_mean_auroc` is not available and no CV repeat runs. Each rank's `pls_loadings.csv` (MOTCO's rotations) is its own and is not nested.

## Anchor and nesting

- anchor (sweep rule 3): a forced run at the primary's rank 8 reproduced the primary before any rank ran: `statistics`, `p_values`, `null_summary`, `config_spectrum`, `selected_lv` equal to the primary record's, and `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv` hash to the values the primary manifest records; its directory was removed. Predeclared anchor rank 8 (`RANK_SENSITIVITY_EXPECTED_COUNTS`); the primary record's 8.
- nesting (sweep rule 3): PLS-DA components are nested, so each rank's latent scores are the first columns of rank 12's, and the ranks at or below the primary's 8 are the primary's first components (through the anchor, equal to the primary by the gate). The check compares the scores in memory; no score is printed or written by it.

| rank | first columns of rank 12's | columns compared with the anchor's | equal to the anchor's |
|---|:---:|---:|:---:|
| rank_02 | yes | 2 | yes |
| rank_03 | yes | 3 | yes |
| rank_04 | yes | 4 | yes |
| rank_06 | yes | 6 | yes |
| rank_09 | yes | 8 | yes |
| rank_12 | yes | 8 | yes |

## Findings

- delta: forced rank 6's status (rejected) differs from the primary's (not rejected) at α = 0.05: rank dependence, not a result at that rank; the primary's status stays the result (sweep rules 1 and 2)

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
