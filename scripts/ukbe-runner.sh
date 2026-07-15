#!/usr/bin/env bash
# ukbe-runner.sh — convenience wrapper for ukbe-run-agent and the backend server
#
# Usage:
#   ukbe-runner.sh worker start  [worker-id]  -- start worker daemon in background
#   ukbe-runner.sh worker stop   [worker-id]  -- stop background worker
#   ukbe-runner.sh worker status [worker-id]  -- check if worker is running
#   ukbe-runner.sh backend start              -- start FastAPI backend in background
#   ukbe-runner.sh backend stop               -- stop background backend
#   ukbe-runner.sh backend status             -- check if backend is running
#   ukbe-runner.sh backend logs               -- tail backend log
#   ukbe-runner.sh submit [args...]           -- submit a run to the backend
#
# Worker ID defaults to the value in ~/.ukbe-runner/config.json → worker_id,
# falling back to "kode-worker-01".
#
# Backend dir defaults to BACKEND_DIR env var, falling back to
# ~/.ukbe-runner/config.json → backend_dir, then to the script's grandparent
# directory (works if ukbe-runner.sh lives inside the backend repo).

set -euo pipefail

UKBE_CLI="${UKBE_CLI:-ukbe-run-agent}"
PID_DIR="${HOME}/.ukbe-runner/workers"
BACKEND_PID_FILE="${HOME}/.ukbe-runner/backend.pid"
BACKEND_LOG_FILE="${HOME}/.ukbe-runner/logs/backend.log"
WORKER_LOG_DIR="${HOME}/.ukbe-runner/logs"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_read_config() {
    local key="$1" default="$2"
    local cfg="${HOME}/.ukbe-runner/config.json"
    if [[ -f "$cfg" ]]; then
        python3 -c "import json; d=json.load(open('${cfg}')); print(d.get('${key}','${default}'))" 2>/dev/null || echo "$default"
    else
        echo "$default"
    fi
}

_default_worker_id() {
    _read_config "worker_id" "kode-worker-01"
}

_default_backend_dir() {
    if [[ -n "${BACKEND_DIR:-}" ]]; then
        echo "$BACKEND_DIR"
        return
    fi
    local cfg_dir
    cfg_dir=$(_read_config "backend_dir" "")
    if [[ -n "$cfg_dir" ]]; then
        echo "$cfg_dir"
        return
    fi
    # Last resort: assume ukbe-runner.sh lives at <backend-repo>/agent_runner_v2/scripts/
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../" && pwd)"
}

_pid_file() {
    local worker_id="$1"
    echo "${PID_DIR}/${worker_id}.pid"
}

_worker_log_file() {
    local worker_id="$1"
    echo "${WORKER_LOG_DIR}/worker-${worker_id}.log"
}

_is_running() {
    local pid_file="$1"
    if [[ ! -f "$pid_file" ]]; then
        return 1
    fi
    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    return 1
}

_kill_pid_file() {
    local pid_file="$1" label="$2"
    local pid
    pid=$(cat "$pid_file")
    echo "Stopping $label (PID $pid)..."
    kill -TERM "$pid" 2>/dev/null || { rm -f "$pid_file"; echo "$label was already stopped."; return 0; }

    local i=0
    while kill -0 "$pid" 2>/dev/null && [[ $i -lt 10 ]]; do
        sleep 0.5
        i=$((i + 1))
    done

    if kill -0 "$pid" 2>/dev/null; then
        echo "$label did not stop gracefully; sending SIGKILL..."
        kill -KILL "$pid" 2>/dev/null || true
    fi

    rm -f "$pid_file"
    echo "$label stopped."
}

# ---------------------------------------------------------------------------
# Worker commands
# ---------------------------------------------------------------------------

cmd_worker_start() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file worker_log_file
    pid_file=$(_pid_file "$worker_id")
    worker_log_file=$(_worker_log_file "$worker_id")

    if _is_running "$pid_file"; then
        echo "Worker '$worker_id' is already running (PID $(cat "$pid_file"))."
        echo "  Log:  $worker_log_file"
        return 0
    fi

    mkdir -p "$PID_DIR" "$(dirname "$worker_log_file")"
    shift 1 2>/dev/null || true

    echo "Starting worker '$worker_id'..."
    nohup "$UKBE_CLI" daemon "$worker_id" "$@" </dev/null >>"$worker_log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"

    local i=0
    while [[ $i -lt 5 ]]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            rm -f "$pid_file"
            echo "ERROR: Worker '$worker_id' failed to stay running."
            echo "  Log:  $worker_log_file"
            return 1
        fi
        sleep 0.2
        i=$((i + 1))
    done

    echo "Worker '$worker_id' started (PID $pid)."
    echo "  Log:  $worker_log_file"
    echo "  PID:  $pid_file"
}

