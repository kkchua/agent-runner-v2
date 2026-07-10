---
title: "Component Architecture"
template_id: "SYS-03-CA"
status: "active"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T11:57:31+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture: agent-runner-v2

## Architecture Profile

| Attribute | Value |
|-----------|-------|
| **Current Profile** | `provisional` |
| **Target Profile** | `structured_delivery` |
| **Migration Mode** | `incremental` |
| **Repo State** | `explicit` |

**Rationale**: The repository is explicit (not empty) with 67+ module docs, structured workflow definitions, and active documentation governance. The provisional status reflects ongoing documentation reconciliation and bundle taxonomy evolution.

## Component Groups

### 1. Core Execution Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| **CLI Entry Point** | `run_agent.py` | Argument parsing, command dispatch, top-level orchestration |
| **Step Runner** | `step_runner.py` | Prompt rendering, coder/action invocation, sidecar validation |
| **Workflow Router** | `workflow_router.py` | Post-step routing for approve/reject/failure cases |
| **Job State** | `job_state.py` | `job.json` lifecycle, state migration, retry logic |

**Interaction Pattern**:
```
CLI → load job → run_step() → invoke_coder() → read meta.json → route_after_step()
```

### 2. Coder Adapter Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| **Coder Adapters** | `coder_adapters.py` | Claude/Codex/Qwen invocation and polling |
| **Model Config** | `model_config.py` | Model resolution, alias handling |

**Key Contract**: Adapters return structured results; sidecar is the only communication channel.

### 3. Runtime Context Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| **Runtime Context** | `runtime_context.py` | Active workflow/runtime path context, lazy path resolution |
| **Bundle Loader** | `bundle_loader.py` | Bootstrap seeding, workflow bundle loading |
| **Constants** | `constants.py` | Centralized artifact keys, folder keys, path templates |

**Pattern**: PathProxy enables lazy resolution from current context.

### 4. Action Layer (Deterministic)

| Component | Path | Responsibility |
|-----------|------|----------------|
| **26 Runner Actions** | `actions/*.py` | Deterministic, non-LLM steps (validation, sync, generation) |

**Key Actions**:
- `scan_repo_codebase.py` - Codebase inventory generation
- `validate_*_docs.py` - Document validation per taxonomy
- `sync_*_docs.py` - Documentation synchronization
- `generate_site.py` - HTML architecture site generation
- `finalize_bootstrap.py` - Bootstrap completion handling

### 5. Backend Integration Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| **Backend Client** | `backend_client.py` | API communication, authentication |
| **Daemon** | `daemon.py` | Workstation supervisor, subprocess spawning |
| **Runner Logger** | `runner_logger.py` | Structured logging, log routing |

**Daemon Architecture**: Spawns fresh subprocess per step via `subprocess.Popen()`:
- Code changes picked up automatically without restart
- Each step isolated with fresh Python interpreter
- No shared memory between steps

### 6. Documentation Governance Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| **Documentation Guardrails** | `documentation_guardrails.py` | Protection rules, generated-doc manifest |
| **Codebase Docs** | `codebase_docs.py` | Codebase documentation utilities |
| **System Docs** | `system_docs.py` | System documentation utilities |
| **Architecture Site** | `architecture_site.py` | HTML site generation orchestration |
| **Site Styles** | `site_styles.py` | CSS/styling for generated sites |

### 7. Bootstrap Bundle Layer

| Component | Path | Responsibility |
|-----------|------|----------------|
| **Template Groups** | `bootstrap/workflows/default/template_groups.py` | Workflow step definitions |
| **Prompt Templates** | `bootstrap/workflows/default/prompts/` | LLM prompt templates per step |
| **JSON Schemas** | `bootstrap/workflows/default/*.json` | Job schema, response schema, model mapping |

**Runtime Contract**: Runtime bundles loaded from `~/.ukbe-runner/workflows/`, not repo tree.

### 8. Support Utilities

| Component | File | Responsibility |
|-----------|------|----------------|
| **Notifications** | `notifications.py` | Pushover notification dispatch |
| **Notification Manager** | `notification_manager.py` | Workflow/step notification orchestration |
| **Artifact Paths** | `artifact_paths.py` | Path computation utilities |
| **Doc Paths** | `doc_paths.py` | Documentation path helpers |
| **Exceptions** | `exceptions.py` | Custom exception types |
| **Workflow Specs** | `workflow_specs.py`, `workflow_spec_commands.py` | Workflow specification handling |

## Architectural Notes

### Dependency Direction

```
CLI (run_agent.py)
  ↓
Step Runner ← → Coder Adapters
  ↓               ↓
Job State ← → Backend Client
  ↓
Runtime Context ← → Bundle Loader
  ↓
Constants (single source of truth)
```

### Key Architectural Decisions

| Decision | Rationale | Status |
|----------|-----------|--------|
| **Sidecar-only result channel** | Eliminates fragile parsing; clean contract boundary | Active |
| **Subprocess per step** | Automatic code reload; isolation | Active |
| **Centralized constants** | Single source of truth; prevents path drift | Active |
| **Declarative document protection** | `produces` lists vs imperative guards | Active |
| **Workflow router decoupling** | Replaces monolithic state management | Active |

### DDD/EDA Status

| Pattern | Application | Notes |
|---------|-------------|-------|
| **Domain-Driven Design (DDD)** | Conditional | Applied to documentation taxonomy, not universal |
| **Event-Driven Architecture (EDA)** | Conditional | Backend events when connected; local state otherwise |

The architecture follows a **structured delivery** profile rather than strict DDD/EDA, prioritizing:
1. Explicit contracts over implicit conventions
2. Deterministic routing over event choreography
3. Filesystem state over distributed consistency
