---
template_id: SYS-02-BAC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 bundle authoring contract; defines the contract every Layer 3 bundle must satisfy"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-002"
---

# Bundle Authoring Contract

## Overview

This document defines the contract every Layer 3 workflow bundle must
satisfy to run on the agent-runner-v2 platform. It covers required files,
the `workflow.toml` manifest format, artifact key conventions, bundle
governance requirements, and metadata compliance.

Layer 3 bundles must operate within this contract. They must not modify
Layer 1 ecosystem governance or this Layer 2 platform constitution.

## Required Bundle Files

Every Layer 3 workflow bundle is a self-contained directory with the
following structure:

```
workflows/<bundle_name>/
+-- workflow.toml              # Required: Step manifest, routing, coder config
+-- prompts/                   # Required: Prompt template .txt files
+-- actions.py                 # Optional: Custom action implementations
+-- context_extensions.py      # Optional: Workflow-specific context injection
+-- output_paths.py            # Optional: Workflow-owned path contracts
+-- bundle_governance.toml     # Required: Bundle governance declaration
+-- bundle_governance/         # Required: Bundle governance package
    +-- core_governance.md     #   Bundle purpose, scope, anti-drift rules
    +-- prompt_sop.md          #   Prompt authoring standards
    +-- prompt_layout.md       #   Prompt section structure
    +-- action_policy.md       #   Allowed and forbidden action types
    +-- review_audit_contract.md # Review and audit obligations
    +-- prompt_contract.json   #   Machine-checkable prompt constraints
```

### File Purpose

| File | Required | Purpose |
|---|---|---|
| `workflow.toml` | Yes | Declares workflow identity, steps, routing, coder policies, and artifact contracts. |
| `prompts/` | Yes | Contains prompt template `.txt` files, one per prompt-driven step. Templates use `{PLACEHOLDER}` syntax for context variable injection. |
| `actions.py` | Conditional | Defines custom action functions for action-driven steps. Required only if the bundle uses custom actions beyond the platform action library. |
| `context_extensions.py` | Optional | Defines a `build_context_extensions()` function that injects workflow-specific variables into the prompt rendering context. |
| `output_paths.py` | Optional | Defines a `build_output_paths()` function that returns a dict of artifact key to output path mappings for workflow-owned artifacts. |
| `bundle_governance.toml` | Yes | Declares governance adapter targets and extensions for the bundle. |
| `bundle_governance/` | Yes | Contains the six bundle-governance files listed above. |

## workflow.toml Format

The `workflow.toml` manifest is a TOML file with these top-level sections:

### `[workflow]`

```toml
[workflow]
name = "my_bundle_v1"
version = "1.0"
label = "My Workflow Bundle"
job_prefix = "MYB"
visibility = "normal"
default_max_rejects = 3
init_step = "generate_docs"
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique bundle identifier. Used as the `--template-group` value. |
| `version` | Yes | Semantic version string. |
| `label` | No | Human-readable bundle name. |
| `job_prefix` | Yes | Short prefix for job IDs (e.g., `MYB`). |
| `visibility` | No | `"normal"` or `"hidden"`. Defaults to `"normal"`. |
| `default_max_rejects` | No | Default refinement budget (overridable per step). |
| `init_step` | Yes | Name of the first step to execute. |

### `[[step]]`

Each step is declared as a TOML array of tables. A step may be
prompt-driven or action-driven.

```toml
[[step]]
name = "generate_docs"
prompt = "prompts/generate.txt"
onsuccess = "review_docs"
requires_human_approval_after = false
enable_notifications = true
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique step name within the workflow. |
| `prompt` | Conditional | Path to prompt template file (prompt-driven steps only). |
| `action` | Conditional | Registered action name (action-driven steps only). |
| `mode` | No | `"normal"` or `"manual"`. Overrides the workflow-level mode when set. |
| `onsuccess` | No | Name of the next step on approval. |
| `requires_human_approval_after` | No | If `true`, pauses for human approval after step completion. Default `false`. |
| `enable_notifications` | No | If `true`, sends notifications for this step. Default `false`. |

### `[step.artifacts]`

```toml
[step.artifacts]
produces = ["GENERATED_DOCS"]
required_inputs = ["LAYER1_GOVERNANCE_SET"]
optional_inputs = ["CODEBASE_INVENTORY"]
result_meta_key = "GENERATED_DOCS_METAJSON"
target_artifact = "GENERATED_DOCS"
edit_mode = "replace"
```

| Field | Required | Description |
|---|---|---|
| `produces` | No | List of artifact keys this step produces. |
| `required_inputs` | No | List of artifact keys that must exist before this step runs. |
| `optional_inputs` | No | List of artifact keys that may optionally exist. |
| `result_meta_key` | No | Context key under which the step's meta.json path is injected. |
| `target_artifact` | No | For refine steps, the artifact being refined. |
| `edit_mode` | No | `"replace"` or `"edit"`. Controls how the coder should modify the target artifact. |

### `[step.coder]`

```toml
[step.coder]
role_policy = "architect_standard"
must_differ = false
allowed_roles = ["architect", "architect_alt"]
```

| Field | Required | Description |
|---|---|---|
| `role_policy` | Yes | Role policy name (e.g., `"architect_standard"`, `"reviewer_standard"`). |
| `must_differ` | No | If `true`, the coder must differ from the previous step's coder. Default `false`. |
| `allowed_roles` | No | List of specific roles allowed from the policy. If empty, all policy roles are allowed. |

