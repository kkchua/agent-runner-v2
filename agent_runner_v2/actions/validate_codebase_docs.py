#!/usr/bin/env python3
from __future__ import annotations

"""
actions/validate_codebase_docs.py — Deterministic validation for bootstrap/reconcile codebase docs.
"""

import json
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..codebase_docs import build_snapshot, render_validation
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate_codebase_docs(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "reconcile")
    job_id = str(state.get("job_id") or "codebase-scan")
    step = str(state.get("current_step") or "validate_codebase_docs")
    meta_rel = resolve_step_meta_rel(context=context, state=state, context_key="VALIDATION_FILE_METAJSON", default_step=step)
    snapshot = build_snapshot(
        project_root,
        mode=mode,
        job_id=job_id,
        step=step,
        workflow_name=str(state.get("template_group") or mode),
    )

    inventory_path = project_root / "docs/codebase/01_inventory/codebase_inventory.md"
    module_dir = project_root / "docs/codebase/02_modules"
    component_dir = project_root / "docs/codebase/03_components"
    change_dir = project_root / "docs/codebase/04_changes"
    change_path = change_dir / f"{job_id}-{mode}.md"

    checks: list[tuple[str, bool, str]] = []
    checks.append(("inventory exists", inventory_path.exists(), str(inventory_path.relative_to(project_root))))
    checks.append(("change impact exists", change_path.exists(), str(change_path.relative_to(project_root))))

    module_docs_ok = True
    for module_record in snapshot["python_modules"]:
        doc_name = Path(module_record["owner_doc_path"]).name
        doc_path = module_dir / doc_name
        if not doc_path.exists():
            module_docs_ok = False
            break
    checks.append(("module docs exist", module_docs_ok, "all Python modules mapped"))

    component_docs = [
        component_dir / "workflow-families.md",
        component_dir / "actions-package.md",
        component_dir / "tests-suite.md",
        component_dir / "scripts-suite.md",
        component_dir / "config-and-data.md",
        component_dir / "codebase-governance.md",
    ]
    checks.append(("component docs exist", all(path.exists() for path in component_docs), "baseline component set"))
    checks.append(("inventory row count", "documentation files" in inventory_path.read_text(encoding="utf-8"), "inventory rendered"))

    passed = all(ok for _, ok, _ in checks)
    title = f"{project_root.name or 'repository'} codebase {mode} validation"
    validation_path = change_dir / f"{job_id}-{mode}-validation.md"
    _write_text(validation_path, render_validation(snapshot, title=title, checks=checks))
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED" if passed else "REJECTED", remark=f"Codebase docs validation {mode} {'passed' if passed else 'failed'}.", artifacts={"VALIDATION_FILE": validation_path.relative_to(project_root).as_posix()})

    status = "APPROVED" if passed else "REJECTED"
    return ActionResult(
        status=status,
        remark=f"Codebase docs validation {mode} {'passed' if passed else 'failed'}.",
        artifacts={"VALIDATION_FILE": validation_path.relative_to(project_root).as_posix()},
        reject_code=None if passed else "CODEBASE_DOCS_VALIDATION_FAILED",
    )
