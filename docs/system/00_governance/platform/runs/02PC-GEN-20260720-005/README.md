---
template_id: SYS-02-IDX
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 platform core index; must be included in operational scans"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-005"
managed_by: workflow-generated
---

# agent-runner-v2 Platform Constitution

## Purpose

This document indexes the agent-runner-v2 platform constitution -- the
set of Layer 2 documents that define how this platform operationalizes
Layer 1 governance.

agent-runner-v2 is a standalone, multi-step AI workflow runner. It
orchestrates LLM-powered workflows defined in TOML manifests, supporting
prompt-driven generation, action-based automation, human-in-the-loop
approval, and daemon-based backend polling.

This constitution is the authoritative Layer 2 reference for the
platform. It is not a runtime operations manual, not a bundle inventory,
and not a Layer 1 governance document.

## Platform Identity

- **Platform name**: agent-runner-v2
- **Owning layer**: Layer 2
- **Platform class**: AI workflow runner and orchestration engine
- **Primary authority**: platform-owned and workflow-generated
- **Layer 1 relationship**: inherits Layer 1 governance without redefining it

agent-runner-v2 translates Layer 1 ecosystem governance into a concrete
operating model for AI-driven workflow execution. It provides the runtime
architecture, bundle authoring contract, shared services, metadata
extensions, and validation model that Layer 3 workflow bundles depend on.

## Layer 1 Inheritance

This platform constitution inherits from the Layer 1 Governance
Foundation without redefining it. Specifically:

- Layer definitions, ownership boundaries, and authority rules are
  inherited from Layer 1 (`docs/system/00_governance/foundation/current/`).
- The metadata baseline (required fields, core vocabularies, scan policy
  rules) is inherited from the Layer 1 Metadata Standard.
- The governance lifecycle model is inherited from the Layer 1 Governance
  Lifecycle standard.
- The bundle taxonomy at the conceptual level is inherited from the
  Layer 1 Bundle Taxonomy.

This platform extends Layer 1 where needed:

- Platform-specific `doc_type` values for platform standards.
- Platform-specific `authority` values for platform-owned and
  bundle-owned content.
- Additional frontmatter fields required by this platform's runtime.
- Platform-specific validation and authoring contracts.

No content in this constitution redefines, contradicts, or replaces
Layer 1 governance. Where Layer 1 and Layer 2 appear to conflict, Layer 1
governs.

## Document Map

This platform constitution set contains six permanent documents:

| Document | File | Template ID | Description |
|---|---|---|---|
| Platform Index | `README.md` | `SYS-02-IDX` | This document. Indexes the platform constitution, states platform identity and Layer 1 inheritance. |
| Runtime Model | `RUNTIME_MODEL.md` | `SYS-02-RM` | Defines the execution architecture: step model, execution paths, job lifecycle, coder integration, rejection and retry. |
| Bundle Authoring Contract | `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Defines the contract every Layer 3 bundle must satisfy to run on this platform. |
| Shared Services | `SHARED_SERVICES.md` | `SYS-02-SS` | Defines runtime services available to Layer 3 bundles: context extensions, artifact resolution, path contracts, action registration. |
| Metadata Contract | `METADATA_CONTRACT.md` | `SYS-02-MC` | Defines platform-specific metadata extensions beyond the Layer 1 baseline. |
| Validation Contract | `VALIDATION_CONTRACT.md` | `SYS-02-VC` | Defines the platform validation model shared across Layer 3 bundles. |

## Audience

Primary audiences:

- platform maintainers and runtime contributors
- Layer 3 bundle authors targeting this platform
- workflow framework designers

Secondary audiences:

- ecosystem owners reviewing platform compliance with Layer 1
- reviewers and auditors

## Relationship to Other Layers

- **Layer 1** (ecosystem constitution): inherited, not redefined. Layer 1
  governance documents are the authoritative source for cross-ecosystem
  rules.
- **Layer 3** (concrete workflow bundles): Layer 3 bundles depend on this
  platform constitution for runtime services, authoring contracts, and
  validation rules. Each Layer 3 bundle must satisfy the Bundle Authoring
  Contract defined in this set.

Dependency direction is downward only: Layer 3 depends on Layer 2,
Layer 2 depends on Layer 1.
