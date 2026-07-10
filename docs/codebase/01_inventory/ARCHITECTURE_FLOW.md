---
template_id: "CB-04-AF"
title: "Architecture Flow - agent-runner-v2"
status: "active"
workflow: "00_master_docs_bootstrap_v1"
step: "04d_generate_architecture_flow_docs"
generated: "2026-07-10T10:15:39+08:00"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04d_generate_architecture_flow_docs`
> This file is workflow-generated and protected from manual edits.

# Architecture Flow: agent-runner-v2

This document describes the end-to-end execution flows for the agent-runner-v2 workflow orchestration engine across different usage modes.

---

## 1. Execution Modes Overview

The agent-runner-v2 supports three primary execution modes:

| Mode | Command | Use Case |
|------|---------|----------|
| **Local Run** | `ukbe-run-agent run` | Manual workflow execution on developer workstation |
| **Backend Worker** | `ukbe-run-agent worker` or `poll` | Backend-connected single-step execution |
| **Daemon** | `ukbe-run-agent daemon` | Production supervisor for continuous workflow processing |

### Mode Characteristics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXECUTION MODE SPECTRUM                              │
├──────────────────┬──────────────────┬───────────────────────────────────────┤
│   LOCAL RUN      │  BACKEND WORKER  │            DAEMON                     │
├──────────────────┼──────────────────┼───────────────────────────────────────┤
│ Interactive CLI    │ Polled execution │ Continuous supervision                │
│ Single job       │ Single step      │ Parallel step execution               │
│ Developer-driven │ Backend-driven   │ Production autonomous                 │
│ Full lifecycle   │ Step-at-a-time   │ Multi-step parallel                   │
│ Local job.json   │ Backend state    │ Backend state + local monitoring      │
└──────────────────┴──────────────────┴───────────────────────────────────────┘
```

---

## 2. Local Execution Flow

The local execution mode runs a complete workflow lifecycle from the CLI, managing job state locally in `~/.ukbe-runner/jobs/`.

### 2.1 Entry Point Sequence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LOCAL RUN ENTRY FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

    CLI Input
        │
        ▼
┌───────────────┐
│  parse_args() │  ──►  Command dispatch (run/init/worker/daemon/etc.)
└───────────────┘
        │
        ▼
┌───────────────┐     ┌──────────────────┐
│  main()       │────►│  _resolve_workflow│  ──►  Load workflow bundle
│  run_agent.py │     │  _bundle_root()   │
└───────────────┘     └──────────────────┘
        │
        ▼
┌───────────────┐     ┌──────────────────┐
│  Job Loading  │────►│  find_matching_  │  ──►  Resume existing or
│               │     │  active_job()     │      create new job
└───────────────┘     └──────────────────┘
        │
        ▼
┌───────────────┐
│  _load_group()│  ──►  Load template_groups.py from workflow bundle
└───────────────┘
        │
        ▼
┌───────────────┐     ┌──────────────────┐
│  Step Loop    │◄────│  route_after_    │  ──►  Core execution loop
│               │     │  step() /          │      (see section 4)
│               │     │  route_after_      │
│               │     │  failure()         │
└───────────────┘     └──────────────────┘
```

### 2.2 Local Job State Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LOCAL JOB STATE MACHINE                              │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐
    │  START   │
    └────┬─────┘
         │
         ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   PENDING    │────►│  IN_PROGRESS   │────►│   COMPLETED    │
│  (initial)   │     │  (step running)│     │  (all steps OK)│
└────────────────┘     └───────┬────────┘     └────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────────┐  ┌──────────────────┐
│FAILED           │  │WAITING_FOR_HUMAN_   │  │WAITING_FOR_      │
│(max rejects)    │  │INTERVENTION         │  │AUTO_RETRY        │
│                 │  │(replan exhausted)    │  │(retryable error) │
└─────────────────┘  └─────────────────────┘  └──────────────────┘
          ▲                    │                    │
          │                    │                    │
          │         ┌─────────┴─────────┐         │
          │         │                   │         │
          │         ▼                   ▼         │
          │  ┌──────────────┐    ┌──────────────┐  │
          └──┤ Human retry  │    │  Auto retry  │──┘
             └──────────────┘    └──────────────┘
```

