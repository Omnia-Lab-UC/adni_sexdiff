# AGENTS.md

Guidance for AI coding agents working in this repository. This file is the single
source of truth; tool-specific files (e.g. `CLAUDE.md`) only reference it.

## Project

Python package + CLI (`adni-sexdiff`) for the sex × stage (CN / MCI / AD)
trajectory comparison on ADNI serum metabolomics with MOTCO: the Biocrates
p180 and Nightingale NMR platforms, one MOTCO block each. It is the first
MOTCO application at a well-powered design (n ≈ 1,300). Later ADNI layers
(lipidomics, proteomics, methylation) may be added as separate blocks, each
by its own change proposal. The repository is modelled on `../sead_sexdiff`
(the SEA-AD astrocyte case study); its conventions apply here unless this
file says otherwise.

Status (2026-10-31): `clean` (change `adni-metabolomics-clean`), `cohort`
(change `adni-cohort`), `export` (change `adni-export`), `analyze`
(change `adni-analyze`), `axis-diagnostics` (change
`adni-axis-diagnostics`) and `report` (change `adni-report`) are
implemented, and so is the sensitivity step `latent-sensitivity` (change
`adni-latent-sensitivity`: the predeclared `stage`-conditioned
latent-adjustment arm, read beside the primary and never replacing it)
and the sensitivity step `export-sensitivity` (change `adni-nist-bridge`:
the predeclared export variants of the p180 run handling, a NIST SRM 1950
bridge of the runs and per-run standardization, each read beside the
primary and never replacing it; the report covers them since change
`adni-report-variants`; a third variant, `nmr_all_columns`, change
`adni-nmr-all-columns`: every cleaned NMR column in the block, the 80
derived ones among them, run by the same step and read beside the primary
under its own rules; the report covers it since change
`adni-report-nmr-all-columns`, whose pin `REPORT_EXPORT_VARIANTS` holds all
three variants, each group of a rule set in its own tables) and the
sensitivity step `stage-sensitivity`
(change `adni-stage-sensitivity`: the predeclared CN / LMCI / AD arm, the
primary export's rows of the participants whose `DX.bl` is CN, LMCI or
AD, read beside the primary and never replacing it; the report covers it
since change `adni-report-stage-arm`) and the sensitivity step
`rank-sensitivity` (change `adni-rank-sensitivity`: the predeclared
forced-rank ladder, the primary's analysis at the forced ranks 2, 3, 4, 6,
9 and 12 after an anchor run at the primary's rank reproduces the primary,
read beside the primary and never replacing it; the report covers it
since change `adni-report-rank-sweep`).
Every step but `report` runs on a data machine; `report` reads committed aggregate
files only and runs on any clone; the reports are committed under
`reports/`; since `adni-report-nmr-all-columns` a report covers the
primary, the latent arm, the three export variants (the two p180 variants
under `EXPORT_VARIANT_READING_RULES`, `nmr_all_columns` under
`NMR_MEMBERSHIP_READING_RULES`), the CN / LMCI / AD arm and the rank sweep
(the reports of 2026-10-28, 2026-10-29, 2026-10-30 and 2026-10-31, of
earlier layouts, cover fewer). The cluster copy and clone do not exist yet. A data machine is
any of the user's machines whose
local participant-level files under `results/` (the export CSVs,
`cohort.csv`, the primary's `latent_scores.csv` and
`analysis_metadata.csv`) hash to the values the committed manifests
record; the hash checks pick it and no machine is named. Any machine with
a data root becomes one by a pinned rebuild from it (`clean` → `cohort` →
`export` → `analyze` into a scratch directory), a hash check of every
output the committed manifests record, and copying the participant-level
files into the gitignored paths under `results/`. The manifests written
before `adni-portable-numerics` record no machine, but their outputs
reproduce pinned on any machine. Decided scientific constants:
`CLEAN_OPTIONS`, `COHORT_RULE`, `STAGE_RULE`, `ANALYSIS_COVARIATES`,
`EXPORT_FEATURE_RULE`, the analysis settings (`ANALYSIS_PERMUTATIONS`,
`ANALYSIS_SEED`, `ANALYSIS_ALPHA` with `ANALYSIS_REJECTION_RULE`,
`ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`), `READING_RULES`, the
diagnostic constants (`DIAGNOSTIC_VARIABLES`,
`DIAGNOSTIC_CORRELATION_THRESHOLD`) and the sensitivity constants
(`LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`,
`LATENT_SENSITIVITY_READING_RULES`; `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE`,
`EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES`;
`STAGE_SENSITIVITY_ARM`, `STAGE_SENSITIVITY_READING_RULES`;
`RANK_SENSITIVITY_LADDER`, `RANK_SENSITIVITY_READING_RULES`); every
constant the six steps and the four sensitivity steps need is decided (see
"Flag and ask"). Each step is
implemented by its own OpenSpec change, in order.

1. `clean` – metabo_adni per platform (`--platform {p180,nmr,all}`): the
   pinned release's QC functions called in-process in the order of its
   `__main__.main` (the console script `clean_files`; metabo_adni has no
   library entry point), with `CLEAN_OPTIONS` (QC at the default cutoffs,
   `--merge`, no transform), in a working copy (`<platform>.tmp/work/`)
   because metabo_adni changes into the data directory and writes its
   output there. Its printed output (it lists `RID`s) is captured to
   `logs/metabo_adni.log`, never shown. Writes `results/cleaned/<platform>/`:
   `P180.csv` / `NMR.csv` (the merged table under the name metabo_adni
   gives it; participant × metabolite, keyed by `RID`; participant-level),
   for p180 `p180_runs.csv` (`RID`, `run` ∈ {`ADNI1`, `ADNI2GO`};
   participant-level), the log (participant-level) and `clean_manifest.json`
   (versions, options and `cli_equivalent`, input hashes and known repairs,
   raw inventory, participants × metabolites after each metabo_adni step,
   imputed points, value summary, runs, output hashes, the predeclared
   `CLEAN_EXPECTED_COUNTS` beside the observed ones, findings, upstream
   behaviours; aggregate, the one file under `results/cleaned/` that is
   committed and synced).
2. `cohort` – from `results/cleaned/` (`P180.csv`, `p180_runs.csv`,
   `NMR.csv`, each checked against its `clean_manifest.json` hash) and, in
   the data root, the ADNIMERGE freeze, the medication table and the visit
   columns of the raw ADNI-GO/2 p180 and NMR files: each participant's
   ADNIMERGE `bl` row, the platform sets (every raw sample at `bl`, a `bl`
   row; `COHORT_RULE`) and their intersection, sex (`PTGENDER`), the merged
   stage (`STAGE_LABELS` = CN / MCI / AD from `DX.bl` by `STAGE_RULE`), the
   covariates (`ANALYSIS_COVARIATES`; nothing imputed). A value outside the
   rules or a missing covariate stops it before anything is written, naming
   the column and a count. Writes `results/cohort/`: `cohort.csv` (one row
   per participant of either platform set, the union, with a flag per
   platform; the intersection is the rows with both flags;
   participant-level), `stage_counts.csv` (sex × stage per platform set and
   for the intersection, plus the intersection's sex × stage × `DX.bl` ×
   phase cells; aggregate, the only committed table) and
   `cohort_manifest.json` (input hashes, the rules as applied, cascade,
   stage-source agreement, phase against the p180 run, descriptives, the
   predeclared `COHORT_EXPECTED_COUNTS` beside the observed ones, output
   hashes, findings; aggregate, committed and synced).
