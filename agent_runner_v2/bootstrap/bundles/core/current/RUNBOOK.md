---
title: "Runbook"
template_id: "OPS-01-RB"
status: "active"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T11:57:31+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook: agent-runner-v2

## Operations Scope

This runbook covers operational procedures for the agent-runner-v2 system, including:
- Job state management and troubleshooting
- Runtime bundle administration
- Log inspection and rotation
- Sidecar validation and recovery
- Daemon supervision and health checks

## Routine Procedures

### Daily Operations

#### Check Job Status

**Location**: `~/.ukbe-runner/jobs/<workflow>/<job_id>/job.json`

```bash
# List active jobs
ls -la ~/.ukbe-runner/jobs/

# Check specific job status
cat ~/.ukbe-runner/jobs/<workflow>/<job_id>/job.json | jq '.status'
```

**Expected Status Values**:
- `PENDING` - Job created, not started
- `IN_PROGRESS` - Steps executing
- `WAITING_FOR_HUMAN_APPROVAL` - Waiting for user decision
- `COMPLETED` - Finished successfully
- `FAILED` - Step failed, not retrying
- `CANCELLED` - Manually cancelled

#### Monitor Daemon Health

**Process Check**:
```bash
# Windows
Get-Process -Name "python" | Where-Object {$_.CommandLine -like "*daemon*"}

# Or check for daemon log
tail ~/.ukbe-runner/logs/daemon.log
```

**Log Location**: `~/.ukbe-runner/logs/`

#### Verify Runtime Bundle

**Location**: `~/.ukbe-runner/workflows/default/`

```bash
# Check if templates exist
ls ~/.ukbe-runner/workflows/default/prompts/

# Check template_groups.py timestamp
ls -la ~/.ukbe-runner/workflows/default/template_groups.py
```

### Weekly Operations

#### Log Rotation

**Location**: `~/.ukbe-runner/logs/`

```bash
# Archive old logs (Windows PowerShell)
$logDir = "$env:USERPROFILE\.ukbe-runner\logs"
$archiveDir = "$env:USERPROFILE\.ukbe-runner\logs\archive"
New-Item -ItemType Directory -Force -Path $archiveDir
Get-ChildItem $logDir -Filter "*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Move-Item -Destination $archiveDir
```

#### Clean Old Jobs

**Location**: `~/.ukbe-runner/jobs/`

```bash
# List jobs older than 30 days (PowerShell)
Get-ChildItem ~/.ukbe-runner/jobs -Recurse -Directory | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)}

# Remove old job directories (careful!)
# Get-ChildItem ... | Remove-Item -Recurse -Force
```

#### Runtime Bundle Sync

**Trigger**: After bootstrap changes in repo

```bash
# Re-initialize to sync bundles
ukbe-run-agent init --project-root <path>

# Or use sync batch file
run-bootstrap-publish.bat
```

## Failure Handling

### Job Stuck in IN_PROGRESS

**Symptoms**: Job status shows `IN_PROGRESS` but no active processes

**Diagnosis**:
```bash
# Check for orphaned step
ls ~/.ukbe-runner/jobs/<wf>/<job>/
cat ~/.ukbe-runner/jobs/<wf>/<job>/job.json | jq '.current_step, .completed_steps'
```

**Resolution**:
1. Check if step actually running: `Get-Process python`
2. If orphaned, reset step: `run-reset-step.bat`
3. Or manually edit `job.json` to restore consistent state

### Meta.json Missing

**Symptoms**: Step failed with `MetaJsonMissingError`

**Diagnosis**:
```bash
# Check step directory
ls ~/.ukbe-runner/jobs/<wf>/<job>/<step>/

# Look for meta.json
cat ~/.ukbe-runner/jobs/<wf>/<job>/<step>/meta.json 2>/dev/null || echo "MISSING"
```

**Causes**:
1. LLM didn't write sidecar
2. Sidecar write failed
3. Path resolution error

**Resolution**:
1. Check step logs for errors
2. Retry step: `run-reset-step.bat` then resume
3. If persistent, check disk space and permissions

### Artifact Validation Failure

**Symptoms**: Step failed with `ArtifactMissingError` or validation error

**Diagnosis**:
```bash
# Check what artifacts exist
ls ~/.ukbe-runner/jobs/<wf>/<job>/<step>/

# Check meta.json for reported artifacts
cat ~/.ukbe-runner/jobs/<wf>/<job>/<step>/meta.json | jq '.coder_result.artifacts'
```

**Resolution**:
1. Verify artifacts exist on disk
2. Check paths in meta.json match actual paths
3. If mismatch, may be path resolution bug
4. Retry step after fixing

### Runtime Bundle Drift

**Symptoms**: Changes to bootstrap templates not taking effect

**Diagnosis**:
```bash
# Compare repo vs runtime
diff agent_runner_v2/bootstrap/workflows/default/template_groups.py ~/.ukbe-runner/workflows/default/template_groups.py
```

**Resolution**:
```bash
# Sync runtime bundle
ukbe-run-agent init --project-root <path>

# Or delete and re-init
Remove-Item -Recurse ~/.ukbe-runner/workflows/default
ukbe-run-agent init --project-root <path>
```

### Backend Connection Failure

**Symptoms**: Daemon can't claim work, worker mode fails

**Diagnosis**:
```bash
# Check engine config
cat ~/.ukbe-runner/engine/config.json | jq '.backend_url, .api_key'

# Test connectivity
Invoke-RestMethod -Uri "<backend_url>/health"
```

