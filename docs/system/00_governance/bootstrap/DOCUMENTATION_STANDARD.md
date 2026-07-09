---
template_id: "SYS-00-DS"
managed_by: workflow-generated
generated: "2026-07-09T21:18:02+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation standards for agent-runner-v2, establishing the baseline rules that apply to every document in the system, how repo-specific profiles are selected, and how documents are maintained over time.

The documentation standard serves as the contract between the workflow system and document consumers, ensuring consistency, discoverability, and maintainability across all generated and manually-authored content.

## Audience Model

| Audience | Concerns | Primary Documents |
|----------|----------|-------------------|
| **Workflow Authors** | Template consistency, section requirements, validation rules | This document, template registry |
| **Document Contributors** | Where to add content, how to structure documents, what sections are required | This document, individual templates |
| **Code Reviewers** | Whether generated documents meet contract, if manual edits violate guardrails | Validation outputs, change logs |
| **System Maintainers** | Migration procedures, profile selection, conditional standards | Migration plan, this document |

## Document Set

### System Documentation

System documentation explains the platform at a level useful to users, developers, and stakeholders.

| Document | Template ID | Purpose | Audience |
|----------|-------------|---------|----------|
| README.md | SYS-00-IDX | Documentation index and navigation | All |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Documentation conventions and baseline rules | Workflow authors |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle structure and organization | System maintainers |
| BUNDLE_MIGRATION_PLAN.md | SYS-00-BMP | Version migration procedures | System maintainers |
| SYSTEM_OVERVIEW.md | SYS-00-SO | Platform purpose and workflow model | Stakeholders, new team members |
| BUSINESS_CAPABILITIES.md | SYS-00-BC | Operational capabilities | Stakeholders, operators |
| FUNCTIONAL_SPEC.md | SYS-00-FS | System behaviors and capabilities | Developers, operators |
| NON_FUNCTIONAL_REQUIREMENTS.md | SYS-00-NFR | Quality and operational expectations | Developers, operators |

### Architecture Documentation

Architecture documentation explains implementation details, component relationships, and operational procedures.

| Document | Template ID | Purpose | Audience |
|----------|-------------|---------|----------|
| SYSTEM_CONTEXT.md | SYS-00-SC | System context and boundaries | Developers |
| COMPONENT_ARCHITECTURE.md | SYS-00-CA | Component structure and interactions | Developers |
| DECISION_LOG.md | SYS-00-DL | Architectural decisions | Developers, stakeholders |
| SYSTEM_FILE_STRUCTURE.md | SYS-00-SFS | File organization and conventions | Developers |
| DEVELOPER_GUIDE.md | SYS-00-DG | Development procedures and conventions | Developers |
| RUNBOOK.md | SYS-00-RB | Operational procedures | Operators |
| EXISTING_REPO_WORKFLOW_SOP.md | SYS-00-SOP | Workflow SOP for existing repos | Developers |

### Codebase Documentation

Codebase documentation tracks repository structure, module documentation, and changes.

| Document | Template ID | Purpose |
|----------|-------------|---------|
| CODEBASE_INVENTORY | CB-01 | Module and file inventory |
| MODULE_DOCUMENTATION | CB-02 | Individual module documentation |
| COMPONENT_DOCUMENTATION | CB-03 | Component and workflow family documentation |
| CHANGE_IMPACT | CB-04 | Change impact documentation |

## Architecture Baseline

### Universal Baseline

The following rules apply to **every** repository using agent-runner-v2:

1. **Frontmatter Required**: All system documents include YAML frontmatter with `template_id`, `managed_by`, `generated`, `workflow`, and `step` fields
2. **Protection Banner**: All workflow-generated documents include a protection banner immediately after frontmatter
3. **Template ID Stability**: `template_id` values are stable and do not change across regeneration
4. **Artifact Keys**: All document references use artifact key constants, never hardcoded paths
5. **Validation**: Documents are validated against section requirements defined in `constants.py`

### Document Lifecycle

| State | Meaning | Transitions |
|-------|---------|-------------|
| **draft** | Initial creation, not yet reviewed | → review |
| **review** | Under review, may have feedback | → approved, → refine |
| **approved** | Accepted as current truth | → superseded |
| **superseded** | Replaced by newer version | — |

### Generation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **create** | New document from template | First generation |
| **refresh** | Update existing document | Periodic reconciliation |
| **patch** | Minimal update for specific change | Targeted fix |

## Repo-Selected Profile

### Profile Selection

Repositories select an architecture profile that determines documentation depth and structure:

| Profile | Description | Documentation Depth |
|---------|-------------|---------------------|
| **minimal** | Essential documents only | Index + overview only |
| **standard** | Core system documentation | All SYS-00-* documents |
| **explicit** | Full documentation with decision tracking | Standard + detailed decision log |
| **universal-bootstrap** | Reusable workflow system | All documents, template registry, agent contracts |

### agent-runner-v2 Profile

| Attribute | Value |
|-----------|-------|
| **current_profile** | explicit |
| **target_profile** | universal-bootstrap |
| **migration_mode** | maintenance |

### Evidence for Profile Selection

1. **Comprehensive workflow definitions**: 12+ workflow families defined in `template_groups.py`
2. **Strict v2 contract enforcement**: Explicit rejection of v1 patterns in code
3. **Centralized constants**: All paths via `constants.py` with artifact keys
4. **Bootstrap bundle structure**: Full template and SOP collection in `bootstrap/bundles/`
5. **Generated doc protection**: `documentation_guardrails.py` with manifest tracking
6. **Test infrastructure**: 109+ unit tests with strict separation

## Migration Mode

### Maintenance Mode

agent-runner-v2 operates in **maintenance mode** for documentation:

- Existing documents are refreshed rather than recreated
- Template IDs are preserved across regenerations
- Section requirements are additive only (never removed)
- Protection banners are preserved
- Manual annotations outside guarded sections are preserved

### Migration Triggers

Documentation migration is triggered by:

| Trigger | Action |
|---------|--------|
| Template ID change | Full regeneration with new IDs |
| Profile change | Reconciliation with new profile requirements |
| Section requirement change | Patch update to affected documents |
| Workflow version change | Refresh with new step references |

## Conditional Standards

### Workflow-Generated Documents

Workflow-generated documents (marked with `managed_by: workflow-generated`):

- **SHALL NOT** be manually edited within guarded sections
- **SHALL** include protection banner after frontmatter
- **SHALL** use artifact key placeholders, never hardcoded paths
- **SHALL** be validated against section requirements
- **MAY** include manual annotations in designated unguarded sections

### Manually-Authored Documents

Manually-authored documents:

- **SHOULD** follow template structure where applicable
- **SHOULD** include frontmatter with `template_id` if part of system docs
- **MAY** omit protection banner
- **SHOULD** use artifact key references where possible
- **SHALL** pass validation if part of required document set

### Bootstrap Documents

Bootstrap documents (in `agent_runner_v2/bootstrap/bundles/`):

- **ARE** workflow-generated and protected
- **SERVE** as seed for `ukbe-run-agent init`
- **SHALL** be synced to runtime bundle after modification
- **SHALL NOT** be edited directly in runtime location

## Update Triggers

### Automatic Updates

Documents are automatically refreshed when:

1. Repository scan detects structural changes
2. Workflow step executes with document generation
3. Bundle migration requires template updates

### Manual Updates

Manual document updates follow the SOP:

1. Modify source prompt in `bootstrap/workflows/default/prompts/`
2. Re-run workflow step
3. Validate generated output
4. Submit via normal workflow

### Review Requirements

| Document Type | Review Required |
|---------------|---------------|
| SYSTEM_OVERVIEW | Stakeholder |
| BUSINESS_CAPABILITIES | Stakeholder |
| FUNCTIONAL_SPEC | Technical lead |
| NON_FUNCTIONAL_REQUIREMENTS | Technical lead |
| Architecture docs | Technical lead |

## Validation

### Validation Levels

| Level | Checks |
|-------|--------|
| **syntax** | Frontmatter parseable, required fields present |
| **structure** | Required sections present in correct order |
| **content** | Section content meets minimum requirements |
| **reference** | Artifact references resolve to known keys |

### Validation Execution

Validation is performed:

- During workflow step execution (blocking)
- During documentation sync (blocking)
- During bundle publication (blocking)
- On demand via `validate_system_docs.py` action

### Validation Failure Handling

| Failure Type | Action |
|--------------|--------|
| Syntax error | Reject document, require fix |
| Missing section | Reject document, require regeneration |
| Content insufficient | Flag for review, allow override |
| Unresolved reference | Reject document, require fix |

### Protection Bypass

Manual editing of workflow-generated documents requires:

1. Explicit override flag in frontmatter
2. Approval from document owner (workflow or manual)
3. Change log entry documenting bypass reason
4. Validation waiver with justification

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 03_generate_system_overview_docs*
