# Design

## Context

See `proposal.md` for the motivation and scope, and `specs/case-study-report/spec.md` for the requirements. This is the state that shapes the approach.

- **The report step today** (changes `adni-report`, `adni-report-variants`, `adni-report-stage-arm`, `adni-report-rank-sweep`; the pin of `adni-nmr-all-columns`, `data.py`):
  - `REPORT_INPUT_FILES`, `_REPORT_MANIFESTS`, `_report_dirs`, `_load_report_inputs` (identity, reported-run and chain gates) and the summary, provenance, findings and reproduction loops all iterate `REPORT_EXPORT_VARIANTS`.
  - `_export_sensitivity_section` writes one set of shared tables for every pinned variant. Its lead, its shared-and-differs sentence, its `angle` paragraphs and its diagnostics paragraphs carry p180 wording as literals: `EXPORT_VARIANT_READING_RULES`, `variant rule N`, "run-handling dependence", "the NMR block", "the p180 values".
  - The summary's variant paragraph carries the same literals ("each changes the p180 values only", `differs (run-handling dependence)`).
  - The reading-rules section prints `EXPORT_VARIANT_READING_RULES` once, led by `_export_variant_rules_heading(REPORT_EXPORT_VARIANTS[0])`.
  - The counts table "Variant exports against the predeclared counts" flattens each pinned variant's `EXPORT_VARIANT_EXPECTED_COUNTS` entry without `analysis` and `phase_offset`.
  - `_check_report_layout` compares level-2 headings with `REPORT_SECTIONS` only.
- **The variant's words already exist.** `_variant_words(variant)` (change `adni-nmr-all-columns`) returns, from `EXPORT_VARIANT_RULE_SETS` and the variant's block and hook:
  - `rules`, `change`, `cite`, `dependence`, `source`, `heading`, `reader`;
  - `rule_tuple`, `differs`;
  - `kept` (the blocks it keeps), `changes`, `does`, `whose`.

  For a p180 variant these give the committed p180 words: `kept` is "the NMR block" and `changes` is "the p180 values". `_export_variant_status_line`, `_export_variant_lines` and `_export_variant_rules_heading` take the variant and are string-equal across `summary.md`, `export_sensitivity.md` and the report.
- **The spike for this proposal** was read-only. It used a scratch copy of `src/` with the pin set to the three variants, on the committed tree at 98d136c:
  - the loader completed with 106 inputs, 33 manifests and 72 aggregate files checked against `outputs`;
  - 189 chain links held. The 22 new ones are 4 for the variant export (the two clean manifests, the cohort manifest, the primary export as `reference`), 8 for its analysis, 6 for the comparison and 4 for its diagnostics;
  - all 33 manifests record the same versions, numerics are pinned in 28 and absent in the same five as before, and no revision is dirty.

  The rendered report had 84 tables, 5454 cells and 234751 bytes. It showed the false p180 sentences listed in the proposal and 13 all-`n/a` `diagnostics.*` rows in the counts table.
- **The variant's committed outputs:**
  - **Rank.** The CV selected 7 (`cv`, 5 repeats).
  - **Statuses.** `delta` is `differs (feature-membership dependence)`; `angle` and `shape` are `same`.
  - **Analysis and comparison findings.** Each manifest records two: the rank and `delta`.
  - **Diagnostics findings.** Four flagged components (`pls_0`, `pls_1`, `pls_4`, `pls_5`) and the not-the-primary note.
  - **`export_sensitivity.md`.** It prints a "Latent space" table with the six quantities the report's latent-space table uses, and an "Export variant" block written by `_export_variant_lines`.
- **The four committed reports:**
  - `reports/motco-adni-2026-10-31.md`: thirteen sections and two export variants, committed at 13ce7c8;
  - `reports/motco-adni-2026-10-30.md`: twelve sections, committed at 2e4a3e1;
  - `reports/motco-adni-2026-10-29.md`: eleven sections, committed at c94f5e7;
  - `reports/motco-adni-2026-10-28.md`: ten sections, committed at 36c9cc8.

  Each lists its export variants through its level-3 headings ``Export variant `<name>` `` (none in the 2026-10-28 report). Today is 2026-10-31, so a report written today would take the name of an existing file.

