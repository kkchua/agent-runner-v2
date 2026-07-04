from __future__ import annotations

"""
documentation_guardrails.py - Workflow-owned document inventory and protection helpers.
"""

from pathlib import Path
from typing import Iterable

from .doc_paths import architecture_site_rel, codebase_doc_rel, delivery_doc_rel, system_doc_rel


MASTER_BOOTSTRAP_WORKFLOW = "00_master_docs_bootstrap_v1"
EXECUTION_SCAFFOLD_WORKFLOW = "10_execution_scaffold_v1"
ARCHITECTURE_SITE_WORKFLOW = "50_architecture_site_v1"

WORKFLOW_GENERATED_MARKER = "workflow-generated"
DEFAULT_LEGACY_QUARANTINE_DIR = "docs/_workflow_legacy"


def managed_banner(*, workflow: str, step: str) -> str:
    return (
        f"> Managed by workflow: `{workflow}` / step: `{step}`\n"
        f"> This file is workflow-generated and protected from manual edits.\n\n"
    )


def master_bootstrap_doc_paths(*, job_id: str, mode: str) -> list[str]:
    return [
        codebase_doc_rel(f"04_changes/{job_id}-{mode}-snapshot.json"),
        codebase_doc_rel(f"04_changes/{job_id}-{mode}.md"),
        codebase_doc_rel("01_inventory/codebase_inventory.md"),
        system_doc_rel("project_analysis.md"),
        system_doc_rel("README.md"),
        system_doc_rel("DOCUMENTATION_STANDARD.md"),
        system_doc_rel("BUNDLE_TAXONOMY.md"),
        system_doc_rel("BUNDLE_MIGRATION_PLAN.md"),
        system_doc_rel("SYSTEM_OVERVIEW.md"),
        system_doc_rel("BUSINESS_CAPABILITIES.md"),
        system_doc_rel("FUNCTIONAL_SPEC.md"),
        system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md"),
        system_doc_rel("SYSTEM_CONTEXT.md"),
        system_doc_rel("COMPONENT_ARCHITECTURE.md"),
        system_doc_rel("DECISION_LOG.md"),
        system_doc_rel("SYSTEM_FILE_STRUCTURE.md"),
        system_doc_rel("DEVELOPER_GUIDE.md"),
        system_doc_rel("RUNBOOK.md"),
        system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
        system_doc_rel(f"{job_id}-{mode}-change-log.md"),
        system_doc_rel(f"{job_id}-{mode}-validation.md"),
        system_doc_rel(f"{job_id}-bootstrap-summary.md"),
    ]


