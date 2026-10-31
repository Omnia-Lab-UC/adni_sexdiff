# case-study-report Specification

## Purpose
Defines the `report` step: the case-study report of the ADNI sex × stage trajectory comparison, generated in full from the kept aggregate outputs of the pipeline, with every number copied and every interpretive sentence produced by the reading rules, and the `--check` mode that compares an existing report with the generated files cell by cell.

## Requirements

### Requirement: Inputs are the kept aggregate outputs only
The step SHALL read only the committed aggregate files of the pipeline, of the latent arm, of every export variant of `REPORT_EXPORT_VARIANTS`, of the CN / LMCI / AD arm and of the rank sweep: manifests, records, summaries, count and comparison tables, diagnostics files and the `nist_bridge` bridge table. It SHALL open no participant-level file and SHALL NOT require one to be present.

#### Scenario: Clone without participant-level files
- **WHEN** `report` runs on a clone that holds the tracked files under `results/` and none of `cohort.csv`, the export CSVs of the primary, of a variant or of the CN / LMCI / AD arm, `latent_scores.csv` or `analysis_metadata.csv`
- **THEN** it writes the report, and every hash it quotes for a participant-level file is the value a manifest records

#### Scenario: Input absent
- **WHEN** `results/motco_latent_sensitivity/comparison/latent_sensitivity.csv` does not exist
- **THEN** the step stops naming the file and the `latent-sensitivity` command, and writes nothing

#### Scenario: Variant inputs
- **WHEN** the report runs with the two variants of `REPORT_EXPORT_VARIANTS`
- **THEN** it reads, per variant in that order, `motco_input/manifest.json`, the analysis' `result.json`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six files, and for `nist_bridge` `bridge/nist_bridge.csv`: 27 files, beside the 26 of the primary and the arm

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
- **THEN** it reads, under `results/motco_rank_sensitivity/`, per rank of `RANK_SENSITIVITY_LADDER` in ladder order the rank's `result.json`, `analysis_manifest.json` and `summary.md`, then the comparison's three files and the diagnostics' six files: 27 files, 93 in all

#### Scenario: Rank sweep input absent
- **WHEN** `results/motco_rank_sensitivity/rank_06/summary.md` does not exist
- **THEN** the step stops naming the file and the `rank-sensitivity` command, and writes nothing

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
- **THEN** the export-sensitivity section holds the statistics table with the primary row first and one row per variant in registry order, each with its status; each variant's rank, floor and eigengap beside `angle`; the latent spaces; the run offset per block of the primary export and of each variant export; each variant export's counts beside its predeclared ones; the bridged metabolites per kit beside the predeclared counts and the unbridged metabolites; each variant's flagged diagnostic rows, components and block PCs; and each variant analysis' `cli_equivalent`

#### Scenario: Stage-definition sensitivity section
- **WHEN** the report is written on the committed outputs
- **THEN** the stage-definition section holds the statistics table with the primary row first and the CN / LMCI / AD arm's row, each with its status; both ranks, floors and eigengaps beside `angle`; the latent spaces; the arm's definition with the participants kept and dropped by `dx_bl` and sex, the sex × stage cells, the runs within each stage and the covariate levels of the primary and the arm; the run offset per block of both beside the arm's predeclared counts; the arm export's counts beside `STAGE_SENSITIVITY_EXPECTED_COUNTS`; the arm's flagged diagnostic rows, components and block PCs; and the arm analysis' `cli_equivalent`

#### Scenario: Rank sensitivity section
- **WHEN** the report is written on the committed outputs
- **THEN** the rank section holds the statistics table with, per statistic, the primary row first and one row per rank in ladder order, each with its rank and status; the latent spaces of the primary and every rank with each `angle` null summary; the anchor and the nesting per rank as the comparison manifest records them; the anchor rank, the comparison rows and each rank's selection, rank and CV repeats beside `RANK_SENSITIVITY_EXPECTED_COUNTS`; the top rank's flagged diagnostic rows, components and block PCs; and each rank's `cli_equivalent`

#### Scenario: QC inputs in the provenance
- **WHEN** the report is written on the committed outputs
- **THEN** the provenance lists the two QC archives and the four NIST workbooks with their sha256 beside the predeclared values, as the `nist_bridge` export manifest records them

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

### Requirement: Reading rules carried verbatim
The report SHALL print `READING_RULES`, then `LATENT_SENSITIVITY_READING_RULES`, `EXPORT_VARIANT_READING_RULES`, `STAGE_SENSITIVITY_READING_RULES` and `RANK_SENSITIVITY_READING_RULES` verbatim in its reading-rules section. Beside every table that quotes a sensitivity it SHALL name that sensitivity's rules, each with `READING_RULES`.

#### Scenario: Rules string-equal
- **WHEN** the five numbered lists of the reading-rules section are compared with the constants
- **THEN** each item is string-equal to its constant, in order

#### Scenario: Variant tables name their rules
- **WHEN** the summary and the export-sensitivity section quote a variant
- **THEN** the text that leads them names `READING_RULES` and `EXPORT_VARIANT_READING_RULES`

#### Scenario: CN / LMCI / AD arm tables name their rules
- **WHEN** the summary and the stage-definition section quote the CN / LMCI / AD arm
- **THEN** the text that leads them names `READING_RULES` and `STAGE_SENSITIVITY_READING_RULES`

#### Scenario: Rank sweep tables name their rules
- **WHEN** the summary and the rank section quote the sweep
- **THEN** the text that leads them names `READING_RULES` and `RANK_SENSITIVITY_READING_RULES`

### Requirement: Deterministic report body
The report body SHALL depend only on the input files and the report's file name: the date SHALL appear in the file name and the title only, and no revision, host, time or runtime of the report run SHALL be written. Two runs on the same inputs to the same path SHALL be byte-identical.

#### Scenario: Rerun with force
- **WHEN** `report --force` runs twice to the same `--out` on unchanged inputs
- **THEN** the two files have equal sha256

#### Scenario: Another date
- **WHEN** the report is written to a file whose name carries another date
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
Without `--out`, `--check` SHALL read the newest `reports/motco-adni-<date>.md` by date. Before any other gate, a report whose level-2 headings differ from the current sections SHALL stop the check, naming the report, the sections it lacks or adds, and how to find the revision that committed it. The check SHALL then run every gate of the write mode before comparing, so a broken chain or an unreported run fails the check naming the cause.

#### Scenario: No report
- **WHEN** `reports/` holds no `motco-adni-*.md` and `--out` is not given
- **THEN** `report --check` stops naming the directory and the pattern

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

#### Scenario: A third variant registered
- **WHEN** `EXPORT_VARIANTS` holds `nist_bridge`, `per_run_standardized` and `nmr_all_columns`, `REPORT_EXPORT_VARIANTS` the first two, and `results/motco_export_sensitivity/nmr_all_columns/` is absent
- **THEN** `report` reads 93 files, writes a body byte-identical to the one before `nmr_all_columns` was registered, and prints that `nmr_all_columns` is registered and not covered by this report

#### Scenario: Newest report still checks
- **WHEN** `report --check` runs on the newest committed report after `nmr_all_columns` is registered and its outputs are committed
- **THEN** it compares every table and line with no mismatch and exits 0

#### Scenario: Pin out of order
- **WHEN** `REPORT_EXPORT_VARIANTS` names a variant that is not in `EXPORT_VARIANTS`, or lists two variants out of registry order
- **THEN** importing the constants fails naming both constants, before any step runs
