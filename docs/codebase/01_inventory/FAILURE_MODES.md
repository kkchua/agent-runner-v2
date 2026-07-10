---
template_id: "CB-04-FM"
title: "Failure Modes Catalog - agent-runner-v2"
Status: draft
managed_by: workflow-generated
generated: "2026-07-10T20:11:50+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04c_generate_failure_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04c_generate_failure_docs`
> This file is workflow-generated and protected from manual edits.

# Failure Modes Catalog: agent-runner-v2

This document catalogs all error conditions, exception handling patterns, and recovery procedures in the agent-runner-v2 codebase.

## 1. Overview

The agent-runner-v2 system uses a strict v2 failure handling model that replaces implicit v1 recovery paths with explicit exception types and classified failure modes. Each failure has a clear classification determining whether it is auto-retryable, requires human intervention, or is fatal.

### Key v2 Principles

- **No silent recovery** — All failures route explicitly through runner failure handling
- **No markdown write-backs** — Runner does not write to markdown files
- **Meta.json as sole channel** — Structured results only via sidecar
- **Explicit classification** — Every failure maps to `AUTO_RETRYABLE`, `HUMAN_RETRY_REQUIRED`, or `FATAL`

---

## 2. Exception Catalog

### 2.1 Core Exception Types

Defined in `agent_runner_v2/exceptions.py`:

| Exception | Description | Attributes |
|-----------|-------------|------------|
| `PreflightBlockedError` | Preflight check blocked step execution (e.g., artifact status not approved) | message |
| `MetaJsonMissingError` | Coder did not write expected meta.json sidecar | message |
| `MetaJsonInvalidError` | Meta.json exists but fails schema validation | message |
| `ArtifactMissingError` | Artifact paths referenced in meta.json don't exist on disk | message, missing (list[str]) |

### 2.2 Adapter-Level Exceptions

Defined in `agent_runner_v2/coder_adapters.py`:

| Exception | Description | Attributes |
|-----------|-------------|------------|
| `CoderInvocationError` | Coder subprocess failed (non-zero exit, timeout, or structured output error) | message, command, return_code, stdout, stderr, raw_events |

### 2.3 Standard Library Exceptions Used

| Exception | Usage Context |
|-----------|---------------|
| `subprocess.TimeoutExpired` | Coder subprocess exceeded timeout (caught and wrapped in `CoderInvocationError`) |
| `json.JSONDecodeError` | Invalid JSON in meta.json or coder output (caught and wrapped) |
| `FileNotFoundError` | Job state file missing, artifact file missing |
| `ValueError` | Invalid configuration, schema validation failures |
| `RuntimeError` | Backend request failures, workflow module not loaded |

---

## 3. Failure Classification System

### 3.1 Classification Constants

Defined in `agent_runner_v2/workflow_router.py` and `agent_runner_v2/job_state.py`:

```python
CONTROL_CLASSES = {"AUTO_RETRYABLE", "HUMAN_RETRY_REQUIRED", "FATAL"}
FAILURE_SOURCES = {"runner", "adapter", "model", "validator"}
```

### 3.2 Classification Categories

| Class | Description | Retry Behavior |
|-------|-------------|----------------|
| `AUTO_RETRYABLE` | Transient errors that may succeed on retry | Automatic retry with backoff |
| `HUMAN_RETRY_REQUIRED` | Errors requiring operator intervention | Pause for human action |
| `FATAL` | Permanent failures that cannot be recovered | Workflow termination |

### 3.3 Failure Source Attribution

| Source | Description | Examples |
|--------|-------------|----------|
| `runner` | Core runner logic errors | Configuration errors, routing failures |
| `adapter` | Coder adapter invocation errors | Subprocess timeout, API errors |
| `model` | LLM/model-level errors | Rejection, malformed output |
| `validator` | Validation errors | Schema validation, artifact checks |

---

## 4. Exception-to-Classification Mapping

### 4.1 Hard Failure Routing (from `route_after_failure`)

The `_classify_exception_v2()` function in `workflow_router.py` maps exceptions:

| Exception | Failure Class | Failure Code | Source |
|-----------|---------------|--------------|--------|
| `CoderInvocationError` (transient indicators) | `AUTO_RETRYABLE` | `TRANSIENT_API_ERROR` | `adapter` |
| `CoderInvocationError` (other) | `HUMAN_RETRY_REQUIRED` | `ADAPTER_INVOCATION_FAILED` | `adapter` |
| `MetaJsonMissingError` | `HUMAN_RETRY_REQUIRED` | `META_JSON_MISSING` | `validator` |
| `MetaJsonInvalidError` | `HUMAN_RETRY_REQUIRED` | `META_JSON_INVALID` | `validator` |
| `ArtifactMissingError` | `HUMAN_RETRY_REQUIRED` | `ARTIFACT_FILES_MISSING` | `validator` |
| Any other exception | `FATAL` | `UNEXPECTED_RUNNER_ERROR` | `runner` |

### 4.2 Transient Error Detection

The `_looks_like_transient_error()` function checks for these patterns (case-insensitive):

- "connection error"
- "fetch failed"
- "timed out" / "timeout"
- "temporar" (prefix match)
- "rate limit"
- "429" (HTTP status)
- "service unavailable"
- "api error"
- "network error"

### 4.3 Model Rejection Classification

The `_classify_model_rejection()` function in `workflow_router.py` classifies model rejections:

| Condition | Failure Class | Code |
|-----------|---------------|------|
| `reject_code` in `CONTROL_CLASSES` | Use reject_code as class | From reject_code |
| Transient indicators in remark | `AUTO_RETRYABLE` | `MODEL_REJECTED` |
| Keywords: pending, not approved, approval, preflight, missing input, missing artifact, schema, invalid | `HUMAN_RETRY_REQUIRED` | `MODEL_REJECTED` |
| Keywords: forbidden, not allowed, out of scope, scope, policy | `FATAL` | `MODEL_REJECTED` |
| Default | `HUMAN_RETRY_REQUIRED` | `MODEL_REJECTED` |

---

## 5. Error Handling Patterns by Step Type

### 5.1 Coder Steps

**Location**: `agent_runner_v2/step_runner.py` → `run_step()`

**Flow**:
1. Invoke coder via `invoke_coder()`
2. Coder writes meta.json sidecar
3. Read and validate meta.json (`_read_and_validate_meta_json()`)
4. Validate artifact files exist (`_validate_artifact_files_exist()`)
5. Return `StepResult` or raise exception

**Error Handling**:

| Error Point | Exception | Handling |
|-------------|-----------|----------|
| Coder subprocess timeout | `CoderInvocationError` | Return code 124, route to failure |
| Coder non-zero exit | `CoderInvocationError` | Route to failure |
| Missing meta.json | `MetaJsonMissingError` | Hard failure, no recovery |
| Invalid meta.json schema | `MetaJsonInvalidError` | Hard failure, attempt repair |
| Artifact files missing | `ArtifactMissingError` | Hard failure |
| Artifacts not in produces list | `ArtifactMissingError` | Hard failure |

### 5.2 Action Steps

**Location**: `agent_runner_v2/step_runner.py` → `run_action()`

**Flow**:
1. Execute action via `runner_actions.execute()`
2. Action writes meta.json sidecar
3. Read and validate meta.json
4. Return `StepResult`

**Error Handling**:

| Error Point | Exception | Handling |
|-------------|-----------|----------|
| Action execution error | Propagated from action | Route to failure |
| Missing meta.json | `MetaJsonMissingError` | Hard failure |
| Invalid meta.json | `MetaJsonInvalidError` | Hard failure |

### 5.3 Review/Refine Loops

**Location**: `agent_runner_v2/workflow_router.py`

**Flow**:
1. Step returns REJECTED status
2. Check for `on_reject_refine` configuration
3. If configured, enter refine loop
4. Loop iterations tracked in `loop_context`
5. If max iterations exceeded, trigger replan

**Error Handling**:

| Condition | Behavior |
|-----------|----------|
| Reject with refine route | Enter loop, increment iteration |
| Loop exhausted | Trigger replan or fail |
| Replan exhausted | `HUMAN_RETRY_REQUIRED`, status `WAITING_FOR_HUMAN_INTERVENTION` |
| Planning budget exceeded | `HUMAN_RETRY_REQUIRED`, code `PLANNING_ATTEMPT_BUDGET_EXCEEDED` |

