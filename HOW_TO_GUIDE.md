# Delivery Scaffold Workflow Guide

## Overview

This guide is specific to `delivery_scaffold_v1`. It is not the general operator manual for the daemon or backend-connected worker modes. For workstation worker setup, logs, heartbeats, and troubleshooting, use [docs/worker_supervisor_manual.md](docs/worker_supervisor_manual.md). For backend run submission parameters by workflow, use [docs/submit_job_manual.md](docs/submit_job_manual.md).
For the full workflow order to use on an existing repository after scaffolding, use [docs/operations/EXISTING_REPO_WORKFLOW_SOP.md](docs/operations/EXISTING_REPO_WORKFLOW_SOP.md).

The `delivery_scaffold_v1` workflow generates a complete delivery documentation system — templates, SOP, status rules, agent contracts, and codebase-documentation governance — into any target repository. This is the first step for any new project that wants to use the agent-runner-v2 orchestration system.

## What Gets Generated

```
docs/delivery/
├── 00_templates/
│   ├── 01_initiative.template.md
│   ├── 02_plan.template.md
│   ├── 02b_task_graph.template.md
│   ├── 03_task.template.md
│   ├── 04_implementation_plan.template.md
│   ├── 04_review.template.md
│   ├── 06_memory.template.md
│   ├── template_registry.md
│   ├── WORKFLOW_SOP_v1.md
│   └── DELIVERY_STATUS_RULES_v1.md
├── 01_initiatives/          # Future initiative documents
├── 02_plans/                # Future plan documents
│   └── artifacts/           # Task graph artifacts
├── 03_tasks/                # Future task documents
├── 04_implementation_plans/ # Future implementation plans
├── 05_reviews/              # Future review documents
├── 06_memory/               # Future memory documents
└── 08_agents/
    ├── AGENTS.md
    ├── AGENT-planner.md
    ├── AGENT-task-decomposer.md
    ├── AGENT-implementation-planner.md
    ├── AGENT-executor.md
    ├── AGENT-reviewer.md
    └── AGENT-memory-manager.md
```

## Prerequisites

1. **agent-runner-v2 installed:**
   ```bash
   cd /path/to/agent-runner-v2
   pip install -e .
   ```

2. **Coder CLIs available:**
   - `qwen` (Qwen Code CLI) — used for project analysis and template generation
   - `claude` (Claude Code CLI) — used for SOP and agent contract generation
   - API keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` (or your configured keys)

3. **Target repository** with at least a `README.md` or similar project description.

## Step 1: Ensure AI Context Files Exist (No Manual Creation Needed)

The scaffold workflow **auto-discovers** project context files — you don't need to create a seed file manually.

### Files That Are Auto-Discovered

The workflow scans the target project root for these files and reads everything it finds:

| Category | Files |
|----------|-------|
| **AI Coder Context** | `QWEN.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.windsurfrules` |
| **Project Metadata** | `README.md`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Gemfile` |
| **Architecture Docs** | `docs/architecture/*.md`, `docs/specs/*.md`, `docs/design/*.md`, `ARCHITECTURE.md`, `DESIGN.md` |
| **Existing Delivery Docs** | Any files already under `docs/delivery/` (for partial scaffolds) |

### What If No Files Exist?

If the target project has **none** of these files, the `project_analysis` step will return `REJECTED` with "No project context files found". Create at least a `README.md` or `QWEN.md` first.

### Example: What Gets Read

For a typical project with `QWEN.md` + `README.md` + `pyproject.toml`:

```
QWEN.md        → project rules, conventions, team structure
README.md      → project description, tech stack overview
pyproject.toml → project name, dependencies, Python version
```

The coder reads all three and synthesizes a structured `PROJECT_ANALYSIS` from them.

## Step 2: Initialize the Runner (if not already done)

In your **agent-runner-v2** directory:

```bash
ukbe-run-agent init
```

This creates `.ukbe-runner/` with workspace config and job storage.

## Step 3: Run the Scaffold Workflow

### Option A: Scaffold into the Same Repository

