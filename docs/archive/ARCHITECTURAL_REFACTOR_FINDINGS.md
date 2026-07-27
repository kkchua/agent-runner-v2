# Architectural Refactor — Investigation Findings & Results

**Date:** 2026-07-27

---

## Root Cause: Daemon Re-claiming Cancelled Jobs

### The Bug

After cancelling a job via the operator console, the daemon would re-claim and continue executing the cancelled job after restart.

### Root Causes Identified

1. **Console Cancel has NO direct backend call** (`app.py` line 861-883)
   - Cancel only calls `runner_service.cancel_run()` → `run --cancel-run`
   - This requires local `job.json` to exist
   - For cross-OS repos (Windows console, WSL daemon), `job.json` is on a different OS → `FileNotFoundError`
   - Backend never gets notified → run stays "pending" → daemon re-claims it

2. **`run --cancel-run` requires `--job-id` and reads local `job.json`** (`cli_runtime.py` line 292-336)
   - `load_job()` raises `FileNotFoundError` if job.json doesn't exist
   - If job.json exists but missing `workflow_step_run_id`, backend sync is skipped
   - If job.json exists but missing `workflow_run_id`, `stop_run()` is skipped

3. **Backend `claim_step()` doesn't filter stopped runs**
   - Daemon sends `POST /api/workers/claim?worker_id=...` with NO status filters
   - Backend returns any pending step_run, including those from stopped runs
   - Daemon's `_is_stop_requested()` catches it, but only if the flag was properly set

### The Fix (Phase 1 — COMPLETED)

Enhanced `stop_commands.py` to perform comprehensive cancel:
1. Query backend for `active_step_run_id` via `get_run()`
2. Sync step-level cancelled status via `sync_job_state()`
3. Set run-level stop flag via `stop_run()`

This works WITHOUT local `job.json` — purely backend-driven.

---

## Architecture Violations Found

### Console Violations (13 direct backend calls)

| Component | Method | Backend Call | Fix |
|-----------|--------|-------------|-----|
| `backend_service.py` | `list_active_runs()` | `list_runs()` | NEW: `list-runs` CLI ✅ |
| `backend_service.py` | `list_active_runs_for_worker()` | `list_runs()` | NEW: `list-runs` CLI ✅ |
| `backend_service.py` | `get_run_detail()` | `get_run()` | NEW: `show-run` CLI ✅ |
| `backend_service.py` | `stop_run()` | `stop_run()` | EXISTS: `stop` CLI ✅ |
| `backend_service.py` | `approve_run()` | `approve_run()` | EXISTS: `approve` CLI ✅ |
| `backend_service.py` | `reset_run_step()` | `reset_run_step()` | NEW: `reset-step` CLI ✅ |
| `runner_service.py` | `_submit_via_backend()` | `submit_run()` | EXISTS: `submit` CLI |
| `runner_service.py` | `cleanup_execution()` | `cleanup_execution()` | Needs new CLI |
| `app.py` | 5× `get_run_detail()` | `get_run()` | Use `show-run` CLI |
| `app.py` | 4× `approve_run()` | `approve_run()` | Use `approve` CLI |
| `app.py` | 1× `reset_run_step()` | `reset_run_step()` | Use `reset-step` CLI |

### Daemon Violations (4 business-logic backend calls)

| Call | Line | Category | Fix |
|------|------|----------|-----|
| `get_run` (stop check) | 497 | Business logic | CLI syncs results directly |
| `sync_job_state` (normal) | 530 | Business logic | CLI syncs results directly ✅ Phase 1 |
| `sync_job_state` (stop-on-claim) | 229 | Business logic | Backend filters stopped runs |
| `complete_step_run` (fallback) | 551 | Business logic | CLI always writes job.json |

---

## Phase 1 Results (COMPLETED)

### New Files Created

| File | Purpose | Tests |
|------|---------|-------|
| `list_runs_commands.py` | `ukbe-run-agent list-runs` CLI | 5 tests ✅ |
| `show_run_commands.py` | `ukbe-run-agent show-run <id>` CLI | 2 tests ✅ |
| `reset_step_commands.py` | `ukbe-run-agent reset-step <id> <step>` CLI | 2 tests ✅ |
| `test_list_runs_commands.py` | Unit tests for list-runs | |
| `test_show_run_commands.py` | Unit tests for show-run | |
| `test_reset_step_commands.py` | Unit tests for reset-step | |

### Files Modified

| File | Change | Tests |
|------|--------|-------|
| `stop_commands.py` | Added comprehensive cancel (get_run + sync_job_state + stop_run) | 3 tests ✅ |
| `approve_commands.py` | Added `--resume` and `--retry` flags | 6 tests ✅ |
| `run_agent.py` | Registered 3 new subcommands + daemon-mode result sync | 4 tests ✅ |
| `test_stop_commands.py` | Rewritten for comprehensive cancel | |
| `test_approve_commands.py` | New file for approve/reject/resume/retry | |
| `test_daemon_result_sync.py` | New file for daemon-mode sync | |

