# Architectural Refactor — Detailed Implementation Spec

**Date:** 2026-07-27
**Status:** PLANNED
**Plan saved to:** `memory/project/architectural-refactor-plan.md`

## Architecture Principle

```
Console (Control Panel) → CLI (brain) → Backend (database)
Daemon  (messenger)     → CLI (brain) → Backend (database)
```

- **Backend**: No logic. Database persistence only.
- **Console**: UI only. ALL operations through CLI. Zero direct backend calls.
- **Daemon**: Messenger. Claims work, spawns CLI, monitors liveness. No business logic.
- **CLI**: The brain. All logic, all backend API calls, all state transitions.

---

# Phase 1: CLI + Backend — Build the Foundation

## 1a. New CLI Command: `list-runs`

**File:** `agent_runner_v2/list_runs_commands.py` (NEW)

**CLI usage:**
```
ukbe-run-agent list-runs [--worker-id X] [--status-group non_terminal|terminal|all] [--workflow-name X]
```

**Pattern:** Follows `stop_commands.py` structure exactly.

```python
"""List workflow runs from the backend."""
from __future__ import annotations

import argparse
import json
import os
import sys

from .backend_client import BackendClient
from .config_loader import load_runner_config


def _load_config() -> dict:
    return load_runner_config()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent list-runs",
        description="List workflow runs from the backend.",
    )
    p.add_argument("--worker-id", default="", help="Filter by worker ID.")
    p.add_argument("--status-group", default="non_terminal",
                   choices=["non_terminal", "terminal", "all"],
                   help="Status group filter (default: non_terminal).")
    p.add_argument("--workflow-name", default="", help="Filter by workflow name.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    client = BackendClient(backend_url)
    try:
        result = client.list_runs(
            status_group=args.status_group if args.status_group != "all" else None,
            worker_id=args.worker_id or None,
            workflow_name=args.workflow_name or None,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
```

**Registration in `run_agent.py`** (add alongside existing subcommand dispatch):
```python
if command == "list-runs":
    ns = argparse.Namespace()
    ns.command = "list-runs"
    ns.list_runs_argv = raw[1:]
    return ns
```

**Dispatch in `main()`** (add alongside existing command dispatch):
```python
if args.command == "list-runs":
    from .list_runs_commands import main as _list_runs_main
    return _list_runs_main(args.list_runs_argv)
```

**Unit test:** `tests/unit/test_list_runs_commands.py`
```python
from __future__ import annotations
import json
from agent_runner_v2 import list_runs_commands

class _FakeBackendClient:
    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url
    def list_runs(self, **kwargs):
        return {"runs": [{"id": "run-1", "status": "pending"}], "kwargs": kwargs}

def test_list_runs_default(monkeypatch, capsys) -> None:
    monkeypatch.setattr(list_runs_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(list_runs_commands, "_load_config",
                        lambda: {"backend_url": "http://127.0.0.1:8100"})
    exit_code = list_runs_commands.main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["runs"][0]["id"] == "run-1"

def test_list_runs_with_worker_filter(monkeypatch, capsys) -> None:
    monkeypatch.setattr(list_runs_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(list_runs_commands, "_load_config",
                        lambda: {"backend_url": "http://127.0.0.1:8100"})
    exit_code = list_runs_commands.main(["--worker-id", "worker-01"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["worker_id"] == "worker-01"
```

---

## 1b. New CLI Command: `show-run`

**File:** `agent_runner_v2/show_run_commands.py` (NEW)

**CLI usage:**
```
ukbe-run-agent show-run <run_id>
```

```python
"""Show a single workflow run's details from the backend."""
from __future__ import annotations

import argparse
import json
import os
import sys

from .backend_client import BackendClient
from .config_loader import load_runner_config


def _load_config() -> dict:
    return load_runner_config()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent show-run",
        description="Show a single workflow run's details from the backend.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to show.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    client = BackendClient(backend_url)
    try:
        result = client.get_run(run_id=args.run_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
```

