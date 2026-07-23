#!/usr/bin/env bash
# sync-workflows-to-backend.sh - Publish runner workflow definitions into the backend registry.
#
# Usage:
#   ./sync-workflows-to-backend.sh
#   ./sync-workflows-to-backend.sh codebase_bootstrap_v1
#   ./sync-workflows-to-backend.sh delivery_scaffold_v1 bug_fix_v1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate .venv if it exists
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

BACKEND_URL=""

if [[ ! -d "$SCRIPT_DIR/workflows" ]]; then
    echo "ERROR: Required workflow source folder is missing: $SCRIPT_DIR/workflows"
    exit 1
fi

echo "==========================================================================="
echo " Workflow Sync Publish"
echo "==========================================================================="
echo " Backend URL:  ${BACKEND_URL:-<from ~/.ukbe-runner/config.json / CLI default>}"
echo "==========================================================================="
echo ""

if [[ -f "$SCRIPT_DIR/.venv/bin/python" ]]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "ERROR: Cannot find Python or .venv/bin/python."
    exit 1
fi

FLAGS=""
[[ -n "$BACKEND_URL" ]] && FLAGS="--backend-url $BACKEND_URL"

"$PYTHON" -m agent_runner_v2.sync_workflows $FLAGS "$@"
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "Workflow definitions published successfully."
else
    echo "Workflow publish failed (exit code $EXIT_CODE)."
fi
exit $EXIT_CODE
