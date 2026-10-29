# Tasks

This change introduces no scientific constant. Before the apply starts, the user accepts the proposal's two presentation decisions. First, the per-metabolite bridge table is quoted by hash, with the seven unbridged rows printed, and not in full (design D4). Second, `reports/motco-adni-2026-10-28.md` stays in place and checks at the revision that committed it, not with the new code (design D6).

Every task runs on any machine with the Nix shell and the committed tree. The inputs are the tracked files under `results/`; no data root, data machine or participant-level file is needed, and the step records no numerics. Scratch copies and scratch outputs live in the session scratchpad, never under `results/` or `reports/`, except task 6.1. No task line records a participant value.

## 1. Constants and the flag

- [x] 1.1 Extend `REPORT_INPUT_FILES` with the roles `export-sensitivity/<variant>/<subdir>` (design D2), built from `EXPORT_VARIANTS` and `EXPORT_SENSITIVITY_SUBDIRS`, with the bridge role for hook `factors`. Add "Export sensitivity" to `REPORT_SECTIONS` between "Latent-adjustment sensitivity" and "Findings". Name this change in the module docstring. Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(sum(len(v) for v in c.REPORT_INPUT_FILES.values()), len(c.REPORT_SECTIONS))"` prints `53 11`;
  - every new name, resolved against `EXPORT_SENSITIVITY_DIR`, is in `git ls-files results/motco_export_sensitivity`.

  Done: the per-subdirectory file lists are the convention `REPORT_VARIANT_FILES` (keyed by `EXPORT_SENSITIVITY_SUBDIRS`), and the roles are built in `EXPORT_SENSITIVITY_SUBDIRS` order (bridge, motco_input, analysis, comparison, diagnostics). Verified: `53 11`; the 27 new names are all tracked.
- [x] 1.2 Add `--export-sensitivity-dir` to the `report` subparser (default `EXPORT_SENSITIVITY_DIR`), and pass it through `cli.main` and `run_report` to `_report_dirs`. Verify that `uv run adni-sexdiff report --help` lists ten flags with their defaults. Verified: ten flags; the seven directory flags show their defaults.

## 2. The loader and the gates

- [x] 2.1 Extend `_report_dirs`, `_report_rerun` and `_REPORT_MANIFESTS` with the variant roles and labels (design D2, D7). Extend `_load_report_inputs` with:
  - the bridge table's hash against `bridge.table.sha256` of its export manifest;
  - the variant identity gate;
  - the variant reported-run gate;
  - the version agreement over 17 manifests;
  - the variant chain links (design D3);
  - the variant tables (comparison CSVs, bridge table, diagnostics CSVs) in the returned `tables`.

  Verify on the committed tree that it completes, and that:
  - the provenance rows list 53 files whose hashes equal `sha256sum`;
  - every chain link reads `ok`, and the count is 76 (31 + 23 + 22), recorded here;
  - the step's own findings are still the five no-`numerics` manifests, with no dirty revision;
  - an audit hook (`sys.addaudithook`) over the loader and the writer lists 53 files opened under `results/`, none participant-level.

  Verified on the committed tree: 53 provenance rows, every hash equal to `hashlib`'s; 76 chain links, all `ok` (31 + 23 for `nist_bridge` + 22 for `per_run_standardized`); the findings are the five no-`numerics` manifests, no dirty revision; the audit hook over `run_report` lists 53 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none participant-level. The bridge table's hash is checked in gate 3, once its variant's export manifest is identified, so that a swapped directory is named as a swap.
