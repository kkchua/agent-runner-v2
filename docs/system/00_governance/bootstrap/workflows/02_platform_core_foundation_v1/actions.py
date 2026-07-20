from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.actions.documentation_validation_core import DocumentationValidationPlan, validate_documentation_plan
from agent_runner_v2.runtime_context import GLOBAL_RUNNER_HOME, resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Permanent document registry
# ---------------------------------------------------------------------------
PERMANENT_DOCS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("L2_PLATFORM_INDEX", "README.md", "SYS-02-IDX", ("Document Map", "Platform Identity", "Layer 1 Inheritance")),
    ("L2_RUNTIME_MODEL", "RUNTIME_MODEL.md", "SYS-02-RM", ("Step Model", "Execution Paths", "Job Lifecycle", "Coder Integration", "Rejection And Retry")),
    ("L2_BUNDLE_AUTHORING_CONTRACT", "BUNDLE_AUTHORING_CONTRACT.md", "SYS-02-BAC", ("Required Bundle Files", "workflow.toml Format", "Artifact Key Conventions", "Bundle Governance Requirements", "Metadata Compliance")),
    ("L2_SHARED_SERVICES", "SHARED_SERVICES.md", "SYS-02-SS", ("Context Extensions", "Artifact Resolution", "Path Contracts", "Meta Sidecar", "Notification Integration", "Backend Sync Protocol", "Action Registration")),
    ("L2_METADATA_CONTRACT", "METADATA_CONTRACT.md", "SYS-02-MC", ("Platform doc_type Values", "Platform authority Values", "Additional Frontmatter Fields", "Inheritance Rules", "Scan Policy Expectations")),
    ("L2_VALIDATION_CONTRACT", "VALIDATION_CONTRACT.md", "SYS-02-VC", ("ValidationPlan Pattern", "Section Checks", "Frontmatter Enforcement", "File Existence Checks", "Bundle Validator Composition")),
)

REQUIRED_FRONTMATTER_FIELDS: tuple[str, ...] = (
    "template_id",
    "version",
    "doc_type",
    "authority",
    "scan_policy",
    "scan_reason",
    "layer",
    "platform",
    "lifecycle_status",
    "effective_version",
)

ALLOWED_STAGED_LIFECYCLE_VALUES: tuple[str, ...] = ("draft",)
ALLOWED_PUBLISHED_LIFECYCLE_VALUES: tuple[str, ...] = ("published",)

FORBIDDEN_LAYER2_HEADINGS: tuple[str, ...] = (
    "# Ecosystem Governance",
    "## Ecosystem Governance",
    "# Layer 1 Governance",
    "## Layer 1 Governance",
    "# Bundle Inventory",
    "## Bundle Inventory",
)

FORBIDDEN_LAYER2_NEEDLES: tuple[str, ...] = (
    "all platforms must",
    "every platform shall",
    "any Layer 2 core must",
    "ecosystem-wide standard",
    "redefines Layer 1 governance",
    "overrides the Layer 1",
    "bundle-specific output is the platform standard",
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
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


def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}", loop_iteration: int = 0) -> dict[str, str]:
    del mode
    run_root = f"docs/system/00_governance/platform/runs/{job_id}"
    history_root = f"docs/system/00_governance/platform/history/{job_id}"
    current_root = "docs/system/00_governance/platform/current"
    iter_suffix = f"_iter{loop_iteration + 1}" if loop_iteration > 0 else ""
    return {
        "L2_PLATFORM_INDEX": f"{run_root}/README.md",
        "L2_RUNTIME_MODEL": f"{run_root}/RUNTIME_MODEL.md",
        "L2_BUNDLE_AUTHORING_CONTRACT": f"{run_root}/BUNDLE_AUTHORING_CONTRACT.md",
        "L2_SHARED_SERVICES": f"{run_root}/SHARED_SERVICES.md",
        "L2_METADATA_CONTRACT": f"{run_root}/METADATA_CONTRACT.md",
        "L2_VALIDATION_CONTRACT": f"{run_root}/VALIDATION_CONTRACT.md",
        "PLATFORM_CONTEXT_INVENTORY": f"{run_root}/{job_id}-platform-context-inventory.md",
        "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-platform-core-review{iter_suffix}.md",
        "PLATFORM_CORE_VALIDATION": f"{run_root}/{job_id}-platform-core-validation{iter_suffix}.md",
        "AUDIT_FILE_SUGGESTED": f"{run_root}/{job_id}-platform-core-audit{iter_suffix}.md",
        "PLATFORM_PUBLISH_MANIFEST": f"{current_root}/platform_set_manifest.json",
        "PLATFORM_PUBLISH_MANIFEST_HISTORY": f"{history_root}/platform_set_manifest.json",
        "PLATFORM_CURRENT_ROOT": current_root,
        "PLATFORM_HISTORY_ROOT": history_root,
    }


