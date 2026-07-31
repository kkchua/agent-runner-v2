# Product Master Generator v1

## Overview

The Product Master Generator workflow consolidates product knowledge from
diverse input sources (images, PDFs, URLs, spec sheets, marketing materials,
notes) into a single, authoritative, structured Product Master document.

The workflow uses a mixed architecture: an action-driven step for input
scanning and classification, followed by prompt-driven steps for each
knowledge section generation, assembly, quality review, and refinement.

Input: A directory path (PRODUCT_SOURCE_DIR) containing product source files
of various types, optionally an existing Product Master for incremental
updates (PRODUCT_MASTER_FILE).

Output: A structured markdown Product Master composed of independently
generated section artifacts -- Product Information, Target Audience,
Benefits/USP, Marketing Assets, and LLM-proposed Additional Sections --
assembled into a single cohesive document with YAML frontmatter, table of
contents, source attribution, and optional changelog for incremental updates.

## Prerequisites

- Python 3.12+ with the agent-runner-v2 virtual environment activated
- The agent-runner-v2 runner installed and configured
- Layer 1 governance foundation seeded at
  ~/.ukbe-runner/bundles/core/current/foundation/
- A product source directory containing at least one file of any supported
  type (images, PDFs, URLs, spreadsheets, text files, documents)
- No external API keys or credentials required (the workflow uses the
  runner's standard LLM coder invocation for prompt-driven steps)

## Installation

To deploy this workflow package:

1. Copy the workflow package directory to the workflows/ directory:

   ```
   workflows/product_master_gen_v1/
       workflow.toml
       context_extensions.py
       actions.py
       prompts/
           02_generate_product_info.txt
           03_generate_target_audience.txt
           04_generate_product_benefits.txt
           05_generate_marketing_assets.txt
           06_generate_additional_sections.txt
           07_assemble_product_master.txt
           08_review_product_master.txt
           09_refine_product_master.txt
   ```

2. Run the runner initialization to sync the workflow:

   ```
   ukbe-run-agent init
   ```

3. Optionally sync to the backend for daemon mode:

   ```
   ukbe-run-agent sync-workflows product_master_gen_v1
   ```

## Usage

### Batch File

Run the workflow using the batch file at the project root:

```
run-product_master_gen_v1.bat
```

### Operator Console

Submit a job via the operator console with the required context variable:

- PRODUCT_SOURCE_DIR: Absolute path to the product source directory

Optional:
- PRODUCT_MASTER_FILE: Absolute path to an existing Product Master for
  incremental update mode

### Daemon Mode

The workflow can be submitted to the backend daemon for async execution.
The backend URL is configured in ~/.ukbe-runner/config.json.

## Step Reference

| # | Step Name | Type | Role Policy | Purpose |
|---|-----------|------|-------------|---------|
| 1 | scan_product_inputs | action | N/A | Recursively scan the product source directory and classify files by source type (image, manual, brochure, specification, document, url_list, notes). Produce a structured scan report. |
| 2 | generate_product_info | prompt | architect_standard | Generate the Product Information section: factual product data (name, manufacturer, model, SKU, dimensions, weight, materials, specs, package contents, certifications). |
| 3 | generate_target_audience | prompt | architect_standard | Generate the Target Audience section: demographic profile, buyer personas, use cases, market segment, psychographic indicators. |
| 4 | generate_product_benefits | prompt | architect_standard | Generate the Benefits/USP section: value proposition, functional/emotional/social benefits, problems solved, competitive differentiators. |
| 5 | generate_marketing_assets | prompt | architect_standard | Generate the Marketing Assets section: brand assets, visual inventory, trending topics, social hooks, campaign themes, influencer angles. |
| 6 | generate_additional_sections | prompt | architect_standard | Analyze the product and propose additional knowledge sections beyond the four standard ones, or produce a stub. |
| 7 | assemble_product_master | prompt | architect_standard | Assemble all section artifacts into the canonical Product Master with frontmatter, TOC, deduplication, cross-references, source attribution, and optional Changelog. |
| 8 | review_product_master | prompt | reviewer_standard | Review the assembled Product Master for quality: factual accuracy, source attribution, completeness, knowledge gap handling, structural coherence. |
| 9 | refine_product_master | prompt | architect_standard | Apply review feedback to correct the Product Master in place. Loops back to review step (max 2 iterations). |
| 10 | stepCompletion | action | N/A | Terminal step. Marks the workflow job as COMPLETED. |

## Artifact Keys

| Key | Description |
|-----|-------------|
| PRODUCT_SOURCE_DIR | (Input) Absolute path to the product source directory containing input files. User-provided context variable. |
| PRODUCT_MASTER_FILE | (Input/Output) Existing Product Master for incremental updates, or the assembled output. Auto-incrementing sequence number. |
| SCAN_REPORT_FILE | Structured scan report classifying input files by source type. Produced by the scan_product_inputs action. |
| PRODUCT_INFO_FILE | Product Information section artifact covering factual product data. |
| TARGET_AUDIENCE_FILE | Target Audience section artifact covering demographic and market insights. |
| PRODUCT_BENEFITS_FILE | Benefits/USP section artifact covering value proposition and differentiators. |
| MARKETING_ASSETS_FILE | Marketing Assets section artifact covering brand assets and trending knowledge. |
| ADDITIONAL_SECTIONS_FILE | LLM-proposed additional knowledge sections, or a stub if none warranted. |
| REVIEW_FILE_SUGGESTED | Review critique document produced during the quality review cycle. |

## Review/Refine Loop

The review step (step 8) includes a human approval gate and a refinement
loop. If the reviewer rejects the Product Master, the refine step (step 9)
applies corrections in place and control returns to the review step.
Maximum refinement iterations: 2. After exhaustion, the workflow fails
with code REFINE_EXHAUSTED and class HUMAN_RETRY_REQUIRED.
