---
template_id: "SYS-00-FS"
title: "Functional Specification - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Functional Specification

## System Purpose

Agent-runner-v2 provides structured workflow execution for LLM-assisted automation. It manages the lifecycle of multi-step workflows, orchestrates LLM invocations, handles step-level routing, and maintains state across execution contexts.

**Key Functions:**
- Load and execute workflow definitions
- Invoke LLM coders with rendered prompts
- Validate step outputs via artifact checking
- Route to next steps based on results
- Persist state for recovery and inspection

## Actors

### Primary Actors

| Actor | Role | Goals |
|-------|------|-------|
| **Workflow Operator** | Runs workflows locally | Execute workflows, monitor progress, approve steps |
| **Backend System** | Distributes work | Queue work, track execution, collect results |
| **Worker Process** | Processes backend work | Claim work, execute steps, submit results |
| **Daemon Process** | Supervises execution | Continuous work processing, child management |

### Secondary Actors

| Actor | Role | Goals |
|-------|------|-------|
| **LLM Provider** | Generates outputs | Provide code, text, or analysis on request |
| **Reviewers** | Approve/reject outputs | Ensure quality before progression |
| **Administrators** | Configure system | Set up runners, manage credentials |

## Functional Capabilities

### F1: Workflow Execution

**Description:** Load workflow bundles and execute steps in sequence.

**Inputs:**
- Workflow name (e.g., `delivery_planning_v1`)
- Job ID (generated or provided)
- Input artifacts (file paths)
- Configuration overrides

**Process:**
1. Load workflow bundle from runtime location
2. Resolve template group and step configuration
3. Create or restore job state
4. Execute current step (coder or action)
5. Validate outputs
6. Route to next step

**Outputs:**
- Updated job state
- Generated artifacts
- Execution logs

**Error Handling:**
- Missing workflow: Error with available workflows list
- Invalid step: Error with valid step names
- Execution failure: Retry or route to failure handling

### F2: Prompt Rendering

**Description:** Build context from artifacts and render prompt templates.

**Inputs:**
- Prompt template file (`.txt`)
- Artifact paths from job state
- Reference files configuration
- Context variables

**Process:**
1. Compute artifact paths relative to project root
2. Load and include artifact contents
3. Apply reference file mappings
4. Substitute context variables
5. Compute prompt checksum

**Outputs:**
- Rendered prompt text
- Checksum for caching/verification

**Error Handling:**
- Missing artifact: Preflight error before invocation
- Missing template: Error with search paths
- Render error: Exception with context

### F3: Coder Invocation

**Description:** Invoke LLM coders (Claude, Codex, Qwen) with prompts.

**Inputs:**
- Coder name (e.g., `claude-sonnet`, `codex`, `qwen`)
- Rendered prompt text
- Timeout configuration
- Schema for response validation

**Process:**
1. Resolve coder configuration from model mapping
2. Invoke appropriate adapter
3. Wait for response (with timeout)
4. Parse and validate response
5. Extract metadata

**Outputs:**
- Invocation result with status
- Usage data (tokens, cost)
- Response metadata

**Error Handling:**
- Timeout: Classify as auto-retryable
- Invalid response: Schema validation error
- Coder error: Invocation error with details

### F4: Meta.json Validation

**Description:** Read and validate sidecar results from coder execution.

**Inputs:**
- Expected meta.json path
- Result schema
- Expected artifacts

**Process:**
1. Read meta.json from step directory
2. Validate against schema (v2)
3. Verify status (APPROVED/REJECTED)
4. Check artifact existence
5. Enrich with usage data

**Outputs:**
- Validated StepResult
- Artifact path mappings

**Error Handling:**
- Missing meta.json: Fatal error, route to failure
- Invalid JSON: Parse error with details
- Schema violation: Validation error with path
- Missing artifacts: ArtifactMissingError

### F5: Step Routing

**Description:** Route job state after step completion.

**Inputs:**
- Step result (APPROVED/REJECTED)
- Job configuration
- Current step context
- Retry history

**Process:**
1. Record step usage in job state
2. If APPROVED: Advance to next step
3. If REJECTED: Classify rejection code
4. Apply retry logic (auto/human)
5. Update routing decision in state

**Outputs:**
- Updated job state
- Next step or terminal status
- Exit code (0=continue, 1=intervention, 2=fatal)

**Routing Logic:**

| Result | Action |
|--------|--------|
| APPROVED | Advance step, continue workflow |
| REJECTED (auto-retryable) | Retry step with retry count |
| REJECTED (human-required) | Wait for human decision |
| REJECTED (replan) | Enter replan workflow |

### F6: Action Execution

**Description:** Execute deterministic runner actions (non-LLM steps).

**Inputs:**
- Action name (e.g., `scan_repo_codebase`)
- Action configuration
- Context artifacts

**Process:**
1. Load action module from `actions/` package
2. Execute action function
3. Generate meta.json sidecar
4. Return action result

**Outputs:**
- Generated files/artifacts
- Action result metadata

**Built-in Actions:**

| Action | Purpose |
|--------|---------|
| `scan_repo_codebase` | Repository analysis and inventory |
| `sync_codebase_docs` | Documentation synchronization |
| `validate_codebase_docs` | Documentation validation |
| `prepare_delivery_scaffold` | Scaffold setup for delivery |
| `promote_artifact` | Artifact promotion between stages |
| `execute_t2i` | Text-to-image generation |
| `execute_i2v` | Image-to-video generation |
| `execute_voiceover` | Voiceover generation |
| `assemble_video` | Video composition |
| `submit_comfyui` | ComfyUI submission |

