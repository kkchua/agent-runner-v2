#!/usr/bin/env python3
from __future__ import annotations

"""
actions/validate_architecture_site.py - Validate the published architecture HTML site.
"""

from pathlib import Path

from ..action_result import ActionResult
from ..architecture_site import SITE_PAGES
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate_architecture_site(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "validate")
    job_id = str(state.get("job_id") or "SITE")
    step = str(state.get("current_step") or "validate_architecture_site")
    meta_rel = resolve_step_meta_rel(context=context, state=state, context_key="VALIDATION_FILE_METAJSON", default_step=step)

    index_path = project_root / "docs/site/architecture/index.html"
    required_pages = [project_root / rel for rel in SITE_PAGES]
    checks: list[tuple[str, bool, str]] = []
    checks.append(("index exists", index_path.exists(), str(index_path.relative_to(project_root))))
    checks.append(("pages exist", all(path.exists() for path in required_pages), "site page set"))

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        checks.append(("index title", "<title>" in content and "Architecture Overview" in content, "title present"))
        checks.append(("architecture posture", "Architecture at a Glance" in content and "Product Strategy" in content, "core sections present"))
        checks.append(("audience views", "Audience Views" in content and "Major Pieces" in content, "audience and major pieces sections present"))
    else:
        checks.append(("index title", False, "missing index"))
        checks.append(("architecture posture", False, "missing index"))
        checks.append(("audience views", False, "missing index"))

    passed = all(ok for _, ok, _ in checks)
    validation_path = project_root / "docs/site/architecture/validation.md"
    lines = [
        "# Architecture Site Validation\n\n",
        f"- Workflow: `{state.get('template_group') or mode}`\n",
        f"- Step: `{step}`\n",
        f"- Job: `{job_id}`\n\n",
        "| Check | Status | Notes |\n|---|---|---|\n",
    ]
    for name, ok, note in checks:
        lines.append(f"| {name} | {'pass' if ok else 'fail'} | {note} |\n")
    lines.append("\n## Validation Summary\n\n")
    lines.append(f"Passed {sum(1 for _, ok, _ in checks if ok)} of {len(checks)} checks.\n")
    _write_text(validation_path, "".join(lines))

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED" if passed else "REJECTED",
            remark=f"Architecture HTML site validation {mode} {'passed' if passed else 'failed'}.",
            artifacts={"VALIDATION_FILE": "docs/site/architecture/validation.md"},
        )

    return ActionResult(
        status="APPROVED" if passed else "REJECTED",
        remark=f"Architecture HTML site validation {mode} {'passed' if passed else 'failed'}.",
        artifacts={"VALIDATION_FILE": "docs/site/architecture/validation.md"},
        reject_code=None if passed else "ARCHITECTURE_SITE_VALIDATION_FAILED",
    )

