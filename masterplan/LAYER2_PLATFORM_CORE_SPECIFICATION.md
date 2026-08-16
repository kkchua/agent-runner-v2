---
doc_type: "masterplan"
authority: "human-authored"
scan_policy: "exclude"
scan_reason: "design specification for Layer 2 platform core; exclude from operational scans"
---

# Layer 2 Platform Core Specification

## Status

**Implemented** — The `02_agent_runner_platform_v1` workflow has been built and shipped.

- **Workflow bundle:** `02_agent_runner_platform_v1`
- **Implementation date:** 2026-07-21
- **Published platform constitution:** `docs/system/00_governance/platform/agent_runner/current/`
- **Job reference:** `02PC-20260721-b092c705` (first clean pass, zero refine cycles)

This document defined the target specification for the Layer 2 platform-core workflow. The workflow has been implemented and the platform constitution is now the active Layer 2 standard for agent-runner-v2.

## Purpose

The purpose of the Layer 2 workflow is to produce and maintain the
`{PLATFORM}` platform constitution — the set of documents that
define how this specific platform operationalizes Layer 1 governance.

This workflow must not be derived from the legacy
`00_repo_master_docs_bootstrap_v1` package. That workflow performs
automated codebase scanning, syncing, and evidence generation — behaviors
that belong in Layer 3, not Layer 2. The new workflow should be designed
from Layer 2 scope first, then implemented from that design.

## Design Objective

The new Layer 2 workflow must:

- generate only Layer 2 platform standards
- inherit from Layer 1 governance without redefining it
- define the runtime model, bundle authoring contract, shared services,
  and platform metadata/validation rules for `{PLATFORM}`
- reject Layer 3 bundle-specific drift and Layer 1 constitutional
  overreach
- be stable enough for multiple future Layer 3 bundles to depend on
- separate permanent platform standards from temporary evidence
- attach explicit metadata to all outputs

## Workflow Identity

### Workflow Bundle Name

`02_agent_runner_platform_v1`

### Workflow Class

Platform-core workflow.

### Owning Layer

Layer 2.

### Platform

`{PLATFORM}`

### Primary Authority

Platform/core maintainer authority.

### Output Authority Model

- permanent platform standards may be `workflow-generated` or
  `platform-owned`
- review, validation, and audit outputs are temporary evidence artifacts
- the Layer Architecture Masterplan remains `human-authored` input

## Bundle Governance Package

The workflow bundle should include an explicit bundle-governance package
governing its own authoring and maintenance.

### Required Bundle-Governance Files

1. `bundle_governance/core_governance.md`
2. `bundle_governance/prompt_sop.md`
3. `bundle_governance/prompt_layout.md`
4. `bundle_governance/action_policy.md`
5. `bundle_governance/review_audit_contract.md`
6. `bundle_governance/prompt_contract.json`

### `core_governance.md`

Must include:

- bundle purpose (platform constitution generation for {PLATFORM})
- owning layer (Layer 2)
- permitted artifact classes
- permanent versus temporary artifact rule
- prohibition on Layer 1 redefinition
- prohibition on Layer 3 bundle-specific drift

### `prompt_sop.md`

Must include:

- prompt authoring principles
- scope discipline rules: Layer 1 governance is inherited, not rewritten
- requirement to treat source code modules as read-only reference, not
  as editable output
- required citation behavior for review and audit prompts
- prompt-change review expectations

### `prompt_layout.md`

Must include guidance for sections such as:

- objective
- layer boundary
- required inputs
- artifact responsibilities
- acceptance criteria
- rejection criteria
- output instructions

### `action_policy.md`

Allowed actions:

- `collect_context` (gather curated reference paths)
- `validate` (deterministic platform-standard checks)
- `publish` (activate approved platform constitution)
- `step_completion`

Forbidden actions:

- mutate platform runtime code during constitution generation
- perform automated codebase scanning or repo analysis
- generate Layer 3 bundle-local prompts or artifact mappings
- rewrite `masterplan/` documents
- perform repository bootstrap or installation operations

