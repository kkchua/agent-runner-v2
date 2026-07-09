---
template_id: "SYS-00-FS"
managed_by: workflow-generated
generated: "2026-07-09T21:18:02+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification

## System Purpose

agent-runner-v2 is a workflow orchestration engine that transforms structured prompts into executable steps, coordinates with AI coders and deterministic actions, and maintains job state throughout multi-step workflows.

The system enables:
- **Repeatable workflows**: Same input produces consistent execution
- **Reviewable outputs**: Each step produces validated artifacts
- **Resumable execution**: State persistence across sessions
- **Scalable operation**: Worker mode distributes execution across workstations
- **Auditable history**: Complete execution trail with sidecar communication

## Functional Capabilities

### Core Capabilities

| Capability | Description | Key Behaviors |
|------------|-------------|---------------|
| **Workflow Execution** | Execute multi-step workflows with state management | Load bundle, render prompt, execute, route |
| **Coder Invocation** | Invoke Claude, Codex, Qwen via unified interface | Adapter pattern, timeout management |
| **Action Execution** | Run deterministic Python actions | 29+ built-in actions, extensible |
| **Sidecar Communication** | Structured result communication via meta.json | Validation, artifact verification |
| **Job State Management** | Persist and resume job execution | Schema versioning, migration |
| **Review Routing** | Route based on approve/reject/refine decisions | Retry logic, failure handling |

### Workflow Capabilities

| Capability | Description |
|------------|-------------|
| **Template Groups** | Define workflow families with steps, prompts, and routing |
| **Prompt Rendering** | Substitute context variables, inject sidecar instructions |
| **Preflight Validation** | Verify required artifacts before execution |
| **Step Execution** | Invoke coder or action with timeout and retry |
| **Result Validation** | Verify meta.json schema and artifact existence |
| **Routing** | Determine next step based on sidecar status |

### Coder Capabilities

| Capability | Description |
|------------|-------------|
| **Multi-Model Support** | Claude Code, Codex CLI, Qwen Code, aliased models |
| **Unified Interface** | Single `invoke_coder()` function for all coders |
| **Timeout Management** | Step override → env var → config → default priority |
| **Polling** | Poll for coder completion with configurable intervals |
| **Result Capture** | Capture stdout, stderr, exit code |
| **Error Handling** | CoderInvocationError with detailed context |

### Action Capabilities

| Category | Actions |
|----------|---------|
| **Documentation** | validate_delivery_docs, validate_codebase_docs, sync_system_docs, validate_system_docs |
| **Architecture** | generate_site, publish_architecture_site, validate_*_site |
| **Bootstrap** | prepare_delivery_scaffold, finalize_bootstrap, scan_repo_codebase |
| **Media** | execute_t2i, execute_i2v, execute_voiceover, assemble_video, submit_comfyui |
| **Artifacts** | copy_artifact, promote_artifact, archive_previous_version |
| **Initiative** | promote_init |

### Execution Mode Capabilities

| Mode | Capabilities |
|------|--------------|
| **Local** | Manual invocation, full control, debugging |
| **Worker** | Backend polling, work claiming, result submission |
| **Daemon** | Process supervision, heartbeat, child tracking |

## Actors

### Primary Actors

| Actor | Role | Goals |
|-------|------|-------|
| **Developer** | Uses workflows for development tasks | Complete tasks with quality, track progress |
| **Operator** | Manages workflow execution | Ensure reliability, monitor health |
| **System** | Executes workflows automatically | Complete steps, handle failures |
| **Reviewer** | Reviews step outputs | Ensure quality, provide feedback |

### Secondary Actors

| Actor | Role | Goals |
|-------|------|-------|
| **Backend** | Provides work queue | Distribute tasks, track progress |
| **Coder** | Executes prompts | Generate code, documentation |
| **Notification Service** | Sends alerts | Inform of completion, failures |

### Actor Interactions

```
Developer → Workflow → Step → Coder/Action → Artifact
                              ↓
Operator ← Monitoring ← Job State ← Sidecar
```

## Core Behaviors

### Behavior: Load Workflow Bundle

**Trigger**: Workflow execution starts

**Steps:**
1. Resolve workflow root from RUNNER_ROOT
2. Load template_groups.py
3. Load prompt templates
4. Validate workflow structure

**Output**: Loaded workflow bundle

**Error Handling**:
- Missing template_groups.py → Error, halt execution
- Invalid JSON → Error, halt execution
- Missing prompts → Warning, continue with fallback

### Behavior: Render Prompt

**Trigger**: Step execution begins

**Steps:**
1. Load prompt template from file
2. Build context from job state and artifact paths
3. Substitute placeholders (e.g., `{PROJECT_ANALYSIS}`)
4. Inject sidecar instructions at end
5. Calculate checksum

**Output**: Rendered prompt text

**Error Handling**:
- Missing template → Error, halt execution
- Unresolved placeholder → Warning, continue with raw placeholder
- Template syntax error → Error, halt execution

### Behavior: Execute Step

**Trigger**: Prompt rendered, preflight passed

**Steps:**
1. Determine execution type (coder vs action)
2. For coder: invoke via adapter with timeout
3. For action: call Python function directly
4. Wait for completion
5. Read sidecar from expected path

**Output**: StepResult with sidecar data

**Error Handling**:
- Coder timeout → Retry with backoff
- Coder failure → Route to failure handler
- Missing sidecar → MetaJsonMissingError
- Invalid sidecar → MetaJsonInvalidError

