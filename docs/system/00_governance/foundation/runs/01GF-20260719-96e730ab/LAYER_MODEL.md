---
template_id: SYS-00-LM
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
managed_by: workflow-generated
scan_policy: "include"
scan_reason: "Layer 1 governance standard; included in operational scans"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-96e730ab"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `generate_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Layer Model

## Overview

The ecosystem operates on a three-layer architecture. Each layer has a
clear contract: what it owns, what it may reference, what it must not
define, and what artifacts it is allowed to generate.

This document defines the three layers, their boundaries, dependency
direction, and the rules governing promotion between layers.

## Layer 1

### Role

Layer 1 is the ecosystem constitution.

It defines the non-negotiable governance model that applies across all
Layer 2 platform cores and all Layer 3 workflow bundles that adopt this
architecture.

### Objective

Layer 1 exists to answer:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed?
- What does each layer own?
- What is forbidden in each layer?
- How are governance documents structured?
- How are ownership, review, approval, and change authority defined?

### What Layer 1 Owns

Layer 1 owns only cross-ecosystem governance concerns:

- Layer definitions and ownership boundaries
- Document authority model
- Document metadata classification rules
- Bundle taxonomy at a conceptual level
- Lifecycle and change control principles
- Review and approval obligations
- Naming and classification principles
- Inheritance rules between layers
- Rules for what lower layers must declare for themselves

### What Layer 1 Must Not Own

Layer 1 must not define:

- Runtime implementation details
- Repository bootstrap mechanics
- Installation flow
- Publish flow
- Registry API behavior
- Execution engine internals
- Path resolution algorithms
- Platform-specific node or tool behavior
- Concrete repository inventory
- Concrete workflow bundle inventory
- Concrete generated outputs for a specific domain

If a statement requires knowledge of how a specific platform executes,
installs, validates, stores, or publishes something, it does not belong
in Layer 1.

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

These are signs that Layer 2 or Layer 3 content has leaked upward.

## Layer 2

### Role

Layer 2 is the platform or domain constitution.

It translates Layer 1 governance into an operating model for one specific
platform, runtime family, or solution domain.

### Objective

Layer 2 exists to answer:

- How does this specific platform or domain apply Layer 1?
- What core capabilities does this platform provide?
- What standard bundle types exist in this platform?
- What shared runtime or framework services are available?
- What conventions must Layer 3 bundles follow in this platform?

### Valid Layer 2 Examples

Examples of valid Layer 2 cores:

- AI-driven SDLC core
- ComfyUI core
- n8n core
- agent-runner-v2 core

Each of these may have very different runtime behavior, packaging shape,
validation logic, and operating constraints. That difference belongs here,
not in Layer 1.

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

- The meaning of Layer 1
- Cross-ecosystem governance authority
- Cross-ecosystem ownership rules
- Generic architectural layer definitions

Layer 2 also must not collapse into Layer 3 by becoming a concrete bundle
inventory or a job-output dump.

### Success Criteria

Layer 2 is successful when:

- It cleanly applies Layer 1 without contradicting it
- It is concrete enough for Layer 3 authors to build against
- Platform details live here instead of leaking into Layer 1
- Multiple Layer 2 cores can coexist under the same Layer 1

## Layer 3

### Role

Layer 3 is the concrete delivery layer.

It contains operational workflow bundles that produce documents, reports,
scaffolds, assets, and other delivery outputs.

### Objective

Layer 3 exists to:

- Define concrete workflows with prompts, actions, and validators
- Produce governed outputs under Layer 1 rules and Layer 2 conventions
- Generate review, validation, and audit evidence
- Own bundle-local governance contracts

### What Layer 3 Owns

Layer 3 owns concrete operational and delivery assets:

- Workflow definitions
- Prompts and context extensions
- Validators
- Bundle-local governance files
- Artifact mappings and output path contracts
- Generated outputs and evidence artifacts

### What Layer 3 Must Not Own

Layer 3 must not:

- Define ecosystem-wide constitutional rules
- Define platform-wide standards that belong in Layer 2
- Claim Layer 1 or Layer 2 authority for its outputs
- Hide dependencies on undocumented Layer 2 behavior

## Relationship Between Layers

### Dependency Direction

Dependencies flow downward only:

```
Layer 1 (Governance)
    |
    v
Layer 2 (Platform/Domain Core)
    |
    v
Layer 3 (Workflow Bundles)
```

- Layer 1 defines governance rules that Layer 2 must apply.
- Layer 2 defines platform conventions that Layer 3 must follow.
- Layer 3 inherits from both Layer 1 and Layer 2.

No layer may silently absorb responsibilities from a higher layer. When
drift appears, the fix is to restore the boundary, not to refine wording
inside the wrong layer.

### Inheritance Rules

Governance rules inherit downward:

- Layer 1 defines common field names and baseline vocabularies.
- Layer 2 may extend value sets for platform-specific needs.
- Layer 3 may apply platform-specific values defined by its parent Layer 2.
- No lower layer may redefine the meaning of Layer 1 baseline values.

### Promotion Overview

Documents do not become higher-layer authority merely because they are
useful, widely reused, or frequently referenced.

Promotion to a higher layer requires:

1. Explicit review against the target layer scope.
2. Reclassification under the target layer metadata rules.
3. Acceptance by the owning authority of that higher layer.

Examples:

- A Layer 3 bundle guide does not become a Layer 2 platform standard by
  convention alone.
- A Layer 2 platform standard does not become Layer 1 governance because
  multiple platforms copied it.
- A generated document that originated in a lower layer stays in that
  layer until explicitly promoted.

### Boundary Decision Heuristics

When content classification is unclear, apply these tests:

1. **Cross-platform test**: If the statement should remain true for every
   adopted platform, it may belong in Layer 1.
2. **Platform test**: If the statement is true for one platform core but
   not necessarily others, it belongs in Layer 2.
3. **Bundle test**: If the statement is true only for one concrete workflow
   bundle or one generated output family, it belongs in Layer 3.
4. **Operationality test**: If the statement explains how something
   executes, installs, resolves, validates, or publishes, it is not
   Layer 1.
5. **Promotion test**: If the content originated as a lower-layer artifact,
   it stays in that layer until explicitly promoted.

### Replaceable Layer 2s

The ecosystem must support multiple Layer 2 cores without changing
Layer 1. Each Layer 2 translates Layer 1 governance into a
platform-specific operating model. This design ensures governance
stability while allowing platform diversity.

### Drift Prevention

No layer may silently absorb responsibilities from another layer. When
drift appears:

- The fix is to restore the boundary, not to refine wording inside the
  wrong layer.
- Review and audit steps should detect and reject cross-layer drift.
- Validators should flag content that belongs in a different layer.
