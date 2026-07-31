---
doc_type: "workflow_design"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-718d968c.2"
spec_source: "product_master_gen_v1.md"
workflow_name: "product_master_gen_v1"
job_prefix: "PRDM"
---

# Workflow Requirements: Product Master Generator

## Overview

The Product Master Generator workflow consolidates product knowledge from diverse
input sources (URLs, images, PDFs, spec sheets, marketing materials, notes) into
a single, authoritative, structured Product Master document. Each knowledge
section (Product Information, Target Audience, Benefits/USP, Marketing Assets,
and LLM-proposed additional sections) is generated independently as a separate
artifact, then assembled into a canonical Product Master. The workflow supports
both fresh generation and incremental updates to an existing Product Master, and
is designed to be downstream-agnostic -- the output contains no campaign, media,
or marketing deployment assumptions.

## Workflow Type

**Mixed** -- The workflow combines action-driven steps with prompt-driven steps.

Justification:

- The specification explicitly identifies this as a mixed workflow.
- An action step (`scan_product_inputs`) is required to recursively scan the
  input directory, classify files by source type, and produce a structured scan
  report. This is deterministic file-system work that does not require an LLM.
- All section generation steps (PRODUCT_INFO_FILE, TARGET_AUDIENCE_FILE,
  PRODUCT_BENEFITS_FILE, MARKETING_ASSETS_FILE, ADDITIONAL_SECTIONS_FILE) are
  prompt-driven, requiring LLM reasoning to synthesize knowledge from sources.
- The assembly step (PRODUCT_MASTER_FILE) is prompt-driven, requiring the LLM
  to merge sections, deduplicate, cross-reference, and generate a changelog
  for incremental updates.
- A review/refine cycle is implied by the presence of REVIEW_FILE_SUGGESTED
  as an output artifact, requiring prompt-driven review and refinement steps.
- A custom Python action (`scan_product_inputs`) must be registered via
  `actions.py` with the `@action` decorator.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| PRODUCT_SOURCE_DIR | Absolute path to a directory containing product source files (images, PDFs, URLs, notes, specs, marketing materials). The workflow scans this directory and uses all available sources. | Yes |
| PRODUCT_MASTER_FILE | Existing Product Master document for incremental updates. When provided, the workflow merges new section content and adds a Changelog section. When absent, the workflow performs a fresh generation. | No |

### Supported Source Types (all optional within the source directory)

| Source Type | File Patterns |
|---|---|
| Image | *.png, *.jpg, *.jpeg, *.webp, *.gif, *.bmp |
| Manual | *.pdf (with manual/guide/user-guide in filename) |
| Brochure | *.pdf (with brochure/catalog/lookbook in filename) |
| Specification | *.pdf (with spec/specification/datasheet in filename), *.csv, *.xlsx, *.xls |
| Document | *.pdf (other), *.docx, *.doc, *.md, *.txt (other) |
| URL List | *.md, *.txt (containing http/https URLs, one per line) |
| Notes | *.md, *.txt (with notes/journal in filename) |

## Output Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| SCAN_REPORT_FILE | Structured markdown report of the input directory scan, classifying each file by source type. Produced by the scan_product_inputs action. | Yes |
| PRODUCT_INFO_FILE | Product Information section: product name, manufacturer, brand, model, SKU, UPC/EAN, dimensions, weight, materials, technical specifications, package contents, certifications. | Yes |
| TARGET_AUDIENCE_FILE | Target Audience section: primary demographic profile, buyer personas (2-3 archetypes), use cases, market segment, psychographic indicators. | Yes |
| PRODUCT_BENEFITS_FILE | Benefits/USP section: core value proposition, key benefits (functional, emotional, social), problems solved, competitive differentiators with source-traced evidence. | Yes |
| MARKETING_ASSETS_FILE | Marketing Assets/Trending section: existing brand assets found in inputs, visual asset inventory, trending topics, social media hooks, campaign theme suggestions, influencer angles. | Yes |
| ADDITIONAL_SECTIONS_FILE | LLM-proposed additional knowledge sections beyond the four standard ones. If no additional sections are warranted, this artifact is a stub stating so. | Yes |
| PRODUCT_MASTER_FILE | Assembled canonical Product Master combining all section artifacts with YAML frontmatter, table of contents, source attribution mapping, and (for incremental updates) a Changelog section. | Yes |
| REVIEW_FILE_SUGGESTED | Review critique document produced during the quality review cycle. Used in review/refine loops. | Yes |

