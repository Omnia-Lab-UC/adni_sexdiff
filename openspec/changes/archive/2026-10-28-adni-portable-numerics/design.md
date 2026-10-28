# Design

## Context

See `proposal.md` for the measurements behind the settings and the user's choice of 1 thread. This is the state that shapes the approach:

- **Entry points.**
  - The console script is `adni_sexdiff.cli:main`, so Python imports the package (`__init__.py`, which defines only `__version__`) before `cli`.
  - `cli` imports `constants`, which imports only `__future__`, and then `data`, which imports numpy and pandas at module top.
  - metabo_adni, MOTCO, scikit-learn and scipy load later, inside the steps.
  - So the package `__init__` runs before numpy in every normal entry: `adni-sexdiff …`, `from adni_sexdiff.data import …`, `python -m adni_sexdiff.cli`.
- **When the libraries read the settings.**
  - numpy reads `NPY_DISABLE_CPU_FEATURES` once, when it is imported.
  - OpenBLAS reads `OPENBLAS_CORETYPE` and `OPENBLAS_NUM_THREADS` when the library loads. Two copies load: numpy's `libscipy_openblas64_` with numpy, and scipy's `libscipy_openblas` when scipy is first imported. Both obey the variables.
  - OpenBLAS caps its threads at the CPUs available to the process.
  - Setting a variable after the library has loaded changes nothing.
- **Observed on the office machine (2026-10-28).** Pinned means `NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL" OPENBLAS_CORETYPE=Haswell OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`.
  - **Introspection:** under the pinned settings, `numpy.lib.introspect.opt_func_info(func_name="^log2$", signature="float64")` reports `current` `baseline(X86_V2)`, against `X86_V4` by default, and `threadpoolctl.threadpool_info()` reports `architecture` `Haswell` and `num_threads` 1 for both OpenBLAS copies. Disabling a dispatchable feature the CPU lacks (`AVX512_SPR` here) is silently ignored.
  - **Rebuild, all 24 CPUs:** `clean` → `cohort` → `export` → `analyze` pinned reproduced 18 of 18 recorded outputs and `result.json` apart from its runtime. They were the same restricted to one CPU (`taskset -c 3`).
  - **Diagnostics:** pinned, they are identical on one CPU and on all CPUs. Against the committed files, `axis_correlations.csv`, `components.csv`, `geometry_shares.csv` and `diagnostics.md` match; `block_pcs.csv` does not, since it was made at 16 threads.
  - **OpenMP:** `OMP_NUM_THREADS` 1 against the default changed nothing in `analyze` or `axis-diagnostics`.
- **The manifests.** Every step builds a dict with `versions` from `_software_versions()` and writes it through `_write_manifest` (sorted keys). The steps are `run_clean` (per platform), `run_cohort`, `run_export`, `run_analysis` and `run_axis_diagnostics`.
- **The cluster scripts** export `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1` and request 2 (`clean`) or 1 (`analyze`) CPU.
- **`threadpoolctl` 3.7.0** is in the lock through scikit-learn but not declared. numpy is 2.4.6, so `numpy.lib.introspect` is public API.

## Goals / Non-Goals

**Goals:**
- Any of the user's machines, and the cluster, write the committed bytes from the same inputs, so the hash chain decides which machine can run a step, not which CPU it has.
- A run that is not pinned is visible in its manifest and in a finding, never silent and never a stop.
- No committed number changes at its printed digits; one file is re-issued.

**Non-Goals:**
- Making unpinned runs reproducible.
- Re-issuing the upstream manifests to carry the new block.
- Non-x86 machines.

## Decisions

**D1. The package sets the settings on import, overwriting.**
`adni_sexdiff/__init__.py` imports `NUMERIC_SETTINGS` from `.constants` (no numpy) and does `os.environ.update(NUMERIC_SETTINGS)` before anything else runs.
- *Why overwrite and not `setdefault`:* a stale export such as `OPENBLAS_NUM_THREADS=16` from an earlier experiment would silently unpin a run. The observed-state record (D3) is the safety net for the case the package cannot fix: a library already loaded.
- *Why the package and not only the shell:* the cluster scripts run `.venv/bin/adni-sexdiff` outside the Nix shell, and the Python API can be used from any interpreter.
- *Alternative: a wrapper script.* Rejected: it covers only one entry point.
- The import side effect is documented in the package docstring and in AGENTS.md. It affects only the process and its children, and the variables change floating-point dispatch, not what is computed.

**D2. The shell and the cluster scripts export the same values.**
- `flake.nix`'s `shellHook` exports the four variables, so `motco analyze` (the `cli_equivalent` reproduction), `uv run python` scratch scripts and the spikes see them. `.envrc` is `use flake`, so direnv gets them too.
- The two sbatch scripts add `NPY_DISABLE_CPU_FEATURES` and `OPENBLAS_CORETYPE` to their export line. Their thread variables already equal the pinned values, and their CPU requests stay as they are.
- The values are written out in both files, which cannot import Python. A task greps that they equal `NUMERIC_SETTINGS`.

