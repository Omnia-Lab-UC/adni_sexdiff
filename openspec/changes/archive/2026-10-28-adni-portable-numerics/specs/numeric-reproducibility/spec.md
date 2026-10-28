# Spec Delta

## Purpose

Defines the pinned numeric environment every pipeline step runs in, so that two machines running a step on the same inputs write byte-identical outputs and the hash chain between steps holds whichever machine runs them, and the record each manifest keeps of the environment a run actually had.

## ADDED Requirements

### Requirement: Numeric settings are a fixed convention
The numeric settings SHALL be the constant `NUMERIC_SETTINGS`: `NPY_DISABLE_CPU_FEATURES` = `X86_V4 AVX512_ICL`, `OPENBLAS_CORETYPE` = `Haswell`, `OPENBLAS_NUM_THREADS` = `1`, `OMP_NUM_THREADS` = `1`. They SHALL NOT be a flag of any step.

#### Scenario: Constant read
- **WHEN** `NUMERIC_SETTINGS` is imported from `adni_sexdiff.constants`
- **THEN** it holds exactly the four variables with the values above

### Requirement: Settings applied before numpy loads
Importing the `adni_sexdiff` package SHALL set each variable of `NUMERIC_SETTINGS` in the process environment, replacing any other value, before any of its modules imports numpy, pandas, scipy, scikit-learn, MOTCO or metabo_adni. This SHALL hold for the `adni-sexdiff` command and for the Python API.

#### Scenario: Command run from a shell without the settings
- **WHEN** `adni-sexdiff analyze` runs from a shell where none of the four variables is set
- **THEN** the analysis manifest's `numerics` block records the four values of `NUMERIC_SETTINGS` as seen by the process, numpy's baseline target for `float64` `log2`, and every OpenBLAS library at `Haswell` with 1 thread

#### Scenario: Conflicting value in the shell
- **WHEN** `OPENBLAS_NUM_THREADS=16` is exported and `adni-sexdiff axis-diagnostics` runs
- **THEN** the process runs with `OPENBLAS_NUM_THREADS=1`, and the manifest records 1 thread for every OpenBLAS library

### Requirement: Shell and cluster scripts export the settings
The Nix development shell SHALL export the four variables with the values of `NUMERIC_SETTINGS`, so that a command run in it outside the package also has them, such as `motco analyze` for a manifest's `cli_equivalent` or a scratch script. Every Slurm script under `scripts/` SHALL export the same values.

#### Scenario: MOTCO's CLI in the shell
- **WHEN** `motco analyze` runs in `nix develop`
- **THEN** its process sees the four variables with the values of `NUMERIC_SETTINGS`

#### Scenario: Cluster script
- **WHEN** `scripts/analyze.sbatch` or `scripts/clean.sbatch` is read
- **THEN** it exports `NPY_DISABLE_CPU_FEATURES`, `OPENBLAS_CORETYPE`, `OPENBLAS_NUM_THREADS` and `OMP_NUM_THREADS` with the values of `NUMERIC_SETTINGS`

### Requirement: Every manifest records the numeric state of its run
Every step's manifest SHALL hold a top-level `numerics` block with: the hostname, the CPU model and the number of CPUs available to the process; `NUMERIC_SETTINGS` as requested; the four variables as the process saw them; numpy's current dispatch target for `float64` `log2`; per loaded BLAS library its API, version, kernel architecture and thread count; and `pinned`.

#### Scenario: Manifest of a pinned run
- **WHEN** `adni-sexdiff cohort` finishes in a pinned process
- **THEN** `cohort_manifest.json` holds `numerics` with the machine's hostname, its CPU model, the available CPU count, the requested and observed settings, the `log2` target `baseline(X86_V2)` or the machine's equivalent baseline, the OpenBLAS entries, and `pinned` true

#### Scenario: No participant data
- **WHEN** a `numerics` block is written
- **THEN** it names the machine and the libraries only, never a participant, a path inside the data root or a file's content

### Requirement: Pinned is determined from the observed state
`pinned` SHALL be true only when the four observed variables equal `NUMERIC_SETTINGS`, numpy's `float64` `log2` runs its baseline target, and every loaded OpenBLAS library reports the `Haswell` kernel and 1 thread. It SHALL be decided from what the process observes, not from what was requested.

#### Scenario: numpy imported first
- **WHEN** a script imports numpy before `adni_sexdiff` on a machine with AVX-512 and runs `run_export`
- **THEN** the manifest records the `log2` target `X86_V4` and `pinned` false

### Requirement: A run that is not pinned carries a finding
When `pinned` is false the step SHALL complete and record a finding, printed and in the manifest. The finding SHALL name each observed value that differs from the pinned state, and SHALL say that the outputs may differ from another machine's at rounding level and that the hash chain may not reproduce. A committed output SHALL come from a pinned run.

#### Scenario: Not pinned
- **WHEN** `analyze` runs in a process where OpenBLAS reports the `SkylakeX` kernel
- **THEN** the analysis completes, and its findings name `SkylakeX` against `Haswell` and state that the outputs may differ from another machine's at rounding level

#### Scenario: Commit check
- **WHEN** an output directory is staged for commit
- **THEN** its manifest records `pinned` true, or the output is not committed

### Requirement: Pinned runs reproduce across machines
Two machines running a step on byte-identical inputs with pinned runs SHALL write byte-identical output files, except fields that record time, runtime, git revision or the machine. This SHALL hold whatever their CPU features or CPU count, among x86-64 machines with AVX2.

#### Scenario: AVX-512 machine reproduces the committed chain
- **WHEN** a machine with AVX-512 and 24 CPUs rebuilds `clean`, `cohort`, `export` and `analyze` under the pinned settings from a data root whose raw files match the recorded hashes
- **THEN** every output whose sha256 the committed manifests record has that sha256, and `result.json` equals the committed one apart from its runtime

#### Scenario: One available CPU
- **WHEN** the same steps run restricted to one CPU, as a cluster job with one CPU is
- **THEN** their outputs have the same sha256 as on the machine with 24 CPUs

### Requirement: The pinned settings change no committed number at its printed digits
Under the pinned settings, every committed output SHALL either keep its sha256 or, for one already made at another thread count (`block_pcs.csv`), change only beyond its printed digits: no flag, no row and no value rendered in `diagnostics.md` or a summary SHALL change.

#### Scenario: Block PCs re-issued
- **WHEN** `axis-diagnostics --force` runs pinned on a data machine
- **THEN** `block_pcs.csv` differs from the committed copy by at most 1e-15 in absolute value, its flags are equal, and `axis_correlations.csv`, `components.csv`, `geometry_shares.csv` and `diagnostics.md` keep their committed sha256
