"""Context extensions for sdlc_10_requirement_v1 workflow.

This module provides the WorkflowExtensions interface for the requirement
generation workflow, including artifact path registration, prompt context
injection, and Layer 1/Layer 2 governance root resolution.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE, extract_slug_from_path, resolve_next_seq
from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc10RequirementExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_10_requirement_v1."""

    workflow_name = "sdlc_10_requirement_v1"

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
            # Initiative document (input from sdlc_00)
            "INIT_FILE": (
                f"{SDLC_DELIVERY_BASE}/00_initiatives/"
                f"INIT-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Requirements document (output)
            "REQ_FILE": (
                f"{SDLC_DELIVERY_BASE}/10_requirements/"
                f"REQ-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Critique document (evidence artifact)
            "CRITIQUE_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-CRITIQUE-10-req.md"
            ),
            # Review document (evidence artifact)
            "REVIEW_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-REV-10-req.md"
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
        """Build context extensions for sdlc_10_requirement_v1 workflow.

        Provides:
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Codebase documentation root (project-local)
        - Resolved artifact paths from register_artifact_keys()
        """
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        # Resolve artifact paths to absolute
        effective_root = Path(project_root or get_workspace_root() or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))

        # Extract slug from INIT_FILE filename for consistent naming
        artifacts = state.get("artifacts") or {}
        init_path = artifacts.get("INIT_FILE", "")
        slug = extract_slug_from_path(init_path)

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

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
