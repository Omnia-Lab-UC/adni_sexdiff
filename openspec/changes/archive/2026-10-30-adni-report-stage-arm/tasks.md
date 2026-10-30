# Tasks

This change introduces no scientific constant. Before the apply starts, the user accepts the proposal's presentation decisions:
- the section title "Stage-definition sensitivity", placed after "Export sensitivity" (design D4);
- the four arm-definition tables under level-3 headings, with the rows of `_stage_arm_lines` moved into a shared helper under the byte gate (design D5, D6);
- the primary row's status `the result` in the new statistics table (design D4).

The user has already decided that the report is written on 2026-10-30 or later, named by the day it is written, and never over the 2026-10-29 file (design D11).

Every task runs on any machine with the Nix shell and the committed tree. The inputs are the tracked files under `results/`. No data root, data machine or participant-level file is needed, and the step records no numerics. Scratch copies and scratch outputs live in the session scratchpad, never under `results/` or `reports/`, except in task 5.2. No task line records a participant value.

## 1. Constants and the flag

- [x] 1.1 Add the convention `REPORT_STAGE_ARM_FILES`, keyed by the keys of `STAGE_SENSITIVITY_SUBDIRS` (design D2). Extend `REPORT_INPUT_FILES` with the roles `stage-sensitivity/<subdir>` after the variants' roles. Add "Stage-definition sensitivity" to `REPORT_SECTIONS` between "Export sensitivity" and "Findings". Name this change in the module docstring and in the comments of the two report constants. Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(sum(len(v) for v in c.REPORT_INPUT_FILES.values()), len(c.REPORT_SECTIONS))"` prints `66 12`;
  - each of the 13 new names, resolved against `STAGE_SENSITIVITY_DIR`, is in `git ls-files results/motco_stage_sensitivity`.
  - Done 2026-10-29: `66 12`; the 13 names are tracked, and the other two tracked arm files are the arm analysis' `stage_means.csv` and `pls_loadings.csv`, quoted by hash. `REPORT_STAGE_ARM_FILES` carries an import-time assertion that its keys are `STAGE_SENSITIVITY_SUBDIRS`'s, in order.
- [x] 1.2 Add `--stage-sensitivity-dir` to the `report` subparser, with default `STAGE_SENSITIVITY_DIR`. Pass it through `cli.main` and `run_report` to `_report_dirs`, and document the parameter in the `run_report` docstring. Verify that `uv run adni-sexdiff report --help` lists eleven flags and that the eight directory flags show their defaults.
  - Done 2026-10-29: eleven flags besides `-h`; the eight directory flags show their defaults, `--stage-sensitivity-dir` with `results/motco_stage_sensitivity`.

## 2. The loader and the gates

- [x] 2.1 Extend the loader as design D2, D3 and D8 describe:
  - `_report_dirs`, `_report_rerun` and `_REPORT_MANIFESTS`: the arm's roles, rerun hints and four labels;
  - `_load_report_inputs`: the arm identity gate, the arm reported-run gate, the version agreement over 21 manifests, the 24 arm chain links, and the arm's tables in the returned `tables` (the comparison CSV and the diagnostics CSVs);
  - the `_load_report_inputs` docstring.

  Verify on the committed tree that the loader completes, and that:
  - the provenance lists 66 files, each hash equal to `sha256sum`;
  - there are 100 chain links (76 + 24), every one `ok`. Record the count in this line;
  - the step's own findings are still the five no-`numerics` manifests, with no dirty revision.
  - Done 2026-10-29: 66 files hashed under 21 directories, 21 manifests, 44 aggregate files equal to their `outputs` hashes; 66 provenance rows, every hash equal to `sha256sum`; 100 chain links (76 + 24), all `ok`; findings the five no-`numerics` manifests (clean p180, clean nmr, cohort, export, analyze), no dirty revision.
