---
template_id: "CB-04-IM"
title: "Integration Map - agent-runner-v2"
status: "active"
generated: "2026-07-10T14:45:58+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04b_generate_integration_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04b_generate_integration_docs`
> This file is workflow-generated and protected from manual edits.

# Integration Map: agent-runner-v2

## 1. Overview

This document maps how modules connect, data flows through the system, and integration points with external systems for the agent-runner-v2 workflow orchestration engine.

**Scope**: Complete integration topology including internal module dependencies, data flows, external system interfaces, and extension points.

---

## 2. Module Dependency Graph

### 2.1 Core Execution Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLI ENTRY POINT                                    │
│                         run_agent.py (2,374 lines)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP RUNNER CORE                                     │
│                      step_runner.py (2,674 lines)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │render_prompt │  │ build_context│  │  run_step    │  │   run_action     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌───────────────────────┐  ┌──────────────────┐  ┌────────────────────────────┐
│   CODER ADAPTERS      │  │  ACTIONS PACKAGE │  │   WORKFLOW ROUTER          │
│ coder_adapters.py     │  │  (28 actions)    │  │   workflow_router.py       │
│ (1,079 lines)         │  │                  │  │   (787 lines)              │
│                       │  │  • validate_*  │  │                            │
│  • invoke_coder()     │  │  • sync_*      │  │  • route_after_step()      │
│  • Claude adapter     │  │  • generate_*  │  │  • route_after_failure()   │
│  • Codex adapter      │  │  • execute_*   │  │                            │
│  • Qwen adapter       │  │  • submit_*    │  │                            │
└───────────────────────┘  └──────────────────┘  └────────────────────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          JOB STATE LIFECYCLE                                 │
│                        job_state.py (1,806 lines)                            │
│                                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐     │
│   │ create_job  │  │  load_job   │  │  save_job   │  │ advance_step    │     │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Module Area Dependencies

| Module Area | Modules | Depends On | Description |
|-------------|---------|------------|-------------|
| **core** | run_agent.py, step_runner.py, workflow_router.py | state, coder, backend | Main execution pipeline |
| **state** | job_state.py, runtime_context.py, execution_request.py, execution_result.py | - | Job lifecycle and context management |
| **coder** | coder_adapters.py, model_config.py | state | LLM backend invocation (Claude/Codex/Qwen) |
| **backend** | backend_client.py, daemon.py, runner_logger.py | state | Worker mode and backend connectivity |
| **actions** | 28 action modules | core, state | Deterministic runner actions |
| **bootstrap** | bundle_loader.py, template_groups.py | constants | Workflow bundle loading and discovery |
| **support** | constants.py, doc_paths.py, exceptions.py | - | Shared utilities and constants |

### 2.3 Detailed Dependency Matrix

```
                    ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
                    │constants │  state   │  coder   │  core    │ actions  │ backend  │ bootstrap│ support  │
┌───────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ run_agent.py      │    ●     │    ●     │    ○     │    ○     │    ○     │    ●     │    ●     │    ●     │
│ step_runner.py    │    ●     │    ●     │    ●     │    ○     │    ○     │    ○     │    ○     │    ●     │
│ workflow_router.py│    ○     │    ●     │    ●     │    ○     │    ○     │    ○     │    ○     │    ●     │
│ job_state.py      │    ●     │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │    ●     │
│ coder_adapters.py │    ○     │    ●     │    ○     │    ○     │    ○     │    ○     │    ○     │    ●     │
│ backend_client.py │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │
│ daemon.py         │    ○     │    ●     │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │
│ actions/*         │    ●     │    ●     │    ○     │    ○     │    ○     │    ●     │    ○     │    ●     │
│ constants.py      │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │    ○     │
└───────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

● = direct import dependency
○ = indirect or configuration dependency
```

---

## 3. Data Flow Through the System

