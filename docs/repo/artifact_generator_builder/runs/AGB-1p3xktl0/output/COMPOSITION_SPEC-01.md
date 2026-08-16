---
doc_type: "composition_spec"
identity_locked: true
source: "simple_text_summarizer.md"
codename: "text_summarizer_ayz"
version: "1.0.0"
standard_reference: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "Input Transformation (Pattern 2)"
spec_date: "2026-08-10"
---

# Composition Specification: Text Summarizer

## Scope and Purpose

This document defines the composition specification for the Text Summarizer
generator. It specifies the intermediate representation (meta schema), the
mapping rules between input and output, the transformation stages and their
invariants, and the extension mechanism for adding new output types.

This specification follows Pattern 2 (Input Transformation) from the
BASE_COMPOSITION_STANDARD_v1.0.md, which defines a three-layer architecture:

- Layer 1: INPUT PARSING -- Decompose input into structured intermediate form
- Layer 2: TRANSFORMATION -- Analyze, transform, and compose intermediate results
- Layer 3: OUTPUT RENDERING -- Render final output from transformed components

This specification is output-type-agnostic. It defines a generic output contract
that supports multiple output types through different runtime implementations.

---

## Meta Schema Definition

The meta schema defines the intermediate representation used between all three
layers. Components are grouped by layer. Each component has typed properties and
declared relationships to other components.

### Layer 1 Components (Input Parsing)

Layer 1 components represent the parsed structure of the input document.

#### COMP-L1-001: SourceDocument

The top-level container for the parsed input.

| Property | Type | Required | Description |
|---|---|---|---|
| doc_id | string | Yes | Unique identifier for this document instance |
| language | string | Yes | Detected ISO 639-1 language code |
| word_count | integer | Yes | Total word count of the source |
| encoding | string | Yes | Character encoding (default: UTF-8) |
| sections | array of StructuralSection | Yes | Ordered list of structural sections |
| raw_format | enum | Yes | Source format: txt, md |

#### COMP-L1-002: StructuralSection

A logical section of the document (introduction, body, conclusion).

| Property | Type | Required | Description |
|---|---|---|---|
| section_id | string | Yes | Unique identifier within the document |
| section_type | enum | Yes | One of: introduction, body, conclusion |
| position | integer | Yes | Sequential order index (1-based) |
| text_units | array of TextUnit | Yes | Ordered list of text units in this section |
| section_word_count | integer | Yes | Word count for this section |

#### COMP-L1-003: TextUnit

The atomic unit of text for analysis (typically a sentence or paragraph).

| Property | Type | Required | Description |
|---|---|---|---|
| unit_id | string | Yes | Unique identifier within the document |
| content | string | Yes | The text content |
| unit_type | enum | Yes | One of: sentence, paragraph |
| position | integer | Yes | Sequential order index (1-based, document-global) |
| word_count | integer | Yes | Word count of this unit |
| section_ref | string | Yes | Reference to parent StructuralSection section_id |

### Layer 2 Components (Transformation)

Layer 2 components represent the results of analysis and transformation.

#### COMP-L2-001: ImportanceAnalysis

The result of importance scoring applied to text units.

| Property | Type | Required | Description |
|---|---|---|---|
| analysis_id | string | Yes | Unique identifier for this analysis |
| scored_units | array of ScoredUnit | Yes | Text units with assigned importance scores |
| scoring_method | string | Yes | Name of the scoring algorithm used |

#### COMP-L2-002: ScoredUnit

A text unit annotated with an importance score.

| Property | Type | Required | Description |
|---|---|---|---|
| unit_ref | string | Yes | Reference to TextUnit unit_id |
| importance_score | float | Yes | Importance score (0.0 to 1.0, normalized) |
| rank | integer | Yes | Position when sorted by importance (1 = most important) |

#### COMP-L2-003: RedundancyCluster

A group of text units expressing substantially the same idea.

| Property | Type | Required | Description |
|---|---|---|---|
| cluster_id | string | Yes | Unique identifier for this cluster |
| representative_unit_ref | string | Yes | Reference to the TextUnit chosen as canonical |
| constituent_unit_refs | array of string | Yes | References to all TextUnit members |
| consolidation_score | float | Yes | Degree of semantic overlap (0.0 to 1.0) |

