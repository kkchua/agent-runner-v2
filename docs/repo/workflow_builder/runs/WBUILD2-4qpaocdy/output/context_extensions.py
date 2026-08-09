"""Context extensions for Workflow Builder v3.

Registers artifact keys and resolves them to absolute paths at runtime.
The WorkflowExtensions class provides the bridge between artifact key
definitions and the filesystem paths the runner uses.

Refinement Summary (Iter 1):
- Added STANDARDS_COMPOSITION_STANDARD_FILE to register_artifact_keys()
  with path template: output/Standards/COMPOSITION_STANDARD.md.

Refinement Summary (Iter 2):
- Verified all 24 artifact keys registered and consistent with
  workflow.toml. No changes required.
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class WorkflowBuilderV3Extensions(WorkflowExtensions):
    """Artifact key registration and path resolution for Workflow Builder v3.

    This workflow is a meta-meta builder that generates composition system
    workflows (meta builders). Each generated meta builder is itself a
    composition system with its own composition standard.
    """

    workflow_name = "workflow_builder_v3"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time.  All paths are relative
        to the workspace root.

        Returns:
            Dict mapping each artifact key to its filename pattern or
            relative path template.
        """
        return {
            # Input artifact
            "WORKFLOW_SPEC_FILE": (
                "docs/repo/workflow_builder/specs/{slug}.md"
            ),
            # Phase 1: Foundation (TDD Loop)
            "TEST_CRITERIA_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "TEST_CRITERIA-{seq}.md"
            ),
            "REVIEW_TEST_CRITERIA_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "REVIEW_TEST_CRITERIA-{seq}.md"
            ),
            # Phase 2: Component Schema (Layer 1)
            "COMPONENT_SCHEMA_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "COMPONENT_SCHEMA-{seq}.md"
            ),
            "GATEKEEP_COMPONENT_SCHEMA_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "GATEKEEP_COMPONENT_SCHEMA-{seq}.md"
            ),
            # Phase 3: Composition Format (Layer 2)
            "COMPOSITION_FORMAT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "COMPOSITION_FORMAT-{seq}.md"
            ),
            "GATEKEEP_COMPOSITION_FORMAT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "GATEKEEP_COMPOSITION_FORMAT-{seq}.md"
            ),
            # Phase 4: Output Format (Layer 3)
            "OUTPUT_FORMAT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "OUTPUT_FORMAT-{seq}.md"
            ),
            "GATEKEEP_OUTPUT_FORMAT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "GATEKEEP_OUTPUT_FORMAT-{seq}.md"
            ),
            # Phase 5: Operational Workflow
            "OPERATIONAL_WORKFLOW_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "OPERATIONAL_WORKFLOW-{seq}.md"
            ),
            "GATEKEEP_OPERATIONAL_WORKFLOW_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md"
            ),
            # Phase 6: Composition Standard (v3 Innovation)
            "COMPOSITION_STANDARD_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "COMPOSITION_STANDARD-{seq}.md"
            ),
            "GATEKEEP_COMPOSITION_STANDARD_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "GATEKEEP_COMPOSITION_STANDARD-{seq}.md"
            ),
            # Phase 7: Meta Composition Spec (v3 Innovation)
            "META_COMPOSITION_SPEC_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "META_COMPOSITION_SPEC-{seq}.md"
            ),
            # Phase 8: Package Assembly -- output files
            "WORKFLOW_MANIFEST_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "output/workflow.toml"
            ),
            "WORKFLOW_EXTENSIONS_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "output/context_extensions.py"
            ),
            "WORKFLOW_ACTIONS_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "output/actions.py"
            ),
            "WORKFLOW_PROMPTS_INDEX_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "output/prompts_index.json"
            ),
            "WORKFLOW_README_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "output/README.md"
            ),
            "STANDARDS_COMPOSITION_STANDARD_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "output/Standards/COMPOSITION_STANDARD.md"
            ),
            "VALIDATION_REPORT_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "VALIDATION_REPORT-{seq}.md"
            ),
            "GATEKEEP_PACKAGE_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "GATEKEEP_PACKAGE-{seq}.md"
            ),
            "REVIEW_FILE_SUGGESTED": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "REVIEW-{seq}.md"
            ),
            # Phase 9: Promotion
            "WORKFLOW_PACKAGE_DIR_FILE": (
                "docs/repo/workflow_builder/runs/{job_id}/"
                "WORKFLOW_PACKAGE_DIR-{seq}.md"
            ),
        }

    def build_context_extensions(
        self,
        *,
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        ctx: dict[str, str],
        project_root: str | Path | None = None,
    ) -> dict[str, str]:
        """Resolve all artifact keys to absolute filesystem paths.

        Called before each step's prompt template is rendered.  Converts
        the relative path templates from ``register_artifact_keys()``
        into absolute paths anchored at the workspace root.

        Returns:
            Dict mapping each artifact key (and governance root keys) to
            absolute path strings.
        """
        result: dict[str, str] = {}
        workspace_root = Path(
            project_root or get_workspace_root() or Path.cwd()
        )

        # Governance and platform runtime roots
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )
        result["COMPOSITION_SYSTEM_STANDARD"] = str(
            workspace_root
            / "docs"
            / "repo"
            / "composition_standard"
            / "COMPOSITION_SYSTEM_STANDARD.md"
        )

        # Resolve all artifact keys to absolute paths
        for key, rel_path in self.register_artifact_keys().items():
            result[key] = str(workspace_root / rel_path)

        return result

    def install_to_global(
        self, *, workspace_root: str | Path, runner_home: str | Path
    ) -> dict[str, Any]:
        """Install workflow extensions to the global runner home.

        Returns:
            Dict with ``status`` key indicating the outcome.
        """
        return {"status": "NO_OP"}

    def sync_to_backend(
        self, *, workspace_root: str | Path
    ) -> dict[str, Any]:
        """Sync workflow definition to the backend.

        Returns:
            Dict with ``status`` key indicating the outcome.
        """
        return {"status": "NO_OP"}
