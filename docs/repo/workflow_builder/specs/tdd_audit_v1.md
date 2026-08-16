# Workflow Specification: TDD Audit v1

> Save to `docs/repo/workflow_builder/specs/tdd_audit_v1.md`.
> The workflow builder reads this document and generates the complete
> workflow package (workflow.toml, context_extensions.py, prompts, actions.py).
>
> **Key principle:** Describe WHAT the workflow does (domain problem, inputs,
> outputs, constraints). The builder infers HOW to structure it (step sequence,
> routing, role policies, gatekeepers, self-validation).

## Overview

**Workflow name:** `tdd_audit_v1`
**Label:** TDD Audit v1
**Job prefix:** `TDDAUD`
**Description:** Semantic audit of all test code in an agent-runner-v2 enabled repo. Reads source modules and their corresponding tests, reasons about what each test is supposed to validate, and critiques whether the tests actually fulfill that objective. Produces an audit report, improvement proposal, and prioritized remediation plan.

## Purpose

Codebases accumulate tests that look correct but don't actually validate what they claim to. Functions get called without assertions. Assertions check the wrong things. Edge cases and error paths go untested. Tests pass but provide false confidence.

This workflow performs a **semantic audit** — it reads the source code, reads the test code, and reasons about whether the tests are actually doing their job. Not "does a test file exist?" but "does this test correctly validate the behavior it's supposed to?"

**Trigger:** Manual — user runs the workflow against a target repo.

**Outcome:** Three documents:
1. **Audit report** — per-module critique: what each test validates, whether it's correct, what's missing
2. **Improvement proposal** — architectural recommendations for test infrastructure and patterns
3. **Remediation plan** — prioritized, actionable list of tests to add/rewrite/fix

**Target:** Any agent-runner-v2 enabled repo (has standard `tests/unit/` and `tests/integration/` structure).

## Workflow Type

**Mixed** — Action-driven source-to-test mapping, plus prompt-driven semantic analysis and document generation.

## Input Artifacts

**No user-provided inputs.** The target repo is configured via context variable.

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `TARGET_REPO_ROOT` | Configurable (default: current workspace root) | Root of the repo to audit |
| `TEST_UNIT_DIR` | `{TARGET_REPO_ROOT}/tests/unit/` | Unit test directory |
| `TEST_INTEGRATION_DIR` | `{TARGET_REPO_ROOT}/tests/integration/` | Integration test directory |
| `SOURCE_DIRS` | `{TARGET_REPO_ROOT}/agent_runner_v2/` | Source code directories to audit |

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `TEST_CRITERIA_FILE` | `TEST_CRITERIA-{date}-{seq}_{slug}.md` | Acceptance criteria for the audit |
| `SCAN_MAP_FILE` | `SCAN_MAP-{date}-{seq}_{slug}.md` | Source-to-test module mapping |
| `AUDIT_REPORT_FILE` | `TDD_AUDIT_REPORT-{date}-{seq}_{slug}.md` | Per-module semantic test critique |
| `IMPROVEMENT_PROPOSAL_FILE` | `TDD_PROPOSAL-{date}-{seq}_{slug}.md` | Architectural recommendations |
| `REMEDIATION_PLAN_FILE` | `TDD_REMEDIATION-{date}-{seq}_{slug}.md` | Prioritized action items |
| `REVIEW_FILE_SUGGESTED` | `TDDAUD-REV-{date}-{seq}_{slug}.md` | Review of generated documents |
| `VALIDATION_REPORT_FILE` | `TDDAUD-VALIDATION-{date}-{seq}_{slug}.md` | Structural validation report |

**Granularity rule:** One artifact key per logical file.

## Quality Requirements

### Audit Report — Per Module Critique

For each source module that has tests, the report must:

- **State the module's purpose** — what does this module do? What are its key functions/classes?
- **State each test's objective** — what is this test supposed to validate?
- **Verdict: correct / incorrect / incomplete** — does the test actually validate its stated objective?
- **Specific findings:**
  - Test calls function but doesn't assert the result → false confidence
  - Test asserts return value but not side effects → partial validation
  - Test only covers happy path → missing error/edge cases
  - Test mocks everything → testing the mock, not the code
  - Test uses real filesystem when it should mock → isolation violation
  - Test asserts too broadly (e.g., `assert result is not None`) → weak validation
  - No test exists for a public function → coverage gap
