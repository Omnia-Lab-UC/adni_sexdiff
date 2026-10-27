# Proposal

## Why

`analyze` needs the two MOTCO blocks, the metadata and the covariate table, and today `export` is a stub with its one scientific constant, `EXPORT_FEATURE_RULE`, undecided. `clean` and `cohort` are committed (n = 1501). The export spike of 2026-10-27 (`spike.md`, aggregate only, `scripts/spike_export_inventory.py`) restricted the cleaned matrices to the cohort and summarised them under the rule below. The rule was settled in an explore session that looked at the blocks' units, families, distribution shape, structure and phase offset, never at a sex or stage difference. Every number this proposal predeclares comes from that spike.

## What Changes

- **`EXPORT_FEATURE_RULE` decided.** It has two parts, membership and scale.
  - **Membership.** A block holds the measured concentrations of its platform, each once.
    - `p180`: every cleaned metabolite enters (133, all µM concentrations).
    - `nmr`: a cleaned column enters if it is a concentration (mmol/l, µmol/l, g/l in the Nightingale dictionary): 165 columns, the 98 lipoprotein-subclass measures and 67 other concentrations. The 80 columns that are deterministic functions of other columns of the block are excluded with status `derived`: the 72 percentages (`_PCT`), the 4 ratios (`_BY_`), the degree of unsaturation (`UNSATURATION`) and the 3 particle sizes (`_SIZE`). The export recognises them by these name marks; the spike checked the marks against the dictionary's units column for all 245 columns (no disagreement). They add weight to the block, not measurement, they are re-derivable from it, and bounded proportions do not share the concentrations' scale.
  - **Scale.** One rule for both blocks: `log2(x + floor)`, where the floor of a metabolite is its 5 % quantile over the exported participants (linear interpolation). The floor is a per-metabolite constant computed without sex, stage or covariates, recorded per feature. MOTCO's unit transform is `identity`; MOTCO then z-scores every feature over all participants.
    - Not `log2(x + 1)`, metabo_adni's `--log2` and the 2022 study's choice: 46 of 133 p180 and 129 of 165 NMR metabolites have medians below 1, so a unit pseudo-count leaves them nearly linear and the transform metabolite-dependent.
    - Not a plain log or a half-minimum pseudo-count: the large-VLDL subclasses sit near zero in fasting serum (values down to 10⁻⁹), and a log turns them into left-tail outliers (23 NMR metabolites with skew < −1, 10 with a |z| above 8), worse than the raw scale.
    - Under the rule: p180 1 metabolite with |skew| > 1 and none with |z| above 8; NMR 3 and 1. The generalized log with the same constant gives the same counts; the floored log is stated because it is the simpler function.
    - Three ketone-body metabolites carry 41 true zeros. The floor handles them; no value is imputed or replaced. A metabolite whose floor is not positive stops the step (0 such metabolites).
    - No winsorizing, no outlier removal, no medication residualization, no per-run centering: the block is the measurement in the declared units, as the template's export is.
- **The p180 run offset recorded, not corrected.** On the same 1501 participants and the rule's scale, the standardized mean difference between phases (= p180 runs) has median |d| 1.12 over the 133 p180 metabolites (80 above 1; PC1 correlates 0.73 with phase), against 0.21 over the 165 NMR metabolites (0 above 1; 0.13). The p180 block's first axis is the run. Covariates are exported, not applied (AGENTS.md step 3), and per-run centering would be wrong here because the runs differ in stage composition (EMCI and SMC exist only in ADNI-GO/2), so centering would move stage signal between runs. The export manifest records the offset per block; the analyze proposal must address it (see out of scope).
- **Block balance recorded, not forced.** MOTCO 0.10.0 z-scores every feature and concatenates the blocks unweighted, with no block-weight parameter. The p180 share of the joint matrix is 133 / 298 = 0.446 under the rule (0.352 with all 245 NMR columns). The manifest records the shares.
- **`export` implemented.** It reads only `results/cleaned/` (`P180.csv`, `NMR.csv`, both `clean_manifest.json`) and `results/cohort/` (`cohort.csv`, `cohort_manifest.json`), checks every file against its manifest's hash and the cohort manifest's recorded clean hashes against the clean manifests, keeps the rows with both platform flags in `cohort.csv` order, applies the rule and writes `results/motco_input/`:
  - `p180.csv`, `nmr.csv`: participant × metabolite on the rule's scale, first column `rid`; participant-level, ignored.
  - `metadata.csv` (`rid`, `sex`, `stage`) and `covariates.csv` (`rid`, `age`, `education`, `apoe4`, `phase`, `statin`, copied unchanged with their codings recorded in the manifest); participant-level, ignored.
  - `features_p180.csv`, `features_nmr.csv`: one row per cleaned metabolite with its family, status (`kept` / `derived`), zero cells, median, floor, floor over median, skew raw and transformed, largest |z| transformed and the phase offset `d`; aggregate per feature, ignored with the other CSVs, regenerable.
  - `manifest.json`: input hashes and the chain check, the rule as applied, block order, column names, stage order, group values, the covariate codings, n per sex × stage, feature counts per status and family, zero cells, floors not positive, non-finite cells, block shares, per-block distribution-shape counts, spectra and phase offsets, expected against observed counts, output hashes, findings; aggregate, the only committed file.
