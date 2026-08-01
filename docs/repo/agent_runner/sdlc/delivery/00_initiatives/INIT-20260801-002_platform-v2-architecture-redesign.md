---
title: "Platform V2 — Architecture Redesign"
version: "1.0.0"
doc_type: "architecture_spec"
status: "draft"
created: "2026-08-01"
author: "operator"
scope: "agent-runner-backend-v2, agent-runner-v2 daemon, CLI, console"
---

# Platform V2 — Architecture Redesign

## 1. Executive Summary

Redesign the agent-runner platform to replace the current "CLI-as-brain, backend-as-dumb-store" architecture with a **backend-authoritative state machine** model. The new backend owns all state transitions, the daemon becomes a thin claim-execute-report worker, the CLI becomes a pure execution engine, and the console becomes a React web app calling the backend API directly.

### Goals

1. **Clear state machine** — two-field model (`run_status` + `action_requested`) replaces overloaded single-status + buried-flags
2. **Backend-authoritative routing** — backend computes next state from (current_status, outcome, workflow_rules)
3. **Direct console-to-API** — React web app replaces Flet console, no CLI intermediary
4. **Simplified daemon** — single claim loop replaces dual polling loops, no flag clearing, no safety-net hacks
5. **Clean migration** — new backend in separate repo, old system runs unchanged until cutover

### Non-Goals

- Rewriting the execution engine (step_runner, coder_adapters, action modules) — these stay unchanged
- Changing workflow TOML format — existing workflow definitions remain valid
- Changing local job.json schema during initial migration — simplified in a follow-up

---

## 2. Current Architecture Problems

### 2.1 Status Overloading

The single `run_status` field serves three purposes simultaneously:

| Purpose | Example | Conflict |
|---|---|---|
| Current state | "awaiting_human" | Console can't distinguish approval vs intervention vs max-retried |
| Scheduling signal | "pending" means both "new work" and "auto-retry" | Daemon can't differentiate |
| Implicit outcome | "completed" means both "all done" and "daemon quit" | Ambiguous terminal cause |

**Status mapping (current):**

```
IN_PROGRESS              → "pending"
WAITING_FOR_AUTO_RETRY   → "pending"          ← same as above
WAITING_FOR_HUMAN_APPROVAL    → "awaiting_human"
WAITING_FOR_HUMAN_INTERVENTION → "awaiting_human"  ← collapsed
WAITING_FOR_HUMAN_MAXRETRIED   → "awaiting_human"  ← collapsed
COMPLETED                → "completed"
FAILED                   → "failed"
STOPPED                  → "stopped"          ← not in mapping, falls through to "pending"
```

### 2.2 Action Requests Buried in Nested JSON

Operator actions (approve, reject, resume, retry, cancel) are stored as boolean flags inside `context_payload.__run_control`:

```python
context_payload.__run_control = {
    "approve_requested": True,
    "action_step": "review_code",
    "feedback": "looks good",
}
```

Problems:
- Not a first-class DB field → can't query, can't enforce schema constraints
- Daemon must parse nested JSON to detect requests
- No protection against conflicting requests (approve + cancel simultaneously)
- Flags cleared by daemon after consumption — if sync fails, flags replay
- Console can't distinguish "waiting for human" from "action pending, being processed"

### 2.3 No "Running" Visibility

When the daemon claims a run and starts executing, `run_status` stays `"pending"` until the CLI syncs results. The console user cannot tell if a submitted run has been picked up.

### 2.4 Dual Polling Loops in Daemon

The daemon interleaves two polling loops in a single function:
1. **Claim loop** — `claim_step()` for executable work
2. **Approval poll** — `list_runs()` + `_get_approval_request()` for human actions

This creates complex control flow, shared state between loops, and makes the daemon hard to reason about.

### 2.5 Safety Net Hacks

`terminal_run_ids` — an in-memory set tracking runs that already failed — exists because the backend may re-serve failed runs. This is a workaround for the backend not enforcing terminal status properly.

### 2.6 step_status Triple Duty

`step_status` is used for step lifecycle (`completed`, `failed`, `cancelled`), result quality (`approved`, `rejected`), AND action labels (`approve`, `reject`, `resume`, `retry`).

---

## 3. New Architecture Overview

### 3.1 Component Roles

```
┌──────────┐         ┌──────────────────┐         ┌──────────┐
│  Console │──REST──▶│  Backend V2      │◀──REST──│  Daemon  │
│ (React)  │         │  (State Machine) │         │  (Worker)│
│          │         │                  │         └────┬─────┘
│ Read     │         │  • run_status    │              │
│ status   │         │  • action_req    │              │ spawns
│ Request  │         │  • workflow defs │              │
│ actions  │         │  • routing rules │              ▼
│          │         │  • validation    │         ┌──────────┐
└──────────┘         └──────────────────┘         │  CLI     │
                                                  │(Execute) │
                                                  └──────────┘
```

| Component | Role | Authority |
|---|---|---|
| **Backend V2** | State machine + persistence | run_status, action_requested, routing, validation |
| **Daemon** | Thin worker loop | Nothing — claims work, executes via CLI, reports outcome |
| **CLI** | Execution engine + outcome classification | Step execution, coder invocation, failure classification |
| **Console** | Operator UI | User intent only (which action, which run) |

### 3.2 Two-Field State Model

Every run in the backend has exactly two state fields:

| Field | Purpose | Set by | Read by |
|---|---|---|---|
| `run_status` | "Where is this run right now?" | Backend (after each transition) | Console (display), Daemon (claim filter), Backend (validation) |
| `action_requested` | "What did the operator ask for?" | Console (via API), Backend (validation) | Daemon (claim), Backend (claim routing) |

These fields are **orthogonal**: `run_status` describes the run's position in its lifecycle, `action_requested` describes a pending operator command. They are never conflated.

### 3.3 Three CLI Layers

The CLI has three internal layers. Only Layer 3 changes:

