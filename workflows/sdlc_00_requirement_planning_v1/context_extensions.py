"""Context extensions for sdlc_00_requirement_planning_v1 workflow.

Combined SDLC pipeline: initiative intake through requirement, planning,
backlog, and task generation with review gates at each phase.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE, extract_slug_from_path, resolve_next_seq
from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


def _extract_backlog_stem(file_path: str) -> str:
    """Extract the backlog stem (BACKLOG- prefix removed) from a file path."""
    if not file_path:
        return "unknown"
    stem = Path(file_path).stem
    if stem.startswith("BACKLOG-"):
        return stem[len("BACKLOG-"):]
    return stem


class Sdlc00RequirementPlanningExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_00_requirement_planning_v1."""

    workflow_name = "sdlc_00_requirement_planning_v1"

    # Step name prefix → slug source artifact mapping
    _PHASE_SLUG_SOURCE = {
        "init": "DRAFT_INIT_FILE",
        "req": "INIT_FILE",
        "plan": "REQ_FILE",
        "backlog": "PLAN_FILE",
    }

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings for all 5 phases."""
        date_str = dt.datetime.now().strftime("%Y%m%d")
        return {
            # Phase 1: Initiative
            "DRAFT_INIT_FILE": (
                f"{SDLC_DELIVERY_BASE}/00_draft_initiatives/"
                f"DRAFT-INIT-{date_str}-{{seq}}_{{slug}}.md"
            ),
            "INIT_FILE": (
                f"{SDLC_DELIVERY_BASE}/00_initiatives/"
                f"INIT-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Phase 2: Requirements
            "REQ_FILE": (
                f"{SDLC_DELIVERY_BASE}/10_requirements/"
                f"REQ-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Phase 3: Planning
            "PLAN_FILE": (
                f"{SDLC_DELIVERY_BASE}/20_plans/"
                f"PLAN-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Phase 4: Backlog
            "BACKLOG_FILE": (
                f"{SDLC_DELIVERY_BASE}/30_backlogs/"
                f"BACKLOG-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Phase 5: Task
            "TASK_FILE": (
                f"{SDLC_DELIVERY_BASE}/40_tasks/"
                f"{{work_item}}.md"
            ),
            # Shared review artifacts (phase-specific suffixes in filenames)
            "CRITIQUE_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-CRITIQUE-{date_str}-{{seq}}.md"
            ),
            "REVIEW_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-REV-{date_str}-{{seq}}.md"
            ),
        }

    def build_context_extensions(
        self,
        *,
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        ctx: dict[str, str],
        project_root: Path | None = None,
    ) -> dict[str, str]:
        """Build context extensions for all 5 phases.

        Determines slug source based on current step's phase prefix.
        Phase 5 (task_*) uses WORK_ITEM instead of slug.
        """
        result: dict[str, str] = {}

        # Governance and platform roots
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        effective_root = Path(project_root or get_workspace_root() or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))
        artifacts = state.get("artifacts") or {}

        # Determine slug source based on current step's phase prefix
        slug = "unknown"
        for prefix, artifact_key in self._PHASE_SLUG_SOURCE.items():
            if step.startswith(prefix + "_") or step == f"promote_{prefix}":
                slug = extract_slug_from_path(artifacts.get(artifact_key, ""))
                break

        # Phase 5: handle WORK_ITEM
        work_item = ""
        if step.startswith("task_") or step == "promote_task":
            work_item = str(artifacts.get("WORK_ITEM", "")).strip()
            result["WORK_ITEM"] = work_item

        # Resolve all artifact paths
        for key, rel_path in self.register_artifact_keys(job_id=job_id).items():
            resolved = rel_path.replace("{slug}", slug)
            resolved = resolved.replace("{work_item}", work_item)
            if "{seq}" in resolved:
                path_dir, path_file = resolved.rsplit("/", 1)
                target_dir = effective_root / path_dir
                prefix = path_file.split("{seq}")[0]
                seq = resolve_next_seq(target_dir, prefix)
                resolved = resolved.replace("{seq}", seq)
            result[key] = str(effective_root / resolved)

        # Add BACKLOG_STEM (used by backlog phase)
        backlog_path = result.get("BACKLOG_FILE", "")
        if backlog_path:
            result["BACKLOG_STEM"] = _extract_backlog_stem(backlog_path)

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