cmd_worker_stop() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file
    pid_file=$(_pid_file "$worker_id")

    if ! _is_running "$pid_file"; then
        echo "Worker '$worker_id' is not running."
        [[ -f "$pid_file" ]] && rm -f "$pid_file"
        return 0
    fi

    _kill_pid_file "$pid_file" "Worker '$worker_id'"
}

cmd_worker_status() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file worker_log_file
    pid_file=$(_pid_file "$worker_id")
    worker_log_file=$(_worker_log_file "$worker_id")

    if _is_running "$pid_file"; then
        echo "Worker '$worker_id' is running (PID $(cat "$pid_file"))."
        echo "  Log:  $worker_log_file"
    else
        echo "Worker '$worker_id' is not running."
        if [[ -f "$worker_log_file" ]]; then
            echo "  Log:  $worker_log_file"
        fi
        [[ -f "$pid_file" ]] && rm -f "$pid_file"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Backend commands
# ---------------------------------------------------------------------------

cmd_backend_start() {
    if _is_running "$BACKEND_PID_FILE"; then
        echo "Backend is already running (PID $(cat "$BACKEND_PID_FILE"))."
        return 0
    fi

    local backend_dir
    backend_dir=$(_default_backend_dir)

    if [[ ! -f "${backend_dir}/start-backend.sh" ]]; then
        echo "ERROR: start-backend.sh not found in ${backend_dir}" >&2
        echo "Set BACKEND_DIR or add backend_dir to ~/.ukbe-runner/config.json" >&2
        exit 1
    fi

    mkdir -p "$(dirname "$BACKEND_LOG_FILE")"

    echo "Starting backend from ${backend_dir}..."
    nohup bash "${backend_dir}/start-backend.sh" </dev/null >"$BACKEND_LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$BACKEND_PID_FILE"
    echo "Backend started (PID $pid)."
    echo "  Log:  $BACKEND_LOG_FILE"
    echo "  PID:  $BACKEND_PID_FILE"
}

cmd_backend_stop() {
    if ! _is_running "$BACKEND_PID_FILE"; then
        echo "Backend is not running."
        [[ -f "$BACKEND_PID_FILE" ]] && rm -f "$BACKEND_PID_FILE"
        return 0
    fi

    _kill_pid_file "$BACKEND_PID_FILE" "Backend"
}

cmd_backend_status() {
    if _is_running "$BACKEND_PID_FILE"; then
        echo "Backend is running (PID $(cat "$BACKEND_PID_FILE"))."
    else
        echo "Backend is not running."
        [[ -f "$BACKEND_PID_FILE" ]] && rm -f "$BACKEND_PID_FILE"
        return 1
    fi
}

cmd_backend_logs() {
    if [[ ! -f "$BACKEND_LOG_FILE" ]]; then
        echo "No log file found at $BACKEND_LOG_FILE"
        exit 1
    fi
    exec tail -f "$BACKEND_LOG_FILE"
}

# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------

cmd_submit() {
    exec "$UKBE_CLI" submit "$@"
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage:
  $(basename "$0") worker start  [worker-id] [daemon-args...]
  $(basename "$0") worker stop   [worker-id]
  $(basename "$0") worker status [worker-id]
  $(basename "$0") backend start
  $(basename "$0") backend stop
  $(basename "$0") backend status
  $(basename "$0") backend logs
  $(basename "$0") submit [--workflow-name NAME] [args...]

Worker ID defaults to worker_id in ~/.ukbe-runner/config.json.
Backend dir defaults to BACKEND_DIR env var, or backend_dir in config.json.
Run 'ukbe-run-agent daemon --help' or 'ukbe-run-agent submit --help' for full options.
EOF
}

if [[ $# -lt 1 ]]; then
    usage
    exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
    worker)
        if [[ $# -lt 1 ]]; then
            echo "ERROR: expected 'start', 'stop', or 'status' after 'worker'" >&2
            usage; exit 1
        fi
        SUBCOMMAND="$1"; shift
        case "$SUBCOMMAND" in
            start)  cmd_worker_start "$@" ;;
            stop)   cmd_worker_stop  "$@" ;;
            status) cmd_worker_status "$@" ;;
            *) echo "ERROR: unknown worker subcommand: $SUBCOMMAND" >&2; usage; exit 1 ;;
        esac
        ;;
    backend)
        if [[ $# -lt 1 ]]; then
            echo "ERROR: expected 'start', 'stop', 'status', or 'logs' after 'backend'" >&2
            usage; exit 1
        fi
        SUBCOMMAND="$1"; shift
        case "$SUBCOMMAND" in
            start)  cmd_backend_start ;;
            stop)   cmd_backend_stop  ;;
            status) cmd_backend_status ;;
            logs)   cmd_backend_logs  ;;
            *) echo "ERROR: unknown backend subcommand: $SUBCOMMAND" >&2; usage; exit 1 ;;
        esac
        ;;
    submit)
        cmd_submit "$@"
        ;;
    *)
        echo "ERROR: unknown command: $COMMAND" >&2
        usage; exit 1
        ;;
esac

