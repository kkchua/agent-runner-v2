---
template_id: "SYS-00-PA"
title: "Project Analysis - agent-runner-v2"
status: "active"
generated: "2026-07-04T10:47:08+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "02_generate_project_analysis"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE. It runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions.

The package provides a CLI entry point (`ukbe-run-agent`) that supports three primary usage modes:

1. **Local workflow execution** - Manual runs with `ukbe-run-agent run`
2. **Backend-connected worker** - Single-step execution via `worker`, `poll`, and `execute-step` commands
3. **Workstation supervision** - Daemon mode with `ukbe-run-agent daemon`

The runner implements a strict v2 execution contract where `meta.json` sidecar is the only structured result channel, with no markdown write-backs by the runner and explicit failure routing.

## Codebase Structure

### Package Layout (`agent_runner_v2/`)

| Directory/File | Responsibility |
|----------------|----------------|
| `run_agent.py` | CLI entry point and top-level orchestration |
| `step_runner.py` | Prompt rendering, sidecar validation, artifact checks |
| `workflow_router.py` | Post-step routing for approve/reject/failure cases |
| `job_state.py` | `job.json` lifecycle management |
| `coder_adapters.py` | Claude/Codex/Qwen invocation and polling |
| `runtime_context.py` | Active workflow/runtime path context |
| `bundle_loader.py` | Bootstrap seeding and workflow bundle loading |
| `actions/` | 20 deterministic runner action modules |
| `bootstrap/workflows/default/` | Packaged bootstrap workflow definitions and prompts |
| `tools/agent_tools.py` | Progress tracking utilities |

### Documentation Structure (`docs/`)

| Directory | Purpose |
|-----------|---------|
| `docs/codebase/01_inventory/` | Codebase inventory (56 Python modules) |
| `docs/codebase/02_modules/` | Per-module documentation |
| `docs/codebase/03_components/` | Component-level documentation |
| `docs/codebase/04_changes/` | Change impact documents |
| `docs/system/00_governance/bootstrap/` | Generated system documentation |

### Workflow Bundles (`agent_runner_v2/bootstrap/workflows/default/`)

The repository packages 11 workflow families:

- `00_master_docs_bootstrap_v1` (10 steps) - Master documentation bootstrap
- `10_execution_scaffold_v1` (13 steps) - Delivery scaffold generation
- `20_initiative_intake_v1` (5 steps) - Initiative intake and refinement
- `21_bug_fix_intake_v1` (7 steps) - Bug fix workflow
- `30_delivery_planning_v1` (10 steps) - Plan and task graph generation
- `31_task_execution_v1` (12 steps) - Task implementation and validation
- `40_documentation_sync_v1` (2 steps) - Documentation reconciliation
- `50_architecture_site_v1` (2 steps) - Architecture site publishing
- `image_csv_gen_v2` (3 steps) - Image CSV generation
- `videoxpress_gen_v1` (9 steps) - Video generation pipeline
- `tiktok_video_pipeline_v1` (10 steps) - TikTok video workflow

### Entry Points

- `ukbe-run-agent` (console script via `pyproject.toml`)
- Batch launchers: `run-*.bat`, `submit-*.bat`, `sync-*.bat`

## Workflow and Runtime Model

### Core Execution Model

Each workflow step follows a strict sequence:

1. **Load** the active workflow bundle from global runner home
2. **Render** a prompt from the bundle prompt template
3. **Invoke** a coder (Claude/Codex/Qwen) or runner action
4. **Read** a `meta.json` sidecar written by the step
5. **Validate** artifacts and route to the next step

### v2 Contract Rules

- `meta.json` sidecar is the **only** communication channel
- No markdown write-backs by the runner
- No silent recovery paths
- Hard failures route explicitly through `route_after_failure()`
- Step results use schema version `"v2"` with `coder_result` object

### Runtime Source of Truth

Two distinct sources exist:

1. **Packaged bootstrap** (in repo): `agent_runner_v2/bootstrap/workflows/default/`
2. **Runtime bundle** (global): `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`

Runtime prompts/templates are loaded from the global runner home, not directly from the repo. The packaged bootstrap files only seed those runtime bundles during `ukbe-run-agent init`.

### Routing Model

The `workflow_router.py` implements sophisticated routing:

- **APPROVED** path: Advance step, clear retry counts, update artifacts
- **REJECTED** path: Check `on_reject_refine` config for review/refine loops
- **Failure** path: Classify exceptions into `AUTO_RETRYABLE`, `HUMAN_RETRY_REQUIRED`, or `FATAL`
- **Loop/Replen** cycles: Support iterative refinement with configurable max iterations

### Artifact Management

Common artifact keys span delivery, task execution, and codebase governance:

