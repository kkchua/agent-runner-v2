"""Context extensions for Codebase Intelligence Generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import (
    WorkflowExtensions,
    resolve_output_artifacts,
)


class CodebaseIntelligenceExtensions(WorkflowExtensions):
    workflow_name = "codebase_intelligence"

    # -- Output artifacts: resolved to {workspace_root}/output/{job_id}/ --
    OUTPUT_ARTIFACTS: dict[str, str] = {
        "CODEBASE_INVENTORY": "CODEBASE_INVENTORY-{seq}.json",
        "IMPORT_GRAPH": "IMPORT_GRAPH-{seq}.json",
        "AUDIENCE_META_FILE": "AUDIENCE_META_FILE-{seq}.md",
        "HEALTH_FINDINGS_FILE": "HEALTH_FINDINGS_FILE-{seq}.md",
        "SECURITY_FINDINGS_FILE": "SECURITY_FINDINGS_FILE-{seq}.md",
        "FINDINGS_REPORT_FILE": "FINDINGS_REPORT_FILE-{seq}.md",
        "VALIDATION_REPORT_FILE": "VALIDATION_REPORT_FILE-{seq}.json",
    }

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        combined: dict[str, str] = {}
        # Input directories — predefined defaults, not user inputs
        combined["CODEBASE_DOCS_DIR"] = "docs/repo/codebase/current"
        combined["SOURCE_CODE_DIR"] = "."
        for key, pattern in self.OUTPUT_ARTIFACTS.items():
            combined[key] = f"output/{job_id}/{pattern}"
        return combined

    def build_context_extensions(
        self, *, state, step, step_cfg, ctx, project_root=None,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        workspace_root = Path(project_root or get_workspace_root() or Path.cwd()).resolve()
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())
        result["BASE_COMPOSITION_STANDARD"] = str(
            get_governance_runtime_root() / "BASE_COMPOSITION_STANDARD_v1.0.md"
        )
        # Input directories — use predefined defaults (workspace-relative)
        result["CODEBASE_DOCS_DIR"] = str(workspace_root / "docs" / "repo" / "codebase" / "current")
        result["SOURCE_CODE_DIR"] = str(workspace_root)
        # Update state artifacts so _missing_artifacts sees valid paths
        artifacts = state.get("artifacts") or {}
        artifacts["CODEBASE_DOCS_DIR"] = result["CODEBASE_DOCS_DIR"]
        artifacts["SOURCE_CODE_DIR"] = result["SOURCE_CODE_DIR"]
        resolve_output_artifacts(result, state, workspace_root, self.OUTPUT_ARTIFACTS)
        return result

    def install_to_global(self, *, workspace_root, runner_home):
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        return {"status": "NO_OP"}
