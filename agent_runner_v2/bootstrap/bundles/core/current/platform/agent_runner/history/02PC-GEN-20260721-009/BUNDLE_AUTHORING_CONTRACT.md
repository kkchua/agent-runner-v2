---
template_id: SYS-02-BAC
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 bundle authoring contract; defines the contract every Layer 3 bundle must satisfy on agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260721-009"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.
> This file is workflow-generated and subject to review, validation, audit, and human approval before publication.

# Bundle Authoring Contract

## Purpose

This document defines the contract every Layer 3 workflow bundle must
satisfy to execute on agent-runner-v2. It specifies required files, the
workflow.toml format, artifact key conventions, bundle governance
requirements, and metadata compliance rules.

## Required Bundle Files

Every valid Layer 3 bundle on agent-runner-v2 must contain at minimum:

| File | Required | Purpose |
|---|---|---|
| `workflow.toml` | Yes | Declares workflow identity, steps, artifacts, coder configuration, and routing rules. |
| `prompts/` | Yes | Directory containing one or more prompt files for prompt-driven steps. |
| `bundle_governance.toml` | Yes | Declares bundle-level governance metadata and compliance rules. |
| `bundle_governance/` | Yes | Directory containing bundle governance documents (`core_governance.md`, `prompt_sop.md`, etc.). |
| `actions.py` | Conditional | Required if the bundle defines custom action functions. Optional for prompt-only bundles. |
| `context_extensions.py` | Optional | Defines `build_context_extensions()` for injecting bundle-specific variables into prompt context. |
| `output_paths.py` | Optional | Defines `build_output_paths()` for mapping artifact keys to file system paths. |

### Bundle Directory Structure

```
workflows/<bundle_name>/
  workflow.toml
  bundle_governance.toml
  actions.py                  # optional
  context_extensions.py       # optional
  output_paths.py             # optional
  prompts/
    generate_prompt.md
    review_prompt.md
    refine_prompt.md
    ...
  bundle_governance/
    core_governance.md
    prompt_sop.md
    prompt_layout.md
    action_policy.md
    review_audit_contract.md
    prompt_contract.json
```

## workflow.toml Format

The `workflow.toml` file defines the workflow structure using TOML
sections.

### `[workflow]` Section

Declares workflow-level metadata:

```toml
[workflow]
name = "my_bundle_name"
description = "What this workflow does"
layer = "layer3"
platform = "agent-runner-v2"
```

### `[[step]]` Section

Each `[[step]]` array entry defines one workflow step:

```toml
[[step]]
name = "generate_docs"
type = "generate"                # prompt-driven: generate, review, refine, audit
prompt = "generate_prompt.md"    # relative to prompts/ directory
coder = "qwen"                   # coder backend name
produces = ["MAIN_ARTIFACT"]     # artifact keys this step creates

[step.coder]
model_id = "qwen-coder-plus"     # model identifier in the coder registry

[step.artifacts]
MAIN_ARTIFACT = "docs/output/my_output.md"

[step.on_reject_refine]
refine_step = "refine_docs"
max_iterations = 3
```

### `[step.coder]` Subsection

Configures the coder backend for prompt-driven steps:

```toml
[step.coder]
connection = "openai"            # connection profile name
model_id = "gpt-4"               # model identifier
auth_type = "openai"             # authentication type
openai_api_key_env = "OPENAI_API_KEY"
openai_base_url = "https://api.openai.com/v1"
agent = "general"                # agent name for coder selection
```

The coder configuration is resolved through the coder registry
(`coder_registry.py`). Fields not specified here inherit from the
registry defaults.

### `[step.artifacts]` Subsection

Maps artifact keys to repo-relative file paths. Each path defines
where the step output file is stored relative to the project root.

### `[step.on_reject_refine]` Subsection

Defines routing when a step returns REJECTED:

```toml
[step.on_reject_refine]
refine_step = "refine_docs"      # step to route to on rejection
max_iterations = 3               # maximum review-refine loops
```

### Action Steps

Action steps use the `action` field instead of `prompt`:

```toml
[[step]]
name = "validate_output"
type = "validate"
action = "validate_docs"         # registered action function name
produces = ["VALIDATION_REPORT"]
```

