# adni_sexdiff

Sex × stage (CN / MCI / AD) trajectory comparison on ADNI serum metabolomics
(Biocrates p180 and Nightingale NMR) with [MOTCO](https://github.com/tomszar/MOTCO):
the first MOTCO application at a well-powered design (n ≈ 1,300). Later ADNI
layers (lipidomics, proteomics, methylation) may be added as separate blocks.

**Status: scaffold.** Every pipeline step is a stub that raises
`NotImplementedError`; no data is in place and no statistical choice has been
made. `AGENTS.md` holds the conventions and the hard constraints and is the
single source of truth.

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
├── scripts/         # sync_results.sh (aggregate outputs between workstation and cluster)
├── src/
│   └── adni_sexdiff/
│       ├── cli.py         # argparse CLI: clean, cohort, export, analyze, axis-diagnostics, report
│       ├── constants.py   # conventions; scientific constants enter through OpenSpec proposals only
│       └── data.py        # pipeline steps (stubs with their output contracts)
├── openspec/        # change proposals and specs
├── flake.nix        # Python 3.12 + uv; the shell hook runs `uv sync --locked`
├── pyproject.toml   # package adni_sexdiff, CLI adni-sexdiff (uv, uv.lock committed)
├── LICENSE
└── README.md
```

Pipeline (each step reads the previous step's outputs only):

1. `clean` – metabo_adni per platform → `results/cleaned/<platform>/`
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
```

Dependencies: `motco` (git tag `v0.10.0`, via `[tool.uv.sources]`),
`metabo_adni==0.5.8` (cleaning, never reimplemented here), `pandas`, `numpy`.
