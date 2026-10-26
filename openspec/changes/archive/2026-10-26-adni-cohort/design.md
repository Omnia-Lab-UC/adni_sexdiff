# Design

## Context

See `proposal.md` for the rules and `spike.md` for every number. The current state that shapes the approach:

- **The stub and the CLI.** `run_cohort` is a stub in `src/adni_sexdiff/data.py`. `cli.py` already exposes `cohort --cleaned-dir --data-root --out-dir --force`.
- **Helpers from `clean`.**
  - `require_raw_files`, `hash_raw_file` and `check_known_repairs`, together with `RAW_INPUT_SHA256` and `KNOWN_RAW_FILE_REPAIRS`. The registry already holds the medication table and the three metabolomics files the cohort reads; it lacks ADNIMERGE.
  - `_git_revision`, `_software_versions`, `_write_manifest`, `_finalize_output_dir`, which the cohort reuses unchanged.
- **The clean outputs.** `results/cleaned/<platform>/clean_manifest.json` records `outputs.<name>.sha256` for `P180.csv`, `p180_runs.csv` and `NMR.csv`. The cleaned tables are keyed by `RID`, one row per participant. metabo_adni's merge drops visit codes, so the sample visit is known only from the raw files.
- **Ignore rules.** `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` already treat `results/cohort/*.csv` as participant-level except `stage_counts.csv`, and `results/**/*.tmp/` as ignored.
- **MOTCO 0.10.0.** `TrajectoryDataset` treats a covariate as categorical when it is listed in `categorical_covariates` or when its dtype is not numeric. It applies `missing_covariates="error"` by default.
- **The data root.** On this workstation, ADNIMERGE now resolves through `ADNI_adnimerge_20170629_QT-freeze.csv -> Clinical/ADNI_adnimerge_20170629_QT-freeze.csv`, with the hash unchanged.

## Goals / Non-Goals

**Goals:**
- One participant table that `export` can restrict to the intersection and later arms can restrict otherwise, with no cohort change.
- Every rule visible in the manifest as applied, every count checked against the spike, and every stop explained by column and count.

**Non-Goals:**
- Any MOTCO setting, the group order, any feature rule, any use of the metabolite values.
- Repairing or re-deriving anything metabo_adni produced.
- A test framework. Verification is the workstation run against the spike, a rerun, and targeted failure checks on scratch copies.

## Decisions

**D1. The three scientific constants as plain literals in `constants.py`.**

```python
COHORT_RULE = {
    "clinical_file": "ADNI_adnimerge_20170629_QT-freeze.csv",
    "baseline_visit": "bl",                       # ADNIMERGE VISCODE
    "sample_visit": "bl",                         # every raw record of the platform
    "sample_visit_columns": {"ADMCDUKEP180UPLCADNI2GO.csv": "VISCODE",
                             "ADMCDUKEP180FIAADNI2GO.csv": "VISCODE",
                             "ADNINIGHTINGALE2.csv": "VISCODE2"},
    "runs_without_visit": ("ADNI1",),             # p180 run taken as baseline
    "platforms": ("p180", "nmr"),                 # analysis cohort = intersection
}
STAGE_RULE = {"source": "DX.bl",
              "map": {"CN": "CN", "SMC": "CN", "EMCI": "MCI", "LMCI": "MCI", "AD": "AD"}}
ANALYSIS_COVARIATES = {                           # order is the declared order
    "age":       {"file": "clinical", "column": "AGE", "coding": "numeric"},
    "education": {"file": "clinical", "column": "PTEDUCAT", "coding": "numeric"},
    "apoe4":     {"file": "clinical", "column": "APOE4", "coding": "categorical", "levels": (0, 1, 2)},
    "phase":     {"file": "clinical", "column": "ORIGPROT", "coding": "categorical",
                  "levels": ("ADNI1", "ADNI2GO"),
                  "map": {"ADNI1": "ADNI1", "ADNIGO": "ADNI2GO", "ADNI2": "ADNI2GO"}},
    "statin":    {"file": "medication", "column": "HMG CoA reductase inhibitors", "visit": "sc",
                  "coding": "categorical", "levels": (0, 1)},
}
```

