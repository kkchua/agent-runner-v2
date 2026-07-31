# sdlc_00_delivery_scaffold_v1 — SDLC Scaffold Generator

## Purpose

Generates the foundational SDLC delivery scaffold — **13 master document templates** and **8 agent contract definitions**. These define the canonical structure for all delivery documents and agent roles used by the downstream SDLC workflow chain (`sdlc_10` through `sdlc_80`).

**This workflow must run before any SDLC delivery workflow.**

## Prerequisites

- Layer 1 governance bootstrapped (`00_bootstrap_lifecycle_admin_v1`)
- Layer 2 platform published (`02_agent_runner_platform_v1`)

## Inputs

None. Generates from L3 SDLC specification context.

## Outputs

| Artifact | Path |
|----------|------|
| 13 templates | `sdlc/current/01_templates/` |
| 8 agent contracts | `sdlc/current/02_agents/` |
| Publish manifest | `sdlc/current/sdlc_scaffold_manifest.json` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `generate_templates` | Prompt | architect | Generate 13 master document templates |
| 2 | `generate_agent_contracts` | Prompt | architect | Generate 8 agent contract files |
| 3 | `review_scaffold` | Prompt | reviewer | Review all 21 artifacts **[HUMAN GATE]** |
| 4 | `refine_scaffold` | Prompt | architect | Fix per review findings (loop → step 3, max 2) |
| 5 | `publish_sdlc_scaffold` | Action | — | Copy to `sdlc/current/` with history archival |
| 6 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_00_delivery_scaffold_v1
```

Or via operator console: select `sdlc_00_delivery_scaffold_v1` from the workflow dropdown.

## Downstream Impact

The published templates and agent contracts are used by all downstream SDLC workflows:

| Workflow | Template Used | Agent Used |
|----------|--------------|------------|
| sdlc_00_init_doc_v1 | INIT template | — |
| sdlc_10_requirement_v1 | REQ template | — |
| sdlc_20_planning_v1 | PLAN template | AGENT-planner |
| sdlc_30_backlog_v1 | BACKLOG template | AGENT-task-decomposer |
| sdlc_40_task_v1 | TASK template | AGENT-task-decomposer |
| sdlc_50_implementation_v1 | IMPL template | AGENT-implementation-planner |
| sdlc_60_execution_v1 | — | AGENT-executor |
| sdlc_70_validation_v1 | VALID template | AGENT-reviewer |
| sdlc_80_review_v1 | REV/MEM/CLOSE templates | AGENT-reviewer, AGENT-memory-manager |

## Special Files

- `install.py` — Copies published scaffold to `~/.ukbe-runner/` for global access
- `context_extensions.py` — Registers shared SDLC artifact keys (`INIT_FILE`, `REQ_FILE`, etc.)
