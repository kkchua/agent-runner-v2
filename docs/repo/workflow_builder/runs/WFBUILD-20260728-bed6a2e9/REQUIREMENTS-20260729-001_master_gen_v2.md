---
doc_type: "workflow_design"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-bed6a2e9"
workflow_name: "product_master_gen_v2"
workflow_label: "Product Master Generator v2"
job_prefix: "PRDM"
spec_source: "product_master_gen_v2.md"
---

# Workflow Requirements: Product Master Generator v2

## Overview

The Product Master Generator v2 workflow consolidates product knowledge
from diverse input sources (URLs, images, PDFs, spreadsheets, marketing
materials, and user notes) into a single canonical Product Master document.
This document serves as the authoritative knowledge base for downstream
workflows such as campaign generation, media creation, and content
production. The workflow supports both first-time generation and
incremental updates with a changelog. It uses a mixed architecture:
deterministic action steps for source inventory and artifact promotion,
combined with LLM-driven prompt steps for knowledge extraction, synthesis,
quality review, and iterative refinement.

## Workflow Type

**Inferred type:** Mixed (action + prompt)

**Justification:**

The workflow contains two distinct classes of work:

1. **Deterministic operations** (action steps): Scanning a directory
   for files, categorizing them by type, and producing a structured
   inventory. This is purely mechanical and requires no LLM reasoning.
   Artifact promotion (setting status to Approved) is also a built-in
   deterministic action.

2. **LLM reasoning operations** (prompt steps): Fetching and analyzing
   web content, extracting knowledge from PDFs and images, synthesizing
   facts from multiple sources into structured sections, identifying
   knowledge gaps, resolving conflicting information, and generating
   a coherent markdown document. These tasks require judgment,
   interpretation, and language generation that only an LLM can perform.

The action steps are lightweight infrastructure (inventory + promotion).
The prompt steps carry the core intellectual work of the workflow. This
is a mixed workflow by nature, not by explicit declaration.

## Proposed Steps

### Step 1: scan_sources

- **Name:** scan_sources
- **Type:** action
- **Purpose:** Scan the PRODUCT_SOURCE_DIR directory, categorize all files
  by type (URLs, images, PDFs, data files, documents, notes), and produce
  a structured SOURCE_INVENTORY artifact that downstream steps consume.
- **Inputs:** PRODUCT_SOURCE_DIR (directory path)
- **Outputs:** SOURCE_INVENTORY (JSON manifest of categorized source files)
- **Role policy:** N/A (action step)
- **Routing:** onsuccess -> generate_master

### Step 2: generate_master

- **Name:** generate_master
- **Type:** prompt
- **Purpose:** Read all source materials listed in the SOURCE_INVENTORY,
  fetch URLs, extract knowledge from PDFs/images/data files, and generate
  a comprehensive Product Master document. If an existing PRODUCT_MASTER_FILE
  is provided, merge new knowledge and append a Changelog section. Includes
  Self-Validation: the LLM checks completeness, consistency, source
  attribution, and gap identification before reporting APPROVED.
- **Inputs:** SOURCE_INVENTORY, PRODUCT_MASTER_FILE (optional)
- **Outputs:** PRODUCT_MASTER_FILE
- **Role policy:** architect_standard
- **Routing:** onsuccess -> review_master
- **Self-reject:** on_reject_refine -> generate_master (max_iterations: 1)

### Step 3: review_master

- **Name:** review_master
- **Type:** prompt
- **Purpose:** Perform a consolidated quality review of the generated
  Product Master. Evaluate factual accuracy, completeness, source
  attribution, knowledge gap identification, conflict handling, structural
  organization, and downstream agnosticism. Produce a structured review
  with findings and recommendations.
- **Inputs:** PRODUCT_MASTER_FILE, SOURCE_INVENTORY
- **Outputs:** REVIEW_FILE_SUGGESTED
- **Role policy:** reviewer_standard
- **Routing:** onsuccess -> promote_master; on_reject_refine -> refine_master
- **Human gate:** requires_human_approval_after = true

### Step 4: refine_master

- **Name:** refine_master
- **Type:** prompt
- **Purpose:** Revise the Product Master in-place based on the review
  feedback. Address identified gaps, resolve conflicts, improve source
  attribution, and fix structural issues.
- **Inputs:** PRODUCT_MASTER_FILE, REVIEW_FILE_SUGGESTED, SOURCE_INVENTORY
- **Outputs:** PRODUCT_MASTER_FILE (in-place edit)
- **Role policy:** refine_standard
- **Routing:** loop_returns_to -> review_master
- **Edit mode:** in_place
- **Target artifact:** PRODUCT_MASTER_FILE

### Step 5: promote_master

- **Name:** promote_master
- **Type:** action
- **Purpose:** Promote the PRODUCT_MASTER_FILE artifact status to Approved,
  marking it as the canonical output of this workflow run.
- **Inputs:** PRODUCT_MASTER_FILE
- **Outputs:** PRODUCT_MASTER_FILE (status: Approved)
- **Role policy:** N/A (built-in promote_artifact action)
- **Routing:** onsuccess -> stepCompletion
- **Promotes:** PRODUCT_MASTER_FILE

