# agent-runner-v2 — QWEN.md

## Project Overview

**agent-runner-v2** is a standalone Python **LLM workflow orchestration engine** extracted from the UKBE (Universal Knowledge Base Engine) project. It manages multi-step, multi-coder delivery pipelines, running AI agents (Claude, Codex, Qwen, and aliased models like DeepSeek) through structured workflows with review loops, automatic retries, and human-in-the-loop approval gates.

The project is a clean extraction into its own installable Python package, shipped as `agent-runner-v2` with a CLI entry point `ukbe-run-agent`.

### What It Does

The runner executes **template-driven workflows** where each workflow consists of a sequence of steps. Each step:
1. Renders a prompt template with context from previous artifacts
2. Invokes an LLM coder (Claude, Codex, Qwen, or aliased models)
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
| `run_agent.py` | Main CLI entry point. Orchestrates: load config → resolve job → preflight → prompt → run_step → route. Supports `init` and `run` subcommands |
| `step_runner.py` | Single-step execution contract. Invokes coder → reads meta.json → validates artifacts → enriches sidecar |
| `workflow_router.py` | Post-step routing logic. Handles approved/rejected results, loop triggers, replan triggers, failure classification |
| `job_state.py` | All `job.json` lifecycle management. CRUD, migration, state reconciliation, approval, retry limits |
| `coder_adapters.py` | Coder invocation layer. Wraps Claude CLI, Codex CLI, Qwen CLI with sidecar polling, timeout handling, usage extraction |
| `template_groups.py` | Workflow definitions. Declares steps, inputs/outputs, coders, max rejects, refine loops, replan configs |
| `bundle_loader.py` | Workflow bundle loading and bootstrap helpers. Handles project config, workflow module loading, and workspace initialization |
| `runtime_context.py` | Process-local runtime context with `PathProxy` for context-aware path resolution |
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
| `agent_runner_v2/prompts/` | Prompt template files, organised by workflow (e.g. `prompts/delivery_planning_v1/02_planner.txt`) |
| `.ukbe-runner/` | Project-local runner home (created by `ukbe-run-agent init`) containing config, jobs, workflows, and logs |

---

## Workflow Templates

Five template groups are defined in `template_groups.py`:

### 1. `initiative_intake_v1`
- **Purpose:** Pre-initialise a draft initiative into a structured pre-init document
- **Steps:** `pre_init` → `review_pre_init` → `refine_pre_init` (loop)
- **Seed artifact:** `DRAFT_INIT_FILE`

### 2. `delivery_planning_v1`
- **Purpose:** Generate a delivery plan and task graph from an approved init document
- **Steps:** `planner` → `review_planner` → `refine_plan` → `replan_plan` → `task_graph` → `review_task_graph` → `refine_task_graph` → `replan_task_graph`
- **Seed artifact:** `INIT_FILE`
- **Features:** Refine loops (max 2 iterations), replan attempts (max 1), planning attempt budget (max 5)
- **Template conformance:** Validates PLAN, TASK_GRAPH, and TASK documents against scaffolded delivery templates via `template_ref`

### 3. `delivery_scaffold_v1`
- **Purpose:** Bootstrap a complete delivery documentation system (templates, SOP, status rules, agent contracts) for any target repository
- **Steps:** `project_analysis` → `generate_sop` → `refine_sop` → `replan_sop` → `generate_templates` → `refine_templates` → `generate_agents` → `refine_agents` → `validate_delivery_docs`
- **Seed artifact:** `PROJECT_CONTEXT_FILE` — a project description file
- **Features:**
  - Cross-project support via `--target-project-root` to scaffold into any repository
  - `project_analysis` (qwen): scans project context, produces structured analysis
  - `generate_sop` (claude): generates WORKFLOW_SOP_v1.md + DELIVERY_STATUS_RULES_v1.md
  - `generate_templates` (qwen): generates all 7 document templates + registry
  - `generate_agents` (claude): generates AGENTS.md + 6 agent contracts
  - `validate_delivery_docs` (runner action): deterministic structural validation — NOT a coder step
- **Note:** Does NOT generate agent master prompts (`07_master_prompts/`) — workflow step configs serve as agent contracts

### 4. `task_execution_v1`
- **Purpose:** Execute individual tasks — generate implementation, review, refine, validate
- **Steps:** `task` → `review_task` → `refine_task` → `impl` → `review_impl` → `refine_impl` → `executor` → `validator`
- **Seed artifact:** `TASK_FILE` (from task graph) or `--task-graph-id` + `--task-node-id`
- **Features:** Task-level execution binding, implementation refinement loops, validation gates

