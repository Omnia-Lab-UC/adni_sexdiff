# Proposal

## Why

The three predeclared scale variants (change `adni-scale-variants`, merged in PR #18) have been run pinned and committed, each with its own axis diagnostics:
- `raw_scale` (both blocks on the concentration scale): CV rank 7;
- `log2_plus_one` (both blocks on `log2(x + 1)`): CV rank 8;
- `glog` (both blocks on the generalized log): CV rank 7.

All nine statuses are `same`, against the primary's rank 8 and its three non-rejections.

No report quotes them yet. `adni-scale-variants` registered them outside the report's pin (`REPORT_EXPORT_VARIANTS` holds `nist_bridge`, `per_run_standardized` and `nmr_all_columns`), so the newest report, `reports/motco-adni-2026-11-02.md`, stays valid. `SCALE_VARIANT_READING_RULES` binds "every report that quotes" a scale variant, and that change left the report to a later change that pins the three and re-issues the report. This is that change. It is the last predeclared sensitivity, so after it the report covers every one that has run.

A read-only spike for this proposal ran the report on the committed tree (bf3f773) from a scratch copy of `src/` with the pin extended to the six variants:
- **Unchanged parts.** The loader, gates, chain and earlier-layout gate need no change. The grouping of `adni-report-nmr-all-columns` already puts the three in one group under their shared rule set.
- **Three defects in the rendering:**
  - The scale group's lead does not cite scale rule 8 ("read against the primary only, never against another scale variant").
  - The summary joins three ranks with "and … and" ("7 (`raw_scale`) and 8 (`log2_plus_one`) and 7 (`glog`)").
  - The preamble does not name this change.
- **Against the 2026-11-02 report.** Only five of its non-table lines differ: the title, the preamble, the summary's diagnostics paragraph, the export section's lead and the lead of the CLI equivalents. Four provenance tables gain rows. Every other table and line is unchanged.

## What Changes

- **The pin.** `REPORT_EXPORT_VARIANTS` becomes all six registered variants in registry order: `nist_bridge`, `per_run_standardized`, `nmr_all_columns`, `raw_scale`, `log2_plus_one` and `glog`. No registered variant is left outside it, and no progress line names one.
- **Inputs, gates and chain extended, with no code change beyond the pin.** The spike checked this on the committed tree.
  - **Inputs.** 39 more files, 145 in all (106 now), 45 of them manifests (33 now). Per scale variant, under `results/motco_export_sensitivity/<variant>/`, the step reads 13 files:
    - `motco_input/manifest.json`;
    - the analysis' `result.json`, `analysis_manifest.json` and `summary.md`;
    - the comparison's three files;
    - the diagnostics' six files.

    No participant-level file is opened or required. The variants' export CSVs, `latent_scores.csv` and `analysis_metadata.csv`, and their `stage_means.csv` and `pls_loadings.csv`, are quoted by the hashes their manifests record.
  - **Hashes.** 27 more aggregate files are checked against their own manifests, 99 in all.
  - **Identity.** The existing variant gate loops over the pin. It checks each variant's manifests name it, its `variant` block equals its `EXPORT_VARIANTS` entry, it records no latent adjustment, and its diagnostics record `is_primary` false and its name.
  - **Reported runs.** The three record `n_jobs` 1. All 45 manifests record MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8. Numerics are pinned in 40 manifests and absent in the same five as before.
  - **Chain.** 66 more links, 255 in all: per variant 4 for the export, 8 for the analysis, 6 for the comparison and 4 for the diagnostics. All hold.
- **"Export sensitivity" gains the scale group, one group of shared tables** (the user's choice for this proposal). It is the third group by rule set, after the run-handling and the membership groups, with `raw_scale`, `log2_plus_one` and `glog` under `SCALE_VARIANT_READING_RULES`.
  - **Tables.** Each holds the primary and the three scale variants, the primary row first and its status the result, as the rank section holds every forced rank.
  - **Titles.** They carry the group's variant names as their prefix, the rule `adni-report-nmr-all-columns` set for a later group (the user's choice for this proposal):
    - `raw_scale, log2_plus_one, glog: Statistics: primary and variants`;
    - `…: Latent space: primary and variants`;
    - `…: Run offset per export`;
    - `…: Exports against the predeclared counts`;
    - `…: First component against phase`.

    The per-variant headings keep their form: ``Status per statistic: `<v>` ``, ``Export variant `<v>` ``, and `<v>: Flagged latent components` and the rest of the diagnostics.
  - **Group lead.** It cites scale rule 8: each variant is read against the primary only, never against another variant of the group. `_GROUP_PRIMARY_ONLY_RULE` maps `SCALE_VARIANT_READING_RULES` to 8, and a group of several variants gets the plural clause. The membership group's clause stays byte for byte.
  - **Lines.** Each variant's `angle` paragraph, status bullets (`_export_variant_status_line`) and "Export variant" block (`_export_variant_lines`: the transform and its offset, the floors recorded and not applied, the offset summary, each block's shape counts and numerical rank of both exports, the run offsets) are the shared renderers' lines. They are string-equal to the variant's `export_sensitivity.md`.
  - **Counts table.** It takes the keys of the three `EXPORT_VARIANT_EXPECTED_COUNTS` entries in registry order, without `analysis` and `phase_offset`. A key one variant lacks (`scale.median_below_offset.*`, `log2_plus_one` only) prints `n/a` for the others.