**Registration:** Same pattern as `list-runs` — add to `parse_args()` and `main()`.

**Unit test:** `tests/unit/test_show_run_commands.py`
```python
from __future__ import annotations
import json
from agent_runner_v2 import show_run_commands

class _FakeBackendClient:
    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url
    def get_run(self, *, run_id):
        return {"run": {"id": run_id, "run_code": "JOB-001", "run_status": "pending",
                        "awaiting_human_step": "generate_prompts", "workflow_name": "agnes_media_gen_v1"}}

def test_show_run(monkeypatch, capsys) -> None:
    monkeypatch.setattr(show_run_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(show_run_commands, "_load_config",
                        lambda: {"backend_url": "http://127.0.0.1:8100"})
    exit_code = show_run_commands.main(["run-uuid-123"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["run"]["id"] == "run-uuid-123"
    assert payload["run"]["run_code"] == "JOB-001"
```

---

## 1c. New CLI Command: `reset-step`

**File:** `agent_runner_v2/reset_step_commands.py` (NEW)

**CLI usage:**
```
ukbe-run-agent reset-step <run_id> <step_name>
```

```python
"""Reset a run's current step to a different step."""
from __future__ import annotations

import argparse
import json
import os
import sys

from .backend_client import BackendClient
from .config_loader import load_runner_config


def _load_config() -> dict:
    return load_runner_config()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent reset-step",
        description="Reset a run's current step to a different step.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to reset.")
    p.add_argument("step_name", help="Target step name.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    client = BackendClient(backend_url)
    try:
        result = client.reset_run_step(run_id=args.run_id, step_name=args.step_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
```

**Registration + Unit test:** Same pattern as above.

---

## 1d. Enhance `stop_commands.py` — Comprehensive Cancel

**Current:** Only calls `client.stop_run()`.
**Enhanced:** Also calls `client.sync_job_state()` to set step-level cancelled status.

**Changes:**
```python
def main(argv: list[str] | None = None) -> int:
    # ... existing arg parsing ...
    client = BackendClient(backend_url)
    try:
        # Step 1: Query run to get active step_run_id
        run_detail = client.get_run(run_id=args.run_id)
        run = run_detail.get("run") or {}
        step_run_id = str(run.get("active_step_run_id") or "").strip()

        # Step 2: Sync step-level cancelled status (if we have a step_run_id)
        if step_run_id:
            client.sync_job_state(
                step_run_id=step_run_id,
                payload={
                    "run_status": "stopped",
                    "step_status": "cancelled",
                    "step_outcome": "cancelled",
                    "step_coder": None,
                    "step_duration_seconds": 0,
                    "next_step_name": None,
                    "output_payload": {},
                    "error_message": "Cancelled by operator",
                    "review": None,
                    "artifacts": [],
                    "context_payload": {"__run_control": {"stop_requested": True}},
                    "events": [{"event_type": "RUN_STOPPED",
                                "message": f"Run {args.run_id} cancelled by operator"}],
                },
            )

        # Step 3: Set run-level stop flag
        result = client.stop_run(
            run_id=args.run_id,
            reason=args.reason or None,
            mode="after_current_step",
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
```

**Note:** The `run_detail` response must include `active_step_run_id`. If the backend doesn't provide this field, the CLI falls back to just calling `stop_run()` (step 3 only). The backend change to provide this field is in Phase 1d (backend).

