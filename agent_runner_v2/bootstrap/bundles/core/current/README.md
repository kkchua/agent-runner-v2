---
template_id: "SYS-00-IDX"
title: "System Documentation Index"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Documentation Index

## System Documentation Index

This directory contains the master system documentation for the `agent-runner-v2` workflow orchestration platform. These documents establish the authoritative reference for platform capabilities, operational standards, and architectural posture.

## Audience Views

The system documentation set is organized to serve distinct reader perspectives:

| Audience | Primary Documents | Purpose |
|----------|-------------------|---------|
| **Stakeholders** | `SYSTEM_OVERVIEW.md`, `BUSINESS_CAPABILITIES.md` | High-level platform value, capabilities, and operational impact |
| **Developers** | `FUNCTIONAL_SPEC.md`, `DEVELOPER_GUIDE.md`, `SYSTEM_FILE_STRUCTURE.md` | Implementation details, extension points, and development workflows |
| **Operators** | `RUNBOOK.md`, `NON_FUNCTIONAL_REQUIREMENTS.md` | Deployment, monitoring, and incident response procedures |
| **Integrators** | `BUNDLE_TAXONOMY.md`, `EXISTING_REPO_WORKFLOW_SOP.md` | Workflow bundle structure and integration patterns |
| **Governance** | `DOCUMENTATION_STANDARD.md`, `DECISION_LOG.md` | Standards, decisions, and compliance requirements |

## Document Map

### Governance and Standards

| Document | Template ID | Purpose |
|----------|-------------|---------|
| `README.md` | SYS-00-IDX | This index document |
| `DOCUMENTATION_STANDARD.md` | SYS-00-DS | Documentation baseline rules and repo-specific profiles |
| `BUNDLE_TAXONOMY.md` | SYS-00-BT | Workflow bundle structure and artifact classification |
| `BUNDLE_MIGRATION_PLAN.md` | SYS-00-BMP | Migration strategy for bundle and documentation evolution |

### Overview and Capabilities

| Document | Template ID | Purpose |
|----------|-------------|---------|
| `SYSTEM_OVERVIEW.md` | SYS-00-SO | Platform purpose, flows, and architecture profile |
| `BUSINESS_CAPABILITIES.md` | SYS-00-BC | Operational capabilities enabled by the platform |
| `FUNCTIONAL_SPEC.md` | SYS-00-FS | Functional behaviors, actors, and core system behaviors |
| `NON_FUNCTIONAL_REQUIREMENTS.md` | SYS-00-NFR | Quality attributes and operational requirements |

### Architecture and Engineering

| Document | Template ID | Purpose |
|----------|-------------|---------|
| `SYSTEM_CONTEXT.md` | SYS-01-SC | System context and external boundaries |
| `COMPONENT_ARCHITECTURE.md` | SYS-01-CA | Component relationships and interfaces |
| `DECISION_LOG.md` | SYS-01-DL | Architectural decision records |
| `SYSTEM_FILE_STRUCTURE.md` | SYS-01-SFS | File organization and directory rationale |

### Operations and Development

| Document | Template ID | Purpose |
|----------|-------------|---------|
| `DEVELOPER_GUIDE.md` | SYS-02-DG | Development setup and contribution workflows |
| `RUNBOOK.md` | SYS-02-RB | Operational procedures and incident response |
| `EXISTING_REPO_WORKFLOW_SOP.md` | SYS-02-SOP | Workflow SOP for existing repository integration |

## Reading Order

For first-time readers, the recommended progression:

1. **Start here** (`README.md`) — Understand the document structure
2. **System Overview** (`SYSTEM_OVERVIEW.md`) — Grasp the platform purpose and value
3. **Business Capabilities** (`BUSINESS_CAPABILITIES.md`) — Learn what the platform enables
4. **Functional Spec** (`FUNCTIONAL_SPEC.md`) — Understand detailed behaviors
5. **Documentation Standard** (`DOCUMENTATION_STANDARD.md`) — Understand governance rules

Architecture and operations documents may be consulted as needed based on role.

## Document Status

| Document | Status | Generated |
|----------|--------|-----------|
| All bootstrap documents | `active` | 2026-07-04 |

---

*This index is maintained by the `00_master_docs_bootstrap_v1` workflow. Updates outside the workflow are subject to reconciliation.*
