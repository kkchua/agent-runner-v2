"""Package-local actions for 00_repo_master_docs_bootstrap_v1.

These actions are registered via the ``@action()`` decorator and dispatched
by the runner when this workflow package is active. They replace the
former globally registered ``finalize_bootstrap`` and ``validate_system_docs``
actions.
"""

from __future__ import annotations

import re
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.actions.documentation_validation_core import (
    check_file_exists,
    has_frontmatter_field,
    has_section,
    read_file,
)
from agent_runner_v2.codebase_docs import build_snapshot  # Compatibility for existing tests.
from agent_runner_v2.constants import (
    ARTIFACT_KEY_BOOTSTRAP_SUMMARY,
    ARTIFACT_KEY_SYSTEM_DOCS_VALIDATION,
    repo_governance_rel,
)
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action
from agent_runner_v2.workflow_path_contracts import resolve_workflow_output_paths

RULE_SOURCE_OUTPUT_PATHS = "workflows/00_repo_master_docs_bootstrap_v1/output_paths.py:build_output_paths"
RULE_SOURCE_VALIDATION = "workflows/00_repo_master_docs_bootstrap_v1/actions.py"
RULE_SOURCE_REQUIRED_SECTIONS = f"{RULE_SOURCE_VALIDATION}:REPO_MASTER_DOC_REQUIRED_SECTIONS"
RULE_SOURCE_FRONTMATTER = f"{RULE_SOURCE_VALIDATION}:validate_system_docs frontmatter contract"
RULE_SOURCE_EXTRA_CHECKS = f"{RULE_SOURCE_VALIDATION}:_repo_master_doc_extra_checks"
RULE_SOURCE_ASCII = f"{RULE_SOURCE_VALIDATION}:ascii_and_scope_checks"

REPO_GOVERNANCE_SCOPE_MECHANICS_TERMS = (
    "sidecar",
    "daemon",
    "subprocess",
    "prompt/coder",
    "prompt mechanics",
    "coder mechanics",
    "retry loop",
    "retry loops",
    "heartbeat",
    "polling interval",
    "polling intervals",
    "http callbacks",
)


def _contains_legacy_repo_standard_reference(text: str) -> bool:
    sanitized = text.replace("REPO_DOCUMENTATION_STANDARD.md", "")
    return bool(re.search(r"(?<!REPO_)DOCUMENTATION_STANDARD\.md", sanitized))


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _should_validate_frontmatter(*, artifact_key: str, rel_path: str) -> bool:
    if artifact_key in {
        "SYSTEM_DOCS_VALIDATION",
        "CODEBASE_SCAN_SNAPSHOT",
        ARTIFACT_KEY_BOOTSTRAP_SUMMARY,
    }:
        return False
    return rel_path.lower().endswith(".md")


def _workflow_source(step_cfg: dict) -> str:
    bundle = step_cfg.get("_workflow_bundle") if step_cfg else None
    manifest_path = getattr(bundle, "manifest_path", None)
    bundle_root = getattr(bundle, "bundle_root", None)
    if manifest_path:
        return str(manifest_path)
    if bundle_root:
        return str(bundle_root)
    return "unknown"


REPO_MASTER_DOC_REQUIRED_SECTIONS: dict[str, list[str]] = {
    repo_governance_rel("PROJECT_ANALYSIS.md"): [
        "Repo Overview",
        "Codebase Structure",
        "Workflow and Runtime Model",
        "Operational Risks",
        "Architectural Observations",
        "Architecture Posture",
        "Unresolved Documentation Gaps",
    ],
    repo_governance_rel("README.md"): [
        "System Documentation Index",
        "Audience Views",
        "Document Map",
    ],
    repo_governance_rel("REPO_DOCUMENTATION_STANDARD.md"): [
        "Purpose",
        "Audience Model",
        "Document Set",
        "Update Triggers",
        "Validation",
        "Architecture Baseline",
        "Repository-Selected Profile",
        "Migration Mode",
        "Conditional Standards",
    ],
    repo_governance_rel("DEVELOPER_GUIDE.md"): [
        "Development Workflow",
        "Key Commands",
        "Documentation Responsibilities",
        "Architecture Posture",
    ],
    repo_governance_rel("DECISION_LOG.md"): ["Decision Table", "Follow-Up Decisions"],
}


