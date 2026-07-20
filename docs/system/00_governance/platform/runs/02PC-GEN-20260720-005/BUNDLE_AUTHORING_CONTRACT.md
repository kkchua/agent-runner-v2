---
template_id: SYS-02-BAC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 bundle authoring contract; defines Layer 3 bundle requirements"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-005"
managed_by: workflow-generated
---

# Bundle Authoring Contract

## Purpose

This document defines the contract every Layer 3 workflow bundle must
satisfy to run on agent-runner-v2. It specifies the required files,
manifest format, artifact key conventions, bundle governance
requirements, and metadata compliance rules.

Layer 3 bundle authors must follow this contract to ensure their bundles
load correctly, execute predictably, and produce compliant outputs.

## Required Bundle Files

Every workflow bundle is a self-contained directory registered with the
platform's workflow registry (`workflow_packages/registry.py`). The
registry discovers bundles by scanning configured search paths for
directories containing a `workflow.toml` manifest.

### Mandatory Files

| File | Purpose |
|---|---|
| `workflow.toml` | The bundle manifest. Defines workflow identity, steps, artifact contracts, coder configuration, and routing. |
| `prompts/` | Directory containing prompt template `.txt` files referenced by prompt-driven steps. |

### Optional Files

| File | Purpose |
|---|---|
| `actions.py` | Custom action implementations for action-driven steps. Required only if the bundle defines action-driven steps. |
| `context_extensions.py` | Workflow-specific context injection via `build_context_extensions()`. Required only if the bundle needs custom prompt context. |
| `output_paths.py` | Workflow-owned path contracts via `build_output_paths()`. Required only if the bundle defines custom artifact output paths. |
| `bundle_governance/` | Bundle governance package directory containing adapter targets, prompt SOP, action policy, and review contracts. |

### Bundle Discovery

The `WorkflowRegistry` class in `workflow_packages/registry.py` discovers
bundles by:

1. Scanning registered search paths for subdirectories.
2. Checking each subdirectory for a `workflow.toml` file.
3. Loading and caching the bundle on demand via `load_workflow_package()`.

Bundles that fail to load (missing manifest, invalid TOML, missing
required fields) are logged and skipped without crashing the registry.

## workflow.toml Format

The `workflow.toml` manifest is parsed by `workflow_packages/loader.py`
into a `WorkflowBundle` dataclass. The manifest uses TOML syntax and
must contain the following sections.

### `[workflow]` Section

Defines the workflow identity and global settings.

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique workflow identifier. Used for job directories and registry lookup. |
| `version` | Yes | Bundle version string. |
| `label` | Yes | Human-readable display label. |
| `job_prefix` | Yes | Prefix for generated job IDs. |
| `visibility` | No | Visibility scope (e.g., `public`, `internal`). |
| `default_max_rejects` | No | Maximum refinement iterations before replan (default: 3). |
| `init_step` | Yes | Name of the first step in the workflow. |

### `[[step]]` Sections

Each step is defined as a TOML array-of-tables entry.

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique step name within the workflow. |
| `prompt` | Conditional | Prompt template filename (relative to `prompts/`). Required for prompt-driven steps. |
| `action` | Conditional | Action function name. Required for action-driven steps. |
| `mode` | No | Execution mode hint. |
| `onsuccess` | No | Name of the next step on success. |
| `requires_human_approval_after` | No | Boolean; if true, pauses for human approval after this step. |
| `enable_notifications` | No | Boolean; if true, sends notifications for this step. |

### `[step.artifacts]` Section

Defines the artifact contract for a step.

| Field | Required | Description |
|---|---|---|
| `produces` | No | List of artifact keys this step generates. |
| `required_inputs` | No | List of artifact keys that must exist before this step runs. |
| `optional_inputs` | No | List of artifact keys used if available. |
| `result_meta_key` | No | Key for storing the step result in meta sidecar. |
| `target_artifact` | No | Primary artifact key for this step's output. |
| `edit_mode` | No | Edit behavior for the target artifact. |

### `[step.coder]` Section

Configures coder invocation for prompt-driven steps.

| Field | Required | Description |
|---|---|---|
| `role_policy` | No | Named role policy from `role_policies.json`. |
| `allowed` | No | List of allowed coder backends. |
| `must_differ` | No | Boolean; if true, refinement must use a different coder. |

### `[step.on_reject_refine]` Section

Configures the refinement loop for rejection handling.

| Field | Required | Description |
|---|---|---|
| `refine_step` | Yes | Name of the refinement step. |
| `artifact` | Yes | Artifact key to refine. |
| `max_iterations` | No | Override for max refinement iterations. |
| `exhausted_failure_code` | No | Failure code when refinement is exhausted. |

