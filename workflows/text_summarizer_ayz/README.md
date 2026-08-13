# Text Summarizer

Transforms long text documents into concise summaries or ranked key points

**Version:** 1.0.0

## Pipeline Steps

| # | Step | Type | Detail |
|---|------|------|--------|
| 1 | parse_input | action | parse_input_document |
| 2 | analyze_structure | prompt | prompts/02_analyze_structure.txt |
| 3 | transform_content | prompt | prompts/03_transform_content.txt |
| 4 | render_output | action | render_prose_output |
| 5 | step_completion | action | step_completion |

## Implementations

| Name | Description |
|------|-------------|
| default | Default implementation (workflow.toml) |
| key_points | Produces ordered list of extracted key points with importance scores |

## Usage

```bash
ukbe-run-agent run --template-group text_summarizer_ayz
```

## File Structure

```
text_summarizer_ayz/
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
    impls/          (if alternative implementations exist)
    README.md
```
