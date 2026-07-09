---
template_id: "SYS-03-CA"
managed_by: workflow-generated
generated: "2026-07-09T21:26:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture

## Component Groups

### Core Execution Components

| Component | Module | Responsibility | Lines |
|-----------|--------|----------------|-------|
| **CLI Entry Point** | `run_agent.py` | Argument parsing, command dispatch, orchestration | ~2,300 |
| **Step Runner** | `step_runner.py` | Prompt rendering, coder invocation, sidecar validation | ~2,400 |
| **Workflow Router** | `workflow_router.py` | Post-step routing for approve/reject/failure | ~800 |
| **Job State** | `job_state.py` | Job.json lifecycle, state transitions, retry logic | ~1,800 |

**Interaction Flow**:
```
CLI (run_agent.py) → Step Runner → Coder/Action → Sidecar → Workflow Router → Next Step
                              ↓
                        Job State (persist/retrieve)
```

### Coder Integration Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Coder Adapters** | `coder_adapters.py` | Claude/Codex/Qwen invocation and polling |
| **Model Config** | `model_config.py` | Coder resolution from aliases |
| **Execution Result** | `execution_result.py` | Result type definitions |
| **Execution Request** | `execution_request.py` | Request type definitions |

### Runtime Context Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Runtime Context** | `runtime_context.py` | Active workflow/runtime path context |
| **Bundle Loader** | `bundle_loader.py` | Bootstrap seeding and workflow bundle loading |
| **Constants** | `constants.py` | Centralized artifact path constants |
| **Doc Paths** | `doc_paths.py` | Path resolution helpers |

### Backend Integration Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Backend Client** | `backend_client.py` | HTTP API communication |
| **Daemon** | `daemon.py` | Worker supervision and child process management |
| **Runner Logger** | `runner_logger.py` | Structured logging |
| **Notifications** | `notifications.py`, `notification_manager.py` | Pushover notifications |

### Deterministic Actions

The `agent_runner_v2/actions/` package contains 29 deterministic runner actions:

| Category | Actions |
|----------|---------|
| **Documentation** | `validate_delivery_docs.py`, `validate_codebase_docs.py`, `sync_system_docs.py`, `sync_codebase_docs.py` |
| **Architecture Site** | `generate_site.py`, `publish_architecture_site.py`, `validate_*_site.py` |
| **Bootstrap** | `prepare_delivery_scaffold.py`, `finalize_bootstrap.py`, `scan_repo_codebase.py` |
| **Media** | `execute_t2i.py`, `execute_i2v.py`, `execute_voiceover.py`, `assemble_video.py` |
| **Artifacts** | `copy_artifact.py`, `promote_artifact.py`, `archive_previous_version.py` |

### Documentation Guardrails

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Documentation Guardrails** | `documentation_guardrails.py` | Generated doc manifest and protection |
| **System Docs** | `system_docs.py` | System documentation utilities |
| **Codebase Docs** | `codebase_docs.py` | Codebase documentation utilities |
| **Architecture Site** | `architecture_site.py` | Site generation utilities |

## Architectural Notes

### Architecture Profile

**Current Profile**: `explicit`
**Target Profile**: `universal-bootstrap`
**Migration Mode**: `maintenance`

This repository follows the **explicit** architecture profile, meaning:
- Architecture decisions are explicitly documented
- Contracts are strictly enforced in code
- Generated documents are protected from manual edits
- Test coverage requirements are mandatory

The `universal-bootstrap` target profile indicates the system is designed as a reusable workflow orchestration platform, not a one-off tool.

### DDD and EDA Status

| Pattern | Status | Notes |
|---------|--------|-------|
| **Domain-Driven Design (DDD)** | Conditional | Used for workflow domain modeling, not universal |
| **Event-Driven Architecture (EDA)** | Conditional | Job state changes emit notifications, not core pattern |
| **Layered Architecture** | Applied | Clear separation between CLI, core, and adapters |
| **Hexagonal Architecture** | Partial | Coder adapters provide abstraction, bundles are runtime dependencies |

**Rationale**: DDD and EDA are conditional rather than universal standards because:
- The workflow domain has clear bounded contexts (delivery, codebase, system)
- Event notifications are operational, not business-logic critical
- The system prioritizes explicit control flow over event choreography

### Dependency Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                           CLI Layer                              │
│                      (run_agent.py, *.bat)                       │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Core Layer                               │
│  (step_runner.py, workflow_router.py, job_state.py)          │
└─────────────────────────────────────────────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Coder Layer    │  │  Action Layer  │  │  Runtime Layer  │
│ (coder_adapters)│  │   (actions/)   │  │ (runtime_ctx,   │
│                 │  │                │  │  bundle_loader) │
└─────────────────┘  └─────────────────┘  └─────────────────┘
              │                   │                   │
              ▼                   ▼                   ▼
        ┌──────────┐       ┌──────────┐       ┌──────────┐
        │ External │       │    FS    │       │   FS/    │
        │  Coders  │       │ (artifacts)│    │  Config  │
        └──────────┘       └──────────┘       └──────────┘
```

### Component Boundaries

**Strict Separation**:
- `step_runner.py` only does prompt rendering and sidecar validation
- `workflow_router.py` only makes routing decisions
- `job_state.py` only manages job.json persistence
- `coder_adapters.py` only invokes external coders
- `actions/` only contains deterministic side-effect-free (relative to workflow state) actions

**No module exceeds ~2,500 lines**; responsibilities are narrowly scoped.

### Bootstrap/Runtime Separation

| Aspect | Bootstrap Source | Runtime Bundle |
|--------|-----------------|----------------|
| **Location** | `agent_runner_v2/bootstrap/` | `~/.ukbe-runner/workflows/` |
| **Purpose** | Package-local seed/template | Active execution source |
| **Updates** | Via code changes + sync | Used by running workflows |
| **Loading** | `bundle_loader.py` | `runtime_context.py` |

**Critical**: Runtime loads from global runner home, not repo tree. Changes to bootstrap must be synced via `sync-workflows-to-backend.bat` or `ukbe-run-agent init`.

### v2 Contract Enforcement

Key architectural differences from v1:

| Aspect | v1 | v2 |
|--------|-----|-----|
| Sidecar | Optional fallback | Only communication channel |
| Markdown writes | Runner writes metadata | Runner never writes markdown |
| Recovery | Disk recovery functions | Explicit failure routing |
| Content analysis | Runner extracts blocking issues | Coder owns content analysis |
| Pre-invocation | Sidecar written before coder | Sidecar only from coder |

This strict contract enables:
- Clear separation of concerns
- Deterministic replay
- Simplified reasoning about state

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 04_generate_architecture_docs*
