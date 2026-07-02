---
title: "Functional Specification"
template_id: "SYS-00-FS"
status: "active"
managed_by: workflow-generated
generated: "2026-07-02T00:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Functional Specification

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

## Overview

This document specifies the functional behaviors of agent-runner-v2. It describes what the system does and how it responds to inputs.

## Functional Areas

### 1. Workflow Execution

#### 1.1 Step Execution Flow

Each step follows this execution flow:

```
┌─────────────────────────────────────────────────────────────────┐
│                      STEP EXECUTION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

1. LOAD WORKFLOW BUNDLE
   └─→ Load template_groups.py from runtime bundle
   └─→ Resolve prompt template path

2. RENDER PROMPT
   └─→ Substitute context variables
   └─→ Compute prompt checksum

3. PREFLIGHT CHECKS
   └─→ Verify required artifacts exist
   └─→ Validate job state

4. INVOKE CODER
   └─→ Select coder based on configuration
   └─→ Send prompt to LLM
   └─→ Receive response

5. READ METa.JSON
   └─→ Parse sidecar file
   └─→ Validate against schema

6. VALIDATE ARTIFACTS
   └─→ Check artifact existence
   └─→ Verify paths

7. ROUTE NEXT STEP
   └─→ Determine next step based on result
   └─→ Update job state
```

#### 1.2 Job State Transitions

```
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
                           │ init
                           ▼
                    ┌─────────────┐
        ┌──────────→│ IN_PROGRESS │←──────────┐
        │           └──────┬──────┘           │
        │                  │                  │
   approve            complete           human retry
        │                  │                  │
        │           ┌──────┴──────┐           │
        └───────────│  COMPLETED  │───────────┘
                    └─────────────┘
                           │
                    fail / reject
                           ▼
              ┌────────────────────────┐
              │   WAITING_FOR_AUTO_    │
              │        RETRY           │
              └───────────┬────────────┘
                          │ auto-retry
                          ▼
                    ┌─────────────┐
                    │   FAILED    │
                    └─────────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   FATAL     │ │ HUMAN_RETRY │ │   retry     │
    │             │ │  REQUIRED   │ │   success   │
    └─────────────┘ └─────────────┘ └──────┬──────┘
                                           │
                                           └──────→ [back to IN_PROGRESS]
```

### 2. Review and Refinement

#### 2.1 Review Decision Flow

```
                    ┌─────────────┐
                    │   Review    │
                    │   Step      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │APPROVED │  │REJECTED │  │ NEEDS   │
        │         │  │         │  │ REPLAN  │
        └────┬────┘  └────┬────┘  └────┬────┘
             │            │            │
             ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │Advance  │  │Refine   │  │Replan   │
        │to Next  │  │Step     │  │Step     │
        └─────────┘  └─────────┘  └─────────┘
```

#### 2.2 Rejection Handling

| Reject Code | Meaning | Action |
|-------------|---------|--------|
| `VALIDATION_FAILED` | Output validation failed | Refine or replan |
| `INCOMPLETE` | Output incomplete | Refine |
| `INCORRECT` | Output incorrect | Refine or replan |
| `CONVERGENCE_FAILED` | Failed to converge after retries | Replan |

### 3. Coder Invocation

#### 3.1 Supported Coders

| Coder | Provider | Best For |
|-------|----------|----------|
| `claude` | Anthropic | Complex reasoning, code generation |
| `codex` | OpenAI | Code-focused tasks |
| `qwen` | Alibaba | General coding, refactoring |
| `claude-mini` | Anthropic | Cost-effective reasoning |

#### 3.2 Invocation Parameters

```python
{
    "coder": "claude",           # Coder alias
    "model": "claude-sonnet-4",  # Specific model
    "temperature": 0.0,          # Determinism
    "max_tokens": 8192,          # Output limit
    "timeout": 300,              # Seconds
}
```

### 4. Artifact Management

#### 4.1 Artifact Types

| Type | Extension | Purpose |
|------|-----------|---------|
| `plan` | `.md` | Delivery plans |
| `task_graph` | `.json` | Task dependencies |
| `task` | `.json` | Task definitions |
| `impl` | `.md` | Implementation specs |
| `review` | `.md` | Review outputs |
| `validation` | `.json` | Validation results |

