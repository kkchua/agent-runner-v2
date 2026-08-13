# Generator Output Artifacts (Variable)

Generator-type workflows produce **variable content artifacts** — the output structure is defined by the requirement document, not fixed.

## Output Pattern

Output artifacts are declared in the requirement document's Output Section:

```yaml
## Output

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `OUTPUT_FILE` | `output/{job_id}/result.md` | Generated output document |
```

## Common Output Types

### Document Outputs
| Type | Artifact Key Pattern | Description |
|---|---|---|
| Summary | `SUMMARY_FILE` | Condensed document |
| Report | `REPORT_FILE` | Structured analysis |
| Analysis | `ANALYSIS_RESULT` | Processed data/insights |

### Media Outputs
| Type | Artifact Key Pattern | Description |
|---|---|---|
| Image | `GENERATED_IMAGE` | Generated image file |
| Video | `GENERATED_VIDEO` | Generated video file |
| Audio | `GENERATED_AUDIO` | Generated audio file |

### Data Outputs
| Type | Artifact Key Pattern | Description |
|---|---|---|
| Processed Data | `PROCESSED_DATA` | Transformed dataset |
| Visualization | `VISUALIZATION_FILE` | Charts, graphs |

## Output Directory Structure

```
{output_dir}/{job_id}/
├── OUTPUT_FILE_1
├── OUTPUT_FILE_2
└── ...
```

## Constraints

- Output artifact keys MUST be declared in the requirement document
- Output filenames follow the pattern defined in the requirement doc
- All outputs are written to the job's output directory
- Generator workflows do NOT produce workflow package files (workflow.toml, actions.py, etc.)
