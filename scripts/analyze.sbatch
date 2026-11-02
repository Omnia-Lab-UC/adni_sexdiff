#!/bin/bash
#SBATCH --job-name=adni-analyze
#SBATCH --partition=512x1024
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=results/motco_analysis/logs/analyze-%j.out
#SBATCH --error=results/motco_analysis/logs/analyze-%j.err

# The MOTCO trajectory analysis on the ing cluster: runs `adni-sexdiff analyze`
# on results/motco_input/ (written by `export` on the login node) and writes
# results/motco_analysis/ (latent_scores.csv and analysis_metadata.csv are
# participant-level; the other five files are aggregate; AGENTS.md
# constraint 1). The settings are the constants of the change adni-analyze
# (9999 RRPP permutations, seed 20261027, rank floor 2, no latent
# adjustment); none is a flag. No --n-jobs is passed, so the run uses
# REPORTED_N_JOBS = 1 and is a reported run (AGENTS.md constraint 6).
#
# Prerequisites (the user's, or an agent's at the user's request; AGENTS.md
# constraint 7): the repository clone at
# /home1/tgonza/adni_sexdiff, `clean` (sbatch), `cohort` and `export` run on
# the cluster, and the environment synced on the login node (compute nodes
# have no internet access):
#   uv sync --locked --compile-bytecode   # a compute node writes each .pyc to NFS slowly
#   mkdir -p results/motco_analysis/logs   # Slurm needs the log directory to exist
#   sbatch scripts/analyze.sbatch
# An existing analysis directory stops the step; to replace it, pass --force:
#   sbatch scripts/analyze.sbatch --force
# Then pull the aggregate outputs to a workstation with scripts/sync_results.sh
# and compare analysis_manifest.json with the workstation's (statistics,
# p-values, rank; a floating-point difference across machines is recorded,
# not a gate).

set -euo pipefail

cd "${SLURM_SUBMIT_DIR:-.}"
mkdir -p results/motco_analysis/logs

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
# The pinned numeric environment (constants.NUMERIC_SETTINGS); the package sets
# the same values on import. OPENBLAS_CORETYPE=Haswell needs AVX2 on the node.
export NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL" OPENBLAS_CORETYPE=Haswell
export PYTHONUNBUFFERED=1  # progress lines reach the log as they happen

# The locked environment, run directly: `uv run` could try to sync, and the
# compute nodes cannot reach the network.
cli=.venv/bin/adni-sexdiff
if [ ! -x "$cli" ]; then
    echo "Missing $cli: run 'uv sync --locked' on the login node first" >&2
    exit 1
fi

echo "[sbatch] host=$(hostname) job=${SLURM_JOB_ID:-none}"
"$cli" analyze "$@"
