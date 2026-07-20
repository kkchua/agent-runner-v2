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
from ..constants import (
    # Artifact paths
    ARTIFACT_PATH_DELIVERY_AGENTS,
    ARTIFACT_PATH_DELIVERY_AGENT_PLANNER,
    ARTIFACT_PATH_DELIVERY_AGENT_TASK_DECOMPOSER,
    ARTIFACT_PATH_DELIVERY_AGENT_IMPL_PLANNER,
    ARTIFACT_PATH_DELIVERY_AGENT_EXECUTOR,
    ARTIFACT_PATH_DELIVERY_AGENT_REVIEWER,
    ARTIFACT_PATH_DELIVERY_AGENT_MEMORY_MANAGER,
    ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY,
    ARTIFACT_PATH_DELIVERY_INITIATIVE_TEMPLATE,
    ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE,
    ARTIFACT_PATH_DELIVERY_TASK_GRAPH_TEMPLATE,
    ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE,
    ARTIFACT_PATH_DELIVERY_IMPL_TEMPLATE,
    ARTIFACT_PATH_DELIVERY_REVIEW_TEMPLATE,
    ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE,
    ARTIFACT_PATH_DELIVERY_MEMORY_TEMPLATE,
    ARTIFACT_PATH_CODEBASE_DOC_SOP,
    ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES,
    ARTIFACT_PATH_CODEBASE_TEMPLATE_REGISTRY,
    ARTIFACT_PATH_CODEBASE_INVENTORY_TEMPLATE,
    ARTIFACT_PATH_CODEBASE_MODULE_TEMPLATE,
    ARTIFACT_PATH_CODEBASE_COMPONENT_TEMPLATE,
    ARTIFACT_PATH_CODEBASE_CHANGE_TEMPLATE,
    ARTIFACT_PATH_CODEBASE_INVENTORY,
    ARTIFACT_PATH_PROJECT_ANALYSIS,
    ARTIFACT_PATH_DOCUMENTATION_STANDARD,
    ARTIFACT_PATH_README,
    ARTIFACT_PATH_SYSTEM_OVERVIEW,
    ARTIFACT_PATH_BUSINESS_CAPABILITIES,
    ARTIFACT_PATH_FUNCTIONAL_SPEC,
    ARTIFACT_PATH_NON_FUNCTIONAL_REQUIREMENTS,
    ARTIFACT_PATH_SYSTEM_CONTEXT,
    ARTIFACT_PATH_COMPONENT_ARCHITECTURE,
    ARTIFACT_PATH_DECISION_LOG,
    ARTIFACT_PATH_SYSTEM_FILE_STRUCTURE,
    ARTIFACT_PATH_DEVELOPER_GUIDE,
    ARTIFACT_PATH_RUNBOOK,
    ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP,
    ARTIFACT_PATH_WORKFLOW_SOP,
    ARTIFACT_PATH_DELIVERY_STATUS_RULES,
    # Filename constants
    FILENAME_DELIVERY_TEMPLATE_REGISTRY,
    FILENAME_DELIVERY_INITIATIVE_TEMPLATE,
    FILENAME_DELIVERY_PLAN_TEMPLATE,
    FILENAME_DELIVERY_TASK_GRAPH_TEMPLATE,
    FILENAME_DELIVERY_TASK_TEMPLATE,
    FILENAME_DELIVERY_IMPL_TEMPLATE,
    FILENAME_DELIVERY_REVIEW_TEMPLATE,
    FILENAME_DELIVERY_VALIDATION_TEMPLATE,
    FILENAME_DELIVERY_MEMORY_TEMPLATE,
    EXT_MD,
    # Folder constants
    FOLDER_KEY_DELIVERY_STANDARDS,
    FOLDER_KEY_DELIVERY_INITIATIVES,
    FOLDER_KEY_DELIVERY_PLANS,
    FOLDER_KEY_DELIVERY_TASKS,
    FOLDER_KEY_DELIVERY_IMPLEMENTATIONS,
    FOLDER_KEY_DELIVERY_REVIEWS,
    FOLDER_KEY_DELIVERY_MEMORY,
    FOLDER_KEY_CODEBASE_STANDARDS,
    FOLDER_KEY_CODEBASE_INVENTORY,
    FOLDER_KEY_CODEBASE_MODULES,
    FOLDER_KEY_CODEBASE_COMPONENTS,
    FOLDER_KEY_CODEBASE_CHANGES,
    FOLDER_KEY_SYSTEM_BOOTSTRAP,
    FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT,
    FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT,
    # Section requirements
    SYSTEM_DOC_SECTION_REQUIREMENTS,
    CODEBASE_DOC_SECTION_REQUIREMENTS,
    DELIVERY_TEMPLATE_SECTION_REQUIREMENTS,
    CODEBASE_TEMPLATE_SECTION_REQUIREMENTS,
    SOP_AND_STATUS_RULES_REQUIREMENTS,
    DELIVERY_SOP_REQUIRED_SECTIONS,
    DELIVERY_STATUS_RULES_REQUIRED_SECTIONS,
    CODEBASE_SOP_REQUIRED_SECTIONS,
    CODEBASE_STATUS_RULES_REQUIRED_SECTIONS,
)
from ..doc_paths import codebase_doc_rel, delivery_doc_rel, system_doc_rel
from ..runtime_context import write_meta_sidecar
from .documentation_validation_core import DocumentationValidationPlan, validate_documentation_plan