| Layer | Contents | Change |
|---|---|---|
| **L1: Execution Engine** | step_runner, coder_adapters, prompt rendering, actions, artifact collection | **UNCHANGED** |
| **L2: Outcome Classification** | `_classify_failure()` → AUTO_RETRYABLE / HUMAN_RETRY_REQUIRED / FATAL | **Minor changes** — stays in CLI |
| **L3: State Machine / Routing** | route_after_step, route_after_failure, set_job_status, advance_to_next_step, approve/reject/resume/retry handlers | **REMOVED** — moves to backend |

---

## 4. State Machine Specification

### 4.1 run_status Values (8 states)

| Status | Meaning | Terminal? | Daemon behavior |
|---|---|---|---|
| `SUBMITTED` | Run created, first step not yet claimed | No | Claim → set RUNNING |
| `PENDING` | Step ready to execute (next step queued, or auto-retry) | No | Claim → set RUNNING |
| `RUNNING` | Daemon actively executing a step | No | Don't re-claim |
| `AWAITING_APPROVAL` | Review gate — step completed, needs human sign-off | No | Wait for action |
| `AWAITING_INTERVENTION` | Error — needs human investigation | No | Wait for action |
| `AWAITING_MAXRETRIED` | Refine+replan budget exhausted | No | Wait for action |
| `COMPLETED` | All steps finished successfully | Yes | N/A |
| `FAILED` | Unrecoverable failure or cancelled | Yes | N/A |

### 4.2 action_requested Values (nullable)

| Value | Set by | Effect |
|---|---|---|
| `null` | — | No pending action |
| `APPROVE` | Console | Daemon spawns CLI with `--approve-step` |
| `REJECT` | Console | Daemon spawns CLI with `--reject-step` |
| `RESUME` | Console | Daemon spawns CLI with `--resume-step` |
| `RETRY` | Console | Daemon spawns CLI with `--retry-step` |
| `CANCEL` | Console | Daemon stops execution, backend sets FAILED |

### 4.3 State Transition Rules

#### 4.3.1 Normal Flow (Step Execution)

```
SUBMITTED ──[daemon claim]──▶ RUNNING
PENDING   ──[daemon claim]──▶ RUNNING

RUNNING ──[step approved, has next]──▶ PENDING       (next_step set)
RUNNING ──[step approved, no next]───▶ COMPLETED
RUNNING ──[review gate]──────────────▶ AWAITING_APPROVAL
RUNNING ──[auto_retryable fail]──────▶ PENDING       (same step, auto-retry)
RUNNING ──[human_retry fail]─────────▶ AWAITING_INTERVENTION
RUNNING ──[fatal fail]───────────────▶ FAILED
RUNNING ──[max_rejects exceeded]─────▶ FAILED
```

#### 4.3.2 Human Action Flow

```
AWAITING_APPROVAL ──[APPROVE]──▶ PENDING     (next step) or COMPLETED
AWAITING_APPROVAL ──[REJECT]───▶ RUNNING     (refine loop) or PENDING
AWAITING_APPROVAL ──[CANCEL]───▶ FAILED

AWAITING_INTERVENTION ──[RESUME]──▶ PENDING  (next step) or COMPLETED
AWAITING_INTERVENTION ──[RETRY]───▶ RUNNING  (same step, fresh attempt)
AWAITING_INTERVENTION ──[CANCEL]──▶ FAILED

AWAITING_MAXRETRIED ──[RESUME]──▶ PENDING    (next step) or COMPLETED
AWAITING_MAXRETRIED ──[RETRY]───▶ RUNNING    (same step, fresh attempts)
AWAITING_MAXRETRIED ──[CANCEL]──▶ FAILED
```

#### 4.3.3 Cancel Flow

```
SUBMITTED ──[CANCEL]──▶ FAILED
PENDING   ──[CANCEL]──▶ FAILED
RUNNING   ──[CANCEL]──▶ FAILED   (after daemon stops current step)
```

#### 4.3.4 Refine/Replan Flow (Backend evaluates workflow rules)

```
RUNNING ──[rejected, refine available, iterations left]──▶ RUNNING
    (backend sets same step, refine prompt; daemon re-claims immediately)

RUNNING ──[rejected, refine exhausted, replan available]──▶ RUNNING
    (backend sets replan step; daemon re-claims)

RUNNING ──[rejected, all exhausted]──▶ AWAITING_MAXRETRIED
```

### 4.4 Valid Actions per Status

The backend enforces these rules. The console uses them to enable/disable UI buttons.

| run_status | Valid actions | Invalid actions (rejected by backend) |
|---|---|---|
| `SUBMITTED` | CANCEL | APPROVE, REJECT, RESUME, RETRY |
| `PENDING` | CANCEL | APPROVE, REJECT, RESUME, RETRY |
| `RUNNING` | CANCEL | APPROVE, REJECT, RESUME, RETRY |
| `AWAITING_APPROVAL` | APPROVE, REJECT, CANCEL | RESUME, RETRY |
| `AWAITING_INTERVENTION` | RESUME, RETRY, CANCEL | APPROVE, REJECT |
| `AWAITING_MAXRETRIED` | RESUME, RETRY, CANCEL | APPROVE, REJECT |
| `COMPLETED` | _(none)_ | All |
| `FAILED` | _(none)_ | All |

### 4.5 Invariants

1. **Single action**: `action_requested` can only be set when `run_status` is non-terminal AND `action_requested` is currently `null`. Backend rejects if an action is already pending.

2. **Atomic consumption**: When the daemon claims work triggered by `action_requested`, the backend atomically sets `action_requested = null` in the same transaction. No replay possible.

3. **Terminal is terminal**: Once `run_status` is `COMPLETED` or `FAILED`, no transitions are possible. No status changes, no actions.

4. **RUNNING exclusivity**: Only one daemon can hold a run in `RUNNING` state. The backend sets `RUNNING` atomically on claim. If a daemon crashes, the backend detects heartbeat loss and transitions to `FAILED` (or `AWAITING_INTERVENTION` based on policy).

