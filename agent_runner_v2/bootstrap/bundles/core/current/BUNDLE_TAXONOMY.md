---
title: "Bundle Taxonomy"
template_id: "SYS-00-BT"
status: "active"
generated: "2026-07-10T11:45:32+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-15f76235"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the taxonomy for workflow bundles in the `agent-runner-v2` ecosystem. It establishes naming conventions, directory structures, and versioning rules for workflow definitions, prompt templates, and supporting assets.

## Bundle Structure

### Runtime Bundle Location

Workflow bundles are loaded at runtime from:

```
%USERPROFILE%\.ukbe-runner\workflows\<workflow>\
```

### Bootstrap Bundle Source

Packaged bootstrap templates exist in the repository at:

```
agent_runner_v2/bootstrap/workflows/default/
```

These seed the runtime bundles during `ukbe-run-agent init`.

## Directory Layout

### Standard Workflow Bundle

```
workflows/<workflow_name>/
├── template_groups.py          # Workflow step definitions
├── job_schema.json             # Job state validation schema
├── llm_response_schema.json    # LLM response validation schema
├── model_mapping.json          # Model aliases and configurations
└── prompts/
    └── <workflow_name>/
        ├── 01_step_name.txt    # Step prompt template
        ├── 01_step_name_qwen.txt  # Model-specific variant
        └── ...
```

### Bootstrap Bundle Layout

```
agent_runner_v2/bootstrap/workflows/default/
├── template_groups.py          # All workflow definitions
├── job_schema.json
├── llm_response_schema.json
├── model_mapping.json
└── prompts/
    ├── 00_master_docs_bootstrap_v1/
    ├── 10_execution_scaffold_v1/
    ├── 20_initiative_intake_v1/
    ├── 21_bug_fix_intake_v1/
    ├── 30_delivery_planning_v1/
    ├── 31_task_execution_v1/
    ├── 40_documentation_sync_v1/
    ├── 41_audience_doc_v1/
    └── ...
```

## Workflow Naming Convention

### Family ID Format

```
<NN>_<descriptive_name>_v<version>
```

| Component | Description | Example |
|-----------|-------------|---------|
| `NN` | Two-digit numeric prefix (ordering) | `00`, `20`, `31` |
| `descriptive_name` | snake_case workflow purpose | `master_docs_bootstrap` |
| `v<version>` | Version suffix | `v1`, `v2` |

### Prefix Ranges

| Range | Category | Examples |
|-------|----------|----------|
| `00-09` | Bootstrap/Scaffold | `00_master_docs_bootstrap_v1` |
| `10-19` | Execution Scaffold | `10_execution_scaffold_v1` |
| `20-29` | Intake/Planning | `20_initiative_intake_v1`, `21_bug_fix_intake_v1` |
| `30-39` | Delivery Planning | `30_delivery_planning_v1` |
| `31-49` | Task Execution | `31_task_execution_v1` |
| `40-59` | Documentation | `40_documentation_sync_v1`, `41_audience_doc_v1` |
| `50-69` | Stakeholder Sites | `50_architecture_site_v1` |
| `70-99` | Reserved | (future use) |

## Step Naming Convention

### Step File Format

```
<NN>_<step_name>.txt
<NN>_<step_name>_<model_alias>.txt
```

| Component | Description | Example |
|-----------|-------------|---------|
| `NN` | Two-digit step number (ordering within workflow) | `01`, `02` |
| `step_name` | snake_case step purpose | `generate_plan` |
| `model_alias` | Optional model-specific suffix | `qwen`, `claude` |

### Step Numbering

- Steps within a workflow are ordered by numeric prefix
- Gaps allowed for future insertion (e.g., `01`, `03`, `05`)
- Review/refine pairs share the same number with different suffixes

## Prompt Template Variants

### Model-Specific Prompts

When a step requires model-specific prompting, create variants:

```
08_impl_task.txt          # Default (Claude)
08_impl_task_qwen.txt     # Qwen variant
08_impl_task_codex.txt    # Codex variant
```

### Variant Selection

1. Runner checks for `{step}_{model_alias}.txt` first
2. Falls back to `{step}.txt` if model-specific variant not found
3. Model alias resolved via `model_mapping.json`

## Schema Files

### job_schema.json

Validates `job.json` structure:

```json
{
  "type": "object",
  "required": ["job_id", "template_group", "state", "artifacts"],
  "properties": {
    "job_id": { "type": "string" },
    "template_group": { "type": "string" },
    "state": { "type": "string" },
    "artifacts": { "type": "object" },
    "created_at": { "type": "string" },
    "updated_at": { "type": "string" }
  }
}
```

