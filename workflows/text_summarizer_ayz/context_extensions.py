"""Context extensions for Text Summarizer workflow (text_summarizer_ayz).

Registers artifact keys and resolves them to absolute paths at runtime.
The TextSummarizerExtensions class provides the bridge between artifact
key definitions and the filesystem paths the runner uses.

This workflow transforms long-form text documents into condensed summaries
or ranked key points using a three-layer pipeline:

  Layer 1: Input Parsing (parse_input)
  Layer 2: Transformation (analyze_structure, score_importance, identify_core_message)
  Layer 3: Output Rendering (render_output, validate_output)

Two implementations are supported:
  - summary (default): Condensed prose summary (3-block structure)
  - key_points: Ordered list of extracted key points with importance scores

Artifact flow:
  INPUT_FILE -> PARSED_DOCUMENT -> ANALYZED_STRUCTURE -> SCORED_SEGMENTS
  -> ANALYSIS_RESULT -> OUTPUT_DOCUMENT -> OUTPUT_SUMMARY / OUTPUT_KEY_POINTS
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
)


class TextSummarizerExtensions(WorkflowExtensions):
    """Artifact key registration and path resolution for Text Summarizer."""

    workflow_name = "text_summarizer_ayz"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time. All paths are relative
        to the workspace root.

        Input artifacts are resolved by the runner from operator context.
        Intermediate artifacts live under ``{job_id}/intermediate/``.
        Output artifacts live under ``{job_id}/output/``.
        """
        return {
            # -- Input (external, provided at invocation) --
            "INPUT_FILE": "input/{input_filename}",

            # -- Intermediate artifacts (Layer 1) --
            "PARSED_DOCUMENT": "{job_id}/intermediate/PARSED_DOCUMENT-{seq}.json",

            # -- Intermediate artifacts (Layer 2) --
            "ANALYZED_STRUCTURE": "{job_id}/intermediate/ANALYZED_STRUCTURE-{seq}.json",
            "SCORED_SEGMENTS": "{job_id}/intermediate/SCORED_SEGMENTS-{seq}.json",
            "ANALYSIS_RESULT": "{job_id}/intermediate/ANALYSIS_RESULT-{seq}.json",

            # -- Intermediate artifacts (Layer 3) --
            "OUTPUT_DOCUMENT": "{job_id}/intermediate/OUTPUT_DOCUMENT-{seq}.json",
            "VALIDATION_RESULT": "{job_id}/intermediate/VALIDATION_RESULT-{seq}.json",

            # -- Output artifacts (conditional on implementation) --
            "OUTPUT_SUMMARY": "{job_id}/output/OUTPUT_SUMMARY-{seq}.txt",
            "OUTPUT_KEY_POINTS": "{job_id}/output/OUTPUT_KEY_POINTS-{seq}.txt",
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

        Resolves {job_id} and {seq} placeholders in path templates.
        The {seq} placeholder is resolved to a zero-padded sequence
        number derived from the current artifact version count.
        """
        result: dict[str, str] = {}
        workspace_root = Path(
            project_root or get_workspace_root() or Path.cwd()
        )

        job_id = ctx.get("job_id") or state.get("job_id") or "unknown"

        # Determine current sequence number from artifacts state
        artifacts = state.get("artifacts") or {}
        seq = self._compute_seq(artifacts)

        # Resolve input filename from operator context
        input_filename = ctx.get("INPUT_FILE", "") or ""
        if input_filename:
            result["INPUT_FILE"] = str(
                workspace_root / "input" / input_filename
            )

        # Resolve all registered artifact keys
        for key, rel_path in self.register_artifact_keys().items():
            if key in result:
                continue
            existing = artifacts.get(key)
            if existing and Path(existing).is_absolute():
                result[key] = existing
                continue
            resolved_path = rel_path.replace("{job_id}", job_id)
            resolved_path = resolved_path.replace("{seq}", seq)
            resolved_path = resolved_path.replace(
                "{input_filename}", input_filename if input_filename else "input.txt"
            )
            result[key] = str(workspace_root / resolved_path)

        return result

    @staticmethod
    def _compute_seq(artifacts: dict[str, Any]) -> str:
        """Compute zero-padded sequence number from artifact count.

        Counts how many artifacts already have a version recorded
        and returns the next sequence number, zero-padded to 2 digits.
        """
        count = 0
        for key, value in artifacts.items():
            if isinstance(value, str) and value:
                count += 1
        return f"{count + 1:02d}"

    def install_to_global(
        self, *, workspace_root: str | Path, runner_home: str | Path
    ) -> dict[str, Any]:
        """No global installation required for this workflow."""
        return {"status": "NO_OP"}

    def sync_to_backend(
        self, *, workspace_root: str | Path
    ) -> dict[str, Any]:
        """No backend sync required for this workflow."""
        return {"status": "NO_OP"}
