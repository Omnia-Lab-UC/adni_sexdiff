# latent-axis-diagnostic Specification

## Purpose
Measures, reproducibly and from the kept outputs only, what the MOTCO latent components and each block's leading principal axes correlate with (the analysis covariates, the p180 run, the design and the enrollment category), how much of the sex × stage geometry lies along each component and which block carries it, so that the primary analysis's measurement space is read from recorded tables under the reading rules and no analysis or preprocessing choice is ever derived from a diagnostic value.

## Requirements

### Requirement: Inputs are kept outputs only
The diagnostic SHALL read only the export directory (the five export files), the analysis directory (`result.json`, `latent_scores.csv`, `stage_means.csv`, `pls_loadings.csv`, `analysis_manifest.json`) and the cohort directory (`cohort.csv`, `cohort_manifest.json`): no data-root file, no cleaned table. A missing input SHALL stop it naming the file and the command that produces it, and it SHALL write nothing under the directories it reads.

#### Scenario: Analysis not yet run
- **WHEN** the analysis directory does not exist
- **THEN** the step stops naming the directory and the `analyze` command, and no diagnostics directory is created

#### Scenario: Inputs untouched
- **WHEN** the step finishes
- **THEN** the export, analysis and cohort directories hash identically before and after, and the manifest lists exactly the twelve input files above with their sha256

### Requirement: Export files are checked against the export manifest
The sha256 of each export CSV SHALL equal the hash the export manifest records for it, and the four participant tables SHALL carry the same `rid` column in the same order. A mismatch SHALL stop the step before anything is written, naming the file.

#### Scenario: Block altered after export
- **WHEN** `nmr.csv` hashes to a value other than the one `manifest.json` records
- **THEN** the step stops naming `nmr.csv` and writes nothing

### Requirement: Analysis is chained to the export
Every input hash the analysis manifest records SHALL equal the sha256 of that export file now on disk; `latent_scores.csv` SHALL list exactly the exported participants; and the number of latent components SHALL equal the record's selected rank in `latent_scores.csv`, `stage_means.csv` and `pls_loadings.csv`. A mismatch SHALL stop the step before anything is written, naming the file and both hashes or both counts.

#### Scenario: Export regenerated after the analysis
- **WHEN** `p180.csv` hashes to a value other than the one `analysis_manifest.json` records
- **THEN** the step stops naming `p180.csv`, the recorded hash and the current hash, and the `analyze` command

#### Scenario: Component column missing
- **WHEN** `stage_means.csv` holds seven `pls_` columns and the record's selected rank is 8
- **THEN** the step stops naming `stage_means.csv`, 7 and 8, and writes nothing

### Requirement: Cohort table is checked and chained to the export
`cohort.csv` SHALL hash to the value `cohort_manifest.json` records, `cohort_manifest.json` SHALL hash to the value the export manifest records for it, and the rows with both platform flags SHALL be the exported participants in export order. A mismatch SHALL stop the step before anything is written, naming the file and the step to rerun.

#### Scenario: Cohort rerun after the export
- **WHEN** `cohort_manifest.json` hashes to a value other than the one the export manifest records
- **THEN** the step stops naming `cohort_manifest.json` and the `export` command, and writes nothing

### Requirement: Predeclared variable set
The variables SHALL be the constant `DIAGNOSTIC_VARIABLES`: `age`, `education`, `apoe4` (0 / 1 / 2), `phase` (1 for `ADNI2GO`) and `statin` from `covariates.csv`; `stage` (CN 0, MCI 1, AD 2) and `male` (1 for Male) from `metadata.csv`; `dx_bl` (CN 0, SMC 1, EMCI 2, LMCI 3, AD 4) from `cohort.csv`. The set SHALL NOT be chosen or extended from a result, and the manifest SHALL list every variable with its source file and derivation.

#### Scenario: Variables recorded
- **WHEN** the diagnostic is written
- **THEN** the manifest lists the eight variables above, each with its source file and derivation, and no other

#### Scenario: Enrollment category outside the rule
- **WHEN** a `dx_bl` value of an exported participant is not one of CN, SMC, EMCI, LMCI, AD
- **THEN** the step stops naming `dx_bl` and a count, without naming a participant

### Requirement: Axis correlations with flags and no p-value
For every latent component the diagnostic SHALL write, per variable, the Spearman correlation, the partial Spearman correlation given the six design columns of the record (undefined for a variable in the conditioning set), the pairwise-complete n, the component's score SD, and one flag per correlation set when |ρ| is at least `DIAGNOSTIC_CORRELATION_THRESHOLD` (0.3). No p-value SHALL be attached to any correlation.

#### Scenario: Primary analysis at rank 8
- **WHEN** the primary analysis has eight components
- **THEN** `axis_correlations.csv` holds 64 rows, one per component × variable, each with both correlations, n, the score SD and both flags, and no p-value column

#### Scenario: Covariate given the covariates
- **WHEN** the variable is one of the five analysis covariates
- **THEN** its partial correlation is recorded as undefined and its partial flag is false

#### Scenario: Flag at the threshold
- **WHEN** a correlation is 0.3 in absolute value
- **THEN** its flag is true, and at 0.2999 it is false

### Requirement: Block principal components
For the first three principal components of each z-scored block the diagnostic SHALL write the same correlations, n and flags, with the component's share of the block's variance, and SHALL record the Spearman correlation of each block's first component with `phase` beside the correlation the export manifest recorded for it.

#### Scenario: Two blocks, three components
- **WHEN** the diagnostic is written on the export of two blocks
- **THEN** `block_pcs.csv` holds 48 rows (2 blocks × 3 components × 8 variables), and the manifest records per block the export's `abs_corr_pc1_phase` beside the diagnostic's value

