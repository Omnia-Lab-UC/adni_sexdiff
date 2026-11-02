# Tasks

This change introduces no scientific constant (proposal, What Changes). While this proposal was written, the user chose to keep all nine draft figures, to give each one a description beyond its axes, and to have `report` draw them (design D1).

Before the apply starts, the user accepts:
- the "Figures" section as the second of fifteen, and its layout (design D2);
- the files, SVG with text drawn as paths plus a data CSV per figure, under `reports/figures/<stem>/` (design D3, D4);
- the nine titles, subtitles and reading texts, and the generated lines and rules per figure (design D5);
- `f6` with all eight exports, and the in-figure text stating no result (design D6);
- `matplotlib==3.11.2` as a direct pin, and the numerics gate on the report run (design D7).

Every task runs on any machine with the Nix shell and the committed tree, except task 7.2, which needs a second machine. The inputs are the tracked files under `results/` and `references/`. No data root, data machine or participant-level file is needed, and the step makes no MOTCO call. Scratch copies and outputs live in the session scratchpad, never under `results/`, `references/` or `reports/`, except in task 7.1. No task line records a participant value.

## 1. The pin and the conventions

- [x] 1.1 Run `uv add "matplotlib==3.11.2"` (design D7). Verify:
  - `git diff uv.lock` shows only the new direct requirement, with matplotlib still at 3.11.2;
  - `uv sync --locked` passes;
  - `uv run python -c "import matplotlib; print(matplotlib.__version__)"` prints `3.11.2`.
- [x] 1.2 Add the conventions to `constants.py` (design D3, D5, D6, D10):
  - `MATPLOTLIB_VERSION` and `REPORT_FIGURES_DIR`;
  - `FIGURE_STYLE`, with the palette, `svg.fonttype` `path`, `svg.hashsalt` `adni-sexdiff`, and the bundled font by file name;
  - `REPORT_FIGURES`, nine entries with the design's titles, subtitles and reading texts verbatim, their inputs, generated lines and rules;
  - "Figures" second in `REPORT_SECTIONS`;
  - `ANALYSIS_STAGE_MEANS` in the `analysis` role of `REPORT_INPUT_FILES`;
  - import-time assertions that every figure input is a path of `REPORT_INPUT_FILES`, and that every rule name is a tuple of the module;
  - the module docstring.

  Verify:
  - the constants print `9` figures, `15` sections and `147` input files;
  - a script finds each title, subtitle and reading text string-equal to design D5;
  - in a scratch copy of `src/`, a figure input outside `REPORT_INPUT_FILES` fails the import naming both constants.
- [x] 1.3 Add `check_matplotlib_version()` to `data.py`, modelled on `check_metabo_adni_version` (design D7). Verify that the installed version passes, and that a version patched in-process stops with both versions and `uv sync --locked`.
- [x] 1.4 Update `AGENTS.md` and `README.md` for the pin and the conventions:
  - the dependencies (matplotlib exact, why);
  - constraint 1's committed aggregate files (`reports/figures/<stem>/`, SVG and data CSV);
  - the Layout entries (`figures.py`, matplotlib imported by `report` only; `reports/figures/`);
  - the `constants.py` entry (the conventions).

  Verify with `grep -n "matplotlib\|reports/figures\|REPORT_FIGURES" AGENTS.md README.md`, which shows every entry.

## 2. The new input

- [x] 2.1 Read `stage_means.csv` in `_load_report_inputs`, checked in gate 2 against `analysis_manifest.json`'s `outputs`, with `analyze` as its rerun hint, and give it a provenance row (design D10). Verify on the committed tree:
  - 147 files hashed;
  - 100 checked against `outputs`, 1 against `bridge.table.sha256`, 1 against the constant, 45 manifests;
  - 255 chain links, every one `ok`;
  - the step's findings are still the five manifests without `numerics`.