logger = logging.getLogger(__name__)

# --- Constants ---

# Delivery and codebase folders to validate (using centralized constants)
DELIVERY_FOLDERS = [
    FOLDER_KEY_DELIVERY_INITIATIVES,
    FOLDER_KEY_DELIVERY_PLANS,
    FOLDER_KEY_DELIVERY_TASKS,
    FOLDER_KEY_DELIVERY_IMPLEMENTATIONS,
    FOLDER_KEY_DELIVERY_REVIEWS,
    FOLDER_KEY_DELIVERY_MEMORY,
    FOLDER_KEY_CODEBASE_STANDARDS,
    FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT,  # templates/codebase
    FOLDER_KEY_CODEBASE_INVENTORY,
    FOLDER_KEY_CODEBASE_MODULES,
    FOLDER_KEY_CODEBASE_COMPONENTS,
    FOLDER_KEY_CODEBASE_CHANGES,
    FOLDER_KEY_SYSTEM_BOOTSTRAP,  # system docs root
    FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT,  # templates/delivery
]

# Use centralized constants from constants.py for template and agent paths
REQUIRED_TEMPLATES = {
    "DELIVERY_TEMPLATE_REGISTRY": ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY,
    "DELIVERY_INITIATIVE_TEMPLATE": ARTIFACT_PATH_DELIVERY_INITIATIVE_TEMPLATE,
    "DELIVERY_PLAN_TEMPLATE": ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE,
    "DELIVERY_TASK_GRAPH_TEMPLATE": ARTIFACT_PATH_DELIVERY_TASK_GRAPH_TEMPLATE,
    "DELIVERY_TASK_TEMPLATE": ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE,
    "DELIVERY_IMPL_TEMPLATE": ARTIFACT_PATH_DELIVERY_IMPL_TEMPLATE,
    "DELIVERY_REVIEW_TEMPLATE": ARTIFACT_PATH_DELIVERY_REVIEW_TEMPLATE,
    "DELIVERY_VALIDATION_TEMPLATE": ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE,
    "DELIVERY_MEMORY_TEMPLATE": ARTIFACT_PATH_DELIVERY_MEMORY_TEMPLATE,
}

