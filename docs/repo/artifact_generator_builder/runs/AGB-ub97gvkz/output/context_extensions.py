"""Context extensions for Codebase Intelligence Generator.

Registers artifact keys and resolves them to absolute paths at runtime.
The CodebaseIntelligenceExtensions class provides the bridge between
artifact key definitions and the filesystem paths the runner uses.

This workflow scans a codebase (documentation + Python source), performs
structural health analysis across 5 dimensions, security audit across
5 phases, and produces audience-tailored intelligence reports.

Pattern: Input Transformation (Pattern 2, per BASE_COMPOSITION_STANDARD)
Layers: 3 (Input Parsing -> Analysis -> Output Rendering)
Stages: 7 (TS-001 through TS-007)
Invariants: 24 (INV-001 through INV-024)
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


class CodebaseIntelligenceExtensions(WorkflowExtensions):
    """Artifact key registration and path resolution for codebase_intelligence."""

    workflow_name = "codebase_intelligence"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time. All paths are relative
        to the workspace root.
        """
        repo = "docs/repo/codebase_intelligence"
        run = f"{repo}/runs/{{job_id}}"
        out = f"{run}/output"
        cache = f"{out}/.cache"

        return {
            # -- Input Artifacts (external, provided at invocation) --
            "SOURCE_CODEBASE_DIR": "docs/repo/codebase/current/",
            "AUDIENCES_DIR": f"{repo}/audiences/",
            "CONFIG_FILE": f"{repo}/config.json",

            # -- Phase 1: Input Preparation --
            "INPUT_VALIDATION_REPORT": f"{run}/INPUT_VALIDATION-{{seq}}.json",
            "RUNTIME_CONFIG": f"{cache}/runtime_config.json",

            # -- Phase 2: Input Parsing (Layer 1) --
            "FILE_INVENTORY": f"{cache}/file_inventory.json",
            "PARSE_ERRORS_LOG": f"{cache}/parse_errors.json",
            "SCAN_INVARIANT_REPORT": f"{run}/SCAN_INVARIANT-{{seq}}.json",
            "IMPORT_GRAPH": f"{cache}/import_graph.json",
            "SOURCE_SYMBOLS": f"{cache}/source_symbols.json",
            "IMPORT_INVARIANT_REPORT": f"{run}/IMPORT_INVARIANT-{{seq}}.json",

            # -- Phase 3: Analysis (Layer 2) --
            "AUDIENCE_OUTPUT_DOCS": f"{cache}/audience_output_docs.json",
            "AUDIENCE_INVARIANT_REPORT": f"{run}/AUDIENCE_INVARIANT-{{seq}}.json",
            "AUDIENCE_VALIDATION_REPORT": f"{run}/AUDIENCE_VALIDATION-{{seq}}.json",
            "HEALTH_FINDINGS": f"{cache}/health_findings.json",
            "HEALTH_INVARIANT_REPORT": f"{run}/HEALTH_INVARIANT-{{seq}}.json",
            "SECURITY_FINDINGS": f"{cache}/security_findings.json",
            "SECURITY_INVARIANT_REPORT": f"{run}/SECURITY_INVARIANT-{{seq}}.json",

            # -- Phase 4: Findings Assembly --
            "STRUCTURAL_HEALTH_REPORT_DRAFT": f"{cache}/health_report_draft.json",
            "SECURITY_AUDIT_REPORT_DRAFT": f"{cache}/security_report_draft.json",
            "ASSEMBLY_INVARIANT_REPORT": f"{run}/ASSEMBLY_INVARIANT-{{seq}}.json",

            # -- Phase 5: Validation and Review --
            "RUN_MANIFEST": f"{cache}/run_manifest.json",
            "OUTPUT_VALIDATION_REPORT": f"{run}/OUTPUT_VALIDATION-{{seq}}.json",
            "QUALITY_REVIEW_REPORT": f"{run}/QUALITY_REVIEW-{{seq}}.json",

            # -- Phase 5: Output Rendering (concrete files) --
            "AUDIENCE_META_CONTENT": f"{out}/audience_meta_content/",
            "STRUCTURAL_HEALTH_REPORT": f"{out}/health_report.md",
            "SECURITY_AUDIT_REPORT": f"{out}/security_report.md",

            # -- Phase 6: Delivery (promoted files) --
            "AUDIENCE_META_CONTENT_PROMOTED": f"{out}/promoted/audience_meta_content/",
            "STRUCTURAL_HEALTH_REPORT_PROMOTED": f"{out}/promoted/health_report.md",
            "SECURITY_AUDIT_REPORT_PROMOTED": f"{out}/promoted/security_report.md",
            "RUN_MANIFEST_PROMOTED": f"{out}/promoted/RUN_MANIFEST.md",

            # -- Auxiliary: Quality Review Refinement --
            "ADJUSTED_CONFIG": f"{cache}/adjusted_config.json",

            # -- Completion --
            "COMPLETION_RESULT": f"{run}/COMPLETION_RESULT-{{seq}}.json",
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
            get_governance_runtime_root() / "BASE_COMPOSITION_STANDARD_v1.0.md"
        )

        # Identity context
        result["CODENAME"] = "codebase_intelligence"
        result["GENERATOR_NAME"] = "Codebase Intelligence Generator"
        result["GENERATOR_VERSION"] = "1.0.0"

        # Resolve input spec paths
        resolve_input_specs(
            result, state, self.workflow_name,
            ["SOURCE_CODEBASE_DIR", "AUDIENCES_DIR", "CONFIG_FILE"]
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