### `[step.on_exhaust_replan]` Section

Configures replan behavior when refinement is exhausted.

| Field | Required | Description |
|---|---|---|
| `replan_step` | Yes | Name of the replan step. |
| `artifact` | Yes | Artifact key for the replan output. |

## Artifact Key Conventions

Artifact keys are canonical string identifiers for named outputs tracked
through workflow state. The platform defines artifact keys as constants
in `constants.py` using the naming pattern `ARTIFACT_KEY_<UPPER_SNAKE>`.

### Key Rules

1. Artifact keys must be uppercase snake_case strings.
2. Each key must be unique within the platform's artifact key namespace.
3. Keys should be semantically meaningful (e.g., `REVIEW_FILE_SUGGESTED`,
   `CODEBASE_INVENTORY`, `DELIVERY_AGENTS`).
4. Workflow bundles must reference artifact keys from `constants.py` or
   declare new keys following the same convention.
5. Artifact keys must not include version suffixes or bundle-specific
   prefixes that prevent reuse across workflows.

### Path Resolution

Artifact keys are mapped to filesystem paths via `known_artifact_paths()`
in `constants.py`. This function returns a dictionary mapping each
artifact key to its canonical relative path. Workflow bundles must not
hardcode artifact paths; they must use the key-to-path resolution system.

### Placeholder Resolution

Workflow prompt templates use `{ARTIFACT_KEY_*}` placeholders that match
keys from `constants.py`. The runner resolves these placeholders during
prompt rendering using the `ARTIFACT_KEYS` set and
`known_artifact_paths()` function. Bundles must not use the deprecated
`REFERENCE_FILES` dictionary for placeholder resolution.

## Bundle Governance Requirements

Each workflow bundle should include a bundle governance package that
controls its own authoring and maintenance behavior.

### Governance Package Structure

The bundle governance package lives under `bundle_governance/` within
the bundle directory and is loaded by `bundle_governance.py` as a
`BundleGovernance` dataclass.

| Component | Purpose |
|---|---|
| `prompt_sop.md` | Prompt authoring standard for this bundle. |
| `prompt_layout.md` | Required prompt sections and layout rules. |
| `action_policy.md` | Allowed and forbidden action types for this bundle. |
| `review_audit_contract.md` | Review and audit behavior contract. |
| `prompt_contract.json` | Machine-checkable prompt constraints. |

### Governance Integration

The `BundleGovernance` dataclass carries:

- **adapter_targets**: which governance adapters to generate (e.g.,
  AGENTS.md, CLAUDE.md, QWEN.md).
- **include_in_prompts**: whether governance content is injected into
  prompt templates.
- **prompt_targets**: which prompt files receive governance blocks.
- **extensions**: optional governance extension content with source
  paths and target configurations.
- **artifact_registry**: list of `GovernanceArtifact` entries defining
  artifacts owned or referenced by the governance package.

### Governance Rendering

The `render_prompt_governance_block()` function in
`bundle_governance.py` generates governance instruction blocks that are
injected into prompt templates. This ensures coders receive consistent
scope and compliance instructions for each bundle.

## Metadata Compliance

All permanent outputs produced by Layer 3 bundles must comply with the
metadata contract defined in this platform's Metadata Contract
(`METADATA_CONTRACT.md`) and the Layer 1 Metadata Standard.

### Required Metadata for Bundle Outputs

Every permanent document produced by a Layer 3 bundle must include YAML
frontmatter with at least:

- `template_id`: stable identifier for structural validation
- `version`: document version
- `doc_type`: functional classification (Layer 1 baseline or platform
  extension value)
- `authority`: ownership declaration (must not claim `human-authored`
  for generated content)
- `scan_policy`: scanner treatment directive
- `scan_reason`: human-readable reason for the scan policy
- `layer`: must be `"layer3"` for bundle outputs
- `platform`: must be `"agent-runner-v2"`
- `lifecycle_status`: current lifecycle state

### Metadata Inheritance

Layer 3 bundles inherit:

- Layer 1 baseline metadata fields and vocabularies.
- Layer 2 platform extensions (additional fields, extended vocabularies).

Bundles must not redefine Layer 1 or Layer 2 metadata values. Bundles
may apply platform-specific values defined in the Metadata Contract.

### Prohibited Metadata Claims

- Generated bundle outputs must not claim `authority: "human-authored"`.
- Bundle outputs must not claim `layer: "layer1"` or `layer: "layer2"`.
- Bundle outputs must not claim `doc_type: "platform_standard"` unless
  explicitly promoted through a higher-layer process.
- Derived artifacts must not present themselves as root authority.
