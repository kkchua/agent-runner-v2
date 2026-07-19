from __future__ import annotations


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    return {
        "PROJECT_ANALYSIS": "docs/repo/governance/PROJECT_ANALYSIS.md",
        "SYSTEM_DOCS_INDEX": "docs/repo/governance/README.md",
        "SYSTEM_DOCS_CHANGE_LOG": f"docs/repo/governance/{job_id}-{mode}-change-log.md",
        "SYSTEM_DOCS_VALIDATION": f"docs/repo/governance/{job_id}-{mode}-validation.md",
        "SYSTEM_DOC_STANDARD": "docs/repo/governance/REPO_DOCUMENTATION_STANDARD.md",
        "DECISION_LOG": "docs/repo/governance/DECISION_LOG.md",
        "DEVELOPER_GUIDE": "docs/repo/governance/DEVELOPER_GUIDE.md",
        "BOOTSTRAP_SUMMARY": f"docs/repo/governance/{job_id}-bootstrap-summary.md",
        "REVIEW_FILE_SUGGESTED": f"docs/repo/governance/{job_id}-master-system-docs-review.md",
        "CODEBASE_SCAN_SNAPSHOT": f"docs/repo/codebase/04_changes/{job_id}-{mode}-snapshot.json",
    }
