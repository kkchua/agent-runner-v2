from __future__ import annotations

from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
    validate_documentation_plan,
)
from agent_runner_v2.doc_paths import system_doc_rel
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action


CORE_GOVERNANCE_REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    system_doc_rel("README.md"): (
        "System Documentation Index",
        "Audience Views",
        "Document Map",
    ),
    system_doc_rel("DOCUMENTATION_STANDARD.md"): (
        "Purpose",
        "Audience Model",
        "Document Set",
        "Update Triggers",
        "Validation",
    ),
    system_doc_rel("BUNDLE_TAXONOMY.md"): (
        "Bundle Classes",
        "Ownership Rules",
        "Packaging Rules",
    ),
    system_doc_rel("BUNDLE_MIGRATION_PLAN.md"): (
        "Current State",
        "Target State",
        "Migration Phases",
    ),
}


STALE_REFERENCE_RULES: tuple[tuple[str, str], ...] = (
    ("delivery_scaffold_v1", "Use `10_execution_scaffold_v2` as the canonical scaffold workflow in this repository."),
    ("{ARTIFACT_KEY_", "Describe the prompt contract using direct artifact placeholders like `{PROJECT_ANALYSIS}`, not `{ARTIFACT_KEY_*}`."),
    ("40_task_execution_v1", "Use actual current workflow IDs from the repository registry; `40_task_execution_v1` is stale here."),
    ("41_bug_fix_intake_v1", "Use actual current workflow IDs from the repository registry; `41_bug_fix_intake_v1` is stale here."),
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


def _load_registry_workflow_names(project_root: Path) -> set[str]:
    workflow_root = project_root / "workflows"
    names: set[str] = set()
    if workflow_root.exists():
        for child in workflow_root.iterdir():
            if child.is_dir():
                names.add(child.name)

    try:
        from agent_runner_v2.bootstrap.workflows.default.template_groups import TEMPLATE_GROUPS

        names.update(TEMPLATE_GROUPS.keys())
    except Exception:
        pass
    return names


def _extra_core_governance_checks(*, project_root: Path) -> list[dict[str, str | bool]]:
    docs = {
        "README.md": (project_root / system_doc_rel("README.md")),
        "DOCUMENTATION_STANDARD.md": (project_root / system_doc_rel("DOCUMENTATION_STANDARD.md")),
        "BUNDLE_TAXONOMY.md": (project_root / system_doc_rel("BUNDLE_TAXONOMY.md")),
        "BUNDLE_MIGRATION_PLAN.md": (project_root / system_doc_rel("BUNDLE_MIGRATION_PLAN.md")),
    }
    checks: list[dict[str, str | bool]] = []
    registry_names = _load_registry_workflow_names(project_root)

    def add(ok: bool, check: str, path: Path, detail: str) -> None:
        checks.append(
            {
                "ok": ok,
                "check": check,
                "path": str(path.relative_to(project_root)),
                "detail": detail,
            }
        )

    for _, path in docs.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for needle, detail in STALE_REFERENCE_RULES:
            add(needle not in text, "stale_reference", path, f"forbidden=`{needle}` {detail}")

    readme_text = docs["README.md"].read_text(encoding="utf-8")
    std_text = docs["DOCUMENTATION_STANDARD.md"].read_text(encoding="utf-8")
    tax_text = docs["BUNDLE_TAXONOMY.md"].read_text(encoding="utf-8")
    migration_text = docs["BUNDLE_MIGRATION_PLAN.md"].read_text(encoding="utf-8")

    add(
        "10_execution_scaffold_v2" in readme_text or "10_execution_scaffold_v2" in std_text,
        "canonical_scaffold_reference",
        docs["DOCUMENTATION_STANDARD.md"],
        "Core governance docs must reference `10_execution_scaffold_v2` as the canonical scaffold workflow in this repository.",
    )
    add(
        "`00_master_docs_bootstrap_v2`" not in tax_text.split("### Class 1: Core Governance Bundles", 1)[-1].split("### Class 2:", 1)[0],
        "bundle_classification",
        docs["BUNDLE_TAXONOMY.md"],
        "`00_master_docs_bootstrap_v2` must not be classified under Core Governance Bundles.",
    )
    add(
        "Core Governance | `docs/system/00_governance/bootstrap/` | `docs/repo/*`" not in tax_text,
        "bundle_write_boundary",
        docs["BUNDLE_TAXONOMY.md"],
        "Core governance bundles must not claim ownership of repo-local outputs under `docs/repo/*`.",
    )
    add(
        "Repo-Document Bundles" not in tax_text,
        "repo_bundle_taxonomy_scope",
        docs["BUNDLE_TAXONOMY.md"],
        "Core governance taxonomy must not define a `Repo-Document Bundles` class.",
    )
    add(
        "Current registered workflows in this repository" not in readme_text,
        "readme_workflow_inventory_scope",
        docs["README.md"],
        "README must not include repository-specific workflow inventory.",
    )
    add(
        "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md" not in tax_text
        and "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md" not in tax_text
        and "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md" not in tax_text,
        "legacy_system_analysis_scope",
        docs["BUNDLE_TAXONOMY.md"],
        "Repo-analysis outputs under `docs/system/00_governance/bootstrap/` must not be treated as active governance artifacts.",
    )
    add(
        all(needle not in std_text for needle in REPO_ARTIFACT_NEEDLES),
        "documentation_standard_scope",
        docs["DOCUMENTATION_STANDARD.md"],
        "DOCUMENTATION_STANDARD must focus on the four ecosystem master docs and must not enumerate repo-derived artifact sets.",
    )
    add(
        "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md" not in migration_text
        and "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md" not in migration_text
        and "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md" not in migration_text,
        "migration_plan_scope",
        docs["BUNDLE_MIGRATION_PLAN.md"],
        "BUNDLE_MIGRATION_PLAN may discuss legacy mixed docs, but must not present repo-analysis docs under `docs/system/00_governance/bootstrap/` as active target-state artifacts.",
    )

    known_names = sorted(name for name in registry_names if name)
    for bad_name in ("40_task_execution_v1", "41_bug_fix_intake_v1"):
        add(
            bad_name not in migration_text and bad_name not in tax_text,
            "registry_workflow_name",
            docs["BUNDLE_MIGRATION_PLAN.md"],
            f"`{bad_name}` is not in the current repository workflow registry. Known names include: {', '.join(known_names[:8])}...",
        )
    add(
        "20_initiative_intake_v1" in registry_names or "20_initiative_intake_v1" not in migration_text,
        "registry_workflow_name",
        docs["BUNDLE_MIGRATION_PLAN.md"],
        "`20_initiative_intake_v1` is not in the current repository workflow registry and must not be listed as current inventory here.",
    )

    return checks


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@action("validate_core_governance_docs")
def validate_core_governance_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    job_id = str(state.get("job_id") or "00CORE")
    step = str(state.get("current_step") or "validate_core_governance_docs")
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
        system_doc_rel("BUNDLE_MIGRATION_PLAN.md"),
    )
    plan = DocumentationValidationPlan(
        required_files=required_files,
        section_requirements=CORE_GOVERNANCE_REQUIRED_SECTIONS,
        template_ids={
            system_doc_rel("README.md"): "SYS-00-IDX",
            system_doc_rel("DOCUMENTATION_STANDARD.md"): "SYS-00-DS",
            system_doc_rel("BUNDLE_TAXONOMY.md"): "SYS-00-BT",
            system_doc_rel("BUNDLE_MIGRATION_PLAN.md"): "SYS-00-BMP",
        },
    )
    checks = validate_documentation_plan(project_root=project_root, plan=plan)
    checks.extend(_extra_core_governance_checks(project_root=project_root))
    failed = [c for c in checks if not c["ok"]]

    validation_rel = system_doc_rel(f"{job_id}-core-governance-validation.md")
    lines = [
        "# Core Governance Validation",
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
            detail = item.get("detail", "")
            path = item.get("path", "")
            lines.append(f"- `{item['check']}` @ `{path}`: {detail}")
    else:
        lines.append("All core governance checks passed.")
    _write_text(project_root / validation_rel, "\n".join(lines) + "\n")

    artifacts = {"SYSTEM_DOCS_VALIDATION": validation_rel}
    if failed:
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=f"Core governance validation failed: {len(failed)} checks failed.",
                artifacts=artifacts,
            )
        return ActionResult(
            status="REJECTED",
            remark=f"Core governance validation failed: {len(failed)} checks failed.",
            artifacts=artifacts,
            reject_code="CORE_GOVERNANCE_VALIDATION_FAILED",
        )

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Core governance validation passed ({len(checks)} checks).",
            artifacts=artifacts,
        )
    return ActionResult(
        status="APPROVED",
        remark=f"Core governance validation passed ({len(checks)} checks).",
        artifacts=artifacts,
    )
