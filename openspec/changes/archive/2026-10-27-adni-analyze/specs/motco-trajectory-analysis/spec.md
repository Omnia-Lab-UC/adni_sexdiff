# Spec Delta

## Purpose
Defines the `analyze` step: the covariate-adjusted comparison of the female and male sex × stage (CN / MCI / AD) trajectories on the exported ADNI metabolomics blocks through MOTCO's validated analysis entry point, at fixed, predeclared settings, with a record that traces every reported number to a pinned MOTCO release, hashed inputs and a fixed seed, and the binding reading rules every reader of the result carries.

## ADDED Requirements

### Requirement: MOTCO version and rank floor checked before any input is read
The system SHALL stop, naming the installed and the required values, when the installed MOTCO is older than the pinned minimum (0.10.0) or when MOTCO's default rank floor differs from `ANALYSIS_RANK_FLOOR` (2), before reading any input file and without writing anything.

#### Scenario: Older MOTCO installed
- **WHEN** the installed MOTCO reports version 0.9.0
- **THEN** the step stops naming 0.9.0 and 0.10.0, and no input file is read

#### Scenario: MOTCO default floor diverges
- **WHEN** the installed MOTCO's default `min_components` is 3
- **THEN** the step stops naming 3 and `ANALYSIS_RANK_FLOOR` 2, and writes nothing

### Requirement: Inputs are the export outputs only
The system SHALL read `p180.csv`, `nmr.csv`, `metadata.csv`, `covariates.csv` and `manifest.json` from the export directory and nothing else: no data-root file, no cohort file, no cleaned table.

#### Scenario: Export not yet run
- **WHEN** the export directory does not exist
- **THEN** the step stops naming the directory and the `export` command, and writes nothing

#### Scenario: Inputs listed
- **WHEN** `analyze` finishes
- **THEN** the manifest lists exactly the five export files as inputs, each with its sha256, and no other path

### Requirement: Inputs are checked against the export manifest
The system SHALL compare the sha256 of each export CSV with the hash the export manifest records for it, and SHALL check that the four participant-indexed tables carry identical `rid` columns in the same order. On a mismatch it SHALL stop before writing anything, naming the file.

#### Scenario: Block changed after export
- **WHEN** `nmr.csv` hashes to a value other than the one in `manifest.json`
- **THEN** the step stops naming `nmr.csv` and writes nothing

#### Scenario: Tables disagree
- **WHEN** `covariates.csv` lists a `rid` that `metadata.csv` does not
- **THEN** the step stops naming both files and writes nothing

### Requirement: Fixed covariate design
The analysis SHALL enter exactly the `ANALYSIS_COVARIATES` additively, in their order (`age`, `education`, `apoe4`, `phase`, `statin`), with `apoe4`, `phase` and `statin` declared categorical under the codings the export manifest carries and `age` and `education` numeric. The missing-covariate policy SHALL be `error`; nothing SHALL be imputed, and no interaction SHALL be entered.

#### Scenario: Design columns of the record
- **WHEN** `analyze` finishes on the exported tables
- **THEN** `result.json` records the covariate columns in the order above, kinds numeric, numeric, categorical, categorical, categorical, and the design columns `age`, `education`, `apoe4[1]`, `apoe4[2]`, `phase[ADNI2GO]`, `statin[1]`

#### Scenario: Missing covariate value
- **WHEN** a `covariates.csv` cell of `statin` is empty
- **THEN** the step stops naming `statin` and a count, and writes nothing

### Requirement: Fixed measurement settings
The analysis SHALL declare blocks `p180` then `nmr` in identity units, sample column `rid`, group `sex` in the order `Female`, `Male`, stage `stage` in the order `CN`, `MCI`, `AD`, cross-validated rank selection at MOTCO's defaults with the rank floor `ANALYSIS_RANK_FLOOR` passed explicitly, `ANALYSIS_PERMUTATIONS` (9999) permutations, `ANALYSIS_SEED` (20261027), no forced rank, no attribution and no latent adjustment. No other MOTCO default SHALL be overridden.

