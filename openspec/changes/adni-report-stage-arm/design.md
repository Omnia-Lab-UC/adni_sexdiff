# Design

## Context

See `proposal.md` for the motivation and scope, and `specs/case-study-report/spec.md` for the requirements. This is the state that shapes the approach.

- **The report step today** (changes `adni-report` and `adni-report-variants`, `data.py`):
  - `_load_report_inputs` reads `REPORT_INPUT_FILES` by role through `_report_dirs`: 53 files, 17 manifests in `_REPORT_MANIFESTS`, and a rerun hint from `_report_rerun`.
  - It runs five gates in order: presence, hashes against `outputs`, identity, reported runs, and the chain (76 links).
  - `render_report` writes the eleven `REPORT_SECTIONS` through `_ReportBuilder`. Every table sits under a level-3 heading and is keyed `"<section> › <title>"`, and section numbers come from `_section_ref`.
  - `_diagnostics_section(..., prefix=…)` renders one diagnostics run.
  - `check_report` starts with `_check_report_layout`, which is generic over `REPORT_SECTIONS`.
- **The arm's outputs are tracked.** `git ls-files results/motco_stage_sensitivity` lists 15 files. The report reads 13 of them. The other two, the arm analysis' `stage_means.csv` and `pls_loadings.csv`, are quoted by hash through its manifest. The arm's export CSVs, `latent_scores.csv` and `analysis_metadata.csv` are gitignored, and their hashes are in the manifests.
- **The chain fields of the arm's manifests.** All four record revision 55841a3 (clean) and pinned `numerics`, with no deviation.
  - **Arm export `motco_input/manifest.json`** (`step` `stage-sensitivity`):
    - `stage_arm`: the constant, plus `constant`;
    - `inputs.cohort.manifest.sha256` and `inputs.primary_export.manifest.sha256`;
    - `reference.manifest.sha256` (the primary export manifest) and `reference.feature_tables.features_<block>.csv.sha256` (the source of the floors). The primary export manifest records the feature tables under `outputs`;
    - `reference.{sex_stage, phase_by_stage, covariate_levels, phase_offset, participants}`, copied from the primary;
    - `counts` and `expected`, plus `outputs`.

    It records no `inputs.clean`, because the arm reads no cleaned table. It has no `variant` block. Its `versions` hold metabo_adni but not MOTCO or scikit-learn.
  - **Arm `analysis/analysis_manifest.json`**:
    - `stage_arm`; `settings.n_jobs` 1, `settings.latent_adjustment` None, `settings.cli_equivalent`;
    - `inputs.export_manifest.sha256` and `inputs.files.<csv>.recorded`;
    - `reference.files.{result.json, analysis_manifest.json}.sha256` and `reference.export.manifest.sha256`;
    - one finding, the rank (6 against 8).

    Its `result.json` records `measurement.n_jobs` 1 and has no `latent_adjustment` block.
  - **`comparison/stage_sensitivity_manifest.json`**:
    - `stage_arm`;
    - `arm`: `name`, `files` and `export.manifest.sha256`;
    - `reference.files`;
    - `inputs.primary.export.manifest.sha256`, and `inputs.primary.analysis.files`, which repeat `reference.files`;
    - `inputs.cohort.files.cohort_manifest.json.sha256`;
    - `counts` with `ranks`, `rejected`, `statuses`, `eigengap` and `cv_mean_auroc`;
    - the rank finding.
  - **Arm `diagnostics/diagnostics_manifest.json`**: the fields of the other diagnostics runs, with `inputs.analysis.is_primary` false and `inputs.analysis.stage_arm` `cn_lmci_ad`. It has no `export_variant` key. Its findings are the flagged rows and the not-the-primary note.
