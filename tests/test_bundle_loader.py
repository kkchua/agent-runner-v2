from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import bundle_loader
from agent_runner_v2 import run_agent as run_agent_module
from conftest import load_bootstrap_workflow_module


def test_init_workspace_seeds_global_example_and_not_repo_workflows(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    monkeypatch.setattr(bundle_loader, "GLOBAL_RUNNER_HOME", fake_home / ".ukbe-runner")

    result = bundle_loader.init_workspace(tmp_path / "workspace")

    assert (fake_home / ".ukbe-runner" / "jobs").exists()
    assert (fake_home / ".ukbe-runner" / "logs").exists()
    assert (fake_home / ".ukbe-runner" / "runtime").exists()
    assert (fake_home / ".ukbe-runner" / "bundles" / "bundle-set.json").exists()
    assert (fake_home / ".ukbe-runner" / "bundles" / "core" / "current").exists()
    assert (fake_home / ".ukbe-runner" / "bundles" / "domains" / "general" / "current").exists()
    assert not (tmp_path / "workspace" / ".ukbe-runner" / "workflows").exists()
    assert (fake_home / ".ukbe-runner" / "workflows" / "example" / "template_groups.py").exists()
    assert result["workflow_root"] == str(fake_home / ".ukbe-runner" / "workflows" / "example")
    assert result["runner_home"] == str(fake_home / ".ukbe-runner")
    assert result["bundle_domain"] == "general"
    assert result["bundle_profile"] == "core+workflow"


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


def test_legacy_workflow_families_are_hidden():
    template_groups_module = load_bootstrap_workflow_module()
    hidden = [
        "delivery_scaffold_v1",
        "initiative_intake_v1",
        "delivery_planning_v1",
        "task_execution_v1",
        "documentation_sync_v1",
        "codebase_bootstrap_v1",
        "codebase_reconcile_v1",
        "system_docs_bootstrap_v1",
        "documentation_bootstrap_v1",
        "codebase_rescan_v1",
        "documentation_validation_v1",
        "bug_fix_v1",
    ]

    for name in hidden:
        assert template_groups_module.TEMPLATE_GROUPS_OLD[name]["visibility"] == "hidden"


def test_codebase_rescan_workflow_definition_exists():
    template_groups_module = load_bootstrap_workflow_module()
    group = template_groups_module.TEMPLATE_GROUPS_OLD["codebase_rescan_v1"]
    assert group["job_prefix"] == "CDRESCAN"
    assert group["steps"] == ["scan_codebase", "validate_codebase_docs"]
    assert group["step_configs"]["scan_codebase"]["mode"] == "reconcile"
    assert group["step_configs"]["validate_codebase_docs"]["mode"] == "reconcile"


def test_documentation_validation_workflow_definition_exists():
    template_groups_module = load_bootstrap_workflow_module()
    group = template_groups_module.TEMPLATE_GROUPS_OLD["documentation_validation_v1"]
    assert group["job_prefix"] == "DOCVAL"
    assert group["steps"] == ["validate_documentation_set"]
    assert group["step_configs"]["validate_documentation_set"]["action"] == "validate_delivery_docs"


def test_bug_fix_workflow_definition_exists():
    template_groups_module = load_bootstrap_workflow_module()
    group = template_groups_module.TEMPLATE_GROUPS_OLD["bug_fix_v1"]
    assert group["job_prefix"] == "BUGFIX"
    assert group["job_init_inputs"] == ["BUG_DRAFT_FILE"]
    assert group["steps"] == [
        "triage_bug",
        "reproduce_bug",
        "isolate_root_cause",
        "patch_bug",
        "regression_validate",
        "sync_codebase_docs",
        "sync_system_docs",
    ]
    assert "21_bug_fix_intake_v1" in group["step_configs"]["triage_bug"]["prompt_file"]
    assert group["step_configs"]["triage_bug"]["prompt_file"].endswith("01_triage_bug.txt")
    assert group["step_configs"]["sync_system_docs"]["action"] == "sync_system_docs"


def test_bug_fix_prompt_bundle_exists():
    bug_fix_prompts = bundle_loader.BOOTSTRAP_ROOT / "prompts" / "21_bug_fix_intake_v1"
    assert (bug_fix_prompts / "01_triage_bug.txt").exists()
    assert (bug_fix_prompts / "02_reproduce_bug.txt").exists()
    assert (bug_fix_prompts / "03_isolate_root_cause.txt").exists()
    assert (bug_fix_prompts / "04_patch_bug.txt").exists()
    assert (bug_fix_prompts / "05_regression_validate.txt").exists()


