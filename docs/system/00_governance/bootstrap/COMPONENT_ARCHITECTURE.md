---
template_id: "SYS-03-CA"
title: "Component Architecture - agent-runner-v2"
status: "active"
generated: "2026-07-10T14:20:05+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture

## Architecture Profile

| Attribute | Value |
|-----------|-------|
| **Current Profile** | `provisional` → `structured` (migration in progress) |
| **Target Profile** | `structured` (post-plugin migration) |
| **Migration Mode** | `in_progress` |
| **Repo State** | `explicit` |

This repository is following a **targeted migration path** rather than the universal baseline. Domain-Driven Design (DDD) and Event-Driven Architecture (EDA) are **conditional standards** applied where appropriate, not universal mandates.

## Component Groups

### Core Execution Layer

| Component | File(s) | Responsibility | Lines |
|-----------|---------|----------------|-------|
| **CLI Entry** | `run_agent.py` | Orchestration, argument parsing, mode dispatch | 2,374 |
| **Step Runner** | `step_runner.py` | Prompt rendering, coder/action invocation, sidecar validation | 2,674 |
| **Workflow Router** | `workflow_router.py` | Post-step routing (approve/reject/failure) | 787 |
| **Job State** | `job_state.py` | `job.json` lifecycle, state management | 1,806 |

### Coder Integration Layer

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Coder Adapters** | `coder_adapters.py` | Claude/Codex/Qwen invocation and polling (1,079 lines) |
| **Model Config** | `model_config.py` | Model resolution and alias handling |
| **Execution Request/Result** | `execution_request.py`, `execution_result.py` | Typed dataclasses for execution contracts |

### Action Layer

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Actions Package** | `actions/*.py` (28 modules) | Deterministic runner actions |
| **Key Actions** | `scan_repo_codebase.py`, `sync_codebase_docs.py`, `validate_*.py` | Code scanning, documentation sync, validation |
| **Site Generation** | `generate_site.py`, `publish_architecture_site.py` | HTML site generation and publishing |
| **Media Pipeline** | `execute_t2i.py`, `execute_i2v.py`, `execute_voiceover.py`, `assemble_video.py` | Image/video/voice generation |

### Runtime Context Layer

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Runtime Context** | `runtime_context.py` | Active workflow/runtime path context, PathProxy pattern |
| **Bundle Loader** | `bundle_loader.py` | Bootstrap seeding and workflow bundle loading |
| **Constants** | `constants.py` | Centralized artifact keys and paths (1,342 lines) |

### Backend Integration Layer

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Backend Client** | `backend_client.py` | HTTP/WebSocket communication with UKBE backend |
| **Daemon** | `daemon.py` | Workstation supervisor, work claiming, child process spawning |
| **Runner Logger** | `runner_logger.py` | Structured logging for runner operations |

### Workflow Definition Layer

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Template Groups** | `bootstrap/workflows/default/template_groups.py` | Monolithic workflow registry (2,453 lines) |
| **Plugin System** | `workflow_packages/` | Plugin-based workflow bundles (migration target) |
| **Workflow Specs** | `workflow_specs.py`, `workflow_spec_commands.py` | Workflow specification handling |

### Documentation Layer

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Documentation Guardrails** | `documentation_guardrails.py` | Validation and protection for generated docs |
| **System/Codebase Docs** | `system_docs.py`, `codebase_docs.py` | Documentation generation utilities |
| **Architecture Site** | `architecture_site.py`, `site_styles.py` | HTML site generation |

### Notification Layer

| Component | File(s) | Responsibility |
|-----------|---------|----------------|
| **Notifications** | `notifications.py`, `notification_manager.py` | Pushover integration, notification dispatch |

## Dependencies

### Internal Dependencies

```
run_agent.py
    ├── step_runner.py
    │   ├── coder_adapters.py
    │   ├── actions/*.py
    │   └── constants.py
    ├── workflow_router.py
    ├── job_state.py
    ├── runtime_context.py
    └── bundle_loader.py
```

### External Dependencies

| Category | Dependencies |
|----------|--------------|
| **HTTP/Networking** | `requests`, `httpx` |
| **CLI** | `argparse`, `colorama` |
| **Data** | `pydantic`, `dataclasses` |
| **Async** | `asyncio`, `aiohttp` |
| **Media** | `Pillow`, `ffmpeg` (external) |

## Architectural Notes

### Provisional Elements (Pre-Migration)

1. **Monolithic Template Groups** (`template_groups.py`, 2,453 lines)
   - 21 workflow families defined in a single file
   - Hardcoded step sequences and routing rules
   - Migration target: plugin-based workflow packages

2. **Dual-Path Discovery**
   - Global runner home (`%USERPROFILE%\.ukbe-runner\`) first
   - Local project fallback
   - Adds complexity during transition period

### Structured Elements (Post-Migration Foundation)

1. **Centralized Constants** (`constants.py`)
   - Single source of truth for all artifact paths
   - Pre-computed path constants, zero hardcoded strings
   - Section requirements for validation

2. **Strict Sidecar Contract** (v2)
   - `meta.json` is the sole communication channel
   - No markdown write-backs, no silent recovery
   - Explicit routing for all outcomes

3. **Deterministic Actions**
   - 28 well-defined action modules
   - Separated from LLM-based coder steps
   - Testable in isolation

4. **Comprehensive Test Coverage**
   - Unit tests: 45+ pure logic tests (isolated)
   - Integration tests: real files, subprocesses
   - Split by `tests/unit/` and `tests/integration/`

### Migration Path

| Phase | From | To | Status |
|-------|------|-----|--------|
| 1 | Hardcoded paths | Centralized constants | ✅ Complete |
| 2 | Inline sidecar instructions | Auto-injection | ✅ Complete |
| 3 | Monolithic template_groups.py | Plugin packages | 🔄 In Progress |
| 4 | v1 sidecar contract | v2 strict contract | ✅ Complete |

### Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Bootstrap/Runtime Duality** | Allows packaged updates while preserving local modifications | Requires explicit sync via `init` |
| **Daemon Spawns Subprocesses** | Code changes picked up automatically | Process overhead per step |
| **Windows Primary** | Original deployment target | Unix/WSL support secondary |
| **Pushover for Notifications** | Simple, reliable mobile push | Vendor lock-in |
| **JSON Sidecar over Markdown** | Unambiguous structured results | Requires strict schema |

### Component Boundaries

| Boundary | Enforcement |
|----------|-------------|
| **Coder/Action Split** | `step_runner.py` routes to either `coder_adapters.py` or `actions/*.py` |
| **Bootstrap/Runtime** | `bundle_loader.py` manages seeding and loading separately |
| **Core/Backend** | Backend client is optional; local mode works standalone |
| **Generation/Validation** | Guardrails protect workflow-generated documents |

### Related Documents

| Document | Purpose |
|----------|---------|
| [SYSTEM_CONTEXT.md](SYSTEM_CONTEXT.md) | External systems and interfaces |
| [DECISION_LOG.md](DECISION_LOG.md) | Key architectural decisions |
| [SYSTEM_FILE_STRUCTURE.md](SYSTEM_FILE_STRUCTURE.md) | Repository organization |
