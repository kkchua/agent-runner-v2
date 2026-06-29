# agent-runner-v2

Standalone runner runtime for local workflow execution and backend-connected worker operation.

## What This Repo Is For

`agent-runner-v2` currently supports three primary usage modes:

- Manual workflow execution with `ukbe-run-agent run`
- Backend-connected single-step execution with `ukbe-run-agent worker`, `poll`, and `execute-step`
- Workstation supervision with `ukbe-run-agent daemon`

The backend is the source of truth for runs, step runs, artifacts, events, and approvals. The runner is responsible for prompt rendering, coder/action execution, output validation, and step result submission.

## Install

```bash
pip install -e .
```

## Initialize the Runner Home

```bash
ukbe-run-agent init
```

This seeds the global runner home under `%USERPROFILE%\.ukbe-runner`:

- `%USERPROFILE%\.ukbe-runner\config.json`
- `%USERPROFILE%\.ukbe-runner\jobs\`
- `%USERPROFILE%\.ukbe-runner\workflows\example\`
- `%USERPROFILE%\.ukbe-runner\logs\`

Runtime workflow definitions and prompt templates are loaded from:

- `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\template_groups.py`
- `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\prompts\...`

The packaged bootstrap source in this repo exists only to seed those global workflow bundles:

- `agent_runner_v2/bootstrap/workflows/default/...`

## Current CLI Modes

### Local workflow execution

```bash
ukbe-run-agent run --template-group initiative_intake_v1 --set DRAFT_INIT_FILE=docs/delivery/01_initiatives/draft/example.md
```

### Backend-connected one-shot worker poll

```bash
ukbe-run-agent poll --backend-url http://127.0.0.1:8100 --worker-id kode-worker-01
```

### Backend-connected worker loop

```bash
ukbe-run-agent worker --backend-url http://127.0.0.1:8100 --worker-id kode-worker-01
```

### Daemon supervisor

```bash
ukbe-run-agent daemon kode-worker-01
```

The daemon is a workstation supervisor. It claims work, spawns child `execute-step` processes, tracks child state, writes logs, and emits child-scoped heartbeats keyed by `workflow_step_run_id`.

## Common Commands

```bash
ukbe-run-agent init
ukbe-run-agent run --template-group delivery_planning_v1 --set INIT_FILE=docs/delivery/01_initiatives/INIT-...md
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --show-job
ukbe-run-agent run --template-group delivery_planning_v1 --job-id PLAN-... --check-job-status
ukbe-run-agent execute-step --request-file /tmp/request.json --result-file /tmp/result.json
ukbe-run-agent worker --backend-url http://127.0.0.1:8100 --worker-id kode-worker-01 --once
ukbe-run-agent daemon kode-worker-01 --backend-url http://127.0.0.1:8100
```

## Documentation

- Submit job manual: [docs/submit_job_manual.md](docs/submit_job_manual.md)
- Operator manual: [docs/worker_supervisor_manual.md](docs/worker_supervisor_manual.md)
- Delivery scaffold workflow guide: [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md)
- Backend-alignment design notes: [docs/backend_alignment_refactor_plan.md](docs/backend_alignment_refactor_plan.md)

## Notes

- `run` defaults to the current directory unless `--project-root` is provided.
- `worker`, `poll`, and `daemon` are for backend-driven execution.
- The daemon uses a stable workstation `worker_id`; it does not generate per-child worker IDs.
- Operational visibility is available from local daemon/child logs and backend run events.
- Runtime workflow prompts are not loaded from this repo tree directly; they are loaded from the global `.ukbe-runner/workflows/...` bundle.
