# plan_first_review_v1 — Plan-First Review

Automated plan-first review process with Codex reviewer and Qwen planner.

## Overview

This workflow implements a structured plan-first review cycle:

1. **Prepare** — Allocate a Planning folder, copy the raw request
2. **Formalize Requirements** — Codex (reviewer role) formalizes the raw request into structured requirements
3. **Generate Plan** — Qwen (planner role) generates an implementation plan from requirements
4. **Codex Review** — Codex reviews the plan; human approval required after this step
5. **Refine Plan** — If Codex rejects, Qwen refines the plan (up to 10 iterations, 3 human rejections)
6. **Promote** — Approved plan is promoted for implementation

## Roles

| Step | Coder Role | Policy |
|------|-----------|--------|
| formalize_requirements | Codex | reviewer_standard |
| generate_plan | Qwen | plan_standard |
| codex_review | Codex | reviewer_standard |
| refine_plan | Qwen | plan_standard |

## Artifacts

| Key | Description |
|-----|-------------|
| `RAW_REQUEST_FILE` | Input: raw request markdown file |
| `PLANNING_FOLDER` | Allocated Planning folder (e.g., `Planning/20261025-01_slug`) |
| `REQUIREMENTS_FILE` | Formalized requirements (baseline-aware path) |
| `QWEN_PLAN_FILE` | Qwen's implementation plan (versioned: `Qwen_Plan_v01.md`) |
| `CODEX_REVIEW_FILE` | Codex's review output (versioned: `Codex_Review_v01.md`) |

## Configuration

### Workflow-Level Flags

- `enable_unauthorized_write_detection = true` — After each prompt-driven step, snapshots all files and verifies the coder only wrote to allowed paths (Planning folder + step dir). Detection is post-hoc reporting; it does not prevent writes at the filesystem level.

### Refinement Limits

| Parameter | Value |
|-----------|-------|
| max_iterations | 10 |
| max_refinements | 10 |
| max_human_rejections | 3 |
| max_ceiling | 20 |

## Path Constants

All paths use the layered constant system in `agent_runner_v2/constants.py`:

- `PLANNING_BASE` — "Planning" directory name
- `ARTIFACT_PATH_RAW_REQUEST(folder)` — `{folder}/request.md`
- `ARTIFACT_PATH_REQUIREMENTS(folder, baseline)` — baseline-aware requirements path
- `ARTIFACT_PATH_QWEN_PLAN(folder, revision, baseline)` — versioned plan path
- `ARTIFACT_PATH_CODEX_REVIEW(folder, revision, baseline)` — versioned review path

Baseline 1 artifacts sit at the Planning folder root; baseline 2+ go into `baseline_NN/` subdirectories.

## Folder Allocation

The `prepare_request` action claims Planning folders atomically using `mkdir(exist_ok=False)`. If two jobs race for the same folder name, the loser retries with the next sequence number.

## Operator Commands

Three intervention commands are available during workflow execution.

### continue-refinement

Extends the cumulative refinement limit beyond the default maximum. Use when the plan needs more iterations than originally allowed.

```bash
ukbe-run-agent continue-refinement --job-id <ID> --additional-allowance <N> [--reason <TEXT>]
```

- **Available when:** Job is `plan_first_review_v1`, status is `WAITING_FOR_HUMAN_INTERVENTION` due to cumulative refinement exhaustion (`last_failure_code = PLAN_REFINEMENT_EXHAUSTED`), `--additional-allowance` is a positive integer, and the resulting effective limit does not exceed `max_ceiling` (default 20).
- **Effect:** Adds `N` to the effective refinement limit for the `codex_review` step's `on_reject_refine` routing, resets per-step reject counts, and reconstructs the refine loop context.
- **Limit:** Only valid for `plan_first_review_v1`. Errors if the job was paused for any reason other than cumulative exhaustion, if the allowance is non-positive, or if the ceiling would be exceeded.

### stop-and-archive

Sets the job to `STOPPED_ARCHIVED` terminal status. The job cannot be resumed.

```bash
ukbe-run-agent stop-and-archive --job-id <ID> --reason <TEXT>
```

- **Available when:** Job exists and is not already `STOPPED_ARCHIVED`.
- **Effect:** Sets `job_status = STOPPED_ARCHIVED` (terminal). Records the reason.
- **Limit:** Works for any workflow. Irreversible — the job cannot be restarted or continued.

### change-requirements

Creates a new requirements baseline when the original requirements change mid-cycle.

```bash
ukbe-run-agent change-requirements --job-id <ID> --new-requirements-file <PATH> --reason <TEXT>
```

- **Available when:** Job is `plan_first_review_v1` and is NOT `STOPPED_ARCHIVED`.
- **Effect:** Increments `requirements_baseline`, copies the new file as the baseline request, and resets the step to `formalize_requirements` for the new baseline.
- **Limit:** Only valid for `plan_first_review_v1`. Blocked if the job is `STOPPED_ARCHIVED` (terminal).

## Running

```bash
# Via CLI
ukbe-run-agent run --template-group plan_first_review_v1 --set RAW_REQUEST_FILE=path/to/request.md

# Via Operator Console
# Select workflow: plan_first_review_v1
# Select implementation: standard
# Provide: RAW_REQUEST_FILE path
```

## Files

| File | Purpose |
|------|---------|
| `workflow.toml` | Step definitions, routing, coder roles, refinement limits |
| `actions.py` | prepare_request, promote_plan, step_completion actions |
| `context_extensions.py` | Artifact path resolution per step |
| `impls/standard/impl.yaml` | Standard implementation slot bindings |
| `prompts/*/standard.txt` | Prompt templates for each prompt-driven step |
