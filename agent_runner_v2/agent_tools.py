"""
agent_tools.py — Task coder tool functions.

Two operations:
  create_todos(job_id, todos)  → POST /api/task-coder/todos
  mark_complete(job_id, index, notes) → PUT /api/task-coder/{job_id}/complete

Calls the agent-runner-backend API. Falls back to local log if backend is down.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from urllib.request import urlopen, Request
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

BACKEND_URL = os.environ.get("AGENT_RUNNER_BACKEND", "http://localhost:8100")
LOG_FILE = Path(__file__).parent / "task_coder_events.log"

# Detect coder from environment if available
CODER = os.environ.get("AGENT_CODER", "unknown")


def _api(method: str, path: str, data: dict = None) -> dict:
    """Call backend API. Returns parsed JSON or None on failure."""
    if not HAS_URLLIB:
        return None
    try:
        url = f"{BACKEND_URL}{path}"
        body = json.dumps(data).encode("utf-8") if data else None
        req = Request(url, data=body, headers={"Content-Type": "application/json"} if body else {}, method=method)
        with urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _log_fallback(op: str, args: dict, result: dict = None):
    """Write to local log file when backend is unavailable."""
    entry = {
        "op": op,
        "args": args,
        "result": result,
        "coder": CODER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def create_todos(job_id: str, todos: list[str]):
    """Create one record per todo under this job. All start as pending."""
    payload = {"job_id": job_id, "todos": todos}
    if CODER != "unknown":
        payload["coder"] = CODER

    result = _api("POST", "/api/task-coder/todos", payload)
    if result:
        return result

    # Fallback: local log
    records = [{"todo_index": i + 1, "todo_text": t, "status": "pending"} for i, t in enumerate(todos)]
    _log_fallback("create_todos", {"job_id": job_id, "todos": todos}, {
        "inserted": len(todos),
        "records": records,
    })
    return {"status": "ok", "job_id": job_id, "inserted": len(todos), "records": records, "mode": "local"}


def mark_complete(job_id: str, todo_index: int, notes: str = ""):
    """Mark the todo at index as completed for this job."""
    payload = {"todo_index": todo_index, "notes": notes}
    if CODER != "unknown":
        payload["coder"] = CODER

    result = _api("PUT", f"/api/task-coder/{job_id}/complete", payload)
    if result:
        return result

    # Fallback: local log
    _log_fallback("mark_complete", {"job_id": job_id, "todo_index": todo_index, "notes": notes}, {
        "updated": todo_index,
        "status": "completed",
        "notes": notes,
    })
    return {"status": "ok", "job_id": job_id, "todo_index": todo_index, "mode": "local"}
