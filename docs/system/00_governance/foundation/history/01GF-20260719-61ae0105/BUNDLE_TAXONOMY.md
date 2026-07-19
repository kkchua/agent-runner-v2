---
template_id: "SYS-00-BT"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "authoritative conceptual bundle taxonomy for the ecosystem"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-61ae0105"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the conceptual bundle taxonomy for the ecosystem.
It classifies bundles by their role, owning layer, and governance
obligations. This taxonomy is purely conceptual and does not define
workflow-specific artifact contracts, bootstrap mechanics, or delivery
procedures.

## Scope

This taxonomy defines bundle classes at the governance level only:

- what kinds of bundles exist
- which layer owns each bundle class
- what governance obligations each class carries
- how bundle classes relate to each other

This taxonomy does not define:

- concrete workflow bundle inventories
- bundle-local artifact path mappings
- workflow prompt content or structure
- bootstrap or delivery mechanics (copying templates, seeding workflows,
  repository initialization)
- platform-specific runtime contracts

Those concerns belong to Layer 2 (platform operating models) or Layer 3
(concrete bundle definitions).

## Bundle Classes

### Governance Bundle

- **Owning layer**: Layer 1
- **Role**: Produces and maintains cross-ecosystem governance standards.
- **Example**: `01_governance_foundation_v1`
- **Governance obligations**:
  - Must generate only Layer 1 governance artifacts.
  - Must not define runtime, platform, or delivery mechanics.
  - Must separate permanent standards from temporary evidence.
  - Must attach explicit metadata to all outputs.

### Platform Core Bundle

- **Owning layer**: Layer 2
- **Role**: Defines the operating model for a specific platform or domain.
- **Examples**: AI-driven SDLC core bundle, ComfyUI core bundle, n8n core
  bundle, agent-runner-v2 core bundle
- **Governance obligations**:
  - Must translate Layer 1 governance into platform-specific rules.
  - Must not redefine Layer 1 baseline values.
  - Must identify the owning platform in all outputs.
  - Must provide a stable contract for Layer 3 bundles.

### Workflow Bundle

- **Owning layer**: Layer 3
- **Role**: Produces concrete outputs (documents, reports, scaffolds,
  assets) through defined workflow steps.
- **Governance obligations**:
  - Must declare which Layer 2 core it targets.
  - Must declare its artifact contract explicitly.
  - Must not claim Layer 1 or Layer 2 constitutional authority.
  - Must separate permanent outputs from temporary evidence.

### Lifecycle Admin Bundle

- **Owning layer**: Layer 2 or Layer 3
- **Role**: Manages lifecycle operations such as initialization, cleanup,
  and maintenance.
- **Governance obligations**:
  - Must operate within the bounds of its owning layer.
  - Must not generate governance standards.
  - Must not mutate platform contracts without explicit authority.

### Bootstrap Bundle

- **Owning layer**: Layer 2
- **Role**: Seeds initial platform structure and reference documents into
  a target repository or environment.
- **Governance obligations**:
  - Must be idempotent where practical.
  - Must not overwrite human-authored content without explicit guardrails.
  - Must declare what it seeds and why.

### Registry Bundle

- **Owning layer**: Layer 2
- **Role**: Maintains the inventory and discovery mechanism for the
  ecosystem.
- **Governance obligations**:
  - Must track bundle identity, version, and owning layer.
  - Must not silently absorb governance authority.
  - Must remain a service, not a source of governance truth.

## Ownership Rules

### Ownership Summary

| Bundle Class | Owning Layer | Authority | Generates Governance? | Generates Outputs? |
|---|---|---|---|---|
| Governance Bundle | Layer 1 | `workflow-generated` or `human-authored` | Yes (Layer 1 only) | No |
| Platform Core Bundle | Layer 2 | `platform-owned` or `workflow-generated` | Yes (Layer 2 only) | No |
| Workflow Bundle | Layer 3 | `bundle-owned` or `workflow-generated` | No | Yes |
| Lifecycle Admin Bundle | Layer 2 or 3 | `platform-owned` or `bundle-owned` | No | Yes (operational) |
| Bootstrap Bundle | Layer 2 | `platform-owned` | No | Yes (seed content) |
| Registry Bundle | Layer 2 | `platform-owned` | No | Yes (inventory) |

### Bundle Class Relationships

#### Dependency Direction

```
Governance Bundle (L1)
    |
    v
Platform Core Bundle (L2)
    |
    v
Workflow Bundle (L3)
```

- A Governance Bundle defines the rules.
- A Platform Core Bundle translates those rules for a platform.
- A Workflow Bundle applies platform rules to produce concrete outputs.

#### Cross-Layer Rules

- A Layer 3 Workflow Bundle must declare which Layer 2 Platform Core it
  targets.
- A Layer 2 Platform Core Bundle must declare which Layer 1 Governance
  Bundle it inherits from.
- No bundle may silently depend on undocumented behavior from another
  layer.

## What This Taxonomy Does Not Own

This taxonomy is a Layer 1 conceptual classification. It does not own:

- workflow-specific artifact contracts (those belong to individual Layer 3
  bundles)
- platform-specific runtime contracts (those belong to Layer 2)
- concrete bundle inventories (those belong to Layer 2 registries)
- bootstrap seeding procedures (those belong to Layer 2 bootstrap bundles)
- delivery mechanics such as copying templates, initializing repository
  structure, or one-time setup (those belong to Layer 2 or Layer 3)

If a statement describes how a specific bundle operates, what files it
produces, or how it is installed, that statement does not belong in this
taxonomy.

## Extending the Taxonomy

Layer 2 may:

- specialize bundle classes for platform-specific needs (e.g., "ComfyUI
  Node Bundle")
- add platform-specific governance obligations
- define platform-specific artifact contracts for bundle classes

Layer 2 must not:

- redefine the meaning of Layer 1 bundle classes
- reclassify a Layer 1 Governance Bundle as a Layer 2 artifact
- claim that a platform-specific bundle class is ecosystem-wide governance

## Governance Bundle Identity

A Governance Bundle at Layer 1 is distinguished by:

1. It generates only governance standards (no runtime, platform, or
   delivery outputs).
2. Its outputs are designed to remain valid across multiple Layer 2 cores.
3. It separates permanent standards from temporary evidence.
4. It attaches explicit metadata classification to all outputs.
5. Its scope is explicitly bounded by the layer model defined in
   `LAYER_MODEL.md`.
