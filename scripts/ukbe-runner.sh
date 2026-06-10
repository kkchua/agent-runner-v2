#!/usr/bin/env bash
# ukbe-runner.sh — convenience wrapper for ukbe-run-agent
#
# Usage:
#   ukbe-runner.sh worker start [worker-id]   -- start worker daemon in background
#   ukbe-runner.sh worker stop  [worker-id]   -- stop background worker
#   ukbe-runner.sh worker status [worker-id]  -- check if worker is running
#   ukbe-runner.sh submit [args...]            -- submit a run to the backend
#
# Worker ID defaults to the value in ~/.ukbe-runner/engine/config.json → worker_id,
# falling back to "kode-worker-01".

set -euo pipefail

UKBE_CLI="${UKBE_CLI:-ukbe-run-agent}"
PID_DIR="${HOME}/.ukbe-runner/workers"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_default_worker_id() {
    local cfg="${HOME}/.ukbe-runner/engine/config.json"
    if [[ -f "$cfg" ]]; then
        python3 -c "import json,sys; d=json.load(open('${cfg}')); print(d.get('worker_id','kode-worker-01'))" 2>/dev/null || echo "kode-worker-01"
    else
        echo "kode-worker-01"
    fi
}

_pid_file() {
    local worker_id="$1"
    echo "${PID_DIR}/${worker_id}.pid"
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

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

cmd_worker_start() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file
    pid_file=$(_pid_file "$worker_id")

    if _is_running "$pid_file"; then
        local existing_pid
        existing_pid=$(cat "$pid_file")
        echo "Worker '$worker_id' is already running (PID $existing_pid)."
        return 0
    fi

    mkdir -p "$PID_DIR"

    # Shift off the worker_id and pass remaining args to daemon
    shift 1 2>/dev/null || true

    echo "Starting worker '$worker_id'..."
    nohup "$UKBE_CLI" daemon "$worker_id" "$@" </dev/null >/dev/null 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"
    echo "Worker '$worker_id' started (PID $pid). PID saved to $pid_file"
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

    local pid
    pid=$(cat "$pid_file")
    echo "Stopping worker '$worker_id' (PID $pid)..."
    kill -TERM "$pid"

    # Wait up to 5s for graceful shutdown
    local i=0
    while kill -0 "$pid" 2>/dev/null && [[ $i -lt 10 ]]; do
        sleep 0.5
        ((i++))
    done

    if kill -0 "$pid" 2>/dev/null; then
        echo "Worker did not stop gracefully; sending SIGKILL..."
        kill -KILL "$pid" 2>/dev/null || true
    fi

    rm -f "$pid_file"
    echo "Worker '$worker_id' stopped."
}

cmd_worker_status() {
    local worker_id="${1:-$(_default_worker_id)}"
    local pid_file
    pid_file=$(_pid_file "$worker_id")

    if _is_running "$pid_file"; then
        local pid
        pid=$(cat "$pid_file")
        echo "Worker '$worker_id' is running (PID $pid)."
    else
        echo "Worker '$worker_id' is not running."
        [[ -f "$pid_file" ]] && rm -f "$pid_file"
        return 1
    fi
}

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
  $(basename "$0") submit [--workflow-name NAME] [args...]

Worker ID defaults to the worker_id field in ~/.ukbe-runner/engine/config.json.
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
            usage
            exit 1
        fi
        SUBCOMMAND="$1"
        shift
        case "$SUBCOMMAND" in
            start)  cmd_worker_start "$@" ;;
            stop)   cmd_worker_stop  "$@" ;;
            status) cmd_worker_status "$@" ;;
            *)
                echo "ERROR: unknown worker subcommand: $SUBCOMMAND" >&2
                usage
                exit 1
                ;;
        esac
        ;;
    submit)
        cmd_submit "$@"
        ;;
    *)
        echo "ERROR: unknown command: $COMMAND" >&2
        usage
        exit 1
        ;;
esac
