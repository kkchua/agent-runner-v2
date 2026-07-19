---
template_id: "SYS-00-LM"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "authoritative layer architecture definition for the ecosystem"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-61ae0105"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Layer Model

## Overview

The ecosystem is organized into three distinct layers. Each layer has a
defined role, ownership boundary, allowed content, and dependency
direction. This model exists to prevent boundary drift and to keep
governance, platform, and delivery concerns separated.

## Design Principles

### Governance Before Implementation

Layer 1 defines what must be governed, who owns what, and what may or may
not appear in lower layers. It does not define runtime mechanics, bootstrap
copy behavior, installer flow, registry internals, or execution algorithms.

### Stable Boundaries

Each layer has a clear contract:

- what it owns
- what it may reference
- what it must not define
- what artifacts it is allowed to generate

### Replaceable Layer 2s

The ecosystem must support multiple Layer 2 cores without changing Layer
1. Each Layer 2 translates Layer 1 governance into a platform-specific
operating model.

### Bundle-Centric Delivery

Layer 3 is where practical workflows live. Layer 3 bundles are the units
that actually generate documents, reports, scaffolds, assets, or other
delivery outputs.

### Drift Prevention

No layer may silently absorb responsibilities from another layer. When
drift appears, the fix is to restore the boundary, not to refine wording
inside the wrong layer.

---

## Layer 1

### Role

Layer 1 is the ecosystem constitution. It defines the non-negotiable
governance model that applies across all Layer 2 cores and all Layer 3
bundles that choose to adopt this architecture.

### Objective

Layer 1 exists to answer these questions:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed?
- What does each layer own?
- What is forbidden in each layer?
- How are governance documents structured?
- How are ownership, review, approval, and change authority defined?

### What Layer 1 Owns

Layer 1 owns only cross-ecosystem governance concerns:

- layer definitions
- ownership boundaries
- document authority model
- document metadata classification rules
- bundle taxonomy at a conceptual level
- change control principles
- review and approval obligations
- naming and classification principles
- inheritance rules between layers
- rules for what lower layers must declare for themselves

### What Layer 1 Must Not Own

Layer 1 must not define:

- runtime implementation details
- repository bootstrap mechanics
- installation flow
- publish flow
- registry API behavior
- execution engine internals
- path resolution algorithms
- platform-specific node or tool behavior
- concrete repository inventory
- concrete workflow bundle inventory
- concrete generated outputs for a specific domain

If a statement requires knowledge of how a specific platform executes,
installs, validates, stores, or publishes something, it does not belong in
Layer 1.

### Layer 1 Success Criteria

Layer 1 is successful when:

- it is reusable across very different Layer 2 cores
- it stays stable even when implementation changes underneath
- it is precise enough to reject out-of-scope content
- it is small enough to remain governable

### Layer 1 Failure Modes

Layer 1 is wrong when it starts describing:

- how code works
- how a runtime should discover files
- how a registry should be queried
- how a repository should be bootstrapped
- how a specific workflow should validate outputs

Those are signs that Layer 2 or Layer 3 content has leaked upward.

### Layer 1 Audience

Primary audiences:

- ecosystem owners
- architecture owners
- platform-core authors
- workflow framework designers

Secondary audiences:

- workflow bundle authors
- reviewers and auditors

---

## Layer 2

### Role

Layer 2 is the platform or domain constitution. It translates Layer 1
governance into an operating model for one specific platform, runtime
family, or solution domain.

### Objective

Layer 2 exists to answer these questions:

- How does this specific platform/domain apply Layer 1?
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

- runtime architecture for that platform
- bundle operating conventions for that platform
- repository or platform structure conventions
- shared services used by Layer 3 bundles
- platform-specific validation model
- platform-specific installation or deployment model
- platform-specific metadata contracts
- standard interfaces that Layer 3 bundles must comply with
- canonical directory conventions for that platform

### What Layer 2 Must Not Own

Layer 2 must not redefine:

- the meaning of Layer 1
- cross-ecosystem governance authority
- cross-ecosystem ownership rules
- generic architectural layer definitions

Layer 2 also must not collapse into Layer 3 by becoming a concrete bundle
inventory or a job-output dump.

### Layer 2 Audience

Primary audiences:

- platform maintainers
- runtime maintainers
- framework contributors
- bundle authors targeting that platform

### Layer 2 Success Criteria

Layer 2 is successful when:

- it cleanly applies Layer 1 without contradicting it
- it is concrete enough for Layer 3 authors to build against
- platform details live here instead of leaking into Layer 1
- multiple Layer 3 bundles can coexist on the same Layer 2 core

---

## Layer 3

### Role

