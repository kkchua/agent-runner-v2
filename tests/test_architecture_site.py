from __future__ import annotations

from pathlib import Path

from agent_runner_v2.actions.validate_architecture_site import validate_architecture_site
from agent_runner_v2.architecture_site import SITE_PAGES, render_architecture_site
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

    assert set(pages) == set(SITE_PAGES)
    assert "Architecture at a Glance" in pages["docs/site/architecture/index.html"]
    assert "Product Strategy" in pages["docs/site/architecture/index.html"]
    assert "Audience Views" in pages["docs/site/architecture/index.html"]
    assert "Major Pieces" in pages["docs/site/architecture/index.html"]


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
        context={"VALIDATION_FILE_METAJSON": "docs/site/architecture/validation.meta.json"},
        state={"job_id": "50SITE-TEST", "template_group": "50_architecture_site_v1", "current_step": "validate_site"},
        step_cfg={"mode": "validate"},
        project_root=tmp_path,
    )

    assert result.status == "APPROVED"
    assert (tmp_path / "docs/site/architecture/validation.md").exists()


def test_architecture_site_workflow_registry_is_action_only():
    template_groups = load_bootstrap_workflow_module()
    workflow = template_groups.TEMPLATE_GROUPS["50_architecture_site_v1"]

    assert workflow["job_init_step"] == "build_site"
    assert workflow["steps"] == ["build_site", "validate_site"]
    assert workflow["step_configs"]["build_site"]["action"] == "publish_architecture_site"
    assert workflow["step_configs"]["validate_site"]["action"] == "validate_architecture_site"
