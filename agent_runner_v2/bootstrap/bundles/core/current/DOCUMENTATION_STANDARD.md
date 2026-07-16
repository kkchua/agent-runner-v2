---
template_id: "SYS-00-DS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T10:05:56+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "generate_layer1_governance_docs"
change_id: "00L1-20260716-e4c16ad4"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `generate_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation authority and structure rules for the
Layer 1 ecosystem governance master documents. It establishes the standards
that govern how the four Layer 1 documents are organized, maintained, and
validated.

## Audience Model

Layer 1 governance documents serve multiple audiences:

| Audience | Role | Document Focus |
|----------|------|----------------|
| System Architects | Define ecosystem governance | DOCUMENTATION_STANDARD.md, BUNDLE_TAXONOMY.md |
| Runtime Operators | Manage workflow execution | RUNTIME_GOVERNANCE.md |
| Workflow Developers | Create plugin workflow bundles | BUNDLE_TAXONOMY.md, RUNTIME_GOVERNANCE.md |
| Repository Owners | Adopt governance for repositories | All four documents |

Each audience should be able to understand the governance model from their
primary documents without needing to read the full document set.

## Document Set

The Layer 1 document set consists of exactly four files:

### README.md (SYS-00-IDX)

- **Purpose**: Index and layering model explanation
- **Audience**: All audiences
- **Content**: Document map, audience views, layering model overview
- **Ownership**: Layer 1 governance workflow

### DOCUMENTATION_STANDARD.md (SYS-00-DS)

- **Purpose**: Documentation authority and structure rules
- **Audience**: System architects, repository owners
- **Content**: Audience model, document set, architecture baseline, validation
- **Ownership**: Layer 1 governance workflow

### BUNDLE_TAXONOMY.md (SYS-00-BT)

- **Purpose**: Bundle classes and ownership rules
- **Audience**: System architects, workflow developers
- **Content**: Bundle class definitions, ownership rules, packaging rules
- **Ownership**: Layer 1 governance workflow

### RUNTIME_GOVERNANCE.md (SYS-00-RG)

- **Purpose**: Runtime operating model
- **Audience**: Runtime operators, workflow developers
- **Content**: Publish/install model, registry control, validation gates
- **Ownership**: Layer 1 governance workflow

## Architecture Baseline

### Layer Separation

Layer 1 documents must remain strictly separated from Layer 2 and Layer 3
concerns:

- **Layer 1**: Ecosystem governance (this directory)
- **Layer 2**: Repository master docs (repository-specific)
- **Layer 3**: Plugin workflow outputs (execution-generated)

Layer 1 documents must not reference concrete workflow identifiers,
repository-specific artifact names, or repository-specific output paths.

### Template Identification

Each Layer 1 document has a unique template ID:

| Document | Template ID |
|----------|-------------|
| README.md | SYS-00-IDX |
| DOCUMENTATION_STANDARD.md | SYS-00-DS |
| BUNDLE_TAXONOMY.md | SYS-00-BT |
| RUNTIME_GOVERNANCE.md | SYS-00-RG |

Template IDs are used in YAML frontmatter for document identification and
validation.

### Ownership Boundaries

Each Layer 1 document is owned by the Layer 1 governance workflow that
generates it. Ownership means:

- The workflow is responsible for document creation and updates
- Manual edits are not permitted (workflow-managed protection)
- Document changes require workflow execution

## Conditional Standards

### Scope Purity

Layer 1 documents must maintain scope purity:

- No concrete workflow identifiers in body text (frontmatter/banner only)
- No repository-specific artifact names
- No repository-specific scaffold names
- No repository-specific output examples

### Format Requirements

All Layer 1 documents must:

- Use YAML frontmatter with required fields
- Include the workflow-managed protection banner
- Use ASCII characters only in body text
- Follow markdown formatting standards

### Content Exclusions

Layer 1 documents must not contain:

- Concrete workflow identifier patterns in body text
- Placeholder syntax for artifact keys
- References to specific delivery scaffold workflows
- Enumeration of repo-derived artifacts

## Update Triggers

Layer 1 documents should be updated when:

1. Bundle taxonomy changes (new bundle classes, ownership changes)
2. Runtime model changes (publish/install procedures, validation gates)
3. Documentation structure changes (new Layer 1 documents, format changes)
4. Governance rules change (ownership boundaries, validation requirements)

Updates must be made through the Layer 1 governance workflow, not through
direct file editing.

## Validation

Layer 1 documents are validated by the workflow that generates them. Validation
checks include:

### Scope Purity Checks

- No concrete workflow identifiers in body text
- No repository-specific artifact names
- No repository-specific output paths

### Ownership Checks

- Correct template IDs in frontmatter
- Workflow-managed banner present
- Generated timestamp recorded

### Consistency Checks

- Cross-references between documents are valid
- Layering model is correctly described
- Bundle taxonomy aligns with runtime governance

Validation failures result in workflow rejection and require prompt refinement
to correct issues.