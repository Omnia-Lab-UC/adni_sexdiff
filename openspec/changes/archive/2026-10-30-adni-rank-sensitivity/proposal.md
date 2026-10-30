# Proposal

## Why

`READING_RULES` rule 1 registers four sensitivities: the latent adjustment, the export variants, the CN / LMCI / AD arm and a rank sweep. The first three exist (changes `adni-latent-sensitivity`, `adni-nist-bridge` and `adni-stage-sensitivity`), and the report of 2026-10-30 quotes them. This change is the fourth.

The rank is the one quantity that moved in every sensitivity. The CV-selected rank is 8 for the primary, 4 for the latent arm, 6 for `nist_bridge`, 4 for `per_run_standardized` and 6 for the CN / LMCI / AD arm (the committed records). Every comparison reports a differing rank "reported, not ranked". What is not yet measured is how the primary's own `delta`, `angle` and `shape` move with the rank alone, on the primary's data, with everything else held fixed. `angle` is measured inside the latent space, so it is the statistic most exposed to the rank. `READING_RULES` rule 2 already puts the rank beside `angle`, but nothing yet says how much `angle` depends on it.

MOTCO 0.10.0 provides the measurement: `TrajectoryAnalysisParams.forced_components` fixes the rank and skips the cross-validation, and `motco analyze --forced-components` reproduces it from the CLI. The template (`../sead_sexdiff`, change `mtg-astrocyte-rank-sensitivity`) ran the same sweep on its case study.

The spike of this change (`spike.md`, 2026-10-30) used synthetic data only. It read no ADNI file and ran no forced rank on ADNI data. Its findings, on MOTCO 0.10.0 with the pinned numerics:
- **Nesting.** The latent scores at a forced rank k are bit for bit the first k columns of the scores at a higher forced rank. MOTCO fits `PLSRegression` (NIPALS with deflation), whose components are extracted one at a time. So a forced rank at or below the primary's 8 measures the primary's own first k components, and a rank above 8 adds components the cross-validation did not select. `pls_loadings.csv` (the rotations) is not nested: it depends on the rank.
- **Forced at the CV rank is the CV run.** A forced run at the CV-selected rank gives the CV run's latent scores, statistics, p-values, null summaries and `config_spectrum`, bit for bit. MOTCO's final fit after the CV is the same pooled fit at the selected rank, and the RRPP draws depend on the seed and the sample size only.
- **Feasibility.** MOTCO rejects a forced rank outside `[2, min(n_features, n_samples)]` rather than clamping it, so rank 1 cannot be forced. Here the bound is 298.

The ladder below was chosen knowing the five CV-selected ranks above and without any forced-rank statistic on ADNI data. No setting below comes from a sex × stage result.

## What Changes

- **New `rank-sensitivity` step** (`adni-sexdiff rank-sensitivity`), a sensitivity step read beside the primary.
  - **Inputs:** the primary export (`results/motco_input/`, its five files checked as `analyze` checks them) and the primary analysis (`result.json` and `analysis_manifest.json`, as a chained reference). It reads no data root, no cohort table and no diagnostics output.
  - **Anchor gate:** before any rank of the ladder runs, one forced run at the primary's recorded rank (8). Its statistics, p-values, null summaries, `config_spectrum` and rank must equal the primary record's, and its `latent_scores.csv`, `pls_loadings.csv` and `stage_means.csv` must hash to the values the primary manifest records. A difference stops the step before anything is written. The anchor is staged, compared and removed; it is not an output.
  - **The sweep:** one `analyze_trajectories` call per rank of the ladder, through the function the other analysis steps share (`_run_trajectory_analysis`), at the primary's settings plus `forced_components = k`.
  - **Comparison:** every rank's statistics beside the primary's.
