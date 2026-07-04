#!/usr/bin/env python3
from __future__ import annotations

"""
actions/publish_architecture_site.py - Publish a browsable HTML architecture site.
"""

import json
from pathlib import Path

from ..action_result import ActionResult
from ..architecture_site import render_architecture_site
from ..codebase_docs import build_snapshot
from ..runtime_context import write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def publish_architecture_site(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "publish")
    job_id = str(state.get("job_id") or "SITE")
    step = str(state.get("current_step") or "publish_architecture_site")
    meta_rel = (
        context.get("ARCHITECTURE_SITE_INDEX_METAJSON", "")
        or context.get("ARCHITECTURE_SITE_METAJSON", "")
    )

    snapshot = build_snapshot(
        project_root,
        mode=mode,
        job_id=job_id,
        step=step,
        workflow_name=str(state.get("template_group") or mode),
    )

    site_pages = render_architecture_site(snapshot, project_root)
    site_root = project_root / "docs/site/architecture"
    site_root.mkdir(parents=True, exist_ok=True)
    manifest_path = site_root / "manifest.json"
    for rel_path, content in site_pages.items():
        _write_text(project_root / rel_path, content)

    manifest = {
        "workflow": str(state.get("template_group") or mode),
        "generated_at": snapshot["generated_at"],
        "pages": sorted(site_pages.keys()),
        "index": "docs/site/architecture/index.html",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark="Architecture HTML site published.",
            artifacts={
                "ARCHITECTURE_SITE_INDEX": "docs/site/architecture/index.html",
                "ARCHITECTURE_SITE_MANIFEST": "docs/site/architecture/manifest.json",
            },
        )

    return ActionResult(
        status="APPROVED",
        remark="Architecture HTML site published.",
        artifacts={
            "ARCHITECTURE_SITE_INDEX": "docs/site/architecture/index.html",
            "ARCHITECTURE_SITE_MANIFEST": "docs/site/architecture/manifest.json",
        },
    )
