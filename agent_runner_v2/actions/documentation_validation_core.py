from __future__ import annotations

"""
Shared documentation validation helpers and a generic validation engine.
"""

from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Any, Callable


ValidationCheck = dict[str, Any]
ValidationChecker = Callable[[Path], list[ValidationCheck]]


@dataclass(frozen=True)
class DocumentationValidationPlan:
    required_folders: tuple[str, ...] = ()
    required_files: tuple[str, ...] = ()
    section_requirements: dict[str, tuple[str, ...]] = field(default_factory=dict)
    template_ids: dict[str, str] = field(default_factory=dict)
    extra_checkers: tuple[ValidationChecker, ...] = ()


def check_file_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    full = project_root / rel_path
    if full.exists() and full.is_file():
        return True, f"exists ({full.stat().st_size} bytes)"
    return False, f"missing at {rel_path}"


def check_folder_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    full = project_root / rel_path
    if full.exists() and full.is_dir():
        count = len(list(full.iterdir()))
        return True, f"exists ({count} items)"
    return False, f"missing at {rel_path}"


def read_file(project_root: Path, rel_path: str) -> str | None:
    full = project_root / rel_path
    if full.exists() and full.is_file():
        return full.read_text(encoding="utf-8")
    return None


def has_section(content: str, section: str) -> bool:
    pattern = re.compile(rf"^#+\s+.*{re.escape(section)}", re.MULTILINE | re.IGNORECASE)
    return bool(pattern.search(content))


def has_frontmatter_field(content: str, field: str) -> bool:
    pattern = re.compile(rf"^\s*-?\s*{re.escape(field)}\s*[:]", re.MULTILINE)
    return bool(pattern.search(content))


def validate_documentation_plan(*, project_root: Path, plan: DocumentationValidationPlan) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []

    for folder in plan.required_folders:
        ok, detail = check_folder_exists(project_root, folder)
        checks.append({
            "check": "folder_structure",
            "path": folder,
            "ok": ok,
            "detail": detail,
        })

    for rel_path in plan.required_files:
        ok, detail = check_file_exists(project_root, rel_path)
        checks.append({
            "check": "file_exists",
            "path": rel_path,
            "ok": ok,
            "detail": detail,
        })

    for rel_path, required_sections in plan.section_requirements.items():
        content = read_file(project_root, rel_path)
        if content is None:
            continue
        for section in required_sections:
            has = has_section(content, section)
            checks.append({
                "check": "file_section",
                "path": rel_path,
                "section": section,
                "ok": has,
                "detail": "found" if has else "missing",
            })

    for rel_path, template_id in plan.template_ids.items():
        content = read_file(project_root, rel_path)
        if content is None:
            continue
        checks.append({
            "check": "template_id",
            "path": rel_path,
            "template_id": template_id,
            "ok": has_frontmatter_field(content, "template_id") and template_id in content,
            "detail": f"template_id {template_id} {'present' if template_id in content else 'missing'}",
        })

    for checker in plan.extra_checkers:
        checks.extend(checker(project_root))

    return checks
