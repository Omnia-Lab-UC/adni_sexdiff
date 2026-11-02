# Tasks

This change introduces no scientific constant. The user chose one group of tables per rule set in "Export sensitivity" while this proposal was written. Before the apply starts, the user accepts the other presentation decisions:
- the run-handling group keeps the 2026-10-31 titles and text, and the membership group's tables carry the prefix `nmr_all_columns: ` (design D2);
- every variant-specific word comes from `_variant_words`, and the membership group's lead cites membership rule 8 through `_GROUP_PRIMARY_ONLY_RULE` (design D3);
- the counts table leaves out the `diagnostics` key, which `axis-diagnostics` compares (design D4);
- `NMR_MEMBERSHIP_READING_RULES` is printed after `EXPORT_VARIANT_READING_RULES`, as the sixth of six lists (design D5);
- `report --check` reads a report's variants from its ``Export variant `<name>` `` headings (design D6).

Following the user's rule for the previous reports, the report is written on 2026-11-01 or later, named by the day it is written, and never over the 2026-10-31 file (design D9).

Every task runs on any machine with the Nix shell and the committed tree. The inputs are the tracked files under `results/`. No data root, data machine or participant-level file is needed, and the step records no numerics. Scratch copies and scratch outputs live in the session scratchpad, never under `results/` or `reports/`, except in task 4.2. No task line records a participant value.

## 1. The pin

- [x] 1.1 Set `REPORT_EXPORT_VARIANTS = ("nist_bridge", "per_run_standardized", "nmr_all_columns")` (design D1). Name this change in the module docstring and in the comments of `REPORT_EXPORT_VARIANTS` and `REPORT_INPUT_FILES`. Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(sum(len(v) for v in c.REPORT_INPUT_FILES.values()), len(c.REPORT_SECTIONS), c.REPORT_EXPORT_VARIANTS)"` prints `106 13` and the three variants;
  - each of the 13 new names, resolved against `EXPORT_SENSITIVITY_DIR`, is in `git ls-files results/motco_export_sensitivity/nmr_all_columns`, and the other 2 tracked files of the variant are its `stage_means.csv` and `pls_loadings.csv`.
