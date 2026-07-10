---
template_id: "SYS-00-FS"
title: "Functional Specification"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:43:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification

## Purpose

This document describes the functional capabilities of `agent-runner-v2`—what the system does, how it behaves, and the major features available to users and developers.

## System Purpose

`agent-runner-v2` is a workflow orchestration engine that executes structured multi-step workflows using LLM models and deterministic actions. It provides:

- **Workflow execution**: Step-by-step execution with routing
- **Quality control**: Review loops and approval gates
- **Resilience**: Retry logic and failure handling
- **Observability**: Execution history and artifact tracking

## Functional Capabilities

### 1. Workflow Execution

#### 1.1 Step Execution

**Function**: Execute a single workflow step

**Inputs**:
- Workflow name
- Step name
- Job state
- Configuration

**Outputs**:
- Step result (APPROVED/REJECTED)
- Generated artifacts
- Updated job state

**Behavior**:
1. Load workflow bundle from runtime
2. Render prompt template with context
3. Invoke coder (LLM) or action (Python)
4. Read meta.json sidecar
5. Validate artifacts
6. Return result

#### 1.2 Workflow Routing

**Function**: Route to next step based on result

**Inputs**:
- Current step result
- Job state
- Workflow configuration

**Outputs**:
- Next step name
- Updated job state
- Exit code

**Behavior**:
- APPROVED → Next step
- REJECTED → Refine or retry
- Failure → Failure handling

### 2. Coder Invocation

#### 2.1 Model Resolution

**Function**: Resolve model alias to actual model

**Aliases**:
| Alias | Model |
|-------|-------|
| default | claude-opus-4 |
| fast | claude-sonnet-4 |
| code | codex |
| local | qwen |

#### 2.2 Multi-Model Support

**Function**: Invoke different models with same interface

**Adapters**:
- `claude_adapter.py`: Claude API
- `codex_adapter.py`: OpenAI Codex
- `qwen_adapter.py`: Local Qwen

**Common Interface**:
```python
def invoke_coder(prompt: str, model: str, timeout: int) -> CoderResult
```

### 3. Artifact Management

#### 3.1 Path Resolution

**Function**: Resolve artifact keys to paths

**Constants**:
- `ARTIFACT_KEY_*`: Artifact identifiers
- `ARTIFACT_PATH_*`: Pre-computed paths
- `FOLDER_KEY_*`: Directory constants

**Resolution**:
```python
path = artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
```

#### 3.2 Validation

**Function**: Validate artifact existence and content

**Checks**:
- File exists
- Frontmatter valid
- Required sections present
- Cross-references resolve

#### 3.3 Protection

**Function**: Protect documents from unauthorized writes

**Rules**:
- Can write only if in `produces` list
- Workflow-scoped protection
- Step-scoped overrides

### 4. Review and Refine

#### 4.1 Review Cycle

**Function**: Review generated artifacts

**Flow**:
```
Generate → Review → Decision
              ↓
       (Approve / Reject)
              ↓
    (Continue / Refine)
```

**Decision Criteria**:
- Content quality
- Standards compliance
- Completeness

#### 4.2 Refine Loop

**Function**: Refine artifacts based on feedback

**Behavior**:
- Takes review feedback as input
- Modifies artifact in-place or creates new
- Returns updated artifact
- Limited iterations (configurable)

### 5. Retry Logic

#### 5.1 Auto-Retry

**Function**: Retry step on transient failure

**Configuration**:
- `max_retries`: Maximum retry attempts
- `retry_delay`: Delay between retries
- `retry_codes`: Which reject codes trigger retry

#### 5.2 Human-Retry

**Function**: Allow human-triggered retry

**Behavior**:
- Human reviews failure
- Decides to retry or abort
- Retry count tracked separately

### 6. Job State Management

#### 6.1 State Persistence

**Function**: Save and load job state

**Storage**: `job.json` in job directory

