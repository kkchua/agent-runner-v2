from __future__ import annotations

import re
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
    validate_documentation_plan,
)
from agent_runner_v2.doc_paths import system_doc_rel
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action


LAYER1_REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    system_doc_rel("README.md"): (
        "System Documentation Index",
        "Audience Views",
        "Document Map",
    ),
    system_doc_rel("DOCUMENTATION_STANDARD.md"): (
        "Purpose",
        "Audience Model",
        "Document Set",
        "Architecture Baseline",
        "Conditional Standards",
        "Update Triggers",
        "Validation",
    ),
    system_doc_rel("BUNDLE_TAXONOMY.md"): (
        "Bundle Classes",
        "Ownership Rules",
        "Packaging Rules",
    ),
    system_doc_rel("RUNTIME_GOVERNANCE.md"): (
        "Purpose",
        "Runtime Scope Model",
        "Bundle Publish And Install Model",
        "Registry Control Plane",
        "Plugin Bundle Control Model",
        "Role And Connection Resolution",
        "Artifact Ownership Enforcement",
        "Execution Mode Parity",
        "Validation Gates",
        "Change Control",
    ),
}

FORBIDDEN_LITERALS: tuple[str, ...] = (
    "delivery_scaffold_v1",
    "{ARTIFACT_KEY_",
)

REPO_ARTIFACT_NEEDLES: tuple[str, ...] = (
    "PROJECT_ANALYSIS",
    "CODEBASE_INVENTORY",
    "SYSTEM_OVERVIEW",
    "BUSINESS_CAPABILITIES",
    "FUNCTIONAL_SPEC",
    "NON_FUNCTIONAL_REQUIREMENTS",
    "SYSTEM_CONTEXT",
    "COMPONENT_ARCHITECTURE",
    "DECISION_LOG",
    "SYSTEM_FILE_STRUCTURE",
    "DEVELOPER_GUIDE",
    "RUNBOOK",
)

REPO_ANALYSIS_PATHS: tuple[str, ...] = (
    "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md",
    "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md",
    "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md",
    "docs/repo/",
)

WORKFLOW_ID_RE = re.compile(r"\b\d{2}_[a-z0-9]+(?:_[a-z0-9]+)*_v\d+\b", re.IGNORECASE)


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    return parts[2]


def _strip_workflow_managed_banner(text: str) -> str:
    lines = text.splitlines()
    filtered: list[str] = []
    for line in lines:
        if line.startswith("> Managed by workflow:"):
            continue
        if line.startswith("> This file is workflow-generated and protected from manual edits."):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _extra_layer1_checks(*, project_root: Path) -> list[dict[str, str | bool]]:
    docs = {
        "README.md": project_root / system_doc_rel("README.md"),
        "DOCUMENTATION_STANDARD.md": project_root / system_doc_rel("DOCUMENTATION_STANDARD.md"),
        "BUNDLE_TAXONOMY.md": project_root / system_doc_rel("BUNDLE_TAXONOMY.md"),
        "RUNTIME_GOVERNANCE.md": project_root / system_doc_rel("RUNTIME_GOVERNANCE.md"),
    }
    checks: list[dict[str, str | bool]] = []

    def add(ok: bool, check: str, path: Path, detail: str) -> None:
        checks.append({
            "ok": ok,
            "check": check,
            "path": str(path.relative_to(project_root)),
            "detail": detail,
        })

    texts: dict[str, str] = {}
    bodies: dict[str, str] = {}
    for name, path in docs.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        texts[name] = text
        bodies[name] = _strip_workflow_managed_banner(_strip_frontmatter(text))
        for literal in FORBIDDEN_LITERALS:
            add(literal not in text, "forbidden_literal", path, f"forbidden=`{literal}`")

    readme_text = texts.get("README.md", "")
    std_text = texts.get("DOCUMENTATION_STANDARD.md", "")
    tax_text = texts.get("BUNDLE_TAXONOMY.md", "")
    runtime_text = texts.get("RUNTIME_GOVERNANCE.md", "")

    for name, body in bodies.items():
        path = docs[name]
        found = sorted(set(WORKFLOW_ID_RE.findall(body)))
        add(
            not found,
            "concrete_workflow_name",
            path,
            "Layer 1 docs must not name concrete workflow identifiers in body text."
            if not found else f"found={', '.join(found)}",
        )

    add(
        all(needle not in std_text for needle in REPO_ARTIFACT_NEEDLES),
        "documentation_standard_scope",
        docs["DOCUMENTATION_STANDARD.md"],
        "DOCUMENTATION_STANDARD must stay generic and must not enumerate repo-derived artifact sets.",
    )
    add(
        all(path not in tax_text for path in REPO_ANALYSIS_PATHS),
        "bundle_taxonomy_scope",
        docs["BUNDLE_TAXONOMY.md"],
        "BUNDLE_TAXONOMY must not present repo-analysis outputs or repo-local outputs as Layer 1 ownership.",
    )
    add(
        all(path not in runtime_text for path in REPO_ANALYSIS_PATHS),
        "runtime_governance_scope",
        docs["RUNTIME_GOVERNANCE.md"],
        "RUNTIME_GOVERNANCE must define steady-state runtime governance, not repo-analysis ownership.",
    )
    add(
        "plugin workflow bundle" in runtime_text.lower() or "plugin bundle" in runtime_text.lower(),
        "plugin_bundle_contract",
        docs["RUNTIME_GOVERNANCE.md"],
        "RUNTIME_GOVERNANCE must define plugin workflow bundles generically.",
    )
    add(
        (
            "one workflow" in runtime_text.lower()
            or "single-workflow" in runtime_text.lower()
            or "single workflow" in runtime_text.lower()
        )
        and ("many workflows" in runtime_text.lower() or "multi-workflow" in runtime_text.lower()),
        "multi_workflow_bundle_support",
        docs["RUNTIME_GOVERNANCE.md"],
        "RUNTIME_GOVERNANCE must recognize both single-workflow and multi-workflow plugin bundles.",
    )
    add(
        "plugin workflow bundle" in tax_text.lower() or "plugin bundle" in tax_text.lower(),
        "bundle_class_presence",
        docs["BUNDLE_TAXONOMY.md"],
        "BUNDLE_TAXONOMY must define plugin workflow bundles generically.",
    )
    add(
        "docs/repo/*" in readme_text or "docs/repo/" in readme_text,
        "repo_output_boundary",
        docs["README.md"],
        "README must make the repo-local output boundary explicit.",
    )

    return checks


