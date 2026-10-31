## ADDED Requirements

### Requirement: NMR membership variant export
Under `nmr_all_columns`, every cleaned NMR column SHALL enter the NMR block in cleaned order, the 80 columns `EXPORT_FEATURE_RULE` marks `derived` among them, and each SHALL take the rule's scale, `log2(x + floor)` with its own 5 % floor over the exported participants. The p180 block, the participants, the metadata and the covariates SHALL be the primary's, and the variant SHALL read no data-root file.

#### Scenario: All columns kept
- **WHEN** `export-sensitivity --variant nmr_all_columns` exports the committed clean and cohort outputs
- **THEN** its `nmr.csv` holds `rid` and the 245 cleaned NMR columns in cleaned order, and its manifest records NMR features cleaned 245, kept 245, excluded as derived 0, and derived kept percentage 72, ratio 4, degree 1, size 3

#### Scenario: Feature table
- **WHEN** the variant's `features_nmr.csv` is written
- **THEN** each of the 245 rows has status `kept`, its family, its floor and its transformed-scale columns filled

#### Scenario: No data root
- **WHEN** `nmr_all_columns` runs with no data root present
- **THEN** it completes, since only `nist_bridge` reads the data root

### Requirement: The rule's columns equal the primary's
Under `nmr_all_columns`, the NMR columns `EXPORT_FEATURE_RULE` keeps SHALL equal the primary `nmr.csv`'s, column for column and cell for cell, and the manifest SHALL record the comparison. A difference SHALL be a finding, never a stop.

#### Scenario: Concentrations unchanged
- **WHEN** the variant export is written on the committed inputs
- **THEN** its manifest records that the 165 concentration columns equal the primary's, and no finding names them

#### Scenario: A concentration differs
- **WHEN** one cell of a concentration column of the variant differs from the primary's
- **THEN** the manifest records the comparison false and a finding names the block and the count of columns that differ, and the run completes

### Requirement: The p180 variants are unchanged
After this change the two p180 variants SHALL keep their committed outputs. On a data machine, a pinned in-place rerun of each SHALL write every CSV, `summary.md`, `export_sensitivity.md` and bridge table with the committed bytes. Each of their committed `summary.md`, `export_sensitivity.md` and `diagnostics.md`, re-rendered from its committed records, SHALL equal the committed file.

#### Scenario: Pinned rerun of the p180 variants
- **WHEN** `export-sensitivity --variant nist_bridge --force` and `--variant per_run_standardized --force` rerun pinned in place, with their `diagnostics/` moved aside
- **THEN** every CSV, `summary.md`, `export_sensitivity.md` and `nist_bridge.csv` hashes to the committed file or to the hash its committed manifest records, and the manifests and `result.json` differ only in time, revision, runtime and the hashes of the files that carry them

#### Scenario: Re-rendered text
- **WHEN** the variant renderers run on the committed records of `nist_bridge`
- **THEN** its `summary.md`, `export_sensitivity.md` and `diagnostics.md` equal the committed files byte for byte

## MODIFIED Requirements

### Requirement: Predeclared variant registry
The step SHALL run only the variants of the registry `EXPORT_VARIANTS`, a constant decided by a change proposal before any run: `nist_bridge`, `per_run_standardized` and `nmr_all_columns`. A variant SHALL be selected by name (`--variant`, or `all`); no flag SHALL set or change a variant's settings, the bridge rule or any analysis setting.

#### Scenario: Unknown variant
- **WHEN** `export-sensitivity --variant raw_scale` runs and `raw_scale` is not in the registry
- **THEN** the command is rejected naming the registered variants, and nothing is read or written

#### Scenario: All variants
- **WHEN** `export-sensitivity --variant all` runs
- **THEN** each registered variant runs in registry order, each into its own directory

### Requirement: Unchanged files equal the primary's
A variant export SHALL keep the primary's participants, order, metadata, covariates and every block it does not change. The CSV of each such block, `metadata.csv` and `covariates.csv` SHALL hash to the primary export manifest's records. A difference SHALL be a finding.

#### Scenario: Unchanged files
- **WHEN** the `nist_bridge` export is written
- **THEN** its `nmr.csv`, `metadata.csv` and `covariates.csv` have the sha256 the primary export manifest records

#### Scenario: Unchanged files of the NMR variant
- **WHEN** the `nmr_all_columns` export is written
- **THEN** its `p180.csv`, `metadata.csv` and `covariates.csv` have the sha256 the primary export manifest records

