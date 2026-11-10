from __future__ import annotations

"""
system_docs.py - Deterministic renderers for audience-oriented system documentation.
"""

from datetime import datetime
from pathlib import PurePosixPath

from .doc_paths import codebase_doc_rel, delivery_doc_rel, system_doc_rel
from .doc_text import sanitize_ascii


SYSTEM_BOOTSTRAP_ROOT = system_doc_rel()
CODEBASE_ROOT = codebase_doc_rel()
DELIVERY_ROOT = delivery_doc_rel()


def _today_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _frontmatter(*, title: str, workflow: str, step: str, audience: str, template_id: str | None = None) -> str:
    template_line = f'template_id: "{template_id}"\n' if template_id else ""
    return (
        "---\n"
        f'title: "{title}"\n'
        + template_line
        + 'status: "active"\n'
        + 'managed_by: "workflow-generated"\n'
        + f'generated: "{_today_iso()}"\n'
        + f'workflow: "{workflow}"\n'
        + f'step: "{step}"\n'
        + f'audience: "{audience}"\n'
        + "---\n\n"
    )


def _banner(*, workflow: str, step: str) -> str:
    return (
        f"> Managed by workflow: `{workflow}` / step: `{step}`\n"
        "> This file is workflow-generated and protected from manual edits.\n\n"
    )


def _bucket_rows(snapshot: dict) -> list[tuple[str, int]]:
    rows: dict[str, int] = {}
    for item in snapshot["items"]:
        top = PurePosixPath(item.rel_path).parts[0]
        rows[top] = rows.get(top, 0) + 1
    return sorted(rows.items(), key=lambda row: row[0])


def _workflow_rows(snapshot: dict) -> list[tuple[str, str, int]]:
    rows = []
    for family in snapshot["workflow_families"]:
        rows.append((family["family_name"], family["job_prefix"], len(family["steps"])))
    return rows


def _module_area_rows(snapshot: dict) -> list[tuple[str, int]]:
    areas: dict[str, int] = {}
    for module in snapshot["python_modules"]:
        area = str(module["module_area"])
        areas[area] = areas.get(area, 0) + 1
    return sorted(areas.items(), key=lambda row: row[0])


def _table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out) + "\n\n"


def _workflow_label(snapshot: dict) -> str:
    return str(snapshot.get("workflow_name") or snapshot.get("mode") or "bootstrap")


def _architecture_profile(snapshot: dict) -> dict[str, str]:
    return {
        "baseline": str(snapshot.get("architecture_baseline") or "universal baseline"),
        "current_profile": str(snapshot.get("architecture_profile") or "provisional"),
        "target_profile": str(snapshot.get("architecture_target_profile") or "repo-selected"),
        "migration_mode": str(snapshot.get("architecture_migration_mode") or "targeted_migration"),
        "source": str(snapshot.get("architecture_profile_source") or "PROJECT_ANALYSIS.md"),
    }


def _architecture_profile_table(snapshot: dict) -> str:
    profile = _architecture_profile(snapshot)
    return _table(
        ["Aspect", "Value"],
        [
            ["Baseline", profile["baseline"]],
            ["Current profile", profile["current_profile"]],
            ["Target profile", profile["target_profile"]],
            ["Migration mode", profile["migration_mode"]],
            ["Source of truth", profile["source"]],
        ],
    )


