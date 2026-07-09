---
template_id: "SYS-00-BC"
managed_by: workflow-generated
generated: "2026-07-09T21:18:02+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities

## Purpose

This document describes the operational capabilities enabled by agent-runner-v2. It explains what the platform enables organizations to do, how it creates value, and the business outcomes it supports.

agent-runner-v2 transforms ad-hoc AI assistance into structured, repeatable, auditable workflows that can be delegated, scaled, and integrated with existing systems.

## Capability Map

### Workflow Orchestration

| Capability | Description | Business Value |
|------------|-------------|----------------|
| **Structured Multi-Step Execution** | Break complex work into discrete, reviewable steps | Risk reduction, quality assurance |
| **State Persistence** | Maintain job state across steps and sessions | Resumable work, audit trail |
| **Review Loops** | Built-in approve/reject/refine cycles | Quality gates, human oversight |
| **Retry Logic** | Automatic retry with backoff and limits | Resilience, reduced manual intervention |
| **Approval Gates** | Explicit human checkpoints | Compliance, safety |

### Coder Integration

| Capability | Description | Business Value |
|------------|-------------|----------------|
| **Multi-Model Support** | Claude, Codex, Qwen, aliased models | Model selection, cost optimization |
| **Unified Interface** | Single interface for multiple coders | Simplified operations, reduced training |
| **Coder Adapters** | Abstraction layer for coder invocation | Swappable implementations, resilience |
| **Timeout Management** | Cascading timeout configuration | Resource management, predictable execution |

### Deterministic Actions

| Capability | Description | Business Value |
|------------|-------------|----------------|
| **Action Library** | 29+ built-in deterministic actions | Repeatable operations, reduced variance |
| **Documentation Actions** | Validation, sync, generation | Documentation accuracy, consistency |
| **Architecture Actions** | Site generation, PDF export | Stakeholder communication |
| **Media Actions** | T2I, I2V, voiceover, assembly | Content generation workflows |
| **Custom Actions** | Extensible action framework | Domain-specific operations |

### Execution Modes

| Capability | Description | Business Value |
|------------|-------------|----------------|
| **Local Execution** | Manual workflow invocation | Development, debugging, one-off tasks |
| **Worker Mode** | Backend-driven step execution | Scalability, distribution |
| **Daemon Mode** | Workstation supervision | 24/7 operation, resource utilization |
| **Mixed Mode** | Combine local and backend | Flexibility, gradual adoption |

### Documentation Governance

| Capability | Description | Business Value |
|------------|-------------|----------------|
| **Generated Doc Protection** | Workflow-attributed, protected from manual edits | Source of truth, drift prevention |
| **Documentation Sync** | Reconcile docs with codebase | Accuracy, reduced staleness |
| **Template Registry** | Standardized document templates | Consistency, reduced setup time |
| **Validation** | Automated document validation | Quality gates, compliance |
| **Inventory Tracking** | Module/component documentation | Discoverability, maintenance |

### Delivery Lifecycle

| Capability | Description | Business Value |
|------------|-------------|----------------|
| **Initiative Intake** | Structured requirement capture | Clear requirements, reduced rework |
| **Delivery Planning** | Plan generation, task decomposition | Predictability, resource planning |
| **Task Execution** | Implementation with validation | Quality, traceability |
| **Documentation Sync** | Post-execution documentation update | Knowledge preservation |
| **Architecture Publishing** | Stakeholder-facing documentation | Communication, alignment |

## Operational Interpretation

### For Development Teams

**Challenge**: Inconsistent AI assistance, ad-hoc usage, quality variance

**Capability Applied:**

- **Structured Workflows**: Consistent approach to AI-assisted development
- **Review Loops**: Quality gates before code changes
- **State Persistence**: Resume long-running tasks
- **Documentation Sync**: Keep docs current with code

**Outcome**: Higher quality, more consistent results, reduced cognitive load

### For Operations Teams

**Challenge**: Managing AI workloads, ensuring availability, monitoring execution

**Capability Applied:**

- **Daemon Mode**: 24/7 operation without manual intervention
- **Worker Mode**: Scalable execution across workstations
- **Heartbeat Monitoring**: Operational visibility
- **Failure Handling**: Automatic retry and escalation

**Outcome**: Reliable operation, better resource utilization, reduced toil

### For Documentation Teams

**Challenge**: Documentation drift, inconsistent structure, manual updates

**Capability Applied:**

- **Generated Doc Protection**: Source of truth maintained by workflows
- **Template Registry**: Standardized document structure
- **Documentation Sync**: Automatic reconciliation
- **Validation**: Quality gates for documentation

**Outcome**: Accurate, consistent, current documentation

### For Stakeholders

**Challenge**: Understanding system state, tracking progress, communication gaps

**Capability Applied:**

- **Architecture Publishing**: Browsable HTML documentation
- **Delivery Tracking**: Initiative and task visibility
- **Decision Logs**: Architectural decision records
- **Business Capabilities**: Clear capability documentation

**Outcome**: Better alignment, reduced communication overhead, informed decisions

## Value Flow

### Input to Output

```
Requirements → Workflows → Steps → Execution → Artifacts → Review → Value
```

**Value Creation at Each Stage:**

| Stage | Input | Output | Value Created |
|-------|-------|--------|---------------|
| Requirements | Raw ideas, problems, opportunities | Structured initiatives | Clarity, scope definition |
| Workflows | Initiatives | Executable plans | Actionability, predictability |
| Steps | Plans | Executed work | Progress, tangible output |
| Execution | Work definitions | Code, docs, decisions | Deliverables, knowledge |
| Artifacts | Raw output | Validated documents | Quality, trustworthiness |
| Review | Completed work | Approved/refined output | Assurance, improvement |

### Cost Reduction

| Area | Before | After |
|------|--------|-------|
| **Documentation** | Manual, drift-prone | Automated, synchronized |
| **Quality Gates** | Ad-hoc, inconsistent | Structured, repeatable |
| **Knowledge Transfer** | Tribal knowledge | Documented, discoverable |
| **Onboarding** | High variance, slow | Standardized, faster |

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Quality Variance** | Review loops, validation |
| **Knowledge Loss** | State persistence, documentation |
| **Audit Requirements** | Complete execution history |
| **Compliance** | Approval gates, structured workflows |

## Integration Points

### External Systems

| System | Integration | Capability |
|--------|-------------|------------|
| **Backend API** | REST API | Work claiming, result submission |
| **Claude Code** | CLI invocation | Coder execution |
| **Codex CLI** | CLI invocation | Coder execution |
| **Qwen Code** | CLI invocation | Coder execution |
| **ComfyUI** | HTTP API | Media generation |
| **Pushover** | HTTP API | Notifications |

### File System

| Location | Purpose |
|----------|---------|
| `%USERPROFILE%\.ukbe-runner\` | Global runner home |
| `%USERPROFILE%\.ukbe-runner\jobs\` | Job state persistence |
| `%USERPROFILE%\.ukbe-runner\workflows\` | Runtime workflow bundles |
| `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

## Success Metrics

### Operational Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Workflow Success Rate** | >95% | Completed vs started |
| **Step Retry Rate** | <10% | Retries vs total steps |
| **Documentation Accuracy** | >90% | Validation pass rate |
| **Job Completion Time** | Baseline +20% | End-to-end time |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Documentation Currency** | >95% | Sync freshness |
| **Review Cycle Time** | <2 days | Time to approval |
| **Onboarding Time** | -50% | Time to productivity |
| **Knowledge Discovery** | <5 min | Time to find docs |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 03_generate_system_overview_docs*
