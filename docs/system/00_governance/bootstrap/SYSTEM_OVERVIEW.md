---
template_id: "SYS-00-SO"
title: "System Overview - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# System Overview: agent-runner-v2

## Purpose

This document explains the agent-runner-v2 platform at a level useful to users, developers, and stakeholders. It describes the workflow model, value flow, and runtime architecture without drifting into low-level implementation detail.

## Scope

This overview covers:
- Platform purpose and positioning
- Core workflow execution model
- Primary usage modes
- Value flow through the system
- Architecture profile and posture
- Key operational risks

## Primary Flows

### Execution Model Overview

Each workflow step follows a deterministic sequence:

```
1. Load workflow bundle
       ↓
2. Render prompt from template
       ↓
3. Invoke coder or action
       ↓
4. Read meta.json sidecar
       ↓
5. Validate artifacts
       ↓
6. Route to next step
```

### Core Components

| Component | Responsibility |
|-----------|---------------|
| **CLI Entry** (`run_agent.py`) | Command parsing and orchestration |
| **Step Runner** (`step_runner.py`) | Prompt rendering, execution, validation |
| **Workflow Router** (`workflow_router.py`) | Post-step routing decisions |
| **Job State** (`job_state.py`) | Job.json lifecycle management |
| **Bundle Loader** (`bundle_loader.py`) | Workflow bundle discovery and loading |
| **Coder Adapters** (`coder_adapters.py`) | LLM invocation and polling |
| **Runtime Context** (`runtime_context.py`) | Active workflow/runtime path context |

### Primary Usage Modes

#### 1. Local Workflow Execution

Manual execution for development and testing:

```bash
ukbe-run-agent run --template-group delivery_planning_v1 \
  --set INIT_FILE=docs/delivery/01_initiatives/INIT-example.md
```

**Characteristics**:
- Self-contained execution
- Local file system for artifacts
- Manual artifact management
- Interactive debugging

#### 2. Backend-Connected Worker

Production execution connected to backend:

```bash
ukbe-run-agent worker --backend-url http://127.0.0.1:8100 \
  --worker-id kode-worker-01
```

**Characteristics**:
- Polls backend for work
- Submits results to backend
- Backend is source of truth
- Daemon supervises execution

#### 3. Workstation Supervision (Daemon)

Long-running supervisor process:

```bash
ukbe-run-agent daemon kode-worker-01 \
  --backend-url http://127.0.0.1:8100
```

**Characteristics**:
- Claims work from backend
- Spawns child processes for steps
- Tracks child state
- Emits heartbeats
- Handles failures

### Workflow Step Types

#### Coder Steps

- **Execution**: Subprocess to LLM (Claude, Codex, Qwen)
- **Output**: Written by LLM
- **Validation**: Artifact existence + content validation
- **Retry**: Configurable with backoff

#### Action Steps

- **Execution**: In-process Python call
- **Output**: Written by action code
- **Validation**: Same as coder steps
- **Deterministic**: No LLM involvement

### Sidecar Contract (v2)

The `meta.json` sidecar is the **only** structured result channel:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED|REJECTED",
    "remark": "Human-readable summary",
    "artifacts": {
      "ARTIFACT_KEY": "relative/path/to/file.md"
    },
    "recorded_at": "2026-07-10T19:47:28+08:00"
  }
}
```

**Key rules**:
- `meta.json` is mandatory — missing sidecar = hard failure
- No markdown write-backs by the runner
- Artifact paths are relative to project root
- Runner enriches sidecar with timing and checksums

### Routing Model

Post-step routing supports:

| Status | Behavior |
|--------|----------|
| **approve** | Step accepted, advance to next |
| **reject** | Step rejected, route to refine/replan |
| **failure** | Hard failure, explicit failure handling |
| **waiting** | Await external input |

Review/refine loops enforce `max_rejects` limits before escalating to replan.

## Value Flow

### User Value Proposition

1. **Structured Workflows**: Multi-step workflows with review loops and gates
2. **LLM Abstraction**: Unified interface across Claude, Codex, Qwen
3. **Deterministic Actions**: Reliable, repeatable action execution
4. **Documentation-First**: Self-documenting with drift detection
5. **Operational Visibility**: Job tracking, logging, notifications

### Value Chain

```
User Intent (initiative, bug fix, task)
    ↓
