# Submit Job Manual

## Purpose

This manual describes how to submit backend-driven workflow runs with `ukbe-run-agent submit` under the **current** implementation.

Use it when you want to:

- create a new backend run manually from CLI
- understand the payload fields sent to `/api/runs`
- know which input parameters are currently required for each workflow
- avoid creating runs that are accepted by the backend but fail later during execution

This document describes the current operational contract, even where that contract is more cumbersome than the desired future design.

For workstation daemon setup and child execution visibility, use [worker_supervisor_manual.md](worker_supervisor_manual.md).

## Important Behavior

The submit API is generic.

It validates:

- workflow exists
- workflow has steps
- `initiative_intake_v1` duplicate draft protection

It does **not** fully validate workflow-specific input requirements at submission time.

That means a run can be created successfully and still fail later when the first worker step starts.

The real workflow contract comes from:

- workflow `job_init_inputs`
- first-step `required_inputs`
- first-step preflight rules
- workflow-specific context expectations used by backend-driven execution

## Command Shape

```bash
ukbe-run-agent submit --workflow-name <workflow> [options]
```

Example:

```bash
ukbe-run-agent submit \
  --workflow-name delivery_planning_v1 \
  --project-root /path/to/project \
  --input INIT_FILE=docs/delivery/01_initiatives/INIT-20260611-01_example.md
```

## General Submit Options

### Required

- `--workflow-name`

### Common optional run-routing options

- `--project-root`
- `--workspace-path`
- `--initiative-id`
- `--worker-id`
- `--worker-label`
- `--assigned-provider`
- `--coder`
- `--repo-url`
- `--repo-ref`
- `--backend-url`

### Payload options

- `--input KEY=VALUE`
  - adds entries to `input_payload`
- `--context KEY=VALUE`
  - adds entries to `context_payload`
- `--env KEY=VALUE`
  - adds entries to `env_overrides`

Repeat these flags for multiple keys.

## Default Resolution

If not passed explicitly, `submit` resolves settings from:

1. CLI flags
2. environment variables
3. `.ukbe-runner/engine/config.json`
4. hardcoded defaults

Notable defaults:

- `backend_url`
  - from `AGENT_RUNNER_BACKEND_URL` or config `backend_url`
  - fallback `http://localhost:8100`
- `worker_id`
  - from `AGENT_RUNNER_WORKER_ID` or config `worker_id`
- `worker_label`
  - from `WORKER_LABEL` or config `worker_label`
  - fallback `live`

## Live Workflow Introspection

If the backend is running, inspect the workflow definition directly:

```bash
curl -s http://localhost:8100/api/workflows/delivery_planning_v1 | jq .
```

Useful fields:

- `job_init_step`
- `job_init_inputs`
- `steps`
- `raw_definition.step_configs`
- `artifact_rules`

This is the best live source of truth for what the backend currently knows.

## Current Workflow Input Reference

## `initiative_intake_v1`

### Current required submit inputs

- `input_payload.DRAFT_INIT_FILE`

CLI example:

```bash
ukbe-run-agent submit \
  --workflow-name initiative_intake_v1 \
  --project-root /path/to/project \
  --input DRAFT_INIT_FILE=docs/delivery/01_initiatives/draft/INIT-DRAFT-20260611-01_example.md
```

### Practical notes

- the draft file must exist and be readable by the worker
- this is the cleanest workflow today because the seed input is a single file path
- the backend rejects duplicate terminal reprocessing of the same draft file path for this workflow

## `delivery_planning_v1`

### Current required submit inputs

- `input_payload.INIT_FILE`

CLI example:

```bash
ukbe-run-agent submit \
  --workflow-name delivery_planning_v1 \
  --project-root /path/to/project \
  --input INIT_FILE=docs/delivery/01_initiatives/INIT-20260611-01_example.md
```

### Practical notes

- the init document must exist and be readable by the worker
- execution preflight expects the init artifact to be in an approved state
- if your project uses scaffolded delivery templates, downstream validation may also depend on files already existing under `docs/delivery/00_templates/`

## `task_execution_v1`

### Current behavior

This is the most cumbersome workflow today.

The current backend-driven path still depends on both:

- seed file inputs
- extra execution context values

This happens because the generated documents preserve lineage mostly by document ID, not by full source filename/path. As a result, the worker cannot always derive everything it needs from one referenced file alone.

### Current required submit data

Input payload:

- `input_payload.PLAN_FILE`
- `input_payload.TASK_GRAPH_FILE`

Context payload:

- `context_payload.CURRENT_TASK_NODE_ID`
- `context_payload.SOURCE_TASK_GRAPH_ID`

Strongly recommended context:

- `context_payload.PLAN_ID`
- `context_payload.CURRENT_TASK_TITLE`

### Why these are needed today

- `TASK_GRAPH_FILE` is needed as the primary file reference for task decomposition lineage
- `CURRENT_TASK_NODE_ID` is needed because one task graph contains multiple tasks
- `SOURCE_TASK_GRAPH_ID` is currently used as explicit lineage context
- `PLAN_FILE` is currently passed because task execution still expects planning lineage artifacts to be available
- `PLAN_ID` and `CURRENT_TASK_TITLE` are often derived by operators today from the referenced documents because the current submit path does not reliably derive them automatically in all cases

### Current operator workflow

In practice, a user often has to:

1. locate the relevant plan document
2. open the plan document and read the `Plan ID`
3. locate the related task graph document
4. open the task graph and read the `Task Graph ID`
5. identify the desired task node ID inside the task graph
6. optionally read the task title for that node
7. pass those values to `ukbe-run-agent submit`

That manual lookup burden is real and is the main reason this workflow should be simplified later.

### CLI example

