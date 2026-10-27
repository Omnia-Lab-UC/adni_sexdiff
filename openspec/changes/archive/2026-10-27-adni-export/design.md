# Design

## Context

See `proposal.md` for the rule and `spike.md` for every number. The current state that shapes the approach:

- **The stub and the CLI.** `run_export` is a stub in `src/adni_sexdiff/data.py`; its docstring already states the output contract. `cli.py` exposes `export --cleaned-dir --cohort-dir --out-dir --force`.
- **Helpers from `clean` and `cohort`.** `_sha256_file`, `_git_revision`, `_software_versions`, `_write_manifest`, `_finalize_output_dir` and `_count_deviations` are reused unchanged. The raw-input helpers are not needed: the export reads no data-root file.
- **The inputs.** `results/cleaned/<platform>/clean_manifest.json` records `outputs.<name>.sha256` for `P180.csv` and `NMR.csv`; `results/cohort/cohort_manifest.json` records `outputs.cohort.csv.sha256` and, under `inputs.clean`, the clean hashes it saw. `cohort.csv` has the columns of `COHORT_COLUMNS` (`rid`, `sex`, `stage`, `dx_bl`, `protocol`, the five covariates, `visit`, `p180`, `nmr`), sorted by `rid`. The cleaned tables are keyed by `RID`.
- **MOTCO 0.10.0.** `analyze_trajectories` takes blocks in the units supplied with transform `identity`, requires finite values, z-scores every feature over all participants and concatenates the blocks unweighted; `TrajectoryAnalysisParams` has no block weight. Collinear features are fine for its PLS.
- **Ignore rules.** `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` already ignore `results/motco_input/**/*.csv` and keep `*manifest*`.

## Goals / Non-Goals

**Goals:**
- Blocks that are the measurement in declared units, with every feature traceable from the cleaned column to its status and floor.
- Every check that `analyze` would otherwise discover late (hash chain, row alignment, finiteness) done here, before anything is written.
- The run offset and the block balance visible in the manifest, so the analyze and diagnostics proposals and the report start from recorded numbers.

