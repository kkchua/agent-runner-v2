---
template_id: SYS-00-IDX
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 1 governance foundation index; must be included in operational scans"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-c5e882c3"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Layer 1 Governance Foundation

## Purpose

The Layer 1 Governance Foundation defines the ecosystem constitution --
the non-negotiable governance model that applies across all Layer 2
platform cores and all Layer 3 workflow bundles that adopt this
architecture.

Layer 1 answers these questions:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed?
- What does each layer own?
- What is forbidden in each layer?
- How are governance documents structured?
- How are ownership, review, approval, and change authority defined?

## Scope

This governance set is Layer 1 only. It defines cross-ecosystem
governance rules and excludes:

- runtime architecture and implementation
- install, publish, deploy, or registry procedures
- platform-specific operating standards
- concrete workflow definitions and artifact mappings
- repository-specific operating instructions

These subjects belong to Layer 2 (platform/domain constitutions) or
Layer 3 (concrete workflow bundles).

## Audience

Primary audiences:

- ecosystem owners and architecture owners
- platform-core authors and workflow framework designers

Secondary audiences:

- workflow bundle authors
- reviewers and auditors

## Document Map

This governance foundation set contains six permanent documents:

| Document | File | Template ID | Description |
|---|---|---|---|
| Foundation Index | `README.md` | `SYS-00-IDX` | This document. Indexes the governance set, states mission and scope. |
| Layer Model | `LAYER_MODEL.md` | `SYS-00-LM` | Defines Layer 1, Layer 2, Layer 3, their boundaries, dependency direction, and promotion overview. |
| Document Authority | `DOCUMENT_AUTHORITY.md` | `SYS-00-DA` | Defines authority vocabulary, document authority matrix, promotion constraints, and permanent-vs-temporary rules. |
| Bundle Taxonomy | `BUNDLE_TAXONOMY.md` | `SYS-00-BT` | Defines the conceptual bundle taxonomy and ownership rules. Workflow-specific artifact contracts are not owned by Layer 1. |
| Governance Lifecycle | `GOVERNANCE_LIFECYCLE.md` | `SYS-00-GL` | Defines lifecycle states, approval versus publication, revision, deprecation, retirement, and promotion interaction. |
| Metadata Standard | `METADATA_STANDARD.md` | `SYS-00-MS` | Defines required metadata fields, baseline vocabularies, scan policy rules, scanner compliance rules, and validation expectations. |

## Relationship to Other Layers

Layer 1 is the ecosystem constitution. It is stable, small, and
platform-independent. It does not change when a specific platform
implementation changes.

Layer 2 translates Layer 1 governance into a platform-specific operating
model. Each Layer 2 core (AI-driven SDLC, ComfyUI, n8n,
agent-runner-v2, etc.) defines its own runtime architecture, shared
services, and bundle-authoring contracts.

Layer 3 contains concrete workflow bundles that produce delivery outputs
within a specific Layer 2 context.

Dependency direction is downward only: Layer 3 depends on Layer 2, Layer 2
depends on Layer 1. No lower layer may redefine a higher layer.

## Document Status

This is a staged run output. Documents carry `lifecycle_status: "draft"`.
They become active only after review, validation, audit, human approval,
and publication through the `01_governance_foundation_v1` workflow.
