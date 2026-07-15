"""Context extensions for image_csv_gen_v3 workflow.

Provides IMAGE_CSV_SUBMIT_RESULT_METAJSON pointing to the absolute path
where submit_comfyui writes its sidecar, so the runner can find it.
"""

from __future__ import annotations

from pathlib import Path

from agent_runner_v2.runtime_context import resolve_artifact_root


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    """Inject IMAGE_CSV_SUBMIT_RESULT_METAJSON for the submit_prompts action."""
    result: dict[str, str] = {}

    run_dir = ctx.get("IMAGE_CSV_RUN_DIR", "")
    project_root = resolve_artifact_root()
    if run_dir and project_root:
        abs_run_dir = str(Path(project_root) / run_dir)
        result["IMAGE_CSV_RUN_DIR"] = abs_run_dir
        result["IMAGE_CSV_SUBMIT_RESULT_PATH"] = str(
            Path(abs_run_dir) / "submission_results.json"
        )
        result["IMAGE_CSV_SUBMIT_RESULT_METAJSON"] = str(
            Path(abs_run_dir) / "submission_results.meta.json"
        )

    return result
