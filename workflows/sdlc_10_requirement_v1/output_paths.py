"""Output paths for sdlc_10_requirement_v1 workflow.

This module defines the artifact path mappings for the requirement intake
workflow, following the SDLC delivery folder structure and naming convention.
"""
from __future__ import annotations

import datetime as dt
from typing import Any


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Build output path mappings for sdlc_10_requirement_v1 workflow.
    
    This function returns a dictionary mapping artifact keys to their
    relative paths within the repository, following the SDLC delivery
    folder structure.
    
    Args:
        job_id: Job identifier for path construction.
        mode: Execution mode (e.g., "manual", "daemon").
    
    Returns:
        Dictionary mapping artifact keys to relative paths.
    """
    date_str = dt.datetime.now().strftime("%Y%m%d")
    
    # Base delivery directory
    delivery_base = "docs/repo/agent_runner/sdlc/delivery"
    
    return {
        # Draft initiative input (user-provided)
        "DRAFT_INIT_DOC": f"{delivery_base}/draft_initiatives/DRAFT-INIT-{date_str}-001_{{slug}}.md",

        # Initiative document (approved output)
        "INIT_DOC": f"{delivery_base}/initiatives/INIT-{date_str}-001_{{slug}}.md",

        # Review document (evidence artifact)
        "REVIEW_FILE_SUGGESTED": f"{delivery_base}/initiatives/{job_id}-init-review.md",
    }
