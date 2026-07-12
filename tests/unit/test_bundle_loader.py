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
    
    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_root)

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


def test_init_workspace_installs_packaged_bootstrap_bundle_and_seeds_global_example(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_package_root = tmp_path / "package"
    package_bootstrap_root = fake_package_root / "bootstrap" / "bundles" / "core" / "current"
    package_bootstrap_root.mkdir(parents=True, exist_ok=True)
    (package_bootstrap_root / "README.md").write_text("# Packaged Bootstrap\n", encoding="utf-8")
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    monkeypatch.setattr(bundle_loader, "PACKAGE_ROOT", fake_package_root)

    seeded_workflow_root = fake_home / ".ukbe-runner" / "workflows" / "example"

    def _fake_seed_workflow_bundle(target_root: Path, workflow_name: str = "example") -> Path:
        wf_root = target_root / workflow_name
        wf_root.mkdir(parents=True, exist_ok=True)
        (wf_root / "template_groups.py").write_text("TEMPLATE_GROUPS = {}\n", encoding="utf-8")
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
    assert (fake_home / ".ukbe-runner" / "workflows" / "example" / "template_groups.py").exists()
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
    
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")
    monkeypatch.setattr(bundle_loader, "bootstrap_source_root", lambda ws: source_root)
    monkeypatch.setattr(bundle_loader, "package_bootstrap_root", lambda: expected_package_root)

    def _fake_seed_workflow_bundle(target_root: Path, workflow_name: str = "example") -> Path:
        wf_root = target_root / workflow_name
        wf_root.mkdir(parents=True, exist_ok=True)
        (wf_root / "template_groups.py").write_text("TEMPLATE_GROUPS = {}\n", encoding="utf-8")
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


def test_master_docs_bootstrap_workflow_definition_exists():
    template_groups_module = load_bootstrap_workflow_module()
    group = template_groups_module.TEMPLATE_GROUPS["00_master_docs_bootstrap_v1"]
    assert group["job_prefix"] == "00DOC"
    assert group["steps"] == [
        "00_scan_repo_codebase",
        "01_generate_codebase_baseline",
        "02_generate_project_analysis",
        "03_generate_system_overview_docs",
        "04_generate_architecture_docs",
        "04b_generate_integration_docs",
        "04c_generate_failure_docs",
        "04d_generate_architecture_flow_docs",
        "05_review_master_system_docs",
        "06_refine_master_system_docs",
        "07_validate_codebase_baseline",
        "08_validate_master_system_docs",
        "09_finalize_bootstrap",
    ]
    assert group["step_configs"]["00_scan_repo_codebase"]["action"] == "scan_repo_codebase"
    assert group["step_configs"]["01_generate_codebase_baseline"]["action"] == "sync_codebase_docs"
    assert group["step_configs"]["02_generate_project_analysis"]["prompt_file"].endswith(
        "prompts\\00_master_docs_bootstrap_v1\\02_generate_project_analysis.txt"
    )
    assert group["step_configs"]["02_generate_project_analysis"]["produces"] == ["PROJECT_ANALYSIS"]
    assert group["step_configs"]["03_generate_system_overview_docs"]["produces"] == [
        "SYSTEM_DOCS_INDEX",
        "SYSTEM_DOC_STANDARD",
        "BUNDLE_TAXONOMY",
        "BUNDLE_MIGRATION_PLAN",
        "SYSTEM_OVERVIEW",
        "BUSINESS_CAPABILITIES",
        "FUNCTIONAL_SPEC",
        "NON_FUNCTIONAL_REQUIREMENTS",
    ]
    assert group["step_configs"]["04_generate_architecture_docs"]["produces"] == [
        "SYSTEM_DOCS_CHANGE_LOG",
        "SYSTEM_CONTEXT",
        "COMPONENT_ARCHITECTURE",
        "DECISION_LOG",
        "SYSTEM_FILE_STRUCTURE",
        "DEVELOPER_GUIDE",
        "RUNBOOK",
        "EXISTING_REPO_WORKFLOW_SOP",
    ]
    assert group["step_configs"]["08_validate_master_system_docs"]["action"] == "validate_system_docs"
    assert group["step_configs"]["09_finalize_bootstrap"]["action"] == "finalize_bootstrap"


def test_bug_fix_prompt_bundle_exists():
    bug_fix_prompts = bundle_loader.BOOTSTRAP_ROOT / "prompts" / "21_bug_fix_intake_v1"
    assert (bug_fix_prompts / "01_triage_bug.txt").exists()
    assert (bug_fix_prompts / "02_reproduce_bug.txt").exists()
    assert (bug_fix_prompts / "03_isolate_root_cause.txt").exists()
    assert (bug_fix_prompts / "04_patch_bug.txt").exists()
    assert (bug_fix_prompts / "05_regression_validate.txt").exists()
