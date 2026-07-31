# sdlc_40_task_v1 — Task Specification

## Purpose

Generates task specifications from an approved backlog, producing approved TASK documents. Each task corresponds to a work item identified by a unique work item ID.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `BACKLOG_FILE` from `sdlc_30_backlog_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `BACKLOG_FILE` | `30_backlogs/BACKLOG-{date}-{seq}_{slug}.md` | Approved backlog from sdlc_30 |
| `WORK_ITEM` (optional) | State artifact | Specific work item ID to decompose (e.g., `WI-my-initiative-001`) |

## Outputs

| Artifact | Path |
|----------|------|
| `TASK_FILE` | `40_tasks/{work_item}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{work_item}-CRITIQUE-40-task.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{work_item}-REV-40-task.md` |

**Note:** This workflow uses `{work_item}` naming (e.g., `WI-my-initiative-001.md`) instead of the date-seq-slug pattern used by other workflows.

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_task` | Prompt | architect | Generate task spec from backlog item |
| 2 | `technical_critique` | Prompt | reviewer | Internal quality gate (loop → step 1, max 2) |
| 3 | `review_task` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_task` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_task` | Action | — | Copy to `40_tasks/` |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_40_task_v1 \
  --input BACKLOG_FILE=docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260801-001_my-initiative.md \
  --input WORK_ITEM=WI-my-initiative-001
```

## Next Workflow

→ `sdlc_50_implementation_v1` (takes `TASK_FILE` as input)
