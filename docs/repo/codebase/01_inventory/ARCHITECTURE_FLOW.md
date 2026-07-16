---
template_id: "CB-04-AF"
version: "1.0.0"
doc_type: "codebase"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:50:25+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04d_generate_architecture_flow_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Architecture Flow: agent-runner-v2

This document describes the end-to-end execution flows for agent-runner-v2, covering the three main execution modes and their interaction patterns.

## 1. Execution Modes Overview

Agent-runner-v2 supports three execution modes for workflow orchestration:

| Mode | Entry Point | Use Case | State Storage |
|------|-------------|----------|---------------|
| **Manual (Local)** | `run_agent.py run` | CLI-based development, testing, ad-hoc execution | `.ukbe-runner/jobs/<template_group>/<job_id>/` |
| **Daemon** | `daemon.py` | Long-running supervisor for backend work claiming | Spawns manual mode subprocess per claimed step |
| **Backend Worker** | Backend API + Daemon | Production execution with external orchestration | Backend database + local job state |

### Key Design Principles

1. **Unified Execution Path**: All modes converge on the same `run_step()` execution logic via `step_runner.py`
2. **Sidecar Contract**: Meta.json is the sole communication channel between coder and runner
3. **Subprocess Architecture**: Daemon spawns manual mode subprocess, ensuring code changes are picked up without restart
4. **Routing Centralization**: All post-step decisions flow through `workflow_router.py`

---

## 2. Local Execution Flow (Manual Mode)

The local execution mode is the primary interface for CLI-driven workflow execution.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCAL EXECUTION FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CLI Entry  │────▶│   Load       │────▶│   Resolve    │────▶│   Validate   │
│  run_agent   │     │   Config     │     │   Workflow   │     │   References │
│              │     │   (TOML)     │     │   Bundle     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Route      │◀────│   Save Job   │◀────│   Execute    │◀────│   Prepare    │
│   After Step │     │   State      │     │   Step       │     │   Context    │
│              │     │              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ROUTING DECISION                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  APPROVED ──────▶ advance_step() ──────▶ IN_PROGRESS | WAITING_FOR_APPROVAL  │
│  REJECTED ──────▶ _route_rejected() ───▶ LOOP | REPLAN | FAILED              │
│  EXCEPTION ─────▶ route_after_failure() ─▶ RETRY | INTERVENTION | FATAL      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Flow

1. **CLI Entry** (`run_agent.py:parse_args()`)
   - Parse command line arguments (`--template-group`, `--job-id`, `--mode`, etc.)
   - Resolve project root and workflow name

2. **Load Configuration** (`config_loader.py`, `bundle_loader.py`)
   - Load `config.json` from workspace root
   - Resolve workflow bundle root (global or local path)
   - Load workflow module with step configurations

3. **Resolve Workflow** (`run_agent.py:_load_group()`)
   - Load step configurations from workflow TOML or plugin package
   - Validate static reference files exist

4. **Resolve/Recover Job** (`run_agent.py:_resolve_manual_run()`)
   - For new job: create job state with seed artifacts
   - For existing job: load from `.ukbe-runner/jobs/<template_group>/<job_id>/job.json`
   - Determine current step to execute

5. **Prepare Context** (`step_runner.py:build_context()`)
   - Resolve artifact paths from state
   - Build prompt template with placeholders
   - Compute checksum for change detection

6. **Execute Step** (`step_runner.py:run_step()`)
   - For coder steps: invoke LLM via `coder_adapters.py`
   - For action steps: execute Python function via `runner_actions.py`
   - Read and validate meta.json sidecar

7. **Route After Step** (`workflow_router.py:route_after_step()`)
   - On APPROVED: advance to next step
   - On REJECTED: trigger loop/replan or escalate
   - On EXCEPTION: classify failure and route accordingly

8. **Save and Notify** (`job_state.py`, `notifications.py`)
   - Persist updated job state
   - Send notifications based on status change

---

## 3. Backend Worker Flow (Daemon Mode)

