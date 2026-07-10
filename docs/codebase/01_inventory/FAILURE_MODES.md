---
template_id: "CB-04-FM"
title: "Failure Modes and Error Handling"
status: "active"
generated: "2026-07-10T14:52:31+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04c_generate_failure_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04c_generate_failure_docs`
> This file is workflow-generated and protected from manual edits.

# Failure Modes and Error Handling

This document catalogs all error conditions, exception handling patterns, and recovery procedures in the agent-runner-v2 codebase.

## 1. Exception Catalog

### 1.1 Core Runner Exceptions

| Exception | Module | When Raised | Raised By | Handling | Recovery |
|-----------|--------|-------------|-----------|----------|----------|
| `PreflightBlockedError` | `exceptions.py` | Pre-flight check blocks step execution (e.g., artifact status not approved, missing input artifacts) | `job_state.py` - `check_preflight_artifact_status()`, `enforce_retry_limit_before_run()` | Caught in `run_agent.py` main execution loop | Human intervention required; use `--reapply-routing` after resolving blockers |
| `MetaJsonMissingError` | `exceptions.py` | Coder did not write expected `meta.json` sidecar after invocation | `step_runner.py` - `_read_and_validate_meta_json()` | Routed via `route_after_failure()` in `workflow_router.py` | Hard failure - requires human investigation of coder process |
| `MetaJsonInvalidError` | `exceptions.py` | `meta.json` exists but fails schema validation (missing required fields, invalid version, malformed JSON) | `step_runner.py` - `_read_and_validate_meta_json()` | Routed via `route_after_failure()`; auto-repair attempted via `_repair_or_validate_meta_json()` | If auto-repair fails, human intervention required |
| `ArtifactMissingError` | `exceptions.py` | `coder_result.artifacts` references paths that don't exist on disk | `step_runner.py` - `_validate_artifact_files_exist()`, `_validate_artifacts_in_produces_list()` | Routed via `route_after_failure()` | Verify artifact paths and retry; check for filesystem issues |
| `CoderInvocationError` | `coder_adapters.py` | Coder process failed (non-zero exit code, timeout, API error) | `coder_adapters.py` - `_invoke_codex()`, `_invoke_claude()`, `_invoke_qwen()`, `_invoke_plain()` | Routed via `route_after_failure()` | Retry for transient errors; human intervention for persistent failures |

### 1.2 Exception Class Definitions

```python
# From exceptions.py

class PreflightBlockedError(Exception):
    """Raised when a preflight check blocks step execution (e.g. artifact status not approved)."""

class MetaJsonMissingError(Exception):
    """Raised when the coder did not write the expected meta.json sidecar after invocation.
    
    In v2 this is a hard failure — no recovery, no disk fallback.
    """

class MetaJsonInvalidError(Exception):
    """Raised when meta.json exists but fails schema validation.
    
    Includes a human-readable reason explaining exactly what is wrong.
    """

class ArtifactMissingError(Exception):
    """Raised when coder_result.artifacts references paths that don't exist on disk.
    
    Contains a list of missing paths for diagnostic output.
    """
    def __init__(self, message: str, missing: list[str]) -> None:
        super().__init__(message)
        self.missing = missing

# From coder_adapters.py

@dataclass
class CoderInvocationError(Exception):
    """Raised when coder subprocess invocation fails."""
    message: str
    command: list[str]
    return_code: int
    stdout: str
    stderr: str
    raw_events: list[str]
```

## 2. Failure Classification System

The runner uses a three-tier classification system for all failures:

### 2.1 Control Classes

| Class | Description | Action | Examples |
|-------|-------------|--------|----------|
| `AUTO_RETRYABLE` | Transient failures that may succeed on retry | Increment retry counter, status → `WAITING_FOR_AUTO_RETRY` | Network timeout, rate limit (429), temporary API unavailability |
| `HUMAN_RETRY_REQUIRED` | Failures requiring human intervention before retry | Increment retry counter, status → `WAITING_FOR_HUMAN_INTERVENTION` | Invalid configuration, missing artifacts, schema violations, permission errors |
| `FATAL` | Non-recoverable failures that should not be retried | Immediate failure, status → `FAILED` | Out-of-scope requests, policy violations, unrecoverable errors |

