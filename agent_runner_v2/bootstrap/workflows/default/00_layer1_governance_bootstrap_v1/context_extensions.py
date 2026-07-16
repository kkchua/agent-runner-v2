"""Context extensions for 00_layer1_governance_bootstrap_v1."""

from __future__ import annotations

from pathlib import Path, PurePath

from agent_runner_v2.constants import ARTIFACT_KEY_REVIEW, get_master_docs_output_paths
from agent_runner_v2.runtime_context import JOBS_ROOT, resolve_repo_or_runtime_path


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    job_id = str(state.get("job_id") or "00L1").strip()
    mode = str((step_cfg or {}).get("mode") or state.get("current_mode") or "bootstrap")
    root = Path(project_root or Path.cwd()).resolve()
    output_paths = get_master_docs_output_paths(job_id=job_id, mode=mode)

    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    if not step_dir_rel:
        try:
            idx = _layer1_step_names().index(step) + 1
        except ValueError:
            idx = 1
        template_group = state.get("template_group", "")
        step_dir_rel = f"{template_group}/{job_id}/{idx:02d}_{step}"
    step_dir_meta = str((JOBS_ROOT / step_dir_rel / "meta.json").resolve()) if step_dir_rel else ""

    keys = [
        "SYSTEM_DOCS_INDEX",
        "SYSTEM_DOC_STANDARD",
        "BUNDLE_TAXONOMY",
        "RUNTIME_GOVERNANCE",
    ]
    extensions: dict[str, str] = {}
    for artifact_key in keys:
        rel_path = output_paths.get(artifact_key)
        if not rel_path:
            continue
        resolved = resolve_repo_or_runtime_path(
            str(rel_path),
            project_root=root,
            runtime_root=JOBS_ROOT,
        )
        resolved_str = str(resolved)
        extensions[artifact_key] = resolved_str
        extensions[f"{artifact_key}_PATH"] = resolved_str
        p = PurePath(resolved_str)
        extensions[f"{artifact_key}_METAJSON"] = step_dir_meta or str(p.parent / f"{p.stem}.meta.json")

    validation_name = f"{job_id}-layer1-governance-validation.md"
    validation_path = resolve_repo_or_runtime_path(
        f"docs/system/00_governance/bootstrap/{validation_name}",
        project_root=root,
        runtime_root=JOBS_ROOT,
    )
    validation_str = str(validation_path)
    extensions["SYSTEM_DOCS_VALIDATION"] = validation_str
    extensions["SYSTEM_DOCS_VALIDATION_PATH"] = validation_str
    validation_pure = PurePath(validation_str)
    extensions["SYSTEM_DOCS_VALIDATION_METAJSON"] = step_dir_meta or str(
        validation_pure.parent / f"{validation_pure.stem}.meta.json"
    )

    review_filename = _layer1_review_filename(step=step, job_id=job_id)
    if review_filename:
        resolved_review = resolve_repo_or_runtime_path(
            f"docs/system/00_governance/bootstrap/{review_filename}",
            project_root=root,
            runtime_root=JOBS_ROOT,
        )
        review_str = str(resolved_review)
        extensions[ARTIFACT_KEY_REVIEW] = review_str
        extensions["REVIEW_FILE_PATH"] = review_str
        p = PurePath(review_str)
        extensions[f"{ARTIFACT_KEY_REVIEW}_METAJSON"] = str(p.parent / f"{p.stem}.meta.json")
        extensions["REVIEW_FILE_METAJSON"] = extensions[f"{ARTIFACT_KEY_REVIEW}_METAJSON"]

    return extensions


def _layer1_step_names() -> list[str]:
    return [
        "generate_layer1_governance_docs",
        "review_layer1_governance_docs",
        "refine_layer1_governance_docs",
        "validate_layer1_governance_docs",
        "audit_layer1_governance_accuracy",
        "stepCompletion",
    ]


def _layer1_review_filename(*, step: str, job_id: str) -> str:
    if step == "review_layer1_governance_docs":
        return f"{job_id}-layer1-governance-review.md"
    if step == "audit_layer1_governance_accuracy":
        return f"{job_id}-layer1-governance-audit.md"
    return ""
