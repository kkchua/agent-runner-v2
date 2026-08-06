"""Custom actions for codebase_to_meta_v1 workflow.

Provides four action-driven steps:
- scan_audiences: Discover and index audience definition files
- validate_meta: Structurally validate generated meta content files
- create_meta_backup: Backup current/ meta content before publishing
- publish_meta: Publish staged meta content to current/ directory
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action


def _write_text(path: Path, content: str) -> None:
    """Write text content to a file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse YAML frontmatter from a Markdown file.

    Returns a dict of frontmatter fields, or empty dict if no valid
    frontmatter is found.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm_text = text[3:end].strip()
    result: dict[str, Any] = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Remove surrounding quotes
        if value and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        # Try to parse as int
        try:
            result[key] = int(value)
        except (ValueError, TypeError):
            # Try to parse as list
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                result[key] = [
                    item.strip().strip("'\"")
                    for item in inner.split(",")
                    if item.strip()
                ]
            else:
                result[key] = value
    return result


def _resolve_run_root(state: dict, project_root: Path) -> Path | None:
    """Construct the run root deterministically from job_id."""
    job_id = str(state.get("job_id") or "").strip()
    if not job_id:
        return None
    run_root = project_root / "docs" / "repo" / "meta_content" / "runs" / job_id
    return run_root if run_root.exists() else None


# ============================================================================
# Action 1: scan_audiences
# ============================================================================

