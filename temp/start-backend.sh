#!/bin/bash
# Wrapper to start agent-runner-backend with correct DATABASE_URL.
# Compose service DNS names are the stable network addresses inside the container network.
# Use `postgres` instead of a hard-coded container_name alias.

set -euo pipefail

BACKEND_ROOT="/workspace/projects/agent-runner-backend"
PYTHON_BIN="$BACKEND_ROOT/.venv/bin/python3"
HEALTH_URL="http://127.0.0.1:8100/api/health"

# Override container-level env vars with the correct Compose network host.
export AGENT_RUNNER_DATABASE_URL="postgresql+psycopg2://postgres:postgres@postgres:5432/agentrunner"
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@postgres:5432/agentrunner"

echo "[backend] startup checks..."
echo "[backend] backend root: $BACKEND_ROOT"
echo "[backend] python bin:   $PYTHON_BIN"

if [ ! -d "$BACKEND_ROOT" ]; then
  echo "[backend] ERROR: backend root does not exist: $BACKEND_ROOT" >&2
  echo "[backend] Available project directories:" >&2
  ls -la /workspace/projects >&2 || true
  exit 1
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "[backend] ERROR: backend python does not exist or is not executable: $PYTHON_BIN" >&2
  echo "[backend] Contents of $BACKEND_ROOT:" >&2
  ls -la "$BACKEND_ROOT" >&2 || true
  echo "[backend] Contents of $BACKEND_ROOT/.venv/bin if present:" >&2
  ls -la "$BACKEND_ROOT/.venv/bin" >&2 || true
  exit 1
fi

cd "$BACKEND_ROOT"

# Verify the env vars are correct
echo "[backend] starting backend with:"
echo "[backend]   DATABASE_URL: $DATABASE_URL"
echo "[backend]   AGENT_RUNNER_DATABASE_URL: $AGENT_RUNNER_DATABASE_URL"

echo "[backend] import check..."
"$PYTHON_BIN" -c "import agent_runner_backend.main; print('import ok')" || {
  echo "[backend] ERROR: backend import check failed" >&2
  exit 1
}

# Start the backend on all interfaces so the host can reach the published port.
echo "[backend] launching uvicorn on 0.0.0.0:8100"
exec "$PYTHON_BIN" -m uvicorn agent_runner_backend.main:create_app --factory --host 0.0.0.0 --port 8100
