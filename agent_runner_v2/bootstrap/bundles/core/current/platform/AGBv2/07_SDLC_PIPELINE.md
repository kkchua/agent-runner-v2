# SDLC Pipeline

> **Purpose:** Step-by-step walkthrough of the AGBv2 pipeline  
> **Audience:** Users wanting to understand how AGB works internally

---

## Overview

AGBv2 follows an **SDLC-scoped pipeline** with quality gates. The pipeline has **11 steps** organized into phases:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SDLC Phase              │  Steps                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  Analysis                │  1. analyze_requirement                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Plan ↔ Challenge        │  2. copy_infrastructure                     │
│                          │  3. plan_domain_logic                       │
│                          │  4. challenge_plan                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Implement ↔ Critic      │  5. implement_domain                        │
│                          │  6. critic_impl                             │
├─────────────────────────────────────────────────────────────────────────┤
│  Execution               │  7. assemble_package                        │
├─────────────────────────────────────────────────────────────────────────┤
│  Review → Validate       │  8. review_package                          │
│  → Gatekeep              │  9. validate_structure                      │
│                          │  10. gatekeep_package                        │
├─────────────────────────────────────────────────────────────────────────┤
│  Promote → Publish       │  11. promote_package                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Analyze Requirement

**Type:** Prompt  
**Purpose:** Understand the requirement document and produce structured Analysis JSON

### What Happens

1. Reads `REQUIREMENT_DOC` from input/
2. Parses YAML frontmatter (codename, title, version)
3. Extracts overview, input, output, transformation, constraints sections
4. Designs appropriate artifact keys (following `_FILE`/`_DIR` conventions)
5. Designs domain steps (action vs prompt selection)
6. Defines implementations if variants implied
7. Produces `ANALYSIS_JSON_FILE`

### Output

- `ANALYSIS_JSON_FILE` — Structured JSON matching the schema

### Quality Focus

- Complete extraction of requirements
- Proper artifact key naming
- Appropriate step types (action vs prompt)

---

## Step 2: Copy Infrastructure

**Type:** Action  
**Purpose:** Copy AGB infrastructure (actions.py + prompts/) to output

### What Happens

1. Extracts codename from requirement doc frontmatter
2. Determines output directory
3. Copies AGB's `actions.py` to output
4. Copies AGB's `prompts/` directory to output

### Why This Step

- Provides base infrastructure for domain-specific extensions
- Enables self-replication (AGB can build AGB)
- Maintains consistency across generated workflows

### Output

- `WORKFLOW_ACTIONS_FILE` — Copied actions.py
- `WORKFLOW_PROMPTS_DIR` — Copied prompts/
- `WORKFLOW_EXTENSIONS_FILE` — Placeholder context_extensions.py

### Skip in Generator

This step is skipped (noop) in generator implementation.

---

## Step 3: Plan Domain Logic

**Type:** Prompt  
**Purpose:** Design the domain-specific actions and prompts needed

### What Happens

1. Reads `ANALYSIS_JSON_FILE` and `REQUIREMENT_DOC`
2. Analyzes transformation requirements
3. Decides which steps need actions vs prompts
4. Designs action signatures (inputs, outputs, error handling)
5. Designs prompt objectives and expected outputs
6. Plans artifact flow between steps
7. Produces `DOMAIN_PLAN_FILE`

### Output

- `DOMAIN_PLAN_FILE` — Design plan for actions + prompts

### Quality Focus

- Clear separation of concerns (action vs prompt)
- Logical artifact flow
- Complete coverage of requirements

---

## Step 4: Challenge Plan

**Type:** Prompt  
**Purpose:** Attack the domain plan to find gaps and weaknesses

### What Happens

1. Reads `DOMAIN_PLAN_FILE` and `ANALYSIS_JSON_FILE`
2. Checks for missing edge cases
3. Identifies weak validations
4. Spots wrong artifact bindings
5. Finds incomplete transformation logic
6. Verifies constraint enforcement
7. Produces `PLAN_CHALLENGE_FILE`

### Refinement Loop

If issues found:
```
plan_domain_logic ──► challenge_plan
        ▲                  │
        └──────────────────┘ (max 2 iterations)
```

**Exhaustion:** If still issues after 2 iterations → `HUMAN_RETRY_REQUIRED`

### Output

- `PLAN_CHALLENGE_FILE` — Critique of the plan

### Quality Focus

- Missing edge cases
- Weak validations
- Wrong artifact bindings

---

## Step 5: Implement Domain

**Type:** Prompt  
**Purpose:** Write the actual domain logic: actions.py and prompt files

### What Happens

1. Reads `DOMAIN_PLAN_FILE`, `ANALYSIS_JSON_FILE`, `REQUIREMENT_DOC`, `WORKFLOW_EXTENSIONS_FILE`
2. Implements action functions with proper signatures
3. Writes prompt templates with objectives and instructions
4. Adds error handling to actions
5. Includes docstrings and type hints
6. Creates requirements.txt for external dependencies
7. Produces domain-specific deliverables

### Output

