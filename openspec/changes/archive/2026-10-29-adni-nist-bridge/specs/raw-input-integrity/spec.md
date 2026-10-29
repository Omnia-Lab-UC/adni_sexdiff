# Spec Delta

## MODIFIED Requirements

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
