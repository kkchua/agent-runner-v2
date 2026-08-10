"""Context extensions for text_summarizer workflow.

Registers artifact keys and resolves them to absolute paths at runtime.
The TextSummarizerExtensions class provides the bridge between artifact
key definitions and the filesystem paths the runner uses.

This workflow transforms an input text file (.txt or .md) into a condensed
summary following the 4-stage pipeline: T1 (Key Point Extraction),
T2 (Redundancy Removal), T3 (Structure Assembly), T4 (Output Rendering).

All runtime paths are resolved relative to the workspace root at job
start time. Intermediate artifacts (Layer 1, 2, 3 meta content) are
placed under meta/ subdirectories within the job directory.
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


class TextSummarizerExtensions(WorkflowExtensions):
    """Workflow extension hooks for text_summarizer.

    Provides:
    - Artifact key registration for all input, output, intermediate,
      and processing artifacts defined in the artifact contract.
    - Prompt context injection for metadata directories and governance
      runtime roots.
    - NO_OP implementations for install_to_global and sync_to_backend.
    """

    workflow_name = "text_summarizer"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use {job_id} and {seq} placeholders that the
        runner resolves at execution time. All paths are relative to
        the workspace root.

        Returns:
            Dictionary mapping artifact keys to relative path patterns.
        """
        repo = "docs/repo/text_summarizer"
        run = f"{repo}/runs/{{job_id}}"
        meta = f"{run}/meta"
        l1 = f"{meta}/layer1"
        l2 = f"{meta}/layer2"
        l3 = f"{meta}/layer3"

        return {
            # -- Input --
            "INPUT_TEXT_FILE": f"{run}/input/{{input_filename}}",

            # -- Output --
            "SUMMARY_FILE": f"{run}/output/{{output_filename}}",

            # -- Layer 1: Input Parsing --
            "DOC_STRUCTURE_FILE": f"{l1}/doc_structure.json",
            "INPUT_VALIDATION_REPORT": f"{l1}/input_validation.json",

            # -- Layer 2: Transformation --
            "KEYPOINT_LIST_FILE": f"{l2}/keypoints.json",
            "REDUNDANCY_MAP_FILE": f"{l2}/redundancy_map.json",
            "CONTENT_BLOCK_LIST_FILE": f"{l2}/content_blocks.json",
            "STRUCTURE_MAP_FILE": f"{l2}/structure_map.json",
            "TRANSFORMATION_INVARIANT_REPORT": f"{l2}/invariant_report.json",

            # -- Layer 3: Output Rendering --
            "OUTPUT_DOC_FILE": f"{l3}/output_doc.json",
            "OUTPUT_METADATA_FILE": f"{l3}/output_metadata.json",
            "OUTPUT_VALIDATION_REPORT": f"{l3}/output_validation.json",

            # -- Processing --
            "RUNTIME_CONFIG_FILE": f"{meta}/runtime_config.json",

            # -- Review and Adjustment --
            "QUALITY_REVIEW_REPORT": f"{run}/quality_review.json",
            "ADJUSTED_CONFIG": f"{run}/adjusted_config.json",

            # -- Delivery --
            "SUMMARY_FILE_PROMOTED": f"{run}/promoted/{{output_filename}}",
            "COMPLETION_RESULT": f"{run}/completion_result.json",
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
        """Build context extensions for text_summarizer workflow.

        Provides:
        - Absolute paths for metadata directories (layer1/, layer2/, layer3/).
        - Absolute path for the runtime configuration file.
        - Layer 1 governance runtime root (global path).
        - Layer 2 platform runtime root (global path).
        - Resolved artifact paths from register_artifact_keys() as absolute.

        All paths are resolved to absolute using workspace_root.
        """
        result: dict[str, str] = {}

        # Resolve workspace root
        workspace_root = Path(
            project_root or get_workspace_root() or Path.cwd()
        )

        # Metadata directories (absolute paths)
        repo = workspace_root / "docs" / "repo" / "text_summarizer"
        run = repo / "runs" / str(state.get("job_id", "unknown"))
        meta = run / "meta"

        result["META_DIR"] = str(meta)
        result["L1_META_DIR"] = str(meta / "layer1")
        result["L2_META_DIR"] = str(meta / "layer2")
        result["L3_META_DIR"] = str(meta / "layer3")
        result["INPUT_DIR"] = str(run / "input")
        result["OUTPUT_DIR"] = str(run / "output")
        result["PROMOTED_DIR"] = str(run / "promoted")

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )

        # Resolve all artifact keys to absolute paths
        for key, rel_path in self.register_artifact_keys().items():
            existing = (state.get("artifacts") or {}).get(key)
            if existing and Path(existing).is_absolute():
                result[key] = existing
                continue
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
