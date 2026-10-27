# Design

## Context

See `proposal.md` for the settings and the reading rules. The state that shapes the approach:

- **The stubs and the CLI.** `run_analysis` and `check_motco_version` are stubs in `src/adni_sexdiff/data.py`; the `run_analysis` docstring states the output contract. `cli.py` exposes `analyze --input-dir --out-dir --n-jobs --force` with `--n-jobs` defaulting to `REPORTED_N_JOBS`. `ANALYSIS_MOTCO_MIN_VERSION = "0.10.0"`, the output file names (`ANALYSIS_RESULT` … `ANALYSIS_SUMMARY`) and `MOTCO_ANALYSIS_DIR` exist in `constants.py`.
- **Helpers from the earlier steps.** `_sha256_file`, `_git_revision`, `_software_versions` (its package list lacks `motco` and `scikit-learn`), `_write_manifest`, `_finalize_output_dir` and `_count_deviations` are reused.
- **The export.** `results/motco_input/manifest.json` records under `outputs.<file>.sha256` every CSV, under `settings` the block order, `block_columns`, the covariate codings copied from the cohort manifest (`ANALYSIS_COVARIATES` with `coding`, `levels`, `map`), `covariates_applied` false and `motco_transform` identity, and under `counts` participants, `sex_stage`, features, `block_shares`, `phase_offset`. `covariates.csv` holds `apoe4` and `statin` as integers and `phase` as a string.
- **MOTCO 0.10.0** (`uv.lock`: git rev `v0.10.0`, commit `098b170`). `TrajectoryDataset(blocks, metadata, sample_col, group_col, stage_col, stage_order, group_order, covariate_cols, categorical_covariates, missing_covariates)`; a covariate is categorical when listed in `categorical_covariates` or non-numeric, levels compared as strings, drop-first indicators with the first level as reference, LS-means at the pooled covariate mean. `TrajectoryAnalysisParams(permutations, seed, n_jobs, orientation_estimator="net_displacement", forced_components=None, cv1_splits=3, cv2_splits=4, n_repeats=5, max_components=20, random_state=1203, covariate_latent_adjustment=None, min_components=2)`. `write_analysis_outputs(result, out_dir, overwrite=False)` writes the four artifact files. The record's top-level keys: `schema_version`, `statistics`, `p_values`, `null_summary`, `config_spectrum` (with `pooled.relative_eigengap`), `latent` (`selected_lv`, `component_selection`, `cv_mean_auroc`, `cv_repeats_completed`, `integration_params.min_components`), `design` (`cell_sizes`, levels), `covariates` (`columns`, `kinds`, `levels`, `reference_levels`, `design_columns`, `reference_row`, `missing_policy`, `n_dropped`, `dropped_sample_ids`, `coefficients`), `blocks`, `measurement`, `params`, `software`, `attribution`. `motco analyze` takes `--block NAME=PATH`, `--metadata`, `--sample-col`, `--group-col`, `--stage-col`, `--stage-order`, `--group-order`, `--covariate`, `--categorical-covariate`, `--missing-covariates`, `--permutations`, `--seed`, `--n-jobs`, `--min-components`, `--out-dir`. The synthetic check at the ADNI shape (1501 × 298, the six design columns, 9999 permutations, `n_jobs = 1`) ran in 25 s and produced the design columns `age`, `education`, `apoe4[1]`, `apoe4[2]`, `phase[ADNI2GO]`, `statin[1]` from integer-coded `apoe4` and `statin` declared categorical.
- **MOTCO's RRPP and `n_jobs`.** The parallel path seeds one stream per worker, so `n_jobs` changes the draws (template task 3.3, 2026-10-19). Reported runs use `n_jobs = 1`.
- **Ignore rules.** `results/**/latent_scores.csv` and `results/**/analysis_metadata.csv` are already in `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS`.
- **The template.** `../sead_sexdiff/src/sead_sexdiff/data.py` holds `check_motco_version`, `check_motco_rank_floor`, `load_analysis_inputs`, `_analyze_cohort`, `_cli_equivalent` and `render_analysis_summary` for a per-cohort, numeric-covariate design; the adaptation here is one cohort, categorical covariates, this repo's manifest layout and the reading rules.

