---
template_id: "CB-04-AF"
managed_by: workflow-generated
generated: "2026-07-09T21:42:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04d_generate_architecture_flow_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04d_generate_architecture_flow_docs`
> This file is workflow-generated and protected from manual edits.

# Architecture Flow: agent-runner-v2

Comprehensive documentation of end-to-end execution flows for different usage modes.

---

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

The agent-runner-v2 supports three primary execution modes:

| Mode | Entry Point | Use Case | Key Characteristics |
|------|-------------|----------|---------------------|
| **Local** | `ukbe-run-agent run` | Interactive development, manual workflows | Direct CLI invocation, prompt rendering, immediate feedback |
| **Backend Worker** | `ukbe-run-agent worker` / `poll` | Backend-connected execution | Claims work from backend API, executes steps, reports results |
| **Daemon** | `ukbe-run-agent daemon` | Production supervision | Long-running supervisor, manages child processes, heartbeats |

All modes share the same core execution engine but differ in orchestration and lifecycle management.

---

## Local Execution Flow

### Sequence Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │     │   run_agent  │     │  step_runner │     │   Coder    │     │     job.json │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                    │                   │                   │
       │  ukbe-run-agent   │                    │                   │                   │
       │  run --template-group X                 │                   │                   │
       │──────────────────>│                    │                   │                   │
       │                   │                    │                   │                   │
       │                   │  Load/Create job   │                   │                   │
       │                   │───────────────────>│                   │                   │
       │                   │                    │                   │                   │
       │                   │  Resolve step      │                   │                   │
       │                   │  Render prompt     │                   │                   │
       │                   │───────────────────>│                   │                   │
       │                   │                    │                   │                   │
       │                   │                    │  Invoke coder     │                   │
       │                   │                    │  (Claude/Qwen)    │                   │
       │                   │                    │──────────────────>│                   │
       │                   │                    │                   │                   │
       │                   │                    │                   │  Write artifacts  │
       │                   │                    │                   │  Write meta.json  │
       │                   │                    │<──────────────────│                   │
       │                   │                    │                   │                   │
       │                   │                    │  Validate meta    │                   │
       │                   │                    │  Validate artifacts│                  │
       │                   │<───────────────────│                   │                   │
       │                   │                    │                   │                   │
       │                   │  Route after step  │                   │                   │
       │                   │  (APPROVED/REJECT) │                   │                   │
       │                   │───────────────────>│                   │                   │
       │                   │                    │                   │                   │
       │                   │  Update job.json   │                   │                   │
       │                   │─────────────────────────────────────────────────────────────>│
       │                   │                    │                   │                   │
       │  Result JSON      │                    │                   │                   │
       │<──────────────────│                    │                   │                   │
       │                   │                    │                   │                   │
```

### ASCII Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              LOCAL EXECUTION FLOW                                      │
└────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │    Start    │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │ Parse CLI args  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐     No     ┌─────────────────┐
    │ Job ID provided?│─────────────>│ Create new job  │
    └────────┬────────┘              └────────┬────────┘
             │ Yes                            │
             ▼                                │
    ┌─────────────────┐                       │
    │ Load existing   │<──────────────────────┘
    │ job state       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Resolve current │
    │ step            │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Load step cfg   │
    │ Build context   │
    │ Render prompt   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐     Action    ┌─────────────────┐
    │ Is action step? │───────────────>│ Execute action  │
    └────────┬────────┘                └────────┬────────┘
             │ No                             │
             ▼                                │
    ┌─────────────────┐                      │
    │ Invoke coder    │                      │
    │ (subprocess)    │                      │
    └────────┬────────┘                      │
             │                               │
             ▼                               │
    ┌─────────────────┐                      │
    │ Coder executes  │                      │
    │ writes artifacts│                      │
    │ writes meta.json│                      │
    └────────┬────────┘                      │
             │                               │
             └──────────────┬────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Read meta.json │
                 │ Validate       │
                 │ artifacts      │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Route result    │
                 │ APPROVED/REJECT │
                 └────────┬────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │ APPROVED  │  │ REJECTED  │  │ FAILURE   │
    └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
          │              │              │
          ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │ Advance   │  │ Check     │  │ Classify  │
    │ to next   │  │ on_reject │  │ exception │
    │ step      │  │ _refine   │  │           │
    └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
          │              │              │
          │        ┌─────┴─────┐        │
          │        │           │        │
          │   ┌────┴────┐ ┌────┴────┐  │
          │   │ Loop    │ │ Terminal│  │
          │   │ refine  │ │ reject  │  │
          │   └────┬────┘ └────┬────┘  │
          │        │           │       │
          │   ┌────┴────┐      │       │
          │   │ Replan  │      │       │
          │   │ trigger │      │       │
          │   └────┬────┘      │       │
          │        │           │       │
          └────────┴───────────┴───────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Update job.json │
            │ Save state      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ More steps?       │
            └────────┬────────┘
               │Yes        │No
               ▼           ▼
        ┌──────────┐  ┌──────────┐
        │ Continue │  │ Complete │
        │ loop     │  │ job      │
        └─────┬────┘  └────┬─────┘
              │            │
              └────────────┘
                     │
                     ▼
              ┌──────────┐
              │   End    │
              └──────────┘
```

