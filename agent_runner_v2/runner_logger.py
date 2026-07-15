"""Structured logger for the agent runner.

Provides both console output (colourised) and file logging (JSON-lines).
All events include: timestamp, step, coder, model, duration, status.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .runtime_context import RUNNER_HOME

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
_LOG_FILE: Path | None = None
_COLOURS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "dim": "\033[2m",
}
_COLOUR_SUPPORTED = sys.stdout.isatty()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _colour(text: str, name: str) -> str:
    if not _COLOUR_SUPPORTED:
        return text
    code = _COLOURS.get(name, "")
    return f"{code}{text}{_COLOURS['reset']}" if code else text


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("ascii", errors="replace"))
        sys.stdout.flush()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _log_dir() -> Path:
    return Path(RUNNER_HOME) / "logs"


def _ensure_log_file() -> Path | None:
    global _LOG_FILE
    if _LOG_FILE is not None:
        return _LOG_FILE
    try:
        d = _log_dir()
        d.mkdir(parents=True, exist_ok=True)
        _LOG_FILE = d / "runner.log"
        return _LOG_FILE
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_event(
    step: str,
    coder: str,
    *,
    model: str = "",
    model_id: str = "",
    connection: str = "",
    auth_type: str = "",
    event: str = "info",
    duration_ms: int | None = None,
    return_code: int | None = None,
    status: str = "",
    message: str = "",
) -> None:
    """Log one event to both console and file."""
    record: dict[str, Any] = {
        "timestamp": _now_iso(),
        "step": step,
        "coder": coder,
        "model": model or "",
        "model_id": model_id or "",
        "connection": connection or "",
        "auth_type": auth_type or "",
        "event": event,
    }
    if duration_ms is not None:
        record["duration_ms"] = duration_ms
    if return_code is not None:
        record["return_code"] = return_code
    if status:
        record["status"] = status
    if message:
        record["message"] = message

    _print_console(record)
    _write_file(record)


def log_invocation_start(
    step: str,
    coder: str,
    *,
    model: str = "",
    model_id: str = "",
    connection: str = "",
    auth_type: str = "",
    command: list[str] | None = None,
) -> None:
    """Log that a coder invocation is about to start."""
    model_name = model or "n/a"
    parts = [f"[{step}] invoking coder={coder}"]
    if connection:
        parts.append(f"connection={connection}")
    if model_id:
        parts.append(f"model_id={model_id}")
    parts.append(f"model={model_name}")
    parts.append(f"auth={auth_type or 'default'}")
    log_event(
        step,
        coder,
        model=model,
        model_id=model_id,
        connection=connection,
        auth_type=auth_type,
        event="invocation_start",
        message=" ".join(parts),
    )


def log_invocation_result(
    step: str,
    coder: str,
    *,
    model: str = "",
    model_id: str = "",
    connection: str = "",
    auth_type: str = "",
    return_code: int,
    duration_ms: int,
    status: str,
    message: str = "",
) -> None:
    """Log the result of a coder invocation."""
    status_label = f"rc={return_code} {status}"
    log_event(
        step,
        coder,
        model=model,
        model_id=model_id,
        connection=connection,
        auth_type=auth_type,
        event="invocation_result",
        return_code=return_code,
        duration_ms=duration_ms,
        status=status,
        message=message or (
            f"[{step}] result coder={coder}"
            f"{f' connection={connection}' if connection else ''}"
            f"{f' model_id={model_id}' if model_id else ''}"
            f" model={model or 'n/a'} {status_label} ({duration_ms}ms)"
        ),
    )


def log_error(
    step: str,
    coder: str,
    *,
    model: str = "",
    model_id: str = "",
    connection: str = "",
    auth_type: str = "",
    error: str = "",
) -> None:
    """Log a coder invocation error."""
    log_event(
        step,
        coder,
        model=model,
        model_id=model_id,
        connection=connection,
        auth_type=auth_type,
        event="error",
        status="ERROR",
        message=error or (
            f"[{step}] error coder={coder}"
            f"{f' connection={connection}' if connection else ''}"
            f"{f' model_id={model_id}' if model_id else ''}"
            f" model={model or 'n/a'}"
        ),
    )


def log_resolver(coder_input: str, resolved: str, *, is_alias: bool) -> None:
    """Log coder alias resolution."""
    if is_alias:
        msg = f"[resolver] '{coder_input}' -> resolved alias to '{resolved}'"
    else:
        msg = f"[resolver] '{coder_input}' -> using plain coder name"
    _safe_print(_colour(f"  {msg}", "dim"))


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def _print_console(record: dict[str, Any]) -> None:
    event = record.get("event", "")
    msg = record.get("message", "")
    if not msg:
        return

    if event == "invocation_start":
        _safe_print(_colour(msg, "cyan"))
    elif event == "invocation_result":
        _safe_print(_colour(msg, "green" if record.get("return_code") == 0 else "red"))
    elif event == "error":
        _safe_print(_colour(msg, "red"))
    else:
        _safe_print(msg)


# ---------------------------------------------------------------------------
# File output (JSON-lines)
# ---------------------------------------------------------------------------

def _write_file(record: dict[str, Any]) -> None:
    log_path = _ensure_log_file()
    if log_path is None:
        return
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass
