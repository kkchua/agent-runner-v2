---
template_id: "CB-04-FM"
workflow: "00_master_docs_bootstrap_v1"
step: "04c_generate_failure_docs"
generated: "2026-07-09T21:38:49+08:00"
managed_by: workflow-generated
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04c_generate_failure_docs`
> This file is workflow-generated and protected from manual edits.

# Failure Modes: agent-runner-v2

Comprehensive catalog of all error conditions, exception handling patterns, and recovery procedures in the agent-runner-v2 codebase.

## 1. Exception Taxonomy

### 1.1 Core Exception Types

The codebase defines explicit exception types in `agent_runner_v2/exceptions.py`:

| Exception | Module | Purpose |
|-----------|--------|---------|
| `PreflightBlockedError` | `exceptions.py` | Raised when preflight checks block step execution (e.g., artifact status not approved) |
| `MetaJsonMissingError` | `exceptions.py` | Raised when coder did not write expected meta.json sidecar after invocation |
| `MetaJsonInvalidError` | `exceptions.py` | Raised when meta.json exists but fails schema validation |
| `ArtifactMissingError` | `exceptions.py` | Raised when coder_result.artifacts references paths that don't exist on disk |
| `CoderInvocationError` | `coder_adapters.py` | Raised when coder process fails (non-zero return code, timeout, or communication error) |

### 1.2 Exception Inheritance

```
Exception (built-in)
├── PreflightBlockedError
├── MetaJsonMissingError
├── MetaJsonInvalidError
├── ArtifactMissingError
└── CoderInvocationError (dataclass)
```

## 2. Failure Classification System

### 2.1 CONTROL_CLASSES

Defined in `agent_runner_v2/job_state.py`:

```python
CONTROL_CLASSES = {"AUTO_RETRYABLE", "HUMAN_RETRY_REQUIRED", "FATAL"}
```

| Class | Meaning | Routing Behavior |
|-------|---------|------------------|
| `AUTO_RETRYABLE` | Transient error that may succeed on retry | Sets job status to `WAITING_FOR_AUTO_RETRY` |
| `HUMAN_RETRY_REQUIRED` | Requires human intervention to resolve | Sets job status to `WAITING_FOR_HUMAN_INTERVENTION` |
| `FATAL` | Unrecoverable error, workflow cannot continue | Sets job status to `FAILED` |

### 2.2 FAILURE_SOURCES

```python
FAILURE_SOURCES = {"runner", "adapter", "model", "validator"}
```

| Source | Description | Typical Failures |
|--------|-------------|------------------|
| `runner` | Internal runner logic error | Configuration errors, state inconsistencies |
| `adapter` | Coder adapter invocation failure | Process spawn failure, timeout, communication error |
| `model` | LLM/coder returned REJECTED | Content rejection, validation failure |
| `validator` | Post-invocation validation failure | Missing meta.json, invalid schema, missing artifacts |

### 2.3 Non-Terminal Job Statuses

```python
NON_TERMINAL_JOB_STATUSES = {
    "IN_PROGRESS",
    "WAITING_FOR_AUTO_RETRY",
    "WAITING_FOR_HUMAN_INTERVENTION",
    "WAITING_FOR_HUMAN_APPROVAL",
}
```

## 3. Exception Catalog

### 3.1 Exception Detail Table

| Exception | When Raised | Raised By | Handling | Recovery |
|-----------|-------------|-----------|----------|----------|
| `PreflightBlockedError` | Artifact required by step has status not in `APPROVED`, `COMPLETED`, or `DRAFT` | `check_preflight_artifact_status()` in `job_state.py` | Caught in `run_agent.py`, routes to failure with `HUMAN_RETRY_REQUIRED` | Approve or complete the blocking artifact; ensure document is in correct status |
| `MetaJsonMissingError` | Coder completed but meta.json sidecar not found at expected path | `_read_and_validate_meta_json()` in `step_runner.py` | Routed via `route_after_failure()` with `HUMAN_RETRY_REQUIRED` | Check coder logs; ensure coder writes sidecar; verify path resolution |
| `MetaJsonInvalidError` | meta.json exists but fails schema validation (missing fields, wrong type, invalid status) | `_read_and_validate_meta_json()` in `step_runner.py` | Routed via `route_after_failure()` with `HUMAN_RETRY_REQUIRED` | Check coder output; ensure valid JSON structure with required fields |
| `ArtifactMissingError` | meta.json references artifact paths that don't exist on disk | `_validate_artifact_files_exist()` in `step_runner.py` | Routed via `route_after_failure()` with `HUMAN_RETRY_REQUIRED` | Check coder file writes; verify paths in meta.json match actual files |
| `ArtifactMissingError` (unauthorized) | Step reported artifacts not in its `produces` list | `_validate_artifacts_in_produces_list()` in `step_runner.py` | Routed via `route_after_failure()` with `HUMAN_RETRY_REQUIRED` | Update step config `produces` list or coder to only write declared artifacts |
| `CoderInvocationError` | Coder process returned non-zero exit code | `invoke_coder()` in `coder_adapters.py` | Routed via `route_after_failure()` with classification based on error message | Check process logs; verify coder installation; check timeout settings |
| `CoderInvocationError` (timeout) | Coder process exceeded timeout without producing valid sidecar | `_run_with_sidecar_poll()` in `coder_adapters.py` | Routed via `route_after_failure()` with `AUTO_RETRYABLE` if transient | Increase timeout; check coder performance; verify network connectivity |

### 3.2 Exception Classification Logic

Located in `workflow_router.py`:

```python
def _classify_exception_v2(exc: Exception) -> tuple[str, str, str]:
    """Map v2 exception types to (failure_class, failure_code, failure_source)."""
    if isinstance(exc, CoderInvocationError):
        if _looks_like_transient_error(str(exc)):
            return "AUTO_RETRYABLE", "TRANSIENT_API_ERROR", "adapter"
        return "HUMAN_RETRY_REQUIRED", "ADAPTER_INVOCATION_FAILED", "adapter"
    if isinstance(exc, MetaJsonMissingError):
        return "HUMAN_RETRY_REQUIRED", "META_JSON_MISSING", "validator"
    if isinstance(exc, MetaJsonInvalidError):
        return "HUMAN_RETRY_REQUIRED", "META_JSON_INVALID", "validator"
    if isinstance(exc, ArtifactMissingError):
        return "HUMAN_RETRY_REQUIRED", "ARTIFACT_FILES_MISSING", "validator"
    # Unknown exception — treat as fatal
    return "FATAL", "UNEXPECTED_RUNNER_ERROR", "runner"
