# motco-latent-adjustment-sensitivity Specification

## Purpose
Defines the `latent-sensitivity` step: the predeclared `stage`-conditioned latent-adjustment arm of the ADNI sex × stage trajectory comparison. The arm reruns MOTCO's analysis entry point on the primary's export and settings with the latent basis fitted on covariate-residualized features, and records it so that it is read beside the primary analysis as a sensitivity, never as its replacement.

## Requirements

### Requirement: MOTCO version and rank floor checked before any input is read
The step SHALL apply the gates of `analyze` before reading any input: the installed MOTCO SHALL be at least `ANALYSIS_MOTCO_MIN_VERSION` (0.10.0), and MOTCO's default rank floor SHALL equal `ANALYSIS_RANK_FLOOR` (2). A failure SHALL stop the step naming both values, without writing anything.

#### Scenario: Older MOTCO installed
- **WHEN** the installed MOTCO reports version 0.9.0
- **THEN** the step stops naming 0.9.0 and 0.10.0, and no input file is read

### Requirement: Inputs are the export, the primary analysis and the cohort manifest
The step SHALL read only the five export files, the primary analysis' `result.json` and `analysis_manifest.json`, and `cohort_manifest.json`: no data-root file, no cleaned table, no `cohort.csv`, nothing under a diagnostics directory. A missing input SHALL stop the step naming the file and the command that produces it, and nothing SHALL be written.

#### Scenario: Primary analysis absent
- **WHEN** `results/motco_analysis/` does not exist
- **THEN** the step stops naming the directory and the `analyze` command, and no output directory is created

#### Scenario: Inputs listed
- **WHEN** the step finishes
- **THEN** the comparison manifest lists exactly the eight input files with their sha256, and the arm's analysis manifest lists the five export files as its inputs

### Requirement: The primary is a chained, read-only reference
Before the arm runs, the step SHALL check that: the primary manifest records, for each export file and the export manifest, the sha256 now on disk; the primary records no latent adjustment; and it was made under the installed MOTCO version with `ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS`. On a difference it SHALL stop, naming the file or setting, both values and the step to rerun, and write nothing.

#### Scenario: Export regenerated after the primary
- **WHEN** `nmr.csv` hashes to a value other than the one `results/motco_analysis/analysis_manifest.json` records
- **THEN** the step stops naming `nmr.csv`, both hashes and the `analyze` command, and writes nothing

#### Scenario: Primary made under another MOTCO
- **WHEN** the primary manifest records MOTCO 0.9.0 and 0.10.0 is installed
- **THEN** the step stops naming both versions and the `analyze` command, and writes nothing

#### Scenario: Primary untouched
- **WHEN** the step finishes
- **THEN** every file under `results/motco_analysis/` and `results/motco_input/` has the sha256 it had before the run

### Requirement: The cohort manifest is chained to the export
The sha256 of `cohort_manifest.json` SHALL equal the hash the export manifest records for it. A mismatch SHALL stop the step before anything is written, naming the file, both hashes and the `cohort` and `export` commands.

#### Scenario: Cohort rerun after the export
- **WHEN** `cohort_manifest.json` hashes to a value other than the one the export manifest records
- **THEN** the step stops naming `cohort_manifest.json` and both hashes, and writes nothing

### Requirement: One predeclared arm
The step SHALL run exactly one arm, `latent_stage` (`LATENT_SENSITIVITY_ARM`), once: MOTCO's covariate latent adjustment conditioned on `stage`, with the five `ANALYSIS_COVARIATES` in their order and coding and every other setting equal to the primary's. The arm SHALL be a constant, never a flag, and SHALL equal `ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`. `group_stage` conditioning SHALL NOT run.

#### Scenario: Arm record
- **WHEN** the step finishes
- **THEN** the arm's `result.json` carries a `latent_adjustment` block with conditioning `stage` and the covariates `age`, `education`, `apoe4`, `phase`, `statin`, and records `component_selection` `cv`, `min_components` 2, 9999 permutations, seed 20261027, the primary's orientation estimator and CV settings, and blocks `p180` and `nmr` with 133 and 165 features

#### Scenario: Same covariate design as the primary
- **WHEN** the arm and the primary records are compared
- **THEN** their `covariates` blocks carry equal columns, kinds, levels, reference levels, design columns and reference row, and their design cell sizes are equal

### Requirement: One call of MOTCO's analysis entry point
The arm SHALL be one call of MOTCO's trajectory-analysis entry point on the dataset the primary declared, with the latent adjustment the only added setting. The step SHALL NOT rerun the primary, SHALL NOT assemble a result from MOTCO's primitives, and SHALL NOT run any other setting.

