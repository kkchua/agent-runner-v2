# agent_runner_v2 — QWEN.md

## Project Overview

**agent_runner_v2** is a Python-based **LLM workflow orchestration engine** that manages multi-step, multi-coder delivery pipelines. It serves as the execution backbone for the UKBE (Universal Knowledge Base Engine) project's delivery system, running AI agents (Claude, Codex, Qwen) through structured workflows with review loops, automatic retries, and human-in-the-loop approval gates.

### What It Does

The runner executes **template-driven workflows** where each workflow consists of a sequence of steps. Each step:
1. Renders a prompt template with context from previous artifacts
2. Invokes an LLM coder (Claude, Codex, Qwen, or aliased models like DeepSeek)
3. Reads a `meta.json` sidecar written by the coder
4. Validates the result against a JSON schema
5. Routes the outcome (approved → next step; rejected → refine loop or human intervention)

### Key v2 Design Principles (vs v1)

- **meta.json sidecar is the ONLY communication channel** — no stdout JSON parsing, no fallback recovery
- **No pre-invocation sidecar writes** — the runner does not touch markdown files before coder invocation
- **No markdown write-backs** — no `sync_review_metadata`, `stamp_created_metadata`, etc.
- **Explicit exception routing** — hard failures go to `route_after_failure()` immediately
- **No disk recovery functions** — failures are explicit, not silently recovered

---

## Architecture

### Core Modules

| File | Responsibility |
|---|---|
| `run_agent.py` | Main CLI entry point. Orchestrates: load config → resolve job → preflight → prompt → run_step → route |
| `step_runner.py` | Single-step execution contract. Invokes coder → reads meta.json → validates artifacts → enriches sidecar |
| `workflow_router.py` | Post-step routing logic. Handles approved/rejected results, loop triggers, replan triggers, failure classification |
| `job_state.py` | All `job.json` lifecycle management. CRUD, migration, state reconciliation, approval, retry limits |
| `coder_adapters.py` | Coder invocation layer. Wraps Claude CLI, Codex CLI, Qwen CLI with sidecar polling, timeout handling, usage extraction |
| `template_groups.py` | Workflow definitions. Declares steps, inputs/outputs, coders, max rejects, refine loops, replan configs |
| `artifact_paths.py` | Single source of truth for artifact file path computation (node_id → artifact path + meta.json path) |
| `model_config.py` | Model alias resolver. Loads `model_mapping.json` to resolve coder aliases to full invocation configs |
| `runner_logger.py` | Structured logging with colorised console output and JSON-lines file logging |
| `exceptions.py` | Custom exception types: `PreflightBlockedError`, `MetaJsonMissingError`, `MetaJsonInvalidError`, `ArtifactMissingError` |

### Supporting Schemas & Config

| File | Purpose |
|---|---|
| `job_schema.json` | Example job.json structure (reference/documentation) |
| `llm_response_schema.json` | JSON schema that coders must conform to in their output |
| `model_mapping.json` | Coder alias definitions (e.g. `deepseek-chat` → qwen with DeepSeek API config) |
| `usage_schema.json` | Usage data structure definition |

### Directories

| Directory | Purpose |
|---|---|
| `prompts/` | Prompt template files, organised by workflow (e.g. `prompts/delivery_planning_v1/02_planner.txt`) |
| `jobs/` | Runtime job state storage, organised by template group (`jobs/delivery_planning_v1/PLAN-.../job.json`) |
| `logs/` | Runner log files (`logs/runner.log` in JSON-lines format) |

---

## Workflow Templates

Three template groups are defined in `template_groups.py`:

### 1. `initiative_intake_v1`
- **Purpose:** Pre-initialise a draft initiative into a structured pre-init document
- **Steps:** `pre_init` → `review_pre_init` → `refine_pre_init` (loop)
- **Seed artifact:** `DRAFT_INIT_FILE`

