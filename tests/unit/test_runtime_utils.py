from __future__ import annotations

from pathlib import Path

from agent_runner_v2.runtime_utils import safe_relative_to


def test_safe_relative_to_returns_absolute_path_for_cross_drive_windows_paths(monkeypatch):
    path = Path(r"D:\repo\prompts\01.txt")
    base = Path(r"C:\Users\kengk\.ukbe-runner")

    def _raise(_path, _base):  # noqa: ANN001
        raise ValueError("path is on mount 'D:', start on mount 'C:'")

    monkeypatch.setattr("agent_runner_v2.runtime_utils.os.path.relpath", _raise)
    assert safe_relative_to(path, base) == str(path)
