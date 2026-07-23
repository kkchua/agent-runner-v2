"""Context extensions for sdlc_00_init_doc_v1 workflow.

This module provides the WorkflowExtensions interface for the initiative
intake workflow, including artifact path registration, prompt context
injection, and Layer 1/Layer 2 governance root resolution.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE, resolve_next_seq
from agent_runner_v2.runtime_context import get_runner_home, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


def _extract_slug_from_path(file_path: str) -> str:
    """Extract the slug from an SDLC artifact filename.

    Pattern: {TYPE}-{date}-{seq}_{slug}.md -> returns {slug}
    Falls back to 'unknown' if pattern doesn't match.
    """
    if not file_path:
        return "unknown"
    filename = Path(file_path).stem  # Remove .md extension
    # Match patterns like DRAFT-INIT-20260722-001_console-sdlc10-support
    match = re.search(r"_(.+)$", filename)
    if match:
        return match.group(1)
    return "unknown"


class Sdlc00InitDocExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_00_init_doc_v1."""

    workflow_name = "sdlc_00_init_doc_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        Paths follow the SDLC delivery folder structure.
        """
        date_str = dt.datetime.now().strftime("%Y%m%d")

        return {
            # Draft initiative input (user-provided)
            "DRAFT_INIT_FILE": (
                f"{SDLC_DELIVERY_BASE}/00_draft_initiatives/"
                f"DRAFT-INIT-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Initiative document (approved output)
            "INIT_FILE": (
                f"{SDLC_DELIVERY_BASE}/00_initiatives/"
                f"INIT-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Critique document (evidence artifact)
            "CRITIQUE_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-CRITIQUE-00-init.md"
            ),
            # Review document (evidence artifact)
            "REVIEW_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-REV-00-init.md"
            ),
        }

    def build_context_extensions(
        self,
        *,
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        ctx: dict[str, str],
        project_root: Path | None = None,
    ) -> dict[str, str]:
        """Build context extensions for sdlc_00_init_doc_v1 workflow.

        Provides:
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Codebase documentation root (project-local)
        - Resolved artifact paths from register_artifact_keys()
        """
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        runner_home = get_runner_home()
        if runner_home:
            foundation_root = (
                Path(runner_home) / "bundles" / "core" / "current" / "foundation"
            )
            result["GOVERNANCE_RUNTIME_ROOT"] = str(foundation_root)

        # Layer 2 platform runtime root (global path)
        if runner_home:
            platform_root = (
                Path(runner_home) / "bundles" / "core" / "current" / "platform"
            )
            result["PLATFORM_RUNTIME_ROOT"] = str(platform_root)

        # Resolve artifact paths to absolute
        effective_root = Path(project_root or workspace_root or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))

        # Extract slug from draft initiative filename for consistent naming
        artifacts = state.get("artifacts") or {}
        draft_path = artifacts.get("DRAFT_INIT_FILE", "")
        slug = _extract_slug_from_path(draft_path)

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
