# agent-runner-v2

Standalone extraction of the UKBE workflow runner.

## Install

```bash
pip install -e .
```

## Initialize a project workspace

```bash
ukbe-run-agent init
```

This creates a project-local runner home in the current directory:

- `.ukbe-runner/config.json`
- `.ukbe-runner/jobs/`
- `.ukbe-runner/workflows/default/`
- `.ukbe-runner/logs/`

## Run a workflow

The runner supports the same flag-style syntax as the original `agent_runner_v2` CLI.

### Explicit `run` form

```bash
ukbe-run-agent run --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/02_plans/INIT-20260409-01_example.md
```

### Backward-compatible shorthand

```bash
ukbe-run-agent --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/02_plans/INIT-20260409-01_example.md
```

### Target another workspace

```bash
ukbe-run-agent run --project-root /path/to/project --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/02_plans/INIT-20260409-01_example.md
```

### Select a workflow bundle

```bash
ukbe-run-agent run --workflow default --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/02_plans/INIT-20260409-01_example.md
```

## Common commands

```bash
ukbe-run-agent init
ukbe-run-agent run --template-group initiative_intake_v1 --set DRAFT_INIT_FILE=docs/delivery/01_initiatives/draft/example.md
ukbe-run-agent run --project-root /path/to/project --workflow default --template-group task_execution_v1 --task-graph-id TASK-GRAPH-... --task-node-id TASK-...
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --show-job
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --check-job-status
```

Notes:

- `init` defaults to the current directory
- `run` defaults to the current directory
- `--project-root` is optional and only needed when triggering the runner from another location
- `--workflow` selects the workflow bundle declared in that project’s `.ukbe-runner/config.json`
