#!/usr/bin/env bash
# run-cleanup-workflow.sh - Delete execution history for a workflow before re-sync.
#
# Usage:
#   ./run-cleanup-workflow.sh <workflow_name>
#   ./run-cleanup-workflow.sh 00_repo_master_docs_bootstrap_v1

set -euo pipefail

# ==================================================================
# Configuration
# ==================================================================

BACKEND_URL="http://127.0.0.1:8100"

# ==================================================================
# Argument validation
# ==================================================================

if [[ $# -lt 1 ]]; then
    echo "ERROR: Missing workflow_name argument."
    echo ""
    echo "Usage: $(basename "$0") <workflow_name>"
    echo "Example: $(basename "$0") 00_repo_master_docs_bootstrap_v1"
    exit 1
fi

WORKFLOW_NAME="$1"

echo "==========================================================================="
echo " Workflow Execution Cleanup"
echo "==========================================================================="
echo " Backend URL:     $BACKEND_URL"
echo " Workflow Name:   $WORKFLOW_NAME"
echo "==========================================================================="
echo ""

# ==================================================================
# Step 1: Dry-run to preview deletions
# ==================================================================

echo "[Step 1] Dry-run: Previewing deletions..."
echo ""

BODY="{\"dry_run\": true, \"include_workers\": false, \"scope\": {\"workflow_name\": \"$WORKFLOW_NAME\"}}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BACKEND_URL}/api/admin/execution/cleanup" \
    -H "Content-Type: application/json" -d "$BODY")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 400 ]]; then
    echo "ERROR: Dry-run failed (HTTP $HTTP_CODE)."
    echo "$RESPONSE_BODY"
    exit 1
fi

echo "Dry-run result:"
echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"

echo ""
echo "==========================================================================="
echo " The above counts show what WOULD be deleted."
echo "==========================================================================="
echo ""

# ==================================================================
# Step 2: Confirm before actual deletion
# ==================================================================

read -rp "Proceed with actual deletion? [y/N]: " CONFIRM
if [[ "${CONFIRM,,}" != "y" ]]; then
    echo "Aborted. No changes were made."
    exit 0
fi

echo ""
echo "[Step 2] Executing cleanup..."
echo ""

BODY="{\"dry_run\": false, \"include_workers\": false, \"scope\": {\"workflow_name\": \"$WORKFLOW_NAME\"}}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BACKEND_URL}/api/admin/execution/cleanup" \
    -H "Content-Type: application/json" -d "$BODY")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 400 ]]; then
    echo "ERROR: Cleanup failed (HTTP $HTTP_CODE)."
    echo "$RESPONSE_BODY"
    exit 1
fi

echo "Cleanup result:"
echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"

echo ""
echo "==========================================================================="
echo " Cleanup completed successfully."
echo "==========================================================================="
echo ""
echo "Next step: Re-sync the workflow"
echo "  sync-workflows-to-backend.sh $WORKFLOW_NAME"