### Key Components

| Component | File | Responsibility |
|-----------|------|----------------|
| CLI Parser | `run_agent.py::parse_args()` | Argument parsing, command dispatch |
| Job Loader | `job_state.py::load_job()` | Deserialize job.json, migration, reconciliation |
| Step Runner | `step_runner.py::run_step()` | Prompt rendering, coder invocation, validation |
| Router | `workflow_router.py::route_after_step()` | Post-step routing logic |

---

## Backend Worker Flow

The worker mode connects to a backend API to claim and execute workflow steps.

### Sequence Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Backend   │     │    Worker    │     │  execute-step│     │  step_runner│     │    Coder    │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                    │                   │                   │
       │                   │  Register worker   │                   │                   │
       │<──────────────────│                    │                   │                   │
       │                   │                    │                   │                   │
       │  Claim step       │                    │                   │                   │
       │<──────────────────│                   │                   │                   │
       │                   │                    │                   │                   │
       │  Return claim     │                    │                   │                   │
       │──────────────────>│                   │                   │                   │
       │                   │                    │                   │                   │
       │                   │  Build request.json│                   │                   │
       │                   │──────────────────>│                   │                   │
       │                   │                    │                   │                   │
       │                   │                    │  Run step         │                   │
       │                   │                    │──────────────────>│                   │
       │                   │                    │                   │                   │
       │                   │                    │                   │  Invoke coder     │
       │                   │                    │                   │──────────────────>│
       │                   │                    │                   │                   │
       │                   │                    │                   │  Write artifacts  │
       │                   │                    │                   │  Write meta.json  │
       │                   │                    │                   │<──────────────────│
       │                   │                    │                   │                   │
       │                   │                    │<──────────────────│                   │
       │                   │                    │                   │                   │
       │                   │                    │                   │                   │
       │                   │  Write result.json │                   │                   │
       │                   │<──────────────────│                   │                   │
       │                   │                    │                   │                   │
       │                   │  Submit result     │                   │                   │
       │<──────────────────│                    │                   │                   │
       │                   │                    │                   │                   │
       │  Acknowledge      │                    │                   │                   │
       │──────────────────>│                   │                   │                   │
       │                   │                    │                   │                   │