### Allowed Step Types

All prompt-driven and action step types defined in the Runtime Model
are allowed:

- Prompt-driven: `generate`, `review`, `refine`, `audit`
- Action-based: `collect_context`, `validate`, `publish`, `step_completion`
- Human control: `human_approval`

## Artifact Key Conventions

Artifact keys are stable identifiers used to reference step outputs
across the workflow. They appear in:

- `produces` lists in step configurations
- `[step.artifacts]` mappings in `workflow.toml`
- Context extension dictionaries
- meta.json artifact maps

### Naming Rules

- Use `UPPER_SNAKE_CASE` for all artifact keys.
- Keys should be descriptive (e.g., `MAIN_REPORT`, `REVIEW_FILE`,
  `VALIDATION_REPORT`).
- The key `REVIEW_FILE_SUGGESTED` is reserved for review step outputs.
- The key `AUDIT_FILE_SUGGESTED` is reserved for audit step outputs.
- Bundle-level keys must not conflict with keys declared by other
  bundles in the same workflow.

### Artifact Path Resolution

Artifact paths in `[step.artifacts]` are repo-relative by default.
During execution, paths are resolved via `resolve_repo_or_runtime_path()`
from the shared runtime context. This ensures artifacts stored under
`docs/` resolve to the project root and artifacts stored under
`.ukbe-runner/` resolve to the runner home.

## Bundle Governance Requirements

Each bundle must include a `bundle_governance/` directory with the
following files:

### `core_governance.md`

Defines the bundle's scope, owning layer, permitted artifact classes,
permanent-vs-temporary artifact rules, and anti-drift policy. Must
include:

- Bundle purpose statement
- Owning layer declaration
- Permitted artifact classes
- Prohibition on Layer 1 or Layer 2 redefinition

### `prompt_sop.md`

Defines how prompts are authored, revised, and reviewed for this
bundle. Must include:

- Prompt authoring principles
- Scope discipline rules
- Required citation behavior for review and audit prompts
- Refinement constraints

### `prompt_layout.md`

Defines the standard section structure for prompts in this bundle.
Must include guidance for:

- Objective
- Scope/layer boundary
- Required inputs
- Artifact responsibilities
- Acceptance criteria
- Rejection criteria
- Output instructions

### `action_policy.md`

Defines allowed and forbidden action types for this bundle. Must
include:

- Allowed action types with justification
- Forbidden action intents
- Required separation between generation and code mutation

### `review_audit_contract.md`

Defines review and audit obligations. Must include:

- Defect classes relevant to this bundle
- Routing policy (refine vs. fail)
- Minimum review obligations
- Minimum audit obligations

### `prompt_contract.json`

Machine-checkable constraints on prompt files. Should validate:

- Required prompt files exist
- Prompts contain required sections or markers
- Review and audit prompts contain explicit rejection logic

### `bundle_governance.toml`

Declares bundle-level governance metadata:

```toml
[bundle]
name = "my_bundle"
layer = "layer3"
platform = "agent-runner-v2"
authority = "bundle-owned"
lifecycle_status = "active"
```

## Metadata Compliance

Every artifact produced by a Layer 3 bundle must carry YAML frontmatter
that satisfies both:

1. The Layer 1 Metadata Standard (required fields: `doc_type`,
   `authority`, `scan_policy`, `scan_reason`, `template_id`, `version`,
   `layer`, `lifecycle_status`)

2. The platform-specific Metadata Contract (this platform) for
   additional fields: `platform`, `managed_by`, `effective_version`

Bundle outputs must declare:

- `doc_type` appropriate to their class (`workflow_output`,
  `bundle_definition`, `review_artifact`, `validation_artifact`,
  `audit_artifact`)
- `authority` reflecting ownership (`bundle-owned`,
  `workflow-generated`, or `derived`)
- `layer: "layer3"`
- `platform: "agent-runner-v2"`

Bundle outputs must never claim:

- `authority: "platform-owned"` (reserved for Layer 2)
- `layer: "layer1"` or `layer: "layer2"`
- `doc_type: "platform_standard"` (reserved for Layer 2)

See the Metadata Contract document for the full metadata specification.
