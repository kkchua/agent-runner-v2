"""Actions for sdlc_00_codebase_scaffold_v1 workflow.

Combined workflow: codebase sync + SDLC delivery scaffold generation.
Contains both publish actions from the original separate workflows.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _write_text(path: Path, content: str) -> None:
    """Write text content to a file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _update_frontmatter_fields(text: str, updates: dict[str, str]) -> str:
    """Update or insert fields in YAML frontmatter."""
    if not text.startswith("---\n"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    frontmatter = parts[1].strip("\n").splitlines()
    body = parts[2].lstrip("\n")
    field_map: dict[str, str] = {}
    order: list[str] = []
    for line in frontmatter:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key not in order:
            order.append(key)
        field_map[key] = value.strip()
    for key, value in updates.items():
        if key not in order:
            order.append(key)
        field_map[key] = json.dumps(value)
    rendered = ["---"]
    for key in order:
        rendered.append(f"{key}: {field_map[key]}")
    rendered.append("---")
    rendered.append("")
    rendered.append(body.rstrip())
    rendered.append("")
    return "\n".join(rendered)


def _update_managed_banner(text: str, *, workflow: str, step: str) -> str:
    """Replace the 'Managed by workflow' banner lines."""
    lines = text.splitlines()
    out: list[str] = []
    replaced_workflow = False
    replaced_protected = False
    for line in lines:
        if line.startswith("> Managed by workflow:"):
            out.append(f"> Managed by workflow: `{workflow}` / step: `{step}`")
            replaced_workflow = True
            continue
        if line.startswith("> This file is workflow-generated and protected from manual edits."):
            out.append("> This file is workflow-generated and protected from manual edits.")
            replaced_protected = True
            continue
        out.append(line)
    if not replaced_workflow:
        insert_at = 0
        if out and out[0] == "---":
            try:
                second_delim = out.index("---", 1)
                insert_at = second_delim + 1
                if insert_at < len(out) and out[insert_at] == "":
                    insert_at += 1
            except ValueError:
                insert_at = 0
        out[insert_at:insert_at] = [
            f"> Managed by workflow: `{workflow}` / step: `{step}`",
            "> This file is workflow-generated and protected from manual edits.",
            "",
        ]
    return "\n".join(out)


# ===========================================================================
# Codebase publish action
# ===========================================================================

# Subdirectories to copy from staging to current
CODEBASE_SUBDIRS = ("01_inventory", "02_modules", "03_components", "04_changes")


@action("publish_codebase_docs")
def publish_codebase_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Publish approved codebase docs to current/ and history/.

    Archives the previous current/ to history/<job_id>/, then copies
    staged docs from runs/<job_id>/ to current/.
    """
    del step_cfg
    job_id = str(state.get("job_id") or "SDLC00CS")
    step = str(state.get("current_step") or "publish_codebase_docs")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="CODEBASE_PUBLISH_MANIFEST_METAJSON",
        default_step=step,
    )

    # Resolve roots from context
    current_root_str = context.get("CODEBASE_CURRENT_ROOT", "")
    history_root_str = context.get("CODEBASE_HISTORY_ROOT", "")
    if not current_root_str or not history_root_str:
        return ActionResult(
            status="REJECTED",
            remark="CODEBASE_CURRENT_ROOT or CODEBASE_HISTORY_ROOT not found in context",
            reject_code="MISSING_CODEBASE_ROOT_CONTEXT",
        )
    current_root = Path(current_root_str)
    history_root = Path(history_root_str)

    # Resolve staging run root
    run_root = _resolve_codebase_run_root(state, project_root)
    if run_root is None:
        return ActionResult(
            status="REJECTED",
            remark="Could not resolve source run root from artifact paths",
            reject_code="SOURCE_RUN_ROOT_NOT_FOUND",
        )

    # Check for previous manifest to record supersedes
    previous_manifest_path = current_root / "codebase_manifest.json"
    previous_version = None
    if previous_manifest_path.exists():
        try:
            previous_version = json.loads(
                previous_manifest_path.read_text(encoding="utf-8")
            ).get("effective_version")
        except json.JSONDecodeError:
            previous_version = None

    # Archive current/ to history/<job_id>/
    if current_root.exists():
        history_root.mkdir(parents=True, exist_ok=True)
        for subdir in CODEBASE_SUBDIRS:
            src = current_root / subdir
            dst = history_root / subdir
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
        # Copy old manifest to history
        if previous_manifest_path.exists():
            _write_text(
                history_root / "codebase_manifest.json",
                previous_manifest_path.read_text(encoding="utf-8"),
            )

    # Copy staged docs from runs/<job_id>/ to current/
    published_files: dict[str, str] = {}
    for subdir in CODEBASE_SUBDIRS:
        src_dir = run_root / subdir
        dst_dir = current_root / subdir
        if not src_dir.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src_file in src_dir.rglob("*.md"):
            rel = src_file.relative_to(src_dir)
            dst_file = dst_dir / rel
            _write_text(dst_file, src_file.read_text(encoding="utf-8"))
            key = f"CODEBASE_{subdir.upper()}_{src_file.stem.upper()}"
            published_files[key] = str(dst_file.relative_to(project_root)).replace(
                "\\", "/"
            )

    # Write manifest
    manifest = {
        "workflow_id": "sdlc_00_codebase_scaffold_v1",
        "workflow_layer": "layer3",
        "platform": "agent-runner-v2",
        "change_or_run_id": job_id,
        "change_class": "codebase_sync",
        "artifact_inventory": published_files,
        "artifact_permanence_class": "permanent",
        "authority": "workflow-generated",
        "lifecycle_status": "published",
        "source_step": step,
        "published_timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "effective_version": job_id,
        "active_set": True,
        "supersedes": previous_version,
        "superseded_by": None,
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    current_manifest = current_root / "codebase_manifest.json"
    history_manifest = history_root / "codebase_manifest.json"
    _write_text(current_manifest, manifest_text)
    _write_text(history_manifest, manifest_text)

    artifacts = {
        "CODEBASE_PUBLISH_MANIFEST": str(current_manifest.relative_to(project_root)).replace("\\", "/"),
        "CODEBASE_PUBLISH_MANIFEST_HISTORY": str(history_manifest.relative_to(project_root)).replace("\\", "/"),
    }
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Codebase docs published ({len(published_files)} files) to codebase/current/.",
            artifacts=artifacts,
        )
    return ActionResult(
        status="APPROVED",
        remark=f"Codebase docs published ({len(published_files)} files) to codebase/current/.",
        artifacts=artifacts,
    )


def _resolve_codebase_run_root(state: dict, project_root: Path) -> Path | None:
    """Construct the codebase run root deterministically from job_id."""
    job_id = str(state.get("job_id") or "").strip()
    if not job_id:
        return None
    run_root = project_root / "docs" / "repo" / "codebase" / "runs" / job_id
    return run_root if run_root.exists() else None


# ===========================================================================
# Scaffold publish action
# ===========================================================================

# Scaffold artifact registry: (artifact_key, filename, subdirectory)
SCAFFOLD_ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    # Templates (01_templates/)
    ("SDLC_TEMPLATE_REGISTRY", "template_registry.md", "01_templates"),
    ("SDLC_WORKFLOW_SOP", "WORKFLOW_SOP_v1.md", "01_templates"),
    ("SDLC_TEMPLATE_DRAFT_INIT", "01_DRAFT_INIT_template.md", "01_templates"),
    ("SDLC_TEMPLATE_INIT", "02_INIT_template.md", "01_templates"),
    ("SDLC_TEMPLATE_REQ", "03_REQ_template.md", "01_templates"),
    ("SDLC_TEMPLATE_PLAN", "04_PLAN_template.md", "01_templates"),
    ("SDLC_TEMPLATE_BACKLOG", "05_BACKLOG_template.md", "01_templates"),
    ("SDLC_TEMPLATE_TASK", "06_TASK_template.md", "01_templates"),
    ("SDLC_TEMPLATE_IMPL", "07_IMPL_template.md", "01_templates"),
    ("SDLC_TEMPLATE_VALID", "08_VALID_template.md", "01_templates"),
    ("SDLC_TEMPLATE_REV", "09_REV_template.md", "01_templates"),
    ("SDLC_TEMPLATE_MEM", "10_MEM_template.md", "01_templates"),
    ("SDLC_TEMPLATE_CLOSE", "11_CLOSE_template.md", "01_templates"),
    # Agent contracts (02_agents/)
    ("SDLC_AGENTS_INDEX", "AGENTS.md", "02_agents"),
    ("SDLC_AGENT_PLANNER", "AGENT-planner.md", "02_agents"),
    ("SDLC_AGENT_TASK_DECOMPOSER", "AGENT-task-decomposer.md", "02_agents"),
    ("SDLC_AGENT_IMPL_PLANNER", "AGENT-implementation-planner.md", "02_agents"),
    ("SDLC_AGENT_EXECUTOR", "AGENT-executor.md", "02_agents"),
    ("SDLC_AGENT_REVIEWER", "AGENT-reviewer.md", "02_agents"),
    ("SDLC_AGENT_MEMORY_MANAGER", "AGENT-memory-manager.md", "02_agents"),
    ("SDLC_DELIVERY_STATUS_RULES", "DELIVERY_STATUS_RULES_v1.md", "02_agents"),
)


@action("publish_sdlc_scaffold")
def publish_sdlc_scaffold(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Publish approved SDLC scaffold to current/ and history/."""
    del step_cfg
    job_id = str(state.get("job_id") or "SDLC00CS")
    step = str(state.get("current_step") or "publish_sdlc_scaffold")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="SDLC_SCAFFOLD_PUBLISH_MANIFEST_METAJSON",
        default_step=step,
    )

    # Resolve roots from context (set by context_extensions.py)
    current_root_str = context.get("SDLC_CURRENT_ROOT", "")
    history_root_str = context.get("SDLC_HISTORY_ROOT", "")
    if not current_root_str or not history_root_str:
        return ActionResult(
            status="REJECTED",
            remark="SDLC_CURRENT_ROOT or SDLC_HISTORY_ROOT not found in context",
            reject_code="MISSING_SDLC_ROOT_CONTEXT",
        )
    current_root = Path(current_root_str)
    history_root = Path(history_root_str)
    current_root.mkdir(parents=True, exist_ok=True)
    history_root.mkdir(parents=True, exist_ok=True)

    # Check for previous manifest to record supersedes
    previous_manifest_path = current_root / "sdlc_scaffold_manifest.json"
    previous_version = None
    if previous_manifest_path.exists():
        try:
            previous_version = json.loads(
                previous_manifest_path.read_text(encoding="utf-8")
            ).get("effective_version")
        except json.JSONDecodeError:
            previous_version = None

    # Resolve source run root from any known artifact path
    run_root = _resolve_scaffold_run_root(context, state, project_root)
    if run_root is None:
        return ActionResult(
            status="REJECTED",
            remark="Could not resolve source run root from artifact paths",
            reject_code="SOURCE_RUN_ROOT_NOT_FOUND",
        )

    published_files: dict[str, str] = {}
    for artifact_key, filename, subdir in SCAFFOLD_ARTIFACTS:
        src_path = run_root / subdir / filename
        if not src_path.exists():
            return ActionResult(
                status="REJECTED",
                remark=f"Source file not found: {src_path}",
                reject_code="SCAFFOLD_SOURCE_MISSING",
            )
        text = _update_frontmatter_fields(
            _read_text(src_path),
            {
                "authority": "sdlc-owned",
                "lifecycle_status": "published",
                "effective_version": job_id,
            },
        )
        text = _update_managed_banner(
            text,
            workflow="sdlc_00_codebase_scaffold_v1",
            step=step,
        )
        current_path = current_root / subdir / filename
        history_path = history_root / subdir / filename
        _write_text(current_path, text)
        _write_text(history_path, text)
        published_files[artifact_key] = str(
            current_path.relative_to(project_root)
        ).replace("\\", "/")

    # Write manifest
    manifest = {
        "workflow_id": "sdlc_00_codebase_scaffold_v1",
        "workflow_layer": "layer3",
        "platform": "agent-runner-v2",
        "change_or_run_id": job_id,
        "change_class": "scaffold_publish",
        "artifact_inventory": published_files,
        "artifact_permanence_class": "permanent",
        "authority": "sdlc-owned",
        "lifecycle_status": "published",
        "source_step": step,
        "published_timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "effective_version": job_id,
        "active_set": True,
        "supersedes": previous_version,
        "superseded_by": None,
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    current_manifest = current_root / "sdlc_scaffold_manifest.json"
    history_manifest = history_root / "sdlc_scaffold_manifest.json"
    _write_text(current_manifest, manifest_text)
    _write_text(history_manifest, manifest_text)

    artifacts = {
        "SDLC_SCAFFOLD_PUBLISH_MANIFEST": str(
            current_manifest.relative_to(project_root)
        ).replace("\\", "/"),
        "SDLC_SCAFFOLD_PUBLISH_MANIFEST_HISTORY": str(
            history_manifest.relative_to(project_root)
        ).replace("\\", "/"),
    }
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"SDLC scaffold published ({len(published_files)} files) to sdlc/current/.",
            artifacts=artifacts,
        )
    return ActionResult(
        status="APPROVED",
        remark=f"SDLC scaffold published ({len(published_files)} files) to sdlc/current/.",
        artifacts=artifacts,
    )


def _resolve_scaffold_run_root(
    context: dict, state: dict, project_root: Path
) -> Path | None:
    """Derive the scaffold run root from any known scaffold artifact path."""
    artifacts_state = state.get("artifacts") or {}
    for artifact_key, _, _ in SCAFFOLD_ARTIFACTS:
        path_str = artifacts_state.get(artifact_key) or context.get(artifact_key, "")
        if path_str:
            p = Path(path_str)
            if not p.is_absolute():
                p = project_root / p
            # Walk up to find the run root (parent of 01_templates/ or 02_agents/)
            if p.parent.name in ("01_templates", "02_agents"):
                return p.parent.parent
    return None
