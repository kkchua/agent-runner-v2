# Workflow Package Developer Guide

## Overview

A workflow package is a self-contained directory that defines a governed,
multi-step workflow. Each package lives under `workflows/<name>/` and is
loaded by the runner as a plugin. The daemon claims steps from a backend
registry and spawns `run_agent.py` per step — the package never runs as
a long-lived process.

## Directory Structure

```
workflows/<name>/
├── workflow.toml              # Manifest: steps, artifacts, routing, coders
├── bundle_governance.toml     # Canonical artifact registry (single source of truth)
├── context_extensions.py      # MANDATORY — WorkflowExtensions interface (see below)
├── actions.py                 # Custom @action functions (optional)
├── prompts/                   # Prompt template .txt files
├── bundle_governance/         # Generated governance adapters
│   ├── core_governance.md     # Bundle-level governance rules
│   ├── prompt_sop.md          # SOP rules injected into every prompt
│   ├── prompt_contract.json   # Required prompt markers and rejection terms
│   └── generated/             # Adapter targets (AGENTS.md, QWEN.md, CLAUDE.md)
│       ├── AGENTS.md
│       ├── QWEN.md
│       └── CLAUDE.md
└── README.md                  # Optional package documentation
```

## Required Files

Every workflow package must contain at minimum:

| File | Purpose |
|---|---|
| `workflow.toml` | Step definitions, routing, coder roles, artifact contracts |
| `bundle_governance.toml` | Canonical artifact registry — the single source of truth for artifact keys |
| `context_extensions.py` | **MANDATORY** — `WorkflowExtensions` subclass implementing lifecycle hooks (see below) |
| `prompts/` | At least one `.txt` prompt template per prompt-driven step |

## `bundle_governance.toml` — Artifact Registry

**This file is the single source of truth for artifact keys.** Every
artifact your workflow can produce or consume must be declared here.

### Structure

```toml
[governance]
canonical_source = "bundle_governance/core_governance.md"
generated_dir = "bundle_governance/generated"
adapter_targets = ["AGENTS.md", "QWEN.md", "CLAUDE.md"]
include_in_prompts = true
prompt_targets = [
  "generate_docs",
  "review_docs",
  "refine_docs",
  "audit_docs",
]

[[artifact]]
key = "MY_FOUNDATION_INDEX"
path = "docs/output/runs/<job_id>/README.md"
description = "Staged foundation index."
required = true

[[artifact]]
key = "MY_VALIDATION_REPORT"
path = "docs/output/runs/<job_id>/<job_id>-validation.md"
description = "Deterministic validation report."
required = false
```

### Artifact declaration fields

| Field | Required | Description |
|---|---|---|
| `key` | Yes | Artifact key — matches keys used in `workflow.toml` step `produces`/`inputs` |
| `path` | Yes | Path template — use `<job_id>` placeholder for run-scoped paths |
| `description` | No | Human-readable description |
| `required` | No | Whether the artifact must exist for validation to pass (default `false`) |

### Why it matters

- The runner stores `workflow_artifact_keys` in job state at creation time.
- `build_job_sync_payload()` filters artifacts to only keys declared here.
- Undeclared artifacts are rejected before reaching the backend, preventing
  foreign-key violations on the backend's `artifact_types` table.
- The backend sync uses these keys to auto-register artifact types.

**If your workflow produces an artifact but doesn't declare it in
`bundle_governance.toml`, the sync will silently drop it.**

---

## `workflow.toml` — Step Definitions

### Top-level metadata

```toml
[workflow]
name = "my_workflow_v1"
version = "1"
label = "My Workflow v1"
job_prefix = "MYWF"
description = "Brief description of what this workflow does."
visibility = "canonical"
default_max_rejects = 3

[workflow.init]
step = "collect_context"
inputs = []
```

### Step types

#### Prompt-driven step

Invokes an LLM coder with a prompt template from `prompts/`.

```toml
[[step]]
name = "generate_docs"
prompt = "prompts/01_generate_docs.txt"
enable_notifications = true
onsuccess = "review_docs"

[step.artifacts]
required_inputs = ["MY_CONTEXT_INVENTORY"]
produces = [
  "MY_FOUNDATION_INDEX",
  "MY_LAYER_MODEL",
]
result_meta_key = "MY_FOUNDATION_INDEX"

[step.coder]
role_policy = "architect_standard"
```

#### Action-driven step

Invokes a Python function registered with the `@action()` decorator.

```toml
[[step]]
name = "validate_docs"
action = "validate_docs"
enable_notifications = true
onsuccess = "publish_docs"

[step.artifacts]
required_inputs = ["MY_FOUNDATION_INDEX", "MY_LAYER_MODEL"]
produces = ["MY_VALIDATION_REPORT"]
result_meta_key = "MY_VALIDATION_REPORT"
```