### 2.2 Failure Sources

| Source | Description |
|--------|-------------|
| `runner` | Failure originated in runner code (configuration, validation, routing) |
| `adapter` | Failure in coder adapter layer (invocation, process management) |
| `model` | Failure from LLM response (rejection, invalid output) |
| `validator` | Failure in post-invocation validation (meta.json schema, artifact checks) |

### 2.3 Classification Logic

```python
# From workflow_router.py _classify_exception_v2()

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

### 2.4 Transient Error Detection

```python
# From workflow_router.py _looks_like_transient_error()

def _looks_like_transient_error(message: str) -> bool:
    lowered = message.lower()
    hints = (
        "connection error", "fetch failed", "timed out", "timeout", "temporar",
        "rate limit", "429", "service unavailable", "api error", "network error",
    )
    return any(hint in lowered for hint in hints)
```

## 3. Error Handling Patterns by Step Type

### 3.1 Coder Steps

For steps invoking LLM backends (Claude, Codex, Qwen):

```
┌─────────────────┐
│   Invoke Coder  │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Success?  │
    └────┬────┘
   ┌─────┴─────┐
   │           │
  No         Yes
   │           │
┌──┴──┐    ┌───┴─────────┐
│Throw│    │ Read meta.json│
│Coder│    └──────┬────────┘
│Error│           │
└─────┘      ┌────┴────┐
             │ Valid?  │
             └────┬────┘
           ┌─────┴─────┐
           │           │
          No         Yes
           │           │
      ┌────┴────┐  ┌───┴──────────┐
      │Throw    │  │Validate      │
      │MetaJson │  │Artifact Files│
      │Invalid  │  └──────┬───────┘
      └─────────┘         │
                     ┌────┴────┐
                     │ Exist?  │
                     └────┬────┘
                   ┌─────┴─────┐
                   │           │
                  No         Yes
                   │           │
              ┌────┴───┐   ┌───┴─────────┐
              │ Throw  │   │ Route After │
              │Artifact│   │   Step      │
              │Missing │   │   (Success) │
              └────────┘   └─────────────┘
```

### 3.2 Action Steps

For deterministic runner actions:

```
┌─────────────────────┐
│ Execute Action      │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │ Success?│
      └────┬────┘
    ┌──────┴──────┐
    │             │
   No           Yes
    │             │
┌───┴─────────┐ ┌┴──────────────┐
│ Exception     │ │ Validate      │
│ propagates to │ │ meta.json     │
│ route_after_  │ └───────┬───────┘
│ failure()     │         │
└───────────────┘   ┌─────┴──────┐
                    │ Route After│
                    │ Step       │
                    └────────────┘
```

### 3.3 Review Steps

For steps with human approval gates:

```
┌─────────────────────┐
│ Review Decision     │
│ (coder_result.status)│
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │   Status    │
    └──────┬──────┘
  ┌────────┼────────┐
  │        │        │
APPROVED REJECTED  FAILED
  │        │        │
  │    ┌───┴───┐   │
  │    │Check  │   │
  │    │on_reject│  │
  │    │_refine │  │
  │    └───┬───┘   │
  │   ┌────┴────┐   │
  │   │ Config? │   │
  │   └────┬────┘   │
  │   ┌────┴────┐   │
  │   │         │   │
  │  Yes       No   │
  │   │         │   │
  │   ▼         ▼   │
  │ Trigger   Route │
  │ Loop/Replan     │
  │                 │
  │            ┌────┴────┐
  │            │Classify │
  │            │Rejection│
  │            └────┬────┘
  │                 ▼
  │         Increment Retry
  │                 │
  │            ┌────┴────┐
  │            │Max      │
  │            │Reached?  │
  │            └────┬────┘
  │         ┌──────┴──────┐
  │         │             │
  │        Yes            No
  │         │             │
  │         ▼             ▼
  │      FAILED      WAITING_FOR_
  │                  AUTO_RETRY/
  │                  HUMAN_INTERVENTION
  │
  ▼
