# Proposal

## Why

The two predeclared export variants of `export-sensitivity` (change `adni-nist-bridge`, merged in PR #10) are run pinned and committed: `nist_bridge` (rank 6) and `per_run_standardized` (rank 4), each beside the primary (rank 8), with every status `same` and their own axis diagnostics. No report quotes them. The committed report `reports/motco-adni-2026-10-28.md` predates them, `REPORT_INPUT_FILES` does not name their files, and `EXPORT_VARIANT_READING_RULES` binds "every report that quotes a variant", a promise no report keeps yet. When `adni-nist-bridge` was decided, the user chose to cover both variants in a later report change. This is that change: it extends step 6 so that the report covers the primary, the latent arm and the export variants together, and it writes and checks the next report. Like the first report change, it reads committed aggregate files only, so it runs on any clone.

## What Changes

- **Inputs extended**, still committed aggregate files only. For every variant of `EXPORT_VARIANTS`, in registry order, under `results/motco_export_sensitivity/<variant>/`: the variant export's `motco_input/manifest.json`; the variant analysis' `result.json`, `analysis_manifest.json` and `summary.md`; the comparison's `export_sensitivity.csv`, `export_sensitivity.md` and `export_sensitivity_manifest.json`; the variant diagnostics' six files; for `nist_bridge`, `bridge/nist_bridge.csv`. That is 27 more files and 53 in all, with 17 manifests (9 now). No participant-level file is opened or required: the hashes of a variant's export CSVs, `latent_scores.csv` and `analysis_metadata.csv` are quoted from its manifests. Every registered variant is required, and no flag selects what is reported.
- **Gates extended**, all of them before anything is written, each naming the file or setting, both values and the command to rerun:
  - Every input is present.
  - Every aggregate file hashes to what its own manifest records. The bridge table is checked against the `bridge.table.sha256` of its variant's export manifest, the one place a manifest records it.
  - Each variant is the registered one: its export, analysis and comparison manifests name it, its export manifest's `variant` block equals its `EXPORT_VARIANTS` entry, its analysis records no latent adjustment, and its diagnostics record `is_primary` false and `export_variant` equal to its name.
  - Each variant analysis is a reported run (`n_jobs = REPORTED_N_JOBS` in manifest and record). Every `numerics` block is pinned, and all 17 manifests record the same MOTCO, scikit-learn and metabo_adni versions.
  - The chain holds from the clean and cohort manifests and the primary export, through each variant's export, analysis and comparison, to its diagnostics, with the bridge table as a link of the comparison.
- **The report gains a section**, "Export sensitivity", placed after "Latent-adjustment sensitivity". `REPORT_SECTIONS` grows from ten sections to eleven. The section holds:
  - The statistics table: the primary row, then one row per variant, read from `export_sensitivity.csv`, with a status per variant row. The primary's status is the result.
  - Each variant's rank, floor, eigengap and null summary beside `angle`.
  - The status sentences of `export_sensitivity.md`, produced by the code that writes that file, so the strings are equal.
  - The latent spaces side by side.
  - The run offset per block for the primary export and each variant export.
  - Each variant export's counts beside its predeclared `EXPORT_VARIANT_EXPECTED_COUNTS`.
  - The variant lines that `export_sensitivity.md` prints: the setting, the runs, the bridge summary and the offsets.
  - For `nist_bridge`: the bridged metabolites per kit beside the predeclared 102 / 24 / 7, and the seven unbridged metabolites with their valid and ISTD-flagged NIST replicates from `nist_bridge.csv`. The full table is quoted by hash.
  - Each variant's diagnostics, laid out as the arm's (flagged rows, components, block PCs), and each analysis' first component against `phase`.
  - Each variant analysis' `cli_equivalent`.
- **Other sections extended** from the same inputs:
  - Summary: each variant's rank and status lines, and its flagged components.
  - Provenance: the new manifests and inputs, the chain links, and the two QC archives and four NIST workbooks with their hashes beside the predeclared ones, as the `nist_bridge` export manifest records them.
  - Findings: every deviation and finding of the eight new manifests, copied verbatim.
  - Reading rules: `READING_RULES`, then `LATENT_SENSITIVITY_READING_RULES`, then `EXPORT_VARIANT_READING_RULES`, verbatim. `EXPORT_VARIANT_READING_RULES` is named beside every table that quotes a variant.
  - Reproduction: the `export-sensitivity` command (its `nist_bridge` variant needs the two archive symlinks in the data root) and the two variant `axis-diagnostics` commands.
- **Checking a report written by an earlier layout.** `report --check` on a report whose level-2 headings are not `REPORT_SECTIONS` stops before comparing. It names the report, the sections the report is missing or adds, and the command that finds the revision that committed the report, where that report checks. This replaces a long list of mismatches that would follow from the layout alone. The committed `reports/motco-adni-2026-10-28.md` stays in place, unchanged. Its 26 inputs are unchanged, and it checks at dd6585b.
- **Flags**: `--export-sensitivity-dir`, the root of `results/motco_export_sensitivity/`, read per variant through `EXPORT_SENSITIVITY_SUBDIRS`. `report` then has ten flags, each defaulting to the pipeline's directory.
- **Constants**: conventions only. `REPORT_INPUT_FILES` gains one role per variant subdirectory, built from `EXPORT_VARIANTS` and `EXPORT_SENSITIVITY_SUBDIRS`; the bridge role applies to variants with hook `factors`. `REPORT_SECTIONS` gains "Export sensitivity".
- **Shared sentences, bytes unchanged.** The report calls the existing `_export_variant_status_line`, `_export_variant_lines` and `_export_variant_rules_heading`. If the apply needs to move any of their code, two gates run on any clone: the committed `export_sensitivity.md` of both variants, re-rendered from the committed records and manifests, must keep the hashes their comparison manifests record, and the variants' `summary.md` must keep the hashes their analysis manifests record.
- **Docs.**
  - `README.md`: the `report` section's inputs, flags, gates, sections and check, and the quick start.
  - `AGENTS.md`: the status paragraph (the report now covers the variants), step 6 (53 inputs, eleven sections, ten flags, the chain's link count), and the Layout entries. "Flag and ask" is unchanged, since no constant is added.
  - The `constants.py` docstring and the `run_report` docstring.
- **The next report**, `reports/motco-adni-<date>.md` (the apply's date): written on the clean tree from the committed outputs, checked with `--check`, and committed alone.

Scientific constants introduced by this change: none. The report decides nothing. It quotes `READING_RULES`, `LATENT_SENSITIVITY_READING_RULES`, `EXPORT_VARIANT_READING_RULES`, `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE` and every setting by constant name from the manifests, and every number from the records.

Out of scope, each its own change:
- A reading of one variant against the other. Variant rule 5 is printed verbatim, but the report adds no status or sentence comparing `nist_bridge` with `per_run_standardized`: no renderer produces one, and the report adds no interpretive sentence of its own.
- The full per-metabolite bridge table (133 rows) printed in the report. The report quotes it by hash, as `export_sensitivity.md` does, and prints the seven unbridged rows.
- A rewrite of the 2026-10-28 report, or a check of it with the new code.
- Any change to the outputs of `clean`, `cohort`, `export`, `analyze`, `axis-diagnostics`, `latent-sensitivity` or `export-sensitivity`.
- The later registered sensitivities: the CN / LMCI / AD arm, the other export variants (all 245 NMR columns, the raw scale, `log2(x + 1)`, the generalized log) and the rank sweep. Each extends the report through its own proposal.
- Figures, HTML or PDF rendering; a written discussion of the results.
- The cluster run (constraint 7). The report reads committed files only and needs no cluster.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `case-study-report`: these requirements change:
  - the inputs (the variant files);
  - the hash check (the bridge table's record);
  - the chain (through each variant's diagnostics);
  - the reported-run gate (the variant analyses, and 17 manifests);
  - the content contract (the eleventh section);
  - every number pasted (the variant tables);
  - the interpretive sentences (the variant status lines);
  - the reading rules carried (a third list);
  - the check's report selection (the earlier-layout gate).

  One requirement is added: the variants are identified before reporting. `motco-export-sensitivity` ("Reading rules bind every reader of a variant") already binds every report that quotes a variant; this change fulfils it without changing its text.

## Impact

- `src/adni_sexdiff/constants.py`: the conventions `REPORT_INPUT_FILES` and `REPORT_SECTIONS` extended, and the docstring names the change. No scientific constant.
- `src/adni_sexdiff/data.py`:
  - `_report_dirs`, `_report_rerun`, `_REPORT_MANIFESTS` and `_load_report_inputs`: the variant roles, the bridge record, the identity, reported-run and chain gates.
  - `render_report`: the new section and the extended summary, provenance, reading rules and reproduction.
  - `check_report`: the earlier-layout gate.
  - The `run_report` signature and docstring.
  - No change to the export-sensitivity renderers' output bytes.
- `src/adni_sexdiff/cli.py`: the `--export-sensitivity-dir` flag.
- `reports/motco-adni-<date>.md`: added and committed. It is aggregate: every value in it is copied from a committed aggregate file or a constant. `reports/motco-adni-2026-10-28.md` is unchanged.
- `.gitignore`, `scripts/sync_results.sh`, `PARTICIPANT_LEVEL_PATTERNS`: unchanged; no participant-level output is added.
- Dependencies: none new. Compute: seconds, no MOTCO call, no numerics recorded.
- Machines: any machine with the Nix shell and the committed tree. No data root, data machine or participant-level file is needed to implement, verify or run the step.
- Workflow: as for the first report. A report is committed alone, only after `report --check` passes on the clean tree, and regenerating any input invalidates it until a new one is written and checked.