- [x] 2.2 Copy the tracked `results/` files into a scratch root (`git ls-files results | xargs cp --parents -t <scratch>`). On one edited copy per case, verify that the step stops naming the file or setting, both values where there are two, and the command to rerun. In every case nothing may be created under the scratch `reports/`, and the copy must be otherwise unchanged. The cases:
  - (a) `per_run_standardized/diagnostics/diagnostics_manifest.json` deleted → the file, and the `axis-diagnostics` command with that variant's three directories;
  - (b) one byte of `nist_bridge/bridge/nist_bridge.csv` changed → the table, both hashes, `export-sensitivity --variant nist_bridge --force`;
  - (c) the `nist_bridge` and `per_run_standardized` directories swapped → the directory, the expected and the recorded variant;
  - (d) the `per_run_standardized` analysis `result.json` with `measurement.n_jobs` 4, and its manifest's recorded hash updated so the hash gate holds → that `result.json` and 4;
  - (e) a variant comparison manifest's `numerics.pinned` set to false → that manifest;
  - (f) the `nist_bridge` analysis manifest rewritten (a key reordered) → the variant diagnostics manifest, both hashes, the variant's `axis-diagnostics` command;
  - (g) the `per_run_standardized` export manifest's `reference.manifest.sha256` edited → that manifest, both hashes, `export-sensitivity --variant per_run_standardized --force`;
  - (h) `EXPORT_VARIANTS["nist_bridge"]["setting"]` patched in-process before the loader runs → the variant, `EXPORT_VARIANTS`, both values and the `export-sensitivity` command.

  Record the eight outcomes in this line. Every case exits 1, creates nothing under the scratch `reports/` and leaves the copy unchanged (every file hashed before and after):
  - (a) `FileNotFoundError`: the absent manifest and `axis-diagnostics --input-dir …/per_run_standardized/motco_input --analysis-dir …/per_run_standardized/analysis --out-dir …/per_run_standardized/diagnostics`.
  - (b) the bridge table, its sha256 beside the `bridge.table.sha256` the `nist_bridge` export manifest records, and `export-sensitivity --variant nist_bridge --force`.
  - (c) with the four subdirectories both variants hold swapped: "`…/nist_bridge` is not the variant 'nist_bridge': `…/nist_bridge/motco_input/manifest.json` records the variant 'per_run_standardized'". With the whole directories swapped, the presence gate stops first, naming the absent `nist_bridge/bridge/nist_bridge.csv` and `export-sensitivity --variant nist_bridge --force`.
  - (d) "`…/per_run_standardized/analysis/result.json` (measurement.n_jobs) records n_jobs = 4", and `export-sensitivity --variant per_run_standardized --force` without `--n-jobs`.
  - (e) "`…/per_run_standardized/comparison/export_sensitivity_manifest.json` records numerics.pinned False".
  - (f) with only the analysis manifest rewritten, the comparison's link breaks first (it records the analysis manifest too): the comparison manifest, both hashes, `export-sensitivity --variant nist_bridge --force`. As a `--force` rerun leaves it (the comparison's record of the analysis manifest updated too): the variant diagnostics manifest, `inputs.analysis.analysis_manifest.sha256`, both hashes and the variant's `axis-diagnostics` command with its three directories.
  - (g) that manifest, `reference.manifest.sha256`, the edited and the primary export manifest's hash, `export-sensitivity --variant per_run_standardized --force`.
  - (h) the `nist_bridge` export manifest, `EXPORT_VARIANTS['nist_bridge']['setting']`, both values and `export-sensitivity --variant nist_bridge --force`.

## 3. The renderer

- [x] 3.1 Implement the "Export sensitivity" section and the extensions of the summary, provenance (with the "QC archives and NIST workbooks" table), reading-rules and reproduction sections (design D4). Section numbers in the text must come from `REPORT_SECTIONS`. Verify on the committed tree into a scratch `--out`:
  - the level-2 headings equal `REPORT_SECTIONS` in order;
  - the export section holds "Statistics: primary and variants" with `delta primary` first, then `nist_bridge`, then `per_run_standardized`, with the primary's status `the result`;
  - it holds the latent-space and run-offset tables with three columns or rows per block, the counts table against `EXPORT_VARIANT_EXPECTED_COUNTS`, the export-variant bullets, "NIST bridge per kit" (102 / 24 / 7 beside the predeclared values) and "Unbridged metabolites" (7 rows);
  - it holds both variants' flagged rows, components and block PCs, "First component against phase" with three rows, and two `cli_equivalent` blocks;
  - the reading-rules section holds three numbered lists, the third with seven items;
  - no literal "section <n>" in the renderer's source refers to a hard-coded number.

  Record the tables and cells generated. Verified: 11 sections, 58 tables (42 before; 15 in "Export sensitivity", 1 new in "Provenance"), 2850 cells, parsed back equal; the renderer holds no literal section number (`_section_ref`).
