# Prompt & Workflow Path Resolution

## Two Locations, Two Purposes

```
agent_runner_v2/prompts/           ← Source code (bootstrap templates)
.ukbe-runner/workflows/default/    ← Runtime (actual prompts read by CLI)
```

## How It Works

### 1. `cli init` — Bootstrap
When you initialize a new repo:
```bash
agent-runner-v2 init --project-root /path/to/repo
```

The `seed_workflow_bundle()` function copies from **code folder** → **.ukbe-runner**:
- `agent_runner_v2/prompts/` → `.ukbe-runner/workflows/default/prompts/`
- `agent_runner_v2/template_groups.py` → `.ukbe-runner/workflows/default/template_groups.py` (seeded but overridden)
- `agent_runner_v2/model_mapping.json` → `.ukbe-runner/workflows/default/model_mapping.json`
- Schemas (job_schema.json, llm_response_schema.json, etc.)

### 2. CLI Runtime — Reads from `.ukbe-runner`
When running steps:
```bash
agent-runner-v2 run_agent --template-group delivery_scaffold_v1 --project-root /path/to/repo
```

The path resolution is:
```
RUNNER_ROOT → workflow_root → .ukbe-runner/workflows/default/
```

So **all prompts are read from `.ukbe-runner/workflows/default/prompts/`** at runtime.

### 3. Template Overrides (Per-Repo)
Each repo can customize by editing files in `.ukbe-runner/workflows/default/`:
- Edit prompts → `.ukbe-runner/workflows/default/prompts/delivery_scaffold_v1/02_generate_sop.txt`
- Add new workflows → `.ukbe-runner/workflows/my-custom-workflow/`
- Add workflow definition → `.ukbe-runner/workflows/my-custom-workflow/template_groups.py`

### 4. Code Folder = Source of Truth for Defaults
The code folder (`agent_runner_v2/`) contains the **default templates**:
- New repos get these via `cli init`
- Changes to code folder prompts must be synced to `.ukbe-runner` for them to take effect

## Prompt Resolution Order

```
resolve_prompt_path(step_cfg, coder, model_id):
  1. {stem}_{model_id}{suffix}     ← model-specific (e.g. 05_refine_sop_sonnet-4-20250514.txt)
  2. {stem}_{coder}{suffix}        ← coder-specific (e.g. 05_refine_sop_codex.txt)
  3. {stem}{suffix}                ← default (e.g. 05_refine_sop.txt)
```

All paths are relative to `RUNNER_ROOT` = `.ukbe-runner/workflows/default/`.

## Critical: Syncing Changes

When modifying prompts in the code folder, you MUST sync to `.ukbe-runner`:

```bash
# Sync all prompts
cp agent_runner_v2/prompts/delivery_scaffold_v1/* \
   .ukbe-runner/workflows/default/prompts/delivery_scaffold_v1/

# Or for a single file
cp agent_runner_v2/prompts/delivery_scaffold_v1/05_refine_sop.txt \
   .ukbe-runner/workflows/default/prompts/delivery_scaffold_v1/
```

**If you don't sync, your changes won't be picked up at runtime!**

## Template Groups Loading

Note: `template_groups.py` (workflow definitions) is **always** loaded from the code folder, not from `.ukbe-runner`:

```python
# bundle_loader.py - line 50
def load_workflow_module(...):
    # Always load template_groups.py from the installed package source
    from . import template_groups as pkg_template_groups
    return pkg_template_groups
```

This ensures workflow code changes (new steps, coder assignments, etc.) take effect immediately without re-seeding.

## Summary

| What | Location | Purpose |
|------|----------|---------|
| **Prompts** | `.ukbe-runner/workflows/default/prompts/` | Runtime - what the CLI reads |
| **Prompt templates** | `agent_runner_v2/prompts/` | Bootstrap - copied to .ukbe-runner on init |
| **Workflow code** | `agent_runner_v2/template_groups.py` | Always loaded from code folder |
| **Workflow config** | `.ukbe-runner/workflows/default/config.json` | Per-repo workflow settings |
| **Job data** | `.ukbe-runner/jobs/<template>/<job>/` | Step logs, state, artifacts |
