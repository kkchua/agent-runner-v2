#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="openclaw-sandbox"
DATA_DIR="$HOME/openclaw-data"

echo "[openclaw] stopping backend..."
if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  if ! docker exec "$CONTAINER_NAME" bash -lc "
    PID_FILE=/tmp/agent-runner-backend.pid
    if [ -f \"\$PID_FILE\" ]; then
      PID=\$(cat \"\$PID_FILE\" 2>/dev/null || true)
      if [ -n \"\$PID\" ]; then
        kill \"\$PID\" >/dev/null 2>&1 || true
      fi
      rm -f \"\$PID_FILE\"
    fi
    pkill -f 'uvicorn agent_runner_backend.main:create_app' >/dev/null 2>&1 || true
  "; then
    echo "[openclaw] backend stop command returned non-zero, continuing..."
  fi
fi

echo "[openclaw] stopping gateway..."
if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  if ! docker exec "$CONTAINER_NAME" bash -lc "
    openclaw gateway stop >/tmp/openclaw-gateway-stop.log 2>&1 \
      || pkill -f 'openclaw gateway run' \
      || true
  "; then
    echo "[openclaw] gateway stop command returned non-zero, continuing..."
  fi
fi

echo "[openclaw] stopping compose services..."
docker compose stop

echo "[openclaw] fixing local data directory ownership..."
if [ -d "$DATA_DIR" ]; then
  sudo chown "$USER:$USER" "$DATA_DIR" 2>/dev/null || true
  chmod u+rwx "$DATA_DIR" 2>/dev/null || true
fi

echo "[openclaw] stopped"
