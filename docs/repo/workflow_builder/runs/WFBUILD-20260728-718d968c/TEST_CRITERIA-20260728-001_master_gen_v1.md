---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-718d968c"
spec_ref: "docs/repo/workflow_builder/specs/product_master_gen_v1.md"
workflow_name: "product_master_gen_v1"
workflow_type: "mixed"
generated_date: "2026-07-28"
---

# Test Criteria: Product Master Generator v1

## 1. Spec Objective Summary

The Product Master Generator workflow ingests a directory of diverse product
source materials (images, PDFs, URLs, text files, spreadsheets) and produces
a canonical Product Master document. The end-to-end transformation is:

INPUT: A directory path (PRODUCT_SOURCE_DIR) containing product source files
of various types (images, PDFs, URLs, specs, notes, marketing materials),
optionally an existing Product Master for incremental updates
(PRODUCT_MASTER_FILE).

OUTPUT: A structured markdown Product Master composed of independently-
generated section artifacts -- Product Information, Target Audience,
Benefits/USP, Marketing Assets, and LLM-proposed Additional Sections --
assembled into a single cohesive document with YAML frontmatter, table of
contents, source attribution, and optional changelog for incremental updates.

The workflow uses a mixed architecture: an action-driven step for input
scanning and classification, followed by prompt-driven steps for each
section's knowledge generation, assembly, review, and refinement.


## 2. Criteria for analyze_spec Step

### 2.1 Requirements Document Content

1. REQ-001: The requirements document must identify the workflow as a Mixed
   type (action steps + prompt-driven steps).
2. REQ-002: The requirements document must list the input artifact
   PRODUCT_SOURCE_DIR as required, with type "directory path".
3. REQ-003: The requirements document must list the input artifact
   PRODUCT_MASTER_FILE as optional, with type "existing markdown file".
4. REQ-004: The requirements document must list all eight output artifact
   keys: SCAN_REPORT_FILE, PRODUCT_INFO_FILE, TARGET_AUDIENCE_FILE,
   PRODUCT_BENEFITS_FILE, MARKETING_ASSETS_FILE, ADDITIONAL_SECTIONS_FILE,
   PRODUCT_MASTER_FILE, REVIEW_FILE_SUGGESTED.
5. REQ-005: The requirements document must describe the scan_product_inputs
   custom action and its file classification rules (images, manuals,
   brochures, specifications, url_lists, notes, documents).
6. REQ-006: The requirements document must describe each of the five standard
   sections (Product Info, Target Audience, Benefits/USP, Marketing Assets,
   Additional Sections) with their expected content domains.
7. REQ-007: The requirements document must capture the constraint that
   sections are generated independently -- each reads the scan report and
   source files, not other sections' output.
8. REQ-008: The requirements document must capture the constraint that the
   assemble step is the only point where all sections come together,
   handling deduplication and cross-references.
9. REQ-009: The requirements document must capture the incremental update
   behavior: if PRODUCT_MASTER_FILE is provided as input, the workflow
   merges new content and adds a Changelog.
10. REQ-010: The requirements document must capture the slug extraction
    requirement (from input directory name) and sequence auto-increment
    for PRODUCT_MASTER_FILE naming.
11. REQ-011: The requirements document must note that URL files contain
    one URL per line, and the LLM fetches/processes URL content during
    section generation.
12. REQ-012: The requirements document must capture the extensibility
    principle: adding a new section in future versions requires only a new
    artifact key, section description, and assembly logic update -- no
    changes to existing sections.

### 2.2 Workflow Type Classification

13. REQ-013: The workflow must be classified as "mixed" type, not purely
    action-driven or purely prompt-driven.
14. REQ-014: The scan_product_inputs step must be classified as
    action-driven (deterministic file scanning, no LLM needed).
15. REQ-015: All section generation steps must be classified as
    prompt-driven (require LLM reasoning over source content).
16. REQ-016: The assembly step must be classified as prompt-driven (requires
    LLM judgment for deduplication, cross-referencing, logical ordering).

### 2.3 Input/Output Artifact Identification

17. REQ-017: The requirements must identify that all output paths are under
    docs/repo/product/runs/{job_id}/.
18. REQ-018: The requirements must specify filename patterns for each
    artifact (SCAN-REPORT-{date}_{slug}.md, PRODUCT-INFO_{slug}.md, etc.).
