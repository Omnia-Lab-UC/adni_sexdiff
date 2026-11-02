# Proposal

## Why

The case-study reports carry every number in tables and contain no figures. Every report change so far (`adni-report` through `adni-operating-characteristics`) listed figures as out of scope.

On 2026-11-02, nine draft figures were drawn in a scratch directory from the committed aggregate files the report already reads. The user chose:
- to keep all nine;
- to give each one a description beyond what its axes show;
- to have `report` draw them, rather than a separate step.

A figure drawn by hand outside the pipeline goes stale without anyone noticing when a result is regenerated, for example when a MOTCO pin move re-issues every output. This change makes the figures part of the report:
- they are drawn in the same run, from the same checked inputs;
- they are committed beside the report;
- `report --check` checks them, so a regenerated result fails the check, naming the figure and the value that moved.

## What Changes

- **Nine figures drawn by `report`** in write mode, after every gate. They are built from the inputs `_load_report_inputs` returns, with no MOTCO call and no data root:
  1. `f1_cohort_design`: the analysis cohort by sex, baseline diagnosis (`DX.bl`) and p180 run (`stage_counts.csv`).
  2. `f2_trajectories`: the primary's stage means, one panel per latent component, each sex a line from CN through MCI to AD (`stage_means.csv`). Above each panel: the component's share of the sex differences and its flagged diagnostic variables.
  3. `f3_primary_tests`: each statistic of the primary against its RRPP null (q50 to q95, whisker to q99), with the most power MOTCO measured at this design.
  4. `f4_operating_characteristics`: MOTCO's size readings and power curves from the cited decision.
  5. `f5_axis_diagnostics`: the raw and partial correlation of each primary component with the eight `DIAGNOSTIC_VARIABLES`, beside the loading share per block.
  6. `f6_block_phase`: |ρ| of each block's first three principal components with `phase`, for the primary export and the seven exports that a sensitivity builds.
  7. `f7_nist_bridge`: the bridge factor `b` per p180 metabolite, with its standard error, bridged or not, and its kit.
  8. `f8_sensitivities`: each sensitivity's p-value per statistic beside the primary's, grouped by rule set, each status that differs from the primary's labelled with its dependence.
  9. `f9_rank_sweep`: each rank's observed statistic against that rank's own null, the primary at its CV-selected rank among the forced ranks.

  Two things differ from the drafts:
  - `f6` shows all eight exports instead of three, so no export is picked for what its figure shows.
  - Titles and subtitles describe what is drawn and state no result, whereas the drafts' subtitles did.
- **Two files per figure** under `reports/figures/<report stem>/`, for example `f1_cohort_design.svg` and `f1_cohort_design.csv`: 18 files, about 1.2 MB per report. Both are aggregate, since every value is copied from a committed aggregate file.
  - **The SVG** draws text as paths, so it renders the same in every viewer. It uses a fixed ID salt and no date. Its metadata holds the figure's title, its input files with their sha256, and the matplotlib version.
  - **The data CSV** has one row per plotted value: a key, the quantity, the value as read from its source, the source file and the field.
- **A new section "Figures"**, the second, after "Summary" (fifteen sections). It opens with:
  - a lead naming the figures directory, the matplotlib version, and how `--check` compares the figures;
  - the table "Figure files": per figure its title, its SVG and data CSV with their sha256, and its input files.

  Then each figure has a level-3 heading, the image and a three-part caption:
  1. **How to read it.** Fixed text per figure, decided verbatim in this change's design: what each mark, line and colour encodes, and which comparisons the figure supports and which it does not. It quotes no value from an input and states no result.
  2. **In this report.** Generated lines, only where a reading sentence already exists, each string-equal to the document that prints it:
     - `f3`: the primary's three reading bullets;
     - `f4`: the decision's verdict and size sentence;
     - `f5`: the primary's flagged rows;
     - `f7`: the bridge summary;
     - `f8`: the status sentence of each status that differs from the primary's;
     - `f9`: the anchor and nesting bullets.
  3. **Sources and rules.** The input files and the rule lists that govern the figure, generated from the figure's input map.
- **Every number in a figure is copied** at the digits the report prints for the same value. A figure computes no statistic, correlation, mean or count of its own:
  - `f7`'s legend counts come from the export manifest's bridge summary, not from a tally of the table;
  - a cell with no row in `stage_counts.csv` is drawn empty and labelled `none`.
- **One more input**: the primary's `stage_means.csv` (for `f2`), checked against `analysis_manifest.json` like every other aggregate file. That makes 147 files in all, still 45 of them manifests.
- **The check.** `report --check` regenerates the figures in memory along with the report. After the report's tables and lines it compares:
  - each figure's data CSV cell by cell, naming the figure, the row key, the column, both values and the source;
  - each SVG's bytes, naming the figure and both sha256;
  - the directory's contents, naming a missing or extra file.

  It exits non-zero on any mismatch and writes nothing. Comparing the data and the drawing separately tells a moved result (the data differ) from a moved drawing (the data are equal and the SVG differs).
