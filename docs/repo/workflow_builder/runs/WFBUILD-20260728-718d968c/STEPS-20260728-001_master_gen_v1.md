---
doc_type: "step_architecture"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-718d968c"
workflow_name: "product_master_gen_v1"
spec_source: "REQUIREMENTS-20260728-001_master_gen_v1.md"
artifact_contract: "ARTIFACTS-20260728-001_master_gen_v1.md"
---

# Step Architecture: Product Master Generator

## Step Sequence

| # | Step Name | Type | Role Policy | Routing Target |
|---|-----------|------|-------------|----------------|
| 1 | scan_product_inputs | action | N/A | generate_product_info |
| 2 | generate_product_info | prompt | architect_standard | generate_target_audience |
| 3 | generate_target_audience | prompt | architect_standard | generate_product_benefits |
| 4 | generate_product_benefits | prompt | architect_standard | generate_marketing_assets |
| 5 | generate_marketing_assets | prompt | architect_standard | generate_additional_sections |
| 6 | generate_additional_sections | prompt | architect_standard | assemble_product_master |
| 7 | assemble_product_master | prompt | architect_standard | review_product_master |
| 8 | review_product_master | prompt | reviewer_standard | stepCompletion (on success) / refine_product_master (on reject) |
| 9 | refine_product_master | prompt | architect_standard | review_product_master (via loop_returns_to) |
| 10 | stepCompletion | action | N/A | terminal |

Total: 10 steps (2 action, 7 prompt-generation, 1 prompt-review/refine pair).

Design decisions applied:
- DD-001: Five separate prompt-driven section generation steps (one per
  section artifact) for modularity and independent extensibility.
- DD-002: Review/refine loop targets the assembled PRODUCT_MASTER_FILE
  only, not individual sections.
- DD-003: Role policies follow the standard SDLC Pattern 2:
  architect_standard for generation/refinement, reviewer_standard for
  review.
- DD-004: All sections regenerated on every run; merge handled at
  assembly step when PRODUCT_MASTER_FILE is provided as input.
- DD-005: Additional sections proposed and generated in a single step.

## Step Details

### 1. scan_product_inputs

- Type: action
- Action function: scan_product_inputs
- Prompt file: N/A (action-driven)
- Role policy: N/A
- Artifact bindings:
  - required_inputs: [PRODUCT_SOURCE_DIR]
  - produces: [SCAN_REPORT_FILE]
  - result_meta_key: SCAN_REPORT_FILE
- Routing:
  - onsuccess: generate_product_info
- Notes: Recursively scans the PRODUCT_SOURCE_DIR directory, classifies
  each file by source type per the classification rules in the
  requirements, and writes a structured markdown scan report. Returns
  APPROVED with scan report path on success, or REJECTED if the
  directory is empty or inaccessible. This is the only action step
  besides stepCompletion.

### 2. generate_product_info

- Type: prompt
- Prompt file: prompts/02_generate_product_info.txt
- Role policy: architect_standard
- Artifact bindings:
  - required_inputs: [SCAN_REPORT_FILE]
  - produces: [PRODUCT_INFO_FILE]
  - result_meta_key: PRODUCT_INFO_FILE
- Routing:
  - onsuccess: generate_target_audience
- Notes: Generates the Product Information section covering product
  name, manufacturer, brand, model, SKU, UPC/EAN, dimensions, weight,
  materials, technical specifications, package contents, and
  certifications. Reads the scan report and source files independently.

### 3. generate_target_audience

- Type: prompt
- Prompt file: prompts/03_generate_target_audience.txt
- Role policy: architect_standard
- Artifact bindings:
  - required_inputs: [SCAN_REPORT_FILE]
  - produces: [TARGET_AUDIENCE_FILE]
  - result_meta_key: TARGET_AUDIENCE_FILE
- Routing:
  - onsuccess: generate_product_benefits
- Notes: Generates the Target Audience section covering primary
  demographic profile, buyer personas (2-3 archetypes), use cases,
  market segment, and psychographic indicators. Reads the scan report
  and source files independently of other section steps.

### 4. generate_product_benefits

- Type: prompt
- Prompt file: prompts/04_generate_product_benefits.txt
- Role policy: architect_standard
- Artifact bindings:
  - required_inputs: [SCAN_REPORT_FILE]
  - produces: [PRODUCT_BENEFITS_FILE]
  - result_meta_key: PRODUCT_BENEFITS_FILE
- Routing:
  - onsuccess: generate_marketing_assets
