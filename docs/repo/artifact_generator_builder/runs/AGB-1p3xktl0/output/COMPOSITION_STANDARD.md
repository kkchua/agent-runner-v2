---
doc_type: "composition_standard"
identity_locked: true
generator_name: "text_summarizer_ayz"
codename: "text_summarizer_ayz"
version: "1.0.0"
standard_reference: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "Input Transformation (Pattern 2)"
generated_at: "2026-08-10"
---

# Composition Standard: text_summarizer_ayz

## 1. Purpose

This document defines the generator-specific composition standard for the
text_summarizer_ayz workflow. It adapts the universal pattern defined in
BASE_COMPOSITION_STANDARD_v1.0.md to the domain of text summarization.

This standard specifies:
- The meta schema for text summarization components (Layer 1, 2, 3)
- The transformation pipeline from input parsing through output rendering
- The invariants and validation rules that must hold at each stage
- The extension interfaces for pluggable components

This standard is traceable to:
- BASE_COMPOSITION_STANDARD_v1.0.md (universal pattern)
- COMPOSITION_SPEC-01.md (generator composition specification)
- RUNTIME_IMPL-01.md (runtime implementation design)

Identity is locked: no downstream configuration may override or substitute
the generator_name or codename values.

---

## 2. Architecture

The text_summarizer_ayz workflow follows Pattern 2 (Input Transformation)
from the base standard. Input content is transformed into output content
through a 7-stage pipeline.

```
Layer 1: INPUT PARSING
    Parse input text into structured intermediate form
    Source text -> SourceDocument -> StructuralSection -> TextUnit
                            |
                            v
Layer 2: TRANSFORMATION
    Analyze, transform, and compose intermediate results
    TextUnit -> ScoredUnit -> RedundancyCluster -> KeyPoint -> SummaryBlock
                            |
                            v
Layer 3: OUTPUT RENDERING
    Render final output from transformed components
    SummaryBlock -> OutputDocument (condensed_summary)
    KeyPoint -> OutputDocument (key_points_list)
```

### Separation of Concerns

- Input Parsing defines HOW to decompose input text into structured form
- Transformation defines HOW to analyze and compose intermediate results
- Output Rendering defines HOW to produce final deliverables

---

## 3. Universal Component Schema

All components conform to the unified schema defined in
BASE_COMPOSITION_STANDARD_v1.0.md Section 3. Components are grouped
by layer. Each component has typed properties and declared relationships.

### 3.1 Common Properties

Every component has these properties:

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier within the library |
| component_type | enum | Yes | Domain-specific type |
| name | string | Yes | Human-readable display name |
| version | string | Yes | Semantic version |
| description | string | Yes | What this component does |

### 3.2 Type-Specific Properties (Text Summarizer Domain)

#### Layer 1 Types

| Component Type | Properties | Description |
|---|---|---|
| SourceDocument | doc_id, language, word_count, encoding, raw_format, sections | Top-level parsed input container |
| StructuralSection | section_id, section_type, position, text_units, section_word_count | Logical section of document |
| TextUnit | unit_id, content, unit_type, position, word_count, section_ref | Atomic unit of text |

#### Layer 2 Types

| Component Type | Properties | Description |
|---|---|---|
| ImportanceAnalysis | analysis_id, scored_units, scoring_method | Importance scoring results |
| ScoredUnit | unit_ref, importance_score, rank | Text unit with importance score |
| RedundancyCluster | cluster_id, representative_unit_ref, constituent_unit_refs, consolidation_score | Group of redundant text units |
| KeyPoint | keypoint_id, source_unit_ref, content, importance_score, rank, section_ref | Extracted key point |
| SummaryBlock | block_id, section_ref, content, target_section_type, source_unit_refs, block_word_count | Per-section summary block |

#### Layer 3 Types

| Component Type | Properties | Description |
|---|---|---|
| OutputDocument | output_id, output_type, source_doc_ref, language, output_blocks, metadata, validation_rules | Generic output interface |
| OutputBlock | block_id, content, block_type, position, metadata | Single content block |
| ValidationRule | rule_id, rule_type, description, threshold, applies_to | Named output constraint |

---

## 4. Transformation Pipeline

