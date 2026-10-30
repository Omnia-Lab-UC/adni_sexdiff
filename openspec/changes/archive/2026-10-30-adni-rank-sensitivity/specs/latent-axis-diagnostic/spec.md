# Spec Delta

## ADDED Requirements

### Requirement: Rank sweep read and its expected counts
When the analysis read is a forced rank of the rank sweep (an analysis manifest that records step `rank-sensitivity`), the manifest SHALL record its forced rank, and the expected counts SHALL be the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS`; on the top rank also the read (rank 12, `forced`, no latent adjustment, `n_jobs` 1) and its rows (`RANK_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]`). A deviation SHALL be a finding, never a stop.

#### Scenario: Forced rank recorded
- **WHEN** the step reads a rank directory of the sweep
- **THEN** the manifest records the analysis read's forced rank, `component_selection` `forced`, and that it is not the primary

#### Scenario: Counts match on the top rank
- **WHEN** the step reads `results/motco_rank_sensitivity/rank_12` with the primary export and cohort
- **THEN** the manifest records the analysis read as forced rank 12 of the sweep, not the primary, expects and observes 1501 participants with the primary's cells and 96 / 48 / 48 / 12 rows in the four tables, and its deviation list is empty

#### Scenario: Another rank read
- **WHEN** the step reads `results/motco_rank_sensitivity/rank_04`
- **THEN** only the rank-independent keys are expected, and a finding says that the sweep's predeclared diagnostic is its top rank's

#### Scenario: Primary components reproduced
- **WHEN** the top rank's diagnostic is compared with the committed primary diagnostic
- **THEN** the rows of `axis_correlations.csv` for components `pls_0` to `pls_7` and every row of `block_pcs.csv` are equal to the primary's

### Requirement: Reading rules of the rank sweep read
On a forced rank of the sweep `diagnostics.md` SHALL name the sweep and the rank, state that its components up to the primary's rank are the primary's, call each flagged row a finding about the measurement space at that rank, and print `RANK_SENSITIVITY_READING_RULES` after `READING_RULES`. The diagnostic's outputs on the primary, the latent arm, the export variants and the CN / LMCI / AD arm SHALL keep their bytes.

#### Scenario: Top rank read
- **WHEN** the analysis read is `results/motco_rank_sensitivity/rank_12/` with the primary export
- **THEN** `diagnostics.md` names forced rank 12 of the rank sweep, states that `pls_0` to `pls_7` are the primary's components, calls each flagged row a finding about the measurement space at rank 12, prints `RANK_SENSITIVITY_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Other reads unchanged
- **WHEN** the diagnostic runs pinned on the primary, the latent arm, an export variant or the CN / LMCI / AD arm after this change
- **THEN** its four CSVs and `diagnostics.md` have the sha256 the committed diagnostics manifest of that read records

## MODIFIED Requirements

### Requirement: Labels are read but feed no choice
The diagnostic reads sex and stage. Its outputs SHALL NOT be an input of `export`, `analyze`, any sensitivity arm, any export variant or the rank sweep, and the documentation SHALL state that variants, arms and the ladder are predeclared in a change proposal, never derived from a diagnostic value.

#### Scenario: No downstream read
- **WHEN** any `export`, `analyze`, `latent-sensitivity`, `export-sensitivity`, `stage-sensitivity` or `rank-sensitivity` command runs
- **THEN** it reads nothing under any diagnostics directory
