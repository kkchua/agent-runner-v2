---
name: template-generation-gate
description: Procedure for the initial generate-templates step in delivery_scaffold_v1 — path resolution, project adaptation, and meta.json sidecar contract
source: auto-skill
extracted_at: '2026-06-03T16:48:00.000Z'
---

# Template Generation Gate Procedure

## When to use
This skill applies when executing the `generate_templates` step in `delivery_scaffold_v1` — the initial creation of all 7 document templates + template registry, adapted to the target project's domain.

## Governing rules
- Every template must have a metadata block with `Doc Type` and `Template Version`.
- Templates must be adapted to the project's domain but preserve their canonical structure.
- Do NOT include agent master prompt templates — they are deprecated.
- Template naming: `{NN}_{name}.template.md` in `docs/delivery/00_templates/`.
- **meta.json sidecar is the ONLY communication channel** — no stdout JSON parsing.

## Output paths (resolved from step_runner.py context)

All template files go to `docs/delivery/00_templates/`:

| Artifact Key | Filename |
|---|---|
| `DELIVERY_TEMPLATE_REGISTRY` | `template_registry.md` |
| `DELIVERY_INITIATIVE_TEMPLATE` | `01_initiative.template.md` |
| `DELIVERY_PLAN_TEMPLATE` | `02_plan.template.md` |
| `DELIVERY_TASK_GRAPH_TEMPLATE` | `02b_task_graph.template.md` |
| `DELIVERY_TASK_TEMPLATE` | `03_task.template.md` |
| `DELIVERY_IMPL_TEMPLATE` | `04_implementation_plan.template.md` |
| `DELIVERY_REVIEW_TEMPLATE` | `04_review.template.md` |
| `DELIVERY_MEMORY_TEMPLATE` | `06_memory.template.md` |

The sidecar path is always `{tmpl_dir}/template_registry.meta.json`.

## Required inputs
1. **Project analysis** — `project_analysis.json` from the project_analysis step
2. **SOP** — `WORKFLOW_SOP_v1.md` (if available)
3. **Status rules** — `DELIVERY_STATUS_RULES_v1.md` (if available)

## Required template sections

Each template has a mandatory set of sections. Do not omit any:

### 01_initiative.template.md
Metadata (Doc Type, Template Version, Initiative ID, Title, Status, Owner, Workflow Governance In Scope, Created At, Approved At), Objective, Problem Statement, Expected Outcomes (Business, Technical, User), Scope (Included, Excluded), Constraints, Dependencies, Success Criteria, References, Notes, Approval.

### 02_plan.template.md
Metadata (Doc Type, Template Version, Plan ID, Initiative ID, Title, Status, Created By, Created At, Reviewed By, Reviewed At, Approved By, Approved At, Finalized At), Plan Objective, Strategy Overview (reference workflow gates, do not redefine approval authority), System Design (Components, Data Flow, Integrations, Key Design Decisions), Task Breakdown (table), Scope Mapping, Explicitly Excluded / Not Planned, Deliverables, Risks & Mitigations, Execution Flow, Acceptance Criteria, References, Notes, Approval.

### 02b_task_graph.template.md
Metadata (Doc Type: 02_plan_artifact, Template Version, Task Graph ID, Plan ID, Initiative ID, Title, Status, Reviewed By, Reviewed At, Approved By, Approved At), Task Graph Objective, Task Graph (one section per task with Description, Owner, Priority, Depends On, Scope, Deliverables, Testability, Review Criteria), Execution Flow (parallelism + validation), Task Success Criteria, References, Notes.

### 03_task.template.md
Metadata (Doc Type, Template Version, Task ID, Plan ID, Title, Status, Priority, Assigned To, Created At, Due At), Objective, Inputs (Source plan, Dependencies, Required documents, Required data/APIs), Outputs (Expected artifacts, Output folder/path, Completion evidence), Implementation Details (Technical Notes, API/Contract Notes, Data/Schema Notes), Execution Steps, Validation Criteria (Acceptance checks, Test cases, Review requirements), Risks / Blockers, References, Notes.

### 04_implementation_plan.template.md
Metadata (Doc Type, Template Version, Plan ID, Task ID, Title, Status, Created At, Author), Objective (HOW, not WHAT), Inputs (table), Outputs (table), Scope Clarification (Included, Excluded), File Plan (MANDATORY — tree with [NEW]/[MODIFY] tags), Module Responsibilities, Reuse Strategy, Data Flow, Test Plan (Test Files, Test Cases, Test Constraints), Constraints, Risks & Mitigations, Dependencies, Notes, Ready for Execution checklist.

