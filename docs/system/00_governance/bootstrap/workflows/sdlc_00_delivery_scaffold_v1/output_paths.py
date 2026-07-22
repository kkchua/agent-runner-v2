"""Output paths for sdlc_00_delivery_scaffold_v1 workflow.

This module defines the artifact path mappings for the delivery scaffold
workflow, following the L2 platform pattern (stage -> publish -> init to global).
"""
from __future__ import annotations


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Build output path mappings for sdlc_00_delivery_scaffold_v1 workflow.

    This function returns a dictionary mapping artifact keys to their
    relative paths within the repository, following the L2 platform
    staging pattern under the sdlc/ subdirectory.

    Args:
        job_id: Job identifier for path construction.
        mode: Execution mode (e.g., "manual", "daemon").

    Returns:
        Dictionary mapping artifact keys to relative paths.
    """
    del mode

    # Staging root (L2 platform pattern)
    run_root = f"docs/system/00_governance/platform/agent_runner/sdlc/runs/{job_id}"

    # Publish and history roots
    current_root = "docs/system/00_governance/platform/agent_runner/sdlc/current"
    history_root = f"docs/system/00_governance/platform/agent_runner/sdlc/history/{job_id}"

    return {
        # -- Master Templates (01_templates/) --
        "SDLC_TEMPLATE_REGISTRY": f"{run_root}/01_templates/template_registry.md",
        "SDLC_WORKFLOW_SOP": f"{run_root}/01_templates/WORKFLOW_SOP_v1.md",
        "SDLC_TEMPLATE_DRAFT_INIT": f"{run_root}/01_templates/01_DRAFT_INIT_template.md",
        "SDLC_TEMPLATE_INIT": f"{run_root}/01_templates/02_INIT_template.md",
        "SDLC_TEMPLATE_REQ": f"{run_root}/01_templates/03_REQ_template.md",
        "SDLC_TEMPLATE_PLAN": f"{run_root}/01_templates/04_PLAN_template.md",
        "SDLC_TEMPLATE_BACKLOG": f"{run_root}/01_templates/05_BACKLOG_template.md",
        "SDLC_TEMPLATE_TASK": f"{run_root}/01_templates/06_TASK_template.md",
        "SDLC_TEMPLATE_IMPL": f"{run_root}/01_templates/07_IMPL_template.md",
        "SDLC_TEMPLATE_VALID": f"{run_root}/01_templates/08_VALID_template.md",
        "SDLC_TEMPLATE_REV": f"{run_root}/01_templates/09_REV_template.md",
        "SDLC_TEMPLATE_MEM": f"{run_root}/01_templates/10_MEM_template.md",
        "SDLC_TEMPLATE_CLOSE": f"{run_root}/01_templates/11_CLOSE_template.md",

        # -- Agent Contracts (02_agents/) --
        "SDLC_AGENTS_INDEX": f"{run_root}/02_agents/AGENTS.md",
        "SDLC_AGENT_PLANNER": f"{run_root}/02_agents/AGENT-planner.md",
        "SDLC_AGENT_TASK_DECOMPOSER": f"{run_root}/02_agents/AGENT-task-decomposer.md",
        "SDLC_AGENT_IMPL_PLANNER": f"{run_root}/02_agents/AGENT-implementation-planner.md",
        "SDLC_AGENT_EXECUTOR": f"{run_root}/02_agents/AGENT-executor.md",
        "SDLC_AGENT_REVIEWER": f"{run_root}/02_agents/AGENT-reviewer.md",
        "SDLC_AGENT_MEMORY_MANAGER": f"{run_root}/02_agents/AGENT-memory-manager.md",
        "SDLC_DELIVERY_STATUS_RULES": f"{run_root}/02_agents/DELIVERY_STATUS_RULES_v1.md",

        # -- Review --
        "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-sdlc-scaffold-review.md",

        # -- Publish targets --
        "SDLC_CURRENT_ROOT": current_root,
        "SDLC_HISTORY_ROOT": history_root,
        "SDLC_SCAFFOLD_PUBLISH_MANIFEST": f"{current_root}/sdlc_scaffold_manifest.json",
        "SDLC_SCAFFOLD_PUBLISH_MANIFEST_HISTORY": f"{history_root}/sdlc_scaffold_manifest.json",
    }
