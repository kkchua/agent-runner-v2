"""Context extensions for codebase_to_meta_v1 workflow.

This module provides the WorkflowExtensions interface for the codebase-to-meta
content transformation workflow, including artifact path registration, prompt
context injection, audience directory installation, and Layer 1/Layer 2
governance root resolution.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import shutil
from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import resolve_next_seq
from agent_runner_v2.runtime_context import (
    JOBS_ROOT,
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
    resolve_repo_or_runtime_path,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


def _extract_slug_from_path(file_path: str) -> str:
    """Extract slug from an artifact filename.

    Looks for a pattern like TYPE-date-seq_slug.ext and returns the slug
    portion. Falls back to the filename stem, then to 'unknown'.
    """
    if not file_path:
        return "unknown"
    filename = Path(file_path).stem
    match = re.search(r"_(.+)$", filename)
    if match:
        return match.group(1)
    return "unknown"


class CodebaseToMetaExtensions(WorkflowExtensions):
    """Workflow extension hooks for codebase_to_meta_v1."""

    workflow_name = "codebase_to_meta_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        Paths follow the L2 platform staging pattern under docs/repo/meta_content/.
        """
        date_str = dt.datetime.now().strftime("%Y%m%d")
        run_root = f"docs/repo/meta_content/runs/{job_id}"
        current_root = "docs/repo/meta_content/current"
        history_root = f"docs/repo/meta_content/history/{job_id}"

        return {
            # External input
            "CODEBASE_MANIFEST": "docs/repo/codebase/current/codebase_manifest.json",
            # Staged artifacts (runs/<job_id>/)
            "AUDIENCE_INDEX": f"{run_root}/audience_index.json",
            # Per-audience meta content files with seq and slug placeholders
            "META_DEV_FILE": f"{run_root}/META-DEV-{date_str}-{{seq}}_{{slug}}.md",
            "META_ARCH_FILE": f"{run_root}/META-ARCH-{date_str}-{{seq}}_{{slug}}.md",
            "META_EXEC_FILE": f"{run_root}/META-EXEC-{date_str}-{{seq}}_{{slug}}.md",
            # Meta index
            "META_INDEX": f"{run_root}/meta_index.json",
            # Review and validation
            "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-review.md",
            "VALIDATION_FILE": f"{run_root}/{job_id}-validation.md",
            # Publish targets
            "META_MANIFEST": f"{current_root}/meta_manifest.json",
            "META_MANIFEST_HISTORY": f"{history_root}/meta_manifest.json",
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
        """Build context extensions for codebase_to_meta_v1 workflow.

        Provides:
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Audiences root (workflow package local)
        - Codebase documentation roots (project-local)
        - Meta content root (project-local)
        - Resolved artifact paths from register_artifact_keys()
        """
        del step_cfg, ctx
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        # Resolve workspace root
        workspace_root = Path(project_root or get_workspace_root() or Path.cwd()).resolve()

        job_id = str(state.get("job_id") or "META").strip()
        artifacts = state.get("artifacts", {})

        # Audiences root (within the workflow package)
        workflow_root = workspace_root / "workflows" / "codebase_to_meta_v1"
        result["AUDIENCES_ROOT"] = str(workflow_root / "audiences")

        # Codebase documentation roots (project-local)
        codebase_root = workspace_root / "docs" / "repo" / "codebase" / "current"
        result["CODEBASE_CURRENT_ROOT"] = str(codebase_root)

        # Meta content root
        meta_content_root = workspace_root / "docs" / "repo" / "meta_content"
        result["META_CONTENT_ROOT"] = str(meta_content_root)

        # Extract slug from source artifact (CODEBASE_MANIFEST or first available)
        slug = _extract_slug_from_path(artifacts.get("CODEBASE_MANIFEST", ""))
        if slug == "unknown":
            # Fall back to job_id suffix for traceability
            slug = job_id.lower().replace("-", "")

        # Resolve artifact paths to absolute
        output_paths = self.register_artifact_keys(job_id=job_id)
        for artifact_key, rel_path in output_paths.items():
            if not rel_path.endswith((".md", ".json", "/")):
                continue

            # Resolve slug placeholder
            resolved = rel_path.replace("{slug}", slug)

            # Resolve seq placeholder
            if "{seq}" in resolved:
                path_dir, path_file = resolved.rsplit("/", 1)
                target_dir = workspace_root / path_dir
                prefix = path_file.split("{seq}")[0]
                seq = resolve_next_seq(target_dir, prefix)
                resolved = resolved.replace("{seq}", seq)

            resolved_path = resolve_repo_or_runtime_path(
                resolved, project_root=workspace_root, runtime_root=JOBS_ROOT
            )
            resolved_str = str(resolved_path)
            result[artifact_key] = resolved_str
            pure = PurePath(resolved_str)
            result[f"{artifact_key}_METAJSON"] = str(
                pure.parent / f"{pure.stem}.meta.json"
            )

        return result

    def install_to_global(
        self, *, workspace_root: Path, runner_home: Path,
    ) -> dict[str, Any]:
        """Install audiences/ directory to global runner home.

        Copies the audiences/ directory from the workflow package to the
        global runner home so the scan_audiences action can discover
        audience definitions when running from the bootstrap copy.
        """
        src = Path(workspace_root) / "workflows" / "codebase_to_meta_v1" / "audiences"
        dst = Path(runner_home) / "workflows" / "default" / "codebase_to_meta_v1" / "audiences"

        if not src.exists():
            return {"status": "SKIPPED", "reason": "audiences/ directory not found"}

        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        files_copied = sum(1 for _ in dst.rglob("*") if _.is_file())
        return {
            "status": "INSTALLED",
            "source": str(src),
            "destination": str(dst),
            "files_copied": files_copied,
        }

    def sync_to_backend(self, *, workspace_root: Path) -> dict[str, Any]:
        """Sync via ukbe-run-agent sync-workflows CLI instead."""
        return {"status": "NO_OP"}