- **Other sections**, from the same inputs:
  - **Preamble:** names this change. The scale group's clause (`SCALE_VARIANT_READING_RULES`) already comes from the groups.
  - **Summary:** a paragraph for the scale group with its three rank lines and status bullets. The ranks are joined as a list ("7 (`raw_scale`), 8 (`log2_plus_one`) and 7 (`glog`)"), which leaves the two-variant text byte-unchanged. The diagnostics paragraph adds the three variants' flagged components.
  - **Provenance:** extended by iteration.
  - **Findings:** the twelve new manifests copied verbatim. That is the rank finding of `raw_scale` and of `glog` under their analysis and comparison manifests, and each variant's flagged-component findings and not-the-primary note under its diagnostics.
  - **Reading rules:** a seventh list, `SCALE_VARIANT_READING_RULES`, after `NMR_MEMBERSHIP_READING_RULES`, led by the line the variants' documents print.
  - **Reproduction:** the three `axis-diagnostics` commands and three `cli_equivalent`s, 15 analyses in all.
- **The earlier-layout gate needs no change.** The 2026-11-02 report lists three variants, so `--check` stops on it at the variant gate (absent: `raw_scale`, `log2_plus_one`, `glog`), naming 28e0d48, where it checks. The four older reports stop as now.
- **Constants:** a convention only. `REPORT_EXPORT_VARIANTS` gains the three, and `REPORT_INPUT_FILES` follows from it. `REPORT_SECTIONS` is unchanged (thirteen sections).
- **Docs:**
  - `README.md`: the status sentence that says a later report change adds the scale variants, and the `report` section (145 inputs, 45 manifests, 255 links, seven rule lists, the 2026-11-02 report as an earlier layout).
  - `AGENTS.md`: the status paragraph, step 6, the earlier-layout list (2026-11-02, 28e0d48) and the Layout entries.
  - The `constants.py`, `render_report`, `_export_sensitivity_section` and `_check_report_layout` docstrings.
  - "Flag and ask" is unchanged.
- **The next report**, `reports/motco-adni-<date>.md`, follows the user's rule for the previous reports. It is written on 2026-11-03 or later, named by the day it is written, and never over the 2026-11-02 file. It is written on the clean tree from the committed outputs, checked with `--check` and committed alone.

Scientific constants introduced by this change: none. The report decides nothing. It quotes `EXPORT_VARIANTS`, `SCALE_VARIANT_RULE`, `SCALE_VARIANT_READING_RULES`, `EXPORT_VARIANT_EXPECTED_COUNTS` and the earlier constants by name, and every number from the records and manifests.

Out of scope, each its own change if wanted:
- Any reading of one scale variant against another, or of a scale variant against another export variant, the latent arm, the CN / LMCI / AD arm or the rank sweep (scale rule 8), and any crossing of sensitivities. A table that lists the three, each beside the primary, compares none, as the rank sweep's tables do.
- The variants' per-statistic reading lines, which their `export_sensitivity.md` and `summary.md` print. The report prints the status lines, as for every other sensitivity.
- One sub-group of tables per scale variant (an alternative the user declined), a rule-set prefix for the titles, or retitling the run-handling and membership groups' tables.
- Any change to the latent-adjustment, stage-definition or rank sections.
- A same-day report name, a rewrite of an earlier report, or a check of one with the new code.
- Any change to the outputs of `clean`, `cohort`, `export`, `analyze`, `axis-diagnostics` or the four sensitivity steps.
- Figures, HTML or PDF rendering, and a written discussion.
- The cluster run (constraint 7).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `case-study-report`: these requirements change:
  - the inputs (the scale variants' files; 145);
  - the content contract (the scale group in the export-sensitivity section);
  - every number pasted (the scale group's values);
  - the interpretive sentences (the scale status lines, and no reading of a scale variant against another or against another sensitivity);
  - the reading rules carried (a seventh list);
  - the findings (the scale variants' carried);
  - the pin (`REPORT_EXPORT_VARIANTS` covers all six variants);
  - the variant gate (the 2026-11-02 report as an earlier layout).

  `motco-export-sensitivity` ("every report that quotes it" in its scale reading rules) is fulfilled without changing its text.

## Impact

- `src/adni_sexdiff/constants.py`: `REPORT_EXPORT_VARIANTS` gains `raw_scale`, `log2_plus_one` and `glog`, and the comments on the report constants and the docstring name this change. No scientific constant is added.
- `src/adni_sexdiff/data.py`:
  - `_GROUP_PRIMARY_ONLY_RULE`: the scale rule set's rule 8;
  - `_export_sensitivity_section`: the plural primary-only clause of a group of several variants, and the docstring;
  - `render_report`: the preamble's change list, the summary's rank list, and the docstring;
  - `run_report`, `check_report` and `_check_report_layout` docstrings.

  The loader, gates, chain, `_check_report_layout`'s logic, `_export_variant_status_line`, `_export_variant_lines` and `_export_variant_rules_heading` are unchanged. No step's output changes.
- `src/adni_sexdiff/cli.py`: none. `report` keeps its twelve flags.
- `reports/motco-adni-<date>.md`: added and committed. It is aggregate. The five earlier reports are unchanged.
- `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged, since no participant-level output is added.
- No new dependencies. The step takes seconds, makes no MOTCO call and records no numerics.
- Machines: any machine with the Nix shell and the committed tree. No data root, data machine or participant-level file is needed.
- Workflow:
  - Implement and verify, then commit the implementation.
  - On 2026-11-03 or later, write the report on the clean tree, check it and commit it alone.
  - Archive, then open the PR and merge.

  Regenerating any input invalidates the report until a new one is written and checked.
