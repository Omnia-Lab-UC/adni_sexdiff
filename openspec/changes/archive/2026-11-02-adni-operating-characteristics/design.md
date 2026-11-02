# Design

## Context

See proposal.md (Why) for the motivation. The state this design works from:

- **The report.** `report` (`run_report` → `_load_report_inputs` → `render_report`, `data.py`) reads the 145 files of `REPORT_INPUT_FILES` from nine directory flags (`_report_dirs`), then gates them in order:
  1. presence;
  2. each aggregate file against its own manifest;
  3. identity of the primary, arm, variants, CN / LMCI / AD arm and sweep;
  4. reported, pinned, version-consistent runs;
  5. the 255-link chain.

  It then renders the thirteen sections of `REPORT_SECTIONS`. `--check` regenerates the report and compares it cell by cell, after `_check_report_layout` has compared the report's sections and variant headings with the current ones.
- **The provenance loop treats a role with no manifest as a bridge table** (`if not role_manifests:` in gate 2). A new role without a manifest must be handled before that branch.
- **The reading sentences are shared code.** `_statistic_reading_line` and the status lines are shared with `summary.md` and the four comparison documents, which are string-equal across documents by design. The `angle` and `shape` non-rejection sentences end with "(reading rule 3: no power statement exists at this design)". The `delta` one says "no evidence of a difference between the sexes' trajectories at this design."
- **The decision file** (MOTCO `0d726922`, `results/adni-design-2026-11-02/run/adni_design_decision.json`, 76,057 bytes) holds these keys:
  - `rule`, `verdict`, `consequence`, `indicative`, `indicative_reasons`;
  - `size`: `holds`, `sentence`, `readings`;
  - `power`: per statistic `effects`, `informative_from`, `max_rate`, `effect_at_max`, `construction_maximum`, `floor`;
  - `statements`, `descriptive`, `calibration_realized`, `adni_reference`, `construction`, `settings_hash`, `units`, `run_directory`.

  The values of `adni_reference` are hard-coded in MOTCO's script from this repository's committed files, at fixed digits.

## Goals / Non-Goals

**Goals:**
- Cite the measurement where it can be checked: a byte-pinned copy, gated by hash and by a value-for-value comparison of `adni_reference` with the committed records it describes.
- Print the measurement's own numbers and sentences verbatim, and the new rule list verbatim, in one new section, the summary and the reading-rules section.
- Leave every step, every step output, every existing reading sentence and every existing rule list byte-unchanged.

**Non-Goals:**
- A reader for MOTCO's other run files (`adni_design_rates.csv`, `size_readings.csv`, the strata, the p-values), which repeat what the decision file holds.
- A general mechanism for citing several external measurements. One source, one constant; a second citation is its own change.
- Any change to how a sensitivity's status is computed or worded.

## Decisions

### D1. Confirm beside the predeclared rules, never rewrite them (user's choice)

The measurement enters as a new rule list, `OPERATING_CHARACTERISTICS_READING_RULES`, printed after `READING_RULES` by the report only. `READING_RULES`, the six sensitivity rule sets, `_statistic_reading_line` and the status lines stay byte-unchanged. The clause "no power statement exists at this design" keeps appearing wherever it appears today, and measurement rule 2 reads it: it records what was known when it was written, before any run.

Alternatives considered:
- **Rewrite rule 3 and the four sensitivity clauses, then re-issue.**
  - It would regenerate 34 committed result files through 16 MOTCO analyses and 10 diagnostics for prose alone. Their statistics would be byte-equal, but every manifest hash downstream of a `summary.md` would change.
  - It would edit rules after their results, which `READING_RULES` rule 9 and MOTCO's exit-review draft ("the case studies' predeclared reading rules stand") argue against.
- **Change `_statistic_reading_line` for the report only.** This breaks the string-equality between the report and `summary.md` that the spec requires.

### D2. Two constants in `constants.py`, a new block after the rank sweep's

