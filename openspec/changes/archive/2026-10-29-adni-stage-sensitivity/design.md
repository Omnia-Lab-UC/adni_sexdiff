# Design

## Context

See `proposal.md` for the motivation, the arm, the reading rules and the predeclared counts, `spike.md` for every number, and the specs for the requirements. This is the state that shapes the approach.

- **Two sensitivity steps exist**, and this one copies their shape:
  - `latent-sensitivity` (`run_latent_sensitivity`). It reads the primary export and the primary analysis as references, runs the arm through `_run_trajectory_analysis`, and stages `analysis/` and `comparison/`.
  - `export-sensitivity` (`run_export_sensitivity`, `_run_export_variant`). It writes its own `motco_input/` per variant, loads it from the staging directory (`_load_analysis_inputs(e_tmp)`), passes the final path as `input_dir` so the record and `cli_equivalent` name it, and renames `motco_input/`, `analysis/` and `comparison/` together.
- **`_run_trajectory_analysis`** is the analysis body all callers share (`step`, `latent_adjustment`, `expected`, `manifest_extra`, `loaded`, `staging`, `log`). Its defaults reproduce the primary byte for byte.
- **The reference checks.** `_check_primary_reference(analysis_dir, loaded, motco_version, step)` chains the primary analysis to the export now on disk. `_check_cohort_chain(cohort_dir, export_manifest, rids)` checks that `cohort.csv` equals its manifest, that the manifest equals the export's record, and that the both-flag rows are the exported participants in order. It returns those rows, `dx_bl` included.
- **The export manifest contract** that the readers rely on:
  - `_load_analysis_inputs` reads `outputs.<csv>.sha256`, `settings.covariates` and `settings.block_columns`;
  - `axis-diagnostics` also reads `inputs.cohort.manifest.sha256` and `counts.phase_offset`;
  - `render_analysis_summary` reads `counts` and keys on `variant`.

  An export directory that carries these keys is read unchanged by every reader. The feature tables are not part of the contract.
- **The primary export's CSVs** are written by pandas `to_csv`: one record per line, `\n` terminators, `rid` first. `cohort.csv`'s both-flag rows are in the same order (the cohort chain).
- **The sensitivity-aware renderers.**
  - `render_analysis_summary` keys on `record["latent_adjustment"]` (the latent arm) and `export_manifest["variant"]` (an export variant).
  - `render_axis_diagnostics` keys on the analysis manifest's latent adjustment and `variant`.
  - `_statistic_reading_line` takes `arm` and `variant`, and the report reuses it.
  - `_analysis_command` names the step that wrote an analysis directory.

  On the reads that exist today, every one of them is gated by committed hashes or `report --check`.
- **Pinned numerics.** Every committed output is pinned, so the committed hashes are the reference for the real-data gates on any data machine. nixos-home is a data machine: the spike checked its cohort, export and cleaned files against the committed manifests on 2026-10-29.

## Goals / Non-Goals

