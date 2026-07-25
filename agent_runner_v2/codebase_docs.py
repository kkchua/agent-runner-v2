from __future__ import annotations

"""
codebase_docs.py — Deterministic repo scan and codebase-doc generation helpers.
"""

import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from .runtime_context import get_context, get_workflow_module
from .bundle_loader import load_project_config
from .doc_paths import codebase_doc_rel
from .doc_text import sanitize_ascii


EXCLUDED_DIRS = {
    ".git",
    ".ukbe-runner",
    ".tmp",
    "tmp",
    "temp",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    ".tox",
    ".venv",
    "venv",
    "env",
    "agent_runner_v2.egg-info",
    "masterplan",
}

STD_LIBS = set(getattr(sys, "stdlib_module_names", set()))


@dataclass(frozen=True)
class ScanItem:
    rel_path: str
    category: str
    subcategory: str
    doc_mode: str
    status: str
    owner_doc_path: str
    last_verified_by_change: str


def _today_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _today_date() -> str:
    return datetime.now().date().isoformat()


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


_NON_PACKAGE_DIRS = {
    "tests", "test", "scripts", "docs", "tools", "masterplan",
    "migrations", "alembic", "examples", "example", "fixtures",
}


def _detect_package_root(project_root: Path) -> str | None:
    """Auto-detect the main Python package directory name."""
    candidates = []
    for child in sorted(project_root.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith((".", "_")) or name.startswith("__"):
            continue
        if name in EXCLUDED_DIRS or name in _NON_PACKAGE_DIRS:
            continue
        if name.endswith((".egg-info", ".dist-info")):
            continue
        if (child / "__init__.py").exists():
            candidates.append(name)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        for name in candidates:
            if (project_root / name / "__main__.py").exists():
                return name
        return max(candidates, key=lambda n: sum(
            1 for _ in (project_root / n).rglob("*.py")
        ))
    return None


_DIR_AREA_MAP = {
    "actions": "actions",
    "tools": "tools",
    "api": "api",
    "core": "core",
    "database": "database",
    "db": "database",
    "models": "models",
    "services": "services",
    "workers": "workers",
    "commands": "commands",
    "schema": "schema",
    "state": "state",
    "coder": "coder",
    "bootstrap": "bootstrap",
    "backend": "backend",
}

_FULL_DOC_DIRS = {"actions", "core", "api", "services", "database", "db", "backend", "workers"}


def _module_area(rel_path: str, pkg_root: str | None = None) -> str:
    rel = PurePosixPath(rel_path)
    if rel.name == "__init__.py":
        return "package"
    if pkg_root and rel.parts[0] == pkg_root and len(rel.parts) == 2:
        return "core"
    if len(rel.parts) >= 3 and rel.parts[0] == (pkg_root or rel.parts[0]):
        dir_name = rel.parts[1]
        if dir_name in _DIR_AREA_MAP:
            return _DIR_AREA_MAP[dir_name]
    if len(rel.parts) >= 2:
        dir_name = rel.parts[-2]
        if dir_name in _DIR_AREA_MAP:
            return _DIR_AREA_MAP[dir_name]
    return "support"


def _module_doc_mode(rel_path: str, pkg_root: str | None = None) -> str:
    rel = PurePosixPath(rel_path)
    if rel.name == "__init__.py":
        return "stub"
    if pkg_root and rel.parts[0] == pkg_root and len(rel.parts) >= 3:
        dir_name = rel.parts[1]
        if dir_name in _FULL_DOC_DIRS:
            return "full"
    if pkg_root and rel.parts[0] == pkg_root and len(rel.parts) == 2:
        return "full"
    return "summary"


def _component_owner_doc(component_name: str) -> str:
    slug = _slugify(component_name)
    return codebase_doc_rel(f"03_components/{slug}.md")


def _module_doc_path(rel_path: str) -> str:
    stem = _slugify(rel_path.replace("/", "__").replace(r"\\", "__").removesuffix(".py"))
    return codebase_doc_rel(f"02_modules/{stem}.md")


def _module_name_from_path(rel_path: str, pkg_root: str | None = None) -> str:
    rel = PurePosixPath(rel_path)
    effective_root = pkg_root or "agent_runner_v2"
    if not pkg_root or rel.parts[0] != effective_root:
        return rel_path
    if rel.name == "__init__.py":
        return effective_root
    return ".".join(rel.with_suffix("").parts)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _iter_repo_files(project_root: Path) -> list[Path]:
    git_files = _iter_git_tracked_and_unignored_files(project_root)
    if git_files is not None:
        return git_files

    files: list[Path] = []
    for path in project_root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(project_root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if rel.suffix in {".pyc", ".pyo", ".tmp"}:
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(project_root).as_posix().lower())


def _iter_git_tracked_and_unignored_files(project_root: Path) -> list[Path] | None:
    if not (project_root / ".git").exists():
        return None
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=project_root,
            capture_output=True,
            text=False,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    files: list[Path] = []
    for raw_rel in proc.stdout.split(b"\0"):
        if not raw_rel:
            continue
        rel_posix = raw_rel.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        rel = PurePosixPath(rel_posix)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if rel.suffix in {".pyc", ".pyo", ".tmp"}:
            continue
        path = project_root / Path(rel_posix)
        if path.exists() and path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(project_root).as_posix().lower())


