---
doc_type: "prompts_index"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-718d968c"
workflow_name: "product_master_gen_v1"
---

# Prompts Index: Product Master Generator

This document lists all prompt template files generated for the
product_master_gen_v1 workflow package.

## Prompt Files

| # | File | Step Name | Type | Purpose |
|---|------|-----------|------|---------|
| 02 | prompts/02_generate_product_info.txt | generate_product_info | prompt | Generate the Product Information section: factual product data including name, manufacturer, model, SKU, dimensions, weight, materials, technical specs, package contents, and certifications. |
| 03 | prompts/03_generate_target_audience.txt | generate_target_audience | prompt | Generate the Target Audience section: demographic profile, buyer personas, use cases, market segment, and psychographic indicators. |
| 04 | prompts/04_generate_product_benefits.txt | generate_product_benefits | prompt | Generate the Benefits/USP section: core value proposition, functional/emotional/social benefits, problems solved, and competitive differentiators with source-traced evidence. |
| 05 | prompts/05_generate_marketing_assets.txt | generate_marketing_assets | prompt | Generate the Marketing Assets section: brand assets inventory, visual assets, trending topics, social media hooks, campaign themes, and influencer angles. |
| 06 | prompts/06_generate_additional_sections.txt | generate_additional_sections | prompt | Analyze the product and propose additional knowledge sections beyond the four standard ones, or produce a stub if none are warranted. |
| 07 | prompts/07_assemble_product_master.txt | assemble_product_master | prompt | Assemble all section artifacts into the canonical Product Master with YAML frontmatter, table of contents, deduplication, cross-references, source attribution, and optional Changelog. |
| 08 | prompts/08_review_product_master.txt | review_product_master | prompt | Review the assembled Product Master for factual accuracy, source attribution, completeness, knowledge gap handling, and structural coherence. |
| 09 | prompts/09_refine_product_master.txt | refine_product_master | prompt | Apply review feedback to correct and improve the Product Master in place, addressing factual corrections, missing content, formatting, and source attribution issues. |

## Notes

- No prompt file exists for step 01 (scan_product_inputs) because it is
  an action-driven step implemented in actions.py, not a prompt-driven
  step. The custom Python action performs deterministic file scanning
  and classification without LLM involvement.
- Prompt numbering starts at 02 to match the step sequence numbers
  from the step architecture.
- All prompt files use bare {ARTIFACT_KEY} placeholders (not backtick-
  wrapped) for artifact path references.
- All prompt files are ASCII-only.
