---
doc_type: "artifact_contract"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-718d968c"
workflow_name: "product_master_gen_v1"
job_prefix: "PRDM"
spec_source: "REQUIREMENTS-20260728-001_master_gen_v1.md"
---

# Artifact Contract: Product Master Generator

## Artifact Key Summary

| Key | Path Pattern | Description | Required |
|---|---|---|---|
| PRODUCT_SOURCE_DIR | (user-provided absolute path) | Absolute path to the product source directory containing input files. | yes |
| PRODUCT_MASTER_FILE | docs/repo/product/runs/{job_id}/PRODUCT-MASTER-{date}-{seq}_{slug}.md | Existing Product Master for incremental updates, or assembled output. | yes |
| SCAN_REPORT_FILE | docs/repo/product/runs/{job_id}/SCAN-REPORT-{date}_{slug}.md | Structured scan report classifying input files by source type. | yes |
| PRODUCT_INFO_FILE | docs/repo/product/runs/{job_id}/PRODUCT-INFO_{slug}.md | Product Information section artifact. | yes |
| TARGET_AUDIENCE_FILE | docs/repo/product/runs/{job_id}/TARGET-AUDIENCE_{slug}.md | Target Audience section artifact. | yes |
| PRODUCT_BENEFITS_FILE | docs/repo/product/runs/{job_id}/PRODUCT-BENEFITS_{slug}.md | Benefits/USP section artifact. | yes |
| MARKETING_ASSETS_FILE | docs/repo/product/runs/{job_id}/MARKETING-ASSETS_{slug}.md | Marketing Assets/Trending section artifact. | yes |
| ADDITIONAL_SECTIONS_FILE | docs/repo/product/runs/{job_id}/ADDITIONAL-SECTIONS_{slug}.md | LLM-proposed additional knowledge sections. | yes |
| REVIEW_FILE_SUGGESTED | docs/repo/product/runs/{job_id}/{job_id}-REV-{iter}_product-master-review.md | Review critique document for quality review cycle. | yes |

Placeholders:
- {job_id} - Workflow job identifier (e.g., PRDM-20260728-xxxx).
- {date} - Run date in YYYYMMDD format, resolved at registration time.
- {seq} - Auto-incrementing sequence number, resolved via resolve_next_seq().
- {slug} - Extracted from the PRODUCT_SOURCE_DIR directory name.
- {iter} - Review iteration number, resolved from state at review time.

## Input Artifacts

### PRODUCT_SOURCE_DIR

- Type: Context variable (directory path, not a file artifact).
- Required: yes
- Source: User input via operator console or job submission.
- Description: Absolute path to a directory containing product source
  files (images, PDFs, URLs, notes, specs, marketing materials). The
  workflow scans this directory recursively and uses all available
  sources. Not registered in register_artifact_keys(); resolved in
  build_context_extensions() from job state.
- Slug source: The directory basename is used to derive the {slug}
  placeholder for all output artifact filenames.

### PRODUCT_MASTER_FILE

- Type: File artifact (optional input).
- Required: no (optional)
- Source: External input from a prior workflow run or operator
  submission. When present as an input artifact with an absolute path,
  the workflow operates in incremental update mode.
- Description: Existing Product Master document for incremental
  updates. When provided, the workflow merges new section content into
  the existing document and adds a Changelog section. When absent, the
  workflow performs a fresh generation from scratch. This key serves
  dual duty: as an optional input for incremental mode, and as the
  primary output artifact containing the assembled Product Master.

## Output Artifacts

### SCAN_REPORT_FILE

- Produced by: scan_product_inputs action (action-driven step).
- Content: Structured markdown inventory of all files found in
  PRODUCT_SOURCE_DIR, classified by source type (image, manual,
  brochure, specification, document, url_list, notes). Each entry
  includes the file path, source type classification, and file
  metadata. Produced deterministically by the custom action.
- Consumers: All five section generation steps read this artifact
  to understand available source material.

### PRODUCT_INFO_FILE

- Produced by: generate_product_info prompt step (prompt-driven).
- Content: Product Information section covering product name,
  manufacturer, brand, model number, SKU, UPC/EAN, dimensions,
  weight, materials, technical specifications, package contents,
  and certifications. Reads SCAN_REPORT_FILE and source files
  independently of other section steps.

### TARGET_AUDIENCE_FILE

- Produced by: generate_target_audience prompt step (prompt-driven).
- Content: Target Audience section covering primary demographic
  profile, buyer personas (2-3 archetypes), use cases, market
  segment and positioning, and psychographic indicators. Reads
  SCAN_REPORT_FILE and source files independently.

### PRODUCT_BENEFITS_FILE

- Produced by: generate_product_benefits prompt step (prompt-driven).
- Content: Benefits/USP section covering core value proposition,
  key benefits (functional, emotional, social), problems solved,
  competitive differentiators, and source-traced supporting
  evidence. Reads SCAN_REPORT_FILE and source files independently.

### MARKETING_ASSETS_FILE

- Produced by: generate_marketing_assets prompt step (prompt-driven).
- Content: Marketing Assets/Trending section covering existing
  brand assets found in inputs, visual asset inventory, trending
  topics, social media hooks, campaign theme suggestions, and
  influencer/partnership angles. Reads SCAN_REPORT_FILE and source
  files independently.

### ADDITIONAL_SECTIONS_FILE

- Produced by: generate_additional_sections prompt step
  (prompt-driven).
