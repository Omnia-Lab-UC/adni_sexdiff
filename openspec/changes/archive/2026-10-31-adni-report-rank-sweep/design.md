# Design

## Context

See `proposal.md` for the motivation and scope, and `specs/case-study-report/spec.md` for the requirements. This is the state that shapes the approach.

- **The report step today** (changes `adni-report`, `adni-report-variants` and `adni-report-stage-arm`, `data.py`):
  - `_load_report_inputs` reads `REPORT_INPUT_FILES` by role through `_report_dirs`: 66 files, 21 manifests in `_REPORT_MANIFESTS`, and a rerun hint from `_report_rerun`.
  - It runs five gates in order: presence, hashes against `outputs`, identity, reported runs, and the chain (100 links).
  - `render_report` writes the twelve `REPORT_SECTIONS` through `_ReportBuilder`. Every table sits under a level-3 heading and is keyed `"<section> › <title>"`, and section numbers come from `_section_ref`.
  - `_diagnostics_section(..., prefix=…)` renders one diagnostics run, and `_first_component_rows` reads each run's first component against `phase`.
  - `check_report` starts with `_check_report_layout`, which is generic over `REPORT_SECTIONS`.
- **The sweep's outputs are tracked.** `git ls-files results/motco_rank_sensitivity` lists 39 files (115 under `results/` in all):
  - per rank, five aggregate files;
  - the comparison's three files;
  - the diagnostics' six files.

  The report reads 27 of them. The other 12, each rank's `stage_means.csv` and `pls_loadings.csv`, are quoted by hash through the rank's manifest. Each rank's `latent_scores.csv` and `analysis_metadata.csv` are gitignored, and their hashes are in the manifests.
