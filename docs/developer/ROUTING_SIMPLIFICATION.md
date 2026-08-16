# Workflow Execution Routing — Single Source of Truth

> **Status:** DRAFT — 2026-08-06
> **Scope:** Simplified routing contract + complete execution matrix for `sdlc_00_codebase_v1`
> **Audience:** Daemon, CLI, and Backend implementors — this is THE reference.

---

## Part 1: Routing Contract

### 1.1 Routing Keys (Complete)

| Key | Where Set | Purpose |
|-----|-----------|---------|
| `onsuccess` | Any step | Next step after success |
| `on_reject_refine` | Review step only | Step to invoke when review rejects (contains `step`, `artifact`, `max_iterations`) |
| `requires_human_approval_after` | Any step (optional) | After success, wait for human approval before advancing |

**Removed:**
- `loop_returns_to` — refine steps use `onsuccess` to return to review
- `replan_returns_to` — same
- `on_exhaust_replan` — backend SOP handles exhaustion

### 1.2 Step Type Detection

| Step Type | How to Detect |
|-----------|---------------|
| **Review** | Step has `on_reject_refine` config |
| **Refine** | Step name matches some other step's `on_reject_refine.step` |
| **Normal** | Neither review nor refine |

### 1.3 Standard SOP (Backend-Managed, Not Workflow-Defined)

| Condition | Backend Action |
|-----------|---------------|
| Review rejects, refine step defined | Create step_run for refine step, status=PENDING |
| Refine succeeds | Create step_run for review step (re-review), status=PENDING |
| Refine itself rejects | status=AWAITING_INTERVENTION (no nested loops) |
| reject_count > max_iterations | status=AWAITING_INTERVENTION |
| Validator failure | status=AWAITING_INTERVENTION |
| Action step fails | status=AWAITING_INTERVENTION |
| Step has `requires_human_approval_after` and succeeds | status=WAITING_FOR_HUMAN_APPROVAL |

### 1.4 Status Vocabulary

| Backend `run_status` | Meaning | Claimable? |
|---------------------|---------|-----------|
| PENDING | Step ready | Yes → EXECUTE_STEP |
| RUNNING | Daemon executing | No |
| WAITING_FOR_HUMAN_APPROVAL | Human gate | No (needs USER_APPROVED/USER_REJECTED) |
| AWAITING_INTERVENTION | Error/exhausted | No (needs USER_RESUMED/USER_RETRIED) |
| USER_APPROVED | Human approved | Yes → PROCESS_ACTION |
| USER_REJECTED | Human rejected | Yes → PROCESS_ACTION |
| USER_RESUMED | Human resumed | Yes → PROCESS_ACTION |
| USER_RETRIED | Human retried | Yes → PROCESS_ACTION |
| COMPLETED | Done | No |
| FAILED | Failed | No |
| CANCELLED | Cancelled | No |

---

## Part 2: sdlc_00_codebase_v1 — Step Definitions

```
sync_codebase_docs → generate_sync_log → review_sync_log ──┐
                                            │               │
                                            │ rejected      │
                                            ▼               │
                                     refine_codebase_docs ──┘
                                            │
                                            │ approved (re-review)
                                            ▼
                                     review_sync_log → validate_codebase_docs ──┐
                                            │                                    │
                                            │ rejected                           │
                                            ▼                                    │
                                     refine_codebase_docs ──────────────────────┘
                                            │
                                            │ approved
                                            ▼
                                     create_backup → publish_codebase_docs → commit_changes → stepCompletion
```

| # | Step | Type | `onsuccess` | `on_reject_refine` | Human Gate |
|---|------|------|-------------|---------------------|------------|
| 1 | sync_codebase_docs | action | generate_sync_log | — | — |
| 2 | generate_sync_log | action | review_sync_log | — | — |
| 3 | review_sync_log | review | validate_codebase_docs | refine_codebase_docs (max=2) | YES |
| 4 | refine_codebase_docs | refine | review_sync_log | — | — |
| 5 | validate_codebase_docs | action | create_backup | refine_codebase_docs (max=2) | — |
| 6 | create_backup | action | publish_codebase_docs | — | — |
| 7 | publish_codebase_docs | action | commit_changes | — | — |
| 8 | commit_changes | action | stepCompletion | — | — |
| 9 | stepCompletion | terminal | — | — | — |

**Key observations:**
- Both `review_sync_log` and `validate_codebase_docs` can reject to the same `refine_codebase_docs`
- `refine_codebase_docs` returns to `review_sync_log` via `onsuccess` (not `loop_returns_to`)
- When `validate_codebase_docs` rejects → refine → re-review → validate (full loop)

---

## Part 3: Execution Matrices — All Scenarios

### Notation

| Symbol | Meaning |
|--------|---------|
| B | Backend |
| D | Daemon |
| C | CLI |
| Q | Queue file |
| → | Data flow |

