"""Context extensions for product_master_gen_v1 workflow.

This module provides the WorkflowExtensions interface for the Product Master
Generator workflow, including artifact path registration, prompt context
injection, and Layer 1/Layer 2 governance root resolution.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import extract_slug_from_path, resolve_next_seq
from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class ProductMasterGenV1Extensions(WorkflowExtensions):
    """Workflow extension hooks for product_master_gen_v1.

    Registers artifact key mappings for the Product Master Generator
    workflow and resolves them to absolute paths at runtime. Injects
    GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT, and PRODUCT_SOURCE_DIR
    into the prompt context.
    """

    workflow_name = "product_master_gen_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        All paths are relative to the workspace root and reside under
        docs/repo/product/runs/{job_id}/. Placeholders {slug}, {date},
        {seq}, and {iter} are resolved at runtime in
        build_context_extensions().
        """
        date_str = dt.datetime.now().strftime("%Y%m%d")
        run_root = f"docs/repo/product/runs/{job_id}"

        return {
            # Scan report produced by scan_product_inputs action
            "SCAN_REPORT_FILE": (
                f"{run_root}/SCAN-REPORT-{date_str}_{{slug}}.md"
            ),
            # Section artifacts produced by prompt-driven generation steps
            "PRODUCT_INFO_FILE": (
                f"{run_root}/PRODUCT-INFO_{{slug}}.md"
            ),
            "TARGET_AUDIENCE_FILE": (
                f"{run_root}/TARGET-AUDIENCE_{{slug}}.md"
            ),
            "PRODUCT_BENEFITS_FILE": (
                f"{run_root}/PRODUCT-BENEFITS_{{slug}}.md"
            ),
            "MARKETING_ASSETS_FILE": (
                f"{run_root}/MARKETING-ASSETS_{{slug}}.md"
            ),
            "ADDITIONAL_SECTIONS_FILE": (
                f"{run_root}/ADDITIONAL-SECTIONS_{{slug}}.md"
            ),
            # Assembled Product Master (auto-incrementing sequence)
            "PRODUCT_MASTER_FILE": (
                f"{run_root}/PRODUCT-MASTER-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Review critique document (iteration-tracked)
            "REVIEW_FILE_SUGGESTED": (
                f"{run_root}/{{job_id}}-REV-{{iter}}_product-master-review.md"
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
        """Build context extensions for product_master_gen_v1 workflow.

        Provides:
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - PRODUCT_SOURCE_DIR from user input (absolute path)
        - SLUG extracted from PRODUCT_SOURCE_DIR directory name
        - Resolved artifact paths from register_artifact_keys()
        """
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        # Resolve workspace root with fallback
        effective_root = Path(project_root or get_workspace_root() or Path.cwd())

        # Extract PRODUCT_SOURCE_DIR from state (user-provided context variable)
        artifacts = state.get("artifacts") or {}
        source_dir = artifacts.get("PRODUCT_SOURCE_DIR", "")
        if source_dir:
            result["PRODUCT_SOURCE_DIR"] = str(Path(source_dir))
        else:
            # Fallback: try from context or state top-level
            source_dir = state.get("PRODUCT_SOURCE_DIR", "") or ctx.get(
                "PRODUCT_SOURCE_DIR", ""
            )
            if source_dir:
                result["PRODUCT_SOURCE_DIR"] = str(Path(source_dir))

        # Extract slug from PRODUCT_SOURCE_DIR directory name
        slug = extract_slug_from_path(source_dir) if source_dir else "unknown"
        result["SLUG"] = slug

        # Determine review iteration from state
        review_iter = state.get("review_iteration", 0)
        iter_str = f"{int(review_iter):02d}"

        # Resolve artifact paths to absolute
        job_id = str(state.get("job_id", "unknown"))

        for key, rel_path in self.register_artifact_keys(job_id=job_id).items():
            resolved = rel_path.replace("{slug}", slug)
            resolved = resolved.replace("{job_id}", job_id)
            resolved = resolved.replace("{iter}", iter_str)

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
        """Sync via ukbe-run-agent sync-workflows CLI instead."""
        return {"status": "NO_OP"}
