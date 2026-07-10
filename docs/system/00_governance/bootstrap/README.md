---
template_id: "SYS-00-IDX"
title: "System Documentation Index"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Documentation Index

## Overview

This directory contains the authoritative system documentation for the `agent-runner-v2` repository. These documents establish the platform's purpose, capabilities, operational model, and documentation standards.

## System Documentation Purpose

The system documentation serves three primary purposes:

1. **Stakeholder Orientation** — Explain what the platform does and why it exists
2. **Developer Guidance** — Describe the functional scope and expected behaviors
3. **Operational Reference** — Document runtime characteristics and quality expectations

## Audience Views

| Audience | Primary Documents | Key Questions Answered |
|----------|-----------------|------------------------|
| **Stakeholders** | SYSTEM_OVERVIEW, BUSINESS_CAPABILITIES | What is this? What does it enable? Why invest? |
| **Developers** | FUNCTIONAL_SPEC, NON_FUNCTIONAL_REQUIREMENTS | What does it do? How should it behave? |
| **Operators** | NON_FUNCTIONAL_REQUIREMENTS, SYSTEM_OVERVIEW | How does it run? What are the constraints? |
| **New Contributors** | DOCUMENTATION_STANDARD, SYSTEM_OVERVIEW | How do we document here? What are the conventions? |

## Document Map

### Governance and Standards

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [README.md](README.md) | SYS-00-IDX | This index — entry point to system documentation |
| [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) | SYS-00-DS | Documentation baseline rules and repo-specific profiles |
| [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) | SYS-00-BT | Classification of documentation bundles and their relationships |
| [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) | SYS-00-BMP | Migration strategy for documentation bundle transitions |

### Platform Overview

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | SYS-00-SO | Platform purpose, workflow model, and value flow |
| [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) | SYS-00-BC | Operational capabilities the runner enables |
| [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) | SYS-00-FS | Major behaviors and workflow capabilities |
| [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) | SYS-00-NFR | Runtime, quality, and operational expectations |

### Architecture and Operations

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [SYSTEM_CONTEXT.md](SYSTEM_CONTEXT.md) | SYS-00-SC | External systems, boundaries, and interfaces |
| [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) | SYS-00-CA | Component breakdown and interaction patterns |
| [DECISION_LOG.md](DECISION_LOG.md) | SYS-00-DL | Key architectural and design decisions |
| [SYSTEM_FILE_STRUCTURE.md](SYSTEM_FILE_STRUCTURE.md) | SYS-00-SFS | Repository organization conventions |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | SYS-00-DG | Development setup and contribution guidelines |
| [RUNBOOK.md](RUNBOOK.md) | SYS-00-RB | Operational procedures and troubleshooting |

### Project Analysis

| Document | Template ID | Purpose |
|----------|-------------|---------|
| [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) | SYS-00-PA | Repository structure, risks, and architecture posture |

## Reading Order

For **first-time readers**, follow this sequence:

1. **SYSTEM_OVERVIEW.md** — Understand what the platform is and does
2. **BUSINESS_CAPABILITIES.md** — Grasp the operational value
3. **FUNCTIONAL_SPEC.md** — Learn the functional scope
4. **DOCUMENTATION_STANDARD.md** — Know how to read and contribute to docs

For **developers joining the project**:

1. **SYSTEM_OVERVIEW.md** — Platform fundamentals
2. **DOCUMENTATION_STANDARD.md** — Documentation conventions
3. **FUNCTIONAL_SPEC.md** — Expected behaviors
4. **NON_FUNCTIONAL_REQUIREMENTS.md** — Quality expectations
5. **DEVELOPER_GUIDE.md** — Development setup

For **operators**:

1. **SYSTEM_OVERVIEW.md** — Platform architecture
2. **NON_FUNCTIONAL_REQUIREMENTS.md** — Runtime expectations
3. **RUNBOOK.md** — Operational procedures

## Document Status

All documents in this directory are **workflow-generated** and protected from manual edits. Changes must be made through the appropriate workflow steps:

- **System overview documents**: `00_master_docs_bootstrap_v2` workflow
- **Codebase documentation**: `40_documentation_sync_v1` workflow
- **Delivery documentation**: `10_execution_scaffold_v1` workflow

## Change Tracking

| Change ID | Date | Description |
|-----------|------|-------------|
| 00DOC-GEN-20260710-004 | 2026-07-10 | Initial system documentation bootstrap |

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
