# Design

## Context

See `proposal.md` for the motivation, the variant, its rules and its counts, `spike.md` for every number, and the specs for the requirements. This is the state that shapes the approach.

- **`export-sensitivity` was built for p180 variants** (change `adni-nist-bridge`):
  - `_run_export` takes one of two hooks, `factors` or `standardize_by_run`, and each acts on `spec["block"]`, which is `p180` for both entries.
  - The unchanged-files check is already generic: it compares the CSVs of every block other than `spec["block"]`, plus `metadata.csv` and `covariates.csv`.
  - The variant text is not generic. It says "p180" in fixed strings:
    - `_export_variant_lines` ("the NMR block … are the primary's");
    - the `phase` line of `render_analysis_summary` ("the variant changes the p180 values only (variant rule 2)");
    - the variant clauses of `_statistic_reading_line`;
    - `_export_variant_findings`, `_export_variant_status_line` and `_EXPORT_SENSITIVITY_STATUS_DIFFERS` ("dependence on the handling of the p180 run", "run-handling dependence");
    - `_export_variant_rules_heading` (it names `EXPORT_VARIANT_READING_RULES` and the first entry's change);
    - the opening paragraph of `render_axis_diagnostics` ("an export whose p180 …").
- **The membership rule.** `_feature_family` maps a cleaned column to its derived family by name mark, and `_run_export` keeps the columns with no family. The floors are column-wise 5 % quantiles of the kept columns, and the counts record `features.<block>` as `cleaned`, `kept` and `derived` per family (the excluded columns).
- **The report reads the registry directly.** `REPORT_INPUT_FILES` is built from `EXPORT_VARIANTS` when the module loads, and the report's loader, gates and sections loop over it. Its identity gate requires each variant manifest's `variant` block to equal the registry entry. Its earlier-layout gate (`_check_report_layout`) compares level-2 headings only.
- **The diagnostics' expected counts** on a variant are the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS`, which fix NMR at 165 features.
- **The primary export manifest is from 2026-10-27, before `adni-portable-numerics`.** Its SVD-based floats (spectrum, PC correlations) differ from a pinned recomputation by about 1e-15 (spike: 1.8e-15 at most). Its files reproduce byte for byte.
- **Pinned numerics.** Every output committed since `adni-portable-numerics` reproduces byte for byte on a data machine, so committed hashes are gates.

## Goals / Non-Goals

**Goals:**
- Register `nmr_all_columns` and run it through the existing step, with the two p180 variants' committed bytes kept.
- A variant's reading rules, citation word and dependence label stated once, as constants, and used by every renderer.
- The committed report stays checkable while a registered variant is not in it yet.

**Non-Goals:**
- Report sections, rules or gates for the new variant (the follow-up report change).
- Any change to the primary's, the latent arm's, the CN / LMCI / AD arm's or the rank sweep's outputs.
- A general variant framework for the three scale variants. They need a `scale` hook and their own rule set, which their change adds. The mapping of D3 is the only part built for them.

## Decisions

### D1. A third registry entry run by the existing step
`nmr_all_columns` joins `EXPORT_VARIANTS` with block `nmr`, hook `membership`, `rule` `None` and `reads_data_root` `False`. `export-sensitivity --variant nmr_all_columns` runs it end to end: export, analysis, comparison.
- **Why:** the step already pairs a variant export with the primary's settings, records the primary as reference and writes the comparison from the two records (design D1 of `adni-nist-bridge`). Its registry was built for later variants to join.
- **The existing entries are not touched.** No key is added to `nist_bridge` or `per_run_standardized`. Their committed export manifests record the entry as their `variant` block, and the report's identity gate compares the two.
- **`--variant all`** now runs three variants. With the p180 variants' outputs present it stops at the existing-variant gate unless `--force`. The real run uses `--variant nmr_all_columns`, and the docs say so.
- **Rejected:** a new step or an `export --membership` flag. Either would duplicate the pairing and the comparison the step already owns.

### D2. The `membership` hook
Under `membership`, the variant's block keeps every cleaned column. The rest of `_run_export` runs unchanged.
- **Membership:** the family of each column is still computed and recorded, but no column is excluded.
  - The counts record `derived` (excluded) as 0 per family, and a new `derived_kept` per family (72 / 4 / 1 / 3). `kept + Σ derived = cleaned` still holds.
  - `derived_kept` exists only under the hook, so the primary's and the p180 variants' counts are unchanged.
  - In `features_nmr.csv`, every row is status `kept` with its family, and the transformed-scale columns are filled for all 245.
- **Floors:** the 5 % quantile is column-wise over the exported participants. The 165 concentrations therefore get the primary's floors bitwise, which the spike confirmed, and each derived column gets its own.
- **The rule's columns against the primary's:** after the scale, the kept-by-rule columns are compared with the primary `nmr.csv`, column names and cells.
  - The primary file is parsed with `float_precision="round_trip"`, since the export writes each float as its shortest repr.
  - The step already checks that file against its manifest (`_check_primary_export_chain`), so this reads nothing new.
  - The result is recorded as `counts.rule_columns_equal_primary`, and a difference is a finding.
- **No bridge and no data root:** `_run_export_variant` takes the bridge path only for hook `factors`. `p180_runs.csv` is still read, as for every variant, for the run count and the run-differs-from-`phase` finding.
- **Rejected:**
  - A second rule constant (an "`EXPORT_FEATURE_RULE` with no derived marks"). The variant's setting is one sentence, and the rule's scale is unchanged.
  - Putting the derived columns after the concentrations. Cleaned order is the export's order, and it keeps the variant's `block_columns` a superset of the primary's in the same relative order.

### D3. `EXPORT_VARIANT_RULE_SETS`: each variant's rules, citation and label
A convention in `constants.py`, keyed by variant, with an import-time assertion that its keys are `EXPORT_VARIANTS`' in order:

| key | `nist_bridge`, `per_run_standardized` | `nmr_all_columns` |
|---|---|---|
| `rules` | `"EXPORT_VARIANT_READING_RULES"` | `"NMR_MEMBERSHIP_READING_RULES"` |
| `change` | `"adni-nist-bridge"` | `"adni-nmr-all-columns"` |
| `cite` | `"variant rule"` | `"membership rule"` |
| `dependence` | `"run-handling dependence"` | `"feature-membership dependence"` |
| `source` | `"the handling of the p180 run"` | `"the NMR feature membership"` |
| `heading` | `"Reading rules of the export variants"` | `"Reading rules of the NMR membership variant"` |

A second assertion checks that each `rules` names a module-level tuple.
- **The renderers take every variant-specific word from the entry:** `_statistic_reading_line`, `render_analysis_summary`, `_export_variant_rules_heading`, `_export_variant_findings`, `_export_variant_status_line`, the status label of `render_export_sensitivity` and `render_axis_diagnostics`.
- **Rule numbers stay fixed.** The two rule sets share the roles of rules 1, 2, 3, 6 and 7 (proposal), so a sentence that cites "rule 6" stays correct under both. Only `cite` and `source` change.
- **Why a mapping, not keys on the registry entries:** keys added to the p180 entries would make their committed `variant` blocks differ from the registry, which fails the report's identity gate until both variants are rerun.
- **Why not one rewritten `EXPORT_VARIANT_READING_RULES`:** it is a decided constant whose results exist. Rewriting it would change the p180 variants' committed `summary.md`, `export_sensitivity.md` and `diagnostics.md`.
- **Why not the current rules plus an addendum:** its rule 2 says the variant "differs only in the p180 values".

### D4. Text by block
Where a sentence names the block a variant changes or keeps, it is written from `spec["block"]`, and the p180 sentence stays the one the p180 entries produce today.
- **`_export_variant_lines`:**
  - the unchanged parts are listed from the blocks other than the variant's;
  - for hook `membership`, it adds the rule's columns equal to the primary's (the recorded value), the block shares and joint features, and the variant block's shape counts (`|skew| > 1`, largest `|z|` > 8), all read from the variant export manifest;
  - for hook `factors`, the bridge lines are as today.
- **The `phase` line of `render_analysis_summary`:** for `nmr_all_columns`, "the variant changes the NMR membership only (membership rule 2) and `phase` carries the run difference, as in the primary".
- **`render_axis_diagnostics`:** the opening paragraph names the block the variant changes, and the flagged-row bullet cites the variant's rule 7.
- **The report is not changed by this decision.** It covers the p180 variants only (D6), so "each changes the p180 values only" stays true for every variant it quotes.

### D5. A variant's own diagnostics counts
`run_axis_diagnostics`, on a variant read, uses `EXPORT_VARIANT_EXPECTED_COUNTS[<variant>]["diagnostics"]` when the entry has the key, and the rank-independent keys of `DIAGNOSTICS_EXPECTED_COUNTS` otherwise. Only `nmr_all_columns` has the key: the rank-independent keys with `blocks.nmr.features` 245. The p180 variants' diagnostics manifests are unchanged.
- **Rejected:** projecting the block features out of the expectation for every variant. That would also change what the p180 variants' diagnostics expect, and so their committed manifests' `expected` blocks.

### D6. `REPORT_EXPORT_VARIANTS`: the report's pin
A convention tuple, `("nist_bridge", "per_run_standardized")`, with an import-time assertion that it is a subsequence of `EXPORT_VARIANTS` in registry order.
- **What uses it:** `REPORT_INPUT_FILES` is built from it, and every loop of the report over variants (`_load_report_inputs`, its gates and chain, `_export_sensitivity_section`, the summary, findings, reading-rules and reproduction sections of `render_report`) iterates it instead of `EXPORT_VARIANTS`.
- **Uncovered variants:** `run_report` prints one progress line per registered variant outside the pin, naming it and saying a report change adds it. Nothing about it enters the body, so the body depends on the same inputs as before.
- **Why (the user's choice B, 2026-10-30):**
  - Without the pin, registering the variant makes `report` require 13 files that don't exist yet (its export manifest, 3 analysis files, 3 comparison files, 6 diagnostics files; 106 inputs in all). Once they exist, the newest report fails `--check` cell by cell rather than as an earlier layout, because the variant adds no level-2 section.
  - With the pin, the newest report stays valid until the report change re-issues it.
- **Why a constant and not a filter** such as "variants of change `adni-nist-bridge`": it states the report's coverage. The report change's earlier-layout gate can compare a report's listed variants with it. That gate is the report change's design, not this one's.
- **The gate:** after the pin, on the committed tree, `report --check` on the newest committed report passes with no mismatch. A `report --out <scratch>/<same file name>` is byte-identical to that report.

### D7. Gates that keep the other outputs' bytes
The changes of D2 to D6 touch code shared with the primary, the latent arm, the p180 variants, the CN / LMCI / AD arm and the rank sweep. Three gates run before the real run:
- **Re-render from committed records (any clone).** A scratch script calls the changed renderers on the committed records and manifests and compares the result with the committed files byte for byte:
  - `render_analysis_summary` for every committed `summary.md` (11 files: the primary, the latent arm, the two p180 variants, the CN / LMCI / AD arm and the six ranks);
  - `render_export_sensitivity` for the two `export_sensitivity.md`;
  - `render_axis_diagnostics` for the six committed `diagnostics.md`, from their committed tables and manifests.

  It is the byte gate of design D6 of `adni-report-rank-sweep`, widened to every reader of `_statistic_reading_line`.
- **Pinned primary export (data machine).** `export --out-dir <scratch>` writes the six output hashes the committed export manifest records.
- **Pinned p180 variants (data machine), in place.** `export-sensitivity --variant nist_bridge --force` and `--variant per_run_standardized --force` run on the default output root, with each variant's `diagnostics/` moved to the scratchpad first so no stale-diagnostics finding enters the rerun.
  - **Why in place:** `export_sensitivity.md` names the variant's own directory, so a scratch output root cannot reproduce its bytes.
  - **Pass condition:** every tracked CSV, `summary.md`, `export_sensitivity.md` and `nist_bridge.csv` is unchanged (`git status`). Every gitignored CSV hashes to its committed manifest's record. The manifests and `result.json` differ only in time, revision, runtime and the hashes of the files that carry them.
  - **Restore:** the tracked manifests and `result.json` are restored from git and the diagnostics moved back, so the committed outputs stay the committed ones.
  - The archive symlinks exist on nixos-office.

A failed gate stops the apply until the cause is found. No committed output is regenerated to make a gate pass.

### D8. Order of the work
The apply starts only after `adni-report-rank-sweep` has written and committed its report, been archived and been merged. This branch is then rebased onto `main`. Two things depend on that:
- the report gate of D6 needs that report;
- this change's `case-study-report` delta modifies "Inputs are the kept aggregate outputs only" as that change leaves it (93 inputs, the rank sweep's scenarios).

The proposal's artifacts and the spike script are the only files on the branch before the rebase.

## Risks / Trade-offs

- **[The derived percentages carry left tails that MOTCO's z-scoring gives leverage]** → They are stated in membership rule 4, and the shape counts are predeclared and reported beside the results. The scale is the rule's by decision, never changed from a result. Another scale for them is out of scope.
- **[The 80 columns are near-linear functions of the 165 (median R² 0.998)]** → The block stays of full numerical rank (245), and MOTCO's PLS-DA fits a collinear block. The CV may select another rank, which is reported, not ranked (membership rule 3).
- **[Branching the text changes a p180 variant's bytes]** → The gates of D7 compare every committed text and CSV of theirs, and a difference stops the apply.
- **[The pin hides a registered variant from a report written in between]** → `run_report` names the variant on a progress line, the spec requirement names the change that must extend the pin, and the report change follows this one.
- **[The layout gate does not see variant lists]** → A report re-issued by the report change will make the newest report fail `--check` cell by cell, not as an earlier layout. The report change owns that gate. Here, the newest report keeps its body.
- **[The primary export manifest's floats are unpinned]** → The variant manifest copies the primary's recorded run offset into `reference.phase_offset`, as the p180 variants do, and never recomputes it. The comparison text prints recorded values only.
- **[`--variant all` stops on the existing variants]** → This is documented, and the real run names its variant.

## Migration Plan

Nothing is migrated. The p180 variants' outputs stay, and the new variant's directory is added. Rollback is reverting the branch: the new directory is then an unregistered variant's, which no step or report reads.
