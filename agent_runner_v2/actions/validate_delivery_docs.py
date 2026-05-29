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
]

REQUIRED_TEMPLATES = {
    "DELIVERY_INITIATIVE_TEMPLATE": "01_initiative.template.md",
    "DELIVERY_PLAN_TEMPLATE": "02_plan.template.md",
    "DELIVERY_TASK_GRAPH_TEMPLATE": "02b_task_graph.template.md",
    "DELIVERY_TASK_TEMPLATE": "03_task.template.md",
    "DELIVERY_IMPL_TEMPLATE": "04_implementation_plan.template.md",
    "DELIVERY_REVIEW_TEMPLATE": "04_review.template.md",
    "DELIVERY_MEMORY_TEMPLATE": "06_memory.template.md",
}

# Minimum required sections per template type (all must be present)
TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    "01_initiative.template.md": [
        "Metadata", "Objective", "Scope", "Constraints",
        "Dependencies", "Success Criteria", "Approval",
    ],
    "02_plan.template.md": [
        "Metadata", "Plan Objective", "Strategy Overview", "Task Breakdown",
        "Scope Mapping", "Deliverables", "Risks", "Acceptance Criteria", "Approval",
    ],
    "02b_task_graph.template.md": [
        "Metadata", "Task Graph Objective", "Task Graph",
        "Execution Flow", "Success Criteria",
    ],
    "03_task.template.md": [
        "Metadata", "Objective", "Inputs", "Outputs",
        "Execution Steps", "Validation Criteria",
    ],
    "04_implementation_plan.template.md": [
        "Metadata", "Objective", "Inputs", "Outputs",
        "Scope Clarification", "File Plan", "Test Plan", "Constraints",
    ],
    "04_review.template.md": [
        "Metadata", "Review Objective", "Issues Identified",
        "Final Decision",
    ],
    "06_memory.template.md": [
        "Metadata", "Purpose", "Key Decisions", "Important References",
    ],
}

SOP_REQUIRED_SECTIONS = [
    "Purpose", "Core Principle", "Authority Precedence",
    "Workflow State Machine", "Agent Roles", "Workflow Phases",
    "Standard Rules", "Folder Structure", "Validation",
]

STATUS_RULES_REQUIRED_SECTIONS = [
    "Purpose", "Core Principles", "Global Workflow Discipline",
    "Lifecycle Rules", "Authority Model", "Approval Gates",
    "Forbidden Transitions", "Document-First", "Traceability",
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

    # Check state machine exists (arrow notation)
    has_state_machine = bool(re.search(r"\w+\s*→\s*\w+", content))
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
    # Check both 00_templates and 08_agents locations
    for rules_path in [
        "docs/delivery/00_templates/DELIVERY_STATUS_RULES_v1.md",
        "docs/delivery/08_agents/DELIVERY_STATUS_RULES_v1.md",
    ]:
        ok, detail = _check_file_exists(project_root, rules_path)
        if ok:
            content = _read_file(project_root, rules_path)
            if content is None:
                continue

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

    # Neither location found
    results.append({
        "check": "status_rules_exists",
        "path": "docs/delivery/08_agents/DELIVERY_STATUS_RULES_v1.md",
        "ok": False,
        "detail": "not found in 00_templates/ or 08_agents/",
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
                # Check metadata
                has_doc_type = _has_metadata_field(agent_content, "Doc Type")
                has_agent_id = _has_metadata_field(agent_content, "Agent ID")
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

    # Write the folder map file
    folder_map_dir = project_root / "docs" / "delivery"
    folder_map_dir.mkdir(parents=True, exist_ok=True)
    folder_map_path = folder_map_dir / "folder_map.json"
    folder_map_path.write_text(
        json.dumps(folder_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Write meta.json sidecar
    meta_path = folder_map_dir / "folder_map.meta.json"
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
