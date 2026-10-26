# metabolomics-cleaning Specification

## Purpose
Defines the `clean` step: metabo_adni's cleaning of the raw ADNI metabolomics files per platform with the decided options, run in a working copy, yielding one cleaned participant × metabolite table per platform on the scale the platform delivers, the p180 run provenance, a captured log and an aggregate manifest whose counts are checked against the predeclared ones.

## Requirements

### Requirement: Inputs are the platform's raw files from the data root only
The system SHALL read, for `p180`, the four p180 concentration files, the four p180 LOD workbooks and the fasting file, and for `nmr`, the NMR concentration file and the fasting file, all from the data root under the names metabo_adni expects. It SHALL read no other file: not the medication table, not a clinical table, not a previous output.

#### Scenario: p180 inputs
- **WHEN** `clean --platform p180` runs
- **THEN** the manifest lists exactly `ADMCDUKEP180UPLC_01_15_16.csv`, `ADMCDUKEP180FIA_01_15_16.csv`, `ADMCDUKEP180UPLCADNI2GO.csv`, `ADMCDUKEP180FIAADNI2GO.csv`, `4097_UPLC_p180_Data.xlsx`, `4097_FIA_p180_Data.xlsx`, `4610 UPLC p180 Data.xlsx`, `4610 FIA p180 Data.xlsx` and `BIOMARK.csv` as inputs

#### Scenario: NMR inputs
- **WHEN** `clean --platform nmr` runs
- **THEN** the manifest lists exactly `ADNINIGHTINGALE2.csv` and `BIOMARK.csv` as inputs

### Requirement: The pinned metabo_adni release is checked before any file is read
The system SHALL compare the installed metabo_adni version with the pinned release (`0.5.8`) before reading any input and SHALL stop with an error naming both versions when they differ.

#### Scenario: Version differs from the pin
- **WHEN** the installed metabo_adni is not `0.5.8`
- **THEN** the step stops naming the installed and the pinned version, and no file under the data root has been read and no output directory created

### Requirement: metabo_adni's pipeline in its own order, in a working copy
The system SHALL run metabo_adni's cleaning functions in the order of metabo_adni's own command line, on a working copy of the inputs, with the fasting file and the LOD workbooks read from that copy. The data root SHALL never be written.

#### Scenario: Working copy, archive untouched
- **WHEN** the step runs on a data root whose files are symlinks into the LONI archive
- **THEN** metabo_adni reads and writes only inside `results/cleaned/<platform>.tmp/`, and every file under the data root has the same bytes after the run as before

#### Scenario: Command line recorded
- **WHEN** the step completes for `p180`
- **THEN** the manifest records a `cli_equivalent` of the form `clean_files -D <work> -P p180 -F BIOMARK.csv -L <work> --mmc 0.2 --mpc 0.2 --cv 0.2 --icc 0.65 --merge`

### Requirement: The decided cleaning options
The system SHALL apply `CLEAN_OPTIONS` for the platform: metabo_adni's QC with its default cutoffs, its merge, and none of its transforms. The options SHALL be recorded in the manifest exactly as applied and SHALL NOT be changed by a flag, a result or a count.

#### Scenario: p180 options
- **WHEN** `p180` is cleaned
- **THEN** the missing-metabolite cutoff is 0.2, the missing-participant cutoff 0.2, the CV cutoff 0.2, the ICC cutoff 0.65, the merge is on, and log2, z-score, winsorizing, multivariate-outlier removal and medication residualization are off

#### Scenario: NMR options
- **WHEN** `nmr` is cleaned
- **THEN** the missing-metabolite cutoff is 0.2, the missing-participant cutoff 0.2, the merge is on, the five transforms are off, and no CV or ICC cutoff is applied (metabo_adni applies them to p180 only)

#### Scenario: No transform is applied
- **WHEN** the cleaned table is written
- **THEN** its values are the concentrations metabo_adni holds after imputation and merging, on the scale the platform delivers, with no log, scaling, capping or residualization applied

### Requirement: One cleaned table per platform under metabo_adni's name
The system SHALL write the merged table under `results/cleaned/<platform>/` with the name and layout metabo_adni's command line gives it: `P180.csv` (participants × the metabolites common to both runs, keyed by `RID`) and `NMR.csv` (participants × metabolites, keyed by `RID`). The index SHALL have no duplicated `RID`; a duplicate is an error.

#### Scenario: Predeclared shape
- **WHEN** the step completes on the inventoried files
- **THEN** `P180.csv` has 1592 participants and 133 metabolites and `NMR.csv` has 1504 participants and 245 metabolites, or the manifest records the deviation as a finding

### Requirement: p180 run provenance table
The system SHALL write `results/cleaned/p180/p180_runs.csv` with columns `RID` and `run` (`ADNI1` for the ADNI-1 kit files, `ADNI2GO` for the ADNI-GO/2 kit files), one row per participant of `P180.csv`, derived from the raw files' participant rows. A participant present in both runs' raw files SHALL be recorded as a finding with its count, never with its identifier.

