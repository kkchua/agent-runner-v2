---
title: "Functional Specification"
template_id: "SYS-00-FS"
status: "active"
generated: "2026-07-10T11:45:32+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-15f76235"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification

## System Purpose

`agent-runner-v2` is a workflow execution platform that orchestrates LLM-based and deterministic actions to accomplish structured tasks. The system serves as an execution engine for:

- **Code generation and modification** via LLM coders
- **Documentation generation and validation** via specialized actions
- **Media content generation** via external service integration
- **Workflow governance** via validation and reconciliation

The primary value is providing a structured, repeatable, observable execution environment for AI-assisted software development workflows.

## Scope

### In Scope

| Category | Functions |
|----------|-----------|
| **Workflow Execution** | Multi-step workflow orchestration, prompt rendering, step routing |
| **LLM Integration** | Claude, Codex, Qwen invocation with model-specific handling |
| **Action Library** | 26 deterministic actions for common operations |
| **Job Management** | Job lifecycle, state persistence, artifact tracking |
| **Backend Integration** | Worker mode, polling, daemon supervision |
| **Bundle Management** | Workflow seeding, template loading, runtime updates |

### Out of Scope

| Category | Exclusions |
|----------|------------|
| **LLM Training** | Fine-tuning, model customization |
| **General Scheduling** | Cron-like job scheduling, distributed task queues |
| **Web Interface** | GUI, web dashboards, real-time collaboration |
| **Version Control** | Git operations (delegates to external tools) |

## Functional Capabilities

### FC-01: Workflow Execution

**Description**: Execute multi-step workflows with deterministic routing and artifact management.

**Requirements**:
- FR-01.1: Load workflow definition from bundle
- FR-01.2: Execute steps in sequence according to workflow definition
- FR-01.3: Support conditional routing (next/failure paths)
- FR-01.4: Persist job state between steps
- FR-01.5: Track artifact production and consumption

**Acceptance Criteria**:
- Workflows complete without manual intervention
- Failed steps route to failure handlers
- Job state is recoverable after interruption

### FC-02: Job State Management

**Description**: Manage job lifecycle from creation through completion.

**Requirements**:
- FR-02.1: Create jobs with unique IDs
- FR-02.2: Persist job state to JSON files
- FR-02.3: Support job querying and status checking
- FR-02.4: Handle job resumption after interruption
- FR-02.5: Archive completed jobs

**Acceptance Criteria**:
- Job files are valid JSON
- State changes are atomic
- Jobs can be resumed across process restarts

### FC-03: Multi-Model Support

**Description**: Support multiple LLM providers with model-specific handling.

**Requirements**:
- FR-03.1: Support Claude (Anthropic) API
- FR-03.2: Support Codex (OpenAI) API
- FR-03.3: Support Qwen (Alibaba) API
- FR-03.4: Allow model-specific prompt templates
- FR-03.5: Provide model aliasing

**Acceptance Criteria**:
- Each model can be invoked independently
- Model-specific prompts are loaded when available
- Aliases resolve to correct model configurations

### FC-04: Step Result Routing

**Description**: Route step execution results to appropriate next steps.

**Requirements**:
- FR-04.1: Parse meta.json sidecar for structured results
- FR-04.2: Route to 'next' step on success
- FR-04.3: Route to 'failure' step on failure
- FR-04.4: Support approval gates
- FR-04.5: Support review/refine loops

**Acceptance Criteria**:
- Routing decisions based on meta.json status
- No silent recovery paths
- Explicit failure routing

### FC-05: Artifact Validation

**Description**: Validate artifacts produced by workflow steps.

**Requirements**:
- FR-05.1: Check artifact existence
- FR-05.2: Validate artifact format (markdown structure)
- FR-05.3: Validate section requirements
- FR-05.4: Report validation failures
- FR-05.5: Support artifact promotion

**Acceptance Criteria**:
- All declared artifacts are checked
- Validation failures block workflow progression
- Reports include specific error details

### FC-06: Local Execution Mode

**Description**: Execute workflows locally without backend connection.

**Requirements**:
- FR-06.1: Run workflows from local files
- FR-06.2: Store artifacts locally
- FR-06.3: Support workflow parameter injection
- FR-06.4: Support artifact reference substitution
- FR-06.5: Provide local job management

**Acceptance Criteria**:
- No backend connectivity required
- All artifacts stored in local filesystem
- Jobs can be listed and inspected

### FC-07: Backend Worker Mode

**Description**: Execute steps assigned by backend.

**Requirements**:
- FR-07.1: Poll backend for available work
- FR-07.2: Claim steps from backend queue
- FR-07.3: Execute claimed steps
- FR-07.4: Report results to backend
- FR-07.5: Handle backend errors gracefully

**Acceptance Criteria**:
- Workers claim and execute steps reliably
- Results are submitted successfully
- Backend unavailability is handled

### FC-08: Daemon Supervision

**Description**: Supervise workflow execution as a long-running daemon.

**Requirements**:
- FR-08.1: Run continuously as supervisor
- FR-08.2: Spawn child processes for steps
- FR-08.3: Monitor child process health
- FR-08.4: Emit heartbeats to backend
- FR-08.5: Aggregate child logs

**Acceptance Criteria**:
- Daemon runs indefinitely
- Child failures don't crash daemon
- Heartbeats maintain worker registration

### FC-09: Documentation Generation

**Description**: Generate documentation artifacts through workflows.

**Requirements**:
- FR-09.1: Generate module documentation
- FR-09.2: Generate system documentation
- FR-09.3: Generate architecture documentation
- FR-09.4: Generate multi-audience documentation
- FR-09.5: Generate HTML sites from markdown

