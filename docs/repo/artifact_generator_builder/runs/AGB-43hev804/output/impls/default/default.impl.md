---
doc_type: "default_impl"
identity_locked: true
generator_name: "text_summarizer_ayz"
codename: "text_summarizer_ayz"
version: "1.0.0"
composition_spec: "COMPOSITION_SPEC-01.md"
base_standard: "BASE_COMPOSITION_STANDARD_v1.0.md"
---

# Default Runtime Implementation

## Overview

This document is the default runtime implementation for the Text Summarizer
generator (codename: text_summarizer_ayz). It provides the complete component
mapping from abstract step interfaces to concrete prompt templates and action
functions, as required by BASE_COMPOSITION_STANDARD_v1.0.md Section 10.1 and
Section 13.8.

This implementation satisfies the composition specification defined in
COMPOSITION_SPEC-01.md. It produces two output artifacts: CONDENSED_SUMMARY
and KEY_POINTS_LIST.

---

## Implementation Identity

| Property | Value |
|----------|-------|
| Implementation Name | default |
| Codename | text_summarizer_ayz |
| Generator Name | Text Summarizer |
| Pattern | Input Transformation (Pattern 2) |
| Supported Output Types | summary, key_points |

---

## Component Mapping

This section maps each abstract step defined in the composition spec to its
concrete implementation component (prompt template or action function).

### Step Mapping Table

| Abstract Step | Step ID | Component Type | Component Reference |
|---------------|---------|----------------|-------------------|
| Load Input | LOAD-001 | Action | shared: actions.load_input_file |
| Parse Document | PARSE-001 | Action | shared: actions.parse_document |
| Validate Layer 1 | VAL-L1-001 | Action | shared: actions.validate_layer1 |
| Extract Key Points | STEP-EXT-001 | Prompt | shared: prompts/extract_keypoints.txt |
| Remove Redundancy | STEP-RED-001 | Prompt | shared: prompts/remove_redundancy.txt |
| Preserve Meaning | STEP-MEAN-001 | Prompt | shared: prompts/preserve_meaning.txt |
| Maintain Structure | STEP-STR-001 | Action | shared: actions.maintain_structure |
| Validate Output | VAL-OUT-001 | Action | shared: actions.validate_output |
| Render Output | RENDER-001 | Action | shared: actions.render_output |

### Validation via Refinement Loops

The prompt-driven steps (STEP-EXT-001, STEP-RED-001, STEP-MEAN-001) do not
have separate validation action steps. Instead, validation is handled through
the on_reject_refine loop mechanism configured in workflow.toml:

| Step | Validation Artifact | Refinement Loop |
|------|--------------------|--------------------|
| Extract Key Points | KEY_POINTS_DATA | max_iterations=2, exhausted_failure_code=EXT_KEYPOINTS_RETRY_EXHAUSTED |
| Remove Redundancy | REDUNDANCY_CLUSTERS | max_iterations=2, exhausted_failure_code=REDUNDANCY_RETRY_EXHAUSTED |
| Preserve Meaning | CONTENT_BLOCKS | max_iterations=2, exhausted_failure_code=MEANING_RETRY_EXHAUSTED |

### Component Source Convention

- "shared:" -- component is in the workflow package root (available to all implementations)

---

## Data Structures

### Layer 1: ParsedDocument

The ParsedDocument is the intermediate representation produced by input parsing.

```
ParsedDocument:
  metadata: DocumentMetadata
  sections: list[Section]

DocumentMetadata:
  document_id: string          # UUID generated at parse time
  source_format: string        # "txt" or "md"
  language: string             # ISO 639-1 code (e.g., "en")
  total_word_count: int        # Whitespace-delimited token count
  total_sentence_count: int    # Sentence-ending punctuation count
  total_paragraph_count: int   # Blank-line-separated block count
  total_section_count: int     # Top-level section count

Section:
  section_id: string           # UUID
  heading: string              # Heading text or empty
  section_type: string         # "introduction" | "body" | "conclusion"
  position: int                # Zero-based ordinal
  paragraph_count: int
  word_count: int
  paragraphs: list[Paragraph]

Paragraph:
  paragraph_id: string         # UUID
  section_ref: string          # Parent Section.section_id
  position: int                # Zero-based within section
  word_count: int
  sentence_count: int
  content: string              # Raw text
  sentences: list[Sentence]

Sentence:
  sentence_id: string          # UUID
  paragraph_ref: string        # Parent Paragraph.paragraph_id
  section_ref: string          # Grandparent Section.section_id
  position: int                # Zero-based within paragraph
  word_count: int
  content: string              # Raw text
```

