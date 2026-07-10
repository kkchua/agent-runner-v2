---
template_id: "SYS-00-SO"
title: "System Overview"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview

## Purpose

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine. It enables structured multi-step workflow execution across multiple LLM backends (Claude, Codex, Qwen), with built-in review loops, retry mechanisms, approval gates, and deterministic runner actions.

The platform serves as a bridge between high-level workflow definitions and low-level LLM execution, providing:

- **Workflow orchestration** — Multi-step execution with routing and state management
- **Multi-backend support** — Unified interface to multiple LLM providers
- **Deterministic actions** — Guaranteed-execution steps alongside LLM-based steps
- **Review and refinement** — Built-in loops for quality assurance
- **State persistence** — Job state tracking with retry and recovery

## Scope

### In Scope

- Local workflow execution with prompt rendering and artifact management
- Backend-connected worker mode for distributed execution
- Daemon supervision for workstation-based work claiming
- Multi-step workflow definition and execution
- Review/reject/approve routing with retry limits
- Deterministic runner actions for non-LLM operations
- Artifact validation and documentation guardrails

### Out of Scope

- LLM training or fine-tuning
- General-purpose task scheduling
- Non-workflow execution models
- Direct database persistence (delegates to backend)

## Primary Flows

### Workflow Execution Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Start     │────▶│  Load Job   │────▶│  Preflight  │
│   (CLI)     │     │    State    │     │   Check     │
└─────────────┘     └─────────────┘     └─────────────┘
                                                  │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Route     │◀────│   Read      │◀────│   Invoke    │
│   Next      │     │   Meta.json │     │   Coder     │
│   Step      │     │             │     │   / Action  │
└─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│  Complete   │
│    / Fail   │
└─────────────┘
```

Each step follows this contract:

1. **Load** — Load workflow bundle from runtime path
2. **Render** — Render prompt from template with artifact context
3. **Invoke** — Call coder (Claude/Codex/Qwen) or execute deterministic action
4. **Validate** — Read `meta.json` sidecar written by the step
5. **Route** — Route to next step based on sidecar status (APPROVED/REJECTED)

### Value Flow

The platform creates value through:

| Input | Process | Output |
|-------|---------|--------|
| Workflow definition | Template rendering | Executed prompt |
| LLM response | Sidecar validation | Structured result |
| Step result | Routing logic | Next step or completion |
| Failed step | Retry logic | Re-execution or escalation |
| Review feedback | Refinement loop | Improved output |

### Execution Modes

#### 1. Manual Execution (`ukbe-run-agent run`)

**Use Case**: Local development, testing, one-off workflows

**Flow**:
```
CLI args → Load config → Resolve job → Render prompt → Run step → Route
```

**Characteristics**:
- Synchronous execution
- Local file system for artifacts
- Human-in-the-loop for approvals
- Immediate feedback

#### 2. Worker Mode (`ukbe-run-agent worker`)

**Use Case**: Backend-driven execution, distributed workers

**Flow**:
```
Poll backend → Claim work → Execute step → Submit result → Poll again
```

**Characteristics**:
- Asynchronous execution
- Backend as source of truth
- Event-driven notifications
- Scalable worker pools

#### 3. Daemon Mode (`ukbe-run-agent daemon`)

**Use Case**: Workstation supervision, continuous operation

**Flow**:
```
Start daemon → Poll backend → Spawn child process → Monitor → Cleanup
```

**Characteristics**:
- Long-running supervisor
- Child process isolation
- Automatic recovery
- Local log aggregation

## Architecture Profile

### Universal Baseline

The repository follows these architectural principles:

| Principle | Implementation |
|-----------|---------------|
| **Separation of concerns** | Coder/adapters separate from routing logic |
| **Deterministic actions** | 28 well-defined actions separate from LLM steps |
| **State persistence** | Job state in JSON with schema versioning |
| **Artifact validation** | Guardrails protect generated documents |
| **Multi-backend support** | Unified interface to Claude, Codex, Qwen |

### Repo-Selected Profile

This repository currently operates in a **`provisional` → `structured` posture**:

| Aspect | Universal Baseline | Current Posture | Target Posture |
|--------|-------------------|-----------------|----------------|
| **Workflow definition** | Declarative | Monolithic registry | Plugin packages |
| **Path management** | Centralized constants | ✅ Centralized | Centralized |
| **Sidecar contract** | meta.json v2 | ✅ v2 strict | v2 strict |
| **Test organization** | Unit/integration split | ✅ Split | Split |
| **Documentation** | Workflow-generated | Partial | Complete |

### Migration Posture

**Current Status**: `in_progress`

The repository exhibits characteristics of both provisional and structured profiles:

#### Provisional Elements

- **Monolithic `template_groups.py`** (2,453 lines) with 21 hardcoded workflows
- Plugin system migration incomplete
- Manual documentation synchronization

#### Structured Elements

- **Centralized constants** in `constants.py` (1,342 lines)
- **Strict sidecar contract** (v2) with meta.json as sole channel
- **Comprehensive test coverage** with unit/integration split
- **Deterministic action separation** with 28 well-defined actions

## Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Monolithic workflow registry** | High | Plugin migration in progress |
| **Bootstrap/runtime drift** | Medium | Sync workflow planned |
| **Windows-centric tooling** | Medium | Cross-platform roadmap defined |
| **Meta.json schema versioning** | Low | Backward compatibility enforced |
| **Documentation gaps** | Medium | Bootstrap workflow in progress |

## External Dependencies

### Required

| Dependency | Purpose |
|------------|---------|
| Python 3.12+ | Runtime environment |
| pip packages | See `requirements.txt` |
| LLM API credentials | For coder invocation |

### Optional

| Dependency | Purpose |
|------------|---------|
| Backend service | Worker/daemon modes |
| Pushover API | Notifications |
| ComfyUI | Image generation workflows |
| Video generation tools | Video workflows |

## Related Documents

- [README.md](README.md) — System documentation index
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Operational capabilities
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional scope
- [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) — Component breakdown
- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository analysis

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