19. REQ-019: The requirements must identify PRODUCT_SOURCE_DIR as a context
    variable that comes from user input, not from artifact registration.
20. REQ-020: The requirements must identify GOVERNANCE_RUNTIME_ROOT as a
    standard context variable injected by context_extensions.py.


## 3. Criteria for generate_package Step

### 3.1 Files That Must Be Generated

1. PKG-001: workflow.toml must exist and be valid TOML with [workflow]
   metadata (name, version, label, job_prefix, init_step) and [[step]]
   definitions for every workflow step.
2. PKG-002: context_extensions.py must exist, define a class extending
   WorkflowExtensions, set workflow_name = "product_master_gen_v1",
   implement register_artifact_keys() and build_context_extensions().
3. PKG-003: actions.py must exist containing the scan_product_inputs action
   decorated with @action("scan_product_inputs").
4. PKG-004: prompts/ directory must contain one .txt file per prompt-driven
   step (section generation prompts, assembly prompt, review prompt,
   refine prompt).
5. PKG-005: Each prompt file must use bare {ARTIFACT_KEY} placeholders
   (not backtick-wrapped) for all artifact references.

### 3.2 Files That Must NOT Be Generated

6. PKG-006: MUST NOT generate bundle_governance.toml unless the spec
   explicitly requests backend sync validation (the spec does not).
7. PKG-007: MUST NOT generate install.py (spec explicitly unchecked
   "Needs global installation").
8. PKG-008: MUST NOT generate prompts for action-driven steps
   (scan_product_inputs is purely action-driven, no LLM involved).
9. PKG-009: MUST NOT generate a batch file (run-*.bat) as part of the
   workflow package -- batch files are created separately at project root.
10. PKG-010: MUST NOT hardcode absolute paths in context_extensions.py
    or prompts. All paths must be computed dynamically using
    get_workspace_root() and get_runner_home().

### 3.3 Action Code Requirements: scan_product_inputs

11. PKG-011: The scan_product_inputs action must read PRODUCT_SOURCE_DIR
    from context variables (not from state artifacts).
12. PKG-012: The action must recursively walk the input directory and
    classify each file by extension and filename pattern according to
    the classification table in the spec.
13. PKG-013: The action must produce a structured markdown scan report
    (SCAN_REPORT_FILE) listing every file found with its classification
    (image, manual, brochure, specification, url_list, notes, document).
14. PKG-014: The action must return ActionResult(status="REJECTED", ...)
    if PRODUCT_SOURCE_DIR does not exist, is empty, or is inaccessible.
15. PKG-015: The action must return ActionResult(status="APPROVED", ...)
    with the scan report path in the artifacts dict when successful.
16. PKG-016: The file classification logic must match the spec's rules:
    - *.png, *.jpg, *.jpeg, *.webp, *.gif, *.bmp -> image
    - *.pdf with manual/guide/user-guide in filename -> manual
    - *.pdf with brochure/catalog/lookbook in filename -> brochure
    - *.pdf with spec/specification/datasheet in filename -> specification
    - *.pdf (other) -> document
    - *.csv, *.xlsx, *.xls -> specification
    - *.md, *.txt containing http/https URLs -> url_list
    - *.md, *.txt with notes/journal in filename -> notes
    - *.md, *.txt (other) -> document
    - *.docx, *.doc -> document
17. PKG-017: The scan report must include file counts per source type
    and a summary of total files discovered.

### 3.4 Prompt Requirements: Section Generation Steps

18. PKG-018: Each section generation prompt must instruct the LLM to read
    the scan report ({SCAN_REPORT_FILE}) to understand what source files
    are available.
19. PKG-019: Each section generation prompt must instruct the LLM to read
    relevant source files from the scan report, not assume all source
    types are available.
20. PKG-020: The Product Info prompt must instruct the LLM to extract
    factual data: product name, manufacturer, model, SKU, dimensions,
    weight, materials, technical specs, package contents, certifications.
21. PKG-021: The Target Audience prompt must instruct the LLM to identify
    demographic profile, buyer personas (2-3), use cases, market segment,
    and psychographic indicators.
22. PKG-022: The Benefits/USP prompt must instruct the LLM to identify
    core value proposition, functional/emotional/social benefits, problems
    solved, competitive differentiators, with source-traced evidence.
23. PKG-023: The Marketing Assets prompt must instruct the LLM to inventory
    brand assets, visual assets, trending topics, social media hooks,
    campaign themes, and influencer angles.
