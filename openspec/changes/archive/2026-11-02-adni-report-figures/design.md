# Design

## Context

See proposal.md (Why) for the motivation. The state this design works from:

- **The report.** `report` (`run_report` → `_load_report_inputs` → `render_report`, in `data.py`) reads the 146 files of `REPORT_INPUT_FILES`, runs its gates (presence, each aggregate file against its manifest, the identity of every run, reported and pinned runs, the 255-link chain, the cited measurement) and renders the fourteen sections of `REPORT_SECTIONS` as one Markdown string plus a dict of table frames.
  - Write mode stages `<out>.tmp`, parses it back (`_parse_back`) and renames it.
  - `--check` (`check_report`) first runs `_check_report_layout`, then regenerates the report and compares the two with `_compare_parsed`: tables cell by cell, other lines line by line.
- **The report records no numerics today.** Every command imports `adni_sexdiff` first, so `NUMERIC_SETTINGS` are already set when it runs; `_numerics_record` and `_numerics_problems` read the state.
- **What the figures need.** Every value the nine drafts plotted is in an input the report already loads, except the primary's `stage_means.csv`. That file is aggregate, committed and recorded in `analysis_manifest.json` under `outputs`, so the existing manifest gate checks it once it is in `REPORT_INPUT_FILES`.
- **matplotlib 3.11.2** is in `uv.lock` only as a MOTCO dependency. The bundled font (DejaVu Sans) and FreeType ship inside its wheel.
- **The spike** (2026-11-02, scratch): with `svg.hashsalt` fixed, `svg.fonttype` `path` and the `Date` metadata removed, two runs on this machine wrote identical SVG bytes for all nine figures (1.2 MB). With `svg.fonttype` `none` the nine weighed 370 KB.
- **The palette** comes from the dataviz reference instance, its pairs validated for colour-vision deficiency: sexes blue `#2a78d6` and orange `#eb6834`; runs aqua `#1baf7a` and violet `#6250d6`; blocks magenta `#e87ba4` and green `#008300`; a blue ordinal ramp; a blue–grey–red diverging map. Three colours fall below 3:1 contrast on the surface, so every series that uses them is also direct-labelled.

## Goals / Non-Goals

**Goals:**
- Figures that a reader of the report on GitHub sees, each with a description of how to read it.
- Every figure tied to the exact inputs it was drawn from, checked by the same command that checks the report, failing visibly when a result moves.
- Byte-reproducible figures on any machine with the lock, like every other committed output.

**Non-Goals:**
- A plotting API for other uses, a style system, or configurable figures (no flag selects or styles a figure).
- Accessibility features beyond what a static SVG carries: direct labels, colour-vision-safe pairs, a title and a description. Hover and other interactivity belong to an HTML page, which is out of scope.

## Decisions

### D1. `report` draws the figures; no separate step (user's choice)

The figures are drawn by `run_report` after every gate, from the `inputs` dict that `_load_report_inputs` returns, and `check_report` regenerates them. One command therefore writes, and one checks, the report and its figures. The report and its figures directory form one dated issue, so a figure cannot exist without the report that cites it.

Alternatives considered:
- **A `figures` step with its own manifest, gated by `report` like any other step.** It is more modular, but it adds one step to rerun after every change and one more link to the chain, and the figures could drift from the report between runs.
- **Figures drawn by the pipeline steps** (`analyze`, the sensitivities), committed under `results/`. That would rerun MOTCO-dependent steps to change a drawing, and spread matplotlib over the data machines' steps.

### D2. One section "Figures", second in `REPORT_SECTIONS`

The fifteen sections are: Summary, **Figures**, Provenance, Cohort, Export, Primary analysis, Axis diagnostics of the primary, Operating characteristics, Latent-adjustment sensitivity, Export sensitivity, Stage-definition sensitivity, Rank sensitivity, Findings, Reading rules, Reproduction. Cross-references are numbered from `REPORT_SECTIONS` already, so every "section N" follows without hand edits.

