from __future__ import annotations


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    del mode
    run_root = f"docs/system/00_governance/foundation/runs/{job_id}"
    history_root = f"docs/system/00_governance/foundation/history/{job_id}"
    current_root = "docs/system/00_governance/foundation/current"
    return {
        "L1_FOUNDATION_INDEX": f"{run_root}/README.md",
        "L1_LAYER_MODEL": f"{run_root}/LAYER_MODEL.md",
        "L1_DOCUMENT_AUTHORITY": f"{run_root}/DOCUMENT_AUTHORITY.md",
        "L1_BUNDLE_TAXONOMY": f"{run_root}/BUNDLE_TAXONOMY.md",
        "L1_GOVERNANCE_LIFECYCLE": f"{run_root}/GOVERNANCE_LIFECYCLE.md",
        "L1_METADATA_STANDARD": f"{run_root}/METADATA_STANDARD.md",
        "GOVERNANCE_CONTEXT_INVENTORY": f"{run_root}/{job_id}-governance-context-inventory.md",
        "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-review.md",
        "GOVERNANCE_FOUNDATION_VALIDATION": f"{run_root}/{job_id}-governance-foundation-validation.md",
        "AUDIT_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-audit.md",
        "GOVERNANCE_PUBLISH_MANIFEST": f"{current_root}/governance_set_manifest.json",
        "GOVERNANCE_PUBLISH_MANIFEST_HISTORY": f"{history_root}/governance_set_manifest.json",
        "GOVERNANCE_CURRENT_ROOT": current_root,
        "GOVERNANCE_HISTORY_ROOT": history_root,
    }
