"""Install SDLC scaffold to global runner home.

This module provides the install_workflow() function that copies the published
SDLC scaffold (templates + agent contracts) from the repo-local current/
directory to the global runner home.
"""
from __future__ import annotations

import shutil
from pathlib import Path


def install_workflow(*, project_root: Path, runner_home: Path) -> dict:
    """Install SDLC scaffold to global path.

    Copies from:
      docs/system/00_governance/platform/agent_runner/sdlc/current/
    To:
      ~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/

    Args:
        project_root: Repository root directory.
        runner_home: Global runner home directory (~/.ukbe-runner/).

    Returns:
        Dictionary with installation status and details.
    """
    source = project_root / "docs/system/00_governance/platform/agent_runner/sdlc/current"
    dest = runner_home / "bundles/core/current/platform/agent_runner/sdlc"

    if not source.is_dir():
        return {
            "status": "SKIPPED",
            "reason": "SDLC scaffold not published yet — run sdlc_00_delivery_scaffold_v1 first",
            "source": str(source),
        }

    # Create parent directory
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy tree (overwrite if exists)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(str(source), str(dest))

    # Count files
    file_count = sum(1 for _ in dest.rglob("*") if _.is_file())

    return {
        "status": "INSTALLED",
        "source": str(source),
        "destination": str(dest),
        "files_copied": file_count,
    }