The daemon mode enables backend-driven workflow execution with external orchestration.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND WORKER FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   Backend API    │◀───────▶│   BackendClient  │◀───────▶│   Daemon         │
│   (External)     │  REST   │   (HTTP Client)  │  Claims │   Supervisor     │
│                  │         │                  │  Sync   │                  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
                                     │                              │
                                     │                              ▼
                                     │         ┌──────────────────────────────────┐
                                     │         │   SUPERVISOR LOOP                 │
                                     │         ├──────────────────────────────────┤
                                     │         │  1. Register worker               │
                                     │         │  2. Poll for claims               │
                                     │         │  3. Spawn child subprocess        │
                                     │         │  4. Monitor child liveness        │
                                     │         │  5. Submit result on completion   │
                                     │         │  6. Send heartbeats               │
                                     │         └──────────────────────────────────┘
                                     │                      │
                                     │                      ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   Request JSON   │◀───────▶│   Child Process  │◀───────▶│   Manual Mode    │
│   (Runtime)      │  Read   │   (Subprocess)   │  Spawn  │   Execution      │
│                  │  Write  │                  │         │                  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
                                                              │
                                                              ▼
                                         ┌────────────────────────────────────────┐
                                         │  Same execution path as local mode     │
                                         │  run_agent.py run --mode daemon        │
                                         │  --job-no <run_code>                   │
                                         └────────────────────────────────────────┘
```

### Daemon Supervisor Responsibilities

1. **Worker Registration** (`daemon.py:register_worker()`)
   - Register worker ID with backend
   - Declare capabilities and worker label (live/dev)

2. **Claim Loop** (`daemon.py:_run_supervisor()`)
   - Poll backend for claimed work
   - Respect `max_parallel` concurrent executions
   - Handle shutdown signals gracefully

3. **Child Spawning** (`daemon.py:_spawn_child()`)
   - Build request payload from backend claim
   - Set subprocess CWD to project root for `.env` loading
   - Pass job parameters via CLI arguments

4. **Watchdog Monitoring**
   - Track log file modification time for stalled detection
   - Implement step timeout with graceful termination
   - Kill grace period before SIGKILL

5. **Result Submission** (`daemon.py:_child_result()`)
   - Read result from job step directory or fallback location
   - Sync job state to backend via `sync_job_state()` API

6. **Heartbeat Management**
   - Send periodic heartbeats with child status
   - Include workflow_step_run_id for backend tracking

---

## 4. Daemon Supervision Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DAEMON SUPERVISION DETAIL                               │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │   START DAEMON  │
                            │   main()        │
                            └────────┬────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │   Register Worker             │
                     │   POST /api/workers/register  │
                     └───────────────┬───────────────┘
                                     │
        ┌────────────────────────────┴────────────────────────────┐
        │                         MAIN LOOP                         │
        │  while running or children:                               │
        ├────────────────────────────────────────────────────────────┤
        │                                                            │
        │   ┌─────────────────────────────────────────────────────┐  │
        │   │  FOR EACH CHILD:                                     │  │
        │   │    - Check process.poll() for completion            │  │
        │   │    - Check last_activity for stall detection         │  │
        │   │    - Check timeout and send termination if needed    │  │
        │   │    - Send heartbeat if interval elapsed              │  │
        │   │    - On exit: submit result, remove from children    │  │
        │   └─────────────────────────────────────────────────────┘  │
        │                                                            │
        │   ┌─────────────────────────────────────────────────────┐  │
        │   │  IF running AND slots available:                     │  │
        │   │    - Send idle heartbeat                              │  │
        │   │    - claim_step() from backend                        │  │
        │   │    - If claim received: spawn child subprocess       │  │
        │   └─────────────────────────────────────────────────────┘  │
        │                                                            │
        │   sleep(poll_seconds)                                      │
        │                                                            │
        └────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   SHUTDOWN      │
                            │   Terminate all │
                            │   children      │
                            └─────────────────┘
```

### Key Implementation Details

- **Subprocess CWD Fix**: Child processes run with CWD set to `project_root` to ensure `.env` file loading works correctly
- **Job ID Detection**: Daemon checks if job folder exists before creating new job, enabling multi-step workflow continuity
- **Dual Result Path**: Reads from job step directory first, falls back to worker runtime directory
- **Code Change Isolation**: Daemon spawns standard `run_agent.py run` subprocess, so Python code changes are picked up without daemon restart

---

