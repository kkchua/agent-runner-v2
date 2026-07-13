---
template_id: "SYS-00-DS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-13T23:04:55+08:00"
workflow: "00_core_governance_bootstrap_v1"
step: "generate_core_governance_docs"
change_id: "00CORE-20260713-7d31e8d4"
---

# Documentation Standard

This document defines the canonical documentation contract for the agent-runner ecosystem's four core governance master docs. It specifies structure, validation requirements, update triggers, and conformance rules that maintain ecosystem-wide consistency.

## Purpose

The documentation standard exists to enforce a single source of truth for ecosystem governance. By constraining the four canonical files under `docs/system/00_governance/bootstrap/` to a uniform contract, the ecosystem prevents:

- **Authority drift**: Multiple conflicting governance sources across repositories
- **Ownership confusion**: Unclear boundaries between ecosystem, bundle, and repo-local docs
- **Stale assumptions**: Legacy mixed-doc models propagating outdated rules
- **Validation gaps**: Inconsistent review criteria allowing non-conforming docs into production

This standard applies exclusively to the four ecosystem master docs. Repo-local generated docs under `docs/repo/*` must conform to ecosystem standards but are not governed by this specific contract.

## Audience Model

The four ecosystem master docs serve distinct audience segments within the platform engineering organization:

| Audience | Primary Interaction | Responsibility |
|----------|-------------------|----------------|
| Platform Engineers | Author and maintain Layer 1 docs | Ensure ecosystem standards reflect actual runtime behavior |
| Workflow Bundle Maintainers | Consume Layer 1, author Layer 2 | Align bundle docs with ecosystem contract without violating ownership boundaries |
| Repository Operators | Consume Layer 1 and Layer 2 | Generate repo-local docs within defined constraints |
| System Auditors | Verify conformance across all layers | Detect drift, validate migration progress, enforce governance contracts |

Each audience must understand which layer they operate within and which documents carry canonical authority for their scope. Platform engineers own Layer 1; bundle maintainers own Layer 2; repository operators produce Layer 3; auditors verify all three.

## Document Set

The ecosystem master doc set consists of exactly four files, each with a fixed template ID and purpose:

| File | Template ID | Canonical Role |
|------|-------------|----------------|
| README.md | SYS-00-IDX | System documentation index and three-layer model overview |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | This document: documentation contract and validation rules |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle classification, ownership rules, packaging requirements |
| BUNDLE_MIGRATION_PLAN.md | SYS-00-BMP | Migration strategy from legacy models to three-layer architecture |

No other files may reside in `docs/system/00_governance/bootstrap/` as canonical governance artifacts. Review outputs, validation reports, and audit trails are transient artifacts generated during workflow execution but do not become part of the persistent governance set.

All four files must include identical frontmatter blocks specifying template_id, version, doc_type, managed_by, generated_at, workflow, step, and change_id. Version strings follow semantic versioning (MAJOR.MINOR.PATCH) and increment only when the documentation contract itself changes.

## Architecture Baseline

The three-layer documentation architecture establishes clear ownership boundaries:

**Layer 1 (Ecosystem)**: Universal rules applicable across all repositories and workflow bundles. Owned by `00_core_governance_bootstrap_v1`. Changes require deterministic review, validation, and audit approval.

**Layer 2 (Workflow Bundles)**: Bundle-specific master docs that travel with each installed workflow package into the global runner home. Each bundle owns its Layer 2 docs but must not contradict Layer 1 rules.

**Layer 3 (Repo-Local)**: Generated outputs produced by repository-scanning workflows. These are downstream consumers of ecosystem and bundle rules, not governance authorities themselves.

The architecture baseline prohibits any Layer 3 output from modifying or overriding Layer 1 or Layer 2 docs. When stale repo-local guidance conflicts with current ecosystem master docs, the ecosystem docs win.

## Repo-Selected Profile