- **Module-level verdict** — overall test adequacy rating with evidence

### Audit Report — Coverage Gaps

For each source module with NO tests:

- List all public functions/classes
- Identify which are most critical (called by other modules, handle user input, etc.)
- Recommend test priority (critical / high / medium / low)

### Improvement Proposal Must Include

- Test infrastructure gaps (missing fixtures, shared utilities, mock helpers)
- Common anti-patterns found across the codebase (not just per-module)
- Naming convention violations
- Recommendations for test organization
- TDD philosophy alignment recommendations

### Remediation Plan Must Include

- Prioritized list (critical → high → medium → low)
- Each item: which module, what's missing/wrong, what the test should validate
- Grouped by category: new tests needed, existing tests to rewrite, tests to strengthen, infrastructure improvements

### Scanning Rules

- Source modules: all `.py` files under source dirs, excluding `__init__.py`, `__pycache__`, `bootstrap/`, `generated/`
- Test files: all `test_*.py` and `*_test.py` files under tests/
- Mapping convention: `agent_runner_v2/module/foo.py` → `tests/unit/test_foo.py` or `tests/unit/module/test_foo.py`
- The scan produces a mapping document (SCAN_MAP_FILE) that pairs each source module with its test file(s)

## Custom Actions

### Action: scan_test_mapping

**Purpose:** Walk the source directory tree and test directory tree. Build a mapping of source modules to test files. For each source module, record:
- Module path and public API (functions, classes)
- Whether a corresponding test file exists
- Test file path if found
- Basic metrics: test function count, file size

Also identify:
- Source modules with no test file at all
- Test files with no corresponding source module (orphan tests)

Scan both `tests/unit/` and `tests/integration/`. Respect `.codebase-scan-ignore` patterns if present.

**Returns:** APPROVED with scan mapping as structured data. REJECTED only if source directory doesn't exist.

## Builder Instructions

**Domain phases:**

1. **TDD loop** — Generate test criteria for the audit itself (what makes a good audit), review, refine
2. **Scan** — Action-driven: discover all source modules and test files, build mapping
3. **Semantic audit** — LLM reads each source+test pair, reasons about test adequacy, produces per-module critique. This is the core analysis step — it needs both the source code and the test code to reason about whether tests validate correctly.
4. **Review audit report** — Validate completeness and accuracy of findings
5. **Generate improvement proposal** — LLM synthesizes cross-cutting patterns from audit findings into architectural recommendations
6. **Generate remediation plan** — LLM produces prioritized, actionable list from audit findings
7. **Validate documents** — Structural validation of all three outputs
8. **Final review** — Human review of all documents

**Domain constraints:**

- The semantic audit step must read BOTH the source module and its test file — it cannot critique tests in isolation
- Each critique must cite specific evidence (line numbers, function names, assertion content)
- The audit must distinguish between unit tests (should be isolated, pure logic) and integration tests (may use real dependencies)
- Modules with no tests are flagged as coverage gaps, not quality failures
- The audit should handle large codebases by grouping modules logically (by package/directory)

**Reference patterns:**

- `sdlc_00_codebase_v1` — existing codebase scanning workflow (module discovery patterns)
- `sdlc_80_review_v1` — review/critique workflow pattern
- Unit testing philosophy: pure logic isolation, no filesystem deps, proper mocking, comprehensive coverage of imports/behavior/exceptions/edge cases

## Notes

- **Semantic, not syntactic** — This workflow reasons about test quality, not just assertion counts. A test with 10 assertions could still be wrong if it asserts the wrong things. A test with 1 assertion could be perfect if it checks the critical behavior.
- **Source+test pairs** — The core analysis unit is a (source module, test file) pair. The LLM reads both and reasons about alignment.
- **Multi-repo support** — The `TARGET_REPO_ROOT` context variable makes it repo-agnostic.
- **Complementary to codebase scan** — `sdlc_00_codebase_v1` generates module documentation; this workflow audits test quality. They share scanning patterns but produce different outputs.
- **Not a coverage tool** — This is not about pytest-cov line coverage percentages. It's about whether tests validate the right behavior. A module can have 100% line coverage but still have tests that don't verify correctness.
