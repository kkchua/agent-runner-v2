---
template_id: "SYS-00-SO"
title: "System Overview"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:43:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview

## Purpose

This document provides a comprehensive overview of the `agent-runner-v2` platform. It explains what the system does, how it works, and why it exists—at a level useful to stakeholders, developers, and operators.

## Scope

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine that executes structured multi-step workflows across multiple AI models (Claude, Codex, Qwen). It provides review loops, retries, approval gates, and deterministic runner actions.

The system operates in three primary modes:
- **Manual execution**: Direct workflow invocation via CLI
- **Backend-connected**: Worker mode for backend-orchestrated execution
- **Daemon supervision**: Continuous supervision with polling

## Primary Flows

### Workflow Execution Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Load Workflow  │────▶│  Render Prompt   │────▶│ Invoke Coder    │
│  Bundle         │     │  Template        │     │ or Action       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
┌─────────────────┐     ┌──────────────────┐            │
│  Route to Next  │◀────│  Validate        │◀───────────┘
│  Step           │     │  Artifacts       │
└─────────────────┘     └──────────────────┘
       │
       ▼
┌─────────────────┐
│  Read meta.json │
│  Sidecar        │
└─────────────────┘
```

### Key v2 Contract

1. **meta.json sidecar is the ONLY result channel**
2. **No markdown write-backs by the runner**
3. **No silent recovery paths**
4. **Hard failures route explicitly through failure handling**
5. **Declarative document protection via `produces` lists**

### Value Flow

The system creates value through:

1. **Structured Execution**: Workflows proceed through defined steps with clear inputs and outputs
2. **Quality Gates**: Review steps with APPROVE/REJECT decisions
3. **Retry Logic**: Automatic retries with configurable limits
4. **Artifact Management**: Consistent artifact paths and validation
5. **Deterministic Actions**: Python functions for predictable operations
6. **Multi-Model Support**: Claude, Codex, Qwen with unified interface

## Architecture Profile

### Universal Baseline

The following applies to all repositories using the runner:

| Aspect | Baseline |
|--------|----------|
| **Execution Model** | Step-by-step with explicit routing |
| **Result Channel** | meta.json sidecar only |
| **Document Protection** | Declarative `produces` lists |
| **Path Management** | Centralized constants |
| **Review Pattern** | Generate → Review → Refine loops |

### Repo-Selected Profile

| Aspect | Current Setting |
|--------|-----------------|
| **Architecture Posture** | `provisional` → `explicit` |
| **Documentation Mode** | `bootstrap-in-progress` |
| **Target Standard** | Delivery scaffold governance model |

### Profile Migration

The repository is transitioning from `provisional` to `explicit`:

```
Current: provisional (no clear standard)
  ↓
Bootstrap: bootstrap-in-progress (generating docs)
  ↓
Target: explicit (delivery scaffold governance)
```

**Migration Posture**: The repository demonstrates explicit architecture through:
- Strong module separation (core, state, adapters, actions)
- Centralized constants (1,333 lines in constants.py)
- Contract-based step execution
- Bootstrap/runtime separation

However, the formal documentation is still being bootstrapped, hence the `provisional` classification.

## Key Risks

### Runtime Sync Risk

**Description**: Changes to bootstrap workflow files must be synced to runtime bundles before taking effect.

**Mitigation**: 
- Explicit sync commands (`ukbe-run-agent sync`)
- Version checking in loader
- Validation on load

**Impact**: High (silent failures if not synced)

### Sidecar Contract Enforcement

**Description**: Strict v2 sidecar schema required; deviation causes hard failures.

**Mitigation**:
- Automated sidecar instruction injection
- Schema validation
- Clear error messages

**Impact**: Medium (failures are explicit)

### Bootstrap-to-Runtime Drift

**Description**: Runtime bundles may diverge from bootstrap source.

**Mitigation**:
- Explicit sync workflow
- Version manifests
- Drift detection

**Impact**: Medium (manageable with process)

### Documentation Protection Model

**Description**: Misconfigured `produces` lists can block writes or allow unauthorized modifications.

**Mitigation**:
- Declarative allow-lists
- Validation on write
- Clear error messages

**Impact**: Low (validation catches issues)

### Multi-Model Consistency

**Description**: Different models may interpret prompts differently.

**Mitigation**:
- Model-specific prompt variants
- Consistent schema enforcement
- Fallback validation

**Impact**: Medium (model-specific handling)

## System Boundaries

### Inside the System

- Workflow step execution
- Prompt rendering and substitution
- Artifact path resolution
- Meta.json validation
- Step routing (approve/reject/failure)

### Outside the System

- Backend state management (backend is source of truth)
- LLM model execution (via adapters)
- File system operations (via actions)
- Network operations (via actions)

### Integration Points

| System | Integration | Responsibility |
|--------|-------------|----------------|
| Backend | REST API | State sync, artifact storage |
| Claude | Adapter | Code generation |
| Codex | Adapter | Code generation |
| Qwen | Adapter | Code generation |
| File System | Actions | Read/write operations |
| Notifications | Manager | Pushover, etc. |

---

## Related Documents

- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository posture
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — What it enables
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — How it behaves
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality expectations

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs` on 2026-07-10T09:43:38+08:00*