### `review_audit_contract.md`

Must define:

- defect classes for platform constitution review
- routing policy for refine versus fail
- minimum review obligations
- minimum audit obligations

### `prompt_contract.json`

Must validate at least:

- required prompt files exist
- prompts contain required sections or markers
- review and audit prompts contain explicit rejection logic
- refine prompt contains no instructions that normalize lower-layer
  drift into platform standards

## Allowed Step Taxonomy

### Prompt-Driven Step Types

- `generate` — creates draft platform constitution artifacts
- `review` — performs scope and quality review with pass/reject outcome
- `refine` — revises artifacts after fixable findings
- `audit` — performs final semantic verification before approval

### Action Step Types

- `collect_context` — gathers curated reference inputs
- `validate` — runs deterministic rules against artifacts
- `publish` — marks an approved set as active
- `step_completion` — closes the workflow

### Human-Control Step Type

- `human_approval` — obtains explicit platform-owner acceptance before
  activation

## Forbidden Action Intent

The Layer 2 workflow bundle must not perform actions intended to:

- perform automated codebase scanning or repo structure analysis
- mutate platform runtime code as part of constitution generation
- generate Layer 3 bundle definitions, prompts, or artifact mappings
- rewrite `masterplan/` source documents
- bootstrap repository structure
- generate job-history or run-scoped evidence beyond temporary review,
  validation, and audit artifacts

## Prompt Design Rules

All prompts in this bundle should follow these rules:

- they must state that the workflow belongs to Layer 2
- they must declare the platform (`{PLATFORM}`) explicitly
- they must distinguish permanent platform standards from temporary
  evidence
- they must treat Layer 1 governance documents as inherited authority,
  not as editable output
- they must treat source code modules as read-only reference inputs
- review and audit prompts must require direct citations for findings
- refine prompts must prioritize reclassification or rejection over
  polishing wrong-scope content

## Review and Audit Defect Classes

The bundle-governance package should classify at least these defects:

- `layer1_redefinition` — redefines or contradicts Layer 1 governance
- `layer3_bundle_drift` — contains bundle-specific outputs or examples
  masquerading as platform-wide rules
- `platform_identity_missing` — platform ownership unclear or absent
- `metadata_noncompliance` — metadata values violate Layer 1 baseline or
  platform extension rules
- `missing_required_structure` — mandatory section or document absent
- `forbidden_operational_content` — contains implementation detail that
  belongs in code, not a platform constitution
- `wrong_document_inventory` — document set does not match the defined
  permanent set
- `evidence_as_standard` — temporary evidence artifact presented as
  permanent platform standard

## Routing Policy

- fixable defects route to refine (metadata omission, missing section,
  weak wording, removable scope leakage)
- conceptual layer mismatch routes to fail (layer1_redefinition,
  layer3_bundle_drift)
- wrong document inventory routes to fail
- platform identity missing routes to fail if systemic, refine if
  isolated
- evidence presented as permanent standard routes to fail

## Design Input Access Model

The workflow should receive reference inputs as explicitly declared file
paths — the same curated-reference pattern used by the Layer 1 workflow.

The platform context collection step must not perform automated codebase
scanning or discovery. Instead, it declares a fixed set of authoritative
source paths that the LLM reads as read-only reference.

### Declared Reference Inputs

