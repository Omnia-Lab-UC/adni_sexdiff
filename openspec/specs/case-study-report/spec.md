# case-study-report Specification

## Purpose
Defines the `report` step: the case-study report of the ADNI sex × stage trajectory comparison, generated in full from the kept aggregate outputs of the pipeline, with every number copied and every interpretive sentence produced by the reading rules, and the `--check` mode that compares an existing report with the generated files cell by cell.

## Requirements

### Requirement: Inputs are the kept aggregate outputs only
The step SHALL read only the committed aggregate files of the pipeline, of the latent arm, of every export variant of `REPORT_EXPORT_VARIANTS`, of the CN / LMCI / AD arm and of the rank sweep: manifests, records, summaries, count and comparison tables, diagnostics files and the `nist_bridge` bridge table; and the committed copy of the cited MOTCO decision file. It SHALL open no participant-level file and SHALL NOT require one to be present.

#### Scenario: Clone without participant-level files
- **WHEN** `report` runs on a clone that holds the tracked files under `results/` and `references/` and none of `cohort.csv`, the export CSVs of the primary, of a variant or of the CN / LMCI / AD arm, `latent_scores.csv` or `analysis_metadata.csv`
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
- **THEN** it reads, under `results/motco_rank_sensitivity/`, per rank of `RANK_SENSITIVITY_LADDER` in ladder order the rank's `result.json`, `analysis_manifest.json` and `summary.md`, then the comparison's three files and the diagnostics' six files: 27 files

#### Scenario: Rank sweep input absent
- **WHEN** `results/motco_rank_sensitivity/rank_06/summary.md` does not exist
- **THEN** the step stops naming the file and the `rank-sensitivity` command, and writes nothing

#### Scenario: Operating-characteristics input
- **WHEN** the report runs on the committed outputs
- **THEN** it reads `references/motco_adni_design/adni_design_decision.json`: 146 files in all, 45 of them manifests

#### Scenario: Operating-characteristics input absent
- **WHEN** `references/motco_adni_design/adni_design_decision.json` does not exist
- **THEN** the step stops naming the file and the `git show` command that copies it from the pinned MOTCO commit, and writes nothing

### Requirement: Aggregate inputs are checked against their manifests
The step SHALL compare the sha256 of every aggregate file it reads with the value the file's own manifest records under `outputs`, and for the bridge table under `bridge.table` of its variant's export manifest, and SHALL stop before writing anything on a mismatch, naming the file, both hashes and the step to rerun.

#### Scenario: Edited record
- **WHEN** the primary's `result.json` hashes to a value other than the one `analysis_manifest.json` records
- **THEN** the step stops naming `result.json`, both hashes and `analyze`, and writes nothing

#### Scenario: Edited bridge table
- **WHEN** `bridge/nist_bridge.csv` hashes to a value other than the `bridge.table.sha256` of the `nist_bridge` export manifest
- **THEN** the step stops naming the bridge table, both hashes and the `export-sensitivity` command for `nist_bridge`, and writes nothing

### Requirement: The pipeline chain is checked end to end
The step SHALL verify every link of the pipeline chain: each manifest's recorded input hashes, from the clean manifests to the diagnostics of the arm, of every variant, of the CN / LMCI / AD arm and of the rank sweep, SHALL equal the hashes of the manifests and files now upstream, the primary's analysis, export and feature tables included wherever a manifest records them as its `reference`. A broken link SHALL stop the step naming the file, both hashes and the step to rerun.

#### Scenario: Export regenerated after the analysis
- **WHEN** the export manifest's sha256 differs from the value the primary's `analysis_manifest.json` records under its inputs
- **THEN** the step stops naming `manifest.json`, both hashes and `analyze`, and writes nothing

#### Scenario: Arm from a replaced primary
- **WHEN** the comparison manifest's `reference` records a `result.json` hash other than the primary's record now on disk
- **THEN** the step stops naming the file, both hashes and `latent-sensitivity`, and writes nothing

#### Scenario: Stale variant diagnostics
- **WHEN** a variant was rerun with `--force` after its diagnostics were written, so its diagnostics manifest records an analysis manifest hash other than the one on disk
- **THEN** the step stops naming the diagnostics manifest, both hashes and the `axis-diagnostics` command with the variant's three directories, and writes nothing

