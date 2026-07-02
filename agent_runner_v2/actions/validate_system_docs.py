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
from ..system_docs import render_system_docs_validation
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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

    expected = [
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
    ]
    checks: list[tuple[str, bool, str]] = []
    for rel_path in expected:
        exists = (project_root / rel_path).exists()
        checks.append((f"{Path(rel_path).name} exists", exists, rel_path))

    index_text = (project_root / "docs/system/00_governance/bootstrap/README.md").read_text(encoding="utf-8")
    checks.append(("index mentions documentation standard", "DOCUMENTATION_STANDARD.md" in index_text, "docs/system/00_governance/bootstrap/README.md"))
    checks.append(("index mentions system overview", "SYSTEM_OVERVIEW.md" in index_text, "docs/system/00_governance/bootstrap/README.md"))

    validation_path = project_root / "docs/system/00_governance/bootstrap" / f"{job_id}-{mode}-validation.md"
    _write_text(
        validation_path,
        render_system_docs_validation(snapshot, title=f"System docs {mode} validation", checks=checks),
    )

    passed = all(ok for _, ok, _ in checks)
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
