# Spec Delta

## Purpose

Defines the `report` step: the case-study report of the ADNI sex × stage trajectory comparison, generated in full from the kept aggregate outputs of the pipeline, with every number copied and every interpretive sentence produced by the reading rules, and the `--check` mode that compares an existing report with the generated files cell by cell.

## ADDED Requirements

### Requirement: Inputs are the kept aggregate outputs only
The step SHALL read only committed aggregate files: the clean manifests, `stage_counts.csv` and the cohort manifest, the export manifest, the primary's `result.json`, `analysis_manifest.json` and `summary.md`, the primary diagnostics' six files, and under the sensitivity root the arm's three aggregate analysis files, the comparison's three files and the arm diagnostics' six files. It SHALL open no participant-level file and SHALL NOT require one to be present.

#### Scenario: Clone without participant-level files
- **WHEN** `report` runs on a clone that holds the tracked files under `results/` and none of `cohort.csv`, the export CSVs, `latent_scores.csv` or `analysis_metadata.csv`
- **THEN** it writes the report, and every hash it quotes for a participant-level file is the value a manifest records

#### Scenario: Input absent
- **WHEN** `results/motco_latent_sensitivity/comparison/latent_sensitivity.csv` does not exist
- **THEN** the step stops naming the file and the `latent-sensitivity` command, and writes nothing

### Requirement: Aggregate inputs are checked against their manifests
The step SHALL compare the sha256 of every aggregate file it reads with the value the file's own manifest records under `outputs`, and SHALL stop before writing anything on a mismatch, naming the file, both hashes and the step to rerun.

#### Scenario: Edited record
- **WHEN** the primary's `result.json` hashes to a value other than the one `analysis_manifest.json` records
- **THEN** the step stops naming `result.json`, both hashes and `analyze`, and writes nothing

### Requirement: The pipeline chain is checked end to end
The step SHALL verify every link of the pipeline chain: each manifest's recorded input hashes, from the clean manifests to the arm diagnostics, SHALL equal the hashes of the manifests and files now upstream, the primary's record and manifest included as the `reference` of the arm and of the comparison. A broken link SHALL stop the step naming the file, both hashes and the step to rerun.

#### Scenario: Export regenerated after the analysis
- **WHEN** the export manifest's sha256 differs from the value the primary's `analysis_manifest.json` records under its inputs
- **THEN** the step stops naming `manifest.json`, both hashes and `analyze`, and writes nothing

#### Scenario: Arm from a replaced primary
- **WHEN** the comparison manifest's `reference` records a `result.json` hash other than the primary's record now on disk
- **THEN** the step stops naming the file, both hashes and `latent-sensitivity`, and writes nothing

### Requirement: Only reported, pinned and version-consistent runs are reported
The step SHALL stop, naming the manifest and the value, when the primary or the arm records `n_jobs` other than 1, when any manifest with a `numerics` block records `pinned` false, or when two manifests record different versions of MOTCO, scikit-learn or metabo_adni. A manifest without a `numerics` block SHALL be accepted and noted.

#### Scenario: Parallel primary
- **WHEN** the primary's manifest records `n_jobs` 4
- **THEN** the step stops naming `analysis_manifest.json` and 4, and writes nothing

#### Scenario: Unpinned arm
- **WHEN** the arm's manifest records `numerics.pinned` false
- **THEN** the step stops naming that manifest, and writes nothing

#### Scenario: Manifest written before the numerics change
- **WHEN** the cohort manifest has no `numerics` block
- **THEN** the report's provenance says so for that step, and the step completes

### Requirement: The primary and the arm are identified before reporting
The step SHALL stop when the primary records a latent adjustment or its diagnostics record `is_primary` false, or when the arm's conditioning differs from `LATENT_SENSITIVITY_ARM` or its diagnostics record `is_primary` true.