## Section Descriptions

Each section below is generated as an independent artifact. Sections do not
depend on each other's output; each reads the scan report and source files
independently.

### PRODUCT_INFO_FILE -- Product Information

Factual product data:
- Product name, manufacturer, brand
- Model number, SKU, UPC/EAN
- Dimensions (L x W x H) and weight
- Materials and construction
- Technical specifications (structured tables preferred)
- Package contents
- Certifications and compliance

### TARGET_AUDIENCE_FILE -- Target Audience

Audience and market insights:
- Primary demographic profile (age, gender, location, income)
- Buyer personas (2-3 archetypes)
- Use cases and scenarios
- Market segment and positioning
- Psychographic indicators

### PRODUCT_BENEFITS_FILE -- Benefits/USP

Value proposition and selling points:
- Core value proposition
- Key benefits (functional, emotional, social)
- Problems solved
- Competitive differentiators
- Supporting evidence for each claim (source-traced)

### MARKETING_ASSETS_FILE -- Marketing Assets/Trending

Marketing-relevant knowledge:
- Existing brand assets found in inputs (logos, style guides, templates)
- Visual asset inventory (product photos, lifestyle images)
- Trending topics and angles relevant to the product
- Social media hooks and content ideas
- Campaign theme suggestions
- Influencer/partnership angles

### ADDITIONAL_SECTIONS_FILE -- LLM-Proposed Sections

The workflow analyzes the product and its sources to identify any additional
knowledge sections beyond the four standard ones that would be valuable.
Examples from the spec:
- A food product might need "Ingredients & Nutrition" and "Storage & Handling"
- A tech product might need "Compatibility" and "Warranty & Support"
- A fashion product might need "Sizing Guide" and "Care Instructions"

If no additional sections are warranted, this artifact is a stub stating so.

### PRODUCT_MASTER_FILE -- Assembled Product Master

The final assembled document combining all section artifacts into a single
cohesive Product Master with:
- YAML frontmatter (product name, version, source count, completeness rating)
- Table of contents
- All sections in logical order
- Source attribution mapping claims to their source files
- For incremental updates: a Changelog section recording what changed

The assembly step is the only point where all section artifacts come together.
It handles deduplication and cross-references.

## Constraints

### Governance and Platform

- Layer 1 governance and Layer 2 platform constitution are read-only authority.
  This workflow must not redefine or contradict them.
- The workflow must comply with the standard runner execution model: steps
  produce meta.json sidecars as the sole communication channel.
- All prompt templates must use ASCII-only content and bare {ARTIFACT_KEY}
  placeholders (no backtick wrapping).

### Naming Conventions

- Workflow package directory name: `product_master_gen_v1` (derived from spec
  slug). Must match `name` in workflow.toml and `workflow_name` in
  context_extensions.py.
- Job prefix: `PRDM`
- Artifact filenames use date-prefixed patterns with slug and sequence numbers:
  - Section files: `{TYPE}_{slug}.md`
  - Scan report: `SCAN-REPORT-{date}_{slug}.md`
  - Product Master: `PRODUCT-MASTER-{date}-{seq}_{slug}.md` (auto-incrementing)
  - Review files: `{job_id}-REV-{iter}_product-master-review.md` (iteration suffix)
- Slug is extracted from the PRODUCT_SOURCE_DIR directory name.
- All output paths are under `docs/repo/product/runs/{job_id}/`.

### External Dependencies

- Custom action `scan_product_inputs` must be implemented in `actions.py`
  using the `@action` decorator from `agent_runner_v2.workflow_packages.actions`.
- The workflow depends on the runner's artifact resolution mechanism
  (`context_extensions.py` `register_artifact_keys` and `build_context_extensions`).
- Sequence auto-increment for PRODUCT_MASTER_FILE requires `resolve_next_seq()`
  from `agent_runner_v2.constants`.
- URL content fetching during section generation is performed by the LLM
  directly, per the specification.

### Content Constraints

- Factual accuracy takes priority over completeness.
- Conflicting information across sources must be explicitly identified with
  both sides noted and source attribution.
- Missing information must be explicitly represented as knowledge gaps,
  not omitted or fabricated.