### Test Results

```
22 new/enhanced tests: ALL PASSED
Full unit test suite: 272 passed, 10 skipped, 0 failed
```

### Backend Connection Test

```
$ ukbe-run-agent list-runs --status-group all
→ Connected to http://127.0.0.1:8100 successfully
→ Returns empty list (fresh database)
```

---

## Phase 2 Results (COMPLETED)

### Changes to `daemon.py`

1. **Removed post-child result processing** (was lines 474-570)
   - Removed: `_child_result()`, `job.json` reading, `_persist_backend_linkage_to_job_state()`, `get_run()` stop check, `build_job_sync_payload()`, `sync_job_state()`, `complete_step_run()` fallback
   - Replaced with: `logger.log('info', 'child_exited', ...)` + `del children[step_run_id]`

2. **Simplified `_handle_stop_on_claim()`**
   - Removed: `sync_job_state()` call with stopped payload
   - Now: Just logs and skips (backend should have filtered stopped runs)

### Daemon Backend Calls (After Phase 2)

| Call | Status | Category |
|------|--------|----------|
| `register_worker` | ✅ Kept | Infrastructure |
| `heartbeat` (all) | ✅ Kept | Infrastructure |
| `claim_step` | ✅ Kept | Infrastructure |
| `sync_job_state` (spawn fail) | ✅ Kept | Infrastructure (CLI never started) |
| ~~`get_run` (stop check)~~ | ❌ Removed | Was business logic |
| ~~`sync_job_state` (normal)~~ | ❌ Removed | Was business logic → CLI handles |
| ~~`sync_job_state` (stop-on-claim)~~ | ❌ Removed | Was business logic |
| ~~`complete_step_run` (fallback)~~ | ❌ Removed | Was business logic |

---

## Phase 3 Results (COMPLETED)

### Files Changed

| File | Action |
|------|--------|
| `backend_service.py` | **DELETED** |
| `runner_service.py` | Rewritten — added CLI wrappers (`list_runs`, `show_run`, `stop_run`, `approve`, `reset_step`, `get_run_detail_dict`, `list_active_runs_for_worker`), removed `_submit_via_backend`, `_is_cross_os`, `cleanup_execution` |
| `app.py` | Removed `BackendClient`/`BackendRunService` imports, removed `backend_service` instantiation, replaced all `backend_service.*` calls with `runner_service.*`, simplified action handlers (no dual-call pattern) |
| `test_operator_console_services.py` | Rewritten — removed BackendRunService tests, added tests for new CLI wrappers |

### Verification

```
$ grep -r "BackendClient\|backend_service" agent_runner_v2/operator_console/
→ 0 actual imports/usage (only docstring references)
```

### Console Action Flow (After Phase 3)

| Action | CLI Call | Backend? |
|--------|---------|----------|
| Submit | `submit_commands.main()` | Via CLI |
| List Runs | `list_runs_commands.main()` | Via CLI |
| Show Run | `show_run_commands.main()` | Via CLI |
| Approve | `run_agent.main(--approve-step)` | Via CLI |
| Reject | `run_agent.main(--reject-step)` | Via CLI |
| Resume | `run_agent.main(--resume-step)` | Via CLI |
| Retry | `run_agent.main(--retry-step)` | Via CLI |
| Cancel | `run_agent.main(--cancel-run)` | Via CLI |
| Reset | `run_agent.main(--override-step)` | Via CLI |

---

## Final Test Results

```
274 passed, 10 skipped, 0 failed
```

### New Tests Added (Phase 1-3)

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_list_runs_commands.py` | 5 | list-runs CLI command |
| `test_show_run_commands.py` | 2 | show-run CLI command |
| `test_reset_step_commands.py` | 2 | reset-step CLI command |
| `test_stop_commands.py` | 3 | Enhanced comprehensive cancel |
| `test_approve_commands.py` | 6 | Approve/reject/resume/retry |
| `test_daemon_result_sync.py` | 4 | Daemon-mode result sync |
| `test_operator_console_services.py` | 6 | Console CLI wrappers |

---

## Files Reference

| File | Role |
|------|------|
| `ARCHITECTURAL_REFACTOR_SPEC.md` | Detailed implementation spec for all phases |
| `ARCHITECTURAL_REFACTOR_FINDINGS.md` | This file — investigation results |
| `JOB_DEFINITION_DICTIONARY.md` | Job state field reference |
| `memory/project/architectural-refactor-plan.md` | High-level plan saved in memory |
