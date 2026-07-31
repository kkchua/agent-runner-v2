---
doc_type: "workflow_review"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-718d968c"
test_criteria_ref: "docs/repo/workflow_builder/runs/WFBUILD-20260728-718d968c/TEST_CRITERIA-20260728-001_master_gen_v1.md"
spec_ref: "docs/repo/workflow_builder/specs/product_master_gen_v1.md"
review_date: "2026-07-28"
reviewer: "automated_gatekeeper"
---

# Test Criteria Review: Product Master Generator v1

## Summary

The test criteria document for the Product Master Generator workflow is comprehensive, well-structured, and fully aligned with the workflow specification. All required sections are present and correctly ordered. The document provides 113 specific, verifiable criteria across seven categories (analyze_spec, generate_package, validate_bundle, review_package, prompt quality, and audit criteria), each with unique identifiers enabling traceability. The criteria accurately capture the spec's intent, correctly identify the mixed workflow architecture, comprehensively cover all spec requirements, and include appropriate negative criteria to prevent scope creep. No issues were found.

## Findings

### 1. Spec Objective Summary

**Status:** APPROVED

**Evidence:**
- Lines 15-22 accurately describe the INPUT/OUTPUT transformation matching spec lines 14-29
- Line 30 correctly identifies the workflow as "mixed architecture" matching spec line 33-34
- The summary captures the end-to-end flow: scan inputs -> generate sections -> assemble -> review -> refine
- The description matches the spec's stated purpose of solving the "consolidation problem"

### 2. Criteria for analyze_spec Step

**Status:** APPROVED

**Evidence:**
- REQ-001 through REQ-012 cover all spec requirements including:
  - Workflow type classification (mixed) - matches spec line 33-34
  - Input artifacts (PRODUCT_SOURCE_DIR required, PRODUCT_MASTER_FILE optional) - matches spec lines 40-41
  - All 8 output artifact keys - matches spec lines 62-70
  - Custom action description (scan_product_inputs with file classification rules) - matches spec lines 143-169
  - All 5 standard sections with content domains - matches spec lines 80-130
  - Independence constraint - matches spec line 212-213
  - Incremental update behavior - matches spec line 216-217
  - Slug extraction - matches spec line 182-183
  - URL handling - matches spec line 218-219

- REQ-013 through REQ-016 correctly classify workflow type and step types
- REQ-017 through REQ-020 correctly identify input/output artifact paths and context variables

### 3. Criteria for generate_package Step

**Status:** APPROVED

**Evidence:**
- PKG-001 through PKG-005 correctly specify required files:
  - workflow.toml with [workflow] metadata and [[step]] definitions
  - context_extensions.py with WorkflowExtensions class
  - actions.py with scan_product_inputs action
  - prompts/ directory with .txt files for each prompt-driven step
  - Bare {ARTIFACT_KEY} placeholders in prompts

- PKG-006 through PKG-010 specify negative criteria preventing:
  - bundle_governance.toml (spec line 186 unchecked)
  - install.py (spec line 181-183 explicitly unchecked)
  - Prompts for action-driven steps
  - Hardcoded absolute paths

- PKG-011 through PKG-017 specify action code requirements including:
  - Reading PRODUCT_SOURCE_DIR from context variables
  - Recursive directory scanning
  - Complete file type classification matching spec lines 156-169 (all 10 patterns)
  - Proper ActionResult return types
  - Error handling for missing/empty/inaccessible directories

- PKG-018 through PKG-028 specify section generation prompt requirements:
  - Each prompt must read scan report and relevant source files
  - Each prompt must handle missing information as knowledge gaps
  - Each prompt must handle conflicting information with source attribution
  - Each prompt must write output to artifact paths (not meta.json result field)

- PKG-029 through PKG-035 specify assembly prompt requirements:
  - Read all section artifacts
  - Produce YAML frontmatter with required fields
  - Generate table of contents
  - Arrange sections logically with deduplication
  - Include source attribution
  - Conditional Changelog for incremental updates

