# Migration Guide: TEMPLATE_GROUPS → Plugin Workflow Package

This guide describes how to migrate an existing workflow definition from the
legacy `TEMPLATE_GROUPS` dict format (in `template_groups.py`) to a
self-contained **plugin workflow package** under `workflows/<name>/`.

## Benefits of Plugin Packages

- **Self-contained**: all prompts, actions, context hooks, and the manifest
  live in one directory — no scattering across `template_groups.py`, multiple
  prompt dirs, and `step_runner.py` alias functions.
- **Versionable**: the package directory can be versioned (e.g.
  `10_execution_scaffold_v2`) and coexist with older versions.
- **Cross-repo portable**: copying one directory moves the entire workflow.
- **TOML manifest**: cleaner syntax than nested Python dicts for step
  definitions, routing, and coder constraints.

## Prerequisites

- The `workflow_packages` system must be installed (it is part of
  `agent-runner-v2` — no extra dependencies).
- The loader (`workflow_packages/loader.py`) supports all common features.
  Verify your workflow does not use unsupported fields (see
  [Feature Reference](#feature-reference) below).

## Migration Steps

### Step 1: Study the Source Definition

Read the workflow's entry in `TEMPLATE_GROUPS` (in
`bootstrap/workflows/default/template_groups.py`). Document:

- The step order.
- For each step: name, prompt file (or action name), required inputs,
  produces, result meta key, coder constraints, review/refine routing,
  notification settings.
- The workflow metadata: `visibility`, `job_prefix`, `job_init_step`,
  `job_init_inputs`, `default_max_rejects`.
- Any `produced_document_status` or `requires_human_approval_after` flags.

### Step 2: Check for Special Aliases

Search `step_runner.py` for a `_set_<workflow>_aliases()` function that
fires for your workflow's `template_group` name. If one exists, you need
a `context_extensions.py` in the plugin package (see
[Context Extensions](#context-extensions) below).

```bash
grep -n "your_workflow_name" agent_runner_v2/step_runner.py
```

**Examples:**
- `00_master_docs_bootstrap_v2` — had `_set_master_docs_aliases()` in
  `step_runner.py`, replaced by `context_extensions.py`.
- `10_execution_scaffold_v1` — had no special aliases, so no
  `context_extensions.py` needed.

### Step 3: Create the Package Directory

```bash
mkdir -p workflows/<workflow_name_v2>/prompts
```

### Step 4: Write `workflow.toml`

Translate the `TEMPLATE_GROUPS` dict entry into TOML. Use
`workflows/00_master_docs_bootstrap_v2/workflow.toml` or
`workflows/10_execution_scaffold_v2/workflow.toml` as reference.

**Structure:**

```toml
[workflow]
name = "<name>"
version = "2"
label = "<Human-readable label>"
job_prefix = "<PREFIX>"
description = "<Description>"
visibility = "canonical"

[workflow.init]
step = "<first_step_name>"
inputs = []
default_max_rejects = <N>

# Coder step (calls an LLM)
[[step]]
name = "<step_name>"
prompt = "prompts/<prompt_file>.txt"
enable_notifications = true

[step.artifacts]
required_inputs = ["ARTIFACT_KEY"]
produces = ["ARTIFACT_KEY"]
result_meta_key = "ARTIFACT_KEY"
# or result_meta_key_from_context = "CONTEXT_VARIABLE"

[step.artifacts.produced_document_status]
artifact = "ARTIFACT_KEY"
required_status = "draft"

[step.coder]
default = "claude-architect"
allowed = ["claude-architect", "codex-architect", "qwen-architect"]
must_differ = false  # optional, default true

# Review routing (on the review step)
[step.on_reject_refine]
step = "<refine_step>"
artifact = "ARTIFACT_KEY"
max_iterations = 2
exhausted_failure_code = "CODE"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"

[step.on_exhaust_replan]
step = "<replan_step>"
artifact = "ARTIFACT_KEY"
max_iterations = 1
exhausted_failure_code = "CODE"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"

requires_human_approval_after = false

# Action step (deterministic runner action, no LLM)
[[step]]
name = "<step_name>"
action = "<action_function_name>"

[step.artifacts]
required_inputs = ["ARTIFACT_KEY"]
produces = ["ARTIFACT_KEY"]
result_meta_key = "ARTIFACT_KEY"
```

**Field mapping: TEMPLATE_GROUPS dict → workflow.toml:**

| TEMPLATE_GROUPS key | TOML path |
|---|---|
| `name` (implicit from dict key) | `[workflow].name` |
| `visibility` | `[workflow].visibility` |
| `job_prefix` | `[workflow].job_prefix` |
| `job_init_step` | `[workflow.init].step` |
| `job_init_inputs` | `[workflow.init].inputs` |
| `default_max_rejects` | `[workflow.init].default_max_rejects` |
| `steps` array order | Order of `[[step]]` entries |
| `step_configs[<name>].prompt_file` | `[[step]].prompt` |
| `step_configs[<name>].action` | `[[step]].action` |
| `step_configs[<name>].mode` | `[[step]].mode` |
| `step_configs[<name>].enable_notifications` | `[[step]].enable_notifications` |
| `step_configs[<name>].required_inputs` | `[[step]].artifacts.required_inputs` |
| `step_configs[<name>].produces` | `[[step]].artifacts.produces` |
| `step_configs[<name>].result_meta_key` | `[[step]].artifacts.result_meta_key` |
| `step_configs[<name>].result_meta_key_from_context` | `[[step]].artifacts.result_meta_key_from_context` |
| `step_configs[<name>].target_artifact` | `[[step]].artifacts.target_artifact` |
| `step_configs[<name>].edit_mode` | `[[step]].artifacts.edit_mode` |
| `step_configs[<name>].loop_returns_to` | `[[step]].artifacts.loop_returns_to` or `[[step]].loop_returns_to` |
| `step_configs[<name>].replan_returns_to` | `[[step]].artifacts.replan_returns_to` or `[[step]].replan_returns_to` |
| `step_configs[<name>].produced_document_status` | `[[step]].artifacts.produced_document_status` |
| `step_configs[<name>].requires_human_approval_after` | `[[step]].requires_human_approval_after` |
| `step_configs[<name>].coder.default` | `[[step]].coder.default` |
| `step_configs[<name>].coder.allowed` | `[[step]].coder.allowed` |
| `step_configs[<name>].coder.must_differ_from_previous_step` | `[[step]].coder.must_differ` |
| `step_configs[<name>].on_reject_refine` | `[[step]].on_reject_refine` |
| `step_configs[<name>].on_exhaust_replan` | `[[step]].on_exhaust_replan` |

### Step 5: Copy Prompt Files

Copy all prompt files from the bootstrap prompts directory:

```bash
cp bootstrap/workflows/default/prompts/<workflow_name>/*.txt \
   workflows/<workflow_name_v2>/prompts/
```

**Important**: Only prompt files referenced by `prompt = "prompts/<file>"` in
`workflow.toml` need to be present. Action steps (with `action = "..."`) do
not need prompt files.

### Step 6: Create `context_extensions.py` (If Needed)

Create this file only if the workflow had a `_set_<workflow>_aliases()`
function in `step_runner.py` that was called for your template group.
The file must export a `build_context_extensions()` function.

```python
"""Context extensions for <workflow_name>.

Injects workflow-specific path aliases into the prompt context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
) -> dict[str, str]:
    """Return additional context variables for this workflow."""
    extensions: dict[str, str] = {}
    # Add your workflow-specific key→path mappings here
    return extensions
```

After creating `context_extensions.py`, you can remove the corresponding
`_set_<workflow>_aliases()` function from `step_runner.py`.

### Step 7: Remove from `template_groups.py` (Optional)

If you want the old version to remain available as a fallback, keep it in
`TEMPLATE_GROUPS`. Otherwise, delete the entry. The v1→v2 pattern keeps
both:

- v1 stays in `TEMPLATE_GROUPS` (backward compatibility).
- v2 is discovered from the plugin package.

### Step 8: Update Hardcoded References

Search the codebase for hardcoded references to the old workflow name.
Common locations:

| File | What to update |
|---|---|
| `run_agent.py:_validate_static_reference_files()` | Add the new v2 name to the skip list tuple |
| `documentation_guardrails.py` | Add the new v2 name to the constant/set |
| `run_agent.py:import` | Update import name if the constant was renamed |
| `run_agent.py:usage` | Update comparison if the constant type changed |
| `system_docs.py` | Update any workflow sequence text |
| Batch files | Usually no change — they reference run target by name |

Search command:
```bash
grep -rn "<old_workflow_name>" agent_runner_v2/
```

### Step 9: Seed to Runtime

The runtime source of truth is under
`%USERPROFILE%\.ukbe-runner\workflows\default\<name>\`. The active
bundle (`default`) contains the runtime copy.

**For development/testing:**
```bash
xcopy /E /I workflows\<name> %USERPROFILE%\.ukbe-runner\workflows\default\<name>\
```

**For production:** This seeding happens as part of `ukbe-run-agent init`
or the bootstrap finalization action. Update the bootstrap seeding logic to
include the new package.

### Step 10: Verification

1. **Discovery (dry-run):**
   ```bash
   ukbe-run-agent run --template-group <name> --dry-run --new-job
   ```
   Verify the output shows the correct step count, prompt resolution, and
   artifact paths.

2. **Backend sync:**
   ```bash
   python -m agent_runner_v2.sync_workflows <name>
   ```
   Verify the backend receives and stores the definition correctly.

3. **Full execution:** Run the workflow end-to-end to verify all steps
   work correctly with prompt rendering, artifact resolution, and
   review/refine loops.

## Feature Reference

### Supported in `workflow.toml`

| Feature | Status | Notes |
|---|---|---|
| `result_meta_key` | ✅ | Standard artifact metadata key |
| `result_meta_key_from_context` | ✅ | Reads meta key from context variable |
| `on_reject_refine` | ✅ | Review→refine routing |
| `on_exhaust_replan` | ✅ | Refine exhaustion→replan routing |
| `replan_returns_to` | ✅ | Replan returns to generate step |
| `loop_returns_to` | ✅ | Refine returns to review step |
| `must_differ` (coder) | ✅ | TOML field, maps to `must_differ_from_previous_step` |
| `produced_document_status` | ✅ | Document status validation |
| `requires_human_approval_after` | ✅ | Human approval gate |
| `enable_notifications` | ✅ | Push notification support |
| Action steps (`action = "..."`) | ✅ | Uses global `actions/__init__.py` registration |
| Package-local actions (`actions.py`) | ✅ | Auto-discovered via `importlib` |

### NOT Supported

| Feature | Status | Alternative |
|---|---|---|
| `backtick` | ❌ | Not present in loader or step config |

## Common Pitfalls

1. **`_workflow_bundle` serialization**: The loader stamps a
   `WorkflowBundle` object on each step config for runtime use. When
   syncing to the backend, this must be stripped via
   `_strip_bundle_refs()` before JSON serialization. The
   `sync_workflows.py` script does this automatically.

2. **Naming collision**: If a plugin package name matches a
   `TEMPLATE_GROUPS` key, the plugin package wins. The loader checks
   `workflow.toml` first before falling back to `TEMPLATE_GROUPS`.

3. **Runtime vs repo**: The repo's `workflows/<name>/` directory is the
   **development** location. The runtime source of truth is
   `%USERPROFILE%\.ukbe-runner\workflows\default\<name>/`. Always seed
   after making changes.

4. **Prompt path resolution**: Prompt paths in `workflow.toml` are
   **relative to the package root**. Use `prompts/<file>.txt`, not
   absolute or bootstrap-relative paths.

5. **Context variables**: If the old workflow relied on context variables
   set by a `_set_*_aliases()` function in `step_runner.py`, you must
   either keep that function or create a `context_extensions.py`.
   Standard artifact keys (those in `REFERENCE_FILES` / `known_artifact_paths`)
   are always available.