The text_summarizer_ayz transformation pipeline consists of 7 stages.
Each stage has pre-conditions, processing logic, and post-conditions.

### Stage 0: Input Loading

**Input:** Raw text file (.txt or .md)
**Output:** SourceDocument (Layer 1)

Parsing rules:
- MAP-IN-001: Read file as UTF-8 text
- MAP-IN-002: Detect format from extension (.txt or .md)
- MAP-IN-003: Detect language (ISO 639-1 code)
- MAP-IN-004: Count words (whitespace-separated tokens)
- MAP-IN-005: Decompose into StructuralSections
- MAP-IN-006: Segment into TextUnits (sentence-level)
- MAP-IN-007: Assemble SourceDocument

Input validation rules:
- V-MAP-IN-001: File must exist and be readable
- V-MAP-IN-002: Extension must be .txt or .md
- V-MAP-IN-003: Content must contain at least one sentence
- V-MAP-IN-004: Language must be detectable
- V-MAP-IN-005: At least one StructuralSection must be produced
- V-MAP-IN-006: Every TextUnit must have non-empty content (skip if empty)
- V-MAP-IN-007: Word count must be greater than zero

### Stage 1: Importance Scoring

**Input:** TextUnit[] (from Layer 1)
**Output:** ImportanceAnalysis with ScoredUnit[] (Layer 2)

Processing:
1. Compute importance_score for each TextUnit
2. Normalize scores to [0.0, 1.0]
3. Assign rank by descending score order

Post-conditions (Invariants):
- INV-S1-001: Every TextUnit has exactly one ScoredUnit
- INV-S1-002: All importance_score values are in [0.0, 1.0]
- INV-S1-003: Ranks are sequential integers starting from 1
- INV-S1-004: No two ScoredUnits share the same rank

### Stage 2: Redundancy Analysis

**Input:** TextUnit[], ScoredUnit[] (from Stage 1)
**Output:** RedundancyCluster[] (Layer 2)

Processing:
1. Compare TextUnit pairs for semantic similarity
2. Group similar units into clusters
3. Select representative (highest score) per cluster
4. Compute consolidation_score per cluster

Post-conditions (Invariants):
- INV-S2-001: Every TextUnit belongs to exactly one cluster
- INV-S2-002: Every cluster has exactly one representative
- INV-S2-003: Representative has highest score in cluster
- INV-S2-004: consolidation_score is in [0.0, 1.0]

### Stage 3: Key Point Extraction

**Input:** ScoredUnit[], RedundancyCluster[] (from Stages 1-2)
**Output:** KeyPoint[] (Layer 2)

Processing:
1. Select representative ScoredUnit per cluster
2. If score >= keypoint_threshold, create KeyPoint
3. Sort by descending importance_score
4. Assign sequential ranks

Post-conditions (Invariants):
- INV-S3-001: Each KeyPoint references exactly one TextUnit
- INV-S3-002: No two KeyPoints reference the same TextUnit
- INV-S3-003: KeyPoints are ordered by descending importance_score
- INV-S3-004: Every KeyPoint.importance_score is above threshold

### Stage 4: Summary Block Composition

**Input:** TextUnit[], ScoredUnit[], RedundancyCluster[], StructuralSection[]
**Output:** SummaryBlock[] (Layer 2)

Processing:
1. Compute max_words = floor(0.20 * source_word_count)
2. Allocate proportional word budgets per section
3. Select top-ranked non-redundant units within budget
4. Compose SummaryBlock content from selected units

Post-conditions (Invariants):
- INV-S4-001: One SummaryBlock per StructuralSection
- INV-S4-002: Total word count <= max_words
- INV-S4-003: Blocks preserve section ordering
- INV-S4-004: Each block content is non-empty
- INV-S4-005: No new information beyond source TextUnits

### Stage 5: Output Assembly

**Input:** SummaryBlock[], KeyPoint[] (from Stages 3-4)
**Output:** OutputDocument[] (Layer 3)

Processing:
1. Create one OutputDocument per requested output type
2. Apply rendering rules (MAP-OUT-001 for summary, MAP-OUT-002 for key points)
3. Assign ValidationRules per output type

