---
template_id: "SYS-00-BT"
title: "Bundle Taxonomy - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy: agent-runner-v2

## Purpose

This document defines the organization and structure of workflow bundles in the agent-runner-v2 ecosystem. It establishes naming conventions, bundle types, and the relationship between bootstrap source and runtime bundles.

## Scope

This taxonomy covers:
- Workflow bundle types and their purposes
- Bundle directory structure and organization
- Naming conventions for bundles and their contents
- Bootstrap-to-runtime bundle relationships
- Migration path from monolithic to plugin-based bundles

## Bundle Types

### 1. Bootstrap Bundles (Packaged)

Located in: `agent_runner_v2/bootstrap/`

**Purpose**: Seed the global runner home with default workflows, templates, and themes.

| Bundle | Location | Contents |
|--------|----------|----------|
| Core System Docs | `bootstrap/bundles/core/current/` | Master documentation templates |
| Default Workflows | `bootstrap/workflows/default/` | Built-in workflow definitions |
| Default Themes | `bootstrap/themes/default/` | HTML site themes |

**Key characteristic**: Bootstrap bundles are **source only** — they are not loaded directly at runtime. They exist to seed the global runner home via `ukbe-run-agent init`.

### 2. Runtime Bundles (Global)

Located in: `%USERPROFILE%\.ukbe-runner\`

**Purpose**: Active execution environment for workflows.

| Directory | Contents |
|-----------|----------|
| `workflows/<workflow>/` | Workflow definitions and prompts |
| `bundles/core/current/` | System documentation templates |
| `jobs/` | Job state and execution artifacts |
| `logs/` | Execution logs |
| `config.json` | Runner configuration |

**Key characteristic**: Runtime bundles are the **source of truth** for execution. The runner loads workflows from here, not from the repo.

### 3. Plugin Workflow Bundles (Project-Local)

Located in: `<repo>/workflows/<workflow>/`

**Purpose**: Self-contained workflow packages that can be developed and versioned independently.

**Structure**:
```
workflows/<workflow_name>/
├── workflow.toml          # Manifest and step definitions
├── prompts/               # Prompt template files
│   ├── 01_step_name.txt
│   └── 02_another_step.txt
└── context_extensions.py  # Optional context hooks
```

**Key characteristic**: Plugin bundles are converted to the same dict format as legacy `TEMPLATE_GROUPS`, enabling backward compatibility.

## Bundle Directory Structure

### Bootstrap Workflows

```
agent_runner_v2/bootstrap/workflows/default/
├── template_groups.py          # Legacy monolithic workflow definitions
├── job_schema.json             # Job validation schema
├── llm_response_schema.json    # LLM response validation
├── model_mapping.json          # Model alias mappings
└── prompts/
    ├── 00_master_docs_bootstrap_v1/
    │   ├── 02_generate_project_analysis.txt
    │   ├── 03_generate_system_overview_docs.txt
    │   └── ...
    ├── 10_execution_scaffold_v1/
    ├── 20_initiative_intake_v1/
    ├── 21_bug_fix_intake_v1/
    ├── 30_delivery_planning_v1/
    ├── 31_task_execution_v1/
    ├── 40_documentation_sync_v1/
    ├── 41_audience_doc_v1/
    ├── 51_stakeholder_docs_v1/
    ├── 52_developer_docs_v1/
    ├── 53_operator_docs_v1/
    ├── 54_tester_docs_v1/
    ├── 55_user_docs_v1/
    └── ...
```

### Runtime Workflows

```
%USERPROFILE%\.ukbe-runner\workflows\<workflow>\
├── template_groups.py          # Copied from bootstrap or plugin
└── prompts/                    # Copied from bootstrap or plugin
    └── ...
```

### Plugin Workflows

```
<repo>/workflows/<workflow_name>/
├── workflow.toml               # Declarative manifest
├── prompts/                    # Prompt templates
│   └── <step_name>.txt
└── context_extensions.py       # Optional hooks
```

## Naming Conventions

### Workflow Names

Pattern: `<number>_<purpose>_<version>`

| Workflow | Purpose | Version |
|----------|---------|---------|
| `00_master_docs_bootstrap_v1` | Master documentation generation | v1 |
| `10_execution_scaffold_v1` | Delivery scaffold establishment | v1 |
| `20_initiative_intake_v1` | Initiative intake | v1 |
| `21_bug_fix_intake_v1` | Bug fix workflow | v1 |
| `30_delivery_planning_v1` | Delivery planning | v1 |
| `31_task_execution_v1` | Task execution | v1 |
| `40_documentation_sync_v1` | Documentation synchronization | v1 |
| `50_architecture_site_v1` | Architecture site generation | v1 |

### Prompt Files

Pattern: `<step_number>_<step_name>.txt`

Examples:
- `02_generate_project_analysis.txt`
- `03_generate_system_overview_docs.txt`
- `08_impl_task.txt`

### Artifact Keys

Pattern: `ARTIFACT_KEY_<DESCRIPTION>`

Examples:
- `ARTIFACT_KEY_PROJECT_ANALYSIS`
- `ARTIFACT_KEY_DELIVERY_SOP`
- `ARTIFACT_KEY_CODEBASE_INVENTORY`

## Bundle Relationships

### Bootstrap → Runtime Flow

```
Bootstrap Source (repo)
    ↓
ukbe-run-agent init
    ↓
Runtime Global (%USERPROFILE%\.ukbe-runner\)
    ↓
Runtime Execution (ukbe-run-agent run)
```

### Plugin → Runtime Flow

```
Plugin Package (repo/workflows/<name>/)
    ↓
Adapter (workflow_packages/loader.py)
    ↓
Dict Format (same as TEMPLATE_GROUPS)
    ↓
Runtime Execution
```

### Dual-Path Discovery

At runtime, workflow discovery uses global-first, local-fallback:

1. Check `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
2. Fallback to repo `workflows/<workflow>/`

This supports both packaged workflows and project-specific overrides.

## Migration: Monolith to Plugin

### Current State

- Legacy `TEMPLATE_GROUPS` dict in `template_groups.py` (2453+ lines)
- 21+ workflows defined in single file
- Active migration to plugin system on `feat/plugin-workflow-system` branch

### Target State

- Each workflow as self-contained plugin package
- `workflow.toml` declarative manifests
- Independent versioning and testing
- Same execution pipeline via adapter pattern

### Migration Path

1. **Phase 1**: Establish plugin infrastructure (`workflow_packages/`)
2. **Phase 2**: Migrate workflows incrementally
3. **Phase 3**: Deprecate monolithic `TEMPLATE_GROUPS`
4. **Phase 4**: Remove legacy support

## Bundle Validation

### Validation Checks

- Workflow manifest schema compliance
- Prompt file existence
- Artifact key uniqueness
- Cross-reference validity
- Template placeholder correctness

### Validation Artifacts

- `VALIDATION_FILE` — validation results
- `SYSTEM_DOCS_VALIDATION` — system doc validation

## Key Risks

### Bootstrap/Runtime Sync Risk

**Risk**: Changes to bootstrap files may not propagate to runtime bundles.

**Mitigation**: Use `sync_workflows.py` for two-tier discovery; document sync requirements.

### Path Resolution Complexity

**Risk**: Multiple path layers may drift or conflict.

**Mitigation**: Centralized constants in `constants.py`; zero hardcoded paths.

### Plugin Compatibility

**Risk**: Plugin bundles may not match expected schema.

**Mitigation**: Adapter validation; schema enforcement at load time.

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
