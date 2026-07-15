---
template_id: "SYS-00-IDX"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-15T22:38:14+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "generate_layer1_governance_docs"
change_id: "00L1-20260715-74497d6b"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `generate_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Layer 1 Ecosystem Governance

## System Documentation Index

This index is the canonical entry point for the Layer 1 ecosystem governance
documentation set. Layer 1 governance defines reusable, repository-agnostic
policies that govern plugin workflow ecosystems across any repository that
adopts the agent-runner framework.

### Documentation Layering Model

The governance framework uses a three-layer model to separate ecosystem-level
policy from repository-level structure and workflow-level execution:

- **Layer 1 — Ecosystem Governance.** Permanent, reusable governance documents
  that define documentation authority, bundle taxonomy, runtime control-plane
  expectations, and validation gates. Layer 1 is owned by the governance
  bootstrap workflow and is intentionally narrow in scope. It does not define
  repository-specific workflow inventories, artifact names, or output paths.

- **Layer 2 — Repository or Bundle Master-Doc and Operating Structure.**
  Repository-specific master documentation, SDLC operating structure, and
  bundle-local SOPs. Layer 2 documents adapt Layer 1 policy to a specific
  repository's context. They may reference concrete workflow identifiers and
  repository-specific artifacts but must not contradict Layer 1 rules.

- **Layer 3 — Plugin Workflow Families and Repository-Local Outputs.**
  Individual plugin workflow bundle definitions, generated artifacts, and
  workflow-specific outputs. Layer 3 is where runtime execution produces
  concrete deliverables governed by the policies established in Layers 1 and 2.

Repo-local outputs live under `docs/repo/` and are outside Layer 1 ownership.
The Layer 1 document set does not enumerate, define, or govern
repository-specific artifacts, filenames, or output paths. Repositories are
responsible for their own `docs/repo/` content under Layer 2 governance.

## Audience Views

The Layer 1 documentation set serves three primary audiences:

| Audience | Primary Interest | Relevant Documents |
|----------|-----------------|-------------------|
| **Ecosystem architects** | Governance policy, bundle taxonomy, runtime control-plane rules | All four Layer 1 documents |
| **Repository maintainers** | Documentation structure rules, bundle ownership boundaries, validation gates | README, DOCUMENTATION_STANDARD, BUNDLE_TAXONOMY |
| **Plugin workflow authors** | Bundle packaging rules, runtime publish/install model, validation expectations | BUNDLE_TAXONOMY, RUNTIME_GOVERNANCE |

## Document Map

| Document | Template ID | Purpose |
|----------|-------------|---------|
| **README.md** | SYS-00-IDX | This index. Defines the three-layer model, audience views, and document map for the Layer 1 governance set. |
| **DOCUMENTATION_STANDARD.md** | SYS-00-DS | Documentation authority, structure rules, and validation criteria for the four Layer 1 governance documents. |
| **BUNDLE_TAXONOMY.md** | SYS-00-BT | Bundle class definitions, ownership boundaries, and packaging rules for core governance bundles and plugin workflow bundles. |
| **RUNTIME_GOVERNANCE.md** | SYS-00-RG | Steady-state runtime model: publish/install, registry control plane, artifact ownership, execution mode parity, and validation gates. |

All four documents are workflow-generated and protected from manual edits.
Changes to the Layer 1 document set must flow through the governance bootstrap
workflow, which enforces scope purity, deterministic ownership, and validation
correctness before accepting changes.
