from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import bundle_loader
from agent_runner_v2 import run_agent as run_agent_module
from agent_runner_v2.workflow_packages.loader import bundle_to_template_group_dict, load_workflow_package
from conftest import load_bootstrap_workflow_module
from agent_runner_v2.workflow_bundle_validator import WorkflowBundleValidationReport


def test_publish_bootstrap_bundle_copies_repo_bootstrap_docs_into_package_bundle(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    source_root = workspace_root / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (workspace_root / "workflows").mkdir(parents=True, exist_ok=True)
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
    (workspace_root / "workflows").mkdir(parents=True, exist_ok=True)

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
    (workspace_root / "workflows").mkdir(parents=True, exist_ok=True)

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
    (workspace_root / "workflows").mkdir(parents=True, exist_ok=True)

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


def test_publish_bootstrap_bundle_aborts_on_invalid_repo_workflow_bundle(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    source_root = workspace_root / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Bootstrap\n", encoding="utf-8")

    invalid_bundle = workspace_root / "workflows" / "bad_bundle"
    invalid_bundle.mkdir(parents=True, exist_ok=True)
    (invalid_bundle / "workflow.toml").write_text(
        "\n".join(
            [
                "[workflow]",
                'name = "bad_bundle"',
                'version = "1"',
                'job_prefix = "BAD"',
                "",
                "[workflow.init]",
                'step = "missing"',
                'inputs = []',
            ]
        ),
        encoding="utf-8",
    )

    package_root = tmp_path / "package"
    expected_root = package_root / "bootstrap" / "bundles" / "core" / "current"
    bootstrap_workflows_root = package_root / "bootstrap" / "workflows" / "default"
    bootstrap_workflows_root.mkdir(parents=True, exist_ok=True)
    (bootstrap_workflows_root / "stale.txt").write_text("stale", encoding="utf-8")

    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_root)
    monkeypatch.setattr(bundle_loader, "BOOTSTRAP_ROOT", bootstrap_workflows_root)

    try:
        bundle_loader.publish_bootstrap_bundle(workspace_root)
        raise AssertionError("Expected WorkflowBundlePublishValidationError")
    except bundle_loader.WorkflowBundlePublishValidationError as exc:
        assert exc.reports
        assert exc.reports[0].workflow_name == "bad_bundle"

    assert (bootstrap_workflows_root / "stale.txt").exists()


def test_init_workspace_installs_packaged_bootstrap_bundle_and_seeds_global_example(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_package_root = tmp_path / "package"
    package_bootstrap_root = fake_package_root / "bootstrap" / "bundles" / "core" / "current"
    package_bootstrap_root.mkdir(parents=True, exist_ok=True)
    (package_bootstrap_root / "README.md").write_text("# Packaged Bootstrap\n", encoding="utf-8")
    source_root = tmp_path / "workspace" / "docs" / "system" / "00_governance" / "foundation" / "current"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Published Governance\n", encoding="utf-8")
    published_workflows = tmp_path / "workspace" / "docs" / "system" / "00_governance" / "bootstrap" / "workflows" / "sample_bundle"
    published_workflows.mkdir(parents=True, exist_ok=True)
    (published_workflows / "workflow.toml").write_text(
        "\n".join(
            [
                "[workflow]",
                'name = "sample_bundle"',
                'version = "1"',
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
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    monkeypatch.setattr(bundle_loader, "PACKAGE_ROOT", fake_package_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: package_bootstrap_root)

    seeded_workflow_root = fake_home / ".ukbe-runner" / "workflows" / "default"

    def _fake_seed_workflow_bundle(target_root: Path, workflow_name: str = "default") -> Path:
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
    assert (fake_home / ".ukbe-runner" / "bundles" / "core" / "current" / "foundation" / "README.md").exists()
    assert (fake_home / ".ukbe-runner" / "bundles" / "domains" / "general" / "current").exists()
    assert not (tmp_path / "workspace" / ".ukbe-runner" / "workflows").exists()
    assert (fake_home / ".ukbe-runner" / "workflows" / "default").exists()
    assert result["workflow_root"] == str(seeded_workflow_root)
    assert result["runner_home"] == str(fake_home / ".ukbe-runner")
    assert result["bundle_domain"] == "general"
    assert result["bundle_profile"] == "core+workflow"
    assert result["bootstrap_install"]["global_bootstrap_root"] == str(
        fake_home / ".ukbe-runner" / "bundles" / "core" / "current" / "foundation"
    )


def test_init_workspace_requires_published_bootstrap_snapshot_when_package_bundle_missing(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_package_root = tmp_path / "package"
    workspace_root = tmp_path / "workspace"
    # Engine repo root layout: workspace_root/agent_runner_v2/bootstrap/...
    engine_bootstrap = workspace_root / "agent_runner_v2" / "bootstrap" / "bundles" / "core" / "current"
    foundation_dir = engine_bootstrap / "foundation"
    foundation_dir.mkdir(parents=True, exist_ok=True)
    (foundation_dir / "README.md").write_text("# Published Governance\n", encoding="utf-8")
    # Workflow packages under engine bootstrap
    engine_workflows = workspace_root / "agent_runner_v2" / "bootstrap" / "workflows" / "default"
    engine_workflows.mkdir(parents=True, exist_ok=True)
    sample_bundle = engine_workflows / "sample_bundle"
    sample_bundle.mkdir(parents=True, exist_ok=True)
    (sample_bundle / "workflow.toml").write_text(
        "\n".join(
            [
                "[workflow]",
                'name = "sample_bundle"',
                'version = "1"',
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

    expected_package_root = fake_package_root / "bootstrap" / "bundles" / "core" / "current"
    bootstrap_workflows_root = fake_package_root / "bootstrap" / "workflows" / "default"

    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_package_root)
    monkeypatch.setattr(bundle_loader, "BOOTSTRAP_ROOT", bootstrap_workflows_root)
    monkeypatch.setattr(bundle_loader, "resolve_engine_repo_root", lambda: workspace_root)

    def _fake_seed_workflow_bundle(target_root: Path, workflow_name: str = "default") -> Path:
        wf_root = target_root / workflow_name
        wf_root.mkdir(parents=True, exist_ok=True)
        (wf_root / "sample_bundle").mkdir(parents=True, exist_ok=True)
        return wf_root

    monkeypatch.setattr(bundle_loader, "seed_workflow_bundle", _fake_seed_workflow_bundle)

    result = bundle_loader.init_workspace(workspace_root)

    expected_global_root = fake_home / ".ukbe-runner" / "bundles" / "core" / "current"
    assert (expected_global_root / "foundation" / "README.md").exists()
    assert result["bootstrap_install"]["source_root"] == str(foundation_dir)


def test_resolve_workflow_root_prefers_global_workflow(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    global_default = fake_home / ".ukbe-runner" / "workflows" / "default"
    global_default.mkdir(parents=True)

    resolved = bundle_loader.resolve_workflow_root(tmp_path / "workspace", "default", config={"workflows": {}})

    assert resolved == global_default.resolve()


def test_resolve_workflow_root_ignores_repo_local_config_override(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    global_default = fake_home / ".ukbe-runner" / "workflows" / "default"
    global_default.mkdir(parents=True, exist_ok=True)

    workspace_root = tmp_path / "workspace"
    (workspace_root / "workflows" / "default").mkdir(parents=True, exist_ok=True)

    resolved = bundle_loader.resolve_workflow_root(
        workspace_root,
        "default",
        config={"workflows": {"default": {"path": "workflows/default"}}},
    )

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
    assert (bundle_loader.BOOTSTRAP_ROOT / "01_governance_foundation_v1" / "workflow.toml").exists()
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
    args = run_agent_module.parse_args(["bootstrap-publish"])

    assert args.command == "bootstrap-publish"


def test_ensure_delivery_folders_omits_master_prompts_and_adds_codebase_docs(tmp_path):
    target_root = tmp_path / "workspace"
    target_root.mkdir()

    run_agent_module._ensure_delivery_folders(target_root)

    assert not (target_root / "docs" / "delivery" / "07_master_prompts").exists()
    assert (target_root / "docs" / "repo" / "codebase" / "current" / "00_standards").exists()
    assert (target_root / "docs" / "system" / "00_governance").exists()
    # Legacy paths are no longer auto-created
    assert not (target_root / "docs" / "repo" / "codebase" / "04_changes").exists()
    assert not (target_root / "docs" / "engineering").exists()
    assert not (target_root / "docs" / "operations").exists()


def test_layer1_governance_bootstrap_workflow_definition_exists():
    bundle = load_workflow_package(
        Path(__file__).resolve().parents[2] / "workflows" / "01_governance_foundation_v1"
    )
    group = bundle_to_template_group_dict(bundle)
    assert group["job_prefix"] == "01GF"
    assert group["default_max_rejects"] == 3
    assert group["steps"] == [
        "collect_governance_context",
        "generate_governance_foundation_docs",
        "review_governance_foundation_docs",
        "refine_governance_foundation_docs",
        "validate_governance_foundation_docs",
        "audit_governance_foundation_docs",
        "publish_governance_foundation_set",
        "stepCompletion",
    ]
    assert group["step_configs"]["generate_governance_foundation_docs"]["prompt_file"].endswith(
        "01_governance_foundation_v1\\prompts\\01_generate_governance_foundation_docs.txt"
    )
    assert group["step_configs"]["generate_governance_foundation_docs"]["produces"] == [
        "L1_FOUNDATION_INDEX",
        "L1_LAYER_MODEL",
        "L1_DOCUMENT_AUTHORITY",
        "L1_BUNDLE_TAXONOMY",
        "L1_GOVERNANCE_LIFECYCLE",
        "L1_METADATA_STANDARD",
    ]
    assert group["step_configs"]["collect_governance_context"]["action"] == "collect_governance_context"
    assert group["step_configs"]["review_governance_foundation_docs"]["required_inputs"] == [
        "GOVERNANCE_CONTEXT_INVENTORY",
        "L1_FOUNDATION_INDEX",
        "L1_LAYER_MODEL",
        "L1_DOCUMENT_AUTHORITY",
        "L1_BUNDLE_TAXONOMY",
        "L1_GOVERNANCE_LIFECYCLE",
        "L1_METADATA_STANDARD",
    ]
    assert group["step_configs"]["validate_governance_foundation_docs"]["action"] == "validate_governance_foundation_docs"
    assert group["step_configs"]["audit_governance_foundation_docs"]["prompt_file"].endswith(
        "01_governance_foundation_v1\\prompts\\04_audit_governance_foundation_docs.txt"
    )
    assert group["step_configs"]["audit_governance_foundation_docs"]["produces"] == [
        "AUDIT_FILE_SUGGESTED"
    ]


def test_bootstrap_root_workflows_are_structurally_valid():
    """Every subdirectory in bootstrap root must be a valid workflow package or the registry."""
    bootstrap_root = bundle_loader.BOOTSTRAP_ROOT
    assert bootstrap_root.is_dir(), f"Bootstrap root does not exist: {bootstrap_root}"

    entries = [p for p in bootstrap_root.iterdir() if p.is_dir()]
    assert len(entries) > 0, "Bootstrap root is empty"

    for entry in entries:
        if entry.name == "_registry":
            continue
        workflow_toml = entry / "workflow.toml"
        assert workflow_toml.is_file(), (
            f"Workflow directory '{entry.name}' is missing workflow.toml"
        )