### 5. `image_csv_gen_v1`
- **Purpose:** Generate CSV metadata from an image folder
- **Steps:** `gen_csv`
- **Seed artifact:** `IMAGE_FOLDER`
- **Produces:** `IMAGE_CSV_JSON`, `IMAGE_CSV_CSV`

---

## Building and Running

### Prerequisites

- Python 3.11+
- Installed coder CLIs: `claude` (Claude Code), `codex` (OpenAI Codex CLI), `qwen` (Qwen Code CLI)
- API keys set in environment (e.g. `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`)

### Install

```bash
pip install -e .
```

### Initialize a Project Workspace

```bash
ukbe-run-agent init
```

This creates a project-local runner home in the current directory:
- `.ukbe-runner/config.json`
- `.ukbe-runner/jobs/`
- `.ukbe-runner/workflows/default/`
- `.ukbe-runner/logs/`

### CLI Usage

```bash
# Scaffold a delivery documentation system into another repo (auto-discovers AI context files)
ukbe-run-agent run \
  --project-root /home/kengkoon/projects/agent-runner-v2 \
  --template-group delivery_scaffold_v1 \
  --target-project-root /path/to/new-project

# Run a workflow (auto-resume if job exists)
ukbe-run-agent run --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/02_plans/INIT-20260409-01_example.md

# Backward-compatible shorthand (no 'run' subcommand)
ukbe-run-agent --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/02_plans/INIT-20260409-01_example.md

# Target another workspace
ukbe-run-agent run --project-root /path/to/project --template-group delivery_planning_v1 --set INIT_FILE=...

# Select a specific workflow bundle
ukbe-run-agent run --workflow default --template-group delivery_planning_v1 --set INIT_FILE=...

# Dry run (render prompt only, no coder invocation)
ukbe-run-agent run --template-group delivery_planning_v1 --job planner --dry-run

# Force a new job (skip resume)
ukbe-run-agent run --template-group delivery_planning_v1 --new-job --set INIT_FILE=...

# Show current job state
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-INIT01-20260409-001 --show-job

# Approve a pending step
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --approve-step review_planner

# Force-approve a step regardless of review decision
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --force-approve-step review_planner

# Re-apply routing for a stuck job
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --reapply-routing

# Override current step and reset loop context
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --override-step planner

# Check job status summary
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --check-job-status

# Task execution with explicit graph binding
ukbe-run-agent run --template-group task_execution_v1 --task-graph-id "TASK-GRAPH-..." --task-node-id "TASK-..."
```

### Key CLI Arguments

| Argument | Description |
|---|---|
| `--template-group` | Required. Workflow template group name |
| `--target-project-root` | Target project root for delivery scaffold artifacts. Defaults to `--project-root` |
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
| `--project-root` | Workspace root (defaults to current directory) |
| `--workflow` | Workflow bundle name (defaults to workspace default) |

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
| `CONTEXT_PACK_FILE` | Context pack artifact |
| `IMAGE_FILE` | Image file |
| `IMAGE_FOLDER` | Source image folder |
| `IMAGE_CSV_JSON` | Image CSV JSON metadata |
| `IMAGE_CSV_CSV` | Image CSV file |
| `PROJECT_CONTEXT_FILE` | Seed project description for delivery scaffold |
| `PROJECT_ANALYSIS` | Structured project analysis (domain, tech stack, complexity) |
| `DELIVERY_SOP` | WORKFLOW_SOP_v1.md |
| `DELIVERY_STATUS_RULES` | DELIVERY_STATUS_RULES_v1.md |
| `DELIVERY_TEMPLATE_REGISTRY` | template_registry.md |
| `DELIVERY_INITIATIVE_TEMPLATE` | 01_initiative.template.md |
| `DELIVERY_PLAN_TEMPLATE` | 02_plan.template.md |
| `DELIVERY_TASK_GRAPH_TEMPLATE` | 02b_task_graph.template.md |
| `DELIVERY_TASK_TEMPLATE` | 03_task.template.md |
| `DELIVERY_IMPL_TEMPLATE` | 04_implementation_plan.template.md |
| `DELIVERY_REVIEW_TEMPLATE` | 04_review.template.md |
| `DELIVERY_MEMORY_TEMPLATE` | 06_memory.template.md |
| `DELIVERY_AGENTS_MD` | AGENTS.md system registry |
| `DELIVERY_AGENT_PLANNER` | AGENT-planner.md |
| `DELIVERY_AGENT_TASK_DECOMPOSER` | AGENT-task-decomposer.md |
| `DELIVERY_AGENT_IMPL_PLANNER` | AGENT-implementation-planner.md |
| `DELIVERY_AGENT_EXECUTOR` | AGENT-executor.md |
| `DELIVERY_AGENT_REVIEWER` | AGENT-reviewer.md |
| `DELIVERY_AGENT_MEMORY_MANAGER` | AGENT-memory-manager.md |
| `DELIVERY_FOLDER_MAP` | Validation output manifest (folder_map.json) |