#### Scenario: Reproduction by MOTCO's CLI
- **WHEN** the arm manifest's `cli_equivalent`, which names `--latent-adjustment stage`, is run with `motco analyze` into a scratch directory
- **THEN** its `statistics`, `p_values`, `null_summary`, `latent_adjustment` and selected rank equal the arm record's, and its `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` are byte-identical

### Requirement: A residualization failure stops the arm
When MOTCO reports a residualization design that is not of full rank, on the full sample or in a CV training set, the step SHALL stop with MOTCO's message and write nothing. No categorical level SHALL be merged and no setting changed to make the arm run.

#### Scenario: Level absent from a training set
- **WHEN** MOTCO raises that the residualization design of a CV training set is not of full rank
- **THEN** the step stops naming the repeat and fold MOTCO names, no output directory is created, and no constant changes

### Requirement: Arm analysis directory mirrors the primary's
The step SHALL write `analysis/` under its output root with the seven files `analyze` writes, laid out as the primary's: MOTCO's artifact, `analysis_metadata.csv`, `analysis_manifest.json` and `summary.md`. It SHALL write `comparison/` beside it, stage both as temporary directories and rename them only when both are complete. An existing output SHALL stop the step unless forced.

#### Scenario: Diagnostics read the arm
- **WHEN** `axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics` runs on the primary export
- **THEN** its chain checks pass and it records the analysis read as not the primary, with latent adjustment `stage`

#### Scenario: Rerun without force
- **WHEN** `results/motco_latent_sensitivity/analysis/` exists and the step runs again without `--force`
- **THEN** it stops naming the directory and leaves both output directories unchanged

### Requirement: Arm manifest records provenance and the reference
The arm's `analysis_manifest.json` SHALL record the five export hashes as its inputs, the primary as its reference (directory and the sha256 of its `result.json` and manifest), the arm by constant name with its conditioning, every setting as passed, a `cli_equivalent`, the versions, the git revision, the `numerics` block, the predeclared counts beside the observed ones, output hashes with a participant-level flag and findings. A committed arm SHALL record `numerics.pinned` true.

#### Scenario: Manifest after the real run
- **WHEN** the step finishes on a data machine
- **THEN** the arm manifest records `latent_adjustment` `stage`, the reference primary's two hashes, `n_jobs`, MOTCO 0.10.0, `numerics` with `pinned` true and the machine's hostname, and a `cli_equivalent` naming `--latent-adjustment stage`, `--min-components 2` and the three `--categorical-covariate` flags

### Requirement: Comparison generated from the two records
The step SHALL write `latent_sensitivity.csv` with the primary row then the arm row (latent adjustment, rank, selection mode, CV AUROC and repeats, eigengap, and per statistic observed, p, rejection under `ANALYSIS_REJECTION_RULE`, null mean, SD and q95; for the arm its residual df, smallest CV training df and `feature_r2` summary), its Markdown rendering and a manifest. Every value SHALL be read from the records.

#### Scenario: Values traceable
- **WHEN** `latent_sensitivity.csv` is written
- **THEN** every statistic, p-value, null summary value, rank and latent-adjustment value in it equals the value in the primary or arm `result.json`

#### Scenario: Status per statistic
- **WHEN** the arm rejects `angle` and the primary does not
- **THEN** `latent_sensitivity.md` marks `angle` as differing, names it basis dependence, and keeps the primary's non-rejection as the result

### Requirement: Covariate roles stated beside the cohort descriptives
`latent_sensitivity.md` SHALL state each covariate's role from `LATENT_SENSITIVITY_COVARIATE_ROLES` (`age`, `education`, `apoe4` precede disease; `phase` is the assay run and protocol; `statin` may follow diagnosis, the mediator candidate) beside its per sex × stage descriptives copied from the cohort manifest. No statistic or threshold SHALL be computed for it, and nothing SHALL change because of it.

#### Scenario: Statin named
- **WHEN** `latent_sensitivity.md` is written
- **THEN** it names `statin` as the mediator candidate, shows its 0 / 1 counts per sex × stage cell as the cohort manifest records them, and states that the arm's basis may have removed stage signal that runs through treatment

#### Scenario: Descriptives cover the analysed cells
- **WHEN** the cohort manifest's descriptive cell counts differ from the arm record's cell sizes
- **THEN** a finding names the cell and both counts, and the arm still completes

### Requirement: Predeclared counts checked
The step SHALL compare the arm record with `LATENT_SENSITIVITY_EXPECTED_COUNTS`: the `ANALYSIS_EXPECTED_COUNTS` keys and values, and the latent-adjustment block (conditioning `stage`, the five covariates, design columns `stage[1]`, `stage[2]` then the six design columns, 1501 samples, residual df 1492, feature scale `pooled_standardized`). Every deviation SHALL be a finding, never a stop. The rank SHALL NOT be predeclared.

