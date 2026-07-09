---
template_id: "SYS-00-BC"
title: "Business Capabilities - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities

## Purpose

This document describes what the `agent-runner-v2` runner enables operationally. It maps technical functions to business outcomes, explaining the platform's operational value.

## Capability Map

### Core Execution Capabilities

| Capability | Description | Operational Outcome |
|------------|-------------|---------------------|
| **Workflow Orchestration** | Execute multi-step workflows with deterministic routing | Reliable automation of complex processes |
| **Multi-Model Execution** | Invoke Claude, Codex, Qwen, and aliased models | Flexibility to use best model for each task |
| **Job State Management** | Track, persist, and resume job execution | Long-running workflows with interruption tolerance |
| **Artifact Validation** | Validate generated outputs against schemas | Quality assurance through structured validation |
| **Retry and Recovery** | Automatic retry with failure tracking | Resilient execution with explicit failure handling |

### Documentation Capabilities

| Capability | Description | Operational Outcome |
|------------|-------------|---------------------|
| **Automated Documentation** | Generate system and codebase docs via workflows | Always-current documentation with minimal effort |
| **Documentation Sync** | Reconcile documentation with codebase changes | Documentation that reflects actual code state |
| **Multi-Audience Output** | Generate stakeholder, developer, operator views | Information tailored to each audience |
| **Architecture Sites** | Publish browsable HTML documentation | Accessible architecture communication |

### Development Capabilities

| Capability | Description | Operational Outcome |
|------------|-------------|---------------------|
| **Initiative Management** | Structured intake for enhancements and refactors | Clear scope before development begins |
| **Bug Fix Workflow** | Triage, reproduce, isolate, patch, validate | Systematic bug resolution with full traceability |
| **Delivery Planning** | Generate plans, task graphs, and contracts | Predictable delivery with clear obligations |
| **Task Execution** | Implement, review, validate tasks | Quality-controlled code delivery |

### Operational Capabilities

| Capability | Description | Operational Outcome |
|------------|-------------|---------------------|
| **Local Execution** | Run workflows on workstation without backend | Independent development and testing |
| **Backend Integration** | Connect to backend for coordinated execution | Enterprise-scale workflow distribution |
| **Daemon Supervision** | Continuous workstation operation with child process management | Always-on execution capability |
| **Notification Integration** | Pushover notifications for step completion | Timely awareness of workflow status |
| **Configuration Management** | Centralized config with environment overrides | Flexible deployment across environments |

## Operational Interpretation

### Workflow Automation Value

The platform enables organizations to automate complex, multi-step processes that require:

- **Human-like reasoning**: LLM-powered analysis and generation
- **Structured output**: Validated artifacts with meta.json sidecars
- **Decision points**: Explicit routing based on validation results
- **Failure handling**: Clear retry and escalation paths

**Example**: A documentation generation workflow that:
1. Scans the codebase
2. Analyzes module dependencies
3. Generates per-module documentation
4. Validates completeness
5. Publishes HTML site

### Documentation Governance Value

The platform enforces documentation standards through:

- **Template-driven generation**: Consistent structure via workflow prompts
- **Protected documents**: Workflow-generated files marked and preserved
- **Validation gates**: Documentation sync verifies completeness
- **Change tracking**: Change impact documents record drift

**Value**: Documentation stays synchronized with code without manual maintenance burden.

### Quality Assurance Value

Quality is built into the execution model:

| Mechanism | How It Works |
|-----------|--------------|
| **Sidecar Validation** | Every step produces validated meta.json |
| **Explicit Routing** | No silent failures; all paths explicit |
| **Retry Limits** | Configurable retry with failure history |
| **Artifact Checking** | Pre-flight validation of required inputs |
| **Schema Enforcement** | Job state and responses validated against schemas |

### Scalability Path

Current capabilities support single-tenant workstation operation. The platform architecture enables future scaling to:

| Current | Future |
|---------|--------|
| Local execution | Distributed workers |
| File-based state | Backend-coordinated state |
| Single user | Multi-tenant isolation |
| Manual workflow trigger | Event-driven execution |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
