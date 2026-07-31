# sdlc_80_review_v1 — Final Review & Closure

## Purpose

Generates review, memory, and closure documents from approved validation, producing approved REV, MEM, and CLOSE documents. This is the **final workflow** in the SDLC delivery chain.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `VAL_FILE` from `sdlc_70_validation_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `VAL_FILE` | `70_validations/VAL-{date}-{seq}_{slug}.md` | Approved validation from sdlc_70 |

## Outputs

| Artifact | Path |
|----------|------|
| `REV_FILE` | `80_reviews/REV-{date}-{seq}_{slug}.md` |
| `MEM_FILE` | `80_reviews/MEM-{date}-{seq}_{slug}.md` |
| `CLOSE_FILE` | `80_reviews/CLOSE-{date}-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-80-rev.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{job_id}-REV-80-all.md` |

**Unique:** This workflow produces **3 artifacts** (REV + MEM + CLOSE) in a single run.

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_review` | Prompt | architect | Generate REV, MEM, and CLOSE documents |
| 2 | `technical_critique` | Prompt | reviewer | Review all 3 documents (loop → step 4, max 2) |
| 3 | `review_all` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_documents` | Prompt | architect | Fix all 3 docs per review (loop → step 3, max 2) |
| 5 | `promote_all` | Action | — | Copy all 3 to `80_reviews/` |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_80_review_v1 \
  --input VAL_FILE=docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260801-001_my-initiative.md
```

## End of Chain

This is the final workflow. After completion, the full SDLC delivery chain is done:

```
DRAFT_INIT → INIT → REQ → PLAN → BACKLOG → TASK → IMPL → EXEC → VAL → REV + MEM + CLOSE
```