5. **Claim filter**: Backend only serves runs where `run_status IN (SUBMITTED, PENDING)` AND `action_requested IS NULL` for EXECUTE_STEP work. For PROCESS_ACTION work, backend serves runs where `action_requested IS NOT NULL`.

### 4.6 step_status and step_outcome (Split)

The current triple-purpose `step_status` is split into two fields:

| Field | Values | Purpose |
|---|---|---|
| `step_status` | `pending`, `running`, `completed`, `failed`, `cancelled` | Step lifecycle only |
| `step_outcome` | `approved`, `rejected`, `auto_retried`, `cancelled`, `skipped`, `completed` | What the result was |

---

## 5. API Contract

### 5.1 Run Management (Console → Backend)

#### Submit Run

```
POST /api/runs
{
    "workflow_name": "agnes_media_gen_v1",
    "worker_id": "worker-1",
    "project_root": "/path/to/project",
    "inputs": { "CONCEPT_FILE": "/path/to/concept.md" },
    "start_step": null               // optional override
}

Response 201:
{
    "run_id": "uuid",
    "run_code": "JOB-001",
    "run_status": "SUBMITTED",
    "action_requested": null,
    "current_step": "generate_descriptions",
    "created_at": "2026-08-01T10:00:00Z"
}
```

#### Request Action

```
POST /api/runs/{run_id}/action
{
    "action": "APPROVE",             // APPROVE | REJECT | RESUME | RETRY | CANCEL
    "feedback": "looks good"         // optional
}

Response 200:
{
    "run_id": "uuid",
    "run_status": "AWAITING_APPROVAL",
    "action_requested": "APPROVE",
    "message": "Action recorded"
}

Response 409 (conflict):
{
    "error": "action_already_pending",
    "current_action": "CANCEL",
    "message": "Run already has a pending CANCEL action"
}

Response 422 (invalid):
{
    "error": "invalid_action_for_status",
    "run_status": "RUNNING",
    "requested_action": "APPROVE",
    "message": "APPROVE is not valid when run_status is RUNNING"
}
```

#### List Runs

```
GET /api/runs?status=active&worker_id=worker-1&workflow_name=...

Query params:
  status: active | terminal | all     (replaces status_group)
  worker_id: optional filter
  workflow_name: optional filter

Response 200:
{
    "runs": [
        {
            "run_id": "uuid",
            "run_code": "JOB-001",
            "workflow_name": "agnes_media_gen_v1",
            "run_status": "AWAITING_APPROVAL",
            "action_requested": null,
            "current_step": "review_prompts",
            "worker_id": "worker-1",
            "updated_at": "2026-08-01T10:30:00Z"
        }
    ]
}
```

#### Get Run Detail

```
GET /api/runs/{run_id}

Response 200:
{
    "run_id": "uuid",
    "run_code": "JOB-001",
    "workflow_name": "agnes_media_gen_v1",
    "run_status": "AWAITING_APPROVAL",
    "action_requested": null,
    "current_step": "review_prompts",
    "current_step_run_id": "step-uuid",
    "worker_id": "worker-1",
    "created_at": "2026-08-01T10:00:00Z",
    "updated_at": "2026-08-01T10:30:00Z",
    "completed_steps": ["generate_descriptions", "generate_prompts"],
    "failed_steps": [],
    "artifacts": { ... },
    "review_state": { ... },
    "valid_actions": ["APPROVE", "REJECT", "CANCEL"]
}
```

Note: `valid_actions` is computed by the backend based on `run_status`. The console uses this to enable/disable buttons — no client-side status logic needed.

#### Reset Step

```
POST /api/runs/{run_id}/reset-step
{
    "step_name": "generate_prompts"
}

Response 200:
{
    "run_id": "uuid",
    "run_status": "PENDING",
    "current_step": "generate_prompts"
}
```

### 5.2 Worker Protocol (Daemon → Backend)

#### Register Worker

```
POST /api/workers/register
{
    "worker_id": "worker-1",
    "label": "live",
    "capabilities": ["execute", "approve"]
}

Response 201:
{
    "worker_id": "worker-1",
    "registered_at": "2026-08-01T10:00:00Z"
}
```

#### Heartbeat

```
POST /api/workers/{worker_id}/heartbeat
{
    "status": "idle",                // idle | busy
    "current_run_id": null,          // set when busy
    "current_step": null             // set when busy
}

Response 200:
{
    "commands": []                   // ["shutdown"] if admin requested
}
```

#### Claim Work

```
POST /api/workers/{worker_id}/claim

Response 200 (execute step):
{
    "work_type": "EXECUTE_STEP",
    "run": {
        "run_id": "uuid",
        "run_code": "JOB-001",
        "workflow_name": "agnes_media_gen_v1",
        "project_root": "/path/to/project"
    },
    "step_run": {
        "step_run_id": "step-uuid",
        "step_name": "generate_images"
    },
    "execution_spec": {
        "coder": "opencode",
        "role_policy": "architect_standard",
        "step_timeout_seconds": 3600,
        ...
    }
}

Response 200 (process action):
{
    "work_type": "PROCESS_ACTION",
    "run": {
        "run_id": "uuid",
        "run_code": "JOB-001",
        "workflow_name": "agnes_media_gen_v1",
        "project_root": "/path/to/project"
    },
    "step_run": {
        "step_run_id": "step-uuid",
        "step_name": "review_prompts"
    },
    "action": "APPROVE",
    "feedback": "looks good",
    "execution_spec": { ... }
}

Response 200 (no work):
{
    "work_type": "IDLE"
}
```

The backend atomically transitions `run_status` to `RUNNING` when serving EXECUTE_STEP work. For PROCESS_ACTION, `action_requested` is atomically set to `null`.

#### Report Outcome

