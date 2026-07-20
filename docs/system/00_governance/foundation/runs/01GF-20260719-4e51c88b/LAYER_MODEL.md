---
template_id: "SYS-00-LM"
version: "0.1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "defines the three-layer architecture that all other governance documents reference"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-4e51c88b"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `generate_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Layer Model

## Overview

The ecosystem documentation and workflow architecture is organized into
three layers. Each layer has a defined role, clear ownership boundaries,
and explicit rules about what it may and may not contain. The purpose of
this model is to prevent scope drift: no layer may silently absorb
responsibilities from another layer.

The dependency direction is strict: Layer 3 depends on Layer 2; Layer 2
depends on Layer 1; Layer 1 depends on nothing below it. Change flows
downward: a Layer 1 change may require Layer 2 and Layer 3 updates;
a Layer 3 change should never force a Layer 1 revision.

## Layer 1

### Role

Layer 1 is the **ecosystem constitution**. It defines the non-negotiable
governance model that applies across all Layer 2 platform cores and all
Layer 3 workflow bundles that adopt this architecture.

### Objective

Layer 1 exists to answer these questions:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed, and what does each layer own?
- What is forbidden in each layer?
- How are governance documents structured and classified?
- How are ownership, review, approval, and change authority defined?
- What is the conceptual bundle taxonomy?
- What lifecycle states and metadata conventions apply across layers?

### What Layer 1 Owns

Layer 1 owns only cross-ecosystem governance concerns:

- Layer definitions and ownership boundaries
- Document authority model and promotion rules
- Document metadata classification rules
- Conceptual bundle taxonomy
- Governance lifecycle rules at principle level
- Change control, review, and approval obligations
- Naming and classification principles
- Inheritance rules between layers
- Rules for what lower layers must declare for themselves

### What Layer 1 Must Not Own

Layer 1 must not define:

- Runtime implementation details or execution engine internals
- Repository bootstrap mechanics
- Installation flow, publish flow, or deploy procedures
- Registry API behavior or path resolution algorithms
- Platform-specific node, tool, or service behavior
- Concrete repository inventory or concrete workflow bundle inventory
- Concrete generated outputs for a specific domain
- Platform-specific validation rules or scanner implementations

If a statement requires knowledge of how a specific platform executes,
installs, validates, stores, or publishes something, it does not belong in
Layer 1.

### Deliverables

Layer 1 produces a compact, stable governance set:

- An index document (`README.md`)
- A layer definition document (`LAYER_MODEL.md`)
- A document authority standard (`DOCUMENT_AUTHORITY.md`)
- A bundle taxonomy (`BUNDLE_TAXONOMY.md`)
- A governance lifecycle standard (`GOVERNANCE_LIFECYCLE.md`)
- A metadata standard (`METADATA_STANDARD.md`)

### Success Criteria

Layer 1 is successful when:

- It is reusable across very different Layer 2 cores
- It stays stable even when implementation changes underneath
- It is precise enough to reject out-of-scope content
- It is small enough to remain governable

### Failure Modes

Layer 1 is wrong when it starts describing:

- How code works
- How a runtime should discover files
- How a registry should be queried
- How a repository should be bootstrapped
- How a specific workflow should validate outputs

Those are signs that Layer 2 or Layer 3 content has leaked upward.

## Layer 2

### Role

Layer 2 is the **platform or domain constitution**. It translates Layer 1
governance into an operating model for one specific platform, runtime
family, or solution domain.

### Objective

Layer 2 exists to answer these questions:

- How does this specific platform or domain apply Layer 1 governance?
- What core capabilities does this platform provide?
- What standard bundle types exist in this platform?
- What shared runtime or framework services are available?
- What conventions must Layer 3 bundles follow on this platform?

### Valid Layer 2 Examples

Examples of valid Layer 2 cores:

- AI-driven SDLC core
- ComfyUI core
- n8n core
- agent-runner-v2 core

Each may have very different runtime behavior, packaging shape, validation
logic, and operating constraints. Those differences belong here, not in
Layer 1.

### What Layer 2 Owns

Layer 2 owns the platform-specific or domain-specific core model:

- Runtime architecture for that platform
- Bundle operating conventions for that platform
- Repository or platform structure conventions
- Shared services used by Layer 3 bundles
- Platform-specific validation model
- Platform-specific installation or deployment model
- Platform-specific metadata contracts
- Standard interfaces that Layer 3 bundles must comply with
- Canonical directory conventions for that platform

### What Layer 2 Must Not Own

Layer 2 must not redefine:

- The meaning of Layer 1 governance
- Cross-ecosystem governance authority
- Cross-ecosystem ownership rules
- Generic architectural layer definitions

Layer 2 also must not collapse into Layer 3 by becoming a concrete bundle
inventory or a job-output dump.

### Deliverables

A Layer 2 core typically defines:

- Platform overview and operating model
- Runtime model and shared service contracts
- Bundle authoring contract
- Metadata and validation contract
- Platform-specific review and release standards

### Success Criteria

Layer 2 is successful when:

- It cleanly applies Layer 1 without contradicting it
- It is concrete enough for Layer 3 authors to build against
- Platform details live here instead of leaking into Layer 1
- Multiple Layer 3 bundles can operate under it without rewriting it

## Layer 3

### Role

Layer 3 is the **workflow and delivery layer**. It contains concrete
workflow bundles that generate documents, reports, scaffolds, assets,
and other delivery outputs.

### Objective

Layer 3 exists to answer these questions:

- What concrete workflows are available?
- What artifacts does each workflow produce?
- What prompts, validators, and context extensions does a workflow use?
- What are the bundle-local governance rules?

### What Layer 3 Owns

Layer 3 owns concrete operational and delivery assets:

- Workflow definitions and prompts
- Context extensions and validators
- Bundle-local governance files
- Artifact mappings and output path contracts
- Generated outputs (documents, reports, scaffolds, assets)
- Review, audit, and validation evidence

### What Layer 3 Must Not Own

Layer 3 must reject:

- Ecosystem-wide constitutional claims (belongs to Layer 1)
- Platform-wide standards that belong in Layer 2
- Hidden dependency on undocumented Layer 2 behavior
- Generated content that pretends to change higher-layer governance by itself

### Deliverables

Layer 3 bundles produce:

- Workflow definitions (`workflow.toml`)
- Prompt templates and context extensions
- Validators and bundle-local governance
- Generated outputs and delivery artifacts
- Temporary review, validation, and audit evidence

## Relationship Between Layers

### Dependency Direction

```
Layer 1 (ecosystem constitution)
    ^
    |  Layer 2 inherits from Layer 1
    |