- **Shared code that already exists:**
  - `_stage_arm_status_line` writes the status bullets of `stage_sensitivity.md`;
  - `_stage_arm_definition` writes the arm clause of the arm's `summary.md` and `stage_sensitivity.md`;
  - `_stage_arm_rules_heading` returns a level-2 heading and a lead line, shared by the three arm documents;
  - `_stage_arm_lines(export_manifest)` writes the "Arm" block of the arm's `summary.md` and of `stage_sensitivity.md`: three bullets, then four tables each led by a plain line ("Exported participants by `dx_bl` …:", "Sex × stage cells:", "Runs within each stage (`phase`):", "Covariate levels:"), then two run-offset bullets.
- **The two committed reports.** `reports/motco-adni-2026-10-29.md` (eleven sections) was committed at c94f5e7, and `reports/motco-adni-2026-10-28.md` (ten sections) at 36c9cc8. Today is 2026-10-29, so a report written today would take the name of an existing file. The user chose to write the new report on the first date after 2026-10-29 (D11).

## Goals / Non-Goals

**Goals:**
- One report that carries the primary and every predeclared sensitivity that has run: the latent arm, the export variants and the CN / LMCI / AD arm. Each is shown beside the primary, never beside another sensitivity. Every number is copied, and every sentence is a constant or comes from an existing renderer.
- The same gates for the arm as for the other sensitivities, so that a stale, swapped or crossed arm directory stops the report and names the command that fixes it.
- No byte of a committed arm document changes.
- Nothing that needs a data root, a data machine, MOTCO at run time or pinned numerics.

**Non-Goals:**
- A general registry of sensitivities. The arm is one constant, and its roles are fixed, as the latent arm's are.
- The arm's per-statistic reading lines from its `summary.md` (proposal, out of scope).
- Unifying the primary row's status cell, which reads `same` in the latent-adjustment table and `the result` in the export table. This change follows the newer convention for the new section only, and leaves the latent section's bytes as they are.

## Decisions

**D1. The arm is a fixed extension of the same step.**
- `report` stays one step with one contract.
- The arm's roles are `stage-sensitivity/<subdir>`, one per value of `STAGE_SENSITIVITY_SUBDIRS`, read from `--stage-sensitivity-dir`.
- The arm is required, and no flag skips it, as for the latent arm and the variants.
- *Alternative:* a separate report for the stage arm. Rejected: the reading rules bind one reader of all results, and a second document would repeat the provenance and the gates.

**D2. Inputs, roles and labels.**
- **Constant.** A new convention, `REPORT_STAGE_ARM_FILES`, is keyed by `STAGE_SENSITIVITY_SUBDIRS`'s keys:
  - `export`: `manifest.json`;
  - `analysis`: `result.json`, `analysis_manifest.json`, `summary.md`;
  - `comparison`: `stage_sensitivity.csv`, `stage_sensitivity.md`, `stage_sensitivity_manifest.json`;
  - `diagnostics`: `DIAGNOSTICS_FILES`.

  `REPORT_INPUT_FILES` gains the four roles after the variants' roles, which makes 13 more files and 66 in all.
- **Labels.** `_REPORT_MANIFESTS` gains four labels after the variants', in pipeline order, for 21 in all:
  - `stage-sensitivity (export)`;
  - `stage-sensitivity (analysis)`;
  - `stage-sensitivity (comparison)`;
  - `axis-diagnostics (cn_lmci_ad)`.

  The latent arm keeps its labels.

**D3. Gates.** They run in the order of `adni-report` D3, extended to the arm.
1. **Presence.** Every input is present. The hint for an absent file is its role's command (D8).
2. **Hashes.** No code change here. The nine aggregate files of the arm are checked against `outputs.<name>.sha256` of their role's manifest, and the four manifests are hashed for the chain.
3. **Identity.** After the variants, the arm is checked:
   - Export manifest: `step` is `stage-sensitivity`. `stage_arm.constant` is `STAGE_SENSITIVITY_ARM`. Each field of the constant (`name`, `source`, `keep`, `drop`, `stage_map`, `floors`, `analysis`, `change`) equals the recorded field, with tuples compared as lists. There is no `variant` block, because the arm is not crossed with an export variant.
   - The analysis and comparison manifests record `stage_arm.name` equal to `cn_lmci_ad`, and the comparison also records `arm.name` equal to it.
   - The analysis records `settings.latent_adjustment` None, and its `result.json` has no `latent_adjustment` block, because the arm is not crossed with the latent adjustment.
   - The diagnostics record `inputs.analysis.is_primary` false and `inputs.analysis.stage_arm` equal to `cn_lmci_ad`.