**Updated unit test:**
```python
class _FakeBackendClient:
    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url
        self.stop_called = False
        self.sync_called = False

    def get_run(self, *, run_id):
        return {"run": {"id": run_id, "active_step_run_id": "step-run-abc"}}

    def sync_job_state(self, *, step_run_id, payload):
        self.sync_called = True
        self.sync_payload = payload
        return {"status": "ok"}

    def stop_run(self, **kwargs):
        self.stop_called = True
        return {"status": "ok", "kwargs": kwargs}

def test_stop_comprehensive_cancel(monkeypatch, capsys) -> None:
    fake_client = _FakeBackendClient(None)
    monkeypatch.setattr(stop_commands, "BackendClient", lambda url: fake_client)
    monkeypatch.setattr(stop_commands, "_load_config",
                        lambda: {"backend_url": "http://127.0.0.1:8100"})
    exit_code = stop_commands.main(["run-1", "--reason", "Cancelled"])
    assert exit_code == 0
    assert fake_client.sync_called
    assert fake_client.sync_payload["run_status"] == "stopped"
    assert fake_client.stop_called
```

---

## 1e. Enhance `approve_commands.py` — Add --resume and --retry

**Current flags:** `--reject`, `--feedback`, `--outcome`
**New flags:** `--resume`, `--retry`

**Changes:**
```python
p.add_argument("--resume", action="store_true", default=False,
               help="Resume a step waiting for intervention (force-approve + advance).")
p.add_argument("--retry", action="store_true", default=False,
               help="Retry a step (reset counts, re-execute).")
```

**Behavior:**
- `--resume`: Sends `action="approve"` with `feedback="Resumed by operator"`
- `--retry`: Sends `action="approve"` with `feedback="Retried by operator"`
- These are backend-level signals. The actual resume/retry logic is handled by the daemon/CLI when it picks up the run next.

**Updated unit test:**
```python
def test_approve_resume(monkeypatch, capsys) -> None:
    monkeypatch.setattr(approve_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(approve_commands, "_load_config",
                        lambda: {"backend_url": "http://127.0.0.1:8100"})
    exit_code = approve_commands.main(["run-1", "--resume"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["action"] == "approve"
    assert payload["kwargs"]["feedback"] == "Resumed by operator"

def test_approve_retry(monkeypatch, capsys) -> None:
    monkeypatch.setattr(approve_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(approve_commands, "_load_config",
                        lambda: {"backend_url": "http://127.0.0.1:8100"})
    exit_code = approve_commands.main(["run-1", "--retry"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["action"] == "approve"
    assert payload["kwargs"]["feedback"] == "Retried by operator"
```

---

## 1f. CLI Daemon-Mode Result Sync

**File:** `agent_runner_v2/run_agent.py` — in the `run` command handler, after `execute_routed_step()` completes.

**What:** When running in daemon mode (`--mode daemon`), after step execution completes and job.json is saved, the CLI syncs results to the backend.

**Where to add:** After the existing result-saving block (~line 830-850 in run_agent.py), add:

```python
# Daemon mode: sync results to backend
if args.mode == "daemon" and state.get("workflow_step_run_id"):
    from .daemon_runtime import build_job_sync_payload
    from .backend_client import BackendClient

    backend_url = os.environ.get("AGENT_RUNNER_BACKEND_URL") or ""
    step_run_id = str(state["workflow_step_run_id"]).strip()
    if backend_url and step_run_id:
        try:
            result_dict = {
                "status": step_result.status,
                "outcome": step_result.status.lower(),
                "coder_used": coder_used,
                "remark": step_result.remark,
            }
            sync_payload = build_job_sync_payload(
                job=state, step_result=result_dict, step_run_id=step_run_id,
            )
            client = BackendClient(backend_url)
            client.sync_job_state(step_run_id=step_run_id, payload=sync_payload)
        except Exception as sync_exc:
            print(f"[daemon-sync] result sync failed: {sync_exc}", file=sys.stderr)
```

**Unit test:** `tests/unit/test_daemon_result_sync.py`
- Mock `BackendClient` and verify `sync_job_state` is called after daemon-mode execution
- Verify it's NOT called in manual mode
- Verify it's NOT called when `workflow_step_run_id` is empty

---

## 1g. Backend Changes (Separate Repo: agent-runner-backend)

