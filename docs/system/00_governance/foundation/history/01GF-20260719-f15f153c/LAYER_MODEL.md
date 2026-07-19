---
template_id: SYS-00-LM
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 governance foundation document; required for operational scans"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-f15f153c"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Layer Model

## Layer 1

### Role

Layer 1 is the ecosystem constitution. It defines the non-negotiable
governance model that applies across all Layer 2 platform cores and all
Layer 3 workflow bundles that adopt this architecture.

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

### Success Criteria

Layer 1 is successful when:

- it is reusable across very different Layer 2 cores
- it stays stable even when implementation changes underneath
- it is precise enough to reject out-of-scope content
- it is small enough to remain governable

### Failure Modes

Layer 1 is wrong when it starts describing:

- how code works
- how a runtime should discover files
- how a registry should be queried
- how a repository should be bootstrapped
- how a specific workflow should validate outputs

Those are signs that Layer 2 or Layer 3 content has leaked upward.

---

## Layer 2

### Role

Layer 2 is the platform or domain constitution. It translates Layer 1
governance into an operating model for one specific platform, runtime
family, or solution domain.

### Objective

Layer 2 exists to answer:

- How does this specific platform or domain apply Layer 1?
- What core capabilities does this platform provide?
- What standard bundle types exist in this platform?
- What shared runtime or framework services are available?
- What conventions must Layer 3 bundles follow in this platform?

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

### What Layer 2 Must Not Own

Layer 2 must not redefine:

- the meaning of Layer 1
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
- multiple Layer 3 bundles can target this layer without redefining it

---

## Layer 3

### Role

Layer 3 is the delivery layer. It contains concrete workflow bundles and
their generated outputs, operating within the conventions of a specific
Layer 2 platform.

### Objective

Layer 3 exists to answer:

- What specific workflows exist and what do they produce?
- What prompts, validators, and context extensions drive each workflow?
- What concrete artifacts does each bundle generate?
- What is the current state of each workflow run?

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
- job state and execution history

### What Layer 3 Must Not Own

Layer 3 must reject:

- ecosystem-wide constitutional claims
- platform-wide standards that belong in Layer 2
- hidden dependency on undocumented Layer 2 behavior
- generated content that pretends to change higher-layer governance by
  itself

---

## Relationship Between Layers

### Dependency Direction

Dependencies flow downward only:

- Layer 3 depends on Layer 2 conventions
- Layer 2 depends on Layer 1 governance
- Layer 1 depends on nothing except its own defined scope

No reverse dependency is permitted. Layer 1 must not reference Layer 2
conventions. Layer 2 must not embed Layer 3 bundle details.

### Content Boundary

Each layer has a clear contract defining what it owns, what it may
reference, what it must not define, and what artifacts it is allowed to
generate.

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

### Conflict Rule

If document authority conflicts with document content, content scope wins
for classification and the document should be flagged.

### Boundary Decision Heuristics

When content classification is unclear, apply these tests:

1. **Cross-platform test:** If the statement should remain true for every
   adopted platform, it may belong in Layer 1.
2. **Platform test:** If the statement is true for one platform core but
   not necessarily others, it belongs in Layer 2.
3. **Bundle test:** If the statement is true only for one concrete
   workflow bundle or one generated output family, it belongs in Layer 3.
4. **Operationality test:** If the statement explains how something
   executes, installs, resolves, validates, or publishes, it is not
   Layer 1.
5. **Promotion test:** If the content originated as a lower-layer
   artifact, it stays in that layer until it is explicitly promoted.