`COHORT_EXPECTED_COUNTS` holds the spike's numbers: the cascade per set, sex × stage per set, the composition cells, the stage-source agreement (1498 / 2 / 1), phase-against-run off-diagonals (0), statin users (704) and missing covariate values (0). The rest are conventions: `COHORT_CLINICAL_FILE`, `COHORT_MEDICATION_FILE` (the existing `CLEAN_MEDICATION_FILE` name, reused), `COHORT_COLUMNS` (the `cohort.csv` column order) and `GROUP_VALUES = ("Female", "Male")`, which is a value check, not an order passed to MOTCO.

Alternative considered: tuples of names with the sources in code. Rejected, because the sources and codings are part of the decision (AGENTS.md: "set, order, coding and sources") and must be visible where the decision lives. The manifest copies the three dicts verbatim under `settings`.

**D2. Sample visits read from the raw files' visit columns, not added to `clean`.**
The cohort reads only `RID` and the visit column (`usecols`) of `ADMCDUKEP180UPLCADNI2GO.csv`, `ADMCDUKEP180FIAADNI2GO.csv` and `ADNINIGHTINGALE2.csv`, hashed through the raw-input helpers. A participant's visit set is the set of codes over all their records. The participant enters the platform set only if that set is exactly `{bl}`, or, for p180, if their run is `ADNI1`.

Alternative considered: `clean` writes a visit table beside `p180_runs.csv`. Rejected. It would modify the metabolomics-cleaning spec, require re-running `clean` and re-committing both manifests, all for a two-column read of files that are already registered.

**D3. `cohort.csv` holds the union of the platform sets, with flags.**
It has 1594 rows: 1501 with both flags, 91 p180-only and 2 NMR-only. Per-platform counts come from the same table. `export` keeps the rows with both flags. A future single-platform arm reads the same file.

Alternative considered: write only the intersection. Rejected, because the per-platform columns of `stage_counts.csv` would then need a second table or a second pass.

**D4. Stops, exclusions and findings.**
- **Stops**, before anything is written: a missing data-root file; an unrepaired known file; an absent clean manifest or a clean output hash mismatch; more than one `bl` row for a participant; a `DX.bl` outside `STAGE_RULE["map"]`; a `PTGENDER` outside `GROUP_VALUES`; an `ORIGPROT` outside the phase map; an absent statin column; a missing covariate value, including a participant with no `sc` medication row. Each message names the column or file and a count.
- **Exclusions**, counted in the cascade: the sample rule, and no ADNIMERGE `bl` row.
- **Findings**: an unknown input hash; each deviation from `COHORT_EXPECTED_COUNTS`; phase-against-run disagreements.

Rationale: a value outside the declared codings means the rule no longer describes the data, which needs a proposal, not a silent drop. The exclusions are exactly what the rule states. Deviations follow the template's rule: a finding, reported, never a stop.

**D5. Statin use from the `sc` row of the medication table.**
The table is filled at screening; the clean spike found almost every `bl` row empty. The cohort reads it with `dtype=str`. A cell is use when it is non-null and non-empty after stripping. Each participant has one `sc` row (2170 rows, 2170 RIDs); a duplicated `sc` row for a cohort participant stops the step. Screening precedes the baseline draw by weeks; the manifest records the visit used.

**D6. The coding lives in the constant, not in the CSV dtype.**
`cohort.csv` writes `apoe4` as `0`/`1`/`2`, `statin` as `0`/`1` and `phase` as a string. MOTCO would read the first two as numeric unless they are declared categorical. The `coding` field of `ANALYSIS_COVARIATES` is what `analyze` passes as `categorical_covariates`, and `export` copies the columns unchanged. Writing labels such as `e4_0` would change the CSV dtype but duplicate the decision in a second place. The analyze change binds the declaration; this change records the coding in `settings`.

**D7. `stage_counts.csv` in long format.**
Columns `set, sex, stage, dx_bl, phase, n`.
- **Set-level rows**: for `set` ∈ {`p180`, `nmr`, `intersection`}, every sex ∈ {`Female`, `Male`, `all`} × stage ∈ {`CN`, `MCI`, `AD`, `all`}, with `dx_bl = phase = all`.
- **Composition rows**: for `intersection`, every observed sex × stage × `dx_bl` × phase cell, with no margins and no zero rows (SMC × ADNI1 does not exist).

