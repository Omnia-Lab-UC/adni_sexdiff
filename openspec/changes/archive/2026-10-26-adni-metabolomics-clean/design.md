# Design

## Context

See `proposal.md` for motivation and `spike.md` for every number. Current state that shapes the approach:

- `run_clean` and `check_metabo_adni_version` are stubs in `src/adni_sexdiff/data.py`; `cli.py` already exposes `clean --platform {p180,nmr,all} --data-root --out-dir --force`. No helper for hashing, manifests or `.tmp` directories exists yet; this is the first step to need them, and the later steps reuse them.
- metabo_adni 0.5.8 (installed, pinned exactly) has no library entry point: `metabo_adni.__main__.main()` (installed as the console script `clean_files`; `python -m metabo_adni` runs nothing, as `__main__.py` has no main guard) parses `sys.argv` and runs eleven functions in a fixed order, then writes `files[key].to_csv(key + ".csv")` into the current directory. `load.read_files(directory, platform)` and `load.read_lod_files(directory)` both `os.chdir` into their directory; `read_files` skips an absent concentration file silently, while `read_lod_files` opens all four workbooks unconditionally. Every function prints tables that list `RID`s. The merge keys are `ADNI1-UPLC`, `ADNI1-FIA`, `ADNI2GO-UPLC`, `ADNI2GO-FIA` → `P180`, and `NMR`. Metabolite columns are found by position through `load._get_metabo_col_names`, participant rows through `load._get_data_indices` (p180: `RID < 99999`, the QC pool is `999999`).
- The data root holds the eleven metabolomics files flat, as relative symlinks into `Metabolomics/` (verified on this workstation on 2026-10-26); `ADMCDUKEP180UPLCADNI2GO.csv` resolves to the repaired archive copy (`7ad17d63…`).
- `results/cleaned/` is ignored whole by `.gitignore`, `constants.PARTICIPANT_LEVEL_PATTERNS` and `scripts/sync_results.sh`.
- The spike script (`scripts/spike_raw_inventory.py`) already drives the same functions step by step with stdout silenced and counts the cells after each; its logic for counting is the reference for the manifest.
- The cluster clone does not exist yet (constraint 7); the workstation holds the data and runs the step now.

## Goals / Non-Goals

**Goals:**
- A `clean` run that is metabo_adni's cleaning, with every option stated, reproducible from the manifest alone (`cli_equivalent`, hashes, versions), and that leaves nothing participant-level outside the ignored directory.
- Per-step counts in the manifest, checked against the spike's, so that a changed input or a changed pin is visible as a finding.
- Helpers (`sha256`, git revision, manifest writing, `.tmp` finalisation, required-file check, repair registry) written once, for every later step.