```
POST /api/step-runs/{step_run_id}/outcome
{
    "outcome": "rejected",
    "failure_class": "AUTO_RETRYABLE",    // null | AUTO_RETRYABLE | HUMAN_RETRY_REQUIRED | FATAL
    "error_message": "API rate limit exceeded",
    "artifacts": {
        "REVIEW_FILE_SUGGESTED": "/path/to/review.md"
    },
    "review": {
        "decision": "REJECTED",
        "remark": "Missing device fidelity requirements",
        "findings": [...]
    },
    "usage_summary": {
        "input_tokens": 5000,
        "output_tokens": 2000
    }
}

Response 200 (backend computed next state):
{
    "run_id": "uuid",
    "run_status": "PENDING",              // backend decided: auto-retry
    "current_step": "generate_images",    // same step (retry)
    "action_requested": null,
    "message": "Auto-retry: step will be re-executed"
}
```

This is the key endpoint. The CLI reports **what happened**, the backend decides **what happens next**.

### 5.3 Workflow Management

#### Sync Workflow Definition

```
POST /api/workflows/sync
{
    "workflow_name": "agnes_media_gen_v1",
    "version": "1.0.0",
    "steps": {
        "generate_descriptions": {
            "prompt": "01_generate_descriptions.txt",
            "coder": { "role_policy": "architect_standard" },
            "artifacts": {
                "produces": ["IMAGE_DESCRIPTIONS"],
                "required_inputs": ["CONCEPT_FILE"]
            },
            "onsuccess": "generate_prompts"
        },
        "generate_prompts": {
            "prompt": "02_generate_prompts.txt",
            "coder": { "role_policy": "architect_standard" },
            "artifacts": {
                "produces": ["PROMPT_VARIANTS"],
                "required_inputs": ["IMAGE_DESCRIPTIONS"]
            },
            "requires_human_approval_after": true,
            "onsuccess": "generate_images",
            "on_reject_refine": {
                "refine_step": "refine_prompts",
                "max_iterations": 3
            }
        },
        ...
    },
    "default_max_rejects": 3,
    "init_step": "generate_descriptions"
}

Response 200:
{
    "workflow_name": "agnes_media_gen_v1",
    "synced_at": "2026-08-01T10:00:00Z",
    "status": "updated"
}
```

### 5.4 Worker Administration (Console → Backend)

```
POST /api/workers/{worker_id}/stop       # Graceful shutdown
POST /api/workers/{worker_id}/restart    # Restart daemon

GET  /api/workers                        # List registered workers
GET  /api/workers/{worker_id}            # Worker detail + health
```

---

## 6. Backend State Machine Engine

### 6.1 Core Function

The state machine engine is the heart of the new backend. Every state mutation goes through it.

```python
def transition(
    run: Run,
    event: TransitionEvent,
    workflow: WorkflowDefinition,
) -> TransitionResult:
    """
    Compute the next state given (current_state, event, workflow_rules).
    
    This is the ONLY function that changes run_status or action_requested.
    All API endpoints call this function.
    """
```

### 6.2 Transition Events

| Event | Source | Inputs |
|---|---|---|
| `STEP_CLAIMED` | Daemon claim | — |
| `STEP_OUTCOME` | CLI report | outcome, failure_class, artifacts, review |
| `ACTION_REQUESTED` | Console | action (APPROVE/REJECT/RESUME/RETRY/CANCEL) |
| `ACTION_CONSUMED` | Daemon claim | — |
| `STEP_RESET` | Console | target_step |
| `WORKER_TIMEOUT` | Backend watchdog | — |

### 6.3 Routing Logic (Pseudocode)

```python
def handle_step_outcome(run, event, workflow):
    step = workflow.steps[run.current_step]
    
    if event.outcome == "approved":
        if step.requires_human_approval_after:
            return TransitionResult(
                run_status="AWAITING_APPROVAL",
                action_requested=None,
            )
        next_step = workflow.next_step(run.current_step)
        if next_step:
            return TransitionResult(
                run_status="PENDING",
                current_step=next_step,
            )
        return TransitionResult(run_status="COMPLETED")
    
    if event.outcome == "rejected":
        # Check refine loop
        if step.on_reject_refine:
            iterations = run.refine_iterations.get(run.current_step, 0)
            if iterations < step.on_reject_refine.max_iterations:
                return TransitionResult(
                    run_status="PENDING",  # or RUNNING for immediate re-claim
                    current_step=step.on_reject_refine.refine_step,
                    refine_iterations={**run.refine_iterations, 
                                       run.current_step: iterations + 1},
                )
            # Refine exhausted — check replan
            if step.on_exhaust_replan:
                return TransitionResult(
                    run_status="PENDING",
                    current_step=step.on_exhaust_replan.replan_step,
                )
            # All exhausted
            return TransitionResult(run_status="AWAITING_MAXRETRIED")
        
        # No refine loop — classify failure
        if event.failure_class == "AUTO_RETRYABLE":
            return TransitionResult(
                run_status="PENDING",
                current_step=run.current_step,  # retry same step
            )
        if event.failure_class == "HUMAN_RETRY_REQUIRED":
            return TransitionResult(run_status="AWAITING_INTERVENTION")
        if event.failure_class == "FATAL":
            return TransitionResult(run_status="FAILED")
    
    if event.outcome == "failed":
        return TransitionResult(run_status="FAILED")
```

### 6.4 Action Handling Logic

```python
def handle_action_requested(run, event, workflow):
    action = event.action
    
    # Validate action against current status
    valid = VALID_ACTIONS.get(run.run_status, set())
    if action not in valid:
        raise ConflictError(f"{action} not valid for status {run.run_status}")
    
    # Check no existing pending action
    if run.action_requested is not None:
        raise ConflictError(f"Action {run.action_requested} already pending")
    
    if action == "CANCEL":
        return TransitionResult(run_status="FAILED")
    
    # For APPROVE/REJECT/RESUME/RETRY: set action_requested, daemon will process
    return TransitionResult(
        run_status=run.run_status,  # status unchanged until daemon processes
        action_requested=action,
    )

def handle_action_consumed(run, event, workflow):
    """Daemon has processed the action. Compute next state."""
    action = run.action_requested
    step = workflow.steps[run.current_step]
    
    if action == "APPROVE":
        next_step = workflow.next_step(run.current_step)
        if next_step:
            return TransitionResult(run_status="PENDING", current_step=next_step,
                                    action_requested=None)
        return TransitionResult(run_status="COMPLETED", action_requested=None)
    
    if action == "REJECT":
        # Trigger refine loop (same logic as rejected outcome)
        ...
    
    if action == "RESUME":
        # Force-approve, advance to next step
        next_step = workflow.next_step(run.current_step)
        if next_step:
            return TransitionResult(run_status="PENDING", current_step=next_step,
                                    action_requested=None)
        return TransitionResult(run_status="COMPLETED", action_requested=None)
    
    if action == "RETRY":
        # Reset counts, re-execute same step
        return TransitionResult(run_status="PENDING", current_step=run.current_step,
                                action_requested=None, reset_counts=True)
```

