---
template_id: "OPS-01-RB"
title: "Runbook - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:56:49+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook: agent-runner-v2

## Operations Scope

This runbook covers operational procedures for running and maintaining the agent-runner-v2 system in production and development environments.

## Routine Procedures

### Initialization

```bash
# Initialize runner home
ukbe-run-agent init

# Creates:
#   ~/.ukbe-runner/config.json
#   ~/.ukbe-runner/workflows/
#   ~/.ukbe-runner/jobs/
#   ~/.ukbe-runner/logs/
```

### Starting the Daemon

```bash
# Start daemon
ukbe-run-agent daemon kode-worker-01 --backend-url http://127.0.0.1:8100

# Daemon will:
# - Poll backend for work
# - Spawn child processes for steps
# - Track child state
# - Emit heartbeats
```

### Checking Job Status

```bash
# List job directories
ls ~/.ukbe-runner/jobs/

# Read job state
cat ~/.ukbe-runner/jobs/<job_id>/job.json

# Check step sidecars
ls ~/.ukbe-runner/jobs/<job_id>/steps/
cat ~/.ukbe-runner/jobs/<job_id>/steps/01_<step>/meta.json
```

### Log Rotation

Logs are stored in `~/.ukbe-runner/logs/` and rotated automatically:

```bash
# View current log
tail -f ~/.ukbe-runner/logs/agent-runner.log

# Archive old logs
mv ~/.ukbe-runner/logs/agent-runner.log ~/.ukbe-runner/logs/agent-runner.log.old
```

## Runtime Locations

| Resource | Path | Description |
|----------|------|-------------|
| **Job State** | `~/.ukbe-runner/jobs/<job_id>/job.json` | Job execution state |
| **Step Sidecars** | `~/.ukbe-runner/jobs/<job_id>/steps/<step>/meta.json` | Step results |
| **Runtime Bundles** | `~/.ukbe-runner/workflows/<workflow>/` | Workflow definitions |
| **Logs** | `~/.ukbe-runner/logs/` | Execution logs |
| **Config** | `~/.ukbe-runner/config.json` | Global configuration |

## Failure Handling

### Meta.json Missing

**Symptom**: Step fails with `MetaJsonMissingError`

**Resolution**:
1. Check if LLM process completed
2. Verify write permissions in step directory
3. Review LLM output for errors
4. Manual retry may be needed

### Artifact Missing

**Symptom**: Step fails with `ArtifactMissingError`

**Resolution**:
1. Check step sidecar for declared artifacts
2. Verify artifact paths exist
3. Review LLM output for file write errors
4. Correct paths in sidecar if needed

### Backend Unavailable

**Symptom**: Worker cannot connect to backend

**Resolution**:
1. Check backend URL in config
2. Verify network connectivity
3. Retry with exponential backoff
4. Degrade to local mode if needed

### Daemon Child Process Failure

**Symptom**: Step process exits with error

**Resolution**:
1. Check child process logs
2. Review step sidecar for errors
3. Verify step configuration
4. Restart daemon if needed

### Notification Failures

**Symptom**: Pushover notifications not received

**Resolution**:
1. Check Pushover credentials in config
2. Verify network connectivity
3. Check rate limits
4. Review notification logs

## Recovery Procedures

### Job Recovery

```bash
# Resume job from specific step
ukbe-run-agent run --template-group <workflow> --job-id <job_id> --resume-from <step>

# Or reset step and retry
ukbe-run-agent run --template-group <workflow> --job-id <job_id> --reset-step <step>
```

### Daemon Recovery

```bash
# Stop daemon (find PID)
taskkill /PID <daemon_pid> /F

# Restart daemon
ukbe-run-agent daemon <worker_id> --backend-url <url>
```

### Bootstrap/Runtime Sync

```bash
# Sync bootstrap to runtime
python -m agent_runner_v2.sync_workflows

# Re-initialize if needed
ukbe-run-agent init
```

## Monitoring

### Health Checks

| Check | Command | Expected |
|-------|---------|----------|
| Daemon running | `tasklist \| findstr python` | Python processes visible |
| Backend reachable | `curl <backend-url>/health` | HTTP 200 |
| Disk space | `df -h ~/.ukbe-runner` | >10% free |
| Job queue | Count jobs in `~/.ukbe-runner/jobs/` | Manageable |

### Key Metrics

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Workflow duration | job.json | >1 hour |
| Step failure rate | job.json | >10% |
| Daemon uptime | Process | <99% |
| Queue depth | job directories | >100 |

## Troubleshooting

### Debugging Steps

1. **Check logs**: `~/.ukbe-runner/logs/`
2. **Check job state**: `~/.ukbe-runner/jobs/<job_id>/job.json`
3. **Check sidecars**: `~/.ukbe-runner/jobs/<job_id>/steps/<step>/meta.json`
4. **Dry run**: Set `DRY_RUN=true` to render prompts without execution

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Path resolution errors | Windows pathlib edge cases | Use `constants.py` paths |
| Workflow not found | Bootstrap not synced | Run `sync_workflows.py` |
| LLM timeout | Slow response | Increase timeout in config |
| Permission denied | File access | Check Windows permissions |

### Getting Help

1. Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
2. Review [DECISION_LOG.md](DECISION_LOG.md)
3. Check recent changes in `docs/codebase/04_changes/`
4. Consult codebase inventory in `docs/codebase/01_inventory/`

---

*Last updated: 2026-07-10T19:56:49+08:00 via workflow `00_master_docs_bootstrap_v2`*