Post-conditions (Invariants):
- INV-S5-001: At least one OutputDocument is produced
- INV-S5-002: Every OutputDocument.language matches SourceDocument.language
- INV-S5-003: Every OutputDocument has at least one OutputBlock
- INV-S5-004: All ValidationRule constraints are satisfied

### Stage 6: Output Validation

**Input:** OutputDocument[] (from Stage 5)
**Output:** Validated OutputDocument[] or failure report

Processing:
1. Evaluate every ValidationRule for each OutputDocument
2. Collect violations
3. If any violations, output fails validation

Post-conditions (Invariants):
- INV-S6-001: No OutputDocument released without passing all rules
- INV-S6-002: Validation results are recorded and traceable

---

## 5. Named Validation Rules

| Rule ID | Rule Type | Description | Threshold | Applies To |
|---|---|---|---|---|
| VR-001 | word_count_ratio | Summary/source word count ratio | 0.20 | condensed_summary |
| VR-002 | language_match | Output language equals source language | N/A | condensed_summary, key_points_list |
| VR-003 | structure_preservation | Output contains intro, body, conclusion | N/A | condensed_summary |
| VR-004 | no_new_info | All output content traces to source | N/A | condensed_summary, key_points_list |
| VR-005 | score_present | Every key point has importance score | N/A | key_points_list |
| VR-006 | language_match | Output language equals source language | N/A | key_points_list |
| VR-007 | no_new_info | All key points trace to source text | N/A | key_points_list |

---

## 6. Global Invariants

These invariants hold across the entire transformation pipeline:

| Invariant ID | Description |
|---|---|
| GI-001 | Source language is preserved in all outputs |
| GI-002 | No information is introduced beyond the source document |
| GI-003 | Condensed summary word count never exceeds 20% of source |
| GI-004 | Every output component traces to at least one source TextUnit |
| GI-005 | Logical structure (introduction, main points, conclusion) is preserved |
| GI-006 | All component references resolve to existing components |

---

## 7. Extension Interfaces

The following protocols define the variable components that runtime
implementations can customize.

### EXT-001: InputParser Protocol

Defines how different input formats can be supported.

```
InputParser Protocol:
    parse(input_path: string) -> SourceDocument
    detect_language(text: string) -> string
    segment_sections(text: string, format: enum) -> StructuralSection[]
    segment_units(section: StructuralSection) -> TextUnit[]
```

Contract:
- Must produce a valid SourceDocument with all required properties
- Must satisfy all V-MAP-IN-* validation rules
- Must handle .txt and .md formats at minimum

Default implementations:
- TxtParser: Blank-line section decomposition for .txt files
- MdParser: Heading-based section decomposition for .md files

### EXT-002: ImportanceScorer Protocol

Defines how importance scoring algorithms can be swapped.

```
ImportanceScorer Protocol:
    score(text_units: TextUnit[], doc: SourceDocument) -> ImportanceAnalysis
```

Contract:
- Must produce a ScoredUnit for every input TextUnit
- Scores must be normalized to [0.0, 1.0]
- Must satisfy INV-S1-001 through INV-S1-004

Default implementation:
- PositionalTFIDFScorer: Positional weighting + term-frequency analysis

### EXT-003: RedundancyDetector Protocol

Defines how redundancy detection algorithms can be swapped.

```
RedundancyDetector Protocol:
    detect_clusters(text_units: TextUnit[], analysis: ImportanceAnalysis) -> RedundancyCluster[]
```

Contract:
- Every TextUnit must belong to exactly one cluster
- Must satisfy INV-S2-001 through INV-S2-004

Default implementation:
- KeywordOverlapClusterer: Jaccard similarity with union-find grouping

### EXT-004: OutputRenderer Protocol

Defines how different output formats can be produced.

```
OutputRenderer Protocol:
    render_summary(blocks: SummaryBlock[], doc: SourceDocument) -> OutputDocument
    render_keypoints(keypoints: KeyPoint[], doc: SourceDocument) -> OutputDocument
    serialize(output: OutputDocument, format: string) -> bytes
```

Contract:
- Must produce valid OutputDocument with all required properties
- Must satisfy all VR-* validation rules for the output type
- Must preserve SourceDocument.language
- Must satisfy GI-001, GI-002, GI-003

