---
template_id: SYS-02-IDX
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 platform constitution index; must be included in operational scans"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260720-86359b88"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
> This file is workflow-generated and protected from manual edits.

# agent-runner-v2 Platform Constitution

## Purpose

This document indexes the Layer 2 platform constitution for
**agent-runner-v2**. It defines what agent-runner-v2 is, how it fits
within the three-layer ecosystem, and provides a navigable map of the
permanent platform documents.

agent-runner-v2 is a standalone, multi-step AI workflow runner. It
orchestrates LLM-powered workflows defined in TOML manifests, supporting
prompt-driven generation, action-based automation, human-in-the-loop
approval, and daemon-based backend polling.

## Platform Identity

- **Platform name:** agent-runner-v2
- **Owning layer:** Layer 2
- **Platform class:** Workflow execution engine
- **Primary role:** Translate Layer 1 governance into a concrete
  operating model for AI-driven workflow orchestration

agent-runner-v2 is one possible Layer 2 core within the ecosystem. It
inherits Layer 1 governance without redefining it and provides the
runtime foundation that Layer 3 workflow bundles depend on.

## Layer 1 Inheritance

This platform constitution inherits the Layer 1 governance set as its
authoritative baseline. Layer 1 governance is not redefined, restated,
or replaced by any document in this set.

The Layer 1 governance set defines:

- ecosystem layer definitions and boundaries
- document authority model and metadata classification rules
- bundle taxonomy at a conceptual level
- governance lifecycle principles
- cross-ecosystem metadata standard

This Layer 2 constitution extends Layer 1 by defining:

- the runtime execution model specific to agent-runner-v2
- the bundle authoring contract for Layer 3 workflows on this platform
- shared services available to Layer 3 bundles
- platform-specific metadata extensions
- platform-specific validation patterns

Dependency direction is downward only: this platform depends on Layer 1.
Layer 3 bundles on this platform depend on Layer 2. No lower layer may
redefine a higher layer.

## Document Map

This platform constitution set contains six permanent documents:

| Document | File | Template ID | Description |
|---|---|---|---|
| Platform Index | `README.md` | `SYS-02-IDX` | This document. Indexes the platform constitution set, states platform identity and Layer 1 inheritance. |
| Runtime Model | `RUNTIME_MODEL.md` | `SYS-02-RM` | Defines the execution architecture: step model, execution paths, job lifecycle, coder integration, rejection and retry. |
| Bundle Authoring Contract | `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Defines the contract every Layer 3 bundle must satisfy to run on this platform. |
| Shared Services | `SHARED_SERVICES.md` | `SYS-02-SS` | Defines runtime services available to Layer 3 bundles: context extensions, artifact resolution, path contracts, action registration. |
| Metadata Contract | `METADATA_CONTRACT.md` | `SYS-02-MC` | Defines platform-specific metadata extensions beyond the Layer 1 baseline. |
| Validation Contract | `VALIDATION_CONTRACT.md` | `SYS-02-VC` | Defines the platform validation model: validation plans, section checks, frontmatter enforcement, bundle validator composition. |

The set is six documents. The index (`README.md`) is a first-class
member of the set, not an implicit companion.

## Audience

Primary audiences:

- platform-core maintainers for agent-runner-v2
- Layer 3 workflow bundle authors targeting this platform

Secondary audiences:

- ecosystem architecture owners
- reviewers and auditors of platform or bundle outputs

## Relationship to Other Layers

- **Layer 1** provides the ecosystem constitution (governance, metadata,
  lifecycle, authority). This platform inherits those rules.
- **Layer 3** bundles execute on this platform. They must satisfy the
  bundle authoring contract and use the shared services defined here.

## Output Location

Published platform constitution documents reside at:

```
docs/system/00_governance/platform/current/
```

Staged run outputs reside at:

```
docs/system/00_governance/platform/runs/<job_id>/
```

Historical published snapshots reside at:

```
docs/system/00_governance/platform/history/<job_id>/
```