| Input | Path | Purpose |
|---|---|---|
| Layer 1 governance set | `GOVERNANCE_RUNTIME_ROOT` (`~/.ukbe-runner/bundles/core/current`) | Inherited governance baseline; injected into prompt context as `{GOVERNANCE_RUNTIME_ROOT}` placeholder |
| Layer Architecture Masterplan | `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md` | Scope and boundary definition |
| Workflow engine core | the platform's workflow packages module | Step types, action dispatching, bundle loading |
| Runtime context | the platform's runtime context module | Context extensions, path resolution, job root |
| Coder registry | the platform's coder registry module | Coder roles, connections, role policies |
| Constants | the platform's constants module | Artifact keys, folder constants, path conventions |
| Shared validation | the platform's documentation validation module | Validation plan pattern, section checks |
| Daemon and execution | the platform's daemon and backend execution modules | Execution model, daemon/worker lifecycle |
| Notification and result handling | the platform's action result module | ActionResult, reject codes, artifact contracts |
| Known workflow bundles | the platform's workflows directory (names only) | Existing Layer 3 bundles on this platform |
| Existing bundle governance | the platform's bootstrap workflow directory | Existing workflow patterns and conventions |

These paths are curated by the workflow designer and listed in the
`collect_platform_context` action. They are not discovered at runtime.

### Design Input Rules

- reference source code is read-only — the workflow must not rewrite it
- reference paths are fixed in the action implementation, not discovered
  dynamically
- the context inventory artifact records which references were available
  during the run for audit traceability

## Workflow Scope

### In Scope

The workflow may:

- generate the {PLATFORM} platform constitution documents
- refine platform constitution documents after review findings
- validate platform constitution documents against deterministic rules
- audit accepted platform constitution documents for layer-boundary
  accuracy
- emit temporary evidence artifacts for review, validation, and audit

### Out of Scope

The workflow must not:

- redefine Layer 1 ecosystem governance
- perform automated codebase scanning, analysis, or evidence generation
- generate Layer 3 bundle definitions, prompts, or artifact mappings
- produce bundle-local validators or output contracts
- mutate platform runtime code as part of the constitution generation run
- bootstrap repository structure or installation state

## Target Permanent Document Set

1. `README.md`
2. `RUNTIME_MODEL.md`
3. `BUNDLE_AUTHORING_CONTRACT.md`
4. `SHARED_SERVICES.md`
5. `METADATA_CONTRACT.md`
6. `VALIDATION_CONTRACT.md`

This set is intentionally platform-constitution-focused and excludes
runbook-level operational procedures, bundle inventories, and generated
job evidence.

## Permanent Document Roles

### `README.md`

Purpose:

- index the {PLATFORM} platform constitution set
- define what {PLATFORM} is and how it fits as a Layer 2 core
- summarize relationship to Layer 1 and Layer 3

Must include:

- platform overview
- document map (self-including — six documents, not five plus an
  implicit index)
- audience summary
- statement that this is the platform constitution, not a runtime
  operations manual

### `RUNTIME_MODEL.md`

Purpose:

- define the execution architecture of {PLATFORM}

Must include:

- step model: prompt-driven versus action steps
- step types: generate, review, refine, audit, collect_context,
  validate, publish, human_approval, step_completion
- daemon mode and manual mode execution paths
- job lifecycle: init, execute, review/refine loops, approve, publish
- coding agent integration: coder roles, connections, role policies
- rejection and retry model
- notification model

### `BUNDLE_AUTHORING_CONTRACT.md`

Purpose:

- define the contract every Layer 3 bundle must satisfy to run on
  {PLATFORM}

Must include:

- required bundle files: `workflow.toml`, `actions.py` (optional for
  prompt-only bundles), `prompts/`, `bundle_governance.toml`,
  `bundle_governance/`, `context_extensions.py` (optional),
  `output_paths.py` (optional)
- `workflow.toml` format: `[workflow]`, `[[step]]`,
  `[step.artifacts]`, `[step.coder]`, `[step.on_reject_refine]`
