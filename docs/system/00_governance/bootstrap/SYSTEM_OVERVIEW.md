---
title: "System Overview"
template_id: "SYS-00-SO"
status: "active"
managed_by: workflow-generated
generated: "2026-07-02T00:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260702-005"
---

# System Overview

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

## What is agent-runner-v2?

**agent-runner-v2** is a standalone Python LLM workflow orchestration engine that enables structured, multi-step execution of complex tasks using large language models (Claude, Codex, Qwen, and aliased models).

It provides:

- **Workflow orchestration** — Multi-step execution with state management
- **Review loops** — Built-in review, refinement, and replanning cycles
- **Approval gates** — Human-in-the-loop decision points
- **Deterministic actions** — Reliable, reproducible repository operations
- **Backend integration** — Optional backend-connected worker mode

## The Problem It Solves

Building LLM-powered automation typically requires:

- Managing conversation context across multiple steps
- Handling retry logic and failure recovery
- Tracking state and artifacts
- Implementing review and approval workflows
- Integrating with multiple LLM providers

agent-runner-v2 solves these challenges by providing a **structured execution framework** with clear contracts between steps.

## Core Concepts

### Workflows

A workflow is a directed graph of steps that transforms inputs into outputs through LLM invocations.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Step 1    │───→│   Step 2    │───→│   Step 3    │
│  (Planner)  │    │  (Review)   │    │ (Executor)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                    │
       └──────────────┬───────────────────────┘
                  (Loop back)
```

### Steps

Each step:

1. Loads the active workflow bundle
2. Renders a prompt from the template
3. Invokes a coder (Claude, Codex, Qwen)
4. Reads a `meta.json` sidecar written by the step
5. Validates artifacts
6. Routes to the next step

### The v2 Contract

Key v2 architectural principles:

1. **meta.json Sidecar is the ONLY Channel**
   - All structured results flow through `meta.json` sidecars
   - No stdout parsing, no markdown write-backs

2. **No Silent Recovery**
   - Hard failures route explicitly through `route_after_failure()`
   - Clear failure classification (AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, FATAL)

3. **Deterministic Actions**
   - All file/system operations go through action modules in `actions/`
   - Reproducible, testable behavior

## Execution Modes

### 1. Local Execution

```bash
ukbe-run-agent run --workflow 30_delivery_planning_v1 --input-file plan.md
```

Manual workflow execution with job state tracking. Ideal for development and testing.

### 2. Backend Worker Mode

```bash
ukbe-run-agent worker
ukbe-run-agent poll
ukbe-run-agent execute-step
```

Backend-connected single-step execution. The worker polls for work and executes steps.

### 3. Daemon Supervisor

```bash
ukbe-run-agent daemon
```

Workstation supervisor for managed execution. Monitors and manages worker processes.

## Value Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUTS                                  │
│  Initiative  │  Bug Report  │  Documentation Gap  │  Task      │
└──────────────┴──────────────┴─────────────────────┴─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WORKFLOW ORCHESTRATION                          │
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   Intake    │───→│   Planning  │───→│  Execution  │        │
│   │             │    │             │    │             │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                    │                   │              │
│         └────────────────────┴───────────────────┘              │
│                              │                                   │
│                              ▼                                   │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │              REVIEW & VALIDATION LOOPS                    │  │
│   │   (Review → Refine → Replan → Approve → Execute)        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUTS                                     │
│  Plans  │  Code  │  Documentation  │  Validation Reports         │
└─────────┴────────┴─────────────────┴────────────────────────────┘
```

## Key Capabilities

### Multi-Model Support

- **Claude** (Anthropic) — Complex reasoning, code generation
- **Codex** (OpenAI) — Code-focused tasks
- **Qwen** (Alibaba) — General-purpose coding assistant
- **Aliased models** — Configurable model mappings

### State Management

- Job state persisted in `job.json` (schema v6)
- Step-level state tracking
- Artifact management
- Retry history
- Usage tracking

### Review & Refinement

- Automatic review steps
- Human approval gates
- Refinement loops
- Replanning on failure
- Convergence detection

### Action System

Deterministic actions for:

- Artifact promotion and copying
- Documentation syncing
- Validation
- Video/media assembly
- ComfyUI submission

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI ENTRY                               │
│                     (run_agent.py)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ORCHESTRATION                        │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │  Step Runner│  │    Router   │  │  Job State  │             │
│   │(step_runner)│  │(workflow_  │  │(job_state)  │             │
│   │             │  │  router.py) │  │             │             │
│   └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │   Coders    │  │   Actions   │  │   Runtime   │             │
│   │(coder_      │  │(actions/)   │  │  Context    │             │
│   │ adapters.py)│  │             │  │(runtime_    │             │
│   │             │  │             │  │ context.py)│             │
│   └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL INTERFACES                          │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │   Claude    │  │    Codex    │  │    Qwen     │             │
│   │   (API)     │  │    (API)    │  │   (API)     │             │
│   └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐                             │
│   │   Backend   │  │   ComfyUI   │                             │
│   │   (HTTP)    │  │   (HTTP)    │                             │
│   └─────────────┘  └─────────────┘                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Target Users

| User Type | Use Case |
|-----------|----------|
| **AI Engineers** | Build and deploy LLM-powered workflows |
| **DevOps/SRE** | Automate documentation, validation, and deployment |
| **Project Managers** | Track initiative intake through delivery |
| **Content Creators** | Video/media generation workflows |
| **Developers** | Bug fix automation, code scaffolding |

## Integration Points

- **CLI** — Primary interface
- **Backend API** — Optional HTTP backend
- **ComfyUI** — Video/image generation
- **File System** — Artifact storage
- **Environment** — Configuration via env vars

## Getting Started

```bash
# Install
pip install -e "."

# Initialize runner home
ukbe-run-agent init

# Run a workflow
ukbe-run-agent run --workflow 30_delivery_planning_v1 --input-file plan.md
```

## Related Documentation

- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Operational value
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Detailed behaviors
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality attributes
- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Workflow structure

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs`*
