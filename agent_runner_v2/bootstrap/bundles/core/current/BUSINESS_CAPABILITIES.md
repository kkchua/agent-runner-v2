---
title: "Business Capabilities"
template_id: "SYS-00-BC"
status: "active"
generated: "2026-07-10T11:45:32+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-15f76235"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities

## Capability Map

The agent-runner-v2 platform enables 10 core business capabilities organized by operational domain:

| ID | Capability | Domain | Maturity |
|----|------------|--------|----------|
| BC-01 | Initiative Intake | Delivery | Active |
| BC-02 | Delivery Planning | Delivery | Active |
| BC-03 | Task Execution | Delivery | Active |
| BC-04 | Documentation Governance | Governance | Active |
| BC-05 | Delivery Scaffold | Governance | Active |
| BC-06 | Bug Triage & Fix | Operations | Active |
| BC-07 | Media Content Generation | Content | Active |
| BC-08 | Multi-Model Orchestration | Platform | Active |
| BC-09 | Distributed Worker Execution | Platform | Active |
| BC-10 | Operational Supervision | Operations | Active |

## Capability Details

### BC-01: Initiative Intake

**Description**: Capture, refine, and validate initiative proposals before committing to delivery.

**Business Value**:
- Reduces waste from poorly-defined initiatives
- Ensures requirements clarity before planning
- Provides decision support for initiative approval

**Workflows**:
- `20_initiative_intake_v1` — Initiative intake and pre-init refinement

**Key Artifacts**:
- `DRAFT_INIT_FILE` — Initial draft capture
- `PRE_INIT_FILE` — Pre-initiative refinement
- `INIT_FILE` — Approved initiative document

**Stakeholders**: Product managers, technical leads, initiative sponsors

---

### BC-02: Delivery Planning

**Description**: Transform approved initiatives into structured delivery plans with task graphs and contracts.

**Business Value**:
- Provides clear delivery roadmap
- Decomposes work into manageable tasks
- Establishes task contracts with acceptance criteria

**Workflows**:
- `30_delivery_planning_v1` — Plan generation, task-graph generation, task contract generation

**Key Artifacts**:
- `PLAN_FILE` — Delivery plan document
- `TASK_GRAPH_FILE` — Task dependency graph
- `TASK_FILE` — Individual task contracts

**Stakeholders**: Delivery managers, tech leads, developers

---

### BC-03: Task Execution

**Description**: Execute planned tasks with implementation, review, documentation sync, and validation.

**Business Value**:
- Ensures quality through review loops
- Maintains documentation alongside code
- Validates deliverables against acceptance criteria

**Workflows**:
- `31_task_execution_v1` — Implementation planning, review, execution, documentation sync, validation

**Key Artifacts**:
- `IMPL_FILE` — Implementation plan
- `REVIEW_FILE` — Review findings
- `VALIDATION_FILE` — Validation results

**Stakeholders**: Developers, QA engineers, technical writers

---

### BC-04: Documentation Governance

**Description**: Maintain documentation quality through reconciliation, validation, and synchronization workflows.

**Business Value**:
- Prevents documentation drift from code
- Ensures documentation completeness
- Validates document structure and cross-references

**Workflows**:
- `40_documentation_sync_v1` — Documentation reconciliation and validation
- `41_audience_doc_v1` / `50_architecture_site_v1` — Multi-audience documentation

**Key Artifacts**:
- `CODEBASE_INVENTORY` — Module inventory
- `CODEBASE_CHANGE_IMPACT` — Change impact analysis
- `DELIVERY_STATUS_RULES` — Documentation status rules

**Stakeholders**: Technical writers, developers, architects

---

### BC-05: Delivery Scaffold

**Description**: Bootstrap new repositories with complete governance documentation, templates, and agent contracts.

**Business Value**:
- Accelerates new project setup
- Establishes documentation standards early
- Provides reusable governance patterns

**Workflows**:
- `10_execution_scaffold_v1` — Scaffolds docs/delivery/ and docs/codebase/ governance

**Key Artifacts**:
- `DELIVERY_SOP` — Delivery standard operating procedure
- `DELIVERY_TEMPLATE_REGISTRY` — Template registry
- `DELIVERY_AGENTS_MD` — Agent contracts

**Stakeholders**: Technical leads, project initiators, architects

---

### BC-06: Bug Triage & Fix

**Description**: Systematic bug triage, reproduction, root cause analysis, patching, and regression validation.

**Business Value**:
- Reduces time to resolution
- Ensures proper fix validation
- Prevents regression through structured testing

**Workflows**:
- `21_bug_fix_intake_v1` — Bug triage, reproduction, root cause, patching, regression validation

**Key Artifacts**:
- `BUG_DRAFT_FILE` — Bug triage document
- `REPRO_FILE` — Reproduction steps
- `PATCH_FILE` — Fix implementation
- `REGRESSION_FILE` — Validation results