---

## 7. Daemon Redesign

### 7.1 Current vs New

| Aspect | Current | New |
|---|---|---|
| Code size | ~1600 lines (daemon.py + daemon_runtime.py) | ~400-500 lines |
| Polling loops | 2 (claim + approval) interleaved | 1 (claim serves all work types) |
| Child states | 5 (spawned, running, stalled, timed_out, killed) | 2 (running, done) |
| Pre-spawn checks | 3 (stop, quit, terminal_run_ids) | 0 (backend filters) |
| Flag clearing | Daemon clears __run_control flags | Backend atomically consumes action_requested |
| Safety nets | terminal_run_ids in-memory set | None needed |
| Timeout | Daemon watchdog + stall detection | Backend monitors heartbeat; daemon uses step_timeout from execution_spec |
| Quit mechanism | __run_control.quit_daemon flag | Backend heartbeat response: `commands: ["shutdown"]` |

### 7.2 New Daemon Loop

```python
def run_daemon(config):
    backend = BackendClient(config.backend_url)
    backend.register_worker(config.worker_id)
    
    children = {}
    running = True
    
    while running:
        # 1. Heartbeat
        hb_response = backend.heartbeat(config.worker_id, status="idle" if not children else "busy")
        if "shutdown" in hb_response.get("commands", []):
            running = False
            break
        
        # 2. Claim work (single endpoint, all types)
        if len(children) < config.max_parallel:
            work = backend.claim(config.worker_id)
            
            if work["work_type"] == "IDLE":
                time.sleep(config.poll_seconds)
                continue
            
            # 3. Spawn CLI
            child = spawn_cli(work, config)
            children[child.step_run_id] = child
        
        # 4. Check completed children
        for step_run_id, child in list(children.items()):
            if child.is_done():
                result = child.load_result()
                
                # 5. Report outcome (backend computes next state)
                backend.report_outcome(
                    step_run_id=step_run_id,
                    outcome=result.outcome,
                    failure_class=result.failure_class,
                    artifacts=result.artifacts,
                    review=result.review,
                    usage=result.usage_summary,
                )
                del children[step_run_id]
        
        time.sleep(config.poll_seconds)
    
    # Graceful shutdown
    backend.unregister_worker(config.worker_id)
```

### 7.3 CLI Spawn Command

The daemon spawns CLI with a unified interface:

```bash
# Execute a step
python -m agent_runner_v2.run_agent run \
    --mode daemon \
    --template-group <workflow> \
    --job-id <job_id> \
    --job-no <job_no> \
    --job-dir <path>

# Process a human action
python -m agent_runner_v2.run_agent run \
    --mode daemon \
    --template-group <workflow> \
    --job-id <job_id> \
    --approve-step <step>          # or --reject-step, --resume-step, --retry-step
    --feedback "..."
```

### 7.4 Crash Recovery

| Scenario | Detection | Recovery |
|---|---|---|
| CLI child crashes | `child.is_done()` returns True with error | Daemon reports `outcome=failed` |
| Daemon crashes mid-step | Backend heartbeat timeout | Backend transitions run to FAILED or AWAITING_INTERVENTION |
| Daemon crashes mid-sync | No outcome recorded | Backend run stays in previous status; daemon re-claims on restart |
| Backend crashes | Claim returns error | Daemon sleeps and retries on next poll |
| Network partition | Heartbeat failures | Daemon continues; backend detects timeout |

---

## 8. CLI Changes

### 8.1 What Stays (Layer 1 — Execution Engine)

These modules are unchanged:

| Module | Role |
|---|---|
| `step_runner.py` | Render prompt, invoke coder, collect meta.json |
| `coder_adapters.py` | Invoke opencode, claude, qwen, codex, local |
| `coder_registry.py` | Coder role → policy resolution |
| `bundle_loader.py` | Workflow package loading |
| `workflow_packages/` | TOML parsing, StepConfig, WorkflowBundle |
| `actions/` | All 30 action modules |
| `notification_manager.py` | Pushover + console notifications |
| Prompt rendering | Artifact placeholder resolution, context building |
| `execution_core.py` | execute_routed_step, invoke_prepared_step |

### 8.2 What Simplifies (Layer 2 — Classification)

| Module | Current | New |
|---|---|---|
| `_classify_failure()` in `workflow_router.py` | Classification + routing combined | Extract classification only |
| Failure classes | AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, FATAL | **Same values** — backend needs these |

### 8.3 What Goes Away (Layer 3 — State Machine)

| Removed | Replaced by |
|---|---|
| `route_after_step()` | Backend `transition()` on STEP_OUTCOME event |
| `route_after_failure()` | Backend `transition()` on STEP_OUTCOME event |
| `set_job_status()` | Backend owns run_status |
| `advance_to_next_step()` | Backend computes next step |
| `approve_step()`, `reject_step()`, `resume_step()`, `retry_step()` | Backend handles action consumption |
| `_map_job_status_to_run_status()` | Backend uses its own status values |
| `build_job_sync_payload()` complex routing fields | Simplified to outcome + artifacts only |
| `__run_control` flag mechanism | `action_requested` first-class field |
| `approve_commands.py` flag setting | Console calls `POST /api/runs/{id}/action` |
| `stop_commands.py` flag setting | Console calls `POST /api/runs/{id}/action` with CANCEL |

