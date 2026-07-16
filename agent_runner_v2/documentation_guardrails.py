from __future__ import annotations

"""
documentation_guardrails.py - Workflow-owned document inventory and protection helpers.
"""

from pathlib import Path
from typing import Iterable

from .doc_paths import architecture_site_rel, codebase_doc_rel, delivery_doc_rel, system_doc_rel
from .constants import (
    get_master_docs_output_paths,
    delivery_scaffold_docs,
    FOLDER_KEY_CODEBASE_CHANGES,
    FILENAME_CHANGE_LOG_PATTERN,
    FILENAME_VALIDATION_PATTERN,
    FILENAME_BOOTSTRAP_SUMMARY_PATTERN,
    EXT_MD,
    EXT_JSON,
    FILENAME_SITE_INDEX_HTML,
    FILENAME_SITE_MANIFEST_JSON,
    FILENAME_ARCH_STAKEHOLDER_HTML,
    FILENAME_ARCH_DEVELOPER_HTML,
    FILENAME_ARCH_FUNCTIONAL_HTML,
    FILENAME_ARCH_RUNTIME_HTML,
    FILENAME_ARCH_COMPONENTS_HTML,
    FILENAME_ARCH_VALIDATION_MD,
)


MASTER_BOOTSTRAP_WORKFLOWS: set[str] = {
    "00_layer1_governance_bootstrap_v1",
}
EXECUTION_SCAFFOLD_WORKFLOWS: set[str] = set()
ARCHITECTURE_SITE_WORKFLOW = ""

WORKFLOW_GENERATED_MARKER = "workflow-generated"
DEFAULT_LEGACY_QUARANTINE_DIR = "docs/_workflow_legacy"


def managed_banner(*, workflow: str, step: str) -> str:
    return (
        f"> Managed by workflow: `{workflow}` / step: `{step}`\n"
        f"> This file is workflow-generated and protected from manual edits.\n\n"
    )


def master_bootstrap_doc_paths(*, job_id: str, mode: str) -> list[str]:
    """Get all master bootstrap workflow document paths."""
    return list(_layer1_governance_doc_paths(job_id=job_id).values())


def legacy_master_bootstrap_doc_paths(*, job_id: str, mode: str) -> list[str]:
    """Get legacy master bootstrap document paths (subset without dynamic filenames)."""
    all_paths = _layer1_governance_doc_paths(job_id=job_id)
    return [
        path for key, path in all_paths.items()
        if key not in ["SYSTEM_DOCS_VALIDATION", "REVIEW_FILE_SUGGESTED"]
    ]


