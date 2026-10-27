# adni_sexdiff

Sex × stage (CN / MCI / AD) trajectory comparison on ADNI serum metabolomics
(Biocrates p180 and Nightingale NMR) with [MOTCO](https://github.com/tomszar/MOTCO):
the first MOTCO application at a well-powered design (n ≈ 1,300). Later ADNI
layers (lipidomics, proteomics, methylation) may be added as separate blocks.

**Status: `clean`, `cohort`, `export`, `analyze` and `axis-diagnostics`
implemented** (changes `adni-metabolomics-clean`, `adni-cohort`,
`adni-export`, `adni-analyze` and `adni-axis-diagnostics`) and run on the
workstation; `report` is a stub that raises `NotImplementedError`. The
statistical choices made so far are `CLEAN_OPTIONS`, `COHORT_RULE`,
`STAGE_RULE`, `ANALYSIS_COVARIATES`, `EXPORT_FEATURE_RULE`, the analysis
settings (`ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA`,
`ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`), `READING_RULES` and
the diagnostic constants (`DIAGNOSTIC_VARIABLES`,
`DIAGNOSTIC_CORRELATION_THRESHOLD`); every constant the six steps need is
decided.
`AGENTS.md` holds the conventions and the hard constraints and is the single
source of truth.

**ADNI is controlled-access (DUA).** Nothing participant-level is ever
committed: no raw file, no cleaned matrix, no cohort table, no MOTCO input
block, no `latent_scores.csv`, no `analysis_metadata.csv`, no table with an
`RID`. `.gitignore` enforces it and `scripts/sync_results.sh` moves only
aggregate outputs between machines. Raw ADNI files are uploaded by hand to the
data root (`ADNI_DATA_ROOT`, default `data/`); there is no download step.

Data root layout: `Metabolomics/` holds the archive as downloaded from LONI
(dated file names, data dictionaries, the p180 LOD workbooks extracted into
`Metabolomics/p180/LOD/`) and `Clinical/` the clinical tables under their
original names (the QT-PAD ADNIMERGE freeze
`ADNI_adnimerge_20170629_QT-freeze.csv`). The top level holds the exact names
the steps read, as relative symlinks into both (for example
`ADNI_adnimerge_20170629_QT-freeze.csv -> Clinical/ADNI_adnimerge_20170629_QT-freeze.csv`).
Replicate a root with `rsync -a` (symlinks preserved); never rename the
archive files.

Project layout:

```
.
├── data/            # raw ADNI files, uploaded by hand: LONI archive under Metabolomics/, clinical tables under Clinical/, the names the steps read as symlinks (gitignored)
├── reports/         # committed case-study reports (numbers pasted from results/, checked by script)
├── results/         # pipeline outputs; only aggregate files are committed (see .gitignore)
├── scripts/         # sync_results.sh (aggregate outputs between workstation and cluster), clean.sbatch and analyze.sbatch (clean and analyze on the cluster), spike_*_inventory.py (the changes' read-only spikes)
├── src/
│   └── adni_sexdiff/
│       ├── cli.py         # argparse CLI: clean, cohort, export, analyze, axis-diagnostics, report
│       ├── constants.py   # conventions; scientific constants enter through OpenSpec proposals only
│       └── data.py        # pipeline steps (clean, cohort, export, analyze and axis-diagnostics implemented; report a stub with its output contract)
├── openspec/        # change proposals and specs
├── flake.nix        # Python 3.12 + uv; the shell hook runs `uv sync --locked`
├── pyproject.toml   # package adni_sexdiff, CLI adni-sexdiff (uv, uv.lock committed)
├── LICENSE
└── README.md
```

Pipeline (each step reads the previous step's outputs only):

1. `clean` – metabo_adni per platform → `results/cleaned/<platform>/` (below)
2. `cohort` – one baseline row per participant (sex, merged stage,
   covariates), the platform sets and their intersection, sex × stage counts
   → `results/cohort/` (below)
3. `export` – the MOTCO blocks under the feature rule, metadata and
   covariates of the analysis cohort → `results/motco_input/` (below)
4. `analyze` – one `motco.analysis.analyze_trajectories` call at the
   predeclared settings → `results/motco_analysis/` (below)
5. `axis-diagnostics` – what the latent components and the block axes
   correlate with, the geometry shares and the block composition per
   component → `results/motco_diagnostics/` (below)
6. `report` – the case-study report from the generated files, or a check of
   one against them → `reports/`

Quick start:

```
direnv allow            # or: nix develop   (Python 3.12, uv, `uv sync --locked`)
uv run adni-sexdiff --help
uv run adni-sexdiff clean --platform all
uv run adni-sexdiff cohort
uv run adni-sexdiff export
uv run adni-sexdiff analyze
uv run adni-sexdiff axis-diagnostics
```

## `clean`

```
uv run adni-sexdiff clean [--platform {p180,nmr,all}] [--data-root DIR] [--out-dir DIR] [--force]
```

Cleans each platform with metabo_adni 0.5.8 (`--platform all`: p180, then
NMR, each in its own directory). metabo_adni has no library entry point: its
command `clean_files` (`metabo_adni.__main__.main`) calls its QC functions in
a fixed order. `clean` calls the same functions in the same order,
in-process, so that it can count participants × metabolites after each step,
and records the equivalent `clean_files` command line in the manifest. The
installed metabo_adni is checked against the pin before any file is read.

Options (`CLEAN_OPTIONS`, decided by the change `adni-metabolomics-clean`):
metabo_adni's QC at its default cutoffs, its merge, and none of its
transforms.

| option | p180 | NMR |
|---|---|---|
| missing metabolites (`--mmc`) | 0.2 | 0.2 |
| missing participants (`--mpc`) | 0.2 | 0.2 |
| coefficient of variation (`--cv`) | 0.2 | not applied (p180 only) |
| intra-class correlation (`--icc`) | 0.65 | not applied (p180 only) |
| `--merge` | on | on |
| `--log2`, `--zscore`, `--winsorize`, `--remove-moutliers`, `--residualize-meds` | off | off |

The fasting file is `BIOMARK.csv`; p180 missing values are imputed from the
four LOD workbooks, NMR missing values at half the minimum (metabo_adni's
rules). Values stay on the scale the platform delivers: the pseudo-count, log
and scaling belong to the export step's feature rule.

Inputs: for p180 the four concentration files, the four LOD workbooks and
`BIOMARK.csv`; for NMR `ADNINIGHTINGALE2.csv` and `BIOMARK.csv`; nothing
else (not the medication table, not a clinical table). Every name is checked
before work starts, and every file is hashed through its data-root symlink.
LONI's `ADMCDUKEP180UPLCADNI2GO.csv` lacks its closing quote and the archive
copy carries a hand-applied repair (`AGENTS.md`): `clean` recognises the
repaired bytes by hash and names the repair in the manifest, stops before
writing anything when it finds LONI's unrepaired bytes, and records any other
unknown hash (a fresh LONI download) as a finding. It never edits the
archive.

metabo_adni changes into the directory it reads and writes its output there,
so the inputs are copied into `results/cleaned/<platform>.tmp/work/`; the
data root is never written. Everything metabo_adni prints (it lists
participant identifiers) goes to the log, never to the terminal. The
directory is renamed to `results/cleaned/<platform>/` when complete; an
existing one stops the step unless `--force` is given.

Outputs per platform:

| file | content | committed / synced |
|---|---|---|
| `P180.csv` / `NMR.csv` | the merged table, participant × metabolite, keyed by `RID` | no (participant-level) |
| `p180_runs.csv` (p180) | `RID`, `run` (`ADNI1` or `ADNI2GO` kit files) | no (participant-level) |
| `logs/metabo_adni.log` | metabo_adni's printed output | no (participant-level) |
| `clean_manifest.json` | versions, git revision, options and `cli_equivalent`, inputs with sha256 and repair, raw inventory, cells after every step, imputed points, value summary, runs, output hashes, expected and observed counts with deviations, findings, metabo_adni 0.5.8's known upstream behaviours with their counts | yes (aggregate, no `RID`) |

The manifest checks the counts predeclared from the change's spike
(`CLEAN_EXPECTED_COUNTS`): p180 1592 × 133 (746 `ADNI1`, 846 `ADNI2GO`, 1651
imputed points) and NMR 1504 × 245 (155 imputed points, 41 zeros in 3
metabolites). A deviation is a finding, printed and recorded; it never stops
the step and never changes an option.

On the cluster, `scripts/clean.sbatch` runs `clean --platform all`
(partition `512x1024`, 2 CPUs, 8 GB, 2 h, `ADNI_DATA_ROOT=/home1/tgonza/adni_sexdiff/data`,
Slurm logs in `results/cleaned/logs/`). It needs the repository clone and the
cluster copy of the data root first (`AGENTS.md`, constraint 7).

## `cohort`

```
uv run adni-sexdiff cohort [--cleaned-dir DIR] [--data-root DIR] [--out-dir DIR] [--force]
```

Builds one baseline row per participant from the outputs of `clean` and the
clinical tables, under the three constants decided by the change
`adni-cohort`:

- `COHORT_RULE`. The clinical table is the QT-PAD ADNIMERGE freeze
  `ADNI_adnimerge_20170629_QT-freeze.csv` (the file of the 2022 study), and a
  participant's clinical values come from its `VISCODE` `bl` row. A cleaned
  participant enters a platform's set when every raw record of the
  participant on that platform has visit `bl` (`VISCODE` in the ADNI-GO/2
  p180 files, `VISCODE2` in `ADNINIGHTINGALE2.csv`; the ADNI-1 p180 files
  have no visit column and count as baseline) and the clinical table has its
  `bl` row. The analysis cohort is the intersection of the p180 and NMR sets.
  There is no other exclusion, and none depends on sex, stage or a covariate.
- `STAGE_RULE`. `DX.bl` onto CN / MCI / AD: `CN` and `SMC` → CN, `EMCI` and
  `LMCI` → MCI, `AD` → AD. `DX.bl` is kept beside the stage.
- `ANALYSIS_COVARIATES`, in this order; missing policy `error`, nothing
  imputed:

| name | source | coding |
|---|---|---|
| `age` | `AGE` | numeric, years |
| `education` | `PTEDUCAT` | numeric, years |
| `apoe4` | `APOE4` | categorical, `0` / `1` / `2` |
| `phase` | `ORIGPROT`: `ADNI1` → `ADNI1`; `ADNIGO`, `ADNI2` → `ADNI2GO` | categorical, 2 levels |
| `statin` | medication table, `HMG CoA reductase inhibitors` on the `sc` row: filled `1`, empty `0` | categorical, `0` / `1` |

Sex is `PTGENDER` (`Female` / `Male`). `apoe4` and `statin` are written as
integers; their categorical coding lives in `ANALYSIS_COVARIATES` and is what
`analyze` declares to MOTCO.

Inputs: from `results/cleaned/`, the participants of `P180.csv` and `NMR.csv`
and the runs of `p180_runs.csv`, each file checked against the sha256 its
`clean_manifest.json` records; from the data root, the ADNIMERGE freeze, the
medication table `ADMCPATIENTDRUGCLASSES_20170512.csv` and the visit columns
of `ADMCDUKEP180UPLCADNI2GO.csv`, `ADMCDUKEP180FIAADNI2GO.csv` and
`ADNINIGHTINGALE2.csv`, through the same raw-input checks as `clean` (names
present, hashes through the symlinks, the known repair recognised, an unknown
hash a finding). Nothing else is read.

Anything outside the rules stops the step before anything is written, naming
the file or column and a count, never a participant: a clean output whose
hash differs from its manifest, an absent column, more than one `bl` row or
`sc` medication row for a participant, and among the participants of the
platform sets a `DX.bl` outside the stage map, a `PTGENDER` other than
`Female` / `Male`, an `ORIGPROT` outside the phase map, a covariate value
outside its levels or a missing covariate value (including no `sc`
medication row).

Outputs in `results/cohort/` (written as `results/cohort.tmp/` and renamed
when complete; an existing directory stops the step unless `--force` is
given):

| file | content | committed / synced |
|---|---|---|
| `cohort.csv` | one row per participant of either platform set: `rid`, `sex`, `stage`, `dx_bl`, `protocol`, `age`, `education`, `apoe4`, `phase`, `statin`, `visit`, `p180`, `nmr`; the intersection is the rows with both flags | no (participant-level) |
| `stage_counts.csv` | `set`, `sex`, `stage`, `dx_bl`, `phase`, `n`: sex × stage with margins for the p180 set, the NMR set and the intersection, and the intersection's sex × stage × `DX.bl` × phase cells | yes (aggregate) |
| `cohort_manifest.json` | versions, git revision, the clean manifests and outputs with their hashes, the data-root inputs with target, sha256 and repair, the three rules as applied, visit sets, cascade and sex × stage per set, composition, agreement of `DX` with the stage, phase against the p180 run, covariate descriptives by sex × stage, expected and observed counts with deviations, output hashes, findings | yes (aggregate, no `RID`) |

The manifest checks the counts predeclared from the change's spike
(`COHORT_EXPECTED_COUNTS`):

| set | n | Female CN / MCI / AD | Male CN / MCI / AD |
|---|---|---|---|
| p180 | 1592 | 254 / 329 / 140 | 230 / 470 / 169 |
| NMR | 1503 | 237 / 310 / 126 | 223 / 449 / 158 |
| intersection | 1501 | 237 / 310 / 125 | 223 / 448 / 158 |

`cohort.csv` has 1594 rows (91 p180-only, 2 NMR-only). One cleaned NMR
participant is excluded because their only NMR sample is from screening.
`DX` on the `bl` row agrees with the stage for 1498 of the intersection,
differs for 2 and is missing for 1. Phase equals the p180 run for every
participant, and there are 704 statin users. A deviation is a finding,
printed and recorded; it never stops the step and never changes a rule. An
unknown input hash and a phase that differs from the p180 run are findings
too.

`cohort` is a light step: on the cluster it runs on the login node after
`clean`, and it needs the cluster copy of the data root including
`Clinical/` and its symlink.

## `export`

```
uv run adni-sexdiff export [--cleaned-dir DIR] [--cohort-dir DIR] [--out-dir DIR] [--force]
```

Builds the MOTCO blocks of the analysis cohort from the outputs of `clean`
and `cohort` only, under `EXPORT_FEATURE_RULE`, decided by the change
`adni-export`. The rule has two parts:

- Membership. A block holds the measured concentrations of its platform,
  each once. Every cleaned p180 metabolite enters (133 µM concentrations).
  A cleaned NMR column enters if it is a concentration (165 columns: the 98
  lipoprotein-subclass measures and 67 other concentrations); the 80
  columns that are deterministic functions of other columns of the block
  are excluded with status `derived`, recognised by name: the 72
  percentages (`_PCT`), the 4 ratios (`_BY_`), the degree of unsaturation
  (`UNSATURATION`) and the 3 particle sizes (`_SIZE`). The change's spike
  checked the marks against the Nightingale dictionary's units for all 245
  columns.
- Scale. One rule for both blocks: `log2(x + floor)`, the floor of a
  metabolite being its 5 % quantile over the exported participants (linear
  interpolation), computed without sex, stage or a covariate and recorded
  per feature. A non-positive floor stops the step. MOTCO's unit transform
  is `identity`; MOTCO z-scores every feature itself. Nothing is imputed,
  replaced, winsorized or removed, and nothing is centred per run.

The exported participants are the rows of `cohort.csv` with both platform
flags, in `cohort.csv` order (n = 1501). Covariates are copied, not
applied: adjustment is MOTCO's. Sex and stage are read only to write
`metadata.csv` and to count cells; the blocks and the feature tables are
byte-identical under permuted labels.

Inputs: `P180.csv` and `NMR.csv` from `results/cleaned/`, each checked
against the sha256 its `clean_manifest.json` records; `cohort.csv` from
`results/cohort/`, checked against `cohort_manifest.json`, whose recorded
clean hashes must equal the clean manifests' (a cohort built from an
earlier clean output stops the step, naming the file and `cohort`). No
data-root file and nothing else is read.

Anything outside the contract stops the step before anything is written,
naming the file, column or platform and a count, never a participant: an
absent column, a duplicated `rid`, a `sex` or `stage` outside its values, a
missing covariate value, a cohort participant absent from a cleaned table,
a missing cleaned cell, a non-positive floor, a non-finite exported cell.

Outputs in `results/motco_input/` (written as `results/motco_input.tmp/`
and renamed when complete; an existing directory stops the step unless
`--force` is given; reruns on the same inputs are byte-identical):

| file | content | committed / synced |
|---|---|---|
| `p180.csv`, `nmr.csv` | `rid`, then the kept metabolites under their cleaned names in cleaned-column order, on the rule's scale (1501 × 133 and 1501 × 165) | no (participant-level) |
| `metadata.csv` | `rid`, `sex`, `stage` | no (participant-level) |
| `covariates.csv` | `rid`, `age`, `education`, `apoe4`, `phase`, `statin`, copied from `cohort.csv` unchanged | no (participant-level) |
| `features_p180.csv`, `features_nmr.csv` | one row per cleaned column: family, status (`kept` / `derived`), zero cells, median, floor, floor over median, skew raw and transformed, largest \|z\| transformed, phase `d` (the transformed-scale columns empty for derived rows) | no (aggregate per feature, gitignored with the other CSVs, regenerable) |
| `manifest.json` | versions, git revision, inputs with hashes and the chain check, the rule as applied, block order and columns, group and stage values, the covariate codings copied from the cohort manifest, `covariates_applied` false, counts (participants, sex × stage, features per status and family, zero cells, floors not positive, non-finite cells, missing covariate values, block shares, per block the distribution-shape counts, the spectrum and the phase offset), expected and observed counts with deviations, output hashes, findings | yes (aggregate, no `RID`) |

The manifest checks the counts predeclared from the change's spike
(`EXPORT_EXPECTED_COUNTS`): 1501 participants (Female CN / MCI / AD
237 / 310 / 125, Male 223 / 448 / 158); p180 133 cleaned, 133 kept; NMR
245 cleaned, 165 kept, 72 / 4 / 1 / 3 derived; 41 zero cells in 3 NMR
metabolites (three ketone bodies, which the floor handles), no non-positive
floor, no non-finite cell, no missing covariate value; 80 p180 and 0 NMR
metabolites with a phase offset |d| above 1. A deviation is a finding,
printed and recorded; it never stops the step and never changes the rule.

The p180 run offset is recorded, not corrected. On the rule's scale the
standardized mean difference between phases (ADNI-1 against ADNI-GO/2,
which equals the p180 run for every cohort participant) has median |d| 1.12
over the 133 p180 metabolites, 80 above 1, and the block's first principal
component correlates 0.73 with phase; for NMR, assayed in one batch, 0.21,
0 and 0.13. The runs differ in stage composition (EMCI and SMC exist only in
ADNI-GO/2), so per-run centering would move stage signal between runs;
`phase` is exported as a covariate and the analyze proposal decides how it
enters MOTCO. The blocks enter MOTCO 0.10.0 unweighted: p180 holds
133 / 298 of the joint features and NMR 165 / 298; the manifest records the
shares.

`export` is a light step: on the cluster it runs on the login node after
`cohort`. Each machine builds its own blocks from its own data root; only
`manifest.json` is synced.

## `analyze`

```
uv run adni-sexdiff analyze [--input-dir DIR] [--out-dir DIR] [--n-jobs N] [--force]
```

Runs the covariate-adjusted MOTCO comparison of the female and male
sex × stage trajectories on the exported blocks: one
`motco.analysis.analyze_trajectories` call (never assembled from `motco plsr`
+ `motco de`), at the settings decided by the change `adni-analyze` before
any run. Each is a constant, never a flag:

| setting | constant | value |
|---|---|---|
| RRPP permutations | `ANALYSIS_PERMUTATIONS` | 9999 (the p-value is `(1 + b) / (1 + B)`, exact in size at any count; the count sets the resolution, 0.0001) |
| RRPP seed | `ANALYSIS_SEED` | 20261027 |
| rejection | `ANALYSIS_ALPHA`, `ANALYSIS_REJECTION_RULE` | α = 0.05, rejected when `p <= alpha` |
| latent-rank floor | `ANALYSIS_RANK_FLOOR` | 2 (`min_components`, MOTCO's validated default, passed explicitly) |
| latent adjustment | `ANALYSIS_LATENT_ADJUSTMENT` | none for the primary (the covariate-blind basis); the `stage`-conditioned adjustment is the predeclared sensitivity arm of the next change, `adni-latent-sensitivity` |
| covariates | `ANALYSIS_COVARIATES` | `age`, `education` numeric; `apoe4`, `phase`, `statin` categorical (`ANALYSIS_CATEGORICAL_COVARIATES`); additive, missing policy `error` |
| everything else | MOTCO's defaults, read back from the record | net-displacement orientation, double CV (4 outer × 3 inner folds, 5 repeats, up to 20 components, random state 1203), no forced rank, no attribution, transform `identity`, group order `Female`, `Male`, stage order `CN`, `MCI`, `AD` |

Gates, before any input is read: the installed MOTCO must be at least
`ANALYSIS_MOTCO_MIN_VERSION` (0.10.0) and MOTCO's default rank floor must
equal `ANALYSIS_RANK_FLOOR` (a MOTCO whose default moved stops the run
instead of changing the primary); either stops naming both values.

Inputs: `p180.csv`, `nmr.csv`, `metadata.csv` and `covariates.csv` from
`results/motco_input/`, each checked against the sha256 `manifest.json`
records, and the manifest itself (block columns, covariate codings,
counts). Nothing else is read. Before anything is written the step checks
that the four tables carry the same `rid` column in the same order, that
the column sets match the contract and the manifest's block columns, that
`sex` and `stage` are within their values, that each categorical covariate
is within its levels and that no covariate value or block cell is missing;
a failure names the file or column and a count, never a participant.

How `phase` enters: as a covariate of the stage means, additively with the
other four. The design has six columns (`age`, `education`, `apoe4[1]`,
`apoe4[2]`, `phase[ADNI2GO]`, `statin[1]`; reference levels `0`, `ADNI1`,
`0`) and the LS-means are evaluated at the pooled covariate mean, so the
stage means are within-phase contrasts at the pooled phase proportion.
The run offset itself is not corrected (`export`), the adjustment has no
sex × covariate or stage × covariate term, and the latent space of the
primary is built without the covariates; the `stage`-conditioned latent
adjustment is the predeclared sensitivity arm, run by the next change
after `axis-diagnostics`.

The metadata table the model sees is `analysis_metadata.csv` parsed back
exactly as `motco analyze --metadata` parses it, so the manifest's
`cli_equivalent` reproduces the run with MOTCO's CLI (checked on the
workstation: the statistics, p-values, null summaries and rank are equal
and `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` are
byte-identical).

Outputs in `results/motco_analysis/` (written as
`results/motco_analysis.tmp/` and renamed when complete; an existing
directory stops the step unless `--force` is given; reruns on the same
inputs, MOTCO release and `n_jobs` give equal statistics, p-values and
rank and byte-identical CSVs):

| file | content | committed / synced |
|---|---|---|
| `result.json` | MOTCO's record: statistics, p-values, null summaries, the configuration spectrum, the latent block (rank, selection mode, `cv_mean_auroc`), the design, the covariate block, the blocks, the settings and software | yes (aggregate) |
| `latent_scores.csv` | the per-participant PLS scores, keyed by `rid` | no (participant-level) |
| `pls_loadings.csv` | `block`, `feature`, one column per component | yes (aggregate) |
| `stage_means.csv` | the fitted LS-mean per sex × stage in latent coordinates | yes (aggregate) |
| `analysis_metadata.csv` | `rid`, `sex`, `stage`, the five covariates, one row per exported participant in export order | no (participant-level) |
| `analysis_manifest.json` | versions (MOTCO, scikit-learn among them), git revision, the inputs with observed and recorded hashes and the export manifest's hash and revision, every setting by constant name, `n_jobs`, the covariate block from the record, the MOTCO defaults used, the latent adjustment with the predeclared arm, `cli_equivalent`, counts, expected and observed counts with deviations, output hashes with a participant-level flag, findings | yes (aggregate, no `RID`) |
| `summary.md` | generated from `result.json`: the statistics with p-values, rejection and null summaries, the CV-selected rank, floor and eigengap beside `angle`, the reading of each status, the cell sizes, the latent and covariate blocks, the export context and `READING_RULES` verbatim | yes (aggregate) |

The manifest checks the counts predeclared from the export and cohort
manifests (`ANALYSIS_EXPECTED_COUNTS`): 1501 participants (Female
CN / MCI / AD 237 / 310 / 125, Male 223 / 448 / 158), 133 + 165 = 298
features, the six design columns, the level counts (`apoe4` 810 / 542 /
149, `phase` 684 / 817, `statin` 797 / 704), 0 dropped, CV rank selection
at floor 2, 9999 permutations. A deviation is a finding, printed and
recorded; it never stops the step and never changes a setting. Findings
also record `n_jobs` other than 1, a CV-selected rank equal to the floor
(the floor is binding), fewer CV repeats completed than requested, a
non-finite statistic or p-value and a MOTCO default that differs from the
one the proposal states.

`--n-jobs`: MOTCO seeds one RRPP stream per worker, so another value
changes the permutation draws (the p-values and null summaries; the
statistics, rank, scores and loadings do not change). Reported runs use
`n_jobs = 1` (`REPORTED_N_JOBS`); another value is a finding and the run
is not reported.

Reading rules (`READING_RULES`, printed verbatim in `summary.md` and
binding for every report, sensitivity and diagnostic), in brief: the
primary stays primary and an arm's differing status is dependence on that
arm's setting; the CV-selected rank, the floor, the eigengap and the null
summary are read beside `angle`; `angle` and `shape` non-rejections are
uninformative (no power statement exists at this design); a `delta`
rejection is a difference, not specifically of size; the covariate block,
the p180 run offset, the block shares and the feature rule are read beside
the results; reported runs use `n_jobs = 1`; no result changes a constant.

On the cluster, `scripts/analyze.sbatch` runs `analyze` (partition
`512x1024`, 1 CPU, 4 GB, 1 h, no `--n-jobs`, so a reported run; Slurm logs
in `results/motco_analysis/logs/`) after `export` on the login node; pull
the aggregate outputs with `scripts/sync_results.sh` and compare the
manifests (statistics, p-values, rank; a floating-point difference across
machines is recorded, not a gate).

## `axis-diagnostics`

```
uv run adni-sexdiff axis-diagnostics [--input-dir DIR] [--analysis-dir DIR] [--cohort-dir DIR] [--out-dir DIR] [--force]
```

Measures, from the kept outputs only, what each latent component of the
analysis and each block's leading principal axes correlate with, how much
of the sex × stage geometry lies along each component and which block
carries it. It reads `results/motco_input/` (`p180.csv`, `nmr.csv`,
`metadata.csv`, `covariates.csv`, each checked against the sha256
`manifest.json` records; the manifest's block columns, covariate codings
and recorded phase offset), `results/motco_analysis/` (`result.json`,
`latent_scores.csv`, `stage_means.csv`, `pls_loadings.csv`,
`analysis_manifest.json`) and `results/cohort/` (`cohort.csv`,
`cohort_manifest.json`), and no data-root file or cleaned table. It takes
seconds on a workstation and runs wherever the analysis outputs are.

Chain checks, before anything is written (a failure names the file and
both hashes or both counts and the step to rerun, never a participant):
every input hash the analysis manifest records equals the export file's
sha256 now, and so does the export manifest's; the `pls_` column count of
`latent_scores.csv`, `stage_means.csv` and `pls_loadings.csv` equals the
record's selected rank; `stage_means.csv` holds one row per sex × stage;
`pls_loadings.csv` holds every exported feature once; `latent_scores.csv`
lists exactly the exported participants; `cohort.csv` hashes to its
manifest's record, `cohort_manifest.json` to the export manifest's record,
and the rows with both platform flags are the exported participants in
export order.

Variables (`DIAGNOSTIC_VARIABLES`, decided by the change
`adni-axis-diagnostics` before any run and never chosen or extended from
a result), in this order; a value outside its levels stops the step naming
the column and a count:

| variable | source | derivation |
|---|---|---|
| `age`, `education` | `covariates.csv` | as exported (years) |
| `apoe4` | `covariates.csv` | ε4 allele count 0 / 1 / 2, read as ordinal |
| `phase` | `covariates.csv` | 1 for `ADNI2GO`, 0 for `ADNI1` (the p180 run; the design column `phase[ADNI2GO]`) |
| `statin` | `covariates.csv` | 1 for a statin user at `sc`, 0 otherwise |
| `stage` | `metadata.csv` | ordinal CN 0, MCI 1, AD 2 |
| `male` | `metadata.csv` | 1 for Male, 0 for Female |
| `dx_bl` | `cohort.csv` | ordinal CN 0, SMC 1, EMCI 2, LMCI 3, AD 4: ADNI's enrollment gradient, which `STAGE_RULE` merges; SMC and EMCI exist only in ADNI-GO/2, so a phase axis is also a `dx_bl` axis and the partial correlation has to show which it is |

Statistics (each defined once in `data.py` and written into the manifest):

- Spearman ρ over the pairwise-complete participants (undefined with fewer
  than three, or a constant);
- the partial Spearman ρ given the six design columns of the record
  (`DIAGNOSTIC_CONDITIONING_COLUMNS`: `age`, `education`, `apoe4[1]`,
  `apoe4[2]`, `phase[ADNI2GO]`, `statin[1]`, built from `covariates.csv`
  with the export's codings and checked by name and by column mean against
  the record's `design_columns` and `reference_row`, so the partial reads
  as what the model's adjustment leaves): the Spearman correlation of the
  OLS residuals of both variables on an intercept and the design;
  undefined for a covariate itself;
- the first three principal components of each z-scored block
  (`DIAGNOSTIC_N_BLOCK_PCS`; population SD, SVD, each sign fixed so that
  its largest loading is positive) with their variance shares, and pc1's
  Spearman with `phase` beside the Pearson value the export recorded (a
  cross-check with no agreement threshold);
- the geometry shares from `stage_means.csv`: per component, the share of
  the squared length of each sex's net displacement (AD minus CN, what
  `angle` reads), of the per-stage sex differences (Female minus Male) and
  of the stage-centred sex differences; the shares of a quantity sum to 1;
- the block composition of each component: the share of its squared
  `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored
  joint features; the blocks enter unweighted, 133 / 298 and 165 / 298)
  held by each block, summing to 1.

A correlation is flagged when |ρ| ≥ `DIAGNOSTIC_CORRELATION_THRESHOLD`
(0.3, decided with the variables), raw and partial separately. The flag is
a reporting threshold on magnitude: no p-value is attached to any
correlation (at n = 1501 the sampling SD of ρ under independence is about
0.026, so a flag lies far outside sampling noise), and it is not an
adoption rule: nothing is chosen from a flagged row.

Outputs in `results/motco_diagnostics/` (written as
`results/motco_diagnostics.tmp/` and renamed when complete; an existing
directory stops the step unless `--force` is given; two runs on the same
inputs give byte-identical CSVs and `diagnostics.md`). Every file is per
component, per block or per variable, holds no `rid`, and is committed:

| file | content |
|---|---|
| `axis_correlations.csv` | per latent component × variable: `component`, `component_sd`, `variable`, `source`, `n`, `spearman`, `n_partial`, `partial_spearman`, `flag_raw`, `flag_partial` (64 rows at rank 8) |
| `block_pcs.csv` | the same for the first three PCs of each block, with `block` and `variance_share` (48 rows) |
| `geometry_shares.csv` | `quantity`, `component`, `value` (the signed component of a single vector; empty for the summed quantities), `along`, `total`, `share` (32 rows at rank 8) |
| `components.csv` | per component: `sd`, `loading_share_p180`, `loading_share_nmr`, `n_flagged_raw`, `n_flagged_partial`, `top_variable`, `top_spearman` (8 rows) |
| `diagnostics.md` | what the tables are and are not, the flagged rows first (latent components, then block PCs, by \|ρ\|), the component summary, the variable × component table, the block PCs beside the export's recorded phase offset, the geometry shares, the analysis read, the findings and `READING_RULES` verbatim |
| `diagnostics_manifest.json` | versions, git revision, the twelve inputs with sha256 and the chain checks, the analysis read (manifest hash, latent adjustment, `n_jobs`, rank, whether it is the primary), the variables with sources and derivations, the threshold, the conditioning columns, the definition of every statistic, the counts, the predeclared `DIAGNOSTICS_EXPECTED_COUNTS` beside them with deviations, output hashes, findings |

The manifest checks the counts predeclared from the export, cohort and
analysis manifests (`DIAGNOSTICS_EXPECTED_COUNTS`): 1501 participants and
the sex × stage cells, the eight variables, the six conditioning columns,
133 and 165 features with three PCs each, and, for the primary, rank 8 by
CV, no latent adjustment, `n_jobs` 1 and the row counts 64 / 48 / 32 / 8.
A deviation is a finding, printed and recorded; it never stops the step
and never changes a constant. Findings also record an analysis read whose
`n_jobs` is not 1 (its draws are not the reported ones; the scores are
unaffected), an analysis that is not the primary, a variable that is
constant or has fewer than three complete rows, and, per component, the
flagged variables as counts and names.

Running on an arm: `--analysis-dir` and `--out-dir` let a sensitivity
change (next: `adni-latent-sensitivity`, the `stage`-conditioned latent
arm) run the same diagnostic on an analysis directory that mirrors the
primary's. The manifest then records `is_primary` false, the `primary`
and `rows` expectations are skipped and a finding names the directory and
the adjustment. No other flag; no setting is a flag.

The diagnostic reads sex and stage, so it is never a filter: no `export`
or `analyze` run reads `results/motco_diagnostics/`, and arms and variants
are predeclared in a change proposal, never derived from a diagnostic
value. An axis correlated with a variable is a finding about the
measurement space of the primary analysis, not a reinterpretation of its
statistics or p-values; `diagnostics.md` prints `READING_RULES` verbatim
and the primary stays primary.

Dependencies: `motco` (git tag `v0.10.0`, via `[tool.uv.sources]`),
`metabo_adni==0.5.8` (cleaning, never reimplemented here), `pandas`, `numpy`.
