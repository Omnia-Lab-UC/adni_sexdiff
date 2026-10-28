# Proposal

## Why

The primary analysis exists (`results/motco_analysis/`, change `adni-analyze`, implemented at `af4d6e4`: CV-selected rank 8, `delta`, `angle` and `shape` not rejected at α = 0.05). That change decided, before any run, one sensitivity arm (`ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`): MOTCO's `stage`-conditioned latent adjustment, which builds the latent basis on features with the five covariates regressed out within each stage, with the same five covariates and every other setting equal. It ordered the arm to run after `axis-diagnostics` had measured the primary's components against phase. That diagnostic is committed (`cf38ec8`; `block_pcs.csv` was re-issued at the pinned thread count in `754c6ba`, every other diagnostics output unchanged), so the arm can now run and its own diagnostic can be read beside the primary's. Since `adni-portable-numerics` (merged in PR #6), every run is pinned (`NUMERIC_SETTINGS`), and a pinned run writes the committed bytes on any machine. So this change's gates compare with the committed hashes directly, wherever they run. Nothing in this proposal is taken from the diagnostic's values. The arm, its covariates and its settings are the ones `adni-analyze` fixed. No number here comes from a run of the arm; the values quoted are from committed manifests, the primary's record and MOTCO's two latent-adjustment reports.

MOTCO 0.10.0, the pinned release, supports the setting (`TrajectoryAnalysisParams.covariate_latent_adjustment`). Its Type I check (`../MOTCO/docs/reports/latent-adjustment-type-i-2026-10-20.md`) returned `adopt_stage` under these conditions:
- the case study's own proposal justifies the covariate set, including why no residualized covariate mediates the stage effect;
- `group_stage` is not used;
- the record's `latent_adjustment` and `covariates` blocks are reported beside the results;
- no categorical level is rare enough to drop out of a CV training set;
- the earlier binding statements stand.

Its power comparison (`latent-adjustment-power-2026-10-20.md`) returned `candidate_fails`, so the arm is a sensitivity, never a replacement. This change is the proposal those conditions ask for.

## What Changes

- **New `latent-sensitivity` step** (`adni-sexdiff latent-sensitivity`), a sensitivity step read beside the primary.
  - **Inputs:** the export (`results/motco_input/`, the five files checked as `analyze` checks them), the primary analysis (`results/motco_analysis/result.json` and `analysis_manifest.json`) and the cohort manifest (`results/cohort/cohort_manifest.json`, for its per-cell covariate descriptives).
  - **Checks before anything is written:**
    - the primary manifest records the export files now on disk;
    - the primary carries no latent adjustment;
    - the primary was made under the installed MOTCO with `ANALYSIS_SEED` and `ANALYSIS_PERMUTATIONS`;
    - the cohort manifest's hash equals the one the export manifest records.

    Any mismatch stops the step, naming the file, both values and the step to rerun.
  - **The run:** one `analyze_trajectories` call at the primary's settings plus `covariate_latent_adjustment = "stage"`. The primary is never rerun or written.