## 5. Workflow Step Execution Detail

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STEP EXECUTION PIPELINE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Validate   │────▶│   Resolve    │────▶│   Render     │────▶│   Compute    │
│   Step Cfg   │     │   Context    │     │   Prompt     │     │   Checksum   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                   │
                                                   ▼
                    ┌────────────────────────────────────────────────────┐
                    │              STEP TYPE BRANCH                       │
                    ├─────────────────────┬──────────────────────────────┤
                    │                     │                              │
                    ▼                     ▼                              ▼
            ┌──────────────┐      ┌──────────────┐              ┌──────────────┐
            │   CODER      │      │   ACTION     │              │   REVIEW     │
            │   (LLM)      │      │   (Python)   │              │   (Special)  │
            └──────────────┘      └──────────────┘              └──────────────┘
                    │                     │                              │
                    └──────────┬──────────┴──────────────────────────────┘
                               ▼
                    ┌──────────────────┐
                    │   Read/Validate  │
                    │   meta.json      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Validate       │
                    │   Artifacts      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Enrich Sidecar │
                    │   (runner_data)  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Return         │
                    │   StepResult     │
                    └──────────────────┘
```

### Context Resolution

The `build_context()` function in `step_runner.py` builds the execution context:

1. **Artifact Path Resolution**: Resolves `REFERENCE_FILES` and `PRODUCED_FILES` paths
2. **Placeholder Substitution**: Replaces `{ARTIFACT_KEY_*}` tokens with resolved paths
3. **Special Keys**: Handles `_METAJSON` suffix for sidecar paths
4. **Governance Injection**: Adds bundle governance blocks for bootstrap workflows

### Meta.json Validation

The `_read_and_validate_meta_json()` function validates:

- Schema version (`v2` or legacy `artifact_meta_v1`)
- `coder_result` object with `status`, `artifacts`, `remark`
- Status must be `APPROVED` or `REJECTED`
- Timestamps and reject_code (optional)

### Artifact Validation

Multiple validation layers:

1. **File Existence**: `_validate_artifact_files_exist()` checks all claimed files exist
2. **Produces List Conformance**: `_validate_artifacts_in_produces_list()` enforces declarative contract
3. **Template Conformance**: `_validate_template_conformance()` checks template_ref compliance

---

## 6. Review Loop Mechanics

Review steps enable iterative refinement of generated documents.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REVIEW LOOP FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   GENERATE STEP  │────────▶│   REVIEW STEP    │────────▶│   APPROVED?      │
│   (Coder)        │         │   (Coder)        │         │                  │
└──────────────────┘         └──────────────────┘         └────────┬─────────┘
                                                              │
                                      ┌───────────────────────┴───────┐
                                      │                               │
                                      ▼                               ▼
                              ┌──────────────┐               ┌──────────────┐
                              │   YES        │               │   NO         │
                              │   APPROVED   │               │   REJECTED   │
                              └──────┬───────┘               └──────┬───────┘
                                     │                              │
                                     ▼                              ▼
                              ┌──────────────┐               ┌──────────────────┐
                              │   ADVANCE     │               │   CHECK LOOP     │
                              │   TO NEXT     │               │   CONFIG         │
                              └──────────────┘               └────────┬─────────┘
                                                                      │
                                         ┌────────────────────────────┴───────┐
                                         │                                    │
                                         ▼                                    ▼
                                 ┌──────────────┐                      ┌──────────────┐
                                 │   ITERATION  │                      │   EXHAUSTED  │
                                 │   < MAX      │                      │   > MAX      │
                                 └──────┬───────┘                      └──────┬───────┘
                                        │                                     │
                                        ▼                                     ▼
                                 ┌──────────────┐                      ┌──────────────┐
                                 │   ACTIVATE   │                      │   TRY REPLAN │
                                 │   REFINE     │                      │   OR FAIL    │
                                 │   LOOP       │                      │              │
                                 └──────┬───────┘                      └──────────────┘
                                        │
                                        ▼
                                 ┌──────────────────────────────────────────────┐
                                 │   LOOP STATE (loop_context):                 │
                                 │   - active: true                             │
                                 │   - loop_step: "03_refine_docs"              │
                                 │   - refine_step: "02_review_docs"            │
                                 │   - loop_target_artifact: "DRAFT_FILE"       │
                                 │   - loop_source_review: "REVIEW_FILE"        │
                                 │   - loop_iteration: N                        │
                                 │   - pre_refine_checksum: <hash>              │
                                 └──────────────────────────────────────────────┘
```

