---
template_id: "CB-04-FM"
version: "1.0.0"
doc_type: "codebase"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:39:14+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04c_generate_failure_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Failure Modes Catalog: agent-runner-v2

## 1. Overview

This document catalogs all error conditions, exception handling patterns, and recovery procedures in the agent-runner-v2 codebase. The runner uses a structured failure classification system to route errors appropriately based on their recoverability and source.

## 2. Failure Classification System

### 2.1 Failure Classes

The runner classifies failures into three categories:

| Class | Code | Description | Handling |
|-------|------|-------------|----------|
| `AUTO_RETRYABLE` | Automatic retry without human intervention | Transient errors that may resolve on retry | System automatically retries up to `max_rejects` |
| `HUMAN_RETRY_REQUIRED` | Human intervention needed | Configuration or input issues requiring correction | Job pauses with `WAITING_FOR_HUMAN_INTERVENTION` |
| `FATAL` | Unrecoverable failure | Critical errors that cannot be retried | Job terminates with `FAILED` status |

### 2.2 Failure Sources

Failures are attributed to one of four sources:

| Source | Description | Examples |
|--------|-------------|----------|
| `runner` | Internal runner logic errors | Invalid configuration, unexpected state |
| `adapter` | Coder invocation failures | Process crash, timeout, API error |
| `model` | LLM-generated rejection responses | Content policy violation, scope error |
| `validator` | Post-invocation validation failures | Missing sidecar, invalid schema, missing artifacts |

### 2.3 Control Classes

The `CONTROL_CLASSES` set defines failure classes that control workflow routing:

```python
CONTROL_CLASSES = {"AUTO_RETRYABLE", "HUMAN_RETRY_REQUIRED", "FATAL"}
```

## 3. Exception Catalog

### 3.1 Core Exceptions

| Exception | Module | When Raised | Handling | Recovery |
|-----------|--------|-------------|----------|----------|
| `PreflightBlockedError` | `exceptions.py` | Preflight check blocks step execution (e.g., artifact status not approved) | Route to `WAITING_FOR_HUMAN_INTERVENTION` | Resolve blocking condition, retry |
| `MetaJsonMissingError` | `exceptions.py` | Coder did not write expected `meta.json` sidecar after invocation | `HUMAN_RETRY_REQUIRED` classification | Re-run step with corrected coder configuration |
| `MetaJsonInvalidError` | `exceptions.py` | `meta.json` exists but fails schema validation | `HUMAN_RETRY_REQUIRED` classification | Fix coder output format, re-run step |
| `ArtifactMissingError` | `exceptions.py` | `coder_result.artifacts` references paths that don't exist on disk | `HUMAN_RETRY_REQUIRED` classification | Ensure artifacts are created, re-run step |
| `CoderInvocationError` | `coder_adapters.py` | Coder process failed (non-zero exit, timeout, crash) | Classified based on error content | See invocation error handling |

### 3.2 Exception Details

#### PreflightBlockedError

**Location**: `agent_runner_v2/exceptions.py`

**Raised By**: Step execution preflight checks in `step_runner.py`

**Conditions**:
- Required input artifact not approved
- Required input artifact missing from disk
- Step prerequisites not satisfied

**Handling**: 
- Classified as `HUMAN_RETRY_REQUIRED`
- Job status set to `WAITING_FOR_HUMAN_INTERVENTION`
- `pending_intervention_for` set to current step

**Recovery**:
1. Review the blocking condition in job logs
2. Resolve the blocking artifact (approve missing artifact, fix path)
3. Use `run-approve-step.bat` or backend approval endpoint
4. Re-run the step

#### MetaJsonMissingError

**Location**: `agent_runner_v2/exceptions.py`

**Raised By**: `_read_and_validate_meta_json()` in `step_runner.py`

**Conditions**:
- Coder process completed but did not write `meta.json`
- Sidecar path resolution failed
- `result_meta_key` and `result_meta_key_from_context` both missing from step config

**Handling**:
- Classified as `HUMAN_RETRY_REQUIRED` with code `META_JSON_MISSING`
- Source: `validator`
- Step does not progress

**Recovery**:
1. Check coder process logs in step directory (`raw_output.txt`, `stderr.txt`)
2. Verify coder configuration in `coder_connections.json`
3. Ensure step config has valid `result_meta_key` or `result_meta_key_from_context`
4. Re-run step with corrected configuration

