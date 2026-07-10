---
template_id: "SYS-03-CA"
title: "Component Architecture - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:56:49+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture: agent-runner-v2

## Component Groups

### 1. Core Execution Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **CLI Entry** | `run_agent.py` | Command parsing, orchestration, top-level error handling |
| **Step Runner** | `step_runner.py` | Prompt rendering, coder/action invocation, sidecar validation |
| **Workflow Router** | `workflow_router.py` | Post-step routing decisions, approve/reject/failure handling |
| **Job State** | `job_state.py` | Job.json lifecycle, state transitions, persistence |

### 2. Coder Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Coder Adapters** | `coder_adapters.py` | LLM invocation (Claude, Codex, Qwen), polling, error handling |
| **Model Config** | `model_config.py` | Model resolution, alias mapping, configuration |

### 3. Bootstrap Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Bundle Loader** | `bundle_loader.py` | Workflow bundle discovery, loading, bootstrap seeding |
| **Template Groups** | `template_groups.py` | Legacy workflow definitions (2453+ lines) |
| **Workflow Packages** | `workflow_packages/` | Plugin-based workflow system (new) |

### 4. Runtime Context Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Runtime Context** | `runtime_context.py` | Process-local context, path resolution, workflow module access |
| **Constants** | `constants.py` | Centralized artifact paths, folder keys, section requirements |

### 5. Action Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Actions Package** | `actions/` | 30+ deterministic runner actions |
| **Scan Repo** | `actions/scan_repo_codebase.py` | Repository scanning for documentation |
| **Sync Codebase** | `actions/sync_codebase_docs.py` | Codebase documentation synchronization |
| **Validate Delivery** | `actions/validate_delivery_docs.py` | Delivery document validation |
| **Generate Site** | `actions/generate_site.py` | HTML site generation |
| **Prepare Scaffold** | `actions/prepare_delivery_scaffold.py` | Delivery scaffold preparation |

### 6. Support Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Notifications** | `notifications.py` | Pushover, console notifications |
| **Notification Manager** | `notification_manager.py` | Workflow/step notification orchestration |
| **Backend Client** | `backend_client.py` | Backend API communication |
| **Daemon** | `daemon.py` | Long-running supervisor process |
| **Runner Logger** | `runner_logger.py` | Structured logging |
| **Architecture Site** | `architecture_site.py` | HTML site building utilities |
| **Codebase Docs** | `codebase_docs.py` | Codebase documentation utilities |
| **System Docs** | `system_docs.py` | System documentation utilities |
| **Documentation Guardrails** | `documentation_guardrails.py` | Generated doc validation, protection |

### 7. Schema Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Action Result** | `action_result.py` | Action result dataclass |
| **Artifact Paths** | `artifact_paths.py` | Artifact path computation |
| **Execution Request** | `execution_request.py` | Execution request schema |
| **Execution Result** | `execution_result.py` | Execution result schema |
| **Runner Actions** | `runner_actions.py` | Action registry |
| **Exceptions** | `exceptions.py` | Custom exceptions |

### 8. Command Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Approve Commands** | `approve_commands.py` | CLI approval commands |
| **Engine Commands** | `engine_commands.py` | CLI engine commands |
| **Submit Commands** | `submit_commands.py` | CLI submission commands |
| **Workflow Specs** | `workflow_specs.py` | Workflow specification parsing |
| **Workflow Spec Commands** | `workflow_spec_commands.py` | Workflow spec CLI commands |
| **Submitter** | `submitter.py` | Job submission utilities |

## Dependencies

```
run_agent.py
├── bundle_loader.py
├── job_state.py
├── runtime_context.py
├── step_runner.py
│   ├── coder_adapters.py
│   ├── exceptions.py
│   └── constants.py
├── workflow_router.py
│   ├── job_state.py
│   └── notifications.py
└── workflow_packages/
    ├── loader.py
    ├── registry.py
    └── base.py
```

## Architecture Posture

### Current Profile: `provisional`

This repository follows a **provisional** architecture profile, not the universal baseline. The provisional posture reflects:

1. **Active migration**: Plugin workflow system replacing monolithic TEMPLATE_GROUPS
2. **Bootstrap/runtime distinction**: Careful synchronization required
3. **Documentation establishment**: Bootstrap documents being generated
4. **Test coverage verification**: Ongoing

### Target Profile: `explicit`

The intended target is `explicit` - fully documented, tested, and typed with clear architectural boundaries.

### Migration Mode: `in_progress`

The current migration is the plugin workflow system on branch `feat/plugin-workflow-system`.

## Architectural Notes

### Strict v2 Sidecar Contract

The system enforces a strict contract:
- `meta.json` is the **only** structured result channel
- No markdown write-backs by the runner
- No silent recovery paths
- Hard failures route explicitly through failure handling

### Adapter Pattern for Workflow Loading

The plugin system is a **configuration source adapter**:

```
WorkflowBundle (workflow.toml + prompts/)
    ↓
Adapter (workflow_packages/loader.py)
    ↓
Dict format (same as TEMPLATE_GROUPS)
    ↓
Existing execution pipeline
```

This minimizes risk while enabling maintainable workflow development.

### Dual-Path Discovery

Runtime workflow discovery uses global-first, local-fallback:

1. Check `~/.ukbe-runner/workflows/<workflow>/`
2. Fallback to repo `workflows/<workflow>/`

### Centralized Constants

All documentation artifact paths and section requirements moved to `constants.py`:
- Pre-computed path constants
- Zero hardcoded strings in path construction
- Direct lookup during validation

### Process-Per-Step Execution

The daemon spawns fresh subprocesses for each step:
- Code changes picked up automatically
- No daemon restart required
- Isolation between steps

### Documentation-First Governance

The system enforces documentation as a first-class artifact:
- Workflows generate and validate docs
- Codebase inventory auto-synchronizes
- Architecture sites publish audience-specific views

## Component Boundaries

| Boundary | Definition |
|----------|------------|
| **CLI ↔ Core** | `run_agent.py` delegates to `step_runner.py` |
| **Core ↔ Coder** | `step_runner.py` invokes `coder_adapters.py` |
| **Core ↔ Action** | `step_runner.py` calls actions directly |
| **Core ↔ Router** | `step_runner.py` returns result to caller, which calls `workflow_router.py` |
| **Core ↔ State** | `job_state.py` provides persistence |
| **Core ↔ Bundle** | `bundle_loader.py` provides workflow definitions |
| **Runtime ↔ Bootstrap** | `runtime_context.py` abstracts path resolution |

---

*Last updated: 2026-07-10T19:56:49+08:00 via workflow `00_master_docs_bootstrap_v2`*
