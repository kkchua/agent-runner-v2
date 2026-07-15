---
template_id: "SYS-00-IDX"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-15T23:45:00+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "refine_layer1_governance_docs"
change_id: "00L1-20260715-c2f96104"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `refine_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# System Documentation Index

This document defines the canonical documentation structure for a plugin workflow ecosystem. It establishes the three-layer model that governs how documentation is organized, owned, and maintained across repositories participating in the ecosystem.

## Audience Views

### Ecosystem Architects
Ecosystem architects define the reusable governance contracts that apply across all repositories using the plugin workflow system. They own the Layer 1 documents in this directory and ensure they remain generic enough to govern multiple repositories without embedding repository-specific details.

### Repository Maintainers
Repository maintainers implement Layer 2 master-doc structures and Layer 3 plugin workflow families within their specific repository. They follow the Layer 1 governance contract but do not modify it. Their outputs live under `docs/repo/`, which is outside Layer 1 ownership.

### Plugin Authors
Plugin authors create workflow bundles that conform to the Layer 1 bundle taxonomy and runtime governance rules. They rely on Layer 1 to define the generic contract for plugin workflow bundles, including packaging, publish/install mechanics, and artifact ownership enforcement.

### Operators
Operators manage the steady-state runtime of plugin workflow bundles through the registry control plane. They enforce validation gates, execution mode parity, and change control as defined in Layer 1 runtime governance.

## Document Map

The Layer 1 governance document set consists of four canonical documents:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [README.md](README.md) | SYS-00-IDX | This index — explains the three-layer model and audience views |
| [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) | SYS-00-DS | Defines the documentation authority, structure rules, and update triggers for Layer 1 docs |
| [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) | SYS-00-BT | Defines bundle classes, ownership rules, and packaging rules for core governance and plugin workflow bundles |
| [RUNTIME_GOVERNANCE.md](RUNTIME_GOVERNANCE.md) | SYS-00-RG | Defines the steady-state runtime model, registry control plane, plugin bundle control, and validation gates |

### Three-Layer Model

**Layer 1 — Ecosystem Governance**  
This layer owns only the four documents above. It defines reusable ecosystem governance that applies across all repositories using the plugin workflow system. Layer 1 must remain generic and must not name concrete workflow identifiers, repository-specific artifact inventories, or repository-specific scaffold names.

**Layer 2 — Repository Master-Doc Structure**  
Each repository defines its own Layer 2 master-doc and operating structure. Layer 2 implements the Layer 1 governance contract within the context of a specific repository. Layer 2 documents describe the repository's concrete workflow inventory, SDLC processes, and delivery scaffolds.

**Layer 3 — Plugin Workflow Families**  
Layer 3 consists of plugin workflow bundles and their repo-local outputs. Plugin bundles conform to the Layer 1 bundle taxonomy and runtime governance rules. Their outputs live under `docs/repo/` and are outside Layer 1 ownership.

### Repo-Local Output Boundary

All repository-specific analysis, delivery scaffolds, codebase inventories, and other repo-derived artifacts live under `docs/repo/`. These outputs are owned by Layer 2 or Layer 3, not by Layer 1. Layer 1 governance documents must not enumerate, reference, or claim ownership over any path under `docs/repo/`.

### Validation

Layer 1 governance documents are validated by the `validate_layer1_governance_docs` action, which enforces:
- Required section presence in each document
- Absence of concrete workflow identifiers in body text
- Absence of forbidden literal patterns that indicate unresolved placeholder tokens or legacy scaffold references
- Explicit mention of `docs/repo/` as the repo-local output boundary in README.md
- Generic definition of plugin workflow bundles in BUNDLE_TAXONOMY.md and RUNTIME_GOVERNANCE.md
- Recognition of both single-workflow and multi-workflow plugin bundles in RUNTIME_GOVERNANCE.md
