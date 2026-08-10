"""Context extensions for the text_summarizer_ayz workflow.

Registers artifact keys and resolves them to absolute paths at runtime.
The TextSummarizerExtensions class provides the bridge between artifact
key definitions and the filesystem paths the runner uses.

This workflow transforms a long-form text document into a condensed
summary (prose) and a key points list (ordered with importance scores)
using a 7-stage pipeline following Pattern 2 (Input Transformation).

Identity:
    generator_name: text_summarizer_ayz
    version: 1.0.0
    pattern: Input Transformation (Pattern 2)
    output_types: condensed_summary, key_points_list
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
)


class TextSummarizerExtensions(WorkflowExtensions):
    """Artifact key registration and path resolution for text_summarizer_ayz."""

    workflow_name = "text_summarizer_ayz"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time. All paths are relative
        to the workspace root.

        The artifact keys are organized by pipeline stage and follow
        the ARTIFACT_CONTRACT-01 specification.

        Returns:
            Dict mapping artifact key strings to repo-relative path
            templates.
        """
        return {
            # -- Input Artifacts --
            "SOURCE_TEXT": "input/SOURCE_TEXT.md",
            "RUNTIME_CONFIG": "input/RUNTIME_CONFIG.json",

            # -- Pipeline Configuration --
            "CONFIG_STATE": "work/CONFIG_STATE-{seq}.json",

            # -- Layer 1: Input Parsing (Stage 0) --
            "PARSED_DOCUMENT": "work/intermediate/PARSED_DOCUMENT-{seq}.json",
            "VALIDATION_INPUT_REPORT": "work/reports/VALIDATION_INPUT-{seq}.json",

            # -- Layer 2: Transformation (Stages 1-4) --
            "IMPORTANCE_ANALYSIS": "work/intermediate/IMPORTANCE_ANALYSIS-{seq}.json",
            "INV_REPORT_S1": "work/reports/INV_REPORT_S1-{seq}.json",
            "REDUNDANCY_CLUSTERS": "work/intermediate/REDUNDANCY_CLUSTERS-{seq}.json",
            "INV_REPORT_S2": "work/reports/INV_REPORT_S2-{seq}.json",
            "KEY_POINTS_RAW": "work/intermediate/KEY_POINTS_RAW-{seq}.json",
            "INV_REPORT_S3": "work/reports/INV_REPORT_S3-{seq}.json",
            "SUMMARY_BLOCKS": "work/intermediate/SUMMARY_BLOCKS-{seq}.json",
            "INV_REPORT_S4": "work/reports/INV_REPORT_S4-{seq}.json",

            # -- Layer 3: Output Rendering (Stages 5-6) --
            "OUTPUT_DOCUMENTS": "work/intermediate/OUTPUT_DOCUMENTS-{seq}.json",
            "INV_REPORT_S5": "work/reports/INV_REPORT_S5-{seq}.json",

            # -- Final Output Artifacts --
            "CONDENSED_SUMMARY": "output/CONDENSED_SUMMARY.md",
            "KEY_POINTS_LIST": "output/KEY_POINTS_LIST.md",

            # -- Validation Artifacts --
            "VALIDATION_REPORT": "work/reports/VALIDATION_REPORT-{seq}.json",
            "QUALITY_REVIEW_REPORT": "work/reports/QUALITY_REVIEW-{seq}.json",
            "ADJUSTED_CONFIG": "work/ADJUSTED_CONFIG-{seq}.json",

            # -- Delivery Artifacts --
            "CONDENSED_SUMMARY_PROMOTED": "output/CONDENSED_SUMMARY.md",
            "KEY_POINTS_LIST_PROMOTED": "output/KEY_POINTS_LIST.md",
            "COMPLETION_RESULT": "work/COMPLETION_RESULT-{seq}.json",

            # -- Error and Log Artifacts --
            "ERROR_REPORT": "work/reports/ERROR_REPORT-{seq}.json",
            "EXECUTION_LOG": "work/logs/EXECUTION_LOG-{seq}.log",
        }

    def build_context_extensions(
        self,
        *,
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        ctx: dict[str, str],
        project_root: str | Path | None = None,
    ) -> dict[str, str]:
        """Resolve all artifact keys to absolute filesystem paths.

        Provides the prompt templates with absolute paths to all
        artifacts, plus workflow identity variables.

        Returns:
            Dict of context-variable name to value strings.
        """
        result: dict[str, str] = {}
        workspace_root = Path(project_root or Path.cwd())

        # Workflow identity
        result["CODENAME"] = "text_summarizer_ayz"
        result["GENERATOR_NAME"] = "text_summarizer_ayz"
        result["GENERATOR_VERSION"] = "1.0.0"
        result["PATTERN"] = "Input Transformation (Pattern 2)"
        result["OUTPUT_TYPES"] = "condensed_summary, key_points_list"

        # Resolve all artifact keys to absolute paths
        artifacts = state.get("artifacts") or {}
        for key, rel_path in self.register_artifact_keys().items():
            existing = artifacts.get(key)
            if existing and Path(existing).is_absolute():
                result[key] = existing
                continue
            result[key] = str(workspace_root / rel_path)

        return result

    def install_to_global(
        self, *, workspace_root: str | Path, runner_home: str | Path
    ) -> dict[str, Any]:
        """Install workflow artifacts to the global runner home.

        This workflow has no global installation requirements.

        Returns:
            Dict with status NO_OP.
        """
        return {"status": "NO_OP"}

    def sync_to_backend(
        self, *, workspace_root: str | Path
    ) -> dict[str, Any]:
        """Sync workflow definition to the backend registry.

        This workflow does not sync to the backend.

        Returns:
            Dict with status NO_OP.
        """
        return {"status": "NO_OP"}
