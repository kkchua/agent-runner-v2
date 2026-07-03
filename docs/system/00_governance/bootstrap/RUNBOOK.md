---
template_id: "OPS-01-RB"
title: "Runbook - agent-runner-v2"
status: "active"
generated: "2026-07-04T10:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook: agent-runner-v2

## Operations Scope

This runbook covers operational procedures for the agent-runner-v2 workflow execution platform, including local execution, worker mode operation, and daemon supervision.

## Routine Procedures

### Daily Operations

#### Check Daemon Status

```bash
# View daemon logs
type "%USERPROFILE%\.ukbe-runner\logs\daemon-<worker-id>.log"

# Check for running daemon processes
tasklist | findstr python
```

#### Verify Worker Health

```bash
# Test worker connectivity
ukbe-run-agent worker --backend-url <url> --worker-id <id> --once
```

#### Monitor Job Queue

```bash
# Check job status
ukbe-run-agent run --template-group <group> --job-id <id> --check-job-status

# Show job details
ukbe-run-agent run --template-group <group> --job-id <id> --show-job
```

### Weekly Operations

#### Log Rotation

Daemon and job logs accumulate in `%USERPROFILE%\.ukbe-runner\logs\`:

```batch
REM Rotate logs (manual)
move "%USERPROFILE%\.ukbe-runner\logs\daemon-*.log" "\archive\logs\"
```

#### Workflow Bundle Verification

Ensure runtime bundles match expected state:

```python
# Check workflow bundle checksums
import hashlib
from pathlib import Path

workflow_root = Path.home() / ".ukbe-runner" / "workflows" / "default"
template_groups = workflow_root / "template_groups.py"
print(f"template_groups.py exists: {template_groups.exists()}")
```

### Monthly Operations

#### Cleanup Old Jobs

Job state persists indefinitely. Clean up completed jobs:

```batch
REM Remove old job directories (careful!)
REM Only remove jobs with terminal status (COMPLETED, FAILED, ABORTED)
```

#### Update Workflow Bundles

If bootstrap source has been updated:

```bash
# Re-seed workflow bundles
ukbe-run-agent init
```

## Failure Handling

### Job State Locations

| Location | Purpose |
|----------|---------|
| `%USERPROFILE%\.ukbe-runner\jobs\<group>\<job-id>\job.json` | Job state persistence |
| `%USERPROFILE%\.ukbe-runner\jobs\<group>\<job-id>\<step>\meta.json` | Step result sidecars |
| `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

### Common Failure Scenarios

#### Scenario 1: meta.json Missing

**Symptoms:**
- Error: `MetaJsonMissingError`
- Step shows as failed
- No artifacts produced

**Diagnosis:**
```bash
# Check if meta.json exists
if exist "%USERPROFILE%\.ukbe-runner\jobs\<group>\<job>\<step>\meta.json" (
    echo meta.json exists
) else (
    echo meta.json MISSING
)
```

**Recovery:**
1. Check coder logs for write errors
2. Verify disk space
3. Re-run step: `run-reset-step.bat` or `--step <step>` to retry

#### Scenario 2: Artifact Missing

**Symptoms:**
- Error: `ArtifactMissingError`
- meta.json exists but claims non-existent artifacts

**Diagnosis:**
```bash
# Check claimed artifact paths
# Read meta.json and verify each artifact exists
```

**Recovery:**
1. Verify artifact was created by coder
2. Check file permissions
3. Re-run step if needed

#### Scenario 3: Backend Connection Failure

**Symptoms:**
- Worker cannot claim work
- Daemon shows connection errors
- `BackendClient` timeout errors

**Diagnosis:**
```bash
# Test backend connectivity
curl <backend-url>/health
```

**Recovery:**
1. Verify backend URL
2. Check network connectivity
3. Restart worker: `ukbe-run-agent worker --backend-url <url> --worker-id <id>`

#### Scenario 4: Coder Timeout

**Symptoms:**
- Step hangs indefinitely
- `CoderInvocationError` with timeout message

