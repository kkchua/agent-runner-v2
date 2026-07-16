---
template_id: "SYS-00-DS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:13:00+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Documentation Standard

## Purpose

This document defines the documentation authority, structure rules, and
standards for the `agent-runner-v2` repository. It establishes the baseline
rules that apply to all documentation and explains how repository-specific
profiles and migration modes are selected.

## Audience Model

Repository documentation serves multiple audiences with distinct needs:

| Audience | Primary Concern | Document Focus |
|----------|-----------------|----------------|
| **Stakeholders** | Business value and capabilities | SYSTEM_OVERVIEW, BUSINESS_CAPABILITIES |
| **Developers** | Implementation guidance | FUNCTIONAL_SPEC, Codebase inventory |
| **Operators** | Runtime behavior and quality | NON_FUNCTIONAL_REQUIREMENTS |
| **Architects** | System design and migration | BUNDLE_TAXONOMY, BUNDLE_MIGRATION_PLAN |
| **Workflow Developers** | Bundle packaging standards | DOCUMENTATION_STANDARD, BUNDLE_TAXONOMY |

## Document Set

### Layer 2 Master Documents (This Directory)

The repository master docs consist of eight governance-facing documents:

| Document | Template ID | Scope | Owner |
|----------|-------------|-------|-------|
| README.md | SYS-00-IDX | Index and audience views | master-docs workflow |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Documentation rules | master-docs workflow |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle classification | master-docs workflow |
| BUNDLE_MIGRATION_PLAN.md | SYS-00-BMP | Migration strategy | master-docs workflow |
| SYSTEM_OVERVIEW.md | SYS-00-SO | Platform purpose and flows | master-docs workflow |
| BUSINESS_CAPABILITIES.md | SYS-00-BC | Operational capabilities | master-docs workflow |
| FUNCTIONAL_SPEC.md | SYS-00-FS | Functional behaviors | master-docs workflow |
| NON_FUNCTIONAL_REQUIREMENTS.md | SYS-00-NFR | Quality attributes | master-docs workflow |

### Layer 1 Ecosystem Baseline

The universal ecosystem baseline lives in `docs/system/00_governance/bootstrap/`:

- Layer 1 governance documents (README, DOCUMENTATION_STANDARD, BUNDLE_TAXONOMY, RUNTIME_GOVERNANCE)
- Ecosystem-wide standards that apply to all repositories
- Published from bootstrap workflows, not modified per-repo

### Codebase Documentation

Repository-specific codebase documentation lives in `docs/repo/codebase/`:

- **01_inventory/**: Module inventory and documentation status
- **02_modules/**: Per-module documentation
- **03_components/**: Component-level documentation
- **04_changes/**: Change impact assessments

## Architecture Baseline

### Universal Baseline (Layer 1)

Layer 1 documents establish the ecosystem-wide governance baseline:

- Documentation structure and template IDs
- Bundle taxonomy and ownership rules
- Runtime governance and publish model
- Scope purity requirements

These rules apply to all repositories in the ecosystem.

### Repository-Selected Profile

This repository has the following architecture posture:

| Attribute | Value | Rationale |
|-----------|-------|-----------|
| `current_profile` | transitional | Migrating from monolithic to plugin-based workflow bundles |
| `target_profile` | plugin-based workflow bundles | Self-contained packages with declarative manifests |
| `migration_mode` | active | Branch `feat/plugin-workflow-system`, version 0.3.0 |
| `repo_state` | explicit | Has CODER_IMPLEMENTATION_SOP.md, governance docs |

### Documentation Scope Rules

1. **Layer 2 documents must not** duplicate Layer 1 ecosystem governance
2. **Layer 2 documents must** reference Layer 1 for universal rules
3. **Layer 2 documents must** document repository-specific deviations
4. **Codebase docs must** remain synchronized with actual code state

## Migration Mode

### Current State

The repository is in active migration from legacy to plugin-based workflow bundles:

- **From**: Monolithic `TEMPLATE_GROUPS` dict (2453 lines in `template_groups.py`)
- **To**: Self-contained plugin workflow packages with declarative TOML manifests
- **Status**: Bootstrap workflows migrated, legacy SDLC workflows pending

### Implications for Documentation

During migration:

1. Both legacy and plugin documentation paths exist
2. Document references may use legacy workflow names until migration completes
3. Migration plan (BUNDLE_MIGRATION_PLAN.md) tracks progress
4. Plugin system is a configuration source adapter, not a runtime replacement

### Completion Criteria

Migration is complete when:

1. All workflow definitions use TOML manifests
2. Legacy `TEMPLATE_GROUPS` dict is removed
3. All workflow prompts are in `prompts/` directories
4. Context extensions are in `context_extensions.py` per workflow

## Conditional Standards

### When Repository Has No Prior Standard

When a repository has no clear prior documentation standard:

1. Apply the universal ecosystem baseline from Layer 1
2. Generate Layer 2 master docs via bootstrap workflow
3. Document the architecture posture (profile, migration mode)
4. Establish documentation update triggers

### When Repository Has Existing Standard

When a repository has existing documentation:

1. Preserve valuable content where possible
2. Map existing docs to new template IDs
3. Document deviations from ecosystem baseline
4. Plan migration if architecture is transitional

## Update Triggers

Layer 2 master documents should be updated when:

1. **Workflow changes**: New workflow bundles added or existing ones removed
2. **Architecture changes**: Migration progress, new capabilities
3. **Capability changes**: New business capabilities enabled by runner
4. **Quality changes**: New non-functional requirements or constraints
5. **Ecosystem baseline changes**: Layer 1 governance updates require propagation

Updates must be made through the `00_repo_master_docs_bootstrap_v1` workflow,
not through direct file editing.

## Validation

### Document Integrity

Each document must have:

- Complete YAML frontmatter with all required fields
- Correct template ID matching the document purpose
- Generated timestamp and workflow attribution
- Change ID for traceability

### Content Integrity

Each document must:

- Reference approved PROJECT_ANALYSIS.md (read-only input)
- Align with actual repository state
- Not duplicate Layer 1 ecosystem governance
- Follow section heading requirements

### Cross-Reference Integrity

- Document map in README.md must list all documents
- Cross-references between documents must be valid
- External references must resolve correctly
