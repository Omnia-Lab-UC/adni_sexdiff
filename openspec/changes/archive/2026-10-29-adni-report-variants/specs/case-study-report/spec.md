## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Inputs are the kept aggregate outputs only
The step SHALL read only the committed aggregate files of the pipeline, of the latent arm and of every export variant of `EXPORT_VARIANTS`: manifests, records, summaries, count and comparison tables, diagnostics files and the `nist_bridge` bridge table. It SHALL open no participant-level file and SHALL NOT require one to be present.

#### Scenario: Clone without participant-level files
- **WHEN** `report` runs on a clone that holds the tracked files under `results/` and none of `cohort.csv`, the export CSVs of the primary or of a variant, `latent_scores.csv` or `analysis_metadata.csv`
- **THEN** it writes the report, and every hash it quotes for a participant-level file is the value a manifest records

#### Scenario: Input absent
- **WHEN** `results/motco_latent_sensitivity/comparison/latent_sensitivity.csv` does not exist
- **THEN** the step stops naming the file and the `latent-sensitivity` command, and writes nothing

#### Scenario: Variant inputs
- **WHEN** the report runs with the two registered variants
- **THEN** it reads, per variant in registry order, `motco_input/manifest.json`, the analysis' `result.json`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six files, and for `nist_bridge` `bridge/nist_bridge.csv`: 53 files in all, with the 26 of the primary and the arm

#### Scenario: Variant input absent
- **WHEN** `results/motco_export_sensitivity/per_run_standardized/diagnostics/diagnostics_manifest.json` does not exist
- **THEN** the step stops naming the file and the `axis-diagnostics` command with that variant's export, analysis and diagnostics directories, and writes nothing

### Requirement: Aggregate inputs are checked against their manifests
The step SHALL compare the sha256 of every aggregate file it reads with the value the file's own manifest records under `outputs`, and for the bridge table under `bridge.table` of its variant's export manifest, and SHALL stop before writing anything on a mismatch, naming the file, both hashes and the step to rerun.

#### Scenario: Edited record
- **WHEN** the primary's `result.json` hashes to a value other than the one `analysis_manifest.json` records
- **THEN** the step stops naming `result.json`, both hashes and `analyze`, and writes nothing

#### Scenario: Edited bridge table
- **WHEN** `bridge/nist_bridge.csv` hashes to a value other than the `bridge.table.sha256` of the `nist_bridge` export manifest
- **THEN** the step stops naming the bridge table, both hashes and the `export-sensitivity` command for `nist_bridge`, and writes nothing

### Requirement: The pipeline chain is checked end to end
The step SHALL verify every link of the pipeline chain: each manifest's recorded input hashes, from the clean manifests to the arm's and every variant's diagnostics, SHALL equal the hashes of the manifests and files now upstream, the primary's analysis and export included wherever a manifest records them as its `reference`. A broken link SHALL stop the step naming the file, both hashes and the step to rerun.

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

### Requirement: Only reported, pinned and version-consistent runs are reported
The step SHALL stop, naming the manifest and the value, when the primary, the arm or an export variant records `n_jobs` other than 1, when any manifest with a `numerics` block records `pinned` false, or when two manifests record different versions of MOTCO, scikit-learn or metabo_adni. A manifest without a `numerics` block SHALL be accepted and noted.

#### Scenario: Parallel primary
- **WHEN** the primary's manifest records `n_jobs` 4
- **THEN** the step stops naming `analysis_manifest.json` and 4, and writes nothing

#### Scenario: Unpinned arm
- **WHEN** the arm's manifest records `numerics.pinned` false
- **THEN** the step stops naming that manifest, and writes nothing

#### Scenario: Parallel variant
- **WHEN** the `per_run_standardized` analysis record holds `measurement.n_jobs` 4
- **THEN** the step stops naming that `result.json`, 4 and the `export-sensitivity` command for that variant without `--n-jobs`, and writes nothing

#### Scenario: Manifest written before the numerics change
- **WHEN** the cohort manifest has no `numerics` block
- **THEN** the report's provenance says so for that step, and the step completes