## Goals / Non-Goals

**Goals:**
- One report that carries the primary and every predeclared sensitivity that has run, `nmr_all_columns` included. Each is read beside the primary under its own rule set, and no table puts the membership variant beside a p180 variant.
- The run-handling variants' part of the report keeps the 2026-10-31 text and tables, so a reader can diff the two reports.
- A report written under an earlier pin stops `--check` as an earlier layout, naming the revision where it checks.
- No change to the loader, the gates, the chain or any step's output.

**Non-Goals:**
- A registry of variant groups. The groups follow from `EXPORT_VARIANT_RULE_SETS` and the pin, and no new constant names them.
- Retitling the run-handling group's tables to make the groups symmetric (Risks).
- Showing the variants' diagnostics counts beside their predeclared ones. `axis-diagnostics` compares them, and a deviation reaches "Findings", as for every other diagnostics run.
- The variant's per-statistic reading lines (proposal, out of scope).

## Decisions

**D1. Coverage is the pin, and the loader is unchanged.**
- `REPORT_EXPORT_VARIANTS` gains `nmr_all_columns`. The import-time assertion keeps it a subsequence of `EXPORT_VARIANTS`.
- `REPORT_INPUT_FILES` follows from the pin: 13 more roles' files, 106 in all, with no bridge role for hook `membership`.
- The loader, gates and chain already iterate the pin, and the spike ran them unchanged on the committed tree (Context).
- *Alternative:* a separate flag or directory for the membership variant. Rejected: it is a variant of `export-sensitivity`, under `--export-sensitivity-dir`, like the others.

