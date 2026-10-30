# motco-rank-sensitivity Specification

## Purpose
Defines the `rank-sensitivity` step: the predeclared rank sweep of the ADNI sex × stage trajectory comparison. It reruns the primary analysis at each rank of a fixed ladder, with the rank forced and every other setting the primary's, after a gate proving that a forced run at the primary's rank reproduces the primary, and compares every rank with the primary, which stays primary.

## Requirements

### Requirement: MOTCO version and rank floor checked before any input is read
The step SHALL apply the gates of `analyze` before reading any input: the installed MOTCO SHALL be at least `ANALYSIS_MOTCO_MIN_VERSION` (0.10.0), and MOTCO's default rank floor SHALL equal `ANALYSIS_RANK_FLOOR` (2). A failure SHALL stop the step naming both values, without writing anything.

#### Scenario: Older MOTCO installed
- **WHEN** the installed MOTCO reports version 0.9.0
- **THEN** the step stops naming 0.9.0 and 0.10.0, and no input file is read

### Requirement: Inputs are the primary export and the primary analysis
The step SHALL read only the primary export's five files and the primary analysis' `result.json` and `analysis_manifest.json`: no data-root file, no cleaned table, no cohort table, no feature table, nothing under a diagnostics directory. A missing input SHALL stop the step naming the file and the command that produces it, and nothing SHALL be written.

#### Scenario: Primary analysis absent
- **WHEN** `results/motco_analysis/` does not exist
- **THEN** the step stops naming the directory and the `analyze` command, and no output directory is created

#### Scenario: Inputs listed
- **WHEN** the step finishes
- **THEN** the comparison manifest lists exactly the seven input files with their sha256

### Requirement: The primary analysis is a chained reference
Before any rank runs, the step SHALL check that the export files hash to the values the export manifest records, that the primary manifest records for each export file and the export manifest the sha256 now on disk, that the primary records no latent adjustment, and that it was made under the installed MOTCO with `ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS`. On a difference it SHALL stop naming the file or setting, both values and the step to rerun.

#### Scenario: Export regenerated after the primary
- **WHEN** `nmr.csv` hashes to a value other than the one `results/motco_analysis/analysis_manifest.json` records
- **THEN** the step stops naming `nmr.csv`, both hashes and the `analyze` command, and writes nothing

#### Scenario: Arm given as the primary
- **WHEN** `--analysis-dir` names a directory whose record carries a `latent_adjustment` block
- **THEN** the step stops naming the directory and the setting, and writes nothing

### Requirement: One predeclared ladder
The step SHALL run exactly the ranks of `RANK_SENSITIVITY_LADDER` (2, 3, 4, 6, 9, 12), each once, in ladder order. The ladder SHALL be a constant, never a flag, its lowest rank SHALL equal `ANALYSIS_RANK_FLOOR`, and no rank SHALL be added, dropped or chosen from a result.

#### Scenario: Ranks run
- **WHEN** the step finishes on the committed export
- **THEN** it has written one analysis directory per rank, `rank_02`, `rank_03`, `rank_04`, `rank_06`, `rank_09` and `rank_12`, each recording component selection `forced` and its rank

#### Scenario: No rank flag
- **WHEN** `adni-sexdiff rank-sensitivity --help` is read
- **THEN** no flag sets, adds or removes a rank

### Requirement: Anchor gate at the primary's rank
Before any rank of the ladder runs, the step SHALL run one forced analysis at the primary record's rank. Its statistics, p-values, null summaries, `config_spectrum` and rank SHALL equal the primary record's (at another `n_jobs`, those the draws do not change), and its `latent_scores.csv`, `pls_loadings.csv` and `stage_means.csv` SHALL hash to the primary manifest's values. A difference SHALL stop the step, naming the field or file and both values.

#### Scenario: Anchor reproduces the primary
- **WHEN** the step runs pinned on the committed export and primary
- **THEN** the forced run at rank 8 equals the primary in every compared field and file, the comparison manifest records the anchor with each comparison true, and no anchor directory remains

#### Scenario: Anchor differs
- **WHEN** the anchor's `delta` p-value differs from the primary record's
- **THEN** the step stops naming `delta`, `p_values` and both values, and no rank directory or comparison is created

### Requirement: Each rank at the primary's settings
Each rank SHALL be one call of MOTCO's trajectory-analysis entry point on the primary export with `forced_components` set to the rank and every other setting the primary's: `ANALYSIS_COVARIATES` with their coding, `ANALYSIS_PERMUTATIONS` and `ANALYSIS_SEED` at every rank, `ANALYSIS_RANK_FLOOR`, no latent adjustment and MOTCO's other defaults. The step SHALL NOT rerun the primary or assemble a result from MOTCO's primitives.