- **The arm, the covariate justification and the reading rules**, each a named constant in `constants.py`. They are proposed here and decided by the user when this proposal is accepted, before any run. On 2026-10-28 the user chose the approach to the mediator condition: predeclared roles beside the cohort manifest's descriptives, with no new statistic and no threshold.
  - `LATENT_SENSITIVITY_ARM`: the single arm `latent_stage`, conditioning `stage`, covariates `ANALYSIS_COVARIATES` (the same five, same order and coding), every other setting the primary's: blocks and transform, group and stage orders, `ANALYSIS_PERMUTATIONS` 9999, `ANALYSIS_SEED` 20261027, `ANALYSIS_RANK_FLOOR` 2, missing policy `error`, MOTCO's other defaults, `n_jobs = 1` for the reported run. An import-time assertion ties its conditioning and change name to `ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`. No `extended_covariates` arm (the kept outputs hold no further covariate) and no `group_stage` arm (not admissible).
  - `LATENT_SENSITIVITY_COVARIATE_ROLES`, the justification MOTCO's Type I condition asks for. Per covariate, its relation to the stage effect:
    - `age` (age at baseline), `education` (years of schooling, completed before enrolment) and `apoe4` (germline genotype) precede disease. They can confound the stage effect but cannot be downstream of it.
    - `phase` is the assay run and enrolment protocol (p180 kits ADNI-1 against ADNI-GO/2). It is tied to stage composition by design (SMC and EMCI exist only in ADNI-GO/2), not caused by stage.
    - `statin` (HMG-CoA reductase inhibitor use on the screening medication row) is a treatment that may follow diagnosis: prescribing differs with cognitive status. It is the one mediator candidate. It stays in the arm because the arm was predeclared with the five covariates, and the reading carries the limitation.
  - `LATENT_SENSITIVITY_READING_RULES`, written before any run. Nine statements printed verbatim, beside `READING_RULES`, in the arm's `summary.md`, the comparison, the arm's `diagnostics.md` and every report that quotes the arm:
    1. The arm is read beside the primary and never replaces it. MOTCO's power comparison returned `candidate_fails` for `stage` conditioning, which excludes the latent adjustment as a replacement of the covariate-blind primary.
    2. The primary and the arm share the export, the covariates and their design, the cells, the CV folds, the seed and the permutations. They differ only in the latent basis and the CV-selected rank: the arm's basis is fitted on the features with the five covariates regressed out within stage, and the raw features are measured in it. A rejection status that differs is basis dependence, not a result of the arm.
    3. The arm's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked as better or worse.
    4. An `angle` rejection that appears only in the arm is read against MOTCO's controls, and is not evidence of an orientation difference on its own:
       - the translation control rejected `angle` at 0.085–0.092 under `stage` conditioning, against the 0.0706 bound (the covariate-blind basis was above it too, at 0.076–0.086);
       - under the Type I check, `angle` held the bound by only 0.004 (0.067 against 0.0706).
    5. A `delta` or `shape` non-rejection in the arm is weaker than the primary's. MOTCO measured lost `shape` power with a covariate-aligned nuisance axis (0.243 against 0.428) and lost small-magnitude `delta` power without one (0.400 against 0.520 at e = 0.1). Reading rules 3 and 4 hold in the arm.
    6. The arm's `latent_adjustment` block and its covariate block are reported beside its results. The `latent_adjustment` block holds the conditioning, the design columns, the residual df, the smallest CV training df and the feature R² summary; `feature_r2` states how much feature variance the residualization removed.
    7. Residualizing a covariate that mediates the stage effect removes real stage signal, and no data can tell a confounder from a mediator. `age`, `education` and `apoe4` precede disease, and `phase` is the assay run and protocol (`LATENT_SENSITIVITY_COVARIATE_ROLES`). `statin` may follow diagnosis, so the arm's basis may have removed stage signal that runs through treatment.
    8. MOTCO's latent-adjustment operating characteristics were measured at one design: n = 80, the SEA-AD MTG structure, 498 features, eight covariates in nine design columns, covariates confounded with group × stage far beyond this design's. None was measured at this design (n = 1501, 298 metabolites, six design columns), and the arm carries no Type I or power claim of its own.
    9. A component of the arm that tracks a variable in its axis diagnostic is a measurement-space finding about the arm. It never reinterprets either analysis' statistics and is never grounds to adopt the arm.
- **The rare-level condition, checked before the run.** The smallest categorical level is `apoe4 = 2`, with 149 participants. Under CV with 4 outer and 3 inner folds, the smallest training set (about 750 rows) holds about 74 of them. If MOTCO still reports a residualization design that is not of full rank in a fold, that error stops the step with nothing written. It is reported, never worked around (no level is merged, no setting is changed).
- **Outputs** under `results/motco_latent_sensitivity/`:
  - `analysis/`: the arm's analysis directory, the seven files `analyze` writes, laid out as the primary's, so `axis-diagnostics --analysis-dir` reads it unchanged.
    - `result.json` carries MOTCO's `latent_adjustment` block.
    - The manifest lists the five export files as its inputs, records the primary as the reference (its `result.json` and manifest hashes) and the arm by constant name. Like every manifest since `adni-portable-numerics`, it carries the `numerics` block (machine, settings, `pinned`); a committed arm must record `pinned` true.
    - `summary.md` is the primary's renderer with a latent-adjustment section and both sets of reading rules.
  - `comparison/`:
    - `latent_sensitivity.csv`: the primary row and the arm row. Each row holds the latent adjustment, the selected rank and selection mode, `cv_mean_auroc`, CV repeats completed, the eigengap, and per statistic the observed value, p, rejection under `ANALYSIS_REJECTION_RULE` and the null mean, SD and q95. The arm row adds the residual df, the smallest CV training df and the `feature_r2` quantiles and mean. Every value is read from the two records.
    - `latent_sensitivity.md`: the tables, the status per statistic (same, or differs: basis dependence), the latent-adjustment block, the covariate roles beside the per-cell descriptives copied from the cohort manifest, MOTCO's operating characteristics, and both sets of reading rules.
    - `latent_sensitivity_manifest.json`.
  - `diagnostics/`: `axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics`, run in this change.

  `analysis/latent_scores.csv` and `analysis/analysis_metadata.csv` are participant-level and already matched by `results/**/latent_scores.csv` and `results/**/analysis_metadata.csv` in `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS`. Every other file is aggregate and committed, named one by one.
