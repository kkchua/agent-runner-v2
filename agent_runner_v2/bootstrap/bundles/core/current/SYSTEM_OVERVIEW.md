---
template_id: "SYS-00-SO"
title: "System Overview"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview

## Purpose

This document provides a high-level overview of the `agent-runner-v2` platform, explaining its purpose, core workflows, and value proposition for stakeholders, developers, and operators.

## Scope

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine that runs structured multi-step workflows across multiple LLM providers (Claude, Codex, Qwen). The platform supports review loops, retries, approval gates, and deterministic runner actions with a strict execution contract.

### What This Platform Does

- **Orchestrates LLM workflows**: Multi-step workflows with deterministic routing
- **Supports multiple usage modes**: Local execution, backend-connected worker, and daemon supervision
- **Enforces strict contracts**: `meta.json` sidecar is the only structured result channel
- **Manages job lifecycle**: State tracking, retry handling, failure classification
- **Provides bootstrap workflows**: Pre-defined workflows for common patterns

### What This Platform Does Not Do

- Does not replace individual LLM APIs (wraps them with adapters)
- Does not persist execution history indefinitely (job-scoped)
- Does not provide a web UI (CLI-focused)
- Does not manage secrets or credentials (relies on environment)

## Primary Flows

### Flow 1: Local Workflow Execution

```
User → ukbe-run-agent run → Load Workflow → Render Prompt → Invoke Coder
                                              ↓
                                        Read meta.json
                                              ↓
                                        Validate Artifacts
                                              ↓
                                        Route to Next Step
```

**Value**: Developers can run workflows locally without backend connectivity.

### Flow 2: Backend-Connected Worker

```
Daemon/Worker → Poll Backend → Claim Work → Execute Step
                                                  ↓
                                        Submit Result → Backend
                                                  ↓
                                        Poll for Next Work
```

**Value**: Workstation acts as a worker node for distributed execution.

### Flow 3: Step Execution Loop

```
Load Job State → Check Preflight → Run Step → Parse Result
                                               ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                                  APPROVED           REJECTED
                                    ↓                   ↓
                              Advance Step         Review Loop
                                    ↓                   ↓
                              Next Step            Refine/Retry
```

**Value**: Strict v2 contract with explicit routing and no silent recovery.

## Architecture Profile

### Universal Baseline

The platform establishes a universal baseline applicable to all repositories:

| Baseline Element | Description |
|-------------------|-------------|
| **Execution Contract** | v2 sidecar-only communication |
| **Job Schema** | Version 2 with structured state |
| **Routing Model** | Explicit approve/reject/failure paths |
| **Artifact Model** | Declared keys with existence validation |
| **Coder Abstraction** | Adapter pattern for Claude, Codex, Qwen |

### Repo-Selected Profile

This repository (`agent-runner-v2`) currently operates under:

| Attribute | Value | Rationale |
|-----------|-------|-----------|
| `current_profile` | `provisional` | Bootstrap in progress |
| `target_profile` | `explicit` | Full system documentation planned |
| `migration_mode` | `in-progress` | Documentation being generated |

### Migration Posture

The repository is transitioning from `provisional` to `explicit`:

- **Current state**: Substantial implementation (56+ modules, 11 workflow families)
- **Documentation state**: System docs being generated via bootstrap workflow
- **Target state**: Full `explicit` documentation profile
- **Timeline**: Bootstrap completion expected 2026-07-04

### Profile Separation

The platform separates universal baseline from repo-specific profiles:

| Concern | Universal Baseline | Repo-Specific |
|---------|-------------------|---------------|
| Execution contract | v2 sidecar rules | Workflow-specific steps |
| Artifact model | Key classification | Specific artifact paths |
| Routing behavior | APPROVED/REJECTED/FAILURE | Step-specific routing config |
| Documentation structure | Required documents | Optional depth level |

## Key Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Bootstrap/Runtime Divergence** | Runtime bundles may diverge from packaged bootstrap | `init` command, version tracking |
| **Strict Contract Violation** | Schema deviations cause hard failures | Clear validation messages |
| **Multi-Coder Complexity** | Different capabilities across LLM providers | Model mapping configuration |
| **Job State Migration** | Legacy formats require migration | `migrate_job_state()` function |
| **Review Loop Exhaustion** | Max iterations may be exceeded | Human intervention triggers |
| **External Dependency** | Runtime depends on global runner home | Clear initialization SOP |

## Platform Value

### For Developers

- **Local execution**: Test workflows without backend
- **Deterministic routing**: Predictable step transitions
- **Rich debugging**: Step-level logging and state inspection

### For Operators

- **Daemon supervision**: Workstation worker management
- **Backend integration**: Distributed work claiming
- **Failure classification**: Automatic retry vs. human intervention

### For Workflow Authors

- **Template groups**: Declarative workflow definitions
- **Artifact model**: Structured input/output contracts
- **Review loops**: Built-in refinement support

---

*This overview provides the high-level context for the agent-runner-v2 platform. See `FUNCTIONAL_SPEC.md` for detailed behaviors and `BUSINESS_CAPABILITIES.md` for operational impact.*
