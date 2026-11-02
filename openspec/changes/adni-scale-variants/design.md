# Design

## Context

See `proposal.md` for the motivation, the three scales, their rules and their counts, `spike.md` for every number, and the specs for the requirements. This is the state that shapes the approach.

- **`export-sensitivity` has three hooks, each on one block.** `factors` and `standardize_by_run` act on `p180`, `membership` on `nmr`; every branch of `_run_export` tests `platform == spec["block"]`. The unchanged-files check lists the CSV of every block other than `spec["block"]`, plus `metadata.csv` and `covariates.csv`. `_run_export_variant` reads the bridge and the data root for hook `factors` only.
- **The scale is applied in one place.** Per block, `_run_export` keeps the rule's columns, computes the floor per kept column (the 5 % quantile over the exported participants), stops on a non-positive floor, applies `log2(Xk + floor)` and then, under `standardize_by_run`, the per-run standardization. It then counts the non-finite cells, the shape (`_shape_counts`), the spectrum (`_spectrum`, with the numerical rank) and the run offset (`_phase_offset`) of the transformed block, and writes the feature table with `_FEATURE_COLUMNS` (`floor`, `floor_over_median`, `skew_transformed`, `max_abs_z_transformed`, `phase_d` among them). The manifest records `settings.units` as the rule's transform; a variant's manifest carries the primary as `reference` with its manifest hash, its output hashes and its `phase_offset`.
- **Every variant-specific word comes from the rule set.** `EXPORT_VARIANT_RULE_SETS` gives the rules, the change, the citation word, the dependence label, the source, the heading and the reader; `_variant_words` adds, from the variant's block and hook, what the variant changes (`changes`), what it keeps (`kept`, the blocks other than its own), `does` and `whose`. `_BLOCK_TEXT` names one platform. The findings, the status line, the comparison, the diagnostics' paragraph and the `phase` line read these words.
- **Rule numbers are cited by role.** `_export_variant_findings` and `_export_variant_status_line` cite the variant's rules 2 and 6 (a status that differs), 3 (a rank that differs) and 1; `_statistic_reading_line` rule 6; `render_axis_diagnostics` rule 7. Each rule set keeps those roles at the same numbers.
- **The report iterates its pin.** `REPORT_EXPORT_VARIANTS` holds the three current variants; `REPORT_INPUT_FILES` is built from it; `run_report` prints one line per registered variant outside it. Its identity gate compares a pinned variant's recorded `variant` block with the registry on `block`, `hook`, `rule`, `setting` and `change`.
- **The diagnostic's expected counts** on a variant are the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS` (165 NMR features) unless the variant's entry holds `diagnostics`.
- **Pinned numerics.** Every output committed since `adni-portable-numerics` reproduces byte for byte on a data machine; nixos-home is one (the spike ran there on 2026-11-02 and every input matched its manifest). The primary export manifest predates the numerics, so its SVD-based floats are copied into references, never recomputed.
- **MOTCO 0.10.0 on a rank-deficient block is untested here.** On the raw scale the NMR block has numerical rank 104 of 165 and the joint matrix 237 of 298. MOTCO z-scores every feature and fits PLS-DA on the joint matrix; no column is constant.

## Goals / Non-Goals

**Goals:**
- Register `raw_scale`, `log2_plus_one` and `glog` and run each through the existing step, with the committed bytes of the three registered variants kept.
- One hook, `scale`, acting on both blocks, with the scale and its offsets stated once as constants.
- The report untouched: the same 106 inputs, the same body, the 2026-11-02 report still checking.

**Non-Goals:**
- Report sections, rules or gates for the scale group (the follow-up report change).
- A general multi-block framework beyond block `all`: the scale variants are the only ones that change both blocks.
- Any treatment of the collinear NMR block on the raw scale beyond recording its numerical rank.
- Any change to the outputs of the primary, the latent arm, the three registered variants, the CN / LMCI / AD arm or the rank sweep.

## Decisions