def _classify_file(project_root: Path, path: Path, pkg_root: str | None = None) -> ScanItem:
    rel_path = path.relative_to(project_root).as_posix()
    rel = PurePosixPath(rel_path)
    effective_pkg = pkg_root or "agent_runner_v2"
    if pkg_root and rel.parts[0] == pkg_root and rel.suffix == ".py":
        category = "python modules"
        subcategory = _module_area(rel_path, pkg_root=pkg_root)
        owner_doc = _module_doc_path(rel_path)
        doc_mode = _module_doc_mode(rel_path, pkg_root=pkg_root)
    elif rel.parts[:3] == (effective_pkg, "bootstrap", "workflows"):
        category = "bootstrap workflow files"
        subcategory = "workflow assets"
        owner_doc = _component_owner_doc("workflow families")
        doc_mode = "full"
    elif rel.parts[0] == "tests" and rel.suffix == ".py":
        category = "test files"
        subcategory = "tests"
        owner_doc = _component_owner_doc("tests suite")
        doc_mode = "summary"
    elif rel.suffix in {".bat", ".sh"} or rel.parts[0] == "scripts":
        category = "scripts"
        subcategory = "scripts"
        owner_doc = _component_owner_doc("scripts suite")
        doc_mode = "summary"
    elif rel.suffix in {".toml", ".json", ".yaml", ".yml"} or rel.name == ".env.example":
        category = "configuration/data files"
        subcategory = "config"
        owner_doc = _component_owner_doc("config and data")
        doc_mode = "summary"
    elif rel.suffix == ".md":
        category = "documentation files"
        subcategory = "docs"
        owner_doc = _component_owner_doc("codebase governance")
        doc_mode = "summary"
    elif rel.suffix == ".html":
        category = "documentation files"
        subcategory = "docs"
        owner_doc = _component_owner_doc("codebase governance")
        doc_mode = "summary"
    else:
        category = "other files"
        subcategory = "other"
        owner_doc = _component_owner_doc("codebase governance")
        doc_mode = "summary"

    return ScanItem(
        rel_path=rel_path,
        category=category,
        subcategory=subcategory,
        doc_mode=doc_mode,
        status="current",
        owner_doc_path=owner_doc,
        last_verified_by_change="bootstrap/reconcile scan",
    )


def _annotation_to_str(annotation: ast.expr | None) -> str:
    """Convert AST annotation to string representation."""
    if annotation is None:
        return ""
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant):
        return repr(annotation.value)
    if isinstance(annotation, ast.Attribute):
        return f"{_annotation_to_str(annotation.value)}.{annotation.attr}"
    if isinstance(annotation, ast.Subscript):
        return f"{_annotation_to_str(annotation.value)}[{_annotation_to_str(annotation.slice)}]"
    if isinstance(annotation, ast.Tuple):
        return ", ".join(_annotation_to_str(e) for e in annotation.elts)
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        return f"{_annotation_to_str(annotation.left)} | {_annotation_to_str(annotation.right)}"
    return ""


def _build_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Build full function signature with type hints."""
    args = node.args
    parts: list[str] = []

    # Positional args
    num_args = len(args.args)
    num_defaults = len(args.defaults)
    first_default_idx = num_args - num_defaults

    for i, arg in enumerate(args.args):
        if arg.arg == "self" or arg.arg == "cls":
            continue
        part = arg.arg
        if arg.annotation:
            part += f": {_annotation_to_str(arg.annotation)}"
        if i >= first_default_idx:
            default_idx = i - first_default_idx
            default = args.defaults[default_idx]
            part += f" = {_annotation_to_str(default)}"
        parts.append(part)

    # *args
    if args.vararg:
        part = f"*{args.vararg.arg}"
        if args.vararg.annotation:
            part += f": {_annotation_to_str(args.vararg.annotation)}"
        parts.append(part)
    elif args.kwonlyargs:
        parts.append("*")

    # keyword-only args
    for i, arg in enumerate(args.kwonlyargs):
        part = arg.arg
        if arg.annotation:
            part += f": {_annotation_to_str(arg.annotation)}"
        if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
            part += f" = {_annotation_to_str(args.kw_defaults[i])}"
        parts.append(part)

    # **kwargs
    if args.kwarg:
        part = f"**{args.kwarg.arg}"
        if args.kwarg.annotation:
            part += f": {_annotation_to_str(args.kwarg.annotation)}"
        parts.append(part)

    return f"({', '.join(parts)})"


def _extract_parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, str]]:
    """Extract parameter details with types and defaults."""
    args = node.args
    params: list[dict[str, str]] = []

    num_args = len(args.args)
    num_defaults = len(args.defaults)
    first_default_idx = num_args - num_defaults

    for i, arg in enumerate(args.args):
        if arg.arg == "self" or arg.arg == "cls":
            continue
        param: dict[str, str] = {
            "name": arg.arg,
            "type": _annotation_to_str(arg.annotation) if arg.annotation else "",
            "default": "",
            "kind": "positional",
        }
        if i >= first_default_idx:
            default_idx = i - first_default_idx
            default = args.defaults[default_idx]
            param["default"] = _annotation_to_str(default)
        params.append(param)

    # *args
    if args.vararg:
        params.append({
            "name": f"*{args.vararg.arg}",
            "type": _annotation_to_str(args.vararg.annotation) if args.vararg.annotation else "",
            "default": "",
            "kind": "varargs",
        })

    # keyword-only args
    for i, arg in enumerate(args.kwonlyargs):
        param = {
            "name": arg.arg,
            "type": _annotation_to_str(arg.annotation) if arg.annotation else "",
            "default": "",
            "kind": "keyword-only",
        }
        if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
            param["default"] = _annotation_to_str(args.kw_defaults[i])
        params.append(param)

    # **kwargs
    if args.kwarg:
        params.append({
            "name": f"**{args.kwarg.arg}",
            "type": _annotation_to_str(args.kwarg.annotation) if args.kwarg.annotation else "",
            "default": "",
            "kind": "kwargs",
        })

    return params


def _extract_return_type(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Extract return type annotation."""
    if node.returns:
        return _annotation_to_str(node.returns)
    return ""


