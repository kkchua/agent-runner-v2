#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="openclaw-sandbox"
DATA_DIR="$HOME/openclaw-data"
DASHBOARD_URL="http://127.0.0.1:18789/"
GATEWAY_LOG="/tmp/openclaw-gateway-start.log"
BACKEND_URL="http://127.0.0.1:8100/api/health"
BACKEND_LOG="/tmp/agent-runner-backend.log"

echo "[openclaw] preparing local data directory..."
mkdir -p "$DATA_DIR"

# Only fix top-level ownership. Avoid recursive chown/chmod on every start.
sudo chown "$USER:$USER" "$DATA_DIR" 2>/dev/null || true
chmod u+rwx "$DATA_DIR" 2>/dev/null || true

echo "[openclaw] starting compose services..."
docker compose up -d

echo "[openclaw] checking container..."
if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  echo "[openclaw] container is not running: $CONTAINER_NAME"
  echo "Check:"
  echo "  docker compose ps"
  echo "  docker logs $CONTAINER_NAME"
  exit 1
fi

echo "[openclaw] starting backend if needed..."
docker exec "$CONTAINER_NAME" bash -lc '
  set -e

  PID_FILE="/tmp/agent-runner-backend.pid"
  LOG_FILE="/tmp/agent-runner-backend.log"
  STARTER="/usr/local/bin/start-backend.sh"

  if wget -q -O- http://127.0.0.1:8100/api/health >/dev/null 2>&1; then
    echo "[backend] already reachable"
    exit 0
  fi

  if [ -f "$PID_FILE" ]; then
    OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" >/dev/null 2>&1; then
      echo "[backend] pid already running: $OLD_PID"
      exit 0
    fi
    rm -f "$PID_FILE"
  fi

  if [ ! -x "$STARTER" ]; then
    chmod +x "$STARTER" 2>/dev/null || true
  fi

  echo "[backend] launching backend..."
  rm -f "$LOG_FILE"

  nohup "$STARTER" >"$LOG_FILE" 2>&1 &
  echo "$!" > "$PID_FILE"

  echo "[backend] pid: $(cat "$PID_FILE")"
'

echo "[openclaw] starting gateway if needed..."
docker exec "$CONTAINER_NAME" bash -lc '
  set -e

  PID_FILE="/tmp/openclaw-gateway.pid"
  LOG_FILE="/tmp/openclaw-gateway-start.log"

  openclaw config set gateway.bind lan >/tmp/openclaw-config.log 2>&1 || true

  if wget -q -O- http://127.0.0.1:18789/ >/dev/null 2>&1; then
    echo "[openclaw] gateway already reachable"
    exit 0
  fi

  if [ -f "$PID_FILE" ]; then
    OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" >/dev/null 2>&1; then
      echo "[openclaw] gateway pid already running: $OLD_PID"
      exit 0
    fi
    rm -f "$PID_FILE"
  fi

  echo "[openclaw] launching gateway..."
  rm -f "$LOG_FILE"

  nohup openclaw gateway run >"$LOG_FILE" 2>&1 &
  echo "$!" > "$PID_FILE"

  echo "[openclaw] gateway pid: $(cat "$PID_FILE")"
'

echo "[openclaw] checking backend..."
for i in {1..60}; do
  if timeout 3 wget -q -O- "$BACKEND_URL" >/dev/null 2>&1; then
    echo "[openclaw] backend OK"
    break
  fi

  echo "[openclaw] waiting for backend... $i/60"
  sleep 2
done

if ! timeout 3 wget -q -O- "$BACKEND_URL" >/dev/null 2>&1; then
  echo "[openclaw] backend did not become ready."
  echo
  echo "Check:"
  echo "  docker compose ps"
  echo "  docker logs $CONTAINER_NAME"
  echo "  docker exec -it $CONTAINER_NAME bash"
  echo "  docker exec $CONTAINER_NAME bash -lc 'cat $BACKEND_LOG'"
  echo "  docker exec $CONTAINER_NAME bash -lc 'ps aux | grep uvicorn'"
  exit 1
fi

echo "[openclaw] checking dashboard..."
for i in {1..60}; do
  if timeout 3 wget -q -O- "$DASHBOARD_URL" >/dev/null 2>&1; then
    echo "[openclaw] dashboard OK"
    echo "Open: http://localhost:18789"
    exit 0
  fi

  echo "[openclaw] waiting for dashboard... $i/60"
  sleep 2
done

echo "[openclaw] dashboard did not become ready."
echo
echo "Check:"
echo "  docker compose ps"
echo "  docker logs $CONTAINER_NAME"
echo "  docker exec -it $CONTAINER_NAME bash"
echo "  docker exec $CONTAINER_NAME bash -lc 'cat $BACKEND_LOG'"
echo "  docker exec $CONTAINER_NAME bash -lc 'cat $GATEWAY_LOG'"
echo "  docker exec $CONTAINER_NAME bash -lc 'ps aux | egrep \"openclaw|uvicorn\"'"
exit 1
