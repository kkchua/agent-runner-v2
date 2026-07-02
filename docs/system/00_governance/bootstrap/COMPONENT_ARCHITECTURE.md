---
title: "Component Architecture: agent-runner-v2"
template_id: "SYS-03-CA"
status: "active"
managed_by: workflow-generated
created: "2026-07-02T20:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Component Architecture: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

## 1. High-Level Component Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              CLI Layer                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        run_agent.py (2,141 lines)                     │  │
│  │                    CLI Entry, Orchestration, Command Routing          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           Core Engine Layer                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           │
│  │  step_runner.py  │  │ workflow_router  │  │   job_state.py   │           │
│  │   (2,000 lines)  │  │    (774 lines)   │  │  (1,781 lines)   │           │
│  │  Prompt Render,  │  │  Post-Step       │  │  Job Lifecycle,  │           │
│  │  Sidecar Validate│  │  Routing Logic   │  │  State Machine   │           │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘           │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          Adapter Layer                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           │
│  │ coder_adapters.py  │  │ runtime_context  │  │  bundle_loader   │           │
│  │  (1,013 lines)   │  │   (281 lines)    │  │   (188 lines)    │           │
│  │ LLM Invocation,  │  │  Path Resolution,│  │  Bundle Seeding,│           │
│  │ Result Polling     │  │  Context Management│  Workflow Loading │           │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘           │
│  ┌──────────────────┐  ┌──────────────────┐                                │
│  │ backend_client.py  │  │   daemon.py      │                                │
│  │   (~200 lines)   │  │   (420 lines)    │                                │
│  │ HTTP API Client    │  │  Worker Supervisor│                               │
│  └──────────────────┘  └──────────────────┘                                │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          Action Layer (16 Actions)                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  scan_repo  │ │ promote_artifact│ │ copy_artifact│ │  submit_     │          │
│  │  _codebase  │ │   _init      │ │             │ │  comfyui     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  execute_   │ │  execute_   │ │  execute_   │ │  assemble_   │          │
│  │    t2i      │ │    i2v      │ │  voiceover  │ │   video      │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  sync_      │ │  sync_      │ │  validate_  │ │  validate_   │          │
│  │ codebase_   │ │ system_docs │ │ codebase_   │ │ delivery_    │          │
│  │   docs      │ │             │ │   docs      │ │   docs       │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  validate_  │ │  prepare_   │ │  finalize_  │ │              │          │
│  │ system_docs │ │delivery_    │ │ bootstrap   │ │              │          │
│  │             │ │ scaffold    │ │             │ │              │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                       External Systems Layer                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Claude    │ │    Codex    │ │    Qwen     │ │   Backend   │          │
│  │     API     │ │     API     │ │    Code     │ │     API     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
└────────────────────────────────────────────────────────────────────────────┘
```

## 2. Core Components

### 2.1 run_agent.py (2,141 lines)

**Responsibilities:**
- CLI entry point and command parsing (`init`, `run`, `worker`, `daemon`, `execute-step`)
- Top-level orchestration flow
- Workflow bundle resolution
- Job state initialization and loading
- Pre-flight artifact validation
- Integration between step_runner, workflow_router, and job_state

**Key Functions:**
- `parse_args()` — Command-line argument parsing
- `run()` — Main execution loop
- `run_worker()` — Backend worker mode
- `run_daemon()` — Daemon supervisor mode

### 2.2 step_runner.py (2,000 lines)

**Responsibilities:**
- Prompt template rendering with Jinja2
- Coder invocation via `coder_adapters`
- Sidecar (`meta.json`) reading and validation
- Artifact path resolution and existence checks
- Protected document snapshotting
- Usage data extraction and recording

**Key Functions:**
- `run_step()` — Main step execution entry point
- `render_prompt()` — Template rendering with context
- `run_action()` — Deterministic action execution
- `build_context()` — Context assembly for templating

### 2.3 workflow_router.py (774 lines)

**Responsibilities:**
- Post-step routing logic
- Review/refine/replan loop management
- Failure classification and routing
- Step advancement and state transitions
- Decision recording (model vs human)

**Key Functions:**
- `route_after_step()` — Normal step completion routing
- `route_after_failure()` — Failure recovery routing
- `advance_step()` — Step progression logic
- `classify_failure()` — Failure type determination

### 2.4 job_state.py (1,781 lines)

**Responsibilities:**
- Job JSON schema definition (v6)
- Job lifecycle management (create, load, save, migrate)
- State machine enforcement
- Artifact tracking
- Retry history recording
- Usage summary aggregation

**Key Types:**
- Job states: `IN_PROGRESS`, `WAITING_FOR_AUTO_RETRY`, `WAITING_FOR_HUMAN_INTERVENTION`, `WAITING_FOR_HUMAN_APPROVAL`, `COMPLETED`, `FAILED`
- Decision sources: `MODEL`, `HUMAN`
- Control classes: `AUTO_RETRYABLE`, `HUMAN_RETRY_REQUIRED`, `FATAL`

## 3. Adapter Components

### 3.1 coder_adapters.py (1,013 lines)

**Responsibilities:**
- LLM provider abstraction (Claude, Codex, Qwen)
- Process invocation and management
- Result polling with timeout
- Sidecar validation
- Usage data extraction
- Model alias resolution

**Key Classes:**
- `CoderInvocationError` — Exception for coder failures
- `UsageData` — Token/cost tracking
- `InvocationResult` — Complete invocation outcome

### 3.2 runtime_context.py (281 lines)

**Responsibilities:**
- Process-local runtime context
- Path resolution (repo vs runtime)
- Workflow module management
- Delivery root override
- PathProxy for lazy evaluation

**Key Constants:**
- `PACKAGE_ROOT` — Package installation directory
- `GLOBAL_RUNNER_HOME` — `%USERPROFILE%\.ukbe-runner`
- `DEFAULT_WORKFLOW_NAME` — "default"

### 3.3 bundle_loader.py (188 lines)

**Responsibilities:**
- Workflow bundle loading
- Bootstrap seeding on `init`
- Global vs workspace workflow resolution
- Project configuration management

**Key Functions:**
- `init_workspace()` — Initialize runner home
- `load_workflow_module()` — Load template_groups.py
- `resolve_workflow_root()` — Determine active workflow

### 3.4 backend_client.py (~200 lines)

**Responsibilities:**
- Backend API communication
- Work claiming
- Step result submission
- Health checking

## 4. Action Components

The `actions/` package contains 16 deterministic runner actions:

| Action | Purpose | Category |
|--------|---------|----------|
| `scan_repo_codebase.py` | Repository scanning and documentation baseline | Documentation |
| `sync_codebase_docs.py` | Codebase documentation synchronization | Documentation |
| `sync_system_docs.py` | System documentation synchronization | Documentation |
| `validate_codebase_docs.py` | Codebase documentation validation | Validation |
| `validate_delivery_docs.py` | Delivery documentation validation | Validation |
| `validate_system_docs.py` | System documentation validation | Validation |
| `prepare_delivery_scaffold.py` | Delivery scaffold preparation | Scaffold |
| `finalize_bootstrap.py` | Bootstrap finalization | Scaffold |
| `promote_artifact.py` | Artifact promotion between stages | Artifact |
| `promote_init.py` | Initiative file promotion | Artifact |
| `copy_artifact.py` | Artifact copying | Artifact |
| `submit_comfyui.py` | ComfyUI workflow submission | External |
| `execute_t2i.py` | Text-to-image execution | External |
| `execute_i2v.py` | Image-to-video execution | External |
| `execute_voiceover.py` | Voiceover generation execution | External |
| `assemble_video.py` | Video assembly from components | External |

## 5. Supporting Components

### 5.1 Schema and State

| Module | Purpose | Lines |
|--------|---------|-------|
| `action_result.py` | Action result dataclasses | ~50 |
| `artifact_paths.py` | Artifact path computation | ~100 |
| `exceptions.py` | Custom exceptions | ~80 |
| `execution_request.py` | Backend request parsing | ~60 |
| `execution_result.py` | Backend result formatting | ~50 |
| `runner_actions.py` | Action registry | ~40 |

### 5.2 Commands

| Module | Purpose | Lines |
|--------|---------|-------|
| `approve_commands.py` | Step approval handling | ~150 |
| `engine_commands.py` | Engine subcommands | ~200 |
| `submit_commands.py` | Submission commands | ~180 |
| `submitter.py` | Backend submission | ~120 |
| `workflow_spec_commands.py` | Workflow spec management | ~100 |

### 5.3 Documentation and Guardrails

| Module | Purpose | Lines |
|--------|---------|-------|
| `documentation_guardrails.py` | Protected doc tracking | ~250 |
| `system_docs.py` | System docs helpers | ~150 |
| `codebase_docs.py` | Codebase docs helpers | ~200 |
| `bundle_taxonomy.py` | Bundle organization | ~100 |

### 5.4 Tools

| Module | Purpose | Lines |
|--------|---------|-------|
| `tools/agent_tools.py` | Progress tracking utilities | ~80 |

## 6. Component Dependencies

```
run_agent.py
    ├── step_runner.py
    │   ├── coder_adapters.py
    │   ├── runtime_context.py
    │   └── artifact_paths.py
    ├── workflow_router.py
    │   └── job_state.py
    ├── job_state.py
    │   └── runtime_context.py
    ├── bundle_loader.py
    │   ├── runtime_context.py
    │   └── bundle_taxonomy.py
    └── backend_client.py

