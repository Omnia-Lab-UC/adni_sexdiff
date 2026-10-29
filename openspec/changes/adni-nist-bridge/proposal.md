# Proposal

## Why

The p180 block's first axis is the assay run: median |d| 1.12 between ADNI-1 and ADNI-GO/2 over the 133 metabolites, and PC1 correlates 0.73 with the run (export manifest). The primary handles it with `phase` as a covariate of the stage means. It leaves the run in the latent space, where `pls_0` tracks phase (ρ 0.54, committed diagnostics). On 2026-10-29 a look at the ADNI QC material found three things:
- metabo_adni's cross-plate correction anchors each run to its own study pool, so it never links the two runs;
- NIST SRM 1950 (NIST's Standard Reference Material 1950, "Metabolites in Frozen Human Plasma") is the one material both runs measured;
- NIST shows the same offset as the participants.

The spike of this change (`spike.md`, `scripts/spike_nist_bridge.py`) quantifies it. It reads no sex, stage, diagnosis or covariate:
- The NIST offset, `b`, has the participants' sign for most metabolites (Spearman 0.82 with the participants' run offset) and carries 85 % of its sum of squares (FIA 90 %, UPLC 38 %).
- Bridging the ADNI-GO/2 concentrations by NIST lowers the block's median |d| from 1.12 to 0.29 and its |d| > 1 count from 80 to 8. PC1's correlation with the run falls from 0.73 to 0.22.
- The bridge leaves a shift common to most metabolites (median 0.11 log2), which moves the run to PC2 (ρ 0.58). It also leaves aspartate and glutamate (residual 0.67 and 0.53 log2), known sample-handling markers that a reference material cannot see.

So the bridge removes the calibration part of the offset, label-free. Per-run z-scoring removes the whole run difference whatever its source, and it is the common practice. Comparing the two separates the calibration part from the rest. Both are predeclared here as export sensitivity variants, read beside the primary and never replacing it.

An exploratory figure of 2026-10-29 (scratch, not committed) read `dx_bl` and `phase` to show the offset is the same within each diagnosis enrolled in both runs. No setting below comes from it, from the spike's participant summaries or from any sex × stage result. The bridge's rule reads NIST alone.

## What Changes

- **New `export-sensitivity` step** (`adni-sexdiff export-sensitivity --variant {nist_bridge,per_run_standardized,all}`). Per variant:
  - **Export.** It reruns the export from `results/cleaned/` and `results/cohort/` with one p180 setting changed. NMR, metadata and covariates are unchanged and must hash to the primary export's bytes.
  - **Analysis.** It runs the analysis on the variant export at the primary's settings (`ANALYSIS_*`, MOTCO's defaults, `n_jobs = 1`, pinned), through the function `analyze` and `latent-sensitivity` already share.
  - **Comparison.** It writes the variant's statistics beside the primary's.

  The primary export and analysis are read, checked and never written. `export` itself gains a variant path whose default is today's code: a pinned `export` after this change must write the committed export's hashes.