### 3.1 Main Execution Path (CLI Mode)

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  CLI    │───▶│  Parse  │───▶│  Load   │───▶│  Create │───▶│ Execute │───▶│  Route  │
│  Args   │    │  Args   │    │ Workflow│    │  Job    │    │  Steps  │    │  Next   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │                                                          │
     │                    ┌───────────────────────────────────────┘
     │                    │
     │                    ▼
     │           ┌────────────────────┐
     │           │   For Each Step:   │
     │           │                    │
     │           │  ┌──────────────┐  │
     │           │  │ Render       │  │
     │           │  │ Prompt       │  │
     │           │  └──────────────┘  │
     │           │         │          │
     │           │         ▼          │
     │           │  ┌──────────────┐  │
     │           │  │ Invoke Coder │  │
     │           │  │ or Action    │  │
     │           │  └──────────────┘  │
     │           │         │          │
     │           │         ▼          │
     │           │  ┌──────────────┐  │
     │           │  │ Read Meta    │  │
     │           │  │ Validate     │  │
     │           │  └──────────────┘  │
     │           │         │          │
     │           │         ▼          │
     │           │  ┌──────────────┐  │
     │           │  │ Route Result │  │
     │           │  └──────────────┘  │
     │           │                    │
     │           └────────────────────┘
     │                    │
     └────────────────────┘
                    ▼
┌─────────┐    ┌─────────┐    ┌─────────┐
│  Save   │◀───│ Update  │◀───│ Final   │
│  State  │    │  State  │    │  Status │
└─────────┘    └─────────┘    └─────────┘
```

### 3.2 Worker Mode Data Flow (Backend-Connected)

```
┌──────────────┐     HTTP/API      ┌──────────────┐
│   Backend    │◀───────────────▶ │   Worker     │
│   Service    │  claim/submit    │   Process    │
└──────────────┘                  └──────────────┘
       │                                  │
       │ 1. Poll for work                 │
       │ 2. Claim step run                │
       │ 3. Execute locally               │
       │ 4. Submit results                │
       │                                  │
       ▼                                  ▼