- [x] 2.2 On scratch copies of the tracked files, run two cases:
  - (a) `stage_means.csv` deleted → stops naming the file and `analyze`;
  - (b) one byte changed → stops naming the file, both hashes and `analyze`.

  Each must exit 1, create no `reports/`, and leave every file unchanged (hashed before and after). Record both outcomes in this line. Outcome (2026-11-02, scratch copies of the tracked `results/` and `references/` at 41fee8e): (a) exit 1, "1 report input(s) absent: results/motco_analysis/stage_means.csv (run `adni-sexdiff analyze`); nothing was written"; (b) exit 1, "results/motco_analysis/stage_means.csv: sha256 1745bad8… differs from the hash results/motco_analysis/analysis_manifest.json records (fc32d435…); rerun `adni-sexdiff analyze` (then every step after it); nothing was written"; in both no `reports/` was created and every file hashed equal before and after.
- [x] 2.3 Update `AGENTS.md` step 6 and `run_report`'s docstring with the counts: 147 inputs, 100 checked against a manifest, the primary's four files. Verify with `grep -n "147\|146" AGENTS.md src/adni_sexdiff/data.py`, which shows no stale count.

## 3. The figure data

- [x] 3.1 In the new `src/adni_sexdiff/figures.py`, implement `figure_rows(inputs)`: per figure the rows `key`, `quantity`, `value`, `source`, `field` in drawing order (design D4, D11). This includes `absent` rows for `f1`, the bridge summary's counts for `f7`, the comparison statuses for `f8`, and the constants as sources for the reference lines. Verify on the committed tree with a script that re-reads every row's source at its field and finds the value equal, and that checks:
  - `f1`'s `absent` rows are exactly the cells `stage_counts.csv` does not list;
  - every source is a path of `REPORT_INPUT_FILES` or `constants.<NAME>`;
  - no row holds `RID` or a `rid` value.

  Record the rows per figure in this line. Outcome (2026-11-02, committed tree at 41fee8e): every row's value equals its source re-read at its field; every source is a path of `REPORT_INPUT_FILES` or `constants.<NAME>`; `f1`'s 4 `absent` rows are exactly the sex × `DX.bl` × run cells `stage_counts.csv` does not list (SMC and EMCI in ADNI1, per sex); no `RID` token. Searched against the 1501 exported `rid` values, 28 cells equal one: all are counts or ranks (`f1` participants, `f7` unbridged count, `f8` and `f9` ranks) that coincide with small integer `rid` values, the same numbers the committed `stage_counts.csv` and reports print; no identifier. Rows: f1 22, f2 64, f3 22, f4 62, f5 274, f6 49, f7 543, f8 147, f9 91 (1274). The `f8` inputs include each comparison's manifest beside its table, the source of the statuses (`counts.statuses`).
- [x] 3.2 Write the rows as CSV bytes (`\n` line endings, minimal quoting, a final newline) and read them back equal. Verify that building the rows twice gives identical bytes.

## 4. The drawing

- [x] 4.1 Implement the drawing frame in `figures.py` (design D6):
  - `matplotlib.figure.Figure` with the SVG canvas;
  - `rc_context` on `rcParamsDefault` plus `FIGURE_STYLE`;
  - the bundled `DejaVuSans.ttf` by path;
  - metadata `Title`, `Description` (inputs with sha256), `Creator` and `Date` `None`;
  - output to a bytes buffer.

  Verify:
  - two draws in one process, and in two processes, give identical bytes;
  - with `MATPLOTLIBRC` pointing to a scratch file that changes `svg.fonttype`, `font.size` and `font.family`, the bytes are unchanged;
  - the SVG holds no `<text>` element;
  - its metadata names every input with its sha256.
