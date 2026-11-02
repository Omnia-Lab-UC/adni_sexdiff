# Proposal

## Why

Since `adni-export`, three scale variants have been named and left for one later change: the raw scale, `log2(x + 1)` and the generalized log. Every other predeclared sensitivity has run and is in the report: the latent arm, the two p180 run variants, `nmr_all_columns`, the CN / LMCI / AD arm and the rank sweep. This change registers the three scale variants and runs them.

`EXPORT_FEATURE_RULE`'s scale is `log2(x + floor)`, the floor a metabolite's 5 % quantile over the exported participants. The log is a choice. MOTCO 0.10.0 z-scores every feature, so what the latent basis and the three statistics see of a feature is the spacing of its values: how far the low values are compressed and how far the high values spread. The three variants span the alternatives: no log (`raw_scale`), the log with a pseudo-count of 1 in the platform's unit (`log2_plus_one`, the transform of the 2022 study, doi:10.3389/fradi.2022.782864) and the log with an offset too small to compress anything (`glog`, the generalized log). Each applies to both blocks. This change measures whether the three statuses depend on that one decision.

The spike of this change (`spike.md`, `scripts/spike_scale_variants.py`, nixos-home, 2026-11-02) is read-only and aggregate. It read the cleaned p180 and NMR tables and the primary export's five files, each checked against its manifest, rebuilt both blocks on the rule's scale and checked them against the primary's CSVs cell for cell, then built the three scales of the same cells. It read no MOTCO output, no metadata and no sex or stage. Its findings:
- **Every scale is monotone in the concentration.** Per feature, the participants' ranks are the primary's on every scale (Spearman 1 with the rule's scale). What changes is the spacing.
- **`raw_scale` adds right tails and loses rank.** On the concentration scale, |skew| > 1 for 46 of the 133 p180 metabolites (rule's scale: 1) and 43 of the 165 NMR concentrations (3); a largest |z| above 8 for 12 and 4 (0 and 1). The NMR block has numerical rank 104 of 165: the lipoprotein measures are exact sums of their components on the concentration scale, a relation the log breaks; the joint matrix has rank 237 of 298. Per metabolite, the Pearson agreement with the rule's scaling has median 0.990 (p180) and 0.994 (NMR) and minimum 0.886 and 0.580 (`XXL_VLDL_TG`).
- **`log2_plus_one` is near-linear for most of the NMR block.** Its offset is 1 in each platform's unit (p180 µM, NMR mostly mmol/L). A metabolite whose values lie well below 1 gets a nearly linear scale (`log2(1 + x) ≈ x / ln 2`); one whose values lie well above 1 gets nearly `log2(x)`. The median lies below 1 for 46 of the 133 p180 metabolites and 129 of the 165 NMR concentrations, and at or above 100 for 13 p180 metabolites and no NMR one. |skew| > 1 for 14 and 30 metabolites, a largest |z| above 8 for 9 and 4. The agreement with the rule's scaling has median 0.998 / 0.997 and minimum 0.934 / 0.608.
- **`glog` is `log2(x)` with the zeros protected, and leaves left tails.** With λ a tenth of the metabolite's smallest positive value, the generalized log equals `log2(x)` within 0.0036 bits on every positive cell, and a zero cell lands at `log2(λ / 2)`, 4.32 bits below the smallest positive value (41 NMR cells in 3 metabolites; the p180 block has none). Without the rule's floor, the low values are not compressed: |skew| > 1 for 6 p180 metabolites (all 6 negative) and 25 NMR concentrations (23 negative), a largest |z| above 8 for 6 and 13, above 15 for 2 p180 metabolites. The agreement with the rule's scaling has median 0.997 / 0.997 and minimum 0.918 / 0.804.
- **The run offset barely moves with the scale.** The p180 median |d| is 1.12 on the rule's scale, 1.08 raw, 1.11 under `log2(x + 1)` and 1.13 under the glog; |corr(PC1, phase)| is 0.72 to 0.73 on every scale; the NMR median |d| is 0.20 to 0.21. The p180 metabolites with |d| > 0.5 / > 1 are 108 / 76 (raw), 108 / 80 (`log2(x + 1)`) and 109 / 80 (glog), against the primary's 109 / 80.
- **The spectra barely move.** The p180 PC1 share is 0.407 to 0.418 across the scales, the NMR one 0.433 to 0.438, the joint effective rank 6.65 to 6.83, and |corr(PC1, phase)| of the standardized joint matrix 0.40 to 0.42. Descriptive only: MOTCO's basis is supervised by stage.
- **The CV folds and the RRPP draws are the primary's.** In MOTCO 0.10.0 the folds are `RepeatedStratifiedKFold(random_state)` on the stage labels and the draws are `rng.permutation(n)` from the seed. Neither reads the features.

No setting below comes from a sex × stage result.

## What Changes

- **Three export variants, `raw_scale`, `log2_plus_one` and `glog`**, run by the existing `export-sensitivity` step (`--variant <name>`) through its shared export body, a new hook `scale` on both blocks, and the shared analysis body.
  - **Export:** every kept cell of both blocks (the primary's membership: 133 p180 metabolites, 165 NMR concentrations) takes the variant's scale in place of the rule's `log2(x + floor)`. The participants, the metadata and the covariates are the primary's. The rule's floor is still computed, gated and recorded per metabolite, as in the primary, and not applied. The data root is not read.
  - **Analysis:** one `analyze_trajectories` call at the primary's settings per variant.
  - **Comparison:** each variant's statistics beside the primary's.
- **Scientific constants**, proposed here and decided by the user when the proposal is accepted (2026-11-02: all three variants, λ per metabolite as its smallest positive value divided by 10, one shared rule set, the report left to a later change), before any run:
  - **`SCALE_VARIANT_RULE`**, per variant, the transform of a kept cell `x` (a cleaned concentration in its platform's unit) and its additive offset:
    - `raw_scale`: `x`; no offset; MOTCO's transform `identity` and its z-scoring, as for every export.
    - `log2_plus_one`: `log2(x + 1)`; offset 1 in the platform's unit.
    - `glog`: `log2((x + sqrt(x² + λ²)) / 2)`; λ per metabolite its smallest positive value over the exported participants divided by 10 (`lambda_divisor`). A metabolite with no positive cell leaves λ undefined and stops the step before anything is written (none exists: 0 in both blocks).
  - **`EXPORT_VARIANTS["raw_scale"]`, `["log2_plus_one"]`, `["glog"]`**, after `nmr_all_columns` in that order: block `all` (both blocks), hook `scale`, rule `SCALE_VARIANT_RULE`, no data root, change `adni-scale-variants`. The settings:
    - `raw_scale`: "both blocks on the raw scale: every kept cell the cleaned concentration as metabo_adni leaves it, in its platform's unit, with no log and no offset (SCALE_VARIANT_RULE); MOTCO's transform identity and its z-scoring; the membership, the participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied";
    - `log2_plus_one`: "both blocks on log2(x + 1): every kept cell log2 of the cleaned concentration plus 1 in its platform's unit, the transform of the 2022 study (SCALE_VARIANT_RULE); the membership, the participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied";
    - `glog`: "both blocks on the generalized log log2((x + sqrt(x² + λ²)) / 2), λ per metabolite its smallest positive value over the exported participants divided by 10 (SCALE_VARIANT_RULE); the membership, the participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied".

    The three existing entries are not touched: no key is added, so their recorded `variant` blocks stay equal to the registry.
  - **`SCALE_VARIANT_READING_RULES`**: eight statements shared by the three variants, printed verbatim after `READING_RULES` in each variant's `summary.md`, its `export_sensitivity.md`, its `diagnostics.md` and every report that quotes it, in place of `EXPORT_VARIANT_READING_RULES`. Cited as "scale rule N".
    1. A scale variant is read beside the primary and never replaces it. No result of a scale variant changes a constant (the scale of `EXPORT_FEATURE_RULE` included), reruns the primary or adopts a variant.
    2. A scale variant shares with the primary the cleaned tables, the participants, the membership of both blocks (133 p180 metabolites, 165 NMR concentrations), the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the scale of the cell values of both blocks. Every scale is a monotone function of the concentration, so each participant's rank on each feature is the primary's; what changes is the spacing of the values, which MOTCO's z-scoring passes to the basis and the statistics. A rejection status that differs is dependence on the scale, not a result of the variant.
    3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
    4. `log2_plus_one` and `glog` keep the log and change its offset. The primary's offset is the metabolite's 5 % quantile (floor over median: p180 median 0.60, NMR 0.65), which compresses the lowest values of every metabolite alike. `log2_plus_one` is the transform of the 2022 study (doi:10.3389/fradi.2022.782864): its offset is 1 in each platform's unit (p180 µM, NMR mostly mmol/L), so an abundant metabolite gets nearly `log2(x)` and a scarce one a nearly linear scale (median below 1: 46 of 133 p180 metabolites, 129 of 165 NMR concentrations). It is not a reproduction of that study, whose membership, winsorizing, outlier removal and medication residuals differ, and no agreement or disagreement with it is read from the variant. `glog` is the generalized log with λ a tenth of the metabolite's smallest positive value: `log2(x)` within 0.004 bits on every positive cell, a zero cell 4.3 bits below the smallest positive value (41 NMR cells in 3 metabolites), and no compression of the low values, so it carries left tails (|skew| > 1 for 6 p180 and 25 NMR metabolites, a largest |z| above 8 for 6 and 13).
    5. `raw_scale` takes the cleaned concentrations with no log. MOTCO z-scores each feature, so the right tails of the concentration distributions carry leverage (|skew| > 1 for 46 p180 and 43 NMR metabolites, a largest |z| above 8 for 12 and 4, against 1 and 3, 0 and 1 on the rule's scale), and the NMR block loses numerical rank (104 of 165; the joint matrix 237 of 298): the lipoprotein measures are exact sums of their components on the concentration scale, a relation the log breaks. A difference reflects those tails and that geometry, never evidence that one scale measures what another does not.
    6. A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in a variant is dependence on the scale, read beside the variant's rank and null summary.
    7. The variant's export manifest records the shape counts of each block on its scale, the numerical rank of each block, the run offset per block and the offset of each metabolite (the feature tables). They are reported beside the results. The run offset barely moves with the scale (p180 median |d| 1.08 to 1.13 against the primary's 1.12). A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.
    8. A scale variant is read against the primary only, never against another scale variant, another export variant, an arm or a rank. No sentence reads it against another sensitivity, and a difference between two scale variants is not evidence for either.

    Rules 1, 2, 3, 6 and 7 have the roles of `EXPORT_VARIANT_READING_RULES` 1, 2, 3, 6 and 7, so a sentence that cites a rule by its role cites the same number under every set.
  - **The dependence label** of the three variants: `differs (scale dependence)`. The p180 variants keep `differs (run-handling dependence)` and `nmr_all_columns` `differs (feature-membership dependence)`.
- **Predeclared counts** (`EXPORT_VARIANT_EXPECTED_COUNTS[<variant>]`, from the spike and the committed manifests, none from a run of a variant; a deviation is a finding, never a stop). Shared by the three: 1501 participants in the primary's cells; features the primary's (p180 133 / 133, NMR 245 cleaned, 165 kept, derived 72 / 4 / 1 / 3); zero cells p180 0 and NMR 41 in 3 metabolites (counted before the transform); floors not positive 0 and non-finite cells 0 per block; 0 participants whose run differs from `phase`; `metadata.csv` and `covariates.csv` equal to the primary's; 0 missing covariate values; `analysis` every key of `ANALYSIS_EXPECTED_COUNTS`. Per variant:

  | quantity | `raw_scale` | `log2_plus_one` | `glog` |
  |---|---|---|---|
  | p180 shape: \|skew\| > 1; largest \|z\| > 8 | 46; 12 | 14; 9 | 6; 6 |
  | NMR shape: \|skew\| > 1; largest \|z\| > 8 | 43; 4 | 30; 4 | 25; 13 |
  | numerical rank p180; NMR | 133; 104 | 133; 165 | 133; 165 |
  | run offset, p180 metabolites with phase \|d\| > 0.5 / > 1 | 108 / 76 | 108 / 80 | 109 / 80 |
  | run offset, NMR metabolites with phase \|d\| > 0.5 / > 1 | 2 / 0 | 2 / 0 | 2 / 0 |
  | metabolites with a median below the offset (p180; NMR) | n/a | 46; 129 | n/a |

  The ranks are not predeclared. No `diagnostics` key: the diagnostic's rank-independent keys hold (165 NMR features).
- **The variant code reads the new rule set.** `EXPORT_VARIANT_RULE_SETS` gains one shared entry for the three (rules `SCALE_VARIANT_READING_RULES`, citation "scale rule", label `scale dependence`, source "the scale of both blocks"), and the words the renderers take from the variant's block and hook gain a branch for block `all` and hook `scale` (what the variant changes, what it keeps, the `phase` line, the "Export variant" lines with the transform, the offsets, the shape counts and numerical ranks of both exports). The six existing text outputs of the three registered variants keep their bytes: every one, re-rendered from its committed records, must equal the committed file.
- **The report is unchanged.** `REPORT_EXPORT_VARIANTS` stays at the three current variants, so `report` reads the same 106 files, prints one progress line per scale variant and writes the same body; `reports/motco-adni-2026-11-02.md` must still pass `report --check` with no mismatch after this change. A later report change adds the scale group.
- **Outputs** under `results/motco_export_sensitivity/<variant>/`, laid out as `nmr_all_columns`'s (no `bridge/`): `motco_input/` (the four CSVs and the two feature tables, participant-level or gitignored, matched by the existing `results/motco_export_sensitivity/*/motco_input/*.csv`; `manifest.json`), `analysis/` (the seven files `analyze` writes), `comparison/` (the three comparison files) and `diagnostics/`, written by `axis-diagnostics --input-dir <variant>/motco_input --analysis-dir <variant>/analysis --out-dir <variant>/diagnostics`, run in this change. No new participant-level pattern is needed.
- **Docs:** `README.md` (the `export-sensitivity` section: the three variants, the hook, the rule set and the counts; the `report` section: three uncovered variants), `AGENTS.md` (the status, constraint 5, the `export-sensitivity` entry, "Flag and ask" with `SCALE_VARIANT_RULE`, `SCALE_VARIANT_READING_RULES` and the counts, the Layout, and the sentence that leaves the scale variants to a later change), the `constants.py` docstring, the step docstrings and the one `export-sensitivity` help string of `cli.py`.

Out of scope, each its own change:
- **The report.** A later change adds the three variants to `REPORT_EXPORT_VARIANTS` as one group under `SCALE_VARIANT_READING_RULES`, chooses that group's table-title prefix, and re-issues the report. Until then the 2026-11-02 report stays valid.
- **Other λ rules or offsets** (a λ per block, a λ from replicates, `log2(x + c)` for another `c`, a log10 or natural log, which differ from `log2` by a constant factor that MOTCO's z-scoring removes).
- **A 2022-like export** that combines `log2(x + 1)` with all 245 NMR columns, winsorizing, outlier removal or medication residuals.
- **Crossings:** a scale variant under the latent adjustment, the CN / LMCI / AD arm, the rank sweep or another export variant.
- **Model terms:** block weighting, a rank-aware treatment of the collinear NMR block, and any change to `EXPORT_FEATURE_RULE` or the primary.
- **Pin and cluster:** a MOTCO pin move, and the cluster run (constraint 7).

No variant result changes a constant, selects a metabolite or a scale, reruns the primary or replaces it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities
- `motco-export-sensitivity`:
  - the registry gains `raw_scale`, `log2_plus_one` and `glog`;
  - a requirement for the scale variant export (both blocks, the three transforms, λ, the offset per metabolite, the rule's floor recorded and not applied, no data root);
  - the unchanged-files rule names a variant of both blocks (`metadata.csv` and `covariates.csv`);
  - the comparison summary, the predeclared counts and the reading rules take the scale variants' rule set and counts;
  - the three variants registered before this change keep their outputs.
- `latent-axis-diagnostic`:
  - "Reading rules of a sensitivity read" names a scale variant and the two blocks it changes, and prints `SCALE_VARIANT_READING_RULES`.

## Impact

- `src/adni_sexdiff/constants.py`:
  - scientific, decided here: `SCALE_VARIANT_RULE`, the three `EXPORT_VARIANTS` entries, `SCALE_VARIANT_READING_RULES` and the label `scale dependence`;
  - predeclared: `EXPORT_VARIANT_EXPECTED_COUNTS` for the three, each with `analysis`;
  - conventions: the shared `EXPORT_VARIANT_RULE_SETS` entry; the existing import-time assertions cover the new keys;
  - the docstring names the change and its constants.
- `src/adni_sexdiff/data.py`:
  - `_run_export` gains the `scale` hook: the variant's transform on both blocks after the rule's floor is computed and gated, λ per metabolite, the `offset` column of the feature tables, the offset and numerical-rank counts, the primary's shape counts copied into the reference;
  - `_variant_words`, `_export_variant_lines`, `_export_variant_phase_line` and the export-context line of `render_analysis_summary` gain their branch for block `all` and hook `scale`;
  - `_run_export_variant`, the comparison, the findings, the status line, `render_export_sensitivity`, `render_axis_diagnostics` and the report are unchanged in code: they already take every variant-specific word from the rule set, and the report iterates the pin.
- `src/adni_sexdiff/cli.py`: `--variant` lists the registry, which now holds six names; the help string of `export-sensitivity` names the scale variants.
- `.gitignore`, `scripts/sync_results.sh`, `PARTICIPANT_LEVEL_PATTERNS`: unchanged. The existing pattern matches each variant's export CSVs.
- `scripts/spike_scale_variants.py` (new, read-only) and `spike.md` in this change.
- Dependencies: none new. MOTCO stays at `v0.10.0`.
- Compute: three CV analyses on 298 features at 9999 permutations, each about the primary's size, three `--force` reruns and three diagnostic runs. The gates add one pinned primary export and one pinned in-place rerun of the three registered variants.
- Machines: a data machine. nixos-home is one: the spike ran there on 2026-11-02 and every input matched its manifest. No machine is named in the code.
- Risk owned by the apply: MOTCO has not been run on a block of numerical rank 104 (`raw_scale`'s NMR block). If `analyze_trajectories` stops on it, the step stops with MOTCO's message and nothing is written, as the latent arm's rare-level condition is not worked around; the proposal is then revised, never the variant's scale.
- Committed, from the data machine's runs, under `results/motco_export_sensitivity/<variant>/` for each of the three: `motco_input/manifest.json`; `analysis/` `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md`; the comparison's three files; the diagnostics' six files (15 per variant, 45 in all). Each file is named at commit with why it is aggregate.
- Scientific choices introduced here (flag and ask before changing):
  - the three scales and λ's rule (`SCALE_VARIANT_RULE`), applied to both blocks on the primary's membership;
  - the shared reading rules and dependence label;
  - the rule that a scale variant never replaces the primary and feeds no choice.
