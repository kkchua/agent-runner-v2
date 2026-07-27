# Daemon Race Conditions and State Synchronization

**Date**: 2026-07-27  
**Status**: Investigation Complete — Fixes Required

---

## Executive Summary

The daemon's claim → execute → sync flow has race conditions where concurrent console operations (cancel, data updates) can be overwritten by the CLI's post-execution sync. The root causes are:

1. **Pre-execution**: CLI does not fetch full backend state before execution — operates on stale/incomplete data
2. **Post-execution**: CLI blindly syncs results without checking if backend state changed during execution

---

## Current Architecture

### Daemon Claim → Execute → Sync Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ DAEMON                                                           │
├─────────────────────────────────────────────────────────────────┤
│ 1. client.claim_step(worker_id)                                  │
│    → receives {run, step_run, step_execution_spec}               │
│                                                                   │
│ 2. _spawn_child()                                                │
│    → builds request_payload from claim                           │
│    → writes request.json to runtime dir                          │
│    → spawns CLI subprocess with:                                 │
│      --job-id, --set flags, --start-step, --mode daemon          │
│                                                                   │
│ 3. Monitor child process (heartbeat, timeout, stalled)           │
│                                                                   │
│ 4. Child exits → daemon logs exit code (NO result processing)    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ CLI SUBPROCESS                                                     │
├─────────────────────────────────────────────────────────────────┤
│ 1. Load/create job.json from --job-id and --set flags            │
│    ⚠️ DOES NOT fetch full backend state                          │
│                                                                   │
│ 2. Execute step (LLM call, action, etc.)                         │
│    → writes results to local job.json                            │
│                                                                   │
│ 3. _sync_results_to_backend()                                    │
│    → build_job_sync_payload(job.json, step_result)               │
│    → client.sync_job_state(step_run_id, payload)                 │
│    ⚠️ DOES NOT check backend status before sync                  │
└─────────────────────────────────────────────────────────────────┘
```

### Console Cancel Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ OPERATOR CONSOLE                                                   │
├─────────────────────────────────────────────────────────────────┤
│ 1. User clicks "Cancel" on job A                                 │
│                                                                   │
│ 2. runner_service.stop_run(run_id)                               │
│    → invokes: ukbe-run-agent stop <run_id>                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STOP CLI COMMAND                                                   │
├─────────────────────────────────────────────────────────────────┤
│ 1. client.get_run(run_id)                                        │
│    → retrieves current_step_run_id                               │
│                                                                   │
│ 2. client.sync_job_state(step_run_id, {                          │
│      run_status: "stopped",                                      │
│      step_status: "cancelled",                                   │
│      step_outcome: "cancelled",                                  │
│      context_payload: {__run_control: {stop_requested: true}}    │
│    })                                                            │
│                                                                   │
│ 3. client.stop_run(run_id, mode="after_current_step")            │
│    → sets context_payload.__run_control.stop_requested flag      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Race Condition Scenarios

### Scenario 1: Cancel During Execution

**Timeline:**
- **T0**: Daemon claims job A, spawns CLI subprocess
- **T1**: CLI starts executing step (e.g., 5-minute LLM generation)
- **T2**: Console triggers cancel → backend sets `run_status="stopped"`, `step_status="cancelled"`, `__run_control.stop_requested=True`
- **T3**: CLI finishes execution, calls `_sync_results_to_backend()`

**Current Behavior:**
```python
# CLI in run_agent.py line 889-920
def _sync_results_to_backend(...):
    sync_payload = build_job_sync_payload(job=state, step_result=result_dict, ...)
    client = BackendClient(backend_url)
    client.sync_job_state(step_run_id=step_run_id, payload=sync_payload)
    # ⚠️ No check of backend status — blindly overwrites
```

**Result:**
- CLI overwrites backend with `run_status="pending"` (from local job.json)
- CLI overwrites `step_status="completed"` with artifacts
- **Cancelled state is lost**
- Backend shows completed instead of cancelled

**Expected Behavior:**
- CLI should check backend status before sync
- If `run_status="stopped"` or `stop_requested=True`, skip sync or log conflict
- Backend should retain cancelled state

---

### Scenario 2: Data Update During Execution

**Timeline:**
- **T0**: Daemon claims job A, spawns CLI subprocess
- **T1**: CLI starts executing step
- **T2**: Console updates job metadata (e.g., changes `context_payload.start_step`, updates artifact paths, adds notes)
- **T3**: CLI finishes, syncs results back

**Current Behavior:**
- CLI's local `job.json` has stale data (from T0)
- CLI overwrites backend with stale data
- **Updates made during execution are lost**

**Expected Behavior:**
- CLI should fetch latest backend state before sync
- Merge local results with backend state
- Preserve updates made during execution

---

### Scenario 3: Pre-Execution State Mismatch

**Timeline:**
- **T0**: Backend has updated state (e.g., new artifacts from previous step, context changes from console)
- **T1**: Daemon claims job
- **T2**: CLI creates `job.json` from request payload only (does NOT fetch full backend state)

**Current Behavior:**
```python
# Daemon in daemon.py line 217-282
def _spawn_child(*, claim, ...):
    request_payload = _build_worker_request_payload(
        run=run, step_run=step_run, step_execution_spec=..., ...
    )
    # request_payload contains:
    # - job_id, template_group, project_root
    # - input_artifacts (from --set flags)
    # - context_payload (start_step, etc.)
    # ⚠️ Does NOT include full backend state
    
    request_path.write_text(json.dumps(request_payload, ...))
    # CLI loads from request_payload, not backend