#### Scenario: Variant from a replaced primary export
- **WHEN** a variant export manifest's `reference` records a primary export manifest hash other than the one on disk
- **THEN** the step stops naming the variant export manifest, both hashes and the `export-sensitivity` command for that variant, and writes nothing

#### Scenario: CN / LMCI / AD arm from a replaced primary export
- **WHEN** the arm's export manifest records under `reference` a primary export manifest hash, or a feature-table hash, other than the primary export's now on disk
- **THEN** the step stops naming the arm's export manifest, the key, both hashes and the `stage-sensitivity` command, and writes nothing

#### Scenario: Stale CN / LMCI / AD arm diagnostics
- **WHEN** the arm was rerun with `--force` after its diagnostics were written, so its diagnostics manifest records an analysis manifest hash other than the one on disk
- **THEN** the step stops naming the diagnostics manifest, both hashes and the `axis-diagnostics` command with the arm's three directories, and writes nothing

#### Scenario: Rank from a replaced primary
- **WHEN** a rank's manifest records under `reference` a primary `result.json` or `analysis_manifest.json` hash other than the primary's now on disk
- **THEN** the step stops naming that rank's manifest, the key, both hashes and the `rank-sensitivity` command, and writes nothing

#### Scenario: Comparison from a replaced rank
- **WHEN** the comparison manifest records under `ranks` a rank's `analysis_manifest.json` hash other than the one on disk
- **THEN** the step stops naming the comparison manifest, the rank, both hashes and the `rank-sensitivity` command, and writes nothing

#### Scenario: Stale sweep diagnostics
- **WHEN** the sweep was rerun with `--force` after its diagnostics were written, so its diagnostics manifest records a rank-12 analysis manifest hash other than the one on disk
- **THEN** the step stops naming the diagnostics manifest, both hashes and the `axis-diagnostics` command with the top rank's analysis directory and the sweep's diagnostics directory, and writes nothing

### Requirement: Only reported, pinned and version-consistent runs are reported
The step SHALL stop, naming the manifest and the value, when the primary, the arm, an export variant, the CN / LMCI / AD arm or a rank of the sweep records `n_jobs` other than 1, when any manifest with a `numerics` block records `pinned` false, or when two manifests record different versions of MOTCO, scikit-learn or metabo_adni. A manifest without a `numerics` block SHALL be accepted and noted.

#### Scenario: Parallel primary
- **WHEN** the primary's manifest records `n_jobs` 4
- **THEN** the step stops naming `analysis_manifest.json` and 4, and writes nothing

#### Scenario: Unpinned arm
- **WHEN** the arm's manifest records `numerics.pinned` false
- **THEN** the step stops naming that manifest, and writes nothing

#### Scenario: Parallel variant
- **WHEN** the `per_run_standardized` analysis record holds `measurement.n_jobs` 4
- **THEN** the step stops naming that `result.json`, 4 and the `export-sensitivity` command for that variant without `--n-jobs`, and writes nothing

#### Scenario: Parallel CN / LMCI / AD arm
- **WHEN** the CN / LMCI / AD arm's analysis manifest records `settings.n_jobs` 4
- **THEN** the step stops naming that manifest, 4 and the `stage-sensitivity` command without `--n-jobs`, and writes nothing

#### Scenario: Parallel rank
- **WHEN** the rank-3 record holds `measurement.n_jobs` 4
- **THEN** the step stops naming that `result.json`, 4 and the `rank-sensitivity` command without `--n-jobs`, and writes nothing

#### Scenario: Manifest written before the numerics change
- **WHEN** the cohort manifest has no `numerics` block
- **THEN** the report's provenance says so for that step, and the step completes

### Requirement: The primary and the arm are identified before reporting
The step SHALL stop when the primary records a latent adjustment or its diagnostics record `is_primary` false, or when the arm's conditioning differs from `LATENT_SENSITIVITY_ARM` or its diagnostics record `is_primary` true.

#### Scenario: Arm directory given as the primary
- **WHEN** `--analysis-dir` names a directory whose record carries a `latent_adjustment` block
- **THEN** the step stops naming the directory and the setting, and writes nothing

### Requirement: Report content contract
The report SHALL be one Markdown file with these sections in order: summary; provenance; cohort; export; primary analysis; axis diagnostics of the primary; operating characteristics; latent-adjustment sensitivity; export sensitivity; stage-definition sensitivity; rank sensitivity; findings; reading rules; reproduction. The primary's statistics SHALL be given in full, each sensitivity beside the primary with a status per statistic, and every value SHALL be aggregate.