### Layer 2: TransformedContent

```
TransformedContent:
  keypoints: list[KeyPoint]
  redundancy_clusters: list[RedundancyCluster]
  content_blocks: list[ContentBlock]

KeyPoint:
  keypoint_id: string          # UUID
  source_sentence_refs: list[string]  # Sentence.sentence_id values
  content: string
  importance_score: float      # [0.0, 1.0]
  section_ref: string          # Source Section.section_id
  position: int

RedundancyCluster:
  cluster_id: string           # UUID
  member_sentence_refs: list[string]
  representative_ref: string   # Must be in member_sentence_refs
  similarity_score: float      # [0.0, 1.0]

ContentBlock:
  block_id: string             # UUID
  block_type: string           # "summary_segment" | "key_point_entry" | "structural_bridge"
  content: string
  source_refs: list[string]    # Sentence.sentence_id or KeyPoint.keypoint_id
  position: int
  word_count: int
```

### Layer 3: OutputDocument

```
OutputDocument:
  output_type: string          # "summary" | "key_points"
  metadata: OutputMetadata
  content_blocks: list[ContentBlock]   # Ordered, from Layer 2
  validation_rules: list[ValidationRule]

OutputMetadata:
  source_document_id: string
  output_word_count: int
  compression_ratio: float     # output_word_count / total_word_count
  language: string
  generation_timestamp: string # ISO 8601

ValidationRule:
  rule_id: string
  rule_name: string
  rule_type: string            # "compression" | "language_preservation" | "no_new_info" | "structure_preservation"
  threshold: any
  description: string
```

---

## Algorithm Descriptions

### Algorithm: Input Loading (LOAD-001)

Type: Action (deterministic)

```
function load_input_file(file_path: string) -> RawInput:
  1. Check file_path exists and is readable.
     - If not: raise FileNotFoundError.
  2. Read file content using UTF-8 encoding.
     - If encoding fails: attempt UTF-16, then Latin-1.
     - If all fail: raise EncodingError.
  3. Scan first 8192 bytes for null bytes (0x00).
     - If found: raise BinaryContentError.
  4. Strip leading/trailing whitespace.
  5. If content length is 0: raise EmptyDocumentError.
  6. Detect format from file extension:
     - ".md" -> source_format = "md"
     - ".txt" -> source_format = "txt"
     - Other: raise UnsupportedFormatError.
  7. Return RawInput(content=stripped_text, source_format=format, file_path=path).
```

### Algorithm: Document Parsing (PARSE-001)

Type: Action (deterministic)

```
function parse_document(raw: RawInput) -> ParsedDocument:
  1. Generate document_id = UUID4.
  2. Detect language:
     - Use trigram frequency analysis against known language profiles.
     - Default to "en" if detection confidence < 0.6.
  3. Split content into paragraphs:
     - Split on double-newline (or more) boundaries.
     - Trim each paragraph.
     - Discard empty paragraphs.
  4. For Markdown input (source_format == "md"):
     a. Scan for heading markers (lines starting with # ## ### etc.).
     b. Group paragraphs under their preceding heading.
     c. Text before any heading belongs to an implicit first section.
     d. Assign section_type by position:
        - First section -> "introduction"
        - Last section -> "conclusion"
        - All others -> "body"
     e. If no headings found: treat entire document as single "body" section.
  5. For Plain Text input (source_format == "txt"):
     a. If paragraph count >= 3:
        - First paragraph -> "introduction"
        - Last paragraph -> "conclusion"
        - All middle paragraphs -> single "body" section
     b. If paragraph count < 3:
        - All paragraphs -> single "body" section
  6. For each paragraph, split into sentences:
     - Delimit on: period, exclamation mark, question mark
     - Followed by: whitespace or end-of-string
     - Handle abbreviations: common patterns (e.g., "Mr.", "Dr.", "U.S.")
       are not treated as sentence boundaries.
  7. Assign unique IDs (UUID4) to each Section, Paragraph, Sentence.
  8. Compute word_count for each component (whitespace-delimited tokens).
  9. Compute aggregate counts for DocumentMetadata.
  10. Return ParsedDocument.
```

