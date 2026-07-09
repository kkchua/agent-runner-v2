---
template_id: "SYS-00-SO"
title: "System Overview - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview

## Purpose

This document explains the `agent-runner-v2` platform at a level useful to users, developers, and stakeholders. It describes the platform's purpose, workflow model, value flow, and separates the universal baseline from the repo-selected architecture profile.

## Scope

### In Scope

- **CLI Execution**: init, run, poll, worker, daemon, execute-step modes
- **Workflow Engine**: Prompt rendering, step execution, artifact validation
- **Multi-Model Support**: Claude, Codex, Qwen, and aliased adapters
- **Bootstrap System**: Packaged workflow definitions and documentation
- **Documentation Governance**: Automated generation and validation
- **Job State Management**: Schema versioning, migration, persistence
- **Runner Actions**: Deterministic, testable action modules

### Out of Scope

- **Backend API**: The backend is a separate service; this is the client runtime
- **LLM Training**: No model training or fine-tuning capabilities
- **Multi-Tenant Isolation**: Single-tenant workstation operation (target: multi-tenant)
- **Web UI**: CLI-only interface

## Primary Flows

### Value Flow

The platform creates value by:

1. **Standardizing Workflow Execution**: Deterministic steps with explicit contracts
2. **Enabling Multi-Model Operation**: Seamless switching between LLM providers
3. **Maintaining Execution State**: Resumable, observable job lifecycles
4. **Validating Artifacts**: Structured output via meta.json sidecars
5. **Automating Documentation**: Generated, synchronized documentation

### Execution Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Trigger   │───▶│  Load Job   │───▶│   Render    │───▶│   Execute   │
│  (CLI/API)  │    │    State    │    │   Prompt    │    │    Step     │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│    Route    │◀───│   Validate  │◀───│  Poll for   │◀──────────┘
│   Next Step │    │   Sidecar   │    │  Completion │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Data Flow

| Stage | Input | Output | Storage |
|-------|-------|--------|---------|
| **Trigger** | CLI args, config | Execution request | N/A |
| **Load** | Job ID | Job state | `job.json` |
| **Render** | Template, state | Prompt text | Step directory |
| **Execute** | Prompt, model config | LLM response | Step directory |
| **Validate** | LLM output | meta.json | Step directory |
| **Route** | Sidecar status | Next step / retry / failure | `job.json` |

## Architecture Profile

### Universal Baseline

These principles apply to all `agent-runner-v2` deployments:

1. **Sidecar-Only Results**: `meta.json` is the sole structured result channel
2. **No Markdown Write-Backs**: Runner never modifies generated markdown files
3. **Explicit Routing**: No silent recovery paths; hard failures route explicitly
4. **Deterministic Artifacts**: All paths computed from centralized constants
5. **Bootstrap/Runtime Separation**: Package seeds runtime; runtime is source of truth

### Repo-Selected Profile

**Current Profile**: `explicit-v2-workflow-runner`
**Target Profile**: `universal-bootstrap` - A standalone workflow engine that can bootstrap any repository with consistent documentation and delivery patterns
**Migration Mode**: `provisional` - The repo has established patterns but the universal abstraction is still evolving
**Repo State**: `explicit` - Clear architecture with centralized constants, defined workflow families, and established conventions

### Profile Characteristics

| Characteristic | Current State | Evidence |
|----------------|---------------|----------|
| **Execution Contract** | Strict v2 | `step_runner.py` sidecar-only results |
| **Error Handling** | Explicit only | `workflow_router.py` no silent fallbacks |
| **Path Management** | Centralized | `constants.py` zero hardcoded strings |
| **State Management** | Schema versioned | `job_state.py` schema v6 |
| **Documentation** | Workflow-generated | All SYS-00-* docs via bootstrap |

## Key Risks

### Operational Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| **Sidecar Contract Violation** | High | Coder fails to write valid meta.json | Strict validation; explicit failure routing |
| **Bundle/Runtime Drift** | Medium | Bootstrap source differs from runtime | `init` re-seeds; version tracking |
| **Job State Corruption** | Medium | Partial writes corrupt job.json | Schema versioning; migration on load |
| **Credential Resolution** | Medium | .env/config inconsistency | Shared helper functions in constants.py |

### Technical Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| **Windows Path Handling** | Low | Path.relative_to() failures | Fixed in codebase; centralized handling |
| **Daemon Subprocess Lifecycle** | Low | Child processes hang | Timeout handling; kill grace period |
| **Notification Context Loss** | Low | Missing workflow name in notifications | State fields enforced |

### Documentation Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| **Generated Doc Drift** | Medium | Manual edits to protected docs | Workflow markers; validation checks |
| **Stale Documentation** | Low | Code changes not reflected | Documentation sync workflow |
| **Missing Context** | Low | New features undocumented | SOP enforcement; review gates |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
