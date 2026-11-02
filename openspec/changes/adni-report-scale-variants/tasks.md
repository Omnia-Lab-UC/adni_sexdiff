# Tasks

This change introduces no scientific constant. While this proposal was written, the user chose one group of shared tables for the three scale variants and the variant-name prefix for their titles (design D2). Before the apply starts, the user accepts the other presentation decisions:
- the group lead cites scale rule 8 through `_GROUP_PRIMARY_ONLY_RULE`, with a plural clause for a group of several variants and the membership group's clause byte-unchanged (design D3);
- the summary joins a group's ranks as a list, the two-variant text unchanged (design D4);
- the scale counts table takes the keys of the three entries, `n/a` where a variant's entry lacks a key (design D5);
- `SCALE_VARIANT_READING_RULES` is printed after `NMR_MEMBERSHIP_READING_RULES`, the fifth of seven lists (design D6);
- the preamble names this change (design D8).

Following the user's rule for the previous reports, the report is written on 2026-11-03 or later, named by the day it is written, and never over the 2026-11-02 file (design D10).

Every task runs on any machine with the Nix shell and the committed tree. The inputs are the tracked files under `results/`. No data root, data machine or participant-level file is needed, and the step records no numerics. Scratch copies and scratch outputs live in the session scratchpad, never under `results/` or `reports/`, except in task 4.2. No task line records a participant value.

## 1. The pin

- [x] 1.1 Set `REPORT_EXPORT_VARIANTS = ("nist_bridge", "per_run_standardized", "nmr_all_columns", "raw_scale", "log2_plus_one", "glog")` (design D1). Name this change in the module docstring and in the comments of `REPORT_EXPORT_VARIANTS` and `REPORT_INPUT_FILES`. Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(sum(len(v) for v in c.REPORT_INPUT_FILES.values()), len(c.REPORT_SECTIONS), c.REPORT_EXPORT_VARIANTS)"` prints `145 13` and the six variants;
  - per scale variant, each of its 13 new names, resolved against `EXPORT_SENSITIVITY_DIR`, is in `git ls-files results/motco_export_sensitivity/<variant>`, and the other 2 tracked files of the variant are its `stage_means.csv` and `pls_loadings.csv`.

  (Verified on 2026-11-02: `145 13` and the six variants; for each of `raw_scale`, `log2_plus_one` and `glog` its 13 names are among its 15 tracked files, and the other 2 are `pls_loadings.csv` and `stage_means.csv`.)