### Algorithm: Layer 1 Validation (VAL-L1-001)

Type: Action (deterministic)

```
function validate_layer1(doc: ParsedDocument) -> ValidationResult:
  errors = []

  # INV-L1-001: Every Sentence belongs to exactly one Paragraph
  for each section in doc.sections:
    for each paragraph in section.paragraphs:
      for each sentence in paragraph.sentences:
        if sentence.paragraph_ref != paragraph.paragraph_id:
          errors.append("INV-L1-001: Sentence {id} has invalid paragraph_ref")

  # INV-L1-002: Every Paragraph belongs to exactly one Section
  for each section in doc.sections:
    for each paragraph in section.paragraphs:
      if paragraph.section_ref != section.section_id:
        errors.append("INV-L1-002: Paragraph {id} has invalid section_ref")

  # INV-L1-003: Sum of Section word_counts equals total
  section_sum = sum(s.word_count for s in doc.sections)
  if section_sum != doc.metadata.total_word_count:
    errors.append("INV-L1-003: Section word sum {section_sum} != total {total}")

  # INV-L1-004: Sum of Sentence word_counts equals total
  sentence_sum = sum(sent.word_count for section in doc.sections
                     for para in section.paragraphs
                     for sent in para.sentences)
  if sentence_sum != doc.metadata.total_word_count:
    errors.append("INV-L1-004: Sentence word sum {sentence_sum} != total {total}")

  # INV-L1-005: total_word_count > 0
  if doc.metadata.total_word_count <= 0:
    errors.append("INV-L1-005: total_word_count must be > 0")

  return ValidationResult(passed=len(errors)==0, errors=errors)
```

### Algorithm: Extract Key Points (STEP-EXT-001)

Type: Prompt (LLM-driven)

```
function extract_key_points(doc: ParsedDocument) -> list[KeyPoint]:
  1. Build the prompt context:
     a. Serialize all Sentences with their sentence_id, section_ref, position.
     b. Include DocumentMetadata (language, total counts).
     c. Include section structure (headings, section_types).

  2. Construct the extraction prompt (see prompts/extract_keypoints.txt):
     - "Given the following document, extract the most important sentences."
     - "For each key point, provide: sentence_ids, content, importance_score (0.0-1.0)."
     - "Assign higher importance to: introductory statements, concluding statements,
        topic sentences, sentences with unique keywords."
     - "Produce at least 3 key points."
     - "Cover all sections of the document."
     - "Use the SAME LANGUAGE as the source document."
     - "Do NOT add information not present in the source."

  3. Send prompt to LLM coder.
  4. Parse the structured response into KeyPoint objects.
  5. Validate:
     - Each KeyPoint has at least one source_sentence_ref (INV-L2-001).
     - Each importance_score is in [0.0, 1.0] (INV-L2-002).
  6. If validation fails, retry up to 2 times with error feedback
     (via on_reject_refine loop in workflow.toml).
  7. If still failing after retries, raise CoderResponseError.
  8. Return list[KeyPoint].
```

### Algorithm: Importance Scoring (Default)

The default importance scoring combines three weighted factors:

```
function compute_importance(sentence: Sentence, doc: ParsedDocument) -> float:
  # Factor 1: Position weight
  position_weight = 0.0
  if sentence is in the first paragraph of an "introduction" section:
    position_weight += 0.15
  if sentence is in the last paragraph of a "conclusion" section:
    position_weight += 0.15
  if sentence.position == 0 within its paragraph:
    position_weight += 0.05  # Topic sentence bonus

  # Factor 2: Keyword density weight
  # Count content words (non-stopwords) relative to document average
  sentence_word_density = count_content_words(sentence) / sentence.word_count
  doc_avg_density = avg_content_word_density(doc)
  frequency_weight = (sentence_word_density / doc_avg_density) * 0.3
  # Clamp to [0.0, 0.3]

  # Factor 3: Uniqueness weight
  # Cosine similarity with previously selected key points
  # Lower similarity = higher uniqueness
  uniqueness_weight = (1.0 - max_similarity_to_existing) * 0.4

  raw_score = position_weight + frequency_weight + uniqueness_weight
  # Normalize across all sentences to [0.0, 1.0]
  return normalize(raw_score, min_possible, max_possible)
```

