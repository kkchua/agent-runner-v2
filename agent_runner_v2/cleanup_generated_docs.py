from __future__ import annotations

"""
cleanup_generated_docs.py - Deterministic cleanup for stale workflow-generated documentation.

This utility removes or quarantines workflow-owned docs that no longer match the
canonical manifest for a workflow.
"""

import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .documentation_guardrails import (
    DEFAULT_LEGACY_QUARANTINE_DIR,
    workflow_stale_generated_doc_paths,
)


@dataclass
class CleanupResult:
    stale_paths: list[str]
    removed_paths: list[str]
    quarantined_paths: list[str]
    action: str


def _build_state(*, job_id: str, mode: str) -> dict:
    return {
        "job_id": job_id,
        "current_mode": mode,
        "current_step_cfg": {"mode": mode},
    }


def cleanup_workflow_generated_docs(
    *,
    project_root: Path,
    template_group: str,
    job_id: str,
    mode: str,
    action: str = "report",
    quarantine_root: str = DEFAULT_LEGACY_QUARANTINE_DIR,
) -> CleanupResult:
    state = _build_state(job_id=job_id, mode=mode)
    stale_paths = workflow_stale_generated_doc_paths(
        template_group=template_group,
        state=state,
        project_root=project_root,
    )
    removed_paths: list[str] = []
    quarantined_paths: list[str] = []
    quarantine_base = project_root / quarantine_root / template_group / datetime.now().strftime("%Y%m%d-%H%M%S")

    for rel_path in stale_paths:
        src = project_root / rel_path
        if not src.exists() or not src.is_file():
            continue
        if action == "remove":
            src.unlink()
            removed_paths.append(rel_path)
        elif action == "quarantine":
            dst = quarantine_base / Path(rel_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            quarantined_paths.append(f"{rel_path} -> {dst.relative_to(project_root).as_posix()}")
        else:
            # report-only
            continue

    return CleanupResult(
        stale_paths=stale_paths,
        removed_paths=removed_paths,
        quarantined_paths=quarantined_paths,
        action=action,
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Cleanup stale workflow-generated docs.")
    p.add_argument("--project-root", default=".", help="Repository root to clean.")
    p.add_argument("--template-group", required=True, help="Workflow template group name.")
    p.add_argument("--job-id", default="", help="Job ID used to resolve workflow-specific paths.")
    p.add_argument("--mode", default="bootstrap", help="Workflow mode used for canonical path resolution.")
    p.add_argument(
        "--action",
        choices=["report", "remove", "quarantine"],
        default="report",
        help="How to handle stale docs.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv)
    project_root = Path(ns.project_root).resolve()
    result = cleanup_workflow_generated_docs(
        project_root=project_root,
        template_group=ns.template_group,
        job_id=ns.job_id,
        mode=ns.mode,
        action=ns.action,
    )

    print(f"Workflow cleanup action: {result.action}")
    print(f"Stale docs found: {len(result.stale_paths)}")
    for rel_path in result.stale_paths:
        print(f"  - {rel_path}")
    if result.action == "remove":
        print(f"Removed: {len(result.removed_paths)}")
    elif result.action == "quarantine":
        print(f"Quarantined: {len(result.quarantined_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
