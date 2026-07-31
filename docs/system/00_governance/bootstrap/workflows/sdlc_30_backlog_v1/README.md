# sdlc_30_backlog_v1 — Backlog Generation

## Purpose

Generates a backlog from an approved plan, producing an approved BACKLOG document. Decomposes the plan into actionable work items.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `PLAN_FILE` from `sdlc_20_planning_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `PLAN_FILE` | `20_plans/PLAN-{date}-{seq}_{slug}.md` | Approved plan from sdlc_20 |

## Outputs

| Artifact | Path |
|----------|------|
| `BACKLOG_FILE` | `30_backlogs/BACKLOG-{date}-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-30-backlog.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{slug}-REV-30-backlog.md` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_backlog` | Prompt | architect | Decompose plan into backlog items |
| 2 | `technical_critique` | Prompt | reviewer | Internal quality gate (loop → step 1, max 2) |
| 3 | `review_backlog` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_backlog` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_backlog` | Action | — | Copy to `30_backlogs/` |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_30_backlog_v1 \
  --input PLAN_FILE=docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260801-001_my-initiative.md
```

## Special Context

This workflow injects a `BACKLOG_STEM` context variable extracted from the BACKLOG_FILE path. This is used downstream by `sdlc_40_task_v1` for work item ID generation.

## Next Workflow

→ `sdlc_40_task_v1` (takes `BACKLOG_FILE` as input)
