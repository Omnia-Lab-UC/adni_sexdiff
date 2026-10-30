# Proposal

## Why

Since `adni-export`, four more export variants have been named, to be registered after the primary analysis: all 245 NMR columns, the raw scale, `log2(x + 1)` and the generalized log. Every other predeclared sensitivity has run and is in the report: the latent arm, the two p180 run variants, the CN / LMCI / AD arm and the rank sweep. This change registers the first of the four, `nmr_all_columns`, and runs it. The three scale variants change the scale of both blocks, so they form one later change.

`EXPORT_FEATURE_RULE` keeps the 165 NMR concentrations and excludes the 80 columns that are functions of them, with status `derived`: 72 percentages, 4 ratios, the degree of unsaturation and 3 particle sizes. The rule's reason is that these columns add weight to the block, not measurement. The 2022 study (doi:10.3389/fradi.2022.782864) used all 245 columns. Because MOTCO 0.10.0 z-scores every feature and weights features, not blocks, membership sets how much the lipoprotein directions weigh in the joint matrix. This variant measures whether the three statuses depend on that one decision.

The spike of this change (`spike.md`, `scripts/spike_nmr_all_columns.py`, nixos-office, 2026-10-30) is read-only and aggregate. It read the cleaned NMR table and the primary export, each checked against its manifest. It read no MOTCO output, no metadata and no sex or stage. Its findings:
- **The rule applies to all 80 columns as it is.** They hold 0 zero cells, every floor is positive and every transformed cell is finite.
- **The 165 concentrations are the primary's.** Their floors, their order and every cell are bitwise equal to the primary `nmr.csv`'s. The variant only adds columns.
- **The 80 columns add no measurement.** On the rule's scale, a least-squares fit on the 165 concentrations explains a median 0.998 of a derived column's variance. The lowest are `XL_VLDL_C_PCT` at 0.798 and `XL_VLDL_CE_PCT` at 0.830.
- **They add left tails.** On the rule's scale, 21 of the 80 have |skew| > 1 and 8 have a largest |z| above 8. All of them are percentages, the largest being those of the large HDL and VLDL lipids (`L_HDL_PL_PCT` −6.96). On the raw scale, 29 have |skew| > 1. So the rule's scale is not worse than raw by that count, but MOTCO's z-scoring gives these tails leverage. The variant's NMR block has 24 columns with |skew| > 1 and 9 with |z| > 8, against 3 and 1 in the primary's.
- **Block weight moves; the run offset barely does.**
  - The p180 share of the joint features falls from 133 / 298 (0.446) to 133 / 378 (0.352).
  - The NMR block's PC1 share falls from 0.438 to 0.335, and its effective rank rises from 3.77 to 4.96. Its numerical rank is full (245).
  - NMR phase |d| > 0.5 goes from 2 to 5 columns, and > 1 stays at 0. PC1's correlation with phase is 0.135 → 0.148.
  - On the standardized joint matrix, PC1's correlation with phase is 0.415 → 0.400. This is descriptive, not MOTCO's supervised basis.
- **The CV folds and the RRPP draws are the primary's.** In MOTCO 0.10.0 the folds are `RepeatedStratifiedKFold(random_state)` on the stage labels, and the draws are `rng.permutation(n)` from the seed. Neither reads the features.

No setting below comes from a sex × stage result.

## What Changes

- **A third export variant, `nmr_all_columns`**, run by the existing `export-sensitivity` step (`--variant nmr_all_columns`) through its shared export body, a new hook `membership` and the shared analysis body.
  - **Export:** every cleaned NMR column enters the block, in cleaned order, each on `EXPORT_FEATURE_RULE`'s scale (`log2(x + floor)`, its own 5 % floor over the exported participants). The p180 block, the participants, the metadata and the covariates are the primary's. The data root is not read.
  - **Analysis:** one `analyze_trajectories` call at the primary's settings.
  - **Comparison:** the variant's statistics beside the primary's.