Workflow Selection (delivery_planning_v1, bug_fix_intake_v1)
    ↓
Prompt Rendering (context + template)
    ↓
Execution (coder or action)
    ↓
Validation (artifact existence, content checks)
    ↓
Routing (approve/reject/failure)
    ↓
Deliverable (document, code, validated artifact)
```

## Architecture Profile

### Universal Baseline

Every repository in the ecosystem shares:

- **v2 sidecar contract**: Meta.json as only result channel
- **Deterministic artifact paths**: Centralized constants
- **Workflow bundle system**: Runtime loading from global home
- **Documentation governance**: Generated docs with validation

### Repo-Selected Profile

**Current Profile**: `provisional`

**Characteristics**:
- Active plugin system migration in progress
- Documentation being bootstrapped
- Some architectural gaps exist
- Test coverage exists, comprehensive verification ongoing

**Target Profile**: `explicit`

**Characteristics**:
- All modules documented
- Architecture decisions recorded
- Operational procedures defined
- Validation automated

### Migration Posture

**Migration Mode**: `in_progress`

**Current Migration**: Plugin workflow system replacing monolithic TEMPLATE_GROUPS

**Evidence**:
- Active branch `feat/plugin-workflow-system`
- Modified `template_groups.py`
- New `workflow_packages/` module
- Dual-path discovery implemented

**Posture Assessment**: The repository is in provisional state because:
1. Active migration in progress
2. Bootstrap vs runtime distinction requires careful sync
3. Documentation being established
4. Test coverage verification ongoing

## Key Risks

### 1. Bootstrap/Runtime Sync Risk

**Risk**: Changes to bootstrap workflow files may not propagate to global runtime bundles.

**Impact**: Runtime executes stale workflow definitions.

**Mitigation**:
- `sync_workflows.py` provides two-tier discovery
- Documented sync requirements
- CI validation

### 2. Meta.json Contract Violation

**Risk**: LLM backends may not write valid meta.json sidecars.

**Impact**: Hard failures with no silent recovery.

**Mitigation**:
- Prompt templates include explicit sidecar instructions
- Validation schema enforced
- Clear error messages

### 3. Path Resolution Complexity

**Risk**: Multiple path resolution layers may drift or conflict.

**Impact**: Incorrect artifact paths, validation failures.

**Mitigation**:
- Centralized constants in `constants.py`
- Zero hardcoded paths
- Layered constant system

### 4. Plugin Compatibility

**Risk**: Plugin bundles may not match expected schema.

**Impact**: Runtime errors, workflow failures.

**Mitigation**:
- Adapter validation
- Schema enforcement at load time
- Backward compatibility

### 5. Windows-Specific Issues

**Risk**: Path manipulation on Windows may hit edge cases.

**Impact**: Cross-platform incompatibility.

**Mitigation**:
- Recent pathlib fixes applied
- Cross-platform testing
- Clear path handling conventions

## Operational Model

### Initialization

```bash
ukbe-run-agent init
```

Seeds global runner home with:
- `config.json` — runner configuration
- `workflows/` — workflow bundles
- `jobs/` — job storage
- `logs/` — execution logs

### Execution Lifecycle

1. **Job Creation**: `job.json` created in `jobs/<job_id>/`
2. **Step Execution**: Spawn subprocess for each step
3. **Result Collection**: Read `meta.json` from step
4. **State Update**: Update `job.json` with results
5. **Routing**: Determine next step based on status
6. **Completion**: Finalize job, emit notifications

### Runtime Source of Truth

| Source | Purpose |
|--------|---------|
| **Backend** | Runs, step runs, artifacts, events, approvals |
| **Global Runner Home** | Workflow bundles, job state, logs |
| **Repository** | Source code, project-local plugins |
| **Bootstrap** | Seeds global home at init time |

## Related Documents

- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Operational capabilities
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Core behaviors
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality expectations
- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Bundle organization
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Migration posture

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
