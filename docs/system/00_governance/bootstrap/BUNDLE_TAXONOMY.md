---
template_id: "SYS-00-BT"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-13T08:00:00+08:00"
workflow: "00_core_governance_bootstrap_v1"
step: "generate_core_governance_docs"
change_id: "INITIAL-BOOTSTRAP"
---

# Bundle Taxonomy

This document defines the bundle classes, ownership rules, and packaging requirements for workflow bundles in the agent-runner ecosystem.

## Bundle Classes

The agent-runner ecosystem recognizes one canonical bundle class at the ecosystem governance layer:

### Core Governance Bundles

Core governance bundles own ecosystem master docs that define the universal documentation contract for the entire agent-runner ecosystem. These bundles operate at Layer 1 of the three-layer documentation model.

**Characteristics**:
- Own only the four ecosystem master docs under `docs/system/00_governance/bootstrap/`
- Define universal rules that apply to all repositories using the framework
- Do not generate repo-derived analysis or claim ownership of `docs/repo/*` outputs
- Travel with the core runner code and take precedence over conflicting local guidance

**Example**: `00_core_governance_bootstrap_v1` is the sole core governance bundle in this ecosystem. It owns README.md, DOCUMENTATION_STANDARD.md, BUNDLE_TAXONOMY.md, and BUNDLE_MIGRATION_PLAN.md.

**Authority**: Highest — core governance bundles define the rules all other layers must follow.

Other workflow bundles exist in the ecosystem but are not classified as core governance bundles. They operate at Layer 2 (workflow bundle master docs) or Layer 3 (repo-local generated docs) and follow the contract defined by core governance bundles without modifying ecosystem master docs.

## Ownership Rules

Ownership rules determine which bundle class may modify which documentation layer:

### Core Governance Bundle Ownership

- Core governance bundles own only the four ecosystem master docs
- They do not own repo-local generated docs under `docs/repo/*`
- They do not classify or enumerate non-core bundle families
- They do not list concrete repository workflow inventory
- They do not describe prompt contracts using artifact placeholder syntax

### Workflow Bundle Ownership

- Individual workflow bundles own their bundle-local governance manifests under `workflows/<name>/bundle_governance/`
- They define how their specific workflow operates within the three-layer model
- They follow the contract defined by core governance bundles
- During publish or install, bundle-local governance files are copied into the global runner home

### Repo-Document Workflow Ownership

- Repo-document, scaffold, sync, and audience workflows own repo-local generated docs under `docs/repo/*`
- These docs are non-authoritative downstream outputs
- They reflect repository state at generation time and may become stale
- They are not canonical governance authority

### Boundary Enforcement

- No workflow or document outside `00_core_governance_bootstrap_v1` may modify the four ecosystem master docs
- No ecosystem master doc may claim ownership of repo-local outputs under `docs/repo/*`
- When prompt instructions conflict with repo-local stale docs, the core governance bundle contract wins

## Packaging Rules

Packaging rules determine how workflow bundles are structured and deployed:

### Bundle Structure

Each workflow package (`workflows/<name>/`) must contain:
- `workflow.toml` — declarative manifest defining steps, routing, artifact keys, and coder policies
- `prompts/` — directory containing prompt template files for each step
- `context_extensions.py` — optional workflow-specific context hooks (replaces hardcoded functions in step_runner.py)
- `bundle_governance/` — directory containing bundle-local governance manifests

### Dual-Path Discovery

Plugin workflow packages use dual-path discovery for runtime deployment:
1. **Global path**: `%USERPROFILE%\.ukbe-runner\workflows\<workflow_name>\<package_files>` — seeded during init or publish
2. **Local path**: `workflows\<workflow_name>\<package_files>` — fallback if global path is not available

The global path takes precedence. If both paths exist, the global copy is used.

### Generated Adapter Files

Bundle-local agent adapter files under `bundle_governance/generated/` (e.g., AGENTS.md, CLAUDE.md, QWEN.md) are generated from the canonical bundle governance source. They must not drift independently and must travel with the bundle into the global runner home during publish or install.

### Artifact Registry

Each workflow bundle declares its owned artifact set in `workflow.toml` under `[step.artifacts].produces`. The artifact registry is authoritative for:
- Bundle scope checks during validation
- Publish/install packaging decisions
- Prompt-time instruction alignment

Core governance bundles have a limited artifact set restricted to the four core governance documents plus deterministic review and validation outputs used by their own refinement loop.

### Versioning

Workflow bundles use semantic versioning in their `workflow.toml` manifest:
- `version = "1"` — major version (breaking changes to step structure or artifact keys)
- Changes to prompt templates or context extensions without structural changes do not require version bumps
- Core governance bundle version is independent of ecosystem master doc versions
