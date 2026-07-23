---
title: "SDLC Technical Critique Step Plan"
version: "1.0.0"
status: "draft"
created: "2026-07-23"
author: "human"
---

# SDLC Technical Critique Step Plan

## Problem Statement

The current SDLC workflow review steps check document compliance (metadata,
encoding, structure, traceability) but never verify that the solution
actually works. This has led to systematic quality failures:

1. **Wrong API usage** -- The sdlc_50 implementation plan specified
   `page.overlay.append(file_picker)` for a Flet FilePicker, but in Flet
   0.86.1 FilePicker is a Service (not a Control) and must use
   `page.services.append()`. The review approved it without checking.

2. **Async/sync mismatch** -- The implementation used a synchronous lambda
   (`lambda _: file_picker.pick_files()`) for an async method. The review
   did not catch this.

3. **Invisible controls** -- The row was set to `visible=False` with no
   way to verify the controls work. The review approved this as correct.

4. **Deprecated APIs** -- `ft.ElevatedButton` is deprecated in Flet 0.86.1
   (use `ft.Button` instead). No step in the chain flagged this.

5. **Metadata hallucination** -- The reviewer wrote a compliance table
   claiming `lifecycle_status = "draft"` when the actual value was
   `"Approved"`. The review prompt's metadata check was too weak.

Root cause: Every SDLC step produces and reviews documents, but nothing
actually runs the code, checks the APIs, or critically evaluates whether
the solution is implementable.

## Solution

Insert a new `technical_critique` step between `generate` and `review` in
each SDLC workflow. This step acts as a skeptical senior engineer -- it
questions the solution, verifies technical claims against the real codebase,
runs code where applicable, and critiques design quality.

### New Workflow Flow

```
generate -> technical_critique -> review -> refine -> promote -> complete
                 |
                 v (REJECTED)
              generate (retry, max 2)
```

- **technical_critique**: Internal quality gate. No human approval needed.
- **APPROVED** -> proceed to review (compliance check).
- **REJECTED** -> loop back to generate with critique feedback.
- Produces a CRITIQUE_FILE_SUGGESTED document artifact.

### Test Traceability Chain

A key improvement is the test-driven chain across sdlc_40 through sdlc_80:

```
sdlc_40 TASK  -- defines Test Scope (what to test)
     |
sdlc_50 IMPL  -- implements tests (write test code)
     |
sdlc_60 EXEC  -- runs tests (execute + record results)
     |
sdlc_70 VAL   -- verifies coverage (all tests ran? evidence accurate?)
     |
sdlc_80 REV   -- captures test quality lessons
```

This ensures every task has defined test criteria, every implementation
includes test code, every execution records actual test results, and every
validation verifies the evidence.

## Critique Focus Per Stage

### sdlc_00 (Initiative) -- Scope & Feasibility Critique

**Input:** INIT_FILE + DRAFT_INIT_FILE

Focus areas:
- Is the problem statement clear and well-motivated?
- Are assumptions explicit and reasonable?
- Is the scope achievable with available resources and constraints?
- Are there early technical risks or blockers not addressed?
- Does the initiative overlap or conflict with existing system capabilities?

### sdlc_10 (Requirements) -- Completeness & Testability Critique

**Input:** REQ_FILE + INIT_FILE

Focus areas:
- Is every requirement unambiguous and testable?
- Are acceptance criteria measurable (not vague)?
- Are edge cases and negative scenarios covered?
- Do non-functional requirements have concrete thresholds?
- Are there contradictions between requirements?
- Does the requirement set fully address the initiative scope?

### sdlc_20 (Planning) -- Architecture & Design Soundness Critique

**Input:** PLAN_FILE + REQ_FILE

Focus areas:
- Do referenced modules, components, and APIs actually exist in the codebase?
- Are the chosen design patterns appropriate for the problem?
- Is the component decomposition clean with clear boundaries?
- Are performance and scalability claims grounded in reality?
- Does the plan account for existing codebase conventions?
- Are there simpler alternatives that were overlooked?