24. PKG-024: The Additional Sections prompt must instruct the LLM to
    analyze the product and propose domain-specific sections beyond the
    four standard ones, or produce a stub if none are warranted.
25. PKG-025: Each section prompt must instruct the LLM to represent
    missing information as explicit knowledge gaps, not fabricate data.
26. PKG-026: Each section prompt must instruct the LLM to flag conflicting
    information across sources with both sides noted and source attribution.
27. PKG-027: Each section prompt must instruct the LLM to write the output
    to the artifact path using file-writing tools (not put content in the
    meta.json result field).
28. PKG-028: Each section prompt must instruct the LLM to use the product
    slug ({SLUG}) in the output filename pattern.

### 3.5 Prompt Requirements: Assembly Step

29. PKG-029: The assembly prompt must instruct the LLM to read ALL section
    artifacts (PRODUCT_INFO_FILE, TARGET_AUDIENCE_FILE,
    PRODUCT_BENEFITS_FILE, MARKETING_ASSETS_FILE, ADDITIONAL_SECTIONS_FILE).
30. PKG-030: The assembly prompt must instruct the LLM to produce YAML
    frontmatter with: product name, version, source count, completeness
    rating.
31. PKG-031: The assembly prompt must instruct the LLM to generate a table
    of contents.
32. PKG-032: The assembly prompt must instruct the LLM to arrange sections
    in logical order and handle deduplication and cross-references.
33. PKG-033: The assembly prompt must instruct the LLM to include source
    attribution mapping claims to their source files.
34. PKG-034: The assembly prompt must instruct the LLM to conditionally
    include a Changelog section when an existing PRODUCT_MASTER_FILE is
    provided as input (incremental update mode).
35. PKG-035: The assembly prompt must instruct the LLM to write the
    assembled document to {PRODUCT_MASTER_FILE}.

### 3.6 Prompt Requirements: Review and Refine Steps

36. PKG-036: The review prompt must instruct the LLM to evaluate the
    assembled Product Master against the spec's quality criteria: factual
    accuracy, source attribution, completeness, knowledge gap handling.
37. PKG-037: The review prompt must instruct the LLM to write its critique
    to {REVIEW_FILE_SUGGESTED}.
38. PKG-038: The refine prompt must instruct the LLM to read the review
    critique ({REVIEW_FILE_SUGGESTED}) and the current Product Master
    ({PRODUCT_MASTER_FILE}), apply fixes, and write back to
    {PRODUCT_MASTER_FILE} in-place.

### 3.7 Context Extensions Requirements

39. PKG-039: register_artifact_keys() must return mappings for all 8 output
    artifact keys with relative paths under docs/repo/product/runs/{job_id}/.
40. PKG-040: register_artifact_keys() must use slug extraction from
    PRODUCT_SOURCE_DIR for consistent naming across all section files.
41. PKG-041: register_artifact_keys() must use resolve_next_seq() for the
    PRODUCT_MASTER_FILE sequence number ({seq} placeholder).
42. PKG-042: register_artifact_keys() must include date strings in filenames
    for SCAN_REPORT_FILE and PRODUCT_MASTER_FILE.
43. PKG-043: build_context_extensions() must resolve ALL artifact paths to
    absolute paths using workspace_root.
44. PKG-044: build_context_extensions() must inject GOVERNANCE_RUNTIME_ROOT
    pointing to the Layer 1 governance foundation directory.
45. PKG-045: build_context_extensions() must inject PRODUCT_SOURCE_DIR from
    user input (passed via state or context) as an absolute path.
46. PKG-046: build_context_extensions() must handle project_root=None by
    falling back to get_workspace_root() or Path.cwd().

### 3.8 Workflow.toml Routing Requirements

47. PKG-047: The init_step must be the scan_product_inputs step.
48. PKG-048: scan_product_inputs must route to the first section generation
    step on success (onsuccess at [[step]] top level).
49. PKG-049: Each section generation step must route to the next section
    generation step (or to assembly if last section) on success.
50. PKG-050: The assembly step must route to the review step on success.
51. PKG-051: The review step must have on_reject_refine routing to the
    refine step, and onsuccess routing to promote or stepCompletion.
52. PKG-052: The refine step must have loop_returns_to pointing back to
    the review step.
53. PKG-053: The workflow must end with a stepCompletion step using
    action = "step_completion".
54. PKG-054: Review step should have requires_human_approval_after = true.

