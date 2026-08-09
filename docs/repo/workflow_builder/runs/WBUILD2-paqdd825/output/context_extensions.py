"""Context extensions for video_campaign_manuscript -- Composition System.

This module provides the WorkflowExtensions interface for the
video_campaign_manuscript workflow, which resolves declarative component
compositions into self-contained video campaign production manuscripts.

The workflow implements the three-layer composition architecture:
- Layer 1: Component Library (reusable creative building blocks)
- Layer 2: Composition Definitions (declarative assembly instructions)
- Layer 3: Resolved Outputs (self-contained production manuscripts)

All runtime paths are resolved relative to the target repository root
(workspace_root) at job start time.
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


class VideoCampaignManuscriptExtensions(WorkflowExtensions):
    """Workflow extension hooks for video_campaign_manuscript.

    Provides:
    - Artifact key registration for all composition system artifacts
    - Prompt context injection for composition resolution paths
    - Layer 1/Layer 2 governance root resolution
    """

    workflow_name = "video_campaign_manuscript"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        All paths are relative to the run root, using {job_id} and {seq}
        placeholders. The runner resolves these to absolute paths at runtime.

        Includes both input artifacts (user-provided directories and upstream
        schema files) and output artifacts (produced during workflow execution).
        """
        return {
            # --- Input artifacts (user-provided or upstream) ---
            "COMPONENT_LIBRARY_DIR": (
                "docs/repo/workflow_builder/runs/{job_id}/input/components"
            ),
            "COMPOSITIONS_DIR": (
                "docs/repo/workflow_builder/runs/{job_id}/input/compositions"
            ),
            "DATA_SOURCE_DIR": (
                "docs/repo/workflow_builder/runs/{job_id}/input/data_sources"
            ),
            "COMPONENT_SCHEMA_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "COMPONENT_SCHEMA-{seq}.md"
            ),
            "OUTPUT_FORMAT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "OUTPUT_FORMAT-{seq}.md"
            ),

            # --- Output artifacts (produced by workflow steps) ---
            "COMPONENT_INVENTORY_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "COMPONENT_INVENTORY-{seq}.yaml"
            ),
            "VALIDATION_REPORT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "VALIDATION_REPORT-{seq}.yaml"
            ),
            "RESOLUTION_PLAN_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "RESOLUTION_PLAN-{seq}.yaml"
            ),
            "OUTPUT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "OUTPUT-{seq}.md"
            ),
            "REVIEW_FILE_SUGGESTED": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "REVIEW_OUTPUT-{seq}.md"
            ),

            # --- Infrastructure artifacts ---
            "PROMOTE_RESULT": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "PROMOTE_RESULT-{seq}.json"
            ),
            "COMPLETION_RESULT": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "COMPLETION_RESULT-{seq}.json"
            ),
            "WORKFLOW_MANIFEST_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "output/workflow.toml"
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
        """Build context extensions for video_campaign_manuscript.

        Provides:
        - Absolute paths for all composition system artifacts
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        """
        result: dict[str, str] = {}

        # Resolve workspace root
        workspace_root = Path(
            project_root or get_workspace_root() or Path.cwd()
        )

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )

        # Artifact paths from register_artifact_keys() -- resolve to absolute
        for key, rel_path in self.register_artifact_keys().items():
            result[key] = str(workspace_root / rel_path)

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
