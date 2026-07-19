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
├── actions.py                 # Custom @action functions (optional)
├── context_extensions.py      # Path resolution and prompt context injection
├── output_paths.py            # Workflow-owned path contracts (optional)
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
| `context_extensions.py` | Injects absolute artifact paths and reference inputs into prompt context |
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

## `context_extensions.py` — Path Resolution

Every workflow must provide a `build_context_extensions()` function that
injects absolute paths and metadata into the prompt rendering context.

```python
def build_context_extensions(*, state, step, step_cfg, ctx, project_root=None):
    job_id = state.get("job_id", "unknown")
    root = Path(project_root or Path.cwd()).resolve()
    output_paths = build_output_paths(job_id=job_id)

    extensions = {
        "MY_REFERENCE_INPUT": str(root / "path" / "to" / "reference.md"),
    }

    for key, rel_path in output_paths.items():
        if rel_path.endswith((".md", ".json")):
            extensions[key] = str(root / rel_path)

    return extensions
```

Use `build_output_paths()` to centralize path templates — keep the same
function in both `context_extensions.py` and `actions.py` for consistency.

**Path convention:** The `loop_iteration` parameter on `build_output_paths()`
appends `_iter{N}` suffixes to loop-able artifact paths (review, validation,
audit) so refinement passes don't overwrite previous iteration outputs.

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

```
Objective

Generate the staged output document set for `my_workflow_v1`.

Reference Inputs

- Read `{MY_REFERENCE_INPUT}`.

Artifacts

Write the required outputs:

- `{MY_FOUNDATION_INDEX}`
- `{MY_LAYER_MODEL}`

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

## Conventions

1. **Artifact keys must be declared once** in `bundle_governance.toml`.
   They appear in `workflow.toml` step `produces`/`inputs` and
   `context_extensions.py` `build_output_paths()`, but the
   `bundle_governance.toml` is the canonical registry.

2. **Path templates use `<job_id>` placeholder** — the runner resolves it
   at runtime from the active job ID.

3. **Loop-able artifacts (review, validation, audit) must use iteration
   suffixes** via `build_output_paths(loop_iteration=...)` to preserve
   per-pass outputs.

4. **Terminal step (`stepCompletion`)** is required at the end of every
   workflow. It must use the shared `step_completion` action.

5. **Three copies** of the workflow package exist in the repo:
   - `workflows/<name>/` — primary development copy
   - `agent_runner_v2/bootstrap/workflows/default/<name>/` — packaged bundle
   - `docs/system/00_governance/bootstrap/workflows/<name>/` — published source

   Keep all three in sync after changes.

6. **All injected path placeholders must use absolute paths** — relative
   paths break when the daemon runs from a different working directory.

7. **Use ASCII only in generated documents** — the deterministic validator
   rejects non-ASCII characters.
