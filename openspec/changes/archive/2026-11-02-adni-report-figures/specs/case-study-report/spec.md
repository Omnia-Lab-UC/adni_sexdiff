# Spec Delta

## MODIFIED Requirements

### Requirement: Inputs are the kept aggregate outputs only
The step SHALL read only the committed aggregate files of the pipeline, of the latent arm, of every export variant of `REPORT_EXPORT_VARIANTS`, of the CN / LMCI / AD arm and of the rank sweep: manifests, records, summaries, the primary's stage means, count and comparison tables, diagnostics files and the `nist_bridge` bridge table; and the committed copy of the cited MOTCO decision file. It SHALL open no participant-level file and SHALL NOT require one to be present.

#### Scenario: Clone without participant-level files
- **WHEN** `report` runs on a clone that holds the tracked files under `results/` and `references/` and none of `cohort.csv`, the export CSVs of the primary, of a variant or of the CN / LMCI / AD arm, `latent_scores.csv` or `analysis_metadata.csv`
- **THEN** it writes the report and its figures, and every hash it quotes for a participant-level file is the value a manifest records

#### Scenario: Input absent
- **WHEN** `results/motco_latent_sensitivity/comparison/latent_sensitivity.csv` does not exist
- **THEN** the step stops naming the file and the `latent-sensitivity` command, and writes nothing

#### Scenario: Stage means input
- **WHEN** the report runs on the committed outputs
- **THEN** it reads the primary's `result.json`, `analysis_manifest.json`, `summary.md` and `stage_means.csv`, and checks `stage_means.csv` against the sha256 that `analysis_manifest.json` records for it

#### Scenario: Stage means absent
- **WHEN** `results/motco_analysis/stage_means.csv` does not exist
- **THEN** the step stops naming the file and the `analyze` command, and writes nothing

#### Scenario: Variant inputs
- **WHEN** the report runs with the six variants of `REPORT_EXPORT_VARIANTS`
- **THEN** it reads, per variant in that order, `motco_input/manifest.json`, the analysis' `result.json`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six files, and for `nist_bridge` `bridge/nist_bridge.csv`: 79 files (14 for `nist_bridge`, 13 each for `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`), beside the 27 of the primary and the arm

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
- **THEN** it reads, under `results/motco_rank_sensitivity/`, per rank of `RANK_SENSITIVITY_LADDER` in ladder order the rank's `result.json`, `analysis_manifest.json` and `summary.md`, then the comparison's three files and the diagnostics' six files: 27 files

#### Scenario: Rank sweep input absent
- **WHEN** `results/motco_rank_sensitivity/rank_06/summary.md` does not exist
- **THEN** the step stops naming the file and the `rank-sensitivity` command, and writes nothing

#### Scenario: Operating-characteristics input
- **WHEN** the report runs on the committed outputs
- **THEN** it reads `references/motco_adni_design/adni_design_decision.json`: 147 files in all, 45 of them manifests

#### Scenario: Operating-characteristics input absent
- **WHEN** `references/motco_adni_design/adni_design_decision.json` does not exist
- **THEN** the step stops naming the file and the `git show` command that copies it from the pinned MOTCO commit, and writes nothing

### Requirement: Report content contract
The report SHALL be one Markdown file with these sections in order: summary; figures; provenance; cohort; export; primary analysis; axis diagnostics of the primary; operating characteristics; latent-adjustment sensitivity; export sensitivity; stage-definition sensitivity; rank sensitivity; findings; reading rules; reproduction. The primary's statistics SHALL be given in full, each sensitivity beside the primary with a status per statistic, and every value SHALL be aggregate.

#### Scenario: Primary statistics
- **WHEN** the report is written
- **THEN** the primary's statistics are given with p-value, rejection and null summary, its rank, floor and eigengap beside `angle`, its covariate block and reference row

#### Scenario: Sections present
- **WHEN** the report is written
- **THEN** its level-2 headings are the fifteen sections in the order above, and the latent-adjustment section holds the comparison table with the primary row first, the arm's `latent_adjustment` block, the covariate roles and the arm's flagged diagnostic rows

#### Scenario: Figures section
- **WHEN** the report is written on the committed outputs
- **THEN** the figures section holds a lead naming the figures directory, the matplotlib version and how `--check` compares the figures; the table "Figure files" with one row per figure of `REPORT_FIGURES` in order (title, SVG and its sha256, data CSV and its sha256, input files); and per figure a level-3 heading, the image and its three-part caption

