# Composition System Specification: Product Master Generator

> **Domain:** Product knowledge consolidation
> **Input to:** workflow_builder_v2
> **Standard:** COMPOSITION_SYSTEM_STANDARD.md
> **Downstream consumers:** video_campaign_manuscript (and other composition systems that need product data)

---

## 1. Domain Overview

**Domain name:** `product_master_gen`
**Label:** Product Master Generator
**Job prefix:** `PRDM`
**Description:** Generates a canonical Product Master document that consolidates knowledge about a single product from diverse input sources.

### 1.1 Purpose

Product knowledge lives scattered across multiple sources — websites, PDFs, images, spec sheets, marketing copy, and personal notes. Downstream composition systems (e.g., video_campaign_manuscript) need a single, authoritative knowledge base to resolve placeholders like `{product_name}`, `{key_benefit}`, `{target_audience}` without repeatedly researching the product.

**Trigger:** User prepares a directory containing product source materials and runs the workflow.

**Outcome:** A structured markdown Product Master document containing all relevant product knowledge organized into logical sections, with source attribution and explicit knowledge gaps. This document serves as the `product_master` data source for downstream composition systems.

### 1.2 Domain Context

The Product Master is a foundational data artifact in the content production pipeline. It sits between raw source materials and downstream composition systems that need product data. The Product Master must be:
- **Downstream-agnostic** — no assumptions about how composition systems will use it
- **Factually accurate** — all claims traceable to source files
- **Complete** — all available sources processed, gaps explicitly noted
- **Incrementally updatable** — supports merging new knowledge into existing Product Masters

---

## 2. Component Schema (Layer 1)

In this composition system, "components" are **source content blocks** — extracted knowledge units from different source types. Each source type has distinct extraction rules and produces structured content.

### 2.1 Component Types

| Component Type | Purpose | Required? | Cardinality |
|---|---|---|---|
| `url_source` | Web content fetched from product URLs | No | Unordered set (0-N URLs) |
| `image_source` | Visual content extracted from product images | No | Unordered set (0-N images) |
| `pdf_source` | Document content extracted from PDFs | No | Unordered set (0-N PDFs) |
| `data_source` | Structured data from CSV/XLSX files | No | Unordered set (0-N data files) |
| `marketing_source` | Marketing copy from DOCX/MD/TXT files | No | Unordered set (0-N files) |
| `note_source` | User notes from MD/TXT files | No | Unordered set (0-N files) |

**Note:** All source types are optional. The workflow must handle any combination gracefully, including an empty source directory (which should REJECT).

### 2.2 Common Properties

All source content blocks share these properties after extraction:

| Property | Type | Required | Description |
|---|---|---|---|
| `source_id` | string | Yes | Unique identifier (format: `{type}-{filename}-{seq}`) |
| `source_type` | enum | Yes | One of the 6 types in 2.1 |
| `source_path` | string | Yes | Original file path or URL |
| `extraction_status` | enum | Yes | Values: success, partial, failed, skipped |
| `content` | string | Yes | Extracted text content |
| `source_attribution` | string | Yes | Human-readable source reference for citation |

### 2.3 Type-Specific Properties

#### Type: url_source

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `url` | string | Yes | The fetched URL | `"https://example.com/product"` |
| `http_status` | integer | Yes | HTTP response status code | `200` |
| `fetch_timeout` | boolean | Yes | Whether the fetch timed out | `false` |
| `page_title` | string | No | HTML page title | `"Product X - Official Site"` |

#### Type: image_source

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `image_format` | enum | Yes | Values: png, jpg, webp | `"png"` |
| `image_dimensions` | string | No | Width x height in pixels | `"1920x1080"` |
| `visual_description` | string | Yes | LLM vision extraction of image content | `"Product bottle on white background, studio lighting"` |

#### Type: pdf_source

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `page_count` | integer | Yes | Number of pages in PDF | `12` |
| `pdf_type` | enum | No | Values: manual, brochure, spec_sheet, unknown | `"spec_sheet"` |
| `extracted_text` | string | Yes | Full text extracted from PDF | (long text) |

#### Type: data_source

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `data_format` | enum | Yes | Values: csv, xlsx | `"csv"` |
| `row_count` | integer | Yes | Number of data rows | `42` |
| `column_headers` | array | Yes | Column header names | `["name", "value", "unit"]` |
| `structured_data` | string | Yes | JSON representation of the data | `"[{...}, {...}]"` |

#### Type: marketing_source

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `doc_format` | enum | Yes | Values: docx, md, txt | `"md"` |
| `word_count` | integer | Yes | Approximate word count | `350` |
| `content_type` | enum | No | Values: press_release, ad_copy, product_description, other | `"product_description"` |

