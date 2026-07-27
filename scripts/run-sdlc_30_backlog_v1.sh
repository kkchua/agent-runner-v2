#!/usr/bin/env bash
# run-sdlc_30_backlog_v1.sh - Edit the variables below, then run.
#
# Runs ukbe-run-agent for the sdlc_30_backlog_v1 workflow:
#   Generates prioritised backlog from approved plan.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate .venv if it exists
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# ==================================================================
# EDIT THESE VARIABLES to match your setup:
# ==================================================================

TEMPLATE_GROUP="sdlc_30_backlog_v1"
JOB_ID=""
DRY_RUN="false"
NEW_JOB="false"
MODE="manual"
JOB_NO=""

# PLAN_FILE input file (filename only)
# Must exist in docs/repo/agent_runner/sdlc/delivery/20_plans/
PLAN_FILE="PLAN-20260722-001_console-sdlc10-support.md"

# ==================================================================
# No changes needed below this line.
# ==================================================================

if ! command -v ukbe-run-agent &>/dev/null; then
    echo "ERROR: Cannot find ukbe-run-agent on PATH."
    echo "Install the package first, for example: pip install -e ."
    exit 1
fi

FLAGS=""
[[ "${DRY_RUN,,}" == "true" ]] && FLAGS="$FLAGS --dry-run"
[[ "${NEW_JOB,,}" == "true" ]] && FLAGS="$FLAGS --new-job"
[[ -n "$JOB_ID" ]] && FLAGS="$FLAGS --job-id $JOB_ID"
FLAGS="$FLAGS --mode $MODE"
[[ -n "$JOB_NO" ]] && FLAGS="$FLAGS --job-no $JOB_NO"

# Build --set flags for seed artifacts
SEED_FLAGS=""
if [[ -n "${PLAN_FILE}" ]]; then
    PLAN_FILE_PATH="$SCRIPT_DIR/docs/repo/agent_runner/sdlc/delivery/20_plans/${PLAN_FILE}"
    if [[ ! -f "${PLAN_FILE_PATH}" ]]; then
        echo "ERROR: Plan File file not found: ${PLAN_FILE_PATH}"
        exit 1
    fi
    SEED_FLAGS="--set PLAN_FILE=${PLAN_FILE_PATH}"
fi

echo "==========================================================================="
echo " Workflow: $TEMPLATE_GROUP"
echo " Repo:     $SCRIPT_DIR"
echo "==========================================================================="
[[ -n "$JOB_ID" ]] && echo " Job ID:       $JOB_ID"
[[ -n "${PLAN_FILE}" ]] && echo " Plan File:  ${PLAN_FILE}"
echo " Dry run:    $DRY_RUN"
echo " New job:    $NEW_JOB"
echo "==========================================================================="
echo ""

ukbe-run-agent run --template-group "$TEMPLATE_GROUP" $FLAGS $SEED_FLAGS
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "Workflow finished with errors (exit code $EXIT_CODE)."
    exit $EXIT_CODE
fi

if [[ -n "$JOB_ID" ]]; then
    echo ""
    STATUS_FILE=$(mktemp)
    if ukbe-run-agent run --template-group "$TEMPLATE_GROUP" --job-id "$JOB_ID" --check-job-status > "$STATUS_FILE" 2>/dev/null; then
        JOB_STATUS=$(grep -m1 '^Status:' "$STATUS_FILE" | sed 's/^Status:[[:space:]]*//')
        if [[ "${JOB_STATUS,,}" == "completed" ]]; then
            echo "Workflow completed successfully."
        else
            echo "Workflow command completed. Job status: $JOB_STATUS"
        fi
    fi
    rm -f "$STATUS_FILE"
fi

exit 0
