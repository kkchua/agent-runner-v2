# 01_governance_foundation_v1 — Governance Foundation (BCS-compliant)

## Purpose

Generates, validates, audits, and publishes the Layer 1 governance foundation set — the conceptual governance framework (layer model, document authority, bundle taxonomy, governance lifecycle, metadata standard) that all other layers build upon.

## Prerequisites

- `sdlc_00_delivery_scaffold_v1` has been run
- Masterplan architecture and workflow spec documents exist

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| *(none)* | — | This workflow generates its inputs from masterplan documents |

## Outputs

| Artifact | Path |
|----------|------|
| `L1_FOUNDATION_INDEX` | `foundation/runs/{job_id}/README.md` |
| `L1_LAYER_MODEL` | `foundation/runs/{job_id}/LAYER_MODEL.md` |
| `L1_DOCUMENT_AUTHORITY` | `foundation/runs/{job_id}/DOCUMENT_AUTHORITY.md` |
| `L1_BUNDLE_TAXONOMY` | `foundation/runs/{job_id}/BUNDLE_TAXONOMY.md` |
| `L1_GOVERNANCE_LIFECYCLE` | `foundation/runs/{job_id}/GOVERNANCE_LIFECYCLE.md` |
| `L1_METADATA_STANDARD` | `foundation/runs/{job_id}/METADATA_STANDARD.md` |
| `REVIEW_FILE_SUGGESTED` | `foundation/runs/{job_id}/{job_id}-governance-foundation-review.md` |
| `GOVERNANCE_FOUNDATION_VALIDATION` | `foundation/runs/{job_id}/{job_id}-governance-foundation-validation.md` |
| `AUDIT_FILE_SUGGESTED` | `foundation/runs/{job_id}/{job_id}-governance-foundation-audit.md` |
| `GOVERNANCE_PUBLISH_MANIFEST` | `foundation/current/governance_set_manifest.json` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `collect_governance_context` | Action | — | Gather governance context inventory |
| 2 | `generate_governance_foundation_docs` | Prompt | architect | Generate 6 Layer 1 governance documents |
| 3 | `review_governance_foundation_docs` | Prompt | reviewer | Internal quality review (loop → step 4, max 2) |
| 4 | `refine_governance_foundation_docs` | Prompt | refine | Address findings in all 6 docs |
| 5 | `validate_governance_foundation_docs` | Action | — | Deterministic validation |
| 6 | `audit_governance_foundation_docs` | Prompt | validation | Semantic audit **[HUMAN GATE]** |
| 7 | `publish_governance_foundation_set` | Action | — | Deploy to `foundation/current/` |
| 8 | `stepCompletion` | Action | — | Terminal |

## Implementations

| Name | Label | Description |
|------|-------|-------------|
| `standard` | Standard | Default Layer 1 governance generation with review, validation, and audit |

## How to Run

```bash
ukbe-run-agent run --template-group 01_governance_foundation_v1
```
