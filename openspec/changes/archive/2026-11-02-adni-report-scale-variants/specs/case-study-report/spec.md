## ADDED Requirements

### Requirement: Report file name
The report SHALL be named `motco-adni-<date>.md` (`REPORT_NAME`) by the day it is written, or `motco-adni-<date>-<n>.md` (`REPORT_NAME_SAME_DAY`), n an integer of 2 or more, for a later report of the same day. The date and the ordinal SHALL be read from the name, and any other name SHALL stop the step naming the file and both patterns. Without `--out`, write mode SHALL use today's name without an ordinal.

#### Scenario: Second report of a day
- **WHEN** `report --out reports/motco-adni-2026-11-02-2.md` runs while `reports/motco-adni-2026-11-02.md` exists
- **THEN** the step writes the new file, leaves the first unchanged, and the new file's title line ends with `2026-11-02, report 2`

#### Scenario: Name outside the patterns
- **WHEN** `--out` names `reports/motco-adni-2026-11-02-1.md` or `reports/motco-adni-latest.md`
- **THEN** the step stops naming the file and both patterns, and writes nothing

#### Scenario: Today's report exists
- **WHEN** `report` runs without `--out` and `--force` while today's report exists
- **THEN** the step stops naming the file, `--force` and the next free same-day name, and writes nothing

## MODIFIED Requirements

### Requirement: Inputs are the kept aggregate outputs only
The step SHALL read only the committed aggregate files of the pipeline, of the latent arm, of every export variant of `REPORT_EXPORT_VARIANTS`, of the CN / LMCI / AD arm and of the rank sweep: manifests, records, summaries, count and comparison tables, diagnostics files and the `nist_bridge` bridge table. It SHALL open no participant-level file and SHALL NOT require one to be present.

#### Scenario: Clone without participant-level files
- **WHEN** `report` runs on a clone that holds the tracked files under `results/` and none of `cohort.csv`, the export CSVs of the primary, of a variant or of the CN / LMCI / AD arm, `latent_scores.csv` or `analysis_metadata.csv`
- **THEN** it writes the report, and every hash it quotes for a participant-level file is the value a manifest records

#### Scenario: Input absent
- **WHEN** `results/motco_latent_sensitivity/comparison/latent_sensitivity.csv` does not exist
- **THEN** the step stops naming the file and the `latent-sensitivity` command, and writes nothing

#### Scenario: Variant inputs
- **WHEN** the report runs with the six variants of `REPORT_EXPORT_VARIANTS`
- **THEN** it reads, per variant in that order, `motco_input/manifest.json`, the analysis' `result.json`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six files, and for `nist_bridge` `bridge/nist_bridge.csv`: 79 files (14 for `nist_bridge`, 13 each for `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`), beside the 26 of the primary and the arm

#### Scenario: Scale variant input absent
- **WHEN** `results/motco_export_sensitivity/glog/comparison/export_sensitivity.csv` does not exist
- **THEN** the step stops naming the file and the `export-sensitivity` command for `glog`, and writes nothing

#### Scenario: Variant input absent
- **WHEN** `results/motco_export_sensitivity/per_run_standardized/diagnostics/diagnostics_manifest.json` does not exist
- **THEN** the step stops naming the file and the `axis-diagnostics` command with that variant's export, analysis and diagnostics directories, and writes nothing

#### Scenario: CN / LMCI / AD arm inputs
- **WHEN** the report runs on the committed outputs
- **THEN** it reads, under `results/motco_stage_sensitivity/`, `motco_input/manifest.json`, the analysis' `result.json`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six files: 13 files

#### Scenario: CN / LMCI / AD arm input absent
- **WHEN** `results/motco_stage_sensitivity/diagnostics/diagnostics_manifest.json` does not exist
- **THEN** the step stops naming the file and the `axis-diagnostics` command with the arm's export, analysis and diagnostics directories, and writes nothing

#### Scenario: Rank sweep inputs
- **WHEN** the report runs on the committed outputs
- **THEN** it reads, under `results/motco_rank_sensitivity/`, per rank of `RANK_SENSITIVITY_LADDER` in ladder order the rank's `result.json`, `analysis_manifest.json` and `summary.md`, then the comparison's three files and the diagnostics' six files: 27 files, 145 in all

