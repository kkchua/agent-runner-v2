"""Context extensions for agnes_gen_video_v1 workflow.

Provides path resolution for step directories and configuration files
used by the video generation workflow.
"""
from __future__ import annotations

from pathlib import Path


def build_context_extensions(
    *, run_root: Path, project_root: Path, workflow_name: str
) -> dict[str, str]:
    """Build context variables for agnes_gen_video_v1 workflow.

    Args:
        run_root: Per-run working directory (e.g., ~/.ukbe-runner/jobs/agnes_gen_video_v1/JOB-ID/).
        project_root: Target repository root where step directories live.
        workflow_name: Workflow name (unused, for consistency).

    Returns:
        Dictionary of context variable names to resolved paths.
    """
    # Step directories (relative to project_root)
    step_dirs = [
        ("STEP_03_DIR", "step_03"),
        ("STEP_04_DIR", "step_04"),
        ("STEP_03_ARCHIVE", "step_03_archive"),
        ("STEP_04_ARCHIVE", "step_04_archive"),
    ]

    context = {}
    for var_name, rel_path in step_dirs:
        context[var_name] = str(project_root / rel_path)

    # Media config (inside run_root)
    context["MEDIA_CONFIG"] = str(run_root / "config.json")

    return context