4. **Reported run.**
   - The arm analysis records `n_jobs = REPORTED_N_JOBS` in `settings.n_jobs` and in `measurement.n_jobs`.
   - Every `numerics` block must be pinned, now over 21 manifests.
   - The version agreement covers the manifests that record each package. The arm export manifest records metabo_adni only.
5. **Chain.** The 76 links stay, and the arm adds 24, for 100 in all.
   - **Arm export manifest (5):**
     - `inputs.cohort.manifest` against the cohort manifest;
     - `inputs.primary_export.manifest` and `reference.manifest` against the primary export manifest;
     - `reference.feature_tables.features_p180.csv` and `features_nmr.csv` against the primary export manifest's `outputs`. These are the source of the arm's floors, and the one link of a new kind.
   - **Arm analysis manifest (8):**
     - `inputs.export_manifest` against the arm export manifest;
     - the four `inputs.files.<csv>.recorded` against the arm export manifest's `outputs`;
     - `reference.files` (2) against the primary's `result.json` and `analysis_manifest.json`;
     - `reference.export.manifest` against the primary export manifest.
   - **Comparison manifest (7):**
     - `reference.files` (2) against the primary;
     - `arm.files` (2) against the arm analysis;
     - `arm.export.manifest` against the arm export manifest;
     - `inputs.primary.export.manifest` against the primary export manifest;
     - `inputs.cohort.files.cohort_manifest.json` against the cohort manifest.

     `inputs.primary.analysis.files` repeat `reference.files` and are not linked twice.
   - **Arm diagnostics manifest (4):** `diagnostics_links` with the arm export role. These are the arm analysis manifest, the arm `result.json` as that manifest records it, the arm export manifest and the cohort manifest.

   A `--force` rerun of the arm after its diagnostics breaks the first diagnostics link, and the hint names the arm's `axis-diagnostics` command. A regenerated primary export breaks the arm export's `reference` links, and the hint names `stage-sensitivity --force`.

The identity and reported-run gates read a manifest's own content, so they run before the chain. A crossed or swapped directory is then named as such, not as a broken link. On the committed tree all 24 links hold. A read-only script checked them while the proposal was written, and task 2.1 rechecks them through the loader.

**D4. The section "Stage-definition sensitivity".** It is number 9, between "Export sensitivity" and "Findings". The title names what the arm varies, as "Latent-adjustment sensitivity" does. Its contents, in order:
- **Lead paragraph.**
  - The primary, with the `result.json` hash taken from the comparison's `reference`.
  - Beside it, the arm `cn_lmci_ad` (`STAGE_SENSITIVITY_ARM`, change `adni-stage-sensitivity`), described by `_stage_arm_definition` of the recorded `stage_arm`, with its directory and its `result.json` hash as its analysis manifest records it.
  - Every table in the section is read under `READING_RULES` and `STAGE_SENSITIVITY_READING_RULES` (section 11).
  - The primary row comes first and its status is the result (stage-arm rule 1).
  - A status that differs is dependence on the stage definition and the sample (stage-arm rule 2).
  - The arm is read against the primary only (stage-arm rule 8).
- **"Statistics: primary and arm".**
  - Rows `<statistic> primary` and `<statistic> cn_lmci_ad`, for each statistic.
  - Columns: row, statistic, analysis, observed, p (RRPP), rejected, null mean, null sd, null q95, status.
  - Values come from `stage_sensitivity.csv`, and statuses from `counts.statuses` of the comparison manifest.
  - The primary's status cell reads `the result`.
  - Digits are as in the other two comparison tables.