3. `export` – from `results/cleaned/` (`P180.csv`, `NMR.csv`, each checked
   against its `clean_manifest.json` hash) and `results/cohort/`
   (`cohort.csv`, checked against `cohort_manifest.json`, whose recorded
   clean hashes must equal the clean manifests', the chain check; a
   mismatch stops it naming the file and `cohort`) only, no data-root
   file: the rows of `cohort.csv` with both platform flags in file order
   (n = 1501), the MOTCO blocks under `EXPORT_FEATURE_RULE` (membership by
   family, `log2(x + floor)` with the per-metabolite 5 % quantile floor),
   covariates exported, not applied. Stops before writing on an absent
   column, a duplicated `rid`, a value outside `GROUP_VALUES` or
   `STAGE_LABELS`, a missing covariate, a participant absent from a
   cleaned table, a non-positive floor or a non-finite cell. Writes
   `results/motco_input/`: `p180.csv`, `nmr.csv` (`rid`, then the kept
   metabolites under their cleaned names, on the rule's scale),
   `metadata.csv` (`rid`, `sex`, `stage`), `covariates.csv` (`rid` plus
   `age`, `education`, `apoe4`, `phase`, `statin`, copied unchanged; all
   four participant-level), `features_<platform>.csv` (one row per cleaned
   column: family, status `kept` / `derived`, zero cells, median, floor,
   floor over median, skew raw and transformed, largest |z| transformed,
   phase `d`; aggregate per feature, gitignored with the other CSVs,
   regenerable) and `manifest.json` (input hashes and the chain check, the
   rule as applied, block order and columns, the covariate codings copied
   from the cohort manifest, `covariates_applied` false, counts: n per
   sex × stage cell, features per status and family, zero cells, floors not
   positive, non-finite cells, block shares, per block the shape counts,
   the spectrum and the phase offset; the predeclared
   `EXPORT_EXPECTED_COUNTS` beside the observed ones, output hashes,
   findings; aggregate, the only committed file). No step before `analyze`
   uses sex or stage to select features; the blocks and feature tables are
   byte-identical under permuted labels.
4. `analyze` – from `results/motco_input/` only (`p180.csv`, `nmr.csv`,
   `metadata.csv`, `covariates.csv`, each checked against the sha256 in
   `manifest.json`; the manifest's block columns, covariate codings and
   counts): one `motco.analysis.analyze_trajectories` call (never
   assembled from `motco plsr` + `motco de`), after two gates that run
   before any input is read (MOTCO ≥ `ANALYSIS_MOTCO_MIN_VERSION` 0.10.0,
   and MOTCO's default rank floor equal to `ANALYSIS_RANK_FLOOR`), on the
   blocks in `EXPORT_BLOCKS` order (transform `identity`), group `sex` in
   `GROUP_VALUES` order, stage `stage` in CN / MCI / AD order, the
   `ANALYSIS_COVARIATES` additively with `ANALYSIS_CATEGORICAL_COVARIATES`
   declared categorical (six design columns, LS-means at the pooled
   covariate mean), missing policy `error`, and
   `TrajectoryAnalysisParams(permutations=ANALYSIS_PERMUTATIONS,
   seed=ANALYSIS_SEED, n_jobs, min_components=ANALYSIS_RANK_FLOOR,
   covariate_latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT)` and nothing
   else; MOTCO's other defaults are not overridden and are read back from
   the record. The four tables must carry the same `rid` column in the
   same order; a value outside the rules, a missing covariate value or a
   missing block cell stops it before anything is written, naming the file
   or column and a count. The metadata table the model sees is
   `analysis_metadata.csv` parsed back as `motco analyze --metadata`
   parses it, so the manifest's `cli_equivalent` reproduces the run with
   MOTCO's CLI. Writes `results/motco_analysis/`: MOTCO's `result.json`,
   `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, plus
   `analysis_metadata.csv` (`rid`, `sex`, `stage`, the five covariates),
   `analysis_manifest.json` (versions with MOTCO and scikit-learn, git
   revision, inputs with observed and recorded hashes and the export
   manifest's hash and revision, every setting by constant name, `n_jobs`,
   the covariate block, the MOTCO defaults used, the latent adjustment
   with the predeclared arm, `cli_equivalent`, counts, the predeclared
   `ANALYSIS_EXPECTED_COUNTS` beside the observed ones with deviations,
   output hashes with a participant-level flag, findings) and `summary.md`
   (generated from the record: the statistics with p-values, rejection
   under `ANALYSIS_REJECTION_RULE` and null summaries, the CV-selected
   rank, floor and eigengap beside `angle`, the cell sizes, the latent and
   covariate blocks, the export context, `READING_RULES` verbatim).
   `latent_scores.csv` and `analysis_metadata.csv` are participant-level;
   the other five files are aggregate and committed. Findings, never
   stops: a count deviation, `n_jobs ≠ 1` (the run is not reported), a
   CV-selected rank equal to the floor, fewer CV repeats than requested, a
   non-finite statistic or p-value, a moved MOTCO default. On the cluster
   it runs through `scripts/analyze.sbatch`.
5. `axis-diagnostics` – from `results/motco_input/` (the four tables, each
   checked against `manifest.json`; the manifest's block columns, covariate
   codings and recorded phase offset), `results/motco_analysis/`
   (`result.json`, `latent_scores.csv`, `stage_means.csv`,
   `pls_loadings.csv`, `analysis_manifest.json`; the analysis manifest's
   recorded input hashes and export-manifest hash checked against the
   export files now, the `pls_` column counts against the record's rank,
   the stage-mean rows, the loadings' features and the `rid` set of the
   scores) and `results/cohort/` (`cohort.csv` against
   `cohort_manifest.json`, whose hash must equal the export manifest's
   record; the both-flag rows must be the exported participants in order)
   only, nothing else; a mismatch stops it before anything is written,
   naming the file, both hashes or both counts and the step to rerun. For
   every latent component: Spearman and partial Spearman correlations
   (given the record's six design columns,
   `DIAGNOSTIC_CONDITIONING_COLUMNS`, built from `covariates.csv` with the
   export's codings and checked by name and column mean against the
   record's `design_columns` and `reference_row`) with the eight
   `DIAGNOSTIC_VARIABLES`, the same for the first `DIAGNOSTIC_N_BLOCK_PCS`
   PCs of each z-scored block (pc1 against `phase` beside the export's
   recorded Pearson value), the geometry shares along each component from
   `stage_means.csv` and the block composition of each component from
   `pls_loadings.csv`; |ρ| at or above `DIAGNOSTIC_CORRELATION_THRESHOLD`
   flagged, raw and partial separately, no p-value. Writes
   `results/motco_diagnostics/` (`axis_correlations.csv`, `block_pcs.csv`,
   `geometry_shares.csv`, `components.csv`, `diagnostics.md` with the
   flagged rows first and `READING_RULES` verbatim,
   `diagnostics_manifest.json` with the twelve input hashes and the chain
   checks, the analysis read with `is_primary`, the variables with sources
   and derivations, the threshold, the conditioning columns, the
   definition of every statistic, the predeclared
   `DIAGNOSTICS_EXPECTED_COUNTS` beside the observed ones with deviations,
   output hashes, findings; every file per component, per block or per
   variable, no `rid`, all committed). Findings, never stops: a count
   deviation, an analysis read with `n_jobs ≠ 1`, an analysis that is not
   the primary (`--analysis-dir` or a recorded latent adjustment: the
   `primary` and `rows` expectations are skipped, the arm path of
   `adni-latent-sensitivity`), a constant variable, the flagged variables
   per component. The sweep read (change `adni-rank-sensitivity`): with
   `--analysis-dir results/motco_rank_sensitivity/rank_<kk>` and the
   primary export, an analysis manifest with step `rank-sensitivity` is a
   forced rank of the rank sweep; the manifest records `is_primary` false
   and `inputs.analysis.rank_sweep` (the forced rank and the primary's
   rank; `null` on every other read); on the top rank (`rank_12`, the
   sweep's predeclared diagnostic) the expected counts are
   `RANK_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]` (the rank-independent
   keys, the read rank 12 `forced` with no latent adjustment and `n_jobs`
   1, rows 96 / 48 / 48 / 12), on another rank the rank-independent keys
   with a finding that the sweep's predeclared diagnostic is the top
   rank's; `diagnostics.md` names the rank sweep and the forced rank,
   states that `pls_0` up to the primary's rank are the primary's
   components (nesting), calls a flagged row a finding about the
   measurement space at that rank and prints
   `RANK_SENSITIVITY_READING_RULES` after `READING_RULES` (sweep rule 7: an
   added component that tracks `phase` is a measurement-space finding,
   never grounds to choose a rank). It reads sex and stage, so it is never
   a filter: its outputs feed no `export`, `analyze` or sensitivity run,
   and no arm, variant or rank is derived from a diagnostic value.
   - Sensitivity step, after `axis-diagnostics` and before `report`:
     `latent-sensitivity` (change `adni-latent-sensitivity`) – from
     `results/motco_input/` (the five files, checked as `analyze` checks
     them), the primary's `results/motco_analysis/result.json` and
     `analysis_manifest.json` (read, never written) and
     `results/cohort/cohort_manifest.json` (its hash and its per-cell
     descriptives; no `cohort.csv`), after the gates of `analyze`: the
     primary manifest must record the export files now on disk and no
     latent adjustment, under the installed MOTCO with `ANALYSIS_SEED` and
     `ANALYSIS_PERMUTATIONS`, and the cohort manifest's hash must equal the
     export manifest's record; a mismatch stops it naming the file or
     setting, both values and the step to rerun. One
     `analyze_trajectories` call through the function `analyze` shares
     (`_run_trajectory_analysis`) at the primary's settings plus
     `covariate_latent_adjustment = "stage"` (`LATENT_SENSITIVITY_ARM`, the
     arm `adni-analyze` predeclared; the five covariates; nothing else).
     MOTCO's rare-level condition is not worked around: a residualization
     design that is not of full rank, on the full sample or in a CV
     training set, stops the step with MOTCO's message and nothing
     written. Writes `results/motco_latent_sensitivity/`: `analysis/` (the
     seven files `analyze` writes, laid out as the primary's so that
     `axis-diagnostics --analysis-dir` reads it unchanged; `result.json`
     carries MOTCO's `latent_adjustment` block, `analysis_manifest.json`
     records `step` `latent-sensitivity`, the arm by constant name, the
     primary as `reference` with its two hashes, the `numerics` block and
     the predeclared `LATENT_SENSITIVITY_EXPECTED_COUNTS` beside the
     observed ones; `summary.md` adds the latent-adjustment section and
     `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`;
     `latent_scores.csv` and `analysis_metadata.csv` participant-level,
     already matched by the `results/**` ignore patterns), `comparison/`
     (`latent_sensitivity.csv`, the primary row then the arm row, every
     value read from the two records; `latent_sensitivity.md`, the
     statistics with a status per statistic, `same` or `differs (basis
     dependence)`, the latent spaces, the arm's latent-adjustment block,
     the covariate roles beside the cohort manifest's per-cell
     descriptives copied value for value, MOTCO's two latent-adjustment
     decisions, the findings and both sets of reading rules;
     `latent_sensitivity_manifest.json`; all aggregate) and never
     `diagnostics/`, which `axis-diagnostics --analysis-dir
     results/motco_latent_sensitivity/analysis --out-dir
     results/motco_latent_sensitivity/diagnostics` writes (its
     `diagnostics.md` names the arm and prints both sets of rules).
     `analysis/` and `comparison/` are staged as `.tmp/` directories and
     renamed together. Findings, never stops: those of `analyze`, an arm
     rank that differs from the primary's, a statistic whose status
     differs (basis dependence), a primary read with `n_jobs ≠ 1`,
     cohort-manifest cells that differ from the record's, a replaced arm
     whose `diagnostics/` exists. The primary stays primary in every output
     and no arm value changes a constant, selects a covariate, reruns the
     primary or defines a variant.
   - Sensitivity step, after `axis-diagnostics` and before `report`:
     `export-sensitivity --variant {nist_bridge,per_run_standardized,nmr_all_columns,all}`
     (changes `adni-nist-bridge` and `adni-nmr-all-columns`) – from
     `results/cleaned/` (`P180.csv`,
     `p180_runs.csv`, `NMR.csv`, each against its `clean_manifest.json`),
     `results/cohort/` (`cohort.csv`, `cohort_manifest.json`), the primary
     export `results/motco_input/` and the primary's `result.json` and
     `analysis_manifest.json` (read, never written) and, for `nist_bridge`
     only, the two QC archives at the top of the data root, read in place;
     no diagnostics output. Gates before anything is written, each naming
     the file or setting, both values and the command to rerun: the
     variant name, the gates of `analyze`, an existing variant without
     `--force`, the clean outputs and the cohort chain, the primary export
     against its manifest and against the clean and cohort files now on
     disk (`_check_primary_export_chain`), the primary analysis as a
     chained reference (`_check_primary_reference`), the archives and their
     four members (`_read_nist_archives`). Per variant of `EXPORT_VARIANTS`
     (registry order for `all`, which stops at the existing-variant gate
     when a variant's outputs exist, so a new variant runs by its name):
     the export through the body `export` shares (`_run_export`, with the
     variant's one hook: `factors`, the ADNI-GO/2 rows multiplied by 2^b of
     `NIST_BRIDGE_RULE` before the floors, or `standardize_by_run`, each
     p180 metabolite standardized within its run on the rule's scale, or
     `membership` (`nmr_all_columns`), every cleaned NMR column kept in
     cleaned order, each on the rule's scale with its own floor, the rule's
     165 columns compared with the primary `nmr.csv`
     (`rule_columns_equal_primary`); the primary's bytes are its gate), the
     analysis through `_run_trajectory_analysis` at the primary's settings,
     and the comparison. Every variant-specific word of the documents (the
     rule set, its citation word, the dependence label and what the variant
     changes) comes from `EXPORT_VARIANT_RULE_SETS` and the variant's block
     (`_variant_words`). Writes `results/motco_export_sensitivity/<variant>/`:
     `bridge/nist_bridge.csv` (`nist_bridge` only; per exported p180
     metabolite the NIST replicates, valid ones, ISTD flags, run means and
     plate-clustered SEs, `b`, `bridged`, `factor_log2`; reference material
     only, aggregate), `motco_input/` (laid out as the primary export; its
     CSVs participant-level, matched by
     `results/motco_export_sensitivity/*/motco_input/*.csv`; `manifest.json`
     with step `export-sensitivity`, the variant, the primary export as
     `reference`, the QC hashes beside the predeclared ones, the bridge's
     hash, summary and factors, for `nmr_all_columns` `derived_kept` and
     `rule_columns_equal_primary`, `EXPORT_VARIANT_EXPECTED_COUNTS` beside
     the observed counts), `analysis/` (the seven files `analyze` writes,
     the primary as `reference`; `summary.md` with an "Export variant"
     section and the variant's rule set after `READING_RULES`) and
     `comparison/` (`export_sensitivity.csv`, the primary row then the
     variant row read from the records; `export_sensitivity.md`, statuses
     `same` / `differs (<dependence>)`, `run-handling dependence` for the
     p180 variants and `feature-membership dependence` for
     `nmr_all_columns`, the run offsets of both exports, the bridge summary
     or the membership, block shares and NMR shape counts, and both sets of
     rules; `export_sensitivity_manifest.json`), the staged subdirectories
     (`bridge/` for `nist_bridge` only) renamed together; never
     `diagnostics/`, which `axis-diagnostics --input-dir
     <variant>/motco_input --analysis-dir <variant>/analysis --out-dir
     <variant>/diagnostics` writes (its `diagnostics.md` names the variant
     and the block it changes and prints both sets of rules; its expected
     counts are the variant's own `diagnostics` counts when its entry holds
     them, `nmr_all_columns` with 245 NMR features). Findings, never stops:
     those of `export` and `analyze`, a QC hash that differs from its
     predeclared value, a metabolite without a NIST column, a run that
     differs from `phase`, an unchanged file that differs from the
     primary's, the rule's NMR columns differing from the primary's, a
     variant rank or status that differs from the primary's (cited under
     the variant's rule set), a primary read with `n_jobs ≠ 1`, stale
     diagnostics. The primary stays primary and no variant value changes a
     constant, selects a metabolite, reruns the primary or adopts a
     variant.
   - Sensitivity step, after `axis-diagnostics` and before `report`:
     `stage-sensitivity` (change `adni-stage-sensitivity`) – from the
     primary export `results/motco_input/` (the five files, checked as
     `analyze` checks them, and its four CSVs read as bytes; no feature
     table), the primary's `result.json` and `analysis_manifest.json`
     (read, never written) and `results/cohort/` (`cohort.csv`, the source
     of `dx_bl`, and `cohort_manifest.json`); no data root, no cleaned
     table, no diagnostics output. Gates before anything is written, each
     naming the file or setting, both values or counts and the command to
     rerun: the gates of `analyze`, an existing arm without `--force`, the
     primary export (and that it records no arm or variant), the primary
     analysis as a chained reference (`_check_primary_reference`), the
     cohort chain (`_check_cohort_chain`: the both-flag rows the exported
     participants in order, with equal sex and stage), a `dx_bl` outside
     `STAGE_RULE`'s map, a kept row whose stage differs from the arm's map.
     The arm `STAGE_SENSITIVITY_ARM` (`cn_lmci_ad`): the exported
     participants whose `dx_bl` is CN, LMCI or AD (SMC and EMCI dropped),
     their rows of the four CSVs copied as bytes from the primary export
     (`_stage_arm_export`: header and kept lines, so every row is the
     primary's and the floors are the primary's; read back equal,
     `rows_equal_primary`), then one `analyze_trajectories` call through
     `_run_trajectory_analysis` at the primary's settings, then the
     comparison. Writes `results/motco_stage_sensitivity/`: `motco_input/`
     (the four CSVs, participant-level, matched by
     `results/motco_stage_sensitivity/motco_input/*.csv`; `manifest.json`
     with step `stage-sensitivity`, `stage_arm`, the primary export as
     `reference` with its feature tables' hashes as the source of the
     floors, the cohort chain, the primary's settings, the counts beside
     `STAGE_SENSITIVITY_EXPECTED_COUNTS["export"]`), `analysis/` (the seven
     files `analyze` writes, the primary as `reference`; `summary.md` with
     an "Arm" section and `STAGE_SENSITIVITY_READING_RULES` after
     `READING_RULES`) and `comparison/` (`stage_sensitivity.csv`, the
     primary row then the arm row read from the records;
     `stage_sensitivity.md`, statuses `same` / `differs (stage-definition
     dependence)`, the cells, runs within stage, covariate levels and run
     offsets of both, and both sets of rules;
     `stage_sensitivity_manifest.json` with the nine inputs), the three
     staged as `.tmp/` and renamed together; never `diagnostics/`, which
     `axis-diagnostics --input-dir <root>/motco_input --analysis-dir
     <root>/analysis --out-dir <root>/diagnostics` writes (its cohort check
     compares the both-flag rows the arm keeps, it expects the arm's
     participants and cells, records `stage_arm`, and its `diagnostics.md`
     names the arm and prints both sets of rules). Findings, never stops:
     those of `analyze`, a count deviation, rows read back that differ
     from the primary's, an arm rank or status that differs from the
     primary's, a primary read with `n_jobs ≠ 1`, stale diagnostics. The
     primary stays primary and no arm value changes a constant,
     `STAGE_RULE` or `COHORT_RULE`, selects a participant, reruns the
     primary or adopts the arm.
   - Sensitivity step, after `axis-diagnostics` and before `report`:
     `rank-sensitivity` (change `adni-rank-sensitivity`) – from the primary
     export `results/motco_input/` (the five files, checked as `analyze`
     checks them) and the primary's `result.json` and
     `analysis_manifest.json` (read, never written); no data root, no
     cohort table, no feature table, no diagnostics output. Gates before
     anything is written, each naming the file or setting, both values and
     the command to rerun: the gates of `analyze`, an existing rank
     directory or `comparison/` without `--force`, the primary export (and
     that it records no arm or variant), the primary analysis as a chained
     reference (`_check_primary_reference`) written by `analyze` with a
     CV-selected rank and its `result.json` equal to its manifest's record,
     then the anchor gate (`_check_anchor`): one forced run at the primary
     record's rank, staged in `anchor.tmp/` through
     `_run_trajectory_analysis`, whose statistics, p-values, null
     summaries, `config_spectrum` and rank must equal the primary's
     `result.json` and whose `latent_scores.csv`, `pls_loadings.csv` and
     `stage_means.csv` must hash to the primary manifest's record (at
     `n_jobs ≠ 1` only what the draws do not change); a difference stops
     it naming the field or file, both values and the numerics state, with
     `anchor.tmp/` kept (ignored); on equality it is removed. The ladder
     `RANK_SENSITIVITY_LADDER` (`forced_rank_ladder`): one
     `analyze_trajectories` call per rank 2, 3, 4, 6, 9 and 12 through
     `_run_trajectory_analysis` at the primary's settings plus
     `forced_components` (the rank fixed, MOTCO's cross-validation
     skipped), then the comparison; before the renames each rank's latent
     scores are compared in memory with the first columns of the top
     rank's and the anchor's (the nesting). Writes
     `results/motco_rank_sensitivity/`: `rank_02/` … `rank_12/` (the seven
     files `analyze` writes, laid out as the primary's; the manifest
     records step `rank-sensitivity`, `settings.forced_components`,
     `rank_sweep` with the ladder by constant name, the forced rank, the
     primary's rank and the anchor, the primary as `reference`, the counts
     beside `RANK_SENSITIVITY_EXPECTED_COUNTS["analysis"][k]`; `summary.md`
     names the forced rank, has a "Rank sweep" section and prints
     `RANK_SENSITIVITY_READING_RULES` after `READING_RULES`;
     `latent_scores.csv` and `analysis_metadata.csv` participant-level,
     already matched by the `results/**` patterns) and `comparison/`
     (`rank_sensitivity.csv`, the primary row then one row per rank read
     from the records; `rank_sensitivity.md`, statuses `same` / `differs
     (rank dependence)`, the status sentences `_rank_status_line`, each
     rank's reading lines, the latent spaces, the anchor and the nesting,
     and both sets of rules; `rank_sensitivity_manifest.json` with the
     seven inputs), staged as `.tmp/` and renamed together; never
     `diagnostics/`, which `axis-diagnostics --analysis-dir
     results/motco_rank_sensitivity/rank_12 --out-dir
     results/motco_rank_sensitivity/diagnostics` writes. Findings, never
     stops: those of `analyze` that apply to a forced run (not the
     conditions of the cross-validation), a primary rank other than the
     predeclared anchor rank, a rank's status that differs from the
     primary's (rank dependence), a nesting check that fails, a primary
     read with `n_jobs ≠ 1`, stale diagnostics. The primary stays primary
     and no sweep value changes a constant (`ANALYSIS_RANK_FLOOR` and the
     ladder included), selects a rank, reruns the primary or defines an
     arm.
6. `report` – from the kept aggregate outputs only (`REPORT_INPUT_FILES`,
   106 committed files with 33 manifests: the two `clean_manifest.json`;
   `stage_counts.csv` and `cohort_manifest.json`; the export
   `manifest.json`; the primary's `result.json`, `analysis_manifest.json`
   and `summary.md`; the primary diagnostics' six files; under
   `results/motco_latent_sensitivity/` the arm's three aggregate analysis
   files, the comparison's three files and the arm diagnostics' six files;
   under `results/motco_export_sensitivity/<variant>/`, per variant of
   `REPORT_EXPORT_VARIANTS` in registry order (change
   `adni-report-variants`; the pin, change `adni-nmr-all-columns`),
   `bridge/nist_bridge.csv` for hook `factors`, `motco_input/manifest.json`,
   the variant analysis' three aggregate files, the comparison's three
   files and the variant diagnostics' six files; every variant of the pin
   required (all three registered variants since change
   `adni-report-nmr-all-columns`), and a variant registered later outside
   it not read or required, named on a progress line and never in the
   body; under `results/motco_stage_sensitivity/`
   (`REPORT_STAGE_ARM_FILES`, change `adni-report-stage-arm`) the
   CN / LMCI / AD arm export's `motco_input/manifest.json`, the arm
   analysis' three aggregate files, the comparison's three files and the
   arm diagnostics' six files, the arm required; under
   `results/motco_rank_sensitivity/` (`REPORT_RANK_SWEEP_FILES`, change
   `adni-report-rank-sweep`), per rank of `RANK_SENSITIVITY_LADDER` in
   ladder order, `rank_<kk>/` `result.json`, `analysis_manifest.json` and
   `summary.md`, then the comparison's three files and the top rank's
   diagnostics' six files, the sweep required), nothing else: no
   participant-level file is opened or required (their hashes are quoted
   from the manifests; every rank's `stage_means.csv` and
   `pls_loadings.csv` too), no data root, no MOTCO call, no pinned
   numerics, so it runs on any clone. Twelve flags: the nine directories
   (`--export-sensitivity-dir` the root of the variants,
   `--stage-sensitivity-dir` the root of the CN / LMCI / AD arm,
   `--rank-sensitivity-dir` the root of the rank sweep), `--out`,
   `--check`, `--force`. Gates before anything is written, each
   naming the file or setting, both values and the step to rerun: every
   input present; every aggregate file hashes to the value its own manifest
   records; the primary is the primary, the arm is
   `LATENT_SENSITIVITY_ARM` (`is_primary` in the two diagnostics manifests)
   and each variant directory of `REPORT_EXPORT_VARIANTS` holds its variant (its export, analysis and
   comparison manifests name it, its export manifest's `variant` block
   equals the `EXPORT_VARIANTS` entry, no latent adjustment, `is_primary`
   false and its name in its diagnostics), then the bridge table hashes to
   its export manifest's `bridge.table.sha256`; the CN / LMCI / AD arm is
   `STAGE_SENSITIVITY_ARM` (its export manifest records step
   `stage-sensitivity`, every field of the constant in its `stage_arm`
   block and no `variant` block, its analysis and comparison manifests name
   it, its analysis records no latent adjustment, `is_primary` false and
   `stage_arm` `cn_lmci_ad` in its diagnostics); the rank sweep is
   `RANK_SENSITIVITY_LADDER` (each rank directory holds its rank: step
   `rank-sensitivity`, `settings.forced_components`,
   `rank_sweep.forced_rank` and its record's `latent.selected_lv` the
   directory's rank with selection `forced`; every field of the constant in
   its `rank_sweep.ladder`; `rank_sweep.primary_rank` the primary record's
   rank; no latent adjustment and no `variant` or `stage_arm` block; the
   comparison manifest records the constant, exactly the ladder's
   directories and an anchor equal at the primary record's rank; the
   diagnostics record `is_primary` false and the forced rank
   `diagnosed_rank`); the primary, the arm, every variant analysis, the
   CN / LMCI / AD arm's analysis and every rank are reported runs
   (`n_jobs = REPORTED_N_JOBS`), every `numerics` block present is pinned
   and all 33 manifests record the same MOTCO, scikit-learn and
   metabo_adni versions; the chain holds link by link from the clean
   manifests to the arm's, every variant's, the CN / LMCI / AD arm's and
   the rank sweep's diagnostics (189 links: 31, then 23 for
   `nist_bridge`, 22 for `per_run_standardized`, 22 for
   `nmr_all_columns`, 24 for the
   CN / LMCI / AD arm, among them the primary feature tables its export
   manifest names as the source of its floors, and 67 for the rank sweep:
   8 per rank against the primary export and the primary as `reference`,
   15 for the comparison against the primary, every rank's two files and
   the primary export, 4 for the top rank's diagnostics). Writes
   `reports/motco-adni-<date>.md` (the date from the file name, in the
   title line only; an existing file stops it unless `--force`; staged as
   `<out>.tmp`, parsed back and renamed): the thirteen sections of
   `REPORT_SECTIONS` (summary; provenance, the report's manifest with the
   QC archives and NIST workbooks; cohort; export; primary analysis; axis
   diagnostics of the primary; latent-adjustment sensitivity; export
   sensitivity, one group of tables per rule set of the pinned variants
   (`_export_variant_groups`, change `adni-report-nmr-all-columns`): the
   run-handling group (`nist_bridge`, `per_run_standardized`) under the
   2026-10-31 titles and the membership group (`nmr_all_columns`) with
   tables titled `nmr_all_columns: …`, each holding the primary and its
   group's variants only, every variant-specific word (rule set, citation
   word, dependence label, what it changes and keeps) from
   `_variant_words`, the membership group's lead citing membership rule 8
   (`_GROUP_PRIMARY_ONLY_RULE`) and each counts table without the
   `analysis`, `phase_offset` and `diagnostics` keys the steps compare
   themselves; stage-definition sensitivity, the CN / LMCI / AD arm beside
   the primary with its four definition tables under their own headings;
   rank sensitivity, the primary beside each forced rank of the ladder with
   the anchor and nesting of `rank_sensitivity.md`, the predeclared counts
   and the top rank's diagnostics under sweep rule 7; findings; reading
   rules; reproduction), every reference to
   another section numbered from `REPORT_SECTIONS`, every table titled by
   a level-3 heading and keyed by its first column, every number copied
   from a record, a manifest or a CSV at the digits of the summary it
   belongs to (no statistic, correlation, mean or count of its own, no
   value across ranks), every reading sentence from
   `_statistic_reading_line`, `_arm_status_line`,
   `_export_variant_status_line`, `_stage_arm_status_line` and
   `_rank_status_line`, the variant lines from `_export_variant_lines`, the
   CN / LMCI / AD arm's bullets and four tables from `_stage_arm_lines` and
   `_stage_arm_tables` and the sweep's anchor and nesting bullets and
   nesting table from `_rank_anchor_lines` and `_rank_nesting_table` (the
   code of `summary.md`, `latent_sensitivity.md`, `export_sensitivity.md`,
   `stage_sensitivity.md` and `rank_sensitivity.md`, string-equal across
   the documents; no sentence reads one sensitivity against another, and no
   forced rank is read against another sensitivity's CV-selected rank),
   the flagged components of every diagnostics run in its
   `components.csv` order, six rule lists verbatim: `READING_RULES`, then
   `LATENT_SENSITIVITY_READING_RULES`, then one list per rule set of the
   pinned variants in group order (`EXPORT_VARIANT_READING_RULES`, then
   `NMR_MEMBERSHIP_READING_RULES`), then `STAGE_SENSITIVITY_READING_RULES`,
   then `RANK_SENSITIVITY_READING_RULES`, the arm's rules named
   beside every table that quotes the arm, each variant group's rule set
   beside every table of the group, the CN / LMCI / AD arm's beside every
   table that quotes it and the sweep's beside every table that quotes the
   sweep, the primary's status the result in every table;
   the body depends on the inputs and the file name only, so two runs are
   byte-identical. With `--check` (default: the newest report under
   `reports/` by the date in its name) it first compares the report's
   level-2 headings with `REPORT_SECTIONS`, then the export variants it
   lists (its headings ``Export variant `<name>` `` in "Export
   sensitivity", in order) with `REPORT_EXPORT_VARIANTS` (change
   `adni-report-nmr-all-columns`): a report of an earlier layout
   (`reports/motco-adni-2026-10-28.md`, ten sections,
   `reports/motco-adni-2026-10-29.md`, eleven sections,
   `reports/motco-adni-2026-10-30.md`, twelve sections, and
   `reports/motco-adni-2026-10-31.md`, two export variants) stops before
   any gate, naming its absent and extra sections or variants (or that
   their order differs) and `git log -1 --format=%H -- <report>`, the
   revision where it checks (36c9cc8, c94f5e7, 2e4a3e1 and 13ce7c8 for
   those reports); otherwise it reruns the gates, regenerates
   the report and compares every table cell by cell and every other line
   line by line, printing each mismatch (section, table, row key, column,
   both values; or the line with both texts), exits 1 on any and writes
   nothing; a regenerated results directory fails it on the provenance
   hashes until a new report is written and checked. Findings,
   never stops: every deviation and finding of every input manifest,
   verbatim under its step; a dirty recorded revision; a manifest without
   a `numerics` block. A report is committed alone after `--check` passes
   on the clean tree; it quotes aggregate values only and holds no
   participant identifier.

`README.md` documents the layout and the pipeline; keep it in sync when
behavior or defaults change.

## Hard constraints

### 1. ADNI is controlled-access (DUA): nothing participant-level is ever committed

- Never commit a raw ADNI file, a cleaned matrix, `p180_runs.csv`,
  metabo_adni's log, `cohort.csv`, a MOTCO
  input block, `metadata.csv`, `covariates.csv`, `latent_scores.csv`,
  `analysis_metadata.csv`, or any table with an `RID`, under any path,
  in any form (also not in a report, a proposal, a spike note, a test
  fixture, a docstring or a commit message).
- Committed outputs are aggregate only: `result.json`, `stage_means.csv`,
  `pls_loadings.csv`, manifests with hashes (among them
  `results/cleaned/*/clean_manifest.json`), `summary.md`,
  `stage_counts.csv` (group × stage counts), the diagnostics tables, the
  latent-sensitivity comparison (`latent_sensitivity.csv`,
  `latent_sensitivity.md`, its manifest), the export-sensitivity bridge
  table (`nist_bridge.csv`) and comparison (`export_sensitivity.csv`,
  `export_sensitivity.md`, its manifest), the stage-sensitivity comparison
  (`stage_sensitivity.csv`, `stage_sensitivity.md`, its manifest), the
  rank-sensitivity comparison (`rank_sensitivity.csv`,
  `rank_sensitivity.md`, its manifest) and the reports under `reports/`.
  An arm's, a variant's or a forced rank's analysis directory follows the
  primary's rule:
  its `latent_scores.csv` and `analysis_metadata.csv` are
  participant-level, its other five files aggregate; a variant's and the
  CN / LMCI / AD arm's `motco_input/` follow the primary export's (their
  CSVs participant-level, their `manifest.json` aggregate).
- `.gitignore` enforces this: `data/`, `results/cleaned/**` except
  `results/cleaned/*/clean_manifest.json`,
  `results/cohort/*.csv` except `stage_counts.csv`,
  `results/motco_input/**/*.csv` except manifests,
  `results/motco_export_sensitivity/*/motco_input/*.csv`,
  `results/motco_stage_sensitivity/motco_input/*.csv`,
  `results/**/latent_scores.csv`, `results/**/analysis_metadata.csv`,
  `results/**/*.tmp/`, `results/**/logs/`. The same list is
  `constants.PARTICIPANT_LEVEL_PATTERNS` (exceptions in
  `constants.AGGREGATE_EXCEPTIONS`) and the filter of
  `scripts/sync_results.sh`. A change that adds a participant-level output
  extends all three in the same change, before the output exists. Before
  committing under `results/`, name every file you add and say why it is
  aggregate.
- Progress output, logs and manifests name counts and files, never
  participants: no `RID` in a print, a finding, a log or a manifest.

### 2. Where the data lives

- Data lives on the user's machines (the data machines of the status
  paragraph above) and on `cluster.ing.uc.cl` only: never in a cloud
  service, never in a public bucket, never in a chat or an artifact.
- There is no download step: LONI needs a login, so the raw ADNI files are
  uploaded by hand into the data root. The canonical copy is
  `/home1/tgonza/adni_sexdiff/data` on the cluster; the data root is an
  explicit flag (`--data-root`) → `ADNI_DATA_ROOT` → `data/`. Machines
  differ only by this value.
- Data root layout: `<root>/Metabolomics/` is the archive as downloaded
  from LONI (dated file names such as `_10Jul2024`, data dictionaries,
  methods documents, the supplement zips with the p180 LOD workbooks
  extracted into `Metabolomics/p180/LOD/`, later layers such as
  `quant500/`); `<root>/Clinical/` holds the clinical tables under their
  original names (the ADNIMERGE freeze); the flat top level of `<root>`
  holds the exact names the steps read (metabo_adni's, the cohort's and the
  two QC archives `export-sensitivity --variant nist_bridge` reads in
  place) as relative symlinks into both (the list is under "Data & domain
  notes").
  Replicate a root with `rsync -a` (symlinks preserved, `Clinical/`
  included); never rename the archive files.
- Only aggregate outputs move between machines, with
  `scripts/sync_results.sh` (rsync of `results/` excluding every
  participant-level file; pull by default, `--push` to reverse). Never copy
  cleaned matrices or MOTCO inputs between machines; each machine makes its
  own from its own data root.

### 3. Cleaning goes through metabo_adni

- Cleaning is metabo_adni's (PyPI, `tomszar/metabo_adni`), pinned to an
  exact version (`metabo_adni==0.5.8` in `pyproject.toml`,
  `constants.METABO_ADNI_VERSION`, checked at run time), never
  reimplemented here. Its QC cutoffs, merge and transforms (`--mmc`,
  `--mpc`, `--cv`, `--icc`, `--merge`, `--log2`, `--zscore`,
  `--winsorize`, `--remove-moutliers`, `--residualize-meds`) are scientific
  choices (`CLEAN_OPTIONS`, decided by `adni-metabolomics-clean`). A
  metabo_adni defect is reported upstream and the pin moved by a change,
  never patched or vendored here; the pinned release's known behaviours are
  counted in `clean_manifest.json` under `upstream_behaviours`.

### 4. MOTCO pin

- `motco` is a git dependency pinned to the release tag `v0.10.0` of
  `https://github.com/tomszar/MOTCO` (`[tool.uv.sources]`; `uv.lock` holds
  the commit). Move it only with
  `uv add "motco @ git+https://github.com/tomszar/MOTCO@vX.Y.Z"`, never as
  a path dependency on `../MOTCO`.
