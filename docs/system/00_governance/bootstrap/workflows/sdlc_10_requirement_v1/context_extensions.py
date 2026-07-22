"""Context extensions for sdlc_10_requirement_v1 workflow.

This module provides workflow-specific context variables for the requirement
intake workflow, including paths to Layer 1 and Layer 2 governance docs,
and codebase context.
"""
from __future__ import annotations

from pathlib import Path

from agent_runner_v2.runtime_context import get_workspace_root, get_runner_home


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    """Build context extensions for sdlc_10_requirement_v1 workflow.
    
    This function provides additional context variables needed by the
    requirement intake workflow prompts, including:
    - Layer 1 governance runtime root
    - Layer 2 platform runtime root
    - Codebase documentation root
    
    Args:
        state: Current job state dictionary.
        step: Current step name.
        step_cfg: Current step configuration dictionary.
        ctx: Base context dictionary from the runner.
        project_root: Project root directory path.
    
    Returns:
        Dictionary of additional context variables for prompt rendering.
    """
    result: dict[str, str] = {}
    
    # Layer 1 governance runtime root (global path)
    runner_home = get_runner_home()
    if runner_home:
        foundation_root = Path(runner_home) / "bundles" / "core" / "current" / "foundation"
        result["GOVERNANCE_RUNTIME_ROOT"] = str(foundation_root)
    
    # Layer 2 platform runtime root (global path)
    if runner_home:
        platform_root = Path(runner_home) / "bundles" / "core" / "current" / "platform"
        result["PLATFORM_RUNTIME_ROOT"] = str(platform_root)
    
    # Codebase documentation root (project-local)
    workspace_root = get_workspace_root()
    if workspace_root:
        codebase_root = Path(workspace_root) / "docs" / "repo" / "codebase"
        result["CODEBASE_DOC_ROOT"] = str(codebase_root)
    
    # SDLC delivery root (project-local)
    if workspace_root:
        sdlc_delivery_root = Path(workspace_root) / "docs" / "repo" / "agent_runner" / "sdlc" / "delivery"
        result["SDLC_DELIVERY_ROOT"] = str(sdlc_delivery_root)

        # Draft initiatives directory (input)
        draft_init_dir = sdlc_delivery_root / "draft_initiatives"
        result["DRAFT_INIT_DIR"] = str(draft_init_dir)

        # Initiatives directory (output)
        init_dir = sdlc_delivery_root / "initiatives"
        result["INIT_DIR"] = str(init_dir)
    
    return result
