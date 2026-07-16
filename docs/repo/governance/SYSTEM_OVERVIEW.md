---
template_id: "SYS-00-SO"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:13:00+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# System Overview

## Purpose

`agent-runner-v2` is a standalone workflow runner extracted from UKBE (UK Build Engine).
It orchestrates AI-Driven SDLC workflows with human approval gates, managing the full
lifecycle of software development artifacts from requirements through validation.

The runner executes declarative workflow bundles defined in TOML manifests, invoking
LLM coders for generative steps and deterministic Python actions for validation and
file operations. It bridges the gap between AI-assisted development and controlled,
auditable artifact production.

## Scope

### In Scope

- **Workflow orchestration**: Step-by-step execution with routing logic (approve/reject/replan)
- **Coder abstraction**: Pluggable LLM backend integration with sidecar metadata contracts
- **Action library**: Deterministic Python functions for file operations, validation, and site generation
- **Bootstrap governance**: Layer 1 ecosystem governance and Layer 2 repo master docs generation
- **Dual deployment**: Global runner home and local project runtime paths
- **Human approval gates**: Review steps with approve/reject transitions

### Out of Scope

- Direct code generation or modification (delegated to LLM coders)
- CI/CD pipeline execution (integrates with external systems)
- Source control operations (delegated to external tools)
- Production deployment (runner produces artifacts, not deployments)

## Primary Flows

### 1. Workflow Execution Flow

```
User → CLI/Daemon → Workflow Router → Step Runner → Coder/Action
    ↓                                                    ↓
Job State ←────────────── Result ←──────────────────────┘
    ↓
Routing Decision → Approve/Reject/Replan
```

The runner follows a step-by-step execution model:

1. **Workflow loading**: TOML manifest → `WorkflowBundle` dataclass
2. **Step execution**: Coder (LLM) or Action (Python) based on step type
3. **Routing**: Post-step routing based on result (approve/reject/replan)
4. **State management**: Job state persisted to `.ukbe-runner/jobs/<job_id>/`
5. **Notifications**: Optional Pushover notifications on step completion

### 2. Coder/Action Split

**Coder steps** (generative):
- Invoke external LLM processes (OpenCode, Claude, etc.)
- Prompt templates rendered with context placeholders
- Sidecar `meta.json` contract for result reporting
- Timeout handling and process management

**Action steps** (deterministic):
- Registered via `@action()` decorator
- Direct filesystem and validation operations
- No external process dependencies

### 3. Bootstrap Governance Flow

```
Layer 1: 00_layer1_governance_bootstrap_v1
    ↓ Generates docs/system/00_governance/
Layer 2: 00_master_docs_bootstrap_v2 (needs restoration)
    ↓ Generates docs/repo/sdlc/00_governance/
Layer 3+: SDLC workflow families
    ↓ Produces phase-specific artifacts
```

Bootstrap workflows generate governance documents without modifying source code.

## Architecture Profile

### Universal Baseline (Layer 1)

The universal ecosystem baseline provides:

- Documentation structure and template IDs
- Bundle taxonomy and ownership rules
- Runtime governance and publish model
- Scope purity requirements

Layer 1 documents are published to `docs/system/00_governance/bootstrap/`.

### Repository-Selected Profile

| Attribute | Value | Rationale |
|-----------|-------|-----------|
| `current_profile` | transitional | Migrating from monolithic to plugin-based workflow bundles |
| `target_profile` | plugin-based workflow bundles | Self-contained packages with declarative manifests |
| `migration_mode` | active | Branch `feat/plugin-workflow-system`, version 0.3.0 |
| `repo_state` | explicit | Has CODER_IMPLEMENTATION_SOP.md, governance docs |

### Plugin System Architecture

The plugin system is a **configuration source adapter**:

- Converts `WorkflowBundle` → legacy dict format
- Preserves execution pipeline compatibility
- Enables independent workflow package evolution
- Supports dual-path discovery (global first, local fallback)

## Key Risks

| Risk | Impact | Mitigation Status |
|------|--------|-------------------|
| Layer 2 bootstrap incomplete | Blocks SDLC workflow-family work | Requires restoration from archive |
| Plugin migration incomplete | Legacy `TEMPLATE_GROUPS` still referenced | Active migration on feature branch |
| Delivery-era artifact keys | Runtime not aligned to SDLC structure | Migration plan documented |
| Daemon subprocess CWD | `.env` loading failures | Fixed in v0.3.0 |
| Windows path handling | `Path.relative_to()` edge cases | Fixed with fallback logic |
| Notification credentials | Missing Pushover tokens cause silent failures | Credential resolution documented |

### Mitigation Strategies

1. **Prioritize Layer 2 restoration**: Unblock SDLC work by restoring master-docs bootstrap
2. **Adapter pattern**: Preserve compatibility during migration
3. **Comprehensive testing**: 45+ unit tests, integration tests for runtime paths
4. **Declarative doc protection**: Allow-list model for document deletion safety
