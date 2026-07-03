---
template_id: "SYS-00-SO"
title: "System Overview - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview

## Purpose

Agent-runner-v2 is a standalone Python-based LLM workflow orchestration engine that enables structured multi-step workflow execution across multiple LLM providers (Claude, Codex, Qwen). It provides review loops, retries, approval gates, and deterministic runner actions for automating complex delivery processes.

**Why:** Manual coordination of LLM-assisted workflows is error-prone and difficult to reproduce. The runner provides deterministic execution, state persistence, and clear contracts between steps, enabling reliable automation of code generation, documentation, content creation, and other AI-assisted tasks.

## Scope

### In Scope

- **Local workflow execution** — Manual execution with artifact-based progression
- **Backend-connected operation** — Worker and daemon modes for distributed execution
- **Multi-provider LLM support** — Claude, Codex, Qwen adapters
- **Step-level routing** — Review/refine loops and failure handling
- **State management** — Job lifecycle with persistence and recovery
- **Template-based prompts** — Externalized prompt templates
- **Deterministic actions** — Non-LLM step execution

### Out of Scope

- **Backend API implementation** — The runner is a client, not the server
- **Model training** — Uses existing LLM APIs, no training
- **General-purpose compute** — Focused on LLM workflow orchestration
- **Persistent queue** — Backend owns queue management
- **Multi-user coordination** — Single-workstation focus

## Primary Flows

### Flow 1: Local Workflow Execution

```
User → CLI → Load Workflow → Resolve Step → Render Prompt → Invoke Coder
                                                    ↓
User ← Results ← Route ← Validate Artifacts ← Read meta.json
```

**Description:** A user initiates a workflow locally, the runner loads the workflow bundle, determines the current step, renders the prompt template, invokes the configured LLM coder, reads the resulting `meta.json` sidecar, validates claimed artifacts, and routes to the next step or approval gate.

**Key Characteristics:**
- Interactive or batch execution
- Artifact files as step outputs
- Review/refine loops for quality control
- Local state in `%USERPROFILE%\.ukbe-runner\jobs\`

### Flow 2: Backend-Connected Worker

```
Backend → Poll → Claim Work → Execute Step → Submit Result → Backend
             ↑                                          ↓
             └──────────── Heartbeat ←──────────────────┘
```

**Description:** A worker process polls a backend for available work, claims a workflow step, executes it using the local runner, submits results back to the backend, and emits heartbeats during execution.

**Key Characteristics:**
- Distributed execution model
- Backend as source of truth
- Worker ID for identification
- Result submission via API

### Flow 3: Daemon Supervision

```
Daemon → Claim Work → Spawn Child → Monitor → Log → Heartbeat
            ↑                             ↓
            └────── Track State ←─────────┘
```

**Description:** A daemon process continuously claims work from the backend, spawns child processes for each step execution, monitors child state, writes logs, and emits child-scoped heartbeats keyed by workflow step run ID.

**Key Characteristics:**
- Long-running supervision
- Child process isolation
- Automatic retry on failure
- Log aggregation

### Flow 4: Review/Refine Loop

```
Step Execution → Coder Returns REJECTED → Review Decision
                                                  ↓
         ↓────────────────── Refine Step ←────────────────┘
         ↓
    APPROVED → Advance Step
```

**Description:** When a coder returns `REJECTED` status, the runner enters a review/refine loop. The rejection code determines the next action: auto-retry, human intervention, or replan. The loop continues until approved or a retry limit is reached.

**Key Characteristics:**
- Configurable max rejects per step
- Auto-retryable vs human-retryable classification
- Replan context for workflow adaptation
- State tracking in `loop_context`

## Architecture Profile

### Universal Baseline

The universal baseline applies to all agent-runner-v2 deployments:

- **CLI Entry Point** — `ukbe-run-agent` command
- **Bootstrap Seeding** — Packaged to runtime bundle copy
- **Job State Management** — JSON-based persistence
- **Meta.json Contract** — Structured step results
- **Multi-coder Support** — Abstracted LLM invocation

### Repo-Selected Profile: `standard`

This repository selects the `standard` architecture profile with these characteristics:

#### Architecture Pattern

- **Modular Design** — Clear separation across 40+ modules
- **State Machine** — Explicit job state transitions
- **Plugin Actions** — Deterministic action system
- **Schema-Driven** — JSON schemas for validation

#### Component Organization

| Layer | Components | Responsibility |
|-------|------------|--------------|
| **CLI** | `run_agent.py` | Command parsing, orchestration |
| **Execution** | `step_runner.py`, `workflow_router.py` | Step execution, routing |
| **State** | `job_state.py`, `runtime_context.py` | Persistence, context |
| **Adapters** | `coder_adapters.py` | LLM invocation |
| **Actions** | `actions/` package | Deterministic operations |
| **Bootstrap** | `bundle_loader.py`, `template_groups.py` | Workflow loading |

#### Runtime Characteristics

- **v2 Runtime Model** — Meta.json sidecar as sole result channel
- **No Silent Recovery** — Explicit failure routing
- **No Markdown Write-Backs** — Runner does not modify doc files
- **Deterministic Paths** — Explicit path resolution

### Migration Posture: `in_progress`

The repository is in documentation bootstrap:

- **Active Generation** — Documentation being created by workflow
- **Guardrail Protected** — Workflow-generated docs block manual edits
- **Validation Advisory** — Failures don't block development
- **Approval Required** — Final transition requires human approval

## Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Global runner home dependency** | Medium | Runtime depends on `%USERPROFILE%\.ukbe-runner` initialization |
| **Coder timeout handling** | Medium | Configurable `coder_timeout_seconds` per step |
| **Backend connectivity failures** | Medium | Worker mode has retry logic; daemon handles child failures |
| **Artifact path resolution errors** | Low | Explicit path resolution via `resolve_repo_or_runtime_path()` |
| **State migration complexity** | Medium | Migration functions in `job_state.py` for backward compatibility |
| **Workflow-generated doc protection** | Low | Guardrails prevent manual edits to workflow-generated documents |
| **Windows-specific paths** | Medium | Path handling uses `pathlib` with Windows conventions |

## Value Proposition

### For Users

- **Reliable Execution** — Deterministic workflows with clear failure handling
- **Quality Control** — Review loops and approval gates
- **Flexibility** — Multiple execution modes (local, worker, daemon)
- **Transparency** — State visible in job JSON, logs for debugging

### For Developers

- **Extensible** — Action system for custom operations
- **Testable** — Schema validation and artifact-based testing
- **Portable** — Python package installable via pip
- **Observable** — Comprehensive logging and usage tracking

### For Operations

- **Scalable** — Daemon mode for continuous processing
- **Resilient** — Automatic retry and failure classification
- **Integrable** — Backend API for distributed systems
- **Maintainable** — Clear module boundaries and documentation

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
