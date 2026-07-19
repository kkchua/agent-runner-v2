from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.actions.documentation_validation_core import DocumentationValidationPlan, validate_documentation_plan
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action

PERMANENT_DOCS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("L1_FOUNDATION_INDEX", "README.md", "SYS-00-IDX", ("Document Map",)),
    ("L1_LAYER_MODEL", "LAYER_MODEL.md", "SYS-00-LM", ("Layer 1", "Layer 2", "Layer 3", "Relationship Between Layers")),
    ("L1_DOCUMENT_AUTHORITY", "DOCUMENT_AUTHORITY.md", "SYS-00-DA", ("Authority Vocabulary", "Document Authority Matrix", "Promotion Rules")),
    ("L1_BUNDLE_TAXONOMY", "BUNDLE_TAXONOMY.md", "SYS-00-BT", ("Bundle Classes", "Ownership Rules")),
    ("L1_GOVERNANCE_LIFECYCLE", "GOVERNANCE_LIFECYCLE.md", "SYS-00-GL", ("Lifecycle States", "Publication Rule", "Promotion And Lifecycle Interaction")),
    ("L1_METADATA_STANDARD", "METADATA_STANDARD.md", "SYS-00-MS", ("Required Metadata Fields", "Allowed Scan Policy Values", "Scanner Compliance Rules")),
)

REQUIRED_FRONTMATTER_FIELDS: tuple[str, ...] = (
    "template_id",
    "version",
    "doc_type",
    "authority",
    "scan_policy",
    "scan_reason",
    "layer",
    "lifecycle_status",
    "effective_version",
)

ALLOWED_STAGED_LIFECYCLE_VALUES: tuple[str, ...] = ("draft",)
ALLOWED_PUBLISHED_LIFECYCLE_VALUES: tuple[str, ...] = ("published",)


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}", loop_iteration: int = 0) -> dict[str, str]:
    del mode
    run_root = f"docs/system/00_governance/foundation/runs/{job_id}"
    history_root = f"docs/system/00_governance/foundation/history/{job_id}"
    current_root = "docs/system/00_governance/foundation/current"
    iter_suffix = f"_iter{loop_iteration + 1}" if loop_iteration > 0 else ""
    return {
        "L1_FOUNDATION_INDEX": f"{run_root}/README.md",
        "L1_LAYER_MODEL": f"{run_root}/LAYER_MODEL.md",
        "L1_DOCUMENT_AUTHORITY": f"{run_root}/DOCUMENT_AUTHORITY.md",
        "L1_BUNDLE_TAXONOMY": f"{run_root}/BUNDLE_TAXONOMY.md",
        "L1_GOVERNANCE_LIFECYCLE": f"{run_root}/GOVERNANCE_LIFECYCLE.md",
        "L1_METADATA_STANDARD": f"{run_root}/METADATA_STANDARD.md",
        "GOVERNANCE_CONTEXT_INVENTORY": f"{run_root}/{job_id}-governance-context-inventory.md",
        "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-review{iter_suffix}.md",
        "GOVERNANCE_FOUNDATION_VALIDATION": f"{run_root}/{job_id}-governance-foundation-validation{iter_suffix}.md",
        "AUDIT_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-audit{iter_suffix}.md",
        "GOVERNANCE_PUBLISH_MANIFEST": f"{current_root}/governance_set_manifest.json",
        "GOVERNANCE_PUBLISH_MANIFEST_HISTORY": f"{history_root}/governance_set_manifest.json",
        "GOVERNANCE_CURRENT_ROOT": current_root,
        "GOVERNANCE_HISTORY_ROOT": history_root,
    }

FORBIDDEN_LAYER1_HEADINGS: tuple[str, ...] = (
    "# Runtime Governance",
    "## Runtime Governance",
    "# Installation Procedure",
    "## Installation Procedure",
    "# Publish Procedure",
    "## Publish Procedure",
    "# Registry Operations",
    "## Registry Operations",
)