#### Scenario: Primary statistics
- **WHEN** the report is written
- **THEN** the primary's statistics are given with p-value, rejection and null summary, its rank, floor and eigengap beside `angle`, its covariate block and reference row

#### Scenario: Sections present
- **WHEN** the report is written
- **THEN** its level-2 headings are the fourteen sections in the order above, and the latent-adjustment section holds the comparison table with the primary row first, the arm's `latent_adjustment` block, the covariate roles and the arm's flagged diagnostic rows

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
Every number in the report SHALL be read from a record, a manifest, a CSV or the cited decision file and formatted with the digits of the summary it belongs to (six significant digits for record values, p-values as recorded, counts as integers, correlations and shares as `diagnostics.md` prints them, the decision's rates and standard errors at three decimals and its bound at four). The step SHALL compute no statistic, correlation, mean or count of its own.

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

### Requirement: Interpretive sentences are generated by rule
Each reading sentence in the report SHALL be produced from the rejection statuses by the code that writes `summary.md` and the four sensitivities' comparison documents (`latent_sensitivity.md`, `export_sensitivity.md`, `stage_sensitivity.md`, `rank_sensitivity.md`), string-equal across the documents. Besides the cited measurement's sentences, quoted verbatim, the report SHALL add no interpretive sentence, and the primary's status SHALL be the result wherever a sensitivity appears.

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

### Requirement: Reading rules carried verbatim
The report SHALL print verbatim in its reading-rules section, in order: `READING_RULES`, `OPERATING_CHARACTERISTICS_READING_RULES`, `LATENT_SENSITIVITY_READING_RULES`, each export variant group's rule set in registry order (`EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES`, `SCALE_VARIANT_READING_RULES`), `STAGE_SENSITIVITY_READING_RULES` and `RANK_SENSITIVITY_READING_RULES`. Beside every table that quotes a sensitivity it SHALL name that sensitivity's rules with `READING_RULES`.

#### Scenario: Rules string-equal
- **WHEN** the eight numbered lists of the reading-rules section are compared with the constants
- **THEN** each item is string-equal to its constant, in order

#### Scenario: Measurement rules after the reading rules
- **WHEN** the reading-rules section is written
- **THEN** `OPERATING_CHARACTERISTICS_READING_RULES` follows `READING_RULES` under its own heading, led by a line that names the change `adni-operating-characteristics` and states that the list was decided after every run and changes no constant, record or status

#### Scenario: Variant tables name their rules
- **WHEN** the summary and the export-sensitivity section quote a variant
- **THEN** the text that leads the variant's group names `READING_RULES` and the group's rule set: `EXPORT_VARIANT_READING_RULES` for `nist_bridge` and `per_run_standardized`, `NMR_MEMBERSHIP_READING_RULES` for `nmr_all_columns`, `SCALE_VARIANT_READING_RULES` for `raw_scale`, `log2_plus_one` and `glog`

#### Scenario: CN / LMCI / AD arm tables name their rules
- **WHEN** the summary and the stage-definition section quote the CN / LMCI / AD arm
- **THEN** the text that leads them names `READING_RULES` and `STAGE_SENSITIVITY_READING_RULES`

#### Scenario: Rank sweep tables name their rules
- **WHEN** the summary and the rank section quote the sweep
- **THEN** the text that leads them names `READING_RULES` and `RANK_SENSITIVITY_READING_RULES`

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

### Requirement: Check compares cell by cell and names every mismatch
With `--check`, the step SHALL regenerate the report from the inputs now on disk, with the date taken from the checked file's name, and compare the file with it: every table cell by cell and every other line line by line. Each mismatch SHALL be named (section, table, row key, column, the report's value and the generated one, or the line), the step SHALL exit non-zero on any mismatch and SHALL write nothing.

#### Scenario: Fresh report passes
- **WHEN** `report --check` runs on a report the step just wrote from unchanged inputs
- **THEN** it reports no mismatch and exits zero

#### Scenario: Edited digit
- **WHEN** one p-value in the report's statistics table is changed by hand
- **THEN** `report --check` names the section, the table, the row `delta` (or the edited statistic), the column, both values, and exits non-zero