- [x] 1.2 Run `_load_report_inputs` on the committed tree. Verify that:
  - the provenance lists 145 files, each hash equal to `sha256sum`, and 99 aggregate files are checked against `outputs`;
  - the 45 manifests record the same MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8 (the export manifests record metabo_adni only), with numerics pinned in 40 and absent in the same five;
  - there are 255 chain links (189 + 66: per scale variant 4 export, 8 analysis, 6 comparison and 4 diagnostics), every one `ok`;
  - `run_report` prints no uncovered-variant line;
  - the step's own findings are still the five no-`numerics` manifests, with no dirty revision.

  Record the counts in this line. (Recorded on 2026-11-02 on the committed tree at 80307ed with the pin extended: 145 files, each hash equal to `sha256sum`; 99 checked against `outputs`, 1 against `bridge.table.sha256` and 45 hashed for the chain; 45 manifests, every recorded version equal (MOTCO 0.10.0, scikit-learn 1.8.0, metabo_adni 0.5.8; the export manifests, the three new ones among them, record metabo_adni 0.5.8 and no MOTCO or scikit-learn); numerics pinned in 40, absent in `clean p180`, `clean nmr`, `cohort`, `export` and `analyze`; 255 chain links, every one `ok`, the 22 per scale variant 4 export, 8 analysis, 6 comparison and 4 diagnostics; no uncovered-variant line (the `run_report` line is checked in 2.1); the step's findings the five no-`numerics` manifests, no dirty revision.)
- [x] 1.3 Copy the tracked `results/` files into a scratch root (`git ls-files results | xargs cp --parents -t <scratch>`; 175 files). Run each case below on its own edited copy (design D9). In every case the step must stop, naming the file or setting, both values where there are two, and the command to rerun. It must exit 1, create nothing under the scratch `reports/`, and leave the copy otherwise unchanged (every file hashed before and after). The cases:
  - (a) `motco_export_sensitivity/glog/comparison/export_sensitivity.csv` deleted → the file and `export-sensitivity --variant glog --force`.
  - (b) One byte of `raw_scale/comparison/export_sensitivity.md` changed → the file, both hashes, and `export-sensitivity --variant raw_scale --force`.
  - (c) The `log2_plus_one` directory replaced by `glog`'s outputs → the directory, the variant it expects and the variant its manifests record (identity, before the chain).
  - (d) `EXPORT_VARIANTS["glog"]["setting"]` patched in-process before the loader runs → the variant, `EXPORT_VARIANTS`, both values and `export-sensitivity --variant glog --force`.
  - (e) `raw_scale`'s `result.json` with `measurement.n_jobs` 4, and its manifest's recorded hash updated so the hash gate holds → that `result.json`, 4, and the `export-sensitivity` command without `--n-jobs`.
  - (f) `log2_plus_one`'s analysis manifest with `numerics.pinned` false → that manifest.
  - (g) `glog`'s export manifest's `reference.manifest.sha256` edited → that manifest, the key, both hashes and `export-sensitivity --variant glog --force`.
  - (h) `raw_scale`'s analysis manifest rewritten with a key reordered, and the comparison's record of it updated, as a `--force` rerun leaves them → the variant's diagnostics manifest, `inputs.analysis.analysis_manifest.sha256`, both hashes and its `axis-diagnostics` command.

  Record the eight outcomes in this line. (Recorded on 2026-11-02, each on its own copy of the 175 tracked files, `report` run with the defaults from the copy's root: every case exit 1, no `reports/`, every file unchanged. (a) `1 report input(s) absent`, the file, `export-sensitivity --variant glog --force`, then the variant's `axis-diagnostics`; (b) the file, its sha256 and the one its comparison manifest records, `export-sensitivity --variant raw_scale --force`, then the variant's `axis-diagnostics`; (c) `results/motco_export_sensitivity/log2_plus_one is not the variant 'log2_plus_one'`, its export manifest records `'glog'` (identity, before the chain), `--export-sensitivity-dir` or `export-sensitivity --variant log2_plus_one --force`; (d) the export manifest's recorded setting against `EXPORT_VARIANTS['glog']['setting']` `'patched setting'`, `export-sensitivity --variant glog --force`; (e) `raw_scale/analysis/result.json (measurement.n_jobs) records n_jobs = 4`, `export-sensitivity --variant raw_scale --force` without `--n-jobs`; (f) `log2_plus_one/analysis/analysis_manifest.json` records `numerics.pinned False`; (g) `glog/motco_input/manifest.json: reference.manifest.sha256`, both hashes, `export-sensitivity --variant glog --force`; (h) `raw_scale/diagnostics/diagnostics_manifest.json: inputs.analysis.analysis_manifest.sha256`, both hashes, and the variant's `axis-diagnostics` command with its three directories.)
- [x] 1.4 Update the docs for what group 1 changes:
  - `README.md`, the `report` section: 145 inputs and 45 manifests, the 13 files per scale variant, and 255 chain links (22 per scale variant);
  - `AGENTS.md`, step 6: 145 inputs, 45 manifests and 255 links (31, then 23, 22 and 22 for the first three variants, 22 for each scale variant, 24 and 67);
  - `AGENTS.md`, the Layout entry for `constants.py` (`REPORT_EXPORT_VARIANTS` with the six variants).

  Verify with `grep` that "106 committed files", "33 manifests" and "189 links" no longer describe the current step in `README.md`, `AGENTS.md` or `src/`. A comment that names the count before this change may remain. (Verified on 2026-11-02: none of the three appears in `README.md`, `AGENTS.md` or `src/`; the README's pin paragraph names the six variants and no longer says the scale variants are outside the pin; the `_REPORT_MANIFESTS` comment and the `run_report` docstring now say 45 manifests, 145 files and 255 links, and the one remaining "106" is the comment of `REPORT_INPUT_FILES` naming the count before this change.)

## 2. The renderer

- [x] 2.1 Add `"SCALE_VARIANT_READING_RULES": 8` to `_GROUP_PRIMARY_ONLY_RULE`. Give a group of several variants the clause "each variant is read against the primary only, never against another variant of the group ({cite} N)" (design D3). Update the docstrings of `_GROUP_PRIMARY_ONLY_RULE` and `_export_sensitivity_section`. Verify on the committed tree, writing to a scratch `--out`:
  - the level-2 headings equal `REPORT_SECTIONS` in order;
  - the section holds the run-handling and membership groups' tables equal to the 2026-11-02 report's, title, columns and rows;
  - it holds the scale group's tables:
    - `raw_scale, log2_plus_one, glog: Statistics: primary and variants` (12 rows: `delta primary`, `delta raw_scale`, `delta log2_plus_one`, `delta glog`, …);
    - `…: Latent space: primary and variants` (6 rows, 4 value columns);
    - `…: Run offset per export` (8 rows);
    - `…: Exports against the predeclared counts`;
    - `…: First component against phase` (4 rows);
  - every scale status is `same` and every primary row `the result`;
  - no table of the section holds variants of two groups;
  - the scale group's lead names `READING_RULES` and `SCALE_VARIANT_READING_RULES` and cites scale rules 1, 2 and 8, with the plural clause. Its `angle` and diagnostics paragraphs cite scale rules 3 and 7, and no scale-group line cites `variant rule`, `membership rule` or another rule set;
  - the membership group's lead is byte-equal to the 2026-11-02 report's.

  (Verified on 2026-11-02 with the scratch checker `check_report_scale_render.py` on a scratch `--out` named for 2026-11-03: the thirteen headings in order; the 24 tables of the run-handling and membership groups equal to the 2026-11-02 report's, title, columns and rows, in order; the scale group's 17 tables, the five shared ones with 12, 6, 8, 39 and 4 rows (the statistics rows `delta primary`, `delta raw_scale`, `delta log2_plus_one`, `delta glog`, …; the latent space with the columns `primary`, `raw_scale`, `log2_plus_one`, `glog`), then per variant its four diagnostics tables titled `<v>: …`; all nine scale statuses `same`, every primary row `the result`; none of the section's 41 tables names variants of two groups, and every scale table names scale variants only; the scale lead names `READING_RULES` and `SCALE_VARIANT_READING_RULES` and cites scale rules 1, 2 and 8 with the plural clause; its three `angle` paragraphs cite scale rule 3 and its diagnostics paragraph scale rule 7, and no scale-group line cites `variant rule`, `membership rule`, `sweep rule`, `arm rule` or another rule set's constant; the membership lead byte-equal. The counts table: 39 keys, the two `scale.median_below_offset.*` rows 46 / 129 for `log2_plus_one` and `n/a` for the others, no row all `n/a`.)
- [x] 2.2 Join the summary's ranks with `_and_join` (design D4), and add this change to the preamble's change list (design D8). Update the docstring of `render_report`. Verify that:
  - the summary's run-handling and membership paragraphs and their bullets equal the 2026-11-02 report's;
  - the scale paragraph reads "selected ranks 7 (`raw_scale`), 8 (`log2_plus_one`) and 7 (`glog`)", names `differs (scale dependence)`, `SCALE_VARIANT_READING_RULES` and section 8, and is followed by the three variants' rank lines and status bullets;
  - the reading-rules section holds seven numbered lists, the fifth `SCALE_VARIANT_READING_RULES` with eight items, led by the line the variants' `export_sensitivity.md` prints;
  - findings, provenance and reproduction carry the three variants by iteration:
    - their twelve manifests under "Findings", with the rank findings of `raw_scale` and `glog` and "None." where a manifest records none;
    - their three `axis-diagnostics` commands;
    - 15 `cli_equivalent`s;
  - the renderer holds no literal section number.

  Record the sections, tables and cells generated, and the report's size. (Recorded on 2026-11-02 on the same scratch `--out`: the summary's run-handling and membership paragraphs and the lines up to the scale paragraph equal to the 2026-11-02 report's; the scale paragraph with "selected ranks 7 (`raw_scale`), 8 (`log2_plus_one`) and 7 (`glog`)", `differs (scale dependence)`, `SCALE_VARIANT_READING_RULES` and section 8, then `` `raw_scale` (rank 7): ``, `` `log2_plus_one` (rank 8): `` and `` `glog` (rank 7): `` with nine status bullets; seven lists in order, each string-equal to its constant (9, 9, 7, 8, 8, 8, 8 items), the fifth `SCALE_VARIANT_READING_RULES` led by the line of the variants' `export_sensitivity.md`; the twelve scale manifests under "Findings", the rank finding once under each of the analysis and comparison manifests of `raw_scale` and `glog`, "None." under the three export manifests and `log2_plus_one`'s analysis and comparison manifests; the three scale `axis-diagnostics` commands and 15 `motco analyze` commands in the reproduction; no literal section number in the renderer. 13 sections, 106 tables, 7182 cells, 323809 bytes.)
- [x] 2.3 Write the scratch diff checker `check_report_scale_diff.py` (design D7). It parses the 2026-11-02 report and the scratch report with `parse_report`. It must report:
  - every 2026-11-02 table present with equal title, columns and rows, except the four provenance tables, whose old rows must be equal and in order;
  - every 2026-11-02 non-table line present in order, except the title line, the preamble, the summary's diagnostics paragraph, the export-sensitivity section lead and the lead of the CLI equivalents.

  Record the changed lines and the tables that gained rows in this line. Any other difference is a defect to fix before going on. (Recorded on 2026-11-02: 89 tables and 929 other lines of the 2026-11-02 report compared, 0 defects. The changed lines are exactly five: the title line (line 1), the preamble (line 3, now naming `adni-report-scale-variants` and the scale group's rule set), the summary's diagnostics paragraph (line 55, with the three variants' flagged components), the export-sensitivity section lead (line 975, now naming three groups) and the lead of the CLI equivalents (line 2012, 12 → 15 analyses). The tables that gained rows, their old rows equal and in order: "Versions per step" 33 → 45, "Revisions and numerics per step" 33 → 45, "Inputs" 106 → 145, "Chain links checked" 189 → 255.)
- [x] 2.4 Write the scratch value checker `check_report_scale_values.py` (design D9). It reads the scratch report's scale-group tables and, independently, the source files with `json`, `csv` and `hashlib`. It must report zero differences, compared at the printed digits, for:
  - the statistics rows against each variant's `export_sensitivity.csv`, and each rank against `latent.selected_lv`;
  - the latent space against the CSVs and the four `config_spectrum`s;
  - the run offsets and counts against the primary and the three variant export manifests (`counts`, `expected`);
  - each variant's diagnostics tables against its CSVs;
  - the 39 new input hashes against `hashlib` and the recording manifests.

  It must also verify string equality, per scale variant:
  - its status bullets, every "Export variant" bullet, and the primary's and its own column of the latent-space table equal their lines in its committed `comparison/export_sensitivity.md`;
  - its rules' lead line equals that document's;
  - the seven rule lists equal the constants, item by item.

  It lists every line that names two scale variants, or a scale variant together with another sensitivity, and verifies that each is a listing (design D9). An audit hook (`sys.addaudithook`) over `run_report` must list 145 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git. Record the counts compared in this line. (Recorded on 2026-11-02 on the scratch report: 1011 comparisons, 0 differences: 180 statistics cells (each against `export_sensitivity.csv` and the record, the statuses against the comparison manifests), 36 latent-space cells (the ranks against `latent.selected_lv`, the eigengaps and nulls against `config_spectrum`), 64 run-offset cells, 234 counts cells (the 39 keys equal to the manifests' `expected` keys, in the order of `EXPORT_VARIANT_EXPECTED_COUNTS`), 362 diagnostics cells (the four tables per variant against its CSVs, the export and diagnostics manifests, and the shared first-component table), 66 hash checks of the 39 new inputs (`hashlib` and the recording manifest), and 69 string checks: per variant its status bullets, its "Export variant" bullets, the primary's and its own latent-space columns and its rules' lead line equal to its `export_sensitivity.md`, and the seven rule lists equal to the constants item by item. The lines naming two scale variants, or one with another sensitivity, are 15, each a listing: the preamble, the summary's scale paragraph and diagnostics paragraph, the export section lead, the scale group lead, the five shared table titles and two shared table headers, scale rule 4 (a constant, verbatim) and the lead of the CLI equivalents; none compares two analyses. The audit hook lists 145 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git.)
- [x] 2.5 Verify determinism and the identifier rule:
  - two `--force` runs to the same scratch `--out` have equal sha256;
  - a run to a file named with another date differs only in the title line;
  - `grep -nE '\bRID\b|\brid\b'` over the scratch report hits only column-name mentions.

  Record the hash and the hits in this line. (Recorded on 2026-11-02: two `--force` runs to a scratch `motco-adni-2026-11-03.md` and the earlier scratch render have sha256 `57f1d2b477cab29072a5992fea40761f98d64d89f4fb4155637224564d5f22c1`; a run to `motco-adni-2026-12-31.md` differs in line 1 only; the grep hits 31 lines, each a column name: the export bullet (sample column `rid`) and 30 `--sample-col rid` in the 15 `motco analyze` commands, printed in their sections and in the reproduction.)
- [x] 2.6 Update the docs for what group 2 changes:
  - `README.md`: the status sentence that says a later report change adds the scale variants, and the `report` section (the scale group, its title prefix, scale rule 8 in its lead, seven rule lists);
  - `AGENTS.md`, the status paragraph: the report covers the scale variants, the pin holds the six variants, and the newest report's coverage;
  - `AGENTS.md`, step 6: the third group, the seven rule lists, and the scale group's lead citing scale rule 8 through `_GROUP_PRIMARY_ONLY_RULE`;
  - `AGENTS.md`, the Layout entry for `data.py`.

  Leave "Flag and ask" unchanged. Verify with `grep` that "registered outside the report's pin", "a later report change" and "not yet in the report" no longer describe the scale variants. (Verified on 2026-11-02: none of the three describes the scale variants in `README.md`, `AGENTS.md` or `src/`; the one remaining "a later report change" is the `adni-nist-bridge` decision record under "Flag and ask", and "the report left to a later change" the `adni-scale-variants` one, both records of what the user chose then. No "six rule lists" remains.)

## 3. The checker

- [x] 3.1 Verify the existing variant gate under the new pin (design D9; `_check_report_layout` needs no code change). Verify:
  - `uv run adni-sexdiff report --check --out reports/motco-adni-2026-11-02.md` stops before any input gate. It names the report, the absent variants 'raw_scale', 'log2_plus_one' and 'glog', no extra variant and `git log -1 --format=%H -- reports/motco-adni-2026-11-02.md` (28e0d48…), writes nothing and exits 1;
  - the 2026-10-31 report stops there too, with the absent variants 'nmr_all_columns', 'raw_scale', 'log2_plus_one' and 'glog';
  - the 2026-10-30, 2026-10-29 and 2026-10-28 reports stop on their sections, with the messages `main`'s `_check_report_layout` gives;
  - a scratch copy of the scratch report with two scale ``Export variant `…` `` blocks swapped stops naming no absent and no extra variant and that the order differs;
  - in a scratch worktree of 28e0d48, the 2026-11-02 report passes its own check with no mismatch. Remove the worktree afterwards;
  - with a scratch copy of `src/` whose pin holds the first three variants, `report` on the committed tree reads 106 files, prints one uncovered-variant line per scale variant, and no line of its body names a scale variant.

  Update the docstring of `_check_report_layout` (the 2026-11-02 report as an earlier layout). Record the outcomes in this line. (Recorded on 2026-11-02: the 2026-11-02 report stops with "its export variants are not REPORT_EXPORT_VARIANTS (absent: 'raw_scale', 'log2_plus_one', 'glog'; extra: none)" and the `git log -1 --format=%H -- reports/motco-adni-2026-11-02.md` command (28e0d48a7fb0…), exit 1; the 2026-10-31 report with absent 'nmr_all_columns', 'raw_scale', 'log2_plus_one', 'glog', exit 1; the 2026-10-30, 2026-10-29 and 2026-10-28 reports stop on their sections with messages equal to those of `main`'s code (bf3f773, run from a scratch worktree); the five reports byte-unchanged and nothing written. The scratch report with the `raw_scale` and `glog` blocks swapped stops with "absent: none; extra: none; the order differs", exit 1. In a scratch worktree of 28e0d48 the 2026-11-02 report passes its own check (89 tables, 5418 cells and 929 other lines, no mismatch, exit 0); both worktrees removed. With a scratch `src/` whose pin holds the first three variants, `report` reads 106 files (33 manifests), prints one uncovered-variant line for each of `raw_scale`, `log2_plus_one` and `glog`, and no line of its body names a scale variant; its body differs from the 2026-11-02 report in the title line and the preamble's change list only.)
- [x] 3.2 Run failure checks of the check, each on a copy of the scratch report or of the scratch results root:
  - (a) one p-value of the `delta glog` row changed by hand → the section, the table, the row, the column and both values; exit 1;
  - (b) one word of `raw_scale`'s `angle` status line changed → the section and the line, with both texts;
  - (c) in a copy of the results root, `log2_plus_one`'s `export_sensitivity.md` edited and its manifest's `outputs` hash updated to match → the provenance cells of both files, with both hashes;
  - (d) `report --check` on unchanged inputs → no mismatch, exit 0;
  - (e) every check run leaves the report and the results root unchanged (hashes before and after).

  Record the printed messages in this line. (Recorded on 2026-11-02 with the scratch script `check_failures.py`: (a) `Export sensitivity › table "raw_scale, log2_plus_one, glog: Statistics: primary and variants" › row delta glog › p (RRPP): report '0.9999', generated '0.2127'`, 1 mismatch, exit 1; (b) `Export sensitivity › line 1568: report "- `angle`: same (primary not rejected, raw_scale not rejected). … no less informative …", generated "… no more informative …"` (the copy in section 8; the summary prints the same line), 1 mismatch, exit 1; (c) on a copy of the 175 tracked files, `Provenance › table "Inputs"` › the row of `log2_plus_one/comparison/export_sensitivity.md` › sha256 and bytes, and the row of its `export_sensitivity_manifest.json` › sha256, each with both values (the manifest's bytes unchanged, one 64-character hash replacing another), 3 mismatches, exit 1; (d) `106 tables, 7182 cells and 1194 other lines compared; no mismatch; nothing was written`, exit 0; (e) every run left the report copy and the results root byte-unchanged and wrote nothing beside the report.)
- [x] 3.3 Update the docs for the check:
  - `README.md` and `AGENTS.md`, the earlier-layout gate: five earlier reports:
    - `reports/motco-adni-2026-10-28.md` (ten sections, 36c9cc8);
    - `reports/motco-adni-2026-10-29.md` (eleven, c94f5e7);
    - `reports/motco-adni-2026-10-30.md` (twelve, 2e4a3e1);
    - `reports/motco-adni-2026-10-31.md` (two export variants, 13ce7c8);
    - `reports/motco-adni-2026-11-02.md` (three export variants, 28e0d48);
  - the docstrings of `check_report` and `run_report`.

  Verify with `grep` that the five reports and the five revisions are named in both files. (Verified on 2026-11-02: each of the five report names and each of 36c9cc8, c94f5e7, 2e4a3e1, 13ce7c8 and 28e0d48 appears in `README.md` and in `AGENTS.md`; the `check_report` docstring names the five reports and the `run_report` docstring the 2026-11-02 report at 28e0d48.)

## 4. The report and commit hygiene

- [x] 4.1 Commit the implementation, the docs and the change's artifacts on the branch `adni-report-scale-variants`, created from `main` (bf3f773). Verify that `git status` is clean and that no file under `results/` or `reports/` changed. (Committed on 2026-11-02 on `adni-report-scale-variants`, from bf3f773 after the proposal commit 80307ed; `git status` clean after it; the commit touches `src/adni_sexdiff/constants.py`, `src/adni_sexdiff/data.py`, `README.md`, `AGENTS.md` and the change's `tasks.md` only, and `git diff --name-only main..HEAD -- results reports` is empty.)
- [ ] 4.2 Only once `date +%F` is later than 2026-11-02 (design D10), on the clean tree at the implementing commit:
  - run `uv run adni-sexdiff report` (no `--out`, so it is named by today's date), then `uv run adni-sexdiff report --check`;
  - verify the check passes and reads the new report as the newest;
  - verify that the new report equals the scratch render of 2.5 apart from its title line;
  - verify that `grep -nE '\bRID\b|\brid\b'` over the new report hits only column-name mentions;
  - verify that the five earlier reports are byte-unchanged.

  Commit the new report alone, and record its name, sections, tables, cells, chain links and size in this line.
- [ ] 4.3 Check commit hygiene. Verify that:
  - `git status` is clean;
  - `git ls-files results` lists the same 175 files as `main`;
  - no file under `results/` changed in any commit of the branch;
  - over every file the branch adds or changes, the identifier grep finds only column names (`RID`, `rid`), never a participant value.

  Record the files the branch adds or changes in this line.

## Workflow follow-up

- After the report is committed, archive the change on the branch. The archive syncs `openspec/specs/case-study-report/`, and `openspec validate --strict` must pass on the synced spec. Then push, open the PR and merge, following the PR workflow of the earlier changes.
- A regenerated results directory invalidates the committed report: `report --check` fails on its provenance cells until a new report is written and checked.
- With this change every predeclared sensitivity is in the report. No further sensitivity is registered; a new one needs its own proposal with its constants. The cluster run waits on the deploy key (constraint 7).