#### Type: note_source

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `note_format` | enum | Yes | Values: md, txt | `"md"` |
| `word_count` | integer | Yes | Approximate word count | `120` |

### 2.4 Component File Format

Source content blocks are not stored as individual files. They are extracted at runtime and cataloged in the SOURCE_INVENTORY_FILE and EXTRACTED_CONTENT_FILE artifacts.

### 2.5 Validation Rules

- **Source directory exists:** PRODUCT_SOURCE_DIR must exist and be non-empty
- **Source type classification:** Every file must be classifiable into one of the 6 types based on extension
- **URL fetch constraints:** 30-second timeout per URL, no retries on failure
- **Extraction status accuracy:** Failed/partial extractions must be flagged with reasons
- **Unreadable files:** Files that can't be read (permissions) logged as "skipped" with warning

---

## 3. Composition Format (Layer 2)

### 3.1 Composition Structure

The "composition" in this domain is the **source directory** — it defines which sources are combined into the Product Master. An optional existing Product Master provides the base for incremental updates.

| Field | Type | Required | Description |
|---|---|---|---|
| `PRODUCT_SOURCE_DIR` | directory | Yes | Directory containing product source files |
| `PRODUCT_MASTER_INPUT` | file | No | Existing Product Master for incremental updates |

### 3.2 Binding Rules

| Binding Name | Source Type | Cardinality | Required? | Description |
|---|---|---|---|---|
| `url_files` | url_source | Unordered set | No | Text files containing URLs (one per line) |
| `image_files` | image_source | Unordered set | No | Product images (PNG, JPG, WEBP) |
| `pdf_files` | pdf_source | Unordered set | No | Product documents (manuals, brochures, specs) |
| `data_files` | data_source | Unordered set | No | Structured data (CSV, XLSX) |
| `marketing_files` | marketing_source | Unordered set | No | Marketing materials (DOCX, MD, TXT) |
| `note_files` | note_source | Unordered set | No | User notes (MD, TXT) |

### 3.3 Override Mechanism

Not applicable in the traditional sense. The "overrides" are:
- **Incremental updates:** When PRODUCT_MASTER_INPUT is provided, new knowledge is merged into the existing document, with a Changelog section tracking dated entries.
- **Conflict resolution:** When sources provide conflicting information, both sides are cited with source attribution. The user resolves conflicts in subsequent runs.

### 3.4 Placeholder Resolution

Not applicable — this workflow produces the data source that OTHER composition systems use for placeholder resolution.

### 3.5 Example Composition

```
PRODUCT_SOURCE_DIR/
├── urls.txt                    # URL list (one per line)
├── product_front.png           # Product image
├── product_back.jpg            # Product image
├── spec_sheet.pdf              # Technical specifications
├── ingredients.csv             # Ingredient data
├── press_release.md            # Marketing copy
└── my_notes.txt                # User observations
```

---

## 4. Output Format (Layer 3)

### 4.1 Output Structure

The output is a markdown file with YAML frontmatter:

| Section | Source | Description |
|---|---|---|
| Frontmatter | Generated | product_name, source_count, completeness_score, generation_date |
| 1. Product Information | All sources | Factual data: name, brand, model, dimensions, materials, specs, certifications |
| 2. Target Audience | Marketing + notes | Demographics, buyer personas, use cases, market segment |
| 3. Benefits & USP | Marketing + URLs | Value proposition, key benefits, problems solved, competitive differentiators |
| 4. Marketing Assets | Marketing + images | Brand assets, visual inventory, trending topics, social hooks, campaign angles |
| 5+. Domain-Specific | All sources | Additional sections based on product type (ingredients, compatibility, sizing, etc.) |
| N. Knowledge Gaps | Generated | Explicit list of missing information with suggested sources |
| N+1. Changelog | Incremental only | Dated entries showing what changed (only when PRODUCT_MASTER_INPUT provided) |

### 4.2 Resolution Rules

- **Source attribution:** Every claim traces back to specific input files
- **Conflict detection:** Contradictory information from different sources flagged with both sides cited
- **Gap identification:** Missing information represented as explicit knowledge gaps
- **No hallucination:** No information invented beyond what sources provide
- **Downstream agnostic:** No assumptions about how downstream workflows will use the Product Master

### 4.3 Quality Requirements

- **Source attribution** — Claims trace back to specific input files
- **Completeness** — All available sources processed, content represented or noted as gaps
- **No hallucination** — No information invented beyond what sources provide
- **Conflict detection** — Contradictory information flagged with both sides cited
- **Downstream agnostic** — No assumptions about downstream usage
- **YAML frontmatter** — Product name, source count, completeness score, generation date

