# Text Summarizer Workflow

Version: 1.0.0

## Purpose

The text_summarizer workflow transforms an input text file (.txt or .md)
into a condensed summary at most 20 percent of the original word count.
It preserves the source language and logical structure (introduction,
main points, conclusion).

The workflow implements a 4-stage transformation pipeline:

- T1: Key Point Extraction -- identifies important sentences
- T2: Redundancy Removal -- clusters and eliminates repetition
- T3: Structure Assembly -- groups keypoints into content blocks
- T4: Output Rendering -- produces the final summary text

## Input Artifacts

| Artifact Key | Format | Required | Description |
|---|---|---|---|
| INPUT_TEXT_FILE | .txt, .md | Yes | The text document to summarize |

### Input Validation Rules

- IV-001: File must exist and be readable
- IV-002: File extension must be .txt or .md
- IV-003: File must contain non-empty text
- IV-004: File must be decodable as UTF-8

## Output Artifacts

| Artifact Key | Format | Required | Description |
|---|---|---|---|
| SUMMARY_FILE | .txt | Yes | Condensed summary of the input |
| SUMMARY_FILE_PROMOTED | .txt | Yes | Final promoted summary |

### Output Quality Constraints

- OV-001: Output word count > 0
- OV-002: Compression ratio <= 0.20 (C-001)
- OV-003: Output language matches input language (C-002)
- OV-004: No content untraceable to source (C-003)
- OV-005: Contains intro, main_body, conclusion blocks
- OV-006: All source_keypoint_ids reference valid keypoints
- OV-007: All keypoint_ids in content blocks are valid

## Intermediate Artifacts

The workflow produces intermediate diagnostic artifacts during processing.
These are optional and can be used for debugging or auditing.

| Artifact Key | Location | Description |
|---|---|---|
| RUNTIME_CONFIG_FILE | meta/runtime_config.json | Pipeline configuration snapshot |
| DOC_STRUCTURE_FILE | meta/layer1/doc_structure.json | Parsed document structure (L1-DOC) |
| INPUT_VALIDATION_REPORT | meta/layer1/input_validation.json | Input validation results |
| KEYPOINT_LIST_FILE | meta/layer2/keypoints.json | Extracted keypoints (L2-KP[]) |
| REDUNDANCY_MAP_FILE | meta/layer2/redundancy_map.json | Redundancy clusters (L2-RC[]) |
| CONTENT_BLOCK_LIST_FILE | meta/layer2/content_blocks.json | Content blocks (L2-CB[]) |
| STRUCTURE_MAP_FILE | meta/layer2/structure_map.json | Structure map (L2-SM) |
| TRANSFORMATION_INVARIANT_REPORT | meta/layer2/invariant_report.json | Invariant check results |
| OUTPUT_DOC_FILE | meta/layer3/output_doc.json | Output document (L3-OD) |
| OUTPUT_METADATA_FILE | meta/layer3/output_metadata.json | Output metadata (L3-MD) |
| OUTPUT_VALIDATION_REPORT | meta/layer3/output_validation.json | Output validation results |

## Workflow Steps

| # | Step Name | Type | Phase | Description |
|---|---|---|---|---|
| 1 | validate_input | action | 1 | Validate input file format and content |
| 2 | prepare_configuration | action | 1 | Build RuntimeConfig with pipeline parameters |
| 3 | parse_input | action | 2 | Parse input into L1 document structure |
| 4 | extract_keypoints | action | 2 | Extract key points (Stage T1) |
| 5 | validate_keypoints | action | 2 | Validate T1 invariants |
| 6 | remove_redundancy | action | 2 | Remove redundant keypoints (Stage T2) |
| 7 | validate_redundancy | action | 2 | Validate T2 invariants |
| 8 | assemble_structure | action | 2 | Assemble content blocks (Stage T3) |
| 9 | validate_structure | action | 2 | Validate T3 invariants |
| 10 | render_output | action | 2 | Render summary output (Stage T4) |
| 11 | validate_language | action | 2 | Validate language match (T4-INV-003) |
| 12 | validate_compression | action | 2 | Validate compression ratio (T4-INV-002) |
| 13 | validate_output | action | 3 | Validate output rules OV-001 to OV-007 |
| 14 | review_quality | prompt | 3 | LLM-based quality review |
| 15 | promote_summary | action | 4 | Copy summary to final location |
| 16 | complete_pipeline | action | 4 | Record pipeline completion |
| 17 | adjust_parameters | prompt | -- | Adjust parameters during quality loop |

## Recovery Loops

### Compression Recovery (max 3 iterations)

When validate_compression (Step 12) detects compression_ratio > 0.20,
the pipeline returns to extract_keypoints (Step 4) with a higher
relevance_threshold. This reduces keypoint count and output size.

Exhausted code: COMPRESSION_RECOVERY_EXHAUSTED (PIPELINE_FAILURE)

### Quality Review (max 2 iterations)

When review_quality (Step 14) rejects the summary, adjust_parameters
(Step 17) modifies RuntimeConfig and the pipeline re-executes from
parse_input (Step 3).

Exhausted code: QUALITY_REVIEW_EXHAUSTED (HUMAN_RETRY_REQUIRED)

## How to Use

### CLI Execution

```bash
ukbe-run-agent run --template-group text_summarizer
```

### Required Setup

1. Place the input text file (.txt or .md) in the job input directory
2. Ensure INPUT_TEXT_FILE artifact path is set in the job state
3. The workflow will produce SUMMARY_FILE in the output directory

### Configuration

The pipeline accepts the following runtime parameters (defaults in
parentheses):

| Parameter | Default | Description |
|---|---|---|
| relevance_threshold | 0.5 | Minimum importance score for keypoint selection |
| redundancy_threshold | 0.8 | Similarity threshold for redundancy clustering |
| target_compression_ratio | 0.20 | Maximum compression ratio (C-001) |
| output_type | summary | Output format discriminator |

## Extension Points

The following components are extensible via Protocol interfaces:

| Protocol | Extension Point | Description |
|---|---|---|
| IP-001 | InputParser | Sentence tokenization, language detection |
| TA-001 | ImportanceScorer | Scoring algorithm for keypoint importance |
| TA-002 | SemanticSimilarity | Similarity computation for redundancy detection |
| TA-003 | WordCounter | Word counting method |
| OR-001 | OutputRenderer | Output format rendering (summary, bullet_points, etc.) |

New implementations can be registered in the EXTENSION_REGISTRY and
referenced by name in the RuntimeConfig.

## Constraints

| Constraint | Rule | Enforcement |
|---|---|---|
| C-001 | Summary at most 20% of original word count | T4-INV-002, validate_compression |
| C-002 | Same language as input | T4-INV-003, validate_language |
| C-003 | No new information not in original | T4-INV-004, structural enforcement |
| C-004 | Only .txt and .md input accepted | IV-002, validate_input |

## File Structure

```
workflow.toml              # Workflow manifest
context_extensions.py      # Artifact key registration and path resolution
actions.py                 # Action-driven step implementations
prompts/
  14_review_quality.txt    # Quality review prompt
  17_adjust_parameters.txt # Parameter adjustment prompt
README.md                  # This file
```
