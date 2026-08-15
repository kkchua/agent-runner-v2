# 02_agent_runner_platform_v1 — Agent Runner Platform Constitution (BCS-compliant)

## Purpose

Generates, validates, audits, and publishes the Layer 2 platform core constitution for agent-runner-v2 — the runtime model, bundle authoring contract, shared services, metadata contract, and validation contract that all Layer 3 workflows build upon.

## Prerequisites

- `01_governance_foundation_v1` has been run (Layer 1 governance available)
- Masterplan architecture and platform spec documents exist

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| *(none)* | — | This workflow generates its inputs from masterplan documents and Layer 1 governance |

## Outputs

| Artifact | Path |
|----------|------|
| `L2_PLATFORM_INDEX` | `platform/agent_runner/runs/{job_id}/README.md` |
| `L2_RUNTIME_MODEL` | `platform/agent_runner/runs/{job_id}/RUNTIME_MODEL.md` |
| `L2_BUNDLE_AUTHORING_CONTRACT` | `platform/agent_runner/runs/{job_id}/BUNDLE_AUTHORING_CONTRACT.md` |
| `L2_SHARED_SERVICES` | `platform/agent_runner/runs/{job_id}/SHARED_SERVICES.md` |
| `L2_METADATA_CONTRACT` | `platform/agent_runner/runs/{job_id}/METADATA_CONTRACT.md` |
| `L2_VALIDATION_CONTRACT` | `platform/agent_runner/runs/{job_id}/VALIDATION_CONTRACT.md` |
| `REVIEW_FILE_SUGGESTED` | `platform/agent_runner/runs/{job_id}/{job_id}-platform-core-review.md` |
| `PLATFORM_CORE_VALIDATION` | `platform/agent_runner/runs/{job_id}/{job_id}-platform-core-validation.md` |
| `AUDIT_FILE_SUGGESTED` | `platform/agent_runner/runs/{job_id}/{job_id}-platform-core-audit.md` |
| `PLATFORM_PUBLISH_MANIFEST` | `platform/agent_runner/current/platform_set/manifest.json` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `collect_platform_context` | Action | — | Gather platform context inventory |
| 2 | `generate_platform_core_docs` | Prompt | architect | Generate 6 Layer 2 platform constitution documents |
| 3 | `review_platform_core_docs` | Prompt | reviewer | Internal quality review (loop → step 4, max 2) |
| 4 | `refine_platform_core_docs` | Prompt | refine | Address findings in platform docs |
| 5 | `validate_platform_core_docs` | Action | — | Deterministic validation |
| 6 | `audit_platform_core_docs` | Prompt | validation | Semantic audit **[HUMAN GATE]** |
| 7 | `publish_platform_core_set` | Action | — | Deploy to `platform/agent_runner/current/` |
| 8 | `stepCompletion` | Action | — | Terminal |

## Implementations

| Name | Label | Description |
|------|-------|-------------|
| `standard` | Standard | Default Layer 2 platform constitution generation with review, validation, and audit |

## How to Run

```bash
ukbe-run-agent run --template-group 02_agent_runner_platform_v1
```
