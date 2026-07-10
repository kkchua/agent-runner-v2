---
template_id: "SYS-03-CA"
title: "Component Architecture - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:52:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture: agent-runner-v2

## Architecture Profile

| Field | Value |
|-------|-------|
| `current_profile` | `provisional` |
| `target_profile` | `explicit` (delivery scaffold governance model) |
| `migration_mode` | `bootstrap-in-progress` |
| `repo_state` | `provisional` |

### Architecture Standard Alignment

This repository follows a **provisional** architecture standard with explicit design patterns:

- **No universal DDD**: Domain-driven design is applied selectively where workflow domains have clear boundaries
- **No universal EDA**: Event-driven architecture is used for backend communication and notifications, not as a universal pattern
- **Repo-selected profile**: The codebase demonstrates explicit architecture through strong module separation and contract-based design

## Component Groups

### Core Execution Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Core Execution Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   run_agent.py  │───▶│  step_runner.py │───▶│ workflow_    │ │
│  │   CLI Entry     │    │  Step Execution │    │ router.py    │ │
│  │   2,308 lines   │    │  2,662 lines    │    │ 787 lines    │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                      │                    │        │
│           ▼                      ▼                    ▼        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   job_state.py  │◀──▶│ runtime_context│◀──▶│ constants.py │ │
│  │   State Mgmt    │    │   Context       │    │ 1,333 lines  │ │
│  │   1,806 lines   │    │   301 lines     │    │ Path constants│ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### run_agent.py (CLI Entry)
- **Responsibility**: CLI parsing, workflow bundle loading, job lifecycle orchestration
- **Key Functions**: `parse_args()`, `cmd_run()`, `cmd_execute_step()`, `cmd_worker()`
- **Patterns**: Command pattern, factory pattern for step execution
- **Dependencies**: All other core modules

#### step_runner.py (Step Execution)
- **Responsibility**: Prompt rendering, coder invocation, artifact validation, meta.json handling
- **Key Functions**: `run_step()`, `render_prompt()`, `run_action()`, `validate_artifacts()`
- **Patterns**: Template method, strategy pattern (coder vs action)
- **Critical Contract**: Meta.json is the ONLY communication channel

#### workflow_router.py (Routing)
- **Responsibility**: Post-step routing, retry logic, approval handling, failure routing
- **Key Functions**: `route_after_step()`, `route_after_failure()`
- **Patterns**: State machine, chain of responsibility
- **Exit Codes**: 0=continue, 1=intervention, 2=fatal

#### job_state.py (State Management)
- **Responsibility**: Job.json lifecycle, status transitions, retry tracking, artifact binding
- **Key Functions**: `create_job()`, `load_job()`, `save_job()`, `advance_step()`, `set_job_status()`
- **Patterns**: Repository pattern, state machine
- **Schema Version**: 6 (v2 runner)

### Adapter Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Adapter Layer                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │ coder_adapters  │    │ backend_client  │    │ daemon.py    │ │
│  │  (3 coders)     │    │                 │    │              │ │
│  │ - Claude        │    │ - WebSocket     │    │ - Supervisor │ │
│  │ - Codex         │    │ - HTTP API      │    │ - Polling    │ │
│  │ - Qwen          │    │ - Events        │    │ - Worker     │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │  notifications  │    │ notification_  │                     │
│  │                 │    │   manager.py   │                     │
│  │ - Pushover      │    │                 │                     │
│  │ - Email         │    │ - Step events  │                     │
│  │ - Console       │    │ - Workflow events│                    │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### coder_adapters.py
- **Responsibility**: LLM invocation abstraction, response handling, error normalization
- **Key Functions**: `invoke_coder()`, `resolve_coder()`, `dataclass_dict()`
- **Supported Models**: Claude 4, Codex, Qwen aliases

#### backend_client.py
- **Responsibility**: Backend API communication, event streaming, job synchronization
- **Key Functions**: `BackendClient.request()`, `stream_events()`
- **Protocols**: HTTP REST, WebSocket for events

### Action Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Actions Layer (29 modules)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Validation Actions          Documentation Actions               │
│  ┌──────────────────┐       ┌──────────────────┐              │
│  │ validate_delivery│       │ sync_codebase    │              │
│  │ validate_system  │       │ sync_system_docs │              │
│  │ validate_arch    │       │ scan_repo        │              │
│  │ validate_*_site  │       │ generate_site    │              │
│  └──────────────────┘       └──────────────────┘              │
│                                                                  │
│  Bootstrap Actions           Workflow Actions                    │
│  ┌──────────────────┐       ┌──────────────────┐              │
│  │ finalize_bootstrap│       │ prepare_delivery │              │
│  │ promote_artifact │       │ copy_artifact    │              │
│  │ promote_init     │       │ execute_*        │              │
│  └──────────────────┘       └──────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Action Categories

