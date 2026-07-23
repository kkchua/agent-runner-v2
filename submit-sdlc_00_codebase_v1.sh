#!/usr/bin/env bash
# submit-sdlc_00_codebase_v1.sh - Edit the variables below, then run.
#
# Submits a new backend job for the sdlc_00_codebase_v1 workflow:
#   ukbe-run-agent submit --workflow-name sdlc_00_codebase_v1 ...
#
# This workflow syncs repository code to codebase documentation.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate .venv if it exists
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# ==================================================================
# EDIT THESE VARIABLES to match your setup:
# ==================================================================

WORKFLOW_NAME="sdlc_00_codebase_v1"
WORKER_LABEL="live"
WORKER_ID=""
BACKEND_URL=""
CODER=""

# ==================================================================
# No changes needed below this line.
# ==================================================================

if ! command -v ukbe-run-agent &>/dev/null; then
    echo "ERROR: Cannot find ukbe-run-agent on PATH."
    echo "Install the package first, for example: pip install -e ."
    exit 1
fi

FLAGS=""
[[ -n "$WORKER_LABEL" ]] && FLAGS="$FLAGS --worker-label $WORKER_LABEL"
[[ -n "$WORKER_ID" ]] && FLAGS="$FLAGS --worker-id $WORKER_ID"
[[ -n "$BACKEND_URL" ]] && FLAGS="$FLAGS --backend-url $BACKEND_URL"
[[ -n "$CODER" ]] && FLAGS="$FLAGS --coder $CODER"

echo "==========================================================================="
echo " Workflow:        $WORKFLOW_NAME"
echo " Repository Root: $SCRIPT_DIR"
echo " Routing:         Queue label"
[[ -n "$WORKER_LABEL" ]] && echo " Worker Label:    $WORKER_LABEL"
[[ -n "$WORKER_ID" ]] && echo " Worker ID:       $WORKER_ID"
[[ -n "$BACKEND_URL" ]] && echo " Backend URL:     $BACKEND_URL"
echo "==========================================================================="
echo ""

ukbe-run-agent submit --workflow-name "$WORKFLOW_NAME" $FLAGS
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "Job submission failed (exit code $EXIT_CODE)."
    exit $EXIT_CODE
fi

echo ""
echo "Job submitted successfully."
exit 0