- **Scientific constants**, proposed here and decided by the user when the proposal is accepted, before any run:
  - **`RANK_SENSITIVITY_LADDER`**: the single ladder `forced_rank_ladder`.
    - **Ranks:** `(2, 3, 4, 6, 9, 12)`. 2 is `ANALYSIS_RANK_FLOOR` and `n_stages − 1`, the smallest space in which `angle` and `shape` are defined. 3 is the next rank. 4, 6, 9 and 12 are the steps of MOTCO's rank ladder (`latent-rank-ladder-2026-09-08`) and of the template's sweep, so the three sweeps are comparable. The ladder spans both sides of the primary's 8, and 12 stays inside the CV's candidate range (2 to 19) and far below the feasibility bound (298). An import-time assertion ties the lowest rank to `ANALYSIS_RANK_FLOOR`.
    - **Setting:** `forced_components` only. The primary's rank is not on the ladder; it enters as the anchor gate, read from the record.
    - **Analysis:** every other setting is the primary's: the primary export, `ANALYSIS_COVARIATES` with their coding, `ANALYSIS_PERMUTATIONS` 9999 and `ANALYSIS_SEED` 20261027 at every rank, `ANALYSIS_RANK_FLOOR` 2, no latent adjustment, MOTCO's defaults, and `n_jobs = 1` for the reported run.
    - **No crossing:** the sweep runs on the primary only, never on the latent arm, an export variant or the CN / LMCI / AD arm.
  - **`RANK_SENSITIVITY_READING_RULES`**: eight statements, printed verbatim after `READING_RULES` in each rank's `summary.md`, the comparison, the top rank's `diagnostics.md` and every report that quotes the sweep.
    1. The sweep is read beside the primary and never replaces it. The primary's rank is its CV-selected rank (8). No rank of the sweep is chosen, adopted or ranked, and no sweep result changes a constant (`ANALYSIS_RANK_FLOOR` and the ladder included), reruns the primary or defines another arm.
    2. Every rank is the primary's analysis with one setting changed: `forced_components`, which fixes the rank and skips MOTCO's cross-validation. The export, the covariates and their coding, the seed, the permutations and every other setting are the primary's, and at `n_jobs = 1` every rank permutes the same residual indices. A difference between ranks is a difference of measurement, not of permutation draws. A rejection status that differs from the primary's is rank dependence, not a result at that rank.
    3. PLS-DA components are nested. At a forced rank at or below the primary's 8, the latent space is spanned by the primary's first components; a rank above 8 adds components the cross-validation did not select. The anchor run at rank 8 reproduces the primary's record and files exactly, so the primary row is also the sweep's row at its rank.
    4. Each rank's floor, eigengap and `angle` null summary are reported beside its `angle`. The `angle` null depends on the rank, so each `angle` is read against its own null, never against the `angle` of another rank. At rank 2, the floor, `angle` and `shape` are measured in two dimensions (reading rule 2).
    5. MOTCO's forced-rank evidence is its Phase 5 rank ladder (2026-09-08; MOTCO 0.6.0, n = 1200, four stages, no covariates): size held at every forced rank, and the ranks above `n_stages − 1` lost `shape` power and gained no `angle` power. No Type I or power check exists at a forced rank at this design or with covariates. A non-rejection at any rank is no more informative than the primary's (reading rule 3), and a rejection at a forced rank only is rank dependence, read beside that rank's null summary.
    6. The sweep is not a test. No rule combines the ranks, picks the rank with the smallest p-value or counts the ranks that reject, and the p-values are not adjusted for multiplicity because no decision is taken from them.
    7. The axis diagnostic of the top rank (12) is reported beside the sweep. Its components up to the primary's rank are the primary's, with the primary's correlations. A component above it that tracks a variable, `phase` in particular, is a measurement-space finding about the higher ranks and never grounds to choose a rank.
    8. The sweep is not crossed with the latent adjustment, an export variant or the CN / LMCI / AD arm, and is read against the primary only. The CV-selected ranks of those analyses are their own selections, and no sentence reads them against the sweep.
