# Workflow Builder Requirements

> **What the builder enforces automatically.** The workflow_builder_v1 reads
> a domain spec and generates a complete workflow package. This document
> captures all structural rules the builder enforces without the spec
> needing to specify them.
>
> **Audience:** Builder prompt maintainers, workflow architects, reviewers.

---

## Table of Contents

- [1: Auto-Enforcement Rules](#1-auto-enforcement-rules)
- [2: Workflow Patterns](#2-workflow-patterns)
- [3: Role Policies](#3-role-policies)
- [4: Routing Rules](#4-routing-rules)
- [5: Gatekeeper Rules](#5-gatekeeper-rules)
- [6: Meta-Workflow Rules](#6-meta-workflow-rules)
- [7: Self-Critic Pattern](#7-self-critic-pattern)
- [8: Action Reuse](#8-action-reuse)
- [9: Generated File Structure](#9-generated-file-structure)
- [10: Artifact Key Conventions](#10-artifact-key-conventions)

---

## 1: Auto-Enforcement Rules

The builder automatically enforces these structural patterns for ALL
generated workflows. Spec authors do NOT need to specify them.

| Rule | What the builder does |
|------|----------------------|
| **Step sequence** | Proposes based on domain requirements |
| **Role policies** | Assigns based on step purpose (generate/review/refine/validate) |
| **Routing** | Determines based on workflow type |
| **Gatekeeper placement** | Auto-places 4 gatekeepers for meta-workflows |
| **TDD loop** | Auto-adds for meta-workflows (generate_test_criteria → review → refine) |
| **exhausted_failure** | Auto-injects `exhausted_failure_code` + `exhausted_failure_class` on ALL refine loops |
| **init_step** | Auto-detects (`generate_test_criteria` for meta-workflows, first step otherwise) |
| **Action reuse** | Audits existing actions before generating custom ones |
| **Self-critic** | Adds self-critic section to ALL generated prompts |
| **Self-validation** | Adds self-validation section to ALL generated prompts |

---

## 2: Workflow Patterns

The builder recognizes 6 patterns and generates appropriate structure:

### Pattern 1: Action-Only Pipeline

All steps are deterministic Python operations. No LLM needed.

```
validate -> publish -> init -> sync -> write_summary -> stepCompletion
```

- No prompts/ directory
- No [step.coder] sections
- Each step is a Python @action function

### Pattern 2: Prompt-Driven with Review/Refine Loop

LLM generates documents that need quality review.

```
generate -> technical_critique -> review -> [refine -> review] -> promote -> stepCompletion
```

- 4 prompt files: generate, critique, review, refine
- 2 role policies: `architect_standard` (generate/refine), `reviewer_standard` (critique/review)
- Refinement loop with exhausted_failure

### Pattern 3: Mixed with Generate + Review + Refine + Audit

Extended Pattern 2 with additional validation/audit steps.

```
generate -> review -> refine -> validate -> audit -> promote -> stepCompletion
```

- Uses `validation_standard` role policy for audit steps
- Has governance adapters

### Pattern 4: Gatekeeper QC Pipeline

Complex multi-phase workflows where each phase output must be validated.

```
generate -> gatekeep -> resolve -> define -> gatekeep -> design -> gatekeep -> generate_pkg -> gatekeep -> validate -> review -> [refine] -> promote -> stepCompletion
```

- Every producer step followed by a QC gatekeeper
- Gatekeepers use `validation_standard` role policy
- Each gatekeeper has `on_reject_refine` with exhausted_failure

### Pattern 5: Step-per-Operation with Human Gates

Each step produces tangible output that a human should review.

```
step_1 -> [human gate] -> step_2 -> [human gate] -> step_3 -> stepCompletion
```

- Every step has `requires_human_approval_after = true`
- Steps can be prompt-driven or action-driven

### Pattern 6: Meta-Workflow Builder

The workflow's output is another workflow package. Specialized variant of
Pattern 4 with mandatory TDD loop.

```
generate_test_criteria -> review -> [refine] -> analyze -> gatekeep -> ...
```

- TDD loop is mandatory (first 3 steps)
- init_step = "generate_test_criteria"
- 4 gatekeepers with distinct artifact keys
- Action reuse required

---

## 3: Role Policies

The builder assigns role policies based on step purpose:

| Policy | Use For |
|--------|---------|
| `architect_standard` | Generation steps (create documents, designs) |
| `reviewer_standard` | Review/critique steps (evaluate quality) |
| `refine_standard` | Refinement steps (fix issues from review) |
| `validation_standard` | Gatekeeper/audit steps (validate completeness) |
| `plan_standard` | Planning steps (create plans, strategies) |
| `documentation_standard` | Documentation generation steps |
| `implement_standard` | Code implementation steps |
| `execution_standard` | Code execution steps |

**Assignment rules:**
- Generate/create → `architect_standard`
- Review/critique → `reviewer_standard`
- Refine/fix → `refine_standard`
- Gatekeep/validate → `validation_standard`

---

## 4: Routing Rules

### Standard Routing

| Field | Purpose |
|-------|---------|
| `onsuccess` | Next step name on success, or `stepCompletion` |
| `on_reject_refine` | (Review steps only) Route to refine step on rejection |
| `requires_human_approval_after` | Pause for human approval after step |

### Mandatory exhausted_failure

**Every step with `on_reject_refine` MUST declare:**

```toml
[step.on_reject_refine]
step = "refine_step_name"
artifact = "ARTIFACT_KEY"
max_iterations = 2
exhausted_failure_code = "STEP_NAME_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"
```

No exceptions. Without these, the runner doesn't know how to handle
refinement exhaustion.

### Terminal Step

Every workflow MUST end with:

```toml
[[step]]
name = "stepCompletion"
action = "step_completion"
```

---

## 5: Gatekeeper Rules

### When to Auto-Place

The builder auto-places 4 gatekeepers for **meta-workflows** (workflows
that generate other workflow packages). For other complex workflows, the
builder suggests gatekeepers based on the number of major phases.

### Standard Gatekeeper Keys

| Gatekeeper | Artifact Key | Validates | Rejects To |
|---|---|---|---|
| After requirements | `GATEKEEP_REQUIREMENTS` | Parse completeness, classification | analyze_spec |
| After artifacts | `GATEKEEP_ARTIFACTS` | Every artifact has one producer | define_artifacts |
| After steps | `GATEKEEP_STEPS` | Step sequence covers all phases | design_steps |
| After package | `GATEKEEP_PACKAGE` | Generated files match design | generate_package |

### Rules

- Each gatekeeper produces a **distinct** artifact key
- Never reuse `REVIEW_FILE_SUGGESTED` for gatekeepers
- Gatekeepers use `validation_standard` role policy
- Each gatekeeper has `on_reject_refine` with exhausted_failure

---

## 6: Meta-Workflow Rules

Meta-workflows generate other workflow packages. They have stricter
requirements because their output is structural, not documentary.

### Mandatory Elements

1. **TDD loop** — First 3 steps must be:
   - `generate_test_criteria` → `review_test_criteria` → `refine_test_criteria`
   - Establishes acceptance criteria before any design work

2. **init_step** — Must be `generate_test_criteria`

3. **4 gatekeepers** — Full pipeline validation:
   - GATEKEEP_REQUIREMENTS, GATEKEEP_ARTIFACTS, GATEKEEP_STEPS, GATEKEEP_PACKAGE

4. **exhausted_failure** — On ALL refine loops (not just some)

5. **Action reuse** — Must reuse:
   - `validate_workflow_bundle` (structural validation)
   - `promote_workflow_package` (copy to workflows/ directory)
   - `step_completion` (terminal step)

### Detection

The builder detects meta-workflows by checking if the spec's output is
another workflow package (workflow.toml + prompts/ + actions.py +
context_extensions.py). The `is_meta_workflow` flag is set in the
requirements document YAML frontmatter.

---

## 7: Self-Critic Pattern

All generated prompts include a self-critic section that challenges
reasoning quality, not just structural completeness.

### Pattern 1: Producer (generate, define, design steps)

```
Self-Critic (Before Self-Validation)

1. Am I introducing assumptions not supported by the input documents?
2. Is this the simplest approach that meets the objective, or am I over-engineering?
3. If a downstream step reads this output, what would confuse them or block them?
4. Did I stay in my lane, or did I leak into another step's scope?
```

### Pattern 2: Gatekeeper/Review (validate, review steps)

```
Self-Critic (Before Final Verdict)

1. Am I rubber-stamping, or did I actually verify each claim against source files?
2. Did I find at least one substantive finding, or am I just saying "looks good"?
3. If I missed an issue that a later step catches, what would it be?
4. Is my verdict based on evidence from the files, or on assumptions?
```

### Pattern 3: Refine (fix steps)

```
Self-Critic (Before Reporting Complete)

1. Did I fix the root cause, or just the symptom the review flagged?
2. Did my changes introduce new inconsistencies in other files?
3. Are there issues the review missed that I should fix proactively?
4. If the reviewer re-reads my output, would they find new issues?
```

---

## 8: Action Reuse

Before generating custom actions, the builder audits existing reusable
actions:

| Action | Location | Purpose |
|--------|----------|---------|
| `validate_workflow_bundle` | workflow_builder_v1/actions.py | Structural validation of workflow packages |
| `promote_workflow_package` | workflow_builder_v1/actions.py | Copy package to workflows/ directory |
| `step_completion` | agent_runner_v2/actions/step_completion.py | Standard terminal step |

**Rule:** Reference existing actions in workflow.toml with
`action = "existing_name"` instead of generating duplicate code.

---

## 9: Generated File Structure

The builder generates these files in the workflow package directory:

```
workflows/{workflow_name}/
├── workflow.toml              # Always generated
├── context_extensions.py      # Always generated
├── README.md                  # Always generated
├── actions.py                 # If any action-driven steps exist
├── .env.sample                # If environment variables needed
├── config.json.sample         # If runtime config needed
└── prompts/                   # One file per prompt-driven step
    ├── 00_step_name.txt
    ├── 01_step_name.txt
    └── ...
```

### Principles-Based Generation

The builder infers what files are needed from the design documents
(REQUIREMENTS, ARTIFACTS, STEPS), not from a fixed list. The fundamental
principle: generate EVERY file the design requires.

---

## 10: Artifact Key Conventions

| Convention | Example |
|------------|---------|
| UPPER_SNAKE_CASE | `REQ_FILE`, `IMAGE_INDEX` |
| `_FILE` suffix for documents | `REQ_FILE`, `PLAN_FILE` |
| `_INDEX` suffix for batch indexes | `IMAGE_INDEX`, `VIDEO_INDEX` |
| `REVIEW_FILE_SUGGESTED` for reviews | Standard runner convention |
| One key per logical file | Never directory keys |
| Path placeholders | `{job_id}`, `{seq}`, `{slug}`, `{iter}` |

---

## Relationship to Other Documents

| Document | Purpose |
|----------|---------|
| **This document** | What the builder enforces (structural rules) |
| `WORKFLOW_CREATION_GUIDE.md` | How to create workflow packages manually (file-by-file reference) |
| `WORKFLOW_SPEC_TEMPLATE.md` | Blank template for domain specs (what to fill in) |
| `SPEC_AUTHORING_GUIDE.md` | How to write a good domain spec (domain guidance) |
| `WORKFLOW_BUILDER_SOP.md` | Storage, naming, audit conventions |
| Builder prompts (00-06) | Step-by-step instructions the builder LLM follows |
