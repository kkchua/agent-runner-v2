"""Context extensions for 00_master_docs_bootstrap_v2.

Injects master-docs-specific path aliases into the prompt context,
replacing the old _set_master_docs_aliases() function in step_runner.py.

This module is discovered and loaded dynamically by
step_runner._apply_workflow_package_context_hooks().
"""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import get_master_docs_output_paths


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    """Return additional context variables for master bootstrap docs.

    For every artifact in MASTER_DOCS_OUTPUT_PATHS, injects:
      - ``{KEY}``         → resolved output path
      - ``{KEY}_PATH``    → same resolved path
      - ``{KEY}_METAJSON`` → path to the meta.json sidecar

    This mirrors the logic of the removed ``_set_master_docs_aliases()``.
    """
    job_id = str(state.get("job_id") or "00DOC").strip()
    step_names = _master_doc_step_names()
    mode = str((step_cfg or {}).get("mode") or state.get("current_mode") or "bootstrap")

    output_paths = get_master_docs_output_paths(job_id=job_id, mode=mode)

    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    if not step_dir_rel and step_names:
        try:
            idx = step_names.index(step) + 1
        except ValueError:
            idx = 1
        template_group = state.get("template_group", "")
        job_id_path = PurePath(state.get("job_id", ""))
        step_dir_rel = f"{template_group}/{job_id_path}/{idx:02d}_{step}"

    extensions: dict[str, str] = {}
    for artifact_key, output_path in output_paths.items():
        resolved_path = str(output_path).replace("\\", "/")
        extensions[artifact_key] = resolved_path
        extensions[f"{artifact_key}_PATH"] = resolved_path

        # Build meta.json path
        if step_dir_rel:
            meta = f"{step_dir_rel}/meta.json"
        else:
            p = PurePath(resolved_path)
            meta = str(p.parent / f"{p.stem}.meta.json").replace("\\", "/")
        extensions[f"{artifact_key}_METAJSON"] = meta

    return extensions


def _master_doc_step_names() -> list[str]:
    """Return the ordered step names for the master bootstrap workflow."""
    return [
        "00_scan_repo_codebase",
        "01_generate_codebase_baseline",
        "02_generate_project_analysis",
        "03_generate_system_overview_docs",
        "04_generate_architecture_docs",
        "04b_generate_integration_docs",
        "04c_generate_failure_docs",
        "04d_generate_architecture_flow_docs",
        "05_review_master_system_docs",
        "06_refine_master_system_docs",
        "07_validate_codebase_baseline",
        "08_validate_master_system_docs",
        "09_finalize_bootstrap",
    ]
