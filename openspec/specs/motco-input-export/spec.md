# motco-input-export Specification

## Purpose
Defines the `export` step: from the outputs of `clean` and `cohort` only, the MOTCO blocks of the analysis cohort under the decided feature rule (membership by family, a floored log2 scale), the metadata and covariate tables aligned row for row, a feature table per platform, and a manifest whose counts are checked against the predeclared ones.

## Requirements

### Requirement: Inputs are the clean and cohort outputs only
The system SHALL read the cleaned tables and their `clean_manifest.json` from the clean output root, and `cohort.csv` and `cohort_manifest.json` from the cohort directory. It SHALL read no data-root file and no other file.

#### Scenario: Inputs listed
- **WHEN** `export` runs
- **THEN** the manifest lists as inputs exactly `p180/P180.csv`, `nmr/NMR.csv`, both clean manifests, `cohort.csv` and `cohort_manifest.json`, each with its sha256, and no data-root path

### Requirement: Inputs are checked against their manifests and the chain
The system SHALL compare the sha256 of every cleaned table and of `cohort.csv` with the hash its manifest records, and the clean hashes the cohort manifest records with the clean manifests' output hashes. On any mismatch or absent manifest it SHALL stop before writing anything, naming the file.

#### Scenario: Cleaned table changed after cohort
- **WHEN** `results/cleaned/nmr/NMR.csv` hashes to a value other than the one in `results/cleaned/nmr/clean_manifest.json`
- **THEN** the step stops naming `nmr/NMR.csv` and no export directory is created

#### Scenario: Cohort built from an earlier clean
- **WHEN** `cohort_manifest.json` records a hash for `P180.csv` different from the one in `results/cleaned/p180/clean_manifest.json`
- **THEN** the step stops naming `P180.csv` and the `cohort` command, and writes nothing

### Requirement: Exported participants are the analysis cohort in cohort order
The system SHALL export the rows of `cohort.csv` that carry both platform flags, in the order of `cohort.csv`. A cohort participant absent from a cleaned table SHALL stop the step with the platform and a count.

#### Scenario: Intersection exported
- **WHEN** the export is built from the inventoried files
- **THEN** every participant-indexed output has 1501 rows, Female CN / MCI / AD 237 / 310 / 125 and Male 223 / 448 / 158

#### Scenario: Participant missing from a block
- **WHEN** one both-flagged participant of `cohort.csv` has no row in `NMR.csv`
- **THEN** the step stops naming `nmr` and the count 1, no identifier, and writes nothing

### Requirement: Block membership by family
The `p180` block SHALL hold every cleaned p180 metabolite. The `nmr` block SHALL hold every cleaned NMR column except the derived families, recognised by name: percentages (suffix `_PCT`), ratios (containing `_BY_`), the degree of unsaturation (`UNSATURATION`) and particle sizes (suffix `_SIZE`). Each excluded column SHALL appear in the feature table with status `derived` and its family.

#### Scenario: Percentage excluded
- **WHEN** the cleaned NMR table holds `XL_VLDL_PL_PCT`
- **THEN** `nmr.csv` has no such column and `features_nmr.csv` lists it with status `derived` and family `percentage`

#### Scenario: Concentration kept
- **WHEN** the cleaned NMR table holds `XL_VLDL_PL` and `GLYCA`
- **THEN** both are columns of `nmr.csv` with status `kept`

#### Scenario: Counts under the inventoried tables
- **WHEN** the export is built from the inventoried files
- **THEN** `p180.csv` has 133 metabolite columns and `nmr.csv` has 165, with 72 percentages, 4 ratios, 1 degree and 3 sizes derived

### Requirement: Floored log2 scale
Every kept value SHALL be exported as `log2(x + floor)`, where the floor of a metabolite is its 5 % quantile over the exported participants with linear interpolation, computed on that metabolite's cleaned values. The floor SHALL be recorded per feature. A metabolite whose floor is not positive SHALL stop the step, naming the platform and the count. No value SHALL be imputed, replaced, winsorized or removed.

#### Scenario: Zeros pass through the floor
- **WHEN** `BOHBUTYRATE` has 34 zero cells among the exported participants and a positive floor
- **THEN** its exported column is finite everywhere and the feature table records 34 zero cells

#### Scenario: Non-positive floor
- **WHEN** a kept metabolite's 5 % quantile is 0
- **THEN** the step stops naming the platform and the number of such metabolites, and writes nothing

#### Scenario: Finite blocks
- **WHEN** the export is built from the inventoried files
- **THEN** no cell of `p180.csv` or `nmr.csv` is missing or non-finite, and the manifest records 0 non-finite cells per block

### Requirement: Membership and scale are label-blind
The system SHALL compute membership and every floor without reading sex, stage or a covariate value. Sex and stage SHALL be read only to write `metadata.csv` and to count cells; `phase` SHALL be read only to write `covariates.csv` and to describe the phase offset.