#### Scenario: Rank sweep input absent
- **WHEN** `results/motco_rank_sensitivity/rank_06/summary.md` does not exist
- **THEN** the step stops naming the file and the `rank-sensitivity` command, and writes nothing

### Requirement: Report content contract
The report SHALL be one Markdown file with these sections in order: summary; provenance; cohort; export; primary analysis; axis diagnostics of the primary; latent-adjustment sensitivity; export sensitivity; stage-definition sensitivity; rank sensitivity; findings; reading rules; reproduction. The primary's statistics SHALL be given in full, each sensitivity beside the primary with a status per statistic, and every value SHALL be aggregate.

#### Scenario: Primary statistics
- **WHEN** the report is written
- **THEN** the primary's statistics are given with p-value, rejection and null summary, its rank, floor and eigengap beside `angle`, its covariate block and reference row

#### Scenario: Sections present
- **WHEN** the report is written
- **THEN** its level-2 headings are the thirteen sections in the order above, and the latent-adjustment section holds the comparison table with the primary row first, the arm's `latent_adjustment` block, the covariate roles and the arm's flagged diagnostic rows

#### Scenario: Diagnostics quoted
- **WHEN** the report is written on the committed outputs
- **THEN** the primary's diagnostics section lists every flagged latent-component and block-PC row of `axis_correlations.csv` and `block_pcs.csv`, the components table with the loading share per block, and each block's first PC against `phase` beside the export's recorded value

#### Scenario: Export sensitivity section
- **WHEN** the report is written on the committed outputs
- **THEN** the export-sensitivity section holds, after a lead that names each group and its rule set, one group per rule set of the variants of `REPORT_EXPORT_VARIANTS`, in registry order: the run-handling group (`nist_bridge`, `per_run_standardized`), the membership group (`nmr_all_columns`) and the scale group (`raw_scale`, `log2_plus_one`, `glog`). Each group holds the statistics table with the primary row first and one row per variant of the group in registry order, each with its status; each variant's rank, floor and eigengap beside `angle`; the latent spaces of the primary and the group's variants; the run offset per block of the primary export and of each variant export of the group; each variant export's counts beside its predeclared ones; for `nist_bridge` the bridged metabolites per kit beside the predeclared counts and the unbridged metabolites; for `nmr_all_columns` its membership, the derived columns kept, the rule's columns against the primary's, the joint features, the block shares and the NMR shape counts; for each scale variant its transform and offset, the rule's floors recorded and not applied, its offset summary, and per block the shape counts and numerical rank of the primary export and of the variant; each variant's flagged diagnostic rows, components and block PCs; the first component against `phase` of the primary and the group's variants; and each variant analysis' `cli_equivalent`

#### Scenario: Stage-definition sensitivity section
- **WHEN** the report is written on the committed outputs
- **THEN** the stage-definition section holds the statistics table with the primary row first and the CN / LMCI / AD arm's row, each with its status; both ranks, floors and eigengaps beside `angle`; the latent spaces; the arm's definition with the participants kept and dropped by `dx_bl` and sex, the sex × stage cells, the runs within each stage and the covariate levels of the primary and the arm; the run offset per block of both beside the arm's predeclared counts; the arm export's counts beside `STAGE_SENSITIVITY_EXPECTED_COUNTS`; the arm's flagged diagnostic rows, components and block PCs; and the arm analysis' `cli_equivalent`

#### Scenario: Rank sensitivity section
- **WHEN** the report is written on the committed outputs
- **THEN** the rank section holds the statistics table with, per statistic, the primary row first and one row per rank in ladder order, each with its rank and status; the latent spaces of the primary and every rank with each `angle` null summary; the anchor and the nesting per rank as the comparison manifest records them; the anchor rank, the comparison rows and each rank's selection, rank and CV repeats beside `RANK_SENSITIVITY_EXPECTED_COUNTS`; the top rank's flagged diagnostic rows, components and block PCs; and each rank's `cli_equivalent`

#### Scenario: QC inputs in the provenance
- **WHEN** the report is written on the committed outputs
- **THEN** the provenance lists the two QC archives and the four NIST workbooks with their sha256 beside the predeclared values, as the `nist_bridge` export manifest records them

#### Scenario: Export variant groups kept apart
- **WHEN** the export-sensitivity section is parsed
- **THEN** no table holds variants of two groups, every table of the membership group holds the primary and `nmr_all_columns` only, every table of the scale group holds the primary and scale variants only, the titles of the membership group's tables begin with `nmr_all_columns: `, and the titles of the scale group's shared tables begin with `raw_scale, log2_plus_one, glog: ` and those of a scale variant's diagnostics with its name