def _unique_paths(paths: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


def _content_mentions_workflow(path: Path, workflow_name: str) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    lowered = content.lower()
    workflow_token = workflow_name.lower()
    return (
        WORKFLOW_GENERATED_MARKER in lowered
        or f"managed by workflow: `{workflow_token}`" in lowered
        or f'workflow: "{workflow_token}"' in lowered
    )


def scan_workflow_generated_paths(*, project_root: Path, template_group: str) -> list[str]:
    docs_root = project_root / "docs"
    if not docs_root.exists():
        return []
    matches: list[str] = []
    quarantine_root = (project_root / DEFAULT_LEGACY_QUARANTINE_DIR).resolve()
    sites_root = (docs_root / "sites").resolve()
    for path in docs_root.rglob("*"):
        if not path.is_file():
            continue
        # Only scan markdown files
        if path.suffix.lower() != ".md":
            continue
        try:
            resolved = path.resolve()
            if quarantine_root in resolved.parents:
                continue
            if sites_root in resolved.parents or resolved == sites_root:
                continue
        except OSError:
            continue
        if _content_mentions_workflow(path, template_group):
            matches.append(path.relative_to(project_root).as_posix())
    return _unique_paths(matches)


def workflow_canonical_doc_paths(*, template_group: str, state: dict) -> list[str]:
    job_id = str(state.get("job_id") or state.get("workflow_run_id") or "").strip()
    mode = str((state.get("current_step_cfg") or {}).get("mode") or state.get("current_mode") or "bootstrap")
    if template_group in MASTER_BOOTSTRAP_WORKFLOWS:
        return master_bootstrap_doc_paths(job_id=job_id, mode=mode)
    if template_group in EXECUTION_SCAFFOLD_WORKFLOWS:
        return execution_scaffold_doc_paths()
    if template_group == ARCHITECTURE_SITE_WORKFLOW:
        return architecture_site_doc_paths()
    return []


def workflow_legacy_doc_paths(*, template_group: str, state: dict) -> list[str]:
    job_id = str(state.get("job_id") or state.get("workflow_run_id") or "").strip()
    mode = str((state.get("current_step_cfg") or {}).get("mode") or state.get("current_mode") or "bootstrap")
    if template_group in MASTER_BOOTSTRAP_WORKFLOWS:
        return legacy_master_bootstrap_doc_paths(job_id=job_id, mode=mode)
    return []


def master_bootstrap_artifact_candidates(*, job_id: str, mode: str) -> dict[str, list[str]]:
    """Get artifact path candidates for master bootstrap workflow."""
    canonical = _layer1_governance_doc_paths(job_id=job_id)
    
    # Build legacy paths (subset without dynamic filenames)
    legacy: dict[str, list[str]] = {}
    for key in canonical:
        if key not in ["SYSTEM_DOCS_CHANGE_LOG", "SYSTEM_DOCS_VALIDATION", "BOOTSTRAP_SUMMARY", "CODEBASE_SCAN_SNAPSHOT"]:
            legacy[key] = [canonical[key]]
        else:
            legacy[key] = []
    
    return {
        key: [canonical[key], *legacy.get(key, [])]
        for key in canonical
    }


def _layer1_governance_doc_paths(*, job_id: str) -> dict[str, str]:
    return {
        "SYSTEM_DOCS_INDEX": system_doc_rel("README.md"),
        "SYSTEM_DOC_STANDARD": system_doc_rel("DOCUMENTATION_STANDARD.md"),
        "BUNDLE_TAXONOMY": system_doc_rel("BUNDLE_TAXONOMY.md"),
        "RUNTIME_GOVERNANCE": system_doc_rel("RUNTIME_GOVERNANCE.md"),
        "SYSTEM_DOCS_VALIDATION": system_doc_rel(f"{job_id}-layer1-governance-validation.md"),
        "REVIEW_FILE_SUGGESTED": system_doc_rel(f"{job_id}-layer1-governance-review.md"),
    }


def execution_scaffold_doc_paths() -> list[str]:
    """Get all execution scaffold workflow document paths."""
    output_paths = delivery_scaffold_docs()
    return list(output_paths.values())


def architecture_site_doc_paths() -> list[str]:
    """Get all architecture site document paths."""
    return [
        architecture_site_rel(FILENAME_SITE_INDEX_HTML),
        architecture_site_rel(FILENAME_ARCH_STAKEHOLDER_HTML),
        architecture_site_rel(FILENAME_ARCH_DEVELOPER_HTML),
        architecture_site_rel(FILENAME_ARCH_FUNCTIONAL_HTML),
        architecture_site_rel(FILENAME_ARCH_RUNTIME_HTML),
        architecture_site_rel(FILENAME_ARCH_COMPONENTS_HTML),
        architecture_site_rel(FILENAME_SITE_MANIFEST_JSON),
        architecture_site_rel(FILENAME_ARCH_VALIDATION_MD),
    ]


def workflow_generated_doc_paths(*, template_group: str, state: dict) -> list[str]:
    return _unique_paths(workflow_canonical_doc_paths(template_group=template_group, state=state))


def workflow_stale_generated_doc_paths(*, template_group: str, state: dict, project_root: Path) -> list[str]:
    canonical = set(workflow_canonical_doc_paths(template_group=template_group, state=state))
    stale: list[str] = []
    for rel_path in _unique_paths(
        workflow_legacy_doc_paths(template_group=template_group, state=state)
        + scan_workflow_generated_paths(project_root=project_root, template_group=template_group)
    ):
        if rel_path not in canonical:
            stale.append(rel_path)
    return _unique_paths(stale)


def workflow_owned_doc_paths_for_cleanup(*, template_group: str, state: dict, project_root: Path) -> list[str]:
    return _unique_paths(workflow_generated_doc_paths(template_group=template_group, state=state) + workflow_stale_generated_doc_paths(template_group=template_group, state=state, project_root=project_root))


def generated_doc_manifest(*, template_group: str, state: dict) -> str:
    paths = workflow_generated_doc_paths(template_group=template_group, state=state)
    if not paths:
        return ""
    lines = ["## Protected Generated Docs", "", "| Path | Owner |", "|------|-------|"]
    for path in paths:
        owner = template_group
        lines.append(f"| `{path}` | `{owner}` |")
    return "\n".join(lines) + "\n"


def snapshot_paths(*, project_root: Path, rel_paths: Iterable[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel_path in rel_paths:
        path = project_root / rel_path
        if path.exists() and path.is_file():
            out[rel_path] = _hash_file(path)
    return out


def _hash_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()