def render_system_index(snapshot: dict, *, repo_name: str) -> str:
    workflow = _workflow_label(snapshot)
    return sanitize_ascii(
        _frontmatter(title="System Documentation Index", workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-IDX")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# System Documentation Index\n\n"
        + "## System Documentation Index\n\n"
        + "This documentation set separates bootstrap-staged system docs from codebase-level generated docs.\n\n"
        + "## Audience Views\n\n"
        + "### Bundle Model\n\n"
        + "- Core bundle: universal governance, standards, and runtime documentation.\n"
        + "- Domain bundle: optional overlays such as frontend, backend, or content.\n"
        + "- Workflow bundle: prompts, schemas, and execution templates for the runner.\n\n"
        + "### Architecture Posture\n\n"
        + "- Universal baseline: always on.\n"
        + "- Repo-selected profile: recorded in analysis when the repository standard is explicit or being migrated.\n"
        + "- DDD and EDA: conditional, not unconditional defaults.\n\n"
        + "## Document Map\n\n"
        + "### Primary Audiences\n\n"
        + "- Stakeholders and sponsors: bootstrap system docs\n"
        + "- Functional analysts and QA: bootstrap system docs\n"
        + "- Architects and senior engineers: bootstrap system docs\n"
        + f"- Developers and maintainers: bootstrap system docs and `{CODEBASE_ROOT}`\n"
        + "- Operators and support engineers: bootstrap system docs\n\n"
        + "## Document Set\n\n"
        + "- [`DOCUMENTATION_STANDARD.md`](./DOCUMENTATION_STANDARD.md)\n"
        + "- [`BUNDLE_TAXONOMY.md`](./BUNDLE_TAXONOMY.md)\n"
        + "- [`RUNTIME_GOVERNANCE.md`](./RUNTIME_GOVERNANCE.md)\n\n"
        + "## Repository Summary\n\n"
        + f"Repository: `{repo_name}`\n\n"
        + _table(
            ["Measure", "Value"],
            [
                ["Python modules", str(len(snapshot["python_modules"]))],
                ["Workflow families", str(len(snapshot["workflow_families"]))],
                ["Scanned files", str(len(snapshot["items"]))],
                ["Generation mode", workflow],
            ],
        )
    )


def render_documentation_standard(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    return sanitize_ascii(
        _frontmatter(title="Documentation Standard", workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-DS")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Documentation Standard\n\n"
        + "## Purpose\n\n"
        + "## Audience Model\n\n"
        + "## Document Set\n\n"
        + "## Update Triggers\n\n"
        + "## Validation\n\n"
        + "This standard defines the Layer 1 ecosystem governance set only.\n\n"
        + "## Layer Model\n\n"
        + f"- `{SYSTEM_BOOTSTRAP_ROOT}` contains the four Layer 1 governance docs only.\n"
        + f"- `{CODEBASE_ROOT}` contains generated inventory, module docs, component docs, and change records.\n"
        + f"- `{DELIVERY_ROOT}` contains delivery workflow outputs and generated agents.\n\n"
        + "The Layer 1 document set is limited to `README.md`, `DOCUMENTATION_STANDARD.md`, `BUNDLE_TAXONOMY.md`, and `RUNTIME_GOVERNANCE.md`.\n\n"
        + "## Architecture Baseline\n\n"
        + "The ecosystem baseline applies to every repository: documentation first, traceable updates, deterministic validation, secure defaults, and visible operational readiness.\n\n"
        + "## Repo-Selected Profile\n\n"
        + "A repository may declare a profile such as monolith, modular monolith, microservices, event-driven, API-first, pipeline, or provisional. Profile choice determines which architecture standards are active.\n\n"
        + "## Migration Mode\n\n"
        + "Existing repositories that do not yet declare a clear standard should be treated as provisional and migrated deliberately toward a target profile rather than forcing DDD or EDA everywhere.\n\n"
        + "## Conditional Standards\n\n"
        + "- DDD, EDA, and similar architecture patterns are enabled when the selected repo profile calls for them.\n"
        + "- The universal baseline remains in force even when the repo profile is provisional or changing.\n\n"
        + "## Bundle Taxonomy\n\n"
        + "- `core`: shared docs and runtime standards used by every repo.\n"
        + "- `domain`: optional repo-class overlays such as frontend, backend, content, data, or platform.\n"
        + "- `workflow`: runner prompts, schemas, and template groups that execute tasks.\n\n"
        + "## Init Rules\n\n"
        + "- `ukbe-run-agent init` installs the selected core/domain/workflow bundle set into `%USERPROFILE%\\.ukbe-runner`.\n"
        + "- The active runtime workflow bundle remains the load target for `run` and worker commands.\n"
        + "- Protected generated docs are owned by the workflow that creates them and should not be edited manually.\n\n"
        + "## Maintenance Rules\n\n"
        + "- System-level narrative docs should be refreshed when architecture, scope, or user-visible behavior changes.\n"
        + "- Codebase docs should be refreshed after source-code drift or as part of implementation workflows.\n"
        + "- Operational docs should be refreshed when deployment, monitoring, or incident procedures change.\n"
    )


def render_bundle_taxonomy(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="Bundle Taxonomy", workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-BT")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Bundle Taxonomy\n\n"
        + "## Purpose\n\n"
        + "The bundle taxonomy separates the global core system docs from optional domain overlays and executable workflow bundles.\n\n"
        + "## Bundle Types\n\n"
        + _table(
            ["Bundle", "Responsibility"],
            [
                ["core", "Universal governance, standards, and global system docs"],
                ["domain", "Optional repo-class overlays such as frontend, backend, content, data, or platform"],
                ["workflow", "Prompt templates, schemas, and workflow execution definitions"],
            ],
        )
        + "## Profile Model\n\n"
        + _architecture_profile_table(snapshot)
        + "## Conditional Standards\n\n"
        + "- The repo profile selects whether architecture patterns such as DDD or EDA are active.\n"
        + "- If the repo profile is provisional, the universal baseline stays active while the target profile is recorded for migration.\n\n"
        + "## Migration Phases\n\n"
        + "1. Establish the core bundle as the authoritative global system-doc source.\n"
        + f"2. Keep repo-local `{DELIVERY_ROOT}` and `{CODEBASE_ROOT}` generated from workflow bundles.\n"
        + "3. Record bundle selection in `~/.ukbe-runner` during init.\n"
        + "4. Add optional domain overlays only after core and workflow bundles are stable.\n"
    )


def render_runtime_governance(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="Runtime Governance", workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-RG")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Runtime Governance\n\n"
        + "## Purpose\n\n"
        + "Define the steady-state global runtime control model for published bundles and shared governance assets.\n\n"
        + "## Runtime Scope Model\n\n"
        + "- Shared runtime code provides generic path helpers, validation hooks, and execution infrastructure.\n"
        + "- Workflow bundles own workflow-specific artifact path contracts, generated document inventories, and review or validation path rules.\n\n"
        + "## Bundle Publish And Install Model\n\n"
        + "- The canonical runtime source is the published global bundle copy under `%USERPROFILE%\\.ukbe-runner`.\n"
        + "- Install and init materialize the active bundle set into the global runtime home before execution begins.\n\n"
        + "## Registry Control Plane\n\n"
        + "- Bundle selection and activation are controlled through the global registry and installed bundle metadata.\n"
        + "- Shared runtime must not depend on workflow-name-specific path resolution branches as the steady-state model.\n\n"
        + "## Plugin Bundle Control Model\n\n"
        + "- Plugin workflow bundles may be `single-workflow` bundles or `multi-workflow` bundles.\n"
        + "- Bundle class and ownership boundaries are defined by Layer 1 governance, not by repository-local conventions.\n\n"
        + "## Role And Connection Resolution\n\n"
        + "- Coder roles, adapter bindings, and runtime connection resolution are shared runtime concerns.\n"
        + "- Workflow bundles consume those shared services without taking ownership of the global control plane.\n\n"
        + "## Artifact Ownership Enforcement\n\n"
        + "- Shared runtime may enforce generic ownership boundaries.\n"
        + "- Workflow bundles own workflow-specific artifact path contracts and protected generated document inventories.\n\n"
        + "## Execution Mode Parity\n\n"
        + "- Manual, submit, and daemon execution modes must resolve the same active published bundle contract.\n"
        + "- Runtime policy must not depend on repo-local fallback loading or dual-path discovery.\n\n"
        + "## Validation Gates\n\n"
        + "- Bundle publication, installation, and execution must pass schema, ownership, and contract validation before use.\n"
        + "- Centralized workflow-family path registries are not the steady-state ownership model.\n\n"
        + "## Change Control\n\n"
        + "- Shared runtime changes may extend generic helpers and enforcement only.\n"
        + "- Changes to workflow-generated output paths must be made in the owning workflow bundle, not in shared runtime path tables.\n"
    )


def render_system_file_structure(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    rows = [[bucket, str(count)] for bucket, count in _bucket_rows(snapshot)]
    return (
        _frontmatter(title="System File Structure", workflow=workflow, step=snapshot["step"], audience="architect", template_id="SYS-03-SF")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# System File Structure\n\n"
        + "## Repository Structure\n\n"
        + "## Top-Level Directories\n\n"
        + "## Documentation Locations\n\n"
        + "## Top-Level Structure\n\n"
        + _table(["Top-Level Path", "Observed File Count"], rows)
        + "## Structure Guidance\n\n"
        + "- `agent_runner_v2/` contains implementation modules.\n"
        + f"- `{SYSTEM_BOOTSTRAP_ROOT}` should hold generated master-doc narratives and governance artifacts.\n"
        + f"- `{CODEBASE_ROOT}` should hold generated technical reference artifacts.\n"
        + f"- `{DELIVERY_ROOT}` should hold delivery workflow outputs and operational handoff material.\n"
    )


def render_system_docs_change_log(snapshot: dict, *, repo_name: str, doc_paths: list[str]) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="System Docs Change Log", workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-CL")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# System Docs Change Log\n\n"
        + "## Summary\n\n"
        + f"System-level documentation was generated or refreshed for `{repo_name}`.\n\n"
        + "## Updated Documents\n\n"
        + _table(["Path", "Change"], [[path, "generated or refreshed"] for path in doc_paths])
    )


def render_system_docs_validation(snapshot: dict, *, title: str, checks: list[tuple[str, bool, str]]) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title=title, workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-VAL")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# System Docs Validation\n\n"
        + _table(
            ["Check", "Status", "Notes"],
            [[name, "pass" if ok else "fail", note] for name, ok, note in checks],
        )
    )