- MOTCO pins scikit-learn exactly; do not loosen that pin to resolve a
  conflict. If metabo_adni does not resolve against MOTCO's pins on Python
  3.12, stop and report; do not vendor or patch either package.
- A pin move reruns `analyze` and re-issues every MOTCO-dependent output as
  the template's `motco-release-migration` spec binds (superseded
  directories moved, not deleted; a version-consistency check of every
  manifest; one re-issue report).

### 5. Statistical choices enter only through OpenSpec

- The cohort rule, the stage rule, the covariate set, the permutations, the
  seed, the rank floor, the reading rules, metabo_adni's options, the
  feature rule and the diagnostic variables are scientific decisions. Each
  enters only through an OpenSpec proposal that states it before any run,
  lives as a named constant in `src/adni_sexdiff/constants.py`, and is
  listed under "Flag and ask" below. Decided so far: `CLEAN_OPTIONS`,
  `COHORT_RULE`, `STAGE_RULE`, `ANALYSIS_COVARIATES`, `EXPORT_FEATURE_RULE`,
  `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA` with
  `ANALYSIS_REJECTION_RULE`, `ANALYSIS_RANK_FLOOR`,
  `ANALYSIS_LATENT_ADJUSTMENT`, `READING_RULES`, `DIAGNOSTIC_VARIABLES`,
  `DIAGNOSTIC_CORRELATION_THRESHOLD`, `LATENT_SENSITIVITY_ARM`,
  `LATENT_SENSITIVITY_COVARIATE_ROLES`, `LATENT_SENSITIVITY_READING_RULES`,
  `EXPORT_VARIANTS` (with its entry `nmr_all_columns`), `NIST_BRIDGE_RULE`,
  `EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES`,
  `STAGE_SENSITIVITY_ARM`, `STAGE_SENSITIVITY_READING_RULES`,
  `RANK_SENSITIVITY_LADDER`, `RANK_SENSITIVITY_READING_RULES`;
  `constants.py` reserves the others' names in its docstring and defines
  none of them.
