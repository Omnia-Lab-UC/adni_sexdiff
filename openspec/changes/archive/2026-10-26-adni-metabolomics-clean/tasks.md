# Tasks

## 1. Constants and the version check

- [x] 1.1 Add `CLEAN_OPTIONS` (the proposal's values per platform), `CLEAN_EXPECTED_COUNTS` (every number of the proposal's table and the spike's per-step cells, imputed points, runs, zeros, duplicated RIDs), `CLEAN_INPUT_FILES`, `CLEAN_FASTING_FILE`, `CLEAN_MEDICATION_FILE`, `CLEAN_TABLES`, `CLEAN_RUNS_TABLE`, `CLEAN_LOG`, `KNOWN_RAW_FILE_REPAIRS` (the UPLC ADNI-GO/2 entry with both hashes) and `RAW_INPUT_SHA256` (full hashes computed from the workstation data root; each must start with the 16-character prefix in `spike.md`) to `constants.py`; drop `CLEAN_OPTIONS` from the docstring's undecided list naming this change; add `results/cleaned/*/clean_manifest.json` to `AGGREGATE_EXCEPTIONS`; verify with `uv run python -c "from adni_sexdiff import constants as c; print(c.CLEAN_OPTIONS, len(c.RAW_INPUT_SHA256))"` and a loop checking each hash against the spike's prefix
- [x] 1.2 Implement `check_metabo_adni_version()` (installed version via `importlib.metadata` equals `METABO_ADNI_VERSION`, else `RuntimeError` naming both); verify it returns `0.5.8` and that calling it with the constant temporarily monkeypatched to `0.5.7` in a one-line Python snippet raises

## 2. Raw-input integrity helpers

- [x] 2.1 Implement `require_raw_files(root, names)` (every name present, error listing every missing one) and `hash_raw_file(path)` (sha256 through the symlink, target relative to the root, bytes); verify on the data root that the eleven files resolve and the hashes equal `RAW_INPUT_SHA256`, and that renaming nothing but passing a wrong name lists it
- [x] 2.2 Implement `check_known_repairs(hashes)` (repaired hash → annotation; `loni_sha256` → error naming file, defect and repair; hash in neither `RAW_INPUT_SHA256` nor the registry → finding); verify the repaired archive file is annotated, that a scratch copy of the UPLC ADNI-GO/2 file with its last two bytes removed (made and deleted in the scratchpad on this workstation, never elsewhere) hashes to `f28ede9a…` and is refused, and that a scratch file with other bytes yields a finding

## 3. The clean step

- [x] 3.1 Implement the shared helpers `_git_revision`, `_software_versions`, `_write_manifest` and `_finalize_output_dir` (stale `.tmp` removed at start, existing final refused without `force`, rename when complete, replacement under `force` only after completion); verify with a scratch directory that each branch behaves as the spec's "Output directory is complete or absent" scenarios state
- [x] 3.2 Implement the working copy (`<platform>.tmp/work/`, hard copies of `CLEAN_INPUT_FILES[platform]`), the in-process metabo_adni pipeline in `__main__.main`'s order with `CLEAN_OPTIONS[platform]`, stdout of every call redirected to `<platform>.tmp/logs/metabo_adni.log` with a step header per call, cwd restored in `finally`, and the per-step cell counts computed as the spike does; verify on the workstation that `clean --platform nmr` writes `NMR.csv` with 1504 × 245 and that the terminal output holds no number that could be a RID (only `[clean]` lines with step names, file names and counts)
- [x] 3.3 Write the cleaned table with `to_csv(key + ".csv")` (`P180.csv` / `NMR.csv`), check the index for duplicated RIDs (error), write `p180_runs.csv` from the raw files' participant rows (both-runs → finding with count), and delete `work/`; verify `P180.csv` is 1592 × 133, `p180_runs.csv` has the same 1592 RIDs with 746 `ADNI1` and 846 `ADNI2GO`, and `work/` is gone
- [x] 3.4 Write `clean_manifest.json` with every section of the spec's "Manifest content" requirement (versions, git revision, data root, options and `cli_equivalent`, inputs with target/bytes/sha256/repair, raw inventory, per-step cells, imputed points, value summary, runs, output hashes, expected vs observed with deviations, findings, upstream behaviours with counts); verify it parses, every section is present, `grep -c RID` on it is 0 except for column-name mentions, and the deviations list is empty on the inventoried files
- [x] 3.5 Wire `--platform all` to run p180 then nmr with independent directories and `--force` to replace; verify a run with an existing `nmr/` and no `--force` stops naming the directory and leaves it unchanged, and that `--force` replaces it

## 4. Ignore list, sync filter and cluster script

- [x] 4.1 Change `.gitignore` to `results/cleaned/**`, `!results/cleaned/*/`, `!results/cleaned/*/clean_manifest.json` (that order) and `scripts/sync_results.sh` to include `/cleaned/`, `/cleaned/*/` and `/cleaned/*/clean_manifest.json` before `--exclude '/cleaned/**'`, with the post-pull `find` excluding `clean_manifest.json`; verify `git check-ignore -v` ignores `results/cleaned/p180/P180.csv`, `results/cleaned/p180/p180_runs.csv` and `results/cleaned/p180/logs/metabo_adni.log` and does not ignore `results/cleaned/p180/clean_manifest.json`, and that `ADNI_SYNC_SOURCE=results ADNI_SYNC_TARGET=<scratch> scripts/sync_results.sh -n` lists only the two manifests under `cleaned/`
- [x] 4.2 Write `scripts/clean.sbatch` (partition `512x1024`, 2 CPUs, 8 GB, 2 h, BLAS threads 1, `ADNI_DATA_ROOT=/home1/tgonza/adni_sexdiff/data`, `uv run adni-sexdiff clean --platform all`, logs under `results/cleaned/logs/`); verify with `bash -n` on the workstation; `sbatch --test-only` is deferred to the workflow follow-up

## 5. Documentation

- [x] 5.1 Update `README.md`: status, the `clean` section (options and their values, the working copy, the outputs and which are participant-level, the manifest, the repair rule, the sbatch); verify `uv run adni-sexdiff clean --help` matches the documented flags
- [x] 5.2 Update `AGENTS.md`: status paragraph, step 1 (metabo_adni's `main` order, `--merge`, `P180.csv` / `NMR.csv`, `p180_runs.csv`, the log, the manifest exception), constraint 1's ignore list, constraint 3's option list with `--merge`, "Flag and ask" with `CLEAN_OPTIONS` decided by this change and its value, the cluster section naming `scripts/clean.sbatch`; correct "the `clean_files` pipeline" in `AGENTS.md` and the `run_clean` docstring (`clean_files` is metabo_adni's console script for `__main__.main`, not a library function); verify every remaining `grep -n clean_files AGENTS.md src/` hit names the console script and `CLAUDE.md` is unchanged
- [x] 5.3 Before committing, run `git status` and `git check-ignore` over every file produced under `results/cleaned/` and list in the commit message the two manifests as the only files added under `results/` with the reason they are aggregate; verify the staged list holds nothing else under `results/`

## 6. Verification runs

- [x] 6.1 Full run on the workstation: `uv run adni-sexdiff clean --platform all --force`; verify both manifests report `deviations: []`, every per-step cell equals the spike's table, imputed points 1651 / 155, runs 746 / 846, 41 zeros in 3 NMR metabolites, and the upstream behaviour counts 34 metabolites / 1608 points
- [x] 6.2 CLI equivalence: in a scratch working copy on this workstation, run `clean_files -D <work> -P p180 -F BIOMARK.csv -L <work> --mmc 0.2 --mpc 0.2 --cv 0.2 --icc 0.65 --merge` and the NMR equivalent, with stdout to a scratch log; verify `P180.csv` and `NMR.csv` are byte-identical to the step's outputs (`cmp`), then delete the scratch copy and its log
- [x] 6.3 Rerun determinism: a second `clean --platform all --force`; verify the output sha256 values in both manifests equal the first run's, and that the data root's files are unchanged (`RAW_INPUT_SHA256` still matches)

## Workflow follow-up

- User: file the three metabo_adni 0.5.8 findings (multi-plate LOD assignment, ADNI2GO-UPLC LOD not halved, medication reader at `bl`) against `tomszar/metabo_adni`; a fix arrives by a pin move and a re-issue of `clean` in its own change.
- User: deploy key or scoped token for the cluster clone (constraint 7) and the data root copy on the cluster; then `uv sync --locked`, `sbatch --test-only scripts/clean.sbatch`, the run, and `scripts/sync_results.sh` to pull the manifests and compare their counts with the workstation's.
- Archive the change after the workstation manifests are committed; the cohort proposal reads them.
