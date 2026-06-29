# agent_runner_v2 — QWEN.md

## Project Overview

`agent_runner_v2` is the Python package that implements the standalone LLM workflow runner. It executes structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with deterministic runner actions, review loops, retries, and approval gates.

The package exposes:

- `ukbe-run-agent`

## Core Execution Model

Each workflow step:

1. loads the active runtime workflow bundle
2. renders a prompt from that bundle
3. invokes a coder or runner action
4. reads a `meta.json` sidecar
5. validates artifacts and routes to the next step

Key rules:

- `meta.json` is the only structured result channel
- the runner does not write back into markdown artifacts before or after invocation
- failures are explicit and routed through runner failure handling

## Runtime Source of Truth

There are two distinct sources:

1. Packaged bootstrap source inside this package
   - `bootstrap/workflows/default/`
2. Runtime workflow bundle used during execution
   - `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`

Prompt/templates are loaded from the runtime bundle, not directly from the package tree:

- `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\template_groups.py`
- `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\prompts\...`

The bootstrap files only seed those runtime bundles.

## Important Modules

| File | Responsibility |
|---|---|
| `run_agent.py` | CLI entry point and top-level orchestration |
| `step_runner.py` | prompt rendering, sidecar validation, artifact checks |
| `workflow_router.py` | post-step routing for approve/reject/failure cases |
| `job_state.py` | `job.json` lifecycle management |
| `coder_adapters.py` | Claude/Codex/Qwen invocation and polling |
| `template_groups.py` | package-local workflow definition mirror |
| `bundle_loader.py` | bootstrap seeding and workflow bundle loading |
| `runtime_context.py` | active workflow/runtime path context |
| `artifact_paths.py` | artifact path computation |
| `actions/` | deterministic runner actions |

## Runner Home Initialization

Initialize with:

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

### `documentation_sync_v1`
- documentation-only synchronization and validation flow

## Documentation Governance

Current lifecycle:

1. `initiative_intake_v1`
   - captures requirement and documentation scope
2. `delivery_planning_v1`
   - turns documentation scope into plan/task obligations
3. `task_execution_v1`
   - executes code and documentation updates together
4. validation
   - rejects stale or missing codebase docs

Current governance lives under:

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
- `DELIVERY_AGENTS_MD`
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

1. update bootstrap workflow definitions in `bootstrap/workflows/default/template_groups.py`
2. update bootstrap prompt templates in `bootstrap/workflows/default/prompts/<workflow_name>/`
3. update tests that validate prompt/runtime assumptions
4. keep the runtime contract strict: v2 sidecars, deterministic artifact paths, explicit review/refine routing

Do not treat package-local prompt folders as runtime sources. The runtime source of truth is the global workflow bundle under `%USERPROFILE%\.ukbe-runner\workflows\...`.

## Testing

Run from the repo root:

```bash
pip install -e ".[dev]"
pytest
```
