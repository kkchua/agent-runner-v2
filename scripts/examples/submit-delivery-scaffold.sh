#!/usr/bin/env bash
# Submit a run for: delivery_scaffold_v1
#
# Purpose: Analyses the project, then generates SOP, delivery templates, and agent
#          definitions. Auto-discovers AI context files — no file inputs required.
#
# Edit the variables below, then run this script from anywhere.
#
# Required inputs:
#   PROJECT_ROOT — absolute path to the repo you are submitting work for

set -euo pipefail

PROJECT_ROOT="/workspace/projects/my-repo"

ukbe-run-agent submit \
  --workflow-name delivery_scaffold_v1 \
  --project-root "$PROJECT_ROOT"