- **Scientific constants**, proposed here and decided by the user when the proposal is accepted, before any run:
  - **`EXPORT_VARIANTS["nmr_all_columns"]`**: block `nmr`, hook `membership`, no rule, no data root. The setting: "every cleaned NMR column enters the block (245): the 165 concentrations of EXPORT_FEATURE_RULE and its 80 derived columns (72 percentages, 4 ratios, the degree of unsaturation, 3 sizes), each on the rule's scale, log2(x + floor) with its own 5 % floor over the exported participants; the p180 block, the participants, the metadata and the covariates the primary's". Change `adni-nmr-all-columns`. The two existing entries are not touched: no key is added, so their recorded `variant` blocks stay equal to the registry.
  - **`NMR_MEMBERSHIP_READING_RULES`**: eight statements, printed verbatim after `READING_RULES` in the variant's `summary.md`, its `export_sensitivity.md`, its `diagnostics.md` and every report that quotes it. It is printed in place of `EXPORT_VARIANT_READING_RULES`, whose rule 2 ("It differs only in the p180 values") does not hold for this variant. Cited as "membership rule N".
    1. `nmr_all_columns` is read beside the primary and never replaces it. No result of it changes a constant (`EXPORT_FEATURE_RULE` included), reruns the primary or adopts the variant.
    2. The variant shares a great deal with the primary: the cleaned tables, the participants, the p180 block, the 165 NMR concentrations with their floors and cells, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the NMR block's membership. It adds the 80 columns `EXPORT_FEATURE_RULE` marks `derived`, so the joint matrix holds 378 features, and the p180 share falls from 133 / 298 (0.446) to 133 / 378 (0.352). A rejection status that differs is dependence on the feature membership, not a result of the variant.
    3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
    4. The 80 columns add no measurement. Each is a function of the block's concentrations: a lipid's share of its lipoprotein subclass (72 percentages), a ratio (4), the degree of unsaturation, or a particle size (3). On the rule's scale the 165 concentrations explain a median 0.998 of a derived column's variance (lowest 0.798). MOTCO z-scores every feature and weights features, not blocks, so the columns add weight to the lipoprotein directions they are computed from. On the rule's scale, 21 of them have |skew| > 1 and 8 a largest |z| above 8, mostly percentages of the large HDL and VLDL lipids. A difference reflects the weight of those directions and those tails, never evidence that the derived columns measure what the concentrations do not.
    5. The 2022 study (doi:10.3389/fradi.2022.782864) used all 245 NMR columns, with `log2(x + 1)`, winsorizing, outlier removal and medication residuals. The variant changes the membership only, on the rule's scale. It is not a reproduction of that study, and no agreement or disagreement with it is read from the variant.
    6. A non-rejection in the variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in the variant is dependence on the feature membership, read beside the variant's rank and null summary.
    7. The variant's export manifest records the block shares, the NMR block's shape counts and the run offset per block. Its axis diagnostic records each block's loading share per component (`components.csv`). They are reported beside the results. A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.
    8. The variant is read against the primary only, never against another export variant, arm or rank. No sentence reads it against another sensitivity.

    Rules 1, 2, 3, 6 and 7 have the roles of `EXPORT_VARIANT_READING_RULES` 1, 2, 3, 6 and 7, so a sentence that cites a rule by its role cites the same number under both sets.
  - **The dependence label** of the variant: `differs (feature-membership dependence)`. The two p180 variants keep `differs (run-handling dependence)`.
