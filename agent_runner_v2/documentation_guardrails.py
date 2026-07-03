from __future__ import annotations

"""
documentation_guardrails.py - Workflow-owned document inventory and protection helpers.
"""

from pathlib import Path
from typing import Iterable


MASTER_BOOTSTRAP_WORKFLOW = "00_master_docs_bootstrap_v1"
EXECUTION_SCAFFOLD_WORKFLOW = "10_execution_scaffold_v1"

WORKFLOW_GENERATED_MARKER = "workflow-generated"
DEFAULT_LEGACY_QUARANTINE_DIR = "docs/_workflow_legacy"


def managed_banner(*, workflow: str, step: str) -> str:
    return (
        f"> Managed by workflow: `{workflow}` / step: `{step}`\n"
        f"> This file is workflow-generated and protected from manual edits.\n\n"
    )


def master_bootstrap_doc_paths(*, job_id: str, mode: str) -> list[str]:
    return [
        "docs/codebase/04_changes/{job_id}-{mode}-snapshot.json".format(job_id=job_id, mode=mode),
        "docs/codebase/04_changes/{job_id}-{mode}.md".format(job_id=job_id, mode=mode),
        "docs/codebase/01_inventory/codebase_inventory.md",
        "docs/system/00_governance/bootstrap/project_analysis.md",
        "docs/system/00_governance/bootstrap/README.md",
        "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md",
        "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md",
        "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md",
        "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md",
        "docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md",
        "docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md",
        "docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md",
        "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md",
        "docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md",
        "docs/system/00_governance/bootstrap/DECISION_LOG.md",
        "docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md",
        "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md",
        "docs/system/00_governance/bootstrap/RUNBOOK.md",
        "docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md",
        "docs/system/00_governance/bootstrap/{job_id}-{mode}-change-log.md".format(job_id=job_id, mode=mode),
        "docs/system/00_governance/bootstrap/{job_id}-{mode}-validation.md".format(job_id=job_id, mode=mode),
        "docs/system/00_governance/bootstrap/{job_id}-bootstrap-summary.md".format(job_id=job_id),
    ]


