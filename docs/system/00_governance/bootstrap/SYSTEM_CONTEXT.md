---
template_id: "SYS-03-CTX"
title: "System Context - agent-runner-v2"
status: "active"
generated: "2026-07-10T14:20:05+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context

## Context Statement

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine that executes structured multi-step workflows across Claude, Codex, Qwen, and aliased models. The system operates as a hybrid local/connected platform: it runs workflows locally using packaged bootstrap assets while optionally connecting to a backend service for distributed execution and job coordination.

## Primary Context Elements

### System Scope

| Element | Description |
|---------|-------------|
| **System Name** | agent-runner-v2 (UKBE Runner v2) |
| **System Type** | Workflow orchestration engine with LLM integration |
| **Execution Model** | Local-first with optional backend connectivity |
| **Primary Language** | Python 3.12+ |
| **Target Platforms** | Windows (primary), Unix/WSL (secondary) |

### External Systems

| System | Relationship | Interface | Protocol |
|--------|--------------|-----------|----------|
| **Anthropic Claude** | Coder backend | `coder_adapters.py` | HTTP REST API |
| **OpenAI Codex** | Coder backend | `coder_adapters.py` | HTTP REST API |
| **Alibaba Qwen** | Coder backend | `coder_adapters.py` | HTTP REST API |
| **UKBE Backend** | Optional job coordination | `backend_client.py` | HTTP/WebSocket |
| **Pushover** | Notification delivery | `notifications.py` | HTTPS API |
| **ComfyUI** | Image generation | `actions/submit_comfyui.py` | HTTP REST API |
| **File System** | Artifact storage | `step_runner.py`, `job_state.py` | Local I/O |

### System Boundaries

| Boundary | Inside | Outside |
|----------|--------|---------|
| **Execution Boundary** | Workflow steps, actions, job state | External coder APIs, user prompts |
| **Storage Boundary** | Local job files, runtime bundles, logs | Backend persistence, external services |
| **Network Boundary** | Optional backend polling, API calls | Internet-based coder services |
| **Configuration Boundary** | `%USERPROFILE%\.ukbe-runner\config.json` | Environment variables, `.env` files |

### Actors

| Actor | Role | Interaction Pattern |
|-------|------|---------------------|
| **Developer** | Uses runner for daily development tasks | CLI commands, batch files |
| **Workflow Author** | Creates and modifies workflow definitions | Template editing, prompt authoring |
| **Operator** | Monitors daemon and job execution | Logs, notifications, dashboard |
| **Backend System** | Coordinates distributed job execution | API polling, work claiming |
| **LLM Backend** | Executes coder steps | Synchronous API calls |

### Runtime Context

| Context Element | Location | Purpose |
|-----------------|----------|---------|
| **Runner Home** | `%USERPROFILE%\.ukbe-runner\` | Global configuration, jobs, workflows, logs |
| **Jobs Directory** | `%USERPROFILE%\.ukbe-runner\jobs\` | Job state files (`job.json`, step artifacts) |
| **Workflow Bundles** | `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\` | Runtime workflow definitions |
| **Logs Directory** | `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs and debug output |
| **Package Root** | `agent_runner_v2/` (repo) | Source code and bootstrap assets |
| **Bootstrap Source** | `agent_runner_v2/bootstrap/` | Packaged workflow seeds |

### Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CLI/Batch     │────▶│   run_agent.py   │────▶│   step_runner   │
│   Entry Point   │     │   Orchestration  │     │   Prompt Render │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                        │
                        ┌──────────────────┐             │
                        │   meta.json      │◀────────────┘
                        │   Sidecar        │    Invoke Coder/Action
                        │   (v2 Contract)  │
                        └────────┬─────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
     │   Claude    │     │   Codex     │     │   Action    │
     │   Backend   │     │   Backend   │     │   Handler   │
     └─────────────┘     └─────────────┘     └─────────────┘
```

### Key Interfaces

| Interface | Description | Contract |
|-----------|-------------|----------|
| **CLI Interface** | `ukbe-run-agent` commands | Subcommands: `run`, `worker`, `poll`, `daemon`, `init`, `execute-step` |
| **Step Contract** | Execution unit | Prompt template → Coder/Action → meta.json sidecar |
| **Sidecar Contract** | Result communication | JSON with `schema_version`, `coder_result` (status, remark, artifacts) |
| **Job State** | Persistence format | `job.json` with step history, artifacts, routing decisions |
| **Workflow Definition** | Template groups | `template_groups.py` or plugin `workflow.toml` |

### Environment Dependencies

| Dependency | Required For | Configuration |
|------------|--------------|---------------|
| **Python 3.12+** | Runtime execution | `.venv` virtual environment |
| **Anthropic API Key** | Claude coder steps | `.env` (`ANTHROPIC_API_KEY`) |
| **OpenAI API Key** | Codex coder steps | `.env` (`OPENAI_API_KEY`) |
| **Pushover Tokens** | Notifications | `.env` (`PUSHOVER_APP_TOKEN`, `PUSHOVER_USER_KEY`) |
| **Backend Endpoint** | Worker mode | `config.json` (`backend.url`) |

### Constraints

| Constraint | Impact |
|------------|--------|
| **Windows-centric batch files** | Unix/WSL support secondary |
| **Bootstrap/Runtime duality** | Changes require explicit sync |
| **v2 Sidecar contract** | No markdown write-backs, no silent recovery |
| **Monolithic template_groups.py** | Migration to plugin system in progress |
| **No automatic bundle sync** | Manual `init` required for updates |

### Related Documents

| Document | Purpose |
|----------|---------|
| [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) | Component breakdown and interactions |
| [SYSTEM_FILE_STRUCTURE.md](SYSTEM_FILE_STRUCTURE.md) | Repository organization |
| [RUNBOOK.md](RUNBOOK.md) | Operational procedures |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Development setup and workflows |