- The Product Master is downstream-agnostic: no campaign execution, media
  generation, or marketing deployment assumptions.
- Each section generation reads the scan report and source files independently.
  Sections do not depend on each other's output.
- The assembly step is the only point where all section artifacts come together.

### Role Policy Constraints

- Role policies must be selected from the available registry
  (workflows/_registry/role_policies.json).
- The specification does not mandate specific role policies per step.
  The design_steps workflow must assign appropriate policies.

## Context Variables

| Variable | Source | Description |
|---|---|---|
| PRODUCT_SOURCE_DIR | User input | Absolute path to the product source directory containing all input files (images, PDFs, URLs, notes, specs, marketing materials). |
| GOVERNANCE_RUNTIME_ROOT | Standard runtime | Path to Layer 1 governance documents, resolved at runtime from the runner home bundles directory. |

All artifact path variables (SCAN_REPORT_FILE, PRODUCT_INFO_FILE, etc.) are
resolved automatically from the artifact key registry via
context_extensions.py. They are not listed here as context variables because
they are managed through the standard artifact resolution mechanism.

## Data Schemas

The specification does not define formal JSON schemas for output artifacts.
All section artifacts are free-form structured markdown documents. However,
the Product Master assembly has a defined frontmatter structure:

### PRODUCT_MASTER_FILE Frontmatter

| Field | Purpose |
|---|---|
| product_name | Name of the product (string) |
| version | Version identifier for the Product Master (string) |
| source_count | Number of source files processed (integer) |
| completeness_rating | Assessment of knowledge coverage (string/enum) |

Total: 4 frontmatter fields.

### SCAN_REPORT_FILE Structure

The scan report is a structured markdown inventory produced by the
scan_product_inputs action. It classifies each file found in
PRODUCT_SOURCE_DIR by source type using the classification rules defined
in the Custom Actions section. No formal schema -- the action determines
the markdown structure.

### Section Artifacts

Each section artifact (PRODUCT_INFO_FILE, TARGET_AUDIENCE_FILE,
PRODUCT_BENEFITS_FILE, MARKETING_ASSETS_FILE, ADDITIONAL_SECTIONS_FILE)
is a standalone markdown document. The specification defines the content
topics each section must cover but does not impose a rigid schema. The
LLM coder determines the internal structure within each section.

## Implementation Notes

### Custom Action: scan_product_inputs

The specification defines a custom action with explicit file type
classification rules:

| File Pattern | Source Type |
|---|---|
| *.png, *.jpg, *.jpeg, *.webp, *.gif, *.bmp | image |
| *.pdf (manual/guide/user-guide in filename) | manual |
| *.pdf (brochure/catalog/lookbook in filename) | brochure |
| *.pdf (spec/specification/datasheet in filename) | specification |
| *.pdf (other) | document |
| *.csv, *.xlsx, *.xls | specification |
| *.md, *.txt (containing http/https URLs) | url_list |
| *.md, *.txt (notes/journal in filename) | notes |
| *.md, *.txt (other) | document |
| *.docx, *.doc | document |

The action must:
- Recursively scan PRODUCT_SOURCE_DIR
- Classify each file using the rules above
- Produce SCAN_REPORT_FILE as structured markdown
- Return APPROVED with scan report path, or REJECTED if directory is empty
  or inaccessible

### Reusable Patterns from Codebase

- **Slug extraction:** Extract slug from PRODUCT_SOURCE_DIR directory name
  for consistent artifact naming. Pattern documented in
  WORKFLOW_CREATION_GUIDE.md (_extract_slug_from_path pattern).
- **Sequence auto-increment:** Use resolve_next_seq() from
  agent_runner_v2.constants for PRODUCT_MASTER_FILE naming. Pattern
  documented in WORKFLOW_CREATION_GUIDE.md.
- **WorkflowExtensions interface:** context_extensions.py must implement
  register_artifact_keys() and build_context_extensions() per the standard
  pattern in WORKFLOW_CREATION_GUIDE.md.
- **Action decorator:** Use @action from
  agent_runner_v2.workflow_packages.actions for scan_product_inputs.

### URL Handling

- URL files (*.md, *.txt) contain one URL per line.
- The LLM fetches and processes URL content during section generation.
- No pre-fetching action is required -- the spec delegates URL fetching
  to the LLM coder's web access capabilities.

### Incremental Update Handling

