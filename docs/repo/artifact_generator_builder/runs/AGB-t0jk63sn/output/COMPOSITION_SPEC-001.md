---
doc_type: "composition_spec"
identity_locked: true
generator_name: "text_summarizer"
version: "1.0.0"
spec_version: "1.0.0"
source_requirement_analysis: "REQUIREMENT_ANALYSIS-001"
source_requirement_doc: "simple_text_summarizer.md"
composed_at: "2026-08-10"
---

# Composition Specification

## 1. Overview

This document defines the composition specification for the text_summarizer
artifact generator. It specifies the intermediate meta schema, input/output
mappings, transformation rules, and extension mechanisms.

The specification follows the three-layer architecture defined in
COMPOSITION_SYSTEM_STANDARD.md:

- Layer 1 (Content Components): Standardized building blocks extracted from input
- Layer 2 (Composition Definitions): Declarative rules for selecting and assembling components
- Layer 3 (Resolved Outputs): The final generated summary

### Traceability

| Element | Source | Trace ID |
|---------|--------|----------|
| Generator identity | REQUIREMENT_DOC frontmatter | TRACE-ID-001 |
| Input specification | REQUIREMENT_ANALYSIS Input Artifacts table | TRACE-ID-002 |
| Output specification | REQUIREMENT_ANALYSIS Output Artifacts table | TRACE-ID-003 |
| Transformation steps | REQUIREMENT_ANALYSIS TR-001 through TR-010 | TRACE-ID-004 |
| Constraints | REQUIREMENT_ANALYSIS CON-001 through CON-003 | TRACE-ID-005 |
| Extension points | REQUIREMENT_ANALYSIS EXT-001 through EXT-004 | TRACE-ID-006 |
| Three-layer architecture | COMPOSITION_SYSTEM_STANDARD.md Sections 2-5 | TRACE-ID-007 |

---

## 2. Meta Schema Definition

The meta schema defines the intermediate representation between input parsing
and output generation. It is organized into three layers following the
composition system standard.

### 2.1 Layer 1: Content Components

Content components represent the structured decomposition of the input text.

#### 2.1.1 Component: DocumentMeta

Top-level metadata about the source document.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "doc-meta-001" |
| component_type | enum | Yes | Fixed value: "document_meta" |
| source_format | enum | Yes | "txt" or "md" |
| source_language | string | Yes | ISO 639-1 language code detected from content |
| original_word_count | integer | Yes | Total word count of the input text |
| section_count | integer | Yes | Number of top-level sections detected |
| encoding | string | Yes | Character encoding (default: "utf-8") |
| has_frontmatter | boolean | No | Whether input contains YAML frontmatter |

#### 2.1.2 Component: Section

A logical section of the document, identified by heading markers or paragraph grouping.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "sec-{index}" |
| component_type | enum | Yes | Fixed value: "section" |
| heading | string | No | Section heading text (empty for unheaded sections) |
| heading_level | integer | No | Heading depth (1-6 for Markdown; 0 for unheaded) |
| position | integer | Yes | Ordinal position in document (1-indexed) |
| paragraph_ids | array[string] | Yes | Ordered list of paragraph component_ids within this section |
| word_count | integer | Yes | Word count of all paragraphs in this section |

#### 2.1.3 Component: Paragraph

A paragraph of text within a section.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "para-{section_index}-{para_index}" |
| component_type | enum | Yes | Fixed value: "paragraph" |
| parent_section_id | string | Yes | component_id of the containing Section |
| position | integer | Yes | Ordinal position within the section (1-indexed) |
| raw_text | string | Yes | Original text content of the paragraph |
| sentence_ids | array[string] | Yes | Ordered list of sentence component_ids |
| word_count | integer | Yes | Word count of this paragraph |

#### 2.1.4 Component: Sentence

An individual sentence within a paragraph.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "s-{section}-{para}-{sent}" |
| component_type | enum | Yes | Fixed value: "sentence" |
| parent_paragraph_id | string | Yes | component_id of the containing Paragraph |
| position | integer | Yes | Ordinal position within the paragraph (1-indexed) |
| raw_text | string | Yes | Original sentence text |
| word_count | integer | Yes | Word count of this sentence |
| is_heading | boolean | No | True if sentence functions as a heading/title |
| is_list_item | boolean | No | True if sentence is a list/bullet item |

### 2.2 Layer 2: Composition Components

Composition components represent the intermediate analysis results used to
assemble the summary.

#### 2.2.1 Component: KeyPoint

