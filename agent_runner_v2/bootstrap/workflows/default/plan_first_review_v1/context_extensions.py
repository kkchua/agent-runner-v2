from __future__ import annotations

from pathlib import Path

from agent_runner_v2.artifact_keys import (
    ARTIFACT_KEY_PLANNING_FOLDER,
    ARTIFACT_KEY_QWEN_PLAN,
    ARTIFACT_KEY_CODEX_REVIEW,
    ARTIFACT_KEY_REQUIREMENTS,
)
from agent_runner_v2.constants import (
    ARTIFACT_PATH_QWEN_PLAN,
    ARTIFACT_PATH_CODEX_REVIEW,
    ARTIFACT_PATH_REQUIREMENTS,
)

# PRIOR_PLAN_FILE is a prompt-only alias — NOT an artifact key.
_PRIOR_PLAN_FILE = "PRIOR_PLAN_FILE"


class WorkflowExtensions:
    def build_context_extensions(
        self,
        *,
        state: dict,
        step: str,
        step_cfg: dict,
        ctx: dict,
        project_root: Path,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        artifacts = state.get("artifacts") or {}
        planning_folder = artifacts.get(ARTIFACT_KEY_PLANNING_FOLDER, "")
        revision = state.get("plan_revision", 1)
        baseline = state.get("requirements_baseline", 1)

        if not planning_folder:
            return result

        if step == "formalize_requirements":
            result[ARTIFACT_KEY_REQUIREMENTS] = str(
                project_root / ARTIFACT_PATH_REQUIREMENTS(planning_folder, baseline)
            )

        elif step == "generate_plan":
            result[ARTIFACT_KEY_QWEN_PLAN] = str(
                project_root / ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision, baseline)
            )

        elif step == "codex_review":
            result[ARTIFACT_KEY_QWEN_PLAN] = str(
                project_root / ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision, baseline)
            )
            result[ARTIFACT_KEY_CODEX_REVIEW] = str(
                project_root / ARTIFACT_PATH_CODEX_REVIEW(planning_folder, revision, baseline)
            )

        elif step == "refine_plan":
            # PRIOR_PLAN_FILE: prompt-only alias (ctx injection only)
            result[_PRIOR_PLAN_FILE] = str(
                project_root / ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision, baseline)
            )
            result[ARTIFACT_KEY_QWEN_PLAN] = str(
                project_root / ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision + 1, baseline)
            )

        return result
