---
title: "Runbook: agent-runner-v2"
template_id: "OPS-01-RB"
status: "active"
managed_by: workflow-generated
created: "2026-07-02T20:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Runbook: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

## 1. Operational Overview

### 1.1 Key Concepts

| Concept | Description |
|---------|-------------|
| **Job** | A workflow execution instance with unique ID |
| **Step** | A single unit of work within a workflow |
| **Sidecar** | The `meta.json` file containing step results |
| **Runner Home** | Global runtime directory (`%USERPROFILE%\.ukbe-runner\`) |
| **Workflow Bundle** | A collection of templates and prompts for a workflow |
| **Action** | Deterministic operation performed by the runner |

### 1.2 Runtime Paths

| Path | Windows | Description |
|------|---------|-------------|
| Runner Home | `%USERPROFILE%\.ukbe-runner\` | Global runtime directory |
| Jobs | `%USERPROFILE%\.ukbe-runner\jobs\<group>\<job-id>\` | Job state |
| Workflows | `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\` | Workflow bundles |
| Logs | `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

## 2. Job State Management

### 2.1 Where Job State Lives

Job state is stored in JSON files:

```
%USERPROFILE%\.ukbe-runner\jobs\<group>\<job-id>\
├── job.json              # Main job state
├── <step-01>\            # Step directory
│   ├── meta.json         # Step result sidecar
│   ├── prompt.txt        # Rendered prompt
│   └── debug\            # Debug outputs
└── ...
```

### 2.2 Key Job State Fields

```json
{
  "job_id": "uuid",
  "job_status": "IN_PROGRESS",
  "template_group": "workflow_name",
  "current_step": "step_name",
  "completed_steps": [...],
  "artifacts": {...},
  "retry_history": [...],
  "schema_version": 6,
  "runner_version": "v2"
}
```

### 2.3 Job Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `CREATED` | Job initialized | Run first step |
| `IN_PROGRESS` | Step executing | Wait for completion |
| `WAITING_FOR_AUTO_RETRY` | Failed, will retry | Automatic retry |
| `WAITING_FOR_HUMAN_INTERVENTION` | Failed, needs help | Manual intervention |
| `WAITING_FOR_HUMAN_APPROVAL` | Step complete, needs approval | Approve or reject |
| `COMPLETED` | Workflow finished | Archive job |
| `FAILED` | Terminal failure | Investigate |

### 2.4 Inspecting Job State

```bash
# Read job state (Windows PowerShell)
Get-Content "$env:USERPROFILE\.ukbe-runner\jobs\default\<job-id>\job.json" | ConvertFrom-Json

# Read step result
Get-Content "$env:USERPROFILE\.ukbe-runner\jobs\default\<job-id>\<step>\meta.json" | ConvertFrom-Json

# List all jobs
Get-ChildItem "$env:USERPROFILE\.ukbe-runner\jobs\default\" | Select-Object Name
```

## 3. Runtime Bundle Management

### 3.1 Where Bundles Live

| Location | Path | Purpose |
|----------|------|---------|
| Bootstrap | `agent_runner_v2/bootstrap/workflows/default/` | Package source |
| Runtime | `%USERPROFILE%\.ukbe-runner\workflows\default\` | Active execution |

### 3.2 Bundle Initialization

Initialize or refresh the runtime bundle:

```bash
ukbe-run-agent init
```

This seeds the runtime home from the package bootstrap.

### 3.3 Bundle Updates

To update the runtime bundle after package upgrade:

```bash
# Backup existing
mv "%USERPROFILE%\.ukbe-runner\workflows\default" "%USERPROFILE%\.ukbe-runner\workflows\default.backup"

# Reinitialize
ukbe-run-agent init

# Restore custom prompts if needed
```

## 4. Logs and Debugging

### 4.1 Log Locations

| Log | Path | Contents |
|-----|------|----------|
| Runner Log | `%USERPROFILE%\.ukbe-runner\logs\ukbe-runner-*.log` | General execution |
| Step Debug | `%USERPROFILE%\.ukbe-runner\jobs\...\<step>\debug\` | Step-specific debug |

### 4.2 Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed execution flow |
| INFO | Normal operations |
| WARNING | Recoverable issues |
| ERROR | Failures requiring attention |

### 4.3 Debug Commands

```bash
# Enable debug logging
$env:AGENT_RUNNER_LOG_LEVEL = "debug"

# View recent logs
Get-Content "$env:USERPROFILE\.ukbe-runner\logs\ukbe-runner-$(Get-Date -Format 'yyyyMMdd').log" -Tail 50

# Monitor logs in real-time
Get-Content "$env:USERPROFILE\.ukbe-runner\logs\ukbe-runner-$(Get-Date -Format 'yyyyMMdd').log" -Wait
```

## 5. Troubleshooting

### 5.1 Workflow Bundle Not Found

**Symptoms:**
```
Error: Workflow bundle not found: default
```

**Resolution:**
```bash
# Reinitialize runner
ukbe-run-agent init

# Verify paths
Test-Path "$env:USERPROFILE\.ukbe-runner\workflows\default\template_groups.py"
```

### 5.2 Meta.json Not Written

**Symptoms:**
Step fails with `MetaJsonMissingError`

**Resolution:**
1. Check coder timeout (default 600s)
2. Check step directory exists
3. Check disk space
4. Review coder logs in debug directory

### 5.3 Artifact Validation Failure

**Symptoms:**
```
Error: ArtifactMissingError: <path> not found
```

**Resolution:**
1. Check artifact path in `meta.json`
2. Verify path is relative to project root
3. Check file actually exists
4. Review coder output

### 5.4 Daemon Issues

**Symptoms:**
Daemon fails to start or crashes

**Resolution:**
```bash
# Check daemon status
ukbe-run-agent daemon --status

# Restart daemon
ukbe-run-agent daemon --stop
ukbe-run-agent daemon --start

# Check daemon logs
cat "%USERPROFILE%\.ukbe-runner\logs\daemon.log"
```

### 5.5 Backend Connection Issues

**Symptoms:**
Worker mode cannot connect to backend

**Resolution:**
1. Verify backend URL
2. Check network connectivity
3. Verify worker registration
4. Check backend health endpoint

## 6. Operational Procedures

### 6.1 Restart Failed Step

```bash
# Reset step and retry
ukbe-run-agent run --job-id <job-id> --retry
```

### 6.2 Approve Step

```bash
# Approve a waiting step
ukbe-run-agent approve <job-id> --step <step-name>

# Or use batch script
run-approve-step.bat <job-id> <step-name>
```

### 6.3 Cleanup Old Jobs

```bash
# List old jobs
Get-ChildItem "$env:USERPROFILE\.ukbe-runner\jobs\default\" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }

# Archive old jobs (manual)
Compress-Archive -Path "$env:USERPROFILE\.ukbe-runner\jobs\default\<job-id>" `
    -DestinationPath "D:\archives\<job-id>.zip"

# Remove old jobs (caution!)
Remove-Item -Recurse "$env:USERPROFILE\.ukbe-runner\jobs\default\<job-id>"
```

### 6.4 Backup Runner Home

```bash
# Backup entire runner home
Compress-Archive -Path "$env:USERPROFILE\.ukbe-runner\" `
    -DestinationPath "D:\backups\ukbe-runner-$(Get-Date -Format 'yyyyMMdd').zip"

# Backup just jobs
Compress-Archive -Path "$env:USERPROFILE\.ukbe-runner\jobs\" `
    -DestinationPath "D:\backups\jobs-$(Get-Date -Format 'yyyyMMdd').zip"
```

## 7. Performance Monitoring

### 7.1 Step Duration

Check step duration in `meta.json`:

```json
{
  "usage": {
    "duration_ms": 45000,
    "started_at": "2026-07-02T10:00:00",
    "finished_at": "2026-07-02T10:00:45"
  }
}
```

### 7.2 Usage Data

Aggregate usage from `job.json`:

```json
{
  "usage_summary": {
    "total_tokens": 15000,
    "total_cost": 0.45,
    "steps_completed": 5
  }
}
```

### 7.3 Disk Space

Monitor runner home size:

```bash
# Get runner home size
(Get-ChildItem "$env:USERPROFILE\.ukbe-runner\" -Recurse |
    Measure-Object -Property Length -Sum).Sum / 1MB

# Get jobs size
(Get-ChildItem "$env:USERPROFILE\.ukbe-runner\jobs\" -Recurse |
    Measure-Object -Property Length -Sum).Sum / 1MB
```

## 8. Emergency Procedures

### 8.1 Stop All Jobs

```bash
# Stop daemon
ukbe-run-agent daemon --stop

# Kill any lingering processes
Get-Process | Where-Object { $_.Name -like "*ukbe*" } | Stop-Process -Force
```

### 8.2 Recover Corrupted State

```bash
# If job.json is corrupted, check for backup
Test-Path "$env:USERPROFILE\.ukbe-runner\jobs\default\<job-id>\job.json.bak"

# Restore from backup
Copy-Item "$env:USERPROFILE\.ukbe-runner\jobs\default\<job-id>\job.json.bak" `
    "$env:USERPROFILE\.ukbe-runner\jobs\default\<job-id>\job.json"
```

### 8.3 Reset Runner Home

**Caution: Destroys all job state and workflows!**

```bash
# Backup first
Compress-Archive -Path "$env:USERPROFILE\.ukbe-runner\" `
    -DestinationPath "D:\backups\ukbe-runner-emergency-$(Get-Date -Format 'yyyyMMdd-HHmm').zip"

# Remove and reinitialize
Remove-Item -Recurse "$env:USERPROFILE\.ukbe-runner\"
ukbe-run-agent init
```

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs`*
