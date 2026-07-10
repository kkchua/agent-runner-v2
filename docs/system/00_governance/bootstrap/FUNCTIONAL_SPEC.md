---
template_id: "SYS-00-FS"
title: "Functional Specification - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification: agent-runner-v2

## System Purpose

agent-runner-v2 is a standalone Python LLM workflow orchestration engine that runs structured multi-step workflows across multiple LLM backends (Claude, Codex, Qwen) with review loops, retries, approval gates, and deterministic runner actions.

## Functional Capabilities

### 1. Workflow Execution

**Capability**: Execute multi-step workflows with defined transitions

**Behaviors**:
- Load workflow definitions from global runtime bundles
- Execute steps in sequence according to workflow graph
- Support conditional routing based on step results
- Handle review/refine loops with configurable limits
- Support replan escalation after max rejects

**Workflow Families**:

| Workflow Family | Purpose | Steps |
|-----------------|---------|-------|
| `00_master_docs_bootstrap_v1` | Generate master system docs | project_analysis → system_overview → architecture_docs → review → refine |
| `10_execution_scaffold_v1` | Establish delivery governance | project_analysis → generate_sop → review_sop → generate_templates → review_templates → generate_agents → review_agents |
| `20_initiative_intake_v1` | Initiative intake and refinement | pre_init → review_pre_init → refine_pre_init → plan → task_graph → task |
| `21_bug_fix_intake_v1` | Bug fix workflow | triage → reproduce → root_cause → patch → regression_validate |
| `30_delivery_planning_v1` | Delivery planning | planner → review_plan → task_graph → review_task_graph → task |
| `31_task_execution_v1` | Task implementation | impl → review_impl → executor → validate |
| `40_documentation_sync_v1` | Documentation reconciliation | sync_docs → review_docs → refine_docs → validate_doc_sync |
| `50_architecture_site_v1` | Generate audience sites | generate_site → validate_site → publish_site |

### 2. Step Types

**Capability**: Support multiple step execution modes

**Coder Steps**:
- Invoke LLM backends via subprocess
- Support Claude, Codex, Qwen, and aliased models
- Handle streaming and polling modes
- Apply timeout and retry policies
- Capture stdout/stderr for debugging

**Action Steps**:
- Execute in-process Python functions
- Access job state and context
- Write artifacts directly
- Support deterministic operations
- No LLM involvement

**Validation Steps**:
- Validate artifact existence
- Check content requirements
- Verify section completeness
- Report validation results
- Route based on pass/fail

### 3. Prompt Rendering

**Capability**: Render templates with context substitution

**Behaviors**:
- Load prompt templates from workflow bundles
- Substitute placeholder variables (`{VAR_NAME}`)
- Support conditional sections
- Include artifact content by reference
- Apply template-specific transformations

**Context Sources**:
- Job state (job_id, step_number, etc.)
- Reference files (artifacts from previous steps)
- Workflow configuration
- Environment variables
- Runtime context (paths, settings)

### 4. Artifact Management

**Capability**: Track and validate workflow artifacts

**Behaviors**:
- Declare expected artifacts in workflow config
- Validate artifact existence after step execution
- Support artifact path templating
- Handle artifact key normalization
- Skip sidecar files in validation

**Artifact Types**:
- Markdown documents (`.md`)
- JSON files (`.json`)
- HTML files (`.html`)
- Image folders
- Video files

### 5. Sidecar Contract

**Capability**: Enforce meta.json as structured result channel

**Requirements**:
- Mandatory meta.json sidecar for every step
- Schema version enforcement (v2)
- Status reporting (APPROVED, REJECTED, FAILURE)
- Artifact declaration with paths
- Timestamp recording

**Validation**:
- Missing meta.json → hard failure
- Invalid JSON → hard failure
- Missing required fields → hard failure
- No silent recovery

### 6. Routing and Control Flow

**Capability**: Route execution based on step results

**Routing Decisions**:
- **approve**: Continue to next step
- **reject**: Route to refine/replan
- **failure**: Route to failure handling
- **waiting**: Pause for external input

**Review Loops**:
- Configurable `max_rejects` per workflow
- Escalate to replan after threshold
- Track iteration count in job state
- Support human-in-the-loop review

### 7. Backend Integration

**Capability**: Connect to backend for enterprise execution

**Modes**:
- **poll**: One-shot work polling
- **worker**: Continuous worker loop
- **daemon**: Supervised execution with child processes
- **execute-step**: Single step execution

