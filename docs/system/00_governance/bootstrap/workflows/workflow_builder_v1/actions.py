"""Custom actions for workflow_builder_v1."""
from __future__ import annotations

import json
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


@action("validate_workflow_bundle")
def validate_workflow_bundle(*, context, state, step_cfg, project_root):
    """Validate the generated workflow package using the bundle validator.

    Reads the generated workflow.toml from the path stored in the
    WORKFLOW_MANIFEST artifact, runs validate_workflow_bundle_dir(),
    and writes a validation report.
    """
    from agent_runner_v2.workflow_bundle_validator import validate_workflow_bundle_dir

    artifacts = state.get("artifacts", {})
    manifest_path_str = artifacts.get("WORKFLOW_MANIFEST", "")

    if not manifest_path_str:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    manifest_path = Path(manifest_path_str)
    if not manifest_path.is_file():
        return ActionResult(
            status="REJECTED",
            remark=f"workflow.toml not found at {manifest_path}",
            artifacts={},
            reject_code="MANIFEST_NOT_FOUND",
        )

    # The bundle root is the parent directory of workflow.toml
    bundle_root = manifest_path.parent

    report = validate_workflow_bundle_dir(bundle_root)
    report_dict = report.to_dict()

    # Write validation report
    run_root = Path(project_root) / "docs" / "repo" / "workflow_builder" / "runs" / str(state.get("job_id", "unknown"))
    run_root.mkdir(parents=True, exist_ok=True)
    report_path = run_root / f"validation-report-{state.get('job_id', 'unknown')}.md"
    report_path.write_text(
        _render_validation_report(report_dict),
        encoding="utf-8",
    )

    if report.valid:
        return ActionResult(
            status="APPROVED",
            remark=f"Workflow bundle is valid. {len(report.findings)} findings (all warnings).",
            artifacts={"VALIDATION_REPORT": str(report_path)},
        )
    else:
        errors = [f for f in report.findings if f.level == "error"]
        error_summary = "\n".join(f"  - [{e.code}] {e.message}" for e in errors[:10])
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow bundle has {len(errors)} validation errors:\n{error_summary}",
            artifacts={"VALIDATION_REPORT": str(report_path)},
            reject_code="VALIDATION_FAILED",
        )


def _render_validation_report(report_dict: dict) -> str:
    """Render a validation report as Markdown."""
    lines = [
        "# Workflow Bundle Validation Report",
        "",
        f"- **Workflow:** {report_dict.get('workflow_name', 'unknown')}",
        f"- **Valid:** {'YES' if report_dict.get('valid') else 'NO'}",
        f"- **Findings:** {report_dict.get('finding_count', 0)}",
        "",
    ]

    findings = report_dict.get("findings", [])
    if findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("| Level | Code | Message | Step |")
        lines.append("|---|---|---|---|")
        for f in findings:
            lines.append(
                f"| {f.get('level', '')} | {f.get('code', '')} "
                f"| {f.get('message', '')} | {f.get('step', '')} |"
            )
    else:
        lines.append("No findings. Bundle is clean.")

    return "\n".join(lines) + "\n"
