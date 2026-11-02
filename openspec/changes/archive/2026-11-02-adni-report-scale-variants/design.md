# Design

## Context

See `proposal.md` for the motivation and scope, and `specs/case-study-report/spec.md` for the requirements. This is the state that shapes the approach.

- **The report step today** (changes `adni-report`, `adni-report-variants`, `adni-report-stage-arm`, `adni-report-rank-sweep` and `adni-report-nmr-all-columns`, `data.py`):
  - `REPORT_INPUT_FILES`, `_REPORT_MANIFESTS`, `_report_dirs`, `_load_report_inputs` (identity, reported-run and chain gates) and the summary, provenance, findings and reproduction loops all iterate `REPORT_EXPORT_VARIANTS`.
  - `_export_sensitivity_section` groups the pinned variants by rule set (`_export_variant_groups`).
    - The first group keeps the 2026-10-31 titles.
    - A later group's titles are prefixed by its variant names joined with ", ", then a colon. The noun is plural for several variants ("primary and variants", "Exports against the predeclared counts").
  - Every variant-specific word comes from `_variant_words`. For a variant with hook `scale` it gives "the scale of both blocks" (`changes`) and "the membership of both blocks" (`kept`).
  - The group lead cites a rule set's "read against the primary only" rule through `_GROUP_PRIMARY_ONLY_RULE = {"NMR_MEMBERSHIP_READING_RULES": 8}`. The clause is singular: "the variant is read against the primary only".
  - The reading-rules section prints one list per group's rule set, led by `_export_variant_rules_heading(<first variant of the group>)[-1]`.
  - The summary prints one paragraph per group. The variants are joined with ", " and the ranks with " and ".
  - `_check_report_layout` compares a report's sections with `REPORT_SECTIONS`, then its ``Export variant `<name>` `` headings with `REPORT_EXPORT_VARIANTS`.
- **The scale variants' committed outputs** (change `adni-scale-variants`, written at 237e916 on nixos-home, pinned):
  - **Ranks.** The CV selected 7 for `raw_scale`, 8 for `log2_plus_one` and 7 for `glog`, each with 5 repeats.
  - **Statuses.** All nine are `same`. No statistic is rejected in any variant.
  - **Analysis and comparison findings.** One each for `raw_scale` and `glog` (the rank), none for `log2_plus_one`.
  - **Diagnostics findings.** Each variant's diagnostics record four flagged-component findings and the not-the-primary note.
  - **Export manifests.** None records a deviation from `EXPORT_VARIANT_EXPECTED_COUNTS`.
  - **Expected counts.** The three entries share `_SCALE_VARIANT_SHARED_COUNTS`, then hold per variant `shape`, `spectrum` and `phase_offset`. `log2_plus_one` alone holds `scale.median_below_offset`. None holds `diagnostics`.
- **The spike for this proposal** was read-only. It used a scratch copy of `src/` with the pin set to the six variants, on the committed tree at bf3f773:
  - **Loader.** It completed with 145 inputs, 45 manifests and 99 aggregate files checked against `outputs`.
  - **Chain.** 255 links held. The 66 new ones are 22 per scale variant: 4 for the export, 8 for the analysis, 6 for the comparison and 4 for the diagnostics.
  - **Manifests.** All 45 record the same versions. Numerics are pinned in 40 and absent in the same five as before, and no revision is dirty.
  - **Size.** The rendered report had 106 tables, 7182 cells and 323676 bytes.
  - **Against the 2026-11-02 report** (89 tables, 5418 cells, 241526 bytes), parsed with `parse_report`:
    - every table of the old report exists in the new one with the same key and columns;
    - the four provenance tables gain rows, the old rows a subsequence in order: "Versions per step" (33 → 45), "Revisions and numerics per step" (33 → 45), "Inputs" (106 → 145) and "Chain links checked" (189 → 255);
    - every other table is equal;
    - every non-table line appears in order, except five: the title, the preamble, the summary's diagnostics paragraph, the export section's lead and the lead of the CLI equivalents.
  - **Defects.** The proposal lists three: the group lead lacks scale rule 8, the summary's ranks read "… and … and …", and the preamble lacks this change.
  - **Variant gate.** On the 2026-11-02 report it stopped with absent `'raw_scale', 'log2_plus_one', 'glog'`, no extra, and the `git log` command, which names 28e0d48.
