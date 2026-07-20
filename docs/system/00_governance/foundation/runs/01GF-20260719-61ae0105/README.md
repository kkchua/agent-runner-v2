---
template_id: "SYS-00-IDX"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "primary index for the Layer 1 governance foundation set"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-61ae0105"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `refine_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Layer 1 Governance Foundation

## Mission

Layer 1 is the ecosystem constitution. It defines the non-negotiable
governance model that applies across all Layer 2 platform cores and all
Layer 3 workflow bundles that adopt this architecture.

Layer 1 exists to answer these questions:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed?
- What does each layer own?
- What is forbidden in each layer?
- How are governance documents structured?
- How are ownership, review, approval, and change authority defined?

## Scope

This governance foundation set defines:

- the three-layer architecture and its boundaries
- document authority, ownership, and promotion rules
- conceptual bundle taxonomy
- governance lifecycle expectations
- cross-ecosystem metadata standards

Layer 1 explicitly excludes:

- runtime architecture and implementation detail
- platform-specific operating procedures
- install, publish, deploy, or registry mechanics
- concrete workflow definitions or artifact mappings
- repository-specific operating instructions
- Layer 3 output inventories

If a statement requires knowledge of how a specific platform executes,
installs, validates, stores, or publishes something, it does not belong in
Layer 1.

## System Documentation Index

This governance foundation set provides the constitutional baseline for
the entire ecosystem. It establishes the layer model, authority
definitions, bundle taxonomy, lifecycle expectations, and metadata rules
that all lower layers must inherit and apply.

The set is designed for stability and reusability across multiple Layer 2
platform cores. Changes to Layer 1 governance require explicit review and
approval through the lifecycle defined in `GOVERNANCE_LIFECYCLE.md`.

## Document Map

This governance set contains six permanent documents:

| # | Document | Artifact Key | Purpose |
|---|----------|-------------|---------|
| 1 | `README.md` | `L1_FOUNDATION_INDEX` | Governance set index, mission, and document map. |
| 2 | `LAYER_MODEL.md` | `L1_LAYER_MODEL` | Three-layer architecture, boundaries, and dependency direction. |
| 3 | `DOCUMENT_AUTHORITY.md` | `L1_DOCUMENT_AUTHORITY` | Authority vocabulary, matrix, promotion, and permanence rules. |
| 4 | `BUNDLE_TAXONOMY.md` | `L1_BUNDLE_TAXONOMY` | Conceptual bundle taxonomy at the governance level. |
| 5 | `GOVERNANCE_LIFECYCLE.md` | `L1_GOVERNANCE_LIFECYCLE` | Lifecycle states, approval, publication, and retirement rules. |
| 6 | `METADATA_STANDARD.md` | `L1_METADATA_STANDARD` | Required metadata fields, baseline vocabularies, and scanner rules. |

All six documents are permanent Layer 1 governance standards. This index
includes itself so the published set inventory remains six documents, not
five companions plus an implicit index.

## Audience

Primary audiences:

- ecosystem owners and architecture owners
- platform-core authors
- workflow framework designers

Secondary audiences:

- workflow bundle authors
- reviewers and auditors

## Relationship to Other Layers

- **Layer 1** (this set) defines governance rules that all layers inherit.
- **Layer 2** translates these rules into platform-specific operating
  models.
- **Layer 3** applies platform rules within concrete workflow bundles.

No lower layer may redefine the meaning of Layer 1 governance. Layer 2
may extend Layer 1 rules for platform needs. Layer 3 inherits rules from
its parent Layer 2.

## Design Authority

This governance set is generated from human-authored masterplan inputs:

- `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md`
- `masterplan/LAYER1_WORKFLOW_SPECIFICATION.md`

These masterplan documents are the reference blueprints. They remain
`human-authored` and are excluded from operational scans. This generated
set is the canonical `workflow-generated` governance baseline.

## Stability

Layer 1 governance is designed to remain stable across:

- multiple Layer 2 platform cores (AI-driven SDLC, ComfyUI, n8n,
  agent-runner-v2, and future platforms)
- changes in platform implementation underneath
- addition of new Layer 3 workflow bundles

Layer 1 changes require explicit governance review and promotion through
the lifecycle defined in `GOVERNANCE_LIFECYCLE.md`.