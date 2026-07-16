---
template_id: "SYS-00-IDX"
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

# System Documentation Index

This index describes the Layer 1 ecosystem governance documentation set. These documents define reusable governance contracts that apply across repositories and plugin workflow ecosystems.

## Layering Model

The documentation architecture follows a three-layer model:

1. **Layer 1 - Ecosystem Governance**: Permanent, reusable governance documents that define documentation authority, bundle taxonomy, runtime control-plane expectations, and validation gates. These documents are repository-agnostic and apply to any ecosystem using the plugin workflow system.

2. **Layer 2 - Repository Master Documentation**: Repository-specific master documents that define local workflow inventories, operating structures, and repository-specific governance extensions. These documents adapt Layer 1 governance to a specific repository context.

3. **Layer 3 - Plugin Workflow Families**: Workflow-specific documentation, templates, and generated outputs produced by plugin workflow bundles. Each workflow bundle owns its artifact path contracts and generated document inventories.

Layer 1 documents remain stable across repositories. Layer 2 and Layer 3 documents vary per repository and workflow bundle.

## Audience Views

Different audiences access documentation through distinct entry points:

| Audience | Primary Entry Point | Purpose |
|----------|---------------------|---------|
| Runtime Operators | RUNTIME_GOVERNANCE.md | Understand control-plane, bundle publish/install, validation gates |
| Workflow Authors | BUNDLE_TAXONOMY.md | Understand bundle classes, ownership rules, packaging requirements |
| Documentation Authors | DOCUMENTATION_STANDARD.md | Understand document structure, validation, and update triggers |
| All Audiences | README.md | Navigate the Layer 1 documentation set |

## Document Map

The Layer 1 governance set contains four permanent documents:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| README.md | SYS-00-IDX | Index and navigation for Layer 1 governance documents |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Documentation authority, structure rules, and validation requirements |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle class definitions, ownership rules, and packaging standards |
| RUNTIME_GOVERNANCE.md | SYS-00-RG | Runtime control-plane, bundle publish/install, validation gates, and parity rules |

## Repository-Local Outputs

Repository-specific documentation outputs live under `docs/repo/` and are outside Layer 1 ownership. These include:

- Repository workflow inventories
- Repository-specific SDLC documentation
- Generated architecture and developer guides
- Delivery and initiative artifacts
- Audience-specific documentation sites

Layer 1 governance does not define the content, structure, or ownership of repository-local outputs. Plugin workflow bundles own their generated artifact paths and document inventories under `docs/repo/`.

## Related Documentation

For repository-specific governance and workflow inventories, consult Layer 2 master documentation in the repository's governance folder. For workflow-specific artifact paths and generated documents, consult the plugin workflow bundle definitions.