**Backend Operations**:
- Claim work from backend queue
- Submit step results
- Report heartbeats
- Upload artifacts
- Request approvals

### 8. Job State Management

**Capability**: Persist and recover job execution state

**Behaviors**:
- Write job.json after each step
- Support job resumption
- Track step execution history
- Store artifact references
- Record timing information

**State Contents**:
- Workflow name and step number
- Artifact paths and status
- Review iteration counts
- Backend run references
- Timing and metadata

### 9. Notification System

**Capability**: Send execution notifications

**Channels**:
- Pushover (mobile push notifications)
- Console (local execution)
- Backend events (enterprise)

**Triggers**:
- Step completion
- Step failure
- Review required
- Approval granted
- Job completion

### 10. Bundle Management

**Capability**: Load and manage workflow bundles

**Sources**:
- Global runtime bundles (`~/.ukbe-runner/workflows/`)
- Project-local plugins (`workflows/<name>/`)
- Legacy TEMPLATE_GROUPS (backward compatibility)

**Discovery**:
- Global first, local fallback
- Plugin adapter pattern
- Schema validation at load
- Cache for performance

## Actors

### Human Actors

| Actor | Role | Interactions |
|-------|------|--------------|
| **Developer** | Uses runner for development | Local execution, debugging, testing |
| **Operator** | Runs daemon, monitors execution | Daemon supervision, log review |
| **Reviewer** | Reviews step outputs | Approval/rejection decisions |
| **Stakeholder** | Consumes documentation | Reads generated docs, sites |

### System Actors

| Actor | Role | Interactions |
|-------|------|--------------|
| **Backend** | Source of truth for enterprise | Job queue, result storage, events |
| **LLM Backend** | Provides AI capabilities | Prompt processing, response generation |
| **Notification Service** | Delivers alerts | Pushover, console, backend events |

## Core Behaviors

### Initialization

```
ukbe-run-agent init
    ↓
Create ~/.ukbe-runner/
    ↓
Copy bootstrap workflows
    ↓
Create config.json
    ↓
Ready for execution
```

### Local Execution

```
ukbe-run-agent run --template-group <workflow>
    ↓
Load workflow bundle
    ↓
For each step:
    Render prompt
    Execute (coder or action)
    Read meta.json
    Validate artifacts
    Route next step
    ↓
Finalize job
```

### Worker Execution

```
ukbe-run-agent worker --backend-url <url>
    ↓
Poll backend for work
    ↓
Claim available job
    ↓
For each step:
    Execute via execute-step
    Submit result to backend
    ↓
Complete job
```

### Daemon Execution

```
ukbe-run-agent daemon <worker_id>
    ↓
Start supervisor loop
    ↓
Poll backend for work
    ↓
Spawn child process for step
    ↓
Monitor child execution
    ↓
Collect result
    ↓
Report to backend
    ↓
Continue polling
```

## Configuration

### Config File (`~/.ukbe-runner/config.json`)

```json
{
  "backend_url": "http://127.0.0.1:8100",
  "worker_id": "kode-worker-01",
  "notification": {
    "pushover": {
      "app_token": "...",
      "user_key": "..."
    }
  },
  "engine": "SNAPSHOT"
}
```

### Workflow Configuration

```toml
[workflow]
name = "example_v1"
description = "Example workflow"

[step.01_example]
produces = ["EXAMPLE_FILE"]
coder = { model = "claude-opus" }
```

## Error Handling

### Error Categories

| Category | Behavior | Recovery |
|------------|----------|----------|
| **Meta.json missing** | Hard failure | None (manual fix) |
| **Meta.json invalid** | Hard failure | None (manual fix) |
| **Artifact missing** | Hard failure | Retry or manual |
| **Validation failed** | Routing decision | Refine/replan |
| **LLM timeout** | Retry with backoff | Escalate |
| **Backend unavailable** | Retry with backoff | Degrade to local |

### Retry Policy

- Exponential backoff (1s, 2s, 4s, 8s, ...)
- Max retries configurable per workflow
- Final failure escalates to human

## Functional Constraints

### Runtime Constraints

- Python 3.10+ required
- Windows/macOS/Linux support
- Filesystem for artifacts
- Network for LLM/backend

### Execution Constraints

- One workflow per job
- Sequential step execution
- Artifact paths relative to project root
- Sidecar required for every step

### Scaling Constraints

- Concurrent jobs limited by backend
- Artifact storage grows over time
- Log retention requires configuration
- Notification rate limiting

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
