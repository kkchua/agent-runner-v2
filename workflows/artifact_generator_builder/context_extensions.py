"""Context extensions for Artifact Generator Builder.

Registers artifact keys and resolves them to absolute paths at runtime.
The ArtifactGeneratorBuilderExtensions class provides the bridge between
artifact key definitions and the filesystem paths the runner uses.

This workflow builds artifact generators that follow the mandatory pattern:
Input → Composition Spec → Runtime Implementation → Output
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root
)
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
    resolve_input_specs,
)


class ArtifactGeneratorBuilderExtensions(WorkflowExtensions):
    """Artifact key registration and path resolution for Artifact Generator Builder."""

    workflow_name = "artifact_generator_builder"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time. All paths are relative
        to the workspace root.
        """
        repo = "docs/repo/artifact_generator_builder"
        run = f"{repo}/runs/{{job_id}}"
        out = f"{run}/output"

        return {
            # -- Input --
            "REQUIREMENT_DOC": "Specs/sample_requirement.md",

            # -- Phase 1: Analyze Requirement --
            "REQUIREMENT_ANALYSIS_FILE": f"{run}/REQUIREMENT_ANALYSIS-{{seq}}.md",
            "REVIEW_REQUIREMENT_FILE": f"{run}/REVIEW_REQUIREMENT-{{seq}}.md",
            "GATEKEEP_REQUIREMENT_FILE": f"{run}/GATEKEEP_REQUIREMENT-{{seq}}.md",

            # -- Phase 2: Design Composition Spec --
            "COMPOSITION_SPEC_FILE": f"{run}/COMPOSITION_SPEC-{{seq}}.md",
            "REVIEW_COMPOSITION_SPEC_FILE": f"{run}/REVIEW_COMPOSITION_SPEC-{{seq}}.md",
            "GATEKEEP_COMPOSITION_SPEC_FILE": f"{run}/GATEKEEP_COMPOSITION_SPEC-{{seq}}.md",

            # -- Phase 3: Design Runtime Implementation --
            "RUNTIME_IMPL_FILE": f"{run}/RUNTIME_IMPL-{{seq}}.md",
            "REVIEW_RUNTIME_IMPL_FILE": f"{run}/REVIEW_RUNTIME_IMPL-{{seq}}.md",
            "GATEKEEP_RUNTIME_IMPL_FILE": f"{run}/GATEKEEP_RUNTIME_IMPL-{{seq}}.md",

            # -- Phase 4: Define Artifacts --
            "ARTIFACT_CONTRACT_FILE": f"{run}/ARTIFACT_CONTRACT-{{seq}}.md",
            "GATEKEEP_ARTIFACTS_FILE": f"{run}/GATEKEEP_ARTIFACTS-{{seq}}.md",

            # -- Phase 5: Design Steps --
            "STEP_SEQUENCE_FILE": f"{run}/STEP_SEQUENCE-{{seq}}.md",
            "GATEKEEP_STEPS_FILE": f"{run}/GATEKEEP_STEPS-{{seq}}.md",

            # -- Phase 6: Generate Package --
            "WORKFLOW_MANIFEST_FILE": f"{out}/workflow.toml",
            "WORKFLOW_EXTENSIONS_FILE": f"{out}/context_extensions.py",
            "WORKFLOW_ACTIONS_FILE": f"{out}/actions.py",
            "WORKFLOW_PROMPTS_DIR": f"{out}/prompts/",
            "WORKFLOW_README_FILE": f"{out}/README.md",
            "REVIEW_PACKAGE_FILE": f"{run}/REVIEW_PACKAGE-{{seq}}.md",
            "GATEKEEP_PACKAGE_FILE": f"{run}/GATEKEEP_PACKAGE-{{seq}}.md",

            # -- Phase 7: Promote Package --
            "PROMOTION_REPORT_FILE": f"{run}/PROMOTION_REPORT-{{seq}}.md",
            "WORKFLOW_PACKAGE_DIR": f"{out}/",
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
        """Resolve all artifact keys to absolute filesystem paths."""
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

        # Base composition standard path (from governance)
        result["BASE_COMPOSITION_STANDARD"] = str(
            get_governance_runtime_root() / "COMPOSITION_SYSTEM_STANDARD.md"
        )

        # Resolve input spec filenames from operator console to Specs/ paths
        resolve_input_specs(
            result, state, self.workflow_name, ["REQUIREMENT_DOC"]
        )

        # Resolve all artifact keys to absolute paths
        artifacts = state.get("artifacts") or {}
        for key, rel_path in self.register_artifact_keys().items():
            # Already resolved by resolve_input_specs() — don't overwrite
            if key in result:
                continue
            existing = artifacts.get(key)
            if existing and Path(existing).is_absolute():
                result[key] = existing
                continue
            result[key] = str(workspace_root / rel_path)

        return result

    def install_to_global(
        self, *, workspace_root: str | Path, runner_home: str | Path
    ) -> dict[str, Any]:
        return {"status": "NO_OP"}

    def sync_to_backend(
        self, *, workspace_root: str | Path
    ) -> dict[str, Any]:
        return {"status": "NO_OP"}
