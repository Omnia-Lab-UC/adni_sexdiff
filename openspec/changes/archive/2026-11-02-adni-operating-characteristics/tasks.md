# Tasks

This change introduces two scientific constants, `OPERATING_CHARACTERISTICS_READING_RULES` and `OPERATING_CHARACTERISTICS_SOURCE` (proposal, What Changes). While this proposal was written, the user chose to confirm the predeclared rules beside them rather than rewrite them (option A, design D1), and to extend reading rule 3 to `delta` (measurement rule 4).

Before the apply starts, the user accepts:
- the wording of the nine measurement rules (proposal);
- the source pin, MOTCO `0d726922…` and sha256 `4cb482e7…` (design D2);
- the copy at `references/motco_adni_design/adni_design_decision.json` (design D3);
- the reference gate and its decimals (design D4);
- the seventh section and its tables (design D5);
- the summary paragraph, preamble, provenance row, eighth rule list and reproduction line (design D6).

Every task runs on any machine with the Nix shell and the committed tree, plus a MOTCO clone at `../MOTCO` for task 1.2 only. The inputs are the tracked files under `results/` and `references/`. No data root, data machine or participant-level file is needed, the step makes no MOTCO call, and it records no numerics. Scratch copies and outputs live in the session scratchpad, never under `results/`, `references/` or `reports/`, except in tasks 1.2 and 5.2. No task line records a participant value.

## 1. The constants and the copy

- [x] 1.1 Add the operating-characteristics block to `constants.py` after the rank sweep's (design D2):
  - `OPERATING_CHARACTERISTICS_READING_RULES`, the nine rules of the proposal verbatim;
  - `OPERATING_CHARACTERISTICS_SOURCE`, with `repository`, `change`, `pull_request`, `commit`, `path`, `report`, `sha256` and `verdict` as in the proposal;
  - `OPERATING_CHARACTERISTICS_DIR` and `OPERATING_CHARACTERISTICS_DECISION`;
  - two import-time assertions tying rule 1 to the commit's first seven characters and to the verdict;
  - the comment that names the change, its date and that it was decided after every run here;
  - the module docstring's list of decided constants.

  Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(len(c.OPERATING_CHARACTERISTICS_READING_RULES), c.OPERATING_CHARACTERISTICS_SOURCE['commit'][:7], c.OPERATING_CHARACTERISTICS_SOURCE['verdict'])"` prints `9 0d72692 non_rejections_uninformative`;
  - each rule is string-equal to the proposal's (a script reading both);
  - in a scratch copy of `src/`, a rule 1 without `0d72692` fails the import naming both constants.

  (Verified on 2026-11-02: the command prints `9 0d72692 non_rejections_uninformative`; a script reading the proposal's nine rules, rule 6's sub-bullets and closing sentence joined with single spaces as the constant stores them (a rule is one string), finds each string-equal to the constant; in a scratch copy of `src/` with rule 1's commit set to `0000000`, the import fails with `AssertionError: OPERATING_CHARACTERISTICS_READING_RULES rule 1 must name the commit of OPERATING_CHARACTERISTICS_SOURCE (0d72692)`.)
- [x] 1.2 Write the copy: `git -C ../MOTCO show 0d726922173188c4d74ce4b2f87f6a26e5fc548f:results/adni-design-2026-11-02/run/adni_design_decision.json > references/motco_adni_design/adni_design_decision.json` (design D3). Verify:
  - its sha256 equals `OPERATING_CHARACTERISTICS_SOURCE["sha256"]` and it is 76,057 bytes;
  - it holds no `RID`, `PTID` or participant-level column (it is MOTCO's synthetic run);
  - each number rules 3 to 6 quote equals the file at the rule's digits, with a script listing every one: 0.076, 0.062, 0.530 and their R; 0.683 (the magnitude e = 1 cell's `cv_mean_auroc_mean`) beside `adni_reference.cv_mean_auroc`; 0.034 to 0.068 and 0.0695; 0.606, 0.578, 1.126, 0.994, 19 in 494 of 500, 0.330 and 51.0 from `calibration_realized`; 0.542, 1.12, 0.73, 8, 0.744 and 35.4 from `adni_reference`.

  The block sizes and shares of rule 6 (367 / 131, 74 % / 26 %) come from MOTCO's report at the pinned commit. Check them against `git -C ../MOTCO show 0d72692:docs/reports/adni-design-2026-11-02.md`. Record the outcome in this line. (Verified on 2026-11-02: the copy hashes to `4cb482e7e16b19278467d6929f6905d71a8aef332ae55fc07ac86a3c1eec3ea1`, the constant's sha256, and is 76,057 bytes; `grep -E '\bRID\b|PTID|[0-9]{3}_S_[0-9]{4}'` finds nothing and no key of the file names a participant, a subject or an ID; a script lists 31 quoted values of rules 3 to 6 beside the file's, each equal at the rule's digits: 0.076, 0.062, 0.530, R 500 in every power and size cell, e = 1 the construction maximum, 0.683 in the magnitude e = 1 cells' `cv_mean_auroc_mean`, 0.600 from `adni_reference.cv_mean_auroc` 0.5995, 0.034 to 0.068 and 0.0695, `delta` 0.034 at both controls, 0.606, 0.578, 1.126, 0.994, 19 in 494 of 500 (`max_components` 20, so 19 the cap), 0.330 and 51.0 from `calibration_realized`, 0.542, 1.12, 0.73, 8, 0.744 and 35.4 from `adni_reference`, 999 permutations from `construction`, 165 and 133 from `adni_reference.phase_offset`. MOTCO's report at 0d72692 states 367 methylation and 131 expression features and the shares 74 / 26 % (lines 187-188); 165 / 298 and 133 / 298 round to 55 % / 45 %, and `ANALYSIS_PERMUTATIONS` is 9999.)
