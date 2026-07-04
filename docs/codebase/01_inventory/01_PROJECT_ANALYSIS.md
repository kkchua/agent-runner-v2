---
title: Project Analysis — agent-runner-v2
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: project_analysis
created: 2026-07-04
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis — agent-runner-v2

## Domain

AI / LLM workflow orchestration and delivery-governance scaffolding. The project is a standalone Python runner that executes multi-step, multi-model LLM workflows (Claude, Codex, Qwen) with deterministic runner actions, sidecar-driven approval gates, review loops, and structured artifact routing.

The runner underpins a documentation governance framework: it drives bootstrap, delivery planning, task execution, documentation sync, and validation workflows against a `docs/codebase/` and `docs/system/` tree.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Packaging | setuptools, `pyproject.toml`, `MANIFEST.in`, `.egg-info` |
| Build | wheel + setuptools backend |
| Testing | pytest ≥ 8.2, pytest-cov ≥ 5.0 |
| Runtime | CLI entry point `ukbe-run-agent` (`agent_runner_v2.run_agent:main`) |
| External LLMs | Claude (Anthropic), Codex (OpenAI), Qwen (Alibaba), aliased models |
| Config | JSON (`config.json`, `meta.json` sidecars, `job.json`, `bundle_map.json`) |
| Templates | Jinja-style `.txt` and `.md` prompt templates under `bootstrap/workflows/default/prompts/` |
| CI / Runner | `.bat` / `.ps1` scripts (Windows-native); `run-daemon.bat` for background mode |
| Host OS | Windows (paths assume `%USERPROFILE%`); POSIX-compatible where noted |
| Dependencies | Zero required runtime deps; only dev extras (pytest) |

## Complexity

**Medium-high**. The runner is non-trivial:

- Multi-LLM adapter layer with polling and timeout handling.
- Two-level source-of-truth model (packaged bootstrap vs. runtime bundle in `%USERPROFILE%\.ukbe-runner\`).
- Strict `meta.json` sidecar contract (v2 schema) with artifact-path validation.
- Governance tree of 86+ codebase docs, 20 system docs, 53 module entries, 6 components, 6 changes.
- Multiple workflow families (`initiative_intake_v1`, `delivery_planning_v1`, `task_execution_v1`, `delivery_scaffold_v1`, `documentation_sync_v1`, `master_docs_bootstrap_v1`).
- Router-based step transitions (approve / reject / failure / retry).
- Architecture-site publishing pipeline (Pandoc + Mermaid).

The codebase is already mature and self-documenting; the complexity lies in the governance model, not in external integrations or scale.

## Recommended Workflow Scope

Full scaffold. The repo warrants the complete `10_execution_scaffold_v1` scope:

- Delivery SOP + status rules.
- Delivery template registry (init → plan → task graph → task → impl → review → validation → memory).
- Codebase doc SOP + status rules.
- Codebase template registry (inventory, module, component, change).
- Agent role contracts (planner, task-decomposer, impl-planner, executor, reviewer, memory-manager).
- Folder map.
- Existing-repo workflow SOP (migration mode — repo already has a governance corpus).

## Recommended Agent Roles

All six standard roles apply:

| Role | Rationale |
|---|---|
| Planner | Translates documentation/initiative scope into delivery plans. Needed because the repo manages a governed docs tree, not ad-hoc changes. |
| Task Decomposer | Breaks plans into task graphs with documentation obligations attached. Required given the 86-doc corpus. |
| Impl Planner | Per-task implementation plan with codebase-doc impact analysis. |
| Executor | Runs coder adapters, writes artifacts, updates codebase docs alongside code. |
| Reviewer | Enforces the strict sidecar contract, doc freshness, and status rules. |
| Memory Manager | Maintains workflow memory and decision history across long-running deliveries. |

## Codebase Documentation Scope

The codebase-docs tree is **already substantial** (86 files). Target state:

| Directory | Purpose | Current | Action |
|---|---|---|---|
| `docs/codebase/00_standards/` | SOPs, status rules | 0 files | Populate with workflow-generated SOPs |
| `docs/codebase/01_inventory/` | Codebase inventory + project analysis | 1 file (`codebase_inventory.md`) | Add `01_PROJECT_ANALYSIS.md`, refresh inventory |
| `docs/codebase/02_modules/` | Module reference | 53 files | Maintain; align with `bundle_map.json` |
| `docs/codebase/03_components/` | Component groupings | 6 files | Maintain |
| `docs/codebase/04_changes/` | Change-impact records | 6 files | Maintain |
| `docs/system/00_governance/bootstrap/` | Delivery governance SOPs, templates, agent contracts | 20 files | Populate remaining templates |

**File-type coverage required:**

- Python source modules (`agent_runner_v2/**/*.py`) → module docs.
- JSON configs and bundle manifests → referenced in module docs.
- Prompt templates (`bootstrap/workflows/default/prompts/*/*.txt`) → inventoried, not individually doc'd.
- Batch / PowerShell runner scripts → referenced from top-level README.
- Markdown context files (`QWEN.md`, `README.md`, `MANIFEST.in`) → inventoried.
- Architecture-site outputs (`docs/system/02_architecture_site/**`) → validated via site pipeline.

## Documentation Freshness Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Module doc drift from code changes | High | Medium | Enforce via `validate_codebase_docs` action; block delivery on stale docs |
| `bundle_map.json` divergence from actual module files | Medium | High | Sync action `scan_repo_codebase`; validate in CI |
| Workflow prompt templates changing without doc update | Medium | Medium | Treat prompts as protected artifacts; require scaffold re-run |
| `QWEN.md` becoming source-of-truth conflict with codebase docs | Low | Medium | `QWEN.md` is context-only; codebase docs are authoritative for reference |
| Architecture-site staleness (Pandoc/Mermaid pipeline drift) | Low | Low | Re-run `publish_architecture_site` action periodically |
| Sidecar schema evolution (v2 → v3) | Low | High | Bump `schema_version` explicitly; migrate existing sidecars |
| Cross-LLM adapter behaviour diverging | Medium | Medium | Per-adapter module docs; contract tests |

## Stale-Document Cleanup Expectations

- **On every delivery**: validate that touched modules have fresh `docs/codebase/02_modules/` entries.
- **On bundle-map change**: re-run `scan_repo_codebase` and reconcile inventory.
- **Quarterly**: audit `docs/codebase/04_changes/` for resolved changes that can be archived.
- **On workflow scaffold re-run**: regenerate protected SOPs; keep manual additions out of protected paths.

## Project-Specific SOP Considerations

- **Dual source of truth**: SOPs must clearly distinguish packaged bootstrap (`agent_runner_v2/bootstrap/workflows/default/`) from runtime bundle (`%USERPROFILE%\.ukbe-runner\workflows\...`).
- **Sidecar contract**: all delivery steps must emit a v2 `meta.json` sidecar; SOPs must enforce this as a hard gate.
- **Zero runtime deps**: adding dependencies requires explicit review — the runner is intentionally dep-free.
- **Windows-first**: paths and scripts assume Windows; SOPs should not assume POSIX tools unless wrapped.
- **Multi-LLM**: SOPs must account for model-specific behaviors (adapter differences, rate limits, error modes).
- **Existing corpus**: repo is not greenfield — scaffold must run in **migration mode**, reconciling existing docs rather than replacing them.

## Operational Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Runtime bundle drift from packaged bootstrap | High | `bundle_loader.py` seeds from bootstrap; never hand-edit runtime bundle |
| Job folder accumulation in `%USERPROFILE%\.ukbe-runner\jobs\` | Low | Periodic cleanup action available (`cleanup_generated_docs`) |
| Polling timeouts in coder adapters | Medium | Configurable via `config.json`; monitor `logs/` |
| Path-length issues on Windows for deep doc trees | Low | Keep doc paths under 180 chars |
| `meta.json` parse failures blocking pipeline | High | Strict schema validation in `step_runner.py`; clear error messages |
| Protected-doc accidental overwrite | Medium | Workflow protection banner + `managed_by` frontmatter |

## Architectural Observations

- **Clean separation of concerns**: adapters, step runner, router, job state, and actions are well-separated modules.
- **Action-based extensibility**: new runner capabilities are added as actions under `agent_runner_v2/actions/`, registered in `action_registry.py`.
- **Workflow-as-data**: workflows are defined in `template_groups.py` and rendered at runtime — not hardcoded in the runner.
- **Sidecar-driven contract**: the `meta.json` sidecar is the single source of truth for step results; this is the strongest architectural invariant.
- **Governance tree is a first-class artifact**: `docs/codebase/` and `docs/system/` are treated as protected, workflow-managed outputs, not afterthoughts.
- **Architecture site pipeline**: unusual for a Python project — the repo publishes its own architecture as a static site via Pandoc + Mermaid.
- **Daemon mode supported**: `run-daemon.bat` suggests long-running or scheduled execution is a supported use case.
- **Archive directory present**: `archive/batch/` indicates historical batches are retained, not deleted.

## Architecture Posture

- **Current profile**: delivery-governance + codebase-documentation scaffold with a mature, populated corpus.
- **Universal baseline**: applies — the repo has all the structural elements (workflows, actions, sidecars, docs tree) that the universal baseline expects.
- **Repo-selected profile**: the repo has evolved its own governance conventions (e.g., `managed_by` frontmatter, protected-doc banner, specific workflow families) that go beyond the baseline.
- **Target profile**: full alignment with `10_execution_scaffold_v1` protected-doc set, with migration-mode reconciliation of the existing 86-file corpus.
- **Migration mode**: **ACTIVE** — repo standard is mature but evolving. Scaffold must coexist with existing docs, not overwrite them. Use `EXISTING_REPO_WORKFLOW_SOP` for reconciliation rules.
- **When repo standard is unclear**: not applicable here — the repo standard is well-established. If it were unclear, fall back to universal baseline + incremental adoption.

## Discovered Files

| Category | Path | Role |
|---|---|---|
| AI coder context | `QWEN.md` | High-level project overview and delivery-workflow reference |
| AI coder context | `agent_runner_v2/QWEN.md` | Package-level developer guide, module map, workflow families |
| Project metadata | `README.md` | Project summary, installation, usage, architecture |
| Project metadata | `pyproject.toml` | Build config, deps, entry points |
| Project metadata | `MANIFEST.in` | Package data includes |
| Project metadata | `WINDOWS_COMPATIBILITY.md` | Windows-specific notes |
| Project metadata | `HOW_TO_GUIDE.md` | Usage guide |
| Existing codebase docs | `docs/codebase/**/*` | 86 files (inventory, 53 modules, 6 components, 6 changes) |
| Existing system docs | `docs/system/**/*` | 20 files (governance, architecture site) |
| Scripts | `scripts/README.md` | Helper-script documentation |
| Archive | `archive/batch/README.md` | Historical batch index |

**Total context files discovered**: 11 primary context files + 106 existing governance docs.
