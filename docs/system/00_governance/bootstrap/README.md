---
template_id: "SYS-00-IDX"
title: "System Documentation Index - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Documentation Index: agent-runner-v2

## System Documentation Index

This index provides a navigational entry point to the complete system documentation set for the agent-runner-v2 platform. The documentation is organized by audience and purpose to serve stakeholders, developers, operators, testers, and end users with appropriately scoped information.

## Audience Views

### For Stakeholders
Stakeholders need high-level understanding of business value, capabilities, and governance posture without implementation detail.

**Start here:**
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform purpose, value flow, and architecture profile
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — What the runner enables operationally
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality and operational expectations

### For Developers
Developers need architectural detail, integration patterns, and implementation guidance.

**Start here:**
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — System boundaries and primary flows
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Core behaviors and workflow capabilities
- [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) — Documentation conventions and standards
- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Workflow bundle organization
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Migration posture and roadmap

### For Operators
Operators need runtime behavior, deployment patterns, and operational procedures.

**Start here:**
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Runtime modes and operational model
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Runtime expectations and constraints
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Deployment considerations

### For Governance
Governance needs standards, conventions, and validation rules.

**Start here:**
- [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) — Baseline rules and repo profiles
- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Bundle structure and conventions

## Document Map

### Core System Documents

| Document | Template ID | Purpose | Primary Audience |
|----------|---------------|---------|------------------|
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | SYS-00-SO | Platform explanation and value flow | All |
| [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) | SYS-00-BC | Operational capabilities | Stakeholders, Operators |
| [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) | SYS-00-FS | Core behaviors and capabilities | Developers |
| [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) | SYS-00-NFR | Quality and operational requirements | Developers, Operators |
| [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) | SYS-00-DS | Documentation conventions | All |

### Bundle and Migration Documents

| Document | Template ID | Purpose | Primary Audience |
|----------|---------------|---------|------------------|
| [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) | SYS-00-BT | Workflow bundle organization | Developers |
| [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) | SYS-00-BMP | Migration posture and roadmap | Developers, Operators |

### Architecture Documents (Separate Set)

The following documents are generated in a separate workflow step and provide deeper architectural detail:

| Document | Template ID | Purpose |
|----------|---------------|---------|
| [SYSTEM_CONTEXT.md](SYSTEM_CONTEXT.md) | SYS-00-SC | System boundaries and external interfaces |
| [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) | SYS-00-CA | Component structure and relationships |
| [DECISION_LOG.md](DECISION_LOG.md) | SYS-00-DL | Architectural decision records |
| [SYSTEM_FILE_STRUCTURE.md](SYSTEM_FILE_STRUCTURE.md) | SYS-00-SFS | Repository organization |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | SYS-00-DG | Implementation guidance |
| [RUNBOOK.md](RUNBOOK.md) | SYS-00-RB | Operational procedures |
| [EXISTING_REPO_WORKFLOW_SOP.md](EXISTING_REPO_WORKFLOW_SOP.md) | SYS-00-SOP | Workflow SOP for this repo |

## Navigation Conventions

- **Cross-references** use relative paths from this directory
- **Template IDs** are stable identifiers for document validation
- **Status badges** indicate document lifecycle state
- **Change IDs** link documents to generation events

## Repository Context

This documentation set applies to the `agent-runner-v2` repository:

- **Repository**: `agent-runner-v2`
- **Current Profile**: `provisional`
- **Target Profile**: `explicit`
- **Migration Mode**: `in_progress`

See [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) for architecture posture details.

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
