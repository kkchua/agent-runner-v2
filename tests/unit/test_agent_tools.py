from __future__ import annotations

import importlib
import json
from pathlib import Path


def _load_agent_tools(monkeypatch, progress_file: Path):
    monkeypatch.setenv("PROGRESS_FILE", str(progress_file))
    import agent_runner_v2.tools.agent_tools as agent_tools
    return importlib.reload(agent_tools)


def test_create_process_complete_flow(monkeypatch, tmp_path: Path):
    progress_file = tmp_path / "progress.jsonl"
    agent_tools = _load_agent_tools(monkeypatch, progress_file)

    agent_tools.create_todos("step_a", ["first task", "second task"])
    agent_tools.mark_process("step_a", 1, notes="started")
    agent_tools.mark_complete("step_a", 1, notes="finished")

    records = [json.loads(line) for line in progress_file.read_text(encoding="utf-8").splitlines()]
    assert [r["status"] for r in records] == ["pending", "pending", "processing", "completed"]
    assert records[0]["item"] == "first task"
    assert records[2]["item"] == "first task"
    assert records[3]["item"] == "first task"


def test_mark_complete_resolves_existing_item_without_pending_filter(monkeypatch, tmp_path: Path):
    progress_file = tmp_path / "progress.jsonl"
    agent_tools = _load_agent_tools(monkeypatch, progress_file)

    agent_tools.create_todos("step_b", ["only task"])
    agent_tools.mark_process("step_b", 1, notes="started")
    agent_tools.mark_complete("step_b", 1, notes="done")

    records = [json.loads(line) for line in progress_file.read_text(encoding="utf-8").splitlines()]
    assert records[-1]["status"] == "completed"
    assert records[-1]["item"] == "only task"


def test_backend_progress_posts_pending_processing_completed(monkeypatch, tmp_path: Path):
    progress_file = tmp_path / "progress.jsonl"
    monkeypatch.setenv("PROGRESS_FILE", str(progress_file))
    monkeypatch.setenv("BACKEND_URL", "http://backend.test")
    monkeypatch.setenv("WORKFLOW_STEP_RUN_ID", "step-run-123")
    import agent_runner_v2.tools.agent_tools as agent_tools
    agent_tools = importlib.reload(agent_tools)

    requests: list[dict[str, object]] = []

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def _fake_urlopen(req, timeout=0):
        requests.append({
            "url": req.full_url,
            "timeout": timeout,
            "payload": json.loads(req.data.decode("utf-8")),
            "content_type": req.get_header("Content-Type"),
        })
        return _Response()

    monkeypatch.setattr(agent_tools.urllib.request, "urlopen", _fake_urlopen)

    agent_tools.create_todos("step_c", ["task one"])
    agent_tools.mark_process("step_c", 1, notes="started")
    agent_tools.mark_complete("step_c", 1, notes="done")

    assert [req["payload"]["status"] for req in requests] == ["pending", "processing", "completed"]
    assert all(req["url"] == "http://backend.test/api/step-runs/step-run-123/progress" for req in requests)
    assert requests[0]["payload"]["item"] == "task one"
    assert requests[1]["payload"]["notes"] == "started"
    assert requests[2]["payload"]["notes"] == "done"
