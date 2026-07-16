from __future__ import annotations

import importlib.util
from pathlib import Path

from agent_runner_v2.constants import get_master_docs_output_paths


def _load_workflow_actions_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "00_repo_master_docs_bootstrap_v1"
        / "actions.py"
    )
    spec = importlib.util.spec_from_file_location("tests.workflow_00_repo_master_docs_bootstrap_v1_actions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load workflow actions module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


workflow_actions = _load_workflow_actions_module()


def test_should_validate_frontmatter_skips_non_document_artifacts() -> None:
    assert workflow_actions._should_validate_frontmatter(
        artifact_key="SYSTEM_DOCS_VALIDATION",
        rel_path="docs/repo/governance/JOB-bootstrap-validation.md",
    ) is False
    assert workflow_actions._should_validate_frontmatter(
        artifact_key="CODEBASE_SCAN_SNAPSHOT",
        rel_path="docs/repo/codebase/04_changes/JOB-bootstrap-snapshot.json",
    ) is False
    assert workflow_actions._should_validate_frontmatter(
        artifact_key="SYSTEM_DOCS_INDEX",
        rel_path="docs/repo/governance/README.md",
    ) is True


def test_validate_system_docs_ignores_existing_validation_artifact_frontmatter(tmp_path, monkeypatch) -> None:
    job_id = "00DOC-GEN-TEST"
    output_paths = get_master_docs_output_paths(job_id=job_id, mode="bootstrap")
    required_files = workflow_actions._required_repo_master_doc_files(job_id=job_id, mode="bootstrap")
    monkeypatch.setattr(
        workflow_actions,
        "build_snapshot",
        lambda **kwargs: {
            "generated_at": "2026-07-12T00:00:00+08:00",
            "workflow_name": kwargs.get("workflow_name", "00_repo_master_docs_bootstrap_v1"),
            "mode": kwargs.get("mode", "bootstrap"),
            "job_id": kwargs.get("job_id", job_id),
            "step": kwargs.get("step", "08_validate_master_system_docs"),
            "items": [],
            "counts": {},
        },
    )
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)

    required_sections = workflow_actions.REPO_MASTER_DOC_REQUIRED_SECTIONS
    validation_path = tmp_path / output_paths["SYSTEM_DOCS_VALIDATION"]
    assert not validation_path.exists()

    for artifact_key, rel_path in required_files.items():
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if rel_path.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
            continue

        lines = [
            "---",
            'template_id: "TEST-ID"',
            'version: "1.0.0"',
            'doc_type: "system"',
            "---",
            "",
            f"# {Path(rel_path).stem}",
            "",
        ]
        for section in required_sections.get(rel_path, []):
            lines.extend([f"## {section}", "", "ok", ""])
        if artifact_key == "SYSTEM_DOCS_INDEX":
            lines.extend(
                [
                    "DOCUMENTATION_STANDARD.md",
                    "",
                    "SYSTEM_OVERVIEW.md",
                    "",
                ]
            )
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    result = workflow_actions.validate_system_docs(
        context={"SYSTEM_DOCS_VALIDATION_METAJSON": "tmp/meta.json"},
        state={
            "job_id": job_id,
            "current_step": "08_validate_master_system_docs",
            "template_group": "00_repo_master_docs_bootstrap_v1",
        },
        step_cfg={"mode": "bootstrap"},
        project_root=tmp_path,
    )

    assert result.status == "APPROVED"
    assert result.artifacts["SYSTEM_DOCS_VALIDATION"] == output_paths["SYSTEM_DOCS_VALIDATION"]
    rendered = validation_path.read_text(encoding="utf-8")
    assert "Workflow Source:" in rendered


