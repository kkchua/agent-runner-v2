"""Output paths for sdlc_30_backlog_v1 workflow.

This module defines the artifact path mappings for the backlog workflow,
following the SDLC delivery folder structure and naming convention.
"""
from __future__ import annotations

import datetime as dt
from typing import Any


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Build output path mappings for sdlc_30_backlog_v1 workflow.

    This function returns a dictionary mapping artifact keys to their
    relative paths within the repository, following the SDLC delivery
    folder structure.

    Args:
        job_id: Job identifier for path construction.
        mode: Execution mode (e.g., "manual", "daemon").

    Returns:
        Dictionary mapping artifact keys to relative paths.
    """
    del mode
    date_str = dt.datetime.now().strftime("%Y%m%d")

    # Base delivery directory
    delivery_base = "docs/repo/agent_runner/sdlc/delivery"

    return {
        # Backlog document (draft stage)
        "BACKLOG_FILE": f"{delivery_base}/backlogs/BACKLOG-{date_str}-001_{{slug}}.md",

        # Review document (evidence artifact)
        "REVIEW_FILE_SUGGESTED": f"{delivery_base}/backlogs/{job_id}-backlog-review.md",
    }
