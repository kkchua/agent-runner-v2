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
- [4: Worked Examples](#4-worked-examples)
- [5: Meta-Builder Specs](#5-meta-builder-specs)
- [6: Common Pitfalls](#6-common-pitfalls)
- [7: Spec Quality Checklist](#7-spec-quality-checklist)

---

## 1: What is a Workflow Spec

A workflow spec is a **single markdown document** that describes what a
workflow does -- its domain problem, inputs, outputs, and constraints. It
is the **sole input** to `workflow_builder_v1`, which reads the spec and
generates a complete workflow package:

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

The spec is the **single source of truth** for domain requirements. If the
spec does not mention something, the builder will not generate it. If the
spec is vague, the builder will guess -- and may guess wrong.

**Key principle:** The spec describes WHAT the workflow does, not HOW the
builder should implement it. The builder automatically infers:

- Step sequence and routing
- Role policies for each step
- Gatekeeper placement (4 gatekeepers for meta-workflows)
- TDD loop for meta-workflows
- exhausted_failure_code/class on all refine loops
- init_step detection
- Action reuse audit
- Self-critic and self-validation in all prompts

For a complete list of what the builder enforces, see
[BUILDER_REQUIREMENTS.md](BUILDER_REQUIREMENTS.md).

---

## 2: Before You Start

Answer these questions mentally before writing the spec:

1. **What problem does this workflow solve?** What is the end-to-end
   transformation from input to output?

2. **What triggers the workflow?** Does a user drop files in a folder?
   Does another workflow produce the input? Is it manually triggered?

3. **What does the output look like?** A markdown document? Generated
   images? A published workflow package? Be specific.

4. **Are there external API calls?** Does the workflow call third-party
   services (image generation, data APIs, etc.)?

5. **What quality requirements must the output meet?** Completeness,
   accuracy, format, edge cases?

6. **What existing workflows are similar?** Can you model this after an
   existing pattern?

---

## 3: Section-by-Section Authoring

### 3.1: Overview

```markdown
## Overview

**Workflow name:** `your_workflow_v1`
**Label:** Your Workflow Label
**Job prefix:** `YRWF`
**Description:** Brief description of what this workflow does.
**Init step:** `first_step_name`
```

**Rules:**

- **Workflow name:** `lowercase_with_underscores`, ending with `_v1` (or
  version number). This becomes the directory name, the `name` field in
  `workflow.toml`, and the `workflow_name` in `context_extensions.py`.
  All three must match exactly.

- **Label:** Human-readable display name. Use title case.

- **Job prefix:** Exactly 4 uppercase letters. Used for job ID generation
  (e.g., `WFBUILD-20260730-abc12345`). Choose something mnemonic.

- **Description:** One sentence. What does this workflow do?

- **Init step:** Name of the first step. Leave blank for the builder to
  determine (it picks the first step, or `generate_test_criteria` for
  meta-workflows).

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

If you leave this blank, the builder will infer from the domain description.

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
  Declare these in the spec.

- **Hardcoded paths** -- directories or config files the workflow expects
  to exist in the runtime repo. Do NOT declare these as inputs. Instead,
  document them as context variables:

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

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `REQ_FILE` | `docs/repo/project/runs/{job_id}/REQ-{date}-{seq}_{slug}.md` | Requirements document |
| `REVIEW_FILE_SUGGESTED` | `docs/repo/project/runs/{job_id}/REV-{date}-{seq}_{slug}.md` | Review document |
```

**Naming conventions:**

- Artifact keys use **UPPER_SNAKE_CASE**.
- Document artifacts should use the `_FILE` suffix: `REQ_FILE`, `PLAN_FILE`.
- Index artifacts (for batch workflows) use `_INDEX` suffix: `IMAGE_INDEX`.
- `REVIEW_FILE_SUGGESTED` is the standard key for review documents.

**Path patterns:**

- Use `{job_id}`, `{date}`, `{seq}`, `{slug}` placeholders.
- All paths are relative to the project root.
- One key per logical file -- never use directory keys.

### 3.6: Context Variables

List additional context the workflow needs beyond artifact paths:

```markdown
## Context Variables

- `IMAGE_INPUT_DIR` -- Absolute path to input image directory
- `MEDIA_CONFIG` -- Absolute path to media_config.json
```

Standard variables (`GOVERNANCE_RUNTIME_ROOT`, `PLATFORM_RUNTIME_ROOT`)
are provided automatically. Only list custom variables.

### 3.7: Quality Requirements

Describe what makes the output "good". These are verifiable criteria the
builder uses to design review and validation steps:

- **Completeness:** What must the output contain?
- **Accuracy:** What must be correct?
- **Format:** Structure, naming, encoding requirements?
- **Edge cases:** What should happen with unusual inputs?

### 3.8: Custom Actions

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
builder to generate working Python code:
- What files to scan and where
- What external APIs to call (endpoints, payload structure)
- What files to produce and where
- How to handle errors (retry, partial failure, etc.)
- What configuration values to read
- What to return (APPROVED/REJECTED conditions)

**Reuse check:** Before defining a new action, check if existing actions
cover the need (`validate_workflow_bundle`, `promote_workflow_package`,
`step_completion`). Only create new actions when existing ones don't fit.

### 3.9: Builder Instructions (Optional)

High-level guidance for the builder. Only include if the domain has special
needs not obvious from the sections above:

- Suggested architecture (if you have a strong preference)
- Domain-specific constraints
- Similar existing workflows to model after
- API documentation references

### 3.10: Notes

Any additional context, constraints, or references.

---

## 4: Worked Examples

### Example A: Mixed Workflow (agnes_media_gen_v1)

This spec describes a media generation pipeline with both LLM steps and
API-calling action steps. Key aspects:

**Input artifacts -- hardcoded, not required_inputs:**
```markdown
**No user-provided inputs.** All paths are hardcoded in context_extensions.py:
| `IMAGE_INPUT_DIR` | `{repo_root}/step_00` | Directory where user places input images |
```

**Custom action -- full detail:**
```markdown
### Action: generate_images
**Purpose:** Scan step_02/ for variant JSONs. For each JSON, iterate over variants
  and call Agnes Image 2.1 Flash API using t2i_prompt1. Download generated images
  to step_03/. Update the JSON with image_url for each variant.
  Apply PROCESS_DELAY between API calls. Handle 503 errors with retry.
**API Reference:**
- Endpoint: `https://apihub.agnes-ai.com/v1/images/generations`
- Model: `agnes-image-2.1-flash`
- Payload: `{"model": "...", "prompt": "...", "size": "..."}`
```

### Example B: Constraints-First (product_master_gen_v2)

This spec describes a document generation workflow where the builder
proposes the step architecture. Key aspects:

**Delegating design decisions to the builder:**
```markdown
## Builder Instructions

The builder should determine the optimal architecture for this workflow:
- **Section generation strategy:** Generate all sections in one step or
  parallel independent steps?
- **Quality control:** How should validation be handled?
- **Review strategy:** What review points make sense?
```

**Flexible output structure:**
```markdown
The workflow should analyze the input sources and determine if additional
sections would be valuable based on the product type.
```

The spec describes WHAT sections should exist but lets the builder decide
HOW to generate them.

---

## 5: Meta-Builder Specs

A **meta-builder** is a workflow whose output is another workflow builder
(not a domain document or media file). Examples: `creative_workflow_builder_v1`
generates builders for creative media workflows from agent-md files.

Meta-builders follow the same spec authoring pattern as normal workflows,
but produce **additional spec documents** alongside the workflow bundle.

### 5.1: Meta-Builder Output Artifacts

In addition to the standard workflow bundle (`workflow.toml`,
`context_extensions.py`, `actions.py`, `prompts/`, `README.md`), a
meta-builder produces three spec documents:

| Artifact | Purpose | Promote Target |
|---|---|---|
| **Spec template** | Blank input template that the generated builder accepts | `docs/repo/workflow_builder/current/templates/` |
| **SOP** | Operating procedure for running the generated builder | `docs/repo/workflow_builder/current/sop/` |
| **Standard** | Builder-specific quality requirements and constraints | `docs/repo/workflow_builder/current/` |

These three documents are generated in the same `generate_package` step
as the workflow bundle. The `promote_builder_docs` action copies them
to the correct subdirectories under `docs/repo/workflow_builder/current/`.

### 5.2: Filename Format

All spec documents use versioned filenames with UPPER_SNAKE_CASE:

```
{SLUG}_SPEC_TEMPLATE_v{N}.md    -- e.g., CREATIVE_WORKFLOW_SPEC_TEMPLATE_v1.md
{SLUG}_SOP_v{N}.md              -- e.g., CREATIVE_WORKFLOW_SOP_v1.md
{SLUG}_STANDARD_v{N}.md         -- e.g., CREATIVE_WORKFLOW_STANDARD_v1.md
```

The `{SLUG}` matches the workflow name (uppercase). The `{N}` is the
version number, starting at 1. Increment when the spec template or
standard changes in a breaking way.

### 5.3: Input Spec Template Reference

The workflow.toml should declare which spec template the builder expects
as input. This allows the gatekeeper to validate that inputs conform to
the expected format:

```toml
[workflow]
name = "creative_workflow_builder_v1"
input_spec_template = "CREATIVE_WORKFLOW_SPEC_TEMPLATE_v1"
```

The `input_spec_template` value is an artifact key that resolves to the
spec template file path via `context_extensions.py`.

### 5.4: Promote Targets

Meta-builder output goes to **two destinations**:

| Output | Destination | Action |
|---|---|---|
| Workflow bundle (`workflow.toml`, `context_extensions.py`, etc.) | `workflows/{slug}/` | `promote_workflow_package` |
| Spec documents (template, SOP, standard) | `docs/repo/workflow_builder/current/` | `promote_builder_docs` |

The `promote_builder_docs` action copies:
- `{SLUG}_SPEC_TEMPLATE_v{N}.md` → `current/templates/`
- `{SLUG}_SOP_v{N}.md` → `current/sop/`
- `{SLUG}_STANDARD_v{N}.md` → `current/`

### 5.5: Spec Authoring for Meta-Builders

When writing a meta-builder spec, include these additional sections:

1. **Spec template requirements** -- Describe what the generated builder's
   input spec template should contain (sections, fields, constraints).

2. **SOP requirements** -- Describe what the SOP should cover (setup,
   execution, troubleshooting, expected outcomes).

3. **Standard requirements** -- Describe the quality bar for the generated
   builder (validation rules, naming conventions, gatekeeper criteria).

4. **Promote targets** -- Declare that spec documents go to
   `docs/repo/workflow_builder/current/`, not `workflows/`.

---

## 6: Common Pitfalls

### Pitfall 1: Vague Action Descriptions

**Bad:**
```
### Action: process_data
Purpose: Process the data and produce output.
```

**Good:**
```
### Action: process_data
Purpose: Read input.csv from step_01/. For each row, validate fields,
  transform the name column to uppercase, calculate the total price
  including tax. Write results to step_02/output.csv. Archive processed
  input.csv to step_01_archive/. Return REJECTED if input.csv is missing
  or has no valid rows.
```

### Pitfall 2: Wrong Artifact Key Naming

**Bad:** `requirements`, `reqDoc`, `req-doc`
**Good:** `REQ_FILE`, `REQUIREMENTS_FILE`, `REVIEW_FILE_SUGGESTED`

Artifact keys must be UPPER_SNAKE_CASE. Document artifacts should use the
`_FILE` suffix.

### Pitfall 3: Declaring Hardcoded Paths as Required Inputs

**Bad:**
```markdown
## Input Artifacts
| `IMAGE_INPUT_DIR` | Directory for input images | Yes |
```

**Good:**
```markdown
## Context Variables
- `IMAGE_INPUT_DIR` -- Absolute path to step_00/ (image input)
```

If the path is resolved from the repo root at runtime (not provided by an
upstream artifact), it belongs in Context Variables, not Input Artifacts.

### Pitfall 4: Missing Action Implementation Detail

**Bad:**
```
### Action: send_notification
Purpose: Send a notification to the user.
```

**Good:**
```
### Action: send_notification
Purpose: Read the notification config from config.json. Construct the
  message body from the workflow status and artifact paths. Send via
  Pushover API (endpoint: https://api.pushover.net/1/messages.json,
  POST with token, user, message fields). Read PUSHOVER_TOKEN and
  PUSHOVER_USER from .env. Return APPROVED if HTTP 200, REJECTED otherwise.
```

### Pitfall 5: Over-Specifying Implementation

**Too much:**
```
Step: generate_doc
Type: prompt
Role: architect_standard
Purpose: Use the LLM to read the input file, parse the YAML frontmatter,
  extract the title field, then generate a markdown document with H1 heading
  matching the title, followed by sections for each key in the frontmatter...
```

**Right level:**
```
## Quality Requirements
- Output must be a structured markdown document with YAML frontmatter
- Must include table of contents and sections for each major topic
- Title must match the input document title
```

Describe WHAT the output should look like, not HOW the LLM should write it.

### Pitfall 6: Reinventing Existing Actions

**Bad:**
```
### Action: validate_creative_bundle
Purpose: Structural validation of the generated workflow package.
```

**Good:**
```
Reuse `validate_workflow_bundle` and `promote_workflow_package` from
workflow_builder_v1. No new custom actions needed.
```

### Pitfall 7: Missing Error Handling Description

For action steps, always describe:
- What happens on failure (retry? partial save? abort?)
- What happens on timeout (how long is too long?)
- What happens on partial success (some items succeed, some fail?)

---

## 7: Spec Quality Checklist

Before submitting the spec to `workflow_builder_v1`, verify:

### Domain Completeness

- [ ] Overview has name, label, job prefix (4 chars), description
- [ ] Purpose describes trigger and expected outcome
- [ ] Workflow type declared (or domain clear enough for builder to infer)
- [ ] Input artifacts identified (or context variables for hardcoded paths)
- [ ] Output artifacts declared with filename patterns
- [ ] Quality requirements describe what "good" output looks like
- [ ] Action steps include enough detail to generate working code

### Naming

- [ ] Workflow name is `lowercase_with_underscores` ending with `_v1`
- [ ] Job prefix is exactly 4 uppercase letters
- [ ] Artifact keys are UPPER_SNAKE_CASE
- [ ] Document artifacts use `_FILE` suffix
- [ ] Review artifact uses `REVIEW_FILE_SUGGESTED` key

### Actions (if applicable)

- [ ] Each action has purpose, inputs, outputs, error handling
- [ ] API endpoints and payload structures included
- [ ] Config file structure described (if needed)
- [ ] Environment variables listed (if needed)
- [ ] Return conditions (APPROVED/REJECTED) specified
- [ ] Existing actions checked for reuse before defining new ones

### Paths

- [ ] Input artifacts distinguished from hardcoded paths (context variables)
- [ ] Output paths use `{job_id}`, `{date}`, `{seq}`, `{slug}` placeholders
- [ ] No hardcoded absolute paths in the spec
- [ ] One artifact key per logical file (no directory keys)

### Quality

- [ ] Action descriptions are specific enough for code generation
- [ ] No vague phrases like "process the data" or "handle the output"
- [ ] Error handling described for all action steps
- [ ] Similar existing workflows referenced (if any)

### Meta-Builder (if applicable)

- [ ] Three spec documents declared as output artifacts (spec template, SOP, standard)
- [ ] Filename format uses `{SLUG}_SPEC_TEMPLATE_v{N}.md` pattern
- [ ] `promote_builder_docs` step declared after `promote_workflow_package`
- [ ] Spec template requirements describe what the generated builder accepts as input
- [ ] SOP requirements describe setup, execution, troubleshooting
- [ ] Standard requirements describe quality bar for generated builder
- [ ] `input_spec_template` declared in workflow.toml if builder expects a specific input format
