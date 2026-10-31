# Proposal

## Why

The predeclared rank sweep of `rank-sensitivity` (change `adni-rank-sensitivity`, merged in PR #14) has been run pinned and committed:
- the anchor at the primary's rank 8 reproduced the primary;
- nesting holds at every rank;
- `delta` differs at rank 6 only (rank dependence), and `angle` and `shape` are `same` at every rank;
- the top rank (12) has its own axis diagnostics.

No report quotes the sweep yet. The newest report, `reports/motco-adni-2026-10-30.md`, predates it, and `REPORT_INPUT_FILES` does not name its files. `RANK_SENSITIVITY_READING_RULES` binds "every report that quotes the sweep", and `adni-rank-sensitivity` left the report to "a later change". This is that change.

It extends step 6 so that one report covers the primary and all four predeclared sensitivities: the latent arm, the export variants, the CN / LMCI / AD arm and the rank sweep. Each is shown beside the primary. The change then writes and checks the next report. Like the earlier report changes, it reads committed aggregate files only, so it runs on any clone.

## What Changes

- **Inputs extended**, still committed aggregate files only. Under `results/motco_rank_sensitivity/` the step reads 27 more files:
  - per rank of the ladder (`rank_02/` … `rank_12/`): `result.json`, `analysis_manifest.json` and `summary.md` (18 files);
  - the comparison's `rank_sensitivity.csv`, `rank_sensitivity.md` and `rank_sensitivity_manifest.json`;
  - the top rank's diagnostics, six files.

  That makes 93 inputs in all (66 now), 29 of them manifests (21 now). No participant-level file is opened or required:
  - the ranks' `latent_scores.csv` and `analysis_metadata.csv` are quoted by the hashes their manifests record;
  - their `stage_means.csv` and `pls_loadings.csv` are quoted by hash too, as the other analyses' are.
- **Gates extended.** All of them run before anything is written, and each names the file or setting, both values and the command to rerun.
  - **Presence.** Every input is present.
  - **Hashes.** Every aggregate file hashes to the value its own manifest records. That adds 19 files, 63 in all.
  - **Identity.** The sweep is `RANK_SENSITIVITY_LADDER`:
    - each rank directory holds that rank: its manifest records step `rank-sensitivity`, `settings.forced_components`, `rank_sweep.forced_rank` and its record's `latent.selected_lv` all equal to the directory's rank, and selection `forced`;
    - each rank's `rank_sweep.ladder` equals the constant, and its `rank_sweep.primary_rank` equals the primary record's rank;
    - each rank records no latent adjustment, in its manifest or in its record;
    - the comparison manifest records the constant, one entry per rank in ladder order, and the anchor equal at the primary record's rank;
    - the diagnostics record `is_primary` false and the forced rank `diagnosed_rank` (12).
  - **Reported runs.** Every rank records `n_jobs = REPORTED_N_JOBS` in its manifest and its record. Every `numerics` block is pinned, and all 29 manifests record the same MOTCO, scikit-learn and metabo_adni versions.
  - **Chain.** The chain holds through the six ranks, the comparison and the top rank's diagnostics: 67 more links, 167 in all.
    - Per rank (8 links each, 48 in all): the primary export manifest and its four CSV hashes, the primary's `result.json` and `analysis_manifest.json` as `reference`, and the primary export as `reference.export`.
    - The comparison (15 links): the primary as `reference` (2), every rank's `result.json` and `analysis_manifest.json` under `ranks` (12), and the primary export (1).
    - The diagnostics (4 links): the rank-12 analysis manifest, its `result.json` as that manifest records it, the primary export and the cohort manifest.

  On the committed tree, all 67 links hold and the 19 aggregate files hash to the values their own manifests record. A read-only script checked this while this proposal was written. It also confirmed that all 9 manifests involved (the sweep's 8 and the primary's) record MOTCO 0.10.0, scikit-learn 1.8.0 and metabo_adni 0.5.8, and that the sweep's 8 are pinned.
- **New report section: "Rank sensitivity"**, placed after "Stage-definition sensitivity". `REPORT_SECTIONS` grows from twelve to thirteen sections. The section holds:
  - **Statistics.** The statistics table, with the primary row and then the six ranks per statistic (21 rows), read from `rank_sensitivity.csv`. Each row has its rank and a status, and the primary's status is the result.
  - **`angle`.** A paragraph that reads `angle` beside each rank's floor, eigengap and its own null, never against another rank's `angle`.
  - **Status sentences.** The three status sentences of `rank_sensitivity.md`, from `_rank_status_line`, so the strings are equal.
  - **Latent spaces.** One row per analysis: the rank and how it was selected, the floor, `cv_mean_auroc`, the CV repeats, the eigengap with its null quantiles, and the `angle` null summary.
  - **Anchor and nesting.** The anchor and nesting bullets and the nesting table of `rank_sensitivity.md`, read from the comparison manifest and printed by the code that writes that file.
  - **Predeclared counts.** The anchor rank, the comparison rows and each rank's selection, rank and CV repeats, beside `RANK_SENSITIVITY_EXPECTED_COUNTS`.
  - **Diagnostics.** The top rank's diagnostics, laid out as the other sensitivities' are: flagged rows, components and block PCs. They are introduced by sweep rule 7: components up to the primary's rank are the primary's, and a component above it that tracks a variable is a measurement-space finding about the higher ranks. Then each analysis' first component against `phase`.
  - **Reproduction.** The six ranks' `cli_equivalent`, each with `--forced-components`.
- **Other sections extended** from the same inputs:
  - **Summary:** the sweep's paragraph and its status lines, and the top rank's flagged diagnostic components.
  - **Provenance:** the eight manifests, the 27 inputs and the 67 links.
  - **Findings:** every finding and deviation of the eight new manifests, copied verbatim. On the committed tree that is the rank-6 `delta` finding (under rank 6 and under the comparison) and the top rank's flagged rows and not-the-primary note.
  - **Reading rules:** a fifth list, `RANK_SENSITIVITY_READING_RULES`, printed after `STAGE_SENSITIVITY_READING_RULES` and named beside every table that quotes the sweep.
  - **Reproduction:** the `rank-sensitivity` command, the top rank's `axis-diagnostics` command, and the six ranks in the list of MOTCO CLI equivalents.
- **No reading against another sensitivity.** Sweep rule 8 reads the sweep against the primary only, and the CV-selected ranks of the other sensitivities are their own selections. No status, sentence or table reads them against the sweep. Each sensitivity keeps its own paragraph and its own section, and a line that lists several sensitivities compares none.
- **Shared sentences keep their bytes.**
  - The report calls `_rank_status_line` and the lead line of `_rank_sweep_rules_heading` as they are.
  - The anchor and nesting bullets and the nesting table are written inline in `render_rank_sensitivity`, so they move into helpers that both callers use.
  - `_anchor_text` lists the compared fields in the order of the anchor record's dict. The step ran with the gate's comparison order, but the manifest stores the record with sorted keys. So the same function, called on the anchor as the manifest records it, lists `config_spectrum` first, and the anchor bullet would no longer equal the committed line. A read-only re-render while this proposal was written showed this. `_anchor_text` therefore lists the fields in the gate's fixed order, whatever the order of the record it is given. The step's own output does not change, since it already used that order.
  - A byte gate covers both changes. `rank_sensitivity.md` is rendered from the committed records and the comparison manifest, and each rank's "Rank sweep" lines from its manifest's `rank_sweep` block. The results must equal the committed files byte for byte. With the gate's field order, the read-only re-render already gave these bytes.
- **Reports of an earlier layout.** No code change is needed: the existing earlier-layout gate covers them.
  - `reports/motco-adni-2026-10-30.md` (twelve sections) becomes a report of an earlier layout. `report --check` on it stops, naming the absent section "Rank sensitivity". It checks at 2e4a3e1, the commit that added it.
  - The 2026-10-29 and 2026-10-28 reports stop the same way, and still check at c94f5e7 and 36c9cc8.
  - All three stay in place, unchanged.
- **Flags:** `--rank-sensitivity-dir`, the root of `results/motco_rank_sensitivity/`, read through `RANK_SENSITIVITY_RANK_DIR` and `RANK_SENSITIVITY_SUBDIRS`. `report` then has twelve flags.
- **Constants:** conventions only.
  - `REPORT_RANK_SWEEP_FILES` names the files read per rank directory, in the comparison and in the diagnostics.
  - `REPORT_INPUT_FILES` gains the roles `rank-sensitivity/<subdir>`, one per rank of the ladder, then the comparison and the diagnostics.
  - `REPORT_SECTIONS` gains "Rank sensitivity".
- **Docs.**
  - `README.md`: the `report` section, and the sentence that says the rank sweep enters the report by a later change.
  - `AGENTS.md`: the status paragraph (the report now covers the sweep), step 6 (93 inputs, 29 manifests, 167 links, thirteen sections, twelve flags, the fifth rule list, the third earlier-layout report), and the Layout entries.
  - The `constants.py` and `run_report` docstrings.
  - "Flag and ask" is unchanged.
- **The next report**, `reports/motco-adni-<date>.md`. It is written on the first date after 2026-10-30, or later, as the user chose for the previous report. The 2026-10-30 file is never overwritten, and the date is never back- or forward-dated. It is written on the clean tree from the committed outputs, checked with `--check` and committed alone.

Scientific constants introduced by this change: none. The report decides nothing. It quotes `RANK_SENSITIVITY_LADDER`, `RANK_SENSITIVITY_READING_RULES` and `RANK_SENSITIVITY_EXPECTED_COUNTS` and the earlier constants by name, and every number from the records and manifests.

Out of scope, each its own change if wanted:
- Any reading of the sweep against the latent arm, an export variant or the CN / LMCI / AD arm (sweep rule 8), and any crossing of sensitivities.
- Each rank's per-statistic reading lines, which `rank_sensitivity.md` and each rank's `summary.md` print. The report prints the status sentences, as it does for the other three sensitivities. A rank's own reading line for the `delta` rejection at rank 6 stays in that rank's files.
- Any statistic across ranks: a combined p-value, a count of the ranks that reject, a trend over rank or a smallest p-value (sweep rule 6).
- The diagnostics of ranks other than 12, which by nesting are the top rank's first components. The other ranks' `stage_means.csv` and `pls_loadings.csv` stay quoted by hash only.
- A same-day report name, such as an ordinal suffix.
- A rewrite of the 2026-10-28, 2026-10-29 or 2026-10-30 report, or a check of any of them with the new code.
- Any change to the outputs of `clean`, `cohort`, `export`, `analyze`, `axis-diagnostics` or the four sensitivity steps.
- The remaining registered sensitivities: the other export variants (all 245 NMR columns, the raw scale, `log2(x + 1)`, the generalized log).
- Figures, HTML or PDF rendering, and a written discussion.
- The cluster run (constraint 7).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `case-study-report`: these requirements change:
  - the inputs (the sweep's files);
  - the chain (through the ranks, the comparison and the top rank's diagnostics);
  - the reported-run gate (every rank, 29 manifests);
  - the content contract (the thirteenth section);
  - every number pasted (the sweep's tables);
  - the interpretive sentences (the sweep's status lines, and no reading against another sensitivity);
  - the reading rules carried (a fifth list);
  - the check's report selection (the 2026-10-30 report as an earlier layout);
  - the findings (the sweep's carried).

  One requirement is added: the rank sweep is identified before reporting. `motco-rank-sensitivity` ("Reading rules bind every reader of the sweep") already binds every report that quotes the sweep. This change fulfils it without changing that text.

## Impact

- `src/adni_sexdiff/constants.py`: `REPORT_RANK_SWEEP_FILES` is added, `REPORT_INPUT_FILES` and `REPORT_SECTIONS` are extended, and the docstring names the change. No scientific constant is added.
- `src/adni_sexdiff/data.py`:
  - `_report_dirs`, `_report_rerun`, `_REPORT_MANIFESTS` and `_load_report_inputs`: the sweep's roles, labels and gates;
  - `render_report`: the new section, and the extended summary, provenance, reading-rules and reproduction sections;
  - `render_rank_sensitivity`: its anchor and nesting lines move into helpers, and `_anchor_text` lists the fields in the gate's order, under the byte gate;
  - the `run_report` signature and docstring.

  `check_report` and the layout gate are unchanged. The bytes of every committed `rank_sensitivity.md` and `summary.md` stay the same.
- `src/adni_sexdiff/cli.py`: the `--rank-sensitivity-dir` flag.
- `reports/motco-adni-<date>.md`: added and committed. It is aggregate. The three earlier reports are unchanged.
- `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged, since no participant-level output is added.
- No new dependencies. The step takes seconds, makes no MOTCO call and records no numerics.
- Machines: any machine with the Nix shell and the committed tree. No data root, data machine or participant-level file is needed.
- Workflow:
  - Implement and verify, then commit the implementation.
  - On or after 2026-10-31, write the report on the clean tree, check it and commit it alone.
  - Archive, then open the PR and merge.

  Regenerating any input invalidates the report until a new one is written and checked.