- PKG-036 through PKG-038 specify review/refine prompt requirements
- PKG-039 through PKG-046 specify context extensions requirements
- PKG-047 through PKG-054 specify workflow.toml routing requirements
- PKG-055 through PKG-062 specify additional negative criteria

### 4. Criteria for validate_bundle Step

**Status:** APPROVED

**Evidence:**
- VAL-001 through VAL-011 provide structural checks:
  - TOML validity
  - Workflow metadata completeness
  - Step naming and prompt/action field presence
  - Init step correctness
  - Routing reference validity

- VAL-012 through VAL-015 provide artifact registration checks:
  - All artifact keys in workflow.toml have context_extensions.py mappings
  - Required inputs are produced by prior steps or are declared inputs
  - Case-sensitive key matching

- VAL-016 through VAL-021 provide semantic checks:
  - Action function contains actual scanning logic (not stub)
  - Action contains complete file classification table
  - Prompts contain substantive instructions
  - Context extensions properly inherits WorkflowExtensions

- VAL-022 through VAL-025 provide file completeness checks:
  - Required files present
  - No unauthorized files
  - All referenced prompts exist
  - No orphan prompts

### 5. Criteria for review_package Step

**Status:** APPROVED

**Evidence:**
- REV-001 through REV-006 verify spec fulfillment:
  - Complete end-to-end flow
  - All 8 output artifacts
  - All section content domains
  - Product Master assembly requirements
  - Incremental update support
  - Downstream independence

- REV-007 through REV-012 verify step-by-step execution:
  - Scan step produces scan report
  - Section steps read scan report and produce artifacts independently
  - Assembly step reads all sections
  - Review step evaluates Product Master
  - Refine step applies fixes in-place
  - URL content fetching support

- REV-013 through REV-018 verify data flow:
  - Scan report is required input for all section steps
  - All section artifacts are required inputs for assembly
  - Product Master is required input for review
  - Both Product Master and Review are required inputs for refine

- REV-019 through REV-023 verify no hallucinations:
  - No campaign/media/marketing deployment steps
  - No hardcoded product data
  - No extra inputs beyond spec
  - No API keys or authentication
  - No invented standard sections

### 6. Quality Checks

**Status:** APPROVED

**Evidence:**

| Field | Expected Value | Actual Value | Status |
|---|---|---|---|
| doc_type | "test_criteria" | "test_criteria" | PASS |
| lifecycle_status | "draft" | "draft" | PASS |
| effective_version | "WFBUILD-20260728-718d968c" | "WFBUILD-20260728-718d968c" | PASS |
| spec_ref | Path to spec | "docs/repo/workflow_builder/specs/product_master_gen_v1.md" | PASS |
| workflow_name | "product_master_gen_v1" | "product_master_gen_v1" | PASS |
| workflow_type | "mixed" | "mixed" | PASS |

- ASCII-only content verified: Standard hyphens (-), straight quotes (' and "), no em-dashes, no curly quotes, no Unicode special characters
- All criteria are specific and verifiable with unique identifiers (REQ-xxx, PKG-xxx, VAL-xxx, REV-xxx, PQ-xxx, LOG-xxx, DAT-xxx, SEC-xxx)
- No contradictory criteria found
- All required sections present and in correct order

### 7. Prompt Quality Criteria

**Status:** APPROVED

**Evidence:**
- PQ-001 through PQ-004 specify output mechanism clarity (file-writing vs. meta.json)
- PQ-005 through PQ-010 specify ambiguity prevention
- PQ-011 through PQ-015 guard against common LLM mistakes (fabrication, silent section dropping)
- PQ-016 through PQ-023 specify completeness requirements for all prompts

### 8. Audit Criteria

**Status:** APPROVED

**Evidence:**
- LOG-001 through LOG-009 cover logic audit (error handling, retry loops, conditional branching)
- DAT-001 through DAT-010 cover data integrity audit (scan report accuracy, section completeness, source attribution, slug consistency)
- SEC-001 through SEC-003 cover security audit (URL handling, no credential exposure)

## Issues

No issues found. The test criteria document meets all review requirements.

## Verdict

APPROVED