---
template_id: "SYS-00-IDX"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-13T23:04:55+08:00"
workflow: "00_core_governance_bootstrap_v1"
step: "generate_core_governance_docs"
change_id: "00CORE-20260713-7d31e8d4"
---

# System Documentation Index

This document defines the canonical documentation index for the agent-runner ecosystem. It governs the universal documentation contract and three-layer model that all workflows and repositories must follow.

## Three-Layer Documentation Model

The agent-runner ecosystem uses a three-layer documentation architecture to separate concerns, enforce ownership boundaries, and prevent documentation drift.

### Layer 1: Ecosystem Master Docs

**Location**: `docs/system/00_governance/bootstrap/`
**Owner**: `00_core_governance_bootstrap_v1` workflow bundle

Ecosystem master docs define the universal documentation contract for the entire agent-runner ecosystem. They specify:

- The documentation standard (structure, validation, update triggers)
- Bundle taxonomy and ownership rules
- Migration plans for evolving documentation models
- Governance contracts that apply across all repositories

These four files are canonical runtime guidance. All other documentation in the ecosystem must conform to the rules defined here.

### Layer 2: Workflow Bundle Master Docs

**Location**: Bundled within each workflow package under `workflows/<name>/bundle_governance/`
**Owner**: Individual workflow bundles

Each workflow bundle carries its own master documentation into the global runner home (`%USERPROFILE%\.ukbe-runner\workflows\<workflow_name>\`). These bundle-local docs define:

- Workflow-specific documentation requirements
- Artifact production rules for that workflow's domain
- Review and validation criteria specific to the workflow's purpose

Workflow bundle docs travel with the bundle during publish and install operations. They are authoritative for their workflow's scope but subordinate to ecosystem master docs when conflicts arise.

### Layer 3: Repo-Local Generated Docs

**Location**: `docs/repo/*` within individual repositories
**Owner**: Repo-document and scaffold workflows

Repo-local generated docs are downstream outputs produced by repository-scanning and delivery workflows. They include various analysis artifacts, architectural descriptions, operational guides, and planning records derived from individual repository state.

**Critical boundary**: Repo-local docs are **not** canonical governance authority. They are derived outputs that must conform to ecosystem standards but do not define ecosystem-wide rules. Changes to repo-local docs never propagate upward to modify ecosystem or bundle master docs.

## Audience Views

The documentation system serves multiple audiences through targeted views:

| Audience | Primary Concern | Key Documents |
|----------|----------------|---------------|
| Platform Engineers | Ecosystem governance, bundle packaging | This index, DOCUMENTATION_STANDARD.md, BUNDLE_TAXONOMY.md |
| Repository Maintainers | Repo-local doc generation, compliance | Scaffold workflow outputs, validation reports |
| Delivery Agents | Task execution, artifact production | Bundle-specific master docs, delivery templates |
| System Auditors | Compliance verification, drift detection | Validation reports, audit trails, migration status |

Each audience interacts primarily with the layer relevant to their role. Platform engineers own Layer 1, repository maintainers consume Layer 2 and produce Layer 3, delivery agents operate within Layer 2 constraints, and auditors verify conformance across all layers.

## Document Map

The four canonical ecosystem master docs form a self-contained governance set:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| **README.md** (this file) | SYS-00-IDX | System documentation index and three-layer model overview |
| **DOCUMENTATION_STANDARD.md** | SYS-00-DS | Documentation contract: structure, validation, update triggers |
| **BUNDLE_TAXONOMY.md** | SYS-00-BT | Bundle classification and ownership rules |
| **BUNDLE_MIGRATION_PLAN.md** | SYS-00-BMP | Migration strategy from legacy mixed-doc models to three-layer architecture |

These documents are managed exclusively by the `00_core_governance_bootstrap_v1` workflow. Updates require passing deterministic review, validation, and audit gates before approval.

The canonical scaffold workflow for repository-level execution is `10_execution_scaffold_v2`, which orchestrates repo-local doc generation within the boundaries defined by these ecosystem master docs.

## Ownership Boundaries

Explicit separation of concerns prevents documentation drift and authority confusion:

- **Global governance docs** (Layer 1): Canonical runtime guidance for the entire ecosystem. Owned by `00_core_governance_bootstrap_v1`.
- **Workflow bundle docs** (Layer 2): Canonical for their specific workflow's domain. Owned by individual workflow bundles.
- **Repo-generated docs** (Layer 3): Downstream derived outputs. Owned by repo-document and scaffold workflows. Not canonical governance authority.

No workflow outside `00_core_governance_bootstrap_v1` may modify Layer 1 docs. No repo-local output may claim governance authority over ecosystem or bundle rules. When prompt instructions or stale repo docs conflict with this contract, the ecosystem master docs win.
