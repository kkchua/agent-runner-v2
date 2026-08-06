# Workflow Specification: {Workflow Name}

> Save to `docs/repo/workflow_builder/specs/{slug}.md`.
> The workflow builder reads this document and generates the complete
> workflow package (workflow.toml, context_extensions.py, prompts, actions.py).
>
> **Key principle:** Describe WHAT the workflow does (domain problem, inputs,
> outputs, constraints). The builder infers HOW to structure it (step sequence,
> routing, role policies, gatekeepers, self-validation).

## Overview

**Workflow name:** `your_workflow_v1`
**Label:** Your Workflow Label
**Job prefix:** `YRWF`
**Description:** Brief description of what this workflow does.
**Init step:** `first_step_name` (or leave blank for builder to determine)

## Purpose

What problem does this workflow solve? What triggers it? What is the
expected outcome?

## Workflow Type

Pick one, or leave blank for the builder to infer:

- [ ] **Prompt-driven** — LLM generates documents with review/refine loops
- [ ] **Action-only** — Python actions only, no LLM invocations
- [ ] **Mixed** — Combination of prompt-driven and action steps

## Input Artifacts

What existing artifacts does this workflow consume?

| Artifact Key | Description | Required? |
|---|---|---|
| `INPUT_KEY_1` | Description of input 1 | Yes |
| `INPUT_KEY_2` | Description of input 2 | No (optional) |

**If no user-provided inputs**, document hardcoded paths as context variables:

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `INPUT_DIR` | `{repo_root}/step_00` | Directory where user places input files |

## Output Artifacts

What artifacts does the workflow produce?

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `OUTPUT_KEY_1` | `OUTPUT-{date}-{seq}_{slug}.md` | Main output document |
| `REVIEW_FILE_SUGGESTED` | `{slug}-REV-xx-type.md` | Review document |

**Granularity rule:** One artifact key per logical file, not per directory.
The runner tracks individual files. Never use a directory key.

## Context Variables

What additional context does the workflow need beyond artifact paths?

- Standard variables (`GOVERNANCE_RUNTIME_ROOT`, `PLATFORM_RUNTIME_ROOT`)
  are provided automatically.
- List only custom variables your workflow needs.

## Quality Requirements

What makes the output "good"? Describe verifiable quality criteria:

- Completeness requirements (what must the output contain?)
- Accuracy requirements (what must be correct?)
- Format requirements (structure, naming, encoding?)
- Edge cases (what should the workflow do when inputs are unusual?)

## Custom Actions

If the workflow needs custom Python actions, describe them.

**Reuse check first:** Before defining a new action, check if an existing
action can be reused:
- `validate_workflow_bundle` — structural validation of generated packages
- `promote_workflow_package` — copy generated package to workflows/ directory
- `step_completion` — terminal step (always reuse this)

Only define new actions when existing ones don't fit. For each new action:

```
Action: action_name
Purpose: What the action does (be specific — files to scan, APIs to call,
  error handling, return conditions).
Returns: APPROVED or REJECTED with reject_code
```

## Builder Instructions (Optional)

High-level guidance for the builder. Only include if the domain has special
needs that aren't obvious from the sections above:

- Suggested workflow architecture (if you have a preference)
- Domain-specific constraints the builder should respect
- Similar existing workflows to model after
- API documentation references

## Notes

Any additional context, constraints, or references.
