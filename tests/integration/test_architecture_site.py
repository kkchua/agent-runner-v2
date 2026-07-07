from __future__ import annotations

from pathlib import Path

from agent_runner_v2.actions.validate_architecture_site import validate_architecture_site
from agent_runner_v2.architecture_site import SITE_PAGES, render_architecture_site
from agent_runner_v2.actions.publish_architecture_site import publish_architecture_site
from agent_runner_v2.runtime_context import set_workflow_module
from conftest import load_bootstrap_workflow_module


def test_architecture_site_renderer_emits_the_expected_pages(tmp_path):
    snapshot = {
        "workflow_name": "50_architecture_site_v1",
        "mode": "publish",
        "step": "build_site",
        "architecture_profile": "baseline",
        "architecture_target_profile": "repo-selected",
        "architecture_migration_mode": "targeted_migration",
        "workflow_families": [
            {
                "family_name": "bootstrap",
                "job_prefix": "00DOC",
                "visibility": "canonical",
                "job_init_step": "generate_project_analysis",
                "steps": ["generate_project_analysis", "generate_system_overview_docs"],
            }
        ],
        "python_modules": [
            {"module_area": "core"},
            {"module_area": "actions"},
        ],
    }

    pages = render_architecture_site(snapshot, tmp_path)

    # Master index now only generates index.html and manifest.json
    assert "docs/site/index.html" in pages
    assert "docs/site/manifest.json" in pages
    # Check content of the master index
    assert "Documentation Hub" in pages["docs/site/index.html"]
    assert "Stakeholder Documentation" in pages["docs/site/index.html"]
    assert "Developer Documentation" in pages["docs/site/index.html"]


def test_architecture_site_validation_passes_when_pages_exist(tmp_path):
    snapshot = {
        "workflow_name": "50_architecture_site_v1",
        "mode": "publish",
        "step": "build_site",
        "architecture_profile": "baseline",
        "architecture_target_profile": "repo-selected",
        "architecture_migration_mode": "targeted_migration",
        "workflow_families": [],
        "python_modules": [],
    }
    pages = render_architecture_site(snapshot, tmp_path)
    for rel_path, content in pages.items():
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    result = validate_architecture_site(
        context={"VALIDATION_FILE_METAJSON": "docs/site/validation.meta.json"},
        state={"job_id": "50SITE-TEST", "template_group": "50_architecture_site_v1", "current_step": "validate_site"},
        step_cfg={"mode": "validate"},
        project_root=tmp_path,
    )

    assert result.status == "APPROVED"
    assert (tmp_path / "docs/site/validation.md").exists()


def test_architecture_site_workflow_registry_is_action_only():
    template_groups = load_bootstrap_workflow_module()
    workflow = template_groups.TEMPLATE_GROUPS["50_architecture_site_v1"]

    assert workflow["job_init_step"] == "build_site"
    assert workflow["steps"] == ["build_site", "validate_site"]
    assert workflow["step_configs"]["build_site"]["action"] == "publish_architecture_site"
    assert workflow["step_configs"]["validate_site"]["action"] == "validate_architecture_site"


def test_publish_architecture_site_writes_sidecar_for_index_metajson(tmp_path):
    context = {"ARCHITECTURE_SITE_INDEX_METAJSON": "docs/site/index.meta.json"}
    state = {"job_id": "50SITE-TEST", "template_group": "50_architecture_site_v1", "current_step": "build_site"}
    set_workflow_module(load_bootstrap_workflow_module())

    result = publish_architecture_site(
        context=context,
        state=state,
        step_cfg={"mode": "publish"},
        project_root=tmp_path,
    )

    assert result.status == "APPROVED"
    # Master index is now at docs/site/ (not docs/site/architecture/)
    assert (tmp_path / "docs/site/index.html").exists()
    assert (tmp_path / "docs/site/manifest.json").exists()
    assert (tmp_path / "docs/site/index.meta.json").exists()
