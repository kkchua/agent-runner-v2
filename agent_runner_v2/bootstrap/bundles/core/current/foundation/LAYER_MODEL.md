---
template_id: SYS-00-LM
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 1 layer model; defines the three-layer architecture boundary"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-c5e882c3"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Layer Model

## Overview

The ecosystem is organized into three layers. Each layer has a distinct
role, owns specific concerns, and respects clear boundaries with the
layers above and below it.

Dependency direction is downward only: Layer 3 depends on Layer 2, and
Layer 2 depends on Layer 1. No lower layer may redefine or contradict a
higher layer.

## Layer 1

### Role

Layer 1 is the ecosystem constitution. It defines the non-negotiable
governance model that applies across all Layer 2 platform cores and all
Layer 3 workflow bundles that adopt this architecture.

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

- layer definitions and boundaries
- ownership rules and document authority model
- metadata classification rules and scan policy
- conceptual bundle taxonomy
- governance lifecycle and change control principles
- review, validation, audit, and approval obligations
- naming and classification principles
- inheritance rules between layers

### What Layer 1 Must Not Own

Layer 1 must not define:

- runtime implementation details
- repository bootstrap mechanics
- installation, publish, deploy, or registry procedures
- execution engine internals
- path resolution algorithms
- platform-specific node or tool behavior
- concrete repository or workflow bundle inventory
- concrete generated outputs for a specific domain

If a statement requires knowledge of how a specific platform executes,
installs, validates, stores, or publishes something, it does not belong in
Layer 1.

### Success Criteria

Layer 1 is successful when:

- it is reusable across very different Layer 2 cores
- it stays stable even when implementation changes underneath
- it is precise enough to reject out-of-scope content
- it is small enough to remain governable

## Layer 2

### Role

Layer 2 is the platform or domain constitution. It translates Layer 1
governance into an operating model for one specific platform, runtime
family, or solution domain.

### Objective

Layer 2 exists to answer:

- How does this specific platform apply Layer 1 governance?
- What core capabilities does this platform provide?
- What standard bundle types exist in this platform?
- What shared runtime or framework services are available?
- What conventions must Layer 3 bundles follow?

### What Layer 2 Owns

Layer 2 owns the platform-specific operating model:

- runtime architecture for that platform
- bundle operating conventions for that platform
- repository or platform structure conventions
- shared services used by Layer 3 bundles
- platform-specific validation model
- platform-specific installation or deployment model
- platform-specific metadata contracts
- standard interfaces that Layer 3 bundles must comply with

### What Layer 2 Must Not Own

Layer 2 must not redefine:

- the meaning of Layer 1 governance
- cross-ecosystem governance authority
- cross-ecosystem ownership rules
- generic architectural layer definitions

Layer 2 also must not collapse into Layer 3 by becoming a concrete bundle
inventory or a job-output dump.

### Success Criteria

Layer 2 is successful when:

- it cleanly applies Layer 1 without contradicting it
- it is concrete enough for Layer 3 authors to build against
- platform details live here instead of leaking into Layer 1
- multiple Layer 3 bundles can operate within it consistently

## Layer 3

### Role

Layer 3 is the concrete delivery layer. It contains workflow bundles that
produce actual outputs -- documents, reports, scaffolds, assets, or other
delivery artifacts.

### Objective

Layer 3 exists to:

- define concrete workflow steps and routing
- produce generated outputs within Layer 2 conventions
- manage bundle-local governance and validation
- produce review, audit, and validation evidence

### What Layer 3 Owns

Layer 3 owns concrete operational and delivery assets:

- workflow definitions and prompts
- context extensions and validators
- bundle-local governance files
- artifact mappings and output path contracts
- generated outputs
- review, audit, and validation evidence

### What Layer 3 Must Not Own

Layer 3 must not:

- define ecosystem-wide constitutional claims
- define platform-wide standards that belong in Layer 2
- hide dependencies on undocumented Layer 2 behavior
- generate content that pretends to change higher-layer governance by
  itself

### Success Criteria

Layer 3 is successful when:

- it operates within Layer 2 conventions
- its outputs are clearly identifiable as bundle-owned
- it does not leak bundle-specific logic into platform standards
- evidence artifacts are kept separate from permanent outputs

## Relationship Between Layers

### Dependency Direction

Dependency flows downward:

```
Layer 1 (ecosystem constitution)
    ^
    | depends on
Layer 2 (platform constitution)
    ^
    | depends on
Layer 3 (workflow bundles)
```

Layer 2 depends on Layer 1 for governance rules. Layer 3 depends on
Layer 2 for platform conventions. No layer depends on a layer below it.

### Inheritance

- Layer 1 defines common vocabulary, field names, and baseline rules.
- Layer 2 may extend value sets for platform-specific needs but must not
  redefine Layer 1 baseline meanings.
- Layer 3 inherits Layer 1 and Layer 2 rules and may apply
  platform-specific values defined by its parent Layer 2.

### Promotion

Content does not move upward by convention alone. Promotion to a higher
layer requires:

1. explicit review against the target layer scope
2. reclassification under the target layer metadata rules
3. acceptance by the owning authority of that higher layer

A Layer 3 bundle guide does not become a Layer 2 platform standard
without explicit promotion. A Layer 2 platform standard does not become
Layer 1 governance because multiple platforms copied it.

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
5. **Promotion test**: If the content originated as a lower-layer
   artifact, it stays in that layer until it is explicitly promoted.

### Drift Prevention

No layer may silently absorb responsibilities from another layer. When
drift appears -- for example, Layer 1 documents describing runtime
behavior, or Layer 3 outputs claiming constitutional authority -- the fix
is to restore the boundary, not to refine wording inside the wrong layer.