```

Transient error detection:

```python
def _looks_like_transient_error(message: str) -> bool:
    lowered = message.lower()
    hints = (
        "connection error", "fetch failed", "timed out", "timeout", "temporar",
        "rate limit", "429", "service unavailable", "api error", "network error",
    )
    return any(hint in lowered for hint in hints)
```

## 4. Error Handling Patterns by Step Type

### 4.1 Coder Steps (LLM Invocation)

**Execution flow in `step_runner.py:run_step()`:**

1. **Pre-invocation**: Resolve meta.json path before coder runs
2. **Invocation**: Call `invoke_coder()` which may raise `CoderInvocationError`
3. **Sidecar reading**: `_repair_or_validate_meta_json()` may raise `MetaJsonMissingError` or `MetaJsonInvalidError`
4. **Artifact validation**: `_validate_artifact_files_exist()` may raise `ArtifactMissingError`
5. **Template conformance**: `_validate_template_conformance()` (optional)
6. **Produces validation**: `_validate_artifacts_in_produces_list()` may raise `ArtifactMissingError`

**Failure routing:**
- All exceptions bubble up to `run_agent.py`
- Caught and routed via `workflow_router.route_after_failure()`
- Exit codes: 0=continue, 1=intervention required, 2=fatal

### 4.2 Action Steps (Deterministic)

**Execution flow in `step_runner.py:run_action()`:**

1. Execute action via `runner_actions.execute()`
2. Action writes its own meta.json
3. Validate with `_read_and_validate_meta_json()`
4. Validate artifacts exist
5. Enrich sidecar with runner_data

**Failure routing:**
- Action-specific exceptions caught same as coder steps
- Action is responsible for writing valid meta.json

### 4.3 Review Steps

**Rejection handling in `workflow_router.py:_route_rejected()`:**

1. Check for `on_reject_refine` configuration
2. If configured, enter refine/replan loop
3. If not, classify as model rejection
4. Update failure tracking
5. Route to auto-retry or human intervention

## 5. Retry and Recovery Procedures

### 5.1 Retry Mechanisms

**Auto-retry (CONTROL_CLASS = AUTO_RETRYABLE):**

```python
set_job_status(state, "WAITING_FOR_AUTO_RETRY")
```

Triggered by:
- Transient API errors (connection, timeout, rate limit)
- Service unavailable errors

**Human retry (CONTROL_CLASS = HUMAN_RETRY_REQUIRED):**

```python
set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
state["pending_intervention_for"] = step
```

Triggered by:
- Configuration errors
- Schema validation failures
- Missing artifacts
- Model rejections that exceed retry limits

### 5.2 Refine/Replan Loop Mechanics

**Loop configuration in template_groups.py:**

```python
"on_reject_refine": {
    "step": "refine_step_name",
    "artifact": "ARTIFACT_KEY",
    "max_iterations": 2,
    "exhausted_failure_code": "REFINEMENT_EXHAUSTED",
    "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
}
```

**Loop execution:**

1. Review step returns REJECTED
2. `_route_loop_or_replan()` checks iteration count
3. If under max_iterations: trigger refine step
4. If exhausted: check for replan configuration
5. If replan exhausted: mark as HUMAN_RETRY_REQUIRED

**Replan configuration:**

```python
"on_exhaust_replan": {
    "step": "replan_step_name",
    "artifact": "ARTIFACT_KEY",
    "max_replans": 1,
    "terminal_failure_code": "REPLAN_EXHAUSTED",
}
```

### 5.3 Planning Attempt Budget

Prevents infinite refinement loops:

```python
def _consume_planning_attempt_budget(*, state: dict, group_cfg: dict) -> tuple[bool, int]:
    limit = int(group_cfg.get("max_planning_attempts", 0) or 0)
    if limit <= 0:
        return True, 0
    current = int(state.get("planning_attempt_count", 0)) + 1
    state["planning_attempt_count"] = current
    return current <= limit, current
