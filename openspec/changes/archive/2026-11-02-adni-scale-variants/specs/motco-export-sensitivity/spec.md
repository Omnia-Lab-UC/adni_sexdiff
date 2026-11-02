## ADDED Requirements

### Requirement: Scale variant export
Under a scale variant (`raw_scale`, `log2_plus_one`, `glog`), every kept cell of both blocks SHALL take the variant's transform of `SCALE_VARIANT_RULE` in place of the rule's `log2(x + floor)`, on the primary's membership. The rule's floor SHALL be computed, gated and recorded per metabolite and not applied. The participants, the metadata and the covariates SHALL be the primary's, and the variant SHALL read no data-root file.

#### Scenario: Raw scale
- **WHEN** `export-sensitivity --variant raw_scale` exports the committed clean and cohort outputs
- **THEN** each kept cell of its `p180.csv` and `nmr.csv` equals the cleaned concentration, its manifest records units `x`, and each feature table records the rule's floor beside an empty offset

#### Scenario: log2(x + 1)
- **WHEN** `export-sensitivity --variant log2_plus_one` exports the committed clean and cohort outputs
- **THEN** each kept cell equals `log2` of the cleaned concentration plus 1, its manifest records units `log2(x + 1)`, and each feature's offset is 1

#### Scenario: Generalized log
- **WHEN** `export-sensitivity --variant glog` exports the committed clean and cohort outputs
- **THEN** each kept cell equals `log2((x + sqrt(x² + λ²)) / 2)` with λ the metabolite's smallest positive value over the exported participants divided by 10, each feature's offset is its λ, and a zero cell lands at `log2(λ / 2)`

#### Scenario: Membership and labels unchanged
- **WHEN** a scale variant is exported
- **THEN** its `p180.csv` and `nmr.csv` hold the primary's columns in the primary's order, and its `metadata.csv` and `covariates.csv` hash to the primary export manifest's records

#### Scenario: No data root
- **WHEN** a scale variant runs with no data root present
- **THEN** it completes, since only `nist_bridge` reads the data root

### Requirement: Undefined λ stops the generalized log
`glog` SHALL stop before anything is written when a kept metabolite has no positive cell among the exported participants, naming the block and the count of such metabolites, never a participant.

#### Scenario: A metabolite with no positive cell
- **WHEN** a kept column of a scratch copy of a cleaned table holds no positive value and `glog` runs on it
- **THEN** the step stops naming the block and the count of metabolites whose λ is undefined, exits with an error and writes nothing

#### Scenario: Committed inputs
- **WHEN** `glog` runs on the committed clean outputs
- **THEN** every kept metabolite of both blocks has a positive λ and the step completes

### Requirement: Scale variant counts are recorded
A scale variant's export manifest SHALL record, per block on the variant's scale, the shape counts and the numerical rank, the run offset, and the offset summary (for `log2_plus_one` the metabolites whose median lies below the offset), with the primary's shape counts copied beside its own.

#### Scenario: Counts on the committed inputs
- **WHEN** the three scale variants export the committed inputs
- **THEN** their manifests record p180 |skew| > 1 / largest |z| > 8 at 46 / 12, 14 / 9 and 6 / 6, NMR at 43 / 4, 30 / 4 and 25 / 13, NMR numerical rank 104, 165 and 165, and for `log2_plus_one` a median below 1 for 46 p180 and 129 NMR metabolites, with no deviation

#### Scenario: Primary shape copied
- **WHEN** a scale variant's export manifest is written
- **THEN** its reference block carries the primary export manifest's shape counts per block, value for value

### Requirement: The variants registered before this change are unchanged
After this change `nist_bridge`, `per_run_standardized` and `nmr_all_columns` SHALL keep their committed outputs. On a data machine, a pinned in-place rerun of each SHALL write every CSV, `summary.md`, `export_sensitivity.md` and bridge table with the committed bytes, and each committed `summary.md`, `export_sensitivity.md` and `diagnostics.md`, re-rendered from its records, SHALL equal the committed file.

#### Scenario: Pinned rerun of the registered variants
- **WHEN** `export-sensitivity --variant <name> --force` reruns pinned in place for each of the three, with its `diagnostics/` moved aside
- **THEN** every CSV, `summary.md`, `export_sensitivity.md` and `nist_bridge.csv` hashes to the committed file or to the hash its committed manifest records, and the manifests and `result.json` differ only in time, revision, runtime and the hashes of the files that carry them

#### Scenario: Re-rendered text
- **WHEN** the variant renderers run on the committed records of `nmr_all_columns`
- **THEN** its `summary.md`, `export_sensitivity.md` and `diagnostics.md` equal the committed files byte for byte

## MODIFIED Requirements

### Requirement: Predeclared variant registry
The step SHALL run only the variants of the registry `EXPORT_VARIANTS`, a constant decided by a change proposal before any run: `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`. A variant SHALL be selected by name (`--variant`, or `all`); no flag SHALL set or change a variant's settings, the bridge rule, a scale or any analysis setting.

#### Scenario: Unknown variant
- **WHEN** `export-sensitivity --variant log10_scale` runs and `log10_scale` is not in the registry
- **THEN** the command is rejected naming the registered variants, and nothing is read or written

#### Scenario: All variants
- **WHEN** `export-sensitivity --variant all` runs
- **THEN** each registered variant runs in registry order, each into its own directory

#### Scenario: Scale variant by name
- **WHEN** `export-sensitivity --variant glog` runs with the other variants' outputs present
- **THEN** it runs `glog` alone into its own directory and reads or writes no other variant's directory

### Requirement: Unchanged files equal the primary's
A variant export SHALL keep the primary's participants, order, metadata, covariates and every block it does not change. The CSV of each such block, `metadata.csv` and `covariates.csv` SHALL hash to the primary export manifest's records. A difference SHALL be a finding.

