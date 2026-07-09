---
template_id: "SYS-03-CA"
title: "Component Architecture - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:26:47+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture: agent-runner-v2

## Component Groups

### Core Execution Components

| Component | Module | Responsibility | Key Collaborators |
|-----------|--------|----------------|-------------------|
| **CLI Entry** | `run_agent.py` | Argument parsing, command dispatch, orchestration | All components |
| **Step Runner** | `step_runner.py` | Prompt rendering, coder invocation, sidecar validation | workflow_router, coder_adapters |
| **Workflow Router** | `workflow_router.py` | Post-step routing based on sidecar status | job_state, step_runner |
| **Job State** | `job_state.py` | Job.json lifecycle, schema migration, preflight | runtime_context |
| **Runtime Context** | `runtime_context.py` | Process-local context, path resolution | constants |

### Coder Integration Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Coder Adapters** | `coder_adapters.py` | LLM invocation (Claude/Codex/Qwen), subprocess management, polling |
| **Model Config** | `model_config.py` | Model resolution, alias mapping |
| **Execution Request/Result** | `execution_request.py`, `execution_result.py` | Request/response schemas |

### Action Components (25+ modules)

| Category | Actions | Purpose |
|----------|---------|---------|
| **Documentation** | `sync_codebase_docs`, `sync_system_docs`, `validate_*_docs` | Codebase and system documentation generation/validation |
| **Architecture Site** | `publish_architecture_site`, `validate_architecture_site`, `generate_site` | HTML site generation and publishing |
| **Delivery Scaffold** | `prepare_delivery_scaffold`, `finalize_bootstrap` | Workflow setup and initialization |
| **Content Generation** | `execute_t2i`, `execute_i2v`, `execute_voiceover`, `assemble_video` | Image/video/audio generation workflows |
| **Utility** | `copy_artifact`, `promote_artifact`, `archive_previous_version` | Artifact lifecycle management |
| **ComfyUI** | `submit_comfyui` | External generation service integration |

### Bootstrap Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Bundle Loader** | `bundle_loader.py` | Bootstrap seeding, workflow bundle loading, workspace initialization |
| **Template Groups** | `template_groups.py` | Workflow definitions, step configurations, artifact mappings |
| **Workflow Specs** | `workflow_specs.py` | Specification loading and validation |

### Support Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| **Constants** | `constants.py` | Centralized artifact keys, folder keys, path constants |
| **Doc Paths** | `doc_paths.py` | Path resolution for documentation artifacts |
| **Artifact Paths** | `artifact_paths.py` | Artifact path computation |
| **Documentation Guardrails** | `documentation_guardrails.py` | Validation rules, generated doc tracking |
| **Notifications** | `notifications.py`, `notification_manager.py` | Pushover integration, step/workflow notifications |
| **Backend Client** | `backend_client.py` | Backend API communication |
| **Runner Logger** | `runner_logger.py` | Structured logging |
| **Daemon** | `daemon.py` | Workstation supervisor, continuous operation |

## Component Dependencies

```
┌──────────────────────────────────────────────────────────────┐
│                         CLI Layer                           │
│                    run_agent.py (orchestrator)               │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                     Execution Core                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ step_runner │──│workflow_router│──│    job_state      │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
│         │                                               │   │
│         ▼                                               │   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │coder_adapters│  │   runtime_   │──│     constants       │   │
│  │             │  │   context    │  │   (centralized)     │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                     Action Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ sync_*_docs │  │ validate_*  │  │ publish_*   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │execute_*    │  │prepare_*    │  │ copy_*      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                    Bootstrap Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │bundle_loader│  │template_    │  │   workflow_specs    │   │
│  │             │  │  groups     │  │                     │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Architectural Notes

### Architecture Posture

This repository follows an **explicit architecture posture** with clear boundaries:

| Aspect | Current State | Target |
|--------|---------------|--------|
| **Profile** | `explicit-v2-workflow-runner` | `mature-multi-tenant-orchestrator` |
| **Migration Mode** | Incremental | — |
| **Repo State** | Explicit (declared standards) | — |

### Key Design Patterns

1. **Explicit over Implicit**
   - All routing decisions explicit; no silent fallbacks
   - REVIEW_DECISIONS, HUMAN_DECISIONS, CONTROL_CLASSES define all state transitions

2. **Contract-First**
   - meta.json schema is the API; no ad-hoc communication channels
   - Strict sidecar validation; hard failures route explicitly

3. **Single Responsibility**
   - step_runner handles execution; workflow_router handles routing
   - job_state manages persistence; runtime_context provides environment

4. **Centralized Constants**
   - All paths defined in `constants.py`; zero hardcoded strings
   - ARTIFACT_KEY_* and FOLDER_KEY_* constants for all artifacts

5. **Bootstrap Seeding**
   - Package provides seed; runtime is source of truth
   - Clear separation between bootstrap source and runtime bundles

### v2 Execution Contract

| Rule | Implementation |
|------|----------------|
| **No markdown write-backs** | Runner never modifies generated markdown files |
| **No pre-invocation sidecar writes** | Sidecar is written by coder, not runner |
| **No silent recovery** | Hard failures route explicitly through failure handling |
| **meta.json is sole channel** | No stdout JSON parsing fallbacks |
| **Deterministic artifact paths** | All paths computed from centralized constants |

### Domain-Driven Design (DDD) Status

**DDD is NOT a universal standard** for this codebase. The repository uses:

- **Functional decomposition** by responsibility (not bounded contexts)
- **Module-level organization** with 67 Python modules grouped by purpose
- **Workflow-oriented semantics** rather than domain entities

DDD patterns are applied only where they provide clear value:
- Artifact keys as value objects (constants.py)
- State transitions as explicit domain logic (job_state.py)

### Event-Driven Architecture (EDA) Status

**EDA is NOT implemented**. The system uses:

- **Synchronous step execution** with explicit state transitions
- **Polling-based completion detection** (not event callbacks)
- **File-based sidecar communication** (not message queues)

### Extension Points

| Extension | Implementation |
|-----------|----------------|
| **New Actions** | Add to `actions/` and register in `__init__.py` |
| **New Workflows** | Add to `template_groups.py` and `prompts/<workflow>/` |
| **New Coder Adapters** | Extend `coder_adapters.py` with new provider |
| **Custom Notifications** | Pluggable via `notification_manager.py` |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 04_generate_architecture_docs | Change: 00DOC-20260708-78fb419e*