### Requirement: Geometry shares along components
From `stage_means.csv` the diagnostic SHALL write, per component, the share of the squared length of each sex's net displacement (last stage minus first), of the per-stage sex-difference vectors and of the stage-centred sex-difference vectors that lies along that component. The shares of one quantity SHALL sum to 1 over the components.

#### Scenario: Shares sum to one
- **WHEN** `geometry_shares.csv` is written at rank 8
- **THEN** it holds 32 rows (4 quantities × 8 components) and each quantity's shares sum to 1 within 1e-9

### Requirement: Block composition of each component
Per latent component the diagnostic SHALL write the share of the component's squared `pls_loadings.csv` entries held by each block, summing to 1 over the blocks, with the component's score SD, the number of variables flagged on the raw and on the partial correlation, and the variable with the largest absolute raw correlation.

#### Scenario: Component summary
- **WHEN** `components.csv` is written at rank 8
- **THEN** it holds 8 rows, each with a p180 and an NMR share summing to 1 within 1e-9

### Requirement: Diagnostic output contract
The step SHALL write the diagnostics directory containing `axis_correlations.csv`, `block_pcs.csv`, `geometry_shares.csv`, `components.csv`, `diagnostics.md` and `diagnostics_manifest.json`, staged in a temporary directory and renamed when complete. An existing diagnostics directory SHALL stop the step unless forced.

#### Scenario: Six files
- **WHEN** the step finishes
- **THEN** the diagnostics directory holds exactly the six files and no temporary directory remains

#### Scenario: Rerun without force
- **WHEN** the diagnostics directory exists and the step runs again without `--force`
- **THEN** it stops naming the directory and leaves it unchanged

### Requirement: Outputs are aggregate only
Every output SHALL be per component, per block or per variable, SHALL hold no participant identifier, and SHALL be committed. The ignore rules, the sync filter and `PARTICIPANT_LEVEL_PATTERNS` SHALL be unchanged by this step.

#### Scenario: No identifier
- **WHEN** the six files are searched for a `rid` value or the token `RID`
- **THEN** only column-name mentions are found

#### Scenario: Ignore state
- **WHEN** the diagnostics directory exists
- **THEN** `git check-ignore -q` fails for each of the six files

### Requirement: Manifest records provenance, definitions and predeclared counts
`diagnostics_manifest.json` SHALL record the software versions, the git revision, every input with its sha256 and the chain checks, the analysis read (manifest hash, latent adjustment, `n_jobs`, selected rank, whether it is the primary), the variables with sources, the threshold, the conditioning columns, the definition of every statistic, the observed counts beside `DIAGNOSTICS_EXPECTED_COUNTS` with the deviations, output hashes and findings.

#### Scenario: Counts match on the primary
- **WHEN** the step runs on the committed export, cohort and primary analysis
- **THEN** the manifest records 1501 participants, 8 components, 8 variables, 6 conditioning columns, 64 / 48 / 32 / 8 rows in the four tables, and an empty deviation list

#### Scenario: A count deviates
- **WHEN** the export holds 1500 participants
- **THEN** the manifest's deviations name `participants`, expected 1501 and observed 1500, and the step still completes

### Requirement: Findings for conditions that change the reading
The step SHALL record a finding, never a stop, when the analysis read has `n_jobs` other than 1, when it is not the primary (a latent adjustment or a non-default analysis directory, so the primary's rank is not expected), when a variable is constant or has fewer than three complete rows, and, per component, the flagged variables as counts and names. A finding SHALL name counts, settings and variables, never a participant.

#### Scenario: Arm read
- **WHEN** `--analysis-dir` names a directory other than the default and its manifest records a latent adjustment
- **THEN** the manifest records the analysis as not the primary, skips the primary-rank expectation, and a finding says so

#### Scenario: Parallel analysis read
- **WHEN** the analysis manifest records `n_jobs` 4
- **THEN** a finding says that the analysis read is not a reported run

### Requirement: Reproducible diagnostics
Two runs on the same inputs SHALL give byte-identical CSVs and `diagnostics.md`, and manifests that differ only in their creation time.

#### Scenario: Rerun into a scratch directory
- **WHEN** the step runs twice on the same inputs into two directories
- **THEN** the four CSVs and `diagnostics.md` have equal sha256

### Requirement: Labels are read but feed no choice
The diagnostic reads sex and stage. Its outputs SHALL NOT be an input of `export`, `analyze` or any sensitivity arm, and the documentation SHALL state that variants and arms are predeclared in a change proposal, never derived from a diagnostic value.

#### Scenario: No downstream read
- **WHEN** any `export` or `analyze` command runs
- **THEN** it reads nothing under the diagnostics directory

### Requirement: Reading rules carried
`diagnostics.md` SHALL print `READING_RULES` verbatim and SHALL state that an axis correlated with a variable is a finding about the measurement space of the analysis read, not a reinterpretation of its statistics or p-values, that the flag is a reporting threshold and not an adoption rule, and that the primary analysis stays primary. On an arm it SHALL name the arm and its latent adjustment and print `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`.

#### Scenario: Run axis found
- **WHEN** `pls_0` is flagged against `phase`
- **THEN** `diagnostics.md` lists the row first, names it a measurement-space finding, and does not restate `delta`, `angle` or `shape` as different

#### Scenario: Arm read
- **WHEN** the analysis read is `results/motco_latent_sensitivity/analysis/`, whose manifest records latent adjustment `stage`
- **THEN** `diagnostics.md` names it the `stage`-conditioned sensitivity arm, calls each flagged row a finding about the arm's measurement space, prints `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Primary output unchanged
- **WHEN** the diagnostic runs pinned on the primary analysis after this change
- **THEN** its four CSVs and `diagnostics.md` have the sha256 the committed diagnostics manifest records