#### Scenario: Variant export counts
- **WHEN** a variant export's counts are reported beside its predeclared ones
- **THEN** the table lists every key of its `EXPORT_VARIANT_EXPECTED_COUNTS` entry except `analysis`, the run offset and `diagnostics`, which the steps compare themselves, and holds no row whose every cell is `n/a`

#### Scenario: Scale group counts
- **WHEN** the scale group's counts table is written on the committed outputs
- **THEN** it holds one column pair per scale variant (observed, expected) in registry order, the keys of the three entries in registry order, the shape counts and numerical ranks of each variant beside its predeclared ones, and the rows `scale.median_below_offset.*` with values for `log2_plus_one` and `n/a` for `raw_scale` and `glog`

### Requirement: Every number is pasted from the generated files
Every number in the report SHALL be read from a record, a manifest or a CSV and formatted with the digits of the summary it belongs to (six significant digits for record values, p-values as recorded, counts as integers, correlations and shares as `diagnostics.md` prints them). The step SHALL compute no statistic, correlation, mean or count of its own.

#### Scenario: Statistics equal the record
- **WHEN** the report's statistics table is compared with `result.json`
- **THEN** every observed value, p-value and null mean, sd and q95 equals the record's value at the printed digits, and the rank equals `latent.selected_lv`

#### Scenario: Counts equal the tables
- **WHEN** the report's cohort tables are compared with `stage_counts.csv` and the cohort manifest
- **THEN** every count and every descriptive equals the source value, and no cell is derived by the step

#### Scenario: Variant values equal their sources
- **WHEN** the export-sensitivity tables are compared with each variant's `export_sensitivity.csv`, export manifest, `nist_bridge.csv` and diagnostics CSVs
- **THEN** every value equals its source at the printed digits, and no cell is derived by the step

#### Scenario: CN / LMCI / AD arm values equal their sources
- **WHEN** the stage-definition tables are compared with `stage_sensitivity.csv`, the arm's export manifest, the primary export manifest and the arm's diagnostics CSVs
- **THEN** every value equals its source at the printed digits, every row of the four arm-definition tables equals the corresponding row of the committed `stage_sensitivity.md`, and no cell is derived by the step

#### Scenario: Rank sweep values equal their sources
- **WHEN** the rank tables are compared with `rank_sensitivity.csv`, each rank's `result.json`, the comparison and rank manifests and the sweep's diagnostics CSVs
- **THEN** every value equals its source at the printed digits, every row of the nesting table equals the corresponding row of the committed `rank_sensitivity.md`, and no cell is derived by the step

#### Scenario: Membership variant values equal their sources
- **WHEN** the membership group's tables are compared with the `nmr_all_columns` `export_sensitivity.csv`, its export manifest, its `result.json` and its diagnostics CSVs
- **THEN** every value equals its source at the printed digits, every row of its latent-space table equals the corresponding row of the committed `export_sensitivity.md`, every line of its "Export variant" block equals the corresponding line of that document, and no cell is derived by the step

#### Scenario: Scale variant values equal their sources
- **WHEN** the scale group's tables are compared with each scale variant's `export_sensitivity.csv`, export manifest, `result.json` and diagnostics CSVs
- **THEN** every value equals its source at the printed digits, the primary's and each variant's column of the latent-space table equal the corresponding columns of that variant's committed `export_sensitivity.md`, every line of each "Export variant" block equals the corresponding line of that document, and no cell is derived by the step

### Requirement: Interpretive sentences are generated by rule
Each reading sentence in the report SHALL be produced from the rejection statuses by the same code that writes `summary.md` and the comparison documents of the four sensitivities (`latent_sensitivity.md`, `export_sensitivity.md`, `stage_sensitivity.md`, `rank_sensitivity.md`), so that the sentences are string-equal across the documents. The report SHALL add no other interpretive sentence, and the primary's status SHALL be the result wherever a sensitivity appears.

#### Scenario: Non-rejection wording
- **WHEN** `angle` is not rejected in the primary
- **THEN** the report states that the result is uninformative about orientation, in the sentence `summary.md` prints

