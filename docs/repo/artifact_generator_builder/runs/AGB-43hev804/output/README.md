# Text Summarizer (text_summarizer_ayz)

## Overview

The Text Summarizer workflow transforms long text documents (.txt or .md)
into two output artifacts:

1. **CONDENSED_SUMMARY** -- A prose summary at most 20% of the original
   word count, preserving the source language and logical structure
   (introduction, main points, conclusion).

2. **KEY_POINTS_LIST** -- An ordered list of extracted key points from
   the source document, each annotated with an importance score.

This workflow follows the Input Transformation pattern (Composition System
Standard Pattern 2) with a three-layer architecture:

- **Layer 1: Input Parsing** -- Parse input into structured document tree
  (Document -> Sections -> Paragraphs -> Sentences).
- **Layer 2: Transformation** -- Analyze and transform (Key Points,
  Redundancy Clusters, Content Blocks).
- **Layer 3: Output Rendering** -- Render final output artifacts.

## Workflow Identity

| Property | Value |
|----------|-------|
| Codename | text_summarizer_ayz |
| Generator Name | Text Summarizer |
| Version | 1.0.0 |
| Job Prefix | TSUM |
| Pattern | Input Transformation (Pattern 2) |

## Input

| Artifact Key | Format | Required | Description |
|--------------|--------|----------|-------------|
| SOURCE_TEXT_FILE | .txt or .md | Yes | Source text document to be summarized |

The input file must:
- Exist and be readable
- Contain text content (not binary)
- Be non-empty
- Use .txt (plain text) or .md (Markdown) format

## Output

| Artifact Key | Format | Description |
|--------------|--------|-------------|
| CONDENSED_SUMMARY | Markdown (.md) | Prose summary with YAML frontmatter |
| KEY_POINTS_LIST | Markdown (.md) | Structured key points list with YAML frontmatter |

## Constraints

| ID | Constraint |
|----|------------|
| C-001 | Summary word count <= 20% of original word count |
| C-002 | Summary language must match input document language |
| C-003 | Must not introduce information not present in original |

## Step Sequence

The workflow consists of 9 execution steps organized into 4 phases:

### Phase 1: Input Processing

| Step | Type | Description |
|------|------|-------------|
| load_input | Action | Load source file, detect format, reject binary |
| parse_document | Action | Decompose text into Layer 1 document tree |
| validate_layer_1 | Action | Validate all 5 Layer 1 invariants |

### Phase 2: Transformation

| Step | Type | Description |
|------|------|-------------|
| extract_key_points | Prompt | Extract important sentences with importance scores |
| remove_redundancy | Prompt | Identify and cluster semantically similar sentences |
| preserve_meaning | Prompt | Compose summary segments from key points |
| maintain_structure | Action | Enforce document ordering and compression |

### Phase 3: Validation and Output

| Step | Type | Description |
|------|------|-------------|
| validate_output | Action | Validate constraints C-001, C-002, C-003 and L3 invariants |
| render_output | Action | Render CONDENSED_SUMMARY and KEY_POINTS_LIST |

## Refinement Loops

Three prompt-driven steps have self-refinement loops (max 2 iterations):

| Step | Exhaustion Code | Failure Class |
|------|----------------|---------------|
| extract_key_points | EXT_KEYPOINTS_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| remove_redundancy | REDUNDANCY_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| preserve_meaning | MEANING_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |

## File Structure

```
text_summarizer_ayz/
    standards/
        COMPOSITION_STANDARD.md
    impls/
        default/
            default.impl.md
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
        extract_keypoints.txt
        remove_redundancy.txt
        preserve_meaning.txt
    README.md
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_compression_ratio | float | 0.20 | Maximum summary-to-source word ratio |
| min_keypoints | integer | 3 | Minimum key points for docs with > 5 sentences |
| redundancy_threshold | float | 0.75 | Similarity threshold for clustering |
| importance_position_weight | float | 0.15 | Position bonus for intro/conclusion |
| output_format | string | "markdown" | Output serialization format |
| language_detection | string | "auto" | "auto" or explicit ISO 639-1 code |

## Extension Points

| ID | Extension Opportunity | Impact |
|----|----------------------|--------|
| E-001 | Multi-language support with target language selection | Adds translation step to Layer 2 |
| E-002 | Configurable summary length (10%, 30%) | Makes C-001 threshold configurable |
| E-003 | Bullet-point summary format | New output type in Layer 3 |
| E-004 | Section-level summaries for structured documents | New output type |
| E-005 | Importance threshold filtering for key points | Adds filter parameter |

## Traceability

This workflow implements the Text Summarizer specification version 1.0.0.
All design artifacts trace back to the Composition System Standard
(BASE_COMPOSITION_STANDARD_v1.0.md).
