from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import bundle_loader


def test_init_workspace_seeds_global_example_and_not_repo_workflows(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")

    result = bundle_loader.init_workspace(tmp_path / "workspace")

    assert (fake_home / ".ukbe-runner" / "jobs").exists()
    assert (fake_home / ".ukbe-runner" / "logs").exists()
    assert (fake_home / ".ukbe-runner" / "runtime").exists()
    assert not (tmp_path / "workspace" / ".ukbe-runner" / "workflows").exists()
    assert (fake_home / ".ukbe-runner" / "workflows" / "example" / "template_groups.py").exists()
    assert result["workflow_root"] == str(fake_home / ".ukbe-runner" / "workflows" / "example")
    assert result["runner_home"] == str(fake_home / ".ukbe-runner")


def test_resolve_workflow_root_prefers_global_workflow(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    global_default = fake_home / ".ukbe-runner" / "workflows" / "default"
    global_default.mkdir(parents=True)

    resolved = bundle_loader.resolve_workflow_root(tmp_path / "workspace", "default", config={"workflows": {}})

    assert resolved == global_default.resolve()


def test_load_project_config_uses_global_config(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    cfg_path = fake_home / ".ukbe-runner" / "config.json"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text('{"default_workflow": "default", "workflows": {}}', encoding='utf-8')

    config = bundle_loader.load_project_config(tmp_path / "workspace")

    assert config["default_workflow"] == "default"
