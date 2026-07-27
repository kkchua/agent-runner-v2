#!/usr/bin/env bash
# submit-sdlc_00_init_doc_v1.sh - Edit the variables below, then run.
#
# Submits a new backend job for the sdlc_00_init_doc_v1 workflow:
#   Captures and structures initiative from draft input.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate .venv if it exists
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# ==================================================================
# EDIT THESE VARIABLES to match your setup:
# ==================================================================

WORKFLOW_NAME="sdlc_00_init_doc_v1"
INITIATIVE_ID=""
WORKER_LABEL="live"
WORKER_ID=""
BACKEND_URL=""
CODER=""

# DRAFT_INIT_FILE input file (filename only)
# Must exist in docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/
DRAFT_INIT_FILE="DRAFT-INIT-20260722-001_console-sdlc10-support.md"

# ==================================================================
# No changes needed below this line.
# ==================================================================

if ! command -v ukbe-run-agent &>/dev/null; then
    echo "ERROR: Cannot find ukbe-run-agent on PATH."
    echo "Install the package first, for example: pip install -e ."
    exit 1
fi

FLAGS=""
[[ -n "$INITIATIVE_ID" ]] && FLAGS="$FLAGS --initiative-id $INITIATIVE_ID"
[[ -n "$WORKER_LABEL" ]] && FLAGS="$FLAGS --worker-label $WORKER_LABEL"
[[ -n "$WORKER_ID" ]] && FLAGS="$FLAGS --worker-id $WORKER_ID"
[[ -n "$BACKEND_URL" ]] && FLAGS="$FLAGS --backend-url $BACKEND_URL"
[[ -n "$CODER" ]] && FLAGS="$FLAGS --coder $CODER"

# Build --input flags for seed artifacts
INPUT_FLAGS=""
if [[ -n "${DRAFT_INIT_FILE}" ]]; then
    DRAFT_INIT_FILE_PATH="$SCRIPT_DIR/docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/${DRAFT_INIT_FILE}"
    if [[ ! -f "${DRAFT_INIT_FILE_PATH}" ]]; then
        echo "ERROR: DRAFT_INIT_FILE file not found: ${DRAFT_INIT_FILE_PATH}"
        exit 1
    fi
    INPUT_FLAGS="--input DRAFT_INIT_FILE=${DRAFT_INIT_FILE_PATH}"
fi

echo "==========================================================================="
echo " Workflow:        $WORKFLOW_NAME"
echo " Repository Root: $SCRIPT_DIR"
echo " Routing:         Queue label"
echo " Worker Label:    ${WORKER_LABEL:-<from config.json / CLI default>}"
echo " Worker ID:       ${WORKER_ID:-<not pinned>}"
echo " Backend URL:     ${BACKEND_URL:-<from ~/.ukbe-runner/config.json / CLI default>}"
[[ -n "${DRAFT_INIT_FILE}" ]] && echo " DRAFT_INIT_FILE:  ${DRAFT_INIT_FILE}"
echo "==========================================================================="
echo ""

ukbe-run-agent submit --workflow-name "$WORKFLOW_NAME" $FLAGS $INPUT_FLAGS
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "Job submission failed (exit code $EXIT_CODE)."
    exit $EXIT_CODE
fi

echo ""
echo "Job submitted successfully."
exit 0
