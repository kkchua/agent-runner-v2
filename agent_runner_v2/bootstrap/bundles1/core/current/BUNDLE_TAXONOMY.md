---
template_id: "SYS-00-BT"
title: "Bundle Taxonomy - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the taxonomy and organization of workflow bundles in the `agent-runner-v2` system. It establishes naming conventions, directory structures, and the relationships between packaged bootstrap source and runtime workflow bundles.

## Bundle Overview

### Two-Source Model

The system maintains two distinct sources of workflow definitions:

1. **Packaged Bootstrap Source**: Located in the repository at `agent_runner_v2/bootstrap/`
2. **Runtime Workflow Bundle**: Located in the user's home at `%USERPROFILE%\.ukbe-runner\workflows\`

### Source of Truth

Runtime prompt/templates are loaded from the global runner home, not from the repo tree directly. The repo bootstrap files seed those runtime bundles during initialization.

## Bundle Structure

### Bootstrap Bundle Layout

```
agent_runner_v2/bootstrap/
├── bundles/core/current/           # Core documentation templates
│   ├── README.md
│   ├── PROJECT_ANALYSIS.md
│   ├── SYSTEM_OVERVIEW.md
│   ├── ... (18 master documents)
│   └── templates/                  # Workflow templates
│       ├── delivery/
│       │   ├── 01_delivery_template_registry.md
│       │   ├── 02_delivery_initiative_template.md
│       │   └── ...
│       └── codebase/
│           ├── 01_codebase_template_registry.md
│           └── ...
├── workflows/default/              # Default workflow definitions
│   ├── template_groups.py          # Workflow family definitions
│   ├── job_schema.json             # Job state schema
│   ├── llm_response_schema.json    # LLM response schema
│   ├── model_mapping.json          # Model alias mappings
│   └── prompts/                    # Workflow step prompts
│       ├── 00_master_docs_bootstrap_v1/
│       ├── 10_execution_scaffold_v1/
│       ├── 20_initiative_intake_v1/
│       ├── 21_bug_fix_intake_v1/
│       ├── 30_delivery_planning_v1/
│       ├── 31_task_execution_v1/
│       ├── 40_documentation_sync_v1/
│       ├── 41_audience_doc_v1/
│       └── 50_architecture_site_v1/
└── themes/default/                 # HTML theme templates
    ├── layout.html
    └── ...
```

### Runtime Bundle Layout

```
%USERPROFILE%\.ukbe-runner/
├── config.json                     # Runner configuration
├── jobs/                           # Job state storage
│   └── <workflow>/<job_id>/
│       ├── job.json
│       └── <step>/
│           ├── meta.json
│           └── ...
├── workflows/                      # Runtime workflow bundles
│   ├── example/
│   │   ├── template_groups.py
│   │   └── prompts/
│   └── <custom-workflow>/
│       ├── template_groups.py
│       └── prompts/
└── logs/                           # Execution logs
```

## Workflow Families

### Supported Workflow Families

| Workflow Family | Steps | Purpose | Entry Point |
|----------------|-------|---------|-------------|
| `00_master_docs_bootstrap_v1` | 13 | Generate master system documentation | Manual/bootstrap |
| `10_execution_scaffold_v1` | 13 | Delivery scaffold SOP and templates | Manual/scaffold |
| `20_initiative_intake_v1` | 5 | Initiative intake and pre-init refinement | `ukbe-run-agent run` |
| `21_bug_fix_intake_v1` | 7 | Bug triage, reproduction, patching | `ukbe-run-agent run` |
| `30_delivery_planning_v1` | 10 | Plan generation, task-graph generation | `ukbe-run-agent run` |
| `31_task_execution_v1` | 12 | Implementation planning, execution, validation | `ukbe-run-agent run` |
| `40_documentation_sync_v1` | 5 | Documentation reconciliation and validation | `ukbe-run-agent run` |
| `41_audience_doc_v1` | 4 | Audience-specific documentation (5 audiences) | `ukbe-run-agent run` |
| `50_architecture_site_v1` | 2 | Architecture site generation | `ukbe-run-agent run` |

