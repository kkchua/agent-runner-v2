---
template_id: "SYS-00-BC"
title: "Business Capabilities - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities: agent-runner-v2

## Purpose

This document describes what the agent-runner-v2 platform enables operationally. It maps technical capabilities to business outcomes for stakeholders and decision-makers.

## Capability Map

### Core Capabilities

| Capability | Business Outcome | Operational Impact |
|------------|------------------|-------------------|
| **Structured Workflow Execution** | Repeatable, auditable processes | Reduced variability, compliance readiness |
| **Multi-Model LLM Support** | Flexibility in AI backend choice | Cost optimization, capability matching |
| **Review Loop Integration** | Quality gates before commitment | Reduced defect escape rate |
| **Approval Gate Enforcement** | Controlled progression | Risk mitigation, audit trail |
| **Deterministic Actions** | Reliable, testable operations | Predictable behavior, debugging ease |
| **Documentation Generation** | Self-documenting workflows | Knowledge retention, onboarding |
| **Drift Detection** | Maintained documentation accuracy | Reduced technical debt |
| **Operational Visibility** | Insight into execution | Proactive issue detection |

## Operational Interpretation

### Workflow Orchestration

**Technical**: Multi-step workflows with conditional routing

**Business Value**:
- Standardized processes across teams
- Consistent delivery methodology
- Reduced tribal knowledge dependency
- Scalable execution model

**Use Cases**:
- Initiative intake and refinement
- Delivery planning and task decomposition
- Bug fix workflows with validation
- Documentation synchronization

### LLM Abstraction

**Technical**: Unified interface for Claude, Codex, Qwen

**Business Value**:
- Vendor flexibility
- Cost optimization per task type
- Model capability matching
- Future-proofing against provider changes

**Operational Impact**:
- Switch models without workflow changes
- A/B test model performance
- Fallback options for availability

### Review and Refinement

**Technical**: Configurable review loops with max_rejects

**Business Value**:
- Quality assurance gates
- Automated rejection handling
- Escalation to replan when needed
- Learning from rejections

**Use Cases**:
- Plan review before execution
- Implementation review before validation
- Documentation review before publication

### Documentation Governance

**Technical**: Generated docs with validation and drift detection

**Business Value**:
- Living documentation
- Reduced manual documentation effort
- Consistency across projects
- Change impact visibility

**Artifacts**:
- System documentation (governance, architecture)
- Delivery documentation (initiatives, plans, tasks)
- Codebase documentation (inventory, modules)
- Audience-specific sites (stakeholders, developers)

### Operational Supervision

**Technical**: Daemon mode with heartbeat and logging

**Business Value**:
- 24/7 execution capability
- Centralized monitoring
- Failure recovery
- Audit trail

**Operational Features**:
- Job tracking and status
- Step-level logging
- Notification integration (Pushover)
- Backend integration for enterprise deployment

## Capability Detail

### 1. Initiative Management

**Scope**: From idea to planned work

**Workflows**:
- `20_initiative_intake_v1`: Draft and refine initiatives
- `30_delivery_planning_v1`: Plan generation and task decomposition

**Outcomes**:
- Structured initiative capture
- Pre-init refinement
- Delivery plan with task graph
- Clear ownership and timeline

### 2. Bug Fix Workflow

**Scope**: From report to validated fix

**Workflow**: `21_bug_fix_intake_v1`

**Steps**:
1. Triage — categorize and prioritize
2. Reproduce — confirm the issue
3. Root cause — isolate the problem
4. Patch — implement fix
5. Regression validate — verify fix and no regressions

**Outcomes**:
- Systematic bug resolution
- Root cause documentation
- Regression prevention
- Closure validation

### 3. Task Execution

**Scope**: Implementation with validation

**Workflow**: `31_task_execution_v1`

**Steps**:
1. Implementation planning
2. Implementation review
3. Execution
4. Documentation sync
5. Validation

**Outcomes**:
- Planned implementation
- Reviewed code changes
- Synchronized documentation
- Validated deliverables

### 4. Documentation Synchronization

**Scope**: Keep docs aligned with code

**Workflow**: `40_documentation_sync_v1`

**Capabilities**:
- Codebase inventory refresh
- Integration map updates
- Failure mode analysis
- Architecture flow documentation

**Outcomes**:
- Accurate codebase representation
- Current integration documentation
- Risk awareness
- Knowledge retention

### 5. Architecture Site Generation

**Scope**: Publish audience-specific documentation

**Workflows**:
- `41_audience_doc_v1`: Generate markdown
- `51-55_*_docs_v1`: Generate HTML sites

**Audiences**:
- Stakeholders — business value view
- Developers — technical implementation
- Operators — runtime and deployment
- Testers — validation criteria
- Users — feature guidance

**Outcomes**:
- Audience-appropriate documentation
- Consistent styling and navigation
- Versioned documentation
- PDF export capability

### 6. Delivery Scaffold

**Scope**: Establish documentation governance

**Workflow**: `10_execution_scaffold_v1`

**Outputs**:
- SOP documents
- Template registry
- Agent contracts
- Governance structure

**Outcomes**:
- Consistent delivery methodology
- Clear agent responsibilities
- Template-driven consistency
- Governance compliance

## Value Proposition by Role

### For Engineering Managers

- **Standardized delivery**: Consistent methodology across teams
- **Visibility**: Job tracking and operational metrics
- **Quality gates**: Review loops prevent defect escape
- **Documentation**: Reduced knowledge silos

### For Developers

- **Clear workflow**: Step-by-step guidance
- **Context preservation**: Documentation generation
- **Review support**: Structured feedback loops
- **Tool integration**: LLM abstraction

### For Operations

- **Daemon supervision**: 24/7 execution
- **Monitoring**: Logging and heartbeats
- **Failure handling**: Retry and recovery
- **Notifications**: Proactive alerts

### For QA/Validation

- **Structured testing**: Validation workflows
- **Regression prevention**: Automated checks
- **Documentation verification**: Drift detection
- **Traceability**: Job and artifact tracking

## Success Metrics

### Operational Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow success rate | >95% | Jobs completing successfully |
| Review loop efficiency | <3 iterations | Average rejects per step |
| Documentation freshness | <7 days | Time since last sync |
| Artifact validation pass | >98% | Validation success rate |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to plan | -50% | vs. manual planning |
| Documentation coverage | 100% | Modules with documentation |
| Knowledge transfer | -30% | Onboarding time reduction |
| Defect escape rate | -40% | Production defects |

## Limitations and Constraints

### Current Limitations

- **Provisioning**: 7-8 minutes per task for backend-connected mode
- **LLM dependency**: Requires API keys for cloud models
- **Platform**: Python-based, requires Python 3.10+
- **Storage**: Local filesystem for artifacts (S3 integration planned)

### Scaling Considerations

- **Concurrent jobs**: Limited by backend capacity
- **Artifact storage**: Growth over time requires cleanup
- **Log retention**: Configurable rotation required
- **Notification volume**: Rate limiting for high-volume scenarios

## Roadmap Alignment

### Current State (v2.x)

- Core workflow execution
- Plugin system migration
- Documentation governance
- Backend integration

### Near Term

- Plugin workflow system completion
- Enhanced validation
- Improved error recovery
- Expanded notification channels

### Future

- Multi-tenant support
- Advanced scheduling
- Integration marketplace
- Analytics and insights

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
