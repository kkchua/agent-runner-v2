---
title: "Project Analysis - agent-runner-v2"
template_id: "PROJECT-ANALYSIS-v1"
status: "active"
generated: "2026-07-04T06:33:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "project_analysis"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Domain

**agent-runner-v2** is a standalone LLM workflow orchestration engine extracted from the UKBE platform. It runs structured multi-step AI workflows (Claude, Codex, Qwen, and aliased models) with deterministic runner actions, review loops, retries, approval gates, and `meta.json` sidecar-based artifact validation.

The system serves three primary operational modes:

1. **Local CLI execution** — `ukbe-run-agent run` for ad-hoc workflow execution against a target project, with `--project-root` and `--target-project-root` support.
2. **Backend-connected worker operation** — `ukbe-run-agent worker`, `poll`, `execute-step` for server-driven task consumption, result submission, and heartbeat emission.
3. **Workstation supervision** — `ukbe-run-agent daemon` for persistent worker processes that claim work, spawn child execute-step processes, and track child state.

The delivery lifecycle spans multiple workflow families:

| Workflow Family | Purpose | Step Count |
|-----------------|---------|------------|
| `20_initiative_intake_v1` | Requirement capture and pre-init refinement | 5 |
| `21_bug_fix_intake_v1` | Bug triage and fix workflow | 7 |
| `30_delivery_planning_v1` | Plan creation, task-graph decomposition, task decomposition | 10 |
| `31_task_execution_v1` | Implementation, review, validation, documentation sync | 12 |
| `40_documentation_sync_v1` | Current-truth reconciliation of code against documentation | 4 |
| `10_execution_scaffold_v1` | Generates governance templates, SOPs, status rules, agent contracts | 13 |
| `00_master_docs_bootstrap_v1` | Master documentation bootstrap for existing repos | 10 |

Additional workflow families for content-generation pipelines:
- `image_csv_gen_v1/v2` — CSV-based image prompt generation for ComfyUI
- `tiktok_video_pipeline_v1` — TikTok video production pipeline
- `videoxpress_gen_v1` — Video workflow generation via ComfyUI nodes

