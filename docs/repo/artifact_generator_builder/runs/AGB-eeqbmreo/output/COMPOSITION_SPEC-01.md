---
doc_type: "composition_spec"
identity_locked: true
generator_name: "text_summarizer"
version: "1.0.0"
source_spec: "simple_text_summarizer.md"
spec_id: "CSPEC-001"
composed_at: "2026-08-10"
---

# Composition Specification: text_summarizer

## Document Metadata

| Field | Value |
|-------|-------|
| Spec ID | CSPEC-001 |
| Generator Name | text_summarizer |
| Version | 1.0.0 |
| Source Spec | simple_text_summarizer.md |
| Architecture Pattern | Input Transformation (Pattern 2) |
| Output-Type-Agnostic | Yes |

This document defines the transformation contract for the text_summarizer
artifact generator. It specifies the meta schema, input/output mappings,
transformation rules, invariants, constraints, and extension interfaces.
It is output-type-agnostic: multiple runtime implementations can satisfy
this spec to produce different output types (summary, bullet points, key
phrases, etc.).

Reference: COMPOSITION_SYSTEM_STANDARD.md, Section 13.


## Meta Schema Definition

The meta schema defines the intermediate representation used between input
parsing and output rendering. It follows the three-layer architecture
defined in the composition system standard: Layer 1 (Input Parsing),
Layer 2 (Transformation), and Layer 3 (Output Rendering).

### Layer 1 Components (Input Parsing)

Layer 1 decomposes raw input into a structured document model.

#### L1-DOC: DocumentStructure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| document_id | string | Yes | Unique identifier for the parsed document |
| source_artifact_key | string | Yes | Artifact key of the source input (e.g., INPUT_TEXT_FILE) |
| source_format | string | Yes | File format of the source (e.g., "txt", "md") |
| detected_language | string | Yes | ISO 639-1 language code of the input text |
| total_word_count | integer | Yes | Total word count of the input text |
| sections | array of L1-SEC | Yes | Ordered list of document sections |
| metadata | dict | No | Additional parsing metadata (encoding, line count, etc.) |

Traceability: Derived from V-IN-001 through V-IN-004.

#### L1-SEC: Section

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| section_id | string | Yes | Unique identifier within the document |
| section_type | enum | Yes | Type: "heading", "implicit" (no heading marker) |
| heading_text | string | No | The heading text, if section_type is "heading" |
| heading_level | integer | No | Heading depth (1-6), if applicable |
| position | integer | Yes | Ordinal position in the document (1-based) |
| paragraphs | array of L1-PAR | Yes | Ordered list of paragraphs in this section |

Traceability: Supports TR-004 (Maintain Structure).

#### L1-PAR: Paragraph

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| paragraph_id | string | Yes | Unique identifier within the document |
| position | integer | Yes | Ordinal position within its section |
| sentences | array of L1-SEN | Yes | Ordered list of sentences |
| word_count | integer | Yes | Word count of this paragraph |

#### L1-SEN: Sentence

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| sentence_id | string | Yes | Unique identifier within the document |
| position | integer | Yes | Ordinal position within its paragraph |
| text | string | Yes | The raw sentence text |
| word_count | integer | Yes | Word count of this sentence |

### Layer 2 Components (Transformation)

Layer 2 holds the results of analyzing, scoring, and transforming Layer 1
components. These represent the intermediate analytical state.

#### L2-KP: KeyPoint

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| keypoint_id | string | Yes | Unique identifier |
| source_sentence_ids | array of string | Yes | IDs of source sentences this keypoint derives from |
| importance_score | float | Yes | Normalized importance score (0.0 to 1.0) |
| consolidated_text | string | Yes | The text of this keypoint (may consolidate multiple sentences) |
| section_position | integer | Yes | Position of the originating section in the document |
| category | enum | Yes | Role: "intro", "main_point", "conclusion", "supporting" |

Traceability: Produced by TR-001 (Extract Key Points).

#### L2-RC: RedundancyCluster

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| cluster_id | string | Yes | Unique identifier |
| keypoint_ids | array of string | Yes | IDs of keypoints that express the same idea |
| representative_keypoint_id | string | Yes | The keypoint chosen to represent the cluster |
| redundancy_score | float | Yes | Degree of overlap (0.0 = no overlap, 1.0 = full duplication) |

