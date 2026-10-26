# Proposal

## Why

`export` and `analyze` need one row per participant with sex, stage and covariates, and today `cohort` is a stub with all three of its scientific constants (`COHORT_RULE`, `STAGE_RULE`, `ANALYSIS_COVARIATES`) undecided. The clean manifests are committed, and the cohort spike of 2026-10-26 (`spike.md`, counts only) applied the rules below to them and to the clinical tables. The rules were settled in an explore session before any sex × stage count under them was looked at. Every number this proposal predeclares comes from that spike.

## What Changes

- **`COHORT_RULE` decided.**
  - Clinical table: the QT-PAD ADNIMERGE freeze `ADNI_adnimerge_20170629_QT-freeze.csv` (sha256 `e3eae046…`), the file the 2022 study (Front. Radiol., doi:10.3389/fradi.2022.782864) used. It now sits in the data root's archive as `Clinical/ADNI_adnimerge_20170629_QT-freeze.csv`, with a relative symlink under its own name at the top level, like the metabolomics files.
  - One row per participant: the ADNIMERGE row with `VISCODE == "bl"`.
  - Each platform's sample must come from baseline. Every raw record of the participant on that platform has visit `bl`: `VISCODE` in the ADNI-GO/2 p180 files, `VISCODE2` in `ADNINIGHTINGALE2.csv`. The ADNI-1 p180 files have no visit column and count as baseline (ADMC measured ADNI-1 baseline serum). This excludes 1 NMR participant whose only NMR sample is from screening (`sc`). `BIOMARK.csv` has no row at that visit, so their fasting status at the draw is unknown.
  - Platform sets: the cleaned participants of a platform that pass the sample rule and have an ADNIMERGE `bl` row (p180 1592, NMR 1503). The analysis cohort is their intersection, n = 1501. MOTCO requires every block's rows to match the metadata row for row, so the intersection is the only joint design.
  - No other exclusion. No exclusion depends on sex, stage or a covariate value. A missing covariate, a `DX.bl` outside the stage map, or a `PTGENDER` other than `Female` / `Male` stops the step, naming the column and the count. Nothing is imputed.
- **`STAGE_RULE` decided.** The source is `DX.bl` on the `bl` row, with the 2022 merge: `CN` → CN, `SMC` → CN, `EMCI` → MCI, `LMCI` → MCI, `AD` → AD. `DX.bl` is ADNI's enrollment category and is complete. Read as the diagnosis at the visit (a recorded change "X to Y" counts as Y), `DX` on the same row agrees with the mapped stage for 1498 of 1501. It differs for 2 and is missing for 1. The three stages are therefore the clinical diagnosis at baseline; SMC, EMCI and LMCI are ADNI enrollment strata.
- **`ANALYSIS_COVARIATES` decided**, in this order. Sources are the ADNIMERGE `bl` row unless stated. Missing policy `error`.

  | name | source | coding |
  |---|---|---|
  | `age` | `AGE` | numeric, years |
  | `education` | `PTEDUCAT` | numeric, years |
  | `apoe4` | `APOE4` | categorical, levels `0`, `1`, `2` |
  | `phase` | `ORIGPROT`: `ADNI1` → `ADNI1`; `ADNIGO`, `ADNI2` → `ADNI2GO` | categorical, 2 levels |
  | `statin` | `ADMCPATIENTDRUGCLASSES_20170512.csv`, column `HMG CoA reductase inhibitors`, the `sc` row: filled → `1`, empty → `0` | categorical, levels `0`, `1` |

  The grounds:
  - Age is a confounder of the metabolome.
  - Education is cognitive reserve: it shifts which diagnosis a given biology receives, and it differs by sex in this cohort (spike).
  - APOE is a lipoprotein gene and its ε4 frequency rises across stages. Coding it as categorical costs 1 df out of 1501 and doesn't assume homozygotes are additive; the 2022 study coded it numerically.
  - Phase is the p180 measurement run (spike: equal for 1501 of 1501) and the blood-draw era (2005–07 vs 2010–13) on both platforms. It can be estimated because CN, LMCI and AD occur in both phases. The 3-level `ORIGPROT` is not used because ADNI-GO's 114 participants are all EMCI and were measured in the ADNI-2 p180 run.
  - Statins are prescribed for cardiovascular risk, not AD. They have a strong direct effect on the lipids and lipoproteins both platforms measure, and their use differs by sex (women 41 %, men 52 % in the clean spike).
  - Deliberately not covariates:
    - Anti-dementia drugs: use follows from the diagnosis (anticholinesterases: CN 0 %, AD 87 %).
    - Thyroxine and antidepressants: they treat conditions linked to sex or stage.
    - BMI: weight loss is part of AD, and BMI is not in the data root.
    - Race, ethnicity, site: sparse levels, and site overlaps with phase.

    They remain candidates for `DIAGNOSTIC_VARIABLES` (axis-diagnostics proposal).
