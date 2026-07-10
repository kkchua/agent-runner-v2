---
template_id: "CB-04-IM"
title: "Integration Map - agent-runner-v2"
Status: draft
managed_by: workflow-generated
generated: "2026-07-10T20:06:30+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04b_generate_integration_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04b_generate_integration_docs`
> This file is workflow-generated and protected from manual edits.

# Integration Map: agent-runner-v2

## 1. Overview

This document maps how modules connect, data flows through the system, and integration points with external systems.

## 2. Module Dependency Graph

### 2.1 Core Execution Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLI Entry Point                                    │
│                     agent_runner_v2/run_agent.py                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Workflow Bundle Resolution                            │
│              bundle_loader.py + workflow_packages/                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│  │ Global Bundle │ or │ Local Plugin │ or │ TEMPLATE_GROUPS│               │
│  │  ~/.ukbe-runner│    │ workflows/<n>│    │  (legacy)      │               │
│  └──────────────┘    └──────────────┘    └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Job State Management                                  │
│                     agent_runner_v2/job_state.py                             │
│  - Create/load job.json                                                      │
│  - Manage step progression                                                   │
│  - Handle failure history                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Step Execution Engine                                 │
│                     agent_runner_v2/step_runner.py                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  1. Render prompt (build_context + render_prompt)                       │  │
│  │  2. Invoke coder OR execute action                                    │  │
│  │  3. Read meta.json sidecar                                            │  │
│  │  4. Validate artifacts                                                │  │
│  │  5. Enrich sidecar with runner_data                                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
┌─────────────────────────────────┐   ┌───────────────────────────────────────┐
│      Coder Invocation           │   │      Action Execution               │
│   agent_runner_v2/              │   │   agent_runner_v2/actions/           │
│   coder_adapters.py             │   │   (30+ deterministic actions)       │
│                                 │   │                                       │
│  ┌─────────────────────────┐    │   │  - scan_repo_codebase                 │
│  │ Claude/Codex/Qwen      │    │   │  - sync_codebase_docs               │
│  │ via subprocess         │    │   │  - validate_delivery_docs           │
│  │ (llm_response_schema)  │    │   │  - generate_site                      │
│  └─────────────────────────┘    │   │  - execute_t2i / execute_i2v        │
└─────────────────────────────────┘   │  - ... (see actions-package)        │
                                      └───────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Post-Step Routing                                     │
│                     agent_runner_v2/workflow_router.py                       │
│  - route_after_step() → approve/reject/refine                              │
│  - route_after_failure() → failure handling                                │
│  - Enforce max_rejects limits                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Backend Integration (Optional)                      │
│                     agent_runner_v2/backend_client.py                        │
│  - submit_run(), approve_run(), get_run()                                  │
│  - register_worker(), heartbeat(), claim_step()                            │
│  - complete_step_run(), create_artifact(), create_event()                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Module Area Classification

| Area | Modules | Responsibility |
|------|---------|----------------|
| **core** | `run_agent.py`, `step_runner.py`, `workflow_router.py` | CLI entry, step execution, routing |
| **coder** | `coder_adapters.py`, `model_config.py` | LLM invocation, model configuration |
| **state** | `job_state.py`, `runtime_context.py`, `execution_request.py`, `execution_result.py` | Job lifecycle, path context, request/result schemas |
| **bootstrap** | `bundle_loader.py`, `bootstrap/workflows/default/template_groups.py` | Bundle seeding, workflow loading |
| **backend** | `backend_client.py`, `daemon.py`, `runner_logger.py` | API client, daemon mode, logging |
| **actions** | `actions/*.py` (28 modules) | Deterministic runner actions |
| **support** | `constants.py`, `doc_paths.py`, `documentation_guardrails.py`, `workflow_packages/*` | Path constants, validation, plugin system |
| **schema** | `exceptions.py`, `artifact_paths.py`, `action_result.py`, `runner_actions.py` | Error types, path schemas, result types |
| **commands** | `approve_commands.py`, `submit_commands.py`, `engine_commands.py`, `submitter.py` | CLI command implementations |

### 2.3 Dependency Direction Matrix

```
                    ┌──────────────┐
                    │  run_agent   │ CLI entry
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐      ┌─────────────┐      ┌──────────┐
   │job_state│      │ step_runner │      │ workflow_│
   │         │◄────►│             │◄────►│ router   │
   └────┬────┘      └──────┬──────┘      └────┬─────┘
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌─────────────┐      ┌──────────┐
   │runtime_ │      │ coder_      │      │ backend_ │
   │context  │      │ adapters    │      │ client   │
   └─────────┘      └─────────────┘      └──────────┘
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌─────────────┐      ┌──────────┐
   │constants│      │ actions/*   │      │ bundle_  │
   │doc_paths│      │             │      │ loader   │
   └─────────┘      └─────────────┘      └──────────┘
```

