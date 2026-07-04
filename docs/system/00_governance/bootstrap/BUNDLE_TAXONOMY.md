---
template_id: "SYS-00-BT"
title: "Bundle Taxonomy"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the taxonomy for workflow bundles in agent-runner-v2. It establishes the classification system for workflows, artifacts, and their relationships, enabling consistent organization and navigation across the platform.

## Audience Model

| Audience | Concern | Primary Sections |
|----------|---------|------------------|
| **Workflow Authors** | How do I structure a new workflow? | Workflow Families, Artifact Classification |
| **Integrators** | How do I reference and extend bundles? | Bundle Structure, Reference Patterns |
| **Operators** | How do I deploy and manage bundles? | Runtime Source of Truth, Versioning |
| **Platform Maintainers** | How do I evolve the taxonomy? | Taxonomy Versioning, Migration |

## Bundle Structure

A workflow bundle is a directory containing:

```
<workflow_root>/<workflow_name>/
├── template_groups.py      # Workflow definitions and step configurations
├── prompts/                # Prompt template directory
│   └── <step_name>/
│       ├── <step_file>.txt # Primary prompt template
│       └── *.txt           # Additional templates
├── *.json                  # Schema and configuration files
└── assets/                 # Workflow-specific assets (optional)
```

## Workflow Families

Workflows are organized into families based on their purpose and lifecycle phase:

| Family ID | Prefix | Steps | Purpose |
|-----------|--------|-------|---------|
| `00_master_docs_bootstrap_v1` | 00DOC | 10 | Master documentation bootstrap |
| `10_execution_scaffold_v1` | EXSC | 13 | Delivery scaffold generation |
| `20_initiative_intake_v1` | INIT | 5 | Initiative intake and refinement |
| `21_bug_fix_intake_v1` | BUG | 7 | Bug fix workflow |
| `30_delivery_planning_v1` | PLAN | 10 | Plan and task graph generation |
| `31_task_execution_v1` | TASK | 12 | Task implementation and validation |
| `40_documentation_sync_v1` | SYNC | 2 | Documentation reconciliation |
| `50_architecture_site_v1` | SITE | 2 | Architecture site publishing |
| `image_csv_gen_v2` | IMG | 3 | Image CSV generation |
| `videoxpress_gen_v1` | VID | 9 | Video generation pipeline |
| `tiktok_video_pipeline_v1` | TTOK | 10 | TikTok video workflow |

### Family Naming Convention

```
[<priority_prefix>][<name>]_v<version>
```

- **Priority prefix**: Two-digit number indicating bootstrap/execution order (00-99)
- **Name**: Lowercase, descriptive, underscore-separated
- **Version**: Integer version for compatibility tracking

## Artifact Classification

Artifacts are classified by their role in the delivery lifecycle:

### Initiative Artifacts

| Artifact Key | File Pattern | Phase | Description |
|--------------|--------------|-------|-------------|
| `DRAFT_INIT_FILE` | `DRAFT-*.md` | Intake | Initial draft requirements |
| `PRE_INIT_FILE` | `PRE-INIT-*.md` | Intake | Pre-approval refinement |
| `INIT_FILE` | `INIT-*.md` | Intake | Approved initiative specification |

### Planning Artifacts

| Artifact Key | File Pattern | Phase | Description |
|--------------|--------------|-------|-------------|
| `PLAN_FILE` | `PLAN-*.md` | Planning | Implementation plan |
| `TASK_GRAPH_FILE` | `TASK-GRAPH-*.json` | Planning | Task dependency graph |
| `TASK_FILE` | `TASK-*.md` | Planning | Individual task specification |

### Execution Artifacts

| Artifact Key | File Pattern | Phase | Description |
|--------------|--------------|-------|-------------|
| `IMPL_FILE` | `IMPL-*.md` | Execution | Implementation specification |
| `REVIEW_FILE` | `REVIEW-*.md` | Execution | Code review output |
| `VALIDATION_FILE` | `VALIDATION-*.md` | Execution | Validation results |

### Codebase Documentation Artifacts

| Artifact Key | File Pattern | Phase | Description |
|--------------|--------------|-------|-------------|
| `CODEBASE_INVENTORY` | `codebase_inventory.md` | Bootstrap | Module inventory |
| `CODEBASE_CHANGE_IMPACT` | `*-change.md` | Sync | Change impact analysis |
| `CODEBASE_SCAN_SNAPSHOT` | `*-snapshot.json` | Sync | Repository scan results |

