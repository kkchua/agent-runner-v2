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
effective_version: "02PC-GEN-20260720-001"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
> This file is workflow-generated and protected from manual edits.

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

### Required Files Summary

| File | Required | Purpose |
|---|---|---|
| `workflow.toml` | Yes | Declarative step manifest, routing, and coder configuration. |
| `prompts/` | Yes | Directory containing prompt template `.txt` files, one per prompt-driven step. |
| `bundle_governance.toml` | Yes | Bundle governance declaration: metadata, platform, layer. |
| `bundle_governance/` | Yes | Bundle-governance package governing the bundle's own authoring and maintenance. |
| `actions.py` | No | Custom action implementations for action-driven steps. Required if the bundle uses custom actions. |
| `context_extensions.py` | No | Workflow-specific context injection hook (`build_context_extensions()`). Required if the bundle needs custom context variables. |
| `output_paths.py` | No | Workflow-owned path contracts. Required if the bundle defines custom artifact paths. |

## workflow.toml Format

The `workflow.toml` manifest defines the workflow's steps, routing, coder
configuration, and artifact contracts. It is the primary declarative
configuration file for the bundle.

### `[workflow]` Section

```toml
[workflow]
name = "my_workflow_v1"
version = "1.0.0"
label = "My Workflow"
job_prefix = "MW"
visibility = "public"
default_max_rejects = 3
init_step = "generate_docs"
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Bundle identifier. Must match the directory name. |
| `version` | Yes | Semantic version of the workflow definition. |
| `label` | Yes | Human-readable label for UI display. |
| `job_prefix` | Yes | Short prefix for auto-generated job IDs (2-4 uppercase characters). |
| `visibility` | No | `public` or `private`. Default: `public`. |
| `default_max_rejects` | No | Default reject budget for steps without explicit configuration. Default: 3. |
| `init_step` | Yes | Name of the first step to execute. |

### `[[step]]` Section

```toml
[[step]]
name = "generate_docs"
prompt = "prompts/generate.txt"
mode = "default"
on_success = "review_docs"
requires_human_approval_after = false
enable_notifications = true
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Step name. Must be unique within the workflow. |
| `prompt` | Conditional | Path to the prompt template file (relative to bundle root). Required for prompt-driven steps. |
| `action` | Conditional | Action name for action-driven steps. Mutually exclusive with `prompt`. |
| `mode` | No | Execution mode hint. `default` for normal execution. |
| `on_success` | Yes | Name of the next step when this step reports `APPROVED`. |
| `requires_human_approval_after` | No | If `true`, pause for human approval after step completion before routing. |
| `enable_notifications` | No | If `true`, send notifications for this step. |

### `[step.artifacts]` Section

```toml
[step.artifacts]
produces = ["MY_OUTPUT", "MY_META"]
required_inputs = ["LAYER1_GOVERNANCE_README"]
optional_inputs = ["CONTEXT_INVENTORY"]
result_meta_key = "MY_OUTPUT"
target_artifact = "MY_OUTPUT"
edit_mode = "replace"
```

| Field | Required | Description |
|---|---|---|
| `produces` | Yes | List of artifact keys this step creates. |
| `required_inputs` | No | Artifact keys that must exist before this step runs. |
| `optional_inputs` | No | Artifact keys that may exist but are not required. |
| `result_meta_key` | No | The artifact key whose path is recorded as the primary result. |
| `target_artifact` | No | Artifact key the coder should write to when `edit_mode` is set. |
| `edit_mode` | No | `replace` (overwrite) or `append`. Only valid with `target_artifact`. |

### `[step.coder]` Section

```toml
[step.coder]
role_policy = "architect_standard"
must_differ = false
allowed_roles = ["architect", "architect_alt"]
default_role = "architect"
```

| Field | Required | Description |
|---|---|---|
| `role_policy` | Yes | Role policy name from `role_policies.json`. |
| `must_differ` | No | If `true`, the coder must differ from the previous step's coder. |
| `allowed_roles` | No | Explicit list of allowed role names. Overrides the policy's default. |
| `default_role` | No | Default role when the policy allows multiple. |

### `[step.on_reject_refine]` Section

```toml
[step.on_reject_refine]
refine_step = "refine_docs"
artifact = "REVIEW_FILE_SUGGESTED"
max_iterations = 3
exhausted = { failure_code = "REFINE_EXHAUSTED" }
```

| Field | Required | Description |
|---|---|---|
| `refine_step` | Yes | Step name to route to on rejection for refinement. |
| `artifact` | Yes | Artifact key carrying review findings for the refine step. |
| `max_iterations` | Yes | Maximum refinement loop iterations before exhaustion. |
| `exhausted` | Yes | Object with `failure_code` for when refinement is exhausted. |

### `[step.on_exhaust_replan]` Section

```toml
[step.on_exhaust_replan]
replan_step = "replan_docs"
replan_artifact = "REVIEW_FILE_SUGGESTED"
```

| Field | Required | Description |
|---|---|---|
| `replan_step` | Yes | Step name to route to when refinement is exhausted. |
| `replan_artifact` | Yes | Artifact key carrying context for the replan step. |

### `[step.reject_code_routes]` Section

```toml
[step.reject_code_routes]
LAYER1_REDEFINITION = { route = "fail" }
METADATA_NONCOMPLIANCE = { route = "refine" }
MISSING_SECTION = { route = "refine" }
```