```bash
ukbe-run-agent submit \
  --workflow-name task_execution_v1 \
  --project-root /path/to/project \
  --input PLAN_FILE=docs/delivery/02_plans/PLAN-20260610-01_step-log-tail-api.md \
  --input TASK_GRAPH_FILE=docs/delivery/02_plans/artifacts/TASK-GRAPH-20260610-PLAN-20260610-01.md \
  --context CURRENT_TASK_NODE_ID=TASK-20260610-01 \
  --context SOURCE_TASK_GRAPH_ID=TASK-GRAPH-20260610-PLAN-20260610-01 \
  --context PLAN_ID=PLAN-20260610-01 \
  --context CURRENT_TASK_TITLE=Implement-Step-Log-Tail-Route
```

### Practical notes

- `TASK_GRAPH_FILE` should correspond to the selected planning lineage
- `CURRENT_TASK_NODE_ID` must identify a real task node in that task graph
- `PLAN_FILE` should match the same task graph lineage
- if any of these values are mismatched, the run may be created but fail later during worker execution

## `image_csv_gen_v1`

### Current required submit inputs

- `input_payload.IMAGE_FOLDER`

CLI example:

```bash
ukbe-run-agent submit \
  --workflow-name image_csv_gen_v1 \
  --project-root /path/to/project \
  --input IMAGE_FOLDER=source_images/20260611-01
```

### Practical notes

- `IMAGE_FOLDER` must exist and be readable by the worker
- later `submit_prompts` step requires ComfyUI credentials and config
- if credentials are missing, the run may be created successfully but fail later during action execution

## `image_csv_gen_v2`

### Current required submit inputs

- `input_payload.IMAGE_FOLDER`

CLI example:

```bash
ukbe-run-agent submit \
  --workflow-name image_csv_gen_v2 \
  --project-root /path/to/project \
  --input IMAGE_FOLDER=source_images/20260611-01
```

### Practical notes

- `IMAGE_FOLDER` must exist and be readable by the worker
- later `submit_prompts` step requires ComfyUI credentials and config

## `delivery_scaffold_v1`

### Current required submit inputs

No seed artifact input is required.

Under the current workflow definition:

- `job_init_inputs = []`
- first step is `project_analysis`
- `project_analysis` auto-discovers repository context files

So unlike `initiative_intake_v1`, `delivery_planning_v1`, and `task_execution_v1`, this workflow does not require `--input KEY=VALUE` to start.

### Current practical submit requirement

In practice, you should provide:

- `--project-root /path/to/target-repo`

CLI example:

```bash
ukbe-run-agent submit \
  --workflow-name delivery_scaffold_v1 \
  --project-root /path/to/target-repo
```

Editable helper script:

```bash
bash scripts/submit-delivery-scaffold.sh
```

### What the workflow reads automatically

The first step scans the target repository for usable project context, typically including:

- `README.md`
- `QWEN.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.cursorrules`
- `.github/copilot-instructions.md`
- project metadata such as `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Gemfile`
- architecture/design/spec docs under `docs/`
- any existing `docs/delivery/` content

### What this workflow produces

The workflow generates and publishes:

- `PROJECT_ANALYSIS`
- `WORKFLOW_SOP_v1.md`
- `DELIVERY_STATUS_RULES_v1.md`
- delivery document templates under `docs/delivery/00_templates/`
- agent contracts under `docs/delivery/08_agents/`
- final structural validation output

Working files are first produced under `.ukbe-runner/jobs/...` and then copied into `docs/delivery/...` according to the scaffold artifact publish rules.

### Current review and validation flow

The workflow runs these major phases:

1. `project_analysis`
2. `generate_sop` -> `review_sop` -> optional `refine_sop` / `replan_sop`
3. `generate_templates` -> `review_templates` -> optional `refine_templates`
4. `generate_agents` -> `review_agents` -> optional `refine_agents`
5. `validate_delivery_docs`

`validate_delivery_docs` is a deterministic runner action, not a coder step.

### Practical notes

- this is currently the simplest backend submit workflow in the repo
- no lineage IDs or document selectors are required from the operator
- the target repository must contain enough readable context for `project_analysis`
- if the repository has no usable context files, the run may be created successfully but reject during the first step

### Current limitation

Manual local `run` mode has richer cross-repo behavior through `--target-project-root`.

`submit` currently sends only the backend run payload and does not expose an equivalent dedicated scaffold-target argument. So for backend submit today, `--project-root` is the practical repository root to use for scaffold execution.

## Current Meaning of `--input` vs `--context`

Under the current implementation:

- `--input` is used for seed artifacts and primary file references
- `--context` is still used by some backend-driven execution paths for lineage and task-selection values
- `--env` is used for runtime overrides passed to worker execution

This split is most visible in `task_execution_v1`.

## Common Failure Pattern

A run can be created successfully, then fail when the worker starts the first step.

Typical causes:

- missing required seed artifact path
- wrong path relative to `project_root`
- `task_execution_v1` lineage values missing or mismatched
- reference files missing for downstream workflow preflight
- external credentials missing for image submission workflows

## Verification Checklist

Before submitting a run, check:

1. workflow name exists in backend
2. required file-path inputs are present
3. referenced files exist under the target `project_root`
4. `worker_label` matches an active worker queue
5. `worker_id` is set only if you intentionally want to pin the run to one workstation
6. for `task_execution_v1`, document IDs and task node ID match the referenced files
7. image workflows have ComfyUI credentials available before they reach the submit action

## Related Documents

- Operator manual: [worker_supervisor_manual.md](worker_supervisor_manual.md)
- Delivery scaffold guide: [../HOW_TO_GUIDE.md](../HOW_TO_GUIDE.md)
