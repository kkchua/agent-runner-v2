from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import bundle_loader
from agent_runner_v2 import run_agent as run_agent_module
from conftest import load_bootstrap_workflow_module


def test_publish_bootstrap_bundle_copies_repo_bootstrap_docs_into_package_bundle(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    source_root = workspace_root / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Bootstrap\n", encoding="utf-8")
    (source_root / "templates" / "delivery").mkdir(parents=True, exist_ok=True)
    (source_root / "templates" / "delivery" / "01_delivery_template_registry.md").write_text("registry", encoding="utf-8")

    package_root = tmp_path / "package"
    expected_root = package_root / "bootstrap" / "bundles" / "core" / "current"
    bootstrap_workflows_root = package_root / "bootstrap" / "workflows" / "default"
    
    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_root)
    monkeypatch.setattr(bundle_loader, "BOOTSTRAP_ROOT", bootstrap_workflows_root)

    result = bundle_loader.publish_bootstrap_bundle(workspace_root)

    assert (expected_root / "README.md").exists()
    assert (expected_root / "templates" / "delivery" / "01_delivery_template_registry.md").exists()
    assert result["package_bootstrap_root"] == str(expected_root)
    assert result["bundle_name"] == "core"


def test_publish_bootstrap_bundle_generates_bundle_governance_adapters(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    source_root = workspace_root / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Bootstrap\n", encoding="utf-8")

    plugin_root = workspace_root / "workflows" / "sample_bundle"
    (plugin_root / "prompts").mkdir(parents=True, exist_ok=True)
    (plugin_root / "workflow.toml").write_text(
        "\n".join(
            [
                "[workflow]",
                'name = "sample_bundle"',
                'version = "1"',
                'label = "Sample Bundle"',
                'job_prefix = "SAMPLE"',
                "",
                "[workflow.init]",
                'step = "one"',
                'inputs = []',
                "",
                "[[step]]",
                'name = "one"',
                'action = "step_completion"',
            ]
        ),
        encoding="utf-8",
    )
    (plugin_root / "bundle_governance.toml").write_text(
        "\n".join(
            [
                "[governance]",
                'canonical_source = "bundle_governance/core.md"',
                'generated_dir = "bundle_governance/generated"',
                'adapter_targets = ["AGENTS.md", "QWEN.md"]',
                'include_in_prompts = true',
            ]
        ),
        encoding="utf-8",
    )
    (plugin_root / "bundle_governance").mkdir(parents=True, exist_ok=True)
    (plugin_root / "bundle_governance" / "core.md").write_text(
        "# Sample Governance\n\nCanonical bundle guidance.\n",
        encoding="utf-8",
    )

    package_root = tmp_path / "package"
    expected_root = package_root / "bootstrap" / "bundles" / "core" / "current"
    bootstrap_workflows_root = package_root / "bootstrap" / "workflows" / "default"

    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_root)
    monkeypatch.setattr(bundle_loader, "BOOTSTRAP_ROOT", bootstrap_workflows_root)

    result = bundle_loader.publish_bootstrap_bundle(
        workspace_root,
        plugin_workflows_root=workspace_root / "workflows",
    )

    agents_path = bootstrap_workflows_root / "sample_bundle" / "bundle_governance" / "generated" / "AGENTS.md"
    qwen_path = bootstrap_workflows_root / "sample_bundle" / "bundle_governance" / "generated" / "QWEN.md"
    assert agents_path.exists()
    assert qwen_path.exists()
    assert "Canonical bundle guidance." in agents_path.read_text(encoding="utf-8")
    assert "sample_bundle" in result["plugin_governance_docs_generated"]
    assert "AGENTS.md" in result["plugin_governance_docs_generated"]["sample_bundle"]


def test_publish_bootstrap_bundle_copies_shared_registry_into_bootstrap_workflows(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    source_root = workspace_root / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Bootstrap\n", encoding="utf-8")

    registry_root = workspace_root / "workflows" / "_registry"
    registry_root.mkdir(parents=True, exist_ok=True)
    (registry_root / "coder_connections.json").write_text('{"connections":{}}', encoding="utf-8")

    package_root = tmp_path / "package"
    expected_root = package_root / "bootstrap" / "bundles" / "core" / "current"
    bootstrap_workflows_root = package_root / "bootstrap" / "workflows" / "default"

    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_root)
    monkeypatch.setattr(bundle_loader, "BOOTSTRAP_ROOT", bootstrap_workflows_root)

    result = bundle_loader.publish_bootstrap_bundle(workspace_root)

    assert result["shared_registry_copied"] is True
    assert (bootstrap_workflows_root / "_registry" / "coder_connections.json").exists()


