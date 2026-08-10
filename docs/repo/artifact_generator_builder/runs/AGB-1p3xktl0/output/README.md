# text_summarizer_ayz

Text Summarizer workflow for the agent-runner-v2 platform.

## Overview

This workflow transforms a long-form text document into two output artifacts:

1. **Condensed Summary** -- A prose summary at most 20% of the original word count, preserving the source language and logical structure (introduction, main points, conclusion).
2. **Key Points List** -- An ordered list of extracted key points from the source document, each with an importance score.

## Identity

| Field | Value |
|---|---|
| Codename | text_summarizer_ayz |
| Version | 1.0.0 |
| Pattern | Input Transformation (Pattern 2) |
| Platform | agent-runner-v2 |
| Layer | Layer 3 |

## Input

| Artifact Key | Format | Required | Description |
|---|---|---|---|
| SOURCE_TEXT | .txt or .md | Yes | Long-form text document to summarize |
| RUNTIME_CONFIG | .json or .yaml | No | Optional configuration for pipeline parameters |

## Output

| Artifact Key | Format | Description |
|---|---|---|
| CONDENSED_SUMMARY | .md | Prose summary preserving introduction-main-conclusion structure |
| KEY_POINTS_LIST | .md | Ordered list of key points with importance scores |

## Pipeline Architecture

The workflow follows a 7-stage linear pipeline (Stage 0 through Stage 6) organized into 4 phases:

### Phase 1: Input Preparation (Steps 1-2)

| Step | Type | Description |
|---|---|---|
| validate_input | action | Validates SOURCE_TEXT (V-MAP-IN-001 through V-MAP-IN-007) |
| load_configuration | action | Loads and merges runtime configuration |

### Phase 2: Pipeline Execution (Steps 3-14)

| Step | Type | Stage | Description |
|---|---|---|---|
| parse_input | action | Stage 0 | Parse source text into Layer 1 components |
| score_importance | action | Stage 1 | Score text unit importance (positional TF-IDF) |
| validate_importance | action | Stage 1 | Check INV-S1-001 through INV-S1-004 |
| detect_redundancy | action | Stage 2 | Detect redundant text units (Jaccard similarity) |
| validate_redundancy | action | Stage 2 | Check INV-S2-001 through INV-S2-004 |
| extract_keypoints | action | Stage 3 | Extract key points above threshold |
| validate_keypoints | action | Stage 3 | Check INV-S3-001 through INV-S3-004 |
| compose_summary_blocks | action | Stage 4 | Compose per-section summary blocks |
| validate_summary_blocks | action | Stage 4 | Check INV-S4-001 through INV-S4-005 |
| assemble_output_documents | action | Stage 5 | Assemble output documents |
| validate_assembly | action | Stage 5 | Check INV-S5-001 through INV-S5-004 |
| render_outputs | action | Module 8 | Render outputs to disk |

### Phase 3: Output Validation and Review (Steps 15-16)

| Step | Type | Description |
|---|---|---|
| validate_outputs | action | Evaluate VR-001 through VR-007 rules |
| review_quality | prompt | LLM-based quality assessment |

### Phase 4: Delivery (Steps 17-18)

| Step | Type | Description |
|---|---|---|
| promote_outputs | action | Copy outputs to final directory |
| complete_pipeline | action | Write execution log and completion record |

### Auxiliary Step (Refinement Only)

| Step | Type | Description |
|---|---|---|
| adjust_parameters | prompt | Adjust pipeline parameters based on review feedback |

## Recovery Loops

### Compression Recovery Loop

Triggered when VR-001 fails (compression ratio exceeds 0.20). The pipeline returns to score_importance with an increased keypoint_threshold. Maximum 3 iterations.

| From | To | Max Iterations | Exhausted Code |
|---|---|---|---|
| validate_outputs | score_importance | 3 | COMPRESSION_RECOVERY_EXHAUSTED |

### Quality Review Loop

Triggered when review_quality rejects the outputs. The adjust_parameters step modifies configuration and the pipeline re-executes from parse_input. Maximum 2 iterations.

| From | To | Max Iterations | Exhausted Code |
|---|---|---|---|
| review_quality | adjust_parameters | 2 | QUALITY_REVIEW_EXHAUSTED |

## Configuration

| Parameter | Default | Description |
|---|---|---|
| compression_ratio | 0.20 | Maximum summary/source word count ratio |
| keypoint_threshold | 0.30 | Minimum importance score for key point extraction |
| similarity_threshold | 0.60 | Jaccard similarity threshold for redundancy clustering |
| output_format | md | Output serialization format |
| output_types | [condensed_summary, key_points_list] | Which output types to produce |
| scoring_method | positional_tfidf | Importance scoring algorithm |
| clustering_method | keyword_overlap | Redundancy detection algorithm |
| language_detection | auto | Language detection method |

Configuration priority: CLI arguments > environment variables (TS_ prefix) > config file > defaults.

## Extension Points

| Protocol | Default | Description |
|---|---|---|
| EXT-001: InputParser | TxtParser, MdParser | Input format parsing |
| EXT-002: ImportanceScorer | PositionalTFIDFScorer | Importance scoring algorithm |
| EXT-003: RedundancyDetector | KeywordOverlapClusterer | Redundancy detection algorithm |
| EXT-004: OutputRenderer | MarkdownRenderer | Output rendering and serialization |

## File Structure

```
text_summarizer_ayz/
    standards/
        COMPOSITION_STANDARD.md
    impls/
        default.impl.md
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
        review_quality.txt
        adjust_parameters.txt
    README.md
```

## Constraints

- Summary word count must not exceed 20% of source word count (GI-003)
- Output language must match source language (GI-001)
- No new information may be introduced (GI-002)
- Logical structure must be preserved (GI-005)
- All output content must trace to source TextUnits (GI-004)

## References

- BASE_COMPOSITION_STANDARD_v1.0.md -- Universal composition system pattern
- COMPOSITION_STANDARD.md -- Generator-specific composition standard
- default.impl.md -- Default runtime implementation design
