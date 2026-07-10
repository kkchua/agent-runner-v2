#!/usr/bin/env python3
from __future__ import annotations

"""
actions/validate_tester_site.py - Validate the published tester documentation site.
"""

from pathlib import Path

from ..action_result import ActionResult
from ..doc_paths import tester_site_rel
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate_tester_site(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "validate")
    job_id = str(state.get("job_id") or "TEST")
    step = str(state.get("current_step") or "validate_tester_site")
    meta_rel = resolve_step_meta_rel(context=context, state=state, context_key="VALIDATION_FILE_METAJSON", default_step=step)

    index_path = project_root / tester_site_rel("index.html")
    manifest_path = project_root / tester_site_rel("manifest.json")

    checks: list[tuple[str, bool, str]] = []
    checks.append(("index exists", index_path.exists(), tester_site_rel("index.html")))
    checks.append(("manifest exists", manifest_path.exists(), tester_site_rel("manifest.json")))

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        checks.append(("index title", "<title>" in content and "Tester" in content, "title present"))
        checks.append(("test strategy", "Test Strategy" in content, "test strategy section present"))
        checks.append(("validation criteria", "Validation Criteria" in content, "validation section present"))
        checks.append(("test coverage", "Test Coverage" in content, "coverage section present"))
        checks.append(("quality gates", "Quality Gates" in content, "quality gates section present"))
        checks.append(("navigation", "<nav>" in content, "navigation present"))
    else:
        checks.append(("index title", False, "missing index"))
        checks.append(("test strategy", False, "missing index"))
        checks.append(("validation criteria", False, "missing index"))
        checks.append(("test coverage", False, "missing index"))
        checks.append(("quality gates", False, "missing index"))
        checks.append(("navigation", False, "missing index"))

    passed = all(ok for _, ok, _ in checks)
    validation_path = project_root / tester_site_rel("validation.md")
    lines = [
        "# Tester Site Validation\n\n",
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
            remark=f"Tester site validation {mode} {'passed' if passed else 'failed'}.",
            artifacts={"VALIDATION_FILE": tester_site_rel("validation.md")},
        )

    return ActionResult(
        status="APPROVED" if passed else "REJECTED",
        remark=f"Tester site validation {mode} {'passed' if passed else 'failed'}.",
        artifacts={"VALIDATION_FILE": tester_site_rel("validation.md")},
        reject_code=None if passed else "TESTER_SITE_VALIDATION_FAILED",
    )
