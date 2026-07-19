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
                    "REPO_DOCUMENTATION_STANDARD.md",
                    "",
                    "DEVELOPER_GUIDE.md",
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
            lines.extend(["REPO_DOCUMENTATION_STANDARD.md", "", "DEVELOPER_GUIDE.md", ""])
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
            lines.extend(["REPO_DOCUMENTATION_STANDARD.md", ""])
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
    assert "index_mentions_developer_guide" in rendered
    assert required_files["SYSTEM_DOCS_INDEX"] in rendered


def test_validate_system_docs_reports_missing_section_name(tmp_path, monkeypatch) -> None:
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
            if rel_path.endswith("REPO_DOCUMENTATION_STANDARD.md") and section == "Document Set":
                continue
            lines.extend([f"## {section}", "", "ok", ""])
        if artifact_key == "SYSTEM_DOCS_INDEX":
            lines.extend(["REPO_DOCUMENTATION_STANDARD.md", "", "DEVELOPER_GUIDE.md", ""])
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
    assert "section=`Document Set`" in rendered
    assert "missing section `Document Set`" in rendered
    assert "Rule source: `workflows/00_repo_master_docs_bootstrap_v1/actions.py:REPO_MASTER_DOC_REQUIRED_SECTIONS`" in rendered


def test_validate_system_docs_rejects_legacy_repo_standard_filename_references(tmp_path, monkeypatch) -> None:
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
            lines.extend(["REPO_DOCUMENTATION_STANDARD.md", "", "DEVELOPER_GUIDE.md", ""])
        if artifact_key == "SYSTEM_DOC_STANDARD":
            lines.extend(["DOCUMENTATION_STANDARD.md", "", "REPO_DOCUMENTATION_STANDARD.md", ""])
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
    assert "repo_standard_avoids_legacy_filename" in rendered
    assert "contains legacy Layer 1 filename `DOCUMENTATION_STANDARD.md` in repo-level standard" in rendered
    assert "Rule source: `workflows/00_repo_master_docs_bootstrap_v1/actions.py:_repo_master_doc_extra_checks`" in rendered


def test_validate_system_docs_rejects_non_ascii_repo_governance_output(tmp_path, monkeypatch) -> None:
    job_id = "00DOC-GEN-TEST"
    output_paths = get_master_docs_output_paths(job_id=job_id, mode="bootstrap")
    required_files = workflow_actions._required_repo_master_doc_files(job_id=job_id, mode="bootstrap")
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)
    required_sections = workflow_actions.REPO_MASTER_DOC_REQUIRED_SECTIONS

    for artifact_key, rel_path in required_files.items():
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
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
            lines.extend(["REPO_DOCUMENTATION_STANDARD.md", "", "DEVELOPER_GUIDE.md", ""])
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    readme_path = tmp_path / output_paths["SYSTEM_DOCS_INDEX"]
    readme_path.write_text(readme_path.read_text(encoding="utf-8") + "bad dash: \u2014\n", encoding="utf-8")

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
    assert "ascii_only_output" in rendered
    assert "non-ASCII characters found" in rendered
    assert "Rule source: `workflows/00_repo_master_docs_bootstrap_v1/actions.py:ascii_and_scope_checks`" in rendered


def test_validate_system_docs_rejects_workflow_mechanics_in_repo_governance_docs(tmp_path, monkeypatch) -> None:
    job_id = "00DOC-GEN-TEST"
    output_paths = get_master_docs_output_paths(job_id=job_id, mode="bootstrap")
    required_files = workflow_actions._required_repo_master_doc_files(job_id=job_id, mode="bootstrap")
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)
    required_sections = workflow_actions.REPO_MASTER_DOC_REQUIRED_SECTIONS

    for artifact_key, rel_path in required_files.items():
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
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
            lines.extend(["REPO_DOCUMENTATION_STANDARD.md", "", "DEVELOPER_GUIDE.md", ""])
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    guide_path = tmp_path / output_paths["DEVELOPER_GUIDE"]
    guide_path.write_text(
        guide_path.read_text(encoding="utf-8") + "\nThis guide explains daemon behavior and heartbeat handling.\n",
        encoding="utf-8",
    )

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
    assert "repo_governance_avoids_workflow_mechanics" in rendered
    assert "contains workflow/runtime mechanics term: daemon" in rendered


def test_validate_system_docs_requires_new_project_analysis_headings(tmp_path, monkeypatch) -> None:
    job_id = "00DOC-GEN-TEST"
    output_paths = get_master_docs_output_paths(job_id=job_id, mode="bootstrap")
    required_files = workflow_actions._required_repo_master_doc_files(job_id=job_id, mode="bootstrap")
    monkeypatch.setattr(workflow_actions, "write_meta_sidecar", lambda *args, **kwargs: None)
    required_sections = workflow_actions.REPO_MASTER_DOC_REQUIRED_SECTIONS

    for artifact_key, rel_path in required_files.items():
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
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
        if rel_path == output_paths["PROJECT_ANALYSIS"]:
            legacy_sections = [
                "Repo Overview",
                "Governance Scope",
                "Repository Posture",
                "Governance Risks",
                "Architectural Observations",
                "Architecture Posture",
                "Unresolved Documentation Gaps",
            ]
            for section in legacy_sections:
                lines.extend([f"## {section}", "", "ok", ""])
        else:
            for section in required_sections.get(rel_path, []):
                lines.extend([f"## {section}", "", "ok", ""])
        if artifact_key == "SYSTEM_DOCS_INDEX":
            lines.extend(["REPO_DOCUMENTATION_STANDARD.md", "", "DEVELOPER_GUIDE.md", ""])
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
    assert "section=`Codebase Structure`" in rendered
    assert "section=`Workflow and Runtime Model`" in rendered
    assert "section=`Operational Risks`" in rendered
