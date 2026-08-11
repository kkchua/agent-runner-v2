"""Context extensions for Artifact Generator Builder v3.

Registers artifact keys and resolves them to absolute paths at runtime.

AGB v3 pipeline: LLM generates domain logic (actions + prompts),
infrastructure assembled mechanically. Single deliverable: workflow package.
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
    resolve_input_specs,
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

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates."""
        repo = "docs/repo/artifact_generator_builder"
        run = f"{repo}/runs/{{job_id}}"
        out = f"{run}/output"

        return {
            # -- Input --
            "REQUIREMENT_DOC": "Specs/sample_requirement.md",

            # -- Step 1: Analyze --
            "ANALYSIS_JSON_FILE": f"{out}/ANALYSIS_JSON-{{seq}}.json",

            # -- Steps 2-3: Plan ↔ Challenge --
            "DOMAIN_PLAN_FILE": f"{out}/DOMAIN_PLAN-{{seq}}.md",
            "PLAN_CHALLENGE_FILE": f"{run}/PLAN_CHALLENGE-{{seq}}.md",

            # -- Steps 4-5: Implement ↔ Critic --
            "WORKFLOW_ACTIONS_FILE": f"{out}/actions.py",
            "WORKFLOW_PROMPTS_DIR": f"{out}/prompts/",
            "IMPL_CRITIQUE_FILE": f"{run}/IMPL_CRITIQUE-{{seq}}.md",

            # -- Step 6: Assemble --
            "WORKFLOW_MANIFEST_FILE": f"{out}/workflow.toml",
            "WORKFLOW_EXTENSIONS_FILE": f"{out}/context_extensions.py",
            "IMPL_OVERRIDE_FILES": f"{out}/impls/",

            # -- Steps 7-9: Review → Validate → Gatekeep --
            "PACKAGE_REVIEW_FILE": f"{run}/PACKAGE_REVIEW-{{seq}}.md",
            "VALIDATION_FINDINGS_FILE": f"{run}/VALIDATION_FINDINGS-{{seq}}.md",
            "GATEKEEP_PACKAGE_FILE": f"{run}/GATEKEEP_PACKAGE-{{seq}}.md",

            # -- Step 10: Promote --
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
        job_id = str(state.get("job_id") or "")
        for key, rel_path in self.register_artifact_keys().items():
            if key in result:
                continue
            existing = artifacts.get(key)
            if existing and Path(existing).is_absolute():
                result[key] = existing
                continue
            resolved_path = rel_path.replace("{codename}", codename)
            if job_id:
                resolved_path = resolved_path.replace("{job_id}", job_id)
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