Layer 3 is the concrete delivery layer. It contains workflow bundles that
produce documents, reports, scaffolds, assets, or other outputs.

### Objective

Layer 3 exists to answer these questions:

- What concrete workflows exist?
- What do they produce?
- How do they validate and review their outputs?
- What bundle-local rules govern their operation?

### What Layer 3 Owns

Layer 3 owns concrete operational and delivery assets:

- workflow definitions
- prompts
- context extensions
- validators
- bundle-local governance files
- artifact mappings
- generated outputs
- review, audit, and validation evidence

### What Layer 3 Must Not Own

Layer 3 must reject:

- ecosystem-wide constitutional claims
- platform-wide standards that belong in Layer 2
- hidden dependency on undocumented Layer 2 behavior
- generated content that pretends to change higher-layer governance by
  itself

### Layer 3 Audience

Primary audiences:

- bundle authors
- workflow operators
- output consumers
- reviewers and auditors of specific bundle outputs

---

## Relationship Between Layers

### Dependency Direction

Dependencies flow downward only:

```
Layer 1 (governance)
    |
    v
Layer 2 (platform core)
    |
    v
Layer 3 (workflow bundles)
```

- Layer 2 inherits from Layer 1 and must not contradict it.
- Layer 3 inherits from its parent Layer 2 and must not contradict it.
- No lower layer may redefine the meaning of a higher layer.
- Higher layers define what lower layers must declare for themselves.

### Inheritance Rules

1. Layer 1 defines the common field names and baseline vocabulary for
   metadata.
2. Layer 2 may extend value sets for platform-specific needs.
3. Layer 3 may apply platform-specific values defined by its parent
   Layer 2.
4. No lower layer may redefine the meaning of Layer 1 baseline values.

This preserves interoperability while still allowing platform-specific
detail where needed.

### Promotion Overview

Documents do not become higher-layer authority merely because they are
useful, widely reused, or frequently referenced.

Promotion to a higher layer requires:

1. explicit review against the target layer scope
2. reclassification under the target layer metadata rules
3. acceptance by the owning authority of that higher layer

Examples:

- a Layer 3 bundle guide does not become a Layer 2 platform standard by
  convention alone
- a Layer 2 platform standard does not become Layer 1 governance because
  multiple platforms copied it

### Boundary Decision Heuristics

When content classification is unclear, apply these tests:

1. **Cross-platform test**: If the statement should remain true for every
   adopted platform, it may belong in Layer 1.
2. **Platform test**: If the statement is true for one platform core but
   not necessarily others, it belongs in Layer 2.
3. **Bundle test**: If the statement is true only for one concrete
   workflow bundle or one generated output family, it belongs in Layer 3.
4. **Operationality test**: If the statement explains how something
   executes, installs, resolves, validates, or publishes, it is not
   Layer 1.
5. **Promotion test**: If the content originated as a lower-layer
   artifact, it stays in that layer until it is explicitly promoted.

## Content Boundary Matrix

| Content Type | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|
| Ecosystem purpose and constitutional scope | Allowed | Reference only | Reference only |
| Definition of Layer 1, Layer 2, and Layer 3 | Allowed | Reference only | Reference only |
| Cross-ecosystem ownership rules | Allowed | Must not redefine | Must not redefine |
| Generic document authority rules | Allowed | May extend | Must inherit |
| Generic metadata classification rules | Allowed | May extend | Must inherit |
| Generic bundle taxonomy | Allowed | May specialize | Applies only |
| Platform/runtime architecture | Forbidden | Allowed | Reference only |
| Platform installation/publish/deploy model | Forbidden | Allowed | Reference only |
| Platform metadata contracts | Forbidden | Allowed | Reference and comply |
| Shared runtime services | Forbidden | Allowed | Reference and consume |
| Concrete workflow definition | Forbidden | Forbidden | Allowed |
| Prompts and context extensions | Forbidden | Template/reference only | Allowed |
| Concrete artifact path contracts | Forbidden | Pattern only | Allowed |
| Concrete output file inventory | Forbidden | Pattern or template only | Allowed |
| Bundle-local review criteria | Forbidden | Standardize pattern only | Allowed |
| Bundle-local validators | Forbidden | Shared framework only | Allowed |
| Job history and execution evidence | Forbidden | Forbidden | Allowed |
| Review/audit/validation evidence | Evidence only | Evidence only | Allowed |
| Platform-specific examples | Forbidden | Allowed | Allowed |
| Bundle-specific examples | Forbidden | Template or reference only | Allowed |
| Repository-specific inventory | Forbidden | Allowed (as Layer 2 subject) | Allowed (bundle-owned) |