### Loop Configuration

Defined in `workflow.toml` under `step_configs.<step>.on_reject_refine`:

```toml
[step_configs.02_review]
on_reject_refine = { step = "03_refine", artifact = "DRAFT_FILE", max_iterations = 2 }
reject_code_routes = { QUALITY_ISSUE = { step = "03_refine", artifact = "DRAFT_FILE" } }
on_exhaust_replan = { step = "01_generate", artifact = "DRAFT_FILE", max_replans = 1 }
```

### Loop Activation

The `activate_refine_loop()` function in `recovery_runtime.py`:

1. Sets `loop_context.active = true`
2. Sets `current_step` to the refine step
3. Stores review file path for refine step input
4. Records checksum of target artifact before refinement

### Loop Termination

When iterations exceed `max_iterations`:

1. Check for `on_exhaust_replan` configuration
2. If replan configured and attempts remaining: activate replan
3. Otherwise: set `WAITING_FOR_HUMAN_INTERVENTION` status

---

## 7. Failure Routing Flow

All failures flow through centralized routing in `workflow_router.py`.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FAILURE CLASSIFICATION                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────────────────┐
                    │              FAILURE SOURCE               │
                    ├──────────────────────────────────────────┤
                    │   • CoderInvocationError (process fail)  │
                    │   • MetaJsonMissingError (no sidecar)    │
                    │   • MetaJsonInvalidError (bad schema)    │
                    │   • ArtifactMissingError (files missing) │
                    │   • Model REJECTED status                │
                    └───────────────────┬──────────────────────┘
                                        │
                                        ▼
                    ┌──────────────────────────────────────────┐
                    │         CLASSIFY FAILURE                  │
                    ├──────────────────────────────────────────┤
                    │   _classify_exception_v2()               │
                    │   _classify_model_rejection()            │
                    └───────────────────┬──────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼                                       ▼
        ┌──────────────────────┐              ┌──────────────────────┐
        │   FAILURE CLASS      │              │   FAILURE SOURCE     │
        ├──────────────────────┤              ├──────────────────────┤
        │   AUTO_RETRYABLE     │              │   adapter            │
        │   (transient errors) │              │   validator          │
        │                      │              │   model              │
        │   HUMAN_RETRY_REQUIRED│             │   runner             │
        │   (config issues)    │              │                      │
        │                      │              │                      │
        │   FATAL              │              │                      │
        │   (unrecoverable)    │              │                      │
        └──────────┬───────────┘              └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────────────────────────────────┐
        │                    ROUTING DECISION                           │
        ├──────────────────────────────────────────────────────────────┤
        │                                                               │
        │   AUTO_RETRYABLE ────────────────────────────────────┐       │
        │     └─▶ WAITING_FOR_AUTO_RETRY                        │       │
        │        (automatic retry on next run)                  │       │
        │                                                       │       │
        │   HUMAN_RETRY_REQUIRED ──────────────────────────────┤       │
        │     └─▶ WAITING_FOR_HUMAN_INTERVENTION               │       │
        │        (requires manual intervention)                 │       │
        │                                                       │       │
        │   FATAL ──────────────────────────────────────────────┤       │
        │     └─▶ FAILED                                       │       │
        │        (terminal state)                               │       │
        │                                                       │       │
        │   Also: reject_count >= max_rejects ──────────────────┤       │
        │     └─▶ FAILED (exceeded retry budget)                │       │
        │                                                       │       │
        └───────────────────────────────────────────────────────────────┘
