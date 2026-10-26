# adni_sexdiff

Sex × stage (CN / MCI / AD) trajectory comparison on ADNI serum metabolomics
(Biocrates p180 and Nightingale NMR) with [MOTCO](https://github.com/tomszar/MOTCO):
the first MOTCO application at a well-powered design (n ≈ 1,300). Later ADNI
layers (lipidomics, proteomics, methylation) may be added as separate blocks.

**Status: `clean` implemented** (change `adni-metabolomics-clean`) and run on
the workstation; every other step is a stub that raises `NotImplementedError`.
The one statistical choice made so far is `CLEAN_OPTIONS`; the cohort rule,
stage rule, covariates, feature rule and the analysis settings are undecided.
`AGENTS.md` holds the conventions and the hard constraints and is the single
source of truth.

**ADNI is controlled-access (DUA).** Nothing participant-level is ever
committed: no raw file, no cleaned matrix, no cohort table, no MOTCO input
block, no `latent_scores.csv`, no `analysis_metadata.csv`, no table with an
`RID`. `.gitignore` enforces it and `scripts/sync_results.sh` moves only
aggregate outputs between machines. Raw ADNI files are uploaded by hand to the
data root (`ADNI_DATA_ROOT`, default `data/`); there is no download step.

Project layout:

```
.
├── data/            # raw ADNI files, uploaded by hand: LONI archive under Metabolomics/, metabo_adni names as symlinks (gitignored)
├── reports/         # committed case-study reports (numbers pasted from results/, checked by script)
├── results/         # pipeline outputs; only aggregate files are committed (see .gitignore)
├── scripts/         # sync_results.sh (aggregate outputs between workstation and cluster), clean.sbatch (clean on the cluster)
├── src/
│   └── adni_sexdiff/
│       ├── cli.py         # argparse CLI: clean, cohort, export, analyze, axis-diagnostics, report
│       ├── constants.py   # conventions; scientific constants enter through OpenSpec proposals only
│       └── data.py        # pipeline steps (clean implemented; the others stubs with their output contracts)
├── openspec/        # change proposals and specs
├── flake.nix        # Python 3.12 + uv; the shell hook runs `uv sync --locked`
├── pyproject.toml   # package adni_sexdiff, CLI adni-sexdiff (uv, uv.lock committed)
├── LICENSE
└── README.md
```

Pipeline (each step reads the previous step's outputs only):

1. `clean` – metabo_adni per platform → `results/cleaned/<platform>/` (below)
2. `cohort` – baseline visit per participant, sex, merged stage, covariates,
   platform intersection, group × stage counts → `results/cohort/`
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

Dependencies: `motco` (git tag `v0.10.0`, via `[tool.uv.sources]`),
`metabo_adni==0.5.8` (cleaning, never reimplemented here), `pandas`, `numpy`.
