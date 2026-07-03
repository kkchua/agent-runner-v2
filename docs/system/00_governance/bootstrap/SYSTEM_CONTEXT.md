---
template_id: "SYS-03-CTX"
title: "System Context - agent-runner-v2"
status: "active"
generated: "2026-07-04T10:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context

## Context Statement

Agent-runner-v2 is a standalone Python-based LLM workflow orchestration engine that operates within a local development workstation environment, interacting with external LLM providers and optional backend services to execute structured multi-step workflows.

The system boundary encompasses the Python package, runtime workflow bundles, job state persistence, and CLI entry points. External entities include LLM providers (Claude, Codex, Qwen), the filesystem, and an optional backend API for distributed execution.

## Primary Context Elements

### System Under Design

| Aspect | Description |
|--------|-------------|
| **Name** | agent-runner-v2 |
| **Type** | Python CLI application and library |
| **Scope** | LLM workflow orchestration with step-level routing |
| **Deployment** | Local workstation (Windows, macOS, Linux) |

### External Entities

| Entity | Role | Interface |
|--------|------|-----------|
| **LLM Providers** | Generate code/text outputs | CLI invocation via `claude`, `codex`, `qwen` commands |
| **Filesystem** | Store jobs, logs, artifacts, bundles | Standard file I/O via `pathlib` |
| **Backend API** | Queue and distribute work (optional) | HTTP REST API via `backend_client.py` |
| **User/Operator** | Initiate workflows, approve steps | CLI (`ukbe-run-agent`) |
| **Environment** | Configuration via env vars | `AGENT_RUNNER_*` variables |

### Data Flows

| Flow | Direction | Description |
|------|-----------|-------------|
| **Workflow Definition** | Internal → Runtime | Bootstrap templates copied to `~/.ukbe-runner/workflows/` |
| **Job State** | Internal ↔ Persistent | JSON read/write to `~/.ukbe-runner/jobs/<job-id>/job.json` |
| **Prompts** | Template → LLM | Rendered `.txt` files passed to coder adapters |
| **Results** | LLM → Internal | `meta.json` sidecar as structured result channel |
| **Artifacts** | Internal → Filesystem | Markdown, JSON, code files written to repo |
| **Backend Sync** | Optional bidirectional | Poll for work, submit results, heartbeats |

### System Boundary

**Inside Boundary:**
- Python package (`agent_runner_v2/`)
- CLI entry point (`ukbe-run-agent`)
- Runtime workflow bundles (loaded from disk)
- Job state management and persistence
- Deterministic action system
- Prompt rendering and template processing

**Outside Boundary:**
- LLM provider implementations (external processes)
- Backend API server (if used)
- Target project repositories (workflow inputs/outputs)
- Version control systems (git operations)
- User's development environment (IDEs, editors)

## Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     agent-runner-v2 System                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   CLI Layer  │  │ Step Runner  │  │   Workflow Router    │ │
│  │  run_agent   │──│  step_runner │──│   workflow_router  │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│         │                 │                      │            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Job State   │  │   Actions    │  │   Bundle Loader      │ │
│  │  job_state   │  │   actions/   │  │   bundle_loader      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│         │                 │                      │            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │Runtime Context│  │Coder Adapters│  │   Backend Client     │ │
│  │runtime_context│ │ coder_adapters│ │   backend_client     │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │Filesystem│      │  LLM     │      │ Backend  │
   │~/.ukbe- │      │ Providers│      │   API    │
   │runner/  │      │(Claude,  │      │(optional)│
   └─────────┘      │ Codex,   │      └──────────┘
                    │  Qwen)   │
                    └──────────┘
```

## Key Interfaces

### LLM Provider Interface

| Provider | Command | Timeout Config |
|----------|---------|--------------|
| Claude | `claude` | `coder_timeout_seconds` in step config |
| Codex | `codex` | `coder_timeout_seconds` in step config |
| Qwen | `qwen` | `coder_timeout_seconds` in step config |

**Contract:**
- Input: Prompt text via stdin or temp file
- Output: Results written to `meta.json` sidecar
- Exit code: 0 for success, non-zero for failure

### Backend API Interface

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/workflow-steps/available` | Poll for available work |
| `POST /api/v1/workflow-steps/{id}/claim` | Claim a step for execution |
| `POST /api/v1/workflow-steps/{id}/submit` | Submit step results |
| `POST /api/v1/workflow-steps/{id}/heartbeat` | Send heartbeat during execution |

**Authentication:** API key via `UKBE_API_KEY` environment variable.

### Filesystem Interface

| Path | Purpose |
|------|---------|
| `~/.ukbe-runner/config.json` | Global runner configuration |
| `~/.ukbe-runner/jobs/<job-id>/` | Job state, sidecars, logs |
| `~/.ukbe-runner/workflows/<workflow>/` | Runtime workflow bundles |
| `~/.ukbe-runner/logs/` | Execution logs |
| `<project-root>/` | Target repository for workflows |

## Assumptions and Constraints

### Assumptions

1. LLM providers are installed and available in PATH
2. User has write access to `~/.ukbe-runner/` directory
3. Python 3.11+ is available
4. Target project repositories are accessible

### Constraints

| Constraint | Rationale |
|------------|-----------|
| Single workstation focus | Designed for individual developer workflows, not multi-user coordination |
| Windows path handling | Some code paths have Windows-specific normalization |
| v2 meta.json contract | Strict sidecar schema, no backward compatibility for legacy formats |
| No silent recovery | Hard failures must be explicitly routed |
| No markdown write-backs | Runner does not modify markdown files (coders own content) |

## Related Documentation

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — System purpose and primary flows
- [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) — Detailed component design
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional capabilities
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality attributes

---

*Generated: 2026-07-04T10:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 04_generate_architecture_docs*
*Change ID: 00DOC-GEN-20260704-001*
