---
template_id: "OPS-01-RB"
managed_by: workflow-generated
generated: "2026-07-09T21:26:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook

## Operations Scope

This runbook covers operational procedures for running agent-runner-v2 in production environments, including:
- Daemon supervision and monitoring
- Job state inspection and troubleshooting
- Log analysis and failure investigation
- Routine maintenance procedures

## Routine Procedures

### Starting the Daemon

**Command**:
```bash
ukbe-run-agent daemon <worker-id> [options]
```

**Example**:
```bash
ukbe-run-agent daemon workstation-01 --backend-url http://backend:8100
```

**What it does**:
- Polls backend for available work
- Spawns child processes for step execution
- Tracks child state and emits heartbeats
- Writes execution logs to `~/.ukbe-runner/logs/`

### Checking Job Status

**Command**:
```bash
ukbe-run-agent status <job-id>
```

**Output**:
- Job status (IN_PROGRESS, COMPLETED, FAILED, etc.)
- Current step
- Retry history
- Artifact paths

### Listing Active Jobs

**Command**:
```bash
ukbe-run-agent list [--workflow <name>]
```

### Restarting a Failed Step

**Command**:
```bash
ukbe-run-agent retry <job-id> [--step <step-name>]
```

### Force-Approving a Step

**Command**:
```bash
ukbe-run-agent force-approve <job-id> [--step <step-name>]
```

**Caution**: Only use when the step outcome is known good but validation failed.

## Where Runtime State Lives

### Job State

**Location**: `~/.ukbe-runner/jobs/<workflow>/<job-id>/`

| File | Purpose |
|------|---------|
| `job.json` | Full job state, step history, artifacts |
| `<NN>_<step>/` | Step working directories |
| `<NN>_<step>/meta.json` | Step result sidecar |
| `<NN>_<step>/prompt.txt` | Rendered prompt |

**Job State Schema**:
- Version: 6 (v2)
- Key fields: `job_status`, `template_group`, `artifacts`, `retry_history`

### Runtime Bundles

**Location**: `~/.ukbe-runner/workflows/<workflow>/`

**Key Files**:
- `template_groups.py` — Workflow definitions
- `prompts/` — Prompt templates
- `job_schema.json` — Job schema
- `model_mapping.json` — Coder aliases

**Important**: Runtime loads from here, not the repo. Changes to repo bootstrap must be synced.

### Logs

**Location**: `~/.ukbe-runner/logs/`

| Log Type | Location | Format |
|----------|----------|--------|
| Daemon events | `daemon/<worker-id>/events.jsonl` | JSON Lines |
| Step execution | `steps/<workflow>/<job-id>/` | Per-step logs |
| Runner output | `runner/` | Text logs |

### Sidecars

**Location**: `~/.ukbe-runner/jobs/<workflow>/<job-id>/<NN>_<step>/meta.json`

**Purpose**: Structured result communication from coder to runner.

**Schema**:
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary",
    "artifacts": {"KEY": "path/to/file.md"},
    "recorded_at": "2026-07-09T21:26:23+08:00"
  }
}
```

## Failure Handling

### Common Failure Modes

| Failure | Symptom | Resolution |
|---------|---------|------------|
| `MetaJsonMissingError` | Coder didn't write sidecar | Check coder output, retry step |
| `MetaJsonInvalidError` | Sidecar malformed JSON | Check coder output, retry step |
| `ArtifactMissingError` | Declared artifact not found | Check coder output, retry step |
| `CoderInvocationError` | Coder process failed | Check coder installation, retry |
| `PreflightBlockedError` | Required artifact missing | Check prior step output |

### Control Classes

| Class | Meaning | Action |
|-------|---------|--------|
| `AUTO_RETRYABLE` | Transient failure, can retry | Automatic retry (if configured) |
| `HUMAN_RETRY_REQUIRED` | Needs human decision | Manual retry or intervention |
| `FATAL` | Unrecoverable failure | Job fails, investigate root cause |

### Investigating Step Failures

1. **Find the job**:
   ```bash
   ukbe-run-agent list | grep FAILED
   ```

2. **Check job state**:
   ```bash
   ukbe-run-agent status <job-id>
   ```

3. **Review step directory**:
   ```bash
   cat ~/.ukbe-runner/jobs/<workflow>/<job-id>/<step>/meta.json
   ```

4. **Check daemon logs** (if daemon mode):
   ```bash
   tail -50 ~/.ukbe-runner/logs/daemon/<worker-id>/events.jsonl
   ```

5. **Check step logs**:
   ```bash
   ls ~/.ukbe-runner/logs/steps/<workflow>/<job-id>/
   ```

### Orphaned Child Processes

**Symptom**: Jobs stuck IN_PROGRESS, no active child process.

**Resolution**:
1. Identify orphaned job: `ukbe-run-agent list`
2. Check process: `ps aux | grep <job-id>`
3. Kill orphaned process if necessary
4. Mark job failed or retry

### Daemon Recovery

**If daemon crashes**:
1. Check daemon logs: `~/.ukbe-runner/logs/daemon/<worker-id>/`
2. Identify last claimed work
3. Restart daemon: `ukbe-run-agent daemon <worker-id>`
4. Backend will re-claim orphaned work automatically

## Configuration

### Config File

**Location**: `~/.ukbe-runner/config.json`

**Example**:
```json
{
  "default_coder": "qwen",
  "workflows": {
    "default": {
      "path": "workflows/default"
    }
  },
  "engine_version": "SNAPSHOT"
}
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `AGENT_RUNNER_BACKEND_URL` | Backend URL for worker mode |
| `AGENT_RUNNER_WORKER_ID` | Worker ID for poll mode |
| `AGENT_RUNNER_V2_SRC` | Override Python source path |
| `WORKER_LABEL` | Worker queue label (live/dev) |
| `PUSHOVER_APP_TOKEN` | Pushover app token |
| `PUSHOVER_USER_KEY` | Pushover user key |

## Monitoring

### Health Checks

**Daemon Health**:
- Check `events.jsonl` for recent heartbeats
- Verify child processes are spawning
- Check backend connectivity

**Job Health**:
- Check for stuck IN_PROGRESS jobs
- Monitor retry counts
- Watch for repeated failures

### Key Metrics

| Metric | Where | Healthy Threshold |
|--------|-------|-------------------|
| Job completion rate | Backend dashboard | > 95% |
| Step retry rate | Job logs | < 10% |
| Daemon heartbeat | events.jsonl | < 60s since last |
| Child spawn time | events.jsonl | < 5s |

## Troubleshooting

### Workflow Bundle Not Found

**Error**: `Workflow module is not loaded`

**Resolution**:
1. Check workflow exists: `ls ~/.ukbe-runner/workflows/`
2. Re-initialize: `ukbe-run-agent init --workflow default`
3. Sync if using custom bundle: `sync-workflows-to-backend.bat`

### Coder Not Found

**Error**: `CoderInvocationError: coder not found`

**Resolution**:
1. Verify coder installation: `claude --version` or `qwen --version`
2. Check PATH: `echo $PATH` or `echo %PATH%`
3. Check coder alias in `model_mapping.json`

### Backend Connection Failed

**Error**: `BackendClient: connection refused`

**Resolution**:
1. Verify backend URL: `AGENT_RUNNER_BACKEND_URL`
2. Check network connectivity
3. Verify backend is running

### Step Timeout

**Error**: `Step timed out after N seconds`

**Resolution**:
1. Check step configuration: `coder_timeout_seconds`
2. Increase timeout if legitimate long-running step
3. Check coder output for hanging

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 04_generate_architecture_docs*
