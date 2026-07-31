# sdlc_00_init_doc_v1 — Initiative Intake

## Purpose

Captures and structures an initiative from a user-provided draft input, producing an approved INIT document. This is the **entry point** of the SDLC delivery chain.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run (templates must exist)
- A draft initiative file exists in `00_draft_initiatives/`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `DRAFT_INIT_FILE` | `00_draft_initiatives/DRAFT-INIT-{date}-{seq}_{slug}.md` | User-provided draft |

## Outputs

| Artifact | Path |
|----------|------|
| `INIT_FILE` | `00_initiatives/INIT-{date}-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-00-init.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{slug}-REV-00-init.md` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_initiative` | Prompt | architect | Structure draft into INIT document |
| 2 | `technical_critique` | Prompt | reviewer | Internal quality gate (loop → step 1, max 2) |
| 3 | `review_initiative` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_initiative` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_initiative` | Action | — | Copy to `00_initiatives/` with approved status |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_00_init_doc_v1 \
  --input DRAFT_INIT_FILE=docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/DRAFT-INIT-20260801-001_my-initiative.md
```

## Next Workflow

→ `sdlc_10_requirement_v1` (takes `INIT_FILE` as input)
