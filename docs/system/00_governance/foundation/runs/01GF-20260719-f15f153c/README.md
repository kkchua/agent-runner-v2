---
template_id: SYS-00-IDX
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 governance foundation index; required for operational scans"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-f15f153c"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `refine_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Layer 1 Governance Foundation

## Purpose

This is the Layer 1 governance foundation set. It defines the
ecosystem constitution: the non-negotiable governance model that applies
across all Layer 2 platform cores and all Layer 3 workflow bundles that
choose to adopt this architecture.

Layer 1 answers what must be governed, who owns what, and what may or may
not appear in lower layers. It does not define runtime mechanics,
bootstrap copy behavior, installer flow, registry internals, platform
operating standards, or execution algorithms.

## Scope

This set covers:

- the three-layer architecture model
- layer ownership boundaries and dependency direction
- document authority and promotion rules
- conceptual bundle taxonomy
- governance lifecycle rules
- metadata classification standards

This set excludes:

- runtime architecture and implementation detail
- installation, publish, deploy, or registry procedures
- platform-specific operating standards
- repository-specific operating instructions
- concrete workflow definitions
- concrete artifact path contracts
- bundle-local prompts, validators, or governance files

Those subjects belong to Layer 2 or Layer 3.

## Document Map

| Document | Template ID | Description |
|---|---|---|
| `README.md` (this file) | `SYS-00-IDX` | Governance foundation index and document map. |
| `LAYER_MODEL.md` | `SYS-00-LM` | Three-layer architecture: Layer 1, Layer 2, Layer 3, their boundaries, dependency direction, and promotion overview. |
| `DOCUMENT_AUTHORITY.md` | `SYS-00-DA` | Document authority vocabulary, authority matrix, promotion constraints, and permanent-versus-temporary artifact rules. |
| `BUNDLE_TAXONOMY.md` | `SYS-00-BT` | Conceptual bundle taxonomy and ownership rules across layers. |
| `GOVERNANCE_LIFECYCLE.md` | `SYS-00-GL` | Lifecycle states, publication rule, revision, deprecation, retirement, and promotion interaction. |
| `METADATA_STANDARD.md` | `SYS-00-MS` | Required metadata fields, allowed vocabularies, scan policy rules, scanner compliance rules, and validation expectations. |

This document map is the published set inventory. The index itself is part
of the governance set, making the complete set six documents including
this index.

## Intended Audience

**Primary audiences:**

- ecosystem owners and architecture owners
- platform-core authors and maintainers
- workflow framework designers

**Secondary audiences:**

- workflow bundle authors
- reviewers and auditors

## Relationship to Lower Layers

**Layer 2** (platform core) translates this governance into a
platform-specific operating model. Layer 2 defines runtime architecture,
platform conventions, shared services, and bundle authoring contracts for
one specific platform or domain.

**Layer 3** (workflow bundles) applies Layer 2 conventions to produce
concrete delivery outputs: workflow definitions, prompts, artifact
mappings, generated documents, and execution evidence.

Layer 1 is intentionally small and stable so it can govern many different
Layer 2 cores without change.

## Stability Expectation

This governance set should remain stable across different Layer 2
platforms. If a statement becomes false when switching from one platform
to another, it does not belong in Layer 1.

Changes to this set require explicit review, validation, audit, and human
approval before activation.