### Algorithm: Remove Redundancy (STEP-RED-001)

Type: Prompt (LLM-driven)

```
function remove_redundancy(doc: ParsedDocument, keypoints: list[KeyPoint]) -> list[RedundancyCluster]:
  1. Build the prompt context:
     a. Serialize all Sentences with their sentence_id and section_ref.
     b. Include the extracted KeyPoints for reference.

  2. Construct the redundancy prompt (see prompts/remove_redundancy.txt):
     - "Identify groups of sentences that express the same idea."
     - "For each group: list member sentence_ids, select the most concise
        and clear representative sentence_id."
     - "Sentences must be in the same section to form a cluster."
     - "Provide a similarity_score (0.0-1.0) for each cluster."

  3. Send prompt to LLM coder.
  4. Parse the structured response into RedundancyCluster objects.
  5. Validate:
     - Each cluster has >= 2 member sentences.
     - All members belong to the same Section (INV-L2-003).
     - representative_ref is in member_sentence_refs (INV-L2-004).
  6. Post-processing:
     - If two KeyPoints reference sentences in the same cluster, merge them.
     - The merged KeyPoint references the representative sentence.
  7. If validation fails, retry up to 2 times
     (via on_reject_refine loop in workflow.toml).
  8. Return list[RedundancyCluster].
```

### Algorithm: Preserve Meaning (STEP-MEAN-001)

Type: Prompt (LLM-driven)

```
function preserve_meaning(doc: ParsedDocument, keypoints: list[KeyPoint],
                          clusters: list[RedundancyCluster]) -> list[ContentBlock]:
  1. Build the prompt context:
     a. All KeyPoints sorted by importance_score descending.
     b. RedundancyCluster representatives.
     c. DocumentMetadata (language, structure).
     d. Source Sentences for each KeyPoint.

  2. Construct the meaning prompt (see prompts/preserve_meaning.txt):
     - "Compose a summary from the key points below."
     - "Use ONLY content from the source sentences. Do NOT introduce new information."
     - "Preserve the source language: {language}."
     - "Structure: introduction content first, body content in order, conclusion last."
     - "For each content segment, list the source_sentence_refs that support it."
     - "Target length: at most 20% of the original word count ({max_words} words)."

  3. Send prompt to LLM coder.
  4. Parse the structured response into ContentBlock objects with
     block_type = "summary_segment".
  5. Validate:
     - Each ContentBlock.source_refs resolves to valid Sentence or KeyPoint (INV-L2-005).
     - No content in blocks originates from outside the source (INV-L2-006).
       Verification: check that paraphrases can be traced to source sentences.
  6. If validation fails, retry up to 2 times with specific error feedback
     (via on_reject_refine loop in workflow.toml).
  7. Return list[ContentBlock].
```

### Algorithm: Maintain Structure (STEP-STR-001)

Type: Action (deterministic)

```
function maintain_structure(blocks: list[ContentBlock], doc: ParsedDocument) -> list[ContentBlock]:
  1. Map each ContentBlock to its source section via source_refs:
     - For each source_ref, find the corresponding Sentence.
     - Find the Sentence's section_ref.
     - Associate the ContentBlock with that Section.

  2. Order ContentBlocks by Section position:
     - Introduction section blocks first (position 0).
     - Body section blocks in original section order.
     - Conclusion section blocks last.
     - Within each section, preserve the order from STEP-MEAN-001.

  3. Reassign position values sequentially (0, 1, 2, ...).

  4. Check section transitions:
     - If two consecutive blocks belong to different sections AND
       there is no structural_bridge between them:
       a. Generate a structural_bridge ContentBlock with transitional text.
       b. Bridge text is a deterministic template: "Continuing with {section_heading}..."
       c. Insert the bridge at the transition point.

  5. Compute word counts:
     - For each ContentBlock: word_count = count words in content.
     - Aggregate: total_summary_words = sum of "summary_segment" block word_counts.

  6. Check C-001 constraint:
     - max_allowed_words = floor(doc.metadata.total_word_count * 0.20)
     - If total_summary_words > max_allowed_words:
       a. Sort summary_segment blocks by their minimum source importance_score ascending.
       b. Remove lowest-importance blocks until total_summary_words <= max_allowed_words.
       c. Re-sequence positions.

  7. Return final ordered list[ContentBlock].
```

