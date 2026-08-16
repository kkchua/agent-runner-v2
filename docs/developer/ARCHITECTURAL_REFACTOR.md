# Architectural Refactor — Complete Documentation

**Date:** 2026-07-27  
**Status:** Phase 1 COMPLETED, Phase 2-3 PLANNED  
**Plan saved to:** `memory/project/architectural-refactor-plan.md`

This document consolidates the architectural refactor investigation, findings, implementation spec, and race condition analysis into a single reference.

---

## Table of Contents

1. [Architecture Principle](#architecture-principle)
2. [Root Cause Analysis](#root-cause-analysis)
3. [Architecture Violations Found](#architecture-violations-found)
4. [Implementation Plan](#implementation-plan)
5. [Race Conditions](#race-conditions)
6. [Phase 1 Results](#phase-1-results)

---

## Architecture Principle

```
Console (Control Panel) → CLI (brain) → Backend (database)
Daemon  (messenger)     → CLI (brain) → Backend (database)
```

### Role Definitions

| Component | Role | Responsibilities |
|-----------|------|------------------|
| **Backend** | Database persistence | No logic. Stores runs, step_runs, artifacts. Returns data on request. |
| **Console** | UI only | ALL operations through CLI. Zero direct backend calls. |
| **Daemon** | Messenger | Claims work, spawns CLI, monitors liveness. No business logic. |
| **CLI** | The brain | All logic, all backend API calls, all state transitions. |

**Why this matters:** The previous architecture had Console making direct backend calls, which bypassed CLI logic and caused race conditions where cancelled jobs were re-claimed by the daemon.

---

## Root Cause Analysis

### The Bug

After cancelling a job via the operator console, the daemon would re-claim and continue executing the cancelled job after restart.

### Root Causes Identified

#### 1. Console Cancel had NO direct backend call

**Location:** `app.py` line 861-883 (before refactor)

**Problem:**
- Cancel only called `runner_service.cancel_run()` → `run --cancel-run`
- This required local `job.json` to exist
- For cross-OS repos (Windows console, WSL daemon), `job.json` is on a different OS → `FileNotFoundError`
- Backend never got notified → run stayed "pending" → daemon re-claimed it

#### 2. `run --cancel-run` required local job.json

**Location:** `cli_runtime.py` line 292-336 (before refactor)

**Problem:**
- `load_job()` raised `FileNotFoundError` if job.json didn't exist
- If job.json existed but missing `workflow_step_run_id`, backend sync was skipped
- If job.json existed but missing `workflow_run_id`, `stop_run()` was skipped

#### 3. Backend `claim_step()` didn't filter stopped runs

**Location:** Backend API (not in this repo)

**Problem:**
- Daemon sent `POST /api/workers/claim?worker_id=...` with NO status filters
- Backend returned any pending step_run, including those from stopped runs
- Daemon's `_is_stop_requested()` caught it, but only if the flag was properly set

### The Fix (Phase 1 — COMPLETED)

Enhanced `stop_commands.py` to perform comprehensive cancel:

```python
# stop_commands.py main()
# Step 1: Query backend for active step_run_id
run_detail = client.get_run(run_id=args.run_id)
step_run_id = run.get("current_step_run_id")

# Step 2: Sync step-level cancelled status
if step_run_id:
    client.sync_job_state(
        step_run_id=step_run_id,
        payload={
            "run_status": "stopped",
            "step_status": "cancelled",
            "step_outcome": "cancelled",
            "context_payload": {"__run_control": {"stop_requested": True}},
            ...
        }
    )

# Step 3: Set run-level stop flag
client.stop_run(run_id=args.run_id, mode="after_current_step")
```

**Result:** Cancel works WITHOUT local `job.json` — purely backend-driven. Cross-OS compatible.

---

## Architecture Violations Found

### Console Violations (13 direct backend calls)

| Component | Method | Backend Call | Fix |
|-----------|--------|--------------|-----|
| `backend_service.py` | `list_active_runs()` | `list_runs()` | NEW: `list-runs` CLI ✅ |
| `backend_service.py` | `list_active_runs_for_worker()` | `list_runs()` | NEW: `list-runs` CLI ✅ |
| `backend_service.py` | `get_run_detail()` | `get_run()` | NEW: `show-run` CLI ✅ |
| `backend_service.py` | `stop_run()` | `stop_run()` | Use `stop` CLI ✅ |
| `backend_service.py` | `approve_run()` | `approve_run()` | Use `approve` CLI ✅ |
| `backend_service.py` | `reject_run()` | `approve_run()` | Use `approve --reject` CLI ✅ |
| `backend_service.py` | `reset_step()` | `reset_step()` | NEW: `reset-step` CLI ✅ |
| `backend_service.py` | `get_run_detail_dict()` | `get_run()` | NEW: `show-run` CLI ✅ |
| `runner_service.py` | `_submit_via_backend()` | `create_run()` | Use `submit` CLI ✅ |
| `runner_service.py` | `_is_cross_os()` | Direct check | Removed — CLI handles cross-OS ✅ |

**Phase 1 Result:** All 13 violations fixed. Console now uses CLI commands exclusively.

### Daemon Violations (post-child result processing)

**Location:** `daemon.py` `_run_supervisor()` (before refactor)

**Problem:**
- Daemon read `job.json` after child exited
- Daemon built sync payload from job.json
- Daemon called `sync_job_state()` to backend
- Daemon checked `get_run()` for stop flag

**Violation:** Daemon was doing CLI's job (business logic, backend sync).

**Fix (Phase 1 — COMPLETED):**
- Removed ~95 lines of post-child result processing
- CLI now syncs results directly via `_sync_results_to_backend()` in `run_agent.py`
- Daemon only monitors liveness and logs exit codes

---

## Implementation Plan

### Phase 1: CLI + Backend — Build the Foundation ✅ COMPLETED

**New CLI Commands:**
- `list-runs` — List workflow runs from backend
- `show-run` — Show run detail
- `reset-step` — Reset step to a different step

**Enhanced CLI Commands:**
- `stop` — Comprehensive cancel (queries backend, syncs step-level, sets run-level flag)
- `approve` — Added `--resume` and `--retry` flags

**Console Changes:**
- Removed `backend_service.py` entirely
- Rewrote `runner_service.py` to use CLI commands
- Updated `app.py` to call `runner_service` methods (which invoke CLI)

**Daemon Changes:**
- Removed post-child result processing (~95 lines)
- CLI subprocess handles result syncing directly

**Tests:**
- `test_list_runs_commands.py` — 5 tests
- `test_show_run_commands.py` — 2 tests
- `test_reset_step_commands.py` — 2 tests
- `test_stop_commands.py` — 3 tests
- `test_approve_commands.py` — 6 tests
- `test_daemon_result_sync.py` — 4 tests
- `test_operator_console_services.py` — 6 tests

**Total:** 28 tests, all passing.

### Phase 2: Daemon Pre-Execution Sync ✅ COMPLETED

**Problem:** Daemon didn't fetch full backend state before spawning CLI. CLI operated on stale/incomplete data.

**Fix:**
- Modified `daemon.py` `_spawn_child()` to call `client.get_run(run_id)` before spawning
- Writes `backend_state.json` to child directory
- Sets `AGENT_RUNNER_BACKEND_STATE_FILE` env var
- CLI reads backend state and initializes `job.json` from it

**Files Modified:**
- `agent_runner_v2/daemon.py` — fetch backend state before spawn
- `agent_runner_v2/manual_runtime.py` — added `_load_backend_state_file()` and `_initialize_state_from_backend()`

**Tests:**
- `test_daemon_race_conditions.py::test_daemon_fetches_backend_state_before_spawn` ✅
- `test_daemon_race_conditions.py::test_cli_initializes_from_backend_state` ✅

### Phase 3: Post-Execution Conflict Check ✅ COMPLETED

**Problem:** CLI blindly synced results to backend without checking if backend state changed during execution (e.g., cancelled by console).

**Fix:**
- Modified `run_agent.py` `_sync_results_to_backend()` to check backend status before sync
- Fetches current run state via `client.get_run(run_id)`
- Checks `run_status` and `__run_control.stop_requested`
- If cancelled/stopped: skips sync, logs warning, preserves cancelled state
- If check fails: proceeds with sync (non-fatal)

**Files Modified:**
- `agent_runner_v2/run_agent.py` — added conflict check in `_sync_results_to_backend()`

**Tests:**
- `test_daemon_race_conditions.py::test_cli_skips_sync_when_backend_cancelled` ✅
- `test_daemon_race_conditions.py::test_cli_syncs_when_backend_active` ✅
- `test_daemon_race_conditions.py::test_cli_syncs_when_backend_check_fails` ✅

### Phase 4: Backend-Side Protection (Future)

**Planned:** Backend `sync_job_state` endpoint should reject updates when `run_status="stopped"` or `step_status="cancelled"`.

**Status:** Not yet implemented (requires backend repo changes).

---

## Race Conditions

### Scenario 1: Cancel During Execution

**Timeline:**
- T0: Daemon claims job A, spawns CLI
- T1: CLI executes step (5-min LLM call)
- T2: Console cancels → backend sets `stopped/cancelled`
- T3: CLI finishes, calls `_sync_results_to_backend()`

**Before Fix:**
- CLI overwrites backend with `completed` from local job.json
- Cancelled state is lost

**After Fix:**
- CLI checks backend status before sync
- Sees `run_status="stopped"` or `stop_requested=True`
- Skips sync, preserves cancelled state
- Logs: `[daemon-sync] Backend state changed during execution, skipping sync`

### Scenario 2: Data Update During Execution

**Timeline:**
- T0: Daemon claims job A, spawns CLI
- T1: CLI executes step
- T2: Console updates metadata (artifacts, context)
- T3: CLI finishes, syncs results

**Before Fix:**
- CLI overwrites with stale local data
- Updates made during execution are lost

**After Fix:**
- Daemon fetches full backend state before spawning CLI
- CLI initializes job.json from latest backend state
- Updates are preserved

### Scenario 3: Pre-Execution State Mismatch

**Timeline:**
- T0: Backend has updated state (new artifacts, context changes)
- T1: Daemon claims job
- T2: CLI creates job.json from request payload only

**Before Fix:**
- CLI operates on incomplete data
- Missing artifacts from previous steps

**After Fix:**
- Daemon fetches full backend state via `get_run(run_id)`
- Passes to CLI via `backend_state.json`
- CLI initializes from complete backend state

---

## Phase 1 Results

### Files Created

**New CLI Commands:**
- `agent_runner_v2/list_runs_commands.py` — `ukbe-run-agent list-runs`
- `agent_runner_v2/show_run_commands.py` — `ukbe-run-agent show-run`
- `agent_runner_v2/reset_step_commands.py` — `ukbe-run-agent reset-step`

**New Tests:**
- `tests/unit/test_list_runs_commands.py` — 5 tests
- `tests/unit/test_show_run_commands.py` — 2 tests
- `tests/unit/test_reset_step_commands.py` — 2 tests
- `tests/unit/test_approve_commands.py` — 6 tests
- `tests/unit/test_daemon_result_sync.py` — 4 tests
- `tests/unit/test_daemon_race_conditions.py` — 5 tests

**Documentation:**
- `JOB_DEFINITION_DICTIONARY.md` — Comprehensive job state reference
- `ARCHITECTURAL_REFACTOR_FINDINGS.md` — Investigation findings (consolidated into this doc)
- `ARCHITECTURAL_REFACTOR_SPEC.md` — Implementation spec (consolidated into this doc)
- `DAEMON_RACE_CONDITIONS.md` — Race condition analysis (consolidated into this doc)

### Files Modified

**Console:**
- `agent_runner_v2/operator_console/services/backend_service.py` — DELETED
- `agent_runner_v2/operator_console/services/runner_service.py` — REWRITTEN (CLI wrappers)
- `agent_runner_v2/operator_console/app.py` — Updated to use runner_service

**Daemon:**
- `agent_runner_v2/daemon.py` — Removed post-child processing, added pre-execution sync
- `agent_runner_v2/run_agent.py` — Added `_sync_results_to_backend()`, conflict check

**CLI Commands:**
- `agent_runner_v2/stop_commands.py` — Enhanced with comprehensive cancel
- `agent_runner_v2/approve_commands.py` — Added `--resume` and `--retry` flags

**Runtime:**
- `agent_runner_v2/manual_runtime.py` — Added backend state initialization

### Test Results

**All tests passing:**
- 279 unit tests passed
- 10 skipped
- 0 failed

**New test coverage:**
- CLI commands: 18 tests
- Daemon sync: 4 tests
- Race conditions: 5 tests
- Console services: 6 tests

**Total new tests:** 33 tests

---

## Key Takeaways

1. **CLI is the brain** — All business logic, backend API calls, and state transitions happen in CLI
2. **Console is dumb** — UI only, delegates everything to CLI
3. **Daemon is a messenger** — Claims work, spawns CLI, monitors liveness. No business logic.
4. **Backend is persistence** — No logic, just stores and returns data
5. **Race conditions are managed** — Pre-execution sync and post-execution conflict check prevent data loss
6. **Cross-OS compatible** — Cancel works without local job.json, purely backend-driven

---

## References

- **README.md** — Master documentation index
- **QWEN.md** — Comprehensive project reference
- **JOB_DEFINITION_DICTIONARY.md** — Job state model reference
- **CODER_IMPLEMENTATION_SOP.md** — Execution discipline for coding tasks
- **AGENT_RUNNER_V2_SPECIALIST.md** — Agent navigation instructions

---

## Maintenance

**Updating this document:**
- Keep the "Phase X Results" sections current as work progresses
- Update the "Race Conditions" section if new scenarios are discovered
- Link to this document from README.md and QWEN.md
- Archive this document when the refactor is fully complete and stable

**Related documents:**
- `memory/project/architectural-refactor-plan.md` — Original plan (memory)
- `ARCHITECTURAL_REFACTOR_FINDINGS.md` — Superseded by this document
- `ARCHITECTURAL_REFACTOR_SPEC.md` — Superseded by this document
- `DAEMON_RACE_CONDITIONS.md` — Superseded by this document
