---
template_id: "OPS-01-RB"
title: "Runbook - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:52:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Runbook: agent-runner-v2

## Operations Scope

This runbook covers operational procedures for the agent-runner-v2 workflow orchestration engine. It addresses routine operations, failure scenarios, and recovery procedures for operators.

## Where Things Live

### Job State Location

```
%USERPROFILE%\.ukbe-runner\jobs\{workflow}\{job_id}\job.json
```

**Contents**:
- Current step
- Status (IN_PROGRESS, WAITING_FOR_HUMAN_APPROVAL, COMPLETED, FAILED)
- Artifacts produced
- Retry counts
- Failure history
- Model usage data

### Runtime Bundles Location

```
%USERPROFILE%\.ukbe-runner\workflows\default\
├── template_groups.py      # Workflow definitions
├── constants.py            # Path constants
├── prompts/                # 290+ prompt templates
├── job_schema.json         # Job JSON schema
├── llm_response_schema.json # LLM response schema
└── model_mapping.json      # Model aliases
```

**Important**: Bootstrap files in the repo only seed runtime. Active changes require explicit sync.

### Logs Location

```
%USERPROFILE%\.ukbe-runner\logs\ukbe-runner.log
```

**Log rotation**: Automatic, based on size and date.

### Sidecar Files Location

```
%USERPROFILE%\.ukbe-runner\jobs\{workflow}\{step}\meta.json
```

**Naming**: `{step_id}.meta.json` or `{step_id}\meta.json` depending on step type.

### Configuration Location

```
%USERPROFILE%\.ukbe-runner\config.json
```

**Contains**:
- Backend URL
- API keys (encrypted)
- Notification settings
- Workflow overrides

## Routine Procedures

### Starting the Daemon

**Command**:
```bash
ukbe-run-agent daemon
```

**Or**:
```batch
run-daemon.bat
```

**What it does**:
- Polls backend for pending jobs
- Spawns subprocess for each step
- Streams events to backend
- Sends notifications on completion

**Monitoring**:
- Check logs: `%USERPROFILE%\.ukbe-runner\logs\ukbe-runner.log`
- Check backend: WebSocket events
- Check notifications: Pushover delivery

### Checking Job Status

**View job file**:
```bash
cat %USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\job.json
```

**Key fields**:
- `job_status`: Current state
- `current_step`: Where execution is
- `completed_steps`: What's done
- `failed_steps`: What failed
- `artifacts`: Produced files

### Approving a Step

**Command**:
```bash
ukbe-run-agent approve-step <job_id> <step_id>
```

**Or**:
```batch
run-approve-step.bat <job_id> <step_id>
```

**Required when**:
- Step status is `WAITING_FOR_HUMAN_APPROVAL`
- Review decision is `PENDING`

### Resetting a Step

**Command**:
```bash
ukbe-run-agent run <workflow> --job-id <id> --step <step> --reset
```

**Or**:
```batch
run-reset-step.bat <workflow> <step> <job_id>
```

**Use when**:
- Need to re-run a step
- Step failed and requires intervention
- Testing changes

### Syncing Bootstrap to Runtime

**Manual sync**:
```bash
copy agent_runner_v2\bootstrap\workflows\default\* %USERPROFILE%\.ukbe-runner\workflows\default\
```

**Or via workflow**:
```batch
run-bootstrap-publish.bat
```

**Required after**:
- Changing `template_groups.py`
- Changing `constants.py`
- Adding new prompt templates

### Cleaning Generated Docs

**Command**:
```batch
run-cleanup-generated-docs.bat
```

**Use when**:
- Disk space low
- Starting fresh documentation
- Troubleshooting doc issues

## Failure Handling

### Common Failures

#### MetaJsonMissingError

**Symptom**: Step fails with "MetaJsonMissingError"

**Cause**: LLM didn't write meta.json sidecar

**Recovery**:
1. Check prompt sidecar injection is enabled
2. Verify artifact paths are correct
3. Reset step and retry
4. Check LLM response in logs

**Prevention**:
- Ensure prompt templates include sidecar instructions
- Verify `SIDECAR_INSTRUCTION_TEMPLATE` in constants.py

#### ArtifactMissingError

**Symptom**: Step fails with "ArtifactMissingError"

**Cause**: Expected artifact file not found

**Recovery**:
1. Check `produces` list in step config
2. Verify LLM actually wrote the file
3. Check file path in meta.json
4. Reset step and retry

#### PreflightBlockedError

**Symptom**: Step blocked at preflight

**Cause**: Missing required artifacts from previous steps

**Recovery**:
1. Check artifact dependencies
2. Verify upstream steps completed
3. Re-run missing upstream steps
4. Retry current step

#### BackendConnectionError

**Symptom**: Cannot connect to backend

**Cause**: Network issue, backend down, wrong URL

**Recovery**:
1. Check `config.json` for correct backend URL
2. Verify network connectivity
3. Check backend service status
4. Retry with exponential backoff

