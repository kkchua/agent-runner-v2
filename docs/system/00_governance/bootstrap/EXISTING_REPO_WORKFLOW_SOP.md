---
title: "Existing Repo Workflow SOP: agent-runner-v2"
template_id: "OPS-02-WSOP"
status: "active"
managed_by: workflow-generated
created: "2026-07-02T20:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Existing Repo Workflow SOP: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

## 1. Workflow Families

The following workflow families are available in the default bundle:

| Family | Steps | Prefix | Purpose |
|--------|-------|--------|---------|
| `00_master_docs_bootstrap_v1` | 10 | `00` | Master documentation bootstrap |
| `10_execution_scaffold_v1` | 13 | `10` | Delivery scaffold generation |
| `20_initiative_intake_v1` | 5 | `20` | Initiative intake and refinement |
| `21_bug_fix_intake_v1` | 7 | `21` | Bug fix workflow |
| `30_delivery_planning_v1` | 10 | `30` | Plan generation, task graph, contracts |
| `31_task_execution_v1` | 12 | `31` | Implementation planning, execution, validation |
| `40_documentation_sync_v1` | 4 | `40` | Documentation synchronization |
| `image_csv_gen_v1` | 5 | - | Image CSV generation pipeline |
| `image_csv_gen_v2` | 5 | - | Enhanced image CSV generation |
| `tiktok_video_pipeline_v1` | 10 | - | TikTok video production pipeline |
| `videoxpress_gen_v1` | 9 | - | Video generation workflow |

## 2. Workflow Selection Guide

| Use Case | Workflow Family | Entry Point |
|----------|-----------------|-------------|
| Generate system documentation | `00_master_docs_bootstrap_v1` | `run-00_master_docs_bootstrap_v1.bat` |
| Set up delivery governance | `10_execution_scaffold_v1` | `run-10_execution_scaffold_v1.bat` |
| Start new initiative | `20_initiative_intake_v1` | `scripts/submit-initiative-intake.sh` |
| Fix a bug | `21_bug_fix_intake_v1` | Manual submission |
| Create delivery plan | `30_delivery_planning_v1` | `scripts/submit-delivery-planning.sh` |
| Execute development task | `31_task_execution_v1` | `scripts/examples/submit-task-execution.sh` |
| Sync documentation | `40_documentation_sync_v1` | Manual submission |
| Generate image dataset | `image_csv_gen_v2` | Manual submission |
| Create TikTok video | `tiktok_video_pipeline_v1` | Manual submission |
| Generate video content | `videoxpress_gen_v1` | Manual submission |

## 3. Standard Operating Procedure

### 3.1 Prerequisites

1. Runner initialized: `ukbe-run-agent init`
2. Job directory exists or will be created
3. Required artifacts from previous steps (if applicable)

### 3.2 Running a Workflow

#### Option A: Using Batch Scripts (Windows)

```bash
# Example: Master docs bootstrap
run-00_master_docs_bootstrap_v1.bat

# Example: Delivery scaffold
run-10_execution_scaffold_v1.bat
```

#### Option B: Using Shell Scripts (WSL/Unix)

```bash
# Example: Initiative intake
./scripts/submit-initiative-intake.sh

# Example: Delivery planning
./scripts/submit-delivery-planning.sh
```

#### Option C: Direct CLI

```bash
# Run a workflow
ukbe-run-agent run <workflow-name>

# Run specific step
ukbe-run-agent run <workflow-name> --step <step-name>

# Resume job
ukbe-run-agent run <workflow-name> --job-id <job-id>
```

### 3.3 Step-by-Step Execution

```
1. Identify workflow family based on use case
2. Check for existing job (resume vs new)
3. Run workflow via appropriate script or CLI
4. Monitor execution for approvals/rejections
5. Review artifacts produced
6. Approve steps as needed
7. Complete or escalate based on results
```

## 4. Artifact Management

### 4.1 Standard Artifact Keys

| Key | Description | Example Path |
|-----|-------------|--------------|
| `DRAFT_INIT_FILE` | Draft initiative | `docs/delivery/initiatives/...` |
| `PRE_INIT_FILE` | Pre-initiative document | `docs/delivery/initiatives/...` |
| `INIT_FILE` | Initiative document | `docs/delivery/initiatives/...` |
| `PLAN_FILE` | Delivery plan | `docs/delivery/plans/...` |
| `TASK_GRAPH_FILE` | Task graph | `docs/delivery/task-graphs/...` |
| `TASK_FILE` | Task contract | `docs/delivery/tasks/...` |
| `IMPL_FILE` | Implementation | `src/...` |
| `REVIEW_FILE` | Review document | `docs/delivery/reviews/...` |
| `VALIDATION_FILE` | Validation result | `docs/delivery/validations/...` |

