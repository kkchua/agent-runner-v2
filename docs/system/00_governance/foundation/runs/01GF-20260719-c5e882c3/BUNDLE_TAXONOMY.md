---
template_id: SYS-00-BT
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 1 bundle taxonomy; defines conceptual bundle classes and ownership rules"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-c5e882c3"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `generate_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the conceptual bundle taxonomy for the ecosystem.
It establishes the classes of bundles that may exist, what each class
owns, and how bundle ownership relates to the layer model.

This is a governance-level taxonomy. It does not define concrete workflow
implementations, artifact path contracts, or bundle-specific operating
procedures. Those belong to Layer 2 (platform conventions) and Layer 3
(concrete bundle definitions).

## Bundle Classes

### Governance Bundle

A governance bundle owns and maintains cross-ecosystem governance
artifacts.

**Owning layer**: Layer 1.

**Purpose**: Produce and maintain the ecosystem constitution -- layer
definitions, authority rules, metadata standards, lifecycle rules, and
conceptual bundle taxonomy.

**Produces**: Permanent governance documents (`doc_type: "system"`),
temporary evidence artifacts for review, validation, and audit.

**Constraints**:
- Must not define runtime architecture.
- Must not define platform-specific operating procedures.
- Must not generate concrete workflow outputs for a specific domain.
- Its outputs must remain valid across multiple Layer 2 cores.

**Example**: `01_governance_foundation_v1`.

### Platform Core Bundle

A platform core bundle owns and maintains a platform or domain
constitution.

**Owning layer**: Layer 2.

**Purpose**: Translate Layer 1 governance into an operating model for one
specific platform, runtime family, or solution domain.

**Produces**: Platform constitution documents (`doc_type:
"platform_standard"` or `"system"`), shared service contracts, bundle
authoring standards, platform-specific metadata and validation contracts.

**Constraints**:
- Must identify the owning platform.
- Must not redefine Layer 1 governance.
- Must not collapse into a concrete bundle inventory.
- Must provide conventions that multiple Layer 3 bundles can follow.

**Example**: `02_platform_core_foundation_v1` (agent-runner-v2 core).

### Workflow Bundle

A workflow bundle owns and executes a concrete multi-step workflow that
produces delivery outputs.

**Owning layer**: Layer 3.

**Purpose**: Define and execute a specific workflow -- prompts, routing,
validation, and artifact generation -- within a Layer 2 platform context.

**Produces**: Generated outputs (`doc_type: "workflow_output"`),
bundle-local definitions (`doc_type: "bundle_definition"`), review,
validation, and audit evidence.

**Constraints**:
- Must operate within a declared Layer 2 platform context.
- Must not claim Layer 1 or Layer 2 constitutional authority.
- Its outputs are authoritative only for the bundle that owns them.
- Evidence artifacts must be kept separate from permanent outputs.

**Examples**: `21_bug_fix_intake_v1`, `image_csv_gen_v3`, architecture
site generation workflows.

### Lifecycle Admin Bundle

A lifecycle admin bundle owns repository-level administrative operations
that do not produce permanent governed content.

**Owning layer**: Layer 1 or Layer 2 (depends on scope).

**Purpose**: Manage operational concerns such as bootstrap lifecycle,
cleanup, repository initialization, and administrative maintenance.

**Produces**: Operational artifacts and administrative records only. Does
not produce permanent constitutional documents.

**Constraints**:
- Must not generate governance standards.
- Its outputs are operational, not constitutional.
- Must not claim governance authority.

**Example**: `00_bootstrap_lifecycle_admin_v1`.

## Ownership Rules

### Bundle Ownership by Layer

| Bundle Class | Owning Layer | Authority |
|---|---|---|
| Governance Bundle | Layer 1 | Ecosystem governance authority |
| Platform Core Bundle | Layer 2 | Platform-specific authority |
| Workflow Bundle | Layer 3 | Bundle-local authority |
| Lifecycle Admin Bundle | Layer 1 or Layer 2 | Operational authority |

### What Layer 1 Does Not Own

Layer 1 defines the conceptual bundle taxonomy. It does not own:

- workflow-specific artifact path contracts
- bundle-local prompt structure and routing rules
- concrete artifact inventory for a specific bundle
- bundle-specific validation criteria
- platform-specific bundle authoring conventions

These belong to Layer 2 (for platform-wide conventions) or Layer 3 (for
bundle-specific contracts).

### Authority Boundaries

- A governance bundle's outputs are authoritative for the ecosystem
  constitution.
- A platform core bundle's outputs are authoritative for that platform's
  operating model.
- A workflow bundle's outputs are authoritative only for that bundle's
  own generated content.
- A lifecycle admin bundle's outputs are operational and carry no
  constitutional authority.

### Bundle Governance

Every bundle that participates in the governed ecosystem should declare
its own bundle-governance contract, including:

- owning layer
- bundle class
- permitted artifact classes
- permanent versus temporary artifact rules
- anti-drift policy

Bundle governance contracts are bundle-local definitions (`doc_type:
"bundle_definition"`) and do not belong in Layer 1. Layer 1 defines only
the conceptual taxonomy; Layer 2 and Layer 3 define concrete bundle
contracts within that taxonomy.

### Cross-Bundle Dependencies

- Layer 3 workflow bundles depend on a declared Layer 2 platform core.
- Layer 2 platform core bundles depend on Layer 1 governance.
- Layer 1 governance bundles depend on human-authored master plan inputs
  but not on any lower-layer bundle.
- Lifecycle admin bundles may span operational concerns across layers but
  must not generate content that belongs in permanent governance or
  platform constitution bundles.

### Extending the Taxonomy

Layer 2 may define additional bundle sub-classes for platform-specific
needs (for example, a "starter template bundle" or a "validation-only
bundle"). These extensions must:

- respect Layer 1 bundle class definitions
- not redefine the meaning of Layer 1 classes
- clearly identify the owning platform

Layer 3 bundles must fit within the class definitions of their parent
Layer 2 platform.