**Goals:**
- One command from the primary export, the primary analysis and the cohort to the arm's export, analysis and comparison. The primary is held fixed as a chained reference.
- An arm export that every reader treats as an export (loader, MOTCO's CLI, `axis-diagnostics`), whose rows are provably the primary's.
- No byte change to any existing output: the primary, its diagnostics, the latent arm, the export variants, their diagnostics, and the report.

**Non-Goals:**
- A generic participant-filter registry. A later arm with another stage definition is its own proposal and may generalize the step then.
- Report sections for the arm (a follow-up change).
- A test framework. Verification is synthetic end to end, the exact real-data gates against the committed hashes, `report --check`, and the data machine's run against the predeclared counts.

## Decisions

### D1. A separate `stage-sensitivity` step, not an export variant or a flag
- **Why a step:** the arm changes the participants, not the p180 values. `EXPORT_VARIANT_READING_RULES` 2 says that a variant "differs only in the p180 values" and shares "the participants". A third registry entry would contradict a decided rule.
- **Why not a flag:** a filter flag on `export` or `analyze` would put a cohort choice one flag away from the primary, which constraint 5 forbids.
- **Shape:** the step follows `export-sensitivity`'s layout without `bridge/`.

### D2. The arm export copies the primary's rows as text
For each of `p180.csv`, `nmr.csv`, `metadata.csv` and `covariates.csv`, the step reads the primary file as bytes, keeps the header line and the lines of the kept participants (by position, in file order), and writes them unchanged.
- **Check before writing:** each file has exactly one line per participant plus the header. The `rid` at the start of each kept line equals the participant's `rid` in `metadata.csv`.
- **Check after writing:** the arm file, read as the loader reads it, equals the primary frame restricted to the kept rows (`DataFrame.equals`). The manifest records `rows_equal_primary: true` per file.
- **Why:** byte identity holds by construction, whatever pandas' float parser does. The spec's "rows byte-identical" needs no tolerance.
- **Rejected: read with pandas and write back with `to_csv`.** That is round-trip exact only with `float_precision="round_trip"`, and a future pandas could change float formatting. The text copy has neither risk.

### D3. The keep mask comes from `cohort.csv`, checked against the export
`_check_cohort_chain` runs on the primary export as it does for `axis-diagnostics`, and returns the both-flag rows in export order. The step then:
- **Category check:** stops if a `dx_bl` is outside `STAGE_RULE["map"]`, naming the column and a count.
- **Mask:** keeps the rows whose `dx_bl` is in `STAGE_SENSITIVITY_ARM["keep"]`.
- **Stage check:** stops if a kept row's `stage` in `metadata.csv` differs from the arm's map of its `dx_bl` (a count, never a participant). The map is asserted equal to `STAGE_RULE`'s at import, so this can only fail on inputs that broke the cohort contract.

No `dx_bl` is written to the arm export. `metadata.csv` keeps `rid`, `sex` and `stage`.

### D4. Constants
```python
STAGE_SENSITIVITY_DIR = "results/motco_stage_sensitivity"
STAGE_SENSITIVITY_SUBDIRS = {"export": "motco_input", "analysis": "analysis", "comparison": "comparison", "diagnostics": "diagnostics"}
STAGE_SENSITIVITY_TABLE = "stage_sensitivity.csv"
STAGE_SENSITIVITY_SUMMARY = "stage_sensitivity.md"
STAGE_SENSITIVITY_MANIFEST = "stage_sensitivity_manifest.json"

STAGE_SENSITIVITY_ARM: dict = {
    "name": "cn_lmci_ad",
    "source": "dx_bl",                       # cohort.csv, ADNIMERGE DX.bl on the bl row
    "keep": ("CN", "LMCI", "AD"),
    "drop": ("SMC", "EMCI"),
    "stage_map": {"CN": "CN", "LMCI": "MCI", "AD": "AD"},
    "floors": "the primary export's (EXPORT_FEATURE_RULE over the exported participants); the arm's rows are the primary export's rows",
    "analysis": "the primary's (ANALYSIS_* constants and MOTCO's defaults; no latent adjustment)",
    "change": "adni-stage-sensitivity",
}
assert set(STAGE_SENSITIVITY_ARM["keep"]) | set(STAGE_SENSITIVITY_ARM["drop"]) == set(STAGE_RULE["map"])
assert all(STAGE_RULE["map"][dx] == st for dx, st in STAGE_SENSITIVITY_ARM["stage_map"].items())
assert tuple(STAGE_SENSITIVITY_ARM["stage_map"]) == STAGE_SENSITIVITY_ARM["keep"]
STAGE_SENSITIVITY_READING_RULES: tuple[str, ...] = (...)   # the proposal's eight statements, verbatim
STAGE_SENSITIVITY_EXPECTED_COUNTS = {
    "export": {
        "participants": 1130,
        "dropped": {"SMC": 96, "EMCI": 275},
        "sex_stage": {"Female": {"CN": 183, "MCI": 187, "AD": 125}, "Male": {"CN": 181, "MCI": 296, "AD": 158}},
        "phase_by_stage": {"CN": {"ADNI1": 192, "ADNI2GO": 172}, "MCI": {"ADNI1": 338, "ADNI2GO": 145}, "AD": {"ADNI1": 154, "ADNI2GO": 129}},
        "features": {"p180": 133, "nmr": 165},
        "rows_equal_primary": {"p180.csv": True, "nmr.csv": True, EXPORT_METADATA: True, EXPORT_COVARIATES: True},
        "missing_covariate_values": 0,
        "non_finite": {"p180": 0, "nmr": 0},
        "phase_offset": {"p180": {"abs_d_gt_0_5": 107, "abs_d_gt_1": 77}, "nmr": {"abs_d_gt_1": 0}},
    },
    "analysis": {
        **ANALYSIS_EXPECTED_COUNTS,
        "participants": 1130,
        "sex_stage": <as above>,
        "covariate_levels": {"apoe4": {"0": 589, "1": 413, "2": 128}, "phase": {"ADNI1": 684, "ADNI2GO": 446}, "statin": {"0": 603, "1": 527}},
    },
    "diagnostics": {**{k: DIAGNOSTICS_EXPECTED_COUNTS[k] for k in DIAGNOSTICS_RANK_INDEPENDENT_KEYS}, "participants": 1130, "sex_stage": <as above>},
}
```
- **The assertions** tie the arm to `STAGE_RULE`, so a later change to the stage rule cannot leave the arm describing another rule.
- **Participant-level pattern:** `PARTICIPANT_LEVEL_PATTERNS` gains `results/motco_stage_sensitivity/motco_input/*.csv`, and `.gitignore` and `scripts/sync_results.sh` gain the same pattern, before the first run (constraint 1).

### D5. The arm export manifest
`motco_input/manifest.json` carries the export-manifest contract keys (Context) plus the arm's own.

Contract keys:
- `settings.block_columns` and `settings.covariates`, copied from the primary export manifest;
- `outputs`: the four CSVs with sha256, bytes and `participant_level: true`;
- `inputs.cohort.manifest`: the cohort manifest's name and sha256, as the primary export records it, so `_check_cohort_chain` works unchanged on the arm's own manifest;
- `counts`:
  - `participants`, `sex_stage`, `features`, `missing_covariate_values` and `non_finite`;
  - `phase_offset` per block, from `_phase_offset` on the arm's rows (the loader's float parse, as `export` measures its own output);
  - `spectrum` and `shape`, from the export's functions on the arm's rows, for the diagnostic's context.

