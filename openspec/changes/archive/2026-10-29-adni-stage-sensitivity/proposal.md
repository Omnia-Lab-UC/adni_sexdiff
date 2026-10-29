# Proposal

## Why

`READING_RULES` rule 1 registers four sensitivities: the latent adjustment, the export variants, the CN / LMCI / AD arm and a rank sweep. The first two exist (changes `adni-latent-sensitivity` and `adni-nist-bridge`), and the report of 2026-10-29 quotes them. This change is the third.

`STAGE_RULE` merges SMC into CN, and EMCI and LMCI into MCI. SMC and EMCI were enrolled only in ADNI-GO/2 (96 and 275 of the 1501 exported participants; committed `stage_counts.csv`). So inside the primary's CN and MCI, the two runs hold different diagnoses: ADNI-1 contributes CN and LMCI, while ADNI-GO/2 adds SMC and EMCI. The stage-means model fits one mean per sex × stage cell, plus an additive `phase` coefficient. Inside a cell, that coefficient therefore carries two things: the run offset, and the difference between the diagnoses the runs enrolled.

The export variants handle the measurement side of the run. This arm handles the design side. It drops the two categories enrolled in only one run, so each stage holds one diagnosis in both runs.

The spike of this change (`spike.md`, `scripts/spike_stage_arm.py`, 2026-10-29) is read-only and aggregate. It read `dx_bl`, the covariates and the primary export's values by run. It read no MOTCO output and computed no sex or stage contrast of a metabolite. Its findings:
- **Cohort.** The arm keeps 1130 participants. Its cells are Female CN 183, MCI 187, AD 125 and Male CN 181, MCI 296, AD 158, and every stage label equals the arm's map of `dx_bl`. The stage-means design is of full rank (12 columns, rank 12).
- **Covariates.** The smallest level is `apoe4 = 2`, with 128 participants.
- **The run offset is not stage composition.** On the arm's rows of the primary export, the p180 median |d| between runs is 1.10, against 1.12 on all rows, and PC1's correlation with phase is 0.71 against 0.73. The arm leaves the offset to `phase`, as the primary does.
- **The arm does not balance the runs across stages.** The ADNI-1 share is CN 0.527, MCI 0.700, AD 0.544, against 0.417, 0.446 and 0.544 in the primary. What it changes is the diagnosis composition within each stage.
- **Floors.** Recomputing the floors over the arm would move them by a median of 4 % (p180) and 0.8 % (NMR). On 2026-10-29 the user was advised to reuse the primary's floors; that choice is the user's when the proposal is accepted.

No setting below comes from a sex × stage result.

## What Changes