#### Scenario: Regenerated input
- **WHEN** a results file the report quotes by hash was regenerated after the report was written
- **THEN** `report --check` names the provenance cell holding that file's hash with both values, and exits non-zero

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

#### Scenario: Report of the thirteen-section layout
- **WHEN** `report --check --out reports/motco-adni-2026-11-02-2.md` runs after the operating-characteristics section is added
- **THEN** the check stops naming the report, the absent section `Operating characteristics` and the command `git log -1 --format=%H -- reports/motco-adni-2026-11-02-2.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of an earlier layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-30.md` runs
- **THEN** the check stops naming the report, the absent sections `Operating characteristics` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-30.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the eleven-section layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-29.md` runs
- **THEN** the check stops naming the report, the absent sections `Operating characteristics`, `Stage-definition sensitivity` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-29.md`, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the first layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-28.md` runs
- **THEN** the check stops naming the report, the absent sections `Operating characteristics`, `Export sensitivity`, `Stage-definition sensitivity` and `Rank sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-28.md`, compares no cell, writes nothing and exits non-zero

### Requirement: Output discipline
The report SHALL be written to a temporary file and renamed when complete; an existing file at `--out` SHALL stop the step unless `--force`. After writing, the step SHALL parse the file through the check parser and verify that the parsed tables equal the generated ones.

#### Scenario: Existing report
- **WHEN** `--out` names a file that exists and `--force` is not given
- **THEN** the step stops naming the file and leaves it unchanged

#### Scenario: Parse-back
- **WHEN** the report is written
- **THEN** the step reports the number of tables and cells it parsed back, equal to the number generated, and no temporary file remains

### Requirement: No participant identifier and aggregate values only
The report and every progress line of the step SHALL hold no participant identifier and SHALL quote aggregate values only: counts, statistics, hashes, settings and constants.

#### Scenario: Identifier search
- **WHEN** the report is searched for a `rid` value or the token `RID`
- **THEN** only column-name mentions are found

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

### Requirement: Export variants are identified before reporting
The step SHALL stop, naming the directory, the setting and both values, when a variant's export, analysis or comparison manifest names another variant, when its export manifest's variant block differs from its `EXPORT_VARIANTS` entry, when its analysis records a latent adjustment, or when its diagnostics record `is_primary` true or another export variant.

#### Scenario: Variant directories swapped
- **WHEN** the `nist_bridge` directory under `--export-sensitivity-dir` holds the outputs of `per_run_standardized`
- **THEN** the step stops naming the directory, the variant it expects and the variant its manifests record, and writes nothing

#### Scenario: Registry entry moved after the run
- **WHEN** the `setting` of an `EXPORT_VARIANTS` entry differs from the `variant` block its export manifest recorded
- **THEN** the step stops naming the variant, `EXPORT_VARIANTS`, both values and the `export-sensitivity` command for that variant, and writes nothing

#### Scenario: Variant diagnostics read the primary
- **WHEN** a variant's diagnostics manifest records `is_primary` true
- **THEN** the step stops naming that manifest and the `axis-diagnostics` command with the variant's export, analysis and diagnostics directories, and writes nothing

### Requirement: The CN / LMCI / AD arm is identified before reporting
The step SHALL stop, naming the manifest, the setting and both values, when the arm's export manifest records a `stage_arm` block other than `STAGE_SENSITIVITY_ARM` or an export variant, when its analysis or comparison manifest names another arm, when its analysis records a latent adjustment, or when its diagnostics record `is_primary` true or another arm.

#### Scenario: Arm constant moved after the run
- **WHEN** a field of `STAGE_SENSITIVITY_ARM` differs from the `stage_arm` block the arm's export manifest recorded
- **THEN** the step stops naming that manifest, `STAGE_SENSITIVITY_ARM`, the field, both values and the `stage-sensitivity` command, and writes nothing

#### Scenario: Latent-adjusted analysis in the arm's directory
- **WHEN** the analysis under `--stage-sensitivity-dir` records a latent adjustment
- **THEN** the step stops naming the directory and the recorded setting, since the arm is not crossed with the latent adjustment, and writes nothing

#### Scenario: Arm diagnostics read the primary
- **WHEN** the arm's diagnostics manifest records `is_primary` true
- **THEN** the step stops naming that manifest and the `axis-diagnostics` command with the arm's export, analysis and diagnostics directories, and writes nothing

### Requirement: The rank sweep is identified before reporting
The step SHALL stop, naming the manifest, the setting and both values, when a rank directory holds another rank, another ladder or a latent adjustment, when a rank records a primary rank other than the primary record's, when the comparison records another ladder, other ranks or an anchor that is not equal at the primary record's rank, or when the sweep's diagnostics record `is_primary` true or a rank other than the ladder's diagnosed rank.

#### Scenario: Rank directories swapped
- **WHEN** the `rank_04` directory under `--rank-sensitivity-dir` holds the outputs of forced rank 6
- **THEN** the step stops naming the directory, the rank it expects and the rank its manifest and record hold, and writes nothing

#### Scenario: Ladder moved after the run
- **WHEN** a field of `RANK_SENSITIVITY_LADDER` differs from the ladder the comparison manifest or a rank's manifest recorded
- **THEN** the step stops naming that manifest, `RANK_SENSITIVITY_LADDER`, the field, both values and the `rank-sensitivity` command, and writes nothing

#### Scenario: Latent-adjusted analysis in a rank directory
- **WHEN** the analysis under `rank_09` records a latent adjustment
- **THEN** the step stops naming the directory and the recorded setting, since the sweep is not crossed with the latent adjustment, and writes nothing

#### Scenario: Anchor not equal
- **WHEN** the comparison manifest records the anchor as not equal, or at a rank other than the primary record's
- **THEN** the step stops naming the comparison manifest, the anchor's rank and the primary's, and the `rank-sensitivity` command, and writes nothing

#### Scenario: Sweep diagnostics read another analysis
- **WHEN** the sweep's diagnostics manifest records `is_primary` true, or a forced rank other than 12
- **THEN** the step stops naming that manifest and the `axis-diagnostics` command with the top rank's analysis directory and the sweep's diagnostics directory, and writes nothing

### Requirement: The report covers the variants it names
The step SHALL read, check and quote exactly the export variants of `REPORT_EXPORT_VARIANTS`, in its order, a subsequence of `EXPORT_VARIANTS`. A registered variant outside it SHALL NOT be read or required, and SHALL leave the report body unchanged. The step SHALL name it on a progress line, never in the body. A change that adds a variant to the report SHALL extend `REPORT_EXPORT_VARIANTS` and re-issue the report.

#### Scenario: Pin covers every registered variant
- **WHEN** the report runs on the committed outputs
- **THEN** it reads, checks and quotes `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog` in registry order, and no progress line names an uncovered variant

#### Scenario: A third variant registered
- **WHEN** `REPORT_EXPORT_VARIANTS` names `nist_bridge` and `per_run_standardized` only, and the outputs of the four variants registered after them are absent
- **THEN** `report` reads 94 files, no line of the body names `nmr_all_columns`, `raw_scale`, `log2_plus_one` or `glog`, and one progress line per uncovered variant says that it is registered and not covered by this report

#### Scenario: Scale variants registered outside the pin
- **WHEN** `EXPORT_VARIANTS` holds the six variants, `REPORT_EXPORT_VARIANTS` names the first three only, and the outputs of the three scale variants are absent
- **THEN** `report` reads 107 files, no line of the body names `raw_scale`, `log2_plus_one` or `glog`, and one progress line per scale variant says that it is registered and not covered by this report

#### Scenario: Newest report still checks
- **WHEN** `report --check` runs on the newest committed report, written under the current layout and pin, on the tree it was written from
- **THEN** it compares every table and line with no mismatch and exits 0; a report of an earlier layout or pin stops at the section or variant gate instead

#### Scenario: Pin out of order
- **WHEN** `REPORT_EXPORT_VARIANTS` names a variant that is not in `EXPORT_VARIANTS`, or lists two variants out of registry order
- **THEN** importing the constants fails naming both constants, before any step runs

### Requirement: Check stops on a report that lists other export variants
After a report's level-2 headings match the current sections and before any input gate, `--check` SHALL compare the export variants the report lists, its level-3 headings ``Export variant `<name>` `` in the export-sensitivity section in order, with `REPORT_EXPORT_VARIANTS`. On a difference it SHALL stop, naming the report, the absent and extra variants and how to find the revision that committed it, compare no cell and write nothing.

#### Scenario: Report of the three-variant pin
- **WHEN** `report --check` runs on a report with the fourteen current sections whose export-sensitivity section lists `nist_bridge`, `per_run_standardized` and `nmr_all_columns` only
- **THEN** the check stops naming the report, the absent variants `raw_scale`, `log2_plus_one` and `glog`, no extra variant and the `git log -1 --format=%H -- <report>` command, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the two-variant pin
- **WHEN** `report --check` runs on a report with the fourteen current sections whose export-sensitivity section lists `nist_bridge` and `per_run_standardized` only
- **THEN** the check stops naming the report, the absent variants `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`, no extra variant and the `git log -1 --format=%H -- <report>` command, compares no cell, writes nothing and exits non-zero

#### Scenario: Committed reports of earlier pins
- **WHEN** `report --check --out reports/motco-adni-2026-11-02.md` or `--out reports/motco-adni-2026-10-31.md` runs
- **THEN** the check stops at the section gate, naming the absent section `Operating characteristics`, before the variant gate, compares no cell, writes nothing and exits non-zero

#### Scenario: Report of the current pin
- **WHEN** `report --check` runs on a report the step just wrote
- **THEN** the report's variants are `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog` in that order, and the check goes on to the input gates and the comparison

#### Scenario: Variants out of order
- **WHEN** a report lists the variants of `REPORT_EXPORT_VARIANTS` in another order
- **THEN** the check stops naming the report, no absent and no extra variant, that the order differs, and the `git log` command, and writes nothing

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

### Requirement: The cited measurement is pinned and checked
The step SHALL read the cited MOTCO operating-characteristics decision only from its committed copy, never from a MOTCO clone. Before anything is written it SHALL stop when the copy is absent, when its sha256 differs from `OPERATING_CHARACTERISTICS_SOURCE`, when its verdict differs from the constant's or it is marked indicative, or when a value of its `adni_reference` differs from the committed value it describes at the decision's digits.

#### Scenario: Reference holds on the committed outputs
- **WHEN** the report runs on the committed outputs and `references/motco_adni_design/adni_design_decision.json`
- **THEN** every key of `adni_reference` equals its committed source at the decision's digits: the primary record's rank, `cv_mean_auroc`, p-values, pooled relative eigengap, `angle` null q95, design columns and `phase[ADNI2GO]` reference value; the export manifest's phase offset and kept features per block; the primary diagnostics' `pls_0` correlation with `phase`; and the lowest and highest `cv_mean_auroc` of the nine CV-selected analyses

#### Scenario: Edited copy
- **WHEN** one byte of the copy differs from the file at the pinned MOTCO commit
- **THEN** the step stops naming the copy, both sha256 values and the command that restores it from the pinned commit, and writes nothing

#### Scenario: Primary regenerated with another rank
- **WHEN** the committed primary record selects a rank other than the 8 that `adni_reference.selected_lv` records
- **THEN** the step stops naming `adni_reference.selected_lv`, both values and that the measurement was calibrated against another analysis, so citing a measurement for this one is a new change, and writes nothing

#### Scenario: No MOTCO clone
- **WHEN** the report runs on a clone with no MOTCO repository beside it
- **THEN** it reads the copy only and writes the report

### Requirement: The cited measurement is quoted verbatim
The report SHALL quote the decision's verdict, its size sentence, its per-statistic statements and its decision rule verbatim, and SHALL print `OPERATING_CHARACTERISTICS_READING_RULES` as the reading of the measurement. It SHALL add no other sentence about the measurement, and SHALL NOT reread any sensitivity's status from the measured size or power.

#### Scenario: Statements string-equal
- **WHEN** the operating-characteristics section and the summary are compared with the decision file
- **THEN** the verdict, the size sentence and the three statements for `delta`, `angle` and `shape` are string-equal to the file's `verdict`, `size.sentence` and `statements`

#### Scenario: Summary carries the measurement
- **WHEN** the report is written on the committed outputs
- **THEN** the summary, after the primary's reading bullets, names the verdict `non_rejections_uninformative`, cites `OPERATING_CHARACTERISTICS_READING_RULES` and the operating-characteristics section, and lists the three statements

#### Scenario: No sensitivity reread
- **WHEN** the sensitivity sections of the report are compared with those generated before this change on the same inputs
- **THEN** their tables and lines are unchanged except for section numbers in cross-references, and no line of a sensitivity section names the measurement
