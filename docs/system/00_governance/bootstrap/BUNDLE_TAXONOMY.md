---
title: "Bundle Taxonomy"
template_id: "SYS-00-BT"
status: "active"
managed_by: workflow-generated
generated: "2026-07-02T00:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Bundle Taxonomy

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

## Overview

The agent-runner-v2 uses a **two-source model** for workflow definitions:

1. **Packaged Bootstrap Source** — Shipped with the package in `agent_runner_v2/bootstrap/`
2. **Runtime Workflow Bundle** — Global user directory at `%USERPROFILE%\.ukbe-runner\workflows\`

This document describes the taxonomy and structure of workflow bundles.

## Bundle Structure

### Runtime Bundle Location

```
%USERPROFILE%\.ukbe-runner/
├── config.json              # Global configuration
├── jobs/                    # Job state storage
│   └── {workflow_name}/
│       └── {job_id}/
│           ├── job.json     # Job state (schema v6)
│           ├── {step_dir}/  # Step artifacts
│           │   ├── meta.json
│           │   └── ...
├── workflows/               # Workflow bundles
│   └── {workflow_name}/
│       ├── template_groups.py    # Workflow definitions
│       ├── job_schema.json         # Job state schema
│       ├── llm_response_schema.json
│       ├── model_mapping.json      # Coder alias resolution
│       └── prompts/               # Prompt templates
│           └── {step_name}/
│               └── {step}.txt
└── logs/                    # Execution logs
```

### Packaged Bootstrap Source

```
agent_runner_v2/bootstrap/workflows/default/
├── template_groups.py       # Workflow definitions
├── job_schema.json
├── llm_response_schema.json
├── model_mapping.json
└── prompts/
    └── {workflow_family}/
        └── {step}.txt
```

## Workflow Families

Workflows are organized into families by purpose:

| Family | Steps | Purpose |
|--------|-------|---------|
| `00_master_docs_bootstrap_v1` | 10 | Master documentation bootstrap and system documentation generation |
| `10_execution_scaffold_v1` | 13 | Delivery scaffold generation (SOPs, templates, agents) |
| `20_initiative_intake_v1` | 5 | Initiative intake and pre-init refinement |
| `21_bug_fix_intake_v1` | 7 | Bug fix workflow (triage, reproduce, isolate, patch, validate) |
| `30_delivery_planning_v1` | 10 | Plan generation, task graph, and task contract generation |
| `31_task_execution_v1` | 12 | Implementation planning, execution, documentation sync, validation |
| `40_documentation_sync_v1` | 4 | Documentation-only synchronization flow |
| `image_csv_gen_v2` | 3 | Image CSV generation pipeline |
| `videoxpress_gen_v1` | 9 | Video generation workflow |
| `tiktok_video_pipeline_v1` | 10 | TikTok video production pipeline |

## Step Naming Convention

Steps follow a semantic naming pattern:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `{NN}_` | Step number | `01_pre_init` |
| `review_` | Review step | `02_review_pre_init` |
| `refine_` | Refinement step | `03_refine_pre_init` |
| `replan_` | Replanning step | `03_replan_plan` |
| `validate_` | Validation step | `11_validate` |
| `sync_` | Synchronization step | `sync_docs` |

## Prompt Template Structure

Each prompt template is a text file with placeholder substitution:

```
# Context
{{CONTEXT}}

## Instructions
{{INSTRUCTIONS}}

## Artifacts
{{ARTIFACTS}}
```

### Placeholder Variables

| Variable | Description |
|----------|-------------|
| `{{CONTEXT}}` | Rendered context from template_groups.py |
| `{{INSTRUCTIONS}}` | Step-specific instructions |
| `{{ARTIFACTS}}` | Artifact path mappings |
| `{{STATE}}` | Current job state |

## Configuration Files

### model_mapping.json

Maps coder aliases to actual model configurations:

```json
{
  "claude": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514"
  },
  "codex": {
    "provider": "openai",
    "model": "codex-latest"
  },
  "qwen": {
    "provider": "alibaba",
    "model": "qwen-coder-latest"
  }
}
```

### job_schema.json

JSON Schema for job state validation (schema version v6).

### llm_response_schema.json

Schema for LLM response validation and structuring.

## Bundle Loading

### Initialization

```bash
ukbe-run-agent init
```

Seeds the global runner home from packaged bootstrap source.

### Runtime Loading

At execution, the runner:

1. Resolves workflow root from `RUNNER_WORKFLOW_ROOT` or default
2. Loads `template_groups.py` from runtime bundle
3. Loads prompt templates from runtime bundle
4. Validates against schemas

## Bundle Taxonomy Module

The `bundle_taxonomy.py` module provides:

- Workflow family enumeration
- Step classification
- Prompt template resolution
- Bundle validation

## Best Practices

### Adding New Workflows

1. Define workflow in `template_groups.py`
2. Create prompt templates in `prompts/{family}/`
3. Update `model_mapping.json` if needed
4. Run `ukbe-run-agent init` to seed

### Modifying Existing Workflows

1. Edit source in package bootstrap
2. Re-run `ukbe-run-agent init` to update runtime
3. Or manually update runtime bundle

### Bundle Versioning

- Bundle version is implicit in package version
- Job state schema is versioned (currently v6)
- Breaking changes require migration

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs`*
