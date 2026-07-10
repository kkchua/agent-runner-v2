# agent-runner-v2 — QWEN.md

## Project Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE. It runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions.

The package ships a CLI entry point:

- `ukbe-run-agent`

## Core Execution Model

Each workflow step:

1. loads the active workflow bundle
2. renders a prompt from the bundle prompt template
3. invokes a coder or runner action
4. reads a `meta.json` sidecar written by the step
5. validates artifacts and routes to the next step

Key v2 rules:

- `meta.json` sidecar is the only structured result channel
- no markdown write-backs by the runner
- no silent recovery paths
- hard failures route explicitly through runner failure handling

## Runtime Source of Truth

There are two distinct sources:

1. Packaged bootstrap source in this repo
   - `agent_runner_v2/bootstrap/workflows/default/`
2. Runtime workflow bundle used during execution
   - `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`

Runtime prompt/templates are loaded from the global runner home, not from the repo tree directly:

- `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\template_groups.py`
- `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\prompts\...`

The repo bootstrap files only seed those runtime bundles.

## Important Modules

| File | Responsibility |
|---|---|
| `agent_runner_v2/run_agent.py` | CLI entry point and top-level orchestration |
| `agent_runner_v2/step_runner.py` | prompt rendering, sidecar validation, artifact checks |
| `agent_runner_v2/workflow_router.py` | post-step routing for approve/reject/failure cases |
| `agent_runner_v2/job_state.py` | `job.json` lifecycle management |
| `agent_runner_v2/coder_adapters.py` | Claude/Codex/Qwen invocation and polling |
| `agent_runner_v2/template_groups.py` | package-local workflow definition mirror |
| `agent_runner_v2/bundle_loader.py` | bootstrap seeding and workflow bundle loading |
| `agent_runner_v2/runtime_context.py` | active workflow/runtime path context |
| `agent_runner_v2/actions/` | deterministic runner actions |

## Runner Home Initialization

Initialize the runner with:

```bash
ukbe-run-agent init
```

This seeds the global runner home under `%USERPROFILE%\.ukbe-runner`:

- `%USERPROFILE%\.ukbe-runner\config.json`
- `%USERPROFILE%\.ukbe-runner\jobs\`
- `%USERPROFILE%\.ukbe-runner\workflows\example\`
- `%USERPROFILE%\.ukbe-runner\logs\`

## Main Workflow Families

### `initiative_intake_v1`
- draft initiative intake and pre-init refinement

### `delivery_planning_v1`
- plan generation
- task-graph generation
- task contract generation
- documentation strategy decomposition

### `task_execution_v1`
- implementation planning
- implementation review/refinement
- execution
- documentation sync
- validation

### `delivery_scaffold_v1`
- scaffolds `docs/delivery/` and `docs/codebase/` governance
- generates templates, SOPs, status rules, and agent contracts

### `documentation_sync_v1` / `40_documentation_sync_v1`
- documentation-only repository reconciliation and validation flow

### `50_architecture_site_v1`
- publishes browsable HTML architecture views for stakeholders, developers, operators, and functional consumers

## Documentation Governance

Current delivery lifecycle:

1. `initiative_intake_v1`
   - captures requirement and documentation scope
2. `delivery_planning_v1`
   - turns documentation scope into plan/task obligations
3. `task_execution_v1`
   - executes code and documentation updates together
4. `documentation_sync_v1`
   - reconciles the codebase inventory and stale guidance after drift or contract changes
5. `architecture_site_v1`
   - publishes the HTML architecture communication layer for human readers

Current documentation governance lives under:

- `docs/delivery/`
- `docs/codebase/`

## Artifact Coverage

Common delivery artifacts:

- `DRAFT_INIT_FILE`
- `PRE_INIT_FILE`
- `INIT_FILE`
- `PLAN_FILE`
- `TASK_GRAPH_FILE`
- `TASK_FILE`
- `IMPL_FILE`
- `REVIEW_FILE`
- `VALIDATION_FILE`

Scaffold/codebase-governance artifacts:

- `PROJECT_ANALYSIS`
- `DELIVERY_SOP`
- `DELIVERY_STATUS_RULES`
- `DELIVERY_TEMPLATE_REGISTRY`
- `DELIVERY_VALIDATION_TEMPLATE`
- `DELIVERY_AGENTS`
- `CODEBASE_DOC_SOP`
- `CODEBASE_DOC_STATUS_RULES`
- `CODEBASE_TEMPLATE_REGISTRY`
- `CODEBASE_INVENTORY_TEMPLATE`
- `CODEBASE_MODULE_TEMPLATE`
- `CODEBASE_COMPONENT_TEMPLATE`
- `CODEBASE_CHANGE_TEMPLATE`
- `CODEBASE_INVENTORY`
- `CODEBASE_CHANGE_IMPACT`
- `DELIVERY_FOLDER_MAP`

## Development Guidance

When adding or changing a workflow:

1. update bootstrap workflow definitions in `agent_runner_v2/bootstrap/workflows/default/template_groups.py`
2. update bootstrap prompt templates in `agent_runner_v2/bootstrap/workflows/default/prompts/<workflow_name>/`
3. update tests that validate prompt/runtime assumptions
4. keep the runtime contract strict: v2 sidecars, deterministic artifact paths, explicit review/refine routing

Do not treat package-local prompt folders as runtime sources. The runtime source of truth is the global workflow bundle under `%USERPROFILE%\.ukbe-runner\workflows\...`.

## Testing

Run:

```bash
pip install -e ".[dev]"
pytest
```