```

When budget exceeded:
- Failure class: `HUMAN_RETRY_REQUIRED`
- Failure code: `PLANNING_ATTEMPT_BUDGET_EXCEEDED`

## 6. Failure State Tracking

### 6.1 Job State Failure Fields

```python
# Current failure (last occurrence)
state["last_failure_class"]      # CONTROL_CLASSES value
state["last_failure_code"]       # Specific error code
state["last_failure_reason"]     # Human-readable message
state["last_failure_source"]     # FAILURE_SOURCES value
state["pending_intervention_for"] # Step requiring intervention

# Historical record
state["failure_history"] = [
    {
        "step": str,
        "failure_class": str,
        "failure_code": str,
        "failure_source": str,
        "timestamp": str,
    }
]

# Retry counters
state["reject_counts"]                # Total rejects by step
state["auto_retry_count_by_step"]      # Auto retries by step
state["human_retry_count_by_step"]    # Human retries by step
```

### 6.2 Retry History

```python
state["retry_history"] = [
    {
        "step": str,
        "attempted_at": str,
        "coder_used": str,
        "return_code": int | None,
        "result_status": str,
        "result_remark": str,
        "reject_code": str | None,
        "reject_type": str | None,  # failure_class for failures
        "failure_source": str | None,
    }
]
```

## 7. Common Failure Scenarios

### 7.1 Sidecar Failures

| Scenario | Cause | Diagnosis | Recovery |
|----------|-------|-----------|----------|
| Missing meta.json | Coder crashed or exited without writing sidecar | Check `raw_output.txt` and `stderr.txt` in step directory | Restart step; check coder health |
| Invalid JSON | Coder wrote malformed JSON | Check meta.json content for syntax errors | Fix coder JSON generation; retry |
| Missing recorded_at | Coder wrote incomplete sidecar | Check meta.json has all required fields | Ensure coder includes timestamp |
| Invalid status | Status not APPROVED/REJECTED | Check coder result status normalization | Update coder to output valid status |

### 7.2 Artifact Failures

| Scenario | Cause | Diagnosis | Recovery |
|----------|-------|-----------|----------|
| Artifact file missing | Coder claimed file in meta.json but didn't write it | Check meta.json artifacts vs actual files | Ensure coder writes files before sidecar |
| Unauthorized artifact | Step wrote artifact not in `produces` list | Check step config `produces` | Add artifact to `produces` or restrict coder |
| Path resolution failure | Artifact path cannot be resolved | Check path format and base directory | Use relative paths from project root |

### 7.3 Coder Invocation Failures

| Scenario | Cause | Diagnosis | Recovery |
|----------|-------|-----------|----------|
| Process timeout | Coder exceeded timeout seconds | Check `duration_ms` in usage | Increase timeout; optimize coder |
| Non-zero exit code | Coder process crashed | Check stderr.txt for stack traces | Fix coder bug; retry |
| Sidecar poll timeout | Coder running but no valid sidecar | Check sidecar validation logs | Debug coder sidecar writing |

### 7.4 Configuration Failures

| Scenario | Cause | Diagnosis | Recovery |
|----------|-------|-----------|----------|
| Unknown coder | Coder not in model_mapping.json | Check coder name in step config | Configure coder in model_mapping.json |
| Missing prompt file | Prompt template not found | Check prompt path resolution | Ensure prompt file exists in workflow bundle |
| Invalid step config | Step configuration malformed | Check step_cfg structure | Fix template_groups.py step definition |

## 8. Operational Troubleshooting Guide

### 8.1 Checking Job State

```bash
# View job state
cat ~/.ukbe-runner/jobs/<workflow>/<job_id>/job.json | jq .

