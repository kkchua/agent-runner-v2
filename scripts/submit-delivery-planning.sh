#!/usr/bin/env bash
# Submit a run for: delivery_planning_v1
#
# Purpose: Takes an approved initiative file and produces a PLAN_FILE and TASK_GRAPH_FILE.
#
# Run from: the project root of the repo you are submitting work for
#   cd /workspace/projects/my-repo
#   bash /path/to/scripts/examples/submit-delivery-planning.sh
#
# Required inputs:
#   INITIATIVE_ID — the initiative ID to link this plan run to
#   INIT_FILE     — path to the approved initiative markdown file, relative to project root

set -euo pipefail

INITIATIVE_ID="INIT-20260609-11"
INIT_FILE="docs/delivery/01_initiatives/INIT-20260609-11_step-log-tail-api.md"

ukbe-run-agent submit \
  --workflow-name delivery_planning_v1 \
  --project-root "$(pwd)" \
  --initiative-id "$INITIATIVE_ID" \
  --input "INIT_FILE=${INIT_FILE}"