#### Promote step

A promote step updates an artifact document's `Status:` field to
`Approved` in-place. Uses the `promote_artifact` or `promote_all`
action.

**IMPORTANT:** The `promotes` key MUST be at the top level of `[[step]]`,
NOT under `[step.artifacts]`. The TOML loader only extracts specific
known fields from `[step.artifacts]` — `promotes` is not one of them and
gets silently dropped if placed there. Top-level unknown keys are
captured by the `extra` passthrough and reach the action's `step_cfg`.

```toml
[[step]]
name = "promote_plan"
action = "promote_artifact"
promotes = "PLAN_FILE"
enable_notifications = true
onsuccess = "stepCompletion"

[step.artifacts]
required_inputs = ["PLAN_FILE"]
result_meta_key = "PLAN_FILE"
```

For `promote_all` (multiple artifacts), use a list:

```toml
[[step]]
name = "promote_all"
action = "promote_all"
promotes = ["REV_FILE", "MEM_FILE", "CLOSE_FILE"]
enable_notifications = true
onsuccess = "stepCompletion"
```

#### Terminal step

Every workflow must end with a `stepCompletion` step.

```toml
[[step]]
name = "stepCompletion"
action = "step_completion"
```

### Routing

| Field | Description |
|---|---|
| `onsuccess` | Step to run after approval |
| `on_reject_refine` | Refinement loop when a step is rejected |
| `on_exhaust_replan` | Replan fallback when refinement is exhausted |
| `requires_human_approval_after` | Gate step completion on human approval |

### Refinement loop

```toml
[step.on_reject_refine]
step = "refine_docs"
artifact = "MY_FOUNDATION_INDEX"
max_iterations = 2
exhausted_failure_code = "MY_REFINEMENT_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"
```

The loop route: `review → validate (rejected) → refine → (loop_returns_to) → review`.
Add `loop_returns_to = "review_docs"` on the refine step.

---

## `context_extensions.py` — Workflow Extension Interface

Every workflow package **must** have a `context_extensions.py` that
defines a `WorkflowExtensions` subclass. This is the workflow's plugin
interface — a single file that handles artifact path registration,
prompt context injection, and initialization hooks.

### Base Class

The base class lives at
`agent_runner_v2/workflow_packages/extensions_base.py` and provides
default no-op implementations for all hooks:

| Method | Purpose | When Called |
|--------|---------|-------------|
| `register_artifact_keys(job_id, mode)` | Return artifact key → path mappings | At workflow startup (CLI `run`) |
| `build_context_extensions(state, step, step_cfg, ctx, project_root)` | Return prompt context variables | Before each step's prompt is rendered |
| `init(workspace_root, runner_home)` | One-time environment setup | At CLI `init` |

### Example

```python
"""Context extensions for my_workflow_v1."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions
from agent_runner_v2.runtime_context import get_workspace_root, get_runner_home


class MyWorkflowExtensions(WorkflowExtensions):
    """Workflow extension hooks for my_workflow_v1."""

    workflow_name = "my_workflow_v1"

    def register_artifact_keys(self, *, job_id: str, mode: str) -> dict[str, str]:
        """Declare artifact paths for the global registry."""
        date_str = dt.datetime.now().strftime("%Y%m%d")
        run_root = f"docs/repo/my_workflow/runs/{job_id}"
        return {
            "MY_OUTPUT": f"{run_root}/MY-OUTPUT-{date_str}_{{slug}}.md",
            "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-review.md",
        }

    def build_context_extensions(
        self, *, state, step, step_cfg, ctx, project_root=None,
    ) -> dict[str, str]:
        """Inject absolute paths and metadata into prompt context."""
        result: dict[str, str] = {}

        # Governance roots (global paths)
        runner_home = get_runner_home()
        if runner_home:
            result["GOVERNANCE_RUNTIME_ROOT"] = str(
                Path(runner_home) / "bundles" / "core" / "current" / "foundation"
            )

        # Resolve artifact paths to absolute
        workspace_root = Path(project_root or get_workspace_root() or Path.cwd())
        job_id = state.get("job_id", "unknown")
        for key, rel_path in self.register_artifact_keys(job_id=job_id, mode="").items():
            resolved = rel_path.replace("{slug}", job_id)
            result[key] = str(workspace_root / resolved)

        return result
```

### Key Rules

1. **`register_artifact_keys()` replaces `output_paths.py`** — all
   path templates are declared here. The returned dict is merged into
   the global `ARTIFACT_PATHS` registry at startup.

2. **`build_context_extensions()` must resolve to absolute paths** —
   prompt placeholders like `{MY_OUTPUT}` are replaced with the values
   returned here. Always use absolute paths.

