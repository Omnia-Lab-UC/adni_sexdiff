# Tasks

Nothing runs on ADNI data until the user has accepted the proposal's scientific constants and they are in `constants.py` (task 1.1):
- `RANK_SENSITIVITY_LADDER`: `forced_rank_ladder`, ranks `(2, 3, 4, 6, 9, 12)`, the one setting `forced_components`, `ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS` at every rank, the anchor gate at the primary record's rank, the top rank diagnosed, every other setting the primary's;
- `RANK_SENSITIVITY_READING_RULES` (eight statements);
- the predeclared `RANK_SENSITIVITY_EXPECTED_COUNTS`.

The spike (`spike.md`) ran on 2026-10-30 on synthetic data only, before the constants were written. It read no ADNI file and fed the design and the reading rules, not a constant's value.

Every run is pinned, and every manifest records its `numerics`.

Groups 1 to 4 use synthetic data in the session scratchpad, never the real data root, and run on any machine.

Group 5 runs on one data machine, whose export, cohort and primary analysis files hash to the committed manifests. Every real-data task line names its hostname.

No task line records a participant value.

## 1. Constants and the synthetic baseline

- [x] 1.1 Add to `constants.py` (design D2):
  - the scientific `RANK_SENSITIVITY_LADDER`, with its three import-time assertions, and `RANK_SENSITIVITY_READING_RULES` (the proposal's eight statements, verbatim);
  - the predeclared `RANK_SENSITIVITY_EXPECTED_COUNTS` (`anchor`, `analysis` per rank, `comparison`, `diagnostics`);
  - the conventions `RANK_SENSITIVITY_DIR`, `RANK_SENSITIVITY_RANK_DIR`, `RANK_SENSITIVITY_SUBDIRS` and the three comparison names;
  - the module docstring naming the change and its constants.

  Update `AGENTS.md` for the constants: constraint 5's decided list, "Flag and ask" with the two constants, their values and the predeclared counts, and the Layout entry for `constants.py`.

  Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; e=c.RANK_SENSITIVITY_EXPECTED_COUNTS; print(c.RANK_SENSITIVITY_LADDER['ranks'], len(c.RANK_SENSITIVITY_READING_RULES), e['anchor']['rank'], e['analysis'][12]['selected_rank'], e['analysis'][12]['component_selection'], e['comparison']['rows'], e['diagnostics']['rows'])"` prints `(2, 3, 4, 6, 9, 12)`, `8`, `8`, `12`, `forced`, `7` and the rows 96 / 48 / 48 / 12;
  - each assertion fails on a scratch copy of `constants.py` with, in turn, an unsorted ladder, a lowest rank of 3 and a diagnosed rank of 9;
  - `grep -n RANK_SENSITIVITY AGENTS.md` lists the constraint 5, "Flag and ask" and Layout lines.
- [x] 1.2 Confirm that the existing ignore rules cover the sweep (design D2). `git check-ignore -v --no-index` must ignore `results/motco_rank_sensitivity/rank_02/latent_scores.csv`, `.../rank_02/analysis_metadata.csv`, `.../rank_12/latent_scores.csv`, `.../rank_12/analysis_metadata.csv` and `.../anchor.tmp/latent_scores.csv`. It must not ignore `.../rank_02/summary.md`, `.../rank_12/result.json` or `.../comparison/rank_sensitivity.md`. Verify that `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged (`git diff --stat`).
- [x] 1.3 In the session scratchpad, reuse or rebuild the synthetic fixtures of `adni-stage-sensitivity` (`make_synthetic.py`, with all five `dx_bl` categories, SMC and EMCI only in `ADNI2GO`). With today's code, run into `syn/A/`, at 99 permutations:
  - the primary export, the analysis and `axis-diagnostics`;
  - the latent arm, both export variants and the CN / LMCI / AD arm, each with its diagnostics.

  These are the byte-identity baseline for the shared code (design D10). Verify that every step completes and the manifests chain.

## 2. `forced_components` through the shared analysis

- [x] 2.1 Give `_run_trajectory_analysis` and `_analysis_cli_equivalent` the `forced_components` keyword (design D4), and make the three CV findings forced-aware (design D5). Update both docstrings. Verify:
  - rerunning the primary, the latent arm, both variants and the CN / LMCI / AD arm into `syn/B/`: every non-JSON output is byte-identical to `syn/A/`, and the manifests are equal apart from time, runtime and revision;
  - a synthetic forced run at rank 3 records `settings.forced_components` 3, carries `--forced-components 3` in its `cli_equivalent`, and raises no CV-repeats, CV-floor or moved-default finding;
  - a forced run whose record is edited in a scratch copy to `forced_components` 4 raises the moved-default finding;
  - `motco analyze` run from that `cli_equivalent` gives equal `statistics`, `p_values` and `null_summary`, and byte-identical `latent_scores.csv`, `pls_loadings.csv` and `stage_means.csv`.
- [x] 2.2 Give `render_analysis_summary` its `rank_sweep` branch and `_statistic_reading_line` its `rank_sweep` note (design D6), and update both docstrings. Verify:
  - `syn/B/`'s `summary.md`, comparison `.md` and `diagnostics.md` files are byte-identical to `syn/A/`'s;
  - a forced summary names the rank in its title and header, has no "CV-selected", has a "Rank sweep" section with the nesting and the anchor, and prints `READING_RULES` then the eight sweep rules, string-equal to the constant.

## 3. The `rank-sensitivity` step

- [x] 3.1 Implement the input checks and the anchor gate (design D3; D7 steps 1–5). On scratch copies, verify that each case below stops naming the file or setting, both values and the command to rerun, and that nothing is created under the output root except, in (e) and (f), the kept `anchor.tmp/`:
  - (a) an absent primary analysis;
  - (b) a primary `nmr.csv` changed after the analysis;
  - (c) the latent arm's `analysis/` given as `--analysis-dir`;
  - (d) an existing output without `--force`;
  - (e) a primary manifest whose recorded `latent_scores.csv` sha256 is edited: the anchor stops naming the file and both hashes;
  - (f) a primary `result.json` with one p-value edited, and the manifest's recorded hash updated to match: the anchor stops naming `p_values`, the statistic and both values.

  Also verify that at `--n-jobs 4` the anchor passes on the comparison D3 restricts it to, and records the fields it did not compare.
- [x] 3.2 Implement the sweep, the staging, the nesting check and the comparison (design D7): `run_rank_sensitivity`, `render_rank_sensitivity` and `_rank_status_line`, with their docstrings. Verify at 99 permutations on the synthetic data:
  - the layout of the spec: six rank directories and `comparison/`, with no `.tmp/` and no `anchor.tmp/` left;
  - each rank manifest's step, ladder, forced rank, reference hashes, anchor record and `numerics`;
  - deviations naming the synthetic sizes, and none naming the forced rank or the selection;
  - the nesting booleans true for every rank;
  - every value in `rank_sensitivity.csv` equal to its source record, and 7 rows;
  - an edited scratch record whose status differs at one rank prints `differs (rank dependence)` at that rank only, with a finding;
  - the reading lines string-equal to `_statistic_reading_line`'s;
  - `--force` with an existing `diagnostics/` records the stale-diagnostics finding;
  - every primary, latent-arm, variant and stage-arm tree hashes the same before and after;
  - two `--force` runs give byte-identical non-JSON outputs.
- [x] 3.3 Add the `rank-sensitivity` subcommand (design D9), with `[rank-sensitivity]` progress lines naming counts and files only. Verify that `--help` lists `--input-dir`, `--analysis-dir`, `--out-dir`, `--n-jobs` and `--force`, and that no flag sets, adds or removes a rank.
- [x] 3.4 Document the step:
  - `README.md`: a `rank-sensitivity` section covering the command, the ladder, the anchor gate, the inputs, the outputs and which are participant-level, the predeclared counts, the diagnostic of the top rank, and the reading rules;
  - `AGENTS.md`: the status, the step listed under 5 as a sensitivity step beside the other three, constraint 1's committed outputs, the commands, and the Layout entries for `cli.py` and `data.py`.

  Verify with `grep -n rank-sensitivity README.md AGENTS.md`, and that the README command runs as written on the synthetic data.

## 4. Diagnostics read a forced rank as the sweep's

- [x] 4.1 Make `run_axis_diagnostics`, `render_axis_diagnostics`, `_analysis_command`, `_ANALYSIS_STEPS` and `_EVERY_ANALYSIS_COMMAND` sweep-aware (design D8), with their docstrings. Verify:
  - the synthetic diagnostics of the primary, the latent arm, both variants and the CN / LMCI / AD arm are byte-identical to `syn/A/`'s;
  - `axis-diagnostics --analysis-dir <syn>/rank_12 --out-dir <syn>/diagnostics` passes its chain checks, records `rank_sweep` and `is_primary` false, expects the rank-12 rows, and writes a `diagnostics.md` that names the sweep and the rank and prints both sets of rules;
  - its `axis_correlations.csv` rows for the components up to the synthetic primary's rank, and its whole `block_pcs.csv`, equal the synthetic primary diagnostic's;
  - on `rank_04`, only the rank-independent keys are expected, and the top-rank finding is recorded.
- [x] 4.2 Document the sweep read: the diagnostics paragraph of `README.md` and step 5 of `AGENTS.md` (the sweep read, its expectations and its rules). Verify with `grep -n "rank_12\|rank sweep" README.md AGENTS.md`.

## 5. The real run (data machine)

- [x] 5.1 Confirm the data machine (hostname recorded): the six primary export files, `cohort.csv`, and the primary's `latent_scores.csv` and `analysis_metadata.csv` hash to the committed manifests.

  Done 2026-10-30 on nixos-office: all nine files hash to the values the committed export, cohort and analysis manifests record.
- [x] 5.2 Run the exact gates on real data (design D10), each into a scratch directory:
  - pinned `analyze`: the committed primary hashes;
  - `axis-diagnostics` on the primary, the latent arm, both variants and the CN / LMCI / AD arm: their committed four CSVs and `diagnostics.md`;
  - `latent-sensitivity`, `export-sensitivity --variant all` and `stage-sensitivity`: their committed `summary.md` and comparison `.csv` and `.md`, with `latent_sensitivity.md` line 3 excepted as before;
  - `report --check` on the committed tree.

  Any difference stops the change and reverts the shared code edit.

  Done 2026-10-30 on nixos-office, on the uncommitted implementation, in a scratch mirror under `results/gates.tmp/` (ignored, never synced) whose `cleaned/`, `cohort/`, `motco_input/` and `motco_analysis/` were symlinks to `results/` (so every printed path is the committed one) and whose own `data/` linked every entry of the data root plus the two QC archives (this machine's data root lacks the two archive symlinks, so it was left untouched); every run pinned (17 manifests). `analyze --out-dir <scratch>`: `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `summary.md` have the committed hashes, `result.json` equal apart from MOTCO's runtime. `axis-diagnostics` on the primary, `latent-sensitivity`, `export-sensitivity --variant all` and `stage-sensitivity`, each with its diagnostics: 45 of the 46 committed non-JSON files byte-identical, the other line 3 of `latent_sensitivity.md` (the latent arm's `result.json` hash, MOTCO's runtime; equal with the hashes masked, as before); the 20 participant-level files of the arms and variants have the committed hashes; every `result.json` equal apart from runtime. `report --check` on the committed tree: 71 tables, 3546 cells, 680 other lines, no mismatch. Scratch mirror deleted.
- [x] 5.3 Run `rank-sensitivity` pinned at `n_jobs = 1`. Verify:
  - the anchor at rank 8 passes, with every field and all three files equal;
  - no deviation from `RANK_SENSITIVITY_EXPECTED_COUNTS` in any rank manifest or the comparison manifest;
  - the nesting booleans true for every rank;
  - every `numerics.pinned` true.

  Record the statistics and statuses in this task line only by pointing to the committed files.

  Done 2026-10-30 on nixos-office, on the uncommitted implementation (rerun on the clean tree in 5.6, whose outputs are the committed ones), in 20 s: the anchor at rank 8 equals the primary in `statistics`, `p_values`, `null_summary`, `config_spectrum` and `selected_lv` and in the hashes of `latent_scores.csv`, `pls_loadings.csv` and `stage_means.csv`; no deviation in the six rank manifests or the comparison manifest; nesting true for every rank (the first columns of rank 12's and of the anchor's); every `numerics.pinned` true; every other file under `results/` unchanged. `rank_sensitivity.csv` holds 7 rows, every value equal to its record. Statistics and statuses: `results/motco_rank_sensitivity/comparison/rank_sensitivity.csv` and `.md`; the one finding is a status that differs at one rank (rank dependence), named there.
- [x] 5.4 Reproduce `rank_04` and `rank_12` with MOTCO's CLI (each manifest's `cli_equivalent`, into scratch directories): equal statistics, p-values, null summaries and rank, and byte-identical `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv`. Then run `--n-jobs 4` into a scratch root. Verify the not-reported finding, the restricted anchor comparison and "not a reported run" in `summary.md` and `rank_sensitivity.md`. Delete the scratch directories.

  Done 2026-10-30 on nixos-office, with `NUMERIC_SETTINGS` exported, scratch directories under the ignored `results/*.tmp/`: `motco analyze` from the `cli_equivalent` of `rank_04` and `rank_12` (each carrying `--forced-components`) gives equal `statistics`, `p_values`, `null_summary` and forced rank, and byte-identical `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv`. `rank-sensitivity --n-jobs 4` into a scratch root: the anchor passes on `statistics`, `selected_lv`, `config_spectrum.pooled` and the three files and records `p_values`, `null_summary` and `config_spectrum.permutation_pooled_eigengap` as not compared; the n_jobs finding in every rank manifest and the comparison manifest; "not a reported run" in every `summary.md` and in `rank_sensitivity.md`. Both scratch directories deleted.
