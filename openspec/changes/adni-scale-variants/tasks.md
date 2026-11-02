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

- [ ] 1.1 Add to `constants.py` (design D1, D2, D3, D5):
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
- [ ] 1.2 The report gate (design D6), on the committed tree:
  - `report --check` (the newest report, `reports/motco-adni-2026-11-02.md`) passes with no mismatch (89 tables, 5418 cells, 929 other lines), exit 0, and prints three lines naming `raw_scale`, `log2_plus_one` and `glog` as registered and not covered;
  - `report --out <scratch>/motco-adni-2026-11-02.md` is byte-identical to the committed report;
  - an audit hook over `run_report` lists 106 files opened under `results/`, equal to `REPORT_INPUT_FILES`, none under the three new directories.

  Record the outcomes in this line.
- [ ] 1.3 Update the docs for group 1: `AGENTS.md` constraint 5 (the decided constants gain `SCALE_VARIANT_RULE` and `SCALE_VARIANT_READING_RULES`), "Flag and ask" (an entry for the three variants: the scales, λ, the rules, the label and the counts) and the `EXPORT_FEATURE_RULE` note that leaves the scale variants to a later change; the `constants.py` docstring. Verify with `grep -n "one later change\|later change" AGENTS.md README.md src/adni_sexdiff/constants.py` that no hit still describes the scale variants as pending.

## 2. Text from the rule set (any clone)

- [ ] 2.1 Give `_variant_words` its branch for hook `scale` (design D3), `_export_variant_lines` and `_export_variant_phase_line` their scale branches and the feature-rule line of `render_analysis_summary` its clause (design D4). Then run the re-render gate of design D7, a scratch script that calls the renderers on the committed records, manifests and tables and compares the output with the committed files:
  - the 12 committed `summary.md` (the primary, the latent arm, the three variants, the CN / LMCI / AD arm, the six ranks);
  - the 3 committed `export_sensitivity.md`;
  - the 7 committed `diagnostics.md` (the primary, the arm, the three variants, the CN / LMCI / AD arm, rank 12).

  Every file must be byte-identical. If one is not, revert and find the cause. Record the counts in this line.
- [ ] 2.2 In the scratchpad, build in-memory record sets for the three scale variants from the committed `nmr_all_columns` records: the variant block of each new entry, an export manifest with the scale counts of the proposal (`counts.shape`, `counts.spectrum`, `counts.scale`, `reference.shape`, `settings.units`, `settings.scale`), no bridge. Verify on each:
  - `summary.md` names the variant and the scale of both blocks, prints the "Export variant" lines with the transform, the offsets and per block the shape counts and numerical rank of both exports, the `phase` line of design D4, the feature-rule clause, and `READING_RULES` then the eight scale rules, string-equal to the constant, with no statement of `EXPORT_VARIANT_READING_RULES` or `NMR_MEMBERSHIP_READING_RULES` (rule 3 excepted, worded alike in every set);
  - with one p-value edited so that `delta` is rejected, `export_sensitivity.md` prints `differs (scale dependence)` with a sentence citing scale rules 2 and 6, and the findings cite them;
  - a rank edited to 5 gives the finding citing scale rule 3;
  - `diagnostics.md` names the variant as an export whose scale differs, cites scale rule 7 and prints the scale rules after `READING_RULES`.

  Record the counts of checks in this line.
- [ ] 2.3 Update the docstrings of the changed renderers and of `_run_export`, `run_export_sensitivity` and `render_export_sensitivity`. Verify with `grep -n "scale of both blocks\|scale rule" src/adni_sexdiff/data.py` that every hit is in the `scale` branch of `_variant_words`, `_export_variant_lines` or `_export_variant_phase_line`, or in a docstring; the citation word itself comes from `cite`.

## 3. The scale hook and the gates (data machine)