**Contents**:
- Current step
- Completed steps
- Artifacts
- Retry counts
- Failure history

#### 6.2 State Transitions

**States**:
| State | Description |
|-------|-------------|
| PENDING | Job created, not started |
| IN_PROGRESS | Executing steps |
| WAITING_FOR_HUMAN_APPROVAL | Human review required |
| COMPLETED | All steps completed |
| FAILED | Step failed, not retrying |

### 7. Deterministic Actions

#### 7.1 Action Execution

**Function**: Execute Python functions as steps

**Location**: `agent_runner_v2/actions/`

**Examples**:
- `finalize_bootstrap.py`: Finalize bootstrap bundles
- `validate_delivery_docs.py`: Validate delivery docs
- `sync_codebase_docs.py`: Sync codebase documentation
- `promote_artifact.py`: Promote artifacts

#### 7.2 Action Interface

```python
def action_func(
    *,
    group_name: str,
    step: str,
    state: dict,
    step_cfg: dict,
    action_args: dict
) -> dict:
    """Execute action and return result."""
    return {
        "status": "APPROVED",
        "remark": "Action completed",
        "artifacts": {...}
    }
```

## Actors

### Primary Actors

| Actor | Role | Interactions |
|-------|------|--------------|
| **Developer** | Uses workflows | Triggers execution, reviews results |
| **Operator** | Manages system | Monitors jobs, handles failures |
| **Workflow** | Automated execution | Executes steps, makes decisions |
| **Coder** | LLM model | Generates content, reviews artifacts |
| **Action** | Python function | Performs deterministic operations |

### Secondary Actors

| Actor | Role | Interactions |
|-------|------|--------------|
| **Backend** | State source | Provides job state, receives results |
| **Notification Service** | Alerts | Sends notifications on events |
| **File System** | Storage | Reads/writes artifacts |

## Core Behaviors

### Behavior: Execute Workflow Step

```
GIVEN a workflow and step are specified
AND the job state is valid
WHEN the step is executed
THEN the prompt is rendered
AND the coder is invoked
AND the meta.json is read
AND artifacts are validated
AND the result is returned
```

### Behavior: Route After Success

```
GIVEN a step completed successfully
AND the result is APPROVED
WHEN routing occurs
THEN the next step is determined
AND the job state is updated
AND execution continues
```

### Behavior: Handle Rejection

```
GIVEN a step completed
AND the result is REJECTED
WHEN handling rejection
THEN the retry count is checked
AND if under limit, refine is triggered
AND if over limit, human approval is requested
```

### Behavior: Handle Failure

```
GIVEN a step failed
WHEN handling failure
THEN the failure is logged
AND the retry count is checked
AND if retryable, retry is attempted
AND if not, job status is set to FAILED
```

### Behavior: Validate Artifacts

```
GIVEN a step produced artifacts
WHEN validating
THEN each artifact is checked for existence
AND frontmatter is validated
AND sections are checked
AND cross-references are verified
```

## Workflow Families

The system supports 21 workflow families with 290+ steps:

| Family | Steps | Purpose |
|--------|-------|---------|
| `00_master_docs_bootstrap_v1` | 13 | Bootstrap system documentation |
| `10_execution_scaffold_v1` | 13 | Scaffold delivery governance |
| `20_initiative_intake_v1` | 5 | Initiative capture |
| `21_bug_fix_intake_v1` | 7 | Bug triage and fix |
| `30_delivery_planning_v1` | 10 | Plan and task graph generation |
| `31_task_execution_v1` | 12 | Implementation and validation |
| `40_documentation_sync_v1` | 5 | Doc reconciliation |
| `50_architecture_site_v1` | 2 | HTML site generation |
| `41_audience_doc_v1` | 4 | Audience-specific docs |
| `51-55_*_docs_v1` | 1-4 | Stakeholder/developer/operator/tester/user docs |

---

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — System explanation
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Business value
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality expectations

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs` on 2026-07-10T09:43:38+08:00*
