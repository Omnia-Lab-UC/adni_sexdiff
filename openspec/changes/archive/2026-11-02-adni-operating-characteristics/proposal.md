# Proposal

## Why

`READING_RULES` rule 3 reads the primary's `angle` and `shape` non-rejections as uninformative because "no power statement exists at this design (n = 1501, 298 metabolites, six design columns)". Four sensitivity rule sets repeat the clause, and so does every committed `summary.md`, comparison document, `diagnostics.md` and report.

On 2026-11-02 MOTCO measured size and power at this design: change `adni-design-operating-characteristics`, PR #71, merged at `0d726922`. MOTCO's code did not change; the version stays 0.13.0.
- **The run.** 7,000 units, R = 500 per cell at 999 permutations, 0 failures.
- **The construction.**
  - This design's sex × stage cells, with six covariate design columns of this design's kinds, a phase-like binary nuisance among them.
  - The stage signal calibrated to this design's held-out AUROC.
  - The primary's settings: `analyze_trajectories` with the covariates, rank floor 2, net displacement, cross-validation 3 × 4 folds, 5 repeats, `max_components` 20, `random_state` 1203, no latent adjustment, no residual correction.
- **The verdict:** `non_rejections_uninformative` (`results/adni-design-2026-11-02/run/adni_design_decision.json`, sha256 `4cb482e7…`, not indicative).
  - Size holds at both controls, at 0.034 to 0.068 against the bound 0.0695.
  - No statistic reaches the 0.80 power floor. `delta` reaches at most 0.530, at the strongest magnitude construction. `angle` and `shape` stay near the null rate (at most 0.076 and 0.062).

MOTCO lists the follow-up as work for this repository: "`adni_sexdiff`: confirm reading rule 3, citing `adni_design_decision.json`, in that repository's own change." This is that change.

Three parts of the current reading no longer match what is known:
- **Rule 3's reason.** The rule says no power statement exists at this design. One now exists.
- **`delta`.** Rule 3 covers `angle` and `shape` only. The measurement shows a `delta` non-rejection is uninformative too, which applies to the primary's `delta` (p 0.1116).
- **Rule 5's validation.** The rule cites validation at three design columns and n = 80. Size is now measured at six design columns and n = 1501.

## What Changes