- **Scientific constants**, proposed here and decided by the user when the proposal is accepted, before any run:
  - **`EXPORT_VARIANTS`**, the registry, with two entries. Every other setting is `EXPORT_FEATURE_RULE`'s.
    - `nist_bridge`: before the rule's floor, every ADNI-GO/2 p180 concentration (run from `p180_runs.csv`) is multiplied by 2^b of its metabolite under `NIST_BRIDGE_RULE`.
    - `per_run_standardized`: the rule's p180 values (pooled floors, `log2(x + floor)`), with each metabolite centred and scaled by its population SD within its run.
  - **`NIST_BRIDGE_RULE`**:
    - **Material:** the `NIST SRM 1950 Data` sheet of the four QC workbooks, read inside `ADMC_supplement.zip` (ADNI-1: `4097_FIA_NIST_and_QC_Data.xlsx`, `4097_UPLC_NIST_and_QC_Data.xlsx`) and `ADMCDUKEP180SUPP_20170410.zip` (ADNI-GO/2: `4610 FIA p180 QC and NIST Data.xlsx`, `4610 UPLC p180 QC and NIST Data.xlsx`), rows labelled `NIST SRM 1950`.
    - **Valid replicate:** a positive number whose status, where the workbook has a status column, is not `ISTD Out of Range`. The methods summary says such data "should not be used"; only the ADNI-GO/2 workbooks carry status columns. `< LOD` and `No Interception` are text and count as missing.
    - **Inclusion:** a metabolite is bridged when at least half its replicates are valid in each run. Otherwise its factor is 1.
    - **Factor:** `b` is the mean log2 of the valid ADNI-1 replicates minus that of the valid ADNI-GO/2 replicates. The reference run is ADNI-1, which MOTCO's z-scoring makes immaterial except for the floor. The NIST rows get no plate correction (the spike: it would change `b` by a median 0.0007 log2).
    - **Scope:** both kits, matched by name with case and punctuation dropped (133 of 133).

    On these bytes the rule bridges 126 metabolites (FIA 102, UPLC 24). `C0`, `C10:2`, `C12`, `C14:1-OH`, `C6 (C4:1-DC)`, serotonin and spermidine stay at factor 1; `C0` because 17 of its 24 ADNI-GO/2 cells are ISTD-flagged.
  - **`EXPORT_VARIANT_READING_RULES`**: seven statements, printed verbatim after `READING_RULES` in every variant's `summary.md`, comparison, `diagnostics.md` and every report that quotes a variant.
    1. A variant is read beside the primary and never replaces it. No variant result changes a constant, reruns the primary or adopts a variant.
    2. A variant shares with the primary the cleaned tables, the participants, the NMR block, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the p180 values. A rejection status that differs is dependence on the handling of the p180 run, not a result of the variant.
    3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
    4. `nist_bridge` removes the part of the run offset that NIST SRM 1950 carries, between-run calibration. It assumes the run acts as one factor per metabolite, the same in plasma (NIST) and serum (participants). It leaves what NIST cannot see: a shift common to most metabolites, sample-handling differences between the protocols (the largest residuals are aspartate and glutamate) and the seven unbridged metabolites. `phase` stays a covariate of the stage means and carries what remains.
    5. `per_run_standardized` removes each p180 metabolite's whole difference in mean and spread between the runs, whatever its source: calibration, sample handling, and the stage-composition difference the runs carry, since SMC and EMCI were enrolled only in ADNI-GO/2. A difference between it and `nist_bridge` is read as the part of the run difference that is not calibration, never as evidence for either variant.
    6. A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in a variant is dependence on the run handling and is read beside the variant's rank and null summary.
    7. The variant's export manifest records the run offset per block, and for `nist_bridge` the factor per metabolite; both are reported beside the results. A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.
- **Predeclared counts** (`EXPORT_VARIANT_EXPECTED_COUNTS`, from the spike; a deviation is a finding, never a stop):

  | quantity | nist_bridge | per_run_standardized |
  |---|---|---|
  | participants, cells, features per block, families, zero cells | as `EXPORT_EXPECTED_COUNTS` | as `EXPORT_EXPECTED_COUNTS` |
  | p180 metabolites bridged: FIA / UPLC / not bridged | 102 / 24 / 7 | — |
  | p180 floors not positive, non-finite cells | 0, 0 | 0, 0 |
  | p180 metabolites with phase \|d\| > 0.5 / > 1 | 35 / 8 | 0 / 0 |
  | `nmr.csv`, `metadata.csv`, `covariates.csv` | the primary's sha256 | the primary's sha256 |
  | analysis | every key of `ANALYSIS_EXPECTED_COUNTS` | every key of `ANALYSIS_EXPECTED_COUNTS` |

  The ranks are not predeclared. Continuous summaries (median |d|, the PC correlations and shares) are quoted in `spike.md` and recorded in the manifests.
- **Raw inputs.** `RAW_INPUT_SHA256` gains the two QC archives, read through new top-level symlinks in the data root:
  - `ADMC_supplement.zip` `dc822b56…`;
  - `ADMCDUKEP180SUPP_20170410.zip` `c3f9a087…`.

  The four workbooks are read inside the archives, nothing extracted, and their sha256 are predeclared beside the rule. Only `nist_bridge` reads the data root.
- **Outputs** under `results/motco_export_sensitivity/<variant>/`:
  - `bridge/` (`nist_bridge` only): `nist_bridge.csv`, one row per p180 metabolite with its kit, replicates, valid replicates, ISTD flags, run means, SEs, `b` and whether it is bridged. Reference material only, aggregate, committed.
  - `motco_input/`: the variant export, laid out as `results/motco_input/`. Its manifest records the variant, the primary export as reference and, for `nist_bridge`, the bridge table's hash and summary.
  - `analysis/`: the seven files `analyze` writes. `summary.md` adds the variant section and `EXPORT_VARIANT_READING_RULES`.
  - `comparison/`: `export_sensitivity.csv` (the primary row, then the variant row, every value read from the records), `export_sensitivity.md` (statuses `same` / `differs (run-handling dependence)`, the run offset per block from both export manifests, the bridge summary, both sets of rules) and `export_sensitivity_manifest.json`.
  - `diagnostics/`: `axis-diagnostics --input-dir <variant>/motco_input --analysis-dir <variant>/analysis --out-dir <variant>/diagnostics`, run in this change.

  `motco_input/*.csv` is participant-level and matched by a new pattern, `results/motco_export_sensitivity/*/motco_input/*.csv`, added to `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` before any output exists. `analysis/latent_scores.csv` and `analysis/analysis_metadata.csv` are already matched. Every other file is aggregate and committed, named one by one.
