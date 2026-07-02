---
title: "System Context: agent-runner-v2"
template_id: "SYS-03-SC"
status: "active"
managed_by: workflow-generated
created: "2026-07-02T20:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260702-005"
---

# System Context: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

## 1. System Boundary

### 1.1 Scope

The **agent-runner-v2** system is a standalone Python LLM workflow orchestration engine that:

- Orchestrates complex multi-step delivery workflows across multiple LLM backends
- Enforces strict v2 sidecar contracts (`meta.json`) for all step results
- Provides deterministic runner actions for repository operations
- Supports local CLI execution, backend-connected worker modes, and daemon supervision
- Manages workflow state through explicit job lifecycle transitions

### 1.2 In-Scope

| Capability | Description |
|------------|-------------|
| Workflow Execution | Multi-step workflow orchestration with review loops and retries |
| LLM Integration | Claude, Codex, Qwen, and aliased model invocation |
| Sidecar Contract | Strict `meta.json` validation as the only result channel |
| Runner Actions | Deterministic file/system operations via action modules |
| Job State Management | JSON-based state machine with schema versioning |
| Backend Integration | Worker mode for backend-driven step execution |
| Bundle Management | Bootstrap seeding and runtime workflow bundle loading |
| Documentation Sync | Automated codebase and system documentation synchronization |

### 1.3 Out-of-Scope

| Capability | Rationale |
|------------|-----------|
| LLM Training | The system consumes LLM APIs, does not train models |
| Persistent Database | Job state is file-based JSON, not a database |
| Real-time Collaboration | Single-user/single-process execution model |
| Web UI | CLI-focused, no built-in web interface |
| General Compute | Actions are domain-specific, not arbitrary code execution |

## 2. External Systems

| System | Type | Interface | Purpose |
|--------|------|-----------|---------|
| **Backend API** | HTTP/REST | `backend_client.py` | Work distribution, step claiming, result submission |
| **Claude API** | HTTP/REST | `coder_adapters.py` | Primary LLM invocation for complex tasks |
| **Codex API** | HTTP/REST | `coder_adapters.py` | Code-focused LLM tasks |
| **Qwen Code** | Local Tool | `coder_adapters.py` | Local-first execution via CLI |
| **File System** | Local I/O | Pathlib, `actions/` | Artifact persistence, state storage |
| **ComfyUI** | HTTP/REST | `actions/submit_comfyui.py` | Image generation workflow execution |
| **VideoXpress** | HTTP/REST | `actions/*.py` | Video generation and assembly |

## 3. Actors and Stakeholders

### 3.1 Primary Actors

| Actor | Role | Interactions |
|-------|------|--------------|
| **Developer** | End user | Runs workflows locally via CLI, reviews artifacts, approves steps |
| **Backend Service** | Orchestrator | Distributes work to workers, manages job queue |
| **Daemon Supervisor** | Process manager | Long-running worker process with heartbeat |
| **LLM Provider** | Compute | Executes prompts, returns structured results |

### 3.2 Stakeholder Concerns

| Stakeholder | Concerns |
|-------------|----------|
| **Developers** | Reliable workflow execution, clear failure messages, actionable retries |
| **Operators** | Observability, log access, job state inspection, emergency procedures |
| **Maintainers** | Contract stability, schema versioning, backward compatibility |
| **Integrators** | Backend API contract, worker mode behavior, step result format |

