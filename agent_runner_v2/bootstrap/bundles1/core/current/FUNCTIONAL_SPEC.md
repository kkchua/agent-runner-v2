---
template_id: "SYS-00-FS"
title: "Functional Specification - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification

## Purpose

This document describes major behaviors and workflow capabilities grounded in the `agent-runner-v2` repository.

## System Purpose

`agent-runner-v2` provides a deterministic execution environment for structured multi-step LLM workflows. It bridges the gap between ad-hoc LLM interactions and production-grade workflow automation through:

- **Explicit Contracts**: Every step declares inputs, outputs, and routing rules
- **Structured Validation**: meta.json sidecars enforce output quality
- **State Persistence**: Jobs can be paused, inspected, and resumed
- **Multi-Model Support**: Seamless switching between LLM providers
- **Documentation Automation**: Generated docs synchronized with code

## Functional Capabilities

### CLI Execution Modes

The platform provides six distinct execution modes via the `ukbe-run-agent` CLI:

| Mode | Command | Purpose |
|------|---------|---------|
| **Initialize** | `init` | Seed runner home with config and bundles |
| **Run** | `run` | Local workflow execution with job management |
| **Poll** | `poll` | Backend-connected single-step execution |
| **Worker** | `worker` | Backend-connected continuous execution |
| **Daemon** | `daemon` | Workstation supervisor for background operation |
| **Execute Step** | `execute-step` | Direct step execution (internal/spawned) |

### Workflow Engine

The core workflow engine provides:

| Capability | Implementation | File |
|------------|----------------|------|
| **Prompt Rendering** | Template loading + variable substitution | `step_runner.py` |
| **Step Execution** | Spawn coder/action subprocess | `step_runner.py` |
| **Completion Polling** | Monitor for sidecar file | `step_runner.py` |
| **Sidecar Validation** | JSON schema validation | `step_runner.py` |
| **Routing** | Next step selection based on status | `workflow_router.py` |

### Job State Management

Job lifecycle management capabilities:

| Capability | Function | Schema Version |
|------------|----------|----------------|
| **Create** | `create_job()` | v6 |
| **Load** | `load_job()` with migration | v1-v6 |
| **Save** | `save_job()` with checksum | v6 |
| **Advance** | `advance_step()` with validation | v6 |
| **Retry** | `prepare_state_for_retry()` | v6 |
| **Recovery** | `recover_exhausted_planning_job()` | v6 |

### Multi-Model Support

Coder adapter capabilities:

| Model | Adapter | Invocation |
|-------|---------|------------|
| **Claude** | `claude_adapter.py` | Subprocess with `--claude` |
| **Codex** | `codex_adapter.py` | Subprocess with `--codex` |
| **Qwen** | `qwen_adapter.py` | Subprocess with `--qwen` |
| **Aliased** | `resolve_coder()` | Config-based resolution |

### Runner Actions

Deterministic action modules (29 actions):

| Category | Actions |
|----------|---------|
| **Documentation** | `sync_system_docs`, `sync_codebase_docs`, `validate_*_docs` |
| **Codebase** | `scan_repo_codebase`, `prepare_delivery_scaffold` |
| **Site Generation** | `generate_site`, `generate_site_pdf`, `publish_architecture_site` |
| **Media** | `execute_t2i`, `execute_i2v`, `execute_voiceover`, `assemble_video` |
| **Artifact** | `copy_artifact`, `promote_artifact`, `archive_previous_version` |

### Documentation Generation

Workflow-generated documentation:

| Workflow | Output |
|----------|--------|
| `00_master_docs_bootstrap_v1` | System governance documents |
| `10_execution_scaffold_v1` | Delivery SOP, agents, templates |
| `40_documentation_sync_v1` | Codebase inventory, module docs |
| `41_*_doc_v1` | Audience-specific documentation |
| `50_architecture_site_v1` | HTML architecture sites |

### Validation

Validation capabilities:

| Target | Validator | Schema |
|--------|-----------|--------|
| **Job State** | Internal validation | `job_schema.json` |
| **LLM Response** | Sidecar validation | `llm_response_schema.json` |
| **System Docs** | `validate_system_docs` | Section requirements |
| **Codebase Docs** | `validate_codebase_docs` | Structure validation |
| **Delivery Docs** | `validate_delivery_docs` | Template compliance |
| **Architecture Site** | `validate_architecture_site` | HTML structure |

## Actors

### Human Actors

| Actor | Role | Primary Interactions |
|-------|------|----------------------|
| **Developer** | Builds on/extends platform | CLI (`run`, `init`), extends actions/workflows |
| **Operator** | Deploys and manages runtime | CLI (`daemon`, `poll`), monitors job state |
| **Stakeholder** | Evaluates platform value | Reads generated documentation |
| **Reviewer** | Approves workflow outputs | Review step outputs, provides feedback |

### System Actors

| Actor | Role | Primary Interactions |
|-------|------|----------------------|
| **CLI** | Command-line interface | Parses args, dispatches to handlers |
| **Workflow Engine** | Step orchestrator | Loads, renders, executes, routes |
| **Coder Adapters** | LLM invocation | Spawns subprocess, manages execution |
| **Runner Actions** | Deterministic operations | Executes file operations, validations |
| **Backend Client** | Remote coordination | Polls for work, submits results |
| **Daemon** | Background supervisor | Manages child processes, heartbeats |

## Core Behaviors

### Step Execution

**Trigger**: CLI `run` command or backend work assignment

**Flow**:
1. Load job state from `job.json`
2. Resolve workflow template group
3. Render prompt from template + job state
4. Execute step via coder adapter or action
5. Poll for completion (sidecar file)
6. Validate sidecar against schema
7. Route based on status (APPROVED/REJECTED)

**Output**: Updated job state, generated artifacts, routing decision

### Job Lifecycle

**States**:
- `created` → `running` → `completed` | `failed` | `cancelled`

**Transitions**:
- Create: Initializes with schema version
- Run: Advances through workflow steps
- Complete: Reaches terminal step with success
- Fail: Exhausts retries or hard failure
- Cancel: External cancellation request

**Persistence**: Job state saved to `job.json` after each step

### Workflow Routing

**Routing Logic**:
- `APPROVED` → next step in sequence
- `REJECTED` → retry or refine step
- `FAILURE` → failure handling path

**Decision Sources**:
- `REVIEW_DECISIONS`: Auto-routing based on validation
- `HUMAN_DECISIONS`: Human review gates
- `CONTROL_CLASSES`: Failure classification

### Bootstrap Seeding

**Trigger**: `ukbe-run-agent init`

**Flow**:
1. Create runner home directory (`~/.ukbe-runner`)
2. Copy config template to `config.json` (if absent)
3. Copy workflow bundles to `workflows/`
4. Copy core bundles to `bundles/`
5. Create job directory structure

**Idempotency**: Safe to re-run; preserves existing config and jobs

### Documentation Sync

**Trigger**: `40_documentation_sync_v1` workflow

**Flow**:
1. Scan repository for source files
2. Compare with existing codebase docs
3. Generate/update module documentation
4. Update codebase inventory
5. Generate change impact document
6. Validate documentation completeness

**Output**: Synchronized documentation reflecting current codebase

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
