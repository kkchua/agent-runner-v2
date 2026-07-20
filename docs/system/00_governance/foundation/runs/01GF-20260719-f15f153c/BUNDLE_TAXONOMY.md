---
template_id: SYS-00-BT
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 governance foundation document; required for operational scans"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-f15f153c"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `refine_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Bundle Classes

The ecosystem recognizes three classes of bundles, each corresponding to a
layer in the three-layer architecture.

### Governance Bundle (Layer 1)

A governance bundle defines the ecosystem constitution. It produces and
maintains governance artifacts: layer definitions, ownership rules,
authority standards, metadata conventions, lifecycle rules, and bundle
taxonomy.

**Scope:** cross-ecosystem governance only

**Example:** the `01_governance_foundation_v1` bundle that generates this
document set

**Constraints:**
- must not define runtime architecture
- must not define platform-specific operating models
- must not define concrete workflow definitions for Layer 3
- outputs are governance standards, not operational artifacts

### Platform Core Bundle (Layer 2)

A platform core bundle defines the operating model for one specific
platform, runtime family, or solution domain. It translates Layer 1
governance into concrete platform conventions that Layer 3 bundles depend
on.

**Scope:** one platform or domain

**Example bundles (conceptual):**
- AI-driven SDLC core
- ComfyUI platform core
- n8n platform core
- agent-runner-v2 platform core

**Constraints:**
- must not redefine Layer 1 governance
- must not collapse into a concrete bundle inventory
- must identify the owning platform or domain explicitly
- outputs are platform standards, not workflow outputs

### Workflow Bundle (Layer 3)

A workflow bundle defines a concrete, executable workflow within a Layer 2
platform context. It contains prompts, actions, validators, context
extensions, artifact mappings, and bundle-local governance.

**Scope:** one workflow or delivery concern

**Example bundles (conceptual):**
- repository bootstrap workflow
- codebase documentation workflow
- bug fix intake workflow
- initiative intake workflow

**Constraints:**
- must not claim ecosystem-wide constitutional authority
- must not define platform-wide standards that belong in Layer 2
- must identify its parent Layer 2 platform
- outputs are workflow-specific artifacts

---

## Ownership Rules

### Layer 1 Ownership

**Governance bundles are owned by the ecosystem governance authority.**

Governance bundle outputs are authoritative for cross-ecosystem governance
rules. No lower-layer bundle may redefine or override Layer 1 governance.

### Layer 2 Ownership

**Platform core bundles are owned by their respective platform authority.**

Each Layer 2 bundle governs its own platform-specific operating model.
Multiple Layer 2 bundles may coexist, each serving a different platform or
domain.

Layer 2 bundles inherit Layer 1 governance and must not contradict it.

### Layer 3 Ownership

**Workflow bundles are owned by their respective bundle authors.**

Each Layer 3 bundle owns its concrete workflow definitions, prompts,
artifact mappings, and generated outputs. Bundle-local governance is valid
only within that bundle's scope.

Workflow-specific artifact contracts (such as concrete file paths, prompt
templates, and validator definitions) are not owned by Layer 1 and are not
defined by the governance foundation. Each Layer 3 bundle declares those
contracts within its own bundle governance package.

### Ownership Inheritance

Ownership flows downward:

- Layer 1 defines cross-ecosystem governance
- Layer 2 inherits Layer 1 and adds platform conventions
- Layer 3 inherits Layer 2 and adds bundle-specific definitions

No layer may claim ownership of content that belongs to a higher or
sibling layer.

### Reclassification Rule

A bundle may be reclassified to a different class only through explicit
review and promotion. A Layer 3 workflow bundle does not become a Layer 2
platform core by accumulating outputs. A Layer 2 platform core does not
become Layer 1 governance by being widely adopted.

---

## Relationship to Artifact Contracts

This bundle taxonomy defines conceptual classes and ownership rules at the
governance level.

Concrete artifact contracts -- such as which specific file paths a workflow
bundle produces, which metadata keys it requires, or which validator
functions it uses -- are defined by the owning bundle itself, not by
Layer 1.

Layer 1 governance provides the classification framework. Layer 2 provides
platform-specific contract patterns. Layer 3 provides concrete contracts
for each bundle.

This separation ensures that adding a new workflow bundle does not require
changing the ecosystem constitution.
