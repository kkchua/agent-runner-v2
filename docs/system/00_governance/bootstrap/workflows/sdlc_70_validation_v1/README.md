# sdlc_70_validation_v1 — Validation Report

## Purpose

Generates a validation report from approved execution documents, producing an approved VAL document. Verifies that the implementation meets the original requirements.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `EXEC_FILE` from `sdlc_60_execution_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `EXEC_FILE` | `60_executions/EXEC-{date}-001-{seq}_{slug}.md` | Approved execution report from sdlc_60 |

## Outputs

| Artifact | Path |
|----------|------|
| `VAL_FILE` | `70_validations/VAL-{date}-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-70-val.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{slug}-REV-70-val.md` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_validation` | Prompt | architect | Generate validation report from EXEC |
| 2 | `technical_critique` | Prompt | reviewer | Internal quality gate (loop → step 4, max 2) |
| 3 | `review_validation` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_validation` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_validation` | Action | — | Copy to `70_validations/` |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_70_validation_v1 \
  --input EXEC_FILE=docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260801-001-001_my-initiative.md
```

## Next Workflow

→ `sdlc_80_review_v1` (takes `VAL_FILE` as input)