```

### ASCII Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             BACKEND WORKER FLOW                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │    Start    │
    │   worker    │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │ Load config     │
    │ Backend URL     │
    │ Worker ID       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Register worker │
    │ with backend    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Poll for work   │<─────────────────────────────┐
    │ (claim_step)    │                              │
    └────────┬────────┘                              │
             │                                        │
             ▼                                        │
    ┌─────────────────┐     No work      ┌─────────┐│
    │ Work available? │─────────────────>│ Wait    ││
    └────────┬────────┘                    │ Sleep   ││
             │ Yes                         └────┬────┘│
             ▼                                  │     │
    ┌─────────────────┐                         │     │
    │ Build request   │                         │     │
    │ payload         │                         │     │
    └────────┬────────┘                         │     │
             │                                  │     │
             ▼                                  │     │
    ┌─────────────────┐                        │     │
    │ Spawn subprocess│                        │     │
    │ execute-step    │                        │     │
    └────────┬────────┘                        │     │
             │                                  │     │
             ▼                                  │     │
    ┌─────────────────┐                        │     │
    │ Execute step    │                        │     │
    │ (same as local) │                        │     │
    └────────┬────────┘                        │     │
             │                                  │     │
             ▼                                  │     │
    ┌─────────────────┐                        │     │
    │ Write result    │                        │     │
    │ to result.json  │                        │     │
    └────────┬────────┘                        │     │
             │                                  │     │
             ▼                                  │     │
    ┌─────────────────┐                        │     │
    │ Submit result   │                        │     │
    │ to backend      │                        │     │
    │ (complete_step) │                        │     │
    └────────┬────────┘                        │     │
             │                                  │     │
             └──────────────────────────────────┘     │
                       │                               │
                       └───────────────────────────────┘
```

### Worker Commands

| Command | Purpose | Behavior |
|---------|---------|----------|
| `worker` | Long-running worker | Polls continuously, executes multiple steps |
| `poll` | Single-shot worker | Claims one step, executes, exits |
| `execute-step` | Internal command | Executes a single step from request.json (used by daemon) |

---

## Daemon Supervision Flow

The daemon is a production-grade supervisor that manages child processes for workflow execution.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DAEMON SUPERVISOR                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  Main Process   │    │  Child Process 1│    │  Child Process 2│         │
│  │  (Supervisor)   │    │  (execute-step) │    │  (execute-step)│         │
│  │                 │    │                 │    │                 │         │
│  │  - Poll backend │    │  - Run step     │    │  - Run step     │         │
│  │  - Spawn children│   │  - Write output │    │  - Write output │         │
│  │  - Monitor      │    │  - Exit         │    │  - Exit         │         │
│  │  - Heartbeat    │    │                 │    │                 │         │
│  └────────┬────────┘    └────────┬──────┘    └────────┬──────┘         │
│           │                      │                    │                  │
│           │         ┌────────────┴────────────────────┘                  │
│           │         │                                                     │
│           ▼         ▼                                                     │
│  ┌─────────────────────────────────┐                                     │
│  │        JSONL Log Files          │                                     │
│  │   - worker-daemon.jsonl         │                                     │
│  │   - child-events.jsonl          │                                     │
│  │   - child.log (stdout/err)      │                                     │
│  └─────────────────────────────────┘                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ASCII Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              DAEMON SUPERVISION FLOW                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │    Start    │
    │   daemon    │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │ Load config     │
    │ Parse CLI args  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Setup signal    │
    │ handlers        │
    │ (SIGINT, SIGTERM)│
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Register worker │
    │ with backend    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Initialize      │<────────────────────────────────────────────────────┐
    │ children dict   │                                                      │
    └────────┬────────┘                                                      │
             │                                                                │
             ▼                                                                │
    ┌─────────────────┐                                                       │
    │ Check running   │                                                       │
    │ flag            │                                                       │
    └────────┬────────┘                                                       │
       │Yes        │No (shutdown)                                              │
       ▼           ▼                                                          │
    ┌────────┐  ┌────────┐                                                      │
    │ Continue│  │ Cleanup│                                                     │
    │         │  │ children│                                                    │
    └────┬────┘  └───┬────┘                                                     │
         │          │                                                         │
         │     ┌────┴────┐                                                     │
         │     │ Terminate│                                                    │
         │     │ remaining│                                                    │
         │     │ children │                                                    │
         │     └────┬────┘                                                     │
         │          │                                                         │
         │          ▼                                                         │
         │     ┌────────┐                                                      │
         │     │  End   │                                                      │
         │     └────────┘                                                      │
         │                                                                      │
         ▼                                                                      │
    ┌─────────────────┐                                                         │
    │ Monitor existing│                                                         │
    │ children        │                                                         │
    └────────┬────────┘                                                         │
             │                                                                   │
    ┌────────┼────────┬────────┬────────┐                                        │
    ▼        ▼        ▼        ▼        ▼                                        │
┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐                                    │
│Running││Stalled││Timeout││Exited ││Killed │                                    │
└───┬───┘└───┬───┘└───┬───┘└───┬───┘└───┬───┘                                    │
    │        │        │        │        │                                       │
    │   Send │   Send │   Send │ Submit │                                       │
    │   HB   │   HB   │   SIG  │ result │                                       │
    │        │        │   TERM │        │                                       │
    │        │        │        │        │                                       │
    └────────┴────────┴────────┴────────┘                                       │
                      │                                                        │
                      ▼                                                        │
             ┌─────────────────┐                                               │
             │ Claim new work  │                                               │
             │ (if capacity)   │                                               │
             └────────┬────────┘                                               │
              │Yes         │No                                                  │
              ▼            │                                                   │
       ┌───────────┐       │                                                   │
       │ Spawn child│       │                                                   │
       │ process   │       │                                                   │
       │ execute-  │       │                                                   │
       │ step      │       │                                                   │
       └─────┬─────┘       │                                                   │
             │             │                                                   │
             └─────────────┘───────────────────────────────────────────────────┘
```

### Daemon Responsibilities

| Responsibility | Implementation | Details |
|----------------|----------------|---------|
| **Child Spawning** | `_spawn_child()` | Creates subprocess with `execute-step` command |
| **Process Monitoring** | `_run_supervisor()` | Polls child processes, checks exit codes |
| **Timeout Management** | Watchdog timers | SIGTERM after `step_timeout_seconds`, SIGKILL after grace period |
| **Stall Detection** | File mtime checks | Marks stalled if no log/output activity |
| **Heartbeat** | `_send_child_heartbeat()` | Reports child status to backend |
| **Result Submission** | `_submit_worker_result()` | Posts results to backend API |
| **Log Aggregation** | JSONL appenders | Structured logging for all events |

### Child Execution Lifecycle

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Spawned │───>│ Running │───>│ Stalled │───>│ Timed   │───>│ Killed  │
└─────────┘    └─────────┘    └────┬────┘    │ Out     │    └─────────┘
     │              │              │         └────┬────┘         │
     │              │              │              │              │
     │              │         ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
     │              │         │ Recovered│    │ SIGTERM │    │ SIGKILL │
     │              │         └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │              │
     │              └──────────────┘              │              │
     │                     │                     │              │
     └─────────────────────┴─────────────────────┴──────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Exited    │
                    │ (completed/ │
                    │  failed)    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Submit      │
                    │ result to   │
                    │ backend     │
                    └─────────────┘
```

---

## Workflow Step Execution Detail

### Step Execution Sequence

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         STEP EXECUTION DETAIL                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                         PREPARATION PHASE                                   │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   Start     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │ Load step cfg   │
    │ from template   │
    │ groups          │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Resolve coder     │
    │ (model mapping)   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Load reference    │
    │ artifacts         │
    │ (inputs)          │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Build context     │
    │ (placeholder      │
    │ substitution)     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Resolve prompt    │
    │ path              │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Render prompt     │
    │ (template +       │
    │ context)          │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                         EXECUTION PHASE                                     │
    └─────────────────────────────────────────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ Compute checksum  │
    │ (prompt hash)     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐     Action step    ┌─────────────────┐
    │ Is action?        │───────────────────>│ Run action      │
    └────────┬────────┘                    │ (deterministic) │
             │ No                            └────────┬────────┘
             ▼                                         │
    ┌─────────────────┐                                │
    │ Invoke coder      │                                │
    │ (subprocess)      │<───────────────────────────────┘
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Wait for coder    │
    │ completion        │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Save raw_output   │
    │ Save stderr       │
    │ Save usage.json   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                      VALIDATION PHASE                                     │
    └─────────────────────────────────────────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ Read meta.json    │
    │ (with repair      │
    │ fallback)         │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Validate schema   │
    │ - schema_version  │
    │ - coder_result    │
    │ - status          │
    │ - artifacts       │
    │ - recorded_at     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Validate artifact │
    │ files exist       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐    Template ref    ┌─────────────────┐
    │ Check template    │─────────────────>│ Validate        │
    │ conformance       │                    │ sections        │
    └────────┬────────┘                    └─────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ Validate against  │
    │ produces list     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                      ENRICHMENT PHASE                                       │
    └─────────────────────────────────────────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ Enrich sidecar    │
    │ with runner_data  │
    │ (atomic write)    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Return StepResult │
    │ to router         │
    └─────────────────┘