FORBIDDEN_LAYER1_NEEDLES: tuple[str, ...] = (
    "copy template files",
    "seed default workflows",
    "repository setup",
    "run once during repository setup",
    "initialize repository or platform structure",
)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _update_frontmatter_fields(text: str, updates: dict[str, str]) -> str:
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
    elif not replaced_protected:
        for idx, line in enumerate(out):
            if line.startswith("> Managed by workflow:"):
                out.insert(idx + 1, "> This file is workflow-generated and protected from manual edits.")
                break
    return "\n".join(out).rstrip() + "\n"


def _doc_paths(job_id: str) -> dict[str, str]:
    output_paths = build_output_paths(job_id=job_id, mode="default")
    return {key: output_paths[key] for key, _, _, _ in PERMANENT_DOCS}


def _build_context_inventory(*, project_root: Path, job_id: str, step: str) -> str:
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    workflow_dirs = sorted(
        path.name for path in (project_root / "workflows").iterdir()
        if path.is_dir() and path.name != "01_governance_foundation_v1"
    )
    lines = [
        "---",
        'doc_type: "validation_artifact"',
        'authority: "workflow-generated"',
        'scan_policy: "exclude"',
        'scan_reason: "run-scoped governance context inventory"',
        'layer: "layer1"',
        'lifecycle_status: "draft"',
        f'effective_version: "{job_id}"',
        f'generated_at: "{generated_at}"',
        "---",
        "",
        "# Governance Context Inventory",
        "",
        "## Reference Files",
        "",
        f"- `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md`",
        f"- `masterplan/LAYER1_GOVERNANCE_SPECIFICATION.md`",
        "",
        "## Known Workflow Bundles",
        "",
    ]
    lines.extend(f"- `{name}`" for name in workflow_dirs)
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This artifact is comparison context only.",
            "- It is not part of the permanent Layer 1 governance set.",
            "- Review should use it to detect lower-layer duplication when applicable.",
            "",
        ]
    )
    return "\n".join(lines)


def _extra_validation_checks(*, project_root: Path, job_id: str) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for artifact_key, _, _, _ in PERMANENT_DOCS:
        rel_path = build_output_paths(job_id=job_id, mode="default")[artifact_key]
        path = project_root / rel_path
        if not path.exists():
            continue
        text = _read_text(path)
        checks.append({
            "check": "ascii_only_output",
            "path": rel_path,
            "ok": text.isascii(),
            "detail": "ASCII-only" if text.isascii() else "non-ASCII characters found",
        })
        for field in REQUIRED_FRONTMATTER_FIELDS:
            checks.append({
                "check": "frontmatter_field",
                "path": rel_path,
                "field": field,
                "ok": f"{field}:" in text.split("---", 2)[1] if text.startswith("---") and len(text.split("---", 2)) >= 3 else False,
                "detail": "found" if (f"{field}:" in text.split("---", 2)[1] if text.startswith("---") and len(text.split("---", 2)) >= 3 else False) else f"missing `{field}`",
            })
        checks.append({
            "check": "layer_field_value",
            "path": rel_path,
            "ok": 'layer: "layer1"' in text or "layer: 'layer1'" in text or "layer: layer1" in text,
            "detail": "layer1 present" if ('layer: "layer1"' in text or "layer: 'layer1'" in text or "layer: layer1" in text) else "layer field must be `layer1`",
        })
        staged_ok = any(
            f'lifecycle_status: "{value}"' in text
            or f"lifecycle_status: '{value}'" in text
            or f"lifecycle_status: {value}" in text
            for value in ALLOWED_STAGED_LIFECYCLE_VALUES
        )
        checks.append({
            "check": "staged_lifecycle_status",
            "path": rel_path,
            "ok": staged_ok,
            "detail": (
                "staged lifecycle status is valid"
                if staged_ok
                else f"staged docs must use one of: {', '.join(ALLOWED_STAGED_LIFECYCLE_VALUES)}"
            ),
        })
        for heading in FORBIDDEN_LAYER1_HEADINGS:
            checks.append({
                "check": "forbidden_operational_heading",
                "path": rel_path,
                "ok": heading not in text,
                "detail": "clear" if heading not in text else f"contains forbidden heading `{heading}`",
            })
        for needle in FORBIDDEN_LAYER1_NEEDLES:
            checks.append({
                "check": "forbidden_operational_phrase",
                "path": rel_path,
                "ok": needle not in text.lower(),
                "detail": "clear" if needle not in text.lower() else f"contains forbidden operational phrase `{needle}`",
            })
    readme_path = project_root / build_output_paths(job_id=job_id, mode="default")["L1_FOUNDATION_INDEX"]
    if readme_path.exists():
        readme_text = _read_text(readme_path)
        checks.append({
            "check": "readme_document_map_includes_readme",
            "path": str(readme_path.relative_to(project_root)).replace("\\", "/"),
            "ok": "README.md" in readme_text,
            "detail": "README.md is listed in the document map" if "README.md" in readme_text else "document map must include README.md as part of the six-document set",
        })
    return checks