def legacy_master_bootstrap_doc_paths(*, job_id: str, mode: str) -> list[str]:
    return [
        system_doc_rel("README.md"),
        system_doc_rel("DOCUMENTATION_STANDARD.md"),
        system_doc_rel("SYSTEM_OVERVIEW.md"),
        system_doc_rel("BUSINESS_CAPABILITIES.md"),
        system_doc_rel("FUNCTIONAL_SPEC.md"),
        system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md"),
        system_doc_rel("SYSTEM_CONTEXT.md"),
        system_doc_rel("COMPONENT_ARCHITECTURE.md"),
        system_doc_rel("DECISION_LOG.md"),
        system_doc_rel("SYSTEM_FILE_STRUCTURE.md"),
        system_doc_rel("DEVELOPER_GUIDE.md"),
        system_doc_rel("RUNBOOK.md"),
        system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
        system_doc_rel(f"{job_id}-bootstrap-change-log.md"),
        system_doc_rel(f"{job_id}-bootstrap-validation.md"),
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
    for path in docs_root.rglob("*"):
        if not path.is_file():
            continue
        try:
            if quarantine_root in path.resolve().parents:
                continue
        except OSError:
            continue
        if _content_mentions_workflow(path, template_group):
            matches.append(path.relative_to(project_root).as_posix())
    return _unique_paths(matches)


def workflow_canonical_doc_paths(*, template_group: str, state: dict) -> list[str]:
    job_id = str(state.get("job_id") or state.get("workflow_run_id") or "").strip()
    mode = str((state.get("current_step_cfg") or {}).get("mode") or state.get("current_mode") or "bootstrap")
    if template_group == MASTER_BOOTSTRAP_WORKFLOW:
        return master_bootstrap_doc_paths(job_id=job_id, mode=mode)
    if template_group == EXECUTION_SCAFFOLD_WORKFLOW:
        return execution_scaffold_doc_paths()
    if template_group == ARCHITECTURE_SITE_WORKFLOW:
        return architecture_site_doc_paths()
    return []


def workflow_legacy_doc_paths(*, template_group: str, state: dict) -> list[str]:
    job_id = str(state.get("job_id") or state.get("workflow_run_id") or "").strip()
    mode = str((state.get("current_step_cfg") or {}).get("mode") or state.get("current_mode") or "bootstrap")
    if template_group == MASTER_BOOTSTRAP_WORKFLOW:
        return legacy_master_bootstrap_doc_paths(job_id=job_id, mode=mode)
    return []


def master_bootstrap_artifact_candidates(*, job_id: str, mode: str) -> dict[str, list[str]]:
    canonical = {
        "PROJECT_ANALYSIS": system_doc_rel("project_analysis.md"),
        "SYSTEM_DOCS_INDEX": system_doc_rel("README.md"),
        "SYSTEM_DOCS_CHANGE_LOG": system_doc_rel(f"{job_id}-{mode}-change-log.md"),
        "SYSTEM_DOCS_VALIDATION": system_doc_rel(f"{job_id}-{mode}-validation.md"),
        "SYSTEM_DOC_STANDARD": system_doc_rel("DOCUMENTATION_STANDARD.md"),
        "BUNDLE_TAXONOMY": system_doc_rel("BUNDLE_TAXONOMY.md"),
        "BUNDLE_MIGRATION_PLAN": system_doc_rel("BUNDLE_MIGRATION_PLAN.md"),
        "SYSTEM_OVERVIEW": system_doc_rel("SYSTEM_OVERVIEW.md"),
        "BUSINESS_CAPABILITIES": system_doc_rel("BUSINESS_CAPABILITIES.md"),
        "FUNCTIONAL_SPEC": system_doc_rel("FUNCTIONAL_SPEC.md"),
        "NON_FUNCTIONAL_REQUIREMENTS": system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md"),
        "SYSTEM_CONTEXT": system_doc_rel("SYSTEM_CONTEXT.md"),
        "COMPONENT_ARCHITECTURE": system_doc_rel("COMPONENT_ARCHITECTURE.md"),
        "DECISION_LOG": system_doc_rel("DECISION_LOG.md"),
        "SYSTEM_FILE_STRUCTURE": system_doc_rel("SYSTEM_FILE_STRUCTURE.md"),
        "DEVELOPER_GUIDE": system_doc_rel("DEVELOPER_GUIDE.md"),
        "RUNBOOK": system_doc_rel("RUNBOOK.md"),
        "EXISTING_REPO_WORKFLOW_SOP": system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
        "BOOTSTRAP_SUMMARY": system_doc_rel(f"{job_id}-bootstrap-summary.md"),
    }
    legacy = {
        "PROJECT_ANALYSIS": [system_doc_rel("project_analysis.md")],
        "SYSTEM_DOCS_INDEX": [system_doc_rel("README.md")],
        "SYSTEM_DOCS_CHANGE_LOG": [system_doc_rel(f"{job_id}-bootstrap-change-log.md")],
        "SYSTEM_DOCS_VALIDATION": [system_doc_rel(f"{job_id}-bootstrap-validation.md")],
        "SYSTEM_DOC_STANDARD": [system_doc_rel("DOCUMENTATION_STANDARD.md")],
        "BUNDLE_TAXONOMY": [system_doc_rel("BUNDLE_TAXONOMY.md")],
        "BUNDLE_MIGRATION_PLAN": [system_doc_rel("BUNDLE_MIGRATION_PLAN.md")],
        "SYSTEM_OVERVIEW": [system_doc_rel("SYSTEM_OVERVIEW.md")],
        "BUSINESS_CAPABILITIES": [system_doc_rel("BUSINESS_CAPABILITIES.md")],
        "FUNCTIONAL_SPEC": [system_doc_rel("FUNCTIONAL_SPEC.md")],
        "NON_FUNCTIONAL_REQUIREMENTS": [system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md")],
        "SYSTEM_CONTEXT": [system_doc_rel("SYSTEM_CONTEXT.md")],
        "COMPONENT_ARCHITECTURE": [system_doc_rel("COMPONENT_ARCHITECTURE.md")],
        "DECISION_LOG": [system_doc_rel("DECISION_LOG.md")],
        "SYSTEM_FILE_STRUCTURE": [system_doc_rel("SYSTEM_FILE_STRUCTURE.md")],
        "DEVELOPER_GUIDE": [system_doc_rel("DEVELOPER_GUIDE.md")],
        "RUNBOOK": [system_doc_rel("RUNBOOK.md")],
        "EXISTING_REPO_WORKFLOW_SOP": [system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md")],
        "BOOTSTRAP_SUMMARY": [system_doc_rel(f"{job_id}-bootstrap-summary.md")],
    }
    return {
        key: [canonical[key], *legacy.get(key, [])]
        for key in canonical
    }


def execution_scaffold_doc_paths() -> list[str]:
    return [
        system_doc_rel("WORKFLOW_SOP_v1.md"),
        system_doc_rel("DELIVERY_STATUS_RULES_v1.md"),
        codebase_doc_rel("00_standards/CODEBASE_DOC_SOP_v1.md"),
        codebase_doc_rel("00_standards/CODEBASE_DOC_STATUS_RULES_v1.md"),
        system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
        system_doc_rel("templates/delivery/01_delivery_template_registry.md"),
        system_doc_rel("templates/delivery/02_delivery_initiative_template.md"),
        system_doc_rel("templates/delivery/03_delivery_plan_template.md"),
        system_doc_rel("templates/delivery/04_delivery_task_graph_template.md"),
        system_doc_rel("templates/delivery/05_delivery_task_template.md"),
        system_doc_rel("templates/delivery/06_delivery_impl_template.md"),
        system_doc_rel("templates/delivery/07_delivery_review_template.md"),
        system_doc_rel("templates/delivery/08_delivery_validation_template.md"),
        system_doc_rel("templates/delivery/09_delivery_memory_template.md"),
        system_doc_rel("templates/codebase/01_codebase_template_registry.md"),
        system_doc_rel("templates/codebase/02_codebase_inventory_template.md"),
        system_doc_rel("templates/codebase/03_codebase_module_template.md"),
        system_doc_rel("templates/codebase/04_codebase_component_template.md"),
        system_doc_rel("templates/codebase/05_codebase_change_template.md"),
        codebase_doc_rel("01_inventory/codebase_inventory.md"),
        delivery_doc_rel("00_standards/DELIVERY_AGENTS_MD.md"),
        delivery_doc_rel("00_standards/DELIVERY_AGENT_PLANNER.md"),
        delivery_doc_rel("00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md"),
        delivery_doc_rel("00_standards/DELIVERY_AGENT_IMPL_PLANNER.md"),
        delivery_doc_rel("00_standards/DELIVERY_AGENT_EXECUTOR.md"),
        delivery_doc_rel("00_standards/DELIVERY_AGENT_REVIEWER.md"),
        delivery_doc_rel("00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md"),
        delivery_doc_rel("DELIVERY_FOLDER_MAP.json"),
    ]


def architecture_site_doc_paths() -> list[str]:
    return [
        architecture_site_rel("index.html"),
        architecture_site_rel("stakeholders.html"),
        architecture_site_rel("developers.html"),
        architecture_site_rel("functional.html"),
        architecture_site_rel("runtime.html"),
        architecture_site_rel("components.html"),
        architecture_site_rel("manifest.json"),
        architecture_site_rel("validation.md"),
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
