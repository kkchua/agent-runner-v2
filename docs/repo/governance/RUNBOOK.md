---
template_id: "OPS-01-RB"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:22:07+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Runbook: agent-runner-v2

## Operations Scope

This runbook covers operational procedures for the `agent-runner-v2` workflow runner. It is intended for operators managing workflow execution, job state, and runtime health.

### Scope Inclusions

- Daemon operation and monitoring
- Job state management and recovery
- Workflow execution troubleshooting
- Log and artifact management
- Notification configuration

### Scope Exclusions

- Development procedures (see `DEVELOPER_GUIDE.md`)
- Architecture decisions (see `DECISION_LOG.md`)
- Workflow implementation (see workflow-specific documentation)

## Routine Procedures

### Starting the Daemon

1. **Prerequisites**:
   - Virtual environment activated (`.venv\Scripts\activate`)
   - Backend server running and accessible
   - Pushover credentials configured in `.env` (optional)

2. **Start command**:
   ```bash
   run-daemon.bat
   ```

3. **Verify startup**:
   - Check console output for "Daemon started" message
   - Verify daemon is polling backend API
   - Monitor for job assignments

### Checking Job State

Job state is persisted in `.ukbe-runner/jobs/<job_id>/`:

| File | Purpose |
|------|---------|
| `job.json` | Job metadata (workflow, mode, current step) |
| `<step_id>/` | Step working directory |
| `<step_id>/meta.json` | Step result sidecar |
| `<step_id>/<artifact>` | Generated artifacts |

To inspect job state:
```bash
type .ukbe-runner\jobs\<job_id>\job.json
```

### Approving Steps (Manual Mode)

When a workflow step requires manual approval:

1. Review the step output in `.ukbe-runner/jobs/<job_id>/<step_id>/`
2. Verify artifacts exist and are correct
3. Run approval command:
   ```bash
   run-approve-step.bat
   ```

### Resetting Failed Steps

If a step fails and needs retry:

1. Identify the failed step in job state
2. Review error in `meta.json` sidecar
3. Run reset command:
   ```bash
   run-reset-step.bat
   ```

### Cleaning Up Jobs

To clean up completed or abandoned jobs:

```bash
run-cleanup-workflow.bat
```

This removes:
- Job state directories under `.ukbe-runner/jobs/`
- Generated artifacts in step directories
- Sidecar files

## Runtime State Locations

### Job Directories

| Location | Purpose | Retention |
|----------|---------|-----------|
| `.ukbe-runner/jobs/<job_id>/` | Job root directory | Until cleanup |
| `.ukbe-runner/jobs/<job_id>/job.json` | Job metadata | Until cleanup |
| `.ukbe-runner/jobs/<job_id>/<step_id>/` | Step working directory | Until cleanup |
| `.ukbe-runner/jobs/<job_id>/<step_id>/meta.json` | Step result sidecar | Until cleanup |

### Runtime Bundles

| Location | Purpose |
|----------|---------|
| `workflows/<workflow_name>/` | Deployed workflow packages |
| `%USERPROFILE%\.ukbe-runner\workflows\` | Global workflow packages |
| `agent_runner_v2/bootstrap/workflows/default/` | Local workflow packages |

### Logs

| Location | Purpose |
|----------|---------|
| Console output | Daemon/worker logs |
| `runner_logger.py` output | Structured JSON logs (when enabled) |

### Sidecars

Sidecar files are JSON metadata files accompanying generated artifacts:

| Pattern | Purpose |
|---------|---------|
| `*.meta.json` | Artifact metadata (timestamps, checksums) |
| `meta.json` | Step result (status, artifacts, usage) |

## Failure Handling

### Coder Invocation Failure

**Symptoms**:
- Step stuck in "processing" state
- No `meta.json` sidecar created
- Coder process timeout

**Diagnosis**:
1. Check step directory for prompt file
2. Verify coder process configuration in `coder_connections.json`
3. Check for stuck subprocesses

**Resolution**:
1. Reset the step: `run-reset-step.bat`
2. Verify coder process can be invoked manually
3. Check timeout settings in `coder_adapters.py`

### Artifact Validation Failure

**Symptoms**:
- `meta.json` shows `status: "REJECTED"`
- Error: "Artifact path does not exist"

**Diagnosis**:
1. Check `meta.json` for artifact paths
2. Verify paths exist on disk
3. Check for path escaping issues

**Resolution**:
1. Verify artifact key normalization in `step_runner.py`
2. Check absolute vs relative path handling
3. Re-run step with corrected artifact paths

### Backend Connection Failure

**Symptoms**:
- Daemon cannot poll backend API
- HTTP errors in console output
- Job queue not updating

**Diagnosis**:
1. Check backend server health
2. Verify network connectivity
3. Check API credentials in `.env`

**Resolution**:
1. Restart backend server
2. Verify backend URL in `config.json`
3. Check firewall rules

### Notification Failure

**Symptoms**:
- No Pushover notifications received
- Silent failures on step completion

**Diagnosis**:
1. Check `.env` for Pushover credentials
2. Verify Pushover API is reachable
3. Check notification logs in `notification_manager.py`

**Resolution**:
1. Add Pushover credentials to `.env`:
   ```
   PUSHOVER_TOKEN=your_token
   PUSHOVER_USER=your_user_key
   ```
2. Test notification: `python -m agent_runner_v2.notifications --test`

### Windows Path Issues

**Symptoms**:
- `Path.relative_to()` errors
- Path not found errors
- Backslash handling issues

**Diagnosis**:
1. Check path construction in `constants.py`
2. Verify absolute paths are used for placeholders
3. Check for mixed path separators

**Resolution**:
1. Use forward slashes in configuration
2. Ensure paths are absolute before placeholder injection
3. Check Windows-specific path handling in `run_agent.py`

## Monitoring

### Health Checks

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Daemon running | Check console output | "Daemon started" message |
| Backend reachable | `curl <backend_url>/health` | HTTP 200 |
| Pushover configured | Check `.env` | Credentials present |
| Workflows synced | Check `workflows/` directory | Workflow packages present |

### Log Analysis

Daemon logs include:
- Job assignment events
- Step execution start/complete
- Notification delivery status
- Error stack traces

Search for errors:
```bash
findstr /i "error" daemon.log
```

### Performance Indicators

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Step execution time | <5 min | >15 min |
| Job queue depth | <10 | >50 |
| Notification latency | <1 sec | >30 sec |
| Coder timeout rate | <5% | >20% |

## Maintenance Windows

### Routine Maintenance

- **Daily**: Check daemon health, review failed jobs
- **Weekly**: Clean up completed jobs, review logs
- **Monthly**: Update dependencies, review workflow registry

### Upgrade Procedure

1. **Stop daemon**: Close daemon console window
2. **Backup state**: Copy `.ukbe-runner/jobs/` to backup location
3. **Pull changes**: `git pull origin feat/plugin-workflow-system`
4. **Update dependencies**: `pip install -e .`
5. **Run bootstrap**: `run-00_layer1_governance_bootstrap_v1.bat`
6. **Start daemon**: `run-daemon.bat`

## Escalation

### Contact Points

| Issue Type | Contact |
|------------|---------|
| Daemon failures | Check `daemon.py` documentation |
| Backend issues | Backend team (external) |
| Workflow errors | Check workflow-specific documentation |
| Notification failures | Check Pushover service status |

### Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| Windows path edge cases | Fixed in v0.3.0 | Use absolute paths |
| Daemon subprocess CWD | Fixed in v0.3.0 | Set CWD correctly |
| pytest tmp_path permission | Workaround in tests | Use `tests/integration/` |