- [x] 1.3 Update the constraint docs for the constants and the copy (design D9):
  - `AGENTS.md` constraint 1: the copy among the committed aggregate files;
  - constraint 5 and "Flag and ask": the two constants with their values in short, decided by `adni-operating-characteristics` after every run, read beside `READING_RULES`;
  - Layout: `references/` and the constants block.

  Verify with `grep -n "OPERATING_CHARACTERISTICS\|references/" AGENTS.md`, which shows every entry. (Verified on 2026-11-02: the grep shows constraint 1 (the copy, line 675), constraint 5 (the two constants as the one exception to "before any run", lines 779-780), the `constants.py` Layout entry (the block and its two conventions, lines 902-906), the Layout entry `references/` (line 1040), the "Flag and ask" list (lines 1221-1222) and its bullet with the source and the nine rules in short (line 1639 on).)

## 2. Inputs and gates

- [x] 2.1 Add the role `operating-characteristics` to `REPORT_INPUT_FILES`, and wire the directory through:
  - `_report_dirs` (the tenth directory);
  - `_load_report_inputs` and `run_report`: `operating_characteristics_dir`;
  - `cli.py`: `--operating-characteristics-dir`, default `OPERATING_CHARACTERISTICS_DIR`;
  - `_report_rerun`: the `git show` copy command at the pinned commit (design D4).

  Verify:
  - the constants print `146` input files and `14` sections once group 3 lands (`146 13` until then);
  - `uv run adni-sexdiff report --help` lists thirteen options besides `--help`.

  (Verified on 2026-11-02: the constants print `146 13` before group 3; `report --help` lists 13 options besides `-h, --help`: the ten directories (`--operating-characteristics-dir` the tenth, default `references/motco_adni_design`), `--out`, `--check` and `--force`. `_report_rerun` gives the role `git -C <MOTCO clone> show 0d726922173188c4d74ce4b2f87f6a26e5fc548f:results/adni-design-2026-11-02/run/adni_design_decision.json > <dir>/adni_design_decision.json`.)
