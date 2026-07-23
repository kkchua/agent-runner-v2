"""Context extensions for sdlc_70_validation_v1 workflow."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE, resolve_next_seq
from agent_runner_v2.runtime_context import get_runner_home, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


def _extract_slug_from_path(file_path: str) -> str:
    """Extract the slug from an SDLC artifact filename."""
    if not file_path:
        return "unknown"
    filename = Path(file_path).stem
    match = re.search(r"_(.+)$", filename)
    if match:
        return match.group(1)
    return "unknown"


class Sdlc70ValidationExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_70_validation_v1."""

    workflow_name = "sdlc_70_validation_v1"

    def register_artifact_keys(self, *, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
        date_str = dt.datetime.now().strftime("%Y%m%d")
        return {
            "VAL_FILE": f"{SDLC_DELIVERY_BASE}/70_validations/VAL-{date_str}-{{seq}}_{{slug}}.md",
            "CRITIQUE_FILE_SUGGESTED": f"{SDLC_DELIVERY_BASE}/80_reviews/{{slug}}-CRITIQUE-70-val.md",
            "REVIEW_FILE_SUGGESTED": f"{SDLC_DELIVERY_BASE}/80_reviews/{{slug}}-REV-70-val.md",
        }

    def build_context_extensions(self, *, state: dict[str, Any], step: str, step_cfg: dict[str, Any], ctx: dict[str, str], project_root: Path | None = None) -> dict[str, str]:
        result: dict[str, str] = {}
        runner_home = get_runner_home()
        if runner_home:
            result["GOVERNANCE_RUNTIME_ROOT"] = str(Path(runner_home) / "bundles" / "core" / "current" / "foundation")
            result["PLATFORM_RUNTIME_ROOT"] = str(Path(runner_home) / "bundles" / "core" / "current" / "platform")
        workspace_root = get_workspace_root()
        effective_root = Path(project_root or workspace_root or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))
        artifacts = state.get("artifacts") or {}
        slug = _extract_slug_from_path(artifacts.get("EXEC_FILE", ""))
        for key, rel_path in self.register_artifact_keys(job_id=job_id).items():
            resolved = rel_path.replace("{slug}", slug)
            if "{seq}" in resolved:
                path_dir, path_file = resolved.rsplit("/", 1)
                target_dir = effective_root / path_dir
                prefix = path_file.split("{seq}")[0]
                seq = resolve_next_seq(target_dir, prefix)
                resolved = resolved.replace("{seq}", seq)
            result[key] = str(effective_root / resolved)
        return result