#### Scenario: Record carries the settings
- **WHEN** `analyze` finishes
- **THEN** `result.json` records `orientation_estimator` `net_displacement`, `component_selection` `cv`, `min_components` 2, a selected rank of at least 2, `permutations` 9999, the seed 20261027, the stage levels `CN`, `MCI`, `AD`, the group levels `Female`, `Male`, blocks `p180` and `nmr` with 133 and 165 features, and no `latent_adjustment` block

### Requirement: One call of MOTCO's analysis entry point
The analysis SHALL be one call of MOTCO's trajectory-analysis entry point (`analyze_trajectories`) on the declared dataset. It SHALL NOT assemble the result from `motco plsr`, `motco de` or the statistics primitives, and SHALL NOT run a second analysis at other settings in the same step.

#### Scenario: Reproduction by MOTCO's CLI
- **WHEN** the manifest's `cli_equivalent` is run with `motco analyze` on `analysis_metadata.csv` and the exported blocks into a scratch directory
- **THEN** its `statistics`, `p_values`, `null_summary` and selected rank equal the record's, and its `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` are byte-identical

### Requirement: Analysis output contract
The step SHALL write the analysis directory containing MOTCO's artifact (`result.json`, `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`), `analysis_metadata.csv` (`rid`, `sex`, `stage`, the five covariates, one row per exported participant in export order), `analysis_manifest.json` and `summary.md`, staged in a temporary directory and renamed when complete. An existing analysis directory SHALL stop the step unless forced.

#### Scenario: Seven files
- **WHEN** `analyze` finishes
- **THEN** the analysis directory holds exactly the seven files above and no temporary directory remains

#### Scenario: Rerun without force
- **WHEN** the analysis directory exists and `analyze` runs again without `--force`
- **THEN** it stops naming the directory and leaves it unchanged

### Requirement: Participant-level outputs stay ignored
`latent_scores.csv` and `analysis_metadata.csv` SHALL be participant-level: ignored by git, excluded by the sync script and matched by `PARTICIPANT_LEVEL_PATTERNS`, and flagged as such in the manifest's outputs. `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md` SHALL hold no participant identifier.

#### Scenario: Ignore state
- **WHEN** the analysis directory exists
- **THEN** `git check-ignore -q` succeeds for `latent_scores.csv` and `analysis_metadata.csv` and fails for the other five files

#### Scenario: No identifier in the aggregate files
- **WHEN** the five aggregate files are searched for a `rid` value or the token `RID`
- **THEN** only column-name mentions are found

### Requirement: Manifest records provenance and settings
`analysis_manifest.json` SHALL record the sha256 of every input, every setting as passed, a `cli_equivalent`, the software versions, the git revision, the predeclared counts beside the observed ones with the deviations, output hashes and findings.

#### Scenario: Manifest after the workstation run
- **WHEN** `analyze` finishes
- **THEN** the manifest is valid JSON holding five input hashes, `permutations` 9999, `seed` 20261027, alpha and the rejection rule, `min_components` 2, `latent_adjustment` null, `n_jobs`, the orientation estimator and CV settings read back from the record, the covariate names, kinds, levels and reference levels, the block order and transforms, the group and stage orders, a `cli_equivalent` naming `--min-components 2` and the three `--categorical-covariate` flags, and the versions of MOTCO (0.10.0), scikit-learn, numpy, pandas and Python

### Requirement: Predeclared counts checked
The step SHALL compare the record with `ANALYSIS_EXPECTED_COUNTS` (participants, sex × stage cells, features per block, design columns, covariate level counts, dropped participants, rank selection mode, floor, permutations) and SHALL record every deviation as a finding, printed and in the manifest, without stopping and without changing a setting.

