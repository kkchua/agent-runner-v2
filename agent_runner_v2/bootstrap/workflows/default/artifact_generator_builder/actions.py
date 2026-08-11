"""Custom actions for Artifact Generator Builder.

This module provides action implementations for the artifact generator
builder workflow. Actions are deterministic, code-driven steps that
perform specific operations without LLM involvement.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


@action("promote_workflow_package")
def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Promote all deliverables to workflows/{codename}/.

    Packages the generated workflow according to the Composition System
    Standard required file structure (Section 10.2):

        workflows/{codename}/
            standards/COMPOSITION_STANDARD.md
            workflow.toml
            context_extensions.py
            actions.py
            prompts/
            README.md
            Specs/
            impls/              (optional — only if alternative impls exist)

    The codename is read from the generated workflow.toml manifest.
    Existing target directories are backed up before overwriting.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    # Source: the directory containing workflow.toml
    manifest_path = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    source_dir = Path(manifest_path).parent
    if not source_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow output directory not found: {source_dir}",
            artifacts={},
            reject_code="SOURCE_DIR_NOT_FOUND",
        )

    # Read codename from manifest
    import tomllib
    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)

    codename = manifest.get("workflow", {}).get("name", "")
    if not codename:
        return ActionResult(
            status="REJECTED",
            remark="Workflow name (codename) not found in workflow.toml [workflow] section.",
            artifacts={},
            reject_code="MISSING_CODENAME",
        )

    # Target: workflows/{codename}/
    target_dir = project_root / "workflows" / codename

    # Backup existing target
    backup_status = "No backup needed"
    if target_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = project_root / "workflows" / f"{codename}_bak_{timestamp}"
        shutil.copytree(target_dir, backup_dir)
        backup_status = f"Backed up existing workflow to {backup_dir}"
        print(f"[promote_workflow_package] backed up {target_dir} -> {backup_dir}", flush=True)

    target_dir.mkdir(parents=True, exist_ok=True)

    promoted = []

    # --- Workflow package files (root of workflows/{codename}/) ---
    always_copy = ["workflow.toml", "context_extensions.py", "README.md"]
    conditional_copy = ["actions.py", ".env.sample", "config.json.sample"]
    copy_dirs = ["prompts", "Specs"]

    for filename in always_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            promoted.append(filename)

    for filename in conditional_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            promoted.append(filename)

    for dirname in copy_dirs:
        src = source_dir / dirname
        if src.is_dir():
            dst = target_dir / dirname
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            promoted.append(f"{dirname}/")

    # --- Deliverable 1: Composition Standard -> standards/ ---
    comp_std_path = artifacts.get("COMPOSITION_STANDARD_FILE", "")
    if comp_std_path:
        src = Path(comp_std_path)
        if src.exists():
            standards_dir = target_dir / "standards"
            standards_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, standards_dir / src.name)
            promoted.append(f"standards/{src.name}")

    # --- Alternative implementations -> impls/ (optional) ---
    impls_src = source_dir / "impls"
    if impls_src.is_dir():
        impls_dst = target_dir / "impls"
        if impls_dst.exists():
            shutil.rmtree(impls_dst)
        shutil.copytree(impls_src, impls_dst)
        promoted.append("impls/")

    if not promoted:
        return ActionResult(
            status="REJECTED",
            remark=f"No files found to promote in {source_dir}",
            artifacts={},
            reject_code="NOTHING_TO_PROMOTE",
        )

    remark = (
        f"Promoted workflow '{codename}' to {target_dir}: "
        f"{', '.join(promoted)}. {backup_status}"
    )
    print(f"[promote_workflow_package] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"PROMOTION_REPORT_FILE": str(target_dir)},
    )


@action("validate_structure")
def validate_structure(*, context, state, step_cfg, project_root):
    """Run deterministic structural validation on the generated package.

    Uses workflow_package_validator.validate_package() to check:
    - TOML parse and structure
    - Python syntax
    - Artifact key bindings
    - Action implementations
    - Prompt file existence
    - Placeholder consistency

    Writes findings to {VALIDATION_FINDINGS_FILE}.
    """
    from agent_runner_v2.workflow_package_validator import (
        validate_package,
        render_report,
    )

    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    manifest_path = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    extensions_path = artifacts.get("WORKFLOW_EXTENSIONS_FILE", "")
    actions_path = artifacts.get("WORKFLOW_ACTIONS_FILE", "")

    result = validate_package(
        manifest_path=Path(manifest_path),
        extensions_path=Path(extensions_path) if extensions_path else None,
        actions_path=Path(actions_path) if actions_path else None,
    )

    job_id = str(state.get("job_id", "unknown"))
    run_root = project_root / "docs" / "repo" / "artifact_generator_builder" / "runs" / job_id
    run_root.mkdir(parents=True, exist_ok=True)
    report_path = run_root / f"VALIDATION_FINDINGS-{datetime.now().strftime('%Y%m%d')}-001.md"

    report = render_report(result, job_id=job_id)
    report_path.write_text(report, encoding="utf-8")

    errors = [f for f in result.findings if f.level == "error"]
    if errors:
        error_summary = "; ".join(f"{f.code}: {f.message}" for f in errors[:5])
        return ActionResult(
            status="REJECTED",
            remark=f"Structural validation failed with {len(errors)} error(s): {error_summary}",
            artifacts={"VALIDATION_FINDINGS_FILE": str(report_path)},
            reject_code="VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Structural validation passed. {render_report(result)}",
        artifacts={"VALIDATION_FINDINGS_FILE": str(report_path)},
    )


@action("run_tests")
def run_tests(*, context, state, step_cfg, project_root):
    """Run the generated pytest test file against the generated actions.py.

    Executes pytest on {TEST_FILE} and captures results.
    Writes a test results report to {TEST_RESULTS_FILE}.

    If tests fail, returns REJECTED so the workflow routes back to
    implement_package to fix the action code.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    test_file = artifacts.get("TEST_FILE", "")
    if not test_file:
        return ActionResult(
            status="REJECTED",
            remark="TEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_TESTS",
        )

    test_path = Path(test_file)
    if not test_path.is_file():
        return ActionResult(
            status="REJECTED",
            remark=f"Test file not found: {test_path}",
            artifacts={},
            reject_code="MISSING_TESTS",
        )

    actions_file = artifacts.get("WORKFLOW_ACTIONS_FILE", "")
    actions_dir = str(Path(actions_file).parent) if actions_file else ""

    # Build pytest command
    python_exe = sys.executable
    cmd = [python_exe, "-m", "pytest", str(test_path), "-v", "--tb=short", "--no-header"]

    env = None
    if actions_dir:
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = actions_dir + os.pathsep + env.get("PYTHONPATH", "")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=actions_dir or None,
            env=env,
        )
        output = proc.stdout + "\n" + proc.stderr
        exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        output = "pytest timed out after 120 seconds"
        exit_code = -1
    except Exception as exc:
        output = f"Failed to run pytest: {exc}"
        exit_code = -1

    # Write test results report
    job_id = str(state.get("job_id", "unknown"))
    run_root = project_root / "docs" / "repo" / "artifact_generator_builder" / "runs" / job_id
    run_root.mkdir(parents=True, exist_ok=True)
    report_path = run_root / f"TEST_RESULTS-{datetime.now().strftime('%Y%m%d')}-001.md"

    passed = exit_code == 0
    report_lines = [
        "---",
        'doc_type: "test_results"',
        f'lifecycle_status: "final"',
        f'job_id: "{job_id}"',
        "---",
        "",
        "# Action Test Results",
        "",
        f"- **Passed:** {'YES' if passed else 'NO'}",
        f"- **Exit Code:** {exit_code}",
        "",
        "## pytest Output",
        "",
        "```",
        output.strip(),
        "```",
        "",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    if passed:
        return ActionResult(
            status="APPROVED",
            remark="All action tests passed.",
            artifacts={"TEST_RESULTS_FILE": str(report_path)},
        )
    else:
        return ActionResult(
            status="REJECTED",
            remark=f"Action tests failed (exit code {exit_code}). See report: {report_path}",
            artifacts={"TEST_RESULTS_FILE": str(report_path)},
            reject_code="TESTS_FAILED",
        )
