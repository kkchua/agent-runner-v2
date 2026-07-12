from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_workflow_actions_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "00_core_governance_bootstrap_v1"
        / "actions.py"
    )
    spec = importlib.util.spec_from_file_location("tests.workflow_00_core_governance_bootstrap_v1_actions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load workflow actions module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


workflow_actions = _load_workflow_actions_module()


def _write_doc(path: Path, template_id: str, title: str, sections: tuple[str, ...], extra: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"template_id: {template_id}",
        'version: "1.0.0"',
        'doc_type: "system"',
        "---",
        "",
        f"# {title}",
        "",
    ]
    for section in sections:
        lines.extend([f"## {section}", "", "ok", ""])
    if extra:
        lines.extend([extra, ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def test_validate_core_governance_docs_rejects_stale_references(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)

    readme = tmp_path / "docs/system/00_governance/bootstrap/README.md"
    standard = tmp_path / "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md"
    taxonomy = tmp_path / "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md"
    migration = tmp_path / "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md"

    _write_doc(
        readme,
        '"SYS-00-IDX"',
        "System Documentation Index",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/README.md"],
        extra="References delivery_scaffold_v1 and uses {ARTIFACT_KEY_PROJECT_ANALYSIS}.",
    )
    _write_doc(
        standard,
        '"SYS-00-DS"',
        "Documentation Standard",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md"],
        extra="The canonical scaffold is delivery_scaffold_v1. Repo-derived inputs include PROJECT_ANALYSIS and SYSTEM_CONTEXT.",
    )
    _write_doc(
        taxonomy,
        '"SYS-00-BT"',
        "Bundle Taxonomy",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md"],
        extra=(
            "### Class 1: Core Governance Bundles\n"
            "- `00_master_docs_bootstrap_v2`\n\n"
            "### Repo-Document Bundles\n"
            "- `PROJECT_ANALYSIS` -> `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md`\n\n"
            "| Bundle Class | Allowed Write Paths | Forbidden Write Paths |\n"
            "|--------------|---------------------|----------------------|\n"
            "| Core Governance | `docs/system/00_governance/bootstrap/` | `docs/repo/*` |\n"
        ),
    )
    _write_doc(
        migration,
        '"SYS-00-BMP"',
        "Bundle Migration Plan",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md"],
        extra=(
            "Current inventory includes 20_initiative_intake_v1, 40_task_execution_v1, and 41_bug_fix_intake_v1.\n\n"
            "Active target-state docs include docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md."
        ),
    )

    result = workflow_actions.validate_core_governance_docs(
        context={"SYSTEM_DOCS_VALIDATION_METAJSON": "tmp/meta.json"},
        state={
            "job_id": "00CORE-GEN-TEST",
            "current_step": "validate_core_governance_docs",
            "template_group": "00_core_governance_bootstrap_v1",
        },
        step_cfg={},
        project_root=tmp_path,
    )

    assert result.status == "REJECTED"
    rendered = (tmp_path / "docs/system/00_governance/bootstrap/00CORE-GEN-TEST-core-governance-validation.md").read_text(
        encoding="utf-8"
    )
    assert "stale_reference" in rendered
    assert "canonical_scaffold_reference" in rendered
    assert "repo_bundle_taxonomy_scope" in rendered
    assert "documentation_standard_scope" in rendered
    assert "migration_plan_scope" in rendered


def test_validate_core_governance_docs_rejects_repo_artifact_path_example_in_standard(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)

    readme = tmp_path / "docs/system/00_governance/bootstrap/README.md"
    standard = tmp_path / "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md"
    taxonomy = tmp_path / "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md"
    migration = tmp_path / "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md"

    _write_doc(
        readme,
        '"SYS-00-IDX"',
        "System Documentation Index",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/README.md"],
        extra="References 10_execution_scaffold_v2 once.",
    )
    _write_doc(
        standard,
        '"SYS-00-DS"',
        "Documentation Standard",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md"],
        extra=(
            "Downstream outputs may be mentioned generically, but this example path is wrong: "
            "`docs/repo/codebase/00_analysis/PROJECT_ANALYSIS.md`."
        ),
    )
    _write_doc(
        taxonomy,
        '"SYS-00-BT"',
        "Bundle Taxonomy",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md"],
        extra="### Class 1: Core Governance Bundles\n- `00_core_governance_bootstrap_v1`\n",
    )
    _write_doc(
        migration,
        '"SYS-00-BMP"',
        "Bundle Migration Plan",
        workflow_actions.CORE_GOVERNANCE_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md"],
        extra="Legacy mixed outputs are tracked generically during migration.",
    )

    result = workflow_actions.validate_core_governance_docs(
        context={"SYSTEM_DOCS_VALIDATION_METAJSON": "tmp/meta.json"},
        state={
            "job_id": "00CORE-GEN-TEST",
            "current_step": "validate_core_governance_docs",
            "template_group": "00_core_governance_bootstrap_v1",
        },
        step_cfg={},
        project_root=tmp_path,
    )

    assert result.status == "REJECTED"
    rendered = (tmp_path / "docs/system/00_governance/bootstrap/00CORE-GEN-TEST-core-governance-validation.md").read_text(
        encoding="utf-8"
    )
    assert "documentation_standard_scope" in rendered