step_runner.py
    ├── coder_adapters.py
    ├── runtime_context.py
    ├── artifact_paths.py
    └── exceptions.py

workflow_router.py
    ├── job_state.py
    ├── coder_adapters.py
    └── exceptions.py

job_state.py
    ├── runtime_context.py
    └── documentation_guardrails.py

coder_adapters.py
    └── runtime_context.py

bundle_loader.py
    ├── runtime_context.py
    └── bundle_taxonomy.py

actions/*.py
    ├── runtime_context.py
    ├── artifact_paths.py
    └── (various helpers)
```

## 7. Design Patterns

### 7.1 Command Pattern
Actions are self-contained commands with:
- Single entry function
- Explicit inputs/outputs
- No side effects outside artifact production

### 7.2 State Machine
Job state follows a strict state machine:
```
CREATED → IN_PROGRESS → [WAITING_FOR_*] → COMPLETED
                              ↓
                           FAILED
```

### 7.3 Strategy Pattern
Coder adapters use strategy pattern for multi-provider support:
- Common interface across Claude, Codex, Qwen
- Provider-specific implementation details hidden

### 7.4 Template Method
Step execution follows template method:
1. Pre-flight (validation)
2. Prompt rendering
3. Coder invocation
4. Result reading
5. Artifact validation
6. State update

### 7.5 Proxy Pattern
`PathProxy` provides lazy path resolution:
- Paths evaluated at access time, not creation
- Supports runtime context changes

## 8. Component Boundaries

### 8.1 Runner vs Coder Boundary

| Aspect | Runner | Coder |
|--------|--------|-------|
| **Owns** | Job state, routing, actions | Content generation, file edits |
| **Produces** | `meta.json` sidecar | File modifications, code |
| **Decides** | Step advancement | Content quality, blocking issues |
| **Communication** | Sidecar only | Sidecar + files |

### 8.2 Runner vs Backend Boundary

| Aspect | Runner | Backend |
|--------|--------|---------|
| **Owns** | Step execution | Work distribution |
| **Produces** | Step results | Step requests |
| **Decides** | Execution success | Job routing |
| **Communication** | HTTP API | HTTP API |

### 8.3 Bootstrap vs Runtime Boundary

| Aspect | Bootstrap | Runtime |
|--------|-----------|---------|
| **Location** | Package directory | User home directory |
| **Updates** | Package releases | `init` command |
| **Used by** | Seeding | Actual execution |
| **Version** | Package | User-managed |

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs`*
