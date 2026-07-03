---
template_id: "SYS-00-IDX"
title: "System Documentation Index - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Documentation Index

This index maps the master system documentation for `agent-runner-v2` — a standalone Python LLM workflow orchestration engine.

## System Documentation Index

The master documentation set provides a comprehensive view of the platform, its capabilities, and operational boundaries.

### Quick Navigation

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [README.md](README.md) | SYS-00-IDX | This index — entry point to system docs |
| [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) | SYS-00-DS | Baseline rules and repo-specific documentation profiles |
| [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) | SYS-00-BT | Canonical bundle organization for runtime workflow bundles |
| [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) | SYS-00-BMP | Migration path for bundle format evolution |
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | SYS-00-SO | Platform purpose, workflow model, and value flow |
| [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) | SYS-00-BC | Operational capabilities the runner enables |
| [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) | SYS-00-FS | Functional behaviors and workflow capabilities |
| [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) | SYS-00-NFR | Quality and operational expectations |

## Audience Views

Documentation is organized by audience to help readers find relevant information quickly.

### For Users (Workflow Operators)

Start here if you run workflows:

1. [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Understand what the platform does
2. [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Learn what workflows can accomplish
3. [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Understand runtime expectations

Reference:
- [EXISTING_REPO_WORKFLOW_SOP.md](EXISTING_REPO_WORKFLOW_SOP.md) — Operating procedures for this repository
- [RUNBOOK.md](RUNBOOK.md) — Operational procedures and troubleshooting

### For Developers (Contributors and Extenders)

Start here if you modify or extend the runner:

1. [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Architecture profile and primary flows
2. [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — System behaviors and actor interactions
3. [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) — Detailed component design
4. [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) — Setup, development workflow, contribution guidelines

Reference:
- [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) — Documentation requirements
- [SYSTEM_FILE_STRUCTURE.md](SYSTEM_FILE_STRUCTURE.md) — Repository organization
- [DECISION_LOG.md](DECISION_LOG.md) — Architectural decisions and rationale

### For Stakeholders (Decision Makers)

Start here if you evaluate or plan around the platform:

1. [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform scope and value proposition
2. [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Operational capabilities
3. [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Reliability, performance, and security posture

Reference:
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Future evolution path

## Document Map

### Governance Documents (this directory)

| File | Template ID | Description |
|------|-------------|-------------|
| README.md | SYS-00-IDX | System documentation index and entry point |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Documentation baseline rules and profiles |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle organization taxonomy |
| BUNDLE_MIGRATION_PLAN.md | SYS-00-BMP | Bundle format migration plan |
| SYSTEM_OVERVIEW.md | SYS-00-SO | System purpose, scope, and flows |
| BUSINESS_CAPABILITIES.md | SYS-00-BC | Business capability mapping |
| FUNCTIONAL_SPEC.md | SYS-00-FS | Functional specification |
| NON_FUNCTIONAL_REQUIREMENTS.md | SYS-00-NFR | Non-functional requirements |
| SYSTEM_CONTEXT.md | SYS-00-SC | System context and boundaries |
| COMPONENT_ARCHITECTURE.md | SYS-00-CA | Component architecture details |
| DECISION_LOG.md | SYS-00-DL | Architectural decision records |
| SYSTEM_FILE_STRUCTURE.md | SYS-00-SFS | Repository file structure |
| DEVELOPER_GUIDE.md | SYS-00-DG | Developer setup and contribution guide |
| RUNBOOK.md | SYS-00-RB | Operational runbook |
| EXISTING_REPO_WORKFLOW_SOP.md | SYS-00-SOP | Repository-specific workflow SOP |

### Supporting Documentation

| Location | Content |
|----------|---------|
| `docs/codebase/` | Codebase documentation (inventory, modules, components, changes) |
| `docs/operations/` | Operational manuals (daemon mode, worker supervision) |
| `README.md` (repo root) | Quick start and usage overview |
| `HOW_TO_GUIDE.md` | Delivery scaffold workflow guide |

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