- Never set, change or default one of them in code, a flag or a script
  without a proposal. Never choose one from a result.

### 6. Reported runs and report numbers

- Reported runs use `n_jobs = 1` (`constants.REPORTED_N_JOBS`): MOTCO seeds
  one RRPP stream per worker, so another value changes the permutation
  draws. Another value is recorded as a finding and the run is not reported.
- Reported and committed runs are pinned (`numerics.pinned` true in their
  manifest; `constants.NUMERIC_SETTINGS`, change `adni-portable-numerics`):
  with the pinned numeric environment every machine writes the same bytes
  from the same inputs, so the hash chain holds whichever machine ran a
  step. A run that is not pinned is a finding and its outputs are not
  committed.
- Report numbers are pasted from the generated files (`summary.md`,
  `result.json`, the manifests, `stage_counts.csv`) and checked by
  `adni-sexdiff report --check`, never retyped.

### 7. Private repository and the cluster

- `Omnia-Lab-UC/adni_sexdiff` is private, so the cluster cannot clone it
  over plain HTTPS as it does the template. It needs a read-only deploy key
  (an SSH key added to the repository's deploy keys, used through a host
  alias in `~/.ssh/config` on the cluster) or a fine-grained token scoped
  to this repository (for HTTPS). Neither is set up yet; setting one up is
  its own task, done by the user, not by an agent.

## Layout

- `src/adni_sexdiff/__init__.py` – sets `constants.NUMERIC_SETTINGS` in
  `os.environ` on import, before any module imports numpy.
- `src/adni_sexdiff/cli.py` – argparse CLI (`build_parser`, `main`); thin
  layer that calls into `data.py` and prints `[command]`-prefixed progress
  messages; `report` takes twelve flags (the nine directories, among them
  `--export-sensitivity-dir`, `--stage-sensitivity-dir` and
  `--rank-sensitivity-dir`, `--out`, `--check`, `--force`) and `main`
  returns 1 on a `--check` mismatch;
  `export-sensitivity` takes `--variant` (a name of `EXPORT_VARIANTS` or
  `all`; the variants and the rule are never flags) and the directories,
  `--n-jobs` and `--force`; `stage-sensitivity` takes `--input-dir`,
  `--analysis-dir`, `--cohort-dir`, `--out-dir`, `--n-jobs` and `--force`
  (the arm, its categories and its floors are never flags);
  `rank-sensitivity` takes `--input-dir`, `--analysis-dir`, `--out-dir`,
  `--n-jobs` and `--force` (the ladder and its ranks are never flags).