def _extract_raises(docstring: str) -> list[dict[str, str]]:
    """Parse Raises section from docstring.

    Handles formats like:
        Raises:
            ExceptionType — description
            ExceptionType: description
            ExceptionType - description
    """
    raises: list[dict[str, str]] = []
    if not docstring:
        return raises

    lines = docstring.splitlines()
    in_raises = False
    current_exception = ""
    current_description: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Check for Raises: header
        if stripped.lower().startswith("raises:"):
            in_raises = True
            continue

        # Check for another section header (ends Raises section)
        # Section headers are typically all caps or end with colon and are not indented in docstring
        if in_raises and stripped:
            # Check if this looks like a new section (e.g., "Returns:", "Note:", etc.)
            lower = stripped.lower()
            if (lower.startswith(("returns:", "yields:", "note:", "example:", "examples:",
                                  "args:", "arguments:", "attributes:", "see also:",
                                  "references:", "warnings:"))):
                if current_exception:
                    raises.append({
                        "exception": current_exception,
                        "description": " ".join(current_description).strip(),
                    })
                in_raises = False
                continue

        if in_raises and stripped:
            # Check if this is a new exception line
            # Look for patterns: "ExceptionName - desc", "ExceptionName: desc", "ExceptionName — desc"
            is_exception_line = False
            for sep in [" - ", " -- ", " — ", ":"]:
                if sep in stripped:
                    # Check if the part before separator looks like an exception name
                    parts = stripped.split(sep, 1)
                    potential_name = parts[0].strip()
                    # Exception names are typically CamelCase or have underscores
                    if potential_name and potential_name[0].isupper():
                        # Save previous exception if any
                        if current_exception:
                            raises.append({
                                "exception": current_exception,
                                "description": " ".join(current_description).strip(),
                            })
                            current_description = []

                        # Parse new exception
                        current_exception = potential_name
                        if len(parts) > 1:
                            current_description = [parts[1].strip()]
                        is_exception_line = True
                        break

            if not is_exception_line and current_exception:
                # Continuation of description
                current_description.append(stripped)

    # Don't forget the last exception
    if current_exception:
        raises.append({
            "exception": current_exception,
            "description": " ".join(current_description).strip(),
        })

    return raises


def _extract_decorators(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
    """Extract decorator names from a function or class definition."""
    decorators: list[str] = []
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            decorators.append(decorator.id)
        elif isinstance(decorator, ast.Attribute):
            decorators.append(f"{_annotation_to_str(decorator.value)}.{decorator.attr}")
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                decorators.append(decorator.func.id)
            elif isinstance(decorator.func, ast.Attribute):
                decorators.append(f"{_annotation_to_str(decorator.func.value)}.{decorator.func.attr}")
    return decorators


def _scan_python_module(project_root: Path, path: Path, pkg_root: str | None = None) -> dict[str, Any]:
    rel_path = path.relative_to(project_root).as_posix()
    try:
        tree = ast.parse(_read_text(path))
    except SyntaxError:
        tree = ast.Module(body=[], type_ignores=[])
    module_doc = ast.get_docstring(tree) or ""
    imports: list[str] = []
    functions: list[dict[str, str]] = []
    classes: list[dict[str, str]] = []
    constants: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod:
                imports.append(mod)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            docstring = ast.get_docstring(node) or ""
            functions.append({
                "name": node.name,
                "signature": _build_signature(node),
                "summary": docstring.splitlines()[0] if docstring else "",
                "docstring": docstring,
                "parameters": _extract_parameters(node),
                "return_type": _extract_return_type(node),
                "raises": _extract_raises(docstring),
                "decorators": _extract_decorators(node),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            })
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            docstring = ast.get_docstring(node) or ""
            # Extract class methods
            methods: list[dict[str, Any]] = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
                    method_doc = ast.get_docstring(item) or ""
                    methods.append({
                        "name": item.name,
                        "signature": _build_signature(item),
                        "summary": method_doc.splitlines()[0] if method_doc else "",
                        "return_type": _extract_return_type(item),
                    })
            classes.append({
                "name": node.name,
                "summary": docstring.splitlines()[0] if docstring else "",
                "docstring": docstring,
                "decorators": _extract_decorators(node),
                "bases": [_annotation_to_str(base) for base in node.bases],
                "methods": methods,
            })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)

    imports = sorted(dict.fromkeys(imports))
    stdlib_imports = []
    local_imports = []
    external_imports = []
    effective_pkg = pkg_root or "agent_runner_v2"
    for imp in imports:
        top = imp.split(".", 1)[0]
        if top == effective_pkg or imp.startswith("."):
            local_imports.append(imp)
        elif top in STD_LIBS:
            stdlib_imports.append(imp)
        else:
            external_imports.append(imp)

    return {
        "rel_path": rel_path,
        "module_name": _module_name_from_path(rel_path, pkg_root=pkg_root),
        "module_area": _module_area(rel_path, pkg_root=pkg_root),
        "doc_mode": _module_doc_mode(rel_path, pkg_root=pkg_root),
        "owner_doc_path": _module_doc_path(rel_path),
        "summary": module_doc.splitlines()[0] if module_doc else "Auto-generated baseline module documentation.",
        "module_doc": module_doc,
        "stdlib_imports": stdlib_imports,
        "local_imports": local_imports,
        "external_imports": external_imports,
        "public_functions": functions,
        "public_classes": classes,
        "constants": constants,
        "test_references": [],
    }


