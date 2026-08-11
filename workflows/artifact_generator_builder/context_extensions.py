"""Context extensions for Artifact Generator Builder v3.

Registers artifact keys and resolves them to absolute paths at runtime.

AGB v3 pipeline: LLM generates domain logic (actions + prompts),
infrastructure assembled mechanically. Single deliverable: workflow package.

Uses the universal two-dict pattern:
    INPUT_ARTIFACTS  → {workspace_root}/input/{filename}
    OUTPUT_ARTIFACTS → {workspace_root}/output/{job_id}/{filename}
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
    resolve_input_artifacts,
    resolve_output_artifacts,
)


def _read_codename_from_requirement_doc(state: dict[str, Any]) -> str:
    """Extract codename from the requirement doc's YAML frontmatter."""
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
    in_frontmatter = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter and stripped.startswith("codename:"):
            value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            if value:
                return value
    return "unknown_generator"


class ArtifactGeneratorBuilderExtensions(WorkflowExtensions):
    """Artifact key registration and path resolution for AGB v3."""

    workflow_name = "artifact_generator_builder"

    # -- Input artifacts: resolved to {workspace_root}/input/ --
    INPUT_ARTIFACTS: dict[str, str] = {
        "REQUIREMENT_DOC": "",
        "EXISTING_WORKFLOW_DIR": "",
    }

    # -- Output artifacts: resolved to {workspace_root}/output/{job_id}/ --
    OUTPUT_ARTIFACTS: dict[str, str] = {
        # Step 1: Analyze
        "ANALYSIS_JSON_FILE": "ANALYSIS_JSON-{seq}.json",
        # Steps 2-3: Plan <-> Challenge
        "DOMAIN_PLAN_FILE": "DOMAIN_PLAN-{seq}.md",
        "PLAN_CHALLENGE_FILE": "PLAN_CHALLENGE-{seq}.md",
        # Steps 4-5: Implement <-> Critic
        "WORKFLOW_ACTIONS_FILE": "actions.py",
        "WORKFLOW_PROMPTS_DIR": "prompts/",
        "IMPL_CRITIQUE_FILE": "IMPL_CRITIQUE-{seq}.md",
        # Step 6: Assemble
        "WORKFLOW_MANIFEST_FILE": "workflow.toml",
        "WORKFLOW_EXTENSIONS_FILE": "context_extensions.py",
        "IMPL_OVERRIDE_FILES": "impls/",
        # Steps 7-9: Review -> Validate -> Gatekeep
        "PACKAGE_REVIEW_FILE": "PACKAGE_REVIEW-{seq}.md",
        "VALIDATION_FINDINGS_FILE": "VALIDATION_FINDINGS-{seq}.md",
        "GATEKEEP_PACKAGE_FILE": "GATEKEEP_PACKAGE-{seq}.md",
        # Step 10: Promote
        "WORKFLOW_PACKAGE_DIR": "",
    }

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a combined mapping of all artifact keys to path templates.

        Kept for backward compatibility. The actual resolution is done
        by resolve_input_artifacts() and resolve_output_artifacts().
        """
        combined: dict[str, str] = {}
        for key in self.INPUT_ARTIFACTS:
            combined[key] = "input/"
        for key, pattern in self.OUTPUT_ARTIFACTS.items():
            combined[key] = f"output/{{job_id}}/{pattern}"
        return combined

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

        # Governance and platform runtime roots (system references)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(
            get_governance_runtime_root()
        )
        result["PLATFORM_RUNTIME_ROOT"] = str(
            get_platform_runtime_root()
        )
        result["BASE_COMPOSITION_STANDARD"] = str(
            get_governance_runtime_root() / "BASE_COMPOSITION_STANDARD_v1.0.md"
        )

        # Resolve input artifacts → {workspace_root}/input/
        resolve_input_artifacts(
            result, state, workspace_root, self.INPUT_ARTIFACTS
        )

        # Resolve output artifacts → {workspace_root}/output/{job_id}/
        resolve_output_artifacts(
            result, state, workspace_root, self.OUTPUT_ARTIFACTS
        )

        return result

    def install_to_global(
        self, *, workspace_root: str | Path, runner_home: str | Path
    ) -> dict[str, Any]:
        return {"status": "NO_OP"}

    def sync_to_backend(
        self, *, workspace_root: str | Path
    ) -> dict[str, Any]:
        return {"status": "NO_OP"}
