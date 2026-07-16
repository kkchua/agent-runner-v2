---
template_id: "CB-04-IM"
version: "1.0.0"
doc_type: "codebase"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:33:38+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04b_generate_integration_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Integration Map: agent-runner-v2

## 1. Overview

This document maps how modules connect, data flows through the system, and integration points with external systems. It serves as the authoritative reference for understanding runtime behavior and extension points.

## 2. Module Dependency Graph

### 2.1 Layer Architecture

The system follows a layered architecture with clear dependency direction:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLI ENTRY POINTS                                   │
│  run_agent.py (main) │ daemon.py (worker) │ submit_commands.py              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RUNTIME LAYER                                      │
│  manual_runtime.py │ daemon_runtime.py │ cli_runtime.py                     │
│  execution_core.py │ step_execution_runtime.py                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                                │
│  step_runner.py │ workflow_router.py │ routing_runtime.py                   │
│  transition_runtime.py │ task_runtime.py                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│        CODER LAYER             │   │        STATE LAYER             │
│  coder_adapters.py            │   │  job_state.py                 │
│  model_config.py              │   │  runtime_context.py           │
│  runner_logger.py             │   │  execution_request.py         │
└───────────────────────────────┘   │  execution_result.py          │
                │                   └───────────────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SUPPORT LAYER                                      │