### Algorithm: Output Validation (VAL-OUT-001)

Type: Action (deterministic)

```
function validate_output(output: OutputDocument, doc: ParsedDocument) -> ValidationResult:
  errors = []

  # C-001: Compression ratio <= 0.20
  if output.metadata.compression_ratio > 0.20:
    errors.append("C-001: compression_ratio {ratio} exceeds 0.20")

  # C-002: Language matches source
  if output.metadata.language != doc.metadata.language:
    errors.append("C-002: output language {out_lang} != source {src_lang}")

  # C-003: No external information
  for block in output.content_blocks:
    for ref in block.source_refs:
      if ref does not resolve to a Sentence or KeyPoint in doc:
        errors.append("C-003: source_ref {ref} has no provenance")

  # INV-L3-001: Language match (redundant with C-002 but explicit)
  # INV-L3-002: ContentBlocks reference valid L2 components
  for block in output.content_blocks:
    for ref in block.source_refs:
      if ref not in all_keypoint_ids and ref not in all_sentence_ids:
        errors.append("INV-L3-002: block {id} has invalid source_ref {ref}")

  # INV-L3-003: Validation rules include all constraints
  required_rule_types = {"compression", "language_preservation", "no_new_info", "structure_preservation"}
  actual_rule_types = {r.rule_type for r in output.validation_rules}
  if not required_rule_types.issubset(actual_rule_types):
    errors.append("INV-L3-003: missing required validation rules")

  return ValidationResult(passed=len(errors)==0, errors=errors)
```

### Algorithm: Output Rendering (RENDER-001)

Type: Action (deterministic)

```
function render_output(doc: ParsedDocument, content: TransformedContent,
                       config: RuntimeConfig) -> list[OutputArtifact]:
  artifacts = []

  # --- CONDENSED_SUMMARY ---
  1. Select ContentBlocks where block_type == "summary_segment".
  2. Sort by position ascending.
  3. Concatenate content into prose form:
     - Join with single space between blocks.
     - Preserve paragraph breaks between sections.
  4. Compute output_word_count = sum of block word_counts.
  5. Compute compression_ratio = output_word_count / doc.metadata.total_word_count.
  6. Build OutputMetadata:
     - source_document_id = doc.metadata.document_id
     - output_word_count
     - compression_ratio
     - language = doc.metadata.language
     - generation_timestamp = ISO 8601 current time
  7. Build ValidationRule[]:
     - VR-C001: compression, threshold=0.20, "Summary <= 20% of source"
     - VR-C002: language_preservation, threshold=doc.metadata.language
     - VR-C003: no_new_info, threshold=null
     - VR-STR: structure_preservation, threshold=null
  8. Assemble OutputDocument for "summary" type.
  9. Serialize to Markdown with YAML frontmatter.
  10. artifacts.append(summary_artifact)

  # --- KEY_POINTS_LIST ---
  1. Select all KeyPoint components from content.keypoints.
  2. Sort by importance_score descending (default order).
  3. Format as numbered list:
     - "1. {content} (importance: {score})"
     - "2. {content} (importance: {score})"
     - ...
  4. Build OutputMetadata for key_points type:
     - source_document_id = doc.metadata.document_id
     - output_word_count = sum of keypoint word counts
     - compression_ratio = N/A (set to 0.0 for key_points type)
     - language = doc.metadata.language
     - generation_timestamp = ISO 8601 current time
  5. Assemble OutputDocument for "key_points" type.
  6. Serialize to Markdown with YAML frontmatter.
  7. artifacts.append(keypoints_artifact)

  return artifacts
```

---

## Prompt Templates

### prompts/extract_keypoints.txt