- If PRODUCT_MASTER_FILE is provided as input, the workflow operates in
  incremental update mode.
- New section content is merged with existing content.
- A Changelog section is added recording what changed.
- The design_steps workflow determines the specific merge strategy
  (see Design Decisions Required section).

### Extensibility

To add a new standard section in a future version:
1. Add a new artifact key (e.g., PRICING_FILE)
2. Add the section description to the spec
3. Update the assembly logic to include the new section artifact

The modular design ensures each section can evolve independently.

## Resolved Questions

1. **Section generation ordering and parallelism:** The specification explicitly
   states "Each section generation should read the scan report and source files
   independently. Sections do not depend on each other's output." This confirms
   that sections are independent. The sequencing and ordering of independent
   steps is delegated to the design_steps workflow (see Design Decisions
   Required below). [Incorporated into Section Descriptions and Constraints.]

2. **LLM URL fetching capability:** The specification explicitly states "URL
   files are expected to contain one URL per line. The LLM fetches and processes
   URL content during section generation." This resolves the question: the
   design intent is LLM-driven URL fetching during section generation. No
   pre-fetching action step is required. [Incorporated into Implementation
   Notes - URL Handling.]

3. **Artifact key traceability:** All 8 output artifact keys and 2 input
   artifact keys are explicitly declared in the specification's Input Artifacts
   and Output Artifacts tables. No inferred or invented artifact keys are
   present. [Verified -- no changes needed.]

4. **Workflow Type classification:** The specification explicitly marks this
   as a Mixed workflow (checkbox checked). The step types (action-driven scan,
   prompt-driven section generation, prompt-driven assembly) are consistent
   with this classification. [Verified -- no changes needed.]

## Design Decisions Required

### DD-001: Section Generation Step Granularity

**Context:** The specification declares five independent section generation
tasks (PRODUCT_INFO_FILE, TARGET_AUDIENCE_FILE, PRODUCT_BENEFITS_FILE,
MARKETING_ASSETS_FILE, ADDITIONAL_SECTIONS_FILE). The runner executes steps
sequentially. The spec says sections are independent and do not depend on
each other.

**Recommended approach:** Create five separate prompt-driven steps, one per
section artifact. Each step reads {SCAN_REPORT_FILE} and relevant source
files from {PRODUCT_SOURCE_DIR}, and produces its single section artifact.
This maximizes modularity, makes each step independently reviewable, and
aligns with the spec's extensibility model (sections can be added/removed
independently).

**Alternative 1:** Combine all five sections into a single generation step
that produces all section artifacts at once. This reduces step count but
violates the modularity principle and makes the step monolithic.

**Alternative 2:** Generate sections in a single step but use a combined
prompt that outputs all five files. This is similar to Alternative 1 but
might be simpler to implement. Still suffers from monolithic step issues.

**Trade-offs:**
- Five steps: more workflow steps, but each is focused, testable, and
  independently extensible. Aligns with spec's modular design.
- Single step: fewer steps, but harder to maintain, review, and extend.
  If one section fails, the entire generation must retry.

**Risks:** Sequential execution of five LLM steps increases total runtime.
However, each step is bounded in scope, which improves output quality.

### DD-002: Review/Refine Loop Scope

**Context:** The specification produces REVIEW_FILE_SUGGESTED as an output
artifact but does not specify which artifacts are subject to review. The
spec defers this to the workflow builder: "The workflow builder should
determine how best to generate, review, and assemble these sections."

**Recommended approach:** Review the assembled PRODUCT_MASTER_FILE only,
not individual sections. Rationale: (a) the spec identifies the assembly
step as "the only point where all section artifacts come together" and
"handles deduplication and cross-references" -- this is where quality
issues are most visible; (b) reviewing each of five sections individually
would require five separate review cycles, greatly increasing complexity;
(c) a single review of the final assembled product is the standard pattern
in existing SDLC workflows.

**Alternative 1:** Review each section individually before assembly. This
provides granular quality control but multiplies the review/refine cycles
by five and contradicts the spec's statement that assembly is the
integration point.

**Alternative 2:** Two-tier review -- lightweight section-level check
followed by full assembly review. This adds complexity without clear
spec support.

**Trade-offs:**
- Assembly-only review: simpler, aligns with spec integration model,
  standard pattern. May miss section-level issues that are diluted in
  the assembled document.