- **The chain fields of the sweep's manifests.** All eight record revision 08e5ddc (clean) and pinned `numerics`, with no deviation. Each records MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8.
  - **Each rank's `analysis_manifest.json`** (`step` `rank-sensitivity`):
    - `settings.forced_components`, `settings.n_jobs` 1, `settings.latent_adjustment` None, `settings.cli_equivalent` with `--forced-components`;
    - `rank_sweep`: `ladder` (the constant plus `constant`), `forced_rank`, `primary_rank` 8 and `anchor`;
    - `inputs.export_manifest.sha256` and `inputs.files.<csv>.recorded`;
    - `reference.files.{result.json, analysis_manifest.json}.sha256` and `reference.export.manifest.sha256`;
    - `counts` and `expected` (selection `forced`, the rank, 0 CV repeats).

    It has no `variant` or `stage_arm` block. Rank 6 records one finding, its `delta` status. Each `result.json` records `measurement.n_jobs` 1, `latent.selected_lv` equal to the rank and `latent.component_selection` `forced`, and has no `latent_adjustment` block.
  - **`comparison/rank_sensitivity_manifest.json`**:
    - `settings.RANK_SENSITIVITY_LADDER` and `settings.n_jobs`;
    - `reference.files` and `reference.export.manifest.sha256`;
    - `anchor` (`equal`, `rank`, `expected_rank`, `fields`, `files`, `n_jobs`, `not_compared`);
    - `ranks.<rank_kk>.files.{result.json, analysis_manifest.json}.sha256`;
    - `inputs.export.export_manifest.sha256`, and `inputs.primary.files`, which repeat `reference.files`;
    - `counts`: `ranks`, `rejected`, `statuses`, `eigengap`, `component_selection`, `nesting`, `nesting_holds`, `rows`;
    - the rank-6 finding.
  - **`diagnostics/diagnostics_manifest.json`**: the fields of the other diagnostics runs, with `inputs.analysis.is_primary` false and `inputs.analysis.rank_sweep` `{forced_rank: 12, primary_rank: 8}`. Its findings are four flagged components (`pls_0`, `pls_1`, `pls_3`, `pls_4`, the primary's flagged components) and the not-the-primary note.
- **Manifests store dicts with sorted keys.** `_write_manifest` sorts keys. This affects two dicts:
  - **`anchor.fields`.** The anchor gate builds it in comparison order (`statistics`, `p_values`, `null_summary`, `config_spectrum`, `selected_lv`), but the manifest stores it alphabetically. `_anchor_text` lists the fields in dict order. Called on the anchor as the manifest records it, it therefore gives a line that differs from the committed `rank_sensitivity.md` and the ranks' `summary.md`. A read-only re-render while the proposal was written showed this. With the fields in the gate's order, the same re-render reproduced the committed `rank_sensitivity.md` byte for byte and every rank's "Rank sweep" lines.
  - **`counts.per_component`** of a diagnostics manifest. For rank 12 it is stored as `pls_0, pls_1, pls_10, pls_11, pls_2, …`. `render_report`'s inner `flagged_components` lists components in that dict order. Every run reported so far has at most 8 components, so no committed line shows the problem.
- **Shared code that already exists:**
  - `_rank_status_line` writes the three status bullets of `rank_sensitivity.md`; its docstring already names the report as a later caller;
  - `_anchor_text` writes the anchor clause of `rank_sensitivity.md` and of each rank's `summary.md` ("Rank sweep" lines, through `_rank_sweep_lines`);
  - `_rank_sweep_rules_heading` returns a level-2 heading and a lead line, shared by the sweep's documents;
  - `render_rank_sensitivity` writes the anchor bullet, the nesting bullet and the nesting table inline.
- **The three committed reports:**
  - `reports/motco-adni-2026-10-30.md`: twelve sections, committed at 2e4a3e1;
  - `reports/motco-adni-2026-10-29.md`: eleven sections, committed at c94f5e7;
  - `reports/motco-adni-2026-10-28.md`: ten sections, committed at 36c9cc8.

  Today is 2026-10-30, so a report written today would take the name of an existing file.

## Goals / Non-Goals

**Goals:**
- One report that carries the primary and every predeclared sensitivity that has run. Each is shown beside the primary, never beside another sensitivity. Every number is copied, and every sentence is a constant or comes from an existing renderer.
- The same gates for the sweep as for the other sensitivities. A stale, swapped, crossed or unanchored sweep directory stops the report and names the command that fixes it.
- No byte of a committed sweep document changes, and no future output of `rank-sensitivity` changes.
- Nothing that needs a data root, a data machine, MOTCO at run time or pinned numerics.

**Non-Goals:**
- A general registry of sensitivities. The sweep's ranks come from `RANK_SENSITIVITY_LADDER`, and its roles are fixed, as the other sensitivities' are.
- Each rank's per-statistic reading lines (proposal, out of scope).
- Any value across ranks that is not in a record or a manifest. In particular, no "ranks that reject" count and no trend (sweep rule 6).
- Unifying the primary row's status cell of the latent-adjustment table (`same`) with the newer sections (`the result`). The new section follows the newer convention, as in `adni-report-stage-arm`.

## Decisions

**D1. The sweep is a fixed extension of the same step.**
- `report` stays one step with one contract.
- The sweep's roles are read from `--rank-sensitivity-dir`:
  - `rank-sensitivity/<rank_kk>`, one per rank of `RANK_SENSITIVITY_LADDER["ranks"]`, named by `RANK_SENSITIVITY_RANK_DIR`;
  - `rank-sensitivity/comparison` and `rank-sensitivity/diagnostics`, through `RANK_SENSITIVITY_SUBDIRS`.
- The sweep is required, and no flag skips it, as for the other sensitivities.
- *Alternative:* a separate sweep report. Rejected, as in `adni-report-stage-arm` D1: the reading rules bind one reader of all results, and a second document would repeat the provenance and the gates.

**D2. Inputs, roles and labels.**
- **Constant.** A new convention, `REPORT_RANK_SWEEP_FILES`, has three keys:
  - `rank`: `result.json`, `analysis_manifest.json`, `summary.md` (read in each rank directory);
  - `comparison`: `rank_sensitivity.csv`, `rank_sensitivity.md`, `rank_sensitivity_manifest.json`;
  - `diagnostics`: `DIAGNOSTICS_FILES`.

  An import-time assertion ties its keys to `("rank", *RANK_SENSITIVITY_SUBDIRS)`. `REPORT_INPUT_FILES` gains the eight roles after the CN / LMCI / AD arm's, the ranks in ladder order: 27 more files, 93 in all.
- **Labels.** `_REPORT_MANIFESTS` gains eight labels after the arm's, for 29 in all:
  - `rank-sensitivity (rank_02)` … `rank-sensitivity (rank_12)`;
  - `rank-sensitivity (comparison)`;
  - `axis-diagnostics (rank_12)`, from `diagnosed_rank`.

**D3. Gates.** They run in the order of `adni-report` D3, extended to the sweep.
1. **Presence.** Every input is present. The hint for an absent file is its role's command (D9).
2. **Hashes.** No code change here. Each rank's `result.json` and `summary.md`, the comparison's CSV and Markdown and the diagnostics' five files are checked against `outputs.<name>.sha256` of their role's manifest: 19 more, 63 in all.
3. **Identity.** After the CN / LMCI / AD arm, the sweep is checked:
   - **Each rank directory holds its rank.** Its manifest records `step` `rank-sensitivity`. `settings.forced_components` and `rank_sweep.forced_rank` both equal the directory's rank. Its `result.json` records `latent.selected_lv` equal to it and `latent.component_selection` `forced`. A swapped directory is named with the rank it should hold and the rank it holds.
   - **The ladder.** Each rank's `rank_sweep.ladder.constant` is `RANK_SENSITIVITY_LADDER`. Every field of the constant (`name`, `setting`, `ranks`, `draws`, `anchor`, `diagnosed_rank`, `analysis`, `change`) equals the recorded field, with tuples compared as lists.
   - **The primary's rank.** Each rank's `rank_sweep.primary_rank` equals the primary record's `latent.selected_lv`.
   - **Not crossed.** Each rank records `settings.latent_adjustment` None, has no `latent_adjustment` block in its `result.json`, and has no `variant` or `stage_arm` block. The chain (gate 5) then ties every rank to the primary export.
   - **Comparison.** `step` is `rank-sensitivity`, and `settings.RANK_SENSITIVITY_LADDER` equals the constant field by field. Its `ranks` hold exactly the ladder's directories, each with `rank` equal to its directory's rank. `anchor.equal` is true and `anchor.rank` equals the primary record's rank.
   - **Diagnostics.** They record `inputs.analysis.is_primary` false, `inputs.analysis.rank_sweep.forced_rank` equal to `diagnosed_rank`, and `primary_rank` equal to the primary record's rank.

   A failed anchor never writes outputs, so `anchor.equal` false on disk means an edited or foreign manifest; the gate names it as such. A failed nesting check is a finding of the step, never a stop, and the report carries it (D10).
4. **Reported runs.**
   - Every rank records `n_jobs = REPORTED_N_JOBS` in `settings.n_jobs` and in `measurement.n_jobs`, with the hint `rank-sensitivity --force` without `--n-jobs`.
   - Every `numerics` block must be pinned, now over 29 manifests.
   - The version agreement covers the manifests that record each package.
5. **Chain.** The 100 links stay, and the sweep adds 67, for 167 in all.
   - **Each rank (8 × 6 = 48):**
     - `export_file_links` against the primary export (5): the export manifest and the four `inputs.files.<csv>.recorded`;
     - `reference.files` (2) against the primary's `result.json` and `analysis_manifest.json`;
     - `reference.export.manifest` against the primary export manifest.
   - **Comparison (15):**
     - `reference.files` (2) against the primary;
     - `ranks.<rank_kk>.files` (12) against each rank's `result.json` and `analysis_manifest.json`;
     - `inputs.export.export_manifest` against the primary export manifest.

     Not linked: `inputs.primary.files`, which repeat `reference.files`, and `inputs.export.files`, which the ranks' links cover.
   - **Diagnostics (4):** `diagnostics_links` with the primary export role: the rank-12 analysis manifest, its `result.json` as that manifest records it, the primary export manifest and the cohort manifest.

   Not linked: the anchor's `files.*.primary_sha256`. These are the primary manifest's own `outputs`, and the `reference.files` links already pin that manifest's hash.

   A `--force` rerun of the sweep after its diagnostics breaks the first diagnostics link, and the hint names the sweep's `axis-diagnostics` command. A regenerated primary breaks every rank's `reference` links and the comparison's, and the hint names `rank-sensitivity --force`. On the committed tree all 67 links hold. A read-only script checked them while the proposal was written, and task 2.1 rechecks them through the loader.

**D4. The section "Rank sensitivity".** It is number 10, between "Stage-definition sensitivity" and "Findings". The title names what the sweep varies, as the other sensitivity sections do. Its contents, in order:
- **Lead paragraph.**
  - The primary, with the `result.json` hash from the comparison's `reference` and its CV-selected rank.
  - Beside it, the sweep `forced_rank_ladder` (`RANK_SENSITIVITY_LADDER`, change `adni-rank-sensitivity`), as the comparison manifest records it: the forced ranks, the one setting, the draws, and every other setting the primary's. Then its directory.
  - Every table in the section is read under `READING_RULES` and `RANK_SENSITIVITY_READING_RULES` (section 12).
  - The primary row comes first and its status is the result, and no rank is chosen, adopted or ranked (sweep rule 1).
  - A status that differs is rank dependence (sweep rule 2).
  - The sweep is not a test (sweep rule 6), and it is read against the primary only (sweep rule 8).
- **"Statistics: primary and ranks".**
  - For each statistic, the row `<statistic> primary`, then `<statistic> rank_kk` in ladder order: 21 rows.
  - Columns: row, statistic, analysis, rank, observed, p (RRPP), rejected, null mean, null sd, null q95, status.
  - Values come from `rank_sensitivity.csv`, and statuses from `counts.statuses` of the comparison manifest.
  - The primary's status cell reads `the result`.
  - Digits are as in the other comparison tables.
- **The `angle` paragraph:** read beside each analysis' rank, floor (`ANALYSIS_RANK_FLOOR`), eigengap and its own null summary, never against another rank's `angle` (reading rule 2, sweep rule 4).
- **"Status per statistic:"**, a lead line followed by the three bullets from `_rank_status_line`, string-equal to `rank_sensitivity.md`. Each rank's own rejection comes from its `result.json` through `_rejected`, and its status from the comparison manifest.
- **"Latent space: primary and ranks".**
  - One row per analysis (7), keyed by the analysis, with the columns of `rank_sensitivity.md`'s latent-space table: rank (selection), rank floor, `cv_mean_auroc`, CV repeats completed, pooled relative eigengap, eigengap null q05 / q50 / q95, and `angle` null mean / sd / q95.
  - Values come from the CSV and each record's `config_spectrum`.
  - The table is one row per analysis, not one column, because seven analyses would make a quantity-per-row table too wide.
- **"Anchor and nesting".** Under its level-3 heading:
  - the anchor and nesting bullets, from the shared helper (D5);
  - the table "Nesting", from `counts.nesting` of the comparison manifest through the shared helper: rank, first columns of rank 12's, columns compared with the anchor's, equal to the anchor's.
- **"Sweep against the predeclared counts".**
  - Rows `anchor.rank`, `comparison.rows`, then per rank `<rank_kk>.selected_rank`, `<rank_kk>.component_selection` and `<rank_kk>.cv_repeats_completed`: 20 rows.
  - Columns: quantity, observed, expected, read from the comparison manifest's `anchor` / `counts` / `expected` and each rank manifest's `counts` / `expected`.
  - A lead line says that the other keys of `RANK_SENSITIVITY_EXPECTED_COUNTS` are compared by the steps, with any deviation copied under "Findings".
- **Diagnostics of the top rank.**
  - A lead paragraph names the directory, the forced rank 12 and the primary's rank as `inputs.analysis.rank_sweep` records them, and `is_primary` false.
  - It states sweep rule 7: the components up to the primary's rank are the primary's, with the primary's correlations, and a component above it that tracks a variable is a measurement-space finding about the higher ranks and never grounds to choose a rank.
  - It names the flagged components above the primary's rank. This is a selection by component order from `components.csv` (D7), not a computation; on the committed outputs it is "none".
  - Then `_diagnostics_section(..., prefix="rank_12: ")`.
- **"First component against phase".** Rows for the primary and `rank_12`, read from the two axis-correlations CSVs, as the other sensitivity sections have. By nesting the two rows are equal; the report prints both and does not compare them.
- **The six ranks' `cli_equivalent`**, in one code block, in ladder order.

The other sections draw on the same inputs:
- **Preamble.** It names `adni-report-rank-sweep` among the changes and `rank_sensitivity.md` among the documents whose sentences it prints. It adds "the rank sweep under `READING_RULES` and `RANK_SENSITIVITY_READING_RULES`".
- **Summary.**
  - After the CN / LMCI / AD arm's paragraph comes the sweep's. It opens with the ladder, its constant, change, ranks and setting, the anchor at the primary's rank, and "section 10". There is no "selected rank" clause, since no rank is selected.
  - It continues "Status per statistic (`same` when …, else `differs (rank dependence)`; the primary's status is the result either way), read under `READING_RULES` and `RANK_SENSITIVITY_READING_RULES` (section 12):", followed by the three `_rank_status_line` bullets.
  - The diagnostics paragraph adds the top rank's flagged-row counts and flagged components, in its own clause.
- **Provenance.** The versions, revisions-and-numerics, inputs and chain tables extend by iteration. No new table is added.
- **Findings.** The eight new manifests are iterated under their paths.
- **Reading rules.** A fifth level-3 heading, `RANK_SENSITIVITY_READING_RULES`, holds the lead line of `_rank_sweep_rules_heading` and the eight rules, numbered.
- **Reproduction.** After the CN / LMCI / AD arm's commands come two more:
  - `uv run adni-sexdiff rank-sensitivity`, which reads the primary export's CSVs, so it runs on a data machine;
  - `uv run adni-sexdiff axis-diagnostics --analysis-dir results/motco_rank_sensitivity/rank_12 --out-dir results/motco_rank_sensitivity/diagnostics`.

  The list of MOTCO `cli_equivalent`s adds the six ranks. The count in its lead sentence comes from the lists, not a literal.

Section numbers in the text come from `_section_ref`. The reading rules move from section 11 to 12 and reproduction to 13, and no literal number is written. About 12 tables are added. The apply records the exact counts.

**D5. The anchor and nesting lines are shared, not copied.**
- **The constraint.** The report must print the anchor bullet, the nesting bullet and the nesting table string-equal to `rank_sensitivity.md`. `render_rank_sensitivity` writes all three inline, and the report keys every table by a level-3 heading, so it cannot reuse that block as it is.
- **The decision.**
  - Move the two bullets into `_rank_anchor_lines(anchor, *, top, primary_rank)`, returning the bullet texts without their list marker.
  - Move the table into `_rank_nesting_table(nesting, ranks, *, top)`, returning the header, the alignment and the rows. This is the pattern of `_stage_arm_tables`.
  - `render_rank_sensitivity` calls both and prints them with the separators it prints now. The report calls both under its own heading.
- **The field order.** `_anchor_text` lists the compared fields in a fixed order, the gate's comparison order. This order is a module constant, `_ANCHOR_FIELD_ORDER`, beside `_ANCHOR_FILES`: `statistics`, `p_values`, `null_summary`, `config_spectrum`, `config_spectrum.pooled`, `selected_lv`, the order in which `_check_anchor` compares them. `_check_anchor` itself is not changed. The order of the dict it is given no longer matters.
  - An in-memory anchor (`_check_anchor`'s) is already in that order, so the step's output does not change.
  - An anchor read back from a manifest (sorted keys) now gives the same line.
  - In the n_jobs ≠ 1 mode the fields are `statistics`, `config_spectrum.pooled` and `selected_lv`, also in that order.
- *Alternative:* sort the fields in the report only. Rejected: the report's line would then differ from the committed documents, which used the gate's order.
- *Alternative:* teach the parser to key a table by its lead line. Rejected for the reason given in `adni-report-stage-arm` D5.

**D6. Shared code keeps its bytes.**
- **Called unchanged.** The report calls `_rank_status_line` and the lead line of `_rank_sweep_rules_heading` as they are.
- **Changed with a byte gate.** D5 changes `render_rank_sensitivity` internally and fixes `_anchor_text`'s order. Four gates follow, and any failure reverts the change:
  - **The comparison document.** `render_rank_sensitivity`, given the committed records (each rank's and the primary's `result.json`, rows through `_rank_comparison_row`) and the committed comparison manifest (`statuses`, `reference`, `anchor`, `nesting`, `findings`, `n_jobs`), returns the committed `rank_sensitivity.md` byte for byte (sha256 `f6dee1af…`).
  - **The ranks' summaries.** Each rank's `_rank_sweep_lines`, given its manifest's `rank_sweep` block, equals the "## Rank sweep" block of its committed `summary.md` line by line.
  - **Unchanged for future runs.** On an in-memory anchor in the gate's order, in both the full and the n_jobs ≠ 1 shape, `_anchor_text` and `render_rank_sensitivity` return the same text as `main`'s versions, imported from a scratch worktree of eb33b70.
  - **The report.** The report's anchor and nesting bullets and its nesting rows equal the committed document's lines.
- **Nothing else.** No other renderer changes, apart from the component order of D7, which changes no committed line.

**D7. Components in component order.**
- `render_report`'s `flagged_components` lists the flagged components of a diagnostics run in the order of that run's `components.csv`, not of `counts.per_component`, whose keys the manifest sorts.
- The new section's "above the primary's rank" selection takes its components from the same order.
- On the committed outputs no existing line changes: every run but rank 12 has at most 8 components, and rank 12's flagged components (`pls_0`, `pls_1`, `pls_3`, `pls_4`) are in the same order either way.
- *Alternative:* sort by the numeric suffix of `pls_<i>`. Rejected: it relies on the naming, while `components.csv` already holds MOTCO's order.

**D8. Reports of an earlier layout.** `_check_report_layout` is generic over `REPORT_SECTIONS` and is not changed. After the change:
- `report --check --out reports/motco-adni-2026-10-30.md` stops, naming the absent section "Rank sensitivity" and `git log -1 --format=%H -- reports/motco-adni-2026-10-30.md`. That command gives 2e4a3e1, where the report checks.
- The 2026-10-29 report stops naming two absent sections and checks at c94f5e7. The 2026-10-28 report stops naming three and checks at 36c9cc8.
- All three files stay in place, unchanged.
- *Alternative:* keep the twelve-section renderer behind a layout version. Rejected, as in `adni-report-variants` D6.

**D9. Flags, rerun hints and constants.**
- **The flag.** `--rank-sensitivity-dir`, default `RANK_SENSITIVITY_DIR`. `report` then has twelve flags.
- **Rerun hints.** `_report_rerun` gains a branch for the sweep's roles, placed before its latent-sensitivity fallback:
  - ranks and comparison: `adni-sexdiff rank-sensitivity --force`, then the sweep's `axis-diagnostics`;
  - diagnostics: `adni-sexdiff axis-diagnostics --analysis-dir <root>/rank_12 --out-dir <root>/diagnostics`.

  The reported-run hint is `rank-sensitivity --force` without `--n-jobs`.
- **Constants.** `REPORT_RANK_SWEEP_FILES` and `REPORT_INPUT_FILES` (D2) and `REPORT_SECTIONS` (thirteen titles) are conventions. `_ANCHOR_FIELD_ORDER` is a module constant of `data.py` (D5). No scientific constant is added, and "Flag and ask" is unchanged.

**D10. Findings.** No new finding type is added. The report's own findings stay the five no-`numerics` manifests, because the eight new ones are pinned and clean. The sweep's findings are copied verbatim under their labels:
- the rank-6 `delta` finding, twice (rank 6 and the comparison);
- the top rank's four flagged-component findings and its not-the-primary note.

A failed nesting check would appear the same way, with the nesting table showing `no`.

**D11. Verification.** It runs on any machine with the Nix shell and the committed tree, all in the session scratchpad.
- **Byte gate.** The four gates of D6.
- **Values.** An independent script reads the scratch report's new tables and, with `json`, `csv` and `hashlib`, the sources. It compares every value at the printed digits:
  - the statistics with `rank_sensitivity.csv`, and the ranks with each `latent.selected_lv`;
  - the latent space with the CSV and `config_spectrum`;
  - the predeclared counts with the manifests' `counts` and `expected`;
  - the diagnostics tables with the sweep's CSVs;
  - the 27 new input hashes with `hashlib` and the recording manifests.

  Every row of the latent-space and nesting tables must equal the corresponding row of the committed `rank_sensitivity.md`.
- **Strings.**
  - The status lines, the anchor bullet and the nesting bullet are string-equal to `rank_sensitivity.md`.
  - The five rule lists are string-equal to the constants.
  - No sentence or table reads the sweep against another sensitivity. Every line that names the sweep or a forced rank together with another sensitivity is listed, and each must be a listing.
- **Failure cases.** Each runs on an edited scratch copy of the tracked `results/`. In every case nothing is written, the exit code is 1, and the copy is otherwise unchanged:
  - a rank input absent;
  - an edited `rank_sensitivity.csv`;
  - a field of `RANK_SENSITIVITY_LADDER` patched in-process;
  - two rank directories swapped;
  - a rank directory replaced by the latent arm's analysis;
  - a rank with `n_jobs` 4;
  - an unpinned comparison manifest;
  - the comparison's anchor not equal;
  - a rank's `reference` hash edited;
  - stale sweep diagnostics;
  - sweep diagnostics with `is_primary` true.
- **Determinism.** Two `--force` runs are byte-identical. A run to another date differs in the title line only.
- **Checks.**
  - `--check` passes on a fresh scratch report.
  - On the three committed reports it stops with the layout message.
  - In a worktree of 2e4a3e1 the 2026-10-30 report passes its own check.
- **Audit.** An audit hook over `run_report` lists 93 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none of them participant-level.

**D12. The report written at the apply.** This follows the user's decision for `adni-report-stage-arm` (its D11).
- **Date.** The report is written on the clean tree at the implementing commit, on the first date after 2026-10-30, or later. It is named by the day it is written: `report` without `--out` uses today's date.
- **Name.** `reports/motco-adni-2026-10-30.md` is never overwritten, and no `--force` is used on a committed report. No `--out` names a date other than the day of writing.
- **Order.** If the implementation is done on 2026-10-30, the report task waits for the next day. Archive, push and merge come after it.
- **Record.** The counts (sections, tables, cells and chain links) go in `tasks.md`.

## Risks / Trade-offs

- **Report length.** The report grows from 153526 bytes to an estimated 200 KB. Most of the growth is the 67 chain links, the 27 inputs and the six `cli_equivalent` commands, printed in the section and in the reproduction list. Mitigation:
  - the ranks' `stage_means.csv` and `pls_loadings.csv` stay quoted by hash;
  - only the top rank's diagnostics are quoted;
  - the statistics and latent-space tables are one table each for all ranks.
- **The `_anchor_text` order fix could change committed bytes.** The D6 gates compare the step's text with `main`'s and with the committed documents, and a failure reverts the change. The read-only re-render done for the proposal already gave the committed bytes with the gate's order.
- **Primary and top-rank diagnostics look duplicated.** Rank 12's first eight components are the primary's, so their flagged rows and the first-component row repeat the primary's. Accepted: sweep rule 7 says so, and the report states it instead of hiding the rows. Hiding them would be a selection by value.
- **A reader could read a forced rank against another sensitivity's CV-selected rank.** For example, forced rank 4 beside the latent arm's selected 4, or forced rank 6 beside the CN / LMCI / AD arm's 6. Mitigation: the sweep's paragraph and section never name another sensitivity's rank, sweep rule 8 is printed, and the verification lists every line that names both.
- **The apply spans two days.** The report waits for 2026-10-31. Accepted, as before. The implementation commit and every verification can be done before then.
- **The earlier reports are not checkable by the new code.** Accepted. The layout gate says so and names the revision, and each report checks at its own revision (D8, D11).
- **A stale, swapped or crossed sweep directory.** It is caught by the identity gate and the chain (D3), and each names its command.

## Migration Plan

1. Branch `adni-report-rank-sweep` from `main` (eb33b70).
2. Add the constants, the flag, the loader and gates, the renderer, the D5 helpers with the `_anchor_text` order, and the D7 component order. Verify on the committed tree as D11 describes.
3. Update `README.md`, `AGENTS.md` and the docstrings, then commit the implementation.
4. On 2026-10-31 or later, write `reports/motco-adni-<date>.md` on the clean tree at the implementing commit, run `report --check`, and commit the report alone.
5. Archive the change on the branch, then push, open the PR and merge.

Rollback: revert the branch. The committed results are untouched, and the three earlier reports stay checkable at their own revisions.