Maps specific rejection codes to routing actions. `route` may be:

- `"fail"` - terminate the workflow with the code as failure reason
- `"refine"` - route to the configured refine step

## Artifact Key Conventions

### Canonical Artifact Keys

Artifact keys are string constants defined in `agent_runner_v2/artifact_keys.py`
and re-exported through `agent_runner_v2/constants.py`. They use the naming
convention `ARTIFACT_KEY_<NAME>`.

**Platform-level keys** (defined by the platform):

- `REVIEW_FILE_SUGGESTED` - Review findings artifact
- `DELIVERY_AGENTS` - Delivery agent contracts
- `CODEBASE_INVENTORY` - Codebase inventory artifact

**Workflow-specific keys** (defined by each bundle):

Bundles define their own artifact keys in the `produces` and
`required_inputs` lists in `workflow.toml`. These are resolved to file
paths by the workflow's `output_paths.py` or by the platform's
`known_artifact_paths()` function.

### Placeholder Syntax

Prompt templates use `{ARTIFACT_KEY_NAME}` placeholders that are resolved
to absolute file paths at render time. For example, a prompt may contain:

```
Read the review findings at {REVIEW_FILE_SUGGESTED}.
```

The runner resolves this to the absolute path of the review artifact on
disk before sending the prompt to the coder.

### Key Naming Rules

1. Use uppercase snake_case: `MY_ARTIFACT_NAME`.
2. Keep keys unique within the workflow.
3. Do not reuse platform-level keys for bundle-specific artifacts.
4. Do not use `_METAJSON` as a suffix - the platform adds this
   automatically for meta context keys.

## Bundle Governance Requirements

### `bundle_governance.toml`

Every bundle must declare its governance contract in
`bundle_governance.toml`:

```toml
[bundle]
name = "my_workflow_v1"
layer = "layer3"
platform = "agent-runner-v2"
bundle_class = "workflow"
authority = "bundle-owned"

[governance]
canonical_source = "bundle_governance/core_governance.md"
generated_dir = "bundle_governance/generated"
adapter_targets = ["AGENTS.md", "QWEN.md", "CLAUDE.md"]
include_in_prompts = true
```

### `bundle_governance/` Package

The bundle governance package governs how the bundle itself is authored
and maintained. It must include:

1. **`core_governance.md`** - Bundle purpose, owning layer, permitted
   artifact classes, permanent vs. temporary artifact rules, prohibition
   on Layer 1 redefinition, prohibition on Layer 2 platform drift.
2. **`prompt_sop.md`** - Prompt authoring principles, scope discipline
   rules, required citation behavior for review and audit prompts,
   refinement constraints.
3. **`prompt_layout.md`** - Standard prompt section structure: objective,
   layer boundary, required inputs, artifact responsibilities, acceptance
   criteria, rejection criteria, output instructions.
4. **`action_policy.md`** - Allowed action types, forbidden action types,
   separation between generation and code mutation.
5. **`review_audit_contract.md`** - Defect classes, routing policy for
   refine vs. fail, minimum review and audit obligations.
6. **`prompt_contract.json`** - Machine-checkable constraints: required
   prompt files exist, prompts contain required sections, review/audit
   prompts contain explicit rejection logic.

## Metadata Compliance

### Required Frontmatter

Every permanent output document produced by a Layer 3 bundle must carry
YAML frontmatter with at least:

| Field | Required | Source |
|---|---|---|
| `doc_type` | Yes | Layer 1 baseline + Layer 2 extensions |
| `authority` | Yes | Layer 1 baseline + Layer 2 extensions |
| `scan_policy` | Yes | Layer 1 baseline |
| `scan_reason` | Yes | Layer 1 baseline |
| `layer` | Yes | Must be `"layer3"` for Layer 3 outputs |
| `platform` | Yes | Must be `"agent-runner-v2"` |
| `lifecycle_status` | Yes | From Layer 1 lifecycle model |
| `effective_version` | Conditional | Required for workflow-generated permanent docs |
| `template_id` | Conditional | Required for permanent documents matching a template |
| `managed_by` | Conditional | Required for workflow-generated documents |

### Metadata Inheritance

Layer 3 bundles inherit metadata rules from:

1. **Layer 1 baseline** - `doc_type`, `authority`, `scan_policy`,
   `scan_reason` field definitions and baseline vocabularies.
2. **Layer 2 platform extensions** - Platform-specific `doc_type` and
   `authority` values, additional frontmatter fields (`platform`,
   `template_id`, `managed_by`).

Layer 3 bundles must not modify Layer 1 baseline values or Layer 2
platform-specific values. They apply the inherited vocabulary to their
outputs.

### Bundle Output Classification

| Output Type | `doc_type` | `authority` | `scan_policy` |
|---|---|---|---|
| Permanent bundle outputs | `workflow_output` or `bundle_definition` | `workflow-generated` or `bundle-owned` | `include` |
| Review evidence | `review_artifact` | `workflow-generated` or `derived` | `conditional` |
| Validation evidence | `validation_artifact` | `workflow-generated` or `derived` | `conditional` |
| Audit evidence | `audit_artifact` | `workflow-generated` or `derived` | `conditional` |

Evidence artifacts must never be classified as permanent bundle outputs
or platform standards.