- [x] 5.5 Run `axis-diagnostics --analysis-dir results/motco_rank_sensitivity/rank_12 --out-dir results/motco_rank_sensitivity/diagnostics`. Verify:
  - the export, analysis and cohort chains pass;
  - `is_primary` is false and `rank_sweep` is 12;
  - there is no deviation on the expected keys;
  - its rows for `pls_0` to `pls_7` in `axis_correlations.csv`, and its whole `block_pcs.csv`, equal the committed `results/motco_diagnostics/` files (design D8).

  Done 2026-10-30 on nixos-office, on the uncommitted implementation: the export, analysis and cohort chains pass (1501 both-flag rows, the exported participants in order); `is_primary` false, `rank_sweep` forced rank 12 with the primary's rank 8; no deviation on the expected keys (the rank-independent keys, the read rank 12 `forced` with no latent adjustment and `n_jobs` 1, rows 96 / 48 / 48 / 12); `numerics.pinned` true; the `pls_0` … `pls_7` rows of `axis_correlations.csv` equal the committed primary diagnostic's, and `block_pcs.csv` is byte-identical to it; `diagnostics.md` names forced rank 12 of the sweep, states that `pls_0` to `pls_7` are the primary's and prints both sets of rules. The flagged rows are in `diagnostics/diagnostics.md`.
