# How to Create a Plugin Workflow Package

This guide describes how to create a **new plugin workflow package** from
scratch — a self-contained workflow definition under `workflows/<name>/`
that the agent-runner-v2 runtime discovers and loads automatically.

## Overview

A plugin workflow package is a directory containing:

```
workflows/<name>/
├── workflow.toml              # Manifest: metadata + step definitions (REQUIRED)
├── context_extensions.py      # Context hook: injects per-step path aliases (OPTIONAL)
├── actions.py                 # Package-local action functions (OPTIONAL)
└── prompts/                   # Prompt template files (REQUIRED for coder steps)
    ├── 01_<step>.txt
    └── ...
```

The runtime discovers these packages via `_load_group()` in `run_agent.py`:
1. Looks for `<workflow_root>/<name>/workflow.toml` — if found, loads as
   plugin package.
2. Falls back to `TEMPLATE_GROUPS` dict.

## Step-by-Step

### 1. Choose a Workflow Name

Convention: `<number>_<descriptive_name>_v<version>`.

```
10_execution_scaffold_v2
31_task_execution_v1
40_documentation_sync_v1
```

The name must be unique across both `workflows/` and `TEMPLATE_GROUPS`.

### 2. Create the Directory Structure

```bash
mkdir -p workflows/<name>/prompts
```

### 3. Write `workflow.toml`

The manifest has three sections: `[workflow]`, `[workflow.init]`, and
one or more `[[step]]` entries.

#### `[workflow]` — Metadata

```toml
[workflow]
name = "<name>"
version = "1"
label = "<Human-readable label shown in logs>"
job_prefix = "<JOB_PREFIX>"        # e.g. "DOCGEN", "SCAFFOLD", "TASKEX"
description = "<Brief description>"
visibility = "canonical"           # or "hidden" for test/internal workflows
```

#### `[workflow.init]` — Initial Step Configuration

```toml
[workflow.init]
step = "<first_step_name>"          # Must match a [[step]].name below
inputs = []                          # Seed artifacts for new jobs
default_max_rejects = 3              # Max coder rejections before failure
```

#### `[[step]]` — Step Definitions

Each step is a `[[step]]` table. The order of `[[step]]` entries determines
the execution order. There are three types of steps:

**Type A: Coder Step** (calls an LLM)

```toml
[[step]]
name = "generate_document"
prompt = "prompts/01_generate_document.txt"
enable_notifications = true

[step.artifacts]
required_inputs = ["PROJECT_ANALYSIS"]
produces = ["DOCUMENT_FILE"]
result_meta_key = "DOCUMENT_FILE"

[step.coder]
default = "qwen-architect"
allowed = ["claude-architect", "codex-architect", "qwen-architect"]
must_differ = false       # optional, default true; set false for review steps
```

**Type B: Action Step** (deterministic Python function, no LLM)

```toml
[[step]]
name = "validate_documents"
action = "validate_delivery_docs"     # Function name in actions/__init__.py

[step.artifacts]
required_inputs = ["DOCUMENT_FILE"]
produces = ["VALIDATION_RESULT"]
result_meta_key = "VALIDATION_RESULT"
```

Actions are either:
- **Global**: registered in `agent_runner_v2/actions/__init__.py`
  (e.g. `validate_delivery_docs`, `prepare_delivery_scaffold`).
- **Package-local**: defined in the package's own `actions.py` file
  (auto-discovered by the loader).

**Type C: Review Step** (review with refine/replan routing)

```toml
[[step]]
name = "review_document"
prompt = "prompts/02_review_document.txt"
enable_notifications = true

[step.artifacts]
required_inputs = ["DOCUMENT_FILE"]
produces = ["REVIEW_FILE_SUGGESTED"]
result_meta_key_from_context = "REVIEW_FILE_SUGGESTED_SUGGESTED"

[step.coder]
default = "qwen-reviewer"
allowed = ["claude-reviewer", "codex-reviewer", "qwen-reviewer"]
must_differ = false

[step.on_reject_refine]
step = "refine_document"
artifact = "DOCUMENT_FILE"
max_iterations = 2
exhausted_failure_code = "REFINEMENT_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"

# Optional: replan fallback when refinement is exhausted
[step.on_exhaust_replan]
step = "replan_document"
artifact = "DOCUMENT_FILE"
max_iterations = 1
exhausted_failure_code = "REPLAN_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"

requires_human_approval_after = false
```

