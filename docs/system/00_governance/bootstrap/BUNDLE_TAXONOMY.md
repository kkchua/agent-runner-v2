---
template_id: "SYS-00-BT"
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

# Bundle Taxonomy

This document defines the bundle classes, ownership rules, and packaging rules
for the plugin workflow ecosystem. It establishes WHAT bundles ARE and WHO owns
them, without defining HOW they are loaded or resolved at runtime.

## Bundle Classes

The ecosystem defines three bundle classes:

### Core Governance Bundles

Core governance bundles contain the foundational governance documents and
runtime infrastructure for the workflow orchestration system.

**Characteristics:**

- Define ecosystem-wide governance rules
- Establish documentation standards and validation gates
- Provide runtime control plane definitions
- Must remain stable and rarely change

**Examples:**

- Layer 1 governance document bundles
- System bootstrap bundles
- Runtime control plane bundles

### Plugin Workflow Bundles

Plugin workflow bundles contain self-contained workflow definitions with their
associated prompts, actions, and context extensions.

**Characteristics:**

- Self-contained workflow definitions
- Include prompts, actions, and context extensions
- May be single-workflow or multi-workflow bundles
- Can be added, updated, or removed independently

**Bundle types:**

- **Single-workflow bundles**: Contain exactly one workflow definition
- **Multi-workflow bundles**: Contain multiple related workflow definitions

Plugin workflow bundles are the primary extension mechanism for the ecosystem.

### Domain Bundles

Domain bundles contain domain-specific logic, templates, and configurations
that support specific business domains or use cases.

**Characteristics:**

- Domain-specific business logic
- Templates and configurations for specific use cases
- May depend on core governance or plugin workflow bundles
- Managed by domain-specific teams

**Examples:**

- Delivery workflow template bundles
- Codebase analysis bundles
- Domain-specific action bundles

## Ownership Rules

### Core Governance Bundle Ownership

| Bundle Type | Owner | Change Authority |
|-------------|-------|------------------|
| Layer 1 governance docs | Layer 1 governance workflow | System architects |
| System bootstrap bundles | Bootstrap workflows | System architects |
| Runtime control plane | Runtime governance workflow | System architects |

Core governance bundles require system architect approval for changes.

### Plugin Workflow Bundle Ownership

| Bundle Type | Owner | Change Authority |
|-------------|-------|------------------|
| Single-workflow bundles | Workflow team | Workflow team lead |
| Multi-workflow bundles | Workflow team | Workflow team lead |

Plugin workflow bundles are owned by the teams that create and maintain them.

### Domain Bundle Ownership

| Bundle Type | Owner | Change Authority |
|-------------|-------|------------------|
| Domain logic bundles | Domain team | Domain team lead |
| Domain template bundles | Domain team | Domain team lead |

Domain bundles are owned by the domain-specific teams that create them.

### Ownership Principles

1. **Clear Ownership**: Every bundle has exactly one owner
2. **Change Authority**: Owners control changes to their bundles
3. **Dependency Direction**: Lower layers do not depend on higher layers
4. **Stability Guarantees**: Core governance bundles are most stable

## Packaging Rules

### Core Governance Bundle Packaging

Core governance bundles must be packaged with:

- Complete governance documentation
- Validation schemas and checks
- Version identifier in manifest
- Change log for governance changes

Packaging requirements:

- Minimal dependencies on other bundles
- Stable versioning scheme
- Comprehensive documentation
- Validation suite for governance compliance

### Plugin Workflow Bundle Packaging

Plugin workflow bundles must be packaged with:

- Workflow manifest (declarative definition)
- Prompt templates for all workflow steps
- Optional: context extensions for workflow-specific hooks
- Optional: actions for workflow-specific behaviors
- Optional: registry files for roles, connections, policies

Packaging requirements:

- Self-contained workflow definition
- No hardcoded repository paths
- Declarative manifest with complete metadata
- Version identifier in manifest

### Domain Bundle Packaging

Domain bundles must be packaged with:

- Domain logic modules
- Domain templates and configurations
- Dependency declarations on required bundles
- Version identifier in manifest

Packaging requirements:

- Clear dependency declarations
- Domain-specific documentation
- Version compatibility with dependencies
- Integration tests for domain logic

### Packaging Standards

All bundle classes must follow these packaging standards:

1. **Manifest Required**: Every bundle must have a declarative manifest
2. **Version Identifier**: Every bundle must declare its version
3. **Dependency Declaration**: Dependencies must be explicitly declared
4. **Documentation**: Every bundle must include documentation
5. **Validation**: Every bundle must pass validation checks