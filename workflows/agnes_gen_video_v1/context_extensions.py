"""Context extensions for agnes_media_gen_v1 workflow.

This module provides the WorkflowExtensions interface for the Agnes Media
Generation v1 workflow, including artifact path registration, prompt context
injection for step directory paths, and Layer 1/Layer 2 governance root
resolution.

All runtime paths are resolved relative to the target repository root
(workspace_root) at job start time. No user-provided inputs are required;
the workflow defines its own folder structure (step_00/ through step_04/
with corresponding _archive/ folders) in the target repository.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class AgnesMediaGenExtensions(WorkflowExtensions):
    """Workflow extension hooks for agnes_media_gen_v1.

    Provides:
    - Artifact key registration for output index files (IMAGE_DESCRIPTIONS,
      PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX).
    - Prompt context injection for all step directory paths, media config
      path, and governance/platform runtime roots.
    - NO_OP implementations for install_to_global and sync_to_backend.
    """

    workflow_name = "agnes_media_gen_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to absolute-path mappings.

        All paths are absolute, resolved from the target repository root.
        These represent the index.json files produced by each processing step.

        Returns:
            Dictionary mapping artifact keys to absolute path patterns.
        """
        from agent_runner_v2.runtime_context import get_workspace_root

        workspace_root = get_workspace_root() or "{workspace_root}"
        return {
            "IMAGE_DESCRIPTIONS": f"{workspace_root}/step_01/index.json",
            "PROMPT_VARIANTS": f"{workspace_root}/step_02/index.json",
            "IMAGE_INDEX": f"{workspace_root}/step_03/index.json",
            "VIDEO_INDEX": f"{workspace_root}/step_04/index.json",
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
        """Build context extensions for agnes_media_gen_v1 workflow.

        Provides:
        - Absolute paths for all step directories (step_00/ through step_04/)
          and their corresponding archive directories.
        - Absolute path for the media configuration file (config.json).
        - Layer 1 governance runtime root (global path).
        - Layer 2 platform runtime root (global path).
        - Resolved artifact paths from register_artifact_keys() as absolute.

        All paths are resolved to absolute using workspace_root. The daemon
        runs from a different working directory, so relative paths would
        fail at runtime.
        """
        result: dict[str, str] = {}

        # Resolve workspace root
        workspace_root = Path(
            project_root or get_workspace_root() or Path.cwd()
        )

        # Step directories (absolute paths)
        step_dirs = [
            ("STEP_00_DIR", "step_00"),
            ("STEP_00_ARCHIVE", "step_00_archive"),
            ("STEP_01_DIR", "step_01"),
            ("STEP_01_ARCHIVE", "step_01_archive"),
            ("STEP_02_DIR", "step_02"),
            ("STEP_02_ARCHIVE", "step_02_archive"),
            ("STEP_03_DIR", "step_03"),
            ("STEP_03_ARCHIVE", "step_03_archive"),
            ("STEP_04_DIR", "step_04"),
            ("STEP_04_ARCHIVE", "step_04_archive"),
        ]
        for key, dirname in step_dirs:
            result[key] = str(workspace_root / dirname)

        # Media configuration file (absolute path)
        result["MEDIA_CONFIG"] = str(workspace_root / "config.json")

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )

        # Artifact paths from register_artifact_keys() are already absolute
        for key, abs_path in self.register_artifact_keys().items():
            result[key] = abs_path

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts.

        The workflow operates entirely within the target repository and
        does not install files to the global runner home.
        """
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via ukbe-run-agent sync-workflows CLI instead.

        Backend sync is handled by the CLI command, not by this hook.
        """
        return {"status": "NO_OP"}
