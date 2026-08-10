"""Context extensions for text_summarizer_ayz workflow.

Registers artifact keys and resolves them to absolute paths at runtime.
The TextSummarizerExtensions class provides the bridge between artifact
key definitions and the filesystem paths the runner uses.

This workflow transforms long text documents into condensed summaries
and key points lists following the Input Transformation pattern
(Composition System Standard Pattern 2).

Artifacts produced:
- PARSED_DOCUMENT: Layer 1 structured document tree (JSON)
- KEY_POINTS_DATA: Layer 2 key point components (JSON)
- REDUNDANCY_CLUSTERS: Layer 2 redundancy analysis (JSON)
- CONTENT_BLOCKS: Layer 2 content blocks (JSON)
- OUTPUT_ASSEMBLY: Layer 3 output document (JSON)
- VALIDATION_REPORT: Invariant and constraint results (Markdown)
- CONDENSED_SUMMARY: Final prose summary (Markdown)
- KEY_POINTS_LIST: Final key points list (Markdown)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
    resolve_input_specs,
)


class TextSummarizerExtensions(WorkflowExtensions):
    """Artifact key registration and path resolution for text_summarizer_ayz.

    Provides:
    - Artifact key registration for all pipeline artifacts.
    - Path resolution for intermediate and final output artifacts.
    - Governance and platform runtime root injection.
    - Input spec resolution for the SOURCE_TEXT_FILE input.
    """

    workflow_name = "text_summarizer_ayz"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time. All paths are relative
        to the workspace root.
        """
        base = "jobs/{job_id}"
        inp = f"{base}/input"
        out = f"{base}/output"
        work = f"{base}/work"
        intermediate = f"{work}/intermediate"
        reports = f"{work}/reports"

        return {
            # -- Input --
            "SOURCE_TEXT_FILE": f"{inp}/source_document",

            # -- Phase 1: Input Processing (Layer 1) --
            "PARSED_DOCUMENT": f"{intermediate}/PARSED_DOCUMENT-{{seq}}.json",

            # -- Phase 1: Validation --
            "VALIDATION_REPORT": f"{reports}/VALIDATION_REPORT-{{seq}}.md",

            # -- Phase 2: Transformation (Layer 2) --
            "KEY_POINTS_DATA": f"{intermediate}/KEY_POINTS_DATA-{{seq}}.json",
            "REDUNDANCY_CLUSTERS": f"{intermediate}/REDUNDANCY_CLUSTERS-{{seq}}.json",
            "CONTENT_BLOCKS": f"{intermediate}/CONTENT_BLOCKS-{{seq}}.json",

            # -- Phase 3: Output (Layer 3) --
            "OUTPUT_ASSEMBLY": f"{intermediate}/OUTPUT_ASSEMBLY-{{seq}}.json",

            # -- Final Outputs --
            "CONDENSED_SUMMARY": f"{out}/CONDENSED_SUMMARY-{{seq}}.md",
            "KEY_POINTS_LIST": f"{out}/KEY_POINTS_LIST-{{seq}}.md",
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

        Provides absolute paths for all pipeline artifacts, governance
        and platform runtime roots, and resolves the input spec path.
        """
        result: dict[str, str] = {}
        workspace_root = Path(
            project_root or get_workspace_root() or Path.cwd()
        )

        # Governance and platform runtime roots
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )

        # Resolve input spec filename from operator console to Specs/ paths
        resolve_input_specs(
            result, state, self.workflow_name, ["SOURCE_TEXT_FILE"]
        )

        # Resolve all artifact keys to absolute paths
        artifacts = state.get("artifacts") or {}
        for key, rel_path in self.register_artifact_keys().items():
            # Already resolved by resolve_input_specs() -- do not overwrite
            if key in result:
                continue
            existing = artifacts.get(key)
            if existing and Path(existing).is_absolute():
                result[key] = existing
                continue
            result[key] = str(workspace_root / rel_path)

        return result

    def install_to_global(
        self, *, workspace_root: str | Path, runner_home: str | Path
    ) -> dict[str, Any]:
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(
        self, *, workspace_root: str | Path
    ) -> dict[str, Any]:
        """Sync via ukbe-run-agent sync-workflows CLI instead."""
        return {"status": "NO_OP"}