```

### Sidecar Contract (meta.json)

The `meta.json` sidecar is the **only** structured communication channel between the coder and the runner.

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "Brief summary of what was accomplished",
    "artifacts": {
      "ARTIFACT_KEY": "relative/path/to/file.md"
    },
    "recorded_at": "2026-07-09T21:42:00+08:00",
    "reject_code": "OPTIONAL_CODE"  // Only if REJECTED
  },
  "runner_data": {
    "step": "step_name",
    "coder_used": "claude|codex|qwen",
    "invoked_at": "2026-07-09T21:40:00+08:00",
    "finished_at": "2026-07-09T21:42:00+08:00",
    "prompt_checksum": "sha256_hash",
    "enriched_at": "2026-07-09T21:42:01+08:00"
  }
}
```

---

## Review Loop Mechanics

The review loop allows iterative refinement of artifacts when a step is REJECTED.

### Review Loop Flow

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              REVIEW LOOP MECHANICS                                     │
└────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ Step returns      │
    │ REJECTED          │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Check on_reject   │
    │ _refine config    │
    └────────┬────────┘
        │No        │Yes
        ▼          ▼
┌──────────────┐  ┌─────────────────┐
│ Classify as   │  │ Start review    │
│ terminal      │  │ loop            │
│ rejection     │  └────────┬────────┘
└────────┬──────┘           │
         │                  ▼
         │         ┌─────────────────┐
         │         │ Increment       │
         │         │ loop_iteration  │
         │         └────────┬────────┘
         │                  │
         │                  ▼
         │         ┌─────────────────┐
         │         │ Check max_iter  │
         │         │ exceeded?       │
         │         └────────┬────────┘
         │            │Yes       │No
         │            ▼          ▼
         │    ┌──────────┐  ┌─────────────────┐
         │    │ Check    │  │ Set refine_step │
         │    │ replan   │  │ as current      │
         │    │ config   │  │                 │
         │    └────┬─────┘  └────────┬────────┘
         │         │                 │
         │    ┌────┴────┐            │
         │    │ Trigger │            │
         │    │ replan  │            │
         │    └────┬────┘            │
         │         │                 │
         └─────────┴─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Execute refine  │
              │ step            │
              │ (coder writes   │
              │  updated artifact)│
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Validate result   │
              └────────┬────────┘
                  │APPROVED │REJECTED
                  ▼          ▼
           ┌──────────┐  ┌─────────────────┐
           │ Continue │  │ Loop again      │
           │ to next  │  │ (if iterations  │
           │ step     │  │  remaining)     │
           └────┬─────┘  └────────┬────────┘
                │                 │
                └─────────────────┘
                          │
                          ▼
                   ┌─────────────────┐
                   │ Update loop     │
                   │ history         │
                   │ in job.json     │
                   └─────────────────┘
