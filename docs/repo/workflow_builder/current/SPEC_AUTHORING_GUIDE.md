# Workflow Spec Authoring Guide

> **Purpose:** How to write a workflow specification document that produces
> high-quality workflow packages via `workflow_builder_v1`.
>
> **Audience:** Human developers and AI agents (e.g., `/workflow_spec_builder` skill).
>
> **Companion documents:**
> - [WORKFLOW_SPEC_TEMPLATE.md](templates/WORKFLOW_SPEC_TEMPLATE.md) -- the blank template
> - [WORKFLOW_CREATION_GUIDE.md](../../../../workflows/WORKFLOW_CREATION_GUIDE.md) -- how the builder works
> - [WORKFLOW_BUILDER_SOP.md](../sop/WORKFLOW_BUILDER_SOP.md) -- storage and naming conventions

---

## Table of Contents

- [1: What is a Workflow Spec](#1-what-is-a-workflow-spec)
- [2: Before You Start](#2-before-you-start)
- [3: Section-by-Section Authoring](#3-section-by-section-authoring)
- [4: Workflow Pattern Reference](#4-workflow-pattern-reference)
- [5: Role Policy Quick Reference](#5-role-policy-quick-reference)
- [6: Worked Examples](#6-worked-examples)
- [7: Common Pitfalls](#7-common-pitfalls)
- [8: Spec Quality Checklist](#8-spec-quality-checklist)

---

## 1: What is a Workflow Spec

A workflow spec is a **single markdown document** that describes everything
about a workflow -- what it does, what it consumes, what it produces, and
how it gets there. It is the **sole input** to `workflow_builder_v1`, which
reads the spec and generates a complete workflow package:

```
spec.md  -->  workflow_builder_v1  -->  workflow package
                                        ├── workflow.toml
                                        ├── context_extensions.py
                                        ├── actions.py (if needed)
                                        ├── prompts/*.txt (if needed)
                                        ├── README.md
                                        ├── .env.sample (if needed)
                                        └── config.json.sample (if needed)
```

The spec is the **single source of truth**. If the spec does not mention
something, the builder will not generate it. If the spec is vague, the
builder will guess -- and may guess wrong.

**Key principle:** The spec describes WHAT the workflow does, not HOW the
builder should implement it. The builder infers implementation details
(step types, routing, file structure) from the spec's description of the
problem domain.

---

## 2: Before You Start

Answer these questions mentally (or jot them down) before writing the spec:

1. **What problem does this workflow solve?** What is the end-to-end
   transformation from input to output?

2. **What triggers the workflow?** Does a user drop files in a folder?
   Does another workflow produce the input? Is it manually triggered?

3. **What does the output look like?** A markdown document? Generated
   images? A published API endpoint? Be specific.

4. **Does it need human review?** Should someone approve intermediate
   results before the workflow continues?

5. **Are there external API calls?** Does the workflow call third-party
   services (image generation, data APIs, etc.)?

6. **Is there retry/rerun logic?** When something fails, should the
   workflow retry the same step, refine the output, or stop for human
   intervention?

7. **What existing workflows are similar?** Can you model this after an
   existing pattern? (See Section 4.)

---

## 3: Section-by-Section Authoring

### 3.1: Overview

```markdown
## Overview

**Workflow name:** `your_workflow_v1`
**Label:** Your Workflow Label
**Job prefix:** `YRWF`
**Description:** Brief description of what this workflow does.
```

**Rules:**

- **Workflow name:** `lowercase_with_underscores`, ending with `_v1` (or
  version number). This becomes the directory name, the `name` field in
  `workflow.toml`, and the `workflow_name` in `context_extensions.py`.
  All three must match exactly.

- **Label:** Human-readable display name. Use title case.

- **Job prefix:** Exactly 4 uppercase letters. Used for job ID generation
  (e.g., `WFBUILD-20260730-abc12345`). Choose something mnemonic:
  - `AMGEN` for Agnes Media Generation
  - `PRDM` for Product Master
  - `SDLC` for Software Development Lifecycle

- **Description:** One sentence. What does this workflow do?

### 3.2: Purpose

Describe:
- What problem this workflow solves
- What triggers it (user action, upstream workflow, schedule)
- What the expected outcome is

**Good example (from agnes_media_gen_v1):**
> Automates the full media creation pipeline from raw images to animated
> videos:
> 1. User drops images into step_00/ folder
> 2. LLM vision extracts detailed structured descriptions
> 3. LLM generates multiple prompt variants per description
> 4. Agnes Image API generates images from prompts
> 5. Agnes Video API generates videos (image-to-video)

**Bad example:**
> This workflow generates stuff from things.

### 3.3: Workflow Type

Declare one of:

| Type | When to use | Example |
|------|-------------|---------|
| **Prompt-driven** | LLM generates documents with review/refine loops | SDLC workflows, documentation generators |
| **Action-only** | Python actions only, no LLM invocations | Bootstrap admin, data processing |
| **Mixed** | Combination of prompt-driven and action steps | Media generation (LLM + API calls) |

If you leave this blank, the builder will infer from your step descriptions.
Being explicit is better.

For mixed workflows, specify which steps are prompt-driven and which are
action-driven in the Step Sequence section.

### 3.4: Input Artifacts

Declare what the workflow consumes:

```markdown
## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `WORKFLOW_SPEC` | The spec document to process | Yes |
| `EXISTING_OUTPUT` | Previous run output for incremental updates | No (optional) |
```

**Important distinction:**

- **Explicit inputs** -- artifacts provided by the user or upstream workflow.
  Declare these in the spec with `required_inputs`.

- **Hardcoded paths** -- directories or config files the workflow expects
  to exist in the runtime repo. Do NOT declare these as `required_inputs`.
  Instead, document them as context variables resolved in
  `context_extensions.py`:

```markdown
**No user-provided inputs.** All paths are hardcoded in context_extensions.py:

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `IMAGE_INPUT_DIR` | `{repo_root}/step_00` | Directory where user places input images |
```

### 3.5: Output Artifacts

Declare what the workflow produces:

```markdown
## Output Artifacts

| Artifact Key | Path Pattern | Description |
|---|---|---|
| `REQ_FILE` | `docs/repo/project/runs/{job_id}/REQ-{date}-{seq}_{slug}.md` | Requirements document |
| `REVIEW_FILE_SUGGESTED` | `docs/repo/project/runs/{job_id}/REV-{date}-{seq}_{slug}.md` | Review document |
```

**Naming conventions:**

- Artifact keys use **UPPER_SNAKE_CASE**.
- Document artifacts should use the `_FILE` suffix: `REQ_FILE`, `PLAN_FILE`,
  `REVIEW_FILE_SUGGESTED`.
- Index artifacts (for batch workflows) use `_INDEX` suffix: `IMAGE_INDEX`,
  `VIDEO_INDEX`.
- `REVIEW_FILE_SUGGESTED` is the standard key for review documents (used
  by the runner's review/refine routing).

**Path patterns:**

- Use `{job_id}`, `{date}`, `{seq}`, `{slug}` placeholders.
- `{date}` is `YYYYMMDD` format.
- `{seq}` is a 3-digit auto-incrementing sequence number (prevents overwrites).
- `{slug}` is extracted from the input artifact filename.
- All paths are relative to the project root.

### 3.6: Step Sequence

This is the most important section. For each step, describe:

1. **Step name** -- `lowercase_with_underscores`
2. **Type** -- `prompt` or `action`
3. **Purpose** -- What this step does (be specific!)
4. **Role policy** -- For prompt steps only (see Section 5)
5. **Routing** -- What happens on success, rejection

**Good step description (from agnes_media_gen_v1):**
```
Step: generate_images
Type: action (generate_images)
Purpose: Scan step_02/ for variant JSONs. For each JSON, iterate over variants
  and call Agnes Image 2.1 Flash API using t2i_prompt1. Download generated images
  to step_03/. Update the JSON with image_url for each variant. Save the updated
  JSON to step_03/ alongside images. Archive processed JSONs to step_02_archive/.
  Apply PROCESS_DELAY between API calls. Handle 503 errors with retry.
On success: -> human approval gate (approve -> generate_videos, reject -> rerun)
```

**Bad step description:**
```
Step: generate_images
Type: action
Purpose: Generate images.
```

The bad version tells the builder nothing about WHAT to implement. The
good version describes the complete behavior: scanning, API calls, file
management, error handling, archiving.

**Routing conventions:**

- `On success: -> next_step_name` -- advance to the named step
- `On success: -> human approval gate (approve -> next_step, reject -> rerun)` --
  requires human approval before advancing
- `On success: -> stepCompletion` -- terminal step (workflow done)
- For review steps: `On rejection: -> refine_step (max N iterations)`

### 3.7: Context Variables

List additional context the workflow needs beyond artifact paths:

```markdown
## Context Variables

- `GOVERNANCE_RUNTIME_ROOT` -- Layer 1 governance docs (standard)
- `PLATFORM_RUNTIME_ROOT` -- Layer 2 platform docs (standard)
- `IMAGE_INPUT_DIR` -- Absolute path to input image directory
- `MEDIA_CONFIG` -- Absolute path to media_config.json
```

Standard variables (`GOVERNANCE_RUNTIME_ROOT`, `PLATFORM_RUNTIME_ROOT`)
are provided automatically. Only list custom variables your workflow needs.

### 3.8: Special Requirements

Check all that apply and describe:

- **Slug extraction** -- Does the workflow extract a naming slug from input
  filenames? (e.g., `product_awesome-widget.md` -> slug `awesome-widget`)

- **Auto-incrementing sequences** -- Do output filenames need sequence
  numbers to prevent overwrites across multiple runs?

- **Custom actions** -- Does the workflow need Python action code? If so,
  describe each action in the Custom Actions section.

- **Config files** -- Does the workflow need a `config.json` for runtime
  settings? Describe the config structure.

- **Environment variables** -- Does the workflow need API keys or credentials
  from `.env`?

- **Archive pattern** -- Does each step archive processed inputs before
  producing outputs?

### 3.9: Custom Actions

For each custom action, describe:

```markdown
### Action: generate_images

**Purpose:** Scan step_02/ for variant JSONs. For each JSON, call Agnes Image
  2.1 Flash API for each variant using t2i_prompt1. Download images to step_03/.
  Update JSON with image_url. Save updated JSON to step_03/. Archive processed
  JSONs to step_02_archive/. Produce step_03/index.json listing all generated images.

**Returns:** APPROVED when all images generated, REJECTED with reject_code on failure.

**Configuration:** Reads from media_config.json: image size/ratio, process_delay,
  api_timeout, api_max_retries.

**Error handling:** 503 "server busy" errors trigger automatic retry with
  exponential backoff (up to api_max_retries). Other errors return REJECTED
  with partial progress saved.
```

**Critical:** The action description must include enough detail for the
builder to generate working Python code. Include:
- What files to scan and where
- What external APIs to call (endpoints, payload structure)
- What files to produce and where
- How to handle errors (retry, partial failure, etc.)
- What configuration values to read
- What to return (APPROVED/REJECTED conditions)

### 3.10: Gatekeeper Requirements (Optional)

For complex multi-step workflows, consider adding QC gatekeepers between
major phases. Each gatekeeper validates the output of the preceding step
before downstream steps consume it.

Specify how many gatekeepers you want:
- **1 gatekeeper** -- After requirements
- **2 gatekeepers** -- After requirements + after steps design
- **4 gatekeepers** -- Full pipeline: requirements -> artifacts -> steps -> package

### 3.11: Self-Validation (Optional)

When enabled, each producer step (generate, define, design) self-checks
its output before reporting APPROVED. This catches errors early and
reduces reviewer burden.

### 3.12: Notes

Any additional context, constraints, or references. Mention:
- Similar existing workflows to model after
- API documentation references
- Legacy systems being replaced
- Constraints the builder should respect

---

## 4: Workflow Pattern Reference

Choose the pattern that best fits your workflow. The builder will use this
to determine step structure, routing, and review gates.

### Pattern 1: Action-Only Pipeline

**Use when:** All steps are deterministic Python operations. No LLM needed.

```
validate -> publish -> init -> sync -> write_summary -> stepCompletion
```

**Characteristics:**
- No prompts/ directory
- No [step.coder] sections
- Fast execution, deterministic results
- Each step is a Python @action function

**Example:** `00_bootstrap_lifecycle_admin_v1`

### Pattern 2: Prompt-Driven with Review/Refine Loop

**Use when:** LLM generates documents that need quality review before approval.

```
generate -> technical_critique -> review -> [refine -> review] -> promote -> stepCompletion
```

**Characteristics:**
- 4 prompt files: generate, critique, review, refine
- 2 role policies: `architect_standard` (generate/refine), `reviewer_standard` (critique/review)
- Refinement loop: review rejects -> refine -> back to review
- `requires_human_approval_after = true` on review step
- Promote step at the end

**Example:** `sdlc_10_requirement_v1` through `sdlc_80_review_v1`

### Pattern 3: Mixed with Generate + Review + Refine + Audit

**Use when:** Extended Pattern 2 with an additional audit/validation step.

```
generate -> review -> refine -> validate -> audit -> promote -> stepCompletion
```

**Characteristics:**
- Has `bundle_governance.toml` with artifact registry
- Uses `validation_standard` role policy for audit steps
- Has governance adapters (AGENTS.md, QWEN.md, CLAUDE.md)

**Example:** `01_governance_foundation_v1`, `02_agent_runner_platform_v1`

### Pattern 4: Gatekeeper QC Pipeline

**Use when:** Complex multi-phase workflows where each phase output must be
validated before the next phase consumes it.

```
generate_test_criteria -> review_test_criteria -> analyze_spec -> gatekeep_requirements
  -> resolve_questions -> define_artifacts -> gatekeep_artifacts
  -> design_steps -> gatekeep_steps -> generate_package -> gatekeep_package
  -> validate_bundle -> review_package -> [refine_package] -> promote_package -> stepCompletion
```

**Characteristics:**
- Every producer step followed by a QC gatekeeper
- Gatekeepers use `validation_standard` role policy
- Gatekeepers have `on_reject_refine` routing back to the producer step
- Producer steps include Self-Validation sections
- Uses principles-based generation (infers files from design)

**Example:** `workflow_builder_v1`

### Pattern 5: Step-per-Operation with Human Gates

**Use when:** Each step produces tangible output that a human should review
before the next step runs. Common for API-calling workflows.

```
step_1 -> [human gate] -> step_2 -> [human gate] -> step_3 -> stepCompletion
```

**Characteristics:**
- Every step has `requires_human_approval_after = true`
- Reject at any gate reruns the same step (not a refine loop)
- Steps can be prompt-driven or action-driven
- Archive pattern: each step archives processed inputs

**Example:** `agnes_media_gen_v1`

---

## 5: Role Policy Quick Reference

Assign role policies to prompt-driven steps based on the step's purpose:

| Policy | Default Model | Use For |
|--------|---------------|---------|
| `architect_standard` | qwen3.7-plus | Generation steps (create documents, designs) |
| `reviewer_standard` | qwen3.7-plus | Review/critique steps (evaluate quality) |
| `refine_standard` | qwen3.7-plus | Refinement steps (fix issues from review) |
| `validation_standard` | qwen3.7-plus | Gatekeeper/audit steps (validate completeness) |
| `plan_standard` | qwen3.7-plus | Planning steps (create plans, strategies) |
| `documentation_standard` | kimi-k2.5 | Documentation generation steps |
| `backlog_standard` | kimi-k2.5 | Backlog management steps |
| `task_standard` | MiniMax-M2.5 | Task decomposition steps |
| `implement_standard` | qwen3-coder-next | Code implementation steps |
| `execution_standard` | qwen3-coder-next | Code execution steps |
| `code_fix_standard` | MiniMax-M2.5 | Bug fix steps |

**Typical assignments:**

| Step Type | Role Policy |
|-----------|-------------|
| Generate/create | `architect_standard` |
| Review/critique | `reviewer_standard` |
| Refine/fix | `refine_standard` |
| Gatekeep/validate | `validation_standard` |
| Analyze/plan | `plan_standard` or `architect_standard` |

---

## 6: Worked Examples

### Example A: Mixed Workflow (agnes_media_gen_v1)

This spec describes a media generation pipeline with both LLM steps and
API-calling action steps. Key aspects:

**Overview section:**
```markdown
**Workflow name:** `agnes_media_gen_v1`
**Job prefix:** `AMGEN`
```
Short, mnemonic name. 4-letter prefix.

**Input artifacts -- hardcoded, not required_inputs:**
```markdown
**No user-provided inputs.** All paths are hardcoded in context_extensions.py:
| `IMAGE_INPUT_DIR` | `{repo_root}/step_00` | Directory where user places input images |
```
The workflow defines its own folder structure. Inputs are not provided by
upstream artifacts but expected as files in specific directories.

**Step description -- action with full detail:**
```markdown
Step: generate_images
Type: action (generate_images)
Purpose: Scan step_02/ for variant JSONs. For each JSON, iterate over variants
  and call Agnes Image 2.1 Flash API using t2i_prompt1. Download generated images
  to step_03/. Update the JSON with image_url for each variant.
  Apply PROCESS_DELAY between API calls. Handle 503 errors with retry.
```
The description includes: what to scan, what API to call, what to produce,
how to handle errors. This is enough detail for the builder to generate
working Python code.

**Custom actions section -- API reference included:**
```markdown
### Action: generate_images
**Purpose:** [full description of batch processing, retry, archiving]
**API Reference:**
- Endpoint: `https://apihub.agnes-ai.com/v1/images/generations`
- Model: `agnes-image-2.1-flash`
- Payload: `{"model": "...", "prompt": "...", "size": "..."}`
```
Including the API endpoint and payload structure ensures the builder
generates correct API call code.

### Example B: Prompt-Driven with Flexible Architecture (product_master_gen_v2)

This spec describes a document generation workflow where the builder has
latitude to determine the optimal architecture. Key aspects:

**Delegating design decisions to the builder:**
```markdown
## Design Decisions for the Builder

The builder should determine the optimal architecture for this workflow:
- **Section generation strategy:** Generate all sections in one step or
  parallel independent steps?
- **Quality control:** How should validation be handled?
- **Review strategy:** What review points make sense?
```
For workflows where multiple architectures are valid, explicitly delegate
design decisions to the builder. This gives it permission to choose the
best approach rather than following a rigid template.

**Flexible output structure:**
```markdown
The workflow should analyze the input sources and determine if additional
sections would be valuable based on the product type.
```
The spec describes WHAT sections should exist but lets the builder decide
HOW to generate them. This is the right level of abstraction for a spec.

---

## 7: Common Pitfalls

### Pitfall 1: Vague Step Descriptions

**Bad:**
```
Step: process_data
Type: action
Purpose: Process the data and produce output.
```

**Good:**
```
Step: process_data
Type: action (process_data)
Purpose: Read input.csv from step_01/. For each row, validate fields,
  transform the name column to uppercase, calculate the total price
  including tax. Write results to step_02/output.csv. Archive processed
  input.csv to step_01_archive/. Return REJECTED if input.csv is missing
  or has no valid rows.
```

The builder cannot generate working code from vague descriptions. Include:
what to read, what to compute, what to write, how to handle errors.

### Pitfall 2: Wrong Artifact Key Naming

**Bad:** `requirements`, `reqDoc`, `req-doc`
**Good:** `REQ_FILE`, `REQUIREMENTS_FILE`, `REVIEW_FILE_SUGGESTED`

Artifact keys must be UPPER_SNAKE_CASE. Document artifacts should use the
`_FILE` suffix. The review artifact key should be `REVIEW_FILE_SUGGESTED`
(this is a runner convention).

### Pitfall 3: Declaring Hardcoded Paths as Required Inputs

**Bad:**
```markdown
## Input Artifacts
| `IMAGE_INPUT_DIR` | Directory for input images | Yes |
```

**Good:**
```markdown
## Input Artifacts
**No user-provided inputs.** All paths are hardcoded in context_extensions.py.

## Context Variables
- `IMAGE_INPUT_DIR` -- Absolute path to step_00/ (image input)
```

If the path is resolved from the repo root at runtime (not provided by an
upstream artifact), it belongs in Context Variables, not Input Artifacts.

### Pitfall 4: Missing Action Implementation Detail

**Bad:**
```markdown
### Action: send_notification
Purpose: Send a notification to the user.
```

**Good:**
```markdown
### Action: send_notification
Purpose: Read the notification config from config.json. Construct the
  message body from the workflow status and artifact paths. Send via
  Pushover API (endpoint: https://api.pushover.net/1/messages.json,
  POST with token, user, message fields). Read PUSHOVER_TOKEN and
  PUSHOVER_USER from .env. Return APPROVED if HTTP 200, REJECTED otherwise.
```

### Pitfall 5: Assuming Repo Structure

**Bad:**
```
Output goes to docs/repo/my-project/output.md
```

**Good:**
```
Output goes to {WORKFLOW_OUTPUT_DIR}/output.md, where WORKFLOW_OUTPUT_DIR
is resolved from the project root in context_extensions.py.
```

The workflow should not assume a specific repo layout. Define its own
folder structure and resolve paths relative to the project root.

### Pitfall 6: Forgetting the Terminal Step

Every workflow must end with `stepCompletion`. If your spec does not
mention it, the builder may forget to include it, and the workflow will
never reach COMPLETED status.

### Pitfall 7: Missing Error Handling Description

For action steps, always describe:
- What happens on failure (retry? partial save? abort?)
- What happens on timeout (how long is too long?)
- What happens on partial success (some items succeed, some fail?)

### Pitfall 8: Over-Specifying Implementation

**Too much:**
```
Step: generate_doc
Type: prompt
Role: architect_standard
Purpose: Use the LLM to read the input file, parse the YAML frontmatter,
  extract the title field, then generate a markdown document with H1 heading
  matching the title, followed by sections for each key in the frontmatter...
```

The spec should describe WHAT the step achieves, not HOW the LLM should
write the document. Leave implementation details to the builder.

**Right level:**
```
Step: generate_doc
Type: prompt
Role: architect_standard
Purpose: Generate a structured markdown document from the input spec.
  Include YAML frontmatter, table of contents, and sections for each
  major topic. Write to {OUTPUT_FILE}.
```

---

## 8: Spec Quality Checklist

Before submitting the spec to `workflow_builder_v1`, verify:

### Completeness

- [ ] Overview section has name, label, job prefix (4 chars), description
- [ ] Purpose section describes trigger and expected outcome
- [ ] Workflow type is declared (or step types are clear enough to infer)
- [ ] Every step has: name, type, purpose, routing
- [ ] Action steps include enough detail to generate working code
- [ ] Terminal step (stepCompletion) is mentioned or implied

### Naming

- [ ] Workflow name is `lowercase_with_underscores` ending with `_v1`
- [ ] Job prefix is exactly 4 uppercase letters
- [ ] Artifact keys are UPPER_SNAKE_CASE
- [ ] Document artifacts use `_FILE` suffix
- [ ] Review artifact uses `REVIEW_FILE_SUGGESTED` key

### Routing

- [ ] Every step has clear onsuccess routing
- [ ] Review steps have on_reject_refine routing
- [ ] Refine steps route back to review via onsuccess
- [ ] Last real step routes to stepCompletion
- [ ] Max iterations specified for refine loops

### Actions (if applicable)

- [ ] Each action has purpose, inputs, outputs, error handling
- [ ] API endpoints and payload structures included
- [ ] Config file structure described (if needed)
- [ ] Environment variables listed (if needed)
- [ ] Return conditions (APPROVED/REJECTED) specified

### Paths

- [ ] Input artifacts distinguished from hardcoded paths
- [ ] Output paths use `{job_id}`, `{date}`, `{seq}`, `{slug}` placeholders
- [ ] No hardcoded absolute paths in the spec
- [ ] Archive pattern described (if used)

### Quality

- [ ] Step descriptions are specific enough for code generation
- [ ] No vague phrases like "process the data" or "handle the output"
- [ ] Error handling described for all action steps
- [ ] Similar existing workflows referenced (if any)
