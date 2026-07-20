---
template_id: SYS-00-BT
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
managed_by: workflow-generated
scan_policy: "include"
scan_reason: "Layer 1 governance standard; included in operational scans"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-96e730ab"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `generate_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Overview

This document defines the conceptual bundle taxonomy for the ecosystem.
It classifies bundles by their role and ownership within the three-layer
architecture.

Layer 1 defines bundle classes at the governance level only.
Workflow-specific artifact contracts, concrete output inventories, and
bundle-local path mappings are owned by individual Layer 3 bundles, not
by this document.

## Bundle Classes

The ecosystem recognizes the following conceptual bundle classes:

### Governance Bundle

**Layer:** Layer 1
**Purpose:** Produces and maintains ecosystem-wide governance standards.
**Ownership:** Ecosystem governance authority.
**Authority:** `workflow-generated` or `human-authored`.

Governance bundles generate permanent governance documents (layer models,
authority standards, metadata standards, lifecycle standards) and
temporary evidence artifacts (review, validation, audit outputs).

A governance bundle must not:

- Define runtime architecture or platform-specific operating procedures.
- Produce Layer 2 platform constitutions.
- Produce Layer 3 workflow outputs.
- Mutate implementation code.

### Platform Core Bundle

**Layer:** Layer 2
**Purpose:** Defines the operating model for a specific platform or domain.
**Ownership:** Platform maintainers.
**Authority:** `platform-owned` or `workflow-generated`.

Platform core bundles translate Layer 1 governance into concrete platform
conventions: runtime architecture, shared services, bundle authoring
contracts, platform-specific validation rules, and platform-specific
metadata standards.

A platform core bundle must not:

- Redefine Layer 1 governance rules.
- Collapse into a concrete bundle inventory.
- Claim cross-ecosystem authority.

### Workflow Bundle

**Layer:** Layer 3
**Purpose:** Defines and executes a concrete workflow that produces
governed outputs.
**Ownership:** Bundle authors.
**Authority:** `bundle-owned` or `workflow-generated`.

Workflow bundles contain prompts, actions, validators, context extensions,
artifact mappings, and bundle-local governance contracts. They are the
concrete delivery units of the ecosystem.

A workflow bundle must not:

- Define ecosystem-wide constitutional rules.
- Define platform-wide standards that belong in Layer 2.
- Claim Layer 1 or Layer 2 authority for its outputs.

### Lifecycle Admin Bundle

**Layer:** Layer 1 (administrative)
**Purpose:** Manages bootstrap, initialization, and lifecycle
administration for the ecosystem.
**Ownership:** Ecosystem governance authority.
**Authority:** `workflow-generated`.

Lifecycle admin bundles handle operational concerns such as bundle
installation, workflow seeding, and runner initialization. They are
administrative infrastructure, not governance content producers.

### Master Docs Bundle

**Layer:** Layer 3 (repo-scoped)
**Purpose:** Generates repository-level master documentation for a
specific project or codebase.
**Ownership:** Bundle authors or repository owners.
**Authority:** `workflow-generated` or `bundle-owned`.

Master docs bundles produce repository-scoped outputs such as codebase
inventories, delivery agent contracts, and architecture site documents.

## Ownership Rules

### Ownership by Bundle Class

| Bundle Class | Layer | Owning Authority | Permanent Outputs |
|-------------|-------|-----------------|-------------------|
| Governance Bundle | Layer 1 | Ecosystem governance authority | Governance standards |
| Platform Core Bundle | Layer 2 | Platform maintainers | Platform operating standards |
| Workflow Bundle | Layer 3 | Bundle authors | Workflow outputs, evidence |
| Lifecycle Admin Bundle | Layer 1 (admin) | Ecosystem governance authority | Administrative artifacts |
| Master Docs Bundle | Layer 3 (repo) | Bundle authors or repo owners | Repo-scoped documentation |

### Ownership Inheritance

- A Layer 3 bundle inherits governance rules from Layer 1 and platform
  conventions from its parent Layer 2 core.
- A bundle may not override governance rules defined by a higher layer.
- A bundle may extend or specialize platform conventions, but must not
  contradict them.

### Bundle Scope Boundaries

Each bundle class operates within a defined scope boundary:

- **Governance bundles** operate at the ecosystem level. Their outputs
  apply across all Layer 2 cores and Layer 3 bundles.
- **Platform core bundles** operate at the platform level. Their outputs
  apply to all Layer 3 bundles targeting that platform.
- **Workflow bundles** operate at the bundle level. Their outputs are
  authoritative only within the owning bundle's scope.
- **Lifecycle admin bundles** operate at the ecosystem administration
  level. Their outputs support ecosystem operations but are not governance
  standards.
- **Master docs bundles** operate at the repository level. Their outputs
  are scoped to a single repository.

### Cross-Bundle References

- A Layer 3 bundle may reference its parent Layer 2 core and Layer 1
  governance standards.
- A Layer 2 core may reference Layer 1 governance standards.
- A bundle must not create hidden dependencies on undocumented behavior
  of another bundle.
- Cross-bundle references must be explicit and traceable.

### What Layer 1 Does Not Own

Layer 1 defines the conceptual bundle taxonomy and ownership rules.
The following are owned by individual bundles and are not part of the
Layer 1 governance set:

- Workflow-specific artifact path contracts.
- Concrete output file inventories.
- Bundle-local prompt templates and context extensions.
- Bundle-local validator implementations.
- Bundle-specific review criteria and routing policies.
- Bundle-specific metadata extensions beyond the Layer 1 baseline.

These concerns belong to the bundle's own definition documents and are
governed by the bundle's parent Layer 2 core conventions.