The block holds `OPERATING_CHARACTERISTICS_READING_RULES` (the nine rules of the proposal, verbatim) and `OPERATING_CHARACTERISTICS_SOURCE`, a dict with:
- `repository`, `change`, `pull_request`, `commit` (the full hash);
- `path`, `report`, `sha256`, `verdict`.

Beside them come the conventions `OPERATING_CHARACTERISTICS_DIR = "references/motco_adni_design"` and `OPERATING_CHARACTERISTICS_DECISION = "adni_design_decision.json"`.

Two import-time assertions tie rule 1 to the source: it contains the commit's first seven characters and the verdict. A later edit of one without the other then fails before any step runs.

The comment above the block names the change, its date and that it was decided after every analysis here ran. That differs from every other rule list, which was decided before any run, and the comment says why: the list reads a measurement made elsewhere, changes no constant and selects nothing.

### D3. A byte copy under `references/`, read only there

The copy is `references/motco_adni_design/adni_design_decision.json`, made with `git -C <MOTCO clone> show <commit>:<path>`.

`references/` is new. It holds committed third-party aggregate files the report cites. It is not under `results/`, because it is no pipeline output: no step writes it, `scripts/sync_results.sh` has no reason to move it (it is in every clone), and no manifest of this repository records it. The constant records it instead.

Alternatives considered:
- **Read it from a MOTCO clone or GitHub at report time.** This breaks the report's any-clone, no-network contract, and the clone's location is not fixed.
- **Copy only the quoted values into constants.** This loses the hash gate and the `adni_reference` gate, and the report's rule that every number comes from a file.

### D4. The gates, in order, before anything is written

The new role `operating-characteristics` joins `REPORT_INPUT_FILES` (one file), and `_report_dirs` maps it from `--operating-characteristics-dir`.
- **Gate 1 (presence)** covers it. `_report_rerun` gives it the `git show` copy command at the pinned commit as its hint.
- **Gate 2** handles it before the bridge-table branch. Its sha256 must equal `OPERATING_CHARACTERISTICS_SOURCE["sha256"]`, and a difference stops the step naming the copy, both hashes and the copy command. Its provenance row's "recorded in" reads `` `OPERATING_CHARACTERISTICS_SOURCE`: sha256 (MOTCO <commit[:7]>) ``. It counts neither among the 99 manifest-checked files nor among the 255 chain links. Its own progress line names it.
- **Gate 6 (the cited measurement)** runs after the chain, so every committed value it reads has passed gates 2 to 5:
  1. `verdict` equals the constant's, and `indicative` is false.
  2. The key set of `adni_reference` equals the map below, exactly.
  3. Each value equals its committed source at the map's decimals: `round(committed, d) == round(recorded, d)`, integers and lists by equality.

  A difference stops the step naming the key, both values and the source file. It also says that the measurement was calibrated against another analysis, so citing one for this analysis is a new change.

