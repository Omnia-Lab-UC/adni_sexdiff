# Spec Delta

## MODIFIED Requirements

### Requirement: Cohort table is checked and chained to the export
`cohort.csv` SHALL hash to the value `cohort_manifest.json` records, `cohort_manifest.json` SHALL hash to the value the export manifest records for it, and the rows with both platform flags SHALL be the exported participants in export order. On the CN / LMCI / AD arm's export (a manifest that records the arm) the rows compared SHALL be the both-flag rows whose `dx_bl` the arm keeps. A mismatch SHALL stop the step before anything is written, naming the file and the step to rerun.

#### Scenario: Cohort rerun after the export
- **WHEN** `cohort_manifest.json` hashes to a value other than the one the export manifest records
- **THEN** the step stops naming `cohort_manifest.json` and the `export` command, and writes nothing

#### Scenario: Arm export read
- **WHEN** `--input-dir results/motco_stage_sensitivity/motco_input` is read, whose manifest records the arm `cn_lmci_ad`
- **THEN** the 1130 both-flag rows of `cohort.csv` whose `dx_bl` is CN, LMCI or AD are compared with the exported participants in order, and the check passes

#### Scenario: Arm export with another cohort
- **WHEN** the arm's manifest records a cohort manifest hash other than the one now on disk
- **THEN** the step stops naming `cohort_manifest.json`, both hashes and the `stage-sensitivity` command, and writes nothing

### Requirement: Manifest records provenance, definitions and predeclared counts
`diagnostics_manifest.json` SHALL record the software versions, the git revision, every input with its sha256 and the chain checks, the analysis read (manifest hash, latent adjustment, `n_jobs`, selected rank, whether it is the primary, the export variant or stage arm it belongs to), the variables with sources, the threshold, the conditioning columns, the definition of every statistic, the observed counts beside `DIAGNOSTICS_EXPECTED_COUNTS` with the deviations, output hashes and findings. On the CN / LMCI / AD arm the expected participants and cells SHALL be the arm's predeclared ones.

#### Scenario: Counts match on the primary
- **WHEN** the step runs on the committed export, cohort and primary analysis
- **THEN** the manifest records 1501 participants, 8 components, 8 variables, 6 conditioning columns, 64 / 48 / 32 / 8 rows in the four tables, and an empty deviation list

#### Scenario: A count deviates
- **WHEN** the export holds 1500 participants
- **THEN** the manifest's deviations name `participants`, expected 1501 and observed 1500, and the step still completes

#### Scenario: Counts match on the arm
- **WHEN** the step reads the arm's export and analysis
- **THEN** the manifest records the analysis read as the stage arm `cn_lmci_ad`, not the primary, expects and observes 1130 participants with the arm's six cells, and its deviation list is empty

### Requirement: Labels are read but feed no choice
The diagnostic reads sex and stage. Its outputs SHALL NOT be an input of `export`, `analyze`, any sensitivity arm or any export variant, and the documentation SHALL state that variants and arms are predeclared in a change proposal, never derived from a diagnostic value.

#### Scenario: No downstream read
- **WHEN** any `export`, `analyze`, `latent-sensitivity`, `export-sensitivity` or `stage-sensitivity` command runs
- **THEN** it reads nothing under any diagnostics directory

### Requirement: Reading rules of a sensitivity read
`diagnostics.md` SHALL name the sensitivity it reads and carry its reading rules after `READING_RULES`. On an arm it SHALL name the arm and its latent adjustment and print `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`. On an export variant (an analysis manifest that records step `export-sensitivity` and a variant name) it SHALL name the variant and print `EXPORT_VARIANT_READING_RULES` after `READING_RULES`. On the CN / LMCI / AD arm (an analysis manifest that records step `stage-sensitivity`) it SHALL name the arm and print `STAGE_SENSITIVITY_READING_RULES` after `READING_RULES`.

#### Scenario: Arm read
- **WHEN** the analysis read is `results/motco_latent_sensitivity/analysis/`, whose manifest records latent adjustment `stage`
- **THEN** `diagnostics.md` names it the `stage`-conditioned sensitivity arm, calls each flagged row a finding about the arm's measurement space, prints `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Export variant read
- **WHEN** the analysis read is `results/motco_export_sensitivity/nist_bridge/analysis/` with its own export directory
- **THEN** `diagnostics.md` names the export variant `nist_bridge`, calls each flagged row a finding about the variant's measurement space, prints `EXPORT_VARIANT_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Stage arm read
- **WHEN** the analysis read is `results/motco_stage_sensitivity/analysis/` with the arm's export directory
- **THEN** `diagnostics.md` names the CN / LMCI / AD arm `cn_lmci_ad`, calls each flagged row a finding about the arm's measurement space, prints `STAGE_SENSITIVITY_READING_RULES` after `READING_RULES`, and states that the primary analysis stays primary

#### Scenario: Other reads unchanged
- **WHEN** the diagnostic runs pinned on the primary, the latent arm or an export variant after this change
- **THEN** its four CSVs and `diagnostics.md` have the sha256 the committed diagnostics manifest of that read records