#### Scenario: Arm status wording
- **WHEN** the primary and the arm both leave `delta` unrejected
- **THEN** the report marks the status `same`, states that the arm's non-rejection is weaker than the primary's and that neither is evidence that the sexes' trajectories agree, in the sentence `latent_sensitivity.md` prints

#### Scenario: Variant status wording
- **WHEN** the primary and `nist_bridge` both leave `angle` unrejected
- **THEN** the report marks the status `same` and states that the variant's non-rejection is no more informative than the primary's, in the sentence the `nist_bridge` `export_sensitivity.md` prints

#### Scenario: No reading of one variant against another
- **WHEN** both variants are reported
- **THEN** no status or sentence of the report compares `nist_bridge` with `per_run_standardized`, and variant rule 5 appears only in the reading-rules section

#### Scenario: CN / LMCI / AD arm status wording
- **WHEN** the primary and the CN / LMCI / AD arm both leave `shape` unrejected
- **THEN** the report marks the status `same` and states that the arm's non-rejection is no more informative than the primary's, in the sentence `stage_sensitivity.md` prints

#### Scenario: No reading of the CN / LMCI / AD arm against another sensitivity
- **WHEN** the CN / LMCI / AD arm is reported beside the latent arm and the export variants
- **THEN** no status or sentence of the report compares the CN / LMCI / AD arm with the latent arm or with an export variant; a sentence that lists several sensitivities, each beside the primary, compares none

#### Scenario: Rank status wording
- **WHEN** the primary leaves `delta` unrejected and forced rank 6 rejects it
- **THEN** the report marks rank 6's status `differs (rank dependence)` and states that a rejection at a forced rank only is rank dependence, not a result at that rank, that the primary's non-rejection stays the result and that no rule counts the ranks that reject, in the sentence `rank_sensitivity.md` prints

#### Scenario: Anchor and nesting wording
- **WHEN** the report prints the anchor and nesting bullets from the comparison manifest
- **THEN** each bullet is string-equal to its line in the committed `rank_sensitivity.md`

#### Scenario: No reading of the sweep against another sensitivity
- **WHEN** the rank sweep is reported beside the other sensitivities
- **THEN** no status, sentence or table of the report compares a forced rank with the CV-selected rank of the latent arm, an export variant or the CN / LMCI / AD arm; a sentence that lists several sensitivities, each beside the primary, compares none

#### Scenario: Membership status wording
- **WHEN** the primary leaves `delta` unrejected and `nmr_all_columns` rejects it
- **THEN** the report marks the status `differs (feature-membership dependence)` and states that the rejection is dependence on the NMR feature membership, not a result of the variant, and that the primary's non-rejection stays the result, in the sentence the `nmr_all_columns` `export_sensitivity.md` prints

#### Scenario: No reading of the membership variant against another sensitivity
- **WHEN** `nmr_all_columns` is reported beside the p180 variants and the other sensitivities
- **THEN** no status, sentence or table of the report compares `nmr_all_columns` with a p180 variant, the latent arm, the CN / LMCI / AD arm or a forced rank; a sentence or provenance table that lists several sensitivities, each beside the primary, compares none

#### Scenario: Scale status wording
- **WHEN** the primary and `glog` both leave `delta` unrejected
- **THEN** the report marks the status `same` and states that the variant's non-rejection is no more informative than the primary's (scale rule 6), in the sentence the `glog` `export_sensitivity.md` prints

#### Scenario: No reading of one scale variant against another
- **WHEN** the three scale variants are reported in the scale group's shared tables
- **THEN** the group's lead states that each variant is read against the primary only, never against another variant of the group (scale rule 8); each `angle` paragraph and each status bullet names the primary and one scale variant; and no status or sentence of the report compares two scale variants, or a scale variant with another export variant, the latent arm, the CN / LMCI / AD arm or a forced rank

### Requirement: Reading rules carried verbatim
The report SHALL print `READING_RULES`, then `LATENT_SENSITIVITY_READING_RULES`, the rule set of each export variant group in registry order (`EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES`, `SCALE_VARIANT_READING_RULES`), `STAGE_SENSITIVITY_READING_RULES` and `RANK_SENSITIVITY_READING_RULES` verbatim in its reading-rules section. Beside every table that quotes a sensitivity it SHALL name that sensitivity's rules, each with `READING_RULES`.

#### Scenario: Rules string-equal
- **WHEN** the seven numbered lists of the reading-rules section are compared with the constants
- **THEN** each item is string-equal to its constant, in order

