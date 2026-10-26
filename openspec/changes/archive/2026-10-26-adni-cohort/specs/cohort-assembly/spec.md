# Spec Delta

## Purpose

Defines the `cohort` step: from the outputs of `clean` and the ADNI clinical tables, one baseline row per participant with sex, stage and the decided covariates, the platform sets and their intersection, the aggregate sex × stage counts, and a manifest whose counts are checked against the predeclared ones.

## ADDED Requirements

### Requirement: Inputs are the clean outputs and named data-root files only
The system SHALL read the cleaned tables and `p180_runs.csv` of `clean`, their `clean_manifest.json`, and from the data root only the ADNIMERGE freeze, the medication table and the visit columns of the ADNI-GO/2 p180 and NMR concentration files. It SHALL read no other file.

#### Scenario: Inputs listed
- **WHEN** `cohort` runs
- **THEN** the manifest lists as data-root inputs exactly `ADNI_adnimerge_20170629_QT-freeze.csv`, `ADMCPATIENTDRUGCLASSES_20170512.csv`, `ADMCDUKEP180UPLCADNI2GO.csv`, `ADMCDUKEP180FIAADNI2GO.csv` and `ADNINIGHTINGALE2.csv`, each with its symlink target, size and sha256, and as clean inputs the two manifests and the three files they hash

### Requirement: Clean outputs are checked against their manifests
The system SHALL compare the sha256 of every clean output it reads with the hash its `clean_manifest.json` records and SHALL stop before writing anything when one differs or a manifest is absent, naming the file.

#### Scenario: Cleaned table changed after clean
- **WHEN** `results/cleaned/nmr/NMR.csv` no longer hashes to the value in `results/cleaned/nmr/clean_manifest.json`
- **THEN** the step stops naming `nmr/NMR.csv` and no cohort directory is created

### Requirement: Raw inputs go through the raw-input integrity rules
The system SHALL treat every data-root input as the raw-input-integrity capability requires: all names present before work starts, content hashed through symlinks, known repairs recognised, an unrepaired known-defective file refused, an unknown hash recorded as a finding.

#### Scenario: Clinical table missing
- **WHEN** `ADNI_adnimerge_20170629_QT-freeze.csv` is absent from the data root
- **THEN** the step stops naming it before any output directory is created

#### Scenario: Clinical table re-downloaded
- **WHEN** the ADNIMERGE file hashes to a value other than `e3eae0464106f0a3df4eb23946e57f1f7fd5f8456eb60af6540654a36a16f7a2`
- **THEN** the step completes and `findings` names the file and its observed hash

### Requirement: One baseline row per participant
The system SHALL take each participant's clinical values from the ADNIMERGE row with `VISCODE` equal to `bl`. A cleaned participant without such a row SHALL be excluded and counted; more than one such row for a participant SHALL stop the step with a count.

#### Scenario: Baseline row
- **WHEN** a participant has 9 ADNIMERGE rows of which one has `VISCODE` `bl`
- **THEN** sex, `DX.bl`, protocol and the ADNIMERGE covariates come from that row

### Requirement: Each platform's sample is a baseline sample
A participant SHALL enter a platform set only if every raw record of the participant on that platform has visit code `bl` (`VISCODE` in the ADNI-GO/2 p180 files, `VISCODE2` in the NMR file). Participants of the ADNI-1 p180 run, whose files carry no visit column, SHALL count as baseline.

#### Scenario: Screening-only NMR sample
- **WHEN** a cleaned NMR participant's only NMR record has `VISCODE2` `sc`
- **THEN** the participant is not in the NMR set, the cascade counts it under the sample rule, and nothing names the participant

#### Scenario: ADNI-1 p180 participant
- **WHEN** a participant's p180 run in `p180_runs.csv` is `ADNI1`
- **THEN** the sample rule holds for p180 without a visit code

### Requirement: Platform sets and the analysis intersection
The system SHALL form one set per platform (cleaned participants passing the sample rule with an ADNIMERGE `bl` row) and the analysis cohort as their intersection. No exclusion SHALL depend on sex, stage or a covariate value.

#### Scenario: Intersection
- **WHEN** a participant is in the p180 set but not in the NMR set
- **THEN** `cohort.csv` holds the participant with `p180` true and `nmr` false, and the participant is not counted in the intersection

### Requirement: Stage from DX.bl by the decided mapping
The system SHALL assign `stage` from `DX.bl` by `STAGE_RULE`: `CN` and `SMC` to `CN`, `EMCI` and `LMCI` to `MCI`, `AD` to `AD`, and SHALL keep `DX.bl` beside it. A `DX.bl` outside the mapping SHALL stop the step naming the value and its count.

#### Scenario: Subtypes merged
- **WHEN** a participant's `DX.bl` is `EMCI`
- **THEN** `stage` is `MCI` and `dx_bl` is `EMCI`

#### Scenario: Unmapped diagnosis
- **WHEN** a participant in a platform set has a `DX.bl` value not in the mapping
- **THEN** the step stops naming the value and the number of participants holding it, and writes nothing

### Requirement: Sex from PTGENDER
The system SHALL take `sex` from `PTGENDER` with the values `Female` and `Male` as they appear. Any other or missing value for a participant in a platform set SHALL stop the step with a count.

