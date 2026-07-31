# sdlc_10_requirement_v1 — Requirement Generation

## Purpose

Generates structured requirements from an approved initiative document, producing an approved REQ document.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Approved `INIT_FILE` from `sdlc_00_init_doc_v1`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| `INIT_FILE` | `00_initiatives/INIT-{date}-{seq}_{slug}.md` | Approved initiative from sdlc_00 |

## Outputs

| Artifact | Path |
|----------|------|
| `REQ_FILE` | `10_requirements/REQ-{date}-{seq}_{slug}.md` |
| `CRITIQUE_FILE_SUGGESTED` | `80_reviews/{slug}-CRITIQUE-10-req.md` |
| `REVIEW_FILE_SUGGESTED` | `80_reviews/{slug}-REV-10-req.md` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_requirements` | Prompt | architect | Generate requirements from INIT |
| 2 | `technical_critique` | Prompt | reviewer | Internal quality gate (loop → step 1, max 2) |
| 3 | `review_requirements` | Prompt | reviewer | Human approval gate **[HUMAN GATE]** |
| 4 | `refine_requirements` | Prompt | architect | Fix per review (loop → step 3, max 2) |
| 5 | `promote_requirements` | Action | — | Copy to `10_requirements/` |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_10_requirement_v1 \
  --input INIT_FILE=docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-001_my-initiative.md
```

## Next Workflow

→ `sdlc_20_planning_v1` (takes `REQ_FILE` as input)
