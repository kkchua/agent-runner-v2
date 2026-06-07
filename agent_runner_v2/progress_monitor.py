"""Progress monitor for LLM agent steps.

Tracks todo.md / progress.md files during coder invocation to provide
real-time visibility into what the LLM is working on.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Progress event types
# ---------------------------------------------------------------------------

@dataclass
class ProgressEvent:
    """A single progress event."""
    timestamp: float
    step: str
    coder: str
    event_type: str  # "todo_created", "todo_updated", "item_completed", "stalled"
    items_total: int
    items_done: int
    current_item: str = ""
    raw_content: str = ""
    message: str = ""


@dataclass
class ProgressState:
    """Current progress state for a step."""
    step: str
    coder: str
    items_total: int = 0
    items_done: int = 0
    items: list[dict[str, Any]] = field(default_factory=list)
    current_item: str = ""
    started_at: float = 0.0
    last_update: float = 0.0
    last_known_content: str = ""


# ---------------------------------------------------------------------------
# Parser — extracts todo state from LLM-written files
# ---------------------------------------------------------------------------

def parse_todo(content: str) -> ProgressState:
    """Parse a todo.md or progress.md file written by the LLM.

    Supports formats:
    - [ ] Task description
    - [x] Completed task
    - ~~Task~~ (strikethrough = done)
    - DONE: Task
    - PENDING: Task

    Returns ProgressState with parsed items.
    """
    state = ProgressState(step="", coder="", started_at=time.time(), last_update=time.time())
    state.raw_content = content

    # Match todo items: [ ] or [x] or [X] or ~~text~~ or DONE:/PENDING:
    patterns = [
        (r'- \[([ xX])\]\s+(.+)', 'checkbox'),  # - [ ] or - [x]
        (r'^\s*~~(.+?)~~\s*$', 'strikethrough'),  # ~~text~~
        (r'-?\s*DONE[:\s]+(.+)', 'done_prefix'),  # DONE: text
        (r'-?\s*PENDING[:\s]+(.+)', 'pending_prefix'),  # PENDING: text
    ]

    items = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        for pattern, fmt in patterns:
            m = re.match(pattern, line)
            if m:
                if fmt == 'checkbox':
                    done = m.group(1).lower() == 'x'
                    desc = m.group(2).strip()
                elif fmt == 'strikethrough':
                    done = True
                    desc = m.group(1).strip()
                elif fmt == 'done_prefix':
                    done = True
                    desc = m.group(1).strip()
                elif fmt == 'pending_prefix':
                    done = False
                    desc = m.group(1).strip()
                else:
                    continue

                items.append({"description": desc, "done": done})
                break

    state.items = items
    state.items_total = len(items)
    state.items_done = sum(1 for item in items if item["done"])

    # Find current (first incomplete) item
    for item in items:
        if not item["done"]:
            state.current_item = item["description"]
            break

    state.last_update = time.time()
    return state


def format_progress_summary(state: ProgressState) -> str:
    """Format a human-readable progress summary."""
    if state.items_total == 0:
        return f"[progress] step={state.step} coder={state.coder} no todo items found"

    pct = int((state.items_done / state.items_total * 100)) if state.items_total > 0 else 0
    status = "COMPLETE" if state.items_done == state.items_total else f"{state.items_done}/{state.items_total}"

    current = f" | working on: {state.current_item}" if state.current_item and state.items_done < state.items_total else ""

    return f"[progress] step={state.step} coder={state.coder} {status} ({pct}%){current}"


# ---------------------------------------------------------------------------
# Monitor — polls for progress files during coder invocation
# ---------------------------------------------------------------------------

class ProgressMonitor:
    """Monitors progress files during a coder invocation.

    Usage:
        monitor = ProgressMonitor(step="generate_sop", coder="claude", step_dir=step_dir)
        monitor.start()
        try:
            while not done:
                monitor.poll()
                time.sleep(3)
        finally:
            monitor.stop()
    """

    def __init__(
        self,
        *,
        step: str,
        coder: str,
        step_dir: Path | None = None,
        project_root: Path | None = None,
        poll_interval: float = 3.0,
        stall_threshold: float = 120.0,
    ):
        self.step = step
        self.coder = coder
        self.step_dir = step_dir
        self.project_root = project_root
        self.poll_interval = poll_interval
        self.stall_threshold = stall_threshold

        self._state = ProgressState(step=step, coder=coder, started_at=time.time())
        self._running = False
        self._events: list[ProgressEvent] = []
        self._last_content_hash = ""

    @property
    def state(self) -> ProgressState:
        return self._state

    @property
    def events(self) -> list[ProgressEvent]:
        return self._events

    def start(self) -> None:
        """Start monitoring."""
        self._running = True
        self._state.started_at = time.time()
        self._state.last_update = time.time()

    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False

    def poll(self) -> ProgressState | None:
        """Poll for progress updates. Returns new state if changed, None otherwise."""
        if not self._running:
            return None

        content = self._read_progress_file()
        if not content:
            return None

        # Check if content actually changed
        content_hash = hash(content)
        if content_hash == self._last_content_hash:
            # Check for stall
            if self._state.items_total > 0 and self._state.items_done < self._state.items_total:
                idle_time = time.time() - self._state.last_update
                if idle_time >= self.stall_threshold:
                    self._emit_event(
                        event_type="stalled",
                        message=f"No progress for {idle_time:.0f}s",
                    )
            return None

        self._last_content_hash = content_hash
        new_state = parse_todo(content)
        new_state.step = self.step
        new_state.coder = self.coder

        # Check if items completed
        prev_done = self._state.items_done
        new_done = new_state.items_done

        if new_done > prev_done:
            # Find newly completed items
            for item in new_state.items:
                if item["done"]:
                    desc = item["description"]
                    was_done = any(
                        i["description"] == desc and i["done"]
                        for i in self._state.items
                    )
                    if not was_done:
                        self._emit_event(
                            event_type="item_completed",
                            items_total=new_state.items_total,
                            items_done=new_state.items_done,
                            current_item=desc,
                            message=f"Completed: {desc}",
                        )

        self._state = new_state
        return new_state

    def summary(self) -> str:
        """Get current progress summary."""
        return format_progress_summary(self._state)

    def _read_progress_file(self) -> str | None:
        """Read progress file from step directory or project root."""
        # Check step directory first
        if self.step_dir:
            for name in ["todo.md", "progress.md", "TODO.md", "PROGRESS.md"]:
                path = self.step_dir / name
                if path.exists():
                    return path.read_text(encoding="utf-8")

        # Check project root
        if self.project_root:
            for name in ["todo.md", "progress.md"]:
                path = self.project_root / name
                if path.exists():
                    return path.read_text(encoding="utf-8")

        return None

    def _emit_event(self, *, event_type: str, message: str = "", **kwargs: Any) -> None:
        """Emit a progress event."""
        event = ProgressEvent(
            timestamp=time.time(),
            step=self.step,
            coder=self.coder,
            event_type=event_type,
            items_total=kwargs.get("items_total", self._state.items_total),
            items_done=kwargs.get("items_done", self._state.items_done),
            current_item=kwargs.get("current_item", self._state.current_item),
            raw_content=self._state.last_known_content,
            message=message,
        )
        self._events.append(event)

        # Print to console for visibility
        if event_type == "item_completed":
            print(f"[progress] ✓ {message}", flush=True)
        elif event_type == "todo_created":
            pct = (event.items_done / event.items_total * 100) if event.items_total > 0 else 0
            print(f"[progress] 📋 Todo created: {event.items_total} items", flush=True)
        elif event_type == "todo_updated":
            pct = (event.items_done / event.items_total * 100) if event.items_total > 0 else 0
            print(f"[progress] 📝 Todo updated: {event.items_done}/{event.items_total} ({pct:.0f}%)", flush=True)
        elif event_type == "stalled":
            print(f"[progress] ⚠️ {message}", flush=True)
