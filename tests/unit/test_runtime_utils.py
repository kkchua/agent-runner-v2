from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import runtime_utils


def test_runtime_utils_save_json_and_text(tmp_path: Path) -> None:
    json_path = tmp_path / "nested" / "data.json"
    text_path = tmp_path / "nested" / "note.txt"

    runtime_utils.save_json(json_path, {"ok": True})
    runtime_utils.save_text(text_path, "hello")

    assert json_path.read_text(encoding="utf-8").strip().startswith("{")
    assert text_path.read_text(encoding="utf-8") == "hello"


def test_runtime_utils_safe_relative_to(tmp_path: Path) -> None:
    base = tmp_path / "base"
    path = base / "child" / "file.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")

    assert runtime_utils.safe_relative_to(path, base) == "child\\file.txt"


def test_runtime_utils_now_iso_shape() -> None:
    value = runtime_utils.now_iso()

    assert "T" in value
    assert len(value) >= 19