### Requirement: Variant values are label-blind
No variant SHALL read sex, stage or a covariate to compute a value. A participant whose run differs from its `phase` SHALL be a finding.

#### Scenario: Labels permuted
- **WHEN** sex and stage are permuted in `cohort.csv` and a variant export is rerun
- **THEN** its `p180.csv` and `nmr.csv` are byte-identical to the unpermuted run's

### Requirement: Comparison summary
`export_sensitivity.md` SHALL print the table with a status per statistic, `same` or `differs (<dependence>)` with the variant's dependence label, the primary's status named the result, and the run offset per block from both export manifests. It SHALL add the bridge summary for `nist_bridge` and the block shares and NMR shape counts for `nmr_all_columns`, then print `READING_RULES` and the variant's rule set verbatim.

#### Scenario: Status differs
- **WHEN** `angle` is not rejected in the primary and rejected in `per_run_standardized`
- **THEN** its status reads `differs (run-handling dependence)`, the primary's status is named the result, and a finding records it

#### Scenario: Status differs in the NMR variant
- **WHEN** `delta` is not rejected in the primary and rejected in `nmr_all_columns`
- **THEN** its status reads `differs (feature-membership dependence)`, the sentence cites membership rules 2 and 6, the primary's status is named the result, and a finding records it

### Requirement: Predeclared counts
Each variant manifest SHALL record `EXPORT_VARIANT_EXPECTED_COUNTS` beside the observed counts: the keys of `EXPORT_EXPECTED_COUNTS` with the variant's run offset, the unchanged files' hashes, every key of `ANALYSIS_EXPECTED_COUNTS` with the variant's features, and its own keys: the bridged metabolites for `nist_bridge`; for `nmr_all_columns` the derived columns kept, the joint features, the NMR shape counts and the rule's columns equal. A deviation SHALL be a finding, never a stop.

#### Scenario: Count deviation
- **WHEN** the bridge rule bridges 125 metabolites against the predeclared 126
- **THEN** the manifest records both values and a finding, and the run completes

#### Scenario: NMR variant counts
- **WHEN** `nmr_all_columns` runs on the committed inputs
- **THEN** its export manifest records 378 joint features, NMR |skew| > 1 at 24 and largest |z| > 8 at 9, NMR phase |d| > 0.5 at 5, and no deviation, and its analysis manifest expects features p180 133, NMR 245, joint 378

### Requirement: Findings
Findings SHALL record:
- every finding condition of `export` and `analyze`;
- a rank that differs from the primary's, and a statistic whose status differs, each named under the variant's rule set;
- a QC archive or workbook hash that differs from its predeclared value, and an unmatched metabolite;
- a run that differs from `phase`, and stale diagnostics;
- the rule's columns differing from the primary's.

A finding SHALL name counts, settings and files, never a participant.

#### Scenario: Rank differs
- **WHEN** the variant's CV-selected rank is 6 and the primary's is 8
- **THEN** a finding records both, reported beside `angle` and not ranked

#### Scenario: Rank differs in the NMR variant
- **WHEN** `nmr_all_columns` selects rank 5 and the primary rank 8
- **THEN** the finding records both and cites membership rule 3

### Requirement: Reading rules bind every reader of a variant
Each variant SHALL carry its rule set, named by `EXPORT_VARIANT_RULE_SETS`: `EXPORT_VARIANT_READING_RULES` for the p180 variants, `NMR_MEMBERSHIP_READING_RULES` for `nmr_all_columns`. That set SHALL be printed verbatim after `READING_RULES` in its `summary.md`, `export_sensitivity.md`, `diagnostics.md` and every report that quotes it. No variant value SHALL change a constant, select a metabolite or covariate, rerun the primary or define a new variant.

#### Scenario: Variant summary
- **WHEN** a variant's `summary.md` is written
- **THEN** it names the variant, states that the primary stays primary, and prints both sets of rules

#### Scenario: NMR variant summary
- **WHEN** the `nmr_all_columns` `summary.md` is written
- **THEN** it prints `READING_RULES` then the eight `NMR_MEMBERSHIP_READING_RULES`, string-equal to the constant, and no line of `EXPORT_VARIANT_READING_RULES`

#### Scenario: Mapping out of step
- **WHEN** `EXPORT_VARIANTS` holds a variant that `EXPORT_VARIANT_RULE_SETS` does not name
- **THEN** importing the constants fails naming both constants, before any step runs
