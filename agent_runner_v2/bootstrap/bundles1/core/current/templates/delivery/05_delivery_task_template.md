---
template_id: "DELIVERY-TASK-v1"
title: "Delivery Task Template"
status: "active"
generated: "2026-07-09T10:35:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "07_generate_templates"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Metadata

- **Template ID**: DELIVERY-TASK-v1
- **Artifact Key**: `DELIVERY_TASK_TEMPLATE`
- **Version**: 1.0
- **Owner**: Task Execution Workflow
- **Purpose**: Specifies task objective, description, inputs, outputs, acceptance criteria, execution steps, validation criteria, documentation impact, dependencies, and notes for deterministic task execution

# Objective

**Task ID**: [Unique task identifier, e.g., T-001]

**Task Name**: [Descriptive name]

**Summary**: [2-3 sentence overview of what this task accomplishes]

**Parent Plan**: [Link to DELIVERY_PLAN_TEMPLATE or DELIVERY_TASK_GRAPH_TEMPLATE that originated this task]

**Current Profile**: [Describe current architecture standard in use, if applicable]

**Target Profile**: [Describe target architecture standard being adopted, if applicable]

**Migration Mode**: [If transitioning between profiles, describe migration approach, if applicable]

# Task Description

## Context

[Provide background information needed to understand why this task exists]

## Scope

### In Scope

- [List specific work items included in this task]
- [Be explicit about boundaries]

### Out of Scope

- [List work items explicitly excluded]
- [Clarify what will NOT be addressed]

## Expected Outcome

[Describe the concrete deliverable or state change this task produces]

# Inputs

## Required Artifacts

[List artifacts that must exist before this task can begin]

| Artifact | Artifact Key | Source | Purpose |
|----------|--------------|--------|---------|
| [Artifact name] | [ARTIFACT_KEY] | [Workflow/step that creates it] | [Why this task needs it] |

## Required State

[List system or repository state prerequisites]

- [Example: "Repository is clean with no uncommitted changes"]
- [Example: "Config.json has valid workflow paths"]

# Outputs

## Produced Artifacts

[List artifacts this task will create or modify]

| Artifact | Artifact Key | Type | Description |
|----------|--------------|------|-------------|
| [Artifact name] | [ARTIFACT_KEY] | new/modified | [What this artifact contains] |

## State Changes

[List state changes this task will produce]

- [Example: "Module count increases by 1"]
- [Example: "Codebase inventory updated with new entry"]

# Acceptance Criteria

## Functional Criteria

[List measurable functional outcomes]

- [ ] [Criterion 1: e.g., "Function executes without errors"]
- [ ] [Criterion 2: e.g., "Returns expected output for test inputs"]

## Documentation Criteria

[List measurable documentation outcomes]

- [ ] All modified modules have updated documentation
- [ ] Change impact document created if change is significant
- [ ] Codebase inventory reflects current state (if applicable)

## Quality Criteria

[List quality gates that must pass]

- [ ] Unit tests pass for affected code
- [ ] No hardcoded paths in modified code (validated via constants.py)
- [ ] Code follows project conventions (naming, structure, imports)

# Execution Steps

## Step 1: [Step Name]

[Detailed instructions for this step]

**Inputs**: [What this step consumes]

**Actions**: [What this step does]

**Outputs**: [What this step produces]

**Validation**: [How to verify this step succeeded]

## Step 2: [Step Name]

[Detailed instructions for this step]

**Inputs**: [What this step consumes]

**Actions**: [What this step does]

**Outputs**: [What this step produces]

**Validation**: [How to verify this step succeeded]

[Continue for all steps...]

# Validation Criteria

## Automated Validation

[List checks that can be automated]

- [ ] [Check 1: e.g., "pytest unit tests pass"]
- [ ] [Check 2: e.g., "No hardcoded paths detected"]

## Manual Validation

[List checks requiring human judgment]

- [ ] [Check 1: e.g., "Code review approves architectural approach"]
- [ ] [Check 2: e.g., "Documentation clarity verified by technical writer"]

## Validation Commands

[Provide exact commands to run validation]

```bash
# Example validation commands
pytest tests/unit/test_affected_module.py -v
python -m agent_runner_v2.tools.validate_constants --check-hardcoded-paths
```

# Documentation Impact

## Affected Documentation

[List all documentation artifacts this task affects]

| Documentation | Artifact Key | Action Required | Owner |
|---------------|--------------|-----------------|-------|
| [Doc name] | [ARTIFACT_KEY] | create/update/retire | [Role] |

## Documentation Update Plan

[Describe how documentation will be updated as part of this task]

1. [Step 1: e.g., "Update module doc for changed functions"]
2. [Step 2: e.g., "Regenerate codebase inventory"]
3. [Step 3: e.g., "Create change impact document"]

## Documentation Freshness Verification

[Define how documentation freshness will be verified after updates]

- [Verification method 1: e.g., "Compare doc examples against actual code"]
- [Verification method 2: e.g., "Validate all referenced files exist"]

## Stale Guidance Handling

[Identify any documentation that may become stale due to this task and define handling rules]

| Potentially Stale Doc | Artifact Key | Handling Rule | Trigger |
|-----------------------|--------------|---------------|---------|
| [Doc name] | [ARTIFACT_KEY] | update/mark_needs_update/supersede | [Condition] |

# Dependencies

## Task Dependencies

[List other tasks this task depends on]

| Dependent Task | Task ID | Dependency Type | Risk if Blocked |
|----------------|---------|-----------------|-----------------|
| [Task name] | T-XXX | blocks/enables | [Risk description] |

## Artifact Dependencies

[List artifacts this task depends on]

| Required Artifact | Artifact Key | Source Workflow | Fallback if Missing |
|-------------------|--------------|-----------------|---------------------|
| [Artifact name] | [ARTIFACT_KEY] | [Workflow name] | [Fallback action] |

## External Dependencies

[List external systems, credentials, or resources this task depends on]

- [Example: "Pushover API credentials in .env for notification testing"]
- [Example: "Backend API availability for worker mode testing"]

# Notes

- [Additional context, assumptions, or constraints]
- [Link to related tasks, discussions, or decision logs]
- [Record any deviations from standard task execution SOP]
- [Note any special considerations for Windows compatibility if applicable]
