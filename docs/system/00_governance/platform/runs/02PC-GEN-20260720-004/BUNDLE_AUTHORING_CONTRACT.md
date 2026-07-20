---
template_id: SYS-02-BAC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 bundle authoring contract; defines Layer 3 compliance requirements"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-004"
managed_by: workflow-generated
---

# Bundle Authoring Contract

## Purpose

This document defines the contract every Layer 3 workflow bundle must
satisfy to run on agent-runner-v2. It specifies required bundle files,
the `workflow.toml` manifest format, artifact key conventions, bundle
governance requirements, and metadata compliance rules.

This contract is the platform-level standard. Individual bundles may
add bundle-local constraints, but they must not weaken or contradict
the requirements defined here.

## Required Bundle Files

A conformant workflow bundle is a directory containing at minimum:

| File | Required | Description |
|---|---|---|
| `workflow.toml` | Yes | The workflow manifest defining steps, artifacts, coder roles, and routing. |
| `prompts/` | Conditional | Directory containing `.txt` prompt templates. Required if the bundle has any prompt-driven steps. |
| `actions.py` | Conditional | Custom action implementations. Required if the bundle defines action-driven steps with bundle-local logic. |
| `context_extensions.py` | No | Optional module providing `build_context_extensions()` for workflow-specific context injection. |
| `output_paths.py` | No | Optional module providing `build_output_paths()` for workflow-owned path contracts. |
| `bundle_governance/` | No | Optional directory containing bundle governance extensions. When present, the bundle carries its own governance contract. |

### `workflow.toml`

The manifest is the single source of truth for the workflow definition.
It is parsed by `workflow_packages/loader.py` using `load_workflow_package()`
and adapted into the same dict shape consumed by the runner.

### `prompts/`

Each prompt-driven step references a `.txt` file in this directory.
Prompt files are rendered with context variables before being sent to
the coder. Placeholder resolution uses `ARTIFACT_KEYS` and
`known_artifact_paths()` from `constants.py`.

### `actions.py`

Bundle-local actions are registered using the `@action()` decorator
from `workflow_packages/actions/__init__.py`. When the bundle is loaded,
the loader imports `actions.py`, which triggers the decorator and
registers the functions in the global `REGISTERED_ACTIONS` dict.

### `context_extensions.py`

When present, this module must export a `build_context_extensions()`
function. The runner calls it during context building to inject
workflow-specific variables into the prompt rendering context.

### `output_paths.py`

When present, this module must export a `build_output_paths()` function.
The runner uses it to resolve workflow-owned output path contracts.

## workflow.toml Format

The manifest uses TOML syntax and is organized into these sections:

### `[workflow]` Section

Top-level workflow metadata:

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique workflow identifier. |
| `version` | Yes | Workflow version string. |
| `label` | Yes | Human-readable display label. |
| `job_prefix` | Yes | Prefix for generated job IDs. |
| `visibility` | No | Visibility scope (e.g., `public`, `internal`). |
| `default_max_rejects` | No | Maximum rejection count before failure (default: 3). |
| `init_step` | Yes | Name of the first step to execute. |
| `description` | No | Human-readable workflow description. |

### `[[step]]` Sections

Each step is a `[[step]]` array entry:

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique step name within the workflow. |
| `prompt` | Conditional | Prompt template filename (relative to `prompts/`). Required for prompt-driven steps. |
| `action` | Conditional | Action name to invoke. Required for action-driven steps. |
| `mode` | No | Execution mode override. |
| `onsuccess` | No | Name of the next step on success. |
| `requires_human_approval_after` | No | Boolean. If true, pauses for human approval after this step. |
| `enable_notifications` | No | Boolean. If true, sends notifications for this step. |

### `[step.artifacts]` Section

Defines the artifact contract for the step:

| Field | Required | Description |
|---|---|---|
| `produces` | No | List of artifact keys this step produces. |
| `required_inputs` | No | List of artifact keys that must exist before this step runs. |
| `optional_inputs` | No | List of artifact keys used if available. |
| `result_meta_key` | No | Key in meta.json that carries the step result. |
| `target_artifact` | No | Primary artifact key for this step's output. |
| `edit_mode` | No | Edit behavior for the target artifact. |

### `[step.coder]` Section

Configures coder selection for prompt-driven steps:

| Field | Required | Description |
|---|---|---|
| `role_policy` | No | Role policy name (e.g., `architect_standard`). |
| `default` | No | Default coder connection name. |
| `allowed` | No | List of allowed coder connections. |
| `default_role` | No | Default coder role. |
| `allowed_roles` | No | List of allowed coder roles. |
| `must_differ` | No | Boolean. If true, the coder must differ from the previous step's coder. |

### `[step.on_reject_refine]` Section

Configures refinement loop behavior:

| Field | Required | Description |
|---|---|---|
| `refine_step` | Yes | Name of the refinement step. |
| `artifact` | Yes | Artifact key to refine. |
| `max_iterations` | No | Maximum refinement iterations before exhaustion. |
| `exhausted_failure_code` | No | Failure code when refinement is exhausted. |

### `[step.on_exhaust_replan]` Section

Configures replan behavior when refinement is exhausted:

| Field | Required | Description |
|---|---|---|
| `replan_step` | Yes | Name of the replan step. |
| `artifact` | Yes | Artifact key to replan. |

## Artifact Key Conventions

Artifact keys are canonical identifiers defined in `artifact_keys.py`
as `ARTIFACT_KEY_*` constants. They flow through the layered constant
system:

1. `artifact_keys.py` -- defines canonical key literals
2. `path_primitives.py` -- defines stable filename and root constants
3. `path_catalog.py` -- provides `known_artifact_paths()` mapping keys
   to filesystem paths
4. `constants.py` -- re-exports everything as the single source of
   truth

### Key Rules

- Artifact keys use uppercase snake_case (e.g., `REVIEW_FILE_SUGGESTED`,
  `CODEBASE_INVENTORY`, `DELIVERY_AGENTS`)
- Keys are defined as constants, never hardcoded in production code
- Path resolution uses `known_artifact_paths()`, not string concatenation
- Prompt templates use `{ARTIFACT_KEY_*}` placeholders that resolve
  against the constant system
- The runner auto-corrects common LLM mistakes in artifact key naming
  (e.g., double suffixes like `_SUGGESTED_SUGGESTED`)

### Artifact Path Resolution

Artifact paths are resolved at runtime by `runtime_context.py` using
`resolve_repo_or_runtime_path()`. This function checks whether an
artifact exists in the job state first, then falls back to the known
artifact path catalog.

## Bundle Governance Requirements

When a bundle includes a `bundle_governance/` directory, the governance
package is loaded by `bundle_governance.py` via
`load_bundle_governance()`. The governance package may include:

| File | Purpose |
|---|---|
| `core_governance.md` | Bundle purpose, owning layer, permitted artifact classes. |
| `prompt_sop.md` | Prompt authoring principles and scope discipline. |
| `prompt_layout.md` | Required prompt sections and structure guidance. |
| `action_policy.md` | Allowed and forbidden action types. |
| `review_audit_contract.md` | Defect classes, routing policy, review obligations. |
| `prompt_contract.json` | Machine-checkable prompt constraints. |

### Governance Adapter Generation

The `bundle_governance.py` module generates adapter files (e.g.,
`AGENTS.md`, `CLAUDE.md`, `QWEN.md`) from the governance package. These
adapters inject governance context into coder prompts so the LLM
operates within the bundle's governance constraints.

### Governance Extensions

The `BundleGovernance` dataclass (in `workflow_packages/base.py`)
carries:

- `adapter_targets` -- list of adapter file targets to generate
- `extensions` -- list of `GovernanceExtension` entries
- `artifact_registry` -- list of `GovernanceArtifact` entries
- `include_in_prompts` -- whether governance content is injected into
  prompts

## Metadata Compliance

All documents produced by Layer 3 bundles must comply with:

1. **Layer 1 metadata baseline** -- required fields defined in the
   Layer 1 Metadata Standard (`METADATA_STANDARD.md`):
   - `doc_type` -- from the allowed vocabulary
   - `authority` -- from the allowed vocabulary
   - `scan_policy` -- from the allowed vocabulary
   - `scan_reason` -- non-empty when scan_policy is `exclude` or
     `conditional`

2. **Layer 2 platform extensions** -- additional fields and values
   defined in this platform's Metadata Contract (`METADATA_CONTRACT.md`):
   - `layer: "layer2"` or `"layer3"` as appropriate
   - `platform: "agent-runner-v2"`
   - platform-specific `doc_type` and `authority` extensions

3. **Lifecycle tracking** -- permanent documents must carry:
   - `template_id` -- matching the document's template definition
   - `version` -- document version
   - `lifecycle_status` -- current state (`draft`, `published`, etc.)
   - `effective_version` -- run or change identifier
   - `managed_by` -- for workflow-generated documents

### Authority Constraints

- Bundle outputs must not claim `human-authored` authority if they are
  workflow-generated
- Bundle outputs must not claim Layer 1 or Layer 2 constitutional
  authority
- Bundle outputs may use `bundle-owned` or `workflow-generated` authority
- Derived artifacts must use `derived` authority

### Scan Policy Expectations

- Bundle definitions should use `scan_policy: "include"` or
  `"conditional"`
- Review, validation, and audit artifacts should use
  `scan_policy: "conditional"` or `"exclude"`
- All documents with `scan_policy: "exclude"` or `"conditional"` must
  provide a non-empty `scan_reason`