```

**Result:**
- CLI operates on incomplete/stale data
- May miss artifacts produced by previous steps
- May miss context updates

**Expected Behavior:**
- Daemon should fetch full run state before spawning CLI
- Pass full state to CLI via `request.json` or environment
- CLI should initialize `job.json` from backend state

---

### Scenario 4: Double-Sync Race

**Timeline:**
- **T0**: Two daemon workers somehow claim different steps of same run (shouldn't happen but...)
- **T1**: Both execute and sync independently
- **T2**: Last write wins

**Current Behavior:**
- No protection against concurrent syncs
- Last `sync_job_state()` call overwrites previous

**Expected Behavior:**
- Backend should enforce single active step_run per run
- Return 409 Conflict if concurrent sync detected

---

### Scenario 5: Console Resume During Execution

**Timeline:**
- **T0**: Daemon claims job A, spawns CLI
- **T1**: CLI executes step, awaiting approval
- **T2**: Console approves/resumes while CLI still running
- **T3**: CLI syncs results

**Current Behavior:**
- CLI may overwrite approval state with stale data

**Expected Behavior:**
- CLI checks backend → sees approval → adjusts sync accordingly

---

## Root Causes

### 1. No Pre-Execution Backend Sync

**Location**: `daemon.py` `_spawn_child()` function (line 217-282)

**Issue**: Daemon builds `request_payload` from the claim response, but does NOT fetch the full run state from backend. CLI creates `job.json` from this incomplete payload.

**Impact**: CLI operates on stale/incomplete data, missing any updates made after the claim.

### 2. No Post-Execution Conflict Check

**Location**: `run_agent.py` `_sync_results_to_backend()` function (line 889-920)

**Issue**: CLI builds sync payload from local `job.json` and calls `sync_job_state()` without checking if backend state changed during execution.

**Impact**: Console cancel/update operations are overwritten by CLI's stale local state.

### 3. Backend Allows Overwrite of Terminal States

**Location**: Backend API (not in this repo, but inferred from behavior)

**Issue**: `sync_job_state` endpoint accepts updates even when `run_status="stopped"` or `step_status="cancelled"`.

**Impact**: No server-side protection against overwriting terminal states.

---

## Correct Behavior Specification

### Pre-Execution: Sync Backend State to Local job.json

**When**: Daemon claims a job, before spawning CLI

**Steps**:
1. Daemon fetches full run state: `client.get_run(run_id)`
2. Daemon writes backend state to `request.json` (or passes via environment)
3. CLI loads this state into `job.json` instead of creating from scratch

**Implementation**:
```python
# daemon.py _spawn_child()
def _spawn_child(*, claim, ...):
    run = claim['run']
    run_id = run['id']
    
    # Fetch full backend state
    client = BackendClient(backend_url)
    run_detail = client.get_run(run_id=run_id)
    
    # Include full backend state in request_payload
    request_payload = _build_worker_request_payload(
        run=run, step_run=step_run, step_execution_spec=...,
        backend_state=run_detail,  # ← NEW: pass full backend state
        ...
    )
    
    # CLI will initialize job.json from backend_state
```

```python
# run_agent.py — CLI initialization
def _load_or_create_job_state(args):
    if args.mode == "daemon" and args.backend_state:
        # Initialize from backend state (daemon mode)
        state = _initialize_from_backend_state(args.backend_state)
    elif args.job_id:
        # Load existing job.json (manual mode or multi-step)
        state = load_job_state(args.job_id, ...)
    else:
        # Create new job.json (manual mode, first step)
        state = create_initial_job_state(...)
    return state