#### Scenario: Same blocks under permuted labels
- **WHEN** the export is rerun on a cohort table whose `sex` and `stage` columns are permuted among participants
- **THEN** `p180.csv`, `nmr.csv` and both feature tables are byte-identical to the original export

### Requirement: Export contract
The system SHALL write `p180.csv` and `nmr.csv` (first column `rid`, then the kept metabolites under their cleaned names), `metadata.csv` (`rid`, `sex`, `stage`), `covariates.csv` (`rid`, `age`, `education`, `apoe4`, `phase`, `statin`, values copied from `cohort.csv`) and `features_p180.csv`, `features_nmr.csv`. All participant-indexed files SHALL list the same `rid` values in the same order.

#### Scenario: Rows align
- **WHEN** the export is built
- **THEN** the `rid` columns of `p180.csv`, `nmr.csv`, `metadata.csv` and `covariates.csv` are identical

#### Scenario: Stage labels
- **WHEN** `metadata.csv` is written
- **THEN** every `stage` is one of `CN`, `MCI`, `AD` and every `sex` one of `Female`, `Male`

#### Scenario: Ignored
- **WHEN** `git check-ignore` runs on `results/motco_input/p180.csv`, `metadata.csv`, `covariates.csv` and `features_nmr.csv`
- **THEN** each is ignored, and `results/motco_input/manifest.json` is not

### Requirement: Covariates exported, not applied
The system SHALL copy the covariate columns unchanged and SHALL NOT residualize, center or scale any block by a covariate, including per run or per phase. The manifest SHALL record each covariate's coding as the cohort manifest declares it and that covariates are not applied.

#### Scenario: Codings recorded
- **WHEN** the manifest is written
- **THEN** it records `apoe4`, `phase` and `statin` as categorical with their levels, `age` and `education` as numeric, and `covariates_applied` false

### Requirement: Feature table per platform
Each `features_<platform>.csv` SHALL hold one row per cleaned metabolite with its family, status (`kept` or `derived`), zero cells, median, floor, floor over median, skew on the raw and the transformed scale, the largest absolute z-score on the transformed scale and the phase offset `d`; the transformed-scale columns SHALL be empty for derived rows. It SHALL hold no participant value or identifier.

#### Scenario: Accounting closes
- **WHEN** `features_nmr.csv` is tallied by status
- **THEN** `kept` plus `derived` equals 245 and `kept` equals the number of metabolite columns of `nmr.csv`

### Requirement: Manifest content
The system SHALL write `manifest.json` with the keys `step`, `versions`, `git_revision`, `inputs`, `settings`, `outputs`, `findings` and the export's counts: the rule as applied, block order, column names, stage order and group values, covariate codings, n per sex × stage, feature counts per status and family, zero cells, floors not positive, non-finite cells, block shares, and per block the distribution-shape counts, the spectrum and the phase offset. It SHALL hold no `RID`.

#### Scenario: Phase offset recorded
- **WHEN** the export is built from the inventoried files
- **THEN** the manifest records for `p180` 80 metabolites with |d| > 1 and for `nmr` 0, each with the median |d| and the correlation of the first two principal components with phase

#### Scenario: Shares recorded
- **WHEN** the export is built from the inventoried files
- **THEN** the manifest records the p180 share of the joint matrix as 133 / 298

### Requirement: Counts are checked against the predeclared ones
The system SHALL compare its counts with `EXPORT_EXPECTED_COUNTS` (participants, sex × stage, features per status and family per platform, zero cells, floors not positive, non-finite cells, metabolites with |d| > 1, missing covariate values) and record expected, observed and every deviation. A deviation SHALL be a finding and a printed line; it SHALL NOT stop the step or change the rule.

#### Scenario: Inventoried files
- **WHEN** the export is built from the files whose hashes the spike recorded
- **THEN** the manifest's deviations list is empty

#### Scenario: Different column set
- **WHEN** the cleaned NMR table has 164 concentration columns instead of 165
- **THEN** the step completes, `findings` and the output name the expected and observed count, and the rule applied is unchanged

### Requirement: Output directory is complete or absent
The system SHALL build the outputs in `results/motco_input.tmp/` and rename it to `results/motco_input/` only when every file is written. An existing `results/motco_input/` SHALL be replaced only under `--force`.

#### Scenario: Existing output without force
- **WHEN** `results/motco_input/` exists and `export` runs without `--force`
- **THEN** the step stops naming the directory and leaves it unchanged

### Requirement: Reruns are deterministic
The system SHALL produce byte-identical CSV outputs when rerun on the same inputs.

#### Scenario: Rerun with force
- **WHEN** `export --force` runs twice on the same inputs
- **THEN** every CSV has the same sha256 both times

### Requirement: No participant identifier in any message
Progress output, error messages, findings and the manifest SHALL name files, columns, platforms, values and counts, never a participant identifier.

#### Scenario: Progress lines
- **WHEN** `export` runs
- **THEN** every printed line starts with `[export]` and holds no `rid` value