### D1. Three registry entries with block `all` and hook `scale`
`raw_scale`, `log2_plus_one` and `glog` join `EXPORT_VARIANTS` after `nmr_all_columns`, each with block `all`, hook `scale`, rule `SCALE_VARIANT_RULE`, `reads_data_root` `False` and the proposal's setting. `export-sensitivity --variant <name>` runs each end to end: export, analysis, comparison.
- **Why `all`:** the hook acts on every block. With `spec["block"]` equal to `all`, the existing expression that lists the unchanged files yields `metadata.csv` and `covariates.csv` alone, which is the right contract, and the report's identity gate compares the string as it compares `p180` or `nmr`. The hook's own branches test `spec["hook"] == "scale"`, never the block.
- **The three existing entries are not touched.** No key is added, so their committed `variant` blocks still equal the registry.
- **`--variant all`** now runs six variants and stops at the existing-variant gate when any variant's outputs exist, unless `--force`. The real runs use `--variant <name>`, and the docs say so.
- **Rejected:** a tuple of blocks in the entry (the recorded `variant` block is compared field by field and `_BLOCK_TEXT[spec["block"]]` assumes one name); one entry per block and scale (six entries for three decisions; a scale is one decision on both blocks); a new step (the pairing with the primary and the comparison already live in `export-sensitivity`).

