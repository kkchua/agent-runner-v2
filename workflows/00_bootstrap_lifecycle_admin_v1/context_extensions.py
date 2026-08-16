"""Context extensions for 00_bootstrap_lifecycle_admin_v1."""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import ARTIFACT_KEY_BOOTSTRAP_SUMMARY
from agent_runner_v2.runtime_context import JOBS_ROOT, get_workspace_root, resolve_repo_or_runtime_path
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class BootstrapLifecycleAdminExtensions(WorkflowExtensions):
    """Workflow extension hooks for 00_bootstrap_lifecycle_admin_v1."""

    workflow_name = "00_bootstrap_lifecycle_admin_v1"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings."""
        return {
            ARTIFACT_KEY_BOOTSTRAP_SUMMARY: (
                f"docs/system/00_governance/bootstrap/{job_id}-bootstrap-lifecycle-summary.md"
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
        """Build context extensions for 00_bootstrap_lifecycle_admin_v1."""
        job_id = str(state.get("job_id") or "00BOOT").strip()
        root = Path(project_root or get_workspace_root() or Path.cwd()).resolve()
        summary_name = f"{job_id}-bootstrap-lifecycle-summary.md"
        summary_path = resolve_repo_or_runtime_path(
            f"docs/system/00_governance/bootstrap/{summary_name}",
            project_root=root,
            runtime_root=JOBS_ROOT,
        )
        summary_str = str(summary_path)
        summary_pure = PurePath(summary_str)
        return {
            ARTIFACT_KEY_BOOTSTRAP_SUMMARY: summary_str,
            "BOOTSTRAP_SUMMARY_PATH": summary_str,
            "BOOTSTRAP_SUMMARY_METAJSON": str(
                summary_pure.parent / f"{summary_pure.stem}.meta.json"
            ),
        }

    def install_to_global(self, *, workspace_root, runner_home):
        """Bootstrap install is handled by init_workspace() in bundle_loader."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