@action("validate_layer1_governance_docs")
def validate_layer1_governance_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    job_id = str(state.get("job_id") or "00L1")
    step = str(state.get("current_step") or "validate_layer1_governance_docs")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="SYSTEM_DOCS_VALIDATION_METAJSON",
        default_step=step,
    )

    required_files = (
        system_doc_rel("README.md"),
        system_doc_rel("DOCUMENTATION_STANDARD.md"),
        system_doc_rel("BUNDLE_TAXONOMY.md"),
        system_doc_rel("RUNTIME_GOVERNANCE.md"),
    )
    plan = DocumentationValidationPlan(
        required_files=required_files,
        section_requirements=LAYER1_REQUIRED_SECTIONS,
        template_ids={
            system_doc_rel("README.md"): "SYS-00-IDX",
            system_doc_rel("DOCUMENTATION_STANDARD.md"): "SYS-00-DS",
            system_doc_rel("BUNDLE_TAXONOMY.md"): "SYS-00-BT",
            system_doc_rel("RUNTIME_GOVERNANCE.md"): "SYS-00-RG",
        },
    )
    checks = validate_documentation_plan(project_root=project_root, plan=plan)
    checks.extend(_extra_layer1_checks(project_root=project_root))
    failed = [item for item in checks if not item["ok"]]

    validation_rel = system_doc_rel(f"{job_id}-layer1-governance-validation.md")
    lines = [
        "# Layer1 Governance Validation",
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
            lines.append(f"- `{item['check']}` @ `{item['path']}`: {item['detail']}")
    else:
        lines.append("All Layer 1 governance checks passed.")
    _write_text(project_root / validation_rel, "\n".join(lines) + "\n")

    artifacts = {"SYSTEM_DOCS_VALIDATION": validation_rel}
    if failed:
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=f"Layer 1 governance validation failed: {len(failed)} checks failed.",
                artifacts=artifacts,
            )
        return ActionResult(
            status="REJECTED",
            remark=f"Layer 1 governance validation failed: {len(failed)} checks failed.",
            artifacts=artifacts,
            reject_code="LAYER1_GOVERNANCE_VALIDATION_FAILED",
        )

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Layer 1 governance validation passed ({len(checks)} checks).",
            artifacts=artifacts,
        )
    return ActionResult(
        status="APPROVED",
        remark=f"Layer 1 governance validation passed ({len(checks)} checks).",
        artifacts=artifacts,
    )
