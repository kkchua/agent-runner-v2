"""Context extensions for sdlc_40_task_v1 workflow."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE
from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc40TaskExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_40_task_v1."""

    workflow_name = "sdlc_40_task_v1"

    def register_artifact_keys(self, *, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
        return {
            "TASK_FILE": f"{SDLC_DELIVERY_BASE}/40_tasks/{{work_item}}.md",
            "CRITIQUE_FILE_SUGGESTED": f"{SDLC_DELIVERY_BASE}/80_reviews/{{work_item}}-CRITIQUE-40-task.md",
            "REVIEW_FILE_SUGGESTED": f"{SDLC_DELIVERY_BASE}/80_reviews/{{work_item}}-REV-40-task.md",
        }

    def build_context_extensions(self, *, state: dict[str, Any], step: str, step_cfg: dict[str, Any], ctx: dict[str, str], project_root: Path | None = None) -> dict[str, str]:
        result: dict[str, str] = {}
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())
        workspace_root = get_workspace_root()
        effective_root = Path(project_root or workspace_root or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))
        artifacts = state.get("artifacts") or {}
        work_item = str(artifacts.get("WORK_ITEM", "")).strip()
        if work_item:
            result["WORK_ITEM"] = work_item
        for key, rel_path in self.register_artifact_keys(job_id=job_id).items():
            resolved = rel_path.replace("{work_item}", work_item)
            result[key] = str(effective_root / resolved)
        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
