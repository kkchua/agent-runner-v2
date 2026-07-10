---
template_id: "SYS-00-BT"
title: "Bundle Taxonomy"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the taxonomy of documentation bundles in the `agent-runner-v2` repository. It classifies:

1. **Bundle types** and their contents
2. **Bundle relationships** and dependencies
3. **Bundle lifecycle** from creation to archival

## Audience

| Role | Use Case |
|------|----------|
| **Developers** | Understanding what documentation artifacts exist and where |
| **Operators** | Locating specific documentation bundles for maintenance |
| **Workflow authors** | Understanding bundle structure for workflow development |

## Bundle Types

### Core Bundles

Core bundles contain the fundamental documentation for the repository.

#### System Documentation Bundle

**Location**: `docs/system/00_governance/bootstrap/`

**Contents**:
- README.md — System documentation index
- DOCUMENTATION_STANDARD.md — Documentation standards
- BUNDLE_TAXONOMY.md — This document
- BUNDLE_MIGRATION_PLAN.md — Migration strategy
- SYSTEM_OVERVIEW.md — Platform overview
- BUSINESS_CAPABILITIES.md — Operational capabilities
- FUNCTIONAL_SPEC.md — Functional specification
- NON_FUNCTIONAL_REQUIREMENTS.md — Quality expectations
- SYSTEM_CONTEXT.md — External boundaries
- COMPONENT_ARCHITECTURE.md — Component breakdown
- DECISION_LOG.md — Design decisions
- SYSTEM_FILE_STRUCTURE.md — Repository organization
- DEVELOPER_GUIDE.md — Development setup
- RUNBOOK.md — Operational procedures
- PROJECT_ANALYSIS.md — Repository analysis

**Purpose**: Provides comprehensive understanding of the platform.

**Maintained By**: `00_master_docs_bootstrap_v2` workflow

**Update Frequency**: Per major release or architecture change

#### Codebase Documentation Bundle

**Location**: `docs/codebase/`