The arm's own keys:
- `step: "stage-sensitivity"` and `stage_arm` (the constant by name);
- `reference`:
  - the primary export's directory and manifest sha256;
  - the feature tables' recorded sha256, as the source of the floors;
  - the primary's `counts.phase_offset`, `sex_stage` and `phase_by_stage`, so the summary can show both without reading the primary;
- `counts.dropped` and `counts.phase_by_stage`;
- `counts.rows_equal_primary`;
- `expected`, `deviations`, `findings`, `numerics`, `versions` and `git_revision`.

### D6. The run and the staging
`run_stage_sensitivity(*, input_dir, analysis_dir, cohort_dir, out_dir, n_jobs, force)` proceeds in this order:
1. **MOTCO gates.**
2. **Existing outputs:** the three output subdirectories, which stop the step unless `force`.
3. **Primary export:** `_load_analysis_inputs(input_dir, step="stage-sensitivity")`.
4. **Primary reference:** `_check_primary_reference(analysis_dir, loaded, step="stage-sensitivity")`.
5. **Cohort chain:** `_check_cohort_chain(cohort_dir, export_manifest, rids)` and the D3 checks.

Nothing is written before step 5 passes. Then, inside nested `_finalize_output_dir`-style staging (`motco_input.tmp/`, `analysis.tmp/`, `comparison.tmp/`), as `_run_export_variant` does:
- write the arm export (D2, D5);
- `_load_analysis_inputs(e_tmp)`;
- `_run_trajectory_analysis(input_dir=<final motco_input>, latent_adjustment=None, expected=STAGE_SENSITIVITY_EXPECTED_COUNTS["analysis"], manifest_extra=<arm and reference>, loaded=..., staging=a_tmp, step="stage-sensitivity")`;
- write the comparison.

