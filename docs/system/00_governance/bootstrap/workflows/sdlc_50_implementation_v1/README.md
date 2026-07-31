# sdlc_50_implementation_v1 — Implementation Planning

## Purpose

Generates an implementation plan from an approved task, producing an approved IMPL document. Defines the technical approach, file changes, and execution steps.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `TASK_FILE` from `sdlc_40_task_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `TASK_FILE` | `40_tasks/{work_item}.md` | Approved task from sdlc_40 |

## Outputs

| Artifact | Path |
|----------|------|
| `IMPL_FILE` | `50_implementations/IMPL-{date}-001-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-50-impl.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{slug}-REV-50-impl.md` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_implementation` | Prompt | architect | Generate implementation plan from task |
| 2 | `technical_critique` | Prompt | reviewer | Internal quality gate (loop → step 1, max 2) |
| 3 | `review_implementation` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_implementation` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_implementation` | Action | — | Copy to `50_implementations/` |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_50_implementation_v1 \
  --input TASK_FILE=docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-my-initiative-001.md
```

## Next Workflow

→ `sdlc_60_execution_v1` (takes `IMPL_FILE` as input)