### sdlc_30 (Backlog) -- Decomposition & Dependency Critique

**Input:** BACKLOG_FILE + PLAN_FILE

Focus areas:
- Are work items properly scoped (not too large, not too small)?
- Are boundaries between work items clear (no overlap)?
- Are dependencies correctly identified and sequenced?
- Are acceptance criteria for each item independently verifiable?
- Does the decomposition cover the full plan scope (no gaps)?
- Are parallel execution opportunities correctly identified?

### sdlc_40 (Task) -- Test Scope & Technical Feasibility Critique

**Input:** TASK_FILE + BACKLOG_FILE

Focus areas:
- **Test Scope Sufficiency** -- Does the test scope cover all acceptance
  criteria? Are edge cases included? Are test cases specific enough to
  be automated?
- **Technical Feasibility** -- Run code checks: import referenced modules,
  verify APIs exist with correct signatures.
- Are file paths and line number references accurate against the current
  codebase?
- Is the technical approach implementable as described?
- Are scope boundaries (in/out) correctly drawn?
- Do constraints (TC-*) actually hold when verified against the code?

**Generate prompt change:** Add "Test Scope" as a required section in the
TASK document, defining what must be tested, test cases, expected outcomes,
and pass/fail criteria.

### sdlc_50 (Implementation) -- Test Implementation & Code Precision Critique

**Input:** IMPL_FILE + TASK_FILE

Focus areas:
- **Test Implementation Correctness** -- Do the tests actually cover the
  test scope defined in TASK? Are tests correctly targeting the acceptance
  criteria? Is the test code syntactically correct?
- **Code Change Precision** -- Verify against actual code: read the files
  to be modified, confirm change locations exist.
- Are all code changes complete (no missing steps)?
- Are variable names consistent with existing codebase conventions?
- Are there side effects or interactions with existing code not addressed?
- Are deprecated APIs or patterns flagged?
- Run import and syntax checks on referenced modules.

**Generate prompt changes:**
- Add "Test Implementation" as a required section in the IMPL document,
  containing actual test code that implements the test scope from the TASK.
- Update Forbidden Content to exempt test code: change "Actual code
  implementation or execution results" to "Actual feature implementation
  code or execution results (test code is permitted and required)".