An extracted key point from the source content.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "kp-{index}" |
| component_type | enum | Yes | Fixed value: "key_point" |
| source_sentence_ids | array[string] | Yes | component_ids of source sentences |
| source_section_id | string | Yes | component_id of the originating section |
| extracted_text | string | Yes | The key point text (may be original or rephrased) |
| importance_score | float | Yes | Score from 0.0 to 1.0 indicating importance |
| redundancy_group | string | No | Group identifier for redundant key points |
| is_core_message | boolean | Yes | True if this key point captures the core message |
| structural_role | enum | Yes | One of: "intro", "main_point", "conclusion" |

#### 2.2.2 Component: RedundancyCluster

A group of redundant or overlapping key points.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "rc-{index}" |
| component_type | enum | Yes | Fixed value: "redundancy_cluster" |
| key_point_ids | array[string] | Yes | component_ids of key points in this cluster |
| representative_key_point_id | string | Yes | component_id of the selected representative |
| similarity_score | float | Yes | Average pairwise similarity (0.0 to 1.0) |

#### 2.2.3 Component: SummaryBlock

A block of summary content assigned to a structural role.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "sb-{index}" |
| component_type | enum | Yes | Fixed value: "summary_block" |
| structural_role | enum | Yes | One of: "intro", "main_point", "conclusion" |
| source_key_point_ids | array[string] | Yes | component_ids of key points contributing to this block |
| content_text | string | Yes | The rendered text for this block |
| word_count | integer | Yes | Word count of content_text |
| position | integer | Yes | Ordinal position within its structural role group |

### 2.3 Layer 3: Output Components

Output components represent the final assembled summary.

#### 2.3.1 Component: SummaryDocument

The complete summary document.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "summary-doc-001" |
| component_type | enum | Yes | Fixed value: "summary_document" |
| output_format | enum | Yes | "txt" or "md" (matches input format per ASM-005) |
| target_language | string | Yes | Must match source_language (CON-002) |
| summary_word_count | integer | Yes | Total word count of the summary |
| original_word_count | integer | Yes | Word count of the original input |
| compression_ratio | float | Yes | summary_word_count / original_word_count |
| intro_blocks | array[string] | Yes | Ordered component_ids of intro SummaryBlocks |
| main_point_blocks | array[string] | Yes | Ordered component_ids of main_point SummaryBlocks |
| conclusion_blocks | array[string] | Yes | Ordered component_ids of conclusion SummaryBlocks |
| generation_timestamp | string | Yes | ISO 8601 timestamp of generation |

#### 2.3.2 Component: ValidationRecord

A record of validation checks performed on the output.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier: "valrec-{index}" |
| component_type | enum | Yes | Fixed value: "validation_record" |
| constraint_id | string | Yes | Reference to constraint (e.g., "CON-001") |
| check_description | string | Yes | Human-readable description of the check |
| passed | boolean | Yes | True if the constraint is satisfied |
| measured_value | string | No | The actual measured value |
| threshold_value | string | No | The constraint threshold |

### 2.4 Component Relationships

The meta schema components form a hierarchical graph:

```
DocumentMeta
  |
  +-- Section (1..N)
        |
        +-- Paragraph (1..N)
              |
              +-- Sentence (1..N)

KeyPoint (derived from Sentence, grouped by Section)
  |
  +-- RedundancyCluster (groups overlapping KeyPoints)

SummaryBlock (assembled from KeyPoints)
  |
  +-- SummaryDocument (contains ordered SummaryBlocks)
        |
        +-- ValidationRecord (validates SummaryDocument)
```

### 2.5 Component Validation Rules

| Rule ID | Component Type | Rule | Severity |
|---------|---------------|------|----------|
| VR-001 | All | component_id must be unique across all components | Error |
| VR-002 | All | component_type must be a recognized type | Error |
| VR-003 | DocumentMeta | source_format must be "txt" or "md" | Error |
| VR-004 | DocumentMeta | original_word_count must be greater than 0 | Error |
| VR-005 | Section | position must be sequential starting from 1 | Error |
| VR-006 | Paragraph | parent_section_id must reference an existing Section | Error |
| VR-007 | Sentence | parent_paragraph_id must reference an existing Paragraph | Error |
| VR-008 | KeyPoint | importance_score must be between 0.0 and 1.0 | Error |
| VR-009 | KeyPoint | structural_role must be "intro", "main_point", or "conclusion" | Error |
| VR-010 | SummaryDocument | compression_ratio must be at most 0.20 (CON-001) | Error |
| VR-011 | SummaryDocument | target_language must match DocumentMeta.source_language (CON-002) | Error |
| VR-012 | SummaryBlock | structural_role must match the block category (intro/main_point/conclusion) | Error |

---

## 3. Input Mapping

Defines how input artifacts map to the meta schema Layer 1 (Content Components).

### 3.1 Input Source