def _ascii_detail(text: str) -> str:
    if text.isascii():
        return "ASCII-only"
    bad = sorted({ch for ch in text if not ch.isascii()})
    preview = ", ".join(repr(ch) for ch in bad[:5])
    return f"non-ASCII characters found: {preview}"


def _contains_any_term(text: str, terms: tuple[str, ...]) -> tuple[bool, str]:
    lower = text.lower()
    for term in terms:
        if term in lower:
            return True, term
    return False, ""


def _required_repo_master_doc_files(*, job_id: str, mode: str) -> dict[str, str]:
    output_paths = resolve_workflow_output_paths(
        template_group="00_repo_master_docs_bootstrap_v1",
        job_id=job_id,
        mode=mode,
    )
    required_files: dict[str, str] = {}
    for artifact_key, rel_path in output_paths.items():
        if artifact_key in {
            ARTIFACT_KEY_BOOTSTRAP_SUMMARY,
            ARTIFACT_KEY_SYSTEM_DOCS_VALIDATION,
            "REVIEW_FILE_SUGGESTED",
        }:
            continue
        required_files[artifact_key] = rel_path
    return required_files


def _repo_master_doc_extra_checks(project_root: Path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    index_path = repo_governance_rel("README.md")
    index_text = read_file(project_root, index_path)
    if index_text is not None:
        checks.append(
            {
                "check": "index_mentions_documentation_standard",
                "path": index_path,
                "ok": "REPO_DOCUMENTATION_STANDARD.md" in index_text,
                "detail": "present" if "REPO_DOCUMENTATION_STANDARD.md" in index_text else "missing",
                "source": RULE_SOURCE_EXTRA_CHECKS,
            }
        )
        checks.append(
            {
                "check": "index_mentions_developer_guide",
                "path": index_path,
                "ok": "DEVELOPER_GUIDE.md" in index_text,
                "detail": "present" if "DEVELOPER_GUIDE.md" in index_text else "missing",
                "source": RULE_SOURCE_EXTRA_CHECKS,
            }
        )
        checks.append(
            {
                "check": "index_avoids_layer1_standard_filename_for_repo_doc",
                "path": index_path,
                "ok": not _contains_legacy_repo_standard_reference(index_text),
                "detail": (
                    "uses repo-level filename"
                    if not _contains_legacy_repo_standard_reference(index_text)
                    else "uses legacy Layer 1 filename `DOCUMENTATION_STANDARD.md` for repo-level standard"
                ),
                "source": RULE_SOURCE_EXTRA_CHECKS,
            }
        )

    repo_standard_path = repo_governance_rel("REPO_DOCUMENTATION_STANDARD.md")
    repo_standard_text = read_file(project_root, repo_standard_path)
    if repo_standard_text is not None:
        checks.append(
            {
                "check": "repo_standard_avoids_legacy_filename",
                "path": repo_standard_path,
                "ok": not _contains_legacy_repo_standard_reference(repo_standard_text),
                "detail": (
                    "uses repo-level filename"
                    if not _contains_legacy_repo_standard_reference(repo_standard_text)
                    else "contains legacy Layer 1 filename `DOCUMENTATION_STANDARD.md` in repo-level standard"
                ),
                "source": RULE_SOURCE_EXTRA_CHECKS,
            }
        )

    for rel_path in (
        repo_governance_rel("PROJECT_ANALYSIS.md"),
        repo_governance_rel("README.md"),
        repo_governance_rel("REPO_DOCUMENTATION_STANDARD.md"),
        repo_governance_rel("DEVELOPER_GUIDE.md"),
        repo_governance_rel("DECISION_LOG.md"),
    ):
        text = read_file(project_root, rel_path)
        if text is None:
            continue
        checks.append(
            {
                "check": "ascii_only_output",
                "path": rel_path,
                "ok": text.isascii(),
                "detail": _ascii_detail(text),
                "source": RULE_SOURCE_ASCII,
            }
        )

    for rel_path in (
        repo_governance_rel("README.md"),
        repo_governance_rel("REPO_DOCUMENTATION_STANDARD.md"),
        repo_governance_rel("DEVELOPER_GUIDE.md"),
    ):
        text = read_file(project_root, rel_path)
        if text is None:
            continue
        found, term = _contains_any_term(text, REPO_GOVERNANCE_SCOPE_MECHANICS_TERMS)
        checks.append(
            {
                "check": "repo_governance_avoids_workflow_mechanics",
                "path": rel_path,
                "ok": not found,
                "detail": "clear" if not found else f"contains workflow/runtime mechanics term: {term}",
                "source": RULE_SOURCE_ASCII,
            }
        )

    return checks


@action("finalize_bootstrap")
def finalize_bootstrap(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    mode = str(step_cfg.get("mode") or "bootstrap")
    job_id = str(state.get("job_id") or "00DOC")
    step = str(state.get("current_step") or "finalize_bootstrap")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="BOOTSTRAP_SUMMARY_METAJSON",
        default_step=step,
    )

    artifacts_state = state.get("artifacts") or {}

    def _artifact_path(key: str) -> str:
        return str(
            artifacts_state.get(key)
            or context.get(f"{key}_PATH")
            or context.get(key)
            or ""
        )

    expected_artifacts = {
        "CODEBASE_SCAN_SNAPSHOT": _artifact_path("CODEBASE_SCAN_SNAPSHOT"),
        "CODEBASE_CHANGE_IMPACT": _artifact_path("CODEBASE_CHANGE_IMPACT"),
        "CODEBASE_INVENTORY": _artifact_path("CODEBASE_INVENTORY"),
        "PROJECT_ANALYSIS": _artifact_path("PROJECT_ANALYSIS"),
        "SYSTEM_DOCS_INDEX": _artifact_path("SYSTEM_DOCS_INDEX"),
        "SYSTEM_DOCS_CHANGE_LOG": _artifact_path("SYSTEM_DOCS_CHANGE_LOG"),
        "VALIDATION_FILE": _artifact_path("VALIDATION_FILE"),
        "SYSTEM_DOCS_VALIDATION": _artifact_path("SYSTEM_DOCS_VALIDATION"),
    }
    missing = [
        f"{artifact_key}: {artifact_rel or '<missing path>'}"
        for artifact_key, artifact_rel in expected_artifacts.items()
        if not artifact_rel or not (project_root / artifact_rel).exists()
    ]
    if missing:
        remark = "Bootstrap finalization failed. Missing required outputs: " + "; ".join(missing)
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=remark,
                artifacts={},
            )
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="BOOTSTRAP_FINALIZATION_FAILED",
        )

    summary_rel = resolve_workflow_output_paths(
        template_group="00_repo_master_docs_bootstrap_v1",
        job_id=job_id,
        mode=mode,
    )[ARTIFACT_KEY_BOOTSTRAP_SUMMARY]
    summary_path = project_root / summary_rel
    summary_lines = [
        "# Bootstrap Summary",
        "",
        f"- Job ID: `{job_id}`",
        f"- Mode: `{mode}`",
        "- Workflow: `00_repo_master_docs_bootstrap_v1`",
        "",
        "## Outputs",
        "",
    ]
    for artifact_key, artifact_rel in expected_artifacts.items():
        summary_lines.append(f"- `{artifact_key}`: `{artifact_rel}`")
    summary_lines.extend(
        [
            "",
            "## Result",
            "",
            "- Master docs bootstrap completed and repository baseline documentation"
            " is ready for governed delivery execution.",
        ]
    )
    _write_text(summary_path, "\n".join(summary_lines) + "\n")

    artifacts = {ARTIFACT_KEY_BOOTSTRAP_SUMMARY: summary_rel}
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark="Bootstrap finalization completed.",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark="Bootstrap finalization completed.",
        artifacts=artifacts,
    )