REQUIRED_CODEBASE_FILES = {
    "CODEBASE_DOC_SOP": ARTIFACT_PATH_CODEBASE_DOC_SOP,
    "CODEBASE_DOC_STATUS_RULES": ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES,
    "CODEBASE_TEMPLATE_REGISTRY": ARTIFACT_PATH_CODEBASE_TEMPLATE_REGISTRY,
    "CODEBASE_INVENTORY_TEMPLATE": ARTIFACT_PATH_CODEBASE_INVENTORY_TEMPLATE,
    "CODEBASE_MODULE_TEMPLATE": ARTIFACT_PATH_CODEBASE_MODULE_TEMPLATE,
    "CODEBASE_COMPONENT_TEMPLATE": ARTIFACT_PATH_CODEBASE_COMPONENT_TEMPLATE,
    "CODEBASE_CHANGE_TEMPLATE": ARTIFACT_PATH_CODEBASE_CHANGE_TEMPLATE,
    "CODEBASE_INVENTORY": ARTIFACT_PATH_CODEBASE_INVENTORY,
}

REQUIRED_SYSTEM_FILES = {
    "PROJECT_ANALYSIS": ARTIFACT_PATH_PROJECT_ANALYSIS,
    "SYSTEM_DOC_STANDARD": ARTIFACT_PATH_DOCUMENTATION_STANDARD,
    "SYSTEM_DOCS_INDEX": ARTIFACT_PATH_README,
    "SYSTEM_OVERVIEW": ARTIFACT_PATH_SYSTEM_OVERVIEW,
    "BUSINESS_CAPABILITIES": ARTIFACT_PATH_BUSINESS_CAPABILITIES,
    "FUNCTIONAL_SPEC": ARTIFACT_PATH_FUNCTIONAL_SPEC,
    "NON_FUNCTIONAL_REQUIREMENTS": ARTIFACT_PATH_NON_FUNCTIONAL_REQUIREMENTS,
    "SYSTEM_CONTEXT": ARTIFACT_PATH_SYSTEM_CONTEXT,
    "COMPONENT_ARCHITECTURE": ARTIFACT_PATH_COMPONENT_ARCHITECTURE,
    "DECISION_LOG": ARTIFACT_PATH_DECISION_LOG,
    "SYSTEM_FILE_STRUCTURE": ARTIFACT_PATH_SYSTEM_FILE_STRUCTURE,
    "DEVELOPER_GUIDE": ARTIFACT_PATH_DEVELOPER_GUIDE,
    "RUNBOOK": ARTIFACT_PATH_RUNBOOK,
    "EXISTING_REPO_WORKFLOW_SOP": ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP,
}

# Agent contract file paths (centralized constants)
AGENT_CONTRACT_PATHS = [
    ARTIFACT_PATH_DELIVERY_AGENTS,
    ARTIFACT_PATH_DELIVERY_AGENT_PLANNER,
    ARTIFACT_PATH_DELIVERY_AGENT_TASK_DECOMPOSER,
    ARTIFACT_PATH_DELIVERY_AGENT_IMPL_PLANNER,
    ARTIFACT_PATH_DELIVERY_AGENT_EXECUTOR,
    ARTIFACT_PATH_DELIVERY_AGENT_REVIEWER,
    ARTIFACT_PATH_DELIVERY_AGENT_MEMORY_MANAGER,
]


def _delivery_template_paths() -> dict[str, str]:
    """Return mapping of artifact keys to their centralized path constants."""
    return REQUIRED_TEMPLATES