┌──────────────┐                  ┌──────────────┐
│ Step Run     │                  │ ukbe-run-agent│
│ Queue        │                  │ worker mode  │
└──────────────┘                  └──────────────┘
```

### 3.3 Data Flow Artifacts

| Stage | Input | Processing | Output | Sidecar |
|-------|-------|------------|--------|---------|
| **Job Creation** | seed_artifacts, group_cfg | `create_job()` | job.json | - |
| **Step Preparation** | job.json, step_cfg | `build_context()` | context dict | - |
| **Prompt Rendering** | template.txt, context | `render_prompt()` | rendered prompt | - |
| **Coder Invocation** | rendered prompt, schema | `invoke_coder()` | process output | - |
| **Result Validation** | meta.json, artifacts | `run_step()` | StepResult | enriched meta.json |
| **Routing** | StepResult, state | `route_after_step()` | updated state | updated job.json |

---

## 4. Integration Points with External Systems

### 4.1 External System Integration Table

| External System | Protocol | Direction | Purpose | Module | Authentication |
|-----------------|----------|-----------|---------|--------|----------------|
| **Backend API** | HTTP/REST | Bidirectional | Workflow orchestration, step claiming, result submission | backend_client.py | Bearer token via config |
| **Claude (Anthropic)** | Subprocess/CLI | Outbound | LLM invocation for coder steps | coder_adapters.py | API key via env |
| **Codex (OpenAI)** | Subprocess/CLI | Outbound | LLM invocation for coder steps | coder_adapters.py | API key via env |
| **Qwen Code** | Subprocess/CLI | Outbound | LLM invocation for coder steps | coder_adapters.py | Local installation |
| **ComfyUI** | HTTP/WebSocket | Outbound | Image generation pipeline | actions/submit_comfyui.py | Local instance |
| **Video Generation (I2V/T2V)** | HTTP/API | Outbound | Video clip generation | actions/execute_i2v.py, execute_t2i.py | Service credentials |
| **Voiceover Service** | HTTP/API | Outbound | Audio generation | actions/execute_voiceover.py | Service credentials |
| **Pushover Notifications** | HTTP/API | Outbound | Push notifications | notification_manager.py | App token via env |
| **GitHub (gh CLI)** | Subprocess | Outbound | Issue fetching for bug workflow | fetch-github-issue-for-bug-fix | gh CLI auth |

### 4.2 Backend API Contract

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         Backend API Integration                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   Endpoints:                                                               │
│   • POST /api/v1/worker/register       - Register worker node              │
│   • POST /api/v1/worker/heartbeat      - Health/status updates             │
│   • POST /api/v1/worker/claim        - Poll for available step runs       │
│   • POST /api/v1/step-runs/{id}/complete - Submit step results            │
│   • GET  /api/v1/runs/{id}           - Get run details                   │
│   • POST /api/v1/runs/{id}/approve    - Approve/reject run                 │
│   • POST /api/v1/artifacts           - Create artifact record              │
│   • POST /api/v1/events              - Create workflow event             │
│                                                                            │
│   Payload Structure (Step Complete):                                       │
│   {                                                                        │
│     "coder_result": {                                                      │
│       "status": "APPROVED|REJECTED",                                       │
│       "remark": "...",                                                    │
│       "artifacts": { "KEY": "path/to/artifact.md" },                      │
│       "recorded_at": "2026-07-10T14:45:58+08:00"                          │
│     },                                                                     │
│     "usage_data": { input_tokens, output_tokens, cost }                  │
│   }                                                                        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 LLM Provider Integration

| Provider | Model Aliases | Invocation Method | Response Format |
|----------|---------------|-------------------|-----------------|
| **Claude** | claude-opus, claude-son, claude-haiku | Subprocess (q CLI) | meta.json sidecar |
| **Codex** | codex-latest | Subprocess (codex CLI) | meta.json sidecar |
| **Qwen Code** | qwen | Subprocess (qwen CLI) | meta.json sidecar |

### 4.4 Notification Integration

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      Notification Flow                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   Step Completion ──▶ notification_manager.py ──▶ Pushover API            │
│        │                                           │                       │
│        │              ┌─────────────────────────────┘                       │
│        │              │                                                    │
│        │         HTTP POST to api.pushover.net                             │
│        │              │                                                    │
│        │         ┌────┴────┐                                                 │
│        │         │         │                                                 │
│     Success    Mobile    Desktop                                             │
│     Failure    Push      Push                                                │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Internal Module Boundaries and Extension Points

### 5.1 Module Area Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BOUNDARY: CLI Layer                              │
│  run_agent.py - Argument parsing, command dispatch                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BOUNDARY: Core Execution                         │
│  step_runner.py, workflow_router.py - Step lifecycle, routing logic         │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BOUNDARY: State Management                       │
│  job_state.py, runtime_context.py - Job persistence, context resolution    │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BOUNDARY: Coder Abstraction                     │
│  coder_adapters.py - LLM backend abstraction                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BOUNDARY: Action Framework                       │
│  actions/*.py - Deterministic runner actions                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BOUNDARY: Backend Integration                    │
│  backend_client.py, daemon.py - External service connectivity               │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BOUNDARY: Bootstrap/Workflow                     │
│  bundle_loader.py, template_groups.py - Workflow definition loading           │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BOUNDARY: Plugin System (In Progress)            │
│  workflow_packages/*.py - New plugin-based workflow architecture            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Extension Points

| Extension Point | Interface | Description | Implementation |
|-----------------|-----------|-------------|----------------|
| **New Actions** | `run_action()` signature | Add deterministic runner actions | Create module in `actions/` |
| **New Workflow** | `TEMPLATE_GROUPS` dict | Add workflow definition | Update `template_groups.py` or add `workflow.toml` |
| **New Coder Backend** | `invoke_coder()` adapter | Support new LLM provider | Extend `coder_adapters.py` |
| **Context Extensions** | `context_extensions.py` hook | Workflow-specific context injection | Add `context_extensions.py` to workflow package |
| **Custom Validations** | Action step with `validate_*` | Domain-specific artifact validation | Create `actions/validate_*.py` |
| **Notification Channels** | `notification_manager.py` | Add new notification backends | Extend `notification_manager.py` |

### 5.3 Plugin Architecture (Migration In Progress)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Current vs Target Architecture                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CURRENT (template_groups.py):                                              │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ TEMPLATE_GROUPS = {                                             │       │
│  │   "workflow_name": {                                            │       │
│  │     "steps": [...],                                             │       │
│  │     "produces": [...],                                          │       │
│  │     "routing": {...}                                            │       │
│  │   }                                                             │       │
│  │ }                                                               │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                              │                                              │
│                              │                                              │
│  TARGET (Plugin Packages):                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ workflows/<name>/                                               │       │
│  │   ├── workflow.toml          # Declarative manifest            │       │
│  │   ├── prompts/               # Prompt templates                │       │
│  │   └── context_extensions.py  # Custom context hooks            │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ WorkflowRegistry (Configuration Source Adapter)                │       │
│  │   • Scans workflows/ directory                                    │       │
│  │   • Falls back to TEMPLATE_GROUPS                                 │       │
│  │   • Converts workflow.toml → TEMPLATE_GROUPS format             │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ Unchanged Execution Pipeline                                    │       │
│  │   step_runner.py → coder_adapters.py → workflow_router.py      │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Key Interaction Sequences

### 6.1 Standard Workflow Step Execution

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│   Job    │         │  Render  │         │  Invoke  │         │  Route   │
│  State   │         │  Prompt  │         │  Coder   │         │  Result  │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ 1. Load state      │                    │                    │
     │────────────────────▶                    │                    │
     │                    │                    │                    │
     │                    │ 2. Substitute      │                    │
     │                    │    placeholders    │                    │
     │                    │────────────────────▶                    │
     │                    │                    │                    │
     │                    │                    │ 3. Execute coder   │
     │                    │                    │    subprocess      │
     │                    │                    │────────────────────▶
     │                    │                    │                    │
     │                    │                    │ 4. Wait for        │
     │                    │                    │    meta.json       │
     │                    │                    │◀───────────────────│
     │                    │                    │                    │
     │                    │                    │ 5. Validate        │
     │                    │                    │    artifacts       │
     │                    │                    │────────────────────▶
     │                    │                    │                    │
     │                    │                    │                    │ 6. Route
     │                    │                    │                    │    next step
     │◀───────────────────────────────────────────────────────────│
     │                    │                    │                    │
```

