"""Context extensions for sdlc_00_codebase_v1 workflow.

This module provides the WorkflowExtensions interface for the codebase sync
maintenance workflow, including artifact path registration, prompt context
injection, and Layer 1/Layer 2 governance root resolution.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.runtime_context import (
    GLOBAL_RUNNER_HOME,
    JOBS_ROOT,
    get_runner_home,
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
            "CODEBASE_BACKUP": f"docs/repo/codebase/backups/BACKUP-{job_id}/",
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
        runner_home = get_runner_home()
        if runner_home:
            foundation_root = (
                Path(runner_home) / "bundles" / "core" / "current" / "foundation"
            )
            result["GOVERNANCE_RUNTIME_ROOT"] = str(foundation_root)

        # Layer 2 platform runtime root (global path)
        if runner_home:
            platform_root = (
                Path(runner_home) / "bundles" / "core" / "current" / "platform"
            )
            result["PLATFORM_RUNTIME_ROOT"] = str(platform_root)

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
            result[f"{artifact_key}_PATH"] = resolved_str
            pure = PurePath(resolved_str)
            result[f"{artifact_key}_METAJSON"] = str(
                pure.parent / f"{pure.stem}.meta.json"
            )

        return result
