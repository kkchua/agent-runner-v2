---
template_id: "SYS-03-CA"
title: "Component Architecture - agent-runner-v2"
status: "active"
generated: "2026-07-04T10:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture

## Component Groups

### 1. CLI Entry and Orchestration

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **CLI Parser** | `run_agent.py` | Argument parsing, command dispatch, top-level orchestration |
| **Main Loop** | `run_agent.py` | Job lifecycle, step iteration, failure handling |
| **Command Handlers** | `run_agent.py` | `init`, `run`, `worker`, `poll`, `execute-step`, `daemon` |

**Key Behaviors:**
- Loads configuration and workflow bundle
- Resolves or creates job state
- Iterates through steps until completion or failure
- Handles preflight checks and routing decisions

### 2. Step Execution Engine

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Step Runner** | `step_runner.py` | Prompt rendering, coder invocation, artifact validation |
| **Prompt Builder** | `step_runner.py` | Context assembly, template rendering, checksum computation |
| **Result Validator** | `step_runner.py` | meta.json validation, artifact existence checks |

**Key Behaviors:**
- Renders prompts from templates with artifact context
- Invokes coder via adapters with timeout handling
- Reads and validates `meta.json` sidecar
- Raises exceptions on validation failures (no silent recovery)

### 3. Workflow Routing

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Workflow Router** | `workflow_router.py` | Post-step routing for approve/reject/failure cases |
| **State Updater** | `workflow_router.py` | Job state transitions, retry tracking, review state |
| **Failure Classifier** | `workflow_router.py` | Auto-retryable vs human-retryable vs fatal |

**Key Behaviors:**
- Routes APPROVED steps to next step
- Handles REJECTED steps with retry limits
- Classifies failures for appropriate handling
- Updates job state with step results

### 4. Job State Management

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Job Lifecycle** | `job_state.py` | Create, load, save, migrate job state |
| **Step Tracking** | `job_state.py` | Completed steps, failed steps, retry counts |
| **Schema Migration** | `job_state.py` | Backward compatibility, state version migration |
| **Preflight Checks** | `job_state.py` | Artifact readiness, binding integrity |

**Key Behaviors:**
- Persists job state as JSON with schema versioning
- Tracks step completion, failures, and retry history
- Supports loop context for review/refine cycles
- Manages task execution bindings for planning/execution split

### 5. Coder Adapters

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Claude Adapter** | `coder_adapters.py` | Anthropic API invocation |
| **Codex Adapter** | `coder_adapters.py` | OpenAI API invocation |
| **Qwen Adapter** | `coder_adapters.py` | Alibaba API invocation |
| **Usage Tracking** | `coder_adapters.py` | Token counting, cost calculation |

**Key Behaviors:**
- Abstracts provider-specific invocation details
- Handles sidecar polling with configurable timeouts
- Returns structured `InvocationResult` with usage data
- Supports environment-based credential configuration

### 6. Runtime Context

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Context Manager** | `runtime_context.py` | Process-local runtime context |
| **Path Resolution** | `runtime_context.py` | Project root, runner home, artifact paths |
| **Path Proxy** | `runtime_context.py` | Lazy path resolution from current context |

**Key Behaviors:**
- Maintains process-local runtime configuration
- Resolves paths relative to project or runner home
- Supports delivery root override for scaffold workflows

### 7. Bundle Loading

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Workflow Loader** | `bundle_loader.py` | Load workflow module from runtime bundle |
| **Bootstrap Seeder** | `bundle_loader.py` | Seed global runner home from package bootstrap |
| **Project Config** | `bundle_loader.py` | Load/save project configuration |

**Key Behaviors:**
- Loads `template_groups.py` from runtime workflow bundle
- Seeds global runner home on `init` command
- Resolves workflow root from config or global home

### 8. Deterministic Actions

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Action Registry** | `actions/__init__.py` | Action discovery and registration |
| **Codebase Scanner** | `actions/scan_repo_codebase.py` | Repository structure analysis |
| **Documentation Sync** | `actions/sync_codebase_docs.py`, `actions/sync_system_docs.py` | Doc generation and synchronization |
| **Validation** | `actions/validate_*.py` | Documentation and delivery validation |
| **Media Actions** | `actions/execute_t2i.py`, `actions/execute_i2v.py`, `actions/execute_voiceover.py`, `actions/assemble_video.py` | Content generation pipeline |
| **Scaffold Actions** | `actions/prepare_delivery_scaffold.py`, `actions/finalize_bootstrap.py` | Delivery scaffold setup |

