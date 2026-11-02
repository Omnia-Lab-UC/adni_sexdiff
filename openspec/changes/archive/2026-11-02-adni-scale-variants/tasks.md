# Tasks

Nothing runs on ADNI data until the user has accepted the proposal's scientific constants and they are in `constants.py` (task 1.1):
- `SCALE_VARIANT_RULE` (the three transforms, their offsets, λ as the metabolite's smallest positive value over the exported participants divided by 10);
- the `EXPORT_VARIANTS` entries `raw_scale`, `log2_plus_one` and `glog` (block `all`, hook `scale`);
- `SCALE_VARIANT_READING_RULES` (eight statements) and the dependence label `scale dependence`;
- the predeclared `EXPORT_VARIANT_EXPECTED_COUNTS` for the three.

On 2026-11-02 the user chose all three variants, λ per metabolite as its smallest positive value divided by 10, one shared rule set, and the report left to a later change. The spike then measured the decided scales; the user accepts its counts with the proposal.

Every run is pinned, and every manifest records its `numerics`.

Where tasks run:
- **Groups 1, 2 and 4** read only committed files and run on any clone.
- **Groups 3 and 5** run on one data machine, whose cleaned, cohort and primary export files hash to the committed manifests. Every one of their task lines names its hostname.
- **Scratch outputs** live in the session scratchpad, never under `results/` or `reports/`, except the in-place gate of task 3.5, which restores every tracked file.

No task line records a participant value.

## 1. Constants (any clone)

- [x] 1.1 Add to `constants.py` (design D1, D2, D3, D5):
  - `SCALE_VARIANT_RULE`, keyed by variant: the transform expression, the offset (`None`, `1`, `"lambda"`) and for `glog` `lambda_divisor` 10 and λ's rule in words;
  - the `EXPORT_VARIANTS` entries `raw_scale`, `log2_plus_one` and `glog`, after `nmr_all_columns`, each with block `all`, hook `scale`, rule `SCALE_VARIANT_RULE`, `reads_data_root` `False`, the proposal's setting verbatim and change `adni-scale-variants`;
  - `SCALE_VARIANT_READING_RULES` (the proposal's eight statements, verbatim);
  - the shared `EXPORT_VARIANT_RULE_SETS` entry of design D3 for the three;
  - `EXPORT_VARIANT_EXPECTED_COUNTS` for the three (the proposal's table: the export keys with `phase_offset`, `shape` and `spectrum` per block, `scale.median_below_offset` for `log2_plus_one`, `unchanged_equal_primary` for `metadata.csv` and `covariates.csv`, and `analysis`);
  - the docstring naming the change and its constants.

  Verify:
  - `uv run python -c "from adni_sexdiff import constants as c; print(tuple(c.EXPORT_VARIANTS), len(c.SCALE_VARIANT_READING_RULES), c.EXPORT_VARIANT_EXPECTED_COUNTS['raw_scale']['spectrum'], c.EXPORT_VARIANT_EXPECTED_COUNTS['log2_plus_one']['scale'], c.REPORT_EXPORT_VARIANTS, sum(len(v) for v in c.REPORT_INPUT_FILES.values()))"` prints the six names in order, `8`, `{'p180': {'numerical_rank': 133}, 'nmr': {'numerical_rank': 104}}`, `{'median_below_offset': {'p180': 46, 'nmr': 129}}`, the three pinned names and `106`;
  - each of the three committed variants' `motco_input/manifest.json` `variant` block equals its registry entry on `block`, `hook`, `rule`, `setting` and `change`;
  - three scratch copies of `constants.py`, each loaded in a fresh interpreter, fail at import naming both constants: one with the shared rule-set entry removed for `glog`, one with its `rules` name misspelt, one with the `raw_scale` counts entry removed.

  Done 2026-11-02 (nixos-home): the one-liner printed the six names in order, `8`, `{'p180': {'numerical_rank': 133}, 'nmr': {'numerical_rank': 104}}`, `{'median_below_offset': {'p180': 46, 'nmr': 129}}`, the three pinned names and `106`; the three committed `variant` blocks equal their registry entries on the five fields; the three scratch copies failed at import with the two `EXPORT_VARIANT_RULE_SETS` assertions and the `EXPORT_VARIANT_EXPECTED_COUNTS` assertion, each naming both constants. The three entries share `_SCALE_VARIANT_SHARED_COUNTS` and `_SCALE_RULE_SET`.
- [x] 1.2 The report gate (design D6), on the committed tree:
  - `report --check` (the newest report, `reports/motco-adni-2026-11-02.md`) passes with no mismatch (89 tables, 5418 cells, 929 other lines), exit 0, and prints three lines naming `raw_scale`, `log2_plus_one` and `glog` as registered and not covered;
  - `report --out <scratch>/motco-adni-2026-11-02.md` is byte-identical to the committed report;
  - an audit hook over `run_report` lists 106 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none under the three new directories.

  Record the outcomes in this line.
  Done 2026-11-02 (nixos-home, committed tree plus task 1.1): `report --check` compared 89 tables, 5418 cells and 929 other lines with no mismatch, exit 0, and printed one line each for `raw_scale`, `log2_plus_one` and `glog` as registered and not covered; the scratch `report --out` is byte-identical to the committed report; an audit hook over `run_report(check=True)` saw 106 files opened under `results/`, equal to `REPORT_INPUT_FILES` resolved through `_report_dirs`, none under the three new directories.
- [x] 1.3 Update the docs for group 1: `AGENTS.md` constraint 5 (the decided constants gain `SCALE_VARIANT_RULE` and `SCALE_VARIANT_READING_RULES`), "Flag and ask" (an entry for the three variants: the scales, λ, the rules, the label and the counts) and the `EXPORT_FEATURE_RULE` note that leaves the scale variants to a later change; the `constants.py` docstring. Verify with `grep -n "one later change\|later change" AGENTS.md README.md src/adni_sexdiff/constants.py` that no hit still describes the scale variants as pending.
  Done 2026-11-02: the decided-constant lists of the status paragraph, constraint 5 and "Flag and ask" name `SCALE_VARIANT_RULE` and `SCALE_VARIANT_READING_RULES` (constraint 5 also the three entries), "Flag and ask" has the scale variants' entry, and the `EXPORT_FEATURE_RULE` note names them as decided by `adni-scale-variants`. The grep's one hit is that entry's note that the report is left to a later change.

## 2. Text from the rule set (any clone)

- [x] 2.1 Give `_variant_words` its branch for hook `scale` (design D3), `_export_variant_lines` and `_export_variant_phase_line` their scale branches and the feature-rule line of `render_analysis_summary` its clause (design D4). Then run the re-render gate of design D7, a scratch script that calls the renderers on the committed records, manifests and tables and compares the output with the committed files:
  - the 12 committed `summary.md` (the primary, the latent arm, the three variants, the CN / LMCI / AD arm, the six ranks);
  - the 3 committed `export_sensitivity.md`;
  - the 7 committed `diagnostics.md` (the primary, the arm, the three variants, the CN / LMCI / AD arm, rank 12).

  Every file must be byte-identical. If one is not, revert and find the cause. Record the counts in this line.
  Done 2026-11-02 (nixos-home, committed files only): the gate re-rendered 22 of 22 byte-identical, 12 `summary.md`, 3 `export_sensitivity.md` and 7 `diagnostics.md`, on the code before the branches (with task 1.1's constants) and after them. The primary's numerical rank comes from `reference.spectrum`, copied beside `reference.shape` (task 3.2), since the spec reads both exports' ranks from the variant's export manifest.
- [x] 2.2 In the scratchpad, build in-memory record sets for the three scale variants from the committed `nmr_all_columns` records: the variant block of each new entry, an export manifest with the scale counts of the proposal (`counts.shape`, `counts.spectrum`, `counts.scale`, `reference.shape`, `settings.units`, `settings.scale`), no bridge. Verify on each:
  - `summary.md` names the variant and the scale of both blocks, prints the "Export variant" lines with the transform, the offsets and per block the shape counts and numerical rank of both exports, the `phase` line of design D4, the feature-rule clause, and `READING_RULES` then the eight scale rules, string-equal to the constant, with no statement of `EXPORT_VARIANT_READING_RULES` or `NMR_MEMBERSHIP_READING_RULES` (rule 3 excepted, worded alike in every set);
  - with one p-value edited so that `delta` is rejected, `export_sensitivity.md` prints `differs (scale dependence)` with a sentence citing scale rules 2 and 6, and the findings cite them;
  - a rank edited to 5 gives the finding citing scale rule 3;
  - `diagnostics.md` names the variant as an export whose scale differs, cites scale rule 7 and prints the scale rules after `READING_RULES`.

  Record the counts of checks in this line.
  Done 2026-11-02 (nixos-home, committed files only): 69 of 69 checks, 23 per variant (the glog record set carries the spike's quantiles of λ over the median as its `counts.scale`). Rule 3 is the one statement worded alike in every set, so "no statement of the other sets" was checked on their other statements and their names. With `delta` rejected and the rank set to 5, the status line and the reading line cite scale rules 2 and 6, the `delta` finding cites them and the rank finding cites scale rule 3.
- [x] 2.3 Update the docstrings of the changed renderers and of `_run_export`, `run_export_sensitivity` and `render_export_sensitivity`. Verify with `grep -n "scale of both blocks\|scale rule" src/adni_sexdiff/data.py` that every hit is in the `scale` branch of `_variant_words`, `_export_variant_lines` or `_export_variant_phase_line`, or in a docstring; the citation word itself comes from `cite`.
  Done 2026-11-02: the docstrings of `render_analysis_summary`, `_export_variant_lines`, `_export_variant_phase_line`, `_variant_words`, `run_export`, `_run_export`, `run_export_sensitivity`, `render_export_sensitivity` and `render_axis_diagnostics` and the module docstring name the scale variants. The grep's two hits are the `scale` branch of `_variant_words` and its docstring; the re-render gate still gives 22 of 22.

## 3. The scale hook and the gates (data machine)

- [x] 3.1 Confirm the data machine and record its hostname: the cleaned tables, `cohort.csv` and the six primary export files hash to the committed manifests; note whether the three registered variants' participant-level files exist (the in-place gate of 3.5 needs none, it rewrites them).
  Done 2026-11-02 on nixos-home: the two cleaned tables, `p180_runs.csv`, the two metabo_adni logs, `cohort.csv` and the six primary export files hash to their committed manifests (12 of 12). The participant-level files of `nist_bridge` and `per_run_standardized` exist here (8 of 8 each); those of `nmr_all_columns` do not (it ran on nixos-office).
- [x] 3.2 Implement the `scale` hook in `_run_export` (design D2). Verify:
  - a pinned `export --out-dir <scratch>` writes the six output hashes the committed export manifest records (design D7);
  - per variant, a scratch script calling `_run_export(..., variant=<name>, staging=<scratch>)` on the committed inputs writes an export whose manifest records the proposal's counts with no deviation (per block the shape counts, the numerical rank, the run offset; for `log2_plus_one` the metabolites with a median below 1; `metadata.csv` and `covariates.csv` equal to the primary's; 41 / 3 NMR zero cells, 0 floors not positive, 0 non-finite cells), `settings.units` as the variant's transform and `reference.shape` equal to the primary export manifest's `counts.shape`;
  - both blocks' columns are the primary's in the primary's order, and the feature tables have 133 and 165 rows, all `kept`, with `floor` equal to the primary's feature tables and `offset` empty, 1 or λ (λ checked against the cleaned table's smallest positive value over the exported participants divided by 10);
  - the cells equal an independent computation from the cleaned tables: `x`, `log2(x + 1)` and the glog, and the 41 NMR zero cells land at 0, 0 and `log2(λ / 2)`;
  - with sex and stage permuted in a scratch copy of `cohort.csv` (its manifest hash updated in the scratch copy), each variant's `p180.csv` and `nmr.csv` are byte-identical;
  - on a scratch copy of the cleaned NMR table with one kept column set to zero (its clean manifest's output hash and the scratch cohort manifest's recorded clean hash updated), `glog` stops naming the block and 1 metabolite, and writes nothing.

  Record the counts of checks in this line.
  Done 2026-11-02 on nixos-home: the pinned `export --out-dir <scratch>` wrote the six committed hashes, with no deviation or finding. The scratch script ran 105 of 105 checks over the three variants: no deviation and no finding, numerics pinned, `settings.units`, `settings.scale`, `reference.shape`, `metadata.csv` and `covariates.csv` equal to the primary's, 41 / 3 NMR zero cells, 0 floors not positive, 0 non-finite cells, per block the predeclared shape counts, numerical ranks and run offsets, and 46 / 129 medians below 1. Both blocks keep the primary's columns, order and rows. The feature tables have the primary's rows (133; 245, of which 165 `kept`) and columns plus `offset`, with the primary's `floor`. The cells equal an independent computation bit for bit (the glog within 1e-12 of its `hypot` form), and the 41 zero cells land at 0, 0 and `log2(λ / 2)`. With sex and stage permuted, every `p180.csv` and `nmr.csv` is byte-identical. The λ gate stopped `glog` with "nmr: 1 kept metabolite(s) with no positive cell …" and wrote nothing. Two corrections came out of the checks, both in design D1 and D2 now. The unchanged-file list needed an `all` case: the expression from `adni-nmr-all-columns` listed both block CSVs. The λ gate had to run before the floor gate: a column with no positive cell also has a non-positive floor, so the floor gate stopped it first without naming λ. The recorded run offsets, spectra and λ quantiles equal the spike's.
- [x] 3.3 Run the feasibility check of design D8 and D10: a scratch `_run_trajectory_analysis` on the scratch `raw_scale` export of 3.2 at the primary's settings with `n_jobs` free, into the scratchpad. Verify that it completes with a CV-selected rank and the three statistics, and record MOTCO's rank, any warning it prints and the runtime in this line; the run is not reported and is discarded. If MOTCO stops, record its message here and stop the apply.
  Done 2026-11-02 on nixos-home, `n_jobs` 8: MOTCO completed on the raw-scale blocks (NMR numerical rank 104 of 165) with a CV-selected rank of 7, 5 of 5 CV repeats, the three statistics and no count deviation, in 74 s. MOTCO printed no warning; the only warnings were Python's `DeprecationWarning` on `fork()` in a multi-threaded process (488, from the 8 workers). The `n_jobs` finding marks the run as not reported; its statistics are not recorded, and it is deleted after task 3.4 reads it.
- [x] 3.4 Verify that `run_axis_diagnostics` reads a scale variant without a code change: a pinned `axis-diagnostics` on the scratch `raw_scale` export and the scratch analysis of 3.3 into the scratchpad expects the rank-independent keys (1501 participants, the primary's cells, p180 133 and NMR 165 features with 3 PCs), records `export_variant` `raw_scale` and `is_primary` false, and its `diagnostics.md` names the variant as an export whose scale differs, cites scale rule 7 and prints the scale rules; a pinned `axis-diagnostics` on the primary into a scratch directory writes the committed hashes. Record the outcomes in this line.
  Done 2026-11-02 on nixos-home, with no code change: the pinned `axis-diagnostics` on the scratch `raw_scale` export and analysis expected the rank-independent keys (1501 participants, the primary's cells, p180 133 and NMR 165 features with 3 PCs) with no deviation, and recorded `export_variant` `raw_scale` and `is_primary` false. Its `diagnostics.md` names "an export whose scale differs", cites scale rule 7 and prints the eight scale rules after `READING_RULES`. Its findings are the flagged components, the `n_jobs` 8 read and the not-primary read. The pinned `axis-diagnostics` on the primary into a scratch directory wrote the five committed hashes. The scratch exports, analysis and diagnostics were then deleted.
- [x] 3.5 Run the in-place gate of the three registered variants (design D7):
  - move each variant's `diagnostics/` to the scratchpad;
  - run `export-sensitivity --variant nist_bridge --force`, then `--variant per_run_standardized --force`, then `--variant nmr_all_columns --force`, pinned at `n_jobs = 1`;
  - verify that `git status` shows no tracked CSV, `summary.md`, `export_sensitivity.md` or `nist_bridge.csv` changed, that every gitignored CSV hashes to its committed manifest's record, and that the manifests and `result.json` differ only in time, revision, runtime, the machine fields of `numerics` and the hashes of the files that carry them;
  - restore the tracked manifests and `result.json` with `git restore`, move the diagnostics back, and verify that `git status` is clean under `results/`.

  If any check fails, stop the apply and record the difference in this line.
  Done 2026-11-02 on nixos-home, pinned at `n_jobs = 1` (119 s, 98 s and 133 s), each with counts that reproduce the predeclared ones. Against HEAD:
  - every tracked CSV, `summary.md`, `export_sensitivity.md` and `nist_bridge.csv` is byte-identical;
  - every ignored CSV (the six export files, `latent_scores.csv` and `analysis_metadata.csv` per variant) hashes to its committed manifest's record, `nmr_all_columns`'s too, whose files had not existed on this machine;
  - the 12 manifests and `result.json` files differ in 82 keys: 48 are times, revisions, MOTCO's runtime and the `numerics` block, and 34 are the sha256 and bytes of `result.json` and of the manifests that carry them; no other key differs.

  The tracked manifests and `result.json` were restored with `git restore`, the diagnostics moved back, and `git status` is clean under `results/`.

## 4. Docs (any clone)

- [x] 4.1 Update the docs for groups 2 and 3:
  - `README.md`, the `export-sensitivity` section: the three variants with block `all` and hook `scale`, `SCALE_VARIANT_RULE`, the `offset` column of the feature tables, the rule's floor recorded and not applied, the λ gate, the counts, the rule set and the label, and `--variant <name>` for the real runs since `--variant all` stops on the existing variants without `--force`;
  - `README.md`, the `report` section: three registered variants outside the pin, named on progress lines;
  - `AGENTS.md`: the status paragraph, the `export-sensitivity` entry (the hook `scale`, the gates, the findings), the `axis-diagnostics` sentence on a variant's expected counts, and the Layout entries for `constants.py`, `data.py` and `scripts/` (`spike_scale_variants.py`);
  - the `export-sensitivity` help string of `cli.py` (one string, as the previous change changed it).

  Verify with `grep -n "raw_scale\|log2_plus_one\|glog" README.md AGENTS.md src/adni_sexdiff/cli.py` that each file names the three, and that `AGENTS.md` lists `SCALE_VARIANT_READING_RULES` in constraint 5 and in "Flag and ask".
  Done 2026-11-02: `README.md` (status, quick start, the diagnostics note, the `export-sensitivity` section with the table rows, a scale-variants paragraph, the λ gate, the outputs, the counts table, the rule sets and the scale rules in brief, and the report pin) names the three 25 times, and `AGENTS.md` names them 22 times (status, the `export-sensitivity` entry with the hook, the λ gate and the outputs, the Layout entries for `constants.py`, `data.py` and `scripts/`). `AGENTS.md` lists `SCALE_VARIANT_READING_RULES` in constraint 5 and "Flag and ask". `cli.py` builds its choices and help from `EXPORT_VARIANTS`, so its source has no literal name; `export-sensitivity --help` prints the six and the help string names the scale of both blocks. `report --help` now lists the pin `REPORT_EXPORT_VARIANTS` for `--export-sensitivity-dir`, in place of the registry, which now includes variants the report does not read.

## 5. The real runs and commit hygiene (data machine)

- [x] 5.1 Commit the implementation, the docs, the spike script and the change's artifacts on the branch `adni-scale-variants`, created from `main`. Verify that `git status` is clean and that no file under `results/` or `reports/` changed.
  Done 2026-11-02: committed as 237e916 on `adni-scale-variants`, on top of the proposal commit c0ad0ef, which holds the spike script and the change's artifacts. `git status` was clean afterwards, and the commit touches no file under `results/` or `reports/`.
- [x] 5.2 On the clean tree at that commit, for each variant in registry order (`raw_scale`, `log2_plus_one`, `glog`): run `export-sensitivity --variant <name>` pinned at `n_jobs = 1`, then `axis-diagnostics --input-dir results/motco_export_sensitivity/<name>/motco_input --analysis-dir results/motco_export_sensitivity/<name>/analysis --out-dir results/motco_export_sensitivity/<name>/diagnostics`. Verify, per variant:
  - no deviation from `EXPORT_VARIANT_EXPECTED_COUNTS[<name>]` in the export, analysis and comparison manifests, nor from the rank-independent keys in the diagnostics manifest;
  - the export counts equal the spike's;
  - `metadata.csv` and `covariates.csv` equal the primary's;
  - every `numerics.pinned` is true;
  - the diagnostics pass their chain checks, with `is_primary` false and `export_variant` the variant;
  - the tracked files of the primary, the latent arm, the three registered variants, the CN / LMCI / AD arm and the rank sweep are unchanged (sha256 before and after).

  Record the hostname, and point to the committed files for each variant's rank, statistics and statuses: none is written in this line.
  Done 2026-11-02 on nixos-home, on the clean tree at 237e916, one variant at a time (export-sensitivity 108 s, 102 s and 83 s). A scratch script ran 61 of 61 checks:
  - the export, analysis, comparison and diagnostics manifests have no deviation, are pinned and record a clean revision at `n_jobs` 1;
  - per block, the run offset (median |d|, |corr(PC1, phase)|) and the spectrum (PC1 share, effective rank) equal the spike's to three decimals;
  - `metadata.csv` and `covariates.csv` equal the primary's;
  - the diagnostics read the variant (`export_variant`, `is_primary` false), expect the rank-independent keys with 165 NMR features, and the hashes they record equal the export and analysis files on disk;
  - the 135 tracked files under `results/` and `reports/` from before the runs are unchanged.

  Each variant's rank, statistics and statuses are in its committed `comparison/export_sensitivity.md` and `export_sensitivity_manifest.json`.
- [x] 5.3 Rerun 5.2's `export-sensitivity` for each variant with `--force` on the same clean tree, with the first run's `diagnostics/` moved aside, then move it back. Verify that every non-JSON file is byte-identical to the first run's, and that the manifests and `result.json` differ only in time, revision, runtime and the hashes of the files that carry them. Record the outcome per variant in this line.
  Done 2026-11-02 on nixos-home, same tree. The first run's 23 files per variant were copied to the scratchpad, and its `diagnostics/` moved there. One step differs from the wording above: after each `--force` rerun, `axis-diagnostics` was rerun on the second run instead of moving the first run's diagnostics back. A diagnostics manifest records the hashes of the analysis' `result.json` and `analysis_manifest.json`, which carry the runtime and time, so only the second run's diagnostics chain to the committed second-run analysis (the committed `nmr_all_columns` diagnostics record its second run's hashes too). Per variant (`raw_scale`, `log2_plus_one`, `glog`):
  - the same 23 files, and the 18 non-JSON files are byte-identical, the diagnostics' included;
  - the JSON files differ only in 9 time, runtime and numerics keys, and in 17, 17 and 12 sha256 and bytes keys of `result.json` and the manifests that carry them;
  - the revision is the same and no stale-diagnostics finding appears.

  The second run's files are the ones committed. The scratch copies were deleted.
- [x] 5.4 Commit the outputs. Before the commit, name every file added under `results/motco_export_sensitivity/<name>/` for the three variants with why it is aggregate: `motco_input/manifest.json`, the analysis' `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six (15 per variant, 45 in all). Verify:
  - `git check-ignore` matches the participant-level files of each variant: the four export CSVs, the two feature tables, `latent_scores.csv` and `analysis_metadata.csv`;
  - no staged CSV has an `rid` or `RID` column, and `grep -w` finds `rid` only as a column name;
  - `report --check` on `reports/motco-adni-2026-11-02.md` still passes with no mismatch and prints the three uncovered-variant lines;
  - `openspec validate adni-scale-variants --strict` passes.

  Done 2026-11-02, committed as 787861d; its message names the 15 files per variant and why each is aggregate. Verified:
  - `git check-ignore` matches all 24 participant-level files (8 per variant);
  - the staged CSV headers are `block`/`feature`, `group`/`stage`, `analysis` and the diagnostics' `component`/`quantity`, never `rid` or `RID`;
  - `grep -w` finds `rid` only as the sample column's name (`sample_column`, `sample_col`, and the `--sample-col` argument of `cli_equivalent`);
  - `report --check` on `reports/motco-adni-2026-11-02.md` passes with no mismatch (89 tables, 5418 cells, 929 other lines) and prints the three uncovered-variant lines;
  - `openspec validate adni-scale-variants --strict` passes.

## Workflow follow-up

- Archive the change on its branch and sync its specs. At the archive, update the Purpose of `openspec/specs/motco-export-sensitivity/spec.md`, which names the run handling and the NMR membership, to name the scale too. Then push, open the PR and merge, as the earlier changes did.
- The follow-up report change adds `raw_scale`, `log2_plus_one` and `glog` to `REPORT_EXPORT_VARIANTS` as one group under `SCALE_VARIANT_READING_RULES` (a seventh rule list), chooses the group's table-title prefix, extends the check's variant gate to the six variants, and re-issues the report on a later date.
- After it, every registered variant is in the report. What remains outside the pipeline: the cluster run (constraint 7) and a written discussion quoting the report.