### 3.9 Negative Criteria

55. PKG-055: MUST NOT include required_inputs for action-driven steps that
    do not read artifacts (scan_product_inputs reads from context, not
    from state artifacts).
56. PKG-056: MUST NOT hardcode the slug value in any prompt or path --
    it must be dynamically extracted at runtime.
57. PKG-057: MUST NOT generate prompts for steps that should be
    action-driven (no LLM prompt for scan_product_inputs).
58. PKG-058: MUST NOT assume all source types are present. The workflow
    must handle the case where only some source types are available.
59. PKG-059: MUST NOT include campaign execution, media generation, or
    marketing deployment logic. The Product Master is downstream-agnostic.
60. PKG-060: MUST NOT place onsuccess under [step.artifacts] -- it must
    be at [[step]] top level.
61. PKG-061: MUST NOT place promotes under [step.artifacts] -- it must
    be at [[step]] top level.
62. PKG-062: MUST NOT backtick-wrap artifact key placeholders in prompts.


## 4. Criteria for validate_bundle Step

### 4.1 Structural Checks

1. VAL-001: workflow.toml must parse as valid TOML without errors.
2. VAL-002: The [workflow] table must contain name = "product_master_gen_v1",
   version, label, job_prefix, and init_step fields.
3. VAL-003: The workflow name in workflow.toml must match the directory
   name exactly: product_master_gen_v1.
4. VAL-004: Every [[step]] must have a name field.
5. VAL-005: Every prompt-driven [[step]] must have a prompt field pointing
   to a file that exists under prompts/.
6. VAL-006: Every action-driven [[step]] must have an action field.
7. VAL-007: The init_step value must match the name of the first [[step]].
8. VAL-008: The last [[step]] must be stepCompletion with
   action = "step_completion".
9. VAL-009: All onsuccess values must reference valid step names that exist
   as [[step]] definitions.
10. VAL-010: All loop_returns_to values must reference valid step names.
11. VAL-011: All [step.on_reject_refine].step values must reference valid
    step names.

### 4.2 Artifact Registration Checks

12. VAL-012: Every artifact key in [step.artifacts].produces must have a
    corresponding entry in context_extensions.py register_artifact_keys().
13. VAL-013: Every artifact key in [step.artifacts].required_inputs must
    either be produced by a prior step or be a declared input artifact.
14. VAL-014: The result_meta_key on each step must match one of the keys
    in that step's produces list.
15. VAL-015: Artifact keys are case-sensitive -- no mismatches between
    workflow.toml keys and context_extensions.py keys.

### 4.3 Semantic Checks

16. VAL-016: The scan_product_inputs action function in actions.py must
    contain actual file scanning logic (os.walk or Path.rglob), not a
    stub or placeholder.
17. VAL-017: The scan_product_inputs action must contain the complete
    file type classification table from the spec (all 10 file pattern
    rules).
18. VAL-018: The scan_product_inputs action must return an ActionResult
    object with appropriate status, remark, and artifacts.
19. VAL-019: Each prompt file must contain substantive instructions
    (not empty or boilerplate). Each prompt must reference at least one
    artifact key placeholder.
20. VAL-020: The context_extensions.py must contain a valid class that
    inherits from WorkflowExtensions and sets workflow_name correctly.
21. VAL-021: The build_context_extensions() method must call
    workspace_root / rel_path for every artifact key (absolute path
    resolution).

### 4.4 File Completeness

22. VAL-022: The workflow package directory must contain:
    - workflow.toml
    - context_extensions.py
    - actions.py (because scan_product_inputs is a custom action)
    - prompts/ directory with all referenced .txt files
23. VAL-023: The package must NOT contain files not required by the spec
    (no install.py, no bundle_governance.toml unless justified).
24. VAL-024: Every prompt file referenced in workflow.toml must exist
    at the specified relative path.
25. VAL-025: No prompt file should exist that is not referenced by any
    step in workflow.toml (no orphan prompts).


## 5. Criteria for review_package Step

### 5.1 Spec Fulfillment

1. REV-001: The generated workflow must implement the complete
    end-to-end flow described in the spec: scan inputs -> generate
    sections -> assemble -> review -> (refine) -> complete.
2. REV-002: The workflow must produce all 8 output artifacts listed
    in the spec's output table.
3. REV-003: Each of the 5 standard section artifacts must cover the
    content domains described in the spec (Product Info, Target Audience,
    Benefits/USP, Marketing Assets, Additional Sections).