```
You are a text analysis assistant. Given the following document, extract the most
important sentences as key points.

DOCUMENT METADATA:
- Language: {language}
- Total words: {total_word_count}
- Total sentences: {total_sentence_count}
- Sections: {section_count}

DOCUMENT STRUCTURE:
{section_structure}

SENTENCES:
{serialized_sentences}

INSTRUCTIONS:
1. Identify the most important sentences in the document.
2. For each key point, provide:
   - keypoint_id: a unique identifier (e.g., "kp-001")
   - source_sentence_refs: list of sentence_ids that support this point
   - content: the key point text (may be a direct quote or slight paraphrase)
   - importance_score: a float between 0.0 and 1.0
   - section_ref: the section_id where this key point originates
3. Produce at least 3 key points.
4. Cover all sections of the document.
5. Use the SAME LANGUAGE as the source document ({language}).
6. Do NOT add any information not present in the source text.
7. Assign higher importance to introductory statements, concluding statements,
   topic sentences, and sentences with unique keywords.

OUTPUT FORMAT:
Return a JSON array of key point objects.
```

### prompts/remove_redundancy.txt

```
You are a text analysis assistant. Given the following sentences from a document,
identify groups of sentences that express the same idea (redundancy).

DOCUMENT STRUCTURE:
{section_structure}

SENTENCES:
{serialized_sentences}

EXTRACTED KEY POINTS:
{serialized_keypoints}

INSTRUCTIONS:
1. Identify groups of sentences that express the same or very similar ideas.
2. For each group (redundancy cluster), provide:
   - cluster_id: a unique identifier (e.g., "rc-001")
   - member_sentence_refs: list of sentence_ids in this cluster
   - representative_ref: the sentence_id of the most concise and clear sentence
   - similarity_score: a float between 0.0 and 1.0 indicating semantic overlap
3. All sentences in a cluster MUST belong to the same section.
4. The representative_ref MUST be one of the member_sentence_refs.
5. Each cluster must contain at least 2 sentences.
6. Select the representative as the shortest sentence that captures the core idea.

OUTPUT FORMAT:
Return a JSON array of redundancy cluster objects.
```

### prompts/preserve_meaning.txt

```
You are a summarization assistant. Compose a condensed summary from the extracted
key points below.

DOCUMENT METADATA:
- Language: {language}
- Total words: {total_word_count}
- Maximum summary words: {max_summary_words}

DOCUMENT STRUCTURE:
{section_structure}

KEY POINTS (sorted by importance):
{serialized_keypoints}

SOURCE SENTENCES FOR KEY POINTS:
{source_sentences}

INSTRUCTIONS:
1. Compose a summary using ONLY content from the key points and their source sentences.
2. Do NOT introduce any information not present in the source text.
3. Preserve the source language: {language}.
4. Structure the summary as:
   - Introduction content first
   - Body content in document order
   - Conclusion content last
5. For each summary segment, list the source_sentence_refs that support it.
6. Target word count: at most {max_summary_words} words (20% of original).
7. Ensure the core message (highest-importance key points) is present.

OUTPUT FORMAT:
Return a JSON array of content block objects:
- block_id: unique identifier
- block_type: "summary_segment"
- content: the summary text for this segment
- source_refs: list of sentence_ids supporting this segment
- position: ordinal position (0-based)
```

---

## Configuration

### Default Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_compression_ratio | float | 0.20 | Maximum summary-to-source word ratio |
| min_keypoints | integer | 3 | Minimum key points for docs with > 5 sentences |
| redundancy_threshold | float | 0.75 | Similarity threshold for clustering |
| importance_position_weight | float | 0.15 | Position bonus for intro/conclusion |
| importance_frequency_weight | float | 0.30 | Max keyword density weight |
| importance_uniqueness_weight | float | 0.40 | Max semantic uniqueness weight |
| output_format | string | "markdown" | Output serialization format |
| language_detection | string | "auto" | "auto" or explicit ISO 639-1 code |
| max_retries | integer | 2 | Max LLM coder retries on validation failure |
| encoding_fallback | list | ["utf-8", "utf-16", "latin-1"] | Encoding detection order |

### Override Priority

1. Workflow invocation arguments (highest priority).
2. Environment variables with prefix TEXTSUM_ (e.g., TEXTSUM_MAX_COMPRESSION_RATIO).
3. Default values listed above (lowest priority).

---

## Extension Point Implementations

### Protocol: InputParser

Default implementation: DefaultInputParser

```
class DefaultInputParser:
  def parse(source_file: str) -> ParsedDocument:
    # Implements LOAD-001 and PARSE-001
    raw = load_input_file(source_file)
    return parse_document(raw)

  def validate(parsed: ParsedDocument) -> ValidationResult:
    # Implements VAL-L1-001
    return validate_layer1(parsed)
```

