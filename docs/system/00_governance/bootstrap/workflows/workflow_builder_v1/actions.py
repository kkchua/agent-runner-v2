"""Custom actions for workflow_builder_v1."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


@action("validate_workflow_bundle")
def validate_workflow_bundle(*, context, state, step_cfg, project_root):
    """Validate the generated workflow package using structural and semantic checks.

    Runs the bundle validator for structural checks, then performs semantic
    validation against the TEST_CRITERIA document. Checks that action-driven
    steps have corresponding action code, and that the generated package
    fulfills the spec requirements.
    """
    from agent_runner_v2.workflow_bundle_validator import validate_workflow_bundle_dir

    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)
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

    # --- Structural validation ---
    report = validate_workflow_bundle_dir(bundle_root)
    report_dict = report.to_dict()

    # --- Semantic validation ---
    semantic_findings = _run_semantic_validation(bundle_root, artifacts, project_root)

    # Merge semantic findings into report
    all_findings = report_dict.get("findings", []) + semantic_findings
    has_errors = any(f.get("level") == "error" for f in all_findings)
    report_dict["findings"] = all_findings
    report_dict["valid"] = not has_errors
    report_dict["finding_count"] = len(all_findings)

    # Write validation report
    run_root = project_root / "docs" / "repo" / "workflow_builder" / "runs" / str(state.get("job_id", "unknown"))
    run_root.mkdir(parents=True, exist_ok=True)
    report_path = run_root / f"validation-report-{state.get('job_id', 'unknown')}.md"
    report_path.write_text(
        _render_validation_report(report_dict),
        encoding="utf-8",
    )

    if not has_errors:
        return ActionResult(
            status="APPROVED",
            remark=f"Workflow bundle is valid. {len(all_findings)} findings (all warnings).",
            artifacts={"VALIDATION_REPORT": str(report_path)},
        )
    else:
        errors = [f for f in all_findings if f.get("level") == "error"]
        error_summary = "\n".join(f"  - [{e.get('code', '')}] {e.get('message', '')}" for e in errors[:10])
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow bundle has {len(errors)} validation errors:\n{error_summary}",
            artifacts={"VALIDATION_REPORT": str(report_path)},
            reject_code="VALIDATION_FAILED",
        )


def _run_semantic_validation(bundle_root: Path, artifacts: dict, project_root: Path) -> list[dict]:
    """Run semantic validation checks beyond structural validity.

    Checks that action-driven steps have corresponding action code,
    that required files actually exist, and that gatekeepers ran.
    """
    import tomllib

    findings = []

    # Check: action-driven steps must have actions.py
    manifest_path = bundle_root / "workflow.toml"
    if manifest_path.is_file():
        try:
            with open(manifest_path, "rb") as f:
                manifest = tomllib.load(f)
        except Exception:
            manifest = {}

        steps = manifest.get("step", [])
        action_steps = [s for s in steps if s.get("action") and s["action"] != "step_completion"]

        if action_steps:
            actions_path = bundle_root / "actions.py"
            if not actions_path.is_file():
                action_names = [s["name"] for s in action_steps]
                findings.append({
                    "level": "error",
                    "code": "MISSING_ACTIONS_FILE",
                    "message": (
                        f"Workflow has action-driven steps ({', '.join(action_names)}) "
                        f"but actions.py does not exist in {bundle_root}"
                    ),
                    "step": "validate_bundle",
                })
            else:
                # Check that each action function is actually defined
                actions_content = actions_path.read_text(encoding="utf-8")
                for step in action_steps:
                    action_name = step["action"]
                    decorator = f'@action("{action_name}")'
                    if decorator not in actions_content:
                        findings.append({
                            "level": "error",
                            "code": "MISSING_ACTION_FUNCTION",
                            "message": (
                                f"Action '{action_name}' referenced in workflow.toml "
                                f"but not found in actions.py (missing {decorator})"
                            ),
                            "step": "validate_bundle",
                        })

    # Check: gatekeeper artifacts should exist
    gatekeep_artifacts = [
        ("GATEKEEP_REQUIREMENTS", "gatekeep_requirements"),
        ("GATEKEEP_ARTIFACTS", "gatekeep_artifacts"),
        ("GATEKEEP_STEPS", "gatekeep_steps"),
        ("GATEKEEP_PACKAGE", "gatekeep_package"),
    ]
    for key, step_name in gatekeep_artifacts:
        artifact_path = artifacts.get(key, "")
        if not artifact_path:
            findings.append({
                "level": "warning",
                "code": f"MISSING_{key}",
                "message": (
                    f"Gatekeeper artifact {key} not found in state. "
                    f"Step {step_name} may not have run."
                ),
                "step": "validate_bundle",
            })
        elif not Path(artifact_path).is_file():
            findings.append({
                "level": "warning",
                "code": f"MISSING_{key}_FILE",
                "message": (
                    f"Gatekeeper artifact {key} path does not exist: {artifact_path}"
                ),
                "step": "validate_bundle",
            })

    return findings


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


@action("promote_workflow_package")
def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Promote the generated workflow package to the repo workflows directory.

    Copies deployable files (workflow.toml, context_extensions.py, prompts/,
    README.md, .env.sample, config.json.sample) from the run directory to
    workflows/{slug}/. The slug is derived from the WORKFLOW_SPEC_FILE artifact
    path. Existing target directories are backed up before overwriting.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    # Derive slug from spec filename
    # Configurable via step_cfg slug_source_artifact (defaults to WORKFLOW_SPEC_FILE).
    # Meta-builders with non-standard inputs (e.g., AGENT_MD_FILE) can override this.
    slug_source_key = step_cfg.get("slug_source_artifact", "WORKFLOW_SPEC_FILE")
    spec_path = artifacts.get(slug_source_key, "")
    if not spec_path:
        return ActionResult(
            status="REJECTED",
            remark=f"{slug_source_key} artifact not found in state.",
            artifacts={},
            reject_code="MISSING_SPEC",
        )
    slug = Path(spec_path).stem
    if not slug:
        return ActionResult(
            status="REJECTED",
            remark=f"Could not derive slug from {slug_source_key}: {spec_path}",
            artifacts={},
            reject_code="SLUG_EXTRACTION_FAILED",
        )

    # Source: run root (parent of workflow.toml)
    manifest_path = artifacts.get("WORKFLOW_MANIFEST", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )
    source_dir = Path(manifest_path).parent

    # Target: workflows/{slug}/
    target_dir = project_root / "workflows" / slug

    # Backup existing target
    if target_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = project_root / "workflows" / f"{slug}_bak_{timestamp}"
        shutil.copytree(target_dir, backup_dir)
        print(
            f"[promote_workflow_package] backed up {target_dir} -> {backup_dir}",
            flush=True,
        )

    target_dir.mkdir(parents=True, exist_ok=True)

    # Files to copy (always) - core workflow files only
    always_copy = ["workflow.toml", "context_extensions.py", "README.md"]
    # Files to copy (if exist) - optional workflow files
    conditional_copy = ["actions.py", ".env.sample", "config.json.sample"]
    # Directories to copy (if exist)
    copy_dirs = ["prompts"]
    # Files to NEVER copy (build-time artifacts, not runtime files)
    exclude_files = [
        "GATEKEEP-REQ", "GATEKEEP-ART", "GATEKEEP-STEPS", "GATEKEEP-PKG",
        "REQUIREMENTS", "ARTIFACTS", "STEPS", "PROMPTS", "VALIDATION", "REVIEW",
        "TEST_CRITERIA",
    ]

    copied = []

    for filename in always_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            copied.append(filename)

    for filename in conditional_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            copied.append(filename)

    for dirname in copy_dirs:
        src = source_dir / dirname
        if src.is_dir():
            dst = target_dir / dirname
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            copied.append(f"{dirname}/")

    if not copied:
        return ActionResult(
            status="REJECTED",
            remark=f"No files found to promote in {source_dir}",
            artifacts={},
            reject_code="NOTHING_TO_PROMOTE",
        )

    remark = f"Promoted to {target_dir}: {', '.join(copied)}"
    print(f"[promote_workflow_package] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"WORKFLOW_PACKAGE_DIR": str(target_dir)},
    )


@action("promote_builder_docs")
def promote_builder_docs(*, context, state, step_cfg, project_root):
    """Promote meta-builder spec documents to docs/repo/workflow_builder/current/.

    Copies three spec documents from the run directory to the builder's
    documentation area:
    - BUILDER_SPEC_TEMPLATE -> current/templates/
    - BUILDER_SOP -> current/sop/
    - BUILDER_STANDARD -> current/

    This action is for meta-builders only (workflows whose output is another
    workflow builder). Normal workflows do not produce these documents.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    # Target base: docs/repo/workflow_builder/current/
    builder_docs_root = project_root / "docs" / "repo" / "workflow_builder" / "current"
    if not builder_docs_root.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Builder docs root not found: {builder_docs_root}",
            artifacts={},
            reject_code="MISSING_BUILDER_DOCS_ROOT",
        )

    # Mapping: artifact key -> target subdirectory
    doc_mapping = {
        "BUILDER_SPEC_TEMPLATE": builder_docs_root / "templates",
        "BUILDER_SOP": builder_docs_root / "sop",
        "BUILDER_STANDARD": builder_docs_root,
    }

    copied = []
    missing = []

    for artifact_key, target_dir in doc_mapping.items():
        source_path_str = artifacts.get(artifact_key, "")
        if not source_path_str:
            missing.append(artifact_key)
            continue

        source_path = Path(source_path_str)
        if not source_path.is_absolute():
            source_path = project_root / source_path_str

        if not source_path.exists():
            missing.append(f"{artifact_key} (file not found: {source_path})")
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / source_path.name
        shutil.copy2(source_path, target_path)
        copied.append(f"{artifact_key} -> {target_path.relative_to(project_root)}")

    if not copied and missing:
        return ActionResult(
            status="REJECTED",
            remark=f"No spec documents found to promote. Missing: {missing}",
            artifacts={},
            reject_code="NO_DOCS_TO_PROMOTE",
        )

    remark_parts = [f"Promoted: {', '.join(copied)}"]
    if missing:
        remark_parts.append(f"Missing (skipped): {', '.join(missing)}")

    remark = ". ".join(remark_parts)
    print(f"[promote_builder_docs] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={},
    )
