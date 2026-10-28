# Proposal

## Why

The pipeline's chain checks compare every input with the sha256 the previous step's committed manifest records. That only works if the user's machines compute the same bits, and they move between machines often (office, home, a laptop on other campuses). Today they do not.

On 2026-10-28 the office machine (`nixos-office`, an AMD Ryzen 9 7900X with AVX-512 and 24 threads) rebuilt the whole chain from its own copy of the data root.
- `clean` and `cohort` reproduced every committed hash.
- `export`'s two blocks and feature tables, and `analyze`'s scores, loadings and stage means, did not. They differed at about 1e-15 relative: the counts, the rank and the p-values were equal, the statistics differed in the 15th–16th digit, and `summary.md` was byte-identical.

The cause is the CPU, not the data or the code. numpy takes an AVX-512 path for `log2` on machines that have it, and OpenBLAS picks AVX-512 kernels ("SkylakeX").

With three environment settings, the office machine reproduced every committed output byte for byte: `NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL"`, `OPENBLAS_CORETYPE=Haswell` and `OPENBLAS_NUM_THREADS=16`. This covered all 24 outputs the six committed manifests record, with `result.json` equal apart from its runtime.

The thread count matters only for the diagnostics' block SVD (`block_pcs.csv`). `analyze` was byte-identical at 1, 8, 16 and 24 threads, and `OMP_NUM_THREADS` changed nothing. OpenBLAS caps its threads at the CPUs available to the process (8 when restricted to 8 CPUs), so 16 could only be reproduced on machines with at least 16 CPUs. The user therefore chose 1 thread (2026-10-28): every machine, and a 1-CPU cluster job, can reproduce it, at the cost of re-issuing one committed file. A 1-thread `analyze` takes the same 19 s.

The office machine now holds a data root and the hash-verified participant-level files, so it can run the next change, `adni-latent-sensitivity`, once these settings are pinned.

## What Changes

- **The settings pinned as a convention.** `NUMERIC_SETTINGS` in `constants.py` (a reproducibility convention like `REPORTED_N_JOBS`, not a statistical choice):

  | variable | value | what it fixes |
  |---|---|---|
  | `NPY_DISABLE_CPU_FEATURES` | `X86_V4 AVX512_ICL` | numpy's AVX-512 dispatch (`log2` in `export`) |
  | `OPENBLAS_CORETYPE` | `Haswell` | OpenBLAS's kernel choice (`analyze`) |
  | `OPENBLAS_NUM_THREADS` | `1` | the block SVD's thread-dependent reductions (`axis-diagnostics`) |
  | `OMP_NUM_THREADS` | `1` | OpenMP threads: no effect today, removes a variable |

  Disabling a feature a machine lacks is silently ignored by numpy, so the settings are safe on machines without AVX-512.
