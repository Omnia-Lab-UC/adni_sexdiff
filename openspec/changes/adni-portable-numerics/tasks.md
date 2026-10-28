# Tasks

The pinned settings (`NUMERIC_SETTINGS`) are a reproducibility convention, not a statistical choice. The thread count of 1 was chosen by the user on 2026-10-28. Group 1 and group 2 need no data and run on any machine. Group 3 runs on one data machine, any machine whose rebuild reproduces the committed hashes, and every task line there names its hostname. The office machine qualified on 2026-10-28. No task line records a participant value. This change is applied before `adni-latent-sensitivity`.

## 1. The convention and where it is applied

- [x] 1.1 Add `NUMERIC_SETTINGS` to `constants.py` (design D7): the four variables, with a comment per variable giving what it fixes and the 2026-10-28 measurement, next to `REPORTED_N_JOBS`. Update the module docstring's conventions paragraph. Verify with `uv run python -c "from adni_sexdiff.constants import NUMERIC_SETTINGS as s; print(s)"` printing the four pairs, and that `constants.py` still imports nothing but `__future__`.
- [x] 1.2 Set the variables in `adni_sexdiff/__init__.py` before anything else (design D1), and document the import side effect in its docstring. Verify, from a shell where the four are unset:
  - `uv run python -c "import adni_sexdiff, os; print({k: os.environ[k] for k in adni_sexdiff.constants.NUMERIC_SETTINGS})"` prints the pinned values;
  - `uv run python -c "import adni_sexdiff, numpy; from numpy.lib.introspect import opt_func_info as o; print(o(func_name='^log2$', signature='float64'))"` reports `current` `baseline(X86_V2)` on this machine;
  - with `OPENBLAS_NUM_THREADS=16` exported, `import adni_sexdiff, numpy, threadpoolctl` reports 1 thread.
- [x] 1.3 Export the four variables in `flake.nix`'s `shellHook`, and add `NPY_DISABLE_CPU_FEATURES` and `OPENBLAS_CORETYPE` to the export lines of `scripts/clean.sbatch` and `scripts/analyze.sbatch`, keeping their thread variables (design D2). Verify:
  - `nix develop -c sh -c 'echo $NPY_DISABLE_CPU_FEATURES $OPENBLAS_CORETYPE $OPENBLAS_NUM_THREADS $OMP_NUM_THREADS'` prints the pinned values;
  - a scratch check that every value in `flake.nix` and both sbatch scripts equals `NUMERIC_SETTINGS`;
  - `bash -n` passes on both scripts.

## 2. The record, the finding and the wiring

- [x] 2.1 Run `uv add threadpoolctl`. Verify `uv.lock` keeps `threadpoolctl` 3.7.0 and that no other entry moves (`git diff uv.lock` shows only the dependency edge).
- [x] 2.2 Implement `_numerics_record()` and `_numerics_finding()` (design D3, D4). Verify with a scratch script:
  - in a pinned process, the record has every key with `pinned` true, `numpy_log2_float64` `baseline(X86_V2)` and two OpenBLAS entries (after `import scipy.linalg`) at `Haswell` × 1, and no path beyond basenames;
  - in a process that imports numpy before `adni_sexdiff` (no variables set), `pinned` is false and the finding names `X86_V4` and `SkylakeX`;
  - with `OPENBLAS_CORETYPE` unset after import, `environment` differs from `requested` and the finding names the variable.