#### Windows Pathlib Bug

**Symptom**: Path.relative_to() fails on valid subpaths

**Cause**: Windows pathlib edge case

**Recovery**: Already fixed via `_safe_relative_to()` helper

**If encountered**:
1. Update to latest code
2. Ensure `_safe_relative_to()` is used

### Retry Procedures

#### Auto-Retry

**Trigger**: `CONTROL_CLASSES: AUTO_RETRYABLE`

**Behavior**:
- Increments `auto_retry_count_by_step`
- Waits with exponential backoff
- Retries up to max limit

**Monitor**: Check `retry_history` in job.json

#### Human Retry

**Trigger**: `CONTROL_CLASSES: HUMAN_RETRY_REQUIRED`

**Behavior**:
- Sets status to `WAITING_FOR_HUMAN_INTERVENTION`
- Sends notification
- Waits for manual retry

**Action required**:
1. Review failure reason
2. Fix underlying issue
3. Run: `ukbe-run-agent approve-step <job> <step>` or reset

#### Fatal Failures

**Trigger**: `CONTROL_CLASSES: FATAL`

**Behavior**:
- Job status set to `FAILED`
- No automatic retry
- Requires manual investigation

**Action required**:
1. Check logs for stack trace
2. Review `last_failure` in job.json
3. Fix code/config issue
4. Create new job

### Notification Issues

#### Pushover Not Receiving

**Check**:
1. `PUSHOVER_TOKEN` and `PUSHOVER_USER` in `.env`
2. Pushover service status
3. Network connectivity
4. Rate limits

#### Missing Notifications

**Check**:
1. Step config has `enable_notifications: true`
2. `notification_manager.py` is functioning
3. No errors in notification delivery

### Daemon Issues

#### Daemon Not Starting

**Check**:
1. Port conflicts
2. Configuration errors
3. Missing dependencies
4. Permissions

#### Steps Not Executing

**Check**:
1. Backend connectivity
2. Job queue has pending jobs
3. Worker slots available
4. Daemon process running

#### High Memory Usage

**Note**: Daemon spawns fresh subprocess for each step. Memory leaks in steps don't affect daemon.

**If daemon itself has issues**:
1. Check for memory leaks in daemon.py
2. Review long-running operations
3. Consider restart

### Workflow Issues

#### Workflow Not Found

**Cause**: Runtime bundle missing or outdated

**Fix**:
```bash
ukbe-run-agent init --force
# Or manually sync bootstrap
```

#### Placeholder Substitution Failures

**Symptom**: Prompts contain `{PLACEHOLDER}` instead of values

**Cause**: `REFERENCE_FILES` mismatch or missing key

**Fix**:
1. Check `REFERENCE_FILES` in `constants.py`
2. Verify template uses correct placeholder
3. Sync bootstrap to runtime

### Environment Issues

#### Python Version Mismatch

**Recommended**: Python 3.12

**If using Python 3.14**:
- May have compatibility issues
- Some dependencies may not support

#### Virtual Environment Issues

**Symptom**: Import errors, missing modules

**Fix**:
```bash
# Recreate venv
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Recovery Procedures

### Job Recovery

**From WAITING_FOR_HUMAN_APPROVAL**:
```bash
ukbe-run-agent approve-step <job_id> <step_id>
```

**From FAILED**:
1. Analyze failure in `last_failure`
2. Fix root cause
3. Create new job with same parameters
4. Or use `recover_exhausted_planning_job()` if applicable

**From IN_PROGRESS (hung)**:
1. Check if process is running
2. Kill if necessary: `taskkill /F /IM python.exe`
3. Reset step
4. Retry

### State Recovery

**Corrupted job.json**:
1. Check backup files (if any)
2. Recreate from scratch
3. Report issue

**Missing workflow module**:
1. Re-initialize: `ukbe-run-agent init`
2. Or manually copy from bootstrap

### Log Recovery

**Logs rotated away**:
- Check backup logs if configured
- Review Windows Event Log if daemon crashed

## Monitoring

### Key Metrics

| Metric | How to Check | Alert Threshold |
|--------|--------------|-----------------|
| Failed jobs | Count in logs | > 5% failure rate |
| Retry rate | `retry_history` length | > 3 retries/step |
| Step duration | `updated_at` - `created_at` | > 30 min |
| Backend latency | Log timestamps | > 5 seconds |

### Health Checks

**Daemon health**:
```bash
ukbe-run-agent status
```

**Backend connectivity**:
```bash
curl <backend_url>/health
```

**Disk space**:
```bash
dir %USERPROFILE%\.ukbe-runner
```

## Escalation

### When to Escalate

- Fatal failures affecting multiple jobs
- Data corruption in job state
- Security incidents
- Performance degradation

### Escalation Path

1. Check logs for root cause
2. Document failure pattern
3. Check existing issues
4. Create detailed bug report
5. Notify development team

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs` on 2026-07-10T09:52:38+08:00*