### llm_response_schema.json

Validates LLM response structure for structured outputs.

### model_mapping.json

Maps model aliases to configurations:

```json
{
  "claude": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514"
  },
  "qwen": {
    "provider": "alibaba",
    "model": "qwen-coder"
  },
  "codex": {
    "provider": "openai",
    "model": "codex-latest"
  }
}
```

## Template Groups Structure

### Workflow Definition

```python
WORKFLOW_FAMILIES = {
    "workflow_name_v1": {
        "description": "Human-readable description",
        "produces": ["ARTIFACT_KEY_1", "ARTIFACT_KEY_2"],
        "steps": [
            {
                "name": "step_name",
                "prompt": "prompts/workflow_name_v1/01_step_name.txt",
                "coder": True,
                "action": None,
                "next": "next_step_name",
                "failure": "failure_step_name"
            }
        ]
    }
}
```

### Step Configuration

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Step identifier |
| `prompt` | string | Path to prompt template |
| `coder` | boolean | Whether to invoke LLM |
| `action` | string | Action function name (if not coder) |
| `next` | string | Next step on success |
| `failure` | string | Next step on failure |
| `enable_notifications` | boolean | Send step notifications |

## Artifact Key Convention

### Key Format

```
<category>_<descriptor>_<suffix>
```

| Category | Purpose | Examples |
|----------|---------|----------|
| `INIT` | Initiative documents | `INIT_FILE`, `PRE_INIT_FILE` |
| `PLAN` | Planning documents | `PLAN_FILE`, `TASK_GRAPH_FILE` |
| `TASK` | Task documents | `TASK_FILE`, `IMPL_FILE` |
| `VALIDATION` | Validation artifacts | `VALIDATION_FILE`, `REVIEW_FILE` |
| `CODEBASE` | Codebase documentation | `CODEBASE_DOC_SOP`, `CODEBASE_INVENTORY` |
| `DELIVERY` | Delivery governance | `DELIVERY_SOP`, `DELIVERY_STATUS_RULES` |
| `SYSTEM` | System documentation | `SYSTEM_CONTEXT`, `COMPONENT_ARCHITECTURE` |

### File Suffix Convention

| Suffix | Meaning |
|--------|---------|
| `_FILE` | Primary document |
| `_v1`, `_v2` | Versioned template |
| `_MD` | Markdown format |
| `_JSON` | JSON format |

## Bundle Versioning

### Version Components

| Level | Format | Example |
|-------|--------|---------|
| Workflow | `v<N>` | `v1`, `v2` |
| Bundle | `default` | (single bundle per distribution) |
| Schema | SemVer | `1.0.0` |

### Version Compatibility

- Major version changes require `init` re-run
- Minor changes are backward compatible
- Patch changes are transparent

## Migration Path

### Adding New Workflows

1. Create prompt templates in `bootstrap/workflows/default/prompts/<workflow>/`
2. Add workflow definition to `template_groups.py`
3. Run `ukbe-run-agent init` to seed runtime bundles
4. Test workflow execution

### Modifying Existing Workflows

1. Update bootstrap templates
2. Run `ukbe-run-agent init` to update runtime bundles
3. Existing jobs continue with previous version
4. New jobs use updated templates

### Workflow Deprecation

1. Mark workflow as deprecated in `template_groups.py`
2. Set `deprecated: true` in workflow config
3. Remove from active documentation after 2 major versions

## Validation Rules

### Structural Validation

- All prompt files referenced in `template_groups.py` must exist
- All step `next` and `failure` targets must be valid step names
- All `produces` artifacts must be valid artifact keys
- Workflow names must follow naming convention

### Content Validation

- Prompt templates must use valid artifact key placeholders
- Prompts must not contain hardcoded paths
- Schema files must be valid JSON

Run validation:
```bash
ukbe-run-agent run --template-group documentation_sync_v1
```

## Reference

| Resource | Location |
|----------|----------|
| Template Groups | `agent_runner_v2/bootstrap/workflows/default/template_groups.py` |
| Job Schema | `agent_runner_v2/bootstrap/workflows/default/job_schema.json` |
| Model Mapping | `agent_runner_v2/bootstrap/workflows/default/model_mapping.json` |
| Prompt Templates | `agent_runner_v2/bootstrap/workflows/default/prompts/` |