**Contents**:
- 01_inventory/codebase_inventory.md — Module inventory
- 02_modules/*.md — Per-module documentation
- 03_components/*.md — Component documentation
- 04_changes/*.md — Change impact documents

**Purpose**: Tracks repository structure and state.

**Maintained By**: `40_documentation_sync_v1` workflow, reconcile scans

**Update Frequency**: Continuous, on code changes

#### Bootstrap Bundle

**Location**: `agent_runner_v2/bootstrap/`

**Contents**:
- bundles/core/current/ — Core documentation bundles (mirrors system docs)
- themes/default/ — HTML theme templates
- workflows/default/ — Default workflow definitions

**Purpose**: Seeds runtime bundles for execution.

**Maintained By**: `00_master_docs_bootstrap_v2` workflow

**Update Frequency**: Per release

### Workflow Bundles

Workflow bundles contain workflow-specific definitions and templates.

#### Workflow Package Bundle

**Location**: `%USERPROFILE%\.ukbe-runner\workflows\<workflow_name>\`

**Contents**:
- workflow.toml — Workflow manifest
- prompts/ — Prompt templates
- context_extensions.py — Context hooks (optional)

**Purpose**: Runtime execution source for workflows.

**Maintained By**: Seeded from bootstrap, then runtime-managed

**Update Frequency**: Per workflow version

#### Workflow Prompt Bundle

**Location**: `agent_runner_v2/bootstrap/workflows/default/prompts/<workflow_name>/`

**Contents**:
- *.txt — Prompt template files

**Purpose**: Bootstrap source for workflow prompts.

**Maintained By**: Workflow authors

**Update Frequency**: Per workflow step change

### Delivery Bundles

Delivery bundles contain initiative and task documentation.

#### Initiative Bundle

**Location**: `docs/delivery/01_initiatives/`

**Contents**:
- DRAFT_*.md — Draft initiatives
- PRE_INIT_*.md — Pre-initiative documents
- INIT_*.md — Approved initiatives

**Purpose**: Captures planned and in-flight work.

**Maintained By**: `20_initiative_intake_v1` workflow

**Update Frequency**: Per initiative

#### Plan Bundle

**Location**: `docs/delivery/03_plans/`

**Contents**:
- PLAN_*.md — Delivery plans

**Purpose**: Documents delivery approach for initiatives.

**Maintained By**: `30_delivery_planning_v1` workflow

**Update Frequency**: Per planning cycle

#### Task Bundle

**Location**: `docs/delivery/04_tasks/`

**Contents**:
- TASK_*.md — Task definitions

**Purpose**: Defines implementation tasks.

**Maintained By**: `30_delivery_planning_v1` workflow

**Update Frequency**: Per task creation

#### Implementation Bundle

**Location**: `docs/delivery/05_implementations/`

**Contents**:
- IMPL_*.md — Implementation records

**Purpose**: Documents implementation execution.

**Maintained By**: `31_task_execution_v1` workflow

**Update Frequency**: Per task execution

#### Review Bundle

**Location**: `docs/delivery/06_reviews/`

**Contents**:
- REVIEW_*.md — Review outcomes

**Purpose**: Captures review decisions.

**Maintained By**: `31_task_execution_v1` workflow

**Update Frequency**: Per review

### Template Bundles

Template bundles contain reusable document templates.

#### Delivery Template Bundle

**Location**: `docs/delivery/00_templates/`

**Contents**:
- 01_delivery_template_registry.md
- 02_delivery_initiative_template.md
- 03_delivery_plan_template.md
- 04_delivery_task_graph_template.md
- 05_delivery_task_template.md
- 06_delivery_impl_template.md
- 07_delivery_review_template.md
- 08_delivery_validation_template.md
- 09_delivery_memory_template.md

**Purpose**: Standardizes delivery document format.

**Maintained By**: `10_execution_scaffold_v1` workflow

**Update Frequency**: Per template revision

#### Codebase Template Bundle

**Location**: `docs/codebase/00_templates/`

**Contents**:
- 01_codebase_template_registry.md
- 02_codebase_inventory_template.md
- 03_codebase_module_template.md
- 04_codebase_component_template.md
- 05_codebase_change_template.md

**Purpose**: Standardizes codebase document format.

**Maintained By**: `10_execution_scaffold_v1` workflow

**Update Frequency**: Per template revision

## Bundle Relationships

### Dependency Graph

```
Bootstrap Bundle
├── System Documentation Bundle (seeds)
├── Workflow Prompt Bundle (seeds)
└── Workflow Package Bundle (seeds runtime)

System Documentation Bundle
├── Codebase Documentation Bundle (references)
└── Delivery Bundles (references)

Delivery Bundles
├── Template Bundles (uses)
└── Bootstrap Bundle (runtime)
```

### Inheritance

| Source Bundle | Target Bundle | Relationship |
|-------------|---------------|--------------|
| `agent_runner_v2/bootstrap/bundles/core/current/` | `docs/system/00_governance/bootstrap/` | Mirror / sync target |
| `agent_runner_v2/bootstrap/workflows/default/` | `~/.ukbe-runner/workflows/` | Runtime seed |
| Template bundles | Delivery bundles | Format standard |

## Bundle Lifecycle

### Creation

| Bundle Type | Creation Trigger | Creator |
|-------------|------------------|---------|
| Core bundles | Repository bootstrap | `00_master_docs_bootstrap_v2` |
| Workflow bundles | Workflow definition | Workflow author |
| Delivery bundles | Initiative/plan/task | Respective workflow |
| Template bundles | Scaffold generation | `10_execution_scaffold_v1` |

### Activation

Bundles become active when:

1. **Core bundles**: Workflow completes successfully
2. **Workflow bundles**: Seeded to runtime path
3. **Delivery bundles**: Workflow step produces artifacts
4. **Template bundles**: Scaffold workflow completes

### Maintenance

| Bundle Type | Maintenance Workflow | Frequency |
|-------------|---------------------|-----------|
| System docs | `00_master_docs_bootstrap_v2` | Per major change |
| Codebase docs | `40_documentation_sync_v1` | Continuous |
| Delivery docs | Respective workflow | Per execution |
| Templates | `10_execution_scaffold_v1` | Per revision |

### Archival

Bundles may be archived when:

1. Superseded by newer versions
2. Associated initiatives complete
3. Workflow versions change

Archival preserves history while indicating obsolescence.

## Bundle Versioning

### Version Strategy

| Bundle Type | Versioning Approach |
|-------------|---------------------|
| System documentation | Change ID + generation timestamp |
| Codebase documentation | Scan timestamp |
| Delivery documents | Document ID + version |
| Templates | Template ID + version |

### Version Indicators

- **Frontmatter**: `change_id`, `generated`, `version`
- **Filename**: Embedded timestamps or version suffixes
- **Directory**: Version-specific subdirectories

## Bundle Validation

### Validation Requirements

| Bundle Type | Validation Rules |
|-------------|------------------|
| System docs | Structure, frontmatter, cross-references |
| Codebase docs | Inventory accuracy, module coverage |
| Delivery docs | Workflow contract compliance |
| Templates | Schema compliance, placeholder completeness |

### Validation Workflow

Validation is performed by:

- `validate_system_docs.py` — System documentation
- `validate_codebase_docs.py` — Codebase documentation
- `validate_delivery_docs.py` — Delivery documentation

## Bundle Metadata

### Required Metadata

All bundles must include:

1. **template_id** — Unique identifier
2. **title** — Human-readable name
3. **status** — active, draft, archived
4. **generated** — Creation timestamp
5. **workflow** — Generating workflow
6. **step** — Generating step
7. **change_id** — Change identifier
8. **managed_by** — workflow-generated or manual

### Optional Metadata

- version — Explicit version number
- author — Document author
- tags — Classification tags
- related — Related document references

---

## Related Documents

- [README.md](README.md) — System documentation index
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Migration strategy
- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository analysis

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