### Requirement: Report content contract
The report SHALL be one Markdown file with these sections in order: summary; provenance; cohort; export; primary analysis; axis diagnostics of the primary; latent-adjustment sensitivity; export sensitivity; findings; reading rules; reproduction. The primary's statistics SHALL be given in full, the arm and each export variant beside the primary with a status per statistic, and every value SHALL be aggregate.

#### Scenario: Primary statistics
- **WHEN** the report is written
- **THEN** the primary's statistics are given with p-value, rejection and null summary, its rank, floor and eigengap beside `angle`, its covariate block and reference row

#### Scenario: Sections present
- **WHEN** the report is written
- **THEN** its level-2 headings are the eleven sections in the order above, and the latent-adjustment section holds the comparison table with the primary row first, the arm's `latent_adjustment` block, the covariate roles and the arm's flagged diagnostic rows

#### Scenario: Diagnostics quoted
- **WHEN** the report is written on the committed outputs
- **THEN** the primary's diagnostics section lists every flagged latent-component and block-PC row of `axis_correlations.csv` and `block_pcs.csv`, the components table with the loading share per block, and each block's first PC against `phase` beside the export's recorded value

#### Scenario: Export sensitivity section
- **WHEN** the report is written on the committed outputs
- **THEN** the export-sensitivity section holds the statistics table with the primary row first and one row per variant in registry order, each with its status; each variant's rank, floor and eigengap beside `angle`; the latent spaces; the run offset per block of the primary export and of each variant export; each variant export's counts beside its predeclared ones; the bridged metabolites per kit beside the predeclared counts and the unbridged metabolites; each variant's flagged diagnostic rows, components and block PCs; and each variant analysis' `cli_equivalent`

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

### Requirement: Interpretive sentences are generated by rule
Each reading sentence in the report SHALL be produced from the rejection statuses by the same code that writes `summary.md`, `latent_sensitivity.md` and `export_sensitivity.md`, so that the sentences are string-equal across the documents. The report SHALL add no other interpretive sentence, and the primary's status SHALL be the result wherever the arm or a variant appears.

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

### Requirement: Reading rules carried verbatim
The report SHALL print `READING_RULES`, then `LATENT_SENSITIVITY_READING_RULES`, then `EXPORT_VARIANT_READING_RULES` verbatim in its reading-rules section. It SHALL name `LATENT_SENSITIVITY_READING_RULES` beside every table that quotes the arm and `EXPORT_VARIANT_READING_RULES` beside every table that quotes a variant, each with `READING_RULES`.

#### Scenario: Rules string-equal
- **WHEN** the three numbered lists of the reading-rules section are compared with the constants
- **THEN** each item is string-equal to its constant, in order

#### Scenario: Variant tables name their rules
- **WHEN** the summary and the export-sensitivity section quote a variant
- **THEN** the text that leads them names `READING_RULES` and `EXPORT_VARIANT_READING_RULES`

### Requirement: Check selects the report and reruns the gates
Without `--out`, `--check` SHALL read the newest `reports/motco-adni-<date>.md` by date. Before any other gate, a report whose level-2 headings differ from the current sections SHALL stop the check, naming the report, the sections it lacks or adds, and how to find the revision that committed it. The check SHALL then run every gate of the write mode before comparing, so a broken chain or an unreported run fails the check naming the cause.

#### Scenario: No report
- **WHEN** `reports/` holds no `motco-adni-*.md` and `--out` is not given
- **THEN** `report --check` stops naming the directory and the pattern

#### Scenario: Broken chain at check time
- **WHEN** the export manifest was regenerated after the primary and `report --check` runs
- **THEN** the check stops naming `manifest.json`, both hashes and `analyze`, before any cell is compared

#### Scenario: Report of an earlier layout
- **WHEN** `report --check --out reports/motco-adni-2026-10-28.md` runs after this change
- **THEN** the check stops naming the report, the absent section `Export sensitivity` and the command `git log -1 --format=%H -- reports/motco-adni-2026-10-28.md`, compares no cell, writes nothing and exits non-zero
