"""Context extensions for 00_bootstrap_lifecycle_admin_v1."""

from __future__ import annotations

from pathlib import Path, PurePath

from agent_runner_v2.constants import ARTIFACT_KEY_BOOTSTRAP_SUMMARY
from agent_runner_v2.runtime_context import JOBS_ROOT, resolve_repo_or_runtime_path


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    job_id = str(state.get("job_id") or "00BOOT").strip()
    root = Path(project_root or Path.cwd()).resolve()
    summary_name = f"{job_id}-bootstrap-lifecycle-summary.md"
    summary_path = resolve_repo_or_runtime_path(
        f"docs/system/00_governance/bootstrap/{summary_name}",
        project_root=root,
        runtime_root=JOBS_ROOT,
    )
    summary_str = str(summary_path)
    summary_pure = PurePath(summary_str)
    return {
        ARTIFACT_KEY_BOOTSTRAP_SUMMARY: summary_str,
        "BOOTSTRAP_SUMMARY_PATH": summary_str,
        "BOOTSTRAP_SUMMARY_METAJSON": str(summary_pure.parent / f"{summary_pure.stem}.meta.json"),
    }