#### MetaJsonInvalidError

**Location**: `agent_runner_v2/exceptions.py`

**Raised By**: `_read_and_validate_meta_json()` in `step_runner.py`

**Conditions**:
- `meta.json` is not valid JSON
- Missing required fields: `schema_version`, `coder_result`, `status`, `artifacts`, `recorded_at`
- Invalid `schema_version` (not `v2` or `artifact_meta_v1`)
- `coder_result.status` not `APPROVED` or `REJECTED`
- `coder_result.artifacts` not a dictionary

**Handling**:
- Classified as `HUMAN_RETRY_REQUIRED` with code `META_JSON_INVALID`
- Source: `validator`
- Error message includes specific validation failure

**Recovery**:
1. Review `meta.json` content in step directory
2. Compare against expected schema (`llm_response_schema.json`)
3. Fix coder prompt or output handling
4. Re-run step

#### ArtifactMissingError

**Location**: `agent_runner_v2/exceptions.py`

**Raised By**: `_validate_artifact_files_exist()` in `step_runner.py`

**Conditions**:
- Artifact paths in `meta.json` don't exist on disk
- Declared produced artifacts not created
- Path resolution failures

**Handling**:
- Classified as `HUMAN_RETRY_REQUIRED` with code `ARTIFACT_FILES_MISSING` or `STEP_CONTRACT_MISMATCH`
- Source: `validator`
- Missing paths included in exception message

**Recovery**:
1. Review missing artifact paths in error message
2. Check if coder created files in unexpected locations
3. Verify path placeholders in workflow context
4. Re-run step with corrected paths

#### CoderInvocationError

**Location**: `agent_runner_v2/coder_adapters.py`

**Raised By**: `invoke_coder()`, `_run_with_sidecar_poll()`

**Conditions**:
- Coder process returned non-zero exit code
- Coder process timed out
- Coder process crashed or was killed
- Transient API errors (rate limits, connection failures)

**Handling**: Classified based on error message content:

| Condition | Classification | Code |
|-----------|----------------|------|
| Transient error (timeout, rate limit, connection) | `AUTO_RETRYABLE` | `TRANSIENT_API_ERROR` |
| Permanent failure | `HUMAN_RETRY_REQUIRED` | `ADAPTER_INVOCATION_FAILED` |

**Recovery**:
1. **Transient errors**: System automatically retries; no action needed
2. **Permanent failures**:
   - Check `raw_output.txt` and `stderr.txt` in step directory
   - Verify coder configuration (model, connection, credentials)
   - Check API quotas and rate limits
   - Re-run step manually

## 4. Failure Handling by Step Type

### 4.1 Coder Steps

Coder steps invoke external LLM processes. Failure handling:

1. **Invocation Phase** (`coder_adapters.py`):
   - `CoderInvocationError` raised on process failure
   - Timeout handling with graceful termination
   - Sidecar polling for early completion detection

2. **Validation Phase** (`step_runner.py`):
   - `MetaJsonMissingError` if sidecar not written
   - `MetaJsonInvalidError` if sidecar schema invalid
   - `ArtifactMissingError` if artifact paths missing

3. **Routing Phase** (`workflow_router.py`):
   - `route_after_failure()` classifies exception
   - Updates failure history and retry counts
   - Sets job status based on classification

### 4.2 Action Steps

Action steps execute deterministic Python functions. Failure handling:

1. **Execution Phase** (`step_runner.py:run_action()`):
   - Action function raises exception
   - Exception propagated to caller
   - Action may write `meta.json` with `REJECTED` status

2. **Routing Phase** (`workflow_router.py`):
   - Generic exception handling
   - Classified as `FATAL` if unknown exception type
   - Known exceptions classified per their type

### 4.3 Review Steps

Review steps validate generated artifacts. Failure handling:

1. **Validation Phase**:
   - Reviewer returns `APPROVED` or `REJECTED`
   - `REJECTED` may trigger refine loop or replan

2. **Loop/Replan Phase** (`workflow_router.py`):
   - `on_reject_refine` config activates refinement loop
   - `on_exhaust_replan` config triggers replan
   - Budget tracking via `planning_attempt_count`

