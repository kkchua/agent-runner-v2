# Workflow Execution Flow — Complete System Overview

**Date:** 2026-08-18  
**Version:** V2 Architecture  
**Status:** Production

---

## Overview

The system uses a **3-party handshake** between **Operator Console**, **Backend API**, and **Local Daemon + CLI** to execute workflows. The Backend owns the state machine; the Daemon and CLI are stateless executors.

---

## Architecture Components

| Component | Location | Role |
|-----------|----------|------|
| **Backend API** | `agent-runner-backend-v2/` | State machine, persistence, routing decisions |
| **Operator Console** | `operator-console-v2/` | Web UI for job submission and monitoring |
| **Local Daemon** | `agent_runner_v2/daemon_v2.py` | Polls backend, spawns CLI children |
| **CLI Runner** | `agent_runner_v2/run_agent.py` | Executes workflow steps, writes outcomes |
| **Queue Folder** | `~/.ukbe-runner/queue/` | File-based handoff between CLI and Daemon |

---

## Step-by-Step Execution Flow

### Phase 1: Job Submission (Operator Console → Backend)

1. **User submits job** via Operator Console (`SubmitPage.tsx`)
   - Selects: worker, repo, workflow, implementation, step slots
   - Provides input artifacts (files or text values)

2. **Console calls Backend API:**
   ```http
   POST /api/runs
   {
     "workflow_name": "...",
     "worker_id": "...",
     "project_root": "...",
     "implementation_name": "...",
     "prompt_selections": {...},
     "input_payload": {...}
   }
   ```

3. **Backend creates run record:**
   - `run_status = "USER_SUBMITTED"`
   - `current_step_name = workflow.init_step`
   - Stores context payload (implementation, prompt selections)

---

### Phase 2: Work Claiming (Daemon ↔ Backend)

4. **Daemon polls backend** (every few seconds):
   ```http
   POST /api/workers/{worker_id}/claim
   ```

5. **Backend `claim_work()` logic:**
   - Check worker's `max_parallel` limit
   - First: Check for action-pending runs (`USER_APPROVED`, `USER_REJECTED`, `USER_RESUMED`, `USER_RETRIED`)
   - Second: Check for claimable runs (`PENDING`, `USER_SUBMITTED`)
   - Transition run to `RUNNING`
   - Create step_run record
   - Return work payload

6. **Claim response types:**
   - `work_type = "IDLE"` — nothing to do
   - `work_type = "PROCESS_ACTION"` — daemon processes user action directly
   - `work_type = "EXECUTE_STEP"` — daemon spawns CLI child

---

### Phase 3: Child Spawning (Daemon → CLI)

7. **Daemon spawns CLI subprocess** (`_spawn_child()`):
   ```bash
   python -m agent_runner_v2.run_agent run \
     --project-root {project_root} \
     --template-group {workflow_name} \
     --mode daemon \
     --job-id {run_code} \
     --job-no {run_code} \
     --job {step_name} \
     --impl-name {implementation_name}
   ```

8. **Environment variables passed:**
   - `AGENT_RUNNER_WORKFLOW_RUN_ID`
   - `AGENT_RUNNER_WORKFLOW_STEP_RUN_ID`
   - `AGENT_RUNNER_JOB_DIR` — for job state persistence
   - `AGENT_RUNNER_QUEUE_DIR` — for outcome handoff
   - `AGENT_RUNNER_BACKEND_STATE_FILE` — pre-fetched backend state

---

### Phase 4: Step Execution (CLI internal)

9. **CLI execution flow** (`run_agent.py`):
   - Load backend state from `AGENT_RUNNER_BACKEND_STATE_FILE`
   - Load or create local `job.json`
   - Execute the step via `step_runner.run_step()`:
     - **Action steps**: Call Python function directly
     - **Prompt steps**: Invoke AI Coder (opencode/qwen CLI)
   - Write output artifacts to disk

10. **CLI writes outcome to queue** (`_write_result_to_queue()`):
    ```json
    {
      "step_run_id": "...",
      "run_id": "...",
      "run_code": "...",
      "step_name": "...",
      "outcome": "approved|rejected|failed",
      "failure_class": null|"AUTO_RETRYABLE"|"HUMAN_RETRY_REQUIRED"|"FATAL",
      "artifacts": {...},
      "review": {...},
      "exit_code": 0,
      "timestamp": "ISO-8601"
    }
    ```
    Written to: `~/.ukbe-runner/queue/{YYYYMMDD}/{workflow}/{run_code}/{step_run_id}.json`

