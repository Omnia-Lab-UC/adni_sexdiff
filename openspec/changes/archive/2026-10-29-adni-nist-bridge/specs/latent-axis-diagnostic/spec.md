# Spec Delta

## MODIFIED Requirements

### Requirement: Labels are read but feed no choice
The diagnostic reads sex and stage. Its outputs SHALL NOT be an input of `export`, `analyze`, any sensitivity arm or any export variant, and the documentation SHALL state that variants and arms are predeclared in a change proposal, never derived from a diagnostic value.

#### Scenario: No downstream read
- **WHEN** any `export`, `analyze`, `latent-sensitivity` or `export-sensitivity` command runs
- **THEN** it reads nothing under any diagnostics directory

### Requirement: Reading rules carried
`diagnostics.md` SHALL print `READING_RULES` verbatim and SHALL state that an axis correlated with a variable is a finding about the measurement space of the analysis read, not a reinterpretation of its statistics or p-values, that the flag is a reporting threshold and not an adoption rule, and that the primary analysis stays primary.

#### Scenario: Run axis found
- **WHEN** `pls_0` is flagged against `phase`
- **THEN** `diagnostics.md` lists the row first, names it a measurement-space finding, and does not restate `delta`, `angle` or `shape` as different

#### Scenario: Primary output unchanged
- **WHEN** the diagnostic runs pinned on the primary analysis after this change
- **THEN** its four CSVs and `diagnostics.md` have the sha256 the committed diagnostics manifest records

## ADDED Requirements

### Requirement: Reading rules of a sensitivity read
`diagnostics.md` SHALL name the sensitivity it reads and carry its reading rules after `READING_RULES`. On an arm it SHALL name the arm and its latent adjustment and print `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`. On an export variant (an analysis manifest that records step `export-sensitivity` and a variant name) it SHALL name the variant and print `EXPORT_VARIANT_READING_RULES` after `READING_RULES`.

#### Scenario: Arm read
- **WHEN** the analysis read is `results/motco_latent_sensitivity/analysis/`, whose manifest records latent adjustment `stage`
- **THEN** `diagnostics.md` names it the `stage`-conditioned sensitivity arm, calls each flagged row a finding about the arm's measurement space, prints `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Export variant read
- **WHEN** the analysis read is `results/motco_export_sensitivity/nist_bridge/analysis/` with its own export directory
- **THEN** `diagnostics.md` names the export variant `nist_bridge`, calls each flagged row a finding about the variant's measurement space, prints `EXPORT_VARIANT_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary
