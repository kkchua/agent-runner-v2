"""Context extensions for sdlc_00_codebase_v1 workflow.

Combined workflow: codebase sync.
Merges artifact keys and context paths from both sdlc_00_codebase_v1
and sdlc_00_delivery_scaffold_v1.
"""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE
from agent_runner_v2.runtime_context import (
    JOBS_ROOT,
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
    resolve_repo_or_runtime_path,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc00CodebaseScaffoldExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_00_codebase_v1."""

    workflow_name = "sdlc_00_codebase_scaffold_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        codebase sync staging (docs/repo/codebase/)
        """
        # -- Codebase staging roots --
        cb_run_root = f"docs/repo/codebase/runs/{job_id}"
        cb_current_root = "docs/repo/codebase/current"
        cb_history_root = f"docs/repo/codebase/history/{job_id}"

        # -- Scaffold staging roots --
        scf_run_root = f"docs/system/00_governance/platform/agent_runner/sdlc/runs/{job_id}"
        scf_current_root = "docs/system/00_governance/platform/agent_runner/sdlc/current"
        scf_history_root = f"docs/system/00_governance/platform/agent_runner/sdlc/history/{job_id}"

        return {
            # =================================================================
            # Codebase Sync artifacts (staged under docs/repo/codebase/)
            # =================================================================
            "CODEBASE_CHANGE_IMPACT": f"{cb_run_root}/04_changes/{job_id}-reconcile.md",
            "CODEBASE_INVENTORY": f"{cb_run_root}/01_inventory/codebase_inventory.md",
            "SYNC_LOG": f"{cb_run_root}/sync_logs/SYNC-{job_id}.md",
            "REVIEW_FILE_SUGGESTED": f"{cb_run_root}/sync_logs/{job_id}-review.md",
            "VALIDATION_FILE": f"{cb_run_root}/04_changes/{job_id}-reconcile-validation.md",
            "CODEBASE_PUBLISH_MANIFEST": f"{cb_current_root}/codebase_manifest.json",
            "CODEBASE_PUBLISH_MANIFEST_HISTORY": f"{cb_history_root}/codebase_manifest.json",

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
        """Build context extensions for sdlc_00_codebase_scaffold_v1 workflow.

        Provides:
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Codebase documentation roots (project-local)
        - SDLC scaffold roots (project-local)
        - Resolved artifact paths from register_artifact_keys()
        """
        del step_cfg, ctx
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root() / "agent_runner")

        # Resolve workspace and project root
        workspace_root = get_workspace_root()
        effective_root = Path(project_root or workspace_root or Path.cwd()).resolve()

        job_id = str(state.get("job_id") or "SDLC00CS").strip()

        # -- Codebase documentation roots (project-local) --
        result["CODEBASE_CURRENT_ROOT"] = str(
            effective_root / "docs" / "repo" / "codebase" / "current"
        )
        result["CODEBASE_HISTORY_ROOT"] = str(
            effective_root / "docs" / "repo" / "codebase" / "history" / job_id
        )

        # -- Resolve artifact paths to absolute --
        for artifact_key, rel_path in output_paths.items():
            if not rel_path.endswith((".md", ".json")):
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

    def install_to_global(self, *, workspace_root, runner_home):
        """Copy SDLC scaffold to global runner home."""
        import shutil

        source = (
            Path(workspace_root)
            / "docs"
            / "system"
            / "00_governance"
            / "platform"
            / "agent_runner"
            / "sdlc"
            / "current"
        )
        dest = (
            Path(runner_home)
            / "bundles"
            / "core"
            / "current"
            / "platform"
            / "agent_runner"
            / "sdlc"
        )
        if not source.is_dir():
            return {"status": "SKIPPED", "reason": "SDLC scaffold not published yet"}
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(str(source), str(dest))
        count = sum(1 for _ in dest.rglob("*") if _.is_file())
        return {
            "status": "INSTALLED",
            "source": str(source),
            "destination": str(dest),
            "files_copied": count,
        }

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