- [x] 2.2 Handle the copy in gate 2 before the bridge-table branch: its sha256 against `OPERATING_CHARACTERISTICS_SOURCE["sha256"]`, a provenance row recorded in `` `OPERATING_CHARACTERISTICS_SOURCE`: sha256 (MOTCO 0d72692) ``, and its own progress line (design D4). Verify on the committed tree:
  - 146 files hashed;
  - 99 checked against `outputs`, 1 against `bridge.table.sha256`, 1 against the constant, 45 manifests hashed for the chain;
  - 255 chain links, every one `ok`;
  - the step's findings still the five no-`numerics` manifests.

  (Verified on 2026-11-02 on the committed tree: 146 files hashed under 46 directories, each hash equal to the sha256 of its bytes; 99 checked against `outputs`, 1 against `bridge.table.sha256`, 1 (the copy) against the constant, its provenance row recorded in `` `OPERATING_CHARACTERISTICS_SOURCE`: sha256 (MOTCO 0d72692) ``, 45 manifests hashed for the chain; the progress line `cited measurement: references/motco_adni_design/adni_design_decision.json hashes to the sha256 OPERATING_CHARACTERISTICS_SOURCE pins (MOTCO change adni-design-operating-characteristics, pull request 71, commit 0d72692)`; 255 chain links, every one `ok`; the step's findings the five no-`numerics` manifests.)
- [x] 2.3 Add gate 6 after the chain (design D4):
  - `verdict` and `indicative`;
  - the key set of `adni_reference` against `_OPERATING_CHARACTERISTICS_REFERENCE`;
  - each value against its committed source at the map's decimals.

  `_load_report_inputs` returns the parsed decision as `inputs["decision"]`, with the reference rows (key, recorded value, committed source) for the construction table. Verify on the committed tree that every key holds and the progress line names the count of values compared. Record the count in this line. (Verified on 2026-11-02 on the committed tree: every key holds; the progress line reads `cited measurement: verdict `non_rejections_uninformative`, not indicative; adni_reference: 19 values, each equal to its committed source at the decision's digits (the AUROC range over 9 CV-selected analyses)`. The 19: `selected_lv` 8; `cv_mean_auroc` 0.5995; the range [0.58, 0.616] over the primary, the latent arm, the six export variants and the CN / LMCI / AD arm; |`spearman`| of `pls_0` · `phase` 0.542; eigengap 0.744; `angle` null q95 35.44; per block the median \|d\|, \|d\| > 1, PC1 correlation and kept features (p180 1.12 / 80 / 0.73 / 133, NMR 0.21 / 0 / 0.13 / 165); the six design columns; `phase[ADNI2GO]` 0.5443; the p-values 0.1116, 0.6879 and 0.7105.)
- [x] 2.4 Copy the tracked `results/` and `references/` files into a scratch root (`git ls-files results references | xargs cp --parents -t <scratch>`). Run each case on its own copy. In every case the step must stop naming the file or key, both values where there are two, and what to do. It must exit 1, create nothing under the scratch `reports/`, and leave every file unchanged (hashed before and after). The cases:
  - (a) the copy deleted → the file and the `git show` command;
  - (b) one byte of the copy changed → the copy, both hashes and the `git show` command;
  - (c) `OPERATING_CHARACTERISTICS_SOURCE["verdict"]` patched in-process → `verdict`, both values;
  - (d) the copy's `adni_reference.selected_lv` set to 7 and the constant's sha256 patched in-process to the edited copy's → `adni_reference.selected_lv`, 7 and 8, `result.json`, and that citing a measurement for this analysis is a new change;
  - (e) a key `extra` added to the copy's `adni_reference` (sha256 patched likewise) → the key set, with `extra` named as extra;
  - (f) the copy's `adni_reference.phase_offset.p180.median_abs_d` set to 1.13 (sha256 patched likewise) → the key, 1.13 against 1.12, the export manifest.

  Then run on an unedited copy with `--operating-characteristics-dir` pointing to a second scratch directory holding the copy. The step passes every gate. Record the seven outcomes in this line. (Recorded on 2026-11-02, each case on its own scratch root of the 175 tracked `results/` files and the copy (not yet tracked, so copied by name), `report` run from the root with the defaults: every case exit 1, no `reports/`, every file unchanged (all hashed before and after). (a) `1 report input(s) absent: references/motco_adni_design/adni_design_decision.json`, with the `git -C <MOTCO clone> show 0d726922…:results/adni-design-2026-11-02/run/adni_design_decision.json > references/motco_adni_design/adni_design_decision.json` command; (b) the copy, its sha256 `d0b88caf…` and the pinned `4cb482e7…` (MOTCO commit 0d72692), `the copy is not the cited measurement`, the same command; (c) `records verdict 'non_rejections_uninformative', but OPERATING_CHARACTERISTICS_SOURCE cites 'power_statement'`; (d) `adni_reference.selected_lv records 7, but the committed value is 8 (`latent.selected_lv` of `results/motco_analysis/result.json`)` and that citing a measurement for this analysis is a new change; (e) the keys of `adni_reference` against `_OPERATING_CHARACTERISTICS_REFERENCE`: absent none, extra `'extra'`; (f) `adni_reference.phase_offset.p180.median_abs_d records 1.13, but the committed value is 1.12 (`counts.phase_offset.p180.median_abs_d` of `results/motco_input/manifest.json`, at 2 decimals)`. Then, on a root without `references/` and the unedited copy in a second scratch directory named by `--operating-characteristics-dir`, the step passed every gate (the copy's hash, 255 links, the 19 reference values) and exit 0.)
- [x] 2.5 Update the docs for group 2:
  - `AGENTS.md` step 6: 146 inputs with the copy, gate 6 with its map, thirteen flags;
  - `AGENTS.md` Layout: the CLI entry for `report`;
  - `README.md`: the `report` section's inputs and flags;
  - the docstrings of `_load_report_inputs` (gate 6 and the return) and `run_report`, and the `report` CLI help.

  Verify with `grep -n "146\|operating-characteristics-dir" AGENTS.md README.md src/adni_sexdiff/cli.py`. (Verified on 2026-11-02: the grep shows step 6's 146 files and its flag (`AGENTS.md` lines 492 and 527), the Layout entry of `cli.py` (line 847), the README's usage line, default and inputs (lines 1380, 1399 and 1429) and the flag in `cli.py` (line 300). Step 6 and the README also name the copy among the inputs, its hash gate before the bridge table and gate 6 with the map and its 19 values; the docstrings of `_load_report_inputs` (parameters, gate 2's copy, gate 6, `decision` and `decision_reference`) and `run_report` (the parameter, 146 inputs, both gates) and the `report` CLI help name the copy. No "145" or "twelve flags" describes the current step any more; the remaining "145" are a stage-arm count and the `REPORT_INPUT_FILES` comment naming the count before this change.)

## 3. Rendering

- [x] 3.1 Add "Operating characteristics" to `REPORT_SECTIONS` after "Axis diagnostics of the primary". Render the section of design D5:
  - the lead;
  - the tables "Cited measurement", "Decision rule", "Size at this design" with the size sentence, "Power at this design" and "Power floor per statistic";
  - the three statements;
  - "Construction beside this design".

  Verify on a scratch report of the committed tree:
  - fourteen level-2 headings in `REPORT_SECTIONS` order;
  - the section's tables are 6 size rows, 12 power rows and 3 floor rows;
  - parse-back equal to the generated tables.

  (Verified on 2026-11-02 on a scratch report of the committed tree, `report --out <scratch>/reports/motco-adni-2026-11-02-3.md`: fourteen level-2 headings equal to `REPORT_SECTIONS` in order, "Operating characteristics" the seventh; its tables "Cited measurement" (13 rows), "Decision rule" (the 9 keys of `rule` in the file's order), "Size at this design" (6 rows), "Power at this design" (12 rows), "Power floor per statistic" (3 rows) and "Construction beside this design" (10 paired rows and the 9 reference keys without a counterpart); the size sentence after the size table and the three statements under "Statements per statistic"; parse-back equal: 112 tables, 7501 cells.)
- [x] 3.2 Render the rest of design D6:
  - the summary paragraph after the primary's reading bullets;
  - the preamble's change list and reading clause;
  - the provenance row;
  - `OPERATING_CHARACTERISTICS_READING_RULES` after `READING_RULES` under its heading and lead line;
  - the reproduction paragraph with the `git show` line.

  Verify with a script on the scratch report:
  - the verdict, `size.sentence` and the three `statements` are string-equal to the file's, in the section and in the summary;
  - the eight rule lists are string-equal to their constants in order, the second being the nine measurement rules;
  - the primary's reading bullets are string-equal to the committed `results/motco_analysis/summary.md` lines.

  (Verified on 2026-11-02 by a script on the scratch report: the verdict is string-equal to the file's in the "Cited measurement" table and appears as `` verdict `non_rejections_uninformative`. `` in the summary paragraph; `size.sentence` is a line of the section; the three `statements` are bullets of the section and of the summary, in `delta`, `angle`, `shape` order, each string-equal to the file's; the reading-rules section holds eight lists string-equal to their constants in order (`READING_RULES` 9, `OPERATING_CHARACTERISTICS_READING_RULES` 9, `LATENT_SENSITIVITY_READING_RULES` 9, `EXPORT_VARIANT_READING_RULES` 7, `NMR_MEMBERSHIP_READING_RULES` 8, `SCALE_VARIANT_READING_RULES` 8, `STAGE_SENSITIVITY_READING_RULES` 8, `RANK_SENSITIVITY_READING_RULES` 8), the measurement list led by the line naming `adni-operating-characteristics`, after every run, no constant, record or status; the primary's three reading bullets are lines of the committed `results/motco_analysis/summary.md`, the clause "no power statement exists at this design" included. The preamble names the change and the reading clause, the provenance inputs table holds the copy's row, and the reproduction section ends with the paragraph and the `git show` line.)
- [x] 3.3 Compare the scratch report with `reports/motco-adni-2026-11-02-2.md`, parsed, by section title. Verify:
  - every table of the twelve shared sections is cell-equal, except the provenance inputs table, which gains the copy's row;
  - every other line is equal, except the title, the preamble, the summary's new paragraph, the section numbers of cross-references, the new section, the new rule list and the reproduction lines.

  Record the counts of tables, cells and differing lines in this line. (Recorded on 2026-11-02, the scratch report against `reports/motco-adni-2026-11-02-2.md`, parsed: the new report adds the section "Operating characteristics" and drops none; the 13 shared sections hold the same 106 tables (7182 cells on the old side), 104 cell-equal; the provenance "Inputs" table gains the copy's row (145 → 146 rows, no other cell differs), and one cell of "Primary analysis › Settings" (the `ANALYSIS_LATENT_ADJUSTMENT` note) differs only in its cross-reference, "section 7" → "section 8". Other lines: the title line and the preamble differ; 22 lines differ only in section numbers (Summary 8, Cohort 1, Primary analysis 1, Latent-adjustment sensitivity 1, Export sensitivity 7, Stage-definition sensitivity 2, Rank sensitivity 2); 26 lines are new: the summary's paragraph and its three bullets with 2 blank lines (6), the measurement rule list with its heading and lead (14), the reproduction paragraph and code block (6). No line of a sensitivity section names the measurement.)
- [x] 3.4 With a script, compare every cell of the section's tables with the decision file. Rates and standard errors at three decimals, the bound at four, construction values at six significant digits, reference values as recorded, and each "checked against" cell naming its source from the D4 map. Verify there is no mismatch and no cell the file does not hold. (Verified on 2026-11-02 by a script that rebuilds each cell from the copy: 251 cells compared, 0 mismatches. "Cited measurement" against the constant, the copy's path and sha256 and the file's verdict, indicative, units and settings hash; "Decision rule" the 9 keys of `rule` in order, each as recorded; "Size at this design" and "Power at this design" every key, effect, rejection and replicate count, rate and standard error at three decimals, bound at four, rank median and the `rank: count` pairs in rank order; "Power floor per statistic" each field; "Construction beside this design" each construction value at six significant digits from `calibration_realized`, each reference value as `adni_reference` records it, the compared decimals and the "checked against" cell naming the field and file of `_OPERATING_CHARACTERISTICS_REFERENCE`, and the 19 reference keys each once. Every cell is the file's or the constant's.)
- [x] 3.5 Run `report --force` twice to the same scratch `--out` and check the files are byte-identical. Verify:
  - `report --check --out <scratch report>` passes with no mismatch;
  - after one rate of "Power at this design" is edited by hand, `--check` names the section, the table, the row, the column and both values, and exits 1.

  (Verified on 2026-11-02: two `report --force` runs to `<scratch>/reports/motco-adni-2026-11-02-3.md` wrote byte-identical files (sha256 `d8b68ef6a30c2253…`); `report --check --out` on it compared 112 tables, 7501 cells and 1250 other lines, no mismatch, exit 0; a copy under the same name with the rate of `delta e = 1` edited from 0.530 to 0.531 gave `MISMATCH: Operating characteristics › table "Power at this design" › row delta e = 1 › rate: report '0.531', generated '0.530'`, one mismatch, exit 1, nothing written.)
- [x] 3.6 Update the docs for group 3:
  - the `render_report` docstring: fourteen sections, the section, the eight lists, the verbatim sentences;
  - `AGENTS.md` step 6: the section list and the eight rule lists in order;
  - `AGENTS.md` "Data & domain notes": one sentence that reading rule 3 is measured at this design for the primary only, `OPERATING_CHARACTERISTICS_READING_RULES`;
  - `README.md`: the report's sections.

  Verify with `grep -n "Operating characteristics" AGENTS.md README.md src/adni_sexdiff/data.py`. (Verified on 2026-11-02: the grep shows the "Data & domain notes" sentence (`AGENTS.md` line 1245), the README's summary entry (line 1554), and in `data.py` the section renderer's docstring, `render_report`'s docstring, the summary paragraph, the section call and the reproduction paragraph. Step 6 of `AGENTS.md` and the README list the fourteen sections, the operating-characteristics section's contents and the eight rule lists in order, `OPERATING_CHARACTERISTICS_READING_RULES` second; `render_report` and `run_report` describe the fourteen sections, the eight lists and the verbatim sentences; no "thirteen sections" or "seven rule lists" describes the current report in `src/`, and in the docs only the earlier-layout list of task 4.2 still says thirteen.)

## 4. The layout gate

- [x] 4.1 Update the `_check_report_layout` docstring for the 2026-11-02-2 report (thirteen sections, checks at 67567e2) (design D7). Verify that `report --check --out <report>` stops at the section gate, naming the report, its absent sections and its `git log -1 --format=%H -- <report>` command, exits 1 and writes nothing:
  - for `reports/motco-adni-2026-11-02-2.md` (absent "Operating characteristics"), `2026-11-02.md` and `2026-10-31.md` (the same);
  - for `2026-10-30.md`, `2026-10-29.md` and `2026-10-28.md` (their older absences added).

  Then:
  - a scratch fourteen-section report whose export section lists three variants stops at the variant gate, naming `raw_scale`, `log2_plus_one` and `glog`;
  - `git log -1 --format=%h -- reports/motco-adni-2026-11-02-2.md` prints `67567e2`, and `report --check --out reports/motco-adni-2026-11-02-2.md` passes in a worktree of 67567e2 (removed afterwards).

  (Verified on 2026-11-02: `report --check --out` on each committed report stopped at the section gate, before any input gate (no `inputs:` line), exit 1, `reports/` unchanged, naming the report, its absent sections and `git log -1 --format=%H -- <report>`: the 2026-11-02-2, 2026-11-02 and 2026-10-31 reports absent `'Operating characteristics'`, the 2026-10-30 report also `'Rank sensitivity'`, the 2026-10-29 report also `'Stage-definition sensitivity'`, the 2026-10-28 report also `'Export sensitivity'`, extra none in each. A scratch copy of the new report with its three scale variants' `Export variant` headings renamed (fourteen sections) stopped at the variant gate, `absent: 'raw_scale', 'log2_plus_one', 'glog'; extra: none`, exit 1, before any input gate. `git log -1 --format=%h -- reports/motco-adni-2026-11-02-2.md` prints `67567e2`; in a detached worktree of 67567e2, its own `src/` on `PYTHONPATH` with the locked environment, `report --check --out reports/motco-adni-2026-11-02-2.md` compared 106 tables, 7182 cells and 1194 other lines, no mismatch, exit 0; the worktree was removed and pruned. The docstrings of `_check_report_layout`, `check_report` and `run_report`'s `check` name the 2026-11-02-2 report at 67567e2.)
- [x] 4.2 Update the earlier-layout list in `AGENTS.md` step 6 and in `README.md`: the 2026-11-02-2 report at 67567e2, and the variant gate reached by no committed report. Verify with `grep -n "67567e2" AGENTS.md README.md`. (Verified on 2026-11-02: the grep shows `AGENTS.md` step 6 (line 673, the revisions 36c9cc8, c94f5e7, 2e4a3e1, 13ce7c8, 28e0d48 and 67567e2) and `README.md` (line 1712); both lists add `reports/motco-adni-2026-11-02-2.md` with thirteen sections, give the 2026-10-31 and 2026-11-02 reports their thirteen sections beside their variants, and say that since this change every committed report stops at the section gate and none reaches the variant gate.)

## 5. The report

- [x] 5.1 Commit the implementation: constants, `data.py`, `cli.py`, the copy, `AGENTS.md`, `README.md` and the change's artifacts with tasks 1.1 to 4.2 recorded. Verify that `git status --short` is empty afterwards and that `git diff --stat main -- results` is empty. (Verified on 2026-11-02: committed as 7a2d212, with the copy as the one added file (MOTCO's synthetic decision, aggregate); `git status --short` empty afterwards and `git diff --stat main -- results` empty.)
- [x] 5.2 On the clean tree at that commit, write the report under the day's next free name:
  - `uv run adni-sexdiff report --out reports/motco-adni-<date>[-<n>].md`, `motco-adni-2026-11-02-3.md` if on 2026-11-02, never over an existing file (design D8);
  - then `uv run adni-sexdiff report --check` without `--out`, which reads it as the newest report.

  Verify:
  - the check passes;
  - `grep -nE "\bRID\b|PTID|[0-9]{3}_S_[0-9]{4}"` on the report finds no identifier;
  - the tables, cells and bytes are recorded in this line.

  Commit the report alone. (Recorded on 2026-11-02 on the clean tree at 7a2d212: `report --out reports/motco-adni-2026-11-02-3.md` wrote 14 sections, 112 tables, 7501 cells, parsed back equal; `report --check` without `--out` read it as the newest report (`date 2026-11-02, report 3 from its name`) and compared 112 tables, 7501 cells and 1250 other lines, no mismatch, exit 0; the identifier grep finds nothing; 340,094 bytes, sha256 `d8b68ef6a30c2253969dcacb9f332b6fe2bfafb546fd56af5d98dc623ac875dc`, byte-identical to the scratch report of tasks 3.1 to 3.5. Committed alone as 9779964.)
- [x] 5.3 Update the status paragraph of `AGENTS.md` and `README.md`: the change, the report's name, and the newest report as the default of `--check`. Verify:
  - `git diff --stat main` lists only `src/`, `references/`, `reports/`, `AGENTS.md`, `README.md` and `openspec/`;
  - `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged;
  - every task line records its outcome.

  Commit the task records. (Verified on 2026-11-02: the status paragraphs of `AGENTS.md` and `README.md` name the change, the section "Operating characteristics", `reports/motco-adni-2026-11-02-3.md` as the newest report and the default of `report --check`, the 2026-11-02-2 report among the earlier layouts and the two measurement constants among the decided ones; the README's layout tree gains `references/`. `git diff --stat main` lists only `src/`, `references/`, `reports/`, `AGENTS.md`, `README.md` and `openspec/`; `.gitignore`, `scripts/sync_results.sh`, `PARTICIPANT_LEVEL_PATTERNS` and `AGGREGATE_EXCEPTIONS` are unchanged; every task line records its outcome.)

## Workflow follow-up

- Archive the change: sync the `case-study-report` spec, then run `openspec validate --specs --strict`. Keep requirement statements under 500 characters.
- Push the branch and open the PR.
- After the merge, tell the MOTCO side that `adni_sexdiff`'s rule 3 confirmation landed, so the Phase 6 exit review's consequent-work list (§8) can mark it done. That is MOTCO's own change.
- Citing MOTCO's Phase 6 exit review in the report's limitations stays a later report change, once that review is merged.
