# sdlc_20_planning_v1 — Solution Architecture Planning

## Purpose

Generates a solution architecture plan from approved requirements, producing an approved PLAN document.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `REQ_FILE` from `sdlc_10_requirement_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `REQ_FILE` | `10_requirements/REQ-{date}-{seq}_{slug}.md` | Approved requirements from sdlc_10 |

## Outputs

| Artifact | Path |
|----------|------|
| `PLAN_FILE` | `20_plans/PLAN-{date}-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-20-plan.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{slug}-REV-20-plan.md` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_plan` | Prompt | architect | Generate solution architecture from REQ |
| 2 | `technical_critique` | Prompt | reviewer | Internal quality gate (loop → step 1, max 2) |
| 3 | `review_plan` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_plan` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_plan` | Action | — | Copy to `20_plans/` |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_20_planning_v1 \
  --input REQ_FILE=docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260801-001_my-initiative.md
```

## Next Workflow

→ `sdlc_30_backlog_v1` (takes `PLAN_FILE` as input)