The three directories are renamed together.
- **`diagnostics/`** is never touched. If it exists while `--force` replaces the arm, a finding records it as stale until `axis-diagnostics` is rerun.
- **Rejected: pass the subset in memory, with no `motco_input/`.** MOTCO's CLI reproduction and `axis-diagnostics` both need the files.

### D7. The comparison
- **Rows:** `_comparison_row` (the latent arm's) with a `participants` column added, then `_comparison_statuses(..., differs="differs (stage-definition dependence)")`.
- **Shared sentence:** `_stage_arm_status_line` is the sentence `stage_sensitivity.md` prints per statistic, shaped like `_export_variant_status_line` so the later report change can reuse it.
- **`stage_sensitivity.md`**, in this order:
  1. the header, with both directories, both `result.json` hashes, the arm by constant name and `n_jobs`;
  2. the statistics table with statuses;
  3. the latent space (ranks, floors, eigengaps, null summaries beside `angle`);
  4. the participants: kept and dropped by `dx_bl` × sex, the cells of both, and runs within stage of both;
  5. the covariate levels of both records;
  6. the run offset per block of both exports;
  7. the findings;
  8. `READING_RULES`, then `STAGE_SENSITIVITY_READING_RULES`.

  Numbers carry six significant digits, as in `summary.md`. No runtime column or line, so a rerun is byte-identical.
- **`stage_sensitivity_manifest.json`:** the common keys, and the nine inputs with sha256 and the chain results. It also holds `settings` (`STAGE_SENSITIVITY_ARM`, `ANALYSIS_ALPHA` with the rule, `n_jobs`), `reference` and `arm` (directory, `result.json` and manifest sha256, rank), the statuses, outputs and findings.

### D8. `render_analysis_summary` and `_statistic_reading_line`
- **`render_analysis_summary`** keys on `export_manifest.get("stage_arm")`. With the key present:
  - the title gains "— CN / LMCI / AD arm `cn_lmci_ad`";
  - the header names the arm, its constant and "read beside the primary, never replacing it";
  - an "Arm" section follows "Latent space", with the D7 items 4 to 6, from the arm export manifest's `counts` and `reference`;
  - the export context names the run offset on the arm's rows beside the primary's;
  - `STAGE_SENSITIVITY_READING_RULES` follows `READING_RULES` under its own heading.

  Without the key, every line is produced as today.
- **`_statistic_reading_line`** gains `stage_arm: bool = False`, which adds the arm's note: a rejection the primary does not make is stage-definition dependence, and a non-rejection is no more informative than the primary's. The default leaves every existing sentence unchanged. That is what keeps `summary.md`, `latent_sensitivity.md`, `export_sensitivity.md` and the report byte-identical, and `report --check` on the committed tree verifies it.

### D9. `axis-diagnostics` on the arm
- **Detection:** `run_axis_diagnostics` recognizes the arm from the analysis manifest's `step == "stage-sensitivity"` and records `inputs.analysis.stage_arm` (`null` on other reads).
- **`_check_cohort_chain`:** when the export manifest carries `stage_arm`, it filters the both-flag rows by `keep` before comparing with the exported `rid`s. The `dx_bl` variable then comes from those rows.
- **Expectations:** with the arm present, `participants` and `sex_stage` come from `STAGE_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]`. The read is not the primary, so only the rank-independent keys are expected, as on every non-primary read.
- **`render_axis_diagnostics`:**
  - the opening paragraph names the CN / LMCI / AD arm and its directory;
  - a flagged row is a finding about the arm's measurement space (the primary stays primary);
  - `STAGE_SENSITIVITY_READING_RULES` follows `READING_RULES`.
- **`_analysis_command` and `_ANALYSIS_STEPS`:** they gain `stage-sensitivity`. The "every command" hint names four commands; it appears only in error messages, never in an output.

### D10. Verification

Synthetic, on any machine, in the scratchpad (never from a data root):
- The synthetic export and cohort of `adni-nist-bridge` (session scratchpad `15832845…/scripts/make_synthetic.py`, or a rebuild), with `dx_bl` holding all five categories and SMC and EMCI only in `ADNI2GO`.
- The primary pipeline on them, then `stage-sensitivity` and `axis-diagnostics` on the arm.
- Byte identity of the kept rows, the counts, the staging, `--force` with stale diagnostics, and the failure gates on scratch copies: a reordered `cohort.csv`, a stale cohort manifest, a `dx_bl` outside the rule, an existing output.
- Before any shared renderer is edited, a baseline of the synthetic primary's `summary.md` and diagnostics. After the edit, they must be byte-identical.

On a data machine (nixos-home, or any machine after the pinned rebuild of `adni-latent-sensitivity` D10):
- **Readiness:** the export CSVs, `cohort.csv`, and the primary's `latent_scores.csv` and `analysis_metadata.csv` hash to their committed records.
- **Exact gates before any arm output is committed:**
  - pinned `analyze --out-dir <scratch>`: the committed primary hashes;
  - `axis-diagnostics` on the primary, the latent arm and each variant into scratch directories: their committed CSV and `diagnostics.md` hashes;
  - `latent-sensitivity` and `export-sensitivity --variant all` into scratch roots: their committed `summary.md` and comparison hashes;
  - `report --check` on the committed tree.

  A difference stops the change and the renderer edit is reverted.
- **The arm:** `stage-sensitivity`, then a `--force` rerun into a scratch root (reproducibility), the arm's `cli_equivalent` into a scratch directory, `--n-jobs 4` into a scratch root, and `axis-diagnostics` on the arm.

Commit the aggregate files only, named one by one:
- `motco_input/manifest.json`;
- `analysis/`: `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json`, `summary.md`;
- `comparison/`: its three files;
- `diagnostics/`: its six files.

## Risks / Trade-offs

- **The arm is read as "the clean result".** Its definition matches ADNI-1's enrollment, which can look more principled. → Every output puts the primary row first and names the status as stage-definition dependence. Reading rules 1 and 6 bind every reader. The proposal states that no arm value adopts it.
- **The runs stay unbalanced across stages.** The arm's MCI is 70 % ADNI-1. → Reading rule 4 states it with the spike's shares. The arm's manifest and summary print the runs within stage. `phase` stays a covariate, as in the primary.
- **The floors are computed over participants the arm drops.** → This is the decided choice: one scale for both analyses. The spike measured the alternative at a median of 4 % (p180) and 0.8 % (NMR) per floor. MOTCO re-standardizes each call. The proposal lists a recomputed-floor arm as out of scope.
- **The MCI stage changes meaning.** It is LMCI only. → Reading rule 5. `angle` reads the endpoints, and the arm's AD cells equal the primary's.
- **Smaller cells.** The smallest is Female AD at 125, unchanged; Female MCI falls from 310 to 187. → Reading rule 6: a non-rejection is no more informative than the primary's.
- **A shared renderer edit changes an existing byte.** → The D10 exact gates and `report --check` run before any arm output is committed. Every new branch keys on a manifest key that no existing output carries.
- **A future pandas writes CSV lines differently.** → The arm copies text (D2), so its rows never depend on the writer. A changed primary export would fail its own committed-hash gates first.

## Migration Plan

1. On any machine: the constants and assertions, the ignore patterns, the arm export, the step and CLI, the renderers with their defaults unchanged, the diagnostic's arm branch, the docs, and the synthetic checks.
2. On a data machine: the readiness gate (with a pinned rebuild if it fails), then the D10 exact gates and `report --check`. Stop and revert the renderer edit if any differs. Then the arm, the reproducibility, CLI and `n_jobs` checks, and `axis-diagnostics` on the arm.
3. Commit the aggregate files from a run on the clean tree at the implementing commit, on the same data machine, so the manifests record the commit.
4. Rollback: every output is additive under `results/motco_stage_sensitivity/`. Reverting the code restores every renderer, whose outputs the gates show unchanged.