4. REV-004: The Product Master assembly must include: YAML frontmatter,
    table of contents, all sections in logical order, source attribution.
5. REV-005: The workflow must support incremental updates when an existing
    PRODUCT_MASTER_FILE is provided (Changelog generation).
6. REV-006: The workflow must be independent of downstream campaign,
    marketing, and media generation workflows.

### 5.2 Step-by-Step Verification

7. REV-007: The scan_product_inputs step must recursively scan the input
    directory, classify files by the spec's rules, and produce a markdown
    scan report.
8. REV-008: Each section generation step must read the scan report, read
    relevant source files, and produce its section artifact independently
    (no dependency on other sections' output).
9. REV-009: The assembly step must read all section artifacts and produce
    the assembled Product Master document.
10. REV-010: The review step must evaluate the Product Master and produce
    a review critique document.
11. REV-011: The refine step must apply review feedback to improve the
    Product Master in-place.
12. REV-012: URL content fetching must be supported: URL files contain
    one URL per line, and the LLM processes URL content during section
    generation.

### 5.3 Data Flow Verification

13. REV-013: The scan report (SCAN_REPORT_FILE) produced by step 1 must
    be listed as required_input for all section generation steps.
14. REV-014: All section artifacts must be listed as required_inputs for
    the assembly step.
15. REV-015: The PRODUCT_MASTER_FILE must be listed as required_input
    for the review step.
16. REV-016: Both PRODUCT_MASTER_FILE and REVIEW_FILE_SUGGESTED must be
    listed as required_inputs for the refine step.
17. REV-017: The PRODUCT_MASTER_FILE optional input must be available
    to the assembly step when provided (for incremental updates).
18. REV-018: PRODUCT_SOURCE_DIR must be accessible as a context variable
    to the scan action and to prompts that need to reference source files.

### 5.4 No Hallucinations

19. REV-019: The workflow must NOT include steps for campaign generation,
    media creation, or marketing deployment -- these are downstream.
20. REV-020: The workflow must NOT hardcode product-specific data or
    assume a specific product type (the workflow is product-agnostic).
21. REV-021: The workflow must NOT require inputs beyond
    PRODUCT_SOURCE_DIR (required) and PRODUCT_MASTER_FILE (optional).
22. REV-022: The workflow must NOT include API keys, authentication
    mechanisms, or external service calls (no LLM API calls beyond the
    prompt-driven steps' standard coder invocation).
23. REV-023: The workflow must NOT invent additional standard sections
    beyond the five described in the spec.


## 6. Prompt Quality Criteria

### 6.1 Output Mechanism Clarity

1. PQ-001: Each prompt must explicitly instruct the LLM to use file-writing
    tools (e.g., write tool) to create actual files on disk at the paths
    specified by artifact placeholders.
2. PQ-002: Each prompt must explicitly state that the meta.json result
    field is for status/summary text ONLY, not for artifact content.
    Example acceptable phrasing: "The result field in meta.json must
    contain a brief summary of what was done. All document content must
    be written to the artifact files."
3. PQ-003: Each prompt must NOT use ambiguous phrasing like "Write the
    output to: {ARTIFACT_KEY}" without clarifying that this means writing
    a file to the resolved absolute path.
4. PQ-004: Prompts should include a sentence like: "Write the generated
    content to the file at {ARTIFACT_KEY}" where {ARTIFACT_KEY} resolves
    to an absolute path, making it unambiguous.

### 6.2 Ambiguity Check

5. PQ-005: No prompt should contain phrases that could be interpreted as
    "put the content in the result field" rather than "write a file".
    Test: Could an LLM reasonably interpret the instruction as putting
    markdown content into meta.json's result string?
6. PQ-006: Prompts must use "Write the file to {KEY}" or "Create the
    document at {KEY}" -- never just "Output: {KEY}" which is ambiguous.
7. PQ-007: For section generation prompts, the prompt must specify
    exactly which source files to consult (via the scan report), not
    leave it to the LLM to guess what "relevant sources" means.
8. PQ-008: The assembly prompt must specify the exact order of sections
    and the exact frontmatter fields required, not use vague terms like
    "organize appropriately".
9. PQ-009: The review prompt must specify concrete evaluation criteria
    (factual accuracy, source attribution, completeness, gap handling),
    not just "review the document".
10. PQ-010: The refine prompt must specify how to handle each type of
    review finding (factual correction, missing section, formatting fix),
    not just "improve the document".

### 6.3 Common LLM Mistake Guards

11. PQ-011: Prompts must guard against the LLM putting JSON/document
    content in the meta.json result field instead of writing files.
    Include explicit instruction: "Write content to files, not to
    the meta.json result field."
12. PQ-012: Section generation prompts must guard against the LLM
    fabricating product data when sources do not contain it. Include
    explicit instruction: "If information is not found in any source
    file, represent it as a knowledge gap (e.g., 'Not available from
    provided sources')."
13. PQ-013: The assembly prompt must guard against the LLM silently
    dropping sections. Include instruction: "Include ALL section
    artifacts. If a section is empty or a stub, include it with a note."
14. PQ-014: Prompts must guard against the LLM skipping index file
    creation when multiple output files are produced. (If applicable
    to the workflow design.)
15. PQ-015: Section generation prompts must guard against the LLM
    including content from other sections' domains. Each section prompt
    must clearly scope what content belongs in that section.

### 6.4 Completeness

16. PQ-016: Each prompt must specify the required output format (markdown
    with YAML frontmatter, ASCII-only).
17. PQ-017: Each section generation prompt must specify the filename
    pattern using the slug placeholder.
18. PQ-018: The assembly prompt must specify all required frontmatter
    fields: product name, version, source count, completeness rating.
19. PQ-019: The assembly prompt must specify that source attribution
    maps claims to their source files.
20. PQ-020: The refine prompt must specify that the output replaces
    the PRODUCT_MASTER_FILE in-place (same file path, updated content).
21. PQ-021: Each prompt must include a Reference Inputs section listing
    all input artifacts to read, using bare {ARTIFACT_KEY} placeholders.
22. PQ-022: Each prompt must include an Artifacts section listing all
    output artifacts to produce, using bare {ARTIFACT_KEY} placeholders.
23. PQ-023: The Additional Sections prompt must specify what to do when
    no additional sections are warranted (produce a stub document stating
    so).


## 7. Audit Criteria

### 7.1 Logic Audit

The spec involves retry, error handling, and conditional branching
(review/refine loops, incremental updates, empty source handling).

1. LOG-001: The scan_product_inputs action must handle the case where
    PRODUCT_SOURCE_DIR does not exist -- return REJECTED with clear
    error message, not raise an unhandled exception.
2. LOG-002: The scan_product_inputs action must handle the case where
    PRODUCT_SOURCE_DIR exists but is empty -- return REJECTED with
    message "No source files found in directory".
3. LOG-003: The scan_product_inputs action must handle permission errors
    when reading the directory -- return REJECTED with descriptive message,
    not crash.
4. LOG-004: The review/refine loop must have a maximum iteration count
    (via on_reject_refine.max_iterations) to prevent infinite loops.
5. LOG-005: The on_reject_refine configuration must specify
    exhausted_failure_code and exhausted_failure_class for when
    refinement iterations are exhausted.
6. LOG-006: The refine step must use edit_mode = "in_place" and
    target_artifact = "PRODUCT_MASTER_FILE" to correctly update the
    artifact in-place.
7. LOG-007: The refine step must have loop_returns_to = "review" (or
    the review step name) to create the correct loop routing.
8. LOG-008: The workflow must handle the case where ADDITIONAL_SECTIONS_FILE
    is a stub (no additional sections warranted) -- the assembly step
    must not fail or produce errors when this section is minimal.
9. LOG-009: The workflow must handle incremental updates correctly:
    when PRODUCT_MASTER_FILE is provided as optional input, the assembly
    step must produce a Changelog. When it is not provided, no Changelog
    section should appear.

### 7.2 Data Integrity Audit

The spec involves file operations, scan report generation, index-like
tracking (scan report as inventory), and assembly of multiple artifacts.

10. DAT-001: The scan report must list every file found in the directory.
    Verify by: compare file count in scan report summary against actual
    directory contents.
11. DAT-002: File classifications in the scan report must match the
    spec's classification rules. Verify by: spot-check at least 3 files
    of different types against the classification table.
12. DAT-003: The scan report must include a summary section with counts
    per source type and total files. This summary must be consistent
    with the file listing above it.
13. DAT-004: Section generation steps must write complete files, not
    partial or truncated content. Verify by: each section file must
    contain content covering all the topics listed in the spec for that
    section (e.g., Product Info must cover name, manufacturer, model,
    dimensions, weight, materials, specs, package contents, certs).
14. DAT-005: The assembled Product Master must include content from ALL
    section artifacts. Verify by: check that each section's key topics
    appear in the final document.
15. DAT-006: Source attribution in the Product Master must reference
    actual files listed in the scan report. Verify by: cross-reference
    source citations in the Product Master against the scan report's
    file inventory.
16. DAT-007: For incremental updates, the Changelog must accurately
    reflect what changed between the old and new Product Master. Verify
    by: compare old PRODUCT_MASTER_FILE input against the new output
    and check that the Changelog entries match the differences.
17. DAT-008: Slug extraction must produce consistent naming across all
    artifacts. Verify by: all output filenames must use the same slug
    value derived from PRODUCT_SOURCE_DIR's directory name.
18. DAT-009: Sequence numbers in PRODUCT_MASTER_FILE must auto-increment
    correctly. Verify by: if a prior PRODUCT_MASTER_FILE exists in the
    same directory, the new one must have a higher sequence number.
19. DAT-010: The workflow must handle partial failure gracefully. If
    some source files are unreadable (corrupt PDFs, broken URLs), the
    scan report should note them and section generation should proceed
    with available sources, noting gaps.

### 7.3 Security Audit

The spec does not involve API keys, authentication, credentials, or
secrets. The workflow operates entirely on local filesystem inputs and
LLM prompt-driven generation. No external API calls are made by the
custom action (scan_product_inputs only scans local files).

However, the following criteria apply to URL handling:

20. SEC-001: When processing URL files (url_list source type), the
    prompts must instruct the LLM to use the webfetch tool (or
    equivalent) to retrieve URL content. The LLM must not execute
    arbitrary URLs as code.
21. SEC-002: The scan_product_inputs action must not execute or
    interpret any file contents -- it only classifies by extension
    and filename pattern. No file content is processed at the action
    level.
22. SEC-003: No credentials, API keys, or tokens should appear in
    any generated artifact or log output. The workflow has no
    authentication requirements.

### 7.4 No Additional Audit Required

The spec does not involve:
- Payment processing or financial data
- Personally identifiable information (PII) handling
- Database write operations
- Concurrent file access or locking requirements

These areas do not require additional audit criteria for this workflow.


## Appendix A: Expected Workflow Structure Summary

The following table summarizes the expected workflow structure for
reference during validation:

| Step | Type | Role Policy | Produces | Routes To |
|---|---|---|---|---|
| scan_product_inputs | action | -- | SCAN_REPORT_FILE | first section gen |
| generate_product_info | prompt | architect_standard | PRODUCT_INFO_FILE | next section |
| generate_target_audience | prompt | architect_standard | TARGET_AUDIENCE_FILE | next section |
| generate_product_benefits | prompt | architect_standard | PRODUCT_BENEFITS_FILE | next section |
| generate_marketing_assets | prompt | architect_standard | MARKETING_ASSETS_FILE | next section |
| generate_additional_sections | prompt | architect_standard | ADDITIONAL_SECTIONS_FILE | assemble |
| assemble_product_master | prompt | architect_standard | PRODUCT_MASTER_FILE | review |
| review_product_master | prompt | reviewer_standard | REVIEW_FILE_SUGGESTED | promote (or refine) |
| refine_product_master | prompt | architect_standard | PRODUCT_MASTER_FILE | review (loop) |
| promote (optional) | action | -- | -- | stepCompletion |
| stepCompletion | action | -- | -- | terminal |

Note: The workflow builder has discretion over exact step decomposition.
The criteria above verify semantic correctness regardless of whether
section generation steps are separate or combined, as long as all
required outputs are produced.


## Appendix B: Verification Quick Reference

To verify a criterion, use the following approach:

- PKG-xxx: Read the generated workflow package files directly.
- VAL-xxx: Run structural checks on workflow.toml and cross-reference
  with context_extensions.py and actions.py.
- REV-xxx: Trace data flow through workflow.toml step definitions and
  verify against spec requirements.
- PQ-xxx: Read each prompt file and check for clarity, completeness,
  and ambiguity guards.
- LOG-xxx: Read actions.py for error handling logic. Read workflow.toml
  for loop/routing configuration.
- DAT-xxx: Trace artifact paths and naming patterns through
  context_extensions.py. Check scan report logic in actions.py.
- SEC-xxx: Verify no credentials appear in any generated file.