- `src/adni_sexdiff/constants.py` – named constants (it imports no numpy):
  conventions (paths, environment variables, platforms, columns, output
  names, pins, the pinned numeric environment `NUMERIC_SETTINGS`, the
  participant-level patterns, the clean inputs and the raw-file repair
  registry, the cohort's file, columns and sex values, the export's block
  order, feature statuses and covariate columns, the analysis' statistics,
  missing policy, categorical covariates and input files) defined;
  scientific constants reserved by name only until a proposal defines them
  (`CLEAN_OPTIONS` defined, with its predeclared `CLEAN_EXPECTED_COUNTS` and
  `RAW_INPUT_SHA256`; `COHORT_RULE`, `STAGE_RULE` and `ANALYSIS_COVARIATES`
  defined, with the predeclared `COHORT_EXPECTED_COUNTS`;
  `EXPORT_FEATURE_RULE` defined, with the predeclared
  `EXPORT_EXPECTED_COUNTS`; `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`,
  `ANALYSIS_ALPHA`, `ANALYSIS_REJECTION_RULE`, `ANALYSIS_RANK_FLOOR`,
  `ANALYSIS_LATENT_ADJUSTMENT` with
  `ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`, and `READING_RULES` defined,
  with the predeclared `ANALYSIS_EXPECTED_COUNTS`; `DIAGNOSTIC_VARIABLES`
  and `DIAGNOSTIC_CORRELATION_THRESHOLD` defined, with the conventions
  `DIAGNOSTIC_N_BLOCK_PCS`, `DIAGNOSTIC_CONDITIONING_COLUMNS`,
  `DIAGNOSTICS_ANALYSIS_FILES`, `DIAGNOSTICS_GEOMETRY_QUANTITIES` and the
  predeclared `DIAGNOSTICS_EXPECTED_COUNTS`; `LATENT_SENSITIVITY_ARM`,
  `LATENT_SENSITIVITY_COVARIATE_ROLES` and
  `LATENT_SENSITIVITY_READING_RULES` defined, with the conventions
  `LATENT_SENSITIVITY_DIR`, `LATENT_SENSITIVITY_SUBDIRS`,
  `LATENT_SENSITIVITY_TABLE`, `LATENT_SENSITIVITY_SUMMARY`,
  `LATENT_SENSITIVITY_MANIFEST` and the predeclared
  `LATENT_SENSITIVITY_EXPECTED_COUNTS`; two import-time assertions tie the
  arm to `ANALYSIS_PREDECLARED_LATENT_SENSITIVITY` and the roles to
  `ANALYSIS_COVARIATES`; `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE` and
  `EXPORT_VARIANT_READING_RULES` defined, with the predeclared
  `EXPORT_VARIANT_EXPECTED_COUNTS` (an import-time assertion ties its
  keys to the registry) and `NIST_BRIDGE_WORKBOOK_SHA256`, the two
  archives in `RAW_INPUT_SHA256`, and the conventions
  `EXPORT_SENSITIVITY_DIR`, `EXPORT_SENSITIVITY_SUBDIRS`,
  `EXPORT_SENSITIVITY_BRIDGE_TABLE`, `EXPORT_SENSITIVITY_TABLE`,
  `EXPORT_SENSITIVITY_SUMMARY` and `EXPORT_SENSITIVITY_MANIFEST`, change
  `adni-nist-bridge`; the `EXPORT_VARIANTS` entry `nmr_all_columns` (block
  `nmr`, hook `membership`) and `NMR_MEMBERSHIP_READING_RULES` defined, with
  the predeclared `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]`
  (`analysis` and `diagnostics` among its keys) and the convention
  `EXPORT_VARIANT_RULE_SETS` (per variant its rules, citation word,
  dependence label, source, heading and reader; two import-time assertions
  tie its keys to the registry and each `rules` to a tuple of the module),
  change `adni-nmr-all-columns`; `STAGE_SENSITIVITY_ARM` and
  `STAGE_SENSITIVITY_READING_RULES` defined, with three import-time
  assertions tying the arm to `STAGE_RULE`, the predeclared
  `STAGE_SENSITIVITY_EXPECTED_COUNTS` (`export`, `analysis`,
  `diagnostics`) and the conventions `STAGE_SENSITIVITY_DIR`,
  `STAGE_SENSITIVITY_SUBDIRS`, `STAGE_SENSITIVITY_TABLE`,
  `STAGE_SENSITIVITY_SUMMARY` and `STAGE_SENSITIVITY_MANIFEST`, change
  `adni-stage-sensitivity`; `RANK_SENSITIVITY_LADDER` and
  `RANK_SENSITIVITY_READING_RULES` defined, with three import-time
  assertions keeping the ladder ordered, its lowest rank
  `ANALYSIS_RANK_FLOOR` and its diagnosed rank its top, the predeclared
  `RANK_SENSITIVITY_EXPECTED_COUNTS` (`anchor`, `analysis` per rank,
  `comparison`, `diagnostics`) and the conventions `RANK_SENSITIVITY_DIR`,
  `RANK_SENSITIVITY_RANK_DIR`, `RANK_SENSITIVITY_SUBDIRS`,
  `RANK_SENSITIVITY_TABLE`, `RANK_SENSITIVITY_SUMMARY` and
  `RANK_SENSITIVITY_MANIFEST`, change `adni-rank-sensitivity`); the
  report's conventions (`DIAGNOSTICS_FILES`,
  `REPORT_VARIANT_FILES`, `REPORT_STAGE_ARM_FILES` keyed by the
  subdirectories of the CN / LMCI / AD arm, `REPORT_RANK_SWEEP_FILES`
  keyed `rank` then by the subdirectories of the rank sweep (an import-time
  assertion ties its keys to `RANK_SENSITIVITY_SUBDIRS`),
  `REPORT_INPUT_FILES` keyed by directory role with one role per variant
  subdirectory, per arm subdirectory, per rank of the ladder and per sweep
  subdirectory, `REPORT_SECTIONS` with thirteen titles; no scientific
  constant, changes `adni-report`, `adni-report-variants`,
  `adni-report-stage-arm` and `adni-report-rank-sweep`; the pin
  `REPORT_EXPORT_VARIANTS`, the variants the report covers, a subsequence of
  `EXPORT_VARIANTS` by an import-time assertion, from which
  `REPORT_INPUT_FILES` is built, change `adni-nmr-all-columns`; it holds
  the three variants `nist_bridge`, `per_run_standardized` and
  `nmr_all_columns` since change `adni-report-nmr-all-columns`).
