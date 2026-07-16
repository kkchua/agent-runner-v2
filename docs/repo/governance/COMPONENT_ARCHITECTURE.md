---
template_id: "SYS-03-CA"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:22:07+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Component Architecture: agent-runner-v2

## Architecture Posture

This repository follows a **transitional profile** migrating from monolithic `TEMPLATE_GROUPS` to plugin-based workflow bundles.

| Attribute | Value | Evidence |
|-----------|-------|----------|
| `current_profile` | transitional | Migrating from monolithic `TEMPLATE_GROUPS` to plugin-based workflow packages |
| `target_profile` | plugin-based workflow bundles | `workflow_packages/` directory with `base.py`, `loader.py`, `registry.py` |
| `migration_mode` | active | Branch `feat/plugin-workflow-system`, version 0.3.0 |
| `repo_state` | explicit | Has `CODER_IMPLEMENTATION_SOP.md`, governance docs under `docs/system/00_governance/` |
| `evidence_sources` | codebase inventory, module docs, migration plan | `docs/repo/codebase/01_inventory/`, `docs/system/03_ai_driven_sdlc_migration_plan.md` |

**DDD/EDA Status**: Domain-Driven Design (DDD) and Event-Driven Architecture (EDA) are **not universal standards** for this repository. The system follows a workflow-centric architecture with step-based orchestration. DDD patterns may apply to specific workflow families but are not required across the codebase.

## Component Groups

### Core Execution

| Component | Module | Purpose | Dependencies |
|-----------|--------|---------|--------------|
| Entry Point | `run_agent.py` | CLI argument parsing, job initialization, mode dispatch | argparse, job_state, workflow_router |
| Step Runner | `step_runner.py` | Invoke coder/action, read meta.json, validate artifacts | coder_adapters, runtime_context |
| Workflow Router | `workflow_router.py` | Post-step routing (approve/reject/replan), failure handling | job_state, notification_manager |
| Job State | `job_state.py` | Persist and load job state, step directories | json, pathlib |

### Coder Integration

| Component | Module | Purpose | Dependencies |
|-----------|--------|---------|--------------|
| Coder Adapters | `coder_adapters.py` | Invoke external LLM processes, manage sidecar contract | subprocess, model_config, runner_logger |
| Model Config | `model_config.py` | LLM model selection and configuration | json, pathlib |
| Runtime Context | `runtime_context.py` | Build context dict for prompt rendering | constants, artifact_paths |

### Backend Integration

| Component | Module | Purpose | Dependencies |
|-----------|--------|---------|--------------|
| Daemon | `daemon.py` | Worker daemon supervisor, backend polling | subprocess, signal, config_loader |
| Backend Client | `backend_client.py` | HTTP client for backend API | requests, json |
| Runner Logger | `runner_logger.py` | Structured logging for daemon/worker modes | logging, json |

### Action Library

The `actions/` package contains 29 deterministic action modules implementing non-coder steps:

| Category | Modules | Purpose |
|----------|---------|---------|
| Validation | `validate_*.py` (12 files) | Document and site validation |
| Site Generation | `generate_site.py`, `generate_site_pdf.py` | HTML/PDF site generation |
| Sync | `sync_codebase_docs.py`, `sync_system_docs.py` | Document synchronization |
| Promotion | `promote_artifact.py`, `promote_init.py` | Artifact promotion |
| Bootstrap | `finalize_bootstrap.py`, `archive_previous_version.py` | Bootstrap lifecycle |
| Media | `execute_t2i.py`, `execute_i2v.py`, `execute_voiceover.py`, `assemble_video.py` | Media generation |
| Codebase | `scan_repo_codebase.py` | Repository scanning |

### Bootstrap Workflows

| Workflow Family | Steps | Purpose |
|-----------------|-------|---------|
| `00_bootstrap_lifecycle_admin_v1` | 5 | Bootstrap lifecycle management |
| `00_layer1_governance_bootstrap_v1` | 6 | Layer 1 ecosystem governance generation |
| `00_repo_master_docs_bootstrap_v1` | 14 | Repo master docs and architecture synthesis |