#### Scenario: Unchanged files
- **WHEN** the `nist_bridge` export is written
- **THEN** its `nmr.csv`, `metadata.csv` and `covariates.csv` have the sha256 the primary export manifest records

#### Scenario: Unchanged files of the NMR variant
- **WHEN** the `nmr_all_columns` export is written
- **THEN** its `p180.csv`, `metadata.csv` and `covariates.csv` have the sha256 the primary export manifest records

#### Scenario: Unchanged files of a scale variant
- **WHEN** a scale variant's export is written
- **THEN** its `metadata.csv` and `covariates.csv` have the sha256 the primary export manifest records, and no block CSV is expected to

### Requirement: Comparison summary
`export_sensitivity.md` SHALL print the table with a status per statistic, `same` or `differs (<dependence>)` with the variant's dependence label, the primary's status named the result, and the run offset per block from both export manifests. It SHALL add the bridge summary for `nist_bridge`, the block shares and NMR shape counts for `nmr_all_columns`, and for a scale variant its transform, its offsets and the shape counts and numerical rank of each block in both exports, then print `READING_RULES` and the variant's rule set verbatim.

#### Scenario: Status differs
- **WHEN** `angle` is not rejected in the primary and rejected in `per_run_standardized`
- **THEN** its status reads `differs (run-handling dependence)`, the primary's status is named the result, and a finding records it

#### Scenario: Status differs in the NMR variant
- **WHEN** `delta` is not rejected in the primary and rejected in `nmr_all_columns`
- **THEN** its status reads `differs (feature-membership dependence)`, the sentence cites membership rules 2 and 6, the primary's status is named the result, and a finding records it

#### Scenario: Status differs in a scale variant
- **WHEN** `delta` is not rejected in the primary and rejected in `raw_scale`
- **THEN** its status reads `differs (scale dependence)`, the sentence cites scale rules 2 and 6, the primary's status is named the result, and a finding records it

#### Scenario: Scale variant lines
- **WHEN** the `glog` comparison summary is written
- **THEN** its export-variant section names the transform, λ's rule, the offset summary, and per block the shape counts and numerical rank of the primary export and of the variant export, every value read from the two export manifests

### Requirement: Predeclared counts
Each variant manifest SHALL record `EXPORT_VARIANT_EXPECTED_COUNTS` beside the observed counts: the keys of `EXPORT_EXPECTED_COUNTS` with the variant's run offset, the unchanged files' hashes, every key of `ANALYSIS_EXPECTED_COUNTS` with the variant's features, and its own keys: the bridged metabolites for `nist_bridge`; for `nmr_all_columns` the derived columns kept, the joint features, the NMR shape counts and the rule's columns equal; for a scale variant the shape counts and numerical rank per block and, for `log2_plus_one`, the metabolites with a median below the offset. A deviation SHALL be a finding, never a stop.

#### Scenario: Count deviation
- **WHEN** the bridge rule bridges 125 metabolites against the predeclared 126
- **THEN** the manifest records both values and a finding, and the run completes

#### Scenario: NMR variant counts
- **WHEN** `nmr_all_columns` runs on the committed inputs
- **THEN** its export manifest records 378 joint features, NMR |skew| > 1 at 24 and largest |z| > 8 at 9, NMR phase |d| > 0.5 at 5, and no deviation, and its analysis manifest expects features p180 133, NMR 245, joint 378

#### Scenario: Scale variant counts
- **WHEN** `raw_scale` runs on the committed inputs
- **THEN** its export manifest records p180 |skew| > 1 at 46 and largest |z| > 8 at 12, NMR at 43 and 4, NMR numerical rank 104, p180 phase |d| > 0.5 / > 1 at 108 / 76, and no deviation, and its analysis manifest expects every key of `ANALYSIS_EXPECTED_COUNTS`

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

#### Scenario: Rank differs in a scale variant
- **WHEN** `log2_plus_one` selects rank 6 and the primary rank 8
- **THEN** the finding records both and cites scale rule 3

### Requirement: Reading rules bind every reader of a variant
Each variant SHALL carry its rule set, named by `EXPORT_VARIANT_RULE_SETS`: `EXPORT_VARIANT_READING_RULES` for the p180 variants, `NMR_MEMBERSHIP_READING_RULES` for `nmr_all_columns`, `SCALE_VARIANT_READING_RULES` for `raw_scale`, `log2_plus_one` and `glog`. That set SHALL be printed verbatim after `READING_RULES` in its `summary.md`, `export_sensitivity.md`, `diagnostics.md` and every report that quotes it. No variant value SHALL change a constant, select a metabolite, a covariate or a scale, rerun the primary or define a new variant.

#### Scenario: Variant summary
- **WHEN** a variant's `summary.md` is written
- **THEN** it names the variant, states that the primary stays primary, and prints both sets of rules

#### Scenario: NMR variant summary
- **WHEN** the `nmr_all_columns` `summary.md` is written
- **THEN** it prints `READING_RULES` then the eight `NMR_MEMBERSHIP_READING_RULES`, string-equal to the constant, and no line of `EXPORT_VARIANT_READING_RULES`

#### Scenario: Scale variant summary
- **WHEN** a scale variant's `summary.md` is written
- **THEN** it prints `READING_RULES` then the eight `SCALE_VARIANT_READING_RULES`, string-equal to the constant, cited as "scale rule N", and its `phase` line says the variant changes the scale of both blocks only and `phase` carries the run difference as in the primary

#### Scenario: Mapping out of step
- **WHEN** `EXPORT_VARIANTS` holds a variant that `EXPORT_VARIANT_RULE_SETS` does not name
- **THEN** importing the constants fails naming both constants, before any step runs
