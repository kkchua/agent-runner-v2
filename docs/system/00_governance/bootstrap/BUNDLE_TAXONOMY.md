---
template_id: "SYS-00-BT"
title: "Bundle Taxonomy - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the canonical organization for runtime workflow bundles in agent-runner-v2. It establishes how workflows, prompts, and configuration are structured within the global runner home (`%USERPROFILE%\.ukbe-runner`).

**Why:** A consistent bundle taxonomy enables the runner to locate and load workflow definitions reliably, supports multiple workflow families, and allows for domain-specific customization without code changes.

## Scope

This taxonomy applies to:

- Packaged bootstrap bundles in `agent_runner_v2/bootstrap/workflows/`
- Runtime bundles in `%USERPROFILE%\.ukbe-runner\workflows\`
- Custom workflow bundles created by users

## Bundle Structure

### Core Bundle (`core`)

The core bundle contains system documentation required for all repositories:

```
bundles/core/
├── README.md                           # SYS-00-IDX
├── DOCUMENTATION_STANDARD.md           # SYS-00-DS
├── BUNDLE_TAXONOMY.md                  # SYS-00-BT
├── BUNDLE_MIGRATION_PLAN.md            # SYS-00-BMP
├── SYSTEM_OVERVIEW.md                  # SYS-00-SO
├── BUSINESS_CAPABILITIES.md            # SYS-00-BC
├── FUNCTIONAL_SPEC.md                  # SYS-00-FS
├── NON_FUNCTIONAL_REQUIREMENTS.md      # SYS-00-NFR
├── SYSTEM_CONTEXT.md                   # SYS-00-SC
├── COMPONENT_ARCHITECTURE.md           # SYS-00-CA
├── DECISION_LOG.md                     # SYS-00-DL
├── SYSTEM_FILE_STRUCTURE.md            # SYS-00-SFS
├── DEVELOPER_GUIDE.md                  # SYS-00-DG
├── RUNBOOK.md                          # SYS-00-RB
└── EXISTING_REPO_WORKFLOW_SOP.md       # SYS-00-SOP
```

### Workflow Bundle (`default`)

Workflow bundles contain executable workflow definitions:

```
workflows/<workflow_name>/
├── template_groups.py                  # Workflow definitions
├── job_schema.json                     # Job state schema
├── llm_response_schema.json            # LLM response schema
├── model_mapping.json                  # Coder model mapping
├── usage_schema.json                   # Usage tracking schema
└── prompts/
    ├── <workflow_family_1>/
    │   ├── 01_step_name.txt
    │   ├── 02_step_name.txt
    │   └── ...
    └── <workflow_family_2>/
        └── ...
```

### Domain Bundles

Domain bundles contain documentation for specific technical domains:

```
bundles/<domain>/
├── overview.md
├── standards.md
├── patterns/
└── reference/
```

**Supported Domains:**
- `frontend` — Frontend development documentation
- `backend` — Backend service documentation
- `content` — Content management documentation
- `data` — Data pipeline documentation
- `platform` — Platform infrastructure documentation

## Bundle Profiles

### Profile: `core+workflow` (Default)

The default profile includes:
- Core system documentation
- Workflow definitions and prompts
- Default domain bundle

### Profile Selection

Profiles are selected at initialization or via configuration:

```json
{
  "bundle_profile": "core+workflow",
  "domain_bundle": "general",
  "workflow_name": "default"
}
```

## Artifact Keys

Workflow bundles define artifact keys used to reference files:

### Delivery Workflow Artifacts

| Key | Description | Typical Location |
|-----|-------------|------------------|
| `DRAFT_INIT_FILE` | Draft initiative | `docs/delivery/01_initiatives/draft/` |
| `PRE_INIT_FILE` | Pre-refined initiative | `docs/delivery/01_initiatives/pre_init/` |
| `INIT_FILE` | Approved initiative | `docs/delivery/01_initiatives/` |
| `PLAN_FILE` | Delivery plan | `docs/delivery/02_plans/` |
| `TASK_GRAPH_FILE` | Task decomposition | `docs/delivery/03_task_graphs/` |
| `TASK_FILE` | Task contract | `docs/delivery/04_tasks/` |
| `IMPL_FILE` | Implementation plan | `docs/delivery/05_impl/` |
| `REVIEW_FILE` | Review findings | `docs/delivery/06_reviews/` |
| `VALIDATION_FILE` | Validation results | `docs/delivery/07_validations/` |

### System Documentation Artifacts

| Key | Description | Location |
|-----|-------------|----------|
| `SYSTEM_DOCS_INDEX` | Documentation index | `docs/system/00_governance/bootstrap/` |
| `SYSTEM_DOC_STANDARD` | Documentation standard | `docs/system/00_governance/bootstrap/` |
| `BUNDLE_TAXONOMY` | Bundle taxonomy | `docs/system/00_governance/bootstrap/` |
| `SYSTEM_OVERVIEW` | System overview | `docs/system/00_governance/bootstrap/` |
| `CODEBASE_INVENTORY` | Codebase inventory | `docs/codebase/01_inventory/` |

### Content Pipeline Artifacts

| Key | Description | Typical Location |
|-----|-------------|------------------|
| `NARRATIVE_FILE` | Video narrative | Workflow-specific |
| `VIDEOWORKFLOW_FILE` | Video workflow definition | Workflow-specific |
| `GENERATED_IMAGES_FOLDER` | Image output folder | Delivery root |
| `GENERATED_VIDEO_CLIPS` | Video clip folder | Delivery root |
| `FINAL_VIDEO_FILE` | Final composed video | Delivery root |

## Bundle Manifest

The bundle manifest (`bundle-set.json`) records the active bundle selection:

```json
{
  "schema_version": "v1",
  "selection": {
    "profile": "core+workflow",
    "domain": "general",
    "workflow_name": "default",
    "core_bundle": "core",
    "domain_bundle": "general"
  },
  "taxonomy": {
    "core_bundle_docs": [...],
    "domain_bundle_names": [...],
    "workflow_bundle_docs": [...],
    "domain_docs": {...}
  }
}
```

## Runtime Resolution

### Path Resolution Order

The runner resolves paths in this order:

1. **Project root** — Repository-relative paths
2. **Runner home** — `%USERPROFILE%\.ukbe-runner\`
3. **Package root** — `agent_runner_v2/` package

### Workflow Loading

Workflows are loaded from the runtime bundle:

1. Load `template_groups.py` from runtime bundle
2. Resolve workflow family by name
3. Load prompt templates from `prompts/<family>/`
4. Validate against schemas

### Configuration Precedence

Configuration values are resolved in this order (highest to lowest):

1. Command-line `--set` arguments
2. Environment variables
3. Project config (`config.json`)
4. Runner home config
5. Package defaults

## Versioning

Bundle format versions:

| Version | Status | Description |
|---------|--------|-------------|
| v1 | Current | Initial bundle taxonomy |

See [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) for migration history.

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
