# Proposal

## Why

The predeclared NMR membership variant `nmr_all_columns` (change `adni-nmr-all-columns`, merged in PR #16) has been run pinned and committed:
- the CV selected rank 7 (the primary's is 8);
- `delta` differs (feature-membership dependence): p 0.0447, rejected, against the primary's 0.1116;
- `angle` and `shape` are `same`;
- it has its own axis diagnostics.

No report quotes it yet. `adni-nmr-all-columns` pinned the report to the two p180 variants (`REPORT_EXPORT_VARIANTS = ("nist_bridge", "per_run_standardized")`), so the newest report, `reports/motco-adni-2026-10-31.md`, stays valid. That change's proposal left the report to "a later change" that adds the variant to the pin and its rule set to the reading-rules section, extends `report --check`'s earlier-layout gate to the variants a report lists, and re-issues the report. `NMR_MEMBERSHIP_READING_RULES` binds "every report that quotes it". This is that change.

Pinning the variant alone is not enough. A read-only spike for this proposal ran the report from a scratch copy of `src/` with the pin extended, on the committed tree. The loader, gates and chain need no change. But several sentences the renderer writes for every variant are p180 wording, and they would be false for `nmr_all_columns`:
- "each changes the p180 values only";
- "it differs only in the p180 values (variant rule 2)";
- "read under `READING_RULES` and `EXPORT_VARIANT_READING_RULES`";
- `variant rule 3` and `variant rule 7` in place of the membership rules.

The reading-rules section would also lack the membership rules. Because the variant adds no level-2 section, the 2026-10-31 report would fail `--check` cell by cell, not as an earlier layout.

## What Changes

- **The pin.** `REPORT_EXPORT_VARIANTS` becomes `("nist_bridge", "per_run_standardized", "nmr_all_columns")`, so the report reads, checks and quotes all three registered variants. No registered variant is left outside the pin, and no progress line names one.
- **Inputs, gates and chain extended, with no code change beyond the pin.** The spike checked all of this on the committed tree.
  - **Inputs.** 13 more files, 106 in all (93 now), 33 of them manifests (29 now). Under `results/motco_export_sensitivity/nmr_all_columns/` the step reads:
    - `motco_input/manifest.json`;
    - the analysis' `result.json`, `analysis_manifest.json` and `summary.md`;
    - the comparison's three files;
    - the diagnostics' six files.

    No participant-level file is opened or required. The variant's export CSVs, `latent_scores.csv` and `analysis_metadata.csv` are quoted by the hashes its manifests record, as are its `stage_means.csv` and `pls_loadings.csv`.
  - **Hashes.** 9 more aggregate files are checked against their own manifests, 72 in all.
  - **Identity.** The existing variant gate already loops over the pin. The variant's export, analysis and comparison manifests name it, its `variant` block equals its `EXPORT_VARIANTS` entry, it records no latent adjustment, and its diagnostics record `is_primary` false and `export_variant` `nmr_all_columns`.
  - **Reported runs.** The variant records `n_jobs` 1. All 33 manifests record MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8. Numerics are pinned in 28 manifests and absent in the same five as before.
  - **Chain.** 22 more links, 189 in all: 4 for the variant export, 8 for its analysis, 6 for the comparison and 4 for its diagnostics. All hold.
- **"Export sensitivity" holds one group of tables per rule set** (the user's choice for this proposal). The variants of the pin are grouped by the rule set `EXPORT_VARIANT_RULE_SETS` names for each, in registry order:
  - the run-handling group: `nist_bridge` and `per_run_standardized` under `EXPORT_VARIANT_READING_RULES`;
  - the membership group: `nmr_all_columns` under `NMR_MEMBERSHIP_READING_RULES`.

  Each group's tables hold the primary and that group's variants only. Membership rule 8 reads the variant against the primary only, never against another export variant, so no table puts `nmr_all_columns` beside a p180 variant.
  - **Section lead.** A new lead names the groups and their rule sets.
  - **Run-handling group.** Its lead is the 2026-10-31 section lead, written for the group. Its tables and lines are the 2026-10-31 report's, titles included.
  - **Membership group.** Its own lead under `READING_RULES` and `NMR_MEMBERSHIP_READING_RULES`, then:
    - `nmr_all_columns: Statistics: primary and variant`;
    - the `angle` paragraph;
    - ``Status per statistic: `nmr_all_columns` ``;
    - `nmr_all_columns: Latent space: primary and variant`;
    - the shared-and-differs sentence (membership rule 2);
    - `nmr_all_columns: Run offset per export`;
    - `nmr_all_columns: Export against the predeclared counts`;
    - ``Export variant `nmr_all_columns` `` with the lines `_export_variant_lines` writes (membership, derived columns kept, rule columns equal to the primary's, joint features, block shares, shape counts, run offsets);
    - the variant's diagnostics (flagged rows, components with each block's loading share, block PCs);
    - `nmr_all_columns: First component against phase`;
    - its `cli_equivalent`.
  - **Wording.** Every sentence that names a variant's rule set, citation word, dependence label or changed block takes it from `_variant_words`, as the variant's own documents do. The status lines are `_export_variant_status_line` and the variant lines `_export_variant_lines`, string-equal to the variant's `export_sensitivity.md`.
- **The predeclared-counts table leaves out the `diagnostics` key.** `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]` holds it, and `axis-diagnostics` compares it, as `export-sensitivity` compares `analysis`. Without this, the spike printed 13 rows of `n/a`.
- **Other sections**, from the same inputs:
  - **Preamble:** names this change and the variant's rule set.
  - **Summary:** one paragraph per group. The run-handling paragraph is the 2026-10-31 one. The membership paragraph names the variant, its change, the block it changes, its rank, the status label and its rule set, followed by its three status lines. The diagnostics paragraph adds the variant's flagged components.
  - **Provenance:** extended by iteration.
  - **Findings:** the four new manifests copied verbatim. That is the rank finding and the `delta` finding, each under the analysis and the comparison manifest, and the diagnostics' four flagged-component findings and not-the-primary note.
  - **Reading rules:** a sixth list, `NMR_MEMBERSHIP_READING_RULES`, after `EXPORT_VARIANT_READING_RULES`, led by the line the variant's documents print.
  - **Reproduction:** the variant's `axis-diagnostics` command and its `cli_equivalent`, 12 in all.
- **The earlier-layout gate covers export variants.**
  - **The gate.** After the level-2 headings match `REPORT_SECTIONS`, `report --check` compares the variants the report lists with `REPORT_EXPORT_VARIANTS`. A report lists its variants through its level-3 headings ``Export variant `<name>` `` in "Export sensitivity", in order. A difference stops the check before any input gate. It names the report, the absent and extra variants and `git log -1 --format=%H -- <report>`, compares no cell and writes nothing.
  - **Effect on the 2026-10-31 report.** It becomes a report of an earlier layout (absent: `nmr_all_columns`). It checks at 13ce7c8, the commit that added it.
  - **Effect on the other reports.** The three older reports still stop on their sections, as now.
- **Constants:** a convention only. `REPORT_EXPORT_VARIANTS` gains `nmr_all_columns`, and `REPORT_INPUT_FILES` follows from it. `REPORT_SECTIONS` is unchanged (thirteen sections).
- **Docs:**
  - `README.md`: the status sentence that says a later report change adds the variant, and the `report` section (106 inputs, 33 manifests, 189 links, six rule lists, the variant gate).
  - `AGENTS.md`: the status paragraph, step 6, the earlier-layout list (2026-10-31, 13ce7c8) and the Layout entries.
  - The `constants.py`, `run_report`, `render_report` and `_check_report_layout` docstrings.
  - "Flag and ask" is unchanged.
- **The next report**, `reports/motco-adni-<date>.md`, follows the user's rule for the previous reports. It is written on the first date after 2026-10-31 or later, named by the day it is written, and never over the 2026-10-31 file. It is written on the clean tree from the committed outputs, checked with `--check` and committed alone.

Scientific constants introduced by this change: none. The report decides nothing. It quotes `EXPORT_VARIANTS`, `NMR_MEMBERSHIP_READING_RULES`, `EXPORT_VARIANT_EXPECTED_COUNTS` and the earlier constants by name, and every number from the records and manifests.

Out of scope, each its own change if wanted:
- Any reading of `nmr_all_columns` against a p180 variant, the latent arm, the CN / LMCI / AD arm or the rank sweep (membership rule 8), and any crossing of sensitivities.
- The variant's per-statistic reading lines, which its `export_sensitivity.md` and `summary.md` print. The report prints the status lines, as for every other sensitivity.
- The scale variants (the raw scale, `log2(x + 1)`, the generalized log): one later change, which registers them, runs them and then adds them to the pin. Choosing the prefix of a later multi-variant group's table titles belongs to that change.
- Regrouping or retitling the run-handling group's tables, or any change to the latent-adjustment, stage-definition or rank sections.
- A same-day report name, a rewrite of an earlier report, or a check of one with the new code.
- Any change to the outputs of `clean`, `cohort`, `export`, `analyze`, `axis-diagnostics` or the four sensitivity steps.
- Figures, HTML or PDF rendering, and a written discussion.
- The cluster run (constraint 7).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `case-study-report`: these requirements change:
  - the inputs (the third variant's files; 106);
  - the content contract (the export-sensitivity section grouped by rule set);
  - every number pasted (the membership group's values);
  - the interpretive sentences (the membership status lines, and no reading of the variant against another sensitivity);
  - the reading rules carried (a sixth list);
  - the check's report selection (the variant gate, and the 2026-10-31 report as an earlier layout);
  - the findings (the variant's carried);
  - the pin (`REPORT_EXPORT_VARIANTS` covers all three variants).

  `motco-export-sensitivity` ("Reading rules" binds every report that quotes the variant) is fulfilled without changing its text.

## Impact

- `src/adni_sexdiff/constants.py`: `REPORT_EXPORT_VARIANTS` gains `nmr_all_columns`, and the comments on the report constants and the docstring name this change. No scientific constant is added.
- `src/adni_sexdiff/data.py`:
  - `_export_sensitivity_section`: the groups, their leads and the prefixed tables of a later group, with the words from `_variant_words`, and the `diagnostics` key left out of the counts table;
  - `render_report`: the preamble, the summary's group paragraphs, the reading-rules lists per rule set, and the docstring;
  - `_check_report_layout`: the variant comparison;
  - `run_report` and `check_report` docstrings.

  The loader, gates, chain, `_export_variant_status_line`, `_export_variant_lines` and `_export_variant_rules_heading` are unchanged. No step's output changes.
- `src/adni_sexdiff/cli.py`: none. `report` keeps its twelve flags.
- `reports/motco-adni-<date>.md`: added and committed. It is aggregate. The four earlier reports are unchanged.
- `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged, since no participant-level output is added.
- No new dependencies. The step takes seconds, makes no MOTCO call and records no numerics.
- Machines: any machine with the Nix shell and the committed tree. No data root, data machine or participant-level file is needed.
- Workflow:
  - Implement and verify, then commit the implementation.
  - On 2026-11-01 or later, write the report on the clean tree, check it and commit it alone.
  - Archive, then open the PR and merge.

  Regenerating any input invalidates the report until a new one is written and checked.