### 8.4 New CLI Sync Payload

```python
# OLD: CLI decides everything
{
    "run_status": "pending",              # CLI computed
    "next_step_name": "review_code",      # CLI computed
    "step_status": "approved",            # overloaded
    "step_outcome": "approve",            # overloaded
    "context_payload": { "__run_control": { ... } },  # buried flags
    ...
}

# NEW: CLI reports outcome, backend decides
{
    "outcome": "approved",                # what happened
    "failure_class": null,                # classification (if failure)
    "artifacts": { "REVIEW_FILE": "/path/to/review.md" },
    "review": { "decision": "APPROVED", "remark": "..." },
    "usage_summary": { "input_tokens": 5000, "output_tokens": 2000 },
    "error_message": null,
}
```

### 8.5 Local job.json

Local `job.json` remains as an **execution record** (not authoritative state):

- Tracks artifacts produced, step outputs, coder results
- Used by CLI for crash recovery within a single execution
- No longer the source of truth for `job_status` — backend is
- Schema stays the same initially; simplified in a follow-up

---

## 9. Console Architecture (React)

### 9.1 Tech Stack

| Layer | Choice |
|---|---|
| Framework | React 19 + TypeScript |
| Build | Vite |
| UI components | shadcn/ui (Radix primitives) |
| Styling | Tailwind CSS |
| Server state | TanStack Query (React Query) |
| HTTP client | fetch API or axios |

### 9.2 Console → Backend Interaction

The console calls the backend API directly. No CLI intermediary.

| Console action | API call |
|---|---|
| View active runs | `GET /api/runs?status=active` |
| View run detail | `GET /api/runs/{id}` |
| Submit job | `POST /api/runs` |
| Approve | `POST /api/runs/{id}/action` `{action: "APPROVE"}` |
| Reject | `POST /api/runs/{id}/action` `{action: "REJECT", feedback: "..."}` |
| Resume | `POST /api/runs/{id}/action` `{action: "RESUME"}` |
| Retry | `POST /api/runs/{id}/action` `{action: "RETRY"}` |
| Cancel | `POST /api/runs/{id}/action` `{action: "CANCEL"}` |
| Reset step | `POST /api/runs/{id}/reset-step` |
| Stop daemon | `POST /api/workers/{id}/stop` |

### 9.3 UI State from Backend

The console does NOT implement status logic. The backend provides:

- `run_status` — display as-is (with human-readable labels)
- `action_requested` — show "Processing: APPROVE" indicator
- `valid_actions` — enable/disable action buttons directly

```typescript
// Console component pseudocode
function RunActions({ run }: { run: RunDetail }) {
    return (
        <div>
            {run.action_requested && (
                <Badge>Pending: {run.action_requested}</Badge>
            )}
            {run.valid_actions.map(action => (
                <Button key={action} onClick={() => requestAction(run.id, action)}>
                    {action}
                </Button>
            ))}
        </div>
    );
}
```

### 9.4 Polling Strategy

- Active runs list: `refetchInterval: 5000` (TanStack Query)
- Run detail: `refetchInterval: 2000` when viewing a specific run
- Manual refresh button always available

---

## 10. Interaction Diagrams

### 10.1 Normal Step Execution

```
Console        Backend          Daemon          CLI
  │               │               │              │
  │ POST /runs    │               │              │
  │──────────────▶│               │              │
  │ 201: SUBMITTED│               │              │
  │◀──────────────│               │              │
  │               │               │              │
  │               │  POST /claim  │              │
  │               │◀──────────────│              │
  │               │──────────────▶│              │
  │               │ EXECUTE_STEP  │              │
  │               │ status→RUNNING│              │
  │               │               │              │
  │               │               │ spawn CLI    │
  │               │               │─────────────▶│
  │               │               │              │ execute step
  │               │               │              │ (coder, prompts)
  │               │               │              │
  │               │               │  outcome     │
  │               │               │◀─────────────│
  │               │               │              │
  │               │  POST /outcome│              │
  │               │◀──────────────│              │
  │               │ {outcome: approved}          │
  │               │               │              │
  │               │ compute next  │              │
  │               │ status→PENDING│              │
  │               │               │              │
  │               │  200: {run_status: PENDING,  │
  │               │        current_step: next}   │
  │               │──────────────▶│              │
  │               │               │              │
  │ GET /runs     │               │              │
  │──────────────▶│               │              │
  │ status:PENDING│               │              │
  │◀──────────────│               │              │
```

### 10.2 Human Approval Flow

```
Console        Backend          Daemon          CLI
  │               │               │              │
  │  ...step completed with review gate...        │
  │               │               │              │
  │               │  status→AWAITING_APPROVAL     │
  │               │               │              │
  │ GET /runs     │               │              │
  │──────────────▶│               │              │
  │ AWAITING_APPROVAL              │              │
  │ valid: [APPROVE,REJECT,CANCEL] │              │
  │◀──────────────│               │              │
  │               │               │              │
  │ User clicks Approve           │              │
  │ POST /action  │               │              │
  │ {APPROVE}     │               │              │
  │──────────────▶│               │              │
  │               │ validate:     │              │
  │               │ status=AWAITING_APPROVAL ✓    │
  │               │ action_req=null ✓             │
  │               │ set action_requested=APPROVE  │
  │ 200: OK       │               │              │
  │◀──────────────│               │              │
  │               │               │              │
  │               │  POST /claim  │              │
  │               │◀──────────────│              │
  │               │ PROCESS_ACTION│              │
  │               │ action=APPROVE│              │
  │               │ action_req→null (atomic)      │
  │               │               │              │
  │               │               │ spawn CLI    │
  │               │               │ --approve-step
  │               │               │─────────────▶│
  │               │               │              │ process approval
  │               │               │              │ in job.json
  │               │               │              │
  │               │  POST /outcome│              │
  │               │◀──────────────│              │
  │               │ {outcome: approved}          │
  │               │               │              │
  │               │ compute next  │              │
  │               │ status→PENDING│              │
  │               │               │              │
  │ GET /runs     │               │              │
  │──────────────▶│               │              │
  │ status:PENDING│               │              │
  │ action_req:null                │              │
  │◀──────────────│               │              │
```