- artifact key conventions
- bundle governance package requirements
- metadata compliance requirements for bundle outputs (inheriting from
  Layer 1 and this platform's metadata contract)

### `SHARED_SERVICES.md`

Purpose:

- define the runtime services available to Layer 3 bundles

Must include:

- context extension pattern (`build_context_extensions()`)
- artifact resolution (`resolve_repo_or_runtime_path()`)
- path contracts (`build_output_paths()`)
- meta sidecar handling (`write_meta_sidecar()`)
- notification integration patterns
- backend sync protocol (for daemon/worker communication)
- action registration via `@action()` decorator

### `METADATA_CONTRACT.md`

Purpose:

- define platform-specific metadata extensions beyond the Layer 1
  baseline

Must include:

- platform-specific `doc_type` values (e.g., `bundle_definition`,
  `workflow_output`) and their meanings
- platform-specific `authority` values (e.g., `platform-owned`,
  `bundle-owned`) and their meanings
- additional frontmatter fields specific to {PLATFORM} artifacts
  (e.g., `platform`, `template_id`, `managed_by`)
- metadata inheritance rules: Layer 3 bundles inherit Layer 1 baseline
  plus Layer 2 platform extensions
- scan-policy expectations for platform artifacts

### `VALIDATION_CONTRACT.md`

Purpose:

- define the platform validation model shared across Layer 3 bundles

Must include:

- `DocumentationValidationPlan` pattern and how bundles compose it
- section-check conventions (`has_section()`)
- frontmatter field enforcement (`has_frontmatter_field()`)
- file existence and folder structure checks
- how Layer 3 bundles should use platform validators
- distinction between platform-level validation and bundle-local checks
- guidance for writing `validate_*` actions in Layer 3 workflows

## Permanent Document Exclusions

The permanent Layer 2 set must not include documents whose primary
purpose is:

- Layer 1 ecosystem governance (belongs to `01_governance_foundation_v1`)
- runtime runbooks or operational how-to guides
- concrete Layer 3 bundle inventories
- job-history evidence
- installation or setup guides for a specific repository instance
- codebase scanning results

## Output Location

```
docs/system/00_governance/platform/agent_runner/
├── runs/{job_id}/        ← staged (draft) artifacts + evidence
├── history/{job_id}/     ← archived published snapshots
└── current/              ← active published platform constitution
    └── platform_set_manifest.json
```

This mirrors the Layer 1 output structure: staged runs, versioned
history, and a current active set with a publish manifest.

## Temporary Evidence Artifacts

The workflow should generate separate temporary artifacts:

- platform core review artifact
- platform core validation artifact
- platform core audit artifact

These artifacts must never be part of the permanent platform
constitution set.

## Artifact Classification

### Permanent Artifacts

Permanent Layer 2 artifacts should carry metadata consistent with:

- `doc_type: "platform_standard"`
- `authority: "workflow-generated"` or `"platform-owned"`
- `scan_policy: "include"`
- `layer: "layer2"`
- `platform: "{PLATFORM}"`

### Temporary Evidence

Temporary artifacts should carry metadata consistent with:

- `doc_type: "review_artifact"` or `"validation_artifact"` or
  `"audit_artifact"`
- `authority: "workflow-generated"` or `"derived"`
- `scan_policy: "conditional"` or `"exclude"`
- `layer: "layer2"`
- `platform: "{PLATFORM}"`

## Step Model

### Step 1: Collect Platform Context

Purpose:

- gather curated reference inputs required to prevent Layer 1
  redefinition and Layer 3 drift

Responsibilities:

- load the Layer 1 governance set and masterplan
- expose declared source code reference paths as read-only input
- list known Layer 3 workflow bundles (names only)
- expose the collected context as read-only input to later steps

Output:

- platform context inventory

### Step 2: Generate Platform Core Docs

Purpose:

- generate the initial permanent {PLATFORM} platform constitution
  documents

Responsibilities:

- use the Layer 1 governance set and masterplan as inherited authority
- use declared source code references as factual input for the runtime
  model
- generate all six permanent target docs together for terminology
  consistency
- avoid Layer 1 redefinition and Layer 3 bundle-specific drift

Output:

- the full permanent platform constitution set draft

### Step 3: Review Platform Core Docs

Purpose:

- perform layer-boundary and platform-scope review

Responsibilities:

- detect Layer 1 redefinitions
- detect Layer 3 bundle-specific drift
- detect missing required sections
- detect metadata or authority mismatch
- detect missing platform identity
- reject when evidence is presented as permanent standard

Output:

- review artifact with findings and explicit pass/reject decision

### Step 4: Refine Platform Core Docs

Purpose:

- revise the permanent docs when review or validation identified fixable
  defects

Responsibilities:

- correct scope, structure, metadata, and terminology defects
- preserve Layer 2 boundaries
- refuse to polish content that redefines Layer 1 or collapses into
  Layer 3

Output:

- revised permanent platform constitution set

### Step 5: Validate Platform Core Docs

Purpose:

- run deterministic checks against the permanent docs

Responsibilities:

- verify Layer 1 governance runtime root exists before any LLM work begins
- confirm metadata presence and baseline validity
- confirm required document inventory exists
- confirm required sections exist per document
- confirm platform identity fields are present
- confirm prohibited topics are absent
- confirm permanent and temporary artifacts are separated

Output:

- validation artifact

### Step 6: Audit Platform Core Accuracy

Purpose:

- perform a final semantic audit after refinement and validation

Responsibilities:

- verify the accepted docs still belong in Layer 2
- verify Layer 1 governance was inherited correctly, not redefined
- verify no bundle-specific content was normalized into platform
  standards
- verify platform identity is clear throughout

Output:

- audit artifact with explicit acceptance or rejection

Audit rejection routing:

- if audit finds fixable Layer 2 defects, route back to refine
- if audit finds Layer 1 redefinition, wrong document inventory, or
  systemic Layer 3 drift, fail the workflow clearly

### Step 7: Human Approval Gate

Purpose:

- obtain explicit platform-owner acceptance before activation

Responsibilities:

- present the approved permanent set plus review, validation, and audit
  evidence
- require acceptance by the platform/core maintainer or equivalent
  authority

Output:

- explicit approval decision

### Step 8: Publish Platform Core Set

Purpose:

- mark the approved permanent set as the active {PLATFORM}
  platform constitution

Responsibilities:

- publish only after review, validation, audit, and human approval
  succeed
- keep evidence artifacts separate from the permanent set
- mark the published set as active in both frontmatter and publish
  manifest
- supersede any prior active set without destroying historical
  traceability
- archive or retain prior manifests and prior generated sets as
  superseded versions

Output:

- active {PLATFORM} platform constitution set

## Review Gates

The review step must reject if any of the following are present:

- Layer 1 governance redefinition or contradiction
- platform standards containing bundle-specific outputs or examples
  presented as platform-wide rules
- required permanent documents missing
- platform identity missing or unclear
- metadata values violating Layer 1 baseline
- evidence artifacts presented as permanent platform standards
- missing mandatory sections in a permanent document

Review should produce direct citations to the offending content.

## Validation Gates

Validation should enforce at least:

- all six target permanent files exist
- all required metadata fields exist with valid values
- `layer: "layer2"` and `platform: "{PLATFORM}"` are present on
  all permanent docs
- all required major sections exist per document
- required cross-document consistency holds
- forbidden Layer 1-redefining content is absent
- forbidden Layer 3 bundle-specific content is absent
- evidence artifacts are not classified as permanent platform standards
- ASCII-only output
- L1 governance references resolve exclusively to `GOVERNANCE_RUNTIME_ROOT`
  (the global runtime path). No repo-local L1 path strings (e.g.,
  `docs/system/00_governance/foundation/current/`) may appear anywhere in
  the L2 workflow — not in prompts, actions, context inventory artifacts,
  or validation checks.
- documented function signatures in SHARED_SERVICES.md
  (`build_context_extensions`, `build_output_paths`,
  `resolve_repo_or_runtime_path`, `BackendClient.*` methods) are
  cross-verified against the installed `{PLATFORM}` package source
  (resolved via `Path({PLATFORM}.__file__).parent`), not against
  the repo working tree. This ensures the gate is portable to any
  CLI-installed PC.
- the `### Resolution Order` section in SHARED_SERVICES.md describes the
  actual prefix-dispatch behavior of `resolve_repo_or_runtime_path()`.
  The phrases "check the repository working tree first" and
  "fall back to the runtime artifact root" are forbidden because they
  describe an existence-based fallback that does not exist.
- the meta sidecar "no disk recovery functions" and
  "no stdout JSON parsing" phrases are forbidden in RUNTIME_MODEL.md
  and SHARED_SERVICES.md when the platform source defines a repair
  function (e.g., `_repair_or_validate_meta_json` in `step_runner.py`).
  The docs must accurately describe both the primary sidecar channel
  and the repair fallback.
- `authority` and `managed_by` in METADATA_CONTRACT.md must be declared
  as orthogonal axes: `authority` = content ownership;
  `managed_by` = mechanical producer/maintainer. A document carrying
  `authority: "platform-owned"` + `managed_by: workflow-generated` is
  consistent when the contract explicitly states this orthogonality.

## Audit Gates

Audit should focus on semantic correctness, especially:

- content truly belongs in Layer 2 (platform constitution), not Layer 1
  or Layer 3
- Layer 1 governance was inherited correctly, not reworded or
  contradicted
- runtime model accurately reflects the platform source code
- bundle authoring contract is precise enough for Layer 3 authors to
  depend on
- no platform-specific detail leaked into claims of ecosystem-wide
  applicability
- METADATA_CONTRACT.md's `### Usage Rules` section explicitly states
  that `authority` and `managed_by` are orthogonal axes. If the
  contract's definitions imply a contradiction between these two fields,
  the audit must reject with the specific inconsistency.

## Rejection and Refinement Policy

Refinement should be allowed only for fixable defects such as:

- missing required section
- weak wording
- metadata omission
- minor scope leakage that can be removed cleanly

Refinement should not be used when:

- the document set redefines Layer 1 governance
- a document has the wrong purpose entirely (e.g., bundle inventory
  instead of platform constitution)
- the target document inventory is wrong

In such cases, the workflow should fail clearly rather than repeatedly
refining the wrong artifact.

## Artifact Tracking Requirements

The workflow should record enough metadata for each artifact:

- workflow id
- workflow layer
- platform identifier
- artifact type
- authority
- permanence class
- lifecycle status
- source step
- change or run id

Per-file frontmatter holds document-local classification. The publish
manifest holds run-level and active-set tracking state.

## Naming and Metadata Rules

- permanent Layer 2 docs must be identifiable as the active platform
  constitution
- evidence artifacts must carry `scan_policy: "conditional"` or
  `"exclude"`
- generated Layer 2 docs must not claim `human-authored`
- Layer 1 governance references must be treated as inherited authority,
  not rewritable content

## Non-Goals

This workflow is not intended to:

- create Layer 1 governance standards (belongs to
  `01_governance_foundation_v1`)
- create Layer 3 workflow bundles
- perform automated codebase scanning or repo analysis
- manage runtime implementation code
- generate job-history evidence beyond temporary review/validation/audit
  artifacts

## Success Criteria

The Layer 2 workflow is successful when:

- it produces a stable platform constitution that Layer 3 bundles can
  depend on
- review reliably rejects Layer 1 redefinitions and Layer 3 drift
- validation catches classification and structure defects
  deterministically
- audit confirms semantic Layer 2 correctness and platform identity
  consistency
- the generated output can govern multiple future Layer 3 bundles on
  {PLATFORM} without rewrite

## Implementation Readiness Checklist

The workflow is ready to implement when these decisions are accepted:

1. the target permanent document set (six docs)
2. the temporary evidence artifact set
3. the review, validation, and audit gate definitions
4. the curated reference input model (declared paths, not scanning)
5. the publication rule for the active platform constitution
6. the human approval gate
7. the publish-manifest tracking model

Only after these are accepted should the workflow package structure,
prompts, validators, and output paths be created.