Advance Step
```

## 4. Retry and Recovery Procedures

### 4.1 Automatic Retry

**Trigger Conditions:**
- Failure class = `AUTO_RETRYABLE`
- Retry count < `max_rejects` (default: 0, configurable per workflow)
- Non-terminal job status

**Process:**
1. Set job status to `WAITING_FOR_AUTO_RETRY`
2. Increment `auto_retry_count_by_step[step]`
3. Save job state
4. On next execution, retry the failed step

**Transient Error Patterns:**
- Connection errors
- Timeout errors
- Rate limit (429)
- Service unavailable
- Temporary API errors

### 4.2 Human Intervention Retry

**Trigger Conditions:**
- Failure class = `HUMAN_RETRY_REQUIRED`
- Retry count < `max_rejects`
- Or configuration error requiring fix

**Process:**
1. Set job status to `WAITING_FOR_HUMAN_INTERVENTION`
2. Set `pending_intervention_for` to failed step
3. Increment `human_retry_count_by_step[step]`
4. Save job state
5. Send notification (if configured)
6. Wait for human resolution

**Recovery Actions:**
```bash
# Check job status
ukbe-run-agent run --template-group <workflow> --job-id <id> --check-job-status

# Reapply routing after fixing issues
ukbe-run-agent run --template-group <workflow> --job-id <id> --reapply-routing

# Force step retry with override
ukbe-run-agent run --template-group <workflow> --job-id <id> --override-step <step>
```

### 4.3 Replan and Refine Loops

For steps with `on_reject_refine` configuration:

```python
# Loop mechanics
on_reject_refine = {
    "step": "refine_step_name",      # Step to run for refinement
    "artifact": "ARTIFACT_KEY",       # Target artifact to refine
    "max_iterations": 2,              # Max refine iterations
    "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
    "exhausted_failure_code": "REFINEMENT_EXHAUSTED"
}

# Replan mechanics (after loop exhaustion)
on_exhaust_replan = {
    "step": "replan_step_name",       # Step to run for replanning
    "artifact": "ARTIFACT_KEY",       # Target artifact to replan
    "max_replans": 2,                 # Max replan attempts
    "terminal_failure_code": "REPLAN_EXHAUSTED"
}
```

**Loop Execution:**
1. Review step returns `REJECTED` with `reject_code`
2. Match `reject_code` to `reject_code_routes` or use `on_reject_refine`
3. Activate `loop_context` with iteration counter
4. Run refine step
5. If approved → return to review step
6. If rejected → increment iteration
7. If `max_iterations` exceeded → trigger replan or fail

### 4.4 Planning Attempt Budget

For recovery operations (replan/refine):

```python
# From workflow_router.py

def _consume_planning_attempt_budget(*, state: dict, group_cfg: dict) -> tuple[bool, int]:
    limit = int(group_cfg.get("max_planning_attempts", 0) or 0)
    if limit <= 0:
        return True, 0  # No limit
    current = int(state.get("planning_attempt_count", 0)) + 1
    state["planning_attempt_count"] = current
    return current <= limit, current
