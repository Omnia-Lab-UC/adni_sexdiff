## ADDED Requirements

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