- **Predeclared counts** (`RANK_SENSITIVITY_EXPECTED_COUNTS`, from the committed primary manifests and the ladder, none from a forced run on ADNI data; a deviation is a finding, never a stop):

  | quantity | value |
  |---|---|
  | anchor | rank 8 (the primary record's `selected_lv`), every compared field equal, three file hashes equal |
  | analysis, per rank k | every key of `ANALYSIS_EXPECTED_COUNTS` (1501 participants, the primary's cells, features, design columns, levels, 0 dropped, floor 2, 9999 permutations) with `component_selection` `forced`, `selected_rank` k and `cv_repeats_completed` 0 |
  | comparison | 7 rows (the primary, then the six ranks in ladder order) |
  | diagnostics, top rank | the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS`; the read rank 12 (`forced`, no latent adjustment, `n_jobs` 1); rows 96 / 48 / 48 / 12 in `axis_correlations.csv`, `block_pcs.csv`, `geometry_shares.csv` and `components.csv` |

  No rank's statistic or status is predeclared.
- **Outputs** under `results/motco_rank_sensitivity/`:
  - `rank_02/`, `rank_03/`, `rank_04/`, `rank_06/`, `rank_09/`, `rank_12/`: the seven files `analyze` writes, laid out as the primary's. `summary.md` names the forced rank, replaces the CV block with the forced rank, and prints `RANK_SENSITIVITY_READING_RULES` after `READING_RULES`. `analysis_manifest.json` records step `rank-sensitivity`, the ladder by constant name, the forced rank, the primary as reference, the anchor's result and the predeclared counts. `latent_scores.csv` and `analysis_metadata.csv` are participant-level, already matched by `results/**/latent_scores.csv` and `results/**/analysis_metadata.csv`.
  - `comparison/`:
    - `rank_sensitivity.csv`: the primary row, then one row per rank in ladder order, every value read from the records;
    - `rank_sensitivity.md`: statuses `same` / `differs (rank dependence)`, the latent spaces, the anchor check, the nesting note, the findings and both sets of rules;
    - `rank_sensitivity_manifest.json`.
  - `diagnostics/`: written by `axis-diagnostics --analysis-dir results/motco_rank_sensitivity/rank_12 --out-dir results/motco_rank_sensitivity/diagnostics`, run in this change. Nesting makes the top rank's components a superset of every other rank's, so one diagnostic covers the sweep.

  The six rank directories and `comparison/` are staged as `.tmp/` and renamed together. No new participant-level pattern is needed, so `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged. Every other file is aggregate and committed, named one by one.
- **`axis-diagnostics` reads a forced rank as the sweep's.**
  - **Detection:** an analysis manifest with step `rank-sensitivity` records the forced rank.
  - **Expectations:** the rank-independent keys, plus the top rank's rows, from `RANK_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]`.
  - **`diagnostics.md`:** it names the sweep and the forced rank, and prints `RANK_SENSITIVITY_READING_RULES` after `READING_RULES`.

  On the primary, the latent arm, the export variants and the CN / LMCI / AD arm, the diagnostic's outputs are unchanged.
- **Docs:**
  - `README.md`: a `rank-sensitivity` section.
  - `AGENTS.md`: the status; the step, listed as a sensitivity step beside the other three; "Flag and ask" with the two constants and the predeclared counts; constraints 1 and 5; the Layout.
  - The `constants.py` docstring and the step docstrings.

Out of scope, each its own change:
- **The report.** A later change adds the sweep to `report`. The committed report's inputs are unchanged, so it stays valid and `report --check` passes.
- **Other ranks and rules:** a rank off the ladder, rank 1 (MOTCO rejects it), a rank-selection rule, and any change to `ANALYSIS_RANK_FLOOR` or MOTCO's CV settings (`max_components`, folds, repeats).
- **Crossings:** the sweep on the latent arm, an export variant or the CN / LMCI / AD arm.
- **Diagnostics of the other ranks:** by nesting, their components are the top rank's first ones.
- **An operating-characteristic study at this design** (Type I or power at a forced rank, with covariates). That is a MOTCO-side measurement.
- **Other registered sensitivities:** the other export variants (all 245 NMR columns, the raw scale, `log2(x + 1)`, the generalized log).
- **Pin and cluster:** a MOTCO pin move, and the cluster run (constraint 7).

No sweep result changes a constant, selects a rank, reruns the primary or replaces it.

## Capabilities

### New Capabilities
- `motco-rank-sensitivity`: the `rank-sensitivity` step. It covers:
  - the predeclared forced-rank ladder;
  - the primary export and primary analysis as chained, read-only references;
  - the anchor gate at the primary's rank;
  - one analysis per rank at the primary's settings;
  - the output layout;
  - the comparison generated from the records;
  - the predeclared counts and findings, and reproducibility;
  - the sweep's reading rules, carried by every reader of the sweep.

### Modified Capabilities
- `latent-axis-diagnostic`:
  - "Labels are read but feed no choice" names `rank-sensitivity` and the ladder.
  - Two requirements are added: the sweep read (its forced rank recorded, the expected counts on the top rank), and the reading rules of a sweep read.

## Impact

- `src/adni_sexdiff/constants.py`:
  - scientific, decided here: `RANK_SENSITIVITY_LADDER` and `RANK_SENSITIVITY_READING_RULES`;
  - predeclared: `RANK_SENSITIVITY_EXPECTED_COUNTS`;
  - conventions: `RANK_SENSITIVITY_DIR`, `RANK_SENSITIVITY_RANK_DIR`, `RANK_SENSITIVITY_SUBDIRS` and the three comparison file names;
  - the docstring names the change and its constants.
- `src/adni_sexdiff/data.py`:
  - `run_rank_sensitivity`, with the anchor gate and `render_rank_sensitivity`;
  - `_run_trajectory_analysis` and `_analysis_cli_equivalent` gain `forced_components`, whose default `None` keeps every existing output's bytes;
  - the analysis findings, `render_analysis_summary`, `_statistic_reading_line`, `run_axis_diagnostics`, `render_axis_diagnostics`, `_analysis_command` and `_ANALYSIS_STEPS`, made forced-rank-aware;
  - the outputs of the primary, the latent arm, the variants and the CN / LMCI / AD arm unchanged.
- `src/adni_sexdiff/cli.py`: the `rank-sensitivity` subcommand (`--input-dir`, `--analysis-dir`, `--out-dir`, `--n-jobs`, `--force`). The ladder is a constant, never a flag.
- `.gitignore`, `scripts/sync_results.sh`, `PARTICIPANT_LEVEL_PATTERNS`: unchanged.
- `spike.md` in this change (synthetic, read no ADNI file).
- Dependencies: none new. MOTCO stays at `v0.10.0`, which provides `forced_components`.
- Compute: seven analyses without cross-validation (the anchor and six ranks) and one diagnostic run. The primary, with its cross-validation, ran in 26 s.
- Machines: a data machine, picked by the hash checks. No machine is named in the code.
- Committed, from the data machine's run, under `results/motco_rank_sensitivity/`:
  - per rank: `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md` (30 files);
  - `comparison/`: its three files;
  - `diagnostics/`: its six files.

  Each file is named at commit with why it is aggregate.
- Scientific choices introduced here (flag and ask before changing):
  - the ladder's ranks, and the single setting it changes;
  - the same seed and permutations at every rank;
  - the anchor gate at the primary's rank;
  - the diagnostic of the top rank only;
  - the sweep's reading rules;
  - the rule that the sweep never replaces the primary and feeds no choice.