3. **Shared constants** — use constants from `constants.py` (e.g.
   `SDLC_DELIVERY_BASE`) instead of hardcoding base paths.

4. **Loop-able artifacts** — use `loop_iteration` parameter to append
   `_iter{N}` suffixes for review/validation/audit paths so refinement
   passes don't overwrite previous outputs.

---

## `actions.py` — Custom Actions

Register action functions with the `@action()` decorator.

```python
from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action

@action("validate_docs")
def validate_docs(*, context, state, step_cfg, project_root):
    # ... validation logic ...
    if failed:
        return ActionResult(
            status="REJECTED",
            remark=f"Validation failed: {len(failed)} checks.",
            artifacts={"MY_VALIDATION_REPORT": report_path},
            reject_code="VALIDATION_FAILED",
        )
    return ActionResult(
        status="APPROVED",
        remark="Validation passed.",
        artifacts={"MY_VALIDATION_REPORT": report_path},
    )
```

**Returning REJECTED** triggers the `on_reject_refine` routing.
**Returning APPROVED** advances to `onsuccess`.

**Terminal actions** that set `job_status = "COMPLETED"` (like `step_completion`)
must NOT include their own backend sync — the daemon handles that after the
child process exits.

---

## Prompt Templates

Prompt files are plain `.txt` files in `prompts/`. Use `{ARTIFACT_KEY}`
placeholders — the runner resolves them to absolute paths via
`context_extensions.py`.

**Critical rule:** Use bare `{ARTIFACT_KEY}` placeholders for paths that the
coder must read or write. Never wrap them in backticks like
`` `{ARTIFACT_KEY}` `` — backticks make the text literal, so the runner
will NOT resolve the placeholder and the coder will see the key name
instead of the actual file path.

```
Objective

Generate the staged output document set for `my_workflow_v1`.

Reference Inputs

- Read {MY_REFERENCE_INPUT}.
- Read Layer 1 governance at {GOVERNANCE_RUNTIME_ROOT}.

Artifacts

Write the required outputs to these paths:

- {MY_FOUNDATION_INDEX}
- {MY_LAYER_MODEL}

Required Frontmatter

Each output must include YAML frontmatter with:

- `template_id`
- `version`
- `doc_type: "system"`
- `authority: "workflow-generated"`
- `layer: "layer1"`
- `lifecycle_status: "draft"`

Output Instructions

- Write complete markdown files.
- Use ASCII only.
```

## Backend Sync

After creating or modifying a workflow, sync it to the backend registry:

```bash
ukbe-run-agent sync-workflows my_workflow_v1
```

This:
1. Validates the workflow bundle locally
2. POSTs the definition to the backend
3. Backend registers all artifact types from `bundle_governance.toml`
4. Backend creates/updates step definitions and routing rules

**Always sync after changing `bundle_governance.toml`** — new artifact keys
must be registered before any run produces them.

---

## Artifact Key Registration

**You do NOT need to register artifact keys in `constants.py` or
`artifact_keys.py`.** The runner automatically accepts any artifact key
declared in your workflow package.

### How it works

When `create_job()` runs, it builds the valid artifact key set by merging:

1. **Global keys** from `constants.py` (shared keys like `REVIEW_FILE_SUGGESTED`)
2. **Step-declared keys** — all `produces`, `required_inputs`, `optional_inputs`,
   `target_artifact`, `promotes`, `result_meta_key`, `source`, and `dest` values
   from every step in `workflow.toml`
3. **Governance registry keys** — all `[[artifact]]` keys from
   `bundle_governance.toml`

This means any key you use in your `workflow.toml` steps is automatically
valid for seed validation (`--set KEY=PATH`), job state tracking, and
context resolution — with zero changes to global files.

### What this means for developers

| Action | Required? |
|---|---|
| Declare keys in `workflow.toml` step `produces`/`required_inputs` | **Yes** — this is how the runner discovers your keys |
| Declare keys in `bundle_governance.toml` `[[artifact]]` | **Yes** — this is the canonical registry for backend sync |
| Declare keys in `register_artifact_keys()` in `context_extensions.py` | **Yes** — maps keys to filesystem paths for context resolution |
| Add keys to `constants.py` or `artifact_keys.py` | **No** — workflow keys are auto-accepted |

### Example

If your workflow has a step that produces `MY_CUSTOM_OUTPUT`:

```toml
# workflow.toml
[[step]]
name = "generate_output"
prompt = "prompts/01_generate.txt"

[step.artifacts]
produces = ["MY_CUSTOM_OUTPUT"]
result_meta_key = "MY_CUSTOM_OUTPUT"
```