- **Predeclared counts** (`EXPORT_EXPECTED_COUNTS`, from the spike). A deviation is a finding, printed and recorded, never silent:

  | quantity | p180 | nmr |
  |---|---|---|
  | cleaned metabolites | 133 | 245 |
  | kept | 133 | 165 |
  | derived: percentage / ratio / degree / size | 0 / 0 / 0 / 0 | 72 / 4 / 1 / 3 |
  | zero cells, metabolites with zeros | 0, 0 | 41, 3 |
  | floors not positive | 0 | 0 |
  | non-finite cells after the transform | 0 | 0 |
  | metabolites with phase \|d\| > 1 | 80 | 0 |

  Participants 1501: Female CN / MCI / AD 237 / 310 / 125, Male 223 / 448 / 158; missing covariate values 0. The continuous summaries (median |d| 1.12 and 0.21, PC1 correlations 0.73 and 0.13, the shape counts, the spectra, the shares) are recorded in the manifest and quoted in `spike.md`; the report reads them from the manifest.
- **Docs**: `README.md` (status, the `export` section); `AGENTS.md` (status, step 3, "Flag and ask" with `EXPORT_FEATURE_RULE` decided and its value, the "Data & domain notes" gaining the run offset as a known property of the p180 block, the Layout entry for `scripts/`); the `constants.py` docstring and the `run_export` docstring.

Precedent and departures. The 2022 study (Front. Radiol., doi:10.3389/fradi.2022.782864) used all 245 NMR columns, `+1` then `log2`, z-scoring, winsorizing at ±3 and Mahalanobis outlier removal on p180, and medication residuals. This export keeps concentrations only, uses a per-metabolite floor instead of `+1`, and leaves z-scoring to MOTCO and every other transform out, as `CLEAN_OPTIONS` already decided.

Out of scope, each its own change:
- Any correction of the p180 run offset. The analyze proposal decides how `phase` enters MOTCO: as a covariate of the stage means (decided by `adni-cohort`) and whether `covariate_latent_adjustment = "stage"` runs as the sensitivity MOTCO's roadmap allows. The axis-diagnostics proposal must put `phase` among `DIAGNOSTIC_VARIABLES`.
- Block weighting, which is MOTCO's (roadmap item 5, opt-in, with its own Type I check).
- Export sensitivity variants, registered after the primary analysis as the template did: all 245 NMR columns, the raw scale, `log2(x + 1)`, the generalized log, and the CN / LMCI / AD arm (which needs no export change beyond a cohort filter).
- Every MOTCO setting (`ANALYSIS_PERMUTATIONS`, `ANALYSIS_SEED`, `ANALYSIS_RANK_FLOOR`, the group order).
- Re-running `clean` or `cohort`; a fresh LONI download; the cluster run.

No number under this rule changes it.

## Capabilities

### New Capabilities
- `motco-input-export`: the `export` step. It covers the inputs and their hash chain, the exported participants, block membership by family, the floored log scale, the label-blind constraint, the export contract (blocks, metadata, covariates, feature tables), the manifest with its recorded structure and phase offset, the predeclared-count check and determinism.

### Modified Capabilities
<!-- None: cohort-assembly and metabolomics-cleaning are read, not changed; raw-input-integrity is untouched because the export reads no data-root file. -->

## Impact

- `src/adni_sexdiff/constants.py`:
  - Scientific, decided here: `EXPORT_FEATURE_RULE`.
  - Predeclared: `EXPORT_EXPECTED_COUNTS`.
  - Conventions: `EXPORT_BLOCKS` (block order `p180`, `nmr`), `EXPORT_FEATURE_STATUSES`, `EXPORT_COVARIATE_COLUMNS` (the `ANALYSIS_COVARIATES` keys in order, reused).
  - The docstring's undecided list loses `EXPORT_FEATURE_RULE`.
- `src/adni_sexdiff/data.py`: `run_export`, reusing the manifest and `.tmp` helpers. `cli.py`: progress messages only; the flags exist.
- Ignore rules: none to change. `.gitignore`, `scripts/sync_results.sh` and `PARTICIPANT_LEVEL_PATTERNS` already treat `results/motco_input/**/*.csv` as participant-level except `*manifest*`, which covers `manifest.json`.
- New `scripts/spike_export_inventory.py`, the read-only spike that produced `spike.md`. It reads the Nightingale dictionary for its cross-check; `export` does not.
- Dependencies: none. The spike uses pandas and numpy only.
