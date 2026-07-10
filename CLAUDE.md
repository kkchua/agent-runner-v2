# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Install
```bash
pip install -e ".[dev]"
```

### Run Tests
```bash
# All tests
pytest

# Single test file
pytest tests/test_architecture_site.py

# Single test function
pytest tests/test_architecture_site.py::test_function_name

# With verbose output
pytest -vv -s
```

On Windows, use `test-runner.ps1` which sets up the environment properly:
```powershell
.\test-runner.ps1
.\test-runner.ps1 tests/test_architecture_site.py
```

### CLI Usage
The package provides the `ukbe-run-agent` CLI:
```bash
# Initialize runner home (seeds %USERPROFILE%\.ukbe-runner\)
ukbe-run-agent init

# Run a workflow
ukbe-run-agent run --template-group 10_execution_scaffold_v1

# Backend-connected worker
ukbe-run-agent worker --backend-url http://127.0.0.1:8100 --worker-id worker-01

# Execute a single backend-provided step
ukbe-run-agent execute-step --request-file request.json --result-file result.json
```

## Architecture

### Core Execution Model
Each workflow step follows this sequence:
1. Load active workflow bundle from global runner home
2. Render prompt from bundle template
3. Invoke coder (Claude/Codex/Qwen) or runner action
4. Read `meta.json` sidecar written by the step
5. Validate artifacts and route to next step

**v2 invariants:**
- `meta.json` sidecar is the only structured result channel
- No markdown write-backs by the runner
- No silent recovery paths — hard failures route explicitly through `route_after_failure()`

### Two Sources of Truth
1. **Packaged bootstrap** (this repo): `agent_runner_v2/bootstrap/workflows/default/`
   - `template_groups.py` — workflow definitions
   - `prompts/` — prompt templates per workflow
   - Only seeds the runtime bundles
2. **Runtime workflow bundle** (global runner home): `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
   - Runtime prompt/templates are loaded from here, NOT from the repo tree directly

### Key Modules

| Module | Responsibility |
|--------|----------------|
| `run_agent.py` | CLI entry point and top-level orchestration |
| `step_runner.py` | Prompt rendering, coder invocation, sidecar validation, artifact checks |
| `workflow_router.py` | Post-step routing (approve/reject/failure/loop/replan) |
| `job_state.py` | `job.json` lifecycle management, schema migration |
| `coder_adapters.py` | Claude/Codex/Qwen invocation and polling |
| `bundle_loader.py` | Bootstrap seeding and workflow bundle loading |
| `runtime_context.py` | Active workflow/runtime path context |
| `runner_actions.py` | Action registry and dispatch |
| `actions/` | Deterministic runner actions (no LLM) |

### Step Types
Steps can be either:
1. **Coder steps** — have `prompt_file`, invoke LLM, expect `meta.json` sidecar
2. **Action steps** — have `action` field, call registered Python function directly (no LLM)

Actions are registered in `runner_actions.py::ACTION_REGISTRY`.

## Workflows

### Documentation Governance Workflows

| Workflow | Objective |
|----------|-----------|
| `00_master_docs_bootstrap_v1` | Generate the master system documentation suite for a repository. Scans the codebase, produces project analysis, system overview docs, architecture docs, and validates everything. First-time setup for repos needing comprehensive documentation. |
| `10_execution_scaffold_v1` | Scaffold the delivery documentation system into any target repository. Generates templates, SOP, status rules, agent contracts, and codebase-documentation governance. First step for any new project adopting the orchestration system. |
| `20_initiative_intake_v1` | Convert a draft initiative note into a structured pre-init artifact. Refines through review loops, then promotes to an official initiative document for planning. |
| `21_bug_fix_intake_v1` | Structured bug fix workflow: triage bug, reproduce, isolate root cause, patch, regression validate, then sync documentation. |
| `30_delivery_planning_v1` | Generate a delivery plan and task graph from an approved initiative. Produces plan document, task graph, and associated artifacts through review/refine loops. |
| `31_task_execution_v1` | Execute an approved task: generate implementation plan, review, execute code changes, sync documentation, validate. The core "do the work" workflow. |
| `40_documentation_sync_v1` | Reconcile codebase documentation after implementation changes. Updates inventory and validates freshness. |
| `50_architecture_site_v1` | Publish a browsable HTML architecture site for stakeholders, developers, and operators. |

### Media Generation Workflows

| Workflow | Objective |
|----------|-----------|
| `image_csv_gen_v2` | Batch image description extraction and prompt generation for ComfyUI submission. |
| `videoxpress_gen_v1` | Video generation pipeline: extract narrative from image descriptions, generate workflow, execute T2I/I2V/voiceover, assemble final video. |
| `tiktok_video_pipeline_v1` | TikTok video pipeline: user input → brief → workflow → submit images/videos/voiceover → compose final video. |

### Workflow Order (Typical)
For a new project adopting the system:
1. `10_execution_scaffold_v1` — scaffold the docs system
2. `20_initiative_intake_v1` — capture a requirement
3. `30_delivery_planning_v1` — plan the work
4. `31_task_execution_v1` — execute tasks
5. `40_documentation_sync_v1` — reconcile docs after changes
6. `50_architecture_site_v1` — publish architecture views

### CLI Commands
- `init` — Initialize runner home
- `run` — Run a workflow locally
- `execute-step` — Execute one backend-provided step
- `worker` — Backend-connected worker loop
- `poll` — Single-shot backend poll
- `daemon` — Workstation supervisor
- `bootstrap-publish` — Publish repo-local bootstrap docs into packaged core bundle
- `submit` — Submit jobs
- `workflow-spec` / `sync-workflow-spec` — Workflow specification management
- `approve` — Record human approval

### Adding or Changing Workflows
1. Update workflow definitions in `agent_runner_v2/bootstrap/workflows/default/template_groups.py`
2. Update prompt templates in `agent_runner_v2/bootstrap/workflows/default/prompts/<workflow_name>/`
3. Update tests that validate prompt/runtime assumptions
4. Keep the runtime contract strict: v2 sidecars, deterministic artifact paths, explicit review/refine routing
