# Design

## Context

See `proposal.md` for the motivation and the scope, and `specs/case-study-report/spec.md` for the requirements. This is the state that shapes the approach:

- **The stub.** `run_report(analysis_dir, cohort_dir, diagnostics_dir, out, check)` raises `NotImplementedError`; its docstring states the inputs, the outputs and the return value `{"path", "tables", "checked", "mismatches"}`. `cli.py` already has a `report` subparser with `--analysis-dir`, `--cohort-dir`, `--diagnostics-dir`, `--out` and `--check`. `constants.py` has `REPORTS_DIR` (`reports`) and `REPORT_NAME` (`motco-adni-{date}.md`).
- **The inputs are all tracked.** `git ls-files results/` lists exactly the 30 aggregate files; 26 of them are the report's inputs (the stage means and loadings are quoted by hash only, through their manifests). Every hash the report needs for a participant-level file is in a manifest. So the step runs on any clone, and every real-input check in `tasks.md` runs on the committed tree, with no data machine.
- **The manifests' chain fields**, as written today:
  - `cohort_manifest.json`: `inputs.clean.<platform>.manifest.sha256`; `outputs.stage_counts.csv.sha256`, `outputs.cohort.csv` (participant-level, hash only).
  - export `manifest.json`: `inputs.clean.<platform>.manifest.sha256`, `inputs.cohort.manifest.sha256`; `outputs.<file>.sha256` with `participant_level`.
  - primary `analysis_manifest.json`: `inputs.export_manifest.sha256`, `inputs.files.<export file>` (`sha256`, `recorded`, `equals_export_manifest`); `outputs.<file>.sha256` for the seven files; `settings.n_jobs`, `settings.latent_adjustment`; no `numerics` block.
  - `diagnostics_manifest.json` (primary and arm): `inputs.analysis.analysis_manifest.sha256`, `inputs.analysis.files.<file>.sha256`, `inputs.analysis.is_primary`, `inputs.analysis.latent_adjustment`, `inputs.analysis.n_jobs`, `inputs.export.export_manifest.sha256`, `inputs.cohort.files.cohort_manifest.json.sha256`; `outputs.<file>.sha256`; `numerics`.
  - arm `analysis_manifest.json`: as the primary's plus `arm` (the constant) and `reference.files.{result.json, analysis_manifest.json}.sha256`; `numerics`.
  - `latent_sensitivity_manifest.json`: `reference.files`, `arm.files` (the two JSON files each), `inputs.export.export_manifest.sha256`, `inputs.cohort.files.cohort_manifest.json.sha256`, `inputs.primary.*`; `outputs.<file>.sha256`; `numerics`.
  - The clean, cohort, export and primary analysis manifests predate `adni-portable-numerics` and have no `numerics` block; their outputs were reproduced pinned on 2026-10-28 (AGENTS.md).
- **The renderers.** `render_analysis_summary(record, *, export_manifest, n_jobs, alpha, rank_floor)` writes the per-statistic reading lines (`data.py` around the "Reading, under the rules below" block); `render_latent_sensitivity(rows, *, statuses, primary, arm, reference, arm_info, descriptives, findings, n_jobs, ...)` writes the per-status lines ("Both are non-rejections; the arm's is weaker …"); `render_axis_diagnostics(tables, *, analysis, variables, blocks, findings, threshold)` formats correlations with three decimals. `_fmt(value, ".6g")` is the summary's number format; `_rejection_text` and `_rejected` give the status words. The committed `summary.md` files hash to the values their manifests record, so a re-render from the committed records is an exact gate on any machine.
- **The template.** `../sead_sexdiff` has no report step: its reports are hand-written Markdown with provenance sections quoting hashes and versions. Their section order (provenance first, results, then the reading rules) is kept here where it fits; nothing else is carried over.
- **Determinism.** The step does no numeric work, so it needs no pinned numerics and records none. Float formatting (`format(x, ".6g")`, `".3f"`) is the same on every machine.

## Goals / Non-Goals

**Goals:**
- One command from the committed outputs to the report, and one from a report back to a cell-level verdict.
- A report whose every number has one source file and one formatting rule, and whose every sentence is either a constant or produced by the renderers the summaries already use.
- A check exact enough that a single changed digit, a regenerated input or a reworded renderer fails it, naming where.
- Nothing in the step that needs a data root, a data machine, MOTCO at run time or a pinned numeric environment.

**Non-Goals:**
- A general document generator or a template language. The report is one fixed structure in Python, like the three summaries.
- Prose beyond the generated sentences (proposal, out of scope).
- A report manifest file. The provenance section is the manifest, and it is checked like every other table (D2).
- Re-issuing the earlier manifests with a `numerics` block.

## Decisions

