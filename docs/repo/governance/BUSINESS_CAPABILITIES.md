---
template_id: "SYS-00-BC"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:13:00+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Business Capabilities

This document describes the operational capabilities that `agent-runner-v2` enables
for organizations adopting AI-Driven SDLC workflows.

## Capability Map

The runner provides four primary capability domains:

### 1. Workflow Orchestration

| Capability | Description | Operational Value |
|------------|-------------|-------------------|
| Step-by-step execution | Sequential workflow execution with state persistence | Controlled, auditable process |
| Routing logic | Approve/reject/replan transitions based on results | Human oversight at decision points |
| Parallel workflows | Multiple independent workflows can run concurrently | Scalable artifact production |
| State recovery | Resume interrupted workflows from last checkpoint | Resilience against failures |

### 2. AI Integration

| Capability | Description | Operational Value |
|------------|-------------|-------------------|
| LLM backend abstraction | Pluggable coder adapters for different LLM providers | Flexibility in AI model selection |
| Prompt templating | Declarative prompt definitions with context injection | Consistent, version-controlled prompts |
| Sidecar metadata contract | Structured result reporting via `meta.json` | Reliable output parsing and validation |
| Token usage tracking | Per-step usage metrics for cost management | Visibility into AI resource consumption |

### 3. Artifact Production

| Capability | Description | Operational Value |
|------------|-------------|-------------------|
| Documentation generation | Automated generation of governance and technical docs | Reduced documentation burden |
| Architecture site publishing | Static site generation for architecture documentation | Stakeholder visibility |
| Validation gates | Automated checks for artifact quality | Quality assurance without manual review |
| Artifact promotion | Controlled promotion through workflow phases | Traceable artifact lifecycle |

### 4. Governance & Control

| Capability | Description | Operational Value |
|------------|-------------|-------------------|
| Human approval gates | Review steps requiring explicit approval | Control over critical decisions |
| Audit trail | Complete execution history in job state | Compliance and debugging support |
| Role-based policies | Coder role definitions for workflow execution | Controlled access to AI capabilities |
| Declarative doc protection | Allow-list model for document deletion | Safety against accidental data loss |

## Operational Interpretation

### For Development Teams

Development teams can use the runner to:

1. **Bootstrap repository governance**: Generate Layer 1 ecosystem governance and Layer 2 repo master docs
2. **Execute SDLC workflows**: Run phase-specific workflows for requirements, planning, implementation, and validation
3. **Produce documentation**: Generate and validate architecture sites, codebase docs, and system docs
4. **Track progress**: Monitor workflow execution state and artifact production

### For Operations Teams

Operations teams can use the runner to:

1. **Deploy as daemon**: Run in backend worker mode for continuous workflow execution
2. **Monitor execution**: Track job state, step progress, and execution history
3. **Manage credentials**: Configure coder connections and notification credentials
4. **Scale horizontally**: Deploy multiple daemon instances for parallel processing

### For Architects

Architects can use the runner to:

1. **Define workflow bundles**: Create new plugin workflow packages for specific use cases
2. **Establish governance**: Define documentation standards and bundle taxonomy
3. **Plan migrations**: Migrate legacy workflows to plugin-based architecture
4. **Validate compliance**: Ensure workflows adhere to governance rules

## Capability Maturity

| Capability Domain | Current Maturity | Target Maturity |
|-------------------|------------------|-----------------|
| Workflow Orchestration | Established | Optimizing |
| AI Integration | Established | Optimizing |
| Artifact Production | Developing | Established |
| Governance & Control | Established | Optimizing |

**Maturity levels:**

- **Initial**: Capability exists but not formalized
- **Developing**: Capability formalized but not fully utilized
- **Established**: Capability actively used with documented processes
- **Optimizing**: Capability continuously improved based on metrics

## Planned Capabilities

The following capabilities are planned for future releases:

| Capability | Target Release | Business Value |
|------------|----------------|----------------|
| SDLC workflow families | Post Layer 2 restoration | Phase-specific artifact production |
| Initiative intake workflow | Post Layer 2 restoration | Structured requirement capture |
| Automated code review | Future | Reduced manual review burden |
| Multi-repo coordination | Future | Cross-repository workflow orchestration |