#### Scenario: Reproduction by MOTCO's CLI
- **WHEN** the `cli_equivalent` of `rank_04/analysis_manifest.json` is run with `motco analyze` into a scratch directory
- **THEN** its `statistics`, `p_values`, `null_summary` and rank equal the rank-4 record's, and its `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` are byte-identical

#### Scenario: Nested latent space
- **WHEN** the ranks have been written on the committed export
- **THEN** the latent scores of each rank are the first columns of `rank_12`'s, and for the ranks below 8 the first columns of the primary's

### Requirement: Each rank records its provenance
Each rank's `analysis_manifest.json` SHALL record step `rank-sensitivity`, the ladder by constant name, the forced rank, the primary export's five files as its inputs, the primary analysis as its reference (directory, `result.json` and manifest sha256, rank), the anchor's result, every setting as passed, a `cli_equivalent` with the forced rank, the versions, the git revision, the `numerics` block, the predeclared counts beside the observed ones, output hashes and findings.

#### Scenario: Manifest after the real run
- **WHEN** the step finishes on a data machine
- **THEN** each rank manifest records step `rank-sensitivity`, its forced rank, latent adjustment none, the reference primary's two hashes, MOTCO 0.10.0, `n_jobs` 1 and `numerics.pinned` true

### Requirement: Output layout mirrors the primary analysis
The step SHALL write `results/motco_rank_sensitivity/` with one directory per rank (`rank_<kk>`, the rank in two digits) laid out as the primary analysis, and `comparison/` (`rank_sensitivity.csv`, `rank_sensitivity.md`, `rank_sensitivity_manifest.json`). `axis-diagnostics` SHALL read a rank directory unchanged with the primary export, and the step SHALL never write `diagnostics/`.

#### Scenario: Diagnostics on the top rank
- **WHEN** `axis-diagnostics --analysis-dir results/motco_rank_sensitivity/rank_12 --out-dir results/motco_rank_sensitivity/diagnostics` runs
- **THEN** it passes its chain checks, records the analysis read as not the primary and as forced rank 12 of the sweep, and writes its six files

### Requirement: Sweep directories are complete or absent
The rank directories and `comparison/` SHALL be staged as `.tmp` and renamed together when every rank and the comparison are complete. An existing output SHALL stop the step unless `--force`; with `--force`, an existing `diagnostics/` SHALL be kept and recorded as stale in a finding.

#### Scenario: Interrupted run
- **WHEN** the run fails at rank 9
- **THEN** no rank directory or `comparison/` is created or replaced, only `.tmp` directories that the next run replaces

#### Scenario: Rerun without force
- **WHEN** `results/motco_rank_sensitivity/comparison/` exists and the step runs again without `--force`
- **THEN** it stops naming the directory and leaves every output directory unchanged

### Requirement: Participant-level outputs stay ignored
Each rank's `latent_scores.csv` and `analysis_metadata.csv` SHALL be matched by the existing patterns `results/**/latent_scores.csv` and `results/**/analysis_metadata.csv`, and `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` SHALL be unchanged. Every other output SHALL be aggregate, and no output, message or manifest SHALL hold a participant identifier.

#### Scenario: Ignore check
- **WHEN** `git check-ignore` runs on `rank_02/latent_scores.csv`, `rank_02/analysis_metadata.csv`, `rank_12/latent_scores.csv` and `rank_12/analysis_metadata.csv`
- **THEN** all four are ignored, and `rank_02/summary.md`, `rank_12/result.json` and `comparison/rank_sensitivity.md` are not

### Requirement: The primary is never modified
The step SHALL NOT write under `results/motco_input/`, `results/motco_analysis/`, `results/motco_diagnostics/`, `results/motco_latent_sensitivity/`, `results/motco_export_sensitivity/`, `results/motco_stage_sensitivity/` or `results/cohort/`, and SHALL NOT rerun the primary analysis.

#### Scenario: Primary untouched
- **WHEN** `rank-sensitivity` finishes
- **THEN** every file under those directories hashes as before

### Requirement: Comparison table generated from the records
`rank_sensitivity.csv` SHALL hold the primary row then one row per rank in ladder order, each with the rank and its mode, `cv_mean_auroc`, CV repeats completed, the eigengap and, per statistic, the observed value, p, rejection under `ANALYSIS_REJECTION_RULE` and the null mean, SD and q95, every value read from the records. No statistic SHALL be computed in the comparison.

