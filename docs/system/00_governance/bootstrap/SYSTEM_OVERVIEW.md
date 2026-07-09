---
template_id: "SYS-00-SO"
managed_by: workflow-generated
generated: "2026-07-09T21:18:02+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview

## Purpose

This document provides a high-level overview of agent-runner-v2, explaining the platform's purpose, its workflow execution model, and the value flow from input to output. It serves as the primary entry point for stakeholders, new team members, and anyone seeking to understand what the system does without diving into implementation details.

agent-runner-v2 is a standalone Python LLM workflow orchestration engine that runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions.

## Scope

### In Scope

- Workflow orchestration and execution
- Multi-step workflow management with state persistence
- Coder invocation (Claude Code, Codex CLI, Qwen Code)
- Deterministic action execution
- Sidecar-based result communication
- Review/refine routing loops
- Backend-connected worker mode
- Daemon supervision

### Out of Scope

- LLM model training or fine-tuning
- General-purpose task scheduling
- CI/CD pipeline management
- Container orchestration
- Database management systems

## Primary Flows

### Value Flow

The core value flow of agent-runner-v2 follows this pattern:

```
Requirement → Workflow → Step → Coder/Action → Artifact → Review → Route
```

**Flow Description:**

1. **Requirement Capture**: User defines work through draft initiatives, bug reports, or direct workflow invocation
2. **Workflow Selection**: Appropriate workflow family selected based on work type
3. **Step Execution**: Each step renders a prompt, invokes a coder or action, and produces artifacts
4. **Result Validation**: Step results validated via `meta.json` sidecar and artifact verification
5. **Review/Route**: Based on sidecar status, workflow routes to next step, retry, or completion
6. **Artifact Accumulation**: Approved artifacts accumulate as project state

### Execution Modes

agent-runner-v2 supports three primary execution modes:

#### Local Workflow Execution

**Purpose**: Manual workflow execution with full control

**Flow:**

```
User → ukbe-run-agent run → Load workflow → Render prompt → Execute step → Route → Repeat
```

**Use Cases:**
- Development and testing
- One-off task execution
- Debugging workflow steps
- Manual approval workflows

#### Backend-Connected Worker

**Purpose**: Backend-driven step execution

**Flow:**

```
Backend → Worker poll → Claim step → Execute → Submit result → Repeat
```

**Commands:**
- `ukbe-run-agent worker` — Continuous polling loop
- `ukbe-run-agent poll` — Single poll operation
- `ukbe-run-agent execute-step` — Single step execution

**Use Cases:**
- Distributed execution across workstations
- Backend-managed work queues
- Scalable task processing
- Workload distribution

#### Daemon Supervision

**Purpose**: Workstation supervisor for backend-connected execution

**Flow:**

```
Daemon start → Poll backend → Claim work → Spawn child process → Monitor → Heartbeat → Repeat
```

**Responsibilities:**
- Claim work from backend
- Spawn child `execute-step` processes
- Track child process state
- Emit child-scoped heartbeats
- Handle child failures

**Use Cases:**
- Long-running workstation agents
- Automatic work claiming
- Process supervision
- Operational visibility

### Workflow Lifecycle

#### Step Execution Lifecycle

Each workflow step follows a strict lifecycle:

```
Load Bundle → Render Prompt → Preflight Check → Execute → Read Sidecar → Validate → Route
```

**Phase Details:**

| Phase | Responsibility | Output |
|-------|---------------|--------|
| Load Bundle | Load workflow definition from runtime bundle | Workflow config, prompt template |
| Render Prompt | Substitute context variables, inject sidecar instructions | Final prompt text |
| Preflight Check | Verify required artifacts exist | Go/No-go decision |
| Execute | Invoke coder or run action | Raw output, artifacts |
| Read Sidecar | Parse `meta.json` for structured results | Status, remark, artifact paths |
| Validate | Verify artifacts exist at declared paths | Validation result |
| Route | Determine next step based on status | Next step or completion |

#### Sidecar Contract

The `meta.json` sidecar is the **only** structured communication channel:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary",
    "artifacts": {"ARTIFACT_KEY": "path/to/file.md"},
    "recorded_at": "2026-07-09T21:18:02+08:00"
  }
}
```

**Status Decision Rules:**
- `APPROVED`: All required artifacts exist, meta.json written
- `REJECTED`: Missing artifact, validation failure, or explicit rejection

## Architecture Profile

### Universal Baseline

agent-runner-v2 implements the **universal-bootstrap** architecture profile:

| Attribute | Value | Evidence |
|-----------|-------|----------|
| **current_profile** | explicit | Documented contracts, strict enforcement |
| **target_profile** | universal-bootstrap | Reusable workflow system |
| **migration_mode** | maintenance | Refreshes vs recreates |
| **repo_state** | explicit | Clear architecture documentation |

### Profile Separation

The system separates universal baseline from repo-selected profile:

| Aspect | Universal Baseline | Repo-Selected Profile |
|--------|-------------------|----------------------|
| **Purpose** | Rules that apply to every repo | Specifics for this repo |
| **Location** | `constants.py`, `template_groups.py` | Workflow family selection |
| **Stability** | Stable across repos | Repo-specific |
| **Migration** | Version controlled | Runtime configuration |

### agent-runner-v2 Profile

agent-runner-v2 selects an **explicit** profile with **maintenance** migration mode:

**Evidence:**

1. **Comprehensive workflow definitions**: 12+ workflow families in `template_groups.py`
2. **Strict v2 contract enforcement**: Explicit rejection of v1 patterns
3. **Centralized constants**: All paths via `constants.py`
4. **Generated doc protection**: Workflow-attributed, protected from manual edits
5. **Test infrastructure**: 109+ unit tests with strict separation

**Migration Posture:**

- Existing documents are refreshed, not recreated
- Template IDs are preserved
- Section requirements are additive
- Manual annotations outside guarded sections are preserved

## Key Risks

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Bootstrap/Runtime Sync Gap** | Changes not reflected in execution | Sync scripts, re-initialization |
| **External Coder Dependency** | Worker failures if coder missing | Pre-flight checks, error handling |
| **Job State Schema Drift** | Compatibility issues | Migration functions, version checks |
| **Daemon Child Process Failure** | Orphaned jobs | Heartbeat monitoring, timeout handling |

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Windows Path Handling** | Path resolution failures | `_safe_relative_to()` helper |
| **Placeholder Resolution Ordering** | Unresolved tokens | Centralized context builder |
| **Sidecar Corruption** | Invalid step results | Schema validation, checksums |
| **Bundle Version Mismatch** | Unexpected behavior | Version pinning, validation |

### Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Documentation Drift** | Stale documentation | Documentation sync workflow |
| **Workflow Complexity** | Steep learning curve | Comprehensive documentation |
| **Toolchain Dependency** | External tool changes | Abstraction layers, adapters |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 03_generate_system_overview_docs*