| Category | Actions | Purpose |
|----------|---------|---------|
| **Validation** | 10 actions | Document and site validation |
| **Documentation** | 5 actions | Doc sync, scanning, generation |
| **Bootstrap** | 3 actions | Bundle finalization, promotion |
| **Media** | 4 actions | Image/video/audio execution |
| **Utility** | 7 actions | Copy, archive, submit |

### Bootstrap Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Bootstrap Layer                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  bundle_loader  │    │ template_groups │    │   prompts/   │ │
│  │                 │    │    .py          │    │              │ │
│  │ - Core bundles  │    │ - 290+ steps    │    │ - 290+ files │ │
│  │ - Workflow root │    │ - 21 workflows  │    │ - 21 dirs    │ │
│  │ - Seeding       │    │ - TEMPLATES     │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### bundle_loader.py
- **Responsibility**: Bootstrap bundle loading, workflow resolution, project initialization
- **Key Functions**: `init_workspace()`, `load_workflow_module()`, `resolve_workflow_root()`
- **Pattern**: Plugin architecture for workflow modules

#### template_groups.py
- **Responsibility**: Workflow step definitions, template configurations, artifact mappings
- **Size**: 2,453 lines, 21 workflow families, 290+ steps
- **Key Structures**: `TEMPLATES`, `ARTIFACT_KEYS`, `REFERENCE_FILES`

### Documentation Components

```
┌─────────────────────────────────────────────────────────────────┐
│                   Documentation Layer                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │ documentation_  │    │   doc_paths.py  │    │ artifact_    │ │
│  │   guardrails    │    │                 │    │   paths.py   │ │
│  │                 │    │ - Path helpers  │    │              │ │
│  │ - Protection    │    │ - Rel paths     │    │ - Compute    │ │
│  │ - Validation    │    │ - Templates     │    │ - Resolve    │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ codebase_docs.py│    │  system_docs.py  │                     │
│  │                 │    │                  │                     │
│  │ - Inventory     │    │ - System docs    │                     │
│  │ - Modules       │    │ - Validation     │                     │
│  │ - Components    │    │ - Sync           │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Dependency Map

```
                    ┌──────────────┐
                    │    CLI       │
                    │  run_agent   │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ step_runner│  │ job_state  │  │   router   │
    └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │               │               │
          ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  adapters  │  │   state    │  │   actions  │
    │  backend   │  │   context  │  │            │
    └────────────┘  └────────────┘  └────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                    ┌────────────┐
                    │  constants │
                    │   (SSOT)   │
                    └────────────┘
```

## Component Boundaries

| Component | Boundary | Enforced By |
|-----------|----------|-------------|
| **Core** | Execution flow | Function signatures, dataclasses |
| **Adapters** | External systems | Interface abstraction |
| **Actions** | Deterministic ops | Module separation, pure functions |
| **Bootstrap** | Workflow definitions | Module loading, path resolution |
| **Docs** | Path/protection | constants.py, guardrails |

## Architectural Notes

### v2 Contract Differences

| Aspect | v1 | v2 |
|--------|-----|-----|
| Communication | Multiple channels | Meta.json only |
| Recovery | Silent recovery functions | Explicit routing |
| Metadata writes | Runner writes markdown | Runner only reads |
| Sidecar | Optional | Mandatory |
| Failure handling | Automatic retry | Explicit routing |

### Centralized Constants Pattern

The `constants.py` module (1,333 lines) provides:
- **Single source of truth** for all paths
- **Layered constants**: FOLDER_KEY → ARTIFACT_KEY → ARTIFACT_PATH
- **Zero hardcoded strings** in path construction
- **REFERENCE_FILES** dictionary for runtime lookup

### Step Runner Contract

```
Input: step_config, state, context
  │
  ▼
Render prompt (template substitution)
  │
  ▼
Invoke coder OR run action
  │
  ▼
Read meta.json (MANDATORY)
  │
  ▼
Validate artifacts (produces list)
  │
  ▼
Return StepResult(status, remark, artifacts)
```

### Review/Refine Loop Pattern

```
Generate ──▶ Review ──▶ Decision
                │
           REJECTED
                │
                ▼
            Refine ──▶ (loop back)
```

Max iterations enforced before human intervention.

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs` on 2026-07-10T09:52:38+08:00*