**Review/Refine/Replan Loop Pattern:**

```
generate_step → review_step → [APPROVED → next]
                              → [REJECTED → refine_step → review_step (loop)]
                                                     → [exhausted → replan_step → generate_step]
```

- **Refine step** sets `loop_returns_to = "<review_step>"` to return to
  review after refinement.
- **Replan step** (optional) sets `replan_returns_to = "<generate_step>"`
  to restart generation after replan.
- Review steps set `on_reject_refine` and optionally `on_exhaust_replan`.

Complete refine step:

```toml
[[step]]
name = "refine_document"
prompt = "prompts/03_refine_document.txt"

[step.artifacts]
required_inputs = ["PROJECT_ANALYSIS", "DOCUMENT_FILE", "REVIEW_FILE_SUGGESTED"]
produces = ["DOCUMENT_FILE"]
target_artifact = "DOCUMENT_FILE"
edit_mode = "in_place"
result_meta_key = "DOCUMENT_FILE"
loop_returns_to = "review_document"

[step.coder]
default = "qwen-architect"
allowed = ["claude-architect", "codex-architect", "qwen-architect"]
```

Complete replan step:

```toml
[[step]]
name = "replan_document"
prompt = "prompts/04_replan_document.txt"

[step.artifacts]
required_inputs = ["PROJECT_ANALYSIS", "DOCUMENT_FILE", "REVIEW_FILE_SUGGESTED"]
produces = ["DOCUMENT_FILE"]
target_artifact = "DOCUMENT_FILE"
edit_mode = "in_place"
result_meta_key = "DOCUMENT_FILE"
replan_returns_to = "generate_document"

[step.coder]
default = "qwen-architect"
allowed = ["claude-architect", "codex-architect", "qwen-architect"]
```

### 4. Write Prompt Files

Each prompt file is a text file in `prompts/<name>.txt` referenced by
`prompt = "prompts/<name>.txt"` in a step definition.

**Prompt file conventions:**
- Paths are relative to the package root (e.g. `prompts/01_step.txt`).
- Use `{ARTIFACT_KEY}` placeholders — the runner resolves these to file
  paths before invoking the coder.
- Available context variables include `{KEY}`, `{KEY_PATH}`,
  `{KEY_METAJSON}` for every artifact in `REFERENCE_FILES` /
  `known_artifact_paths()` from `constants.py`, plus any injected by
  `context_extensions.py`.

**Required sections in a prompt file (based on existing workflow patterns):**

```
Runner Gate (MANDATORY)
- <step-specific instructions>

Role:
- <agent role description>

Inputs:
- <input artifacts to read>

Task:
- <task description>

Completion rule (MANDATORY)
- Return APPROVED only after:
  - <output artifact> exists
  - meta.json sidecar exists
```

### 5. Create `context_extensions.py` (Only If Needed)

If your workflow introduces **new artifact keys** that are not in
`known_artifact_paths()` (from `constants.py`), you need a context
extensions module to inject those path aliases into the prompt context.

**When to use:** Your workflow produces artifacts whose paths are
computed at runtime (e.g., job-id-dependent paths like
`docs/delivery/03_tasks/<job_id>/TASK.md`) and don't have a static
entry in `REFERENCE_FILES`.

**When NOT to use:** If your workflow only uses standard artifact keys
that are already defined in `constants.py` (all `DELIVERY_*`, `CODEBASE_*`,
`PROJECT_ANALYSIS`, etc.), you do NOT need this file.

```python
"""Context extensions for <workflow_name>.

Injects workflow-specific path aliases into the prompt context.
This module is discovered and loaded dynamically by
step_runner._apply_workflow_package_context_hooks().
"""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any


def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
) -> dict[str, str]:
    """Return additional context variables for this workflow.

    For each custom artifact key, inject:
    - ``{KEY}`` -> resolved output path
    - ``{KEY}_PATH`` -> same resolved path
    - ``{KEY}_METAJSON`` -> path to the meta.json sidecar
    """
    extensions: dict[str, str] = {}

    # Example: compute custom artifact paths
    job_id = str(state.get("job_id") or "").strip()
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()

    for artifact_key, path_template in _CUSTOM_ARTIFACT_PATHS.items():
        resolved = path_template.format(job_id=job_id, step_dir_rel=step_dir_rel)
        resolved = resolved.replace("\\", "/")
        extensions[artifact_key] = resolved
        extensions[f"{artifact_key}_PATH"] = resolved
        if step_dir_rel:
            extensions[f"{artifact_key}_METAJSON"] = f"{step_dir_rel}/meta.json"
        else:
            p = PurePath(resolved)
            extensions[f"{artifact_key}_METAJSON"] = str(p.parent / f"{p.stem}.meta.json")

    return extensions


# Custom artifact path templates for this workflow
_CUSTOM_ARTIFACT_PATHS: dict[str, str] = {
    "CUSTOM_KEY": "docs/delivery/03_tasks/{job_id}/{step_dir_rel}/CUSTOM_FILE.md",
}
```

### 6. Create `actions.py` (Only If Needed)

If your workflow has action steps that are **specific to this workflow**
and not shared with others, define them in a package-local `actions.py`.

```python
"""Package-local actions for <workflow_name>."""

from __future__ import annotations

from pathlib import Path

from agent_runner_v2.action_result import ActionResult


def my_custom_action(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Perform a workflow-specific deterministic action."""
    # Implementation here
    return ActionResult(
        status="APPROVED",
        remark="Action completed.",
        artifacts={},
    )
```

The loader auto-discovers functions in `actions.py` via `importlib` and
makes them available by name. Reference them in `workflow.toml` as:

```toml
[[step]]
name = "my_action"
action = "my_custom_action"
```

**For shared actions** (used by multiple workflows), register them in
`agent_runner_v2/actions/__init__.py` instead.

### 7. Update Hardcoded References

If your workflow name triggers special handling anywhere in the runtime,
update those references. Search the codebase:

```bash
grep -rn "<other_workflow_name>" agent_runner_v2/ --include="*.py"
```

Common locations that may need updating:

| File | Purpose | When to Update |
|---|---|---|
| `run_agent.py` — `_validate_static_reference_files()` | Skip pre-existing file checks for bootstrap/scaffold workflows | Only for workflows that generate ALL artifacts from scratch |
| `documentation_guardrails.py` | Route to workflow-specific canonical doc paths | Only when the workflow generates protected documents |
| `system_docs.py` | Workflow sequence text in generated docs | When the workflow name appears in generated documentation |
| `step_runner.py` — `_set_*_aliases()` | Special context variable injection | Only if you're migrating from an old version that had aliases — and ideally replace with `context_extensions.py` |

### 8. Create the Prompt Files

Write one `.txt` per coder step in `prompts/`. The prompt filename must
match the `prompt = "prompts/<file>"` value in `workflow.toml`.

Action steps (`action = "..."`) do not need prompt files.

### 9. Seed to the Runtime Location

The runtime loads plugin packages from the active workflow bundle,
typically at:

```
%USERPROFILE%\.ukbe-runner\workflows\default\<name>\
```

Seed the package:

```bash
xcopy /E /I workflows\<name> %USERPROFILE%\.ukbe-runner\workflows\default\<name>\
```

For production deployments, update the bootstrap seeding logic (in
`actions/finalize_bootstrap.py` or the `init` command) to include the
new package.

### 10. Verify

**Dry-run to confirm discovery and prompt resolution:**

```bash
ukbe-run-agent run --template-group <name> --dry-run --new-job
```

Expected output:
- `step <N> of <total>` — confirms all steps loaded.
- `Using default prompt: <name>\prompts\<step>.txt` — confirms prompt
  resolution.
- `APPROVED` status — confirm dry-run completed.

**Backend sync:**

```bash
python -m agent_runner_v2.sync_workflows <name>
```

Expected output:
- `[<name>] created -> id=<uuid> name=<name>`

**Full execution:** Run the workflow end-to-end.