- **How a stale figure shows up.** A regenerated result has a new hash, so its provenance cell, the figure's data and the figure's SVG metadata no longer match, and `--check` names each. The fix is a new report, which draws new figures in its own directory; earlier reports keep theirs.
- **Pins.**
  - `matplotlib==3.11.2` becomes a direct dependency; today it is in the lock only because MOTCO needs it. A convention `MATPLOTLIB_VERSION`, checked at run time before anything is written, works as `METABO_ADNI_VERSION` does.
  - Figures are drawn under the package's pinned numeric settings. A state that is not pinned stops the step, because a committed output must be pinned (constraint 6).
  - The report then depends on its inputs, its file name and the pinned drawing library.
- **Output discipline.** The figures directory is staged as `<stem>.tmp/` along with the report's `.tmp` file. The report is parsed back, then both are renamed. An existing figures directory stops write mode unless `--force` is given.
- **Earlier layouts.** All seven committed reports stop at the section gate, with "Figures" absent. The report of 2026-11-02-3 checks at 9779964.
- **The next report** is written on the clean tree under that day's next free name, with its figures. It is checked with `--check` on this machine and on a second machine (the cluster login node or another data machine), then committed alone with its figures directory.

A scratch spike for this proposal (2026-11-02, read-only) drew the nine drafts from the committed tree. With text as paths, a fixed hash salt and no date, the SVG output was identical byte for byte across two runs on this machine: 1.2 MB for the nine, against 370 KB with text kept as text. No second machine has been checked yet.

**Scientific constants introduced: none.** The change reads and draws committed values. It adds no statistic, threshold or reading rule, and the fixed caption texts describe how the figures encode values, not results.

Conventions added:
- `REPORT_FIGURES`: per figure its file stem, title, subtitle, input files, rule lists and reading text;
- `REPORT_FIGURES_DIR` (`figures`);
- `FIGURE_STYLE`: the palette and the drawing settings;
- `MATPLOTLIB_VERSION` (`3.11.2`);
- "Figures" as the second entry of `REPORT_SECTIONS`;
- `ANALYSIS_STAGE_MEANS` in the `analysis` role of `REPORT_INPUT_FILES`.

Out of scope, each its own change if wanted:
- Figures beyond the nine; interactive or HTML pages; PNG or PDF output; slides.
- Any figure of participant-level data, such as latent scores or one metabolite's values. This is never in scope (constraint 1).
- Figures placed inline in the other sections, and any rewrite of an existing section's tables or sentences.
- Figures drawn by a pipeline step, or committed under `results/`.
- Rewriting earlier reports, or drawing figures for them.
- Publishing the figures outside the repository (an artifact or a website).
- The cluster clone (constraint 7).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `case-study-report`: these requirements change:
  - the inputs (`stage_means.csv`; 147 files);
  - the content contract (the "Figures" section; fifteen sections);
  - every number pasted (the figures and their data);
  - the interpretive sentences (the captions: fixed reading texts and existing sentences only);
  - the deterministic body (the figures, with the pinned drawing library and numerics);
  - the check (the figures compared) and its layout gate (the seven committed reports);
  - output discipline (the figures directory).

  Two requirements are added: the figures are drawn from the report's inputs under pins, and each figure is captioned and traced to its inputs.

## Impact

- `src/adni_sexdiff/constants.py`:
  - the conventions above;
  - `REPORT_SECTIONS` (fifteen) and `REPORT_INPUT_FILES` (`stage_means.csv`);
  - the module docstring.
- `src/adni_sexdiff/figures.py`, new: the figure data rows and the drawing. matplotlib is imported here only, when `report` runs, so the pipeline steps never load it.
- `src/adni_sexdiff/data.py`:
  - `_load_report_inputs` (`stage_means.csv`);
  - `render_report` (the "Figures" section);
  - `run_report` (the version and numerics gates, staging and renaming the figures);
  - `check_report` (the figure comparison);
  - `_check_report_layout`, with their docstrings.

  No step and no reading-sentence function changes.
- `src/adni_sexdiff/cli.py`: no new flag. The figures directory follows `--out`, and the help text says so.
- `pyproject.toml` and `uv.lock`: `matplotlib==3.11.2` added as a direct dependency with `uv add`, the locked version unchanged.
- `reports/motco-adni-<date>[-<n>].md` and `reports/figures/<stem>/`: added and committed, aggregate. The seven earlier reports are unchanged.
- `README.md` and `AGENTS.md`:
  - the status paragraph and step 6;
  - constraint 1's list of committed aggregate files (the figures);
  - the Layout entries (`figures.py`, `reports/figures/`);
  - the dependencies.
- `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged, since no participant-level output is added.
- No MOTCO call and no data root. Any machine with the Nix shell and the committed tree can run the step. The second-machine byte check needs a second machine with the same lock.
- Workflow:
  1. Implement and verify on the committed tree and on synthetic edits in a scratch directory, then commit.
  2. Write the report with its figures on the clean tree, check it here and on a second machine, and commit it alone.
  3. Archive, then open the PR.