- Content: LLM-proposed additional knowledge sections beyond the
  four standard ones. The LLM both proposes and generates full
  content for additional sections (e.g., Ingredients and Nutrition
  for food products, Compatibility for tech products). If no
  additional sections are warranted, this artifact is a stub
  stating so. Reads SCAN_REPORT_FILE and source files
  independently.

### PRODUCT_MASTER_FILE (output)

- Produced by: assemble_product_master prompt step (prompt-driven).
- Content: Assembled canonical Product Master combining all section
  artifacts into a single cohesive document. Includes YAML
  frontmatter (product_name, version, source_count,
  completeness_rating), table of contents, all sections in logical
  order, and source attribution mapping claims to source files.
  For incremental updates, includes a Changelog section recording
  what changed. This is the only step where all section artifacts
  converge; it handles deduplication and cross-references.
- Sequence: Uses resolve_next_seq() for auto-incrementing {seq}
  to prevent overwrites across multiple runs.

### REVIEW_FILE_SUGGESTED

- Produced by: review_product_master prompt step (prompt-driven).
- Content: Review critique document evaluating the assembled
  PRODUCT_MASTER_FILE. Used in the review/refine quality loop.
  The reviewer assesses factual accuracy, completeness, source
  attribution, and structural coherence. If the review rejects
  the Product Master, the refine step uses this document as
  feedback for improvement.
- Iteration: The {iter} component tracks the review cycle number.
  On first review, iter=00. If refinement is needed and a
  subsequent review occurs, iter increments.

## Shared Artifacts

### REVIEW_FILE_SUGGESTED

- Framework-level key used by the standard review/refine loop
  pattern (Pattern 2 in WORKFLOW_CREATION_GUIDE.md).
- Recognized by the runner for routing: the review step writes
  this artifact; the refine step reads it as required input.
- Consistent with REVIEW_FILE_SUGGESTED usage across all SDLC
  chain workflows (sdlc_10 through sdlc_80) and other workflows
  (workflow_builder_v1, 01_governance_foundation_v1, etc.).

## Naming Rationale

### Key Names

All artifact keys use UPPER_SNAKE_CASE consistent with the
codebase convention established across existing workflows.

- PRODUCT_SOURCE_DIR: Named as a directory reference rather than
  a file artifact. The _DIR suffix distinguishes it from file
  artifacts and signals that it requires special handling in
  build_context_extensions() (not registered as a file path).
- PRODUCT_MASTER_FILE: Serves dual purpose as both optional input
  (for incremental updates) and primary output. The name reflects
  its role as the canonical Product Master document.
- SCAN_REPORT_FILE: Describes the scan action output. The SCAN
  prefix distinguishes it from the content section artifacts.
- Section artifact keys (PRODUCT_INFO_FILE, TARGET_AUDIENCE_FILE,
  PRODUCT_BENEFITS_FILE, MARKETING_ASSETS_FILE,
  ADDITIONAL_SECTIONS_FILE): Each key directly describes the
  section content. The _FILE suffix follows the standard artifact
  key convention. Keys are verbose by design to avoid ambiguity
  in prompt templates and workflow.toml step definitions.
- REVIEW_FILE_SUGGESTED: Matches the framework-level shared key
  used by all review/refine loops. Not renamed to avoid breaking
  the standard routing pattern.

### Path Patterns

- Base directory: docs/repo/product/runs/{job_id}/ -- follows the
  convention of placing workflow outputs under docs/repo/<area>/
  runs/{job_id}/. The "product" area name is derived from the
  workflow domain (Product Master Generator).
- Slug extraction: The {slug} placeholder is derived from the
  PRODUCT_SOURCE_DIR directory basename using the standard
  extract_slug_from_path() utility from constants.py. This
  ensures all artifacts from the same product source are
  co-named and discoverable.
- Date prefix: The {date} component (YYYYMMDD) provides temporal
  ordering and is resolved at registration time via
  dt.datetime.now().strftime("%Y%m%d").
- Sequence auto-increment: The {seq} component on
  PRODUCT_MASTER_FILE uses resolve_next_seq() from constants.py
  to prevent overwrites when multiple runs produce the same
  artifact type. Applied only to the assembled Product Master
  because section artifacts are regenerated on each run and
  overwritten intentionally.
- Section file naming: Uses hyphen-separated type prefixes
  (PRODUCT-INFO, TARGET-AUDIENCE, etc.) followed by underscore
  and slug. This matches the convention in workflow_builder_v1
  where artifact filenames embed the key type as a prefix.
- Review file naming: Uses {job_id}-REV-{iter} prefix to enable
  traceability from review back to the originating job. The
  {iter} suffix tracks the review cycle number within the
  refine loop.

### Collision Check

A grep of all existing context_extensions.py files across 17
workflow packages confirmed that none of the product-specific
keys (PRODUCT_SOURCE_DIR, SCAN_REPORT_FILE, PRODUCT_INFO_FILE,
TARGET_AUDIENCE_FILE, PRODUCT_BENEFITS_FILE, MARKETING_ASSETS_FILE,
ADDITIONAL_SECTIONS_FILE) collide with existing artifact keys.

PRODUCT_MASTER_FILE and REVIEW_FILE_SUGGESTED are existing
convention keys. PRODUCT_MASTER_FILE is new to this workflow
(no collision). REVIEW_FILE_SUGGESTED is a shared framework key
used intentionally for standard review/refine routing.
