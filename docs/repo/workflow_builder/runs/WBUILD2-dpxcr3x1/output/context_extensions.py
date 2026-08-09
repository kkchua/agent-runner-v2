"""Context extensions for video_campaign_manuscript -- Composition System.

This module provides the WorkflowExtensions interface for the
video_campaign_manuscript workflow, which implements the three-layer
composition architecture for short-form video campaign manuscripts.

The workflow:
- Scans and validates a component library (Layer 1)
- Resolves declarative composition definitions (Layer 2)
- Produces fully resolved video production manuscripts (Layer 3)

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
    - Prompt context injection for composition system paths
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

        This includes both output artifacts (produced by steps) and input
        artifacts (consumed by steps), so that the runner can verify
        existence before step execution.
        """
        return {
            # Workflow inputs -- user-provided directories
            "COMPONENT_LIBRARY_DIR": "docs/repo/workflow_builder/runs/{job_id}/inputs/components",
            "COMPOSITIONS_DIR": "docs/repo/workflow_builder/runs/{job_id}/inputs/compositions",
            "DATA_SOURCE_DIR": "docs/repo/workflow_builder/runs/{job_id}/inputs/data_sources",

            # Workflow inputs -- supplementary schema files (from builder phases)
            "COMPONENT_SCHEMA_FILE": "docs/repo/workflow_builder/runs/{job_id}/schema/component_schema.md",
            "COMPOSITION_FORMAT_FILE": "docs/repo/workflow_builder/runs/{job_id}/schema/composition_format_spec.md",
            "OUTPUT_FORMAT_FILE": "docs/repo/workflow_builder/runs/{job_id}/schema/output_format_spec.md",

            # Step 1 outputs: scan_components
            "COMPONENT_INVENTORY_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/component_inventory.json",
            "VALIDATION_REPORT_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/component_validation_report.md",

            # Step 2 output: plan_compositions
            "RESOLUTION_PLAN_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/resolution_plan.md",

            # Step 3 / Step 5 output: generate_output / refine_output
            "OUTPUT_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/manuscript_output.md",

            # Step 4 output: review_output
            "REVIEW_FILE_SUGGESTED": "docs/repo/workflow_builder/runs/{job_id}/output/output_review.md",
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
        - Composition System Standard reference path
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

        # Composition System Standard reference
        result["COMPOSITION_SYSTEM_STANDARD"] = str(
            workspace_root / "docs" / "repo" / "workflow_builder" / "standards" / "COMPOSITION_SYSTEM_STANDARD.md"
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