#### 4.2 Artifact Lifecycle

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Created   │───→│   Active    │───→│   Archived  │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
      │                   │                  │
      │              ┌────┴────┐             │
      │              │         │             │
      │              ▼         ▼             │
      │         ┌────────┐ ┌────────┐       │
      │         │Promoted│ │Updated │       │
      │         └────────┘ └────────┘       │
      │                                     │
      └─────────────────────────────────────┘
```

### 5. Action System

#### 5.1 Deterministic Actions

Actions are deterministic repository operations:

| Action | Purpose |
|--------|---------|
| `assemble_video` | Assemble video from segments |
| `copy_artifact` | Copy artifacts between locations |
| `execute_i2v` | Execute image-to-video generation |
| `execute_t2i` | Execute text-to-image generation |
| `execute_voiceover` | Execute voiceover generation |
| `promote_artifact` | Promote artifact to active |
| `promote_init` | Promote initiative file |
| `submit_comfyui` | Submit job to ComfyUI |
| `validate_delivery_docs` | Validate delivery documentation |
| `validate_codebase_docs` | Validate codebase documentation |
| `validate_system_docs` | Validate system documentation |
| `sync_codebase_docs` | Sync codebase docs |
| `sync_system_docs` | Sync system docs |

#### 5.2 Action Contract

Each action:

1. Takes structured input
2. Performs deterministic operation
3. Returns structured output
4. Writes to `meta.json`

### 6. Validation

#### 6.1 Validation Types

| Type | Description |
|------|-------------|
| Schema Validation | Validate against JSON schema |
| Artifact Validation | Verify required artifacts exist |
| Content Validation | Check content meets criteria |
| Cross-reference Validation | Verify internal consistency |

#### 6.2 Validation Results

```json
{
    "valid": false,
    "errors": [
        {
            "code": "ARTIFACT_MISSING",
            "path": "docs/plan.md",
            "message": "Required artifact not found"
        }
    ],
    "warnings": []
}
```

### 7. CLI Commands

#### 7.1 Core Commands

| Command | Purpose |
|---------|---------|
| `init` | Initialize runner home |
| `run` | Execute workflow locally |
| `status` | Check job status |
| `approve` | Approve a step |
| `reset-step` | Reset step for retry |

#### 7.2 Worker Commands

| Command | Purpose |
|---------|---------|
| `worker` | Run worker loop |
| `poll` | Poll for work once |
| `execute-step` | Execute single step |
| `daemon` | Run daemon supervisor |

### 8. Configuration

#### 8.1 Configuration Sources

Priority (highest to lowest):

1. Command-line arguments
2. Environment variables
3. `config.json` in runner home
4. Default values

#### 8.2 Key Configuration

```json
{
    "backend_url": "https://api.example.com",
    "api_key": "sk-...",
    "default_coder": "claude",
    "max_retries": 3,
    "timeout": 300
}
```

### 9. Error Handling

#### 9.1 Failure Classification

| Class | Description | Example |
|-------|-------------|---------|
| `AUTO_RETRYABLE` | Transient, can retry | Network timeout |
| `HUMAN_RETRY_REQUIRED` | Needs human input | Validation failed |
| `FATAL` | Cannot recover | Schema mismatch |

#### 9.2 Error Routing

```
Error Detected
      │
      ▼
┌─────────────┐
│  Classify   │
│   Error     │
└──────┬──────┘
       │
   ┌───┴───┬───────────┐
   │       │           │
   ▼       ▼           ▼
┌────┐ ┌───────┐  ┌────────┐
│AUTO│ │ HUMAN │  │ FATAL  │
│    │ │       │  │        │
└────┘ └───────┘  └────────┘
  │       │           │
  │   ┌───┘           │
  │   │               │
  ▼   ▼               ▼
Retry Human      Terminate
      Input
```

## Functional Constraints

### Must Support

- Python 3.11+
- Windows and Unix-like systems
- Multiple LLM providers
- Async execution

### Must Not

- Write to markdown files (v2 contract)
- Parse stdout for results (v2 contract)
- Allow silent recovery (v2 contract)

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs`*
