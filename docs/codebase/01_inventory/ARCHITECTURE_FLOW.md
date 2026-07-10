---
template_id: "CB-04-AF"
title: "Architecture Flow - agent-runner-v2"
Status: draft
managed_by: workflow-generated
generated: "2026-07-10T20:16:17+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04d_generate_architecture_flow_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04d_generate_architecture_flow_docs`
> This file is workflow-generated and protected from manual edits.

# Architecture Flow: agent-runner-v2

This document describes the end-to-end execution flows for different usage modes of the agent-runner-v2 workflow orchestration engine.

## Table of Contents

1. [Execution Modes Overview](#execution-modes-overview)
2. [Local Execution Flow](#local-execution-flow)
3. [Backend Worker Flow](#backend-worker-flow)
4. [Daemon Supervision Flow](#daemon-supervision-flow)
5. [Workflow Step Execution Detail](#workflow-step-execution-detail)
6. [Review Loop Mechanics](#review-loop-mechanics)
7. [Failure Routing Flow](#failure-routing-flow)
8. [Documentation Sync Flow](#documentation-sync-flow)

---

## Execution Modes Overview

The agent-runner-v2 system supports three primary execution modes:

| Mode | Entry Point | Use Case | Key Characteristics |
|------|-------------|----------|---------------------|
| **Local Run** | `ukbe-run-agent run` | Manual workflow execution, development, testing | Interactive CLI, immediate feedback, full control |
| **Backend Worker** | `ukbe-run-agent worker` / `ukbe-run-agent poll` | Backend-connected single-step execution | Polls backend for work, executes one step per invocation |
| **Daemon Mode** | `ukbe-run-agent daemon` | Production supervision | Long-running supervisor, spawns child processes, monitors health |

All three modes converge on the same core execution path through `step_runner.py`, ensuring consistent behavior regardless of entry point.

---

## Local Execution Flow

### ASCII Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOCAL EXECUTION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

    User CLI
       │
       ▼
┌──────────────┐
│  run_agent   │  ←── Parse args, resolve workflow bundle
│   main()     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Load Job    │  ←── Load existing or create new job.json
│   State      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Build Context│  ←── Render prompt template with context
│ Render Prompt│
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────┐
│  step_runner │────▶│ invoke_coder│ ←── Subprocess to LLM
│   run_step() │      │  (coder_    │     (Claude/Codex/Qwen)
└──────┬───────┘      │  adapters)  │
       │              └──────┬──────┘
       │                     │
       │              ┌──────▼──────┐
       │              │ Write       │ ←── Coder writes artifacts
       │              │ Artifacts   │     + meta.json sidecar
       │              └──────┬──────┘
       │                     │
       ▼                     │
┌──────────────┐             │
│ Read &       │◀────────────┘
│ Validate     │  ←── meta.json is ONLY result channel
│ meta.json    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validate    │  ←── Check artifact files exist on disk
│  Artifacts   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ workflow_    │  ←── Route based on status (APPROVED/REJECTED)
│   router     │
└──────┬───────┘
       │
       ├──▶ APPROVED ──▶ advance_step() ──▶ Next step
       │
       ├──▶ REJECTED ──▶ Loop/Refine/Replenish
       │
       └──▶ FAILURE ──▶ route_after_failure()
```

### Step-by-Step Flow

1. **CLI Entry** (`run_agent.py::main()`)
   - Parse command-line arguments
   - Resolve workflow bundle root (global runner home or project-local)
   - Load workflow module from bootstrap or plugin package

2. **Job State Resolution** (`job_state.py`)
   - Load existing job by ID or create new job
   - Apply state migrations and reconciliation
   - Resolve current step from job state

3. **Context Building** (`step_runner.py::build_context()`)
   - Load reference files declared in step config
   - Apply context aliases (e.g., `REVIEW_FILE_PATH`)
   - Inject automatic sidecar instructions

4. **Prompt Rendering** (`step_runner.py::render_prompt()`)
   - Load prompt template from workflow bundle
   - Substitute context variables
   - Compute prompt checksum for tracking

5. **Coder Invocation** (`coder_adapters.py::invoke_coder()`)
   - Spawn subprocess to LLM backend
   - Pass rendered prompt and schema
   - Wait for completion or timeout

6. **Meta.json Validation** (`step_runner.py::_read_and_validate_meta_json()`)
   - Read sidecar from expected path
   - Validate schema version (v2)
   - Validate required fields (status, remark, artifacts, recorded_at)

7. **Artifact Validation** (`step_runner.py::_validate_artifact_files_exist()`)
   - Check each artifact path exists on disk
   - Skip `.meta.json` files (sidecars, not artifacts)

8. **Post-Step Routing** (`workflow_router.py::route_after_step()`)
   - Update job state with results
   - Route to next step based on status
   - Handle review loops and failure recovery

---

## Backend Worker Flow

### ASCII Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND WORKER FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Backend    │
│   Server     │
└──────┬───────┘
       │
       │ 1. Poll for work
       ▼
┌──────────────┐
│    worker    │  ←── Register, claim step, execute, submit result
│   command    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  claim_step  │  ←── BackendClient.claim_step(worker_id)
│   (API)      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Build Worker │  ←── _build_worker_request_payload()
│   Request    │     Transform backend payload to execution request
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ execute-step │  ←── Same execution path as local mode
│   command    │     (reuses step_runner.run_step)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Read Result │  ←── result.json written by execute-step
│  from Disk   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│complete_step_│  ←── BackendClient.complete_step_run()
│    run       │     Submit result back to backend
│   (API)      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Backend    │
│  State Update│
└──────────────┘
```

### Step-by-Step Flow

1. **Worker Registration** (`run_agent.py::_worker_command()`)
   - Register worker with backend using `BackendClient.register_worker()`
   - Report capabilities and worker label (live/dev)

2. **Claim Step** (`backend_client.py::claim_step()`)
   - Poll backend for available work
   - Backend assigns a workflow run and step run
   - Return claim payload with run context and step execution spec

3. **Build Request Payload** (`run_agent.py::_build_worker_request_payload()`)
   - Transform backend claim into execution request
   - Extract template group, job ID, step config
   - Handle step spec source (global, backend, or hybrid)

4. **Execute Step** (`run_agent.py::_execute_step_command()`)
   - Load execution request from file
   - Run step through same `step_runner.run_step()` path as local mode
   - Write execution result to result file

5. **Submit Result** (`run_agent.py::_submit_worker_result()`)
   - Read result from disk
   - Submit to backend via `BackendClient.complete_step_run()`
   - Backend advances workflow state

6. **Finalize Completion** (`run_agent.py::_finalize_worker_completion()`)
   - Poll backend for updated run status
   - Log completion details

---

## Daemon Supervision Flow

### ASCII Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DAEMON SUPERVISION FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Daemon Process                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │            _run_supervisor() Loop               │    │
│  │                                                 │    │
│  │  ┌─────────────┐    ┌─────────────┐            │    │
│  │  │ Poll Backend│───▶│ Claim Step  │            │    │
│  │  └─────────────┘    └──────┬──────┘            │    │
│  │                          │                     │    │
│  │                          ▼                     │    │
│  │                   ┌─────────────┐             │    │
│  │                   │ Spawn Child │             │    │
│  │                   │ subprocess  │             │    │
│  │                   └──────┬──────┘             │    │
│  │                          │                     │    │
│  │                          ▼                     │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │           Child Process Monitor          │  │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐    │  │    │
│  │  │  │Running  │ │Stalled  │ │Timeout  │    │  │    │
│  │  │  │Check    │ │Check    │ │Check    │    │  │    │
│  │  │  └────┬────┘ └────┬────┘ └────┬────┘    │  │    │
│  │  │       │          │          │          │  │    │
│  │  │       ▼          ▼          ▼          │  │    │
│  │  │  ┌──────────────────────────────────┐  │  │    │
│  │  │  │        Child Exited              │  │  │    │
│  │  │  │   Read result.json / Log       │  │  │    │
│  │  │  └──────────────────────────────────┘  │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  │                          │                     │    │
│  │                          ▼                     │    │
│  │                   ┌─────────────┐               │    │
│  │                   │Send Heartbeat│              │    │
│  │                   │  to Backend │               │    │
│  │                   └─────────────┘               │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Child execute-step Subprocess              │
│                                                         │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │
│   │ Load Request│──▶│ run_step()  │──▶│ Write Result│  │
│   │  from File  │   │ (same path  │   │  to File    │  │
│   │             │   │  as local)  │   │             │  │
│   └─────────────┘   └─────────────┘   └─────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Step-by-Step Flow

1. **Daemon Startup** (`daemon.py::main()`)
   - Load configuration from `~/.ukbe-runner/engine/config.json`
   - Resolve engine Python path (SNAPSHOT or versioned)
   - Initialize logger and runtime directories

2. **Supervisor Loop** (`daemon.py::_run_supervisor()`)
   - Register worker with backend
   - Enter main supervision loop

3. **Poll for Work**
   - Send heartbeat to backend (status: polling)
   - Call `BackendClient.claim_step()`
   - If no work, sleep and poll again

4. **Spawn Child** (`daemon.py::_spawn_child()`)
   - Create child runtime directory
   - Write request.json to child directory
   - Spawn subprocess: `python -m agent_runner_v2.run_agent execute-step ...`
   - Set subprocess cwd to project_root for `.env` loading

5. **Monitor Child**
   - Track process liveness via `process.poll()`
   - Check log activity to detect stalls
   - Enforce step timeout (SIGTERM → grace period → SIGKILL)

6. **Child Completion**
   - Read result.json from child directory
   - Submit result to backend via `BackendClient.complete_step_run()`
   - Write result.json to job step directory (matching manual mode)

7. **Heartbeat**
   - Send child-scoped heartbeat to backend
   - Include run_id, step_run_id, pid, state, log_file

### Child Process Isolation

The daemon spawns a **fresh subprocess** for each step:
- Code changes are picked up automatically (no daemon restart needed)
- Each subprocess imports latest code from disk
- Isolation prevents step corruption from affecting supervisor
- Child working directory set to project root for credential loading

---

## Workflow Step Execution Detail

### ASCII Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     WORKFLOW STEP EXECUTION DETAIL                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        step_runner.py                                │
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
│  │   run_step()    │    │   run_action()  │    │ build_context() │   │
│  │   (Coder Step)  │    │  (Action Step)  │    │   (Context)     │   │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘   │
│           │                       │                       │          │
│           ▼                       ▼                       ▼          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Common Execution Path                       │   │
│  │                                                                 │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │   │
│  │  │ 1. Resolve│──▶│ 2. Pre-     │──▶│ 3. Invoke   │            │   │
│  │  │    Paths    │   │   flight    │   │  Coder/   │            │   │
│  │  │             │   │   Checks    │   │  Action   │            │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘            │   │
│  │                                              │                   │   │
│  │                                              ▼                   │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │   │
│  │  │ 6. Enrich   │◀──│ 5. Validate │◀──│ 4. Read     │            │   │
│  │  │   Sidecar   │   │  Artifacts  │   │  meta.json  │            │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘            │   │
│  │         │                                            │            │   │
│  │         ▼                                            ▼            │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │              Return StepResult                           │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐   │   │   │
│  │  │  │ status  │ │ remark  │ │artifacts│ │ meta_json   │   │   │   │
│  │  │  │         │ │         │ │         │ │    _path    │   │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────────┘   │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Detailed Execution Phases

#### Phase 1: Path Resolution
- Resolve `meta.json` path from step config
- Compute allowed write paths from `produces` and `updates` lists
- Take snapshot of file system before execution

#### Phase 2: Pre-flight Checks
- Validate step write contract configuration
- Check for required context variables
- Verify reference files exist

#### Phase 3: Invocation

**Coder Steps:**
- Call `coder_adapters.invoke_coder()`
- Spawn subprocess with timeout
- Stream stdout/stderr to `raw_output.txt`

**Action Steps:**
- Call `runner_actions.execute()`
- Execute Python function in-process
- Action writes its own meta.json

#### Phase 4: Meta.json Reading
- Read sidecar from resolved path
- Validate schema version (v2)
- Repair common mistakes (direct result → wrapped sidecar)
- Validate required fields:
  - `schema_version`: must be "v2"
  - `coder_result.status`: must be "APPROVED" or "REJECTED"
  - `coder_result.artifacts`: must be dict
  - `coder_result.recorded_at`: must be present

#### Phase 5: Artifact Validation
- Check each artifact path exists on disk
- Skip `.meta.json` files (sidecars)
- Validate artifacts are in step's `produces` list (declarative protection)
- Normalize artifact keys (strip `_METAJSON`, `_PATH` suffixes)

#### Phase 6: Sidecar Enrichment
- Add runner_data section (non-destructive)
- Include timing, checksums, changed paths
- Preserve original coder_result unchanged

---

## Review Loop Mechanics

### ASCII Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          REVIEW LOOP MECHANICS                                │
└─────────────────────────────────────────────────────────────────────────────┘

    Step Execution
         │
         ▼
    ┌─────────┐
    │ REVIEW  │
    │  Step   │
    └────┬────┘
         │
         ▼
    ┌─────────┐     REJECTED          ┌─────────┐
    │ Review  │──────────────────────▶│ REFINE  │
    │ Result  │   (with feedback)     │  Step   │
    └────┬────┘                       └────┬────┘
         │                                │
    APPROVED                              │
         │                                ▼
         │                           ┌─────────┐
         │                           │ Refine  │
         │                           │ Artifact│
         │                           └────┬────┘
         │                                │
         │                                ▼
         │                           ┌─────────┐
         │                           │  Back   │
         │                           │ Review  │
         │                           └────┬────┘
         │                                │
         │                ┌───────────────┼───────────────┐
         │                │               │               │
         │           REJECTED       (max_iter)      APPROVED
         │           (loop)         exceeded            │
         │                │               │             │
         │                └───────┐      │             │
         │                        ▼      ▼             ▼
         │                   ┌─────────┐         ┌─────────┐
         │                   │ REPLAN  │         │ Advance │
         │                   │  Step   │         │ to Next │
         │                   └────┬────┘         └─────────┘
         │                        │
         │              ┌─────────┴─────────┐
         │              │                   │
         │         REJECTED            APPROVED
         │         (replan               (advance)
         │         exhausted)
         │              │
         ▼              ▼
    ┌─────────────────────────┐
    │ WAITING_FOR_HUMAN_      │
    │   INTERVENTION          │
    └─────────────────────────┘

Loop Context (stored in job.json):
├── active: bool
├── loop_step: str          # Original step being reviewed
├── refine_step: str        # Step to run for refinement
├── loop_target_artifact: str
├── loop_source_review: str # Path to review file
├── loop_iteration: int
└── pre_refine_checksum: str

Replan Context (stored in job.json):
├── active: bool
├── source_review_step: str
├── replan_step: str
├── target_artifact: str
├── source_review_file: str
├── replan_attempt: int
├── trigger_reason: str
└── blocking_issues: []     # v2: always empty
```

### Review Loop Configuration

Step configuration defines review/refine behavior:

```python
{
    "name": "review_plan",
    "produces": ["REVIEW_FILE"],
    "on_reject_refine": {
        "step": "refine_plan",
        "artifact": "PLAN_FILE",
        "max_iterations": 2
    },
    "on_exhaust_replan": {
        "step": "replan_plan",
        "artifact": "PLAN_FILE",
        "max_replans": 1
    },
    "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
    "exhausted_failure_code": "REFINEMENT_EXHAUSTED"
}
```

### Loop Iteration Tracking

1. **Initial Review**: Review step produces `REVIEW_FILE`
2. **Reject with Refine Route**: If rejected and `on_reject_refine` configured:
   - Increment `loop_iteration`
   - Check against `max_iterations`
   - If within budget: activate loop context, route to refine step
3. **Refine Step**: Updates target artifact based on review feedback
4. **Return to Review**: After refine, workflow routes back to review step
5. **Loop Exhaustion**: If max iterations exceeded:
   - Try replan if `on_exhaust_replan` configured
   - Else: fail with `HUMAN_RETRY_REQUIRED`

---

## Failure Routing Flow

### ASCII Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FAILURE ROUTING FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    Exception
         │
         ▼
┌─────────────────┐
│ route_after_    │  ←── workflow_router.py entry point
│    failure()    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classify        │  ←── Map exception to (failure_class, failure_code, source)
│ Exception       │
└────────┬────────┘
         │
         ├──▶ CoderInvocationError ──▶ Check if transient ──▶ AUTO_RETRYABLE
         │
         ├──▶ MetaJsonMissingError ──▶ HUMAN_RETRY_REQUIRED
         │
         ├──▶ MetaJsonInvalidError ──▶ HUMAN_RETRY_REQUIRED
         │
         ├──▶ ArtifactMissingError ──▶ HUMAN_RETRY_REQUIRED
         │
         └──▶ Unknown Exception ──▶ FATAL
         │
         ▼
┌─────────────────┐
│ Check Non-      │  ←── Non-progressing failures don't increment reject count
│ Progressing?    │     (e.g., INVALID_RUNNER_CONFIGURATION)
└────────┬────────┘
         │
         ├──▶ Yes ──▶ WAITING_FOR_HUMAN_INTERVENTION
         │
         └──▶ No ──▶ Increment reject count
                       │
                       ▼
              ┌─────────────────┐
              │ Check Failure   │
              │ Class & Budget  │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    FATAL        Budget          AUTO_RETRYABLE
    Error        Exceeded?       (transient API)
         │             │             │
         ▼             ▼             ▼
    ┌────────┐   ┌────────┐   ┌──────────────┐
    │ FAILED │   │ FAILED │   │ WAITING_FOR_ │
    │ Status │   │ Status │   │ AUTO_RETRY   │
    └────────┘   └────────┘   └──────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │ Auto-retry   │
                              │ on next poll │
                              └──────────────┘
```

### Failure Classification

| Exception Type | Failure Class | Failure Code | Source |
|----------------|---------------|--------------|--------|
| `CoderInvocationError` (transient) | AUTO_RETRYABLE | TRANSIENT_API_ERROR | adapter |
| `CoderInvocationError` (other) | HUMAN_RETRY_REQUIRED | ADAPTER_INVOCATION_FAILED | adapter |
| `MetaJsonMissingError` | HUMAN_RETRY_REQUIRED | META_JSON_MISSING | validator |
| `MetaJsonInvalidError` | HUMAN_RETRY_REQUIRED | META_JSON_INVALID | validator |
| `ArtifactMissingError` | HUMAN_RETRY_REQUIRED | ARTIFACT_FILES_MISSING | validator |
| Unknown exception | FATAL | UNEXPECTED_RUNNER_ERROR | runner |

### Retry States

- **WAITING_FOR_AUTO_RETRY**: Transient failure, will auto-retry on next poll
- **WAITING_FOR_HUMAN_INTERVENTION**: Requires manual intervention
- **FAILED**: Terminal state, workflow cannot proceed

### Failure History Tracking

Each failure is recorded in job state:

```python
{
    "last_failure": {
        "step": "review_plan",
        "failure_class": "HUMAN_RETRY_REQUIRED",
        "failure_code": "META_JSON_MISSING",
        "failure_reason": "Coder did not write meta.json",
        "failure_source": "validator",
        "failed_at": "2026-07-10T20:00:00+08:00"
    },
    "failure_history": [
        # All failures recorded chronologically
    ],
    "retry_history": [
        # All attempts (success and failure) recorded
    ]
}
```

---

## Documentation Sync Flow

### ASCII Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENTATION SYNC FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    40_documentation_sync_v1 Workflow                     │
│                                                                          │
│  Trigger: Scheduled or manual invocation                                 │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
│  │   01_sync_docs  │───▶│  02_review_docs │───▶│  03_refine_docs │   │
│  │   (scan +       │    │  (validate)     │    │  (fix issues)   │   │
│  │    generate)    │    │                 │    │                 │   │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘   │
│          │                                               │             │
│          │          ┌─────────────────────────────────────┘             │
│          │          │                                               │
│          ▼          ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  04_validate_doc_sync                                           │ │
│  │  (final validation + summary)                                   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     sync_codebase_docs Action                           │
│                                                                          │
│  Input: Repository path                                                  │
│                                                                          │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐ │
│  │ Scan Source │──▶│ Compare with│──▶│ Generate    │──▶│ Write    │ │
│  │ Files       │   │ Inventory   │   │ Updates     │   │ Outputs  │ │
│  └─────────────┘   └─────────────┘   └─────────────┘   └──────────┘ │
│         │                 │                                          │
│         │                 ▼                                          │
│         │          ┌─────────────┐                                   │
│         │          │ Detect Drift│                                   │
│         │          │ (added/     │                                   │
│         │          │ removed/    │                                   │
│         │          │ modified)    │                                   │
│         │          └─────────────┘                                   │
│         ▼                                                            │
│  ┌─────────────┐                                                    │
│  │ Update       │                                                    │
│  │ Inventory     │                                                    │
│  │ (codebase_   │                                                    │
│  │ inventory.md) │                                                    │
│  └─────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Sync Process

1. **Scan Source Files** (`actions/scan_repo_codebase.py`)
   - Discover Python modules, tests, workflow files
   - Extract docstrings and structure
   - Identify entry points and exports

2. **Compare with Inventory** (`actions/sync_codebase_docs.py`)
   - Load existing `codebase_inventory.md`
   - Compare scanned state with recorded state
   - Detect added, removed, or modified files

3. **Detect Drift**
   - **Added files**: New modules since last sync
   - **Removed files**: Modules deleted from repo
   - **Modified files**: Changed since last verification

4. **Generate Updates**
   - Update inventory table
   - Regenerate module documentation if changed
   - Update change impact document

5. **Validate Documentation** (`actions/validate_codebase_docs.py`)
   - Check all linked documents exist
   - Verify section requirements
   - Report stale or missing documentation

### Documentation Guardrails

The system includes declarative document protection:

- **Generated docs**: Protected from manual edits via banner
- **Managed by**: Workflow ownership tracked in frontmatter
- **Change log**: Every sync records what changed
- **Validation**: CI gates can enforce documentation freshness

---

## Execution Mode Comparison

| Aspect | Local | Worker | Daemon |
|--------|-------|--------|--------|
| Entry Point | `run` command | `worker`/`poll` | `daemon` command |
| Backend Required | No | Yes | Yes |
| Steps per Invocation | Multiple (full workflow) | Single | Multiple (supervised) |
| Process Model | Main process | Main process | Supervisor + child subprocesses |
| Concurrency | Sequential | Sequential | Configurable parallelism |
| Failure Recovery | Interactive | Backend retry | Backend retry + watchdog |
| Use Case | Development, testing | Backend integration | Production supervision |

---

## Key Design Principles

1. **Single Execution Path**: All modes converge on `step_runner.run_step()`
2. **Meta.json Contract**: Only structured result channel, no markdown write-backs
3. **Hard Failures**: No silent recovery; explicit failure routing
4. **Process Isolation**: Daemon uses subprocesses for automatic code reload
5. **Shared State Machine**: `workflow_router.py` handles routing for all modes
6. **Declarative Protection**: Step configs declare allowed outputs

---

## Related Documents

- `docs/codebase/02_modules/agent-runner-v2-run-agent.md` - CLI entry point
- `docs/codebase/02_modules/agent-runner-v2-step-runner.md` - Step execution
- `docs/codebase/02_modules/agent-runner-v2-workflow-router.md` - Post-step routing
- `docs/codebase/02_modules/agent-runner-v2-daemon.md` - Daemon supervision
- `docs/codebase/02_modules/agent-runner-v2-backend-client.md` - Backend API client
- `docs/codebase/01_inventory/INTEGRATION_MAP.md` - System integration map
- `docs/codebase/01_inventory/FAILURE_MODES.md` - Failure mode reference
