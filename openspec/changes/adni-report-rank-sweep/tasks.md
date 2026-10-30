# Tasks

This change introduces no scientific constant. Before the apply starts, the user accepts the proposal's presentation decisions:
- the section title "Rank sensitivity", placed after "Stage-definition sensitivity" (design D4);
- one row per analysis in the latent-space table, and the predeclared-counts table limited to the anchor, the comparison rows and each rank's selection, rank and CV repeats (design D4);
- the anchor and nesting lines moved into shared helpers, and `_anchor_text` listing the compared fields in the gate's order, under the byte gate (design D5, D6);
- components listed in `components.csv` order (design D7);
- each rank's per-statistic reading lines left out, as for the other sensitivities (proposal, out of scope).

Following the user's decision for the previous report, the report is written on 2026-10-31 or later, named by the day it is written, and never over the 2026-10-30 file (design D12).

Every task runs on any machine with the Nix shell and the committed tree. The inputs are the tracked files under `results/`. No data root, data machine or participant-level file is needed, and the step records no numerics. Scratch copies and scratch outputs live in the session scratchpad, never under `results/` or `reports/`, except in task 5.2. No task line records a participant value.

## 1. Constants and the flag

- [x] 1.1 Add the convention `REPORT_RANK_SWEEP_FILES` with the keys `rank`, `comparison` and `diagnostics`, and an import-time assertion that its keys are `("rank", *RANK_SENSITIVITY_SUBDIRS)` (design D2). Extend `REPORT_INPUT_FILES` after the CN / LMCI / AD arm's roles:
  - with `rank-sensitivity/<rank_kk>` for each rank of `RANK_SENSITIVITY_LADDER["ranks"]`, named by `RANK_SENSITIVITY_RANK_DIR`;
  - then with `rank-sensitivity/comparison` and `rank-sensitivity/diagnostics`.

  Add "Rank sensitivity" to `REPORT_SECTIONS` between "Stage-definition sensitivity" and "Findings". Name this change in the module docstring and in the comments of the report constants. Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(sum(len(v) for v in c.REPORT_INPUT_FILES.values()), len(c.REPORT_SECTIONS))"` prints `93 13`;
  - each of the 27 new names, resolved against `RANK_SENSITIVITY_DIR`, is in `git ls-files results/motco_rank_sensitivity`, and the other 12 tracked sweep files are the ranks' `stage_means.csv` and `pls_loadings.csv`.
- [x] 1.2 Add `--rank-sensitivity-dir` to the `report` subparser, with default `RANK_SENSITIVITY_DIR`. Pass it through `cli.main` and `run_report` to `_report_dirs`, and document the parameter in the `run_report` docstring. Verify that `uv run adni-sexdiff report --help` lists twelve flags and that the nine directory flags show their defaults.

## 2. The loader and the gates

