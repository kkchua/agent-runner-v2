---
template_id: "SYS-00-DS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-15T22:38:14+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "generate_layer1_governance_docs"
change_id: "00L1-20260715-74497d6b"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `generate_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation authority, structure rules, and
validation criteria for the four Layer 1 ecosystem governance documents. It
governs only the Layer 1 document set and does not prescribe rules for
repository-level or workflow-level documentation.

Layer 1 governance documents are the permanent, reusable policy foundation for
plugin workflow ecosystems. They must remain free of repository-specific
content, concrete workflow identifiers, and repository-derived artifact names.

## Audience Model

The Layer 1 documentation standard addresses three audience profiles:

1. **Ecosystem architects** — responsible for maintaining governance policy
   across repositories. They need clear ownership boundaries and structure
   rules to ensure consistency.

2. **Repository maintainers** — responsible for adapting Layer 1 policy to a
   specific repository. They need to understand which rules are fixed at
   Layer 1 and which are open to repository-level adaptation at Layer 2.

3. **Plugin workflow authors** — responsible for creating workflow bundles
   that conform to governance expectations. They need to understand the
   documentation set's scope and validation gates.

## Document Set

The Layer 1 document set consists of exactly four permanent documents:

| Document | Template ID | Scope |
|----------|-------------|-------|
| README.md | SYS-00-IDX | Documentation index, three-layer model, audience views, and document map. |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | This document. Documentation authority, structure rules, and validation criteria. |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle class definitions, ownership boundaries, and packaging rules. |
| RUNTIME_GOVERNANCE.md | SYS-00-RG | Steady-state runtime model, publish/install, registry, validation, and parity rules. |

No additional documents may be added to the Layer 1 set without governance
workflow approval. Review, validation, and audit artifacts are supporting
evidence only and are not part of the permanent Layer 1 document set.

## Architecture Baseline

Every Layer 1 document must conform to the following baseline:

- **Frontmatter.** Each document must include YAML frontmatter with the
  fields: `template_id`, `version`, `doc_type`, `managed_by`,
  `generated_at`, `workflow`, `step`, and `change_id`. The `doc_type` field
  must be `system` for all Layer 1 documents.

- **Protection banner.** Immediately after frontmatter, each document must
  include the workflow-managed protection banner stating the owning workflow
  and step, and that the file is protected from manual edits.

- **Scope purity.** Layer 1 documents must not contain concrete workflow
  identifiers, repository-specific artifact names, repository-specific
  output paths, or provider authentication flows. The documents must remain
  generic enough to govern plugin workflow ecosystems across repositories.

- **Layering respect.** Layer 1 documents must not define repository-level
  workflow inventories, repository-specific scaffold names, or
  SDLC-specific outputs. Those concerns belong to Layer 2.

## Conditional Standards

The following conditional rules apply to the Layer 1 document set:

- **Versioning.** All Layer 1 documents share version `1.0.0`. A version bump
  across all four documents requires a new governance bootstrap run with a
  new change ID.

- **Cross-references.** Layer 1 documents may cross-reference each other by
  filename and template ID. They must not reference Layer 2 or Layer 3
  documents by concrete path, as those paths are repository-specific.

- **Section requirements.** Each document has a fixed set of required
  sections. These sections must exist and be populated. Optional subsections
  may be added within required sections but must not introduce
  repository-specific content.

- **No repo-derived artifacts.** Layer 1 documents must not enumerate or
  reference repository-derived artifact names. The document set is
  ecosystem-level policy only.

## Update Triggers

Layer 1 documents may be updated only through the governance bootstrap
workflow. The following triggers warrant a re-generation cycle:

1. **Runtime model changes.** When the publish/install, registry, or
   execution mode parity model changes at the framework level.

2. **Bundle taxonomy changes.** When a new bundle class is introduced or
   ownership boundaries shift.

3. **Documentation structure changes.** When required sections, frontmatter
   fields, or protection banner rules change.

4. **Validation gate changes.** When validation criteria or gates are added,
   removed, or modified.

Manual edits to Layer 1 documents are prohibited. All changes must flow
through the governance bootstrap workflow's generate, review, refine,
validate, and audit cycle.

## Validation

The governance bootstrap workflow enforces the following validation checks on
the Layer 1 document set:

- **File existence.** All four required documents must exist on disk at the
  canonical paths under `docs/system/00_governance/bootstrap/`.

- **Frontmatter integrity.** Each document must include all required
  frontmatter fields with correct values for `template_id`, `version`,
  `doc_type`, `managed_by`, `generated_at`, `workflow`, `step`, and
  `change_id`.

- **Protection banner.** Each document must include the workflow-managed
  protection banner immediately after frontmatter.

- **Required sections.** Each document must contain all required sections as
  specified in the governance contract.

- **Scope purity.** No document body text may contain concrete workflow
  identifiers, repository-derived artifact names, or provider authentication
  flows.

- **No forbidden tokens.** No document may contain placeholder artifact key
  tokens or references to repository-specific scaffold workflow names.

Validation failures trigger the refinement loop. If refinement is exhausted,
the workflow reports a human-retry-required failure and does not accept the
changes.
