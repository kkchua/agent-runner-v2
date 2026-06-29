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

logger = logging.getLogger(__name__)

# --- Constants ---

DELIVERY_FOLDERS = [
    "docs/delivery/00_templates",
    "docs/delivery/01_initiatives",
    "docs/delivery/02_plans",
    "docs/delivery/03_tasks",
    "docs/delivery/04_implementation_plans",
    "docs/delivery/05_reviews",
    "docs/delivery/06_memory",
    "docs/delivery/08_agents",
    "docs/codebase/00_standards",
    "docs/codebase/00_templates",
    "docs/codebase/01_inventory",
    "docs/codebase/02_modules",
    "docs/codebase/03_components",
    "docs/codebase/04_changes",
    "docs/codebase/05_archives",
]

REQUIRED_TEMPLATES = {
    "DELIVERY_INITIATIVE_TEMPLATE": "01_initiative.template.md",
    "DELIVERY_PLAN_TEMPLATE": "02_plan.template.md",
    "DELIVERY_TASK_GRAPH_TEMPLATE": "02b_task_graph.template.md",
    "DELIVERY_TASK_TEMPLATE": "03_task.template.md",
    "DELIVERY_IMPL_TEMPLATE": "04_implementation_plan.template.md",
    "DELIVERY_REVIEW_TEMPLATE": "04_review.template.md",
    "DELIVERY_VALIDATION_TEMPLATE": "05_validation.template.md",
    "DELIVERY_MEMORY_TEMPLATE": "06_memory.template.md",
}

REQUIRED_CODEBASE_FILES = {
    "CODEBASE_DOC_SOP": "docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md",
    "CODEBASE_DOC_STATUS_RULES": "docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md",
    "CODEBASE_TEMPLATE_REGISTRY": "docs/codebase/00_templates/codebase_template_registry.md",
    "CODEBASE_INVENTORY_TEMPLATE": "docs/codebase/00_templates/01_codebase_inventory.template.md",
    "CODEBASE_MODULE_TEMPLATE": "docs/codebase/00_templates/02_module_doc.template.md",
    "CODEBASE_COMPONENT_TEMPLATE": "docs/codebase/00_templates/03_component_doc.template.md",
    "CODEBASE_CHANGE_TEMPLATE": "docs/codebase/00_templates/04_change_impact.template.md",
    "CODEBASE_INVENTORY": "docs/codebase/01_inventory/codebase_inventory.md",
}

# Minimum required sections per template type (all must be present)
TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    "01_initiative.template.md": [
        "Objective", "Scope", "Constraints",
        "Dependencies", "Documentation Scope", "Stale Guidance Risks",
        "Success Criteria", "Approval",
    ],
    "02_plan.template.md": [
        "Plan Objective", "Strategy Overview", "Task Breakdown",
        "Scope Mapping", "Documentation Strategy", "Documentation Freshness Risks",
        "Deliverables", "Risks", "Acceptance Criteria", "Approval",
    ],
    "02b_task_graph.template.md": [
        "Task Graph Objective", "Task Graph",
        "Execution Flow", "Documentation Workstream", "Success Criteria",
    ],
    "03_task.template.md": [
        "Objective", "Inputs", "Outputs",
        "Execution Steps", "Validation Criteria", "Documentation Impact",
    ],
    "04_implementation_plan.template.md": [
        "Objective", "Inputs", "Outputs",
        "Scope Clarification", "File Plan", "Test Plan", "Documentation Update Plan", "Constraints",
    ],
    "04_review.template.md": [
        "Review Objective", "Issues Identified",
        "Final Decision",
    ],
    "05_validation.template.md": [
        "Validation Objective", "Validation Checks", "Test Results", "Documentation Sync Results", "Final Decision",
    ],
    "06_memory.template.md": [
        "Purpose", "Key Decisions", "Important References",
    ],
}