- **`cohort` implemented.** It reads the outputs of `clean` (each checked against its `clean_manifest.json` hash) and the visit columns of three raw metabolomics files. It also reads the clinical table and the medication table, all through the raw-input-integrity helpers (`RAW_INPUT_SHA256` gains the ADNIMERGE hash). It applies the three rules and writes `results/cohort/`:
  - `cohort.csv`, participant-level, already ignored: one row per participant in either platform set (1594). Columns: `rid`, `sex`, `stage`, `dx_bl`, `protocol`, the five covariates, `visit` (`bl`), and a flag per platform (`p180`, `nmr`). The intersection is the rows with both flags.
  - `stage_counts.csv`, aggregate, committed, long format `set, sex, stage, dx_bl, phase, n`. It holds sex × stage per platform set and for the intersection, plus, for the intersection, sex × stage × `dx_bl` × phase. This makes the EMCI share within MCI and the SMC share within CN visible for each sex and phase.
  - `cohort_manifest.json`, aggregate, committed: the rules as applied, input hashes, the exclusion cascade, the stage-source agreement, the phase-against-run check, covariate summaries by sex × stage, output hashes, expected against observed counts, findings. It contains no `RID`.
- **Predeclared counts** (`COHORT_EXPECTED_COUNTS`, from the spike). A deviation is a finding, printed and recorded, never silent:

  | set | n | Female CN / MCI / AD | Male CN / MCI / AD |
  |---|---|---|---|
  | p180 | 1592 | 254 / 329 / 140 | 230 / 470 / 169 |
  | nmr | 1503 | 237 / 310 / 126 | 223 / 449 / 158 |
  | intersection | 1501 | 237 / 310 / 125 | 223 / 448 / 158 |

  Also predeclared:
  - Cascade: NMR sample not at `bl` 1, no ADNIMERGE `bl` row 0.
  - Stage source: `DX` differs 2, missing 1.
  - Phase against p180 run: 0 disagreements.
  - Statin users in the intersection: 704.
  - Missing covariate values: 0.
  - The composition cells of `spike.md`.
- **Docs**:
  - `README.md`: the `cohort` section and the data-root layout with `Clinical/`.
  - `AGENTS.md`:
    - status and step 2: the inputs now include the raw files' visit columns and the medication table.
    - "Flag and ask": `COHORT_RULE`, `STAGE_RULE`, `ANALYSIS_COVARIATES` decided, with their values.
    - The data-root layout gains `Clinical/`; the clinical tables are named.
  - `constants.py` docstring and the `run_cohort` docstring.

Out of scope, each its own change:
- the CN / LMCI / AD-only sensitivity arm (n = 1130 in the spike). `cohort.csv` carries `dx_bl`, so it needs no cohort change.
- `covariate_latent_adjustment` and every other MOTCO setting (analyze proposal). Phase correlates with stage composition, so that proposal must decide whether covariates also condition the latent space.
- the group order passed to MOTCO (analyze).
- `EXPORT_FEATURE_RULE` (export).
- `DIAGNOSTIC_VARIABLES` (axis-diagnostics).
- a fresh ADNIMERGE download.
- medication classes beyond statins.
- the cluster data copy, which must replicate `Clinical/` (`rsync -a`).
- the metabo_adni upstream issues.

No count under these rules changes them.

## Capabilities

### New Capabilities
- `cohort-assembly`: the `cohort` step. It covers the baseline-sample rule, the platform sets and their intersection, the stage mapping, the covariates with their sources and codings, the participant table and its aggregate counts, and the manifest with its predeclared-count check.

### Modified Capabilities
<!-- None: raw-input-integrity's requirements already cover any raw file a step reads; the cohort step adds the ADNIMERGE hash to the predeclared registry without changing a requirement. -->

## Impact

- `src/adni_sexdiff/constants.py`:
  - Scientific, decided here: `COHORT_RULE`, `STAGE_RULE`, `ANALYSIS_COVARIATES`.
  - Predeclared: `COHORT_EXPECTED_COUNTS`.
  - Conventions: `COHORT_CLINICAL_FILE`, `COHORT_MEDICATION_VISIT`, `COHORT_VISIT_FILES`, `COHORT_COLUMNS`.
  - `RAW_INPUT_SHA256` gains the ADNIMERGE entry.
  - The docstring's undecided list loses the three names.
- `src/adni_sexdiff/data.py`: `run_cohort`, which reuses the raw-input, manifest and `.tmp` helpers of `clean`. `cli.py`: progress messages only; the flags exist.
- Ignore rules: none to change. `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` already treat `results/cohort/*.csv` as participant-level except `stage_counts.csv`, and `cohort_manifest.json` is not a CSV.
- New `scripts/spike_cohort_inventory.py`, the read-only spike that produced `spike.md`.
- Data root: `Clinical/` holds the ADNIMERGE freeze with its top-level symlink, moved on the workstation on 2026-10-26 with the hash unchanged. The cluster copy must replicate it.
- Dependencies: none.
