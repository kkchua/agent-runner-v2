---
template_id: SYS-02-IDX
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 platform core index; indexes the agent-runner-v2 platform constitution set"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260721-009"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.
> This file is workflow-generated and subject to review, validation, audit, and human approval before publication.

# Agent-Runner v2 Platform Constitution

## Purpose

This document indexes the platform constitution for agent-runner-v2 --
the Layer 2 core that defines how workflows execute, how bundles are
authored, what shared services are available, and how governance
metadata and validation operate on this platform.

agent-runner-v2 is a general-purpose workflow execution engine. It
accepts workflow bundles (Layer 3) conforming to this platform contract
and executes their steps through integrated coder backends (CLI-based
coding agents such as qwen, claude, codex, and opencode), action
functions, and daemon-managed worker processes.

## Platform Identity

agent-runner-v2 is one of several possible Layer 2 cores that
operationalize Layer 1 ecosystem governance for a specific runtime
family. Other Layer 2 cores may include a ComfyUI core, an n8n core,
or an AI-driven SDLC core. Each core translates Layer 1 governance
into its own platform-specific operating model.

agent-runner-v2 defines:

- The step execution model (prompt-driven steps vs. action steps)
- The daemon and manual execution paths
- The bundle authoring contract that every Layer 3 bundle must satisfy
- The shared runtime services available to bundles
- Platform-specific metadata and validation extensions

## Document Map

This platform constitution set contains six permanent documents:

| Document | File | Template ID | Description |
|---|---|---|---|
| Platform Index | `README.md` | `SYS-02-IDX` | This document. Indexes the platform constitution, states platform identity, and declares Layer 1 inheritance. |
| Runtime Model | `RUNTIME_MODEL.md` | `SYS-02-RM` | Defines the execution architecture: step model, execution paths, job lifecycle, coder integration, rejection/retry model, and notification model. |
| Bundle Authoring Contract | `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Defines the contract every Layer 3 bundle must satisfy: required files, TOML format, artifact key conventions, bundle governance requirements, and metadata compliance. |
| Shared Services | `SHARED_SERVICES.md` | `SYS-02-SS` | Defines runtime services available to Layer 3 bundles: context extensions, artifact resolution, path contracts, meta sidecar handling, notification integration, backend sync protocol, and action registration. |
| Metadata Contract | `METADATA_CONTRACT.md` | `SYS-02-MC` | Defines platform-specific metadata extensions beyond the Layer 1 baseline: doc_type values, authority values, additional frontmatter fields, inheritance rules, and scan-policy expectations. |
| Validation Contract | `VALIDATION_CONTRACT.md` | `SYS-02-VC` | Defines the platform validation model: DocumentationValidationPlan pattern, section-check conventions, frontmatter enforcement, file existence checks, and bundle validator composition. |

## Layer 1 Inheritance

This platform constitution inherits from Layer 1 governance without
redefining it. Layer 1 defines the ecosystem constitution -- the
three-layer architecture, document authority, bundle taxonomy,
governance lifecycle, and metadata standard. This platform
operationalizes those rules for agent-runner-v2 specifically.

The dependency direction is downward only:

```
Layer 1 (ecosystem constitution)
    |
    v
Layer 2 (agent-runner-v2 platform constitution)  <-- this document set
    |
    v
Layer 3 (concrete workflow bundles)
```

Layer 1 governance documents are read from the governance runtime root
and are the inherited authority for all platform-level rules in this
constitution. No document in this set may contradict or redefine Layer 1.

## Audience

Primary audiences:

- Platform maintainers and runtime maintainers
- Framework contributors
- Bundle authors targeting agent-runner-v2

Secondary audiences:

- Ecosystem owners verifying platform compliance with Layer 1
- Reviewers and auditors

## Scope

This document set defines the platform constitution only. It does not
include:

- Layer 1 ecosystem governance (belongs to `01_governance_foundation_v1`)
- Concrete Layer 3 bundle inventories
- Job-history evidence
- Runtime installation or setup guides
- Codebase scanning results

It does not serve as a runtime operations manual. Execution details
are documented in the runtime model and shared services documents at a
platform-contract level, not at the level of individual runbook
procedures.
