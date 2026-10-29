# raw-input-integrity Specification

## Purpose
Defines how a pipeline step treats the raw ADNI files it reads from the data root: every required name present, content hashed through the symlinks into the LONI archive, known hand-applied repairs recognised by hash, an unrepaired known-defective file refused, an unknown hash recorded. Written for `clean`; the cohort step reuses it for the clinical tables.

## Requirements

### Requirement: Required files are present before work starts
The system SHALL check that every raw file a step needs exists under the data root, by its exact expected name, before any file is read or any output directory created, and SHALL stop naming every missing name. It SHALL NOT rely on the reader's own handling of absent files. An archive a step reads members from is a raw file under its own name; a member absent from a present archive SHALL stop the step naming the archive and the member.

#### Scenario: Missing LOD workbook
- **WHEN** `4610 FIA p180 Data.xlsx` is absent from the data root and `clean --platform p180` runs
- **THEN** the step stops naming that file, with no working copy made, although metabo_adni itself would only fail later

#### Scenario: Missing concentration file
- **WHEN** `ADMCDUKEP180FIA_01_15_16.csv` is absent
- **THEN** the step stops naming it, although metabo_adni's reader would skip it silently

#### Scenario: Missing QC archive
- **WHEN** `ADMC_supplement.zip` is absent from the top level of the data root and `export-sensitivity --variant nist_bridge` runs
- **THEN** the step stops naming that file before any output directory is created

#### Scenario: Missing archive member
- **WHEN** `ADMCDUKEP180SUPP_20170410.zip` is present but holds no `4610 FIA p180 QC and NIST Data.xlsx`
- **THEN** the step stops naming the archive and the member

### Requirement: Content is hashed through the symlinks and the target is recorded
The system SHALL compute the sha256 of each input's resolved content (following symlinks), record it in the manifest with the file's expected name, its symlink target relative to the data root when it is a symlink, and its size in bytes, and SHALL never alter the archive. For an archive read in place, the manifest SHALL also record each member read, by its member name, with the sha256 of its bytes; nothing SHALL be extracted into the data root.

#### Scenario: Symlinked input
- **WHEN** `ADNINIGHTINGALE2.csv` is a symlink to `Metabolomics/NMR/ADNINIGHTINGALE2_11Jul2024.csv`
- **THEN** the manifest records the name, the target path and the sha256 of the target's bytes

#### Scenario: Archive member
- **WHEN** `export-sensitivity --variant nist_bridge` reads `4097_FIA_NIST_and_QC_Data.xlsx` inside `ADMC_supplement.zip`
- **THEN** the manifest records the archive's name, target, size and sha256, and the member's name and sha256, and the data root holds no extracted copy

### Requirement: Known repairs are recognised by hash
The system SHALL hold a registry of known raw-file defects, each with the defect, the hand-applied repair, the sha256 of LONI's bytes and the sha256 of the repaired file. When an input's hash equals a registry entry's repaired hash, the manifest SHALL name the repair beside that input.

#### Scenario: Repaired UPLC ADNI-GO/2 file
- **WHEN** the resolved content of `ADMCDUKEP180UPLCADNI2GO.csv` hashes to `7ad17d63eed26368a3e51254c942e9c2f39890d43decda37f7b1a2ade38de3a6`
- **THEN** the manifest records that the archive copy carries the closing-quote repair of 2026-10-26

### Requirement: An unrepaired known-defective file is refused
When an input's hash equals a registry entry's unrepaired hash, the system SHALL stop before any reader runs, naming the file, the defect and the repair the archive copy must carry. It SHALL NOT repair the archive, the symlink target or a working copy on the caller's behalf.

#### Scenario: Fresh LONI download placed unrepaired
- **WHEN** `ADMCDUKEP180UPLCADNI2GO.csv` resolves to bytes hashing to `f28ede9aa70e02d2c8bf4ef2b3f4873a217675e424cd2498e4dd3f43d03df326`
- **THEN** the step stops, says the file lacks its final closing double quote and that a `"` and a newline must be appended to the archive copy, and writes nothing

### Requirement: An unknown hash is a finding
When an input's hash matches neither the hash recorded at the last predeclaration nor a registry entry, the system SHALL proceed and record a finding naming the file and the observed hash, so that a fresh LONI download is visible in the manifest beside any count deviation it causes.

#### Scenario: Re-downloaded fasting file
- **WHEN** `BIOMARK.csv` hashes to a value not seen before
- **THEN** the step completes and `findings` holds a line naming `BIOMARK.csv` and its hash