### 6.2 Review Loop Sequence

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Review  │    │ HUMAN   │    │  Check  │    │  Route  │    │ Continue│
│ Request │───▶│DECISION │───▶│  Limit  │───▶│         │───▶│  / Fail │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                  │               │               │
                  │               │               │
              ┌───┴───┐       ┌─┴─┐          ┌──┴───┐
              │approve│       │< N│          │retry │
              │reject │       │>=N│          │abort │
              └───┬───┘       └─┬─┘          └──────┘
                  │               │
                  ▼               ▼
              Continue        Max Rejects
                              Reached
```

### 6.3 Failure Handling Sequence

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Exception │     │   Classify  │     │    Route    │     │    Record   │
│    Raised   │────▶│   Failure   │────▶│   After     │────▶│   History   │
│             │     │             │     │   Failure   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                    │                    │
                           ▼                    ▼                    ▼
                    ┌──────────────┐      ┌─────────────┐      ┌─────────────┐
                    │ Coder Error  │      │  Transient  │      │  Update     │
                    │ Missing Meta │      │   Retry     │      │  job.json   │
                    │ Invalid JSON │      │  Permanent  │      │             │
                    └──────────────┘      │   Abort     │      └─────────────┘
                                          └─────────────┘
```

### 6.4 Artifact Validation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Artifact Validation                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Step Completion                                                           │
│        │                                                                    │
│        ▼                                                                    │
│   ┌────────────────┐                                                        │
│   │ Read meta.json │                                                        │
│   └───────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│   ┌────────────────┐     ┌───────────────┐     ┌──────────────────────┐    │
│   │ Validate       │────▶│ Check Schema  │────▶│ Validate Artifacts   │    │
│   │ Schema         │     │ Version       │     │ Exist on Disk        │    │
│   └────────────────┘     └───────────────┘     └──────────┬───────────┘    │
│                                                            │                │
│                                                            ▼                │
│                                                   ┌──────────────────┐     │
│                                                   │  Check Guardrails │     │
│                                                   │  (if applicable)  │     │
│                                                   └────────┬─────────┘     │
│                                                            │                │
│                                                            ▼                │
│                                                   ┌──────────────────┐     │
│                                                   │ Enrich Sidecar     │     │
│                                                   │ with Runner Data   │     │
│                                                   └────────┬─────────┘     │
│                                                            │                │
│                                                            ▼                │
│                                                   ┌──────────────────┐     │
│                                                   │ Update Job State   │     │
│                                                   └──────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Runtime Source of Truth