## 5. Retry and Recovery Mechanics

### 5.1 Automatic Retry

**Trigger**: `AUTO_RETRYABLE` failure class

**Mechanics**:
- `auto_retry_count_by_step` incremented
- Job status set to `WAITING_FOR_AUTO_RETRY`
- No human intervention required
- Backend daemon automatically re-claims step

**Conditions for Auto-Retry**:
- Transient API errors (rate limits, timeouts)
- Connection failures
- Temporary network issues

**Configuration**:
```toml
[workflow]
max_rejects = 3  # Maximum rejects before FATAL
```

### 5.2 Human Retry Required

**Trigger**: `HUMAN_RETRY_REQUIRED` failure class

**Mechanics**:
- `human_retry_count_by_step` incremented
- Job status set to `WAITING_FOR_HUMAN_INTERVENTION`
- `pending_intervention_for` set to current step
- Notification sent (if configured)

**Conditions for Human Intervention**:
- Configuration errors
- Missing or invalid artifacts
- Schema validation failures
- Coder process failures (non-transient)

**Recovery Procedure**:
1. Review failure details in `job.json`:
   - `last_failure_class`
   - `last_failure_code`
   - `last_failure_reason`
   - `last_failure_source`
2. Review step directory for logs:
   - `raw_output.txt` - coder stdout
   - `stderr.txt` - coder stderr
   - `usage.json` - token usage
   - `step_manifest.json` - invocation details
3. Resolve the blocking condition
4. Use approval command or backend API to retry

### 5.3 Fatal Failures

**Trigger**: `FATAL` failure class or `max_rejects` exceeded

**Mechanics**:
- Job status set to `FAILED`
- Step added to `failed_steps` list
- Workflow terminates

**Conditions for Fatal**:
- Content policy violations
- Scope errors (out-of-bounds requests)
- Maximum retries exceeded
- Unknown exception types

**Recovery Procedure**:
1. Review failure history in `job.json`
2. Determine if failure is recoverable
3. If recoverable, reset job state and retry
4. If not recoverable, create new job with corrected inputs

### 5.4 Refine Loop Recovery

**Trigger**: Step has `on_reject_refine` configuration

**Mechanics**:
- `loop_context` activated with:
  - `loop_step`: Original step
  - `refine_step`: Refinement step
  - `target_artifact`: Artifact to refine
  - `iteration`: Current iteration count
- Loop history tracked in `loop_history`
- Maximum iterations configurable via `max_iterations`

**Exhaustion Handling**:
- When `iteration > max_iterations`:
  - Attempt replan if `on_exhaust_replan` configured
  - Otherwise, escalate to `HUMAN_RETRY_REQUIRED`

### 5.5 Replan Recovery

**Trigger**: Refine loop exhausted with `on_exhaust_replan` configured

**Mechanics**:
- `replan_context` activated with:
  - `source_review_step`: Original review step
  - `replan_step`: Replanning step
  - `target_artifact`: Artifact to replan
  - `replan_attempt`: Current replan count
- Pre-replan checksum saved for convergence check
- Replan history tracked in `replan_history`

**Budget Tracking**:
- `planning_attempt_count` limits total recovery attempts
- `PLANNING_ATTEMPT_BUDGET_EXCEEDED` failure when exhausted

## 6. Error Handling Patterns

### 6.1 Exception Classification Pattern

```python
def _classify_exception_v2(exc: Exception) -> tuple[str, str, str]:
    """Map exception types to (failure_class, failure_code, failure_source)."""
    if isinstance(exc, CoderInvocationError):
        if _looks_like_transient_error(str(exc)):
            return "AUTO_RETRYABLE", "TRANSIENT_API_ERROR", "adapter"
        return "HUMAN_RETRY_REQUIRED", "ADAPTER_INVOCATION_FAILED", "adapter"
    if isinstance(exc, MetaJsonMissingError):
        return "HUMAN_RETRY_REQUIRED", "META_JSON_MISSING", "validator"
    if isinstance(exc, MetaJsonInvalidError):
        return "HUMAN_RETRY_REQUIRED", "META_JSON_INVALID", "validator"
    if isinstance(exc, ArtifactMissingError):
        # ... classification logic
    return "FATAL", "UNEXPECTED_RUNNER_ERROR", "runner"
```