def _doc_paths(job_id: str) -> dict[str, str]:
    output_paths = build_output_paths(job_id=job_id, mode="default")
    return {key: output_paths[key] for key, _, _, _ in PERMANENT_DOCS}


# ---------------------------------------------------------------------------
# Context inventory (curated reference paths — no scanning)
# ---------------------------------------------------------------------------
DECLARED_REFERENCE_MODULES: tuple[str, ...] = (
    "agent_runner_v2/runtime_context.py",
    "agent_runner_v2/step_runner.py",
    "agent_runner_v2/daemon.py",
    "agent_runner_v2/coder_adapters.py",
    "agent_runner_v2/coder_registry.py",
    "agent_runner_v2/constants.py",
    "agent_runner_v2/bundle_loader.py",
    "agent_runner_v2/backend_client.py",
    "agent_runner_v2/backend_execution.py",
    "agent_runner_v2/action_result.py",
    "agent_runner_v2/notification_manager.py",
    "agent_runner_v2/workflow_packages/base.py",
    "agent_runner_v2/workflow_packages/loader.py",
    "agent_runner_v2/workflow_packages/actions.py",
    "agent_runner_v2/workflow_packages/registry.py",
    "agent_runner_v2/actions/documentation_validation_core.py",
    "agent_runner_v2/workflow_bundle_validator.py",
)