### System Documentation Artifacts

| Artifact Key | File Pattern | Phase | Description |
|--------------|--------------|-------|-------------|
| `SYSTEM_OVERVIEW` | `SYSTEM_OVERVIEW.md` | Bootstrap | System overview |
| `FUNCTIONAL_SPEC` | `FUNCTIONAL_SPEC.md` | Bootstrap | Functional specification |
| `COMPONENT_ARCHITECTURE` | `COMPONENT_ARCHITECTURE.md` | Bootstrap | Architecture documentation |
| `DECISION_LOG` | `DECISION_LOG.md` | Bootstrap | Decision records |

### Scaffold Artifacts

| Artifact Key | File Pattern | Phase | Description |
|--------------|--------------|-------|-------------|
| `PROJECT_ANALYSIS` | `project_analysis.md` | Scaffold | Project analysis |
| `DELIVERY_SOP` | `DELIVERY_SOP_*.md` | Scaffold | Delivery SOP |
| `DELIVERY_AGENTS_MD` | `AGENTS.md` | Scaffold | Agent contracts |
| `DELIVERY_STATUS_RULES` | `DELIVERY_STATUS_RULES_*.md` | Scaffold | Status rules |

## Step Classification

Steps are classified by their execution type:

| Step Type | Description | Example |
|-----------|-------------|---------|
| `scan` | Repository analysis | `00_scan_repo_codebase` |
| `generate` | Document generation | `02_generate_project_analysis` |
| `review` | Human review checkpoint | `05_review_master_system_docs` |
| `refine` | Iterative refinement | `06_refine_master_system_docs` |
| `validate` | Validation and verification | `08_validate_master_system_docs` |
| `finalize` | Completion and cleanup | `09_finalize_bootstrap` |

### Step Naming Convention

```
[<priority>]_<action>_<target>
```

- **Priority**: Two-digit number for ordering within workflow
- **Action**: Verb describing the step's primary action
- **Target**: Noun describing what the step operates on

## Runtime Source of Truth

The platform maintains two sources of workflow definitions:

| Source | Location | Purpose | Update Mechanism |
|--------|----------|---------|------------------|
| **Packaged Bootstrap** | `agent_runner_v2/bootstrap/workflows/default/` | Repository distribution | Git commit |
| **Runtime Bundle** | `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\` | Active execution | `ukbe-run-agent init` |

### Initialization Flow

1. User runs `ukbe-run-agent init`
2. Bootstrap copies workflow files from package to runtime home
3. Runtime loads workflows from runtime home, not package
4. Updates to bootstrap require re-initialization to propagate

### Versioning Strategy

| Component | Version Location | Compatibility |
|-----------|------------------|---------------|
| Job schema | `job_schema.json` | Required for state loading |
| LLM response | `llm_response_schema.json` | Required for coder output |
| Template groups | `template_groups.py` | Workflow definitions |
| Prompt templates | `prompts/` directory | Step-specific inputs |

## Reference Patterns

### Cross-Workflow References

```python
# Reference another workflow's artifact
"reference_files": {
    "OTHER_WORKFLOW_ARTIFACT": "path/to/artifact.md"
}
```

### Artifact Path Resolution

```python
# Runtime context resolves paths
from agent_runner_v2.runtime_context import get_delivery_root
from agent_runner_v2.doc_paths import delivery_doc_rel

# Absolute path to delivery artifact
delivery_path = get_delivery_root() / "01_initiatives" / "INIT-001.md"

# Relative path from repo root
rel_path = delivery_doc_rel("01_initiatives/INIT-001.md")
```

## Taxonomy Versioning

The bundle taxonomy is versioned independently from the platform:

| Taxonomy Version | Platform Compatibility | Changes |
|------------------|------------------------|---------|
| 1.0 | agent-runner-v2 >= 0.1.0 | Initial taxonomy |

### Taxonomy Extension Rules

1. **New artifact keys**: Add to `ARTIFACT_KEYS` list
2. **New workflow families**: Add to `TEMPLATE_GROUPS` dictionary
3. **New step types**: Follow naming convention, document in taxonomy
4. **Breaking changes**: Require taxonomy version bump

---

*This taxonomy defines the structure for all workflow bundles in agent-runner-v2. Extensions should follow established patterns and update this document.*
