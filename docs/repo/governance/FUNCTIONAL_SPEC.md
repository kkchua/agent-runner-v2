---
template_id: "SYS-00-FS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:13:00+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Functional Specification

This document describes the major behaviors and workflow capabilities of
`agent-runner-v2`, grounded in the actual repository implementation.

## System Purpose

`agent-runner-v2` orchestrates AI-Driven SDLC workflows with human approval gates.
It manages the full lifecycle of software development artifacts from requirements
through validation, bridging the gap between AI-assisted development and controlled,
auditable artifact production.

## Actors

| Actor | Role | Interaction Points |
|-------|------|-------------------|
| **Developer** | Executes workflows, reviews results | CLI commands, job state |
| **Operator** | Monitors execution, manages daemon | Daemon mode, notifications |
| **LLM Coder** | Generates artifacts, reports results | Sidecar contract, prompt templates |
| **Action** | Validates and transforms files | Python function calls |
| **Backend** | Coordinates distributed execution | API endpoints, job queue |

## Functional Capabilities

### FC-01: Workflow Execution

**Description**: Execute declarative workflow bundles step by step.

**Behaviors**:
- Load workflow from TOML manifest
- Execute steps in declared order
- Persist job state after each step
- Support parallel independent workflows

**Inputs**: Workflow name, optional job parameters
**Outputs**: Job state, step artifacts

### FC-02: Coder Step Execution

**Description**: Invoke LLM coders for generative steps.

**Behaviors**:
- Render prompt template with context
- Spawn coder subprocess (OpenCode, Claude, etc.)
- Monitor for timeout and termination
- Parse sidecar `meta.json` for results

**Inputs**: Prompt template, context variables
**Outputs**: Generated artifacts, usage metrics

### FC-03: Action Step Execution

**Description**: Execute deterministic Python actions.

**Behaviors**:
- Resolve action name to registered function
- Execute with step context parameters
- Return structured result (status, artifacts, remark)
- Handle exceptions gracefully

**Inputs**: Action name, parameters
**Outputs**: Action result (APPROVED/REJECTED, artifacts)

### FC-04: Workflow Routing

**Description**: Transition between workflow steps based on results.

**Behaviors**:
- Resolve routing logic from workflow manifest
- Support approve/reject/replan transitions
- Handle review-refine-replan loops
- Default to resolve_transition() fallback

**Inputs**: Current step, step result
**Outputs**: Next step name or workflow completion

### FC-05: State Management

**Description**: Persist and recover workflow execution state.

**Behaviors**:
- Create job directory structure
- Write job state after each step
- Track step directories and artifacts
- Support recovery from interrupted execution

**Inputs**: Job ID, step results
**Outputs**: Persisted state files

### FC-06: Notification Dispatch

**Description**: Send notifications on workflow events.

**Behaviors**:
- Resolve credentials from config/env
- Send Pushover notifications on step completion
- Include job context in notification messages
- Handle credential errors gracefully

**Inputs**: Event type, job context
**Outputs**: Notification delivery status

### FC-07: Daemon Mode

**Description**: Run as background daemon for continuous execution.

**Behaviors**:
- Poll backend for pending jobs
- Spawn worker subprocesses for execution
- Handle graceful shutdown
- Maintain heartbeat with backend

**Inputs**: Backend connection configuration
**Outputs**: Execution results to backend

### FC-08: Bootstrap Governance

**Description**: Generate ecosystem and repository governance documents.

**Behaviors**:
- Execute Layer 1 governance bootstrap
- Execute Layer 2 master docs bootstrap
- Generate documentation without code modification
- Validate governance compliance

**Inputs**: Repository analysis
**Outputs**: Governance documents

## Core Behaviors

### Workflow Loading

```
workflow.toml → BundleLoader → WorkflowBundle → validated steps
```

The bundle loader:
1. Reads TOML manifest from workflow directory
2. Validates required fields and structure
3. Resolves prompt and action references
4. Returns canonical `WorkflowBundle` dataclass

### Step Execution

```
StepConfig → StepRunner → CoderAdapter/Action → Result
```

The step runner:
1. Resolves step type (coder/action/review)
2. Builds execution context from workflow parameters
3. Invokes appropriate executor
4. Returns structured result for routing

### Result Routing

```
Result → WorkflowRouter → next_step | workflow_complete
```

The workflow router:
1. Checks result status (APPROVED/REJECTED)
2. Resolves routing from workflow manifest
3. Falls back to `resolve_transition()` if no explicit routing
4. Returns next step name or completion signal

### Sidecar Contract

Each coder step produces a `meta.json` sidecar:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "Brief summary",
    "artifacts": {
      "ARTIFACT_KEY": "absolute/path/to/artifact"
    }
  },
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 567
  }
}
```

## Workflow Capabilities

### Bootstrap Workflow Families

| Workflow | Steps | Purpose |
|----------|-------|---------|
| `00_bootstrap_lifecycle_admin_v1` | 5 | Bootstrap lifecycle management |
| `00_layer1_governance_bootstrap_v1` | 6 | Layer 1 governance generation |
| `00_repo_master_docs_bootstrap_v1` | 14 | Repo master docs bootstrap |

### Action Library

| Action Category | Actions | Purpose |
|-----------------|---------|---------|
| Validation | 12 | Validate docs, sites, governance |
| Site Generation | 2 | Generate HTML/PDF sites |
| Scaffolding | 3 | Prepare delivery scaffold, promote artifacts |
| Sync | 2 | Sync codebase and system docs |
| Cleanup | 1 | Archive previous versions |

### Execution Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Manual | CLI-driven execution | Development, debugging |
| Daemon | Background worker mode | Production, continuous execution |
| Backend | API-driven coordination | Distributed execution |

## Constraints

1. **Zero code mutation**: Bootstrap workflows must not alter source code
2. **Absolute paths**: All placeholder paths must be absolute for Windows compatibility
3. **Sidecar contract**: Coder results must be valid `meta.json`
4. **Credential resolution**: Notifications require valid Pushover credentials
5. **Layer dependency**: Lower layers must complete before higher layers