- Section-level review: more thorough but significantly more complex
  and costly in runtime.

**Risks:** Assembly-only review may not catch section-specific quality
issues. Mitigation: the review prompt should instruct the reviewer to
evaluate each section's contribution to the whole.

### DD-003: Review and Refine Role Policies

**Context:** The specification does not specify which role policies should
be used for review and refinement steps.

**Recommended approach:** Follow the standard SDLC pattern from the
workflow creation guide:
- Section generation steps: `architect_standard` (generation/refinement)
- Review step: `reviewer_standard` (review/critique)
- Refine step: `architect_standard` (refinement based on review feedback)
- Assembly step: `architect_standard` (generation)

This is consistent with Pattern 2 (Prompt-Driven with Review/Refine Loop)
documented in the workflow creation guide.

**Alternative 1:** Use `reviewer_standard` for both review and refinement.
This deviates from the standard pattern where refine uses the same role
as generation.

**Alternative 2:** Use `validation_standard` for review instead of
`reviewer_standard`. This is for validation/audit rather than critique.

**Trade-offs:**
- Standard pattern: proven, consistent with other workflows, predictable
  coder behavior.
- Deviations: may offer specific advantages but break consistency.

**Risks:** None significant. The standard pattern is well-established.

### DD-004: Incremental Update Merge Strategy

**Context:** When an existing PRODUCT_MASTER_FILE is provided, the spec
says the workflow "merges new section content and adds a Changelog." It
does not specify whether all sections are regenerated or only sections
with new/changed source data.

**Recommended approach:** Regenerate all sections on every run, then merge
with existing content. Rationale: (a) product knowledge may have evolved
even if source files are unchanged (LLM synthesis improvements); (b) the
spec says "utilize all available information to maximize knowledge
completeness"; (c) comparing source changes to determine which sections
need regeneration adds significant complexity without clear benefit;
(d) the Changelog captures what changed between versions regardless.

**Alternative 1:** Analyze source directory changes (new/modified/deleted
files since last run) and only regenerate sections affected by changed
sources. This is more efficient but requires tracking which sources feed
which sections, and the mapping is implicit (LLM-driven).

**Alternative 2:** Always perform a fresh generation, ignoring the existing
Product Master except for the Changelog comparison. Simpler but loses the
benefit of incremental updates.

**Trade-offs:**
- Regenerate all: simpler implementation, consistent quality, full use of
  available sources. Higher runtime cost.
- Selective regeneration: more efficient but complex to implement correctly.
  Risk of stale sections if source-to-section mapping is inaccurate.

**Risks:** Full regeneration increases runtime. For products with many
source files, this could be significant. Mitigation: the scan report
provides source inventory, enabling future optimization if needed.

### DD-005: Additional Sections Generation Approach

**Context:** The ADDITIONAL_SECTIONS_FILE is described as "LLM-proposed
extra sections." The spec says the workflow should "analyze the product
and its sources to identify any additional knowledge sections." It is
unclear whether the LLM proposes section titles only, or both proposes
and generates full content.

**Recommended approach:** The LLM both proposes and generates full content
for additional sections within the single ADDITIONAL_SECTIONS_FILE artifact.
Rationale: (a) the spec defines ADDITIONAL_SECTIONS_FILE as a single
artifact, not a proposal followed by separate generation steps; (b) the
spec gives examples of what additional sections might contain (e.g.,
"Ingredients & Nutrition" for food products), implying content generation;
(c) the modular design means additional sections are already separated
from the standard four, so bundling proposal + content in one artifact
is consistent.

**Alternative 1:** Two-step process: first step proposes section titles
and outlines, second step generates full content for each proposed section
as separate artifacts. More modular but contradicts the single-artifact
design in the spec.

**Alternative 2:** The LLM proposes section titles only, and a downstream
workflow generates content. This defers content generation entirely and
produces an incomplete Product Master.

**Trade-offs:**
- Single step (propose + generate): produces a complete artifact, aligns
  with spec's single-artifact design. May produce irrelevant content if
  proposals are poor.
- Two-step process: more modular, allows review of proposals before
  committing to generation. Contradicts spec's single-artifact design.

**Risks:** If the LLM proposes inappropriate additional sections, the
artifact contains wasted content. Mitigation: the stub fallback ("no
additional sections warranted") handles the case where no extras are
needed, and the review step can flag poor proposals.
