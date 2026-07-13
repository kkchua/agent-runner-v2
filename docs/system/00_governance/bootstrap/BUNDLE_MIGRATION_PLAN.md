---
template_id: "SYS-00-BMP"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-13T08:00:00+08:00"
workflow: "00_core_governance_bootstrap_v1"
step: "generate_core_governance_docs"
change_id: "INITIAL-BOOTSTRAP"
---

# Bundle Migration Plan

This document describes the migration from legacy mixed-doc models toward the three-layer documentation model for the agent-runner ecosystem.

## Current State

Many repositories using the agent-runner framework currently operate with a mixed-doc model characterized by:

- Historical root markdown files (QWEN.md, CLAUDE.md, README.md) serving as both governance guidance and repo-specific documentation
- Stale repo-derived analysis docs scattered across `docs/system/` or project root directories
- Workflow prompts that reference outdated artifact placeholder syntax or legacy workflow IDs
- No clear separation between ecosystem-level governance and repository-local generated outputs
- Core runner code and active workflow bundles coexisting with outdated markdown that creates conflicting guidance

In this state, documentation authority is ambiguous. Contributors may follow stale root guidance instead of current workflow behavior, leading to inconsistent implementations and maintenance overhead.

Some repositories may have already begun partial migration by archiving historical root guidance under `docs/archive/root-guidance/` but still retain stale mixed outputs under `docs/system/00_governance/bootstrap/` from previous bootstrap workflows that did not enforce strict ownership boundaries.

## Target State

The target state is a clean three-layer documentation model with unambiguous ownership:

### Layer 1: Ecosystem Master Docs

Four canonical governance documents under `docs/system/00_governance/bootstrap/` owned exclusively by `00_core_governance_bootstrap_v1`:
- README.md — defines the three-layer model
- DOCUMENTATION_STANDARD.md — specifies structure and validation requirements
- BUNDLE_TAXONOMY.md — defines bundle classes and ownership rules
- BUNDLE_MIGRATION_PLAN.md — this document

These docs define universal rules and do not contain repo-derived analysis or enumerate repository-specific artifacts.

### Layer 2: Workflow Bundle Master Docs

Each workflow package (`workflows/<name>/`) contains its own governance manifest:
- `workflow.toml` — declarative step definition and artifact registry
- `prompts/` — prompt templates for each step
- `context_extensions.py` — optional workflow-specific context hooks
- `bundle_governance/` — bundle-local governance manifests including generated adapter files

Bundle-local docs travel with the workflow into the global runner home during publish or install.

### Layer 3: Repo-Local Generated Docs

Repository-specific outputs live cleanly under `docs/repo/*` and are owned by repo-document, scaffold, sync, and audience workflows:
- Repository analysis and codebase inventory
- System overviews and component architecture docs
- Audience-facing documentation and delivery run state

These docs are non-authoritative downstream outputs that reflect repository state at generation time. They are not canonical governance authority.

### Authority Chain

The canonical source of truth follows this order:
1. CODER_IMPLEMENTATION_SOP.md (execution discipline)
2. Active workflow bundle under `workflows/<name>/`
3. Current runner code under `agent_runner_v2/`
4. Generated ecosystem master docs under `docs/system/00_governance/bootstrap/`
5. Generated repo-local docs under `docs/repo/*`

Historical root guidance is moved to `docs/archive/root-guidance/` and treated as non-authoritative.

## Migration Phases

Migration occurs in four phases, each with specific deliverables and validation criteria.

### Phase 1: Inventory and Archive

**Goal**: Identify all existing documentation artifacts and archive historical root guidance.

**Actions**:
- Scan project root for historical markdown files (QWEN.md, CLAUDE.md, README.md, TODO_LIST.md, etc.)
- Move historical root guidance to `docs/archive/root-guidance/`
- Identify stale repo-derived analysis docs under `docs/system/` that belong to Layer 3
- Catalog existing workflow bundles and their current governance manifests

**Deliverables**:
- Archived root guidance under `docs/archive/root-guidance/`
- Inventory of stale system-level docs requiring migration or removal
- Updated CLAUDE.md and QWEN.md pointing to new authority chain

**Validation**:
- No historical root markdown files remain at project root except minimal pointer files
- CODER_IMPLEMENTATION_SOP.md exists and defines execution discipline
- Root markdown files explicitly defer to active workflow bundles and current runner code

