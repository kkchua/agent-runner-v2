from __future__ import annotations

import json
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.bundle_loader import (
    init_workspace,
    publish_bootstrap_bundle,
)
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_bundle_validator import validate_workflow_bundle_dir
from agent_runner_v2.workflow_packages.actions import action
from agent_runner_v2 import sync_workflows


def _bucket(state: dict) -> dict:
    return state.setdefault("bootstrap_lifecycle", {})


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _repo_bundle_dirs(project_root: Path) -> list[Path]:
    workflows_root = project_root / "workflows"
    if not workflows_root.is_dir():
        return []
    return sorted(
        candidate
        for candidate in workflows_root.iterdir()
        if candidate.is_dir() and (candidate / "workflow.toml").is_file()
    )


@action("validate_bootstrap_lifecycle_sources")
def validate_bootstrap_lifecycle_sources(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    source_root = (project_root / "docs" / "system" / "00_governance" / "bootstrap").resolve()
    if not source_root.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Bootstrap source docs directory is missing: {source_root}",
            artifacts={},
            reject_code="BOOTSTRAP_SOURCE_DOCS_MISSING",
        )

    reports = [validate_workflow_bundle_dir(path) for path in _repo_bundle_dirs(project_root)]
    invalid = [report for report in reports if not report.valid]
    if invalid:
        first = invalid[0]
        finding = first.findings[0] if first.findings else None
        detail = (
            f"{first.workflow_name}: [{finding.code}] {finding.message}"
            if finding is not None
            else first.workflow_name
        )
        _bucket(state)["validation"] = {
            "valid": False,
            "workflow_count": len(reports),
            "invalid_workflows": [report.workflow_name for report in invalid],
        }
        return ActionResult(
            status="REJECTED",
            remark=f"Bootstrap lifecycle validation failed. {detail}",
            artifacts={},
            reject_code="BOOTSTRAP_WORKFLOW_BUNDLE_VALIDATION_FAILED",
        )

    _bucket(state)["validation"] = {
        "valid": True,
        "workflow_count": len(reports),
        "validated_workflows": [report.workflow_name for report in reports],
        "source_root": str(source_root),
    }
    return ActionResult(
        status="APPROVED",
        remark=f"Validated {len(reports)} workflow bundle(s) and bootstrap source docs.",
        artifacts={},
    )


@action("publish_bootstrap_lifecycle_bundle")
def publish_bootstrap_lifecycle_bundle(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    result = publish_bootstrap_bundle(project_root)
    _bucket(state)["publish"] = result
    return ActionResult(
        status="APPROVED",
        remark="Bootstrap bundle published successfully.",
        artifacts={},
    )


@action("init_bootstrap_lifecycle_workspace")
def init_bootstrap_lifecycle_workspace(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    workflow_name = str(step_cfg.get("seed_workflow_name") or "default")
    domain = str(step_cfg.get("bundle_domain") or "general")
    bundle_profile = str(step_cfg.get("bundle_profile") or "core+workflow")
    result = init_workspace(
        project_root,
        workflow_name=workflow_name,
        domain=domain,
        bundle_profile=bundle_profile,
    )
    _bucket(state)["init"] = result
    return ActionResult(
        status="APPROVED",
        remark="Bootstrap runtime initialized successfully.",
        artifacts={},
    )


@action("sync_workflow_definitions")
def sync_workflow_definitions(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    workflow_name = str(step_cfg.get("seed_workflow_name") or state.get("template_group") or "")
    names = [workflow_name] if workflow_name else []
    try:
        exit_code = sync_workflows.main(names)
    except Exception as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow sync failed: {exc}",
            artifacts={},
            reject_code="SYNC_FAILED",
        )
    if exit_code != 0:
        return ActionResult(
            status="REJECTED",
            remark="Workflow sync returned non-zero exit code.",
            artifacts={},
            reject_code="SYNC_FAILED",
        )
    _bucket(state)["sync"] = {"workflow_name": workflow_name or "all"}
    return ActionResult(
        status="APPROVED",
        remark="Workflow definitions synced to backend.",
        artifacts={},
    )


@action("write_bootstrap_lifecycle_summary")
def write_bootstrap_lifecycle_summary(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    job_id = str(state.get("job_id") or "00BOOT")
    step = str(state.get("current_step") or "write_bootstrap_lifecycle_summary")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="BOOTSTRAP_SUMMARY_METAJSON",
        default_step=step,
    )
    summary_target = (
        context.get("BOOTSTRAP_SUMMARY_PATH")
        or context.get("BOOTSTRAP_SUMMARY")
        or context.get("BOOTSTRAP_SUMMARY_PATH".upper())
        or ""
    )
    if not summary_target:
        return ActionResult(
            status="REJECTED",
            remark="BOOTSTRAP_SUMMARY path is missing from workflow context.",
            artifacts={},
            reject_code="BOOTSTRAP_SUMMARY_PATH_MISSING",
        )

    lifecycle = _bucket(state)
    summary_path = Path(summary_target)
    lines = [
        "# Bootstrap Lifecycle Summary",
        "",
        f"- Job ID: `{job_id}`",
        f"- Workflow: `00_bootstrap_lifecycle_admin_v1`",
        f"- Project root: `{project_root}`",
        "",
        "## Validation",
        "",
    ]
    validation = lifecycle.get("validation") or {}
    lines.append(f"- Valid: `{validation.get('valid', False)}`")
    lines.append(f"- Workflow bundles checked: `{validation.get('workflow_count', 0)}`")
    for name in validation.get("validated_workflows", []):
        lines.append(f"- Validated workflow: `{name}`")

    publish = lifecycle.get("publish") or {}
    lines.extend(["", "## Publish", ""])
    if publish:
        lines.append(f"- Source root: `{publish.get('source_root', '')}`")
        lines.append(f"- Package bootstrap root: `{publish.get('package_bootstrap_root', '')}`")
        lines.append(f"- Shared registry copied: `{publish.get('shared_registry_copied', False)}`")
        for name in publish.get("plugin_workflows_copied", []):
            lines.append(f"- Published workflow: `{name}`")

    init_data = lifecycle.get("init") or {}
    lines.extend(["", "## Init", ""])
    if init_data:
        lines.append(f"- Runner home: `{init_data.get('runner_home', '')}`")
        lines.append(f"- Workflow root: `{init_data.get('workflow_root', '')}`")
        lines.append(f"- Bundle profile: `{init_data.get('bundle_profile', '')}`")
        lines.append(f"- Bundle domain: `{init_data.get('bundle_domain', '')}`")
        for name in init_data.get("plugin_workflows_seeded", []):
            lines.append(f"- Seeded workflow: `{name}`")

    lines.extend(
        [
            "",
            "## Result",
            "",
            "- Repo source workflows were validated before publish.",
            "- Packaged bootstrap bundle was rebuilt from repo source of truth.",
            "- Global runner home was initialized from the packaged bootstrap bundle.",
        ]
    )
    _write_text(summary_path, "\n".join(lines) + "\n")

    artifacts = {"BOOTSTRAP_SUMMARY": str(summary_path)}
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark="Bootstrap lifecycle summary written.",
            artifacts=artifacts,
        )
    return ActionResult(
        status="APPROVED",
        remark="Bootstrap lifecycle summary written.",
        artifacts=artifacts,
    )
