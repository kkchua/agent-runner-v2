# sdlc_60_execution_v1 — Task Execution

## Purpose

Executes tasks following an approved implementation plan, producing an approved EXEC document and actual code changes. This is the **coding step** of the SDLC chain.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `IMPL_FILE` from `sdlc_50_implementation_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `IMPL_FILE` | `50_implementations/IMPL-{date}-001-{seq}_{slug}.md` | Approved implementation plan from sdlc_50 |

## Outputs

| Artifact | Path |
|----------|------|
| `EXEC_FILE` | `60_executions/EXEC-{date}-001-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-60-exec.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{slug}-REV-60-exec.md` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `execute_task` | Prompt | architect | Execute implementation, produce EXEC report |
| 2 | `technical_critique` | Prompt | reviewer | Compare execution against plan (loop → step 4, max 2) |
| 3 | `internal_review` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_execution` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_execution` | Action | — | Copy to `60_executions/` |
| 6 | `stepCompletion` | Action | — | Terminal |

**Differences from sdlc_00–sdlc_50:**
- Step 1 is `execute_task` (actual coding), not `generate_*`
- Critique and review require both `EXEC_FILE` and `IMPL_FILE` (compares execution against plan)
- On critique rejection → loops to `refine_execution` (not back to `execute_task`)

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_60_execution_v1 \
  --input IMPL_FILE=docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260801-001-001_my-initiative.md
```

## Next Workflow

→ `sdlc_70_validation_v1` (takes `EXEC_FILE` as input)