CODEBASE_TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    "01_codebase_inventory.template.md": [
        "Inventory Objective", "Coverage Rules", "Entry Schema", "Status Model", "Freshness Triggers",
    ],
    "02_module_doc.template.md": [
        "Module Objective", "Responsibilities", "Key Files", "Interfaces", "Documentation Mode", "Change Risks",
    ],
    "03_component_doc.template.md": [
        "Component Objective", "Inputs", "Outputs", "Dependencies", "Documentation Mode", "Operational Notes",
    ],
    "04_change_impact.template.md": [
        "Change Objective", "Changed Files", "Documentation Updates", "Superseded Content", "Validation",
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
    templates_dir = project_root / "docs" / "delivery" / "00_templates"

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

        # Check metadata block
        has_doc_type = _has_metadata_field(content, "Doc Type")
        has_version = _has_metadata_field(content, "Template Version")
        results.append({
            "check": "template_metadata",
            "path": str(file_path.relative_to(project_root)),
            "ok": has_doc_type and has_version,
            "detail": f"Doc Type: {'present' if has_doc_type else 'missing'}, Template Version: {'present' if has_version else 'missing'}",
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
            "has_pending_review_status": "`pending_review`" in inventory_content or "pending_review" in inventory_content.lower(),
            "has_superseded_status": "`superseded`" in inventory_content or "superseded" in inventory_content.lower(),
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

    deprecated_dir = project_root / "docs" / "delivery" / "07_master_prompts"
    results.append({
        "check": "deprecated_master_prompts_absent",
        "path": "docs/delivery/07_master_prompts",
        "ok": not deprecated_dir.exists(),
        "detail": "absent as expected" if not deprecated_dir.exists() else "deprecated folder still exists",
    })

    return results


def _validate_sop(project_root: Path) -> list[dict[str, Any]]:
    """Validate WORKFLOW_SOP_v1.md structure."""
    results = []
    sop_path = "docs/delivery/00_templates/WORKFLOW_SOP_v1.md"

    ok, detail = _check_file_exists(project_root, sop_path)
    results.append({
        "check": "sop_exists",
        "path": sop_path,
        "ok": ok,
        "detail": detail,
    })

    if not ok:
        # Also check 08_agents/ as alternative location
        sop_path_alt = "docs/delivery/08_agents/WORKFLOW_SOP_v1.md"
        ok_alt, detail_alt = _check_file_exists(project_root, sop_path_alt)
        if ok_alt:
            sop_path = sop_path_alt
            ok = True
            detail = detail_alt
            results.append({
                "check": "sop_exists_alt",
                "path": sop_path_alt,
                "ok": True,
                "detail": f"found at alternate location",
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
    rules_path = "docs/delivery/00_templates/DELIVERY_STATUS_RULES_v1.md"
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
    """Validate AGENTS.md registry consistency with individual agent contracts."""
    results = []
    agents_dir = project_root / "docs" / "delivery" / "08_agents"
    agents_md_path = agents_dir / "AGENTS.md"

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
        "AGENT-planner.md",
        "AGENT-task-decomposer.md",
        "AGENT-implementation-planner.md",
        "AGENT-executor.md",
        "AGENT-reviewer.md",
        "AGENT-memory-manager.md",
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
                # Accept "doc_type:", "document_type:" (YAML frontmatter) or "Doc Type:" (inline)
                has_doc_type = (
                    _has_metadata_field(agent_content, "doc_type")
                    or _has_metadata_field(agent_content, "document_type")
                    or _has_metadata_field(agent_content, "Doc Type")
                )
                # Accept both "agent_id:" (YAML frontmatter) and "Agent ID:" (inline)
                has_agent_id = (
                    _has_metadata_field(agent_content, "agent_id")
                    or _has_metadata_field(agent_content, "Agent ID")
                )
                results.append({
                    "check": "agent_contract_metadata",
                    "path": rel,
                    "ok": has_doc_type and has_agent_id,
                    "detail": f"Doc Type: {'present' if has_doc_type else 'missing'}, Agent ID: {'present' if has_agent_id else 'missing'}",
                })

    return results


def _validate_cross_references(project_root: Path) -> list[dict[str, Any]]:
    """Validate that templates reference each other correctly."""
    results = []
    templates_dir = project_root / "docs" / "delivery" / "00_templates"

    # Plan template should reference initiative template
    plan_path = templates_dir / "02_plan.template.md"
    if plan_path.exists():
        content = plan_path.read_text(encoding="utf-8")
        refs_initiative = "initiative" in content.lower() or "INIT" in content
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
    task_path = templates_dir / "03_task.template.md"
    if task_path.exists():
        content = task_path.read_text(encoding="utf-8")
        refs_plan = "plan" in content.lower() or "PLAN" in content
        results.append({
            "check": "cross_ref_task_plan",
            "path": str(task_path.relative_to(project_root)),
            "ok": refs_plan,
            "detail": "task references plan" if refs_plan else "task does not reference plan",
        })
        docs_impact_present = "documentation impact" in content.lower()
        results.append({
            "check": "cross_ref_task_doc_impact",
            "path": str(task_path.relative_to(project_root)),
            "ok": docs_impact_present,
            "detail": "task includes documentation impact" if docs_impact_present else "task missing documentation impact section",
        })

    validation_path = templates_dir / "05_validation.template.md"
    if validation_path.exists():
        content = validation_path.read_text(encoding="utf-8")
        doc_sync_present = "documentation sync" in content.lower()
        results.append({
            "check": "cross_ref_validation_doc_sync",
            "path": str(validation_path.relative_to(project_root)),
            "ok": doc_sync_present,
            "detail": "validation includes documentation sync" if doc_sync_present else "validation missing documentation sync section",
        })

    # Template registry should list all templates
    registry_path = templates_dir / "template_registry.md"
    if registry_path.exists():
        content = registry_path.read_text(encoding="utf-8")
        expected_types = ["01_initiative", "02_plan", "03_task", "04_review"]
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

    all_checks = []

    # 1. Folder structure
    print("[validate_delivery_docs] checking folder structure...", flush=True)
    all_checks.extend(_validate_folder_structure(project_root))

    # 2 & 3. Template completeness and structure
    print("[validate_delivery_docs] checking templates...", flush=True)
    all_checks.extend(_validate_templates(project_root))

    # 4. SOP validity
    print("[validate_delivery_docs] checking SOP...", flush=True)
    all_checks.extend(_validate_sop(project_root))

    # 5. Status rules validity
    print("[validate_delivery_docs] checking status rules...", flush=True)
    all_checks.extend(_validate_status_rules(project_root))

    # 5b. Codebase documentation standards
    print("[validate_delivery_docs] checking codebase docs...", flush=True)
    all_checks.extend(_validate_codebase_docs(project_root))

    # 6. Agent registry consistency
    print("[validate_delivery_docs] checking agent registry...", flush=True)
    all_checks.extend(_validate_agents(project_root))

    # 7. Cross-reference integrity
    print("[validate_delivery_docs] checking cross-references...", flush=True)
    all_checks.extend(_validate_cross_references(project_root))

    # Summary
    total = len(all_checks)
    passed = sum(1 for c in all_checks if c["ok"])
    failed = total - passed

    # Write folder map manifest
    folder_map = {
        "schema_version": "v2",
        "validated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "delivery_root": "docs/delivery",
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
        or "docs/delivery/DELIVERY_FOLDER_MAP.json"
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
        meta_path = project_root / meta_json_rel
    else:
        p = Path(folder_map_rel)
        meta_path = project_root / p.parent / f"{p.stem}.meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": "v2",
        "coder_result": {
            "status": "APPROVED" if failed == 0 else "REJECTED",
            "remark": f"Validation: {passed}/{total} checks passed ({failed} failed)",
            "artifacts": {
                "DELIVERY_FOLDER_MAP": str(folder_map_path.relative_to(project_root)),
            },
            "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        },
    }
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
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
