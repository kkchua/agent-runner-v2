"""Context extensions for Artifact Generator Builder.

Registers artifact keys and resolves them to absolute paths at runtime.
The ArtifactGeneratorBuilderExtensions class provides the bridge between
artifact key definitions and the filesystem paths the runner uses.

This workflow builds artifact generators that follow the mandatory pattern:
Input -> Composition Spec -> Runtime Implementation -> Output

Every AGB run produces two deliverables:
1. Generator-specific Composition Standard (COMPOSITION_STANDARD_FILE)
2. Workflow Package (workflow.toml, context_extensions.py, actions.py, prompts/, README.md)

The codename is read from the requirement doc's YAML frontmatter and used
to name the deliverable files and determine the promote target directory.
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


def _read_codename_from_requirement_doc(state: dict[str, Any]) -> str:
    """Extract codename from the requirement doc's YAML frontmatter.

    Falls back to 'unknown_generator' if the requirement doc cannot be
    read or does not contain a codename field.
    """
    artifacts = state.get("artifacts") or {}
    req_doc_path = artifacts.get("REQUIREMENT_DOC", "")
    if not req_doc_path:
        return "unknown_generator"
    req_path = Path(req_doc_path)
    if not req_path.exists():
        return "unknown_generator"
    try:
        content = req_path.read_text(encoding="utf-8")
    except Exception:
        return "unknown_generator"
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("codename:"):
            value = line.split(":", 1)[1].strip().strip('"').strip("'")
            if value:
                return value
        if line == "---" and content.index(line) > 0:
            break
    return "unknown_generator"


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

        Deliverable files (COMPOSITION_STANDARD_FILE) use a
        ``{codename}`` placeholder resolved at runtime from the
        requirement doc's frontmatter.
        """
        repo = "docs/repo/artifact_generator_builder"
        run = f"{repo}/runs/{{job_id}}"
        out = f"{run}/output"

        return {
            # -- Input --
            "REQUIREMENT_DOC": "Specs/sample_requirement.md",

            # -- Phase 1: Requirement Study --
            "REQUIREMENT_ANALYSIS_FILE": f"{run}/REQUIREMENT_ANALYSIS-{{seq}}.md",

            # -- Phase 2: Design (adversarial challenge) --
            "COMPOSITION_SPEC_FILE": f"{out}/COMPOSITION_SPEC-{{seq}}.md",
            "CHALLENGE_COMPOSITION_SPEC_FILE": f"{run}/CHALLENGE_COMPOSITION_SPEC-{{seq}}.md",
            "RESPONSE_COMPOSITION_SPEC_FILE": f"{run}/RESPONSE_COMPOSITION_SPEC-{{seq}}.md",
            "GATEKEEP_COMPOSITION_SPEC_FILE": f"{run}/GATEKEEP_COMPOSITION_SPEC-{{seq}}.md",

            "RUNTIME_IMPL_FILE": f"{out}/RUNTIME_IMPL-{{seq}}.md",
            "CHALLENGE_RUNTIME_IMPL_FILE": f"{run}/CHALLENGE_RUNTIME_IMPL-{{seq}}.md",
            "RESPONSE_RUNTIME_IMPL_FILE": f"{run}/RESPONSE_RUNTIME_IMPL-{{seq}}.md",
            "GATEKEEP_RUNTIME_IMPL_FILE": f"{run}/GATEKEEP_RUNTIME_IMPL-{{seq}}.md",

            "ARTIFACT_CONTRACT_FILE": f"{run}/ARTIFACT_CONTRACT-{{seq}}.md",

            # -- Phase 3: Planning --
            "IMPLEMENTATION_PLAN_FILE": f"{run}/IMPLEMENTATION_PLAN-{{seq}}.md",

            # -- Phase 4: Implementation --
            "COMPOSITION_STANDARD_FILE": f"{out}/standards/COMPOSITION_STANDARD.md",
            "WORKFLOW_MANIFEST_FILE": f"{out}/workflow.toml",
            "WORKFLOW_EXTENSIONS_FILE": f"{out}/context_extensions.py",
            "WORKFLOW_ACTIONS_FILE": f"{out}/actions.py",
            "WORKFLOW_PROMPTS_DIR": f"{out}/prompts/",
            "WORKFLOW_README_FILE": f"{out}/README.md",
            "VALIDATION_FINDINGS_FILE": f"{run}/VALIDATION_FINDINGS-{{seq}}.md",

            # -- Phase 5: Testing --
            "TEST_CRITERIA_FILE": f"{run}/TEST_CRITERIA-{{seq}}.md",
            "TEST_FILE": f"{out}/test_actions.py",
            "TEST_RESULTS_FILE": f"{run}/TEST_RESULTS-{{seq}}.md",

            # -- Phase 6: Promote --
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

        # Read codename from requirement doc frontmatter
        codename = _read_codename_from_requirement_doc(state)
        result["CODENAME"] = codename

        # Governance and platform runtime roots
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )

        # Base composition standard path (from governance)
        result["BASE_COMPOSITION_STANDARD"] = str(
            get_governance_runtime_root() / "BASE_COMPOSITION_STANDARD_v1.0.md"
        )

        # Resolve input spec filenames from operator console to Specs/ paths
        resolve_input_specs(
            result, state, self.workflow_name, ["REQUIREMENT_DOC"]
        )

        # Resolve all artifact keys to absolute paths
        artifacts = state.get("artifacts") or {}
        for key, rel_path in self.register_artifact_keys().items():
            # Already resolved by resolve_input_specs() -- don't overwrite
            if key in result:
                continue
            existing = artifacts.get(key)
            if existing and Path(existing).is_absolute():
                result[key] = existing
                continue
            # Resolve {codename} placeholder in path templates
            resolved_path = rel_path.replace("{codename}", codename)
            result[key] = str(workspace_root / resolved_path)

        return result

    def install_to_global(
        self, *, workspace_root: str | Path, runner_home: str | Path
    ) -> dict[str, Any]:
        return {"status": "NO_OP"}

    def sync_to_backend(
        self, *, workspace_root: str | Path
    ) -> dict[str, Any]:
        return {"status": "NO_OP"}