### Behavior: Validate Result

**Trigger**: Step execution completed

**Steps:**
1. Parse meta.json sidecar
2. Validate schema version
3. Check status field (APPROVED/REJECTED)
4. Verify all declared artifacts exist
5. Calculate artifact checksums

**Output**: Validation result

**Error Handling**:
- Invalid schema → MetaJsonInvalidError
- Missing artifact → ArtifactMissingError
- Status mismatch → Log warning, continue

### Behavior: Route After Step

**Trigger**: Step validated

**Steps:**
1. Check sidecar status
2. If APPROVED → Determine next step from template
3. If REJECTED → Check retry count
4. If retry available → Retry step
5. If retry exhausted → Route to failure
6. Update job state with routing decision

**Output**: Next step ID or completion

**Error Handling**:
- Routing logic error → Log error, halt
- Step not found → Log error, halt
- State update failure → Retry with backoff

### Behavior: Handle Failure

**Trigger**: Step failed or retry exhausted

**Steps:**
1. Classify failure (AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, FATAL)
2. Update job state with failure info
3. If AUTO_RETRYABLE → Schedule retry
4. If HUMAN_RETRY_REQUIRED → Wait for human decision
5. If FATAL → Mark job failed, notify

**Output**: Failure envelope

**Error Handling**:
- Classification error → Default to HUMAN_RETRY_REQUIRED
- State update failure → Log error, continue

### Behavior: Poll Backend

**Trigger**: Worker mode execution

**Steps:**
1. Authenticate with backend
2. Request available work
3. If work available → Claim step
4. Execute claimed step
5. Submit results
6. Repeat until stopped

**Output**: Step execution results

**Error Handling**:
- Backend unavailable → Retry with backoff
- Authentication failure → Log error, halt
- Claim conflict → Retry claim

### Behavior: Supervise Children

**Trigger**: Daemon mode execution

**Steps:**
1. Poll backend for work
2. Claim available step
3. Spawn child process for execution
4. Monitor child process
5. Emit heartbeat with child status
6. Handle child completion/failure
7. Repeat until stopped

**Output**: Child process management

**Error Handling**:
- Child spawn failure → Log error, continue
- Child timeout → Terminate, report failure
- Heartbeat failure → Log error, continue

## State Management

### Job State Schema

| Field | Type | Description |
|-------|------|-------------|
| job_id | string | Unique job identifier |
| workflow | string | Workflow family ID |
| current_step | string | Current step ID |
| status | string | PENDING, IN_PROGRESS, COMPLETED, FAILED |
| created_at | datetime | Job creation time |
| updated_at | datetime | Last update time |
| step_runs | array | History of step executions |
| artifacts | object | Generated artifact paths |

### Step State

| Field | Type | Description |
|-------|------|-------------|
| step_id | string | Step identifier |
| status | string | PENDING, RUNNING, COMPLETED, FAILED |
| started_at | datetime | Step start time |
| completed_at | datetime | Step completion time |
| result | object | Sidecar result data |
| retry_count | integer | Number of retries |

### State Transitions

```
PENDING → IN_PROGRESS → COMPLETED
                    → FAILED
                    → WAITING_FOR_APPROVAL
                    → RETRYING
```

## Workflow Families

### Initiative Intake (20_initiative_intake_v1)

**Purpose**: Structured requirement capture

**Steps**:
1. Pre-init drafting
2. Pre-init review
3. Pre-init refinement

**Artifacts**: DRAFT_INIT_FILE, PRE_INIT_FILE

### Delivery Planning (30_delivery_planning_v1)

**Purpose**: Plan generation and task decomposition

**Steps**:
1. Planner step
2. Plan review/refine
3. Task graph generation
4. Task graph review/refine
5. Task contract generation
6. Task contract review

**Artifacts**: PLAN_FILE, TASK_GRAPH_FILE, TASK_FILE

### Task Execution (31_task_execution_v1)

**Purpose**: Implementation and validation

**Steps**:
1. Implementation planning
2. Implementation review
3. Execution
4. Documentation sync
5. Validation

**Artifacts**: IMPL_FILE, REVIEW_FILE, VALIDATION_FILE

### Documentation Sync (40_documentation_sync_v1)

**Purpose**: Reconcile documentation with codebase

**Steps**:
1. Sync documentation
2. Review documentation
3. Refine documentation
4. Validate documentation

**Artifacts**: Updated documentation set

### Architecture Site (50_architecture_site_v1)

**Purpose**: Publish browsable HTML documentation

**Steps**:
1. Generate stakeholder site
2. Generate developer site
3. Generate operator site
4. Validate sites
5. Publish sites

**Artifacts**: HTML sites, PDF exports

## Error Handling

### Error Classification

| Class | Description | Action |
|-------|-------------|--------|
| **AUTO_RETRYABLE** | Transient failure, can retry | Automatic retry with backoff |
| **HUMAN_RETRY_REQUIRED** | Requires human decision | Wait for human input |
| **FATAL** | Unrecoverable error | Mark job failed |

### Failure Sources

| Source | Examples |
|--------|----------|
| **PREFLIGHT** | Missing required artifacts, validation failure |
| **INVOCATION** | Coder timeout, process failure |
| **SIDEcar** | Missing meta.json, invalid schema |
| **ARTIFACT** | Missing declared artifact, checksum mismatch |
| **ROUTING** | Unknown step, invalid transition |
| **STATE** | Corrupted job state, schema mismatch |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 03_generate_system_overview_docs*