- **Applied before numpy loads.** Importing `adni_sexdiff` (the CLI or the Python API) sets the four variables before any submodule imports numpy, overwriting other values for that process. The Nix shell (`flake.nix`, so `.envrc` too) exports them, so `uv run python`, scratch scripts and `motco analyze` (the manifests' `cli_equivalent`) see them. `scripts/clean.sbatch` and `scripts/analyze.sbatch` export them; their existing `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` already agree.
- **Recorded in every manifest.** Every step's manifest gains a top-level `numerics` block: `clean`, `cohort`, `export`, `analyze`, `axis-diagnostics`, and later steps through the shared helper. It records:
  - the machine (hostname, CPU model, CPUs available to the process);
  - `NUMERIC_SETTINGS` as requested, and the four variables as the process saw them;
  - numpy's dispatch target for `float64` `log2`, from numpy's public `numpy.lib.introspect.opt_func_info`;
  - each loaded BLAS library's API, version, kernel architecture and thread count (`threadpoolctl`);
  - `pinned`: true when the dispatch target is numpy's baseline and every OpenBLAS reports `Haswell` with 1 thread.

  The hostname replaces the separate `host` key that `adni-latent-sensitivity` planned for its own manifests.
- **A finding, never a stop, when a run is not pinned.** This happens, for example, when numpy was imported before `adni_sexdiff`, or when a later numpy renames a feature. The finding names what differs and states that the outputs may differ from other machines at rounding level and that the hash chain may not reproduce. A committed output must come from a pinned run, as it must come from `n_jobs = 1` (constraint 6).
- **One committed file re-issued.** `results/motco_diagnostics/block_pcs.csv` was made at 16 threads. At 1 thread, 40 of its 144 cells move by at most 5.8e-16. Its flags, `diagnostics.md`, and the other three diagnostics CSVs are byte-identical, checked on 2026-10-28.
  - The diagnostic is rerun with `--force` under the pinned settings on a data machine. The new `block_pcs.csv` and `diagnostics_manifest.json` (the first committed manifest with a `numerics` block) are committed.
  - No committed number in any table or report changes at the digits printed.
  - No other committed file is rewritten. The upstream manifests' hashes are recorded downstream, so re-issuing one would break the chain for no change in any output. The upstream files are recorded as reproduced under the pinned settings (tasks).
- **Docs:**
  - `AGENTS.md`: Environment & commands, the manifest keys in Code conventions, constraint 6 (reported runs are pinned), the Cluster section;
  - `README.md`: an environment note with the four variables and how to check a machine;
  - the `constants.py` docstring.

Out of scope, each its own change if wanted:
- Re-issuing the upstream manifests to carry a `numerics` block.
- Pinning other libraries' internals: pandas has no CPU dispatch that affected the outputs, and MKL is not used (the wheels bundle OpenBLAS).
- Supporting non-x86 machines (`OPENBLAS_CORETYPE=Haswell` needs AVX2; every current machine has it).
- `adni-latent-sensitivity` itself. It is revised after this change so that its comparisons with the committed hashes become gates, and it uses `numerics.host` instead of its own `host` key.

No statistical choice, constant or result changes. The settings change how floating-point operations are dispatched, not what is computed, and every committed number keeps its printed digits.

## Capabilities

### New Capabilities
- `numeric-reproducibility`: the pinned numeric environment of every pipeline step. It covers:
  - the settings applied before numpy loads, in the package, the Nix shell and the cluster scripts;
  - the `numerics` record in every manifest;
  - the not-pinned finding;
  - the guarantee that two machines running a step on the same inputs under the pinned settings write byte-identical outputs.

### Modified Capabilities
<!-- None at requirement level: every step's manifest gains a `numerics` key through a shared helper (stated by the new capability), and no existing requirement of `metabolomics-cleaning`, `cohort-assembly`, `motco-input-export`, `motco-trajectory-analysis` or `latent-axis-diagnostic` changes. The `block_pcs.csv` re-issue is a one-time task, not a requirement. -->

## Impact

- `src/adni_sexdiff/__init__.py`: sets `NUMERIC_SETTINGS` in `os.environ` before anything else; it reads the values from `constants.py`, which imports no numpy.
- `src/adni_sexdiff/constants.py`: `NUMERIC_SETTINGS` and the docstring.
- `src/adni_sexdiff/data.py`:
  - `_numerics_record()` (the observed state and `pinned`);
  - a `numerics` key and, when not pinned, a finding in every step's manifest;
  - a `[<step>] numerics: pinned …` progress line per step.
- `flake.nix`: the four exports in `shellHook`. `scripts/clean.sbatch`, `scripts/analyze.sbatch`: the two variables they lack.
- `pyproject.toml` / `uv.lock`: `threadpoolctl` declared as a direct dependency at its locked 3.7.0 (`uv add`). It is already installed through scikit-learn, so no resolution changes. numpy's introspection is public API since 2.0; the lock holds 2.4.6.
- Outputs: on a data machine, `axis-diagnostics --force` re-issues `block_pcs.csv` and `diagnostics_manifest.json`. No other committed file changes.
- Compute: none beyond the reruns that verify the change, which take minutes. `analyze` at 1 thread runs in the same 19 s.
- Machines: none named. Any machine whose rebuild under the pinned settings reproduces the committed hashes is a data machine; the office machine does today.
