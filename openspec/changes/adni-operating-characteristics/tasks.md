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

- [ ] 1.1 Add the operating-characteristics block to `constants.py` after the rank sweep's (design D2):
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
- [ ] 1.2 Write the copy: `git -C ../MOTCO show 0d726922173188c4d74ce4b2f87f6a26e5fc548f:results/adni-design-2026-11-02/run/adni_design_decision.json > references/motco_adni_design/adni_design_decision.json` (design D3). Verify:
  - its sha256 equals `OPERATING_CHARACTERISTICS_SOURCE["sha256"]` and it is 76,057 bytes;
  - it holds no `RID`, `PTID` or participant-level column (it is MOTCO's synthetic run);
  - each number rules 3 to 6 quote equals the file at the rule's digits, with a script listing every one: 0.076, 0.062, 0.530 and their R; 0.683 (the magnitude e = 1 cell's `cv_mean_auroc_mean`) beside `adni_reference.cv_mean_auroc`; 0.034 to 0.068 and 0.0695; 0.606, 0.578, 1.126, 0.994, 19 in 494 of 500, 0.330 and 51.0 from `calibration_realized`; 0.542, 1.12, 0.73, 8, 0.744 and 35.4 from `adni_reference`.

  The block sizes and shares of rule 6 (367 / 131, 74 % / 26 %) come from MOTCO's report at the pinned commit. Check them against `git -C ../MOTCO show 0d72692:docs/reports/adni-design-2026-11-02.md`. Record the outcome in this line.
- [ ] 1.3 Update the constraint docs for the constants and the copy (design D9):
  - `AGENTS.md` constraint 1: the copy among the committed aggregate files;
  - constraint 5 and "Flag and ask": the two constants with their values in short, decided by `adni-operating-characteristics` after every run, read beside `READING_RULES`;
  - Layout: `references/` and the constants block.

  Verify with `grep -n "OPERATING_CHARACTERISTICS\|references/" AGENTS.md`, which shows every entry.

## 2. Inputs and gates

- [ ] 2.1 Add the role `operating-characteristics` to `REPORT_INPUT_FILES`, and wire the directory through:
  - `_report_dirs` (the tenth directory);
  - `_load_report_inputs` and `run_report`: `operating_characteristics_dir`;
  - `cli.py`: `--operating-characteristics-dir`, default `OPERATING_CHARACTERISTICS_DIR`;
  - `_report_rerun`: the `git show` copy command at the pinned commit (design D4).

  Verify:
  - the constants print `146` input files and `14` sections once group 3 lands (`146 13` until then);
  - `uv run adni-sexdiff report --help` lists thirteen options besides `--help`.
- [ ] 2.2 Handle the copy in gate 2 before the bridge-table branch: its sha256 against `OPERATING_CHARACTERISTICS_SOURCE["sha256"]`, a provenance row recorded in `` `OPERATING_CHARACTERISTICS_SOURCE`: sha256 (MOTCO 0d72692) ``, and its own progress line (design D4). Verify on the committed tree:
  - 146 files hashed;
  - 99 checked against `outputs`, 1 against `bridge.table.sha256`, 1 against the constant, 45 manifests hashed for the chain;
  - 255 chain links, every one `ok`;
  - the step's findings still the five no-`numerics` manifests.
- [ ] 2.3 Add gate 6 after the chain (design D4):
  - `verdict` and `indicative`;
  - the key set of `adni_reference` against `_OPERATING_CHARACTERISTICS_REFERENCE`;
  - each value against its committed source at the map's decimals.

  `_load_report_inputs` returns the parsed decision as `inputs["decision"]`, with the reference rows (key, recorded value, committed source) for the construction table. Verify on the committed tree that every key holds and the progress line names the count of values compared. Record the count in this line.
- [ ] 2.4 Copy the tracked `results/` and `references/` files into a scratch root (`git ls-files results references | xargs cp --parents -t <scratch>`). Run each case on its own copy. In every case the step must stop naming the file or key, both values where there are two, and what to do. It must exit 1, create nothing under the scratch `reports/`, and leave every file unchanged (hashed before and after). The cases:
  - (a) the copy deleted → the file and the `git show` command;
  - (b) one byte of the copy changed → the copy, both hashes and the `git show` command;
  - (c) `OPERATING_CHARACTERISTICS_SOURCE["verdict"]` patched in-process → `verdict`, both values;
  - (d) the copy's `adni_reference.selected_lv` set to 7 and the constant's sha256 patched in-process to the edited copy's → `adni_reference.selected_lv`, 7 and 8, `result.json`, and that citing a measurement for this analysis is a new change;
  - (e) a key `extra` added to the copy's `adni_reference` (sha256 patched likewise) → the key set, with `extra` named as extra;
  - (f) the copy's `adni_reference.phase_offset.p180.median_abs_d` set to 1.13 (sha256 patched likewise) → the key, 1.13 against 1.12, the export manifest.

  Then run on an unedited copy with `--operating-characteristics-dir` pointing to a second scratch directory holding the copy. The step passes every gate. Record the seven outcomes in this line.
- [ ] 2.5 Update the docs for group 2:
  - `AGENTS.md` step 6: 146 inputs with the copy, gate 6 with its map, thirteen flags;
  - `AGENTS.md` Layout: the CLI entry for `report`;
  - `README.md`: the `report` section's inputs and flags;
  - the docstrings of `_load_report_inputs` (gate 6 and the return) and `run_report`, and the `report` CLI help.

  Verify with `grep -n "146\|operating-characteristics-dir" AGENTS.md README.md src/adni_sexdiff/cli.py`.

## 3. Rendering

