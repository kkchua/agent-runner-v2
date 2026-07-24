---
title: "Worker-Scoped Active Runs in Operator Console"
version: "1.1.0"
status: "implemented"
updated: "2026-07-24"
status: "implemented"
created: "2026-07-24"
author: "human + agent"`r`nupdated: "2026-07-24"
---

# Worker-Scoped Active Runs

## 1. Problem

The active runs listing is filtered by **repo + workflow**, forcing the user to
click through each repo and select each workflow individually to discover what
jobs are running. There is no single view of "what is running on this workstation".

## 2. Goal

Change the active runs listing to be **worker-scoped** — show all non-terminal
runs for the configured `worker_id` across all repos and workflows. The dropdown
display will include the workflow name so the user can identify each run.

## 3. Current Behavior

`refresh_active_runs()` (app.py ~line 420) calls:
```python
active_runs = backend_service.list_active_runs(
    repo_path=selected_repo_path(),
    workflow_name=workflow.workflow_name if workflow else None,
)
```

This requires a repo and workflow to be selected. The user must navigate
repo-by-repo, workflow-by-workflow to find active runs.

## 4. Solution Design

### 4.1 Backend: `list_active_runs_for_worker()`

The backend `list_runs()` API already supports `worker_id` filtering
(backend_client.py line 96-113). We add a new method to `BackendRunService`
that omits `repo_path` and `workflow_name`:

```python
def list_active_runs_for_worker(self) -> list[ActiveRunSummary]:
    """List all non-terminal runs for this worker across all repos and workflows."""
    payload = self.client.list_runs(
        status_group="non_terminal",
        worker_id=self.worker_id,
    )
    return _extract_runs(payload)
```

Also extract the run-coercion logic into a shared `_extract_runs()` helper
to avoid duplication between `list_active_runs()` and the new method.

### 4.2 UI: `refresh_active_runs()`

- Call `backend_service.list_active_runs_for_worker()` — no repo/workflow params.
- Dropdown display text includes workflow name for context:
  ```python
  text=f"[{run.workflow_name}] {run.run_code or run.run_id} | {run.status} | {run.current_step or '-'}"
  ```

### 4.3 UI: `update_visibility()`

- Active runs refresh triggers unconditionally when action needs active runs
  (Approve/Reject/Reset/Cancel), not gated by repo/workflow selection.

**Before:**
```python
if needs_active and repo_dd.value and workflow_dd.value:
    refresh_active_runs()
```

**After:**
```python
if needs_active:
    refresh_active_runs()
```

### 4.4 UI: `execute_action()` — Approve/Reset repo/workflow resolution

These actions currently require `repo_path` and `workflow` from dropdowns to
call `runner_service.approve_step()` / `runner_service.override_step()`. Since
runs are now worker-scoped, the user may not have the matching repo/workflow
selected.

**Resolution strategy:** Scan all configured repos for a matching `workflow_name`
from the selected run:

```python
def _resolve_repo_and_workflow(workflow_name: str) -> tuple[str, WorkflowEntry | None]:
    """Find the repo path and WorkflowEntry matching a workflow_name."""
    for repo in console_config.repos:
        for wf in repo.workflows:
            if wf.workflow_name == workflow_name:
                return repo.path, wf
    return "", None
```

For **Approve**: Use resolved repo_path + workflow to call both local
`runner_service.approve_step()` and backend `backend_service.approve_run()`.

For **Reset**: Use resolved repo_path + workflow to call both local
`runner_service.override_step()` and backend `backend_service.reset_run_step()`.

For **Reject / Cancel**: Backend-only already (no change needed).

### 4.5 UI: `execute_action()` — Submit unchanged

Submit still requires the user to select a repo and workflow from the dropdowns.
This is correct — you must specify what to submit.

## 5. Files to Modify

| File | Change |
|---|---|
| `operator_console/services/backend_service.py` | Add `list_active_runs_for_worker()`; extract `_extract_runs()` helper |
| `operator_console/app.py` | Update `refresh_active_runs()`, `update_visibility()`, `execute_action()`; add `_resolve_repo_and_workflow()` helper |
| `tests/unit/test_operator_console_services.py` | Add test for `list_active_runs_for_worker()` |

## 6. Step-by-Step Implementation

### Step 1: `backend_service.py` — Extract `_extract_runs()` and add worker-scoped method

1. Extract existing run extraction logic into `_extract_runs(payload)` helper.
2. Update `list_active_runs()` to use `_extract_runs()`.
3. Add `list_active_runs_for_worker()` that calls `client.list_runs(status_group="non_terminal", worker_id=...)`.

### Step 2: `app.py` — `refresh_active_runs()` worker-scoped

1. Replace `backend_service.list_active_runs(repo_path=..., workflow_name=...)` with `backend_service.list_active_runs_for_worker()`.
2. Remove `selected_repo_path()` and `selected_workflow()` calls from this function.
3. Update dropdown text to include `[run.workflow_name]` prefix.

### Step 3: `app.py` — `update_visibility()` unconditional refresh

1. Remove `repo_dd.value and workflow_dd.value` gate from the active runs refresh condition.

### Step 4: `app.py` — Add `_resolve_repo_and_workflow()` helper

1. Add function that scans `console_config.repos` for a matching `workflow_name`.
2. Returns `(repo_path, WorkflowEntry)` tuple.

### Step 5: `app.py` — `execute_action()` Approve/Reset resolution

1. For **Approve**: Use `_resolve_repo_and_workflow()` based on the selected run's `workflow_name` to get repo_path and workflow for local runner call.
2. For **Reset**: Same resolution approach.
3. For **Reject / Cancel**: No change (backend-only).

### Step 6: Tests

1. Add `test_backend_run_service_lists_active_runs_for_worker()` verifying:
   - Calls `list_runs` with only `status_group="non_terminal"` and `worker_id`.
   - Returns coerced `ActiveRunSummary` list.
2. Run all existing tests to verify no regressions.

## 7. Verification Checklist

1. **Launch console** → active runs dropdown shows all worker runs across repos.
2. **Dropdown entries** include `[workflow_name]` prefix for identification.
3. **Select Approve/Reject/Reset/Cancel** → active runs refresh without repo/workflow selected.
4. **Approve** works — repo/workflow resolved from run's `workflow_name`.
5. **Reset** works — repo/workflow resolved from run's `workflow_name`.
6. **Reject / Cancel** work (unchanged, backend-only).
7. **Submit** still requires repo/workflow selection (unchanged).
8. **Existing tests pass** — `.venv\Scripts\python -m pytest tests/unit/test_operator_console_services.py -v`

## 8. Key Design Decisions

| Decision | Rationale |
|---|---|
| Keep local runner calls for Approve/Reset | Local runner may need to update local state/files alongside backend approval |
| Resolve repo/workflow from run's workflow_name | User doesn't need to manually select the matching repo/workflow dropdown |
| Backend-only for Reject/Cancel | These actions don't need local runner involvement |
| Submit unchanged | You must specify what workflow to submit — dropdown selection is correct |
| Extract `_extract_runs()` helper | Avoids code duplication, follows SOP rule 3 |

## 9. SOP Rules Applied

1. Re-read files from disk before editing.
2. Verify current behavior before assuming API contracts.
3. Prefer extending shared modules (extract `_extract_runs()`).
4. Update tests alongside code changes.
5. When docs and code disagree, prefer active workflow files and current code.
6. Verify files exist and tests pass before returning success.
7. Use `.venv\Scripts\python` for pytest.
8. All code must include docstrings (PEP 257).