The key `MY_CUSTOM_OUTPUT` is immediately valid. You can seed it via
`--set MY_CUSTOM_OUTPUT=/path/to/file`, reference it in prompts as
`{MY_CUSTOM_OUTPUT}`, and track it in job state — all without touching
any global registration file.

### When to add keys to `artifact_keys.py`

Only add keys to the global `artifact_keys.py` when:

- The key is **shared across multiple workflows** (e.g., `REVIEW_FILE_SUGGESTED`)
- The key needs a **centralized path mapping** in `known_artifact_paths()`
- The key is used by **core runner logic** outside any specific workflow

For workflow-specific keys, keep them in your workflow package only.

---

## Conventions

1. **`context_extensions.py` is mandatory.** Every workflow package
   must implement `WorkflowExtensions` from
   `agent_runner_v2.workflow_packages.extensions_base`. This is the
   single interface file — no separate `output_paths.py`. See the
   "Workflow Extension Interface" section above.

2. **Artifact keys are workflow-owned.** Declare them in `workflow.toml`
   step fields (`produces`, `required_inputs`) and in
   `bundle_governance.toml` `[[artifact]]` entries. The runner auto-discovers
   them — do NOT add workflow-specific keys to `constants.py` or
   `artifact_keys.py`. Only shared cross-workflow keys (like
   `REVIEW_FILE_SUGGESTED`) belong in the global registry.

3. **Use shared base path constants.** SDLC workflows must use
   `SDLC_DELIVERY_BASE` from `constants.py` instead of hardcoding
   `"docs/repo/agent_runner/sdlc/delivery"` in each workflow.

4. **Path templates use `<job_id>` placeholder** — the runner resolves it
   at runtime from the active job ID.

5. **Loop-able artifacts (review, validation, audit) must use iteration
   suffixes** via `loop_iteration` parameter in `register_artifact_keys()`
   to preserve per-pass outputs.

6. **Terminal step (`stepCompletion`)** is required at the end of every
   workflow. It must use the shared `step_completion` action.

7. **Three copies** of the workflow package exist in the repo:
   - `workflows/<name>/` — primary development copy
   - `agent_runner_v2/bootstrap/workflows/default/<name>/` — packaged bundle
   - `docs/system/00_governance/bootstrap/workflows/<name>/` — published source

   Keep all three in sync after changes.

8. **All injected path placeholders must use absolute paths** — relative
   paths break when the daemon runs from a different working directory.

9. **Use ASCII only in generated documents** — the deterministic validator
   rejects non-ASCII characters.

10. **Prompt placeholders must be bare `{KEY}`** — never `` `{KEY}` ``.
    Backtick-wrapped placeholders are literal text and will NOT be resolved
    by the runner. The coder needs actual file paths, not key names.

11. **`promotes` key must be top-level in `[[step]]`** — for promote steps
    using `promote_artifact` or `promote_all` actions, the `promotes` key
    MUST be placed at the top level of `[[step]]`, NOT under
    `[step.artifacts]`. The TOML loader silently drops unknown fields from
    `[step.artifacts]` — only top-level unknown keys are captured by the
    `extra` passthrough dict and reach the action's `step_cfg`.

---

## Extending the Workflow Interface

When a new cross-cutting feature is needed that all (or some) workflows
must handle, add a new hook method to the interface. **Do NOT create
new file types or new discovery mechanisms.**

### Steps to Add a New Hook

1. **Add method to `WorkflowExtensions` base class** in
   `extensions_base.py` with a default no-op implementation:

   ```python
   def on_job_complete(self, *, state, project_root) -> None:
       """Called when a workflow job completes."""
       pass
   ```

2. **Add scanner function in `hooks.py`**:

   ```python
   def notify_all_job_completions(*, state, project_root) -> None:
       """Call on_job_complete() on all workflows."""
       scan_all("on_job_complete", state=state, project_root=project_root)
   ```

3. **Wire to CLI command** in `run_agent.py` at the appropriate point.

4. **Implement in workflows that need it** — override the method in
   their `context_extensions.py` subclass. Workflows that don't care
   inherit the no-op default.

### Example: Adding a Validation Hook

```python
# 1. extensions_base.py
def validate_environment(self, *, workspace_root) -> list[str]:
    """Return list of validation errors. Empty = pass."""
    return []

# 2. hooks.py
def validate_all_environments(*, workspace_root) -> dict[str, list[str]]:
    """Call validate_environment() on all workflows. Return failures."""
    return scan_all("validate_environment", workspace_root=workspace_root)

# 3. run_agent.py — wire to init or pre-run check

# 4. Workflow implementation
class MyWorkflowExtensions(WorkflowExtensions):
    def validate_environment(self, *, workspace_root):
        errors = []
        if not (workspace_root / "required_folder").is_dir():
            errors.append("required_folder/ missing")
        return errors
```