- [x] 2.2 Copy the tracked `results/` files into a scratch root (`git ls-files results | xargs cp --parents -t <scratch>`). Run each case below on its own edited copy. In every case the step must stop, naming the file or setting, both values where there are two, and the command to rerun. It must exit 1, create nothing under the scratch `reports/`, and leave the copy otherwise unchanged (every file hashed before and after). The cases:
  - (a) `motco_stage_sensitivity/diagnostics/diagnostics_manifest.json` deleted → the file, and the `axis-diagnostics` command with the arm's three directories.
  - (b) One byte of `motco_stage_sensitivity/comparison/stage_sensitivity.csv` changed → the file, both hashes, and `stage-sensitivity --force`.
  - (c) `STAGE_SENSITIVITY_ARM["floors"]` patched in-process before the loader runs → the arm export manifest, `STAGE_SENSITIVITY_ARM`, the field, both values, and `stage-sensitivity --force`.
  - (d) The arm's `analysis/` replaced by the latent arm's (`results/motco_latent_sensitivity/analysis`) → the directory and the recorded name or latent adjustment, named as an identity failure, not as a broken link.
  - (e) The arm's `result.json` with `measurement.n_jobs` 4, and its manifest's recorded hash updated so the hash gate holds → that `result.json`, 4, and `stage-sensitivity --force` without `--n-jobs`.
  - (f) The arm comparison manifest's `numerics.pinned` set to false → that manifest.
  - (g) The arm export manifest's `reference.feature_tables.features_p180.csv.sha256` edited → that manifest, the key, both hashes, and `stage-sensitivity --force`.
  - (h) The arm analysis manifest rewritten with a key reordered, and the comparison's record of it updated, as a `--force` rerun leaves them → the arm diagnostics manifest, `inputs.analysis.analysis_manifest.sha256`, both hashes, and the arm's `axis-diagnostics` command.
  - (i) The arm diagnostics manifest with `inputs.analysis.is_primary` true → that manifest and the arm's `axis-diagnostics` command.

  Record the nine outcomes in this line.
  - Done 2026-10-29 (scratch `checks/failure_cases.py`): all nine exit 1, leave every file of the copy unchanged and create no `reports/`. (a) absent input, the file and `axis-diagnostics --input-dir results/motco_stage_sensitivity/motco_input --analysis-dir results/motco_stage_sensitivity/analysis --out-dir results/motco_stage_sensitivity/diagnostics`; (b) the CSV, both hashes, `stage-sensitivity --force`, then the arm's `axis-diagnostics`; (c) the arm export manifest, the arm, `floors`, both values, `STAGE_SENSITIVITY_ARM['floors']`, `stage-sensitivity --force`; (d) `results/motco_stage_sensitivity/analysis is not the CN / LMCI / AD arm's analysis`: the arm None, latent adjustment 'stage' and the `latent_adjustment` block (identity, not a link); (e) `result.json (measurement.n_jobs) records n_jobs = 4`, `stage-sensitivity --force` without `--n-jobs`; (f) the comparison manifest, `numerics.pinned False`; (g) the arm export manifest, `reference.feature_tables.features_p180.csv.sha256`, both hashes, `stage-sensitivity --force`; (h) the arm diagnostics manifest, `inputs.analysis.analysis_manifest.sha256`, both hashes, the arm's `axis-diagnostics` command; (i) the arm diagnostics manifest, `is_primary True`, the arm's `axis-diagnostics` command.
- [x] 2.3 Update the docs for what groups 1 and 2 change:
  - `README.md`, the `report` section: the inputs with the arm's 13 files, eleven flags, the arm identity gate and its chain links;
  - `AGENTS.md`, step 6: 66 inputs, 21 manifests and 100 chain links (76, then 24 for the arm), and the gates;
  - `AGENTS.md`, the Layout entries for `cli.py` (eleven flags), `constants.py` (`REPORT_STAGE_ARM_FILES`) and `data.py`.

  Verify with `grep` that "53 committed files", "17 manifests", "76 links" and "ten flags" no longer appear where they describe the current step.
  - Done 2026-10-29: none of the four appears in `README.md`, `AGENTS.md` or `src/`; the `run_report`, `_load_report_inputs` and `constants.py` docstrings name 66 inputs, 21 manifests and 100 links. The `data.py` module docstring also names `stage-sensitivity` and the report's three changes.

## 3. The renderer

- [x] 3.1 Move the headers and rows of the four tables of `_stage_arm_lines` into one helper (design D5). `_stage_arm_lines` calls the helper and keeps its lead lines. Verify the byte gate of design D6:
  - on the committed arm export manifest, `_stage_arm_lines` returns the same list as `main`'s version, imported from a scratch worktree of 975ccd8 (`git worktree add <scratch> 975ccd8`, its `src/` first on `PYTHONPATH`);
  - that list equals line by line the "## Arm" block of the committed `results/motco_stage_sensitivity/comparison/stage_sensitivity.md` and of `results/motco_stage_sensitivity/analysis/summary.md`.

  Remove the worktree afterwards. If either check fails, revert the refactor.
  - Done 2026-10-29: the helper is `_stage_arm_tables` (header, alignment `l`/`r`/`c`, rows per table); `_stage_arm_lines` keeps its bullets and lead lines and prints the helper's tables with the same separators. On the committed arm export manifest its 43 lines equal those of 975ccd8's version, and the "## Arm" blocks of `stage_sensitivity.md` (up to "## Findings") and of the arm's `summary.md` (up to "## Covariates") equal them line by line. Worktree removed. `_markdown_table` learned the `c` alignment (`:---:`), which no earlier table uses.
- [x] 3.2 Implement the section "Stage-definition sensitivity", and extend the summary, provenance, findings, reading-rules and reproduction sections (design D4). Section numbers in the text come from `_section_ref`. Verify on the committed tree, writing to a scratch `--out`:
  - the level-2 headings equal `REPORT_SECTIONS` in order;
  - the new section holds "Statistics: primary and arm", with `delta primary` first, then `delta cn_lmci_ad`, and the primary's status `the result`;
  - it holds the latent-space table, the "Arm `cn_lmci_ad`" bullets, the four arm-definition tables (5, 2, 3 and 7 rows), "Run offset: primary and arm" (4 rows) and "Arm export against the predeclared counts";
  - it holds the arm's flagged rows, components and block PCs, "First component against phase" with two rows, and one `cli_equivalent` block;
  - the reading-rules section holds four numbered lists, the fourth with eight items;
  - the summary carries the arm's paragraph with section 9 and section 11 references;
  - the renderer holds no literal section number.

  Record the sections, tables and cells generated.
  - Done 2026-10-29 (scratch `--out`): 12 sections, 71 tables (58 before), 3546 cells (2850 before), parsed back equal; the new section holds 13 tables and 444 cells: statistics (6 rows, `delta primary` first, primary status `the result`), latent space (7), the four definition tables (5, 2, 3, 7), run offset (4), arm export counts (24), flagged latent components (4), flagged block PCs (5), components (6), block PCs (2), first component against phase (2), and one `cli_equivalent` block. Reading-rule lists 9 / 9 / 7 / 8. The summary's arm paragraph refers to sections 9 and 11, and its diagnostics paragraph adds the arm's 4 raw / 1 partial flagged rows (`pls_0`, `pls_1`, `pls_4`). No `section <n>` literal in `data.py`. Report 153526 bytes (122375 before).
- [x] 3.3 Write the scratch value checker `check_report_stage_arm_values.py` (design D10). It reads the scratch report's new tables and, independently, the source files with `json`, `csv` and `hashlib`. It must report zero differences, compared at the printed digits, for:
  - the statistics rows against `stage_sensitivity.csv`, and the ranks against `latent.selected_lv`;
  - the latent space against the CSV and `config_spectrum`;
  - the offsets and counts against the two export manifests;
  - the diagnostics tables against the arm's CSVs;
  - the 13 new input hashes against `hashlib` and the recording manifests.

  It must also verify string equality:
  - every row of the four arm-definition tables equals the corresponding row of the committed `stage_sensitivity.md`;
  - each status line and each of the five arm bullets equals its line in `stage_sensitivity.md`;
  - the four rule lists equal the constants, item by item.

  List every line that names the arm and another sensitivity (the latent arm or a variant), and verify that each is a listing, with none comparing them. Also verify that an audit hook (`sys.addaudithook`) over `run_report` lists 66 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none participant-level. Record the counts compared.
  - Done 2026-10-29: 0 differences over 222 values, 140 strings and 22 hashes (13 by `hashlib`, 9 against the recording manifests). The four tables' lines (separators included), the three status lines (section and summary) and the five bullets equal `stage_sensitivity.md`; the rule lists equal the constants. Three lines name the arm beside another sensitivity, each a listing: the preamble (each sensitivity under its own rules), the summary's diagnostics counts (one clause per run) and the list of MOTCO CLI equivalents. Audit: 66 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git.
- [x] 3.4 Verify determinism and the identifier rule:
  - two `--force` runs to the same scratch `--out` have equal sha256;
  - a run to a file named with another date differs only in the title line;
  - `grep -nE '\bRID\b|\brid\b'` over the scratch report hits only column-name mentions.
  - Done 2026-10-29: two `--force` runs sha256 `dbb69ac5…ef38824`, equal; a run named 2026-11-02 differs in line 1 only; the grep hits 11 lines, the export bullet (sample column `rid`) and the ten `--sample-col rid` of the `cli_equivalent` commands.
- [x] 3.5 Update the docs for what group 3 changes:
  - `README.md`, the `report` section: twelve sections, and the fourth rule list;
  - `AGENTS.md`, the status paragraph: the report covers the CN / LMCI / AD arm, so remove "a later change adds it to the report";
  - `AGENTS.md`, step 6: twelve sections, the stage-definition section, the fourth rule list, and the shared helpers named (`_stage_arm_status_line`, `_stage_arm_lines` and the new table helper);
  - `AGENTS.md`, the Layout entry for `data.py`.

  Leave "Flag and ask" unchanged. Verify with `grep` that "eleven sections" no longer describes the current step.
  - Done 2026-10-29: "eleven sections" remains only where `README.md` and `AGENTS.md` describe `reports/motco-adni-2026-10-29.md`; "Flag and ask" unchanged.

## 4. The checker

- [x] 4.1 Verify the earlier-layout gate, unchanged in code (design D7):
  - `uv run adni-sexdiff report --check --out reports/motco-adni-2026-10-29.md` stops before any input gate. It names the report, the absent section 'Stage-definition sensitivity' and `git log -1 --format=%H -- reports/motco-adni-2026-10-29.md` (c94f5e7…), writes nothing and exits 1;
  - the same check on `reports/motco-adni-2026-10-28.md` names the absent sections 'Export sensitivity' and 'Stage-definition sensitivity';
  - in a scratch worktree of c94f5e7, the 2026-10-29 report passes its own check with no mismatch. Remove the worktree afterwards.
  - Done 2026-10-29: the 2026-10-29 report stops with absent 'Stage-definition sensitivity', extra none, and the `git log` command (c94f5e7); the 2026-10-28 report with absent 'Export sensitivity', 'Stage-definition sensitivity' (36c9cc8); both exit 1, print no `[report]` progress line (no input read) and leave `reports/` unchanged. At c94f5e7 the 2026-10-29 report checks: 58 tables, 2850 cells, 560 other lines, no mismatch. Worktree removed.
- [x] 4.2 Run failure checks of the check, each on a copy of the scratch report or of the scratch results root:
  - (a) one p-value of the arm row of "Statistics: primary and arm" changed by hand → the section, the table, the row, the column and both values; exit 1;
  - (b) one word of an arm status line changed → the section and the line, with both texts;
  - (c) one count in "cn_lmci_ad: Covariate levels" changed → the table, the row (a repeated key gets `#k`), the column and both values;
  - (d) in a copy of the results root, the arm's `stage_sensitivity.md` edited and its manifest's `outputs` hash updated to match → the provenance cells of both files, with both hashes;
  - (e) `report --check` on unchanged inputs → no mismatch, exit 0;
  - (f) every check run leaves the report and the results root unchanged (hashes before and after).

  Record the printed messages in this line.
  - Done 2026-10-29 (scratch `checks/check_failures.py`): (a) `Stage-definition sensitivity › table "Statistics: primary and arm" › row delta cn_lmci_ad › p (RRPP): report '0.189', generated '0.188'`, exit 1; (b) `Stage-definition sensitivity › line 1076: report "- `shape`: same … the arm's is less informative …", generated "… no more informative …"`, exit 1; (c) `… table "cn_lmci_ad: Covariate levels" › row `apoe4` #2 › arm: report '414', generated '413'`, exit 1; (d) three provenance cells, `Inputs` › `stage_sensitivity.md` sha256 and bytes and › `stage_sensitivity_manifest.json` sha256, each with both values, exit 1; (e) 71 tables, 3546 cells and 680 other lines compared, no mismatch, exit 0; (f) every run left the report and the results root unchanged.