The section holds, in order:
1. A lead, partly fixed and partly generated. It names the directory `figures/<stem>/`, the matplotlib version, that each SVG's metadata names its inputs with their sha256, that each data CSV holds one row per plotted value with its source and field, and that `report --check` compares the data cell by cell and the SVG by its bytes. It also states that the figures add no number, statistic or reading, and that the primary's status is the result wherever a sensitivity appears.
2. `### Figure files`: a table keyed by figure, with columns `figure`, `title`, `svg`, `svg sha256`, `data`, `data sha256`, `inputs`. The `inputs` cell lists the input paths in the figure's order, separated by `; `.
3. Per figure:
   - `### Figure <k>: <title>`;
   - the image line `![Figure <k>: <title>](figures/<stem>/<file>.svg)`;
   - `How to read it:` followed by the fixed reading text;
   - `In this report:` followed by the generated lines, a bullet list, present only when the figure's entry names lines;
   - `Sources:` followed by the input paths and the data CSV;
   - `Rules:` followed by the rule lists by constant name and the section that prints them.

Placing it second means a GitHub reader reaches the figures right after the summary. The parser needs no change: images and captions are lines, "Figure files" is a titled table.

Alternatives considered:
- **Figures inline in the sections they illustrate.** `f8` spans four sections. Inline figures would change the layout of six existing sections and the scenario that the sensitivity sections are unchanged.
- **An appendix after "Reproduction."** It keeps the figures far from the summary, which is the part they illustrate.

### D3. Files: SVG and a data CSV per figure, under `reports/figures/<stem>/`

`<stem>` is the report's file name without `.md`, so `motco-adni-2026-11-03.md` has its figures in `reports/figures/motco-adni-2026-11-03/`. Each of the nine figures writes `<id>.svg` and `<id>.csv`, eighteen files in all.

- **SVG** because it is text: it renders on GitHub, its size is reasonable, and its bytes are reproducible (spike).
- **Text drawn as paths** (`svg.fonttype` `path`) so it renders identically in every viewer. With `none`, text would fall back to the viewer's fonts on GitHub and could overlap. The cost is 1.2 MB against 370 KB per report.
- **No PNG**: it is binary, its bytes depend on antialiasing, and it is larger.
- **The data CSV** is the diffable record of what the figure plots, and the unit `--check` compares cell by cell (D7).

### D4. The data CSV: one row per plotted value

The columns are `key`, `quantity`, `value`, `source`, `field`.
- **`key`** is unique within the figure and built from its coordinates, `|`-joined, for example `Female|CN|pls_0` in `f2`, `delta|rank_06|p` in `f8`, `C10|b` in `f7`.
- **`value`** is the source value as read:
  - a CSV cell unchanged (an empty cell stays empty);
  - a JSON number by Python's `repr`, the shortest round trip;
  - a JSON string unchanged;
  - `absent` for a cell with no source row (only `f1`, for a sex × `DX.bl` × run cell that `stage_counts.csv` does not list).
- **`source`** is the input path relative to the repository, or `constants.<NAME>` for a reference line: `ANALYSIS_ALPHA` in `f3` and `f8`, `DIAGNOSTIC_CORRELATION_THRESHOLD` in `f2`, `f5` and `f6`.
- **`field`** locates the value in the source: a JSON path (`null_summary.delta.q95`), or a CSV row key and column (`component=pls_0,variable=phase:spearman`), or for `absent` the key looked up.

Rows follow the drawing order. The file ends with a newline and uses `\n` line endings and minimal quoting, so its bytes are deterministic.

The figure's own text (labels and annotations) prints values at the digits the report prints for the same value, through the report's own formatters. A figure never derives a value. The counts in `f7`'s legend come from the `nist_bridge` export manifest's `bridge.summary.p180_bridged`, and the unbridged labels from `nist_bridge.csv`'s `nist_column`.

### D5. Captions: the convention `REPORT_FIGURES`