- **The `angle` paragraph**, worded as in `stage_sensitivity.md`: both ranks, floors and eigengaps, ending "the ranks differ, which is reported, not ranked (stage-arm rule 3)".
- **"Status per statistic:"**, a lead line followed by the three bullets from `_stage_arm_status_line`, string-equal to `stage_sensitivity.md`.
- **"Latent space: primary and arm".** Rows: participants, PLS-DA rank (selection), rank floor, `cv_mean_auroc`, CV repeats completed, pooled relative eigengap, and eigengap null q05 / q50 / q95. They come from the comparison CSV and the two records' `config_spectrum`, as in `stage_sensitivity.md`.
- **"Arm `cn_lmci_ad`".** The five bullets that `_stage_arm_lines` writes, string-equal and in their order (the three definition bullets, then the two run-offset bullets). Four tables follow, each under its own level-3 heading:
  - "cn_lmci_ad: Exported participants by `dx_bl`";
  - "cn_lmci_ad: Sex × stage cells";
  - "cn_lmci_ad: Runs within each stage";
  - "cn_lmci_ad: Covariate levels".

  Their headers and rows are the ones `stage_sensitivity.md` prints (D5).
- **"Run offset: primary and arm".**
  - Rows `<block> primary` and `<block> cn_lmci_ad` per block.
  - Columns: median |d|, max |d|, |d| > 0.5, |d| > 1, |corr(PC1, phase)|, |corr(PC2, phase)|, expected |d| > 0.5, expected |d| > 1.
  - The primary's values and expectations come from the primary export manifest. The arm's come from its export manifest's `counts.phase_offset` and `expected.phase_offset`.
  - A key that is not predeclared shows `n/a`, for example nmr > 0.5 for the arm.
  - Digits are as in the export section's offset table.
- **"Arm export against the predeclared counts".** One row per flattened key of the arm export manifest's `expected`, except `phase_offset`, with columns observed and expected, read from `counts` and `expected`. The analysis and diagnostics expectations are checked by their steps, and any deviation is copied under "Findings".
- **Diagnostics of the arm.**
  - A lead paragraph names the directory, the rank, `is_primary` false and `stage_arm`. It states that a component of the arm that tracks a variable is a measurement-space finding about the arm and never grounds to adopt it, and that in the arm `dx_bl` orders the participants as `stage` does (stage-arm rule 7).
  - Then `_diagnostics_section(..., prefix="cn_lmci_ad: ")`.
- **"First component against phase".** Rows for the primary and `cn_lmci_ad`, read from the two axis-correlations CSVs.
- **The arm analysis' `cli_equivalent`**, in a code block.

The other sections draw on the same inputs:
- **Summary.** After the variants' paragraph comes the arm's. It opens with the arm, its constant, change, definition and rank, and "section 9". It continues "Status per statistic (`same` when …, else `differs (stage-definition dependence)`; the primary's status is the result either way), read under `READING_RULES` and `STAGE_SENSITIVITY_READING_RULES` (section 11):", followed by the three `_stage_arm_status_line` bullets. The diagnostics paragraph adds the arm's flagged-row counts and flagged components. Each sensitivity is a separate clause beside the primary.
- **Provenance.** The versions, revisions-and-numerics, inputs and chain tables extend by iteration. No new table is added.
- **Findings.** The four new manifests are iterated under their paths.
- **Reading rules.** A fourth level-3 heading, `STAGE_SENSITIVITY_READING_RULES`, holds the lead line of `_stage_arm_rules_heading` (its last element) and the eight rules, numbered. The helper's level-2 heading is not printed, since it would open a section.
- **Reproduction.** After the variants' commands come two more:
  - `uv run adni-sexdiff stage-sensitivity`, which reads `cohort.csv` and the primary export's CSVs, so it runs on a data machine;
  - `uv run adni-sexdiff axis-diagnostics --input-dir results/motco_stage_sensitivity/motco_input --analysis-dir results/motco_stage_sensitivity/analysis --out-dir results/motco_stage_sensitivity/diagnostics`.

  The MOTCO `cli_equivalent` list adds the arm.

