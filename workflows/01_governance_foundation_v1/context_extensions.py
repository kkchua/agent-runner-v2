"""Context extensions for 01_governance_foundation_v1."""

from __future__ import annotations

from pathlib import Path, PurePath

from agent_runner_v2.constants import ARTIFACT_KEY_AUDIT, ARTIFACT_KEY_REVIEW
from agent_runner_v2.runtime_context import JOBS_ROOT, resolve_repo_or_runtime_path


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}", loop_iteration: int = 0) -> dict[str, str]:
    del mode
    run_root = f"docs/system/00_governance/foundation/runs/{job_id}"
    history_root = f"docs/system/00_governance/foundation/history/{job_id}"
    current_root = "docs/system/00_governance/foundation/current"
    iter_suffix = f"_iter{loop_iteration + 1}" if loop_iteration > 0 else ""
    return {
        "L1_FOUNDATION_INDEX": f"{run_root}/README.md",
        "L1_LAYER_MODEL": f"{run_root}/LAYER_MODEL.md",
        "L1_DOCUMENT_AUTHORITY": f"{run_root}/DOCUMENT_AUTHORITY.md",
        "L1_BUNDLE_TAXONOMY": f"{run_root}/BUNDLE_TAXONOMY.md",
        "L1_GOVERNANCE_LIFECYCLE": f"{run_root}/GOVERNANCE_LIFECYCLE.md",
        "L1_METADATA_STANDARD": f"{run_root}/METADATA_STANDARD.md",
        "GOVERNANCE_CONTEXT_INVENTORY": f"{run_root}/{job_id}-governance-context-inventory.md",
        "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-review{iter_suffix}.md",
        "GOVERNANCE_FOUNDATION_VALIDATION": f"{run_root}/{job_id}-governance-foundation-validation{iter_suffix}.md",
        "AUDIT_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-audit{iter_suffix}.md",
        "GOVERNANCE_PUBLISH_MANIFEST": f"{current_root}/governance_set_manifest.json",
        "GOVERNANCE_PUBLISH_MANIFEST_HISTORY": f"{history_root}/governance_set_manifest.json",
        "GOVERNANCE_CURRENT_ROOT": current_root,
        "GOVERNANCE_HISTORY_ROOT": history_root,
    }


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    del step_cfg, ctx
    job_id = str(state.get("job_id") or "00GF").strip()
    root = Path(project_root or Path.cwd()).resolve()
    loop_ctx = state.get("loop_context") or {}
    loop_iteration = int(loop_ctx.get("loop_iteration", 0)) if loop_ctx.get("active") else 0
    output_paths = build_output_paths(job_id=job_id, mode=str(state.get("mode") or "default"), loop_iteration=loop_iteration)

    extensions: dict[str, str] = {
        "MASTERPLAN_ARCHITECTURE_PATH": str(root / "masterplan" / "LAYER_ARCHITECTURE_MASTERPLAN.md"),
        "MASTERPLAN_WORKFLOW_SPEC_PATH": str(root / "masterplan" / "LAYER1_GOVERNANCE_SPECIFICATION.md"),
        "GOVERNANCE_ACTIVE_ROOT": str(root / "docs" / "system" / "00_governance" / "foundation" / "current"),
        "GOVERNANCE_HISTORY_ROOT": str(root / output_paths["GOVERNANCE_HISTORY_ROOT"]),
    }

    for artifact_key, rel_path in output_paths.items():
        if not rel_path.endswith((".md", ".json")):
            continue
        resolved = resolve_repo_or_runtime_path(rel_path, project_root=root, runtime_root=JOBS_ROOT)
        resolved_str = str(resolved)
        extensions[artifact_key] = resolved_str
        extensions[f"{artifact_key}_PATH"] = resolved_str
        pure = PurePath(resolved_str)
        extensions[f"{artifact_key}_METAJSON"] = str(pure.parent / f"{pure.stem}.meta.json")

    extensions[ARTIFACT_KEY_REVIEW] = extensions["REVIEW_FILE_SUGGESTED"]
    extensions["REVIEW_FILE_PATH"] = extensions["REVIEW_FILE_SUGGESTED"]
    extensions["REVIEW_FILE_METAJSON"] = extensions["REVIEW_FILE_SUGGESTED_METAJSON"]

    extensions[ARTIFACT_KEY_AUDIT] = extensions["AUDIT_FILE_SUGGESTED"]
    extensions["AUDIT_FILE_PATH"] = extensions["AUDIT_FILE_SUGGESTED"]
    extensions["AUDIT_FILE_METAJSON"] = extensions["AUDIT_FILE_SUGGESTED_METAJSON"]

    return extensions
