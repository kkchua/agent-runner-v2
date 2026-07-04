#!/usr/bin/env python3
"""
actions/validate_delivery_docs.py — Deterministic validation of scaffolded delivery docs.

Validates folder structure, template completeness, template structure, SOP validity,
status rules validity, agent registry consistency, and cross-reference integrity.

Outputs DELIVERY_FOLDER_MAP — a JSON manifest of what was validated.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ..action_result import ActionResult
from ..doc_paths import codebase_doc_rel, delivery_doc_rel, system_doc_rel
from ..runtime_context import write_meta_sidecar
from .documentation_validation_core import DocumentationValidationPlan, validate_documentation_plan

logger = logging.getLogger(__name__)

# --- Constants ---

DELIVERY_FOLDERS = [
    delivery_doc_rel("01_initiatives"),
    delivery_doc_rel("02_plans"),
    delivery_doc_rel("03_tasks"),
    delivery_doc_rel("04_implementation_plans"),
    delivery_doc_rel("05_reviews"),
    delivery_doc_rel("06_memory"),
    codebase_doc_rel("00_standards"),
    codebase_doc_rel("00_templates"),
    codebase_doc_rel("01_inventory"),
    codebase_doc_rel("02_modules"),
    codebase_doc_rel("03_components"),
    codebase_doc_rel("04_changes"),
    codebase_doc_rel("05_archives"),
    system_doc_rel(),
    system_doc_rel("templates"),
]

DELIVERY_TEMPLATE_ROOT = Path(system_doc_rel("templates/delivery"))
CODEBASE_TEMPLATE_ROOT = Path(system_doc_rel("templates/codebase"))
DELIVERY_AGENT_ROOT = Path(delivery_doc_rel("00_standards"))

REQUIRED_TEMPLATES = {
    "DELIVERY_TEMPLATE_REGISTRY": "01_delivery_template_registry.md",
    "DELIVERY_INITIATIVE_TEMPLATE": "02_delivery_initiative_template.md",
    "DELIVERY_PLAN_TEMPLATE": "03_delivery_plan_template.md",
    "DELIVERY_TASK_GRAPH_TEMPLATE": "04_delivery_task_graph_template.md",
    "DELIVERY_TASK_TEMPLATE": "05_delivery_task_template.md",
    "DELIVERY_IMPL_TEMPLATE": "06_delivery_impl_template.md",
    "DELIVERY_REVIEW_TEMPLATE": "07_delivery_review_template.md",
    "DELIVERY_VALIDATION_TEMPLATE": "08_delivery_validation_template.md",
    "DELIVERY_MEMORY_TEMPLATE": "09_delivery_memory_template.md",
}

REQUIRED_CODEBASE_FILES = {
    "CODEBASE_DOC_SOP": codebase_doc_rel("00_standards/CODEBASE_DOC_SOP_v1.md"),
    "CODEBASE_DOC_STATUS_RULES": codebase_doc_rel("00_standards/CODEBASE_DOC_STATUS_RULES_v1.md"),
    "CODEBASE_TEMPLATE_REGISTRY": system_doc_rel("templates/codebase/01_codebase_template_registry.md"),
    "CODEBASE_INVENTORY_TEMPLATE": system_doc_rel("templates/codebase/02_codebase_inventory_template.md"),
    "CODEBASE_MODULE_TEMPLATE": system_doc_rel("templates/codebase/03_codebase_module_template.md"),
    "CODEBASE_COMPONENT_TEMPLATE": system_doc_rel("templates/codebase/04_codebase_component_template.md"),
    "CODEBASE_CHANGE_TEMPLATE": system_doc_rel("templates/codebase/05_codebase_change_template.md"),
    "CODEBASE_INVENTORY": codebase_doc_rel("01_inventory/codebase_inventory.md"),
}

REQUIRED_SYSTEM_FILES = {
    "PROJECT_ANALYSIS": system_doc_rel("project_analysis.md"),
    "SYSTEM_DOC_STANDARD": system_doc_rel("DOCUMENTATION_STANDARD.md"),
    "SYSTEM_DOCS_INDEX": system_doc_rel("README.md"),
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
}


def _delivery_template_paths() -> dict[str, str]:
    return {
        artifact_key: str(DELIVERY_TEMPLATE_ROOT / filename)
        for artifact_key, filename in REQUIRED_TEMPLATES.items()
    }

# Minimum required sections per template type (all must be present)
TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    "01_delivery_template_registry.md": [
        "Metadata", "Registry Overview", "Template Families",
        "Usage Rules", "Cross-References",
    ],
    "02_delivery_initiative_template.md": [
        "Metadata", "Initiative Description", "Scope",
        "Documentation Scope", "Dependencies", "Acceptance Criteria", "Notes",
    ],
    "03_delivery_plan_template.md": [
        "Metadata", "Plan Objective", "Strategy Overview",
        "Scope Mapping", "Task Breakdown", "Documentation Strategy",
        "Risks", "Deliverables", "Acceptance Criteria", "Notes",
    ],
    "04_delivery_task_graph_template.md": [
        "Metadata", "Task Graph Objective", "Task Graph",
        "Execution Flow", "Documentation Workstream", "Success Criteria", "Notes",
    ],
    "05_delivery_task_template.md": [
        "Metadata", "Objective", "Inputs", "Outputs",
        "Execution Steps", "Validation Criteria", "Documentation Impact",
        "Dependencies", "Notes",
    ],
    "06_delivery_impl_template.md": [
        "Metadata", "Implementation Objective", "Changes Overview",
        "Implementation Steps", "Documentation Update Plan", "Risk Assessment",
        "Validation Criteria", "Notes",
    ],
    "07_delivery_review_template.md": [
        "Metadata", "Review Scope", "Findings",
        "Documentation Compliance", "Verdict", "Notes",
    ],
    "08_delivery_validation_template.md": [
        "Metadata", "Validation Scope", "Code Validation",
        "Documentation Synchronization Validation", "Validation Issues", "Validation Summary", "Verdict", "Approval", "Notes",
    ],
    "09_delivery_memory_template.md": [
        "Metadata", "Context", "Lessons Learned",
        "Reusable Patterns", "Anti-Patterns", "Documentation Notes",
        "Related Memories", "Notes",
    ],
}

CODEBASE_TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    "01_codebase_template_registry.md": [
        "Metadata", "Registry Overview", "Template Families",
        "Usage Rules", "Cross-References",
    ],
    "02_codebase_inventory_template.md": [
        "Metadata", "Template Fields", "Entry Template", "Status Definitions", "File Type Coverage",
    ],
    "03_codebase_module_template.md": [
        "Metadata", "Module Overview", "File Inventory", "Architecture",
        "Key Components", "Public API", "Dependencies", "Testing",
        "Change Log", "Notes",
    ],
    "04_codebase_component_template.md": [
        "Metadata", "Component Overview", "File Coverage", "Interface",
        "Implementation Details", "Dependencies", "Testing", "Change Log", "Notes",
    ],
    "05_codebase_change_template.md": [
        "Metadata", "Change Summary", "Changed Files", "Documentation Updates",
        "Stale Documentation Removal", "Documentation Freshness Verification",
        "Cross-References", "Notes",
    ],
}

SOP_REQUIRED_SECTIONS = [
    "Purpose", "Core Principle", "Authority Precedence",
    "Workflow State Machine", "Agent Roles", "Workflow Phases",
    "Standard Rules", "Folder Structure", "Validation",
]

STATUS_RULES_REQUIRED_SECTIONS = [
    "Core Principles", "Global Workflow Discipline",
    "Lifecycle Rules", "Authority Model", "Approval Gates",
    "Forbidden Transitions", "Document-First", "Traceability",
]

CODEBASE_SOP_REQUIRED_SECTIONS = [
    "Purpose", "Coverage Model", "Documentation Modes", "Freshness Rules",
    "Stale Content Policy", "Workflow Integration", "File-Type Rules", "Validation",
]

CODEBASE_STATUS_RULES_REQUIRED_SECTIONS = [
    "Core Principles", "Inventory Status Model", "Document Status Model",
    "Supersession Rules", "Update Triggers", "Traceability", "Removal Rules",
]

SYSTEM_DOC_REQUIRED_SECTIONS: dict[str, list[str]] = {
    system_doc_rel("project_analysis.md"): [
        "Repo Overview",
        "Codebase Structure",
        "Operational Risks",
        "Architectural Observations",
        "Architecture Posture",
    ],
    system_doc_rel("DOCUMENTATION_STANDARD.md"): [
        "Purpose", "Audience Model", "Document Set", "Update Triggers", "Validation",
        "Architecture Baseline", "Repo-Selected Profile", "Migration Mode", "Conditional Standards",
    ],
    system_doc_rel("README.md"): [
        "System Documentation Index", "Audience Views", "Document Map",
    ],
    system_doc_rel("SYSTEM_OVERVIEW.md"): [
        "Purpose", "Scope", "Primary Flows", "Key Risks", "Architecture Profile",
    ],
    system_doc_rel("SYSTEM_FILE_STRUCTURE.md"): [
        "Repository Structure", "Top-Level Directories", "Documentation Locations",
    ],
    system_doc_rel("DEVELOPER_GUIDE.md"): [
        "Development Workflow", "Key Commands", "Documentation Responsibilities", "Architecture Posture",
    ],
    system_doc_rel("RUNBOOK.md"): [
        "Operations Scope", "Routine Procedures", "Failure Handling",
    ],
    system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"): [
        "Purpose", "First-Time Setup", "Normal Governed Delivery",
        "Drift Reconciliation", "Governance Refresh", "Batch Files", "Notes",
    ],
}

AGENT_REGISTRY_ENTRY_PATTERN = re.compile(r"\|[\s-]*(\w[\w\s-]+)\s*\|[\s-]*(\w[\w\s-]+)\s*\|", re.MULTILINE)


def _check_file_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    """Check if a file exists relative to project root. Returns (ok, detail)."""
    full = project_root / rel_path
    if full.exists() and full.is_file():
        return True, f"exists ({full.stat().st_size} bytes)"
    return False, f"missing at {rel_path}"


def _check_folder_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    """Check if a folder exists relative to project root."""
    full = project_root / rel_path
    if full.exists() and full.is_dir():
        count = len(list(full.iterdir()))
        return True, f"exists ({count} items)"
    return False, f"missing at {rel_path}"


def _has_section(content: str, section: str) -> bool:
    """Check if a markdown file contains a section heading (case-insensitive)."""
    # Match ## or ### headings
    pattern = re.compile(rf"^#+\s+.*{re.escape(section)}", re.MULTILINE | re.IGNORECASE)
    return bool(pattern.search(content))


def _has_metadata_field(content: str, field: str) -> bool:
    """Check if metadata block contains a field."""
    pattern = re.compile(rf"^\s*-?\s*{re.escape(field)}\s*[:：]", re.MULTILINE)
    return bool(pattern.search(content))


def _read_file(project_root: Path, rel_path: str) -> str | None:
    """Read a file, return None if missing."""
    full = project_root / rel_path
    if full.exists() and full.is_file():
        return full.read_text(encoding="utf-8")
    return None


def _validate_folder_structure(project_root: Path) -> list[dict[str, Any]]:
    """Validate all required delivery folders exist."""
    results = []
    for folder in DELIVERY_FOLDERS:
        ok, detail = _check_folder_exists(project_root, folder)
        results.append({
            "check": "folder_structure",
            "path": folder,
            "ok": ok,
            "detail": detail,
        })
    return results


def _validate_templates(project_root: Path) -> list[dict[str, Any]]:
    """Validate all required template files exist and have required sections."""
    results = []
    templates_dir = project_root / DELIVERY_TEMPLATE_ROOT

    for artifact_key, filename in REQUIRED_TEMPLATES.items():
        # Check file exists
        file_path = templates_dir / filename
        ok, detail = _check_file_exists(project_root, str(file_path.relative_to(project_root)))
        results.append({
            "check": "template_exists",
            "artifact_key": artifact_key,
            "path": str(file_path.relative_to(project_root)),
            "ok": ok,
            "detail": detail,
        })

        if not ok:
            continue

        # Check content
        content = _read_file(project_root, str(file_path.relative_to(project_root)))
        if content is None:
            continue

        # Accept both legacy inline metadata and current YAML-frontmatter templates.
        has_doc_type = (
            _has_metadata_field(content, "Doc Type")
            or _has_metadata_field(content, "doc_type")
            or _has_metadata_field(content, "document_type")
            or _has_metadata_field(content, "template_id")
        )
        has_version = (
            _has_metadata_field(content, "Template Version")
            or _has_metadata_field(content, "template_version")
            or _has_metadata_field(content, "version")
            or _has_metadata_field(content, "generated")
        )
        results.append({
            "check": "template_metadata",
            "path": str(file_path.relative_to(project_root)),
            "ok": has_doc_type and has_version,
            "detail": f"Template identity: {'present' if has_doc_type else 'missing'}, Template version marker: {'present' if has_version else 'missing'}",
        })

        # Check required sections
        required = TEMPLATE_SECTION_REQUIREMENTS.get(filename, [])
        for section in required:
            has = _has_section(content, section)
            results.append({
                "check": "template_section",
                "path": str(file_path.relative_to(project_root)),
                "section": section,
                "ok": has,
                "detail": f"{'found' if has else 'missing'}",
            })

    return results


def _validate_codebase_docs(project_root: Path) -> list[dict[str, Any]]:
    """Validate scaffolded codebase documentation standards, templates, and inventory."""
    results = []

    for artifact_key, rel_path in REQUIRED_CODEBASE_FILES.items():
        ok, detail = _check_file_exists(project_root, rel_path)
        results.append({
            "check": "codebase_file_exists",
            "artifact_key": artifact_key,
            "path": rel_path,
            "ok": ok,
            "detail": detail,
        })
        if not ok:
            continue

        content = _read_file(project_root, rel_path)
        if content is None:
            continue

        filename = Path(rel_path).name
        required_sections = CODEBASE_TEMPLATE_SECTION_REQUIREMENTS.get(filename, [])
        for section in required_sections:
            has = _has_section(content, section)
            results.append({
                "check": "codebase_template_section",
                "path": rel_path,
                "section": section,
                "ok": has,
                "detail": f"{'found' if has else 'missing'}",
            })

    sop_path = REQUIRED_CODEBASE_FILES["CODEBASE_DOC_SOP"]
    sop_content = _read_file(project_root, sop_path)
    if sop_content is not None:
        for section in CODEBASE_SOP_REQUIRED_SECTIONS:
            has = _has_section(sop_content, section)
            results.append({
                "check": "codebase_sop_section",
                "path": sop_path,
                "section": section,
                "ok": has,
                "detail": f"{'found' if has else 'missing'}",
            })

    rules_path = REQUIRED_CODEBASE_FILES["CODEBASE_DOC_STATUS_RULES"]
    rules_content = _read_file(project_root, rules_path)
    if rules_content is not None:
        for section in CODEBASE_STATUS_RULES_REQUIRED_SECTIONS:
            has = _has_section(rules_content, section)
            results.append({
                "check": "codebase_status_section",
                "path": rules_path,
                "section": section,
                "ok": has,
                "detail": f"{'found' if has else 'missing'}",
            })

    inventory_path = REQUIRED_CODEBASE_FILES["CODEBASE_INVENTORY"]
    inventory_content = _read_file(project_root, inventory_path)
    if inventory_content is not None:
        inventory_checks = {
            "has_current_status": "`current`" in inventory_content or "current" in inventory_content.lower(),
            "has_needs_update_status": "`needs_update`" in inventory_content or "needs_update" in inventory_content.lower(),
            "has_doc_mode": "documentation mode" in inventory_content.lower(),
            "has_owner_doc_path": "owner doc path" in inventory_content.lower(),
            "has_last_verified_by_change": "last verified by change" in inventory_content.lower(),
        }
        for check_name, ok in inventory_checks.items():
            results.append({
                "check": f"codebase_inventory_{check_name}",
                "path": inventory_path,
                "ok": ok,
                "detail": "present" if ok else "missing",
            })

    deprecated_dir = project_root / delivery_doc_rel("07_master_prompts")
    results.append({
        "check": "deprecated_master_prompts_absent",
        "path": delivery_doc_rel("07_master_prompts"),
        "ok": not deprecated_dir.exists(),
        "detail": "absent as expected" if not deprecated_dir.exists() else "deprecated folder still exists",
    })

    return results


def _validate_system_docs(project_root: Path) -> list[dict[str, Any]]:
    """Validate scaffolded system documentation standards and core documents."""
    results = []

    for artifact_key, rel_path in REQUIRED_SYSTEM_FILES.items():
        ok, detail = _check_file_exists(project_root, rel_path)
        results.append({
            "check": "system_file_exists",
            "artifact_key": artifact_key,
            "path": rel_path,
            "ok": ok,
            "detail": detail,
        })
        if not ok:
            continue

        content = _read_file(project_root, rel_path)
        if content is None:
            continue

        for section in SYSTEM_DOC_REQUIRED_SECTIONS.get(rel_path, []):
            has = _has_section(content, section)
            results.append({
                "check": "system_doc_section",
                "path": rel_path,
                "section": section,
                "ok": has,
                "detail": f"{'found' if has else 'missing'}",
            })

    return results


def _validate_sop(project_root: Path) -> list[dict[str, Any]]:
    """Validate WORKFLOW_SOP_v1.md structure."""
    results = []
    sop_path = system_doc_rel("WORKFLOW_SOP_v1.md")

    ok, detail = _check_file_exists(project_root, sop_path)
    results.append({
        "check": "sop_exists",
        "path": sop_path,
        "ok": ok,
        "detail": detail,
    })

    if not ok:
        return results

    content = _read_file(project_root, sop_path)
    if content is None:
        return results

    for section in SOP_REQUIRED_SECTIONS:
        has = _has_section(content, section)
        results.append({
            "check": "sop_section",
            "path": sop_path,
            "section": section,
            "ok": has,
            "detail": f"{'found' if has else 'missing'}",
        })

    # Check state machine exists (arrow notation — allow backtick-wrapped state names)
    has_state_machine = bool(re.search(r"→", content))
    results.append({
        "check": "sop_state_machine",
        "path": sop_path,
        "ok": has_state_machine,
        "detail": "state machine notation found" if has_state_machine else "state machine arrows not found",
    })

    return results


def _validate_status_rules(project_root: Path) -> list[dict[str, Any]]:
    """Validate DELIVERY_STATUS_RULES_v1.md structure."""
    results = []
    rules_path = system_doc_rel("DELIVERY_STATUS_RULES_v1.md")
    ok, detail = _check_file_exists(project_root, rules_path)
    if ok:
        content = _read_file(project_root, rules_path)
        if content is None:
            return results

        results.append({
            "check": "status_rules_exists",
            "path": rules_path,
            "ok": True,
            "detail": detail,
        })

        for section in STATUS_RULES_REQUIRED_SECTIONS:
            has = _has_section(content, section)
            results.append({
                "check": "status_rules_section",
                "path": rules_path,
                "section": section,
                "ok": has,
                "detail": f"{'found' if has else 'missing'}",
            })

        # Check forbidden transitions exist
        has_forbidden = bool(re.search(r"forbidden|must not|invalid", content, re.IGNORECASE))
        results.append({
            "check": "status_rules_forbidden_transitions",
            "path": rules_path,
            "ok": has_forbidden,
            "detail": "forbidden transition rules found" if has_forbidden else "no forbidden transition rules found",
        })

        return results

    # Status rules not found in canonical location
    results.append({
        "check": "status_rules_exists",
        "path": rules_path,
        "ok": False,
        "detail": "not found in 00_templates/",
    })
    return results


def _validate_agents(project_root: Path) -> list[dict[str, Any]]:
    """Validate delivery agent registry consistency with individual agent contracts."""
    results = []
    agents_dir = project_root / DELIVERY_AGENT_ROOT
    agents_md_path = agents_dir / "DELIVERY_AGENTS_MD.md"

    # Check AGENTS.md exists
    ok, detail = _check_file_exists(project_root, str(agents_md_path.relative_to(project_root)))
    results.append({
        "check": "agents_registry_exists",
        "path": str(agents_md_path.relative_to(project_root)),
        "ok": ok,
        "detail": detail,
    })

    if not ok:
        return results

    content = _read_file(project_root, str(agents_md_path.relative_to(project_root)))
    if content is None:
        return results

    # Extract agent names from registry table
    # Pattern: | AgentName | role | ...
    agent_names = set()
    for line in content.splitlines():
        if line.strip().startswith("|") and "role" not in line.lower():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and parts[1]:
                name = parts[1].strip()
                if name and name not in ("Agent", "Role", "---"):
                    agent_names.add(name)

    results.append({
        "check": "agents_registry_entries",
        "path": str(agents_md_path.relative_to(project_root)),
        "ok": len(agent_names) > 0,
        "detail": f"found {len(agent_names)} agent(s) in registry: {', '.join(sorted(agent_names))}",
    })

    # Check individual agent contracts exist
    known_agent_files = [
        "DELIVERY_AGENT_PLANNER.md",
        "DELIVERY_AGENT_TASK_DECOMPOSER.md",
        "DELIVERY_AGENT_IMPL_PLANNER.md",
        "DELIVERY_AGENT_EXECUTOR.md",
        "DELIVERY_AGENT_REVIEWER.md",
        "DELIVERY_AGENT_MEMORY_MANAGER.md",
    ]

    for agent_file in known_agent_files:
        agent_path = agents_dir / agent_file
        rel = str(agent_path.relative_to(project_root))
        ok, detail = _check_file_exists(project_root, rel)
        results.append({
            "check": "agent_contract_exists",
            "path": rel,
            "ok": ok,
            "detail": detail,
        })

        if ok:
            agent_content = _read_file(project_root, rel)
            if agent_content:
                has_doc_type = (
                    _has_metadata_field(agent_content, "doc_type")
                    or _has_metadata_field(agent_content, "document_type")
                    or _has_metadata_field(agent_content, "Doc Type")
                )
                has_agent_id = (
                    _has_metadata_field(agent_content, "agent_id")
                    or _has_metadata_field(agent_content, "Agent ID")
                )
                results.append({
                    "check": "agent_contract_metadata",
                    "path": rel,
                    "ok": has_doc_type and has_agent_id,
                    "detail": f"Agent contract marker: {'present' if has_doc_type else 'missing'}, Agent identifier: {'present' if has_agent_id else 'missing'}",
                })

    return results


def _validate_cross_references(project_root: Path) -> list[dict[str, Any]]:
    """Validate that templates reference each other correctly."""
    results = []
    templates_dir = project_root / DELIVERY_TEMPLATE_ROOT

    # Plan template should reference initiative template
    plan_path = templates_dir / "03_delivery_plan_template.md"
    if plan_path.exists():
        content = plan_path.read_text(encoding="utf-8")
        refs_initiative = "initiative" in content.lower() or "DELIVERY_INITIATIVE_TEMPLATE" in content
        results.append({
            "check": "cross_ref_plan_initiative",
            "path": str(plan_path.relative_to(project_root)),
            "ok": refs_initiative,
            "detail": "plan references initiative" if refs_initiative else "plan does not reference initiative",
        })
        docs_strategy_present = "documentation strategy" in content.lower()
        results.append({
            "check": "cross_ref_plan_doc_strategy",
            "path": str(plan_path.relative_to(project_root)),
            "ok": docs_strategy_present,
            "detail": "plan includes documentation strategy" if docs_strategy_present else "plan missing documentation strategy",
        })

    # Task template should reference plan
    task_path = templates_dir / "05_delivery_task_template.md"
    if task_path.exists():
        content = task_path.read_text(encoding="utf-8")
        refs_plan = "plan" in content.lower() or "DELIVERY_PLAN_TEMPLATE" in content
        results.append({
            "check": "cross_ref_task_plan",
            "path": str(task_path.relative_to(project_root)),
            "ok": refs_plan,
            "detail": "task references plan" if refs_plan else "task does not reference plan",
        })
        docs_impact_present = "documentation impact" in content.lower() or "documentation obligations" in content.lower()
        results.append({
            "check": "cross_ref_task_doc_impact",
            "path": str(task_path.relative_to(project_root)),
            "ok": docs_impact_present,
            "detail": "task includes documentation impact" if docs_impact_present else "task missing documentation impact section",
        })

    validation_path = templates_dir / "08_delivery_validation_template.md"
    if validation_path.exists():
        content = validation_path.read_text(encoding="utf-8")
        doc_sync_present = "documentation synchronization" in content.lower() or "documentation sync" in content.lower()
        results.append({
            "check": "cross_ref_validation_doc_sync",
            "path": str(validation_path.relative_to(project_root)),
            "ok": doc_sync_present,
            "detail": "validation includes documentation sync" if doc_sync_present else "validation missing documentation sync section",
        })

    # Template registry should list all templates
    registry_path = templates_dir / "01_delivery_template_registry.md"
    if registry_path.exists():
        content = registry_path.read_text(encoding="utf-8")
        expected_types = [
            "DELIVERY_INITIATIVE_TEMPLATE",
            "DELIVERY_PLAN_TEMPLATE",
            "DELIVERY_TASK_GRAPH_TEMPLATE",
            "DELIVERY_TASK_TEMPLATE",
            "DELIVERY_IMPL_TEMPLATE",
            "DELIVERY_REVIEW_TEMPLATE",
            "DELIVERY_VALIDATION_TEMPLATE",
            "DELIVERY_MEMORY_TEMPLATE",
        ]
        missing_types = [t for t in expected_types if t not in content]
        results.append({
            "check": "cross_ref_registry_completeness",
            "path": str(registry_path.relative_to(project_root)),
            "ok": len(missing_types) == 0,
            "detail": f"all types registered" if not missing_types else f"missing types: {', '.join(missing_types)}",
        })

    return results


def validate_delivery_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Validate the complete delivery documentation scaffold.

    Checks:
    1. Folder structure — all 8 delivery folders exist
    2. Template completeness — all 7 template files present
    3. Template structure — each template has required sections
    4. SOP validity — WORKFLOW_SOP_v1.md has required sections
    5. Status rules validity — DELIVERY_STATUS_RULES_v1.md has required sections
    6. Agent registry consistency — AGENTS.md matches individual contracts
    7. Cross-reference integrity — templates reference each other correctly

    Outputs DELIVERY_FOLDER_MAP — a JSON manifest of validation results.
    """
    logger.info("[validate_delivery_docs] starting validation")
    print("[validate_delivery_docs] starting delivery docs validation", flush=True)

    required_files = tuple(
        list(REQUIRED_CODEBASE_FILES.values())
        + list(REQUIRED_SYSTEM_FILES.values())
        + list(_delivery_template_paths().values())
        + [str(DELIVERY_AGENT_ROOT / name) for name in [
            "DELIVERY_AGENTS_MD.md",
            "DELIVERY_AGENT_PLANNER.md",
            "DELIVERY_AGENT_TASK_DECOMPOSER.md",
            "DELIVERY_AGENT_IMPL_PLANNER.md",
            "DELIVERY_AGENT_EXECUTOR.md",
            "DELIVERY_AGENT_REVIEWER.md",
            "DELIVERY_AGENT_MEMORY_MANAGER.md",
        ]]
        + [
            system_doc_rel("WORKFLOW_SOP_v1.md"),
            system_doc_rel("DELIVERY_STATUS_RULES_v1.md"),
        ]
    )

    section_requirements = dict(SYSTEM_DOC_REQUIRED_SECTIONS)
    section_requirements.update({path: sections for path, sections in {
        str(DELIVERY_TEMPLATE_ROOT / name): sections
        for name, sections in TEMPLATE_SECTION_REQUIREMENTS.items()
    }.items()})
    section_requirements.update({system_doc_rel(f"templates/codebase/{name}"): sections for name, sections in CODEBASE_TEMPLATE_SECTION_REQUIREMENTS.items()})
    section_requirements[system_doc_rel("WORKFLOW_SOP_v1.md")] = SOP_REQUIRED_SECTIONS
    section_requirements[system_doc_rel("DELIVERY_STATUS_RULES_v1.md")] = STATUS_RULES_REQUIRED_SECTIONS
    section_requirements[codebase_doc_rel("00_standards/CODEBASE_DOC_SOP_v1.md")] = CODEBASE_SOP_REQUIRED_SECTIONS
    section_requirements[codebase_doc_rel("00_standards/CODEBASE_DOC_STATUS_RULES_v1.md")] = CODEBASE_STATUS_RULES_REQUIRED_SECTIONS

    plan = DocumentationValidationPlan(
        required_folders=tuple(DELIVERY_FOLDERS),
        required_files=required_files,
        section_requirements={path: tuple(sections) for path, sections in section_requirements.items()},
        extra_checkers=(
            _validate_codebase_docs,
            _validate_system_docs,
            _validate_sop,
            _validate_status_rules,
            _validate_agents,
            _validate_cross_references,
        ),
    )

    print("[validate_delivery_docs] checking shared validation plan...", flush=True)
    all_checks = validate_documentation_plan(project_root=project_root, plan=plan)

    # Summary
    total = len(all_checks)
    passed = sum(1 for c in all_checks if c["ok"])
    failed = total - passed

    # Write folder map manifest
    folder_map = {
        "schema_version": "v2",
        "validated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "delivery_root": delivery_doc_rel(),
        "summary": {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        },
        "checks": all_checks,
    }

    # Resolve output paths from runner-injected context so the sidecar lands where
    # the runner expects it (determined by DELIVERY_FOLDER_MAP_METAJSON in context).
    folder_map_rel = (
        context.get("DELIVERY_FOLDER_MAP")
        or context.get("DELIVERY_FOLDER_MAP_PATH")
        or delivery_doc_rel("DELIVERY_FOLDER_MAP.json")
    )
    meta_json_rel = context.get("DELIVERY_FOLDER_MAP_METAJSON", "")

    # Write the folder map file
    folder_map_path = project_root / folder_map_rel
    folder_map_path.parent.mkdir(parents=True, exist_ok=True)
    folder_map_path.write_text(
        json.dumps(folder_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Write meta.json sidecar to the runner-expected path
    if meta_json_rel:
        meta_path = meta_json_rel
    else:
        p = Path(folder_map_rel)
        meta_path = str(p.parent / f"{p.stem}.meta.json")
    write_meta_sidecar(
        meta_path,
        project_root=project_root,
        status="APPROVED" if failed == 0 else "REJECTED",
        remark=f"Validation: {passed}/{total} checks passed ({failed} failed)",
        artifacts={
            "DELIVERY_FOLDER_MAP": str(folder_map_path.relative_to(project_root)),
        },
    )

    # Print summary
    print(f"[validate_delivery_docs] {passed}/{total} checks passed ({failed} failed)", flush=True)
    if failed > 0:
        failed_checks = [c for c in all_checks if not c["ok"]]
        for fc in failed_checks:
            print(f"  ✗ [{fc.get('check', '?')}] {fc.get('path', '')}: {fc.get('detail', '')}", flush=True)

    overall_status = "APPROVED" if failed == 0 else "REJECTED"
    remark = f"Validation: {passed}/{total} checks passed"
    if failed > 0:
        remark += f" ({failed} failed)"

    artifacts = {}
    if overall_status == "APPROVED":
        artifacts["DELIVERY_FOLDER_MAP"] = str(folder_map_path.relative_to(project_root))

    logger.info(
        "[validate_delivery_docs] validation complete: status=%s passed=%d/%d",
        overall_status, passed, total,
    )

    return ActionResult(
        status=overall_status,
        remark=remark,
        artifacts=artifacts,
        reject_code="DELIVERY_VALIDATION_FAILED" if failed > 0 else None,
    )
