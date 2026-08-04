"""Context extensions for sdlc_00_codebase_v1 workflow.

This module provides the WorkflowExtensions interface for the codebase sync
maintenance workflow, including artifact path registration, prompt context
injection, and Layer 1/Layer 2 governance root resolution.
"""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.runtime_context import (
    JOBS_ROOT,
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
    resolve_repo_or_runtime_path,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc00CodebaseExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_00_codebase_v1."""

    workflow_name = "sdlc_00_codebase_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        Paths follow the L2 platform staging pattern under docs/repo/codebase/.
        """
        run_root = f"docs/repo/codebase/runs/{job_id}"
        current_root = "docs/repo/codebase/current"
        history_root = f"docs/repo/codebase/history/{job_id}"

        return {
            # Staged artifacts (runs/<job_id>/)
            # NOTE: CODEBASE_BACKUP is a directory, not a file — excluded from path resolution
            "CODEBASE_CHANGE_IMPACT": f"{run_root}/04_changes/{job_id}-reconcile.md",
            "CODEBASE_INVENTORY": f"{run_root}/01_inventory/codebase_inventory.md",
            "SYNC_LOG": f"{run_root}/sync_logs/SYNC-{job_id}.md",
            "REVIEW_FILE_SUGGESTED": f"{run_root}/sync_logs/{job_id}-review.md",
            "VALIDATION_FILE": f"{run_root}/04_changes/{job_id}-reconcile-validation.md",
            # Publish targets
            "CODEBASE_PUBLISH_MANIFEST": f"{current_root}/codebase_manifest.json",
            "CODEBASE_PUBLISH_MANIFEST_HISTORY": f"{history_root}/codebase_manifest.json",
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
        """Build context extensions for sdlc_00_codebase_v1 workflow.

        Provides:
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Codebase documentation roots (project-local)
        - Resolved artifact paths from register_artifact_keys()
        """
        del step_cfg, ctx
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        # Codebase documentation roots (project-local)
        workspace_root = get_workspace_root()
        effective_root = Path(project_root or workspace_root or Path.cwd()).resolve()

        codebase_root = effective_root / "docs" / "repo" / "codebase" / "current"

        job_id = str(state.get("job_id") or "SDLC00CB").strip()
        result["CODEBASE_CURRENT_ROOT"] = str(codebase_root)
        result["CODEBASE_HISTORY_ROOT"] = str(effective_root / "docs" / "repo" / "codebase" / "history" / job_id)

        # Resolve artifact paths to absolute
        output_paths = self.register_artifact_keys(job_id=job_id)
        for artifact_key, rel_path in output_paths.items():
            if not rel_path.endswith((".md", ".json", "/")):
                continue
            resolved = resolve_repo_or_runtime_path(
                rel_path, project_root=effective_root, runtime_root=JOBS_ROOT
            )
            resolved_str = str(resolved)
            result[artifact_key] = resolved_str
            pure = PurePath(resolved_str)
            result[f"{artifact_key}_METAJSON"] = str(
                pure.parent / f"{pure.stem}.meta.json"
            )

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
