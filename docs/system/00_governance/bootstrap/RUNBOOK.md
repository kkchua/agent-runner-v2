---
template_id: "OPS-01-RB"
title: "Runbook"
status: "active"
generated: "2026-07-04T14:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook

## Operations Scope

This runbook covers operational procedures for the `agent-runner-v2` platform, including:

- Job state management
- Runtime bundle maintenance
- Log monitoring
- Failure handling
- Daemon supervision
- Backend connectivity

## Routine Procedures

### Procedure 1: Initialize Runner Home

**Purpose**: Set up global runner home for first-time use.

**Command**:
```bash
ukbe-run-agent init
```

**Creates**:
- `%USERPROFILE%\.ukbe-runner\config.json`
- `%USERPROFILE%\.ukbe-runner\jobs\`
- `%USERPROFILE%\.ukbe-runner\workflows\` (seeded from bootstrap)
- `%USERPROFILE%\.ukbe-runner\logs\`

**Verification**:
```bash
dir %USERPROFILE%\.ukbe-runner\
```

### Procedure 2: Start Daemon Mode

**Purpose**: Run workstation as supervised worker node.

**Command**:
```bash
ukbe-run-agent daemon
```

**Behavior**:
- Polls backend for available work
- Spawns child processes for step execution
- Emits periodic heartbeats
- Handles graceful shutdown on SIGTERM

**Verification**:
```bash
tasklist | findstr ukbe-run-agent
```

### Procedure 3: Inspect Job State

**Purpose**: View current job execution status.

**Command**:
```bash
ukbe-run-agent show-job <workflow> <job-id>
```

**Shows**:
- Current step
- Completed/failed steps
- Artifact paths
- Reject counts
- Loop context

### Procedure 4: Retry Failed Steps

**Purpose**: Retry steps after transient failures.

**Command**:
```bash
ukbe-run-agent retry <workflow> <job-id>
```

**Behavior**:
- Loads existing job state
- Retries failed steps up to configured max
- Updates job.json with new attempts

### Procedure 5: Sync Workflows

**Purpose**: Update runtime bundles with latest packaged versions.

**Command**:
```bash
sync-workflows-to-backend.bat
```

**Or manually**:
```bash
ukbe-run-agent init
```

### Procedure 6: Clean Generated Documentation

**Purpose**: Remove generated docs to force regeneration.

**Command**:
```bash
run-cleanup-generated-docs.bat
```

## Failure Handling

### Failure 1: Backend Connection Failure

**Symptoms**: Daemon cannot claim work, timeouts on poll.

**Classification**: `AUTO_RETRYABLE`

**Response**:
1. Check network connectivity
2. Verify backend URL in config
3. Check backend service status
4. Retry will happen automatically

**Escalation**: If retries exhausted, job enters `WAITING_FOR_HUMAN_APPROVAL`.

### Failure 2: Schema Validation Failure

**Symptoms**: Step fails with "Invalid meta.json schema".

**Classification**: `FATAL` (coder contract violation)

**Response**:
1. Inspect step output directory
2. Check meta.json format
3. Verify schema_version is "v2"
4. Check coder_result structure

**Recovery**: Fix underlying issue, retry step.

### Failure 3: Artifact Missing

**Symptoms**: "Artifact file not found" after step completion.

**Classification**: `FATAL` (contract violation)

**Response**:
1. Check step output directory
2. Verify file was created
3. Check path in meta.json matches actual file

**Recovery**: Fix step to produce declared artifact, retry.

### Failure 4: Bundle Version Mismatch

**Symptoms**: "Workflow not found" or step configuration mismatch.

**Classification**: `HUMAN_RETRY_REQUIRED`

**Response**:
1. Check if workflow exists in runtime bundle
2. Compare packaged vs runtime versions
3. Run `ukbe-run-agent init` to reseed
4. Or run `sync-workflows-to-backend.bat`

### Failure 5: Review Loop Exhaustion

**Symptoms**: Step rejected, max iterations reached.

**Classification**: Depends on `on_exhaust_replan` config.

**Response**:
1. Inspect review history
2. If configured, trigger replan
3. Otherwise, manual intervention required
4. Use `approve-step` to force advance if appropriate

## Operational Locations

### Job State Location

| Path | Purpose |
|------|---------|
| `%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job-id>\job.json` | Primary job state |
| `%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job-id>\<step>\` | Step output directories |
| `%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job-id>\<step>\meta.json` | Step result sidecar |

### Runtime Bundle Location

| Path | Purpose |
|------|---------|
| `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\template_groups.py` | Workflow definitions |
| `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\prompts\` | Prompt templates |
| `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\*.json` | Schema files |

### Log Location

| Path | Purpose |
|------|---------|
| `%USERPROFILE%\.ukbe-runner\logs\` | Runner-level logs |
| `%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job-id>\logs\` | Job-level logs |

### Sidecar Location

| Path | Purpose |
|------|---------|
| `<step-dir>\meta.json` | Step result (v2 schema) |

## Monitoring

### Daemon Health

Check daemon status:
```bash
tasklist | findstr ukbe-run-agent
```

View daemon logs:
```bash
type %USERPROFILE%\.ukbe-runner\logs\daemon.log
```

### Job Progress

List active jobs:
```bash
ukbe-run-agent list-jobs <workflow>
```

View job details:
```bash
ukbe-run-agent show-job <workflow> <job-id>
```

### Backend Connectivity

Test backend connection:
```bash
ukbe-run-agent poll
```

## Common Operational Tasks

| Task | Command |
|------|---------|
| Force approve step | `ukbe-run-agent approve-step <wf> <job> <step>` |
| Reset step | `ukbe-run-agent reset-step <wf> <job> <step>` |
| Clean old jobs | Manual deletion from jobs/ directory |
| Rotate logs | Delete old log files |
| Backup job state | Copy job.json to backup location |
| Migrate job state | `migrate_job_state()` in job_state.py |

---

*This runbook provides operational guidance for agent-runner-v2. See DEVELOPER_GUIDE.md for development workflows and EXISTING_REPO_WORKFLOW_SOP.md for workflow procedures.*
