---
template_id: "SYS-00-BT"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 bundle taxonomy definition"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-0864b1f2"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Overview

This document defines the conceptual bundle taxonomy for the ecosystem.
It describes what classes of bundles exist, what each class is responsible
for, and who owns the content within each class.

This taxonomy is a governance-level classification. It does not describe
how bundles are bootstrapped, installed, published, or deployed. Those
operational details belong to Layer 2 platform cores.

Workflow-specific artifact contracts, prompts, validators, context
extensions, and output path mappings are not owned by Layer 1. They are
owned by the Layer 3 bundle that defines them, under the rules established
by its parent Layer 2 core.

## Bundle Classes

The ecosystem recognizes the following bundle classes.

### Governance Bundle

A governance bundle produces and maintains cross-ecosystem governance
artifacts.

- **Owning layer:** Layer 1
- **Purpose:** Define the constitutional rules that apply across all
  Layer 2 cores and Layer 3 bundles
- **Output scope:** Governance standards only (layer model, authority
  rules, metadata rules, lifecycle rules, bundle taxonomy)
- **Output exclusions:** Runtime architecture, install procedures,
  publish mechanics, registry operations, platform-specific contracts

### Platform Core Bundle

A platform core bundle defines the operating model for one specific
platform, runtime family, or solution domain.

- **Owning layer:** Layer 2
- **Purpose:** Translate Layer 1 governance into a concrete operating
  model that Layer 3 bundles can target
- **Output scope:** Platform runtime architecture, operating conventions,
  shared service contracts, bundle authoring standards, platform-specific
  validation models
- **Output exclusions:** Redefinition of Layer 1 governance, concrete
  Layer 3 bundle definitions

### Delivery Bundle

A delivery bundle is a concrete workflow that produces documents, reports,
scaffolds, assets, or other delivery outputs.

- **Owning layer:** Layer 3
- **Purpose:** Execute a specific workflow to generate governed outputs
  under the rules of a Layer 2 core
- **Output scope:** Workflow definitions, prompts, context extensions,
  validators, artifact mappings, generated outputs, and operational
  evidence
- **Output exclusions:** Ecosystem-wide constitutional claims,
  platform-wide standards that belong in Layer 2

### Lifecycle Admin Bundle

A lifecycle admin bundle performs administrative lifecycle operations
across the ecosystem.

- **Owning layer:** Layer 1 (governed by Layer 1 standards)
- **Purpose:** Manage the lifecycle of governance and platform artifacts
  (bootstrap, publish, supersede, archive)
- **Output scope:** Lifecycle administration artifacts, publish manifests,
  archival records
- **Output exclusions:** Governance content creation, platform-specific
  implementation detail

## Ownership Rules

### General Rule

Each bundle owns the artifacts it generates. No bundle may claim ownership
of artifacts produced by another bundle, nor may a bundle generate content
that redefines the governance rules of a higher layer.

### Layer 1 Ownership

Layer 1 governance bundles own ecosystem-wide governance standards. These
standards apply across all Layer 2 cores and Layer 3 bundles that adopt
this architecture.

### Layer 2 Ownership

Layer 2 platform core bundles own the platform-specific operating model.
Each Layer 2 core is independently governed and may define its own
conventions within the boundaries established by Layer 1.

### Layer 3 Ownership

Layer 3 delivery bundles own their workflow definitions, prompts, and
generated outputs. A Layer 3 output may be authoritative for the bundle
that produced it, but it does not automatically become authoritative for
other bundles, for its parent Layer 2 core, or for Layer 1 governance.

### Cross-Bundle Boundaries

A bundle must not:

- generate artifacts that belong to a different bundle class without
  explicit authority
- redefine the scope or ownership rules of another bundle
- emit outputs that claim to replace higher-layer governance standards
- include operational mechanics from a different layer as if they were
  within its own scope

### Workflow-Specific Contracts

Workflow-specific artifact contracts (including prompt templates, context
extensions, validator logic, and output path mappings) are owned by the
Layer 3 delivery bundle that defines them. Layer 1 defines the conceptual
taxonomy and ownership rules, but it does not own or define the concrete
contracts of individual bundles.
