---
template_id: SYS-02-BAC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 bundle authoring contract; defines requirements for all Layer 3 bundles on this platform"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260720-86359b88"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Authoring Contract

## Purpose

This document defines the contract that every Layer 3 workflow bundle
must satisfy to execute on the agent-runner-v2 platform. It specifies
required files, manifest format, artifact key conventions, bundle
governance requirements, and metadata compliance rules.

Layer 3 bundle authors must conform to this contract. The platform
runtime enforces these requirements during workflow loading and
execution.

## Required Bundle Files

Every Layer 3 workflow bundle is a self-contained directory. The
following files define the bundle structure:

### Mandatory Files

| File | Purpose |
|---|---|
| `workflow.toml` | Declarative workflow manifest: steps, routing, artifact keys, coder policies. |
| `prompts/` | Directory containing prompt template `.txt` files referenced by prompt-driven steps. |

### Conditionally Required Files

| File | Required When | Purpose |
|---|---|---|
| `actions.py` | The bundle defines custom action steps | Custom action implementations for action-driven steps. |
| `context_extensions.py` | The bundle needs workflow-specific context injection | Workflow-specific context hooks via `build_context_extensions()`. |
| `output_paths.py` | The bundle defines workflow-owned output path contracts | Workflow-owned path contract declarations via `build_output_paths()`. |

### Bundle Governance

| File | Purpose |
|---|---|
| `bundle_governance.toml` | Bundle governance manifest: adapter targets, governance extensions, artifact registry. |
| `bundle_governance/` | Directory containing governance documents (prompt SOP, action policy, review contract, etc.). |

The `bundle_governance/` directory may contain:

- `prompt_sop.md` -- prompt authoring principles for this bundle.
- `prompt_layout.md` -- required prompt sections and structure.
- `action_policy.md` -- allowed and forbidden action types.
- `review_audit_contract.md` -- review and audit obligations.
- `prompt_contract.json` -- machine-checkable prompt constraints.

### Optional Files

| File | Purpose |
|---|---|
| `_registry/coder_connections.json` | Bundle-local coder connection overrides. |
| `_registry/role_policies.json` | Bundle-local role policy overrides. |
| `_registry/coder_roles.json` | Bundle-local coder role definitions. |

## workflow.toml Format

The `workflow.toml` manifest is the primary declaration of a workflow
bundle. It is parsed by the workflow package loader
(`workflow_packages/loader.py`) and converted to a `WorkflowBundle`
dataclass (`workflow_packages/base.py`).

### Top-Level Sections

#### `[workflow]`

Defines workflow identity and global settings:

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique workflow identifier (e.g., `my_workflow_v1`). |
| `version` | Yes | Semantic version string. |
| `label` | No | Human-readable display label. |
| `job_prefix` | Yes | Prefix for job IDs (e.g., `MW`). |
| `visibility` | No | Visibility scope (e.g., `public`, `internal`). |
| `default_max_rejects` | No | Default maximum rejection iterations for refine loops. |
| `init_step` | No | Name of the initialization step, if any. |

#### `[[step]]`

Defines a single workflow step. Multiple `[[step]]` sections are allowed.

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique step identifier within the workflow. |
| `prompt` | Conditional | Prompt template filename (for prompt-driven steps). |
| `action` | Conditional | Action function name (for action-driven steps). |
| `mode` | No | Execution mode override. |
| `onsuccess` | No | Name of the next step on success. |
| `requires_human_approval_after` | No | Whether to pause for human approval after this step. |
| `enable_notifications` | No | Whether to send notifications for this step. |

#### `[step.artifacts]`

Defines the artifact contract for a step:

| Field | Required | Description |
|---|---|---|
| `produces` | No | List of artifact keys this step produces. |
| `required_inputs` | No | List of artifact keys required as input. |
| `optional_inputs` | No | List of artifact keys optionally used as input. |
| `result_meta_key` | No | Key in meta.json holding the result. |
| `target_artifact` | No | Primary artifact key for this step's output. |
| `edit_mode` | No | Edit behavior for the target artifact. |

#### `[step.coder]`

Defines coder configuration for a prompt-driven step:

| Field | Required | Description |
|---|---|---|
| `role_policy` | No | Role policy name for coder selection. |
| `must_differ` | No | Whether this step's coder must differ from the previous step. |
| `allowed` | No | List of allowed coder connection names. |

#### `[step.on_reject_refine]`

Defines the refinement loop when a step is rejected:

| Field | Required | Description |
|---|---|---|
| `refine_step` | Yes | Name of the refine step to route to. |
| `artifact` | Yes | Artifact key being refined. |
| `max_iterations` | No | Maximum number of refine iterations. |
| `exhausted_failure_code` | No | Failure code when iterations are exhausted. |

#### `[step.on_exhaust_replan]`

Defines replan behavior when refine iterations are exhausted:

| Field | Required | Description |
|---|---|---|
| `replan_step` | Yes | Name of the replan step. |
| `artifact` | Yes | Artifact key being replanned. |

## Artifact Key Conventions

Artifact keys are canonical identifiers for named outputs tracked through
workflow state. They are defined as constants in `artifact_keys.py` and
used throughout the platform.

### Naming Rules

1. Artifact keys use `UPPER_SNAKE_CASE`.
2. Keys must be unique across the platform.
3. Keys are defined as `ARTIFACT_KEY_*` constants in `artifact_keys.py`.
4. Path resolution uses `known_artifact_paths()` from `path_catalog.py`.

### Key Categories

| Category | Example | Description |
|---|---|---|
| Document artifacts | `REVIEW_FILE_SUGGESTED` | Named document outputs. |
| Meta artifacts | `*_METAJSON` | Sidecar metadata references. |
| Directory artifacts | `CODEBASE_INVENTORY` | Directory-type outputs. |

### Path Resolution

Artifact paths are resolved through the layered constants system:

1. `artifact_keys.py` -- canonical key literals (`ARTIFACT_KEY_*`).
2. `path_primitives.py` -- stable filename and root constants.
3. `path_catalog.py` -- computed mappings (`known_artifact_paths()`).
4. `constants.py` -- layered re-export of all path constants.

No hardcoded path strings are permitted in production code. All path
resolution flows through the constants layer.

## Bundle Governance Requirements

Every Layer 3 bundle must declare its governance contract. The bundle
governance system (`bundle_governance.py`) generates adapter documents
for coder consumption.

### Governance Manifest

The `bundle_governance.toml` file declares:

- adapter targets (which governance documents to generate).
- governance extensions (additional governance content).
- artifact registry (artifacts owned or referenced by the bundle).

### Generated Governance Documents

The platform generates governance adapter documents from the bundle
governance manifest. These documents are injected into coder prompts to
ensure the coder operates within the bundle's governance constraints.

Generated documents may include:

- `AGENTS.md` -- agent-specific governance instructions.
- `CLAUDE.md` -- Claude-specific governance instructions.
- `QWEN.md` -- Qwen-specific governance instructions.
- `prompt_contract.json` -- machine-checkable prompt constraints.

### Governance Extensions

Bundles may extend the base governance with additional documents or
constraints. Extensions are declared in `bundle_governance.toml` and
processed by the governance adapter generator.

## Metadata Compliance

All permanent documents produced by a Layer 3 bundle must comply with
the metadata requirements defined in this platform's Metadata Contract
(`METADATA_CONTRACT.md`) and inherited from the Layer 1 Metadata
Standard.

### Required Metadata Fields

Every permanent bundle output must include at minimum:

| Field | Value Pattern |
|---|---|
| `template_id` | Bundle-specific template identifier. |
| `version` | Document version. |
| `doc_type` | A valid value from the platform metadata contract. |
| `authority` | A valid value from the platform metadata contract. |
| `scan_policy` | `include`, `exclude`, or `conditional`. |
| `scan_reason` | Non-empty explanation. |
| `layer` | `layer3` for bundle outputs. |
| `platform` | `agent-runner-v2`. |
| `lifecycle_status` | Current lifecycle state. |
| `effective_version` | Run or change identifier. |
| `managed_by` | Required for workflow-generated documents. |

### Inheritance

Layer 3 bundles inherit:

1. Layer 1 baseline metadata fields and vocabularies.
2. Layer 2 platform-specific metadata extensions.

Bundles must not redefine Layer 1 or Layer 2 metadata values. Bundles
may add bundle-specific metadata fields for their own needs.

### Validation

The platform validates metadata compliance during:

- workflow bundle loading (`workflow_bundle_validator.py`).
- documentation validation steps (`documentation_validation_core.py`).
- review and audit steps.

Non-compliant metadata is a governance defect that must be corrected
before publication.