Section numbers in the text come from `_section_ref`. The reading rules move from section 10 to 11 and reproduction to 12, and no literal number is written. About 13 tables are added. The apply records the exact counts.

**D5. The arm-definition tables are shared row by row, not as a block.**
- **The constraint.** The report's parser keys every table by a level-3 heading. `_stage_arm_lines` instead leads its four tables with plain lines. So the report cannot print that block as it is.
- **The decision.**
  - Move the four tables' headers and rows into one helper. `_stage_arm_lines` keeps its lead lines and calls the helper, and the report calls it under its own level-3 headings.
  - The bullets stay in `_stage_arm_lines`. The report takes them from its output (its lines that start with `- `), so the shared lines come from one code path.
  - The byte gate of D6 applies.
- *Alternative:* teach the parser to key a table by its lead line. Rejected: it changes the table contract and the check of every section.
- *Alternative:* make `_stage_arm_lines` emit level-3 headings. Rejected: it changes the bytes of the committed `stage_sensitivity.md` and the arm's `summary.md`, which would force a rerun of the arm.
- *Alternative:* copy the row code into the report. Rejected: two code paths for one table invite drift.

**D6. Shared code keeps its bytes.**
- **Called unchanged.** The report calls `_stage_arm_status_line`, `_stage_arm_definition` and the lead line of `_stage_arm_rules_heading` as they are.
- **Changed with a byte gate.** D5 changes `_stage_arm_lines` internally. That function depends only on the export manifest, so three gates are enough. Any failure reverts the refactor.
  - Its output on the committed arm export manifest must equal that of `main`'s version, imported from a scratch worktree of 975ccd8.
  - The "## Arm" block of the committed `stage_sensitivity.md` must equal that output line by line.
  - The same holds for the "## Arm" block of the arm's `summary.md`.
- **Nothing else.** No other renderer changes.

**D7. Reports of an earlier layout.** `_check_report_layout` is generic over `REPORT_SECTIONS` and is not changed.
- After the change, `report --check --out reports/motco-adni-2026-10-29.md` stops, naming the absent section "Stage-definition sensitivity" and `git log -1 --format=%H -- reports/motco-adni-2026-10-29.md`. That command gives c94f5e7, where the report checks.
- The 2026-10-28 report stops naming both absent sections, and checks at 36c9cc8.
- Both files stay in place, unchanged.
- *Alternative:* keep the eleven-section renderer behind a layout version. Rejected, as in `adni-report-variants` D6.

**D8. Flags, rerun hints and constants.**
- **The flag.** `--stage-sensitivity-dir`, default `STAGE_SENSITIVITY_DIR`, read through `STAGE_SENSITIVITY_SUBDIRS`. `report` then has eleven flags.
- **Rerun hints.** `_report_rerun` gains a branch for the arm's roles, placed before its latent-sensitivity fallback:
  - export, analysis and comparison: `adni-sexdiff stage-sensitivity --force`, then the arm's `axis-diagnostics`;
  - diagnostics: `adni-sexdiff axis-diagnostics --input-dir <root>/motco_input --analysis-dir <root>/analysis --out-dir <root>/diagnostics`.

  The reported-run hint is `stage-sensitivity --force` without `--n-jobs`.
- **Constants.** `REPORT_STAGE_ARM_FILES` and `REPORT_INPUT_FILES` (D2) and `REPORT_SECTIONS` (twelve titles) are conventions. No scientific constant is added, and "Flag and ask" is unchanged.

**D9. Findings.** No new finding type is added. The report's own findings stay the five no-`numerics` manifests, because the four new ones are pinned and clean. The arm's findings are copied verbatim under their labels: the rank finding twice (analysis and comparison), the flagged rows and the not-the-primary note.