To add a new parser (e.g., PDFInputParser):
1. Implement the InputParser protocol.
2. Ensure parse() returns a ParsedDocument conforming to Layer 1 schema.
3. Register for the new file extension (.pdf).

### Protocol: TransformationAlgorithm

Default implementation: DefaultTransformationAlgorithm

```
class DefaultTransformationAlgorithm:
  def extract_key_points(parsed: ParsedDocument) -> list[KeyPoint]:
    # Implements STEP-EXT-001 via prompt template
    return extract_key_points(parsed)

  def remove_redundancy(keypoints: list[KeyPoint], parsed: ParsedDocument) -> list[RedundancyCluster]:
    # Implements STEP-RED-001 via prompt template
    return remove_redundancy(parsed, keypoints)

  def preserve_meaning(keypoints: list[KeyPoint], clusters: list[RedundancyCluster]) -> list[ContentBlock]:
    # Implements STEP-MEAN-001 via prompt template
    return preserve_meaning(doc, keypoints, clusters)

  def maintain_structure(blocks: list[ContentBlock], parsed: ParsedDocument) -> list[ContentBlock]:
    # Implements STEP-STR-001 via deterministic action
    return maintain_structure(blocks, parsed)
```

To add a new algorithm (e.g., TextRankTransformationAlgorithm):
1. Implement the TransformationAlgorithm protocol.
2. Ensure all invariants hold (INV-L2-001 through INV-L2-006).
3. Register in the implementation's component mapping.

### Protocol: OutputRenderer

Default implementation: DefaultOutputRenderer

```
class DefaultOutputRenderer:
  def render_summary(blocks: list[ContentBlock], metadata: OutputMetadata) -> str:
    # Implements CONDENSED_SUMMARY rendering per MAP-OM-001
    return render_condensed_summary(blocks, metadata)

  def render_keypoints(points: list[KeyPoint], metadata: OutputMetadata) -> str:
    # Implements KEY_POINTS_LIST rendering per MAP-OM-002
    return render_key_points_list(points, metadata)

  def supports_output_type(output_type: str) -> bool:
    return output_type in ["summary", "key_points"]
```

To add a new output type renderer (e.g., BulletPointRenderer):
1. Implement the OutputRenderer protocol.
2. Add render_bullet_points() method.
3. Update supports_output_type() to include "bullet_points".

### Protocol: ValidationStrategy

Default implementation: RuleBasedValidationStrategy

```
class RuleBasedValidationStrategy:
  def validate_output(output: OutputDocument, parsed: ParsedDocument) -> ValidationResult:
    # Implements VAL-OUT-001
    return validate_output(output, parsed)

  def check_constraint(constraint_id: str, output: OutputDocument) -> ConstraintResult:
    if constraint_id == "C-001":
      return check_compression(output)
    elif constraint_id == "C-002":
      return check_language(output)
    elif constraint_id == "C-003":
      return check_provenance(output)
    else:
      return ConstraintResult(passed=False, error="Unknown constraint")
```

To add a new validation strategy (e.g., MLBasedValidationStrategy):
1. Implement the ValidationStrategy protocol.
2. Ensure all constraints (C-001 through C-003) are checked.
3. Register in the implementation's component mapping.

---

## Error Handling

### Error Types

| Error | Condition | Raised By |
|-------|-----------|-----------|
| FileNotFoundError | SOURCE_TEXT_FILE does not exist | InputLoader |
| EmptyDocumentError | File content is empty after stripping | InputLoader |
| BinaryContentError | Null bytes detected in content | InputLoader |
| UnsupportedFormatError | File extension not .txt or .md | InputLoader |
| EncodingError | All encoding attempts fail | InputLoader |
| StructureError | Layer 1 invariant violation | DocumentParser |
| CoderResponseError | LLM coder returns invalid/unparseable response | TransformationEngine |
| ProvenanceError | Content without source traceability | TransformationEngine |
| ConstraintViolationError | C-001, C-002, or C-003 violation | OutputValidator |

### Recovery Strategy

- FileNotFoundError, EmptyDocumentError, BinaryContentError, UnsupportedFormatError:
  Halt immediately. These are unrecoverable input errors.

- StructureError: Halt with diagnostic. Layer 1 must be structurally sound.