The map (`_OPERATING_CHARACTERISTICS_REFERENCE`, a private convention in `data.py`; the decimals are those MOTCO's script writes):

| `adni_reference` key | committed source | decimals |
|---|---|---|
| `selected_lv` | primary `result.json` `latent.selected_lv` | integer |
| `cv_mean_auroc` | primary `latent.cv_mean_auroc` | 4 |
| `cv_mean_auroc_range_cv_selected` | lowest and highest `latent.cv_mean_auroc` of the nine records with `component_selection` `cv` (primary, latent arm, six variants, CN / LMCI / AD arm) | 3 |
| `first_component_spearman_phase` | primary diagnostics `axis_correlations.csv`, row `pls_0` / `phase`, \|`spearman`\| | 3 |
| `pooled_relative_eigengap` | primary `config_spectrum.pooled.relative_eigengap` | 3 |
| `angle_null_q95` | primary `null_summary.angle.q95` | 2 |
| `phase_offset.<block>.median_abs_d`, `.abs_corr_pc1_phase` | export manifest `counts.phase_offset.<block>` | 2 |
| `phase_offset.<block>.abs_d_gt_1` | export manifest `counts.phase_offset.<block>.abs_d_gt_1` | integer |
| `phase_offset.<block>.n_features` | export manifest `counts.features.<block>.kept` | integer |
| `design_columns` | primary `covariates.design_columns` | list |
| `phase_pooled_share` | primary `covariates.reference_row["phase[ADNI2GO]"]` | 4 |
| `p_values.<statistic>` | primary `p_values.<statistic>` | 4 |

The absolute value for `pls_0` is used because a PLS component's sign is arbitrary. The minimum and maximum over the nine records are used in the gate only. The report prints MOTCO's range as recorded, and computes no range of its own.

The spike for this proposal ran the whole map on the committed tree, and every key holds.

### D5. The section "Operating characteristics", seventh of fourteen

It sits after "Axis diagnostics of the primary" and before "Latent-adjustment sensitivity": the measurement is of the primary's construction, and the sensitivity sections follow it. Cross-references are numbered from `REPORT_SECTIONS` (`_section_ref`), so later sections renumber without code.

The section, in order:
1. **A lead paragraph.** It says what was measured and where. It names the change, PR and commit, and states that the measurement changes no constant, record or status. It says the section is read under `READING_RULES` and `OPERATING_CHARACTERISTICS_READING_RULES`.
2. **Table "Cited measurement"** (field → value):
   - from the constant: repository, change, pull request, commit, path, report, pinned sha256;
   - the copy's path and observed sha256;
   - from the file: verdict, indicative, units recorded / expected / failures, and the settings hash.
3. **Table "Decision rule"** (item → text): every key of `rule` in the file's order, verbatim (`alpha`, `indicative`, `k`, `power`, `power_floor`, `rank_strata`, `size`, `targets`, `verdict`).
4. **Table "Size at this design"**, one row per reading of `size.readings`, keyed `<mode> <statistic>`: effect, rejections / replicates, rate (three decimals), bound (four), verdict. Then the paragraph `size.sentence`, verbatim.
5. **Table "Power at this design"**, one row per effect of each `power.<statistic>.effects`, keyed `<statistic> e = <effect>`: construction (`mode`), rejections / replicates, rate, Monte Carlo SE (three decimals), CV-selected rank median, and the CV-selected ranks as `rank: count` pairs in rank order.
6. **Table "Power floor per statistic"**, keyed by statistic: floor, maximum rate, effect at the maximum, construction maximum, informative from (`none` when null).
7. **The three `statements`**, verbatim, as bullets in `delta`, `angle`, `shape` order.
8. **Table "Construction beside this design"**, one row per `calibration_realized` quantity beside its `adni_reference` value:
   - AUROC mean;
   - AUROC q05–q95 beside the range;
   - first component |ρ| with phase;
   - CV-selected ranks beside the rank;
   - eigengap;
   - `angle` null q95;
   - the p180 and NMR phase offsets beside the injected and other block's.

   Then the `adni_reference` keys without a construction counterpart (design columns, phase share, p-values, offset counts), with `n/a` in the construction column. Each row names its committed source from the D4 map. Construction values are printed at six significant digits (`_fmt`), reference values as recorded.

The section prints no sentence of its own beyond the lead. The limits are measurement rules 6 to 9, printed in the reading-rules section.

### D6. Summary, preamble, provenance, reading rules, reproduction

- **Summary.** After the primary's reading bullets, a paragraph: "MOTCO's operating characteristics at this design (`OPERATING_CHARACTERISTICS_SOURCE`, <section ref>), read under `OPERATING_CHARACTERISTICS_READING_RULES` (<section ref>): verdict `non_rejections_uninformative`. Its statements, verbatim:" Then the three statements as bullets. Every later summary paragraph is unchanged.
- **Preamble.** Adds `adni-operating-characteristics` to the change list and "the operating characteristics MOTCO measured at this design under `READING_RULES` and `OPERATING_CHARACTERISTICS_READING_RULES`" to the reading clause.
- **Provenance.** The inputs table gains the copy's row. The versions and revisions tables are per manifest and unchanged (45 manifests).
- **Reading rules.** After `READING_RULES`, the heading `OPERATING_CHARACTERISTICS_READING_RULES`, then this lead line, then the nine rules numbered: "Binding for every reader of the result after MOTCO's measurement at this design (`OPERATING_CHARACTERISTICS_READING_RULES`, decided by `adni-operating-characteristics` after every run here; it changes no constant, record or status), after `READING_RULES`, cited as \"measurement rule N\":". Eight lists in all.
- **Reproduction.** A paragraph and a code line: the `git show` copy command at the pinned commit, and MOTCO's report path at that commit for the run itself.

### D7. The layout gate needs no logic change

`REPORT_SECTIONS` gains "Operating characteristics", so every committed report fails `_check_report_layout` at the section gate:
- the 2026-11-02-2 report: absent "Operating characteristics";
- the earlier reports: absent that and their older absences.

They stop before any input gate, naming `git log -1 --format=%H -- <report>`. The 2026-11-02-2 report checks at 67567e2, and the docstring lists it with the other five. The variant gate's logic stays. Its scenarios move to synthetic fourteen-section reports, since no committed report reaches it any more.

### D8. Report name and timing

The report is written from the committed outputs on the clean tree at the implementation commit, the day the change is implemented, under that day's next free name: `motco-adni-2026-11-02-3.md` if on 2026-11-02, otherwise `motco-adni-<date>.md`. Write mode never picks an ordinal itself, so it is passed with `--out`. It is checked with `--check` and committed alone.

### D9. Documentation

- **`AGENTS.md`:**
  - the status paragraph (the change and its section);
  - step 6 (146 inputs, the decision copy, gate 6, fourteen sections, eight rule lists, thirteen flags, the 2026-11-02-2 report as an earlier layout at 67567e2);
  - constraint 1 (the copy among committed aggregate files);
  - constraint 5 and "Flag and ask" (the two constants, with their values in short);
  - Layout (`references/`, the report entries, the constants);
  - "Data & domain notes" (one sentence: rule 3 measured at this design, the primary only).
- **`README.md`:** the report section and the layout.
- **Docstrings:** the `constants.py` module docstring's decided constants, and `render_report`, `_load_report_inputs`, `run_report`, `_check_report_layout` and the `report` CLI help.

## Risks / Trade-offs

- **[Two wordings side by side]** The report prints "(reading rule 3: no power statement exists at this design)" in the primary's reading bullets, then the measured statements. → Measurement rule 2 reads the clause explicitly, and the summary paragraph follows the bullets directly. A reader sees the predeclared sentence, then what supersedes its reason.
- **[Numbers in the rules not checked at run time]** Rules 3 to 6 quote values from the decision file. Once implemented, a task checks each against the file. The section beside them prints the file's values, so a typo would show on reading. The file is hash-pinned, so the values cannot drift.
- **[Upstream re-issue]** MOTCO may re-run or amend the measurement. → The citation is pinned by commit and sha256, and citing a new run is a new change. The copy keeps the report checkable even if MOTCO's history moves.
- **[Primary re-issued, e.g. by a pin move]** → Gate 6 stops on the first `adni_reference` key that differs, naming it. A pin-move change then decides whether the measurement still applies.
- **[Rounding at a boundary]** A committed value could round to the recorded one only by a hair. → The decimals are MOTCO's own, and the spike confirmed every key on the committed tree. A future boundary failure names both values.
- **[The construction's geometry differs from this design's]** Rank 19 against 8, eigengap 0.330 against 0.744. → This is a scientific limit, not a code risk. Measurement rule 6 carries it, and the construction table prints it.
- **[Report runtime]** One extra 76 KB JSON read and a handful of comparisons. Negligible.

## Migration Plan

1. Implement on the branch.
2. Verify on the committed tree. Then verify the failure modes on synthetic edits in a scratch copy (one byte of the copy; an `adni_reference` key; an absent copy; a fourteen-section report with three variants).
3. Commit the implementation.
4. Write the report on the clean tree, check it and commit it alone.
5. Archive, sync the `case-study-report` spec, then open the PR.

Rollback is a revert of the branch's commits: no step output changes, and the earlier reports check at their own revisions.