#### Scenario: Variant tables name their rules
- **WHEN** the summary and the export-sensitivity section quote a variant
- **THEN** the text that leads the variant's group names `READING_RULES` and the group's rule set: `EXPORT_VARIANT_READING_RULES` for `nist_bridge` and `per_run_standardized`, `NMR_MEMBERSHIP_READING_RULES` for `nmr_all_columns`, `SCALE_VARIANT_READING_RULES` for `raw_scale`, `log2_plus_one` and `glog`

#### Scenario: CN / LMCI / AD arm tables name their rules
- **WHEN** the summary and the stage-definition section quote the CN / LMCI / AD arm
- **THEN** the text that leads them names `READING_RULES` and `STAGE_SENSITIVITY_READING_RULES`

#### Scenario: Rank sweep tables name their rules
- **WHEN** the summary and the rank section quote the sweep
- **THEN** the text that leads them names `READING_RULES` and `RANK_SENSITIVITY_READING_RULES`

### Requirement: Findings copied, never stops
The report's findings section SHALL list every deviation and finding of every input manifest, verbatim and attributed to its step, and the step's own findings: a manifest whose recorded revision is dirty, and a manifest without a `numerics` block. None of these SHALL stop the step.

#### Scenario: Arm rank finding carried
- **WHEN** the arm's manifest records the finding that its rank differs from the primary's
- **THEN** the report's findings section lists it under `latent-sensitivity`, verbatim

#### Scenario: CN / LMCI / AD arm rank finding carried
- **WHEN** the CN / LMCI / AD arm's analysis manifest records the finding that its rank differs from the primary's
- **THEN** the report's findings section lists it under `stage-sensitivity`, verbatim

#### Scenario: Rank dependence finding carried
- **WHEN** the rank-6 manifest and the comparison manifest record the finding that forced rank 6's `delta` status differs from the primary's
- **THEN** the report's findings section lists it under `rank-sensitivity`, verbatim, once for each manifest

#### Scenario: Nesting finding carried
- **WHEN** the comparison manifest records a nesting check that fails
- **THEN** the report's findings section lists the finding under `rank-sensitivity`, the nesting table shows the failing rank, and the report is still written

#### Scenario: Dirty revision
- **WHEN** a manifest records `git_revision.dirty` true
- **THEN** the findings section names the step and the revision, and the report is still written

#### Scenario: Membership dependence finding carried
- **WHEN** the `nmr_all_columns` analysis manifest and comparison manifest record the finding that its `delta` status differs from the primary's
- **THEN** the report's findings section lists it under `export-sensitivity`, verbatim, once for each manifest

#### Scenario: Scale variant rank finding carried
- **WHEN** the `raw_scale` analysis manifest and comparison manifest record the finding that its CV-selected rank 7 differs from the primary's 8
- **THEN** the report's findings section lists it under `export-sensitivity`, verbatim, once for each manifest, and lists no rank finding for `log2_plus_one`, whose manifests record none

### Requirement: The report covers the variants it names
The step SHALL read, check and quote exactly the export variants of `REPORT_EXPORT_VARIANTS`, in its order, a subsequence of `EXPORT_VARIANTS`. A registered variant outside it SHALL NOT be read or required, and SHALL leave the report body unchanged. The step SHALL name it on a progress line, never in the body. A change that adds a variant to the report SHALL extend `REPORT_EXPORT_VARIANTS` and re-issue the report.

#### Scenario: Pin covers every registered variant
- **WHEN** the report runs on the committed outputs
- **THEN** it reads, checks and quotes `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog` in registry order, and no progress line names an uncovered variant

#### Scenario: A third variant registered
- **WHEN** `REPORT_EXPORT_VARIANTS` names `nist_bridge` and `per_run_standardized` only, and the outputs of the four variants registered after them are absent
- **THEN** `report` reads 93 files, no line of the body names `nmr_all_columns`, `raw_scale`, `log2_plus_one` or `glog`, and one progress line per uncovered variant says that it is registered and not covered by this report

#### Scenario: Scale variants registered outside the pin
- **WHEN** `EXPORT_VARIANTS` holds the six variants, `REPORT_EXPORT_VARIANTS` names the first three only, and the outputs of the three scale variants are absent
- **THEN** `report` reads 106 files, no line of the body names `raw_scale`, `log2_plus_one` or `glog`, and one progress line per scale variant says that it is registered and not covered by this report

