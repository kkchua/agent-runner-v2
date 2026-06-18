#!/usr/bin/env bash
# Submit a run for: task_execution_v1
#
# Purpose: Takes an approved task graph and plan, produces a TASK_FILE then executes it.
#
# Edit the variables below, then run this script from anywhere.
#
# Required inputs:
#   PROJECT_ROOT    — absolute path to the repo you are submitting work for
#   INITIATIVE_ID   — the initiative ID to link this execution run to
#   PLAN_FILE       — path to the approved plan markdown file, relative to PROJECT_ROOT
#   TASK_GRAPH_FILE — path to the approved task graph markdown file, relative to PROJECT_ROOT

set -euo pipefail

PROJECT_ROOT="/workspace/projects/my-repo"
INITIATIVE_ID="INIT-20260610-01"
PLAN_FILE="docs/delivery/02_plans/P-0610-01_my-plan.md"
TASK_GRAPH_FILE="docs/delivery/03_tasks/TG-0610-01_my-task-graph.md"

ukbe-run-agent submit \
  --workflow-name task_execution_v1 \
  --project-root "$PROJECT_ROOT" \
  --initiative-id "$INITIATIVE_ID" \
  --input "PLAN_FILE=${PLAN_FILE}" \
  --input "TASK_GRAPH_FILE=${TASK_GRAPH_FILE}"