- `WORKFLOW_ACTIONS_FILE` — Complete actions.py
- `WORKFLOW_PROMPTS_DIR/` — Prompt template files
- `WORKFLOW_REQUIREMENTS_FILE` — requirements.txt

### Quality Focus

- Code logic and error handling
- Prompt clarity and completeness
- Constraint enforcement

---

## Step 6: Critic Implementation

**Type:** Prompt  
**Purpose:** Review the generated code and prompts for quality

### What Happens

1. Reads `WORKFLOW_ACTIONS_FILE`, `WORKFLOW_PROMPTS_DIR/`, `DOMAIN_PLAN_FILE`
2. Reviews code logic and error handling
3. Checks prompt clarity and completeness
4. Verifies constraint enforcement
5. Identifies missing validations
6. Assesses functional viability
7. Produces `IMPL_CRITIQUE_FILE`

### Refinement Loop

If issues found:
```
implement_domain ──► critic_impl
        ▲                │
        └────────────────┘ (max 2 iterations)
```

**Exhaustion:** If still issues after 2 iterations → `HUMAN_RETRY_REQUIRED`

### Output

- `IMPL_CRITIQUE_FILE` — Review findings

### Quality Focus

- Code correctness
- Prompt quality
- Functional viability

---

## Step 7: Assemble Package

**Type:** Action  
**Purpose:** Mechanically build structural files (no LLM)

### What Happens

1. Reads `ANALYSIS_JSON_FILE`
2. Generates `workflow.toml` with step chaining
3. Generates `context_extensions.py` with two-dict pattern
4. Generates `impls/{name}/impl.yaml` for each implementation
5. Filters out infrastructure steps (prefixed with `_`)

### What Gets Generated

**workflow.toml:**
- `[workflow]` section from identity
- `[[step]]` sections from domain_steps with `onsuccess` chaining
- `[[workflow.implementation]]` sections from implementations
- Terminal `step_completion` step

**context_extensions.py:**
- `INPUT_ARTIFACTS` dict from artifact_keys.inputs
- `OUTPUT_ARTIFACTS` dict from artifact_keys.intermediate + outputs
- `register_artifact_keys()` for backward compatibility
- `build_context_extensions()` using resolvers

**impls/{name}/impl.yaml:**
- `name`, `description`, `label` from implementation entry
- `overrides` section from implementation entry

### Output

- `WORKFLOW_MANIFEST_FILE` — Generated workflow.toml
- `WORKFLOW_EXTENSIONS_FILE` — Generated context_extensions.py
- `IMPL_OVERRIDE_FILES` — Generated impls/ directory

### Skip in Generator

This step is skipped (noop) in generator implementation.

---

## Step 8: Review Package

**Type:** Prompt  
**Purpose:** Holistic review of the assembled package

### What Happens

1. Reads all assembled files:
   - `WORKFLOW_MANIFEST_FILE`
   - `WORKFLOW_ACTIONS_FILE`
   - `WORKFLOW_EXTENSIONS_FILE`
   - `WORKFLOW_PROMPTS_DIR/`
   - `ANALYSIS_JSON_FILE`
2. Verifies alignment between requirements and output
3. Checks action/prompt quality
4. Validates artifact flow
5. Reviews implementation completeness
6. Assesses usability
7. Produces `PACKAGE_REVIEW_FILE`

### Refinement Loop

If issues found:
```
implement_domain ──► ... ──► review_package
        ▲                          │
        └──────────────────────────┘ (max 2 iterations)
```

Loops back to `implement_domain` to fix issues.

### Output

- `PACKAGE_REVIEW_FILE` — Comprehensive review

### Quality Focus

- Holistic quality
- Alignment with requirements
- Usability

---

## Step 9: Validate Structure

**Type:** Action  
**Purpose:** Deterministic structural validation

### What Happens

1. Validates file existence
2. Validates TOML syntax in workflow.toml
3. Validates Python syntax in actions.py
4. Checks artifact key consistency
5. Verifies step references exist

### Validation Checks

| Check | Description |
|-------|-------------|
| File existence | All declared files exist |
| TOML syntax | workflow.toml is valid TOML |
| Python syntax | actions.py is valid Python |
| Artifact keys | All keys in steps are declared in context_extensions |
| Step references | All `onsuccess` targets exist |
| Implementation dirs | All implementations have matching directories |

### Output

- `VALIDATION_FINDINGS_FILE` — Validation results

### Skip in Generator

This step is skipped (noop) in generator implementation.

---

## Step 10: Gatekeep Package

**Type:** Prompt  
**Purpose:** Final pass/fail gate with go/no-go decision

### What Happens

1. Reads all prior quality artifacts:
   - `WORKFLOW_MANIFEST_FILE`
   - `WORKFLOW_ACTIONS_FILE`
   - `VALIDATION_FINDINGS_FILE`
   - `PACKAGE_REVIEW_FILE`
   - `ANALYSIS_JSON_FILE`
2. Reviews all prior quality gates
3. Verifies functional viability
4. Confirms the workflow can actually run
5. Makes pass/fail decision
6. Produces `GATEKEEP_PACKAGE_FILE`