### Workflow Family Taxonomy

Workflow families are organized by function:

```
Workflow Families
├── Bootstrap (00_*)
│   └── 00_master_docs_bootstrap_v1
├── Scaffold (10_*)
│   └── 10_execution_scaffold_v1
├── Intake (20_*)
│   ├── 20_initiative_intake_v1
│   └── 21_bug_fix_intake_v1
├── Planning (30_*)
│   ├── 30_delivery_planning_v1
│   └── 31_task_execution_v1
├── Sync (40_*)
│   ├── 40_documentation_sync_v1
│   └── 41_audience_doc_v1
└── Publish (50_*)
    └── 50_architecture_site_v1
```

## Artifact Taxonomy

### Artifact Key Conventions

Artifact keys follow these naming conventions:

| Pattern | Example | Purpose |
|---------|---------|---------|
| `*_FILE` | `INIT_FILE`, `PLAN_FILE` | Single-file artifacts |
| `*_FOLDER` | `IMAGE_FOLDER` | Directory artifacts |
| `*_TEMPLATE` | `DELIVERY_PLAN_TEMPLATE` | Template artifacts |
| `*_SOP` | `DELIVERY_SOP` | Standard operating procedure |
| `AGENT_*` | `AGENT_PLANNER` | Agent contract documents |

### Artifact Categories

```
Artifacts
├── Delivery Workflow
│   ├── DRAFT_INIT_FILE
│   ├── PRE_INIT_FILE
│   ├── INIT_FILE
│   ├── PLAN_FILE
│   ├── TASK_GRAPH_FILE
│   ├── TASK_FILE
│   ├── IMPL_FILE
│   ├── REVIEW_FILE
│   └── VALIDATION_FILE
├── Scaffold/Governance
│   ├── PROJECT_ANALYSIS
│   ├── DELIVERY_SOP
│   ├── DELIVERY_STATUS_RULES
│   ├── DELIVERY_TEMPLATE_REGISTRY
│   └── DELIVERY_AGENTS
├── Codebase Documentation
│   ├── CODEBASE_DOC_SOP
│   ├── CODEBASE_DOC_STATUS_RULES
│   ├── CODEBASE_TEMPLATE_REGISTRY
│   └── CODEBASE_INVENTORY
└── System Documentation
    ├── SYSTEM_OVERVIEW
    ├── BUSINESS_CAPABILITIES
    ├── FUNCTIONAL_SPEC
    └── NON_FUNCTIONAL_REQUIREMENTS
```

## Bundle Versioning

### Versioning Scheme

Bundles are versioned using:

- **Semantic Versioning**: For released bundles
- **Change IDs**: For generated bundles (e.g., `00DOC-20260708-78fb419e`)
- **Git Commits**: For bootstrap source tracking

### Migration Strategy

See [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) for detailed migration procedures.

## Naming Conventions

### File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Workflow prompt | `{step_number}_{step_name}.txt` | `02_generate_project_analysis.txt` |
| Template registry | `01_{scope}_template_registry.md` | `01_delivery_template_registry.md` |
| Change document | `00DOC-{YYYYMMDD}-{hash}-{type}.md` | `00DOC-20260708-78fb419e-bootstrap.md` |
| Validation document | `00DOC-{id}-validation.md` | `00DOC-20260708-78fb419e-validation.md` |

### Directory Naming

| Type | Pattern | Example |
|------|---------|---------|
| Workflow family | `{number}_{name}_v{version}` | `00_master_docs_bootstrap_v1` |
| Job directory | `{workflow}/{job_id}` | `delivery_planning_v1/PLAN-20260708-001` |
| Step directory | `{step_number}_{step_name}` | `02_generate_project_analysis` |

## Bundle Operations

### Initialization

```bash
ukbe-run-agent init
```

Seeds the global runner home with default workflows from the packaged bootstrap source.

### Publishing

```bash
ukbe-run-agent publish-bundle
```

Publishes the current bootstrap bundle to the runtime location.

### Validation

Bundle validation ensures:

- All required files are present
- JSON schemas are valid
- Prompt templates are complete
- Cross-references resolve

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
