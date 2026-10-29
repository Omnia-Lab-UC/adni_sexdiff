#!/usr/bin/env bash
# Move aggregate results between this machine and the cluster.
#
# ADNI is controlled-access (DUA): every participant-level file is excluded,
# so the raw files, the cleaned matrices, the cohort table, the MOTCO input
# blocks (the primary's, each export variant's and the CN / LMCI / AD arm's),
# latent_scores.csv and analysis_metadata.csv never leave the machine they
# were made on. Only aggregate outputs move (result.json,
# stage_means.csv, pls_loadings.csv, manifests incl. cleaned/*/clean_manifest.json,
# summary.md, stage_counts.csv, diagnostics tables). The filter list below mirrors .gitignore and
# constants.PARTICIPANT_LEVEL_PATTERNS; change all three together.
#
# Usage: scripts/sync_results.sh [--push] [extra rsync args, e.g. -n]
#   default   pull <cluster>:<dir>/results/ into results/
#   --push    push results/ to <cluster>:<dir>/results/
#
# Environment: ADNI_CLUSTER (default tgonza@cluster.ing.uc.cl) and
# ADNI_CLUSTER_DIR (default /home1/tgonza/adni_sexdiff). For a local test,
# ADNI_SYNC_SOURCE / ADNI_SYNC_TARGET override both ends with directories.

set -euo pipefail

host="${ADNI_CLUSTER:-tgonza@cluster.ing.uc.cl}"
remote_dir="${ADNI_CLUSTER_DIR:-/home1/tgonza/adni_sexdiff}"
direction=pull
if [ "${1:-}" = "--push" ]; then
    direction=push
    shift
fi

# rsync filters: the first match wins, so the aggregate exceptions come
# before the pattern they are excepted from. Patterns with a leading / are
# anchored at results/. In-progress directories and logs are excluded first,
# so no exception below re-includes a file inside them.
filters=(
    --exclude '*.tmp/'
    --exclude 'logs/'
    --include '/cleaned/'
    --include '/cleaned/*/'
    --include '/cleaned/*/clean_manifest.json'
    --exclude '/cleaned/**'
    --include '/cohort/stage_counts.csv'
    --exclude '/cohort/*.csv'
    --include '/motco_input/**manifest*'
    --exclude '/motco_input/**.csv'
    --exclude '/motco_export_sensitivity/*/motco_input/*.csv'
    --exclude '/motco_stage_sensitivity/motco_input/*.csv'
    --exclude 'latent_scores.csv'
    --exclude 'analysis_metadata.csv'
)

cd "$(dirname "$0")/.."
local_dir=results
if [ "$direction" = pull ]; then
    src="${ADNI_SYNC_SOURCE:-$host:$remote_dir/results}/"
    dst="${ADNI_SYNC_TARGET:-$local_dir}/"
else
    src="${ADNI_SYNC_SOURCE:-$local_dir}/"
    dst="${ADNI_SYNC_TARGET:-$host:$remote_dir/results}/"
fi
mkdir -p "$local_dir"
echo "[sync_results] $direction: $src -> $dst"
rsync -av "${filters[@]}" "$@" "$src" "$dst"

# After a pull, refuse silently holding a known participant-level file (a
# new name is caught only once it is added to the filters above).
if [ "$direction" = pull ] && [ -d "${ADNI_SYNC_TARGET:-$local_dir}" ]; then
    found=$(cd "${ADNI_SYNC_TARGET:-$local_dir}" && find . \
        \( \( -path './cleaned/*' ! -type d ! -name clean_manifest.json \) \
           -o -path './cohort/*.csv' ! -name stage_counts.csv \
           -o \( -path './motco_input/*' -name '*.csv' ! -name '*manifest*' \) \
           -o -path './motco_export_sensitivity/*/motco_input/*.csv' \
           -o -path './motco_stage_sensitivity/motco_input/*.csv' \
           -o -name latent_scores.csv -o -name analysis_metadata.csv \) -print)
    if [ -n "$found" ]; then
        echo "[sync_results] participant-level files present after the pull:" >&2
        echo "$found" >&2
        exit 1
    fi
fi