**D10. Verification.** It runs on any machine with the Nix shell and the committed tree, all in the session scratchpad.
- **Values.** An independent script reads the scratch report's new tables and, with `json`, `csv` and `hashlib`, the sources. It compares every value at the printed digits:
  - the statistics with `stage_sensitivity.csv` and the ranks with `latent.selected_lv`;
  - the latent space with the CSV and `config_spectrum`;
  - the offsets and counts with the two export manifests;
  - the diagnostics tables with the arm's CSVs;
  - the 13 new input hashes with `hashlib` and the recording manifests.

  Every row of the four arm-definition tables must equal the corresponding row of the committed `stage_sensitivity.md`.
- **Strings.**
  - The status lines and the five arm bullets are string-equal to `stage_sensitivity.md`.
  - The four rule lists are string-equal to the constants.
  - No sentence compares the arm with the latent arm or a variant. Every line that names the arm and another sensitivity is listed, and each must be a listing.
- **Failure cases.** Each runs on an edited scratch copy of the tracked `results/`. In every case nothing is written, the exit code is 1, and the copy is otherwise unchanged:
  - an arm input absent;
  - an edited arm `stage_sensitivity.csv`;
  - a field of `STAGE_SENSITIVITY_ARM` patched in-process;
  - the arm's analysis replaced by the latent arm's (identity);
  - an arm analysis with `n_jobs` 4;
  - an unpinned arm manifest;
  - stale arm diagnostics;
  - an arm export whose `reference.feature_tables` hash is edited;
  - arm diagnostics with `is_primary` true.
- **Determinism.** Two `--force` runs are byte-identical. A run to another date differs in the title line only.
- **Checks.**
  - `--check` passes on a fresh scratch report.
  - On both committed reports it stops with the layout message.
  - In a worktree of c94f5e7 the 2026-10-29 report passes its own check.
- **Audit.** An audit hook over `run_report` lists 66 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none of them participant-level.

**D11. The report written at the apply.** The user decided the naming.
- **Date.** The report is written on the clean tree at the implementing commit, on the first date after 2026-10-29, or later. It is named by the day it is written: `report` without `--out` uses today's date.
- **Name.** `reports/motco-adni-2026-10-29.md` is never overwritten, and no `--force` is used on a committed report. No `--out` names a date other than the day of writing.
- **Order.** If the implementation is done on 2026-10-29, the report task waits for the next day. Archive, push and merge come after it.
- **Record.** The counts (sections, tables, cells and chain links) go in `tasks.md`.

## Risks / Trade-offs

- **Report length.** The report grows from about 122 KB to an estimated 150 KB. Mitigation: the arm's full diagnostics tables stay quoted by hash, and the four definition tables are small (5, 2, 3 and 7 rows).
- **The refactor of `_stage_arm_lines` could change committed bytes.** The D6 gates compare its output with `main`'s and with the committed documents line by line, and a failure reverts the refactor.
- **The apply spans two days.** The report waits for 2026-10-30. Accepted (the user's choice). The implementation commit and every verification can be done before then, and nothing else blocks.
- **The earlier reports are not checkable by the new code.** Accepted. The layout gate says so and names the revision, and both reports check at their own revisions (D7, D10).
- **Inconsistent primary status cells.** The new section and the export section say `the result`, while the latent section says `same`. Accepted for now; changing the latent section is its own decision (Non-Goals).
- **A stale or crossed arm directory.** It is caught by the identity gate and the chain (D3), and each names its command.

## Migration Plan

1. Branch `adni-report-stage-arm` from `main` (975ccd8).
2. Add the constants, the flag, the loader and gates, the renderer and the `_stage_arm_lines` refactor. Verify on the committed tree as D10 describes.
3. Update `README.md`, `AGENTS.md` and the docstrings, then commit the implementation.
4. On 2026-10-30 or later, write `reports/motco-adni-<date>.md` on the clean tree at the implementing commit, run `report --check`, and commit the report alone.
5. Archive the change on the branch, then push, open the PR and merge.

Rollback: revert the branch. The committed results are untouched, and both earlier reports stay checkable at their own revisions.
