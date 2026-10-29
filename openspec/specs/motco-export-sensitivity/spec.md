# motco-export-sensitivity Specification

## Purpose
Defines the `export-sensitivity` step: predeclared variants of the MOTCO export that change only how the p180 assay run is handled (a NIST SRM 1950 bridge between the runs, per-run standardization), each exported, analysed at the primary's settings and compared with the primary, which stays primary.

## Requirements

### Requirement: Predeclared variant registry
The step SHALL run only the variants of the registry `EXPORT_VARIANTS`, a constant decided by a change proposal before any run: `nist_bridge` and `per_run_standardized`. A variant SHALL be selected by name (`--variant`, or `all`); no flag SHALL set or change a variant's settings, the bridge rule or any analysis setting.

#### Scenario: Unknown variant
- **WHEN** `export-sensitivity --variant raw_scale` runs and `raw_scale` is not in the registry
- **THEN** the command is rejected naming the registered variants, and nothing is read or written

#### Scenario: All variants
- **WHEN** `export-sensitivity --variant all` runs
- **THEN** each registered variant runs in registry order, each into its own directory

### Requirement: Inputs are kept outputs and the QC archives
A variant SHALL read only the outputs of `clean` (`p180/P180.csv`, `p180/p180_runs.csv`, `nmr/NMR.csv`, both `clean_manifest.json`), of `cohort` (`cohort.csv`, `cohort_manifest.json`), the primary export (`results/motco_input/`) and the primary analysis (`result.json`, `analysis_manifest.json`). `nist_bridge` SHALL also read the two QC archives of the data root. The step SHALL NOT read any diagnostics output.

#### Scenario: Per-run variant without a data root
- **WHEN** `export-sensitivity --variant per_run_standardized` runs on a machine whose data root lacks the archives
- **THEN** it completes, having read no data-root file

### Requirement: Inputs are checked against their manifests
Before anything is written, every cleaned, cohort and primary export file SHALL hash to its manifest's record, and the cohort manifest's recorded clean hashes SHALL equal the clean manifests'. A mismatch SHALL stop the step naming the file, both hashes and the step to rerun.

#### Scenario: Cleaned table altered
- **WHEN** `P180.csv` hashes to a value other than the one `clean_manifest.json` records
- **THEN** the step stops naming `P180.csv`, both hashes and the `clean` command, and writes nothing

### Requirement: The primary analysis is a checked reference
The primary analysis manifest SHALL record the primary export files now on disk, no latent adjustment, the installed MOTCO version, `ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS`. A mismatch SHALL stop the step before anything is written, naming the file or setting, both values and the step to rerun.

#### Scenario: Primary export regenerated after the analysis
- **WHEN** `results/motco_input/p180.csv` hashes to a value other than the one `analysis_manifest.json` records
- **THEN** the step stops naming `p180.csv`, both hashes and the `analyze` command, and writes nothing

#### Scenario: Primary is an arm
- **WHEN** the analysis manifest read as the primary records latent adjustment `stage`
- **THEN** the step stops naming the setting and writes nothing

### Requirement: QC archives are read in place
`nist_bridge` SHALL require `ADMC_supplement.zip` and `ADMCDUKEP180SUPP_20170410.zip` at the top level of the data root, hash each through its symlink as every raw input is hashed, and read the four QC workbooks inside them without extracting anything. An absent archive SHALL stop `nist_bridge` before any output directory is created.

#### Scenario: Archive symlink missing
- **WHEN** the data root has no top-level `ADMCDUKEP180SUPP_20170410.zip`
- **THEN** `nist_bridge` stops naming that file before any output directory is created, and `per_run_standardized` is unaffected

### Requirement: QC hashes are compared with the predeclared ones
The variant manifest SHALL record each archive's name, symlink target, size and sha256 beside `RAW_INPUT_SHA256`, and each workbook's member name and sha256 beside its predeclared hash. A hash that differs SHALL be a finding, never a stop.