### 6.2 Transient Error Detection

```python
def _looks_like_transient_error(message: str) -> bool:
    lowered = message.lower()
    hints = (
        "connection error", "fetch failed", "timed out", "timeout",
        "temporar", "rate limit", "429", "service unavailable",
        "api error", "network error",
    )
    return any(hint in lowered for hint in hints)
```

### 6.3 Non-Progressing Failure Detection

Non-progressing failures do not increment reject counts:

```python
def _is_non_progressing(*, failure_class: str, failure_code: str, failure_source: str) -> bool:
    return (
        failure_source in {"runner", "validator"}
        and failure_class == "HUMAN_RETRY_REQUIRED"
        and failure_code in {
            "INVALID_RUNNER_CONFIGURATION",
            "UNKNOWN_CODER",
            "STEP_CONTRACT_MISMATCH",
        }
    )
```

## 7. Daemon-Specific Failure Modes

### 7.1 Child Process Failures

| Failure Code | Condition | Handling |
|--------------|-----------|----------|
| `CHILD_RESULT_MISSING` | Child process exited without `result.json` | Return failure result, log diagnostics |
| `step_timeout_exceeded` | Child process exceeded timeout | Terminate process, return failure |
| `kill_grace_exceeded` | Process did not terminate after SIGTERM | Force kill with SIGKILL |
| `log_inactive` | No log activity for `stalled_seconds` | Mark as stalled, continue monitoring |

### 7.2 Backend Communication Failures

| Condition | Handling |
|-----------|----------|
| Backend unreachable | Retry with exponential backoff |
| Claim failed | Wait `poll_seconds` before next claim attempt |
| Submission failed | Retry submission, log error |

### 7.3 Daemon Recovery

The daemon automatically handles:
- Process crashes: Detect via `poll()`, harvest available results
- Timeouts: Terminate and report failure
- Stalled processes: Log warning, continue monitoring
- Missing results: Generate failure envelope with diagnostics

## 8. Operational Troubleshooting Guide

### 8.1 Step Failure Diagnosis

**Symptom**: Step fails with `WAITING_FOR_HUMAN_INTERVENTION`

**Diagnosis Steps**:

1. Check job state:
   ```bash
   cat .ukbe-runner/jobs/<template_group>/<job_id>/job.json | jq '.last_failure_'
   ```

2. Check step logs:
   ```bash
   ls .ukbe-runner/jobs/<template_group>/<job_id>/<step_dir>/
   # Review: raw_output.txt, stderr.txt, step_manifest.json
   ```

3. Check sidecar:
   ```bash
   cat <artifact_path>.meta.json
   ```

4. Check usage:
   ```bash
   cat .ukbe-runner/jobs/<template_group>/<job_id>/<step_dir>/usage.json
   ```

### 8.2 Common Failure Scenarios

#### Scenario: Coder Timeout

**Symptoms**:
- `CoderInvocationError` with message "timed out after X seconds"
- No `meta.json` written

**Diagnosis**:
1. Check `step_manifest.json` for duration
2. Check `raw_output.txt` for partial output
3. Review model latency in usage data

**Resolution**:
- Increase timeout: `coder_timeout_seconds` in step config
- Use faster model variant
- Simplify prompt

#### Scenario: Missing Artifact

**Symptoms**:
- `ArtifactMissingError` with list of missing paths
- `meta.json` exists but artifacts not on disk

**Diagnosis**:
1. Review `meta.json` for artifact paths
2. Check if paths are absolute vs relative
3. Verify coder created files in expected locations

**Resolution**:
- Fix artifact path resolution in workflow context
- Update step `produces` configuration
- Ensure coder writes to correct location

#### Scenario: Schema Validation Failure

**Symptoms**:
- `MetaJsonInvalidError` with validation message
- `meta.json` exists but incomplete

**Diagnosis**:
1. Review `meta.json` against schema
2. Check for missing fields
3. Check field types

**Resolution**:
- Fix coder prompt to produce valid output
- Add missing fields to coder output
- Validate JSON structure before submission

#### Scenario: Rate Limit / API Error

**Symptoms**:
- `CoderInvocationError` with "rate limit" or "429"
- Transient error classification

**Diagnosis**:
1. Check API quotas
2. Review rate limit headers in response
3. Check concurrent request count