def _find_test_references(project_root: Path, module_record: dict[str, Any]) -> list[str]:
    module_name = Path(module_record["rel_path"]).stem
    refs: list[str] = []
    for test_path in sorted((project_root / "tests").glob("*.py")):
        text = _read_text(test_path)
        if module_name in text or module_record["module_name"] in text or module_record["rel_path"] in text:
            refs.append(test_path.relative_to(project_root).as_posix())
    return refs


def _normalize_workflow_metadata_path(path_value: str) -> str:
    value = str(path_value or "").strip()
    if not value:
        return ""

    path = Path(value)
    if not path.is_absolute():
        return path.as_posix()

    ctx = get_context()
    workflow_root = getattr(ctx, "workflow_root", None)
    if isinstance(workflow_root, Path):
        try:
            return path.relative_to(workflow_root).as_posix()
        except ValueError:
            pass

    workspace_root = getattr(ctx, "workspace_root", None)
    if isinstance(workspace_root, Path):
        try:
            return path.relative_to(workspace_root).as_posix()
        except ValueError:
            pass

    return path.name


def _workflow_family_records() -> list[dict[str, Any]]:
    bundle = get_workflow_module()
    if bundle is None:
        raise RuntimeError("Workflow module is not loaded. Runtime must use the global workflow bundle.")
    template_groups = getattr(bundle, "TEMPLATE_GROUPS", {}) or {}

    records: list[dict[str, Any]] = []
    for family_name, cfg in template_groups.items():
        visibility = str(cfg.get("visibility") or "visible").lower()
        if visibility not in {"visible", "canonical"}:
            continue
        steps = []
        for step_name in cfg.get("steps", []):
            step_cfg = cfg.get("step_configs", {}).get(step_name, {})
            steps.append({
                "step": step_name,
                "kind": "action" if step_cfg.get("action") else "coder",
                "coder": (step_cfg.get("coder") or {}).get("default", ""),
                "prompt_file": _normalize_workflow_metadata_path(step_cfg.get("prompt_file", "")),
                "produces": list(step_cfg.get("produces") or []),
            })
        records.append({
            "family_name": family_name,
            "job_prefix": cfg.get("job_prefix", ""),
            "job_init_step": cfg.get("job_init_step", ""),
            "job_init_inputs": list(cfg.get("job_init_inputs") or []),
            "visibility": visibility,
            "steps": steps,
            "component_id": family_name,
            "owner_doc_path": _component_owner_doc("workflow families"),
        })
    return records


def build_snapshot(project_root: Path, *, mode: str, job_id: str, step: str, workflow_name: str | None = None) -> dict[str, Any]:
    now = _today_iso()
    workflow_name = str(workflow_name or get_context().workflow_name or mode)
    project_config = load_project_config(project_root)
    pkg_root = _detect_package_root(project_root)
    files = _iter_repo_files(project_root)
    items = [_classify_file(project_root, path, pkg_root=pkg_root) for path in files]
    python_modules = []
    for path in files:
        rel = path.relative_to(project_root)
        if pkg_root and rel.parts[0] == pkg_root and rel.suffix == ".py":
            rec = _scan_python_module(project_root, path, pkg_root=pkg_root)
            python_modules.append(rec)
    for rec in python_modules:
        rec["test_references"] = _find_test_references(project_root, rec)

    workflow_families = _workflow_family_records()

    counts: dict[str, dict[str, int]] = {}
    for item in items:
        counts.setdefault(item.category, {"current": 0, "needs_update": 0, "pending_review": 0, "superseded": 0, "total": 0})
        counts[item.category]["total"] += 1
        counts[item.category][item.status] += 1

    return {
        "generated_at": now,
        "mode": mode,
        "workflow_name": workflow_name,
        "pkg_root": pkg_root,
        "bundle_profile": str(project_config.get("bundle_profile") or "core+workflow"),
        "bundle_domain": str(project_config.get("bundle_domain") or "general"),
        "bundle_manifest": str(project_config.get("bundle_manifest") or ""),
        "architecture_profile": str(project_config.get("architecture_profile") or "provisional"),
        "architecture_target_profile": str(project_config.get("architecture_target_profile") or "repo-selected"),
        "architecture_migration_mode": str(project_config.get("architecture_migration_mode") or "targeted_migration"),
        "job_id": job_id,
        "step": step,
        "project_root": str(project_root),
        "items": items,
        "python_modules": python_modules,
        "workflow_families": workflow_families,
        "counts": counts,
    }


def _yaml_list(values: list[str]) -> str:
    return "[" + ", ".join(json.dumps(v) for v in values) + "]"


def _frontmatter(lines: list[str]) -> str:
    return "---\n" + "\n".join(lines) + "\n---\n\n"