### Workflow Package System

| Component | Module | Purpose |
|-----------|--------|---------|
| Base | `workflow_packages/base.py` | `WorkflowBundle`, `StepConfig`, `BundleGovernance` dataclasses |
| Loader | `workflow_packages/loader.py` | TOML manifest parsing, validation |
| Registry | `workflow_packages/registry.py` | Dual-path discovery (global first, local fallback) |

### Support Modules

| Component | Module | Purpose |
|-----------|--------|---------|
| Constants | `constants.py` | Artifact keys, folder paths, centralized path construction |
| Config Loader | `config_loader.py` | Configuration file resolution |
| Notifications | `notifications.py`, `notification_manager.py` | Pushover notification integration |
| Doc Paths | `doc_paths.py` | Documentation path utilities |
| Architecture Site | `architecture_site.py` | Site generation support |

## Architectural Notes

### Adapter Pattern

The plugin system converts `WorkflowBundle` → legacy dict format, preserving execution pipeline compatibility. This minimizes risk by reusing the proven execution pipeline in `step_runner.py` and `workflow_router.py`.

### Sidecar Contract

Meta.json decouples coder output from runner state management:

```
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "...",
    "artifacts": { ... }
  },
  "runner_data": { ... },
  "usage": { ... }
}
```

### Layer Dependency Chain

```
Layer 1: 00_layer1_governance_bootstrap_v1 → docs/system/00_governance/
    ↓
Layer 2: 00_repo_master_docs_bootstrap_v1 → docs/repo/governance/
    ↓
Layer 3+: SDLC workflow families → docs/repo/sdlc/
```

**Current Status**:
- Layer 1: ✅ Operational
- Layer 2: ⚠️ In progress (this bootstrap pass)
- Layer 3+: ❌ Blocked until Layer 2 complete

### Dual-Path Deployment

Plugin workflow packages are discovered in order:
1. Global: `%USERPROFILE%\.ukbe-runner\workflows\<workflow_name>\`
2. Local: `agent_runner_v2/bootstrap/workflows/default/<workflow_name>/`

This allows stable workflows to be deployed globally while development versions remain in the local project.

### Runtime Isolation

Each step execution creates an isolated working directory under `.ukbe-runner/jobs/<job_id>/<step_id>/`. The step directory contains:
- Prompt file (rendered template)
- Meta.json sidecar (result)
- Any generated artifacts

### Zero Source Mutation

Bootstrap workflows must not alter source code. All generated artifacts are documentation files under `docs/`. This constraint is enforced by:
- Explicit `allowed_write_paths` in workflow configuration
- Documentation guardrails in `documentation_guardrails.py`
- Manual review gates before destructive operations

## Dependencies

### Internal Dependencies

- Python 3.12+ (per project requirements)
- No runtime database (file-based state only)
- Standard library preferred over third-party packages

### External Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `requests` | Backend API communication | For daemon mode |
| `markdown` | Architecture site generation | For 50_architecture_site_v1 |
| `pytest` | Testing | Development only |

## Boundaries

### Internal Boundaries

| Boundary | Modules | Crossing Mechanism |
|----------|---------|-------------------|
| Core ↔ Coder | `step_runner.py` ↔ `coder_adapters.py` | Function calls, dataclasses |
| Core ↔ Backend | `run_agent.py` ↔ `daemon.py` | Subprocess spawn |
| Core ↔ Actions | `step_runner.py` ↔ `actions/*.py` | `@action()` decorator |

### External Boundaries

| Boundary | Protocol | Owner |
|----------|----------|-------|
| LLM Coders | Subprocess/stdio | External process |
| Backend API | HTTP/JSON | External server |
| Pushover | HTTP POST | External service |
| Git | CLI | External process (read-only) |
