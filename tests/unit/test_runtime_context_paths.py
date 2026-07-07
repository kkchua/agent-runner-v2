from __future__ import annotations

import json

from agent_runner_v2 import runtime_context


def test_resolve_repo_or_runtime_path_uses_global_runner_home_for_ukbe_runner_paths(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_home = tmp_path / "home" / ".ukbe-runner"
    runner_home.parent.mkdir()

    monkeypatch.setattr(runtime_context, "GLOBAL_RUNNER_HOME", runner_home)
    runtime_context.set_context(workspace_root=workspace)

    resolved = runtime_context.resolve_repo_or_runtime_path(
        ".ukbe-runner/jobs/demo/job-1/meta.json",
        project_root=workspace,
    )

    assert resolved == runner_home / "jobs" / "demo" / "job-1" / "meta.json"


def test_artifact_rel_to_meta_rel():
    assert runtime_context.artifact_rel_to_meta_rel("docs/delivery/01_initiatives/INIT-1.md") == "docs/delivery/01_initiatives/INIT-1.meta.json"
    assert runtime_context.artifact_rel_to_meta_rel("") == ""


def test_write_meta_sidecar_resolves_repo_relative_paths(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_home = tmp_path / "home" / ".ukbe-runner"
    runner_home.parent.mkdir()

    monkeypatch.setattr(runtime_context, "GLOBAL_RUNNER_HOME", runner_home)
    runtime_context.set_context(workspace_root=workspace)

    meta_path = runtime_context.write_meta_sidecar(
        "docs/delivery/01_initiatives/meta.json",
        project_root=workspace,
        status="APPROVED",
        remark="ok",
        artifacts={"A": "b"},
    )

    assert meta_path == workspace / "docs" / "delivery" / "01_initiatives" / "meta.json"
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    assert payload["coder_result"]["status"] == "APPROVED"
    assert payload["coder_result"]["artifacts"] == {"A": "b"}
