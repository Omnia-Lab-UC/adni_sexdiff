# Design

## Context

See `proposal.md` for the motivation, the ladder, the reading rules and the predeclared counts, `spike.md` for the synthetic findings, and the specs for the requirements. This is the state that shapes the approach.

- **Three sensitivity steps exist**, and this one copies their shape most closely from `latent-sensitivity` (`run_latent_sensitivity`). That step reads the primary export and the primary analysis as references, runs its analysis through `_run_trajectory_analysis`, and stages `analysis/` and `comparison/` together. The sweep needs no export of its own: every rank reads the primary export.
- **`_run_trajectory_analysis`** is the analysis body every caller shares (`step`, `latent_adjustment`, `expected`, `manifest_extra`, `loaded`, `staging`, `log`). Its defaults reproduce the primary byte for byte. It builds `TrajectoryAnalysisParams(permutations, seed, n_jobs, min_components, covariate_latent_adjustment)` and has no `forced_components` yet.
- **Three of its findings assume a CV run.** On a forced record (`spike.md`), each of them would fire on every rank:
  - "cross-validation completed 0 of 5 repeat(s)", from `cv_repeats_completed`;
  - "the CV ran with rank floor 1", because `integration_params` has no `min_components`;
  - "MOTCO default `forced_components` is k", from `_MOTCO_DEFAULTS_STATED`.
- **`_analysis_cli_equivalent`** emits the flags the step passes; it has no `--forced-components`. MOTCO's CLI has the flag.
- **`render_analysis_summary`** writes "CV-selected rank" in the `angle` note and a CV line in "Latent space". It keys on the latent adjustment, `export_manifest["variant"]` and `export_manifest["stage_arm"]`; a forced rank has none of them, since its export manifest is the primary's.
- **`_check_primary_reference(analysis_dir, loaded, motco_version, step)`** chains the primary analysis to the export now on disk and returns its record, manifest, rank and `n_jobs`. It reads only the two JSON files. The primary manifest's `outputs` record the sha256 of all six files, `latent_scores.csv` included, so the anchor can be compared without opening a primary participant-level file.
- **`axis-diagnostics`** decides `is_primary` from the analysis directory and the recorded latent adjustment, export variant and stage arm. It records the read under `counts["primary"]` (rank, selection, latent adjustment, `n_jobs`) whatever the read is, and expects only the rank-independent keys on a non-primary read.
- **Ignore rules** already match the sweep's participant-level files (`results/**/latent_scores.csv`, `results/**/analysis_metadata.csv`) and its staging (`results/**/*.tmp/`); `git check-ignore` confirmed this on 2026-10-30.
- **Pinned numerics.** The committed outputs are pinned, so the committed hashes are the reference for the real-data gates on any data machine.

## Goals / Non-Goals

