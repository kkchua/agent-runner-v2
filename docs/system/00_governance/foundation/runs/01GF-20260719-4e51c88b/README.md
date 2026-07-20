---
template_id: "SYS-00-IDX"
version: "0.1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "index document for the Layer 1 governance foundation set; must be discoverable by scanners"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-4e51c88b"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `generate_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Layer 1 Governance Foundation

## Purpose

This document set defines the ecosystem governance baseline. It answers the
fundamental questions that apply across every Layer 2 platform core and
every Layer 3 workflow bundle that chooses to adopt this architecture:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed, and what does each layer own?
- How are governance documents structured, classified, and scanned?
- How are ownership, authority, review, approval, and change control defined?
- What is the conceptual bundle taxonomy for the ecosystem?
- What lifecycle states apply to governed documents?
- What metadata conventions ensure machine-readable classification?

Layer 1 is the **ecosystem constitution**. It defines the non-negotiable
governance model. It does not define runtime architecture, platform-specific
implementation, install or publish procedures, registry operations, or
repository operating instructions. Those responsibilities belong to Layer 2
and Layer 3.

## Document Map

The Layer 1 governance foundation set consists of six permanent documents:

| # | Document | template_id | Description |
|---|---|---|---|
| 1 | `README.md` | `SYS-00-IDX` | This index. Summarizes the governance set, audience, and scope. |
| 2 | `LAYER_MODEL.md` | `SYS-00-LM` | Defines Layer 1, Layer 2, Layer 3, their boundaries, dependency direction, and promotion overview. |
| 3 | `DOCUMENT_AUTHORITY.md` | `SYS-00-DA` | Defines authority vocabulary, authority matrix, promotion constraints, and permanent-vs-temporary rules. |
| 4 | `BUNDLE_TAXONOMY.md` | `SYS-00-BT` | Defines the conceptual bundle taxonomy and ownership rules. Does not define workflow-specific artifact contracts. |
| 5 | `GOVERNANCE_LIFECYCLE.md` | `SYS-00-GL` | Defines lifecycle states, approval versus publication, revision, deprecation, retirement, and promotion interaction. |
| 6 | `METADATA_STANDARD.md` | `SYS-00-MS` | Defines required metadata fields, baseline vocabularies, scan policy rules, scanner compliance rules, and validation expectations. |

## Audience

Primary audiences for Layer 1 governance:

- **Ecosystem owners**: define and maintain the constitutional governance model
- **Architecture owners**: design layer boundaries and promotion rules
- **Platform-core authors**: translate Layer 1 into a platform-specific operating model for Layer 2
- **Workflow framework designers**: build workflow engines that comply with Layer 1 authority and metadata rules

Secondary audiences:

- **Workflow bundle authors**: understand the governance constraints that Layer 3 bundles inherit
- **Reviewers and auditors**: verify that generated artifacts respect layer boundaries

## Relationship to Other Layers

Layer 1 is the topmost governance layer in a three-layer ecosystem:

```
Layer 1  - Ecosystem governance constitution (this set)
Layer 2  - Platform or domain core operating model
Layer 3  - Concrete workflow bundles and delivery outputs
```

- **Layer 1** defines what must be governed, who owns what, and what may or may
  not appear in lower layers.
- **Layer 2** translates Layer 1 governance into a platform-specific operating
  model. Multiple Layer 2 cores may coexist under one Layer 1.
- **Layer 3** is where practical workflows live. Bundles generate documents,
  reports, scaffolds, assets, and other delivery outputs under the governance
  rules inherited from Layer 1 and Layer 2.

## Scope of This Set

This governance foundation set:

- Defines the three-layer architecture and its boundaries
- Establishes document authority, ownership, and promotion rules
- Provides a conceptual bundle taxonomy
- Defines governance lifecycle expectations
- Establishes a common metadata standard for machine-readable classification

### Explicitly Excluded

Layer 1 governance does **not** define:

- Runtime architecture or execution engine internals
- Install, publish, deploy, or registry procedures
- Platform-specific operating standards
- Repository-specific operating instructions
- Concrete workflow bundle inventories or artifact path contracts
- Prompts, context extensions, or validators for specific workflows

If a statement requires knowledge of how a specific platform executes,
installs, validates, stores, or publishes something, it does not belong in
Layer 1.

## Stability

Layer 1 governance is designed to remain stable across multiple Layer 2
platform cores. A change to how a specific platform operates should not
require a change to Layer 1. If Layer 1 changes every time a platform
changes, the boundary has drifted and must be restored.
