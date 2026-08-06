---
doc_type: "prompts_index"
lifecycle_status: "draft"
effective_version: "WFBUILD-u0z31rdx"
workflow_name: "codebase_to_meta_v1"
workflow_label: "Codebase to Meta Content v1"
---

# Prompts Index: Codebase to Meta Content v1

## Prompt Files

| # | File | Step | Type | Role Policy |
|---|------|------|------|-------------|
| 1 | prompts/02_generate_meta.txt | generate_meta | prompt | architect_standard |
| 2 | prompts/03_review_meta.txt | review_meta | prompt | reviewer_standard |
| 3 | prompts/04_refine_meta.txt | refine_meta | prompt | architect_standard |

## Prompt Summary

### 02_generate_meta.txt

**Objective:** Generate audience-specific Rich Markdown meta content files from the codebase documentation.

**Inputs:** AUDIENCE_INDEX, CODEBASE_MANIFEST, CODEBASE_CURRENT_ROOT, GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT

**Outputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX

**Key Instructions:**
- Parse AUDIENCE_INDEX to discover all audience definitions
- Read codebase documentation guided by each audience's focus_areas
- Apply tone, exclude list, and section_structure per audience definition
- Generate self-contained meta content with 6 required YAML frontmatter fields
- Produce META_INDEX JSON mapping audiences to generated files
- Include Self-Validation section with 7 compliance checks

---

### 03_review_meta.txt

**Objective:** Review all generated meta content files for completeness, accuracy, audience-appropriateness, and structural compliance.

**Inputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX, AUDIENCE_INDEX, GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT

**Outputs:** REVIEW_FILE_SUGGESTED

**Key Instructions:**
- Evaluate each file against 8 review criteria (frontmatter, sections, tone, focus, exclude, accuracy, encoding, self-containment)
- Produce consolidated review with per-audience sections
- Include specific PASS/FAIL results for each check
- Decision: APPROVED or REJECTED with actionable feedback
- This step has requires_human_approval_after = true

---

### 04_refine_meta.txt

**Objective:** Refine generated meta content files based on review feedback.

**Inputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX, AUDIENCE_INDEX, REVIEW_FILE_SUGGESTED

**Outputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX (updated in place)

**Key Instructions:**
- Address all critical and major findings from review
- Modify files in place using edit_mode = "in_place"
- Only modify files that received specific feedback
- Verify technical accuracy against actual codebase
- Include Self-Validation section with 8 compliance checks
- Routes back to review_meta after refinement (loop)

## Action Steps (No Prompts)

The following steps are action-driven and do not have prompt files:

| Step | Action | Source |
|------|--------|--------|
| scan_audiences | scan_audiences | actions.py |
| validate_meta | validate_meta | actions.py |
| create_meta_backup | create_meta_backup | actions.py |
| publish_meta | publish_meta | actions.py |
| stepCompletion | step_completion | sdlc_shared_actions.py |

## Placeholder Reference

All prompt files use these artifact key placeholders (resolved to absolute paths at runtime):

| Placeholder | Description |
|-------------|-------------|
| {AUDIENCE_INDEX} | JSON index of discovered audience definitions |
| {CODEBASE_MANIFEST} | Codebase manifest inventory file |
| {CODEBASE_CURRENT_ROOT} | Root of codebase documentation tree |
| {META_DEV_FILE} | Developer meta content file path |
| {META_ARCH_FILE} | Architect meta content file path |
| {META_EXEC_FILE} | Executive meta content file path |
| {META_INDEX} | JSON index of all generated meta files |
| {REVIEW_FILE_SUGGESTED} | Consolidated review document path |
| {GOVERNANCE_RUNTIME_ROOT} | Layer 1 governance runtime root |
| {PLATFORM_RUNTIME_ROOT} | Layer 2 platform constitution runtime root |
