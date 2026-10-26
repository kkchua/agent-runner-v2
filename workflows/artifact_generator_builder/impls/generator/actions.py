"""Generator implementation actions for AGB.

Promotes only domain files, skipping infrastructure files (actions.py, prompts/).
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


@action("promote_generator_package")
def promote_generator_package(*, context, state, step_cfg, project_root):
    """Promote Generator workflow - copies only domain files, no infrastructure.

    For Generator workflows, the target package should NOT contain:
    - actions.py (infrastructure)
    - prompts/ (infrastructure prompts)

    Only domain files are copied:
    - workflow.toml (assembled with domain steps only)
    - context_extensions.py (domain artifact keys only)
    - impls/standard/ (domain logic, prompts, impl.yaml)
    - README.md (generated documentation)

    The codename is read from the generated workflow.toml manifest.
    Existing target directories are backed up before overwriting.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    # Source: the directory containing workflow.toml
    manifest_path = artifacts.get("TARGET_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="TARGET_MANIFEST_FILE artifact not found in state.",
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
        print(f"[promote_generator_package] backed up {target_dir} -> {backup_dir}", flush=True)

    target_dir.mkdir(parents=True, exist_ok=True)

    promoted = []

    # --- Generator files (root of workflows/{codename}/) ---
    # Only copy infrastructure-free files
    always_copy = ["workflow.toml", "context_extensions.py", "README.md"]
    conditional_copy = [".env.sample", "config.json.sample"]

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

    # --- Domain implementation -> impls/ (always present for Generator) ---
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
        f"Promoted Generator workflow '{codename}' to {target_dir}: "
        f"{', '.join(promoted)}. {backup_status}"
    )
    print(f"[promote_generator_package] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"TARGET_PACKAGE_DIR": str(target_dir)},
    )