**Goals:**
- One command from the primary export and the primary analysis to the six ranks and the comparison, with the primary held fixed as a chained reference.
- A proof, on every run, that the sweep is the primary with one setting changed: the anchor gate.
- A rank directory that every reader treats as an analysis directory (MOTCO's CLI, `axis-diagnostics`).
- No byte change to any existing output: the primary, its diagnostics, the latent arm, the export variants, the CN / LMCI / AD arm, all their diagnostics, and the report.

**Non-Goals:**
- A generic multi-setting sweep registry. Another sweep axis is its own proposal.
- Report sections for the sweep (a follow-up change).
- A test framework. Verification is synthetic end to end, the exact real-data gates against the committed hashes, `report --check`, and the data machine's run against the predeclared counts.

## Decisions

### D1. A separate `rank-sensitivity` step, not a flag or a registry entry
- **Why a step:** the sweep changes a measurement setting, not the export or the participants, so it is neither an `EXPORT_VARIANTS` entry nor a row subset.
- **Why not a flag:** a `--forced-components` flag on `analyze` would put a rank one flag away from the primary, which constraint 5 forbids, and invites choosing a rank after seeing results.
- **Shape:** `results/motco_rank_sensitivity/` with one analysis directory per rank, `comparison/` and `diagnostics/`. There is no `motco_input/`: every rank's manifest records the primary export as its input, so `axis-diagnostics` reads a rank directory with the default `--input-dir`.

### D2. Constants
```python
RANK_SENSITIVITY_DIR = "results/motco_rank_sensitivity"
RANK_SENSITIVITY_RANK_DIR = "rank_{rank:02d}"           # directory order is rank order
RANK_SENSITIVITY_SUBDIRS = {"comparison": "comparison", "diagnostics": "diagnostics"}
RANK_SENSITIVITY_TABLE = "rank_sensitivity.csv"
RANK_SENSITIVITY_SUMMARY = "rank_sensitivity.md"
RANK_SENSITIVITY_MANIFEST = "rank_sensitivity_manifest.json"

RANK_SENSITIVITY_LADDER: dict = {
    "name": "forced_rank_ladder",
    "setting": "forced_components",
    "ranks": (2, 3, 4, 6, 9, 12),
    "draws": "ANALYSIS_SEED and ANALYSIS_PERMUTATIONS at every rank (the same permutation indices at n_jobs = 1)",
    "anchor": "one forced run at the primary record's rank, compared with the primary before any rank runs; not kept",
    "diagnosed_rank": 12,
    "analysis": "the primary's (the primary export; ANALYSIS_* constants and MOTCO's defaults; no latent adjustment)",
    "change": "adni-rank-sensitivity",
}
assert RANK_SENSITIVITY_LADDER["ranks"] == tuple(sorted(set(RANK_SENSITIVITY_LADDER["ranks"])))
assert RANK_SENSITIVITY_LADDER["ranks"][0] == ANALYSIS_RANK_FLOOR
assert RANK_SENSITIVITY_LADDER["diagnosed_rank"] == max(RANK_SENSITIVITY_LADDER["ranks"])
RANK_SENSITIVITY_READING_RULES: tuple[str, ...] = (...)   # the proposal's eight statements, verbatim

RANK_SENSITIVITY_EXPECTED_COUNTS = {
    "anchor": {"rank": DIAGNOSTICS_EXPECTED_COUNTS["primary"]["selected_rank"]},   # 8, the committed primary's
    "analysis": {
        k: {**ANALYSIS_EXPECTED_COUNTS, "component_selection": "forced", "selected_rank": k, "cv_repeats_completed": 0}
        for k in RANK_SENSITIVITY_LADDER["ranks"]
    },
    "comparison": {"rows": 1 + len(RANK_SENSITIVITY_LADDER["ranks"])},
    "diagnostics": {
        **{key: DIAGNOSTICS_EXPECTED_COUNTS[key] for key in DIAGNOSTICS_RANK_INDEPENDENT_KEYS},
        "primary": {"selected_rank": 12, "component_selection": "forced", "latent_adjustment": None, "n_jobs": 1},
        "rows": {"axis_correlations": 96, "block_pcs": 48, "geometry_shares": 48, "components": 12},
    },
}
```
- **The assertions** keep the ladder ordered, tie its bottom to the floor, and tie the diagnosed rank to its top.
- **`counts["primary"]`** is the diagnostic's existing name for "the analysis read", so the top-rank expectation uses it unchanged.
- **The diagnostics rows** follow from the rank: 12 × 8 variables, 2 blocks × 3 PCs × 8, 4 quantities × 12, and 12.
- **No new participant-level pattern** (Context).

### D3. The anchor gate
After the input checks and before any rank, the step runs `_run_trajectory_analysis(forced_components=<the primary record's rank>, staging=<root>/anchor.tmp, ...)` and compares:
- **record fields:** `statistics`, `p_values`, `null_summary`, `config_spectrum` and `latent.selected_lv` against the primary record, with exact equality (pinned numerics, `spike.md`);
- **files:** the sha256 of `latent_scores.csv`, `pls_loadings.csv` and `stage_means.csv` against the primary manifest's `outputs`.

Then:
- **On equality**, `anchor.tmp/` is removed, and every rank manifest and the comparison manifest record the anchor: the rank, each field and file with `equal: true`, and the hashes.
- **On a difference**, the step stops before any rank runs. It names the field or file and both values, and the numerics state when it is not pinned. `anchor.tmp/` is kept for inspection (it is ignored), as `_finalize_output_dir` keeps a failed staging directory.
- **At `n_jobs ≠ 1`**, the permutation draws differ from the primary's (`REPORTED_N_JOBS`). The gate then compares only the statistics, the rank, `config_spectrum["pooled"]` and the three files; the p-values, null summaries and `config_spectrum["permutation_pooled_eigengap"]` are not compared, and the anchor record says so.
- **Why a gate and not a ladder rank:** the ladder stays independent of any result, and the gate proves the machinery on every machine and every run. A primary regenerated after the sweep fails the reference chain first.
- **Rejected: compare in memory without writing.** Writing the anchor through `_run_trajectory_analysis` is the exact path every rank takes, so the gate tests the files the ranks write, not a second code path.

### D4. `_run_trajectory_analysis` and `_analysis_cli_equivalent` gain `forced_components`
- **New keyword** `forced_components: int | None = None`, passed to `TrajectoryAnalysisParams`.
- **Manifest:** `settings.forced_components` is written only when the value is not `None`.
- **CLI equivalent:** `_analysis_cli_equivalent` emits `--forced-components k` only when it is not `None`.
- **Progress line:** the "CV rank selection" line reads "forced rank k (no cross-validation)" on a forced run.
- **The default leaves every existing caller's bytes unchanged.**
- **New keyword** `rank_sweep: dict | None = None`: the ladder entry, the primary's rank and the anchor record, passed on to `render_analysis_summary` (D6) and added to the manifest under `rank_sweep`.

### D5. Forced-aware findings
In `_run_trajectory_analysis`, when `latent["component_selection"] == "forced"`:
- **CV repeats:** the repeats finding is not raised; `cv_repeats_completed` 0 is the predeclared value.
- **Floor:** the CV-floor finding is not raised. The floor is recorded in `params.min_components` and in the counts, and does not bind a forced run.
- **Moved default:** the `forced_components` comparison expects the forced rank instead of `None`, so a record whose `forced_components` differs from the rank passed is still a finding.
- **Everything else is unchanged:** the deviations, `n_jobs`, non-finite statistics and p-values, the other moved defaults and the numerics.

On a CV record every branch is today's, so the primary and the other arms keep their findings and bytes.

### D6. `render_analysis_summary` and `_statistic_reading_line`
- **`render_analysis_summary`** gains `rank_sweep: dict | None = None`. With it:
  - **title:** gains "— forced rank k (rank sweep)";
  - **header:** the latent clause names the forced rank, `RANK_SENSITIVITY_LADDER`, the setting, the skipped cross-validation, and "read beside the primary, never replacing it";
  - **`angle` note:** reads "forced rank k (rank floor 2)" instead of "CV-selected rank";
  - **"Latent space":** the CV line reads "none (MOTCO skips the cross-validation at a forced rank)";
  - **a "Rank sweep" section** follows "Latent space": the ladder; this rank's place in it; the nesting relative to the primary's rank (the primary's first k components, or the primary's 8 plus k − 8); the anchor result; and a note that `pls_loadings.csv` is rank-specific;
  - **rules:** `RANK_SENSITIVITY_READING_RULES` follows `READING_RULES` under its own heading.

  Without it, every line is today's.
- **`_statistic_reading_line`** gains `rank_sweep: bool = False`, which adds the sweep's note: a rejection the primary does not make is rank dependence, and a non-rejection is no more informative than the primary's. The default leaves every existing sentence unchanged, and `report --check` on the committed tree verifies that.

### D7. The run, the staging and the comparison
`run_rank_sensitivity(*, input_dir, analysis_dir, out_dir, n_jobs, force)` proceeds in this order:
1. **MOTCO gates.**
2. **Existing outputs:** any rank directory or `comparison/` stops the step unless `force`.
3. **Primary export:** `_load_analysis_inputs(input_dir, step="rank-sensitivity")`.
4. **Primary reference:** `_check_primary_reference(analysis_dir, loaded, step="rank-sensitivity")`.
5. **Anchor gate** (D3).

Nothing under the output root is written before step 5 passes, except `anchor.tmp/`. Then each rank runs into `rank_<kk>.tmp/` through `_run_trajectory_analysis(forced_components=k, staging=..., expected=RANK_SENSITIVITY_EXPECTED_COUNTS["analysis"][k], rank_sweep=..., loaded=loaded)`, and the comparison is written into `comparison.tmp/`. All the `.tmp/` directories are renamed together.
- **Nesting check:** before the renames, the step compares each rank's latent scores, in memory, with the first k columns of the top rank's and, for k at most the anchor's rank, with the anchor's (equal to the primary's by the gate). The comparison manifest records a boolean per rank. A false value is a finding, never a stop: it would contradict `spike.md` and is reported as such. No score is printed or written by the check.
- **`diagnostics/`** is never touched. If it exists while `--force` replaces the sweep, a finding records it as stale until `axis-diagnostics` is rerun.
- **Rows:** `_comparison_row` per analysis (`primary`, then `rank_02` … `rank_12`), without the latent-adjustment columns; `directory` is the subdirectory name, so the table does not depend on `--out-dir`. Statuses come from `_comparison_statuses(..., differs="differs (rank dependence)")`, rank by rank against the primary.
- **Shared sentence:** `_rank_status_line(statistic, primary_rejected, statuses)` is one sentence per statistic naming the ranks whose status differs, or "same at every rank", shaped like `_stage_arm_status_line` so the later report change can reuse it.
- **`rank_sensitivity.md`**, in this order:
  1. the header, with the primary's directory and `result.json` hash, the ladder by constant name, MOTCO and `n_jobs`;
  2. the statistics table: per statistic, the primary row then the ranks, each with its status;
  3. the status sentences;
  4. the latent spaces: rank, mode, floor, eigengap with its permutation quantiles, the `angle` null summary;
  5. the anchor check and the nesting;
  6. the findings;
  7. `READING_RULES`, then `RANK_SENSITIVITY_READING_RULES`.

  Numbers carry six significant digits, as in `summary.md`. No runtime column or line, so a rerun is byte-identical.
- **`rank_sensitivity_manifest.json`:** the common keys and the seven inputs with sha256 and the chain results. It also holds:
  - `settings` (`RANK_SENSITIVITY_LADDER`, `ANALYSIS_ALPHA` with the rule, `n_jobs`);
  - `reference` and `anchor`;
  - `ranks` (per rank: directory, `result.json` and manifest sha256, rank);
  - the statuses, the nesting, the counts beside `RANK_SENSITIVITY_EXPECTED_COUNTS["comparison"]`, the outputs and the findings.

### D8. `axis-diagnostics` on a forced rank
- **Detection:** `run_axis_diagnostics` recognizes a sweep read from the analysis manifest's `step == "rank-sensitivity"`. It records `inputs.analysis.rank_sweep` (the forced rank and the primary's rank; `null` on other reads) and sets `is_primary` false.
- **Expectations:** on the diagnosed rank, `RANK_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]`. On another rank of the sweep, the rank-independent keys, plus a finding that the sweep's predeclared diagnostic is the top rank's.
- **`render_axis_diagnostics`:**
  - the opening paragraph names the rank sweep, the forced rank and its directory, and states that components `pls_0` to `pls_<r−1>` (r the primary's rank) are the primary's;
  - a flagged row is a finding about the measurement space at that rank (the primary stays primary);
  - `RANK_SENSITIVITY_READING_RULES` follows `READING_RULES`.
- **`_analysis_command`, `_ANALYSIS_STEPS` and `_EVERY_ANALYSIS_COMMAND`:** they gain `rank-sensitivity` (hint `adni-sexdiff rank-sensitivity --force`); the hint appears only in error messages.
- **Why the top rank only:** nesting makes its components a superset of every rank's. Its rows for `pls_0` … `pls_7` in `axis_correlations.csv` equal the primary's, because they depend only on the scores. So do all of `block_pcs.csv`, which does not depend on the analysis. `geometry_shares.csv` and `components.csv` are rank-specific: the shares sum over the rank's components, and the loading shares come from the rank's rotations. The equal rows are a verification of the change (task 5.6), not a gate of the step, because the diagnostic does not read another diagnostic.

### D9. CLI
`adni-sexdiff rank-sensitivity [--input-dir results/motco_input] [--analysis-dir results/motco_analysis] [--out-dir results/motco_rank_sensitivity] [--n-jobs 1] [--force]`. It prints `[rank-sensitivity]` progress per rank (rank, statistics and p-values, the deviation count) and the anchor result, naming counts and files only. The ladder is never a flag.

### D10. Verification

Synthetic, on any machine, in the scratchpad (never from a data root):
- **Fixtures:** the synthetic export and cohort of `adni-stage-sensitivity` (`make_synthetic.py`), or a rebuild with all five `dx_bl` categories.
- **Baseline before any shared code is edited:** the primary, the latent arm, both variants, the CN / LMCI / AD arm and every diagnostic, at 99 permutations. After the edits, every non-JSON output must be byte-identical.
- **The sweep on the synthetic data:**
  - the anchor passes;
  - the nesting booleans are true;
  - the layout, the predeclared-count deviations naming the synthetic sizes, and `--force` with stale diagnostics;
  - the failure gates on scratch copies: an absent primary, a changed `nmr.csv`, a latent-adjusted analysis given as the primary, an existing output, and a primary manifest whose recorded `latent_scores.csv` hash is edited (the anchor stops).

On a data machine:
- **Readiness:** the primary export CSVs, `cohort.csv` (for the diagnostic), and the primary's `latent_scores.csv` and `analysis_metadata.csv` hash to their committed records.
- **Exact gates before any sweep output is committed**, each into a scratch directory:
  - pinned `analyze`: the committed primary hashes;
  - `axis-diagnostics` on the primary, the latent arm, each variant and the CN / LMCI / AD arm: their committed CSV and `diagnostics.md` hashes;
  - `latent-sensitivity`, `export-sensitivity --variant all` and `stage-sensitivity`: their committed `summary.md` and comparison hashes (`latent_sensitivity.md` line 3 excepted, as before, since it prints a hash that carries MOTCO's runtime);
  - `report --check` on the committed tree.

  A difference stops the change, and the shared code edit is reverted.
- **The sweep:** `rank-sensitivity` pinned at `n_jobs = 1`. Then:
  - a `--force` rerun into a scratch root, for reproducibility;
  - `rank_04`'s and `rank_12`'s `cli_equivalent` into scratch directories;
  - `--n-jobs 4` into a scratch root;
  - `axis-diagnostics` on `rank_12`, with its `pls_0` … `pls_7` rows and its `block_pcs.csv` compared with the committed primary diagnostic.

Commit the aggregate files only, named one by one: per rank `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md`; `comparison/`'s three files; `diagnostics/`'s six files.

## Risks / Trade-offs

- **A forced rank is read as "the" result, or a rank is picked afterwards.** → The ladder is a constant, the primary row comes first in every table, and statuses name rank dependence. Reading rules 1 and 6 bind every reader, and no sweep value feeds a constant.
- **Eighteen readings (six ranks × three statistics) invite a chance rejection.** The ranks are nested and share the draws, so they are strongly dependent, but a forced-rank rejection under no true difference is still plausible. → Rule 6: the sweep is not a test and nothing counts rejections. A forced-rank-only rejection is rank dependence, read beside its null summary.
- **No operating characteristics at a forced rank with covariates at this design.** → Rule 5 cites MOTCO's unadjusted ladder for what it is and states the gap. A MOTCO-side study is out of scope.
- **The ranks below 8 are not independent evidence:** they are subspaces of the primary's latent space. → Rule 3 and the "Rank sweep" section state the nesting, and the comparison manifest records it per rank.
- **The anchor gate is exact, so unpinned numerics can fail it at about 1e-15.** → Runs are pinned (constraint 6). The gate's message names the numerics state, and an unpinned run is not committed anyway.
- **High ranks add technical axes (the p180 run).** → The top rank's diagnostic measures every added component against `phase` and the other variables, and rule 7 reads a flagged axis as a measurement-space finding.
- **`pls_loadings.csv` is not nested**, so a reader could compare loadings across ranks. → The "Rank sweep" section and the design say that the rotations are rank-specific. The diagnostic's `components.csv` is the top rank's own.
- **A shared code edit changes an existing byte.** → The D10 exact gates and `report --check` run before any sweep output is committed. Every new branch keys on `forced_components` or step `rank-sensitivity`, which no existing output carries, and every new keyword defaults to today's behavior.

## Migration Plan

1. On any machine: the constants and assertions; `forced_components` and `rank_sweep` through `_run_trajectory_analysis`, the CLI equivalent, the findings and the summary, with their defaults unchanged; the step, the anchor, the comparison and the CLI; the diagnostic's sweep branch; the docs; and the synthetic checks.
2. On a data machine: the readiness gate (with a pinned rebuild if it fails), then the D10 exact gates and `report --check`. Stop and revert the shared code edit if any differs. Then the sweep, the reproducibility, CLI and `n_jobs` checks, and `axis-diagnostics` on `rank_12`.
3. Commit the aggregate files from a run on the clean tree at the implementing commit, on the same data machine, so the manifests record the commit.
4. Rollback: every output is additive under `results/motco_rank_sensitivity/`. Reverting the code restores every shared function, whose outputs the gates show unchanged.