**Acceptance Criteria**:
- Generated docs follow templates
- Cross-references are valid
- Sites are renderable HTML

### FC-10: Documentation Validation

**Description**: Validate documentation against standards.

**Requirements**:
- FR-10.1: Validate frontmatter completeness
- FR-10.2: Validate required sections present
- FR-10.3: Validate cross-reference resolution
- FR-10.4: Validate section requirements
- FR-10.5: Report validation results

**Acceptance Criteria**:
- All validation checks execute
- Results indicate pass/fail status
- Errors reference specific issues

### FC-11: Delivery Scaffold

**Description**: Bootstrap new repositories with governance documentation.

**Requirements**:
- FR-11.1: Generate SOP documents
- FR-11.2: Generate template registry
- FR-11.3: Generate agent contracts
- FR-11.4: Generate status rules
- FR-11.5: Populate folder structure

**Acceptance Criteria**:
- Scaffold creates all required documents
- Documents follow template_id conventions
- Structure matches governance standards

### FC-12: Review and Refine Loops

**Description**: Support iterative review/refine cycles in workflows.

**Requirements**:
- FR-12.1: Route to review steps
- FR-12.2: Accept approve/reject decisions
- FR-12.3: Route to refinement on reject
- FR-12.4: Track review iterations
- FR-12.5: Support human-in-the-loop approval

**Acceptance Criteria**:
- Reviews block until approved
- Rejections trigger refinement
- Iteration counts are tracked

### FC-13: Failure Handling

**Description**: Handle step failures gracefully.

**Requirements**:
- FR-13.1: Detect step failures
- FR-13.2: Route to failure handlers
- FR-13.3: Support retry logic
- FR-13.4: Support failure recovery
- FR-13.5: Report failure details

**Acceptance Criteria**:
- Failures are detected promptly
- No silent failures
- Failure paths are explicit

### FC-14: Runner Home Initialization

**Description**: Initialize runtime environment for workflows.

**Requirements**:
- FR-14.1: Create runner home directory
- FR-14.2: Create config.json
- FR-14.3: Seed workflow bundles
- FR-14.4: Create logs directory
- FR-14.5: Create jobs directory

**Acceptance Criteria**:
- Init creates all required directories
- Config template is valid JSON
- Bundles are copied from bootstrap

## Actors

### Human Actors

| Actor | Role | Primary Interactions |
|-------|------|---------------------|
| **Workflow User** | Initiates workflow execution | `ukbe-run-agent run` |
| **Operator** | Manages daemon and workers | `ukbe-run-agent daemon`, monitoring |
| **Approver** | Reviews and approves outputs | Approval workflows |
| **Developer** | Extends actions and workflows | Action development, template editing |

### System Actors

| Actor | Role | Primary Interactions |
|-------|------|---------------------|
| **Backend API** | Assigns work to workers | Step assignment, result submission |
| **LLM Providers** | Executes coder steps | Claude, Codex, Qwen APIs |
| **External Services** | Media generation | ComfyUI, video assembly |

## Core Behaviors

### Behavior 1: Step Execution

**Trigger**: Workflow step is reached

**Preconditions**:
- Job exists with valid state
- Step configuration is loaded
- Input artifacts are available

**Main Flow**:
1. Load step configuration from template groups
2. Render prompt template with artifact substitution
3. If coder step: invoke LLM via adapter
4. If action step: execute Python function
5. Wait for completion
6. Read meta.json sidecar
7. Validate artifacts
8. Route to next step or failure handler

**Postconditions**:
- Artifacts written to disk
- meta.json exists with result
- Job state updated

### Behavior 2: Worker Claim

**Trigger**: Daemon polls backend

**Preconditions**:
- Backend is reachable
- Worker is registered
- Daemon is running

**Main Flow**:
1. Poll backend for available steps
2. If step available: claim assignment
3. Spawn child process for execution
4. Monitor child process
5. Read result file
6. Submit result to backend
7. Return to polling

**Postconditions**:
- Step is executed
- Result is submitted
- Child process terminates

### Behavior 3: Documentation Sync

**Trigger**: `documentation_sync_v1` workflow invoked

**Preconditions**:
- Codebase has changed
- Documentation may be stale

**Main Flow**:
1. Scan repository for modules
2. Compare with existing documentation
3. Generate missing module docs
4. Update stale module docs
5. Generate change impact document
6. Validate documentation
7. Report sync results

**Postconditions**:
- Documentation reflects current code
- Change impact documented
- Validation passed

## Data Requirements

### Job State Schema

```json
{
  "job_id": "JOB-YYYYMMDD-XXXXXXXX",
  "template_group": "workflow_name_v1",
  "state": "running|completed|failed",
  "current_step": "step_name",
  "artifacts": {
    "ARTIFACT_KEY": "path/to/artifact.md"
  },
  "created_at": "2026-07-10T11:45:32+08:00",
  "updated_at": "2026-07-10T11:45:32+08:00",
  "step_history": [...],
  "metadata": {...}
}
```

### Meta.json Schema

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED|REJECTED",
    "remark": "Human-readable summary",
    "artifacts": {
      "ARTIFACT_KEY": "path/to/artifact.md"
    },
    "recorded_at": "2026-07-10T11:45:32+08:00"
  }
}
```

### Execution Request Schema

```json
{
  "template_group": "workflow_name_v1",
  "step": "step_name",
  "job_id": "JOB-...",
  "artifacts": {...},
  "context": {...}
}
```

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform overview
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Business capabilities
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality attributes