**Resolution**:
1. Verify network connectivity
2. Check API key validity
3. Verify backend URL correct
4. Check firewall rules

### Notification Failures

**Symptoms**: Expected notifications not received

**Diagnosis**:
```bash
# Check notification log
cat ~/.ukbe-runner/logs/notifications.log | tail -20

# Verify Pushover config
cat ~/.ukbe-runner/config.json | jq '.pushover'
```

**Resolution**:
1. Verify Pushover API key
2. Check user key configuration
3. Verify `enable_notifications: true` in step config
4. Check notification manager log

## Locations Reference

### Job State

| Location | Path | Purpose |
|----------|------|---------|
| Jobs root | `~/.ukbe-runner/jobs/` | All job directories |
| Job state | `~/.ukbe-runner/jobs/<wf>/<job>/job.json` | Job metadata and status |
| Step dirs | `~/.ukbe-runner/jobs/<wf>/<job>/<step>/` | Step working directories |
| Sidecars | `~/.ukbe-runner/jobs/<wf>/<job>/<step>/meta.json` | Step results |

### Runtime Bundles

| Location | Path | Purpose |
|----------|------|---------|
| Workflows root | `~/.ukbe-runner/workflows/` | All workflow bundles |
| Default bundle | `~/.ukbe-runner/workflows/default/` | Active workflow definitions |
| Templates | `~/.ukbe-runner/workflows/default/prompts/` | LLM prompt templates |
| Config | `~/.ukbe-runner/workflows/default/template_groups.py` | Step definitions |

### Logs

| Location | Path | Purpose |
|----------|------|---------|
| Logs root | `~/.ukbe-runner/logs/` | All log files |
| Daemon log | `~/.ukbe-runner/logs/daemon.log` | Daemon supervisor log |
| Step logs | `~/.ukbe-runner/jobs/<wf>/<job>/<step>/logs/` | Per-step execution logs |

### Configuration

| Location | Path | Purpose |
|----------|------|---------|
| User config | `~/.ukbe-runner/config.json` | User preferences, credentials |
| Engine config | `~/.ukbe-runner/engine/config.json` | Daemon/backend settings |

## Recovery Procedures

### Recover Failed Job

1. **Identify failure**:
   ```bash
   cat ~/.ukbe-runner/jobs/<wf>/<job>/job.json | jq '.last_failure'
   ```

2. **Check failure history**:
   ```bash
   cat ~/.ukbe-runner/jobs/<wf>/<job>/job.json | jq '.failure_history'
   ```

3. **Determine if retryable**:
   - Check retry counts in state
   - Verify not exceeded `max_retries`

4. **Reset and retry**:
   ```bash
   run-reset-step.bat
   # Or manually via backend UI
   ```

### Clean Corrupted Job State

**Warning**: Destructive operation

1. **Backup first**:
   ```bash
   Copy-Item ~/.ukbe-runner/jobs/<wf>/<job> ~/.ukbe-runner/jobs/<wf>/<job>.backup
   ```

2. **Inspect corruption**:
   ```bash
   cat ~/.ukbe-runner/jobs/<wf>/<job>/job.json | jq .
   ```

3. **Fix or delete**:
   - Option A: Edit `job.json` to restore consistency
   - Option B: Delete job and recreate

### Reinitialize Runner Home

**Warning**: Destroys all job history

1. **Backup**:
   ```bash
   Move-Item ~/.ukbe-runner ~/.ukbe-runner.backup
   ```

2. **Reinitialize**:
   ```bash
   ukbe-run-agent init --project-root <path>
   ```

3. **Restore config** (optional):
   ```bash
   Copy-Item ~/.ukbe-runner.backup/config.json ~/.ukbe-runner/
   ```

## Monitoring

### Key Metrics

| Metric | Location | Warning Threshold |
|--------|----------|-------------------|
| Job queue depth | Backend API or `~/.ukbe-runner/jobs/` | >100 pending |
| Step duration | `meta.json` recorded_at - created_at | >30 min per step |
| Daemon heartbeat | `~/.ukbe-runner/logs/daemon.log` | >60 sec gap |
| Disk usage | `~/.ukbe-runner/` | >80% full |

### Health Checks

```bash
# Job state health
python -c "
import json
from pathlib import Path
jobs_root = Path.home() / '.ukbe-runner' / 'jobs'
for wf_dir in jobs_root.iterdir():
    if wf_dir.is_dir():
        for job_dir in wf_dir.iterdir():
            job_file = job_dir / 'job.json'
            if job_file.exists():
                state = json.loads(job_file.read_text())
                if state['status'] == 'IN_PROGRESS':
                    print(f'WARNING: {job_dir.name} stuck in IN_PROGRESS')
"

# Runtime bundle health
python -c "
from pathlib import Path
wf_root = Path.home() / '.ukbe-runner' / 'workflows' / 'default'
required = ['template_groups.py', 'prompts/']
missing = [r for r in required if not (wf_root / r).exists()]
if missing:
    print(f'ERROR: Missing runtime files: {missing}')
else:
    print('Runtime bundle OK')
"
```

## Emergency Contacts

| Issue | Escalation |
|-------|------------|
| Backend API down | Backend team |
| LLM provider issues | Provider status page |
| Infrastructure | DevOps team |
| Documentation | Technical lead |
