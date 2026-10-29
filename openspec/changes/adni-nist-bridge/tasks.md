# Tasks

Nothing runs on ADNI data until the user has accepted the proposal's scientific constants and they are in `constants.py` (task 1.1):
- `EXPORT_VARIANTS` (`nist_bridge`, `per_run_standardized`);
- `NIST_BRIDGE_RULE` (validity without `ISTD Out of Range`, half valid in each run, mean log2, no plate correction, reference ADNI-1, both kits; 126 metabolites bridged, `C0` not);
- `EXPORT_VARIANT_READING_RULES` (seven statements);
- the predeclared `EXPORT_VARIANT_EXPECTED_COUNTS`.

The user chose the validity rule, the kit scope, the second variant and the follow-up report on 2026-10-29.

Every run is pinned, and every manifest records its `numerics`.

Groups 1 to 4 use synthetic data and a synthetic data root in the session scratchpad, never the real data root. They run on any machine.

Groups 5 and 6 run on one data machine, whose cleaned, cohort and export files hash to the committed manifests (nixos-home on 2026-10-29). Every real-data task line names its hostname.

No task line records a participant value.

## 1. Constants, ignore patterns and the synthetic baseline

- [x] 1.1 Add to `constants.py`:
  - the scientific `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE` (the archives and members per run × kit, the sheet and row label, the status excluded, the inclusion share 0.5, the estimator, the reference run, the kits) and `EXPORT_VARIANT_READING_RULES` (the proposal's seven statements, verbatim);
  - the predeclared `EXPORT_VARIANT_EXPECTED_COUNTS` and the four workbook sha256;
  - `RAW_INPUT_SHA256` with the two archives;
  - the conventions `EXPORT_SENSITIVITY_DIR`, its subdirectories and output names;
  - the docstring naming the change and its constants.

  Verify with `uv run python -c "from adni_sexdiff import constants as c; print(tuple(c.EXPORT_VARIANTS), c.NIST_BRIDGE_RULE['inclusion_share'], len(c.EXPORT_VARIANT_READING_RULES), c.EXPORT_VARIANT_EXPECTED_COUNTS['nist_bridge']['p180_bridged'])"`, which must print the two names, `0.5`, `7` and the FIA / UPLC / not-bridged counts 102 / 24 / 7.
- [x] 1.2 Add `results/motco_export_sensitivity/*/motco_input/*.csv` to `.gitignore`, the exclude filter of `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS`. Verify:
  - `git check-ignore -v --no-index` ignores `results/motco_export_sensitivity/nist_bridge/motco_input/p180.csv`, `.../motco_input/features_p180.csv` and `.../analysis/latent_scores.csv`;
  - it does not ignore `.../bridge/nist_bridge.csv`, `.../motco_input/manifest.json` or `.../comparison/export_sensitivity.md`;
  - `sync_results.sh --dry-run` lists none of the ignored three.
- [x] 1.3 In the session scratchpad, write `make_synthetic.py` (design D11). It builds:
  - a synthetic data root with the two archives (fabricated QC workbooks: per run × kit, a `NIST SRM 1950 Data` sheet with plates, text `< LOD` cells, ADNI-GO/2 status columns with some `ISTD Out of Range` cells, one metabolite below half valid, one with no match) and the top-level symlinks;
  - synthetic `clean` outputs (`P180.csv`, `p180_runs.csv`, `NMR.csv`, manifests) with a planted multiplicative ADNI-GO/2 offset, and a bound `cohort` output;
  - the primary export, analysis (99 permutations) and diagnostics with today's code, into `syn/A/` as the byte-identity baseline.

  Verify that all three steps complete and their manifests chain.

## 2. The shared export path and the bridge

- [x] 2.1 Move `run_export`'s body into `_run_export(..., variant=None)` with the two p180 hooks (design D2), `run_export` calling it with the primary's values. Verify that the synthetic primary export rerun into `syn/B/` is byte-identical to `syn/A/` (every CSV, `manifest.json` apart from `created_at` and `git_revision`).
- [x] 2.2 Implement the NIST reader and `NIST_BRIDGE_RULE` (design D3 to D5): members read in place, valid replicates, ISTD exclusion where a status column exists, the half-valid inclusion, `b`, plate-clustered SEs, name matching within kit, the bridge table. Verify on the synthetic archives against values computed by hand in the scratchpad:
  - the below-half metabolite has factor 1;
  - an ISTD-flagged cell is not counted;
  - the unmatched metabolite yields a finding and factor 1;
  - the table holds one row per exported p180 metabolite and no participant value.
- [x] 2.3 Implement the hooks: the factors on the cleaned ADNI-GO/2 p180 rows before the floors (run from `p180_runs.csv`, checked against `phase`), and the per-run standardization after the scale. Verify on the synthetic data:
  - `nmr.csv`, `metadata.csv` and `covariates.csv` of both variants are byte-identical to the primary's;
  - the planted offset is removed by the bridge and the p180 per-run means and SDs are 0 and 1 under `per_run_standardized`;
  - permuting sex and stage in the synthetic `cohort.csv` leaves both variants' `p180.csv` byte-identical;
  - a participant whose run differs from its `phase` yields a finding.

## 3. The `export-sensitivity` step

- [x] 3.1 Implement the gates (design D1, D8). On scratch copies, verify that each of these stops naming the file or setting, both values and the command to rerun, with nothing created under the output root:
  - (a) an absent primary analysis;
  - (b) a primary `p180.csv` changed after the analysis;
  - (c) a primary manifest with a latent adjustment;
  - (d) a cleaned `P180.csv` changed after `clean`;
  - (e) an absent archive symlink (for `nist_bridge` only; `per_run_standardized` must still run);
  - (f) an archive missing a member.
- [x] 3.2 Implement `run_export_sensitivity` (design D1, D2, D8, D9): per variant, the export into `motco_input.tmp/`, the bridge table into `bridge.tmp/`, the analysis through `_run_trajectory_analysis` into `analysis.tmp/` with the variant and the reference recorded, the comparison into `comparison.tmp/`, the renames together, the predeclared counts and the findings. Verify at 99 permutations on the synthetic data:
  - the layout of the spec;
  - no `.tmp/` left;
  - the manifests' inputs, reference hashes and `numerics`;
  - deviations naming the synthetic sizes;
  - `--force` with an existing `diagnostics/` records the stale-diagnostics finding;
  - an existing variant without `--force` stops;
  - the primary trees hash the same before and after.
- [x] 3.3 Give `render_analysis_summary` the variant branch (design D8). Verify that the synthetic primary's and arm's `summary.md` are byte-identical to before, and that a variant's names the variant, carries the run-offset section and prints `READING_RULES` then the seven variant rules, string-equal to the constant.
- [x] 3.4 Implement `render_export_sensitivity` (design D10). Verify on the synthetic run:
  - every value in `export_sensitivity.csv` equals its source record;
  - a forced status difference (an edited scratch record) prints `differs (run-handling dependence)` and a finding;
  - the reading lines are string-equal to `_statistic_reading_line`'s.
- [x] 3.5 Add the `export-sensitivity` subcommand (`--variant`, `--data-root`, `--cleaned-dir`, `--cohort-dir`, `--input-dir`, `--analysis-dir`, `--out-dir`, `--n-jobs`, `--force`) with `[export-sensitivity]` progress lines naming counts and files only. Verify that `--help` lists the registered variants and that an unknown variant is rejected naming them.

## 4. Diagnostics read a variant as a variant

- [x] 4.1 Make `render_axis_diagnostics` and the `_check_analysis_inputs` hints variant-aware (design D10). Verify that the synthetic primary's and arm's diagnostics outputs are byte-identical to the baseline, and that `axis-diagnostics --input-dir <variant>/motco_input --analysis-dir <variant>/analysis --out-dir <variant>/diagnostics` passes its chain checks and writes a `diagnostics.md` that names the variant and prints both sets of rules.

## 5. The real run (data machine)

- [x] 5.1 Confirm the data machine (hostname recorded):
  - the cleaned, cohort and primary export files hash to the committed manifests;
  - the user has created the two top-level archive symlinks;
  - `hash_raw_file` on both archives returns `predeclared` true, and the four members hash to the predeclared values.

  Done 2026-10-29 on nixos-home: `P180.csv`, `p180_runs.csv`, `NMR.csv` and `cohort.csv` match their manifests (the cohort manifest's three clean hashes equal the clean manifests'), the six primary export files match `manifest.json`; the two symlinks were created on 2026-10-29 at the user's request (`ADMC_supplement.zip -> Metabolomics/p180/ADMC_supplement.zip`, `ADMCDUKEP180SUPP_20170410.zip -> Metabolomics/p180/ADMCDUKEP180SUPP_20170410.zip`); both archives `predeclared` true, the four members equal `NIST_BRIDGE_WORKBOOK_SHA256`.
- [x] 5.2 Run the gates on real data:
  - a pinned `export` into a scratch directory reproduces every hash the committed export manifest records (design D2);
  - a pinned `axis-diagnostics` on the primary into a scratch directory reproduces the committed diagnostics hashes.

  Done 2026-10-29 on nixos-home: the pinned `export --out-dir <scratch>` wrote the six output hashes the committed `manifest.json` records, counts without deviation; the pinned `axis-diagnostics --out-dir <scratch>` wrote the four CSVs and `diagnostics.md` with the committed hashes; both `numerics.pinned` true; scratch directories deleted.
- [x] 5.3 Run `export-sensitivity --variant all` pinned at `n_jobs = 1`. Verify:
  - no deviation from `EXPORT_VARIANT_EXPECTED_COUNTS`;
  - the unchanged files hash to the primary's;
  - `bridge/nist_bridge.csv` equals the spike's appendix (valid counts, bridged flags, `b` to 3 decimals);
  - the p180 run offsets equal the spike's (median |d| 0.29 and 0.00; |d| > 1 at 8 and 0);
  - every `numerics.pinned` is true.

  Record the ranks, statistics and statuses in this task line only by pointing to the committed files.

  Done 2026-10-29 on nixos-home, on the uncommitted implementation (rerun on the clean tree in 5.5, whose outputs are the committed ones): no deviation in either variant's export, analysis or comparison manifest; `nmr.csv`, `metadata.csv` and `covariates.csv` equal the primary's; `bridge/nist_bridge.csv` equals the spike's appendix for all 133 metabolites (kit, valid counts, ISTD flags, bridged, run means, applied `b` and its SE at 3 decimals; not bridged: `C0`, `C10.2`, `C12`, `C14.1.OH`, `C6..C4.1.DC.`, `Serotonin`, `Spermidine`); p180 run offsets `nist_bridge` / `per_run_standardized`: median |d| 0.29 / 0.00, |d| > 0.5 35 / 0, |d| > 1 8 / 0, |corr(PC1, phase)| 0.22 / 0.00, |corr(PC2, phase)| 0.58 / 0.00; runs 684 / 817, none differing from `phase`; every `numerics.pinned` true. Ranks, statistics and statuses: `results/motco_export_sensitivity/<variant>/comparison/export_sensitivity.csv` and `.md`; the only finding of each variant is its rank differing from the primary's.
- [x] 5.4 Run `axis-diagnostics` on both variants into `<variant>/diagnostics`. Verify the chain checks pass and `is_primary` is false. (Done 2026-10-29 on nixos-home: both pass the chain checks, `is_primary` false with `export_variant` recorded, `numerics.pinned` true, no deviation on the rank-independent keys; the flagged rows are in each `diagnostics/diagnostics.md`.)
- [ ] 5.5 Rerun 5.3 and 5.4 with `--force` on the clean tree after the implementation commit. Verify every output except the manifests' timestamps and revision is byte-identical to the first run.

## 6. Docs and commit hygiene

- [x] 6.1 Update `README.md` (an `export-sensitivity` section: command, variants, rule, inputs, outputs and which are participant-level, the predeclared counts, the diagnostics on a variant, the reading rules) and `AGENTS.md`:
  - the status;
  - the step listed as a sensitivity step beside `latent-sensitivity`;
  - "Flag and ask" with the four constants and their values;
  - the Layout;
  - the data-root symlinks under "Data & domain notes";
  - the participant-level patterns of constraint 1.

  Verify with `grep -n export-sensitivity README.md AGENTS.md`.
- [ ] 6.2 Before the commit of outputs, name every file added under `results/motco_export_sensitivity/` with why it is aggregate. Verify:
  - `git check-ignore` on every participant-level file;
  - `grep -rIl` for any `RID` column or value in the staged files returns nothing;
  - `openspec validate adni-nist-bridge --strict` passes.

## Workflow follow-up

- Archive the change on its branch, sync the specs, open the PR and merge, as the earlier changes did.
- The follow-up change that extends `report` with every registered export variant.
