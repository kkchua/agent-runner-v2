# Text Summarizer Workflow

Transforms an input text file into a condensed summary via a 10-stage transformation pipeline. The workflow enforces structural constraints (20% max compression, same language, no new information) through deterministic validation and recovery loops.

## Purpose and Functionality

The text_summarizer workflow performs extractive summarization on plain text (.txt) or Markdown (.md) documents. It decomposes the input into structured components, identifies key points, removes redundancy, preserves meaning, and assembles a summary that respects the intro-main point-conclusion structure of the source document.

### Key Capabilities

- Input formats: Plain text (.txt) and Markdown (.md)
- Output format: Matches input format (txt in -> txt out, md in -> md out)
- Maximum compression: Summary is at most 20% of original word count (CON-001)
- Language preservation: Output is in the same language as input (CON-002)
- Fidelity guarantee: No new information is introduced (CON-003)
- Structural integrity: Summary maintains intro -> main points -> conclusion flow (FMT-003)

### Pipeline Architecture

The workflow executes a 10-stage transformation pipeline:

| Stage | Step Name | Description |
|-------|-----------|-------------|
| 1 | parse_input | Parse input into Layer 1 content components |
| 2 | validate_segments | Validate Section/Paragraph/Sentence hierarchy |
| 3 | score_importance | Score sentences for importance |
| 4 | detect_redundancy | Detect and cluster redundant key points |
| 5 | preserve_meaning | Validate section coverage |
| 6 | select_compression | Select key points within word budget |
| 7 | assemble_structure | Assemble summary blocks |
| 8 | validate_language | Validate output language matches input |
| 9 | validate_length | Validate compression ratio |
| 10 | render_output | Render and write summary file |

## Input Artifacts

| Artifact Key | Type | Format | Description |
|--------------|------|--------|-------------|
| INPUT_TEXT_FILE | file | .txt or .md | The source document to be summarized |

### Input Requirements

- File must exist and be readable (INV-001)
- Extension must be .txt or .md (INV-002)
- Content must be non-empty (INV-003)
- Content must be natural language (INV-004)
- At least one section must be detectable (INV-005)
- At least one sentence must be present (INV-006)

## Output Artifacts

| Artifact Key | Type | Format | Description |
|--------------|------|--------|-------------|
| SUMMARY_FILE | file | .txt or .md | The condensed summary document |
| SUMMARY_FILE_PROMOTED | file | .txt or .md | Summary promoted to final delivery location |

### Output Quality Requirements

- SUMMARY-QR-001: Word count at most 20% of original (CON-001)
- SUMMARY-QR-002: Same language as input (CON-002)
- SUMMARY-QR-003: No new information introduced (CON-003)
- SUMMARY-QR-004: Captures core message of the document
- SUMMARY-QR-005: Maintains logical structure (intro -> main points -> conclusion)

## Workflow Steps

The workflow contains 17 steps organized into 4 phases:

### Phase 1: Input Preparation (2 action steps)

| Step | Type | Description |
|------|------|-------------|
| validate_input | action | Validate file existence and format |
| prepare_configuration | action | Construct RuntimeConfig |

### Phase 2: Pipeline Execution (10 action steps)

Each step corresponds to one transformation stage (TR-001 through TR-010).

### Phase 3: Output Validation (1 action, 1 prompt)

| Step | Type | Description |
|------|------|-------------|
| validate_summary | action | Check output validation rules (OV-001 to OV-006) |
| review_quality | prompt | LLM-based quality assessment of summary content |

### Phase 4: Delivery (2 action steps)

| Step | Type | Description |
|------|------|-------------|
| promote_summary | action | Copy summary to final delivery location |
| complete_pipeline | action | Record pipeline completion |

### Auxiliary: Quality Review Refinement

| Step | Type | Description |
|------|------|-------------|
| adjust_parameters | prompt | Adjust pipeline parameters based on quality review feedback |

## Recovery Loops

### Compression Recovery Loop

When validate_length detects that the compression ratio exceeds 0.20, the pipeline returns to select_compression with a tighter word budget. This loop repeats up to 3 times before halting with COMPRESSION_RECOVERY_EXHAUSTED.

### Quality Review Loop

When review_quality determines that the summary does not meet quality standards, the workflow enters an adjustment loop through adjust_parameters. This loop repeats up to 2 times before halting with QUALITY_REVIEW_EXHAUSTED.

## How to Use

### CLI Execution

```bash
ukbe-run-agent run --template-group text_summarizer
```

### Daemon Execution

The workflow can be executed by the daemon when claimed from the backend:

```bash
ukbe-run-agent daemon
```

### Required Configuration

No special configuration is required. The workflow operates on file I/O with no external service dependencies.

### Configuration Overrides

Pipeline parameters can be customized through the RuntimeConfig:

| Parameter | Default | Description |
|-----------|---------|-------------|
| target_compression_ratio | 0.20 | Maximum compression ratio |
| importance_threshold | 0.5 | Minimum score for KeyPoint selection |
| redundancy_similarity_threshold | 0.7 | Similarity threshold for redundancy clustering |
| max_recovery_attempts | 3 | Maximum compression recovery loop iterations |
| output_format_override | None | Force output format ("txt" or "md") |
| scorer_impl | "default" | Importance scorer implementation |
| detector_impl | "default" | Redundancy detector implementation |
| selector_impl | "default" | Compression selector implementation |
| renderer_impl | "default" | Output renderer implementation |

## Extension Points

The workflow supports pluggable implementations for several pipeline stages:

| Extension Point | Protocol | Registry Key |
|-----------------|----------|-------------|
| Importance scoring | ImportanceScorer | "importance_scorer" |
| Redundancy detection | RedundancyDetector | "redundancy_detector" |
| Compression selection | CompressionSelector | "compression_selector" |
| Structure assembly | StructureMaintainer | "structure_maintainer" |
| Output rendering | OutputRenderer | "output_renderer" |

### Adding New Implementations

1. Create a class conforming to the appropriate Protocol
2. Register it in the EXTENSION_REGISTRY under the correct key
3. Reference it by name in RuntimeConfig (e.g., scorer_impl = "tfidf")

### Planned Extensions

| Extension ID | Description |
|--------------|-------------|
| EXT-001 | Bullet-point summary |
| EXT-002 | Executive summary (5% compression) |
| EXT-003 | Key phrases extraction |
| EXT-004 | Section-by-section summary |

## File Structure

```
text_summarizer/
  workflow.toml           -- Workflow manifest (17 steps, 4 phases)
  context_extensions.py   -- Artifact key registration and path resolution
  actions.py              -- Action implementations for all 15 action steps
  prompts/
    01_review_quality.txt      -- Quality review prompt (review_quality step)
    02_adjust_parameters.txt   -- Parameter adjustment prompt (adjust_parameters step)
  README.md               -- This file
```

## Traceability

| Element | Source | Reference |
|---------|--------|-----------|
| Pipeline stages (TR-001 to TR-010) | Requirement Analysis | Transformation Requirements |
| Constraints (CON-001 to CON-003) | Requirement Analysis | Hard Constraints |
| Invariants (INV-T-001 to INV-T-011) | Composition Specification | Transformation Invariants |
| Output validation (OV-001 to OV-006) | Composition Specification | Output Validation Rules |
| Extension points (EXT-001 to EXT-004) | Requirement Analysis | Extension Points |