@action("collect_governance_context")
def collect_governance_context(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    del step_cfg
    job_id = str(state.get("job_id") or "00GF")
    step = str(state.get("current_step") or "collect_governance_context")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="GOVERNANCE_CONTEXT_INVENTORY_METAJSON",
        default_step=step,
    )
    rel_path = build_output_paths(job_id=job_id, mode="default")["GOVERNANCE_CONTEXT_INVENTORY"]
    _write_text(project_root / rel_path, _build_context_inventory(project_root=project_root, job_id=job_id, step=step))
    artifacts = {"GOVERNANCE_CONTEXT_INVENTORY": rel_path}
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark="Governance context inventory collected.", artifacts=artifacts)
    return ActionResult(status="APPROVED", remark="Governance context inventory collected.", artifacts=artifacts)


@action("validate_governance_foundation_docs")
def validate_governance_foundation_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    del step_cfg
    job_id = str(state.get("job_id") or "00GF")
    step = str(state.get("current_step") or "validate_governance_foundation_docs")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="GOVERNANCE_FOUNDATION_VALIDATION_METAJSON",
        default_step=step,
    )
    loop_ctx = state.get("loop_context") or {}
    loop_iteration = int(loop_ctx.get("loop_iteration", 0)) if loop_ctx.get("active") else 0
    output_paths = build_output_paths(job_id=job_id, mode="default", loop_iteration=loop_iteration)
    section_requirements = {
        output_paths[key]: sections
        for key, _, _, sections in PERMANENT_DOCS
    }
    template_ids = {
        output_paths[key]: template_id
        for key, _, template_id, _ in PERMANENT_DOCS
    }
    plan = DocumentationValidationPlan(
        required_files=tuple(output_paths[key] for key, _, _, _ in PERMANENT_DOCS),
        section_requirements=section_requirements,
        template_ids=template_ids,
    )
    checks = validate_documentation_plan(project_root=project_root, plan=plan)
    checks.extend(_extra_validation_checks(project_root=project_root, job_id=job_id))
    failed = [item for item in checks if not item["ok"]]

    validation_rel = output_paths["GOVERNANCE_FOUNDATION_VALIDATION"]
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "---",
        'doc_type: "validation_artifact"',
        'authority: "workflow-generated"',
        'scan_policy: "exclude"',
        'scan_reason: "run-scoped validation report for governance foundation"',
        'layer: "layer1"',
        f'lifecycle_status: "{("rejected" if failed else "approved").lower()}"',
        f'effective_version: "{job_id}"',
        f'generated_at: "{generated_at}"',
        "---",
        "",
        "# Governance Foundation Validation",
        "",
        f"- Job ID: `{job_id}`",
        f"- Total checks: `{len(checks)}`",
        f"- Failed checks: `{len(failed)}`",
        "",
    ]
    if failed:
        lines.append("## Failed Checks")
        lines.append("")
        for item in failed:
            suffix = f" @ `{item['path']}`"
            if item.get("field"):
                suffix += f" field=`{item['field']}`"
            if item.get("section"):
                suffix += f" section=`{item['section']}`"
            lines.append(f"- `{item['check']}`{suffix}: {item['detail']}")
    else:
        lines.append("All governance foundation validation checks passed.")
    _write_text(project_root / validation_rel, "\n".join(lines) + "\n")
    artifacts = {"GOVERNANCE_FOUNDATION_VALIDATION": validation_rel}
    if failed:
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=f"Governance foundation validation failed: {len(failed)} checks failed.", artifacts=artifacts)
        return ActionResult(
            status="REJECTED",
            remark=f"Governance foundation validation failed: {len(failed)} checks failed.",
            artifacts=artifacts,
            reject_code="GOVERNANCE_FOUNDATION_VALIDATION_FAILED",
        )
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark=f"Governance foundation validation passed ({len(checks)} checks).", artifacts=artifacts)
    return ActionResult(status="APPROVED", remark=f"Governance foundation validation passed ({len(checks)} checks).", artifacts=artifacts)


