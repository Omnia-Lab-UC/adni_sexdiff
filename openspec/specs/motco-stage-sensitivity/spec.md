# motco-stage-sensitivity Specification

## Purpose
Defines the `stage-sensitivity` step: the predeclared CN / LMCI / AD arm of the ADNI sex × stage trajectory comparison. It drops the two enrollment categories ADNI-GO/2 alone enrolled (SMC, EMCI), takes the primary export's rows of the participants it keeps, analyses them at the primary's settings and compares them with the primary, which stays primary.

## Requirements

### Requirement: MOTCO version and rank floor checked before any input is read
The step SHALL apply the gates of `analyze` before reading any input: the installed MOTCO SHALL be at least `ANALYSIS_MOTCO_MIN_VERSION` (0.10.0), and MOTCO's default rank floor SHALL equal `ANALYSIS_RANK_FLOOR` (2). A failure SHALL stop the step naming both values, without writing anything.

#### Scenario: Older MOTCO installed
- **WHEN** the installed MOTCO reports version 0.9.0
- **THEN** the step stops naming 0.9.0 and 0.10.0, and no input file is read

### Requirement: Inputs are the primary export, the primary analysis and the cohort
The step SHALL read only the primary export's five files, the primary analysis' `result.json` and `analysis_manifest.json`, and `cohort.csv` with `cohort_manifest.json`: no data-root file, no cleaned table, no feature table, nothing under a diagnostics directory. A missing input SHALL stop the step naming the file and the command that produces it, and nothing SHALL be written.

#### Scenario: Primary analysis absent
- **WHEN** `results/motco_analysis/` does not exist
- **THEN** the step stops naming the directory and the `analyze` command, and no output directory is created

#### Scenario: Inputs listed
- **WHEN** the step finishes
- **THEN** the comparison manifest lists exactly the nine input files with their sha256

### Requirement: Inputs are checked against their manifests
The export files SHALL hash to the values the export manifest records, `cohort.csv` to the value `cohort_manifest.json` records, and `cohort_manifest.json` to the value the export manifest records; the rows of `cohort.csv` with both platform flags SHALL be the exported participants in export order, with equal sex and stage. A mismatch SHALL stop the step before anything is written, naming the file, both values and the step to rerun.

#### Scenario: Cohort rerun after the export
- **WHEN** `cohort_manifest.json` hashes to a value other than the one the export manifest records
- **THEN** the step stops naming `cohort_manifest.json`, both hashes and the `export` command, and writes nothing

#### Scenario: Rows out of order
- **WHEN** the both-flag rows of `cohort.csv` hold the exported participants in another order
- **THEN** the step stops naming `cohort.csv` and the counts, never a participant, and writes nothing

### Requirement: The primary analysis is a chained reference
Before the arm runs, the step SHALL check that the primary manifest records, for each export file and the export manifest, the sha256 now on disk, that the primary records no latent adjustment, and that it was made under the installed MOTCO with `ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS`. On a difference it SHALL stop naming the file or setting, both values and the step to rerun, and write nothing.

#### Scenario: Export regenerated after the primary
- **WHEN** `nmr.csv` hashes to a value other than the one `results/motco_analysis/analysis_manifest.json` records
- **THEN** the step stops naming `nmr.csv`, both hashes and the `analyze` command, and writes nothing

### Requirement: One predeclared arm
The step SHALL run exactly one arm, `cn_lmci_ad` (`STAGE_SENSITIVITY_ARM`), once: the exported participants whose `dx_bl` is CN, LMCI or AD, staged by `STAGE_RULE`'s map (CN → CN, LMCI → MCI, AD → AD), SMC and EMCI dropped. The arm SHALL be a constant, never a flag, and its map SHALL equal `STAGE_RULE`'s for the categories it keeps.

#### Scenario: Arm participants
- **WHEN** the step runs on the committed export and cohort
- **THEN** the arm export holds 1130 participants (Female CN 183, MCI 187, AD 125; Male CN 181, MCI 296, AD 158) and its manifest records 96 SMC and 275 EMCI dropped

#### Scenario: Enrollment category outside the rule
- **WHEN** a `dx_bl` value of an exported participant is not one of CN, SMC, EMCI, LMCI, AD
- **THEN** the step stops naming `dx_bl` and a count, without naming a participant, and writes nothing

### Requirement: The arm export is a row subset of the primary export
The arm's `p180.csv`, `nmr.csv`, `metadata.csv` and `covariates.csv` SHALL be the primary export's header and the primary export's rows of the kept participants, in export order, each row byte-identical to the primary's. No floor SHALL be recomputed, no value transformed and no cleaned table read.

#### Scenario: Rows equal the primary's
- **WHEN** the arm export is written
- **THEN** every row of each of its four CSVs equals, byte for byte, the row of the same participant in the primary export's file, and its manifest records that for each file

