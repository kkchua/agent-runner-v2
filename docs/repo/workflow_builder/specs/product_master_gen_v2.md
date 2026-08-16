# Workflow Specification: Product Master Generator v2

## Overview

**Workflow name:** `product_master_gen_v2`
**Label:** Product Master Generator v2
**Job prefix:** `PRDM`
**Init step:** `scan_sources`
**Description:** Generates a canonical Product Master document that consolidates
knowledge about a single product from diverse input sources (URLs, images, PDFs,
data files, marketing materials, user notes). Supports incremental updates when
an existing Product Master is provided.

## Purpose

Product knowledge lives scattered across multiple sources -- websites, PDFs,
images, spec sheets, marketing copy, and personal notes. Downstream workflows
(campaign generation, media creation, content production) need a single,
authoritative knowledge base to reason about a product without repeatedly
researching it.

**Trigger:** A user prepares a directory containing product source materials
and runs the workflow.

**Outcome:** A structured markdown Product Master document containing all
relevant product knowledge organized into logical sections, with source
attribution and explicit knowledge gaps.

## Workflow Type

**Mixed** -- Action step for source scanning, prompt-driven steps for content
extraction, assembly, and review.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `PRODUCT_SOURCE_DIR` | Directory containing product source files | Yes |
| `PRODUCT_MASTER_INPUT` | Existing Product Master for incremental updates | No (optional) |

**Supported source types** (all optional, use whatever is available):
- Product URLs (text files with URLs, one per line)
- Product images (PNG, JPG, WEBP)
- PDFs (manuals, brochures, specifications)
- Data files (CSV, XLSX)
- Marketing materials (DOCX, MD, TXT)
- User notes (MD, TXT)

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `SOURCE_INVENTORY_FILE` | `SOURCE_INV-{date}-{seq}_{slug}.md` | Catalog of all discovered source files with type classification |
| `EXTRACTED_CONTENT_FILE` | `EXTRACT-{date}-{seq}_{slug}.md` | Raw extracted content from all sources, with source attribution |
| `PRODUCT_MASTER_FILE` | `PRODUCT_MASTER-{date}-{seq}_{slug}.md` | The assembled canonical Product Master document |
| `REVIEW_FILE_SUGGESTED` | `PRDM-REV-{date}-{seq}_{slug}.md` | Quality review of the Product Master |

## Product Master Content Requirements

The Product Master must contain at minimum these sections:

1. **Product Information** -- Factual data: name, brand, model, dimensions,
   materials, technical specs, package contents, certifications.

2. **Target Audience** -- Demographics, buyer personas, use cases, market
   segment, psychographic indicators.

3. **Benefits & USP** -- Value proposition, key benefits, problems solved,
   competitive differentiators with supporting evidence.

4. **Marketing Assets** -- Brand assets found, visual inventory, trending
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
- Use slug derived from PRODUCT_SOURCE_DIR name for consistent artifact naming.
- Support incremental updates: when PRODUCT_MASTER_INPUT is provided, merge
  new knowledge and add a Changelog section with dated entries.
- URL files contain one URL per line; the LLM should fetch and process them.
- Not all source types will be present -- the workflow must handle any
  combination gracefully.

## Quality Requirements

The final Product Master must pass these quality checks:

- **Source attribution** -- Claims trace back to specific input files.
- **Completeness** -- All available sources were processed and their content
  represented (or explicitly noted as gaps).
- **No hallucination** -- No information invented beyond what sources provide.
- **Conflict detection** -- Contradictory information from different sources
  is flagged with both sides cited.
- **Downstream agnostic** -- No assumptions about how downstream workflows
  will use the Product Master.
- **YAML frontmatter** -- Product name, source count, completeness score,
  generation date.

## Builder Instructions

**Step architecture:** The builder shall propose the step sequence based on
the domain requirements above. The workflow is NOT a meta-workflow, so TDD
loop is not required. Suggested phase decomposition (builder may adjust):

1. **Scan phase** -- Discover and catalog all source files in PRODUCT_SOURCE_DIR
2. **Extract phase** -- Process each source type and extract content
3. **Assemble phase** -- Synthesize extracted content into the Product Master
4. **Review phase** -- Quality review against the constraints above
5. **Refine phase** -- Fix issues found in review (conditional)

### Action: scan_product_sources

**Purpose:** Recursively scan PRODUCT_SOURCE_DIR for all files. Classify each file
by type (URL list, image, PDF, data file, marketing material, user note) based on
extension. Build a source inventory with file path, type, size, and modification
date. Write the inventory to SOURCE_INVENTORY_FILE.

**Inputs:** PRODUCT_SOURCE_DIR

**Outputs:** SOURCE_INVENTORY_FILE

**Error handling:**
- If PRODUCT_SOURCE_DIR doesn't exist or is empty, return REJECTED with reject_code `NO_SOURCES_FOUND`.
- If a file can't be read (permissions), log a warning and skip it — include skipped files in the inventory with status "unreadable".

**Returns:** APPROVED when at least one source file is found and classified. REJECTED if directory is missing or empty.

### URL Fetching

URL files contain one URL per line. The prompt-driven extract step shall fetch
each URL and process the response. Fetch constraints:
- Timeout: 30 seconds per URL
- On failure (timeout, HTTP error, SSL error): log the URL and error, skip it,
  note it as a knowledge gap in the Product Master
- Do not retry failed URLs — the review step will flag missing content

**Gatekeepers:** The builder should determine where QC gates add value. At minimum,
a quality gate after assembly (before final review) is recommended.

## Notes

- The output must be downstream-agnostic (no execution assumptions).
- The design should balance extensibility (easy to add sections later)
  with simplicity (don't over-engineer for the current use case).
- Reference: `agnes_media_gen_v1` shows the pattern for multi-source
  directory scanning and archive handling.