---

## 6. Retry and Recovery Mechanics

### 6.1 Retry Counters

Stored in job state (`job.json`):

| Counter | Key | Description |
|---------|-----|-------------|
| `reject_counts` | `{step: count}` | Per-step rejection count |
| `auto_retry_count_by_step` | `{step: count}` | Auto-retry attempts per step |
| `human_retry_count_by_step` | `{step: count}` | Human retry attempts per step |
| `planning_attempt_count` | int | Total planning attempts |

### 6.2 Retry Limits

| Limit | Source | Behavior When Exceeded |
|-------|--------|------------------------|
| `max_rejects` | Step configuration | Workflow FAILURE |
| `max_iterations` | `on_reject_refine` config | Trigger replan |
| `max_replans` | `on_exhaust_replan` config | Human intervention |
| `max_planning_attempts` | Group configuration | Human intervention |

### 6.3 Job Status Transitions

| From Status | Event | To Status |
|-------------|-------|-----------|
| `IN_PROGRESS` | Step APPROVED | `IN_PROGRESS` (advance) |
| `IN_PROGRESS` | Step REJECTED (retryable) | `WAITING_FOR_AUTO_RETRY` |
| `IN_PROGRESS` | Step REJECTED (max exceeded) | `FAILED` |
| `IN_PROGRESS` | Hard failure (auto-retryable) | `WAITING_FOR_AUTO_RETRY` |
| `IN_PROGRESS` | Hard failure (human required) | `WAITING_FOR_HUMAN_INTERVENTION` |
| `WAITING_FOR_AUTO_RETRY` | Retry initiated | `IN_PROGRESS` |
| `WAITING_FOR_HUMAN_INTERVENTION` | Human approval | `IN_PROGRESS` |
| `WAITING_FOR_HUMAN_INTERVENTION` | Human reject (max exceeded) | `FAILED` |
| Any | Fatal error | `FAILED` |

### 6.4 Non-Progressing Failures

Certain failures are classified as "non-progressing" — they do not increment reject counts:

```python
_is_non_progressing(
    failure_source="runner",
    failure_class="HUMAN_RETRY_REQUIRED",
    failure_code="INVALID_RUNNER_CONFIGURATION" | "UNKNOWN_CODER"
)
```

These indicate runner configuration errors that won't be fixed by retrying the step.

---

## 7. Recovery Procedures

### 7.1 Auto-Retryable Recovery

**Trigger**: `WAITING_FOR_AUTO_RETRY` status

**Procedure**:
1. Wait for backoff period
2. Re-invoke same step with same inputs
3. Increment `auto_retry_count_by_step`
4. If success, continue workflow
5. If still failing after max retries, escalate to human intervention

### 7.2 Human Intervention Recovery

**Trigger**: `WAITING_FOR_HUMAN_INTERVENTION` status

**Procedure**:
1. Operator examines failure details in job.json
2. Operator examines step logs and artifacts
3. Operator may:
   - Fix underlying issue and `approve` step
   - `reject` step (causes retry)
   - `force-approve` step
4. On approval, workflow resumes from next step

### 7.3 Refinement Loop Recovery

**Trigger**: Step rejected with `on_reject_refine` config

**Procedure**:
1. Original artifact preserved
2. Review file created with feedback
3. Refine step invoked with review context
4. Refine step updates target artifact
5. Review step re-invoked
6. Loop continues until approved or max iterations reached

### 7.4 Replan Recovery

**Trigger**: Refinement loop exhausted with `on_exhaust_replan` config

**Procedure**:
1. Capture pre-replan checksum of target artifact
2. Invoke replan step with review feedback
3. Replanner generates new plan/task graph
4. Reset loop context
5. Continue with new plan

---

## 8. Operational Troubleshooting Guide

### 8.1 Diagnosing Workflow Failures

**Check job state**:
```bash
cat %USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job-id>\job.json
```

**Key fields to examine**:

| Field | Meaning |
|-------|---------|
| `job_status` | Current workflow status |
| `current_step` | Step that failed or is pending |
| `last_failure_class` | `AUTO_RETRYABLE`, `HUMAN_RETRY_REQUIRED`, or `FATAL` |
| `last_failure_code` | Machine-readable failure code |
| `last_failure_reason` | Human-readable failure description |
| `last_failure_source` | `runner`, `adapter`, `model`, or `validator` |
| `failure_history` | Chronological failure log |
| `retry_history` | All retry attempts with timestamps |

### 8.2 Common Failure Scenarios

#### Scenario 1: Meta.json Missing

**Symptoms**:
- Failure code: `META_JSON_MISSING`
- Coder process exited but sidecar not written

**Diagnosis**:
1. Check coder logs in step directory (`raw_output.txt`, `stderr.txt`)
2. Verify coder actually ran (check `manifest.json`)
3. Check if coder crashed before writing sidecar

**Recovery**:
- Typically `HUMAN_RETRY_REQUIRED`
- Re-run step after fixing coder issue

#### Scenario 2: Artifact Files Missing

**Symptoms**:
- Failure code: `ARTIFACT_FILES_MISSING`
- Meta.json claims artifacts that don't exist

**Diagnosis**:
1. Check `meta.json` for claimed artifact paths
2. Verify paths exist relative to project root
3. Check coder output for write failures

**Recovery**:
- Typically `HUMAN_RETRY_REQUIRED`
- Re-run step after investigating coder write permissions

#### Scenario 3: Transient API Errors

**Symptoms**:
- Failure class: `AUTO_RETRYABLE`
- Failure code: `TRANSIENT_API_ERROR`
- Keywords in error: "rate limit", "timeout", "connection error"

**Diagnosis**:
- Check service status of LLM provider
- Verify network connectivity
- Check rate limit quotas

**Recovery**:
- Automatic retry with backoff
- If persistent, escalate to human

#### Scenario 4: Model Rejection

**Symptoms**:
- Step status: `REJECTED`
- Review file created with feedback

**Diagnosis**:
1. Read review file for model's concerns
2. Check if concerns are addressable
3. Verify inputs meet requirements

**Recovery**:
- Enter refine loop (if configured)
- Manual fix and retry
- Escalate to replan (if loop exhausted)

#### Scenario 5: Planning Budget Exceeded

**Symptoms**:
- Failure code: `PLANNING_ATTEMPT_BUDGET_EXCEEDED`
- Status: draft

**Diagnosis**:
- Check `planning_attempt_count` in job.json
- Review failure history for repeated attempts
- Verify `max_planning_attempts` in workflow config

**Recovery**:
- Human must intervene
- Consider increasing budget or simplifying task

#### Scenario 6: Invalid Runner Configuration

**Symptoms**:
- Failure code: `INVALID_RUNNER_CONFIGURATION` or `UNKNOWN_CODER`
- Source: `runner`
- Non-progressing (no retry count increment)

**Diagnosis**:
- Check step configuration in template_groups.py
- Verify coder name is valid
- Check workflow module loading