Default implementation:
- MarkdownRenderer: Renders .md files with structured formatting

---

## 8. Output Mapping

### MAP-OUT-001: Condensed Summary Rendering

Source: SummaryBlock[] (ordered by section position)
Target: OutputDocument with output_type = "condensed_summary"

Rendering process:
1. Create OutputDocument with output_type = "condensed_summary"
2. For each SummaryBlock, create OutputBlock with block_type = "prose_paragraph"
3. Set OutputDocument.language to SourceDocument.language
4. Set metadata: source_word_count, summary_word_count, compression_ratio
5. Assign validation rules: VR-001, VR-002, VR-003, VR-004

### MAP-OUT-002: Key Points List Rendering

Source: KeyPoint[] (ordered by rank)
Target: OutputDocument with output_type = "key_points_list"

Rendering process:
1. Create OutputDocument with output_type = "key_points_list"
2. For each KeyPoint, create OutputBlock with block_type = "scored_item"
3. Set metadata: importance_score per block
4. Set metadata: total_key_points, score_range
5. Assign validation rules: VR-005, VR-006, VR-007

### MAP-OUT-003: Serialization Format

Serialization must preserve:
- All content text from OutputBlocks
- Ordering from position fields
- Scores from metadata fields
- Language provenance from OutputDocument.language

---

## 9. Component Relationships

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

## 10. Processing Order Constraints

| Constraint ID | Description |
|---|---|
| ORD-001 | PARSED_DOCUMENT must be produced before IMPORTANCE_ANALYSIS |
| ORD-002 | IMPORTANCE_ANALYSIS must be produced before REDUNDANCY_CLUSTERS |
| ORD-003 | REDUNDANCY_CLUSTERS must be produced before KEY_POINTS_RAW |
| ORD-004 | REDUNDANCY_CLUSTERS must be produced before SUMMARY_BLOCKS |
| ORD-005 | KEY_POINTS_RAW must be produced before OUTPUT_DOCUMENTS |
| ORD-006 | SUMMARY_BLOCKS must be produced before OUTPUT_DOCUMENTS |
| ORD-007 | OUTPUT_DOCUMENTS must be produced before CONDENSED_SUMMARY |
| ORD-008 | OUTPUT_DOCUMENTS must be produced before KEY_POINTS_LIST |
| ORD-009 | VALIDATION_REPORT is produced after all output artifacts |
| ORD-010 | RUNTIME_CONFIG, if present, must be loaded before Stage 0 |

---

## 11. Self-Validation

### Completeness Check

| Check | Status |
|---|---|
| Meta schema defines all three layers | PASS |
| All components have typed properties | PASS |
| Component relationships are declared | PASS |
| Input mapping covers all input fields | PASS |
| Output mapping covers all output types | PASS |
| Transformation stages are defined | PASS |
| Invariants are declared per stage | PASS |
| Validation rules are named and typed | PASS |
| Extension mechanism is defined | PASS |
| Fixed vs variable parts are identified | PASS |
| Output-type-agnostic design | PASS |

### Consistency Check

| Check | Status |
|---|---|
| All *_ref fields reference declared components | PASS |
| No orphan components | PASS |
| Validation rules reference valid output types | PASS |
| Stage ordering is acyclic | PASS |
| No contradiction between invariants | PASS |

### Traceability Check

| Source | Traced To |
|---|---|
| BASE_COMPOSITION_STANDARD_v1.0.md | Sections 1-9 adapted to text summarizer domain |
| COMPOSITION_SPEC-01.md | Meta schema, transformation rules, invariants |
| RUNTIME_IMPL-01.md | Pipeline architecture, extension implementations |
| REQUIREMENT_ANALYSIS-01.md | Input/output requirements, constraints |
| simple_text_summarizer.md | Original requirement document |

---

## References

- BASE_COMPOSITION_STANDARD_v1.0.md -- Universal composition system pattern
- COMPOSITION_SPEC-01.md -- Generator composition specification
- RUNTIME_IMPL-01.md -- Runtime implementation design
- REQUIREMENT_ANALYSIS-01.md -- Requirement analysis
- simple_text_summarizer.md -- Original requirement document

---

**End of Composition Standard**