Each artifact has an associated `meta.json` sidecar at `{artifact_stem}.meta.json` containing the coder's structured result.

---

## Coder Model Aliases

Defined in `model_mapping.json`. The runner resolves aliases to full invocation configs:

| Alias | Underlying Coder | Model |
|---|---|---|
| `deepseek-chat` | qwen | deepseek-chat (DeepSeek API) |
| `deepseek-reasoner` | qwen | deepseek-reasoner (DeepSeek API) |
| `deepseek-coder` | qwen | deepseek-coder (DeepSeek API) |
| `gpt-5.4-nano` | qwen | gpt-5.4-nano (OpenAI API) |
| `qwen-claude` | qwen | claude-3-5-sonnet (Anthropic) |
| `qwen-gemini` | qwen | gemini-2.0-flash (Gemini) |

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

## Development Conventions

### Code Style

- Python 3.11+ with type hints throughout
- `from __future__ import annotations` at the top of every file
- Dataclasses for structured data (`StepResult`, `UsageData`, `InvocationManifest`, `InvocationResult`)
- Explicit exception types — no implicit error paths

### Testing

- Test configuration: `pytest` with `tests/` directory
- Dev dependencies: `pytest>=8.2.0`, `pytest-cov>=5.0.0`
- No test files currently exist in the project
- Manual testing via `--dry-run` and actual job execution

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Adding a New Workflow

1. Define the workflow in `TEMPLATE_GROUPS` in `template_groups.py`
2. Create prompt templates in `prompts/<workflow_name>/`
3. Register artifact keys in `ARTIFACT_KEYS` if new artifact types are needed
4. Each step config requires: `prompt_file`, `required_inputs`, `produces`, `result_meta_key`, `coder` config

---

## Project Structure

```
agent-runner-v2/
├── pyproject.toml              # Package configuration, dependencies, CLI entry point
├── MANIFEST.in                 # Package manifest
├── README.md                   # Project README
├── .gitignore                  # Git ignore rules
├── .codex                      # Codex configuration
├── agent_runner_v2/
│   ├── __init__.py
│   ├── run_agent.py            # CLI entry point (ukbe-run-agent)
│   ├── step_runner.py          # Single-step execution
│   ├── workflow_router.py      # Post-step routing
│   ├── job_state.py            # Job state management
│   ├── coder_adapters.py       # Claude/Codex/Qwen adapters
│   ├── template_groups.py      # Workflow definitions
│   ├── bundle_loader.py        # Workflow bundle loading
│   ├── runtime_context.py      # Runtime context & path proxies
│   ├── artifact_paths.py       # Artifact path computation
│   ├── model_config.py         # Model alias resolution
│   ├── runner_logger.py        # Structured logging
│   ├── exceptions.py           # Custom exception types
│   ├── action_result.py        # Return type for runner actions
│   ├── runner_actions.py       # Action registry and dispatch
│   ├── actions/                # Runner action implementations
│   │   ├── __init__.py
│   │   ├── submit_comfyui.py   # ComfyUI prompt submission
│   │   └── validate_delivery_docs.py  # Delivery docs validation
│   ├── job_schema.json         # Job schema reference
│   ├── llm_response_schema.json # LLM output schema
│   ├── model_mapping.json      # Coder alias definitions
│   ├── usage_schema.json       # Usage schema definition
│   ├── prompts/                # Prompt templates by workflow
│   │   ├── delivery_planning_v1/
│   │   ├── delivery_scaffold_v1/  # ← NEW: delivery scaffold prompts
│   │   │   ├── 01_project_analysis.txt
│   │   │   ├── 02_generate_sop.txt
│   │   │   ├── 03_generate_templates.txt
│   │   │   ├── 04_generate_agents.txt
│   │   │   ├── 05_refine_sop.txt
│   │   │   ├── 05_replan_sop.txt
│   │   │   ├── 06_refine_templates.txt
│   │   │   └── 07_refine_agents.txt
│   │   ├── initiative_intake_v1/
│   │   ├── task_execution_v1/
│   │   └── image_csv_gen_v1/
│   └── QWEN.md                 # Internal QWEN context
└── agent_runner_v2.egg-info/   # Build artifacts
```
