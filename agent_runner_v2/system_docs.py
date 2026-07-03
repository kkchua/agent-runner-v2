from __future__ import annotations

"""
system_docs.py - Deterministic renderers for audience-oriented system documentation.
"""

from datetime import datetime
from pathlib import PurePosixPath


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
        "source": str(snapshot.get("architecture_profile_source") or "project_analysis.md"),
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
    return (
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
        + "- Developers and maintainers: bootstrap system docs and `docs/codebase/`\n"
        + "- Operators and support engineers: bootstrap system docs\n\n"
        + "## Document Set\n\n"
        + "- [`DOCUMENTATION_STANDARD.md`](./DOCUMENTATION_STANDARD.md)\n"
        + "- [`SYSTEM_OVERVIEW.md`](./SYSTEM_OVERVIEW.md)\n"
        + "- [`BUSINESS_CAPABILITIES.md`](./BUSINESS_CAPABILITIES.md)\n"
        + "- [`FUNCTIONAL_SPEC.md`](./FUNCTIONAL_SPEC.md)\n"
        + "- [`NON_FUNCTIONAL_REQUIREMENTS.md`](./NON_FUNCTIONAL_REQUIREMENTS.md)\n"
        + "- [`BUNDLE_TAXONOMY.md`](./BUNDLE_TAXONOMY.md)\n"
        + "- [`BUNDLE_MIGRATION_PLAN.md`](./BUNDLE_MIGRATION_PLAN.md)\n"
        + "- [`SYSTEM_CONTEXT.md`](./SYSTEM_CONTEXT.md)\n"
        + "- [`COMPONENT_ARCHITECTURE.md`](./COMPONENT_ARCHITECTURE.md)\n"
        + "- [`DECISION_LOG.md`](./DECISION_LOG.md)\n"
        + "- [`SYSTEM_FILE_STRUCTURE.md`](./SYSTEM_FILE_STRUCTURE.md)\n"
        + "- [`DEVELOPER_GUIDE.md`](./DEVELOPER_GUIDE.md)\n"
        + "- [`RUNBOOK.md`](./RUNBOOK.md)\n\n"
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
    return (
        _frontmatter(title="Documentation Standard", workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-DS")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Documentation Standard\n\n"
        + "## Purpose\n\n"
        + "## Audience Model\n\n"
        + "## Document Set\n\n"
        + "## Update Triggers\n\n"
        + "## Validation\n\n"
        + "This standard defines the target software documentation set for stakeholder, functional, architecture, engineering, and operations audiences.\n\n"
        + "## Layer Model\n\n"
        + "- `docs/system/00_governance/bootstrap/` contains business, functional, architecture, and governance narrative documents.\n"
        + "- `docs/codebase/` contains generated inventory, module docs, component docs, and change records.\n"
        + "- `docs/delivery/` contains delivery workflow outputs and generated agents.\n\n"
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
        + "2. Keep repo-local `docs/delivery/` and `docs/codebase/` generated from workflow bundles.\n"
        + "3. Record bundle selection in `~/.ukbe-runner` during init.\n"
        + "4. Add optional domain overlays only after core and workflow bundles are stable.\n"
    )


def render_bundle_migration_plan(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="Bundle Migration Plan", workflow=workflow, step=snapshot["step"], audience="all", template_id="SYS-00-BMP")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Bundle Migration Plan\n\n"
        + "## Goal\n\n"
        + "Move the runner to a global system-doc source of truth plus repo-local delivery/codebase docs.\n\n"
        + "## Migration Modes\n\n"
        + _table(
            ["Mode", "Meaning"],
            [
                ["native", "The repository already follows the selected profile and only needs normal baseline upkeep."],
                ["provisional", "The repository has no declared standard yet and should stay under the universal baseline until a profile is chosen."],
                ["targeted_migration", "The repository is being incrementally refactored toward a chosen target profile."],
            ],
        )
        + "## Repository Rule\n\n"
        + "Do not force DDD or EDA as unconditional defaults; select them only when the repo profile and migration plan require them.\n\n"
        + "## Phases\n\n"
        + _table(
            ["Phase", "Focus"],
            [
                ["Phase 1", "Core bundle and global system docs"],
                ["Phase 2", "Delivery/codebase scaffold bundle"],
                ["Phase 3", "CLI install/init integration"],
                ["Phase 4", "Optional domain overlays"],
            ],
        )
        + "## Stability Rule\n\n"
        + "The `00_master_docs_bootstrap_v1` and `10_execution_scaffold_v1` workflows must be stable before later phases are activated.\n"
    )


def render_system_overview(snapshot: dict, *, repo_name: str) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="System Overview", workflow=workflow, step=snapshot["step"], audience="stakeholder", template_id="SYS-00-SO")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# System Overview\n\n"
        + "## Purpose\n\n"
        + "## Scope\n\n"
        + "## Primary Flows\n\n"
        + "## Key Risks\n\n"
        + "## Architecture Profile\n\n"
        + _architecture_profile_table(snapshot)
        + "The universal ecosystem baseline applies to every repository. If the repository has not declared a stable architecture standard, treat the current posture as provisional and use the target profile to drive migration planning.\n\n"
        + "## Executive Summary\n\n"
        + f"`{repo_name}` is a software system with generated workflow, codebase, and operational governance. This overview is derived from the repository structure and should be refined with product-specific domain language.\n\n"
        + "## What The System Contains Today\n\n"
        + _table(
            ["Area", "Observed Count"],
            [[area, str(count)] for area, count in _module_area_rows(snapshot)],
        )
        + "## Business Value Hypothesis\n\n"
        + "- Standardize how work is planned, executed, reviewed, and documented.\n"
        + "- Reduce undocumented code and process drift.\n"
        + "- Improve traceability from high-level intent to implementation artifacts.\n\n"
        + "## Scope Boundaries\n\n"
        + "- Included: repository workflows, runtime components, documentation controls, and automation entrypoints.\n"
        + "- Not inferred here: product-specific commercial goals, customer segmentation, and contractual commitments.\n"
        + "## Bundle Composition\n\n"
        + "- The system is installed as a bundle set: core + optional domain overlay + active workflow bundle.\n"
        + "- The CLI materializes the bundle set under `%USERPROFILE%\\.ukbe-runner` and loads the active workflow bundle at runtime.\n"
        + "- Repo-local docs are generated from the same source bundle so the set remains consistent across projects.\n"
    )


