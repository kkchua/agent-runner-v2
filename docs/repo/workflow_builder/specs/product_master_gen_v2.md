# Workflow Specification: Product Master Generator v2

## Overview

**Workflow name:** `product_master_gen_v2`
**Label:** Product Master Generator v2
**Job prefix:** `PRDM`
**Description:** Generates a canonical Product Master document that consolidates
knowledge about a single product from diverse input sources.

## Purpose

Product knowledge lives scattered across multiple sources -- websites, PDFs,
images, spec sheets, marketing copy, and personal notes. Downstream workflows
(campaign generation, media creation, content production) need a single,
authoritative knowledge base to reason about a product without repeatedly
researching it.

**Trigger:** A user prepares a directory containing product source materials
and runs the workflow.

**Outcome:** A structured markdown Product Master document containing all
relevant product knowledge organized into logical sections.

## Inputs

**PRODUCT_SOURCE_DIR** — Path to directory containing product source files.
Supported types (all optional, use whatever is available):
- Product URLs (text files with URLs)
- Product images (PNG, JPG, WEBP)
- PDFs (manuals, brochures, specifications)
- Data files (CSV, XLSX)
- Marketing materials (DOCX, MD, TXT)
- User notes (MD, TXT)

**PRODUCT_MASTER_FILE** (optional) — Existing Product Master for incremental
updates. If provided, the workflow should merge new knowledge and add a
Changelog.

## Outputs

**PRODUCT_MASTER_FILE** — The assembled canonical Product Master document.

The Product Master should be a comprehensive markdown document with:
- YAML frontmatter (product name, source count, completeness)
- Table of contents
- Knowledge sections organized logically
- Source attribution where claims trace to input files
- Changelog (if incremental update)

## Knowledge Sections

The Product Master should contain at minimum these sections:

1. **Product Information** — Factual data: name, brand, model, dimensions,
   materials, technical specs, package contents, certifications.

2. **Target Audience** — Demographics, buyer personas, use cases, market
   segment, psychographic indicators.

3. **Benefits & USP** — Value proposition, key benefits, problems solved,
   competitive differentiators with supporting evidence.

4. **Marketing Assets** — Brand assets found, visual inventory, trending
   topics, social hooks, campaign angles.

The workflow should analyze the input sources and determine if additional
sections would be valuable based on the product type. For example:
- Food products might need "Ingredients & Nutrition"
- Tech products might need "Compatibility & Warranty"
- Fashion products might need "Sizing & Care"

## Constraints

- Prioritize factual accuracy over completeness.
- Identify conflicting information clearly (both sides + sources).
- Represent missing information as explicit knowledge gaps.
- Remain independent of downstream workflows (no campaign/media assumptions).
- Use slug from PRODUCT_SOURCE_DIR name for consistent artifact naming.
- Support incremental updates (merge + changelog).

## Design Decisions for the Builder

The builder should determine the optimal architecture for this workflow:

- **Section generation strategy:** Generate all sections in one step or
  parallel independent steps? What makes sense for data flow and review?

- **Quality control:** How should validation be handled? Where do gatekeepers
  add value in this specific workflow?

- **Review strategy:** What review points make sense? Should there be
  per-section reviews, a consolidated review, or both?

- **Self-Validation:** Which producer steps benefit from self-checking
  before reporting completion?

- **Action steps:** What custom actions are needed (input scanning, etc.)?

- **Artifact structure:** Should sections be separate artifacts or a
  single assembled document? Consider modularity vs simplicity.

- **Routing:** How should refinement loops work? What triggers APPROVED
  vs REJECTED at each review point?

The builder should apply the gatekeeper pattern, self-validation, and
principles-based generation where they add value, but is not constrained
to any specific number of steps or gatekeepers.

## Notes

- The workflow should not assume all source types are present.
- URL files contain one URL per line; the LLM should fetch and process them.
- The output should be downstream-agnostic (no execution assumptions).
- The design should balance extensibility (easy to add sections later)
  with simplicity (don't over-engineer for the current use case).