```

### Exception Classification

| Exception Type | Failure Class | Failure Code | Behavior |
|----------------|---------------|--------------|----------|
| `CoderInvocationError` (transient) | AUTO_RETRYABLE | TRANSIENT_API_ERROR | Auto retry |
| `CoderInvocationError` (other) | HUMAN_RETRY_REQUIRED | ADAPTER_INVOCATION_FAILED | Manual intervention |
| `MetaJsonMissingError` | HUMAN_RETRY_REQUIRED | META_JSON_MISSING | Manual intervention |
| `MetaJsonInvalidError` | HUMAN_RETRY_REQUIRED | META_JSON_INVALID | Manual intervention |
| `ArtifactMissingError` | HUMAN_RETRY_REQUIRED | ARTIFACT_FILES_MISSING | Manual intervention |
| Unknown exception | FATAL | UNEXPECTED_RUNNER_ERROR | Terminal failure |

### Model Rejection Classification

Based on `reject_code` and `remark` content:

- **TRANSIENT**: Network errors, rate limits → AUTO_RETRYABLE
- **PREFLIGHT**: Missing inputs, schema issues → HUMAN_RETRY_REQUIRED
- **POLICY**: Out of scope, forbidden → FATAL
- **DEFAULT**: Other → HUMAN_RETRY_REQUIRED

---

## 8. Documentation Sync Flow

Documentation synchronization between repo and runtime paths.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION SYNC FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐                           ┌──────────────────┐
│   WORKFLOW       │                           │   ARTIFACT       │
│   GENERATES      │──────────────────────────▶│   OUTPUT         │
│   DOCUMENT       │                           │   (repo path)    │
└──────────────────┘                           └──────────────────┘
                                                        │
                                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         PATH RESOLUTION                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│   1. Check context for pre-resolved path                                     │
│   2. Resolve from state.artifacts dict                                       │
│   3. Compute from constants.py (ARTIFACT_PATH_*)                             │
│   4. Fallback to step_dir/meta.json for producing steps                      │
└──────────────────────────────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   ARTIFACT       │────────▶│   VALIDATION     │────────▶│   SIDECAR        │
│   EXISTENCE      │         │   (optional)     │         │   WRITE          │
│   CHECK          │         │                  │         │   (meta.json)    │
└──────────────────┘         └──────────────────┘         └──────────────────┘
                                                        │
                                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      STATE PERSISTENCE                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│   • job.json: artifacts dict, current_step, status                           │
│   • step_manifest.json: execution metadata                                   │
│   • usage.json: token counts and model info                                  │
│   • result.json: final step output (daemon mode)                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Path Resolution Strategy

1. **Context Variables**: Pre-resolved paths injected into prompt context
2. **State Artifacts Dict**: Paths from previous steps stored in job state
3. **Constants Module**: Centralized `ARTIFACT_PATH_*` definitions
4. **Step Directory Fallback**: For producing steps where artifact doesn't exist yet

### Sidecar Enrichment

The `enrich_sidecar()` function adds runner-managed metadata:

```json
{
  "schema_version": "v2",
  "coder_result": { ... },
  "runner_data": {
    "step": "02_generate_docs",
    "coder_used": "opencode",
    "invoked_at": "2026-07-16T22:00:00+08:00",
    "finished_at": "2026-07-16T22:05:00+08:00",
    "prompt_checksum": "abc123...",
    "allowed_write_paths": ["docs/repo/..."],
    "changed_paths": ["docs/repo/codebase/..."]
  },
  "usage": { "input_tokens": 5000, "output_tokens": 2000 }
}
```

---

## 9. Key Module Interactions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MODULE DEPENDENCY GRAPH                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │   run_agent.py  │
                            │   (Entry Point) │
                            └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ step_runner  │ │workflow_router│ │   job_state  │
            │              │ │              │ │              │
            │ • run_step() │ │ • route_*()  │ │ • save_job() │
            │ • run_action │ │ • classify() │ │ • load_job() │
            └──────┬───────┘ └──────────────┘ └──────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│coder_adapters│ │runtime_context│ │  constants   │
│              │ │              │ │              │
│• invoke()    │ │• PROJECT_ROOT│ │• ARTIFACT_*  │
│• parse()     │ │• JOBS_ROOT   │ │• FOLDER_*    │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 10. Summary

The agent-runner-v2 architecture follows these core principles:

1. **Single Execution Path**: All modes converge on `step_runner.py` for consistent behavior
2. **Sidecar Contract**: Meta.json is the sole LLM communication channel
3. **Centralized Routing**: `workflow_router.py` handles all post-step decisions
4. **State Isolation**: Job state persisted to `.ukbe-runner/jobs/` with atomic writes
5. **Subprocess Delegation**: Daemon spawns manual mode for automatic code update pickup
6. **Declarative Workflows**: TOML manifests define steps, routing, and artifact contracts

This architecture enables:
- CLI-driven development with immediate feedback
- Backend integration for production orchestration
- Iterative refinement via review loops
- Graceful failure handling with recovery paths
- Zero-code-change daemon updates