- **The five committed reports:**
  - `reports/motco-adni-2026-11-02.md`: thirteen sections and three export variants, committed at 28e0d48;
  - `reports/motco-adni-2026-10-31.md`: thirteen sections and two variants, committed at 13ce7c8;
  - `reports/motco-adni-2026-10-30.md`: twelve sections, committed at 2e4a3e1;
  - `reports/motco-adni-2026-10-29.md`: eleven sections, committed at c94f5e7;
  - `reports/motco-adni-2026-10-28.md`: ten sections, committed at 36c9cc8.

  Today is 2026-11-02, so a report written today would take the name of an existing file: `REPORT_NAME` (`_REPORT_NAME_RE`) admits one name per day, and `_newest_report` orders the reports by that date alone.

## Goals / Non-Goals

**Goals:**
- One report that carries the primary and every predeclared sensitivity, the three scale variants included. Each is read beside the primary under its own rule set, and the group lead states scale rule 8 where the three share tables.
- The run-handling and membership groups keep the 2026-11-02 text and tables, so a reader can diff the two reports.
- No change to the loader, the gates, the chain, the earlier-layout gate or any step's output.

**Non-Goals:**
- A registry of variant groups or of title prefixes. The groups follow from `EXPORT_VARIANT_RULE_SETS` and the pin, and the prefix from the group's variant names.
- A sentence that explains the `n/a` cells of the scale counts table (Risks).
- Showing the scale variants' diagnostics counts beside predeclared ones. Their entries hold no `diagnostics` key, and `axis-diagnostics` compares the rank-independent keys.

## Decisions

**D1. Coverage is the pin, and the loader is unchanged.**
- `REPORT_EXPORT_VARIANTS` becomes the six registered variants in registry order. The import-time assertion keeps it a subsequence of `EXPORT_VARIANTS`.
- `REPORT_INPUT_FILES` follows from the pin: 39 more files, 145 in all, with no bridge role for hook `scale`.
- The loader, gates and chain already iterate the pin, and the spike ran them unchanged on the committed tree (Context).
- *Alternative:* pin one scale variant per change. Rejected: the three share one rule set and one change, and pinning them together issues one report instead of three.

