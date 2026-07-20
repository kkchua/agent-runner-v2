---
template_id: SYS-02-BAC
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 bundle authoring contract; defines the contract every Layer 3 bundle must satisfy"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-20260720-fd35ddf1"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
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
    workflow.toml              (Required) Step manifest, routing, coder config
    prompts/                   (Required) Prompt template .txt files
    actions.py                 (Optional) Custom action implementations
    context_extensions.py      (Optional) Workflow-specific context injection
    output_paths.py            (Optional) Workflow-owned path contracts
    bundle_governance.toml     (Required) Bundle governance declaration
    bundle_governance/         (Required) Bundle governance package
        core_governance.md     Bundle purpose, scope, anti-drift rules
        prompt_sop.md          Prompt authoring standards
        prompt_layout.md       Prompt section structure
        action_policy.md       Allowed and forbidden action types
        review_audit_contract.md  Review and audit obligations
        prompt_contract.json   Machine-checkable prompt constraints
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
| `name` | Yes | Unique bundle name. Must match the directory name. |
| `version` | Yes | Semantic version string (e.g., `1.0.0`). |
| `label` | Yes | Human-readable display name. |
| `job_prefix` | Yes | Short prefix for job IDs (2-4 uppercase letters). |
| `visibility` | No | `public` or `private`. Default: `public`. |
| `default_max_rejects` | No | Default reject limit before failure. Default: `3`. |
| `init_step` | Yes | Name of the first step to execute. |

### `[[step]]` Section

