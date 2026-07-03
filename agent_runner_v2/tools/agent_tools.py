"""
agent_tools.py — Task coder tool functions for agent-runner steps.

Two operations:
  create_todos(step_id, todos)        → records all todo items as pending
  mark_complete(step_id, index, notes) → marks a todo item as completed

Writes append-only JSON lines to the file at PROGRESS_FILE env var.
Also POSTs to the backend API when BACKEND_URL and WORKFLOW_STEP_RUN_ID are set.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROGRESS_FILE = Path(os.environ.get("PROGRESS_FILE", "progress.jsonl"))
BACKEND_URL = os.environ.get("BACKEND_URL", "").rstrip("/")
STEP_RUN_ID = os.environ.get("WORKFLOW_STEP_RUN_ID", "")


def _write(step: str, index: int, item: str, status: str, notes: str = "") -> None:
    record: dict = {
        "step": step,
        "index": index,
        "item": item,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if notes:
        record["notes"] = notes
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _post_progress(step: str, index: int, item: str, status: str, notes: str = "") -> None:
    if not BACKEND_URL or not STEP_RUN_ID:
        return
    try:
        payload = json.dumps({
            "step_name": step,
            "todo_index": index,
            "item": item,
            "status": status,
            "notes": notes or None,
        }).encode()
        req = urllib.request.Request(
            f"{BACKEND_URL}/api/step-runs/{STEP_RUN_ID}/progress",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as exc:
        print(
            f"[agent_tools] warning: backend progress update failed for step={step!r} "
            f"index={index} status={status!r}: {exc}",
            file=sys.stderr,
            flush=True,
        )


def create_todos(step_id: str, todos: list) -> dict:
    """Register all todo items for this step. All start as pending."""
    for i, todo in enumerate(todos, start=1):
        _write(step_id, i, todo, "pending")      # file write MUST succeed
        _post_progress(step_id, i, todo, "pending")  # DB post is best-effort
    return {"status": "ok", "step_id": step_id, "inserted": len(todos)}


def mark_complete(step_id: str, todo_index: int, notes: str = "") -> dict:
    """Mark the todo at 1-based index as completed, resolving the original item description."""
    item = f"item-{todo_index}"
    try:
        if PROGRESS_FILE.exists():
            for line in PROGRESS_FILE.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                if rec.get("index") == todo_index and rec.get("status") == "pending":
                    item = rec.get("item", item)
                    break
    except Exception:
        pass
    _write(step_id, todo_index, item, "done", notes=notes)      # file write MUST succeed
    _post_progress(step_id, todo_index, item, "done", notes=notes)  # DB post is best-effort
    return {"status": "ok", "step_id": step_id, "todo_index": todo_index}