| Endpoint | Change |
|----------|--------|
| `POST /api/workers/claim` | Filter out runs where `run_status = 'stopped'` or `context_payload.__run_control.stop_requested = True` |
| `POST /api/runs/{id}/stop` | Set `run_status = 'stopped'` in addition to setting `__run_control.stop_requested` flag |
| `GET /api/runs/{id}` | Include `active_step_run_id` field (the step_run currently being processed or next to process) |

---

# Phase 2: Daemon — Move Result Sync to CLI, Simplify

## 2a. Remove Post-Child Result Processing

**File:** `agent_runner_v2/daemon.py`

**Current flow (after child exits, ~lines 474-570):**
1. Read result.json ← REMOVE
2. Read job.json ← REMOVE
3. Persist backend linkage ← REMOVE
4. Check stop_requested via get_run ← REMOVE
5. Build sync payload ← REMOVE
6. Sync to backend ← REMOVE
7. Log + cleanup ← KEEP

**New flow:**
```python
child.exit_code = proc_rc
logger.log('info', 'child_exited', message='child finished',
           child=child, details={'exit_code': proc_rc})
del children[step_run_id]
```

## 2b. Remove _handle_stop_on_claim

**Remove:** `_handle_stop_on_claim()` function and its call site.

**Why:** The backend's claim endpoint now filters stopped runs (Phase 1g). If a stopped run somehow gets through, the daemon's `_is_stop_requested()` check still catches it — but instead of calling `sync_job_state`, it just skips (logs and continues).

**Replace with:**
```python
if _is_stop_requested(claim['run']):
    run_code = claim['run'].get('run_code', '')
    logger.log('info', 'stop_requested_on_claim',
               message=f"Stop requested for run {run_code}, skipping",
               details={"run_id": claim['run'].get('id')})
    continue  # Skip this claim, backend should not have returned it
```

## 2c. Remove get_run Stop Check

**Remove:** Lines 495-507 (the `client.get_run()` call after child exit).

**Why:** The CLI now syncs results itself (Phase 1f). The daemon doesn't need to re-check stop status.

## 2d. Keep Spawn-Failure Sync

**Keep:** `sync_job_state` for spawn failures (~line 590). This must stay because the CLI never started — there's no subprocess to handle it.

## 2e. What Remains in Daemon

| Function | Status |
|----------|--------|
| `_run_supervisor()` | KEEP — simplified |
| `_spawn_child()` | KEEP — unchanged |
| `_is_stop_requested()` | KEEP — safety net (log + skip) |
| `_handle_stop_on_claim()` | REMOVE |
| `_child_result()` | REMOVE |
| `_persist_backend_linkage_to_job_state()` | REMOVE |
| `register_worker` | KEEP |
| `heartbeat` (all) | KEEP |
| `claim_step` | KEEP |
| `sync_job_state` (spawn fail only) | KEEP |
| `get_run` | REMOVE |

## 2f. Unit Tests

- Test that daemon does NOT call `sync_job_state` after normal child exit
- Test that daemon DOES call `sync_job_state` when spawn fails
- Test that `_is_stop_requested()` still detects stop flag and skips

---

# Phase 3: Operator Console — Switch to CLI-Only

## 3a. Delete `backend_service.py`

**File:** `agent_runner_v2/operator_console/services/backend_service.py` → DELETE

All 6 methods replaced by CLI commands:
| Method | Replaced by |
|--------|------------|
| `list_active_runs()` | `runner_service.list_runs()` → `list-runs` CLI |
| `list_active_runs_for_worker()` | `runner_service.list_runs()` → `list-runs --worker-id` CLI |
| `get_run_detail()` | `runner_service.show_run()` → `show-run` CLI |
| `stop_run()` | `runner_service.stop_run()` → `stop` CLI |
| `approve_run()` | `runner_service.approve()` → `approve` CLI |
| `reset_run_step()` | `runner_service.reset_step()` → `reset-step` CLI |