```

**Benefits**:
- CLI has latest backend state (including updates made between claim and spawn)
- CLI doesn't overwrite stale data
- Artifacts from previous steps are available

---

### Post-Execution: Check Backend Status Before Sync

**When**: CLI finishes execution, before calling `sync_job_state()`

**Steps**:
1. CLI fetches current backend state: `client.get_run(run_id)`
2. Check if backend state indicates cancellation or conflict:
   - `run_status="stopped"` or
   - `context_payload.__run_control.stop_requested=True` or
   - `step_status="cancelled"`
3. If conflict detected:
   - Log warning: "Backend state changed during execution, skipping sync"
   - Do NOT call `sync_job_state()`
   - Optionally sync with a "conflict" flag for audit trail

**Implementation**:
```python
# run_agent.py _sync_results_to_backend()
def _sync_results_to_backend(*, state, step_result, coder_used, backend_url):
    step_run_id = state.get("workflow_step_run_id")
    run_id = state.get("workflow_run_id")
    
    if not backend_url or not step_run_id:
        return
    
    try:
        from .backend_client import BackendClient
        client = BackendClient(backend_url)
        
        # Check backend status before sync
        run_detail = client.get_run(run_id=run_id)
        run = run_detail.get("run", {})
        run_status = run.get("run_status", "")
        context = run.get("context_payload", {})
        stop_requested = context.get("__run_control", {}).get("stop_requested", False)
        
        if run_status == "stopped" or stop_requested:
            print(
                f"[daemon-sync] Backend state changed during execution "
                f"(run_status={run_status}, stop_requested={stop_requested}), "
                f"skipping sync to preserve cancelled state",
                file=sys.stderr
            )
            return
        
        # Proceed with sync
        from .daemon_runtime import build_job_sync_payload
        result_dict = {
            "status": step_result.status,
            "outcome": step_result.status.lower(),
            "coder_used": coder_used,
            "remark": step_result.remark,
        }
        sync_payload = build_job_sync_payload(
            job=state, step_result=result_dict, step_run_id=step_run_id,
        )
        client.sync_job_state(step_run_id=step_run_id, payload=sync_payload)
        print(f"[daemon-sync] results synced to backend (step_run_id={step_run_id})", file=sys.stderr)
    except Exception as sync_exc:
        print(f"[daemon-sync] result sync failed: {sync_exc}", file=sys.stderr)
```

**Benefits**:
- Console cancel operations are preserved
- No overwriting of terminal states
- Clear audit trail of conflicts

---

## Implementation Plan

### Phase 1: Pre-Execution Backend Sync

**Files to Modify**:
- `agent_runner_v2/daemon.py` — fetch full backend state in `_spawn_child()`
- `agent_runner_v2/run_agent.py` — initialize `job.json` from backend state in daemon mode
- `agent_runner_v2/run_agent.py` — add `_initialize_from_backend_state()` function

**Tests**:
- `tests/unit/test_daemon_pre_execution_sync.py` — verify daemon fetches backend state
- `tests/unit/test_cli_backend_state_init.py` — verify CLI initializes from backend state

### Phase 2: Post-Execution Conflict Check

**Files to Modify**:
- `agent_runner_v2/run_agent.py` — check backend status before sync in `_sync_results_to_backend()`

**Tests**:
- `tests/unit/test_daemon_post_execution_conflict.py` — verify CLI skips sync when backend cancelled

### Phase 3: Backend-Side Protection (Optional, Backend Repo)

**Backend Changes**:
- `sync_job_state` endpoint should reject updates when `run_status="stopped"` or `step_status="cancelled"`
- Return 409 Conflict with current state
- CLI should handle 409 gracefully

---

## Summary Table

| Scenario | Current Behavior | Correct Behavior |
|----------|------------------|------------------|
| Cancel during execution | CLI overwrites cancelled state with completed | CLI checks backend status, skips sync if cancelled |
| Data update during execution | CLI overwrites updates with stale data | CLI fetches latest backend state before sync |
| Pre-execution state mismatch | CLI operates on incomplete data | Daemon fetches full backend state, passes to CLI |
| Double-sync race | Last write wins | Backend enforces single active step_run |
| Resume during execution | CLI may overwrite approval | CLI checks backend, adjusts sync |

---

## References

- **Daemon code**: `agent_runner_v2/daemon.py` lines 217-282 (`_spawn_child`)
- **CLI sync code**: `agent_runner_v2/run_agent.py` lines 889-920 (`_sync_results_to_backend`)
- **Console cancel code**: `agent_runner_v2/stop_commands.py` lines 20-90 (`main`)
- **Backend client**: `agent_runner_v2/backend_client.py` lines 170-180 (`claim_step`, `sync_job_state`, `get_run`)
- **Job state schema**: `agent_runner_v2/job_state.py` lines 0-100 (schema v6, `NON_TERMINAL_JOB_STATUSES`)