#### COMP-L2-004: KeyPoint

An extracted key point derived from a scored text unit.

| Property | Type | Required | Description |
|---|---|---|---|
| keypoint_id | string | Yes | Unique identifier for this key point |
| source_unit_ref | string | Yes | Reference to the source TextUnit unit_id |
| content | string | Yes | The extracted key point text |
| importance_score | float | Yes | Inherited from ScoredUnit |
| rank | integer | Yes | Ordering position (1 = most important) |
| section_ref | string | Yes | Reference to origin StructuralSection |

#### COMP-L2-005: SummaryBlock

A block of summary content corresponding to a structural section.

| Property | Type | Required | Description |
|---|---|---|---|
| block_id | string | Yes | Unique identifier for this block |
| section_ref | string | Yes | Reference to the source StructuralSection |
| content | string | Yes | The condensed summary text for this section |
| target_section_type | enum | Yes | One of: introduction, body, conclusion |
| source_unit_refs | array of string | Yes | References to TextUnits used in this block |
| block_word_count | integer | Yes | Word count of this summary block |

### Layer 3 Components (Output Rendering)

Layer 3 components define the generic output contract.

#### COMP-L3-001: OutputDocument

The generic interface for all output types. This is NOT a concrete output format.
It is a contract that runtime implementations must satisfy.

| Property | Type | Required | Description |
|---|---|---|---|
| output_id | string | Yes | Unique identifier for this output |
| output_type | enum | Yes | The output variant: condensed_summary, key_points_list, executive_summary, bullet_overview, abstract |
| source_doc_ref | string | Yes | Reference to the SourceDocument doc_id |
| language | string | Yes | Must match SourceDocument language |
| output_blocks | array of OutputBlock | Yes | Ordered content blocks |
| metadata | dict | Yes | Output-type-specific metadata |
| validation_rules | array of ValidationRule | Yes | Rules that must pass for this output type |

#### COMP-L3-002: OutputBlock

A single content block within an output document.

| Property | Type | Required | Description |
|---|---|---|---|
| block_id | string | Yes | Unique identifier |
| content | string | Yes | The rendered text content |
| block_type | enum | Yes | One of: prose_paragraph, numbered_item, scored_item, section_heading |
| position | integer | Yes | Sequential order index |
| metadata | dict | No | Block-level metadata (e.g., importance_score for scored_item) |

#### COMP-L3-003: ValidationRule

A named constraint that output content must satisfy.

| Property | Type | Required | Description |
|---|---|---|---|
| rule_id | string | Yes | Unique identifier for this rule |
| rule_type | enum | Yes | One of: word_count_ratio, language_match, structure_preservation, no_new_info, score_present |
| description | string | Yes | Human-readable description of the constraint |
| threshold | float | No | Numeric threshold (e.g., 0.2 for 20% ratio) |
| applies_to | array of enum | Yes | Which output_type values this rule applies to |

### Component Relationships

The relationships between components form a directed acyclic graph:

```
SourceDocument
  |-- contains --> StructuralSection[]
       |-- contains --> TextUnit[]
            |-- referenced by --> ScoredUnit (in ImportanceAnalysis)
            |-- referenced by --> RedundancyCluster (as constituent)
            |-- referenced by --> KeyPoint (as source)
            |-- referenced by --> SummaryBlock (as source)

ImportanceAnalysis
  |-- contains --> ScoredUnit[]
       |-- references --> TextUnit

RedundancyCluster
  |-- representative --> TextUnit
  |-- members --> TextUnit[]

KeyPoint[] --> ordered by rank, each references one TextUnit

SummaryBlock[] --> ordered by section position, each references one StructuralSection

OutputDocument
  |-- contains --> OutputBlock[]
  |-- validates against --> ValidationRule[]
  |-- derived from --> SourceDocument
```

---

## Input Mapping

This section defines how raw input artifacts are mapped to Layer 1 meta schema
components.

### Input Artifact

| Field | Source | Target Component |
|---|---|---|
| Source text file (.txt or .md) | Raw file content | SourceDocument (COMP-L1-001) |

### Parsing Rules

#### MAP-IN-001: File Reading and Encoding

Read the input file as UTF-8 text. If the file cannot be read or is empty,
the mapping fails with a validation error.