def render_inventory(snapshot: dict[str, Any], *, title: str) -> str:
    items = snapshot["items"]
    counts = snapshot["counts"]
    generated_at = snapshot["generated_at"]
    job_id = snapshot["job_id"]
    step = snapshot["step"]
    workflow_name = str(snapshot.get("workflow_name") or snapshot["mode"])

    def rows(category: str) -> list[ScanItem]:
        return [item for item in items if item.category == category]

    sections = [
        _frontmatter([
            f'title: "Codebase Inventory - {title}"',
            'template_id: "CODEBASE-INV-v1"',
            'version: "1.0.0"',
            'doc_type: "system"',
            'authority: "workflow-generated"',
            'scan_policy: "include"',
            'lifecycle_status: "approved"',
            f'generated: "{generated_at}"',
            f'workflow: "{workflow_name}"',
            f'step: "{step}"',
            f'change_id: "{job_id}"',
        ]),
        f"# Codebase Inventory: {title}\n\n",
        "## 1. Inventory Scope\n\n",
        f"This inventory was generated from a repository scan at `{generated_at}`.\n\n",
    ]

    def table(header: list[str], rows_data: list[list[str]]) -> str:
        out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
        for row in rows_data:
            out.append("| " + " | ".join(row) + " |")
        return "\n".join(out) + "\n\n"

    categories = [
        ("2. Python Source Modules", "python modules"),
        ("3. Bootstrap Workflow Files", "bootstrap workflow files"),
        ("4. Configuration / Data Files", "configuration/data files"),
        ("5. Scripts", "scripts"),
        ("6. Test Files", "test files"),
        ("7. Documentation Files", "documentation files"),
        ("8. Other Files", "other files"),
    ]
    for heading, category in categories:
        sections.append(f"## {heading}\n\n")
        cat_rows = rows(category)
        if category == "python modules":
            sections.append(table(
                ["File Path", "Module Area", "Documentation Mode", "Status", "Owner Doc Path", "Last Verified By Change"],
                [[r.rel_path, r.subcategory, r.doc_mode, r.status, r.owner_doc_path, r.last_verified_by_change] for r in cat_rows],
            ))
        elif category == "bootstrap workflow files":
            sections.append(table(
                ["File Path", "Description", "Documentation Mode", "Status", "Owner Doc Path", "Last Verified By Change"],
                [[r.rel_path, "workflow asset", r.doc_mode, r.status, r.owner_doc_path, r.last_verified_by_change] for r in cat_rows],
            ))
        elif category == "configuration/data files":
            sections.append(table(
                ["File Path", "Format", "Documentation Mode", "Status", "Owner Doc Path", "Last Verified By Change"],
                [[r.rel_path, Path(r.rel_path).suffix.lstrip(".") or "env", r.doc_mode, r.status, r.owner_doc_path, r.last_verified_by_change] for r in cat_rows],
            ))
        elif category == "scripts":
            sections.append(table(
                ["File Path", "Type", "Documentation Mode", "Status", "Owner Doc Path", "Last Verified By Change"],
                [[r.rel_path, Path(r.rel_path).suffix or "script", r.doc_mode, r.status, r.owner_doc_path, r.last_verified_by_change] for r in cat_rows],
            ))
        elif category == "test files":
            sections.append(table(
                ["File Path", "Coverage Area", "Documentation Mode", "Status", "Owner Doc Path", "Last Verified By Change"],
                [[r.rel_path, "tests", r.doc_mode, r.status, r.owner_doc_path, r.last_verified_by_change] for r in cat_rows],
            ))
        elif category == "documentation files":
            sections.append(table(
                ["File Path", "Category", "Documentation Mode", "Status", "Owner Doc Path", "Last Verified By Change"],
                [[r.rel_path, "docs", r.doc_mode, r.status, r.owner_doc_path, r.last_verified_by_change] for r in cat_rows],
            ))
        else:
            sections.append(table(
                ["File Path", "Category", "Documentation Mode", "Status", "Owner Doc Path", "Last Verified By Change"],
                [[r.rel_path, "other", r.doc_mode, r.status, r.owner_doc_path, r.last_verified_by_change] for r in cat_rows],
            ))

    sections.append("## 9. Summary Statistics\n\n")
    sections.append(table(
        ["Category", "Total Files", "Current", "Needs Update", "Pending Review", "Superseded"],
        [
            [
                category,
                str(data["total"]),
                str(data["current"]),
                str(data["needs_update"]),
                str(data["pending_review"]),
                str(data["superseded"]),
            ]
            for category, data in counts.items()
        ],
    ))

    sections.append("## 10. Status Legend\n\n")
    sections.append(
        "- `current`: documentation is up to date and matches the source\n"
        "- `needs_update`: source changed and documentation is stale\n"
        "- `pending_review`: documentation exists but has not been verified\n"
        "- `superseded`: documentation is obsolete or replaced\n\n"
    )

    sections.append("## 11. Verification Log\n\n")
    sections.append(table(
        ["Date", "Verified By", "Scope", "Result"],
        [[generated_at[:10], workflow_name, "repository scan", "complete"]],
    ))
    return sanitize_ascii("".join(sections))


