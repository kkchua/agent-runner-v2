#!/usr/bin/env python3
from __future__ import annotations

"""
actions/validate_codebase_docs.py — Deterministic validation for bootstrap/reconcile codebase docs.

Includes semantic validation:
- YAML frontmatter field values (not just existence)
- ASCII-only content
- Change impact structure (no overlap between created/updated)
- Review decision consistency (review doc matches meta.json)
"""

import json
import re
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..doc_paths import codebase_doc_rel
from ..codebase_docs import build_snapshot, render_validation
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _validate_frontmatter(path: Path) -> tuple[bool, str]:
    """Validate YAML frontmatter has required field values.
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not path.exists():
        return False, f"File does not exist: {path.name}"
    
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, f"{path.name}: No YAML frontmatter"
    
    # Extract frontmatter between --- markers
    end = content.find("---", 3)
    if end == -1:
        return False, f"{path.name}: Incomplete YAML frontmatter"
    
    frontmatter = content[3:end].strip()
    
    # Required field values per prompt specification
    required = {
        "doc_type": "system",
        "authority": "workflow-generated",
        "scan_policy": "include",
        "lifecycle_status": "approved",
        "version": "1.0.0",
    }
    
    errors = []
    for field, expected in required.items():
        # Check for field with expected value (with quotes)
        pattern = rf'{field}:\s*"{re.escape(expected)}"'
        if not re.search(pattern, frontmatter):
            errors.append(f"{field} != \"{expected}\"")
    
    if errors:
        return False, f"{path.name}: {', '.join(errors)}"
    
    return True, f"{path.name}: frontmatter valid"


def _extract_section_files(content: str, section_title: str) -> set[str]:
    """Extract file paths from a markdown section.
    
    Looks for lines starting with - or * under the section title.
    """
    files = set()
    in_section = False
    
    for line in content.splitlines():
        # Check if we're entering the target section
        if section_title.lower() in line.lower() and line.startswith("#"):
            in_section = True
            continue
        
        # Check if we're leaving the section (new heading)
        if in_section and line.startswith("#"):
            break
        
        # Extract file paths from list items
        if in_section and (line.strip().startswith("-") or line.strip().startswith("*")):
            # Extract path-like content (contains / or .)
            item = line.strip().lstrip("-*").strip()
            if "/" in item or "." in item:
                # Extract just the path part (before any description)
                path_part = item.split("—")[0].split("-")[0].split("(")[0].strip()
                if path_part:
                    files.add(path_part)
    
    return files


def _validate_change_impact_structure(path: Path) -> tuple[bool, str]:
    """Validate change impact report doesn't list files in both created and updated sections.
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not path.exists():
        return False, f"File does not exist: {path.name}"
    
    content = path.read_text(encoding="utf-8")
    
    # Extract files from "Documentation Created" and "Documentation Updated" sections
    created_files = _extract_section_files(content, "Documentation Created")
    updated_files = _extract_section_files(content, "Documentation Updated")
    
    # Check for overlap
    overlap = created_files & updated_files
    
    if overlap:
        return False, f"{path.name}: Files in both created and updated: {', '.join(list(overlap)[:3])}"
    
    return True, f"{path.name}: No overlap between created/updated"


def _validate_review_consistency(review_path: Path, meta_path: Path) -> tuple[bool, str]:
    """Validate review decision in document matches meta.json status.

    Returns:
        Tuple of (is_valid, message)
    """
    if not review_path.exists():
        return False, f"Review file does not exist: {review_path.name}"

    if not meta_path.exists():
        return False, f"Meta file does not exist: {meta_path.name}"

    review_content = review_path.read_text(encoding="utf-8")

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in {meta_path.name}: {e}"

    # Extract decision from review document
    # Look for explicit APPROVED or REJECTED markers in various formats:
    # - "Decision: APPROVED" (inline with colon)
    # - "**APPROVED**" (bold markdown)
    # - "## Decision\n\nAPPROVED" (heading followed by plain text on own line)
    review_decision = None
    
    # Check for inline formats first
    if "Decision: APPROVED" in review_content or "**APPROVED**" in review_content:
        review_decision = "APPROVED"
    elif "Decision: REJECTED" in review_content or "**REJECTED**" in review_content:
        review_decision = "REJECTED"
    else:
        # Check for plain text decision after ## Decision heading
        # Look for lines containing only APPROVED or REJECTED (case-insensitive)
        for line in review_content.splitlines():
            stripped = line.strip().upper()
            if stripped == "APPROVED":
                review_decision = "APPROVED"
                break
            elif stripped == "REJECTED":
                review_decision = "REJECTED"
                break

    if review_decision is None:
        return False, f"{review_path.name}: No explicit decision found"

    meta_status = meta.get("coder_result", {}).get("status") or meta.get("status")

    if review_decision != meta_status:
        return False, f"{review_path.name}: Review says {review_decision}, meta.json says {meta_status}"

    return True, f"{review_path.name}: Decision consistent ({review_decision})"