#### Scenario: Operating characteristics section
- **WHEN** the report is written on the committed outputs
- **THEN** the operating-characteristics section holds the cited source (MOTCO change, pull request, commit, path, report and sha256 of `OPERATING_CHARACTERISTICS_SOURCE`, the copy's path, the run's units and failures and its settings hash), MOTCO's decision rule, the six size readings with their bound and the size sentence, the power rate per target statistic and effect with its standard error and CV-selected ranks, the three statements, and the construction beside this design with, per reference value, the committed source it was checked against

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
Every number in the report and in its figures SHALL be read from a record, a manifest, a CSV or the cited decision file and formatted with the digits of the summary it belongs to (six significant digits for record values, p-values as recorded, counts as integers, correlations and shares as `diagnostics.md` prints them, the decision's rates and standard errors at three decimals and its bound at four). The step SHALL compute no statistic, correlation, mean or count of its own.

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

#### Scenario: Measured values equal the decision file
- **WHEN** the operating-characteristics tables are compared with the decision file
- **THEN** every rejection count, replicate count, rate, standard error, bound, effect, CV-selected rank and construction value equals the file's value at the printed digits, every reference value is printed as the file records it, and no cell is derived by the step

#### Scenario: Figure values equal their sources
- **WHEN** each row of a figure's data CSV is compared with the file and field, or the constant, it names
- **THEN** its value is the source's value as read (a JSON number by its shortest round-trip form, a CSV cell unchanged; for a reference line such as α or the correlation flag, the named constant of `constants.py`), and every number printed inside the figure is that value at the digits the report prints for it

#### Scenario: Legend counts copied
- **WHEN** `f7_nist_bridge` labels the bridged metabolites per kit and the unbridged ones
- **THEN** the counts are the `nist_bridge` export manifest's bridge summary, not a tally of `nist_bridge.csv`

#### Scenario: Cell without a row
- **WHEN** `stage_counts.csv` holds no intersection row for a sex, `DX.bl` and p180 run, such as SMC in ADNI-1
- **THEN** `f1_cohort_design` draws the cell empty and labelled `none`, and its data CSV records the value `absent`, not 0

### Requirement: Interpretive sentences are generated by rule
Each reading sentence in the report SHALL be produced from the rejection statuses by the code that writes `summary.md` and the four sensitivities' comparison documents, string-equal across the documents. Besides the cited measurement's sentences, quoted verbatim, and the figures' fixed reading texts (`REPORT_FIGURES`), the report SHALL add no interpretive sentence, and the primary's status SHALL be the result wherever a sensitivity appears.

#### Scenario: Non-rejection wording
- **WHEN** `angle` is not rejected in the primary
- **THEN** the report states that the result is uninformative about orientation, in the sentence `summary.md` prints

#### Scenario: Reading sentences unchanged by the measurement
- **WHEN** the primary's reading bullets of the report are compared with the committed `results/motco_analysis/summary.md`
- **THEN** each bullet is string-equal to its line there, including the clause that no power statement exists at this design, which measurement rule 2 reads

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

#### Scenario: Figure caption sentences
- **WHEN** the figures section is compared with the documents the report already quotes
- **THEN** every generated caption line is string-equal to the line that prints it elsewhere in the report, each fixed reading text describes how its figure encodes values, and no title, subtitle, reading text or text inside a figure states a result

#### Scenario: Sensitivity figure reads each row against the primary
- **WHEN** `f8_sensitivities` labels the forced rank 6 `delta` row, whose status differs from the primary's
- **THEN** the label is the status `differs (rank dependence)` from the rank's comparison, the caption prints that status's sentence from `rank_sensitivity.md`, and nothing in the figure or the caption compares two sensitivities, combines ranks or marks a row by its p-value alone

### Requirement: Deterministic report body
The report body and its figures SHALL depend only on the input files, the report's file name and the pinned drawing library: the date, with its same-day ordinal when the name carries one, SHALL appear in the file name, the title and the figures directory only, and no revision, host, time or runtime of the report run SHALL be written. Two runs on the same inputs to the same path SHALL write byte-identical files.

#### Scenario: Rerun with force
- **WHEN** `report --force` runs twice to the same `--out` on unchanged inputs
- **THEN** the two reports have equal sha256, and so has each of the eighteen figure files

#### Scenario: Another date
- **WHEN** the report is written to a file whose name carries another date
- **THEN** the two reports differ only in the title line and in the figures directory their figures section names, and their figure files are byte-identical

#### Scenario: Same-day name
- **WHEN** the report is written from the same inputs to `motco-adni-2026-11-02.md` and to `motco-adni-2026-11-02-2.md`
- **THEN** the two reports differ only in the title line and in the figures directory their figures section names, and their figure files are byte-identical

#### Scenario: Another machine
- **WHEN** the report is written on two machines from the same committed tree under the same lock
- **THEN** the reports and every figure file are byte-identical

### Requirement: Check compares cell by cell and names every mismatch
With `--check`, the step SHALL regenerate the report and its figures from the inputs now on disk, with the date taken from the checked file's name, and compare: the report's tables cell by cell and its other lines line by line, then each figure's data CSV cell by cell, then each figure's SVG by its bytes. Each mismatch SHALL be named (section, table, row key, column and both values, or the line), and the step SHALL exit non-zero on any mismatch and SHALL write nothing.

#### Scenario: Fresh report passes
- **WHEN** `report --check` runs on a report the step just wrote from unchanged inputs
- **THEN** it reports no mismatch in the report or its figures and exits zero

#### Scenario: Edited digit
- **WHEN** one p-value in the report's statistics table is changed by hand
- **THEN** `report --check` names the section, the table, the row `delta` (or the edited statistic), the column, both values, and exits non-zero

#### Scenario: Regenerated input
- **WHEN** a results file the report quotes by hash was regenerated after the report was written
- **THEN** `report --check` names the provenance cell holding that file's hash with both values, and every figure that reads the file, and exits non-zero

#### Scenario: Edited figure data
- **WHEN** one value of `f8_sensitivities.csv` is changed by hand
- **THEN** `report --check` names the file, the row key, the column, both values and the row's source, and exits non-zero

#### Scenario: Drawing changed, data equal
- **WHEN** an SVG's bytes differ from the regenerated drawing while its data CSV equals the regenerated data
- **THEN** `report --check` names the SVG and both sha256, says that its data are equal so the drawing moved and not a result, and exits non-zero

#### Scenario: Figure file missing or extra
- **WHEN** the figures directory lacks a file the report names, or holds a file the report does not name
- **THEN** `report --check` names the directory and each missing or extra file, and exits non-zero

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

#### Scenario: Report of the fourteen-section layout
- **WHEN** `report --check --out reports/motco-adni-2026-11-02-3.md` runs after the figures section is added
- **THEN** the check stops naming the report, the absent section `Figures` and the command `git log -1 --format=%H -- reports/motco-adni-2026-11-02-3.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the thirteen-section layout
- **WHEN** `report --check --out reports/motco-adni-2026-11-02-2.md` runs
- **THEN** the check stops naming the report, the absent sections `Figures` and `Operating characteristics` and the command `git log -1 --format=%H -- reports/motco-adni-2026-11-02-2.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of an earlier layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-30.md` runs
- **THEN** the check stops naming the report, the absent sections `Figures`, `Operating characteristics` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-30.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the eleven-section layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-29.md` runs
- **THEN** the check stops naming the report, the absent sections `Figures`, `Operating characteristics`, `Stage-definition sensitivity` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-29.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the first layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-28.md` runs
- **THEN** the check stops naming the report, the absent sections `Figures`, `Operating characteristics`, `Export sensitivity`, `Stage-definition sensitivity` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-28.md`, compares no cell, writes nothing and exits non-zero

### Requirement: Output discipline
The report SHALL be written to a temporary file and its figures to a temporary directory, and both SHALL be renamed when complete; an existing file at `--out`, or an existing figures directory for its name, SHALL stop the step unless `--force`. After writing, the step SHALL parse the file through the check parser and verify that the parsed tables equal the generated ones.

#### Scenario: Existing report
- **WHEN** `--out` names a file that exists and `--force` is not given
- **THEN** the step stops naming the file and leaves it unchanged

#### Scenario: Existing figures directory
- **WHEN** `reports/figures/<stem>/` exists for the report's name, the report does not, and `--force` is not given
- **THEN** the step stops naming the directory and leaves it unchanged

#### Scenario: Parse-back
- **WHEN** the report is written
- **THEN** the step reports the number of tables and cells it parsed back, equal to the number generated, and the number of figure files written, and no temporary file or directory remains

#### Scenario: Failure while drawing
- **WHEN** drawing a figure fails
- **THEN** the step stops naming the figure, writes neither the report nor any figure file, and no temporary file or directory remains

### Requirement: No participant identifier and aggregate values only
The report, its figures, their data CSVs and every progress line of the step SHALL hold no participant identifier and SHALL quote aggregate values only: counts, statistics, hashes, settings and constants.

#### Scenario: Identifier search
- **WHEN** the report is searched for the token `RID` and for the `rid` values of the exported participants
- **THEN** the token appears only as a column name, and no value is a participant identifier: a number equal to a `rid` value is a count, rank or other aggregate value copied from its source

#### Scenario: Figure data search
- **WHEN** the figures directory is searched for the token `RID` and for the `rid` values of the exported participants
- **THEN** the token is not found; no key, field or value is a participant identifier, since a cell equal to a `rid` value is a count, rank or other aggregate value, as its `source` and `field` show; and every source named in a data CSV is a committed aggregate file of `REPORT_INPUT_FILES` or, for a reference line such as α or the correlation flag, a named constant of `constants.py`

### Requirement: The report covers the variants it names
The step SHALL read, check and quote exactly the export variants of `REPORT_EXPORT_VARIANTS`, in its order, a subsequence of `EXPORT_VARIANTS`. A registered variant outside it SHALL NOT be read or required, and SHALL leave the report body unchanged. The step SHALL name it on a progress line, never in the body. A change that adds a variant to the report SHALL extend `REPORT_EXPORT_VARIANTS` and re-issue the report.

#### Scenario: Pin covers every registered variant
- **WHEN** the report runs on the committed outputs
- **THEN** it reads, checks and quotes `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog` in registry order, and no progress line names an uncovered variant

#### Scenario: A third variant registered
- **WHEN** `REPORT_EXPORT_VARIANTS` names `nist_bridge` and `per_run_standardized` only, and the outputs of the four variants registered after them are absent
- **THEN** `report` reads 95 files, no line of the body or of a figure names `nmr_all_columns`, `raw_scale`, `log2_plus_one` or `glog`, and one progress line per uncovered variant says that it is registered and not covered by this report

#### Scenario: Scale variants registered outside the pin
- **WHEN** `EXPORT_VARIANTS` holds the six variants, `REPORT_EXPORT_VARIANTS` names the first three only, and the outputs of the three scale variants are absent
- **THEN** `report` reads 108 files, no line of the body or of a figure names `raw_scale`, `log2_plus_one` or `glog`, and one progress line per scale variant says that it is registered and not covered by this report

#### Scenario: Newest report still checks
- **WHEN** `report --check` runs on the newest committed report, written under the current layout and pin, on the tree it was written from
- **THEN** it compares every table, line and figure with no mismatch and exits 0; a report of an earlier layout or pin stops at the section or variant gate instead

#### Scenario: Pin out of order
- **WHEN** `REPORT_EXPORT_VARIANTS` names a variant that is not in `EXPORT_VARIANTS`, or lists two variants out of registry order
- **THEN** importing the constants fails naming both constants, before any step runs

### Requirement: Check stops on a report that lists other export variants
After a report's level-2 headings match the current sections and before any input gate, `--check` SHALL compare the export variants the report lists, its level-3 headings ``Export variant `<name>` `` in the export-sensitivity section in order, with `REPORT_EXPORT_VARIANTS`. On a difference it SHALL stop, naming the report, the absent and extra variants and how to find the revision that committed it, compare no cell and write nothing.

#### Scenario: Report of the three-variant pin
- **WHEN** `report --check` runs on a report with the fifteen current sections whose export-sensitivity section lists `nist_bridge`, `per_run_standardized` and `nmr_all_columns` only
- **THEN** the check stops naming the report, the absent variants `raw_scale`, `log2_plus_one` and `glog`, no extra variant and the `git log -1 --format=%H -- <report>` command, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the two-variant pin
- **WHEN** `report --check` runs on a report with the fifteen current sections whose export-sensitivity section lists `nist_bridge` and `per_run_standardized` only
- **THEN** the check stops naming the report, the absent variants `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`, no extra variant and the `git log -1 --format=%H -- <report>` command, compares no cell, writes nothing and exits non-zero

#### Scenario: Committed reports of earlier pins
- **WHEN** `report --check --out reports/motco-adni-2026-11-02.md` or `--out reports/motco-adni-2026-10-31.md` runs
- **THEN** the check stops at the section gate, naming the absent sections `Figures` and `Operating characteristics`, before the variant gate, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the current pin
- **WHEN** `report --check` runs on a report the step just wrote
- **THEN** the report's variants are `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog` in that order, and the check goes on to the input gates and the comparison

#### Scenario: Variants out of order
- **WHEN** a report lists the variants of `REPORT_EXPORT_VARIANTS` in another order
- **THEN** the check stops naming the report, no absent and no extra variant, that the order differs, and the `git log` command, and writes nothing

## ADDED Requirements

### Requirement: Figures are drawn from the report's inputs
In write mode, after every gate, the step SHALL draw the nine figures of `REPORT_FIGURES` in order from the inputs it has loaded and checked, and read no other file. Each figure SHALL be written as an SVG and a data CSV under `reports/figures/<report stem>/`, and no other file SHALL be written there.

#### Scenario: Nine figures
- **WHEN** the report is written on the committed outputs to `reports/motco-adni-<date>.md`
- **THEN** `reports/figures/motco-adni-<date>/` holds `f1_cohort_design` to `f9_rank_sweep`, each as `.svg` and `.csv`, eighteen files and nothing else

#### Scenario: Every export in the run-offset figure
- **WHEN** `f6_block_phase` is drawn
- **THEN** it holds one row per export in this order: the primary, the six variants of `REPORT_EXPORT_VARIANTS` grouped by rule set, then the CN / LMCI / AD arm; and no row for the latent arm or a forced rank, which use the primary export

#### Scenario: No figure of participant-level data
- **WHEN** the figures are drawn
- **THEN** no figure plots a latent score, a metabolite value of a participant or any value not held by a committed aggregate input

### Requirement: Figures are drawn under pinned software and numerics
Before anything is written, the step SHALL stop when the installed matplotlib differs from `MATPLOTLIB_VERSION`, or when the numeric state of the run is not pinned, naming the version or the unpinned settings. Each SVG SHALL be drawn with `FIGURE_STYLE`: text as paths, a fixed ID salt and no date.

#### Scenario: Another matplotlib
- **WHEN** the installed matplotlib is not 3.11.2
- **THEN** the step stops naming both versions and `uv sync --locked`, and writes nothing

#### Scenario: Numerics not pinned
- **WHEN** `adni_sexdiff` was imported after numpy, so the run's numeric state is not pinned
- **THEN** the step stops naming the settings that differ from `NUMERIC_SETTINGS`, and writes nothing

#### Scenario: Check under another matplotlib
- **WHEN** `report --check` runs with an installed matplotlib other than `MATPLOTLIB_VERSION`
- **THEN** the check stops naming both versions before any comparison, and writes nothing

### Requirement: Each figure is captioned in three parts
Under its image each figure SHALL carry: its fixed reading text from `REPORT_FIGURES`, which quotes no value from an input and states no result; the generated lines its entry names, each string-equal to the line that prints it elsewhere in the report; and its input files and rule lists. A figure with no generated lines SHALL carry the other two parts.

#### Scenario: Reading text verbatim
- **WHEN** the figures section is compared with `REPORT_FIGURES`
- **THEN** each figure's reading paragraph is string-equal to its entry's reading text

#### Scenario: Primary tests caption
- **WHEN** `f3_primary_tests` is captioned on the committed outputs
- **THEN** its generated lines are the primary's three reading bullets, string-equal to `summary.md`, and its rules name `READING_RULES` and `OPERATING_CHARACTERISTICS_READING_RULES`

#### Scenario: Sensitivity figure caption
- **WHEN** `f8_sensitivities` is captioned on the committed outputs
- **THEN** its generated lines are the status sentences of `nmr_all_columns` `delta` and forced rank 6 `delta`, string-equal to the comparison documents, and its rules name `READING_RULES` and every sensitivity's rule set

#### Scenario: Figure without generated lines
- **WHEN** `f1_cohort_design` is captioned
- **THEN** it carries its reading text, its input file `results/cohort/stage_counts.csv` and `READING_RULES`, and no generated line

### Requirement: Each figure is traced to its inputs
Each figure SHALL name its inputs three times: in the "Figure files" table of the report (its input files, with its SVG and data CSV and their sha256), in its SVG metadata (each input file with its sha256 and the matplotlib version), and in its data CSV (one row per plotted value with the source file and field).

#### Scenario: Figure files table
- **WHEN** the report is written on the committed outputs
- **THEN** each row of "Figure files" holds the sha256 of the SVG and data CSV just written, and input files that are all in `REPORT_INPUT_FILES` and listed in the provenance with their hashes

#### Scenario: Stray figure traced back
- **WHEN** `f9_rank_sweep.svg` is read on its own
- **THEN** its metadata names each `result.json` it was drawn from with its sha256, and those hashes equal the provenance of the report whose figures directory holds it

#### Scenario: Data row traced back
- **WHEN** a row of `f2_trajectories.csv` is read
- **THEN** it names `results/motco_analysis/stage_means.csv`, the row and column it was read from, and the value read