**Stakeholders**: Support engineers, developers, QA

---

### BC-07: Media Content Generation

**Description**: Automated media generation pipelines including image generation, video assembly, and voiceover.

**Business Value**:
- Scales content production
- Maintains consistency across assets
- Reduces manual media creation effort

**Workflows**:
- `image_csv_gen_v1/v2` — Image prompt generation from CSV
- `tiktok_video_pipeline_v1` — TikTok video production pipeline
- `videoxpress_gen_v1` — Video express generation

**Key Artifacts**:
- Image prompts CSV
- Video workflow definitions
- Assembled media files

**Stakeholders**: Content creators, marketing teams, media producers

---

### BC-08: Multi-Model Orchestration

**Description**: Orchestrate LLM workflows across multiple providers (Claude, Codex, Qwen) with model-specific optimizations.

**Business Value**:
- Uses best model for each task
- Provides redundancy and flexibility
- Optimizes cost/performance

**Features**:
- Model-specific prompt templates
- Automatic model selection
- Fallback handling

**Stakeholders**: Platform engineers, workflow designers

---

### BC-09: Distributed Worker Execution

**Description**: Execute workflows through backend-connected workers with queue-based work distribution.

**Business Value**:
- Scales execution across workstations
- Centralizes work coordination
- Provides execution visibility

**Modes**:
- `worker` — Continuous worker loop
- `poll` — One-shot poll mode
- `daemon` — Workstation supervisor

**Stakeholders**: Operations teams, platform administrators

---

### BC-10: Operational Supervision

**Description**: Monitor, supervise, and maintain workflow execution with daemon-based workstation management.

**Business Value**:
- Provides operational visibility
- Enables hands-off execution
- Facilitates troubleshooting

**Features**:
- Heartbeat monitoring
- Log aggregation
- Child process supervision

**Stakeholders**: Operations engineers, support staff

## Capability Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                    BC-05: Delivery Scaffold                 │
│                    (Foundation Capability)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  BC-01:       │   │  BC-04:       │   │  BC-06:       │
│ Initiative    │   │ Documentation │   │ Bug Triage    │
│ Intake        │   │ Governance    │   │               │
└───────┬───────┘   └───────────────┘   └───────────────┘
        │
        ▼
┌───────────────┐
│  BC-02:       │
│ Delivery      │
│ Planning      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  BC-03:       │
│ Task          │
│ Execution     │
└───────────────┘
        │
        ▼
┌───────────────┐
│  BC-07:       │
│ Media Content │
│ Generation    │
└───────────────┘

Supporting Platform Capabilities:
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  BC-08:       │   │  BC-09:       │   │  BC-10:       │
│ Multi-Model   │   │ Distributed   │   │ Operational   │
│ Orchestration │   │ Worker        │   │ Supervision   │
│               │   │ Execution     │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Capability Maturity Levels

| Level | Description | Criteria |
|-------|-------------|----------|
| **Experimental** | New capability, limited use | Workflow exists, minimal validation |
| **Active** | Production use, stable | Proven in production, documented |
| **Mature** | Widely adopted, optimized | Multiple teams using, metrics collected |
| **Legacy** | Being superseded | Replacement capability exists |

### Current Maturity Assessment

| Capability | Current | Target | Notes |
|------------|---------|--------|-------|
| Initiative Intake | Active | Mature | Core delivery workflow |
| Delivery Planning | Active | Mature | Core delivery workflow |
| Task Execution | Active | Mature | Core delivery workflow |
| Documentation Governance | Active | Mature | Active sync workflows |
| Delivery Scaffold | Active | Mature | Bootstrap capability |
| Bug Triage | Active | Active | Recently added |
| Media Content | Active | Active | Specialized use |
| Multi-Model Orchestration | Active | Mature | Core platform feature |
| Distributed Worker | Active | Mature | Production deployment |
| Operational Supervision | Active | Mature | Production deployment |

## Operational Interpretation

### For Stakeholders

**What this means for the business**:
- Faster initiative turnaround through structured intake
- Higher quality deliverables through review loops
- Reduced documentation debt through governance
- Scalable content production through automation

### For Developers

**What this means for engineering**:
- Clear task contracts with acceptance criteria
- Automated documentation synchronization
- Multi-model flexibility for different tasks
- Deterministic actions for reliable operations

### For Operators

**What this means for operations**:
- Centralized work distribution via backend
- Daemon-based workstation supervision
- Comprehensive logging and monitoring
- Clear troubleshooting procedures

### For Governance

**What this means for compliance**:
- Structured documentation standards
- Change impact tracking
- Audit trail through job state
- Validation gates for quality

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform overview
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional requirements
- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Workflow definitions