**D3. `_numerics_record()` reads the state the process actually has.**
It is called by each step after its work and immediately before the manifest is assembled, so every BLAS library the step loaded (scipy's included) is listed. It returns:
```python
{
  "host": platform.node(),
  "cpu_model": <"model name" from /proc/cpuinfo, else platform.processor()>,
  "cpus_available": len(os.sched_getaffinity(0)),
  "requested": NUMERIC_SETTINGS,
  "environment": {k: os.environ.get(k) for k in NUMERIC_SETTINGS},
  "numpy_log2_float64": <opt_func_info(func_name="^log2$", signature="float64")["log2"]["dd"]["current"]>,
  "blas": [<{"api", "version", "architecture", "num_threads", "library": basename}> per threadpoolctl entry, sorted by library],
  "pinned": <bool, D4>,
}
```
- Only file basenames are recorded, so no home or data-root path enters a manifest.
- A field that cannot be read (non-Linux, no OpenBLAS loaded) is `null`, and `pinned` is then false.
- `threadpoolctl` is declared with `uv add threadpoolctl`; the lock keeps 3.7.0.

**D4. `pinned` is a conjunction of observed facts.**
It requires all four:
- `environment == requested`;
- `numpy_log2_float64` starts with `baseline`;
- at least one OpenBLAS entry;
- every entry whose `api` is `openblas` reports `architecture` `Haswell` and `num_threads` 1.

Each failing fact becomes a clause of one finding, for example:

> numerics not pinned: numpy log2 runs X86_V4 (pinned: baseline); OpenBLAS libscipy_openblas reports SkylakeX (pinned: Haswell); outputs may differ from another machine's at rounding level and the hash chain may not reproduce; do not commit this output

A non-OpenBLAS BLAS (MKL, Accelerate) is named in the finding as unpinnable.

**D5. Wiring, one call per step.**
- Each `run_*` calls `_numerics_record()` and, when `pinned` is false, `_numerics_finding()`.
- It adds `"numerics": record` at the manifest's top level and extends `findings`.
- It prints `[<step>] numerics: pinned (log2 baseline, OpenBLAS Haswell × 1 thread, host <name>)` or the finding.

`run_clean` records once per platform manifest. No step's outputs other than its manifest change.
- *Alternative: inject the block inside `_write_manifest`.* Rejected: the findings would not be printed with the step's other findings, and `_write_manifest` would gain knowledge of the manifest layout.

**D6. Re-issue `block_pcs.csv` only.**
After the change, on a data machine:
1. Run `axis-diagnostics --force` pinned.
2. Check that the four other outputs keep their committed sha256, that `block_pcs.csv` differs by at most 1e-15 with equal flags, and that `diagnostics_manifest.json` carries `numerics.pinned` true.
3. Commit the two changed files.

The upstream manifests stay as committed. Re-issuing any of them changes its sha256, which a downstream manifest records, and would force a re-issue of everything after it for no change in any output. Their reproduction under the pinned settings is recorded in the tasks instead: 18 of 18 on 24 CPUs and on 1 CPU, 2026-10-28.

**D7. Constant and docs.**
- `NUMERIC_SETTINGS: dict[str, str]` sits in `constants.py` beside `REPORTED_N_JOBS`. Its docstring gives the reason for each variable and the 2026-10-28 measurements.
- AGENTS.md:
  - constraint 6 gains "reported and committed runs are pinned (`numerics.pinned` true)";
  - Code conventions list `numerics` among the manifest keys;
  - Environment & commands state that the package pins the settings on import and how to check a machine (run any step and read `numerics`);
  - the Cluster section notes the exports.
- README gains a short "Numerics" note.

## Risks / Trade-offs

- **numpy renames a feature or adds an AVX-512 target for `log2`.** The variable then disables nothing. → `numpy_log2_float64` is no longer `baseline`, so `pinned` is false and a finding names it. The fix is a constant change, verified by a rebuild against the committed hashes.
- **OpenBLAS changes kernels between versions, or a lock update swaps the BLAS.** → The version is recorded per library, and a non-OpenBLAS BLAS makes `pinned` false. A lock move that changes a BLAS or numpy version reruns the hash comparison (tasks) before anything is committed.
- **`OPENBLAS_CORETYPE=Haswell` on a CPU without AVX2 crashes with an illegal instruction.** → The office Ryzen 9 7900X has AVX2. The home machine and the laptop produced the committed outputs, which the Haswell kernels reproduce, so they very likely have it. The cluster's nodes are unverified: the first cluster run checks `grep -m1 -o avx2 /proc/cpuinfo` on the node, and its `numerics` block records the CPU. This is documented, and non-x86 is out of scope.
- **numpy imported before `adni_sexdiff`,** for example in a notebook. → `pinned` is false with a finding. AGENTS.md says to import `adni_sexdiff` first.
- **One BLAS thread is slower.** → It was measured: `analyze` takes 19 s at 1 thread as at 24, and `clean` 10 s. Nothing in the pipeline is BLAS-bound at these sizes.
- **The import side effect surprises a user** who set different thread counts. → It is documented. The values apply only to processes that import the package, and the manifest records them.

## Migration Plan

1. On any machine: the constant, `__init__.py`, `_numerics_record` and the finding, the five wirings, `flake.nix`, the two sbatch scripts, `threadpoolctl` declared, docs. Verify without data that a step's manifest records the block and that a numpy-first import yields the finding (tasks, group 2).
2. On a data machine:
   - rebuild the chain into the scratchpad from a shell with none of the variables set, so only the package pins them;
   - compare every recorded hash, and repeat on one CPU;
   - re-issue `block_pcs.csv` (D6).
3. Commit the code, then the two re-issued files from a pinned run on the clean tree, as earlier steps did.
4. Revise `adni-latent-sensitivity`: its comparisons with the committed hashes become gates, and its `host` key comes from `numerics`.
5. Rollback: revert the code and restore the committed `block_pcs.csv` and `diagnostics_manifest.json` from git. The outputs of every other step are unchanged either way.