Rows are sorted by set, sex, stage, `dx_bl` order (`CN`, `SMC`, `EMCI`, `LMCI`, `AD`), then phase. One file keeps the committed-file list unchanged.

Alternative considered: a second committed file for composition. Rejected, because it would need a new exception in `.gitignore`, the sync filter and `AGGREGATE_EXCEPTIONS` for no gain.

**D8. Manifest layout as in `clean`.**
- **Common keys**: `step` (`cohort`), `created_at`, `versions`, `git_revision`, `data_root`.
- `inputs`:
  - `clean`: each manifest's own sha256, and each clean output with the hash observed equal to the one recorded.
  - `raw`: the `hash_raw_file` records annotated by `check_known_repairs`.
- `settings`: the three constants verbatim, plus `COHORT_COLUMNS`.
- `counts`: the cascade per set, sex × stage per set, composition, `stage_source` (agree / differ / missing), `phase_vs_run` (2 × 2), statin users, missing covariate values.
- `descriptives`: per sex × stage, n, age mean and sd, education mean and sd, APOE4 0/1/2 counts, phase counts, statin users.
- `expected`, `deviations`, `outputs` (bytes, sha256, `participant_level`), `findings`.

No `RID` appears in any key or value. Verified by a `grep` at apply.

**D9. Data-root layout: `Clinical/` beside `Metabolomics/`.**
Clinical tables live under `<root>/Clinical/` under their original names, with relative symlinks at the top level. The cohort reads top-level names, like `clean`. `rsync -a` replicates the layout to the cluster. A dangling symlink fails `require_raw_files` naming the file, because existence is checked through the link. README and AGENTS.md document it.

**D10. No cluster script.**
`cohort` is a light step and runs on the login node, as AGENTS.md says. Each machine builds its own `cohort.csv`, and only `stage_counts.csv` and the manifest are synced.

## Risks / Trade-offs

- **`analyze` reads `apoe4` / `statin` as numeric because the categorical declaration is missed** → D6 puts the coding in `settings`. The analyze proposal must pass it and record the declaration in its own manifest, so the two manifests can be compared. For a 0/1 `statin` the two codings give the same model; only `apoe4` differs.
- **Phase and stage composition stay correlated** (SMC and EMCI only in ADNI-GO/2), and covariates do not condition MOTCO's latent space by default → `stage_counts.csv` makes the composition visible per sex. The latent adjustment is named in the proposal as a decision for analyze. The CN / LMCI / AD arm is predeclared as out of scope here.
- **metabo_adni averages replicates across visits** (upstream behaviour 4), so a participant with `bl` and non-`bl` NMR records has a mixed value → the sample rule excludes any participant whose visit set is not `{bl}`. Today that is the one screening-only participant; 0 have mixed sets.
- **A fresh ADNIMERGE or medication download changes counts** → the hash finding and the count deviations appear together in the manifest. The rules do not move without a proposal.
- **The 2017 freeze predates later diagnosis corrections** → accepted for comparability with the 2022 study and because the baseline values used here (age, education, APOE4, enrollment category) are fixed at enrollment. A fresh download is its own change.
- **Small cells in `descriptives`** (e.g. APOE4 = 2 among female CN: 3) → these are aggregate counts in a 1501-person cohort with no quasi-identifier beside them. They are needed for the report's cohort table. Nothing is suppressed, as in the clean manifests.
- **Exact column name with spaces** (`HMG CoA reductase inhibitors`) → an absent column stops the step naming it (D4), so a renamed column cannot silently become "no statin".

## Migration Plan

1. Land the constants (with `RAW_INPUT_SHA256` gaining the ADNIMERGE hash), `run_cohort`, the docstrings and the docs. No existing default changes.
2. On the workstation, run `uv run adni-sexdiff cohort`. Compare the manifest's counts with `spike.md`, then rerun with `--force` and compare the output hashes.
3. Commit `results/cohort/stage_counts.csv` and `results/cohort/cohort_manifest.json` only, naming them and why they are aggregate.
4. Cluster: when the deploy key and the data copy (including `Clinical/` and its symlink) exist, run `cohort` on the login node after `clean`. Pull with `scripts/sync_results.sh` and compare.
5. Rollback: the outputs are additive under `results/cohort/`. Reverting the constants returns `cohort` to a stub; the data-root move is undone by moving the file back over its symlink.
