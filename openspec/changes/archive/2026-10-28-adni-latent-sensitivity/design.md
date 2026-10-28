# Design

## Context

See `proposal.md` for the motivation, the arm, the covariate roles and the reading rules, and the specs for the requirements. This is the state that shapes the approach:

- **`run_analysis`** (`data.py`) does everything in one function:
  - the MOTCO gates;
  - `_load_analysis_inputs(input_dir, step=...)`, which checks the five export files and builds the metadata frame;
  - the dataset (`TrajectoryDataset` with `ANALYSIS_COVARIATES` and `ANALYSIS_CATEGORICAL_COVARIATES`) and `TrajectoryAnalysisParams(... covariate_latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT)`;
  - the one call;
  - the counts against `ANALYSIS_EXPECTED_COUNTS` and the findings;
  - the manifest, whose `settings` carry `latent_adjustment: null` and `predeclared_sensitivity`;
  - `summary.md` from `render_analysis_summary`, and `_finalize_output_dir`.

  `_analysis_cli_equivalent` already emits `--latent-adjustment <c>` when the setting is set. `render_analysis_summary` hard-codes the header clause "latent adjustment: none (the primary; …)" and has no latent-adjustment section.
- **MOTCO 0.10.0** (pinned).
  - With `covariate_latent_adjustment="stage"`, it builds the residualization design `[1, stage[1], stage[2], <six covariate design columns>]`. The stage indicators are named by MOTCO's ordinal codes: `stage[1]` is MCI, `stage[2]` is AD.
  - It checks full rank on the full sample, then fits the coefficients in every CV training set and residualizes that set's own rows. Held-out rows use the training coefficients and their covariate columns only.
  - The CV folds are stratified on the conditioning cells, which under `stage` partition the rows like the stage labels. So the folds equal the unadjusted analysis's.
  - The final basis is fitted on the full-sample residualized features, and the pooled-standardized raw features are projected onto it. The trajectory model, LS-means and RRPP are those of the unadjusted path.
  - The record gains `latent_adjustment` (`conditioning`, `covariates`, `design_columns`, `n_samples`, `residual_df` = n − 1 − k − q, `cv_min_training_df`, `feature_scale`, `feature_r2` with q05 / q25 / q50 / q75 / q95 / mean) and `params.covariate_latent_adjustment`.
  - A training design that is not of full rank, for example a categorical level absent from a training set, raises an error naming the repeat and fold.
- **`axis-diagnostics`** already reads an arm through `--analysis-dir` / `--out-dir`. `_check_analysis_inputs` chains the analysis manifest's `inputs.files` to the export files now on disk. `is_primary` is false for a non-default directory or a recorded `settings.latent_adjustment`. `render_axis_diagnostics` already says "an arm (not the primary)" in its first paragraph, but still calls a flagged row a finding about "the primary analysis", prints only `READING_RULES`, and its error hints always name `analyze`.
- **The kept aggregate inputs.**
  - The export manifest records the cohort manifest's hash under `inputs.cohort.manifest`.
  - The cohort manifest records `descriptives` for the intersection set, per sex × stage cell: `n`, age and education mean and sd, and counts per level of `apoe4`, `phase` and `statin`.
  - The committed primary manifest (`af4d6e4`) records the sha256 of all seven primary outputs. The committed diagnostics manifest records those of its outputs: it was re-issued in `754c6ba` at the pinned thread count, where `block_pcs.csv` changed and the other four kept their `cf38ec8` hashes.
