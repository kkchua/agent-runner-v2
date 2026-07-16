---
template_id: "SYS-00-BT"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:13:00+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Bundle Taxonomy

This document defines the bundle classes, ownership rules, and packaging
standards for the `agent-runner-v2` workflow bundle ecosystem. It establishes
what bundles exist, who owns them, and how they are structured.

## Bundle Classes

The repository defines three bundle classes aligned with the ecosystem taxonomy:

### Core Governance Bundles

Core governance bundles contain foundational governance documents and runtime
infrastructure for the workflow orchestration system.

**Characteristics:**

- Define ecosystem-wide governance rules
- Establish documentation standards and validation gates
- Provide runtime control plane definitions
- Must remain stable and rarely change
- Published to `agent_runner_v2/bootstrap/bundles/core/current/`

**Examples in this repository:**

| Bundle | Purpose | Location |
|--------|---------|----------|
| Layer 1 governance | Ecosystem baseline documents | `bootstrap/bundles/core/current/` |
| Runtime governance | Workflow execution rules | `bootstrap/bundles/core/current/RUNTIME_GOVERNANCE.md` |
| Documentation standard | Doc authority and structure | `bootstrap/bundles/core/current/DOCUMENTATION_STANDARD.md` |

### Plugin Workflow Bundles

Plugin workflow bundles contain self-contained workflow definitions with their
associated prompts, actions, and context extensions.

**Characteristics:**

- Self-contained workflow definitions
- Declarative TOML manifest (`workflow.toml`)
- Prompt templates in `prompts/` directory
- Optional context extensions (`context_extensions.py`)
- Optional workflow-specific actions (`actions.py`)
- May be single-workflow or multi-workflow bundles

**Current bootstrap workflow bundles:**

| Bundle | Steps | Purpose |
|--------|-------|---------|
| `00_bootstrap_lifecycle_admin_v1` | 5 | Bootstrap lifecycle management |
| `00_layer1_governance_bootstrap_v1` | 6 | Layer 1 governance generation |
| `00_repo_master_docs_bootstrap_v1` | 14 | Repo master docs bootstrap |

**Deployment paths:**

- Global: `%USERPROFILE%\.ukbe-runner\workflows\<workflow_name>\`
- Local: `agent_runner_v2/bootstrap/workflows/default/` (fallback)

### Domain Bundles

Domain bundles contain domain-specific logic, templates, and configurations
that support specific business domains or use cases.

**Characteristics:**

- Domain-specific business logic
- Templates and configurations for specific use cases
- May depend on core governance or plugin workflow bundles
- Managed by domain-specific teams
- Planned for SDLC workflow families (10, 20, 30, etc.)

**Planned SDLC domain bundles:**

| Bundle Family | Purpose | Status |
|---------------|---------|--------|
| `10_*` | Requirements phase | Planned |
| `20_*` | Planning phase | Planned |
| `30_*` | Task management phase | Planned |
| `40_*` | Execution phase | Planned |
| `50_*` | Validation phase | Planned |

## Ownership Rules

### Core Governance Bundle Ownership

| Bundle Type | Owner | Change Authority |
|-------------|-------|------------------|
| Layer 1 governance docs | Layer 1 governance workflow | System architects |
| System bootstrap bundles | Bootstrap workflows | System architects |
| Runtime control plane | Runtime governance workflow | System architects |

Core governance bundles require system architect approval for changes.

### Plugin Workflow Bundle Ownership

| Bundle Type | Owner | Change Authority |
|-------------|-------|------------------|
| Bootstrap lifecycle | Bootstrap workflow team | System architects |
| Layer 1 governance | Layer 1 governance workflow | System architects |
| Repo master docs | Master docs workflow | System architects |
| SDLC workflows | SDLC team (planned) | SDLC team lead |

Plugin workflow bundles are owned by the teams that create and maintain them.

### Ownership Principles

1. **Clear Ownership**: Every bundle has exactly one owner
2. **Change Authority**: Owners control changes to their bundles
3. **Dependency Direction**: Lower layers do not depend on higher layers
4. **Stability Guarantees**: Core governance bundles are most stable

## Packaging Standards

### Core Governance Bundle Packaging

Core governance bundles must be packaged with:

- Complete governance documentation
- Validation schemas and checks
- Version identifier in `bootstrap_publish_manifest.json`
- Change log for governance changes

### Plugin Workflow Bundle Packaging

Plugin workflow bundles must be packaged with:

- **Required**: `workflow.toml` — Declarative manifest with complete metadata
- **Required**: `prompts/` — Prompt template files for all coder steps
- **Optional**: `context_extensions.py` — Workflow-specific context hooks
- **Optional**: `actions.py` — Workflow-specific action implementations
- **Optional**: `bundle_governance.toml` — Governance extension for generated artifacts

### Workflow Manifest Schema

The `workflow.toml` manifest must include:

```toml
[workflow]
name = "<workflow_name>"
version = "<semver>"
description = "<one-line description>"
layer = 1  # Layer number (1, 2, 3+)

[steps.<step_id>]
type = "coder" | "action" | "review-refine-replan"
prompt = "<prompt_file>"  # For coder steps
action = "<action_name>"  # For action steps
# ... step-specific configuration
```

### Domain Bundle Packaging

Domain bundles must be packaged with:

- Domain logic modules
- Domain templates and configurations
- Dependency declarations on required bundles
- Version identifier in manifest

## Bundle Registry

The workflow registry (`_registry/`) contains:

| File | Purpose |
|------|---------|
| `coder_connections.json` | Coder backend connection configurations |
| `coder_roles.json` | Role definitions for coder invocation |
| `role_policies.json` | Role-based policies for workflow execution |

Registry files are consulted during workflow loading to resolve coder
configurations and role policies.