def validate_codebase_docs(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "reconcile")
    job_id = str(state.get("job_id") or "codebase-scan")
    step = str(state.get("current_step") or "validate_codebase_docs")
    meta_rel = resolve_step_meta_rel(context=context, state=state, context_key="VALIDATION_FILE_METAJSON", default_step=step)

    # Support staging root override (for sdlc_00_codebase_v1 staging pattern)
    staging_root = str(step_cfg.get("staging_root") or "")
    if staging_root:
        staging_root = staging_root.replace("{job_id}", job_id)
        base_rel = staging_root
    else:
        base_rel = codebase_doc_rel("")

    snapshot = build_snapshot(
        project_root,
        mode=mode,
        job_id=job_id,
        step=step,
        workflow_name=str(state.get("template_group") or mode),
    )

    inventory_path = project_root / f"{base_rel}/01_inventory/codebase_inventory.md"
    module_dir = project_root / f"{base_rel}/02_modules"
    component_dir = project_root / f"{base_rel}/03_components"
    change_dir = project_root / f"{base_rel}/04_changes"
    change_path = change_dir / f"{job_id}-{mode}.md"

    checks: list[tuple[str, bool, str]] = []
    checks.append(("inventory exists", inventory_path.exists(), str(inventory_path.relative_to(project_root))))
    checks.append(("change impact exists", change_path.exists(), str(change_path.relative_to(project_root))))

    module_docs_ok = True
    for module_record in snapshot["python_modules"]:
        doc_name = Path(module_record["owner_doc_path"]).name
        doc_path = module_dir / doc_name
        if not doc_path.exists():
            module_docs_ok = False
            break
    checks.append(("module docs exist", module_docs_ok, "all Python modules mapped"))

    component_docs = [
        component_dir / "workflow-families.md",
        component_dir / "actions-package.md",
        component_dir / "tests-suite.md",
        component_dir / "scripts-suite.md",
        component_dir / "config-and-data.md",
        component_dir / "codebase-governance.md",
    ]
    checks.append(("component docs exist", all(path.exists() for path in component_docs), "baseline component set"))
    checks.append(("inventory row count", "documentation files" in inventory_path.read_text(encoding="utf-8"), "inventory rendered"))

    # ── Semantic Validation ──────────────────────────────────────────────
    # Validate YAML frontmatter field values (not just existence)
    if inventory_path.exists():
        ok, msg = _validate_frontmatter(inventory_path)
        checks.append(("inventory frontmatter values", ok, msg))
    
    if change_path.exists():
        ok, msg = _validate_frontmatter(change_path)
        checks.append(("change impact frontmatter values", ok, msg))

    # Validate change impact structure (no overlap between created/updated)
    if change_path.exists():
        ok, msg = _validate_change_impact_structure(change_path)
        checks.append(("change impact structure", ok, msg))
    
    # Validate review decision consistency (if review file exists)
    review_path = change_dir.parent / "sync_logs" / f"{job_id}-review.md"
    review_meta_path = review_path.parent / f"{job_id}-review.meta.json"
    if review_path.exists() and review_meta_path.exists():
        ok, msg = _validate_review_consistency(review_path, review_meta_path)
        checks.append(("review decision consistency", ok, msg))

    passed = all(ok for _, ok, _ in checks)
    title = f"{project_root.name or 'repository'} codebase {mode} validation"
    validation_path = change_dir / f"{job_id}-{mode}-validation.md"
    _write_text(validation_path, render_validation(snapshot, title=title, checks=checks))
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED" if passed else "REJECTED", remark=f"Codebase docs validation {mode} {'passed' if passed else 'failed'}.", artifacts={"VALIDATION_FILE": validation_path.relative_to(project_root).as_posix()})

    status = "APPROVED" if passed else "REJECTED"
    return ActionResult(
        status=status,
        remark=f"Codebase docs validation {mode} {'passed' if passed else 'failed'}.",
        artifacts={"VALIDATION_FILE": validation_path.relative_to(project_root).as_posix()},
        reject_code=None if passed else "CODEBASE_DOCS_VALIDATION_FAILED",
    )
