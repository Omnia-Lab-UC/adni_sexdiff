# adni_sexdiff

Sex × stage (CN / MCI / AD) trajectory comparison on ADNI serum metabolomics
(Biocrates p180 and Nightingale NMR) with [MOTCO](https://github.com/tomszar/MOTCO):
the first MOTCO application at a well-powered design (n ≈ 1,300). Later ADNI
layers (lipidomics, proteomics, methylation) may be added as separate blocks.

**Status: `clean` and `cohort` implemented** (changes `adni-metabolomics-clean`
and `adni-cohort`) and run on the workstation; every other step is a stub
that raises `NotImplementedError`. The statistical choices made so far are
`CLEAN_OPTIONS`, `COHORT_RULE`, `STAGE_RULE` and `ANALYSIS_COVARIATES`; the
feature rule, the analysis settings, the diagnostic variables and the reading
rules are undecided.
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
├── scripts/         # sync_results.sh (aggregate outputs between workstation and cluster), clean.sbatch (clean on the cluster)
├── src/
│   └── adni_sexdiff/
│       ├── cli.py         # argparse CLI: clean, cohort, export, analyze, axis-diagnostics, report
│       ├── constants.py   # conventions; scientific constants enter through OpenSpec proposals only
│       └── data.py        # pipeline steps (clean and cohort implemented; the others stubs with their output contracts)
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
3. `export` – MOTCO blocks + metadata → `results/motco_input/`
4. `analyze` – `motco.analysis.analyze_trajectories` → `results/motco_analysis/`
5. `axis-diagnostics` – what the latent and block axes correlate with →
   `results/motco_diagnostics/`
6. `report` – the case-study report from the generated files, or a check of
   one against them → `reports/`

Quick start:

```
direnv allow            # or: nix develop   (Python 3.12, uv, `uv sync --locked`)
uv run adni-sexdiff --help
uv run adni-sexdiff clean --platform all
uv run adni-sexdiff cohort
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

Dependencies: `motco` (git tag `v0.10.0`, via `[tool.uv.sources]`),
`metabo_adni==0.5.8` (cleaning, never reimplemented here), `pandas`, `numpy`.