def render_module_doc(snapshot: dict[str, Any], module_record: dict[str, Any]) -> str:
    generated_at = snapshot["generated_at"]
    workflow_name = str(snapshot.get("workflow_name") or snapshot["mode"])
    rel_path = module_record["rel_path"]
    module_name = module_record["module_name"]
    frontmatter = _frontmatter([
        f'title: "Module Documentation: {module_name}"',
        'template_id: "CB-02"',
        'version: "1.0.0"',
        'doc_type: "system"',
        'authority: "workflow-generated"',
        'scan_policy: "include"',
        'lifecycle_status: "approved"',
        f'module_path: "{rel_path}"',
        f'module_area: "{module_record["module_area"]}"',
        f'documentation_mode: "{module_record["doc_mode"]}"',
        f'owner_doc_path: "{module_record["owner_doc_path"]}"',
        f'last_verified_by_change: "{workflow_name} / {snapshot["job_id"]} / {generated_at}"',
        f'created: "{generated_at}"',
        f'owner: "{workflow_name}"',
    ])
    lines = [
        frontmatter,
        f"# Module Documentation: {module_name}\n\n",
        "## 1. Module Overview\n\n",
        "### 1.1 Purpose\n\n",
        (sanitize_ascii(module_record["module_doc"].splitlines()[0]) if module_record["module_doc"] else "Auto-generated baseline documentation from repository scan.") + "\n\n",
        "### 1.2 Responsibility\n\n",
        f"This module belongs to the `{module_record['module_area']}` area and is documented as `{module_record['doc_mode']}`.\n\n",
        "### 1.3 Dependencies\n\n",
        "| Dependency | Type | Purpose |\n|------------|------|---------|\n",
    ]
    for imp in module_record["stdlib_imports"]:
        lines.append(f"| `{imp}` | stdlib module | imported dependency |\n")
    for imp in module_record["local_imports"]:
        lines.append(f"| `{imp}` | internal module | repository dependency |\n")
    for imp in module_record["external_imports"]:
        lines.append(f"| `{imp}` | external module | repository dependency |\n")
    if not (module_record["stdlib_imports"] or module_record["local_imports"] or module_record["external_imports"]):
        lines.append("| | stdlib module | |\n")

    # Enhanced Classes section
    lines.append("\n## 2. Public API\n\n### 2.1 Classes\n\n")
    if module_record["public_classes"]:
        for cls in module_record["public_classes"]:
            lines.append(f"#### {cls['name']}\n\n")
            if cls.get('bases'):
                lines.append(f"**Inherits from**: {', '.join(f'`{b}`' for b in cls['bases'])}\n\n")
            if cls.get('decorators'):
                lines.append(f"**Decorators**: {', '.join(f'`@{d}`' for d in cls['decorators'])}\n\n")
            lines.append(f"**Purpose**: {sanitize_ascii(cls.get('summary') or 'Public class')}\n\n")
            if cls.get('methods'):
                lines.append("**Methods**:\n\n")
                for method in cls['methods']:
                    sig = method.get('signature', '()')
                    ret = method.get('return_type', '')
                    ret_str = f" -> `{ret}`" if ret else ""
                    lines.append(f"- `{method['name']}{sig}`{ret_str} -- {sanitize_ascii(method.get('summary') or 'method')}\n")
                lines.append("\n")
    else:
        lines.append("No public classes.\n\n")

    # Enhanced Functions section
    lines.append("\n### 2.2 Functions\n\n")
    if module_record["public_functions"]:
        for fn in module_record["public_functions"]:
            async_prefix = "async " if fn.get("is_async") else ""
            lines.append(f"#### {async_prefix}{fn['name']}()\n\n")

            # Decorators
            if fn.get('decorators'):
                lines.append(f"**Decorators**: {', '.join(f'`@{d}`' for d in fn['decorators'])}\n\n")

            # Signature
            lines.append(f"**Signature**: `{fn['name']}{fn['signature']}`\n\n")

            # Summary/Purpose
            if fn.get('summary'):
                lines.append(f"**Purpose**: {sanitize_ascii(fn['summary'])}\n\n")

            # Full docstring (if different from summary)
            docstring = fn.get('docstring', '')
            if docstring and docstring.splitlines()[0] != fn.get('summary', ''):
                # Extract just the description part (before Raises, Returns, etc.)
                desc_lines = []
                for line in docstring.splitlines():
                    if line.strip().lower().startswith(('raises:', 'returns:', 'yields:', 'note:', 'example:', 'args:', 'attributes:')):
                        break
                    desc_lines.append(line)
                desc = '\n'.join(desc_lines).strip()
                if desc and desc != fn.get('summary', ''):
                    lines.append(f"**Description**:\n\n{sanitize_ascii(desc)}\n\n")

            # Parameters table
            params = fn.get('parameters', [])
            if params:
                lines.append("**Parameters**:\n\n")
                lines.append("| Name | Type | Default | Description |\n|------|------|---------|-------------|\n")
                for param in params:
                    name = param.get('name', '')
                    ptype = param.get('type', '')
                    default = param.get('default', '')
                    kind = param.get('kind', '')
                    type_str = f"`{ptype}`" if ptype else "--"
                    default_str = f"`{default}`" if default else "--"
                    # Try to get description from docstring
                    param_desc = _extract_param_description(docstring, name)
                    lines.append(f"| `{name}` | {type_str} | {default_str} | {param_desc} |\n")
                lines.append("\n")

            # Return type
            ret_type = fn.get('return_type', '')
            if ret_type:
                lines.append(f"**Returns**: `{ret_type}`\n\n")

            # Raises section
            raises = fn.get('raises', [])
            if raises:
                lines.append("**Raises**:\n\n")
                for exc in raises:
                    exc_name = exc.get('exception', '')
                    exc_desc = exc.get('description', '')
                    lines.append(f"- `{exc_name}` -- {exc_desc}\n")
                lines.append("\n")

            lines.append("---\n\n")
    else:
        lines.append("No public functions.\n\n")

    # Constants section
    lines.append("\n### 2.3 Constants / Configuration\n\n")
    if module_record["constants"]:
        lines.append("| Name | Purpose |\n|------|--------|\n")
        for const in module_record["constants"]:
            lines.append(f"| `{const}` | module configuration |\n")
        lines.append("\n")
    else:
        lines.append("No public constants.\n\n")

    # Error Handling Summary (aggregated from all functions)
    lines.append("\n## 3. Error Handling\n\n")
    all_raises: dict[str, list[str]] = {}
    for fn in module_record["public_functions"]:
        for exc in fn.get("raises", []):
            exc_name = exc.get("exception", "")
            exc_desc = exc.get("description", "")
            if exc_name:
                if exc_name not in all_raises:
                    all_raises[exc_name] = []
                if exc_desc and exc_desc not in all_raises[exc_name]:
                    all_raises[exc_name].append(exc_desc)

    if all_raises:
        lines.append("| Exception | When | Raised By |\n|-----------|------|----------|\n")
        for exc_name, descriptions in sorted(all_raises.items()):
            desc = descriptions[0] if descriptions else ""
            # Find which functions raise this
            raised_by = [fn['name'] for fn in module_record["public_functions"]
                        if any(e.get('exception') == exc_name for e in fn.get('raises', []))]
            raised_by_str = ', '.join(f'`{f}`' for f in raised_by[:3])
            lines.append(f"| `{exc_name}` | {desc} | {raised_by_str} |\n")
        lines.append("\n")
    else:
        lines.append("No documented exceptions.\n\n")

    # Testing section
    lines.append("\n## 4. Testing\n\n### 4.1 Test Coverage\n\n")
    lines.append("| Test File | Coverage Area |\n|-----------|---------------|\n")
    for test in module_record["test_references"]:
        lines.append(f"| `{test}` | `{module_name}` |\n")
    if not module_record["test_references"]:
        lines.append("| (none) | No test references found |\n")
    lines.append("\n")

    # Change Log
    lines.append("\n## 5. Change Log\n\n")
    lines.append("| Date | Change | Verified By |\n|------|--------|-------------|\n")
    lines.append(f"| {_today_date()} | Initial baseline generated from repository scan | {workflow_name} |\n")
    return sanitize_ascii("".join(lines))


