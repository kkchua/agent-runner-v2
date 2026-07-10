---
template_id: "SYS-00-FS"
title: "Functional Specification"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification

## System Purpose

`agent-runner-v2` is a workflow orchestration engine that enables structured multi-step execution using LLM backends and deterministic actions. The system provides:

1. **Workflow definition** — Declarative step sequences with routing logic
2. **Prompt rendering** — Template-based prompt generation with context substitution
3. **Coder invocation** — Multi-backend LLM execution with result validation
4. **Action execution** — Deterministic operations as workflow steps
5. **State management** — Job lifecycle with persistence and retry
6. **Review routing** — Built-in quality gates with approve/reject flows

## Functional Capabilities

### FC-1: Workflow Definition

**Description**: Define multi-step workflows with step sequences and routing rules.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-1.1 | Workflows SHALL define an ordered sequence of steps | Must |
| FC-1.2 | Steps SHALL have unique identifiers within a workflow | Must |
| FC-1.3 | Steps SHALL specify their execution type (coder or action) | Must |
| FC-1.4 | Steps SHALL define routing rules for next step selection | Must |
| FC-1.5 | Workflows SHALL support conditional routing based on step results | Must |
| FC-1.6 | Workflows SHALL support review loops with approve/reject routing | Must |

**Current Implementation**:

- `template_groups.py` — Monolithic workflow registry (2,453 lines)
- `workflow_packages/` — Plugin-based migration in progress

### FC-2: Prompt Rendering

**Description**: Render prompt templates with context substitution.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-2.1 | Prompts SHALL be stored as template files | Must |
| FC-2.2 | Templates SHALL support variable substitution | Must |
| FC-2.3 | Context SHALL include artifact paths and content | Must |
| FC-2.4 | Rendering SHALL fail gracefully on missing variables | Must |
| FC-2.5 | Prompts SHALL include sidecar instruction injection | Must |

**Current Implementation**:

- `step_runner.py` — Prompt rendering logic
- `agent_runner_v2/bootstrap/workflows/default/prompts/` — Template storage
- `{ARTIFACT_KEY}` pattern for context substitution

### FC-3: Coder Invocation

**Description**: Invoke LLM backends with unified interface.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-3.1 | System SHALL support multiple LLM backends (Claude, Codex, Qwen) | Must |
| FC-3.2 | Backends SHALL be configurable per step | Must |
| FC-3.3 | Invocation SHALL include prompt and context | Must |
| FC-3.4 | Results SHALL be validated against schema | Must |
| FC-3.5 | Token usage SHALL be tracked per invocation | Should |
| FC-3.6 | Failures SHALL be categorized for retry decisions | Must |

**Current Implementation**:

- `coder_adapters.py` — Unified invocation interface
- Model configuration via `model_mapping.json`
- `CoderInvocationError` for failure handling

### FC-4: Action Execution

**Description**: Execute deterministic actions as workflow steps.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-4.1 | Actions SHALL be deterministic and reproducible | Must |
| FC-4.2 | Actions SHALL declare input/output artifacts | Must |
| FC-4.3 | Actions SHALL validate preconditions | Must |
| FC-4.4 | Actions SHALL produce valid artifacts | Must |
| FC-4.5 | Actions SHALL report success/failure via return | Must |
| FC-4.6 | Custom actions SHALL be supported | Should |

**Current Implementation**:

- `actions/` package — 28 defined actions
- `run_action()` in `step_runner.py`
- Action registry via module imports

### FC-5: State Management

**Description**: Track and persist job state across step boundaries.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-5.1 | Job state SHALL be persisted to disk | Must |
| FC-5.2 | State SHALL include step execution history | Must |
| FC-5.3 | State SHALL track retry attempts | Must |
| FC-5.4 | State SHALL record artifact paths | Must |
| FC-5.5 | State schema SHALL be versioned | Must |
| FC-5.6 | State SHALL support backward compatibility | Must |

**Current Implementation**:

- `job_state.py` — State management (1,806 lines)
- JSON files in `~/.ukbe-runner/jobs/`
- Schema version 6 (CURRENT_SCHEMA_VERSION)

### FC-6: Review Routing

**Description**: Route workflow based on review outcomes.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-6.1 | Steps SHALL report APPROVED or REJECTED status | Must |
| FC-6.2 | REJECTED steps SHALL trigger retry or refinement | Must |
| FC-6.3 | Retry limits SHALL be configurable | Must |
| FC-6.4 | Review state SHALL be persisted | Must |
| FC-6.5 | Human approval SHALL be supported | Should |

**Current Implementation**:

- `workflow_router.py` — Routing logic (787 lines)
- `route_after_step()` for success routing
- `route_after_failure()` for failure handling

### FC-7: Sidecar Contract

**Description**: Structured communication via meta.json sidecar files.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-7.1 | Steps SHALL write meta.json sidecar on completion | Must |
| FC-7.2 | Sidecar SHALL follow v2 schema | Must |
| FC-7.3 | Sidecar SHALL include status (APPROVED/REJECTED) | Must |
| FC-7.4 | Sidecar SHALL list produced artifacts | Must |
| FC-7.5 | Sidecar SHALL include timestamp | Must |
| FC-7.6 | Missing sidecar SHALL be treated as failure | Must |