### 2. `delivery_planning_v1`
- **Purpose:** Generate a delivery plan and task graph from an approved init document
- **Steps:** `planner` → `review_planner` → `refine_plan` → `replan_plan` → `task_graph` → `review_task_graph` → `refine_task_graph` → `replan_task_graph`
- **Seed artifact:** `INIT_FILE`
- **Features:** Refine loops (max 2 iterations), replan attempts (max 1), planning attempt budget (max 5)

### 3. `task_execution_v1`
- **Purpose:** Execute individual tasks — generate implementation, review, refine, validate
- **Steps:** `task` → `review_task` → `refine_task` → `impl` → `review_impl` → `refine_impl` → `executor` → `validator`
- **Seed artifact:** `TASK_FILE` (from task graph) or `--task-graph-id` + `--task-node-id`
- **Features:** Task-level execution binding, implementation refinement loops, validation gates

---

## Building and Running

### Prerequisites

- Python 3.11+
- Installed coder CLIs: `claude` (Claude Code), `codex` (OpenAI Codex CLI), `qwen` (Qwen Code CLI)
- API keys set in environment (e.g. `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`)

### CLI Usage

```bash
# Run a workflow (auto-resume if job exists)
python run_agent.py --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/02_plans/INIT-20260409-01_example.md

# Dry run (render prompt only, no coder invocation)
python run_agent.py --template-group delivery_planning_v1 --job planner --dry-run

# Force a new job (skip resume)
python run_agent.py --template-group delivery_planning_v1 --new-job --set INIT_FILE=...

# Show current job state
python run_agent.py --template-group delivery_planning_v1 --job-id PLAN-INIT01-20260409-001 --show-job

# Approve a pending step
python run_agent.py --template-group delivery_planning_v1 --job-id PLAN-... --approve-step review_planner

# Force-approve a step regardless of review decision
python run_agent.py --template-group delivery_planning_v1 --job-id PLAN-... --force-approve-step review_planner

# Re-apply routing for a stuck job
python run_agent.py --template-group delivery_planning_v1 --job-id PLAN-... --reapply-routing

# Override current step and reset loop context
python run_agent.py --template-group delivery_planning_v1 --job-id PLAN-... --override-step planner

# Check job status summary
python run_agent.py --template-group delivery_planning_v1 --job-id PLAN-... --check-job-status

# Task execution with explicit graph binding
python run_agent.py --template-group task_execution_v1 --task-graph-id "TASK-GRAPH-..." --task-node-id "TASK-..."
```

### Key CLI Arguments

| Argument | Description |
|---|---|
| `--template-group` | Required. Workflow template group name |
| `--coder` | Optional coder override for current step |
| `--job-id` | Existing job ID to resume |
| `--job` | Explicit step to run (omit for auto-resolve) |
| `--set KEY=PATH` | Seed artifact for new job (e.g. `--set INIT_FILE=path/to/file.md`) |
| `--task-graph-id` | Approved task graph ID (task_execution_v1 only) |
| `--task-node-id` | Selected task node ID within the graph (task_execution_v1 only) |
| `--dry-run` | Render prompt and save `prompt.txt` without invoking coder |
| `--new-job` | Force new job creation instead of auto-resume |
| `--max-rejects` | Override max rejects for this run |
| `--show-job` | Print current `job.json` and exit |
| `--approve-step` | Record human approval for a pending step |
| `--force-approve-step` | Force-approve regardless of review decision |
| `--reapply-routing` | Re-apply routing logic to stuck jobs |
| `--override-step` | Force current_step and reset loop context |
| `--check-job-status` | Print formatted job status summary |

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENT_RUNNER_CODER_TIMEOUT_SECONDS` | `600` | Timeout for coder invocations (seconds) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `DEEPSEEK_API_KEY` | — | DeepSeek API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key (for Claude) |

---

## State Machine

### Job Statuses

| Status | Meaning |
|---|---|
| `IN_PROGRESS` | Actively executing |
| `WAITING_FOR_HUMAN_APPROVAL` | Model approved, awaiting human sign-off |
| `WAITING_FOR_AUTO_RETRY` | Transient failure — will retry automatically |
| `WAITING_FOR_HUMAN_INTERVENTION` | Non-transient failure — requires human action |
| `COMPLETED` | All steps finished |
| `FAILED` | Max rejects exceeded or fatal error |

### Step Result Routing

```
coder invocation → meta.json → StepResult(status, remark, artifacts, reject_code)

