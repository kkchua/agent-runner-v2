---
template_id: "SYS-03-CTX"
title: "System Context"
status: "active"
generated: "2026-07-04T14:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context

## Context Statement

The `agent-runner-v2` platform operates as a workflow orchestration engine that bridges human intent (via workflow definitions) with LLM execution (via coder adapters) and artifact management (via the runtime bundle system).

## Primary Context Elements

### External Actors

| Actor | Role | Interaction Pattern |
|-------|------|---------------------|
| **Developer** | Local workflow execution and debugging | CLI invocation, job inspection, retry operations |
| **Operator** | Production worker supervision | Daemon management, log monitoring, incident response |
| **Workflow Author** | Creates and maintains workflow definitions | Edits template_groups.py and prompt templates |
| **Backend System** | External work distribution system | REST API for work claiming and result submission |
| **LLM Providers** | Claude, Codex, Qwen API endpoints | HTTP requests with retry and timeout handling |
| **File System** | Artifact storage and job state persistence | Atomic writes, path resolution, bundle management |

### External Systems

| System | Purpose | Interface |
|--------|---------|-----------|
| **Claude API** | Anthropic LLM inference | HTTP REST via `coder_adapters.py` |
| **Codex API** | OpenAI Codex inference | HTTP REST via `coder_adapters.py` |
| **Qwen API** | Qwen Code inference | HTTP REST via `coder_adapters.py` |
| **Backend Server** | Distributed work coordination | REST API via `backend_client.py` |
| **Runner Home** | Global runtime bundle storage | File system at `%USERPROFILE%\.ukbe-runner\` |

### Information Flows

#### Flow 1: Local Execution Context

```
Developer (CLI)
    ↓
ukbe-run-agent run <workflow>
    ↓
Load workflow bundle from ~/.ukbe-runner/workflows/
    ↓
Render prompt → Invoke Coder → Read meta.json
    ↓
Validate artifacts → Route to next step
    ↓
Update job.json → Continue or complete
```

#### Flow 2: Worker Mode Context

```
Backend Server
    ↓
Daemon polls via backend_client
    ↓
Claim work → Spawn execute-step subprocess
    ↓
Child process runs step → Submits result
    ↓
Backend receives structured result
    ↓
Daemon continues polling
```

#### Flow 3: Bootstrap/R Runtime Context

```
Packaged Bootstrap (repo)
    ↓
ukbe-run-agent init
    ↓
Copy to ~/.ukbe-runner/workflows/
    ↓
Runtime Bundle (global)
    ↓
Workflow execution loads from runtime
```

### Context Boundaries

| Boundary | Inside | Outside |
|----------|--------|---------|
| **Platform Boundary** | Workflow orchestration, job state, routing | LLM provider implementations, backend server |
| **Runtime Boundary** | Job execution, artifact validation, step routing | Workflow definition authoring, prompt template design |
| **Repository Boundary** | Packaged bootstrap, source code, tests | Global runner home, job directories, logs |
| **Contract Boundary** | meta.json sidecar validation, artifact existence | Content validation, semantic correctness |

### Domain Context

The platform sits at the intersection of three domains:

1. **Workflow Domain**: Template groups, steps, routing configuration
2. **Execution Domain**: Coder invocation, action execution, result processing
3. **Artifact Domain**: File generation, path resolution, document lifecycle

### Constraints and Assumptions

| Constraint | Rationale |
|------------|-----------|
| Sidecar-only communication | Deterministic, auditable, machine-parseable |
| No markdown write-backs | Separation of concerns - runner orchestrates, coders generate |
| Hard failures on schema violations | Fail fast, explicit recovery paths |
| Runtime bundle precedence | Allows local workflow customization without source changes |
| Atomic file operations | Prevent partial writes during concurrent execution |

---

*This context document describes the external boundaries of agent-runner-v2. See COMPONENT_ARCHITECTURE.md for internal component relationships.*