```toml
[[step]]
name = "generate_docs"
prompt = "prompts/generate_docs.txt"
mode = "default"
onsuccess = "review_docs"
requires_human_approval_after = false
enable_notifications = true

[step.artifacts]
produces = ["MY_OUTPUT"]
required_inputs = ["REFERENCE_INPUT"]
result_meta_key = "MY_OUTPUT"
target_artifact = "MY_OUTPUT"
edit_mode = "create"

[step.coder]
role_policy = "architect_standard"
must_differ = false
allowed_roles = ["architect_standard", "refine_standard"]

[step.on_reject_refine]
refine_step = "refine_docs"
artifact = "MY_OUTPUT"
max_iterations = 3
exhausted = "REVIEW_EXHAUSTED"
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique step name within the workflow. |
| `prompt` | Conditional | Path to prompt template `.txt` file. Required for prompt-driven steps. |
| `action` | Conditional | Action name for action-driven steps. Required if `prompt` is absent. |
| `mode` | No | Execution mode hint. `default` for standard execution. |
| `onsuccess` | No | Next step name on `APPROVED` status. |
| `requires_human_approval_after` | No | Pause for human approval after this step completes. Default: `false`. |
| `enable_notifications` | No | Whether to send notifications for this step. Default: `true`. |

### `[step.artifacts]` Section

| Field | Required | Description |
|---|---|---|
| `produces` | No | List of artifact keys this step creates. |
| `required_inputs` | No | Artifact keys that must exist before this step executes. |
| `optional_inputs` | No | Artifact keys that improve results if present but are not required. |
| `result_meta_key` | No | Key in `meta.json` where the coder reports the output artifact path. |
| `target_artifact` | No | The artifact this step modifies or creates. |
| `edit_mode` | No | `create` (new artifact) or `edit` (modify existing). |
| `immutable_inputs` | No | Artifacts that the step may read but must not modify. |
| `produced_document_status` | No | Status metadata for the produced document (lifecycle, authority). |

### `[step.coder]` Section

| Field | Required | Description |
|---|---|---|
| `role_policy` | No | Role policy name (e.g., `architect_standard`). Resolved by `coder_registry.py`. |
| `must_differ` | No | Require a different coder than the previous step. Default: `false`. |
| `allowed_roles` | No | Explicit whitelist of allowed roles. |
| `coder_default` | No | Default coder name for this step. |
| `coder_default_role` | No | Default role for this step. |

### `[step.on_reject_refine]` Section

| Field | Required | Description |
|---|---|---|
| `refine_step` | Yes | Step name to activate on rejection. |
| `artifact` | No | Artifact key to pass to the refine step. |
| `max_iterations` | No | Maximum refine attempts. Default: `3`. |
| `exhausted` | No | Failure code when max iterations are reached. |

### `[step.on_exhaust_replan]` Section

| Field | Required | Description |
|---|---|---|
| `replan_step` | Yes | Step name to activate when refine is exhausted. |
| `artifact` | No | Artifact key to pass to the replan step. |

## Artifact Key Conventions

### Canonical Artifact Keys

Artifact keys are string constants defined in `agent_runner_v2/artifact_keys.py`.
They identify named outputs tracked through workflow state.

Each key follows the pattern `ARTIFACT_KEY_<NAME>` (e.g.,
`ARTIFACT_KEY_REVIEW`, `ARTIFACT_KEY_DELIVERY_AGENTS`).

### Key Naming Rules

- Use `UPPER_SNAKE_CASE` for key constant names.
- Keep keys descriptive and platform-scoped.
- Do not reuse Layer 1 or Layer 2 canonical keys with different semantics.
- Bundle-local keys follow the same naming convention.

### Key Usage in workflow.toml

Artifact keys are referenced in the `[step.artifacts]` section without the
`ARTIFACT_KEY_` prefix. For example, `produces = ["REVIEW_FILE_SUGGESTED"]`
references the key `ARTIFACT_KEY_REVIEW_FILE_SUGGESTED`.

### Key Usage in Prompt Templates

Prompt templates use placeholder syntax `{ARTIFACT_KEY_NAME}` to reference
artifact paths. These placeholders are resolved by the runner during prompt
rendering using `known_artifact_paths()` from `constants.py`.

## Bundle Governance Requirements

### bundle_governance.toml

The `bundle_governance.toml` file declares the bundle's governance
metadata. It must include:

```toml
[bundle]
name = "my_workflow_v1"
layer = "layer3"
platform = "agent-runner-v2"
```

### bundle_governance/ Package

The bundle governance package contains six files governing the bundle's
own authoring and maintenance:

1. **`core_governance.md`** : Bundle purpose, owning layer, permitted
   artifact classes, permanent-vs-temporary artifact rules, prohibition on
   Layer 1 redefinition, prohibition on Layer 3 bundle-specific drift.
2. **`prompt_sop.md`** : Prompt authoring principles, scope discipline
   rules, treatment of source code as read-only reference, citation
   behavior, prompt-change review expectations.
3. **`prompt_layout.md`** : Guidance for required prompt sections:
   objective, layer boundary, required inputs, artifact responsibilities,
   acceptance criteria, rejection criteria, output instructions.
4. **`action_policy.md`** : Allowed and forbidden action types for the
   bundle. Must declare which actions the bundle may invoke.
5. **`review_audit_contract.md`** : Defect classes for bundle review,
   routing policy for refine versus fail, minimum review obligations,
   minimum audit obligations.
6. **`prompt_contract.json`** : Machine-checkable constraints: required
   prompt files must exist, prompts must contain required sections or
   markers, review and audit prompts must contain explicit rejection
   logic.

### Generated Adapters

The platform's bundle governance adapter generator
(`bundle_governance.py`) reads the `bundle_governance/` package and
generates agent-specific guidance files (`AGENTS.md`, `CLAUDE.md`,
`QWEN.md`, `CODER_IMPLEMENTATION_SOP.md`) that enforce the bundle's
governance contract during prompt execution.

## Metadata Compliance

### Required Frontmatter

Every permanent document produced by a Layer 3 bundle must include YAML
frontmatter with at least these fields:

| Field | Required | Description |
|---|---|---|
| `template_id` | Yes | Template identifier for structural validation. |
| `version` | Yes | Document version. |
| `doc_type` | Yes | Functional class per Layer 1 vocabulary and Layer 2 extensions. |
| `authority` | Yes | Ownership source per Layer 1 vocabulary and Layer 2 extensions. |
| `scan_policy` | Yes | Scanner treatment: `include`, `exclude`, or `conditional`. |
| `scan_reason` | Yes | Why the scan policy was chosen. |
| `layer` | Yes | `layer3` for Layer 3 documents. |
| `platform` | Yes | `agent-runner-v2` for documents on this platform. |
| `lifecycle_status` | Yes | Current lifecycle state. Drafts use `"draft"`; published use `"published"`. |
| `effective_version` | Conditional | Run or change identifier. Required for workflow-generated permanent documents. |
| `managed_by` | Conditional | `workflow-generated` indicator. Required for workflow-generated documents. |

### Metadata Inheritance

Layer 3 bundles inherit the Layer 1 metadata baseline (field names and
vocabulary) plus Layer 2 platform extensions (`platform`, `template_id`,
`managed_by`). Layer 3 must not:

- Redefine the meaning of Layer 1 `doc_type` or `authority` values
- Use `platform_standard` as `doc_type` (reserved for Layer 2)
- Claim `platform-owned` as `authority` (reserved for Layer 2)
- Omit the `platform` field on permanent outputs

### Scan Policy for Layer 3 Outputs

| Artifact Class | Typical `scan_policy` |
|---|---|
| Permanent bundle outputs | `include` |
| Bundle governance files | `include` |
| Review artifacts | `conditional` or `exclude` |
| Validation artifacts | `conditional` or `exclude` |
| Audit artifacts | `conditional` or `exclude` |
| Temporary evidence | `exclude` |