Traceability: Produced by TR-002 (Remove Redundancy).

#### L2-CB: ContentBlock

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| block_id | string | Yes | Unique identifier |
| block_type | enum | Yes | Type: "intro", "main_body", "conclusion" |
| keypoint_ids | array of string | Yes | Ordered list of keypoints in this block |
| position | integer | Yes | Ordinal position in the output structure |

Traceability: Produced by TR-004 (Maintain Structure).

#### L2-SM: StructureMap

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| map_id | string | Yes | Unique identifier |
| source_document_id | string | Yes | Reference to the L1-DOC this was derived from |
| content_blocks | array of L2-CB | Yes | Ordered content blocks |
| total_keypoints | integer | Yes | Number of keypoints before redundancy removal |
| retained_keypoints | integer | Yes | Number of keypoints after redundancy removal |

Traceability: Aggregate view supporting all transformation requirements.

### Layer 3 Components (Output Rendering)

Layer 3 defines the generic output interface. It is output-type-agnostic.

#### L3-OD: OutputDocument (Interface)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| document_id | string | Yes | Unique identifier for the output |
| output_type | enum | Yes | Discriminator: "summary", "bullet_points", "key_phrases", etc. |
| structure_map_id | string | Yes | Reference to the L2-SM this was rendered from |
| content_blocks | array of L3-OB | Yes | Ordered output blocks |
| metadata | dict | Yes | Output metadata (see below) |
| validation_results | array | Yes | Results of post-rendering validation |

This interface is satisfied by different runtime implementations. The
output_type discriminator determines how content_blocks are structured
and what validation_rules apply.

#### L3-OB: OutputBlock

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| block_id | string | Yes | Unique identifier |
| block_type | enum | Yes | Matches L2-CB block_type or output-specific type |
| content | string | Yes | Rendered text content |
| source_keypoint_ids | array of string | Yes | Traceability to L2 keypoints |

#### L3-MD: OutputMetadata

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| source_word_count | integer | Yes | Word count of original input |
| output_word_count | integer | Yes | Word count of generated output |
| compression_ratio | float | Yes | output_word_count / source_word_count |
| language | string | Yes | Language of the output (must match input) |
| generator_version | string | Yes | Version of the generator that produced this |

Traceability: Supports C-001 (Length Constraint), C-002 (Language Fidelity).

### Component Relationships

```
L1-DOC 1:* L1-SEC 1:* L1-PAR 1:* L1-SEN
  |
  v (Input Parsing)
L2-KP (many-to-one with L1-SEN via source_sentence_ids)
  |
  v (Redundancy Removal)
L2-RC (many-to-many with L2-KP via keypoint_ids)
  |
  v (Structure Assembly)
L2-CB (one-to-many with L2-KP via keypoint_ids)
  |
  v (Aggregate)
L2-SM 1:* L2-CB
  |
  v (Output Rendering)
L3-OD 1:* L3-OB (via content_blocks)
L3-OD 1:1 L3-MD (via metadata)
```

All relationships are traceable via explicit ID references.


## Input Mapping

### Input Artifact to Layer 1 Mapping

