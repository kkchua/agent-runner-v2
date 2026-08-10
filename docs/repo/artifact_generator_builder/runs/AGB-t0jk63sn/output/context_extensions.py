"""Context extensions for Text Summarizer workflow.

Registers artifact keys and resolves them to absolute paths at runtime.
The WorkflowExtensions class provides the bridge between artifact key
definitions and the filesystem paths the runner uses.
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import (
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class TextSummarizerExtensions(WorkflowExtensions):
    """Artifact key registration and path resolution for Text Summarizer.

    This workflow transforms an input text file into a condensed summary
    via a 10-stage transformation pipeline with structural constraints
    and recovery loops.
    """

    workflow_name = "text_summarizer"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}"
    ) -> dict[str, str]:
        """Return a mapping of artifact keys to relative path templates.

        Path templates use ``{job_id}`` and ``{seq}`` placeholders that
        the runner resolves at execution time. All paths are relative
        to the workspace root.

        Returns:
            Dict mapping each artifact key to its filename pattern or
            relative path template.
        """
        return {
            # Input artifact
            "INPUT_TEXT_FILE": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "input/{input_filename}"
            ),
            # Phase 1: Input Preparation
            "INPUT_VALIDATION_REPORT": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "INPUT_VALIDATION-{seq}.json"
            ),
            # Pipeline Configuration
            "RUNTIME_CONFIG": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "RUNTIME_CONFIG-{seq}.json"
            ),
            # Phase 2: Pipeline Execution - Layer 1 Content Components
            "PARSED_CONTENT": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "PARSED_CONTENT-{seq}.json"
            ),
            "DocumentMeta": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "DocumentMeta-{seq}.json"
            ),
            "Section[]": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "Section-{seq}.json"
            ),
            "Paragraph[]": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "Paragraph-{seq}.json"
            ),
            "Sentence[]": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "Sentence-{seq}.json"
            ),
            "Layer_1_Validated": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "Layer_1_Validated-{seq}.json"
            ),
            # Phase 2: Pipeline Execution - Layer 2 Composition Components
            "KeyPoint[]": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "KeyPoint-{seq}.json"
            ),
            "RedundancyCluster[]": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "RedundancyCluster-{seq}.json"
            ),
            "KeyPoint_Deduplicated": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "KeyPoint_Deduplicated-{seq}.json"
            ),
            "KeyPoint_Selected": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "KeyPoint_Selected-{seq}.json"
            ),
            "SummaryBlock[]": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "SummaryBlock-{seq}.json"
            ),
            # Phase 2: Pipeline Execution - Layer 3 Output Components
            "ValidationRecord_CON002": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "ValidationRecord_CON002-{seq}.json"
            ),
            "ValidationRecord_CON001": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "ValidationRecord_CON001-{seq}.json"
            ),
            "SummaryDocument": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "SummaryDocument-{seq}.json"
            ),
            # Output artifact
            "SUMMARY_FILE": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "output/{output_filename}"
            ),
            # Phase 3: Output Validation
            "OUTPUT_VALIDATION_REPORT": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "OUTPUT_VALIDATION_REPORT-{seq}.md"
            ),
            "QUALITY_REVIEW_REPORT": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "QUALITY_REVIEW_REPORT-{seq}.md"
            ),
            # Phase 4: Delivery
            "SUMMARY_FILE_PROMOTED": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "promoted/{output_filename}"
            ),
            # Auxiliary: Quality Review Refinement
            "ADJUSTED_CONFIG": (
                "docs/repo/text_summarizer/runs/{job_id}/"
                "ADJUSTED_CONFIG-{seq}.json"
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

        Called before each step's prompt template is rendered. Converts
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

        # Resolve all artifact keys to absolute paths
        artifacts = state.get("artifacts") or {}
        for key, rel_path in self.register_artifact_keys().items():
            # Input artifacts provided externally already have absolute
            # paths in state - preserve them.
            if key in artifacts and artifacts[key]:
                existing = artifacts[key]
                if Path(existing).is_absolute():
                    result[key] = existing
                    continue
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
