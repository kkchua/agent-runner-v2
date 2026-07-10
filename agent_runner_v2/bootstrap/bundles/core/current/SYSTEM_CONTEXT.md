---
template_id: "SYS-03-CTX"
title: "System Context - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:52:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context: agent-runner-v2

## Context Statement

The agent-runner-v2 is a standalone Python LLM workflow orchestration engine that executes structured multi-step workflows across multiple AI models (Claude, Codex, Qwen) with review loops, retries, approval gates, and deterministic runner actions. It operates as a bridge between human intent and AI execution, providing a governed delivery framework for software development tasks.

## Primary Context Elements

### External Systems

| System | Interface | Direction | Purpose |
|--------|-----------|-----------|---------|
| **Claude API** | HTTP/API | Outbound | Primary LLM for complex reasoning tasks |
| **Codex API** | HTTP/API | Outbound | Code generation and implementation |
| **Qwen Code** | Local/IPC | Inbound/Outbound | Local agent execution and tool integration |
| **Backend API** | HTTP/WebSocket | Bidirectional | Job state persistence and event streaming |
| **Pushover** | HTTP/API | Outbound | Notification delivery for step completion |
| **File System** | OS/Filesystem | Bidirectional | Artifact storage and job state |
| **Git** | CLI/Subprocess | Bidirectional | Repository operations and change tracking |
| **ComfyUI** | HTTP/API | Outbound | Image generation pipeline |
| **VideoXpress** | HTTP/API | Outbound | Video generation pipeline |

### External Data Sources

| Source | Format | Usage |
|--------|--------|-------|
| **Workflow Bundles** | Python modules + JSON | Runtime workflow definitions |
| **Prompt Templates** | Text files | Step prompt rendering |
| **Job State** | JSON | Execution state persistence |
| **Meta.json Sidecars** | JSON | Step result communication |
| **Environment Config** | .env / JSON | Credential and configuration |

### Users and Stakeholders

| Role | Interaction | Concerns |
|------|-------------|----------|
| **Developers** | CLI, batch files | Workflow execution, task implementation |
| **Operators** | Daemon mode, logs | System monitoring, failure handling |
| **Reviewers** | Review files, approvals | Quality gates, decision authority |
| **Stakeholders** | Architecture site | Understanding system capabilities |

### System Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                    agent-runner-v2 System Boundary                   │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   CLI Entry  │  │ Step Runner  │  │   Router     │               │
│  │  run_agent.py │  │ step_runner  │  │workflow_router│               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                  │                  │                      │
│  ┌──────▼──────────────────▼──────────────────▼───────┐               │
│  │              Job State Manager                   │               │
│  │                 job_state.py                     │               │
│  └──────────────────────────────────────────────────┘               │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   Actions    │  │   Adapters   │  │  Templates   │               │
│  │   (29)       │  │  (3 coders)  │  │  (290+ steps)│               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└───────┬───────────────────────────────────────────────┬───────────────┘
        │                                               │
   ┌────▼────┐                                     ┌───▼────┐
   │  LLMs   │                                     │Backend │
   └─────────┘                                     └────────┘
```

### Data Flow

1. **Initiation**: CLI receives command → loads workflow bundle → creates job state
2. **Execution**: Step runner renders prompt → invokes coder/action → validates artifacts
3. **Routing**: Workflow router evaluates result → advances step or triggers retry/replan
4. **Persistence**: Job state saved to JSON → events streamed to backend
5. **Notification**: Completion events trigger notifications via Pushover

### Trust Boundaries

| Boundary | Inside | Outside | Trust Model |
|----------|--------|---------|-------------|
| **Runner Core** | run_agent, step_runner, job_state | External LLMs | Runner validates all outputs |
| **Coder Invocation** | step_runner, adapters | Claude/Codex APIs | API keys, response validation |
| **Job State** | JSON files, backend | File system | Local FS + backend sync |
| **Artifact Storage** | docs/, jobs/ | Git repo | Version controlled |

### Integration Points

#### Backend Integration
- **Protocol**: WebSocket for events, HTTP for API calls
- **Authentication**: API key from environment
- **Data**: Job creation, step execution, artifact submission
- **Resilience**: Retry with backoff, graceful degradation

#### LLM Integration
- **Protocol**: HTTP REST APIs
- **Models**: Claude 4, Codex, Qwen aliases
- **Pattern**: Prompt → Invocation → Sidecar response
- **Validation**: Meta.json schema, artifact existence

#### Notification Integration
- **Protocol**: HTTP POST to Pushover API
- **Triggers**: Step completion, failures, approvals
- **Content**: Workflow name, step name, duration, status

### Deployment Context

| Environment | Runtime Mode | Backend Connection |
|-------------|--------------|-------------------|
| **Local Dev** | `ukbe-run-agent run` | Optional |
| **Workstation** | `ukbe-run-agent daemon` | Required |
| **CI/CD** | `ukbe-run-agent execute-step` | Required |
| **Backend Worker** | `ukbe-run-agent worker` | Required |

### Configuration Context

```
%USERPROFILE%\.ukbe-runner/
├── config.json           # Runner configuration
├── jobs/                 # Job state persistence
│   └── {workflow}/
│       └── {job_id}/
│           └── job.json
├── workflows/            # Runtime workflow bundles
│   └── default/
│       ├── template_groups.py
│       ├── prompts/
│       └── ...
└── logs/                 # Execution logs
```

### Security Context

| Asset | Protection | Mechanism |
|-------|------------|-----------|
| API Keys | Environment | `.env` file, not committed |
| Job State | File permissions | User-owned directories |
| Artifacts | Git + Review | PR review, approval gates |
| Credentials | Runtime only | Loaded at startup, not logged |

### Regulatory Context

This system operates as a development tool with the following considerations:
- Generated code requires human review before production
- LLM usage subject to provider terms of service
- Audit trail maintained in job state and git history
- No PII handling in workflow artifacts

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs` on 2026-07-10T09:52:38+08:00*
