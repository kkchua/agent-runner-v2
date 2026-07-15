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
    assert runtime_context.artifact_rel_to_meta_rel("docs/repo/delivery/01_initiatives/INIT-1.md") == "docs/repo/delivery/01_initiatives/INIT-1.meta.json"
    assert runtime_context.artifact_rel_to_meta_rel("") == ""


def test_write_meta_sidecar_resolves_repo_relative_paths(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_home = tmp_path / "home" / ".ukbe-runner"
    runner_home.parent.mkdir()

    monkeypatch.setattr(runtime_context, "GLOBAL_RUNNER_HOME", runner_home)
    runtime_context.set_context(workspace_root=workspace)

    meta_path = runtime_context.write_meta_sidecar(
        "docs/repo/delivery/01_initiatives/meta.json",
        project_root=workspace,
        status="APPROVED",
        remark="ok",
        artifacts={"A": "b"},
    )

    assert meta_path == workspace / "docs" / "repo" / "delivery" / "01_initiatives" / "meta.json"
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    assert payload["coder_result"]["status"] == "APPROVED"
    assert payload["coder_result"]["artifacts"] == {"A": "b"}


def test_format_report_path_resolves_repo_relative_paths(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_home = tmp_path / "home" / ".ukbe-runner"
    runner_home.parent.mkdir()

    monkeypatch.setattr(runtime_context, "GLOBAL_RUNNER_HOME", runner_home)
    runtime_context.set_context(workspace_root=workspace)

    resolved = runtime_context.format_report_path(
        "docs/system/00_governance/bootstrap/README.md",
        project_root=workspace,
    )

    assert resolved == str((workspace / "docs" / "system" / "00_governance" / "bootstrap" / "README.md").resolve())


def test_format_report_artifacts_normalizes_repo_and_runtime_paths(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_home = tmp_path / "home" / ".ukbe-runner"
    runner_home.parent.mkdir()

    monkeypatch.setattr(runtime_context, "GLOBAL_RUNNER_HOME", runner_home)
    runtime_context.set_context(workspace_root=workspace)

    artifacts = runtime_context.format_report_artifacts(
        {
            "DOC": "docs/system/00_governance/bootstrap/README.md",
            "META": ".ukbe-runner/jobs/demo/job-1/meta.json",
            "RAW": "artifacts/step-1/output.md",
        },
        project_root=workspace,
        runtime_root=runner_home,
    )

    assert artifacts["DOC"] == str((workspace / "docs" / "system" / "00_governance" / "bootstrap" / "README.md").resolve())
    assert artifacts["META"] == str((runner_home / "jobs" / "demo" / "job-1" / "meta.json").resolve())
    assert artifacts["RAW"] == "artifacts/step-1/output.md"


def test_format_report_artifacts_preserves_none_values(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_home = tmp_path / "home" / ".ukbe-runner"
    runner_home.parent.mkdir()

    monkeypatch.setattr(runtime_context, "GLOBAL_RUNNER_HOME", runner_home)
    runtime_context.set_context(workspace_root=workspace)

    artifacts = runtime_context.format_report_artifacts(
        {
            "EMPTY": None,
            "DOC": "docs/system/00_governance/bootstrap/README.md",
        },
        project_root=workspace,
        runtime_root=runner_home,
    )

    assert artifacts["EMPTY"] is None
    assert artifacts["DOC"] == str((workspace / "docs" / "system" / "00_governance" / "bootstrap" / "README.md").resolve())