**D1. The report is generated in full; no hand-written text.**
Every section is produced by `render_report` from the loaded inputs and the constants. The only interpretive sentences are the ones `summary.md` and `latent_sensitivity.md` already print, through shared helpers (D5).
- *Alternative: generated tables plus a hand-written discussion, with the checker scanning the prose for numbers.* Rejected. A number in prose has no cell to be checked against; the scan would be heuristic, and reading rule 8 asks for an exact check. A discussion quotes the report from outside it.

**D2. The body is a function of the inputs and the file name; the provenance section is the manifest.**
- The date appears in the file name and in the title line (`# … — <date>`), parsed back from the file name by the checker. Nothing else of the report run is written: no revision, host, time or runtime. Two runs are byte-identical (spec: deterministic body).
- The provenance section carries what a manifest would: every input with its sha256 and the manifest that records it; per step the recorded revision and `dirty` flag, the versions and the `numerics` state (`pinned` and host, or "no block, written before `adni-portable-numerics`"); the raw LONI inputs as the clean and cohort manifests record them (name, sha256, predeclared, repair); the chain links checked. A separate `reports/<name>.manifest.json` would duplicate this and escape the check.
- Default `--out`: `reports/motco-adni-<today>.md` with the local date (`date.today().isoformat()`). `--check` without `--out`: the newest `motco-adni-*.md` by the date in the name.

**D3. Inputs, gates and the chain, in this order, before anything is written.**
1. Resolve the six directories (D7) and `REPORT_INPUT_FILES`; an absent file stops naming it and the command that writes it (`clean --platform <p>`, `cohort`, `export`, `analyze`, `axis-diagnostics`, `latent-sensitivity`, `axis-diagnostics --analysis-dir … --out-dir …`).
2. Hash every aggregate input and compare with its own manifest's `outputs` entry (`stage_counts.csv` against the cohort manifest; `result.json` and `summary.md` against their analysis manifest; the four diagnostic CSVs and `diagnostics.md` against their diagnostics manifest; `latent_sensitivity.csv` and `.md` against the comparison manifest). Manifests are hashed for the chain, not checked against themselves.
3. The chain, link by link, each named by the downstream step to rerun:
   - cohort manifest `inputs.clean.<p>.manifest.sha256` = sha256(`<p>/clean_manifest.json`) → `cohort`;
   - export manifest `inputs.clean.<p>.manifest.sha256` and `inputs.cohort.manifest.sha256` → `export`;
   - primary manifest `inputs.export_manifest.sha256` = sha256(export manifest), and each `inputs.files.<f>.recorded` = export manifest `outputs.<f>.sha256` → `analyze`;
   - primary diagnostics `inputs.analysis.analysis_manifest.sha256` = sha256(primary manifest), `inputs.analysis.files.result.json.sha256` = primary `outputs.result.json.sha256`, `inputs.export.export_manifest.sha256`, `inputs.cohort.files.cohort_manifest.json.sha256` → `axis-diagnostics`;
   - arm manifest `inputs.export_manifest.sha256`, `reference.files.{result.json, analysis_manifest.json}.sha256` = the primary's hashes → `latent-sensitivity`;
   - comparison manifest `reference.files` = the primary's, `arm.files` = sha256(arm `result.json`) and sha256(arm manifest), `inputs.export.export_manifest.sha256`, `inputs.cohort.files.cohort_manifest.json.sha256` → `latent-sensitivity`;
   - arm diagnostics `inputs.analysis.analysis_manifest.sha256` = sha256(arm manifest), `inputs.analysis.files.result.json.sha256` = arm `outputs.result.json.sha256`, the export and cohort links → `axis-diagnostics --analysis-dir … --out-dir …`.
4. Reported runs: primary and arm `settings.n_jobs` = `REPORTED_N_JOBS` and the records' `measurement.n_jobs`; every `numerics.pinned` present is true; `versions.motco`, `versions["scikit-learn"]` and `versions.metabo_adni` equal across the manifests that record them.
5. Identity: primary `settings.latent_adjustment` null and no `latent_adjustment` in its record; primary diagnostics `inputs.analysis.is_primary` true; arm record `latent_adjustment.conditioning` = `LATENT_SENSITIVITY_ARM["conditioning"]` and arm manifest `arm.name` = `LATENT_SENSITIVITY_ARM["name"]`; arm diagnostics `inputs.analysis.is_primary` false.
6. Write mode only: `--out` exists without `--force` → stop naming it.

Participant-level files are never opened or hashed: the chain uses the hashes the manifests recorded (`equals_export_manifest`, `equals_cohort_manifest` are read, not recomputed). The loader returns one dict: the parsed JSON records and manifests, the CSV tables, the provenance rows and the findings of the gates (D8).

