#!/usr/bin/env python3
from __future__ import annotations

"""
actions/validate_system_docs.py - Deterministic validation for system-level documentation bootstrap.
"""

import json
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..codebase_docs import build_snapshot
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar
from ..system_docs import render_system_docs_validation
from .documentation_validation_core import (
    DocumentationValidationPlan,
    has_section,
    read_file,
    validate_documentation_plan,
)


SYSTEM_DOC_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "docs/system/00_governance/bootstrap/project_analysis.md": [
        "Repo Overview",
        "Codebase Structure",
        "Operational Risks",
        "Architectural Observations",
        "Architecture Posture",
    ],
    "docs/system/00_governance/bootstrap/README.md": [
        "System Documentation Index",
        "Audience Views",
        "Document Map",
    ],
    "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md": [
        "Purpose",
        "Audience Model",
        "Document Set",
        "Update Triggers",
        "Validation",
        "Architecture Baseline",
        "Repo-Selected Profile",
        "Migration Mode",
        "Conditional Standards",
    ],
    "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md": [
        "Purpose",
        "Scope",
        "Primary Flows",
        "Key Risks",
        "Architecture Profile",
    ],
    "docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md": [
        "Repository Structure",
        "Top-Level Directories",
        "Documentation Locations",
    ],
    "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md": [
        "Development Workflow",
        "Key Commands",
        "Documentation Responsibilities",
        "Architecture Posture",
    ],
    "docs/system/00_governance/bootstrap/RUNBOOK.md": [
        "Operations Scope",
        "Routine Procedures",
        "Failure Handling",
    ],
    "docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md": [
        "Purpose",
        "First-Time Setup",
        "Normal Governed Delivery",
        "Drift Reconciliation",
        "Governance Refresh",
        "Batch Files",
        "Notes",
    ],
}


def _system_extra_checks(project_root: Path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    index_path = "docs/system/00_governance/bootstrap/README.md"
    index_text = read_file(project_root, index_path)
    if index_text is not None:
        checks.append({"check": "index_mentions_documentation_standard", "path": index_path, "ok": "DOCUMENTATION_STANDARD.md" in index_text, "detail": "present" if "DOCUMENTATION_STANDARD.md" in index_text else "missing"})
        checks.append({"check": "index_mentions_system_overview", "path": index_path, "ok": "SYSTEM_OVERVIEW.md" in index_text, "detail": "present" if "SYSTEM_OVERVIEW.md" in index_text else "missing"})

    return checks


def validate_system_docs(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "bootstrap")
    job_id = str(state.get("job_id") or "system-docs")
    step = str(state.get("current_step") or "validate_system_docs")
    meta_rel = resolve_step_meta_rel(context=context, state=state, context_key="SYSTEM_DOCS_VALIDATION_METAJSON", default_step=step)
    snapshot = build_snapshot(
        project_root,
        mode=mode,
        job_id=job_id,
        step=step,
        workflow_name=str(state.get("template_group") or mode),
    )

    required_files = (
        "docs/system/00_governance/bootstrap/project_analysis.md",
        "docs/system/00_governance/bootstrap/README.md",
        "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md",
        "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md",
        "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md",
        "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md",
        "docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md",
        "docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md",
        "docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md",
        "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md",
        "docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md",
        "docs/system/00_governance/bootstrap/DECISION_LOG.md",
        "docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md",
        "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md",
        "docs/system/00_governance/bootstrap/RUNBOOK.md",
        "docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md",
        f"docs/system/00_governance/bootstrap/{job_id}-{mode}-change-log.md",
    )

    plan = DocumentationValidationPlan(
        required_files=required_files,
        section_requirements=SYSTEM_DOC_REQUIRED_SECTIONS,
        template_ids={
            "docs/system/00_governance/bootstrap/README.md": "SYS-00-IDX",
            "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md": "SYS-00-DS",
            "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md": "SYS-00-BT",
            "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md": "SYS-00-BMP",
            "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md": "SYS-00-SO",
            "docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md": "SYS-00-BC",
            "docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md": "SYS-00-FS",
            "docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md": "SYS-00-NFR",
            "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md": "SYS-03-CTX",
            "docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md": "SYS-03-CA",
            "docs/system/00_governance/bootstrap/DECISION_LOG.md": "SYS-03-DL",
            "docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md": "SYS-03-SF",
            "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md": "ENG-01-DG",
            "docs/system/00_governance/bootstrap/RUNBOOK.md": "OPS-01-RB",
        },
        extra_checkers=(_system_extra_checks,),
    )

    checks = validate_documentation_plan(project_root=project_root, plan=plan)
    validation_path = project_root / "docs/system/00_governance/bootstrap" / f"{job_id}-{mode}-validation.md"
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_checks = [
        (
            f"{item['check']} @ {item['path']}",
            bool(item["ok"]),
            str(item.get("detail") or ""),
        )
        for item in checks
    ]
    validation_path.write_text(
        render_system_docs_validation(snapshot, title=f"System docs {mode} validation", checks=rendered_checks),
        encoding="utf-8",
    )

    passed = all(bool(item["ok"]) for item in checks)
    artifacts = {"SYSTEM_DOCS_VALIDATION": validation_path.relative_to(project_root).as_posix()}
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED" if passed else "REJECTED",
            remark=f"System docs validation {mode} {'passed' if passed else 'failed'}.",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED" if passed else "REJECTED",
        remark=f"System docs validation {mode} {'passed' if passed else 'failed'}.",
        artifacts=artifacts,
        reject_code=None if passed else "SYSTEM_DOCS_VALIDATION_FAILED",
    )