## Goals / Non-Goals

**Goals:**
- One command from the export outputs to MOTCO's artifact plus a manifest and summary that make the run reproducible by hand and readable without the participant-level files.
- Every setting a constant, recorded in the manifest, never a flag; `--n-jobs` the only runtime knob, and one that cannot change a reported result silently.
- The reading rules in the summary itself, so no report can quote the numbers without them.

**Non-Goals:**
- Any sensitivity arm, diagnostic or report (steps 5 and 6 and the follow-up changes).
- A test framework; verification is a synthetic end-to-end check, the workstation run against the predeclared counts, a rerun, the CLI reproduction and targeted failure checks on scratch copies.
- The cluster run (the script is added; the run waits for the clone).

## Decisions

**D1. The constants as plain literals in `constants.py`.**

```python
ANALYSIS_PERMUTATIONS = 9999
ANALYSIS_SEED = 20261027
ANALYSIS_ALPHA = 0.05
ANALYSIS_REJECTION_RULE = "p <= alpha"       # MOTCO's covariate Type I check; exact for (1 + b) / (1 + B)
ANALYSIS_RANK_FLOOR = 2                      # MOTCO's validated default, passed explicitly and checked
ANALYSIS_LATENT_ADJUSTMENT: str | None = None   # the primary; "stage" is the predeclared sensitivity arm
ANALYSIS_STATISTICS = ("delta", "angle", "shape")
ANALYSIS_MISSING_COVARIATES = "error"
ANALYSIS_CATEGORICAL_COVARIATES = tuple(k for k, v in ANALYSIS_COVARIATES.items() if v["coding"] == "categorical")
ANALYSIS_INPUT_FILES = ("p180.csv", "nmr.csv", EXPORT_METADATA, EXPORT_COVARIATES, EXPORT_MANIFEST)
READING_RULES: tuple[str, ...] = (...)       # the nine statements of the proposal, verbatim
ANALYSIS_EXPECTED_COUNTS: dict = {...}       # the proposal's predeclared counts
```

`ANALYSIS_CATEGORICAL_COVARIATES` is derived from `ANALYSIS_COVARIATES` rather than typed, so the coding decided by `adni-cohort` is the only place it lives; the expected design columns are typed out (`age`, `education`, `apoe4[1]`, `apoe4[2]`, `phase[ADNI2GO]`, `statin[1]`) because they are MOTCO's rendering of that coding and a renamed level should surface as a deviation. Alternative considered: `ANALYSIS_PERMUTATIONS = 999` as the template. Rejected by the user: the count sets the p-value resolution, not the size, and the cost is seconds.

