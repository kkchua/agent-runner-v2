#!/usr/bin/env python3
from __future__ import annotations

"""
actions/sync_system_docs.py - Bootstrap or reconcile audience-oriented system documentation.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..doc_paths import codebase_doc_rel, system_doc_rel
from ..codebase_docs import build_snapshot
from ..system_docs import (
    render_bundle_migration_plan,
    render_bundle_taxonomy,
    render_business_capabilities,
    render_component_architecture,
    render_decision_log,
    render_developer_guide,
    render_documentation_standard,
    render_functional_spec,
    render_nfr,
    render_runbook,
    render_system_context,
    render_system_docs_change_log,
    render_system_file_structure,
    render_system_index,
    render_system_overview,
)
from ..runtime_context import write_meta_sidecar


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _architecture_profile_from_project_analysis(project_root: Path) -> dict[str, str]:
    analysis_path = project_root / codebase_doc_rel("00_analysis/PROJECT_ANALYSIS.md")
    if not analysis_path.exists():
        return {}
    text = analysis_path.read_text(encoding="utf-8")
    patterns = {
        "architecture_profile": r"^Current Profile:\s*(.+)$",
        "architecture_target_profile": r"^Target Profile:\s*(.+)$",
        "architecture_migration_mode": r"^Migration Mode:\s*(.+)$",
        "architecture_baseline": r"^Baseline:\s*(.+)$",
    }
    result: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            result[key] = match.group(1).strip()
    if "architecture_profile" not in result:
        result["architecture_profile"] = "provisional"
    if "architecture_target_profile" not in result:
        result["architecture_target_profile"] = "repo-selected"
    if "architecture_migration_mode" not in result:
        result["architecture_migration_mode"] = "targeted_migration"
    if "architecture_baseline" not in result:
        result["architecture_baseline"] = "universal baseline"
    result["architecture_profile_source"] = codebase_doc_rel("00_analysis/PROJECT_ANALYSIS.md")
    return result


def sync_system_docs(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "bootstrap")
    job_id = str(state.get("job_id") or "system-docs")
    step = str(state.get("current_step") or "generate_system_docs")
    meta_rel = context.get("SYSTEM_DOCS_INDEX_METAJSON", "")
    snapshot = build_snapshot(
        project_root,
        mode=mode,
        job_id=job_id,
        step=step,
        workflow_name=str(state.get("template_group") or mode),
    )
    snapshot.update(_architecture_profile_from_project_analysis(project_root))
    repo_name = project_root.name or "repository"

    docs_to_write = {
        system_doc_rel("README.md"): render_system_index(snapshot, repo_name=repo_name),
        system_doc_rel("DOCUMENTATION_STANDARD.md"): render_documentation_standard(snapshot),
        system_doc_rel("BUNDLE_TAXONOMY.md"): render_bundle_taxonomy(snapshot),
        system_doc_rel("BUNDLE_MIGRATION_PLAN.md"): render_bundle_migration_plan(snapshot),
        system_doc_rel("SYSTEM_OVERVIEW.md"): render_system_overview(snapshot, repo_name=repo_name),
        system_doc_rel("BUSINESS_CAPABILITIES.md"): render_business_capabilities(snapshot),
        system_doc_rel("FUNCTIONAL_SPEC.md"): render_functional_spec(snapshot, repo_name=repo_name),
        system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md"): render_nfr(snapshot),
        system_doc_rel("SYSTEM_CONTEXT.md"): render_system_context(snapshot, repo_name=repo_name),
        system_doc_rel("COMPONENT_ARCHITECTURE.md"): render_component_architecture(snapshot),
        system_doc_rel("DECISION_LOG.md"): render_decision_log(snapshot),
        system_doc_rel("SYSTEM_FILE_STRUCTURE.md"): render_system_file_structure(snapshot),
        system_doc_rel("DEVELOPER_GUIDE.md"): render_developer_guide(snapshot),
        system_doc_rel("RUNBOOK.md"): render_runbook(snapshot),
    }

    doc_paths = list(docs_to_write.keys())
    for rel_path, content in docs_to_write.items():
        _write_text(project_root / rel_path, content)

    change_log_path = project_root / system_doc_rel(f"{job_id}-{mode}-change-log.md")
    _write_text(change_log_path, render_system_docs_change_log(snapshot, repo_name=repo_name, doc_paths=doc_paths))

    artifacts = {
        "SYSTEM_DOCS_INDEX": system_doc_rel("README.md"),
        "SYSTEM_DOCS_CHANGE_LOG": change_log_path.relative_to(project_root).as_posix(),
    }
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark=f"System docs {mode} completed.", artifacts=artifacts)

    return ActionResult(
        status="APPROVED",
        remark=f"System docs {mode} completed for {repo_name}.",
        artifacts=artifacts,
    )
