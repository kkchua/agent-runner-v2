---
template_id: "SYS-00-IDX"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 governance foundation index document"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-0864b1f2"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Layer 1 Governance Foundation

## Overview

This document set defines the Layer 1 governance foundation for the
ecosystem. Layer 1 is the ecosystem constitution: it defines the
non-negotiable governance model that applies across all Layer 2 platform
cores and all Layer 3 workflow bundles that choose to adopt this
architecture.

Layer 1 answers the following questions:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed?
- What does each layer own?
- What is forbidden in each layer?
- How are governance documents structured?
- How are ownership, review, approval, and change authority defined?

## Scope

Layer 1 governs only cross-ecosystem concerns:

- layer definitions and ownership boundaries
- document authority and promotion rules
- document metadata classification rules
- bundle taxonomy at a conceptual level
- governance lifecycle and change control principles
- review and approval obligations

Layer 1 excludes all runtime and platform implementation detail. It does
not define runtime architecture, install procedures, publish procedures,
registry operations, platform-specific contracts, or bundle-local artifact
mappings. Those concerns belong to Layer 2 (platform/domain core) and
Layer 3 (concrete workflow bundles).

## Document Map

This governance foundation set contains the following permanent documents:

| # | Document | Template ID | Description |
|---|---|---|---|
| 1 | `README.md` | `SYS-00-IDX` | Governance foundation index (this document). |
| 2 | `LAYER_MODEL.md` | `SYS-00-LM` | Three-layer architecture definition and boundaries. |
| 3 | `DOCUMENT_AUTHORITY.md` | `SYS-00-DA` | Document authority classes, promotion rules, and ownership matrix. |
| 4 | `BUNDLE_TAXONOMY.md` | `SYS-00-BT` | Conceptual bundle taxonomy and ownership rules. |
| 5 | `GOVERNANCE_LIFECYCLE.md` | `SYS-00-GL` | Lifecycle states, approval, publication, and promotion interaction. |
| 6 | `METADATA_STANDARD.md` | `SYS-00-MS` | Required metadata fields, baseline vocabularies, and scanner rules. |

The document map includes this index document so the published set
inventory remains six documents.

## Audience

Primary audiences:

- ecosystem owners and architecture owners
- platform-core authors (Layer 2 designers)
- workflow framework designers

Secondary audiences:

- workflow bundle authors (Layer 3 designers)
- reviewers and auditors

## Relationship to Lower Layers

Layer 1 defines what must be governed and who owns what. Layer 2
translates Layer 1 governance into a platform-specific operating model.
Layer 3 produces concrete workflow bundles and delivery outputs under the
rules established by Layers 1 and 2.

The dependency direction flows downward: Layer 3 depends on Layer 2,
Layer 2 depends on Layer 1. No lower layer may silently absorb or redefine
responsibilities from a higher layer.

## Status

These documents are staged run outputs with `lifecycle_status: "draft"`.
They are not active published documents until they pass review,
validation, audit, and human approval, and are published by the publish
step.