- **Predeclared counts** (`EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]`, from the spike and the committed manifests, none from a run of the variant; a deviation is a finding, never a stop):

  | quantity | value |
  |---|---|
  | participants; sex × stage | 1501; the primary's cells |
  | p180 features | cleaned 133, kept 133 (the primary's) |
  | NMR features | cleaned 245, kept 245, excluded as derived 0; derived kept: percentage 72, ratio 4, degree 1, size 3 |
  | joint features | 378 |
  | zero cells / metabolites with zeros | p180 0 / 0; NMR 41 / 3 |
  | floors not positive; non-finite cells | 0; 0, per block |
  | NMR shape | \|skew\| > 1: 24; largest \|z\| > 8: 9 |
  | run offset, metabolites with phase \|d\| > 0.5 / > 1 | p180 109 / 80 (the primary's); NMR 5 / 0 |
  | participants whose run differs from `phase` | 0 |
  | files equal to the primary's | `p180.csv`, `metadata.csv`, `covariates.csv` |
  | the 165 concentration columns' cells equal to the primary `nmr.csv`'s | yes |
  | missing covariate values | 0 |
  | analysis | every key of `ANALYSIS_EXPECTED_COUNTS`, with features p180 133, NMR 245, joint 378 |
  | diagnostics | the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS`, with 245 NMR features |

  The rank is not predeclared.
- **The variant code reads each variant's rule set.** A convention `EXPORT_VARIANT_RULE_SETS` names, per variant, its rule set, its citation word and its dependence label. An import-time assertion ties its keys to `EXPORT_VARIANTS`. The sentences and headings that today hold p180 wording are written from it: `summary.md`, `export_sensitivity.md`, the comparison findings and a variant's `diagnostics.md`. The two p180 variants keep their committed bytes: every one of their text outputs, re-rendered from its committed records, must equal the committed file.
- **`axis-diagnostics` takes a variant's own expected counts** when the variant predeclares them (`EXPORT_VARIANT_EXPECTED_COUNTS[<variant>]["diagnostics"]`, this variant only). Otherwise it keeps today's rank-independent keys, so the two p180 variants' diagnostics are unchanged.
- **The report is pinned to the variants it covers.** A convention `REPORT_EXPORT_VARIANTS = ("nist_bridge", "per_run_standardized")` replaces `EXPORT_VARIANTS` wherever `report` reads or names a variant (its inputs, gates, chain and sections). An import-time assertion keeps it a subsequence of the registry. The report's body is unchanged. After this change the newest committed report (written by `adni-report-rank-sweep`) must still pass `report --check` with no mismatch. A registered variant outside the pin is named on a progress line, never in the report body.
- **Outputs** under `results/motco_export_sensitivity/nmr_all_columns/`, laid out as the other variants' without `bridge/`:
  - `motco_input/`: the four CSVs and the two feature tables (participant-level or gitignored, matched by the existing `results/motco_export_sensitivity/*/motco_input/*.csv`), and `manifest.json`;
  - `analysis/`: the seven files `analyze` writes;
  - `comparison/`: `export_sensitivity.csv`, `export_sensitivity.md` and `export_sensitivity_manifest.json`;
  - `diagnostics/`: written by `axis-diagnostics --input-dir results/motco_export_sensitivity/nmr_all_columns/motco_input --analysis-dir results/motco_export_sensitivity/nmr_all_columns/analysis --out-dir results/motco_export_sensitivity/nmr_all_columns/diagnostics`, run in this change.

  No new participant-level pattern is needed. `analysis/latent_scores.csv` and `analysis/analysis_metadata.csv` are already matched.
- **Docs:**
  - `README.md`: the `export-sensitivity` section gains the variant, its hook, its rules and its counts.
  - `AGENTS.md`: the status; the `export-sensitivity` entry; "Flag and ask" with the entry, the rule set and the counts; the Layout.
  - The `constants.py` docstring and the step docstrings.

Out of scope, each its own change:
- **The report.** A later change adds `nmr_all_columns` to `REPORT_EXPORT_VARIANTS` and its rule set to the reading-rules section. It also extends `report --check`'s earlier-layout gate to the variants a report lists, and re-issues the report. Until then the committed report stays valid.
- **The scale variants:** the raw scale, `log2(x + 1)` and the generalized log, one later change.
- **Other memberships:** a subset of the derived families (percentages only, say), another scale for the derived columns, and a 2022-like export that combines membership and scale.
- **Crossings:** the variant under the latent adjustment, the CN / LMCI / AD arm, the rank sweep or another export variant.
- **Model terms:** block weighting, and any change to `EXPORT_FEATURE_RULE` or the primary.
- **Pin and cluster:** a MOTCO pin move, and the cluster run (constraint 7).

No variant result changes a constant, selects a metabolite, reruns the primary or replaces it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities
- `motco-export-sensitivity`:
  - the registry gains `nmr_all_columns`;
  - a requirement for the NMR membership export;
  - the unchanged-files rule names the blocks a variant does not change;
  - the 165 columns equal to the primary's;
  - the comparison summary, the predeclared counts, the findings and the reading rules take each variant's rule set and label;
  - the two p180 variants' text outputs are unchanged.
- `latent-axis-diagnostic`:
  - "Reading rules of a sensitivity read" prints each variant's own rule set;
  - a requirement for a variant's own expected counts.
- `case-study-report`:
  - "Inputs are the kept aggregate outputs only" reads the variants of `REPORT_EXPORT_VARIANTS`;
  - a requirement that a registered variant outside the pin is not read and leaves the body unchanged.

## Impact

- `src/adni_sexdiff/constants.py`:
  - scientific, decided here: the `EXPORT_VARIANTS` entry `nmr_all_columns`, `NMR_MEMBERSHIP_READING_RULES` and the variant's dependence label;
  - predeclared: `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]`, with `analysis` and `diagnostics`;
  - conventions: `EXPORT_VARIANT_RULE_SETS` and `REPORT_EXPORT_VARIANTS`, each with an import-time assertion;
  - the docstring names the change and its constants.
- `src/adni_sexdiff/data.py`:
  - `_run_export` gains the `membership` hook: the derived families kept, their counts, the 165 columns compared with the primary's;
  - `_run_export_variant` handles a variant without a bridge;
  - these are written from `EXPORT_VARIANT_RULE_SETS`: `_statistic_reading_line`, `render_analysis_summary`, `_export_variant_lines`, `_export_variant_rules_heading`, `_export_variant_findings`, `_export_variant_status_line`, `render_export_sensitivity` and `render_axis_diagnostics`;
  - `run_axis_diagnostics` takes the variant's expected counts;
  - the report's loader, gates and sections loop over `REPORT_EXPORT_VARIANTS`;
  - the primary's, the latent arm's, the p180 variants', the CN / LMCI / AD arm's and the rank sweep's outputs are unchanged.
- `src/adni_sexdiff/cli.py`: none. `--variant` lists the registry, which now holds three names.
- `.gitignore`, `scripts/sync_results.sh`, `PARTICIPANT_LEVEL_PATTERNS`: unchanged. The existing pattern matches the variant's export CSVs.
- `scripts/spike_nmr_all_columns.py` (new, read-only) and `spike.md` in this change.
- Dependencies: none new. MOTCO stays at `v0.10.0`.
- Compute: one CV analysis on 378 features, about the primary's size, and one diagnostic run. The gates add one pinned primary export and one pinned rerun of the two p180 variants into a scratch directory.
- Machines: a data machine. nixos-office is one: the spike ran there on 2026-10-30, and the cleaned NMR table and the primary export matched their manifests. No machine is named in the code.
- Order: the apply starts after `adni-report-rank-sweep` is merged with its report, on this branch rebased onto `main`. The report gate needs that report, and this change's `case-study-report` delta modifies the requirement as that change leaves it.
- Committed, from the data machine's run, under `results/motco_export_sensitivity/nmr_all_columns/`:
  - `motco_input/manifest.json`;
  - `analysis/`: `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md`;
  - `comparison/`: its three files;
  - `diagnostics/`: its six files.

  Each file is named at commit with why it is aggregate.
- Scientific choices introduced here (flag and ask before changing):
  - the variant's membership (all 245 NMR columns) and scale (the rule's, each column its own floor);
  - its reading rules and dependence label;
  - the rule that the variant never replaces the primary and feeds no choice.