#### Scenario: Sex values
- **WHEN** the cohort is built
- **THEN** every row of `cohort.csv` has `sex` `Female` or `Male`

### Requirement: The decided covariates with their sources and codings
The system SHALL write the covariates of `ANALYSIS_COVARIATES` in their declared order: `age` (`AGE`), `education` (`PTEDUCAT`), `apoe4` (`APOE4`, levels 0/1/2), `phase` (`ORIGPROT`: `ADNI1` → `ADNI1`, `ADNIGO`/`ADNI2` → `ADNI2GO`) and `statin` (medication table, `sc` row, column `HMG CoA reductase inhibitors`: filled 1, empty 0).

#### Scenario: Phase coding
- **WHEN** a participant's `ORIGPROT` is `ADNIGO`
- **THEN** `phase` is `ADNI2GO` and `protocol` is `ADNIGO`

#### Scenario: Statin coding
- **WHEN** a participant's `sc` medication row has an empty `HMG CoA reductase inhibitors` cell
- **THEN** `statin` is `0`

### Requirement: Missing covariates stop the step
A missing covariate value for a participant in a platform set, including a participant without an `sc` medication row, SHALL stop the step naming the covariate and the number of participants missing it. Nothing SHALL be imputed and no participant SHALL be dropped for it.

#### Scenario: Missing APOE4
- **WHEN** one participant of the NMR set has no `APOE4` on the `bl` row
- **THEN** the step stops with a message naming `apoe4` and the count 1, no RID, and no cohort directory is created

### Requirement: Phase is checked against the p180 run
For every participant of the p180 set, the system SHALL compare `phase` with the run in `p180_runs.csv` and record the cross-tabulation in the manifest; each disagreement SHALL be a finding with its count.

#### Scenario: Phase equals run
- **WHEN** the cohort is built from the inventoried files
- **THEN** the manifest's phase-against-run table has 0 off-diagonal participants and `findings` holds no phase line

### Requirement: Participant table
The system SHALL write `cohort.csv` with one row per participant of either platform set and the columns `rid`, `sex`, `stage`, `dx_bl`, `protocol`, the covariates in declared order, `visit` and the flags `p180` and `nmr`. The file SHALL be participant-level and never committed or synced.

#### Scenario: Rows and flags
- **WHEN** the cohort is built from the inventoried files
- **THEN** `cohort.csv` has 1594 rows, of which 1501 have both flags true

#### Scenario: Ignored
- **WHEN** `git check-ignore results/cohort/cohort.csv` runs
- **THEN** the file is ignored

### Requirement: Aggregate stage counts
The system SHALL write `stage_counts.csv` with the columns `set`, `sex`, `stage`, `dx_bl`, `phase`, `n`: sex × stage for the p180 set, the NMR set and the intersection (`dx_bl` and `phase` `all`), and for the intersection every observed sex × stage × `dx_bl` × phase cell. It SHALL hold no participant identifier.

#### Scenario: Intersection cell
- **WHEN** the cohort is built from the inventoried files
- **THEN** the row `intersection, Female, MCI, all, all` has `n` 310 and the row `intersection, Male, MCI, EMCI, ADNI2GO` has `n` 152

#### Scenario: Committed
- **WHEN** `git check-ignore results/cohort/stage_counts.csv` runs
- **THEN** the file is not ignored

### Requirement: Manifest content
The system SHALL write `cohort_manifest.json` with the keys `step`, `versions`, `git_revision`, `inputs`, `settings`, `outputs`, `findings` and the cohort's counts: the rules as applied, the exclusion cascade, the stage-source agreement of `DX` with the mapped stage, the phase-against-run table, covariate summaries by sex × stage, and every output's sha256. It SHALL hold no `RID`.

#### Scenario: Stage-source agreement
- **WHEN** the cohort is built from the inventoried files
- **THEN** the manifest records that `DX` on the `bl` row, read as the diagnosis at the visit, agrees with the stage for 1498 intersection participants, differs for 2 and is missing for 1

### Requirement: Counts are checked against the predeclared ones
The system SHALL compare its counts with `COHORT_EXPECTED_COUNTS` (cascade, sex × stage per set, composition cells, stage-source agreement, phase disagreements, statin users, missing covariates) and record expected, observed and every deviation. A deviation SHALL be a finding and a printed line; it SHALL NOT stop the step or change a rule.

#### Scenario: Inventoried files
- **WHEN** the cohort is built from the files whose hashes the spike recorded
- **THEN** the manifest's deviations list is empty

#### Scenario: Different download
- **WHEN** the NMR set has 1502 participants instead of 1503
- **THEN** the step completes, `findings` and the output name the expected and observed count, and the rules applied are unchanged

### Requirement: Output directory is complete or absent
The system SHALL build the outputs in `results/cohort.tmp/` and rename it to `results/cohort/` only when every file is written. An existing `results/cohort/` SHALL be replaced only under `--force`.

#### Scenario: Existing output without force
- **WHEN** `results/cohort/` exists and `cohort` runs without `--force`
- **THEN** the step stops naming the directory and leaves it unchanged

### Requirement: No participant identifier in any message
Progress output, error messages, findings and the manifest SHALL name files, columns, values and counts, never a participant identifier.

#### Scenario: Stop on missing covariate
- **WHEN** the step stops on a missing covariate
- **THEN** the message names the covariate and a count, and holds no RID