## 3. Data Flow Diagrams

### 3.1 Local Workflow Execution Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  CLI     │───►│  Load    │───►│  Create  │───►│  Execute │───►│  Route   │
│  Invoke  │    │  Workflow│    │  Job     │    │  Step    │    │  Next    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
  Arguments    TEMPLATE_GROUPS    job.json      Prompt render    meta.json
  --workflow   or workflow.toml   State init    Coder/action     Validation
  --step                                                        Artifact check
```

### 3.2 Backend-Connected Worker Flow

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Backend    │◄───────►│    Daemon    │◄──────►│   Worker     │
│   API        │  Poll   │   (poller)   │  Spawn  │  (executor)  │
└──────────────┘         └──────────────┘         └──────────────┘
        │                         │                        │
        │                         ▼                        ▼
        │                ┌──────────────┐           ┌──────────────┐
        │                │ claim_step() │           │ execute-step │
        │                └──────────────┘           └──────────────┘
        │                                                   │
        ▼                                                   ▼
┌──────────────┐                                    ┌──────────────┐
│ complete_    │◄───────────────────────────────────│ meta.json    │
│ step_run()   │         Submit results               │ sidecar      │
└──────────────┘                                    └──────────────┘
```

### 3.3 Meta.json Sidecar Contract

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Sidecar Data Flow                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  Step Execution
       │
       ▼
  ┌─────────────────┐
  │ coder_adapters  │──► LLM subprocess writes meta.json
  └─────────────────┘    to step directory
       │
       ▼
  ┌─────────────────┐
  │  step_runner    │──► Read meta.json (REQUIRED)
  │                 │    Validate schema
  │                 │    Check artifact existence
  └─────────────────┘
       │
       ▼
  ┌─────────────────┐
  │ enrich_sidecar() │──► Append runner_data section:
  │                  │    - timestamps
  │                  │    - coder_used
  │                  │    - prompt_checksum
  │                  │    - changed_paths (git diff)
  │                  │    - allowed_write_paths
  └─────────────────┘
       │
       ▼
  ┌─────────────────┐
  │ workflow_router │──► Route based on status:
  │                 │    - APPROVED → next step
  │                 │    - REJECTED → refine/replan
  │                 │    - FAILURE → failure handling
  └─────────────────┘