- [x] 2.1 Extend the loader as design D2, D3 and D9 describe:
  - `_report_dirs`, `_report_rerun` and `_REPORT_MANIFESTS`: the sweep's roles, rerun hints and eight labels;
  - `_load_report_inputs`:
    - the sweep identity gate (each rank, the ladder, the primary's rank, not crossed, the comparison with its anchor, the diagnostics);
    - the sweep reported-run gate and the version agreement over 29 manifests;
    - the 67 sweep chain links;
    - the sweep's records (`records["ranks"]`, by rank) and tables (the comparison CSV and the diagnostics CSVs) in the returned dict;
  - the `_load_report_inputs` docstring.

  Verify on the committed tree that the loader completes, and that:
  - the provenance lists 93 files, each hash equal to `sha256sum`, and 63 aggregate files are checked against `outputs`;
  - there are 167 chain links (100 + 67), every one `ok`. Record the count in this line (recorded on the committed tree: 167 links, 100 + 67, every one `ok`; 93 files, each equal to `sha256sum`; 63 checked against `outputs`; 29 manifests);
  - the step's own findings are still the five no-`numerics` manifests, with no dirty revision.
- [x] 2.2 Copy the tracked `results/` files into a scratch root (`git ls-files results | xargs cp --parents -t <scratch>`). Run each case below on its own edited copy. In every case the step must stop, naming the file or setting, both values where there are two, and the command to rerun. It must exit 1, create nothing under the scratch `reports/`, and leave the copy otherwise unchanged (every file hashed before and after). The cases:
  - (a) `motco_rank_sensitivity/rank_06/summary.md` deleted → the file and `rank-sensitivity --force`.
  - (b) One byte of `motco_rank_sensitivity/comparison/rank_sensitivity.csv` changed → the file, both hashes, and `rank-sensitivity --force`.
  - (c) `RANK_SENSITIVITY_LADDER["draws"]` patched in-process before the loader runs → the manifest that records the ladder, `RANK_SENSITIVITY_LADDER`, the field, both values, and `rank-sensitivity --force`.
  - (d) The directories `rank_04` and `rank_06` swapped → the directory, the rank it should hold and the rank it holds, named as an identity failure, not as a broken link.
  - (e) `rank_09` replaced by the latent arm's `analysis/` → the directory and the recorded latent adjustment (identity).
  - (f) The rank-3 `result.json` with `measurement.n_jobs` 4, and its manifest's recorded hash updated so the hash gate holds → that `result.json`, 4, and `rank-sensitivity --force` without `--n-jobs`.
  - (g) The comparison manifest's `numerics.pinned` set to false → that manifest.
  - (h) The comparison manifest's `anchor.equal` set to false → that manifest, the anchor, and `rank-sensitivity --force`.
  - (i) The rank-2 manifest's `reference.files.result.json.sha256` edited, and the comparison's record of that manifest updated → the rank-2 manifest, the key, both hashes, and `rank-sensitivity --force`.
  - (j) The rank-12 manifest rewritten with a key reordered, and the comparison's record of it updated, as a `--force` rerun leaves them → the sweep's diagnostics manifest, `inputs.analysis.analysis_manifest.sha256`, both hashes, and the sweep's `axis-diagnostics` command.
  - (k) The sweep's diagnostics manifest with `inputs.analysis.is_primary` true → that manifest and the sweep's `axis-diagnostics` command.

  Record the eleven outcomes in this line (recorded on 2026-10-30, each on its own copy of the 115 tracked files: every case exit 1, no `reports/`, every file unchanged. (a) the file absent and `rank-sensitivity --force`, then the sweep's `axis-diagnostics`; (b) `comparison/rank_sensitivity.csv`, both hashes, the comparison manifest and `rank-sensitivity --force`; (c) `rank_02/analysis_manifest.json (rank_sweep.ladder)`, `RANK_SENSITIVITY_LADDER['draws']`, both values and `rank-sensitivity --force`; (d) `rank_04 does not hold forced rank 4`, the five recorded values against the expected ones, `the directory holds rank 6, not 4` (identity, before the chain); (e) `rank_09 is not forced rank 9`, latent adjustment `'stage'` and the `latent_adjustment` block (identity); (f) `rank_03/result.json (measurement.n_jobs) records n_jobs = 4` and `rank-sensitivity --force` without `--n-jobs`; (g) the comparison manifest records `numerics.pinned False`; (h) the comparison manifest's anchor at rank 8 with equal False, sweep rule 3, `rank-sensitivity --force`; (i) `rank_02/analysis_manifest.json: reference.files.result.json.sha256`, both hashes, `rank-sensitivity --force`; (j) the sweep's `diagnostics_manifest.json: inputs.analysis.analysis_manifest.sha256`, both hashes, `axis-diagnostics --analysis-dir results/motco_rank_sensitivity/rank_12 --out-dir results/motco_rank_sensitivity/diagnostics`; (k) the sweep's diagnostics manifest with `is_primary True`, the expected read and the same `axis-diagnostics` command).
- [x] 2.3 Update the docs for what groups 1 and 2 change:
  - `README.md`, the `report` section: the inputs with the sweep's 27 files, twelve flags, the sweep identity gate and its chain links;
  - `AGENTS.md`, step 6: 93 inputs, 29 manifests and 167 chain links (100, then 67 for the sweep), and the gates;
  - `AGENTS.md`, the Layout entries for `cli.py` (twelve flags), `constants.py` (`REPORT_RANK_SWEEP_FILES`) and `data.py`.

  Verify with `grep` that "66 committed files", "21 manifests", "100 links" and "eleven flags" no longer appear where they describe the current step. (Verified on 2026-10-30: none of the four appears in `README.md`, `AGENTS.md` or `src/`.)

## 3. The renderer

- [x] 3.1 Move the anchor and nesting bullets of `render_rank_sensitivity` into `_rank_anchor_lines`, and its nesting table into `_rank_nesting_table` (header, alignment, rows). Add `_ANCHOR_FIELD_ORDER` and make `_anchor_text` list the compared fields in that order (design D5). Verify the byte gate of design D6:
  - `render_rank_sensitivity`, given the committed records and the committed comparison manifest, returns the committed `results/motco_rank_sensitivity/comparison/rank_sensitivity.md` byte for byte;
  - for each rank, `_rank_sweep_lines` on its manifest's `rank_sweep` block equals the "## Rank sweep" block of its committed `summary.md` line by line;
  - on an in-memory anchor in the gate's order, both the full shape and the n_jobs ≠ 1 shape, `_anchor_text` and `render_rank_sensitivity` return the same text as `main`'s versions, imported from a scratch worktree of eb33b70 (`git worktree add <scratch> eb33b70`, its `src/` first on `PYTHONPATH`).

  Remove the worktree afterwards. If any check fails, revert the change. (Recorded on 2026-10-30: the committed `rank_sensitivity.md` re-rendered from the committed records and comparison manifest, byte for byte, 13899 bytes; the six ranks' "Rank sweep" lines equal, 5 lines each; on the full and the n_jobs = 4 in-memory anchors, `_anchor_text` and `render_rank_sensitivity` equal to eb33b70's; the worktree removed.)
- [x] 3.2 Hoist `render_report`'s inner `flagged_components` to a module-level helper that lists a run's flagged components in the order of its `components.csv` (design D7). Verify on the committed tree:
  - for the primary's, the latent arm's, each variant's and the CN / LMCI / AD arm's diagnostics, the helper returns the same text as the dict-order version;
  - for the sweep's diagnostics it returns `pls_0`, `pls_1`, `pls_3`, `pls_4`;
  - on a scratch copy of the sweep's diagnostics manifest that also flags `pls_10`, it lists `pls_10` after `pls_4`, while the dict-order version lists it before `pls_3`.

  (Recorded on 2026-10-30: the same text for the primary (`pls_0`, `pls_1`, `pls_3`, `pls_4`), the arm (`pls_1`, `pls_2`), `nist_bridge` (`pls_1`), `per_run_standardized` (`pls_1`, `pls_3`) and `cn_lmci_ad` (`pls_0`, `pls_1`, `pls_4`); the sweep `pls_0`, `pls_1`, `pls_3`, `pls_4`; with `pls_10` flagged in memory, `… pls_4, pls_10` against the dict order's `… pls_1, pls_10, pls_3 …`.)
- [x] 3.3 Implement the section "Rank sensitivity", and extend the preamble and the summary, provenance, findings, reading-rules and reproduction sections (design D4). Section numbers in the text come from `_section_ref`. Verify on the committed tree, writing to a scratch `--out`:
  - the level-2 headings equal `REPORT_SECTIONS` in order;
  - the new section holds "Statistics: primary and ranks" with 21 rows: `delta primary` first, then `delta rank_02` … `delta rank_12`. The primary's status is `the result`, and `delta rank_06` is `differs (rank dependence)`;
  - it holds "Latent space: primary and ranks" (7 rows), the anchor and nesting bullets with "Nesting" (6 rows), and "Sweep against the predeclared counts" (20 rows);
  - it holds the top rank's flagged rows, components (12 rows) and block PCs, "First component against phase" with two rows, and one code block with six `cli_equivalent` commands;
  - the reading-rules section holds five numbered lists, the fifth with eight items;
  - the summary carries the sweep's paragraph with section 10 and section 12 references;
  - the renderer holds no literal section number.

  Record the sections, tables and cells generated, and the report's size (recorded on 2026-10-30 for a scratch report dated 2026-10-31: 13 sections, 80 tables (9 in "Rank sensitivity", 588 cells), 4737 cells, 207049 bytes; every check above holds).
- [x] 3.4 Write the scratch value checker `check_report_rank_sweep_values.py` (design D11). It reads the scratch report's new tables and, independently, the source files with `json`, `csv` and `hashlib`. It must report zero differences, compared at the printed digits, for:
  - the statistics rows against `rank_sensitivity.csv`, and the ranks against each `latent.selected_lv`;
  - the latent space against the CSV and `config_spectrum`;
  - the predeclared counts against the manifests' `counts` and `expected`;
  - the diagnostics tables against the sweep's CSVs;
  - the 27 new input hashes against `hashlib` and the recording manifests.

  It must also verify string equality:
  - every row of the latent-space and nesting tables equals the corresponding row of the committed `rank_sensitivity.md`;
  - each status line and the anchor and nesting bullets equal their lines in `rank_sensitivity.md`;
  - the five rule lists equal the constants, item by item.

  List every line that names the sweep or a forced rank together with another sensitivity (the latent arm, a variant or the CN / LMCI / AD arm), and verify that each is a listing, with none comparing them. Also verify that an audit hook (`sys.addaudithook`) over `run_report` lists 93 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git. Record the counts compared (recorded on 2026-10-30, the scratch report of 3.3: 0 differences over 482 values, 73 hash and byte cells (the 27 new inputs against `hashlib`, their sizes and the 19 recording manifests) and 56 strings (the latent-space and nesting tables, the three status lines in the section and in the summary, the anchor and nesting bullets, the 41 items of the five rule lists); 5 lines name the sweep with another sensitivity, each a listing: the preamble, the summary's diagnostics paragraph, `READING_RULES` item 1, sweep rule 8 and the lead of the CLI equivalents; the audit hook: 93 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git).
- [x] 3.5 Verify determinism and the identifier rule:
  - two `--force` runs to the same scratch `--out` have equal sha256;
  - a run to a file named with another date differs only in the title line;
  - `grep -nE '\bRID\b|\brid\b'` over the scratch report hits only column-name mentions.

  (Recorded on 2026-10-30: two `--force` runs, sha256 `089ebd78…117631` both; the run dated 2026-12-01 differs in the title line only; the grep hits 23 lines, the export's `sample column` and 22 `--sample-col rid` arguments of the `cli_equivalent` commands, never a value.)
- [x] 3.6 Update the docs for what group 3 changes:
  - `README.md`, the `report` section: thirteen sections and the fifth rule list. Also the status sentence that says the rank sweep enters the report by a later change;
  - `AGENTS.md`, the status paragraph: the report covers the rank sweep, so remove "a later change adds it to the report", and name the newest report's coverage;
  - `AGENTS.md`, step 6: thirteen sections, the rank section, the fifth rule list, and the shared helpers named (`_rank_status_line`, `_rank_anchor_lines`, `_rank_nesting_table`);
  - `AGENTS.md`, the Layout entry for `data.py`;
  - the `_rank_status_line` docstring, which names the report as a caller.

  Leave "Flag and ask" unchanged. Verify with `grep` that "twelve sections" no longer describes the current step. (Verified on 2026-10-30: the one remaining "twelve sections" names the 2026-10-30 report as an earlier layout; "Flag and ask" unchanged.)

## 4. The checker

- [x] 4.1 Verify the earlier-layout gate, unchanged in code (design D8):
  - `uv run adni-sexdiff report --check --out reports/motco-adni-2026-10-30.md` stops before any input gate. It names the report, the absent section 'Rank sensitivity' and `git log -1 --format=%H -- reports/motco-adni-2026-10-30.md` (2e4a3e1…), writes nothing and exits 1;
  - the same check on the 2026-10-29 report names two absent sections, and on the 2026-10-28 report three;
  - in a scratch worktree of 2e4a3e1, the 2026-10-30 report passes its own check with no mismatch. Remove the worktree afterwards.

  (Recorded on 2026-10-30: the 2026-10-30 report stops naming the absent 'Rank sensitivity', the 2026-10-29 report 'Stage-definition sensitivity' and 'Rank sensitivity', the 2026-10-28 report 'Export sensitivity', 'Stage-definition sensitivity' and 'Rank sensitivity', each with the `git log` command (2e4a3e1, c94f5e7, 36c9cc8), before any input gate, exit 1, the three reports byte-unchanged; in a worktree of 2e4a3e1 the 2026-10-30 report checks with no mismatch, 71 tables, 3546 cells and 680 other lines compared; the worktree removed.)
- [x] 4.2 Run failure checks of the check, each on a copy of the scratch report or of the scratch results root:
  - (a) one p-value of the `delta rank_06` row of "Statistics: primary and ranks" changed by hand → the section, the table, the row, the column and both values; exit 1;
  - (b) one word of a sweep status line changed → the section and the line, with both texts;
  - (c) one cell of "Nesting" changed → the table, the row, the column and both values;
  - (d) in a copy of the results root, the comparison's `rank_sensitivity.md` edited and its manifest's `outputs` hash updated to match → the provenance cells of both files, with both hashes;
  - (e) `report --check` on unchanged inputs → no mismatch, exit 0;
  - (f) every check run leaves the report and the results root unchanged (hashes before and after).

  Record the printed messages in this line (recorded on 2026-10-30 against the scratch report of 3.3, each check 80 tables, 4737 cells and 812 other lines compared: (a) `Rank sensitivity › table "Statistics: primary and ranks" › row delta rank_06 › p (RRPP): report '0.0417', generated '0.0471'`, exit 1; (b) `Rank sensitivity › line 1387: report "- `delta`: … A rejection in a forced rank only …", generated "… A rejection at a forced rank only …"`, exit 1; (c) `Rank sensitivity › table "Nesting" › row rank_09 › columns compared with the anchor's: report '9', generated '8'`, exit 1; (d) `Provenance › table "Inputs"` › the rows of `rank_sensitivity.md` (`f6dee1af…` against `4df97478…`) and `rank_sensitivity_manifest.json` (`d1537b9c…` against `8d0a21fc…`) › sha256, exit 1; (e) no mismatch, exit 0; (f) every report copy, the edited results root, the committed reports and the 115 committed results files unchanged).
- [x] 4.3 Update the docs for the check:
  - `README.md` and `AGENTS.md`, the earlier-layout gate: three earlier reports, `reports/motco-adni-2026-10-28.md` (ten sections, checks at 36c9cc8), `reports/motco-adni-2026-10-29.md` (eleven, c94f5e7) and `reports/motco-adni-2026-10-30.md` (twelve, 2e4a3e1).

  Verify with `grep` that the three reports and the three revisions are named. (Verified on 2026-10-30: each of `README.md` and `AGENTS.md` names the three reports and 36c9cc8, c94f5e7 and 2e4a3e1.)

## 5. The report and commit hygiene

- [x] 5.1 Commit the implementation, the docs and the change's artifacts on the branch `adni-report-rank-sweep`. Verify that `git status` is clean and that no file under `results/` or `reports/` changed. (Committed on 2026-10-30 on `adni-report-rank-sweep`, from eb33b70; `git status` clean after it; the commit touches `src/`, `README.md`, `AGENTS.md` and the change's artifacts only.)
- [ ] 5.2 Only once `date +%F` is later than 2026-10-30 (design D12), on the clean tree at the implementing commit:
  - run `uv run adni-sexdiff report` (no `--out`, so it is named by today's date), then `uv run adni-sexdiff report --check`;
  - verify the check passes and reads the new report as the newest;
  - verify that `grep -nE '\bRID\b|\brid\b'` over the new report hits only column-name mentions;
  - verify that the three earlier reports are byte-unchanged.

  Commit the new report alone, and record its name, sections, tables, cells, chain links and size in this line.
- [ ] 5.3 Check commit hygiene. Verify that:
  - `git status` is clean;
  - `git ls-files results` lists the same 115 files as `main`;
  - no file under `results/` changed in any commit of the branch;
  - over every file the branch adds or changes, the identifier grep finds only column names (`RID`, `rid`), never a participant value.

## Workflow follow-up

- After the report is committed, archive the change on the branch. The archive syncs `openspec/specs/case-study-report/`, and `openspec validate --strict` must pass on the synced spec. Then push, open the PR and merge, following the PR workflow of the earlier changes.
- A regenerated results directory invalidates the committed report: `report --check` fails on its provenance cells until a new report is written and checked.
- With this change every predeclared sensitivity is in the report. The next changes are each their own proposal: the other export variants (all 245 NMR columns first), each of which extends the report's sections and re-issues the report. The cluster run waits on the deploy key (constraint 7).
