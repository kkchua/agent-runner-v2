---
template_id: "SYS-00-BT"
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

# Bundle Taxonomy

## Bundle Classes

The plugin workflow ecosystem recognizes two primary bundle classes:

**Core Governance Bundles**  
These bundles own the Layer 1 governance documents (README.md, DOCUMENTATION_STANDARD.md, BUNDLE_TAXONOMY.md, RUNTIME_GOVERNANCE.md). They define reusable ecosystem governance that applies across all repositories. Core governance bundles are canonical and must remain generic — they must not name concrete workflow identifiers or repository-specific artifacts.

**Plugin Workflow Bundles**  
These bundles define one or more workflows that conform to the Layer 1 runtime governance contract. A plugin workflow bundle may be a single-workflow bundle (containing exactly one workflow) or a multi-workflow bundle (containing multiple related workflows). Plugin bundles are owned by their authors and must declare their artifact production, validation rules, and execution mode parity requirements.

## Ownership Rules

Bundle ownership follows these rules:

**Core Governance Ownership**
Layer 1 governance documents are owned by the ecosystem architect role. Changes require ecosystem-wide review and must preserve backward compatibility where possible.

**Plugin Bundle Ownership**
Each plugin workflow bundle is owned by its author. The author defines the bundle's workflow definitions, artifact production rules, and validation gates. Plugin bundles must conform to the Layer 1 runtime governance contract but are otherwise autonomous.

**Repo-Local Output Boundary**
Repository-specific outputs live under `docs/repo/`. These outputs are outside Layer 1 ownership and are managed by Layer 2 (repository master-doc structure) or Layer 3 (plugin workflow families). Layer 1 bundles define the generic contract for bundle packaging and artifact declaration but do not claim ownership over repository-specific artifacts.

## Packaging Rules

Plugin workflow bundles must follow these packaging rules:

**Bundle Manifest**
Every plugin bundle must include a manifest declaring its schema version, workflow definitions, artifact production rules, and validation gates.

**Artifact Declaration**  
Each workflow in a bundle must declare which artifacts it produces and which artifacts it requires as inputs. This enables deterministic artifact flow validation.

**Execution Mode Parity**  
Bundles must ensure their workflows behave identically across daemon mode, manual mode, and backend execution mode. Execution mode parity is enforced at validation time.

**Validation Gates**  
Each bundle must define validation gates that verify artifact correctness, section presence, and scope purity before a workflow step can complete.

**Single-Workflow and Multi-Workflow Support**  
A plugin bundle may contain exactly one workflow (single-workflow bundle) or multiple workflows (multi-workflow bundle). The runtime control plane must support both patterns without requiring separate handling logic.