### 4.4 Example Output (Skeleton)

```markdown
---
product_name: "Lumiere Radiance Serum"
source_count: 7
completeness_score: 0.85
generation_date: "2026-08-08"
---

# Lumiere Radiance Serum — Product Master

## 1. Product Information
- **Brand:** Lumiere Skincare
- **Product Name:** Radiance Serum
- **Model:** LS-RAD-30ML
- **Dimensions:** 4cm x 4cm x 12cm
- **Materials:** Glass bottle, aluminum cap
- **Key Ingredients:** Vitamin C (15%), Hyaluronic Acid, Niacinamide
- **Certifications:** Cruelty-free, Vegan, Dermatologist-tested
- *Source: spec_sheet.pdf, product_front.png*

## 2. Target Audience
- **Demographics:** Women 25-45, urban professionals
- **Use Cases:** Daily skincare routine, anti-aging, brightening
- **Market Segment:** Premium skincare, mid-luxury
- *Source: press_release.md, my_notes.txt*

## 3. Benefits & USP
- **Key Benefit:** Visible brightening in 2 weeks
- **Problem Solved:** Dull, uneven skin tone
- **Differentiator:** 15% Vitamin C concentration (higher than competitors)
- *Source: press_release.md, urls.txt (https://...)*

## 4. Marketing Assets
- **Visual Style:** Minimalist, warm neutrals with gold accents
- **Social Hooks:** "What if your skincare routine was missing one ingredient?"
- **Campaign Angles:** Product launch, summer glow, science-backed
- *Source: product_front.png, press_release.md*

## 5. Knowledge Gaps
- **Pricing:** Not found in any source
- **Shelf life:** Not mentioned in spec sheet
- **Customer reviews:** No review data provided
- **Suggested sources:** Add pricing page URL, customer review export

## 6. Changelog
- **2026-08-08:** Initial generation from 7 sources
```

---

## 5. Operational Requirements

### 5.1 Workflow Phases

| Phase | Purpose |
|---|---|
| **Scan** | Discover and catalog all source files in PRODUCT_SOURCE_DIR, classify by type |
| **Extract** | Process each source type: fetch URLs, read images (vision), extract PDFs, parse data files, read text files |
| **Assemble** | Synthesize extracted content into the Product Master document with source attribution |
| **Review** | Quality review against constraints (attribution, completeness, no hallucination, conflict detection) |
| **Refine** | Fix issues found in review (conditional) |

### 5.2 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `PRODUCT_SOURCE_DIR` | Directory containing product source files | Yes |
| `PRODUCT_MASTER_INPUT` | Existing Product Master for incremental updates | No |

### 5.3 Output Artifacts

| Artifact Key | Description |
|---|---|
| `SOURCE_INVENTORY_FILE` | Catalog of all discovered source files with type classification |
| `EXTRACTED_CONTENT_FILE` | Raw extracted content from all sources, with source attribution |
| `PRODUCT_MASTER_FILE` | The assembled canonical Product Master document |
| `REVIEW_FILE_SUGGESTED` | Quality review of the Product Master |

### 5.4 Action Steps

One custom action step needed:

1. **scan_product_sources** — Recursively scan PRODUCT_SOURCE_DIR for all files. Classify each file by type based on extension (url→url_source, png/jpg/webp→image_source, pdf→pdf_source, csv/xlsx→data_source, docx→marketing_source, md/txt→note_source or marketing_source). Build a source inventory with file path, type, size, and modification date. Write the inventory to SOURCE_INVENTORY_FILE.

**Error handling:**
- If PRODUCT_SOURCE_DIR doesn't exist or is empty, return REJECTED with reject_code `NO_SOURCES_FOUND`
- If a file can't be read (permissions), log a warning and skip it — include skipped files in the inventory with status "unreadable"

**Returns:** APPROVED when at least one source file is found and classified. REJECTED if directory is missing or empty.

### 5.5 Domain-Specific Requirements

- **URL fetching:** 30-second timeout per URL, no retries on failure. Failed URLs noted as knowledge gaps.
- **Incremental updates:** When PRODUCT_MASTER_INPUT is provided, merge new knowledge and add a Changelog section with dated entries.
- **Slug derivation:** Use PRODUCT_SOURCE_DIR name for consistent artifact naming.
- **No downstream assumptions:** The Product Master must not assume how downstream composition systems will use it.

---

## 6. References

- **Downstream consumer:** `video_campaign_manuscript_v2` (uses Product Master for placeholder resolution)
- **Related workflows:** `agnes_media_gen_v1` (pattern for multi-source directory scanning)
- **Composition System Standard:** `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md`

---

**End of Specification**