#### Scenario: Newest report still checks
- **WHEN** `report --check` runs on the newest committed report, written under the current pin, on the tree it was written from
- **THEN** it compares every table and line with no mismatch and exits 0; a report written under an earlier pin stops at the variant gate instead

#### Scenario: Pin out of order
- **WHEN** `REPORT_EXPORT_VARIANTS` names a variant that is not in `EXPORT_VARIANTS`, or lists two variants out of registry order
- **THEN** importing the constants fails naming both constants, before any step runs

### Requirement: Check stops on a report that lists other export variants
After a report's level-2 headings match the current sections and before any input gate, `--check` SHALL compare the export variants the report lists, its level-3 headings ``Export variant `<name>` `` in the export-sensitivity section in order, with `REPORT_EXPORT_VARIANTS`. On a difference it SHALL stop, naming the report, the absent and extra variants and how to find the revision that committed it, compare no cell and write nothing.

#### Scenario: Report of the three-variant pin
- **WHEN** `report --check --out reports/motco-adni-2026-11-02.md` runs after the scale variants are added to `REPORT_EXPORT_VARIANTS`
- **THEN** the check stops naming the report, the absent variants `raw_scale`, `log2_plus_one` and `glog`, no extra variant and the command `git log -1 --format=%H -- reports/motco-adni-2026-11-02.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the two-variant pin
- **WHEN** `report --check --out reports/motco-adni-2026-10-31.md` runs
- **THEN** the check stops naming the report, the absent variants `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`, no extra variant and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-31.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the current pin
- **WHEN** `report --check` runs on a report the step just wrote
- **THEN** the report's variants are `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog` in that order, and the check goes on to the input gates and the comparison

#### Scenario: Variants out of order
- **WHEN** a report lists the variants of `REPORT_EXPORT_VARIANTS` in another order
- **THEN** the check stops naming the report, no absent and no extra variant, that the order differs, and the `git log` command, and writes nothing

### Requirement: Deterministic report body
The report body SHALL depend only on the input files and the report's file name: the date, with its same-day ordinal when the name carries one, SHALL appear in the file name and the title only, and no revision, host, time or runtime of the report run SHALL be written. Two runs on the same inputs to the same path SHALL be byte-identical.

#### Scenario: Rerun with force
- **WHEN** `report --force` runs twice to the same `--out` on unchanged inputs
- **THEN** the two files have equal sha256

#### Scenario: Another date
- **WHEN** the report is written to a file whose name carries another date
- **THEN** the two files differ only in the title line

#### Scenario: Same-day name
- **WHEN** the report is written from the same inputs to `motco-adni-2026-11-02.md` and to `motco-adni-2026-11-02-2.md`
- **THEN** the two files differ only in the title line

### Requirement: Check selects the report and reruns the gates
Without `--out`, `--check` SHALL read the newest report under `reports/` by the date in its name, then by its same-day ordinal (a name without one first). Before any other gate, a report whose level-2 headings differ from the current sections SHALL stop the check, naming the report, the sections it lacks or adds, and how to find the revision that committed it. The check SHALL then run every gate of the write mode before comparing.

#### Scenario: No report
- **WHEN** `reports/` holds no `motco-adni-*.md` and `--out` is not given
- **THEN** `report --check` stops naming the directory and the pattern

#### Scenario: Same-day report is the newest
- **WHEN** `reports/` holds `motco-adni-2026-11-02.md` and `motco-adni-2026-11-02-2.md` and `--out` is not given
- **THEN** `report --check` reads `motco-adni-2026-11-02-2.md`

#### Scenario: Broken chain at check time
- **WHEN** the export manifest was regenerated after the primary and `report --check` runs
- **THEN** the check stops naming `manifest.json`, both hashes and `analyze`, before any cell is compared

#### Scenario: Report of an earlier layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-30.md` runs after the rank section is added
- **THEN** the check stops naming the report, the absent section `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-30.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the eleven-section layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-29.md` runs
- **THEN** the check stops naming the report, the absent sections `Stage-definition sensitivity` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-29.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the first layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-28.md` runs
- **THEN** the check stops naming the report, the absent sections `Export sensitivity`, `Stage-definition sensitivity` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-28.md`, compares no cell, writes nothing and exits non-zero