### 10.3 Cancel Flow

```
Console        Backend          Daemon          CLI
  │               │               │              │
  │ POST /action  │               │              │
  │ {CANCEL}      │               │              │
  │──────────────▶│               │              │
  │               │ validate ✓    │              │
  │               │ status→FAILED │              │
  │ 200: OK       │               │              │
  │◀──────────────│               │              │
  │               │               │              │
  │               │  POST /claim  │              │
  │               │  (run not served — FAILED)    │
  │               │◀──────────────│              │
  │               │ IDLE          │              │
  │               │               │              │
  │               │  If CLI was running:          │
  │               │  CLI syncs outcome            │
  │               │  Backend rejects (run FAILED) │
```

---

## 11. Migration Plan

### Phase 1: New Backend (standalone, zero risk)

**Repo:** `agent-runner-backend-v2`  
**Port:** 8200  
**Duration:** 2-3 weeks

| Task | Description |
|---|---|
| 1.1 | Set up project structure (FastAPI/Flask, DB migrations, test framework) |
| 1.2 | Define schema: runs, step_runs, workers, workflows, artifacts, events |
| 1.3 | Implement state machine engine with comprehensive unit tests |
| 1.4 | Implement API endpoints (runs, workers, workflows) |
| 1.5 | Implement workflow sync (accept workflow definitions from existing sync CLI) |
| 1.6 | Integration tests: submit → claim → outcome → transition cycles |

**Deliverable:** New backend passes all state machine tests. Can accept workflow syncs.  
**Risk:** None — completely separate repo, old system untouched.

### Phase 2: Adapt Daemon + CLI (feature-flagged)

**Duration:** 2 weeks

| Task | Description |
|---|---|
| 2.1 | Add `v2_backend_url` config option to `~/.ukbe-runner/config.json` |
| 2.2 | Create new sync payload builder in `daemon_runtime.py` (outcome-only format) |
| 2.3 | Adapt `run_agent.py` post-execution sync to use new format when v2 enabled |
| 2.4 | Adapt daemon claim loop to handle new work_type field |
| 2.5 | Adapt daemon to read `action_requested` directly (no __run_control parsing) |
| 2.6 | Add new claim endpoint client method in `backend_client.py` |
| 2.7 | End-to-end test: run a real workflow on new backend with v2 flag enabled |

**Deliverable:** Daemon + CLI can run workflows against new backend.  
**Risk:** Low — old flow remains default. V2 only activates with explicit config.  
**Old system:** Runs unchanged with `v2_backend_url` unset.

### Phase 3: Cutover

**Duration:** 1 day

| Step | Action |
|---|---|
| 3.1 | Ensure all active runs are in stable state (completed, failed, or awaiting human) |
| 3.2 | Stop daemon |
| 3.3 | Set `backend_url` to `http://localhost:8200` (new backend) |
| 3.4 | Start daemon — now speaks new API exclusively |
| 3.5 | Verify with a test workflow |
| 3.6 | Monitor for 24 hours |

**Rollback:** Set `backend_url` back to `http://localhost:8100`, restart daemon.

### Phase 4: React Console

**Duration:** 2-3 weeks (parallel with Phase 2-3)

| Task | Description |
|---|---|
| 4.1 | Set up React + Vite + TypeScript + Tailwind + shadcn/ui |
| 4.2 | Implement run list view (GET /api/runs) |
| 4.3 | Implement run detail view with valid_actions buttons |
| 4.4 | Implement submit job form |
| 4.5 | Implement action requests (POST /api/runs/{id}/action) |
| 4.6 | Implement daemon management (worker list, stop/restart) |
| 4.7 | Implement workflow management (sync, list) |

**Deliverable:** React console replaces Flet console.  
**Note:** Can be developed in parallel with Phase 2 since it only needs the new backend API.

### Phase 5: Cleanup

**Duration:** 1 week

| Task | Description |
|---|---|
| 5.1 | Remove old backend (port 8100) |
| 5.2 | Remove old API code from CLI/daemon |
| 5.3 | Remove Layer 3 from CLI (routing, state machine logic) |
| 5.4 | Remove `__run_control` flag mechanism |
| 5.5 | Remove `v2_backend_url` flag — new API is the only API |
| 5.6 | Rename `agent-runner-backend-v2` to `agent-runner-backend` |
| 5.7 | Update documentation |

---

## 12. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| State machine bug in new backend | Wrong routing, stuck runs | Medium | Comprehensive unit tests for all transitions; Phase 2 dual-mode allows comparison |
| Daemon crash mid-sync | Run stuck in RUNNING | Low | Backend heartbeat timeout detection; auto-transition to FAILED |
| CLI outcome format mismatch | Backend can't process outcome | Low | Shared schema validation; integration tests in Phase 2 |
| Workflow sync incompatibility | New backend can't parse existing workflows | Low | Use existing workflow TOML format; validate sync in Phase 1 |
| React console API contract drift | Console and backend disagree on API | Low | API contract defined in this spec; both developed against it |
| Data migration (old → new backend) | Lost run history | Low | Run history is reference-only; active runs drained before cutover |

---

## 13. Technology Stack

### 13.1 Backend Stack (matches existing backend patterns)

| Layer | Technology | Notes |
|---|---|---|
| Framework | FastAPI | Same as existing backend |
| ORM | SQLAlchemy 2.x | Same as existing backend |
| Database | PostgreSQL | Same as existing backend |
| Migrations | Alembic | Same as existing backend |
| Testing | pytest | Same as existing backend |
| Python | 3.12+ | Same as runner |

### 13.2 Three-Layer Architecture

Mirrors the existing backend (`agent-runner-backend`) layer structure:

```
agent_runner_backend_v2/
├── api/                    # Layer 1: HTTP routes, schemas, serializers
│   ├── run_routes.py       #   POST /api/runs, GET /api/runs, POST /api/runs/{id}/action
│   ├── worker_routes.py    #   POST /api/workers/register, /claim, /heartbeat
│   ├── workflow_routes.py  #   POST /api/workflows/sync, GET /api/workflows
│   ├── schemas.py          #   Pydantic request/response models
│   └── serializers.py      #   ORM → JSON serialization
│
├── services/               # Layer 2: Business logic, state machine engine
│   ├── state_machine.py    #   transition(), handle_step_outcome(), handle_action()
│   ├── run_service.py      #   submit_run(), claim_work(), report_outcome()
│   ├── worker_service.py   #   register_worker(), heartbeat(), check_timeout()
│   └── workflow_service.py #   sync_workflow(), get_workflow_definition()
│
├── database/               # Layer 3: Data access (repository pattern)
│   ├── run_repository.py   #   get_run_by_id(), list_runs(), create_run(), update_run()
│   ├── worker_repository.py
│   └── workflow_repository.py
│
├── models/                 # SQLAlchemy ORM models
│   ├── run.py              #   WorkflowRun, WorkflowStepRun, WorkflowEvent, WorkflowArtifact
│   ├── worker.py           #   WorkerRegistry
│   └── workflow.py         #   WorkflowDefinition, WorkflowStepDefinition
│
├── main.py                 # FastAPI app entry point
└── config.py               # Settings (DB URL, port, timeouts)
```

**Layer rules (enforced by convention and tests):**

| Rule | Description |
|---|---|
| API → Service | Routes call service functions. Routes never call repository directly. |
| Service → Repository | Services call repository functions. Services never use `db.query()` directly. |
| Repository → DB | Repositories take `Session`, return model objects. No business logic. |
| No circular deps | Repository doesn't import service. Service doesn't import API. |

### 13.3 Testing Strategy — TDD, Real Database, No Mocks

**Principle:** Test behavior, not wiring. Every function has a unit test that verifies its actual output given real inputs. Avoid mock objects — use a real test database.

#### Test Layers

| Layer | Test location | What it tests | Database? |
|---|---|---|---|
| Repository | `tests/unit/test_*_repository.py` | CRUD operations, query filters, constraints | Real test DB |
| Service | `tests/unit/test_*_service.py` | State machine transitions, business rules, validation | Real test DB |
| API | `tests/integration/test_*_routes.py` | HTTP endpoints, request validation, response format | Real test DB |
| State machine | `tests/unit/test_state_machine.py` | All transition rules, edge cases, invariants | Real test DB |

#### TDD Cycle

```
1. Write a failing test for the desired behavior
2. Write the minimum code to make the test pass
3. Refactor while keeping tests green
4. Repeat
```

#### Unit Test Rules

1. **No mock objects for database** — Use a real PostgreSQL test database. Tests create their own data, verify results, clean up.
2. **Test behavior, not wiring** — Verify the function returns the correct result, not that it calls another function.
3. **Every function tested** — Repository CRUD, service logic, state machine transitions, validation rules.
4. **Edge cases covered** — Invalid transitions, concurrent claims, duplicate actions, terminal state enforcement.
5. **Fast feedback** — Unit tests run in < 10 seconds. Integration tests run separately.

#### Test Database Setup

```python
# conftest.py
TEST_DATABASE_URL = os.environ.get("AGENT_RUNNER_TEST_DATABASE_URL")
# Falls back to same PostgreSQL with a test schema or separate test database

@pytest.fixture
def db_session():
    """Create a fresh database session for each test, with rollback."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)
```

#### State Machine Test Coverage (Critical)

The state machine engine is the most important code in the backend. It gets exhaustive test coverage:

```python
# tests/unit/test_state_machine.py

class TestNormalFlow:
    def test_submitted_to_running_on_claim(self): ...
    def test_running_to_pending_on_approved_with_next_step(self): ...
    def test_running_to_completed_on_approved_no_next_step(self): ...
    def test_running_to_awaiting_approval_on_review_gate(self): ...
    def test_running_to_pending_on_auto_retryable_failure(self): ...
    def test_running_to_awaiting_intervention_on_human_retry_failure(self): ...
    def test_running_to_failed_on_fatal_failure(self): ...

class TestRefineLoop:
    def test_rejected_with_refine_available_decrements_iterations(self): ...
    def test_rejected_refine_exhausted_with_replan(self): ...
    def test_rejected_all_exhausted_to_awaiting_maxretried(self): ...

class TestHumanActions:
    def test_approve_from_awaiting_approval(self): ...
    def test_reject_from_awaiting_approval(self): ...
    def test_resume_from_awaiting_intervention(self): ...
    def test_retry_from_awaiting_intervention(self): ...
    def test_cancel_from_any_non_terminal(self): ...

class TestValidation:
    def test_reject_approve_when_not_awaiting_approval(self): ...
    def test_reject_action_when_another_action_pending(self): ...
    def test_reject_any_action_on_terminal_status(self): ...
    def test_atomic_action_consumption(self): ...

class TestInvariants:
    def test_single_action_enforced(self): ...
    def test_terminal_is_terminal(self): ...
    def test_running_exclusivity(self): ...
    def test_claim_filter_excludes_action_pending(self): ...
```

### 13.4 Resolved Design Decisions

| Decision | Resolution | Rationale |
|---|---|---|
| Worker timeout | Configurable, default 60s (3x 20s heartbeat) | Simple, tunable per environment |
| Parallel steps | Keep `max_parallel` support | Existing capability, minimal complexity in new design |
| Event storage | Store transition events (not event-sourced) | Audit trail + debugging without architectural overhead |
| Console transport | Start with HTTP polling (5s), WebSocket later if needed | Simpler to build, good enough for operator console |
| Local job.json | Keep as execution scratch space | Simplify schema in follow-up initiative |

## 14. Open Questions

_None remaining — all resolved in Section 13.4._