```

If budget exceeded → `HUMAN_RETRY_REQUIRED` with code `PLANNING_ATTEMPT_BUDGET_EXCEEDED`

## 5. Failure History and Diagnostics

### 5.1 Job State Failure Tracking

```python
# Tracked in job.json
{
  "last_failure_class": "HUMAN_RETRY_REQUIRED",
  "last_failure_code": "ARTIFACT_FILES_MISSING",
  "last_failure_reason": "Artifact files claimed in meta.json do not exist: [...]",
  "last_failure_source": "validator",
  "pending_intervention_for": "step_name",
  "failure_history": [
    {
      "step": "step_name",
      "failure_class": "AUTO_RETRYABLE",
      "failure_code": "TRANSIENT_API_ERROR",
      "failure_source": "adapter",
      "timestamp": "2026-07-10T14:30:00"
    }
  ],
  "retry_history": [
    {
      "step": "step_name",
      "attempted_at": "2026-07-10T14:25:00",
      "coder_used": "claude",
      "return_code": 1,
      "result_status": "FAILED_BEFORE_RESULT",
      "result_remark": "Connection timeout",
      "reject_type": "AUTO_RETRYABLE",
      "reject_code": "TRANSIENT_API_ERROR",
      "failure_source": "adapter"
    }
  ],
  "auto_retry_count_by_step": {"step_name": 1},
  "human_retry_count_by_step": {"step_name": 2},
  "reject_counts": {"step_name": 3}
}
```

### 5.2 Step Directory Debug Artifacts

On failure, the runner saves debug information to the step directory:

```
<job_dir>/
├── <step_idx>_<step_name>/
│   ├── raw_output.txt           # Raw coder stdout
│   ├── stderr.txt               # Coder stderr (if any)
│   ├── usage.json               # Token/cost usage data
│   ├── step_manifest.json       # Invocation metadata
│   ├── raw_events.jsonl         # Structured event stream
│   └── debug_failure.json       # Detailed failure info (on exception)
```

## 6. Operational Troubleshooting Guide

### 6.1 Common Failure Scenarios

#### Scenario 1: Meta.json Missing

**Symptoms:**
- Error: `Coder did not write meta.json to expected path: <path>`
- Status: `WAITING_FOR_HUMAN_INTERVENTION`
- `last_failure_code`: `META_JSON_MISSING`

**Diagnosis:**
1. Check if coder process completed: review `raw_output.txt` and `stderr.txt`
2. Check for sidecar write permissions
3. Verify coder didn't crash before writing sidecar

**Resolution:**
- If coder crashed: investigate root cause in stderr
- If permission issue: fix filesystem permissions
- If logic error: fix and retry with `--reapply-routing`

#### Scenario 2: Artifact Files Missing

**Symptoms:**
- Error: `Artifact files claimed in meta.json do not exist: [...]`
- Status: `WAITING_FOR_HUMAN_INTERVENTION`
- `last_failure_code`: `ARTIFACT_FILES_MISSING`

**Diagnosis:**
1. Check if files exist at claimed paths
2. Review `meta.json` for artifact declarations
3. Check for path case sensitivity issues (Windows)

**Resolution:**
- If files exist but at different path: fix path in code
- If files truly missing: coder failed to write; investigate coder output
- Re-run step after fix

#### Scenario 3: Meta.json Invalid Schema

**Symptoms:**
- Error: `meta.json at <path> has unrecognised version: ...`
- Status: `WAITING_FOR_HUMAN_INTERVENTION`
- `last_failure_code`: `META_JSON_INVALID`

**Diagnosis:**
1. Review `meta.json` content
2. Check `schema_version` field (should be "v2")
3. Verify required fields: `coder_result.status`, `coder_result.artifacts`, `coder_result.recorded_at`

**Resolution:**
- If legacy format: runner attempts auto-repair
- If malformed: fix coder to output correct schema
- Manual fix: edit `meta.json` to valid schema and retry

#### Scenario 4: Coder Timeout

**Symptoms:**
- Error: `Coder subprocess timed out after <seconds> seconds.`
- Status: `WAITING_FOR_AUTO_RETRY` (if transient) or `WAITING_FOR_HUMAN_INTERVENTION`
- `last_failure_code`: `TRANSIENT_API_ERROR` or `ADAPTER_INVOCATION_FAILED`

**Diagnosis:**
1. Check step complexity vs timeout (default: 600s)
2. Review `raw_output.txt` for partial progress
3. Check API status for provider outages

**Resolution:**
- Increase timeout: set `coder_timeout_seconds` in config.json
- Or set step-level: `coder_timeout_seconds` in step config
- Or use environment: `AGENT_RUNNER_CODER_TIMEOUT_SECONDS`

#### Scenario 5: Preflight Block - Missing Input

**Symptoms:**
- Error: `Missing required input artifact(s): [...]`
- Status: `WAITING_FOR_HUMAN_INTERVENTION`
- `last_failure_code`: `PREFLIGHT_BLOCKED`

**Diagnosis:**
1. Check upstream step completion status
2. Verify artifact promotion (if cross-workflow)
3. Review `reference_artifacts` in step config

**Resolution:**
- Complete upstream workflow steps
- Promote artifacts if needed
- Seed artifacts with `--set KEY=PATH` if bootstrapping

#### Scenario 6: Max Rejects Exceeded

**Symptoms:**
- Status: `FAILED`
- Step in `failed_steps` list
- `reject_counts[step]` >= `max_rejects`

**Diagnosis:**
1. Review `failure_history` for repeated failures
2. Check if issue is persistent (not transient)
3. Review `retry_history` for patterns

**Resolution:**
- Start new job with fixed parameters
- Or increase `max_rejects` in workflow config
- Or bypass with `--force-approve-step` (emergency only)

### 6.2 Recovery Commands Reference

| Command | Purpose |
|---------|---------|
| `--check-job-status` | Display formatted job status summary |
| `--reapply-routing` | Re-run routing logic after intervention |
| `--override-step <step>` | Force current_step to specific step |
| `--approve-step <step>` | Record human approval for pending step |
| `--force-approve-step <step>` | Emergency force-approve regardless of review |
| `--show-job` | Print full job.json for inspection |

### 6.3 Notification Configuration

Failures trigger notifications based on step configuration:

```python
# Step-level notification config
step_cfg = {
    "enable_notifications": True,
    "notify_on": ["STEP_FAILED", "STEP_REJECTED"]
}