`REPORT_FIGURES` is an ordered dict, figure id → `stem`, `title`, `subtitle`, `inputs` (paths, built from the report's directory roles), `generated` (the name of the report fragment it reuses, or none), `rules` (constant names), `reading` (fixed text). Titles, subtitles and reading texts describe what is drawn, quote no value from an input and state no result. They are decided here, verbatim:

| id | title | subtitle |
|---|---|---|
| `f1_cohort_design` | Analysis cohort by baseline diagnosis and p180 run | Participants per sex, baseline diagnosis (DX.bl) and p180 run; diagnoses grouped by the stage STAGE_RULE assigns. |
| `f2_trajectories` | Sex × stage trajectories in the primary's latent space | Covariate-adjusted stage means of each sex on each latent component of the primary; component signs are arbitrary. |
| `f3_primary_tests` | The primary's statistics against their permutation nulls | Observed delta, angle and shape against their RRPP nulls; below each, the most power measured at this design. |
| `f4_operating_characteristics` | MOTCO's operating characteristics at this design | Rejection rates with no effect (size) and as the effect grows (power), from the cited MOTCO decision. |
| `f5_axis_diagnostics` | What the primary's latent components track | Correlation of each component with the diagnostic variables, raw and partial, beside its loading share per block. |
| `f6_block_phase` | Each export's block principal components against the p180 run | \|Spearman ρ\| of each block's first three principal components with phase, for the primary export and each sensitivity's own export. |
| `f7_nist_bridge` | The NIST SRM 1950 bridge factor per p180 metabolite | b = mean log2 in ADNI-1 minus mean log2 in ADNI-GO/2 of the reference material, per metabolite, ordered by b. |
| `f8_sensitivities` | Every predeclared sensitivity beside the primary | RRPP p-value of each sensitivity per statistic, on a log scale, beside the primary's. |
| `f9_rank_sweep` | The rank sweep, each rank against its own null | Observed delta, angle and shape at each PLS-DA rank against that rank's RRPP null; the primary at its CV-selected rank. |

Reading texts, verbatim:

- **`f1_cohort_design`**: "Each bar counts the participants of the analysis cohort (both platforms at baseline) in one cell of sex, baseline diagnosis (`DX.bl`) and p180 run; the run is the `phase` covariate. Diagnoses are grouped under the stage `STAGE_RULE` assigns them (CN and SMC to CN, EMCI and LMCI to MCI, AD to AD). A cell with no row in `stage_counts.csv` is drawn empty and labelled `none`. The figure describes the design: it shows how the composition of each stage differs between the two runs, which is why `phase` enters the analysis as a covariate and why the CN / LMCI / AD arm exists. It is not a result."
- **`f2_trajectories`**: "Each panel is one component of the primary's PLS-DA latent space at its CV-selected rank, and each line joins one sex's covariate-adjusted stage means (LS-means at the record's reference row) from CN through MCI to AD. Every component has a panel, so no projection hides a dimension. A component's sign and scale are arbitrary, so a line's direction or a panel's range is not compared across panels. Above each panel are the component's share of the summed squared sex differences across stages (`sex_difference_by_stage` in `geometry_shares.csv`) and the diagnostic variables it tracks at or above `DIAGNOSTIC_CORRELATION_THRESHOLD`, a reporting flag on magnitude and never a test. `delta`, `angle` and `shape` are computed on all components together; no panel tests a sex difference on its own."
- **`f3_primary_tests`**: "For each statistic the grey box spans the primary's RRPP null from its median (q50) to its 95th percentile (q95), the whisker reaches the 99th (q99), and the dot is the observed value, all from the primary's record. The p-value is the share of null draws at or above the observed value, so a dot beyond q95 lies near a rejection at `ANALYSIS_ALPHA`; the recorded p-value under `ANALYSIS_REJECTION_RULE` decides. Below each panel is the highest rejection rate MOTCO measured for that statistic at this design, beside the decision's power floor. A dot inside the box is a non-rejection, and what a non-rejection says is set by that measured power, not by the dot's distance from the box."
- **`f4_operating_characteristics`**: "Left: each statistic's rejection rate when no sex effect is injected, at MOTCO's two controls (anchor and translation), with ±1.96 Monte Carlo standard errors, against the decision's α and one-sided bound. Right: each statistic's rejection rate as the injected effect grows along its own construction (magnitude for `delta`, orientation for `angle`, shape for `shape`), against the decision's power floor. The rates are MOTCO's synthetic measurement (`OPERATING_CHARACTERISTICS_SOURCE`), a structural analogue of this design for the primary's construction only: they say nothing about a metabolite and are not the size or power of any sensitivity (measurement rules 6 to 8)."
- **`f5_axis_diagnostics`**: "Rows are the primary's latent components and columns the eight `DIAGNOSTIC_VARIABLES`. The left panel holds the Spearman correlation of each component's scores with each variable, and the middle panel the partial correlation given the record's six design columns, drawn `—` for a variable that is itself a conditioning column. Colour runs from blue (negative) through grey to red (positive); an outlined cell reaches \|ρ\| ≥ `DIAGNOSTIC_CORRELATION_THRESHOLD`, a reporting flag on magnitude with no p-value. The right panel splits each component's loadings between the p180 and NMR blocks, beside the p180 share of the joint features (dashed). A component that tracks `phase` or `dx_bl` is a reading of the measurement space (reading rule 6), never grounds to change the analysis."
- **`f6_block_phase`**: "Each row is one export: the primary's, each export variant's (grouped by rule set) and the CN / LMCI / AD arm's. Each mark is the absolute Spearman correlation of one of the first three principal components of a z-scored block with `phase`, from that export's diagnostics (`block_pcs.csv`); the dashed line is `DIAGNOSTIC_CORRELATION_THRESHOLD`. The latent arm and the forced ranks use the primary export and have no row of their own. Each export is read against the primary's only, under its own rule set, and a block axis that follows `phase` describes the measurement, not the sex × stage result."
- **`f7_nist_bridge`**: "Each mark is one p180 metabolite, ordered by its bridge factor b: the mean log2 of NIST SRM 1950 in ADNI-1 minus that in ADNI-GO/2, over each run's valid replicates, with a ±1.96 plate-clustered standard error where the table records one. A b above zero means ADNI-1 measured the reference material higher. Filled marks are bridged under `NIST_BRIDGE_RULE`, and the `nist_bridge` variant multiplies their ADNI-GO/2 values by 2^b; open, labelled marks are not bridged and keep the factor 1. The shape marks the kit (FIA or UPLC). The factors come from reference material alone: they describe calibration between the runs and say nothing about sex or stage."
- **`f8_sensitivities`**: "Each row is one sensitivity (the latent arm, the six export variants in their rule-set groups, the CN / LMCI / AD arm and the six forced ranks of the sweep) and each panel one statistic. The dot is the row's RRPP p-value on a log scale, filled when rejected under `ANALYSIS_REJECTION_RULE`; the solid line is the primary's p-value and the dashed line `ANALYSIS_ALPHA`. A row is read against the primary only: a status that differs from the primary's carries its dependence label and never replaces the primary (reading rule 1 and the row's rule set). Rows are not read against one another, nothing is combined across the rank sweep, and no row is singled out by its p-value."
- **`f9_rank_sweep`**: "At each PLS-DA rank the grey box spans that rank's own RRPP null from q50 to q95, the whisker reaches q99, and the dot is the observed statistic. The black dot is the primary at its CV-selected rank, and the blue dots are the forced ranks of `RANK_SENSITIVITY_LADDER`, each the primary with only the rank fixed and the same permutation draws. The nulls change with the rank, so each dot is read against its own box only: observed values are not compared across ranks, no rank is chosen, and the sweep is not a test (`RANK_SENSITIVITY_READING_RULES`)."

Inputs, generated lines and rules per figure (paths relative to the repository; the directories follow the report's flags):

| id | inputs | generated lines (each string-equal to the line printed elsewhere in the report) | rules |
|---|---|---|---|
| `f1` | `results/cohort/stage_counts.csv` | none | `READING_RULES` |
| `f2` | `results/motco_analysis/stage_means.csv`, `result.json`; `results/motco_diagnostics/geometry_shares.csv`, `axis_correlations.csv` | none | `READING_RULES` |
| `f3` | `results/motco_analysis/result.json`; the decision's copy | the primary's three reading bullets (`_statistic_reading_line`) | `READING_RULES`, `OPERATING_CHARACTERISTICS_READING_RULES` |
| `f4` | the decision's copy | the verdict and the size sentence, as "Operating characteristics" prints them | `OPERATING_CHARACTERISTICS_READING_RULES` |
| `f5` | `results/motco_diagnostics/axis_correlations.csv`, `components.csv`; `results/motco_input/manifest.json` | the primary's flagged rows, as "Axis diagnostics of the primary" prints them | `READING_RULES` |
| `f6` | `block_pcs.csv` of the primary diagnostics, of each variant's diagnostics in `REPORT_EXPORT_VARIANTS` order and of the CN / LMCI / AD arm's diagnostics | none | `READING_RULES`, `EXPORT_VARIANT_READING_RULES`, `NMR_MEMBERSHIP_READING_RULES`, `SCALE_VARIANT_READING_RULES`, `STAGE_SENSITIVITY_READING_RULES` |
| `f7` | `results/motco_export_sensitivity/nist_bridge/bridge/nist_bridge.csv`, its export manifest | the bridge lines of `nist_bridge` (bridged per kit beside the predeclared counts, the unbridged metabolites), as "Export sensitivity" prints them | `READING_RULES`, `EXPORT_VARIANT_READING_RULES` |
| `f8` | the comparison table of the latent arm, of each variant, of the CN / LMCI / AD arm and of the rank sweep | the status sentence of each status that differs from the primary's, in figure order, as the summary prints it; then a fixed line pointing to the summary and the sensitivity sections for every status | `READING_RULES` and the six sensitivity rule sets |
| `f9` | `results/motco_analysis/result.json`, each rank's `result.json`, the sweep's comparison manifest | the anchor and nesting bullets (`_rank_anchor_lines`) | `READING_RULES`, `RANK_SENSITIVITY_READING_RULES` |

The generated lines call the same functions the report already uses for those lines, which keeps them string-equal by construction. The figure-specific code builds no sentence.

### D6. Drawing: `figures.py`, the object API, a pinned style

A new module `src/adni_sexdiff/figures.py` holds `figure_rows(inputs) -> dict[id, list[row]]` (D4) and `draw_figures(inputs, rows) -> dict[filename, bytes]`. `data.py` imports it inside `run_report` and `check_report` only, so no pipeline step loads matplotlib. The module exception to "`data.py` holds all logic" is recorded in AGENTS.md's Layout.

The drawing uses `matplotlib.figure.Figure` with the SVG canvas, never `pyplot`, so no backend or global state is involved. Each figure is drawn inside `matplotlib.rc_context` on top of matplotlib's defaults (`rcParamsDefault`) updated with `FIGURE_STYLE`. A user's `matplotlibrc` or style therefore cannot move the bytes. `FIGURE_STYLE` holds:
- the palette (Context);
- `svg.fonttype` `path` and a fixed `svg.hashsalt` (`adni-sexdiff`);
- `font.family` resolved to the bundled `DejaVuSans.ttf`, by file path from `matplotlib.get_data_path()` and not by family name. A system DejaVu of another version cannot be picked that way.
- the sizes, line widths and grid settings of the drafts.

SVG metadata:
- `Title`: the figure's title;
- `Description`: one line per input, `<path> sha256 <hash>`, from the hashes the gates computed;
- `Creator`: `adni-sexdiff report, matplotlib <version>`;
- `Date`: `None`.

The SVG is written to an in-memory buffer, and nothing touches the disk until D8.

The drafts change in two ways:
- `f6` holds the eight exports, grouped as in `f8`.
- Every in-figure title, subtitle and footer is the fixed text of `REPORT_FIGURES` or a generated source line. The draft subtitles that stated results ("None is rejected", "The NIST bridge moves the run…") are gone.

In `f8` and `f9`, nothing connects marks across rows or ranks: lines between ranks would draw a value across ranks.

### D7. Pins: `MATPLOTLIB_VERSION` and the numeric state

- **The dependency.** `uv add "matplotlib==3.11.2"` makes the locked version a direct, exact pin. The convention `MATPLOTLIB_VERSION = "3.11.2"` is checked by `check_matplotlib_version()`, modelled on `check_metabo_adni_version`, before any input is read, in write and check mode alike. A difference stops the step naming both versions and `uv sync --locked`. Moving matplotlib is then a change that re-issues the report, as a MOTCO pin move already does.
- **The numeric state.** It is read with `_numerics_record()` after the figures are drawn in memory (so every library they loaded is listed) and before anything is written. Non-empty `_numerics_problems` stops the step naming them; a committed output must be pinned (constraint 6). The report still writes no `numerics` block of its own: its body depends on the inputs, its name and the pinned library only, and the gate guarantees the pinned state.

### D8. Writing: staged together, renamed together

In write mode:
1. Draw every figure and build every data CSV in memory.
2. Run the numerics gate.
3. Render the report text, whose "Figure files" table quotes the in-memory hashes.
4. Write `reports/figures/<stem>.tmp/` (eighteen files) and `<out>.tmp`.
5. Parse the report back (`_parse_back`), read each CSV back and compare it with its rows.
6. Rename the figures directory, then the report.

The existing-output check covers both targets: an existing `<out>` or an existing `reports/figures/<stem>/` stops the step without `--force`. With `--force`, the old figures directory is removed just before the rename. A failure at any point removes both temporaries, and nothing is renamed. A failure between the two renames is not expected, since both are on one filesystem. The progress line names the report, the counts of tables and cells, and "18 figure files".

### D9. Check: the report, then the data, then the drawing

`check_report`:
1. Runs `_check_report_layout`, then the version gate, then every input gate.
2. Regenerates the report text, the figure rows and the SVG bytes in memory.
3. Compares:
   - the report through `_compare_parsed` (unchanged), which covers the "Figure files" hashes, the captions and the image lines;
   - each committed data CSV against its rows, by `key`: missing, extra or changed rows, naming the file, key, column, both values and the regenerated row's `source`;
   - each committed SVG's sha256 against the regenerated bytes. When a figure's data are equal but its SVG differs, the message says that the data are equal, so the drawing moved and not a result.
   - the directory's file list against the eighteen expected names.

All mismatches are printed, nothing is written, and the CLI exits 1 on any. A regenerated input therefore shows up three times: in its provenance cell, in the rows of each figure that reads it, and in those figures' SVGs. Each figure's `inputs` make the spec's "every figure that reads the file" direct to report.

### D10. Inputs: `stage_means.csv`

`REPORT_INPUT_FILES["analysis"]` becomes `(ANALYSIS_RESULT, ANALYSIS_MANIFEST, ANALYSIS_SUMMARY, ANALYSIS_STAGE_MEANS)`. Gate 2 checks it against `analysis_manifest.json`'s `outputs["stage_means.csv"]`, and its rerun hint is `analyze`. The latent arm's analysis role keeps its three files, because no figure reads the arm's stage means. Counts become 147 files, 45 manifests, 100 checked against a manifest, and 255 chain links (unchanged). The provenance gains one row.

### D11. Earlier layouts

`_check_report_layout` needs no new logic: the fifteen-title `REPORT_SECTIONS` makes every committed report stop at the section gate, with `Figures` absent. Its docstring and `run_report`'s gain the 2026-11-02-3 report, which checks at 9779964.

## Risks / Trade-offs

- **[SVG bytes differ on another machine]** Fonts, FreeType or float formatting could differ between machines. → The font is resolved by path from matplotlib's wheel, FreeType ships in that wheel, the numerics gate pins BLAS and numpy dispatch, and `rc_context` isolates user settings. The proposal's workflow checks the bytes on a second machine before the report is committed. If they differ, the change stops for diagnosis; weakening the check to the data alone would be a decision for the user, not a fallback.
- **[A figure invites a reading the rules forbid]** `f8` and `f9` set sensitivities side by side. → Each row or rank is drawn against the primary or its own null, nothing joins rows or ranks, the labels are the comparison's own statuses, and the caption states the rules. The figure's text is fixed and holds no result.
- **[A drawing bug passes the check]** The check compares the figures with themselves, regenerated. → The data CSV is read back and compared with the source values in the implementation's verification. Each figure is also rendered and looked at during implementation (tasks), as the drafts were.
- **[Repository growth]** About 1.2 MB per report re-issue. → Accepted for faithful rendering. Text kept as text would be 370 KB, but GitHub would render it in fallback fonts.
- **[matplotlib pin against MOTCO's]** A MOTCO move could require another matplotlib. → A MOTCO move re-issues the report anyway (constraint 4), and the matplotlib pin moves in that change.
- **[Heavier `report`]** matplotlib adds about a second of import time. → It is imported only by `report`.

## Migration Plan

1. Implement and verify on the committed tree and on scratch edits.
2. Write the next report with its figures on the clean tree, check it here and on a second machine, and commit the report and `reports/figures/<stem>/` alone.

Rollback is reverting the commits: earlier reports and their checks at their own revisions are untouched.
