#!/usr/bin/env bash
# Submit a run for: delivery_scaffold_v1
#
# Purpose: Analyse a target repository and generate delivery scaffold docs.
#
# Edit the variables below, then run this script.
#
# Required practical input:
#   PROJECT_ROOT — absolute path to the repository you want to scaffold
#
# Optional:
#   BACKEND_URL   — backend base URL
#   WORKER_ID     — pin the run to a specific worker/workstation
#   WORKER_LABEL  — worker queue label, usually live or dev
#   INITIATIVE_ID — initiative linkage if you want to tag the run

set -euo pipefail

PROJECT_ROOT="/workspace/projects/my-repo"
BACKEND_URL="${BACKEND_URL:-http://localhost:8100}"
WORKER_ID="${WORKER_ID:-}"
WORKER_LABEL="${WORKER_LABEL:-live}"
INITIATIVE_ID="${INITIATIVE_ID:-}"

cmd=(
  ukbe-run-agent submit
  --workflow-name delivery_scaffold_v1
  --backend-url "$BACKEND_URL"
  --project-root "$PROJECT_ROOT"
  --worker-label "$WORKER_LABEL"
)

if [[ -n "$WORKER_ID" ]]; then
  cmd+=(--worker-id "$WORKER_ID")
fi

if [[ -n "$INITIATIVE_ID" ]]; then
  cmd+=(--initiative-id "$INITIATIVE_ID")
fi

printf 'Running:\n  '
printf '%q ' "${cmd[@]}"
printf '\n'

"${cmd[@]}"
