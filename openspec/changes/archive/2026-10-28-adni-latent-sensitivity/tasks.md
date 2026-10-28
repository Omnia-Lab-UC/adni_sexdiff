# Tasks

Nothing runs on ADNI data until the user has accepted the proposal's three scientific constants: `LATENT_SENSITIVITY_ARM` (the single `stage`-conditioned arm, which must equal `ANALYSIS_PREDECLARED_LATENT_SENSITIVITY`), `LATENT_SENSITIVITY_COVARIATE_ROLES` (`statin` the mediator candidate) and `LATENT_SENSITIVITY_READING_RULES` (nine statements). They must also be in `constants.py` (task 1.1). The approach to the mediator condition, roles beside the cohort manifest's descriptives with no new statistic, was chosen by the user on 2026-10-28.

Every run is pinned (`NUMERIC_SETTINGS`, `adni-portable-numerics`, merged in PR #6), and every manifest records its `numerics`.

Groups 1 to 4 use synthetic data only, never a data root, and can run on any machine, including one without a data root.

Groups 5 and 6 run on a data machine (design, Context):
- A data machine is any machine whose local participant-level inputs hash to the values the committed manifests record: the export CSVs, `cohort.csv`, and the primary's `latent_scores.csv` and `analysis_metadata.csv`.
- Task 5.1 gates on that, and rebuilds the machine pinned first if needed. No machine is assumed; nixos-office qualified on 2026-10-28.
- Pinned runs write the committed bytes on any machine, so the real-data gates compare with the committed hashes exactly.
- Groups 5 and 6 still run on one data machine throughout, and every real-data task line names its hostname.

No task line records a participant value.

## 1. Constants and the synthetic baseline

- [x] 1.1 Add the constants of design D3 to `constants.py`:
  - the conventions `LATENT_SENSITIVITY_DIR`, `LATENT_SENSITIVITY_SUBDIRS`, `LATENT_SENSITIVITY_TABLE`, `LATENT_SENSITIVITY_SUMMARY` and `LATENT_SENSITIVITY_MANIFEST`;
  - the scientific `LATENT_SENSITIVITY_ARM`, `LATENT_SENSITIVITY_COVARIATE_ROLES` (role and justification per covariate, the proposal's wording) and `LATENT_SENSITIVITY_READING_RULES` (the proposal's nine statements, verbatim);
  - the predeclared `LATENT_SENSITIVITY_EXPECTED_COUNTS`;
  - the two import-time assertions;
  - the module docstring, naming this change and its constants.

  Verify with `uv run python -c "from adni_sexdiff import constants as c; print(c.LATENT_SENSITIVITY_ARM['conditioning'], tuple(c.LATENT_SENSITIVITY_COVARIATE_ROLES), len(c.LATENT_SENSITIVITY_READING_RULES), c.LATENT_SENSITIVITY_EXPECTED_COUNTS['latent_adjustment']['design_columns'], c.LATENT_SENSITIVITY_EXPECTED_COUNTS['latent_adjustment']['residual_df'])"`. It must print `stage`, the five covariates in `ANALYSIS_COVARIATES` order, `9`, the eight residualization design columns starting `stage[1]`, `stage[2]`, and `1492`. A deliberately edited copy of the module in the scratchpad (`conditioning` `group_stage`) must fail the assertion at import.
- [x] 1.2 In the session scratchpad, write `make_synthetic.py` (design D10).
  - It writes an export directory that `_load_analysis_inputs` accepts:
    - random blocks of 133 and 165 features for n = 400;
    - `sex` and `stage` with every cell populated;
    - the five covariates with the real codings and every level present;
    - a `phase` offset planted on most `p180` features;
    - `manifest.json` with `outputs` hashes, `settings.block_columns`, `settings.covariates`, `inputs.cohort.manifest.sha256` and the `counts` that `analyze` and `axis-diagnostics` read.
  - It also writes a bound cohort directory: `cohort.csv` with `dx_bl` and both platform flags, and `cohort_manifest.json` with the table's hash and `descriptives.cells` per sex × stage in the real layout.
  - Then it runs the unmodified `run_analysis` and `run_axis_diagnostics` into `syn/A/` as the byte-identity baseline, at 99 permutations so a run takes seconds.

  Verify that both complete and that the analysis manifest records the five export hashes. Keep `syn/A/`.

## 2. The shared analysis path and the arm's summary

- [x] 2.1 Move `run_analysis`'s body into `_run_trajectory_analysis` (design D2), with `step`, `latent_adjustment`, `expected` and `manifest_extra`. `run_analysis` becomes a call with the primary's values, its docstring unchanged in substance. The manifest of the primary keeps every key and value it has today. Verify that a rerun of the synthetic primary into `syn/B/` gives `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `summary.md` byte-identical to `syn/A/`, and `result.json` and `analysis_manifest.json` equal apart from `created_at`, `runtime_seconds`, `git_revision` and the output path in `cli_equivalent`.
- [x] 2.2 Teach `render_analysis_summary` the arm (design D7): the title and header, a "Latent adjustment" section, the arm note on each non-rejection, and `LATENT_SENSITIVITY_READING_RULES` after `READING_RULES`. All of it only when the record carries `latent_adjustment`.
  - The synthetic primary's `summary.md` must stay byte-identical to `syn/A/` (rerun 2.1's check).
  - A synthetic arm record from `_run_trajectory_analysis(latent_adjustment="stage", ...)` into a scratch directory must render the section with conditioning `stage`, the eight design columns with `stage[1]` = MCI and `stage[2]` = AD, residual df n − 9, the smallest CV training df, the `feature_r2` quantiles and mean, and the nine arm rules string-equal to the constant.

## 3. The `latent-sensitivity` step

- [x] 3.1 Implement `_check_primary_reference` and `_check_cohort_manifest` (design D4). On scratch copies of the synthetic trees, verify that each of these stops naming the file or setting, both values and the command to rerun, with nothing created under the output root and the input trees hashing the same before and after:
  - (a) an absent primary directory;
  - (b) `p180.csv` rewritten with its hash updated in the export manifest only;
  - (c) a primary manifest edited to record MOTCO `0.9.0`;
  - (d) a primary manifest with `latent_adjustment` `stage`;
  - (e) an edited `cohort_manifest.json`;
  - (f) a primary manifest with `ANALYSIS_SEED` changed.
- [x] 3.2 Implement `run_latent_sensitivity` (design D4, D5, D9): the gates; the output check; the loader and the two reference checks; the arm through `_run_trajectory_analysis` into `analysis.tmp/` with `manifest_extra` (`arm`, `reference`); the comparison into `comparison.tmp/`; the nested renames; the findings. Verify on the synthetic trees at 99 permutations:
  - `analysis/` holds the seven files and `comparison/` its three files, with no `.tmp/` left;
  - the arm record carries `latent_adjustment` with conditioning `stage` and `params.covariate_latent_adjustment` `stage`;
  - the arm's `covariates` block (columns, kinds, levels, reference levels, design columns, reference row) and `design.cell_sizes` equal the primary's;
  - the arm manifest lists exactly the five export files as inputs, records the primary's two hashes under `reference`, and carries the `numerics` block with `pinned` true and no separate `host` key, as the comparison manifest does;
  - `deviations` name the synthetic sizes (participants 400 against 1501, the cells, `n_samples`, `residual_df`) and the step completes;
  - the primary and export trees hash the same before and after;
  - an existing output without `--force` raises naming the directory, and leaves both directories unchanged.
- [x] 3.3 Implement the comparison rows, `latent_sensitivity.csv`, `render_latent_sensitivity` and `latent_sensitivity_manifest.json` (design D6). Verify on the synthetic run:
  - every cell of the CSV equals its value in the primary or arm `result.json` (round-trip parsing);
  - the status column reads `same` or `differs (basis dependence)` exactly as the two rejections dictate, and a hand-edited copy of the arm record with one flipped p-value turns that row's status and adds the finding;
  - the Markdown carries the roles string-equal to `LATENT_SENSITIVITY_COVARIATE_ROLES` beside the cohort manifest's per-cell descriptives copied value for value, names `statin` as the mediator candidate, and prints `READING_RULES` then the nine arm rules verbatim;
  - a cohort manifest whose cells differ from the record's gives the cell finding;
  - a second `--force` run gives a byte-identical `latent_sensitivity.csv` and byte-identical arm CSVs.
- [x] 3.4 Force a residualization failure on a scratch copy of the synthetic export: give one `apoe4` level a single participant, so the CV training sets that exclude that participant lack the level, with the export manifest's hashes and counts updated. Verify that the step stops with MOTCO's message naming the repeat and fold (or the full-sample design), that no output directory or `.tmp/` remains under the output root, and that no constant or input changed. (Done 2026-10-28 on nixos-office: the primary manifest of the scratch copy was re-chained to the edited export manifest too, since the primary-reference check otherwise stops first; MOTCO stopped at repeat 1, outer fold 1, with the output root absent and the inputs and constants unchanged.)
- [x] 3.5 Add the `latent-sensitivity` subcommand to `cli.py` (`--input-dir`, `--analysis-dir`, `--cohort-dir`, `--out-dir`, `--n-jobs`, `--force`; `[latent-sensitivity]` progress lines with counts only; the comparison's statistics and statuses printed at the end) and the `run_latent_sensitivity` docstring (inputs, checks, outputs, contract, findings). Verify:
  - `uv run adni-sexdiff latent-sensitivity --help` lists the six flags with their defaults;
  - a synthetic run through `cli.main` prints no `rid` value;
  - `--n-jobs 4` into a scratch root gives the `n_jobs` finding in both manifests.
- [x] 3.6 Run the synthetic arm's `cli_equivalent` with `uv run motco analyze` into a scratch directory. Verify that `statistics`, `p_values`, `null_summary`, `latent_adjustment` and the selected rank equal the arm record's, and that `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` are byte-identical.

## 4. `axis-diagnostics` on an arm, and the docs

- [x] 4.1 Make `render_axis_diagnostics` and the `_check_analysis_inputs` hints arm-aware (design D8). Verify:
  - a rerun of the synthetic primary diagnostic into `syn/B/` gives four CSVs and `diagnostics.md` byte-identical to `syn/A/`;
  - `axis-diagnostics --analysis-dir <synthetic root>/analysis --out-dir <synthetic root>/diagnostics` passes its chain checks, records `is_primary` false with latent adjustment `stage`, and writes a `diagnostics.md` that names the `stage`-conditioned arm, calls flagged rows findings about the arm's measurement space, and prints the nine arm rules after `READING_RULES`;
  - an arm directory with an altered export hash stops naming `adni-sexdiff latent-sensitivity`.
- [x] 4.2 Rerun `run_latent_sensitivity --force` on the synthetic trees while `diagnostics/` exists. Verify the replaced-arm finding (design D5), that `diagnostics/` is untouched (same hashes), and, by reading the code, that the step only tests the directory's existence and opens nothing under it.
- [x] 4.3 Update the docs:
  - `README.md` and `AGENTS.md`: replace every "the workstation" with the data-machine definition.
    - A data machine is any machine whose local participant-level `results/` hash to the committed manifests. The checks pick it, and no machine is named.
    - Any machine with a data root becomes one by a pinned rebuild from it, a hash check, and copying the files into `results/`.
    - The manifests before `adni-portable-numerics` record no machine, but their outputs reproduce pinned on any machine.
  - `README.md`: the status, and a `latent-sensitivity` section after `axis-diagnostics` with:
    - the command and flags;
    - the arm, and why it is the only one;
    - the covariate roles;
    - the checks and the rare-level condition;
    - the layout, with every file marked participant-level or committed;
    - the predeclared counts and findings;
    - the diagnostics on the arm;
    - the reading rules.
  - `AGENTS.md`:
    - the status paragraph;
    - the step, listed as a sensitivity step after step 5 without renumbering;
    - "Flag and ask" with the three scientific constants and their values, the rule that the arm never replaces the primary and feeds no choice;
    - the Layout entries for `constants.py`, `data.py` and `results/`;
    - step 6's inputs, which gain the comparison and the arm's diagnostics.
  - The `run_report` stub docstring, naming the same inputs.

  Verify that every `LATENT_SENSITIVITY_*` name in `README.md` and `AGENTS.md` exists in `constants.py`, that the documented flags match `--help`, that `CLAUDE.md` is unchanged and that `grep -n "undecided" AGENTS.md README.md src/adni_sexdiff/constants.py` lists nothing.

## 5. Real-data gates and run on a data machine

- [x] 5.1 Readiness gate (design D10), after `git pull` and `uv sync --locked` on the branch. With a scratch script that prints only file names and `match` / `DIFFERS` / `absent`, compare the sha256 of:
  - `results/motco_input/*.csv` against `results/motco_input/manifest.json`;
  - `results/cohort/cohort.csv` against `results/cohort/cohort_manifest.json`;
  - `results/motco_analysis/latent_scores.csv` and `analysis_metadata.csv` against `results/motco_analysis/analysis_manifest.json`.

  Every file must read `match`. If any does not, make the machine ready:
  1. Run a pinned rebuild from its own data root into the scratchpad: `clean --data-root <root>`, `cohort`, `export`, `analyze`, each reading the previous scratch output.
  2. Check every output hash the committed manifests record.
  3. Copy the participant-level files into the gitignored paths under `results/`, without overwriting a committed manifest.

  A rebuild that does not reproduce the committed hashes stops the change; report it to the user. Record in this line the hostname, whether a rebuild was needed, and the outcome. (Done 2026-10-28 on nixos-office at `16bef50` plus the uncommitted implementation: the six export CSVs, `cohort.csv`, `latent_scores.csv` and `analysis_metadata.csv` all read `match`; no rebuild was needed.)
- [x] 5.2 Exact gate for `analyze` (design D2): a pinned `uv run adni-sexdiff analyze --out-dir <scratch>/primary` on the default inputs. Verify that `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv` and `summary.md` have the sha256 the committed `results/motco_analysis/analysis_manifest.json` records, and that `result.json` equals the committed one apart from `measurement.runtime_seconds`. On any difference, stop and revert the refactor. Record the outcome in this line; delete the scratch directory. (Done 2026-10-28 on nixos-office: the five files match the committed hashes, `result.json` equals apart from the runtime, the scratch manifest records `numerics.pinned` true, no deviation, no finding; rank 8, 19.3 s; scratch directory deleted.)
- [x] 5.3 Exact gate for `axis-diagnostics` (design D10): a pinned `uv run adni-sexdiff axis-diagnostics --out-dir <scratch>/diagnostics` on the default inputs. Verify that the four CSVs and `diagnostics.md` have the sha256 the committed `results/motco_diagnostics/diagnostics_manifest.json` records (re-issued in `754c6ba`), and that the scratch manifest records `numerics.pinned` true. On any difference, stop and revert 4.1. Record the outcome in this line; delete the scratch directory. (Done 2026-10-28 on nixos-office: the four CSVs and `diagnostics.md` match the committed hashes, `numerics.pinned` true, no deviation; scratch directory deleted.)
- [x] 5.4 Run `uv run adni-sexdiff latent-sensitivity` at `n_jobs = 1`. Verify:
  - `results/motco_latent_sensitivity/analysis/` and `comparison/` hold their files, with no `.tmp/`;
  - `deviations` is `[]` (1501, the six cells, 133 / 165 / 298, the six design columns, the level counts, 0 dropped, `cv`, floor 2, 9999 permutations, conditioning `stage`, the eight residualization design columns, 1501 samples, residual df 1492, `pooled_standardized`);
  - the arm's `covariates` block equals the primary's;
  - both new manifests record `numerics.pinned` true and this machine's hostname;
  - `results/motco_input/`, `results/motco_analysis/` and `results/cohort/` hash the same before and after.

  Record in this line, numbers only:
  - per analysis the rank, `cv_mean_auroc` and eigengap;
  - per statistic observed, p, rejection and status;
  - the smallest CV training df;
  - the `feature_r2` quantiles and mean;
  - the findings;
  - the runtime.

  Done 2026-10-28 on nixos-office (`numerics.pinned` true in both manifests, host nixos-office; the input trees hashed the same before and after; `deviations` `[]`; the arm's covariates block and cell sizes equal the primary's):
  - rank: primary 8, arm 4; `cv_mean_auroc` 0.599514 / 0.580311; pooled relative eigengap 0.743990 / 0.878123;
  - `delta`: primary 1.10279 (p 0.1116, not rejected), arm 1.55786 (p 0.0568, not rejected), same; `angle`: 16.5406 (p 0.6879, not rejected), 14.2407 (p 0.7244, not rejected), same; `shape`: 0.107355 (p 0.7105, not rejected), 0.179861 (p 0.6402, not rejected), same;
  - smallest CV training df 741 (residual df 1492, 8 residualization design columns);
  - `feature_r2` q05 / q25 / q50 / q75 / q95 0.0145 / 0.0338 / 0.1161 / 0.2582 / 0.4864, mean 0.1658 (fraction above 0.5: 0.047);
  - findings: the arm's CV-selected rank 4 differs from the primary's 8 (arm rule 3); nothing else;
  - runtime 18.3 s.
- [x] 5.5 Verify the arm: a `--force` rerun into a scratch `--out-dir` gives a byte-identical `latent_sensitivity.csv` and arm CSVs; the arm's `cli_equivalent` run with `uv run motco analyze` into a scratch directory reproduces the record and the three MOTCO CSVs byte for byte; a run with `--n-jobs 4` into a scratch root carries the `n_jobs` finding. Record the outcomes in this line; delete the scratch directories. (Done 2026-10-28 on nixos-office: the scratch-root rerun matched `latent_sensitivity.csv`, `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv` and `analysis_metadata.csv` byte for byte, after the arm row's `directory` column was made the subdirectory name under the output root so the table does not depend on the root; `motco analyze` reproduced `statistics`, `p_values`, `null_summary`, `latent_adjustment`, rank 4 and the three CSVs; the `--n-jobs 4` run carried the `n_jobs` finding in both manifests with the same statistics and rank; scratch directories deleted.)
- [x] 5.6 Run `uv run adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics`. Verify the six files, `is_primary` false with latent adjustment `stage`, `numerics.pinned` true, the rank-independent expectations without deviation, and the arm wording and rules in `diagnostics.md`. Record in this line, numbers only: per component the score SD and the loading shares, the flagged rows (variable, rho, partial rho), and the first component's correlation with `phase` beside the primary's 0.542. (Done 2026-10-28 on nixos-office: six files, `is_primary` false, latent adjustment `stage`, `numerics.pinned` true, `deviations` `[]` on the five rank-independent keys, the arm named and both rule sets printed. Components (sd; loading share p180 / nmr): pls_0 6.298, 0.254 / 0.746; pls_1 3.583, 0.573 / 0.427; pls_2 6.797, 0.676 / 0.324; pls_3 2.453, 0.768 / 0.232. Flagged rows: pls_1 `male` rho −0.477, partial −0.458; pls_2 `phase` 0.416, partial n/a; pls_2 `statin` 0.334, partial n/a. pls_0 against `phase`: 0.241, beside the primary's 0.542; block pc1 against `phase` unchanged (p180 −0.757, nmr −0.130).)
- [x] 5.7 Verify the controlled-access contract:
  - `git check-ignore -q` succeeds for `analysis/latent_scores.csv` and `analysis/analysis_metadata.csv` and fails for every other file under `results/motco_latent_sensitivity/`;
  - `grep -nE '\bRID\b|\brid\b'` over every file under `results/motco_latent_sensitivity/` that `git check-ignore` does not match hits only column-name mentions;
  - `ADNI_SYNC_SOURCE=results ADNI_SYNC_TARGET=<scratch> scripts/sync_results.sh -n` lists the aggregate files and neither participant-level file.

  Record the outcome in this line. (Done 2026-10-28 on nixos-office: `git check-ignore -q` succeeds for exactly `analysis/latent_scores.csv` and `analysis/analysis_metadata.csv` and fails for the other fourteen files; the `RID` / `rid` grep hits only the sample-column name in `analysis_manifest.json` (settings and `cli_equivalent`) and `result.json`; the sync dry run lists the fourteen aggregate files and neither participant-level file.)

## 6. Commit hygiene

- [x] 6.1 (Done 2026-10-28 on nixos-office, branch `adni-latent-sensitivity`: the implementation is `ed17ca9`; the arm, its comparison and its diagnostic were regenerated on the clean tree at that commit with `diagnostics/` absent, so no stale replaced-arm finding, and committed as `eac892d` with the fourteen files listed one by one; the staged list held nothing else under `results/`; the three manifests record `ed17ca9`, `dirty` false and `numerics.pinned` true; the regenerated CSVs equal 5.4's and 5.6's byte for byte; the `RID` grep over the change directory hits only the spec's and this file's column-name mentions; `openspec validate adni-latent-sensitivity --strict` passes.) Commit the implementation first. Then regenerate the arm (`latent-sensitivity --force`) and its diagnostics (`axis-diagnostics --force` with the arm's directories) on the clean tree at that commit, on the data machine of group 5, so the manifests record the commit and that machine. Run `git status` and `git check-ignore -q` over every file under `results/motco_latent_sensitivity/`. List in the outputs commit message the fourteen added files, each with why it is aggregate:
  - `analysis/`: `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json`, `summary.md`;
  - `comparison/`: its three files;
  - `diagnostics/`: its six files.

  Verify that the staged list holds nothing else under `results/`, that every manifest under `results/motco_latent_sensitivity/` records `numerics.pinned` true, that the regenerated CSVs equal 5.4's and 5.6's byte for byte, that `grep -nE '\bRID\b' openspec/changes/adni-latent-sensitivity` hits only column-name mentions, and that `openspec validate adni-latent-sensitivity --strict` passes.

## Workflow follow-up

- Archive the change after the data machine's outputs are committed and the PR is merged. The archive creates `openspec/specs/motco-latent-adjustment-sensitivity/` and applies the `latent-axis-diagnostic` delta.
- Next change: `adni-report` (step 6 with `--check`). It pastes the primary, its diagnostics, the comparison and the arm's diagnostics, and carries `READING_RULES` and `LATENT_SENSITIVITY_READING_RULES`. Later: the export sensitivity variants, the CN / LMCI / AD arm and the rank sweep, each its own proposal.
- User: when the deploy key and the cluster data copy exist, check AVX2 on a node first (`grep -m1 -o avx2 /proc/cpuinfo` in a job; the pinned OpenBLAS kernel needs it). Then rerun `analyze` and `latent-sensitivity` on the cluster pinned: the pulled outputs must reproduce the committed hashes, with `numerics.pinned` true and the node's CPU in the manifests.