Layer 2 (platform/domain constitution)
    ^
    |  Layer 3 inherits from Layer 1 and Layer 2
    |
Layer 3 (workflow bundles and delivery)
```

Each layer depends on the layer above it. Dependencies never flow upward.
A Layer 3 bundle may reference Layer 2 and Layer 1; a Layer 2 platform may
reference Layer 1; Layer 1 depends on nothing below it.

### Change Direction

Changes flow downward. A Layer 1 governance change may require Layer 2
and Layer 3 updates. A Layer 2 platform change may require Layer 3 bundle
updates. A Layer 3 change must never force a Layer 1 or Layer 2 revision.

### Promotion Overview

Documents do not become higher-layer authority merely because they are
useful, widely reused, or frequently referenced. Promotion to a higher
layer requires:

1. Explicit review against the target layer scope
2. Reclassification under the target layer metadata rules
3. Acceptance by the owning authority of that higher layer

Examples:

- A Layer 3 bundle guide does not become a Layer 2 platform standard by
  convention alone
- A Layer 2 platform standard does not become Layer 1 governance because
  multiple platforms copied it

### Content Boundary

The content boundary matrix establishes what each layer may contain:

| Content Type | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|
| Ecosystem purpose and constitutional scope | Allowed | Reference only | Reference only |
| Layer definitions and boundaries | Allowed | Reference only | Reference only |
| Cross-ecosystem ownership rules | Allowed | Must not redefine | Must not redefine |
| Document authority rules | Allowed | May extend | Must inherit |
| Metadata classification rules | Allowed | May extend | Must inherit |
| Conceptual bundle taxonomy | Allowed | May specialize | Applies only |
| Platform/runtime architecture | Forbidden | Allowed | Reference only |
| Platform install/publish/deploy model | Forbidden | Allowed | Reference only |
| Platform metadata contracts | Forbidden | Allowed | Reference and comply |
| Shared runtime services | Forbidden | Allowed | Reference and consume |
| Concrete workflow definition | Forbidden | Forbidden | Allowed |
| Prompts and context extensions | Forbidden | Template/reference only | Allowed |
| Concrete artifact path contracts | Forbidden | Pattern only | Allowed |
| Concrete output file inventory | Forbidden | Pattern or template only | Allowed |
| Review/audit/validation evidence | Evidence only | Evidence only | Allowed |

### Boundary Decision Heuristics

When content classification is unclear, apply these tests:

1. **Cross-platform test**: If the statement should remain true for every
   adopted platform, it may belong in Layer 1.
2. **Platform test**: If the statement is true for one platform core but not
   necessarily others, it belongs in Layer 2.
3. **Bundle test**: If the statement is true only for one concrete workflow
   bundle or one generated output family, it belongs in Layer 3.
4. **Operationality test**: If the statement explains how something executes,
   installs, resolves, validates, or publishes, it is not Layer 1.
5. **Promotion test**: If the content originated as a lower-layer artifact,
   it stays in that layer until it is explicitly promoted.

### Conflict Rule

If document authority conflicts with document content, content scope wins
for classification and the document should be flagged:

- A document marked `masterplan` that contains operational runbook detail
  is misclassified
- A document marked `workflow_output` that tries to define ecosystem
  governance is misclassified
- A document marked `system` but limited to one platform probably belongs
  in Layer 2, not Layer 1
