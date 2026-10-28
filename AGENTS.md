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

Status (2026-10-28): `clean` (change `adni-metabolomics-clean`), `cohort`
(change `adni-cohort`), `export` (change `adni-export`), `analyze`
(change `adni-analyze`) and `axis-diagnostics` (change
`adni-axis-diagnostics`) are implemented, and so is the sensitivity step
`latent-sensitivity` (change `adni-latent-sensitivity`: the predeclared
`stage`-conditioned latent-adjustment arm, read beside the primary and
never replacing it). They run on a data machine; the cluster copy and
clone do not exist yet. A data machine is any of the user's machines whose
local participant-level files under `results/` (the export CSVs,
`cohort.csv`, the primary's `latent_scores.csv` and
`analysis_metadata.csv`) hash to the values the committed manifests
record; the hash checks pick it and no machine is named. Any machine with
a data root becomes one by a pinned rebuild from it (`clean` → `cohort` →
`export` → `analyze` into a scratch directory), a hash check of every
output the committed manifests record, and copying the participant-level
files into the gitignored paths under `results/`. The manifests written
before `adni-portable-numerics` record no machine, but their outputs
reproduce pinned on any machine. `report` is a stub whose body raises
`NotImplementedError`; its docstring in `data.py` states the inputs, the
outputs and the output contract. Decided scientific constants:
`CLEAN_OPTIONS`, `COHORT_RULE`, `STAGE_RULE`, `ANALYSIS_COVARIATES`,
`EXPORT_FEATURE_RULE`, the analysis settings (`ANALYSIS_PERMUTATIONS`,
`ANALYSIS_SEED`, `ANALYSIS_ALPHA` with `ANALYSIS_REJECTION_RULE`,
`ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`), `READING_RULES`, the
diagnostic constants (`DIAGNOSTIC_VARIABLES`,
`DIAGNOSTIC_CORRELATION_THRESHOLD`) and the sensitivity constants
(`LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`,
`LATENT_SENSITIVITY_READING_RULES`); every constant the six steps and the
sensitivity step need is decided (see "Flag and ask"). Each step is
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
   per component. It reads sex and stage, so it is never a filter: its
   outputs feed no `export` or `analyze` run, and no arm or variant is
   derived from a diagnostic value.
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
6. `report` – from the generated files only (`result.json`, `summary.md`,
   the manifests, `stage_counts.csv`, the diagnostics, and the sensitivity
   step's comparison, arm record and arm diagnostics under
   `results/motco_latent_sensitivity/`): writes
   `reports/motco-adni-<date>.md`, or with `--check` compares every number
   of an existing report with the generated files and fails naming the
   cell. Reports quote aggregate values only and carry
   `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES` wherever they
   quote the arm.

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
  `latent_sensitivity.md`, its manifest) and the reports under `reports/`.
  An arm's analysis directory follows the primary's rule: its
  `latent_scores.csv` and `analysis_metadata.csv` are participant-level,
  its other five files aggregate.
- `.gitignore` enforces this: `data/`, `results/cleaned/**` except
  `results/cleaned/*/clean_manifest.json`,
  `results/cohort/*.csv` except `stage_counts.csv`,
  `results/motco_input/**/*.csv` except manifests,
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
  holds the exact names the steps read (metabo_adni's and the cohort's) as
  relative symlinks into both (the list is under "Data & domain notes").
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
  `LATENT_SENSITIVITY_COVARIATE_ROLES`, `LATENT_SENSITIVITY_READING_RULES`;
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
  messages.
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
  `ANALYSIS_COVARIATES`).
- `src/adni_sexdiff/data.py` – all logic: the six steps (`clean`, `cohort`,
  `export`, `analyze` and `axis-diagnostics` implemented, `report` a stub)
  and the sensitivity step `latent-sensitivity` (`run_latent_sensitivity`,
  with the reference checks `_check_primary_reference` and
  `_check_cohort_manifest`, the comparison rows and
  `render_latent_sensitivity`), `resolve_data_root`, the version gates
  (`check_metabo_adni_version`, `check_motco_version`,
  `check_motco_rank_floor`), the raw-input helpers, the analysis input
  loader (shared by `analyze`, `axis-diagnostics` and
  `latent-sensitivity`), the shared analysis function
  (`_run_trajectory_analysis`: the body of `analyze`, which the arm calls
  with `latent_adjustment` as its one differing setting; the primary's
  bytes are its gate) and the summary renderer (arm-aware when the record
  carries `latent_adjustment`), the diagnostic statistics (`spearman`,
  `partial_spearman`, `block_principal_components`, `geometry_shares`,
  `block_loading_shares`), the chain checks (`_check_analysis_inputs`,
  whose hints name the command that wrote the analysis read,
  `_check_cohort_chain`) and `render_axis_diagnostics` (arm-aware), the
  numeric-state record (`_numerics_record`, `_numerics_finding`,
  `_numerics`), and the manifest / `.tmp` helpers every step reuses.
- `scripts/` – `sync_results.sh` (aggregate outputs between a machine
  and the cluster), `clean.sbatch` (`clean --platform all` on the cluster),
  `analyze.sbatch` (`analyze` on the cluster, no `--n-jobs`, so a reported
  run), `spike_raw_inventory.py` (the clean change's read-only spike),
  `spike_cohort_inventory.py` (the cohort change's read-only spike),
  `spike_export_inventory.py` (the export change's read-only spike; it
  reads the Nightingale dictionary for the name-mark cross-check, which
  `export` does not).
- `data/` – raw ADNI files, uploaded by hand; gitignored, never committed.
- `results/` – pipeline outputs; only the aggregate files named in
  constraint 1 are committed. `results/motco_latent_sensitivity/` holds the
  sensitivity step's `analysis/` (the arm, laid out as
  `results/motco_analysis/`), `comparison/` and `diagnostics/`.
- `reports/` – committed case-study reports (`motco-adni-<date>.md`),
  numbers pasted from generated outputs and checked by `report --check`.
- `openspec/` – OpenSpec change proposals/specs (see below).

## Environment & commands

- Python `>=3.12,<3.14`, managed with **uv** (`uv.lock` is committed).
- Setup: the Nix flake (`flake.nix`) provides Python 3.12 and uv (no R);
  its shell hook runs `uv sync --locked`. Enter it with direnv (`.envrc` →
  `use flake`) or `nix develop`. Python packages come from uv, not Nix.
  Outside the Nix shell numpy cannot load its native libraries; run
  commands through `nix develop -c ...` there.
- Run the CLI:
  `uv run adni-sexdiff <clean|cohort|export|analyze|axis-diagnostics|latent-sensitivity|report> [options]`.
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
  `LATENT_SENSITIVITY_READING_RULES`; every constant the six steps and the
  sensitivity step need is decided:
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
    `EXPORT_EXPECTED_COUNTS`. The sensitivity variants (all 245 NMR
    columns, the raw scale, `log2(x + 1)`, the generalized log) are a
    later change, registered after the primary analysis.
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
  data machine's: statistics, p-values, rank). `latent-sensitivity` runs
  there the same way once the clone exists (pinned, so it must reproduce
  the committed hashes). Both scripts export
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