@action("scan_audiences")
def scan_audiences(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Discover and index audience definition files from the audiences/ directory.

    Scans the workflow package's audiences/ directory for .md files. Parses
    each file's YAML frontmatter to extract audience_id, label, tone,
    focus_areas, exclude, and section_structure. Writes a JSON index mapping
    each audience_id to its parsed metadata and definition file path.
    """
    del step_cfg
    job_id = str(state.get("job_id") or "META")
    step = str(state.get("current_step") or "scan_audiences")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="AUDIENCE_INDEX_METAJSON",
        default_step=step,
    )

    # Resolve audiences root
    audiences_root_str = context.get("AUDIENCES_ROOT", "")
    if not audiences_root_str:
        # Fall back to workflow package path
        audiences_root = project_root / "workflows" / "codebase_to_meta_v1" / "audiences"
    else:
        audiences_root = Path(audiences_root_str)

    if not audiences_root.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Audiences directory not found: {audiences_root}",
            artifacts={},
            reject_code="AUDIENCES_DIR_NOT_FOUND",
        )

    # Scan for .md files
    audience_index: dict[str, Any] = {}
    md_files = sorted(audiences_root.glob("*.md"))

    if not md_files:
        return ActionResult(
            status="REJECTED",
            remark=f"No audience definition .md files found in {audiences_root}",
            artifacts={},
            reject_code="NO_AUDIENCE_FILES",
        )

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)

        audience_id = fm.get("audience_id", md_file.stem)
        if not audience_id:
            continue

        # Extract body text (everything after frontmatter)
        body_start = text.find("---", 3)
        body_text = text[body_start + 3:].strip() if body_start != -1 else ""

        audience_index[audience_id] = {
            "audience_id": audience_id,
            "label": fm.get("label", audience_id),
            "tone": fm.get("tone", "neutral"),
            "focus_areas": fm.get("focus_areas", []),
            "exclude": fm.get("exclude", []),
            "section_structure": fm.get("section_structure", []),
            "definition_path": str(md_file),
            "body_text": body_text,
        }

    # Write audience index JSON
    run_root = project_root / "docs" / "repo" / "meta_content" / "runs" / job_id
    run_root.mkdir(parents=True, exist_ok=True)
    index_path = run_root / "audience_index.json"
    _write_text(index_path, json.dumps(audience_index, indent=2) + "\n")

    artifacts = {
        "AUDIENCE_INDEX": str(index_path),
    }

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Discovered {len(audience_index)} audience definitions.",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Discovered {len(audience_index)} audience definitions.",
        artifacts=artifacts,
    )


# ============================================================================
# Action 2: validate_meta
# ============================================================================

@action("validate_meta")
def validate_meta(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Structurally validate all generated meta content files.

    Checks each meta content file for:
    - Valid YAML frontmatter with required fields
    - Audience ID matches AUDIENCE_INDEX
    - Section structure matches audience definition
    - Valid UTF-8 encoding
    """
    del step_cfg
    job_id = str(state.get("job_id") or "META")
    step = str(state.get("current_step") or "validate_meta")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="VALIDATION_FILE_METAJSON",
        default_step=step,
    )

    # Resolve artifact paths
    artifacts = state.get("artifacts", {})
    meta_index_path = artifacts.get("META_INDEX", context.get("META_INDEX", ""))
    audience_index_path = artifacts.get("AUDIENCE_INDEX", context.get("AUDIENCE_INDEX", ""))

    if not meta_index_path or not audience_index_path:
        return ActionResult(
            status="REJECTED",
            remark="META_INDEX or AUDIENCE_INDEX path not available",
            artifacts={},
            reject_code="MISSING_ARTIFACT_PATHS",
        )

    meta_index_file = Path(meta_index_path)
    audience_index_file = Path(audience_index_path)

    if not meta_index_file.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"META_INDEX file not found: {meta_index_file}",
            artifacts={},
            reject_code="META_INDEX_NOT_FOUND",
        )

    if not audience_index_file.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"AUDIENCE_INDEX file not found: {audience_index_file}",
            artifacts={},
            reject_code="AUDIENCE_INDEX_NOT_FOUND",
        )

    # Load indexes
    meta_index = json.loads(meta_index_file.read_text(encoding="utf-8"))
    audience_index = json.loads(audience_index_file.read_text(encoding="utf-8"))

    # Required frontmatter fields
    required_fm_fields = [
        "title", "audience", "audience_label",
        "generated_date", "source_version", "section_count",
    ]

    # Validation results
    results: list[dict[str, str]] = []
    all_pass = True

    for audience_id, entry in meta_index.items():
        file_path = entry.get("file", "")
        if not file_path:
            results.append({
                "file": audience_id,
                "check": "file_path",
                "result": "FAIL",
                "detail": "No file path in meta index",
            })
            all_pass = False
            continue

        fp = Path(file_path)
        if not fp.exists():
            results.append({
                "file": fp.name,
                "check": "file_exists",
                "result": "FAIL",
                "detail": f"File not found: {fp}",
            })
            all_pass = False
            continue

        # Read file
        try:
            text = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            results.append({
                "file": fp.name,
                "check": "utf8_encoding",
                "result": "FAIL",
                "detail": "File is not valid UTF-8",
            })
            all_pass = False
            continue

        results.append({
            "file": fp.name,
            "check": "utf8_encoding",
            "result": "PASS",
            "detail": "",
        })

        # Check frontmatter
        fm = _parse_frontmatter(text)
        for field in required_fm_fields:
            if field in fm:
                results.append({
                    "file": fp.name,
                    "check": f"frontmatter.{field}",
                    "result": "PASS",
                    "detail": "",
                })
            else:
                results.append({
                    "file": fp.name,
                    "check": f"frontmatter.{field}",
                    "result": "FAIL",
                    "detail": f"Missing required field: {field}",
                })
                all_pass = False

        # Check audience ID match
        fm_audience = fm.get("audience", "")
        if fm_audience == audience_id:
            results.append({
                "file": fp.name,
                "check": "audience_id_match",
                "result": "PASS",
                "detail": "",
            })
        else:
            results.append({
                "file": fp.name,
                "check": "audience_id_match",
                "result": "FAIL",
                "detail": f"Expected '{audience_id}', got '{fm_audience}'",
            })
            all_pass = False

        # Check audience exists in AUDIENCE_INDEX
        if audience_id in audience_index:
            results.append({
                "file": fp.name,
                "check": "audience_in_index",
                "result": "PASS",
                "detail": "",
            })

            # Check section structure
            expected_sections = audience_index[audience_id].get("section_structure", [])
            if expected_sections:
                # Extract section headings from file (lines starting with ##)
                actual_sections = [
                    line.lstrip("#").strip()
                    for line in text.splitlines()
                    if line.startswith("## ")
                ]
                missing = [
                    s for s in expected_sections
                    if s not in actual_sections
                ]
                if not missing:
                    results.append({
                        "file": fp.name,
                        "check": "section_structure",
                        "result": "PASS",
                        "detail": "",
                    })
                else:
                    results.append({
                        "file": fp.name,
                        "check": "section_structure",
                        "result": "FAIL",
                        "detail": f"Missing sections: {', '.join(missing)}",
                    })
                    all_pass = False
        else:
            results.append({
                "file": fp.name,
                "check": "audience_in_index",
                "result": "FAIL",
                "detail": f"Audience '{audience_id}' not in AUDIENCE_INDEX",
            })
            all_pass = False

    # Write validation report
    run_root = project_root / "docs" / "repo" / "meta_content" / "runs" / job_id
    run_root.mkdir(parents=True, exist_ok=True)
    validation_path = run_root / f"{job_id}-validation.md"

    report_lines = [
        "---",
        f"title: \"Meta Content Validation Report -- {job_id}\"",
        "doc_type: \"validation_report\"",
        f"generated_date: \"{datetime.now().strftime('%Y-%m-%d')}\"",
        f"source_version: \"{job_id}\"",
        "---",
        "",
        "# Meta Content Validation Report",
        "",
        f"Job ID: {job_id}",
        f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Overall Result: {'PASS' if all_pass else 'FAIL'}",
        "",
        "## Validation Results",
        "",
        "| File | Check | Result | Detail |",
        "|------|-------|--------|--------|",
    ]
    for r in results:
        report_lines.append(
            f"| {r['file']} | {r['check']} | {r['result']} | {r['detail']} |"
        )

    _write_text(validation_path, "\n".join(report_lines) + "\n")

    status = "APPROVED" if all_pass else "REJECTED"
    remark = (
        f"All {len(meta_index)} meta files passed validation."
        if all_pass
        else "Validation failed -- see report for details."
    )

    artifacts_out = {
        "VALIDATION_FILE": str(validation_path),
    }

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status=status,
            remark=remark,
            artifacts=artifacts_out,
        )

    return ActionResult(
        status=status,
        remark=remark,
        artifacts=artifacts_out,
        reject_code=None if all_pass else "VALIDATION_FAILED",
    )


