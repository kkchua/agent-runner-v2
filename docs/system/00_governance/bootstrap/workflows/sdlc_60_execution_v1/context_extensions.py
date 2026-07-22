"""Context extensions for sdlc_60_execution_v1 workflow."""
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
    """Build context extensions for sdlc_60_execution_v1 workflow.

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

    runner_home = get_runner_home()
    if runner_home:
        result["GOVERNANCE_RUNTIME_ROOT"] = str(Path(runner_home) / "bundles" / "core" / "current" / "foundation")
        result["PLATFORM_RUNTIME_ROOT"] = str(Path(runner_home) / "bundles" / "core" / "current" / "platform")

    workspace_root = get_workspace_root()
    if workspace_root:
        result["CODEBASE_DOC_ROOT"] = str(Path(workspace_root) / "docs" / "repo" / "codebase")
        sdlc_delivery_root = Path(workspace_root) / "docs" / "repo" / "agent_runner" / "sdlc" / "delivery"
        result["SDLC_DELIVERY_ROOT"] = str(sdlc_delivery_root)
        result["EXEC_DIR"] = str(sdlc_delivery_root / "executions")

    return result