**Recovery**:
- Fix configuration
- Do not retry same step (config error won't self-resolve)

---

## 9. Failure History Tracking

### 9.1 Failure History Entry Schema

```json
{
  "step": "step_name",
  "failure_class": "AUTO_RETRYABLE|HUMAN_RETRY_REQUIRED|FATAL",
  "failure_code": "ERROR_CODE",
  "failure_source": "runner|adapter|model|validator",
  "timestamp": "2026-07-10T20:11:50+08:00"
}
```

### 9.2 Retry History Entry Schema

```json
{
  "step": "step_name",
  "attempted_at": "2026-07-10T20:11:50+08:00",
  "coder_used": "claude|codex|qwen",
  "return_code": 0,
  "result_status": "APPROVED|REJECTED|FAILED_BEFORE_RESULT",
  "result_remark": "...",
  "reject_code": "...",
  "reject_type": "...",
  "failure_source": "..."
}
```

---

## 10. Meta.json Validation Errors

The `_read_and_validate_meta_json()` function enforces this schema:

| Check | Error if Failed | Exception Raised |
|-------|-----------------|------------------|
| File exists | File missing | `MetaJsonMissingError` |
| Valid JSON | Parse error | `MetaJsonInvalidError` |
| JSON is object | Not a dict | `MetaJsonInvalidError` |
| Schema version | Not "v2" or "artifact_meta_v1" | `MetaJsonInvalidError` |
| `coder_result` present | Missing key | `MetaJsonInvalidError` |
| `coder_result.status` valid | Not "APPROVED" or "REJECTED" | `MetaJsonInvalidError` |
| `coder_result.artifacts` present | Missing or not dict | `MetaJsonInvalidError` |
| `coder_result.recorded_at` present | Missing or empty | `MetaJsonInvalidError` |

---

## 11. Sidecar Polling and Timeout Handling

### 11.1 Timeout Configuration

| Timeout | Default | Configuration Source |
|---------|---------|---------------------|
| Coder timeout | 600s | Step config → Env → Global config → Default |
| Sidecar poll interval | 3.0s | Hardcoded |
| Sidecar settle delay | 5.0s | Hardcoded |
| Post-complete grace | 12.0s | Env → Global config → Default |

### 11.2 Early Exit Signal

The coder adapter polls for meta.json as an early-exit signal:

1. Process launches via Popen
2. Poll every 3 seconds for:
   - Process exit (normal completion)
   - Valid sidecar written (early completion)
3. If sidecar valid:
   - Wait settle delay (5s)
   - Wait grace window (12s) for process to exit naturally
   - Force terminate if still running
4. Return code 0 if sidecar-triggered

### 11.3 Sidecar Validation Checks

The `_is_valid_sidecar_json()` function checks:

1. File stat successful (not locked)
2. Modification time stable (100ms check)
3. JSON parses successfully
4. Schema version valid ("v2" or "artifact_meta_v1")
5. `coder_result` is dict
6. Status is "APPROVED" or "REJECTED"
7. `artifacts` is dict
8. `recorded_at` is non-empty

---

## 12. Backend API Error Handling

### 12.1 Backend Client Errors

In `agent_runner_v2/backend_client.py`:

| Error | Exception |
|-------|-----------|
| HTTP error (4xx, 5xx) | `RuntimeError` with status and body |
| URL error (connection) | `RuntimeError` with error details |
| Empty response | Empty dict returned |

### 12.2 Backend Worker Mode Errors

| Scenario | Behavior |
|----------|----------|
| Step claim fails | Log and retry poll loop |
| Step completion fails | Log error, continue |
| Heartbeat fails | Log warning, retry |

---

## 13. Notification on Failure

The `notification_manager.py` sends notifications for:

| Event | Notification Type |
|-------|-------------------|
| `STEP_FAILED` | Step notification (if configured) |
| `WAITING_FOR_HUMAN_INTERVENTION` | Workflow notification |
| `FAILED` | Workflow notification |

Notifications require:
- Step config: `enable_notifications: True`
- State with `workflow_name` and `template_group`
- Valid timestamps in state

---

## 14. Summary of Error Handling Differences (v1 vs v2)

| Aspect | v1 | v2 |
|--------|-----|-----|
| Recovery paths | Silent fallback functions | Explicit exceptions only |
| Sidecar channel | Multiple channels | meta.json only |
| Markdown writes | Runner writes metadata | Runner never writes markdown |
| Blocking issues | Runner extracts from content | Coder owns analysis, runner trusts REJECTED |
| Review convergence | Runner decides | Coder decides |
| Failure classification | Implicit | Explicit `CONTROL_CLASSES` |
| Content analysis | Runner validates markdown | Sidecar schema validation only |

---

## 15. References

- `agent_runner_v2/exceptions.py` — Exception definitions
- `agent_runner_v2/step_runner.py` — Step execution and validation
- `agent_runner_v2/workflow_router.py` — Failure routing and classification
- `agent_runner_v2/job_state.py` — State management and counters
- `agent_runner_v2/coder_adapters.py` — Invocation and timeout handling
- `agent_runner_v2/backend_client.py` — API error handling

---

*Generated: 2026-07-10T20:11:50+08:00*
*Workflow: 00_master_docs_bootstrap_v2 / step: 04c_generate_failure_docs*