- [x] 2.3 Wire the record into `run_clean` (each platform manifest), `run_cohort`, `run_export`, `run_analysis` and `run_axis_diagnostics` (design D5): the `numerics` key, the finding, the progress line. Update each step's docstring Notes (manifest keys, the finding). Verify with the synthetic export of `adni-latent-sensitivity`'s design (blocks, metadata, covariates and manifest in the scratchpad) that `analyze` and `axis-diagnostics` write `numerics` with `pinned` true and print the line, and that their CSVs and Markdown are byte-identical to a run of the pre-change code on the same synthetic inputs. Then repeat the analysis with numpy imported first and check that the finding is in the manifest and printed.
  Done 2026-10-28 on nixos-office, with the real inputs in place of the synthetic export. That export is not built yet, and this machine holds the hash-verified `results/`; all outputs went to the scratchpad.
  - The pre-change code (a `git worktree` of `facb12c`, its own `uv sync --locked`, pinned by the shell) and the new code (from a shell with the four variables unset, so the package pins them) ran `analyze` and `axis-diagnostics` from the repo directory on the default inputs.
  - Their `latent_scores.csv`, `pls_loadings.csv`, `stage_means.csv`, `analysis_metadata.csv`, `summary.md`, the four diagnostics CSVs and `diagnostics.md` are byte-identical.
  - The manifests are equal apart from `created_at`, `git_revision`, `outputs`, the runtime, the `cli_equivalent` path and the new `numerics` block, which records `pinned` true. Both steps print `numerics: pinned (log2 baseline(X86_V2), OpenBLAS Haswell × 1 thread, host nixos-office)`.
  - With numpy imported before `adni_sexdiff`, `run_analysis` completes, prints `numerics: NOT pinned` and the finding (log2 `X86_V4`, OpenBLAS `SkylakeX`, 24 threads), and records `pinned` false with the finding in the manifest.
  - `clean`, `cohort` and `export` are wired the same way and exercised in 3.1.

## 3. Real data on a data machine

- [x] 3.1 From a shell where none of the four variables is set, so only the package pins them, rebuild into the scratchpad: `clean --data-root <root>`, `cohort`, `export` and `analyze`, each reading the previous scratch output. Verify that every output whose sha256 the five committed upstream manifests record has that sha256 (18 files), that `result.json` equals the committed one apart from its runtime, and that every scratch manifest records `numerics.pinned` true. Then repeat the four steps with `taskset -c 0` (one available CPU) and check the same hashes. Record in this line the hostname, the CPU model, both outcomes and the runtimes.
  Done 2026-10-28 on nixos-office (AMD Ryzen 9 7900X, AVX-512), from a shell with the four variables unset.
  - On 24 CPUs: 18 of 18 recorded outputs have their committed sha256, `result.json` is equal apart from its runtime, and all five scratch manifests (two `clean`, `cohort`, `export`, `analyze`) record `numerics.pinned` true and print `numerics: pinned`. Total 39 s, `analyze` 25.0 s.
  - With `taskset -c 0` (1 CPU available): the same 18 of 18, the same `result.json` and the same `pinned` true. Total 42 s, `analyze` 28.7 s.
  - Scratch directories deleted.
- [x] 3.2 Re-issue the diagnostics (design D6): `uv run adni-sexdiff axis-diagnostics --force` on the default inputs (the data machine's `results/` must pass the hash check of 3.1's comparison first). Verify:
  - `axis_correlations.csv`, `components.csv`, `geometry_shares.csv` and `diagnostics.md` keep the sha256 the committed `diagnostics_manifest.json` recorded;
  - `block_pcs.csv` differs from the committed copy (`git show HEAD:results/motco_diagnostics/block_pcs.csv`) by at most 1e-15 in absolute value with equal flags;
  - the new manifest records `numerics.pinned` true;
  - a second run into a scratch `--out-dir` restricted to one CPU writes the same five sha256.

  Record in this line the number of changed cells and the largest absolute difference.
  Done 2026-10-28 on nixos-office, from a shell with the four variables unset. Its `results/` had passed the comparison earlier that day: all 24 recorded outputs of the six committed manifests matched.
  - `axis_correlations.csv`, `components.csv`, `geometry_shares.csv` and `diagnostics.md` keep their committed sha256.
  - `block_pcs.csv`: 40 of 144 numeric cells changed, the largest absolute difference 5.83e-16. Flags and the non-numeric columns are equal.
  - The new `diagnostics_manifest.json` records `numerics.pinned` true, with the same four per-component findings (`pls_0`, `pls_1`, `pls_3`, `pls_4`).
  - A rerun restricted to one CPU into the scratchpad wrote the same five sha256.
  - `git status` shows only `block_pcs.csv` and `diagnostics_manifest.json` modified under `results/`.
