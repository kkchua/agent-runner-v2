"""Context extensions for sdlc_70_validation_v1 workflow."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE, extract_slug_from_path, resolve_next_seq
from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc70ValidationExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_70_validation_v1."""

    workflow_name = "sdlc_70_validation_v1"

    def register_artifact_keys(self, *, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
        date_str = dt.datetime.now().strftime("%Y%m%d")
        return {
            "EXEC_FILE": f"{SDLC_DELIVERY_BASE}/60_executions/EXEC-{date_str}-001-{{seq}}_{{slug}}.md",
            "VAL_FILE": f"{SDLC_DELIVERY_BASE}/70_validations/VAL-{date_str}-{{seq}}_{{slug}}.md",
            "CRITIQUE_FILE_SUGGESTED": f"{SDLC_DELIVERY_BASE}/80_reviews/{{slug}}-CRITIQUE-70-val.md",
            "REVIEW_FILE_SUGGESTED": f"{SDLC_DELIVERY_BASE}/80_reviews/{{slug}}-REV-70-val.md",
        }

    def build_context_extensions(self, *, state: dict[str, Any], step: str, step_cfg: dict[str, Any], ctx: dict[str, str], project_root: Path | None = None) -> dict[str, str]:
        result: dict[str, str] = {}
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())
        workspace_root = get_workspace_root()
        effective_root = Path(project_root or workspace_root or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))
        artifacts = state.get("artifacts") or {}
        slug = extract_slug_from_path(artifacts.get("EXEC_FILE", ""))
        for key, rel_path in self.register_artifact_keys(job_id=job_id).items():
            resolved = rel_path.replace("{slug}", slug)
            if "{seq}" in resolved:
                path_dir, path_file = resolved.rsplit("/", 1)
                target_dir = effective_root / path_dir
                prefix = path_file.split("{seq}")[0]
                seq = resolve_next_seq(target_dir, prefix)
                resolved = resolved.replace("{seq}", seq)
            result[key] = str(effective_root / resolved)
        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