- [x] 3.2 Extend the scratch value checker of `adni-report` (design D9), or write `check_report_variant_values.py`. It reads the scratch report's new tables and, independently, the source files, and must report zero differences, compared at the printed digits:
  - the variant statistics rows with `export_sensitivity.csv`, and the ranks with `latent.selected_lv` of each variant `result.json`;
  - the offsets and counts with each export manifest's `counts` and `expected`;
  - the bridge tables with `bridge.summary` and `nist_bridge.csv`;
  - the flagged rows, components and block PCs with each variant's diagnostics CSVs;
  - the QC rows with `inputs.qc`;
  - the 27 new input hashes with `hashlib` and the recording manifests.

  Also verify string equality:
  - each status line and each export-variant bullet of the report equals the corresponding line of the committed `export_sensitivity.md` of its variant;
  - the three numbered rule lists equal `READING_RULES`, `LATENT_SENSITIVITY_READING_RULES` and `EXPORT_VARIANT_READING_RULES`, item by item;
  - no sentence compares one variant with the other.

  Record the counts compared. `check_report_variant_values.py` (session scratchpad, own Markdown parser, sources read with `json`, `csv` and `hashlib`): 663 cells, 47 strings and 27 input hashes compared, zero differences. Four lines name both variants, all listings (the summary's lead, its diagnostics sentence, the section's lead, the reproduction's list); none compares them.
- [x] 3.3 Verify determinism and the identifier rule:
  - two `--force` runs to the same scratch `--out` have equal sha256;
  - a run to a file named with another date differs only in the title line;
  - `grep -nE '\bRID\b|\brid\b'` over the report hits only column-name mentions.

  Verified: two runs hash to the same sha256; a run named 2027-01-15 differs in line 1 only; the grep hits the sample column `rid` and `--sample-col rid` of the four `cli_equivalent` commands only.
- [x] 3.4 Only if task 3.1 changed `_export_variant_status_line`, `_export_variant_lines` or `_export_variant_rules_heading` (design D5): re-render from the committed files the two `export_sensitivity.md`, the two variant `summary.md` and the two variant `diagnostics.md`. Each must hash to the value its manifest records; a difference reverts the change. Otherwise, record here that no helper changed. No helper changed: `_export_variant_status_line`, `_export_variant_lines`, `_export_variant_rules_heading`, `_offset_text` and the four document renderers are byte-identical to `main`.

## 4. The checker

- [x] 4.1 Add the earlier-layout gate to `check_report` (design D6). Verify:
  - `uv run adni-sexdiff report --check --out reports/motco-adni-2026-10-28.md` stops before any input gate, naming the report, the absent section "Export sensitivity" and `git log -1 --format=%H -- reports/motco-adni-2026-10-28.md`; it writes nothing and exits non-zero;
  - in a scratch worktree of 36c9cc8 (`git worktree add <scratch> 36c9cc8`), the same check passes with no mismatch. Remove the worktree afterwards.

  Verified: the check stops before any gate (no `[report]` line), naming the report, absent 'Export sensitivity', extra none and `git log -1 --format=%H -- reports/motco-adni-2026-10-28.md` (36c9cc8d), exit 1, nothing written. At 36c9cc8 (its `src/` first on `PYTHONPATH`): 42 tables, 1631 cells and 365 other lines compared, no mismatch, exit 0; the worktree is removed.
- [x] 4.2 Failure checks of the check, each on a copy of the scratch report or of the scratch results root. Record the printed messages in this line. The cases:
  - (a) one p-value of a variant row of "Statistics: primary and variants" changed by hand → the section, the table, the row, the column and both values; exit non-zero;
  - (b) one word of a variant status line changed → the section and the line, with both texts;
  - (c) in a copy of the results root, a variant's `export_sensitivity.md` edited and its manifest's `outputs` hash updated to match → the provenance cells of both files, with both hashes;
  - (d) `report --check` on unchanged inputs → no mismatch, exit zero;
  - (e) every check run leaves the report and the results root unchanged (hashes before and after).

  Outcomes: (a) "Export sensitivity › table \"Statistics: primary and variants\" › row delta nist_bridge › p (RRPP): report '0.1367', generated '0.1366'", exit 1. (b) "Export sensitivity › line 786: report \"- `angle`: same … no less informative …\", generated \"… no more informative …\"", exit 1. (c) run from inside the copy: the sha256 and bytes cells of `export_sensitivity.md` and the sha256 cell of `export_sensitivity_manifest.json` in "Provenance › Inputs", each with both values, exit 1. (d) 58 tables, 2850 cells and 560 other lines compared, no mismatch, exit 0. (e) the tracked `results/`, the copy and every scratch report hash the same before and after.

## 5. The docs

- [x] 5.1 Update `README.md`: the status paragraph, the `report` section (inputs with the variant files, the ten flags, the gates with the variant identity and chain, the eleven sections, the earlier-layout check), and the quick start (it already lists `export-sensitivity --variant all` and the two variant `axis-diagnostics` commands, unchanged).
- [x] 5.2 Update `AGENTS.md`:
  - the status paragraph: the report covers the export variants; remove "the committed report does not cover them yet";
  - step 6: 53 inputs, 17 manifests, 76 chain links, eleven sections, ten flags, the third rule list, the layout gate;
  - the Layout entries for `cli.py`, `constants.py` and `data.py`.

  "Flag and ask" stays unchanged. Update the `constants.py` docstring and the `run_report` docstring. Verify by `grep` that "26 committed files", "31 links", "ten sections" and "nine flags" no longer appear where they describe the current step. Verified: the one hit left in each of `AGENTS.md` and `README.md` is "ten sections" describing `reports/motco-adni-2026-10-28.md` under the earlier-layout gate.

## 6. The report and commit hygiene

- [ ] 6.1 Commit the implementation first. Then, on the clean tree at that commit (`git status` clean):
  - run `uv run adni-sexdiff report`, then `uv run adni-sexdiff report --check`;
  - verify the check passes and reads the new report as the newest;
  - verify `grep -nE '\bRID\b|\brid\b' reports/motco-adni-<date>.md` hits only column-name mentions;
  - verify `reports/motco-adni-2026-10-28.md` is byte-unchanged.

  Commit the new report alone, and record its sections, tables, cells and chain links in this line.
- [ ] 6.2 Commit hygiene. Verify:
  - `git status` is clean;
  - `git ls-files results` lists the same 61 files as before the change (30 + 31);
  - no file under `results/` changed in any commit of the branch;
  - no committed file holds a participant identifier (the grep of 6.1 over every file the branch adds).

## Workflow follow-up

- Archive the change on the branch, after the report is committed. The archive syncs `openspec/specs/case-study-report/`, and `openspec validate --strict` must pass on the synced spec. Then push, open the PR and merge (the PR workflow of the earlier changes).
- A regenerated results directory invalidates the committed report: `report --check` fails on its provenance cells until a new report is written and checked.
- Next changes, each its own proposal: the CN / LMCI / AD arm, the other export variants (all 245 NMR columns first), the rank sweep. Each extends the report's sections and re-issues the report. The cluster run waits on the deploy key (constraint 7).
