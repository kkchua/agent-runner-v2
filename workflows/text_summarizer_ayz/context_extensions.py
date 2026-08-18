"""Context extensions for Text Summarizer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
    resolve_input_artifacts,
    resolve_output_artifacts,
)


class TextSummarizerAyzExtensions(WorkflowExtensions):
    workflow_name = "text_summarizer_ayz"

    # -- Input artifacts: resolved to {workspace_root}/input/ --
    INPUT_ARTIFACTS: dict[str, str] = {
        "SOURCE_DOCUMENT_FILE": "",
    }

    # -- Output artifacts: resolved to {workspace_root}/output/{job_id}/ --
    OUTPUT_ARTIFACTS: dict[str, str] = {
        "PARSED_DOCUMENT": "PARSED_DOCUMENT.json",
        "STRUCTURAL_ANALYSIS": "STRUCTURAL_ANALYSIS.json",
        "TRANSFORMED_CONTENT": "TRANSFORMED_CONTENT.json",
        "OUTPUT_FILE": "OUTPUT_FILE.md",
    }

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        combined: dict[str, str] = {}
        for key in self.INPUT_ARTIFACTS:
            combined[key] = "input/"
        for key, pattern in self.OUTPUT_ARTIFACTS.items():
            combined[key] = f"output/{job_id}/{pattern}"
        return combined

    def build_context_extensions(
        self, *, state, step, step_cfg, ctx, project_root=None,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        workspace_root = Path(project_root or get_workspace_root() or Path.cwd()).resolve()
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())
        result["BASE_COMPOSITION_STANDARD"] = str(
            get_governance_runtime_root() / "BCS_v2.0.md"
        )
        resolve_input_artifacts(result, state, workspace_root, self.INPUT_ARTIFACTS)
        resolve_output_artifacts(result, state, workspace_root, self.OUTPUT_ARTIFACTS)

        # -- Dynamic Output Naming: use source doc filename + impl suffix --
        artifacts = state.get("artifacts") or {}
        source_path = artifacts.get("SOURCE_DOCUMENT_FILE", "")
        if source_path:
            source_filename = Path(source_path).stem
            result["source_doc_filename"] = source_filename

            # Determine output suffix from implementation name
            impl_name = artifacts.get("IMPLEMENTATION", "default")
            impl_suffix_map = {
                "default": "_summary",
                "key_points": "_bulletpoint",
            }
            output_suffix = impl_suffix_map.get(impl_name, f"_{impl_name}")

            # Override the static output path with the dynamic filename
            job_id = state.get("job_id", "unknown")
            result["OUTPUT_FILE"] = str(
                workspace_root / "output" / job_id / f"{source_filename}{output_suffix}.md"
            )

        # -- Inject file content for prompt steps --
        parsed_path = result.get("PARSED_DOCUMENT", "")
        if parsed_path and Path(parsed_path).is_file():
            try:
                result["PARSED_DOCUMENT_CONTENT"] = Path(parsed_path).read_text(encoding="utf-8")
            except Exception:
                result["PARSED_DOCUMENT_CONTENT"] = "(unable to read PARSED_DOCUMENT)"

        struct_path = result.get("STRUCTURAL_ANALYSIS", "")
        if struct_path and Path(struct_path).is_file():
            try:
                result["STRUCTURAL_ANALYSIS_CONTENT"] = Path(struct_path).read_text(encoding="utf-8")
            except Exception:
                result["STRUCTURAL_ANALYSIS_CONTENT"] = "(unable to read STRUCTURAL_ANALYSIS)"

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        return {"status": "NO_OP"}