#### Scenario: Counts match
- **WHEN** `analyze` runs on the exported tables of the committed export manifest
- **THEN** the manifest records 1501 participants, Female CN / MCI / AD 237 / 310 / 125, Male 223 / 448 / 158, six design columns, 0 dropped participants and an empty deviation list

#### Scenario: A count deviates
- **WHEN** the export holds 1500 participants
- **THEN** the manifest's deviations name `participants`, expected 1501 and observed 1500, and the analysis still completes at the predeclared settings

### Requirement: Findings for conditions that change the reading
The step SHALL record a finding when `n_jobs` is not 1, when the CV-selected rank equals the rank floor, when fewer CV repeats completed than requested, or when a statistic or p-value is not finite. A finding SHALL name counts and settings, never a participant.

#### Scenario: Parallel run
- **WHEN** `analyze` runs with `--n-jobs 4`
- **THEN** the manifest's findings say that `n_jobs` 4 changes the permutation draws and the run is not reported

#### Scenario: Rank at the floor
- **WHEN** the CV-selected rank is 2
- **THEN** the manifest's findings and the `angle` row of `summary.md` say that the floor is binding

### Requirement: Summary generated from the record
`summary.md` SHALL be generated from `result.json`, not typed by hand, and SHALL show per statistic the observed value, the p-value, the rejection at `ANALYSIS_ALPHA` under `ANALYSIS_REJECTION_RULE`, and the null mean, sd and 95 % quantile; the CV-selected rank, the floor, the pooled eigengap and `cv_mean_auroc`; the sex × stage cell sizes; the covariate block (design columns, reference row, missing policy, dropped participants); and the reading rules.

#### Scenario: Rank beside angle
- **WHEN** `summary.md` is written
- **THEN** the `angle` row names the selected rank, the floor and the eigengap from `result.json`

#### Scenario: Rejection wording
- **WHEN** a statistic's p-value is 0.0500
- **THEN** the summary marks it rejected, and at 0.0501 not rejected

### Requirement: Reproducible results
Two runs on the same inputs, MOTCO release, seed and `n_jobs` SHALL give equal statistics, p-values, selected rank and null summaries, and byte-identical `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv` and `analysis_metadata.csv`.

#### Scenario: Rerun with force
- **WHEN** `analyze` runs twice with `--force` and the same `n_jobs`
- **THEN** the two records agree in `statistics`, `p_values`, `null_summary` and `latent.selected_lv`, and the four CSVs have equal sha256

### Requirement: Reading rules bind every reader of the result
`READING_RULES` SHALL be a constant written before the first run and printed verbatim in `summary.md`, and every report, sensitivity and diagnostic that reads the analysis SHALL carry its statements.

#### Scenario: The rules carried
- **WHEN** `summary.md` or a report quotes a statistic of the analysis
- **THEN** it carries, beside it, that the primary stays primary and an arm's differing status is dependence; the rank, floor, eigengap and null summary beside `angle`; that `angle` and `shape` non-rejections are uninformative with no power statement at this design; that a `delta` rejection is a difference, not of size; the covariate block, the run offset, the block shares and the feature rule; that reported runs use `n_jobs = 1`; and that no result changes a constant

#### Scenario: Non-rejection wording
- **WHEN** `angle` is not rejected
- **THEN** the summary and any report state that the result is uninformative about orientation, not that the sexes' directions agree

#### Scenario: Delta rejection wording
- **WHEN** `delta` is rejected
- **THEN** the summary and any report state that the sexes' trajectories differ, without claiming the difference is in size

### Requirement: Latent adjustment is a predeclared sensitivity, not the primary
The primary analysis SHALL run with no latent adjustment. The `stage`-conditioned latent adjustment with the same covariates and settings is predeclared as a sensitivity arm for a following change; it SHALL NOT replace the primary, and `group_stage` conditioning SHALL NOT run.

#### Scenario: Primary record
- **WHEN** the primary analysis finishes
- **THEN** its record carries no `latent_adjustment` block and the manifest records `latent_adjustment` null with the arm named as the predeclared sensitivity