```

### Loop Context Structure

```json
{
  "loop_context": {
    "active": true,
    "loop_step": "original_step_name",
    "refine_step": "refine_step_name",
    "loop_target_artifact": "ARTIFACT_KEY",
    "loop_source_review": "path/to/review.md",
    "loop_iteration": 1,
    "pre_refine_checksum": "sha256_hash"
  },
  "loop_history": [
    {
      "iteration": 1,
      "loop_step": "original_step_name",
      "refine_step": "refine_step_name",
      "review_result": "REJECTED",
      "review_file": "path/to/review.md",
      "review_at": "2026-07-09T21:42:00+08:00",
      "refine_result": "APPROVED",
      "refine_at": "2026-07-09T21:45:00+08:00",
      "started_at": "2026-07-09T21:42:00+08:00",
      "resolved_at": "2026-07-09T21:45:00+08:00"
    }
  ]
}
```

### Replan Context Structure

When refinement loops are exhausted, a replan may be triggered:

```json
{
  "replan_context": {
    "active": true,
    "source_review_step": "original_step_name",
    "replan_step": "replan_step_name",
    "target_artifact": "ARTIFACT_KEY",
    "source_review_file": "path/to/review.md",
    "replan_attempt": 1,
    "pre_replan_checksum": "sha256_hash",
    "trigger_reason": "REFINEMENT_EXHAUSTED",
    "blocking_issues": [],
    "previous_blocking_issue_count": 0,
    "previous_blocking_issue_severity": 0
  }
}
```

---

## Failure Routing Flow

The failure routing system classifies exceptions and routes them appropriately.

### Failure Classification

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FAILURE ROUTING FLOW                                      │
└────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                         EXCEPTION SOURCES                                   │
    └─────────────────────────────────────────────────────────────────────────────┘

         ┌─────────────────┐
         │ Exception raised  │
         │ during execution  │
         └────────┬────────┘
                  │
        ┌────────┼────────┬────────┬────────┬────────┐
        ▼        ▼        ▼        ▼        ▼        ▼
   ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
   │Coder   ││MetaJson││MetaJson││Artifact││Preflight││General │
   │Invoke  ││Missing ││Invalid ││Missing ││Blocked  ││Exception│
   │Error   ││Error   ││Error   ││Error   ││Error    ││         │
   └───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘
       │         │         │         │         │         │
       └─────────┴─────────┴─────────┴─────────┴─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Classify        │
                    │ exception       │
                    │ _classify_      │
                    │ exception_v2()  │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ AUTO_RETRYABLE│ │HUMAN_RETRY_   │ │    FATAL      │
    │               │ │REQUIRED       │ │               │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │                 │                 │
            ▼                 ▼                 ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ Increment     │ │ Increment     │ │ Set status    │
    │ auto_retry_   │ │ human_retry_  │ │ FAILED        │
    │ count         │ │ count         │ │               │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │                 │                 │
            ▼                 ▼                 ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ Check retry   │ │ Check retry   │ │ Add to        │
    │ limit         │ │ limit         │ │ failed_steps  │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
       │Exceed              │Exceed             │
       │ed                  │ed                 │
       ▼                   ▼                  │
    ┌───────────┐      ┌───────────┐         │
    │ FAILED    │      │ WAITING_  │         │
    │ status    │      │ FOR_HUMAN │<────────┘
    └───────────┘      │ _INTERVENT│
                       │ ION       │
                       └───────────┘
```

### Control Classes

| Class | Description | Examples | Routing |
|-------|-------------|----------|---------|
| `AUTO_RETRYABLE` | Temporary failures that may succeed on retry | Network timeout, transient coder error | `WAITING_FOR_AUTO_RETRY` |
| `HUMAN_RETRY_REQUIRED` | Failures requiring human investigation | Invalid schema, missing required input | `WAITING_FOR_HUMAN_INTERVENTION` |
| `FATAL` | Unrecoverable failures | Code bug, corrupted state | `FAILED` |

### Failure Sources

| Source | Description |
|--------|-------------|
| `coder` | Exception from coder invocation |
| `runner` | Exception from runner validation/routing |
| `preflight` | Exception from pre-execution checks |
| `action` | Exception from deterministic action |

### Failure Envelope Structure

```json
{
  "failure_class": "AUTO_RETRYABLE|HUMAN_RETRY_REQUIRED|FATAL",
  "failure_code": "CODER_TIMEOUT|SCHEMA_INVALID|ARTIFACT_MISSING|...",
  "failure_reason": "Human-readable description",
  "failure_source": "coder|runner|preflight|action",
  "step": "step_name",
  "attempted_at": "2026-07-09T21:42:00+08:00"
}
```