#### Scenario: Counts match
- **WHEN** the step runs on the export of the committed export manifest
- **THEN** the arm manifest records 1501 participants, the six cells, eight residualization design columns, residual df 1492 and an empty deviation list

### Requirement: Findings for conditions that change the reading
The step SHALL record a finding, never a stop, for: every finding condition of `analyze` (`n_jobs` not 1, a rank at the floor, fewer CV repeats than requested, a non-finite statistic or p-value, a moved MOTCO default); an arm rank that differs from the primary's; a statistic whose rejection status differs from the primary's, named as basis dependence; and a primary read with `n_jobs` not 1. No finding SHALL name a participant.

#### Scenario: Rank differs
- **WHEN** the arm's CV-selected rank is 5 and the primary's is 8
- **THEN** a finding names both ranks, and the `angle` row of the comparison carries both

#### Scenario: Parallel run
- **WHEN** the step runs with `--n-jobs 4`
- **THEN** the findings say that `n_jobs` 4 changes the permutation draws and the arm is not reported

### Requirement: Participant-level outputs stay ignored
`analysis/latent_scores.csv` and `analysis/analysis_metadata.csv` SHALL be ignored by git, excluded by the sync script, matched by `PARTICIPANT_LEVEL_PATTERNS` and flagged participant-level in the manifest. Every other output file SHALL be aggregate and SHALL hold no participant identifier.

#### Scenario: Ignore state
- **WHEN** the output directories exist
- **THEN** `git check-ignore -q` succeeds for the two participant-level files and fails for the other files under `analysis/` and `comparison/`

#### Scenario: No identifier in the aggregate files
- **WHEN** the aggregate files are searched for a `rid` value or the token `RID`
- **THEN** only column-name mentions are found

### Requirement: Reproducible arm
Two pinned runs on the same inputs, MOTCO release, seed and `n_jobs`, on the same machine or on different ones, SHALL give equal arm statistics, p-values, null summaries, selected rank and latent-adjustment block; byte-identical `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `latent_sensitivity.csv`; and manifests that differ only in time, runtime and, across machines, the machine fields of `numerics` (host, CPU model, CPUs available).

#### Scenario: Rerun with force
- **WHEN** the step runs twice with `--force` and `n_jobs = 1`
- **THEN** both `latent_sensitivity.csv` files and the four arm CSVs have equal sha256

### Requirement: The primary path is unchanged by the shared analysis code
The analysis code the arm shares with `analyze` SHALL leave the primary's outputs unchanged. Pinned, on a data machine's export, `analyze` after this change SHALL write `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `summary.md` with the sha256 the committed primary manifest records, and a `result.json` equal to the committed one apart from its runtime.

#### Scenario: Primary rerun after the change
- **WHEN** a pinned `analyze --out-dir <scratch>` runs on a data machine's export after this change
- **THEN** its four CSVs and `summary.md` have the sha256 the committed primary manifest records, and its `result.json` equals the committed one apart from the runtime

#### Scenario: Any data machine
- **WHEN** the same pinned rerun runs on another data machine, whatever its CPU features or CPU count
- **THEN** it writes the same sha256, so the gate does not depend on which machine made the committed primary

### Requirement: Reading rules bind every reader of the arm
`LATENT_SENSITIVITY_READING_RULES` SHALL be a constant written before any run. It SHALL be printed verbatim after `READING_RULES` in the arm's `summary.md`, in `latent_sensitivity.md` and in the arm's `diagnostics.md`, and every report that quotes the arm SHALL carry it.

#### Scenario: Rules carried
- **WHEN** `latent_sensitivity.md` quotes an arm statistic
- **THEN** it carries: the arm never replaces the primary (`candidate_fails`); a differing status is basis dependence; the rank beside `angle`; an arm-only `angle` rejection is read against the translation control; an arm's non-rejection is weaker; the `latent_adjustment` block and `feature_r2`; the mediator limitation with `statin`; no operating characteristic at this design; an arm axis is a measurement-space finding

#### Scenario: Arm-only delta non-rejection
- **WHEN** the primary and the arm both leave `delta` unrejected
- **THEN** the comparison states both as non-rejections and that the arm's is weaker than the primary's, not that the sexes' trajectories agree

### Requirement: The arm never replaces the primary and feeds no choice
The primary analysis SHALL stay the primary result in every output of the step. No arm value SHALL change a constant, select a covariate, rerun the primary or define a variant, and no `export`, `analyze` or later arm SHALL read the step's outputs to choose a setting.

#### Scenario: Arm rejects
- **WHEN** the arm rejects a statistic the primary does not
- **THEN** every output keeps the primary's status as the result, and no constant or primary output changes