### 7.1 Bootstrap vs Runtime Duality

| Aspect | Bootstrap Source | Runtime Bundle | Sync Mechanism |
|--------|-----------------|----------------|----------------|
| **Location** | `agent_runner_v2/bootstrap/` | `%USERPROFILE%\.ukbe-runner\workflows\` | `ukbe-run-agent init` |
| **Purpose** | Package source of truth | Active execution source | Seeding command |
| **Prompts** | `prompts/<workflow>/*.txt` | Same structure | Copied on init |
| **Templates** | `template_groups.py` | Loaded dynamically | Registry scan |
| **Changes** | Version controlled | User-modified | Manual sync |

### 7.2 Path Resolution Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Path Resolution Order                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. Runtime Path (%USERPROFILE%\.ukbe-runner\workflows\<workflow>\)       │
│      ↓ (if not found)                                                       │
│   2. Local Project Path (./workflows/<workflow>/ - for plugin development)  │
│      ↓ (if not found)                                                       │
│   3. Bootstrap Path (agent_runner_v2/bootstrap/workflows/default/)          │
│                                                                             │
│   Resolution Function: workflow_packages.loader._resolve_workflow_path()  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Cross-Module Communication Patterns

### 8.1 Communication Mechanisms

| Pattern | Used Between | Mechanism | Data Format |
|---------|-------------|-----------|-------------|
| **Function Calls** | Core modules | Direct Python invocation | Typed parameters, dataclasses |
| **Job State** | All modules | job.json file | JSON with schema_version |
| **Meta Sidecar** | Coder → Runner | meta.json file | v2 schema with coder_result |
| **Subprocess** | Runner → Coder CLI | Popen with stdin/stdout | Plain text prompt, JSON result |
| **HTTP REST** | Runner → Backend | urllib requests | JSON payloads |
| **Context Dict** | Step preparation | In-memory dict | String-keyed context map |

### 8.2 Data Contract: Meta.json Sidecar

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED|REJECTED",
    "remark": "Summary of work completed",
    "artifacts": {
      "ARTIFACT_KEY": "relative/path/to/artifact.md"
    },
    "recorded_at": "2026-07-10T14:45:58+08:00"
  },
  "runner_data": {
    "step": "step_name",
    "coder_used": "claude-opus-4",
    "invoked_at": "2026-07-10T14:40:00+08:00",
    "finished_at": "2026-07-10T14:45:58+08:00",
    "prompt_checksum": "sha256:abc...",
    "allowed_write_paths": [...],
    "changed_paths": [...]
  }
}
```

---

## 9. Summary

### 9.1 Key Integration Points Index

| Integration | Module | External System | Criticality |
|-------------|--------|-----------------|-------------|
| CLI Entry | run_agent.py | User/Shell | Critical |
| Step Execution | step_runner.py | Coder CLI | Critical |
| Job Persistence | job_state.py | File System | Critical |
| Result Routing | workflow_router.py | Internal | Critical |
| LLM Invocation | coder_adapters.py | Claude/Codex/Qwen | High |
| Backend Sync | backend_client.py | Backend API | High |
| Worker Mode | daemon.py | OS Process | Medium |
| Notifications | notification_manager.py | Pushover | Low |

### 9.2 Integration Risk Areas

| Risk Area | Description | Mitigation |
|-----------|-------------|------------|
| **Bootstrap/Runtime Drift** | Changes to bootstrap not reflected in runtime | Use `init` command to reseed |
| **Schema Version Compatibility** | meta.json v2 schema must be maintained | CURRENT_SCHEMA_VERSION constant |
| **Path Resolution Across Platforms** | Windows vs POSIX path handling | PurePosixPath usage |
| **LLM Provider Changes** | CLI interface changes | Adapter pattern in coder_adapters.py |
| **Backend API Changes** | REST contract evolution | Versioned endpoints |

---

## 10. Change Log

| Date | Change | Modules Affected | Verified By |
|------|--------|------------------|-------------|
| 2026-07-10 | Initial integration map generated from codebase baseline | All | 00_master_docs_bootstrap_v2 |
