---
template_id: "CB-04-IM"
title: "Integration Map - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04b_generate_integration_docs"
managed_by: workflow-generated
generated: "2026-07-10T10:02:42+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04b_generate_integration_docs`
> This file is workflow-generated and protected from manual edits.

# Integration Map: agent-runner-v2

## 1. Overview

This document maps the integration points, module dependencies, and data flows within the agent-runner-v2 system. It serves as a reference for understanding how components interact and where external system boundaries exist.

## 2. Module Dependency Graph

### 2.1 Core Module Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLI Entry Points                                │
│  run_agent.py (CLI) → daemon.py (supervisor) → backend_client.py (API)    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Execution Orchestration                            │
│                    step_runner.py → workflow_router.py                       │
│                         │              │                                     │
│                         ▼              ▼                                     │
│              coder_adapters.py    job_state.py                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Runtime Context & State                            │
│         runtime_context.py ← constants.py ← bundle_loader.py               │
│         doc_paths.py ← artifact_paths.py                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Deterministic Actions                              │
│   actions/ (29 modules) → validation, sync, generation, submission         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Dependency Details

| Module | Depends On | Purpose |
|--------|------------|---------|
| `run_agent.py` | `step_runner`, `workflow_router`, `job_state`, `bundle_loader`, `runtime_context`, `constants` | CLI entry point and orchestration |
| `step_runner.py` | `coder_adapters`, `job_state`, `runtime_context`, `constants`, `documentation_guardrails` | Core step execution contract |
| `workflow_router.py` | `job_state`, `notifications`, `step_runner` | Post-step routing logic |
| `coder_adapters.py` | `runtime_context` | LLM invocation (Claude/Codex/Qwen) |
| `job_state.py` | `runtime_context`, `notifications`, `documentation_guardrails` | Job.json lifecycle management |
| `backend_client.py` | — | Backend API client (HTTP) |
| `daemon.py` | `job_state`, `runtime_context` | Worker supervisor |
| `bundle_loader.py` | `runtime_context`, `bundle_taxonomy` | Bootstrap seeding and bundle loading |
| `runtime_context.py` | — | Process-local context management |
| `constants.py` | — | Centralized path constants (SSOT) |

## 3. Data Flow Diagrams

### 3.1 Main Execution Flow (Manual Mode)

```
┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CLI    │───▶│ Load Config │───▶│ Resolve Job │───▶│ Run Preflight│
│  Input   │    │   /Init     │    │   State     │    │   Checks    │
└──────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Route to │◀───│ Read Meta   │◀───│  Invoke     │◀───│   Render    │
│ Next Step│    │   .json     │    │   Coder     │    │   Prompt    │
└──────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     │
     ▼
┌──────────┐    ┌─────────────┐    ┌─────────────┐
│ Validate │───▶│  Update Job │───▶│   Repeat    │
│ Artifacts│    │   State     │    │ or Complete │
└──────────┘    └─────────────┘    └─────────────┘
```

### 3.2 Backend-Connected Worker Flow

```
┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Daemon  │───▶│  Register   │───▶│   Heartbeat │───▶│ Claim Step  │
│  Start   │    │   Worker    │    │   (loop)    │    │             │
└──────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Submit   │◀───│ Child Proc  │◀───│  Spawn      │◀───│ execute-step│
│  Result   │    │   Exits     │    │  Subprocess │    │   Command   │
└──────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     │
     ▼
┌──────────┐
│ Backend  │
│ Notified │
└──────────┘
```

### 3.3 Bootstrap-to-Runtime Flow

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Packaged Source  │───▶│  Publish Bundle  │───▶│ Global Runtime   │
│ (repo/bootstrap) │    │ (bootstrap/      │    │ (~/.ukbe-runner) │
│                  │    │  bundles/core)   │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                               │                          │
                               ▼                          ▼
                        ┌──────────────┐          ┌──────────────┐
                        │  Install to  │          │  Workflow    │
                        │  Global Home │─────────▶│  Execution   │
                        └──────────────┘          └──────────────┘
