#!/usr/bin/env bash
# run-bootstrap-publish.sh - Build the packaged bootstrap bundle from repo-local docs and workflow packages
#
# Sequence:
#   1. Run this script after changing:
#      - docs/system/00_governance/bootstrap
#      - workflows/<name>/workflow.toml packages
#   2. Run run-init.sh to install the packaged bundle into ~/.ukbe-runner/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate .venv if it exists
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

UKBE_CLI="ukbe-run-agent"

if [[ -f "$SCRIPT_DIR/.venv/bin/python" ]]; then
    RUNNER_CMD="$SCRIPT_DIR/.venv/bin/python -m agent_runner_v2.run_agent"
else
    if ! command -v "$UKBE_CLI" &>/dev/null; then
        echo "ERROR: '$UKBE_CLI' not found on PATH."
        echo "Install agent-runner-v2 first: pip install -e ."
        exit 1
    fi
    RUNNER_CMD="$UKBE_CLI"
fi

if [[ ! -d "$SCRIPT_DIR/workflows" ]]; then
    echo "ERROR: Required workflow source folder is missing: $SCRIPT_DIR/workflows"
    exit 1
fi

CMD="$RUNNER_CMD bootstrap-publish"

echo "==========================================================================="
echo " Bootstrap Bundle Publish"
echo "==========================================================================="
echo " Repository root:  $SCRIPT_DIR"
echo ""
echo " Next step after publish:"
echo "   run-init.sh"
echo ""
echo " Command: $CMD"
echo "==========================================================================="
echo ""

eval "$CMD"
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "Bootstrap publish completed successfully."
    echo "Next step: run-init.sh"
else
    echo "Bootstrap publish exited with code $EXIT_CODE."
fi
exit $EXIT_CODE