- **Predeclared counts** (`LATENT_SENSITIVITY_EXPECTED_COUNTS`, from the committed manifests and MOTCO's design rules, none from a run):
  - every key of `ANALYSIS_EXPECTED_COUNTS` with its value (1501 participants and the six cells, 133 / 165 / 298 features, the six design columns, the level counts, 0 dropped, `cv`, floor 2, 9999 permutations);
  - the latent-adjustment block: conditioning `stage`, the five covariates, the residualization design columns `stage[1]`, `stage[2]` (MOTCO's ordinal codes for MCI and AD), then the six design columns, `n_samples` 1501, `residual_df` 1492 (1501 − 1 − 2 − 6), `feature_scale` `pooled_standardized`.

  The arm's rank is not predeclared. A deviation is a finding, printed and recorded, never a stop.

  Findings also record:
  - every finding condition of `analyze`;
  - a CV-selected rank that differs from the primary's;
  - a statistic whose rejection status differs from the primary's, named as basis dependence;
  - a primary read with `n_jobs ≠ 1`;
  - cohort-manifest cells that differ from the record's cells.
- **The shared analysis path.**
  - `run_analysis`'s body becomes one function that both steps call. Its defaults reproduce the primary.
    - On a data machine, a pinned `analyze` after this change must write the four CSVs and `summary.md` with the sha256 the committed primary manifest records, and `result.json` equal apart from its runtime. This is an exact gate, which pinning makes valid on any machine.
    - On a synthetic dataset, which has no committed reference, the code before and after must write byte-identical CSVs and `summary.md`.
  - `render_analysis_summary` adds the latent-adjustment section and the arm's rules only when the record carries the block.
- **`axis-diagnostics` on an arm reads as an arm.** `diagnostics.md` names the analysis read as the `stage`-conditioned sensitivity arm, calls a flagged row a finding about the arm's measurement space, and prints `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`. Its error hints name the command that wrote the analysis read. On the primary, pinned, its outputs keep the hashes the committed diagnostics manifest records (`754c6ba`).
- **Docs**:
  - `README.md` and `AGENTS.md`: "the workstation" replaced by the data-machine definition below, wherever it appears.
  - `README.md`: a `latent-sensitivity` section with the command, flags, arm, covariate roles, checks, outputs and which are participant-level, the predeclared counts, the diagnostics on the arm, and the reading rules.
  - `AGENTS.md`:
    - the status;
    - the step, listed as a sensitivity step after `axis-diagnostics` without renumbering the six;
    - "Flag and ask" with the four constants;
    - the Layout entries;
    - the `report` step's inputs, which gain the comparison and the arm's diagnostics.
  - the `constants.py` docstring, and the docstrings of `run_latent_sensitivity` and of the `run_report` stub (its inputs).

Out of scope, each its own change:
- The `report` step (step 6), which pastes the comparison and the arm's diagnostics beside the primary and checks them with `report --check`. No report is written here.
- A revised primary: MOTCO's `candidate_fails` excludes it, and reading rule 9 holds.
- `group_stage` conditioning, another covariate set, latent adjustment on an export variant, the export sensitivity variants, the CN / LMCI / AD arm, the rank sweep, block weighting and attribution.
- A MOTCO pin move. MOTCO stays at `v0.10.0`, so the primary is not rerun under another release.
- The cluster run. The clone needs the deploy key (constraint 7). When it exists, the arm is rerun there pinned and must reproduce the committed hashes; a node needs AVX2 for the pinned OpenBLAS kernel, checked once before the first run.
- Any change to `clean`, `cohort`, `export` or the primary's outputs.

No result of the arm changes a constant, selects a covariate, or reruns or replaces the primary.

## Capabilities

### New Capabilities
- `motco-latent-adjustment-sensitivity`: the `latent-sensitivity` step. It covers:
  - the predeclared `stage`-conditioned arm on the primary's export and settings;
  - the primary as a read-only, chained reference;
  - the covariate-role justification and the rare-level condition;
  - the arm's analysis directory, which mirrors the primary's;
  - the comparison generated from the two records;
  - the predeclared counts and findings, and reproducibility;
  - the arm's reading rules, carried by every reader of the arm.

### Modified Capabilities
- `latent-axis-diagnostic`: the reading-rules requirement. On an arm, `diagnostics.md` names the analysis read as the sensitivity arm, describes flagged rows as findings about the arm's measurement space and carries `LATENT_SENSITIVITY_READING_RULES` beside `READING_RULES`. Its output on the primary is unchanged.

## Impact

- `src/adni_sexdiff/constants.py`:
  - Scientific, decided here: `LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES`, `LATENT_SENSITIVITY_READING_RULES`.
  - Predeclared: `LATENT_SENSITIVITY_EXPECTED_COUNTS`.
  - Conventions: `LATENT_SENSITIVITY_DIR` (`results/motco_latent_sensitivity`), its subdirectory names (`analysis`, `comparison`, `diagnostics`), and the output names `latent_sensitivity.csv`, `latent_sensitivity.md`, `latent_sensitivity_manifest.json`.
  - The docstring names the change and its constants.
- `src/adni_sexdiff/data.py`:
  - the shared analysis function (from `run_analysis`, primary bytes unchanged);
  - `render_analysis_summary` with the latent-adjustment section;
  - `run_latent_sensitivity` and `render_latent_sensitivity`;
  - the primary-reference and cohort-manifest checks;
  - `render_axis_diagnostics` and the `_check_analysis_inputs` hints, arm-aware.
- `src/adni_sexdiff/cli.py`: the `latent-sensitivity` subcommand (`--input-dir`, `--analysis-dir`, `--cohort-dir`, `--out-dir`, `--n-jobs`, `--force`). The arm and its settings are constants, never flags.
- Ignore rules, the sync filter and `PARTICIPANT_LEVEL_PATTERNS`: unchanged. The two participant-level files are already matched under any `results/` path, which `git check-ignore` verifies at apply.
- Dependencies: none new. MOTCO stays at `v0.10.0` and scikit-learn at MOTCO's pin. Depends on `adni-portable-numerics` (merged, PR #6): the pinned numerics and the `numerics` block.
- Compute: one CV analysis of the primary's size (the primary ran in 26 s) plus one least-squares fit per CV training set, and one diagnostic run.
- Machines. The real run needs a data machine: any of the user's machines whose local participant-level inputs hash to the values the committed manifests record. Those inputs are `results/motco_input/*.csv` and `results/cohort/cohort.csv` for the arm, plus the primary's `latent_scores.csv` and `analysis_metadata.csv` for the primary's gates. No machine is named.
  - Any machine with a data root becomes a data machine by a pinned rebuild from it (`clean` → `cohort` → `export` → `analyze` into the scratchpad), a hash check, and copying the files into `results/`. That took under a minute on 2026-10-28.
  - nixos-office is a data machine as of 2026-10-28.
  - A machine without a data root can run every synthetic check.
- Committed, from the data machine's run, under `results/motco_latent_sensitivity/`:
  - `analysis/`: `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json`, `summary.md`;
  - `comparison/`: its three files;
  - `diagnostics/`: its six files.

  Each file is named at commit with why it is aggregate.
- Scientific choices introduced here (flag and ask before changing):
  - the single arm and its identity with the predeclared one;
  - the covariate roles, with `statin` the mediator candidate;
  - the arm's reading rules;
  - the rule that the arm never replaces the primary and feeds no choice.