```

## 4. Integration Points with External Systems

### 4.1 External Systems Table

| System | Direction | Protocol | Purpose |
|--------|-----------|----------|---------|
| **Backend API** | Bidirectional | HTTP/REST (JSON) | Run/step lifecycle, artifact storage, worker coordination |
| **Claude API** | Outbound | HTTP/REST (Anthropic) | LLM coding tasks |
| **Codex API** | Outbound | HTTP/REST (OpenAI) | LLM coding tasks |
| **Qwen Code** | Internal | In-process | Local LLM execution |
| **ComfyUI** | Outbound | HTTP/REST | Image generation (T2I, I2V) |
| **Pushover** | Outbound | HTTP/REST | Mobile notifications |
| **Git** | Outbound | CLI/subprocess | Repository operations |
| **File System** | Local | OS-native | Artifact storage |

### 4.2 Backend API Integration

```
┌─────────────────┐         ┌─────────────────┐
│   BackendClient │◀───────▶│  Backend Server │
│  (backend_)     │  HTTP   │  (Port 8100)    │
│                 │         │                 │
│ - submit_run()  │         │ - /api/runs     │
│ - approve_run() │         │ - /api/workers  │
│ - claim_step()  │         │ - /api/step-runs│
│ - heartbeat()   │         │                 │
└─────────────────┘         └─────────────────┘
```

**Key Endpoints:**
- `POST /api/runs` - Submit new workflow run
- `GET /api/runs/{id}` - Get run status
- `POST /api/runs/{id}/approve` - Approve/reject run
- `POST /api/workers/register` - Register worker
- `POST /api/workers/claim` - Claim work item
- `POST /api/workers/heartbeat` - Worker heartbeat
- `POST /api/step-runs/{id}/complete` - Complete step

### 4.3 LLM Provider Integration

```
┌─────────────────┐
│  coder_adapters │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Claude │ │ Codex │ │ Qwen  │ │ Aliased│
│  API  │ │  API  │ │ Code  │ │ Models │
└───────┘ └───────┘ └───────┘ └───────┘
```

**Coder Adapter Responsibilities:**
- Invoke LLM with prompt and context
- Poll for sidecar (meta.json) completion
- Parse usage data (tokens, cost, duration)
- Handle timeouts and failures

## 5. Module Areas and Responsibilities

### 5.1 Core Execution (run_agent.py, step_runner.py, workflow_router.py)

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `run_agent.py` | ~2,300 | CLI entry point, command dispatch, manual mode orchestration |
| `step_runner.py` | ~2,650 | Step execution contract, prompt rendering, artifact validation |
| `workflow_router.py` | ~787 | Post-step routing (APPROVE/REJECT/failure paths) |

**Key Interaction:**
```
run_agent.run_step() 
  → step_runner.run_step() [invoke coder, validate]
    → workflow_router.route_after_step() [routing decision]
      → job_state.advance_step() [state update]
```

### 5.2 State Management (job_state.py, runtime_context.py)

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `job_state.py` | ~1,800 | Job.json CRUD, status transitions, retry logic |
| `runtime_context.py` | ~301 | Process-local context (paths, workflow module) |

**Key Interaction:**
```
step_runner uses runtime_context for paths
  → job_state persists to job.json
    → bundle_loader loads workflow definitions
```

### 5.3 Coder Integration (coder_adapters.py)

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `coder_adapters.py` | ~1,040 | LLM invocation, sidecar polling, usage tracking |

**Key Flow:**
```
invoke_coder() → Spawn subprocess → Poll meta.json → Parse result
```

### 5.4 Actions Package (29 modules)

| Category | Modules | Purpose |
|----------|---------|---------|
| Validation | `validate_*.py` (10 modules) | Document/site validation |
| Sync | `sync_*.py` (2 modules) | Documentation synchronization |
| Generation | `generate_*.py` (4 modules) | Site/PDF generation |
| Submission | `submit_comfyui.py`, `execute_*.py` | External service submission |
| Scaffold | `prepare_delivery_scaffold.py`, `finalize_bootstrap.py` | Workflow setup |

## 6. Key Interaction Sequences

### 6.1 Workflow Step Execution Sequence

```
1. run_agent.run_workflow_step()
   └── Load job state (job_state.load_job)
   └── Resolve workflow bundle (bundle_loader)
   └── Build context (step_runner.build_context)
   └── Render prompt (step_runner.render_prompt)

2. step_runner.run_step()
   └── Validate step config
   └── Resolve allowed write paths
   └── Invoke coder (coder_adapters.invoke_coder)
   └── Poll for meta.json
   └── Validate artifacts exist
   └── Enrich sidecar with usage data

3. workflow_router.route_after_step()
   └── Check step_result.status
   ├── APPROVED → advance_step → save_job
   └── REJECTED → handle retry/replan → save_job

4. run_agent (next iteration)
   └── Load updated job state
   └── Continue to next step
```

### 6.2 Review/Refine Loop Sequence

```
1. Initial generation step
   └── Produces ARTIFACT_SUGGESTED
   └── Status: APPROVED (content generated)

2. Review step
   └── Reads ARTIFACT_SUGGESTED
   └── Produces REVIEW_FILE_SUGGESTED
   └── Status: APPROVED or REJECTED

3. If REJECTED:
   └── Refine step (with edit_mode: in_place)
   └── Updates artifact in place
   └── Returns to Review step
   └── Loop iteration counter incremented

4. Max iterations enforced:
   └── After N rejections → WAITING_FOR_HUMAN_INTERVENTION
