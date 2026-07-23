"""
agent_tools.py — Task coder tool functions for agent-runner steps.

Three operations:
  create_todos(step_id, todos)         → records all todo items as pending
  mark_process(step_id, index, notes)  → marks a todo item as processing
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


def _resolve_todo_item(todo_index: int) -> str:
    item = f"item-{todo_index}"
    try:
        if PROGRESS_FILE.exists():
            for line in PROGRESS_FILE.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                if rec.get("index") == todo_index and rec.get("item"):
                    item = rec.get("item", item)
                    break
    except Exception:
        pass
    return item


def mark_process(step_id: str, todo_index: int, notes: str = "") -> dict:
    """Mark the todo at 1-based index as processing."""
    item = _resolve_todo_item(todo_index)
    _write(step_id, todo_index, item, "processing", notes=notes)
    _post_progress(step_id, todo_index, item, "processing", notes=notes)
    return {"status": "ok", "step_id": step_id, "todo_index": todo_index}


def mark_complete(step_id: str, todo_index: int, notes: str = "") -> dict:
    """Mark the todo at 1-based index as completed, resolving the original item description."""
    item = _resolve_todo_item(todo_index)
    _write(step_id, todo_index, item, "completed", notes=notes)      # file write MUST succeed
    _post_progress(step_id, todo_index, item, "completed", notes=notes)  # DB post is best-effort
    return {"status": "ok", "step_id": step_id, "todo_index": todo_index}


# =============================================================================
# ASCII Sanitization Tools
# =============================================================================

def sanitize_ascii(text: str) -> str:
    """Replace common non-ASCII characters with ASCII equivalents.

    Call this before writing documentation files to ensure ASCII-only content.

    Args:
        text: Input text that may contain non-ASCII characters.

    Returns:
        Text with common non-ASCII characters replaced by ASCII equivalents.

    Usage (bash):
        python -c "from agent_tools import sanitize_ascii; print(sanitize_ascii('text with em-dash'))"
    """
    if not text:
        return text
    # Em-dash / en-dash to double hyphen
    text = text.replace("\u2014", "--")  # —
    text = text.replace("\u2013", "--")  # –
    # Curly quotes to straight quotes
    text = text.replace("\u201c", '"')   # "
    text = text.replace("\u201d", '"')   # "
    text = text.replace("\u2018", "'")   # '
    text = text.replace("\u2019", "'")   # '
    # Arrows
    text = text.replace("\u2192", "->")  # →
    text = text.replace("\u2190", "<-")  # ←
    # Bullets
    text = text.replace("\u2022", "*")   # •
    # Ellipsis
    text = text.replace("\u2026", "...")  # …
    # Private Use Area angle brackets (sometimes used by LLMs or fonts)
    text = text.replace("\ue000", "<")
    text = text.replace("\ue001", ">")
    text = text.replace("\uf03c", "<")  # PUA angle bracket < (font-specific)
    text = text.replace("\uf03e", ">")  # PUA angle bracket > (font-specific)
    # Catch-all: replace any remaining Private Use Area characters (U+E000-U+F8FF)
    import re as _re
    text = _re.sub(r"[\ue000-\uf8ff]", "", text)
    return text


def sanitize_ascii_file(file_path: str) -> dict:
    """Read a Markdown file, sanitize non-ASCII characters, and write it back.

    Only processes .md files. Refuses to touch JSON or other file types to
    prevent corruption of structured data (e.g. meta.json sidecars).

    Args:
        file_path: Path to the .md file to sanitize.

    Returns:
        Dict with status and number of replacements made.

    Usage (bash):
        python -c "from agent_tools import sanitize_ascii_file; sanitize_ascii_file('path/to/file.md')"
    """
    path = Path(file_path)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}

    if path.suffix.lower() != ".md":
        return {
            "status": "error",
            "message": f"Refusing to sanitize non-Markdown file: {file_path} (only .md files are allowed)",
        }

    try:
        content = path.read_text(encoding="utf-8")
        sanitized = sanitize_ascii(content)
        replacements = len(content) - len(sanitized)  # Approximate
        # Count actual character replacements more accurately
        replacements = sum(
            content.count(c)
            for c in "\u2014\u2013\u201c\u201d\u2018\u2019\u2192\u2190\u2022\u2026\ue000\ue001"
        )
        path.write_text(sanitized, encoding="utf-8")
        return {"status": "ok", "file": file_path, "replacements": replacements}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