```

## 4. Integration Points with External Systems

### 4.1 LLM Provider Integration

| Provider | Module | Protocol | Direction | Purpose |
|----------|--------|----------|-----------|---------|
| **Claude** (Anthropic) | `coder_adapters.py` | Subprocess CLI | Outbound | Code generation, review |
| **Codex** (OpenAI) | `coder_adapters.py` | Subprocess CLI | Outbound | Code generation, review |
| **Qwen** (Alibaba) | `coder_adapters.py` | Subprocess CLI | Outbound | Code generation, review |

**Integration Pattern**: Each coder is invoked via subprocess with:
- Prompt text (rendered from template)
- Schema path (`llm_response_schema.json`)
- Working directory (step directory)
- Timeout configuration

**Sidecar Polling**: `coder_adapters.py` polls for `meta.json` with configurable intervals.

### 4.2 Backend API Integration

| Endpoint | Module | Protocol | Direction | Purpose |
|----------|--------|----------|-----------|---------|
| `POST /runs` | `backend_client.py` | HTTP/JSON | Outbound | Submit new workflow run |
| `GET /runs/{id}` | `backend_client.py` | HTTP/JSON | Bidirectional | Get run status |
| `POST /runs/{id}/approve` | `backend_client.py` | HTTP/JSON | Outbound | Approve/reject step |
| `POST /workers/register` | `backend_client.py` | HTTP/JSON | Outbound | Register worker |
| `POST /workers/{id}/heartbeat` | `backend_client.py` | HTTP/JSON | Outbound | Worker heartbeat |
| `POST /workers/{id}/claim` | `backend_client.py` | HTTP/JSON | Outbound | Claim step for execution |
| `POST /step-runs/{id}/complete` | `backend_client.py` | HTTP/JSON | Outbound | Submit step results |
| `POST /artifacts` | `backend_client.py` | HTTP/JSON | Outbound | Create artifact records |
| `POST /events` | `backend_client.py` | HTTP/JSON | Outbound | Emit events |

**Authentication**: Backend API credentials resolved via `.env` file or environment variables.

### 4.3 ComfyUI/Media Generation Integration

| System | Module | Protocol | Direction | Purpose |
|--------|--------|----------|-----------|---------|
| **ComfyUI** | `actions/execute_t2i.py` | HTTP/WebSocket | Outbound | Text-to-image generation |
| **ComfyUI** | `actions/execute_i2v.py` | HTTP/WebSocket | Outbound | Image-to-video generation |
| **Voiceover** | `actions/execute_voiceover.py` | HTTP/API | Outbound | Audio generation |
| **FFmpeg** | `actions/assemble_video.py` | Subprocess | Outbound | Video composition |

### 4.4 Git Integration

| Operation | Module | Purpose |
|-----------|--------|---------|
| `git diff` | `step_runner.py` | Detect changed paths for sidecar enrichment |
| `git status` | Multiple actions | Repository state validation |

### 4.5 Notification Integration

| Service | Module | Protocol | Purpose |
|---------|--------|----------|---------|
| **Pushover** | `notifications.py`, `notification_manager.py` | HTTP/API | Push notifications for step completion/failure |

## 5. Module Boundaries and Responsibilities

### 5.1 Core Execution Boundary

| Module | Invariants | Extension Points |
|--------|------------|------------------|
| `run_agent.py` | CLI argument parsing, command dispatch | New CLI commands |
| `step_runner.py` | Prompt rendering, sidecar validation, artifact checking | New context builders |
| `workflow_router.py` | Routing logic, retry enforcement, notification triggers | Custom routing rules |

### 5.2 Coder Boundary

| Module | Invariants | Extension Points |
|--------|------------|------------------|
| `coder_adapters.py` | Subprocess invocation, sidecar polling, timeout handling | New coder backends |
| `model_config.py` | Model aliasing, configuration resolution | New model configurations |

### 5.3 State Management Boundary

| Module | Invariants | Extension Points |
|--------|------------|------------------|
| `job_state.py` | Job.json schema, step progression, failure tracking | New state migrations |
| `runtime_context.py` | Path resolution, context management | New path types |

### 5.4 Bootstrap Boundary

| Module | Invariants | Extension Points |
|--------|------------|------------------|
| `bundle_loader.py` | Global/local workflow resolution, seeding | New bundle formats |
| `workflow_packages/` | Plugin loading, TOML parsing | New workflow adapters |

## 6. Key Interaction Sequences

### 6.1 Workflow Step Execution Sequence

```
1. run_agent.py receives "run" command
   └── Parse args: --workflow, --step, --job-id

2. Load workflow configuration
   └── bundle_loader.resolve_workflow_root()
   └── Load from: global bundle → local plugin → TEMPLATE_GROUPS

3. Load or create job state
   └── job_state.load_job() or job_state.create_job()

4. For each step in sequence:
   a. step_runner.build_context()
      └── Merge state, step_cfg, artifact paths
      └── Inject REFERENCE_FILES placeholders

   b. step_runner.render_prompt()
      └── Resolve prompt file path (3-level fallback)
      └── Substitute placeholders with context

   c. step_runner.run_step() [for coder steps]
      └── coder_adapters.invoke_coder()
          └── Spawn subprocess (claude/codex/qwen)
          └── Poll for meta.json
      └── Validate artifacts exist
      └── enrich_sidecar() with runner_data

   d. step_runner.run_action() [for action steps]
      └── Import action from actions/
      └── Execute in-process
      └── Return StepResult

   e. workflow_router.route_after_step()
      └── Determine next step based on status
      └── Check max_rejects limit
      └── Send notification if configured

   f. job_state.advance_step()
      └── Update job.json state
      └── Persist to disk
```

### 6.2 Review/Refine Loop Sequence

```
1. Step returns status "REJECTED"

2. workflow_router.route_after_step()
   └── Check reject count vs max_rejects
   └── If under limit: route to refine step
   └── If over limit: route to replan step

3. Refine step executes with original + feedback context

4. Loop continues until:
   - Status becomes "APPROVED" → advance
   - Max rejects exceeded → escalate to replan
   - Hard failure → route to failure handling