- [x] 1.2 Run `_load_report_inputs` on the committed tree. Verify that:
  - the provenance lists 106 files, each hash equal to `sha256sum`, and 72 aggregate files are checked against `outputs`;
  - the 33 manifests record MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8, with numerics pinned in 28 and absent in the same five;
  - there are 189 chain links (167 + 22: 4 export, 8 analysis, 6 comparison and 4 diagnostics), every one `ok`;
  - `run_report` prints no uncovered-variant line;
  - the step's own findings are still the five no-`numerics` manifests, with no dirty revision.

  Record the counts in this line. (Recorded on 2026-10-31 on the committed tree at 98d136c with the pin extended: 106 files, each hash equal to `hashlib.sha256` of the file; 72 checked against `outputs`, 1 against `bridge.table.sha256` and 33 hashed for the chain; 33 manifests, every recorded version equal: 25 record MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8, and the 8 manifests of `clean` (2), `cohort`, `export` and the four variant and arm exports record metabo_adni 0.5.8 and no MOTCO or scikit-learn; numerics pinned in 28, absent in `clean p180`, `clean nmr`, `cohort`, `export` and `analyze`; 189 chain links, every one `ok`, the 22 that name `nmr_all_columns` 4 export, 8 analysis, 6 comparison and 4 diagnostics; no uncovered-variant line; the step's findings the five no-`numerics` manifests, no dirty revision.)
- [x] 1.3 Copy the tracked `results/` files into a scratch root (`git ls-files results | xargs cp --parents -t <scratch>`). Run each case below on its own edited copy (design D8). In every case the step must stop, naming the file or setting, both values where there are two, and the command to rerun. It must exit 1, create nothing under the scratch `reports/`, and leave the copy otherwise unchanged (every file hashed before and after). The cases:
  - (a) `motco_export_sensitivity/nmr_all_columns/diagnostics/diagnostics_manifest.json` deleted → the file and the variant's `axis-diagnostics` command with its three directories.
  - (b) One byte of `nmr_all_columns/comparison/export_sensitivity.csv` changed → the file, both hashes, and `export-sensitivity --variant nmr_all_columns --force`.
  - (c) The `nmr_all_columns` directory replaced by `per_run_standardized`'s outputs → the directory, the variant it expects and the variant its manifests record (identity, before the chain).
  - (d) `EXPORT_VARIANTS["nmr_all_columns"]["setting"]` patched in-process before the loader runs → the variant, `EXPORT_VARIANTS`, both values and `export-sensitivity --variant nmr_all_columns --force`.
  - (e) The variant's `result.json` with `measurement.n_jobs` 4, and its manifest's recorded hash updated so the hash gate holds → that `result.json`, 4, and the `export-sensitivity` command without `--n-jobs`.
  - (f) The variant's analysis manifest with `numerics.pinned` false → that manifest.
  - (g) The variant export manifest's `reference.manifest.sha256` edited → that manifest, the key, both hashes and `export-sensitivity --variant nmr_all_columns --force`.
  - (h) The variant's analysis manifest rewritten with a key reordered, and the comparison's record of it updated, as a `--force` rerun leaves them → the variant's diagnostics manifest, `inputs.analysis.analysis_manifest.sha256`, both hashes and its `axis-diagnostics` command.

  Record the eight outcomes in this line. (Recorded on 2026-10-31, each on its own copy of the 130 tracked files, `report` run with the defaults from the copy's root: every case exit 1, no `reports/`, every file unchanged. (a) `1 report input(s) absent`, the file, and `axis-diagnostics --input-dir results/motco_export_sensitivity/nmr_all_columns/motco_input --analysis-dir results/motco_export_sensitivity/nmr_all_columns/analysis --out-dir results/motco_export_sensitivity/nmr_all_columns/diagnostics`; (b) the file, its sha256 and the one its comparison manifest records, `export-sensitivity --variant nmr_all_columns --force`, then the variant's `axis-diagnostics`; (c) `results/motco_export_sensitivity/nmr_all_columns is not the variant 'nmr_all_columns'`, its export manifest records `'per_run_standardized'` (identity, before the chain), `--export-sensitivity-dir` or `export-sensitivity --variant nmr_all_columns --force`; (d) the export manifest's recorded setting against `EXPORT_VARIANTS['nmr_all_columns']['setting']` `'patched setting'`, `export-sensitivity --variant nmr_all_columns --force`; (e) `nmr_all_columns/analysis/result.json (measurement.n_jobs) records n_jobs = 4`, `export-sensitivity --variant nmr_all_columns --force` without `--n-jobs`; (f) the variant's `analysis_manifest.json` records `numerics.pinned False`; (g) `nmr_all_columns/motco_input/manifest.json: reference.manifest.sha256`, both hashes, `export-sensitivity --variant nmr_all_columns --force`; (h) the variant's `diagnostics_manifest.json: inputs.analysis.analysis_manifest.sha256`, both hashes, and the variant's `axis-diagnostics` command with its three directories.)
- [x] 1.4 Update the docs for what group 1 changes:
  - `README.md`, the `report` section: 106 inputs and 33 manifests, the variant's 13 files, and 189 chain links (22 for `nmr_all_columns`);
  - `AGENTS.md`, step 6: 106 inputs, 33 manifests and 189 links (31, then 23, 22 and 22 for the three variants, 24 and 67);
  - `AGENTS.md`, the Layout entry for `constants.py` (`REPORT_EXPORT_VARIANTS` with the three variants).

  Verify with `grep` that "93 committed files", "29 manifests" and "167 links" no longer describe the current step in `README.md`, `AGENTS.md` or `src/`. (Verified on 2026-10-31: none of the three appears in `README.md`, `AGENTS.md` or `src/`; the `_REPORT_MANIFESTS` comment and the `run_report` docstring now say 33 manifests, 106 files and 189 links, and the one remaining "93" is the comment of `REPORT_INPUT_FILES` naming the count before this change.)

## 2. The renderer

- [x] 2.1 Group the "Export sensitivity" section by rule set (design D2, D3):
  - the section lead when the pin holds more than one group;
  - per group: its lead, its tables (group 1 under the 2026-10-31 titles, a later group's prefixed by its variant names, with the singular for one variant), its per-variant headings, blocks and diagnostics, and its `cli_equivalent`s;
  - every variant-specific word taken from `_variant_words`;
  - `_GROUP_PRIMARY_ONLY_RULE`, mapping `NMR_MEMBERSHIP_READING_RULES` to 8.

  Verify on the committed tree, writing to a scratch `--out`:
  - the level-2 headings equal `REPORT_SECTIONS` in order;
  - the section holds the group-1 tables under their 2026-10-31 titles, and the group-2 tables `nmr_all_columns: Statistics: primary and variant` (6 rows: `delta primary`, `delta nmr_all_columns`, …), `nmr_all_columns: Latent space: primary and variant` (6 rows), `nmr_all_columns: Run offset per export` (4 rows), `nmr_all_columns: Export against the predeclared counts` and `nmr_all_columns: First component against phase` (2 rows);
  - `delta nmr_all_columns` has status `differs (feature-membership dependence)`, and `angle` and `shape` are `same`;
  - no table of the section holds a group-1 variant together with `nmr_all_columns`;
  - the group-2 lead names `READING_RULES` and `NMR_MEMBERSHIP_READING_RULES` and cites membership rules 1, 2 and 8. Its `angle` and diagnostics paragraphs cite membership rules 3 and 7, and no group-2 line cites `variant rule` or `EXPORT_VARIANT_READING_RULES`.

  (Verified on 2026-10-31 with the scratch checker `check_report_nmr_render.py` on a scratch `--out`: the thirteen headings in order; the five group-1 tables equal to the 2026-10-31 report's, title, columns and rows; the group-2 tables with 6, 6, 4, 40 and 2 rows, the statistics rows `delta primary`, `delta nmr_all_columns`, … `shape nmr_all_columns`; `delta nmr_all_columns` `differs (feature-membership dependence)`, `angle` and `shape` `same`, every primary row `the result`; none of the section's 24 tables holds a group-1 variant with `nmr_all_columns`; the group-2 lead cites membership rules 1, 2 and 8, its `angle` paragraph membership rule 3 and its diagnostics paragraph membership rule 7, and none of its 70 lines cites `variant rule` or `EXPORT_VARIANT_READING_RULES`.)
- [x] 2.2 Leave the `diagnostics` key out of the counts table (design D4). Verify that:
  - the group-1 counts table equals the 2026-10-31 report's "Variant exports against the predeclared counts" (title, columns and rows);
  - the group-2 table holds every key of `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]` except `analysis`, `phase_offset` and `diagnostics`, and no row of either table is `n/a` in every cell.

  (Verified on 2026-10-31: the group-1 table equal, 36 rows; the group-2 table's 40 rows are the flattened keys of the entry without `analysis`, `phase_offset` and `diagnostics`, in order; no row of either is `n/a` in every cell.)
- [x] 2.3 Write the summary's group paragraphs, the preamble, the six rule lists and the docstring of `render_report` (design D3, D5). Verify that:
  - the summary holds the 2026-10-31 run-handling paragraph and its bullets unchanged, then the membership paragraph with `differs (feature-membership dependence)`, `NMR_MEMBERSHIP_READING_RULES`, rank 7, section 8 and the three status bullets;
  - each change name is in its own backticks;
  - the reading-rules section holds six numbered lists, the fourth `NMR_MEMBERSHIP_READING_RULES` with eight items, led by the line its `export_sensitivity.md` prints;
  - findings, provenance and reproduction carry the variant by iteration: its four manifests under "Findings", its `axis-diagnostics` command, and 12 `cli_equivalent`s;
  - the renderer holds no literal section number.

  Record the sections, tables and cells generated, and the report's size. (Recorded on 2026-10-31 on a scratch `--out` named for 2026-11-01: the summary's run-handling paragraph and its 12 following lines equal to the 2026-10-31 report's, then the membership paragraph with `differs (feature-membership dependence)`, `NMR_MEMBERSHIP_READING_RULES`, rank 7 and section 8, `` `nmr_all_columns` (rank 7): `` and its three status bullets; no backtick span holds two change names; six lists in order, each string-equal to its constant (9, 9, 7, 8, 8, 8 items), the fourth `NMR_MEMBERSHIP_READING_RULES` led by the line of its `export_sensitivity.md`; the variant's four manifests under "Findings", its 13 inputs and 22 chain links in the provenance, its `axis-diagnostics` command and 12 `motco analyze` commands in the reproduction; no literal `section <n>` in the renderer. 13 sections, 89 tables, 5418 cells, 241526 bytes.)
- [x] 2.4 Write the scratch diff checker `check_report_nmr_diff.py` (design D7). It parses the 2026-10-31 report and the scratch report with `parse_report`. It must report:
  - every 2026-10-31 table present with equal title, columns and rows, except the four provenance tables, whose old rows must be equal and in order;
  - every 2026-10-31 non-table line present in order, except the title line, the preamble, the export-sensitivity section lead, the summary's diagnostics paragraph and the lead of the CLI equivalents.

  Record the changed lines and the tables that gained rows in this line. Any other difference is a defect to fix before going on. (Recorded on 2026-10-31: 80 tables and 812 other lines of the 2026-10-31 report compared, 0 defects. The changed lines are exactly five: the title line (line 1), the preamble (line 3), the summary's diagnostics paragraph (line 47), the export-sensitivity section lead (line 924, now the run-handling group's lead, "Every table of this group" without the primary's hash, which the new section lead carries) and the lead of the CLI equivalents (line 1756, 11 → 12 analyses). The tables that gained rows, their old rows equal and in order: "Versions per step" 29 → 33, "Revisions and numerics per step" 29 → 33, "Inputs" 93 → 106, "Chain links checked" 167 → 189.)
- [x] 2.5 Write the scratch value checker `check_report_nmr_values.py` (design D8). It reads the scratch report's group-2 tables and, independently, the source files with `json`, `csv` and `hashlib`. It must report zero differences, compared at the printed digits, for:
  - the statistics rows against the variant's `export_sensitivity.csv`, and the rank against `latent.selected_lv`;
  - the latent space against the CSV and both `config_spectrum`s;
  - the run offsets and counts against the two export manifests;
  - the diagnostics tables against the variant's CSVs;
  - the 13 new input hashes against `hashlib` and the recording manifests.

  It must also verify string equality:
  - the status bullets, every "Export variant" bullet and every latent-space row equal their lines in the committed `nmr_all_columns/comparison/export_sensitivity.md`;
  - the rules' lead line equals that document's;
  - the six rule lists equal the constants, item by item.

  It lists every line that names `nmr_all_columns` together with another sensitivity and verifies that each is a listing. An audit hook (`sys.addaudithook`) over `run_report` must list 106 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git. Record the counts compared in this line. (Recorded on 2026-10-31, the report split by the checker itself and the sources read with `json`, `csv` and `hashlib`: 331 cells compared, 0 differences: the six statistics rows against `export_sensitivity.csv` and the comparison manifest's statuses; the latent space against the CSV, both `latent` blocks (ranks 8 and 7, `cv`) and both `config_spectrum`s; the four run-offset rows against the two export manifests; the 40 count rows against the variant export manifest's `counts` and `expected`; the flagged rows, components and block PCs against `axis_correlations.csv`, `block_pcs.csv`, `components.csv` and the export manifest's Pearson value; the first-component rows against both `axis_correlations.csv`; the 13 new inputs' sha256 and bytes against `hashlib`, the 11 aggregate files against their manifests' `outputs`, the variant export manifest recorded by 3 manifests downstream and its analysis manifest by 2, the comparison and diagnostics manifests the chain's leaves. 67 lines string-equal: the 3 status bullets, the 8 "Export variant" bullets and the 6 latent-space rows to `nmr_all_columns/comparison/export_sensitivity.md`, its rules' lead line, and the 49 items of the six rule lists to the constants. Four lines name `nmr_all_columns` with another sensitivity, each a listing: the preamble, the summary's diagnostics paragraph, the section lead and the lead of the CLI equivalents. The audit: 106 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git.)
- [x] 2.6 Verify determinism and the identifier rule:
  - two `--force` runs to the same scratch `--out` have equal sha256;
  - a run to a file named with another date differs only in the title line;
  - `grep -nE '\bRID\b|\brid\b'` over the scratch report hits only column-name mentions.

  Record the hash and the hits in this line. (Recorded on 2026-10-31 on the scratch `motco-adni-2026-11-01.md`: two `--force` runs sha256 `b818d544c05c1b9d97865f1f912a9cb270fc8512d6135da34a9cd10455dd78d6`, equal to the render of 2.3; a run named for 2026-12-25 differs in line 1 only; 25 hits, all column names: the export bullet's sample column `rid` and `--sample-col rid` in the 12 `cli_equivalent`s of the sections and the 12 of the reproduction (the 2026-10-31 report had 23).)
- [x] 2.7 Update the docs for what group 2 changes:
  - `README.md`: the status sentence that says the report does not cover `nmr_all_columns` yet, and the `report` section (the groups, six rule lists);
  - `AGENTS.md`, the status paragraph: the report covers `nmr_all_columns`, the pin holds the three variants, and the newest report's coverage;
  - `AGENTS.md`, step 6: the groups, the six rule lists and the membership group's wording from `_variant_words`;
  - `AGENTS.md`, the Layout entry for `data.py`;
  - the docstrings of `_export_sensitivity_section` and `run_report`.

  Leave "Flag and ask" unchanged. Verify with `grep` that "not yet covered by the report" and "a later report change adds it" no longer describe `nmr_all_columns`. (Verified on 2026-10-31: neither phrase, nor "does not cover it yet", appears in `README.md`, `AGENTS.md` or `src/`; the `README.md` pin paragraph names the three variants and the progress line only for a variant registered later; no hunk of `AGENTS.md` touches "Flag and ask".)

## 3. The checker

- [x] 3.1 Add the variant comparison to `_check_report_layout` (design D6). Verify:
  - `uv run adni-sexdiff report --check --out reports/motco-adni-2026-10-31.md` stops before any input gate. It names the report, the absent variant 'nmr_all_columns', no extra variant and `git log -1 --format=%H -- reports/motco-adni-2026-10-31.md` (13ce7c8…), writes nothing and exits 1;
  - the 2026-10-30, 2026-10-29 and 2026-10-28 reports stop on their sections, with the messages of `adni-report-rank-sweep` task 4.1;
  - a scratch copy of the scratch report with two ``Export variant `…` `` blocks swapped stops naming no absent and no extra variant and that the order differs;
  - in a scratch worktree of 13ce7c8, the 2026-10-31 report passes its own check with no mismatch. Remove the worktree afterwards;
  - with a scratch copy of `src/` whose pin holds the two p180 variants, `report` on the committed tree reads 93 files, prints the uncovered-variant line for `nmr_all_columns`, and no line of its body names `nmr_all_columns`.

  Record the outcomes in this line. (Recorded on 2026-10-31: the 2026-10-31 report stops naming `its export variants are not REPORT_EXPORT_VARIANTS (absent: 'nmr_all_columns'; extra: none)` and `git log -1 --format=%H -- reports/motco-adni-2026-10-31.md`, which gives 13ce7c852aa0…, with no progress line before it (no input gate ran), exit 1; the 2026-10-30, 2026-10-29 and 2026-10-28 reports stop on their sections, absent 'Rank sensitivity'; 'Stage-definition sensitivity', 'Rank sensitivity'; 'Export sensitivity', 'Stage-definition sensitivity', 'Rank sensitivity', each message string-equal to the one `main`'s `_check_report_layout` gives, imported from a scratch worktree of 98d136c; the four reports byte-unchanged; the scratch report with its `nist_bridge` and `per_run_standardized` "Export variant" headings swapped stops with `absent: none; extra: none; the order differs`, before any input gate, exit 1, the copy unchanged; in a scratch worktree of 13ce7c8 the 2026-10-31 report checks with no mismatch, 80 tables, 4737 cells and 812 other lines compared, exit 0; both worktrees removed; with a scratch `src/` whose pin holds the two p180 variants, `report` opens 93 files under `results/`, prints `export variant nmr_all_columns (change adni-nmr-all-columns) is registered and not covered by this report`, writes 80 tables and 4737 cells, no line names `nmr_all_columns`, and every line after the preamble equals the 2026-10-31 report's.)
- [x] 3.2 Run failure checks of the check, each on a copy of the scratch report or of the scratch results root:
  - (a) one p-value of the `delta nmr_all_columns` row changed by hand → the section, the table, the row, the column and both values; exit 1;
  - (b) one word of the variant's `delta` status line changed → the section and the line, with both texts;
  - (c) in a copy of the results root, the variant's `export_sensitivity.md` edited and its manifest's `outputs` hash updated to match → the provenance cells of both files, with both hashes;
  - (d) `report --check` on unchanged inputs → no mismatch, exit 0;
  - (e) every check run leaves the report and the results root unchanged (hashes before and after).

  Record the printed messages in this line. (Recorded on 2026-10-31, each on its own copy of the scratch report of 2.3: (a) `Export sensitivity › table "nmr_all_columns: Statistics: primary and variant" › row delta nmr_all_columns › p (RRPP): report '0.0448', generated '0.0447'`, 1 mismatch, exit 1; (b) the summary's `delta` line with "rejects whereas" for "rejects where": `Summary › line 39: report "…", generated "…"` with both texts, 1 mismatch, exit 1; (c) on a copy of the 130 tracked files, a line added to the variant's `export_sensitivity.md` and its comparison manifest's `outputs` hash updated: `Provenance › table "Inputs"` rows of both files, the `.md`'s sha256 and bytes (12890 → 12891) and the manifest's sha256, 3 mismatches, exit 1; (d) `89 tables, 5418 cells and 929 other lines compared; no mismatch; nothing was written`, exit 0; (e) every run left the report copy and the results root it read byte-unchanged.)
- [x] 3.3 Update the docs for the check:
  - `README.md` and `AGENTS.md`, the earlier-layout gate: the variant comparison, and four earlier reports, `reports/motco-adni-2026-10-28.md` (ten sections, 36c9cc8), `reports/motco-adni-2026-10-29.md` (eleven, c94f5e7), `reports/motco-adni-2026-10-30.md` (twelve, 2e4a3e1) and `reports/motco-adni-2026-10-31.md` (two export variants, 13ce7c8);
  - the docstrings of `_check_report_layout`, `check_report` and `run_report`.

  Verify with `grep` that the four reports and the four revisions are named in both files. (Verified on 2026-10-31: each of the four report names and each of 36c9cc8, c94f5e7, 2e4a3e1 and 13ce7c8 appears once in `README.md` and once in `AGENTS.md`, in the earlier-layout paragraph.)

## 4. The report and commit hygiene

- [x] 4.1 Commit the implementation, the docs and the change's artifacts on the branch `adni-report-nmr-all-columns`, created from `main` (98d136c). Verify that `git status` is clean and that no file under `results/` or `reports/` changed. (Committed on 2026-10-31 on `adni-report-nmr-all-columns`, from 98d136c; `git status` clean after it; the commit touches `src/adni_sexdiff/constants.py`, `src/adni_sexdiff/data.py`, `README.md`, `AGENTS.md` and the change's artifacts only.)
- [x] 4.2 Only once `date +%F` is later than 2026-10-31 (design D9), on the clean tree at the implementing commit:
  - run `uv run adni-sexdiff report` (no `--out`, so it is named by today's date), then `uv run adni-sexdiff report --check`;
  - verify the check passes and reads the new report as the newest;
  - verify that the new report equals the scratch render of 2.6 apart from its title line;
  - verify that `grep -nE '\bRID\b|\brid\b'` over the new report hits only column-name mentions;
  - verify that the four earlier reports are byte-unchanged.

  Commit the new report alone, and record its name, sections, tables, cells, chain links and size in this line. (Recorded on 2026-11-02 on the clean tree at 5f11f58: the scratch render of 2.6, regenerated first under its 2026-11-01 name, reproduced its sha256 `b818d544c05c1b9d97865f1f912a9cb270fc8512d6135da34a9cd10455dd78d6`; `uv run adni-sexdiff report` wrote `reports/motco-adni-2026-11-02.md`, 13 sections, 89 tables, 5418 cells, 106 inputs under 33 directories, 33 manifests, 189 chain links, 241526 bytes, parsed back equal to the generated tables; `uv run adni-sexdiff report --check` read it as the newest, compared 89 tables, 5418 cells and 929 other lines, no mismatch, exit 0, the five no-`numerics` findings as before; `diff` against the scratch render differs in line 1 only; the identifier grep gives 25 hits, every one the sample column `rid` (the export bullet and `--sample-col rid` in the 24 `cli_equivalent`s); the four earlier reports byte-unchanged (`git status` shows the new file alone). Committed alone as 28e0d48.)
- [x] 4.3 Check commit hygiene. Verify that:
  - `git status` is clean;
  - `git ls-files results` lists the same files as `main`;
  - no file under `results/` changed in any commit of the branch;
  - over every file the branch adds or changes, the identifier grep finds only column names (`RID`, `rid`), never a participant value.

  Record the files the branch adds or changes in this line. (Recorded on 2026-11-02 after 28e0d48: `git status` clean; `git ls-files results` lists the same 130 files as `main`; no commit of the branch touches `results/`; the branch changes `AGENTS.md`, `README.md`, `src/adni_sexdiff/constants.py` and `src/adni_sexdiff/data.py` and adds `reports/motco-adni-2026-11-02.md` and the change's five artifacts under `openspec/changes/adni-report-nmr-all-columns/`; the identifier grep over them finds column names (`RID`, `rid`), the constants `PARTICIPANT_ID_COLUMN` and `SAMPLE_COLUMN` and loop variables named `rid` in `data.py`, never a participant value.)

## Workflow follow-up

- After the report is committed, archive the change on the branch. The archive syncs `openspec/specs/case-study-report/`, and `openspec validate --strict` must pass on the synced spec. Then push, open the PR and merge, following the PR workflow of the earlier changes.
- A regenerated results directory invalidates the committed report: `report --check` fails on its provenance cells until a new report is written and checked.
- With this change every predeclared sensitivity that has run is in the report. The next change is the scale variants (the raw scale, `log2(x + 1)`, the generalized log), its own proposal. It registers and runs them, and a report change then adds their group. The cluster run waits on the deploy key (constraint 7).