@action("validate_system_docs")
def validate_system_docs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    mode = str(step_cfg.get("mode") or "bootstrap")
    job_id = str(state.get("job_id") or "00DOC")
    step = str(state.get("current_step") or "validate_master_system_docs")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="SYSTEM_DOCS_VALIDATION_METAJSON",
        default_step=step,
    )

    output_paths = resolve_workflow_output_paths(
        template_group="00_repo_master_docs_bootstrap_v1",
        job_id=job_id,
        mode=mode,
    )
    required_files = _required_repo_master_doc_files(job_id=job_id, mode=mode)

    checks: list[dict[str, object]] = []
    for rel_path in required_files.values():
        ok, detail = check_file_exists(project_root, rel_path)
        checks.append(
            {
                "check": "file_exists",
                "path": rel_path,
                "ok": ok,
                "detail": detail,
                "source": RULE_SOURCE_OUTPUT_PATHS,
            }
        )
    for artifact_key, rel_path in required_files.items():
        if not _should_validate_frontmatter(artifact_key=artifact_key, rel_path=rel_path):
            continue
        content = read_file(project_root, rel_path)
        if content is None:
            continue
        for field in ("template_id", "version", "doc_type"):
            has = has_frontmatter_field(content, field)
            checks.append(
                {
                    "check": "frontmatter_field",
                    "path": rel_path,
                    "field": field,
                    "ok": has,
                    "detail": "found" if has else "missing",
                    "source": RULE_SOURCE_FRONTMATTER,
                }
            )
    for rel_path, sections in REPO_MASTER_DOC_REQUIRED_SECTIONS.items():
        content = read_file(project_root, rel_path)
        if content is None:
            continue
        for section in sections:
            has = has_section(content, section)
            checks.append(
                {
                    "check": "file_section",
                    "path": rel_path,
                    "section": section,
                    "ok": has,
                    "detail": "found" if has else f"missing section `{section}`",
                    "source": RULE_SOURCE_REQUIRED_SECTIONS,
                }
            )
    checks.extend(_repo_master_doc_extra_checks(project_root))

    failed = [c for c in checks if not c["ok"]]
    validation_lines = [
        f"# System Documentation Validation - {job_id}",
        "",
        f"- Mode: `{mode}`",
        f"- Workflow Source: `{_workflow_source(step_cfg)}`",
        f"- Total checks: `{len(checks)}`",
        f"- Passed: `{len(checks) - len(failed)}`",
        f"- Failed: `{len(failed)}`",
        "",
    ]
    if failed:
        validation_lines.append("## Failed Checks")
        validation_lines.append("")
        for check in failed:
            detail = str(check.get("detail", check.get("message", "")))
            path = str(check.get("path", ""))
            field = str(check.get("field", ""))
            section = str(check.get("section", ""))
            source = str(check.get("source", ""))
            suffix = ""
            if path:
                suffix += f" @ `{path}`"
            if field:
                suffix += f" field=`{field}`"
            if section:
                suffix += f" section=`{section}`"
            validation_lines.append(f"- **{check['check']}**{suffix}: {detail}")
            if source:
                validation_lines.append(f"  Rule source: `{source}`")
    else:
        validation_lines.append("**All checks passed.**")

    validation_rel = output_paths.get("SYSTEM_DOCS_VALIDATION", "")
    if validation_rel:
        _write_text(project_root / validation_rel, "\n".join(validation_lines) + "\n")

    artifacts: dict[str, str] = {}
    if validation_rel:
        artifacts["SYSTEM_DOCS_VALIDATION"] = validation_rel

    if failed:
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=f"System docs validation failed: {len(failed)} checks failed",
                artifacts=artifacts,
            )
        return ActionResult(
            status="REJECTED",
            remark=f"System docs validation failed: {len(failed)} checks failed",
            artifacts=artifacts,
            reject_code="SYSTEM_DOCS_VALIDATION_FAILED",
        )

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"System docs validation passed ({len(checks)} checks).",
            artifacts=artifacts,
        )
    return ActionResult(
        status="APPROVED",
        remark=f"System docs validation passed ({len(checks)} checks).",
        artifacts=artifacts,
    )
