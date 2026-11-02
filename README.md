# adni_sexdiff

Sex × stage (CN / MCI / AD) trajectory comparison on ADNI serum metabolomics
(Biocrates p180 and Nightingale NMR) with [MOTCO](https://github.com/tomszar/MOTCO):
the first MOTCO application at a well-powered design (n ≈ 1,300). Later ADNI
layers (lipidomics, proteomics, methylation) may be added as separate blocks.

**Status: every step implemented.** `clean`, `cohort`, `export`,
`analyze`, `axis-diagnostics`, the sensitivity steps `latent-sensitivity`,
`export-sensitivity`, `stage-sensitivity` and `rank-sensitivity`, and
`report` (changes `adni-metabolomics-clean`, `adni-cohort`, `adni-export`,
`adni-analyze`, `adni-axis-diagnostics`, `adni-latent-sensitivity`,
`adni-nist-bridge`, `adni-report`, `adni-report-variants`,
`adni-stage-sensitivity`, `adni-report-stage-arm`,
`adni-rank-sensitivity`, `adni-report-rank-sweep`, `adni-nmr-all-columns`,
`adni-report-nmr-all-columns`, `adni-scale-variants` and
`adni-report-scale-variants`); every step but `report` runs on a data
machine, `report` on any clone (it reads committed aggregate files only),
and the reports are committed under `reports/` and checked by
`report --check`; since `adni-report-scale-variants` a report covers the
primary, the latent arm, the six export variants (the two p180 variants,
`nmr_all_columns`, all 245 cleaned NMR columns in the block, and the three
scale variants `raw_scale`, `log2_plus_one` and `glog`, both blocks on the
raw scale, `log2(x + 1)` or the generalized log; each group read under its
own rule set), the CN / LMCI / AD arm and the rank sweep (the reports of
2026-10-28, 2026-10-29, 2026-10-30, 2026-10-31 and 2026-11-02, of earlier
layouts, cover fewer).
The
statistical choices made so far are `CLEAN_OPTIONS`, `COHORT_RULE`,
`STAGE_RULE`, `ANALYSIS_COVARIATES`, `EXPORT_FEATURE_RULE`, the analysis
settings (`ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA`,
`ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`), `READING_RULES`, the
diagnostic constants (`DIAGNOSTIC_VARIABLES`,
`DIAGNOSTIC_CORRELATION_THRESHOLD`) and the sensitivity constants
(`LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`,
`LATENT_SENSITIVITY_READING_RULES`; `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE`,
`EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES`,
`SCALE_VARIANT_RULE`, `SCALE_VARIANT_READING_RULES`; `STAGE_SENSITIVITY_ARM`,
`STAGE_SENSITIVITY_READING_RULES`; `RANK_SENSITIVITY_LADDER`,
`RANK_SENSITIVITY_READING_RULES`); every constant the six steps and the
four sensitivity steps need is decided.
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
`export-sensitivity --variant nist_bridge` also reads the two p180
supplement archives in place, through two symlinks made by hand on every
data machine and the cluster:
`ln -s Metabolomics/p180/ADMC_supplement.zip <root>/ADMC_supplement.zip` and
`ln -s Metabolomics/p180/ADMCDUKEP180SUPP_20170410.zip <root>/ADMCDUKEP180SUPP_20170410.zip`
(nothing is extracted).
Replicate a root with `rsync -a` (symlinks preserved); never rename the
archive files.

Project layout:

```
.
├── data/            # raw ADNI files, uploaded by hand: LONI archive under Metabolomics/, clinical tables under Clinical/, the names the steps read as symlinks (gitignored)
├── reports/         # committed case-study reports, generated in full by `report` from the aggregate outputs and checked by `report --check`
├── results/         # pipeline outputs; only aggregate files are committed (see .gitignore)
├── scripts/         # sync_results.sh (aggregate outputs between a machine and the cluster), clean.sbatch and analyze.sbatch (clean and analyze on the cluster), spike_*_inventory.py, spike_nist_bridge.py, spike_stage_arm.py and spike_nmr_all_columns.py (the changes' read-only spikes)
├── src/
│   └── adni_sexdiff/
│       ├── cli.py         # argparse CLI: clean, cohort, export, analyze, axis-diagnostics, latent-sensitivity, export-sensitivity, stage-sensitivity, rank-sensitivity, report (exits 1 on a --check mismatch)
│       ├── constants.py   # conventions; scientific constants enter through OpenSpec proposals only
│       └── data.py        # pipeline steps (clean, cohort, export, analyze, axis-diagnostics, report and the sensitivity steps latent-sensitivity, export-sensitivity, stage-sensitivity and rank-sensitivity)
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
   - `export-sensitivity` (sensitivity step, after 5) – the predeclared
     export variants: two of the p180 run handling (a NIST SRM 1950 bridge
     of the runs, per-run standardization) and one of the NMR membership
     (all 245 cleaned NMR columns), each exported, analysed at the primary's
     settings and compared with the primary, and `axis-diagnostics` on each
     → `results/motco_export_sensitivity/` (below)
   - `stage-sensitivity` (sensitivity step, after 5) – the predeclared
     CN / LMCI / AD arm (SMC and EMCI, enrolled only in ADNI-GO/2, dropped):
     the primary export's rows of the kept participants, analysed at the
     primary's settings and compared with the primary, and
     `axis-diagnostics` on the arm → `results/motco_stage_sensitivity/`
     (below)
   - `rank-sensitivity` (sensitivity step, after 5) – the predeclared rank
     sweep: after an anchor run at the primary's rank reproduces the
     primary, the primary's analysis at the forced ranks 2, 3, 4, 6, 9 and
     12, compared with the primary, and `axis-diagnostics` on the top rank
     → `results/motco_rank_sensitivity/` (below)
6. `report` – the case-study report generated in full from the kept
   aggregate outputs (the clean, cohort and export manifests, the primary,
   its diagnostics, the latent arm with its comparison and diagnostics,
   each export variant of `REPORT_EXPORT_VARIANTS` with its export
   manifest, analysis, comparison, diagnostics and bridge table, the
   CN / LMCI / AD arm with its export manifest, analysis, comparison and
   diagnostics, and the rank sweep), or a cell-by-cell check of one against
   them → `reports/` (below)

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
uv run adni-sexdiff export-sensitivity --variant all
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir results/motco_export_sensitivity/nist_bridge/diagnostics
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/per_run_standardized/motco_input --analysis-dir results/motco_export_sensitivity/per_run_standardized/analysis --out-dir results/motco_export_sensitivity/per_run_standardized/diagnostics
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/nmr_all_columns/motco_input --analysis-dir results/motco_export_sensitivity/nmr_all_columns/analysis --out-dir results/motco_export_sensitivity/nmr_all_columns/diagnostics
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/raw_scale/motco_input --analysis-dir results/motco_export_sensitivity/raw_scale/analysis --out-dir results/motco_export_sensitivity/raw_scale/diagnostics
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/log2_plus_one/motco_input --analysis-dir results/motco_export_sensitivity/log2_plus_one/analysis --out-dir results/motco_export_sensitivity/log2_plus_one/diagnostics
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/glog/motco_input --analysis-dir results/motco_export_sensitivity/glog/analysis --out-dir results/motco_export_sensitivity/glog/diagnostics
uv run adni-sexdiff stage-sensitivity
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_stage_sensitivity/motco_input --analysis-dir results/motco_stage_sensitivity/analysis --out-dir results/motco_stage_sensitivity/diagnostics
uv run adni-sexdiff rank-sensitivity
uv run adni-sexdiff axis-diagnostics --analysis-dir results/motco_rank_sensitivity/rank_12 --out-dir results/motco_rank_sensitivity/diagnostics
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
`LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`. With
`--input-dir` as well, it reads an export variant of `export-sensitivity`
(below). The manifest records `is_primary` false and the variant's name.
The expected counts are the variant's own `diagnostics` counts when its
`EXPORT_VARIANT_EXPECTED_COUNTS` entry holds them (`nmr_all_columns`: 245
NMR features), and the rank-independent ones otherwise. `diagnostics.md`
names the variant and the block it changes, calls a flagged row a finding
about the variant's measurement space, and prints the variant's rule set
(`EXPORT_VARIANT_RULE_SETS`) after `READING_RULES`:
`EXPORT_VARIANT_READING_RULES` for the p180 variants,
`NMR_MEMBERSHIP_READING_RULES` for `nmr_all_columns`,
`SCALE_VARIANT_READING_RULES` for the scale variants (whose
`diagnostics.md` names an export whose scale differs, with the
rank-independent counts and 165 NMR features). With the
CN / LMCI / AD arm of `stage-sensitivity` (below) the cohort check
compares the both-flag rows whose `dx_bl` the arm keeps, the expected
participants and cells are the arm's (`STAGE_SENSITIVITY_EXPECTED_COUNTS`),
the manifest records `is_primary` false and `stage_arm`, and
`diagnostics.md` names the arm and prints
`STAGE_SENSITIVITY_READING_RULES` after `READING_RULES`. With a forced rank
of the rank sweep of `rank-sensitivity` (below; `--analysis-dir
results/motco_rank_sensitivity/rank_<kk>` with the primary export), the
manifest records `is_primary` false and `rank_sweep` (the forced rank and
the primary's rank; `null` on every other read); on the top rank,
`rank_12`, the sweep's predeclared diagnostic, the expected counts are
`RANK_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]` (the rank-independent
keys, the read: rank 12, `forced`, no latent adjustment, `n_jobs` 1, and
the rows 96 / 48 / 48 / 12), on another rank the rank-independent keys
with a finding that the sweep's predeclared diagnostic is the top rank's;
`diagnostics.md` names the rank sweep and the forced rank, states that its
components up to the primary's rank are the primary's (nesting), calls a
flagged row a finding about the measurement space at that rank and prints
`RANK_SENSITIVITY_READING_RULES` after `READING_RULES`. Its error hints
name the command that wrote the analysis read (`adni-sexdiff analyze`,
`adni-sexdiff latent-sensitivity`, `adni-sexdiff export-sensitivity
--variant <name>`, `adni-sexdiff stage-sensitivity` or `adni-sexdiff
rank-sensitivity --force`, from the manifest's `step`). No other flag; no
setting is a flag.

The diagnostic reads sex and stage, so it is never a filter: no `export`,
`analyze` or sensitivity run reads `results/motco_diagnostics/` or any
other diagnostics directory, and arms, variants and the rank ladder are
predeclared in a change proposal, never derived from a diagnostic
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

## `export-sensitivity`

```
uv run adni-sexdiff export-sensitivity --variant {nist_bridge,per_run_standardized,nmr_all_columns,raw_scale,log2_plus_one,glog,all} [--data-root DIR] [--cleaned-dir DIR] [--cohort-dir DIR] [--input-dir DIR] [--analysis-dir DIR] [--out-dir DIR] [--n-jobs N] [--force]
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/<variant>/motco_input --analysis-dir results/motco_export_sensitivity/<variant>/analysis --out-dir results/motco_export_sensitivity/<variant>/diagnostics [--force]
```

A sensitivity step, read beside the primary and never replacing it
(changes `adni-nist-bridge`, `adni-nmr-all-columns` and
`adni-scale-variants`). Each registered variant reruns the export with one
setting changed (of one block, or the scale of both), analyses
it at the primary's settings (one `analyze_trajectories` call through the
code `analyze` uses: `ANALYSIS_*`, MOTCO's defaults, no latent
adjustment, `n_jobs = 1`, pinned) and compares it with the primary. The
participants, the metadata, the covariates and the block a variant does
not change are the primary's, byte for byte. Two variants handle the p180
run: the p180 block's first axis is the assay run (ADNI-1 against
ADNI-GO/2: median |d| 1.12, PC1 correlation 0.73 with phase), and the
primary keeps `phase` as a covariate of the stage means. The third,
`nmr_all_columns`, changes the NMR block's membership. The last three,
`raw_scale`, `log2_plus_one` and `glog`, change the scale of both blocks.
The variants, the bridge rule and the scales are constants, never flags.
`--variant` selects a registered name, or `all` for every variant in
registry order. With a variant's outputs present, `all` stops at the
existing-variant gate unless `--force`, so a run of one new variant names
it (`--variant raw_scale`). `--input-dir` and `--analysis-dir` name the
primary to read as the reference.

Variants (`EXPORT_VARIANTS`):

| variant | block, hook | setting | reads the data root |
|---|---|---|---|
| `nist_bridge` | p180, `factors` | every cleaned p180 concentration of an ADNI-GO/2 participant (the run of `p180_runs.csv`) multiplied by 2^b of its metabolite under `NIST_BRIDGE_RULE`, before the floors; `EXPORT_FEATURE_RULE` then unchanged, its floors recomputed | yes: the two QC archives |
| `per_run_standardized` | p180, `standardize_by_run` | the rule's p180 values (pooled floors, `log2(x + floor)`), each metabolite centred and divided by its population SD within its run | no |
| `nmr_all_columns` | nmr, `membership` | every cleaned NMR column enters the block (245): the 165 concentrations of `EXPORT_FEATURE_RULE` and its 80 derived columns (72 percentages, 4 ratios, the degree of unsaturation, 3 sizes), in cleaned order, each on the rule's scale, `log2(x + floor)` with its own 5 % floor over the exported participants | no |
| `raw_scale` | all, `scale` | every kept cell of both blocks the cleaned concentration in its platform's unit, no log and no offset (`SCALE_VARIANT_RULE`); the rule's floors recorded, not applied | no |
| `log2_plus_one` | all, `scale` | every kept cell of both blocks `log2(x + 1)`, offset 1 in the platform's unit (the 2022 study's transform); the rule's floors recorded, not applied | no |
| `glog` | all, `scale` | every kept cell of both blocks `log2((x + sqrt(x² + λ²)) / 2)`, λ per metabolite its smallest positive value over the exported participants divided by 10; the rule's floors recorded, not applied | no |

The membership variant (`nmr_all_columns`, change `adni-nmr-all-columns`,
decided before any run of it):
- **What it keeps.** The 165 concentrations keep the primary's floors,
  order and every cell. The export compares them with the primary
  `nmr.csv` (`rule_columns_equal_primary`; a difference is a finding).
- **What it adds.** The 80 derived columns, each with its own floor. They
  add no measurement: on the rule's scale the concentrations explain a
  median 0.998 of a derived column's variance, lowest 0.798.
- **What changes.** The block's weight in the joint matrix: MOTCO 0.10.0
  z-scores every feature and weights features, not blocks, so the p180
  share falls from 133 / 298 to 133 / 378. The NMR block also gains left
  tails: 24 columns with |skew| > 1 and 9 with a largest |z| above 8,
  against 3 and 1.
- **What it shares.** The CV folds and the RRPP draws are the primary's,
  since neither reads the features. The 2022 study used all 245 columns,
  but with `log2(x + 1)`, winsorizing, outlier removal and medication
  residuals; the variant changes the membership only and is no
  reproduction of it.

The scale variants (`raw_scale`, `log2_plus_one`, `glog`; change
`adni-scale-variants`, decided before any run of them; block `all`, hook
`scale`, rule `SCALE_VARIANT_RULE`):
- **What they keep.** The primary's membership of both blocks (133 p180
  metabolites, 165 NMR concentrations), participants, metadata and
  covariates; `metadata.csv` and `covariates.csv` equal the primary's.
  Every scale is monotone in the concentration, so each participant's rank
  on each feature is the primary's.
- **What they change.** The scale of every kept cell, in place of the
  rule's `log2(x + floor)`. The rule's floor is still computed, gated and
  recorded per metabolite (the feature tables' `floor`), and not applied;
  the feature tables gain an `offset` column (empty for `raw_scale`, 1 for
  `log2_plus_one`, λ for `glog`). `settings.units` records the variant's
  transform.
- **What they show.** `raw_scale` has right tails (|skew| > 1 for 46 p180
  and 43 NMR metabolites) and an NMR block of numerical rank 104 of 165,
  since the lipoprotein measures are exact sums on the concentration
  scale. `log2(x + 1)` is nearly linear for a scarce metabolite (median
  below 1: 46 p180, 129 NMR). `glog` is `log2(x)` within 0.004 bits, puts
  the 41 NMR zero cells at `log2(λ / 2)` and keeps left tails. The run
  offset barely moves (p180 median |d| 1.08 to 1.13).
- **The λ gate.** A kept metabolite with no positive cell leaves λ
  undefined: `glog` stops naming the block and the count, before anything
  is written (none on the committed inputs).
- **What they share.** The CV folds and the RRPP draws are the primary's.
  `log2_plus_one` is the 2022 study's transform, but the variant is no
  reproduction of that study.

The bridge (`NIST_BRIDGE_RULE`), from NIST SRM 1950 alone (the one
material both runs measured; no participant row, label or covariate is
read): the rows labelled `NIST SRM 1950` of the sheet `NIST SRM 1950 Data`
of four QC workbooks, read in place inside `ADMC_supplement.zip` (ADNI-1:
`4097_FIA_NIST_and_QC_Data.xlsx`, `4097_UPLC_NIST_and_QC_Data.xlsx`) and
`ADMCDUKEP180SUPP_20170410.zip` (ADNI-GO/2: `4610 FIA p180 QC and NIST
Data.xlsx`, `4610 UPLC p180 QC and NIST Data.xlsx`). A replicate's cell is
valid when it is a positive number whose status, where the workbook has a
status column (ADNI-GO/2 only), is not `ISTD Out of Range`; `< LOD` and
`No Interception` are text and missing. A metabolite is bridged when at
least half its replicates are valid in each run; `b` is the mean log2 of
its valid ADNI-1 replicates minus that of its valid ADNI-GO/2 replicates,
without plate correction (it would move `b` by a median 0.0007 log2), and
a metabolite not bridged keeps factor 1. Names are matched within kit with
case and punctuation dropped. On the predeclared bytes it bridges 126 of
133 (FIA 102, UPLC 24); `C0`, `C10:2`, `C12`, `C14:1-OH`, `C6 (C4:1-DC)`,
serotonin and spermidine keep factor 1 (`C0` because 17 of its 24
ADNI-GO/2 cells are ISTD-flagged). The plate-clustered SE is recorded
beside `b` and never used by the rule.

Inputs: `results/cleaned/` (`P180.csv`, `p180_runs.csv`, `NMR.csv`, each
against its `clean_manifest.json`), `results/cohort/` (`cohort.csv`,
`cohort_manifest.json`), the primary export `results/motco_input/` and the
primary's `result.json` and `analysis_manifest.json`; for `nist_bridge`
the two archives at the top of the data root. Nothing under a diagnostics
directory.

Checks, in this order, before anything is written (a failure names the
file or setting, both values and the command to rerun, never a
participant, and nothing is created under the output root): the variant
name; the gates of `analyze`; an existing variant without `--force`; the
clean outputs and the cohort chain; the primary export against its
manifest and against the clean and cohort files now on disk; the primary
analysis as a chained reference (its recorded export hashes, no latent
adjustment, the installed MOTCO, the seed and permutations); for
`nist_bridge`, the archives (an absent one names the file; a missing
member names the archive and the member); for `glog`, a kept metabolite
with no positive cell (λ undefined). `per_run_standardized`,
`nmr_all_columns` and the scale variants read no data-root file.

Outputs under `results/motco_export_sensitivity/<variant>/`, each
subdirectory staged as `<sub>.tmp/` and the set renamed together when
complete; `--force` replaces them, and a replaced variant whose
`diagnostics/` exists gets a finding (stale until `axis-diagnostics` is
rerun). Two pinned runs write byte-identical CSVs, `summary.md`,
`export_sensitivity.md` and bridge table; `result.json` differs only in
MOTCO's runtime:

| file | content | committed / synced |
|---|---|---|
| `bridge/nist_bridge.csv` | `nist_bridge` only: one row per exported p180 metabolite, its kit and NIST column, per run the replicates, valid replicates, ISTD flags, mean log2 and plate-clustered SE, then `b`, its SE, `bridged` and the applied `factor_log2` (reference material only) | yes (aggregate) |
| `motco_input/p180.csv`, `nmr.csv`, `metadata.csv`, `covariates.csv` | the variant export, laid out as the primary's | no (participant-level; matched by `results/motco_export_sensitivity/*/motco_input/*.csv`) |
| `motco_input/features_p180.csv`, `features_nmr.csv` | per feature, as the primary's; a scale variant adds `offset` | no (ignored with the other CSVs, regenerable) |
| `motco_input/manifest.json` | step `export-sensitivity`; the variant; the primary export as `reference` (its manifest hash, output hashes and run offset); the QC archives and members with their hashes beside the predeclared ones and the bridge table's hash, summary and factor per metabolite (`nist_bridge`); the counts with the runs, the participants whose run differs from `phase` and the unchanged files against the primary's, for `nmr_all_columns` also the derived columns kept (`derived_kept`) and the rule's columns against the primary's (`rule_columns_equal_primary`); for a scale variant `settings.scale` (the constant and its entry), `counts.scale` (the transform and offset; the medians below the offset for `log2_plus_one`, the quantiles of λ over the median for `glog`) and the primary's shape counts and spectrum in `reference`; `EXPORT_VARIANT_EXPECTED_COUNTS` beside them with deviations; output hashes; findings | yes (aggregate, no `RID`) |
| `analysis/result.json`, `pls_loadings.csv`, `stage_means.csv` | as for the primary | yes (aggregate) |
| `analysis/latent_scores.csv`, `analysis_metadata.csv` | as for the primary | no (participant-level; matched by `results/**/`) |
| `analysis/analysis_manifest.json` | step `export-sensitivity`; the variant export's five files as inputs; the variant; the primary as `reference` (its two hashes, rank, MOTCO, `n_jobs`, its export); every setting as the primary's; the variant's `analysis` expected counts with deviations; findings | yes (aggregate) |
| `analysis/summary.md` | the primary's renderer with the variant's title, an "Export variant" section (the setting, the blocks kept, the runs, the bridge for `nist_bridge`, the membership, block shares and NMR shape counts for `nmr_all_columns`, the transform, offset, offset summary and per block the shape counts and numerical rank of both exports for a scale variant, the run offset per block of both exports), the variant's note on each reading line and the variant's rule set after `READING_RULES` | yes (aggregate) |
| `comparison/export_sensitivity.csv` | the primary row then the variant row: selected rank and mode, `cv_mean_auroc`, CV repeats, eigengap, per statistic observed, p, rejection, null mean, SD and q95; every value read from the two records | yes (aggregate) |
| `comparison/export_sensitivity.md` | the statistics with a status per statistic (`same`, or `differs (<dependence>)` with the variant's label: `run-handling dependence` for the p180 variants, `feature-membership dependence` for `nmr_all_columns`, `scale dependence` for the scale variants; the primary's status is the result either way), the variant's reading lines, the latent spaces, the export variant section, the findings, `READING_RULES` then the variant's rule set | yes (aggregate) |
| `comparison/export_sensitivity_manifest.json` | the inputs (both exports and analyses, the bridge table, the QC files) with sha256 and chains; the settings; the counts (statuses, ranks, run offsets); both expected counts and deviations; output hashes; findings | yes (aggregate) |
| `diagnostics/` (six files) | `axis-diagnostics` on the variant, run with the second command above | yes (aggregate) |

Predeclared counts (`EXPORT_VARIANT_EXPECTED_COUNTS`, from the change's
spike, none from a run of a variant), per variant: every key of
`EXPORT_EXPECTED_COUNTS` with the p180 run offset replaced (phase |d| > 0.5
/ > 1: `nist_bridge` 35 / 8, `per_run_standardized` 0 / 0); for
`nist_bridge` 102 FIA and 24 UPLC metabolites bridged, 7 not, 0 without a
NIST column; 0 participants whose run differs from `phase`; `nmr.csv`,
`metadata.csv` and `covariates.csv` equal to the primary's; and every key
of `ANALYSIS_EXPECTED_COUNTS` for the analysis. For `nmr_all_columns`
(from its spike and the committed manifests):
- **Participants:** 1501, in the primary's cells.
- **Features:** p180 133 / 133; NMR 245 cleaned, 245 kept, 0 excluded as
  derived, derived kept percentage 72, ratio 4, degree 1, size 3; 378
  joint features.
- **Cells:** zero cells p180 0, NMR 41 in 3 metabolites; 0 floors not
  positive and 0 non-finite cells per block.
- **NMR shape:** |skew| > 1 for 24 columns, largest |z| > 8 for 9.
- **Run offset:** phase |d| > 0.5 / > 1 at p180 109 / 80 (the primary's)
  and NMR 5 / 0; 0 participants whose run differs from `phase`.
- **Equal to the primary's:** `p180.csv`, `metadata.csv` and
  `covariates.csv`, and the 165 concentration columns.
- **Analysis:** every key of `ANALYSIS_EXPECTED_COUNTS`, with features
  p180 133, NMR 245, joint 378.
- **Diagnostics:** the rank-independent keys of
  `DIAGNOSTICS_EXPECTED_COUNTS` with 245 NMR features.

For the scale variants (from the change's spike and the committed
manifests), shared by the three: 1501 participants in the primary's cells;
the primary's features (p180 133 / 133, NMR 245 cleaned, 165 kept); zero
cells p180 0 and NMR 41 in 3 metabolites (before the transform); 0 floors
not positive and 0 non-finite cells; 0 participants whose run differs from
`phase`; `metadata.csv` and `covariates.csv` equal to the primary's; every
key of `ANALYSIS_EXPECTED_COUNTS` for the analysis; no `diagnostics` key
(the rank-independent counts, 165 NMR features). Per variant:

| quantity | `raw_scale` | `log2_plus_one` | `glog` |
|---|---|---|---|
| p180 shape: \|skew\| > 1; largest \|z\| > 8 | 46; 12 | 14; 9 | 6; 6 |
| NMR shape: \|skew\| > 1; largest \|z\| > 8 | 43; 4 | 30; 4 | 25; 13 |
| numerical rank p180; NMR | 133; 104 | 133; 165 | 133; 165 |
| p180 phase \|d\| > 0.5 / > 1 | 108 / 76 | 108 / 80 | 109 / 80 |
| NMR phase \|d\| > 0.5 / > 1 | 2 / 0 | 2 / 0 | 2 / 0 |
| median below the offset (p180; NMR) | n/a | 46; 129 | n/a |

The ranks are not predeclared. A deviation is a finding, never a stop.
Findings also record:
- every finding of `export` and `analyze`;
- a QC hash that differs from its predeclared value, and a metabolite
  without a NIST column;
- for `nmr_all_columns`, the rule's columns differing from the primary's;
- a variant rank that differs from the primary's;
- a statistic whose status differs, under the variant's label and rule
  set;
- a primary read with `n_jobs ≠ 1`, and stale diagnostics.

Diagnostics on a variant: the second command above writes the six files of
`axis-diagnostics` under `diagnostics/`, with `is_primary` false. The
expected counts are the rank-independent ones, or the variant's own
`diagnostics` counts when its entry holds them (`nmr_all_columns`: 245 NMR
features; the scale variants hold none). Its `diagnostics.md` names the
variant and the block it changes (for a scale variant, an export whose
scale differs), and prints `READING_RULES` and the variant's rule set. The
bridged block keeps a run axis: in the spike, a shift common to most
metabolites puts the run on PC2, ρ 0.58. A flagged row is a
measurement-space finding about the variant and never grounds to adopt it.

Each variant carries one rule set, named by the convention
`EXPORT_VARIANT_RULE_SETS` (an import-time assertion keeps it in step with
the registry). The entry also gives the word readers cite ("variant rule
N", "membership rule N", "scale rule N") and the dependence label. The two
p180 variants carry `EXPORT_VARIANT_READING_RULES`; `nmr_all_columns`
carries `NMR_MEMBERSHIP_READING_RULES`; the three scale variants share
`SCALE_VARIANT_READING_RULES`. Rules 1, 2, 3, 6 and 7 have the same roles
in every set.

Reading rules of the p180 variants (`EXPORT_VARIANT_READING_RULES`, written
before any run and printed verbatim after `READING_RULES` in each
variant's `summary.md`, `export_sensitivity.md`, a variant's
`diagnostics.md` and every report that quotes a variant), in brief: a variant never replaces the primary
and no variant result changes a constant, reruns the primary or adopts a
variant; a variant differs from the primary only in the p180 values, so a
differing status is dependence on the handling of the p180 run; its rank,
floor, eigengap and null summary are read beside its `angle`;
`nist_bridge` removes the calibration part of the run offset that NIST
carries, assuming one factor per metabolite shared by plasma and serum,
and leaves a common shift, sample handling (aspartate, glutamate) and the
seven unbridged metabolites to `phase`; `per_run_standardized` removes the
whole run difference, stage composition included, and a difference
between the two variants is the part that is not calibration, never
evidence for either; a variant's non-rejection is no more informative
than the primary's and a variant-only rejection is run-handling
dependence; the run offset per block and the bridge factors are reported
beside the results, and a variant axis in the diagnostic is a
measurement-space finding.

Reading rules of the membership variant (`NMR_MEMBERSHIP_READING_RULES`,
decided by `adni-nmr-all-columns` before any run and printed verbatim after
`READING_RULES` in its `summary.md`, `export_sensitivity.md`,
`diagnostics.md` and every report that quotes it), in brief:
1. `nmr_all_columns` never replaces the primary, and no result of it
   changes a constant (`EXPORT_FEATURE_RULE` included).
2. It differs from the primary only in the NMR block's membership, so a
   differing status is feature-membership dependence.
3. Its rank, floor, eigengap and null summary are read beside its
   `angle`.
4. The 80 derived columns add no measurement, only weight and tails to
   the lipoprotein directions they are computed from.
5. It is not a reproduction of the 2022 study.
6. Its non-rejection is no more informative than the primary's, and a
   rejection only in the variant is membership dependence.
7. The block shares, the NMR shape counts, the run offset and the loading
   shares are reported beside the results.
8. It is read against the primary only.

Reading rules of the scale variants (`SCALE_VARIANT_READING_RULES`,
decided by `adni-scale-variants` before any run, shared by the three and
printed verbatim after `READING_RULES` in each one's `summary.md`,
`export_sensitivity.md`, `diagnostics.md` and every report that quotes
it), in brief:
1. A scale variant never replaces the primary, and no result of it changes
   a constant (the scale of `EXPORT_FEATURE_RULE` included).
2. It differs from the primary only in the scale of both blocks; each
   participant's rank on each feature is the primary's and the spacing
   changes, so a differing status is scale dependence.
3. Its rank, floor, eigengap and null summary are read beside its
   `angle`.
4. `log2_plus_one` and `glog` keep the log and change its offset;
   `log2_plus_one` is not a reproduction of the 2022 study, and `glog`
   carries left tails.
5. `raw_scale` has right tails and an NMR block of numerical rank 104; a
   difference reflects those tails and that geometry.
6. Its non-rejection is no more informative than the primary's, and a
   rejection only in a variant is scale dependence.
7. The shape counts, numerical ranks, run offset and offsets per
   metabolite are reported beside the results.
8. It is read against the primary only, never against another scale
   variant.

## `stage-sensitivity`

```
uv run adni-sexdiff stage-sensitivity [--input-dir DIR] [--analysis-dir DIR] [--cohort-dir DIR] [--out-dir DIR] [--n-jobs N] [--force]
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_stage_sensitivity/motco_input --analysis-dir results/motco_stage_sensitivity/analysis --out-dir results/motco_stage_sensitivity/diagnostics [--force]
```

A sensitivity step, read beside the primary and never replacing it
(change `adni-stage-sensitivity`). `STAGE_RULE` merges SMC into CN and
EMCI and LMCI into MCI, and SMC and EMCI were enrolled only in ADNI-GO/2,
so inside the primary's CN and MCI the two runs hold different
diagnoses and the additive `phase` coefficient carries both the run
offset and that difference. The export variants handle the measurement
side of the run; this arm handles the design side. `STAGE_SENSITIVITY_ARM`
is `cn_lmci_ad`: the exported participants whose `dx_bl` (`cohort.csv`,
ADNIMERGE `DX.bl` on the baseline row) is CN, LMCI or AD, staged by
`STAGE_RULE`'s own map (CN → CN, LMCI → MCI, AD → AD; three import-time
assertions tie the arm to `STAGE_RULE`), SMC and EMCI dropped; the
primary export's rows of those participants, every cell unchanged (the
primary's floors and scale; nothing re-exported); every analysis setting
the primary's (`ANALYSIS_*`, MOTCO's defaults, no latent adjustment,
`n_jobs = 1` for the reported run, one `analyze_trajectories` call
through the code `analyze` uses). The arm is not crossed with the latent
adjustment or an export variant. The arm and its rule are constants,
never flags; `--input-dir`, `--analysis-dir` and `--cohort-dir` name the
primary and the cohort to read.

What it changes, from the change's spike (`openspec/changes/archive/2026-10-29-adni-stage-sensitivity/spike.md`):
each stage holds one `DX.bl` category in both runs, so the `phase`
coefficient is estimated within one diagnosis. It does not balance the
runs across stages (ADNI-1 share CN 0.527, MCI 0.700, AD 0.544, against
0.417, 0.446, 0.544 in the primary) and does not remove the run offset,
which is measurement (p180 median |d| 1.10 on its rows against 1.12, PC1
correlation 0.71 against 0.73).

Inputs: the primary export `results/motco_input/` (the five files, checked
as `analyze` checks them, and the four CSVs read as bytes for the copy; no
feature table), the primary's `result.json` and `analysis_manifest.json`
(read, never written) and `results/cohort/` (`cohort.csv`, the source of
`dx_bl`, and `cohort_manifest.json`). No data-root file, no cleaned table,
nothing under a diagnostics directory.

Checks, in this order, before anything is written (a failure names the
file or setting, both values or counts and the command to rerun, never a
participant, and nothing is created under the output root): the gates of
`analyze`; an existing `motco_input/`, `analysis/` or `comparison/`
without `--force`; the primary export against its manifest, and that it
is the primary (no arm or variant recorded); the primary analysis as a
chained reference (its recorded export hashes, no latent adjustment, the
installed MOTCO, the seed and permutations); the cohort chain
(`cohort.csv` against its manifest, the manifest against the export
manifest's record, the both-flag rows the exported participants in order,
with equal sex and stage); every `dx_bl` in `STAGE_RULE`'s map; and every
kept row's stage equal to the arm's map of its `dx_bl`.

Outputs under `results/motco_stage_sensitivity/`, each subdirectory
staged as `<sub>.tmp/` and the three renamed together when complete;
`--force` replaces them, and replacing the arm while `diagnostics/`
exists is a finding (stale until `axis-diagnostics` is rerun). Two pinned
runs write byte-identical CSVs, `summary.md` and `stage_sensitivity.md`;
`result.json` differs only in MOTCO's runtime:

| file | content | committed / synced |
|---|---|---|
| `motco_input/p180.csv`, `nmr.csv`, `metadata.csv`, `covariates.csv` | the primary export's header and the lines of the kept participants, in export order, copied as bytes (every row the primary's; no `dx_bl` written) | no (participant-level; matched by `results/motco_stage_sensitivity/motco_input/*.csv`) |
| `motco_input/manifest.json` | step `stage-sensitivity`; `stage_arm` (the constant by name); the primary export as `reference` (its manifest hash, the four files copied, its feature tables' hashes as the source of the floors, its cells, runs within stage, covariate levels and run offset); the cohort chain; the primary's settings (`block_columns`, covariate codings); the counts (kept, dropped per `dx_bl`, `dx_bl` × sex, cells, runs within stage, levels, features, missing covariate values, non-finite cells, `rows_equal_primary` per file, and per block the shape counts, spectrum and run offset on the arm's rows); `STAGE_SENSITIVITY_EXPECTED_COUNTS["export"]` beside them with deviations; output hashes; findings | yes (aggregate, no `RID`) |
| `analysis/result.json`, `pls_loadings.csv`, `stage_means.csv` | as for the primary | yes (aggregate) |
| `analysis/latent_scores.csv`, `analysis_metadata.csv` | as for the primary | no (participant-level; matched by `results/**/`) |
| `analysis/analysis_manifest.json` | step `stage-sensitivity`; the arm export's five files as inputs; `stage_arm`; the primary as `reference` (its two hashes, rank, MOTCO, `n_jobs`, its export); every setting as the primary's; `cli_equivalent`; the arm's `analysis` expected counts with deviations; findings | yes (aggregate) |
| `analysis/summary.md` | the primary's renderer with the arm's title, an "Arm" section (the participants by `dx_bl` × sex, the cells, runs within stage and covariate levels of both, the run offset per block of both), the arm's note on each reading line and `STAGE_SENSITIVITY_READING_RULES` after `READING_RULES` | yes (aggregate) |
| `comparison/stage_sensitivity.csv` | the primary row then the arm row: participants, selected rank and mode, `cv_mean_auroc`, CV repeats, eigengap, per statistic observed, p, rejection, null mean, SD and q95; every value read from the two records | yes (aggregate) |
| `comparison/stage_sensitivity.md` | the statistics with a status per statistic (`same`, or `differs (stage-definition dependence)`; the primary's status is the result either way), the arm's reading lines, the latent spaces, the arm section, the findings, `READING_RULES` then `STAGE_SENSITIVITY_READING_RULES` | yes (aggregate) |
| `comparison/stage_sensitivity_manifest.json` | the nine inputs (the primary export's five files, the primary's two, the cohort's two) with sha256 and chains; the settings; the arm's own files; the counts (statuses, ranks, participants, cells, levels, runs within stage, run offsets); both expected counts and deviations; output hashes; findings | yes (aggregate) |
| `diagnostics/` (six files) | `axis-diagnostics` on the arm, run with the second command above | yes (aggregate) |

Predeclared counts (`STAGE_SENSITIVITY_EXPECTED_COUNTS`, from the committed
`stage_counts.csv` and the spike, none from a run of the arm): `export`
1130 participants kept, SMC 96 and EMCI 275 dropped, cells Female CN 183,
MCI 187, AD 125 and Male CN 181, MCI 296, AD 158, runs within stage
(ADNI1 / ADNI2GO) CN 192 / 172, MCI 338 / 145, AD 154 / 129, features p180
133 and NMR 165, every row of the four CSVs equal to the primary's, 0
missing covariate values and non-finite cells, p180 metabolites with
phase |d| > 0.5 / > 1 at 107 / 77 (NMR > 1 at 0); `analysis` every key of
`ANALYSIS_EXPECTED_COUNTS` with 1130 participants, the cells above and the
levels `apoe4` 589 / 413 / 128, `phase` 684 / 446, `statin` 603 / 527;
`diagnostics` the rank-independent keys with the arm's participants and
cells. The arm's rank is not predeclared. A deviation is a finding, never
a stop. Findings also record every finding of `analyze`, rows read back
that differ from the primary's, an arm rank that differs from the
primary's, a statistic whose status differs (stage-definition
dependence), a primary read with `n_jobs ≠ 1` and stale diagnostics.

Diagnostics on the arm: the second command above writes the six files of
`axis-diagnostics` under `diagnostics/`, with `is_primary` false,
`stage_arm` `cn_lmci_ad`, the cohort check on the both-flag rows the arm
keeps, the arm's participants and cells expected, and a `diagnostics.md`
that names the arm and prints both sets of reading rules. In the arm
`dx_bl` orders the participants as `stage` does, so their correlations
coincide; a flagged row is a measurement-space finding about the arm and
never grounds to adopt it.

Reading rules (`STAGE_SENSITIVITY_READING_RULES`, written before any run
and printed verbatim after `READING_RULES` in the arm's `summary.md`,
`stage_sensitivity.md`, the arm's `diagnostics.md` and every report that
quotes the arm), in brief: the arm never replaces the primary, and no arm
result changes a constant, `STAGE_RULE` or `COHORT_RULE`, reruns the
primary or adopts the arm; the arm differs in the participants (its CN is
`DX.bl` CN, its MCI is LMCI) and so in its z-scoring, CV folds, basis,
rank, reference row and permutation draws, and a differing status is
dependence on the stage definition and the sample; its rank, floor,
eigengap and null summary are read beside its `angle`; `phase` is
estimated within one diagnosis per stage while the runs stay unbalanced
and the run offset stays; the arm's MCI is a later, narrower stage, and
`angle` reads the endpoints (the AD cells are the primary's, the CN cells
lose SMC); a non-rejection is no more informative than the primary's and
an arm-only rejection is stage-definition dependence; the cells, runs
within stage and run offset are reported beside the results; the arm is
read against the primary only, never against another sensitivity.

## `rank-sensitivity`

```
uv run adni-sexdiff rank-sensitivity [--input-dir DIR] [--analysis-dir DIR] [--out-dir DIR] [--n-jobs N] [--force]
uv run adni-sexdiff axis-diagnostics --analysis-dir results/motco_rank_sensitivity/rank_12 --out-dir results/motco_rank_sensitivity/diagnostics [--force]
```

A sensitivity step, read beside the primary and never replacing it
(change `adni-rank-sensitivity`). The rank is the one quantity that moved
in every other sensitivity (the CV selected 8 for the primary, 4 for the
latent arm, 6 for `nist_bridge`, 4 for `per_run_standardized` and 6 for
the CN / LMCI / AD arm); this step measures how the primary's own `delta`,
`angle` and `shape` move with the rank alone, on the primary's data, with
everything else held fixed. `RANK_SENSITIVITY_LADDER` is
`forced_rank_ladder`: the primary's analysis at the forced ranks 2, 3, 4,
6, 9 and 12 (2 the rank floor and `n_stages − 1`, 3 the next rank, 4, 6, 9
and 12 the steps of MOTCO's rank ladder and of the template's sweep), with
MOTCO's `forced_components` set to the rank, which skips MOTCO's
cross-validation, and every other setting the primary's (the primary
export, `ANALYSIS_*`, MOTCO's defaults, no latent adjustment, the same
seed and permutations at every rank, `n_jobs = 1` for the reported run,
one `analyze_trajectories` call per rank through the code `analyze`
uses). Three import-time assertions keep the ranks ordered, the lowest
`ANALYSIS_RANK_FLOOR` and the diagnosed rank the top. The sweep is not
crossed with the latent adjustment, an export variant or the CN / LMCI /
AD arm. The ladder is a constant, never a flag; `--input-dir` and
`--analysis-dir` name the primary to read.

What it rests on, from the change's spike
(`openspec/changes/archive/2026-10-30-adni-rank-sensitivity/spike.md`, synthetic data only):
PLS-DA components are nested (the latent scores at a forced rank k are
bit for bit the first k columns of a higher forced rank's), so a rank at
or below the primary's 8 measures the primary's own first components and
a rank above 8 adds components the cross-validation did not select; a
forced run at the CV-selected rank is the CV run, bit for bit; MOTCO
rejects a forced rank outside `[2, 298]` here, so rank 1 cannot be forced.
`pls_loadings.csv` (the rotations) is not nested.

Anchor gate: before any rank runs, one forced run at the primary record's
rank, staged in `anchor.tmp/` through the path every rank takes, must
reproduce the primary: its statistics, p-values, null summaries,
`config_spectrum` and rank equal the primary's `result.json`, and its
`latent_scores.csv`, `pls_loadings.csv` and `stage_means.csv` hash to the
values the primary manifest records (no primary participant-level file is
opened). At `--n-jobs` other than 1 the draws differ, so only the
statistics, the rank, the pooled `config_spectrum` and the three files are
compared, and the record says so. A difference stops the step naming the
field or file, both values and the numerics state when it is not pinned,
with `anchor.tmp/` kept for inspection (ignored); on equality
`anchor.tmp/` is removed and every manifest records the anchor.

Inputs: the primary export `results/motco_input/` (the five files, checked
as `analyze` checks them) and the primary's `result.json` and
`analysis_manifest.json` (read, never written). No data-root file, no
cohort table, no feature table, nothing under a diagnostics directory.

Checks, in this order, before anything is written (a failure names the
file or setting, both values and the command to rerun, never a
participant, and nothing is created under the output root but, for a
failed anchor, `anchor.tmp/`): the gates of `analyze`; an existing rank
directory or `comparison/` without `--force`; the primary export against
its manifest, and that it is the primary (no arm or variant recorded);
the primary analysis as a chained reference (its recorded export hashes,
no latent adjustment, the installed MOTCO, the seed and permutations),
written by `analyze` with a CV-selected rank, its `result.json` hashing to
the value its manifest records; then the anchor gate.

Outputs under `results/motco_rank_sensitivity/`, each directory staged as
`<dir>.tmp/` and all renamed together when complete; `--force` replaces
them, and replacing the sweep while `diagnostics/` exists is a finding
(stale until `axis-diagnostics` is rerun). Before the renames each rank's
latent scores are compared in memory with the first columns of the top
rank's and of the anchor's (the nesting, recorded per rank; a false value
is a finding). Two pinned runs write byte-identical CSVs, `summary.md` and
`rank_sensitivity.md`; `result.json` differs only in MOTCO's runtime:

| file | content | committed / synced |
|---|---|---|
| `rank_<kk>/result.json`, `pls_loadings.csv`, `stage_means.csv` (six ranks, `rank_02` … `rank_12`) | as for the primary, at the forced rank (`component_selection` `forced`, no CV block) | yes (aggregate) |
| `rank_<kk>/latent_scores.csv`, `analysis_metadata.csv` | as for the primary | no (participant-level; matched by `results/**/`) |
| `rank_<kk>/analysis_manifest.json` | step `rank-sensitivity`; the primary export's five files as inputs; `settings.forced_components`; `rank_sweep` (the ladder by constant name, the forced rank, the primary's rank, the anchor's result); the primary as `reference` (its two hashes, rank, MOTCO, `n_jobs`, its export); every setting as the primary's; `cli_equivalent` with `--forced-components`; `RANK_SENSITIVITY_EXPECTED_COUNTS["analysis"][k]` beside the counts with deviations; findings | yes (aggregate) |
| `rank_<kk>/summary.md` | the primary's renderer with the forced rank in the title and header, the `angle` note naming the forced rank, the CV line saying MOTCO skips the cross-validation, a "Rank sweep" section (the ladder, this rank's place in it, the nesting relative to the primary's rank, the anchor, the rank-specific loadings), the sweep's note on each reading line and `RANK_SENSITIVITY_READING_RULES` after `READING_RULES` | yes (aggregate) |
| `comparison/rank_sensitivity.csv` | the primary row then one row per rank in ladder order: rank and mode, `cv_mean_auroc`, CV repeats, eigengap, per statistic observed, p, rejection, null mean, SD and q95; every value read from the records | yes (aggregate) |
| `comparison/rank_sensitivity.md` | the statistics with a status per statistic and rank (`same`, or `differs (rank dependence)`; the primary's status is the result), one status sentence per statistic, each rank's reading lines, the latent spaces (rank, floor, eigengap with its permutation quantiles, the `angle` null), the anchor and the nesting, the findings, `READING_RULES` then `RANK_SENSITIVITY_READING_RULES` | yes (aggregate) |
| `comparison/rank_sensitivity_manifest.json` | the seven inputs (the primary export's five files, the primary's two) with sha256 and chains; the settings; the reference and the anchor; per rank its directory, `result.json` and manifest hashes, deviations and findings; the counts (statuses, ranks, eigengaps, rejections, nesting); the expected counts and deviations; output hashes; findings | yes (aggregate) |
| `diagnostics/` (six files) | `axis-diagnostics` on the top rank, run with the second command above | yes (aggregate) |

Predeclared counts (`RANK_SENSITIVITY_EXPECTED_COUNTS`, from the committed
primary manifests and the ladder, none from a forced run on ADNI data):
`anchor` rank 8; `analysis`, per rank, every key of
`ANALYSIS_EXPECTED_COUNTS` (1501 participants, the primary's cells,
features, design columns and levels, 0 dropped, floor 2, 9999
permutations) with selection `forced`, the rank and 0 CV repeats;
`comparison` 7 rows; `diagnostics` the rank-independent keys, the read
(rank 12, `forced`, no latent adjustment, `n_jobs` 1) and rows 96 / 48 /
48 / 12. No rank's statistic or status is predeclared. A deviation is a
finding, never a stop. Findings also record every finding of `analyze`
that applies to a forced run (the conditions of the cross-validation are
not raised), a primary rank other than the predeclared anchor rank, a
statistic whose status at a rank differs from the primary's (rank
dependence), a nesting check that fails, a primary read with `n_jobs ≠ 1`
and stale diagnostics.

Diagnostics on the sweep: the second command above writes the six files
of `axis-diagnostics` for the top rank under `diagnostics/`. By nesting
its components hold every rank's, so one diagnostic covers the sweep: its
`pls_0` … `pls_7` rows of `axis_correlations.csv` are the primary's, and
`block_pcs.csv` does not depend on the analysis; `geometry_shares.csv` and
`components.csv` are the rank's own.

Reading rules (`RANK_SENSITIVITY_READING_RULES`, written before any run
and printed verbatim after `READING_RULES` in each rank's `summary.md`,
`rank_sensitivity.md`, the top rank's `diagnostics.md` and every report
that quotes the sweep), in brief: the sweep never replaces the primary,
whose rank is its CV-selected 8, no rank is chosen, adopted or ranked and
no sweep result changes a constant (the floor and the ladder included),
reruns the primary or defines another arm; every rank is the primary
with `forced_components` changed and the same draws, so a differing
status is rank dependence; the components are nested and the anchor
reproduces the primary exactly; each `angle` is read against its own
null; MOTCO's forced-rank evidence is its unadjusted rank ladder (MOTCO
0.6.0, n = 1200), with no Type I or power check at a forced rank at this
design or with covariates, so a non-rejection is no more informative
than the primary's and a forced-rank-only rejection is rank dependence;
the sweep is not a test (nothing combines the ranks, picks the smallest p
or counts rejections); the top rank's diagnostic is reported beside the
sweep, an added component that tracks `phase` a measurement-space
finding; the sweep is read against the primary only.

## `report`

```
uv run adni-sexdiff report [--cleaned-dir DIR] [--cohort-dir DIR] [--input-dir DIR] [--analysis-dir DIR] [--diagnostics-dir DIR] [--sensitivity-dir DIR] [--export-sensitivity-dir DIR] [--stage-sensitivity-dir DIR] [--rank-sensitivity-dir DIR] [--operating-characteristics-dir DIR] [--out FILE] [--force]
uv run adni-sexdiff report --check [--out FILE] [the same directory flags]
```

The last step of the pipeline (changes `adni-report`,
`adni-report-variants`, `adni-report-stage-arm`, `adni-report-rank-sweep`,
`adni-report-nmr-all-columns`, `adni-report-scale-variants` and
`adni-operating-characteristics`): the case-study report, generated in full from
the kept aggregate outputs, and its check. Thirteen flags; every directory
default is the pipeline's directory (`results/cleaned`, `results/cohort`,
`results/motco_input`, `results/motco_analysis`,
`results/motco_diagnostics`, `results/motco_latent_sensitivity` read as
`analysis/`, `comparison/` and `diagnostics/`,
`results/motco_export_sensitivity` read per variant of
`REPORT_EXPORT_VARIANTS` as `bridge/`, `motco_input/`, `analysis/`,
`comparison/` and `diagnostics/`, `results/motco_stage_sensitivity` read as
`motco_input/`, `analysis/`, `comparison/` and `diagnostics/`,
`results/motco_rank_sensitivity` read as one `rank_<kk>/` per rank of
`RANK_SENSITIVITY_LADDER`, then `comparison/` and `diagnostics/`), and
`--operating-characteristics-dir` defaults to `references/motco_adni_design`,
the committed copy of the cited MOTCO decision; every
variant of `REPORT_EXPORT_VARIANTS`, the CN / LMCI / AD arm, the rank
sweep and the copy are required and no flag selects what is reported.

The report's pin (`REPORT_EXPORT_VARIANTS`, change
`adni-nmr-all-columns`) holds the variants it covers, a subsequence of
`EXPORT_VARIANTS` in registry order (an import-time assertion): since
change `adni-report-scale-variants` all six, `nist_bridge`,
`per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one`
and `glog` (`nmr_all_columns` added by change
`adni-report-nmr-all-columns`, the three scale variants by change
`adni-report-scale-variants`). A variant registered later and left
outside it is not read or required and leaves the body unchanged;
`report` names it on a progress line ("export variant … is registered and
not covered by this report"), never in the report, so the newest report
stays checkable until the report change that adds the variant to the pin
and re-issues the report. Every registered variant is in the pin, so no
such line is printed. `--out` must be named `reports/motco-adni-<date>.md`
(`REPORT_NAME`) by the day it is written or, for a later report of the same
day, `reports/motco-adni-<date>-<n>.md` with `<n>` 2 or more
(`REPORT_NAME_SAME_DAY`, change `adni-report-scale-variants`; `-1` and any
other name stop the step), so no report is written over a committed one:
the date and the ordinal are read from the name and written in the title
line only (`… — 2026-11-02, report 2`). Write mode defaults to today's
name without an ordinal and, when that file exists without `--force`,
stops naming the next free same-day name to pass with `--out` (it never
picks one itself); `--check` defaults to the newest report under
`reports/` by the date in its name, then by its ordinal.

Inputs (`REPORT_INPUT_FILES`, 146 files with 45 manifests, all
committed): the two `clean_manifest.json`; `stage_counts.csv` and
`cohort_manifest.json`; the export `manifest.json`; the primary's
`result.json`, `analysis_manifest.json` and `summary.md`; the primary
diagnostics' six files; the arm's three aggregate analysis files, the
comparison's three files and the arm diagnostics' six files; and per
variant of `REPORT_EXPORT_VARIANTS`, in registry order, `bridge/nist_bridge.csv` (hook `factors`
only), `motco_input/manifest.json`, the variant analysis' three aggregate
files, the comparison's three files (`export_sensitivity.csv`,
`export_sensitivity.md`, `export_sensitivity_manifest.json`) and the
variant diagnostics' six files (14 for `nist_bridge`, 13 each for
`per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one`
and `glog`); and under `results/motco_stage_sensitivity/`
(`REPORT_STAGE_ARM_FILES`) the CN / LMCI / AD arm export's
`motco_input/manifest.json`, the arm analysis' three aggregate files, the
comparison's three files (`stage_sensitivity.csv`, `stage_sensitivity.md`,
`stage_sensitivity_manifest.json`) and the arm diagnostics' six files (13);
and under `results/motco_rank_sensitivity/` (`REPORT_RANK_SWEEP_FILES`,
change `adni-report-rank-sweep`), per rank of `RANK_SENSITIVITY_LADDER` in
ladder order, `rank_<kk>/result.json`, `analysis_manifest.json` and
`summary.md`, then the comparison's three files (`rank_sensitivity.csv`,
`rank_sensitivity.md`, `rank_sensitivity_manifest.json`) and the top
rank's diagnostics' six files (27); and under `references/` (change
`adni-operating-characteristics`) the committed copy of the cited MOTCO
decision, `motco_adni_design/adni_design_decision.json`, copied byte for
byte at the commit `OPERATING_CHARACTERISTICS_SOURCE` pins and never read
from a MOTCO clone (1).
Nothing else: no participant-level file is opened or required
(`cohort.csv`, the export CSVs of the primary, of every variant and of the
CN / LMCI / AD arm, `latent_scores.csv` and `analysis_metadata.csv` are
quoted by the hashes the manifests record; the arm analysis' and every
rank's `stage_means.csv` and `pls_loadings.csv` too, as the other
analyses'),
no data root, no MOTCO call and no
pinned numeric environment, so the step runs on any clone with the
committed tree and records no numerics.

Gates, before anything is written, each stopping naming the file or
setting, both values and the step to rerun: every input present (an
absent copy names the `git show` command that restores it from the pinned
MOTCO commit); every
aggregate file hashes to the value its own manifest records under
`outputs` (manifests are hashed for the chain, not checked against
themselves), and the copy to the sha256 `OPERATING_CHARACTERISTICS_SOURCE`
pins (it is neither among the 99 manifest-checked files nor a chain link); the primary is the primary (no latent adjustment,
`is_primary` true in its diagnostics) and the arm is
`LATENT_SENSITIVITY_ARM` (`is_primary` false in its diagnostics); each
variant directory holds its variant (its export, analysis and comparison
manifests name it, its export manifest's `variant` block equals its
`EXPORT_VARIANTS` entry, its analysis records no latent adjustment, its
diagnostics record `is_primary` false and its name), so swapped variant
directories are named as a swap, and then the bridge table hashes to the
`bridge.table.sha256` of its export manifest; the CN / LMCI / AD arm is
`STAGE_SENSITIVITY_ARM` (its export manifest records step
`stage-sensitivity`, every field of the constant in its `stage_arm` block
and no `variant` block, its analysis and comparison manifests name the arm,
its analysis records no latent adjustment, its diagnostics record
`is_primary` false and the arm), so a crossed or swapped arm directory is
named as such; the rank sweep is `RANK_SENSITIVITY_LADDER` (each rank
directory holds its rank: its manifest records step `rank-sensitivity`,
`settings.forced_components` and `rank_sweep.forced_rank` equal to the
directory's rank, its record `latent.selected_lv` equal to it with
selection `forced`; its `rank_sweep.ladder` holds every field of the
constant and its `rank_sweep.primary_rank` the primary record's rank; it
records no latent adjustment and no `variant` or `stage_arm` block; the
comparison manifest records step `rank-sensitivity`, the constant, exactly
the ladder's directories and an anchor equal at the primary record's rank;
the diagnostics record `is_primary` false and the forced rank
`diagnosed_rank`, 12), so swapped rank directories, a latent-adjusted
analysis in a rank directory, a moved ladder or an unanchored sweep is
named as such; the primary, the arm, every variant analysis, the
CN / LMCI / AD arm's analysis and every rank are reported runs
(`n_jobs = 1` in manifest and record), every `numerics` block present
records `pinned` true, and all 45 manifests record the same MOTCO,
scikit-learn and metabo_adni versions (the clean, cohort and export
manifests, the variant and arm exports among them, record metabo_adni
only);
the chain holds link by link (255 links: the first report's 31 (the clean
manifests in the cohort and export manifests, the cohort manifest in the
export manifest, the export manifest and files in the four
analysis-reading manifests, the primary's two files as the arm's and the
comparison's `reference`, the arm's two files in the comparison and the
arm diagnostics), then per variant its export manifest against the clean,
cohort and primary export manifests, its analysis against its export and
the primary, its comparison against both analyses, both exports and the
bridge table, and its diagnostics against its analysis, its export and the
cohort manifest: 23 for `nist_bridge`, 22 each for `per_run_standardized`,
`nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`;
then 24 for the CN / LMCI / AD arm: its export manifest against the cohort
manifest, the primary export manifest (as input and as `reference`) and
the primary feature tables it names as the source of its floors (against
the primary export manifest's `outputs`), its analysis against its export
and the primary, its comparison against both analyses, both exports and
the cohort manifest, and its diagnostics against its analysis, its export
and the cohort manifest; then 67 for the rank sweep: per rank (8 each, 48)
its export manifest and its four export CSV hashes against the primary
export, the primary's two files and the primary export as its `reference`;
the comparison (15) against the primary's two files, every rank's
`result.json` and `analysis_manifest.json` and the primary export; and the
top rank's diagnostics (4) against the rank-12 analysis manifest, its
`result.json` as that manifest records it, the primary export manifest and
the cohort manifest). A variant, the CN / LMCI / AD arm or the sweep rerun
with `--force` after its diagnostics breaks the diagnostics link, whose
hint names its `axis-diagnostics` command with its directories; a
regenerated primary export breaks the arm export's `reference` links,
whose hint names `stage-sensitivity --force`, and a regenerated primary
breaks every rank's and the comparison's `reference` links, whose hint
names `rank-sensitivity --force`. Then the cited measurement (gate 6,
after the chain, so every committed value it reads has passed the gates
before it): the copy's `verdict` equals the constant's and `indicative` is
false, the keys of its `adni_reference` are exactly the report's map
(`_OPERATING_CHARACTERISTICS_REFERENCE`), and each of the 19 values equals
the committed value it describes at the decision's digits: the primary
record's rank, `cv_mean_auroc`, pooled relative eigengap, `angle` null q95,
design columns, `phase[ADNI2GO]` reference value and three p-values; the
export manifest's run offset and kept features per block; |ρ| of `pls_0`
with `phase` in the primary diagnostics; and the lowest and highest
`cv_mean_auroc` of the nine CV-selected analyses (the primary, the latent
arm, the six export variants, the CN / LMCI / AD arm). A difference names
the key, both values and the source, and says that the measurement was
calibrated against another analysis, so citing one for this analysis is a
new change. An existing `--out` stops write mode unless `--force`.

The report (`REPORT_SECTIONS`, fourteen level-2 sections in order): summary
(the primary's reading, then MOTCO's measured verdict and its three
statements per statistic, verbatim, citing "Operating characteristics";
one paragraph per group of export variants, naming its rule set and its
dependence label, with the rank and status lines of each variant, those of
the CN / LMCI / AD arm, the sweep's status lines, and the flagged components of every
diagnostics run, the top rank's among them); provenance (versions,
revisions and numerics per step, the 146 inputs
with their sha256 (the decision's copy beside the constant that pins it), the raw
LONI inputs as the clean and cohort manifests record them, the QC archives
and NIST workbooks beside their predeclared sha256 as the `nist_bridge`
export manifest records them, the chain links checked: the report's
manifest); cohort (the rules
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
operating characteristics (change `adni-operating-characteristics`:
MOTCO's size and power at this design, quoted from the decision's copy:
the citation with the pinned and observed sha256, MOTCO's decision rule,
the six size readings against their bound with the size sentence, the
power rate per target statistic and effect with its standard error and
CV-selected ranks, the floor per statistic, the three statements, and the
construction beside this design, each reference value with the committed
source gate 6 checked it against);
latent-adjustment sensitivity (the comparison with a status per
statistic, the status lines, the latent spaces, the arm's
`latent_adjustment` block, the covariate roles, MOTCO's two decisions, the
arm's diagnostics, the first component against `phase` beside the
primary's, the arm's `cli_equivalent`); export sensitivity (a lead that
names the groups, then one group of tables per rule set of
`EXPORT_VARIANT_RULE_SETS`, in registry order: the run-handling group,
`nist_bridge` and `per_run_standardized` under
`EXPORT_VARIANT_READING_RULES`, with the titles of the 2026-10-31 report,
the membership group, `nmr_all_columns` under
`NMR_MEMBERSHIP_READING_RULES`, its tables titled `nmr_all_columns: …`,
and the scale group (change `adni-report-scale-variants`), `raw_scale`,
`log2_plus_one` and `glog` under `SCALE_VARIANT_READING_RULES`, its shared
tables titled `raw_scale, log2_plus_one, glog: …` and each variant's
diagnostics `<variant>: …`; each group's tables hold the primary and that
group's variants only, so no table puts `nmr_all_columns` beside a p180
variant (membership rule 8) or a scale variant beside another export
variant (scale rule 8).
Each group: its lead, which names its rule set and cites its rules 1 and 2
(and the rule that reads its variants against the primary only,
`_GROUP_PRIMARY_ONLY_RULE`: membership rule 8, and scale rule 8, "each
variant is read against the primary only, never against another variant
of the group"); the statistics of
the primary and of each variant with a status per variant row, each
variant's rank, floor and eigengap beside `angle`, the status lines, the
latent spaces, the run offset per block of every export, each variant
export's counts beside `EXPORT_VARIANT_EXPECTED_COUNTS` (every key but
`analysis`, `phase_offset` and `diagnostics`, which the steps compare
themselves), the variant lines of `export_sensitivity.md`, for
`nist_bridge` the bridged metabolites per kit beside the predeclared
102 / 24 / 7 and the seven unbridged metabolites with their NIST
replicates (the full bridge table quoted by hash), for `nmr_all_columns`
its membership, derived columns kept, joint features, block shares and
NMR shape counts, for each scale variant its transform and offset, the
rule's floors recorded and not applied, its offset summary and per block
the shape counts and numerical rank of both exports (the scale counts
table `n/a` where a variant's entry has no such key, as
`scale.median_below_offset.*` for all but `log2_plus_one`), each
variant's diagnostics, the first component against
`phase`, each variant's `cli_equivalent`; every word that depends on the
variant, its rule set, citation word, dependence label and what it
changes, from `_variant_words`); stage-definition sensitivity
(the statistics of the primary and the CN / LMCI / AD arm with a status,
both ranks, floors and eigengaps beside `angle`, the status lines, the
latent spaces, the arm's bullets of `stage_sensitivity.md` and its four
tables under their own headings: the exported participants by `dx_bl` ×
sex, the sex × stage cells, the runs within each stage and the covariate
levels of the primary and the arm; the run offset per block of both beside
the predeclared counts, the arm export's counts beside
`STAGE_SENSITIVITY_EXPECTED_COUNTS`, the arm's diagnostics, the first
component against `phase`, the arm's `cli_equivalent`); rank sensitivity
(the statistics of the primary and of each forced rank in ladder order,
per statistic, with its rank and a status; `angle` read beside each rank's
floor, eigengap and own null; the status lines; the latent spaces, one row
per analysis with each eigengap and `angle` null summary; the anchor and
nesting bullets and the nesting table of `rank_sensitivity.md`; the
anchor rank, the comparison rows and each rank's selection, rank and CV
repeats beside `RANK_SENSITIVITY_EXPECTED_COUNTS`; the top rank's
diagnostics under sweep rule 7, with the flagged components after the
primary's rank in `components.csv` order; the first component against
`phase`; each rank's `cli_equivalent`); findings (every
deviation and finding of every manifest, verbatim under its step, then the
report's own: a dirty recorded revision, a manifest without a `numerics`
block); eight rule lists, verbatim: `READING_RULES`, then
`OPERATING_CHARACTERISTICS_READING_RULES` (the nine measurement rules,
change `adni-operating-characteristics`), then
`LATENT_SENSITIVITY_READING_RULES`, then one list per rule set of the
pinned variants in group order (`EXPORT_VARIANT_READING_RULES`, then
`NMR_MEMBERSHIP_READING_RULES`, then `SCALE_VARIANT_READING_RULES`), then
`STAGE_SENSITIVITY_READING_RULES`,
then `RANK_SENSITIVITY_READING_RULES`, each led by the line its own
documents print; the commands that
reproduce the pipeline (the variants, the CN / LMCI / AD arm, the rank
sweep and their diagnostics included) and check the report, and the
`git show` command that restores the decision's copy from the pinned MOTCO
commit. Every reference to another section is numbered from
`REPORT_SECTIONS`. Every table is
titled by a level-3 heading and keyed by its first column; every number is
copied from a record, a manifest, a CSV or the cited decision file at the
digits of the summary it belongs to (the decision's rates and standard
errors at three decimals, its bound at four; the step computes no
statistic, correlation, mean or count, and no value across the ranks of
the sweep); besides MOTCO's own sentences (its verdict, size sentence and
statements), quoted verbatim from the decision file and never used to
reread a sensitivity's status,
the only interpretive sentences are the ones `summary.md`,
`latent_sensitivity.md`, `export_sensitivity.md`, `stage_sensitivity.md`
and `rank_sensitivity.md` print, produced by the same code
(`_statistic_reading_line`, `_arm_status_line`,
`_export_variant_status_line`, `_stage_arm_status_line`,
`_rank_status_line`; the variant lines by `_export_variant_lines`, the
CN / LMCI / AD arm's bullets by `_stage_arm_lines` and its four tables by
`_stage_arm_tables`, the sweep's anchor and nesting bullets by
`_rank_anchor_lines` and its nesting table by `_rank_nesting_table`) so
that they are string-equal across the documents,
and no sentence reads one sensitivity against another (a sentence that
lists several, each beside the primary, compares none; no forced rank is
read against another sensitivity's CV-selected rank); the primary's
status is the result wherever the arm, a variant, the CN / LMCI / AD arm
or a forced rank appears, and `LATENT_SENSITIVITY_READING_RULES` is named
beside every table that quotes the arm, `EXPORT_VARIANT_READING_RULES`
beside every table that quotes a p180 variant,
`NMR_MEMBERSHIP_READING_RULES` beside every table that quotes
`nmr_all_columns`, `SCALE_VARIANT_READING_RULES` beside every table that
quotes a scale variant, `STAGE_SENSITIVITY_READING_RULES`
beside every table that quotes the CN / LMCI / AD arm and
`RANK_SENSITIVITY_READING_RULES` beside every table that quotes the sweep,
each with `READING_RULES`. The body depends on the inputs and the
file name only (no revision, host, time or runtime of the report run), so
two runs on the same inputs are byte-identical and two dates differ in the
title line alone. The file is written to `<out>.tmp`, parsed back through
the checker's parser and checked against the generated tables, then
renamed. It quotes aggregate values only and holds no participant
identifier.

`--check` first compares the report's level-2 headings with
`REPORT_SECTIONS`, then the export variants it lists (its level-3
headings ``Export variant `<name>` `` in "Export sensitivity", in order)
with `REPORT_EXPORT_VARIANTS` (change `adni-report-nmr-all-columns`): a
report written by an earlier layout (`reports/motco-adni-2026-10-28.md`,
ten sections, which checks at 36c9cc8, `reports/motco-adni-2026-10-29.md`,
eleven sections, which checks at c94f5e7,
`reports/motco-adni-2026-10-30.md`, twelve sections, which checks at
2e4a3e1, `reports/motco-adni-2026-10-31.md`, thirteen sections and two
export variants, which checks at 13ce7c8,
`reports/motco-adni-2026-11-02.md`, thirteen sections and three export
variants, which checks at 28e0d48, and
`reports/motco-adni-2026-11-02-2.md`, thirteen sections, which checks at
67567e2; since change `adni-operating-characteristics` added "Operating
characteristics" every one of them stops at the section gate, so no
committed report reaches the variant gate) stops before any gate, naming
its absent and extra sections or variants (or that their order differs)
and the command `git log -1 --format=%H -- <report>` that finds the
revision that committed it, where `report --check --out <report>` passes
in a worktree; nothing is compared or written and the CLI exits 1. Then it reads the
report, runs every gate, regenerates the report from
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
