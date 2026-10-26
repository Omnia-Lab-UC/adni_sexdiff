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

Status (2026-10-26): scaffold only. Every step below is a stub whose body
raises `NotImplementedError`; its docstring in `data.py` states the inputs,
the outputs and the output contract. No data is in place. No scientific
constant is decided (see "Flag and ask"). Each step is implemented by its own
OpenSpec change, in order.

1. `clean` – metabo_adni per platform (`--platform {p180,nmr,all}`): the
   pinned release's `clean_files` pipeline with the options of the
   (undecided) `CLEAN_OPTIONS`, run in a working copy because metabo_adni
   changes into the data directory and writes its cleaned files there.
   Writes `results/cleaned/<platform>/`: metabo_adni's cleaned files under
   the names it gives them (participant × metabolite, keyed by `RID`;
   participant-level) and `clean_manifest.json` (versions, options, input
   file hashes, participant and metabolite counts before and after each
   metabo_adni step, findings; aggregate).
2. `cohort` – from `results/cleaned/` and the ADNI clinical tables in the
   data root: the baseline visit per participant, sex, the merged stage
   (`STAGE_LABELS` = CN / MCI / AD by the undecided `STAGE_RULE`), the
   covariates (`ANALYSIS_COVARIATES`, undecided; nothing imputed), the
   platform intersection (`COHORT_RULE`, undecided). Writes
   `results/cohort/`: `cohort.csv` (one row per participant;
   participant-level), `stage_counts.csv` (sex × stage counts per platform
   and for the intersection; aggregate, the only committed table) and
   `cohort_manifest.json`.
3. `export` – from `results/cleaned/` and `results/cohort/` only: the MOTCO
   blocks restricted to the cohort (`EXPORT_FEATURE_RULE`, undecided:
   which cleaned metabolites enter each block and on which scale),
   covariates exported, not applied. Writes `results/motco_input/`:
   `p180.csv`, `nmr.csv`, `metadata.csv` (`rid`, `sex`, `stage`),
   `covariates.csv` (participant-level), `features_<platform>.csv`
   (feature statuses; gitignored with the other CSVs) and `manifest.json`
   (hashes, n per sex × stage cell, feature counts; the only committed file).
   No step before `analyze` uses sex or stage to select features.