| Input Artifact | Target Layer 1 Component | Mapping Method |
|----------------|--------------------------|----------------|
| INPUT_TEXT_FILE | L1-DOC | Parse entire file into DocumentStructure |
| File content (text) | L1-SEN | Tokenize into sentences |
| Paragraph breaks | L1-PAR | Split on blank lines or paragraph markers |
| Headings (if .md) | L1-SEC | Detect heading markers (#, ##, etc.) |
| File extension | L1-DOC.source_format | Read from artifact metadata |

### Parsing Rules

PR-001: Read the input file as UTF-8 text. If decoding fails, the input
is invalid per V-IN-004.

PR-002: Validate file extension is .txt or .md per V-IN-002.

PR-003: If the file has heading markers (e.g., Markdown headings), create
one L1-SEC per heading. If no headings are present, create a single
L1-SEC with section_type "implicit".

PR-004: Within each section, split text into L1-PAR components on paragraph
boundaries (blank lines).

PR-005: Within each paragraph, split text into L1-SEN components using
sentence boundary detection.

PR-006: Compute word_count for each L1-SEN, L1-PAR, L1-SEC, and L1-DOC
by counting whitespace-delimited tokens.

PR-007: Detect the language of the input text and set L1-DOC.detected_language.
The detection method is defined by the runtime implementation (extension
point IP-001).

### Input Validation Rules

| Rule ID | Constraint | Enforcement Point | Traceability |
|---------|------------|-------------------|--------------|
| IV-001 | File must exist and be readable | Before parsing | V-IN-001 |
| IV-002 | File extension must be .txt or .md | Before parsing | V-IN-002 |
| IV-003 | File must contain non-empty text | After parsing (total_word_count > 0) | V-IN-003 |
| IV-004 | File must be UTF-8 decodable | During parsing | V-IN-004 |
| IV-005 | At least one sentence must be parsed | After parsing | Derived from IV-003 |
| IV-006 | Sentence ordering must be consistent | After parsing | Structural integrity |

Validation failure at any point aborts the pipeline with a specific error
identifying the failing rule.


## Output Mapping

### Layer 3 to Output Artifact Mapping

| Layer 3 Component | Target Output Artifact | Mapping Method |
|-------------------|------------------------|----------------|
| L3-OD | SUMMARY_FILE (or other) | Render content_blocks to text |
| L3-OB | Output text sections | Concatenate block content with separators |
| L3-MD | Output metadata sidecar (optional) | Serialize metadata fields |

The specific output artifact key (SUMMARY_FILE, BULLET_POINT_FILE, etc.)
is determined by the runtime implementation's declared output_type.

### Rendering Rules

OR-001: Each L3-OB content field is rendered as a text segment.

OR-002: OutputBlocks are concatenated in order of their position field,
with appropriate separators defined by the output_type.

OR-003: For output_type "summary": blocks are joined as paragraphs with
blank-line separators, forming a continuous prose summary.

OR-004: For output_type "bullet_points": each block's content is rendered
as a bullet item with a list marker prefix.

OR-005: For output_type "key_phrases": content_blocks are rendered as a
delimited list of phrases.

OR-006: The rendered output must be written as a plain text file. The
file extension is determined by the runtime implementation.

OR-007: L3-MD.compression_ratio must be computed after rendering and
must satisfy constraint C-001.

### Output Validation Rules

| Rule ID | Constraint | Enforcement Point | Traceability |
|---------|------------|-------------------|--------------|
| OV-001 | Output word count > 0 | After rendering | Basic validity |
| OV-002 | compression_ratio <= 0.20 | After rendering | C-001 |
| OV-003 | output language matches input language | After rendering | C-002 |
| OV-004 | No content in output that cannot be traced to a source sentence | After rendering | C-003 |
| OV-005 | Output contains at least one intro block, one main_body block, and one conclusion block | After rendering | TR-004, Q-OUT-005 |
| OV-006 | All source_keypoint_ids in L3-OB reference valid L2-KP components | After rendering | Traceability integrity |
| OV-007 | All keypoint_ids in L2-CB reference valid L2-KP components | After rendering | Internal consistency |

Validation failure at any point triggers the refinement loop if configured,
or aborts with a specific error.


## Transformation Rules

### Layer 1 to Layer 2 Transformation

#### Stage T1: Key Point Extraction (TR-001)

Input: L1-DOC (all sentences)
Output: Array of L2-KP

Process:
1. For each L1-SEN, compute an importance_score based on the scoring
   algorithm (extension point TA-001).
2. Select sentences exceeding a relevance threshold as keypoints.
3. Each selected sentence becomes an L2-KP with:
   - source_sentence_ids = [sentence_id]
   - consolidated_text = sentence.text
   - category = determined by position (first section = "intro",
     last section = "conclusion", middle sections = "main_point"
     or "supporting")
4. Assign section_position from the parent L1-SEC.

Invariant T1-INV-001: Every L2-KP.source_sentence_ids references a
valid L1-SEN in the source L1-DOC.

Invariant T1-INV-002: The total_word_count of all selected keypoints
must not exceed the budget defined by C-001 (20% of source word count)
after redundancy removal.

Traceability: TR-001 from source specification and requirement analysis.

#### Stage T2: Redundancy Removal (TR-002)

Input: Array of L2-KP
Output: Array of L2-RC, pruned array of L2-KP

Process:
1. Cluster L2-KPs that express the same idea (semantic similarity
   above a threshold defined by the runtime implementation).
2. For each cluster (L2-RC), select the representative keypoint
   (highest importance_score within the cluster).
3. Remove non-representative keypoints from the active set.

Invariant T2-INV-001: Every L2-RC.keypoint_ids references valid L2-KP
components.

Invariant T2-INV-002: Every L2-KP belongs to exactly one L2-RC (either
a singleton cluster or a multi-member cluster).

Invariant T2-INV-003: The representative keypoint's consolidated_text
preserves the semantic content of the cluster.

Traceability: TR-002 from source specification and requirement analysis.

#### Stage T3: Structure Assembly (TR-004)

Input: Pruned array of L2-KP, L1-DOC structure
Output: Array of L2-CB, L2-SM

Process:
1. Group retained L2-KPs by their category into content blocks:
   - category "intro" -> L2-CB with block_type "intro"
   - category "main_point" and "supporting" -> L2-CB with block_type "main_body"
   - category "conclusion" -> L2-CB with block_type "conclusion"
2. Order keypoints within each block by section_position.
3. Order content blocks: intro (position=1), main_body (position=2),
   conclusion (position=3).
4. Create L2-SM referencing all content blocks.

Invariant T3-INV-001: The output contains exactly one "intro" block,
at least one "main_body" block, and exactly one "conclusion" block.

Invariant T3-INV-002: The block ordering preserves the logical flow
of the original document (intro before main_body before conclusion).

Invariant T3-INV-003: Every retained L2-KP is referenced by exactly
one L2-CB.

Traceability: TR-004 from source specification, Q-OUT-005 from requirement
analysis.

### Layer 2 to Layer 3 Transformation

#### Stage T4: Output Rendering (TR-003)

Input: L2-SM
Output: L3-OD

Process:
1. For each L2-CB in the structure map:
   a. Concatenate the consolidated_text of all keypoints in the block.
   b. Create an L3-OB with the concatenated text.
   c. Set source_keypoint_ids to the block's keypoint_ids.
2. Create L3-OD with:
   - output_type = declared by the runtime implementation
   - content_blocks = the array of L3-OBs
   - metadata = L3-MD with computed compression_ratio and language
3. Run output validation rules OV-001 through OV-007.

Invariant T4-INV-001: Every L3-OB.source_keypoint_ids references valid
L2-KP components in the source L2-SM.

Invariant T4-INV-002: L3-MD.compression_ratio <= 0.20 (C-001).

Invariant T4-INV-003: L3-MD.language == L1-DOC.detected_language (C-002).

Invariant T4-INV-004: All text in L3-OB.content is traceable to
L1-SEN.text via the chain L3-OB -> L2-KP -> L1-SEN (C-003).

Traceability: TR-003 from source specification, C-003 from requirement
analysis.

### Invariants Summary

| Invariant ID | Stage | Condition | Traceability |
|--------------|-------|-----------|--------------|
| T1-INV-001 | T1 | Keypoint source references are valid | Structural integrity |
| T1-INV-002 | T1 | Keypoint word count within budget | C-001 (preliminary) |
| T2-INV-001 | T2 | Cluster references are valid | Structural integrity |
| T2-INV-002 | T2 | Every keypoint in exactly one cluster | Completeness |
| T2-INV-003 | T2 | Representative preserves cluster meaning | TR-003 |
| T3-INV-001 | T3 | Required block types present | TR-004, Q-OUT-005 |
| T3-INV-002 | T3 | Block ordering matches source | TR-004 |
| T3-INV-003 | T3 | Every keypoint in exactly one block | Completeness |
| T4-INV-001 | T4 | Output block references are valid | Structural integrity |
| T4-INV-002 | T4 | Compression ratio <= 20% | C-001 |
| T4-INV-003 | T4 | Output language matches input | C-002 |
| T4-INV-004 | T4 | No new information introduced | C-003 |

### Constraints Summary

| Constraint ID | Requirement | Enforcement | Traceability |
|---------------|-------------|-------------|--------------|
| C-001 | Summary at most 20% of original word count | T4-INV-002, OV-002 | Source spec, REQ C-001 |
| C-002 | Same language as input | T4-INV-003, OV-003 | Source spec, REQ C-002 |
| C-003 | No new information not in original | T4-INV-004, OV-004 | Source spec, REQ C-003 |
| C-004 | Only .txt and .md input accepted | IV-002 | Source spec, REQ C-004 |


## Extension Mechanism

### Fixed Components

The following are fixed and cannot be changed by runtime implementations:

| Component | Reason |
|-----------|--------|
| L1-DOC, L1-SEC, L1-PAR, L1-SEN schema | Universal document model |
| L2-KP, L2-RC, L2-CB, L2-SM schema | Universal transformation model |
| L3-OD, L3-OB, L3-MD interface | Universal output contract |
| Transformation stages T1, T2, T3, T4 | Required processing pipeline |
| All invariants (T1-INV through T4-INV) | Non-negotiable correctness |
| Constraints C-001 through C-004 | Source specification requirements |
| Input validation rules IV-001 through IV-006 | Source specification requirements |
| Output validation rules OV-001 through OV-007 | Source specification requirements |

### Variable Components

The following are variable and can be customized by runtime implementations:

| Component | Variability | Example Variations |
|-----------|-------------|-------------------|
| Sentence boundary detection algorithm | Implementation choice | Regex, NLP library, rule-based |
| Language detection algorithm | Implementation choice | Heuristic, library-based |
| Importance scoring algorithm | Extension point TA-001 | TF-IDF, TextRank, frequency-based |
| Relevance threshold for keypoint selection | Runtime parameter | 0.5, 0.7, adaptive |
| Semantic similarity algorithm for clustering | Extension point TA-002 | Cosine similarity, Jaccard, embedding-based |
| Similarity threshold for clustering | Runtime parameter | 0.8, 0.9 |
| Output type (summary, bullet_points, key_phrases) | Extension point OR-001 | Determines rendering logic |
| File extension for output | Runtime parameter | .txt, .md |
| Word counting method | Extension point TA-003 | Whitespace-split, linguistic |

### Extension Interfaces

All extension interfaces are defined as Protocol contracts. Runtime
implementations must provide concrete classes that satisfy these Protocols.

#### IP-001: InputParser Protocol

```
Protocol InputParser:
  parse(input_path: Path) -> L1-DOC
  detect_language(text: string) -> string
  tokenize_sentences(text: string) -> array of string
  count_words(text: string) -> integer
```

Contract: The parse method must produce a valid L1-DOC that satisfies
all input validation rules (IV-001 through IV-006). The detect_language
method must return a valid ISO 639-1 code.

#### TA-001: ImportanceScorer Protocol

```
Protocol ImportanceScorer:
  score(sentence: L1-SEN, context: L1-DOC) -> float
```

Contract: Must return a float in range [0.0, 1.0]. Must be deterministic
for the same input. Must consider sentence position, content, and
relationship to surrounding context.

#### TA-002: SemanticSimilarity Protocol

```
Protocol SemanticSimilarity:
  compute_similarity(text_a: string, text_b: string) -> float
```

Contract: Must return a float in range [0.0, 1.0]. Where 0.0 means
completely unrelated and 1.0 means identical meaning.

#### TA-003: WordCounter Protocol

```
Protocol WordCounter:
  count(text: string) -> integer
```

Contract: Must return a non-negative integer. Must be consistent: the
same text always produces the same count.

#### OR-001: OutputRenderer Protocol

```
Protocol OutputRenderer:
  render(structure_map: L2-SM, output_type: string) -> L3-OD
  get_output_type() -> string
  get_file_extension() -> string
```

Contract: The render method must produce a valid L3-OD that satisfies
all output validation rules (OV-001 through OV-007). The output_type
must match one of the declared supported types. The file extension
must be a valid text file extension.

### Extension Contracts

New runtime implementations must:

1. Declare which output_type they produce.
2. Implement all required Protocols (InputParser, ImportanceScorer,
   SemanticSimilarity, WordCounter, OutputRenderer).
3. Satisfy all invariants (T1-INV through T4-INV).
4. Satisfy all constraints (C-001 through C-004).
5. Pass all output validation rules (OV-001 through OV-007).

New output types can be added without modifying the meta schema or
transformation stages T1 through T3. Only Stage T4 and the OutputRenderer
protocol implementation change.


## Self-Validation

### Coverage Checklist

| Requirement | Covered | Spec Section | Traceability |
|-------------|---------|--------------|--------------|
| Generator Identity | Yes | Document Metadata | Source spec frontmatter |
| Input Artifacts | Yes | Input Mapping | REQ Input Specification |
| Output Artifacts | Yes | Output Mapping | REQ Output Specification |
| TR-001: Extract Key Points | Yes | Stage T1 | REQ TR-001 |
| TR-002: Remove Redundancy | Yes | Stage T2 | REQ TR-002 |
| TR-003: Preserve Meaning | Yes | T2-INV-003, T4-INV-004 | REQ TR-003, C-003 |
| TR-004: Maintain Structure | Yes | Stage T3, T3-INV-001/002 | REQ TR-004, Q-OUT-005 |
| C-001: Length Constraint | Yes | T4-INV-002, OV-002 | REQ C-001, Q-OUT-001 |
| C-002: Language Fidelity | Yes | T4-INV-003, OV-003 | REQ C-002, Q-OUT-002 |
| C-003: No New Information | Yes | T4-INV-004, OV-004 | REQ C-003, Q-OUT-003 |
| C-004: Input Format | Yes | IV-002 | REQ C-004, V-IN-002 |
| Extension Points | Yes | Extension Mechanism | REQ Extension Points |

### Consistency Checklist

| Check | Status | Notes |
|-------|--------|-------|
| All Layer 1 components defined | Pass | L1-DOC, L1-SEC, L1-PAR, L1-SEN |
| All Layer 2 components defined | Pass | L2-KP, L2-RC, L2-CB, L2-SM |
| All Layer 3 components defined | Pass | L3-OD, L3-OB, L3-MD |
| All transformation stages have invariants | Pass | T1 through T4, each with invariants |
| All constraints mapped to invariants or validation rules | Pass | C-001 through C-004 |
| Input validation covers all V-IN rules | Pass | IV-001 through IV-006 |
| Output validation covers all Q-OUT rules | Pass | OV-001 through OV-007 |
| Extension interfaces cover all variable components | Pass | IP-001, TA-001/002/003, OR-001 |
| No output-type-specific content in Layer 3 | Pass | L3-OD is an interface with output_type discriminator |
| Relationship graph is complete and acyclic | Pass | Verified in Component Relationships |

### Ambiguity Log

| ID | Item | Status | Resolution Approach |
|----|------|--------|---------------------|
| CA-001 | Output file extension not specified | Recorded | Runtime implementation decides (OR-001) |
| CA-002 | Maximum input file size not specified | Recorded | Runtime implementation may add limits |
| CA-003 | Whether output must be .txt or .md | Recorded | Runtime implementation decides (OR-001) |
| CA-004 | Word counting method not specified | Recorded | Extension point TA-003 |
| CA-005 | Single paragraph vs. multi-paragraph output | Recorded | Determined by output_type and runtime |

### Completeness Statement

All requirements from the source specification (simple_text_summarizer.md)
and the requirement analysis (REQUIREMENT_ANALYSIS-01.md) have been
captured in this composition specification. The spec follows Pattern 2
(Input Transformation) of the composition system standard with
output-type-agnostic design per Section 13.

No requirements have been invented beyond what is stated in the source
documents. Ambiguities are recorded but not resolved with assumed
defaults. Extension points from the requirement analysis are supported
through the Extension Mechanism section.

The spec is self-consistent: every component is defined, every
transformation stage has invariants, every constraint is enforced by
at least one invariant or validation rule, and every extension interface
has a clear contract.


## References

| Reference | Source |
|-----------|--------|
| simple_text_summarizer.md | Source specification |
| REQUIREMENT_ANALYSIS-01.md | Upstream requirement analysis |
| COMPOSITION_SYSTEM_STANDARD.md | Layer 1 governance (read-only) |

---

End of Composition Specification.