- CoderResponseError: Retry the prompt step up to max_retries (default: 2) times,
  appending the validation error to the prompt for context. If all retries fail, halt.

- ProvenanceError: Retry STEP-MEAN-001 with explicit feedback about the violating content.
  If still failing, halt.

- ConstraintViolationError (C-001 only): Attempt recovery by trimming lowest-importance
  ContentBlocks. If compression is still violated after trimming all removable blocks, halt.

- ConstraintViolationError (C-002, C-003): Halt immediately. These indicate fundamental
  issues that cannot be auto-recovered.

---

## Pipeline Execution Flow

```
ENTRY: SOURCE_TEXT_FILE path provided

[LOAD-001: Load Input]
  -> RawInput(content, format, path)
  -> On error: HALT with diagnostic

[PARSE-001: Parse Document]
  -> ParsedDocument (Layer 1)
  -> On error: HALT with diagnostic

[VAL-L1-001: Validate Layer 1]
  -> ValidationResult
  -> On failure: HALT with invariant diagnostic

[STEP-EXT-001: Extract Key Points] (Prompt)
  -> list[KeyPoint]
  -> On validation failure: retry via on_reject_refine (max 2 iterations)
  -> On exhaustion: HALT with EXT_KEYPOINTS_RETRY_EXHAUSTED

[STEP-RED-001: Remove Redundancy] (Prompt)
  -> list[RedundancyCluster]
  -> On validation failure: retry via on_reject_refine (max 2 iterations)
  -> On exhaustion: HALT with REDUNDANCY_RETRY_EXHAUSTED

[STEP-MEAN-001: Preserve Meaning] (Prompt)
  -> list[ContentBlock] (summary_segment)
  -> On validation failure: retry via on_reject_refine (max 2 iterations)
  -> On exhaustion: HALT with MEANING_RETRY_EXHAUSTED

[STEP-STR-001: Maintain Structure] (Action)
  -> list[ContentBlock] (final ordered)
  -> On C-001 violation: trim blocks; re-check

[VAL-OUT-001: Validate Output]
  -> ValidationResult (C-001, C-002, C-003)
  -> On failure: HALT with constraint diagnostic

[RENDER-001: Render Output]
  -> CONDENSED_SUMMARY artifact
  -> KEY_POINTS_LIST artifact

EXIT: Write artifacts to output directory
```

---

## File Structure After Promotion

```
workflows/text_summarizer_ayz/
    standards/
        COMPOSITION_STANDARD.md
    impls/
        default/
            default.impl.md              <- this document
    workflow.toml
    context_extensions.py
    actions.py                           <- shared: load_input_file, parse_document,
                                            validate_layer1, maintain_structure,
                                            validate_output, render_output
    prompts/
        extract_keypoints.txt
        remove_redundancy.txt
        preserve_meaning.txt
    README.md
```

---

## Self-Validation

| Check | Status | Notes |
|-------|--------|-------|
| All abstract steps mapped to concrete components | PASS | 9 steps mapped: 6 actions + 3 prompts |
| Complete algorithm descriptions | PASS | All 9 algorithms documented with step-by-step logic |
| Data structures fully specified | PASS | Layer 1, 2, 3 structures with all properties and types |
| Configuration defaults provided | PASS | 10 parameters with defaults documented |
| Extension point implementations provided | PASS | 4 protocols with default implementations |
| Error handling strategy defined | PASS | 9 error types with recovery strategies |
| Pipeline execution flow documented | PASS | 9-step flow with error paths and refinement loops |
| All invariants addressed | PASS | INV-L1 through INV-L3 checked at appropriate stages |
| All constraints enforced | PASS | C-001, C-002, C-003 validated in VAL-OUT-001 |
| Prompt templates specified | PASS | 3 prompt templates for STEP-EXT, STEP-RED, STEP-MEAN |
| Output artifacts defined | PASS | CONDENSED_SUMMARY and KEY_POINTS_LIST with format specs |
| Traces to composition spec | PASS | Every element references COMPOSITION_SPEC-01.md |
| No invented scope | PASS | All content derived from input artifacts |
| No phantom references | PASS | Component mapping matches workflow.toml step definitions exactly |
| ASCII-only | PASS | No em-dashes, curly quotes, or Unicode |
| Identity locked | PASS | generator_name and codename = text_summarizer_ayz |