- Notes: Generates the Benefits/USP section covering core value
  proposition, key benefits (functional, emotional, social), problems
  solved, competitive differentiators, and source-traced supporting
  evidence. Reads the scan report and source files independently.

### 5. generate_marketing_assets

- Type: prompt
- Prompt file: prompts/05_generate_marketing_assets.txt
- Role policy: architect_standard
- Artifact bindings:
  - required_inputs: [SCAN_REPORT_FILE]
  - produces: [MARKETING_ASSETS_FILE]
  - result_meta_key: MARKETING_ASSETS_FILE
- Routing:
  - onsuccess: generate_additional_sections
- Notes: Generates the Marketing Assets/Trending section covering
  existing brand assets found in inputs, visual asset inventory,
  trending topics, social media hooks, campaign theme suggestions,
  and influencer/partnership angles. Reads the scan report and source
  files independently.

### 6. generate_additional_sections

- Type: prompt
- Prompt file: prompts/06_generate_additional_sections.txt
- Role policy: architect_standard
- Artifact bindings:
  - required_inputs: [SCAN_REPORT_FILE]
  - produces: [ADDITIONAL_SECTIONS_FILE]
  - result_meta_key: ADDITIONAL_SECTIONS_FILE
- Routing:
  - onsuccess: assemble_product_master
- Notes: Analyzes the product and sources to identify additional
  knowledge sections beyond the four standard ones. Proposes and
  generates full content for each additional section. If no additional
  sections are warranted, produces a stub artifact stating so. Reads
  the scan report and source files independently.

### 7. assemble_product_master

- Type: prompt
- Prompt file: prompts/07_assemble_product_master.txt
- Role policy: architect_standard
- Artifact bindings:
  - required_inputs: [PRODUCT_INFO_FILE, TARGET_AUDIENCE_FILE, PRODUCT_BENEFITS_FILE, MARKETING_ASSETS_FILE, ADDITIONAL_SECTIONS_FILE]
  - optional_inputs: [PRODUCT_MASTER_FILE]
  - produces: [PRODUCT_MASTER_FILE]
  - result_meta_key: PRODUCT_MASTER_FILE
- Routing:
  - onsuccess: review_product_master
- Notes: Assembles all section artifacts into the canonical Product
  Master document. This is the only step where all section artifacts
  converge. Handles deduplication and cross-references. Adds YAML
  frontmatter (product_name, version, source_count,
  completeness_rating) and a table of contents. When PRODUCT_MASTER_FILE
  is provided as optional input (incremental update mode), merges new
  section content with existing content and adds a Changelog section.

### 8. review_product_master

- Type: prompt
- Prompt file: prompts/08_review_product_master.txt
- Role policy: reviewer_standard
- Artifact bindings:
  - required_inputs: [PRODUCT_MASTER_FILE]
  - produces: [REVIEW_FILE_SUGGESTED]
  - result_meta_key: REVIEW_FILE_SUGGESTED
- Routing:
  - onsuccess: stepCompletion
  - on_reject_refine:
    - step: refine_product_master
    - artifact: PRODUCT_MASTER_FILE
    - max_iterations: 2
    - exhausted_failure_code: REFINE_EXHAUSTED
    - exhausted_failure_class: HUMAN_RETRY_REQUIRED
  - requires_human_approval_after: true
- Notes: Reviews the assembled Product Master for factual accuracy,
  completeness, source attribution, and structural coherence. Produces
  a review critique document. If approved, workflow proceeds to
  completion. If rejected, triggers the refine step. Human gate is
  enabled because the Product Master is the primary deliverable.

### 9. refine_product_master

- Type: prompt
- Prompt file: prompts/09_refine_product_master.txt
- Role policy: architect_standard
- Artifact bindings:
  - required_inputs: [PRODUCT_MASTER_FILE, REVIEW_FILE_SUGGESTED]
  - produces: [PRODUCT_MASTER_FILE]
  - target_artifact: PRODUCT_MASTER_FILE
  - edit_mode: in_place
  - result_meta_key: PRODUCT_MASTER_FILE
- Routing:
  - loop_returns_to: review_product_master
- Notes: Refines the Product Master based on review feedback. Reads
  both the current PRODUCT_MASTER_FILE and the REVIEW_FILE_SUGGESTED
  critique. Applies corrections in place. After refinement, control
  returns to review_product_master for re-evaluation.

### 10. stepCompletion

- Type: action
- Action function: step_completion
- Prompt file: N/A (action-driven)
- Role policy: N/A
- Artifact bindings:
  - required_inputs: []
  - produces: []
  - result_meta_key: N/A