### F7: State Management

**Description:** Persist and restore job state across execution.

**Inputs:**
- Job ID
- State mutations
- Step completions

**Process:**
1. Create job with initial state
2. Save state after each step
3. Load state on resume
4. Migrate state if schema changes

**State Contents:**
- Current step
- Completed steps
- Artifact paths
- Retry counts
- Usage tracking
- Failure history
- Loop context
- Review state

**Storage:**
- Location: `%USERPROFILE%\.ukbe-runner\jobs\<group>\<job_id>\`
- Format: JSON with schema versioning
- Backup: Automatic on migration

### F8: Backend Integration

**Description:** Connect to backend for distributed execution.

**Inputs:**
- Backend URL
- Worker ID
- Authentication credentials

**Operations:**
- Poll for available work
- Claim workflow step
- Submit step results
- Emit heartbeats

**Process (Worker):**
1. Poll backend for pending work
2. Claim work item
3. Execute step locally
4. Submit result to backend

**Process (Daemon):**
1. Continuous poll loop
2. Spawn child for each work item
3. Monitor child process
4. Submit result on child completion
5. Handle child failures

## Core Behaviors

### B1: Workflow Initialization

**Trigger:** `ukbe-run-agent init`

**Behavior:**
1. Create runner home directory structure
2. Seed workflow bundles from package
3. Create initial configuration files
4. Set up log directories

**Result:** Runner home ready for execution

### B2: Single Step Execution

**Trigger:** `ukbe-run-agent execute-step --request-file <file>`

**Behavior:**
1. Parse execution request JSON
2. Load workflow and resolve step
3. Render prompt
4. Invoke coder or action
5. Validate result
6. Write result JSON

**Result:** Step executed, result available

### B3: Full Workflow Execution

**Trigger:** `ukbe-run-agent run --template-group <group>`

**Behavior:**
1. Create or load job
2. Execute current step
3. Route to next step
4. Repeat until terminal
5. Report final status

**Result:** Workflow completed or awaiting approval

### B4: Job Inspection

**Trigger:** `ukbe-run-agent run --job-id <id> --show-job`

**Behavior:**
1. Load job state
2. Display step history
3. Show artifact paths
4. Report current status

**Result:** Job state visible

### B5: Step Approval

**Trigger:** `ukbe-run-agent run --job-id <id> --approve-step`

**Behavior:**
1. Load job state
2. Verify step awaiting approval
3. Apply human decision
4. Advance workflow

**Result:** Workflow continues past review gate

### B6: Step Reset

**Trigger:** `ukbe-run-agent run --job-id <id> --reset-step <step>`

**Behavior:**
1. Load job state
2. Mark step incomplete
3. Clear associated artifacts
4. Reset routing state

**Result:** Step ready for re-execution

### B7: Backend Polling

**Trigger:** `ukbe-run-agent poll --backend-url <url>`

**Behavior:**
1. Connect to backend
2. Poll for available work
3. Execute single work item
4. Submit result
5. Exit

**Result:** One work item processed

### B8: Continuous Worker

**Trigger:** `ukbe-run-agent worker --backend-url <url>`

**Behavior:**
1. Register worker with backend
2. Poll loop for work
3. Execute claimed work
4. Submit results
5. Continue until interrupted

**Result:** Continuous work processing

### B9: Daemon Supervision

**Trigger:** `ukbe-run-agent daemon <worker-id>`

**Behavior:**
1. Start supervisor process
2. Claim work from backend
3. Spawn child process per work item
4. Monitor child execution
5. Restart failed children
6. Log all activity

**Result:** Continuous supervised execution

## Workflow Families

### Delivery Planning (`30_delivery_planning_v1`)

**Steps:**
1. `02_planner` — Generate delivery plan
2. `03_review_planner` — Review plan quality
3. `03_refine_plan` — Refine based on review
4. `04_task_graph` — Generate task graph
5. `05_review_task_graph` — Review task decomposition
6. `05_refine_task_graph` — Refine tasks
7. `06_task` — Generate task contract
8. `07_review_task` — Review task contract
9. `07_refine_task` — Refine task

**Purpose:** Turn initiatives into executable task plans

### Task Execution (`31_task_execution_v1`)

**Steps:**
1. `08_impl_task` — Generate implementation plan
2. `09_review_impl_task` — Review implementation
3. `09_refine_impl` — Refine implementation
4. `10_executor` — Execute implementation
5. `11_validate` — Validate results

**Purpose:** Implement and validate tasks

### Documentation Bootstrap (`00_master_docs_bootstrap_v1`)

**Steps:**
1. `00_scan_repo_codebase` — Scan repository
2. `01_generate_codebase_baseline` — Generate inventory
3. `02_generate_project_analysis` — Analyze project
4. `03_generate_system_overview_docs` — Generate overview docs
5. `04_generate_architecture_docs` — Generate architecture docs
6. `05_review_master_system_docs` — Review documentation
7. `06_refine_master_system_docs` — Refine documentation
8. `07_validate_codebase_baseline` — Validate codebase
9. `08_validate_master_system_docs` — Validate system docs
10. `09_finalize_bootstrap` — Complete bootstrap

**Purpose:** Generate master system documentation

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