│  constants.py │ doc_paths.py │ documentation_guardrails.py                 │
│  exceptions.py │ runtime_utils.py │ state_defaults.py                      │
│  notification_manager.py │ notifications.py                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND LAYER                                      │
│  backend_client.py │ runner_logger.py                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ACTIONS LAYER                                      │
│  actions/*.py (29 modules)                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Module Dependencies

| Module | Depends On | Provides |
|--------|------------|----------|
| `run_agent.py` | `step_runner`, `job_state`, `workflow_router`, `coder_adapters`, `backend_client` | CLI entry point, command routing |
| `step_runner.py` | `coder_adapters`, `runtime_context`, `constants`, `exceptions` | Step execution contract, prompt rendering |
| `workflow_router.py` | `step_runner`, `job_state`, `failure_runtime`, `recovery_runtime` | Post-step routing logic |
| `coder_adapters.py` | `model_config`, `runner_logger`, `runtime_context` | LLM invocation, sidecar handling |
| `job_state.py` | `constants`, `doc_paths`, `documentation_guardrails`, `exceptions` | Job lifecycle management |
| `backend_client.py` | `urllib` (stdlib) | Backend API communication |
| `daemon.py` | `config_loader`, `runtime_context` | Worker daemon supervisor |

### 2.3 Workflow Package Dependencies

```
workflow_packages/
├── base.py          → (dataclasses only) - WorkflowBundle, StepConfig definitions
├── loader.py        → base.py, runtime_context - Bundle loading and conversion
├── registry.py      → base.py, loader.py - Package registration
└── actions/__init__.py → runner_actions - Action decorator registry
```

## 3. Data Flow Diagrams

### 3.1 Manual Execution Flow

```
User CLI Command
       │
       ▼
┌─────────────────┐
│ parse_args()    │  ← Parse CLI arguments
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ load_project_   │  ← Read config.json
│ config()        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ load_workflow_  │  ← Load workflow.toml → WorkflowBundle
│ module()        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ resolve_manual_ │  ← Find/create job, determine step
│ run()           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ _prepare_step_  │  ← Build context, render prompt
│ execution()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ run_step() or   │  ← Execute coder or action
│ run_action()    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ route_after_    │  ← Determine next step based on result
│ step()          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ save_job()      │  ← Persist job.json state
└─────────────────┘
```

### 3.2 Daemon Worker Flow

```
Backend Poll Loop
       │
       ▼
┌─────────────────┐
│ BackendClient.  │  ← GET /api/worker/{id}/claim
│ claim_step()    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build request   │  ← Create ExecutionRequest from claim
│ payload         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ subprocess run  │  ← Spawn: python -m agent_runner_v2.run_agent run
│ agent.py        │     (identical to manual execution)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Read meta.json  │  ← Parse coder result from sidecar
│ sidecar         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BackendClient.  │  ← POST /api/step-runs/{id}/complete
│ complete_step() │
└─────────────────┘
```

### 3.3 Step Execution Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                         STEP EXECUTION                               │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐                                                │
│  │ build_context() │  ← Merge state + workflow context               │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │ render_prompt() │  ← Substitute placeholders with context values  │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐     ┌─────────────────┐                        │
│  │  CODER STEP?    │──No─→│ run_action()    │                        │
│  └────────┬────────┘     │ (Python call)   │                        │
│           │              └────────┬────────┘                        │
│           │Yes                   │                                  │
│           ▼                      │                                  │
│  ┌─────────────────┐             │                                  │
│  │ invoke_coder()  │             │                                  │
│  │ via subprocess  │             │                                  │
│  └────────┬────────┘             │                                  │
│           │                      │                                  │
│           ▼                      │                                  │
│  ┌─────────────────┐             │                                  │
│  │ Poll meta.json  │             │                                  │
│  │ sidecar         │             │                                  │
│  └────────┬────────┘             │                                  │
│           │                      │                                  │
│           ▼                      │                                  │
│  ┌─────────────────┐             │                                  │
│  │ validate        │             │                                  │
│  │ artifacts       │             │                                  │
│  └────────┬────────┘             │                                  │
│           │                      │                                  │
│           └──────────┬───────────┘                                  │
│                      │                                              │
│                      ▼                                              │
│           ┌─────────────────┐                                       │
│           │ enrich_sidecar()│  ← Add runner_data section            │
│           └────────┬────────┘                                       │
│                    │                                                 │
│                    ▼                                                 │
│           ┌─────────────────┐                                       │
│           │ return          │                                       │
│           │ StepResult      │                                       │
│           └─────────────────┘                                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.4 Routing Flow

```
StepResult
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│                    ROUTING DECISION                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  result.status == "APPROVED"                               │
│       │                                                    │
│       ├─── on_approve == "next_step" ──→ advance_step()    │
│       │                                                    │
│       ├─── on_approve == "loop_refine" ──→ loop context    │
│       │                                                    │
│       └─── requires_human_approval_after ──→ WAITING       │
│                                                            │
│  result.status == "REJECTED"                               │
│       │                                                    │
│       ├─── reject_count < max_rejects                      │
│       │        │                                           │
│       │        └─── on_reject_refine ──→ return to refine  │
│       │                                                    │
│       └─── reject_count >= max_rejects                     │
│                │                                           │
│                └─── on_exhaust_replan ──→ replan           │
│                                                            │
│  Exception (hard failure)                                  │
│       │                                                    │
│       └─── route_after_failure() ──→ failure_runtime       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## 4. Integration Points

### 4.1 External Systems

| System | Direction | Protocol | Module | Purpose |
|--------|-----------|----------|--------|---------|
| Backend API | Outbound | HTTP/JSON | `backend_client.py` | Job claims, heartbeats, step completion |
| LLM Coder | Outbound | Subprocess/CLI | `coder_adapters.py` | Prompt execution, text generation |
| ComfyUI | Outbound | HTTP/API | `actions/submit_comfyui.py` | Image/video generation |
| Pushover | Outbound | HTTPS/API | `notification_manager.py` | Step completion notifications |
| Filesystem | In/Out | Local I/O | `job_state.py`, `step_runner.py` | Job state, artifacts, prompts |

### 4.2 Backend API Endpoints

| Endpoint | Method | Module | Purpose |
|----------|--------|--------|---------|
| `/api/worker/{id}/register` | POST | `backend_client.py` | Worker registration |
| `/api/worker/{id}/heartbeat` | POST | `backend_client.py` | Health monitoring |
| `/api/worker/{id}/claim` | POST | `backend_client.py` | Claim pending step |
| `/api/step-runs/{id}/complete` | POST | `backend_client.py` | Report step result |
| `/api/step-runs/{id}/sync-job-state` | POST | `backend_client.py` | Sync job.json to backend |
| `/api/workflow-runs` | POST | `backend_client.py` | Submit new workflow run |
| `/api/workflow-runs/{id}` | GET | `backend_client.py` | Get run status |
| `/api/admin/execution/cleanup` | POST | `backend_client.py` | Delete workflow runs |

### 4.3 Coder Integration Contract

The coder integration follows a subprocess-based contract:

```
┌─────────────────┐                    ┌─────────────────┐
│ coder_adapters  │ ──subprocess───→   │ LLM Coder       │
│ .invoke_coder() │                    │ (OpenCode,      │
└────────┬────────┘                    │  Claude, etc.)  │
         │                             └────────┬────────┘
         │                                      │
         │  ┌──────────────────────────────┐    │
         │  │ Prompt rendered to cwd/      │    │
         │  │ prompt.txt                   │    │
         │  └──────────────────────────────┘    │
         │                                      │
         │                              ┌───────┴───────┐
         │                              │ Coder reads   │
         │                              │ prompt.txt    │
         │                              │ writes files  │
         │                              │ writes        │
         │                              │ meta.json     │
         │                              └───────┬───────┘
         │                                      │
         ▼                                      ▼
┌─────────────────────────────────────────────────────────┐
│ Poll loop checks for meta.json sidecar                  │
│ - Validates schema (schema_version, coder_result)       │
│ - Checks artifact existence                             │
│ - Enriches with runner_data                             │
└─────────────────────────────────────────────────────────┘
```

### 4.4 Sidecar Contract (meta.json)

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "Brief summary",
    "artifacts": {
      "ARTIFACT_KEY": "relative/path/to/artifact.md"
    },
    "recorded_at": "2026-07-16T22:33:38+08:00"
  },
  "runner_data": {
    "step": "01_generate",
    "coder_used": "opencode",
    "invoked_at": "2026-07-16T22:30:00+08:00",
    "finished_at": "2026-07-16T22:33:38+08:00",
    "prompt_checksum": "abc123",
    "changed_paths": ["docs/repo/codebase/01_inventory/INTEGRATION_MAP.md"]
  },
  "usage": {
    "input_tokens": 5000,
    "output_tokens": 2000,
    "total_tokens": 7000,
    "duration_ms": 200000
  }
}
```

## 5. Module Areas and Responsibilities

### 5.1 Core Area

| Module | Responsibility |
|--------|---------------|
| `run_agent.py` | Main CLI entry point, command routing, execution orchestration |
| `step_runner.py` | Step execution contract, prompt rendering, artifact validation |
| `workflow_router.py` | Post-step routing, approve/reject/replan logic |

### 5.2 Coder Area

| Module | Responsibility |
|--------|---------------|
| `coder_adapters.py` | LLM subprocess invocation, timeout handling, sidecar polling |
| `model_config.py` | Coder role resolution, model mapping, role policy lookup |

### 5.3 Backend Area

| Module | Responsibility |
|--------|---------------|
| `daemon.py` | Worker daemon supervisor, poll loop, subprocess spawning |
| `backend_client.py` | HTTP client for backend API, request/response handling |
| `runner_logger.py` | Structured logging with backend sink capability |

### 5.4 State Area

| Module | Responsibility |
|--------|---------------|
| `job_state.py` | Job lifecycle management, state transitions, task queue |
| `runtime_context.py` | Global context, path resolution, workflow module access |
| `execution_request.py` | Execution request schema for daemon-to-runner communication |
| `execution_result.py` | Execution result schema for result reporting |

### 5.5 Support Area

| Module | Responsibility |
|--------|---------------|
| `constants.py` | Centralized path constants, artifact keys, folder definitions |
| `doc_paths.py` | Documentation path helpers (deprecated, consolidated into constants) |
| `documentation_guardrails.py` | Document protection, deletion safety, scaffold workflows |
| `exceptions.py` | Custom exception hierarchy |
| `notification_manager.py` | Pushover notification dispatch |
| `runtime_utils.py` | Shared utility functions |

### 5.6 Actions Area

29 deterministic action modules implementing non-coder steps:

| Category | Modules |
|----------|---------|
| **Validation** | `validate_codebase_docs`, `validate_system_docs`, `validate_delivery_docs`, `validate_architecture_site`, `validate_developer_site`, `validate_operator_site`, `validate_stakeholder_site`, `validate_tester_site`, `validate_user_site` |
| **Sync** | `sync_codebase_docs`, `sync_system_docs` |
| **Generation** | `generate_site`, `generate_site_pdf`, `publish_architecture_site` |
| **Bootstrap** | `finalize_bootstrap`, `prepare_delivery_scaffold`, `archive_previous_version` |
| **Promotion** | `promote_artifact`, `promote_init` |
| **Media** | `execute_t2i`, `execute_i2v`, `execute_voiceover`, `assemble_video`, `submit_comfyui` |
| **Utility** | `copy_artifact`, `step_completion`, `scan_repo_codebase` |

### 5.7 Workflow Package Area

| Module | Responsibility |
|--------|---------------|
| `base.py` | Dataclass definitions: WorkflowBundle, StepConfig, BundleGovernance |
| `loader.py` | TOML parsing, bundle loading, dict conversion |
| `registry.py` | Package registration and discovery |

## 6. Key Interaction Sequences

### 6.1 New Job Creation

```
1. CLI: python -m agent_runner_v2.run_agent run --template-group XXX
2. run_agent.parse_args() → args
3. load_project_config(workspace_root) → config
4. load_workflow_module() → WorkflowBundle
5. resolve_manual_run() → create_job()
   - make_job_id() generates unique ID
   - create step directory structure
   - save initial job.json
6. return state with current_step = init step
```

### 6.2 Coder Step Execution

```
1. _prepare_step_execution()
   - build_context(state, step, step_cfg)
   - resolve_prompt_path() → find prompt template
   - render_prompt(template, context) → prompt_text
   - prompt_checksum(prompt_text) → checksum

2. run_step()
   - invoke_coder(coder, prompt_text, cwd, schema_path, ...)
     - Write prompt.txt to step directory
     - Spawn subprocess: coder CLI with schema argument
     - Poll for meta.json appearance
     - Validate sidecar schema
   - Read meta.json → coder_result
   - Validate artifact paths exist on disk
   - enrich_sidecar() with runner_data
   - return StepResult

3. route_after_step()
   - Parse result.status
   - Apply routing rules from step_cfg
   - advance_step() or loop handling
   - save_job()
```

### 6.3 Action Step Execution

```
1. run_action(action_name, state, step, step_cfg, ...)
   - Lookup action in registry (from @action() decorator)
   - Execute action function with parameters
   - Action directly modifies files
   - return StepResult

2. route_after_step() (same as coder)
```

### 6.4 Failure Handling

```
1. Exception raised from run_step() or run_action()
2. route_after_failure(exc, ...)
   - Classify exception type
   - Build failure envelope
   - Set job status: WAITING_FOR_HUMAN_INTERVENTION
   - Record failure history
   - Send notification if enabled
   - save_job()
3. Return exit code 2 (failure)
```

### 6.5 Human Approval Gate

```
1. Step completes with result.status = "APPROVED"
2. Step cfg has requires_human_approval_after = true
3. route_after_step() sets:
   - status: WAITING_FOR_HUMAN_INTERVENTION
   - pending_intervention_for: step
4. save_job() and exit
5. User runs: approve-step --job-id XXX --step YYY
6. approve_step() updates:
   - status: IN_PROGRESS
   - review.decision: APPROVED
   - advance_step() to next step
7. save_job()
```

## 7. Extension Points

### 7.1 Adding a New Workflow

1. Create directory: `workflows/<workflow_name>/`
2. Define `workflow.toml` with steps, routing, artifact contracts
3. Create `prompts/` directory with step prompt templates
4. Optionally add `context_extensions.py` for workflow-specific context hooks
5. Optionally add `actions.py` with `@action()` decorated functions

### 7.2 Adding a New Action

1. Create file: `agent_runner_v2/actions/<action_name>.py`
2. Define function with `@action()` decorator
3. Register in `agent_runner_v2/actions/__init__.py`
4. Reference in workflow.toml step config: `action = "<action_name>"`

### 7.3 Adding a New Coder

1. Add coder config to `_registry/coder_connections.json`
2. Add role mapping to `_registry/coder_roles.json`
3. Add policy to `_registry/role_policies.json`
4. Implement invocation in `coder_adapters.py` if non-standard CLI

### 7.4 Adding Backend Integration

1. Extend `backend_client.py` with new endpoint methods
2. Update `daemon.py` to handle new claim types if needed
3. Update `execution_request.py` schema if payload structure changes

## 8. Configuration Sources

### 8.1 Configuration Cascade

```
Priority 1: CLI arguments (--template-group, --coder, etc.)
    │
    ▼
Priority 2: Environment variables
    │ AGENT_RUNNER_BACKEND_URL
    │ AGENT_RUNNER_WORKER_ID
    │ AGENT_RUNNER_CODER_TIMEOUT_SECONDS
    │ WORKER_LABEL
    ▼
Priority 3: Global config.json (~/.ukbe-runner/config.json)
    │ backend_url, engine_root, coder_timeout_seconds
    ▼
Priority 4: Project config.json (<workspace>/.ukbe-runner/config.json)
    │ default_workflow, workflows.{name}.path
    ▼
Priority 5: Workflow workflow.toml defaults
    │ default_max_rejects, coder_default, etc.
    ▼
Priority 6: Hardcoded defaults in constants.py
```

### 8.2 Path Resolution

| Path | Source | Resolution |
|------|--------|------------|
| `RUNNER_ROOT` | `~/.ukbe-runner` | Global runner home |
| `JOBS_ROOT` | `{RUNNER_ROOT}/jobs` | Job state storage |
| `ARTIFACT_ROOT` | `{RUNNER_ROOT}/artifacts` | Artifact storage |
| `PACKAGE_ROOT` | `agent_runner_v2/` | Package root |
| `PROJECT_ROOT` | CLI `--project-root` | Workspace root |

## 9. Security Boundaries

### 9.1 Trust Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│ TRUSTED ZONE (runner process)                               │
│                                                             │
│  - Full filesystem access within project root               │
│  - Access to environment variables                          │
│  - Access to config files                                   │
│  - Direct action execution                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    │ subprocess boundary
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ UNTRUSTED ZONE (coder subprocess)                           │
│                                                             │
│  - Limited to step working directory                        │
│  - Must write meta.json for results                         │
│  - Cannot modify job.json directly                          │
│  - Cannot affect other steps                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Input Validation

- **Prompt templates**: Validated for placeholder syntax
- **Artifact paths**: Verified to exist before step completion
- **Meta.json**: Schema validation required
- **Config files**: JSON parsing with graceful fallback

## 10. Related Documentation

- `PROJECT_ANALYSIS.md` — High-level project overview and posture
- `codebase_inventory.md` — Complete module inventory
- `workflow-families.md` — Bootstrap workflow definitions
- `actions-package.md` — Action module documentation
- `CODER_IMPLEMENTATION_SOP.md` — Implementation standards