**D2. Gates before any read, in this order.**
`check_motco_version()` (installed `motco.__version__` against `ANALYSIS_MOTCO_MIN_VERSION`, `packaging.version` which the lock holds, with the tuple fallback of the template) and `check_motco_rank_floor()` (`TrajectoryAnalysisParams().min_components` against `ANALYSIS_RANK_FLOOR`; MOTCO normalizes a floor of 1 to `None`, so `None` reads as 1). Both raise `RuntimeError` naming both values. Then the export directory's existence (naming `export`), the five files, the hashes against the export manifest's `outputs`, the `rid` alignment, the column sets (`metadata.csv` exactly `rid`, `sex`, `stage`; `covariates.csv` `rid` plus the `ANALYSIS_COVARIATES` keys; blocks `rid` plus the manifest's `block_columns`), the values (`sex` in `GROUP_VALUES`, `stage` in `STAGE_LABELS`, each categorical covariate within its levels, no missing cell). A missing covariate cell stops here with the column and a count, before MOTCO would name a sample id in its own error. Only then is the output directory staged.

**D3. The dataset, built from the export manifest's codings.**
`OmicsBlock(name, frame)` per block in `EXPORT_BLOCKS` order with the `rid` column as the index; the metadata frame is `metadata.csv ⋈ covariates.csv` on `rid` (inner join, then an equality check on the `rid` sets), columns `rid`, `sex`, `stage`, then the covariates. `apoe4` and `statin` stay integers and are declared through `categorical_covariates`, so MOTCO compares their levels as strings `0`, `1`, `2`; `phase` is a string. `stage_order = STAGE_LABELS`, `group_order = GROUP_VALUES`, `missing_covariates = ANALYSIS_MISSING_COVARIATES`. `TrajectoryAnalysisParams(permutations=ANALYSIS_PERMUTATIONS, seed=ANALYSIS_SEED, n_jobs=n_jobs, min_components=ANALYSIS_RANK_FLOOR, covariate_latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT)` and nothing else: the CV settings and the estimator stay MOTCO's defaults and are read back from the record into the manifest, not restated from constants. Alternative: a MOTCO CLI subprocess. Rejected as in the template: it needs the merged CSV anyway, and the API lets the step hash what it passed.

**D4. `analysis_metadata.csv` written first, then parsed back.**
The merged frame is written to the staging directory and read back with pandas' default parsing, as `motco analyze --metadata` reads it, and the parsed frame is what `TrajectoryDataset` receives. So the `cli_equivalent` (`motco analyze --block p180=<path> --block nmr=<path> --metadata <analysis_metadata.csv> --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir <dir>`) reproduces the record, which task 4.4 checks. Covariate flags are emitted in `ANALYSIS_COVARIATES` order, `--covariate` for numeric and `--categorical-covariate` for categorical, since MOTCO's CLI preserves declaration order across both flags.

**D5. Manifest layout as in `export`.**
- Common keys: `step` (`analyze`), `created_at`, `versions` (`_software_versions` with `motco` and `scikit-learn` added to its list for this step), `git_revision`.
- `inputs`: per file the sha256 observed and, for the CSVs, the hash the export manifest records (`recorded`, `match` true); the export manifest's own hash; `export_git_revision` copied from it.
- `settings`: every constant of D1 by name with its value; `n_jobs`; `blocks` (order, transforms `identity`, feature counts); `sample_column`, `group_column` with `GROUP_VALUES`, `stage_column` with `STAGE_LABELS`; `covariates` (name, kind, levels, reference level, design columns, from the record); `motco_defaults_used` (estimator, CV settings, `random_state`, `max_components`, from the record's `params`); `latent_adjustment` null with `predeclared_sensitivity: {"conditioning": "stage", "change": "adni-latent-sensitivity"}`; `cli_equivalent`.
- `counts`: `participants`, `sex_stage` (from `design.cell_sizes`), `features` per block and joint, `design_columns` (names), `covariate_levels` (observed counts per level, computed from the metadata frame), `dropped`, `selected_rank`, `cv_mean_auroc`, `cv_repeats_completed`, `eigengap` (`config_spectrum.pooled.relative_eigengap`), `statistics`, `p_values`, `rejected` (per statistic under `ANALYSIS_REJECTION_RULE`), `runtime_seconds`.
- `expected` (`ANALYSIS_EXPECTED_COUNTS`), `deviations` (`_count_deviations` over the shared keys), `outputs` (bytes, sha256, `participant_level`), `findings`.
No `rid` value appears in any key or value: `dropped_sample_ids` is not copied (its length is), and a `grep` at apply checks the five aggregate files.

**D6. Findings, never stops, for what changes the reading.**
`n_jobs != 1` (the run is not reported); `selected_lv == ANALYSIS_RANK_FLOOR` (the floor is binding; the `angle` row of the summary says so); `cv_repeats_completed < n_repeats`; a non-finite statistic or p-value; every deviation from the predeclared counts. The template's rank-1 findings do not apply under the floor and are not carried.

**D7. `summary.md` rendered from the record.**
Header (MOTCO version, n, groups, stages, estimator, permutations, seed, α and the rule, `n_jobs`), the statistics table (observed, p, rejected, null mean, sd, q95; the `angle` row: degrees, selected rank, floor, eigengap, a floor-binding note when it applies), the cell-size table, the latent block (rank and selection mode, `cv_mean_auroc`, repeats completed, CV settings, blocks with feature counts and transforms), the covariate block (entered with kinds, design columns, reference levels, missing policy, dropped count, the reference-row table), the export context (block shares and the phase offset per block copied from the export manifest's `counts`), then `READING_RULES` as a numbered list. Numbers are formatted with six significant digits, as the template's renderer does, so `report --check` can match them against the record under the same formatting.

**D8. `scripts/analyze.sbatch`.**
As `clean.sbatch`: partition `512x1024`, `--cpus-per-task=1`, `--mem=4G`, `--time=01:00:00`, logs under `results/motco_analysis/logs/` (ignored), thread variables pinned to 1, `.venv/bin/adni-sexdiff analyze "$@"` from the locked environment. It passes no `--n-jobs`, so the cluster run is a reported run. The reported run of this change is the workstation's; the cluster rerun, when the clone exists, is compared through the pulled manifest (statistics, p-values, rank; floating-point results are not byte-reproducible across machines, so a difference there is recorded, not a gate).

**D9. Committed outputs.**
`result.json`, `pls_loadings.csv` (298 × rank loadings, aggregate), `stage_means.csv` (2 × 3 LS-means in latent coordinates, aggregate), `analysis_manifest.json` and `summary.md`, regenerated on the clean tree so the manifest records the implementing commit, as the earlier steps did. `latent_scores.csv` and `analysis_metadata.csv` never leave the workstation.

## Risks / Trade-offs

- **The latent basis is the p180 run axis** (export: PC1 correlation 0.73 with phase) and the CV picks a rank that spends a component on it → the covariates adjust the stage means within that basis and the RRPP stays valid under the covariate Type I check; what is measured is reported through the eigengap and `cv_mean_auroc`, `axis-diagnostics` correlates every component with phase, and the predeclared `stage` arm fits the basis on phase-residualized features. Nothing here corrects the primary.
- **Six design columns at n = 1501** → far from the near-singular regime MOTCO warns about at n = 80; the record's `design_columns` and the manifest's level counts (the smallest level `apoe4 = 2`, 149) state the degrees of freedom. The reading rules carry that the check covered three columns at n = 80.
- **A rare categorical level drops out of a CV training set** → the smallest level has 149 participants against outer training sets of about 1125; the manifest's `covariate_levels` makes any future shift visible, and MOTCO reports a dropped repeat in `cv_repeats_completed`, which is a finding.
- **9999 permutations depart from MOTCO's 999 grade** → size is exact at any count; the manifest records the count and the report states it.
- **`n_jobs` changes the draws** → the reported run is `n_jobs = 1` by default; another value is a finding and the summary's header shows it.
- **Collinear NMR concentrations and the p180 LOD clusters** → PLS tolerates both; the export manifest's numerical rank and shape counts are copied into the summary's export context.
- **A moved MOTCO default (floor, estimator, CV)** → the floor is gated; the others are read back from the record into the manifest and compared with the values the proposal states (`motco_defaults_used`), a difference being a finding.

## Migration Plan

1. Land the constants, `check_motco_version`, `check_motco_rank_floor`, `run_analysis` with its loader, renderer and `cli_equivalent`, the sbatch script, the docstrings and the docs. No existing default changes; `export` and earlier steps are untouched.
2. Verify on a synthetic dataset of the ADNI shape (made in the scratchpad, never from the data root) that the step runs end to end, that the gates and stops fire, and that the summary and manifest hold every key.
3. On the workstation, run `uv run adni-sexdiff analyze`. Compare the manifest's counts with `ANALYSIS_EXPECTED_COUNTS`, rerun with `--force` and compare the CSV hashes and the record, reproduce with the `cli_equivalent` into a scratch directory, and run once with `--n-jobs 4` into a scratch `--out-dir` to confirm the finding fires.
4. Commit the five aggregate files only, naming each and why it is aggregate, from a run made on the clean tree at the implementing commit.
5. Cluster: when the deploy key and the data copy exist, `sbatch scripts/analyze.sbatch` after `export` on the login node; pull with `scripts/sync_results.sh` and compare the manifests.
6. Rollback: the outputs are additive under `results/motco_analysis/`; reverting the constants returns `analyze` to a stub.