- [x] 3.3 Run `motco analyze` with the committed analysis manifest's `cli_equivalent` in `nix develop` into a scratch directory. Verify that its `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` have the committed sha256, which shows that the shell's exports pin MOTCO's own CLI. Record the outcome; delete the scratch directories.
  Done 2026-10-28 on nixos-office. The shell exported `OPENBLAS_CORETYPE=Haswell` and `OPENBLAS_NUM_THREADS=1`. `motco analyze` with the committed `cli_equivalent` (`OUT_DIR` in the scratchpad) exited 0, and `pls_loadings.csv`, `stage_means.csv` and `latent_scores.csv` have their committed sha256. Scratch directory deleted.

## 4. Docs

- [x] 4.1 Update `AGENTS.md` (design D7):
  - constraint 6: reported and committed runs are pinned;
  - Code conventions: `numerics` among the manifest keys;
  - Environment & commands: the package pins the settings on import; import `adni_sexdiff` before numpy; check a machine by reading any manifest's `numerics`; non-x86 is unsupported;
  - the Cluster section: the exports, and the AVX2 check on a node;
  - the Layout entries for `constants.py`, `data.py` and `__init__.py`.

  Update `README.md` with a "Numerics" note (the four variables, what each fixes, how to check a machine, the 2026-10-28 measurement in one sentence). Verify that both name `NUMERIC_SETTINGS` and the four values exactly as `constants.py` does, and that `CLAUDE.md` is unchanged.

## 5. Commit hygiene

- [x] 5.1 Commit the implementation first. Then rerun 3.2's `axis-diagnostics --force` on the clean tree at that commit, so the manifest records it, on the same data machine. Commit only `results/motco_diagnostics/block_pcs.csv` and `results/motco_diagnostics/diagnostics_manifest.json`, naming each in the message with why it is aggregate (per block and PC, no `rid`) and why it changed (1 BLAS thread; the largest difference). Verify that `git status` shows no other change under `results/`, that `git check-ignore -q` fails for both files, and that `openspec validate adni-portable-numerics --strict` passes.
  Done 2026-10-28 on nixos-office.
  - The implementation was committed first (`35a1b62`), and the two files re-issued in 3.2 were restored to HEAD.
  - `axis-diagnostics --force` was rerun from a shell with the four variables unset. The user's uncommitted `.idea/modules.xml` was stashed for the run and popped after, so the tracked tree was clean.
  - `diagnostics_manifest.json` records `35a1b62`, `dirty` false and `numerics.pinned` true (host nixos-office). The five outputs equal 3.2's byte for byte.
  - `git status` shows only `block_pcs.csv` and `diagnostics_manifest.json` modified under `results/`. `git check-ignore -q` fails for both, the `rid` / `RID` grep finds nothing in them, and `openspec validate --strict` passes.
  - The outputs commit adds those two files and this task file only.

## Workflow follow-up

- Cross-machine check (non-blocking; when the user is next at nixos-home or the Dell laptop). On that machine, after `git pull` and `uv sync --locked`, repeat 3.1's pinned rebuild into the scratchpad, plus `axis-diagnostics` into a scratch `--out-dir`. Compare every output hash with the committed manifests, including the re-issued `block_pcs.csv`. This turns the indirect evidence that the Haswell kernels give the same bits on that CPU into a direct test. Record the hostname, the CPU model and the outcome in the PR or in a note on this change. A mismatch is reported to the user and is not resolved by changing a setting silently.
- Archive the change after the PR is merged. The archive creates `openspec/specs/numeric-reproducibility/`.
- Then revise `adni-latent-sensitivity` (design, Migration Plan step 4):
  - its same-machine gates may compare with the committed hashes directly;
  - its readiness check and its "recorded, not a gate" comparisons become gates;
  - its manifests take the hostname from `numerics` instead of a `host` key.
- Optional later change: re-issue the upstream manifests so that every committed manifest carries a `numerics` block.
