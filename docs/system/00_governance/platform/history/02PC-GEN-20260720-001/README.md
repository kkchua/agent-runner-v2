---
template_id: SYS-02-IDX
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 platform core index; must be included in operational scans"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260720-001"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.

# agent-runner-v2 Platform Constitution

## Platform Identity

**agent-runner-v2** is a standalone, multi-step AI workflow runner. It
orchestrates LLM-powered ("coder") workflows defined in TOML manifests,
supporting prompt-driven generation, action-based automation,
human-in-the-loop approval, and daemon-based backend polling.

As a Layer 2 platform core, agent-runner-v2 translates Layer 1 ecosystem
governance into a platform-specific operating model. It defines the
runtime architecture, bundle authoring contract, shared services,
metadata contract, and validation contract that all Layer 3 workflow
bundles on this platform must follow.

**Key capabilities:**

- Multi-step workflow execution with prompt-driven and action-driven steps
- Plugin-based workflow package system with TOML manifest configuration
- Coder (LLM) integration with role-based policy resolution
- Human-in-the-loop approval gating for governed workflows
- Daemon mode for backend-polling autonomous execution
- Notification integration (Pushover + console)
- Backend sync protocol for distributed worker coordination

## Document Map

This platform constitution set contains six permanent documents:

| Document | File | Template ID | Description |
|---|---|---|---|
| Platform Index | `README.md` | `SYS-02-IDX` | This document. Indexes the platform constitution set, defines platform identity, and declares Layer 1 inheritance. |
| Runtime Model | `RUNTIME_MODEL.md` | `SYS-02-RM` | Defines the execution architecture: step model, execution paths, job lifecycle, coder integration, rejection/retry model, and notification model. |
| Bundle Authoring Contract | `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Defines the contract every Layer 3 bundle must satisfy: required files, TOML format, artifact key conventions, bundle governance requirements, and metadata compliance. |
| Shared Services | `SHARED_SERVICES.md` | `SYS-02-SS` | Defines runtime services available to Layer 3 bundles: context extensions, artifact resolution, path contracts, meta sidecar handling, notification integration, backend sync protocol, and action registration. |
| Metadata Contract | `METADATA_CONTRACT.md` | `SYS-02-MC` | Defines platform-specific metadata extensions: doc_type values, authority values, additional frontmatter fields, inheritance rules, and scan-policy expectations. |
| Validation Contract | `VALIDATION_CONTRACT.md` | `SYS-02-VC` | Defines the platform validation model: ValidationPlan pattern, section checks, frontmatter enforcement, file existence checks, and bundle validator composition. |

## Layer 1 Inheritance

This platform constitution inherits from Layer 1 ecosystem governance
without modifying it.

**Inherited standards (read-only reference):**

| Layer 1 Document | Template ID | How Layer 2 Applies It |
|---|---|---|
| Layer Model | `SYS-00-LM` | Layer 2 operates within the defined three-layer architecture. This platform core is a Layer 2 platform constitution. |
| Document Authority | `SYS-00-DA` | Layer 2 extends the authority vocabulary with platform-specific values (`platform-owned`, `bundle-owned`) without changing Layer 1 baseline meanings. |
| Bundle Taxonomy | `SYS-00-BT` | Layer 2 defines the platform core bundle class concretely for agent-runner-v2. Layer 3 bundles on this platform must be workflow bundles. |
| Governance Lifecycle | `SYS-00-GL` | Layer 2 applies the lifecycle model: staged run outputs carry `lifecycle_status: "draft"`; published platform standards carry `lifecycle_status: "published"`. |
| Metadata Standard | `SYS-00-MS` | Layer 2 extends the `doc_type` vocabulary with `platform_standard` and `bundle_definition`. Layer 2 adds platform-specific frontmatter fields (`platform`, `template_id`, `managed_by`). |

**Layer 1 is inherited, not modified.** This platform constitution:

- Does not change the meaning of any Layer 1 `doc_type` or `authority` value
- Does not alter the three-layer architecture definition
- Does not modify platform-level ownership or promotion rules
- Does not assert constitutional authority beyond this platform

Layer 1 governance documents under `docs/system/00_governance/foundation/current/`
are the authoritative source for platform-level governance. This platform
constitution applies Layer 1 rules to the agent-runner-v2 platform
specifically.

## Relationship to Other Layers

### Layer 1 (above)

Layer 1 is the ecosystem constitution. It defines platform-wide
governance rules that apply to all Layer 2 platform cores. This platform
core depends on Layer 1 and inherits its rules.

### Layer 3 (below)

Layer 3 workflow bundles on agent-runner-v2 depend on this platform
constitution for:

- Runtime model (how steps execute, how routing works)
- Bundle authoring contract (required files, TOML format)
- Shared services (context extensions, artifact resolution, path contracts)
- Metadata contract (platform-specific fields and values)
- Validation contract (how to write validators)

Layer 3 bundles must not modify Layer 1 governance or this platform
constitution. Their outputs are authoritative only for the bundle that
owns them.

## Audience

**Primary audiences:**

- Platform maintainers and runtime contributors
- Workflow bundle authors targeting agent-runner-v2
- Workflow framework designers

**Secondary audiences:**

- Reviewers and auditors of Layer 3 workflow bundles
- Ecosystem governance owners verifying Layer 2 compliance with Layer 1

## Document Status

This is a staged run output. All documents carry `lifecycle_status: "draft"`.
They become active only after review, validation, audit, human approval,
and publication through the `02_platform_core_foundation_v1` workflow.