**Source:** Raw file bytes
**Target:** SourceDocument.raw_format, SourceDocument.encoding

#### MAP-IN-002: Format Detection

Determine the source format from the file extension.

| File Extension | raw_format Value |
|---|---|
| .txt | txt |
| .md | md |

Any other extension is a validation failure.

#### MAP-IN-003: Language Detection

Apply language detection to the full document text. The detected language code
is stored in SourceDocument.language. Detection must produce a result; if the
language cannot be detected, the mapping fails.

**Source:** Full document text
**Target:** SourceDocument.language

#### MAP-IN-004: Word Count

Count words in the full document text. Word boundaries are defined as
whitespace-separated tokens. Punctuation attached to words does not create
additional tokens.

**Source:** Full document text
**Target:** SourceDocument.word_count

#### MAP-IN-005: Structural Section Decomposition

Decompose the document into StructuralSection components. The decomposition
strategy depends on the input format:

**For .txt files:**
- If the text contains explicit section markers (e.g., blank-line-separated
  blocks), treat each block as a section.
- Classify the first section as "introduction", the last as "conclusion",
  and all middle sections as "body".
- If only one block exists, classify it as "body" with no introduction or
  conclusion sections.

**For .md files:**
- Use heading markers (# ## ###) to identify section boundaries.
- Content before the first heading is "introduction" if present.
- Content under headings maps to "body" sections.
- The final section or explicit conclusion heading maps to "conclusion".
- If no headings exist, fall back to the .txt strategy.

Each StructuralSection receives:
- section_id: generated as "sec-{position}" (e.g., sec-1, sec-2)
- section_type: introduction, body, or conclusion
- position: sequential 1-based index

#### MAP-IN-006: Text Unit Segmentation

Within each StructuralSection, segment the text into TextUnit components.

**Primary unit:** sentence. Split on sentence-ending punctuation
(period, question mark, exclamation mark) followed by whitespace or end-of-text.

Each TextUnit receives:
- unit_id: generated as "tu-{position}" (document-global sequential)
- content: the sentence text
- unit_type: "sentence"
- position: document-global sequential 1-based index
- word_count: count of words in this sentence
- section_ref: the parent section_id

#### MAP-IN-007: Document Assembly

Assemble the SourceDocument from all parsed components:
- doc_id: generated as "doc-{timestamp}" or assigned by the runtime
- sections: ordered array of StructuralSection objects
- Each section contains its ordered array of TextUnit objects

### Input Mapping Validation Rules

| Rule ID | Validation | Failure Action |
|---|---|---|
| V-MAP-IN-001 | File exists and is readable | Abort with error |
| V-MAP-IN-002 | File extension is .txt or .md | Abort with error |
| V-MAP-IN-003 | Content is non-empty (at least one sentence) | Abort with error |
| V-MAP-IN-004 | Language detection succeeds | Abort with error |
| V-MAP-IN-005 | At least one StructuralSection is produced | Abort with error |
| V-MAP-IN-006 | Every TextUnit has non-empty content | Skip unit, log warning |
| V-MAP-IN-007 | word_count > 0 | Abort with error |

---

## Output Mapping

This section defines how Layer 3 meta schema components are mapped to output
artifacts.

### Output Artifacts

The composition spec defines a generic output contract. Different runtime
implementations produce different concrete outputs. The following table shows
the known output types and their artifact mappings.

| Output Type | Output Artifact Key (Inferred) | Rendered Format |
|---|---|---|
| condensed_summary | CONDENSED_SUMMARY | Prose text file |
| key_points_list | KEY_POINTS_LIST | Ordered list with scores |

### Output Rendering Rules

#### MAP-OUT-001: Condensed Summary Rendering

**Source Components:** SummaryBlock[] (ordered by section position)
**Target:** OutputDocument with output_type = "condensed_summary"

Rendering process:
1. Create an OutputDocument with output_type = "condensed_summary".
2. For each SummaryBlock (in section position order):
   a. Create an OutputBlock with block_type = "prose_paragraph".
   b. Set content to the SummaryBlock.content.
   c. Set position to the sequential order index.
3. Set OutputDocument.language to SourceDocument.language.
4. Set metadata:
   - source_word_count: SourceDocument.word_count
   - summary_word_count: sum of all SummaryBlock.block_word_count
   - compression_ratio: summary_word_count / source_word_count
5. Assign validation rules: VR-001, VR-002, VR-003, VR-004.
6. Serialize the OutputBlock contents as continuous prose paragraphs.

**Validation checks on output:**
- The concatenated prose must form a coherent summary.
- Word count must not exceed 20% of source word count.
- Language must match source language.
- Structure must reflect introduction, main points, conclusion order.

#### MAP-OUT-002: Key Points List Rendering

**Source Components:** KeyPoint[] (ordered by rank)
**Target:** OutputDocument with output_type = "key_points_list"

Rendering process:
1. Create an OutputDocument with output_type = "key_points_list".
2. For each KeyPoint (in rank order):
   a. Create an OutputBlock with block_type = "scored_item".
   b. Set content to the KeyPoint.content.
   c. Set position to the KeyPoint.rank.
   d. Set metadata: { "importance_score": KeyPoint.importance_score }.
3. Set OutputDocument.language to SourceDocument.language.
4. Set metadata:
   - total_key_points: count of KeyPoint components
   - score_range: [min_score, max_score]
5. Assign validation rules: VR-005, VR-006, VR-007.
6. Serialize as a numbered list where each item includes its importance score.

**Validation checks on output:**
- Each key point must trace to a source TextUnit.
- Every item must have an importance score.
- Items must be ordered by importance.

#### MAP-OUT-003: Serialization Format

The runtime implementation decides the serialization format (e.g., .txt, .md,
.json). The composition spec does not mandate a specific file format. However,
the serialization must preserve:
- All content text from OutputBlocks
- Ordering from position fields
- Scores from metadata fields (for scored_item blocks)
- Language provenance from OutputDocument.language

### Output Mapping Validation Rules

| Rule ID | Validation | Applies To | Failure Action |
|---|---|---|---|
| V-MAP-OUT-001 | OutputDocument has at least one OutputBlock | All types | Abort with error |
| V-MAP-OUT-002 | OutputBlock positions are sequential and gap-free | All types | Abort with error |
| V-MAP-OUT-003 | OutputDocument.language matches SourceDocument.language | All types | Abort with error |
| V-MAP-OUT-004 | All ValidationRule constraints pass | All types | Abort with error |
| V-MAP-OUT-005 | Serialization preserves all content and ordering | All types | Abort with error |

---

## Transformation Rules

This section defines the transformation pipeline from Layer 1 to Layer 2 to
Layer 3. Each stage has pre-conditions, processing logic, and post-conditions
(invariants).

### Stage 1: Importance Scoring

**Input:** TextUnit[] (from Layer 1)
**Output:** ImportanceAnalysis with ScoredUnit[] (Layer 2)

**Pre-conditions:**
- All TextUnit components are valid (non-empty content, valid positions).
- SourceDocument.language is detected.

**Processing:**
1. For each TextUnit, compute an importance_score based on:
   - Positional features (units in introduction/conclusion may score higher)
   - Structural features (units with heading proximity may score higher)
   - Linguistic features (keyword density, specificity indicators)
2. Normalize all scores to the range [0.0, 1.0].
3. Assign rank based on descending importance_score order.
4. Package results into an ImportanceAnalysis component.

**Post-conditions (Invariants):**
- INV-S1-001: Every TextUnit has exactly one ScoredUnit.
- INV-S1-002: All importance_score values are in [0.0, 1.0].
- INV-S1-003: Ranks are sequential integers starting from 1 with no gaps.
- INV-S1-004: No two ScoredUnits share the same rank.

### Stage 2: Redundancy Analysis

**Input:** TextUnit[], ScoredUnit[] (from Stage 1)
**Output:** RedundancyCluster[] (Layer 2)

**Pre-conditions:**
- ImportanceAnalysis is complete (all TextUnits scored).

**Processing:**
1. Compare all pairs of TextUnits for semantic similarity.
2. Group TextUnits that exceed a similarity threshold into RedundancyClusters.
3. For each cluster, select the representative unit as the one with the highest
   importance_score among cluster members.
4. TextUnits not similar to any other remain as single-member clusters.
5. Compute consolidation_score for each cluster (average pairwise similarity).

**Post-conditions (Invariants):**
- INV-S2-001: Every TextUnit belongs to exactly one RedundancyCluster.
- INV-S2-002: Every cluster has exactly one representative_unit_ref.
- INV-S2-003: The representative has the highest importance_score in the cluster.
- INV-S2-004: consolidation_score is in [0.0, 1.0].

### Stage 3: Key Point Extraction

**Input:** ScoredUnit[], RedundancyCluster[] (from Stages 1-2)
**Output:** KeyPoint[] (Layer 2)

**Pre-conditions:**
- Stages 1 and 2 are complete.

**Processing:**
1. For each RedundancyCluster, select the representative ScoredUnit.
2. If the representative's importance_score exceeds a configurable threshold,
   create a KeyPoint from it.
3. KeyPoint.content is set to the source TextUnit.content (verbatim or lightly
   edited for standalone readability).
4. KeyPoint.importance_score is inherited from the ScoredUnit.
5. KeyPoint.rank reflects the ordering by importance_score (highest first).
6. KeyPoint.section_ref is inherited from the source TextUnit.

**Post-conditions (Invariants):**
- INV-S3-001: Each KeyPoint references exactly one TextUnit.
- INV-S3-002: No two KeyPoints reference the same TextUnit.
- INV-S3-003: KeyPoints are ordered by descending importance_score.
- INV-S3-004: Every KeyPoint.importance_score is above the extraction threshold.

### Stage 4: Summary Block Composition

**Input:** TextUnit[], ScoredUnit[], RedundancyCluster[], StructuralSection[]
**Output:** SummaryBlock[] (Layer 2)

**Pre-conditions:**
- Stages 1-3 are complete.
- SourceDocument.word_count is known.

**Processing:**
1. Compute the maximum summary word count: max_words = floor(0.20 * source_word_count).
2. Allocate word count budgets to each StructuralSection proportionally:
   - budget_i = floor(max_words * (section_word_count_i / source_word_count))
3. For each StructuralSection:
   a. Identify the TextUnits belonging to this section.
   b. Remove redundant TextUnits (keep only cluster representatives).
   c. Rank remaining TextUnits by importance_score.
   d. Compose a condensed summary paragraph using the highest-ranked non-redundant
      TextUnits, staying within the section's word count budget.
   e. Create a SummaryBlock with the composed content.
4. Verify total block_word_count across all SummaryBlocks does not exceed max_words.

**Post-conditions (Invariants):**
- INV-S4-001: Exactly one SummaryBlock is produced per StructuralSection.
- INV-S4-002: Sum of all SummaryBlock.block_word_count <= max_words.
- INV-S4-003: SummaryBlocks preserve section ordering (introduction first, conclusion last).
- INV-S4-004: Each SummaryBlock.content is non-empty.
- INV-S4-005: No new information is introduced beyond what exists in the source TextUnits.

### Stage 5: Output Assembly

**Input:** SummaryBlock[], KeyPoint[] (from Stages 3-4)
**Output:** OutputDocument[] (Layer 3)

**Pre-conditions:**
- Stages 1-4 are complete.

**Processing:**
1. Create one OutputDocument per requested output type.
2. For condensed_summary output type:
   a. Apply MAP-OUT-001 rendering rules.
   b. Create OutputBlocks from SummaryBlocks.
3. For key_points_list output type:
   a. Apply MAP-OUT-002 rendering rules.
   b. Create OutputBlocks from KeyPoints.
4. Assign ValidationRules to each OutputDocument.

**Post-conditions (Invariants):**
- INV-S5-001: At least one OutputDocument is produced.
- INV-S5-002: Every OutputDocument.language matches SourceDocument.language.
- INV-S5-003: Every OutputDocument has at least one OutputBlock.
- INV-S5-004: All ValidationRule constraints are satisfied.

### Stage 6: Output Validation

**Input:** OutputDocument[] (from Stage 5)
**Output:** Validated OutputDocument[] or validation failure report

**Pre-conditions:**
- Stage 5 is complete.

**Processing:**
1. For each OutputDocument, evaluate every assigned ValidationRule.
2. Collect any violations.
3. If any violations exist, the output fails validation.
4. If all rules pass, the output is marked as validated.

**Post-conditions (Invariants):**
- INV-S6-001: No OutputDocument is released without passing all its ValidationRules.
- INV-S6-002: Validation results are recorded and traceable.

### Global Invariants

These invariants hold across the entire transformation pipeline:

| Invariant ID | Description |
|---|---|
| GI-001 | Source language is preserved in all outputs (same language as input). |
| GI-002 | No information is introduced that does not exist in the source document. |
| GI-003 | The condensed summary word count never exceeds 20% of source word count. |
| GI-004 | Every output component traces back to at least one source TextUnit. |
| GI-005 | The logical structure (introduction, main points, conclusion) is preserved. |
| GI-006 | All component references (unit_ref, section_ref, source_unit_ref) resolve. |

### Named Validation Rules

| Rule ID | Rule Type | Description | Threshold | Applies To |
|---|---|---|---|---|
| VR-001 | word_count_ratio | Summary word count / source word count | 0.20 | condensed_summary |
| VR-002 | language_match | Output language equals source language | N/A | condensed_summary, key_points_list |
| VR-003 | structure_preservation | Output contains intro, body, conclusion sections | N/A | condensed_summary |
| VR-004 | no_new_info | All output content traces to source | N/A | condensed_summary, key_points_list |
| VR-005 | score_present | Every key point has an importance score | N/A | key_points_list |
| VR-006 | language_match | Output language equals source language | N/A | key_points_list |
| VR-007 | no_new_info | All key points trace to source text | N/A | key_points_list |

---

## Extension Mechanism

This section defines what parts of the specification are fixed and what parts
are variable, enabling new runtime implementations to plug in.

### Fixed Components (Cannot Be Changed)

The following elements are fixed by this specification and must not be altered
by any runtime implementation:

1. **Layer 1 component schema** (COMP-L1-001 through COMP-L1-003): The
   SourceDocument, StructuralSection, and TextUnit components and their required
   properties are fixed. All implementations must produce these components.

2. **Global invariants** (GI-001 through GI-006): All invariants must hold
   regardless of implementation choices.

3. **Input mapping validation rules** (V-MAP-IN-001 through V-MAP-IN-007):
   All input validation rules are mandatory.

4. **Stage ordering**: The six transformation stages must execute in the
   declared order. No stage can be skipped.

5. **Stage invariants**: All INV-S* invariants and GI-* invariants must hold
   after their respective stages complete.

### Variable Components (Implementation-Defined)

The following elements are defined as protocols (interfaces) that runtime
implementations must satisfy, but the concrete implementation is free to vary:

#### EXT-001: InputParser Protocol

Defines how different input formats can be supported.

```
InputParser Protocol:
  parse(input_path: string) -> SourceDocument
  detect_language(text: string) -> string
  segment_sections(text: string, format: enum) -> StructuralSection[]
  segment_units(section: StructuralSection) -> TextUnit[]
```

**Contract:**
- Must produce a valid SourceDocument with all required properties.
- Must satisfy all V-MAP-IN-* validation rules.
- Must handle .txt and .md formats at minimum.

**Extension examples:**
- MarkdownParser: Enhanced heading-based section detection
- PlainTextParser: Heuristic block-based section detection
- PDFParser: Future extension for .pdf input format
- DocxParser: Future extension for .docx input format

#### EXT-002: ImportanceScorer Protocol

Defines how importance scoring algorithms can be swapped.

```
ImportanceScorer Protocol:
  score(text_units: TextUnit[], doc: SourceDocument) -> ImportanceAnalysis
```

**Contract:**
- Must produce a ScoredUnit for every input TextUnit.
- Scores must be normalized to [0.0, 1.0].
- Must satisfy INV-S1-001 through INV-S1-004.

**Extension examples:**
- TFIDFScorer: Term frequency-inverse document frequency
- TextRankScorer: Graph-based ranking algorithm
- PositionalScorer: Position-weighted simple heuristic
- NeuralScorer: ML-based importance estimation

#### EXT-003: RedundancyDetector Protocol

Defines how redundancy detection algorithms can be swapped.

```
RedundancyDetector Protocol:
  detect_clusters(text_units: TextUnit[], analysis: ImportanceAnalysis) -> RedundancyCluster[]
```

**Contract:**
- Every TextUnit must belong to exactly one cluster.
- Must satisfy INV-S2-001 through INV-S2-004.

**Extension examples:**
- CosineSimilarityClusterer: Vector-based semantic similarity
- EmbeddingClusterer: Neural embedding-based clustering
- KeywordOverlapClusterer: Simple keyword overlap heuristic

#### EXT-004: OutputRenderer Protocol

Defines how different output formats can be produced.

```
OutputRenderer Protocol:
  render_summary(blocks: SummaryBlock[], doc: SourceDocument) -> OutputDocument
  render_keypoints(keypoints: KeyPoint[], doc: SourceDocument) -> OutputDocument
  serialize(output: OutputDocument, format: string) -> bytes
```

**Contract:**
- Must produce valid OutputDocument with all required properties.
- Must satisfy all VR-* validation rules for the output type.
- Must preserve SourceDocument.language.
- Must satisfy GI-001 (language preservation).
- Must satisfy GI-002 (no new information).
- Must satisfy GI-003 (compression ratio for condensed_summary).

**Extension examples:**
- MarkdownRenderer: Renders output as .md files
- PlainTextRenderer: Renders output as .txt files
- JSONRenderer: Renders output as structured .json files
- HTMLRenderer: Renders output as .html files

### Adding a New Output Type

To add a new output type (e.g., executive_summary, bullet_overview, abstract),
a runtime implementation must:

1. Define how the new output type maps from Layer 2 components to Layer 3
   OutputDocument.
2. Define the OutputBlock structure for the new type.
3. Define ValidationRules specific to the new type.
4. Implement an OutputRenderer that produces the new type.
5. Ensure all Global Invariants (GI-001 through GI-006) hold for the new type.

The new output type is added to the output_type enum in COMP-L3-001 without
changing any Layer 1 or Layer 2 components.

### Adding a New Input Format

To add a new input format (e.g., .pdf, .docx), a runtime implementation must:

1. Implement an InputParser that satisfies the EXT-001 protocol.
2. Produce SourceDocument, StructuralSection, and TextUnit components that
   conform to the Layer 1 schema.
3. Satisfy all V-MAP-IN-* validation rules.
4. The new format is handled entirely within Layer 1; no changes to Layer 2
   or Layer 3 are required.

### Runtime Implementation Registration

A runtime implementation registers itself by providing:

| Registration Field | Description |
|---|---|
| impl_id | Unique identifier for this implementation |
| input_parsers | Map of format -> InputParser instance |
| importance_scorer | ImportanceScorer instance |
| redundancy_detector | RedundancyDetector instance |
| output_renderers | Map of output_type -> OutputRenderer instance |
| config | Runtime configuration (thresholds, parameters) |

The runtime selects components based on the input format and requested output
types. The composition spec does not prescribe which concrete implementations
to use.

---

## Self-Validation

### Completeness Check

| Check | Status | Notes |
|---|---|---|
| Meta schema defines all three layers | PASS | Layer 1: 3 components, Layer 2: 5 components, Layer 3: 3 components |
| All components have typed properties | PASS | Every property has type, required flag, and description |
| Component relationships are declared | PASS | Directed references via *_ref fields, relationship diagram provided |
| Input mapping covers all input fields | PASS | 7 mapping rules (MAP-IN-001 through MAP-IN-007) |
| Output mapping covers all output types | PASS | 2 rendering rules (MAP-OUT-001, MAP-OUT-002) with generic contract |
| Transformation stages are defined | PASS | 6 stages with pre/post-conditions |
| Invariants are declared per stage | PASS | INV-S1 through INV-S6 plus 6 global invariants |
| Validation rules are named and typed | PASS | VR-001 through VR-007 with rule_type, threshold, applies_to |
| Extension mechanism is defined | PASS | 4 protocol interfaces with contracts and examples |
| Fixed vs variable parts are identified | PASS | Fixed: L1 schema, invariants, stage order. Variable: protocols |
| Output-type-agnostic design | PASS | Layer 3 uses generic OutputDocument interface, not hardcoded type |

### Consistency Check

| Check | Status | Notes |
|---|---|---|
| All *_ref fields reference declared components | PASS | unit_ref -> TextUnit, section_ref -> StructuralSection, etc. |
| No orphan components (all are reachable) | PASS | SourceDocument -> Sections -> TextUnits -> L2 -> L3 chain |
| Validation rules reference valid output types | PASS | All applies_to values match declared output_type enum values |
| Stage ordering is acyclic | PASS | S1 -> S2 -> S3 -> S4 -> S5 -> S6, no cycles |
| Input mapping produces all Layer 1 components | PASS | SourceDocument, StructuralSection, TextUnit all produced |
| Transformation produces all Layer 2 components | PASS | ImportanceAnalysis, RedundancyCluster, KeyPoint, SummaryBlock |
| Output mapping produces all Layer 3 components | PASS | OutputDocument, OutputBlock, ValidationRule |
| No contradiction between invariants | PASS | GI-* invariants are a subset of stage-specific invariants |

### Traceability Check

| Source Requirement | Traced To |
|---|---|
| IN-001: Source text document (.txt/.md) | COMP-L1-001 SourceDocument, MAP-IN-001 through MAP-IN-007 |
| V-IN-001: File must exist and be readable | V-MAP-IN-001 |
| V-IN-002: File extension .txt or .md | V-MAP-IN-002, MAP-IN-002 |
| V-IN-003: Content non-empty | V-MAP-IN-003, V-MAP-IN-007 |
| V-IN-004: Detectable language | V-MAP-IN-004, MAP-IN-003 |
| OUT-001: Condensed Summary | MAP-OUT-001, VR-001 through VR-004 |
| OUT-002: Key Points List | MAP-OUT-002, VR-005 through VR-007 |
| Q-OUT-001: Capture core message | GI-002, INV-S4-005 |
| Q-OUT-002: No new information | GI-002, VR-004 |
| Q-OUT-003: Logical flow | GI-005, INV-S4-003, VR-003 |
| Q-OUT-004: At most 20% word count | GI-003, VR-001, INV-S4-002 |
| Q-OUT-005: Key points trace to source | GI-004, VR-007 |
| Q-OUT-006: Importance scores present | VR-005, INV-S3-001 |
| Q-OUT-007: Key points ordered | INV-S3-003, MAP-OUT-002 |
| TR-001: Extract key points | Stage 3 (Key Point Extraction) |
| TR-002: Remove redundancy | Stage 2 (Redundancy Analysis) |
| TR-003: Preserve meaning | GI-002, INV-S4-005 |
| TR-004: Maintain structure | GI-005, INV-S4-003, MAP-IN-005 |
| C-PERF-001: 20% compression | GI-003, VR-001, INV-S4-002 |
| C-FMT-001: Input .txt/.md | V-MAP-IN-002, EXT-001 |
| C-FMT-002: Summary is prose | MAP-OUT-001, block_type = prose_paragraph |
| C-FMT-003: Key points ordered with scores | MAP-OUT-002, block_type = scored_item |
| C-FMT-004: Same language | GI-001, VR-002, VR-006 |
| C-CMP-001: No new information | GI-002, VR-004, VR-007 |
| C-CMP-002: Preserve source language | GI-001, INV-S5-002 |
| C-CMP-003: Preserve logical structure | GI-005, INV-S4-003 |

### Explicit Assumptions

The following assumptions are recorded where the requirement analysis identified
missing information:

| Assumption ID | Description | Resolution in Spec |
|---|---|---|
| A-001 | Importance score scale not defined | Spec defines [0.0, 1.0] normalized range |
| A-002 | Max/min key points not defined | Spec leaves count unbounded, controlled by extraction threshold |
| A-003 | Output file format not specified | Spec is format-agnostic; serialization is in EXT-004 OutputRenderer |
| A-004 | Artifact key names inferred | Spec uses inferred keys; runtime determines actual keys |
| A-005 | Input encoding not specified | Spec defaults to UTF-8 (MAP-IN-001) |
| A-006 | Maximum input size not bounded | Spec does not impose a bound; runtime may add one |
| A-007 | Word count definition not specified | Spec defines: whitespace-separated tokens, punctuation does not split |

### Self-Validation Summary

All checks pass. The composition specification is complete, consistent, and
fully traceable to the source requirement analysis and the base composition
standard.

---

## References

- BASE_COMPOSITION_STANDARD_v1.0.md -- Universal composition system pattern
- REQUIREMENT_ANALYSIS-01.md -- Requirement analysis for this generator
- simple_text_summarizer.md -- Original requirement document

---

**End of Composition Specification**