- [x] 4.2 Draw the nine figures from the rows, porting the scratch drafts with design D5 and D6's changes:
  - fixed titles and subtitles;
  - `f6` with eight exports grouped as in `f8`;
  - no line joining ranks or rows;
  - every printed number through the report's formatter for its value.

  Verify:
  - render each to PNG in the scratch directory with the same `Figure`, and look at each for overlap, clipping and legibility;
  - in a scratch render with `svg.fonttype` `none`, a script lists every text string and finds each number equal to the report's formatting of its row value, and no draft result subtitle.

  Record the review in this line. Outcome (2026-11-02): PNGs of the nine `Figure`s rendered in the scratch directory and looked at; fixed before recording: gridlines drawn over bars and boxes (`axes.axisbelow` added to `FIGURE_STYLE`), tick marks on shared y axes (`f1`, `f6`, `f8`), the first y label clipped in `f4`, the loading-share title clipped in `f5`; no overlap, clipping or illegible text remains. With `svg.fonttype` `none`, every string was listed (512 in the nine, 285 of them tick labels): every number outside a tick label equals the report's formatting of a row value of its figure, or a digit of its fixed title, subtitle or footer; tick labels are axis scale, except the ranks of `f8`'s row labels and `f9`'s ticks, printed with `_count` from their rows; no draft result subtitle remains. Two draws in one process and in two processes, and a draw under a `MATPLOTLIBRC` setting `svg.fonttype`, `font.size` and `font.family`, gave identical bytes; no SVG holds a `<text>`, `<image>` or date element, and each names its title, its inputs with their sha256 and matplotlib 3.11.2 in its metadata.
- [x] 4.3 Add the numerics gate after the figures are drawn and before anything is written (design D7). Verify:
  - on the committed tree the state is pinned;
  - a script that imports numpy before `adni_sexdiff` and calls the report stops naming the settings that differ, and writes nothing.

## 5. The section and writing

- [x] 5.1 Render the "Figures" section in `render_report` (design D2, D5): the lead, `### Figure files`, then per figure the heading, the image line and the caption. The generated lines must come from the functions that print them elsewhere. Verify on the committed tree with a script that checks:
  - each reading paragraph is string-equal to `REPORT_FIGURES`;
  - each generated line is string-equal to its line elsewhere in the same report (`f3` to `summary.md`);
  - `f8`'s lines are the two differing statuses;
  - every "section N" reference follows the fifteen sections;
  - `parse_report` finds "Figure files" with nine rows.
- [x] 5.2 Write the report and figures as design D8 describes: staged together, parsed and read back, renamed together, with `--force` and the existing-directory gate. Verify in a scratch copy:
  - two `--force` runs to one `--out` give equal sha256 for the report and all eighteen files;
  - runs to `motco-adni-2026-11-02.md` and `-2.md` differ only in the title line and the figures directory lines, with identical figure files;
  - an existing `reports/figures/<stem>/` without the report and without `--force` stops naming the directory;
  - a draw that raises (patched in-process) leaves no report, no figure and no temporary.