| Input Artifact | Mapping Target | Method |
|----------------|---------------|--------|
| INPUT_TEXT_FILE | DocumentMeta + Section[] + Paragraph[] + Sentence[] | Parse and decompose |

### 3.2 Parsing Procedure

#### 3.2.1 Step INM-001: Detect Format

Read the file extension of INPUT_TEXT_FILE.

| Condition | Result |
|-----------|--------|
| Extension is ".txt" | source_format = "txt" |
| Extension is ".md" | source_format = "md" |
| Other extension | Error: unsupported format (violates FMT-001) |

#### 3.2.2 Step INM-002: Detect Frontmatter

If source_format is "md", check for YAML frontmatter (content between "---" delimiters at file start).

| Condition | Result |
|-----------|--------|
| Frontmatter present | has_frontmatter = true; exclude frontmatter from content parsing |
| No frontmatter | has_frontmatter = false |

#### 3.2.3 Step INM-003: Detect Language

Analyze the text content to determine the primary language.

| Method | Result |
|--------|--------|
| Language detection algorithm | source_language = ISO 639-1 code (e.g., "en", "zh", "fr") |

#### 3.2.4 Step INM-004: Segment into Sections

Decompose the text into Sections based on format-specific rules.

| Format | Section Detection Rule |
|--------|----------------------|
| md | Split on heading markers (# through ######) |
| txt | Split on double-newline boundaries if no headings present; each group becomes one section |

Create a DocumentMeta component with:
- section_count = number of sections detected
- encoding = "utf-8"

#### 3.2.5 Step INM-005: Segment Sections into Paragraphs

Within each Section, split on paragraph boundaries (double newline or blank line).

For each Paragraph, create a component with:
- parent_section_id = component_id of the containing Section
- raw_text = paragraph text content
- position = sequential index within section

#### 3.2.6 Step INM-006: Segment Paragraphs into Sentences

Within each Paragraph, split on sentence boundaries (period, exclamation mark, question mark followed by space or end of text).

For each Sentence, create a component with:
- parent_paragraph_id = component_id of the containing Paragraph
- raw_text = sentence text
- is_heading = true if sentence matches heading pattern
- is_list_item = true if sentence starts with bullet/number marker

#### 3.2.7 Step INM-007: Compute Word Counts

For each component that has a word_count property, count the words in its text content.
Propagate word counts upward:
- Section.word_count = sum of Paragraph.word_count values
- DocumentMeta.original_word_count = sum of Section.word_count values

### 3.3 Input Validation Rules

| Rule ID | Validation | Error Condition | Trace |
|---------|-----------|-----------------|-------|
| INV-001 | File exists and is readable | File not found or permission denied | FMT-001 |
| INV-002 | File extension is .txt or .md | Unsupported format | FMT-001 |
| INV-003 | Content is non-empty after frontmatter removal | Empty input | ASM-001 |
| INV-004 | Content appears to be natural language | Binary or code-only content | REQUIREMENT_ANALYSIS validation |
| INV-005 | At least one Section detected | Unable to segment | Parsing failure |
| INV-006 | At least one Sentence detected | Unable to decompose | Parsing failure |

---

## 4. Output Mapping

Defines how meta schema Layer 3 (Output Components) maps to output artifacts.

### 4.1 Output Target

| Meta Component | Output Artifact | Method |
|----------------|----------------|--------|
| SummaryDocument | SUMMARY_FILE | Render and write |
| ValidationRecord[] | SUMMARY_FILE (inline or appended) | Include validation results |

### 4.2 Rendering Procedure

#### 4.2.1 Step OUTM-001: Determine Output Format

| Condition | Result |
|-----------|--------|
| DocumentMeta.source_format is "md" | output_format = "md" |
| DocumentMeta.source_format is "txt" | output_format = "txt" |

Trace: ASM-005 (output format follows input format)

#### 4.2.2 Step OUTM-002: Assemble Summary Sections

Construct the summary text by concatenating SummaryBlocks in structural order:

1. Intro blocks (ordered by position)
2. Main point blocks (ordered by position)
3. Conclusion blocks (ordered by position)

Separate each block with appropriate formatting:
- For "md" format: use heading markers and paragraph breaks
- For "txt" format: use blank lines between sections

#### 4.2.3 Step OUTM-003: Add Summary Metadata

If output_format is "md", prepend a metadata header:

```
Summary ({compression_ratio*100}% of original)
Language: {target_language}
```

If output_format is "txt", prepend a plain text header:

```
Summary (approximately {compression_ratio*100}% of original)
```

#### 4.2.4 Step OUTM-004: Write Output File

Write the assembled text to the SUMMARY_FILE artifact path using UTF-8 encoding.

### 4.3 Output Validation Rules

| Rule ID | Validation | Error Condition | Trace |
|---------|-----------|-----------------|-------|
| OV-001 | SUMMARY_FILE exists and is readable | Write failure | FMT-002 |
| OV-002 | summary_word_count <= 0.20 * original_word_count | Exceeds 20% limit | CON-001 |
| OV-003 | target_language matches source_language | Language mismatch | CON-002 |
| OV-004 | Summary contains no information not in source | Hallucination detected | CON-003 |
| OV-005 | Summary contains intro, main_point, and conclusion blocks | Missing structural element | FMT-003 |
| OV-006 | Summary is coherent and readable | Structural integrity failure | SUMMARY-QR-005 |

---

## 5. Transformation Rules

Defines the core logic that transforms Layer 1 (Content Components) into
Layer 2 (Composition Components) and then into Layer 3 (Output Components).

### 5.1 Transformation Pipeline

The transformation follows a linear pipeline with 10 stages, each
corresponding to a transformation step from the requirement analysis.

```
Stage 1: Read Input       -> DocumentMeta + Content Components
Stage 2: Segment Content  -> Validate Section/Paragraph/Sentence hierarchy
Stage 3: Identify Key     -> KeyPoint[] with importance scores
         Points
Stage 4: Remove           -> RedundancyCluster[] + deduplicated KeyPoint[]
         Redundancy
Stage 5: Preserve         -> Verify is_core_message coverage
         Meaning
Stage 6: Compress         -> Select KeyPoints to meet 20% target
Stage 7: Maintain         -> SummaryBlock[] assigned to structural roles
         Structure
Stage 8: Validate         -> Check target_language == source_language
         Language
Stage 9: Validate         -> Check compression_ratio <= 0.20
         Length
Stage 10: Write Output    -> SummaryDocument -> SUMMARY_FILE
```

### 5.2 Stage Definitions

#### 5.2.1 Stage 1: Read Input (TR-001)

**Input:** INPUT_TEXT_FILE path
**Output:** DocumentMeta component
**Side effect:** Populates Layer 1 content components

**Logic:**
1. Execute Input Mapping steps INM-001 through INM-007
2. Create DocumentMeta with all detected properties
3. Create Section, Paragraph, Sentence components for all content

**Invariant:** DocumentMeta.original_word_count equals the sum of all Sentence.word_count values.

#### 5.2.2 Stage 2: Segment Content (TR-002)

**Input:** Content Components from Stage 1
**Output:** Validated component hierarchy
**Side effect:** None

**Logic:**
1. Verify Section hierarchy: each Section has at least one Paragraph
2. Verify Paragraph hierarchy: each Paragraph has at least one Sentence
3. Verify ordering: positions are sequential within each parent

**Invariant:** Every Sentence belongs to exactly one Paragraph. Every Paragraph belongs to exactly one Section.

#### 5.2.3 Stage 3: Identify Key Points (TR-003)

**Input:** Sentence components
**Output:** KeyPoint components with importance_score values
**Side effect:** None

**Logic:**
1. For each Sentence, compute an importance score based on:
   - Position in document (first and last sentences score higher)
   - Position in section (first sentence of section scores higher)
   - Contains heading-like patterns (e.g., "In conclusion", "The main point")
   - Sentence length (moderate-length sentences preferred)
   - Semantic significance indicators (defined per language)
2. Select sentences exceeding an importance threshold as KeyPoints
3. Assign structural_role based on position:
   - First section, first key point -> "intro"
   - Last section, last key point -> "conclusion"
   - All others -> "main_point"
4. Mark the highest-scoring key point as is_core_message = true

**Invariant:** At least one KeyPoint has is_core_message = true. At least one KeyPoint exists for each structural_role.

#### 5.2.4 Stage 4: Remove Redundancy (TR-004)

**Input:** KeyPoint components
**Output:** RedundancyCluster components + deduplicated KeyPoint set
**Side effect:** None

**Logic:**
1. Compute pairwise similarity between all KeyPoint extracted_text values
2. Group KeyPoints with similarity above a threshold into RedundancyClusters
3. For each cluster, select the representative (highest importance_score)
4. Mark non-representative key points as redundant

**Invariant:** Every KeyPoint belongs to at most one RedundancyCluster. Each cluster has exactly one representative.

#### 5.2.5 Stage 5: Preserve Meaning (TR-005)

**Input:** Deduplicated KeyPoints
**Output:** Validated KeyPoint set with meaning coverage confirmed
**Side effect:** None

**Logic:**
1. Verify that the representative KeyPoints from each RedundancyCluster
   collectively cover all sections present in the source
2. If any section has no surviving KeyPoint, promote the highest-scoring
   redundant KeyPoint from that section
3. Confirm is_core_message KeyPoint is still present

**Invariant:** Every Section with at least one Sentence has at least one contributing KeyPoint.

#### 5.2.6 Stage 6: Compress (TR-006)

**Input:** Validated KeyPoints
**Output:** Selected KeyPoints meeting compression target
**Side effect:** None

**Logic:**
1. Calculate total word count of all selected KeyPoint extracted_text values
2. If total exceeds 20% of original_word_count:
   a. Sort KeyPoints by importance_score descending
   b. Greedily select KeyPoints until adding the next would exceed the budget
   c. Ensure at least one KeyPoint per structural_role is retained
3. If total is below target, the summary may be shorter than 20% (acceptable)

**Invariant:** Sum of selected KeyPoint word counts <= 0.20 * original_word_count.
**Invariant:** At least one KeyPoint with structural_role "intro" is selected.
**Invariant:** At least one KeyPoint with structural_role "main_point" is selected.
**Invariant:** At least one KeyPoint with structural_role "conclusion" is selected.

#### 5.2.7 Stage 7: Maintain Structure (TR-007)

**Input:** Selected KeyPoints
**Output:** SummaryBlock components
**Side effect:** None

**Logic:**
1. Group selected KeyPoints by structural_role
2. Within each group, order KeyPoints by their original position in the source
3. For each group, create SummaryBlock(s):
   - Concatenate or synthesize KeyPoint extracted_text values into coherent prose
   - Assign structural_role matching the group
   - Set position = sequential index within the group
4. If a group has multiple key points, they may form one SummaryBlock or
   multiple SummaryBlocks depending on content coherence

**Invariant:** SummaryBlocks preserve the order: intro blocks appear before main_point blocks, which appear before conclusion blocks.

#### 5.2.8 Stage 8: Validate Language (TR-008)

**Input:** SummaryBlocks
**Output:** ValidationRecord for CON-002
**Side effect:** None

**Logic:**
1. Detect the language of the combined SummaryBlock content
2. Compare with DocumentMeta.source_language
3. Create ValidationRecord:
   - constraint_id = "CON-002"
   - passed = (detected_language == source_language)
   - measured_value = detected_language
   - threshold_value = source_language

**Invariant:** ValidationRecord.passed must be true. If false, transformation must halt.

#### 5.2.9 Stage 9: Validate Length (TR-009)

**Input:** SummaryBlocks
**Output:** ValidationRecord for CON-001
**Side effect:** None

**Logic:**
1. Calculate summary_word_count = sum of all SummaryBlock.word_count values
2. Calculate compression_ratio = summary_word_count / original_word_count
3. Create ValidationRecord:
   - constraint_id = "CON-001"
   - passed = (compression_ratio <= 0.20)
   - measured_value = str(compression_ratio)
   - threshold_value = "0.20"

**Invariant:** ValidationRecord.passed must be true. If false, return to Stage 6 and reduce selection.

#### 5.2.10 Stage 10: Write Output (TR-010)

**Input:** SummaryBlocks + ValidationRecords
**Output:** SummaryDocument component + SUMMARY_FILE
**Side effect:** Writes file to disk

**Logic:**
1. Execute Output Mapping steps OUTM-001 through OUTM-004
2. Create SummaryDocument component with all references
3. Attach ValidationRecords to the SummaryDocument

**Invariant:** SUMMARY_FILE exists on disk. SummaryDocument.compression_ratio <= 0.20.

### 5.3 Transformation Invariants Summary

| Invariant ID | Stage | Invariant | Trace |
|-------------|-------|-----------|-------|
| INV-T-001 | All | Every Sentence belongs to exactly one Paragraph | TR-002 |
| INV-T-002 | All | Every Paragraph belongs to exactly one Section | TR-002 |
| INV-T-003 | Stage 3 | At least one KeyPoint has is_core_message = true | TR-003 |
| INV-T-004 | Stage 3 | At least one KeyPoint per structural_role exists | TR-003 |
| INV-T-005 | Stage 4 | Every KeyPoint belongs to at most one RedundancyCluster | TR-004 |
| INV-T-006 | Stage 5 | Every Section with content has at least one contributing KeyPoint | TR-005 |
| INV-T-007 | Stage 6 | Sum of selected KeyPoint words <= 0.20 * original_word_count | TR-006, CON-001 |
| INV-T-008 | Stage 7 | SummaryBlocks preserve intro -> main_point -> conclusion order | TR-007, FMT-003 |
| INV-T-009 | Stage 8 | Output language matches input language | TR-008, CON-002 |
| INV-T-010 | Stage 9 | Compression ratio <= 0.20 | TR-009, CON-001 |
| INV-T-011 | Stage 10 | SUMMARY_FILE exists and is valid | TR-010, FMT-002 |

---

## 6. Extension Mechanism

Defines how the composition specification supports new output types and
runtime implementations without modifying the core meta schema.

### 6.1 Fixed vs Variable Parts

#### 6.1.1 Fixed Parts (Core Contract)

The following elements are fixed and must not change across implementations:

| Element | Scope | Rationale |
|---------|-------|-----------|
| Layer 1 component types | document_meta, section, paragraph, sentence | Input parsing contract |
| Layer 1 component properties | All required properties defined in Section 2.1 | Downstream dependency |
| Component validation rules | VR-001 through VR-012 | Schema integrity |
| Input validation rules | INV-001 through INV-006 | Input contract |
| Stage pipeline order | Stages 1-10 must execute in sequence | Dependency chain |
| Core invariants | INV-T-001 through INV-T-011 | Correctness guarantees |
| CON-001 (20% compression) | Hard constraint | Requirement document |
| CON-002 (same language) | Hard constraint | Requirement document |
| CON-003 (no new information) | Hard constraint | Requirement document |

#### 6.1.2 Variable Parts (Extension Points)

The following elements are designed for extension:

| Element | Extension Type | Reference |
|---------|---------------|-----------|
| Output format rendering | Strategy pattern | EXT-004, VAR-004 |
| Importance scoring algorithm | Pluggable scorer | Stage 3 |
| Redundancy detection algorithm | Pluggable detector | Stage 4 |
| Key point selection strategy | Pluggable selector | Stage 6 |
| Structural role assignment | Configurable rules | Stage 3 |
| Additional output types | New output component types | EXT-001 to EXT-004 |
| Compression ratio target | Configurable parameter | VAR-001 |

### 6.2 Extension Point Contracts

#### 6.2.1 Output Renderer Contract

An output renderer transforms Layer 3 Output Components into a file artifact.

**Required interface:**

```
OutputRenderer:
  - supported_formats: list[string]
  - render(summary_document: SummaryDocument, 
           blocks: list[SummaryBlock]) -> string
```

**Contract rules:**
1. Must accept a valid SummaryDocument and its associated SummaryBlocks
2. Must return a string suitable for writing to disk
3. Must not modify the input components
4. Must respect the target_language and output_format properties
5. Must produce output that passes all output validation rules (OV-001 to OV-006)

**Built-in renderers:**
- TextRenderer: produces plain text output (output_format = "txt")
- MarkdownRenderer: produces Markdown output (output_format = "md")

**Extension example (VAR-004):**
- JSONRenderer: produces structured JSON output
- YAMLRenderer: produces YAML output

#### 6.2.2 Importance Scorer Contract

An importance scorer assigns importance_score values to Sentence components.

**Required interface:**

```
ImportanceScorer:
  - score(sentences: list[Sentence], 
           document_meta: DocumentMeta) -> list[float]
```

**Contract rules:**
1. Must accept a list of Sentence components and the DocumentMeta
2. Must return a list of floats (0.0 to 1.0) in the same order as input sentences
3. Must not modify the input components
4. Scores must be deterministic for the same input

#### 6.2.3 Redundancy Detector Contract

A redundancy detector groups similar KeyPoints into clusters.

**Required interface:**

```
RedundancyDetector:
  - detect(key_points: list[KeyPoint], 
           threshold: float) -> list[RedundancyCluster]
```

**Contract rules:**
1. Must accept a list of KeyPoint components and a similarity threshold
2. Must return a list of RedundancyCluster components
3. Each KeyPoint must appear in at most one cluster
4. Each cluster must have exactly one representative_key_point_id

#### 6.2.4 Compression Selector Contract

A compression selector chooses which KeyPoints to include in the summary.

**Required interface:**

```
CompressionSelector:
  - select(key_points: list[KeyPoint], 
           target_ratio: float, 
           original_word_count: int) -> list[KeyPoint]
```

**Contract rules:**
1. Must accept KeyPoints, a target compression ratio, and the original word count
2. Must return a subset of the input KeyPoints
3. The returned subset must satisfy INV-T-007 (total words <= target)
4. The returned subset must include at least one KeyPoint per structural_role
5. Must preserve the relative ordering of selected KeyPoints

### 6.3 Adding New Output Types

To support the extension points identified in the requirement analysis:

#### 6.3.1 Bullet-point Summary (EXT-001)

**New components required:**
- BulletPoint (Layer 3): A single bullet point in the output
- BulletListDocument (Layer 3): Collection of bullet points

**Changes:**
- Add new Output Renderer: BulletListRenderer
- Modify Stage 7 to produce BulletPoint components instead of prose SummaryBlocks
- Add new output validation rules for bullet list format

**No changes to:** Layer 1 components, Stages 1-6, core invariants

#### 6.3.2 Executive Summary (EXT-002)

**New components required:**
- None (reuse existing SummaryDocument)

**Changes:**
- Configurable target_ratio parameter (default 0.05 instead of 0.20)
- Modified compression threshold in Stage 6

**No changes to:** Layer 1 or Layer 2 components, Stages 1-5, Stage 7-10 logic

#### 6.3.3 Key Phrases Extraction (EXT-003)

**New components required:**
- KeyPhrase (Layer 2): A standalone key phrase (shorter than KeyPoint)
- KeyPhraseList (Layer 3): Ordered list of key phrases

**Changes:**
- Add new Stage 3 variant: phrase extraction instead of sentence scoring
- Add new Output Renderer: KeyPhraseListRenderer
- New output validation rules for phrase format

**No changes to:** Layer 1 components, core invariants

#### 6.3.4 Section-by-Section Summary (EXT-004)

**New components required:**
- SectionSummary (Layer 3): Per-section summary block
- SectionedSummaryDocument (Layer 3): Collection preserving original section order

**Changes:**
- Modify Stage 7 to group KeyPoints by source_section_id instead of structural_role
- Add new Output Renderer: SectionedRenderer
- New output validation for section structure preservation

**No changes to:** Layer 1 components, Stages 1-6

### 6.4 Runtime Implementation Plug-in Contract

A runtime implementation must provide:

| Interface | Required | Description |
|-----------|----------|-------------|
| InputParser | Yes | Implements Input Mapping (INM-001 to INM-007) |
| ImportanceScorer | Yes | Implements Stage 3 scoring |
| RedundancyDetector | Yes | Implements Stage 4 clustering |
| CompressionSelector | Yes | Implements Stage 6 selection |
| StructureMaintainer | Yes | Implements Stage 7 assembly |
| OutputRenderer | Yes | Implements Output Mapping (OUTM-001 to OUTM-004) |

Each interface must:
1. Accept the meta schema components as defined in Section 2
2. Return components conforming to the defined schemas
3. Maintain all invariants for its stage
4. Be independently testable

---

## 7. Self-Validation

### 7.1 Completeness Check

| Check ID | Check | Status | Evidence |
|----------|-------|--------|----------|
| SC-001 | Meta schema defines all component types | PASS | 9 component types across 3 layers: document_meta, section, paragraph, sentence, key_point, redundancy_cluster, summary_block, summary_document, validation_record |
| SC-002 | Every component type has required properties defined | PASS | Section 2.1-2.3 define all properties with types and required flags |
| SC-003 | Component relationships are explicitly documented | PASS | Section 2.4 defines hierarchical graph |
| SC-004 | Input mapping covers all transformation steps from input | PASS | Section 3.2 defines INM-001 through INM-007, mapping to TR-001 and TR-002 |
| SC-005 | Output mapping covers all generation steps | PASS | Section 4.2 defines OUTM-001 through OUTM-004, mapping to TR-010 |
| SC-006 | Transformation rules cover all TR steps | PASS | Section 5.2 defines Stages 1-10 mapping to TR-001 through TR-010 |
| SC-007 | All constraints are enforced | PASS | CON-001 in Stage 9 (INV-T-010), CON-002 in Stage 8 (INV-T-009), CON-003 in Stage 5 (INV-T-006) |
| SC-008 | Extension mechanism is defined | PASS | Section 6 defines 4 plug-in contracts and 4 extension examples |
| SC-009 | Validation rules are defined for all layers | PASS | VR-001 to VR-012 (meta), INV-001 to INV-006 (input), OV-001 to OV-006 (output) |
| SC-010 | Invariants are defined for all stages | PASS | INV-T-001 to INV-T-011 cover all 10 stages |

### 7.2 Consistency Check

| Check ID | Check | Status | Evidence |
|----------|-------|--------|----------|
| CC-001 | No contradictions between input mapping and transformation rules | PASS | Input mapping produces content components; transformation stages consume them in order |
| CC-002 | No contradictions between transformation rules and output mapping | PASS | Stage 10 produces SummaryDocument; output mapping renders it |
| CC-003 | Component types referenced in relationships are all defined | PASS | All referenced types exist in Sections 2.1-2.3 |
| CC-004 | Validation rules reference valid constraint IDs | PASS | CON-001, CON-002, CON-003, FMT-001, FMT-002, FMT-003 all from REQUIREMENT_ANALYSIS |
| CC-005 | Extension points trace back to requirement analysis | PASS | EXT-001 to EXT-004, VAR-001 to VAR-004 from REQUIREMENT_ANALYSIS |
| CC-006 | No scope invention beyond input artifacts | PASS | All content traceable via TRACE-ID table in Section 1 |

### 7.3 Traceability Check

| Requirement Analysis Element | Composition Spec Location | Status |
|-----------------------------|--------------------------|--------|
| TR-001 (Read Input) | Section 5.2.1 (Stage 1) | Covered |
| TR-002 (Segment Content) | Section 5.2.2 (Stage 2) | Covered |
| TR-003 (Identify Key Points) | Section 5.2.3 (Stage 3) | Covered |
| TR-004 (Remove Redundancy) | Section 5.2.4 (Stage 4) | Covered |
| TR-005 (Preserve Meaning) | Section 5.2.5 (Stage 5) | Covered |
| TR-006 (Compress) | Section 5.2.6 (Stage 6) | Covered |
| TR-007 (Maintain Structure) | Section 5.2.7 (Stage 7) | Covered |
| TR-008 (Validate Language) | Section 5.2.8 (Stage 8) | Covered |
| TR-009 (Validate Length) | Section 5.2.9 (Stage 9) | Covered |
| TR-010 (Write Output) | Section 5.2.10 (Stage 10) | Covered |
| CON-001 (20% max) | Invariant INV-T-007, INV-T-010; Rule OV-002 | Covered |
| CON-002 (same language) | Invariant INV-T-009; Rule OV-003 | Covered |
| CON-003 (no new info) | Invariant INV-T-006; Rule OV-004 | Covered |
| FMT-001 (input format) | Input Mapping INM-001; Rule INV-002 | Covered |
| FMT-002 (output format) | Output Mapping OUTM-001; Rule OV-001 | Covered |
| FMT-003 (logical flow) | Stage 7; Invariant INV-T-008; Rule OV-005 | Covered |
| SUMMARY-QR-001 (word count) | Stage 9; Invariant INV-T-010 | Covered |
| SUMMARY-QR-002 (same language) | Stage 8; Invariant INV-T-009 | Covered |
| SUMMARY-QR-003 (no new info) | Stage 5; Invariant INV-T-006 | Covered |
| SUMMARY-QR-004 (core message) | Stage 3; Invariant INV-T-003 | Covered |
| SUMMARY-QR-005 (logical structure) | Stage 7; Invariant INV-T-008 | Covered |

### 7.4 Three-Layer Architecture Compliance

| Layer | Standard Reference | Implementation | Status |
|-------|-------------------|----------------|--------|
| Layer 1: Component Library | COMPOSITION_SYSTEM_STANDARD.md Section 3 | Section 2.1 (Content Components) | PASS |
| Layer 2: Composition Definitions | COMPOSITION_SYSTEM_STANDARD.md Section 4 | Section 2.2 (Composition Components) + Section 5 (Transformation Rules) | PASS |
| Layer 3: Resolved Outputs | COMPOSITION_SYSTEM_STANDARD.md Section 5 | Section 2.3 (Output Components) + Section 4 (Output Mapping) | PASS |

### 7.5 ASCII Compliance

| Check | Status |
|-------|--------|
| No em-dashes used | PASS |
| No curly quotes used | PASS |
| No Unicode characters used | PASS |
| YAML frontmatter uses plain ASCII | PASS |

---

## Appendix A: Meta Schema Quick Reference

### Component Type Registry

| component_type | Layer | Required Properties | Reference |
|---------------|-------|--------------------|-----------|
| document_meta | 1 | component_id, component_type, source_format, source_language, original_word_count, section_count, encoding | Section 2.1.1 |
| section | 1 | component_id, component_type, position, paragraph_ids, word_count | Section 2.1.2 |
| paragraph | 1 | component_id, component_type, parent_section_id, position, raw_text, sentence_ids, word_count | Section 2.1.3 |
| sentence | 1 | component_id, component_type, parent_paragraph_id, position, raw_text, word_count | Section 2.1.4 |
| key_point | 2 | component_id, component_type, source_sentence_ids, source_section_id, extracted_text, importance_score, is_core_message, structural_role | Section 2.2.1 |
| redundancy_cluster | 2 | component_id, component_type, key_point_ids, representative_key_point_id, similarity_score | Section 2.2.2 |
| summary_block | 2 | component_id, component_type, structural_role, source_key_point_ids, content_text, word_count, position | Section 2.2.3 |
| summary_document | 3 | component_id, component_type, output_format, target_language, summary_word_count, original_word_count, compression_ratio, intro_blocks, main_point_blocks, conclusion_blocks, generation_timestamp | Section 2.3.1 |
| validation_record | 3 | component_id, component_type, constraint_id, check_description, passed | Section 2.3.2 |

---

End of Composition Specification