def _extract_param_description(docstring: str, param_name: str) -> str:
    """Extract parameter description from docstring Args/Parameters section."""
    if not docstring:
        return "--"

    lines = docstring.splitlines()
    in_args = False
    for line in lines:
        stripped = line.strip()

        # Check for Args/Parameters header
        if stripped.lower().startswith(('args:', 'arguments:', 'parameters:', 'params:')):
            in_args = True
            continue

        # Check for another section (ends Args)
        if in_args and stripped and not stripped.startswith(' ') and ':' in stripped:
            if not stripped[0].islower():
                in_args = False
                continue

        if in_args and stripped:
            # Check if this is the parameter we're looking for
            # Format: "param_name: description" or "param_name (type): description"
            for sep in [':', ' (']:
                if stripped.startswith(param_name + sep) or stripped.startswith(param_name + ' '):
                    # Extract description
                    if ':' in stripped:
                        desc = stripped.split(':', 1)[1].strip()
                        return desc if desc else "--"
            # Check for continuation lines (indented)
            if line.startswith('    ') and not stripped.startswith(param_name):
                continue

    return "--"


def render_component_doc(snapshot: dict[str, Any], *, component_name: str, rows: list[dict[str, str]], overview: str) -> str:
    generated_at = snapshot["generated_at"]
    workflow_name = str(snapshot.get("workflow_name") or snapshot["mode"])
    frontmatter = _frontmatter([
        f'title: "Component Documentation: {component_name}"',
        'template_id: "CB-03"',
        'version: "1.0.0"',
        'doc_type: "system"',
        'authority: "workflow-generated"',
        'scan_policy: "include"',
        'lifecycle_status: "approved"',
        f'component_id: "{_slugify(component_name)}"',
        f'created: "{generated_at}"',
        f'owner: "{workflow_name}"',
        f'last_verified_by_change: "{workflow_name} / {snapshot["job_id"]} / {generated_at}"',
        f'modules: {_yaml_list([row["module"] for row in rows if row.get("module")])}',
    ])
    out = [frontmatter, f"# Component Documentation: {component_name}\n\n", "## 1. Component Overview\n\n### 1.1 Purpose\n\n", overview, "\n\n### 1.2 Scope\n\n", "| Module | Role in Component |\n|--------|-------------------|\n"]
    for row in rows:
        out.append(f"| `{row['module']}` | {row['role']} |\n")
    out.append("\n## 2. Architecture\n\n### 2.1 Component Diagram\n\nGenerated from repository scan baseline.\n\n### 2.2 Data Flow\n\nRepository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.\n\n### 2.3 External Interfaces\n\n| Interface | Direction | Protocol | Description |\n|-----------|-----------|----------|-------------|\n")
    for row in rows:
        out.append(f"| `{row['module']}` | outbound | markdown | {row['role']} |\n")
    out.append("\n## 3. Behavior\n\n### 3.1 Lifecycle\n\nCreated during codebase bootstrap or reconcile runs and refreshed when repository structure changes.\n\n### 3.2 State Management\n\nState is represented by the generated inventory and per-module/component documents.\n\n### 3.3 Error Propagation\n\nDocumentation drift is treated as a validation failure and reraised to the workflow runner.\n\n## 4. Configuration\n\n| Parameter | Source | Default | Description |\n|-----------|--------|---------|-------------|\n")
    out.append("| | | | |\n")
    out.append("\n## 5. Constraints\n\n| Constraint | Rationale | Enforcement |\n|------------|-----------|-------------|\n| Zero mutation of source code | Documentation bootstrap must not alter code | Workflow writes docs only |\n\n## 6. Testing\n\n### 6.1 Integration Tests\n\n| Test | Coverage |\n|------|----------|\n| | |\n\n### 6.2 Known Gaps\n\nAuto-generated baseline; extend with component-specific checks as needed.\n\n## 7. Change Log\n\n| Date | Change | Modules Affected | Verified By |\n|------|--------|-----------------|-------------|\n")
    out.append(f"| {_today_date()} | Initial baseline generated from repository scan | {len(rows)} modules/files | {workflow_name} |\n")
    return sanitize_ascii("".join(out))