def render_business_capabilities(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    rows = [[name, prefix, str(step_count)] for name, prefix, step_count in _workflow_rows(snapshot)]
    return (
        _frontmatter(title="Business Capabilities", workflow=workflow, step=snapshot["step"], audience="stakeholder", template_id="SYS-00-BC")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Business Capabilities\n\n"
        + "## Capability Map\n\n"
        + _table(["Capability / Workflow Family", "Job Prefix", "Step Count"], rows)
        + "## Interpretation Notes\n\n"
        + "- Each workflow family represents an operational capability exposed by the repository.\n"
        + "- Capability naming should be refined with business terminology if the system serves a product domain beyond engineering workflow orchestration.\n"
    )


def render_functional_spec(snapshot: dict, *, repo_name: str) -> str:
    workflow = _workflow_label(snapshot)
    rows = [[name, f"{step_count} steps", "See workflow and architecture docs"] for name, _, step_count in _workflow_rows(snapshot)]
    return (
        _frontmatter(title="Functional Specification", workflow=workflow, step=snapshot["step"], audience="functional", template_id="SYS-00-FS")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Functional Specification\n\n"
        + "## System Purpose\n\n"
        + f"The `{repo_name}` system coordinates repository workflows, artifacts, and validation logic.\n\n"
        + "## Functional Capabilities\n\n"
        + _table(["Function", "Observed Workflow Size", "Notes"], rows)
        + "## Actors\n\n"
        + "- Stakeholder or sponsor approving delivery direction.\n"
        + "- Functional analyst defining workflow and output requirements.\n"
        + "- Developer or maintainer executing tasks and documentation updates.\n"
        + "- Operator monitoring job execution and incident recovery.\n\n"
        + "## Core Behaviors\n\n"
        + "- Initialize and resume multi-step workflows.\n"
        + "- Validate required artifacts and status transitions.\n"
        + "- Produce documentation and change records from repository state.\n"
        + "- Maintain traceability across planning, execution, and review.\n"
    )


def render_nfr(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="Non-Functional Requirements", workflow=workflow, step=snapshot["step"], audience="functional", template_id="SYS-00-NFR")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Non-Functional Requirements\n\n"
        + _table(
            ["Category", "Baseline Requirement", "Rationale"],
            [
                ["Traceability", "Workflow artifacts must remain linkable across job runs.", "Supports review and auditability."],
                ["Operability", "Job status and step outputs must be inspectable from the runner workspace.", "Supports manual troubleshooting."],
                ["Performance", "Deterministic scan workflows should complete without LLM dependency.", "Controls cost and runtime variance."],
                ["Maintainability", "Generated docs should be separated by audience and layer.", "Reduces ambiguity between system and codebase documentation."],
                ["Reliability", "Validation should reject incomplete documentation sets.", "Prevents false-complete runs."],
            ],
        )
    )


