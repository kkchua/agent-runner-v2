# Workflow Specification: {Workflow Name}

> Fill in this template and save to `docs/repo/workflow_builder/specs/{slug}.md`.
> The workflow builder reads this document to generate the workflow package.

## Overview

**Workflow name:** `your_workflow_v1`
**Label:** Your Workflow Label
**Job prefix:** `YRWF`
**Description:** Brief description of what this workflow does.
**Init step:** `first_step_name`

## Purpose

What problem does this workflow solve? What triggers it? What is the
expected outcome?

## Workflow Type

Pick one, or leave blank for the builder to infer from step descriptions:

- [ ] **Prompt-driven** — LLM generates documents with review/refine loops
- [ ] **Action-only** — Python actions only, no LLM invocations
- [ ] **Mixed** — Combination of prompt-driven and action steps

The builder will infer the workflow type from your step descriptions if
not explicitly declared. For mixed workflows, specify which steps are
prompt-driven and which are action-driven.

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

**Granularity rule:** Declare one artifact key per logical file, not per
directory. The runner tracks individual files. If a step produces 6 files,
declare 6 keys (e.g., `WORKFLOW_MANIFEST`, `WORKFLOW_EXTENSIONS`,
`WORKFLOW_ACTIONS`, `WORKFLOW_PROMPTS_INDEX`, `WORKFLOW_README`,
`WORKFLOW_ENV_SAMPLE`). Never use a single directory key like
`WORKFLOW_BUNDLE` — the validator cannot check inside directories.

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

**Routing conventions:**

- `On success: → next_step_name` — advance to the named step
- `On success: → human approval gate (approve → next_step, reject → rerun)` —
  requires human approval before advancing
- `On success: → stepCompletion` — terminal step (workflow done)
- For review steps: `On rejection: → refine_step (max 2 iterations)`
- **Exhausted failure handling:** Every `on_reject_refine` must specify what
  happens when max iterations is reached:
  - `exhausted_failure_code` — a unique error code (e.g., `REQUIREMENTS_GATEKEEP_EXHAUSTED`)
  - `exhausted_failure_class` — typically `HUMAN_RETRY_REQUIRED`

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

If your workflow needs custom Python actions, describe them.

**Reuse check first:** Before defining a new action, check if an existing
action can be reused. Common reusable actions:
- `validate_workflow_bundle` — structural validation of generated packages
- `promote_workflow_package` — copy generated package to workflows/ directory
- `step_completion` — terminal step (always reuse this)

Only define new actions when existing ones don't fit your needs.

```
Action: validate_output
Purpose: Check that the generated output meets quality criteria.
Returns: APPROVED or REJECTED with reject_code
```

## Gatekeeper Requirements

For complex multi-step workflows, add quality control (QC) gatekeepers
between major phases. Each gatekeeper validates the output of the preceding
step before downstream steps consume it.

**Critical rule:** Each gatekeeper must produce a **distinct** artifact key.
Never reuse `REVIEW_FILE_SUGGESTED` for multiple gatekeepers — the runner
cannot distinguish which review rejected which step.

**Standard gatekeeper keys:**

| Gatekeeper | Artifact Key | Validates |
|---|---|---|
| After requirements | `GATEKEEP_REQUIREMENTS` | Parse completeness, archetype classification |
| After artifacts | `GATEKEEP_ARTIFACTS` | Every artifact has one producer, no dangling refs |
| After steps | `GATEKEEP_STEPS` | Step sequence covers all phases, routing correct |
| After package | `GATEKEEP_PACKAGE` | Generated files match design, no hallucinated keys |

Choose how many gatekeepers you need:
- [ ] **1 gatekeeper** — After requirements
- [ ] **2 gatekeepers** — After requirements + after steps design
- [ ] **4 gatekeepers** — Full pipeline (recommended for meta-workflows)

## Meta-Workflow Requirements

**Apply this section if your workflow generates other workflow packages**
(e.g., a builder like `workflow_builder_v1`). Meta-workflows have stricter
requirements because their output is structural, not documentary.

**Mandatory elements for meta-workflows:**

1. **TDD loop** — Must start with `generate_test_criteria` → `review_test_criteria`
   → `refine_test_criteria`. This establishes acceptance criteria before any
   design work begins. Without it, the validate_bundle step has no explicit
   criteria to check against.

2. **init_step declaration** — Must declare `init_step = "generate_test_criteria"`
   in the Overview section. The runner uses this to know where to start.

3. **4 gatekeepers with distinct keys** — Full pipeline validation is mandatory:
   requirements → artifacts → steps → package. Each gatekeeper produces a
   distinct artifact key (see table above).

4. **exhausted_failure_code/class on all refine loops** — Every `on_reject_refine`
   must include:
   ```
   exhausted_failure_code = "STEP_NAME_EXHAUSTED"
   exhausted_failure_class = "HUMAN_RETRY_REQUIRED"
   ```

5. **Action reuse audit** — Must reuse `validate_workflow_bundle` and
   `promote_workflow_package` from `workflow_builder_v1` unless there is a
   documented reason why the existing actions don't fit. Do not create
   `validate_creative_bundle` or `promote_creative_workflow` without
   explaining what the existing actions cannot do.

## Self-Validation (Optional)

Require each producer step (generate, define, design) to self-check its
output before reporting APPROVED. The LLM validates its own work against
criteria before submission.

- [ ] **Enable Self-Validation** — Producer steps include self-check section

Benefits: Catches errors early, reduces reviewer burden, improves output
quality through self-correction.

## Principles-Based Generation (Optional)

Choose how the generate_package step should determine what files to create:

- [ ] **Principles-based** — Infer required files from the design
  documents (REQUIREMENTS, ARTIFACTS, STEPS). The LLM determines what files
  are needed based on principles, not a fixed list.

- [ ] **Fixed task list** (safer) — Explicitly list the files to generate
  (workflow.toml, context_extensions.py, prompts, README.md, .env.sample,
  config.json.sample). Use for simple workflows with predictable structure.

**Risk warning:** Principles-based generation gives the LLM latitude to
decide what files are needed. This can lead to hallucinated files or
invented artifact keys. If you choose principles-based, add explicit
forbidden-content instructions to the generate_package prompt:
- "Report ONLY the declared artifact keys. Do NOT invent new keys."
- "Do NOT add configuration fields not requested in the spec."

For meta-workflows, prefer **fixed task list** unless you have a specific
reason why the file set is unpredictable.

## Notes

Any additional context, constraints, or references.
