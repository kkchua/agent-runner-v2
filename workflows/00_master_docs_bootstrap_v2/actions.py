"""Package-local actions for 00_master_docs_bootstrap_v2.

These actions are registered via the ``@action()`` decorator and dispatched
by the runner when this workflow package is active. They replace the
former globally registered ``finalize_bootstrap`` and ``validate_system_docs``
actions.
"""

from __future__ import annotations

from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
    check_file_exists,
    has_frontmatter_field,
    has_section,
)
from agent_runner_v2.actions.validate_system_docs import (
    SYSTEM_DOC_REQUIRED_SECTIONS,
    _system_extra_checks,
)
from agent_runner_v2.codebase_docs import build_snapshot
from agent_runner_v2.constants import (
    ARTIFACT_KEY_BOOTSTRAP_SUMMARY,
    get_master_docs_output_paths,
)
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action


# ======================================================================
# finalize_bootstrap
# ======================================================================


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@action("finalize_bootstrap")
def finalize_bootstrap(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
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
        remark = (
            "Bootstrap finalization failed. Missing required outputs: "
            + "; ".join(missing)
        )
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=remark,
                artifacts={},
            )
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="BOOTSTRAP_FINALIZATION_FAILED",
        )

    summary_rel = get_master_docs_output_paths(job_id=job_id, mode=mode)[
        ARTIFACT_KEY_BOOTSTRAP_SUMMARY
    ]
    summary_path = project_root / summary_rel
    summary_lines = [
        "# Bootstrap Summary",
        "",
        f"- Job ID: `{job_id}`",
        f"- Mode: `{mode}`",
        "- Workflow: `00_master_docs_bootstrap_v2`",
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
            "- Master docs bootstrap completed and repository baseline documentation"
            " is ready for governed delivery execution.",
        ]
    )
    _write_text(summary_path, "\n".join(summary_lines) + "\n")

    artifacts = {ARTIFACT_KEY_BOOTSTRAP_SUMMARY: summary_rel}
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


# ======================================================================
# validate_system_docs
# ======================================================================


@action("validate_system_docs")
def validate_system_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    mode = str(step_cfg.get("mode") or "bootstrap")
    job_id = str(state.get("job_id") or "00DOC")
    step = str(state.get("current_step") or "validate_master_system_docs")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="SYSTEM_DOCS_VALIDATION_METAJSON",
        default_step=step,
    )

    snapshot = build_snapshot(project_root=project_root)
    output_paths = get_master_docs_output_paths(job_id=job_id, mode=mode)

    required_files: dict[str, str] = {}
    for key, rel_path in output_paths.items():
        if key == ARTIFACT_KEY_BOOTSTRAP_SUMMARY:
            continue
        required_files[key] = rel_path

    plan = DocumentationValidationPlan(
        required_folders=[],
        required_files=required_files,
        section_requirements=SYSTEM_DOC_REQUIRED_SECTIONS,
        template_ids={},
        extra_checkers=[
            _system_extra_checks(snapshot=snapshot, output_paths=output_paths),
        ],
    )

    checks: list[dict] = []
    for file_key, rel_path in required_files.items():
        checks.append(check_file_exists(file_key, rel_path, project_root))
    for file_key, rel_path in required_files.items():
        checks.append(has_frontmatter_field(file_key, rel_path, project_root, ["template_id", "version", "doc_type"]))
    section_checks = plan.get("section_requirements", {})
    for file_key, sections in section_checks.items():
        for section in sections:
            checks.append(has_section(file_key, section, dict(required_files), project_root))
    for checker in plan.get("extra_checkers", []):
        checks.extend(checker(project_root=project_root))

    failed = [c for c in checks if not c["passed"]]
    validation_lines = [
        f"# System Documentation Validation — {job_id}",
        "",
        f"- Mode: `{mode}`",
        f"- Total checks: `{len(checks)}`",
        f"- Passed: `{len(checks) - len(failed)}`",
        f"- Failed: `{len(failed)}`",
        "",
    ]
    if failed:
        validation_lines.append("## Failed Checks")
        validation_lines.append("")
        for c in failed:
            detail = c.get("detail", c.get("message", ""))
            validation_lines.append(f"- **{c['check']}**: {detail}")
    else:
        validation_lines.append("**All checks passed.**")

    validation_rel = output_paths.get("SYSTEM_DOCS_VALIDATION", "")
    if validation_rel:
        validation_path = project_root / validation_rel
        _write_text(validation_path, "\n".join(validation_lines) + "\n")

    artifacts = {}
    if validation_rel:
        artifacts["SYSTEM_DOCS_VALIDATION"] = validation_rel

    if failed:
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=f"System docs validation failed: {len(failed)} checks failed",
                artifacts=artifacts,
            )
        return ActionResult(
            status="REJECTED",
            remark=f"System docs validation failed: {len(failed)} checks failed",
            artifacts=artifacts,
            reject_code="SYSTEM_DOCS_VALIDATION_FAILED",
        )

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"System docs validation passed ({len(checks)} checks).",
            artifacts=artifacts,
        )
    return ActionResult(
        status="APPROVED",
        remark=f"System docs validation passed ({len(checks)} checks).",
        artifacts=artifacts,
    )
