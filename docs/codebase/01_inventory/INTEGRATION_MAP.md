---
template_id: "CB-04-IM"
managed_by: workflow-generated
generated: "2026-07-09T21:34:12+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04b_generate_integration_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04b_generate_integration_docs`
> This file is workflow-generated and protected from manual edits.

# Integration Map: agent-runner-v2

## Table of Contents

1. [Overview](#1-overview)
2. [Module Dependency Graph](#2-module-dependency-graph)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Integration Points](#4-integration-points)
5. [Module Areas and Responsibilities](#5-module-areas-and-responsibilities)
6. [Key Interaction Sequences](#6-key-interaction-sequences)
7. [Extension Points](#7-extension-points)

---

## 1. Overview

This document provides a comprehensive map of how modules connect, data flows through the system, and integration points with external systems in agent-runner-v2. It serves as the authoritative reference for understanding module boundaries, data transformations, and system interactions.

**Key Architecture Principles:**
- **Strict Separation of Concerns**: Each module has a narrowly scoped responsibility
- **meta.json Sidecar Contract**: All structured communication flows through sidecar files
- **Bootstrap/Runtime Distinction**: Workflow definitions are loaded from runtime bundles, not directly from the repo
- **Deterministic Actions vs. LLM Coders**: Clear split between programmatic actions and AI-driven steps

---

## 2. Module Dependency Graph

### 2.1 Core Module Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLI Entry Point                                │
│                        run_agent.py (main)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Command Dispatch Layer                               │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┬─────────────┐ │
│  │     run      │    worker    │     poll     │ execute-step │   daemon    │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Core Execution Layer                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   step_runner.py │  │ workflow_router  │  │    job_state.py  │          │
│  │  (prompt render,  │  │ (post-step route)│  │ (job.json mgmt)  │          │
│  │  sidecar validate)│  └──────────────────┘  └──────────────────┘          │
│  └──────────────────┘                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   coder_adapters.py  │  │   actions/*.py       │  │  runtime_context.py  │
│  (LLM invocation)    │  │ (deterministic)      │  │ (path resolution)    │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
                    │                 │
                    ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        External Systems                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ Claude Code │  │  Codex CLI  │  │  Qwen Code  │  │ Backend API     │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Dependency Direction Matrix

| Source Module | Depends On | Dependency Type | Purpose |
|---------------|------------|-----------------|---------|
| `run_agent.py` | `step_runner.py` | Direct import | Step execution orchestration |
| `run_agent.py` | `workflow_router.py` | Direct import | Post-step routing |
| `run_agent.py` | `job_state.py` | Direct import | Job lifecycle management |
| `run_agent.py` | `bundle_loader.py` | Direct import | Workflow bundle loading |
| `run_agent.py` | `runtime_context.py` | Direct import | Path resolution |
| `step_runner.py` | `coder_adapters.py` | Direct import | LLM coder invocation |
| `step_runner.py` | `runtime_context.py` | Direct import | Artifact path resolution |
| `step_runner.py` | `constants.py` | Direct import | Artifact key constants |
| `workflow_router.py` | `job_state.py` | Direct import | State transitions |
| `workflow_router.py` | `coder_adapters.py` | Direct import | Retry logic |
| `job_state.py` | `runtime_context.py` | Direct import | Job directory paths |
| `job_state.py` | `notification_manager.py` | Direct import | Step notifications |
| `coder_adapters.py` | `model_config.py` | Direct import | Coder configuration |
| `coder_adapters.py` | `runner_logger.py` | Direct import | Execution logging |
| `daemon.py` | `runtime_context.py` | Direct import | Context for subprocess |
| `backend_client.py` | — | None | Standalone HTTP client |

### 2.3 Actions Package Dependencies

```
agent_runner_v2/actions/
│
├── __init__.py              (action registration)
├── documentation_validation_core.py
│   └── constants.py         (artifact paths)
├── sync_system_docs.py
│   ├── runtime_context.py   (path resolution)
│   └── constants.py         (artifact paths)
├── sync_codebase_docs.py
│   ├── runtime_context.py
│   └── constants.py
├── validate_*_docs.py       (all validation actions)
│   └── constants.py
├── generate_site.py
│   ├── runtime_context.py
│   └── architecture_site.py
└── execute_t2i.py, execute_i2v.py, etc.
    └── submit_comfyui.py    (ComfyUI API client)
```

---

## 3. Data Flow Diagrams

### 3.1 Main Execution Flow: `ukbe-run-agent run`

```
┌─────────┐    ┌────────────────────────────────────────────────────────────────────┐
│   CLI   │───▶│ 1. Parse arguments (workflow, step, artifacts, coder override)       │
└─────────┘    └────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 2. Load workflow bundle from ~/.ukbe-runner/workflows/<workflow>/                    │
│    - Load template_groups.py for step definitions                                  │
│    - Load prompt template files                                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 3. Initialize/Load job state                                                       │
│    - Create job_id from workflow + seed artifacts                                  │
│    - Load existing job.json or create new                                          │
│    - Apply job state migrations if needed                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 4. Resolve step configuration                                                      │
│    - Get step definition from template_groups.py                                   │
│    - Merge with command-line overrides                                              │
│    - Resolve prompt path (coder-specific fallback)                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 5. Build execution context                                                          │
│    - Load reference artifacts into context dict                                     │
│    - Resolve {PLACEHOLDER} tokens using ARTIFACT_KEY_* constants                    │
│    - Add step-specific context (step name, job_id, etc.)                           │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 6. Render prompt template                                                           │
│    - Substitute context variables into prompt text                                  │
│    - Calculate prompt checksum for cache invalidation                               │
│    - Append sidecar instructions (meta.json requirements)                           │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 7. Execute step                                                                     │
│    ┌─────────────────────────────────────────────────────────────────────────────┐  │
│    │ IF action:  run_action() ──▶ Execute deterministic Python function           │  │
│    │                              Return StepResult                               │  │
│    │                                                                              │  │
│    │ IF coder:   invoke_coder() ──▶ Spawn subprocess (claude/codex/qwen)          │  │
│    │                              Wait for completion                              │  │
│    │                              Read meta.json sidecar                          │  │
│    │                              Validate artifacts exist                        │  │
│    │                              Return StepResult                               │  │
│    └─────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 8. Route based on result                                                            │
│    ┌─────────────────────────────────────────────────────────────────────────────┐  │
│    │ Status = APPROVED:  Advance to next step / Complete workflow               │  │
│    │ Status = REJECTED:  Check retry limit ──▶ Retry or fail                    │  │
│    │ Exception thrown:   route_after_failure() ──▶ Hard failure handling        │  │
│    └─────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 9. Save job state and exit                                                           │
│    - Write updated job.json with step results                                       │
│    - Return exit code (0=success, 1=waiting, 2=failure)                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Backend-Connected Execution Flow

```
┌─────────┐     ┌─────────────────────────────────────────────────────────────────────┐
│  daemon │────▶│ 1. Register worker with backend API                                 │
└─────────┘     │    - POST /workers/register with capabilities                      │
                └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                ┌─────────────────────────────────────────────────────────────────────┐
                │ 2. Heartbeat loop (every 30s)                                       │
                │    - POST /workers/heartbeat with current status                     │
                │    - Report active step_run_id if executing                          │
                └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                ┌─────────────────────────────────────────────────────────────────────┐
                │ 3. Claim work (polling loop)                                          │
                │    - POST /steps/claim with worker_id                              │
                │    - Returns step_run payload or 204 (no work)                       │
                └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                ┌─────────────────────────────────────────────────────────────────────┐
                │ 4. Spawn child process for step execution                           │
                │    - subprocess.Popen([python, -m agent_runner_v2.run_agent,       │
                │                       'execute-step', ...])                        │
                │    - Fresh process loads latest code from disk                     │
                └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                ┌─────────────────────────────────────────────────────────────────────┐
                │ 5. Monitor execution                                                │
                │    - Child process runs step to completion                         │
                │    - Daemon continues heartbeats with step context                │
                │    - Capture exit code and log file                                │
                └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                ┌─────────────────────────────────────────────────────────────────────┐
                │ 6. Complete step_run via API                                        │
                │    - POST /steps/{id}/complete with result payload                 │
                │    - Upload artifacts if configured                                │
                │    - Return to claim loop                                          │
                └─────────────────────────────────────────────────────────────────────┘
```

### 3.3 Coder Invocation Data Flow

```
┌────────────────┐
│  step_runner   │
│   run_step()   │
└───────┬────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ coder_adapters.invoke_coder()                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│ │ 1. Prepare invocation manifest                                                  │   │
│ │    - Build coder-specific command line (claude/codex/qwen)                       │   │
│ │    - Set working directory to step directory                                   │   │
│ │    - Configure timeout (step config > env > config.json > default)               │   │
│ └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                              │
│                                      ▼                                              │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│ │ 2. Spawn subprocess with prompt                                                   │   │
│ │    - Write prompt text to temp file or stdin                                     │   │
│ │    - Execute: claude --prompt-file <path> --output-dir <step_dir>                │   │
│ │    - Poll for sidecar file appearance                                            │   │
│ └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                              │
│                                      ▼                                              │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│ │ 3. Wait for completion / timeout                                                  │   │
│ │    - Poll sidecar every SIDECAR_POLL_INTERVAL_SECONDS (5s)                       │   │
│ │    - Check for coder process termination                                          │   │
│ │    - Enforce timeout if specified                                                │   │
│ └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                              │
│                                      ▼                                              │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│ │ 4. Read and validate meta.json                                                    │   │
│ │    - Parse JSON schema                                                           │   │
│ │    - Extract status, remark, artifacts                                            │   │
│ │    - Return InvocationResult with usage data                                      │   │
│ └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────┐
│  step_runner   │
│ validate and  │
│ enrich sidecar │
└────────────────┘
```

---

## 4. Integration Points

### 4.1 External System Integration Table

| System | Direction | Protocol | Module | Purpose |
|--------|-----------|----------|--------|---------|
| **Claude Code** | Outbound | CLI/subprocess | `coder_adapters.py` | LLM step execution via `claude` CLI |
| **Codex CLI** | Outbound | CLI/subprocess | `coder_adapters.py` | LLM step execution via `codex` CLI |
| **Qwen Code** | Outbound | CLI/subprocess | `coder_adapters.py` | LLM step execution via `qwen` CLI |
| **Backend API** | Bidirectional | HTTP/REST | `backend_client.py` | Worker registration, claim, heartbeat, completion |
| **ComfyUI** | Outbound | HTTP/WebSocket | `actions/submit_comfyui.py` | Image/video generation workflows |
| **Pushover** | Outbound | HTTP API | `notifications.py` | Mobile push notifications |
| **Filesystem** | Bidirectional | Local I/O | All modules | Artifact storage, job state, logs |

### 4.2 Backend API Contract

| Endpoint | Method | Request Body | Response | Module Function |
|----------|--------|--------------|----------|-----------------|
| `/workers/register` | POST | `{worker_id, host_name, capabilities, worker_label}` | Worker record | `register_worker()` |
| `/workers/heartbeat` | POST | `{worker_id, status, current_step_run_id, ...}` | Ack | `heartbeat()` |
| `/steps/claim` | POST | `{worker_id}` | Step run or 204 | `claim_step()` |
| `/steps/{id}/complete` | POST | `{exit_code, log_file, state, artifacts, ...}` | Completion record | `complete_step_run()` |
| `/runs` | POST | `{workflow_name, initiative_id, ...}` | Run record | `submit_run()` |
| `/runs/{id}/approve` | POST | `{action, feedback, outcome}` | Updated run | `approve_run()` |
| `/runs/{id}` | GET | — | Run details | `get_run()` |
| `/artifacts` | POST | `{run_id, artifact_type, file_path, content}` | Artifact record | `create_artifact()` |
| `/events` | POST | `{run_id, event_type, message, ...}` | Event record | `create_event()` |

### 4.3 LLM Coder Interface

| Coder | Command Pattern | Output Contract | Timeout Default |
|-------|-----------------||-----------------|-----------------|
| Claude | `claude --prompt-file <path> --output-dir <dir>` | meta.json in output dir | 600s |
| Codex | `codex --prompt-file <path> --output-dir <dir>` | meta.json in output dir | 600s |
| Qwen | `qwen --prompt-file <path> --output-dir <dir>` | meta.json in output dir | 600s |

**Sidecar Contract (meta.json):**
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "Brief summary of what was accomplished",
    "artifacts": {
      "ARTIFACT_KEY_NAME": "relative/path/to/file.md"
    },
    "recorded_at": "2026-07-09T21:34:12+08:00"
  }
}
```

---

## 5. Module Areas and Responsibilities

### 5.1 Module Area Classification

| Module | Area | Lines | Responsibility Summary |
|--------|------|-------|------------------------|
| `run_agent.py` | core | ~2,300 | CLI entry point, command dispatch, top-level orchestration |
| `step_runner.py` | core | ~2,400 | Prompt rendering, coder/action invocation, sidecar validation |
| `workflow_router.py` | core | ~800 | Post-step routing, approve/reject/failure handling |
| `job_state.py` | state | ~1,800 | Job.json lifecycle, state transitions, retry logic |
| `coder_adapters.py` | coder | ~1,000 | LLM coder invocation (Claude/Codex/Qwen), polling |
| `backend_client.py` | backend | ~400 | HTTP client for backend API communication |
| `daemon.py` | backend | ~600 | Worker supervisor, child process management |
| `runtime_context.py` | state | ~500 | Runtime path resolution, context management |
| `bundle_loader.py` | bootstrap | ~600 | Workflow bundle loading, workspace initialization |
| `constants.py` | support | ~1,000 | Centralized artifact keys and path constants |
| `actions/*.py` | actions | ~3,500 | 29 deterministic runner actions |

### 5.2 Module Boundary Contracts

#### Core Layer (run_agent, step_runner, workflow_router)

**Input:** CLI arguments, workflow bundle, job state  
**Output:** Updated job state, exit codes, sidecar files  
**Contracts:**
- Commands receive parsed args and execute to completion
- Steps receive context dict and produce StepResult
- Router receives StepResult and returns next state

#### State Layer (job_state, runtime_context)

**Input:** Job identifiers, step names, state mutations  
**Output:** Persistent job.json files, resolved paths  
**Contracts:**
- Job state is JSON-serializable and versioned (schema v6)
- Paths are resolved through runtime_context (lazy evaluation)
- All state mutations are atomic (write to temp, then rename)

#### Coder Layer (coder_adapters)

**Input:** Coder name, prompt text, working directory, timeout  
**Output:** InvocationResult with status, usage data, sidecar path  
**Contracts:**
- Subprocess execution with timeout enforcement
- Sidecar polling with configurable intervals
- Usage data aggregation for cost tracking

#### Actions Layer (actions/*.py)

**Input:** Step context dict, project_root, step_dir  
**Output:** StepResult with status, artifacts dict  
**Contracts:**
- Deterministic execution (no external API calls except specified)
- Self-contained artifact generation
- Return StepResult consistent with coder steps

---

## 6. Key Interaction Sequences

### 6.1 Workflow Step Execution Sequence

```
┌────────┐    ┌──────────────┐    ┌─────────────┐    ┌────────────┐    ┌──────────┐
│  CLI   │───▶│  run_agent.py  │───▶│ step_runner │───▶│  coder OR  │───▶│ meta.json │
│  User  │    │  main()        │    │  run_step() │    │  action    │    │ written   │
└────────┘    └──────────────┘    └─────────────┘    └────────────┘    └────┬───────┘
                                                                            │
┌────────┐    ┌──────────────┐    ┌─────────────┐    ┌────────────┐         │
│  Job   │◀───│ workflow_    │◀───│ step_runner │◀───│  validate  │◀────────┘
│ State  │    │ router.route │    │  enrich    │    │  sidecar   │
└────────┘    │ _after_step()│    │  _sidecar  │    │            │
              └──────────────┘    └─────────────┘    └────────────┘
```

**Sequence Steps:**
1. CLI parses arguments and dispatches to `main()`
2. `run_agent.py` loads workflow bundle and job state
3. `step_runner.run_step()` builds context and renders prompt
4. If coder step: `coder_adapters.invoke_coder()` spawns subprocess
5. Coder writes meta.json sidecar on completion
6. `step_runner` validates meta.json and artifact paths
7. `enrich_sidecar()` appends runner_data section
8. `workflow_router.route_after_step()` determines next step
9. Updated state saved to job.json

### 6.2 Review Loop Sequence

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Step Result │────▶│ router.route_    │────▶│ REJECTED status  │
│  REJECTED    │     │ after_step()     │     │ Check retry limit│
└─────────────┘     └──────────────────┘     └────────┬─────────┘
                                                      │
                        ┌─────────────────────────────┘
                        │
                        ▼
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Next step  │◀────│ retry < max      │◀────│ Increment retry  │
│  = REFINE   │     │ NO ──▶ FAIL      │     │ counter          │
│  (retry)    │     │ YES ──▶ Continue │     │                  │
└─────────────┘     └──────────────────┘     └──────────────────┘
```

**Retry Logic:**
- Max rejects configurable per workflow (default: 3)
- REJECTED steps route to REFINE step if available
- Exhausted retries route to REPLAN or FAILURE

### 6.3 Failure Handling Sequence

```
┌──────────────────┐
│ Exception thrown │
│ during step      │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ workflow_router.route_after_failure()    │
│ - classify_pre_run_failure(exc)         │
│ - set_last_failure() in state            │
│ - append_failure_history()                 │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ CONTROL_CLASS determination              │
│ - AUTO_RETRYABLE (transient errors)      │
│ - HUMAN_RETRY_REQUIRED (env issues)        │
│ - FATAL (code defects)                   │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ State updated with:                      │
│ - last_failure envelope                  │
│ - failure_history[] entry                │
│ - next_step = FAILURE or RETRY           │
└──────────────────────────────────────────┘
```

**Failure Classification:**
| Source | Example | Control Class |
|--------|---------|---------------|
| Coder process | Timeout, crash | HUMAN_RETRY_REQUIRED |
| Pre-run check | Missing artifact | AUTO_RETRYABLE (if transient) |
| Validation | Schema mismatch | FATAL |
| Filesystem | Permission denied | HUMAN_RETRY_REQUIRED |

---

## 7. Extension Points

### 7.1 Adding New Actions

**Location:** `agent_runner_v2/actions/<new_action>.py`  
**Registration:** Add to `__init__.py` action registry  
**Contract:**
```python
def run_action(*, action_name: str, state: dict, step: str, 
               step_cfg: dict, step_dir: Path, project_root: Path, 
               context: dict[str, str]) -> StepResult:
    # Implementation
    return StepResult(...)
```

**Steps:**
1. Create new module in `actions/` directory
2. Import required dependencies (runtime_context, constants)
3. Implement action function with standard signature
4. Add action name to `__init__.py` registry
5. Reference in workflow step config as `action: <name>`

### 7.2 Adding New Coders

**Location:** `agent_runner_v2/coder_adapters.py`  
**Requirements:** CLI tool supporting `--prompt-file` and `--output-dir`

**Steps:**
1. Add coder name to `SUPPORTED_CODERS` constant
2. Implement command builder in `_build_coder_command()`
3. Add timeout configuration in `model_config.py`
4. Create prompt template directory: `prompts/<workflow>/<step>_<coder>.txt`

### 7.3 Adding New Workflow Families

**Location:** `agent_runner_v2/bootstrap/workflows/default/template_groups.py`  
**Assets:**
- Step definitions in `TEMPLATE_GROUPS`
- Prompt templates in `prompts/<workflow_family>/`

**Steps:**
1. Define workflow in `template_groups.py`
2. Create prompt template files
3. Run `ukbe-run-agent init` to seed to runtime bundle
4. Create batch launcher: `run-<workflow>.bat`

### 7.4 Backend Integration Extension

**Location:** `agent_runner_v2/backend_client.py`  
**Pattern:** Add method following existing REST client pattern

**Example:**
```python
def new_endpoint(self, *, param1: str, param2: str) -> dict[str, Any]:
    url = f"{self.base_url}/new/endpoint"
    body = {"param1": param1, "param2": param2}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())
```

---

## 8. Runtime Environment

### 8.1 Path Resolution Hierarchy

```
Workspace Paths:
├── project_root/                      (git repo root)
│   ├── docs/
│   │   ├── system/00_governance/      (system docs)
│   │   ├── codebase/                  (codebase docs)
│   │   ├── operations/                (operational guides)
│   │   └── site/                      (generated HTML sites)
│   └── .env, .gitignore, etc.
│
Runner Home (~/.ukbe-runner/):
├── config.json                        (runner configuration)
├── jobs/                              (job state storage)
│   └── <workflow>/
│       └── <job_id>/
│           ├── job.json               (job state)
│           └── <step>/
│               ├── meta.json            (step result)
│               └── <artifacts>          (step outputs)
├── workflows/                         (runtime workflow bundles)
│   └── <workflow>/
│       ├── template_groups.py         (workflow definition)
│       └── prompts/                   (prompt templates)
└── logs/                              (execution logs)
```

### 8.2 Bootstrap vs Runtime

| Aspect | Bootstrap (Repo) | Runtime (Global) |
|--------|------------------|------------------|
| **Location** | `agent_runner_v2/bootstrap/` | `~/.ukbe-runner/workflows/` |
| **Purpose** | Development source, version control | Active execution source |
| **Updates** | Git commits, code changes | `ukbe-run-agent init`, sync scripts |
| **Loading** | `bundle_loader.py` | `runtime_context.py` |

**Critical Rule:** Runtime always loads from global runner home, not the repo. Changes to bootstrap files must be synced before they take effect.

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-07-09 | Initial integration map generated | 00_master_docs_bootstrap_v1 |