**D4. Structure.** `REPORT_SECTIONS`, the ten level-2 headings in order; under each, titled tables so that the checker can name them (`### <table title>` or a bold lead line; the parser keys tables by the nearest heading and their order within it). Every table's first column is its row key (the statistic, the step, the file, the component, the sex × stage cell).

1. **Summary.** One paragraph: n, the cells, rank and floor; the three statistics with observed value, p and status, each followed by its reading line (D5); the arm's rank and the status per statistic with its status line; the count of flagged components in each diagnostic. All from the records.
2. **Provenance.** Tables: versions per step (step × package, as each manifest's `versions`); revisions and numerics per step (recorded commit, `dirty`, `numerics.pinned`, host, or the no-block note); inputs (file, sha256, recorded in); raw LONI inputs (name, sha256, predeclared, repair) from the clean and cohort manifests; chain links checked (link, `ok`).
3. **Cohort.** `COHORT_RULE` and `STAGE_RULE` as the cohort manifest records them; the cascade per platform set and the union (`counts.p180`, `counts.nmr`, `counts.union`, `counts.intersection.cascade`); the sex × stage tables of `stage_counts.csv` (one per set) and the intersection's sex × stage × `DX.bl` × phase cells; the per-cell descriptives (`descriptives.cells`, the table `latent_sensitivity.md` prints); the phase-against-run agreement; the cleaning options (`CLEAN_OPTIONS` as recorded) and the participants × metabolites after each metabo_adni step per platform (`counts.observed`), with the expected counts beside them.
4. **Export.** `EXPORT_FEATURE_RULE` as recorded (units, transform, membership marks); features per block (cleaned, kept, derived by mark); block shares; `phase_offset` per block (median |d|, |d| > 1, |corr(pc1, phase)|); zero cells, floors not positive, non-finite cells.
5. **Primary analysis.** Settings by constant name (`ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA` with `ANALYSIS_REJECTION_RULE`, `ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`, `n_jobs`) and `motco_defaults_used`; the statistics table of `summary.md`; the reading lines; cell sizes; latent space (rank, selection, `cv_mean_auroc`, repeats, eigengap with its null q05 / q50 / q95, CV settings); covariates (columns and kinds, design columns, reference levels, reference row, missing policy, dropped); the `cli_equivalent`.
6. **Axis diagnostics of the primary.** `DIAGNOSTIC_VARIABLES` and the threshold as recorded; flagged latent-component rows and flagged block-PC rows (the two tables of `diagnostics.md`'s first section); the components table; per block the variance shares of the three PCs and pc1 against `phase` (Spearman here, Pearson recorded by export). The full tables are referenced by hash.
7. **Latent-adjustment sensitivity.** The arm by constant name; the comparison's statistics table (primary row first, status column); the latent-space table; the arm's `latent_adjustment` block; the covariate roles table (`LATENT_SENSITIVITY_COVARIATE_ROLES`) with a pointer to the descriptives in section 3; MOTCO's two decisions as the comparison manifest records them; the arm diagnostics' flagged rows and components table, with the first component against `phase` beside the primary's; the arm's `cli_equivalent`.
8. **Findings.** Per step: `deviations` and `findings`, verbatim; then the report's own (D8).
9. **Reading rules.** `READING_RULES`, then `LATENT_SENSITIVITY_READING_RULES`, numbered, verbatim, under their constant names.
10. **Reproduction.** The pipeline commands in order, the two `cli_equivalent` commands, and `adni-sexdiff report --check --out <this file>`.

**D5. Formatting and the shared reading lines.**
- Record values through `_fmt` (`.6g`); p-values as recorded (MOTCO writes four decimals); counts as integers; correlations, shares and SDs with the specs `render_axis_diagnostics` uses, so the report's digits equal the summaries'.
- The per-statistic reading lines move out of `render_analysis_summary` into `_statistic_reading_line(statistic, rejected, *, stages, arm)`; the per-status lines move out of `render_latent_sensitivity` into `_arm_status_line(statistic, status, rejected_primary, rejected_arm)`. Both renderers call them; the report calls them. The gate: the committed `summary.md` of the primary and of the arm, re-rendered from the committed `result.json` and export manifest at `n_jobs = 1`, must hash to the values their manifests record; `latent_sensitivity.md`, re-rendered through the helpers `run_latent_sensitivity` uses from the committed records and manifests, must hash to the comparison manifest's value. A difference reverts the refactor.

**D6. The checker.**
- `parse_report(text)` splits the Markdown into sections (level-2 headings), and within each into tables (runs of lines starting with `|`, header and separator rows, cells split on unescaped `|`, `\|` unescaped) and other lines. Tables are keyed `(section, index)` and titled by the nearest preceding `###` or bold lead line; rows by the first column; cells by the header.
- `check_report(path, inputs)` regenerates the text with the date from the file name, parses both, and compares: for each table, the set of row keys, then every cell; for the other lines, line by line in order. Mismatches: `section › table "<title>" › row <key> › <column>: report <a>, generated <b>` or `section › line <i>: report "<a>", generated "<b>"`; extra or missing tables and rows are mismatches too. Every mismatch is listed; the CLI exits 1 on any. The gates (D3) run first and stop on their own messages.
- Write mode parses the written file back and asserts the parsed tables equal the generated `tables` (the DataFrames the function returns), so a parser gap fails at write time.
- `--check` writes nothing and returns `{"path", "tables", "checked": True, "mismatches": [...]}`.

**D7. Flags and constants.**
- `report --cleaned-dir` (`results/cleaned`), `--cohort-dir`, `--input-dir` (`results/motco_input`, as `analyze` names it), `--analysis-dir`, `--diagnostics-dir`, `--sensitivity-dir` (`LATENT_SENSITIVITY_DIR`, read through `LATENT_SENSITIVITY_SUBDIRS`), `--out`, `--check`, `--force`. Progress lines `[report]` name files and counts (inputs hashed, links checked, tables and cells written or compared), never a participant.
- `REPORT_INPUT_FILES: dict[str, tuple[str, ...]]` keyed by the directory role (`cleaned`, `cohort`, `export`, `analysis`, `diagnostics`, `sensitivity/analysis`, `sensitivity/comparison`, `sensitivity/diagnostics`), built from the existing name constants; `REPORT_SECTIONS: tuple[str, ...]` the ten titles. Both conventions.

**D8. Findings, never stops.** The report's own: a manifest with `git_revision.dirty` true (step and commit named); a manifest without `numerics` (step named, "written before `adni-portable-numerics`"). The copied ones: every `deviations` and `findings` entry of every manifest, under its step. Progress prints each.

**D9. Verification, on any machine with the Nix shell and the committed tree.**
- Scratch copies of the tracked `results/` files (`git ls-files results | xargs cp --parents` into the scratchpad) are the fixtures for every failure check; each is edited in one place and the step is pointed at it with the directory flags and a scratch `--out`. No data root and no participant-level file is involved.
- An independent scratch script re-reads the written report's tables and the source files with `json` and `pandas` and compares every statistic, p-value, null summary, rank, count, descriptive, hash and correlation it finds; it must report zero differences. It is a second reading of the sources, not the renderer's.
- The first report is written on the clean tree at the implementing commit and checked before it is committed.

**D10. Return value and docstring.** `run_report` returns the stub's dict; `tables` holds every table the report prints as a DataFrame keyed by `"<section> › <title>"`. The docstring states inputs, gates, sections, the check and the contract, and replaces the stub's "implemented by the report change" note.

## Risks / Trade-offs

- **A cell holds a `|` or a backtick** (`rho \| design` in the diagnostics tables; code-formatted names). → Cells are escaped as the existing renderers do and the parser unescapes; the write-mode parse-back catches any gap before a report is committed.
- **A later change rewords a renderer or a reading rule.** Every committed report then fails `--check` on a line. → That is the intended coupling: the change that rewords re-issues the report (or the date-named report stays as the dated record and the new one is written beside it); the check names the line.
- **The chain gate is strict**: regenerating any upstream output with `--force` requires every downstream step again before a report can be written. → Already the pipeline's discipline; the message names the step to rerun.
- **The report is long** (the full correlation and geometry tables would add hundreds of rows). → Only flagged rows, the components tables and the block-PC lines are quoted; the full tables are referenced by hash.
- **The date from the file name**: a report renamed by hand fails on the title line. → Named by the checker; `--out` keeps the name.
- **Hostnames in the report** (`numerics.host`). → Already in the committed manifests; quoted as recorded.
- **The refactor of the reading lines changes a summary byte.** → The D5 gate on the committed hashes, before any report is written; a difference reverts.
- **A manifest key moves** in a later step change. → The loader names the manifest and the key it could not find; the report change that follows updates the chain map.

## Migration Plan

1. Constants, the shared reading-line helpers and the D5 gate.
2. The loader and the gates, with the failure checks on scratch copies.
3. The renderer, the independent value check, determinism.
4. The parser and `--check`, with the edited-cell, edited-line and regenerated-input checks.
5. The CLI, the docstring, README and AGENTS.md.
6. Commit the implementation. On the clean tree at that commit: `report`, then `report --check`; commit the report alone, named, with why it is aggregate.
7. Rollback: delete the report; reverting the code restores the stub, and the D5 gate shows the summaries unchanged.