**Key Behaviors:**
- Implements non-coder steps deterministically
- Provides consistent I/O contracts matching coder steps
- Supports workflow-specific operations (video generation, doc sync)

### 9. Backend Integration

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Backend Client** | `backend_client.py` | HTTP API client for backend service |
| **Worker Loop** | `run_agent.py` (worker command) | Poll and claim work from backend |
| **Daemon Supervisor** | `daemon.py` | Child process management, heartbeat emission |

**Key Behaviors:**
- Claims work items from backend queue
- Submits step results with artifact references
- Emits heartbeats for long-running operations
- Manages child process lifecycle in daemon mode

### 10. Documentation Guardrails

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Manifest Tracker** | `documentation_guardrails.py` | Workflow-generated document registry |
| **Protection Enforcer** | `documentation_guardrails.py` | Prevents manual edits to generated docs |
| **Banner Manager** | `documentation_guardrails.py` | Managed-by banner injection |

**Key Behaviors:**
- Tracks documents generated by workflows
- Prevents accidental modification of protected docs
- Manages workflow-generated banners

## Architectural Notes

### Architecture Posture

| Attribute | Value | Notes |
|-----------|-------|-------|
| **Current Profile** | `explicit` | Mature codebase with established patterns |
| **Target Profile** | `standard` | Moving toward ecosystem-standard patterns |
| **Migration Mode** | `in_progress` | Active documentation and standardization effort |
| **DDD Applicability** | Conditional | Domain boundaries defined but not strictly enforced |
| **EDA Applicability** | Conditional | Event-driven patterns in backend integration only |

### Repository vs. Ecosystem Baseline

This repository follows a **repo-selected profile** that diverges from the universal baseline in the following ways:

1. **Workflow-First Organization**: The codebase is organized around workflow families rather than technical layers, reflecting its purpose as a workflow execution engine.

2. **Bootstrap/Runtime Split**: The strict separation between packaged bootstrap source and runtime bundles is specific to this system's deployment model.

3. **Sidecar-Only Communication**: The exclusive use of `meta.json` sidecars for step results is a deliberate v2 design decision that differs from typical request/response patterns.

4. **Global Runner Home**: The use of a global user-directory runtime location (`%USERPROFILE%\.ukbe-runner`) is a Windows-first design choice.

### Component Dependencies

```
run_agent.py (CLI Entry)
    ├── bundle_loader.py
    ├── job_state.py
    ├── step_runner.py
    │   ├── coder_adapters.py
    │   ├── runtime_context.py
    │   └── documentation_guardrails.py
    ├── workflow_router.py
    ├── backend_client.py (worker/daemon modes)
    └── daemon.py (daemon mode)

actions/*.py
    └── runtime_context.py
    └── documentation_guardrails.py
```

### Data Flow Patterns

**Local Mode:**
```
CLI → Load Bundle → Create/Load Job → For Each Step:
    Render Prompt → Invoke Coder → Validate Result → Route Next
```

**Worker Mode:**
```
CLI → Poll Backend → Claim Work → Execute Step → Submit Result → Poll
```

**Daemon Mode:**
```
Daemon → Poll Backend → Spawn Child → Monitor Child → Collect Result → Submit → Heartbeat
```

### Failure Handling Strategy

| Failure Type | Handling | Responsibility |
|--------------|----------|--------------|
| **Coder Timeout** | Exception → Router → Auto-retry or Human-intervention | Router classifies |
| **Meta JSON Missing** | Exception → Router → Fatal or Retry | step_runner raises |
| **Artifact Missing** | Exception → Router → Fatal | step_runner raises |
| **Backend Unavailable** | Retry with backoff → Worker exit | backend_client |
| **Child Process Failure** | Log → Cleanup → Continue polling | daemon |

### Scalability Considerations

| Aspect | Current | Limits |
|--------|---------|--------|
| **Concurrent Jobs** | File-system isolated (one per job_id) | Limited by disk space |
| **Worker Pool** | Single worker per process | Backend-managed queue |
| **Daemon Children** | Configurable max concurrent | System resources |
| **Prompt Size** | Template + artifact context | LLM context windows |

---

*Generated: 2026-07-04T10:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 04_generate_architecture_docs*
*Change ID: 00DOC-GEN-20260704-001*