#### Scenario: Arm directory given as the primary
- **WHEN** `--analysis-dir` names a directory whose record carries a `latent_adjustment` block
- **THEN** the step stops naming the directory and the setting, and writes nothing

### Requirement: Report content contract
The report SHALL be one Markdown file with these sections in order: summary; provenance; cohort; export; primary analysis; axis diagnostics of the primary; latent-adjustment sensitivity; findings; reading rules; reproduction. The primary's statistics SHALL be given with p-value, rejection and null summary, its rank, floor and eigengap beside `angle`, its covariate block and reference row; the arm SHALL be given beside the primary with a status per statistic; every value SHALL be aggregate.

#### Scenario: Sections present
- **WHEN** the report is written
- **THEN** its level-2 headings are the ten sections in the order above, and the latent-adjustment section holds the comparison table with the primary row first, the arm's `latent_adjustment` block, the covariate roles and the arm's flagged diagnostic rows

#### Scenario: Diagnostics quoted
- **WHEN** the report is written on the committed outputs
- **THEN** the primary's diagnostics section lists every flagged latent-component and block-PC row of `axis_correlations.csv` and `block_pcs.csv`, the components table with the loading share per block, and each block's first PC against `phase` beside the export's recorded value

### Requirement: Every number is pasted from the generated files
Every number in the report SHALL be read from a record, a manifest or a CSV and formatted with the digits of the summary it belongs to (six significant digits for record values, p-values as recorded, counts as integers, correlations and shares as `diagnostics.md` prints them). The step SHALL compute no statistic, correlation, mean or count of its own.

#### Scenario: Statistics equal the record
- **WHEN** the report's statistics table is compared with `result.json`
- **THEN** every observed value, p-value and null mean, sd and q95 equals the record's value at the printed digits, and the rank equals `latent.selected_lv`

#### Scenario: Counts equal the tables
- **WHEN** the report's cohort tables are compared with `stage_counts.csv` and the cohort manifest
- **THEN** every count and every descriptive equals the source value, and no cell is derived by the step

### Requirement: Interpretive sentences are generated by rule
Each reading sentence in the report SHALL be produced from the rejection statuses by the same code that writes `summary.md` and `latent_sensitivity.md`, so that the sentences are string-equal across the three documents. The report SHALL add no other interpretive sentence, and the primary's status SHALL be the result wherever the arm appears.

#### Scenario: Non-rejection wording
- **WHEN** `angle` is not rejected in the primary
- **THEN** the report states that the result is uninformative about orientation, in the sentence `summary.md` prints

#### Scenario: Arm status wording
- **WHEN** the primary and the arm both leave `delta` unrejected
- **THEN** the report marks the status `same`, states that the arm's non-rejection is weaker than the primary's and that neither is evidence that the sexes' trajectories agree, in the sentence `latent_sensitivity.md` prints

### Requirement: Reading rules carried verbatim
The report SHALL print `READING_RULES` and then `LATENT_SENSITIVITY_READING_RULES` verbatim in its reading-rules section, and SHALL name both constants beside every table that quotes the arm.

#### Scenario: Rules string-equal
- **WHEN** the two numbered lists of the reading-rules section are compared with the constants
- **THEN** each item is string-equal to its constant, in order

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
Without `--out`, `--check` SHALL read the newest `reports/motco-adni-<date>.md` by date. The check SHALL run every gate of the write mode before comparing, so a broken chain or an unreported run fails the check naming the cause.

#### Scenario: No report
- **WHEN** `reports/` holds no `motco-adni-*.md` and `--out` is not given
- **THEN** `report --check` stops naming the directory and the pattern

#### Scenario: Broken chain at check time
- **WHEN** the export manifest was regenerated after the primary and `report --check` runs
- **THEN** the check stops naming `manifest.json`, both hashes and `analyze`, before any cell is compared

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

#### Scenario: Dirty revision
- **WHEN** a manifest records `git_revision.dirty` true
- **THEN** the findings section names the step and the revision, and the report is still written