APPROVED → advance to next step → exit_code=0

REJECTED → has on_reject_refine?
  ├─ YES → loop exhausted?
  │   ├─ NO → trigger refine loop → exit_code=0
  │   └─ YES → replan exhausted?
  │       ├─ NO → trigger replan → exit_code=0
  │       └─ YES → human intervention required → exit_code=1
  └─ NO → classify rejection → auto-retry / human-intervention / fatal

EXCEPTION → classify exception → route_after_failure()
```

### Failure Classification

| Exception | Failure Class | Failure Code | Source |
|---|---|---|---|
| Transient API error (timeout, rate limit, 429) | `AUTO_RETRYABLE` | `TRANSIENT_API_ERROR` | adapter |
| CoderInvocationError (non-transient) | `HUMAN_RETRY_REQUIRED` | `ADAPTER_INVOCATION_FAILED` | adapter |
| MetaJsonMissingError | `HUMAN_RETRY_REQUIRED` | `META_JSON_MISSING` | validator |
| MetaJsonInvalidError | `HUMAN_RETRY_REQUIRED` | `META_JSON_INVALID` | validator |
| ArtifactMissingError | `HUMAN_RETRY_REQUIRED` | `ARTIFACT_FILES_MISSING` | validator |
| Unknown exception | `FATAL` | `UNEXPECTED_RUNNER_ERROR` | runner |

---

## Artifact Types

| Artifact Key | Description |
|---|---|
| `DRAFT_INIT_FILE` | Draft initiative document |
| `PRE_INIT_FILE` | Pre-processed initiative |
| `INIT_FILE` | Approved initiative document |
| `PLAN_FILE` | Delivery plan |
| `TASK_GRAPH_FILE` | Task graph (structured task nodes) |
| `TASK_FILE` | Individual task specification |
| `IMPL_FILE` | Implementation document |
| `REVIEW_FILE` | Review/feedback document |
| `VALIDATION_FILE` | Validation report |

Each artifact has an associated `meta.json` sidecar at `{artifact_stem}.meta.json` containing the coder's structured result.

---

## Development Conventions

### Code Style

- Python 3.11+ with type hints throughout
- `from __future__ import annotations` at the top of every file
- Dataclasses for structured data (`StepResult`, `UsageData`, `InvocationManifest`, `InvocationResult`)
- Explicit exception types — no implicit error paths

### Testing

- No test files currently in this directory (tests may be at project level)
- Manual testing via `--dry-run` and actual job execution

### Adding a New Workflow

1. Define the workflow in `TEMPLATE_GROUPS` in `template_groups.py`
2. Create prompt templates in `prompts/<workflow_name>/`
3. Register artifact keys in `ARTIFACT_KEYS` if new artifact types are needed
4. Each step config requires: `prompt_file`, `required_inputs`, `produces`, `result_meta_key`, `coder` config

### Adding a New Coder Alias

Add an entry to `model_mapping.json` under `coder_aliases`:
```json
"my-alias": {
  "coder": "qwen",
  "model": "model-name",
  "auth_type": "openai",
  "openai_api_key_env": "MY_API_KEY_ENV",
  "openai_base_url": "https://api.example.com/v1"
}
```

---

## Key File Locations (Parent Project)

The agent runner lives at `ukbe/agent_runner_v2/`. Its parent project root is `ukbe/` (one level up). The runner expects to operate relative to this parent project root for artifact paths.
