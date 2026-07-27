#!/usr/bin/env bash
# run-reset-step.sh - Reset a job to a specific step.
#
# Resets workflow execution state to the selected step using:
#   ukbe-run-agent run --override-step <step>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate .venv if it exists
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# ==================================================================
# EDIT THESE VARIABLES to match your setup:
# ==================================================================

AGENT_RUNNER_ROOT="$SCRIPT_DIR"
TEMPLATE_GROUP="sdlc_10_requirement_v1"
JOB_ID="SDLC10REQ-GEN-20260722-003"
STEP_NAME="review_initiative"

# ==================================================================
# No changes needed below this line.
# ==================================================================

UKBE_CLI="ukbe-run-agent"

if [[ -z "$TEMPLATE_GROUP" ]]; then echo "ERROR: TEMPLATE_GROUP is required."; exit 1; fi
if [[ -z "$JOB_ID" ]]; then echo "ERROR: JOB_ID is required."; exit 1; fi
if [[ -z "$STEP_NAME" ]]; then echo "ERROR: STEP_NAME is required."; exit 1; fi

if ! command -v "$UKBE_CLI" &>/dev/null; then
    echo "ERROR: '$UKBE_CLI' not found on PATH."; exit 1
fi

CMD="$UKBE_CLI run --project-root \"$AGENT_RUNNER_ROOT\" --template-group $TEMPLATE_GROUP --job-id $JOB_ID --override-step $STEP_NAME"

echo "==========================================================================="
echo " Step Reset"
echo "==========================================================================="
echo " Agent-runner:   $AGENT_RUNNER_ROOT"
echo " Template group: $TEMPLATE_GROUP"
echo " Job ID:         $JOB_ID"
echo " Reset to step:  $STEP_NAME"
echo ""
echo " Command: $CMD"
echo "==========================================================================="
echo ""

eval "$CMD"
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "Step reset recorded successfully."
    echo "Re-run the normal workflow script to continue from $STEP_NAME."
else
    echo "Step reset failed (exit code $EXIT_CODE)."
    echo "Check job status: $UKBE_CLI run --project-root \"$AGENT_RUNNER_ROOT\" --template-group $TEMPLATE_GROUP --job-id $JOB_ID --check-job-status"
fi
exit $EXIT_CODE
