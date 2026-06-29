from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import bundle_loader
from agent_runner_v2 import run_agent as run_agent_module


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


def test_bootstrap_root_is_packaged_with_template_groups():
    assert bundle_loader.BOOTSTRAP_ROOT.exists()
    assert (bundle_loader.BOOTSTRAP_ROOT / "template_groups.py").exists()
    assert (bundle_loader.BOOTSTRAP_ROOT / "prompts").exists()


def test_run_agent_resolves_global_workflow_bundle_root(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    global_root = tmp_path / "home" / ".ukbe-runner" / "workflows" / "default"
    global_root.mkdir(parents=True)
    monkeypatch.setattr(run_agent_module, 'resolve_workflow_root', lambda workspace_root_arg, workflow_name, config=None: global_root)

    resolved = run_agent_module._resolve_workflow_bundle_root(
        workspace_root,
        'default',
        {'default_workflow': 'default', 'workflows': {}},
    )

    assert resolved == global_root.resolve()


def test_ensure_delivery_folders_omits_master_prompts_and_adds_codebase_docs(tmp_path):
    target_root = tmp_path / "workspace"
    target_root.mkdir()

    run_agent_module._ensure_delivery_folders(target_root)

    assert not (target_root / "docs" / "delivery" / "07_master_prompts").exists()
    assert (target_root / "docs" / "codebase" / "00_standards").exists()
    assert (target_root / "docs" / "codebase" / "04_changes").exists()

