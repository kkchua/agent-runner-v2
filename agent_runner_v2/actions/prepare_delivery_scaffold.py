#!/usr/bin/env python3
from __future__ import annotations

"""
actions/prepare_delivery_scaffold.py - Create canonical delivery/codebase scaffold folders.
"""

from pathlib import Path

from ..action_result import ActionResult
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


SCAFFOLD_DIRS = [
    "docs/delivery/01_initiatives",
    "docs/delivery/02_plans",
    "docs/delivery/03_tasks",
    "docs/delivery/04_implementation_plans",
    "docs/delivery/05_reviews",
    "docs/delivery/06_memory",
    "docs/delivery/00_standards",
    "docs/codebase/00_templates",
    "docs/codebase/05_archives",
    "docs/system/00_governance/bootstrap/templates/delivery",
    "docs/system/00_governance/bootstrap/templates/codebase",
]


def prepare_delivery_scaffold(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    step = str(state.get("current_step") or "prepare_delivery_scaffold")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="PREPARE_DELIVERY_SCAFFOLD_METAJSON",
        default_step=step,
    )

    for rel_path in SCAFFOLD_DIRS:
        (project_root / rel_path).mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, str] = {}
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark="Canonical scaffold directories ensured.",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark="Canonical scaffold directories ensured.",
        artifacts=artifacts,
    )