## 3b. Refactor `runner_service.py`

**Remove:**
- `_submit_via_backend()` method
- `_is_cross_os()` function
- `cleanup_execution()` method (uses BackendClient directly)
- All `--backend-url` arguments from `_invoke()` calls

**Add:**
```python
def list_runs(self, *, worker_id: str = "", status_group: str = "non_terminal",
              workflow_name: str = "") -> str:
    """List runs via CLI."""
    args = ["list-runs"]
    if worker_id:
        args.extend(["--worker-id", worker_id])
    if status_group != "all":
        args.extend(["--status-group", status_group])
    if workflow_name:
        args.extend(["--workflow-name", workflow_name])
    return self._invoke_from_anywhere(func=list_runs_commands.main, argv=args)

def show_run(self, *, run_id: str) -> str:
    """Show run detail via CLI."""
    args = ["show-run", run_id]
    return self._invoke_from_anywhere(func=show_run_commands.main, argv=args)

def stop_run(self, *, run_id: str, reason: str = "") -> str:
    """Stop/cancel a run via CLI."""
    args = ["stop", run_id]
    if reason:
        args.extend(["--reason", reason])
    return self._invoke_from_anywhere(func=stop_commands.main, argv=args)

def approve(self, *, run_id: str, reject: bool = False, feedback: str = "",
            resume: bool = False, retry: bool = False) -> str:
    """Approve/reject/resume/retry via CLI."""
    args = ["approve", run_id]
    if reject:
        args.append("--reject")
    if resume:
        args.append("--resume")
    if retry:
        args.append("--retry")
    if feedback:
        args.extend(["--feedback", feedback])
    return self._invoke_from_anywhere(func=approve_commands.main, argv=args)

def reset_step(self, *, run_id: str, step_name: str) -> str:
    """Reset step via CLI."""
    args = ["reset-step", run_id, step_name]
    return self._invoke_from_anywhere(func=reset_step_commands.main, argv=args)
```

**New `_invoke_from_anywhere()` method:**
```python
def _invoke_from_anywhere(
    self, *,
    func: Callable,
    argv: list[str],
) -> str:
    """Execute a CLI function without chdir (for backend API wrapper commands)."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = 1
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = func(argv)
    except Exception as exc:
        raise ActionExecutionError(str(exc)) from exc

    rendered = stdout.getvalue().strip()
    error_text = stderr.getvalue().strip()
    if exit_code != 0:
        raise ActionExecutionError(error_text or rendered or f"exit code {exit_code}")
    return rendered or error_text or "ok"
```

**Keep existing `_invoke()` for commands that need chdir** (like `submit_job` which uses cwd as project_root).

## 3c. Refactor `app.py`

**Replace all `backend_service.*` calls:**

| Current | New |
|---------|-----|
| `backend_service.list_active_runs_for_worker(worker_id=...)` | `runner_service.list_runs(worker_id=...)` |
| `backend_service.get_run_detail(run_id=...)` | `runner_service.show_run(run_id=...)` |
| `backend_service.approve_run(run_id=..., reject=False)` | `runner_service.approve(run_id=...)` |
| `backend_service.approve_run(run_id=..., reject=True)` | `runner_service.approve(run_id=..., reject=True)` |
| `backend_service.stop_run(run_id=...)` | `runner_service.stop_run(run_id=...)` |
| `backend_service.reset_run_step(run_id=..., step_name=...)` | `runner_service.reset_step(run_id=..., step_name=...)` |

**Simplify action handlers** — each action becomes a single CLI call instead of dual calls:

```python
elif action == "Cancel":
    run_id = str(selected_run_id or "").strip()
    if not run_id:
        raise ActionExecutionError("Select an active run to cancel.")
    rendered = runner_service.stop_run(run_id=run_id, reason="Cancelled by operator")

elif action == "Approve":
    run_id = str(selected_run_id or "").strip()
    if not run_id:
        raise ActionExecutionError("Select an active run to approve.")
    rendered = runner_service.approve(run_id=run_id)

elif action == "Reject":
    run_id = str(selected_run_id or "").strip()
    if not run_id:
        raise ActionExecutionError("Select an active run to reject.")
    rendered = runner_service.approve(run_id=run_id, reject=True, feedback=feedback_tf.value or "")
```

**Remove `backend_service` import and instantiation.**

## 3d. Remove Cross-OS Handling

**File:** `operator_console/config.py`
- Remove `_is_cross_os()` path normalization logic
- All repo paths stored as-is

**File:** `operator_console/services/runner_service.py`
- Remove `_is_cross_os()` function
- Remove `_submit_via_backend()` method
- `submit_job()` always uses `submit_commands.main()` via `_invoke()`

**File:** `operator_console/app.py`
- Remove cross-OS branching in file picker and input resolution
- Input paths always constructed as: `repo_path / subdirectory / filename`

---

# Phase 4: CLI Admin --run-id Support (Lower Priority)

## 4a. Add --run-id to cli_runtime.py Admin Commands

**File:** `agent_runner_v2/cli_runtime.py`

**Current:** All admin commands require `--job-id` and read local `job.json`.
**Enhanced:** Accept `--run-id` (backend UUID) as alternative. When provided, query backend for run data.

```python
if args.cancel_run:
    run_id = str(args.run_id or "").strip()
    job_id = str(args.job_id or "").strip()

    if run_id and not job_id:
        # Backend-first mode: query backend for run data
        backend_url = os.environ.get("AGENT_RUNNER_BACKEND_URL") or str(load_runner_config().get("backend_url") or "")
        if not backend_url:
            raise ValueError("--run-id requires backend_url in config.json")
        client = BackendClient(backend_url)
        run_detail = client.get_run(run_id=run_id)
        run = run_detail.get("run") or {}
        job_id = str(run.get("run_code") or "").strip()
        # ... proceed with job_id ...
```

**Same pattern for:** `--approve-step`, `--reject-step`, `--resume-step`, `--retry-step`, `--override-step`

---

# Verification Plan

## After Phase 1
```bash
# All new CLI commands work
.venv\Scripts\python -m agent_runner_v2.run_agent list-runs --worker-id my-worker-01
.venv\Scripts\python -m agent_runner_v2.run_agent show-run <run_id>
.venv\Scripts\python -m agent_runner_v2.run_agent stop <run_id> --reason "test"
.venv\Scripts\python -m agent_runner_v2.run_agent approve <run_id> --resume
.venv\Scripts\python -m agent_runner_v2.run_agent reset-step <run_id> <step_name>

# All unit tests pass
.venv\Scripts\python -m pytest tests/unit/test_list_runs_commands.py -v
.venv\Scripts\python -m pytest tests/unit/test_show_run_commands.py -v
.venv\Scripts\python -m pytest tests/unit/test_reset_step_commands.py -v
.venv\Scripts\python -m pytest tests/unit/test_stop_commands.py -v
.venv\Scripts\python -m pytest tests/unit/test_approve_commands.py -v
.venv\Scripts\python -m pytest tests/unit/test_daemon_result_sync.py -v
```

## After Phase 2
```bash
# Daemon does NOT call sync_job_state after normal exit (check daemon log)
# Daemon DOES call sync_job_state for spawn failures
.venv\Scripts\python -m pytest tests/unit/test_daemon*.py -v
```

## After Phase 3
```bash
# Zero BackendClient imports in console
grep -r "BackendClient" agent_runner_v2/operator_console/ → 0 matches

# Console actions work end-to-end
# Launch console, test each action: submit, list, approve, reject, cancel, reset
```

## Cancel Bug Verification
1. Submit job via console → Cancel via console
2. Check backend: `run_status = 'stopped'`
3. Restart daemon → verify it does NOT claim the cancelled run
