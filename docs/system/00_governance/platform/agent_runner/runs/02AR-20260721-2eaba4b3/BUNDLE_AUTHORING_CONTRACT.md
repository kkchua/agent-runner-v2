---
template_id: "SYS-02-BAC"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 bundle authoring contract for agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02AR-20260721-2eaba4b3"
---

# agent-runner-v2 Bundle Authoring Contract

This document defines the contract every Layer 3 workflow bundle must satisfy to run on the agent-runner-v2 platform.

## Required Bundle Files

A valid Layer 3 bundle must contain at minimum:

| File | Required | Purpose |
|---|---|---|
| `workflow.toml` | Yes | Declares the workflow, its steps, coders, artifacts, and routing rules. |
| `actions.py` | Conditional | Python module defining action functions decorated with `@action()`. Required if the workflow uses action steps. |
| `prompts/` | Yes | Directory containing prompt template files (Markdown) for each prompt-driven step. |
| `bundle_governance.toml` | Yes | Machine-readable governance contract declaring the bundle's layer, platform, allowed action types, and output policy. |
| `bundle_governance/` | Yes | Directory containing bundle-local governance documents (at minimum `core_governance.md`). |
| `context_extensions.py` | Optional | Python module providing the `build_context_extensions()` hook for custom context variables. |
| `output_paths.py` | Optional | Python module providing the `build_output_paths()` hook for custom artifact path mappings. |

## workflow.toml Format

The `workflow.toml` file is the primary workflow definition. Its structure:

```toml
[workflow]
name = "my_bundle"
layer = "layer3"
platform = "agent-runner-v2"
authority = "bundle-owned"
description = "Description of what this bundle does."

[[step]]
name = "generate_output"
type = "generate"
prompt = "prompts/generate.md"
coder = "claude-code"
produces = ["MY_OUTPUT_FILE"]
result_meta_key = "MY_OUTPUT_FILE"
on_reject_refine = { prompt = "prompts/refine.md", max_iterations = 3 }

[step.artifacts]
MY_OUTPUT_FILE = "docs/my_output/{job_id}/output.md"

[step.coder]
model = "claude-sonnet-4"
timeout_seconds = 600

[[step]]
name = "validate_output"
type = "validate"
action = "validate_my_output"
produces = ["VALIDATION_REPORT"]
```

### `[workflow]` Section

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique workflow bundle identifier. |
| `layer` | Yes | Must be `"layer3"` for Layer 3 bundles. |
| `platform` | Yes | Must be `"agent-runner-v2"`. |
| `authority` | Yes | Bundle authority (`bundle-owned`, `workflow-generated`, etc.). |
| `description` | No | Human-readable description of the bundle purpose. |

### `[[step]]` Sections

Each `[[step]]` defines one workflow step. Multiple steps run in declaration order.

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique step name within the workflow. |
| `type` | Yes | Step type: `generate`, `review`, `refine`, `audit`, `validate`, `publish`, `collect_context`, `step_completion`, `human_approval`. |
| `prompt` | Conditional | Path to the prompt file (required for prompt-driven steps). |
| `coder` | Conditional | Coder name to use (required for prompt-driven steps). |
| `action` | Conditional | Action function name (required for action steps). |
| `produces` | No | List of artifact keys this step creates. |
| `updates` | No | List of artifact keys this step modifies in-place. |
| `result_meta_key` | No | Artifact key whose sidecar path is used for the meta.json. |
| `on_reject_refine` | No | Loop configuration for refinement on rejection. |
| `enable_notifications` | No | Whether step notifications are enabled for this step. |
| `coder_timeout_seconds` | No | Timeout override for the coder invocation. |

### `[step.artifacts]` Section

Maps artifact keys to their relative output paths. The runner resolves these paths to compute the expected file locations and validate that produced files exist.

### `[step.coder]` Section

| Field | Required | Description |
|---|---|---|
| `model` | No | Specific model identifier for this step. |
| `timeout_seconds` | No | Per-step timeout override. |

### `[step.on_reject_refine]` Section

| Field | Required | Description |
|---|---|---|
| `prompt` | Yes | Path to the refine prompt. |
| `max_iterations` | No | Maximum number of refine loops (default: 3). |

## Artifact Key Conventions

Artifact keys are the identifiers used throughout the workflow system to reference produced files.

### Naming Rules

- Keys must use `UPPER_SNAKE_CASE`.
- Keys should be descriptive of the artifact content (e.g., `REVIEW_FILE_SUGGESTED`, not `RFS`).
- Keys must match between `workflow.toml` production declarations, `output_paths.py`, `context_extensions.py`, and the meta.json artifacts map.
- Keys for temporary evidence (review, validation, audit) should be clearly distinguishable from keys for permanent deliverables.

### Path Conventions

- Artifact paths are relative to the project root for repository-scoped workflows.
- Paths follow the platform directory conventions: `docs/system/00_governance/` for governance artifacts, `docs/repo/` for delivery artifacts, etc.
- The `build_output_paths()` hook allows bundles to declare their own path mappings.

## Bundle Governance Requirements

Every bundle must include a `bundle_governance/` directory with at minimum:

1. **`core_governance.md`**: Declares:
   - Bundle purpose and owning layer
   - Permitted artifact classes
   - Permanent versus temporary artifact rule
   - Prohibition on Layer 1 redefinition
   - Prohibition on Layer 2 platform-wide claims

2. **`prompt_sop.md`**: Prompt authoring principles and scope discipline rules.

3. **`prompt_layout.md`**: Required sections per prompt (objective, layer boundary, inputs, artifacts, acceptance criteria, rejection criteria, output instructions).

4. **`action_policy.md`**: Allowed and forbidden action types for the bundle.

5. **`review_audit_contract.md`**: Defect classes, routing policy, review and audit obligations.

6. **`bundle_governance.toml`**: Machine-readable governance contract (at the bundle root, alongside `workflow.toml`). This TOML file declares the bundle's ownership layer, platform, allowed actions, and output policy in a format the runner can validate automatically.

## Metadata Compliance

All outputs produced by the bundle must comply with:

1. **Layer 1 baseline metadata** (`METADATA_STANDARD.md`): Required fields (`doc_type`, `authority`, `scan_policy`, `scan_reason`), extended fields (`template_id`, `version`, `layer`, `lifecycle_status`), allowed vocabularies, and scanner compliance rules.

2. **Layer 2 platform metadata** (`METADATA_CONTRACT.md`): Platform-specific `doc_type` and `authority` values, additional frontmatter fields (`platform`, `template_id`, `managed_by`), and metadata inheritance rules.

3. **Bundle-local metadata**: The bundle may add its own frontmatter fields but must not conflict with Layer 1 or Layer 2 fields. Bundle-owned documents carry `authority: "bundle-owned"`. Generated outputs carry `authority: "workflow-generated"` or `"derived"`.

Every file produced by the bundle must carry YAML frontmatter with at minimum the Layer 1 required fields and the platform-required fields. Temporary evidence artifacts (review, validation, audit) must carry `scan_policy: "conditional"` or `"exclude"` and must not be classified as `"platform_standard"`.