**Diagnosis:**
Check `AGENT_RUNNER_CODER_TIMEOUT_SECONDS` environment variable (default: 600s)

**Recovery:**
1. Increase timeout: `set AGENT_RUNNER_CODER_TIMEOUT_SECONDS=900`
2. Check LLM provider status
3. Re-run step

#### Scenario 5: Daemon Child Process Failure

**Symptoms:**
- Daemon log shows child exit with error
- Step shows as failed but daemon continues

**Diagnosis:**
```batch
# Check daemon logs
type "%USERPROFILE%\.ukbe-runner\logs\daemon-<worker-id>.log"
```

**Recovery:**
1. Daemon automatically restarts polling
2. Check child process logs
3. Verify step configuration

### Failure Classification

| Class | Meaning | Auto-Recovery |
|-------|---------|---------------|
| `AUTO_RETRYABLE` | Transient failure (timeout, backend unavailable) | Yes, with backoff |
| `HUMAN_RETRY_REQUIRED` | Logic error, needs human review | No |
| `FATAL` | Unrecoverable error | No |

### Retry Limits

| Type | Default Limit | Configurable |
|------|---------------|--------------|
| Auto-retry | 3 | Per-step in template group |
| Human retry | Unlimited | Per-step in template group |

## Troubleshooting Commands

### Job State Inspection

```bash
# Show job state
ukbe-run-agent run --template-group <group> --job-id <id> --show-job

# Check job status
ukbe-run-agent run --template-group <group> --job-id <id> --check-job-status
```

### Log Inspection

```batch
REM View daemon logs
type "%USERPROFILE%\.ukbe-runner\logs\daemon-<worker-id>.log"

REM View job logs (in job directory)
type "%USERPROFILE%\.ukbe-runner\jobs\<group>\<job>\logs\*.log"
```

### Meta.json Inspection

```bash
# Read step result
type "%USERPROFILE%\.ukbe-runner\jobs\<group>\<job>\<step>\meta.json"
```

### Dry Run Testing

```bash
# Test prompt rendering without invoking coder
ukbe-run-agent run --template-group <group> --step <step> --dry-run
```

## Runtime Bundle Locations

### Global Runner Home

```
%USERPROFILE%\.ukbe-runner\
├───config.json              # User configuration
├───jobs\                    # Job state persistence
│   └───<template_group>\    # e.g., 00_master_docs_bootstrap_v1
│       └───<job_id>\        # e.g., 00DOC-GEN-20260703-007
│           ├───job.json     # Job state
│           └───<step_id>\   # Per-step directories
│               └───meta.json
├───workflows\               # Runtime workflow bundles
│   └───<workflow_name>\     # e.g., default
│       ├───template_groups.py
│       ├───*.json
│       └───prompts\         # Prompt templates
│           └───<workflow_family>\
│               └───*.txt
└───logs\                    # Execution logs
    ├───daemon-<worker-id>.log
    └───...
```

### Sidecar Locations

Step results are stored as `meta.json` sidecars:

```
%USERPROFILE%\.ukbe-runner\jobs\<group>\<job>\<step>\meta.json
```

**Sidecar Schema (v2):**
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "...",
    "artifacts": {...},
    "recorded_at": "..."
  }
}
```

## Emergency Procedures

### Daemon Won't Start

1. Check for existing daemon process
2. Kill if necessary: `taskkill /F /IM python.exe`
3. Clear daemon logs
4. Restart: `ukbe-run-agent daemon <worker-id>`

### Workflow Bundle Corruption

1. Backup custom workflows if needed
2. Remove corrupt bundle: `rmdir /S "%USERPROFILE%\.ukbe-runner\workflows\<name>"`
3. Re-seed: `ukbe-run-agent init`

### Job State Corruption

1. Identify corrupt job: `--show-job` shows invalid JSON
2. Archive if needed
3. Create new job: `--new-job` flag

---

*Generated: 2026-07-04T10:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 04_generate_architecture_docs*
*Change ID: 00DOC-GEN-20260704-001*