def test_publish_bootstrap_bundle_resets_bootstrap_workflow_root_before_copy(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    source_root = workspace_root / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Bootstrap\n", encoding="utf-8")

    registry_root = workspace_root / "workflows" / "_registry"
    registry_root.mkdir(parents=True, exist_ok=True)
    (registry_root / "coder_roles.json").write_text('{"roles":{}}', encoding="utf-8")

    plugin_root = workspace_root / "workflows" / "sample_bundle"
    plugin_root.mkdir(parents=True, exist_ok=True)
    (plugin_root / "workflow.toml").write_text(
        "\n".join(
            [
                "[workflow]",
                'name = "sample_bundle"',
                'job_prefix = "SAMPLE"',
                "",
                "[workflow.init]",
                'step = "one"',
                'inputs = []',
                "",
                "[[step]]",
                'name = "one"',
                'action = "step_completion"',
            ]
        ),
        encoding="utf-8",
    )

    package_root = tmp_path / "package"
    expected_root = package_root / "bootstrap" / "bundles" / "core" / "current"
    bootstrap_workflows_root = package_root / "bootstrap" / "workflows" / "default"
    bootstrap_workflows_root.mkdir(parents=True, exist_ok=True)
    (bootstrap_workflows_root / "coder_roles.json").write_text('{"stale":true}', encoding="utf-8")
    (bootstrap_workflows_root / "obsolete.txt").write_text("stale", encoding="utf-8")

    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_root)
    monkeypatch.setattr(bundle_loader, "BOOTSTRAP_ROOT", bootstrap_workflows_root)

    bundle_loader.publish_bootstrap_bundle(workspace_root)

    assert not (bootstrap_workflows_root / "coder_roles.json").exists()
    assert not (bootstrap_workflows_root / "obsolete.txt").exists()
    assert (bootstrap_workflows_root / "_registry" / "coder_roles.json").exists()
    assert (bootstrap_workflows_root / "sample_bundle" / "workflow.toml").exists()