If your target project IS the agent-runner-v2 repo:

```bash
ukbe-run-agent run \
  --template-group delivery_scaffold_v1
```

### Option B: Scaffold into Another Repository (Recommended)

```bash
ukbe-run-agent run \
  --project-root /home/kengkoon/projects/agent-runner-v2 \
  --template-group delivery_scaffold_v1 \
  --target-project-root /path/to/your-target-project
```

This places `docs/delivery/` into `/path/to/your-target-project/`. The coder auto-discovers AI context files from the target project.

### Option C: Dry Run (Test Without Coder Invocation)

```bash
ukbe-run-agent run \
  --project-root /home/kengkoon/projects/agent-runner-v2 \
  --template-group delivery_scaffold_v1 \
  --target-project-root /path/to/your-target-project \
  --dry-run
```

This renders the prompt and saves it to `.ukbe-runner/jobs/...` without invoking any coder. Useful for verifying context variable resolution.

## Full Lifecycle Integration

The scaffolded governance is intended for the full requirement lifecycle:

1. `initiative_intake_v1`
   - captures requirement scope and documentation scope
   - records likely codebase areas affected and stale-guidance risk
2. `delivery_planning_v1`
   - turns documentation scope into plan, task-graph, and task obligations
   - defines documentation strategy and freshness risks
3. `task_execution_v1`
   - executes code and documentation updates together
   - validates tests and documentation synchronization before task completion

## Step 4: Monitor Workflow Progress

### Check Job State

```bash
ukbe-run-agent run \
  --template-group delivery_scaffold_v1 \
  --job-id SCAFFOLD-GEN-20260524-001 \
  --show-job
```

### Check Job Status Summary

```bash
ukbe-run-agent run \
  --template-group delivery_scaffold_v1 \
  --job-id SCAFFOLD-GEN-20260524-001 \
  --check-job-status
```

## Step 5: Handle Review Gates

The scaffold workflow has coder-driven review loops:

| Step | Coder | Review Coder | Loop |
|------|-------|--------------|------|
| `generate_sop` | claude | claude | refine_sop (max 2) → replan_sop (max 1) |
| `generate_templates` | qwen | qwen | refine_templates (max 2) |
| `generate_agents` | claude | claude | refine_agents (max 2) |

If a step is **REJECTED**, the runner automatically triggers the refine loop. If refine is exhausted, replan triggers (for SOP only).

### Force-Approve a Step (Skip Review)

```bash
ukbe-run-agent run \
  --template-group delivery_scaffold_v1 \
  --job-id SCAFFOLD-GEN-20260524-001 \
  --force-approve-step generate_sop
```

### Override to a Specific Step

```bash
ukbe-run-agent run \
  --template-group delivery_scaffold_v1 \
  --job-id SCAFFOLD-GEN-20260524-001 \
  --override-step generate_templates
```

## Step 6: Validate Generated Delivery Docs

The final step `validate_delivery_docs` is a **runner action** (not a coder step) that performs deterministic structural validation:

1. **Folder structure** — all 8 delivery folders exist
2. **Template completeness** — all 7 template files present
3. **Template structure** — required sections in each template
4. **SOP validity** — state machine, agent roles, approval rules
5. **Status rules validity** — lifecycles, forbidden transitions, authority model
6. **Agent registry consistency** — AGENTS.md matches individual contracts
7. **Cross-reference integrity** — templates reference each other correctly

The validation output is saved as `docs/delivery/folder_map.json`.

The validation also covers the codebase-documentation governance scaffold under `docs/codebase/`, including inventory, templates, and freshness / supersession rules.

### Run Validation Standalone

You can also run the validation action independently using Python:

```python
from pathlib import Path
from agent_runner_v2.actions.validate_delivery_docs import validate_delivery_docs

result = validate_delivery_docs(
    context={},
    state={},
    step_cfg={},
    project_root=Path('/path/to/your-target-project'),
)
print(f"Status: {result.status}")
print(f"Remark: {result.remark}")
```

## Step 7: Use the Scaffolded Delivery System

