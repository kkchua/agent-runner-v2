---
template_id: "SYS-00-BT"
version: "0.1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "defines the conceptual bundle taxonomy referenced by all layers"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-4e51c88b"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This standard defines the conceptual bundle taxonomy for the ecosystem.
A bundle is a self-contained package that defines and governs a specific
unit of work: a workflow, a platform core, or a governance foundation.

This taxonomy is conceptual: it describes what classes of bundles exist,
what they own, and where they reside in the layer model. It does not
define workflow-specific artifact contracts, concrete output path
mappings, or bundle-local prompt structure. Those responsibilities belong
to the owning bundle, not to Layer 1.

## Bundle Classes

Three bundle classes correspond to the three layers of the ecosystem.

### Governance Bundle (Layer 1)

A governance bundle produces and maintains ecosystem-wide governance
standards. It belongs to Layer 1.

**Purpose**: Define the constitutional rules that apply across all
platforms and all workflow bundles.

**Characteristics**:

- Generates only governance artifacts (layer model, authority rules,
  metadata standards, lifecycle rules, bundle taxonomy)
- Does not define runtime mechanics, install flows, or platform-specific
  operating procedures
- Its outputs are permanent system documents (`doc_type: "system"`)
- Review, validation, and audit evidence are temporary artifacts
- Multiple Layer 2 cores may depend on one governance bundle

**Examples**:

- `01_governance_foundation_v1`: generates the Layer 1 governance
  foundation set

### Platform Core Bundle (Layer 2)

A platform core bundle produces and maintains the operating constitution
for one specific platform or domain. It belongs to Layer 2.

**Purpose**: Translate Layer 1 governance into a concrete operating model
that Layer 3 bundles can depend on.

**Characteristics**:

- Inherits Layer 1 governance without redefining it
- Defines runtime architecture, shared services, bundle authoring
  contracts, platform metadata extensions, and platform validation
  contracts
- Identifies the platform it governs
- Its outputs are permanent platform standards
  (`doc_type: "platform_standard"`)
- Multiple Layer 3 bundles may depend on one platform core bundle

**Examples**:

- `02_platform_core_foundation_v1`: generates a platform constitution
  for a specific runtime (e.g., agent-runner-v2)

### Workflow Bundle (Layer 3)

A workflow bundle defines and executes a concrete workflow that produces
delivery outputs. It belongs to Layer 3.

**Purpose**: Generate documents, reports, scaffolds, assets, or other
delivery outputs under the governance rules inherited from Layer 1 and
Layer 2.

**Characteristics**:

- Inherits Layer 1 governance and Layer 2 platform standards
- Contains concrete workflow definitions (`workflow.toml`), prompts,
  context extensions, validators, and bundle-local governance
- Owns its artifact path contracts and output inventory
- Generates workflow outputs and temporary review/validation/audit
  evidence
- May be authoritative for its own outputs but must not claim
  higher-layer constitutional authority

**Examples**:

- `21_bug_fix_intake_v1`: a bug-fix intake workflow
- `50_architecture_site_v1`: an architecture site generation workflow
- `image_csv_gen_v3`: an image generation workflow

## Ownership Rules

### Bundle Ownership by Layer

| Bundle Class | Layer | Owns | Does Not Own |
|---|---|---|---|
| Governance Bundle | Layer 1 | Ecosystem governance standards, authority rules, metadata baseline, bundle taxonomy, lifecycle rules | Platform-specific operating standards, runtime architecture, concrete workflow definitions |
| Platform Core Bundle | Layer 2 | Platform runtime model, shared services, bundle authoring contract, platform metadata extensions, platform validation contract | Layer 1 governance redefinition, Layer 3 bundle-local artifact contracts |
| Workflow Bundle | Layer 3 | Workflow definition, prompts, context extensions, validators, output paths, generated outputs, temporary evidence | Layer 1 or Layer 2 constitutional authority, platform-wide standards |

### Cross-Bundle References

- A Layer 2 platform core bundle may reference and specialize the Layer 1
  bundle taxonomy
- A Layer 3 workflow bundle may reference both Layer 1 governance and its
  parent Layer 2 platform core
- A Layer 3 workflow bundle must not reference another Layer 3 bundle as
  if it were a governance authority

### Artifact Contract Ownership

Workflow-specific artifact contracts (paths, output inventories, prompt
templates, and bundle-local validators) are owned by the individual
Layer 3 bundle that defines them. Layer 1 does not own, define, or
enumerate concrete artifact contracts for any workflow bundle.

Layer 2 may define artifact contract patterns or templates that Layer 3
bundles should follow, but the concrete contract is a Layer 3 concern.

### Promotion Between Bundle Classes

A bundle does not change class by convention or reuse:

- A widely-used Layer 3 workflow bundle does not become a Layer 2 platform
  core by adoption
- A Layer 2 platform core does not become Layer 1 governance by being
  copied across multiple platforms
- Promotion requires explicit review, reclassification, and acceptance by
  the owning authority of the target layer

### Bundle Governance

Every bundle, regardless of class, should carry a bundle-governance
package that governs its own authoring and maintenance. The bundle
governance package defines:

- Prompt structure and authoring rules
- Allowed and forbidden action types
- Review and audit behavior
- Bundle-local anti-drift rules

Bundle governance is self-referential: it governs the bundle that
contains it. It does not extend to other bundles or to higher layers.
