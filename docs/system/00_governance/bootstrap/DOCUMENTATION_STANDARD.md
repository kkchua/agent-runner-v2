---
template_id: "SYS-00-DS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-17T06:15:00+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "generate_layer1_governance_docs"
change_id: "00L1-20260716-4841a345"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `generate_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation authority, structure rules, and validation requirements for the Layer 1 ecosystem governance set. It governs only the four permanent Layer 1 documents and does not extend to repository-local outputs or plugin workflow bundle documentation.

## Audience Model

Layer 1 documentation serves multiple audiences with distinct access patterns:

| Audience | Role | Primary Concern |
|----------|------|-----------------|
| Runtime Operators | Operate the plugin workflow system | Control-plane behavior, bundle management, validation gates |
| Workflow Authors | Create and maintain workflow bundles | Bundle taxonomy, ownership boundaries, packaging rules |
| Documentation Authors | Maintain governance documents | Structure requirements, update triggers, validation rules |
| Auditors | Verify compliance | Governance contracts, ownership proof, change control |

Each audience reads documentation with different goals. The document structure accommodates all access patterns without duplication.

## Document Set

The Layer 1 governance set contains exactly four documents:

| Document | Template ID | Scope |
|----------|-------------|-------|
| README.md | SYS-00-IDX | Index and navigation for Layer 1 governance |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Documentation authority and structure rules |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle classification and ownership |
| RUNTIME_GOVERNANCE.md | SYS-00-RG | Runtime control-plane and validation |

No other documents belong to Layer 1. Repository-specific documents, workflow-specific templates, and generated artifacts belong to Layer 2 or Layer 3.

## Architecture Baseline

Layer 1 documents follow these structural rules:

### File Location

All Layer 1 documents reside under `docs/system/00_governance/bootstrap/`. This location is fixed and does not vary by repository.

### Frontmatter Requirements

Each document includes YAML frontmatter with these required fields:

| Field | Value Pattern |
|-------|---------------|
| template_id | Fixed identifier from template registry |
| version | Semantic version string |
| doc_type | "system" for Layer 1 documents |
| managed_by | "workflow-generated" |
| generated_at | ISO 8601 timestamp |
| workflow | Workflow identifier that produced the document |
| step | Step identifier that produced the document |
| change_id | Unique identifier for the generation job |

### Workflow-Managed Protection

Each document includes a workflow-managed protection banner immediately after frontmatter. This banner identifies the owning workflow and step, and declares the document protected from manual edits.

### Section Requirements

Each document defines required sections. Documents must contain all required sections in the specified order. Additional sections are permitted after required sections.

## Conditional Standards

### ASCII Character Restriction

Layer 1 document body text must use ASCII characters only. Smart quotes, em dashes, en dashes, replacement characters, and other non-ASCII punctuation are prohibited.

### No Concrete Workflow Identifiers in Body Text

Layer 1 documents must not include concrete workflow identifiers matching patterns like `XX_workflow_name_vN` in body text. Concrete identifiers are permitted only in YAML frontmatter and the workflow-managed protection banner.

### No Repository-Specific Artifact Names

Layer 1 documents must not enumerate repository-derived artifact names. Governance applies generically to any repository using the plugin workflow system.

### Layer Separation

Layer 1 documents must not define:
- Repository workflow inventories
- Repository-specific scaffold names
- Plugin bundle names
- Generated artifact filenames

## Update Triggers

Layer 1 documents are updated only through the governance bootstrap workflow. Manual edits are prohibited.

Update triggers include:

| Trigger | Affected Documents |
|---------|-------------------|
| Bundle taxonomy change | BUNDLE_TAXONOMY.md, README.md |
| Runtime control-plane change | RUNTIME_GOVERNANCE.md, README.md |
| Documentation standard change | DOCUMENTATION_STANDARD.md, README.md |
| New Layer 1 document added | README.md (document map) |

All updates require regeneration through the governance bootstrap workflow to preserve frontmatter consistency and workflow-managed protection.

## Validation

Layer 1 documents undergo validation during the governance bootstrap workflow. Validation checks include:

| Check | Description |
|-------|-------------|
| Frontmatter completeness | All required fields present and correctly typed |
| Section presence | All required sections present in correct order |
| ASCII compliance | No non-ASCII characters in body text |
| Scope purity | No repository-specific content or concrete workflow identifiers |
| Ownership correctness | Each document matches its template ID and scope |

Validation failures block governance bootstrap completion. Review and remediation are required before approval.