# Design

## Context

See `proposal.md` for the motivation and the constants. The state that shapes the approach:

- **The stub and the CLI.** `run_axis_diagnostics(*, input_dir, analysis_dir, cohort_dir, out_dir, force)` is a stub in `src/adni_sexdiff/data.py` whose docstring states the output contract; `cli.py` exposes `axis-diagnostics --input-dir --analysis-dir --cohort-dir --out-dir --force`. `constants.py` defines `DIAGNOSTICS_DIR` and the five output names (`DIAGNOSTICS_AXIS_CORRELATIONS`, `DIAGNOSTICS_BLOCK_PCS`, `DIAGNOSTICS_GEOMETRY_SHARES`, `DIAGNOSTICS_SUMMARY`, `DIAGNOSTICS_MANIFEST`) and names `DIAGNOSTIC_VARIABLES` and `DIAGNOSTIC_CORRELATION_THRESHOLD` as the last undecided constants in its docstring.
- **Helpers from the earlier steps.** `_load_analysis_inputs(input_dir)` is the `analyze` loader: the five export files against the export manifest's hashes, the column sets, the `rid` alignment of the four tables, the value and missing checks; it returns the blocks indexed by `rid`, the merged `rid`, `sex`, `stage`, covariates frame in export order and the export manifest, and its messages say `analyze`. `_check_cohort_outputs(cohort_dir, clean_inputs)` is the `export` check of `cohort.csv` against `cohort_manifest.json` (with an empty `clean_inputs` it makes no clean-chain check). Also `_sha256_file`, `_git_revision`, `_software_versions`, `_write_manifest` (sorted keys), `_finalize_output_dir`, `_count_deviations`, `_project` and `_fmt` (six significant digits).
- **What the analysis wrote** (committed at `af4d6e4`): `result.json` with `latent.selected_lv` 8, `latent.component_selection` `cv`, `design.group_levels`, `design.stage_levels`, `design.cell_sizes`, `covariates.design_columns` (the six names), `covariates.reference_levels`, `covariates.reference_row` (the pooled mean of each design column) and `measurement.n_jobs`; `latent_scores.csv` (`rid`, `pls_0` … `pls_7`, export order); `stage_means.csv` (`group`, `stage`, `pls_k`); `pls_loadings.csv` (`block`, `feature`, `pls_k`: MOTCO's `x_rotations_` on the z-scored joint features, so the entries are comparable across blocks); `analysis_manifest.json` with `inputs.files.<name>.sha256` for the five export files, `inputs.export_manifest.sha256`, `settings.latent_adjustment`, `settings.n_jobs`, `counts.selected_rank`.
- **What the export and the cohort wrote.** The export manifest records `outputs.<csv>.sha256`, `inputs.cohort.manifest.sha256` (the cohort manifest's hash) and `inputs.cohort.outputs.cohort.csv.sha256`, `settings.covariates` (the codings with `levels`), `settings.block_columns`, `counts.phase_offset.<block>.abs_corr_pc1_phase` (Pearson correlation of the first left-singular vector of the standardized block with the ADNI1 indicator: 0.734 p180, 0.135 NMR) and `counts.spectrum.<block>.pc1_share` (0.418, 0.438). `cohort.csv` holds `rid`, `sex`, `stage`, `dx_bl`, `protocol`, the five covariates, `visit`, `p180`, `nmr`.
- **The template.** `../sead_sexdiff/src/sead_sexdiff/data.py` holds `spearman`, `partial_spearman`, `block_principal_components`, `geometry_shares`, `_correlation_rows`, `_check_analysis_inputs` and `render_axis_diagnostics` (archived change `2026-10-19-mtg-astrocyte-technical-axis-diagnostic`, spec `latent-axis-diagnostic`). The repositories share no package, so the functions are carried over by copy and their definitions are written into the manifest.
- **A synthetic export already exists in form.** The `adni-analyze` change timed MOTCO on a synthetic dataset of the ADNI shape built from random numbers in a session scratchpad (`time_synth.py`); the verification here needs the same kind of export plus a cohort directory and a real `run_analysis` on it, so that the hash chain is genuine.
- **Ignore rules.** `results/motco_diagnostics/` matches no participant-level pattern of `.gitignore`, `scripts/sync_results.sh` or `PARTICIPANT_LEVEL_PATTERNS`; nothing to add.

## Goals / Non-Goals

**Goals:**
- One command from the kept outputs to four tables, a rendering and a manifest: deterministic, every input hashed and chained, readable without any participant-level file.
- Every variable, threshold and definition a constant recorded in the manifest; the only runtime knobs the directories and `--force`.
- The same command usable, unchanged, on the latent-adjusted arm of the next change.

**Non-Goals:**
- Any inference on a correlation, any stratified or per-feature table, any rule that reads a flag (see the proposal's out-of-scope list).
- A test framework; verification is a synthetic trio of directories, hand checks of each statistic, the workstation run against the predeclared counts, a rerun and targeted failure checks on scratch copies.

## Decisions

**D1. The constants as plain literals in `constants.py`.**

```python
# scientific, decided by adni-axis-diagnostics
DIAGNOSTIC_VARIABLES: dict[str, dict] = {
    "age":       {"file": EXPORT_COVARIATES, "column": "age", "derivation": "as exported (years)"},
    "education": {"file": EXPORT_COVARIATES, "column": "education", "derivation": "as exported (years)"},
    "apoe4":     {"file": EXPORT_COVARIATES, "column": "apoe4", "levels": (0, 1, 2),
                  "derivation": "APOE e4 allele count, read as ordinal"},
    "phase":     {"file": EXPORT_COVARIATES, "column": "phase", "levels": ("ADNI1", "ADNI2GO"),
                  "derivation": "1 for ADNI2GO, 0 for ADNI1 (the p180 run)"},
    "statin":    {"file": EXPORT_COVARIATES, "column": "statin", "levels": (0, 1),
                  "derivation": "1 for a statin user at sc, 0 otherwise"},
    "stage":     {"file": EXPORT_METADATA, "column": STAGE_COLUMN, "levels": STAGE_LABELS,
                  "derivation": "ordinal CN 0, MCI 1, AD 2"},
    "male":      {"file": EXPORT_METADATA, "column": GROUP_COLUMN, "levels": GROUP_VALUES,
                  "derivation": "1 for Male, 0 for Female"},
    "dx_bl":     {"file": COHORT_TABLE, "column": "dx_bl", "levels": ("CN", "SMC", "EMCI", "LMCI", "AD"),
                  "derivation": "ordinal CN 0, SMC 1, EMCI 2, LMCI 3, AD 4 (ADNI's enrollment gradient)"},
}
DIAGNOSTIC_CORRELATION_THRESHOLD = 0.3      # a reporting flag on |rho|, raw and partial; never an adoption rule
# conventions
DIAGNOSTIC_N_BLOCK_PCS = 3
DIAGNOSTIC_CONDITIONING_COLUMNS = ANALYSIS_EXPECTED_COUNTS["design_columns"]   # the record's six design columns
DIAGNOSTICS_COMPONENTS = "components.csv"
DIAGNOSTICS_ANALYSIS_FILES = (ANALYSIS_RESULT, ANALYSIS_LATENT_SCORES, ANALYSIS_STAGE_MEANS, ANALYSIS_PLS_LOADINGS, ANALYSIS_MANIFEST)
DIAGNOSTICS_GEOMETRY_QUANTITIES = {"net_displacement": "...", "sex_difference_by_stage": "...", "sex_difference_centred": "..."}
# predeclared
DIAGNOSTICS_EXPECTED_COUNTS = {
    "participants": 1501, "sex_stage": {...the cohort cells...},
    "variables": tuple(DIAGNOSTIC_VARIABLES), "conditioning_columns": DIAGNOSTIC_CONDITIONING_COLUMNS,
    "blocks": {"p180": {"features": 133, "pcs": 3}, "nmr": {"features": 165, "pcs": 3}},
    "primary": {"selected_rank": 8, "component_selection": "cv", "latent_adjustment": None, "n_jobs": 1},
    "rows": {"axis_correlations": 64, "block_pcs": 48, "geometry_shares": 32, "components": 8},
}
```

A variable's value is the source column as is when the entry has no `levels`, and the index of the value in `levels` when it has (so `apoe4` and `statin` keep their integers, `phase`, `stage`, `male` and `dx_bl` become 0-based ordinals; a value outside `levels` stops the step naming the column and a count). The variables are declared in this order and the tables keep it (covariates, design, enrollment), not alphabetical as the template. *Alternative considered:* `protocol` as a three-level ordinal. Rejected in the proposal: GO against 2 is no assay run. *Alternative:* a threshold of 0.5 (the template's feature-level cut). Rejected: the flag is a reading aid on a small table, and 0.3 is what the template used for axes; at either value nothing is adopted.

**D2. Checks before anything is written, in this order.** (1) The output directory: an existing `DIAGNOSTICS_DIR` without `--force` stops first (`_finalize_output_dir` does this, but it is entered only after the reads, so the existence check is made up front). (2) The export, through `_load_analysis_inputs(input_dir, step="axis-diagnostics")` (a `step` parameter added so its messages name this step; `analyze` keeps its default). (3) The analysis directory: existence (naming `analyze`), the five `DIAGNOSTICS_ANALYSIS_FILES`, then the chain: every `inputs.files.<name>.sha256` of the analysis manifest against the sha256 of the export file now (naming the file, both hashes and `analyze`), and the analysis manifest's `inputs.export_manifest.sha256` against the export manifest's hash now. (4) The components: `latent.selected_lv` of the record against the number of `pls_` columns in `latent_scores.csv`, `stage_means.csv` and `pls_loadings.csv` (naming the file and both counts); `stage_means.csv` holding every group × stage row of `design`; `pls_loadings.csv` holding every `block_columns` feature of every block, each once. (5) The scores: the `rid` set of `latent_scores.csv` equal to the export's, re-indexed to export order. (6) The cohort: `_check_cohort_outputs(cohort_dir, {})` (the table against its manifest), the cohort manifest's sha256 against the export manifest's `inputs.cohort.manifest.sha256` (naming `cohort_manifest.json` and `export`), and the rows with both platform flags equal to the exported `rid`s in order. (7) The variable table and the conditioning design (D3), whose value checks stop naming a column and a count. Only then is the staging directory created. *Alternative:* a generic `_check_analysis_inputs` as the template. Kept as a function of the same name, but it also checks the export-manifest hash and the component counts, which the template left to the per-analysis loop.

**D3. The variable table and the conditioning design.** The table is participants × 8, built from the loader's merged frame (`rid`, `sex`, `stage`, the covariates) joined on `rid` with `dx_bl` from `cohort.csv`, under the rule of D1. The conditioning matrix `z` is built from the same frame with the codings of `ANALYSIS_COVARIATES` as the export manifest records them: numeric columns as is, a categorical covariate as drop-first indicators in level order (the first level is the reference), named `<name>[<level>]`. Two checks make it the model's design rather than a reimplementation of it: the column names must equal `DIAGNOSTIC_CONDITIONING_COLUMNS` and the record's `covariates.design_columns`, and each column's mean must equal the record's `covariates.reference_row` entry within 1e-9 (MOTCO's reference row is the pooled mean of the design columns). Either difference stops the step naming the column. *Alternative:* conditioning on the five raw covariates as numbers (apoe4 as 0 / 1 / 2). Rejected: the model adjusts on the indicator coding, and the partial should be what that adjustment leaves.

**D4. Statistics carried from the template, each defined once and written into the manifest.** `spearman(x, y)`: scipy's `spearmanr` over the pairwise-complete rows; NaN with fewer than three rows or a constant. `partial_spearman(x, y, z)`: the Spearman correlation of the OLS residuals of `x` and `y` on an intercept and `z`; NaN when a residual is numerically zero (a variable in the span of `z`, as each covariate is). `block_principal_components(block, n_components=3)`: SVD of the block z-scored with the population SD, scores `U S`, each component's sign fixed so that its largest-magnitude loading is positive, variance share `s² / Σ s²`. `geometry_shares(stage_means, groups, stages)`: for each sex the net displacement (last stage mean minus first), the per-stage sex differences (first group minus second) and the stage-centred sex differences; per component the squared length along it over the squared length over all components. New here, `block_loading_shares(loadings, block_columns)`: per component the sum of squared `pls_loadings.csv` entries over each block's rows over the sum over all rows. The Spearman of each block's PC1 with `phase` is recorded beside the export's Pearson `abs_corr_pc1_phase` as a cross-check, with no agreement threshold (two statistics of the same pair). *Alternative:* Pearson correlations. Rejected as in the template: `age` and `education` are not symmetric, the ordinals are not interval, and the two repositories should agree in definition.

**D5. Tables, columns, order and formatting.**
- `axis_correlations.csv`: `component`, `component_sd`, `variable`, `source`, `n`, `spearman`, `n_partial`, `partial_spearman`, `flag_raw`, `flag_partial`; rows by component index, then `DIAGNOSTIC_VARIABLES` order.
- `block_pcs.csv`: `block`, `component` (`pc1` … `pc3`), `variance_share`, `variable`, `source`, `n`, `spearman`, `n_partial`, `partial_spearman`, `flag_raw`, `flag_partial`; rows by `EXPORT_BLOCKS` order, component, variable.
- `geometry_shares.csv`: `quantity` (`net_displacement_Female`, `net_displacement_Male`, `sex_difference_by_stage`, `sex_difference_centred`), `component`, `value` (the signed component of a single vector; empty for the summed quantities), `along`, `total`, `share`.
- `components.csv`: `component`, `sd`, `loading_share_p180`, `loading_share_nmr` (one column per block in `EXPORT_BLOCKS` order), `n_flagged_raw`, `n_flagged_partial`, `top_variable`, `top_spearman`.
Written with pandas `to_csv(index=False)` as the earlier steps (deterministic for the same inputs; NaN as an empty cell; flags as `True` / `False`). *Alternative:* a fixed float format as the template's `_csv_float`. Not needed: the earlier steps of this repository write pandas' default round-trip representation and `report --check` will parse numbers, not compare strings.

**D6. Manifest layout as in `analyze`.** Top-level `step` (`axis-diagnostics`), `created_at`, `versions`, `git_revision`, `inputs`, `settings`, `counts`, `expected`, `deviations`, `outputs`, `findings`.
- `inputs`: `export` (dir, the five files with sha256 and, for the CSVs, the recorded hash and `equals_export_manifest`), `analysis` (dir, the five files with sha256, `chain` per export file true, `export_manifest_equals` true, `latent_adjustment`, `n_jobs`, `selected_rank`, `component_selection`, `is_primary`, the analysis manifest's git revision copied), `cohort` (dir, `cohort.csv` sha256 with `equals_cohort_manifest`, `cohort_manifest.json` sha256 with `equals_export_manifest`).
- `settings`: `DIAGNOSTIC_VARIABLES` (resolved: name, file, column, derivation, levels), `DIAGNOSTIC_CORRELATION_THRESHOLD` with `threshold_note`, `DIAGNOSTIC_N_BLOCK_PCS`, `conditioning_columns`, `definitions` (one sentence per statistic, from D4), `downstream` ("read by no export or analyze run; arms and variants are predeclared in a change proposal, never derived from a diagnostic value").
- `counts`: `participants`, `sex_stage`, `components`, `variables`, `conditioning_columns`, `blocks` (per block `features`, `pcs`, `variance_shares`, `pc1_phase` with `spearman` and `export_abs_corr_pearson`), `rows` per table, `flagged` (axis raw / partial, block PCs raw / partial), `per_component` (per `pls_k`: `sd`, `loading_share` per block, `n_flagged_raw`, `n_flagged_partial`, `top_variable`, `top_spearman`, `flagged_variables` as names).
- `expected`: `DIAGNOSTICS_EXPECTED_COUNTS`, or its rank-independent keys (`participants`, `sex_stage`, `variables`, `conditioning_columns`, `blocks`) when the analysis is not the primary (D8), with `primary_expectations_checked`; `deviations` from `_count_deviations` over `_project(observed, expected)`.
- `outputs`: the six files with sha256, bytes and `participant_level` false. No `rid` value appears in any key or value.

**D7. `diagnostics.md` rendered from the tables.** A header paragraph stating what the tables are and are not (descriptive measurement-space diagnostics of the primary analysis; Spearman and partial Spearman given the six design columns; rows with |ρ| ≥ 0.3 flagged and listed first; the flag a reporting threshold, not an adoption rule; no p-value, no inferential claim; an axis correlated with a variable a finding about the measurement space, not a reinterpretation of the statistics; the primary stays primary). Then: "Flagged correlations" (latent components, then block PCs, each by |ρ| descending); "Components" (`components.csv` as a table); "Correlations of the latent components" (variable rows × component columns, ρ and partial with `*` for a flag, the source column); "Block principal components" (one table per block, the variance shares and the export's recorded PC1 phase correlation beside the diagnostic's in the heading); "Geometry shares"; "Analysis read" (directory, rank, selection, latent adjustment, `n_jobs`, primary or not); "Findings"; "Reading rules" (`READING_RULES` numbered, verbatim, as `summary.md` prints them). ρ and shares with `.3f`, SDs with `.4g`, as the template, so that `report --check` matches the rendered precision.

**D8. Runs on an arm.** `is_primary` is true when the resolved `analysis_dir` equals the resolved default (`MOTCO_ANALYSIS_DIR`) and the analysis manifest's `settings.latent_adjustment` is null. When false, the `primary` and `rows` expectations are skipped (`primary_expectations_checked` false), a finding names the directory and the adjustment, and the header of `diagnostics.md` says which analysis was read. The default `out_dir` is still `DIAGNOSTICS_DIR`; the next change passes its own `--out-dir`. *Alternative:* a `--label` flag. Rejected: the manifest records the directory and the adjustment, which is the label.

**D9. Verification on a synthetic trio.** A scratch script (in the session scratchpad, random numbers, n = 300, two blocks of 30 and 40 features, the five covariates with the real codings, `dx_bl` drawn within each stage under `STAGE_RULE`, both platform flags true for every row) writes `cohort/` (`cohort.csv` with the thirteen `COHORT_COLUMNS`, `cohort_manifest.json` with the table's hash) and `motco_input/` (the four tables, `manifest.json` with `outputs` hashes, `settings.covariates` = `ANALYSIS_COVARIATES`, `settings.block_columns`, `inputs.cohort.manifest.sha256`, `counts.phase_offset` and `counts.spectrum` computed the export's way), then runs `run_analysis(input_dir=..., out_dir=...)` on it (at the constants' 9999 permutations, seconds at this size), so that the analysis manifest's chain hashes are genuine. The hand checks: `spearman` against scipy on small arrays; the partial of a variable with itself given `z` equal to 1 and of a covariate n/a; block PC scores and shares against a direct SVD with shares summing to 1; geometry shares summing to 1 per quantity on a hand-made rank-3 `stage_means`; loading shares summing to 1; the conditioning design's column means equal to the record's reference row; a byte-identical rerun; each stop of D2 on an altered scratch copy, with no `.tmp` left and the inputs' tree hash unchanged. *Alternative:* verification on the real data only. Rejected: the stops have to be exercised on copies, and the hand checks need known answers.

## Risks / Trade-offs

- [n = 1501 makes nearly every correlation distinguishable from zero] → the threshold reads magnitude; no p-value is written; the rendering and the manifest say so.
- [`dx_bl` and `phase` are confounded: SMC and EMCI exist only in ADNI-GO/2] → raw and partial (given the design, phase included) are both written and read together; neither is chosen from.
- [The diagnostic reads sex and stage and could steer a later choice] → no `export` or `analyze` run reads it (spec), the latent arm is already predeclared, and the documentation states that variants are predeclared in a proposal.
- [The arm's CV-selected rank differs from 8] → the `primary` and `rows` expectations are skipped on an arm and the manifest says so (D8).
- [Spearman here against the export's Pearson on PC1] → both recorded as a cross-check with no agreement threshold; a large difference is visible, not a gate.
- [`pls_loadings.csv` holds rotation weights, not loadings] → the manifest's definition names `x_rotations_`; the shares are of squared rotation weights on z-scored features, comparable across the unweighted blocks.
- [Functions copied from the template drift] → each definition is written into the manifest; a difference between repositories is a visible difference of definition.
- [Cross-machine floating point] → byte identity is checked between two runs on the same machine only; the cluster run, when it exists, is compared through the manifests.
- [`_load_analysis_inputs` gains a parameter] → default `analyze`; the analyze step's messages and behaviour are unchanged (checked by its `--help` and a synthetic run in the tasks).

## Migration Plan

1. Land the constants, the statistics, the chain checks, `run_axis_diagnostics`, the renderer, the docstrings and the docs. No existing default changes; `analyze` and earlier steps are untouched (the loader's new parameter defaults to its old behaviour).
2. Verify on the synthetic trio (D9): the run end to end, each stop, the hand checks, the rerun.
3. On the workstation, run `uv run adni-sexdiff axis-diagnostics`. Compare the manifest's counts with `DIAGNOSTICS_EXPECTED_COUNTS`, rerun into a scratch `--out-dir` and compare hashes, run once with `--analysis-dir` on a scratch copy of the primary to confirm the arm path, and check the controlled-access contract on the real output.
4. Commit the six aggregate files only, naming each and why it is aggregate, from a run made on the clean tree at the implementing commit.
5. Rollback: the outputs are additive under `results/motco_diagnostics/`; reverting the constants returns `axis-diagnostics` to a stub.
