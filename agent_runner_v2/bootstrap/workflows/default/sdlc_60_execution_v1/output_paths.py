"""Output paths for sdlc_60_execution_v1 workflow."""
from __future__ import annotations

import datetime as dt


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Build output path mappings for sdlc_60_execution_v1 workflow.

    Args:
        job_id: Job identifier for path construction.
        mode: Execution mode (e.g., "manual", "daemon").

    Returns:
        Dictionary mapping artifact keys to relative paths.
    """
    del mode
    date_str = dt.datetime.now().strftime("%Y%m%d")
    delivery_base = "docs/repo/agent_runner/sdlc/delivery"

    return {
        "EXEC_FILE": f"{delivery_base}/executions/EXEC-{date_str}-001-001_{{slug}}.md",
        "REVIEW_FILE_SUGGESTED": f"{delivery_base}/executions/{job_id}-exec-review.md",
    }
