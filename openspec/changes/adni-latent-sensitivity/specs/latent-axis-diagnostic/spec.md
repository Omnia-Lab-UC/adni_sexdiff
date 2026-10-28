# Spec Delta

## MODIFIED Requirements

### Requirement: Reading rules carried
`diagnostics.md` SHALL print `READING_RULES` verbatim and SHALL state that an axis correlated with a variable is a finding about the measurement space of the analysis read, not a reinterpretation of its statistics or p-values, that the flag is a reporting threshold and not an adoption rule, and that the primary analysis stays primary. On an arm it SHALL name the arm and its latent adjustment and print `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`.

#### Scenario: Run axis found
- **WHEN** `pls_0` is flagged against `phase`
- **THEN** `diagnostics.md` lists the row first, names it a measurement-space finding, and does not restate `delta`, `angle` or `shape` as different

#### Scenario: Arm read
- **WHEN** the analysis read is `results/motco_latent_sensitivity/analysis/`, whose manifest records latent adjustment `stage`
- **THEN** `diagnostics.md` names it the `stage`-conditioned sensitivity arm, calls each flagged row a finding about the arm's measurement space, prints `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Primary output unchanged
- **WHEN** the diagnostic runs pinned on the primary analysis after this change
- **THEN** its four CSVs and `diagnostics.md` have the sha256 the committed diagnostics manifest records