### Phase 2: Core Governance Bootstrap

**Goal**: Generate the four ecosystem master docs and establish Layer 1 ownership.

**Actions**:
- Run `00_core_governance_bootstrap_v1` to generate the four ecosystem master docs
- Verify all four files exist under `docs/system/00_governance/bootstrap/` with correct frontmatter
- Validate structural and content requirements per DOCUMENTATION_STANDARD.md
- Ensure no scope violations (no repo-derived artifact names, no forbidden workflow IDs, no artifact placeholder syntax)

**Deliverables**:
- README.md with three-layer model description
- DOCUMENTATION_STANDARD.md with required sections
- BUNDLE_TAXONOMY.md with single core governance bundle class
- BUNDLE_MIGRATION_PLAN.md (this document)

**Validation**:
- All four files pass structural validation (required frontmatter, required sections)
- No file contains artifact placeholder syntax using curly-brace token patterns
- No file mentions deprecated workflow identifiers from legacy implementations
- BUNDLE_TAXONOMY.md contains no non-core bundle classifications
- DOCUMENTATION_STANDARD.md contains no repo-derived artifact names

### Phase 3: Workflow Bundle Alignment

**Goal**: Ensure all workflow bundles comply with the three-layer model and use dual-path discovery.

**Actions**:
- Review each workflow bundle under `workflows/<name>/` for compliance with BUNDLE_TAXONOMY.md
- Ensure each bundle contains `workflow.toml`, `prompts/`, `context_extensions.py`, and `bundle_governance/`
- Migrate hardcoded functions from `step_runner.py` into workflow-specific `context_extensions.py` files
- Update workflow prompts to remove references to stale artifact placeholder syntax
- Verify dual-path discovery works correctly (global path takes precedence over local fallback)

**Deliverables**:
- All workflow bundles structured according to packaging rules
- Context extensions separated from core runner code
- Prompt templates using centralized artifact key constants
- Dual-path discovery validated for global and local workflow copies

**Validation**:
- No hardcoded path strings in `step_runner.py` or `documentation_guardrails.py`
- All workflow prompts reference artifact keys via centralized constants
- Bundle governance files exist and are consistent with workflow.toml declarations
- Publish/install correctly seeds bundles to global runner home

### Phase 4: Repo-Local Doc Separation

**Goal**: Move all repo-derived analysis outputs to `docs/repo/*` and clarify non-authoritative status.

**Actions**:
- Identify repo-document, scaffold, sync, and audience workflows (including the canonical scaffold workflow and other repo-bootstrap workflows)
- Configure these workflows to write outputs under `docs/repo/*` instead of `docs/system/`
- Remove any remaining stale repo-derived analysis docs from `docs/system/00_governance/bootstrap/`
- Update ecosystem master docs to reference the canonical scaffold workflow if needed
- Clarify in README.md that repo-local docs are non-authoritative downstream outputs

**Deliverables**:
- Clean separation: `docs/system/` contains only four ecosystem master docs
- Repo-local outputs under `docs/repo/*` owned by appropriate workflows
- Updated migration plan reflecting completion status
- Final audit confirming no scope violations remain

**Validation**:
- `docs/system/00_governance/bootstrap/` contains exactly four files (README.md, DOCUMENTATION_STANDARD.md, BUNDLE_TAXONOMY.md, BUNDLE_MIGRATION_PLAN.md) plus optional review/validation outputs
- No repo-derived artifact names appear in ecosystem master docs
- No ecosystem master doc claims ownership of `docs/repo/*` outputs
- Canonical scaffold workflow ID is correct (`10_execution_scaffold_v2`, not deprecated alternatives)
- Final workflow audit passes all scope violation checks

### Phase Completion Criteria

Migration is complete when:
- All four ecosystem master docs exist and pass validation
- Legacy root guidance has been archived under `docs/archive/root-guidance/`
- All workflow bundles comply with packaging rules and use dual-path discovery
- Repo-local docs are cleanly separated under `docs/repo/*`
- No stale mixed-doc assumptions remain in workflow prompts or bundle governance
- Final audit step in `00_core_governance_bootstrap_v1` approves accuracy

Repositories may remain in any phase indefinitely if business constraints prevent immediate migration, but should prioritize reaching Phase 4 to eliminate ambiguous documentation authority.