### 4.2 Artifact Path Resolution

Artifacts are resolved relative to:
- Project root (default)
- Delivery root (if set)
- Artifact root (step-specific)

### 4.3 Promoting Artifacts

```bash
# Promote artifact to next stage
ukbe-run-agent run promote --from <source> --to <target>

# Or use action directly
python -m agent_runner_v2.actions.promote_artifact ...
```

## 5. Workflow Customization

### 5.1 Customizing Prompts

1. Edit prompt in runtime bundle:
   `%USERPROFILE%\.ukbe-runner\workflows\default\prompts\<workflow>\<step>.txt`

2. Changes take effect immediately (no restart needed)

### 5.2 Customizing Step Config

Edit `template_groups.py` in runtime bundle:

```python
"my_step": {
    "prompt": "prompts/my_workflow/my_step.txt",
    "coder": "claude",
    "coder_timeout_seconds": 900,  # Custom timeout
    "action": "my_custom_action",
}
```

### 5.3 Adding Workflow Families

1. Create folder: `%USERPROFILE%\.ukbe-runner\workflows\default\prompts\my_workflow\`
2. Add prompts: `01_step.txt`, `02_step.txt`, etc.
3. Add to `template_groups.py`:
```python
MY_WORKFLOW = {
    "steps": {...},
    "transitions": [...],
}
TEMPLATE_GROUPS["my_workflow_v1"] = MY_WORKFLOW
```

## 6. Integration with Development Workflow

### 6.1 Git Workflow

| Workflow Stage | Git Action |
|----------------|------------|
| Before workflow | Commit current work |
| During workflow | Monitor, don't commit |
| After approval | Commit generated artifacts |
| Review phase | Review diff before commit |

### 6.2 CI/CD Integration

```yaml
# Example GitHub Actions step
- name: Run Documentation Sync
  run: |
    pip install -e ".[dev]"
    ukbe-run-agent init
    ukbe-run-agent run 40_documentation_sync_v1 --step 01_sync_docs
```

### 6.3 IDE Integration

Recommended setup:
- Monitor `%USERPROFILE%\.ukbe-runner\logs\` for real-time status
- Use file watchers on `meta.json` for step completion
- Configure artifact directories for quick access

## 7. Troubleshooting Workflows

### 7.1 Workflow Not Found

**Symptoms:**
```
Error: Template group not found: my_workflow
```

**Resolution:**
1. Check workflow name spelling
2. Verify `template_groups.py` includes the workflow
3. Check runtime bundle is up to date: `ukbe-run-agent init`

### 7.2 Step Not Found

**Symptoms:**
```
Error: Step not found: my_step
```

**Resolution:**
1. Check step name in `template_groups.py`
2. Verify prompt file exists: `prompts/<workflow>/<step>.txt`
3. Check for step naming conventions (prefix with numbers)

### 7.3 Artifact Key Not Found

**Symptoms:**
Validation fails for expected artifact

**Resolution:**
1. Check `ARTIFACT_KEYS` in `template_groups.py`
2. Verify artifact is produced by coder
3. Check artifact path is relative to project root

### 7.4 Prompt Not Found

**Symptoms:**
```
Error: Prompt file not found: prompts/my_workflow/my_step.txt
```

**Resolution:**
1. Create missing prompt file
2. Check path in step config
3. Verify runtime bundle structure

## 8. Best Practices

### 8.1 Naming Conventions

- Workflows: `NN_description_vN` (e.g., `20_initiative_intake_v1`)
- Steps: `NN_step_name` (e.g., `01_pre_init`)
- Jobs: Use UUIDs or descriptive IDs with timestamps

### 8.2 Documentation Hygiene

- Commit generated docs before starting new workflows
- Review diff before committing workflow-generated changes
- Keep `meta.json` files for audit trail
- Archive old job directories periodically

### 8.3 Backup Strategy

- Backup runner home weekly
- Keep job directories until workflow completed
- Use version control for workflow customizations
- Document custom prompts in project README

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs`*