@action("publish_governance_foundation_set")
def publish_governance_foundation_set(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    del step_cfg
    job_id = str(state.get("job_id") or "00GF")
    step = str(state.get("current_step") or "publish_governance_foundation_set")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="GOVERNANCE_PUBLISH_MANIFEST_METAJSON",
        default_step=step,
    )
    output_paths = build_output_paths(job_id=job_id, mode="default")
    current_root = project_root / output_paths["GOVERNANCE_CURRENT_ROOT"]
    history_root = project_root / output_paths["GOVERNANCE_HISTORY_ROOT"]
    current_root.mkdir(parents=True, exist_ok=True)
    history_root.mkdir(parents=True, exist_ok=True)

    previous_manifest_path = current_root / "governance_set_manifest.json"
    previous_version = None
    if previous_manifest_path.exists():
        try:
            previous_version = json.loads(previous_manifest_path.read_text(encoding="utf-8")).get("effective_version")
        except json.JSONDecodeError:
            previous_version = None

    published_files: dict[str, str] = {}
    for artifact_key, filename, _, _ in PERMANENT_DOCS:
        src_rel = output_paths[artifact_key]
        src_path = project_root / src_rel
        current_path = current_root / filename
        history_path = history_root / filename
        text = _update_frontmatter_fields(
            _read_text(src_path),
            {
                "lifecycle_status": "published",
                "effective_version": job_id,
            },
        )
        text = _update_managed_banner(
            text,
            workflow="01_governance_foundation_v1",
            step=step,
        )
        _write_text(current_path, text)
        _write_text(history_path, text)
        published_files[artifact_key] = str(current_path.relative_to(project_root)).replace("\\", "/")

    manifest = {
        "workflow_id": "01_governance_foundation_v1",
        "workflow_layer": "layer1",
        "change_or_run_id": job_id,
        "change_class": "governance_change",
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
    current_manifest_rel = output_paths["GOVERNANCE_PUBLISH_MANIFEST"]
    history_manifest_rel = output_paths["GOVERNANCE_PUBLISH_MANIFEST_HISTORY"]
    _write_text(project_root / current_manifest_rel, manifest_text)
    _write_text(project_root / history_manifest_rel, manifest_text)

    artifacts = {"GOVERNANCE_PUBLISH_MANIFEST": current_manifest_rel}
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark="Governance foundation set published as the active Layer 1 set.", artifacts=artifacts)
    return ActionResult(status="APPROVED", remark="Governance foundation set published as the active Layer 1 set.", artifacts=artifacts)