### Queue Outcome Schema (applies to ALL scenarios)

```json
{
  "step_run_id": "uuid",
  "run_id": "uuid",
  "run_code": "SDLC00CB-xxxx",
  "workflow_name": "sdlc_00_codebase_v1",
  "step_name": "<actual step executed>",
  "job_dir": "/path/to/job",
  "outcome": "approved | rejected | failed",
  "failure_class": null | "AUTO_RETRYABLE" | "HUMAN_RETRY_REQUIRED" | "FATAL",
  "artifacts": { "KEY": "path" },
  "review": { "decision": "APPROVED | REJECTED", "remark": "..." },
  "error_message": null,
  "usage_summary": {},
  "exit_code": 0,
  "timestamp": "ISO-8601"
}
```

**Critical rule:** `step_name` = the step that WAS EXECUTED, NOT the next step.

---

### Scenario A: Happy Path (all approved)

| Round | B: run_status | B: current_step | D: Action | C: Executes | C: job.json update | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|-------------------|------------|-------------|
| 1 | PENDING | sync_codebase_docs | claim→spawn | sync_codebase_docs | step→generate_sync_log | approved | PENDING, generate_sync_log |
| 2 | PENDING | generate_sync_log | claim→spawn | generate_sync_log | step→review_sync_log | approved | PENDING, review_sync_log |
| 3 | PENDING | review_sync_log | claim→spawn | review_sync_log | step→validate_codebase_docs, review=APPROVED | approved, review={APPROVED} | **WAITING_FOR_HUMAN_APPROVAL** (gate) |
| 4 | USER_APPROVED | review_sync_log | claim ACTION→spawn | --approve-step | clear pending_approval | approved | PENDING, validate_codebase_docs |
| 5 | PENDING | validate_codebase_docs | claim→spawn | validate_codebase_docs | step→create_backup | approved | PENDING, create_backup |
| 6 | PENDING | create_backup | claim→spawn | create_backup | step→publish_codebase_docs | approved | PENDING, publish_codebase_docs |
| 7 | PENDING | publish_codebase_docs | claim→spawn | publish_codebase_docs | step→commit_changes | approved | PENDING, commit_changes |
| 8 | PENDING | commit_changes | claim→spawn | commit_changes | step→stepCompletion | approved | PENDING, stepCompletion |
| 9 | PENDING | stepCompletion | claim→spawn | step_completion | status=COMPLETED | approved | **COMPLETED** |

---

### Scenario B: Review Rejects → Refine → Re-review Approved

| Round | B: run_status | B: current_step | D: Action | C: Executes | C: job.json update | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|-------------------|------------|-------------|
| 1-2 | PENDING | (steps 1-2) | — | — | — | — | — |
| 3 | PENDING | review_sync_log | claim→spawn | review_sync_log | step→refine_codebase_docs, review=REJECTED, loop_ctx.active=true, loop_iter=1 | rejected, review={REJECTED} | PENDING, **refine_codebase_docs** |
| 4 | PENDING | refine_codebase_docs | claim→spawn | refine_codebase_docs | loop_history.refine_result=APPROVED, loop_ctx.active=false, review cleared, step→review_sync_log | approved | PENDING, **review_sync_log** |
| 5 | PENDING | review_sync_log | claim→spawn | review_sync_log (re-review) | step→validate_codebase_docs, review=APPROVED | approved, review={APPROVED} | WAITING_FOR_HUMAN_APPROVAL |
| 6+ | (continues from Scenario A round 4) | — | — | — | — | — | — |

**CLI loop bookkeeping at round 3:**
```
loop_context = {
  active: true,
  loop_step: "review_sync_log",
  refine_step: "refine_codebase_docs",
  loop_target_artifact: "REVIEW_FILE_SUGGESTED",
  loop_iteration: 1,
}
loop_history.append({iteration: 1, review_result: "REJECTED", refine_result: null})
```

**CLI loop bookkeeping at round 4:**
```
loop_history[-1].refine_result = "APPROVED"
loop_history[-1].resolved_at = <timestamp>
loop_context = {active: false}
review_state.review_decision = null    ← clear stale REJECTED
```

---

### Scenario C: Max Iterations Exhausted (review rejects 3 times, max=2)

