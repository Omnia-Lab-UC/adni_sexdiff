# Proposal

## Why

The MOTCO inputs exist (`results/motco_input/`, change `adni-export`, manifest committed at `b10da51`: 1501 participants, blocks p180 133 and NMR 165 metabolites, the five covariates with their codings) and MOTCO is pinned at `v0.10.0`, the release with the validated rank floor. `analyze` is a stub and its settings are undecided, so the case study has no result. This change decides the measurement settings and the reading rules before any run and implements `analyze` as AGENTS.md step 4 binds: one `motco.analysis.analyze_trajectories` call on the exported blocks, never assembled from `motco plsr` + `motco de`. No number in this proposal comes from a MOTCO run on ADNI data; the only run made for it is a synthetic one at the ADNI shape, for timing.

## What Changes

- **The measurement settings decided**, each a named constant in `constants.py` (decided by the user on 2026-10-27, before any run):
  - `ANALYSIS_PERMUTATIONS = 9999`. RRPP p-values are `(1 + b) / (1 + B)`, exact in size at any `B`; the count sets the Monte Carlo resolution (0.0001 here), not the size. MOTCO's operating studies ran 999; at n = 1501 and a latent rank of at most 20 the extra permutations cost seconds, and the finer resolution is worth it at the first well-powered design.
  - `ANALYSIS_SEED = 20261027` (the proposal's date, as the template did).
  - `ANALYSIS_ALPHA = 0.05`, rejected when `p ≤ α` (`ANALYSIS_REJECTION_RULE`), the rule of MOTCO's covariate Type I check, exact for the p-value above.
  - `ANALYSIS_RANK_FLOOR = 2`, MOTCO's validated default (`min_components`; `rank-floor-2026-10-23.md`, `adopt_floor`), passed explicitly and checked equal to MOTCO's default before any input is read; a MOTCO whose default moved stops the run instead of changing the primary.
  - `ANALYSIS_LATENT_ADJUSTMENT = None` for the primary: the covariate-blind basis of MOTCO's validated 0.8.0 path. The `stage`-conditioned latent adjustment is **decided here as a predeclared sensitivity arm**, with the same five covariates and every other setting equal, to be run by the following change `adni-latent-sensitivity` after `axis-diagnostics` has measured the primary's components against phase. MOTCO binds it to be a sensitivity beside the covariate-adjusted analysis, never a replacement (`latent-adjustment-type-i-2026-10-20.md` §5, `latent-adjustment-power-2026-10-20.md` §6, `adopt_stage` / `candidate_fails`); `group_stage` is not admissible and will not run.
  - Everything else is MOTCO's default and is not overridden: net-displacement orientation, double CV (`cv2_splits` 4, `cv1_splits` 3, `n_repeats` 5, `max_components` 20, `random_state` 1203), no forced rank, attribution off (MOTCO refuses it with covariates), transform `identity` for both blocks (decided by `adni-export`), group order `Female`, `Male` (`GROUP_VALUES`; the statistics are symmetric in the groups), stage order `CN`, `MCI`, `AD` (`STAGE_LABELS`), missing-covariate policy `error`. `n_jobs = 1` for the reported run (`REPORTED_N_JOBS`).
- **How `phase` enters MOTCO, decided**: as a covariate of the stage means, additively, with `age`, `education`, `apoe4` and `statin` (`ANALYSIS_COVARIATES`, decided by `adni-cohort`; `apoe4`, `phase` and `statin` declared categorical with the codings the export manifest carries, so the design has six columns: `age`, `education`, `apoe4[1]`, `apoe4[2]`, `phase[ADNI2GO]`, `statin[1]`, reference levels `0`, `ADNI1`, `0`). The LS-means are evaluated at the pooled covariate mean, so the stage means are within-phase contrasts at the pooled phase proportion. The run offset itself is not corrected (decided by `adni-export`: stage composition differs by phase, EMCI and SMC exist only in ADNI-GO/2). The sensitivity arm above is the only other way phase enters.
- **`READING_RULES` written before any run**, a constant of statements the `report` step will print verbatim and the proposal binds now:
  1. The primary result is the covariate-adjusted analysis on the covariate-blind basis with the five covariates; every sensitivity (latent adjustment, export variants, the CN / LMCI / AD arm, a rank sweep) is read beside it, and a rejection status that differs in an arm is dependence on that arm's setting, never a replacement of the primary.
  2. The CV-selected rank, the rank floor, the record's `config_spectrum` eigengap and the `angle` null summary are reported beside `angle`. The floor defines `angle` and `shape` in at least two dimensions; it does not make them powerful.
  3. `angle` and `shape` non-rejections are uninformative: MOTCO's operating characteristics were measured at n = 80 on a structural analogue (InterSIM blocks, 498 features), and no power statement exists at this design (n = 1501, 298 metabolites, six design columns). `angle` reads only the endpoint stages (CN and AD). A rejection is evidence that the trajectories differ in that respect, with Type I controlled at the validated designs.
  4. A `delta` rejection is evidence of a difference between the sexes' trajectories, not specifically of a difference in size.
  5. The covariate block of the record (design columns, reference row, missing policy, dropped participants) is reported beside the results. The adjustment is additive and linear on a covariate-blind basis, validated at three design columns and n = 80, and has no sex × covariate or stage × covariate term: the run offset is assumed equal in both sexes and across stages.
  6. The p180 run offset (export manifest `counts.phase_offset`: median |d| 1.12, 80 of 133 metabolites above 1, PC1 correlation 0.73 with phase; NMR 0.21, 0, 0.13) and the block shares (p180 133 / 298, unweighted in MOTCO 0.10.0) are reported beside the results. A latent component that tracks phase is a reading matter for `axis-diagnostics` and the latent-adjusted arm, not an adjustment of the primary.
  7. Feature membership and scale (`EXPORT_FEATURE_RULE`: 165 of 245 NMR columns, the floored log2, nothing imputed, winsorized or removed) are reported beside the results.
  8. Reported runs use `n_jobs = 1`; a run at another value carries a finding and is not reported. Report numbers are pasted from the generated files and checked by `report --check`.
  9. No result changes a constant. The analysis is run once at these settings; a second run at other settings is a new proposal.
- **`analyze` implemented.** It reads only `results/motco_input/` (`p180.csv`, `nmr.csv`, `metadata.csv`, `covariates.csv`, each checked against the sha256 in `manifest.json`; the manifest's counts, blocks and covariate codings), checks the MOTCO version and the floor before any read, builds the dataset above, runs the one call and writes `results/motco_analysis/` (as `motco_analysis.tmp/`, renamed when complete; an existing directory stops it unless `--force`):
  - MOTCO's artifact `result.json`, `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`;
  - `analysis_metadata.csv`, the table the model saw (`rid`, `sex`, `stage`, the five covariates), parsed back as `motco analyze --metadata` would, so the manifest's `cli_equivalent` reproduces the run with MOTCO's CLI;
  - `analysis_manifest.json`: input hashes and the export manifest's hash, the settings as passed (every constant above, `min_components`, `n_jobs`, the covariate kinds, levels and reference levels), `cli_equivalent`, versions (MOTCO, scikit-learn, numpy, pandas, Python), git revision, the predeclared `ANALYSIS_EXPECTED_COUNTS` beside the observed ones, output hashes with a participant-level flag, findings;
  - `summary.md`, generated from the record: per statistic the observed value, p, rejection, null mean, sd and q95, the CV-selected rank and floor in the `angle` row with the eigengap; the cell sizes; the latent block; the covariate block; the reading rules.
  `latent_scores.csv` and `analysis_metadata.csv` are participant-level and already in `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS`; the other five files are aggregate and the committed ones (constraint 1 names them).
- **Predeclared counts** (`ANALYSIS_EXPECTED_COUNTS`, all from the export and cohort manifests, none from a run): participants 1501, Female CN / MCI / AD 237 / 310 / 125, Male 223 / 448 / 158; features p180 133, NMR 165, joint 298; six design columns under the names above; covariate levels apoe4 810 / 542 / 149, phase 684 / 817, statin 797 / 704; dropped participants 0; `component_selection` `cv`, `min_components` 2, permutations 9999. A deviation is a finding, printed and recorded, never silent. Findings also record: `n_jobs ≠ 1`; a CV-selected rank equal to the floor (the floor is binding); `cv_repeats_completed` below 5; a non-finite statistic or p-value.
- **`scripts/analyze.sbatch`**, the cluster script AGENTS.md assigns to this change (modelled on `clean.sbatch`: partition `512x1024`, one CPU, the locked `.venv/bin/adni-sexdiff`, `n_jobs = 1`). The reported run of this change is the workstation's, since the cluster clone and data copy do not exist yet (constraint 7); the cluster rerun is a follow-up that compares manifests.
- **Docs**: `README.md` (status; an `analyze` section with the settings, the inputs, the outputs and which are participant-level, the manifest, the reproduction by hand, the reading rules); `AGENTS.md` (status; step 4 as built; "Flag and ask" with every constant above decided and its value, and the latent arm decided as a sensitivity for the next change; the Layout entries for `scripts/` and `constants.py`; the cluster section); the `constants.py` docstring and the `run_analysis` docstring.

Precedent and departures. The template's `mtg-astrocyte-motco-analysis` and `mtg-rank-floor-primary` changes used 999 permutations, seed = the proposal's date, α = 0.05 with `p ≤ α`, floor 2, and wrote the report in the same change. This change uses 9999 permutations, keeps the report for step 6 (`adni-report`, with `--check`) and predeclares the latent-adjusted arm instead of discovering the need for it from a diagnostic, because the export already recorded that the p180 block's first axis is the run. The 2022 study (Front. Radiol.) tested metabolites one at a time within sex with the runs pooled by z-scoring; here one joint test, the run as a covariate.

Out of scope, each its own change:
- `axis-diagnostics` (step 5, `DIAGNOSTIC_VARIABLES` with `phase`) and `report` (step 6).
- The latent-adjusted sensitivity arm (`adni-latent-sensitivity`, decided above, implemented and run next), the rank-sweep sensitivity, the export sensitivity variants (all 245 NMR columns, raw scale, `log2(x + 1)`, generalized log) and the CN / LMCI / AD arm.
- Block weighting (MOTCO roadmap item 5), attribution, enrichment.
- A MOTCO pin move; the cluster run (it needs the deploy key and the data copy); any change to `clean`, `cohort` or `export`.

No number under these settings changes them.

## Capabilities

### New Capabilities
- `motco-trajectory-analysis`: the `analyze` step. The MOTCO version and rank-floor gates, the inputs and their hash checks, the fixed covariate design, the fixed measurement settings, the one-call constraint, the output contract (MOTCO's artifact, the metadata table, the manifest, the summary), the predeclared-count check, reproducibility and `n_jobs`, and the binding reading rules every reader of the result carries.

### Modified Capabilities
<!-- None: motco-input-export is read, not changed; cohort-assembly and metabolomics-cleaning are untouched. -->

## Impact

- `src/adni_sexdiff/constants.py`:
  - Scientific, decided here: `ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_ALPHA`, `ANALYSIS_REJECTION_RULE`, `ANALYSIS_RANK_FLOOR`, `ANALYSIS_LATENT_ADJUSTMENT`, `READING_RULES`.
  - Predeclared: `ANALYSIS_EXPECTED_COUNTS`.
  - Conventions: `ANALYSIS_STATISTICS` (`delta`, `angle`, `shape`), `ANALYSIS_MISSING_COVARIATES` (`error`), `ANALYSIS_CATEGORICAL_COVARIATES` (derived from `ANALYSIS_COVARIATES`' codings), `ANALYSIS_INPUT_FILES`. `ANALYSIS_MOTCO_MIN_VERSION` and `REPORTED_N_JOBS` exist.
  - The docstring's undecided list loses the analysis constants and `READING_RULES`; `DIAGNOSTIC_VARIABLES` and `DIAGNOSTIC_CORRELATION_THRESHOLD` stay undecided.
- `src/adni_sexdiff/data.py`: `run_analysis` and `check_motco_version` (replacing the stubs), a rank-floor check, the input loader, the summary renderer and the `cli_equivalent` builder; the manifest and `.tmp` helpers reused. `cli.py`: progress messages only; the flags (`--input-dir`, `--out-dir`, `--n-jobs`, `--force`) exist.
- New `scripts/analyze.sbatch`.
- Ignore rules: none to change (`latent_scores.csv` and `analysis_metadata.csv` are already covered under any `results/` path).
- Dependencies: none new. MOTCO `v0.10.0` is in `uv.lock`; scikit-learn stays at MOTCO's pin.
- Compute: a synthetic dataset of the ADNI shape (1501 × 133 + 165, six design columns) ran in 22 s with 999 permutations and in 25 s with 9999, `n_jobs = 1`, on the workstation. No cluster time is needed for the primary.
- `results/motco_analysis/` on the workstation (new); `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md` are committed, named one by one with why each is aggregate.
- Scientific choices introduced here (flag and ask before changing): the five measurement constants above, the primary on the covariate-blind basis with the latent-adjusted arm as a predeclared sensitivity, phase as an additive covariate, and the reading rules.
