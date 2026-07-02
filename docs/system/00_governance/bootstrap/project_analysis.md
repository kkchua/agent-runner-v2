---
title: "Project Analysis: agent-runner-v2"
template_id: "SYS-00-PA"
status: "active"
managed_by: workflow-generated
generated: "2026-07-02T18:05:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "02_generate_project_analysis"
change_id: "00DOC-GEN-20260702-005"
---

# Project Analysis: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

## 1. Repository Overview

**agent-runner-v2** is a standalone Python LLM workflow orchestration engine extracted from UKBE. It provides structured multi-step workflow execution across multiple LLM backends (Claude, Codex, Qwen, and aliased models), with built-in review loops, retry logic, approval gates, and deterministic runner actions.

### 1.1 Primary Purpose

The system serves as a workflow runner that:
- Orchestrates complex multi-step delivery workflows (initiative intake, planning, task execution, documentation)
- Supports both local CLI execution and backend-connected worker modes
- Enforces strict v2 sidecar contracts (`meta.json`) for all step results
- Provides deterministic runner actions for repository operations

### 1.2 Distribution Model

- **Package Name:** `agent-runner-v2`
- **CLI Entry Point:** `ukbe-run-agent`
- **Install:** `pip install -e .`
- **Runtime Home:** `%USERPROFILE%\.ukbe-runner\`

## 2. Runtime Structure and Major Components

### 2.1 Three Primary Execution Modes

| Mode | Command | Purpose |
|------|---------|---------|
| **Local Execution** | `ukbe-run-agent run` | Manual workflow execution with job state tracking |
| **Backend Worker** | `ukbe-run-agent worker`, `poll`, `execute-step` | Backend-connected single-step execution |
| **Daemon Supervisor** | `ukbe-run-agent daemon` | Workstation supervisor for managed execution |

### 2.2 Core Runtime Components

```
agent_runner_v2/
├── run_agent.py          # CLI entry point and top-level orchestration
├── step_runner.py        # Prompt rendering, sidecar validation, artifact checks
├── workflow_router.py    # Post-step routing for approve/reject/failure cases
├── job_state.py          # job.json lifecycle management (schema v6)
├── coder_adapters.py     # Claude/Codex/Qwen invocation and polling
├── bundle_loader.py      # Bootstrap seeding and workflow bundle loading
├── runtime_context.py    # Active workflow/runtime path context
├── daemon.py             # Worker daemon supervisor
├── backend_client.py     # Backend API communication
└── actions/              # Deterministic runner actions
```

### 2.3 Key v2 Architectural Principles

1. **meta.json Sidecar is the ONLY Channel**: All structured results flow through `meta.json` sidecars written by steps
2. **No Markdown Write-Backs**: Runner never writes to markdown files (no sync_review_metadata, no stamp_created_metadata)
3. **No Silent Recovery**: Hard failures route explicitly through `route_after_failure()`
4. **Deterministic Actions**: All file/system operations go through action modules

### 2.4 Runtime Source of Truth

Two distinct sources:

1. **Packaged Bootstrap Source** (in repo):
   - `agent_runner_v2/bootstrap/workflows/default/`
   - Seeds global runner home on `init`

2. **Runtime Workflow Bundle** (global):
   - `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
   - Actually loaded at runtime

### 2.5 Workflow Families (10 Active)

| Family | Steps | Purpose |
|--------|-------|---------|
| `00_master_docs_bootstrap_v1` | 10 | Master documentation bootstrap |
| `10_execution_scaffold_v1` | 13 | Delivery scaffold generation |
| `20_initiative_intake_v1` | 5 | Initiative intake and pre-init refinement |
| `21_bug_fix_intake_v1` | 7 | Bug fix workflow |
| `30_delivery_planning_v1` | 10 | Plan generation, task graph, task contracts |
| `31_task_execution_v1` | 12 | Implementation planning, execution, validation |
| `40_documentation_sync_v1` | 4 | Documentation-only synchronization |
| `image_csv_gen_v2` | 3 | Image CSV generation pipeline |
| `videoxpress_gen_v1` | 9 | Video generation workflow |
| `tiktok_video_pipeline_v1` | 10 | TikTok video production pipeline |

## 3. Codebase Organization

### 3.1 Module Inventory (47 Python Modules)

**Core Modules (Full Documentation Mode):**
- `run_agent.py` (2,141 lines) - CLI entry point
- `step_runner.py` (2,000 lines) - Step execution contract
- `workflow_router.py` (774 lines) - Post-step routing
- `job_state.py` (1,781 lines) - Job lifecycle management
- `coder_adapters.py` (1,013 lines) - LLM invocation
- `daemon.py` (420 lines) - Worker daemon
- `bundle_loader.py` (~200 lines) - Bundle loading

**Action Modules (16 actions):**
- assemble_video, copy_artifact, execute_i2v, execute_t2i
- execute_voiceover, finalize_bootstrap, prepare_delivery_scaffold
- promote_artifact, promote_init, scan_repo_codebase
- submit_comfyui, sync_codebase_docs, sync_system_docs
- validate_codebase_docs, validate_delivery_docs, validate_system_docs

