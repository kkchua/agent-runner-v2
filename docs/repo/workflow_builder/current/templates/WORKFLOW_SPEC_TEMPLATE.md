# Workflow Specification: {Workflow Name}

> Fill in this template and save to `docs/repo/workflow_builder/specs/{slug}.md`.
> The workflow builder reads this document to generate the workflow package.

## Overview

**Workflow name:** `your_workflow_v1`
**Label:** Your Workflow Label
**Job prefix:** `YRWF`
**Description:** Brief description of what this workflow does.

## Purpose

What problem does this workflow solve? What triggers it? What is the
expected outcome?

## Workflow Type

Pick one:

- [ ] **Prompt-driven** — LLM generates documents with review/refine loops
- [ ] **Action-only** — Python actions only, no LLM invocations
- [ ] **Mixed** — Combination of prompt-driven and action steps

## Input Artifacts

What existing artifacts does this workflow consume?

| Artifact Key | Description | Required? |
|---|---|---|
| `INPUT_KEY_1` | Description of input 1 | Yes |
| `INPUT_KEY_2` | Description of input 2 | No (optional) |

## Output Artifacts

What artifacts does this workflow produce?

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `OUTPUT_KEY_1` | `OUTPUT-{date}-{seq}_{slug}.md` | Main output document |
| `REVIEW_FILE_SUGGESTED` | `{slug}-REV-xx-type.md` | Review document |

## Step Sequence

Describe the steps in order. For each step, specify:

1. **Step name:** `step_name`
2. **Type:** prompt or action
3. **Purpose:** What this step does
4. **Role policy:** (for prompt steps) architect_standard, reviewer_standard, etc.
5. **Routing:** What happens on success, rejection, exhaustion

### Example Step

```
Step: generate_output
Type: prompt
Role: architect_standard
Purpose: Generate the main output document from inputs.
On success: → review_output
On rejection: → (none, proceed to review)

Step: review_output
Type: prompt
Role: reviewer_standard
Purpose: Review the generated output for quality and completeness.
On success: → promote_output (requires human approval)
On rejection: → refine_output (max 2 iterations)

Step: refine_output
Type: prompt
Role: architect_standard
Purpose: Fix issues identified by review.
After refine: → back to review_output

Step: promote_output
Type: action (promote_artifact)
Purpose: Mark the output as Approved.
On success: → stepCompletion
```

## Context Variables

What additional context does the workflow need beyond artifact paths?

- `GOVERNANCE_RUNTIME_ROOT` — Layer 1 governance docs (standard)
- `PLATFORM_RUNTIME_ROOT` — Layer 2 platform docs (standard)
- Any custom variables?

## Special Requirements

- [ ] Needs slug extraction from input filenames
- [ ] Needs auto-incrementing sequence numbers
- [ ] Needs loop iteration suffixes for review/validation artifacts
- [ ] Needs custom actions (describe below)
- [ ] Needs global installation (copies files to ~/.ukbe-runner/)

## Custom Actions

If your workflow needs custom Python actions, describe them:

```
Action: validate_output
Purpose: Check that the generated output meets quality criteria.
Returns: APPROVED or REJECTED with reject_code
```

## Notes

Any additional context, constraints, or references.