After the scaffold workflow completes, you can use the existing workflow groups against the scaffolded delivery system:

```bash
# Run delivery planning against the scaffolded templates
ukbe-run-agent run \
  --project-root /path/to/your-target-project \
  --template-group delivery_planning_v1 \
  --set INIT_FILE=docs/delivery/01_initiatives/INIT-20260524-01_my-initiative.md
```

The `delivery_planning_v1` workflow will validate its output (PLAN, TASK_GRAPH, TASK) against the templates generated by `delivery_scaffold_v1` via the `template_ref` configuration.

The planning and execution workflows are also expected to carry documentation-governance obligations forward so codebase docs stay current across the full intake -> planning -> execution lifecycle.

## Troubleshooting

### "Missing static reference file(s)" Error

This happens when running `delivery_planning_v1` or other workflows on a project that hasn't been scaffolded yet. Run `delivery_scaffold_v1` first, or ensure the referenced files exist.

### "Workflow bundle not found" Error

Run `ukbe-run-agent init` in the target project directory first to create the `.ukbe-runner/` workspace.

### Coder Timeout

If a coder step takes too long, increase the timeout:

```bash
export AGENT_RUNNER_CODER_TIMEOUT_SECONDS=1200  # 20 minutes
```

### Re-Apply Routing for Stuck Jobs

```bash
ukbe-run-agent run \
  --template-group delivery_scaffold_v1 \
  --job-id SCAFFOLD-GEN-20260524-001 \
  --reapply-routing
```

## Integration with Existing Workflows

The `delivery_scaffold_v1` workflow integrates with existing workflows through `template_ref`:

| Workflow Step | Template Type | Validated Sections |
|---------------|---------------|-------------------|
| `delivery_planning_v1` → `planner` | `02_plan` | Plan Objective, Strategy Overview, Task Breakdown, Scope Mapping, Risks, Deliverables, Acceptance Criteria |
| `delivery_planning_v1` → `task_graph` | `02b_task_graph` | Task Graph Objective, Task Graph, Execution Flow, Success Criteria |
| `delivery_planning_v1` → `task` | `03_task` | Objective, Inputs, Outputs, Execution Steps, Validation Criteria |
| `task_execution_v1` → `task` | `03_task` | Objective, Inputs, Outputs, Execution Steps, Validation Criteria |

If the scaffolded templates are available, the runner validates generated documents against them. If not, it falls back to the inline `required_sections` configuration.

## Architecture Notes

### Cross-Project Root Support

The `--target-project-root` argument enables the runner to generate delivery docs into a different repository than where the runner is installed:

- `--project-root` = where agent-runner-v2 is installed (runner's workspace)
- `--target-project-root` = where `docs/delivery/` is created (target project)

This is implemented via `ARTIFACT_ROOT` in `runtime_context.py`, which resolves to `delivery_root` when set.

### Runner Actions vs Coder Steps

The `validate_delivery_docs` step is a **runner action**, not a coder step. This means:

- No LLM invocation — it's pure Python validation
- Deterministic — always produces the same result for the same input
- Fast — no API calls or token costs
- Reliable — no transient failures from API timeouts

This follows the same pattern as `submit_comfyui` in `image_csv_gen_v1`.

### Agent Contracts

The scaffold workflow does not generate a standalone master-prompts folder. The workflow step definitions in `template_groups.py` serve as the agent contracts, while `docs/codebase/` governs full-repository documentation coverage and stale-doc cleanup.

### Codebase Documentation Tree

The scaffold also prepares this governance structure:

```text
docs/codebase/
|- 00_standards/
|  |- CODEBASE_DOC_SOP_v1.md
|  `- CODEBASE_DOC_STATUS_RULES_v1.md
|- 00_templates/
|  |- codebase_template_registry.md
|  |- 01_codebase_inventory.template.md
|  |- 02_module_doc.template.md
|  |- 03_component_doc.template.md
|  `- 04_change_impact.template.md
|- 01_inventory/
|  `- codebase_inventory.md
|- 02_modules/
|- 03_components/
|- 04_changes/
`- 05_archives/
```
