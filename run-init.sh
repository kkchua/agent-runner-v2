#!/usr/bin/env bash
# run-init.sh - Install the packaged bootstrap bundle into runner home and seed workflows
#
# Usage:
#   ./run-init.sh [--workflow <name>] [--bundle-domain <name>] [--bundle-profile <name>]
#
# Sequence:
#   1. Run run-bootstrap-publish.sh after changing bootstrap docs or repo workflow packages.
#   2. Run this script to install the packaged bundle into ~/.ukbe-runner/
#      and seed the example workflow bundle.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate .venv if it exists
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

UKBE_CLI="ukbe-run-agent"
WORKFLOW="default"
BUNDLE_DOMAIN="general"
BUNDLE_PROFILE="core+workflow"

usage() {
    echo "Usage: $(basename "$0") [--workflow <name>] [--bundle-domain <name>] [--bundle-profile <name>]"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --workflow) WORKFLOW="$2"; shift 2 ;;
        --bundle-domain) BUNDLE_DOMAIN="$2"; shift 2 ;;
        --bundle-profile) BUNDLE_PROFILE="$2"; shift 2 ;;
        *) echo "ERROR: Unknown option: $1"; usage; exit 1 ;;
    esac
done

if ! command -v "$UKBE_CLI" &>/dev/null; then
    echo "ERROR: '$UKBE_CLI' not found on PATH."
    echo "Install agent-runner-v2 first: pip install -e ."
    exit 1
fi

if [[ ! -d "$SCRIPT_DIR/docs/system/00_governance/bootstrap" ]]; then
    echo "ERROR: Required bootstrap snapshot folder is missing: $SCRIPT_DIR/docs/system/00_governance/bootstrap"
    exit 1
fi

CMD="$UKBE_CLI init --workflow \"$WORKFLOW\" --bundle-domain \"$BUNDLE_DOMAIN\" --bundle-profile \"$BUNDLE_PROFILE\""

echo "==========================================================================="
echo " Runner Init"
echo "==========================================================================="
echo " Repository root:  $SCRIPT_DIR"
echo " Workflow:         $WORKFLOW"
echo " Bundle domain:    $BUNDLE_DOMAIN"
echo " Bundle profile:   $BUNDLE_PROFILE"
echo ""
echo " Recommended sequence:"
echo "   1. run-bootstrap-publish.sh"
echo "   2. run-init.sh"
echo ""
echo " Command: $CMD"
echo "==========================================================================="
echo ""

eval "$CMD"
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "Init completed successfully."
else
    echo "Init exited with code $EXIT_CODE."
fi
exit $EXIT_CODE
