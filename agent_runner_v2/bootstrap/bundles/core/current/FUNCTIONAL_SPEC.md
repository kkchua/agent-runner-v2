---
template_id: "SYS-00-FS"
title: "Functional Specification"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification

## System Purpose

`agent-runner-v2` provides a runtime environment for executing structured LLM workflows with deterministic routing, artifact validation, and multi-provider LLM support.

## Functional Capabilities

### FC-1: Workflow Execution

**Description**: Execute multi-step workflows defined in template groups.

**Inputs**:
- Workflow name (template group)
- Initial artifact values
- Optional job ID for resumption

**Outputs**:
- Updated job state
- Generated artifacts
- Execution logs

**Behaviors**:
- Load workflow definition from runtime bundle
- Execute steps sequentially
- Validate artifacts after each step
- Route to next step based on result

### FC-2: Prompt Rendering

**Description**: Render step prompts with template substitution.

**Inputs**:
- Prompt template path
- Context variables (artifacts, state)

**Outputs**:
- Rendered prompt text
- Prompt checksum

**Behaviors**:
- Load template from workflow bundle
- Substitute variable references
- Compute checksum for caching
- Support literal aliases for common paths

### FC-3: Coder Invocation

**Description**: Invoke LLM providers with adapter pattern.

**Supported Providers**:
| Provider | Adapter | Models |
|----------|---------|--------|
| Claude | `coder_adapters.py` | claude-sonnet-4, claude-opus-4 |
| Codex | `coder_adapters.py` | codex-mini, codex-latest |
| Qwen | `coder_adapters.py` | qwen-coder |

**Inputs**:
- Provider/model selection
- Rendered prompt
- Timeout configuration

**Outputs**:
- LLM response
- Usage data (tokens, duration)

### FC-4: Meta.json Processing

**Description**: Parse and validate step results from `meta.json` sidecar.

**Schema** (v2):
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED | REJECTED",
    "remark": "<summary>",
    "artifacts": {"<key>": "<path>"},
    "recorded_at": "ISO8601"
  }
}
```

**Behaviors**:
- Validate schema version
- Extract status, remark, artifacts
- Verify artifact file existence
- Enrich with usage data

### FC-5: Routing

**Description**: Route job state after step completion.

**Routes**:
| Result | Action | Exit Code |
|--------|--------|-----------|
| APPROVED | Advance step, update artifacts | 0 |
| REJECTED | Check review/refine config, loop or advance | 0 or 1 |
| Failure | Classify, retry or escalate | 1 or 2 |

**Review/Refine Loops**:
- Configured via `on_reject_refine`
- Track iteration count
- Max iterations triggers replan or human intervention

### FC-6: Job State Management

**Description**: Persist and manage job execution state.

**State Elements**:
- `completed_steps`: List of finished steps
- `failed_steps`: List of failed steps
- `artifacts`: Map of artifact keys to paths
- `reject_counts`: Per-step rejection tracking
- `retry_history`: Execution attempts
- `review_state`: Current review decisions

**Behaviors**:
- Load existing job or create new
- Save after each step
- Support job resumption
- Migrate legacy formats

### FC-7: Artifact Validation

**Description**: Validate artifact existence and conformance.

**Checks**:
- File existence for declared artifacts
- Path format validation
- Protected document guards
- Template conformance (for generated docs)

### FC-8: Daemon Operation

**Description**: Run workstation as supervised worker node.

**Behaviors**:
- Claim work from backend
- Spawn child processes for steps
- Track child state
- Emit heartbeats
- Handle graceful shutdown

### FC-9: Backend Integration

**Description**: Connect to external backend for distributed execution.

**Behaviors**:
- Poll for available work
- Submit step results
- Report worker status
- Handle authentication

### FC-10: Runner Actions

**Description**: Execute deterministic actions (non-LLM steps).

**Action Types**:
| Action | Purpose |
|--------|---------|
| `copy_artifact` | File copying |
| `prepare_delivery_scaffold` | Scaffold generation |
| `scan_repo_codebase` | Repository analysis |
| `sync_codebase_docs` | Doc synchronization |
| `validate_codebase_docs` | Doc validation |
| `finalize_bootstrap` | Bootstrap completion |

## Actors

### Actor: Developer

**Description**: Local workflow execution and development.

**Goals**:
- Run workflows locally
- Debug step failures
- Inspect job state
- Test workflow changes

**Interactions**:
- `ukbe-run-agent run`: Execute workflow
- `ukbe-run-agent show-job`: Inspect state
- `ukbe-run-agent retry`: Retry failed steps

### Actor: Operator

**Description**: Production worker operation and monitoring.

**Goals**:
- Maintain worker availability
- Monitor execution health
- Handle escalations
- Manage daemon lifecycle

**Interactions**:
- `ukbe-run-agent worker`: Worker loop
- `ukbe-run-agent daemon`: Daemon supervision
- Log monitoring

### Actor: Workflow Author

**Description**: Creates and maintains workflow definitions.

**Goals**:
- Define workflow steps
- Author prompt templates
- Configure routing
- Test workflows

**Interactions**:
- Edit `template_groups.py`
- Edit `prompts/*.txt`
- Test with `ukbe-run-agent run`

### Actor: Backend System

**Description**: External system that assigns and tracks work.

**Goals**:
- Distribute work to workers
- Collect step results
- Track job progress

**Interactions**:
- REST API for work claiming
- REST API for result submission

## Core Behaviors

### Behavior: Step Execution Loop

```
WHILE step_remaining:
    1. LOAD step configuration
    2. RENDER prompt with context
    3. INVOKE coder or action
    4. READ meta.json sidecar
    5. VALIDATE artifacts
    6. ROUTE based on result
    7. SAVE job state
```

### Behavior: Review/Refine Cycle

```
ON step_result.status == REJECTED:
    IF on_reject_refine configured:
        IF iteration < max_iterations:
            1. INCREMENT iteration counter
            2. RENDER refine prompt
            3. INVOKE coder
            4. RETURN to validation
        ELSE:
            1. TRIGGER replan or human intervention
    ELSE:
        1. ADVANCE to next step (rejection recorded)
```

### Behavior: Failure Recovery

```
ON exception:
    1. CLASSIFY exception type
    2. IF AUTO_RETRYABLE:
         a. INCREMENT retry counter
         b. IF retries < max:
              RETRY step
         c. ELSE:
              ESCALATE to human
    3. IF HUMAN_RETRY_REQUIRED:
         a. SET status WAITING_FOR_HUMAN_APPROVAL
         b. EXIT for intervention
    4. IF FATAL:
         a. SET job status FAILED
         b. EXIT with error
```

### Behavior: Daemon Work Claiming

```
WHILE daemon_running:
    1. POLL backend for available work
    2. IF work available:
         a. CLAIM work item
         b. SPAWN execute-step child process
         c. MONITOR child execution
         d. SUBMIT result on completion
    3. ELSE:
         a. SLEEP for poll interval
    4. EMIT heartbeat
```

## Functional Constraints

| Constraint | Description |
|------------|-------------|
| Sidecar-only | `meta.json` is only structured output channel |
| No markdown write-backs | Runner never modifies markdown files |
| Explicit routing | All paths must be explicitly defined |
| Hard failures | Invalid sidecar causes immediate failure |
| Artifact existence | Declared artifacts must exist after step |

---

*This functional specification defines the behaviors of agent-runner-v2. See `SYSTEM_OVERVIEW.md` for high-level context and `NON_FUNCTIONAL_REQUIREMENTS.md` for quality attributes.*