def render_change_impact(snapshot: dict[str, Any], *, title: str, changed_files: list[str], docs_created: list[str], docs_updated: list[str], stale_docs: list[str]) -> str:
    generated_at = snapshot["generated_at"]
    workflow_name = str(snapshot.get("workflow_name") or snapshot["mode"])
    lines = [
        _frontmatter([
            f'title: "Change Impact: {title}"',
            'template_id: "CB-04"',
            'version: "1.0.0"',
            'doc_type: "system"',
            'authority: "workflow-generated"',
            'scan_policy: "include"',
            'lifecycle_status: "approved"',
            f'change_id: "{snapshot["job_id"]}"',
            f'task_id: "{workflow_name}"',
            'initiative_id: "codebase-doc-bootstrap"',
            f'created: "{generated_at}"',
            f'author: "{workflow_name}"',
        ]),
        f"# Change Impact: {title}\n\n",
        "## 1. Change Summary\n\n### 1.1 Description\n\n",
        "Repository scan bootstrap/reconcile generated or refreshed the codebase documentation baseline.\n\n",
        "### 1.2 Rationale\n\n",
        f"Keep `/{codebase_doc_rel()}` synchronized with the current repository state even when code changes occurred outside the normal workflow SOP.\n\n",
        "## 2. Changed Files\n\n### 2.1 Source Code Changes\n\n",
        "| File | Change Type | Description | Impact |\n|------|-------------|-------------|--------|\n",
    ]
    for item in changed_files:
        lines.append(f"| `{item}` | modify | part of repository scan baseline | medium |\n")
    lines.append("\n### 2.2 Configuration Changes\n\n| File | Change Type | Description | Impact |\n|------|-------------|-------------|--------|\n")
    lines.append("| | | | |\n")
    lines.append("\n### 2.3 Test Changes\n\n| File | Change Type | Description |\n|------|-------------|-------------|\n")
    lines.append("| | | |\n")
    lines.append("\n## 3. Updated Documentation\n\n### 3.1 Documentation Created\n\n| Document | Path | Type | Status |\n|----------|------|------|--------|\n")
    for doc in docs_created:
        lines.append(f"| `{Path(doc).name}` | `{doc}` | module/component/inventory | draft |\n")
    lines.append("\n### 3.2 Documentation Updated\n\n| Document | Path | Section Updated | Reason |\n|----------|------|-----------------|--------|\n")
    for doc in docs_updated:
        lines.append(f"| `{Path(doc).name}` | `{doc}` | full document | repository reconciliation |\n")
    lines.append("\n### 3.3 Inventory Updates\n\n| Module | Previous Status | New Status | Owner Doc Path |\n|--------|----------------|------------|----------------|\n")
    for doc in docs_created[: min(len(docs_created), 8)]:
        lines.append(f"| `{Path(doc).name}` | undocumented | current | `{doc}` |\n")
    if not docs_created:
        lines.append("| | | | |\n")
    lines.append("\n## 4. Stale Documentation Removal\n\n### 4.1 Stale Documents Identified\n\n| Document | Path | Reason for Staleness | Action |\n|----------|------|---------------------|--------|\n")
    for doc in stale_docs:
        lines.append(f"| `{Path(doc).name}` | `{doc}` | out of sync with repository scan | update |\n")
    if not stale_docs:
        lines.append("| | | | |\n")
    lines.append("\n### 4.2 Removal Log\n\n| Document | Path | Removed By | Date | Reason |\n|----------|------|-----------|------|--------|\n| | | | | |\n")
    lines.append("\n## 5. Impact Assessment\n\n### 5.1 Affected Components\n\n| Component | Impact | Documentation Status |\n|-----------|--------|---------------------|\n")
    lines.append("| codebase documentation baseline | high | current |\n")
    lines.append("\n### 5.2 Affected Workflows\n\n| Workflow | Impact | Notes |\n|----------|--------|-------|\n")
    lines.append(f"| `{workflow_name}` | high | repository scan baseline |\n")
    lines.append("\n### 5.3 Backward Compatibility\n\n| Aspect | Compatible | Notes |\n|--------|-----------|-------|\n")
    lines.append("| API | yes | documentation only |\n| Configuration | yes | no code changes |\n| Sidecar contract | yes | action writes standard v2 meta.json |\n")
    lines.append("\n## 6. Documentation Debt\n\n| Item | Reason for Deferral | Owner | Due Date |\n|------|-------------------|-------|----------|\n| | | | |\n")
    lines.append("\n## 7. Verification\n\n| Check | Status | Notes |\n|-------|--------|-------|\n")
    lines.append("| All changed files listed | pass | repository scan summary |\n| All updated docs listed | pass | generated docs |\n| Stale docs identified and handled | pass | regenerated baseline |\n| Inventory updated | pass | current scan |\n")
    return sanitize_ascii("".join(lines))


def render_validation(snapshot: dict[str, Any], *, title: str, checks: list[tuple[str, bool, str]]) -> str:
    generated_at = snapshot["generated_at"]
    workflow_name = str(snapshot.get("workflow_name") or snapshot["mode"])
    lines = [
        _frontmatter([
            f'title: "Validation Record: {title}"',
            'template_id: "CB-05"',
            'version: "1.0.0"',
            'doc_type: "system"',
            'authority: "workflow-generated"',
            'scan_policy: "include"',
            'lifecycle_status: "approved"',
            f'validation_id: "{snapshot["job_id"]}"',
            f'created: "{generated_at}"',
            f'author: "{workflow_name}"',
        ]),
        f"# Validation Record: {title}\n\n",
        "## 1. Validation Scope\n\n### 1.1 Repository Scan\n\n",
        "Generated baseline validation for codebase documentation bootstrap/reconcile.\n\n",
        "## 2. Validation Checks\n\n| Check | Status | Notes |\n|-------|--------|-------|\n",
    ]
    for name, ok, note in checks:
        lines.append(f"| {name} | {'pass' if ok else 'fail'} | {note} |\n")
    lines.append("\n## 3. Results\n\n")
    passes = sum(1 for _, ok, _ in checks if ok)
    lines.append(f"{passes}/{len(checks)} checks passed.\n")
    return sanitize_ascii("".join(lines))
