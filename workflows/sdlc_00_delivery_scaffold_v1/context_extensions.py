"""Context extensions for sdlc_00_delivery_scaffold_v1 workflow.

This module provides workflow-specific context variables for the delivery
scaffold workflow, including paths to Layer 1/L2 governance docs, masterplan
reference files, and output artifact paths.
"""
from __future__ import annotations

from pathlib import Path, PurePath

from agent_runner_v2.runtime_context import GLOBAL_RUNNER_HOME, JOBS_ROOT, resolve_repo_or_runtime_path


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Build output path mappings for sdlc_00_delivery_scaffold_v1 workflow.

    Delegated to output_paths module. Uses importlib to load output_paths.py
    from the same directory, avoiding dependency on sys.path containing the
    workflows package.

    Args:
        job_id: Job identifier for path construction.
        mode: Execution mode (e.g., "manual", "daemon").

    Returns:
        Dictionary mapping artifact keys to relative paths.
    """
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "_sdlc00_output_paths",
        Path(__file__).parent / "output_paths.py",
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    return _mod.build_output_paths(job_id=job_id, mode=mode)


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    """Build context extensions for sdlc_00_delivery_scaffold_v1 workflow.

    This function provides additional context variables needed by the
    delivery scaffold workflow prompts, including:
    - Layer 1 governance runtime root
    - Layer 2 platform runtime root
    - Masterplan reference paths for template and agent designs
    - L3 specification path
    - Resolved absolute paths for all output artifacts

    Args:
        state: Current job state dictionary.
        step: Current step name.
        step_cfg: Current step configuration dictionary.
        ctx: Base context dictionary from the runner.
        project_root: Project root directory path.

    Returns:
        Dictionary of additional context variables for prompt rendering.
    """
    del step_cfg, ctx
    job_id = str(state.get("job_id") or "SDLC00SCF").strip()
    root = Path(project_root or Path.cwd()).resolve()
    output_paths = build_output_paths(job_id=job_id, mode=str(state.get("mode") or "default"))

    extensions: dict[str, str] = {
        # Layer 1 governance runtime root (global)
        "GOVERNANCE_RUNTIME_ROOT": str(GLOBAL_RUNNER_HOME / "bundles" / "core" / "current" / "foundation"),

        # Layer 2 platform runtime root (global)
        "PLATFORM_RUNTIME_ROOT": str(GLOBAL_RUNNER_HOME / "bundles" / "core" / "current" / "platform" / "agent_runner"),

        # SDLC L3 specification path
        "SDLC_L3_SPEC_PATH": str(root / "masterplan" / "LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md"),

        # Masterplan reference paths (design reference only)
        "SDLC_MASTER_TEMPLATE_ROOT": str(root / "masterplan" / "delivery" / "00_templates"),
        "SDLC_MASTER_AGENT_ROOT": str(root / "masterplan" / "delivery" / "08_agents"),

        # SDLC platform roots
        "SDLC_CURRENT_ROOT": str(root / output_paths["SDLC_CURRENT_ROOT"]),
        "SDLC_HISTORY_ROOT": str(root / output_paths["SDLC_HISTORY_ROOT"]),
    }

    # Resolve all output artifact paths to absolute paths
    for artifact_key, rel_path in output_paths.items():
        if not rel_path.endswith((".md", ".json")):
            continue
        resolved = resolve_repo_or_runtime_path(rel_path, project_root=root, runtime_root=JOBS_ROOT)
        resolved_str = str(resolved)
        extensions[artifact_key] = resolved_str
        extensions[f"{artifact_key}_PATH"] = resolved_str
        pure = PurePath(resolved_str)
        extensions[f"{artifact_key}_METAJSON"] = str(pure.parent / f"{pure.stem}.meta.json")

    return extensions
