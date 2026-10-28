#!/bin/bash
#SBATCH --job-name=adni-clean
#SBATCH --partition=512x1024
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=results/cleaned/logs/clean-%j.out
#SBATCH --error=results/cleaned/logs/clean-%j.err

# metabo_adni cleaning of both platforms on the ing cluster: runs
# `adni-sexdiff clean --platform all` against the cluster's data root and
# writes results/cleaned/p180/ and results/cleaned/nmr/ (participant-level
# except each clean_manifest.json; see AGENTS.md constraint 1).
#
# Prerequisites (the user's, AGENTS.md constraint 7): the repository clone at
# /home1/tgonza/adni_sexdiff, the raw files uploaded by hand into its data/
# (the metabo_adni names as symlinks into Metabolomics/), and the environment
# synced on the login node (compute nodes have no internet access):
#   uv sync --locked
#   mkdir -p results/cleaned/logs   # Slurm needs the log directory to exist
#   sbatch scripts/clean.sbatch
# An existing platform directory stops the step; to replace it, pass --force:
#   sbatch scripts/clean.sbatch --force
# Then pull the two manifests to a workstation with scripts/sync_results.sh
# and compare their counts with the workstation's.

set -euo pipefail

cd "${SLURM_SUBMIT_DIR:-.}"
mkdir -p results/cleaned/logs

export ADNI_DATA_ROOT="${ADNI_DATA_ROOT:-/home1/tgonza/adni_sexdiff/data}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
# The pinned numeric environment (constants.NUMERIC_SETTINGS); the package sets
# the same values on import. OPENBLAS_CORETYPE=Haswell needs AVX2 on the node.
export NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL" OPENBLAS_CORETYPE=Haswell
export PYTHONUNBUFFERED=1  # per-step counts reach the log as they happen

# The locked environment, run directly: `uv run` could try to sync, and the
# compute nodes cannot reach the network.
cli=.venv/bin/adni-sexdiff
if [ ! -x "$cli" ]; then
    echo "Missing $cli: run 'uv sync --locked' on the login node first" >&2
    exit 1
fi

echo "[sbatch] host=$(hostname) job=${SLURM_JOB_ID:-none} data_root=$ADNI_DATA_ROOT"
"$cli" clean --platform all "$@"
