#!/usr/bin/env python3
from __future__ import annotations

"""
actions/finalize_bootstrap.py - Final bootstrap summary for the master-doc workflow.
"""

from pathlib import Path

from ..action_result import ActionResult
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def finalize_bootstrap(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "bootstrap")
    job_id = str(state.get("job_id") or "00DOC")
    step = str(state.get("current_step") or "finalize_bootstrap")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="BOOTSTRAP_SUMMARY_METAJSON",
        default_step=step,
    )

    artifacts_state = state.get("artifacts") or {}

    def _artifact_path(key: str) -> str:
        return str(
            artifacts_state.get(key)
            or context.get(f"{key}_PATH")
            or context.get(key)
            or ""
        )

    expected_artifacts = {
        "CODEBASE_SCAN_SNAPSHOT": _artifact_path("CODEBASE_SCAN_SNAPSHOT"),
        "CODEBASE_CHANGE_IMPACT": _artifact_path("CODEBASE_CHANGE_IMPACT"),
        "CODEBASE_INVENTORY": _artifact_path("CODEBASE_INVENTORY"),
        "PROJECT_ANALYSIS": _artifact_path("PROJECT_ANALYSIS"),
        "SYSTEM_DOCS_INDEX": _artifact_path("SYSTEM_DOCS_INDEX"),
        "SYSTEM_DOCS_CHANGE_LOG": _artifact_path("SYSTEM_DOCS_CHANGE_LOG"),
        "VALIDATION_FILE": _artifact_path("VALIDATION_FILE"),
        "SYSTEM_DOCS_VALIDATION": _artifact_path("SYSTEM_DOCS_VALIDATION"),
    }
    missing = [
        f"{artifact_key}: {artifact_rel or '<missing path>'}"
        for artifact_key, artifact_rel in expected_artifacts.items()
        if not artifact_rel or not (project_root / artifact_rel).exists()
    ]
    if missing:
        remark = "Bootstrap finalization failed. Missing required outputs: " + "; ".join(missing)
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="BOOTSTRAP_FINALIZATION_FAILED",
        )

    summary_path = project_root / "docs" / "system" / "00_governance" / "bootstrap" / f"{job_id}-bootstrap-summary.md"
    summary_lines = [
        "# Bootstrap Summary",
        "",
        f"- Job ID: `{job_id}`",
        f"- Mode: `{mode}`",
        f"- Workflow: `00_master_docs_bootstrap_v1`",
        "",
        "## Outputs",
        "",
    ]
    for artifact_key, artifact_rel in expected_artifacts.items():
        summary_lines.append(f"- `{artifact_key}`: `{artifact_rel}`")
    summary_lines.extend(
        [
            "",
            "## Result",
            "",
            "- Master docs bootstrap completed and repository baseline documentation is ready for governed delivery execution.",
        ]
    )
    _write_text(summary_path, "\n".join(summary_lines) + "\n")

    artifact_rel = summary_path.relative_to(project_root).as_posix()
    artifacts = {"BOOTSTRAP_SUMMARY": artifact_rel}
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark="Bootstrap finalization completed.",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark="Bootstrap finalization completed.",
        artifacts=artifacts,
    )
