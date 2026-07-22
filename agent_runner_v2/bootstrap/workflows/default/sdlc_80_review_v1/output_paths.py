"""Output paths for sdlc_80_review_v1 workflow.

This module defines the artifact path mappings for the review workflow,
following the SDLC delivery folder structure and naming convention.
"""
from __future__ import annotations

import datetime as dt
from typing import Any


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Build output path mappings for sdlc_80_review_v1 workflow.

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
        # Review document (final review)
        "REV_FILE": f"{delivery_base}/reviews/REV-{date_str}-001_{{slug}}.md",

        # Memory document (lessons learned)
        "MEM_FILE": f"{delivery_base}/reviews/MEM-{date_str}-001_{{slug}}.md",

        # Closure document (initiative closure)
        "CLOSE_FILE": f"{delivery_base}/reviews/CLOSE-{date_str}-001_{{slug}}.md",

        # Review evidence document
        "REVIEW_FILE_SUGGESTED": f"{delivery_base}/reviews/{job_id}-review-all-review.md",
    }
