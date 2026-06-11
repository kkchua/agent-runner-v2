#!/usr/bin/env bash
# Submit a run for: initiative_intake_v1
#
# Purpose: Takes a draft initiative file and produces a structured PRE_INIT_FILE.
#
# Edit the variables below, then run this script from anywhere.
#
# Required inputs:
#   PROJECT_ROOT    — absolute path to the repo you are submitting work for
#   DRAFT_INIT_FILE — path to the raw draft initiative markdown, relative to PROJECT_ROOT

set -euo pipefail

PROJECT_ROOT="/workspace/projects/my-repo"
DRAFT_INIT_FILE="docs/delivery/01_initiatives/draft/my-initiative.md"

ukbe-run-agent submit \
  --workflow-name initiative_intake_v1 \
  --project-root "$PROJECT_ROOT" \
  --input "DRAFT_INIT_FILE=${DRAFT_INIT_FILE}"