#### Scenario: Fresh download
- **WHEN** `ADMC_supplement.zip` hashes to a value not in `RAW_INPUT_SHA256`
- **THEN** the manifest records both hashes and a finding says the predeclared counts hold for the recorded bytes only

### Requirement: Valid NIST replicates
A NIST replicate SHALL be a row labelled `NIST SRM 1950` of a workbook's `NIST SRM 1950 Data` sheet. A replicate's cell SHALL be valid when it is a positive number whose status, where the workbook has a status column, is not `ISTD Out of Range`. Text cells (`< LOD`, `No Interception`) SHALL be missing.

#### Scenario: ISTD-flagged cells
- **WHEN** 17 of C0's 24 ADNI-GO/2 cells carry the status `ISTD Out of Range`
- **THEN** those cells are not valid and C0 has 7 of 24 valid replicates in ADNI-GO/2

### Requirement: Bridge inclusion and factor
A metabolite SHALL be bridged when at least half its replicates are valid in each run. Its factor `b` SHALL be the mean log2 of its valid ADNI-1 replicates minus the mean log2 of its valid ADNI-GO/2 replicates, with no plate correction. A metabolite not bridged SHALL have factor 1.

#### Scenario: Metabolite below LOD in most ADNI-GO/2 replicates
- **WHEN** spermidine has 1 valid replicate of 24 in ADNI-GO/2
- **THEN** it is not bridged and its factor is 1

### Requirement: Metabolite names are matched within kit
Each exported p180 metabolite SHALL be matched to a NIST column with case and punctuation dropped, within the kit whose sheet holds it. An exported metabolite with no match SHALL be a finding and SHALL keep factor 1.

#### Scenario: Renamed column
- **WHEN** an exported metabolite has no matching column in either kit's NIST sheet
- **THEN** a finding names it and its factor is 1

### Requirement: The bridge reads reference material only
The bridge SHALL be computed from the NIST rows alone and SHALL read no participant row, no label and no covariate. `bridge/nist_bridge.csv` SHALL hold one row per exported p180 metabolite with its kit, replicates and valid replicates per run, ISTD flags, run means and plate-clustered SEs, `b` and whether it is bridged.

#### Scenario: Bridge table
- **WHEN** `nist_bridge` runs
- **THEN** `bridge/nist_bridge.csv` has 133 rows, holds no participant value, and is committed as aggregate

### Requirement: NIST bridge variant export
Under `nist_bridge`, every cleaned p180 concentration of a participant whose run in `p180_runs.csv` is `ADNI2GO` SHALL be multiplied by 2^b of its metabolite before the floors are computed, and `EXPORT_FEATURE_RULE` SHALL then apply unchanged, its floors recomputed over the exported participants.

#### Scenario: Run label
- **WHEN** a participant's run in `p180_runs.csv` is `ADNI2GO`
- **THEN** each of its bridged p180 concentrations is multiplied by its metabolite's 2^b before the floor, and the ADNI-1 rows are not changed

### Requirement: Per-run standardized variant export
Under `per_run_standardized`, the p180 values on the scale of `EXPORT_FEATURE_RULE` (pooled floors) SHALL be centred and divided by their population SD within each run of `p180_runs.csv`.

#### Scenario: Standardized block
- **WHEN** `per_run_standardized` is exported
- **THEN** every p180 metabolite has mean 0 and population SD 1 within each run

### Requirement: Unchanged files equal the primary's
A variant export SHALL keep the primary's participants, order, block membership, NMR block, metadata and covariates, and its `nmr.csv`, `metadata.csv` and `covariates.csv` SHALL hash to the primary export manifest's records. A difference SHALL be a finding.

#### Scenario: Unchanged files
- **WHEN** the `nist_bridge` export is written
- **THEN** its `nmr.csv`, `metadata.csv` and `covariates.csv` have the sha256 the primary export manifest records

### Requirement: Variant values are label-blind
Neither variant SHALL read sex, stage or a covariate to compute a value. A participant whose run differs from its `phase` SHALL be a finding.

