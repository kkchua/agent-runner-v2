# Prompts Reference

> **Purpose:** Documentation of all prompt slots in the AGBv2 pipeline  
> **Audience:** Developers creating custom implementations or debugging prompt issues

---

## Overview

AGBv2 has **7 prompt-driven steps**, each using a **slot** that can be filled by different implementations. The prompts are resolved using a **two-tier fallback**:

1. **Implementation-specific:** `impls/{name}/prompts/{step}/{option}.txt`
2. **Shared fallback:** `prompts/{step}/{option}.txt`

---

## Prompt Slots

| Slot | Step | Purpose | Artifacts In | Artifacts Out |
|------|------|---------|--------------|---------------|
| `analyze_requirement` | 1 | Parse requirement doc → Analysis JSON | `REQUIREMENT_DOC` | `ANALYSIS_JSON_FILE` |
| `plan_domain_logic` | 3 | Design actions + prompts | `ANALYSIS_JSON_FILE`, `REQUIREMENT_DOC` | `DOMAIN_PLAN_FILE` |
| `challenge_plan` | 4 | Attack the plan | `DOMAIN_PLAN_FILE`, `ANALYSIS_JSON_FILE` | `PLAN_CHALLENGE_FILE` |
| `implement_domain` | 5 | Write actions.py + prompts/ | `DOMAIN_PLAN_FILE`, `ANALYSIS_JSON_FILE`, `REQUIREMENT_DOC`, `WORKFLOW_EXTENSIONS_FILE` | `WORKFLOW_ACTIONS_FILE`, `WORKFLOW_PROMPTS_DIR`, `WORKFLOW_REQUIREMENTS_FILE` |
| `critic_impl` | 6 | Review code + prompts | `WORKFLOW_ACTIONS_FILE`, `WORKFLOW_PROMPTS_DIR`, `DOMAIN_PLAN_FILE` | `IMPL_CRITIQUE_FILE` |
| `review_package` | 8 | Holistic review | `WORKFLOW_MANIFEST_FILE`, `WORKFLOW_ACTIONS_FILE`, `WORKFLOW_EXTENSIONS_FILE`, `WORKFLOW_PROMPTS_DIR`, `ANALYSIS_JSON_FILE` | `PACKAGE_REVIEW_FILE` |
| `gatekeep_package` | 10 | Final pass/fail | `WORKFLOW_MANIFEST_FILE`, `WORKFLOW_ACTIONS_FILE`, `VALIDATION_FINDINGS_FILE`, `PACKAGE_REVIEW_FILE`, `ANALYSIS_JSON_FILE` | `GATEKEEP_PACKAGE_FILE` |

---

## Slot 1: analyze_requirement

**Purpose:** Read the requirement document and produce structured Analysis JSON.

**Inputs:**
- `REQUIREMENT_DOC` — The requirement markdown file
- `CODENAME` — Extracted from requirement frontmatter

**Outputs:**
- `ANALYSIS_JSON_FILE` — Structured JSON matching the schema

**What the prompt does:**
1. Parse requirement doc frontmatter (codename, title, version)
2. Extract input/output/transform/constraints sections
3. Design appropriate artifact keys (following `_FILE`/`_DIR` conventions)
4. Design domain steps (action vs prompt selection)
5. Define implementations if variants are implied

**Key considerations:**
- Artifact keys MUST end with `_FILE` for files, `_DIR` for directories
- Domain steps should NOT include infrastructure steps (prefixed with `_`)
- The assembler filters infrastructure steps automatically

---

## Slot 2: plan_domain_logic

**Purpose:** Design the domain-specific actions and prompts needed.

**Inputs:**
- `ANALYSIS_JSON_FILE` — Structured requirements
- `REQUIREMENT_DOC` — Original requirement

**Outputs:**
- `DOMAIN_PLAN_FILE` — Design plan for actions + prompts

**What the prompt does:**
1. Analyze the transformation requirements
2. Decide which steps need actions vs prompts
3. Design action signatures (inputs, outputs, error handling)
4. Design prompt objectives and expected outputs
5. Plan artifact flow between steps

**Key considerations:**
- Actions are for deterministic operations (parsing, API calls, file I/O)
- Prompts are for LLM-driven operations (analysis, generation, review)
- Each step should have clear inputs and outputs

---

## Slot 3: challenge_plan

**Purpose:** Attack the domain plan to find gaps and weaknesses.

**Inputs:**
- `DOMAIN_PLAN_FILE` — The domain plan
- `ANALYSIS_JSON_FILE` — Requirements

**Outputs:**
- `PLAN_CHALLENGE_FILE` — Critique of the plan

**What the prompt does:**
1. Check for missing edge cases
2. Identify weak validations
3. Spot wrong artifact bindings
4. Find incomplete transformation logic
5. Verify constraint enforcement

**Key considerations:**
- This is a self-challenge step (SDLC plan ↔ challenge pattern)
- If issues found, the plan is refined (max 2 iterations)
- Focus on domain logic, not infrastructure

---

## Slot 4: implement_domain

**Purpose:** Write the actual domain logic: actions.py and prompt files.

**Inputs:**
- `DOMAIN_PLAN_FILE` — Approved domain plan
- `ANALYSIS_JSON_FILE` — Requirements
- `REQUIREMENT_DOC` — Original requirement
- `WORKFLOW_EXTENSIONS_FILE` — Context extensions (for artifact key reference)

