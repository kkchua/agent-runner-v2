#!/usr/bin/env bash
# Submit a run for: delivery_planning_v1
#
# Purpose: Takes an approved initiative file and produces a PLAN_FILE and TASK_GRAPH_FILE.
#
# Edit the variables below, then run this script from anywhere.
#
# Required inputs:
#   PROJECT_ROOT  — absolute path to the repo you are submitting work for
#   INITIATIVE_ID — the initiative ID to link this plan run to
#   INIT_FILE     — path to the approved initiative markdown file, relative to PROJECT_ROOT

set -euo pipefail

PROJECT_ROOT="/workspace/projects/my-repo"
INITIATIVE_ID="INIT-20260610-01"
INIT_FILE="docs/delivery/01_initiatives/INIT-20260610-01_my-initiative.md"

ukbe-run-agent submit \
  --workflow-name delivery_planning_v1 \
  --project-root "$PROJECT_ROOT" \
  --initiative-id "$INITIATIVE_ID" \
  --input "INIT_FILE=${INIT_FILE}"