**Current Implementation**:

- v2 schema with `schema_version`, `coder_result` structure
- `MetaJsonMissingError`, `MetaJsonInvalidError` exceptions
- Automatic validation in `step_runner.py`

### FC-8: Execution Modes

**Description**: Support multiple execution patterns.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| FC-8.1 | Manual execution SHALL be supported | Must |
| FC-8.2 | Worker mode SHALL poll backend for work | Must |
| FC-8.3 | Daemon mode SHALL supervise child processes | Must |
| FC-8.4 | Modes SHALL share core execution logic | Must |
| FC-8.5 | Mode selection SHALL be CLI-driven | Must |

**Current Implementation**:

- `run_agent.py` — CLI entry point
- `daemon.py` — Daemon supervision
- `backend_client.py` — Backend integration

## Actors

### Human Actors

| Actor | Role | Capabilities |
|-------|------|--------------|
| **Developer** | Workflow author | Define workflows, test locally, debug |
| **Operator** | System administrator | Deploy, monitor, troubleshoot |
| **Reviewer** | Quality assurance | Review outputs, approve/reject |
| **End User** | Workflow consumer | Submit jobs, receive results |

### System Actors

| Actor | Role | Capabilities |
|-------|------|--------------|
| **CLI** | Command-line interface | Parse args, invoke workflows |
| **Worker** | Backend-connected executor | Poll, claim, execute, submit |
| **Daemon** | Workstation supervisor | Spawn, monitor, recover |
| **Backend** | Orchestration service | Queue, dispatch, track |

## Core Behaviors

### Behavior: Workflow Execution

**Trigger**: CLI command or backend dispatch

**Flow**:
1. Parse CLI arguments
2. Load or create job state
3. Load workflow definition
4. For each step:
   a. Render prompt (if coder step)
   b. Invoke coder or execute action
   c. Validate meta.json sidecar
   d. Route to next step
5. Complete or fail

**Success Criteria**: All steps complete with APPROVED status

**Failure Criteria**: Step failure with exhausted retries

### Behavior: Retry

**Trigger**: Step REJECTED or failure

**Flow**:
1. Check retry limits
2. If within limits:
   a. Increment retry count
   b. Log retry attempt
   c. Re-execute step
3. If limits exceeded:
   a. Mark job failed
   b. Record failure
   c. Route to failure handling

**Success Criteria**: Step succeeds on retry

**Failure Criteria**: Retry limits exceeded

### Behavior: Review Loop

**Trigger**: Step configured with review

**Flow**:
1. Execute step
2. Present output for review
3. Wait for approve/reject
4. If approved:
   a. Continue to next step
5. If rejected:
   a. Incorporate feedback
   b. Retry step

**Success Criteria**: Reviewer approves

**Failure Criteria**: Reject limits exceeded

### Behavior: Worker Polling

**Trigger**: Worker mode start

**Flow**:
1. Register with backend
2. Poll for available work
3. If work available:
   a. Claim work item
   b. Execute step
   c. Submit result
4. Repeat until stopped

**Success Criteria**: Continuous operation

**Failure Criteria**: Backend unreachable, authentication failure

## Data Flows

### Flow: Step Execution

```
┌────────┐    ┌──────────┐    ┌────────┐    ┌──────────┐    ┌────────┐
│  Load  │───▶│ Render   │───▶│ Invoke │───▶│ Validate │───▶│ Route  │
│  Step  │    │ Prompt   │    │ Coder  │    │ Sidecar  │    │ Next   │
└────────┘    └──────────┘    └────────┘    └──────────┘    └────────┘
                                    │
                                    ▼
                              ┌──────────┐
                              │ Write    │
                              │ Artifacts│
                              └──────────┘
```

### Flow: Job Lifecycle

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ Create │───▶│  Run   │───▶│ Step   │───▶│Complete│───▶│ Archive│
│  Job   │    │  Steps │    │ Loop   │    │/ Fail  │    │        │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
                                │
                                ▼
                           ┌────────┐
                           │ Retry  │
                           │/ Review│
                           └────────┘
```

## Functional Constraints

| Constraint | Description |
|------------|-------------|
| **Windows primary** | Execution optimized for Windows; Unix secondary |
| **Local filesystem** | Artifacts stored on local filesystem |
| **JSON state** | Job state in JSON format |
| **Template-based** | Prompts as template files, not inline |
| **Sidecar required** | meta.json mandatory for all coder steps |

## Functional Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Monolithic workflow registry | Hard to maintain | Plugin migration in progress |
| Windows-centric paths | Unix support limited | Path abstraction planned |
| Backend required for worker | Cannot run standalone | Local mode available |
| No built-in scheduling | External scheduler needed | Cron/CI integration |

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform overview
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Operational capabilities
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality requirements
- [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) — Component breakdown

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
