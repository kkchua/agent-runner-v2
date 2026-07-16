---
template_id: "SYS-00-BT"
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

# Bundle Taxonomy

## Bundle Classes

The plugin workflow system defines three bundle classes with distinct ownership and packaging characteristics.

### Core Governance Bundles

Core governance bundles provide permanent ecosystem governance documents. They define reusable contracts that apply across repositories and plugin workflow ecosystems.

| Attribute | Value |
|-----------|-------|
| Scope | Ecosystem-wide, repository-agnostic |
| Ownership | Layer 1 governance bootstrap workflow |
| Artifacts | Layer 1 governance documents under system governance folder |
| Mutability | Updated only through governance bootstrap workflow |

Core governance bundles produce the Layer 1 document set: README.md, DOCUMENTATION_STANDARD.md, BUNDLE_TAXONOMY.md, and RUNTIME_GOVERNANCE.md. These documents remain stable and reusable across repositories.

### Plugin Workflow Bundles

Plugin workflow bundles provide workflow-specific logic, templates, and artifact generation. Each bundle owns its execution steps, prompt templates, and artifact contracts.

| Attribute | Value |
|-----------|-------|
| Scope | Repository-specific, workflow-specific |
| Ownership | Workflow bundle author |
| Artifacts | Workflow-generated documents, templates, and supporting files |
| Mutability | Updated through workflow bundle development lifecycle |

Plugin workflow bundles may be either:
- **Single-workflow bundles**: Contain one workflow with its steps, prompts, and artifact contracts
- **Multi-workflow bundles**: Contain multiple related workflows sharing templates and context extensions

Each plugin workflow bundle owns its artifact path contracts, including:
- Canonical output paths for generated documents
- Review and validation path rules
- Generated document inventory and naming conventions
- Protected document identification

### Domain Bundles

Domain bundles provide domain-specific extensions, including specialized templates, coder role definitions, and domain-specific context builders.

| Attribute | Value |
|-----------|-------|
| Scope | Domain-specific, potentially cross-repository |
| Ownership | Domain specialist or workflow author |
| Artifacts | Domain templates, role definitions, context extensions |
| Mutability | Updated through domain bundle development lifecycle |

Domain bundles extend plugin workflow bundles with domain-specific behavior without modifying core workflow logic.

## Ownership Rules

### Core Governance Ownership

Core governance bundles have strict ownership rules:

1. Only the governance bootstrap workflow may modify Layer 1 documents
2. Layer 1 documents are workflow-generated and protected from manual edits
3. No plugin workflow bundle may override Layer 1 governance contracts
4. Changes to core governance require regeneration through the governance bootstrap workflow

### Plugin Workflow Bundle Ownership

Plugin workflow bundles own their internal structure and output contracts:

1. Each bundle owns its workflow definition, steps, and routing logic
2. Each bundle owns its prompt templates and context extensions
3. Each bundle owns its artifact path contracts and generated document inventory
4. Bundles must not modify Layer 1 governance documents
5. Bundles must not interfere with other bundles' artifact paths

### Shared Runtime Code Ownership

Shared runtime code provides generic infrastructure:

1. Generic path helpers for constructing artifact paths
2. Generic enforcement for document protection and validation
3. Generic execution infrastructure for workflow steps

Shared runtime code must not own:
- Workflow-specific document output paths
- Workflow-name-specific path resolution branches
- Centralized workflow-family path registries

Workflow bundles own workflow-specific path contracts. Shared runtime provides only generic infrastructure.

## Packaging Rules

### Core Governance Packaging

Core governance bundles are packaged as part of the core bundle set:

| Rule | Description |
|------|-------------|
| Location | Packaged with core runtime distribution |
| Versioning | Follows runtime versioning, not workflow versioning |
| Distribution | Included in global runtime bundle copy |
| Activation | Automatically available to all repositories |

### Plugin Workflow Bundle Packaging

Plugin workflow bundles are self-contained packages:

| Rule | Description |
|------|-------------|
| Self-containment | Bundle contains all prompts, templates, and context extensions |
| Manifest | Bundle includes declarative workflow manifest |
| Versioning | Each bundle versions independently |
| Distribution | Published to global bundle registry for runtime discovery |

### Domain Bundle Packaging

Domain bundles extend plugin workflow bundles:

| Rule | Description |
|------|-------------|
| Extension model | Domain bundles extend, not replace, plugin workflow bundles |
| Dependency | Domain bundles declare dependencies on base plugin workflow bundles |
| Versioning | Domain bundles version independently of base bundles |
| Distribution | Published to global bundle registry alongside base bundles |

## Artifact Ownership Enforcement

The system enforces artifact ownership through validation gates:

1. **Layer 1 protection**: Layer 1 documents reject modifications from plugin workflow bundles
2. **Bundle isolation**: Plugin workflow bundles cannot modify artifacts owned by other bundles
3. **Path contract enforcement**: Runtime validates that bundles write only to their declared artifact paths
4. **Workflow-generated verification**: Documents declare workflow ownership in frontmatter and protection banner

Validation failures block workflow completion. Remediation requires correcting bundle artifact path declarations or workflow step logic.