## 4. Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         agent-runner-v2                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  run_agent  │  │ step_runner │  │workflow_router│ │ job_state   │    │
│  │   (CLI)     │  │  (invoke)   │  │   (route)   │  │  (state)    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│         └────────────────┴────────────────┴────────────────┘            │
│                                   │                                     │
│                          ┌────────┴────────┐                            │
│                          │  coder_adapters │                           │
│                          │ (Claude/Codex/  │                           │
│                          │    Qwen)        │                           │
│                          └────────┬────────┘                            │
└───────────────────────────────────┼───────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │   Claude    │          │    Codex    │          │    Qwen     │
    │    API      │          │    API      │          │    Code     │
    └─────────────┘          └─────────────┘          └─────────────┘

           ┌─────────────────────────────────────────────────┐
           │              Backend API                         │
           │  (Work distribution, claiming, submission)      │
           └─────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                   ▼
    ┌─────────────┐                                    ┌─────────────┐
    │   Worker    │                                    │   Daemon    │
    │   Process   │                                    │ Supervisor  │
    └─────────────┘                                    └─────────────┘

           ┌─────────────────────────────────────────────────┐
           │              File System                         │
           │  (%USERPROFILE%\.ukbe-runner\)                   │
           │  - jobs/<group>/<job>/job.json                  │
           │  - workflows/<workflow>/template_groups.py      │
           │  - logs/*.log                                   │
           └─────────────────────────────────────────────────┘
```

## 5. Runtime Contexts

The system operates in three distinct runtime contexts:

| Context | Command | Execution Model |
|---------|---------|-----------------|
| **Local Execution** | `ukbe-run-agent run` | Synchronous, blocking CLI execution with job state tracking |
| **Backend Worker** | `ukbe-run-agent worker`, `poll`, `execute-step` | Asynchronous, backend-driven single-step execution |
| **Daemon Supervisor** | `ukbe-run-agent daemon` | Long-running process managing multiple worker lifecycles |

### 5.1 Local Execution Flow

```
Developer → ukbe-run-agent run → Load Config → Resolve Job
                                    ↓
                              Pre-flight Check
                                    ↓
                              Render Prompt
                                    ↓
                              Invoke Coder
                                    ↓
                              Read meta.json
                                    ↓
                              Validate Artifacts
                                    ↓
                              Route After Step
                                    ↓
                              Update Job State
                                    ↓
                              Exit (continue/retry/fail)
```

### 5.2 Backend Worker Flow

```
Backend → Poll for Work → Claim Step → Execute Step
                              ↓
                         Submit Result
                              ↓
                         Wait for Next
```

## 6. Data Flow

### 6.1 Normal Execution Flow

| Step | Data | Source | Destination |
|------|------|--------|-------------|
| 1 | Job Config | `config.json` | `run_agent.py` |
| 2 | Job State | `job.json` | `job_state.py` |
| 3 | Prompt Template | `prompts/<step>.txt` | `step_runner.py` |
| 4 | Rendered Prompt | `step_runner.py` | LLM Provider |
| 5 | LLM Response | LLM Provider | Coder Process |
| 6 | Sidecar Result | Coder Process | `meta.json` |
| 7 | Validation | `step_runner.py` | `meta.json` (enriched) |
| 8 | Routing Decision | `workflow_router.py` | `job.json` (updated) |
| 9 | Artifacts | `meta.json` | Filesystem |

### 6.2 Failure Handling Flow

| Failure Type | Detection | Routing | Recovery |
|--------------|-----------|---------|----------|
| **Coder Timeout** | `coder_adapters.py` | `route_after_failure()` | AUTO_RETRYABLE → Retry with backoff |
| **Meta.json Missing** | `step_runner.py` | `route_after_failure()` | HUMAN_RETRY_REQUIRED → Intervention |
| **Artifact Missing** | `step_runner.py` | `route_after_failure()` | Depends on step config |
| **Validation Error** | `step_runner.py` | `route_after_failure()` | FATAL → Terminal failure |

## 7. Deployment Context

### 7.1 Installation

```bash
pip install -e ".[dev]"
ukbe-run-agent init
```

### 7.2 Runtime Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| Python | Runtime | 3.11+ |
| Jinja2 | Prompt templating | Latest |
| Pathlib | Cross-platform paths | Built-in |
| Requests | Backend API calls | Latest |

### 7.3 Runtime File Structure

After initialization, the runner home contains:

```
%USERPROFILE%\.ukbe-runner\
├── config.json                    # Global configuration
├── jobs\                         # Job state directory
│   └── <workflow-group>\         # Group-scoped jobs
│       └── <job-id>\             # Individual job
│           ├── job.json          # Job state (schema v6)
│           └── <step>/           # Step directories
│               └── meta.json     # Step result sidecar
├── workflows\                    # Runtime workflow bundles
│   └── default\                  # Active workflow
│       ├── template_groups.py    # Workflow definitions
│       └── prompts/              # Prompt templates
└── logs\                         # Execution logs
```

## 8. Key Constraints

### 8.1 Contract Constraints

| Constraint | Enforcement | Violation |
|------------|-------------|-----------|
| meta.json is ONLY channel | `step_runner.py` | Hard failure, no fallback |
| No markdown write-backs | Code review | Manual edits rejected |
| Explicit failure routing | `workflow_router.py` | Silent failures prevented |
| Blocking issues owned by coder | `step_runner.py` | Empty blocking_issues list |
| Schema version tracking | `job_state.py` | Migration required |

### 8.2 Operational Constraints

| Constraint | Source | Implication |
|------------|--------|-------------|
| Bootstrap vs Runtime split | Architecture | Two sources of truth, sync on init |
| Job state immutability | Design | State transitions are append-only |
| Coder timeout | Configuration | 600s default, configurable per-step |
| Review loop budget | Template config | Max attempts prevents infinite loops |

## 9. Bootstrap/Runtime Duality

A key architectural characteristic is the split between **packaged bootstrap source** and **runtime workflow bundles**:

| Aspect | Bootstrap Source | Runtime Bundle |
|--------|-----------------|------------------|
| Location | `agent_runner_v2/bootstrap/` | `%USERPROFILE%\.ukbe-runner\workflows\` |
| Purpose | Seeds initial runtime | Actually loaded at execution |
| Updates | Via package update | Via `init` or manual sync |
| Version | Package version | User-managed |

This split enables:
- Safe workflow customization without package modification
- Version isolation between projects
- Rollback capability via bundle management

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs`*