**D2. "Export sensitivity" holds one group per rule set** (the user's choice for this proposal).
- **Grouping.** The pinned variants are grouped by `EXPORT_VARIANT_RULE_SETS[v]["rules"]`, in the order each rule set first appears in the registry:
  - group 1: `nist_bridge` and `per_run_standardized` (`EXPORT_VARIANT_READING_RULES`);
  - group 2: `nmr_all_columns` (`NMR_MEMBERSHIP_READING_RULES`).
- **Section lead.** It is written when the pin holds more than one group. It names the primary with its `result.json` hash, as now, and the groups with their variants and rule sets (section 12). It says that each group's tables hold the primary and that group's variants only, the primary row first with its status the result.
- **Each group's content**, in the 2026-10-31 order:
  - its lead;
  - the statistics table;
  - one `angle` paragraph per variant;
  - one "Status per statistic" heading per variant, with its bullets;
  - the latent-space table;
  - the shared-and-differs sentence;
  - the run-offset table;
  - the counts table;
  - one "Export variant" block per variant, with the bridge tables for hook `factors`;
  - one diagnostics paragraph and block per variant;
  - the first-component table;
  - one `cli_equivalent` per variant.

  Every table holds the primary and the group's variants only.
- **Titles.**
  - Group 1 keeps the 2026-10-31 titles: "Statistics: primary and variants", "Latent space: primary and variants", "Run offset per export", "Variant exports against the predeclared counts" and "First component against phase".
  - A later group's tables are prefixed by its variant names and a colon, with the singular for one variant: "nmr_all_columns: Statistics: primary and variant", "nmr_all_columns: Latent space: primary and variant", "nmr_all_columns: Run offset per export", "nmr_all_columns: Export against the predeclared counts", "nmr_all_columns: First component against phase".
  - The per-variant headings stay as they are: ``Status per statistic: `<v>` ``, ``Export variant `<v>` ``, and `<v>: Flagged latent components` and the rest of the diagnostics.
  - Titles are unique within the section, as `report --check` keys tables by `"<section> › <title>"`.
- *Alternative:* `nmr_all_columns` as one more row and column of the shared tables. Rejected by the user. Membership rule 8 reads the variant against the primary only, and a shared table invites reading it against the p180 variants. Groups also give the later scale variants a place.
- *Alternative:* a fourteenth section. Rejected: one step's variants would be split across sections, and each later rule set would need another section.

**D3. Every variant-specific word comes from `_variant_words`.**
- **Group lead:**
  - the group's variants, each with its change, setting and directory, as now;
  - "Every other export and analysis setting is the primary's.";
  - "Every table of this group quotes {a variant | the variant} and is read under `READING_RULES` and `{rules}` (section 12): the primary row comes first and its status is the result; {a variant | the variant} never replaces it ({cite} 1), and a status that differs is {dependence} ({cite} 2)";
  - for a rule set that reads its variant against the primary only, the clause "and the variant is read against the primary only ({cite} N)". `_GROUP_PRIMARY_ONLY_RULE`, a module constant of `data.py`, maps `NMR_MEMBERSHIP_READING_RULES` to 8. `EXPORT_VARIANT_READING_RULES` has no such rule; its rule 5 defines how a difference between its two variants is read.
- **Shared-and-differs sentence:** "{Each variant | The variant} shares with the primary the cleaned tables, the participants, {kept}, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations; it differs only in {changes} ({cite} 2)." For group 1 this is the 2026-10-31 sentence byte for byte.
- **`angle` paragraph:** `(reading rule 2, {cite} 3)` and `reported, not ranked ({cite} 3)`.
- **Diagnostics paragraph:** `({cite} 7)`. Rule 7 has the same role in both sets.
- **Unchanged and called as they are:** the status lines (`_export_variant_status_line`), the "Export variant" blocks (`_export_variant_lines`) and the rules' lead line (`_export_variant_rules_heading(v)[-1]`).
- **Summary.** One paragraph per group, then each variant's rank line and status bullets:
  - "The predeclared export variant(s) … (`EXPORT_VARIANTS`, change(s) `…`: {each changes | it changes} {changes} only, every other export and analysis setting the primary's; section 8) selected rank(s) …";
  - "Status per statistic (`same` when …, else `{differs}`; the primary's status is the result either way), read under `READING_RULES` and `{rules}`:".

  Each change name is in its own backticks, which avoids the spike's `adni-nist-bridge, adni-nmr-all-columns` in one span. The group-1 paragraph is the 2026-10-31 one.
- **Preamble.** It names this change and replaces "each export variant under `READING_RULES` and `EXPORT_VARIANT_READING_RULES`" with one clause per group naming its rule set.

**D4. The counts table drops the steps' own comparisons.**
- **Keys.** A group's counts table takes the keys of its variants' `EXPORT_VARIANT_EXPECTED_COUNTS` entries in registry order, without `analysis`, `phase_offset` and now `diagnostics`.
  - `export-sensitivity` compares `analysis`.
  - The run-offset table shows `phase_offset`.
  - `axis-diagnostics` compares `diagnostics` (`EXPORT_VARIANT_EXPECTED_COUNTS[<variant>]["diagnostics"]`).
- **Effect on group 1.** None: its entries have no `diagnostics` key.
- **Group 2's table** holds `nmr_all_columns` and `nmr_all_columns expected`. Its rows include `features.nmr.derived_kept.*`, `joint_features`, `shape.nmr.*`, `unchanged_equal_primary.p180.csv` and `rule_columns_equal_primary`.

**D5. Six rule lists, one per rule set.**
- **Order.** The reading-rules section prints:
  1. `READING_RULES`;
  2. `LATENT_SENSITIVITY_READING_RULES`;
  3. one list per rule set of the pinned variants, in group order: `EXPORT_VARIANT_READING_RULES`, then `NMR_MEMBERSHIP_READING_RULES`;
  4. `STAGE_SENSITIVITY_READING_RULES`;
  5. `RANK_SENSITIVITY_READING_RULES`.
- **Each list.** Under a level-3 heading with the constant's name, led by `_export_variant_rules_heading(<first variant of the group>)[-1]`. For the membership list that is the line the variant's `summary.md`, `export_sensitivity.md` and `diagnostics.md` print.
- **Placement.** The rule sets stay beside the export-sensitivity section they serve, in the report's section order, not in the order the changes were decided.

**D6. The earlier-layout gate compares export variants.**
- **The comparison.** `_check_report_layout` keeps its section comparison and message. When the sections match, it reads the report's export variants from the level-3 headings ``Export variant `<name>` `` of the "Export sensitivity" section, in order, through `parse_report`'s section lines. It compares them with `REPORT_EXPORT_VARIANTS`.
- **The stop.** A difference stops the check before any input gate. The message has the form of the section message: "written by an earlier layout of `report`: its export variants are not REPORT_EXPORT_VARIANTS (absent: …; extra: …[; the order differs])". It then gives the `git log` and worktree instructions, says no cell was compared and that nothing was written.
- **Effect.** The 2026-10-31 report stops there, with absent 'nmr_all_columns' and its revision 13ce7c8. The three older reports stop on their sections first, unchanged.
- **Why the heading.** It is the one line per variant every report since `adni-report-variants` writes, and the renderer's own output. The provenance's role names would also work, but they sit in table cells that a later change could reorder.
- *Alternative:* key the gate by a layout version written in the report. Rejected: the report body holds no metadata of the run (determinism), and the headings already carry the coverage.

**D7. Byte and string gates.**
- **Against the 2026-10-31 report.** Both reports are parsed with `parse_report`:
  - **Tables.** Every table of the 2026-10-31 report must exist in the new one with the same key, the same columns and the same rows. The exceptions are the four provenance tables "Versions per step", "Revisions and numerics per step", "Inputs" and "Chain links checked". These gain the variant's rows, and their other rows must be equal and in order.
  - **Other lines.** Every non-table line of the 2026-10-31 report must appear in the new one, in order. The exceptions are the title line, the preamble, the export-sensitivity section lead (now group 1's lead), the summary's diagnostics paragraph (which adds the variant) and the lead of the CLI equivalents (12 analyses).
  - **Recording.** The apply records the exact list of changed lines in `tasks.md`.
- **Against the variant's documents.** The membership group's status bullets, its "Export variant" bullets and every row of its latent-space table must be string-equal to the committed `results/motco_export_sensitivity/nmr_all_columns/comparison/export_sensitivity.md`. Its rules' lead line must equal that document's.
- **Shared renderers.** No function that writes a step's output changes. The variant's `summary.md`, `export_sensitivity.md` and `diagnostics.md` are not regenerated.

**D8. Verification.** It runs on any machine with the Nix shell and the committed tree, all in the session scratchpad.
- **Loader.** 106 files, each hash equal to `sha256sum`; 72 checked against `outputs`; 33 manifests; 189 links, all `ok`; no uncovered-variant progress line.
- **Gates of D7.**
- **Values.** An independent script reads the scratch report's membership-group tables and, with `json`, `csv` and `hashlib`, the sources. It compares every value at the printed digits:
  - statistics against `export_sensitivity.csv`, with the rank against `latent.selected_lv`;
  - latent space against the CSV and `config_spectrum`;
  - run offsets and counts against the two export manifests;
  - diagnostics against the variant's CSVs;
  - the 13 new input hashes against `hashlib` and the recording manifests.
- **Separation.** No table of the export-sensitivity section holds a group-1 variant together with `nmr_all_columns`.
  - Every line that names `nmr_all_columns` with another sensitivity is listed, and each must be a listing. The expected ones are the summary's diagnostics paragraph, the preamble, the section lead, the reproduction lists and the provenance and findings entries.
- **Rules.** The six lists are string-equal to the constants, item by item.
- **Failure cases.** Each runs on an edited scratch copy of the tracked `results/`. In every case nothing is written, the exit code is 1, and the copy is otherwise unchanged:
  - the variant's `diagnostics_manifest.json` absent;
  - one byte of its `export_sensitivity.csv` changed;
  - the `nmr_all_columns` directory holding `per_run_standardized`'s outputs;
  - `EXPORT_VARIANTS["nmr_all_columns"]["setting"]` patched in-process;
  - its `result.json` with `measurement.n_jobs` 4, its manifest's hash updated;
  - its analysis manifest's `numerics.pinned` false;
  - its export manifest's `reference.manifest.sha256` edited;
  - stale diagnostics, from its analysis manifest rewritten with a key reordered.
- **Checks.**
  - `--check` passes on a fresh scratch report.
  - On the 2026-10-31 report it stops at the variant gate, and on the three older reports at the section gate.
  - In a worktree of 13ce7c8 the 2026-10-31 report passes its own check.
  - With a scratch copy of the constants whose pin holds the two p180 variants, `report` reads 93 files, prints the uncovered-variant line, and no body line names `nmr_all_columns`.
- **Determinism.** Two `--force` runs are byte-identical. A run to another date differs in the title line only.
- **Audit.** An audit hook over `run_report` lists 106 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git.

**D9. The report written at the apply.** This follows the user's rule for `adni-report-stage-arm` and `adni-report-rank-sweep`.
- **Date.** The report is written on the clean tree at the implementing commit, on 2026-11-01 or later, and named by the day it is written: `report` without `--out` uses today's date.
- **Name.** `reports/motco-adni-2026-10-31.md` is never overwritten, and no `--force` is used on a committed report.
- **Record.** Its counts (sections, tables, cells, links, bytes) go in `tasks.md`.

## Risks / Trade-offs

- **[The primary's rows repeat in each group]** The statistics, latent-space, run-offset and first-component tables of group 2 repeat the primary's values from group 1. → Accepted: each group is read against the primary only, and repeating the primary keeps each group's tables self-contained. The values are copied from the same sources, and the value checker compares both.
- **[The titles are not symmetric]** Group 1's tables are unprefixed and group 2's carry `nmr_all_columns: `. → Accepted for continuity with the 2026-10-31 report (D7). The section lead names both groups, and every group-2 title names its variant. A later change that pins a group of several variants may retitle its own group.
- **[The variant gate depends on a heading]** A later change that renames ``Export variant `<v>` `` breaks the gate's reading of older reports. → The heading is the renderer's own, and the spec requirement names it. A change that renames it must keep the gate's reading.
- **[`_GROUP_PRIMARY_ONLY_RULE` duplicates a rule number]** A renumbered `NMR_MEMBERSHIP_READING_RULES` would leave it stale. → The rules are decided constants that no result changes. The string gate of D7 compares the group lead's citation with the rule list.
- **[Report length]** It grows from 207049 bytes to about 236 KB. → Most of the growth is the group's tables and diagnostics, the 22 chain links and the 13 inputs. The variant's `stage_means.csv` and `pls_loadings.csv` stay quoted by hash.
- **[The apply spans two days]** The report waits for 2026-11-01. → Accepted, as before. The implementation commit and every verification can be done before then.
- **[The 2026-10-31 report is not checkable by the new code]** → The variant gate says so and names 13ce7c8, where it checks (D6, D8).

## Migration Plan

1. Branch `adni-report-nmr-all-columns` from `main` (98d136c).
2. Extend the pin, and write the groups, the words, the counts-table keys, the rule lists and the variant gate. Verify on the committed tree as D7 and D8 describe.
3. Update `README.md`, `AGENTS.md` and the docstrings, then commit the implementation.
4. On 2026-11-01 or later, write `reports/motco-adni-<date>.md` on the clean tree at the implementing commit, run `report --check`, and commit the report alone.
5. Archive the change on the branch, then push, open the PR and merge.

Rollback: revert the branch. The committed results are untouched, and the four earlier reports stay checkable at their own revisions.
