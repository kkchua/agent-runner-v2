#!/usr/bin/env python3
from __future__ import annotations

"""
actions/sync_codebase_docs.py — Bootstrap or reconcile docs/codebase from the current repo tree.
"""

import json
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..doc_paths import codebase_doc_rel
from ..codebase_docs import (
    build_snapshot,
    render_change_impact,
    render_component_doc,
    render_inventory,
    render_module_doc,
)
from ..runtime_context import write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _component_specs(snapshot: dict, project_root: Path, *, base_rel: str = "") -> list[dict[str, object]]:
    """Build component doc specs.

    Args:
        snapshot: The codebase snapshot dict.
        project_root: The project root path.
        base_rel: Optional base path override for staging (e.g. "docs/repo/codebase/runs/<job_id>").
                  When empty, uses the default codebase_doc_rel() paths.
    """
    python_modules = snapshot["python_modules"]
    module_paths = [m["rel_path"] for m in python_modules]
    action_modules = [m for m in module_paths if m.startswith("agent_runner_v2/actions/")]
    workflow_modules = [m for m in module_paths if m in {"agent_runner_v2/run_agent.py", "agent_runner_v2/step_runner.py", "agent_runner_v2/workflow_router.py", "agent_runner_v2/bundle_loader.py"}]
    tests = [item.rel_path for item in snapshot["items"] if item.category == "test files"]
    scripts = [item.rel_path for item in snapshot["items"] if item.category == "scripts"]
    config = [item.rel_path for item in snapshot["items"] if item.category == "configuration/data files"]
    docs = [
        item.rel_path
        for item in snapshot["items"]
        if item.category == "documentation files"
        and not item.rel_path.startswith(codebase_doc_rel("02_modules"))
        and not item.rel_path.startswith(codebase_doc_rel("03_components"))
        and not item.rel_path.startswith(codebase_doc_rel("04_changes"))
    ]

    def _path(subpath: str) -> str:
        """Build output path using base_rel or default codebase_doc_rel."""
        if base_rel:
            return f"{base_rel}/{subpath}"
        return codebase_doc_rel(subpath)

    return [
        {
            "name": "workflow families",
            "path": _path("03_components/workflow-families.md"),
            "overview": "Repository workflow families, their step sequences, and their current bootstrap/runtime contracts.",
            "modules": workflow_modules,
            "rows": [
                {"module": family["family_name"], "role": f"{family['job_prefix']} / {len(family['steps'])} steps"}
                for family in snapshot["workflow_families"]
            ],
        },
        {
            "name": "actions package",
            "path": _path("03_components/actions-package.md"),
            "overview": "Deterministic action modules that implement non-coder steps and their I/O contracts.",
            "modules": action_modules,
            "rows": [{"module": module, "role": "deterministic runner action"} for module in action_modules],
        },
        {
            "name": "tests suite",
            "path": _path("03_components/tests-suite.md"),
            "overview": "Repository test suite coverage grouped as a single logical component.",
            "modules": tests,
            "rows": [{"module": test, "role": "test coverage"} for test in tests],
        },
        {
            "name": "scripts suite",
            "path": _path("03_components/scripts-suite.md"),
            "overview": "Shell and batch scripts used to run and operate the repository workflows.",
            "modules": scripts,
            "rows": [{"module": script, "role": "automation / entrypoint"} for script in scripts],
        },
        {
            "name": "config and data",
            "path": _path("03_components/config-and-data.md"),
            "overview": "Configuration and structured data files that define runtime and documentation behavior.",
            "modules": config,
            "rows": [{"module": cfg, "role": "configuration / structured data"} for cfg in config],
        },
        {
            "name": "codebase governance",
            "path": _path("03_components/codebase-governance.md"),
            "overview": "The codebase documentation standards, templates, inventory, and validation rules that govern `/docs/codebase`.",
            "modules": docs,
            "rows": [{"module": doc, "role": "documentation artifact"} for doc in docs],
        },
    ]


def sync_codebase_docs(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "reconcile")
    job_id = str(state.get("job_id") or "codebase-scan")
    step = str(state.get("current_step") or "scan_codebase")
    meta_rel = context.get("CODEBASE_CHANGE_IMPACT_METAJSON", "")

    # Support staging root override (for sdlc_00_codebase_v1 staging pattern)
    staging_root = str(step_cfg.get("staging_root") or "")
    if staging_root:
        # Resolve {job_id} placeholder
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
    repo_name = project_root.name or "repository"

    inventory_path = project_root / f"{base_rel}/01_inventory/codebase_inventory.md"
    module_dir = project_root / f"{base_rel}/02_modules"
    component_dir = project_root / f"{base_rel}/03_components"
    change_dir = project_root / f"{base_rel}/04_changes"
    for folder in (inventory_path.parent, module_dir, component_dir, change_dir):
        folder.mkdir(parents=True, exist_ok=True)

    inventory_content = render_inventory(snapshot, title=repo_name)
    all_doc_paths: list[str] = []

    # Track created vs updated based on whether file existed before writing
    docs_created: list[str] = []
    docs_updated: list[str] = []

    inv_rel = inventory_path.relative_to(project_root).as_posix()
    all_doc_paths.append(inv_rel)
    if not inventory_path.exists():
        docs_created.append(inv_rel)
    else:
        docs_updated.append(inv_rel)
    _write_text(inventory_path, inventory_content)

    changed_files: list[str] = [item.rel_path for item in snapshot["items"] if item.category in {"python modules", "bootstrap workflow files", "configuration/data files", "scripts", "test files", "documentation files"}]
    for module_record in snapshot["python_modules"]:
        doc_path = module_dir / Path(module_record["owner_doc_path"]).name
        doc_rel = doc_path.relative_to(project_root).as_posix()
        all_doc_paths.append(doc_rel)
        if not doc_path.exists():
            docs_created.append(doc_rel)
        else:
            docs_updated.append(doc_rel)
        _write_text(doc_path, render_module_doc(snapshot, module_record))

    component_docs: list[str] = []
    for spec in _component_specs(snapshot, project_root, base_rel=base_rel):
        component_doc_path = project_root / str(spec["path"])
        doc_rel = component_doc_path.relative_to(project_root).as_posix()
        component_docs.append(doc_rel)
        all_doc_paths.append(doc_rel)
        if not component_doc_path.exists():
            docs_created.append(doc_rel)
        else:
            docs_updated.append(doc_rel)
        overview = str(spec["overview"])
        rows = list(spec["rows"])  # type: ignore[arg-type]
        _write_text(component_doc_path, render_component_doc(snapshot, component_name=str(spec["name"]), rows=rows, overview=overview))

    change_id = f"{job_id}-{mode}"
    change_path = change_dir / f"{change_id}.md"
    change_content = render_change_impact(
        snapshot,
        title=f"{repo_name} codebase {mode}",
        changed_files=changed_files,
        docs_created=docs_created,
        docs_updated=docs_updated,
        stale_docs=[],
    )
    _write_text(change_path, change_content)
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark=f"Codebase docs {mode} completed.", artifacts={"CODEBASE_CHANGE_IMPACT": change_path.relative_to(project_root).as_posix(), "CODEBASE_INVENTORY": inventory_path.relative_to(project_root).as_posix()})

    return ActionResult(
        status="APPROVED",
        remark=f"Codebase docs {mode} completed for {repo_name}.",
        artifacts={
            "CODEBASE_CHANGE_IMPACT": change_path.relative_to(project_root).as_posix(),
            "CODEBASE_INVENTORY": inventory_path.relative_to(project_root).as_posix(),
        },
    )