# Workflow-level notification
send_workflow_notification("FAILED", state)
send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", state)
```

## 7. Exit Codes

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Continue to next step or complete |
| 1 | Intervention Required | Status set to waiting state; human action needed |
| 2 | Fatal Failure | Status set to `FAILED`; workflow terminates |
| 124 | Timeout (coder) | Coder process exceeded timeout |
| Non-zero | Error | Check logs for details |

## 8. Prevention and Best Practices

### 8.1 For Workflow Authors

1. **Set appropriate timeouts**: Configure `coder_timeout_seconds` based on step complexity
2. **Declare produces/updates**: Always declare `produces` and `updates` in step config
3. **Use reject_code_routes**: Provide specific recovery paths for known rejection types
4. **Set max_planning_attempts**: Limit recovery loops to prevent runaway execution

### 8.2 For Operators

1. **Monitor failure_history**: Watch for repeated patterns
2. **Check debug artifacts**: Review `raw_output.txt` and `stderr.txt` on failures
3. **Use --check-job-status**: Get quick status overview before intervening
4. **Set up notifications**: Configure Pushover for real-time alerts

### 8.3 For Coder Implementations

1. **Always write meta.json**: Even on failure, write sidecar with REJECTED status
2. **Verify artifacts before APPROVED**: Check files exist before reporting success
3. **Use correct schema_version**: Set to "v2" for v2 runner compatibility
4. **Include recorded_at**: ISO timestamp required for validation

## 9. Related Documentation

- `step_runner.py` - Step execution and validation
- `workflow_router.py` - Post-step routing and failure classification
- `job_state.py` - Job state management and failure tracking
- `coder_adapters.py` - Coder invocation and error handling
- `exceptions.py` - Exception class definitions
- `RUNBOOK.md` - Operational procedures
