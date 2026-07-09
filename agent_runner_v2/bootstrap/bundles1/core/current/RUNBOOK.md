---
template_id: "OPS-01-RB"
title: "Runbook - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:26:47+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook: agent-runner-v2

## Operations Scope

This runbook covers operational procedures for running and troubleshooting the agent-runner-v2 workflow orchestration engine.

### Runtime Locations

| Resource | Location | Purpose |
|----------|----------|---------|
| **Runner Home** | `%USERPROFILE%\.ukbe-runner\` | Global state and configuration |
| **Config** | `%USERPROFILE%\.ukbe-runner\config.json` | User settings, credentials |
| **Workflows** | `%USERPROFILE%\.ukbe-runner\workflows\<name>\` | Runtime workflow bundles |
| **Jobs** | `%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\` | Job state, sidecars, artifacts |
| **Logs** | `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

### Job State Structure

```
%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\
├── job.json              # Job state (schema v6)
├── meta.json             # Current step sidecar
├── context.json            # Step context
├── progress.jsonl        # Progress tracking
├── step-01/              # Step 1 artifacts
│   ├── meta.json
│   └── ...
├── step-02/              # Step 2 artifacts
│   └── ...
└── ...
```

## Routine Procedures

### Initial Setup

```bash
# 1. Install package
pip install -e ".[dev]"

# 2. Initialize runner home
ukbe-run-agent init

# 3. Configure credentials (copy and edit .env)
copy .env.example .env
# Edit .env with your credentials
```

### Running a Workflow

```bash
# Option 1: Use batch launcher
double-click run-00_master_docs_bootstrap_v1.bat

# Option 2: Direct CLI
ukbe-run-agent run 00_master_docs_bootstrap_v1 --target-project-root <path>
```

### Checking Job Status

```bash
# List jobs for workflow
ukbe-run-agent status <workflow>

# View specific job
cat %USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\job.json
```

### Resuming a Job

```bash
# Resume from last completed step
ukbe-run-agent run <workflow> --job-id <job_id>

# Or edit batch file and set JOB_ID=...
```

### Daemon Mode Operations

```bash
# Start daemon
ukbe-run-agent daemon

# Check daemon status
ukbe-run-agent daemon --status

# Stop daemon
ukbe-run-agent daemon --stop
```

### Workflow Bundle Management

```bash
# Re-seed workflow bundles (after package update)
ukbe-run-agent init

# Sync workflows to runtime
ukbe-run-agent sync-workflows
```

## Failure Handling

### Sidecar Missing (MetaJsonMissingError)

**Symptoms**: Workflow stalls; step never completes

**Diagnosis**:
```bash
# Check if meta.json exists
dir %USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\step-XX\meta.json

# Check step output for errors
```

**Resolution**:
1. Check coder process is running
2. Verify coder wrote meta.json correctly
3. Retry step: `ukbe-run-agent run <workflow> --job-id <job_id> --step <step>`
4. Or use `run-reset-step.bat` to reset and retry

### Job State Corruption

**Symptoms**: Job fails to load; schema errors

**Diagnosis**:
```bash
# Check schema version in job.json
cat %USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\job.json | findstr schema_version
```

**Resolution**:
1. Automatic migration attempted on load
2. If migration fails: Create new job with `--new-job`
3. For severe corruption: Delete job directory and restart

### LLM Provider Failures

**Symptoms**: Coder invocation fails; timeouts

**Diagnosis**:
```bash
# Check model configuration
cat %USERPROFILE%\.ukbe-runner\config.json | findstr default_model

# Check .env credentials
cat .env | findstr ANTHROPIC_API_KEY
```

**Resolution**:
1. Verify API credentials in `.env`
2. Check network connectivity
3. Try alternative model: `--model qwen`
4. Check rate limits with provider

### Backend Disconnection (Daemon Mode)

**Symptoms**: Daemon falls back to local mode

**Resolution**:
1. Check backend URL in config
2. Verify network connectivity
3. Check authentication token
4. Daemon continues in local mode; reconnects automatically

### Notification Failures

**Symptoms**: Push notifications not received

**Diagnosis**:
```bash
# Check Pushover config
cat %USERPROFILE%\.ukbe-runner\config.json | findstr pushover
```

**Resolution**:
1. Verify PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY in `.env`
2. Check Pushover service status
3. Notifications are optional; workflow continues without them

### Windows Path Issues

**Symptoms**: Path.relative_to() failures; permission errors

**Resolution**:
1. Fixed in current codebase
2. Use centralized constants.py for all paths
3. Avoid manual path construction

### Test Failures

**Symptoms**: pytest failures; tmp_path issues

**Resolution**:
1. Use `tests/unit/` for pure logic tests
2. Use `tests/integration/` for filesystem tests
3. On Windows: Use `--basetemp` for pytest temp directories

## Troubleshooting Commands

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent --version` | Check version |
| `ukbe-run-agent init --dry-run` | Preview init changes |
| `ukbe-run-agent run <wf> --dry-run` | Preview step execution |
| `cat job.json | python -m json.tool` | Pretty-print job state |
| `findstr "status" job.json` | Find status field |

## Log Locations

| Log Type | Location |
|----------|----------|
| **Runner logs** | `%USERPROFILE%\.ukbe-runner\logs\` |
| **Step output** | `jobs/<workflow>/<job_id>/step-XX/output.log` |
| **Error logs** | `jobs/<workflow>/<job_id>/step-XX/error.log` |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 04_generate_architecture_docs | Change: 00DOC-20260708-78fb419e*
