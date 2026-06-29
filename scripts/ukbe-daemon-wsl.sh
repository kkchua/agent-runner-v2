#!/usr/bin/env bash
# ukbe-daemon-wsl.sh — WSL/Linux convenience wrapper for ukbe-run-agent daemon
#
# Usage:
#   ukbe-daemon-wsl.sh start  [worker-id]  -- start worker daemon in background
#   ukbe-daemon-wsl.sh stop   [worker-id]  -- stop background worker
#   ukbe-daemon-wsl.sh status [worker-id]  -- check if worker is running
#   ukbe-daemon-wsl.sh logs   [worker-id]  -- tail worker log
#   ukbe-daemon-wsl.sh restart [worker-id] -- restart worker
#
# Worker ID defaults to the value in ~/.ukbe-runner/engine/config.json → worker_id,
# falling back to "kode-worker-01".

set -euo pipefail

UKBE_CLI="${UKBE_CLI:-ukbe-run-agent}"
CONFIG_DIR="${HOME}/.ukbe-runner"
PID_DIR="${CONFIG_DIR}/workers"
LOG_DIR="${CONFIG_DIR}/logs"
DEFAULT_WORKER_ID="kode-worker-01"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_read_config() {
    local key="$1" default="$2"
    local cfg="${CONFIG_DIR}/engine/config.json"
    if [[ -f "$cfg" ]]; then
        python3 -c "import json; d=json.load(open('${cfg}')); print(d.get('${key}','${default}'))" 2>/dev/null || echo "$default"
    else
        echo "$default"
    fi
}

_default_worker_id() {
    _read_config "worker_id" "$DEFAULT_WORKER_ID"
}

_pid_file() {
    local worker_id="$1"
    echo "${PID_DIR}/${worker_id}.pid"
}

_log_file() {
    local worker_id="$1"
    echo "${LOG_DIR}/worker-${worker_id}.log"
}

_is_running() {
    local pid_file="$1"
    if [[ ! -f "$pid_file" ]]; then
        return 1
    fi
    local pid
    pid=$(cat "$pid_file" 2>/dev/null) || return 1
    [[ -z "$pid" ]] && return 1
    kill -0 "$pid" 2>/dev/null
}

_ensure_dirs() {
    mkdir -p "$PID_DIR" "$LOG_DIR"
}

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

cmd_start() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file log_file
    pid_file=$(_pid_file "$worker_id")
    log_file=$(_log_file "$worker_id")

    if _is_running "$pid_file"; then
        echo "Worker '$worker_id' is already running (PID $(cat "$pid_file"))."
        echo "  Log:  $log_file"
        return 0
    fi

    _ensure_dirs

    # Clean up stale PID file
    rm -f "$pid_file"

    echo "Starting worker '$worker_id'..."
    echo "  Log:  $log_file"

    # Start daemon in background using nohup
    # Redirect both stdout and stderr to log file
    nohup "$UKBE_CLI" daemon "$worker_id" </dev/null >>"$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"

    # Wait a moment and verify process is still running
    sleep 1
    if ! kill -0 "$pid" 2>/dev/null; then
        rm -f "$pid_file"
        echo "ERROR: Worker '$worker_id' failed to start."
        echo "  Log:  $log_file"
        return 1
    fi

    echo "Worker '$worker_id' started (PID $pid)."
    echo "  Log:  $log_file"
    echo "  PID:  $pid_file"
}

cmd_stop() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file
    pid_file=$(_pid_file "$worker_id")

    if ! _is_running "$pid_file"; then
        echo "Worker '$worker_id' is not running."
        rm -f "$pid_file"
        return 0
    fi

    local pid
    pid=$(cat "$pid_file")
    echo "Stopping worker '$worker_id' (PID $pid)..."

    # Send SIGTERM for graceful shutdown
    kill -TERM "$pid" 2>/dev/null || { rm -f "$pid_file"; echo "Worker was already stopped."; return 0; }

    # Wait up to 5 seconds for graceful shutdown
    local i=0
    while kill -0 "$pid" 2>/dev/null && [[ $i -lt 10 ]]; do
        sleep 0.5
        i=$((i + 1))
    done

    # If still running, force kill
    if kill -0 "$pid" 2>/dev/null; then
        echo "Worker did not stop gracefully; sending SIGKILL..."
        kill -KILL "$pid" 2>/dev/null || true
    fi

    rm -f "$pid_file"
    echo "Worker '$worker_id' stopped."
}

cmd_status() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file log_file
    pid_file=$(_pid_file "$worker_id")
    log_file=$(_log_file "$worker_id")

    if _is_running "$pid_file"; then
        echo "Worker '$worker_id' is running (PID $(cat "$pid_file"))."
        echo "  Log:  $log_file"
    else
        echo "Worker '$worker_id' is not running."
        if [[ -f "$log_file" ]]; then
            echo "  Log:  $log_file"
        fi
        rm -f "$pid_file"
        return 1
    fi
}

cmd_logs() {
    local worker_id="${1:-$(_default_worker_id)}"
    local log_file
    log_file=$(_log_file "$worker_id")

    if [[ ! -f "$log_file" ]]; then
        echo "No log file found at $log_file"
        exit 1
    fi

    echo "Showing logs for worker '$worker_id' (Ctrl+C to exit):"
    echo ""
    exec tail -f "$log_file"
}

cmd_restart() {
    local worker_id="${1:-$(_default_worker_id)}"
    cmd_stop "$worker_id" || true
    sleep 1
    cmd_start "$worker_id"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage:
  $(basename "$0") start  [worker-id]  -- start worker daemon
  $(basename "$0") stop   [worker-id]  -- stop worker daemon
  $(basename "$0") status [worker-id]  -- check if worker is running
  $(basename "$0") logs   [worker-id]  -- tail worker log (Ctrl+C to exit)
  $(basename "$0") restart [worker-id] -- restart worker daemon

Worker ID defaults to worker_id in ~/.ukbe-runner/engine/config.json
EOF
}

if [[ $# -lt 1 ]]; then
    usage
    exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
    start)  cmd_start "$@" ;;
    stop)   cmd_stop  "$@" ;;
    status) cmd_status "$@" ;;
    logs)   cmd_logs  "$@" ;;
    restart) cmd_restart "$@" ;;
    *)
        echo "ERROR: unknown command: $COMMAND" >&2
        usage
        exit 1
        ;;
esac
