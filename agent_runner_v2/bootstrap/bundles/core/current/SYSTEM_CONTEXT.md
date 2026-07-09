---
template_id: "SYS-03-CTX"
managed_by: workflow-generated
generated: "2026-07-09T21:26:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context

## Context Statement

agent-runner-v2 is a standalone Python LLM workflow orchestration engine that operates within a larger ecosystem of AI-assisted software development tools. It serves as the execution runtime for structured multi-step workflows, bridging human intent (expressed through initiatives, bug reports, or direct invocation) with AI-powered implementation via external coder tools (Claude Code, Codex CLI, Qwen Code).

The system exists at the intersection of:
- **Human operators** who define work through initiatives and approve/reject step outcomes
- **AI coders** that execute implementation steps and produce artifacts
- **Backend systems** that manage work distribution and track execution state
- **Documentation systems** that maintain codebase and delivery governance

## Primary Context Elements

### Business Context

**Purpose**: Enable deterministic, repeatable, and reviewable AI-assisted software delivery through structured workflows.

**Value Proposition**:
- Reduces cognitive load by encoding best practices into workflow templates
- Ensures consistent artifact generation and validation across projects
- Provides audit trail through job state and step history
- Enables parallel execution across distributed workstations

**Stakeholders**:
| Stakeholder | Concern | Interaction |
|-------------|---------|-------------|
| Developers | Implement features, fix bugs | Invoke workflows, review step outputs |
| Tech Leads | Ensure quality and consistency | Approve/reject steps, configure workflows |
| Operators | Maintain runtime health | Monitor daemon, review logs |
| Backend Systems | Distribute work, track state | Queue jobs, receive results |

### Technical Context

**Runtime Environment**:
- Python 3.12+ (primary development target)
- Windows (primary platform) with cross-platform compatibility
- User home directory for runner state (`%USERPROFILE%\.ukbe-runner`)

**External Dependencies**:
| Dependency | Purpose | Integration |
|------------|---------|-------------|
| Claude Code | AI coding assistant | CLI invocation via `claude` |
| Codex CLI | OpenAI coding assistant | CLI invocation via `codex` |
| Qwen Code | Qwen coding assistant | CLI invocation via `qwen` |
| Backend API | Work distribution | HTTP REST API |

**Data Stores**:
| Store | Location | Purpose |
|-------|----------|---------|
| Job State | `~/.ukbe-runner/jobs/` | Workflow execution state |
| Workflow Bundles | `~/.ukbe-runner/workflows/` | Runtime workflow definitions |
| Logs | `~/.ukbe-runner/logs/` | Execution logs and events |
| Config | `~/.ukbe-runner/config.json` | Runtime configuration |

### Execution Context

**Workflow Execution Model**:
```
Job → Step → Prompt → Coder/Action → Artifacts → Sidecar → Route
```

Each workflow execution:
1. Creates a job with unique ID under `jobs/<workflow>/<job_id>/`
2. Executes steps sequentially, with each step having its own working directory
3. Produces artifacts written to disk
4. Reports results via `meta.json` sidecar
5. Routes to next step based on approval/rejection status

**State Management**:
- Job state persisted to `job.json` with schema version 6 (v2)
- Step results tracked in `retry_history` array
- Artifact paths accumulated in `artifacts` dictionary
- Review decisions recorded per artifact type

**Failure Handling**:
- Control classes: `AUTO_RETRYABLE`, `HUMAN_RETRY_REQUIRED`, `FATAL`
- Retry limits enforced per step configuration
- Failure history maintained for operational visibility

### Documentation Context

**Documentation Domains**:
| Domain | Location | Purpose |
|--------|----------|---------|
| System Docs | `docs/system/` | Platform-level documentation |
| Codebase Docs | `docs/codebase/` | Implementation documentation |
| Delivery Docs | `docs/delivery/` | Project work tracking |
| Bootstrap Bundle | `agent_runner_v2/bootstrap/` | Package seed documentation |

**Generated Document Protection**:
- Workflow-generated docs carry `managed_by: workflow-generated` frontmatter
- Protected from manual edits with explicit banner
- Manifest tracked in `documentation_guardrails.py`
- Regenerated via `documentation_sync_v1` workflow

### Operational Context

**Deployment Patterns**:
- **Local Development**: Direct CLI invocation with manual workflow selection
- **Backend-Connected**: Worker mode polling backend for work
- **Daemon Mode**: Supervisor process managing child step execution

**Monitoring**:
- Job status queryable via `ukbe-run-agent status <job_id>`
- Daemon emits heartbeats keyed by `workflow_step_run_id`
- Child process state tracked via JSONL event logs
- Pushover notifications for step completion/failure (if configured)

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 04_generate_architecture_docs*
