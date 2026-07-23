#!/usr/bin/env bash
# run-daemon.sh - Edit the variables below, then run in a terminal.
#
# Starts the backend-connected workstation daemon in the foreground:
#   .venv/bin/python -m agent_runner_v2.run_agent daemon [worker_id]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ==================================================================
# EDIT THESE VARIABLES to match your setup:
# ==================================================================

AGENT_RUNNER_ROOT="$SCRIPT_DIR"

# Optional daemon identity and routing
# WORKER_ID="kode-worker-01"
WORKER_LABEL="live"
BACKEND_URL=""

# Optional daemon tuning (leave blank to use config.json / CLI defaults)
STEP_SPEC_SOURCE="backend"
POLL_SECONDS=""
MAX_PARALLEL="2"
RUNTIME_DIR=""
LOG_FILE=""
STALLED_SECONDS=""
STEP_TIMEOUT_SECONDS=""
KILL_GRACE_SECONDS=""

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
    echo "  ./.venv/bin/python -m pip install -e \".[dev]\""
    exit 1
fi

FLAGS=""
[[ -n "$WORKER_LABEL" ]] && FLAGS="$FLAGS --worker-label $WORKER_LABEL"
[[ -n "$BACKEND_URL" ]] && FLAGS="$FLAGS --backend-url $BACKEND_URL"
[[ -n "$STEP_SPEC_SOURCE" ]] && FLAGS="$FLAGS --step-spec-source $STEP_SPEC_SOURCE"
[[ -n "$POLL_SECONDS" ]] && FLAGS="$FLAGS --poll-seconds $POLL_SECONDS"
[[ -n "$MAX_PARALLEL" ]] && FLAGS="$FLAGS --max-parallel $MAX_PARALLEL"
[[ -n "$RUNTIME_DIR" ]] && FLAGS="$FLAGS --runtime-dir \"$RUNTIME_DIR\""
[[ -n "$LOG_FILE" ]] && FLAGS="$FLAGS --log-file \"$LOG_FILE\""
[[ -n "$STALLED_SECONDS" ]] && FLAGS="$FLAGS --stalled-seconds $STALLED_SECONDS"
[[ -n "$STEP_TIMEOUT_SECONDS" ]] && FLAGS="$FLAGS --step-timeout-seconds $STEP_TIMEOUT_SECONDS"
[[ -n "$KILL_GRACE_SECONDS" ]] && FLAGS="$FLAGS --kill-grace-seconds $KILL_GRACE_SECONDS"

echo "==========================================================================="
echo " Mode:            Daemon Supervisor"
echo " Agent-runner:    $AGENT_RUNNER_ROOT"
echo " Python:          $VENV_PYTHON"
echo " Worker ID:       ${WORKER_ID:-<from config.json / CLI default>}"
echo " Worker Label:    ${WORKER_LABEL:-<from config.json / CLI default>}"
echo " Backend URL:     ${BACKEND_URL:-<from ~/.ukbe-runner/config.json / CLI default>}"
echo " Step Spec:       ${STEP_SPEC_SOURCE:-<from config.json / CLI default>}"
echo "==========================================================================="
echo ""

cd "$AGENT_RUNNER_ROOT"
if [[ -n "${WORKER_ID:-}" ]]; then
    "$VENV_PYTHON" -m agent_runner_v2.run_agent daemon "$WORKER_ID" $FLAGS
else
    "$VENV_PYTHON" -m agent_runner_v2.run_agent daemon $FLAGS
fi
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "Daemon stopped normally."
else
    echo "Daemon exited with code $EXIT_CODE."
fi
exit $EXIT_CODE
