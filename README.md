# adni_sexdiff

Sex × stage (CN / MCI / AD) trajectory comparison on ADNI serum metabolomics
(Biocrates p180 and Nightingale NMR) with [MOTCO](https://github.com/tomszar/MOTCO):
the first MOTCO application at a well-powered design (n ≈ 1,300). Later ADNI
layers (lipidomics, proteomics, methylation) may be added as separate blocks.

**Status: every step implemented.** `clean`, `cohort`, `export`,
`analyze`, `axis-diagnostics`, the sensitivity step `latent-sensitivity`
and `report` (changes `adni-metabolomics-clean`, `adni-cohort`,
`adni-export`, `adni-analyze`, `adni-axis-diagnostics`,
`adni-latent-sensitivity` and `adni-report`); the first six run on a data
machine, `report` on any clone (it reads committed aggregate files only),
and the first report is committed under `reports/` and checked by
`report --check`. The
statistical choices made so far are `CLEAN_OPTIONS`, `COHORT_RULE`,
`STAGE_RULE`, `ANALYSIS_COVARIATES`, `EXPORT_FEATURE_RULE`, the analysis
settings (`ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA`,
`ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`), `READING_RULES`, the
diagnostic constants (`DIAGNOSTIC_VARIABLES`,
`DIAGNOSTIC_CORRELATION_THRESHOLD`) and the sensitivity constants
(`LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`,
`LATENT_SENSITIVITY_READING_RULES`); every constant the six steps and the
sensitivity step need is decided.
`AGENTS.md` holds the conventions and the hard constraints and is the single
source of truth.

A data machine is any machine whose local participant-level files under
`results/` (the export CSVs, `cohort.csv`, the primary's
`latent_scores.csv` and `analysis_metadata.csv`) hash to the values the
committed manifests record; the hash checks pick it and no machine is
named. Any machine with a data root becomes one by a pinned rebuild from
it (`clean` → `cohort` → `export` → `analyze` into a scratch directory), a
hash check of every output the committed manifests record, and copying
the participant-level files into the gitignored paths under `results/`.
The manifests written before `adni-portable-numerics` record no machine,
but their outputs reproduce pinned on any machine.

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
├── reports/         # committed case-study reports, generated in full by `report` from the aggregate outputs and checked by `report --check`
├── results/         # pipeline outputs; only aggregate files are committed (see .gitignore)
├── scripts/         # sync_results.sh (aggregate outputs between a machine and the cluster), clean.sbatch and analyze.sbatch (clean and analyze on the cluster), spike_*_inventory.py (the changes' read-only spikes)
├── src/
│   └── adni_sexdiff/
│       ├── cli.py         # argparse CLI: clean, cohort, export, analyze, axis-diagnostics, latent-sensitivity, report (exits 1 on a --check mismatch)
│       ├── constants.py   # conventions; scientific constants enter through OpenSpec proposals only
│       └── data.py        # pipeline steps (clean, cohort, export, analyze, axis-diagnostics, report and the sensitivity step latent-sensitivity)
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
   - `latent-sensitivity` (sensitivity step, after 5) – the predeclared
     `stage`-conditioned latent-adjustment arm beside the primary, its
     comparison, and `axis-diagnostics` on the arm →
     `results/motco_latent_sensitivity/` (below)
6. `report` – the case-study report generated in full from the kept
   aggregate outputs (the clean, cohort and export manifests, the primary,
   its diagnostics, the comparison and the arm's diagnostics), or a
   cell-by-cell check of one against them → `reports/` (below)

Quick start:

```
direnv allow            # or: nix develop   (Python 3.12, uv, `uv sync --locked`)
uv run adni-sexdiff --help
uv run adni-sexdiff clean --platform all
uv run adni-sexdiff cohort
uv run adni-sexdiff export
uv run adni-sexdiff analyze
uv run adni-sexdiff axis-diagnostics
uv run adni-sexdiff latent-sensitivity
uv run adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics
uv run adni-sexdiff report
uv run adni-sexdiff report --check
```

Numerics. Every step runs in a pinned numeric environment
(`constants.NUMERIC_SETTINGS`, change `adni-portable-numerics`), so any
machine writes the same bytes from the same inputs and the hash chain holds
whichever machine ran a step. Importing `adni_sexdiff` sets the four
variables before numpy loads; the Nix shell and the sbatch scripts export
them too:

| variable | value | what it fixes |
|---|---|---|
| `NPY_DISABLE_CPU_FEATURES` | `X86_V4 AVX512_ICL` | numpy's AVX-512 `log2` (`export`) |
| `OPENBLAS_CORETYPE` | `Haswell` | OpenBLAS's kernel choice (`analyze`) |
| `OPENBLAS_NUM_THREADS` | `1` | the block SVD's thread-dependent reductions (`axis-diagnostics`) |
| `OMP_NUM_THREADS` | `1` | OpenMP threads (no effect today) |

Every manifest records the state the run actually had (`numerics`: host,
CPU, the variables, numpy's `log2` target, each BLAS library's kernel and
threads, `pinned`). To check a machine, run a step and read
`numerics.pinned`. A run that is not pinned completes with a finding and is
not committed; this happens, for example, when numpy was imported before
`adni_sexdiff` in a script. On 2026-10-28 an AVX-512 machine reproduced every
committed output pinned, on 24 CPUs and on 1, where unpinned runs had
differed at about 1e-15. The pin needs x86-64 with AVX2.

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
`cli_equivalent` reproduces the run with MOTCO's CLI (checked on a data
machine: the statistics, p-values, null summaries and rank are equal
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
seconds and runs wherever the analysis outputs are.

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

Running on an arm: `--analysis-dir` and `--out-dir` run the same
diagnostic on an analysis directory that mirrors the primary's, which is
how `latent-sensitivity`'s arm is read (below). The manifest then records
`is_primary` false, the `primary` and `rows` expectations are skipped and
a finding names the directory and the adjustment; `diagnostics.md` names
the `stage`-conditioned arm, calls a flagged row a finding about the arm's
measurement space (the primary stays primary) and prints
`LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`. Its error hints
name the command that wrote the analysis read (`adni-sexdiff analyze` or
`adni-sexdiff latent-sensitivity`, from the manifest's `step`). No other
flag; no setting is a flag.

The diagnostic reads sex and stage, so it is never a filter: no `export`
or `analyze` run reads `results/motco_diagnostics/`, and arms and variants
are predeclared in a change proposal, never derived from a diagnostic
value. An axis correlated with a variable is a finding about the
measurement space of the analysis read, not a reinterpretation of its
statistics or p-values; `diagnostics.md` prints `READING_RULES` verbatim
and the primary stays primary.

## `latent-sensitivity`

```
uv run adni-sexdiff latent-sensitivity [--input-dir DIR] [--analysis-dir DIR] [--cohort-dir DIR] [--out-dir DIR] [--n-jobs N] [--force]
uv run adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics [--force]
```

A sensitivity step, read beside the primary and never replacing it
(change `adni-latent-sensitivity`). It runs the one arm `adni-analyze`
predeclared: MOTCO's covariate latent adjustment conditioned on `stage`.
`LATENT_SENSITIVITY_ARM` is `latent_stage`:
`covariate_latent_adjustment = "stage"`, the same five covariates
(`ANALYSIS_COVARIATES`) in the same order and coding, and every other
setting the primary's (`ANALYSIS_PERMUTATIONS` 9999, `ANALYSIS_SEED`
20261027, `ANALYSIS_RANK_FLOOR` 2, missing policy `error`, MOTCO's other
defaults, `n_jobs = 1` for the reported run); an import-time assertion
ties it to `ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`. The latent basis is
fitted on the pooled-standardized features with the covariates regressed
out given the intercept and the stage indicators, per CV training set and
on the full sample; the raw features are projected onto it; the
trajectory model, LS-means and RRPP are the primary's, and the CV folds
(stratified on the stage) equal the primary's. The arm and its settings
are constants, never flags: `--analysis-dir` names the primary to read as
the reference, not an arm to run.

It is the only arm. MOTCO's latent-adjustment Type I check
(`../MOTCO/docs/reports/latent-adjustment-type-i-2026-10-20.md`) returned
`adopt_stage` under conditions this change meets (the proposal justifies
the covariate set, `group_stage` is not used, the record's
`latent_adjustment` and `covariates` blocks are reported beside the
results, no categorical level is rare enough to drop out of a CV training
set); its power comparison (`latent-adjustment-power-2026-10-20.md`)
returned `candidate_fails`, so the adjustment is a sensitivity and not a
replacement; `group_stage` conditioning is not admissible and does not
run; the kept outputs hold no further covariate for an extended set.

Covariate roles (`LATENT_SENSITIVITY_COVARIATE_ROLES`, the justification
MOTCO's Type I condition asks for: why no residualized covariate mediates
the stage effect). Residualizing a mediator removes real stage signal, and
no data can tell a confounder from a mediator, so the roles are
predeclared; no statistic or threshold is computed for them and nothing
changes because of them. `latent_sensitivity.md` prints them beside the
cohort manifest's per sex × stage descriptives (n, age and education mean
and sd, counts per level of `apoe4`, `phase` and `statin`), copied, not
recomputed.

| covariate | role | why |
|---|---|---|
| `age` | pre-disease | age at baseline: it can confound the stage effect but cannot be downstream of it |
| `education` | pre-disease | years of schooling, completed before enrolment |
| `apoe4` | pre-disease | germline genotype |
| `phase` | design | the assay run and enrolment protocol (p180 kits ADNI-1 against ADNI-GO/2), tied to stage composition by design (SMC and EMCI exist only in ADNI-GO/2), not caused by stage |
| `statin` | mediator candidate | HMG-CoA reductase inhibitor use on the screening medication row: a treatment that may follow diagnosis, so the arm's basis may have removed stage signal that runs through treatment; it stays in the arm because the arm was predeclared with the five covariates, and the reading carries the limitation |

Inputs: `results/motco_input/` (the five files, checked as `analyze`
checks them), the primary's `results/motco_analysis/result.json` and
`analysis_manifest.json` (read, never written; no primary CSV) and
`results/cohort/cohort_manifest.json` (its hash and its descriptives; no
`cohort.csv`). Nothing else, nothing under a diagnostics directory.

Checks, in this order, before anything is written (a failure names the
file or setting, both values and the step to rerun, never a participant):
the gates of `analyze` (MOTCO ≥ 0.10.0, MOTCO's default rank floor equal
to `ANALYSIS_RANK_FLOOR`); `analysis/` or `comparison/` existing without
`--force`; the export; the primary as a chained, read-only reference (its
directory and two JSON files exist, every input hash and the
export-manifest hash it records equal the export files now, it records no
latent adjustment, it was made under the installed MOTCO version with
`ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS`); the cohort manifest's sha256
against the export manifest's record. The rare-level condition is
MOTCO's: the smallest categorical level is `apoe4 = 2` with 149
participants, about 74 of them in the smallest CV training set, and if
MOTCO still reports a residualization design that is not of full rank, on
the full sample or in a CV training set, the step stops with MOTCO's
message (naming the repeat and fold), nothing is written, no level is
merged and no setting changes.

Outputs under `results/motco_latent_sensitivity/`. `analysis/` and
`comparison/` are staged as `analysis.tmp/` and `comparison.tmp/` and
renamed together when both are complete; a failure leaves both final
directories as they were, and `--force` replaces both. `diagnostics/` is
never touched by the step (when it replaces `analysis/` while
`diagnostics/` exists, a finding says the arm diagnostic must be rerun;
the step tests only that the directory exists and opens nothing under
it). Reruns on the same inputs give byte-identical CSVs:

| file | content | committed / synced |
|---|---|---|
| `analysis/result.json` | MOTCO's record for the arm, with its `latent_adjustment` block (conditioning, covariates, the eight residualization design columns, samples, residual df, smallest CV training df, feature scale, `feature_r2` quantiles and mean) | yes (aggregate) |
| `analysis/latent_scores.csv` | the arm's per-participant PLS scores | no (participant-level; matched by `results/**/latent_scores.csv`) |
| `analysis/pls_loadings.csv`, `analysis/stage_means.csv` | as for the primary | yes (aggregate) |
| `analysis/analysis_metadata.csv` | the metadata table the model saw | no (participant-level; matched by `results/**/analysis_metadata.csv`) |
| `analysis/analysis_manifest.json` | `step` `latent-sensitivity`; the five export files as inputs; `arm` (the constant by name) and `reference` (the primary's directory, its two hashes, rank, MOTCO version, `n_jobs`); every setting as passed with `latent_adjustment` `stage`; `cli_equivalent` naming `--latent-adjustment stage`; `numerics`; the predeclared `LATENT_SENSITIVITY_EXPECTED_COUNTS` beside the observed ones with deviations; output hashes with a participant-level flag; findings | yes (aggregate, no `RID`) |
| `analysis/summary.md` | the primary's renderer with the arm's title, a "Latent adjustment" section, the arm's note on each reading line and `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES` | yes (aggregate) |
| `comparison/latent_sensitivity.csv` | two rows, the primary then the arm: `directory` (the primary's as read; for the arm its subdirectory under the output root, so the table does not depend on where the root is), latent adjustment, selected rank and selection mode, `cv_mean_auroc`, CV repeats, eigengap, per statistic observed, p, rejection under `ANALYSIS_REJECTION_RULE`, null mean, SD and q95, and for the arm the residual df, smallest CV training df and `feature_r2` quantiles and mean; every value read from the two records, no runtime column | yes (aggregate) |
| `comparison/latent_sensitivity.md` | the header, the statistics with a status per statistic (`same`, or `differs (basis dependence)`; the primary's status is the result either way), the latent spaces, the arm's latent-adjustment block, the covariate roles beside the cohort manifest's descriptives, MOTCO's two latent-adjustment decisions, the findings, `READING_RULES` then `LATENT_SENSITIVITY_READING_RULES` | yes (aggregate) |
| `comparison/latent_sensitivity_manifest.json` | versions, `numerics`, git revision; the eight inputs with sha256 and the chain results; the arm, the roles, α with the rule, `n_jobs`; `reference` and `arm`; the counts (statuses, ranks, CV AUROC, the latent-adjustment block, the cohort cells against the record's); the arm's expected counts and deviations, copied; output hashes; findings | yes (aggregate) |
| `diagnostics/` (six files) | `axis-diagnostics` on the arm, run with the command above | yes (aggregate) |

Predeclared counts (`LATENT_SENSITIVITY_EXPECTED_COUNTS`, from the
committed manifests and MOTCO's design rules, none from a run): every key
of `ANALYSIS_EXPECTED_COUNTS` (1501 participants and the six cells,
133 / 165 / 298 features, the six design columns, the level counts, 0
dropped, `cv`, floor 2, 9999 permutations) and the latent-adjustment
block (conditioning `stage`, the five covariates, the design columns
`stage[1]`, `stage[2]` (MOTCO's ordinal codes for MCI and AD) then the
six design columns, 1501 samples, residual df 1492 = 1501 − 1 − 2 − 6,
feature scale `pooled_standardized`). The arm's rank is not predeclared.
A deviation is a finding, printed and recorded, never a stop. Findings
also record every finding condition of `analyze`, an arm rank that
differs from the primary's, a statistic whose rejection status differs
(basis dependence), a primary read with `n_jobs ≠ 1`, cohort-manifest
cells that differ from the record's cells, and a replaced arm whose
`diagnostics/` exists. A run that is not pinned (`numerics.pinned`) is a
finding and is not committed.

Diagnostics on the arm: the second command above writes the six files of
`axis-diagnostics` under `diagnostics/`, with `is_primary` false, latent
adjustment `stage`, the rank-independent expectations checked, and a
`diagnostics.md` that names the arm and prints both sets of reading
rules. The arm's components can still track phase, since the raw features
are measured in the adjusted basis; a flagged row is a measurement-space
finding about the arm and never grounds to adopt it.

Reading rules (`LATENT_SENSITIVITY_READING_RULES`, written before any run
and printed verbatim after `READING_RULES` in the arm's `summary.md`,
`latent_sensitivity.md`, the arm's `diagnostics.md` and every report that
quotes the arm), in brief: the arm never replaces the primary (MOTCO's
`candidate_fails`); the two analyses share everything but the latent
basis and the CV-selected rank, so a differing status is basis
dependence; the arm's rank, floor, eigengap and null summary are read
beside its `angle`, and a differing rank is reported, not ranked; an
arm-only `angle` rejection is read against MOTCO's translation control
(0.085–0.092 against the 0.0706 bound; the Type I check held it by
0.004); a `delta` or `shape` non-rejection in the arm is weaker than the
primary's (MOTCO measured lost `shape` and small-`delta` power); the
`latent_adjustment` and covariate blocks are reported beside the results,
`feature_r2` stating how much feature variance the residualization
removed; `statin` may follow diagnosis, so the arm's basis may have
removed stage signal that runs through treatment; MOTCO's operating
characteristics were measured at n = 80 and none at this design, so the
arm carries no Type I or power claim; an arm axis in the diagnostic is a
measurement-space finding and never grounds to adopt the arm. No arm value
changes a constant, selects a covariate, reruns the primary or defines a
variant.

## `report`

```
uv run adni-sexdiff report [--cleaned-dir DIR] [--cohort-dir DIR] [--input-dir DIR] [--analysis-dir DIR] [--diagnostics-dir DIR] [--sensitivity-dir DIR] [--out FILE] [--force]
uv run adni-sexdiff report --check [--out FILE] [the same directory flags]
```

The last step of the pipeline (change `adni-report`): the case-study
report, generated in full from the kept aggregate outputs, and its check.
Every default is the pipeline's directory (`results/cleaned`,
`results/cohort`, `results/motco_input`, `results/motco_analysis`,
`results/motco_diagnostics`, `results/motco_latent_sensitivity` read as
`analysis/`, `comparison/` and `diagnostics/`); no flag selects what is
reported. `--out` must be named `reports/motco-adni-<date>.md`
(`REPORT_NAME`): the date is read from the name and written in the title
line only, write mode defaults to today's date and `--check` to the newest
report under `reports/` by the date in its name.

Inputs (`REPORT_INPUT_FILES`, 26 files, all committed): the two
`clean_manifest.json`; `stage_counts.csv` and `cohort_manifest.json`; the
export `manifest.json`; the primary's `result.json`,
`analysis_manifest.json` and `summary.md`; the primary diagnostics' six
files; the arm's three aggregate analysis files, the comparison's three
files and the arm diagnostics' six files. Nothing else: no
participant-level file is opened or required (`cohort.csv`, the export
CSVs, `latent_scores.csv` and `analysis_metadata.csv` are quoted by the
hashes the manifests record), no data root, no MOTCO call and no pinned
numeric environment, so the step runs on any clone with the committed
tree and records no numerics.

Gates, before anything is written, each stopping naming the file or
setting, both values and the step to rerun: every input present; every
aggregate file hashes to the value its own manifest records under
`outputs` (manifests are hashed for the chain, not checked against
themselves); the primary is the primary (no latent adjustment,
`is_primary` true in its diagnostics) and the arm is
`LATENT_SENSITIVITY_ARM` (`is_primary` false in its diagnostics); the
primary and the arm are reported runs (`n_jobs = 1` in manifest and
record), every `numerics` block present records `pinned` true, and every
manifest records the same MOTCO, scikit-learn and metabo_adni versions;
the chain holds link by link (31 links: the clean manifests in the cohort
and export manifests, the cohort manifest in the export manifest, the
export manifest and files in the four analysis-reading manifests, the
primary's two files as the arm's and the comparison's `reference`, the
arm's two files in the comparison and the arm diagnostics). An existing
`--out` stops write mode unless `--force`.

The report (`REPORT_SECTIONS`, ten level-2 sections in order): summary;
provenance (versions, revisions and numerics per step, the 26 inputs with
their sha256, the raw LONI inputs as the clean and cohort manifests record
them, the chain links checked: the report's manifest); cohort (the rules
as recorded, the cascades, the sex × stage tables of both platform sets
and the intersection, the intersection's `DX.bl` × phase cells, the
per-cell covariate descriptives, phase against the p180 run, the cleaning
options and counts with the expected ones beside them); export (the
feature rule as recorded, features per block, block shares, the run offset
per block, cells); primary analysis (settings by constant name, MOTCO's
defaults read back, the statistics with p-values, rejection and null
summaries, the reading lines, cell sizes, the latent space, the covariate
block with the reference row, the `cli_equivalent`); axis diagnostics of
the primary (the variables, the flagged rows, the components table, the
block PCs with pc1 against `phase` beside the export's Pearson value);
latent-adjustment sensitivity (the comparison with a status per
statistic, the status lines, the latent spaces, the arm's
`latent_adjustment` block, the covariate roles, MOTCO's two decisions, the
arm's diagnostics, the first component against `phase` beside the
primary's, the arm's `cli_equivalent`); findings (every deviation and
finding of every manifest, verbatim under its step, then the report's own:
a dirty recorded revision, a manifest without a `numerics` block);
`READING_RULES` then `LATENT_SENSITIVITY_READING_RULES`, verbatim; the
commands that reproduce the pipeline and check the report. Every table is
titled by a level-3 heading and keyed by its first column; every number is
copied from a record, a manifest or a CSV at the digits of the summary it
belongs to (the step computes no statistic, correlation, mean or count);
the only interpretive sentences are the ones `summary.md` and
`latent_sensitivity.md` print, produced by the same code
(`_statistic_reading_line`, `_arm_status_line`) so that they are
string-equal across the three documents; the primary's status is the
result wherever the arm appears, and both rule constants are named beside
every table that quotes the arm. The body depends on the inputs and the
file name only (no revision, host, time or runtime of the report run), so
two runs on the same inputs are byte-identical and two dates differ in the
title line alone. The file is written to `<out>.tmp`, parsed back through
the checker's parser and checked against the generated tables, then
renamed. It quotes aggregate values only and holds no participant
identifier.

`--check` reads the report, runs every gate, regenerates the report from
the outputs now on disk with the date taken from the file name and
compares: every table cell by cell (section, table, row key, column, both
values) and every other line line by line (section, line number, both
texts); absent or extra sections, tables, rows and lines are mismatches
too. Every mismatch is printed, the CLI exits 1 on any, and nothing is
written. A results directory regenerated after the report fails the check
on the provenance hashes: the committed report corresponds to the
committed outputs, and a change that regenerates an output or rewords a
renderer re-issues the report.

Commit discipline: a report is written on the clean tree at the
implementing commit, checked with `report --check`, and committed alone,
naming it and stating why it is aggregate (every value in it is copied
from a committed aggregate file or a constant). `reports/` is committed
and is unchanged in `.gitignore`, the sync filter and
`PARTICIPANT_LEVEL_PATTERNS`.

Dependencies: `motco` (git tag `v0.10.0`, via `[tool.uv.sources]`),
`metabo_adni==0.5.8` (cleaning, never reimplemented here), `pandas`, `numpy`.