- `DRAFT_INIT_FILE`, `PRE_INIT_FILE`, `INIT_FILE` - Initiative artifacts
- `PLAN_FILE`, `TASK_GRAPH_FILE`, `TASK_FILE` - Planning artifacts  
- `IMPL_FILE`, `REVIEW_FILE`, `VALIDATION_FILE` - Execution artifacts
- `PROJECT_ANALYSIS`, `DELIVERY_SOP`, `CODEBASE_INVENTORY` - Scaffold artifacts

## Operational Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Bootstrap/Runtime Version Mismatch** | Runtime bundles in `~/.ukbe-runner` may diverge from packaged bootstrap | Version pinning, `init` re-run documentation |
| **Strict Sidecar Validation** | Any `meta.json` schema deviation causes hard failures | Clear schema documentation, validation error messages |
| **Multi-Coder Complexity** | Support for Claude, Codex, Qwen with different timeouts and capabilities | Model mapping configuration, timeout overrides |
| **External Workflow Dependency** | Runtime depends on global runner home state outside repo | Clear initialization SOP, bundle validation |
| **Job State Migration** | Legacy job.json formats require migration | `migrate_job_state()` function, backward compatibility |
| **Review Loop Exhaustion** | Iterative refinement loops may exhaust configured max iterations | Human intervention triggers, clear failure codes |

## Architectural Observations

### Separation of Concerns

The codebase demonstrates clean separation:

- **`run_agent.py`**: CLI parsing and orchestration only
- **`step_runner.py`**: Coder/action invocation and sidecar validation
- **`workflow_router.py`**: Pure routing logic, no I/O
- **`job_state.py`**: State mutations and persistence
- **`coder_adapters.py`**: Adapter pattern for multiple LLM providers

### Template Group Configuration

Workflows are data-driven via `template_groups.py`:

- Step definitions with `required_inputs`, `produces`, `result_meta_key`
- Coder configuration with `default` and `allowed` models
- Routing configuration via `on_reject_refine` and `on_exhaust_replan`
- Timeout overrides per step (`coder_timeout_seconds`)

### State Management

Job state is centralized in `job.json` with:

- `loop_context`: Active refine loops with iteration tracking
- `replan_context`: Replen cycles with attempt counting
- `review_state`: Artifact review decisions
- `retry_history`: Complete execution history
- `failed_steps`, `completed_steps`: Progress tracking

### Validation Strategy

Multi-layer validation ensures contract compliance:

1. **Sidecar schema validation** (`_read_and_validate_meta_json`)
2. **Artifact existence checks** (`_validate_artifact_files_exist`)
3. **Protected document guards** (`_assert_protected_docs_unchanged`)
4. **Template conformance** (`_validate_template_conformance`)

## Architecture Posture

| Attribute | Value |
|-----------|-------|
| `current_profile` | `provisional` |
| `target_profile` | `explicit` (standard architecture documentation) |
| `migration_mode` | `in-progress` |
| `repo_state` | `explicit` |

### Evidence Sources

- `codebase_inventory.md` (56 Python modules inventoried)
- `template_groups.py` (11 workflow families, 83+ steps)
- `00DOC-GEN-20260704-002-bootstrap.md` (change impact document)
- `QWEN.md` (project context and conventions)
- `pyproject.toml` (package configuration)

### Posture Assessment

The repository is **explicit** - it contains substantial implementation with:

- Complete workflow orchestration system
- Multi-coder LLM adapter layer
- Deterministic action framework
- Bootstrap/runtime bundle separation
- Comprehensive documentation structure

The current documentation standard is **provisional** - codebase documentation exists but system documentation is being generated through the bootstrap workflow. The target is **explicit** with full architecture documentation following delivery scaffold standards.

## Unresolved Documentation Gaps

The following gaps must be addressed by later bootstrap steps:

1. **System Overview Documentation**
   - `SYSTEM_OVERVIEW.md` - High-level system description
   - `BUSINESS_CAPABILITIES.md` - Capability mapping
   - `FUNCTIONAL_SPEC.md` - Functional requirements
   - `NON_FUNCTIONAL_REQUIREMENTS.md` - NFR documentation

2. **Architecture Documentation**
   - `SYSTEM_CONTEXT.md` - System context diagram
   - `COMPONENT_ARCHITECTURE.md` - Component relationships
   - `DECISION_LOG.md` - Architectural decisions
   - `SYSTEM_FILE_STRUCTURE.md` - File organization rationale

3. **Operational Documentation**
   - `DEVELOPER_GUIDE.md` - Development setup and workflows
   - `RUNBOOK.md` - Operational procedures
   - `EXISTING_REPO_WORKFLOW_SOP.md` - Workflow SOP for existing repos

4. **Governance Documentation**
   - `DOCUMENTATION_STANDARD.md` - Documentation standards
   - `BUNDLE_TAXONOMY.md` - Bundle taxonomy definition
   - `BUNDLE_MIGRATION_PLAN.md` - Migration strategy

5. **Validation**
   - Cross-document consistency review
   - Repository baseline alignment verification
   - Template conformance validation
