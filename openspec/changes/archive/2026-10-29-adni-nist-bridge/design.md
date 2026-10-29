# Design

## Context

See `proposal.md` for the motivation, the two variants, the bridge rule and the reading rules, `spike.md` for every number, and the specs for the requirements. This is the state that shapes the approach.

- **`run_export`** (`data.py`) does the whole export in one function:
  - it checks the clean outputs (`_check_clean_outputs(..., runs=False)`: the run table is not read today) and the cohort chain;
  - it keeps the participants with both flags in `cohort.csv` order and aligns the cleaned tables to them;
  - per block it applies membership, the 5 % floor and `log2(x + floor)`;
  - it computes `_phase_offset` against the `phase` covariate, then the counts against `EXPORT_EXPECTED_COUNTS`;
  - it writes through `_finalize_output_dir`.

  It reads no data-root file.
- **`_run_trajectory_analysis`** is the analysis body that `analyze` and `latent-sensitivity` share. Its defaults reproduce the primary byte for byte. `_check_primary_reference` and `_check_cohort_manifest` are `latent-sensitivity`'s gates on the primary analysis and the cohort manifest. `render_analysis_summary` and `render_axis_diagnostics` already branch on a recorded latent adjustment (the arm).
- **The QC material.** NIST SRM 1950 sits in the sheet `NIST SRM 1950 Data` of four workbooks inside two LONI supplement archives under `Metabolomics/p180/`. The data root has no top-level symlink to either archive today.
  - ADNI-1: 11 plates × 3 replicates.
  - ADNI-GO/2: 12 plates × 2 replicates.
  - Below-LOD cells are the text `< LOD` / `<LOD` / `No Interception`.
  - Only the ADNI-GO/2 workbooks carry per-cell status columns: `Valid`, `Semi Quant.`, `<Lowest CS`, `< LOD` and 41 FIA cells `ISTD Out of Range`. The ADNI-1 workbooks mark quality by cell colour only.
  - Every NIST plate is a data plate that carries study-pool rows.