## Reference: Existing Plugin Packages

| Package | Steps | Aliases | Actions | Notes |
|---|---|---|---|---|
| `00_master_docs_bootstrap_v2` | 13 | `context_extensions.py` | 5 action steps | Master documentation bootstrap |
| `10_execution_scaffold_v2` | 13 | None | 2 action steps | Delivery scaffold governance |

## TOML Schema Reference

### `[workflow]` Table

| Key | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | string | yes | — | Workflow name (must match directory name) |
| `version` | string | no | `"1"` | Version string |
| `label` | string | no | — | Human-readable label |
| `job_prefix` | string | yes | — | Prefix for job IDs (e.g. `DOCGEN`) |
| `description` | string | no | — | Longer description |
| `visibility` | string | no | `"canonical"` | `"canonical"` or `"hidden"` |

### `[workflow.init]` Table

| Key | Type | Required | Default | Description |
|---|---|---|---|---|
| `step` | string | yes | — | Name of the first step to execute |
| `inputs` | array of strings | no | `[]` | Seed artifact keys for new jobs |
| `default_max_rejects` | integer | no | `3` | Max coder rejections before failure |

### `[[step]]` Table

| Key | Type | Required | Applies To | Description |
|---|---|---|---|---|
| `name` | string | yes | all | Step name (unique within workflow) |
| `prompt` | string | conditional | coder steps | Path to prompt file (relative to package root) |
| `action` | string | conditional | action steps | Name of action function |
| `mode` | string | no | all | Step mode (e.g. `"bootstrap"`) |
| `enable_notifications` | boolean | no | all | Send push notification for this step |
| `requires_human_approval_after` | boolean | no | review steps | Require manual approval gate |
| `loop_returns_to` | string | no | refine steps | Return to this step after refinement |
| `replan_returns_to` | string | no | replan steps | Return to this step after replan |
| `target_artifact` | string | no | refine/replan | Target artifact for in-place editing |
| `edit_mode` | string | no | refine/replan | Edit mode (e.g. `"in_place"`) |

### `[[step]].artifacts` Table

| Key | Type | Required | Description |
|---|---|---|---|
| `required_inputs` | array of strings | no | Artifact keys that must exist before running |
| `produces` | array of strings | yes | Artifact keys this step creates |
| `result_meta_key` | string | conditional | Artifact key to write to `meta.json` as result |
| `result_meta_key_from_context` | string | conditional | Context variable name for the result meta key |
| `target_artifact` | string | no | Artifact key for in-place editing |
| `edit_mode` | string | no | Edit mode (e.g. `"in_place"`) |

### `[[step]].artifacts.produced_document_status` Table

| Key | Type | Required | Description |
|---|---|---|---|
| `artifact` | string | yes | Artifact key to validate status on |
| `required_status` | string | yes | Expected status value (e.g. `"draft"`) |

### `[[step]].coder` Table

| Key | Type | Required | Description |
|---|---|---|---|
| `default` | string | yes | Default coder (e.g. `"qwen-architect"`) |
| `allowed` | array of strings | no | Allowed coders for this step |
| `must_differ` | boolean | no | Require a different coder from previous step (default `true`) |

### `[[step]].on_reject_refine` Table

| Key | Type | Required | Description |
|---|---|---|---|
| `step` | string | yes | Refine step name to route to on rejection |
| `artifact` | string | yes | Artifact key to refine |
| `max_iterations` | integer | yes | Max number of refine iterations |
| `exhausted_failure_code` | string | yes | Failure code when iterations exhausted |
| `exhausted_failure_class` | string | yes | Failure class (e.g. `"HUMAN_RETRY_REQUIRED"`) |

### `[[step]].on_exhaust_replan` Table

| Key | Type | Required | Description |
|---|---|---|---|
| `step` | string | yes | Replan step name to route to |
| `artifact` | string | yes | Artifact key to regenerate |
| `max_iterations` | integer | yes | Max number of replan iterations |
| `exhausted_failure_code` | string | yes | Failure code when iterations exhausted |
| `exhausted_failure_class` | string | yes | Failure class (e.g. `"HUMAN_RETRY_REQUIRED"`) |