- **Pinned numerics** (`adni-portable-numerics`, merged in PR #6). Importing `adni_sexdiff` sets `NUMERIC_SETTINGS` before numpy loads, and every step's manifest carries a `numerics` block (`_numerics(prefix)`, taken after the work) with a finding when the run is not pinned.
  - On 2026-10-28, pinned runs reproduced every committed output on an AVX-512 machine, on 24 CPUs and on 1. A pinned run therefore writes the committed bytes on any data machine, and the committed hashes are the reference for every real-data gate below.
  - `run_analysis` already writes the block. The shared function (D2) inherits it, so the arm's manifest has it with no extra key.
  - The manifests written before PR #6 (the primary's among them) have no block.
- **Machines.** The user moves between machines (office, home, a laptop on other campuses). This design names none.
  - A **data machine** is any machine whose local participant-level inputs hash to the values the committed manifests record: the export CSVs and `cohort.csv` for the arm, plus the primary's `latent_scores.csv` and `analysis_metadata.csv` for the primary's diagnostics gate.
  - The arm itself reads only the primary's two git-tracked JSON files.
  - Any machine with a data root becomes a data machine by a pinned rebuild (D10). nixos-office became one on 2026-10-28.
  - Any machine can run the synthetic checks.
- **The template.** `../sead_sexdiff` change `mtg-astrocyte-latent-adjustment-sensitivity` ran two arms (an extended covariate set, then the same set latent-adjusted) per cohort, with a mediator check and a report. Here there is one arm on the primary's own covariates and one cohort; the mediator condition is met by predeclared roles with no statistic; and the report is step 6.

## Goals / Non-Goals

**Goals:**
- One command from the export and the primary to the arm's analysis directory and the comparison, with the provenance discipline of `analyze`.
- An arm directory that is a primary directory with exactly the latent-adjustment setting changed, readable by `axis-diagnostics` unchanged.
- The primary's outputs and the primary diagnostic's outputs byte-identical across the refactor.
- The arm's reading rules printed wherever an arm number is printed.

**Non-Goals:**
- Any adoption rule, revised primary or choice made from the arm.
- A generic arm registry for future sensitivities. Each later arm is its own proposal and may generalize the step then.
- A test framework. Verification is a synthetic end-to-end check, the exact real-data gates against the committed hashes, the data machine's run against the predeclared counts, a rerun, the CLI reproduction and targeted failure checks on scratch copies.
- Re-issuing the earlier steps' manifests so they carry a `numerics` block. Their outputs were reproduced pinned on 2026-10-28, which is all this change needs.

## Decisions

**D1. A separate `latent-sensitivity` step, not a flag on `analyze`.**
The `motco-trajectory-analysis` spec fixes "no latent adjustment" for `analyze` and forbids a second analysis in the step, and constraint 5 forbids a scientific setting as a flag. A separate step reads the primary as a reference and writes beside it, so the primary directory is never written.
- *Alternative: `analyze --arm latent_stage`.* Rejected: it puts the arm in the primary's contract and the primary's default output path one flag away from the arm.

**D2. One shared analysis function; the primary's bytes are the gate.**
`run_analysis`'s body moves to `_run_trajectory_analysis(*, input_dir, final, n_jobs, force, step, latent_adjustment, expected, manifest_extra=None)`. The summary needs no extra argument: the renderer keys on the record (D7).
- `run_analysis` calls it with `step="analyze"`, `latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT` and `expected=ANALYSIS_EXPECTED_COUNTS`.
- The primary manifest keeps every key it has today, `latent_adjustment: null` and `predeclared_sensitivity` included, in the same order.
- The arm passes `step="latent-sensitivity"`, `latent_adjustment=LATENT_SENSITIVITY_ARM["conditioning"]`, `expected=LATENT_SENSITIVITY_EXPECTED_COUNTS`, and a `manifest_extra` with:
  - `arm` (the constant, by name);
  - `reference` (the primary's directory, `result.json` and manifest sha256, rank, MOTCO version);
  - the arm findings of D9.

  The machine and the numeric state come from the `numerics` block the shared function already writes. There is no separate `host` key.

Verification has two gates:
- **Synthetic:** before the refactor, run the unmodified `analyze` on the synthetic export as the baseline. After it, the four CSVs and `summary.md` must be byte-identical and the JSON equal apart from `created_at`, `runtime_seconds` and `git_revision`. A synthetic dataset has no committed reference, so this gate compares the code before and after.
- **Real data, on any data machine, exact:**
  - A pinned `analyze --out-dir <scratch>` on the default inputs must write the four CSVs and `summary.md` with the sha256 the committed primary manifest records, and a `result.json` equal to the committed one apart from its runtime.
  - Pinned runs write the same bytes on every machine (`adni-portable-numerics`), so this gate holds wherever it runs, and no worktree of the old code is needed.
  - A difference stops the change, and the refactor is reverted.

*Alternative: copy the function for the arm.* Rejected: the comparison rests on nothing but the setting differing, and two copies would drift.

**D3. Constants.**
```python
LATENT_SENSITIVITY_DIR = "results/motco_latent_sensitivity"
LATENT_SENSITIVITY_SUBDIRS = {"analysis": "analysis", "comparison": "comparison", "diagnostics": "diagnostics"}
LATENT_SENSITIVITY_TABLE = "latent_sensitivity.csv"
LATENT_SENSITIVITY_SUMMARY = "latent_sensitivity.md"
LATENT_SENSITIVITY_MANIFEST = "latent_sensitivity_manifest.json"

LATENT_SENSITIVITY_ARM: dict = {
    "name": "latent_stage",
    "setting": "covariate_latent_adjustment",
    "conditioning": "stage",
    "covariates": tuple(ANALYSIS_COVARIATES),
    "change": "adni-latent-sensitivity",
    "other_settings": "the primary's (ANALYSIS_* constants and MOTCO's defaults)",
}
assert {k: LATENT_SENSITIVITY_ARM[k] for k in ("setting", "conditioning", "change")} == ANALYSIS_PREDECLARED_LATENT_SENSITIVITY
LATENT_SENSITIVITY_COVARIATE_ROLES: dict[str, dict[str, str]] = {   # role + justification, per proposal
    "age": {"role": "pre-disease", ...}, "education": {...}, "apoe4": {...},
    "phase": {"role": "design", ...}, "statin": {"role": "mediator candidate", ...},
}
assert tuple(LATENT_SENSITIVITY_COVARIATE_ROLES) == tuple(ANALYSIS_COVARIATES)
LATENT_SENSITIVITY_READING_RULES: tuple[str, ...] = (...)   # the proposal's nine statements, verbatim
LATENT_SENSITIVITY_EXPECTED_COUNTS = {
    **ANALYSIS_EXPECTED_COUNTS,
    "latent_adjustment": {
        "conditioning": "stage",
        "covariates": tuple(ANALYSIS_COVARIATES),
        "design_columns": ("stage[1]", "stage[2]", *ANALYSIS_EXPECTED_COUNTS["design_columns"]),
        "n_samples": 1501,
        "residual_df": 1501 - 1 - 2 - 6,
        "feature_scale": "pooled_standardized",
    },
}
```
- The assertions tie the arm to the decision of `adni-analyze` and the roles to the covariate set, so neither can drift.
- `residual_df` is written as its formula so the source shows where 1492 comes from.
- The arm is not added to `PARTICIPANT_LEVEL_PATTERNS`: its two participant-level files are matched by the existing `results/**/` patterns.

**D4. Checks, in this order, before anything is written.**
1. The gates: `check_motco_version`, then `check_motco_rank_floor`.
2. Either output subdirectory existing without `force`.
3. `_load_analysis_inputs(input_dir, step="latent-sensitivity")`, the export.
4. `_check_primary_reference(analysis_dir, loaded)`, the primary as a reference:
   - the primary directory and its `result.json` / `analysis_manifest.json` exist (else name `analyze`);
   - every `inputs.files` hash and `inputs.export_manifest` equals the file now on disk;
   - `settings.latent_adjustment` is null and the record has no `latent_adjustment` block;
   - `versions.motco` equals the installed version;
   - `settings.ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS` equal the constants.

   This reuses the chain logic of `_check_analysis_inputs` but reads only the two JSON files: the arm needs no primary CSV. It does not require a `numerics` block in the primary's manifest. That manifest predates PR #6, and the pinned rebuild of 2026-10-28 reproduced its outputs, which the D2 gate checks again.
5. `_check_cohort_manifest(cohort_dir, export_manifest)`, the cohort manifest's sha256 against `inputs.cohort.manifest.sha256`. It reads no `cohort.csv`.

A failure raises naming the file or setting, both values and the command to rerun.

**D5. Layout and atomicity.**
```
results/motco_latent_sensitivity/
  analysis/     # written by latent-sensitivity: the seven files analyze writes (arm)
  comparison/   # written by latent-sensitivity: latent_sensitivity.{csv,md}, latent_sensitivity_manifest.json
  diagnostics/  # written by axis-diagnostics --analysis-dir …/analysis --out-dir …/diagnostics
```
- `analysis/` and `comparison/` are staged by nested `_finalize_output_dir` blocks (`analysis.tmp/`, `comparison.tmp/`). The comparison is computed from the in-memory arm record and the primary record, and hashes the staged arm files.
- A failure before the blocks exit leaves both final directories as they were. `--force` replaces both.
- The step never touches `diagnostics/`. When it replaces an existing `analysis/` while `diagnostics/` exists, it records a finding that the arm diagnostic is from the replaced arm and must be rerun. It checks only that the directory exists and reads nothing in it (the diagnostic feeds no arm).
- *Alternative: stage the whole root.* Rejected: `--force` would silently delete the arm's diagnostics.

**D6. The comparison.**
- **`latent_sensitivity.csv`:** two rows, in the column order:
  - `analysis` (`primary`, `latent_stage`), `directory` and `latent_adjustment` (empty, `stage`);
  - `selected_rank`, `component_selection`, `cv_mean_auroc`, `cv_repeats_completed` and `eigengap`;
  - per statistic `<s>_observed`, `<s>_p`, `<s>_rejected`, `<s>_null_mean`, `<s>_null_sd` and `<s>_null_q95`;
  - `residual_df`, `cv_min_training_df`, `feature_r2_{q05,q25,q50,q75,q95,mean}` (empty for the primary).

  Floats go through pandas' default `to_csv` (repr round-trip). No runtime column, so a rerun is byte-identical.
- **Status per statistic:** `same` when both rejections are equal, otherwise `differs (basis dependence)`. The primary's status is the result either way.
- **`latent_sensitivity.md`** (`render_latent_sensitivity`), in this order:
  1. the header (reference and arm directories with their `result.json` sha256, the arm by constant name, `n_jobs`);
  2. the statistics table (primary row, arm row, status), with both ranks, floors, eigengaps and null summaries beside `angle`;
  3. the latent-space table (rank, selection, CV AUROC, repeats, eigengap with its permutation null);
  4. the arm's latent-adjustment block (design columns with `stage[1]` = MCI and `stage[2]` = AD, residual df, smallest CV training df, feature scale, the `feature_r2` quantiles);
  5. "Covariates residualized by the arm": each role and justification from `LATENT_SENSITIVITY_COVARIATE_ROLES`, then a sex × stage table of the cohort manifest's descriptives (n; age and education mean (sd); `apoe4` 0 / 1 / 2, `phase` ADNI1 / ADNI2GO and `statin` 0 / 1 counts), copied, not recomputed;
  6. MOTCO's two latent-adjustment decisions with their report paths;
  7. the findings;
  8. `READING_RULES`, then `LATENT_SENSITIVITY_READING_RULES`, both verbatim.

  Numbers carry six significant digits, as in `summary.md`.
- **`latent_sensitivity_manifest.json`:**
  - the common keys, `numerics` among them (`_numerics("[latent-sensitivity]")`, taken after the comparison is built);
  - `inputs`: the eight files with sha256, plus the chain results (`primary_records_export`, `cohort_manifest_equals_export_record`);
  - `settings`: `LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`, `ANALYSIS_ALPHA` with the rule, and `n_jobs`;
  - `reference` and `arm`: directory, `result.json` and manifest sha256, rank;
  - `counts`: statuses, ranks, CV AUROC, the latent-adjustment block, the cohort cells against the record's cells;
  - the arm's `expected` and `deviations`, copied; `outputs`; `findings`.
- *Alternative: the template's Spearman mediator check.* Not taken (the user's choice of 2026-10-28). The cohort manifest already records the covariates per cell, and a flag would mislabel `apoe4`, a genotype, as a mediator candidate.

**D7. `summary.md` of the arm.**
`render_analysis_summary` reads `record.get("latent_adjustment")`. When the block is absent, every line is produced exactly as today, which the D2 gate checks. When present:
- the title gains "— `stage`-conditioned latent-adjustment arm";
- the header clause names the arm, its constant and "read beside the primary, never replacing it";
- a "Latent adjustment" section follows "Latent space" (as in D6);
- each non-rejection reading line adds that the arm's non-rejection is weaker than the primary's (arm rule 5);
- `LATENT_SENSITIVITY_READING_RULES` follows `READING_RULES` under its own heading.

The renderer takes the arm rules from `constants`. It does not need the primary record, since the comparison carries the side-by-side.

**D8. `axis-diagnostics` on an arm.**
- `render_axis_diagnostics` keys on `analysis["latent_adjustment"]`:
  - when it is not null, the opening paragraph names the `stage`-conditioned sensitivity arm and its directory;
  - the sentence "a finding about the measurement space of the primary analysis" becomes "… of this arm (the primary stays primary)";
  - `LATENT_SENSITIVITY_READING_RULES` follows `READING_RULES`.

  On the primary every byte is unchanged. The D10 gate checks that the outputs have the hashes the committed diagnostics manifest (`754c6ba`) records.
- `_check_analysis_inputs` hints name `adni-sexdiff <manifest step>` (`analyze` or `latent-sensitivity`) when the manifest is readable, and both commands when the directory is absent.
- No other behaviour of the diagnostic changes.

**D9. Findings, never stops, beyond those of `analyze`.**
- the arm's rank differs from the primary's (both named);
- a statistic's rejection status differs (named as basis dependence);
- the primary manifest records `n_jobs ≠ 1` (the reference is not a reported run);
- the cohort manifest's descriptive cells differ from the record's `cell_sizes`;
- `diagnostics/` is from a replaced arm (D5).

The `analyze` findings come with the shared function: count deviations, `n_jobs`, rank at the floor, CV repeats, non-finite values, moved MOTCO defaults, CV clamping, and a run that is not pinned (`numerics`). The comparison manifest adds its own not-pinned finding from `_numerics`. A not-pinned arm is not committed.

**D10. Verification, committed outputs.**

Synthetic, on any machine, in the scratchpad (never from a data root):
- `make_synthetic.py` writes an export directory that `_load_analysis_inputs` accepts: blocks of 133 and 165 features for a few hundred participants, a sex × stage design, the five covariates with ADNI's codings, a `phase` offset planted on most of the first block's features, and a manifest with hashes, `block_columns`, codings and counts. It also writes a cohort directory (`cohort.csv` with `dx_bl`, `cohort_manifest.json` with `descriptives`) bound to it.
- The synthetic steps run with the scratch root as the working directory, so the default relative paths resolve there and the diagnostic takes its primary branch.
- The baseline (D2) is run before any edit.

On a data machine:
- **The readiness gate first.** The export CSVs, `cohort.csv`, and the primary's `latent_scores.csv` and `analysis_metadata.csv` must hash to the values the committed manifests record.
  - If any differs or is absent, make the machine ready: a pinned rebuild from its own data root (constraint 2: `clean` → `cohort` → `export` → `analyze`, each into the scratchpad), a hash check of every output the committed manifests record, then the participant-level files copied into the gitignored paths under `results/`, beside the untouched committed manifests. This is the procedure of 2026-10-28.
  - A rebuild that does not reproduce the committed hashes means something other than the CPU differs. It is reported to the user, not resolved here.
- **The exact primary gate (D2).**
- **The exact diagnostics gate:** a pinned `axis-diagnostics --out-dir <scratch>` on the default inputs. Its four CSVs and `diagnostics.md` must have the sha256 the committed diagnostics manifest (`754c6ba`) records; a difference stops the change and D8's wording change is reverted;
- `latent-sensitivity`, then a `--force` rerun into a scratch root for reproducibility;
- the arm's `cli_equivalent` into a scratch directory;
- `--n-jobs 4` into a scratch root;
- `axis-diagnostics` on the arm.

Commit the aggregate files only, named one by one:
- `analysis/`: `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json`, `summary.md`;
- `comparison/`: its three files;
- `diagnostics/`: its six files.

## Risks / Trade-offs

- **The arm's components still track phase.** The basis is fitted on residualized features, but the raw features are measured in it, so a component can carry phase through the raw scores. → This is MOTCO's design: the trajectory model's covariate adjustment acts on the stage means. The arm's diagnostic measures it, and arm rule 9 reads it as a measurement-space finding.
- **The residualization removes much of the p180 variance.** The export recorded a median |d| of 1.12 between runs, so `phase` explains a large share of many p180 features within stage, and the residualized blocks no longer hold the 133 / 165 balance the primary sees. → `feature_r2` records it, and arm rule 6 puts it beside the results. It changes no setting.
- **`statin` is a mediator.** → The roles name it, `latent_sensitivity.md` shows its counts per cell, and arm rule 7 carries the limitation. The covariate set stays the predeclared one.
- **`apoe4` acts on lipids differently by sex.** → The adjustment is additive with no sex × covariate term (`READING_RULES` 5). The arm inherits that assumption and says so through the shared rules.
- **A categorical level drops out of a training set.** The smallest level is 149 against training sets of about 750. → MOTCO's error stops the step with nothing written. No level is merged, since merging would change the covariate coding decided by `adni-cohort`.
- **The arm rejects and is read as the result.** → The primary row comes first everywhere, the status column names the difference as basis dependence, and both sets of rules are printed.
- **The refactor changes the primary or the diagnostic.** → The D2 and D10 gates run before any arm output is committed: byte-identity on the synthetic data, exact hashes on the real data.
- **A run is not pinned.** For example, numpy was imported before `adni_sexdiff` in a script, or a numpy upgrade renamed a CPU feature. → The `numerics` finding names it, the exact gates fail loudly instead of passing at rounding level, and a not-pinned arm is not committed.
- **No machine at hand is a data machine.** → Any machine with a data root becomes one by the pinned rebuild (D10), in under a minute. A machine without one runs the synthetic groups. Nothing about the plan depends on which machine it is.

## Migration Plan

1. On any machine: constants, the shared function and the D2 synthetic gate, the renderers, the step and CLI, the diagnostic's arm wording, the docs. No default of an existing step changes.
2. On a data machine: pull the branch, run `uv sync --locked` and the readiness gate, rebuilding first if it fails. Run the exact D2 and D10 gates against the committed hashes; stop and revert if either differs. Then run `latent-sensitivity`, the reproducibility, CLI and `n_jobs` checks, and `axis-diagnostics` on the arm. Each task line names the machine, which the manifests also record in `numerics`.
3. Commit the aggregate files from a run on the clean tree at the implementing commit, on the same data machine, so the manifests record the commit, as the earlier steps did.
4. Rollback: every output is additive under `results/motco_latent_sensitivity/`. Reverting the code restores `analyze` and `axis-diagnostics`, whose outputs the gates show unchanged.