---

### Phase 5: Outcome Reporting (Daemon → Backend)

11. **Daemon scans queue folder** (`_process_queue()`):
    - Finds pending outcome files
    - Reads and parses JSON

12. **Daemon reports to backend:**
    ```http
    POST /api/runs/step-runs/{step_run_id}/outcome
    {
      "outcome": "approved",
      "failure_class": null,
      "artifacts": {...},
      ...
    }
    ```

13. **Backend `report_outcome()` logic:**
    - Update step_run record with outcome
    - **State machine computes next state:**
      - Approved → next step from `onsuccess`
      - Rejected → check `on_reject_refine` for retry loop
      - Failed → check `on_exhaust_replan` or go to `AWAITING_INTERVENTION`
    - Create next step_run if needed
    - Update run status (`PENDING`, `WAITING_FOR_HUMAN_APPROVAL`, `COMPLETED`, etc.)

14. **Daemon archives processed outcome:**
    - Moves file to `queue/{...}/archive/`

---

### Phase 6: Continuation

15. **Daemon loops back** to claim next work
    - If run has more steps: Claims next step (now `PENDING`)
    - If run complete: Status is `COMPLETED`, no more claims

---

## State Machine Diagram

```
USER_SUBMITTED ──┐
USER_APPROVED ───┤
USER_REJECTED ───┤
USER_RESUMED ────┤
USER_RETRIED ────┤
                 ▼
             RUNNING ──(daemon spawns CLI)──► CLI executes step
                 ▲                              │
                 │                              ▼
                 │                         Queue file written
                 │                              │
                 │                              ▼
                 │                    Daemon reports outcome
                 │                              │
                 │                              ▼
                 └──────────┬───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   (approved)          (rejected)          (failed)
        │                   │                   │
        ▼                   ▼                   ▼
   onsuccess          on_reject_refine    AWAITING_INTERVENTION
        │                   │              (or exhausted)
        │                   │
        │                   ▼
        │              retry loop (max 3)
        │
        ▼
   next step
        │
   (no more steps)
        │
        ▼
   COMPLETED/FAILED
```

---

## Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Backend-authoritative state** | All routing decisions made by backend |
| **File-based handoff** | Queue folder between CLI and Daemon |
| **Stateless CLI** | CLI reads state from env, writes outcome to queue |
| **Pre-execution sync** | Daemon fetches backend state before spawning |
| **Idempotent claims** | Backend commits before responding to claim |
| **Atomic queue writes** | Temp file → rename pattern |

---

## File Locations Summary

| File | Purpose |
|------|---------|
| `~/.ukbe-runner/jobs/{date}/{workflow}/{run_code}/job.json` | Local job state |
| `~/.ukbe-runner/queue/{date}/{workflow}/{run_code}/{step_run_id}.json` | Outcome handoff |
| `~/.ukbe-runner/runs/{child_dir}/backend_state.json` | Pre-fetched backend state |
| `~/.ukbe-runner/runs/{child_dir}/child.log` | Child process logs |
| Backend PostgreSQL | Run, step_run, workflow_definition tables |

---

## API Endpoints Reference

### Worker Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/workers/register` | POST | Register new worker |
| `/api/workers/{worker_id}` | GET | Get worker details |
| `/api/workers/{worker_id}/heartbeat` | POST | Heartbeat + command polling |
| `/api/workers/{worker_id}/claim` | POST | Claim next work item |

### Run Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/runs` | POST | Submit new run |
| `/api/runs` | GET | List runs |
| `/api/runs/{run_id}` | GET | Get run details |
| `/api/runs/{run_id}/action` | POST | Request action (approve/reject/resume/retry/cancel) |
| `/api/runs/step-runs/{step_run_id}/outcome` | POST | Report step outcome |

---

## Related Documentation

- [BASE_COMPOSITION_STANDARD_v2.0.md](../system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v2.0.md) — Workflow package structure
- [daemon_v2.py](../../agent_runner_v2/daemon_v2.py) — Daemon implementation
- [run_agent.py](../../agent_runner_v2/run_agent.py) — CLI implementation
- [v2/backend_client.py](../../agent_runner_v2/v2/backend_client.py) — Backend API client
- [v2/queue.py](../../agent_runner_v2/v2/queue.py) — Queue file operations