def render_system_context(snapshot: dict, *, repo_name: str) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="System Context", workflow=workflow, step=snapshot["step"], audience="architect", template_id="SYS-03-CTX")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# System Context\n\n"
        + "## Context Statement\n\n"
        + f"`{repo_name}` operates as a repository-local orchestration and documentation system. It reads project files, manages workflow jobs, writes generated artifacts, and exposes operational entrypoints through scripts and CLI commands.\n\n"
        + "## Primary Context Elements\n\n"
        + _table(
            ["Element", "Role"],
            [
                ["Repository source tree", "Primary system of record for code and docs"],
                ["Workflow bundle definitions", "Define steps, prompts, and action contracts"],
                ["Runner job state", "Tracks execution progress and review state"],
                ["Generated docs", "Publishes system, codebase, and delivery documentation"],
                ["Scripts and CLI", "Provide human and automation entrypoints"],
            ],
        )
    )


def render_component_architecture(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    rows = [[area, str(count), "See docs/codebase/03_components or module docs"] for area, count in _module_area_rows(snapshot)]
    return (
        _frontmatter(title="Component Architecture", workflow=workflow, step=snapshot["step"], audience="architect", template_id="SYS-03-CA")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Component Architecture\n\n"
        + "## Component Groups\n\n"
        + _table(["Component Group", "Module Count", "Reference"], rows)
        + "## Architectural Notes\n\n"
        + "- The system mixes workflow orchestration, deterministic actions, runtime context management, and generated documentation.\n"
        + "- DDD, EDA, API-first, or monolith-style guidance should be interpreted through the repo-selected profile, not treated as a universal default.\n"
        + "- Detailed file-level ownership stays in `docs/codebase/`, while this document stays at the component boundary level.\n"
    )


def render_decision_log(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="Decision Log", workflow=workflow, step=snapshot["step"], audience="architect", template_id="SYS-03-DL")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Decision Log\n\n"
        + _table(
            ["Decision ID", "Decision", "Current Position", "Evidence"],
            [
                ["DEC-001", "Separate system docs from codebase docs", "Accepted", "Needed to support multiple audiences cleanly."],
                ["DEC-002", "Use deterministic bootstrap for baseline docs", "Accepted", "Reduces cost and ensures repeatable output."],
                ["DEC-003", "Keep codebase inventory as the low-level source layer", "Accepted", "Provides direct traceability to repository files."],
            ],
        )
        + "## Follow-Up Decisions Needed\n\n"
        + "- Confirm product-domain terminology for stakeholder-facing documents.\n"
        + "- Decide whether higher-level docs should remain deterministic or use a review LLM pass.\n"
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
        + "- `docs/system/00_governance/bootstrap/` should hold generated master-doc narratives and governance artifacts.\n"
        + "- `docs/codebase/` should hold generated technical reference artifacts.\n"
        + "- `docs/delivery/` should hold delivery workflow outputs and operational handoff material.\n"
    )


