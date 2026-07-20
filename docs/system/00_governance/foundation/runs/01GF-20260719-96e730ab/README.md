---
template_id: SYS-00-IDX
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
managed_by: workflow-generated
scan_policy: "include"
scan_reason: "Layer 1 governance foundation index; included in operational scans"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-96e730ab"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `generate_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Layer 1 Governance Foundation

## Overview

The Layer 1 Governance Foundation defines the ecosystem constitution:
the non-negotiable governance model that applies across all Layer 2
platform cores and all Layer 3 workflow bundles that adopt this
architecture.

Layer 1 answers the following questions:

- What is the purpose and structure of the ecosystem?
- What does each layer own, and what must each layer not define?
- How are document authority, ownership, and promotion governed?
- How are governance documents classified, scanned, and validated?
- How do documents move through creation, review, approval, publication,
  and retirement?

Layer 1 defines governance only. It does not define runtime architecture,
platform-specific operating procedures, installation flows, publish
mechanics, registry operations, or concrete bundle inventories.

## Document Map

The Layer 1 Governance Foundation consists of six permanent documents:

| # | Document | Template ID | Purpose |
|---|----------|-------------|---------|
| 1 | `README.md` | `SYS-00-IDX` | Index and overview of the Layer 1 governance set. |
| 2 | `LAYER_MODEL.md` | `SYS-00-LM` | Definition of Layer 1, Layer 2, and Layer 3, their boundaries, dependency direction, and promotion overview. |
| 3 | `DOCUMENT_AUTHORITY.md` | `SYS-00-DA` | Authority vocabulary, document authority matrix, promotion constraints, and permanent-versus-temporary rules. |
| 4 | `BUNDLE_TAXONOMY.md` | `SYS-00-BT` | Conceptual bundle taxonomy and ownership rules for bundle classes. |
| 5 | `GOVERNANCE_LIFECYCLE.md` | `SYS-00-GL` | Lifecycle states, approval versus publication, revision, deprecation, retirement, and promotion interaction. |
| 6 | `METADATA_STANDARD.md` | `SYS-00-MS` | Required metadata fields, baseline vocabularies, scan policy rules, scanner compliance rules, and validation expectations. |

## Intended Audience

Primary audiences for Layer 1 governance:

- Ecosystem owners and architecture owners
- Platform-core authors designing a new Layer 2 core
- Workflow framework designers building governance-aware tooling

Secondary audiences:

- Workflow bundle authors who need to understand governance boundaries
- Reviewers and auditors evaluating document compliance

## Layer 1 Scope Boundary

Layer 1 owns only cross-ecosystem governance concerns:

- Layer definitions and ownership boundaries
- Document authority model and promotion rules
- Document metadata classification rules
- Bundle taxonomy at a conceptual level
- Lifecycle and change control principles
- Review, validation, and audit obligations at the principle level

Layer 1 excludes:

- Runtime architecture and implementation details
- Platform-specific operating procedures
- Installation, publish, deploy, or registry mechanics
- Concrete workflow bundle inventories
- Concrete artifact path contracts
- Repository-specific operating instructions
- Layer 3 output inventories

## Relationship to Other Layers

Layer 1 sits at the top of a three-layer architecture:

- **Layer 2** translates Layer 1 governance into a platform-specific
  operating model. Each Layer 2 core applies Layer 1 rules to its
  own runtime, conventions, and bundle ecosystem.
- **Layer 3** contains concrete workflow bundles and their delivery
  outputs. Each bundle inherits governance rules from Layer 1 and
  platform conventions from its parent Layer 2.

Layer 1 must remain stable across different Layer 2 cores and must not
contain content that becomes false when switching platforms.

## Status

This document set is a staged draft. It becomes the active Layer 1
governance set only after review, validation, audit, and explicit human
approval followed by publication.