- [x] 5.6 Rerun 5.3 and 5.5 with `--force` on the clean tree after the implementation commit, with the first run's `diagnostics/` moved aside so that no stale-diagnostics finding enters the committed outputs. Verify:
  - every non-JSON output is byte-identical to the first run;
  - the manifests are equal apart from time, revision, MOTCO's runtime and the hashes of the files that carry them.

  These are the committed outputs.

  Done 2026-10-30 on nixos-office at `08e5ddc`, clean: a scratch copy of the first run kept under the ignored `results/*.tmp/`, the first run's `diagnostics/` removed, `rank-sensitivity --force` and `axis-diagnostics` on `rank_12` rerun (no stale-diagnostics finding). Against the first run: the 37 non-JSON files (every CSV, `summary.md`, `rank_sensitivity.md`, `diagnostics.md`) byte-identical; the eight manifests and six `result.json` equal apart from time, revision (dirty → clean), MOTCO's runtime and the hashes and sizes of `manifest.json`, `result.json` and `analysis_manifest.json`, which carry them; no deviation; every `numerics.pinned` true; scratch copy deleted.

## 6. Commit hygiene

- [x] 6.1 Before the commit of outputs, name every file added under `results/motco_rank_sensitivity/` (39: five per rank, three in `comparison/`, six in `diagnostics/`) with why it is aggregate. Verify:
  - `git check-ignore` matches the twelve participant-level files (`latent_scores.csv` and `analysis_metadata.csv` per rank);
  - `scripts/sync_results.sh --dry-run` lists none of them;
  - no staged CSV has an `rid` or `RID` column, and `grep -w` finds `rid` only as a column name;
  - `openspec validate adni-rank-sensitivity --strict` passes;
  - `report --check` still passes on the committed report.

  Done 2026-10-30 on nixos-office. The 39 files, each aggregate: per rank (`rank_02`, `rank_03`, `rank_04`, `rank_06`, `rank_09`, `rank_12`) `result.json` (statistics, p-values, null summaries, the design and latent blocks), `pls_loadings.csv` (one row per metabolite), `stage_means.csv` (one row per sex × stage cell), `analysis_manifest.json` (hashes, settings, counts, findings) and `summary.md`; `comparison/` `rank_sensitivity.csv` (the primary row and one row per rank), `rank_sensitivity.md` and `rank_sensitivity_manifest.json`; `diagnostics/` `axis_correlations.csv`, `block_pcs.csv`, `geometry_shares.csv` and `components.csv` (per component, block and variable), `diagnostics.md` and `diagnostics_manifest.json`. `git check-ignore` matches the twelve participant-level files and none of the 39; a local dry-run push of `sync_results.sh` (`--push -n` into an empty scratch target) lists the 39 and none of the twelve; no CSV has an `rid` or `RID` column and `grep -w` finds `rid` only as the sample column (`sample_col`, `sample_column`, `--sample-col rid`); `openspec validate adni-rank-sensitivity --strict` passes; `report --check` on the committed report: 71 tables, 3546 cells, 680 other lines, no mismatch. Committed as `7da3750`.

## Workflow follow-up

- Archive the change on its branch, sync the specs, open the PR and merge, as the earlier changes did.
- The follow-up change that adds the sweep to `report`: a section, its inputs in `REPORT_INPUT_FILES` and its chain links. Until then the committed report stays valid.
- Then, each its own proposal: the other export variants (all 245 NMR columns first). The cluster run waits on the deploy key (constraint 7).
