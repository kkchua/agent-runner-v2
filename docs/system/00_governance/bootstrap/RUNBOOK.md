---
template_id: "OPS-01-RB"
title: "Runbook - agent-runner-v2"
status: "active"
generated: "2026-07-10T14:20:05+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook

## Operations Scope

This runbook covers operational procedures for the `agent-runner-v2` workflow orchestration engine, including:

- Job state management
- Runtime bundle locations
- Log access and interpretation
- Sidecar validation
- Failure handling and recovery
- Daemon supervision

## Routine Procedures

### Initialize Runner Home

```bash
ukbe-run-agent init
```

This seeds the global runner home at `%USERPROFILE%\.ukbe-runner\`:
- `config.json` — User configuration
- `jobs\` — Job state files
- `workflows\` — Runtime workflow bundles
- `logs\` — Execution logs

### Start Daemon Mode

```bash
ukbe-run-agent daemon
```

Or via batch file:
```batch
scripts\ukbe-daemon.bat
```

The daemon:
- Polls backend for available work
- Claims jobs for this workstation
- Spawns child processes for each step
- Does NOT need restart for code changes (spawns fresh subprocesses)

### Check Job Status

Jobs are stored in `%USERPROFILE%\.ukbe-runner\jobs\<job_id>\`:

| File | Purpose |
|------|---------|
| `job.json` | Job state, step history, artifacts |
| `00_*\meta.json` | Step result sidecars |
| `progress.jsonl` | Step progress tracking |

### Monitor Logs

| Log Location | Contents |
|--------------|----------|
| `%USERPROFILE%\.ukbe-runner\logs\` | Runner execution logs |
| Console output | Real-time step execution |
| `job.json` | Structured job state |

### Run Workflow Manually

```bash
ukbe-run-agent run <workflow_name> --initiative-id <id>
```

Examples:
```bash
ukbe-run-agent run 40_documentation_sync_v1 --initiative-id DOC-20260710-001
ukbe-run-agent run 31_task_execution_v1 --initiative-id TASK-20260710-001
```

## Runtime Locations

| Element | Path | Purpose |
|---------|------|---------|
| **Runner Home** | `%USERPROFILE%\.ukbe-runner\` | Global configuration root |
| **Config** | `%USERPROFILE%\.ukbe-runner\config.json` | User settings, backend URL |
| **Jobs** | `%USERPROFILE%\.ukbe-runner\jobs\<job_id>\` | Job state, sidecars |
| **Workflows** | `%USERPROFILE%\.ukbe-runner\workflows\<name>\` | Runtime workflow bundles |
| **Logs** | `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |
| **Step Outputs** | `jobs\<job_id>\<step_num>_\<step_name>\` | Step artifacts and meta.json |

### Sidecar Files

Each step produces a `meta.json` sidecar:

```
jobs\<job_id>\
├── 00_init\meta.json
├── 01_scan\meta.json
├── 02_generate\meta.json
└── ...
```

Sidecar structure:
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED|REJECTED",
    "remark": "Summary",
    "artifacts": {"KEY": "path/to/artifact.md"},
    "recorded_at": "2026-07-10T14:20:05+08:00"
  }
}
```

## Failure Handling

### Step Failure Types

| Failure | Cause | Resolution |
|---------|-------|------------|
| **MetaJsonMissingError** | Coder didn't write sidecar | Check coder output, retry step |
| **MetaJsonInvalidError** | Sidecar malformed | Check coder output, fix and retry |
| **ArtifactMissingError** | Declared artifact not found | Verify artifact paths, retry |
| **PreflightBlockedError** | Validation failed | Fix issues, retry from failed step |
| **CoderInvocationError** | LLM API failure | Check API keys, retry |

### Recovery Procedures

**Restart from failed step:**
```bash
ukbe-run-agent run <workflow> --resume --job-id <job_id>
```

**Retry with fresh job:**
```bash
ukbe-run-agent run <workflow> --initiative-id <id> --force-new
```

**Clear stuck daemon:**
```batch
taskkill /F /IM python.exe  # Terminate all Python processes
ukbe-run-agent daemon       # Restart daemon
```

### Notification Failures

If Pushover notifications fail:

1. Check `.env` for `PUSHOVER_APP_TOKEN` and `PUSHOVER_USER_KEY`
2. Verify network connectivity
3. Check `%USERPROFILE%\.ukbe-runner\logs\` for errors

### Backend Connectivity

If worker mode fails:

1. Check `config.json` for `backend.url`
2. Verify network connectivity
3. Check backend status
4. Switch to local mode: `ukbe-run-agent run <workflow>`

## Troubleshooting

### Workflow Not Found

```
Error: Workflow '<name>' not found
```

**Solution:**
```bash
ukbe-run-agent init  # Re-seed bootstrap workflows
```

### Step Hangs

**Symptoms:** Step appears stuck, no output

**Diagnosis:**
```batch
tasklist | findstr python
```

**Resolution:**
- Check for interactive prompts (should not happen in v2)
- Kill process and retry
- Check coder API status

### Bundle Drift

**Symptoms:** Runtime workflows differ from repo

**Solution:**
```bash
ukbe-run-agent init  # Sync bootstrap to runtime
```

Note: There is no automatic sync; manual `init` required.

### Windows Path Issues

**Symptoms:** Path resolution fails on Windows

**Check:**
- Paths use forward slashes in templates
- `PurePosixPath` for cross-platform compatibility
- No drive-relative paths in config

### Test Failures

```bash
# Run unit tests only
pytest tests/unit/ -v

# Run specific test
pytest tests/unit/test_constants.py -v
```

## Related Documents

| Document | Purpose |
|----------|---------|
| [SYSTEM_CONTEXT.md](SYSTEM_CONTEXT.md) | External systems |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Development procedures |
| [EXISTING_REPO_WORKFLOW_SOP.md](EXISTING_REPO_WORKFLOW_SOP.md) | Workflow sequences |