### Role Policy

Uses `gatekeeper_standard` role policy for final authority.

### Refinement Loop

If rejected:
```
implement_domain ──► ... ──► gatekeep_package
        ▲                          │
        └──────────────────────────┘ (max 2 iterations)
```

**Exhaustion:** If still rejected after 2 iterations → `HUMAN_RETRY_REQUIRED`

### Output

- `GATEKEEP_PACKAGE_FILE` — Go/no-go decision

### Quality Focus

- Functional viability
- Can the workflow actually run?

---

## Step 11: Promote Package

**Type:** Action  
**Purpose:** Deploy the workflow package

### What Happens

1. Reads codename from workflow.toml
2. Determines source directory
3. Determines target directory (`workflows/{codename}/`)
4. Backs up existing target (if exists)
5. Copies all files to target
6. Generates README.md if not present

### Output Location

```
workflows/{codename}/
├── workflow.toml
├── context_extensions.py
├── actions.py
├── prompts/
├── impls/ (optional)
└── README.md
```

### Backup

If target exists:
```
workflows/{codename}_bak_{timestamp}/
```

### Skip in Generator

This step is skipped (noop) in generator implementation.

---

## Quality Gates Summary

| Gate | Reviews | Does NOT Review |
|------|---------|-----------------|
| challenge_plan | Missing edge cases, weak validations, wrong artifact bindings | Workflow structure (predefined) |
| critic_impl | Code logic, error handling, prompt clarity, constraint enforcement | workflow.toml syntax (assembled) |
| review_package | Holistic quality of actions + prompts | Infrastructure assembly |
| validate_structure | File existence, syntax, artifact consistency | Domain logic correctness |
| gatekeep_package | Functional viability — can it run? | Structural compliance (already validated) |

---

## Refinement Loops

Three refinement loops in the pipeline:

```
Plan ↔ Challenge:
  plan_domain_logic ──► challenge_plan
          ▲                  │
          └──────────────────┘ (max 2)

Implement ↔ Critic:
  implement_domain ──► critic_impl
          ▲               │
          └───────────────┘ (max 2)

Review/Gatekeep:
  implement_domain ──► ... ──► review_package/gatekeep_package
          ▲                          │
          └──────────────────────────┘ (max 2)
```

---

## Extend Mode Pipeline

When `EXISTING_WORKFLOW_DIR` is provided (extend mode):

| Step | Normal Mode | Extend Mode |
|------|-------------|-------------|
| analyze_requirement | Design full structure | Read existing, analyze new impl only |
| copy_infrastructure | Copy AGB infra | Copy from existing |
| plan_domain_logic | Plan all actions/prompts | Plan new impl overrides only |
| implement_domain | Write full actions/prompts | Write new impl files only |
| assemble_package | Generate all from scratch | Merge existing + new |
| promote_package | Promote to workflows/ | Merge into existing workflows/ |

---

## Artifacts Flow

```
Step 1:  REQUIREMENT_DOC
         ↓
Step 2:  ANALYSIS_JSON_FILE ──► WORKFLOW_ACTIONS_FILE (infra)
         │                       WORKFLOW_PROMPTS_DIR (infra)
         │                       WORKFLOW_EXTENSIONS_FILE (placeholder)
         ↓
Step 3:  DOMAIN_PLAN_FILE
         ↓
Step 4:  PLAN_CHALLENGE_FILE (optional refine)
         ↓
Step 5:  WORKFLOW_ACTIONS_FILE (domain)
         WORKFLOW_PROMPTS_DIR (domain)
         WORKFLOW_REQUIREMENTS_FILE
         ↓
Step 6:  IMPL_CRITIQUE_FILE (optional refine)
         ↓
Step 7:  WORKFLOW_MANIFEST_FILE
         WORKFLOW_EXTENSIONS_FILE (final)
         IMPL_OVERRIDE_FILES
         ↓
Step 8:  PACKAGE_REVIEW_FILE (optional refine)
         ↓
Step 9:  VALIDATION_FINDINGS_FILE
         ↓
Step 10: GATEKEEP_PACKAGE_FILE (optional refine)
         ↓
Step 11: WORKFLOW_PACKAGE_DIR
```

---

## Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Analysis | ~3 min | ~3 min |
| Plan ↔ Challenge | ~6 min | ~9 min |
| Implement ↔ Critic | ~10 min | ~19 min |
| Execution | ~2 min | ~21 min |
| Review → Validate → Gatekeep | ~6 min | ~27 min |
| Promote | ~3 min | ~30 min |

**Total estimated time:** ~30 minutes for builder, ~15 minutes for generator.

---

## See Also

- [README.md](./README.md) — Quick start
- [04_PROMPTS_REFERENCE.md](./04_PROMPTS_REFERENCE.md) — Prompt slots
- [05_ACTIONS_REFERENCE.md](./05_ACTIONS_REFERENCE.md) — Actions
- [06_IMPLEMENTATIONS.md](./06_IMPLEMENTATIONS.md) — Builder vs Generator
- Workflow source: `workflows/artifact_generator_builder/workflow.toml`
