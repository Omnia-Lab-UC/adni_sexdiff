# Tasks

Nothing runs on ADNI data until the user has accepted the proposal's scientific constants and they are in `constants.py` (task 1.1):
- the `EXPORT_VARIANTS` entry `nmr_all_columns` (all 245 NMR columns, the rule's scale, each column with its own 5 % floor);
- `NMR_MEMBERSHIP_READING_RULES` (eight statements) and the dependence label `feature-membership dependence`;
- the predeclared `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]`.

On 2026-10-30 the user chose `nmr_all_columns` alone, the split with the report pin, the rule's scale for the 80 derived columns, and a self-contained rule set with an explicit mapping and the eight rules. Membership rule 4 then gained the spike's tail counts (21 with |skew| > 1, 8 with |z| > 8), which the user accepts with the proposal.

Order (design D8): the apply starts after `adni-report-rank-sweep` has committed its report and been archived and merged. This branch is then rebased onto `main`.

Every run is pinned, and every manifest records its `numerics`.

Where tasks run:
- **Groups 1, 2 and 5** read only committed files and run on any clone.
- **Groups 3, 4 and 6** run on one data machine, whose cleaned, cohort and primary export files hash to the committed manifests. Every one of their task lines names its hostname.
- **Scratch outputs** live in the session scratchpad, never under `results/` or `reports/`, except the in-place gate of task 3.3, which restores every tracked file.

No task line records a participant value.

## 1. Constants

- [x] 1.1 Add to `constants.py` (design D1, D3, D5, D6):
  - the `EXPORT_VARIANTS` entry `nmr_all_columns`, after the two p180 entries, with the proposal's setting verbatim;
  - `NMR_MEMBERSHIP_READING_RULES` (the proposal's eight statements, verbatim);
  - `EXPORT_VARIANT_RULE_SETS` (the table of design D3), with an import-time assertion that its keys are `EXPORT_VARIANTS`' in order and a second one that each `rules` names a module-level tuple;
  - `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]` (the proposal's table: the export keys, `analysis` with features p180 133, NMR 245, joint 378, and `diagnostics`, the rank-independent keys with `blocks.nmr.features` 245);
  - `REPORT_EXPORT_VARIANTS = ("nist_bridge", "per_run_standardized")`, with an import-time assertion that it is a subsequence of `EXPORT_VARIANTS` in order, and `REPORT_INPUT_FILES` built from it;
  - the docstring naming the change and its constants.

  Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(tuple(c.EXPORT_VARIANTS), len(c.NMR_MEMBERSHIP_READING_RULES), c.EXPORT_VARIANT_EXPECTED_COUNTS['nmr_all_columns']['analysis']['features'], c.REPORT_EXPORT_VARIANTS, sum(len(v) for v in c.REPORT_INPUT_FILES.values()))"` prints the three names, `8`, the features `{'p180': 133, 'nmr': 245, 'joint': 378}`, the two p180 names and `93`;
  - each of the two p180 variants' committed `motco_input/manifest.json` `variant` block equals its registry entry;
  - three scratch copies of `constants.py`, each loaded in a fresh interpreter, fail at import naming both constants: one with a mapping key removed, one with a `rules` name misspelt, one with the pin out of registry order.

## 2. Text from the rule sets (any clone)

- [x] 2.1 Make the renderers take every variant-specific word from `EXPORT_VARIANT_RULE_SETS` and every block name from the variant's block (design D3, D4). The renderers are `_statistic_reading_line`, `render_analysis_summary`, `_export_variant_lines`, `_export_variant_rules_heading`, `_export_variant_findings`, `_export_variant_status_line`, `render_export_sensitivity` and `render_axis_diagnostics`. Then run the re-render gate of design D7, a scratch script that calls the renderers on the committed records, manifests and tables and compares the output with the committed files:
  - the 11 committed `summary.md` (the primary, the latent arm, the two p180 variants, the CN / LMCI / AD arm, the six ranks);
  - the two committed `export_sensitivity.md`;
  - the six committed `diagnostics.md`.

  Every file must be byte-identical. If one is not, revert and find the cause. Record the counts in this line.
  Done 2026-10-30 (nixos-office, committed files only): the gate re-rendered 19 of 19 byte-identical, 11 `summary.md`, 2 `export_sensitivity.md` and 6 `diagnostics.md`. The same gate on the code before the change also gave 19 of 19. The regenerated `_export_variant_findings` and `status_rule` of both p180 variants equal their committed manifests'.
- [x] 2.2 In the scratchpad, build an in-memory `nmr_all_columns` record set from the committed `nist_bridge` records: the variant block of the new entry, an export manifest with the membership counts of the proposal, and the bridge removed. Verify on it:
  - `summary.md` names the variant and the NMR block it changes, prints the "Export variant" lines with the rule's columns equal, the block shares and the NMR shape counts, and prints `READING_RULES` then the eight membership rules, string-equal to the constant, with no line of `EXPORT_VARIANT_READING_RULES`;
  - its `phase` line is the one of design D4;
  - with one p-value edited so that `delta` is rejected, `export_sensitivity.md` prints `differs (feature-membership dependence)` with a sentence citing membership rules 2 and 6, and the findings cite them;
  - a rank edited to 5 gives the finding citing membership rule 3;
  - `diagnostics.md` names the variant and the NMR block, cites membership rule 7 and prints the membership rules after `READING_RULES`.

  Done 2026-10-30, 21 of 21 checks. Rule 3 is the one statement worded alike in both sets, so "no line of `EXPORT_VARIANT_READING_RULES`" was checked on that set's own statements, its name and its heading. A differing status's finding cites the variant's rules 2 and 6 when the variant alone rejects, else rule 2. For the p180 variants this wording appears in no committed file, since every status there is `same`.
- [x] 2.3 Update the docstrings of the changed renderers. Verify with `grep -n "p180 values only\|handling of the p180 run" src/adni_sexdiff/data.py` that every remaining hit is read from the p180 entries of `EXPORT_VARIANT_RULE_SETS` or sits in the report's code, which is pinned to the p180 variants.
  Done 2026-10-30: one hit remains, in `render_report`'s summary section (the report's code). The p180 words now live in `EXPORT_VARIANT_RULE_SETS` (`source`) and in `_variant_words`.

## 3. The membership hook and the gates (data machine)

- [x] 3.1 Confirm the data machine and record its hostname:
  - the cleaned tables, `cohort.csv` and the six primary export files hash to the committed manifests;
  - the two QC archive symlinks exist, and `hash_raw_file` returns `predeclared` true for both.

  Done 2026-10-30 on `nixos-office`. Every file hashes to its manifest: `P180.csv`, `p180_runs.csv`, `NMR.csv` and both logs, `cohort.csv`, and the six primary export files. Both archives are symlinks into `Metabolomics/p180/`. `predeclared` is true for both, set by `check_known_repairs` on the `hash_raw_file` records.
- [x] 3.2 Implement the `membership` hook in `_run_export` and the no-bridge path in `_run_export_variant` (design D2). Verify:
  - a pinned `export --out-dir <scratch>` writes the six output hashes the committed export manifest records (design D7);
  - a scratch script calling `_run_export(..., variant="nmr_all_columns", staging=<scratch>)` on the committed inputs writes an export whose manifest records the proposal's counts with no deviation: the features with `derived_kept`, 41 / 3 zero cells, 0 floors not positive and 0 non-finite cells, NMR shape 24 / 9, NMR phase |d| > 0.5 / > 1 at 5 / 0, 378 joint features, shares 0.352 / 0.648, `rule_columns_equal_primary` true, and `p180.csv`, `metadata.csv` and `covariates.csv` equal to the primary's;
  - its `features_nmr.csv` holds 245 rows, all `kept`, with the families of the spike;
  - with sex and stage permuted in a scratch copy of `cohort.csv` (its manifest hash updated in the scratch copy), the variant's `p180.csv` and `nmr.csv` are byte-identical;
  - with one cell of a concentration column edited in a scratch copy of the primary `nmr.csv` (its recorded hash updated in the scratch copy of the manifest), `rule_columns_equal_primary` is false and a finding names the block and the count of columns, while the run completes.

  Done 2026-10-30 on `nixos-office`, every run pinned, outputs in the scratchpad and deleted afterwards. The pinned `export --out-dir <scratch>` wrote the six committed hashes with no deviation. The variant export passed 28 of 28 checks:
  - every predeclared count with no deviation and no finding; the 245 columns in cleaned order; the 165 concentrations' floors equal the primary's;
  - `features_nmr.csv`: 245 rows, all `kept`, concentration 165, percentage 72, ratio 4, degree 1, size 3;
  - permuted labels: `p180.csv` and `nmr.csv` byte-identical;
  - one edited cell: the comparison false, the finding "nmr: 1 of the 165 column(s) …", a deviation, and the run completed.

  `_run_export_variant` needed no new branch. It already reads the bridge and the data root only for hook `factors`. `_run_export` now leaves `diagnostics` out of the expected export counts, as it does `analysis`.
- [x] 3.3 Run the in-place gate of the p180 variants (design D7):
  - move both variants' `diagnostics/` to the scratchpad;
  - run `export-sensitivity --variant nist_bridge --force`, then `--variant per_run_standardized --force`, pinned at `n_jobs = 1`;
  - verify that `git status` shows no tracked CSV, `summary.md`, `export_sensitivity.md` or `nist_bridge.csv` changed, that every gitignored CSV hashes to its committed manifest's record, and that the manifests and `result.json` differ only in time, revision, runtime and the hashes of the files that carry them;
  - restore the tracked manifests and `result.json` with `git restore`, move the diagnostics back, and verify that `git status` is clean under `results/`.

  If any check fails, stop the apply and record the difference in this line.

  Done 2026-10-30 on `nixos-office`, on the working tree of groups 1 to 3 before commit, so the manifests recorded a dirty revision before the restore. Both reruns were pinned at `n_jobs = 1`, with every predeclared count reproduced and only the committed rank findings (variant rule 3). Results:
  - `git status`: no tracked CSV, `summary.md`, `export_sensitivity.md` or `nist_bridge.csv` changed.
  - The six export files of each variant, `latent_scores.csv` and `analysis_metadata.csv` hash to their committed manifest's record.
  - The manifests and `result.json` differ only in `created_at`, the export's recorded `created_at`, `git_revision`, `runtime_seconds`, the hash and bytes of the files that carry them, and `numerics.host`, `cpu_model` and `cpus_available`. The committed run was on `nixos-home`; `pinned` and the settings are equal.
  - After `git restore` and with the diagnostics moved back, `git status` is clean under `results/`, and every tracked file is byte-identical to a pre-run backup.
  - The participant-level files of the two p180 variants were absent on `nixos-office` before this gate. They now exist here, gitignored, with the committed hashes.

## 4. Diagnostics read the variant (data machine)

- [x] 4.1 Make `run_axis_diagnostics` take a variant's `diagnostics` counts when its entry holds them (design D5). Verify:
  - a pinned `axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir <scratch>` writes the four CSVs and `diagnostics.md` with the committed hashes, and its manifest's `expected` equals the committed manifest's;
  - the same for `per_run_standardized`;
  - a pinned `axis-diagnostics` on the primary into a scratch directory writes the committed hashes.

  Done 2026-10-30 on `nixos-office`, pinned, into the scratchpad, using the p180 variants' participant-level files from task 3.3. For `nist_bridge`, `per_run_standardized` and the primary, the four CSVs and `diagnostics.md` equal the committed files, with `expected` equal to the committed manifest's and no deviation. On a variant with its own `diagnostics` counts, the not-primary finding adds "(with the variant's block features, EXPORT_VARIANT_EXPECTED_COUNTS)". On the p180 variants it is unchanged.

## 5. The report pin (any clone)

- [x] 5.1 Make the report loop over `REPORT_EXPORT_VARIANTS` wherever it reads or names a variant, and print one progress line per registered variant outside the pin (design D6). Verify on the committed tree:
  - `report --check` on the newest committed report passes with no mismatch, exit 0, and prints the line naming `nmr_all_columns`;
  - `report --out <scratch>/<the newest report's file name>` is byte-identical to that report;
  - an audit hook over `run_report` lists 93 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none under `results/motco_export_sensitivity/nmr_all_columns/`.

  Open until the rank-sweep report is committed (design D8). The code is done. On 2026-10-30 the newest committed report was still `motco-adni-2026-10-30.md`, of the twelve-section layout, and `--check` on it stops at the earlier-layout gate whatever the code. Interim checks on `nixos-office`, committed files only:
  - before the change, `report --out <scratch>/motco-adni-2026-10-31.md` (sha256 `089ebd78…`);
  - after it, `report --check --out` on that file: exit 0, no mismatch (80 tables, 4737 cells, 812 other lines), and the line "export variant nmr_all_columns (change adni-nmr-all-columns) is registered and not covered by this report";
  - a fresh render: byte-identical to it;
  - the audit hook: 93 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none under `nmr_all_columns/`.

  Done 2026-10-31 (nixos-dell-laptop), against the committed rank-sweep report `reports/motco-adni-2026-10-31.md` (13ce7c8, merged in #15), on the clean tree at 7ac3ed6, this branch rebased onto `main`:
  - `report --check` without `--out` read it as the newest: exit 0, no mismatch (80 tables, 4737 cells, 812 other lines), and the line "export variant nmr_all_columns (change adni-nmr-all-columns) is registered and not covered by this report";
  - `report --out <scratch>/motco-adni-2026-10-31.md`: byte-identical to the committed report;
  - the audit hook: 93 files opened under `results/`, equal to `REPORT_INPUT_FILES` resolved through `_report_dirs`, every one tracked, none ignored by git, none under `nmr_all_columns/`;
  - the four committed reports byte-unchanged and `git status` clean after the checks.
- [x] 5.2 Update the docs for groups 1, 2, 4 and 5:
  - `README.md`, the `export-sensitivity` section: the third variant, its hook, its rules, its counts, and `--variant nmr_all_columns` for the real run, since `--variant all` stops on the existing variants without `--force`;
  - `README.md`, the `report` section: the pin, and the report change that adds the variant;
  - `AGENTS.md`: the status paragraph (the third variant, not yet in the report), the `export-sensitivity` entry, the `report` entry (the pin), "Flag and ask" (the entry, the rule set, the label and the counts), and the Layout entries for `constants.py` and `data.py`.

  Verify with `grep -n nmr_all_columns README.md AGENTS.md`, and verify that `AGENTS.md` lists `NMR_MEMBERSHIP_READING_RULES` among the decided constants in constraint 5 and in "Flag and ask".

  Done 2026-10-30. `nmr_all_columns` appears in 21 lines of `README.md` and 14 of `AGENTS.md`. `NMR_MEMBERSHIP_READING_RULES` is listed in `AGENTS.md`'s constraint 5 and in "Flag and ask", which also gains the variant's entry, rules, label and counts. Also updated:
  - README: its status, pipeline, quick start, layout and `axis-diagnostics` sections;
  - `AGENTS.md`: the `EXPORT_FEATURE_RULE` variant note and the `scripts/` layout;
  - the `data.py` module docstring;
  - the `export-sensitivity` help text in `cli.py`, which said every variant handles the p180 run. This is outside the proposal's "cli.py: none", one string.

## 6. The real run and commit hygiene (data machine)

- [x] 6.1 Commit the implementation, the docs and the change's artifacts on the branch. Verify that `git status` is clean and that no file under `results/` or `reports/` changed.
  Committed 2026-10-30 on `adni-nmr-all-columns`, on top of the rank sweep's implementing commit 5b3953b. The rank-sweep report was not yet written, archived or merged (design D8). Since then:
  - 2026-10-31: `adni-report-rank-sweep` merged into `main` (#15, 87c707d), and this branch rebased onto it. The implementing commit is now 7ac3ed6, unchanged by the rebase (`git range-diff`: `=`); no file it touches changed on `main` after 5b3953b;
  - 2026-10-31: 5.1's checks against the committed rank-sweep report, recorded in the commit after 7ac3ed6, which changes this file only;
  - not yet run: 6.2, on a data machine, on the clean tree at the branch head, whose code is 7ac3ed6's.
- [ ] 6.2 On the clean tree at that commit, run `export-sensitivity --variant nmr_all_columns` pinned at `n_jobs = 1`, then `axis-diagnostics --input-dir results/motco_export_sensitivity/nmr_all_columns/motco_input --analysis-dir results/motco_export_sensitivity/nmr_all_columns/analysis --out-dir results/motco_export_sensitivity/nmr_all_columns/diagnostics`. Verify:
  - no deviation from `EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]` in the export, analysis and comparison manifests, nor in the diagnostics manifest;
  - the export counts equal the spike's;
  - `p180.csv`, `metadata.csv` and `covariates.csv` equal the primary's, and the rule's columns equal the primary's;
  - every `numerics.pinned` is true;
  - the diagnostics pass their chain checks, with `is_primary` false and `export_variant` `nmr_all_columns`;
  - the primary's, the latent arm's, the p180 variants', the CN / LMCI / AD arm's and the rank sweep's tracked files are unchanged.

  Record the hostname, and point to the committed files for the rank, statistics and statuses: none is written in this line.
- [ ] 6.3 Rerun 6.2 with `--force` on the same clean tree, with the first run's `diagnostics/` moved aside. Verify that every non-JSON file is byte-identical to the first run, and that the manifests and `result.json` differ only in time, revision, runtime and the hashes of the files that carry them.
- [ ] 6.4 Commit the outputs. Before the commit, name every file added under `results/motco_export_sensitivity/nmr_all_columns/` with why it is aggregate: `motco_input/manifest.json`, the analysis' `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six. Verify:
  - `git check-ignore` matches the participant-level files: the four export CSVs, the two feature tables, `latent_scores.csv` and `analysis_metadata.csv`;
  - no staged CSV has an `rid` or `RID` column, and `grep -w` finds `rid` only as a column name;
  - `report --check` on the newest committed report still passes with no mismatch;
  - `openspec validate adni-nmr-all-columns --strict` passes.

## Workflow follow-up

- Archive the change on its branch and sync its specs. At the archive, update the Purpose of `openspec/specs/motco-export-sensitivity/spec.md`, which says variants change only how the p180 run is handled. Then open the PR and merge, as the earlier changes did.
- The follow-up report change:
  - adds `nmr_all_columns` to `REPORT_EXPORT_VARIANTS` and `NMR_MEMBERSHIP_READING_RULES` to the reading-rules section;
  - generalizes the report's variant sentences that say "the p180 values only";
  - extends the earlier-layout gate to the variants a report lists;
  - re-issues the report.
- The scale variants (the raw scale, `log2(x + 1)`, the generalized log) are one later change, after the report change.
