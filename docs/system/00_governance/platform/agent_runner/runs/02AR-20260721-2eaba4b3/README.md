---
template_id: "SYS-02-IDX"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 platform core index for agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02AR-20260721-2eaba4b3"
---

# agent-runner-v2 Platform Core Index

## Document Map

This document set defines the agent-runner-v2 platform constitution -- the operating model that translates Layer 1 ecosystem governance into a concrete runtime platform.

The platform constitution consists of six permanent documents:

| # | Document | template_id | Purpose |
|---|---|---|---|
| 1 | `README.md` (this file) | `SYS-02-IDX` | Platform identity, document map, Layer 1 inheritance statement. |
| 2 | `RUNTIME_MODEL.md` | `SYS-02-RM` | Execution architecture: step model, daemon/manual paths, job lifecycle, coder integration, rejection/retry, notifications. |
| 3 | `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Contract every Layer 3 bundle must satisfy to run on this platform. |
| 4 | `SHARED_SERVICES.md` | `SYS-02-SS` | Runtime services available to Layer 3 bundles: context extensions, artifact resolution, path contracts, meta sidecar, notifications, backend sync, action registration. |
| 5 | `METADATA_CONTRACT.md` | `SYS-02-MC` | Platform-specific metadata extensions beyond the Layer 1 baseline. |
| 6 | `VALIDATION_CONTRACT.md` | `SYS-02-VC` | Platform validation model shared across Layer 3 bundles. |

The document map includes this index itself so the published set inventory is six documents, not five companions plus an implicit index.

## Platform Identity

agent-runner-v2 is a Layer 2 platform core that provides the runtime execution environment for AI-driven workflow bundles.

The platform provides:

- A **step execution engine** that invokes coding agents (CLI coders such as Claude Code or Qwen Code) to execute prompt-driven workflow steps.
- A **daemon/worker model** that polls a backend for work, spawns child processes per claimed step, monitors liveness, and reports results.
- A **bundle authoring contract** defining the required file structure, TOML format, and metadata rules every Layer 3 workflow bundle must satisfy.
- **Shared runtime services** including context extensions, artifact path resolution, meta sidecar handling, notification integration, and action registration.
- A **validation framework** built on the `DocumentationValidationPlan` pattern that Layer 3 bundles compose for their own output checks.

As a Layer 2 core, agent-runner-v2 is one of several possible platforms (alongside ComfyUI core, n8n core, etc.) that operationalize the same Layer 1 governance for a specific runtime family.

## Layer 1 Inheritance

This platform constitution inherits from Layer 1 governance without redefining it.

The following Layer 1 documents form the inherited governance baseline:

- `LAYER_MODEL.md` -- three-layer architecture boundaries
- `METADATA_STANDARD.md` -- required metadata fields, vocabularies, scanner compliance rules
- `DOCUMENT_AUTHORITY.md` -- ownership, authority, and promotion rules
- `BUNDLE_TAXONOMY.md` -- conceptual bundle classes and ownership model
- `GOVERNANCE_LIFECYCLE.md` -- lifecycle states and change control

This platform constitution extends Layer 1 rules for the agent-runner-v2 platform without contradicting them. Platform-specific values for `doc_type`, `authority`, and additional frontmatter fields are defined in `METADATA_CONTRACT.md`. Bundle-specific operating detail belongs in Layer 3, not here.

The Layer 1 governance documents are installed at the global runtime root (`GOVERNANCE_RUNTIME_ROOT`) and are treated as read-only inherited authority. This platform does not reproduce or duplicate them -- it references them.

Layer 1 defines the ecosystem constitution. Layer 2 defines the agent-runner-v2 platform operating model. Layer 3 bundles implement concrete workflows within this platform context.