# Check specific failure fields
cat ~/.ukbe-runner/jobs/<workflow>/<job_id>/job.json | jq '{status, last_failure_class, last_failure_code, last_failure_reason}'
```

### 8.2 Examining Step Outputs

```bash
# List step directories
ls -la ~/.ukbe-runner/jobs/<workflow>/<job_id>/

# Check step outputs
cat ~/.ukbe-runner/jobs/<workflow>/<job_id>/<step_dir>/raw_output.txt
cat ~/.ukbe-runner/jobs/<workflow>/<job_id>/<step_dir>/stderr.txt
cat ~/.ukbe-runner/jobs/<workflow>/<job_id>/<step_dir>/meta.json | jq .
```

### 8.3 Retry Commands

```bash
# Retry failed step
ukbe-run-agent run --workflow <workflow> --retry <job_id>

# Force approve (emergency only)
ukbe-run-agent approve --workflow <workflow> --job-id <job_id> --step <step>
```

### 8.4 Log Analysis

Key log locations:
- Step directory: `raw_output.txt`, `stderr.txt`, `usage.json`
- Job directory: `job.json`
- Runner logs: Console output from `run_agent.py`

Sidecar validation debug logs (when enabled):
- `[_is_valid_sidecar_json]` entries show validation progress
- Check mtime stability checks for file write races

## 9. Failure Code Reference

### 9.1 System Failure Codes

| Code | Class | Description |
|------|-------|-------------|
| `TRANSIENT_API_ERROR` | AUTO_RETRYABLE | Network/connection/temporary API failure |
| `ADAPTER_INVOCATION_FAILED` | HUMAN_RETRY_REQUIRED | Coder process failed to spawn or communicate |
| `META_JSON_MISSING` | HUMAN_RETRY_REQUIRED | Coder did not write required meta.json sidecar |
| `META_JSON_INVALID` | HUMAN_RETRY_REQUIRED | meta.json failed schema validation |
| `ARTIFACT_FILES_MISSING` | HUMAN_RETRY_REQUIRED | Referenced artifact files don't exist |
| `INVALID_RUNNER_CONFIGURATION` | HUMAN_RETRY_REQUIRED | Step or workflow configuration error |
| `UNKNOWN_CODER` | HUMAN_RETRY_REQUIRED | Coder not found in configuration |
| `PLANNING_ATTEMPT_BUDGET_EXCEEDED` | HUMAN_RETRY_REQUIRED | Max refinement/replan attempts exceeded |
| `UNEXPECTED_RUNNER_ERROR` | FATAL | Unhandled exception in runner |

### 9.2 Workflow-Specific Failure Codes

Defined in `template_groups.py` for each workflow:

| Workflow | Failure Code | Description |
|----------|--------------|-------------|
| master_docs_bootstrap_v1 | `MASTER_SYSTEM_DOC_REFINEMENT_EXHAUSTED` | Refinement loop exhausted for master docs |
| execution_scaffold_v1 | `SOP_REFINEMENT_EXHAUSTED` | SOP refinement exhausted |
| execution_scaffold_v1 | `TEMPLATE_REFINEMENT_EXHAUSTED` | Template refinement exhausted |
| execution_scaffold_v1 | `AGENT_REFINEMENT_EXHAUSTED` | Agent refinement exhausted |
| initiative_intake_v1 | `PRE_INIT_REFINEMENT_EXHAUSTED` | Pre-init refinement exhausted |
| delivery_planning_v1 | `PLAN_REFINEMENT_EXHAUSTED` | Plan refinement exhausted |
| delivery_planning_v1 | `TASK_GRAPH_REFINEMENT_EXHAUSTED` | Task graph refinement exhausted |
| task_execution_v1 | `TASK_REFINEMENT_EXHAUSTED` | Task refinement exhausted |
| task_execution_v1 | `IMPL_REFINEMENT_EXHAUSTED` | Implementation refinement exhausted |
| documentation_sync_v1 | `DOC_SYNC_REFINEMENT_EXHAUSTED` | Doc sync refinement exhausted |
| audience_doc_v1 | `STAKEHOLDER_REFINEMENT_EXHAUSTED` | Stakeholder doc refinement exhausted |
| audience_doc_v1 | `DEVELOPER_REFINEMENT_EXHAUSTED` | Developer doc refinement exhausted |
| audience_doc_v1 | `OPERATOR_REFINEMENT_EXHAUSTED` | Operator doc refinement exhausted |
| audience_doc_v1 | `TESTER_REFINEMENT_EXHAUSTED` | Tester doc refinement exhausted |
| audience_doc_v1 | `USER_REFINEMENT_EXHAUSTED` | User doc refinement exhausted |

## 10. Prevention Best Practices

### 10.1 For Workflow Authors

1. **Always declare produces**: Ensure `produces` list in step config matches artifacts written
2. **Set appropriate timeouts**: Configure `coder_timeout_seconds` based on expected duration
3. **Configure refinement limits**: Set `max_iterations` and `max_replans` to prevent infinite loops
4. **Use descriptive failure codes**: Custom failure codes aid debugging

### 10.2 For Coder Implementers

1. **Write sidecar last**: Ensure all artifacts are written before meta.json
2. **Validate before writing**: Check artifacts exist before claiming them in sidecar
3. **Use valid status**: Only write "APPROVED" or "REJECTED" (uppercase)
4. **Include timestamp**: Always set `recorded_at` in ISO format
5. **Handle timeouts**: Respect timeout and write sidecar promptly

### 10.3 For Operators

1. **Monitor auto-retries**: Repeated auto-retries indicate systemic issues
2. **Check step outputs**: Always review `raw_output.txt` and `stderr.txt`
3. **Preserve job state**: Don't delete job directories for failed runs
4. **Use force approve sparingly**: Only when coder result is acceptable despite REJECTED status

## 11. Related Documentation

- `docs/codebase/02_modules/agent-runner-v2-exceptions.md` — Exception module documentation
- `docs/codebase/02_modules/agent-runner-v2-step-runner.md` — Step execution documentation
- `docs/codebase/02_modules/agent-runner-v2-workflow-router.md` — Routing logic documentation
- `docs/codebase/02_modules/agent-runner-v2-job-state.md` — Job state management documentation
- `docs/codebase/02_modules/agent-runner-v2-coder-adapters.md` — Coder invocation documentation