**Non-Goals:**
- Any transform or scaling (export), any participant selection beyond metabo_adni's QC (cohort), any use of sex or stage.
- A test framework; verification is the workstation run, its counts against the spike, a CLI-equivalence check and a rerun.
- Fixing metabo_adni (upstream), or making the cluster run possible (deploy key, data copy: the user's).

## Decisions

**D1. metabo_adni's functions called in-process, in `__main__.main`'s order, not as a subprocess.**
`run_clean` calls `load.read_files`, `metabolites.remove_missing`, (p180) `metabolites.cross_plate_correction`, `metabolites.remove_cv`, `metabolites.remove_icc`, `participants.remove_missing`, `participants.consolidate_replicates`, `participants.remove_non_fasters`, `participants.remove_bad_qc_tags`, `transformations.imputation`, `transformations.merge`, with the values of `CLEAN_OPTIONS[platform]`, exactly as the pinned `main` sequences them (the five transform branches are skipped because every flag is `False`). Between calls it counts participants × metabolites per table the way the spike does (`_get_metabo_col_names`, `_get_data_indices`, unique `RID`s). Alternative: `subprocess.run(["clean_files", ...])`. Rejected: no per-step counts (AGENTS.md names them as a manifest content), and `-L` chdir semantics put the outputs wherever the last chdir went. Guard against drift: the pin is exact and checked first, so the order cannot change under this code without a pin move, which is its own change; the manifest's `cli_equivalent` records the command line, and apply task 6.2 verifies once that the CLI in a scratch working copy writes byte-identical `P180.csv` / `NMR.csv`. The two underscore helpers are private API of a pinned release; a pin move revisits them.

**D2. A working copy of hard copies, cwd restored, stdout captured.**
`results/cleaned/<platform>.tmp/work/` receives a hard copy (`shutil.copyfile`, following the symlinks) of each required input, so metabo_adni's `chdir` and its `to_csv` touch only that directory and the archive is never written. `os.getcwd()` is saved before `read_files` and restored in a `finally`. Every metabo_adni call runs under `contextlib.redirect_stdout` into `<platform>.tmp/logs/metabo_adni.log` (one file, step headers added by the caller); the file moves with the directory and sits under `results/**/logs/`, already ignored and unsynced. After the pipeline the cleaned table is written with `to_csv(key + ".csv")` into `<platform>.tmp/` and `work/` is deleted. Alternative: symlinks in the working copy. Rejected: `glob("*")` and `to_csv` would still work, but copying lets the hash and the bytes metabo_adni read be the same object, and 20 MB is nothing.

**D3. Merge on, transforms off, scale deferred to export.**
`--merge` is metabo_adni's own stacking and intersection; doing it here keeps "cleaning is metabo_adni's" literal and gives export one table per platform. Every transform stays off for the reasons in the proposal; the value summary in the manifest (zeros, share below 1, smallest positive, median) is the input the export proposal needs to state the pseudo-count. Alternative: `--log2` here with metabo_adni's `1e-6`. Rejected: `log2(1e-6) ≈ −19.9` for the 41 NMR zeros would be a silent scale decision.

**D4. Run provenance from the raw files, not from the merged table's row order.**
`transformations.merge` concatenates ADNI-1 rows before ADNI-GO/2 rows, but that is positional. `run_clean` reads the participant `RID`s (`< 99999`) of each run's raw files before QC and labels each `RID` of `P180.csv` by the run whose files hold it; both → finding with a count. The spike found the runs coincide with `ORIGPROT` (ADNI1 ↔ ADNI1; ADNI2GO ↔ ADNI2 + ADNIGO) in the intersection cohort, so the cohort step can cross-check. The plate barcode is a finer batch; it is not carried because no proposal asks for it, and the raw files remain available if one does.

**D5. Predeclared counts as a constant, deviations as findings.**
`CLEAN_EXPECTED_COUNTS` holds, per platform, the cells after each step, imputed points, final shape, runs, zeros and duplicated `RID`s, copied from `spike.md`. The manifest stores `expected`, `observed` and `deviations`; each deviation is one line in `findings` and one `[clean]` print. The step never stops on a deviation (a fresh LONI download is the expected cause) and never reads a count to choose an option. Alternative: stop on deviation. Rejected: the template's rule is "finding, reported", and a stop would hide the other counts.

**D6. Raw-input integrity helpers.**
`require_raw_files(root, names)` → error naming every missing name (before any copy); `hash_raw_file(path)` → `{name, target, bytes, sha256}` with `os.readlink` for symlinks; `KNOWN_RAW_FILE_REPAIRS` (constants) keyed by expected name with `defect`, `repair`, `loni_sha256`, `repaired_sha256`; `check_known_repairs(hashes)` → annotate, or raise naming file, defect and repair when a `loni_sha256` matches. `RAW_INPUT_SHA256` (constants) records each input's full sha256 at this predeclaration (filled at apply from the data root; the spike holds the 16-character prefixes to check against); a hash matching neither it nor the registry is a finding. The cohort change extends the same helpers to the clinical tables.

**D7. Manifest and directory helpers shared by every step.**
`_git_revision()` (hash plus a dirty flag), `_software_versions(names)`, `_write_manifest(path, dict)` (sorted keys, indent 2), `_finalize_output_dir(tmp, final, force)` (remove a stale `.tmp` at start, refuse an existing `final` without `force`, rename when complete, replace under `force` only after the new directory is complete). The manifest layout is fixed by the spec's "Manifest content" requirement; later manifests reuse the same top-level keys (`step`, `versions`, `git_revision`, `inputs`, `settings`, `outputs`, `findings`) so `report` can read them uniformly.

**D8. Upstream behaviours recorded, not worked around.**
The four behaviours of 0.5.8 named in the proposal are computed as counts from the data the way the spike computes them (multi-plate missingness before imputation; the `ADNI2GO-UPLC` branch is a property of the code and recorded as such with the number of points it affects; NMR non-`bl` records from the raw file; the `bl` medication reader is recorded as not used) and written under `upstream_behaviours`. Filing them against `tomszar/metabo_adni` is the user's task; the fix arrives by a pin move and a re-issue of `clean`.

**D9. The manifest becomes the one committed and synced file under `results/cleaned/`.**
`.gitignore` gains `!results/cleaned/*/clean_manifest.json` after `results/cleaned/`; because git cannot re-include a file inside an excluded directory, the directory line changes to `results/cleaned/**` with `!results/cleaned/*/` and the file exception, in that order. `scripts/sync_results.sh` gains `--include '/cleaned/'`, `--include '/cleaned/*/'`, `--include '/cleaned/*/clean_manifest.json'` before `--exclude '/cleaned/**'`, and the post-pull `find` excludes `clean_manifest.json` from the cleaned branch. `constants.AGGREGATE_EXCEPTIONS` gains `results/cleaned/*/clean_manifest.json`. All three in one change, before the file exists (constraint 1). Alternative: keep the manifest local and let the cohort manifest carry its hash. Rejected: the step would leave no committed record of its counts, and `report` quotes cleaning counts from committed files.

**D10. Constants.**
Scientific: `CLEAN_OPTIONS` (the values in the proposal). Predeclared: `CLEAN_EXPECTED_COUNTS`, `RAW_INPUT_SHA256`. Conventions: `CLEAN_INPUT_FILES` (per platform, the exact names), `CLEAN_FASTING_FILE = "BIOMARK.csv"`, `CLEAN_MEDICATION_FILE` (named, not read), `CLEAN_TABLES = {"p180": "P180.csv", "nmr": "NMR.csv"}`, `CLEAN_RUNS_TABLE = "p180_runs.csv"`, `CLEAN_LOG = "logs/metabo_adni.log"`, `KNOWN_RAW_FILE_REPAIRS`. The module docstring drops `CLEAN_OPTIONS` from the undecided list and points to this change.

**D11. Cluster script.**
`scripts/clean.sbatch`: partition `512x1024`, 2 CPUs, 8 GB, 2 h, `OMP/OPENBLAS/MKL_NUM_THREADS=1`, `ADNI_DATA_ROOT=/home1/tgonza/adni_sexdiff/data`, `cd /home1/tgonza/adni_sexdiff && uv run adni-sexdiff clean --platform all`, logs under `results/cleaned/logs/`. `sbatch --test-only` is verified once the clone exists; the script is written now so the cluster run needs no further change.

## Risks / Trade-offs

- [Private metabo_adni helpers (`_get_metabo_col_names`, `_get_data_indices`) or the step order change in a later release] → the exact pin and the version check make this impossible without a pin move, whose change revisits D1; the CLI-equivalence check (task 6.2) is rerun at every pin move.
- [metabo_adni's `chdir` leaves the process in the working copy after an exception] → cwd saved and restored in `finally`; the working copy is deleted only on success, kept under `.tmp/` for inspection on failure.
- [A count deviates on the cluster but not on the workstation (different LONI download)] → the manifest's input hashes and findings show which file differs; each machine cleans its own data root and the manifests are compared through the sync.
- [Floating-point differences across machines make `P180.csv` differ by bytes between the workstation and the cluster] → determinism is promised per machine; across machines the counts and the manifests are what the cohort checks, not the bytes.
- [The ICC loop (pingouin, 141 metabolites × replicate pairs) is slow] → it ran within the spike on the workstation; the sbatch asks for 2 h.
- [The git re-include pattern for the manifest is wrong and a cleaned table becomes committable] → task 5.3 verifies with `git check-ignore -v` on every file the run produces and with `git status`; constraint 1's rule to name every file added under `results/` applies at the commit.
- [The 3 NMR records at visits other than `bl` are averaged into a participant's baseline value by metabo_adni] → a 0.5.8 behaviour, recorded with its count; whether it matters is for the cohort proposal (which has the visit codes from the manifest).

## Migration Plan

1. Land constants, helpers, `run_clean`, the ignore-list change, the script and the docs; no existing default changes (the CLI already has the flags).
2. Run `uv run adni-sexdiff clean --platform all` on the workstation; compare the manifests with the spike; commit the two manifests (and nothing else under `results/`).
3. When the deploy key and the cluster data copy exist (user), clone, `uv sync --locked`, `sbatch scripts/clean.sbatch`, pull the manifests with `scripts/sync_results.sh`, compare counts.
4. Rollback: outputs are additive under `results/cleaned/`; reverting the ignore-list change restores the fully ignored directory.
