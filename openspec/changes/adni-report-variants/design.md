# Design

## Context

See `proposal.md` for the motivation and the scope, and `specs/case-study-report/spec.md` for the requirements. This is the state that shapes the approach:

- **The report step today** (change `adni-report`, `data.py`):
  - `_load_report_inputs` reads the 26 files of `REPORT_INPUT_FILES` through `_report_dirs`. `_REPORT_MANIFESTS` lists 9 manifests by label, and every gate message ends with the rerun hint of `_report_rerun`.
  - `render_report` writes the ten sections of `REPORT_SECTIONS` through `_ReportBuilder`, which keys every table `"<section> › <title>"`. `_diagnostics_section(b, tables, manifest, prefix=…)` already renders one diagnostics run under a prefix, as it does for the arm.
  - `check_report` regenerates the report and compares it with `parse_report`. The reading-rules section prints each rule list under a level-3 heading named after its constant.
  - In-text references to other sections are literals ("section 7", "section 9").
- **The variant outputs are tracked.** `git ls-files results/motco_export_sensitivity` lists 31 files: 14 for `nist_bridge` and 13 for `per_run_standardized` are the report's inputs. The stage means and loadings of each variant analysis (4 files) are quoted by hash only, through their manifests, as the primary's and the arm's are. The variant export CSVs, `features_<platform>.csv`, `latent_scores.csv` and `analysis_metadata.csv` are gitignored, and their hashes are in the manifests.
- **The chain fields of the variant manifests**, as written by `export-sensitivity` and `axis-diagnostics`:
  - **Variant export `motco_input/manifest.json`**, `step` `export-sensitivity`:
    - `variant`: the `EXPORT_VARIANTS` entry with `name` and `constant`;
    - `inputs.clean.<platform>.manifest.sha256`, `inputs.cohort.manifest.sha256`;
    - `reference.manifest.sha256`, the primary export manifest, and `reference.phase_offset`, the primary's offsets copied;
    - `outputs.<file>.sha256`;
    - for `nist_bridge`: `inputs.qc.archives` and `inputs.qc.workbooks`, each with `sha256` beside `predeclared_sha256`, and `bridge` with `summary`, `factors_log2` and `table` (`name`, `sha256`, `rows`). The bridge table is recorded only there, not under `outputs`.
  - **Variant `analysis/analysis_manifest.json`**, `step` `export-sensitivity`:
    - `variant`; `settings.n_jobs`, `settings.latent_adjustment` (None), `settings.cli_equivalent`;
    - `inputs.export_manifest.sha256`, `inputs.files.<export file>.recorded`;
    - `reference.files.{result.json, analysis_manifest.json}.sha256` and `reference.export.manifest.sha256`;
    - `outputs.<file>.sha256`.

    `result.json` carries `measurement.n_jobs` and no `latent_adjustment` block.
  - **`comparison/export_sensitivity_manifest.json`**:
    - `variant`; `reference.files` (the primary's two files);
    - `inputs.variant.analysis.files` (the variant's two), `inputs.variant.export.manifest.sha256`, `inputs.variant.bridge.sha256` (None for `per_run_standardized`), `inputs.primary.export.manifest.sha256`;
    - `counts` with `ranks`, `rejected`, `statuses` and `phase_offset`; `outputs` for the CSV and the Markdown.
  - **Variant `diagnostics/diagnostics_manifest.json`**: as the arm's, with `inputs.analysis.is_primary` false and `inputs.analysis.export_variant` set to the variant's name.
  - All eight manifests carry a pinned `numerics` block (nixos-home) and the versions MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8, with revision 94a0046 clean. None records a deviation. The analyses and comparisons record the rank finding, and the diagnostics record their flagged variables.
- **The shared sentences already exist**:
  - `_export_variant_status_line` writes the status lines of `export_sensitivity.md`;
  - `_export_variant_lines` writes the "Export variant" bullets of both `export_sensitivity.md` and the variant `summary.md`;
  - `_export_variant_rules_heading` returns a level-2 heading and the lead line of `EXPORT_VARIANT_READING_RULES`, shared by `export_sensitivity.md`, the variant `summary.md` and the variant `diagnostics.md`.
- **The first report** `reports/motco-adni-2026-10-28.md` was committed at 36c9cc8. It passes `--check` at dd6585b, and its 26 inputs are unchanged by `adni-nist-bridge`.

## Goals / Non-Goals

**Goals:**
- One report that carries the primary, the latent arm and every registered export variant, each beside the primary, with every number copied and every sentence a constant or an existing renderer's.
- The same gates for the variants as for the arm: presence, hashes, identity, reported runs, the chain, so a stale or swapped variant directory stops the report naming the command that fixes it.
- A check that still names every mismatch cell by cell, and that says plainly when the checked report predates the current layout instead of listing the consequences.
- Nothing that needs a data root, a data machine, MOTCO at run time or pinned numerics.

**Non-Goals:**
- A reading of one variant against another (proposal, out of scope).
- The full bridge table in the report (D4).
- Re-checking the 2026-10-28 report with the new code (D6).
- A general mechanism for future sensitivities. Each later arm or variant extends the report by its own change; this one is generic over `EXPORT_VARIANTS` only because the variant layout is.

## Decisions

**D1. The variants are a registry-driven extension of the same step.** `report` stays one step with one contract. The variants it reads are the keys of `EXPORT_VARIANTS` in registry order. Every registered variant is required, and no flag selects or skips one, as with the arm. A variant registered later fails the presence gate until its outputs exist; the change that registers it then extends the report. The variant-specific content is keyed on the variant export manifest: the bridge parts appear when the manifest carries a `bridge` block, the role list is built from hook `factors` (D7), and nothing branches on a variant's name. *Alternative*: a separate `variant-report` step or document. Rejected: the reading rules bind one reader of all results, and a second document would repeat the provenance and the gates.

**D2. Inputs and roles.** `REPORT_INPUT_FILES` gains the roles `export-sensitivity/<variant>/<subdir>`, built from `EXPORT_VARIANTS` and `EXPORT_SENSITIVITY_SUBDIRS`:
- `motco_input`: `manifest.json`;
- `analysis`: `result.json`, `analysis_manifest.json`, `summary.md`;
- `comparison`: `export_sensitivity.csv`, `export_sensitivity.md`, `export_sensitivity_manifest.json`;
- `diagnostics`: `DIAGNOSTICS_FILES`;
- `bridge`: `nist_bridge.csv`, for variants with hook `factors`.

That makes 27 files and 53 in all. `_REPORT_MANIFESTS` gains four labels per variant, after the arm's, in pipeline order: `export-sensitivity <variant> (export)`, `export-sensitivity <variant> (analysis)`, `export-sensitivity <variant> (comparison)` and `axis-diagnostics (<variant>)`, for 17 in all. The labels name the step in the provenance tables and under "Findings".

**D3. Gates, in the order of `adni-report` D3, extended.**
1. Every input is present. The hint for each absent file is its role's command (D7).
2. Hashes. Every aggregate file is checked against `outputs.<name>.sha256` of its role's manifest. The bridge table is the one exception: it is checked against `bridge.table.sha256` of the variant export manifest, where the step recorded it. Manifests are hashed for the chain.
3. Identity. The primary and the arm are checked as before. Then, per variant:
   - The export, analysis and comparison manifests record `variant.name` equal to the registry key.
   - The export manifest's `variant` entries `block`, `hook`, `rule`, `setting` and `change` equal `EXPORT_VARIANTS[<name>]`.
   - The analysis records `settings.latent_adjustment` None, and its `result.json` holds no `latent_adjustment` block.
   - The diagnostics record `inputs.analysis.is_primary` false and `inputs.analysis.export_variant` equal to the name.
4. Reported runs. Each variant analysis records `n_jobs = REPORTED_N_JOBS` in `settings.n_jobs` and in `measurement.n_jobs`. Every `numerics` block present is pinned, and the version agreement is checked over all 17 manifests.
5. The chain, link by link. The 31 links of the first report stay. Each variant adds the links below: 23 for `nist_bridge` and 22 for `per_run_standardized`, so the report checks 76 links in all.
   - Its export manifest (4 links): the two clean manifests, the cohort manifest, and the primary export manifest as `reference.manifest`.
   - Its analysis manifest (8 links): the variant export manifest; the four export files' `recorded` hashes against the variant export manifest's `outputs`; the primary's `result.json` and `analysis_manifest.json` as `reference.files`; the primary export manifest as `reference.export.manifest`.
   - Its comparison manifest (6 links, 7 with a bridge): the primary's two files as `reference.files`; the variant's two analysis files under `inputs.variant.analysis.files`; the variant export manifest; the primary export manifest under `inputs.primary.export.manifest`. Where `inputs.variant.bridge` is not None, its `sha256` against the bridge table.
   - Its diagnostics manifest (4 links): the variant analysis manifest; the variant `result.json` as the analysis manifest records it; the variant export manifest; the cohort manifest.

   A `--force` rerun of a variant after its diagnostics breaks the first diagnostics link. The hint names the variant's `axis-diagnostics` command with its three directories.

The identity and reported-run gates read a manifest's own content, so they run before the chain, as in `adni-report`. A swapped directory is named as a swap, not as a broken link.

**D4. The section "Export sensitivity"**, number 8, between "Latent-adjustment sensitivity" and "Findings". In order:
- **Lead paragraph.** The primary, with its `result.json` hash from the first variant's comparison `reference`, beside each variant: its name, `EXPORT_VARIANTS` entry setting and change, and directory. Every table in the section quotes a variant and is read under `READING_RULES` and `EXPORT_VARIANT_READING_RULES` (section 10). The primary row comes first and its status is the result. A variant never replaces it (variant rule 1), and a status that differs is run-handling dependence (variant rule 2).
- **"Statistics: primary and variants".** Rows `<statistic> primary`, then `<statistic> <variant>` per variant in registry order, for each statistic. Columns: statistic, analysis, observed, p (RRPP), rejected, null mean, null sd, null q95, status. The primary rows come from the first registered variant's `export_sensitivity.csv`; the chain guarantees every comparison references the same primary record. Each variant's rows come from its own CSV, and its status from its comparison manifest's `counts.statuses`. The primary's status cell reads `the result`. Digits as in the arm's table.
- **The `angle` sentence.** One paragraph per variant, worded as the one in `export_sensitivity.md`: each analysis' rank, floor and eigengap, and "the ranks differ, which is reported, not ranked" where they differ.
- **"Status per statistic".** Under one level-3 heading per variant (`` `nist_bridge` ``, `` `per_run_standardized` ``), the bullets `_export_variant_status_line` writes, string-equal to that variant's `export_sensitivity.md`.
- **"Latent space: primary and variants".** Rows: rank (selection), floor, `cv_mean_auroc`, CV repeats completed, pooled relative eigengap, eigengap null q05 / q50 / q95. Columns: primary and each variant. Values from the comparison CSVs and the records' `config_spectrum`, as in the arm's table.
- **"Run offset per export".** Rows `<block> primary` and `<block> <variant>` for each block. Columns: median |d|, max |d|, |d| > 0.5, |d| > 1, |corr(PC1, phase)|, |corr(PC2, phase)|, expected |d| > 0.5, expected |d| > 1. The primary's values and expectations come from the primary export manifest, and a variant's from its export manifest's `counts.phase_offset` and `expected.phase_offset`. A key that is not predeclared is `n/a`. Digits as in the export section's offset table.
- **"Variant exports against the predeclared counts".** One row per flattened key of `EXPORT_VARIANT_EXPECTED_COUNTS[<variant>]`, excluding `analysis` and `phase_offset`. Columns `<variant>` and `<variant> expected` per variant, from `counts` and `expected` of its export manifest, `n/a` where a variant has no such key. This is the layout of the "Cleaning counts" table. The analysis expectations are checked by the step itself, and any deviation is copied under "Findings".
- **"Export variant `<variant>`".** Per variant, under a level-3 heading, the bullets of `_export_variant_lines`, string-equal to the "Export variant" section of its `export_sensitivity.md`. Where the export manifest carries a `bridge` block, two tables follow:
  - "NIST bridge per kit": rows FIA, UPLC and not bridged, observed from `bridge.summary.p180_bridged` beside `expected.p180_bridged`.
  - "Unbridged metabolites": the rows of `nist_bridge.csv` with `bridged` False. Columns: metabolite, kit, NIST column, replicates, valid replicates and ISTD flags per run, and `b` at `+.3f`.

  A sentence quotes the full table by name, hash and row count.
- **Diagnostics per variant.** A lead paragraph names the directory, the rank and `is_primary`, and states that a variant component that tracks a variable is a measurement-space finding, never grounds to adopt the variant (variant rule 7). Then `_diagnostics_section(..., prefix="<variant>: ")`.
- **"First component against phase".** The primary and each variant, read from the axis-correlations CSVs as in the arm's table. The table key is unique by section.
- **The `cli_equivalent` of each variant analysis**, one code block per variant.

*Alternative*: one block per variant mirroring `export_sensitivity.md`. Rejected for the statistics, latent-space and offset tables: three rows side by side are what a reader compares. Kept for the status bullets and the export lines, whose string equality is per variant.

*The bridge table.* Quoted by hash with the seven unbridged rows, as `export_sensitivity.md` quotes it. Variant rule 7's "reported beside the results" is met by the factor summary in `_export_variant_lines` and the hash. Printing all 133 rows is a one-table addition if the user wants it before the apply.

The other sections, from the same inputs:
- **Summary.** After the arm's paragraph: each variant's rank and its status bullets (`_export_variant_status_line`), led by a sentence naming `EXPORT_VARIANTS`, `READING_RULES` and `EXPORT_VARIANT_READING_RULES`. The diagnostics paragraph adds each variant's flagged-row counts and flagged components.
- **Provenance.** The versions, revisions, inputs and chain tables extend by iteration. A new table, "QC archives and NIST workbooks", lists each archive and each workbook member from `inputs.qc` of the variant export manifests that carry one: file, run and kit for members, sha256, bytes, predeclared sha256, `predeclared`, recorded in.
- **Findings.** Iteration over the 17 manifests.
- **Reading rules.** A third level-3 heading `EXPORT_VARIANT_READING_RULES`, with the lead line of `_export_variant_rules_heading` (its last element; the helper's level-2 heading is not printed, since it would open a section) and the seven rules numbered.
- **Reproduction.** After the arm's commands: `uv run adni-sexdiff export-sensitivity --variant all` (its `nist_bridge` variant reads the two QC archives in the data root), and per variant `axis-diagnostics --input-dir … --analysis-dir … --out-dir …`. The MOTCO `cli_equivalent` list adds the variant analyses.

Section numbers in the text come from `REPORT_SECTIONS` (a helper returns a title's 1-based index), never literals, so "section 9" cannot survive as a stale reference to the reading rules, now section 10.

**D5. Shared sentences, bytes unchanged.** The report calls `_export_variant_status_line`, `_export_variant_lines` and the lead line of `_export_variant_rules_heading` as they are. The plan moves no renderer code. If the apply has to change one of the three helpers, it must re-render from the committed files the two `export_sensitivity.md`, the two variant `summary.md` and the two variant `diagnostics.md`, and each must keep the sha256 its manifest records, or the change is reverted. Without such a change, string equality is verified line by line against the committed files (D9).

**D6. A report of an earlier layout.** `check_report` parses the report first. When its level-2 headings are not `REPORT_SECTIONS` in order, the check stops before the input gates and before any comparison. It names the report, the sections absent and extra, and that the report was written by an earlier layout of `report` and checks at the revision that committed it: `git log -1 --format=%H -- <report>`, then `report --check --out <report>` in a worktree of that revision. Nothing is written and the CLI exits non-zero. `reports/motco-adni-2026-10-28.md` stays in place and unchanged, as the record of its time. `--check` without `--out` reads the newest report by date, so after the apply it reads the new one. *Alternative*: keep the old renderer behind a layout version. Rejected: two renderers to maintain for a file whose inputs and check are pinned by git anyway.

**D7. Flags, rerun hints and constants.**
- `--export-sensitivity-dir`, default `EXPORT_SENSITIVITY_DIR`, read per variant through `EXPORT_SENSITIVITY_SUBDIRS`. `report` then has ten flags.
- `_report_rerun` for the new roles:
  - export, analysis, comparison and bridge: `adni-sexdiff export-sensitivity --variant <v> --force`, then the variant's diagnostics;
  - diagnostics: `adni-sexdiff axis-diagnostics --input-dir <root>/<v>/motco_input --analysis-dir <root>/<v>/analysis --out-dir <root>/<v>/diagnostics`.
- `REPORT_INPUT_FILES` (D2) and `REPORT_SECTIONS` (eleven titles) are conventions. No scientific constant is added, and "Flag and ask" is unchanged.

**D8. Findings.** No new finding type. The report's own findings (a dirty revision, a missing `numerics` block) are evaluated over all 17 manifests. On the committed tree they stay the five no-`numerics` manifests, since the eight new ones are pinned and clean. The variant manifests' findings and deviations are copied verbatim under their labels.

**D9. Verification, on any machine with the Nix shell and the committed tree**, all in the session scratchpad:
- **Values.** An independent script reads the scratch report's new tables and, with `json` and `pandas`, the source files, and compares every value at the printed digits:
  - the variant statistics with `export_sensitivity.csv` and the records;
  - the offsets and counts with the export manifests;
  - the bridge tables with the manifest and `nist_bridge.csv`;
  - the diagnostics tables with the variant CSVs;
  - the QC hashes and the 27 new input hashes with `hashlib` and the recording manifests.
- **Strings.** Every status line and export-variant line is string-equal to the committed `export_sensitivity.md` lines, and the three rule lists to the constants.
- **Failure cases.** Each on an edited scratch copy of the tracked `results/`; nothing written in any case:
  - a variant input absent;
  - an edited bridge table;
  - swapped variant directories;
  - a variant manifest with `n_jobs` 4;
  - an unpinned variant manifest;
  - stale variant diagnostics;
  - a variant export whose `reference` is another primary export;
  - an `EXPORT_VARIANTS` setting edited in a scratch copy of `constants.py`, imported from the scratch tree.
- **Determinism**: two `--force` runs are byte-identical, and a run to another date differs in the title line only.
- **Checks**: `--check` passes on the new report. On the old report it stops with the layout message. In a worktree of 36c9cc8, the old report still passes its own check.
- **Audit**: an audit hook lists 53 files opened under `results/`, none participant-level.

**D10. The report written at the apply.** `reports/motco-adni-<apply date>.md`, written on the clean tree from the committed outputs, checked with `--check` on the clean tree, and committed alone. Its counts (sections, tables, cells, chain links) are recorded in `tasks.md`.

## Risks / Trade-offs

- **Report length.** Three more statistics rows per statistic, the variant diagnostics twice over and a provenance about twice as long take the report from about 62 KB to an estimated 110 KB. Mitigation: the per-metabolite bridge table stays out (D4), and full diagnostics tables stay quoted by hash, as before.
- **The registry and the report are coupled.** A change that registers a variant without running it makes `report` stop on the presence gate. Accepted: that change has to run the variant and extend the report anyway (D1), and the stop names the command.
- **A swapped or stale variant directory.** Caught by the identity gate and the chain (D3), each naming its command.
- **The old report is not checkable by the new code.** Accepted. The layout gate says so and names the revision, the old report's inputs are unchanged, and it checks at 36c9cc8 (D6, D9).
- **In-text section numbers.** Every reference is computed from `REPORT_SECTIONS` (D4), and the check compares every line, so a wrong number cannot pass silently.
- **String equality depends on unchanged helpers.** D5's byte gates apply if a helper is touched. Otherwise the line-by-line comparison against the committed files proves it (D9).

## Migration Plan

1. Branch `adni-report-variants` from `main` (dd6585b).
2. Add the constants, the loader and gates, the renderer, the layout gate in the checker, and the flag. Verify on the committed tree per D9.
3. Update `README.md`, `AGENTS.md` and the docstrings.
4. On the clean tree at the implementing commit, write `reports/motco-adni-<date>.md`, run `report --check`, and commit the report alone.
5. Archive the change on the branch, then push, open the PR and merge.

Rollback: revert the branch. The committed results are untouched, and the 2026-10-28 report stays checkable at its revision.
