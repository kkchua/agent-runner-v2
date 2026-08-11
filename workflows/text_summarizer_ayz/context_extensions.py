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
        "PARSED_DOCUMENT": "PARSED_DOCUMENT.txt",
        "ANALYSIS_RESULT": "ANALYSIS_RESULT.json",
        "TRANSFORMED_CONTENT": "TRANSFORMED_CONTENT.json",
        "OUTPUT_FILE": "{input_stem}-{seq}.md",
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
            get_governance_runtime_root() / "BASE_COMPOSITION_STANDARD_v1.0.md"
        )
        resolve_input_artifacts(result, state, workspace_root, self.INPUT_ARTIFACTS)
        resolve_output_artifacts(result, state, workspace_root, self.OUTPUT_ARTIFACTS)

        # Derive OUTPUT_FILE filename from input filename: {input_stem}-{seq}.md
        source_path = result.get("SOURCE_DOCUMENT_FILE", "")
        if source_path:
            stem = Path(source_path).stem
            job_id = str(state.get("job_id") or "unknown")
            seq = str(state.get("seq") or "001").zfill(3)
            output_dir = Path(workspace_root) / "output" / job_id
            result["OUTPUT_FILE"] = str(output_dir / f"{stem}-{seq}.md")

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        return {"status": "NO_OP"}