### 2.3 Local Directory Structure

```
~/.ukbe-runner/
├── jobs/
│   └── <template_group>/
│       └── <job_id>/
│           ├── job.json              # Job state
│           ├── 01_<step_name>/       # Step 1 directory
│           │   ├── prompt.txt          # Rendered prompt
│           │   ├── meta.json         # Coder result sidecar
│           │   ├── raw_output.txt    # LLM stdout
│           │   ├── stderr.txt        # LLM stderr
│           │   ├── usage.json        # Token usage
│           │   ├── step_manifest.json# Invocation manifest
│           │   ├── raw_events.jsonl  # Raw events log
│           │   └── result.json       # Execution result
│           ├── 02_<step_name>/       # Step 2 directory
│           └── ...
├── workflows/
│   └── <workflow>/
│       ├── template_groups.py        # Workflow definition
│       └── prompts/                  # Prompt templates
└── config.json                       # Runner configuration
```

---

## 3. Backend Worker Flow

The backend worker mode connects to a remote backend API, claiming and executing single steps under backend coordination.

### 3.1 Worker Registration and Polling

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND WORKER FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐                                    ┌──────────────────────────┐
│  Worker  │                                    │        Backend API         │
│  Process │                                    │     (http://backend:8100)  │
└────┬─────┘                                    └──────────────┬─────────────┘
     │                                                         │
     │  1. REGISTER_WORKER                                   │
     │ ─────────────────────────────────────────────────────►│
     │     {worker_id, capabilities, host_name}              │
     │                                                         │
     │  2. ACKNOWLEDGE                                       │
     │ ◄─────────────────────────────────────────────────────│
     │                                                         │
     │  3. HEARTBEAT (every N seconds)                       │
     │ ─────────────────────────────────────────────────────►│
     │     {worker_id, status: "idle|busy|polling"}           │
     │                                                         │
     │  4. CLAIM_STEP                                          │
     │ ─────────────────────────────────────────────────────►│
     │                                                         │
     │  5. STEP_AVAILABLE                                      │
     │ ◄─────────────────────────────────────────────────────│
     │     {run, step_run, step_execution_spec}              │
     │                                                         │
     ▼
┌─────────────────────────┐
│  Execute Step           │  ──►  Spawns subprocess for actual execution
│  (see section 4)        │       (execute-step command)
└─────────────────────────┘
     │
     │  6. COMPLETE_STEP_RUN
     │ ─────────────────────────────────────────────────────►│
     │     {status, outcome, artifacts, failure?, review?}   │
     │                                                         │
     │  7. ACKNOWLEDGE                                         │
     │ ◄─────────────────────────────────────────────────────│
```

### 3.2 Worker Modes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORKER SUB-MODES                                     │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────┐        ┌────────────────────┐
    │   WORKER MODE      │        │    POLL MODE       │
    │  ukbe-run-agent    │        │  ukbe-run-agent    │
    │  worker ...        │        │  poll              │
    ├────────────────────┤        ├────────────────────┤
    │ Continuous polling │        │ Single execution   │
    │ --poll-seconds N   │        │ --once implied     │
    │ Can run multiple   │        │ Exits after one    │
    │ steps sequentially │        │ step or no work    │
    └────────────────────┘        └────────────────────┘
```

### 3.3 Worker Request/Result Payload

```python
# Worker request payload (backend → worker)
{
    "template_group": "task_execution_v1",
    "step": "08_impl_task",
    "job_id": "task-20260710-abc123",
    "step_execution_spec": {...},
    "workspace_root": "/path/to/project",
    "backend_url": "http://127.0.0.1:8100",
    "coder_override": "qwen",
    "max_rejects": 3
}

# Worker result payload (worker → backend)
{
    "status": "completed|failed",
    "outcome": "success|rejected|failed",
    "step_name": "08_impl_task",
    "coder_used": "qwen",
    "remark": "Step completed successfully",
    "artifacts": {"IMPL_FILE": "docs/delivery/.../impl.md"},
    "meta_json_path": ".../meta.json",
    "review": {...},  # If review step
    "usage": {"prompt_tokens": 1500, ...},
    "failure": {...}  # If failed
}
```

---

## 4. Daemon Supervision Flow

The daemon provides production-grade supervision with parallel execution, health monitoring, and automatic recovery.

### 4.1 Daemon Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DAEMON SUPERVISION ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           DAEMON PROCESS                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  _run_supervisor()                                                    │ │
│  │  • Polls backend for work                                             │ │
│  │  • Manages child process pool                                         │ │
│  │  • Sends heartbeats to backend                                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐              │
│         │                          │                          │              │
│         ▼                          ▼                          ▼              │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐         │
│  │  Child #1   │           │  Child #2   │           │  Child #N   │         │
│  │  Process    │           │  Process    │           │  Process    │         │
│  │  (subprocess│           │  (subprocess│           │  (subprocess│         │
│  │   .Popen)   │           │   .Popen)   │           │   .Popen)   │         │
│  └──────┬──────┘           └──────┬──────┘           └──────┬──────┘         │
│         │                          │                          │              │
│         ▼                          ▼                          ▼              │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐         │
│  │ execute-step│           │ execute-step│           │ execute-step│         │
│  │   subprocess│           │   subprocess│           │   subprocess│         │
│  └─────────────┘           └─────────────┘           └─────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Child Process Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CHILD PROCESS STATE MACHINE                             │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌───────────┐
    │   SPAWN   │  ──►  subprocess.Popen([python, -m, agent_runner_v2.run_agent,
    │           │        execute-step, --request-file, ...])
    └─────┬─────┘
          │
          ▼
    ┌───────────┐     ┌─────────────────────────────────────────────────────┐
    │  RUNNING  │────►│  MONITORING CHECKS:                                 │
    │           │     │  • poll() → check if process exited                 │
    └─────┬─────┘     │  • Timeout: step_timeout_seconds exceeded?          │
          │          │  • Stalled: log inactivity > stalled_seconds?       │
          │          │  • Heartbeat: send to backend every poll_seconds    │
          │          └─────────────────────────────────────────────────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌───────┐   ┌───────┐
│COMPLETED│   │FAILED  │
│        │   │        │
│proc    │   │proc     │
│return  │   │return  │
│code=0  │   │code≠0  │
└───┬────┘   └────┬───┘
    │             │
    │    ┌────────┘
    │    │
    ▼    ▼
┌─────────────────┐
│ RESULT_SUBMITTED│  ──►  _submit_worker_result() → BackendClient.complete_step_run()
└─────────────────┘
```

### 4.3 Daemon Watchdog Logic

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DAEMON WATCHDOG TRIGGERS                              │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  Check Interval │  Every poll_seconds
    └────────┬────────┘
             │
             ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │  IF now - started_at >= step_timeout_seconds:                  │
    │     → state = 'timed_out'                                      │
    │     → watchdog_reason = 'step_timeout_exceeded'                │
    │     → _terminate_child(sigterm)                              │
    ├──────────────────────────────────────────────────────────────────┤
    │  IF now - last_activity >= stalled_seconds:                    │
    │     → state = 'stalled'                                        │
    │     → watchdog_reason = 'log_inactive'                           │
    │     → Continue monitoring (warning only)                       │
    ├──────────────────────────────────────────────────────────────────┤
    │  IF term_sent_at and now - term_sent_at >= kill_grace_seconds: │
    │     → _terminate_child(sigkill=True)                           │
    │     → state = 'killed'                                         │
    │     → watchdog_reason = 'kill_grace_exceeded'                  │
    └──────────────────────────────────────────────────────────────────┘
```

### 4.4 Configuration Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DAEMON CONFIGURATION HIERARCHY                          │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │  1. CLI ARGUMENTS (highest priority)                                │
    │     ukbe-run-agent daemon --backend-url X --poll-seconds 10         │
    ├─────────────────────────────────────────────────────────────────────┤
    │  2. ENVIRONMENT VARIABLES                                           │
    │     AGENT_RUNNER_BACKEND_URL, WORKER_ID, WORKER_POLL_SEC, ...      │
    ├─────────────────────────────────────────────────────────────────────┤
    │  3. CONFIG FILE (~/.ukbe-runner/engine/config.json)                 │
    │     {backend_url, worker_id, poll_seconds, ...}                     │
    ├─────────────────────────────────────────────────────────────────────┤
    │  4. DEFAULT VALUES (lowest priority)                              │
    │     backend_url: http://127.0.0.1:8100                              │
    │     poll_seconds: 5                                                 │
    │     max_parallel: 1                                                 │
    │     step_timeout_seconds: 3600                                    │
    │     kill_grace_seconds: 30                                        │
    └─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Workflow Step Execution Detail

The core step execution flow is common across all modes, implemented in `step_runner.py`.

### 5.1 Step Execution Sequence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STEP EXECUTION SEQUENCE                               │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌───────────┐
    │ run_step()│  ──►  Entry point from run_agent.py or execute-step
    └─────┬─────┘
          │
          ▼
┌─────────────────┐
│ 1. RESOLVE      │  ──►  Compute meta.json path
│    meta.json    │      Validate write contract
│    PATH         │      Build allowed_write_paths list
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. AUDIT        │  ──►  _snapshot_allowed_write_roots()
│    FILESYSTEM   │      Record pre-execution state
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────────────────────────────────────┐
│ 3. INVOKE       │────►│ Coder Adapters (Claude/Codex/Qwen):            │
│    CODER        │     │ • Render prompt with template substitution     │
│                 │     │ • Add sidecar instruction injection            │
│                 │     │ • Invoke LLM via subprocess/API                │
│                 │     │ • Return invocation result with stdout/stderr  │
└────────┬────────┘     └─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ 4. SAVE         │  ──►  raw_output.txt, stderr.txt, usage.json,
│    ARTIFACTS    │      step_manifest.json, raw_events.jsonl
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. READ &       │  ──►  _repair_or_validate_meta_json()
│    VALIDATE     │      Must exist and conform to schema
│    meta.json    │      Raises MetaJsonMissingError if absent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. VALIDATE     │  ──►  _validate_artifact_files_exist()
│    ARTIFACTS    │      All paths in artifacts dict must exist
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. VERIFY       │  ──►  _verify_only_allowed_paths_changed()
│    FILESYSTEM   │      Detect unauthorized writes
│    CHANGES      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 8. BUILD        │  ──►  Return StepResult dataclass
│    StepResult   │      {status, remark, artifacts, meta_json_path, ...}
└─────────────────┘
```

### 5.2 Prompt Rendering Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROMPT RENDERING PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────┘

    Template File (.txt)
            │
            ▼
    ┌───────────────┐
    │ render_prompt()│
    └───────┬───────┘
            │
    ┌───────┴──────────────────────────────────────────────────────────┐
    │  1. LOAD TEMPLATE                                                │
    │     Read from workflow bundle:                                   │
    │     ~/.ukbe-runner/workflows/<workflow>/prompts/...             │
    ├────────────────────────────────────────────────────────────────────┤
    │  2. BUILD CONTEXT                                                │
    │     • Static placeholders from template_groups.py                │
    │     • Dynamic values from job state artifacts                    │
    │     • Computed paths from known_artifact_paths()                 │
    ├────────────────────────────────────────────────────────────────────┤
    │  3. SUBSTITUTE PLACEHOLDERS                                        │
    │     • {PROJECT_ANALYSIS} → actual path                           │
    │     • {STEP_NAME} → current step name                            │
    │     • {META_JSON_PATH} → computed sidecar path                   │
    ├────────────────────────────────────────────────────────────────────┤
    │  4. INJECT SIDECAR INSTRUCTIONS                                    │
    │     Append CRITICAL meta.json reporting requirement block        │
    ├────────────────────────────────────────────────────────────────────┤
    │  5. RETURN RENDERED TEXT                                           │
    └────────────────────────────────────────────────────────────────────┘
```

### 5.3 Coder Invocation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CODER INVOCATION FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌──────────────────────────────────────────────────┐
│ invoke_coder()  │────►│ Model Resolution:                                │
│                 │     │ • Resolve alias (claude → claude-opus-4)        │
│                 │     │ • Load coder config from model_mapping.json     │
└────────┬────────┘     └──────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Execution Strategy (by coder type):                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐   │
│  │   QWEN (Codex)    │    │   CLAUDE          │    │   CLAUDE via      │   │
│  │                   │    │   (direct)        │    │   Desktop           │   │
│  ├───────────────────┤    ├───────────────────┤    ├───────────────────┤   │
│  │ HTTP API call to  │    │ subprocess to     │    │ HTTP to local     │   │
│  │ api.codex.ai      │    │ claude-cli tool   │    │ Claude desktop    │   │
│  │                   │    │                   │    │ on port 3456      │   │
│  │ Streaming response│    │ Blocking call     │    │                   │   │
│  └───────────────────┘    └───────────────────┘    └───────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Return          │  ──►  InvocationResult {return_code, stdout, stderr,
│ InvocationResult│      parsed_result, usage, manifest, raw_events}
└─────────────────┘
```

---

## 6. Review Loop Mechanics

The review/refine loop enables iterative improvement of generated artifacts.

### 6.1 Review Loop Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REVIEW LOOP FLOW                                      │
└─────────────────────────────────────────────────────────────────────────────┘

    Step N: Review Step (e.g., 02_review_pre_init)
            │
            │ Produces REVIEW_FILE with decision
            │
            ▼
    ┌───────────────┐
    │ APPROVED?     │
    └───────┬───────┘
            │
       ┌────┴────┐
       │         │
      YES        NO
       │         │
       ▼         ▼
┌───────────┐  ┌─────────────────────────────────────────────────────────┐
│ Advance to│  │ Check on_reject_refine config                           │
│ next step │  │ {refine_step, loop_target_artifact, max_iterations}     │
└───────────┘  └─────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
                          ┌───────────────────────┐
                          │ Check loop_iteration  │
                          │ < max_iterations?     │
                          └───────────┬───────────┘
                                      │
                                 ┌────┴────┐
                                 │         │
                               YES         NO
                                 │         │
                                 ▼         ▼
                    ┌────────────────┐  ┌──────────────────┐
                    │ Trigger Refine │  │ Trigger Replan   │
                    │ Step (loop)    │  │ (if configured)  │
                    └───────┬────────┘  └───────┬──────────┘
                            │                   │
                            │    ┌──────────────┘
                            │    │
                            ▼    ▼
                    ┌────────────────┐
                    │ Refine Step    │  ──►  edit_mode: in_place
                    │ executes with  │      Modifies artifact directly
                    │ review_file in │      Returns to review step
                    │ context        │
                    └───────┬────────┘
                            │
                            └──────────────────────────┐
                                                       │
                            ┌──────────────────────────┘
                            │
                            ▼
                    Return to Review Step
                    (loop_iteration++)
```

### 6.2 Loop Context State

```python
# Loop context maintained in job.json
{
    "loop_context": {
        "active": true,
        "loop_step": "02_review_pre_init",
        "refine_step": "03_refine_pre_init",
        "loop_target_artifact": "PRE_INIT_FILE",
        "loop_source_review": "docs/delivery/.../02_review.md",
        "loop_iteration": 1,
        "pre_refine_checksum": null
    },
    "loop_history": [
        {
            "iteration": 1,
            "loop_step": "02_review_pre_init",
            "refine_step": "03_refine_pre_init",
            "review_result": "REJECTED",
            "review_file": "...",
            "review_at": "2026-07-10T10:00:00Z",
            "refine_result": null,
            "refine_at": null,
            "started_at": "2026-07-10T10:00:00Z",
            "resolved_at": null
        }
    ]
}
```

### 6.3 Replan Flow (After Loop Exhaustion)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REPLAN FLOW                                           │
└─────────────────────────────────────────────────────────────────────────────┘

    Review loop exhausted (iteration > max_iterations)
                    │
                    ▼
    ┌───────────────────────────────┐
    │ Check on_exhaust_replan config │
    │ {step, artifact, max_replans}  │
    └───────────────┬───────────────┘
                    │
               ┌────┴────┐
               │         │
           Config?     No config
               │         │
              YES        │
               │         ▼
               │    ┌─────────────────────────┐
               │    │ WAITING_FOR_HUMAN_      │
               │    │ INTERVENTION            │
               │    │ (refinement_exhausted)  │
               │    └─────────────────────────┘
               ▼
    ┌───────────────────────────────┐
    │ Trigger Replan Step           │
    │ (e.g., 03_replan_plan)        │
    ├───────────────────────────────┤
    │ replan_context:               │
    │   active: true                │
    │   source_review_step: "..."   │
    │   replan_step: "03_replan..."│
    │   target_artifact: "PLAN_FILE"│
    │   replan_attempt: N           │
    │   blocking_issues: []         │
    └───────────────────────────────┘
                    │
                    ▼
    Replan step executes → generates fresh artifact
                    │
                    ▼
    Returns to original review step (loop iteration reset to 0)
```

---

## 7. Failure Routing Flow

Hard failures are routed through explicit failure handling paths.

### 7.1 Failure Classification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FAILURE CLASSIFICATION                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    Exception Types:
    ┌────────────────────┬────────────────────┬──────────────────────────┐
    │ Exception          │ Classification     │ Routing                  │
    ├────────────────────┼────────────────────┼──────────────────────────┤
    │ CoderInvocationError│ AUTO_RETRYABLE     │ WAITING_FOR_AUTO_RETRY   │
    │ (process failure)  │                    │ or FATAL if exhausted   │
    ├────────────────────┼────────────────────┼──────────────────────────┤
    │ MetaJsonMissingError│ AUTO_RETRYABLE     │ WAITING_FOR_AUTO_RETRY   │
    │                    │                    │ or FATAL if exhausted   │
    ├────────────────────┼────────────────────┼──────────────────────────┤
    │ MetaJsonInvalidError│ AUTO_RETRYABLE    │ WAITING_FOR_AUTO_RETRY   │
    │                    │                    │ or FATAL if exhausted   │
    ├────────────────────┼────────────────────┼──────────────────────────┤
    │ ArtifactMissingError│ AUTO_RETRYABLE    │ WAITING_FOR_AUTO_RETRY   │
    │                    │                    │ or FATAL if exhausted   │
    ├────────────────────┼────────────────────┼──────────────────────────┤
    │ NonProgressing     │ HUMAN_RETRY_       │ WAITING_FOR_HUMAN_       │
    │ (same failure)     │ REQUIRED           │ INTERVENTION            │
    │                    │                    │ (no auto retry)         │
    ├────────────────────┼────────────────────┼──────────────────────────┤
    │ Max rejects        │ FATAL              │ FAILED                  │
    │ exceeded           │                    │ (terminal)              │
    └────────────────────┴────────────────────┴──────────────────────────┘
```

### 7.2 Failure Routing Sequence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FAILURE ROUTING SEQUENCE                               │
└─────────────────────────────────────────────────────────────────────────────┘

    Exception raised in run_step()
            │
            ▼
    ┌───────────────────┐
    │ route_after_      │
    │ failure()         │
    └─────────┬─────────┘
              │
              ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 1. CLASSIFY EXCEPTION                                               │
    │    _classify_exception_v2() → (failure_class, failure_code,       │
    │    failure_source)                                                   │
    ├─────────────────────────────────────────────────────────────────────┤
    │ 2. CHECK NON-PROGRESSING                                            │
    │    _is_non_progressing() → Same failure as before?                 │
    │    If yes: immediate human intervention                             │
    ├─────────────────────────────────────────────────────────────────────┤
    │ 3. INCREMENT COUNTERS                                               │
    │    reject_counts[step]++                                           │
    │    auto_retry_count_by_step[step]++ or                             │
    │    human_retry_count_by_step[step]++                                │
    ├─────────────────────────────────────────────────────────────────────┤
    │ 4. RECORD FAILURE                                                   │
    │    set_last_failure() → job.json["last_failure"]                   │
    │    append_failure_history() → job.json["failure_history"]          │
    ├─────────────────────────────────────────────────────────────────────┤
    │ 5. CHECK THRESHOLDS                                                 │
    │    IF failure_class == "FATAL" OR reject_counts[step] >= max_rejects │
    │       → status = FAILED (terminal)                                 │
    │    ELSE IF failure_class == "AUTO_RETRYABLE"                        │
    │       → status = WAITING_FOR_AUTO_RETRY                              │
    │    ELSE                                                             │
    │       → status = WAITING_FOR_HUMAN_INTERVENTION                      │
    ├─────────────────────────────────────────────────────────────────────┤
    │ 6. SAVE JOB STATE                                                   │
    │    save_job() → Persist to disk                                     │
    │    send_workflow_notification() → Optional notification              │
    └─────────────────────────────────────────────────────────────────────┘
```

### 7.3 Recovery Paths

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FAILURE RECOVERY PATHS                               │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │                    WAITING_FOR_AUTO_RETRY                            │
    └───────────────────────────┬─────────────────────────────────────────┘
                                │
                                │ Manual or automated retry
                                │ (ukbe-run-agent run --job-id <id>)
                                ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    prepare_state_for_retry()                        │
    │  • Clear last_failure                                               │
    │  • Reset retry counters (for auto_retryable)                       │
    │  • Keep current_step                                                │
    └───────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
                    Return to step execution


    ┌─────────────────────────────────────────────────────────────────────┐
    │                    WAITING_FOR_HUMAN_INTERVENTION                 │
    └───────────────────────────┬─────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
    ┌───────────────────────────┐  ┌───────────────────────────┐
    │ --reapply-routing         │  │ --override-step         │
    │ (Re-run routing logic)    │  │ (Force specific step)    │
    └─────────────┬─────────────┘  └─────────────┬─────────────┘
                  │                               │
                  ▼                               ▼
    ┌───────────────────────────┐  ┌───────────────────────────┐
    │ --approve-step            │  │ --force-approve-step    │
    │ (Human approval)          │  │ (Bypass review)          │
    └───────────────────────────┘  └───────────────────────────┘
```

---

## 8. Documentation Sync Flow

The documentation sync workflow reconciles codebase documentation with actual repository state.

### 8.1 Sync Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DOCUMENTATION SYNC FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    Trigger: 40_documentation_sync_v1 workflow
                    │
                    ▼
    ┌───────────────────────────┐
    │ Step 01: sync_docs          │  ──►  scan_repo_codebase.py action
    │                             │       Discovers actual repository state
    └─────────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ REPOSITORY SCAN                                                     │
    │  • List all Python modules (*.py files)                            │
    │  • Identify public APIs (exports, classes, functions)              │
    │  • Extract docstrings and type hints                               │
    │  • Map module dependencies                                         │
    │  • Detect orphaned docs (no matching source)                       │
    └─────────────────────────┬───────────────────────────────────────────┘
                                │
                                ▼
    ┌───────────────────────────┐
    │ Step 02: review_docs        │  ──►  Compare scan vs. existing docs
    └─────────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ COMPARISON MATRIX                                                   │
    │  • New modules → Create docs                                         │
    │  • Modified modules → Update docs                                    │
    │  • Deleted modules → Mark deprecated                                 │
    │  • Unchanged modules → Verify current                              │
    └─────────────────────────┬───────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ 02_review_docs│ │03_refine_docs │ │04_validate_   │
    │ (generate)    │ │ (update)      │ │ doc_sync      │
    │               │ │               │ │               │
    │ Produces:     │ │ Produces:     │ │ Validates:    │
    │ CODEBASE_     │ │ Updated       │ │ Completeness  │
    │ CHANGE_IMPACT │ │ module docs   │ │ Accuracy      │
    └───────────────┘ └───────────────┘ └───────────────┘
```

### 8.2 Sync Action Detail

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SYNC_CODEBASE_DOCS ACTION                                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │ scan_repo_codebase.py                                               │
    ├─────────────────────────────────────────────────────────────────────┤
    │ Input: project_root                                                 │
    │ Output: CODEBASE_INVENTORY, CODEBASE_CHANGE_IMPACT                  │
    ├─────────────────────────────────────────────────────────────────────┤
    │ Steps:                                                              │
    │ 1. Walk source tree (agent_runner_v2/)                              │
    │ 2. Parse each .py file:                                             │
    │    - AST extraction of classes, functions, docstrings               │
    │    - Import analysis for dependencies                              │
    │    - Decorator detection (@dataclass, etc.)                         │
    │ 3. Load existing inventory (if any)                                 │
    │ 4. Compute delta:                                                   │
    │    - added: new files/modules                                       │
    │    - removed: deleted files/modules                                 │
    │    - modified: changed signatures, docstrings                       │
    │    - unchanged: verified current                                    │
    │ 5. Write CODEBASE_INVENTORY.md                                     │
    │ 6. Write CODEBASE_CHANGE_IMPACT.md                                 │
    └─────────────────────────────────────────────────────────────────────┘
```

### 8.3 Module Documentation Modes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MODULE DOCUMENTATION MODES                              │
└─────────────────────────────────────────────────────────────────────────────┘

    Each module in codebase_inventory.md has a documentation mode:

    ┌─────────────────────────────────────────────────────────────────────┐
    │ Mode          │ Description                 │ Owner Doc            │
    ├─────────────────────────────────────────────────────────────────────┤
    │ stub          │ Minimal placeholder         │ 02_modules/...init.md│
    │ summary       │ Brief overview              │ 02_modules/*.md      │
    │ full          │ Comprehensive documentation │ 02_modules/*.md      │
    │ auto-generated│ From docstrings             │ 03_components/*.md   │
    └─────────────────────────────────────────────────────────────────────┘

    Mode assignment logic:
    • __init__.py → stub
    • actions/* → full (complex logic)
    • core modules → full (run_agent, step_runner, workflow_router)
    • schema modules → summary
    • support modules → summary
```

---

## 9. Cross-Mode Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CROSS-MODE COMPARISON                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    Aspect              │ Local Run    │ Worker       │ Daemon
    ────────────────────┼──────────────┼──────────────┼──────────────────────
    Entry Command       │ run          │ worker/poll  │ daemon
    Job State Location  │ ~/.ukbe-     │ Backend DB   │ Backend DB + local
                        │ runner/jobs/ │              │ runtime/
    Step Execution      │ Sequential   │ Single step  │ Parallel (max_parallel)
    Step Lifecycle      │ In-process   │ Subprocess   │ Child process
    Backend Connection  │ Optional     │ Required     │ Required
    Notifications       │ Optional     │ Optional     │ Full event logging
    Recovery Logic      │ Manual CLI   │ Backend-     │ Auto-retry + watchdog
                        │              │ driven       │
    Use Case            │ Development  │ CI/CD        │ Production
    Restart Required    │ No           │ No           │ No (spawns fresh)
                        │              │              │ subprocesses)

    Key Insight:
    The daemon spawns fresh subprocesses for each step, so code changes
    are picked up automatically without daemon restart.
```

---

## 10. Key Architectural Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ARCHITECTURAL PRINCIPLES                                │
└─────────────────────────────────────────────────────────────────────────────┘

    1. META.JSON CONTRACT
       • Sidecar file is the ONLY structured communication channel
       • No markdown write-backs by runner
       • No silent recovery paths

    2. DECLARATIVE PROTECTION
       • produces list controls allowed artifact writes
       • Document protection via allow-lists, not denylists
       • Unauthorized writes trigger validation errors

    3. EXPLICIT ROUTING
       • APPROVED → advance to next step
       • REJECTED → loop/replan/intervention
       • FAILURE → classified routing with retry limits

    4. SEPARATION OF CONCERNS
       • run_agent.py: CLI orchestration only
       • step_runner.py: Step execution contract
       • workflow_router.py: Post-step routing only
       • daemon.py: Child process supervision only

    5. BOOTSTRAP/RUNTIME SEPARATION
       • Packaged source seeds runtime bundles
       • Runtime loads from ~/.ukbe-runner/workflows/
       • Changes require explicit sync to take effect

    6. CENTRALIZED CONSTANTS
       • constants.py as single source of truth
       • Zero hardcoded path strings
       • Layered: FOLDER_KEY → ARTIFACT_KEY → ARTIFACT_PATH
```

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04d_generate_architecture_flow_docs` on 2026-07-10T10:15:39+08:00*