- The distinction: implementation code (the feature) is still forbidden
  (that is sdlc_60's job), but test code (verification of the feature)
  is now required in sdlc_50.

### sdlc_60 (Execution) -- Code Implementation & Test Results Critique

**Input:** EXEC_FILE + IMPL_FILE

sdlc_60 has three responsibilities:
1. **Implement the code** -- Make the actual code changes specified in
   the IMPL document.
2. **Run the tests** -- Execute the test code from sdlc_50.
3. **Record results** -- Document pass/fail with actual output.

Focus areas:
- **Code Implementation Correctness** -- Do the actual code changes match
  what the IMPL specified? Are all changes complete? Are APIs used
  correctly (verify against installed library version)?
- **Runtime Verification** -- Actually run the code. Execute modified
  modules, check for runtime errors.
- **Test Execution** -- Run the test suite. Verify all tests from sdlc_50
  actually executed.
- **Results Accuracy** -- Are test results recorded accurately (not
  fabricated)? Do results match expectations from TASK test scope?
- Are there unexplained failures?
- Run the full test suite to check for regressions.

**Generate prompt changes:**
- Add "Test Execution Results" as a required section in the EXEC document,
  containing actual test output and pass/fail results.
- Add "Code Changes Made" as a required section, listing all files modified
  with a summary of changes per file.

### sdlc_70 (Validation) -- Coverage & Evidence Critique

**Input:** VAL_FILE + EXEC_FILE + TASK_FILE

Focus areas:
- Is every acceptance criteria verified with actual evidence (not just
  "PASS" claims)?
- Are all test cases from the TASK test scope covered in the validation?
- Are validation methods appropriate for what is being verified?
- Are edge cases and boundary conditions tested?
- Is the validation reproducible (someone else could run the same checks)?
- Are there gaps between task requirements and validation coverage?

### sdlc_80 (Review) -- Finding Quality & Knowledge Value Critique

**Input:** REV_FILE + MEM_FILE + CLOSE_FILE + VAL_FILE

Focus areas:
- Are review findings specific and evidence-based (not generic)?
- Is the approval or rejection decision justified by the evidence?
- Are memory items genuinely reusable (not just restating what is in
  the code)?
- Does the memory capture include test quality insights and lessons
  learned?
- Is the closure assessment honest about remaining risks and limitations?
- Are lessons learned actionable for future initiatives?

## Implementation Plan

### Per-Workflow File Changes

For each of the 9 SDLC workflows:

1. **workflow.toml** -- Add `technical_critique` step definition:
   - Change generate step `onsuccess` from `review_*` to `technical_critique`
   - Add new `technical_critique` step with `onsuccess = "review_*"`
   - Add `on_reject_refine` routing back to generate step
   - Renumber existing steps (review becomes step 3, refine becomes step 4)

2. **prompts/02_technical_critique.txt** -- New stage-specific critique
   prompt with focus areas from the table above.

3. **Rename existing prompts:**
   - `02_review_*.txt` -> `03_review_*.txt`
   - `03_refine_*.txt` -> `04_refine_*.txt`

4. **context_extensions.py** -- Register `CRITIQUE_FILE_SUGGESTED` artifact
   key and path in `register_artifact_keys()`.

5. **Generate prompt updates** (sdlc_40, sdlc_50, sdlc_60 only):
   - sdlc_40: Add "Test Scope" required section
   - sdlc_50: Add "Test Implementation" required section
   - sdlc_60: Add "Test Execution Results" required section

### Artifact Key

Each workflow registers `CRITIQUE_FILE_SUGGESTED` in its
context_extensions.py:
- Artifact key: `CRITIQUE_FILE_SUGGESTED`
- Path pattern: `docs/repo/agent_runner/sdlc/delivery/80_reviews/{slug}-CRITIQUE-{stage}-{type}.md`

### Critique Document Structure

Each critique document follows this structure:

```
YAML Frontmatter:
  template_id: "SYS-03-CR"
  version: "1.0.0"
  doc_type: "review_artifact"
  lifecycle_status: "draft"
  ...

# Critique Decision
APPROVED or REJECTED

# Critique Summary
Brief overview of findings.

# Technical Findings
Stage-specific findings (API correctness, design quality, test coverage,
runtime verification, etc.)

# Design Quality Assessment
Is this the right approach? Are there better alternatives?

# Recommendations
Specific actions to address findings (if REJECTED).
```

## Workflow Inventory

| Workflow | workflow.toml | Prompts | context_extensions.py |
|---|---|---|---|
| sdlc_00_init_doc_v1 | Add critique step | New 02, rename 03/04 | Register key |
| sdlc_10_requirement_v1 | Add critique step | New 02, rename 03/04 | Register key |
| sdlc_20_planning_v1 | Add critique step | New 02, rename 03/04 | Register key |
| sdlc_30_backlog_v1 | Add critique step | New 02, rename 03/04 | Register key |
| sdlc_40_task_v1 | Add critique step | New 02, rename 03/04 + generate update | Register key |
| sdlc_50_implementation_v1 | Add critique step | New 02, rename 03/04 + generate update | Register key |
| sdlc_60_execution_v1 | Add critique step | New 02, rename 03/04 + generate update | Register key |
| sdlc_70_validation_v1 | Add critique step | New 02, rename 03/04 | Register key |
| sdlc_80_review_v1 | Add critique step | New 02, rename 03/04 | Register key |

## Verification

1. Run unit tests: `.venv\Scripts\python -m pytest tests/unit/ -x -q`
2. Verify each workflow.toml parses correctly via workflow_bundle_validator
3. Run sdlc_50 end-to-end to confirm the new step routes correctly
4. Verify the critique prompt produces a CRITIQUE_FILE_SUGGESTED artifact
5. Verify rejection routing loops back to generate step
