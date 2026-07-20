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
effective_version: "02PC-GEN-20260720-004"
managed_by: workflow-generated
---

# agent-runner-v2 Platform Constitution

## Purpose

This document indexes the platform constitution for agent-runner-v2.
It defines what agent-runner-v2 is, how it relates to the ecosystem
layer model, and which documents comprise the active Layer 2 platform
core set.

agent-runner-v2 is a standalone, multi-step AI workflow runner. It
orchestrates LLM-powered workflows defined in TOML manifests,
supporting prompt-driven generation, action-based automation,
human-in-the-loop approval, and daemon-based backend polling.

This constitution is the Layer 2 platform core for agent-runner-v2.
It translates Layer 1 ecosystem governance into the platform-specific
operating model that Layer 3 workflow bundles depend on.

## Platform Identity

- **Platform name:** agent-runner-v2
- **Platform class:** AI workflow runner / multi-step orchestration engine
- **Owning layer:** Layer 2
- **Primary audience:** platform maintainers, runtime contributors,
  workflow bundle authors, reviewers and auditors

agent-runner-v2 provides:

- a step execution model (prompt-driven and action-driven steps)
- a workflow package system (TOML manifests, bundle governance, plugin
  registry)
- multiple execution paths (CLI, daemon, manual)
- coder integration via configurable role policies and connections
- artifact tracking, validation, and routing
- notification and backend synchronization

## Layer 1 Inheritance

This platform constitution inherits Layer 1 governance without
redefining it. The Layer 1 governance foundation set
(`docs/system/00_governance/foundation/current/`) defines the
cross-ecosystem rules for:

- layer definitions and boundaries
- document authority and ownership
- metadata classification and scan policy
- bundle taxonomy at a conceptual level
- governance lifecycle and promotion rules

agent-runner-v2 extends Layer 1 by defining how these governance rules
operate within this specific platform. It does not redefine, contradict,
or replace Layer 1 governance. Where Layer 1 provides baseline
vocabularies (e.g., `doc_type`, `authority`, `scan_policy`), this
platform may extend those vocabularies for platform-specific needs but
must preserve the meaning of Layer 1 baseline values.

Dependency direction is downward only: this Layer 2 constitution depends
on Layer 1 governance. Layer 3 workflow bundles running on
agent-runner-v2 depend on this Layer 2 constitution. No lower layer may
redefine a higher layer.

## Document Map

This platform constitution set contains six permanent documents:

| Document | File | Template ID | Description |
|---|---|---|---|
| Platform Index | `README.md` | `SYS-02-IDX` | This document. Indexes the platform constitution set, states platform identity and Layer 1 inheritance. |
| Runtime Model | `RUNTIME_MODEL.md` | `SYS-02-RM` | Defines the execution architecture: step model, execution paths, job lifecycle, coder integration, rejection and retry. |
| Bundle Authoring Contract | `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Defines the contract every Layer 3 bundle must satisfy: required files, TOML format, artifact keys, governance requirements. |
| Shared Services | `SHARED_SERVICES.md` | `SYS-02-SS` | Defines runtime services available to Layer 3 bundles: context extensions, artifact resolution, path contracts, action registration. |
| Metadata Contract | `METADATA_CONTRACT.md` | `SYS-02-MC` | Defines platform-specific metadata extensions beyond Layer 1 baseline: doc_type values, authority values, additional frontmatter fields. |
| Validation Contract | `VALIDATION_CONTRACT.md` | `SYS-02-VC` | Defines the platform validation model: DocumentationValidationPlan pattern, section checks, frontmatter enforcement, bundle composition. |

The document map includes this index document. The published set
inventory is six documents, not five companions plus an implicit index.

## Scope

This constitution set covers:

- the platform runtime architecture and execution model
- the contract Layer 3 bundles must satisfy to run on this platform
- shared runtime services available to bundles
- platform-specific metadata extensions
- platform-specific validation patterns

This constitution set excludes:

- Layer 1 ecosystem governance (owned by `01_governance_foundation_v1`)
- concrete Layer 3 bundle definitions or inventories
- runtime runbooks or operational how-to guides
- installation or setup procedures
- job-history evidence or run-scoped artifacts
- codebase scanning or repository analysis results