#### Scenario: Feature membership unchanged
- **WHEN** the arm's manifest is read
- **THEN** its `block_columns` and covariate codings equal the primary export manifest's, and it names the primary's feature tables by their recorded hashes as the source of the floors

### Requirement: Arm export manifest records provenance and counts
The arm's `manifest.json` SHALL record the step, the arm by constant name, the primary export as reference (its manifest's sha256), the cohort chain, the output hashes with a participant-level flag, and counts: participants kept and dropped per `dx_bl`, sex × stage, runs within stage, covariate levels, missing covariate values, non-finite cells, and the run offset per block on the arm's rows beside the primary's recorded one.

#### Scenario: Run offset recorded
- **WHEN** the arm export is written on the committed inputs
- **THEN** its manifest records the p180 run offset on the arm's rows (107 metabolites above |d| 0.5, 77 above 1) beside the primary export manifest's (109, 80)

### Requirement: Arm analysis at the primary's settings
The arm SHALL be one call of MOTCO's trajectory-analysis entry point on the arm export, with every setting the primary's: `ANALYSIS_COVARIATES` with their coding, `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_RANK_FLOOR`, no latent adjustment and MOTCO's defaults. The step SHALL NOT rerun the primary or assemble a result from MOTCO's primitives.

#### Scenario: Reproduction by MOTCO's CLI
- **WHEN** the arm manifest's `cli_equivalent` is run with `motco analyze` into a scratch directory
- **THEN** its `statistics`, `p_values`, `null_summary` and selected rank equal the arm record's, and its `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` are byte-identical

### Requirement: Arm analysis records its provenance
The arm's `analysis_manifest.json` SHALL record step `stage-sensitivity`, the arm by constant name, the arm export's five files as its inputs, the primary analysis as its reference (directory, `result.json` and manifest sha256, rank), every setting as passed, a `cli_equivalent`, the versions, the git revision, the `numerics` block, the predeclared counts beside the observed ones, output hashes and findings. A committed arm SHALL record `numerics.pinned` true and `n_jobs` 1.

#### Scenario: Manifest after the real run
- **WHEN** the step finishes on a data machine
- **THEN** the arm manifest records step `stage-sensitivity`, arm `cn_lmci_ad`, latent adjustment none, the reference primary's two hashes, MOTCO 0.10.0 and `numerics.pinned` true

### Requirement: Output layout mirrors the primary pipeline
The step SHALL write `results/motco_stage_sensitivity/` with `motco_input/` laid out as the primary export without its feature tables, `analysis/` laid out as the primary analysis and `comparison/` (`stage_sensitivity.csv`, `stage_sensitivity.md`, `stage_sensitivity_manifest.json`). `axis-diagnostics` SHALL read `motco_input/` and `analysis/` unchanged, and the step SHALL never write `diagnostics/`.

#### Scenario: Diagnostics on the arm
- **WHEN** `axis-diagnostics --input-dir results/motco_stage_sensitivity/motco_input --analysis-dir results/motco_stage_sensitivity/analysis --out-dir results/motco_stage_sensitivity/diagnostics` runs
- **THEN** it passes its chain checks, records the analysis read as not the primary and as the arm `cn_lmci_ad`, and writes its six files

### Requirement: Arm directories are complete or absent
The three subdirectories the step writes SHALL be staged as `.tmp` and renamed together when complete. An existing output SHALL stop the step unless `--force`; with `--force`, an existing `diagnostics/` SHALL be kept and recorded as stale in a finding.

#### Scenario: Interrupted run
- **WHEN** the run fails during the analysis
- **THEN** no `motco_input/`, `analysis/` or `comparison/` is created or replaced, only `.tmp` directories that the next run replaces

#### Scenario: Rerun without force
- **WHEN** `results/motco_stage_sensitivity/analysis/` exists and the step runs again without `--force`
- **THEN** it stops naming the directory and leaves every output directory unchanged

### Requirement: Participant-level outputs are ignored before they exist
The arm export's CSVs SHALL be matched by `results/motco_stage_sensitivity/motco_input/*.csv` in `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` before the first run. Every other output SHALL be aggregate, and no output, message or manifest SHALL hold a participant identifier.

#### Scenario: Ignore check
- **WHEN** `git check-ignore` runs on the arm's `motco_input/p180.csv`, `motco_input/metadata.csv`, `analysis/latent_scores.csv` and `analysis/analysis_metadata.csv`
- **THEN** all four are ignored, and `motco_input/manifest.json`, `analysis/summary.md` and `comparison/stage_sensitivity.md` are not

### Requirement: The primary is never modified
The step SHALL NOT write under `results/motco_input/`, `results/motco_analysis/`, `results/motco_diagnostics/`, `results/motco_latent_sensitivity/`, `results/motco_export_sensitivity/` or `results/cohort/`, and SHALL NOT rerun the primary analysis.