**Non-Goals:**
- Any correction of the run offset, any block weighting, any sensitivity variant, any MOTCO setting.
- Reading the Nightingale dictionary at run time (the spike's cross-check is the evidence for the name marks).
- A test framework. Verification is the workstation run against the spike, a rerun, and targeted failure checks on scratch copies.

## Decisions

**D1. The scientific constant and its predeclared counts as plain literals in `constants.py`.**

```python
EXPORT_FEATURE_RULE: dict[str, dict] = {
    "membership": {
        "p180": {"derived": {}},                       # every cleaned metabolite enters (µM concentrations)
        "nmr": {"derived": {                           # name marks; every other cleaned column is a concentration
            "percentage": ("endswith", "_PCT"),
            "ratio": ("contains", "_BY_"),
            "degree": ("equals", "UNSATURATION"),
            "size": ("endswith", "_SIZE"),
        }},
    },
    "scale": {
        "transform": "log2(x + floor)",
        "floor_quantile": 0.05,                        # per metabolite, over the exported participants
        "floor_method": "linear",                      # numpy's default quantile interpolation
        "motco_transform": "identity",
    },
}
```

`EXPORT_EXPECTED_COUNTS` holds the spike's numbers: participants 1501 and the sex × stage cells; per platform cleaned / kept / derived-by-family, zero cells, metabolites with zeros, floors not positive, non-finite cells, metabolites with |d| > 1; missing covariate values 0. Conventions: `EXPORT_BLOCKS = ("p180", "nmr")` (the block order passed to MOTCO), `EXPORT_FEATURE_STATUSES = ("kept", "derived")`, `EXPORT_COVARIATE_COLUMNS = tuple(ANALYSIS_COVARIATES)`.

Alternative considered: a list of the 80 derived column names. Rejected: the marks are the rule (a percentage, a ratio, a degree, a size), the list would be the result, and the predeclared family counts catch any drift of the marks against a new column set.

**D2. Membership by name marks, with the dictionary check in the spike.**
`export` reads only `results/`. The spike reads the dictionary once and reports that every mark-matched column has a non-concentration unit and every other column a concentration unit, for all 245. A fresh NMR download is its own change and reruns the spike. At run time the family counts are checked against `EXPORT_EXPECTED_COUNTS`: a renamed or added column changes `kept` or a family count and becomes a finding.

**D3. One scale for both blocks: `log2(x + floor)`, floor = the metabolite's 5 % quantile over the exported participants.**
Why a floor at all: a log without one amplifies the near-zero region of the large-VLDL subclasses and the ketone bodies into left tails (spike: 23 NMR metabolites with skew < −1 and 10 with |z| > 8 under `log2(x + min/2)`), and `log2(x + 1)` leaves most metabolites nearly linear (46 of 133 p180 and 129 of 165 NMR medians are below 1). Why the 5 % quantile: it is label-blind, scale-equivariant (a change of units moves it with the data), computed from the exported rows like the template's `k`, and it gives the flattest shape of the candidates (spike: p180 1 metabolite with |skew| > 1 and 0 with |z| > 8; NMR 3 and 1). Why not the generalized log: same counts, one more function to explain. Why not raw: 46 and 43 skewed metabolites and 12 and 4 with |z| > 8, and MOTCO's pooled z-scoring then hands those points their leverage. Why one rule and not per platform: the metabolites of both platforms are concentrations with multiplicative error, and one rule is one sentence in the methods.

Why not winsorize or remove outliers: both change the measured geometry, neither is in `CLEAN_OPTIONS`, and MOTCO's doctrine is to analyse the units supplied. Why the floor is computed over the exported participants and not the cleaned table: the export is per cohort, so a later arm recomputes its own floors from its own rows.

Trade-off accepted: for the three zero-carrying ketone bodies the floor is 0.14 to 0.39 of the median, so the low end is compressed; the feature table records floor over median for every metabolite.

**D4. The run offset is recorded, never corrected.**
The manifest and the feature tables carry, per block and per metabolite, the standardized mean difference between phases on the rule's scale and the correlation of the first two principal components with phase. The export does nothing else with phase. Per-run centering or scaling was considered and rejected: the runs differ in stage composition (EMCI and SMC only in ADNI-GO/2, LMCI mostly ADNI-1), so per-run centering subtracts part of the stage effect from one run and adds it to the other. A batch model with stage in the design uses the label upstream of the permutation test, which MOTCO documents as forbidden. The remedy is MOTCO's: `phase` is a declared covariate (0.8.0 adjustment of the stage means) and `covariate_latent_adjustment = "stage"` is the sensitivity the roadmap allows; both are the analyze proposal's.

**D5. Block balance accepted and recorded.**
Under the rule the p180 share of the unit-variance budget is 133 / 298. There is no label-blind count-matching for metabolites, and weighting is a property of the joint measurement that MOTCO's roadmap reserves for an opt-in setting with its own Type I check. The manifest records the shares and the reading rules of the analyze proposal must carry them.

**D6. Files and columns.**
- Blocks: `rid` first, then the kept metabolites in cleaned-column order under their cleaned names. Values are written by pandas' default float formatting (shortest round-trip), which is deterministic for equal inputs and library versions.
- `metadata.csv`: `rid`, `sex`, `stage` (labels CN / MCI / AD; `analyze` passes `STAGE_LABELS` as the explicit stage order).
- `covariates.csv`: `rid` then `EXPORT_COVARIATE_COLUMNS`, copied from `cohort.csv` unchanged (`apoe4` and `statin` as integers, `phase` as a string); the coding lives in `ANALYSIS_COVARIATES`, which the manifest copies from the cohort manifest's `settings`.
- `features_<platform>.csv`: `feature`, `family`, `status`, `zero_cells`, `median`, `floor`, `floor_over_median`, `skew_raw`, `skew_transformed`, `max_abs_z_transformed`, `phase_d`; derived rows carry the raw columns only. Skew is pandas' bias-corrected skew; |z| uses the population standard deviation, as the spike does.
- Row order: `cohort.csv` order restricted to both flags, which is ascending `rid`.

**D7. Manifest layout as in `cohort`.**
- Common keys: `step` (`export`), `created_at`, `versions`, `git_revision`.
- `inputs`: `clean` (per platform the manifest's sha256 and the table's sha256, observed equal to recorded), `cohort` (the manifest's and `cohort.csv`'s sha256) and `chain` (the cohort manifest's recorded clean hashes equal the clean manifests').
- `settings`: `EXPORT_FEATURE_RULE` verbatim, `blocks` (order), `sample_column`, `group_column` with `GROUP_VALUES`, `stage_column` with `STAGE_LABELS`, `covariates` (name, coding, levels, from the cohort manifest), `covariates_applied: false`, `motco_transform: identity`, `units: "log2(x + floor)"`.
- `counts`: `participants`, `sex_stage`, `features` (per platform: cleaned, kept, derived by family), `zero_cells`, `metabolites_with_zeros`, `floors_not_positive`, `non_finite`, `missing_covariate_values`, `block_shares`, `shape` (per block: the six counts of the spike's table), `spectrum` (per block: PC1, PC1-3, PC1-10 shares, effective rank, numerical rank), `phase_offset` (per block: median and max |d|, counts above 0.5 and 1, |corr| of PC1 and PC2 with phase).
- `expected`, `deviations`, `outputs` (bytes, sha256, `participant_level`), `findings`.
No `RID` appears in any key or value; verified by a `grep` at apply.

**D8. Stops and findings.**
- Stops, before anything is written: an absent input or manifest; a hash mismatch; a chain mismatch (named with the `cohort` command); a both-flagged participant absent from a cleaned table; a duplicated `rid`; a non-positive floor; a non-finite exported cell; a `sex` outside `GROUP_VALUES`, a `stage` outside `STAGE_LABELS` or a missing covariate value (none expected: `cohort` already stops on them, but the export does not trust that); an existing output directory without `--force`.
- Findings: each deviation from `EXPORT_EXPECTED_COUNTS`.
Rationale: everything that would make `analyze` fail or silently change is checked where it is cheapest to name.

**D9. The spike script is committed.**
`scripts/spike_export_inventory.py` stays beside the cohort spike so the numbers can be regenerated on any machine with a data root, and so the dictionary cross-check can be rerun after a new download.

**D10. No cluster script.**
`export` is a light step and runs on the login node after `cohort`, as AGENTS.md says. Each machine builds its own blocks; only `manifest.json` is synced.

## Risks / Trade-offs

- **The floor quantile is a convention** → stated here before any analysis, recorded per feature, and listed among the export sensitivity variants a later change registers (raw, `+1`, generalized log). It is never tuned on a result.
- **Excluding the derived NMR columns departs from the 2022 study** → the all-245 export is the first registered sensitivity variant; the proposal states the departure and its reason.
- **The p180 block's first axis is the run** (|d| median 1.12, PC1 correlation 0.73) → recorded here; the analyze proposal must pass `phase` as a covariate, decide the `stage` latent adjustment as a sensitivity, and the diagnostics must correlate every component with phase. A latent axis that tracks phase is a reading-rule matter, not an export fix.
- **NMR carries 55 % of the joint matrix** → recorded; MOTCO's weighting is the proper remedy, opt-in and not yet validated.
- **Half-LOD imputations in p180** (1,651 points, the ADNI-GO/2 UPLC kit at the LOD itself) sit as left clusters under the log → the floor bounds their leverage (0 metabolites with |z| > 8), and the feature table's skew and |z| columns show where they are.
- **A new NMR download renames or adds a column** → the family counts deviate and become a finding; the spike's dictionary check is rerun by that download's own change.
- **Collinear NMR concentrations** (totals are sums of subclasses) → PLS tolerates exact collinearity; the manifest records the numerical rank so the diagnostics can see it.

## Migration Plan

1. Land the constants, `run_export`, the spike script, the docstrings and the docs. No existing default changes.
2. On the workstation, run `uv run adni-sexdiff export`. Compare the manifest's counts with `spike.md`, then rerun with `--force` and compare the CSV hashes.
3. Commit `results/motco_input/manifest.json` only, naming it and why it is aggregate.
4. Cluster: when the deploy key and the data copy exist, run `clean`, `cohort` and `export` there (the first through sbatch, the others on the login node). Pull with `scripts/sync_results.sh` and compare the manifests' counts.
5. Rollback: the outputs are additive under `results/motco_input/`. Reverting the constant returns `export` to a stub.