- **New `stage-sensitivity` step** (`adni-sexdiff stage-sensitivity`), a sensitivity step read beside the primary.
  - **Inputs:** the primary export (`results/motco_input/`, its five files checked as `analyze` checks them), the primary analysis (`result.json` and `analysis_manifest.json`, as a chained reference) and the cohort (`cohort.csv` against `cohort_manifest.json`, whose hash must equal the export manifest's record). It reads no data root and no cleaned table.
  - **Arm export:** the primary export's rows of the participants the arm keeps, in export order, with every cell, the header and the columns unchanged. No floor is recomputed and nothing is re-exported.
  - **Arm analysis:** one `analyze_trajectories` call on the arm export at the primary's settings, through the function `analyze`, `latent-sensitivity` and `export-sensitivity` share (`_run_trajectory_analysis`).
  - **Comparison:** the arm's statistics beside the primary's.
- **Scientific constants**, proposed here and decided by the user when the proposal is accepted, before any run:
  - **`STAGE_SENSITIVITY_ARM`**: the single arm `cn_lmci_ad`.
    - **Participants:** the exported participants whose `dx_bl` (`cohort.csv`, ADNIMERGE `DX.bl` on the baseline row) is CN, LMCI or AD. SMC and EMCI are dropped.
    - **Stages:** `STAGE_LABELS` unchanged, by `STAGE_RULE`'s own map (CN → CN, LMCI → MCI, AD → AD). An import-time assertion ties the arm's map to `STAGE_RULE`.
    - **Floors and scale:** the primary export's (`EXPORT_FEATURE_RULE` over the 1501). The arm's blocks are the primary's rows.
    - **Analysis:** every setting the primary's: `ANALYSIS_COVARIATES` with their coding, `ANALYSIS_PERMUTATIONS` 9999, `ANALYSIS_SEED` 20261027, `ANALYSIS_RANK_FLOOR` 2, no latent adjustment, MOTCO's defaults, and `n_jobs = 1` for the reported run.
    - **No crossing:** the arm is not crossed with the latent adjustment or an export variant.
  - **`STAGE_SENSITIVITY_READING_RULES`**: eight statements, printed verbatim after `READING_RULES` in the arm's `summary.md`, the comparison, the arm's `diagnostics.md` and every report that quotes the arm.
    1. The arm is read beside the primary and never replaces it. No arm result changes a constant, `STAGE_RULE` or `COHORT_RULE`, reruns the primary or adopts the arm.
    2. The arm's rows are the primary export's rows of the 1130 participants whose `DX.bl` is CN, LMCI or AD, with the cells unchanged (the primary's floors). The covariates, their coding and every analysis setting are the primary's.
       - It differs in the participants: the 96 SMC and 275 EMCI participants, enrolled only in ADNI-GO/2, are dropped. Its CN is `DX.bl` CN and its MCI is LMCI.
       - Its z-scoring, CV folds, latent basis, rank, covariate reference row and permutation draws are its own.
       - A rejection status that differs is dependence on the stage definition and the sample, not a result of the arm.
    3. The arm's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
    4. In the arm each stage holds one `DX.bl` category in both runs, so the `phase` coefficient of the stage-means model is estimated from contrasts within one diagnosis. In the primary, the ADNI-GO/2 rows of CN and MCI add SMC and EMCI. The arm neither balances the runs across stages nor removes the run offset, which is measurement:
       - ADNI-1 share per stage: CN 0.527, MCI 0.700, AD 0.544 in the arm; 0.417, 0.446, 0.544 in the primary.
       - p180 median |d|: 1.10 on the arm's rows, 1.12 on the primary's. PC1 correlation with phase: 0.71 and 0.73.

       `phase` stays a covariate under the additive assumption of reading rule 5.
    5. The arm's MCI (LMCI) is a later and narrower stage than the primary's MCI, and its CN excludes subjective memory concern. A difference that involves the middle stage is a difference of stage definition. `angle` reads only the endpoint stages: the arm's AD cells are the primary's, and its CN cells lose the SMC participants.
    6. The arm holds 1130 of the 1501 participants. Its non-rejection is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in the arm is dependence on the stage definition and the sample, read beside its rank and null summary.
    7. The arm's export manifest records its cells, the runs within each stage and the run offset on its rows, and they are reported beside the results with the primary's. A component of the arm that tracks a variable in its axis diagnostic is a measurement-space finding about the arm and never grounds to adopt it. In the arm, `dx_bl` orders the participants as `stage` does, so their correlations coincide.
    8. The arm is not crossed with the latent adjustment or an export variant, and is read against the primary only. No sentence reads it against another sensitivity.
- **Predeclared counts** (`STAGE_SENSITIVITY_EXPECTED_COUNTS`, from the committed `stage_counts.csv` and the spike, none from a run of the arm; a deviation is a finding, never a stop):

  | quantity | value |
  |---|---|
  | participants kept / dropped (SMC, EMCI) | 1130 / 96, 275 |
  | sex × stage | Female 183 / 187 / 125, Male 181 / 296 / 158 |
  | runs within stage, ADNI1 / ADNI2GO | CN 192 / 172, MCI 338 / 145, AD 154 / 129 |
  | features | p180 133, NMR 165 (the primary's `block_columns`) |
  | rows equal to the primary's, per CSV | all, for `p180.csv`, `nmr.csv`, `metadata.csv`, `covariates.csv` |
  | missing covariate values, non-finite cells | 0, 0 |
  | p180 metabolites with phase \|d\| > 0.5 / > 1; NMR \|d\| > 1 | 107 / 77; 0 |
  | analysis | the keys of `ANALYSIS_EXPECTED_COUNTS`, with participants 1130, the cells above and the levels `apoe4` 589 / 413 / 128, `phase` 684 / 446, `statin` 603 / 527; the six design columns, 0 dropped, `cv`, floor 2 and 9999 permutations unchanged |
  | diagnostics | the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS`, with participants 1130 and the cells above |

  The arm's rank is not predeclared.
- **Outputs** under `results/motco_stage_sensitivity/`:
  - `motco_input/`: the arm export, laid out as `results/motco_input/` without the feature tables (the floors are the primary's, recorded by hash). Its four CSVs are participant-level. `manifest.json` records:
    - the arm, with the primary export as reference;
    - the cohort chain;
    - `block_columns` and the covariate codings, copied from the primary export manifest;
    - the counts above, with the primary's run offset beside the arm's;
    - output hashes.
  - `analysis/`: the seven files `analyze` writes. `summary.md` adds an "Arm" section and `STAGE_SENSITIVITY_READING_RULES` after `READING_RULES`.
  - `comparison/`:
    - `stage_sensitivity.csv`: the primary row, then the arm row, every value read from the two records.
    - `stage_sensitivity.md`: statuses `same` / `differs (stage-definition dependence)`, the cells, runs within stage and covariate levels of both, the run offset of both exports, and both sets of rules.
    - `stage_sensitivity_manifest.json`.
  - `diagnostics/`: written by `axis-diagnostics --input-dir results/motco_stage_sensitivity/motco_input --analysis-dir results/motco_stage_sensitivity/analysis --out-dir results/motco_stage_sensitivity/diagnostics`, run in this change.

  `motco_input/*.csv` is matched by a new pattern, `results/motco_stage_sensitivity/motco_input/*.csv`, added to `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` before any output exists. `analysis/latent_scores.csv` and `analysis/analysis_metadata.csv` are already matched. Every other file is aggregate and committed, named one by one.
- **`axis-diagnostics` reads the arm as an arm.**
  - **Cohort check:** when the export manifest records the arm, the cohort chain compares the exported participants with the both-flag rows of `cohort.csv` that the arm keeps.
  - **Expectations:** the participants and cells come from `STAGE_SENSITIVITY_EXPECTED_COUNTS`.
  - **`diagnostics.md`:** it names the arm and prints `STAGE_SENSITIVITY_READING_RULES` after `READING_RULES`.

  On the primary, the latent arm and the export variants, the diagnostic's outputs are unchanged.
- **Docs:**
  - `README.md`: a `stage-sensitivity` section.
  - `AGENTS.md`: the status; the step, listed as a sensitivity step beside the other two; "Flag and ask" with the two constants and the predeclared counts; the Layout; the participant-level patterns.
  - The `constants.py` docstring and the step docstrings.

Out of scope, each its own change:
- **The report.** A later change adds the arm to `report`. The committed report's inputs are unchanged, so it stays valid and `report --check` passes.
- **The arm with recomputed floors** (a re-export over the 1130), other stage definitions (CN / AD only, EMCI as its own stage), and any change to `COHORT_RULE` or `STAGE_RULE`.
- **Crossings:** the arm under the latent adjustment or an export variant.
- **Other registered sensitivities:** the rank sweep, and the other export variants (all 245 NMR columns, the raw scale, `log2(x + 1)`, the generalized log).
- **Model terms:** a per-sex or per-stage phase term, and block weighting.
- **Pin and cluster:** a MOTCO pin move, and the cluster run (constraint 7).

No arm result changes a constant, selects a participant, reruns the primary or replaces it.

## Capabilities

### New Capabilities
- `motco-stage-sensitivity`: the `stage-sensitivity` step. It covers:
  - the predeclared CN / LMCI / AD arm;
  - the primary export, primary analysis and cohort as chained, read-only references;
  - the arm export as a row subset of the primary export, with the cells unchanged;
  - the arm analysis at the primary's settings;
  - the output layout and its participant-level pattern;
  - the comparison generated from the records;
  - the predeclared counts and findings, and reproducibility;
  - the arm's reading rules, carried by every reader of the arm.

### Modified Capabilities
- `latent-axis-diagnostic`:
  - "Cohort table is checked and chained to the export" gains the arm: the both-flag rows the arm keeps.
  - "Manifest records provenance, definitions and predeclared counts" takes the arm's participants and cells.
  - "Labels are read but feed no choice" names `stage-sensitivity`.
  - "Reading rules of a sensitivity read" gains the arm read.

## Impact

- `src/adni_sexdiff/constants.py`:
  - scientific, decided here: `STAGE_SENSITIVITY_ARM` and `STAGE_SENSITIVITY_READING_RULES`;
  - predeclared: `STAGE_SENSITIVITY_EXPECTED_COUNTS`;
  - conventions: `STAGE_SENSITIVITY_DIR`, `STAGE_SENSITIVITY_SUBDIRS` and the three comparison file names;
  - participant-level: `PARTICIPANT_LEVEL_PATTERNS` gains the arm export pattern;
  - the docstring names the change and its constants.
- `src/adni_sexdiff/data.py`:
  - `run_stage_sensitivity`, with the arm export (`_stage_arm_export`) and `render_stage_sensitivity`;
  - `_check_cohort_chain`, `run_axis_diagnostics`, `render_axis_diagnostics`, `render_analysis_summary`, `_statistic_reading_line` and `_analysis_command`, made arm-aware;
  - the primary's, the latent arm's and the variants' outputs unchanged.
- `src/adni_sexdiff/cli.py`: the `stage-sensitivity` subcommand (`--input-dir`, `--analysis-dir`, `--cohort-dir`, `--out-dir`, `--n-jobs`, `--force`). The arm and its rule are constants, never flags.
- `.gitignore`, `scripts/sync_results.sh`: the arm export pattern.
- `scripts/spike_stage_arm.py` (new, read-only) and `spike.md` in this change.
- Dependencies: none new. MOTCO stays at `v0.10.0`.
- Compute: one CV analysis smaller than the primary's (which ran in 26 s), and one diagnostic run.
- Machines: a data machine. nixos-home is one: the spike ran there on 2026-10-29, and its `cohort.csv`, export and cleaned tables matched the committed manifests. No machine is named in the code.
- Committed, from the data machine's run, under `results/motco_stage_sensitivity/`:
  - `motco_input/manifest.json`;
  - `analysis/`: `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md`;
  - `comparison/`: its three files;
  - `diagnostics/`: its six files.

  Each file is named at commit with why it is aggregate.
- Scientific choices introduced here (flag and ask before changing):
  - the arm's participants and stage map;
  - the primary's floors;
  - the arm's reading rules;
  - the rule that the arm never replaces the primary and feeds no choice.