#### Scenario: Primary untouched
- **WHEN** `stage-sensitivity` finishes
- **THEN** every file under those directories hashes as before

### Requirement: Comparison table generated from the records
`stage_sensitivity.csv` SHALL hold the primary row then the arm row, each with the participants, the selected rank and mode, `cv_mean_auroc`, CV repeats completed, the eigengap and, per statistic, the observed value, p, rejection under `ANALYSIS_REJECTION_RULE` and the null mean, SD and q95, every value read from the two analysis records. No statistic SHALL be computed in the comparison.

#### Scenario: Values traced
- **WHEN** the comparison is written
- **THEN** every value in `stage_sensitivity.csv` equals the field it is read from in one of the two records

### Requirement: Comparison summary
`stage_sensitivity.md` SHALL print the table with a status per statistic (`same`, or `differs (stage-definition dependence)`), the primary's status named the result, the cells, runs within stage and covariate levels of both analyses, the run offset of both exports, and `READING_RULES` then `STAGE_SENSITIVITY_READING_RULES` verbatim.

#### Scenario: Status differs
- **WHEN** `delta` is not rejected in the primary and rejected in the arm
- **THEN** its status reads `differs (stage-definition dependence)`, the primary's status is named the result, and a finding records it

### Requirement: Predeclared counts checked
The step SHALL compare the arm export and the arm record with `STAGE_SENSITIVITY_EXPECTED_COUNTS`: 1130 participants with 96 SMC and 275 EMCI dropped, the six cells, the runs within stage, the features, rows equal to the primary's, 0 missing covariate values and non-finite cells, the p180 run offset counts, and the `ANALYSIS_EXPECTED_COUNTS` keys with the arm's participants, cells and levels. A deviation SHALL be a finding, never a stop; the rank SHALL NOT be predeclared.

#### Scenario: Counts match
- **WHEN** the step runs on the committed export and cohort
- **THEN** the arm manifests record the counts above, the covariate levels `apoe4` 589 / 413 / 128, `phase` 684 / 446 and `statin` 603 / 527, and empty deviation lists

### Requirement: Findings for conditions that change the reading
The step SHALL record a finding, never a stop, for every finding condition of `analyze`, an arm rank that differs from the primary's, a statistic whose rejection status differs (named as stage-definition dependence), a primary read with `n_jobs` not 1, and stale diagnostics. No finding SHALL name a participant.

#### Scenario: Rank differs
- **WHEN** the arm's CV-selected rank is 5 and the primary's is 8
- **THEN** a finding names both ranks, reported beside `angle` and not ranked

#### Scenario: Parallel run
- **WHEN** the step runs with `--n-jobs 4`
- **THEN** the findings say that `n_jobs` 4 changes the permutation draws and the arm is not reported

### Requirement: Reproducible arm
Two pinned runs on the same inputs, MOTCO release, seed and `n_jobs`, on one machine or on two, SHALL give byte-identical arm export CSVs, `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `stage_sensitivity.csv`, equal statistics, p-values, null summaries and rank, and manifests that differ only in time, runtime and the machine fields of `numerics`.

#### Scenario: Rerun with force
- **WHEN** the step runs twice with `--force` and `n_jobs = 1`
- **THEN** `stage_sensitivity.csv`, the four arm export CSVs and the four arm analysis CSVs have equal sha256 across the two runs

### Requirement: Reading rules bind every reader of the arm
`STAGE_SENSITIVITY_READING_RULES` SHALL be a constant written before any run. It SHALL be printed verbatim after `READING_RULES` in the arm's `summary.md`, in `stage_sensitivity.md` and in the arm's `diagnostics.md`, and every report that quotes the arm SHALL carry it.

#### Scenario: Rules carried
- **WHEN** `stage_sensitivity.md` quotes an arm statistic
- **THEN** it carries: the arm never replaces the primary; a differing status is dependence on the stage definition and the sample; the rank beside `angle`; `phase` estimated within one diagnosis per stage while the run offset stays; the middle stage is LMCI and `angle` reads the endpoints; a non-rejection no more informative than the primary's; the cells, runs within stage and run offset beside the results; no reading against another sensitivity

### Requirement: The arm never replaces the primary and feeds no choice
The primary analysis SHALL stay the primary result in every output of the step. No arm value SHALL change a constant, `STAGE_RULE` or `COHORT_RULE`, select a participant or a setting, rerun the primary or define another arm, and no `cohort`, `export`, `analyze` or later sensitivity SHALL read the step's outputs to choose a setting.

#### Scenario: Arm rejects
- **WHEN** the arm rejects a statistic the primary does not
- **THEN** every output keeps the primary's status as the result, and no constant or primary output changes
