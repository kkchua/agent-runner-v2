---
title: "System Overview"
template_id: "SYS-00-SO"
status: "active"
generated: "2026-07-10T11:45:32+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-15f76235"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview

## Purpose

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine that executes structured multi-step workflows across multiple LLM providers (Claude, Codex, Qwen), with support for review loops, retries, approval gates, and deterministic runner actions.

The platform serves as a bridge between:
- **Human intent** (captured in workflow definitions and prompt templates)
- **LLM execution** (through coder adapters for different providers)
- **Deterministic actions** (through Python action library)
- **Structured outputs** (via meta.json sidecar pattern)

### Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Developers** | Structured workflow execution with predictable routing, review loops, and artifact validation |
| **Teams** | Multi-model orchestration, documentation governance, and delivery scaffold workflows |
| **Operators** | Daemon supervision, backend integration, and operational visibility |

## Scope

### In Scope

- Local workflow execution via CLI
- Multi-model LLM invocation (Claude, Codex, Qwen)
- Deterministic action execution
- Job state management and persistence
- Backend-connected worker modes
- Workstation daemon supervision
- Documentation generation and validation
- Bundle seeding and runtime workflow management

### Out of Scope

- LLM training or fine-tuning
- General-purpose task scheduling
- Distributed execution across multiple machines
- Web UI or graphical interface
- Real-time collaboration features

### System Boundary

The system boundary encompasses:
- The `agent-runner-v2` Python package
- Runtime state in `%USERPROFILE%\.ukbe-runner\`
- Integration with LLM providers (Claude, Codex, Qwen APIs)
- Optional backend API integration
- Local file system for artifact storage

External systems (out of scope):
- Backend API implementation
- LLM provider services
- ComfyUI/media generation services
- Version control systems

## Primary Flows

### Flow 1: Local Workflow Execution

```
User → ukbe-run-agent run → Load Workflow Bundle → Render Prompt
    → Invoke Coder/Action → LLM/Action Executes → Write Artifacts
    → Write meta.json → Validate → Route to Next Step → Repeat
```

1. User invokes `ukbe-run-agent run --template-group <workflow>`
2. Runner loads workflow bundle from runtime location
3. Step runner renders prompt template with artifact substitution
4. Coder adapter invokes LLM or runner executes action
5. LLM/action writes artifacts to disk
6. LLM writes structured results to `meta.json` sidecar
7. Step runner validates artifacts
8. Workflow router determines next step
9. Repeat until completion or failure

### Flow 2: Backend-Connected Execution

```
Daemon → Poll Backend → Claim Step → Spawn execute-step
    → Child Process Executes → Report Result → Backend Updates
    → Daemon Claims Next Step → Repeat
```

1. Daemon polls backend for available work
2. Backend assigns step to worker
3. Daemon spawns `execute-step` subprocess
4. Child process executes step (same as Flow 1)
5. Child reports result via result file
6. Daemon submits result to backend
7. Backend updates run state
8. Daemon polls for next assignment

### Flow 3: Documentation Bootstrap

```
Project Analysis → Generate Codebase Baseline → Generate System Docs
    → Generate Architecture Docs → Review/Refine → Finalize
```

1. `00_master_docs_bootstrap_v1` analyzes repository
2. Generates codebase inventory and module docs
3. Generates master system documentation (this set)
4. Generates architecture and operations docs
5. Review cycle for refinement
6. Finalize bootstrap

## Architecture Profile

### Universal Baseline

The universal baseline defines capabilities present in every deployment:

| Attribute | Value |
|-----------|-------|
| **Language** | Python 3.11+ |
| **Dependencies** | Zero runtime dependencies (stdlib only) |
| **Interface** | CLI-only |
| **State** | File-based (JSON) |
| **Concurrency** | Single-threaded (per process) |

### Repo-Selected Profile

The repository has selected additional architectural characteristics:

| Attribute | Selection | Rationale |
|-----------|-----------|-----------|
| **Documentation Governance** | `enabled` | 67 module docs, active validation workflows |
| **Multi-Model Support** | `Claude, Codex, Qwen` | Flexibility for different tasks |
| **Backend Integration** | `optional` | Supports both local and backend-connected modes |
| **Daemon Supervision** | `enabled` | Production workstation deployment |
| **Action Library** | `26 actions` | Comprehensive deterministic operations |

### Architecture Posture

| Attribute | Value |
|-----------|-------|
| **Current Profile** | `provisional` |
| **Target Profile** | `structured_delivery` |
| **Migration Mode** | `incremental` |
| **Repo State** | `explicit` |

### Posture Rationale

**Current Profile: Provisional**

The repository is in provisional posture because:
- Master system docs are currently being generated
- Documentation is actively being reconciled
- Bundle taxonomy is evolving

**Target Profile: Structured Delivery**

The target is structured delivery based on:
- 8+ active workflow families
- Comprehensive documentation governance
- Delivery scaffold workflows
- Multi-audience documentation generation

**Migration Mode: Incremental**

Migration is incremental because:
- Existing codebase documentation exists (67 modules)
- Changes are being made without disrupting existing workflows
- Bootstrap workflow handles gradual adoption

## Key Risks

### Risk 1: Runtime Bundle Drift

**Description**: Bootstrap templates in repo may diverge from runtime bundles.

**Impact**: Changes to bootstrap may not take effect until `init` re-run.

**Mitigation**: 
- Document sync requirement
- Provide sync batch files
- Validate runtime bundle freshness

### Risk 2: Meta.json Contract Violation

**Description**: LLMs may not write proper meta.json sidecar.

**Impact**: Step routing fails, workflows stall.

**Mitigation**:
- Prompt instructions for meta.json format
- Sidecar validation before routing
- Explicit failure handling

### Risk 3: Backend Availability

**Description**: Backend-connected modes require backend availability.

**Impact**: Worker/daemon modes fail if backend unreachable.

**Mitigation**:
- Local mode works without backend
- Retry logic with backoff
- Clear error messages

### Risk 4: Windows Path Handling

**Description**: Path resolution issues on Windows.

**Impact**: Artifact paths may fail to resolve.

**Mitigation**:
- Centralized path constants using `PurePosixPath`
- Cross-platform testing
- Path normalization in constants

### Risk 5: LLM Provider Rate Limits

**Description**: External API rate limits may throttle execution.

**Impact**: Slow workflow execution, timeouts.

**Mitigation**:
- Configurable timeouts
- Retry with exponential backoff
- Local caching where appropriate

### Risk 6: Job State Migration

**Description**: Schema changes may break existing jobs.

**Impact**: Old jobs fail to load after updates.

**Mitigation**:
- Backward compatibility functions
- Migration helpers
- Version tracking in job state

## Related Documents

- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Detailed repository analysis
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Operational capabilities
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional requirements
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality attributes
