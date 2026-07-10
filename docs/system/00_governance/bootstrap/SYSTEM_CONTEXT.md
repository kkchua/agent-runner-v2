---
template_id: "SYS-03-CTX"
title: "System Context - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:56:49+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context: agent-runner-v2

## Context Statement

The agent-runner-v2 system operates as a standalone Python LLM workflow orchestration engine that bridges human intent (via structured workflows) to LLM-powered execution and deterministic action outputs. It sits at the intersection of:

1. **Human users** who define initiatives, tasks, and requirements
2. **LLM backends** (Claude, Codex, Qwen) that perform intelligent work
3. **File system artifacts** that persist workflow state and outputs
4. **Optional backend services** that provide enterprise job management

The system is designed to operate standalone (local mode) or connected to a backend (enterprise mode), with the same core execution semantics in both configurations.

## Primary Context Elements

### External Actors

| Actor | Role | Interface |
|-------|------|-----------|
| **Developer** | Creates and debugs workflows | CLI (`ukbe-run-agent`), batch files |
| **Operator** | Runs daemon, monitors health | CLI (`daemon` command), logs |
| **Reviewer** | Reviews and approves step outputs | Markdown files, notifications |
| **Stakeholder** | Consumes documentation outputs | Generated HTML sites, markdown docs |

### System Actors

| Actor | Role | Interface |
|-------|------|-----------|
| **LLM Backend** | Performs AI-powered work | Subprocess invocation via `coder_adapters.py` |
| **Backend API** | Enterprise job queue and state | HTTP API via `backend_client.py` |
| **Notification Service** | Delivers alerts | Pushover API, console output |
| **File System** | Persists state and artifacts | Standard filesystem operations |

### External Systems

| System | Purpose | Integration Point |
|--------|---------|-------------------|
| **Anthropic Claude API** | LLM execution for coding tasks | `coder_adapters.py` → subprocess |
| **OpenAI Codex API** | LLM execution for coding tasks | `coder_adapters.py` → subprocess |
| **Alibaba Qwen** | LLM execution for coding tasks | `coder_adapters.py` → subprocess |
| **Pushover API** | Mobile push notifications | `notifications.py` → HTTP POST |
| **Backend Service** | Job queue and orchestration | `backend_client.py` → HTTP API |
| **Git** | Version control for artifacts | Shell commands via `subprocess` |

### System Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                        agent-runner-v2                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   CLI Entry │  │  Step       │  │   Workflow              │ │
│  │   (run_agent│→ │  Runner     │→ │   Router                │ │
│  │   .py)      │  │             │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│         │                │                    │                 │
│         ▼                ▼                    ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Bundle     │  │  Coder      │  │   Job State             │ │
│  │  Loader     │  │  Adapters   │  │   (job_state.py)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│         │                │                                      │
│         ▼                ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Runtime Context                        │  │
│  │              (paths, workflow module, etc.)               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐
│   Global    │  │   Project   │  │   LLM Backends              │
│   Runner    │  │   Root      │  │   (Claude, Codex, Qwen)    │
│   Home      │  │             │  │                             │
│   (~/.ukbe- │  │             │  │                             │
│   runner)   │  │             │  │                             │
└─────────────┘  └─────────────┘  └─────────────────────────────┘
```

### Data Stores

| Store | Purpose | Location |
|-------|---------|----------|
| **Job State** | Execution state per job | `~/.ukbe-runner/jobs/<job_id>/job.json` |
| **Workflow Bundles** | Workflow definitions | `~/.ukbe-runner/workflows/<workflow>/` |
| **Step Sidecars** | Step results and metadata | `<job_step_dir>/meta.json` |
| **Artifacts** | Generated documents, code | Project-local paths |
| **Logs** | Execution logs | `~/.ukbe-runner/logs/` |
| **Config** | Runner configuration | `~/.ukbe-runner/config.json` |

### Execution Contexts

| Context | Purpose | Trigger |
|---------|---------|---------|
| **Local Execution** | Development and testing | `ukbe-run-agent run` |
| **Worker Mode** | Single-step execution | `ukbe-run-agent worker` |
| **Daemon Mode** | Supervised continuous execution | `ukbe-run-agent daemon` |
| **Backend Mode** | Enterprise-managed execution | Backend claims work |

### Configuration Context

| Config | Scope | Source |
|--------|-------|--------|
| **Runner Config** | Global settings | `~/.ukbe-runner/config.json` |
| **Workflow Config** | Per-workflow settings | `workflow.toml` or `template_groups.py` |
| **Step Config** | Per-step settings | Step definition in workflow |
| **Environment** | Secrets and overrides | `.env` file, environment variables |

### Security Boundaries

| Boundary | Protection |
|----------|------------|
| **Credential Storage** | `.env` files excluded from Git |
| **Job State Isolation** | Per-job directories |
| **Subprocess Isolation** | Fresh process per step |
| **File System Access** | Project-root-relative paths only |

---

*Last updated: 2026-07-10T19:56:49+08:00 via workflow `00_master_docs_bootstrap_v2`*