- `src/adni_sexdiff/data.py` – all logic: the six steps (`clean`, `cohort`,
  `export`, `analyze`, `axis-diagnostics` and `report`: `run_report` with
  the loader and gates `_load_report_inputs` (the variant roles and labels
  `_variant_role` and `_variant_labels`, the CN / LMCI / AD arm's
  `_stage_arm_role` and `_STAGE_ARM_LABELS`, the rank sweep's
  `_rank_sweep_role` and `_RANK_SWEEP_LABELS`), the renderer
  `render_report` with its table builders, `_flagged_components` (a run's
  flagged components in its `components.csv` order),
  `_export_sensitivity_section` (one group of tables per rule set of the
  pinned variants, `_export_variant_groups`, the lead of a rule set that
  reads its variant against the primary only citing that rule,
  `_GROUP_PRIMARY_ONLY_RULE`, change `adni-report-nmr-all-columns`),
  `_stage_sensitivity_section` and `_rank_sensitivity_section`, the parser
  `parse_report` and the checker `check_report` with the earlier-layout
  gate `_check_report_layout` (the sections, then the export variants a
  report lists against `REPORT_EXPORT_VARIANTS`); the shared reading sentences
  `_statistic_reading_line` and `_arm_status_line` that `summary.md`,
  `latent_sensitivity.md` and the report print) and the sensitivity step `latent-sensitivity` (`run_latent_sensitivity`,
  with the reference checks `_check_primary_reference` and
  `_check_cohort_manifest`, the comparison rows and
  `render_latent_sensitivity`) and the sensitivity step
  `export-sensitivity` (`run_export_sensitivity` and `_run_export_variant`,
  with `_check_primary_export_chain`, the NIST reader and bridge
  `read_nist_workbook`, `_read_nist_archives` and `nist_bridge`, the
  status sentence `_export_variant_status_line` and the variant lines
  `_export_variant_lines`, which the report prints too, the variant's words
  `_variant_words` (its entry of `EXPORT_VARIANT_RULE_SETS` with what it
  changes and keeps, read by every variant renderer, change
  `adni-nmr-all-columns`), the rules section `_export_variant_rules_lines`,
  the `phase` line `_export_variant_phase_line`, and
  `render_export_sensitivity`) and the sensitivity step
  `stage-sensitivity` (`run_stage_sensitivity`, with the arm export
  `_stage_arm_export`, the status sentence `_stage_arm_status_line`, the
  arm lines `_stage_arm_lines` shared by the arm's `summary.md` and
  `stage_sensitivity.md` and the arm's four definition tables
  `_stage_arm_tables` they print, all three printed by the report too, and
  `render_stage_sensitivity`) and the sensitivity step `rank-sensitivity`
  (`run_rank_sensitivity`, with the anchor gate `_check_anchor`, the rank
  findings `_rank_findings`, the status sentence `_rank_status_line`, the
  summary's "Rank sweep" lines `_rank_sweep_lines` with `_anchor_text`
  (the compared fields in the gate's order `_ANCHOR_FIELD_ORDER`, so the
  clause read back from a manifest equals the step's), the anchor and
  nesting bullets `_rank_anchor_lines` and the nesting table
  `_rank_nesting_table`, the status sentence, bullets and table printed by
  `rank_sensitivity.md` and the report alike, and
  `render_rank_sensitivity`),
  `resolve_data_root`, the version gates
  (`check_metabo_adni_version`, `check_motco_version`,
  `check_motco_rank_floor`), the raw-input helpers, the analysis input
  loader (shared by `analyze`, `axis-diagnostics` and the four
  sensitivity steps), the shared export function (`_run_export`:
  the body of `export`, which a variant calls with its one hook, a p180 one
  or `membership` on the NMR block; the primary's bytes are its gate), the
  shared analysis function
  (`_run_trajectory_analysis`: the body of `analyze`, which the arm calls
  with `latent_adjustment` as its one differing setting, a variant
  with its export, the CN / LMCI / AD arm with its row subset and a rank
  of the sweep with `forced_components`, which skips the CV findings; the
  primary's bytes are its gate) and the summary renderer (arm-aware when
  the record carries `latent_adjustment`, variant-aware when the export
  manifest carries `variant`, stage-arm-aware when it carries
  `stage_arm`, sweep-aware when given `rank_sweep`), the diagnostic
  statistics (`spearman`,
  `partial_spearman`, `block_principal_components`, `geometry_shares`,
  `block_loading_shares`), the chain checks (`_check_analysis_inputs`,
  whose hints name the command that wrote the analysis read,
  `_check_cohort_chain`, which compares the rows the CN / LMCI / AD arm
  keeps on its export) and `render_axis_diagnostics` (arm-, variant-,
  stage-arm- and sweep-aware), the
  numeric-state record (`_numerics_record`, `_numerics_finding`,
  `_numerics`), and the manifest / `.tmp` helpers every step reuses.
- `scripts/` – `sync_results.sh` (aggregate outputs between a machine
  and the cluster), `clean.sbatch` (`clean --platform all` on the cluster),
  `analyze.sbatch` (`analyze` on the cluster, no `--n-jobs`, so a reported
  run), `spike_raw_inventory.py` (the clean change's read-only spike),
  `spike_cohort_inventory.py` (the cohort change's read-only spike),
  `spike_export_inventory.py` (the export change's read-only spike; it
  reads the Nightingale dictionary for the name-mark cross-check, which
  `export` does not), `spike_nist_bridge.py` (the NIST bridge change's
  read-only spike; it reads the study-pool rows of the raw p180 files and
  the participants' run offsets, which `export-sensitivity` does not),
  `spike_stage_arm.py` (the stage arm change's read-only spike; it reads
  the cleaned tables to measure recomputed floors, which
  `stage-sensitivity` does not), `spike_nmr_all_columns.py` (the NMR
  membership change's read-only spike; it fits the derived columns on the
  concentrations and measures the joint matrix, which `export-sensitivity`
  does not).
- `data/` – raw ADNI files, uploaded by hand; gitignored, never committed.
- `results/` – pipeline outputs; only the aggregate files named in
  constraint 1 are committed. `results/motco_latent_sensitivity/` holds the
  sensitivity step's `analysis/` (the arm, laid out as
  `results/motco_analysis/`), `comparison/` and `diagnostics/`;
  `results/motco_export_sensitivity/<variant>/` holds `bridge/`
  (`nist_bridge` only), `motco_input/`, `analysis/`, `comparison/` and
  `diagnostics/`; `results/motco_stage_sensitivity/` holds `motco_input/`,
  `analysis/`, `comparison/` and `diagnostics/`;
  `results/motco_rank_sensitivity/` holds `rank_02/` … `rank_12/` (each
  laid out as `results/motco_analysis/`), `comparison/` and
  `diagnostics/`.
- `reports/` – committed case-study reports (`motco-adni-<date>.md`),
  generated in full by `report` from the aggregate outputs (every number
  copied, every sentence a constant or a renderer's) and checked by
  `report --check`; aggregate, no participant identifier.
- `openspec/` – OpenSpec change proposals/specs (see below).

## Environment & commands

- Python `>=3.12,<3.14`, managed with **uv** (`uv.lock` is committed).
- Setup: the Nix flake (`flake.nix`) provides Python 3.12 and uv (no R);
  its shell hook runs `uv sync --locked`. Enter it with direnv (`.envrc` →
  `use flake`) or `nix develop`. Python packages come from uv, not Nix.
  Outside the Nix shell numpy cannot load its native libraries; run
  commands through `nix develop -c ...` there.
- Run the CLI:
  `uv run adni-sexdiff <clean|cohort|export|analyze|axis-diagnostics|latent-sensitivity|export-sensitivity|stage-sensitivity|rank-sensitivity|report> [options]`.
  `report` and `report --check` read committed aggregate files only, so
  they run on any clone (no data root, no data machine, no MOTCO call);
  every real-input check of the report change runs on the committed tree.
- Dependencies: `motco` (git tag, constraint 4), `metabo_adni==0.5.8`
  (constraint 3), `pandas`, `numpy`, `threadpoolctl` (the numeric-state
  record). Add dependencies with `uv add <pkg>` so `pyproject.toml` and
  `uv.lock` stay consistent.
- Numerics (constraint 6, change `adni-portable-numerics`): importing
  `adni_sexdiff` sets `constants.NUMERIC_SETTINGS` in the process
  environment, replacing other values, before numpy loads:
  `NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL"` (numpy's AVX-512
  dispatch), `OPENBLAS_CORETYPE=Haswell` (OpenBLAS's kernel),
  `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1`. The Nix shell and the
  sbatch scripts export the same values, so `motco analyze` and scratch
  scripts get them too.
  - In a script or notebook, import `adni_sexdiff` before numpy; otherwise
    the settings come too late and the step records a not-pinned finding.
  - Every manifest's `numerics` block records the host, the CPU, the
    variables, numpy's `log2` target and each BLAS library's kernel and
    threads. To check a machine, run a step and read `numerics.pinned`.
  - On 2026-10-28 an AVX-512 machine (24 CPUs) reproduced every committed
    output pinned, on 24 CPUs and on 1. Unpinned, `export`, `analyze` and
    the block SVD differed at about 1e-15.
  - Requires x86-64 with AVX2 (`OPENBLAS_CORETYPE=Haswell`); other
    architectures are unsupported.
- Data root: `--data-root` → `ADNI_DATA_ROOT` → `data/` (constraint 2).
- There is no test suite or linter configured yet. Verify changes by running
  the relevant CLI command or importing the function; say so explicitly when
  something could not be verified (real data is never available to an agent
  outside the data machines and the cluster). Synthetic checks run on any
  machine from a scratch directory, never from a data root.

## Data & domain notes

- Platforms (`constants.PLATFORMS`): `p180` (Biocrates p180, two kits, UPLC
  and FIA, measured on ADNI-1 and on ADNI-GO/2) and `nmr` (Nightingale NMR).
  metabo_adni 0.5.8 reads them from the data root by their original LONI
  names (`load.read_files`): `ADMCDUKEP180UPLC_01_15_16.csv`,
  `ADMCDUKEP180FIA_01_15_16.csv`, `ADMCDUKEP180UPLCADNI2GO.csv`,
  `ADMCDUKEP180FIAADNI2GO.csv` and the p180 LOD workbooks
  (`4097_UPLC_p180_Data.xlsx`, `4097_FIA_p180_Data.xlsx`,
  `4610 UPLC p180 Data.xlsx`, `4610 FIA p180 Data.xlsx`;
  `read_lod_files`); `ADNINIGHTINGALE2.csv`; the fasting file `BIOMARK.csv`
  (`RID`, `VISCODE2`, `BIFAST`; baseline rows); for `--residualize-meds`
  only, `ADMCPATIENTDRUGCLASSES_20170512.csv`. Do not rename them. In the data
  root these are symlinks to the dated LONI downloads under
  `Metabolomics/` (the LOD workbooks come from
  `ADMCDUKEP180SUPP_20170410.zip` and `ADMC_supplement.zip`).
  metabo_adni skips an absent concentration file silently but reads all
  four LOD workbooks unconditionally.
- The QC archives (`export-sensitivity --variant nist_bridge` only, change
  `adni-nist-bridge`): `ADMC_supplement.zip` and
  `ADMCDUKEP180SUPP_20170410.zip` at the top level of the data root, as
  relative symlinks made by hand on every data machine and the cluster
  (`ln -s Metabolomics/p180/ADMC_supplement.zip <root>/ADMC_supplement.zip`,
  `ln -s Metabolomics/p180/ADMCDUKEP180SUPP_20170410.zip <root>/ADMCDUKEP180SUPP_20170410.zip`).
  The step hashes each archive through its symlink (`RAW_INPUT_SHA256`)
  and reads four members in place, nothing extracted:
  `admc_supplement/duke_raw_data/4097_FIA_NIST_and_QC_Data.xlsx` and
  `admc_supplement/duke_raw_data/4097_UPLC_NIST_and_QC_Data.xlsx`
  (ADNI-1), `4610 FIA p180 QC and NIST Data.xlsx` and
  `4610 UPLC p180 QC and NIST Data.xlsx` (ADNI-GO/2), each against
  `NIST_BRIDGE_WORKBOOK_SHA256`. Their sheet `NIST SRM 1950 Data` holds
  NIST SRM 1950, the one material both p180 runs measured (ADNI-1 11
  plates × 3 replicates, ADNI-GO/2 12 × 2); the study pools are
  run-specific, so metabo_adni's cross-plate correction never links the
  runs. Only the ADNI-GO/2 workbooks carry per-cell status columns (41 FIA
  cells `ISTD Out of Range`); the ADNI-1 ones mark quality by colour only.
  `clean` and `cohort` do not read the archives.
- Known raw-file defect (LONI's own export, confirmed 2026-10-26):
  LONI's `ADMCDUKEP180UPLCADNI2GO.csv` lacks its final byte, the closing
  double quote of the last record's `update_stamp` field, so pandas' C
  parser (which metabo_adni uses) fails with "EOF inside string". The
  timestamp and every metabolite value of that record are complete. The
  archive copy under `Metabolomics/p180/` carries the repair, applied by
  hand on 2026-10-26 (a `"` and a newline appended; it parses as 941 × 67
  like its FIA sibling). Hashes: LONI's bytes
  `f28ede9aa70e02d2c8bf4ef2b3f4873a217675e424cd2498e4dd3f43d03df326`,
  the repaired file
  `7ad17d63eed26368a3e51254c942e9c2f39890d43decda37f7b1a2ade38de3a6`.
  `clean` records the file's sha256 in `clean_manifest.json` and names
  this repair when the hash is the repaired one; a fresh LONI download
  must be repaired the same way before it is put in the archive. `clean`
  implements this rule (`constants.KNOWN_RAW_FILE_REPAIRS`): LONI's
  unrepaired hash stops it before anything is written, and any other
  unknown hash is a finding.
- The cohort step reads, besides the visit columns of
  `ADMCDUKEP180UPLCADNI2GO.csv` (`VISCODE`), `ADMCDUKEP180FIAADNI2GO.csv`
  (`VISCODE`) and `ADNINIGHTINGALE2.csv` (`VISCODE2`): the QT-PAD ADNIMERGE
  freeze `ADNI_adnimerge_20170629_QT-freeze.csv` (sha256
  `e3eae0464106f0a3df4eb23946e57f1f7fd5f8456eb60af6540654a36a16f7a2`; the
  file of the 2022 study; in the archive as
  `Clinical/ADNI_adnimerge_20170629_QT-freeze.csv` with a top-level
  symlink; columns `RID`, `VISCODE`, `PTGENDER`, `DX.bl`, `DX`, `ORIGPROT`,
  `AGE`, `PTEDUCAT`, `APOE4`) and the medication table
  `ADMCPATIENTDRUGCLASSES_20170512.csv` (`RID`, `VISCODE2`,
  `HMG CoA reductase inhibitors`; classes are filled at `sc`, read with
  `dtype=str`). Both go through the raw-input checks (`RAW_INPUT_SHA256`
  holds both hashes). A fresh download is its own change.
- `RID` is ADNI's participant key (`constants.PARTICIPANT_ID_COLUMN`). Any
  table that holds it is participant-level (constraint 1). The export's
  sample column is `rid`, the group column `sex`, the stage column `stage`
  with `STAGE_LABELS` CN / MCI / AD in trajectory order.
- Known property of the p180 block (recorded by `export`, confirmed
  2026-10-27): the p180 run (ADNI-1 against ADNI-GO/2, which equals the
  `phase` covariate for every cohort participant) is the block's first
  axis. On the rule's scale and the 1501 exported participants, the
  standardized mean difference between phases has median |d| 1.12 over the
  133 p180 metabolites (80 above 1) and the block's first principal
  component correlates 0.73 with phase; the NMR block, assayed in one
  batch, has 0.21, 0 and 0.13. `export` records the offset per block
  (`manifest.json`, `counts.phase_offset`) and per metabolite
  (`features_<platform>.csv`, `phase_d`) and does not correct it: the runs
  differ in stage composition (EMCI and SMC exist only in ADNI-GO/2), so
  per-run centering would move stage signal between runs. `phase` enters
  MOTCO as a covariate of the stage means (decided by `adni-analyze`:
  additively with the other four covariates, design column
  `phase[ADNI2GO]`, LS-means at the pooled phase proportion, no sex ×
  covariate or stage × covariate term); the primary's latent space is
  built without the covariates, and the `stage`-conditioned latent
  adjustment is the predeclared sensitivity arm, run by
  `latent-sensitivity` (change `adni-latent-sensitivity`) after
  `axis-diagnostics` measured the primary's components against phase
  (`phase` is among `DIAGNOSTIC_VARIABLES`, decided by
  `adni-axis-diagnostics`; the diagnostic also correlates each block's PCs
  with `phase` beside the export's recorded value and records which block
  carries each component) and read beside the primary, never replacing
  it. The arm's components can still track phase, since the raw features
  are measured in the adjusted basis; its own `axis-diagnostics` run
  measures that, and arm rule 9 reads it as a measurement-space finding.
  The run offset is mostly measurement (the spike of `adni-nist-bridge`,
  2026-10-29): NIST SRM 1950 shows the participants' offset (Spearman 0.82)
  and carries 85 % of its sum of squares (FIA 90 %, UPLC 38 %). The two
  predeclared export variants of `export-sensitivity` handle it beside the
  primary, never replacing it: `nist_bridge` (median |d| 1.12 → 0.29, PC1
  correlation 0.73 → 0.22, the run moving to PC2 at 0.58 with a common
  residual shift) and `per_run_standardized` (the whole run difference,
  stage composition included). The design side is the predeclared
  CN / LMCI / AD arm of `stage-sensitivity` (change
  `adni-stage-sensitivity`): it drops SMC and EMCI, so each stage holds
  one `DX.bl` category in both runs and the `phase` coefficient is
  estimated within one diagnosis; it does not balance the runs across
  stages (ADNI-1 share CN 0.527, MCI 0.700, AD 0.544) or remove the run
  offset (median |d| 1.10 on its rows).
  The blocks enter MOTCO 0.10.0 unweighted: p180 holds 133 / 298 of the
  joint features; the export manifest records the shares and
  `components.csv` the loading share of each block per component.
- Flag and ask before changing, and never set without a proposal
  (constraint 5); decided so far: `CLEAN_OPTIONS`, `COHORT_RULE`,
  `STAGE_RULE`, `ANALYSIS_COVARIATES`, `EXPORT_FEATURE_RULE`,
  `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA`,
  `ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`, `READING_RULES`,
  `DIAGNOSTIC_VARIABLES`, `DIAGNOSTIC_CORRELATION_THRESHOLD`,
  `LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`,
  `LATENT_SENSITIVITY_READING_RULES`, `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE`,
  `EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES` (with the
  predeclared `EXPORT_VARIANT_EXPECTED_COUNTS`), `STAGE_SENSITIVITY_ARM`,
  `STAGE_SENSITIVITY_READING_RULES` (with the predeclared
  `STAGE_SENSITIVITY_EXPECTED_COUNTS`), `RANK_SENSITIVITY_LADDER`,
  `RANK_SENSITIVITY_READING_RULES` (with the predeclared
  `RANK_SENSITIVITY_EXPECTED_COUNTS`); every constant the six steps and
  the four sensitivity steps need is decided:
  - `CLEAN_OPTIONS` – metabo_adni's cutoffs, merge and transforms per
    platform. Decided by `adni-metabolomics-clean`: `mmc` 0.2, `mpc` 0.2,
    for p180 also `cv` 0.2 and `icc` 0.65 (p180-only in metabo_adni),
    `merge` on; `log2`, `zscore`, `winsorize`, `remove_moutliers`,
    `residualize_meds` off. Its predeclared counts are
    `CLEAN_EXPECTED_COUNTS`. A change of it is a new proposal.
  - `COHORT_RULE` – decided by `adni-cohort`: clinical table the ADNIMERGE
    freeze `ADNI_adnimerge_20170629_QT-freeze.csv`, one row per
    participant from its `VISCODE` `bl` row; a cleaned participant enters a
    platform's set only if every raw record on that platform has visit `bl`
    (`VISCODE` in the ADNI-GO/2 p180 files, `VISCODE2` in the NMR file; the
    ADNI-1 p180 run has no visit column and counts as baseline) and it has
    a `bl` row; the analysis cohort is the intersection of the p180 and NMR
    sets (n = 1501); no other exclusion. Its predeclared counts are
    `COHORT_EXPECTED_COUNTS`.
  - `STAGE_RULE` – decided by `adni-cohort`: `DX.bl` on the `bl` row,
    `CN` and `SMC` → CN, `EMCI` and `LMCI` → MCI, `AD` → AD.
  - `ANALYSIS_COVARIATES` – decided by `adni-cohort`, in this order: `age`
    (`AGE`, numeric), `education` (`PTEDUCAT`, numeric), `apoe4` (`APOE4`,
    categorical 0/1/2), `phase` (`ORIGPROT`: `ADNI1` → `ADNI1`, `ADNIGO` and
    `ADNI2` → `ADNI2GO`; categorical), `statin` (medication table,
    `HMG CoA reductase inhibitors` on the `sc` row, filled 1, empty 0;
    categorical); missing policy `error`, nothing imputed. They do not
    condition the primary's latent space (`ANALYSIS_LATENT_ADJUSTMENT`,
    decided by `adni-analyze`).
  - `EXPORT_FEATURE_RULE` – decided by `adni-export`. Membership: a block
    holds the measured concentrations of its platform, each once; every
    cleaned p180 metabolite enters (133); a cleaned NMR column enters unless
    its name carries a derived mark, the percentages (`_PCT`, 72), the
    ratios (`_BY_`, 4), the degree of unsaturation (`UNSATURATION`, 1) and
    the particle sizes (`_SIZE`, 3), which are excluded with status
    `derived` (165 kept of 245; the change's spike checked the marks
    against the Nightingale dictionary's units). Scale: `log2(x + floor)`
    for both blocks, the floor of a metabolite its 5 % quantile (linear
    interpolation) over the exported participants, computed without sex,
    stage or a covariate and recorded per feature; MOTCO's transform
    `identity`, MOTCO's own z-scoring. Nothing imputed, replaced,
    winsorized, removed or centred per run. Its predeclared counts are
    `EXPORT_EXPECTED_COUNTS`. Its variants enter `EXPORT_VARIANTS`, each by
    its own proposal: `nist_bridge` and `per_run_standardized` by
    `adni-nist-bridge`, `nmr_all_columns` (all 245 NMR columns) by
    `adni-nmr-all-columns`; the others registered after the primary
    analysis (the raw scale, `log2(x + 1)`, the generalized log) are one
    later change.
  - `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA`,
    `ANALYSIS_REJECTION_RULE` – decided by `adni-analyze`: 9999 RRPP
    permutations (the p-value `(1 + b) / (1 + B)` is exact in size at any
    count; the count sets the resolution, 0.0001), seed 20261027 (the
    proposal's date), α = 0.05, rejected when `p <= alpha` (the rule of
    MOTCO's covariate Type I check).
  - `ANALYSIS_RANK_FLOOR` – decided by `adni-analyze`: 2, MOTCO's validated
    default `min_components`, passed explicitly and checked equal to
    MOTCO's default before any input is read; a MOTCO whose default moved
    stops the run.
  - `ANALYSIS_LATENT_ADJUSTMENT` – decided by `adni-analyze`: `None` for the
    primary (the covariate-blind basis of MOTCO's validated path). The
    `stage`-conditioned latent adjustment with the same five covariates and
    every other setting equal is the predeclared sensitivity arm
    (`ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`) of the next change
    `adni-latent-sensitivity`, read beside the primary and never replacing
    it; `group_stage` conditioning is not admissible and does not run.
    Every other MOTCO setting stays MOTCO's default (net-displacement
    orientation, double CV 4 × 3 folds, 5 repeats, `max_components` 20,
    `random_state` 1203, no forced rank, no attribution) and is read back
    from the record; a moved default is a finding.
  - `READING_RULES` – decided by `adni-analyze`, written before any run:
    nine statements printed verbatim in `summary.md` and carried by every
    report, sensitivity and diagnostic (the primary stays primary and an
    arm's differing status is dependence; the CV-selected rank, floor,
    eigengap and null summary beside `angle`; `angle` and `shape`
    non-rejections uninformative, no power statement at this design; a
    `delta` rejection a difference, not of size; the covariate block, the
    run offset, the block shares and the feature rule beside the results;
    reported runs at `n_jobs = 1`; no result changes a constant).
  - `DIAGNOSTIC_VARIABLES`, `DIAGNOSTIC_CORRELATION_THRESHOLD` – decided by
    `adni-axis-diagnostics` (2026-10-27, before any run). The variables, in
    this order, each with its source among the kept outputs: `age`,
    `education` (`covariates.csv`, years), `apoe4` (0 / 1 / 2, ordinal),
    `phase` (1 for `ADNI2GO`, 0 for `ADNI1`: the p180 run), `statin`
    (1 / 0), `stage` (`metadata.csv`: CN 0, MCI 1, AD 2), `male` (1 for
    Male), `dx_bl` (`cohort.csv`: CN 0, SMC 1, EMCI 2, LMCI 3, AD 4, the
    enrollment gradient `STAGE_RULE` merges; SMC and EMCI exist only in
    ADNI-GO/2, so a phase axis is also a `dx_bl` axis). The threshold 0.3
    is a reporting flag on |ρ|, raw and partial, for latent components and
    block PCs alike: magnitude, not significance (no p-value on any
    correlation), and never an adoption rule. Conventions beside them: the
    partial correlations condition on the record's six design columns
    (`DIAGNOSTIC_CONDITIONING_COLUMNS`), `DIAGNOSTIC_N_BLOCK_PCS` = 3; the
    predeclared counts are `DIAGNOSTICS_EXPECTED_COUNTS`. The diagnostic
    feeds no filter, variant or arm: nothing is chosen from a flagged row,
    and no `export` or `analyze` run reads its outputs.
  - `LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`,
    `LATENT_SENSITIVITY_READING_RULES` – decided by
    `adni-latent-sensitivity` (2026-10-28, before any run). The single arm
    `latent_stage`: `covariate_latent_adjustment = "stage"`, the five
    `ANALYSIS_COVARIATES` in their order and coding, every other setting
    the primary's (`ANALYSIS_*` and MOTCO's defaults, `n_jobs = 1` for the
    reported run); it must equal `ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`
    (an import-time assertion), and no `extended_covariates` or
    `group_stage` arm exists. The roles, per covariate, as its relation to
    the stage effect: `age`, `education` and `apoe4` pre-disease (they can
    confound the stage effect, not be downstream of it), `phase` design
    (the assay run and protocol, tied to stage composition by design),
    `statin` the one mediator candidate (a treatment that may follow
    diagnosis; it stays in the arm because the arm was predeclared with
    the five covariates, and the reading carries the limitation); no
    statistic or threshold is computed for them, and
    `latent_sensitivity.md` prints them beside the cohort manifest's
    per-cell descriptives, copied. The nine arm rules, printed verbatim
    after `READING_RULES` in the arm's `summary.md`,
    `latent_sensitivity.md`, the arm's `diagnostics.md` and every report
    that quotes the arm: the arm never replaces the primary (MOTCO's
    `candidate_fails`); a differing status is basis dependence; the arm's
    rank, floor, eigengap and null summary beside its `angle`; an
    arm-only `angle` rejection is read against MOTCO's translation
    control; an arm's non-rejection is weaker than the primary's; the
    `latent_adjustment` and covariate blocks with `feature_r2` beside the
    results; the mediator limitation with `statin`; no operating
    characteristic at this design; an arm axis in the diagnostic is a
    measurement-space finding and never grounds to adopt the arm. The
    rule that binds all of it: the arm never replaces the primary and
    feeds no choice (no constant, covariate, variant or rerun of the
    primary comes from an arm value). Its predeclared counts are
    `LATENT_SENSITIVITY_EXPECTED_COUNTS` (the `ANALYSIS_EXPECTED_COUNTS`
    plus the latent-adjustment block: conditioning `stage`, the five
    covariates, the eight residualization design columns `stage[1]`,
    `stage[2]` then the six design columns, 1501 samples, residual df
    1492, feature scale `pooled_standardized`); the arm's rank is not
    predeclared.
  - `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE`, `EXPORT_VARIANT_READING_RULES`,
    `EXPORT_VARIANT_EXPECTED_COUNTS` – decided by `adni-nist-bridge`
    (2026-10-29, before any run; the user chose the validity rule, both
    kits, the second variant and a later report change). The registry, in
    order: `nist_bridge` (block p180, hook `factors`: every cleaned p180
    concentration of a participant whose run in `p180_runs.csv` is
    ADNI2GO multiplied by 2^b of its metabolite before the floors; the
    feature rule then unchanged) and `per_run_standardized` (block p180,
    hook `standardize_by_run`: the rule's p180 values, pooled floors and
    `log2(x + floor)`, each metabolite centred and divided by its
    population SD within its run); every other export and analysis
    setting the primary's. The bridge rule, from NIST SRM 1950 alone: the
    rows labelled `NIST SRM 1950` of the sheet `NIST SRM 1950 Data` of the
    four QC workbooks; a replicate's cell valid when a positive number
    whose status, where a status column exists, is not
    `ISTD Out of Range` (text cells missing); a metabolite bridged when at
    least half (0.5) its replicates are valid in each run; `b` the mean
    log2 of its valid ADNI-1 replicates minus that of its valid ADNI-GO/2
    ones, reference run ADNI-1, no plate correction, no significance gate;
    both kits, names matched within kit with case and punctuation dropped;
    factor 1 when not bridged. On the predeclared bytes: 126 of 133
    bridged (FIA 102, UPLC 24); `C0`, `C10:2`, `C12`, `C14:1-OH`,
    `C6 (C4:1-DC)`, serotonin and spermidine not (`C0`: 17 of its 24
    ADNI-GO/2 cells ISTD-flagged). The seven reading rules, printed
    verbatim after `READING_RULES` in each variant's `summary.md`,
    `export_sensitivity.md`, a variant's `diagnostics.md` and every report
    that quotes a variant: a variant never replaces the primary and no
    variant result changes a constant, reruns the primary or adopts a
    variant; a variant differs only in the p180 values, so a differing
    status is run-handling dependence; its rank, floor, eigengap and null
    summary beside its `angle`, a differing rank reported, not ranked;
    `nist_bridge` removes the calibration part NIST carries and assumes
    one factor per metabolite shared by plasma and serum, leaving a common
    shift, sample handling (aspartate, glutamate) and the seven unbridged
    metabolites to `phase`; `per_run_standardized` removes the whole run
    difference, stage composition included, and a difference between the
    two variants is the part that is not calibration, never evidence for
    either; a variant's non-rejection is no more informative than the
    primary's, a variant-only rejection is run-handling dependence; the
    run offset per block and the bridge factors beside the results, and a
    variant axis in the diagnostic a measurement-space finding. Predeclared
    counts, per variant: every key of `EXPORT_EXPECTED_COUNTS` with the
    p180 phase |d| > 0.5 / > 1 replaced (`nist_bridge` 35 / 8,
    `per_run_standardized` 0 / 0), for `nist_bridge` 102 / 24 / 7 bridged
    FIA / UPLC / not and 0 unmatched, 0 runs that differ from `phase`,
    `nmr.csv`, `metadata.csv` and `covariates.csv` equal to the primary's,
    and every key of `ANALYSIS_EXPECTED_COUNTS` for the analysis; the
    ranks are not predeclared. No variant value selects a metabolite,
    changes a constant or defines a variant.
  - `EXPORT_VARIANTS["nmr_all_columns"]`, `NMR_MEMBERSHIP_READING_RULES`,
    the dependence label, `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]`
    – decided by `adni-nmr-all-columns` (2026-10-30, before any run of it;
    the user chose this variant alone, the report pin, the rule's scale
    for the derived columns and a self-contained rule set). The entry:
    block `nmr`, hook `membership`, no rule, no data root; every cleaned
    NMR column enters the block (245), the 165 concentrations of
    `EXPORT_FEATURE_RULE` and its 80 derived columns (72 percentages, 4
    ratios, the degree of unsaturation, 3 sizes), in cleaned order, each on
    the rule's scale, `log2(x + floor)` with its own 5 % floor over the
    exported participants; the p180 block, the participants, the metadata
    and the covariates the primary's; every analysis setting the primary's.
    The two p180 entries are untouched (no key added), so their recorded
    `variant` blocks still equal the registry. The eight membership rules,
    printed verbatim after `READING_RULES` in the variant's `summary.md`,
    `export_sensitivity.md`, `diagnostics.md` and every report that quotes
    it, in place of `EXPORT_VARIANT_READING_RULES` (whose rule 2 says a
    variant differs only in the p180 values), cited as "membership rule N":
    1. The variant never replaces the primary, and no result of it changes
       a constant (`EXPORT_FEATURE_RULE` included).
    2. It differs only in the NMR block's membership: 378 joint features,
       the p180 share 133 / 298 (0.446) → 133 / 378 (0.352). A differing
       status is dependence on the feature membership.
    3. Its rank, floor, eigengap and `angle` null summary are read beside
       its `angle`; a differing rank is reported, not ranked.
    4. The 80 columns add no measurement: the concentrations explain a
       median 0.998 of a derived column's variance (lowest 0.798). They
       add weight to the lipoprotein directions, and tails: 21 with
       |skew| > 1 and 8 with a largest |z| above 8, mostly percentages of
       the large HDL and VLDL lipids.
    5. It is not a reproduction of the 2022 study, which used all 245
       columns with `log2(x + 1)`, winsorizing, outlier removal and
       medication residuals.
    6. Its non-rejection is no more informative than the primary's; a
       rejection only in the variant is feature-membership dependence.
    7. The block shares, the NMR shape counts, the run offset per block and
       each block's loading share are reported beside the results. A
       variant axis in the diagnostic is a measurement-space finding.
    8. It is read against the primary only, never against another
       sensitivity.

    Rules 1, 2, 3, 6 and 7 have the roles of `EXPORT_VARIANT_READING_RULES`
    1, 2, 3, 6 and 7. The dependence label is `differs (feature-membership
    dependence)`; the p180 variants keep `differs (run-handling
    dependence)`. The rule set, citation word and label of each variant
    live in the convention `EXPORT_VARIANT_RULE_SETS`.

    Predeclared counts, from the change's spike and the committed
    manifests:
    - the export: 1501 participants in the primary's cells; p180 133 / 133;
      NMR 245 cleaned, 245 kept, 0 derived, derived kept 72 / 4 / 1 / 3;
      378 joint features; zero cells p180 0 and NMR 41 in 3 metabolites;
      0 floors not positive and 0 non-finite cells;
    - the NMR shape: |skew| > 1 for 24 columns, largest |z| > 8 for 9;
    - the run offset: phase |d| > 0.5 / > 1 at p180 109 / 80 and NMR 5 / 0;
      0 runs that differ from `phase`;
    - `p180.csv`, `metadata.csv`, `covariates.csv` and the 165
      concentration columns equal to the primary's;
    - the analysis: every key of `ANALYSIS_EXPECTED_COUNTS` with features
      133 / 245 / 378;
    - the diagnostics: the rank-independent keys with 245 NMR features.

    The rank is not predeclared. No variant value selects a metabolite,
    changes a constant or defines a variant.
  - `STAGE_SENSITIVITY_ARM`, `STAGE_SENSITIVITY_READING_RULES`,
    `STAGE_SENSITIVITY_EXPECTED_COUNTS` – decided by
    `adni-stage-sensitivity` (2026-10-29, before any run; the user chose
    the primary's floors). The single arm `cn_lmci_ad`: the exported
    participants whose `dx_bl` (`cohort.csv`, ADNIMERGE `DX.bl` on the
    `bl` row) is CN, LMCI or AD, staged by `STAGE_RULE`'s own map (CN →
    CN, LMCI → MCI, AD → AD), SMC and EMCI (enrolled only in ADNI-GO/2)
    dropped; three import-time assertions tie the keep and drop sets and
    the map to `STAGE_RULE`. Its rows are the primary export's rows of the
    kept participants, every cell unchanged (the primary's floors and
    scale, no re-export); every analysis setting the primary's
    (`ANALYSIS_*`, MOTCO's defaults, no latent adjustment, `n_jobs = 1`
    for the reported run); not crossed with the latent adjustment or an
    export variant. The eight reading rules, printed verbatim after
    `READING_RULES` in the arm's `summary.md`, `stage_sensitivity.md`, the
    arm's `diagnostics.md` and every report that quotes the arm: the arm
    never replaces the primary and no arm result changes a constant,
    `STAGE_RULE` or `COHORT_RULE`, reruns the primary or adopts the arm;
    the arm's rows are the primary's rows of the 1130 participants, it
    differs in the participants (its CN is `DX.bl` CN, its MCI is LMCI)
    and so in its z-scoring, CV folds, basis, rank, reference row and
    draws, and a differing status is dependence on the stage definition
    and the sample; its rank, floor, eigengap and null summary beside its
    `angle`, a differing rank reported, not ranked; each stage holds one
    `DX.bl` category in both runs, so `phase` is estimated within one
    diagnosis, while the runs stay unbalanced (ADNI-1 share CN 0.527, MCI
    0.700, AD 0.544 against 0.417, 0.446, 0.544) and the run offset stays
    (median |d| 1.10 against 1.12, PC1 0.71 against 0.73); the arm's MCI is
    a later and narrower stage and its CN excludes subjective memory
    concern, and `angle` reads the endpoints (the AD cells are the
    primary's, the CN cells lose SMC); a non-rejection is no more
    informative than the primary's and an arm-only rejection is
    stage-definition dependence; the cells, runs within stage and run
    offset beside the results, an arm axis in the diagnostic a
    measurement-space finding, and `dx_bl` coinciding with `stage` in the
    arm; the arm is read against the primary only. Predeclared counts,
    from the committed `stage_counts.csv` and the change's spike: `export`
    1130 kept, SMC 96 and EMCI 275 dropped, cells Female 183 / 187 / 125
    and Male 181 / 296 / 158, runs within stage (ADNI1 / ADNI2GO) CN
    192 / 172, MCI 338 / 145, AD 154 / 129, features 133 / 165, every row
    of the four CSVs equal to the primary's, 0 missing covariate values
    and non-finite cells, p180 phase |d| > 0.5 / > 1 at 107 / 77 (NMR > 1
    at 0); `analysis` every key of `ANALYSIS_EXPECTED_COUNTS` with 1130
    participants, those cells and the levels `apoe4` 589 / 413 / 128,
    `phase` 684 / 446, `statin` 603 / 527; `diagnostics` the
    rank-independent keys with the arm's participants and cells. The rank
    is not predeclared. No arm value selects a participant, changes a
    constant or defines another arm.
  - `RANK_SENSITIVITY_LADDER`, `RANK_SENSITIVITY_READING_RULES`,
    `RANK_SENSITIVITY_EXPECTED_COUNTS` – decided by
    `adni-rank-sensitivity` (2026-10-30, before any forced rank ran on
    ADNI data; the spike was synthetic). The single ladder
    `forced_rank_ladder`: ranks 2, 3, 4, 6, 9 and 12 (2 the rank floor and
    `n_stages − 1`, 3 the next rank, 4, 6, 9 and 12 the steps of MOTCO's
    rank ladder and the template's sweep; both sides of the primary's 8,
    inside the CV's candidate range and far below the feasibility bound
    298), the one setting `forced_components` (the rank fixed, MOTCO's
    cross-validation skipped), `ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS`
    at every rank, every other setting the primary's (the primary export,
    `ANALYSIS_*`, MOTCO's defaults, no latent adjustment, `n_jobs = 1` for
    the reported run); the primary's rank is not on the ladder but the
    anchor: one forced run at the primary record's rank, compared with the
    primary before any rank runs and not kept; the top rank (12) is the
    one the axis diagnostic reads; not crossed with the latent adjustment,
    an export variant or the CN / LMCI / AD arm; three import-time
    assertions keep the ranks ordered, the lowest `ANALYSIS_RANK_FLOOR` and
    the diagnosed rank the top. The eight reading rules, printed verbatim
    after `READING_RULES` in each rank's `summary.md`,
    `rank_sensitivity.md`, the top rank's `diagnostics.md` and every report
    that quotes the sweep: the sweep never replaces the primary (whose
    rank is its CV-selected 8), no rank is chosen, adopted or ranked and no
    sweep result changes a constant (`ANALYSIS_RANK_FLOOR` and the ladder
    included), reruns the primary or defines another arm; every rank is the
    primary with `forced_components` changed and the same draws at
    `n_jobs = 1`, so a differing status is rank dependence; PLS-DA
    components are nested (a rank at or below 8 is the primary's first
    components, a rank above adds components the CV did not select) and
    the anchor reproduces the primary exactly; each rank's floor, eigengap
    and `angle` null beside its `angle`, each `angle` against its own null,
    rank 2 two-dimensional; MOTCO's forced-rank evidence is its Phase 5
    rank ladder (2026-09-08; MOTCO 0.6.0, n = 1200, four stages, no
    covariates), no Type I or power check exists at a forced rank at this
    design or with covariates, a non-rejection is no more informative than
    the primary's and a forced-rank-only rejection is rank dependence; the
    sweep is not a test (nothing combines ranks, picks the smallest p or
    counts rejections; no multiplicity adjustment); the top rank's axis
    diagnostic beside the sweep, its components up to 8 the primary's and
    an added component that tracks a variable a measurement-space finding;
    the sweep is read against the primary only. Predeclared counts, from
    the committed primary manifests and the ladder: `anchor` rank 8;
    `analysis` per rank every key of `ANALYSIS_EXPECTED_COUNTS` with
    selection `forced`, the rank and 0 CV repeats; `comparison` 7 rows;
    `diagnostics` the rank-independent keys, the read (rank 12, `forced`,
    no latent adjustment, `n_jobs` 1) and rows 96 / 48 / 48 / 12. No
    rank's statistic or status is predeclared. No sweep value selects a
    rank, changes a constant or defines another arm.
- Deviations from predeclared counts go to a manifest's `findings`, never
  silently.
- Statistical choices are scientific decisions. Don't change them silently;
  flag them and ask.

## Cluster (`cluster.ing.uc.cl`)

- Repo clone at `/home1/tgonza/adni_sexdiff` (needs the deploy key or token
  of constraint 7); raw data canonical at `/home1/tgonza/adni_sexdiff/data`,
  uploaded by hand; `uv sync --locked` on the login node (uv in
  `~/.local/bin`; MOTCO is fetched from public GitHub there).
- Partition `512x1024`, no scratch. Avoid the `full` partition: node n14 has
  glibc 2.17 and cannot import the numpy wheels installed from the login
  node (glibc 2.34).
- Compute nodes have no internet access. Light steps (`cohort`, `export`,
  `report`) run on the login node; `clean` through `scripts/clean.sbatch`
  (it calls `.venv/bin/adni-sexdiff`, synced on the login node, since
  `uv run` could try to reach the network), `analyze` through
  `scripts/analyze.sbatch` (the same locked environment, no `--n-jobs`, so
  a reported run; compare the pulled `analysis_manifest.json` with the
  data machine's: statistics, p-values, rank). `latent-sensitivity`,
  `export-sensitivity`, `stage-sensitivity` and `rank-sensitivity` run
  there the same way once
  the clone exists (pinned,
  so they must reproduce the committed hashes; `nist_bridge` needs the two
  archive symlinks in the cluster's data root). Both scripts export
  `NUMERIC_SETTINGS`; `OPENBLAS_CORETYPE=Haswell` needs AVX2, so check a
  node once (`grep -m1 -o avx2 /proc/cpuinfo` in a job) and read the pulled
  manifest's `numerics` (`pinned` true, the node's CPU).
- Only aggregate outputs leave the cluster: `scripts/sync_results.sh`
  (constraint 2). Never copy raw files, cleaned matrices or MOTCO inputs
  between machines.

## Code conventions

- `from __future__ import annotations`, modern type hints (`str | Path`,
  `list[str]`), keyword-only args (`*`) for optional parameters.
- NumPy-style docstrings (`Parameters`, `Returns`, `Notes` sections); a
  step's docstring states its inputs, outputs and output contract.
- Accept `str | Path` for paths and convert with `Path(...)` internally.
- Use `print` with a `[command]` prefix for CLI progress output (no logging
  framework yet); never print a participant identifier.
- Each step reads only the previous steps' outputs, checks their manifests'
  hashes, writes `<name>.tmp/` and renames when complete, and records
  inputs (with sha256), settings, versions, git revision and findings in a
  manifest. `data.py`'s shared helpers do this (`require_raw_files`,
  `hash_raw_file`, `check_known_repairs`, `_finalize_output_dir`,
  `_write_manifest`, `_git_revision`, `_software_versions`, `_numerics`);
  manifests use the top-level keys `step`, `versions`, `numerics`,
  `git_revision`, `inputs`, `settings`, `outputs`, `findings`. Manifests
  written before `adni-portable-numerics` have no `numerics` block; their
  outputs were reproduced pinned on 2026-10-28.

## OpenSpec workflow

Non-trivial features go through OpenSpec (`openspec/changes/`, specs in
`openspec/specs/`): propose → apply → archive. Agent skills/commands for this
live in `.claude/`. Every proposal states what is out of scope and names
every scientific constant it introduces, with its value, before any run
(`openspec/config.yaml`).
