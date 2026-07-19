#!/usr/bin/env python3
from __future__ import annotations

"""
actions/validate_system_docs.py - Deterministic validation for system-level documentation bootstrap.
"""

import json
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..doc_paths import codebase_doc_rel, system_doc_rel
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
    system_doc_rel("README.md"): [
        "System Documentation Index",
        "Audience Views",
        "Document Map",
    ],
    system_doc_rel("DOCUMENTATION_STANDARD.md"): [
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
    system_doc_rel("BUNDLE_TAXONOMY.md"): [
        "Bundle Classes",
        "Ownership Rules",
        "Packaging Rules",
    ],
    system_doc_rel("RUNTIME_GOVERNANCE.md"): [
        "Purpose",
        "Runtime Scope Model",
        "Bundle Publish And Install Model",
        "Registry Control Plane",
        "Plugin Bundle Control Model",
        "Role And Connection Resolution",
        "Artifact Ownership Enforcement",
        "Execution Mode Parity",
        "Validation Gates",
        "Change Control",
    ],
}


def _system_extra_checks(project_root: Path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    index_path = system_doc_rel("README.md")
    index_text = read_file(project_root, index_path)
    if index_text is not None:
        checks.append({"check": "index_mentions_documentation_standard", "path": index_path, "ok": "DOCUMENTATION_STANDARD.md" in index_text, "detail": "present" if "DOCUMENTATION_STANDARD.md" in index_text else "missing"})
        checks.append({"check": "index_mentions_runtime_governance", "path": index_path, "ok": "RUNTIME_GOVERNANCE.md" in index_text, "detail": "present" if "RUNTIME_GOVERNANCE.md" in index_text else "missing"})

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
        system_doc_rel("README.md"),
        system_doc_rel("DOCUMENTATION_STANDARD.md"),
        system_doc_rel("BUNDLE_TAXONOMY.md"),
        system_doc_rel("RUNTIME_GOVERNANCE.md"),
        system_doc_rel(f"{job_id}-{mode}-change-log.md"),
    )

    plan = DocumentationValidationPlan(
        required_files=required_files,
        section_requirements=SYSTEM_DOC_REQUIRED_SECTIONS,
        template_ids={
            system_doc_rel("README.md"): "SYS-00-IDX",
            system_doc_rel("DOCUMENTATION_STANDARD.md"): "SYS-00-DS",
            system_doc_rel("BUNDLE_TAXONOMY.md"): "SYS-00-BT",
            system_doc_rel("RUNTIME_GOVERNANCE.md"): "SYS-00-RG",
        },
        extra_checkers=(_system_extra_checks,),
    )

    checks = validate_documentation_plan(project_root=project_root, plan=plan)
    validation_path = project_root / system_doc_rel(f"{job_id}-{mode}-validation.md")
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