### Step 6: stepCompletion

- **Name:** stepCompletion
- **Type:** action
- **Purpose:** Terminal step. Marks the workflow job as COMPLETED.
- **Inputs:** None
- **Outputs:** None
- **Role policy:** N/A (built-in step_completion action)

## Custom Actions

| action_name | purpose | inputs | outputs | logic_description |
|---|---|---|---|---|
| scan_sources | Scan PRODUCT_SOURCE_DIR and build a structured inventory of source files categorized by type | PRODUCT_SOURCE_DIR (directory path from context) | SOURCE_INVENTORY (JSON file with categorized file listing) | Walk the source directory recursively. Categorize files by extension into groups: urls (.txt files containing URLs), images (.png, .jpg, .jpeg, .webp), pdfs (.pdf), data (.csv, .xlsx), documents (.docx, .md, .txt), notes (.md, .txt). For each file record: relative path, file size, category, and detected type. For URL files, read contents and list each URL as a sub-entry. Produce a JSON file with summary counts and per-category file lists. Return APPROVED with the inventory path, or REJECTED if the directory does not exist or contains no recognized files. |

## Input Artifacts

| artifact_key | description | required_or_optional |
|---|---|---|
| PRODUCT_SOURCE_DIR | Path to directory containing product source materials (URLs, images, PDFs, data files, marketing materials, notes). All file types within are optional; workflow uses whatever is available. | Required |
| PRODUCT_MASTER_FILE | Existing Product Master document for incremental updates. If provided, the workflow merges new knowledge and adds a Changelog section. If not provided, generates from scratch. | Optional |
| WORKFLOW_SPEC | The user-provided workflow specification document. Referenced by review steps for context on expected scope and constraints. | Required |

## Output Artifacts

| artifact_key | description | required_or_optional |
|---|---|---|
| SOURCE_INVENTORY | JSON manifest produced by scan_sources. Contains categorized listing of all source files found in PRODUCT_SOURCE_DIR with file counts, paths, sizes, and extracted URLs. Consumed by generate_master and review_master. | Required |
| PRODUCT_MASTER_FILE | The canonical Product Master document. Structured markdown with YAML frontmatter (product name, source count, completeness), table of contents, knowledge sections (Product Information, Target Audience, Benefits and USP, Marketing Assets, plus product-type-specific sections), source attribution, and optional Changelog. | Required |
| REVIEW_FILE_SUGGESTED | Structured quality review report produced by review_master. Contains findings, recommendations, and an APPROVED or REJECTED verdict. Consumed by refine_master for revision guidance. | Required |

## Constraints

### Governance Constraints

- Layer 1 (governance) and Layer 2 (platform constitution) documents are
  read-only authority. This workflow operates at Layer 3 and must not
  redefine or contradict them.
- All generated documents must include YAML frontmatter as specified.
- All generated documents must be ASCII-only (no em-dashes, curly quotes,
  or Unicode characters).
- The workflow must include install_to_global and sync_to_backend hooks
  in context_extensions.py (returning NO_OP for this workflow).

### Naming Constraints

- Workflow slug: product_master_gen_v2 (from spec filename).
- Job prefix: PRDM.
- Artifact keys use UPPER_SNAKE_CASE.
- Step names use lowercase_with_underscores.
- Prompt files follow pattern: prompts/NN_step_name.txt.

### Content Constraints (from specification)

- Prioritize factual accuracy over completeness.
- Identify conflicting information clearly (both sides plus source
  attribution for each).
- Represent missing information as explicit knowledge gaps.
- Remain independent of downstream workflows (no campaign, media, or
  content production assumptions in the output).
- Use slug derived from PRODUCT_SOURCE_DIR name for consistent artifact
  naming.
- Support incremental updates (merge existing master plus changelog).
- The workflow must not assume all source types are present.
- URL files contain one URL per line; the LLM should fetch and process
  them.
- The output must be downstream-agnostic.

### Design Constraints

- Section generation: Single assembled document (not separate section
  artifacts). This avoids assembly complexity while keeping the workflow
  straightforward.
- Review strategy: Consolidated review of the complete document (not
  per-section review). This catches cross-section inconsistencies and
  is simpler to route.
- Gatekeeper pattern: Not applied within this workflow. The consolidated
  review step with refine loop provides quality control. The workflow
  builder pipeline itself has gatekeepers for the design artifacts.
- Self-Validation: Applied to generate_master step. The LLM checks
  completeness, consistency, source attribution, and gap identification
  before reporting APPROVED.

## Open Questions

1. None. All design decisions requested by the specification have been
   resolved within this requirements document:
   - Section generation strategy: Single document (not parallel sections).
   - Quality control: Consolidated review with refine loop.
   - Review strategy: Consolidated (not per-section).
   - Self-Validation: Applied to generate_master step.
   - Action steps: scan_sources for input inventory.
   - Artifact structure: Single assembled document.
   - Routing: Standard review -> refine loop with human approval gate
     on review.
