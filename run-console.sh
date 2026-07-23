#!/usr/bin/env bash
# run-console.sh - Launch the Flet-based operator console.
#
# Prerequisites:
#   1. Install console dependencies:
#        ./.venv/bin/python -m pip install -e ".[console]"
#   2. Ensure ~/.ukbe-runner/config.json contains backend_url and worker_id

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ==================================================================
# EDIT THESE VARIABLES to match your setup:
# ==================================================================

AGENT_RUNNER_ROOT="$SCRIPT_DIR"
CONSOLE_CONFIG="${HOME}/.ukbe-runner/operator-console.json"

# ==================================================================
# No changes needed below this line.
# ==================================================================

if [[ ! -d "$AGENT_RUNNER_ROOT" ]]; then
    echo "ERROR: Agent-runner root does not exist: $AGENT_RUNNER_ROOT"
    exit 1
fi

VENV_PYTHON="$AGENT_RUNNER_ROOT/.venv/bin/python"
if [[ ! -f "$VENV_PYTHON" ]]; then
    echo "ERROR: Repo venv Python not found: $VENV_PYTHON"
    echo "Create the repo venv and install editable first:"
    echo "  ./.venv/bin/python -m pip install -e \".[dev,console]\""
    exit 1
fi

FLAGS=""
[[ -n "$CONSOLE_CONFIG" ]] && FLAGS="$FLAGS --config \"$CONSOLE_CONFIG\""

echo "==========================================================================="
echo " Mode:            Operator Console"
echo " Agent-runner:    $AGENT_RUNNER_ROOT"
echo " Python:          $VENV_PYTHON"
echo " Console Config:  ${CONSOLE_CONFIG:-<from ~/.ukbe-runner/operator-console.json>}"
echo "==========================================================================="
echo ""

cd "$AGENT_RUNNER_ROOT"
eval "$VENV_PYTHON" -m agent_runner_v2.run_agent console $FLAGS
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "Operator console closed normally."
else
    echo "Operator console exited with code $EXIT_CODE."
fi
exit $EXIT_CODE