- [ ] 3.1 Confirm the data machine and record its hostname: the cleaned tables, `cohort.csv` and the six primary export files hash to the committed manifests; note whether the three registered variants' participant-level files exist (the in-place gate of 3.5 needs none, it rewrites them).
- [ ] 3.2 Implement the `scale` hook in `_run_export` (design D2). Verify:
  - a pinned `export --out-dir <scratch>` writes the six output hashes the committed export manifest records (design D7);
  - per variant, a scratch script calling `_run_export(..., variant=<name>, staging=<scratch>)` on the committed inputs writes an export whose manifest records the proposal's counts with no deviation (per block the shape counts, the numerical rank, the run offset; for `log2_plus_one` the metabolites with a median below 1; `metadata.csv` and `covariates.csv` equal to the primary's; 41 / 3 NMR zero cells, 0 floors not positive, 0 non-finite cells), `settings.units` as the variant's transform and `reference.shape` equal to the primary export manifest's `counts.shape`;
  - both blocks' columns are the primary's in the primary's order, and the feature tables have 133 and 165 rows, all `kept`, with `floor` equal to the primary's feature tables and `offset` empty, 1 or λ (λ checked against the cleaned table's smallest positive value over the exported participants divided by 10);
  - the cells equal an independent computation from the cleaned tables: `x`, `log2(x + 1)` and the glog, and the 41 NMR zero cells land at 0, 0 and `log2(λ / 2)`;
  - with sex and stage permuted in a scratch copy of `cohort.csv` (its manifest hash updated in the scratch copy), each variant's `p180.csv` and `nmr.csv` are byte-identical;
  - on a scratch copy of the cleaned NMR table with one kept column set to zero (its clean manifest's output hash and the scratch cohort manifest's recorded clean hash updated), `glog` stops naming the block and 1 metabolite, and writes nothing.

  Record the counts of checks in this line.
- [ ] 3.3 Run the feasibility check of design D8 and D10: a scratch `_run_trajectory_analysis` on the scratch `raw_scale` export of 3.2 at the primary's settings with `n_jobs` free, into the scratchpad. Verify that it completes with a CV-selected rank and the three statistics, and record MOTCO's rank, any warning it prints and the runtime in this line; the run is not reported and is discarded. If MOTCO stops, record its message here and stop the apply.
- [ ] 3.4 Verify that `run_axis_diagnostics` reads a scale variant without a code change: a pinned `axis-diagnostics` on the scratch `raw_scale` export and the scratch analysis of 3.3 into the scratchpad expects the rank-independent keys (1501 participants, the primary's cells, p180 133 and NMR 165 features with 3 PCs), records `export_variant` `raw_scale` and `is_primary` false, and its `diagnostics.md` names the variant as an export whose scale differs, cites scale rule 7 and prints the scale rules; a pinned `axis-diagnostics` on the primary into a scratch directory writes the committed hashes. Record the outcomes in this line.
- [ ] 3.5 Run the in-place gate of the three registered variants (design D7):
  - move each variant's `diagnostics/` to the scratchpad;
  - run `export-sensitivity --variant nist_bridge --force`, then `--variant per_run_standardized --force`, then `--variant nmr_all_columns --force`, pinned at `n_jobs = 1`;
  - verify that `git status` shows no tracked CSV, `summary.md`, `export_sensitivity.md` or `nist_bridge.csv` changed, that every gitignored CSV hashes to its committed manifest's record, and that the manifests and `result.json` differ only in time, revision, runtime, the machine fields of `numerics` and the hashes of the files that carry them;
  - restore the tracked manifests and `result.json` with `git restore`, move the diagnostics back, and verify that `git status` is clean under `results/`.

  If any check fails, stop the apply and record the difference in this line.

## 4. Docs (any clone)

- [ ] 4.1 Update the docs for groups 2 and 3:
  - `README.md`, the `export-sensitivity` section: the three variants with block `all` and hook `scale`, `SCALE_VARIANT_RULE`, the `offset` column of the feature tables, the rule's floor recorded and not applied, the λ gate, the counts, the rule set and the label, and `--variant <name>` for the real runs since `--variant all` stops on the existing variants without `--force`;
  - `README.md`, the `report` section: three registered variants outside the pin, named on progress lines;
  - `AGENTS.md`: the status paragraph, the `export-sensitivity` entry (the hook `scale`, the gates, the findings), the `axis-diagnostics` sentence on a variant's expected counts, and the Layout entries for `constants.py`, `data.py` and `scripts/` (`spike_scale_variants.py`);
  - the `export-sensitivity` help string of `cli.py` (one string, as the previous change changed it).

  Verify with `grep -n "raw_scale\|log2_plus_one\|glog" README.md AGENTS.md src/adni_sexdiff/cli.py` that each file names the three, and that `AGENTS.md` lists `SCALE_VARIANT_READING_RULES` in constraint 5 and in "Flag and ask".

## 5. The real runs and commit hygiene (data machine)

- [ ] 5.1 Commit the implementation, the docs, the spike script and the change's artifacts on the branch `adni-scale-variants`, created from `main`. Verify that `git status` is clean and that no file under `results/` or `reports/` changed.
- [ ] 5.2 On the clean tree at that commit, for each variant in registry order (`raw_scale`, `log2_plus_one`, `glog`): run `export-sensitivity --variant <name>` pinned at `n_jobs = 1`, then `axis-diagnostics --input-dir results/motco_export_sensitivity/<name>/motco_input --analysis-dir results/motco_export_sensitivity/<name>/analysis --out-dir results/motco_export_sensitivity/<name>/diagnostics`. Verify, per variant:
  - no deviation from `EXPORT_VARIANT_EXPECTED_COUNTS[<name>]` in the export, analysis and comparison manifests, nor from the rank-independent keys in the diagnostics manifest;
  - the export counts equal the spike's;
  - `metadata.csv` and `covariates.csv` equal the primary's;
  - every `numerics.pinned` is true;
  - the diagnostics pass their chain checks, with `is_primary` false and `export_variant` the variant;
  - the tracked files of the primary, the latent arm, the three registered variants, the CN / LMCI / AD arm and the rank sweep are unchanged (sha256 before and after).

  Record the hostname, and point to the committed files for each variant's rank, statistics and statuses: none is written in this line.
- [ ] 5.3 Rerun 5.2's `export-sensitivity` for each variant with `--force` on the same clean tree, with the first run's `diagnostics/` moved aside, then move it back. Verify that every non-JSON file is byte-identical to the first run's, and that the manifests and `result.json` differ only in time, revision, runtime and the hashes of the files that carry them. Record the outcome per variant in this line.
- [ ] 5.4 Commit the outputs. Before the commit, name every file added under `results/motco_export_sensitivity/<name>/` for the three variants with why it is aggregate: `motco_input/manifest.json`, the analysis' `result.json`, `pls_loadings.csv`, `stage_means.csv`, `analysis_manifest.json` and `summary.md`, the comparison's three files and the diagnostics' six (15 per variant, 45 in all). Verify:
  - `git check-ignore` matches the participant-level files of each variant: the four export CSVs, the two feature tables, `latent_scores.csv` and `analysis_metadata.csv`;
  - no staged CSV has an `rid` or `RID` column, and `grep -w` finds `rid` only as a column name;
  - `report --check` on `reports/motco-adni-2026-11-02.md` still passes with no mismatch and prints the three uncovered-variant lines;
  - `openspec validate adni-scale-variants --strict` passes.

## Workflow follow-up

- Archive the change on its branch and sync its specs. At the archive, update the Purpose of `openspec/specs/motco-export-sensitivity/spec.md`, which names the run handling and the NMR membership, to name the scale too. Then push, open the PR and merge, as the earlier changes did.
- The follow-up report change adds `raw_scale`, `log2_plus_one` and `glog` to `REPORT_EXPORT_VARIANTS` as one group under `SCALE_VARIANT_READING_RULES` (a seventh rule list), chooses the group's table-title prefix, extends the check's variant gate to the six variants, and re-issues the report on a later date.
- After it, every registered variant is in the report. What remains outside the pipeline: the cluster run (constraint 7) and a written discussion quoting the report.
