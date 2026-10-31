## ADDED Requirements

### Requirement: Expected counts on an export variant
On an export variant whose `EXPORT_VARIANT_EXPECTED_COUNTS` entry holds a `diagnostics` key, the manifest SHALL record those counts as the expected ones: the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS` with the variant's block features. On a variant without the key, the rank-independent keys SHALL be expected unchanged.

#### Scenario: NMR variant read
- **WHEN** the step reads `results/motco_export_sensitivity/nmr_all_columns/` with its own export directory
- **THEN** the manifest expects 1501 participants, the primary's cells, p180 133 and NMR 245 features with 3 PCs each, and records no deviation on the committed outputs

#### Scenario: p180 variant read
- **WHEN** the step reads `results/motco_export_sensitivity/nist_bridge/` with its own export directory
- **THEN** the manifest expects the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS`, as before this change, and its outputs equal the committed ones

## MODIFIED Requirements

### Requirement: Reading rules of a sensitivity read
`diagnostics.md` SHALL name the sensitivity it reads and carry its reading rules after `READING_RULES`. On an arm it SHALL name the arm and its latent adjustment and print `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`. On an export variant (an analysis manifest that records step `export-sensitivity` and a variant name) it SHALL name the variant and print the variant's rule set, named by `EXPORT_VARIANT_RULE_SETS`, after `READING_RULES`.

#### Scenario: Arm read
- **WHEN** the analysis read is `results/motco_latent_sensitivity/analysis/`, whose manifest records latent adjustment `stage`
- **THEN** `diagnostics.md` names it the `stage`-conditioned sensitivity arm, calls each flagged row a finding about the arm's measurement space, prints `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Export variant read
- **WHEN** the analysis read is `results/motco_export_sensitivity/nist_bridge/analysis/` with its own export directory
- **THEN** `diagnostics.md` names the export variant `nist_bridge`, calls each flagged row a finding about the variant's measurement space, prints `EXPORT_VARIANT_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: NMR variant read
- **WHEN** the analysis read is `results/motco_export_sensitivity/nmr_all_columns/analysis/` with its own export directory
- **THEN** `diagnostics.md` names the export variant `nmr_all_columns` and the NMR block it changes, calls each flagged row a finding about the variant's measurement space under membership rule 7, prints `NMR_MEMBERSHIP_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary
