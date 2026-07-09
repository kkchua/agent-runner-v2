---
template_id: "SYS-00-IDX"
title: "System Documentation Index - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Documentation Index

## System Documentation Index

This index provides a navigable entry point to the complete system documentation for the `agent-runner-v2` platform.

## Audience Views

### Stakeholder View
**Target Audience**: Business stakeholders, product managers, and decision-makers

**Key Documents**:
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform purpose, value proposition, and primary flows
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Operational capabilities and business value
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality attributes and operational expectations

### Developer View
**Target Audience**: Software engineers, integration developers, and technical contributors

**Key Documents**:
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional capabilities and system behaviors
- [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) — Documentation conventions and standards
- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Workflow bundle structure and organization
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Bundle versioning and migration strategy

### Operator View
**Target Audience**: DevOps engineers, system administrators, and operations staff

**Key Documents**:
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Runtime, quality, and operational requirements
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Operational migration procedures
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Architecture profile and key risks

### Functional Consumer View
**Target Audience**: Users of the workflow platform and workflow authors

**Key Documents**:
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Workflow model and primary flows
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional capabilities and workflow families
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — What the platform enables operationally

## Document Map

### Governance Documents

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) | SYS-00-PA | Repository analysis and architecture posture |
| [README.md](README.md) | SYS-00-IDX | This index document |
| [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) | SYS-00-DS | Baseline documentation rules and conventions |
| [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) | SYS-00-BT | Workflow bundle structure and organization |
| [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) | SYS-00-BMP | Bundle versioning and migration procedures |

### Overview Documents

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | SYS-00-SO | Platform overview, workflow model, value flow |
| [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) | SYS-00-BC | Operational capabilities and business value |
| [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) | SYS-00-FS | Functional behaviors and workflow capabilities |
| [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) | SYS-00-NFR | Quality and operational requirements |

### Architecture Documents

| Document | Template ID | Purpose |
|----------|-------------|---------|
| SYSTEM_CONTEXT.md | SYS-01-SC | External system interfaces and context |
| COMPONENT_ARCHITECTURE.md | SYS-01-CA | Component structure and interactions |
| DECISION_LOG.md | SYS-01-DL | Architecture decision records |
| SYSTEM_FILE_STRUCTURE.md | SYS-01-SFS | Repository file organization |

### Operations Documents

| Document | Template ID | Purpose |
|----------|-------------|---------|
| DEVELOPER_GUIDE.md | SYS-01-DG | Developer onboarding and contribution guide |
| RUNBOOK.md | SYS-01-RB | Operational procedures and troubleshooting |
| EXISTING_REPO_WORKFLOW_SOP.md | SYS-01-WRS | Workflow SOP for existing repositories |

## Documentation Conventions

### Frontmatter Contract

All system documents include YAML frontmatter with:

- `template_id`: Stable document identifier (e.g., `SYS-00-IDX`)
- `title`: Human-readable document title
- `status`: Document status (`active`, `draft`, `archived`)
- `generated`: ISO 8601 timestamp
- `workflow`: Generating workflow name
- `step`: Generating step name
- `change_id`: Change identifier
- `managed_by`: Set to `workflow-generated` for protected documents

### Protected Documents

Documents marked with `managed_by: workflow-generated` are automatically generated and protected from manual edits. Changes must be made through the generating workflow's prompt templates.

### Versioning

System documents follow the bundle change ID for versioning. Each regeneration creates a new change ID, preserving historical snapshots in the change log.

## Navigation Quick Reference

```
docs/system/
├── 00_governance/bootstrap/
│   ├── README.md                    # This index (SYS-00-IDX)
│   ├── PROJECT_ANALYSIS.md          # Repository analysis (SYS-00-PA)
│   ├── DOCUMENTATION_STANDARD.md    # Doc standards (SYS-00-DS)
│   ├── BUNDLE_TAXONOMY.md           # Bundle structure (SYS-00-BT)
│   ├── BUNDLE_MIGRATION_PLAN.md     # Migration plan (SYS-00-BMP)
│   ├── SYSTEM_OVERVIEW.md           # Platform overview (SYS-00-SO)
│   ├── BUSINESS_CAPABILITIES.md     # Business capabilities (SYS-00-BC)
│   ├── FUNCTIONAL_SPEC.md           # Functional spec (SYS-00-FS)
│   ├── NON_FUNCTIONAL_REQUIREMENTS.md # Quality requirements (SYS-00-NFR)
│   ├── SYSTEM_CONTEXT.md            # System context (SYS-01-SC)
│   ├── COMPONENT_ARCHITECTURE.md    # Component architecture (SYS-01-CA)
│   ├── DECISION_LOG.md              # Decision records (SYS-01-DL)
│   ├── SYSTEM_FILE_STRUCTURE.md     # File structure (SYS-01-SFS)
│   ├── DEVELOPER_GUIDE.md           # Developer guide (SYS-01-DG)
│   ├── RUNBOOK.md                   # Operations runbook (SYS-01-RB)
│   └── EXISTING_REPO_WORKFLOW_SOP.md # Workflow SOP (SYS-01-WRS)
```

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