4. `analyze` – from `results/motco_input/` only: one
   `motco.analysis.analyze_trajectories` call (MOTCO ≥ 0.10.0; never
   assembled from `motco plsr` + `motco de`), group `sex`, stage `stage` in
   CN / MCI / AD order, the undecided `ANALYSIS_COVARIATES`,
   `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_RANK_FLOOR` (passed
   explicitly, checked against MOTCO's default before any input is read),
   MOTCO's other defaults not overridden. Writes `results/motco_analysis/`:
   MOTCO's `result.json`, `latent_scores.csv`, `pls_loadings.csv`,
   `stage_means.csv`, plus `analysis_metadata.csv`, `analysis_manifest.json`
   (hashes, settings, `n_jobs`, a `cli_equivalent`, versions, findings) and
   `summary.md`. `latent_scores.csv` and `analysis_metadata.csv` are
   participant-level.
5. `axis-diagnostics` – from `results/motco_input/`, `results/motco_analysis/`
   and `results/cohort/` only: Spearman and covariate-partial Spearman
   correlations of every latent component with the undecided
   `DIAGNOSTIC_VARIABLES`, the same for the first PCs of each z-scored
   block, the geometry shares along each component; rows at or above
   `DIAGNOSTIC_CORRELATION_THRESHOLD` flagged, no p-values. Writes
   `results/motco_diagnostics/` (`axis_correlations.csv`, `block_pcs.csv`,
   `geometry_shares.csv`, `diagnostics.md`, `diagnostics_manifest.json`; all
   aggregate). It reads sex and stage, so it is never a filter: its outputs
   feed no `export` or `analyze` run.
6. `report` – from the generated files only (`result.json`, `summary.md`,
   the manifests, `stage_counts.csv`, the diagnostics): writes
   `reports/motco-adni-<date>.md`, or with `--check` compares every number
   of an existing report with the generated files and fails naming the
   cell. Reports quote aggregate values only.

`README.md` documents the layout and the pipeline; keep it in sync when
behavior or defaults change.

## Hard constraints

### 1. ADNI is controlled-access (DUA): nothing participant-level is ever committed

- Never commit a raw ADNI file, a cleaned matrix, `cohort.csv`, a MOTCO
  input block, `metadata.csv`, `covariates.csv`, `latent_scores.csv`,
  `analysis_metadata.csv`, or any table with an `RID`, under any path,
  in any form (also not in a report, a proposal, a spike note, a test
  fixture, a docstring or a commit message).
- Committed outputs are aggregate only: `result.json`, `stage_means.csv`,
  `pls_loadings.csv`, manifests with hashes, `summary.md`,
  `stage_counts.csv` (group × stage counts), the diagnostics tables and the
  reports under `reports/`.
- `.gitignore` enforces this: `data/`, `results/cleaned/`,
  `results/cohort/*.csv` except `stage_counts.csv`,
  `results/motco_input/**/*.csv` except manifests,
  `results/**/latent_scores.csv`, `results/**/analysis_metadata.csv`,
  `results/**/*.tmp/`, `results/**/logs/`. The same list is
  `constants.PARTICIPANT_LEVEL_PATTERNS` and the filter of
  `scripts/sync_results.sh`. A change that adds a participant-level output
  extends all three in the same change, before the output exists. Before
  committing under `results/`, name every file you add and say why it is
  aggregate.
- Progress output, logs and manifests name counts and files, never
  participants: no `RID` in a print, a finding, a log or a manifest.

### 2. Where the data lives

- Data lives on the workstations and on `cluster.ing.uc.cl` only: never in a
  cloud service, never in a public bucket, never in a chat or an artifact.
- There is no download step: LONI needs a login, so the raw ADNI files are
  uploaded by hand into the data root. The canonical copy is
  `/home1/tgonza/adni_sexdiff/data` on the cluster; the data root is an
  explicit flag (`--data-root`) → `ADNI_DATA_ROOT` → `data/`. Machines
  differ only by this value.
- Data root layout: `<root>/Metabolomics/` is the archive as downloaded
  from LONI (dated file names such as `_10Jul2024`, data dictionaries,
  methods documents, the supplement zips with the p180 LOD workbooks
  extracted into `Metabolomics/p180/LOD/`, later layers such as
  `quant500/`); the flat top level of `<root>` holds the exact names
  metabo_adni expects as relative symlinks into that archive (the list is
  under "Data & domain notes"). Replicate a root with `rsync -a` (symlinks
  preserved); never rename the archive files.
- Only aggregate outputs move between machines, with
  `scripts/sync_results.sh` (rsync of `results/` excluding every
  participant-level file; pull by default, `--push` to reverse). Never copy
  cleaned matrices or MOTCO inputs between machines; each machine makes its
  own from its own data root.

### 3. Cleaning goes through metabo_adni

- Cleaning is metabo_adni's (PyPI, `tomszar/metabo_adni`), pinned to an
  exact version (`metabo_adni==0.5.8` in `pyproject.toml`,
  `constants.METABO_ADNI_VERSION`, checked at run time), never
  reimplemented here. Its QC cutoffs and transforms (`--mmc`, `--mpc`,
  `--cv`, `--icc`, `--log2`, `--zscore`, `--winsorize`,
  `--remove-moutliers`, `--residualize-meds`) are scientific choices
  (`CLEAN_OPTIONS`, undecided). A metabo_adni defect is reported upstream
  and the pin moved by a change, never patched or vendored here.

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
  listed under "Flag and ask" below. None is decided today; `constants.py`
  reserves their names in its docstring and defines none of them.
- Never set, change or default one of them in code, a flag or a script
  without a proposal. Never choose one from a result.

### 6. Reported runs and report numbers

- Reported runs use `n_jobs = 1` (`constants.REPORTED_N_JOBS`): MOTCO seeds
  one RRPP stream per worker, so another value changes the permutation
  draws. Another value is recorded as a finding and the run is not reported.
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

- `src/adni_sexdiff/cli.py` – argparse CLI (`build_parser`, `main`); thin
  layer that calls into `data.py` and prints `[command]`-prefixed progress
  messages.
- `src/adni_sexdiff/constants.py` – named constants: conventions (paths,
  environment variables, platforms, columns, output names, pins, the
  participant-level patterns) defined; scientific constants reserved by
  name only until a proposal defines them.
- `src/adni_sexdiff/data.py` – all logic: the six steps (stubs today),
  `resolve_data_root`, the version checks.
- `scripts/` – `sync_results.sh` (aggregate outputs between a workstation
  and the cluster). No sbatch scripts yet; they come with the first step
  that needs the cluster.
- `data/` – raw ADNI files, uploaded by hand; gitignored, never committed.
- `results/` – pipeline outputs; only the aggregate files named in
  constraint 1 are committed.
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
  `uv run adni-sexdiff <clean|cohort|export|analyze|axis-diagnostics|report> [options]`.
- Dependencies: `motco` (git tag, constraint 4), `metabo_adni==0.5.8`
  (constraint 3), `pandas`, `numpy`. Add dependencies with `uv add <pkg>`
  so `pyproject.toml` and `uv.lock` stay consistent.
- Data root: `--data-root` → `ADNI_DATA_ROOT` → `data/` (constraint 2).
- There is no test suite or linter configured yet. Verify changes by running
  the relevant CLI command or importing the function; say so explicitly when
  something could not be verified (real data is never available to an agent
  outside the workstations and the cluster).

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
  must be repaired the same way before it is put in the archive. The
  clean proposal states this rule. The clinical tables the cohort step reads
  (diagnosis, demographics, covariate sources) are named by the cohort
  proposal and uploaded the same way.
- `RID` is ADNI's participant key (`constants.PARTICIPANT_ID_COLUMN`). Any
  table that holds it is participant-level (constraint 1). The export's
  sample column is `rid`, the group column `sex`, the stage column `stage`
  with `STAGE_LABELS` CN / MCI / AD in trajectory order.
- Flag and ask before changing, and never set without a proposal
  (constraint 5); none is decided today:
  - `CLEAN_OPTIONS` – metabo_adni's cutoffs and transforms per platform.
  - `COHORT_RULE` – the baseline visit per participant, the platform
    intersection, exclusions; the predeclared counts the manifest checks.
  - `STAGE_RULE` – the ADNI diagnosis → CN / MCI / AD mapping and the
    merging of subtypes.
  - `ANALYSIS_COVARIATES` – set, order, coding and sources; missing policy
    `error`, nothing imputed.
  - `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA` – MOTCO's RRPP
    permutations, seed and rejection rule.
  - `ANALYSIS_RANK_FLOOR` – the latent-rank floor passed to MOTCO.
  - `EXPORT_FEATURE_RULE` – which cleaned metabolites enter each block and
    on which scale.
  - `DIAGNOSTIC_VARIABLES`, `DIAGNOSTIC_CORRELATION_THRESHOLD` – the axis
    diagnostics' variables and reporting flag.
  - `READING_RULES` – the binding reading rules of the report, carried from
    MOTCO's reports (`../MOTCO/docs/roadmap.md`): CV-selected rank beside
    `angle`; `angle`/`shape` non-rejections uninformative; a `delta`
    rejection a difference, not specifically of size; covariate block and
    feature filtering beside the results. Written into the analyze proposal
    before any run.
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
  `report`) run on the login node; `clean` and `analyze` through sbatch
  scripts that a later change adds under `scripts/` (none yet).
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
  manifest.

## OpenSpec workflow

Non-trivial features go through OpenSpec (`openspec/changes/`, specs in
`openspec/specs/`): propose → apply → archive. Agent skills/commands for this
live in `.claude/`. Every proposal states what is out of scope and names
every scientific constant it introduces, with its value, before any run
(`openspec/config.yaml`).
