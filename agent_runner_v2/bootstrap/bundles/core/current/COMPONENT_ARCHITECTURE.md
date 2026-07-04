---
template_id: "SYS-03-CA"
title: "Component Architecture"
status: "active"
generated: "2026-07-04T14:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Component Architecture

## Architecture Profile

This repository follows a **repo-selected profile** with the following posture:

| Attribute | Value | Notes |
|-----------|-------|-------|
| `current_profile` | `provisional` | Bootstrap in progress |
| `target_profile` | `explicit` | Full architecture documentation |
| `migration_mode` | `in-progress` | Documentation being generated |
| `architecture_pattern` | Layered orchestration | Core, adapters, actions layers |

### Profile Separation

The platform separates **universal baseline** (applicable to all repos using the runner) from **repo-specific** concerns:

| Concern | Universal Baseline | Repo-Specific (agent-runner-v2) |
|---------|-------------------|--------------------------------|
| Execution contract | v2 sidecar rules | Workflow step definitions |
| Artifact model | Key classification | 40+ artifact keys in template_groups |
| Routing behavior | APPROVED/REJECTED/FAILURE | Per-step routing configuration |
| Coder abstraction | Adapter interface | Claude/Codex/Qwen implementations |

### DDD/EDA Status

| Pattern | Status | Rationale |
|---------|--------|-----------|
| **Domain-Driven Design (DDD)** | Conditional | Applied to workflow domain modeling; not universal standard |
| **Event-Driven Architecture (EDA)** | Conditional | Event loop in daemon; explicit routing preferred over event bus |

## Component Groups

### Group 1: Core Orchestration

| Component | File | Responsibility | Dependencies |
|-----------|------|----------------|--------------|
| **CLI Entry** | `run_agent.py` | Argument parsing, command dispatch, main orchestration | All other components |
| **Step Runner** | `step_runner.py` | Prompt rendering, coder/action invocation, meta.json validation | coder_adapters, runtime_context |
| **Workflow Router** | `workflow_router.py` | Post-step routing, review/refine loops, failure classification | job_state, exceptions |
| **Job State** | `job_state.py` | Job lifecycle, persistence, migration, advancement logic | runtime_context, doc_paths |

### Group 2: Coder Abstraction

| Component | File | Responsibility | Dependencies |
|-----------|------|----------------|--------------|
| **Coder Adapters** | `coder_adapters.py` | LLM provider abstraction, invocation, polling, usage tracking | model_config |
| **Model Config** | `model_config.py` | Model aliases, timeout defaults, capability mapping | - |

### Group 3: Runtime Context

| Component | File | Responsibility | Dependencies |
|-----------|------|----------------|--------------|
| **Runtime Context** | `runtime_context.py` | Active workflow bundle resolution, path management | bundle_loader |
| **Bundle Loader** | `bundle_loader.py` | Bootstrap seeding, workflow bundle loading, template resolution | - |

### Group 4: Runner Actions

| Component | Purpose |
|-----------|---------|
| `scan_repo_codebase.py` | Repository analysis and documentation generation |
| `sync_codebase_docs.py` | Codebase documentation synchronization |
| `sync_system_docs.py` | System documentation synchronization |
| `validate_codebase_docs.py` | Codebase documentation validation |
| `validate_system_docs.py` | System documentation validation |
| `validate_delivery_docs.py` | Delivery documentation validation |
| `prepare_delivery_scaffold.py` | Delivery scaffold preparation |
| `finalize_bootstrap.py` | Bootstrap completion actions |
| `copy_artifact.py` | Artifact file copying |
| `promote_artifact.py` | Artifact promotion between stages |
| `promote_init.py` | Initiative promotion |
| `publish_architecture_site.py` | Architecture site publishing |
| `validate_architecture_site.py` | Architecture site validation |
| `execute_t2i.py` | Text-to-image execution |
| `execute_i2v.py` | Image-to-video execution |
| `execute_voiceover.py` | Voiceover execution |
| `assemble_video.py` | Video assembly |
| `submit_comfyui.py` | ComfyUI submission |

### Group 5: Backend Integration

| Component | File | Responsibility |
|-----------|------|----------------|
| **Backend Client** | `backend_client.py` | REST API client for work claiming and submission |
| **Daemon** | `daemon.py` | Workstation supervision, process management, heartbeats |

### Group 6: Support Utilities

| Component | File | Responsibility |
|-----------|------|----------------|
| **Documentation Guardrails** | `documentation_guardrails.py` | Protected document enforcement |
| **Codebase Docs** | `codebase_docs.py` | Codebase documentation utilities |
| **System Docs** | `system_docs.py` | System documentation utilities |
| **Artifact Paths** | `artifact_paths.py` | Path resolution for artifacts |
| **Doc Paths** | `doc_paths.py` | Documentation path utilities |
| **Bundle Taxonomy** | `bundle_taxonomy.py` | Bundle structure definitions |
| **Runner Logger** | `runner_logger.py` | Structured logging |
| **Exceptions** | `exceptions.py` | Custom exception types |
| **Tools** | `tools/agent_tools.py` | Progress tracking utilities |

### Group 7: Bootstrap Workflows

| Component | File | Responsibility |
|-----------|------|----------------|
| **Template Groups** | `bootstrap/workflows/default/template_groups.py` | 11 workflow families, 83+ step definitions |
| **Prompts** | `bootstrap/workflows/default/prompts/*` | Per-step prompt templates |
| **Schemas** | `bootstrap/workflows/default/*.json` | Job schema, LLM response schema, usage schema |

## Component Dependencies

```
                    CLI (run_agent.py)
                         │
    ┌────────────────────┼────────────────────┐
    ↓                    ↓                    ↓
step_runner.py   workflow_router.py   job_state.py
    │                    │                    │
    ↓                    ↓                    ↓
coder_adapters.py   exceptions.py    runtime_context.py
    │                                     │
    ↓                                     ↓
model_config.py                    bundle_loader.py
                                          │
                                          ↓
                              bootstrap/workflows/default/
```

## Architectural Notes

### Separation of Concerns

The architecture demonstrates clean separation across layers:

1. **CLI Layer** (`run_agent.py`): Command parsing and orchestration only
2. **Execution Layer** (`step_runner.py`): Step execution and validation
3. **Routing Layer** (`workflow_router.py`): Pure routing logic, no I/O
4. **State Layer** (`job_state.py`): State mutations and persistence
5. **Adapter Layer** (`coder_adapters.py`): LLM provider abstraction
6. **Action Layer** (`actions/`): Deterministic operations

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

### Template Group Configuration

Workflows are data-driven via `template_groups.py`:

- Step definitions with `required_inputs`, `produces`, `result_meta_key`
- Coder configuration with `default` and `allowed` models
- Routing configuration via `on_reject_refine` and `on_exhaust_replan`
- Timeout overrides per step (`coder_timeout_seconds`)

---

*This component architecture describes the internal structure of agent-runner-v2. See SYSTEM_FILE_STRUCTURE.md for directory organization and file-level details.*