def test_validate_system_docs_reports_exact_frontmatter_failure(tmp_path, monkeypatch) -> None:
    job_id = "00DOC-GEN-TEST"
    output_paths = get_master_docs_output_paths(job_id=job_id, mode="bootstrap")
    required_files = workflow_actions._required_repo_master_doc_files(job_id=job_id, mode="bootstrap")
    monkeypatch.setattr(
        workflow_actions,
        "build_snapshot",
        lambda **kwargs: {
            "generated_at": "2026-07-12T00:00:00+08:00",
            "workflow_name": kwargs.get("workflow_name", "00_repo_master_docs_bootstrap_v1"),
            "mode": kwargs.get("mode", "bootstrap"),
            "job_id": kwargs.get("job_id", job_id),
            "step": kwargs.get("step", "08_validate_master_system_docs"),
            "items": [],
            "counts": {},
        },
    )
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)
    required_sections = workflow_actions.REPO_MASTER_DOC_REQUIRED_SECTIONS

    for artifact_key, rel_path in required_files.items():
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if rel_path.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
            continue

        lines = [
            "---",
            'template_id: "TEST-ID"',
            'version: "1.0.0"',
            'doc_type: "system"',
            "---",
            "",
            f"# {Path(rel_path).stem}",
            "",
        ]
        for section in required_sections.get(rel_path, []):
            lines.extend([f"## {section}", "", "ok", ""])
        if artifact_key == "SYSTEM_DOCS_INDEX":
            lines.extend(["DOCUMENTATION_STANDARD.md", "", "SYSTEM_OVERVIEW.md", ""])
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    project_analysis_path = tmp_path / output_paths["PROJECT_ANALYSIS"]
    broken = project_analysis_path.read_text(encoding="utf-8").replace('doc_type: "system"\n', "")
    project_analysis_path.write_text(broken, encoding="utf-8")

    result = workflow_actions.validate_system_docs(
        context={"SYSTEM_DOCS_VALIDATION_METAJSON": "tmp/meta.json"},
        state={
            "job_id": job_id,
            "current_step": "08_validate_master_system_docs",
            "template_group": "00_repo_master_docs_bootstrap_v1",
        },
        step_cfg={"mode": "bootstrap"},
        project_root=tmp_path,
    )

    assert result.status == "REJECTED"
    rendered = (tmp_path / output_paths["SYSTEM_DOCS_VALIDATION"]).read_text(encoding="utf-8")
    assert "frontmatter_field" in rendered
    assert required_files["PROJECT_ANALYSIS"] in rendered
    assert "field=`doc_type`" in rendered


def test_validate_system_docs_requires_repo_governance_index_mentions(tmp_path, monkeypatch) -> None:
    job_id = "00DOC-GEN-TEST"
    output_paths = get_master_docs_output_paths(job_id=job_id, mode="bootstrap")
    required_files = workflow_actions._required_repo_master_doc_files(job_id=job_id, mode="bootstrap")
    monkeypatch.setattr(
        workflow_actions,
        "build_snapshot",
        lambda **kwargs: {
            "generated_at": "2026-07-12T00:00:00+08:00",
            "workflow_name": kwargs.get("workflow_name", "00_repo_master_docs_bootstrap_v1"),
            "mode": kwargs.get("mode", "bootstrap"),
            "job_id": kwargs.get("job_id", job_id),
            "step": kwargs.get("step", "08_validate_master_system_docs"),
            "items": [],
            "counts": {},
        },
    )
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)
    required_sections = workflow_actions.REPO_MASTER_DOC_REQUIRED_SECTIONS

    for artifact_key, rel_path in required_files.items():
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if rel_path.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
            continue

        lines = [
            "---",
            'template_id: "TEST-ID"',
            'version: "1.0.0"',
            'doc_type: "system"',
            "---",
            "",
            f"# {Path(rel_path).stem}",
            "",
        ]
        for section in required_sections.get(rel_path, []):
            lines.extend([f"## {section}", "", "ok", ""])
        if artifact_key == "SYSTEM_DOCS_INDEX":
            lines.extend(["DOCUMENTATION_STANDARD.md", ""])
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    result = workflow_actions.validate_system_docs(
        context={"SYSTEM_DOCS_VALIDATION_METAJSON": "tmp/meta.json"},
        state={
            "job_id": job_id,
            "current_step": "08_validate_master_system_docs",
            "template_group": "00_repo_master_docs_bootstrap_v1",
        },
        step_cfg={"mode": "bootstrap"},
        project_root=tmp_path,
    )

    assert result.status == "REJECTED"
    rendered = (tmp_path / output_paths["SYSTEM_DOCS_VALIDATION"]).read_text(encoding="utf-8")
    assert "index_mentions_system_overview" in rendered
    assert required_files["SYSTEM_DOCS_INDEX"] in rendered
