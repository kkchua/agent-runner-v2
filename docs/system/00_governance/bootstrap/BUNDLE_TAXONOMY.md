---
template_id: "SYS-00-BT"
managed_by: workflow-generated
generated: "2026-07-09T21:18:02+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the taxonomy and organization of workflow bundles in agent-runner-v2. It describes the structure of bootstrap bundles, runtime bundles, and the relationship between them.

The bundle taxonomy serves as the reference for understanding where workflow definitions live, how they are organized, and how changes propagate from bootstrap source to runtime execution.

## Audience Model

| Audience | Concerns | How This Document Helps |
|----------|----------|----------------------|
| **System Maintainers** | Bundle structure, versioning, migration | Understanding taxonomy and organization |
| **Workflow Authors** | Where to place new workflows, naming conventions | Bundle structure and conventions |
| **Operators** | Runtime bundle location, troubleshooting | Runtime bundle paths and sync procedures |
| **Developers** | Bootstrap vs runtime distinction | Clear separation of concerns |

## Bundle Structure

### Bootstrap Bundle

The bootstrap bundle is the package-local source of workflow definitions and templates.

**Location:** `agent_runner_v2/bootstrap/`

**Structure:**

```
agent_runner_v2/bootstrap/
├── workflows/
│   └── default/
│       ├── template_groups.py          # Workflow family definitions
│       ├── job_schema.json             # Job state schema
│       ├── llm_response_schema.json    # LLM response schema
│       ├── model_mapping.json          # Model name mappings
│       └── prompts/                    # Workflow step prompts
│           ├── 00_master_docs_bootstrap_v1/
│           ├── 10_execution_scaffold_v1/
│           ├── 20_initiative_intake_v1/
│           ├── 21_bug_fix_intake_v1/
│           ├── 30_delivery_planning_v1/
│           ├── 31_task_execution_v1/
│           ├── 40_documentation_sync_v1/
│           ├── 41_audience_doc_v1/
│           └── ...
├── bundles/
│   └── core/
│       └── current/                    # Core system documentation bundle
│           ├── README.md
│           ├── SYSTEM_OVERVIEW.md
│           ├── FUNCTIONAL_SPEC.md
│           ├── templates/              # Document templates
│           │   ├── delivery/
│           │   └── codebase/
│           └── ...
└── themes/
    └── default/                        # Architecture site themes
        ├── layout.html
        ├── styles.css
        └── ...
```

### Runtime Bundle

The runtime bundle is the active execution source loaded during workflow execution.

**Location:** `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`

**Structure:**

```
%USERPROFILE%\.ukbe-runner\workflows\default/
├── template_groups.py          # Copied from bootstrap
├── job_schema.json             # Copied from bootstrap
├── llm_response_schema.json    # Copied from bootstrap
├── model_mapping.json          # Copied from bootstrap
└── prompts/                    # Copied from bootstrap
    └── ...
```

### Critical Distinction

| Aspect | Bootstrap Source | Runtime Bundle |
|--------|-----------------|----------------|
| **Purpose** | Package-local seed/template | Active execution source |
| **Location** | `agent_runner_v2/bootstrap/...` | `%USERPROFILE%\.ukbe-runner\workflows\...` |
| **Updates** | Via code changes | Used by running workflows |
| **Loading** | `bundle_loader.py` | `runtime_context.py` |
| **Persistence** | Version controlled | Global user directory |

**Critical Rule:** Changes to bootstrap workflow files must be synced to the global runner home before they take effect in prompts.

## Workflow Families

### Core Workflow Families

| Workflow Family | ID Pattern | Purpose |
|-----------------|------------|---------|
| **Master Docs Bootstrap** | `00_master_docs_bootstrap_v1` | Generate core system documentation |
| **Execution Scaffold** | `10_execution_scaffold_v1` | Scaffold delivery and codebase governance |
| **Initiative Intake** | `20_initiative_intake_v1` | Draft and refine initiative intake |
| **Bug Fix Intake** | `21_bug_fix_intake_v1` | Triage and fix bugs |
| **Delivery Planning** | `30_delivery_planning_v1` | Plan generation and task decomposition |
| **Task Execution** | `31_task_execution_v1` | Implement and validate tasks |
| **Documentation Sync** | `40_documentation_sync_v1` | Reconcile documentation with codebase |
| **Audience Documentation** | `41_audience_doc_v1` | Generate audience-specific docs |
| **Architecture Site** | `50_architecture_site_v1` | Publish browsable HTML architecture |
| **Developer Documentation** | `51_developer_doc_v1` | Generate developer-facing docs |
| **Operator Documentation** | `52_operator_doc_v1` | Generate operator-facing docs |
| **User Documentation** | `55_user_docs_v1` | Generate end-user docs |