- [x] 5.3 Update the docs for groups 3 to 5:
  - `run_report` and `render_report` docstrings, the section, files, captions and gates;
  - `AGENTS.md` step 6 (the fifteen sections, the figures, the version and numerics gates);
  - `README.md` (the report's figures);
  - `cli.py` `report` help (the figures directory follows `--out`).

  Verify with `uv run adni-sexdiff report --help` and `grep -n "Figures\|figures/" AGENTS.md README.md`.

## 6. The check

- [x] 6.1 Extend `check_report` (design D9): the version gate, then the regenerated rows and SVG bytes, the data compared cell by cell, the SVGs by sha256, and the directory listing. Run each case in a scratch copy holding a report just written; each must name what the spec's scenarios name, exit 1 (the first case 0) and write nothing:
  - (a) unchanged → no mismatch, exit 0;
  - (b) one value of `f8_sensitivities.csv` edited → the file, key, column, both values and source;
  - (c) `f4`'s SVG with one byte changed → the file, both sha256, and that its data are equal;
  - (d) `f5`'s CSV deleted and an extra file added → both named;
  - (e) one value of the primary's `geometry_shares.csv` changed, with the diagnostics manifest's recorded hash updated → the provenance cell, `f2`'s row and `f2`'s SVG;
  - (f) matplotlib's version patched in-process → stops before any comparison.

  Record the six outcomes in this line. Outcome (2026-11-02, scratch copies of a tree holding a report just written from the committed outputs; every file hashed equal before and after in all six): (a) exit 0, "113 tables, 7568 cells and 1385 other lines of the report; 9 data CSVs (1274 rows) cell by cell and 9 SVGs by their bytes … compared; no mismatch"; (b) exit 1, one mismatch: `f8_sensitivities.csv › row rank_06|delta|p › value: committed '0.0499', generated '0.0471' (source results/motco_rank_sensitivity/comparison/rank_sensitivity.csv, field analysis=rank_06:delta_p)`; (c) exit 1, one mismatch: `f4_operating_characteristics.svg: sha256 aff65af2… committed, 480100dd… generated; its data CSV equals the regenerated data, so the drawing moved, not a result`; (d) exit 1, two mismatches: the directory's missing `f5_axis_diagnostics.csv` and extra `notes.txt`; (e) exit 1, six mismatches: the provenance cells of `geometry_shares.csv` and of `diagnostics_manifest.json`, `f2_trajectories`'s `svg sha256` and `data sha256` in "Figure files", `f2_trajectories.csv › row pls_0|share › value` with its source and field, and `f2_trajectories.svg` with both sha256 ("its data differ too"); (f) exit 1 before any input was read and before any comparison: "matplotlib 3.10.7 is installed but the pin is 3.11.2 (MATPLOTLIB_VERSION) … run `uv sync --locked` …; nothing was written".
- [x] 6.2 Check the earlier-layout gate on the committed reports:
  - `report --check --out reports/motco-adni-2026-11-02-3.md` stops naming the absent `Figures` and the `git log` command;
  - `--out reports/motco-adni-2026-10-28.md` names `Figures` among its absent sections.

  Update `_check_report_layout`'s and `run_report`'s docstrings with 9779964. Record the messages in this line. Outcome (2026-11-02, committed tree): both exit 1 at the section gate, before any input gate, comparing no cell and writing nothing. 2026-11-02-3: "reports/motco-adni-2026-11-02-3.md was written by an earlier layout of `report`: its level-2 sections are not REPORT_SECTIONS (absent: 'Figures'; extra: none). It checks at the revision that committed it: `git log -1 --format=%H -- reports/motco-adni-2026-11-02-3.md` …" (that command gives 9779964). 2026-10-28: the same message with "absent: 'Figures', 'Operating characteristics', 'Export sensitivity', 'Stage-definition sensitivity', 'Rank sensitivity'; extra: none".

## 7. The report

- [ ] 7.1 On the clean tree, after the implementation is committed, run `uv run adni-sexdiff report` (today's name, or `--out` with the day's next free name). Verify:
  - it writes the report and `reports/figures/<stem>/` (eighteen files);
  - `report --check` passes;
  - PNG renders in the scratch directory look right;
  - `grep -rn "RID" reports/figures/<stem>/` finds nothing.

  Update the status paragraph of `AGENTS.md` (the newest report, the default of `--check`) in a separate commit.
- [ ] 7.2 On a second machine (the cluster login node once the clone exists, or another of the user's machines) with the same lock, run `uv sync --locked` and then `uv run adni-sexdiff report --check` on the branch. Verify that it passes, every SVG included. Record the machine's CPU and the outcome in this line. If an SVG differs, stop and diagnose (design, Risks) before committing the report.
- [ ] 7.3 Commit the report and its figures directory alone, naming every file added and why it is aggregate. Verify with `git show --stat HEAD`, which lists the report and the eighteen figure files only.

## Workflow follow-up

- Archive the change (`openspec archive adni-report-figures`), which syncs the delta into `openspec/specs/case-study-report/spec.md`.
- Open the PR to `main`.