**Resolution**:
- Wait for rate limit reset
- Reduce concurrent requests
- Use API key with higher quota

### 8.3 Recovery Commands

**Approve and retry step**:
```bash
run-approve-step.bat --job-id <job_id> --step <step>
```

**Reset step for retry**:
```bash
run-reset-step.bat --job-id <job_id> --step <step>
```

**Manual intervention**:
1. Fix blocking condition
2. Update job state if needed
3. Use backend API to clear intervention flag

## 9. Failure History Tracking

### 9.1 State Fields

| Field | Type | Purpose |
|-------|------|---------|
| `last_failure_class` | `str \| None` | Current failure class |
| `last_failure_code` | `str \| None` | Current failure code |
| `last_failure_reason` | `str \| None` | Human-readable reason |
| `last_failure_source` | `str \| None` | Failure source attribution |
| `failure_history` | `list[dict]` | Historical failure records |
| `auto_retry_count_by_step` | `dict[str, int]` | Auto-retry counts per step |
| `human_retry_count_by_step` | `dict[str, int]` | Human-retry counts per step |

### 9.2 Failure History Entry

```json
{
  "step": "generate_plan",
  "failure_class": "HUMAN_RETRY_REQUIRED",
  "failure_code": "META_JSON_MISSING",
  "failure_source": "validator",
  "timestamp": "2026-07-16T22:39:14+08:00"
}
```

## 10. Notification Integration

### 10.1 Failure Notifications

| Event | Notification Type |
|-------|-------------------|
| `STEP_FAILED` | Step-specific failure notification |
| `FAILED` | Workflow failure notification |
| `WAITING_FOR_HUMAN_INTERVENTION` | Human intervention required notification |

### 10.2 Notification Configuration

```toml
[workflow.notifications]
enabled = true
pushover_api_token_env = "PUSHOVER_API_TOKEN"
pushover_user_key_env = "PUSHOVER_USER_KEY"
```

## 11. Appendix: Error Codes Reference

### 11.1 Runner Error Codes

| Code | Class | Source | Description |
|------|-------|--------|-------------|
| `INVALID_RUNNER_CONFIGURATION` | `HUMAN_RETRY_REQUIRED` | `runner` | Invalid runner configuration |
| `UNKNOWN_CODER` | `HUMAN_RETRY_REQUIRED` | `runner` | Coder not found in registry |
| `STEP_CONTRACT_MISMATCH` | `HUMAN_RETRY_REQUIRED` | `validator` | Artifact contract violation |
| `PLANNING_ATTEMPT_BUDGET_EXCEEDED` | `HUMAN_RETRY_REQUIRED` | `runner` | Recovery budget exhausted |
| `REFINEMENT_EXHAUSTED` | `HUMAN_RETRY_REQUIRED` | `runner` | Refine loop exhausted |
| `UNEXPECTED_RUNNER_ERROR` | `FATAL` | `runner` | Unknown exception |

### 11.2 Adapter Error Codes

| Code | Class | Source | Description |
|------|-------|--------|-------------|
| `TRANSIENT_API_ERROR` | `AUTO_RETRYABLE` | `adapter` | Temporary API failure |
| `ADAPTER_INVOCATION_FAILED` | `HUMAN_RETRY_REQUIRED` | `adapter` | Coder process failure |

### 11.3 Validator Error Codes

| Code | Class | Source | Description |
|------|-------|--------|-------------|
| `META_JSON_MISSING` | `HUMAN_RETRY_REQUIRED` | `validator` | Sidecar not written |
| `META_JSON_INVALID` | `HUMAN_RETRY_REQUIRED` | `validator` | Sidecar schema invalid |
| `ARTIFACT_FILES_MISSING` | `HUMAN_RETRY_REQUIRED` | `validator` | Artifact paths not found |

### 11.4 Daemon Error Codes

| Code | Condition |
|------|-----------|
| `CHILD_RESULT_MISSING` | Process exited without result file |
| `DAEMON_INITIALIZATION_FAILED` | Daemon startup failure |
| `ENGINE_VERSION_NOT_FOUND` | Engine version missing from store |

## 12. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-16 | Initial baseline generated from codebase analysis | 00_repo_master_docs_bootstrap_v1 |