```

### 6.3 Failure Handling Sequence

```
1. Exception raised during step execution
   └── CoderInvocationError (LLM process failed)
   └── MetaJsonMissingError (no sidecar written)
   └── MetaJsonInvalidError (invalid sidecar schema)
   └── ArtifactMissingError (declared artifacts don't exist)

2. workflow_router.route_after_failure()
   └── Capture exception details
   └── Update failure history in job state
   └── Classify failure type

3. Decision:
   └── Transient error → retry step
   └── Hard failure → terminal state

4. Notification sent if configured
```

### 6.4 Daemon Mode Sequence

```
1. Daemon startup
   └── backend_client.register_worker()
   └── Begin heartbeat loop

2. Poll cycle:
   └── backend_client.claim_step()
   └── If step claimed:
       └── Spawn subprocess: run_agent execute-step
       └── Wait for completion
       └── backend_client.complete_step_run()
   └── Send heartbeat

3. Code changes picked up automatically
   └── Each subprocess loads fresh Python code
   └── No daemon restart required
```

## 7. Data Contracts

### 7.1 Job State Contract

**File**: `~/.ukbe-runner/jobs/{workflow}/{job_id}/job.json`

```json
{
  "job_id": "uuid",
  "workflow": "workflow_name",
  "template_group": "group_name",
  "current_step": "step_name",
  "status": "running|waiting|completed|failed",
  "artifacts": {"ARTIFACT_KEY": "relative/path"},
  "failure_history": [],
  "review_state": {},
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### 7.2 Meta.json Sidecar Contract

**File**: `{artifact_path}.meta.json`

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED|REJECTED",
    "remark": "Human-readable summary",
    "artifacts": {"ARTIFACT_KEY": "relative/path"},
    "recorded_at": "ISO8601"
  },
  "runner_data": {
    "step": "step_name",
    "coder_used": "claude|codex|qwen",
    "invoked_at": "ISO8601",
    "finished_at": "ISO8601",
    "prompt_checksum": "sha256",
    "changed_paths": ["git/changed/file.py"],
    "allowed_write_paths": ["docs/..."]
  }
}
```

### 7.3 Workflow Bundle Contract

**Plugin Package**: `workflows/{name}/workflow.toml`

```toml
[workflow]
name = "workflow_name"
version = "1.0.0"

[steps.step_name]
coder = "claude|codex|qwen|action"
action = "action_name"  # for action steps
prompt = "prompts/step.txt"
allowed_artifacts = ["ARTIFACT_KEY"]
next = "next_step"
refine = "refine_step"
replan = "replan_step"
```

## 8. Configuration Sources

| Configuration | Source | Module | Priority |
|---------------|--------|--------|----------|
| Workflow bundles | `~/.ukbe-runner/workflows/` | `bundle_loader.py` | 1 (Global) |
| Workflow plugins | `./workflows/{name}/` | `workflow_packages/loader.py` | 2 (Local) |
| Legacy templates | `template_groups.py` | `template_groups.py` | 3 (Fallback) |
| Backend API | `.env` → environment | `backend_client.py` | - |
| Model configs | `~/.ukbe-runner/config.json` | `model_config.py` | - |
| Runner home | Environment → default | `runtime_context.py` | - |

## 9. Error Propagation Paths

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Error Sources                                    │
└─────────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│  Coder Errors  │    │ Action Errors  │    │ Routing Errors │
│                │    │                │    │                │
│ • Timeout      │    │ • Validation   │    │ • Invalid next │
│ • Crash        │    │ • I/O failure  │    │ • Max rejects  │
│ • No meta.json │    │ • External API │    │ exceeded       │
└────────────────┘    └────────────────┘    └────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌────────────────┐
                    │ workflow_router│
                    │ route_after_   │
                    │ failure()      │
                    └────────────────┘
                              │
                              ▼
                    ┌────────────────┐
                    │  job_state     │
                    │  Update status │
                    │  Log failure   │
                    └────────────────┘
```

## 10. Extension Points

| Extension | Location | Contract |
|-----------|----------|----------|
| **New Action** | `actions/{action_name}.py` | Function accepting `(state, context, step_cfg)` returning `ActionResult` with `meta_path` |
| **New Workflow** | `workflows/{name}/workflow.toml` | TOML manifest with steps, routing, artifact keys |
| **New Coder** | `coder_adapters.py` | Subprocess wrapper following sidecar contract |
| **New Template** | `bootstrap/workflows/default/prompts/{wf}/{step}.txt` | Text with `{PLACEHOLDER}` substitutions |
| **Context Hook** | `workflows/{name}/context_extensions.py` | Module with `extend_context(context, state, step_cfg)` function |

---

*This integration map was generated from repository analysis and reflects the system architecture as of the bootstrap timestamp.*