Individual repositories may select a documentation profile that determines which subset of repo-local outputs they generate. Profiles are configured at the repository level and influence which scaffold workflows execute during bootstrap operations.

Common profile dimensions include language stack, deployment model, and compliance tier. Profile selection does not modify the ecosystem master docs. It only controls which repo-local outputs appear under `docs/repo/*` for that specific repository.

## Migration Mode

Repositories transitioning from legacy mixed-doc models to the three-layer architecture operate in migration mode. During migration:

1. Legacy repo-derived analysis docs remain readable but are marked as deprecated
2. New repo-local outputs conform to the three-layer model from inception
3. Ecosystem master docs reference migration status but do not enumerate legacy artifact names
4. Validation gates check for ownership drift and stale assumptions before approving updates

Migration mode is temporary. Once a repository completes its transition, migration markers are removed and the repo operates under standard three-layer rules.

## Conditional Standards

Certain documentation requirements apply conditionally based on workflow visibility, bundle scope, or repository characteristics:

| Condition | Requirement | Applies To |
|-----------|-------------|------------|
| Workflow visibility = "canonical" | Must pass deterministic review gate | All ecosystem master docs |
| Bundle owns repo-local outputs | Must declare artifact registry in bundle_governance.toml | Layer 2 workflow bundles |
| Repository in migration mode | Must mark legacy outputs as deprecated | Repositories transitioning from mixed-doc models |
| Doc_type = "system" | Must include full frontmatter block | All four ecosystem master docs |

Conditional standards are evaluated during validation. Failure to meet applicable conditions results in rejection at the review or validation gate.

## Update Triggers

The four ecosystem master docs update only when specific triggers fire:

| Trigger | Description | Response |
|---------|-------------|----------|
| Ecosystem contract change | Universal documentation rule modified | Regenerate all four docs via `00_core_governance_bootstrap_v1` |
| Bundle taxonomy evolution | New bundle class added or ownership rule changed | Update BUNDLE_TAXONOMY.md, then cascade to affected docs |
| Migration milestone reached | Repository completes transition to three-layer model | Update BUNDLE_MIGRATION_PLAN.md status tracking |
| Validation failure detected | Deterministic check identifies ownership drift or stale assumption | Refine affected docs through review loop until approved |

Manual edits to ecosystem master docs are prohibited. All updates must flow through the workflow's deterministic generation, review, validation, and audit pipeline.

## Validation

Deterministic validation enforces the documentation contract before any ecosystem master doc reaches production. The validation gate checks:

1. **Frontmatter completeness**: All four files contain required metadata fields with correct values
2. **Section presence**: Required sections exist in each file (see individual file requirements below)
3. **Ownership boundary integrity**: No file claims authority outside its designated layer
4. **Forbidden pattern absence**: No file contains hardcoded artifact keys, legacy workflow IDs, or repo-derived placeholder names
5. **Cross-reference consistency**: Template IDs and document references match across all four files

### Required Sections by File

**README.md (SYS-00-IDX)**:
- System Documentation Index
- Audience Views
- Document Map

**DOCUMENTATION_STANDARD.md (SYS-00-DS)**:
- Purpose
- Audience Model
- Document Set
- Architecture Baseline
- Repo-Selected Profile
- Migration Mode
- Conditional Standards
- Update Triggers
- Validation

**BUNDLE_TAXONOMY.md (SYS-00-BT)**:
- Bundle Classes
- Ownership Rules
- Packaging Rules

**BUNDLE_MIGRATION_PLAN.md (SYS-00-BMP)**:
- Current State
- Target State
- Migration Phases

Validation fails immediately if any required section is missing, if forbidden patterns appear in file content, or if ownership boundaries are violated. Failed validation triggers the refinement loop, which updates only the owned core governance files before returning to deterministic review.

Repo-local generated docs under `docs/repo/*` undergo separate validation within their respective workflow bundles. They are not subject to this specific validation contract but must still conform to the broader ecosystem standards defined here.