def test_init_workspace_installs_packaged_bootstrap_bundle_and_seeds_global_example(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_package_root = tmp_path / "package"
    package_bootstrap_root = fake_package_root / "bootstrap" / "bundles" / "core" / "current"
    package_bootstrap_root.mkdir(parents=True, exist_ok=True)
    (package_bootstrap_root / "README.md").write_text("# Packaged Bootstrap\n", encoding="utf-8")
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    monkeypatch.setattr(bundle_loader, "PACKAGE_ROOT", fake_package_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: package_bootstrap_root)

    seeded_workflow_root = fake_home / ".ukbe-runner" / "workflows" / "example"

    def _fake_seed_workflow_bundle(target_root: Path, workflow_name: str = "example") -> Path:
        wf_root = target_root / workflow_name
        wf_root.mkdir(parents=True, exist_ok=True)
        (wf_root / "sample_bundle").mkdir(parents=True, exist_ok=True)
        return wf_root

    monkeypatch.setattr(bundle_loader, "seed_workflow_bundle", _fake_seed_workflow_bundle)

    result = bundle_loader.init_workspace(tmp_path / "workspace")

    assert (fake_home / ".ukbe-runner" / "jobs").exists()
    assert (fake_home / ".ukbe-runner" / "logs").exists()
    assert (fake_home / ".ukbe-runner" / "runtime").exists()
    assert (fake_home / ".ukbe-runner" / "bundles" / "bundle-set.json").exists()
    assert (fake_home / ".ukbe-runner" / "bundles" / "core" / "current" / "README.md").exists()
    assert (fake_home / ".ukbe-runner" / "bundles" / "domains" / "general" / "current").exists()
    assert not (tmp_path / "workspace" / ".ukbe-runner" / "workflows").exists()
    assert (fake_home / ".ukbe-runner" / "workflows" / "example").exists()
    assert result["workflow_root"] == str(seeded_workflow_root)
    assert result["runner_home"] == str(fake_home / ".ukbe-runner")
    assert result["bundle_domain"] == "general"
    assert result["bundle_profile"] == "core+workflow"
    assert result["bootstrap_install"]["global_bootstrap_root"] == str(
        fake_home / ".ukbe-runner" / "bundles" / "core" / "current"
    )


def test_init_workspace_auto_publishes_bootstrap_bundle_when_package_bundle_missing(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_package_root = tmp_path / "package"
    workspace_root = tmp_path / "workspace"
    source_root = workspace_root / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Workspace Bootstrap\n", encoding="utf-8")

    expected_package_root = fake_package_root / "bootstrap" / "bundles" / "core" / "current"
    bootstrap_workflows_root = fake_package_root / "bootstrap" / "workflows" / "default"
    
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_package_root)
    monkeypatch.setattr(bundle_loader, "BOOTSTRAP_ROOT", bootstrap_workflows_root)

    def _fake_seed_workflow_bundle(target_root: Path, workflow_name: str = "example") -> Path:
        wf_root = target_root / workflow_name
        wf_root.mkdir(parents=True, exist_ok=True)
        (wf_root / "sample_bundle").mkdir(parents=True, exist_ok=True)
        return wf_root

    monkeypatch.setattr(bundle_loader, "seed_workflow_bundle", _fake_seed_workflow_bundle)

    result = bundle_loader.init_workspace(workspace_root)

    expected_global_root = fake_home / ".ukbe-runner" / "bundles" / "core" / "current"
    assert (expected_package_root / "README.md").exists()
    assert (expected_global_root / "README.md").exists()
    assert result["bootstrap_install"]["package_bootstrap_root"] == str(expected_package_root)


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


def test_bootstrap_root_is_packaged_with_workflow_packages():
    assert bundle_loader.BOOTSTRAP_ROOT.exists()
    assert (bundle_loader.BOOTSTRAP_ROOT / "00_layer1_governance_bootstrap_v1" / "workflow.toml").exists()
    assert (bundle_loader.BOOTSTRAP_ROOT / "_registry").exists()


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


def test_run_agent_parse_args_supports_bootstrap_publish():
    args = run_agent_module.parse_args(["bootstrap-publish", "--project-root", "D:\\repo"])

    assert args.command == "bootstrap-publish"
    assert args.project_root == "D:\\repo"


def test_ensure_delivery_folders_omits_master_prompts_and_adds_codebase_docs(tmp_path):
    target_root = tmp_path / "workspace"
    target_root.mkdir()

    run_agent_module._ensure_delivery_folders(target_root)

    assert not (target_root / "docs" / "delivery" / "07_master_prompts").exists()
    assert (target_root / "docs" / "repo" / "codebase" / "00_standards").exists()
    assert (target_root / "docs" / "repo" / "codebase" / "04_changes").exists()
    assert (target_root / "docs" / "system" / "00_governance").exists()
    assert (target_root / "docs" / "engineering").exists()
    assert (target_root / "docs" / "operations").exists()


def test_layer1_governance_bootstrap_workflow_definition_exists():
    template_groups_module = load_bootstrap_workflow_module()
    group = template_groups_module.TEMPLATE_GROUPS["00_layer1_governance_bootstrap_v1"]
    assert group["job_prefix"] == "00L1"
    assert group["steps"] == [
        "generate_layer1_governance_docs",
        "review_layer1_governance_docs",
        "refine_layer1_governance_docs",
        "validate_layer1_governance_docs",
        "audit_layer1_governance_accuracy",
        "stepCompletion",
    ]
    assert group["step_configs"]["generate_layer1_governance_docs"]["prompt_file"].endswith(
        "00_layer1_governance_bootstrap_v1\\prompts\\01_generate_layer1_governance_docs.txt"
    )
    assert group["step_configs"]["generate_layer1_governance_docs"]["produces"] == [
        "SYSTEM_DOCS_INDEX",
        "SYSTEM_DOC_STANDARD",
        "BUNDLE_TAXONOMY",
        "RUNTIME_GOVERNANCE",
    ]
    assert group["step_configs"]["validate_layer1_governance_docs"]["action"] == "validate_layer1_governance_docs"
    assert group["step_configs"]["audit_layer1_governance_accuracy"]["prompt_file"].endswith(
        "00_layer1_governance_bootstrap_v1\\prompts\\04_audit_layer1_governance_accuracy.txt"
    )


def test_bootstrap_root_contains_only_active_workflow_and_registry():
    names = {path.name for path in bundle_loader.BOOTSTRAP_ROOT.iterdir()}
    assert names == {"00_layer1_governance_bootstrap_v1", "_registry"}
