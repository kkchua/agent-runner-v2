# Worker Supervisor Manual

## Overview

This manual describes how to operate `agent-runner-v2` as a backend-connected workstation worker.

For workflow-specific backend run submission parameters, use [submit_job_manual.md](submit_job_manual.md).

Key concepts:

- `worker_id`: stable identifier for the workstation
- daemon: supervisor process for that workstation
- child execution: one claimed `workflow_step_run_id` executed by one child process
- backend: source of truth for run and step state

The daemon does not create synthetic child worker IDs. One workstation keeps one `worker_id` and may run multiple child executions concurrently when configured to do so.

## Execution Modes

### Manual local workflow run

Use this when you want to run a workflow directly without backend worker orchestration.

```bash
ukbe-run-agent run --template-group initiative_intake_v1 --set DRAFT_INIT_FILE=docs/delivery/01_initiatives/draft/example.md
```

### Backend one-shot claim and execute

```bash
ukbe-run-agent worker --backend-url http://127.0.0.1:8100 --worker-id kode-worker-01 --once
```

This claims at most one step, executes it, submits the result, and exits.

### Workstation daemon supervisor

```bash
ukbe-run-agent daemon kode-worker-01 --backend-url http://127.0.0.1:8100
```

This keeps polling the backend, spawns child `execute-step` processes, supervises them, and reports child state.

## Configuration

Persistent daemon settings should live in `.ukbe-runner/engine/config.json`.

Example:

```json
{
  "worker_id": "kode-worker-01",
  "worker_label": "live",
  "backend_url": "http://127.0.0.1:8100",
  "poll_seconds": 5,
  "max_parallel": 1,
  "stalled_seconds": 300,
  "step_timeout_seconds": 3600,
  "kill_grace_seconds": 30,
  "log_file": ".ukbe-runner/logs/worker-daemon.jsonl",
  "runtime_dir": ".ukbe-runner/runtime/worker"
}
```

Resolution order per setting:

1. CLI flag
2. environment variable
3. `.ukbe-runner/engine/config.json`
4. hardcoded default

## Important Paths

### Persistent config

- `.ukbe-runner/engine/config.json`

### Runtime state

- `.ukbe-runner/runtime/worker/`

Each child execution gets a directory under this path keyed by `workflow_step_run_id`.

Typical files:

- `request.json`
- `result.json`
- `child.log`
- `child-events.jsonl`

### Logs

- daemon log: `.ukbe-runner/logs/worker-daemon.jsonl`
- child log: `.ukbe-runner/runtime/worker/<workflow_step_run_id>/child.log`
- child event log: `.ukbe-runner/runtime/worker/<workflow_step_run_id>/child-events.jsonl`

## Running the Daemon

### Start with config defaults

```bash
ukbe-run-agent daemon kode-worker-01
```

### Override backend URL and concurrency

```bash
ukbe-run-agent daemon kode-worker-01   --backend-url http://127.0.0.1:8100   --max-parallel 2
```

### Useful daemon flags

- `--backend-url`
- `--poll-seconds`
- `--max-parallel`
- `--runtime-dir`
- `--log-file`
- `--stalled-seconds`
- `--step-timeout-seconds`
- `--kill-grace-seconds`

## Child Heartbeats and Visibility

The daemon emits child-scoped heartbeat/status updates keyed by `workflow_step_run_id`.

These updates include:

- `worker_id`
- `workflow_run_id`
- `workflow_step_run_id`
- `run_code`
- `pid`
- `state`
- `log_file`
- `watchdog_reason`
- `exit_code`

This allows one workstation `worker_id` to supervise multiple child executions while keeping per-step visibility.

## Child States

Expected daemon-reported child states:

- `running`
- `stalled`
- `timed_out`
- `killed`
- `completed`
- `failed`
- `submit_failed`

## Troubleshooting

### Daemon appears idle

Check:

- backend connectivity
- `worker_label`
- target worker assignment on the run
- `.ukbe-runner/logs/worker-daemon.jsonl`

Look for:

- `poll_started`
- `poll_no_work`
- `step_claimed`

### Child looks stuck

Check the child log and event log under `.ukbe-runner/runtime/worker/<workflow_step_run_id>/`.

If the process stays alive but no log or result activity occurs past `stalled_seconds`, the daemon marks it `stalled`.

If runtime exceeds `step_timeout_seconds`, the daemon marks it `timed_out`, sends `SIGTERM`, waits `kill_grace_seconds`, and then sends `SIGKILL` if necessary.

### Backend shows no progress

Use both sources together:

- backend run events and step status
- local daemon and child logs

If backend status is static but local logs continue, the execution may still be running normally and only final submission has not happened yet.

If local logs also stop changing, inspect for `child_stalled`, `child_timeout`, `child_terminated`, or `result_submit_failed`.

### Manual step execution debugging

You can run a backend request directly:

```bash
ukbe-run-agent execute-step --request-file /tmp/request.json --result-file /tmp/result.json
```

This is the fastest way to verify whether a failure is in prompt/coder execution versus daemon supervision.

## Operational Recommendations

- Keep one stable `worker_id` per workstation.
- Start with `max_parallel = 1` until reliability is proven.
- Treat local logs as the primary live-debug surface.
- Use backend events as execution audit history.
- Do not rely on `current_step_run_id` alone for multi-child visibility.
