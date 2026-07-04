---
template_id: "SYS-00-DS"
title: "Documentation Standard"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the universal documentation baseline that applies to every repository using the agent-runner-v2 platform. It establishes the minimum documentation expectations, the document set structure, and the rules for repo-specific profile selection and migration.

## Audience Model

| Audience | Concern | Primary Sections |
|----------|---------|------------------|
| **Repository Contributors** | What documents must I maintain? | Document Set, Conditional Standards |
| **Workflow Authors** | How do I define documentation requirements? | Architecture Baseline, Update Triggers |
| **Platform Maintainers** | How do I evolve documentation standards? | Migration Mode, Validation |
| **New Team Members** | Where do I find information? | Document Set, Repo-Selected Profile |

## Document Set

### Universal Baseline Documents

Every repository using agent-runner-v2 must maintain these documents:

| Document | Location | Purpose | Owner |
|----------|----------|---------|-------|
| `README.md` | Repository root | Entry point and quick start | Manual |
| `QWEN.md` | Repository root | Project context for Qwen Code | Manual |
| `codebase_inventory.md` | `docs/codebase/01_inventory/` | Codebase module inventory | Workflow-generated |
| `README.md` | `docs/system/00_governance/bootstrap/` | System doc index | Workflow-generated |

### Required System Documents

Repositories must maintain these system documents at minimum:

| Document | Template ID | Required For |
|----------|-------------|--------------|
| `SYSTEM_OVERVIEW.md` | SYS-00-SO | All profiles |
| `FUNCTIONAL_SPEC.md` | SYS-00-FS | All profiles |
| `DOCUMENTATION_STANDARD.md` | SYS-00-DS | All profiles |

### Architecture Documents (Profile-Dependent)

| Document | Template ID | Required For |
|----------|-------------|--------------|
| `SYSTEM_CONTEXT.md` | SYS-01-SC | `explicit` and `strict` profiles |
| `COMPONENT_ARCHITECTURE.md` | SYS-01-CA | `explicit` and `strict` profiles |
| `DECISION_LOG.md` | SYS-01-DL | `explicit` and `strict` profiles |

### Operations Documents (Profile-Dependent)

| Document | Template ID | Required For |
|----------|-------------|--------------|
| `RUNBOOK.md` | SYS-02-RB | `explicit` and `strict` profiles |
| `DEVELOPER_GUIDE.md` | SYS-02-DG | `explicit` and `strict` profiles |

## Architecture Baseline

The documentation standard recognizes three architecture profiles that determine documentation obligations:

| Profile | Description | Documentation Requirement |
|---------|-------------|---------------------------|
| `provisional` | Early-stage repository with minimal documentation | Core documents only; bootstrap generates rest |
| `explicit` | Mature repository with documented architecture | Full system documentation set |
| `strict` | Repository with compliance requirements | Full set plus validation gates |

### Profile Selection Criteria

Repositories select profiles based on:

1. **Lifecycle Stage**: New repositories start as `provisional`
2. **Team Size**: Larger teams benefit from `explicit` documentation
3. **Integration Complexity**: External-facing APIs warrant `strict` documentation
4. **Operational Criticality**: Production systems should be `explicit` or `strict`

## Repo-Selected Profile

This repository (`agent-runner-v2`) operates under the following profile:

| Attribute | Value |
|-----------|-------|
| `current_profile` | `provisional` |
| `target_profile` | `explicit` |
| `selection_reason` | Bootstrap workflow in progress; documentation being generated |

The repository contains substantial implementation (56+ Python modules, 11 workflow families) but is currently generating its system documentation through the `00_master_docs_bootstrap_v1` workflow. Upon bootstrap completion, the profile transitions to `explicit`.

## Migration Mode

Repositories may transition between profiles as they mature:

| Transition | Trigger | Action |
|------------|---------|--------|
| `provisional` → `explicit` | Bootstrap completion | Generate full architecture documentation |
| `explicit` → `strict` | Compliance requirement | Add validation gates and stricter change control |
| Any → lower | Simplification | Archive documents no longer required |

### Migration Rules

1. **Up-migrations** are triggered by workflow completion or governance decision
2. **Down-migrations** require explicit approval and document archival
3. **Profile changes** must be recorded in `DECISION_LOG.md`
4. **Document retention**: Documents from higher profiles may be retained as reference but marked `archived`

## Conditional Standards

### Workflow-Generated Documents

Documents marked as `workflow-generated` in the Document Set:

- Are owned by specific workflows
- Must not be edited manually (changes will be overwritten)
- Include workflow attribution in frontmatter
- Carry the managed banner: "This file is workflow-generated and protected from manual edits"

### Protected Document Rules

1. **No manual edits** to workflow-generated content
2. **No rename** without workflow update
3. **No deletion** without workflow deregistration
4. **Review required** before workflow updates that change structure

### Manual Document Rules

1. **Authors** maintain documents they create
2. **Updates** must not break workflow contracts
3. **Frontmatter** must be preserved on workflow-generated files
4. **Cross-references** must remain valid

## Update Triggers

Documentation updates are triggered by:

| Trigger | Documents Affected | Action |
|---------|-------------------|--------|
| Code change affecting API | Module docs, COMPONENT_ARCHITECTURE | Sync via documentation_sync_v1 |
| Workflow bundle update | Workflow-specific generated docs | Regenerate via workflow |
| Bootstrap milestone | System docs, inventory | Regenerate via bootstrap workflow |
| Manual governance decision | Standards, DECISION_LOG | Manual update with ADR |
| Dependency change | Affected integration docs | Sync via documentation_sync_v1 |

## Validation

Documentation compliance is validated by:

1. **Existence checks**: Required documents must exist
2. **Frontmatter validation**: Required fields present and valid
3. **Cross-reference validation**: Links must resolve
4. **Template conformance**: Documents must match their template_id structure
5. **Protected document guards**: Manual edits to workflow-generated docs are flagged

### Validation Failures

| Failure | Severity | Remediation |
|---------|----------|-------------|
| Missing required document | Error | Generate or create manually |
| Invalid frontmatter | Warning | Fix frontmatter fields |
| Broken cross-reference | Warning | Update or remove reference |
| Manual edit to protected doc | Error | Revert or escalate to workflow |

---

*This standard applies to all repositories using agent-runner-v2. Profile selection is repository-specific and recorded in repository analysis.*
