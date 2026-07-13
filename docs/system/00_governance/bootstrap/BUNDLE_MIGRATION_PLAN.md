---
template_id: "SYS-00-BMP"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-13T23:04:55+08:00"
workflow: "00_core_governance_bootstrap_v1"
step: "generate_core_governance_docs"
change_id: "00CORE-20260713-7d31e8d4"
---

# Bundle Migration Plan

This document defines the canonical migration strategy for transitioning the agent-runner ecosystem from legacy mixed-doc models to the three-layer documentation architecture. It specifies current state, target state, and phased migration approach that maintains operational continuity throughout the transition.

## Current State

The ecosystem currently operates in a transitional mode where legacy mixed-doc outputs coexist with emerging three-layer model artifacts. Key characteristics of the current state include:

### Legacy Mixed-Doc Presence

Repositories contain repo-derived analysis docs produced by repository-scanning workflows. These outputs historically served dual purposes: both as local development references and as de facto governance guidance. This mixing of concerns created authority confusion and documentation drift.

Legacy outputs remain readable but are progressively marked as deprecated as repositories adopt the three-layer model. They do not define ecosystem-wide rules and must not be treated as canonical governance authority.

### Emerging Three-Layer Adoption

Core governance bundles now own the universal documentation contract through four canonical files under `docs/system/00_governance/bootstrap/`. Workflow bundles carry their own master docs into the global runner home during publish and install operations. Repo-local generated docs live under `docs/repo/*` as downstream outputs.

The scaffold workflow `10_execution_scaffold_v2` orchestrates repo-local doc generation within boundaries defined by ecosystem master docs. It does not claim ownership of governance rules or attempt to modify Layer 1 artifacts.

### Operational Gaps

Current gaps that migration addresses:

- Inconsistent validation criteria across repositories
- Unclear ownership boundaries between ecosystem, bundle, and repo-local layers
- Stale assumptions propagating from deprecated workflow IDs and legacy placeholder styles
- Missing deterministic review gates allowing non-conforming docs into production

## Target State

The target state achieves complete separation of concerns with clear ownership boundaries and deterministic validation at every layer:

### Fully Separated Layers

**Layer 1 (Ecosystem)**: Four canonical master docs under `docs/system/00_governance/bootstrap/` define universal rules. Owned exclusively by `00_core_governance_bootstrap_v1`. Changes require deterministic review, validation, and audit approval. No repo-derived content appears in Layer 1.

**Layer 2 (Workflow Bundles)**: Each workflow bundle carries its own master docs into the global runner home. Bundle-local docs govern their specific workflow's domain but must not contradict Layer 1 rules. The plugin-based workflow bundle system uses dual-path discovery (global first, local fallback) for runtime deployment.

**Layer 3 (Repo-Local)**: Generated outputs under `docs/repo/*` serve as downstream derived artifacts. They conform to ecosystem and bundle standards but hold no governance authority. Repository operators consume Layer 1 and Layer 2 rules to produce Layer 3 outputs within defined constraints.

### Deterministic Validation

All four ecosystem master docs pass through deterministic review, validation, and audit gates before reaching production. Validation checks:

- Frontmatter completeness with correct template IDs and version strings
- Required section presence matching each file's specification
- Ownership boundary integrity preventing authority drift
- Forbidden pattern absence (hardcoded artifact keys, legacy workflow IDs, repo-derived placeholder names)
- Cross-reference consistency across all four files

Workflow bundles undergo similar validation within their own governance manifests. Repo-local outputs validate against their respective bundle rules but are not subject to the core governance validation contract.

### Zero Legacy Artifacts

Legacy mixed-doc outputs are fully deprecated and removed from active governance consideration. Repositories operate exclusively within the three-layer model. Migration markers are removed once transition completes.

## Migration Phases

Migration proceeds through four sequential phases, each building on the previous phase's foundation. Repositories may enter migration at different times but must complete all phases to reach target state.

### Phase 1: Ecosystem Master Doc Establishment

**Objective**: Establish the four canonical ecosystem master docs as the universal documentation contract.

**Activities**:
- Generate README.md, DOCUMENTATION_STANDARD.md, BUNDLE_TAXONOMY.md, and BUNDLE_MIGRATION_PLAN.md via `00_core_governance_bootstrap_v1`
- Pass deterministic review, validation, and audit gates for initial approval
- Publish ecosystem master docs to `docs/system/00_governance/bootstrap/`
- Declare core governance bundle as supreme authority over documentation contracts

**Success Criteria**:
- All four files exist with correct frontmatter and required sections
- No forbidden patterns appear in file content
- Ownership boundaries explicitly documented
- Validation gate passes without refinement loops

**Exit Condition**: Ecosystem master docs approved and published to production.

### Phase 2: Workflow Bundle Alignment

**Objective**: Align existing workflow bundles with the three-layer model and establish dual-path discovery.

**Activities**:
- Convert monolithic template configurations to plugin-based workflow packages
- Each bundle creates `bundle_governance/` directory with canonical governance docs
- Generated adapter files (AGENTS.md, CLAUDE.md, QWEN.md) travel with bundle during publish/install
- Validate bundle manifests declare artifact registries excluding paths owned by other bundles

**Success Criteria**:
- All active workflows use plugin-based package structure
- Bundle governance docs explicitly declare ownership boundaries
- Dual-path discovery functional (global runner home primary, local repo fallback secondary)
- No bundle claims ownership of another bundle's artifact paths

**Exit Condition**: All workflow bundles conform to three-layer model without ownership conflicts.

### Phase 3: Repo-Local Output Segregation

**Objective**: Separate repo-derived analysis docs from governance authority and mark them as downstream outputs.

**Activities**:
- Identify all repo-local generated docs under `docs/repo/*` in each repository
- Mark legacy mixed-doc outputs as deprecated (not deleted, but flagged as non-authoritative)
- Configure scaffold workflow `10_execution_scaffold_v2` to generate new repo-local outputs within three-layer boundaries
- Update repository operators' understanding of Layer 3's subordinate role

**Success Criteria**:
- All repo-local docs clearly labeled as downstream derived outputs
- No repo-local doc claims governance authority over ecosystem or bundle rules
- Scaffold workflow generates compliant outputs without violating ownership boundaries
- Repository operators understand Layer 3's limited scope

**Exit Condition**: All repositories segregate repo-local outputs from governance authority.

### Phase 4: Legacy Artifact Decommission

**Objective**: Remove deprecated legacy outputs and achieve zero legacy artifact presence.

**Activities**:
- Archive legacy repo-derived analysis docs that served dual governance/development purposes
- Remove stale workflow IDs and legacy placeholder styles from active configurations
- Clean up hardcoded artifact keys and mixed assumption prompts
- Verify all repositories operate exclusively within three-layer model

**Success Criteria**:
- Zero legacy mixed-doc outputs remain in active governance consideration
- All workflow IDs match current registry without deprecated identifiers
- Prompt templates use centralized REFERENCE_FILES dict keys instead of hardcoded paths
- Validation gates consistently reject ownership drift and stale assumptions

**Exit Condition**: Ecosystem reaches target state with fully separated layers, deterministic validation, and zero legacy artifacts. Migration markers removed from all repositories.

### Post-Migration Governance

After completing all four phases, the ecosystem operates under standard three-layer rules without migration mode overhead. Ongoing governance follows these principles:

- Core governance bundles update only through deterministic workflow execution
- Workflow bundles evolve within their declared ownership boundaries
- Repo-local outputs conform to ecosystem and bundle standards without claiming authority
- System auditors verify conformance across all layers and detect drift before it propagates

New repositories bootstrap directly into the three-layer model without passing through migration phases. Legacy repositories that completed migration maintain target state indefinitely unless ecosystem contract changes trigger a new migration cycle.