def legacy_master_bootstrap_doc_paths(*, job_id: str, mode: str) -> list[str]:
    return [
        "docs/system/README.md",
        "docs/system/00_governance/DOCUMENTATION_STANDARD.md",
        "docs/system/01_overview/SYSTEM_OVERVIEW.md",
        "docs/system/01_overview/BUSINESS_CAPABILITIES.md",
        "docs/system/02_functional/FUNCTIONAL_SPEC.md",
        "docs/system/02_functional/NON_FUNCTIONAL_REQUIREMENTS.md",
        "docs/system/03_architecture/SYSTEM_CONTEXT.md",
        "docs/system/03_architecture/COMPONENT_ARCHITECTURE.md",
        "docs/system/03_architecture/DECISION_LOG.md",
        "docs/system/03_architecture/SYSTEM_FILE_STRUCTURE.md",
        "docs/engineering/DEVELOPER_GUIDE.md",
        "docs/operations/RUNBOOK.md",
        "docs/operations/EXISTING_REPO_WORKFLOW_SOP.md",
        "docs/system/00_governance/bootstrap/{job_id}-bootstrap-change-log.md".format(job_id=job_id),
        "docs/system/00_governance/bootstrap/{job_id}-bootstrap-validation.md".format(job_id=job_id),
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
    return []


def workflow_legacy_doc_paths(*, template_group: str, state: dict) -> list[str]:
    job_id = str(state.get("job_id") or state.get("workflow_run_id") or "").strip()
    mode = str((state.get("current_step_cfg") or {}).get("mode") or state.get("current_mode") or "bootstrap")
    if template_group == MASTER_BOOTSTRAP_WORKFLOW:
        return legacy_master_bootstrap_doc_paths(job_id=job_id, mode=mode)
    return []


def master_bootstrap_artifact_candidates(*, job_id: str, mode: str) -> dict[str, list[str]]:
    canonical = {
        "PROJECT_ANALYSIS": "docs/system/00_governance/bootstrap/project_analysis.md",
        "SYSTEM_DOCS_INDEX": "docs/system/00_governance/bootstrap/README.md",
        "SYSTEM_DOCS_CHANGE_LOG": "docs/system/00_governance/bootstrap/{job_id}-{mode}-change-log.md".format(
            job_id=job_id, mode=mode
        ),
        "SYSTEM_DOCS_VALIDATION": "docs/system/00_governance/bootstrap/{job_id}-{mode}-validation.md".format(
            job_id=job_id, mode=mode
        ),
        "SYSTEM_DOC_STANDARD": "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md",
        "BUNDLE_TAXONOMY": "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md",
        "BUNDLE_MIGRATION_PLAN": "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md",
        "SYSTEM_OVERVIEW": "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md",
        "BUSINESS_CAPABILITIES": "docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md",
        "FUNCTIONAL_SPEC": "docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md",
        "NON_FUNCTIONAL_REQUIREMENTS": "docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md",
        "SYSTEM_CONTEXT": "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md",
        "COMPONENT_ARCHITECTURE": "docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md",
        "DECISION_LOG": "docs/system/00_governance/bootstrap/DECISION_LOG.md",
        "SYSTEM_FILE_STRUCTURE": "docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md",
        "DEVELOPER_GUIDE": "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md",
        "RUNBOOK": "docs/system/00_governance/bootstrap/RUNBOOK.md",
        "EXISTING_REPO_WORKFLOW_SOP": "docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md",
        "BOOTSTRAP_SUMMARY": "docs/system/00_governance/bootstrap/{job_id}-bootstrap-summary.md".format(job_id=job_id),
    }
    legacy = {
        "PROJECT_ANALYSIS": ["docs/system/00_governance/bootstrap/project_analysis.md"],
        "SYSTEM_DOCS_INDEX": ["docs/system/README.md"],
        "SYSTEM_DOCS_CHANGE_LOG": [
            "docs/system/00_governance/bootstrap/{job_id}-bootstrap-change-log.md".format(job_id=job_id)
        ],
        "SYSTEM_DOCS_VALIDATION": [
            "docs/system/00_governance/bootstrap/{job_id}-bootstrap-validation.md".format(job_id=job_id)
        ],
        "SYSTEM_DOC_STANDARD": ["docs/system/00_governance/DOCUMENTATION_STANDARD.md"],
        "BUNDLE_TAXONOMY": ["docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md"],
        "BUNDLE_MIGRATION_PLAN": ["docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md"],
        "SYSTEM_OVERVIEW": ["docs/system/01_overview/SYSTEM_OVERVIEW.md"],
        "BUSINESS_CAPABILITIES": ["docs/system/01_overview/BUSINESS_CAPABILITIES.md"],
        "FUNCTIONAL_SPEC": ["docs/system/02_functional/FUNCTIONAL_SPEC.md"],
        "NON_FUNCTIONAL_REQUIREMENTS": ["docs/system/02_functional/NON_FUNCTIONAL_REQUIREMENTS.md"],
        "SYSTEM_CONTEXT": ["docs/system/03_architecture/SYSTEM_CONTEXT.md"],
        "COMPONENT_ARCHITECTURE": ["docs/system/03_architecture/COMPONENT_ARCHITECTURE.md"],
        "DECISION_LOG": ["docs/system/03_architecture/DECISION_LOG.md"],
        "SYSTEM_FILE_STRUCTURE": ["docs/system/03_architecture/SYSTEM_FILE_STRUCTURE.md"],
        "DEVELOPER_GUIDE": ["docs/engineering/DEVELOPER_GUIDE.md"],
        "RUNBOOK": ["docs/operations/RUNBOOK.md"],
        "EXISTING_REPO_WORKFLOW_SOP": ["docs/operations/EXISTING_REPO_WORKFLOW_SOP.md"],
        "BOOTSTRAP_SUMMARY": ["docs/system/00_governance/bootstrap/{job_id}-bootstrap-summary.md".format(job_id=job_id)],
    }
    return {
        key: [canonical[key], *legacy.get(key, [])]
        for key in canonical
    }


def execution_scaffold_doc_paths() -> list[str]:
    return [
        "docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md",
        "docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md",
        "docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md",
        "docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md",
        "docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md",
        "docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md",
        "docs/system/00_governance/bootstrap/templates/delivery/02_delivery_initiative_template.md",
        "docs/system/00_governance/bootstrap/templates/delivery/03_delivery_plan_template.md",
        "docs/system/00_governance/bootstrap/templates/delivery/04_delivery_task_graph_template.md",
        "docs/system/00_governance/bootstrap/templates/delivery/05_delivery_task_template.md",
        "docs/system/00_governance/bootstrap/templates/delivery/06_delivery_impl_template.md",
        "docs/system/00_governance/bootstrap/templates/delivery/07_delivery_review_template.md",
        "docs/system/00_governance/bootstrap/templates/delivery/08_delivery_validation_template.md",
        "docs/system/00_governance/bootstrap/templates/delivery/09_delivery_memory_template.md",
        "docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md",
        "docs/system/00_governance/bootstrap/templates/codebase/02_codebase_inventory_template.md",
        "docs/system/00_governance/bootstrap/templates/codebase/03_codebase_module_template.md",
        "docs/system/00_governance/bootstrap/templates/codebase/04_codebase_component_template.md",
        "docs/system/00_governance/bootstrap/templates/codebase/05_codebase_change_template.md",
        "docs/codebase/01_inventory/codebase_inventory.md",
        "docs/delivery/00_standards/DELIVERY_AGENTS_MD.md",
        "docs/delivery/00_standards/DELIVERY_AGENT_PLANNER.md",
        "docs/delivery/00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md",
        "docs/delivery/00_standards/DELIVERY_AGENT_IMPL_PLANNER.md",
        "docs/delivery/00_standards/DELIVERY_AGENT_EXECUTOR.md",
        "docs/delivery/00_standards/DELIVERY_AGENT_REVIEWER.md",
        "docs/delivery/00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md",
        "docs/delivery/DELIVERY_FOLDER_MAP.json",
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
