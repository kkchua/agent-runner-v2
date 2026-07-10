---
template_id: "CB-04-FM"
title: "Failure Modes Catalog - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04c_generate_failure_docs"
managed_by: workflow-generated
generated: "2026-07-10T10:10:12+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04c_generate_failure_docs`
> This file is workflow-generated and protected from manual edits.

# Failure Modes Catalog: agent-runner-v2

This document provides a comprehensive catalog of all error conditions, exception handling patterns, and recovery procedures in the agent-runner-v2 codebase.

## Table of Contents

1. [Exception Catalog](#exception-catalog)
2. [Failure Classification System](#failure-classification-system)
3. [Error Handling Patterns](#error-handling-patterns)
4. [Retry and Recovery Procedures](#retry-and-recovery-procedures)
5. [Operational Troubleshooting Guide](#operational-troubleshooting-guide)
6. [Common Failure Scenarios](#common-failure-scenarios)

---

## Exception Catalog

### Core Exception Types (exceptions.py)

| Exception | When Raised | Raised By | Handling | Recovery |
|-----------|-------------|-----------|----------|----------|
| `PreflightBlockedError` | Preflight check blocks step execution (e.g., artifact status not approved, missing dependencies) | `job_state.py` - various preflight validation functions | Caught in `run_agent.py`, routed to failure handling | Human intervention required - review preflight conditions |
| `MetaJsonMissingError` | Coder did not write expected meta.json sidecar after invocation | `step_runner.py` - `_read_and_validate_meta_json()` | Hard failure - no recovery, no disk fallback | Human retry required - check coder output and sidecar path |
| `MetaJsonInvalidError` | meta.json exists but fails schema validation (missing required fields, invalid JSON, wrong version) | `step_runner.py` - `_read_and_validate_meta_json()` | Hard failure with descriptive error message | Human retry required - validate sidecar schema |
| `ArtifactMissingError` | meta.json references artifact paths that don't exist on disk | `step_runner.py` - `_validate_artifact_files_exist()` | Hard failure with list of missing paths | Human retry required - verify artifact generation |

### Coder Adapter Exception (coder_adapters.py)

| Exception | When Raised | Raised By | Handling | Recovery |
|-----------|-------------|-----------|----------|----------|
| `CoderInvocationError` | Coder process failed (non-zero exit, timeout, API error) | `coder_adapters.py` - all `_invoke_*` functions | Caught in `run_agent.py`, routed to failure handling | Transient errors are auto-retryable; persistent errors require human intervention |

### Standard Library Exceptions Used

| Exception | Usage Context | Handling Pattern |
|-----------|---------------|------------------|
| `ValueError` | Configuration validation, parameter validation, preflight checks | Raised for invalid inputs; caught and classified in `classify_pre_run_failure()` |
| `FileNotFoundError` | Missing job files, missing artifact directories | Raised when required files don't exist; caught and converted to failure envelope |
| `RuntimeError` | Workflow module not loaded, backend request failures | Raised for unrecoverable runtime conditions |
| `subprocess.TimeoutExpired` | Coder subprocess timeout | Caught and wrapped in `CoderInvocationError` |
| `json.JSONDecodeError` | Invalid JSON in sidecar or job state | Caught and classified as `CORRUPTED_JOB_STATE` (FATAL) |

---

## Failure Classification System

### Control Classes (job_state.py)

The `CONTROL_CLASSES` constant defines three failure severity levels:

```python
CONTROL_CLASSES = {"AUTO_RETRYABLE", "HUMAN_RETRY_REQUIRED", "FATAL"}
```

| Class | Description | Auto-Retry | Human Intervention | Examples |
|-------|-------------|------------|-------------------|----------|
| `AUTO_RETRYABLE` | Transient errors that may succeed on retry | Yes | No | Network timeouts, rate limits, API temporary failures |
| `HUMAN_RETRY_REQUIRED` | Errors requiring human review before retry | No | Yes | Invalid sidecar, missing artifacts, configuration errors |
| `FATAL` | Errors that cannot be recovered | No | Terminal | Policy violations, out-of-scope requests, corrupted state |

### Failure Sources (job_state.py)

The `FAILURE_SOURCES` constant identifies where failures originate:

```python
FAILURE_SOURCES = {"runner", "adapter", "model", "validator"}
```

| Source | Description | Typical Failure Codes |
|--------|-------------|---------------------|
| `runner` | Core runner logic and orchestration | `INVALID_RUNNER_CONFIGURATION`, `UNKNOWN_CODER` |
| `adapter` | Coder adapter layer (Claude, Codex, Qwen) | `ADAPTER_INVOCATION_FAILED`, `TRANSIENT_API_ERROR` |
| `model` | LLM coder decisions and outputs | `MODEL_REJECTED`, various content errors |
| `validator` | Validation layer (meta.json, artifacts) | `META_JSON_MISSING`, `META_JSON_INVALID`, `ARTIFACT_MISSING` |

### Exception Classification Mapping

The `_classify_exception_v2()` function in `workflow_router.py` maps exceptions to failure classes:

| Exception | Failure Class | Failure Code | Failure Source |
|-----------|---------------|--------------|----------------|
| `CoderInvocationError` (transient) | `AUTO_RETRYABLE` | `TRANSIENT_API_ERROR` | `adapter` |
| `CoderInvocationError` (persistent) | `HUMAN_RETRY_REQUIRED` | `ADAPTER_INVOCATION_FAILED` | `adapter` |
| `MetaJsonMissingError` | `HUMAN_RETRY_REQUIRED` | `META_JSON_MISSING` | `validator` |
| `MetaJsonInvalidError` | `HUMAN_RETRY_REQUIRED` | `META_JSON_INVALID` | `validator` |
| `ArtifactMissingError` | `HUMAN_RETRY_REQUIRED` | `ARTIFACT_FILES_MISSING` | `validator` |
| Unknown exceptions | `FATAL` | `UNEXPECTED_RUNNER_ERROR` | `runner` |

### Transient Error Detection

The `_looks_like_transient_error()` function identifies auto-retryable conditions:

```python
def _looks_like_transient_error(message: str) -> bool:
    hints = (
        "connection error", "fetch failed", "timed out", "timeout", "temporar",
        "rate limit", "429", "service unavailable", "api error", "network error",
    )
    return any(hint in lowered for hint in hints)
```

---

## Error Handling Patterns

### Coder Step Execution Flow

```
run_step() in step_runner.py
├── invoke_coder() → May raise CoderInvocationError
├── _read_and_validate_meta_json() → May raise MetaJsonMissingError, MetaJsonInvalidError
├── _validate_artifact_files_exist() → May raise ArtifactMissingError
├── _validate_artifacts_in_produces_list() → May raise ArtifactMissingError (unauthorized)
└── Returns StepResult
```

### Action Step Execution Flow

```
run_action() in step_runner.py
├── execute_action() from runner_actions.py
├── _read_and_validate_meta_json() → May raise MetaJsonMissingError, MetaJsonInvalidError
├── _validate_artifact_files_exist() → May raise ArtifactMissingError
└── Returns StepResult
```

### Failure Routing Flow

```
Exception raised
├── Caught in run_agent.py main execution loop
├── classify_pre_run_failure() for pre-run failures
│   └── Returns failure envelope with class, code, source
└── route_after_failure() in workflow_router.py
    ├── _classify_exception_v2() maps exception to (class, code, source)
    ├── set_last_failure() records failure in job state
    ├── append_failure_history() adds to failure history
    └── Routes to:
        ├── AUTO_RETRYABLE → WAITING_FOR_AUTO_RETRY
        ├── HUMAN_RETRY_REQUIRED → WAITING_FOR_HUMAN_INTERVENTION
        └── FATAL → FAILED (terminal)
```

### Model Rejection Handling

When a step returns `REJECTED` status (not an exception):

```
route_after_step() in workflow_router.py
├── If on_reject_refine configured → _route_loop_or_replan()
│   ├── Loop iteration check
│   ├── Replan attempt check
│   └── Exhaustion → HUMAN_RETRY_REQUIRED
└── Otherwise → _classify_model_rejection()
    ├── Check reject_code against CONTROL_CLASSES
    ├── Check for transient error patterns
    └── Classify as AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, or FATAL
```

---

## Retry and Recovery Procedures

### Retry Counter Mechanics

Three retry counters are maintained per step in job state:

| Counter | Purpose | Increment Condition |
|---------|---------|---------------------|
| `reject_counts` | Total rejection count for a step | Every rejection or failure |
| `auto_retry_count_by_step` | Auto-retry specific count | Only for AUTO_RETRYABLE failures |
| `human_retry_count_by_step` | Human retry specific count | Only for HUMAN_RETRY_REQUIRED failures |

### Max Rejects Threshold

The `max_rejects` parameter (default from group config) determines when a step is considered failed:

```python
if failure_class == "FATAL" or current_count >= max_rejects:
    set_job_status(state, "FAILED")
    # Terminal state
```

### Recovery State Machine

```
IN_PROGRESS
├── Step completes APPROVED → advance to next step
├── Step returns REJECTED → evaluate retry/replan
│   ├── Loop iteration available → refine step
│   ├── Replan available → replan step
│   └── Exhausted → WAITING_FOR_HUMAN_INTERVENTION
└── Exception → route_after_failure()
    ├── AUTO_RETRYABLE → WAITING_FOR_AUTO_RETRY
    ├── HUMAN_RETRY_REQUIRED → WAITING_FOR_HUMAN_INTERVENTION
    └── FATAL → FAILED

WAITING_FOR_AUTO_RETRY
└── Automatic retry on next poll/execution

WAITING_FOR_HUMAN_INTERVENTION
└── Requires manual --approve-step or investigation

FAILED
└── Terminal - requires new job or manual recovery
```

### Preflight Blocked Recovery

When `PreflightBlockedError` is raised:

```python
# In run_agent.py
try:
    check_preflight_artifact_status(...)
except PreflightBlockedError as exc:
    envelope = classify_pre_run_failure(exc)
    # Record failure and route
    set_last_failure(...)
    append_failure_history(...)
```

Common preflight block conditions:
- `PREFLIGHT_STATUS_NOT_APPROVED`: Required artifact not in approved state
- `PREFLIGHT_ARTIFACT_MISSING`: Required artifact file not found
- `PREFLIGHT_TASK_QUEUE_EXHAUSTED`: Task generation queue exhausted

---

## Operational Troubleshooting Guide

### Diagnosing Failures

1. **Check job.json status:**
   ```bash
   ukbe-run-agent run --template-group <group> --job-id <id> --check-job-status
   ```

2. **Review last failure fields:**
   - `last_failure_class`: AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, FATAL
   - `last_failure_code`: Specific error code
   - `last_failure_reason`: Human-readable description
   - `last_failure_source`: runner, adapter, model, validator

3. **Examine failure_history:**
   ```json
   {
     "step": "step_name",
     "failure_class": "HUMAN_RETRY_REQUIRED",
     "failure_code": "META_JSON_MISSING",
     "failure_source": "validator",
     "timestamp": "2026-07-10T10:10:12"
   }
   ```

### Common Error Codes and Resolution

| Error Code | Meaning | Resolution |
|------------|---------|------------|
| `META_JSON_MISSING` | Coder didn't write sidecar | Check coder logs, verify prompt instructions |
| `META_JSON_INVALID` | Sidecar schema invalid | Validate JSON structure, check required fields |
| `ARTIFACT_MISSING` | Referenced files don't exist | Verify artifact generation, check paths |
| `ADAPTER_INVOCATION_FAILED` | Coder process failed | Check API keys, network, coder configuration |
| `TRANSIENT_API_ERROR` | Temporary API failure | Auto-retry will handle; check rate limits |
| `PREFLIGHT_STATUS_NOT_APPROVED` | Required artifact not approved | Approve prerequisite steps first |
| `PLANNING_ATTEMPT_BUDGET_EXCEEDED` | Max planning attempts reached | Review planning loop configuration |
| `REFINEMENT_EXHAUSTED` | Max refinement iterations reached | Review coder output quality, adjust thresholds |

### Notification on Failure

The runner sends notifications for failure events:

```python
# workflow_router.py
send_workflow_notification("FAILED", dict(state))  # Terminal failures
send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(state))  # Intervention required
send_step_notification("STEP_FAILED", state, step, step_cfg)  # Step-specific failures
```

### Recovery Commands

```bash
# Force approve a stuck step
ukbe-run-agent run --template-group <group> --job-id <id> --approve-step <step>

# Force approve regardless of review decision
ukbe-run-agent run --template-group <group> --job-id <id> --force-approve-step <step>

# Reapply routing logic
ukbe-run-agent run --template-group <group> --job-id <id> --reapply-routing

# Override current step
ukbe-run-agent run --template-group <group> --job-id <id> --override-step <step>
```

---

## Common Failure Scenarios

### Scenario 1: Sidecar Not Written

**Symptoms:**
- `MetaJsonMissingError` raised
- `failure_code`: `META_JSON_MISSING`

**Causes:**
- Coder didn't understand sidecar requirement
- Coder process crashed before writing
- Wrong path calculation

**Resolution:**
1. Check step directory for any output files
2. Review coder logs in `raw_output.txt` and `stderr.txt`
3. Verify prompt includes sidecar instruction template
4. Retry with corrected prompt

### Scenario 2: Artifact Files Missing

**Symptoms:**
- `ArtifactMissingError` raised
- List of missing paths in error message

**Causes:**
- Coder claimed artifacts it didn't create
- Path resolution error
- File write failed silently

**Resolution:**
1. Check step directory for actual files created
2. Verify `produces` list in step configuration
3. Check for path construction errors
4. Retry with corrected artifact paths

### Scenario 3: Coder Timeout

**Symptoms:**
- `CoderInvocationError` with timeout message
- `failure_code`: `TRANSIENT_API_ERROR` (if transient) or `ADAPTER_INVOCATION_FAILED`

**Causes:**
- Network latency
- API rate limiting
- Complex operation taking too long

**Resolution:**
1. Check `AGENT_RUNNER_CODER_TIMEOUT_SECONDS` environment variable
2. Review global config.json for `coder_timeout_seconds`
3. For persistent timeouts, consider increasing timeout or breaking step into smaller steps

### Scenario 4: Model Rejection Loop

**Symptoms:**
- Repeated REJECTED status
- `reject_counts` incrementing
- Loop/replan exhaustion

**Causes:**
- Coder consistently producing inadequate output
- Review criteria too strict
- Template conformance issues

**Resolution:**
1. Review `REVIEW_FILE` for specific issues
2. Check `loop_history` and `replan_history` for patterns
3. Adjust `max_iterations` or `max_replans` if needed
4. Force approve or manual intervention if coder is stuck

### Scenario 5: Preflight Block on Missing Artifact

**Symptoms:**
- `PreflightBlockedError` with `PREFLIGHT_ARTIFACT_MISSING`
- Step won't start

**Causes:**
- Previous step didn't produce required artifact
- Artifact was deleted
- Wrong artifact key in configuration

**Resolution:**
1. Verify prerequisite step completed successfully
2. Check artifact paths in job state
3. Re-run prerequisite step if needed
4. Force approve with `--force-approve-step` if artifact exists but not detected

---

## Related Documentation

- [SYSTEM_OVERVIEW.md](../00_governance/bootstrap/SYSTEM_OVERVIEW.md) - System architecture
- [RUNBOOK.md](../00_governance/bootstrap/RUNBOOK.md) - Operational procedures
- [COMPONENT_ARCHITECTURE.md](../00_governance/bootstrap/COMPONENT_ARCHITECTURE.md) - Component details
- [PROJECT_ANALYSIS.md](../00_governance/bootstrap/PROJECT_ANALYSIS.md) - Project context

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04c_generate_failure_docs` on 2026-07-10T10:10:12+08:00*
