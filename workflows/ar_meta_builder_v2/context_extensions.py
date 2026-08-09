"""Context extensions for AR Meta Builder v2.

Registers artifact keys and resolves them to absolute paths at runtime.
The ArMetaBuilderV2Extensions class provides the bridge between artifact
key definitions and the filesystem paths the runner uses.

This workflow is a composition system meta-builder that transforms a
runtime specification into a complete, executable workflow package
through a 9-phase TDD-driven pipeline with identity locking and base
schema fine-tuning.
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


class ArMetaBuilderV2Extensions(WorkflowExtensions):
    """Artifact key registration and path resolution for AR Meta Builder v2."""

    workflow_name = "ar_meta_builder_v2"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time.  All paths are relative
        to the workspace root.
        """
        repo = "docs/repo/ar_meta_builder_v2"
        run = f"{repo}/runs/{{job_id}}"
        out = f"{run}/output"
        specs = f"{repo}/specs"
        standards = f"{repo}/standards"
        impls = f"{repo}/impls"

        return {
            # -- Inputs --
            "BOOTSTRAP_SPEC_FILE": (
                "Specs/detault.spec.md"
            ),

            # -- Promoted deliverables --
            "MASTER_SPEC_FILE": f"{specs}/{{workflow_name}}_{{codename}}.md",
            "DEFAULT_IMPL_FILE": f"{impls}/default.impl.md",

            # -- Phase 0: Input Validation --
            "VALIDATION_INPUT_SPEC_FILE": (
                f"{run}/VALIDATION_INPUT_SPEC-{{seq}}.md"
            ),

            # -- Phase 1: Domain Analysis --
            "TEST_CRITERIA_FILE": f"{run}/TEST_CRITERIA-{{seq}}.md",
            "REVIEW_TEST_CRITERIA_FILE": (
                f"{run}/REVIEW_TEST_CRITERIA-{{seq}}.md"
            ),
            "DOMAIN_ANALYSIS_FILE": (
                f"{run}/DOMAIN_ANALYSIS-{{seq}}.md"
            ),
            "VALIDATE_DOMAIN_ANALYSIS_FILE": (
                f"{run}/VALIDATE_DOMAIN_ANALYSIS-{{seq}}.md"
            ),
            "GATEKEEP_DOMAIN_ANALYSIS_FILE": (
                f"{run}/GATEKEEP_DOMAIN_ANALYSIS-{{seq}}.md"
            ),

            # -- Phase 2: Component Schema --
            "DOMAIN_COMPONENT_SCHEMA_FILE": (
                f"{run}/DOMAIN_COMPONENT_SCHEMA-{{seq}}.md"
            ),
            "REVIEW_COMPONENT_SCHEMA_FILE": (
                f"{run}/REVIEW_COMPONENT_SCHEMA-{{seq}}.md"
            ),
            "VALIDATE_COMPONENT_SCHEMA_FILE": (
                f"{run}/VALIDATE_COMPONENT_SCHEMA-{{seq}}.md"
            ),
            "GATEKEEP_COMPONENT_SCHEMA_FILE": (
                f"{run}/GATEKEEP_COMPONENT_SCHEMA-{{seq}}.md"
            ),

            # -- Phase 3: Composition Format --
            "COMPOSITION_FORMAT_FILE": (
                f"{run}/COMPOSITION_FORMAT-{{seq}}.md"
            ),
            "REVIEW_COMPOSITION_FORMAT_FILE": (
                f"{run}/REVIEW_COMPOSITION_FORMAT-{{seq}}.md"
            ),
            "VALIDATE_COMPOSITION_FORMAT_FILE": (
                f"{run}/VALIDATE_COMPOSITION_FORMAT-{{seq}}.md"
            ),
            "GATEKEEP_COMPOSITION_FORMAT_FILE": (
                f"{run}/GATEKEEP_COMPOSITION_FORMAT-{{seq}}.md"
            ),

            # -- Phase 4: Output Format --
            "OUTPUT_FORMAT_FILE": f"{run}/OUTPUT_FORMAT-{{seq}}.md",
            "REVIEW_OUTPUT_FORMAT_FILE": (
                f"{run}/REVIEW_OUTPUT_FORMAT-{{seq}}.md"
            ),
            "VALIDATE_OUTPUT_FORMAT_FILE": (
                f"{run}/VALIDATE_OUTPUT_FORMAT-{{seq}}.md"
            ),
            "GATEKEEP_OUTPUT_FORMAT_FILE": (
                f"{run}/GATEKEEP_OUTPUT_FORMAT-{{seq}}.md"
            ),

            # -- Phase 5: Artifact Contract --
            "ARTIFACT_CONTRACT_FILE": (
                f"{run}/ARTIFACT_CONTRACT-{{seq}}.md"
            ),
            "REVIEW_ARTIFACT_CONTRACT_FILE": (
                f"{run}/REVIEW_ARTIFACT_CONTRACT-{{seq}}.md"
            ),
            "VALIDATE_ARTIFACT_CONTRACT_FILE": (
                f"{run}/VALIDATE_ARTIFACT_CONTRACT-{{seq}}.md"
            ),
            "GATEKEEP_ARTIFACT_CONTRACT_FILE": (
                f"{run}/GATEKEEP_ARTIFACT_CONTRACT-{{seq}}.md"
            ),

            # -- Phase 6: Step Sequence --
            "STEP_SEQUENCE_FILE": f"{run}/STEP_SEQUENCE-{{seq}}.md",
            "REVIEW_STEP_SEQUENCE_FILE": (
                f"{run}/REVIEW_STEP_SEQUENCE-{{seq}}.md"
            ),
            "VALIDATE_STEP_SEQUENCE_FILE": (
                f"{run}/VALIDATE_STEP_SEQUENCE-{{seq}}.md"
            ),
            "GATEKEEP_STEP_SEQUENCE_FILE": (
                f"{run}/GATEKEEP_STEP_SEQUENCE-{{seq}}.md"
            ),

            # -- Phase 7: Runtime Standard --
            "RUNTIME_STANDARD_FILE": (
                f"{run}/RUNTIME_STANDARD-{{seq}}.md"
            ),
            "REVIEW_RUNTIME_STANDARD_FILE": (
                f"{run}/REVIEW_RUNTIME_STANDARD-{{seq}}.md"
            ),
            "VALIDATE_RUNTIME_STANDARD_FILE": (
                f"{run}/VALIDATE_RUNTIME_STANDARD-{{seq}}.md"
            ),
            "GATEKEEP_RUNTIME_STANDARD_FILE": (
                f"{run}/GATEKEEP_RUNTIME_STANDARD-{{seq}}.md"
            ),

            # -- Phase 8: Operational Workflow --
            "OPERATIONAL_WORKFLOW_FILE": (
                f"{run}/OPERATIONAL_WORKFLOW-{{seq}}.md"
            ),
            "REVIEW_OPERATIONAL_WORKFLOW_FILE": (
                f"{run}/REVIEW_OPERATIONAL_WORKFLOW-{{seq}}.md"
            ),
            "VALIDATE_OPERATIONAL_WORKFLOW_FILE": (
                f"{run}/VALIDATE_OPERATIONAL_WORKFLOW-{{seq}}.md"
            ),
            "GATEKEEP_OPERATIONAL_WORKFLOW_FILE": (
                f"{run}/GATEKEEP_OPERATIONAL_WORKFLOW-{{seq}}.md"
            ),

            # -- Phase 9: Package Assembly --
            "WORKFLOW_MANIFEST_FILE": f"{out}/workflow.toml",
            "WORKFLOW_EXTENSIONS_FILE": f"{out}/context_extensions.py",
            "WORKFLOW_ACTIONS_FILE": f"{out}/actions.py",
            "WORKFLOW_PROMPTS_INDEX_FILE": f"{out}/prompts_index.json",
            "WORKFLOW_README_FILE": f"{out}/README.md",
            "STANDARDS_COMPOSITION_STANDARD_FILE": (
                f"{standards}/COMPOSITION_STANDARD.md"
            ),
            "VALIDATION_REPORT_FILE": (
                f"{run}/VALIDATION_REPORT-{{seq}}.md"
            ),
            "REVIEW_FILE_SUGGESTED": f"{run}/REVIEW-{{seq}}.md",

            # -- Phase 9: Promotion --
            "WORKFLOW_PACKAGE_DIR_FILE": (
                f"{run}/WORKFLOW_PACKAGE_DIR-{{seq}}.md"
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

        # Base composition standard path
        result["BASE_COMPOSITION_STANDARD"] = str(
            workspace_root
            / "docs"
            / "repo"
            / "composition_standard"
            / "COMPOSITION_SYSTEM_STANDARD.md"
        )

        # Resolve input spec filenames from operator console to Specs/ paths
        resolve_input_specs(
            result, state, self.workflow_name, ["BOOTSTRAP_SPEC_FILE"]
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
