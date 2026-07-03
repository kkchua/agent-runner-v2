---
template_id: "SYS-00-DS"
title: "Documentation Standard - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation baseline rules that apply to every repository using the agent-runner-v2 platform. It establishes the minimum viable documentation set, content expectations, and the mechanism for selecting repo-specific profiles and migration modes.

**Why:** Documentation drift is a major source of operational friction. A consistent baseline ensures stakeholders can always find critical information, while flexible profiles allow repositories to adapt to their domain needs.

## Audience Model

| Audience | Needs | Primary Documents |
|----------|-------|-------------------|
| **Users** | Run workflows, interpret results | System Overview, Functional Spec, Runbook |
| **Developers** | Extend, debug, contribute | Developer Guide, Component Architecture, Decision Log |
| **Stakeholders** | Evaluate, plan, govern | Business Capabilities, System Overview, NFRs |

## Document Set

### Universal Baseline (Required Everywhere)

Every repository must maintain:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| System Documentation Index | SYS-00-IDX | Entry point and navigation |
| Documentation Standard | SYS-00-DS | This document — rules and profiles |
| Bundle Taxonomy | SYS-00-BT | Runtime bundle organization |
| System Overview | SYS-00-SO | Purpose, scope, and value flow |

### Architecture Baseline (Required for `standard` profile)

Repositories targeting the `standard` architecture profile must additionally maintain:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| System Context | SYS-00-SC | Context and boundaries |
| Component Architecture | SYS-00-CA | Component design |
| Decision Log | SYS-00-DL | ADRs and rationale |
| System File Structure | SYS-00-SFS | Repository organization |
| Developer Guide | SYS-00-DG | Setup and contribution |
| Runbook | SYS-00-RB | Operations and troubleshooting |

### Functional Baseline (Required for active delivery)

Repositories with active delivery workflows must maintain:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| Business Capabilities | SYS-00-BC | Capability mapping |
| Functional Specification | SYS-00-FS | Behaviors and capabilities |
| Non-Functional Requirements | SYS-00-NFR | Quality and operational expectations |

## Architecture Baseline

### Universal Baseline

The universal baseline applies to **all** repositories, regardless of profile or state:

1. **Documentation Index (SYS-00-IDX)** — Must exist and be accurate
2. **Documentation Standard (SYS-00-DS)** — Must define current profile and migration mode
3. **Bundle Taxonomy (SYS-00-BT)** — Must describe runtime bundle organization
4. **System Overview (SYS-00-SO)** — Must explain platform purpose and scope

**Rationale:** Even minimal repositories need navigation, rules, bundle structure, and purpose documentation. These four documents provide the minimum viable system documentation.

### Profile-Specific Requirements

| Profile | Additional Required Documents |
|---------|------------------------------|
| `minimal` | None (universal baseline only) |
| `standard` | SYS-00-SC, SYS-00-CA, SYS-00-DL, SYS-00-SFS, SYS-00-DG, SYS-00-RB |
| `comprehensive` | All `standard` docs plus domain-specific extensions |

## Repo-Selected Profile

### Current Profile

| Attribute | Value |
|-----------|-------|
| **Repository** | agent-runner-v2 |
| **Current Profile** | `standard` |
| **Target Profile** | `standard` |
| **Migration Mode** | `in_progress` |

### Profile Selection Rationale

The `agent-runner-v2` repository selects the `standard` profile because:

1. **Mature codebase** — 40+ modules with clear architectural patterns
2. **Multi-stakeholder** — Users, developers, and operators interact with the system
3. **Production usage** — Backend-connected worker and daemon modes require operational documentation
4. **Extensible design** — Action system and workflow families invite contribution

### Profile Components

This repository maintains the full standard profile:

- **Core system docs**: Index, Standard, Taxonomy, Overview, Capabilities, Functional Spec, NFRs
- **Architecture docs**: Context, Component Architecture, Decision Log, File Structure
- **Operational docs**: Developer Guide, Runbook, Repository SOP

## Migration Mode

### Current Mode: `in_progress`

The repository is actively generating its documentation baseline. This mode indicates:

- Documentation is being created by the bootstrap workflow
- Some documents may be stubs or incomplete
- Updates are expected as the codebase evolves

### Mode Transitions

| From | To | Trigger |
|------|-----|---------|
| `in_progress` | `active` | Bootstrap complete, all docs validated |
| `active` | `drift_detected` | Validation finds stale or missing docs |
| `drift_detected` | `in_progress` | Documentation sync workflow initiated |
| `any` | `archived` | Repository deprecated |

### Migration Posture

When the repository standard is provisional (during bootstrap), the following applies:

1. **Docs are workflow-generated** — Manual edits are blocked by guardrails
2. **Validation is advisory** — Failures don't block development
3. **Updates are batched** — Changes accumulate until explicit sync
4. **Approval required** — Final transition to `active` requires human approval

## Conditional Standards

### For Workflow Bundles

Workflow bundles under `agent_runner_v2/bootstrap/workflows/default/` must maintain:

1. **template_groups.py** — Workflow definitions and step configurations
2. **JSON schemas** — job_schema.json, llm_response_schema.json, usage_schema.json
3. **Prompt templates** — One .txt file per step under `prompts/<workflow>/`

### For Packaged Code

Python modules under `agent_runner_v2/` must maintain:

1. **Module docstrings** — Purpose and responsibility
2. **Type hints** — Function signatures and return types
3. **Runtime context** — Integration with `runtime_context.py`

### For Documentation

All markdown files must include:

1. **YAML frontmatter** — template_id, status, generated timestamp
2. **Workflow banner** — Managed by workflow notice
3. **Version tracking** — Change ID for traceability

## Update Triggers

Documentation must be refreshed when:

| Trigger | Documents Affected |
|---------|-------------------|
| Code change impacting public API | Functional Spec, Developer Guide |
| New workflow family added | Bundle Taxonomy, Functional Spec |
| Architecture decision | Decision Log, Component Architecture |
| Operational procedure change | Runbook, Repository SOP |
| Bundle format change | Bundle Taxonomy, Bundle Migration Plan |
| Release cut | System Overview, Business Capabilities |

## Validation

### Automated Checks

The following validations run automatically:

1. **Frontmatter validation** — All required fields present
2. **Template ID uniqueness** — No duplicate template IDs
3. **Cross-reference integrity** — Links to other docs resolve
4. **Schema compliance** — JSON sidecars match schemas

### Manual Reviews

The following require human review:

1. **Content accuracy** — Technical correctness
2. **Completeness** — All topics covered
3. **Clarity** — Appropriate for target audience
4. **Consistency** — Terminology and style

### Validation Results

Validation results are recorded in:

- `docs/system/00_governance/bootstrap/00DOC-GEN-<id>-bootstrap-validation.md`
- `docs/codebase/04_changes/00DOC-GEN-<id>-bootstrap.md`

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