### 04_review.template.md
Metadata (Doc Type, Template Version, Review ID, Related Doc Type, Related Doc ID, Title, Reviewer, Status, Review Date), Review Objective, Summary of Reviewed Content, Strengths, Issues Identified (table with Severity), Suggested Improvements, Validation Against Acceptance Criteria (table), Final Decision (Decision, Rationale, Required next action), References, Notes, Naming contract note.

### 06_memory.template.md
Metadata (Doc Type, Template Version, Memory ID, Title, Version, Status, Last Updated, Owner), Purpose, Key Decisions, Architecture Notes, Important References (Initiative IDs, Plan IDs, Task IDs, Review IDs, External references), Known Issues, Learnings, Change Log (table), Notes.

### template_registry.md
Table: Layer | Doc Type | Folder (exact values below), Flow section: Initiative → Plan → Task → Implementation Plan → Code → Review → Memory.

Exact registry table:

| Layer | Doc Type | Folder |
|---|---|---|
| Initiative | 01_initiative | 01_initiatives |
| Plan | 02_plan | 02_plans |
| Task Graph | 02b_task_graph | 02_plans/artifacts |
| Task | 03_task | 03_tasks |
| Implementation Plan | 04_implementation_plan | 04_implementation_plans |
| Review | 04_review | 05_reviews |
| Memory | 06_memory | 06_memory |

## Execution sequence

### Step 1: Read project analysis
- Read `project_analysis.json` from disk to understand the target project's domain, tech stack, complexity, and recommended scope.

### Step 2: Read existing template files (if they exist)
- **CRITICAL**: Template files may already exist from a previous scaffold run. You MUST read each file before overwriting.
- Use `read_file` for every template file before writing new content.
- If a file does not exist, proceed to write it.

### Step 3: Write all 7 template files
- Adapt placeholder examples to the project's domain (e.g., reference Python 3.11+, meta.json sidecar contract, runner architecture for agent-runner-v2).
- Preserve ALL required sections — do not omit any.
- Keep placeholder variables (`{{YYYYMMDD}}`, `{{NN}}`, `{{TITLE}}`, `{{SLUG}}`, etc.) for runtime substitution.

### Step 4: Write template_registry.md
- Include the exact Layer/Doc Type/Folder table above.
- Include the Flow diagram.
- Do NOT include validation or agent master prompt entries unless the SOP explicitly requires them.

### Step 5: Verify all 8 files exist on disk
- Confirm each file exists at its path before writing the sidecar.

### Step 6: Write meta.json sidecar
- **CRITICAL**: Read the existing meta.json sidecar with `read_file` BEFORE overwriting it. The tool will reject a write if the file hasn't been read in the current session.
- Path: `{tmpl_dir}/template_registry.meta.json`
- Structure:
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "Brief summary",
    "artifacts": {
      "DELIVERY_TEMPLATE_REGISTRY": "<absolute path>",
      "DELIVERY_INITIATIVE_TEMPLATE": "<absolute path>",
      "DELIVERY_PLAN_TEMPLATE": "<absolute path>",
      "DELIVERY_TASK_GRAPH_TEMPLATE": "<absolute path>",
      "DELIVERY_TASK_TEMPLATE": "<absolute path>",
      "DELIVERY_IMPL_TEMPLATE": "<absolute path>",
      "DELIVERY_REVIEW_TEMPLATE": "<absolute path>",
      "DELIVERY_MEMORY_TEMPLATE": "<absolute path>"
    },
    "recorded_at": "ISO-8601 timestamp"
  }
}
```
- Use absolute paths in the artifacts map.

### Step 7: Return final JSON
- Return only valid JSON matching the required schema.
- No markdown, no explanation, no text before or after.

## Adaptation rules
- Use the project's domain to make template examples more relevant (e.g., for a Python CLI tool, reference `pyproject.toml`, `pytest`, dataclasses).
- Preserve canonical structure — only adapt example content, placeholders, and domain references.
- Do NOT add sections that are not in the required list above.
- Keep the `Template Version` as `v1` for first-generation templates.

## Anti-patterns to avoid
- Writing template files without reading existing ones first (causes data loss if files exist)
- Using relative paths in the meta.json sidecar artifacts map
- Writing the meta.json sidecar before all 8 files exist on disk
- Adding agent master prompt templates (07_master_prompts/)
- Omitting required sections from any template
- Changing Doc Type values away from the canonical names listed above
