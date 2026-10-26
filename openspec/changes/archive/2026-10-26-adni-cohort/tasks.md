# Tasks

## 1. Constants

- [x] 1.1 Add `COHORT_RULE`, `STAGE_RULE` and `ANALYSIS_COVARIATES` (the design's D1 literals, the proposal's values) to `constants.py`; add `COHORT_EXPECTED_COUNTS` (every number of `spike.md`: cascade per set, sex × stage per set, composition cells, stage source 1498 / 2 / 1, phase-against-run 0, statin users 704, missing covariate values 0); add the conventions `COHORT_CLINICAL_FILE`, `COHORT_COLUMNS` and `GROUP_VALUES`; add the ADNIMERGE entry (`e3eae0464106f0a3df4eb23946e57f1f7fd5f8456eb60af6540654a36a16f7a2`) to `RAW_INPUT_SHA256`; drop the three names from the docstring's undecided list, naming this change. Verify with `uv run python -c "from adni_sexdiff import constants as c; print(list(c.ANALYSIS_COVARIATES), c.STAGE_RULE['map'], c.COHORT_EXPECTED_COUNTS['intersection'])"` and by checking that the ADNIMERGE hash equals `sha256sum data/ADNI_adnimerge_20170629_QT-freeze.csv`.

## 2. Inputs

- [x] 2.1 In `run_cohort`, check the five data-root names with `require_raw_files`, then hash them with `hash_raw_file` and `check_known_repairs`. Read both clean manifests and compare the sha256 of `P180.csv`, `p180_runs.csv` and `NMR.csv` with their `outputs` entries, stopping on an absent manifest or a mismatch. Verify on the workstation that the ADNIMERGE record shows `target` `Clinical/ADNI_adnimerge_20170629_QT-freeze.csv` with `predeclared` true and the UPLC ADNI-GO/2 file shows its repair. Then verify, with `--cleaned-dir` pointing at a scratch copy of `results/cleaned/` where one byte of `NMR.csv` is changed (made and deleted on this workstation), that the step stops naming `nmr/NMR.csv` and creates no output directory.
- [x] 2.2 Read the visit columns (`usecols` `RID` plus the visit column) of the three raw files in `COHORT_RULE["sample_visit_columns"]` and form each participant's visit set per platform. Read the ADNIMERGE `bl` rows, stopping on a duplicated `bl` RID. Read the medication table's `sc` rows with `dtype=str`, stopping on a duplicated `sc` RID among cohort participants. Verify the visit sets give p180 ADNI-GO/2 `{bl}` 846, NMR `{bl}` 1503 and `{sc}` 1.

## 3. Rules and outputs

- [x] 3.1 Build the platform sets: sample rule, ADNIMERGE `bl` row, union with flags, intersection. Apply `STAGE_RULE`, the `PTGENDER` check and the covariates of `ANALYSIS_COVARIATES` with their maps and level checks. Apply the stops of design D4 with column-and-count messages and no RID. Verify the cascade equals `spike.md` (p180 1592 → 1592; NMR 1504 → 1503; intersection 1501; union 1594). Then verify, on scratch copies of the clinical table made and deleted on this workstation, that one blanked `APOE4` stops the step with `apoe4` and count 1, and that one `DX.bl` set to `XX` stops it naming `XX` and count 1.
- [x] 3.2 Write `cohort.csv` (`COHORT_COLUMNS` order: `rid`, `sex`, `stage`, `dx_bl`, `protocol`, `age`, `education`, `apoe4`, `phase`, `statin`, `visit`, `p180`, `nmr`), `stage_counts.csv` (design D7: set-level rows with margins, composition rows for the intersection) and the counts. Verify `cohort.csv` has 1594 rows with 1501 both-flagged, that `stage_counts.csv` has `intersection, Female, MCI, all, all` = 310 and `intersection, Male, MCI, EMCI, ADNI2GO` = 152, that every set-level cell equals the proposal's table, and that no `stage_counts.csv` column holds participant values.
- [x] 3.3 Compute the stage-source agreement (`DX` read as the diagnosis at the visit), the phase-against-run table, the statin count and the descriptives by sex × stage. Write `cohort_manifest.json` with the design D8 keys, expected against observed, deviations and findings, and output hashes. Verify that it parses, that `deviations` is `[]`, that stage source is 1498 / 2 / 1, that phase-against-run has 0 off-diagonal entries, and that `grep -c '"RID"\|rid' results/cohort/cohort_manifest.json` hits only column-name mentions.
- [x] 3.4 Wire the step through `_finalize_output_dir` (`results/cohort.tmp/` → `results/cohort/`, `--force`) and print `[cohort]` progress lines with file names and counts only. Verify that a second run without `--force` stops naming `results/cohort` and leaves it unchanged, and that a run with `--force` gives identical `cohort.csv` and `stage_counts.csv` hashes (determinism).

## 4. Ignore rules and documentation

- [x] 4.1 Verify the existing ignore rules cover the outputs, with no edit: `git check-ignore -v` ignores `results/cohort/cohort.csv` and `results/cohort.tmp/`, and does not ignore `results/cohort/stage_counts.csv` or `results/cohort/cohort_manifest.json`. Also verify that `ADNI_SYNC_SOURCE=results ADNI_SYNC_TARGET=<scratch> scripts/sync_results.sh -n` lists only those two files under `cohort/`.
- [x] 4.2 Update the `run_cohort` docstring (inputs including the raw visit columns and the medication table; outputs; the stops; the union with flags) and the CLI help line if it no longer matches. Verify `uv run adni-sexdiff cohort --help`.
- [x] 4.3 Update `README.md`: status, the `cohort` section (rules, outputs and which are participant-level, the manifest), and the data-root layout with `Clinical/` and its symlink. Verify the documented flags match `--help`.
- [x] 4.4 Update `AGENTS.md`:
  - the status paragraph;
  - step 2, whose inputs now include the raw visit columns and the medication table, with outputs as built;
  - constraint 2's data-root layout, which gains `Clinical/`;
  - the "Data & domain notes", which name the clinical tables;
  - "Flag and ask", where `COHORT_RULE`, `STAGE_RULE` and `ANALYSIS_COVARIATES` are decided by this change with their values;
  - the Layout entry for `scripts/`, which gains `spike_cohort_inventory.py`.

  Verify `grep -n "undecided" AGENTS.md src/adni_sexdiff/constants.py` no longer lists the three names, and that `CLAUDE.md` is unchanged.

## 5. Commit hygiene

- [x] 5.1 Before committing, run `git status` and `git check-ignore` over every file under `results/cohort/`. List in the commit message `results/cohort/stage_counts.csv` and `results/cohort/cohort_manifest.json` as the only files added under `results/`, each with why it is aggregate. Verify that the staged list holds nothing else under `results/` and that `spike.md` and the proposal hold no RID (`grep -nE '\bRID\b' openspec/changes/adni-cohort` hits only column-name mentions).

## Workflow follow-up

- User: when the deploy key and the cluster data copy exist (with `Clinical/` and its symlink, replicated by `rsync -a`), run `clean` then `cohort` on the cluster and compare the pulled `cohort_manifest.json` counts with the workstation's.
- Archive the change after the workstation outputs are committed. The export proposal reads `results/cohort/` next, and the analyze proposal must pass `ANALYSIS_COVARIATES`' categorical codings and decide `covariate_latent_adjustment`.
- A later proposal adds the CN / LMCI / AD sensitivity arm, which needs no cohort change because `dx_bl` is in `cohort.csv`.
