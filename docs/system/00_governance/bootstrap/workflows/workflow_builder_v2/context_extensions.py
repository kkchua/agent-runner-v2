"""Context extensions for workflow_builder_v2 — Composition System Builder.

This module provides the WorkflowExtensions interface for the workflow_builder_v2
workflow, which builds composition system workflows following the Composition
System Standard.

The workflow generates:
- Component schemas (LEGO bricks)
- Composition formats (assembly instructions)
- Output formats (resolved deliverables)
- Operational workflows (scan → resolve → generate)
- Complete workflow packages

All runtime paths are resolved relative to the target repository root
(workspace_root) at job start time.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
    resolve_input_specs,
)


class WorkflowBuilderV2Extensions(WorkflowExtensions):
    """Workflow extension hooks for workflow_builder_v2.

    Provides:
    - Artifact key registration for all composition system artifacts
    - Prompt context injection for composition system paths
    - Layer 1/Layer 2 governance root resolution
    """

    workflow_name = "workflow_builder_v2"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        All paths are relative to the run root, using {job_id} and {seq}
        placeholders. The runner resolves these to absolute paths at runtime.
        """
        return {
            # Phase 1: Foundation
            "TEST_CRITERIA_FILE": "docs/repo/workflow_builder/runs/{job_id}/TEST_CRITERIA-{seq}.md",
            "REVIEW_TEST_CRITERIA_FILE": "docs/repo/workflow_builder/runs/{job_id}/REV_TEST_CRITERIA-{seq}.md",

            # Phase 2: Component Schema
            "COMPONENT_SCHEMA_FILE": "docs/repo/workflow_builder/runs/{job_id}/COMPONENT_SCHEMA-{seq}.md",
            "GATEKEEP_COMPONENT_SCHEMA_FILE": "docs/repo/workflow_builder/runs/{job_id}/GK_COMPONENT_SCHEMA-{seq}.md",

            # Phase 3: Composition Format
            "COMPOSITION_FORMAT_FILE": "docs/repo/workflow_builder/runs/{job_id}/COMPOSITION_FORMAT-{seq}.md",
            "GATEKEEP_COMPOSITION_FORMAT_FILE": "docs/repo/workflow_builder/runs/{job_id}/GK_COMPOSITION_FORMAT-{seq}.md",

            # Phase 4: Output Format
            "OUTPUT_FORMAT_FILE": "docs/repo/workflow_builder/runs/{job_id}/OUTPUT_FORMAT-{seq}.md",
            "GATEKEEP_OUTPUT_FORMAT_FILE": "docs/repo/workflow_builder/runs/{job_id}/GK_OUTPUT_FORMAT-{seq}.md",

            # Phase 5: Operational Workflow
            "OPERATIONAL_WORKFLOW_FILE": "docs/repo/workflow_builder/runs/{job_id}/OPERATIONAL_WORKFLOW-{seq}.md",
            "GATEKEEP_OPERATIONAL_WORKFLOW_FILE": "docs/repo/workflow_builder/runs/{job_id}/GK_OPERATIONAL_WORKFLOW-{seq}.md",

            # Phase 5b: Output Composition Spec (extensibility)
            "OUTPUT_COMPOSITION_SPEC_FILE": "docs/repo/workflow_builder/runs/{job_id}/OUTPUT_COMPOSITION_SPEC-{seq}.md",

            # Phase 6: Package
            "WORKFLOW_MANIFEST_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/workflow.toml",
            "WORKFLOW_EXTENSIONS_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/context_extensions.py",
            "WORKFLOW_ACTIONS_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/actions.py",
            "WORKFLOW_PROMPTS_INDEX_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/prompts_index.json",
            "WORKFLOW_README_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/README.md",
            "WORKFLOW_ENV_SAMPLE_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/.env.sample",
            "WORKFLOW_CONFIG_SAMPLE_FILE": "docs/repo/workflow_builder/runs/{job_id}/output/config.json.sample",
            "VALIDATION_REPORT_FILE": "docs/repo/workflow_builder/runs/{job_id}/VALIDATION-{seq}.md",
            "REVIEW_FILE_SUGGESTED": "docs/repo/workflow_builder/runs/{job_id}/REV_PACKAGE-{seq}.md",
            "GATEKEEP_PACKAGE_FILE": "docs/repo/workflow_builder/runs/{job_id}/GK_PACKAGE-{seq}.md",

            # Input artifacts (static dir — backend resolves user-uploaded files
            # before job_id exists, so no {job_id} placeholder allowed here)
            "WORKFLOW_SPEC_FILE": "docs/repo/workflow_builder/specs/{slug}.md"
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
        """Build context extensions for workflow_builder_v2.

        Provides:
        - Absolute paths for all composition system artifacts
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Composition System Standard reference path
        """
        result: dict[str, str] = {}

        # Resolve workspace root
        workspace_root = Path(
            project_root or get_workspace_root() or Path.cwd()
        )

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )

        # Composition System Standard reference
        result["COMPOSITION_SYSTEM_STANDARD"] = str(
            workspace_root / "docs" / "repo" / "workflow_builder" / "standards" / "COMPOSITION_SYSTEM_STANDARD.md"
        )

        # Meta-Workflow Builder Architecture reference
        result["META_WORKFLOW_BUILDER_ARCHITECTURE"] = str(
            workspace_root / "docs" / "repo" / "workflow_builder" / "standards" / "META_WORKFLOW_BUILDER_ARCHITECTURE.md"
        )

        # Resolve input spec filenames from operator console to Specs/ paths
        resolve_input_specs(
            result, state, self.workflow_name, ["WORKFLOW_SPEC_FILE"]
        )

        # Artifact paths from register_artifact_keys() — resolve to absolute
        artifacts = state.get("artifacts") or {}
        for key, rel_path in self.register_artifact_keys().items():
            # Already resolved by resolve_input_specs() — don't overwrite
            if key in result:
                continue
            # Input artifacts provided externally already have absolute
            # paths in state — preserve them.
            if key in artifacts and artifacts[key]:
                existing = artifacts[key]
                if Path(existing).is_absolute():
                    result[key] = existing
                    continue
            result[key] = str(workspace_root / rel_path)

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts.

        The workflow operates entirely within the target repository and
        does not install files to the global runner home.
        """
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via ukbe-run-agent sync-workflows CLI instead.

        Backend sync is handled by the CLI command, not by this hook.
        """
        return {"status": "NO_OP"}
