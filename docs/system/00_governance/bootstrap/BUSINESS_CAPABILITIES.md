---
template_id: "SYS-00-BC"
title: "Business Capabilities"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities

## Purpose

This document describes the operational capabilities that `agent-runner-v2` enables. It explains what users can accomplish with the platform, organized by capability area.

## Audience

| Role | Interest |
|------|----------|
| **Stakeholders** | Understanding platform value and use cases |
| **Product managers** | Feature prioritization and roadmap planning |
| **Operators** | Operational possibilities and constraints |
| **New users** | What can be built with this platform |

## Capability Map

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT-RUNNER-V2                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   WORKFLOW  │  │   CODER     │  │   ACTION    │       │
│  │ ORCHESTRATION│  │  EXECUTION  │  │  EXECUTION  │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                │                │              │
│         ▼                ▼                ▼              │
│  ┌──────────────────────────────────────────────────┐   │
│  │              EXECUTION MODES                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐   │   │
│  │  │  Manual │  │ Worker  │  │     Daemon      │   │   │
│  │  │   Run   │  │  Poll   │  │  Supervision    │   │   │
│  │  └─────────┘  └─────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   REVIEW    │  │   STATE     │  │     NOTIFICATION   ││
│  │    LOOPS    │  │ MANAGEMENT  │  │     MANAGEMENT     ││
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Capability Areas

### 1. Workflow Orchestration

**Description**: Define and execute multi-step workflows with structured routing between steps.

**Capabilities**:

| Capability | Description |
|------------|-------------|
| **Multi-step execution** | Execute sequences of steps with state persistence between steps |
| **Conditional routing** | Route to different next steps based on previous step results |
| **Retry logic** | Automatic retry of failed steps with configurable limits |
| **Review loops** | Built-in review/reject/approve cycles for quality assurance |
| **Parallel execution** | Support for concurrent step execution where applicable |
| **State persistence** | Job state saved and resumed across step boundaries |

**Operational Value**:

- Reduces manual coordination overhead
- Ensures consistent execution patterns
- Enables long-running workflows
- Supports human-in-the-loop approval

**Workflow Families**:

The platform includes 21 predefined workflow families:

| Workflow Family | Steps | Purpose |
|-----------------|-------|---------|
| `00_master_docs_bootstrap_v1/v2` | 13 | Master system documentation generation |
| `10_execution_scaffold_v1` | 13 | Delivery scaffold generation |
| `20_initiative_intake_v1` | 5 | Initiative capture and refinement |
| `21_bug_fix_intake_v1` | 7 | Bug triage and patching |
| `30_delivery_planning_v1` | 10 | Plan and task graph generation |
| `31_task_execution_v1` | 12 | Implementation and validation |
| `40_documentation_sync_v1` | 5 | Documentation reconciliation |
| `50_architecture_site_v1` | 2 | HTML architecture site publishing |
| Image/video pipelines | 3-10 | Content generation workflows |

### 2. Coder Execution

**Description**: Invoke LLM backends with unified interface and result handling.

**Capabilities**:

| Capability | Description |
|------------|-------------|
| **Multi-backend support** | Claude, Codex, Qwen with unified interface |
| **Model aliasing** | Map logical names to configured models |
| **Prompt templating** | Template substitution with artifact context |
| **Result validation** | Structured result parsing via meta.json |
| **Usage tracking** | Token usage and cost tracking |
| **Error handling** | Graceful degradation on coder failures |

**Operational Value**:

- Reduces vendor lock-in
- Enables backend selection per step
- Standardizes result handling
- Tracks operational costs

**Supported Backends**:

| Backend | Model Types | Use Case |
|---------|-------------|----------|
| Claude | Sonnet, Opus, Haiku | Complex reasoning, long context |
| Codex | GPT-4o, GPT-4 | Code generation, general tasks |
| Qwen | Various | Alternative provider, cost optimization |

### 3. Action Execution

**Description**: Execute deterministic, non-LLM operations as workflow steps.

**Capabilities**:

| Capability | Description |
|------------|-------------|
| **28 deterministic actions** | Pre-defined actions for common operations |
| **Custom actions** | Support for user-defined action implementations |
| **Action validation** | Pre and post-action validation |
| **Artifact generation** | Actions that produce and validate artifacts |
| **External integration** | Actions that interact with external systems |

**Operational Value**:

- Guarantees deterministic outcomes
- Enables non-LLM operations in workflows
- Provides building blocks for complex workflows
- Maintains audit trail

**Action Categories**:

| Category | Actions | Purpose |
|----------|---------|---------|
| **Documentation** | validate_*, sync_* | Documentation validation and sync |
| **Site generation** | generate_site, publish_* | HTML site generation |
| **Media** | execute_t2i, execute_i2v, execute_voiceover | Content generation |
| **Artifact** | copy_artifact, promote_artifact, archive_* | Artifact lifecycle |
| **Scaffold** | prepare_delivery_scaffold, finalize_bootstrap | Setup operations |

