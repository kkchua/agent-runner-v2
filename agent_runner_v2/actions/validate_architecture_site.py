#!/usr/bin/env python3
from __future__ import annotations

"""
actions/validate_architecture_site.py - Validate the published documentation hub index.
"""

from pathlib import Path

from ..action_result import ActionResult
from ..architecture_site import AUDIENCE_SITES
from ..doc_paths import docs_site_rel
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate_architecture_site(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "validate")
    job_id = str(state.get("job_id") or "SITE")
    step = str(state.get("current_step") or "validate_architecture_site")
    meta_rel = resolve_step_meta_rel(context=context, state=state, context_key="VALIDATION_FILE_METAJSON", default_step=step)

    index_path = project_root / docs_site_rel("index.html")
    manifest_path = project_root / docs_site_rel("manifest.json")

    checks: list[tuple[str, bool, str]] = []
    checks.append(("index exists", index_path.exists(), docs_site_rel("index.html")))
    checks.append(("manifest exists", manifest_path.exists(), docs_site_rel("manifest.json")))

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        checks.append(("index title", "<title>" in content and "Documentation Hub" in content, "title present"))
        checks.append(("audience cards", "Stakeholder Documentation" in content and "Developer Documentation" in content, "audience sections present"))
        checks.append(("navigation", "<nav>" in content, "navigation present"))

        # Check for audience site links
        for site in AUDIENCE_SITES:
            link_present = f'href="{site["path"]}index.html"' in content
            checks.append((f"{site['name']} link", link_present, f"link to {site['path']}index.html"))
    else:
        checks.append(("index title", False, "missing index"))
        checks.append(("audience cards", False, "missing index"))
        checks.append(("navigation", False, "missing index"))

    passed = all(ok for _, ok, _ in checks)
    validation_path = project_root / docs_site_rel("validation.md")
    lines = [
        "# Documentation Hub Validation\n\n",
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
            remark=f"Documentation hub validation {mode} {'passed' if passed else 'failed'}.",
            artifacts={"VALIDATION_FILE": docs_site_rel("validation.md")},
        )

    return ActionResult(
        status="APPROVED" if passed else "REJECTED",
        remark=f"Documentation hub validation {mode} {'passed' if passed else 'failed'}.",
        artifacts={"VALIDATION_FILE": docs_site_rel("validation.md")},
        reject_code=None if passed else "ARCHITECTURE_SITE_VALIDATION_FAILED",
    )
