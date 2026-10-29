# Tasks

Nothing runs on ADNI data until the user has accepted the proposal's scientific constants and they are in `constants.py` (task 1.1):
- `STAGE_SENSITIVITY_ARM`: `cn_lmci_ad`, keep CN / LMCI / AD, drop SMC / EMCI, `STAGE_RULE`'s map, the primary's floors, the primary's analysis settings;
- `STAGE_SENSITIVITY_READING_RULES` (eight statements);
- the predeclared `STAGE_SENSITIVITY_EXPECTED_COUNTS`.

The spike (`spike.md`) ran on nixos-home on 2026-10-29 before the constants were written. It is read-only and aggregate and fed only the predeclared counts.

Every run is pinned, and every manifest records its `numerics`.

Groups 1 to 4 use synthetic data in the session scratchpad, never the real data root, and run on any machine.

Groups 5 and 6 run on one data machine, whose cohort, export and primary analysis files hash to the committed manifests. Every real-data task line names its hostname.

No task line records a participant value.

## 1. Constants, ignore patterns and the synthetic baseline

- [x] 1.1 Add to `constants.py` (design D4):
  - the scientific `STAGE_SENSITIVITY_ARM`, with the three import-time assertions tying it to `STAGE_RULE`, and `STAGE_SENSITIVITY_READING_RULES` (the proposal's eight statements, verbatim);
  - the predeclared `STAGE_SENSITIVITY_EXPECTED_COUNTS` (`export`, `analysis`, `diagnostics`);
  - the conventions `STAGE_SENSITIVITY_DIR`, `STAGE_SENSITIVITY_SUBDIRS` and the three comparison names;
  - the docstring naming the change and its constants.

  Verify with `uv run python -c "from adni_sexdiff import constants as c; print(c.STAGE_SENSITIVITY_ARM['name'], c.STAGE_SENSITIVITY_ARM['keep'], len(c.STAGE_SENSITIVITY_READING_RULES), c.STAGE_SENSITIVITY_EXPECTED_COUNTS['export']['participants'], c.STAGE_SENSITIVITY_EXPECTED_COUNTS['analysis']['covariate_levels']['apoe4'])"`, which must print `cn_lmci_ad`, the three kept categories, `8`, `1130` and 589 / 413 / 128. Also verify that each assertion fails on a scratch copy of `constants.py` with a broken map.
- [x] 1.2 Add `results/motco_stage_sensitivity/motco_input/*.csv` to `.gitignore`, the exclude filter of `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS`. Verify:
  - `git check-ignore -v --no-index` ignores `results/motco_stage_sensitivity/motco_input/p180.csv`, `.../motco_input/metadata.csv`, `.../analysis/latent_scores.csv` and `.../analysis/analysis_metadata.csv`;
  - it does not ignore `.../motco_input/manifest.json`, `.../analysis/summary.md` or `.../comparison/stage_sensitivity.md`;
  - `sync_results.sh --dry-run` lists none of the ignored four.
- [x] 1.3 In the session scratchpad, reuse or rebuild the synthetic fixtures of `adni-nist-bridge` (`make_synthetic.py`). The synthetic `cohort.csv` must hold all five `dx_bl` categories, with SMC and EMCI only in `ADNI2GO`. Run the primary export, the analysis (99 permutations) and `axis-diagnostics` with today's code into `syn/A/`, plus the latent arm and both export variants with their diagnostics. These are the byte-identity baseline for the shared renderers. Verify that every step completes and the manifests chain.

## 2. The arm export

- [x] 2.1 Implement the input checks (design D3, D6 steps 1–5): the MOTCO gates, the existing outputs, `_load_analysis_inputs` on the primary export, `_check_primary_reference` with step `stage-sensitivity`, `_check_cohort_chain`, a `dx_bl` outside `STAGE_RULE`, and a kept row whose stage differs from the arm's map. On scratch copies, verify that each of these stops naming the file or setting, both values or counts and the command to rerun, with nothing created under the output root:
  - (a) an absent primary analysis;
  - (b) a primary `nmr.csv` changed after the analysis;
  - (c) a primary manifest with a latent adjustment;
  - (d) a `cohort_manifest.json` changed after the export;
  - (e) a `cohort.csv` with its both-flag rows reordered;
  - (f) a `dx_bl` value outside the rule;
  - (g) an existing output without `--force`.
- [x] 2.2 Implement the arm export (design D2, D5): the text copy of the header and the kept lines of the four CSVs, the line-count and `rid` checks, the read-back equality, and the manifest with the contract keys, the counts, the reference and `rows_equal_primary`. Verify on the synthetic data:
  - every kept line is byte-identical to the primary's line for that participant;
  - `_load_analysis_inputs` accepts the directory;
  - the counts (kept, dropped per `dx_bl`, cells, runs within stage, levels, run offset) equal values computed by hand in the scratchpad;
  - permuting sex in the synthetic `cohort.csv` and `metadata.csv` together changes no kept line of `p180.csv` or `nmr.csv`.

## 3. The `stage-sensitivity` step

- [x] 3.1 Implement `run_stage_sensitivity` (design D6): the three staged directories, the analysis through `_run_trajectory_analysis` with the arm and the reference recorded, the comparison, the renames together, the predeclared counts and the findings. Verify at 99 permutations on the synthetic data:
  - the layout of the spec, with no `.tmp/` left;
  - the manifests' inputs, reference hashes and `numerics`;
  - deviations naming the synthetic sizes;
  - `--force` with an existing `diagnostics/` records the stale-diagnostics finding;
  - every primary, latent-arm and variant tree hashes the same before and after.
- [x] 3.2 Give `render_analysis_summary` the arm branch and `_statistic_reading_line` its `stage_arm` note (design D8). Verify:
  - the synthetic primary's, latent arm's and variants' `summary.md` and comparison `.md` files are byte-identical to the 1.3 baseline;
  - the arm's `summary.md` names the arm, carries the "Arm" section and prints `READING_RULES` then the eight arm rules, string-equal to the constant.
- [x] 3.3 Implement `render_stage_sensitivity` and `_stage_arm_status_line` (design D7). Verify on the synthetic run:
  - every value in `stage_sensitivity.csv` equals its source record;
  - a forced status difference (an edited scratch record) prints `differs (stage-definition dependence)` and a finding;
  - the reading lines are string-equal to `_statistic_reading_line`'s.
- [x] 3.4 Add the `stage-sensitivity` subcommand (`--input-dir`, `--analysis-dir`, `--cohort-dir`, `--out-dir`, `--n-jobs`, `--force`), with `[stage-sensitivity]` progress lines naming counts and files only. Verify that `--help` lists the flags and that no flag sets the arm, its categories or its floors.

## 4. Diagnostics read the arm as the arm

- [x] 4.1 Make `_check_cohort_chain`, `run_axis_diagnostics`, `render_axis_diagnostics`, `_analysis_command` and `_ANALYSIS_STEPS` arm-aware (design D9). Verify:
  - the synthetic primary's, latent arm's and variants' diagnostics outputs are byte-identical to the 1.3 baseline;
  - `axis-diagnostics --input-dir <arm>/motco_input --analysis-dir <arm>/analysis --out-dir <arm>/diagnostics` passes its chain checks, records `stage_arm` and `is_primary` false, expects the arm's participants and cells, and writes a `diagnostics.md` that names the arm and prints both sets of rules;
  - an arm manifest whose recorded cohort hash differs stops naming `stage-sensitivity`.

## 5. The real run (data machine)

- [x] 5.1 Confirm the data machine (hostname recorded): `cohort.csv`, the six primary export files, and the primary's `latent_scores.csv` and `analysis_metadata.csv` hash to the committed manifests.
  (Done 2026-10-29 on nixos-home: `cohort.csv` equals `cohort_manifest.json`, whose hash equals the export manifest's record; the six primary export files equal `manifest.json`; the primary's `latent_scores.csv` and `analysis_metadata.csv` equal its analysis manifest; so do both export variants' six export files and two participant-level analysis files. The latent arm's two participant-level files were made on nixos-office and are absent here; gate 5.2 regenerates them with the committed hashes.)
- [x] 5.2 Run the exact gates on real data (design D10), each into a scratch directory:
  - pinned `analyze`: the committed primary hashes;
  - `axis-diagnostics` on the primary, the latent arm and both variants: their committed four CSVs and `diagnostics.md`;
  - `latent-sensitivity` and `export-sensitivity --variant all`: their committed `summary.md`, comparison `.csv` and `.md`;
  - `report --check` on the committed tree.

  Any difference stops the change and reverts the renderer edit.

  Done 2026-10-29 on nixos-home, on the uncommitted implementation, in a scratch mirror whose `cleaned/`, `cohort/`, `motco_input/` and `motco_analysis/` were read-only symlinks to `results/` (so every printed path is the committed one); every run pinned. `analyze --out-dir <scratch>`: `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `summary.md` have the committed hashes, `result.json` equal apart from MOTCO's runtime. `axis-diagnostics` on the primary, `latent-sensitivity` with its diagnostics and `export-sensitivity --variant all` with both diagnostics: the 36 committed non-JSON files byte-identical, but line 3 of `latent_sensitivity.md`, which prints the latent arm's `result.json` hash (MOTCO's runtime; equal with the hashes masked, as before this change); the latent arm's and both variants' participant-level files have the committed hashes, every `result.json` equal apart from runtime. `report --check` on the committed tree: 58 tables, 2850 cells, 560 other lines, no mismatch. Scratch mirror deleted.
- [x] 5.3 Run `stage-sensitivity` pinned at `n_jobs = 1`. Verify:
  - no deviation from `STAGE_SENSITIVITY_EXPECTED_COUNTS` in the export, analysis or comparison manifest;
  - `rows_equal_primary` true for the four CSVs;
  - the run offsets equal the spike's (p180 median |d| 1.10, |d| > 0.5 / > 1 at 107 / 77, PC1 correlation 0.71);
  - every `numerics.pinned` is true.

  Record the rank, statistics and statuses in this task line only by pointing to the committed files.

  Done 2026-10-29 on nixos-home, on the uncommitted implementation (rerun on the clean tree in 5.6, whose outputs are the committed ones): no deviation in the export, analysis or comparison manifest; `rows_equal_primary` true for the four CSVs; p180 run offset on the arm's rows median |d| 1.10, |d| > 0.5 / > 1 at 107 / 77, |corr(PC1, phase)| 0.71 (|corr(PC2, phase)| 0.43; NMR 0.26, 2 / 0, 0.15), equal to the spike's; every `numerics.pinned` true. Rank, statistics and statuses: `results/motco_stage_sensitivity/comparison/stage_sensitivity.csv` and `.md`; the only finding is the arm's rank differing from the primary's.
- [x] 5.4 Reproduce the arm with MOTCO's CLI (the manifest's `cli_equivalent`, into a scratch directory): equal statistics, p-values, null summaries and rank, and byte-identical `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv`. Then run `--n-jobs 4` into a scratch root and verify the not-reported finding. Delete both scratch directories. (Done 2026-10-29 on nixos-home, with `NUMERIC_SETTINGS` exported: `motco analyze` from the arm manifest's `cli_equivalent` gives equal `statistics`, `p_values`, `null_summary` and selected rank, and byte-identical `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv`; `--n-jobs 4` into a scratch root records the n_jobs finding and prints "not a reported run" in `summary.md` and `stage_sensitivity.md`; both scratch directories deleted.)
- [x] 5.5 Run `axis-diagnostics` on the arm into `results/motco_stage_sensitivity/diagnostics`. Verify the chain checks pass, `is_primary` is false, `stage_arm` is `cn_lmci_ad`, and there is no deviation on the expected keys. (Done 2026-10-29 on nixos-home: the export, analysis and cohort chains pass, the cohort check comparing the 1130 both-flag rows the arm keeps; `is_primary` false, `stage_arm` `cn_lmci_ad`; no deviation on the rank-independent keys with the arm's participants and cells; `numerics.pinned` true; the flagged rows are in `diagnostics/diagnostics.md`.)
- [x] 5.6 Rerun 5.3 and 5.5 with `--force` on the clean tree after the implementation commit, with the first run's `diagnostics/` moved aside so that no stale-diagnostics finding enters the committed outputs. Verify every non-JSON output is byte-identical to the first run, and the manifests equal apart from time, revision, MOTCO's runtime and the hashes of the files that carry them. These are the committed outputs. (Done 2026-10-29 on nixos-home at `55841a3`, clean: the first run's `diagnostics/` removed after a scratch copy of the first run was kept for the comparison; `stage-sensitivity --force` and `axis-diagnostics` on the arm rerun. Against the first run: the 17 non-JSON files (every CSV, `summary.md`, `stage_sensitivity.md`, `diagnostics.md`) byte-identical; the four manifests and `result.json` equal apart from time, revision (dirty → clean), MOTCO's runtime and the hashes and sizes of `manifest.json`, `result.json` and `analysis_manifest.json`, which carry them; no deviation; every `numerics.pinned` true; scratch copy deleted. Committed as `3cc369b`.)

## 6. Docs and commit hygiene

- [x] 6.1 Update `README.md` with a `stage-sensitivity` section: command, arm, inputs, outputs and which are participant-level, the predeclared counts, the diagnostics on the arm, and the reading rules. Update `AGENTS.md`:
  - the status;
  - the step listed as a sensitivity step beside the other two;
  - "Flag and ask" with the two constants and their values, and the predeclared counts;
  - the Layout;
  - the participant-level patterns of constraint 1.

  Verify with `grep -n stage-sensitivity README.md AGENTS.md`.

  Done 2026-10-29: a `stage-sensitivity` section in `README.md` (and the status, layout, pipeline, quick start and the diagnostics' arm paragraph); in `AGENTS.md` the status, the step under 5, constraint 1's committed outputs and patterns, constraint 5, the Layout (`cli.py`, `constants.py`, `data.py`, `scripts/`, `results/`), the commands, the run-offset note and "Flag and ask" with the two constants, their values and the predeclared counts, the cluster note; `grep -n stage-sensitivity README.md AGENTS.md` lists 28 lines.
- [x] 6.2 Before the commit of outputs, name every file added under `results/motco_stage_sensitivity/` with why it is aggregate. Verify:
  - `git check-ignore` matches every participant-level file (the four `motco_input/*.csv`, `latent_scores.csv` and `analysis_metadata.csv`);
  - no staged CSV has an `rid` or `RID` column, and `grep -w` finds `rid` only as a column name;
  - `openspec validate adni-stage-sensitivity --strict` passes.

  Done 2026-10-29 before `3cc369b`: 15 aggregate files added under `results/motco_stage_sensitivity/`: `motco_input/manifest.json` (hashes, settings, counts per cell, run, level and `dx_bl` category, run offsets); `analysis/result.json` (MOTCO's record: statistics, p-values, null summaries, cell sizes, the covariate block), `pls_loadings.csv` (per metabolite and component), `stage_means.csv` (per sex × stage cell), `analysis_manifest.json`, `summary.md`; `comparison/stage_sensitivity.csv` (two rows, primary and arm), `stage_sensitivity.md`, `stage_sensitivity_manifest.json`; `diagnostics/` (`axis_correlations.csv`, `block_pcs.csv`, `geometry_shares.csv`, `components.csv`: per component, block and variable; `diagnostics.md`, `diagnostics_manifest.json`). `git check-ignore` matches the four `motco_input/*.csv`, `latent_scores.csv` and `analysis_metadata.csv`; no staged CSV has an `rid` or `RID` column, and `grep -w` finds `rid` only as a column name (`sample_column`, `sample_col`, `--sample-col`); `openspec validate --strict` passes; `report --check` still passes on the committed report.

## Workflow follow-up

- Archive the change on its branch, sync the specs, open the PR and merge, as the earlier changes did.
- The follow-up change that adds the arm to `report` (a section, its inputs in `REPORT_INPUT_FILES`, its chain links).