#### Scenario: Labels permuted
- **WHEN** sex and stage are permuted in `cohort.csv` and a variant export is rerun
- **THEN** its `p180.csv` and `nmr.csv` are byte-identical to the unpermuted run's

### Requirement: Primary export unchanged
`export` SHALL keep writing the primary export under the code path it shares with the variants. On a data machine, a pinned `export` after this change SHALL write files with the sha256 the committed export manifest records.

#### Scenario: Primary rerun
- **WHEN** `export` runs pinned into a scratch directory on the committed clean and cohort outputs after this change
- **THEN** every output hash equals the committed `manifest.json`'s

### Requirement: Variant analysis uses the primary's settings
A variant analysis SHALL be one `analyze_trajectories` call on the variant export with every setting of the primary analysis (`ANALYSIS_*`, `ANALYSIS_LATENT_ADJUSTMENT`, MOTCO's defaults, the covariates and their codings), through the code path `analyze` uses.

#### Scenario: Settings recorded
- **WHEN** a variant analysis finishes
- **THEN** its manifest records the same constant names and values as the primary's

### Requirement: Variant analysis records its provenance
The variant analysis manifest SHALL record step `export-sensitivity`, the variant by name, the primary analysis as its reference (the sha256 of its `result.json` and manifest) and the variant export's files as its inputs.

#### Scenario: Reference recorded
- **WHEN** a variant analysis finishes
- **THEN** its manifest names the variant and records the primary's two hashes under its reference

### Requirement: Reported variant runs
A reported variant run SHALL use `n_jobs = 1` and pinned numerics. Another `n_jobs` or an unpinned run SHALL be a finding, and its outputs are not reported or committed.

#### Scenario: Parallel run
- **WHEN** `export-sensitivity --n-jobs 4` runs
- **THEN** the analysis manifest records a finding that the run is not reported

### Requirement: Output layout mirrors the primary pipeline
Each variant SHALL write `results/motco_export_sensitivity/<variant>/` with `motco_input/` laid out as the primary export, `analysis/` laid out as the primary analysis, `comparison/` (`export_sensitivity.csv`, `export_sensitivity.md`, `export_sensitivity_manifest.json`) and, for `nist_bridge`, `bridge/nist_bridge.csv`. `axis-diagnostics` SHALL read `motco_input/` and `analysis/` unchanged.

#### Scenario: Diagnostics on a variant
- **WHEN** `axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir results/motco_export_sensitivity/nist_bridge/diagnostics` runs
- **THEN** it passes its chain checks and writes its six files

### Requirement: Variant directories are complete or absent
Each subdirectory a variant writes SHALL be staged as `.tmp` and the set renamed together when complete. An existing variant SHALL stop the step unless `--force`; with `--force`, an existing `diagnostics/` SHALL be kept and recorded as stale in a finding.

#### Scenario: Interrupted run
- **WHEN** a variant run fails during the analysis
- **THEN** no `analysis/` or `comparison/` of that variant exists, only `.tmp` directories that the next run replaces

#### Scenario: Rerun with diagnostics present
- **WHEN** `--force` replaces a variant whose `diagnostics/` exists
- **THEN** a finding says the diagnostics are stale until `axis-diagnostics` is rerun

### Requirement: Participant-level outputs are ignored before they exist
The variant export's CSVs SHALL be matched by `results/motco_export_sensitivity/*/motco_input/*.csv` in `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` before the first variant run. Every other output SHALL be aggregate, and no output, message or manifest SHALL hold a participant identifier.

#### Scenario: Ignore check
- **WHEN** `git check-ignore` runs on a variant's `motco_input/p180.csv`, `motco_input/features_p180.csv` and `analysis/latent_scores.csv`
- **THEN** all three are ignored, and `bridge/nist_bridge.csv`, `motco_input/manifest.json` and `comparison/export_sensitivity.md` are not

### Requirement: The primary is never modified
The step SHALL NOT write under `results/motco_input/`, `results/motco_analysis/`, `results/motco_diagnostics/` or `results/motco_latent_sensitivity/`, and SHALL NOT rerun the primary analysis.

#### Scenario: Primary untouched
- **WHEN** `export-sensitivity --variant all` finishes
- **THEN** every primary file hashes as before

### Requirement: Comparison table generated from the records
`export_sensitivity.csv` SHALL hold the primary row then the variant row, each with the selected rank and mode, `cv_mean_auroc`, CV repeats completed, the eigengap and, per statistic, the observed value, p, rejection under `ANALYSIS_REJECTION_RULE` and the null mean, SD and q95, every value read from the two analysis records. No statistic SHALL be computed in the comparison.

#### Scenario: Values traced
- **WHEN** the comparison is written
- **THEN** every value in `export_sensitivity.csv` equals the field it is read from in one of the two records

### Requirement: Comparison summary
`export_sensitivity.md` SHALL print the table with a status per statistic (`same`, or `differs (run-handling dependence)`), the primary's status named the result, the p180 and NMR run offsets from both export manifests, for `nist_bridge` the bridge summary (bridged per kit, the unbridged metabolites, the quantiles of `b`), and `READING_RULES` then `EXPORT_VARIANT_READING_RULES` verbatim.

#### Scenario: Status differs
- **WHEN** `angle` is not rejected in the primary and rejected in `per_run_standardized`
- **THEN** its status reads `differs (run-handling dependence)`, the primary's status is named the result, and a finding records it

### Requirement: Predeclared counts
Each variant manifest SHALL record `EXPORT_VARIANT_EXPECTED_COUNTS` beside the observed counts: those of `EXPORT_EXPECTED_COUNTS`, for `nist_bridge` the bridged metabolites per kit and the unbridged count, the p180 floors not positive and non-finite cells, the p180 metabolites with phase |d| above 0.5 and 1, the unchanged files' hashes, and every key of `ANALYSIS_EXPECTED_COUNTS`. A deviation SHALL be a finding, never a stop.

#### Scenario: Count deviation
- **WHEN** the bridge rule bridges 125 metabolites against the predeclared 126
- **THEN** the manifest records both values and a finding, and the run completes

### Requirement: Findings
Findings SHALL record every finding condition of `export` and `analyze`, a rank that differs from the primary's, a statistic whose status differs, a QC archive or workbook hash that differs from its predeclared value, an unmatched metabolite, a run that differs from `phase`, and stale diagnostics. A finding SHALL name counts, settings and files, never a participant.

#### Scenario: Rank differs
- **WHEN** the variant's CV-selected rank is 6 and the primary's is 8
- **THEN** a finding records both, reported beside `angle` and not ranked

### Requirement: Reproducible run
Two pinned runs of a variant on the same inputs SHALL write byte-identical CSVs, `summary.md`, `export_sensitivity.md` and bridge table, a `result.json` equal apart from MOTCO's runtime, and manifests that differ only in time, revision, runtime and the hashes of the files that carry them; the bridge table SHALL depend only on the four workbooks.

#### Scenario: Rerun
- **WHEN** `export-sensitivity --variant nist_bridge --force` runs twice pinned, with the same `diagnostics/` state
- **THEN** every CSV, `summary.md`, `export_sensitivity.md` and the bridge table hash identically, `result.json` differs only in MOTCO's runtime, and the manifests only in their timestamps, revision, runtime and the hashes of the manifests and `result.json`

### Requirement: Reading rules bind every reader of a variant
`EXPORT_VARIANT_READING_RULES` SHALL be printed verbatim after `READING_RULES` in each variant's `summary.md`, in `export_sensitivity.md`, in a variant's `diagnostics.md` and in every report that quotes a variant. No variant value SHALL change a constant, select a metabolite or covariate, rerun the primary or define a new variant.

#### Scenario: Variant summary
- **WHEN** a variant's `summary.md` is written
- **THEN** it names the variant, states that the primary stays primary, and prints both sets of rules
