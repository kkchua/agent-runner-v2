"""Context extensions for agnes_media_gen_v1 workflow.

This module provides the WorkflowExtensions interface for the media
generation workflow, including artifact path registration, prompt context
injection, and Layer 1/Layer 2 governance root resolution.

The workflow operates on a target repository containing step directories
(step_00 through step_04) and archive directories. All paths are resolved
relative to the target repository root (the workspace root).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class AgnesMediaGenExtensions(WorkflowExtensions):
    """Workflow extension hooks for agnes_media_gen_v1.

    Provides artifact path registration for the media generation pipeline
    and injects step directory paths, configuration paths, and governance
    roots into the prompt/action context.
    """

    workflow_name = "agnes_media_gen_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        Paths are relative to the target repository root. The index
        manifests reside in fixed step directories and are overwritten
        each run. Historical tracking is handled by the archive pattern.

        Returns:
            dict mapping artifact keys to relative path strings.
        """
        return {
            "IMAGE_DESCRIPTIONS": "step_01/index.json",
            "PROMPT_VARIANTS": "step_02/index.json",
            "IMAGE_INDEX": "step_03/index.json",
            "VIDEO_INDEX": "step_04/index.json",
            "MEDIA_CONFIG": "config.json",
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
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Step directory paths (step_00 through step_04)
        - Step archive directory paths
        - Media configuration file path
        - Input image directory and archive paths
        - Resolved artifact paths from register_artifact_keys()

        All paths are resolved to absolute paths relative to the
        target repository root.
        """
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        # Resolve target repository root
        effective_root = Path(project_root or get_workspace_root() or Path.cwd())

        # Step active directories
        result["STEP_00_DIR"] = str(effective_root / "step_00")
        result["STEP_00_ARCHIVE"] = str(effective_root / "step_00_archive")
        result["STEP_01_DIR"] = str(effective_root / "step_01")
        result["STEP_01_ARCHIVE"] = str(effective_root / "step_01_archive")
        result["STEP_02_DIR"] = str(effective_root / "step_02")
        result["STEP_02_ARCHIVE"] = str(effective_root / "step_02_archive")
        result["STEP_03_DIR"] = str(effective_root / "step_03")
        result["STEP_03_ARCHIVE"] = str(effective_root / "step_03_archive")
        result["STEP_04_DIR"] = str(effective_root / "step_04")
        result["STEP_04_ARCHIVE"] = str(effective_root / "step_04_archive")

        # Input image directory and archive (aliases for step_00)
        result["IMAGE_INPUT_DIR"] = str(effective_root / "step_00")
        result["IMAGE_INPUT_ARCHIVE"] = str(effective_root / "step_00_archive")

        # Resolve artifact paths to absolute
        for key, rel_path in self.register_artifact_keys().items():
            result[key] = str(effective_root / rel_path)

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts.

        Returns:
            dict with NO_OP status indicating no installation needed.
        """
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via ukbe-run-agent sync-workflows CLI instead.

        Returns:
            dict with NO_OP status indicating no direct sync needed.
        """
        return {"status": "NO_OP"}