- **`p180_runs.csv`** (`clean`'s run table; participant-level) holds each cleaned participant's assay run. The cohort manifest records that it equals `phase` for every cohort participant.
- **Pinned numerics.** Every committed output is pinned, so the committed hashes are the reference for the real-data gates on any data machine.
- **The template.** `../sead_sexdiff` runs export variants through one `preprocessing-sensitivity` step: a registry of variants, each rerunning the export with one setting changed, analysing it at the primary's settings and writing `<variant>/motco_input`, `motco_analysis` and `comparison`.

## Goals / Non-Goals

**Goals:**
- One step that runs any registered export variant end to end (export, analysis, comparison) from kept outputs, the primary held fixed as a chained reference.
- A bridge computed from reference material alone, recorded per metabolite, reproducible from four hashed workbooks.
- A registry the later export variants (all 245 NMR columns, the raw scale, `log2(x + 1)`, the generalized log) can join without another step.

**Non-Goals:**
- Any change to the primary's bytes: the export, the analysis, the diagnostics, the latent arm, the report.
- A statistic of the bridge's quality computed from participants inside the step. The spike's participant summaries stay in `spike.md`.
- Report sections for the variants (a follow-up change).

## Decisions

### D1. One `export-sensitivity` step with a registry, not an `export --variant` flag
`EXPORT_VARIANTS` maps each name to its p180 setting, and `export-sensitivity --variant <name|all>` runs export, analysis and comparison in one call.
- **Why:** the variant analysis must read exactly the variant export and the primary's settings. One step guarantees that, records the primary as its reference, and writes the comparison from the two records. The template's `preprocessing-sensitivity` has this shape.
- **Rejected:** `export --variant` followed by `analyze --input-dir`. It leaves the pairing to the operator and has no place for the comparison. `export` stays the primary's command.

### D2. The export body becomes a shared function with two p180 hooks
`run_export`'s body moves into `_run_export(..., variant=None)`.
- **Hooks:** a variant can do two things.
  - `factors`: a per-metabolite multiplier applied to the ADNI-GO/2 rows of the cleaned p180 concentrations, before the floors.
  - `standardize_by_run`: per-run centring and scaling of the p180 values after the scale.
- **Primary:** `run_export` calls the function with `variant=None`, which takes neither hook and writes today's bytes. The gate is a pinned `export --force` on the data machine reproducing the committed export manifest's output hashes, as `adni-latent-sensitivity` gated the shared analysis.
- **Rejected:** a separate variant exporter. It would duplicate membership, floors, counts and the manifest, and could drift from the primary.

### D3. The NIST workbooks are read inside the archives through top-level symlinks
`nist_bridge` requires `ADMC_supplement.zip` and `ADMCDUKEP180SUPP_20170410.zip` at the top of the data root, as relative symlinks into `Metabolomics/p180/`, created by hand like the others.
- **Reading:** `require_raw_files` and `hash_raw_file` treat them as any raw input (`RAW_INPUT_SHA256` gains both). `zipfile` reads the four members in place, and their sha256 are compared with the predeclared workbook hashes.
- **Why:** the archive stays as downloaded and nothing is extracted. The flat top level keeps holding exactly the names the steps read, which the layout rule asks for.
- **Rejected:** extracting the workbooks into `Metabolomics/p180/QC/` with four symlinks, as was done for the LOD workbooks. That adds four hand-made files and an extraction step on every machine.

### D4. The bridge estimator
Per run and metabolite, the run level is the mean of log2 over valid replicates (the geometric mean). `b` is ADNI-1's level minus ADNI-GO/2's.
- **No plate correction:** the spike measured the effect of metabo_adni's pool factors on `b` at a median 0.0007 log2. Skipping it also avoids reimplementing a metabo_adni function here, which constraint 3 forbids.
- **No significance gate on `b`:** a factor near 0 changes almost nothing, and a gate would select metabolites by noise. The plate-clustered SE is recorded beside `b`, never used by the rule.
- **ISTD flags:** honoured only where a status column exists, in ADNI-GO/2. This follows the methods summary; the asymmetry is a risk below.
- **Reference run ADNI-1:** after MOTCO's z-scoring the reference only moves the floors. ADNI-1 is the run the methods summary documents.

### D5. Matching names
A NIST column matches a cleaned metabolite when both are equal with case and punctuation dropped, within the kit whose sheet holds it. The spike matched 133 of 133 with no duplicate key. An unmatched exported metabolite is a finding and keeps factor 1, so a renamed column cannot silently change a factor.

### D6. The run label is the assay run, checked against `phase`
`nist_bridge` reads `p180_runs.csv` (its hash against `clean_manifest.json`, `runs=True`) for the run of each exported participant, because the bridge corrects the assay batch. `per_run_standardized` uses the same table. The variant manifest counts the exported participants whose run differs from their `phase`: a finding if not 0. The cohort manifest records 0.

### D7. `per_run_standardized` after the primary's scale
The primary's rule runs unchanged (pooled floors, `log2(x + floor)`). Each p180 metabolite is then centred and divided by its population SD within each run.
- **Why:** this way the variant changes one thing.
- **Rejected:** per-run floors, which would change the scale and the standardization at once.

The NMR block is untouched: it was assayed in one batch, with median |d| 0.21.

### D8. The variant analysis reuses `_run_trajectory_analysis`
The analysis manifest records step `export-sensitivity`, the variant name and constant, the primary analysis as reference (`_check_primary_reference`: its `result.json` and manifest hashes, no latent adjustment, the installed MOTCO, the seed and permutations) and the variant export's five files as inputs. `render_analysis_summary` gains a variant branch: the header names the variant, a section summarises the p180 setting and the run offset from the variant export manifest, and `EXPORT_VARIANT_READING_RULES` follows `READING_RULES`. The arm branch is unchanged, and the primary's bytes are unchanged.

### D9. Layout, staging and ignore patterns
- **Layout:** `results/motco_export_sensitivity/<variant>/` with `bridge/` (`nist_bridge` only), `motco_input/`, `analysis/` and `comparison/`.
- **Staging:** each subdirectory is staged as `<sub>.tmp/` and the four are renamed together at the end, as `latent-sensitivity` stages `analysis/` and `comparison/`.
- **`--force`:** it replaces them. An existing `diagnostics/` is left in place and recorded as a finding (stale until `axis-diagnostics` is rerun).
- **The bridge table** lives in `bridge/`, not `motco_input/`. The new ignore pattern `results/motco_export_sensitivity/*/motco_input/*.csv` then needs no exception, and the variant's feature tables are ignored like the primary's.

### D10. Comparison and diagnostics
`render_export_sensitivity` builds `export_sensitivity.csv` and `.md` from the two analysis records, the two export manifests and the bridge table, reusing `_statistic_reading_line` and the status wording of `_arm_status_line`, with "run-handling dependence" in place of "basis dependence". `render_axis_diagnostics` recognises a variant from the analysis manifest's `step` and `variant`. Its error hints name `export-sensitivity` when that step wrote the analysis read.

### D11. Verification without a data root
A synthetic data root holds two small archives with fabricated QC workbooks: status columns, text cells, ISTD flags and a metabolite below half valid. Together with the existing synthetic cohort and export, they exercise the reader, the rule, the hooks, the byte-identity of the unchanged files and the staging on any machine. The real run happens on a data machine.

## Risks / Trade-offs

- **NIST is plasma, the participants serum** → the bridge assumes a matrix-independent factor per metabolite. In the spike it carries 90 % of the FIA offset's sum of squares but 38 % of UPLC's. Reading rule 4 states the assumption, and `phase` stays a covariate.
- **ADNI-1 quality flags are colours, not statuses** → ISTD-out-of-range cells may remain in ADNI-1. In ADNI-GO/2 such cells moved `b` by at most 0.077 log2 (3 metabolites). The asymmetry is recorded in the rule and the manifest.
- **Truncation at the LOD** → a run mean over the valid replicates of a metabolite near its LOD is biased upward. The half-valid inclusion bounds it, and the seven unbridged metabolites keep factor 1.
- **The bridge leaves a run axis** → the spike shows a common residual shift (median 0.11 log2) on PC2 (ρ 0.58). The variant is not run-free. Reading rules 4 and 7 say so, and its diagnostics measure it.
- **`per_run_standardized` removes real between-run differences** (stage composition included) → reading rule 5. It is a comparator, not a candidate.
- **The spike's participant summaries could invite tuning** → the rule and its counts are fixed in this proposal before any run, from NIST alone. Every participant summary is labelled descriptive.
- **The committed report does not cover the variants** → its inputs are unchanged, so it stays valid. The follow-up change extends it.

## Migration Plan

1. On every data machine and on the cluster, the user creates the two symlinks:
   - `ln -s Metabolomics/p180/ADMC_supplement.zip <root>/ADMC_supplement.zip`
   - `ln -s Metabolomics/p180/ADMCDUKEP180SUPP_20170410.zip <root>/ADMCDUKEP180SUPP_20170410.zip`

   `clean` and `cohort` do not read them, so their manifests are unaffected.
2. The ignore patterns are extended before the first variant run (constraint 1).
3. A pinned `export --force` into a scratch directory reproduces the committed export hashes (the D2 gate). A pinned `axis-diagnostics` on the primary reproduces the committed diagnostics hashes after the variant-aware renderer lands.
4. `export-sensitivity --variant all`, then `axis-diagnostics` on each variant. The aggregate outputs are committed after the clean-tree rerun.

Rollback: delete `results/motco_export_sensitivity/` and revert the change. No primary output moves.
