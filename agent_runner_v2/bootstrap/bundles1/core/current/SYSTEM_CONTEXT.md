---
template_id: "SYS-03-CTX"
title: "System Context - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:26:47+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context: agent-runner-v2

## Context Statement

agent-runner-v2 is a standalone Python-based workflow orchestration engine that executes structured multi-step LLM workflows. It serves as the local execution runtime for the UKBE (UK Business Engine) workflow system, providing deterministic step execution with artifact validation, review loops, and explicit failure routing.

The system operates in a **workstation-centric context** — the primary execution environment is a developer workstation with optional backend coordination for distributed workflows.

## Primary Context Elements

### External Systems

| System | Interface | Purpose | Integration Pattern |
|--------|-----------|---------|---------------------|
| **LLM Providers** | Subprocess invocation (Claude/Codex/Qwen) | Code generation and reasoning | Adapter pattern via `coder_adapters.py` |
| **Backend API** | HTTP/WebSocket (`backend_client.py`) | Job distribution and status reporting | Optional; system works standalone |
| **Pushover** | HTTPS API | Push notifications for workflow events | Configured via `.env` credentials |
| **Git** | CLI subprocess | Version control and diff generation | Local git operations only |
| **ComfyUI** | HTTP API | Image/video generation for content workflows | Optional; content workflows only |

### Runtime Environment

| Element | Location | Purpose |
|---------|----------|---------|
| **Runner Home** | `%USERPROFILE%\.ukbe-runner\` | Global state, configs, jobs, logs |
| **Workflow Bundles** | `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\` | Runtime workflow definitions and prompts |
| **Job State** | `%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\` | Per-job state, sidecars, artifacts |
| **Logs** | `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs and diagnostics |
| **Package Root** | Repository `agent_runner_v2/` | Bootstrap source, CLI entry point |
| **Target Project** | Configurable `--target-project-root` | Where generated artifacts are written |

### Configuration Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                     WORKSTATION                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              agent-runner-v2 (Package)             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │   │
│  │  │  Bootstrap  │  │   Actions   │  │   CLI    │   │   │
│  │  │   Source    │  │  (25+ mod)  │  │  Entry   │   │   │
│  │  └─────────────┘  └─────────────┘  └──────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Global Runner Home (~/.ukbe-runner)      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │   │
│  │  │   Config    │  │  Workflows  │  │   Jobs   │   │   │
│  │  │ config.json │  │  (runtime)  │  │  (state) │   │   │
│  │  └─────────────┘  └─────────────┘  └──────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Target Project Workspace                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │   │
│  │  │    docs/    │  │   Delivery  │  │  Source  │   │   │
│  │  │   output    │  │  artifacts  │  │   code   │   │   │
│  │  └─────────────┘  └─────────────┘  └──────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                        │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐           │
│  │    LLMs     │  │   Backend   │  │ Pushover │           │
│  │ Claude/Codex│  │    (opt)    │  │(opt)     │           │
│  └─────────────┘  └─────────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

#### CLI Interface (`ukbe-run-agent`)

The primary external interface is the CLI entry point supporting six execution modes:

| Mode | Purpose | Context |
|------|---------|---------|
| `init` | Initialize runner home with config and workflow bundles | One-time setup |
| `run` | Local workflow execution with full job state management | Development |
| `poll` | Backend-connected single-step execution | Backend worker |
| `worker` | Alias for poll mode with worker-specific logging | Backend worker |
| `daemon` | Workstation supervisor for continuous operation | Production |
| `execute-step` | Direct step execution for spawned subprocesses | Internal |

#### Artifact Contract

The system communicates with LLM coders through a strict artifact contract:

1. **Input**: Prompt rendered from templates with artifact placeholders
2. **Processing**: LLM writes artifact files to disk
3. **Output**: `meta.json` sidecar with status, remark, and artifact list
4. **Routing**: Runner reads sidecar and routes to next step based on status

### Security Boundaries

| Boundary | Protection Mechanism |
|----------|---------------------|
| **Credential Storage** | `.env` file in project root (gitignored) |
| **Job Isolation** | Each job has dedicated directory with restricted access |
| **Subprocess Sandboxing** | Fresh Python process per step (implicit isolation) |
| **Backend Auth** | Token-based authentication via config |

### Failure Domains

| Domain | Impact | Mitigation |
|--------|--------|------------|
| **Sidecar Missing** | Step stalls, requires retry | Explicit failure routing; no silent recovery |
| **Job State Corruption** | Job unrecoverable | Schema versioning with migration on load |
| **LLM Provider Failure** | Step fails | Retry with backoff; fallback to alternative models |
| **Backend Disconnection** | Daemon falls back to local mode | Graceful degradation; local execution continues |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 04_generate_architecture_docs | Change: 00DOC-20260708-78fb419e*