- **`axis-diagnostics` reads a variant as a variant.** `diagnostics.md` names the export variant and prints `EXPORT_VARIANT_READING_RULES` after `READING_RULES`. Its output on the primary is unchanged.
- **Docs:** `README.md` (an `export-sensitivity` section); `AGENTS.md` (status, the step listed as a sensitivity step beside `latent-sensitivity`, "Flag and ask" with the four constants, the Layout, the data-root symlinks, the participant-level patterns); the `constants.py` docstring; the step docstrings.

Out of scope, each its own change:
- The report. One later change extends `report` for every variant registered by then (decided 2026-10-29).
- The other registered export variants: all 245 NMR columns, the raw scale, `log2(x + 1)`, the generalized log. The CN / LMCI / AD arm, the rank sweep, a latent-adjusted arm on a variant.
- A bridge in metabo_adni (an upstream feature and a pin move), a cleaning change, a revised primary.
- The 2022 study's reanalysis with a run term.
- The cluster run (constraint 7).

No variant result changes a constant, selects a metabolite, reruns the primary or replaces it.

## Capabilities

### New Capabilities
- `motco-export-sensitivity`: the `export-sensitivity` step and its registry of export variants. It covers:
  - the predeclared variants and the NIST bridge rule;
  - the QC archives as raw inputs;
  - the variant export as the primary pipeline with one p180 setting changed, the unchanged files byte-identical to the primary's;
  - the primary export and analysis as read-only chained references;
  - the variant analysis at the primary's settings;
  - the output layout and its participant-level patterns;
  - the comparison generated from the records;
  - the predeclared counts and findings, reproducibility, and the reading rules carried by every reader of a variant.

### Modified Capabilities
- `latent-axis-diagnostic`: "Reading rules carried" gains the variant read: `diagnostics.md` names the export variant and prints `EXPORT_VARIANT_READING_RULES` after `READING_RULES`. "Labels are read but feed no choice" names export variants beside arms.
- `raw-input-integrity`: an archive read in place is a raw file under its own name. A missing member stops the step, and the manifest records each member read with its sha256 (presence and hashing requirements).

## Impact

- `src/adni_sexdiff/constants.py`:
  - scientific, decided here: `EXPORT_VARIANTS`, `NIST_BRIDGE_RULE`, `EXPORT_VARIANT_READING_RULES`;
  - predeclared: `EXPORT_VARIANT_EXPECTED_COUNTS`, the four workbook hashes;
  - integrity: `RAW_INPUT_SHA256` gains the two archives;
  - conventions: `EXPORT_SENSITIVITY_DIR`, its subdirectories and output names;
  - participant-level: `PARTICIPANT_LEVEL_PATTERNS` gains the variant export pattern.
- `src/adni_sexdiff/data.py`:
  - the export body as a shared function with a variant path (primary bytes unchanged);
  - the NIST reader and bridge;
  - `run_export_sensitivity`, with the primary-reference checks and `render_export_sensitivity`;
  - `render_analysis_summary` and `render_axis_diagnostics`, variant-aware.
- `src/adni_sexdiff/cli.py`: the `export-sensitivity` subcommand (`--variant`, `--data-root`, `--cleaned-dir`, `--cohort-dir`, `--input-dir`, `--analysis-dir`, `--out-dir`, `--n-jobs`, `--force`). The variants and the rule are constants, never flags.
- `.gitignore`, `scripts/sync_results.sh`: the variant export pattern.
- Data root, by hand, on every data machine and the cluster: two relative symlinks, `ADMC_supplement.zip` and `ADMCDUKEP180SUPP_20170410.zip`, into `Metabolomics/p180/`.
- `scripts/spike_nist_bridge.py` (new, read-only) and `spike.md` in this change.
- Dependencies: none new. openpyxl, already installed through metabo_adni, reads the workbooks.
- Compute: per variant, one export and one CV analysis of the primary's size (the primary ran in 26 s) and one diagnostic run.
- Machines: a data machine whose data root holds the two archives. nixos-home is one: the spike ran there on 2026-10-29 and its cleaned and export inputs matched the committed manifests. No machine is named in the code.