- [ ] 3.1 Add "Operating characteristics" to `REPORT_SECTIONS` after "Axis diagnostics of the primary". Render the section of design D5:
  - the lead;
  - the tables "Cited measurement", "Decision rule", "Size at this design" with the size sentence, "Power at this design" and "Power floor per statistic";
  - the three statements;
  - "Construction beside this design".

  Verify on a scratch report of the committed tree:
  - fourteen level-2 headings in `REPORT_SECTIONS` order;
  - the section's tables are 6 size rows, 12 power rows and 3 floor rows;
  - parse-back equal to the generated tables.
- [ ] 3.2 Render the rest of design D6:
  - the summary paragraph after the primary's reading bullets;
  - the preamble's change list and reading clause;
  - the provenance row;
  - `OPERATING_CHARACTERISTICS_READING_RULES` after `READING_RULES` under its heading and lead line;
  - the reproduction paragraph with the `git show` line.

  Verify with a script on the scratch report:
  - the verdict, `size.sentence` and the three `statements` are string-equal to the file's, in the section and in the summary;
  - the eight rule lists are string-equal to their constants in order, the second being the nine measurement rules;
  - the primary's reading bullets are string-equal to the committed `results/motco_analysis/summary.md` lines.
- [ ] 3.3 Compare the scratch report with `reports/motco-adni-2026-11-02-2.md`, parsed, by section title. Verify:
  - every table of the twelve shared sections is cell-equal, except the provenance inputs table, which gains the copy's row;
  - every other line is equal, except the title, the preamble, the summary's new paragraph, the section numbers of cross-references, the new section, the new rule list and the reproduction lines.

  Record the counts of tables, cells and differing lines in this line.
- [ ] 3.4 With a script, compare every cell of the section's tables with the decision file. Rates and standard errors at three decimals, the bound at four, construction values at six significant digits, reference values as recorded, and each "checked against" cell naming its source from the D4 map. Verify there is no mismatch and no cell the file does not hold.
- [ ] 3.5 Run `report --force` twice to the same scratch `--out` and check the files are byte-identical. Verify:
  - `report --check --out <scratch report>` passes with no mismatch;
  - after one rate of "Power at this design" is edited by hand, `--check` names the section, the table, the row, the column and both values, and exits 1.
- [ ] 3.6 Update the docs for group 3:
  - the `render_report` docstring: fourteen sections, the section, the eight lists, the verbatim sentences;
  - `AGENTS.md` step 6: the section list and the eight rule lists in order;
  - `AGENTS.md` "Data & domain notes": one sentence that reading rule 3 is measured at this design for the primary only, `OPERATING_CHARACTERISTICS_READING_RULES`;
  - `README.md`: the report's sections.

  Verify with `grep -n "Operating characteristics" AGENTS.md README.md src/adni_sexdiff/data.py`.

## 4. The layout gate

- [ ] 4.1 Update the `_check_report_layout` docstring for the 2026-11-02-2 report (thirteen sections, checks at 67567e2) (design D7). Verify that `report --check --out <report>` stops at the section gate, naming the report, its absent sections and its `git log -1 --format=%H -- <report>` command, exits 1 and writes nothing:
  - for `reports/motco-adni-2026-11-02-2.md` (absent "Operating characteristics"), `2026-11-02.md` and `2026-10-31.md` (the same);
  - for `2026-10-30.md`, `2026-10-29.md` and `2026-10-28.md` (their older absences added).

  Then:
  - a scratch fourteen-section report whose export section lists three variants stops at the variant gate, naming `raw_scale`, `log2_plus_one` and `glog`;
  - `git log -1 --format=%h -- reports/motco-adni-2026-11-02-2.md` prints `67567e2`, and `report --check --out reports/motco-adni-2026-11-02-2.md` passes in a worktree of 67567e2 (removed afterwards).
- [ ] 4.2 Update the earlier-layout list in `AGENTS.md` step 6 and in `README.md`: the 2026-11-02-2 report at 67567e2, and the variant gate reached by no committed report. Verify with `grep -n "67567e2" AGENTS.md README.md`.

## 5. The report

- [ ] 5.1 Commit the implementation: constants, `data.py`, `cli.py`, the copy, `AGENTS.md`, `README.md` and the change's artifacts with tasks 1.1 to 4.2 recorded. Verify that `git status --short` is empty afterwards and that `git diff --stat main -- results` is empty.
- [ ] 5.2 On the clean tree at that commit, write the report under the day's next free name:
  - `uv run adni-sexdiff report --out reports/motco-adni-<date>[-<n>].md`, `motco-adni-2026-11-02-3.md` if on 2026-11-02, never over an existing file (design D8);
  - then `uv run adni-sexdiff report --check` without `--out`, which reads it as the newest report.

  Verify:
  - the check passes;
  - `grep -nE "\bRID\b|PTID|[0-9]{3}_S_[0-9]{4}"` on the report finds no identifier;
  - the tables, cells and bytes are recorded in this line.

  Commit the report alone.
- [ ] 5.3 Update the status paragraph of `AGENTS.md` and `README.md`: the change, the report's name, and the newest report as the default of `--check`. Verify:
  - `git diff --stat main` lists only `src/`, `references/`, `reports/`, `AGENTS.md`, `README.md` and `openspec/`;
  - `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged;
  - every task line records its outcome.

  Commit the task records.

## Workflow follow-up

- Archive the change: sync the `case-study-report` spec, then run `openspec validate --specs --strict`. Keep requirement statements under 500 characters.
- Push the branch and open the PR.
- After the merge, tell the MOTCO side that `adni_sexdiff`'s rule 3 confirmation landed, so the Phase 6 exit review's consequent-work list (§8) can mark it done. That is MOTCO's own change.
- Citing MOTCO's Phase 6 exit review in the report's limitations stays a later report change, once that review is merged.