# Minimum required sections per template type (all must be present)
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

    for artifact_key, file_path in REQUIRED_TEMPLATES.items():
        # Check file exists (file_path is already a full path from constants)
        ok, detail = _check_file_exists(project_root, file_path)
        results.append({
            "check": "template_exists",
            "artifact_key": artifact_key,
            "path": file_path,
            "ok": ok,
            "detail": detail,
        })

        if not ok:
            continue

        # Check content
        content = _read_file(project_root, file_path)
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
        required = DELIVERY_TEMPLATE_SECTION_REQUIREMENTS.get(filename, [])
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

        for section in SYSTEM_DOC_SECTION_REQUIREMENTS.get(rel_path, []):
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
    sop_path = ARTIFACT_PATH_WORKFLOW_SOP

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

    for section in DELIVERY_SOP_REQUIRED_SECTIONS:
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
    rules_path = ARTIFACT_PATH_DELIVERY_STATUS_RULES
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

        for section in DELIVERY_STATUS_RULES_REQUIRED_SECTIONS:
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

    # Use centralized constant for agents directory
    agents_dir = Path(FOLDER_KEY_DELIVERY_AGENTS)
    
    # Check AGENTS.md exists using centralized constant
    agents_md_path = ARTIFACT_PATH_DELIVERY_AGENTS
    ok, detail = _check_file_exists(project_root, agents_md_path)
    results.append({
        "check": "agents_registry_exists",
        "path": agents_md_path,
        "ok": ok,
        "detail": detail,
    })

    if not ok:
        return results

    content = _read_file(project_root, agents_md_path)
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
        "path": agents_md_path,
        "ok": len(agent_names) > 0,
        "detail": f"found {len(agent_names)} agent(s) in registry: {', '.join(sorted(agent_names))}",
    })

    # Check individual agent contracts exist using centralized constants
    for agent_path in AGENT_CONTRACT_PATHS[1:]:  # Skip first entry (DELIVERY_AGENTS itself)
        ok, detail = _check_file_exists(project_root, agent_path)
        results.append({
            "check": "agent_contract_exists",
            "path": agent_path,
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

    # Plan template should reference initiative template
    plan_path = ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE
    if Path(plan_path).exists():
        content = Path(plan_path).read_text(encoding="utf-8")
        refs_initiative = "initiative" in content.lower() or "DELIVERY_INITIATIVE_TEMPLATE" in content
        results.append({
            "check": "cross_ref_plan_initiative",
            "path": plan_path,
            "ok": refs_initiative,
            "detail": "plan references initiative" if refs_initiative else "plan does not reference initiative",
        })
        docs_strategy_present = "documentation strategy" in content.lower()
        results.append({
            "check": "cross_ref_plan_doc_strategy",
            "path": plan_path,
            "ok": docs_strategy_present,
            "detail": "plan includes documentation strategy" if docs_strategy_present else "plan missing documentation strategy",
        })

    # Task template should reference plan
    task_path = ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE
    if Path(task_path).exists():
        content = Path(task_path).read_text(encoding="utf-8")
        refs_plan = "plan" in content.lower() or "DELIVERY_PLAN_TEMPLATE" in content
        results.append({
            "check": "cross_ref_task_plan",
            "path": task_path,
            "ok": refs_plan,
            "detail": "task references plan" if refs_plan else "task does not reference plan",
        })
        docs_impact_present = "documentation impact" in content.lower() or "documentation obligations" in content.lower()
        results.append({
            "check": "cross_ref_task_doc_impact",
            "path": task_path,
            "ok": docs_impact_present,
            "detail": "task includes documentation impact" if docs_impact_present else "task missing documentation impact section",
        })

    validation_path = ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE
    if Path(validation_path).exists():
        content = Path(validation_path).read_text(encoding="utf-8")
        doc_sync_present = "documentation synchronization" in content.lower() or "documentation sync" in content.lower()
        results.append({
            "check": "cross_ref_validation_doc_sync",
            "path": validation_path,
            "ok": doc_sync_present,
            "detail": "validation includes documentation sync" if doc_sync_present else "validation missing documentation sync section",
        })

    # Template registry should list all templates
    registry_path = ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY
    if Path(registry_path).exists():
        content = Path(registry_path).read_text(encoding="utf-8")
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
            "path": registry_path,
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
        + AGENT_CONTRACT_PATHS  # Use centralized constants
        + [
            ARTIFACT_PATH_WORKFLOW_SOP,
            ARTIFACT_PATH_DELIVERY_STATUS_RULES,
        ]
    )

    # Build section requirements by merging centralized dictionaries
    section_requirements = {}
    section_requirements.update(SYSTEM_DOC_SECTION_REQUIREMENTS)
    section_requirements.update(CODEBASE_DOC_SECTION_REQUIREMENTS)
    section_requirements.update(DELIVERY_TEMPLATE_SECTION_REQUIREMENTS)
    section_requirements.update(CODEBASE_TEMPLATE_SECTION_REQUIREMENTS)
    section_requirements.update(SOP_AND_STATUS_RULES_REQUIREMENTS)

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