The system is purpose-built for **AI-assisted software delivery governance** — ensuring code changes and documentation updates are co-evolved through structured LLM-driven steps with deterministic validation gates.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.11+ |
| **Packaging** | setuptools with `pyproject.toml` |
| **CLI** | `ukbe-run-agent` entry point resolving to `agent_runner_v2.run_agent:main` |
| **LLM Providers** | Claude (Anthropic), Codex, Qwen (via CLI adapters and API) |
| **Test Framework** | pytest 8.2+ with pytest-cov |
| **Runtime Home** | `%USERPROFILE%\.ukbe-runner\` (Windows-native global runner home) |
| **State Management** | `job.json` lifecycle via `JobState` class (current schema version: 6) |
| **Result Channel** | `meta.json` sidecar (v2 schema) — the only structured output channel |
| **Backend Protocol** | HTTP API for worker poll/submit; child process management via subprocess |
| **Cross-Platform** | Windows (primary), Linux/macOS (daemon, signal handling) |
| **External Services** | ComfyUI (image/video generation via `submit_comfyui` action) |

**Zero external runtime dependencies** — the package is self-contained with only dev-time test dependencies (`pytest`, `pytest-cov`). This minimizes supply-chain risk and makes the runner highly portable.

## Complexity

| Dimension | Assessment | Evidence |
|-----------|-----------|----------|
| **Module count** | Medium-high | 49 Python source modules, 80+ bootstrap workflow files, 43 scripts |
| **Workflow count** | High | 9+ workflow families with 100+ prompt templates |
| **Execution modes** | High | 3 distinct modes (local run, backend worker/daemon) |
| **State management** | Medium-high | `job.json` lifecycle with review loops (max 2 refine), replan (max 1), schema version 6 |
| **Cross-project** | Medium | `--target-project-root` enables scaffold into different repos |
| **Platform concerns** | Medium | Windows signal handling (`TerminateProcess`), process orphan prevention, WSL daemon support |
| **Template system** | High | `template_groups.py` at ~3,000 lines of Python dict-based workflow definitions |
| **Documentation burden** | High | 49 module docs, 5 component docs, 74+ doc files tracked in inventory |
| **Runner actions** | High | 18 deterministic actions across validation, sync, copy, promote, execute |

**Overall complexity: High.** The system is a full workflow orchestration engine with multiple execution models, a rich template system, bidirectional documentation governance, and content-generation pipeline support.

## Recommended Workflow Scope

For the `10_execution_scaffold_v1` workflow targeting this repository:

| Scope Item | Recommendation |
|------------|---------------|
| **Delivery governance** | Full scaffold — generate `docs/delivery/` with all 7 folders, SOP, status rules, agent contracts, template registry |
| **Codebase governance** | Merge + extend — existing `docs/codebase/02_modules/` and `03_components/` are comprehensive; scaffold `00_standards/` with SOP and status rules |
| **Agent contracts** | Generate all 6 agent role documents under `docs/delivery/00_standards/` |
| **Template registry** | Generate with cross-references to both delivery and codebase template families under `docs/system/00_governance/bootstrap/templates/` |
| **Existing docs reconciliation** | Validate and merge, do not overwrite. Existing module/component docs generated by `00_master_docs_bootstrap_v1` are comprehensive. |
| **System docs** | Extend `docs/system/00_governance/bootstrap/` with template registry; preserve existing bootstrap docs (BUNDLE_TAXONOMY, COMPONENT_ARCHITECTURE, etc.) |

## Recommended Agent Roles

| Role | Responsibility | Coder Model |
|------|---------------|-------------|
| **Project Analyst** | Auto-discover project context, produce `PROJECT_ANALYSIS` | qwen |
| **SOP Author** | Generate `WORKFLOW_SOP_v1.md` and `DELIVERY_STATUS_RULES_v1.md` | claude |
| **Codebase SOP Author** | Generate `CODEBASE_DOC_SOP_v1.md` and `CODEBASE_DOC_STATUS_RULES_v1.md` | claude |
| **Template Generator** | Generate all delivery and codebase templates from registry | qwen |
| **Agent Contract Writer** | Produce `AGENTS.md` and individual `DELIVERY_AGENT_*.md` files | claude |
| **Reviewer (SOP)** | Validate SOP structure, state machine, forbidden transitions, authority precedence | claude |
| **Reviewer (Templates)** | Validate template completeness, section presence, cross-references | qwen |
| **Reviewer (Agents)** | Validate agent registry consistency, role definitions | claude |
| **Validator (Runner Action)** | Deterministic structural validation of all generated artifacts | deterministic Python |

## Codebase Documentation Scope

### Current State

The repository has a comprehensive codebase documentation tree under `docs/codebase/`:

| Directory | Content | File Count |
|-----------|---------|-----------|
| `00_standards/` | SOP and status rules | 2 (CODEBASE_DOC_SOP_v1.md, CODEBASE_DOC_STATUS_RULES_v1.md) |
| `01_inventory/` | Full module inventory | 1 (codebase_inventory.md, 74+ entries) |
| `02_modules/` | Per-module documentation | 49 module docs |
| `03_components/` | Component-level docs | 5 component docs (actions, codebase-governance, config-and-data, scripts, tests, workflow-families) |
| `04_changes/` | Change-impact records | 10+ change records with snapshot JSON |
| `05_archives/` | Archived docs | 0 (empty) |

### Coverage Assessment

| Category | Coverage | Notes |
|----------|----------|-------|
| **Python modules** | Full | All 49 modules documented with stub/summary/full modes |
| **Bootstrap workflows** | Full | All 80+ workflow files covered under workflow-families component |
| **Configuration files** | Full | 12 config/data files documented |
| **Scripts** | Full | 43 scripts (.bat, .sh) documented |
| **Test files** | Full | 11 test files documented |
| **Documentation files** | Full | 74 doc files tracked in inventory |

### Documentation Gaps

1. **Existing codebase docs are comprehensive** — `00_standards/` now has both SOP and status rules (generated by a prior scaffold run).
2. **Delivery governance exists** — `docs/delivery/` has been scaffolded with standards, templates, reviews, and folder map.
3. **Template completeness** — All 7 delivery templates and 5 codebase templates exist under `docs/system/00_governance/bootstrap/templates/`.

## Documentation Freshness Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Code changes outpace doc updates** | High | 49 Python modules across 9+ workflow families — frequent change surface. Enforcement via `31_task_execution_v1` doc-update obligations. |
| **Bootstrap template drift** | Medium | Runtime bundles at `%USERPROFILE%\.ukbe-runner\workflows\...` can diverge from repo bootstrap source. Mitigated by `sync-workflows-to-backend.bat`. |
| **Cross-reference breakage** | Medium | 7 delivery templates + 5 codebase templates with inter-references — template changes can break links. Mitigated by deterministic `validate_delivery_docs` action. |
| **Agent contract staleness** | Medium | Agent roles and contracts must match actual runner behavior and step configurations. Mitigated by scaffold re-run on governance changes. |
| **Workflow family additions** | Medium | New workflow families beyond the current 9+ require prompt template and validation updates. |
| **Platform-specific doc accuracy** | Low | Windows compatibility docs must stay in sync with daemon changes. |
| **Inventory drift** | Medium | Codebase inventory was generated by a bootstrap scan; new files added after bootstrap won't appear until next rescan. |
| **Dual project analysis files** | Low | Two project_analysis.md files exist at different paths (docs/delivery/ and docs/system/00_governance/bootstrap/). Source of truth should be `docs/delivery/project_analysis.md`. |

## Stale-Document Cleanup Expectations

Per the `CODEBASE_DOC_STATUS_RULES_v1.md` and `WORKFLOW_SOP_v1.md`:

- **30-day freshness threshold**: Documentation stale beyond 30 days is flagged. Critical misdirection triggers emergency correction.
- **Supersession over deletion**: No delivery artifact is ever deleted. Replaced artifacts are marked `superseded` with a pointer to the replacement.
- **Drift reconciliation**: The `40_documentation_sync_v1` workflow is the single current-truth synchronization workflow. It reconciles actual codebase state against all active documentation.
- **Change-impact records**: Significant changes produce change-impact records in `docs/codebase/04_changes/` with snapshot JSON for rollback comparison.

## Project-Specific SOP Considerations

1. **Bootstrap-first governance**: This repo is both the runner package AND a consumer of its own scaffolding. The SOP must account for self-hosting — the delivery scaffold generates governance docs into the same repo that powers the scaffold workflow. This creates a circular dependency that must be managed carefully.

2. **Dual source of truth**: Runtime workflow bundles (`%USERPROFILE%\.ukbe-runner\workflows\...`) are the active source; repo bootstrap (`agent_runner_v2/bootstrap/...`) is the seed. Changes flow from repo bootstrap to runtime bundle via `sync-workflows-to-backend.bat` or manual install. The reverse direction is not supported — runtime changes are ephemeral.

3. **Cross-project scaffolding**: The `--target-project-root` flag enables scaffolding into other repos. Codebase docs in the target repo are owned by the target repo's governance, not by this runner's governance.

4. **ComfyUI integration**: Three workflow families (`image_csv_gen_v1/v2`, `tiktok_video_pipeline_v1`, `videoxpress_gen_v1`) interact with ComfyUI. These are content-generation workflows, distinct from the software-delivery workflows. They share the same governance umbrella but may have different acceptance criteria.

5. **Daemon on Windows**: The daemon supervisor has Windows-specific signal handling, process termination via `TerminateProcess()`, and WSL support. Changes to `daemon.py` require documentation updates in both the module doc and `WINDOWS_COMPATIBILITY.md`.

6. **Template groups as code**: Workflow definitions are Python dictionaries in `template_groups.py`, not external configuration. This provides type safety and IDE support at the cost of requiring code changes for workflow modifications.

## Operational Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| **Backend API breaking change** | Worker poll/submit fails | Low | Backend is internal; version compatibility should be maintained |
| **LLM API timeout** | Coder step hangs | Medium | Configurable timeout via `AGENT_RUNNER_CODER_TIMEOUT_SECONDS` |
| **Job state corruption** | Workflow stuck mid-execution | Low | `job.json` has schema versioning (v6) with `migrate_job_state()` |
| **Bootstrap-repo drift** | Runtime uses stale prompts | Medium | `sync-workflows-to-backend.bat` and manual seed process |
| **Windows process orphaning** | Daemon child processes leak | Low | Both `terminate()` and `kill()` use `TerminateProcess()` |
| **Token cost overruns** | Expensive multi-step workflows | Medium | Review loops bounded (refine: 2, replan: 1) |
| **Schema migration gaps** | Old job.json schemas incompatible | Medium | `migrate_job_state()` exists but no migration history documentation |
| **Large template_groups.py** | ~3,000 lines approaching maintainability limit | Medium | Consider splitting by workflow family in future refactor |

## Architectural Observations

### Strengths
- **Deterministic sidecar protocol**: `meta.json` as the only structured result channel eliminates ambiguity between coder output and runner validation.
- **Explicit review loops**: Refine (max 2) and replan (max 1) loops have bounded iteration counts, preventing infinite retry cycles.
- **Zero runtime dependencies**: Minimal attack surface, easy to deploy, no supply-chain concerns.
- **Cross-project root support**: Enables the runner to scaffold governance into any target repo without modifying the runner's own tree.
- **Runner actions vs coder steps**: Deterministic validation steps (e.g., `validate_delivery_docs`) avoid LLM costs for structural checks.
- **Clear separation of concerns**: Coder adapters, step runner, workflow router, job state — each with distinct responsibility.
- **Planning attempt budgets**: `max_planning_attempts` prevents infinite refinement loops.

### Areas for Improvement
- **Template proliferation**: 9+ workflow families with 100+ prompt templates creates significant maintenance burden. Consider template composition or inheritance.
- **Bootstrap seeding is manual**: There is no automated process to sync repo bootstrap changes into the runtime bundle. A `sync` command or install-hook would reduce drift risk.
- **Large monolithic modules**: `template_groups.py` (~3,000 lines) and `run_agent.py` (~2,141 lines) approach size limits; consider splitting by workflow family.
- **Manual path normalization**: Some paths use manual string replacement instead of pathlib — potential cross-platform fragility.
- **Codebase doc ownership is implicit**: Module docs point to owner docs, but there is no enforcement mechanism when source files change.

## Architecture Posture

| Dimension | Rating | Notes |
|-----------|--------|-------|
| **Modularity** | High | Clear separation: actions, commands, coder, bootstrap, state, core |
| **Testability** | Medium | 11 test files covering key paths; some actions lack dedicated tests |
| **Extensibility** | High | New workflow families can be added by creating prompt templates and updating `template_groups.py` |
| **Portability** | High | Zero runtime deps, Python 3.11+, Windows and Unix support |
| **Observability** | Medium | Local daemon/child logs and backend run events; no distributed tracing |
| **Security** | High | No external runtime dependencies, local execution model, API keys via environment |
| **Maintainability** | Medium-High | Clear module boundaries but large monolithic files in hot paths |

**Overall posture: Solid foundation with room for operational improvements.** The architecture supports the intended use case well. The main risks are operational (token cost, bootstrap drift) rather than architectural.

## Discovered Files

### AI Coder Context

| File | Exists | Size | Notes |
|------|--------|------|-------|
| `QWEN.md` | Yes | 5,106 bytes | Primary AI coder context — project overview, core modules, workflow families, artifact coverage |
| `AGENTS.md` | No | — | Not present at project root |
| `CLAUDE.md` | No | — | Not present at project root (exists in user-level config only) |
| `.cursorrules` | No | — | Not present |
| `.github/copilot-instructions.md` | No | — | Not present |
| `.windsurfrules` | No | — | Not present |

### Project Metadata

| File | Exists | Size | Notes |
|------|--------|------|-------|
| `README.md` | Yes | 3,839 bytes | Project description, CLI modes, install instructions, documentation links |
| `pyproject.toml` | Yes | 929 bytes | Package config: setuptools, Python 3.11+, zero runtime deps, `ukbe-run-agent` entry point |
| `package.json` | No | — | N/A (Python project) |
| `Cargo.toml` | No | — | N/A (Python project) |
| `go.mod` | No | — | N/A (Python project) |
| `Gemfile` | No | — | N/A (Python project) |

### Additional Project Docs

| File | Exists | Size | Notes |
|------|--------|------|-------|
| `HOW_TO_GUIDE.md` | Yes | ~12,798 bytes | Delivery scaffold workflow guide — full lifecycle, troubleshooting, validation |

### Architecture / Design Docs

| Path | Exists | Notes |
|------|--------|-------|
| `docs/architecture/*.md` | No | No dedicated architecture docs at this path |
| `docs/specs/*.md` | No | No spec documents at this path |
| `docs/design/*.md` | No | No design documents at this path |
| `ARCHITECTURE.md` | No | Not present |
| `DESIGN.md` | No | Not present |
| `docs/system/00_governance/bootstrap/` | Yes | 20+ governance docs generated by `00_master_docs_bootstrap_v1` |

### Existing Delivery Docs

| Path | Exists | Notes |
|------|--------|-------|
| `docs/delivery/project_analysis.md` | Yes | Prior scaffold output |
| `docs/delivery/DELIVERY_FOLDER_MAP.json` | Yes | Validation output (388/392 checks passed) |
| `docs/delivery/00_standards/` | Yes | 7 agent contract documents |
| `docs/delivery/01_initiatives/` | Yes | Empty directory |
| `docs/delivery/02_plans/` | Yes | Empty directory |
| `docs/delivery/03_tasks/` | Yes | Empty directory |
| `docs/delivery/04_implementation_plans/` | Yes | Empty directory |
| `docs/delivery/05_reviews/` | Yes | 12 review records with meta.json sidecars |
| `docs/delivery/06_memory/` | Yes | Empty directory |

### Existing Codebase Docs

| Path | Exists | Notes |
|------|--------|-------|
| `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` | Yes | Full SOP |
| `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` | Yes | Full status rules |
| `docs/codebase/01_inventory/codebase_inventory.md` | Yes | Full inventory: 74+ entries |
| `docs/codebase/02_modules/*.md` | Yes | 49 module documentation files |
| `docs/codebase/03_components/*.md` | Yes | 5 component documentation files |
| `docs/codebase/04_changes/*.md` | Yes | 10+ change records with snapshot JSON |
| `docs/codebase/05_archives/` | Yes | Empty directory |

### System Bootstrap Docs

| Path | Exists | Notes |
|------|--------|-------|
| `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` | Yes | Full delivery workflow SOP |
| `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` | Yes | Full delivery status rules |
| `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` | Yes | Existing repo workflow SOP |
| `docs/system/00_governance/bootstrap/templates/delivery/` | Yes | 9 delivery templates |
| `docs/system/00_governance/bootstrap/templates/codebase/` | Yes | 5 codebase templates |
| `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md` | Yes | Bundle taxonomy reference |
| `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md` | Yes | Component architecture reference |
| `docs/system/00_governance/bootstrap/DECISION_LOG.md` | Yes | Architecture decision records |
| `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md` | Yes | Developer onboarding guide |
| `docs/system/00_governance/bootstrap/RUNBOOK.md` | Yes | Operational procedures |
| `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md` | Yes | System overview |

### Summary

- **Context files discovered**: 3 core (QWEN.md, README.md, pyproject.toml) + 1 guide (HOW_TO_GUIDE.md)
- **No standalone architecture/design docs**: The project relies on inline QWEN.md, README.md, and `docs/system/00_governance/bootstrap/` for architectural guidance
- **Existing codebase docs**: Comprehensive (49 module + 5 component docs) — generated by `00_master_docs_bootstrap_v1`
- **Existing delivery docs**: Scaffolded but sparse — standards and reviews exist, initiatives/plans/tasks are empty
- **Status**: **APPROVED** — sufficient context files exist to proceed with scaffold

## Universal Baseline vs Repo-Selected Profile

| Dimension | Universal Baseline | This Repo | Rationale |
|-----------|-------------------|-----------|-----------|
| **Delivery governance** | Full `docs/delivery/` tree | **Selected: Merge + extend** | Partial scaffold exists; fill gaps and refresh |
| **Codebase governance** | Full `docs/codebase/` tree | **Selected: Merge + extend** | Existing modules and components are comprehensive; standards already generated |
| **Agent contracts** | All 6 agent roles | **Selected: Refresh** | 7 agent docs exist under `00_standards/`; refresh for consistency |
| **Template families** | Delivery + codebase templates | **Selected: Verify** | 9 delivery + 5 codebase templates exist; verify completeness |
| **System docs** | Governance bootstrap docs | **Selected: Preserve** | 20+ bootstrap docs exist; preserve and reference |
| **Architecture profile** | `none` (default) | **Selected: none** | No DDD, EDA, layered, or clean architecture conventions adopted |
| **Migration mode** | `none` (default) | **Selected: none** | Repo already bootstrapped; no active migration in progress |

## Current Profile, Target Profile, and Migration Mode

| Profile | Current | Target |
|---------|---------|--------|
| **Delivery governance** | Partially scaffolded (standards, reviews exist; empty initiatives/plans/tasks) | Refreshed scaffold — validate existing, fill gaps |
| **Codebase standards** | Full (SOP + status rules exist) | No change — verify completeness |
| **Agent contracts** | 7 agent docs under `00_standards/` | Refresh for consistency with latest SOP |
| **Templates** | 9 delivery + 5 codebase templates | Verify completeness, no changes needed |
| **System docs** | 20+ bootstrap docs | Preserve, no changes |
| **Architecture profile** | `none` | `none` |
| **Migration mode** | `none` | `none` |

**Migration mode: None.** This repo is already fully bootstrapped. The scaffold run serves as a refresh/validation pass, not an initial onboarding. Existing comprehensive codebase docs and delivery governance should be preserved and validated, not regenerated from scratch.
