"""Context extensions for workflow_builder_v1."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import extract_slug_from_path, resolve_next_seq
from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class WorkflowBuilderExtensions(WorkflowExtensions):
    """Workflow extension hooks for workflow_builder_v1."""

    workflow_name = "workflow_builder_v1"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings."""
        date_str = dt.datetime.now().strftime("%Y%m%d")
        run_root = f"docs/repo/workflow_builder/runs/{job_id}"
        return {
            "WORKFLOW_SPEC": "docs/repo/workflow_builder/specs/{slug}.md",
            "TEST_CRITERIA": f"{run_root}/TEST_CRITERIA-{date_str}-{{seq}}_{{slug}}.md",
            "WORKFLOW_REQUIREMENTS": f"{run_root}/REQUIREMENTS-{date_str}-{{seq}}_{{slug}}.md",
            "ARTIFACT_CONTRACT": f"{run_root}/ARTIFACTS-{date_str}-{{seq}}_{{slug}}.md",
            "STEP_ARCHITECTURE": f"{run_root}/STEPS-{date_str}-{{seq}}_{{slug}}.md",
            "WORKFLOW_MANIFEST": f"{run_root}/workflow.toml",
            "WORKFLOW_EXTENSIONS": f"{run_root}/context_extensions.py",
            "WORKFLOW_PROMPTS_INDEX": f"{run_root}/PROMPTS-{date_str}-{{seq}}_{{slug}}.md",
            "WORKFLOW_README": f"{run_root}/README.md",
            "WORKFLOW_ENV_SAMPLE": f"{run_root}/.env.sample",
            "WORKFLOW_CONFIG_SAMPLE": f"{run_root}/config.json.sample",
            "VALIDATION_REPORT": f"{run_root}/VALIDATION-{date_str}-{{seq}}_{{slug}}.md",
            "REVIEW_FILE_SUGGESTED": f"{run_root}/REVIEW-{date_str}-{{seq}}_{{slug}}.md",
        }

    def build_context_extensions(
        self, *, state, step, step_cfg, ctx, project_root=None,
    ) -> dict[str, str]:
        """Inject absolute paths and metadata into prompt context."""
        result: dict[str, str] = {}
        workspace_root = Path(project_root or get_workspace_root() or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))

        # Governance roots
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        # Workflow creation guide path
        result["WORKFLOW_CREATION_GUIDE"] = str(
            workspace_root / "workflows" / "WORKFLOW_CREATION_GUIDE.md"
        )
        result["WORKFLOW_BUILDER_SOP"] = str(
            workspace_root / "docs" / "repo" / "workflow_builder" / "current" / "sop" / "WORKFLOW_BUILDER_SOP.md"
        )

        # Role policies reference
        result["ROLE_POLICIES"] = str(
            workspace_root / "workflows" / "_registry" / "role_policies.json"
        )

        # Example workflow references
        result["EXAMPLE_WORKFLOW_TOML"] = str(
            workspace_root / "workflows" / "sdlc_10_requirement_v1" / "workflow.toml"
        )
        result["EXAMPLE_CONTEXT_EXTENSIONS"] = str(
            workspace_root / "workflows" / "sdlc_10_requirement_v1" / "context_extensions.py"
        )

        # Resolve artifact paths to absolute
        artifacts = state.get("artifacts") or {}
        spec_path = artifacts.get("WORKFLOW_SPEC", "")
        slug = extract_slug_from_path(spec_path)

        for key, rel_path in self.register_artifact_keys(job_id=job_id).items():
            # Input artifacts provided externally (e.g. by operator console)
            # already have absolute paths in state — preserve them.
            if key in artifacts and artifacts[key]:
                existing = artifacts[key]
                if Path(existing).is_absolute():
                    result[key] = existing
                    continue
            resolved = rel_path.replace("{slug}", slug)
            if "{seq}" in resolved:
                path_dir, path_file = resolved.rsplit("/", 1)
                target_dir = workspace_root / path_dir
                prefix = path_file.split("{seq}")[0]
                seq = resolve_next_seq(target_dir, prefix)
                resolved = resolved.replace("{seq}", seq)
            result[key] = str(workspace_root / resolved)

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
