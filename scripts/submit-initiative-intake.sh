#!/usr/bin/env bash
# Submit a run for: initiative_intake_v1
#
# Purpose: Takes a draft initiative file and produces a structured PRE_INIT_FILE.
#
# Run from: the project root of the repo you are submitting work for
#   cd /workspace/projects/my-repo
#   bash /path/to/scripts/examples/submit-initiative-intake.sh
#
# Required inputs:
#   DRAFT_INIT_FILE — path to the raw draft initiative markdown, relative to project root

set -euo pipefail

DRAFT_INIT_FILE="docs/delivery/01_initiatives/draft/26-0002_step-log-tail-api.md"

ukbe-run-agent submit \
  --workflow-name initiative_intake_v1 \
  --project-root "$(pwd)" \
  --input "DRAFT_INIT_FILE=${DRAFT_INIT_FILE}"