#### Scenario: Runs partition the cleaned table
- **WHEN** `P180.csv` holds 1592 participants
- **THEN** `p180_runs.csv` holds the same 1592 `RID`s, each with one run, and the manifest reports 746 `ADNI1` and 846 `ADNI2GO`, or a finding

### Requirement: metabo_adni's output is captured, never shown
The system SHALL redirect everything metabo_adni prints, which lists participant identifiers, to `results/cleaned/<platform>/logs/metabo_adni.log` and SHALL print to the terminal only `[clean]`-prefixed messages naming files, steps and counts. No participant identifier SHALL appear in the terminal output or in the manifest.

#### Scenario: Participant removal
- **WHEN** metabo_adni removes non-fasting participants and prints their table
- **THEN** the terminal shows only the count removed per table and the identifiers are in the log file

### Requirement: Manifest content
The system SHALL write `results/cleaned/<platform>/clean_manifest.json`, an aggregate record of the run: what was read, with which software and options, what each step left, what was written, and what deviated. It SHALL contain no participant identifier.

#### Scenario: Sections present
- **WHEN** the manifest is written
- **THEN** it is valid JSON holding: metabo_adni and library versions; git revision; data root; the options and `cli_equivalent`; each input's name, symlink target, size, sha256 and known repair; the raw inventory (records, QC-pool records, participant records, unique participants, participants with replicates, plates, visit-code counts); participants × metabolites after every step; imputed points per table; the cleaned table's value summary (zeros, share below 1, smallest positive, median); p180 participants per run; each output's sha256; expected and observed counts with deviations; findings; the upstream behaviours with counts

#### Scenario: Manifest is aggregate
- **WHEN** the manifest is searched for any `RID` value of the cleaned table
- **THEN** none is found; identifiers occur only in the cleaned tables, the provenance table and the log

### Requirement: Predeclared counts are checked and deviations are findings
The system SHALL compare the observed counts (cells after each step, imputed points, final shape, p180 participants per run, zeros in the cleaned table) with `CLEAN_EXPECTED_COUNTS` and SHALL record every difference in `findings`, naming the quantity, the expected and the observed value, and print it. A deviation SHALL NOT stop the step and SHALL NOT change any option.

#### Scenario: Counts reproduce
- **WHEN** the inventoried files are cleaned
- **THEN** `findings` holds no count deviation and the manifest marks the counts as reproduced

#### Scenario: Fresh LONI download changes a count
- **WHEN** a re-downloaded NMR file yields 1505 participants instead of 1504
- **THEN** the step completes, the manifest lists `nmr final participants: expected 1504, observed 1505` under `findings`, and the terminal prints the same line

### Requirement: Known upstream behaviours recorded with their counts
The system SHALL record in the manifest, for the pinned release, the p180 metabolites whose missing values span more than one plate and their imputed points, that `ADNI2GO-UPLC` missing values receive the LOD rather than half of it, that the medication reader keeps `bl` rows (not used here), and the NMR records at visits other than `bl`, each as a count. None of them SHALL be patched or worked around.

#### Scenario: Multi-plate imputation count
- **WHEN** `p180` is cleaned from the inventoried files
- **THEN** the manifest reports 34 metabolites and 1608 points under the multi-plate behaviour, or the observed counts

### Requirement: Output directory is complete or absent
The system SHALL write each platform under `results/cleaned/<platform>.tmp/`, remove the working copy, and rename to `results/cleaned/<platform>/` only when every output and the manifest exist. An existing platform directory SHALL stop the step unless `--force` is given, in which case it is replaced after the new one is complete. A leftover `.tmp` directory SHALL be removed at start. `--platform all` SHALL run the platforms one after the other, each with its own directory.

#### Scenario: Failure leaves no partial platform directory
- **WHEN** metabo_adni raises midway through `nmr`
- **THEN** `results/cleaned/nmr/` does not exist and `results/cleaned/nmr.tmp/` holds whatever was written, for inspection

#### Scenario: Existing output without force
- **WHEN** `results/cleaned/p180/` exists and `--force` is not given
- **THEN** the step stops naming the directory and leaves it unchanged

### Requirement: Reruns reproduce the outputs
The system SHALL produce byte-identical cleaned tables and provenance table when rerun on the same machine with the same inputs and options, and the manifest's output hashes SHALL make this checkable.

#### Scenario: Rerun with force
- **WHEN** `clean --platform all --force` runs twice on the same data root
- **THEN** the sha256 of `P180.csv`, `p180_runs.csv` and `NMR.csv` are equal between the two manifests

### Requirement: Only the manifest leaves the cleaned directory
The system SHALL treat every file under `results/cleaned/` except `clean_manifest.json` as participant-level: ignored by git, excluded by the sync script and never quoted. `clean_manifest.json` SHALL be the only file under `results/cleaned/` that is committed and synced.

#### Scenario: Git sees only the manifests
- **WHEN** `git status` runs after a full clean
- **THEN** the only untracked paths under `results/cleaned/` are `p180/clean_manifest.json` and `nmr/clean_manifest.json`

#### Scenario: Sync carries only the manifests
- **WHEN** `scripts/sync_results.sh -n` lists what a pull would transfer
- **THEN** under `cleaned/` it lists only the two `clean_manifest.json` files