- [x] 4.3 Update the docs for the check:
  - `README.md` and `AGENTS.md`, the earlier-layout gate: two earlier reports, `reports/motco-adni-2026-10-28.md` (ten sections, checks at 36c9cc8) and `reports/motco-adni-2026-10-29.md` (eleven sections, checks at c94f5e7).

  Verify with `grep` that both reports and both revisions are named.
  - Done 2026-10-29: both files name both reports with their section counts and 36c9cc8 and c94f5e7.

## 5. The report and commit hygiene

- [x] 5.1 Commit the implementation, the docs and the change's artifacts. Verify that `git status` is clean and that no file under `results/` or `reports/` changed.
  - Done 2026-10-29: the implementing commit on branch `adni-report-stage-arm` holds `cli.py`, `constants.py`, `data.py`, `README.md`, `AGENTS.md` and this change's artifacts; nothing under `results/` or `reports/`.
- [x] 5.2 Only once `date +%F` is later than 2026-10-29 (design D11), on the clean tree at the implementing commit:
  - run `uv run adni-sexdiff report` (no `--out`, so it is named by today's date), then `uv run adni-sexdiff report --check`;
  - verify the check passes and reads the new report as the newest;
  - verify that `grep -nE '\bRID\b|\brid\b'` over the new report hits only column-name mentions;
  - verify that `reports/motco-adni-2026-10-28.md` and `reports/motco-adni-2026-10-29.md` are byte-unchanged.

  Commit the new report alone, and record its name, sections, tables, cells and chain links in this line.
  - Done 2026-10-30 (nixos-office): on the clean tree at the implementing commit 6883869, `report` wrote `reports/motco-adni-2026-10-30.md` (12 sections, 71 tables, 3546 cells, parsed back equal; 100 chain links; 153526 bytes, sha256 `2cf39009…5122af9`). `report --check` without `--out` read it as the newest: 71 tables, 3546 cells and 680 other lines compared, no mismatch, exit 0. The grep hits 11 lines: the export bullet (sample column `rid`) and the ten `--sample-col rid` of the `cli_equivalent` commands. `reports/motco-adni-2026-10-28.md` and `reports/motco-adni-2026-10-29.md` are byte-unchanged. The step's findings are the five no-`numerics` manifests. The report is committed alone as 2e4a3e1.
- [x] 5.3 Check commit hygiene. Verify that:
  - `git status` is clean;
  - `git ls-files results` lists the same 76 files as `main`;
  - no file under `results/` changed in any commit of the branch;
  - over every file the branch adds or changes, the identifier grep finds only column names (`RID`, `rid`), never a participant value.
  - Done 2026-10-30: `git status` clean but for this record, committed with it; `git ls-files results` lists the same 76 files as `main`; no commit of the branch touches `results/`. The branch adds or changes eleven files (`AGENTS.md`, `README.md`, `cli.py`, `constants.py`, `data.py`, the change's five artifacts and the report). Over their added lines the grep hits 14 lines, each the name of the column: the ten `--sample-col rid`, the report's export bullet and the task lines that quote them. No hit is followed by a value.

## Workflow follow-up

- After the report is committed, archive the change on the branch. The archive syncs `openspec/specs/case-study-report/`, and `openspec validate --strict` must pass on the synced spec. Then push, open the PR and merge, following the PR workflow of the earlier changes.
- A regenerated results directory invalidates the committed report: `report --check` fails on its provenance cells until a new report is written and checked.
- The next changes are each their own proposal: the other export variants (all 245 NMR columns first) and the rank sweep. Each extends the report's sections and re-issues the report. The cluster run waits on the deploy key (constraint 7).