| Round | B: run_status | B: current_step | D: Action | C: Executes | C: job.json update | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|-------------------|------------|-------------|
| 3 | PENDING | review_sync_log | claim→spawn | review_sync_log (iter 1) | review=REJECTED, loop_iter=1 | rejected | PENDING, refine_codebase_docs |
| 4 | PENDING | refine_codebase_docs | claim→spawn | refine_codebase_docs | loop resolved, step→review_sync_log | approved | PENDING, review_sync_log |
| 5 | PENDING | review_sync_log | claim→spawn | review_sync_log (iter 2) | review=REJECTED, loop_iter=2 | rejected | PENDING, refine_codebase_docs |
| 6 | PENDING | refine_codebase_docs | claim→spawn | refine_codebase_docs | loop resolved, step→review_sync_log | approved | PENDING, review_sync_log |
| 7 | PENDING | review_sync_log | claim→spawn | review_sync_log (iter 3) | review=REJECTED, loop_iter=3 | rejected | **AWAITING_INTERVENTION** |

**Backend logic at round 7:**
```
reject_count for this loop = 3
max_iterations = 2
3 > 2 → set run_status = AWAITING_INTERVENTION
Do NOT create step_run for refine_codebase_docs
```

**Human resumes:**

| Round | B: run_status | B: current_step | D: Action | C: Executes | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|------------|-------------|
| 8 | USER_RESUMED | review_sync_log | claim ACTION→spawn | --resume-step | clear failure, step→validate_codebase_docs | approved | PENDING, validate_codebase_docs |

---

### Scenario D: Refine Step Itself Rejected

| Round | B: run_status | B: current_step | D: Action | C: Executes | C: job.json update | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|-------------------|------------|-------------|
| 3 | PENDING | review_sync_log | claim→spawn | review_sync_log | review=REJECTED, loop_iter=1 | rejected | PENDING, refine_codebase_docs |
| 4 | PENDING | refine_codebase_docs | claim→spawn | refine_codebase_docs | (coder returns REJECTED) | **rejected**, failure_class=HUMAN_RETRY_REQUIRED | **AWAITING_INTERVENTION** |

**Backend logic at round 4:**
```
Refine step rejected → no nested loops
Set run_status = AWAITING_INTERVENTION
```

---

### Scenario E: Validate Step Rejects → Refine → Full Loop Back to Validate

| Round | B: run_status | B: current_step | D: Action | C: Executes | C: job.json update | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|-------------------|------------|-------------|
| 1-4 | (happy path through human approval) | — | — | — | — | — | — |
| 5 | PENDING | validate_codebase_docs | claim→spawn | validate_codebase_docs | step→refine_codebase_docs, loop_ctx.active=true, loop_iter=1 | rejected, failure_class=HUMAN_RETRY_REQUIRED | PENDING, **refine_codebase_docs** |
| 6 | PENDING | refine_codebase_docs | claim→spawn | refine_codebase_docs | loop resolved, step→**review_sync_log** | approved | PENDING, **review_sync_log** |
| 7 | PENDING | review_sync_log | claim→spawn | review_sync_log (re-review) | step→validate_codebase_docs, review=APPROVED | approved | WAITING_FOR_HUMAN_APPROVAL |
| 8 | USER_APPROVED | — | claim ACTION→spawn | --approve-step | — | approved | PENDING, validate_codebase_docs |
| 9 | PENDING | validate_codebase_docs | claim→spawn | validate_codebase_docs (re-validate) | step→create_backup | approved | PENDING, create_backup |

**Key insight:** When validate rejects → refine → returns to review (via onsuccess) → review must approve again → then validate runs again. This is the full loop.

---

### Scenario F: Action Step Failure (e.g., sync_codebase_docs crashes)

| Round | B: run_status | B: current_step | D: Action | C: Executes | C: job.json update | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|-------------------|------------|-------------|
| 1 | PENDING | sync_codebase_docs | claim→spawn | sync_codebase_docs | (exception thrown) | **failed**, failure_class=HUMAN_RETRY_REQUIRED | **AWAITING_INTERVENTION** |

**Note:** Action steps have no `on_reject_refine` — failures go straight to AWAITING_INTERVENTION.

---

### Scenario G: Validator Failure (STEP_CONTRACT_MISMATCH)

| Round | B: run_status | B: current_step | D: Action | C: Executes | C: job.json update | Q: outcome | B: Response |
|-------|--------------|-----------------|-----------|-------------|-------------------|------------|-------------|
| N | PENDING | any_step | claim→spawn | step runs OK | (guardrail post_check fails) | **rejected**, failure_class=HUMAN_RETRY_REQUIRED, failure_source=guardrail | **AWAITING_INTERVENTION** |

**Note:** Validator failures bypass the refine loop entirely — they indicate structural contract violations, not content issues.

---

## Part 4: Handshake Contracts

The complete loop: **Backend → Daemon → CLI → Queue → Daemon → Backend**

```
┌──────────┐  claim_work   ┌──────────┐
│ Backend  │──────────────►│  Daemon   │
│          │               │          │
│          │               │ spawn    │
│          │               │──────────►┌──────────┐
│          │               │          │   CLI     │
│          │               │          │          │
│          │               │          │ write    │
│          │               │          │ outcome  │
│          │               │          │─────────►┤ Queue │
│          │  report_      │          │          │       │
│          │  outcome      │◄─────────│          │       │
│          │◄──────────────│  read    └──────────┘       │
│          │  next step    │  queue           │          │
└──────────┘               └──────────┘       └──────────┘
```