#### Scenario: Values traced
- **WHEN** the comparison is written
- **THEN** every value in `rank_sensitivity.csv` equals the field it is read from in the primary record or a rank's record, and the table holds 7 rows

### Requirement: Comparison summary
`rank_sensitivity.md` SHALL print the table with a status per statistic and rank (`same`, or `differs (rank dependence)`), the primary's status named the result, each rank's floor, eigengap and `angle` null summary, the anchor check, the nesting of the ranks, the findings, and `READING_RULES` then `RANK_SENSITIVITY_READING_RULES` verbatim.

#### Scenario: Status differs at one rank
- **WHEN** `delta` is not rejected in the primary and rejected at rank 3 only
- **THEN** its status at rank 3 reads `differs (rank dependence)`, every other rank reads `same`, the primary's status is named the result, and a finding records it

### Requirement: Predeclared counts checked
The step SHALL compare each rank's record with `RANK_SENSITIVITY_EXPECTED_COUNTS`: every key of `ANALYSIS_EXPECTED_COUNTS` with component selection `forced`, the forced rank and 0 CV repeats, and the comparison's 7 rows. A deviation SHALL be a finding, never a stop; no statistic or status SHALL be predeclared.

#### Scenario: Counts match
- **WHEN** the step runs on the committed export
- **THEN** each rank manifest records 1501 participants, the primary's six cells, 298 features, the six design columns, floor 2, 9999 permutations, selection `forced` at its own rank, and an empty deviation list

### Requirement: Findings for conditions that change the reading
The step SHALL record a finding, never a stop, for every finding condition of `analyze` that applies to a forced run, a statistic whose rejection status at a rank differs from the primary's (named as rank dependence), a primary read with `n_jobs` not 1, and stale diagnostics. The conditions of the cross-validation SHALL NOT be raised on a forced run. No finding SHALL name a participant.

#### Scenario: No CV findings on a forced run
- **WHEN** a rank's record has no CV block and 0 CV repeats
- **THEN** no finding says that the cross-validation completed fewer repeats, ran with another floor or moved MOTCO's `forced_components` default

#### Scenario: Parallel run
- **WHEN** the step runs with `--n-jobs 4`
- **THEN** each rank's findings say that `n_jobs` 4 changes the permutation draws and the sweep is not reported, and the anchor gate compares only what the draws do not change (the statistics, the rank, the pooled `config_spectrum` and the three files), not the p-values, null summaries or permutation eigengap

### Requirement: Reproducible sweep
Two pinned runs on the same inputs, MOTCO release, seed and `n_jobs`, on one machine or on two, SHALL give byte-identical per-rank `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `summary.md`, a byte-identical `rank_sensitivity.csv` and `rank_sensitivity.md`, equal statistics, p-values and null summaries, and manifests that differ only in time, runtime and the machine fields of `numerics`.

#### Scenario: Rerun with force
- **WHEN** the step runs twice with `--force` and `n_jobs = 1`
- **THEN** `rank_sensitivity.csv`, `rank_sensitivity.md` and every rank's four CSVs and `summary.md` have equal sha256 across the two runs

### Requirement: Reading rules bind every reader of the sweep
`RANK_SENSITIVITY_READING_RULES` SHALL be a constant written before any run. It SHALL be printed verbatim after `READING_RULES` in each rank's `summary.md`, in `rank_sensitivity.md` and in the top rank's `diagnostics.md`, and every report that quotes the sweep SHALL carry it.

#### Scenario: Rules carried
- **WHEN** `rank_sensitivity.md` quotes a rank's statistic
- **THEN** it carries: the sweep never replaces the primary; one setting changed and the same draws; nested components and the anchor; each `angle` against its own null; MOTCO's forced-rank evidence and no check at this design; the sweep is not a test; the top rank's diagnostic; no reading against another sensitivity

### Requirement: The sweep never replaces the primary and feeds no choice
The primary analysis SHALL stay the primary result in every output of the step. No sweep value SHALL change a constant, `ANALYSIS_RANK_FLOOR` and the ladder included, select a rank or a setting, rerun the primary or define an arm, and no `export`, `analyze` or later sensitivity SHALL read the step's outputs to choose a setting.

#### Scenario: A forced rank rejects
- **WHEN** rank 2 rejects a statistic the primary does not
- **THEN** every output keeps the primary's status as the result, the rank's status reads `differs (rank dependence)`, and no constant or primary output changes