**Supporting Modules:**
- Schema: `action_result.py`, `artifact_paths.py`, `exceptions.py`
- State: `execution_request.py`, `execution_result.py`, `runtime_context.py`
- Commands: `approve_commands.py`, `engine_commands.py`, `submit_commands.py`, `submitter.py`
- Support: `backend_client.py`, `bundle_taxonomy.py`, `codebase_docs.py`, `documentation_guardrails.py`, `model_config.py`, `runner_actions.py`, `runner_logger.py`, `system_docs.py`, `workflow_spec_commands.py`, `workflow_specs.py`
- Tools: `agent_tools.py`

### 3.2 Configuration Files

- `pyproject.toml` - Package definition, CLI entry point `ukbe-run-agent`
- `job_schema.json` - Job state JSON schema
- `llm_response_schema.json` - LLM response schema
- `model_mapping.json` - Coder alias resolution
- `usage_schema.json` - Usage tracking schema

### 3.3 Bootstrap Workflow Assets

- `agent_runner_v2/bootstrap/workflows/default/template_groups.py` - Workflow definitions
- `agent_runner_v2/bootstrap/workflows/default/prompts/` - 100+ prompt templates
- JSON schemas for validation

### 3.4 Test Suite

- `tests/conftest.py`
- 8 test modules covering backend worker, bundle loading, codebase docs, daemon, run agent status, runtime context, tool instructions, wrapper

### 3.5 Scripts and Launchers

- Root-level `.bat` files for Windows execution
- `scripts/` directory with shell scripts for WSL/Unix
- `archive/batch/` for legacy batch scripts

## 4. Key Operational Risks

### 4.1 High-Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Meta.json Contract Violation** | Hard failures, step rejection | Strict validation in step_runner.py; no fallbacks |
| **Coder Timeout/Failure** | Job stuck in non-terminal state | CoderInvocationError handling; retry classification |
| **Backend Connectivity Loss** | Worker unable to claim/submit steps | Daemon heartbeat monitoring; local logging |
| **Workflow Bundle Drift** | Runtime uses outdated prompts | Bundle seeding on init; version tracking |
| **Protected Doc Modification** | Validation failures | Guardrails in step_runner.py; snapshot comparison |

### 4.2 Medium-Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Planning Attempt Budget Exhaustion** | Early termination of refinement loops | Configurable max_planning_attempts |
| **Artifact Path Resolution** | File not found errors | Canonical path resolution in runtime_context.py |
| **Schema Version Migration** | Legacy job state incompatibility | migrate_job_state() with version detection |
| **Windows/Unix Path Handling** | Cross-platform issues | Path abstraction layer |

### 4.3 Low-Priority Risks

- Test coverage gaps in actions package
- Documentation drift between code and docs

## 5. Main Architectural Observations

### 5.1 Strengths

1. **Strict Contract Enforcement**: The v2 sidecar contract eliminates ambiguity in step results
2. **Separation of Concerns**: Clear boundaries between CLI, step execution, routing, and state management
3. **Backend-First Design**: Worker/daemon modes treat backend as source of truth
4. **Extensible Action System**: New deterministic actions can be added to `actions/` package
5. **Multi-Model Support**: Claude, Codex, Qwen adapters with unified interface

### 5.2 Design Patterns

1. **State Machine**: Job states (IN_PROGRESS, WAITING_FOR_AUTO_RETRY, FAILED, etc.)
2. **Loop Context**: Review/refine loops with iteration tracking
3. **Replan Context**: Escalation from refinement to replanning
4. **Failure Classification**: AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, FATAL

### 5.3 Current Limitations

1. **Documentation Gap**: No comprehensive API documentation for internal modules
2. **Test Coverage**: Actions package lacks comprehensive tests
3. **Error Messages**: Some validation errors could be more actionable
4. **Cross-Platform**: Windows batch scripts may drift from Unix shell equivalents

## 6. Unresolved Documentation Gaps

The following gaps should be addressed by later bootstrap steps:

1. **API Documentation**: Module-level API docs for programmatic usage
2. **Action Development Guide**: How to add new deterministic actions
3. **Backend Integration Spec**: Detailed backend API contract
4. **Troubleshooting Guide**: Common failure modes and resolutions
5. **Migration Guide**: v1 to v2 migration procedures
6. **Configuration Reference**: Complete config.json schema documentation
7. **Workflow Authoring Guide**: How to create custom workflow families

## 7. Change Context

This analysis was generated as part of the `00_master_docs_bootstrap_v1` workflow, step `02_generate_project_analysis`, change `00DOC-GEN-20260702-005`.

**Baseline:** Repository scan at 2026-07-02T18:00:53+08:00
**Scope:** Full codebase inventory with 47 Python modules, 10 workflow families
**Method:** Static analysis of source code, configuration, and documentation