def render_developer_guide(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    workflow_rows = [[name, str(step_count)] for name, _, step_count in _workflow_rows(snapshot)]
    return (
        _frontmatter(title="Developer Guide", workflow=workflow, step=snapshot["step"], audience="developer", template_id="ENG-01-DG")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Developer Guide\n\n"
        + "## Development Workflow\n\n"
        + "## Key Commands\n\n"
        + "## Documentation Responsibilities\n\n"
        + "## Architecture Posture\n\n"
        + "## Start Here\n\n"
        + "- Read `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md` for the high-level system shape.\n"
        + "- Read `docs/codebase/01_inventory/codebase_inventory.md` for the file-level map.\n"
        + "- Use `docs/codebase/02_modules/` for module contracts and dependencies.\n\n"
        + "## Workflow Families\n\n"
        + _table(["Workflow Family", "Step Count"], workflow_rows)
        + "## Working Rules\n\n"
        + "- Refresh `docs/codebase/` after code drift or implementation changes.\n"
        + "- Update system-level docs when product behavior, architecture, or operating model changes.\n"
        + "- Record the universal baseline, repo profile, and migration mode in project analysis before treating DDD or EDA as active standards.\n"
        + "- Treat `core` docs as universal, `domain` docs as optional overlays, and `workflow` prompts/templates as executable assets.\n"
        + "- When adding a new repo class, create a new domain bundle rather than copying and mutating the core bundle.\n"
        + "- Keep developer and operator docs separate from stakeholder-facing material.\n"
        + "- Runtime jobs and sidecars live under `%USERPROFILE%\\.ukbe-runner\\jobs\\` and `%USERPROFILE%\\.ukbe-runner\\workflows\\`; do not write generated runtime files into the repo root.\n"
        + "- Use the project venv explicitly for local validation and testing. Prefer `.venv\\Scripts\\python.exe` or `.venv\\Scripts\\pytest.exe` over ambient `python` / `py` commands.\n"
    )


def render_runbook(snapshot: dict) -> str:
    workflow = _workflow_label(snapshot)
    return (
        _frontmatter(title="Runbook", workflow=workflow, step=snapshot["step"], audience="operations", template_id="OPS-01-RB")
        + _banner(workflow=workflow, step=snapshot["step"])
        + "# Runbook\n\n"
        + "## Operations Scope\n\n"
        + "## Routine Procedures\n\n"
        + "## Failure Handling\n\n"
        + "## Operating Model\n\n"
        + "- Use runner scripts or CLI entrypoints to start workflow jobs.\n"
        + "- If a repository standard is not explicit, keep the universal baseline active and record the repo profile as provisional until project analysis or governance updates resolve it.\n"
        + "- Inspect `%USERPROFILE%\\.ukbe-runner\\jobs\\<template_group>\\<job_id>\\` for job-state troubleshooting.\n"
        + "- The global runner home is `%USERPROFILE%\\.ukbe-runner`; that is where job state, bundles, logs, and sidecars are expected.\n"
        + "- Bundle inventory lives under `%USERPROFILE%\\.ukbe-runner\\bundles\\` and the active runtime workflow bundle under `%USERPROFILE%\\.ukbe-runner\\workflows\\`.\n"
        + "- Inspect `docs/codebase/04_changes/` and `docs/system/00_governance/bootstrap/` for generated documentation runs.\n\n"
        + "## Python Execution SOP\n\n"
        + "1. Use the repository venv explicitly for any Python command run from this workspace.\n"
        + "2. Prefer `.venv\\Scripts\\python.exe -m pytest` for tests and `.venv\\Scripts\\python.exe -m py_compile <file>` for syntax checks.\n"
        + "3. Do not rely on ambient `python` or `py` resolution when validating repository code.\n"
        + "4. If a command fails under the ambient interpreter, rerun it with the venv interpreter before treating it as a repository issue.\n\n"
        + "## Common Checks\n\n"
        + _table(
            ["Check", "Location", "Purpose"],
            [
                ["Job status", "%USERPROFILE%\\.ukbe-runner\\jobs\\...\\job.json", "Verify current step, failures, and artifacts"],
                ["Bundle manifest", "%USERPROFILE%\\.ukbe-runner\\bundles\\bundle-set.json", "Verify installed core/domain/workflow bundle selection"],
                ["Generated codebase docs", "docs/codebase/", "Verify low-level documentation refresh"],
                ["Generated system docs", "docs/system/00_governance/bootstrap/", "Verify audience-facing documentation refresh"],
            ],
        )
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