- Routing:
  - Terminal step (no onsuccess)
- Notes: Standard terminal step. Marks the workflow job as COMPLETED.

## Routing Diagram

```
                          +-----------------------+
                          | scan_product_inputs    |
                          | (action)               |
                          +-----------+-----------+
                                      |
                                      | onsuccess
                                      v
                          +-----------------------+
                          | generate_product_info  |
                          | (prompt)               |
                          +-----------+-----------+
                                      |
                                      | onsuccess
                                      v
                          +---------------------------+
                          | generate_target_audience   |
                          | (prompt)                   |
                          +-----------+---------------+
                                      |
                                      | onsuccess
                                      v
                          +-----------------------------+
                          | generate_product_benefits    |
                          | (prompt)                     |
                          +-----------+-----------------+
                                      |
                                      | onsuccess
                                      v
                          +-----------------------------+
                          | generate_marketing_assets    |
                          | (prompt)                     |
                          +-----------+-----------------+
                                      |
                                      | onsuccess
                                      v
                          +-------------------------------+
                          | generate_additional_sections   |
                          | (prompt)                       |
                          +-----------+-------------------+
                                      |
                                      | onsuccess
                                      v
                          +---------------------------+
                          | assemble_product_master    |
                          | (prompt)                   |
                          +-----------+---------------+
                                      |
                                      | onsuccess
                                      v
                     +----------------------------------+
                     | review_product_master             |
                     | (prompt, requires_human_approval) |
                     +---+--------------------------+---+
                         |                          |
          onsuccess      |                          | on_reject_refine
                         v                          v
            +-----------------+        +---------------------------+
            | stepCompletion   |        | refine_product_master      |
            | (action/terminal)|        | (prompt, in_place edit)    |
            +-----------------+        +-------------+-------------+
                                                     |
                                                     | loop_returns_to
                                                     |
                                                     v
                                         (back to review_product_master)
```

Review/Refine Loop Detail:

```
    review_product_master
            |
            |--- onsuccess --------> stepCompletion
            |
            |--- on_reject_refine -> refine_product_master
                                          |
                                          | loop_returns_to
                                          |
                                          +--> review_product_master
```

Maximum refine iterations: 2 (controlled by on_reject_refine.max_iterations).
After exhaustion: REFINE_EXHAUSTED / HUMAN_RETRY_REQUIRED.

## Terminal Steps

| Step Name | Type | Action | Notes |
|-----------|------|--------|-------|
| stepCompletion | action | step_completion | Standard terminal step. Marks workflow as COMPLETED. |

Failure routing:
- If scan_product_inputs fails (REJECTED), the workflow fails immediately.
  No refine loop for action steps. Failure code: ACTION_FAILED.
- If review_product_master exhausts all refine iterations (max_iterations=2),
  the workflow fails with code REFINE_EXHAUSTED and class
  HUMAN_RETRY_REQUIRED.
- All prompt-driven generation steps (steps 2-7) have no individual review
  gates. If a generation step fails, the workflow halts at that step.

## Configuration Summary

| Parameter | Value |
|-----------|-------|
| init_step | scan_product_inputs |
| default_max_rejects | 3 |
| enable_notifications | true (for all prompt-driven steps) |
| requires_human_approval_after | true (on review_product_master step only) |
| on_reject_refine.max_iterations | 2 (on review_product_master) |
| on_reject_refine.exhausted_failure_code | REFINE_EXHAUSTED |
| on_reject_refine.exhausted_failure_class | HUMAN_RETRY_REQUIRED |

Step count summary:
- Action steps: 2 (scan_product_inputs, stepCompletion)
- Prompt-driven generation steps: 6 (generate_product_info,
  generate_target_audience, generate_product_benefits,
  generate_marketing_assets, generate_additional_sections,
  assemble_product_master)
- Prompt-driven review step: 1 (review_product_master)
- Prompt-driven refine step: 1 (refine_product_master)
- Total: 10 steps

Prompt file inventory:
- prompts/02_generate_product_info.txt
- prompts/03_generate_target_audience.txt
- prompts/04_generate_product_benefits.txt
- prompts/05_generate_marketing_assets.txt
- prompts/06_generate_additional_sections.txt
- prompts/07_assemble_product_master.txt
- prompts/08_review_product_master.txt
- prompts/09_refine_product_master.txt

Note: No prompts/01_ file is needed because step 1 is an action step
(scan_product_inputs), not a prompt-driven step. Prompt numbering starts
at 02 for the first prompt-driven step.