def _build_context_inventory(*, project_root: Path, job_id: str, step: str) -> str:
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    workflow_dirs = sorted(
        path.name for path in (project_root / "workflows").iterdir()
        if path.is_dir() and path.name != "02_platform_core_foundation_v1"
    )
    lines = [
        "---",
        'doc_type: "validation_artifact"',
        'authority: "workflow-generated"',
        'scan_policy: "exclude"',
        'scan_reason: "run-scoped platform context inventory"',
        'layer: "layer2"',
        'platform: "agent-runner-v2"',
        'lifecycle_status: "draft"',
        f'effective_version: "{job_id}"',
        f'generated_at: "{generated_at}"',
        "---",
        "",
        "# Platform Context Inventory",
        "",
        "## Reference Files",
        "",
        f"- `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md`",
        f"- `masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md`",
        f"- Layer 1 governance set: `docs/system/00_governance/foundation/current/`",
        "",
        "## Source Code Modules (read-only reference)",
        "",
    ]
    for mod in DECLARED_REFERENCE_MODULES:
        exists = (project_root / mod).exists()
        status = "present" if exists else "missing"
        lines.append(f"- `{mod}` ({status})")
    lines.extend([
        "",
        "## Known Workflow Bundles",
        "",
    ])
    lines.extend(f"- `{name}`" for name in workflow_dirs)
    lines.extend([
        "",
        "## Notes",
        "",
        "- This artifact is comparison context only.",
        "- It is not part of the permanent Layer 2 platform set.",
        "- Source code modules are read-only reference for the runtime model.",
        "- The curated reference list is fixed in the action implementation, not discovered at runtime.",
        "",
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Extra validation (beyond the generic DocumentationValidationPlan)
# ---------------------------------------------------------------------------
def _extra_validation_checks(*, project_root: Path, job_id: str) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []

    # ------------------------------------------------------------------
    # Pre-flight: Layer 1 governance must be installed at global runtime root
    # ------------------------------------------------------------------
    governance_root = GLOBAL_RUNNER_HOME / "bundles" / "core" / "current"
    checks.append({
        "check": "governance_runtime_root_exists",
        "path": str(governance_root),
        "ok": governance_root.is_dir(),
        "detail": (
            "found" if governance_root.is_dir()
            else "missing — run `ukbe-run-agent init` to install Layer 1 governance"
        ),
    })

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
            fm_ok = False
            if text.startswith("---") and len(text.split("---", 2)) >= 3:
                fm_ok = f"{field}:" in text.split("---", 2)[1]
            checks.append({
                "check": "frontmatter_field",
                "path": rel_path,
                "field": field,
                "ok": fm_ok,
                "detail": "found" if fm_ok else f"missing `{field}`",
            })
        checks.append({
            "check": "layer_field_value",
            "path": rel_path,
            "ok": 'layer: "layer2"' in text or "layer: 'layer2'" in text or "layer: layer2" in text,
            "detail": "layer2 present" if ('layer: "layer2"' in text or "layer: 'layer2'" in text or "layer: layer2" in text) else "layer field must be `layer2`",
        })
        checks.append({
            "check": "platform_field_value",
            "path": rel_path,
            "ok": 'agent-runner-v2' in text and ('platform: "agent-runner-v2"' in text or "platform: 'agent-runner-v2'" in text or "platform: agent-runner-v2" in text),
            "detail": "agent-runner-v2 present" if ('agent-runner-v2' in text) else "platform field must be `agent-runner-v2`",
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
        for heading in FORBIDDEN_LAYER2_HEADINGS:
            checks.append({
                "check": "forbidden_heading",
                "path": rel_path,
                "ok": heading not in text,
                "detail": "clear" if heading not in text else f"contains forbidden heading `{heading}`",
            })
        for needle in FORBIDDEN_LAYER2_NEEDLES:
            checks.append({
                "check": "forbidden_phrase",
                "path": rel_path,
                "ok": needle not in text.lower(),
                "detail": "clear" if needle not in text.lower() else f"contains forbidden phrase `{needle}`",
            })
        # ------------------------------------------------------------------
        # Source-code cross-reference: verify documented API symbols exist
        # ------------------------------------------------------------------
        if artifact_key == "L2_SHARED_SERVICES":
            backend_client_path = project_root / "agent_runner_v2" / "backend_client.py"
            if backend_client_path.exists():
                source_text = _read_text(backend_client_path)
                actual_methods: set[str] = set(re.findall(r"^\s+def ([a-z_][a-z0-9_]*)", source_text, re.MULTILINE))
                # Extract only the BackendClient section from the doc
                bc_section_match = re.search(r"^### BackendClient\n\n(.*?)(?=^### |\Z)", text, re.MULTILINE | re.DOTALL)
                bc_section = bc_section_match.group(1) if bc_section_match else ""
                documented = set(re.findall(r"- `([a-z_][a-z0-9_]*)\(\)`", bc_section))
                for doc_name in sorted(documented):
                    checks.append({
                        "check": "backend_client_method_verification",
                        "path": rel_path,
                        "field": doc_name,
                        "ok": doc_name in actual_methods,
                        "detail": (
                            f"matches source" if doc_name in actual_methods
                            else f"no `{doc_name}` in backend_client.py"
                        ),
                    })
    readme_path = project_root / build_output_paths(job_id=job_id, mode="default")["L2_PLATFORM_INDEX"]
    if readme_path.exists():
        readme_text = _read_text(readme_path)
        checks.append({
            "check": "readme_document_map_includes_readme",
            "path": str(readme_path.relative_to(project_root)).replace("\\", "/"),
            "ok": "README.md" in readme_text,
            "detail": "README.md is listed in the document map" if "README.md" in readme_text else "document map must include README.md as part of the six-document set",
        })
    return checks


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
@action("collect_platform_context")
def collect_platform_context(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    del step_cfg
    job_id = str(state.get("job_id") or "02PC")
    step = str(state.get("current_step") or "collect_platform_context")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="PLATFORM_CONTEXT_INVENTORY_METAJSON",
        default_step=step,
    )
    rel_path = build_output_paths(job_id=job_id, mode="default")["PLATFORM_CONTEXT_INVENTORY"]
    _write_text(project_root / rel_path, _build_context_inventory(project_root=project_root, job_id=job_id, step=step))
    artifacts = {"PLATFORM_CONTEXT_INVENTORY": rel_path}
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark="Platform context inventory collected.", artifacts=artifacts)
    return ActionResult(status="APPROVED", remark="Platform context inventory collected.", artifacts=artifacts)


@action("validate_platform_core_docs")
def validate_platform_core_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    del step_cfg
    job_id = str(state.get("job_id") or "02PC")
    step = str(state.get("current_step") or "validate_platform_core_docs")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="PLATFORM_CORE_VALIDATION_METAJSON",
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

    validation_rel = output_paths["PLATFORM_CORE_VALIDATION"]
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "---",
        'doc_type: "validation_artifact"',
        'authority: "workflow-generated"',
        'scan_policy: "exclude"',
        'scan_reason: "run-scoped validation report for platform core"',
        'layer: "layer2"',
        'platform: "agent-runner-v2"',
        f'lifecycle_status: "{("rejected" if failed else "approved").lower()}"',
        f'effective_version: "{job_id}"',
        f'generated_at: "{generated_at}"',
        "---",
        "",
        "# Platform Core Validation",
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
        lines.append("All platform core validation checks passed.")
    _write_text(project_root / validation_rel, "\n".join(lines) + "\n")
    artifacts = {"PLATFORM_CORE_VALIDATION": validation_rel}
    if failed:
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=f"Platform core validation failed: {len(failed)} checks failed.", artifacts=artifacts)
        return ActionResult(
            status="REJECTED",
            remark=f"Platform core validation failed: {len(failed)} checks failed.",
            artifacts=artifacts,
            reject_code="PLATFORM_CORE_VALIDATION_FAILED",
        )
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark=f"Platform core validation passed ({len(checks)} checks).", artifacts=artifacts)
    return ActionResult(status="APPROVED", remark=f"Platform core validation passed ({len(checks)} checks).", artifacts=artifacts)


@action("publish_platform_core_set")
def publish_platform_core_set(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    del step_cfg
    job_id = str(state.get("job_id") or "02PC")
    step = str(state.get("current_step") or "publish_platform_core_set")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="PLATFORM_PUBLISH_MANIFEST_METAJSON",
        default_step=step,
    )
    output_paths = build_output_paths(job_id=job_id, mode="default")
    current_root = project_root / output_paths["PLATFORM_CURRENT_ROOT"]
    history_root = project_root / output_paths["PLATFORM_HISTORY_ROOT"]
    current_root.mkdir(parents=True, exist_ok=True)
    history_root.mkdir(parents=True, exist_ok=True)

    previous_manifest_path = current_root / "platform_set_manifest.json"
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
                "authority": "platform-owned",
                "lifecycle_status": "published",
                "effective_version": job_id,
            },
        )
        text = _update_managed_banner(
            text,
            workflow="02_platform_core_foundation_v1",
            step=step,
        )
        _write_text(current_path, text)
        _write_text(history_path, text)
        published_files[artifact_key] = str(current_path.relative_to(project_root)).replace("\\", "/")

    manifest = {
        "workflow_id": "02_platform_core_foundation_v1",
        "workflow_layer": "layer2",
        "platform": "agent-runner-v2",
        "change_or_run_id": job_id,
        "change_class": "governance_change",
        "artifact_inventory": published_files,
        "artifact_permanence_class": "permanent",
        "authority": "platform-owned",
        "lifecycle_status": "published",
        "source_step": step,
        "published_timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "effective_version": job_id,
        "active_set": True,
        "supersedes": previous_version,
        "superseded_by": None,
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    current_manifest_rel = output_paths["PLATFORM_PUBLISH_MANIFEST"]
    history_manifest_rel = output_paths["PLATFORM_PUBLISH_MANIFEST_HISTORY"]
    _write_text(project_root / current_manifest_rel, manifest_text)
    _write_text(project_root / history_manifest_rel, manifest_text)

    artifacts = {"PLATFORM_PUBLISH_MANIFEST": current_manifest_rel}
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark="Platform core set published as the active Layer 2 set for agent-runner-v2.", artifacts=artifacts)
    return ActionResult(status="APPROVED", remark="Platform core set published as the active Layer 2 set for agent-runner-v2.", artifacts=artifacts)