```

### 6.3 Failure Handling Sequence

```
1. Exception raised in step_runner.run_step()
   ├── CoderInvocationError (subprocess failure)
   ├── MetaJsonMissingError (no sidecar written)
   ├── MetaJsonInvalidError (invalid sidecar schema)
   └── ArtifactMissingError (referenced file missing)

2. workflow_router.route_after_failure()
   └── Classify exception → failure_class/failure_code
   └── Update reject_counts
   └── set_last_failure(state, ...)
   └── append_failure_history

3. Routing decision:
   ├── AUTO_RETRYABLE → WAITING_FOR_AUTO_RETRY
   ├── HUMAN_RETRY_REQUIRED → WAITING_FOR_HUMAN_INTERVENTION
   └── FATAL → terminal failure

4. Daemon/manual mode handles accordingly
   └── Auto-retry: daemon re-claims same step
   └── Human intervention: blocks for approval
```

## 7. Internal Module Boundaries

### 7.1 Bootstrap vs Runtime Boundary

```
┌─────────────────────────────────────────┐     ┌─────────────────────────────────────────┐
│         PACKAGED BOOTSTRAP              │     │          RUNTIME EXECUTION              │
│  (agent_runner_v2/bootstrap/)           │     │       (~/.ukbe-runner/)                 │
│                                         │     │                                         │
│  • template_groups.py (definitions)     │────▶│  • workflows/<name>/template_groups.py  │
│  • prompts/ (prompt templates)           │     │  • prompts/ (runtime copies)            │
│  • bundles/core/ (master docs)            │     │  • jobs/ (job state)                    │
│                                         │     │  • config.json (global settings)        │
└─────────────────────────────────────────┘     └─────────────────────────────────────────┘
              │                                                  │
              └───────────────── Sync via ─────────────────────────┘
                  ukbe-run-agent init
                  ukbe-run-agent bootstrap-publish
```

### 7.2 Documentation Guardrails Boundary

```
┌─────────────────────────────────────────────────────────────────┐
│                    documentation_guardrails.py                   │
│                                                                  │
│  • Generated doc manifest (what files are workflow-managed)     │
│  • Managed banner injection (auto-added to generated docs)      │
│  • Workflow ownership rules (which workflows can write where) │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   step_runner    │ │   job_state     │ │   run_agent     │
│  (validate      │ │ (status rules)  │ │ (enforce        │
│   produces)      │ │                 │ │   boundaries)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 8. Extension Points

### 8.1 Adding New Actions

1. Create module in `agent_runner_v2/actions/`
2. Define `run()` function with signature:
   ```python
   def run(*, context: dict, state: dict, **kwargs) -> dict:
       ...
   ```
3. Register in `actions/__init__.py` ACTION_REGISTRY
4. Reference from workflow step config as `action: module_name`

### 8.2 Adding New Coder Types

1. Add entry to `model_mapping.json` (coder → provider mapping)
2. Implement adapter in `coder_adapters.py` (if needed)
3. Configure in `config.json` coder section

### 8.3 Adding New Workflow Families

1. Define in `template_groups.py` TEMPLATE_GROUPS
2. Create prompt templates in `bootstrap/workflows/default/prompts/`
3. Run `ukbe-run-agent bootstrap-publish` to sync
4. Create launcher batch file

## 9. File System Layout Integration

### 9.1 Runtime Directory Structure

```
~/.ukbe-runner/
├── config.json                 # Global configuration
├── workflows/
│   └── default/
│       ├── template_groups.py  # Workflow definitions
│       └── prompts/            # Prompt templates
├── jobs/
│   └── <workflow>/
│       └── <job_id>/
│           ├── job.json        # Job state
│           └── <step>/
│               ├── prompt.txt  # Rendered prompt
│               ├── meta.json   # Step result sidecar
│               └── artifacts/  # Step outputs
├── bundles/
│   └── core/
│       └── current/            # Bootstrap bundle
└── logs/
    └── daemon/                 # Daemon logs
```

### 9.2 Repository Directory Structure

```
agent_runner_v2/
├── run_agent.py          # CLI entry
├── step_runner.py        # Step execution
├── workflow_router.py    # Routing logic
├── job_state.py          # State management
├── coder_adapters.py     # LLM adapters
├── backend_client.py     # API client
├── daemon.py             # Worker supervisor
├── constants.py          # Centralized constants
├── runtime_context.py    # Context management
├── bundle_loader.py      # Bundle management
├── actions/              # 29 action modules
├── bootstrap/            # Packaged workflows
│   ├── workflows/default/
│   └── bundles/core/
└── tools/                # Utility modules
```

## 10. Change Log

| Date | Change | Modules Affected | Verified By |
|------|--------|------------------|-------------|
| 2026-07-10 | Initial integration map generated | All | 00_master_docs_bootstrap_v1 |

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04b_generate_integration_docs` on 2026-07-10T10:02:42+08:00*