**D2. The scale group is one group of shared tables, prefixed by its variant names** (the user's choices for this proposal).
- **Grouping.** `_export_variant_groups` puts the three in the third group, by their shared rule set `SCALE_VARIANT_READING_RULES`, after the run-handling and membership groups.
- **Shared tables.** Each holds the primary row first and one row (or column) per scale variant in registry order. The rank section uses the same layout for six forced ranks under sweep rule 8.
- **Titles.**
  - The existing rule for a later group gives `raw_scale, log2_plus_one, glog: ` before:
    - "Statistics: primary and variants";
    - "Latent space: primary and variants";
    - "Run offset per export";
    - "Exports against the predeclared counts";
    - "First component against phase".
  - The per-variant headings keep their form: ``Status per statistic: `<v>` ``, ``Export variant `<v>` `` and `<v>: Flagged latent components` and the rest.
  - No title changes in the first two groups, and every title in the section stays unique.
- *Alternative:* one sub-group per scale variant, each table holding the primary and one variant. Declined by the user. It reads scale rule 8 most strictly, but it repeats the primary's rows three more times and adds about 15 tables. The rank section already shows that a shared table, under a lead that cites the primary-only rule, compares no two of its analyses.
- *Alternative:* a rule-set prefix (`scale variants: `). Declined by the user. It needs a new convention, and the titles would no longer name the variants their tables hold.

**D3. The group lead cites scale rule 8.**
- **The map.** `_GROUP_PRIMARY_ONLY_RULE` gains `"SCALE_VARIANT_READING_RULES": 8`. Scale rule 8 reads a scale variant against the primary only, never against another scale variant, another export variant, an arm or a rank.
- **The clause** depends on the group's size:
  - one variant: "the variant is read against the primary only ({cite} N)", the membership group's clause byte for byte;
  - several variants: "each variant is read against the primary only, never against another variant of the group ({cite} N)".

  The words come from the group's size and `_variant_words`, as the rest of the lead does. No scale-specific literal enters the renderer.
- **Not cited elsewhere.** The summary's group paragraph and the `angle` paragraphs do not cite rule 8, as for the membership group. Each `angle` paragraph and status bullet already names the primary and one variant.

**D4. The summary joins the ranks as a list.**
- `render_report` joins the group's ranks with `_and_join` instead of `" and ".join`. For two variants the text is unchanged ("6 (`nist_bridge`) and 4 (`per_run_standardized`)"). For three it reads "7 (`raw_scale`), 8 (`log2_plus_one`) and 7 (`glog`)".
- The variant list before it stays joined with ", " ("`raw_scale`, `log2_plus_one`, `glog`"). `_and_join` there would rewrite the run-handling paragraph, which D7 keeps byte-unchanged.

**D5. The scale counts table takes its keys from the three entries.**
- **Keys.** The existing rule takes the keys of the group's `EXPORT_VARIANT_EXPECTED_COUNTS` entries in registry order, without `analysis`, `phase_offset` and `diagnostics`.
- **Columns.** Observed and expected per variant: six value columns.
- **Rows.** The shared keys come first, then `shape.*`, `spectrum.*` and `scale.median_below_offset.*`. The last two rows hold values for `log2_plus_one` only, and `n/a` for `raw_scale` and `glog`, whose entries have no such key. No row is all `n/a`.

**D6. Seven rule lists.**
- The reading-rules section prints `READING_RULES`, `LATENT_SENSITIVITY_READING_RULES`, then one list per group's rule set: `EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES` and `SCALE_VARIANT_READING_RULES`. `STAGE_SENSITIVITY_READING_RULES` and `RANK_SENSITIVITY_READING_RULES` follow.
- The scale list is led by `_export_variant_rules_heading("raw_scale")[-1]`, the line the three variants' `summary.md`, `export_sensitivity.md` and `diagnostics.md` print.
- The renderer already does this for any group. Only the spec's count changes.

**D7. Byte and string gates.**
- **Against the 2026-11-02 report.** Both reports are parsed with `parse_report`:
  - **Tables.** Every table of the 2026-11-02 report must exist in the new one with the same key, columns and rows. The four provenance tables of Context are the exception: they gain the scale variants' rows, and their old rows must be a subsequence in order.
  - **Other lines.** Every non-table line must appear in the new report in order. The exceptions are the title line, the preamble (D8), the summary's diagnostics paragraph, the export section's lead and the lead of the CLI equivalents (15 analyses).
  - **Recording.** The apply records the exact list of changed lines in `tasks.md`.
- **Against the variants' documents.** Per scale variant, these must be string-equal to its committed `comparison/export_sensitivity.md`:
  - its status bullets;
  - its "Export variant" bullets;
  - the primary's and its own column of the shared latent-space table;
  - the lead line of its rules.
- **Shared renderers.** No function that writes a step's output changes. The variants' `summary.md`, `export_sensitivity.md` and `diagnostics.md` are not regenerated.

**D8. The preamble names this change.** The change list becomes "(changes `adni-report`, `adni-report-variants`, `adni-report-stage-arm`, `adni-report-rank-sweep`, `adni-report-nmr-all-columns` and `adni-report-scale-variants`)". Its group clauses already name `SCALE_VARIANT_READING_RULES`.

**D9. Verification.** It runs on any machine with the Nix shell and the committed tree, all in the session scratchpad.
- **Loader.** 145 files, each hash equal to `sha256sum`; 99 checked against `outputs`; 45 manifests; 255 links, all `ok`; no uncovered-variant progress line.
- **Gates of D7.**
- **Values.** An independent script reads the scratch report's scale-group tables and, with `json`, `csv` and `hashlib`, the sources. It compares every value at the printed digits:
  - statistics against each `export_sensitivity.csv`, with the rank against `latent.selected_lv`;
  - latent space against the CSVs and `config_spectrum`;
  - run offsets and counts against the export manifests (`counts`, `expected`);
  - diagnostics against each variant's CSVs;
  - the 39 new input hashes against `hashlib` and the recording manifests.
- **Separation.** No table of the export-sensitivity section holds variants of two groups.
  - Every table of the scale group holds the primary and scale variants only.
  - Every line that names two scale variants is listed and must be a listing: the group lead, the summary paragraph, the section lead, the preamble, the reproduction lists, the provenance and findings entries, and the shared tables' titles. None compares two variants.
- **Rules.** The seven lists are string-equal to the constants, item by item. The scale group's lead cites "scale rule 8" and the membership group's lead is byte-unchanged.
- **Failure cases.** Each runs on an edited scratch copy of the tracked `results/`. In every case nothing is written, the exit code is 1, and the copy is otherwise unchanged:
  - `glog`'s `comparison/export_sensitivity.csv` absent;
  - one byte of `raw_scale`'s `export_sensitivity.md` changed;
  - the `log2_plus_one` directory holding `glog`'s outputs;
  - `EXPORT_VARIANTS["glog"]["setting"]` patched in-process;
  - `raw_scale`'s `result.json` with `measurement.n_jobs` 4, its manifest's hash updated;
  - `log2_plus_one`'s analysis manifest's `numerics.pinned` false;
  - `glog`'s export manifest's `reference.manifest.sha256` edited;
  - stale diagnostics, from `raw_scale`'s analysis manifest rewritten with a key reordered.
- **Checks.**
  - `--check` passes on a fresh scratch report.
  - On the 2026-11-02 report it stops at the variant gate, with the three scale variants absent. On the 2026-10-31 report it stops there with four absent. The three older reports stop at the section gate.
  - In a worktree of 28e0d48 the 2026-11-02 report passes its own check.
  - With a scratch copy of the constants whose pin holds the first three variants, `report` reads 106 files, prints one uncovered-variant line per scale variant, and no body line names a scale variant.
- **Determinism.** Two `--force` runs are byte-identical. A run to another date differs in the title line only.
- **Audit.** An audit hook over `run_report` lists 145 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none ignored by git.

**D10. The report written at the apply, under a same-day name** (the user's choice on 2026-11-02, after the implementation was committed).
- **Date.** The report is written on 2026-11-02, the day the change is implemented, on the clean tree at the commit of the naming change (D11).
- **Name.** `reports/motco-adni-2026-11-02-2.md`, the day's second report, passed with `--out`. This reverses the user's rule of 2026-10-29 against same-day ordinal names. `reports/motco-adni-2026-11-02.md` is never overwritten, and no `--force` is used on a committed report.
- **Record.** Its counts (sections, tables, cells, links, bytes) go in `tasks.md`.
- *Alternatives declined by the user:*
  - wait for 2026-11-03 and name the report by that day, the rule of the previous report changes;
  - merge without the report and write it the next day as a follow-up commit, leaving `main` overnight with a newest report that `--check` stops on as an earlier layout;
  - replace the 2026-11-02 report with `--force`. That rewrites a committed report, which the variant gate, the docs and the spec name as an earlier layout that checks at 28e0d48.

**D11. A later report of a day is named with an ordinal.**
- **Name.** `motco-adni-<date>-<n>.md` (`REPORT_NAME_SAME_DAY`, a convention), n an integer of 2 or more without a leading zero. A name without an ordinal is the day's first report, so every committed name stays valid and checks as before. `-1` is refused: the first report carries no ordinal.
- **Title.** The title line carries the ordinal: `… — 2026-11-02, report 2`. The date and the ordinal appear in the name and the title only, so the body still depends on the inputs and the name only.
- **Selection.** `--check` without `--out` reads the newest report by its date, then by its ordinal; a name without one counts as 1.
- **Write mode.** Without `--out` it still uses today's name without an ordinal. When that file exists and `--force` is not given, it stops naming the next free same-day name to pass with `--out`. No ordinal is chosen automatically, so a rerun never adds a report silently.
- **Body.** The reproduction sentence "`report --check` reads the newest `reports/motco-adni-<date>.md`" stays as written, so the five changed lines of D7 hold. The rule for a same-day name is stated in `README.md`, `AGENTS.md` and the `--out` help.
- **Constant.** `REPORT_NAME_SAME_DAY = "motco-adni-{date}-{n}.md"` is tied to `REPORT_NAME` by an import-time assertion. It is a convention, not a scientific constant.
- **Verification.** Accepted and refused names (`-2` and `-10`; `-1`, `-02`, `-0` and a name without a date); the title of a `-2` render and its byte-equality with the scratch render of task 2.5 apart from line 1; the newest selection among the five committed reports and a `-2` render; the existing-file message (`-2`, then `-3`); the earlier-layout gates of task 3.1 unchanged.
- *Alternatives:* a letter suffix (`2026-11-02b`), which runs out after `z` and reads as part of the date; a time in the name, which makes the name depend on the run rather than the day.

## Risks / Trade-offs

- **[The shared tables invite reading one scale variant against another]** Three variants side by side make a comparison between them easy to draw. → Mitigations:
  - The group lead cites scale rule 8 (D3), and the rule is printed verbatim in section 12.
  - Each `angle` paragraph and status bullet names the primary and one variant.
  - No sentence of the report reads two variants against each other (D9).

  The rank sweep has used this layout under sweep rule 8 since `adni-report-rank-sweep`.
- **[Long titles]** The prefix `raw_scale, log2_plus_one, glog: ` is 33 characters. → Accepted: the titles stay unique keys for `report --check`, and each names the variants its table holds (D2).
- **[`n/a` cells in the counts table]** `scale.median_below_offset.*` prints `n/a` for `raw_scale` and `glog`, which have no offset to compare. → Accepted: the table copies the predeclared keys, and the variants' "Export variant" lines say what the offset is. An explanatory sentence would change the paragraph the first two groups share (Non-Goals).
- **[`_GROUP_PRIMARY_ONLY_RULE` duplicates a rule number]** A renumbered `SCALE_VARIANT_READING_RULES` would leave it stale. → The rules are decided constants that no result changes. The string gate of D9 compares the lead's citation with the rule list.
- **[Report length]** It grows from 241526 bytes to about 324 KB. → Most of the growth is the three variants' diagnostics tables, the 66 chain links and the 39 inputs. Their `stage_means.csv` and `pls_loadings.csv` stay quoted by hash.
- **[Two reports carry the date 2026-11-02]** → The ordinal is in the name and the title line (D11), `--check` reads the `-2` report as the newest, and the 2026-11-02 report stays an earlier layout that checks at 28e0d48.
- **[The 2026-11-02 report is not checkable by the new code]** → The variant gate says so and names 28e0d48, where it checks (D9).

## Migration Plan

1. Branch `adni-report-scale-variants` from `main` (bf3f773).
2. Extend the pin, write the plural primary-only clause, the rank list and the preamble, and verify on the committed tree as D7 and D9 describe.
3. Update `README.md`, `AGENTS.md` and the docstrings, then commit the implementation.
4. Implement and verify the same-day name (D11), update the docs, and commit. Then write `reports/motco-adni-2026-11-02-2.md` on the clean tree at that commit (D10), run `report --check`, and commit the report alone.
5. Archive the change on the branch, then push, open the PR and merge.

Rollback: revert the branch. The committed results are untouched, and the five earlier reports stay checkable at their own revisions.
