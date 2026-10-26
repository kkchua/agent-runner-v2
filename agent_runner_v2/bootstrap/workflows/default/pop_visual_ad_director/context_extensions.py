"""Context extensions for Pop Visual Ad Director."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
    resolve_input_artifacts,
    resolve_output_artifacts,
)


class PopVisualAdDirectorExtensions(WorkflowExtensions):
    workflow_name = "pop_visual_ad_director"

    # -- Input artifacts: resolved to {workspace_root}/input/ --
    INPUT_ARTIFACTS: dict[str, str] = {
        "REQUIREMENT_INPUT_FILE": "{source_file}",
    }

    # -- Output artifacts: resolved to {workspace_root}/output/{job_id}/ --
    OUTPUT_ARTIFACTS: dict[str, str] = {
        # Domain artifacts
        "COLLECTED_REQUIREMENTS_FILE": "{codename}/collected_requirements.json",
        "STORYBOARD_FILE": "{codename}/storyboard.md",
        "VIDEO_PROMPTS_FILE": "{codename}/video_prompts.json",
        "VIDEO_CLIPS_FILE": "{codename}/video_clips/manifest.json",
        "FINAL_VIDEO_FILE": "{codename}/final_video.mp4",
        # Infrastructure artifacts
        "TARGET_EXTENSIONS_FILE": "context_extensions.py",
        "TARGET_MANIFEST_FILE": "workflow.toml",
        "AGB_VALIDATION_FINDINGS": "VALIDATION_FINDINGS-{seq}.md",
        "AGB_PACKAGE_REVIEW": "PACKAGE_REVIEW-{seq}.md",
        "AGB_GATEKEEP_REPORT": "GATEKEEP_PACKAGE-{seq}.md",
        "TARGET_PACKAGE_DIR": "",
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
        return result

    def install_to_global(self, *, workspace_root, runner_home):
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        return {"status": "NO_OP"}