### D2. `SCALE_VARIANT_RULE` and the `scale` hook
A constant keyed by variant: the transform as an expression, the offset (`None`, `1`, or `"lambda"`) and, for `glog`, `lambda_divisor` 10 and the rule of λ in words. The hook, per block, after the rule's floor:
- **The rule's floor is computed, gated and recorded, not applied.** `floors_not_positive` keeps its meaning (the rule's check, 0 / 0 on the committed inputs), `floor` and `floor_over_median` in the feature table stay the rule's, and the feature tables of the primary and of a scale variant describe the same metabolites with the same columns.
- **The transform replaces `log2(Xk + floor)`:** `Xk` for `raw_scale`; `log2(Xk + 1)` for `log2_plus_one`; `log2((Xk + sqrt(Xk² + λ²)) / 2)` for `glog`, with λ per column the smallest positive value over the exported participants divided by `lambda_divisor`. A column with no positive cell leaves λ undefined and raises before anything is written, naming the block and the count of such columns. The non-finite gate runs as it does for every export.
- **The feature table gains an `offset` column** under the hook, after `phase_d`: empty for `raw_scale`, 1 for `log2_plus_one`, λ for `glog`. `_FEATURE_COLUMNS` is unchanged, so the primary's and the other variants' tables keep their bytes. `skew_transformed`, `max_abs_z_transformed` and `phase_d` are on the variant's scale, as for every export.
- **The manifest records** `settings.units` as the variant's transform (so every reader that prints the units prints the variant's), `settings.scale` as the constant name and the variant's entry, `counts.scale` (the transform and, for `log2_plus_one`, `median_below_offset` per block; for `glog`, the quantiles of λ over the median per block), and copies the primary's `counts.shape` into `reference.shape`, as `reference.phase_offset` is copied. The numerical rank is already under `counts.spectrum.<block>`.
- **Rejected:** writing the offset into the `floor` column (it would change a column's meaning by hook, and `raw_scale` has none); skipping the rule's floor under the hook (its cost is nil and it keeps the tables comparable); a per-block λ or the rule's floor as λ (the user chose the per-metabolite smallest positive value over 10 on 2026-11-02, before the spike measured it).

### D3. One shared rule set, with the roles at the same numbers
`EXPORT_VARIANT_RULE_SETS` gains one entry shared by the three variants:

| key | value |
|---|---|
| `rules` | `"SCALE_VARIANT_READING_RULES"` |
| `change` | `"adni-scale-variants"` |
| `cite` | `"scale rule"` |
| `dependence` | `"scale dependence"` |
| `source` | `"the scale of both blocks"` |
| `heading` | `"Reading rules of the scale variants"` |
| `reader` | `"a scale variant"` |

- **Roles:** rules 1, 2, 3, 6 and 7 have the roles of `EXPORT_VARIANT_READING_RULES` 1, 2, 3, 6 and 7, so the fixed citations in the code stay correct; rules 4 and 5 describe the scales (the two log variants, then the raw scale) and rule 8 reads the variant against the primary only.
- **`_variant_words` for hook `scale`:** `changes` "the scale of both blocks", `does` "changes the scale of both blocks", `whose` "scale", `kept` "the membership of both blocks". `kept` is reworded because the generic expression (the blocks other than the variant's) is empty for block `all`, and the sentence that prints it ("the participants, …, the metadata and the covariates are the primary's") must stay true.
- **Why one shared set:** the user's choice (2026-11-02); the three variants differ in one setting of one kind, as the p180 pair does, and the later report change groups them under one rule set.

### D4. Text by hook
- **`_export_variant_lines`,** for hook `scale`: the transform and the offset rule; the offset summary (for `log2_plus_one` the metabolites with a median below 1 per block; for `glog` the quantiles of λ over the median per block; nothing for `raw_scale`); per block the shape counts (|skew| > 1, largest |z| > 8) and the numerical rank of the primary export, then of the variant, every value read from the variant export manifest (`reference.shape`, `counts.shape`, `counts.spectrum`); then the run offset lines as for every variant.
- **`_export_variant_phase_line`,** for hook `scale`: "the variant changes the scale of both blocks only (scale rule 2) and `phase` carries the run difference, as in the primary".
- **The feature-rule line of `render_analysis_summary`** adds, when the export manifest carries `settings.scale`, that the rule's scale is replaced by the variant's (`SCALE_VARIANT_RULE`), beside the units it already prints.
- **`render_axis_diagnostics`** is unchanged: its paragraph already prints "an export whose scale differs" from `whose`.
- **The three registered variants take no new branch.** Every committed `summary.md`, `export_sensitivity.md` and `diagnostics.md`, re-rendered from its records, must equal the committed file (D7).

### D5. Predeclared counts per variant
`EXPORT_VARIANT_EXPECTED_COUNTS` gains the three entries of the proposal's table: every key of `EXPORT_EXPECTED_COUNTS` with `phase_offset` replaced, `shape` per block (|skew| > 1, largest |z| > 8), `spectrum` per block (`numerical_rank`), for `log2_plus_one` `scale.median_below_offset` per block, `runs_differing_from_phase` 0, `unchanged_equal_primary` for `metadata.csv` and `covariates.csv`, and `analysis` equal to `ANALYSIS_EXPECTED_COUNTS`. No `diagnostics` key: the rank-independent keys hold.
- `_project` already projects the observed counts onto nested partial expectations (as `phase_offset` holds two of the six keys), so `spectrum.<block>.numerical_rank` needs no code.

### D6. The report is untouched
`REPORT_EXPORT_VARIANTS` and `REPORT_INPUT_FILES` are unchanged. After the registration, `run_report` prints three uncovered-variant lines, reads 106 files and writes the same body. The gate: `report --check` on `reports/motco-adni-2026-11-02.md` passes with no mismatch, and a render to a scratch file of the same name is byte-identical. The later report change extends the pin, decides the scale group's table-title prefix and re-issues the report.

### D7. Gates that keep the other outputs' bytes
- **Re-render from committed records (any clone):** `render_analysis_summary` on the 12 committed `summary.md` (the primary, the latent arm, the three variants, the CN / LMCI / AD arm, the six ranks), `render_export_sensitivity` on the 3 committed `export_sensitivity.md`, `render_axis_diagnostics` on the 7 committed `diagnostics.md` (the primary, the arm, the three variants, the CN / LMCI / AD arm, rank 12). Byte-identical, every one.
- **Pinned primary export (data machine):** `export --out-dir <scratch>` writes the six output hashes the committed export manifest records.
- **Pinned registered variants (data machine), in place:** `export-sensitivity --variant <name> --force` for `nist_bridge`, `per_run_standardized` and `nmr_all_columns`, pinned at `n_jobs = 1`, each with its `diagnostics/` moved aside. Pass: no tracked CSV, `summary.md`, `export_sensitivity.md` or `nist_bridge.csv` changes; every gitignored CSV hashes to its committed manifest's record; the manifests and `result.json` differ only in time, revision, runtime, the machine fields of `numerics` and the hashes of the files that carry them. Restore the tracked manifests and `result.json` with `git restore` and move the diagnostics back. Why in place: `export_sensitivity.md` names its own directory.

A failed gate stops the apply until the cause is found. No committed output is regenerated to make a gate pass.

### D8. Verification on the data machine, in the scratchpad
- Per variant, a scratch `_run_export(..., variant=<name>, staging=<scratch>)` on the committed inputs: every predeclared count with no deviation; `metadata.csv` and `covariates.csv` equal to the primary's; both blocks' columns the primary's in order; the feature tables with the rule's floors (equal to the primary's feature tables) and the `offset` column; the cells against an independent computation from the cleaned tables (`x`, `log2(x + 1)`, the glog with λ from the smallest positive value); the zero cells at 0, 0 and `log2(λ / 2)`; `settings.units` and `reference.shape`.
- Permuted sex and stage in a scratch copy of `cohort.csv` (its manifest hash updated in the scratch copy): `p180.csv` and `nmr.csv` byte-identical.
- The λ gate: a scratch copy of the cleaned NMR table with one kept column set to zero, its clean manifest's output hash and the scratch cohort manifest's recorded clean hash updated: `glog` stops naming the block and one metabolite, writes nothing.
- **MOTCO on the raw scale, before the gates that cost the most:** a scratch analysis of the scratch `raw_scale` export at the primary's settings, `n_jobs` free, into the scratchpad. It must complete with a CV-selected rank and the three statistics. It is not reported (its `n_jobs` finding) and is discarded. If MOTCO stops on the block, the apply stops and the proposal is revised (D10).
- Synthetic records, in memory, from the committed `nmr_all_columns` records with the variant block of each scale entry and a scale export manifest: the wording of `summary.md`, `export_sensitivity.md` (a p-value edited so that `delta` is rejected; a rank edited) and `diagnostics.md`, and the eight rules string-equal to the constant.

### D9. Order and machines
No change is pending, so the apply starts when the proposal is accepted. Groups that read only committed files run on any clone; the hook, the gates and the real runs on a data machine (nixos-home). The real runs: per variant `export-sensitivity --variant <name>` pinned at `n_jobs = 1`, then its `axis-diagnostics`, then a `--force` rerun for reproducibility; the committed outputs are the second run's. Nine CV analyses in all (three gates, three runs, three reruns); the gate reruns and the real runs can go in the background, one at a time to keep `n_jobs = 1` meaningful.

### D10. The rank-deficient block is not worked around
If `analyze_trajectories` stops on the raw-scale NMR block, the step stops with MOTCO's message and nothing is written, as the latent arm's rare-level condition is not worked around. The variant's scale is never changed to make it run; the proposal is revised (the variant withdrawn or MOTCO's behaviour reported upstream), by the user.

## Risks / Trade-offs

- **[MOTCO on a block of numerical rank 104]** → The feasibility run of D8 comes before the costly gates; D10 if it stops.
- **[The raw scale's right tails and the glog's left tails carry leverage under z-scoring; the glog puts 41 NMR zero cells 4.3 bits below their metabolite's smallest value]** → Stated in scale rules 4 and 5, with the shape counts predeclared and reported beside the results. The scales are the user's decisions, never changed from a result.
- **[The `floor` column on a scale variant is not the offset applied]** → D2: it stays the rule's floor, documented as recorded and not applied; the `offset` column holds the variant's.
- **[Branching the text changes a registered variant's bytes]** → The gates of D7 compare every committed text and CSV of theirs, and a difference stops the apply.
- **[Compute]** → Nine CV analyses at 9999 permutations on one data machine. Accepted: the in-place gate is the project's standard for shared code, and the reruns are its reproducibility check.
- **[`--variant all` stops on the existing variants]** → Documented; the real runs name their variant.
- **[Three registered variants outside the report pin]** → By design (D6): three progress lines, and the later report change.
- **[The primary export manifest's floats are unpinned]** → `reference.shape` and `reference.phase_offset` are copied from it, never recomputed; the comparison prints recorded values only.

## Migration Plan

Nothing is migrated. The three directories are added under `results/motco_export_sensitivity/`; the registered variants' outputs stay. Rollback is reverting the branch: the new directories are then unregistered variants', which no step or report reads.