### 4.1 Backend → Daemon: `claim_work`

**Endpoint:** `POST /api/workers/{worker_id}/claim`

```json
{
  "work_type": "EXECUTE_STEP | PROCESS_ACTION | IDLE",
  "run": {
    "run_id": "uuid",
    "run_code": "SDLC00CB-xxxx",
    "workflow_name": "sdlc_00_codebase_v1",
    "project_root": "D:/path/to/project",
    "job_dir": "C:/.../jobs/.../SDLC00CB-xxxx"
  },
  "step_run": {
    "step_run_id": "uuid",
    "step_name": "sync_codebase_docs"
  }
}
```

### 4.2 Daemon → CLI: Subprocess Spawn

| Channel | Key | Value |
|---------|-----|-------|
| arg | `--mode` | `daemon` |
| arg | `--job` | `<step_name>` from claim |
| arg | `--job-id` | `<run_code>` if job exists, else empty |
| arg | `--job-no` | `<run_code>` |
| arg | `--start-step` | `<step_name>` (new jobs only) |
| arg | `--template-group` | `<workflow_name>` |
| arg | `--project-root` | from claim |
| env | `AGENT_RUNNER_WORKFLOW_RUN_ID` | run_id |
| env | `AGENT_RUNNER_WORKFLOW_STEP_RUN_ID` | step_run_id |
| env | `AGENT_RUNNER_JOB_DIR` | job directory |
| env | `AGENT_RUNNER_QUEUE_DIR` | queue directory |
| env | `AGENT_RUNNER_BACKEND_STATE_FILE` | backend_state.json path |

### 4.3 CLI → Queue: Outcome File

**File:** `{queue_dir}/{step_run_id}.json`

See Queue Outcome Schema in Part 3.

### 4.4 Daemon → Backend: `report_outcome`

**Endpoint:** `POST /api/runs/step-runs/{step_run_id}/outcome`

Daemon reads queue file, relays to backend. Daemon does NOT send `step_name` — backend identifies step by `step_run_id` in URL.

```json
{
  "outcome": "approved | rejected | failed",
  "failure_class": null | "AUTO_RETRYABLE" | "HUMAN_RETRY_REQUIRED" | "FATAL",
  "artifacts": {},
  "review": { "decision": "...", "remark": "..." },
  "error_message": null,
  "usage_summary": {},
  "job_dir": "/path"
}
```

Daemon does not wait for or use the response — next `claim_work` poll gets the new state.

---

## Part 5: State Ownership

| State | Owner | Persisted In | Synced Via |
|-------|-------|-------------|------------|
| run_status | **Backend** | DB | claim_work, backend_state.json |
| current_step | **Backend** | DB | claim_work, backend_state.json |
| step_run_id | **Backend** | DB | claim_work, env var |
| reject_count | **Backend** | DB | backend_state.json |
| max_iterations | **Backend** | DB (from workflow sync) | backend_state.json |
| completed_steps | CLI | job.json | — |
| loop_context | CLI | job.json | — |
| loop_history | CLI | job.json | — |
| review_state | CLI | job.json | — |
| artifacts | CLI | job.json | queue → backend mirror |
| usage_summary | CLI | job.json | queue → backend mirror |

---

## Part 6: Code Changes Required

### CLI (agent-runner-v2)

| File | Change |
|------|--------|
| `run_agent.py` | `_write_result_to_queue()`: add `step` param, use for `step_name` instead of `state["current_step"]` |
| `job_state.py:advance_step()` | Replace `step_cfg.get("loop_returns_to")` with `_is_refine_step(group_cfg, step)` scan |
| `job_state.py:_handle_refine_success()` | Use `step_cfg["onsuccess"]` instead of `step_cfg["loop_returns_to"]` |
| `workflow_packages/base.py` | Remove `loop_returns_to`, `replan_returns_to` fields |
| `workflow_packages/loader.py` | Remove `loop_returns_to`, `replan_returns_to` loading |
| `step_execution_runtime.py:76` | Replace `loop_returns_to` check with refine step detection |
| `workflow_bundle_validator.py` | Remove `loop_returns_to` validation |
| `workflow_specs.py` | Remove `loop_returns_to`, `replan_returns_to` |

### Backend (agent-runner-backend-v2)

| Change |
|--------|
| Track `reject_count` per review loop in state machine |
| `reject_count > max_iterations` → AWAITING_INTERVENTION |
| Remove `AWAITING_MAXRETRIED` status |
| Remove `on_exhaust_replan` handling |
| Validate outcome `step_name` matches `step_run_id` |