### 4. Execution Modes

**Description**: Multiple execution patterns for different operational contexts.

#### 4.1 Manual Execution

| Capability | Description |
|------------|-------------|
| **CLI interface** | Command-line execution with argument passing |
| **Interactive mode** | Human-in-the-loop for approvals |
| **Local artifacts** | File-system based artifact management |
| **Immediate feedback** | Synchronous execution with console output |
| **Development friendly** | Ideal for testing and development |

**Use Cases**:
- Development and testing
- One-off workflow runs
- Initial workflow development
- Local debugging

#### 4.2 Worker Mode

| Capability | Description |
|------------|-------------|
| **Backend polling** | Poll backend for available work |
| **Distributed workers** | Multiple workers sharing workload |
| **Event notifications** | Real-time status updates |
| **Result submission** | Structured result reporting |
| **Worker identity** | Stable worker IDs for attribution |

**Use Cases**:
- Production execution
- Distributed workloads
- Backend-driven workflows
- Scalable processing

#### 4.3 Daemon Mode

| Capability | Description |
|------------|-------------|
| **Supervision** | Long-running workstation supervisor |
| **Child process management** | Spawns and monitors child processes |
| **Automatic recovery** | Restarts failed children |
| **Log aggregation** | Centralized logging |
| **Heartbeat tracking** | Health monitoring |

**Use Cases**:
- Continuous operation
- Workstation-based processing
- Background execution
- Production deployment

### 5. Review and Refinement

**Description**: Built-in quality assurance through review loops.

**Capabilities**:

| Capability | Description |
|------------|-------------|
| **Review gates** | Mandatory review steps in workflows |
| **Approve/reject routing** | Conditional routing based on review outcome |
| **Refinement loops** | Automatic retry with feedback incorporation |
| **Review tracking** | Review state persistence |
| **Human approval** | Human-in-the-loop for critical steps |

**Operational Value**:

- Ensures output quality
- Captures review rationale
- Enables continuous improvement
- Supports compliance requirements

### 6. State Management

**Description**: Comprehensive job state tracking and persistence.

**Capabilities**:

| Capability | Description |
|------------|-------------|
| **Job lifecycle** | Create → Execute → Complete/Failed |
| **State persistence** | JSON-based state storage |
| **Schema versioning** | Backward compatible state evolution |
| **Retry history** | Track retry attempts and outcomes |
| **Artifact tracking** | Record produced and consumed artifacts |
| **Usage aggregation** | Aggregate token usage across steps |

**Operational Value**:

- Enables long-running workflows
- Supports failure recovery
- Provides audit trail
- Tracks operational costs

### 7. Notification Management

**Description**: Real-time notifications for workflow events.

**Capabilities**:

| Capability | Description |
|------------|-------------|
| **Pushover integration** | Mobile notifications |
| **Event types** | Start, complete, failure, approval needed |
| **Step-level notifications** | Per-step notification configuration |
| **Workflow notifications** | Workflow-level summary notifications |

**Operational Value**:

- Reduces monitoring overhead
- Enables mobile awareness
- Supports on-call workflows
- Improves response time

## Operational Interpretation

### For Developers

The platform enables:

- **Rapid workflow development** — Define workflows in code or configuration
- **Local testing** — Test workflows before deployment
- **Backend integration** — Connect to backend for production execution
- **Quality assurance** — Built-in review and refinement

### For Operators

The platform provides:

- **Multiple execution modes** — Choose appropriate mode for context
- **Monitoring and alerting** — Notifications and status tracking
- **Scalability** — Distributed worker pools
- **Reliability** — Retry logic and state persistence

### For Stakeholders

The platform delivers:

- **Consistent execution** — Standardized workflow patterns
- **Quality assurance** — Review loops and validation
- **Cost visibility** — Usage tracking and attribution
- **Auditability** — Complete execution history

## Capability Dependencies

```
Workflow Orchestration
├── Coder Execution
├── Action Execution
├── State Management
└── Review/Refinement

Execution Modes
├── Manual Execution
├── Worker Mode
└── Daemon Mode

Support Capabilities
├── Notification Management
└── State Management
```

## Limitations

| Capability Area | Current Limitation |
|-----------------|-------------------|
| **Workflow definition** | Monolithic registry (migration in progress) |
| **Cross-platform** | Windows-centric (Unix support secondary) |
| **Backend integration** | Requires backend for worker/daemon modes |
| **Media generation** | Requires external tools (ComfyUI, etc.) |

## Future Capabilities

| Capability | Status |
|------------|--------|
| Plugin-based workflows | In progress |
| Full Unix/Linux support | Planned |
| Additional LLM backends | Future consideration |
| Enhanced monitoring | Planned |

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform overview
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional capabilities
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality expectations
- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository analysis

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
