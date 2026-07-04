---
template_id: "SYS-00-BC"
title: "Business Capabilities"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities

## Purpose

This document describes the operational capabilities enabled by the `agent-runner-v2` platform. It maps technical features to business outcomes and explains the value delivered to different stakeholder groups.

## Capability Map

| Capability | Description | Business Outcome |
|------------|-------------|------------------|
| **Workflow Orchestration** | Multi-step workflow execution with deterministic routing | Consistent, repeatable process execution |
| **LLM Provider Abstraction** | Unified interface to Claude, Codex, Qwen | Vendor flexibility, cost optimization |
| **Review Loop Management** | Built-in refinement cycles with configurable limits | Quality assurance without infinite loops |
| **Failure Classification** | Automatic categorization (retryable vs. fatal) | Efficient error handling |
| **State Persistence** | Job state with artifact tracking | Resume capability, audit trail |
| **Bootstrap Workflows** | Pre-defined templates for common patterns | Reduced time-to-value |
| **Documentation Governance** | Automated doc generation and validation | Maintained documentation without drift |

## Operational Interpretation

### Capability: Workflow Orchestration

**What It Enables**: Organizations can define and execute complex multi-step processes with consistent behavior across environments.

**Operational Impact**:
- Delivery planning workflows decompose initiatives into implementable tasks
- Code review workflows ensure quality gates before merge
- Documentation workflows keep technical docs synchronized with code

**Metrics**:
- Workflow completion rate
- Average steps per workflow
- Time from initiation to completion

### Capability: LLM Provider Abstraction

**What It Enables**: Organizations can use the optimal LLM for each task without workflow changes.

**Operational Impact**:
- Cost optimization (route simple tasks to cheaper models)
- Capability matching (complex tasks to more capable models)
- Vendor independence (switch providers without workflow rewrite)

**Metrics**:
- Cost per workflow
- Success rate by model
- Model utilization distribution

### Capability: Review Loop Management

**What It Enables**: Iterative refinement of LLM outputs with human oversight and automatic limits.

**Operational Impact**:
- Quality assurance through structured review
- Prevention of infinite refinement cycles
- Clear escalation paths for complex cases

**Metrics**:
- Average refinement iterations
- Review rejection rate
- Human intervention frequency

### Capability: Failure Classification

**What It Enables**: Automatic handling of transient failures with clear escalation for persistent issues.

**Operational Impact**:
- Reduced manual intervention for transient issues
- Fast failure for configuration problems
- Clear ownership for resolution

**Failure Classes**:
| Class | Description | Action |
|-------|-------------|--------|
| `AUTO_RETRYABLE` | Transient failures (network, rate limits) | Automatic retry with backoff |
| `HUMAN_RETRY_REQUIRED` | Context or configuration issues | Alert human operator |
| `FATAL` | Unrecoverable errors | Terminate workflow |

### Capability: State Persistence

**What It Enables**: Long-running workflows can be interrupted and resumed; audit trails for compliance.

**Operational Impact**:
- Workstation reboot doesn't lose progress
- Historical analysis of execution patterns
- Compliance evidence for regulated industries

**State Elements**:
- Completed steps
- Artifact paths
- Review decisions
- Retry history
- Model usage

### Capability: Bootstrap Workflows

**What It Enables**: Pre-built workflows for common patterns accelerate adoption.

**Included Families**:
| Family | Purpose | Time Savings |
|--------|---------|--------------|
| `initiative_intake_v1` | Requirements capture and refinement | 2-3 days |
| `delivery_planning_v1` | Plan and task decomposition | 1-2 days |
| `task_execution_v1` | Implementation and validation | 1-2 days |
| `documentation_sync_v1` | Doc maintenance | Ongoing |
| `architecture_site_v1` | Architecture visualization | 1 day |

### Capability: Documentation Governance

**What It Enables**: Documentation stays synchronized with code through automated generation and validation.

**Operational Impact**:
- Reduced documentation drift
- Consistent documentation structure
- Automatic validation of doc completeness

**Governance Elements**:
- Protected document sets
- Template conformance validation
- Change impact tracking

## Actor Capabilities

### Developer Capabilities

| Capability | Description | Command |
|------------|-------------|---------|
| Local workflow run | Execute workflows without backend | `ukbe-run-agent run` |
| Job inspection | View job state and history | `ukbe-run-agent show-job` |
| Step retry | Retry failed steps | `ukbe-run-agent retry` |
| Daemon control | Manage workstation daemon | `ukbe-run-agent daemon` |

### Operator Capabilities

| Capability | Description | Command |
|------------|-------------|---------|
| Worker registration | Connect to backend | `ukbe-run-agent worker` |
| Work claiming | Poll for available work | `ukbe-run-agent poll` |
| Step execution | Execute claimed steps | `ukbe-run-agent execute-step` |
| Log streaming | Monitor execution | Daemon logs |

### Workflow Author Capabilities

| Capability | Description | Mechanism |
|------------|-------------|-----------|
| Template definition | Define step sequences | `template_groups.py` |
| Prompt authoring | Create step prompts | `prompts/<step>.txt` |
| Artifact declaration | Define inputs/outputs | `required_inputs`, `produces` |
| Routing configuration | Configure review/refine | `on_reject_refine` |

## Capability Dependencies

```
Workflow Orchestration
├── LLM Provider Abstraction
│   └── Model Mapping Configuration
├── State Persistence
│   └── Job Schema Definition
├── Review Loop Management
│   └── Routing Configuration
└── Failure Classification
    └── Exception Hierarchy

Bootstrap Workflows
├── Documentation Governance
│   └── Protected Document Model
└── Workflow Orchestration
```

## Capability Evolution

| Phase | Capabilities | Target Users |
|-------|--------------|--------------|
| v0.1 (Current) | Core orchestration, local execution, daemon | Developers |
| v0.2 (Planned) | Enhanced backend integration, metrics | Operators |
| v1.0 (Target) | Full governance, audit, multi-tenant | Enterprise |

---

*This capability map describes what the platform enables operationally. See `FUNCTIONAL_SPEC.md` for detailed functional behaviors.*
