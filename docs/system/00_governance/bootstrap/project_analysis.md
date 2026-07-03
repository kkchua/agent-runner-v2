---
template_id: "SYS-00-PA"
title: "Project Analysis - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "02_generate_project_analysis"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE. It runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions. The package provides a CLI entry point `ukbe-run-agent` for workflow execution.

The engine supports three primary usage modes:
- **Manual workflow execution** with `ukbe-run-agent run` for local development
- **Backend-connected execution** with `ukbe-run-agent worker`, `poll`, and `execute-step` for distributed operation
- **Workstation supervision** with `ukbe-run-agent daemon` for persistent worker processes

Key capabilities include:
- Multi-step workflow execution with explicit step routing
- Review/refine/replan loops for iterative document improvement
- Deterministic runner actions for non-LLM operations (file operations, validation)
- Sidecar-based result contracts (meta.json) with no markdown write-backs
- Backend integration for remote job queuing and execution

## Codebase Structure

The repository is organized as a standard Python package with the following structure:

### Core Package (`agent_runner_v2/`)

| Module | Responsibility |
|--------|----------------|
| `run_agent.py` | CLI entry point and top-level orchestration (2,141 lines) |
| `step_runner.py` | Prompt rendering, sidecar validation, artifact checks (2,006 lines) |
| `workflow_router.py` | Post-step routing for approve/reject/failure cases (774 lines) |
| `job_state.py` | `job.json` lifecycle management (1,781 lines) |
| `coder_adapters.py` | Claude/Codex/Qwen invocation and polling |
| `bundle_loader.py` | Bootstrap seeding and workflow bundle loading |
| `runtime_context.py` | Active workflow/runtime path context |
| `template_groups.py` | Package-local workflow definition mirror (2,979 lines) |
| `actions/` | 18 deterministic runner actions (validation, sync, execution) |

### Bootstrap Workflow Bundles (`agent_runner_v2/bootstrap/workflows/default/`)

- `template_groups.py` - Workflow step definitions and artifact keys
- `prompts/` - 100+ prompt templates across 10 workflow families
- `*.json` - Schema definitions (job_schema, llm_response_schema, model_mapping, usage_schema)

### Documentation (`docs/`)

- `docs/codebase/` - Codebase governance (standards, inventory, modules, components, changes)
- `docs/delivery/` - Delivery artifacts (initiatives, plans, tasks)
- `docs/system/` - System documentation (governance, architecture, runbooks)
- `docs/operations/` - Operational guides (daemon mode, worker SOPs)

### Launcher Scripts

- `run-*.bat` - Local workflow execution wrappers
- `submit-*.bat` - Backend submission wrappers
- `scripts/` - Shell script utilities for Unix environments

### Configuration

- `pyproject.toml` - Package metadata, entry points (`ukbe-run-agent`), dependencies
- `.env.example` - Environment variable templates

## Workflow and Runtime Model

### Execution Model

Each workflow step follows a strict execution pattern:

1. **Load workflow bundle** - Runtime templates loaded from `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
2. **Render prompt** - Template rendering with job state context
3. **Invoke coder or action** - LLM coder (Claude/Codex/Qwen) or deterministic action
4. **Read meta.json sidecar** - The ONLY structured result channel (v2 contract)
5. **Validate artifacts** - Check file existence and template conformance
6. **Route to next step** - approve/reject/failure routing via workflow_router

### Key v2 Architectural Principles

- **meta.json is the only result channel** - No markdown write-backs, no stdout JSON parsing
- **No pre-invocation sidecar writes** - Clean separation of concerns
- **Hard failures route explicitly** - No silent recovery paths
- **Coder owns content analysis** - Runner does not extract blocking issues
- **Trust coder's REJECTED** - No duplicate review file checks

### Runtime Source of Truth

There are two distinct sources:

1. **Packaged bootstrap source** in this repo (`agent_runner_v2/bootstrap/workflows/default/`)
2. **Runtime workflow bundle** used during execution (`%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`)

Runtime prompts/templates are loaded from the global runner home, not from the repo tree directly.

### Workflow Families

| Workflow | Purpose | Steps |
|----------|---------|-------|
| `00_master_docs_bootstrap_v1` | Master documentation bootstrap | 10 |
| `10_execution_scaffold_v1` | Delivery scaffold generation | 13 |
| `20_initiative_intake_v1` | Initiative intake and refinement | 5 |
| `21_bug_fix_intake_v1` | Bug triage and fix workflow | 7 |
| `30_delivery_planning_v1` | Plan and task graph generation | 10 |
| `31_task_execution_v1` | Task implementation execution | 12 |
| `40_documentation_sync_v1` | Documentation synchronization | 4 |

## Operational Risks

### 1. Runtime Bundle Synchronization Risk
**Risk**: Runtime workflow bundles in `%USERPROFILE%\.ukbe-runner\` may diverge from packaged bootstrap source.
**Impact**: Behavior differences between environments; debugging confusion.
**Mitigation**: `ukbe-run-agent init` reseeds bundles; version pinning in config.json.

### 2. Schema Version Migration Risk
**Risk**: Job state schema is at version 6 (v2 runner); legacy jobs may need migration.
**Impact**: State loading failures for old jobs.
**Mitigation**: `migrate_job_state()` in job_state.py handles forward migration.

### 3. Coder Timeout Risk
**Risk**: Long-running coder steps (900-1200s timeouts) may hit limits.
**Impact**: Step failures, retry storms.
**Mitigation**: Configurable `coder_timeout_seconds` per step; auto-retry classification.

### 4. Artifact Path Resolution Risk
**Risk**: Complex path resolution logic (repo vs runtime) may produce incorrect paths.
**Impact**: Artifact validation failures, meta.json not found.
**Mitigation**: Extensive path helpers in runtime_context.py; validation at multiple layers.

### 5. Backend Integration Risk
**Risk**: Backend-connected modes (worker, daemon) depend on external API availability.
**Impact**: Work stalls, heartbeat failures.
**Mitigation**: Retry logic with backoff; graceful degradation to local mode.

### 6. Windows-Specific Path Risk
**Risk**: Path handling has Windows-specific branches (e.g., `str(path).replace("\\", "/")`).
**Impact**: Cross-platform inconsistencies.
**Mitigation**: Uses pathlib extensively; manual normalization in hot paths.

## Architectural Observations

### 1. Strict Sidecar Contract
The v2 runner enforces a strict meta.json contract with no fallbacks. This is a deliberate simplification from v1 that removes ambiguity but requires all coders to conform to the exact schema.

### 2. Separation of Concerns
- **Coder adapters** (`coder_adapters.py`) handle LLM provider specifics
- **Step runner** (`step_runner.py`) handles execution contract
- **Workflow router** (`workflow_router.py`) handles routing logic
- **Job state** (`job_state.py`) handles persistence

### 3. Loop and Replan Contexts
Sophisticated state machines for review loops and replan cycles:
- `loop_context`: Tracks refine iterations for rejected reviews
- `replan_context`: Tracks replan attempts after loop exhaustion

### 4. Planning Attempt Budgets
Workflows can configure `max_planning_attempts` to prevent infinite refinement loops.

### 5. Action-Based Steps
18 deterministic actions in `actions/` package for operations that don't require LLM invocation (file operations, validation, syncing).

### 6. Template Groups as Code
Workflow definitions are Python dictionaries in `template_groups.py`, not external configuration. This provides type safety and IDE support at the cost of requiring code changes for workflow modifications.

## Architecture Posture

| Attribute | Value |
|-----------|-------|
| `current_profile` | `explicit` |
| `target_profile` | `explicit` |
| `migration_mode` | `none` |
| `repo_state` | `explicit` |

### Evidence Sources

- `pyproject.toml` declares explicit dependencies and entry points
- `template_groups.py` contains 2,979 lines of explicit workflow definitions
- 49 Python modules with clear responsibility separation
- 10 workflow families with explicit step sequences
- 100+ prompt templates with explicit versioning

### Architecture Standard Alignment

The repository follows an **explicit architecture standard** with:
- Clear module boundaries and responsibilities
- Explicit contract definitions (schemas, artifact keys)
- Type hints throughout (Python 3.11+)
- Dataclass-based result types
- Explicit error hierarchies (`exceptions.py`)

## Unresolved Documentation Gaps

The following gaps should be addressed in subsequent bootstrap steps:

1. **SYSTEM_OVERVIEW.md** - High-level system description and capabilities
2. **BUSINESS_CAPABILITIES.md** - Business capability mapping
3. **FUNCTIONAL_SPEC.md** - Detailed functional requirements
4. **NON_FUNCTIONAL_REQUIREMENTS.md** - Performance, reliability, security requirements
5. **SYSTEM_CONTEXT.md** - System boundary and external interfaces
6. **COMPONENT_ARCHITECTURE.md** - Detailed component diagrams and interactions
7. **DECISION_LOG.md** - Architecture decision records
8. **SYSTEM_FILE_STRUCTURE.md** - File organization conventions
9. **DEVELOPER_GUIDE.md** - Developer onboarding and contribution guide
10. **RUNBOOK.md** - Operational procedures and troubleshooting
11. **EXISTING_REPO_WORKFLOW_SOP.md** - SOP for existing repository workflows

### Technical Debt Observations

1. `template_groups.py` at 2,979 lines is approaching size limits; consider splitting by workflow family
2. `run_agent.py` at 2,141 lines mixes CLI parsing with orchestration logic
3. Some path normalization uses manual string replacement instead of pathlib
4. Windows-specific code paths may need testing on Unix environments

---

*Analysis generated: 2026-07-04*
*Change ID: 00DOC-GEN-20260704-001*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 02_generate_project_analysis*
