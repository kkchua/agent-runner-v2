---
template_id: "SYS-00-PA"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "02_generate_project_analysis"
managed_by: workflow-generated
generated: "2026-07-10T11:42:09+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE. It runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions.

The package provides a CLI entry point (`ukbe-run-agent`) supporting three primary usage modes:
- **Manual workflow execution** with `ukbe-run-agent run`
- **Backend-connected execution** with `ukbe-run-agent worker`, `poll`, and `execute-step`
- **Workstation supervision** with `ukbe-run-agent daemon`

The runner is responsible for prompt rendering, coder/action execution, output validation, and step result submission. The backend (when connected) is the source of truth for runs, step runs, artifacts, events, and approvals.

## Codebase Structure

### Package Layout

```
agent_runner_v2/              # Main Python package (47+ modules)
├── __init__.py               # Package entry
├── run_agent.py              # CLI entry point (2,338 lines)
├── step_runner.py            # Core step execution (2,582 lines)
├── workflow_router.py        # Post-step routing (787 lines)
├── job_state.py              # Job lifecycle management
├── coder_adapters.py         # Claude/Codex/Qwen invocation
├── runtime_context.py        # Active workflow/runtime path context
├── bundle_loader.py          # Bootstrap seeding and workflow loading
├── constants.py              # Centralized artifact path constants
├── daemon.py                 # Workstation supervisor
├── actions/                  # 26 deterministic runner actions
│   ├── init.py
│   ├── prepare_delivery_scaffold.py
│   ├── scan_repo_codebase.py
│   ├── validate_*.py         # Multiple validation actions
│   └── ...
├── bootstrap/                # Packaged workflow definitions
│   └── workflows/default/
│       ├── template_groups.py
│       ├── prompts/
│       │   ├── 00_master_docs_bootstrap_v1/
│       │   ├── 10_execution_scaffold_v1/
│       │   ├── 20_initiative_intake_v1/
│       │   ├── 21_bug_fix_intake_v1/
│       │   ├── 30_delivery_planning_v1/
│       │   ├── 31_task_execution_v1/
│       │   ├── 40_documentation_sync_v1/
│       │   └── 41_audience_doc_v1/
│       └── *.json schemas
└── tools/
    └── agent_tools.py        # Workflow utility tools
```

### Documentation Structure

```
docs/
├── delivery/                 # Delivery governance
│   ├── 01_initiatives/
│   ├── 02_plans/
│   ├── 03_tasks/
│   └── 04_validation/
├── codebase/                 # Codebase documentation
│   ├── 01_inventory/
│   ├── 02_modules/          # 67 module docs
│   ├── 03_components/
│   └── 04_changes/
└── system/                   # System governance
    └── 00_governance/bootstrap/
```

### Test Structure

```
tests/
├── unit/                     # 45 pure unit tests
├── integration/              # Integration tests with real files
└── conftest.py
```

### Entry Points

- **CLI**: `ukbe-run-agent` (defined in `pyproject.toml`)
- **Batch launchers**: `run-*.bat` files for each workflow family

## Workflow and Runtime Model

### Core Execution Model

Each workflow step follows a strict v2 contract:

1. **Load** the active workflow bundle from `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
2. **Render** a prompt from the bundle prompt template with artifact substitution
3. **Invoke** a coder (Claude/Codex/Qwen) or runner action
4. **Read** a `meta.json` sidecar written by the step (only structured result channel)
5. **Validate** artifacts and route to the next step via `workflow_router.py`

### Key v2 Contract Rules

- `meta.json` sidecar is the **only** structured result channel
- No markdown write-backs by the runner
- No silent recovery paths
- Hard failures route explicitly through `route_after_failure()`
- Prompt templates use `REFERENCE_FILES` dict keys as placeholders

### Runtime Source of Truth

Two distinct sources exist:

1. **Packaged bootstrap source** in this repo (`agent_runner_v2/bootstrap/workflows/default/`)
2. **Runtime workflow bundle** used during execution (`%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`)

Runtime prompts/templates are loaded from the global runner home, not from the repo tree directly. The repo bootstrap files only seed those runtime bundles during `ukbe-run-agent init`.

### Workflow Families

| Workflow | Purpose |
|----------|---------|
| `00_master_docs_bootstrap_v1` | Master documentation generation for new repositories |
| `10_execution_scaffold_v1` | Scaffolds delivery/codebase governance |
| `20_initiative_intake_v1` | Initiative intake and pre-init refinement |
| `21_bug_fix_intake_v1` | Bug triage, reproduction, and patching |
| `30_delivery_planning_v1` | Plan generation, task-graph generation, task contracts |
| `31_task_execution_v1` | Implementation, review, execution, validation |
| `40_documentation_sync_v1` | Documentation reconciliation and validation |
| `41_audience_doc_v1` / `50_architecture_site_v1` | Multi-audience documentation and HTML site generation |

### Coder/Action Split

- **Coder actions**: Invoke LLMs (Claude, Codex, Qwen) with rendered prompts
- **Runner actions**: Deterministic Python functions in `actions/` directory

## Operational Risks

### Risk 1: Runtime Bundle Drift

**Description**: Bootstrap files in the repo may diverge from the runtime bundles in `%USERPROFILE%\.ukbe-runner\workflows\`.

**Impact**: Changes to bootstrap templates may not take effect until `ukbe-run-agent init` reseeds the runtime bundles.

**Mitigation**: The `init` command must be run after bootstrap changes; workflow sync batch files exist for this purpose.

### Risk 2: Windows Path Handling

**Description**: Pathlib `relative_to()` failures on Windows with mixed path separators.

**Impact**: Artifact path resolution may fail on Windows workstations.

**Mitigation**: Fixed via centralized path constants using `PurePosixPath` in `constants.py`.

### Risk 3: Job State Migration

**Description**: `job.json` schema evolution requires backward compatibility handling.

**Impact**: Old job files may fail to load after schema changes.

**Mitigation**: `ensure_backward_compatible_state()` and `migrate_job_state()` functions in `job_state.py`.

### Risk 4: Notification Context Completeness

**Description**: Step-level notifications require specific state fields (`workflow_name`, `template_group`, timestamps).

**Impact**: Notifications may show incomplete information if state is not properly populated.

**Mitigation**: State normalization in `step_runner.py` before notification dispatch.

### Risk 5: Test Execution Environment

**Description**: pytest's `tmp_path` fixture creates directories that may have permission issues on Windows.

**Impact**: Integration tests using filesystem operations may fail on Windows.

**Mitigation**: Unit tests are pure logic without filesystem dependencies; integration tests are isolated.

## Architectural Observations

### Observation 1: Centralized Constants Pattern

The codebase uses a layered constant system in `constants.py`:
- `ARTIFACT_KEY_*` constants for artifact identification
- `ARTIFACT_PATH_*` constants for path templates
- `FOLDER_KEY_*` constants for directory locations
- `REFERENCE_FILES` dict for prompt placeholder substitution

This eliminates hardcoded paths and provides a single source of truth.

### Observation 2: Sidecar-Only Result Channel

The v2 architecture strictly separates concerns:
- LLM writes markdown artifacts to disk
- LLM writes structured results to `meta.json` sidecar
- Runner reads `meta.json` for routing decisions
- Runner does NOT parse markdown or stdout

This eliminates fragile parsing and provides a clean contract boundary.

### Observation 3: Workflow Router Decoupling

The `workflow_router.py` module replaces monolithic state management from v1:
- No `extract_blocking_issues()` — coder owns content analysis
- No `review_converges()` check — coder decides adequacy
- Explicit routing functions: `route_after_step()`, `route_after_failure()`

### Observation 4: Daemon Subprocess Architecture

The daemon spawns fresh subprocesses for each step via `subprocess.Popen()`. This means:
- Code changes are picked up automatically without daemon restart
- Each step runs in isolation with fresh Python interpreter
- No shared memory between steps

### Observation 5: Documentation Governance Integration

The runner has deep integration with documentation governance:
- Automatic document protection via `produces` lists
- Validation of document sections against `section_requirements.py`
- Codebase inventory scanning and synchronization
- Architecture site generation with multi-audience views

## Architecture Posture

| Attribute | Value |
|-----------|-------|
| **current_profile** | `provisional` |
| **target_profile** | `structured_delivery` |
| **migration_mode** | `incremental` |
| **repo_state** | `explicit` |

### Evidence Sources

1. **Codebase Inventory**: 67 module documentation files exist in `docs/codebase/02_modules/`
2. **Template Groups**: 8+ workflow families defined in `template_groups.py`
3. **Test Structure**: Split `tests/unit/` and `tests/integration/` directories
4. **Documentation Governance**: Active `docs/delivery/` and `docs/codebase/` directories
5. **Bootstrap Bundle**: `agent_runner_v2/bootstrap/workflows/default/` contains full workflow definitions
6. **Change Impact Documents**: Latest change at `docs/codebase/04_changes/00DOC-20260710-15f76235-bootstrap.md`

### Posture Rationale

The repository is **explicit** (not empty) because it contains:
- 67+ module documentation files
- Structured workflow definitions
- Comprehensive test suite
- Active documentation governance

The posture is **provisional** because:
- Documentation is still being actively reconciled
- Master system docs are currently being generated
- Bundle taxonomy is evolving

The target profile is **structured_delivery** based on:
- Workflow-driven delivery lifecycle
- Multi-audience documentation generation
- Structured artifact contracts

## Unresolved Documentation Gaps

### Gap 1: System Context Documentation

**Description**: High-level system context diagram showing agent-runner-v2 in relation to external systems (backend, LLM providers, user workstations).

**Required By**: Downstream master system docs generation

### Gap 2: Component Architecture

**Description**: Detailed component interaction diagram showing how `run_agent.py`, `step_runner.py`, `workflow_router.py`, and `coder_adapters.py` interact.

**Required By**: Architecture site generation for developer audience

### Gap 3: Decision Log

**Description**: Documented architectural decisions including the v2 sidecar-only contract, daemon subprocess architecture, and centralized constants pattern.

**Required By**: Future developers understanding design rationale

### Gap 4: Integration Map

**Description**: Comprehensive mapping of integration points with the backend API, including endpoint contracts and error handling strategies.

**Required By**: Backend-connected execution modes

### Gap 5: Failure Modes Reference

**Description**: Catalog of failure modes and recovery strategies for each workflow step type.

**Required By**: Operational runbook and troubleshooting guides

### Gap 6: Bundle Migration History

**Description**: Historical record of bundle taxonomy changes and migration strategies.

**Required By**: Long-term maintenance of workflow bundles