- **The predeclared rules stay as written** (the user's choice for this proposal):
  - `READING_RULES`, every sensitivity's rule set and every reading sentence (`_statistic_reading_line` and the status lines);
  - every step's output.

  The rules were written before any run, and a rule rewritten after the results would read them anew. Rewriting them would also mean rerunning 16 MOTCO analyses and 10 diagnostics only to change prose. Instead, a new rule list states what the measurement adds, and only the report prints it. No step reruns, and no data root or data machine is needed.
- **New scientific constant `OPERATING_CHARACTERISTICS_READING_RULES`** (cited as "measurement rule N"). It confirms rule 3, extends it to `delta` (the user's choice for this proposal) and carries the measurement's limits. Its nine rules, verbatim:
  1. MOTCO measured size and power at this design after every analysis here had run (MOTCO change `adni-design-operating-characteristics`, PR #71, commit 0d72692, 2026-11-02; `adni_design_decision.json`, verdict `non_rejections_uninformative`, not indicative). The measurement changes no constant, no record and no status: `READING_RULES`, every sensitivity's rules and every reading sentence of the generated documents stand as written before any run, and this list states what the measurement adds to them.
  2. Reading rule 3 is confirmed by a measurement, no longer by the absence of one. Where a rule or a reading sentence says that no power statement exists at this design, it records what was known when it was written; for the primary's construction a power statement now exists, and it is this list.
  3. `angle` and `shape` non-rejections are uninformative, as reading rule 3 states. At this design the orientation and shape constructions, up to their maximum (e = 1), left `angle` at most 0.076 and `shape` at most 0.062 (R = 500), near the null rate and far below the 0.80 power floor.
  4. Reading rule 3 extends to `delta`: a `delta` non-rejection is uninformative too, not evidence that the sexes' trajectories agree. `delta` reached at most 0.530 (R = 500), below the 0.80 floor, at the magnitude construction's maximum: one sex's stage effect twice the other's, which raised the held-out stage AUROC to 0.683 against this design's 0.600. The primary's `delta` non-rejection is read so. Reading rule 4 on a `delta` rejection is unchanged.
  5. Size held at both controls. The six rejection rates of the anchor and of the translation control lie at 0.034 to 0.068 against the one-sided bound 0.0695 (R = 500), and `delta` was conservative (0.034 at both). The Type I control that reading rules 3 and 5 cite from the validated designs (three design columns, n = 80) is now measured at this design too: six design columns, a phase-like binary nuisance that the covariate-blind basis follows, n = 1501.
  6. The measurement is a structural analogue, not a replication of this analysis, and no statement about a metabolite follows from it.
     - Its blocks are InterSIM methylation and expression (367 and 131 features, 74 % / 26 %) in place of NMR and p180 (165 and 133, 55 % / 45 %), and it ran 999 permutations against 9999 here.
     - It matched this design's held-out stage AUROC (0.606 against 0.600), a first component that follows phase (median |ρ| 0.578 against 0.542) and the size of the p180 run offset (median |d| 1.126 against 1.12).
     - It did not match the latent geometry. The offset is the injected block's whole first axis (PC1 |r| 0.994 against 0.73). The cross-validation selected the cap of 19 components in 494 of 500 anchor units, against this design's 8. The stage means were less one-dimensional (eigengap 0.330 against 0.744), and the `angle` null was wider (q95 51.0° against 35.4°).

     The `angle` and `shape` rates are those of that geometry.
  7. The measurement covers the primary's construction only: one table (n = 1501), the CV-selected rank, no latent adjustment, the rule's export. The latent arm, the export variants, the CN / LMCI / AD arm (n = 1130) and the forced ranks were not measured, so their size and power stay inferred. Their rules' statements that no power statement, or no Type I or power check, exists at this design hold for them as written. A sensitivity's non-rejection stays no more informative than the primary's, which is now measured as uninformative.
  8. The measured size of the primary's construction is not the size of any sensitivity, and no sensitivity's status is reread from it. A `delta` rejection in a sensitivity stays the dependence its own rules name, read against the primary only.
  9. The measurement ran MOTCO 0.13.0's code without residual correction, as the primary ran: MOTCO 0.11.0 to 0.13.0 add design-guidance tools and the opt-in `residual_correction`, which, unset, leaves the 0.10.0 analysis path unchanged. The pin stays v0.10.0, and a pin move or a residual correction is its own change. The measurement is cited for the analysis it was calibrated against, its `adni_reference`, which `report` checks against the committed records.
- **New scientific constant `OPERATING_CHARACTERISTICS_SOURCE`**, the cited measurement, pinned:
  - repository `https://github.com/Omnia-Lab-UC/MOTCO`;
  - change `adni-design-operating-characteristics`, pull request 71;
  - commit `0d726922173188c4d74ce4b2f87f6a26e5fc548f`;
  - path `results/adni-design-2026-11-02/run/adni_design_decision.json`;
  - report `docs/reports/adni-design-2026-11-02.md`;
  - sha256 `4cb482e7e16b19278467d6929f6905d71a8aef332ae55fc07ac86a3c1eec3ea1`;
  - verdict `non_rejections_uninformative`.

  Citing another measurement is a new change.
- **A pinned copy of the decision file** at `references/motco_adni_design/adni_design_decision.json`, copied byte for byte from MOTCO at the pinned commit (76,057 bytes).
  - It is aggregate. It comes from synthetic data, and its `adni_reference` block holds aggregate values already in the committed outputs. It holds no participant value or identifier.
  - `references/` is a new top-level directory for committed third-party aggregate files the report cites. It is not a pipeline output, so `results/` and `scripts/sync_results.sh` are not involved.
- **The report** (`report`, change `adni-report`) reads the copy and gates it before anything is written:
  - the file is present, and its sha256 equals the constant's;
  - the file's `verdict` equals the constant's, and it is not indicative;
  - its `adni_reference` equals this repository's committed values at the decision's own digits (the spike below).

  New flag: `--operating-characteristics-dir`, default `references/motco_adni_design`, for thirteen flags.
- **A fourteenth section, "Operating characteristics"**, after "Axis diagnostics of the primary". It holds:
  - the source;
  - MOTCO's decision rule, verbatim;
  - the size readings, with the size sentence verbatim;
  - the power rates per target statistic and effect;
  - the three per-statistic statements, verbatim;
  - the construction beside this design, each reference value with the committed value it was checked against.

  Other sections change too:
  - **Summary:** the measured verdict and the three statements after the primary's reading.
  - **Preamble:** names this change.
  - **Provenance:** the copy and its source in the inputs.
  - **Reading rules:** an eighth list, `OPERATING_CHARACTERISTICS_READING_RULES`, after `READING_RULES`.
  - **Reproduction:** the copy command.

  The new sentences are the constant's rules and the decision file's own sentences, copied verbatim. No reading sentence of the steps changes.
- **The earlier-layout gate** stops on `reports/motco-adni-2026-11-02-2.md` by its thirteen sections, naming 67567e2, where it checks. The earlier reports stop the same way.
- **The next report** is written from the committed outputs on the clean tree, on the day the change is implemented, under that day's next free name (`motco-adni-2026-11-02-3.md` if on 2026-11-02). It is checked with `--check` and committed alone.

A read-only spike for this proposal compared the decision file with the committed files.
- **The source.** The file at MOTCO `0d72692` hashes to the value above, and so does the working copy.
- **The reference.** Every key of `adni_reference` equals the committed value at the decision's digits:
  - from the primary's `result.json`: rank 8, `cv_mean_auroc` 0.5995, the three p-values, the eigengap 0.744, the `angle` null q95 35.44, the six design columns, and the `phase[ADNI2GO]` reference value 0.5443;
  - from the export manifest's `counts.phase_offset` and `counts.features`: p180 1.12 / 80 / 133 / 0.73 and NMR 0.21 / 0 / 165 / 0.13;
  - from the primary diagnostics' `axis_correlations.csv`: `pls_0` against `phase`, 0.542;
  - the range 0.580 to 0.616: the lowest and highest `cv_mean_auroc` of the nine CV-selected analyses (the primary, the latent arm, the six variants, the CN / LMCI / AD arm).
- **The code path.** `git diff v0.10.0 v0.13.0 -- src/motco` changes the analysis path only by adding `residual_correction`, which defaults to `None`, then permutes the raw residuals as before and is omitted from the record.

Scientific constants introduced by this change, each with its value above, decided before any report quotes the measurement:
- `OPERATING_CHARACTERISTICS_READING_RULES` (nine rules);
- `OPERATING_CHARACTERISTICS_SOURCE` (the pinned measurement).

Conventions added: `OPERATING_CHARACTERISTICS_DIR` (`references/motco_adni_design`), `OPERATING_CHARACTERISTICS_DECISION` (`adni_design_decision.json`), the fourteenth entry of `REPORT_SECTIONS`, and the role `operating-characteristics` of `REPORT_INPUT_FILES`.

Out of scope, each its own change if wanted:
- A rewrite of `READING_RULES`, of a sensitivity's rule set or of a reading sentence, and a rerun of any step to print new wording.
- Moving the MOTCO pin (constraint 4) or adopting `residual_correction` (constraint 5).
- Operating characteristics of a sensitivity (the latent arm, an export variant, the CN / LMCI / AD arm, a forced rank). These are MOTCO measurements not yet run.
- Citing MOTCO's Phase 6 exit review (`phase6-exit-review`, in progress, not merged). It asks the case studies to cite it when they next re-issue, so a later report change adds the citation once the review is merged.
- Any reading of a sensitivity's status from the measured size (measurement rule 8).
- A copy of MOTCO's other run files (rates, strata, p-values, records), and figures.
- A rewrite of an earlier report, or a check of one with the new code.
- The cluster run (constraint 7).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `case-study-report`: these requirements change:
  - the inputs (the decision file; 146);
  - the content contract (the "Operating characteristics" section, fourteen sections);
  - every number pasted (the decision file's values at its digits);
  - the interpretive sentences (the decision file's sentences and the new rules, verbatim; no step sentence changes);
  - the reading rules carried (eight lists);
  - the check's layout gate (the 2026-11-02-2 report as an earlier layout).

  One requirement is added: the cited measurement is pinned and checked against the committed records.

## Impact

- `src/adni_sexdiff/constants.py`:
  - the two scientific constants and the two conventions;
  - `REPORT_SECTIONS` (fourteen) and `REPORT_INPUT_FILES` (the new role);
  - the docstring's list of decided constants.
- `src/adni_sexdiff/data.py`:
  - `_report_dirs` (the tenth directory);
  - `_load_report_inputs`: the presence, hash, verdict and reference gates, and the decision in the returned inputs and the provenance;
  - `render_report`: the preamble, the summary paragraph, the new section, the provenance rows, the eighth rule list and the reproduction line;
  - `_check_report_layout` and `run_report`, with their docstrings.

  The steps, `_statistic_reading_line`, the status lines and every other renderer are unchanged.
- `src/adni_sexdiff/cli.py`: `--operating-characteristics-dir` on `report` (thirteen flags).
- `references/motco_adni_design/adni_design_decision.json`: added and committed, aggregate.
- `reports/motco-adni-<date>[-<n>].md`: added and committed, aggregate. The six earlier reports are unchanged.
- `README.md` and `AGENTS.md`:
  - the status paragraph and step 6;
  - constraint 1's list of committed aggregate files (the copy);
  - constraint 5 and "Flag and ask" (the two constants);
  - the Layout entries (`references/`, the report flags).
- `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` are unchanged, since no participant-level output is added.
- No new dependencies, no MOTCO call, no numerics. Any machine with the Nix shell and the committed tree can run it.
- Workflow:
  1. Implement and verify on the committed tree and on synthetic edits in a scratch directory, then commit.
  2. Write the report on the clean tree, check it and commit it alone.
  3. Archive, then open the PR.
