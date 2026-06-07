#!/bin/bash
# test-delivery-scaffold.sh — Run delivery_scaffold_v1 with full logging
# Captures all CLI output, step transitions, errors, and timing

set -e

PROJECT_ROOT="/workspace/projects/agent-runner-v2"
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/delivery-scaffold-${TIMESTAMP}.log"
SUMMARY_FILE="${LOG_DIR}/delivery-scaffold-summary-${TIMESTAMP}.md"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "============================================================================"
echo "  delivery_scaffold_v1 — Real Test Run"
echo "  Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "  Log file: $LOG_FILE"
echo "============================================================================"
echo ""

# Check backend is running
echo "[test-runner] Checking backend health..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8100/api/health 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" != "200" ]; then
    echo "[test-runner] ⚠️  Backend not running on :8100 (HTTP $BACKEND_STATUS)"
    echo "[test-runner] Starting backend..."
    cd "$PROJECT_ROOT" && python3 -m uvicorn agent_runner_backend.main:create_app --factory --host 0.0.0.0 --port 8100 &
    sleep 3
fi

# Check worker is registered
echo "[test-runner] Checking worker status..."
WORKER_STATUS=$(curl -s http://localhost:8100/api/workers/list 2>/dev/null || echo "[]")
echo "[test-runner] Workers: $WORKER_STATUS"
echo ""

# Create new job with --new-job flag
echo "[test-runner] === STEP 0: Creating new delivery_scaffold_v1 job ==="
echo ""

cd "$PROJECT_ROOT"

# Run the first step (project_analysis — no seed files needed)
python3 -m agent_runner_v2.run_agent \
    --template-group delivery_scaffold_v1 \
    --new-job \
    --project-root "$PROJECT_ROOT" \
    2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "============================================================================"
echo "  First step completed with exit code: $EXIT_CODE"
echo "  Log: $LOG_FILE"
echo "============================================================================"

# Capture the job ID from the log
JOB_ID=$(grep -o '"job_id": "[^"]*"' "$LOG_FILE" | head -1 | cut -d'"' -f4)
if [ -n "$JOB_ID" ]; then
    echo ""
    echo "[test-runner] Job ID: $JOB_ID"
    
    # Save job state snapshot
    echo ""
    echo "[test-runner] === Job State ==="
    python3 -m agent_runner_v2.run_agent \
        --template-group delivery_scaffold_v1 \
        --job-id "$JOB_ID" \
        --show-job \
        2>&1 | tee -a "$LOG_FILE"
    
    echo ""
    echo "[test-runner] To continue the job, run:"
    echo "  python3 -m agent_runner_v2.run_agent --template-group delivery_scaffold_v1 --job-id $JOB_ID --project-root $PROJECT_ROOT"
fi

exit $EXIT_CODE