### `[step.on_reject_refine]`

```toml
[step.on_reject_refine]
refine_step = "refine_docs"
artifact = "REVIEW_FILE_SUGGESTED"
max_iterations = 3
exhausted = { failure_code = "REFINE_EXHAUSTED" }
```

| Field | Required | Description |
|---|---|---|
| `refine_step` | Yes | Name of the refine step to route to on rejection. |
| `artifact` | No | Artifact key for the review finding to pass to the refine step. |
| `max_iterations` | No | Maximum refinement iterations before exhaustion. |
| `exhausted` | No | Table with `failure_code` value used when refinement is exhausted. |

### `[step.on_exhaust_replan]`

```toml
[step.on_exhaust_replan]
replan_step = "replan_docs"
replan_artifact = "REVIEW_FILE_SUGGESTED"
```

| Field | Required | Description |
|---|---|---|
| `replan_step` | Yes | Name of the replan step. |
| `replan_artifact` | No | Artifact key passed to the replan step. |

### `[step.reject_code_routes]`

```toml
[step.reject_code_routes]
LAYER1_REDEFINITION = { route = "fail" }
METADATA_NONCOMPLIANCE = { route = "refine" }
```

Maps rejection codes to routing decisions (`"refine"` or `"fail"`).

## Artifact Key Conventions

Artifact keys are semantic identifiers used throughout the platform to
reference named outputs. They are defined in `artifact_keys.py` and
resolved to paths via `known_artifact_paths()` in `constants.py`.

### Key Naming

Artifact keys use `UPPER_SNAKE_CASE` and follow this naming convention:

- `ARTIFACT_KEY_<PURPOSE>` for canonical platform keys
- Workflow-specific keys use the pattern defined in the workflow's artifact registry

### Key Usage

Artifact keys appear in:

1. `workflow.toml` step `produces`, `required_inputs`, `optional_inputs` fields
2. Prompt templates as `{ARTIFACT_KEY_*}` placeholders
3. `bundle_governance.toml` artifact registry
4. `output_paths.py` return dict keys
5. `meta.json` sidecar `artifacts` dict

### Path Resolution

Artifact paths are resolved by the platform through the layered constants
system: `artifact_keys.py` (keys) -> `path_primitives.py` (roots/helpers)
-> `path_catalog.py` (computed mappings). Bundle authors should not
hardcode paths; they should use artifact keys and let the platform resolve
them.

### Workflow-Owned Artifacts

Workflow bundles declare their owned artifacts in:

1. `output_paths.py` via `build_output_paths()` returning a dict of
   `{artifact_key: relative_path}` mappings.
2. `bundle_governance.toml` artifact registry listing all artifacts the
   bundle owns or references.

## Bundle Governance Requirements

Every Layer 3 bundle must include a `bundle_governance/` package with
these six files:

### `core_governance.md`

Defines the bundle's purpose, owning layer, permitted artifact classes,
permanent versus temporary artifact rules, and anti-drift policy. Must
include:

- Bundle purpose
- Owning layer
- Permitted artifact classes
- Permanent versus temporary artifact rule
- Prohibition on redefining higher-layer governance

### `prompt_sop.md`

Defines prompt authoring standards for the bundle. Must include:

- Prompt authoring principles
- Scope discipline rules
- Required citation behavior for review and audit prompts
- Refinement constraints
- Prompt-change review expectations

### `prompt_layout.md`

Defines the standard structure for prompts in this bundle. Must include
guidance for sections such as objective, layer boundary, required inputs,
artifact responsibilities, acceptance criteria, rejection criteria, and
output instructions.

### `action_policy.md`

Defines allowed and forbidden action types for the bundle. Must include:

- Allowed action types (from the platform action library and bundle-local actions)
- Forbidden action types (e.g., mutating platform code, performing automated codebase scanning)
- Required separation between generation and code mutation

### `review_audit_contract.md`

Defines review and audit obligations for the bundle. Must include:

- Defect classes the review must detect
- What review must reject
- What audit must verify
- Routing expectations for refine versus fail

### `prompt_contract.json`

Defines machine-checkable prompt constraints. Must validate at least:

- Required prompt files exist
- Prompts contain required sections or markers
- Review and audit prompts contain explicit rejection logic
- Refine prompt contains no instructions that normalize lower-layer drift

## Metadata Compliance

All outputs produced by Layer 3 bundles must comply with the metadata
standards defined in:

- Layer 1 Metadata Standard (`METADATA_STANDARD.md`, template `SYS-00-MS`)
- This platform's Metadata Contract (`METADATA_CONTRACT.md`, template `SYS-02-MC`)

### Required Fields

Every governed document must carry YAML frontmatter with at least:

- `doc_type` - one of the Layer 1 baseline or platform-specific values
- `authority` - ownership source (`workflow-generated`, `bundle-owned`, or `derived`)
- `scan_policy` - `include`, `conditional`, or `exclude`
- `scan_reason` - human-readable explanation for the scan policy

Platform-specific fields (`template_id`, `platform`, `managed_by`) should
be included where applicable.

### Lifecycle Status

Bundle outputs must declare `lifecycle_status` in frontmatter:

- Staged (draft) outputs: `"draft"`
- Published (active) outputs: `"published"`

The publish action sets the lifecycle status to `"published"`.