# ============================================================================
# Action 3: create_meta_backup
# ============================================================================

@action("create_meta_backup")
def create_meta_backup(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Create a backup of current/ meta content before publishing.

    Copies docs/repo/meta_content/current/ to
    docs/repo/meta_content/backups/BACKUP-{timestamp}/.
    Handles first-run gracefully when current/ does not exist.
    """
    del step_cfg
    step = str(state.get("current_step") or "create_meta_backup")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="META_BACKUP_METAJSON",
        default_step=step,
    )

    meta_content_root = project_root / "docs" / "repo" / "meta_content"
    current_root = meta_content_root / "current"
    backups_root = meta_content_root / "backups"

    # First run: current/ does not exist
    if not current_root.exists():
        artifacts = {"META_BACKUP": ""}
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="APPROVED",
                remark="First run -- no current/ directory to back up.",
                artifacts=artifacts,
            )
        return ActionResult(
            status="APPROVED",
            remark="First run -- no current/ directory to back up.",
            artifacts=artifacts,
        )

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = backups_root / f"BACKUP-{timestamp}"
    backups_root.mkdir(parents=True, exist_ok=True)

    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    shutil.copytree(current_root, backup_dir)

    artifacts = {
        "META_BACKUP": str(backup_dir),
    }

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Backed up current/ to {backup_dir.name}.",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Backed up current/ to {backup_dir.name}.",
        artifacts=artifacts,
    )


# ============================================================================
# Action 4: publish_meta
# ============================================================================

@action("publish_meta")
def publish_meta(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Publish staged meta content to current/ and archive to history/.

    Two-phase publish:
    1. Archive existing current/ to history/<job_id>/
    2. Copy staged audience meta files from runs/<job_id>/ to current/
    3. Write meta_manifest.json to both current/ and history/
    """
    del step_cfg
    job_id = str(state.get("job_id") or "META")
    step = str(state.get("current_step") or "publish_meta")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="META_MANIFEST_METAJSON",
        default_step=step,
    )

    meta_content_root = project_root / "docs" / "repo" / "meta_content"
    current_root = meta_content_root / "current"
    history_root = meta_content_root / "history" / job_id
    run_root = project_root / "docs" / "repo" / "meta_content" / "runs" / job_id

    # Resolve artifact paths
    artifacts = state.get("artifacts", {})
    meta_index_path = artifacts.get("META_INDEX", context.get("META_INDEX", ""))
    audience_index_path = artifacts.get("AUDIENCE_INDEX", context.get("AUDIENCE_INDEX", ""))

    if not meta_index_path or not audience_index_path:
        return ActionResult(
            status="REJECTED",
            remark="META_INDEX or AUDIENCE_INDEX path not available",
            artifacts={},
            reject_code="MISSING_ARTIFACT_PATHS",
        )

    meta_index_file = Path(meta_index_path)
    audience_index_file = Path(audience_index_path)

    if not meta_index_file.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"META_INDEX file not found: {meta_index_file}",
            artifacts={},
            reject_code="META_INDEX_NOT_FOUND",
        )

    if not audience_index_file.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"AUDIENCE_INDEX file not found: {audience_index_file}",
            artifacts={},
            reject_code="AUDIENCE_INDEX_NOT_FOUND",
        )

    # Load indexes
    meta_index = json.loads(meta_index_file.read_text(encoding="utf-8"))
    audience_index = json.loads(audience_index_file.read_text(encoding="utf-8"))

    # Check for previous manifest to record supersedes
    previous_manifest_path = current_root / "meta_manifest.json"
    supersedes = None
    if previous_manifest_path.exists():
        try:
            prev = json.loads(
                previous_manifest_path.read_text(encoding="utf-8")
            )
            supersedes = prev.get("change_or_run_id")
        except (json.JSONDecodeError, OSError):
            supersedes = None

    # Phase 1: Archive existing current/ to history/<job_id>/
    if current_root.exists():
        history_root.mkdir(parents=True, exist_ok=True)
        # Copy existing files to history
        for item in current_root.iterdir():
            dst = history_root / item.name
            if item.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)

    # Phase 2: Copy staged meta files to current/
    current_root.mkdir(parents=True, exist_ok=True)
    published_files: dict[str, dict[str, str]] = {}

    for audience_id, entry in meta_index.items():
        file_path_str = entry.get("file", "")
        if not file_path_str:
            continue
        src_file = Path(file_path_str)
        if not src_file.exists():
            continue
        dst_file = current_root / src_file.name
        _write_text(dst_file, src_file.read_text(encoding="utf-8"))

        audience_info = audience_index.get(audience_id, {})
        published_files[audience_id] = {
            "label": audience_info.get("label", audience_id),
            "file": src_file.name,
            "generated_date": entry.get("generated_date", ""),
        }

    # Also copy the meta_index.json and audience_index.json to current/
    for index_name in ["meta_index.json", "audience_index.json"]:
        src = run_root / index_name
        if src.exists():
            _write_text(
                current_root / index_name,
                src.read_text(encoding="utf-8"),
            )

    # Write manifest
    manifest = {
        "workflow_id": "codebase_to_meta_v1",
        "change_or_run_id": job_id,
        "source_codebase_version": context.get("CODEBASE_MANIFEST", ""),
        "audiences": published_files,
        "published_timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "supersedes": supersedes,
        "active_set": True,
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"

    current_manifest = current_root / "meta_manifest.json"
    _write_text(current_manifest, manifest_text)

    # Also write to history/
    history_root.mkdir(parents=True, exist_ok=True)
    history_manifest = history_root / "meta_manifest.json"
    _write_text(history_manifest, manifest_text)

    artifacts_out = {
        "META_MANIFEST": str(current_manifest),
        "META_MANIFEST_HISTORY": str(history_manifest),
    }

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Published {len(published_files)} audience meta files to current/.",
            artifacts=artifacts_out,
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Published {len(published_files)} audience meta files to current/.",
        artifacts=artifacts_out,
    )
