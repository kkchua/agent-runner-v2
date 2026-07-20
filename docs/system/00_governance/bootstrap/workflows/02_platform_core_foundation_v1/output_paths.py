from __future__ import annotations


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    del mode
    run_root = f"docs/system/00_governance/platform/runs/{job_id}"
    history_root = f"docs/system/00_governance/platform/history/{job_id}"
    current_root = "docs/system/00_governance/platform/current"
    return {
        "L2_PLATFORM_INDEX": f"{run_root}/README.md",
        "L2_RUNTIME_MODEL": f"{run_root}/RUNTIME_MODEL.md",
        "L2_BUNDLE_AUTHORING_CONTRACT": f"{run_root}/BUNDLE_AUTHORING_CONTRACT.md",
        "L2_SHARED_SERVICES": f"{run_root}/SHARED_SERVICES.md",
        "L2_METADATA_CONTRACT": f"{run_root}/METADATA_CONTRACT.md",
        "L2_VALIDATION_CONTRACT": f"{run_root}/VALIDATION_CONTRACT.md",
        "PLATFORM_CONTEXT_INVENTORY": f"{run_root}/{job_id}-platform-context-inventory.md",
        "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-platform-core-review.md",
        "PLATFORM_CORE_VALIDATION": f"{run_root}/{job_id}-platform-core-validation.md",
        "AUDIT_FILE_SUGGESTED": f"{run_root}/{job_id}-platform-core-audit.md",
        "PLATFORM_PUBLISH_MANIFEST": f"{current_root}/platform_set_manifest.json",
        "PLATFORM_PUBLISH_MANIFEST_HISTORY": f"{history_root}/platform_set_manifest.json",
        "PLATFORM_CURRENT_ROOT": current_root,
        "PLATFORM_HISTORY_ROOT": history_root,
    }