**Outputs:**
- `WORKFLOW_ACTIONS_FILE` — Complete actions.py
- `WORKFLOW_PROMPTS_DIR` — Prompt template files
- `WORKFLOW_REQUIREMENTS_FILE` — requirements.txt (if needed)

**What the prompt does:**
1. Implement action functions with proper signatures
2. Write prompt templates with objectives and instructions
3. Add error handling to actions
4. Include docstrings and type hints
5. Create requirements.txt for external dependencies

**Key considerations:**
- Actions MUST use `@action("name")` decorator
- Actions MUST accept `context`, `state`, `step_cfg`, `project_root`
- Actions MUST return `ActionResult`
- Prompts should include objective, inputs, outputs, and self-critic

---

## Slot 5: critic_impl

**Purpose:** Review the generated code and prompts for quality.

**Inputs:**
- `WORKFLOW_ACTIONS_FILE` — Generated actions.py
- `WORKFLOW_PROMPTS_DIR` — Generated prompts
- `DOMAIN_PLAN_FILE` — Original plan

**Outputs:**
- `IMPL_CRITIQUE_FILE` — Review findings

**What the prompt does:**
1. Review code logic and error handling
2. Check prompt clarity and completeness
3. Verify constraint enforcement
4. Identify missing validations
5. Assess functional viability

**Key considerations:**
- This is a self-review step (SDLC implement ↔ critic pattern)
- If issues found, implementation is refined (max 2 iterations)
- Focus on functional correctness, not style

---

## Slot 6: review_package

**Purpose:** Holistic review of the assembled package.

**Inputs:**
- `WORKFLOW_MANIFEST_FILE` — workflow.toml
- `WORKFLOW_ACTIONS_FILE` — actions.py
- `WORKFLOW_EXTENSIONS_FILE` — context_extensions.py
- `WORKFLOW_PROMPTS_DIR` — prompts/
- `ANALYSIS_JSON_FILE` — Original requirements

**Outputs:**
- `PACKAGE_REVIEW_FILE` — Comprehensive review

**What the prompt does:**
1. Verify alignment between requirements and output
2. Check action/prompt quality
3. Validate artifact flow
4. Review implementation completeness
5. Assess usability

**Key considerations:**
- This is the final quality gate before validation
- Can trigger refinement loop back to implement_domain
- Max 2 refinement iterations

---

## Slot 7: gatekeep_package

**Purpose:** Final pass/fail gate with go/no-go decision.

**Inputs:**
- `WORKFLOW_MANIFEST_FILE` — workflow.toml
- `WORKFLOW_ACTIONS_FILE` — actions.py
- `VALIDATION_FINDINGS_FILE` — Structural validation results
- `PACKAGE_REVIEW_FILE` — Holistic review
- `ANALYSIS_JSON_FILE` — Original requirements

**Outputs:**
- `GATEKEEP_PACKAGE_FILE` — Go/no-go decision

**What the prompt does:**
1. Review all prior quality gates
2. Verify functional viability
3. Confirm the workflow can actually run
4. Make pass/fail decision

**Key considerations:**
- This is the final gate before promotion
- If rejected, loops back to implement_domain (max 2 iterations)
- Uses `gatekeeper_standard` role policy

---

## Implementation-Specific Prompts

Each implementation (`builder`, `generator`, or custom) can provide its own prompt variants:

### Directory Structure

```
impls/{name}/
└── prompts/
    ├── analyze_requirement/
    │   └── {option}.txt
    ├── plan_domain_logic/
    │   └── {option}.txt
    ├── challenge_plan/
    │   └── {option}.txt
    ├── implement_domain/
    │   └── {option}.txt
    ├── critic_impl/
    │   └── {option}.txt
    ├── review_package/
    │   └── {option}.txt
    └── gatekeep_package/
        └── {option}.txt
```

### impl.yaml Configuration

```yaml
prompt_slots:
  analyze_requirement:
    label: "Analyze Requirement"
    default: standard
    options:
      - name: standard
        file: "prompts/analyze_requirement/standard.txt"
      - name: advanced
        file: "prompts/analyze_requirement/advanced.txt"
```

### Two-Tier Resolution

When `{{ slot.analyze_requirement }}` is resolved:

1. Check `impls/{active_impl}/prompts/analyze_requirement/{selected_option}.txt`
2. If not found, check `prompts/analyze_requirement/{selected_option}.txt`

This allows implementations to override specific prompts while sharing a common pool.

---

## Prompt Writing Guidelines

### Structure

A good prompt template has these sections:

```markdown
# Objective
What the LLM should accomplish.

# Context
Relevant background information.

# Input Artifacts
What to read (use {ARTIFACT_KEY} placeholders).

# Instructions
Step-by-step directions.

# Output Instructions
Where to write, what format.

# Constraints
Hard requirements.

# Self-Critic
Before finishing, verify...
```

### Do's and Don'ts

**✅ Do:**
- Be specific about expected output
- Include example formats
- Reference artifacts with `{ARTIFACT_KEY}` placeholders
- Add validation instructions
- Include self-critic section

**❌ Don't:**
- Be vague about expected output
- Hardcode file paths
- Assume specific tool availability
- Skip error handling guidance

---

## See Also

- [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) — Plugin architecture
- [07_SDLC_PIPELINE.md](./07_SDLC_PIPELINE.md) — Pipeline walkthrough
- Workflow source: `workflows/artifact_generator_builder/prompts/`