### Workflow Naming Convention

| Element | Convention | Example |
|---------|------------|---------|
| **Family ID** | `{prefix}_{descriptive_name}_v{version}` | `30_delivery_planning_v1` |
| **Step ID** | `{zero_padded_step}_{step_name}` | `02_generate_project_analysis` |
| **Prompt File** | `{step_number}_{step_name}.txt` | `02_generate_project_analysis.txt` |

## Core Bundle Contents

### System Documentation

The core bundle contains the complete system documentation set:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| README.md | SYS-00-IDX | Documentation index |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Documentation conventions |
| BUNDLE_TAXONOMY.md | SYS-00-BT | This document — bundle organization |
| BUNDLE_MIGRATION_PLAN.md | SYS-00-BMP | Migration procedures |
| SYSTEM_OVERVIEW.md | SYS-00-SO | Platform overview |
| BUSINESS_CAPABILITIES.md | SYS-00-BC | Operational capabilities |
| FUNCTIONAL_SPEC.md | SYS-00-FS | System behaviors |
| NON_FUNCTIONAL_REQUIREMENTS.md | SYS-00-NFR | Quality expectations |
| SYSTEM_CONTEXT.md | SYS-00-SC | System context |
| COMPONENT_ARCHITECTURE.md | SYS-00-CA | Component structure |
| DECISION_LOG.md | SYS-00-DL | Architectural decisions |
| SYSTEM_FILE_STRUCTURE.md | SYS-00-SFS | File organization |
| DEVELOPER_GUIDE.md | SYS-00-DG | Development procedures |
| RUNBOOK.md | SYS-00-RB | Operational procedures |
| EXISTING_REPO_WORKFLOW_SOP.md | SYS-00-SOP | Workflow SOP |
| PROJECT_ANALYSIS.md | SYS-00-PA | Project analysis |

### Template Registry

The core bundle includes document templates for delivery and codebase documentation:

**Delivery Templates:**
- Delivery template registry
- Initiative template
- Plan template
- Task graph template
- Task template
- Implementation template
- Review template
- Validation template
- Memory template

**Codebase Templates:**
- Codebase template registry
- Inventory template
- Module template
- Component template
- Change template

### Agent Contracts

The core bundle includes agent contract documentation:

- AGENTS.md — Master agent index
- AGENT-PLANNER.md — Planning agent
- AGENT-EXECUTOR.md — Execution agent
- AGENT-REVIEWER.md — Review agent
- AGENT-IMPL-PLANNER.md — Implementation planner
- AGENT-TASK-DECOMPOSER.md — Task decomposer
- AGENT-MEMORY-MANAGER.md — Memory manager

## Synchronization

### Sync Procedures

Changes to bootstrap files must be synchronized to the runtime bundle:

| Change Type | Sync Method | Command |
|-------------|-------------|---------|
| Workflow prompts | Manual sync | `sync-workflows-to-backend.bat` |
| Template groups | Manual sync | `sync-10_execution_scaffold_v1-workflow-spec.bat` |
| Core bundle | Init command | `ukbe-run-agent init` (re-seeds) |

### Sync Validation

After synchronization:

1. Verify runtime bundle matches bootstrap source
2. Check prompt templates are updated
3. Validate template_groups.py changes
4. Confirm schema files are current

### Sync Failure Handling

| Failure | Action |
|---------|--------|
| Partial sync | Re-run sync command |
| Version mismatch | Check bundle versions, re-initialize if needed |
| File permission | Check user directory permissions |
| Path resolution | Verify RUNNER_ROOT environment |

## Versioning

### Bundle Versions

Bundles are versioned through:

| Mechanism | Description |
|-----------|-------------|
| **Git commit** | Bootstrap source version controlled |
| **Change ID** | Generated documents tagged with change ID |
| **Template version** | Workflow family version in ID |

### Version Compatibility

| Bootstrap Version | Runtime Version | Compatibility |
|-------------------|-----------------|---------------|
| Same | Same | Full compatibility |
| Newer | Older | May have new features not available |
| Older | Newer | Backward compatible if schema unchanged |

## Extension Points

### Custom Workflows

New workflow families can be added:

1. Create workflow directory in `bootstrap/workflows/default/prompts/`
2. Define in `template_groups.py`
3. Sync to runtime bundle
4. Test with local execution

### Custom Templates

Repository-specific templates:

1. Add to `bootstrap/bundles/core/current/templates/`
2. Update template registry
3. Reference via artifact keys

### Custom Themes

Architecture site themes:

1. Add to `bootstrap/themes/`
2. Reference in workflow config
3. Validate HTML output

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 03_generate_system_overview_docs*
