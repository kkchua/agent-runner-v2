# Draft Initiative Authoring Guide

> **Purpose:** How to write a DRAFT_INIT document that kicks off the SDLC
> pipeline. The draft is the human-authored input to `sdlc_00_init_doc_v1`,
> which transforms it into a structured, approved INIT-DOC.
>
> **Audience:** Human developers and AI agents (e.g., `/initiative_draft_builder` skill).
>
> **Companion documents:**
> - [DRAFT_INIT Template](../../docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/01_DRAFT_INIT_template.md) -- the canonical template
> - [INIT Template](../../docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/02_INIT_template.md) -- what the draft becomes after sdlc_00
> - [SDLC Workflow SOP](../../docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/WORKFLOW_SOP_v1.md) -- full SDLC process reference

---

## Table of Contents

- [1: What is a Draft Initiative](#1-what-is-a-draft-initiative)
- [2: Before You Start](#2-before-you-start)
- [3: Section-by-Section Authoring](#3-section-by-section-authoring)
- [4: Writing Guidelines](#4-writing-guidelines)
- [5: Worked Example](#5-worked-example)
- [6: Common Pitfalls](#6-common-pitfalls)
- [7: Draft Quality Checklist](#7-draft-quality-checklist)

---

## 1: What is a Draft Initiative

A draft initiative is a **human-authored markdown document** that describes
a new piece of work you want the SDLC pipeline to process. It is the
starting point of the entire SDLC chain:

```
DRAFT_INIT  -->  sdlc_00 (init_doc)  -->  INIT-DOC (approved)
    -->  sdlc_10 (requirements)  -->  REQ-DOC
    -->  sdlc_20 (planning)  -->  PLAN-DOC
    -->  sdlc_30 (backlog)  -->  BACKLOG-DOC
    -->  ... through sdlc_80 (review)
```

The draft does NOT need to be perfect. The `sdlc_00_init_doc_v1` workflow
will refine it into a structured, validated INIT-DOC. But the better your
draft, the better the output.

**Key principle:** The draft describes WHAT you want to achieve and WHY.
The SDLC pipeline figures out HOW.

### Storage Location

```
docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/
```

### Naming Convention

```
DRAFT-INIT-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description | Example |
|---|---|---|
| `DRAFT-INIT` | Fixed prefix | `DRAFT-INIT` |
| `YYYYMMDD` | Date of creation | `20260731` |
| `NN` | Sequence number (01-99) | `001` |
| `slug` | Short hyphenated description | `console-sdlc10-support` |

**Example:** `DRAFT-INIT-20260731-001_add-user-authentication.md`

---

## 2: Before You Start

Answer these questions before writing:

1. **What is the initiative?** Can you describe it in one sentence?

2. **What problem does it solve?** What is broken, missing, or painful today?

3. **What does success look like?** How will you know the initiative is done?

4. **What are the boundaries?** What is explicitly in scope? Out of scope?

5. **What does it depend on?** Other initiatives, systems, data, approvals?

6. **What constraints exist?** Technology, time, budget, compliance?

7. **Who cares?** Who is the sponsor? Who are the users? Who reviews?

---

## 3: Section-by-Section Authoring

### 3.1: YAML Frontmatter

Every draft MUST include this frontmatter:

```yaml
---
template_id: SYS-03-DI
version: "1.0.0"
doc_type: "workflow_output"
authority: "human-authored"
scan_policy: "include"
scan_reason: "Brief reason this doc should be scanned"
managed_by: "human-authored"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

**Rules:**
- `template_id` must be `SYS-03-DI` (identifies this as a draft initiative)
- `authority` and `managed_by` must be `human-authored` (not workflow-generated)
- `lifecycle_status` must be `draft`
- `layer` must be `layer3` (SDLC delivery layer)
- `scan_reason` should briefly describe the initiative topic

### 3.2: Title

A clear, concise title as a level-1 heading:

```markdown
# Add User Authentication to Operator Console
```

**Good:** Specific, actionable, clear scope.
**Bad:** "Improve the system" (vague), "Fix Everything" (no scope).

### 3.3: Objective

One paragraph describing what this initiative aims to achieve. Focus on
the desired outcome, not the implementation.

**Good:**
```markdown
## Objective

Add SDLC workflow support to the operator console for sdlc_10_requirement_v1
(Initiative Intake). The console must allow users to select a draft initiative
document, submit it as a job to the backend, and have the daemon process it
through the sdlc_10 workflow.
```

**Bad:**
```markdown
## Objective

Make the console better.
```

### 3.4: Problem Statement

This is the most important section. It convinces the reader (and the LLM)
that this initiative is worth doing. Structure it as:

**Current State** -- What exists today? What is the status quo?

**Pain Points** -- What is broken, missing, or frustrating?

**Why This Initiative Is Needed** -- Why can't the current state continue?

**Impact of Not Undertaking** -- What happens if we do nothing?

```markdown
## Problem Statement

### Current State

The operator console currently supports generic job submission via the
"submit job" action, but has no awareness of SDLC workflow input requirements.

### Pain Points

- No file picker for selecting draft initiative documents.
- Users must manually construct --input KEY=VALUE arguments.
- No visual feedback on which workflows require which inputs.

### Why This Initiative Is Needed

Without SDLC-specific input handling, users cannot efficiently submit SDLC
workflow jobs through the console.

### Impact of Not Undertaking This Initiative

- SDLC workflows remain unusable from the console UI.
- Users must fall back to batch files or CLI.
```

### 3.5: Expected Outcomes

A bullet list of concrete, measurable outcomes. Each should be verifiable.

**Good:**
```markdown
## Expected Outcomes

- Users can select sdlc_10_requirement_v1 from the workflow dropdown and
  see a file picker for the draft initiative document.
- Clicking "Run Action" with "submit job" submits the job with the correct
  DRAFT_INIT_DOC input artifact path.
- The daemon processes the submitted job through sdlc_10 workflow steps.
```

**Bad:**
```markdown
## Expected Outcomes

- The console works better.
- Users are happier.
```

### 3.6: Scope

Define boundaries explicitly. Three sub-sections:

**In Scope** -- What WILL be done. Be specific.

**Out of Scope** -- What WILL NOT be done. This prevents scope creep.

**Boundary Conditions** (optional) -- Edge cases or gray areas.

```markdown
## Scope

### In Scope

- File picker UI component (Flet FilePicker + TextField + Browse button).
- Conditional visibility: show file picker only when action is "submit job"
  AND selected workflow name starts with "sdlc_".
- Pass selected file path as --input DRAFT_INIT_DOC=<path>.

### Out of Scope

- Support for sdlc_20 through sdlc_80 workflows (separate phases).
- Artifact dropdown for selecting approved outputs from previous runs.
- Output display for generated artifacts after job completion.
```

### 3.7: Constraints

List all constraints -- things that limit how the work can be done:

- **Technical:** Must use Flet UI framework. Must integrate with existing
  submit_commands.main() flow.
- **Platform:** Must work on Windows (primary development platform).
- **Time:** No specific deadline.
- **Resource:** Single developer.

If a constraint category does not apply, write "None" explicitly.

### 3.8: Dependencies

List external dependencies:

- Other initiatives that must complete first.
- Third-party systems or services required.
- Data or infrastructure prerequisites.
- Organizational approvals needed.

```markdown
## Dependencies

- Draft initiative documents must exist in the
  docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/ directory.
- The sdlc_10_requirement_v1 workflow must be synced to the backend.
```

### 3.9: Success Criteria

Specific, testable criteria. Think of these as acceptance tests:

```markdown
## Success Criteria

- Console launches without errors with SDLC workflows in the config.
- Selecting sdlc_10_requirement_v1 shows the file picker row.
- Selecting a non-SDLC workflow hides the file picker row.
- Browsing and selecting a .md file populates the path text field.
- Clicking "Run Action" with "submit job" submits successfully.
```

**Good criteria are testable:** Someone can read each line and verify
pass/fail by running the software or inspecting the output.

**Bad criteria are vague:** "The feature works correctly" -- how do you
measure "correctly"?

### 3.10: Notes (Optional)

Additional context, assumptions, or background:

- Related plans or documents
- Prior art or similar implementations
- Assumptions made during drafting
- Open questions for the review process

---

## 4: Writing Guidelines

### Length

Aim for **1-3 pages** for the complete draft. Each section should be
concise but complete. The Problem Statement and Scope sections may be
longer than others.

### Tone

- Clear, direct language. No marketing or promotional tone.
- Specific and precise. Avoid vague statements.
- Active voice where possible.
- Short, focused paragraphs.

### ASCII Only

All content MUST use ASCII characters only:
- Use plain hyphens (`-`) for dashes. NOT em-dashes or en-dashes.
- Use straight quotes (`"` and `'`). NOT curly quotes.
- No Unicode bullets, arrows, or ellipsis.

### Plain Text Headings

Section headings must use plain text only. No backticks, bold, italics,
or other inline formatting in headings.

### Completeness

- All required sections MUST be present.
- If a sub-item does not apply, state "None" or "N/A" explicitly.
- Do not leave sections empty -- either fill them or state "None".

---

## 5: Worked Example

See the sample draft at:
```
docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/
  DRAFT-INIT-20260722-001_console-sdlc10-support.md
```

This draft describes adding SDLC workflow support to the operator console.
Notice how it:

1. **States the problem clearly** -- "No file picker", "Users must manually
   construct arguments"
2. **Defines scope precisely** -- "File picker UI component", "Conditional
   visibility", but NOT "Support for sdlc_20 through sdlc_80"
3. **Lists testable success criteria** -- "Selecting sdlc_10 shows the file
   picker row", "Selecting a non-SDLC workflow hides the file picker row"
4. **Acknowledges constraints** -- "Must use Flet UI framework", "Must work
   on Windows"
5. **Notes future work** -- "This is Phase 1 of the console SDLC support plan"

---

## 6: Common Pitfalls

### Pitfall 1: Too Vague

**Bad:**
```markdown
## Objective

Improve the workflow system.

## Expected Outcomes

- Better performance.
- Easier to use.
```

The sdlc_00 workflow cannot produce a meaningful INIT-DOC from vague input.
Be specific about what you want, why, and how you will measure success.

### Pitfall 2: Including Implementation Details

**Bad:**
```markdown
## Scope

### In Scope

- Create a new Flet TextField widget at line 142 of handlers.py.
- Add a submit_job_v2() method to RunnerActionService class.
- Modify the backend API to accept multipart form data.
```

The draft describes WHAT, not HOW. Implementation details belong in later
SDLC phases (planning, task decomposition). Keep the draft at the problem
and outcome level.

### Pitfall 3: Missing Out of Scope

Without explicit "Out of Scope" boundaries, the INIT-DOC may include
assumptions about scope that you did not intend. Always state what is
NOT covered.

### Pitfall 4: Untestable Success Criteria

**Bad:**
```markdown
## Success Criteria

- The feature works as expected.
- Users find it intuitive.
```

**Good:**
```markdown
## Success Criteria

- File picker appears when sdlc_10 is selected.
- File picker disappears when a non-SDLC workflow is selected.
- Submitting a job with a selected file produces a 200 response from backend.
```

### Pitfall 5: Wrong Frontmatter

Using `authority: "workflow-generated"` or `lifecycle_status: "approved"`
in a draft. Drafts are human-authored and start as draft status.

### Pitfall 6: Wrong File Location or Name

Drafts must go in `00_draft_initiatives/` with the naming pattern
`DRAFT-INIT-{YYYYMMDD}-{NN}_{slug}.md`. The workflow discovers inputs
from this directory.

---

## 7: Draft Quality Checklist

Before submitting to `sdlc_00_init_doc_v1`, verify:

### Structure

- [ ] YAML frontmatter present with all required fields
- [ ] `template_id: SYS-03-DI`
- [ ] `authority: "human-authored"`
- [ ] `lifecycle_status: "draft"`
- [ ] Title as level-1 heading

### Content

- [ ] Objective is one clear paragraph describing the desired outcome
- [ ] Problem Statement includes current state, pain points, why needed, impact of not doing
- [ ] Expected Outcomes are concrete and measurable
- [ ] Scope has both "In Scope" and "Out of Scope" sub-sections
- [ ] Constraints are listed (or "None" stated for each category)
- [ ] Dependencies are listed (or "None" stated)
- [ ] Success Criteria are specific and testable
- [ ] Notes section included if there is additional context

### Quality

- [ ] No implementation details (that belongs in planning phase)
- [ ] No vague statements ("improve", "better", "easier")
- [ ] ASCII-only content (no em-dashes, curly quotes)
- [ ] Plain text headings (no backticks or formatting)
- [ ] 1-3 pages total length

### File

- [ ] Filename follows pattern: `DRAFT-INIT-{YYYYMMDD}-{NN}_{slug}.md`
- [ ] Saved in `docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/`
- [ ] Slug is short, hyphenated, descriptive