---

## Documentation Sync Flow

The documentation sync workflow reconciles codebase changes with documentation.

### Documentation Sync Sequence

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           DOCUMENTATION SYNC FLOW                                      │
└────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │    Start    │
    │   40_doc_   │
    │   sync_v1   │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │ Scan codebase     │
    │ for changes       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Compare against   │
    │ inventory         │
    └────────┬────────┘
             │
        ┌────┴────┐
        │Changes?  │
        └────┬────┘
       Yes        │No
       ▼          ▼
┌──────────┐  ┌──────────┐
│ Generate │  │ Complete │
│ sync doc │  │ (no-op)  │
└────┬─────┘  └──────────┘
     │
     ▼
┌─────────────────┐
│ Review sync       │
│ recommendations   │
└────────┬────────┘
         │
    ┌────┴────┐
    │Approved?│
    └────┬────┘
   │Yes       │No
   ▼          ▼
┌──────────┐┌──────────┐
│ Apply    ││ Refine   │
│ changes  ││ sync     │
└────┬─────┘└────┬─────┘
     │           │
     │           └───────────────┐
     │                           │
     ▼                           ▼
┌─────────────────┐       ┌─────────────────┐
│ Update          │       │ Update review   │
│ inventory       │       │ file            │
└────────┬────────┘       └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Validate docs   │
│ (cross-ref)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │Valid?   │
    └────┬────┘
   │Yes       │No
   ▼          ▼
┌──────────┐┌──────────┐
│ Generate ││ Flag for │
│ arch docs││ human    │
│ (site)   ││ review   │
└────┬─────┘└──────────┘
     │
     ▼
┌─────────────────┐
│ Complete sync   │
└─────────────────┘
```

### Sync Steps

| Step | Purpose | Input | Output |
|------|---------|-------|--------|
| `01_sync_docs` | Scan and compare | Codebase, inventory | Sync recommendations |
| `02_review_docs` | Review changes | Sync recommendations | Approved/rejected |
| `03_refine_docs` | Refine if rejected | Review feedback | Updated recommendations |
| `04_validate_doc_sync` | Cross-reference | All docs | Validation report |

---

## Appendix: Module Responsibilities

| Module | File | Core Function |
|--------|------|---------------|
| Entry Point | `run_agent.py` | CLI parsing, job lifecycle, orchestration |
| Step Execution | `step_runner.py` | Prompt rendering, coder invocation, validation |
| Routing | `workflow_router.py` | Post-step routing, failure handling |
| Job State | `job_state.py` | job.json CRUD, state migration, reconciliation |
| Coder Adapters | `coder_adapters.py` | External coder invocation (Claude, Codex, Qwen) |
| Daemon | `daemon.py` | Child process supervision, backend polling |
| Backend Client | `backend_client.py` | HTTP API client for backend communication |
| Runtime Context | `runtime_context.py` | Global path/configuration context |
| Bundle Loader | `bundle_loader.py` | Workflow loading, bootstrap publishing |

---

## Appendix: State Machine Summary

```
                    ┌─────────────┐
                    │    NEW      │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ IN_PROGRESS │<──────────────────┐
                    └──────┬──────┘                   │
                           │                          │
        ┌──────────────────┼──────────────────┐        │
        │                  │                  │        │
        ▼                  ▼                  ▼        │
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ │
│WAITING_FOR_   │ │WAITING_FOR_   │ │WAITING_FOR_   │ │
│HUMAN_APPROVAL │ │AUTO_RETRY     │ │HUMAN_INTERVENT│─┘
└───────────────┘ └───────────────┘ └───────────────┘
        │                  │                  │
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  COMPLETED    │ │    FAILED     │ │    FAILED     │
│               │ │  (retryable)  │ │   (terminal)  │
└───────────────┘ └───────────────┘ └───────────────┘
```
