---
title: "System Context"
template_id: "SYS-03-CTX"
status: "active"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T11:57:31+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System Context: agent-runner-v2

## Context Statement

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine that executes structured multi-step workflows across multiple AI model backends (Claude, Codex, Qwen). It operates as a client-side runner that can function in three modes: manual workflow execution, backend-connected execution via daemon, and workstation supervision. The system maintains strict contracts around artifact generation, validation, and routing through explicit sidecar-based communication.

## Primary Context Elements

### External Systems

| System | Relationship | Protocol | Purpose |
|--------|--------------|----------|---------|
| **LLM Providers** (Claude, Codex, Qwen) | Outbound invocation | HTTP/API | Code generation, document creation, review |
| **Backend API** (optional) | Bidirectional | HTTP/REST | Job claims, step runs, artifact submission, events |
| **ComfyUI** (optional) | Outbound submission | HTTP/REST | Image/video generation for creative workflows |
| **Pushover** (optional) | Outbound notification | HTTP/API | User notifications for step completion/failure |
| **File System** | Local persistence | OS-native | Job state, artifacts, logs, runtime bundles |
| **Git Repository** | Workspace target | Git CLI | Code changes, documentation, version control |

### Users and Roles

| Role | Interaction Pattern | Primary Concern |
|------|---------------------|-----------------|
| **Software Engineers** | CLI (`ukbe-run-agent`), batch files | Task execution, code generation, documentation |
| **DevOps/Operators** | Daemon mode, runbooks | Monitoring, troubleshooting, job management |
| **Technical Leads** | Workflow configuration, governance | Standards compliance, process oversight |
| **Stakeholders** | HTML architecture site, markdown docs | Understanding capabilities, reviewing deliverables |

### Runtime Boundaries

| Boundary | Inside | Outside |
|----------|--------|---------|
| **Process** | Python runner, subprocess per step | Daemon supervisor, backend API |
| **Storage** | Job state in `~/.ukbe-runner/jobs/` | Runtime bundles in `~/.ukbe-runner/workflows/` |
| **Workspace** | Target project root (git repo) | Runner home (cross-project) |
| **Network** | LLM APIs, optional backend | User notification services |

### Data Flows

1. **Workflow Initiation**: User invokes CLI → runner loads workflow bundle → creates job state → begins step execution
2. **Step Execution**: Render prompt → invoke coder/action → read meta.json sidecar → validate artifacts → route next step
3. **Backend Integration** (optional): Daemon polls backend → claims work → spawns subprocess → reports results
4. **Documentation Governance**: Scan codebase → generate inventory → validate against templates → produce site

### Key Assumptions

- **Sidecar-Only Contract**: `meta.json` is the sole structured communication channel between runner and LLM
- **Subprocess Isolation**: Each step runs in a fresh subprocess, enabling code changes without restart
- **Filesystem as Source of Truth**: Job state persisted to JSON; artifacts as markdown files
- **Explicit Routing**: No silent recovery; failures route through explicit failure handlers
- **Declarative Protection**: Documents protected via `produces` lists, not imperative guards

### Risk Context

| Risk | Mitigation |
|------|------------|
| Runtime bundle drift | `init` command reseeds; sync batch files available |
| Windows path handling | Centralized `PurePosixPath` constants |
| Job state schema evolution | Backward compatibility functions in `job_state.py` |
| Notification context completeness | State normalization before dispatch |
