# Generator Input Artifacts

Generator-type workflows take **source content** and produce **variable output artifacts**.

## Standard Input

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `REQUIREMENT_DOC` | `input/*.md` | Requirement document describing the target workflow |

## Requirement Document Structure

The requirement document MUST contain:

1. **Frontmatter** (YAML)
   - `codename`: workflow name (lowercase, underscores)
   - `label`: human-readable display name
   - `version`: semantic version
   - `job_prefix`: 2-10 uppercase characters for job ID generation
   - `implementation`: `generator` (or omitted — generator is the default)
   - `description`: one-line description

2. **Purpose Section**
   - What the target workflow does
   - What it produces

3. **Input Section**
   - What the target workflow takes as input
   - Input artifact keys and filename patterns

4. **Output Section**
   - What the target workflow produces
   - Output artifact keys and filename patterns

5. **Transformation Requirements**
   - How inputs are transformed to outputs
   - Domain-specific rules

6. **Constraints**
   - Hard rules the workflow must follow

## Common Generator Patterns

### Document Generators
- Input: source documents (.txt, .md, .pdf, .docx)
- Output: transformed documents (summaries, reports, analyses)

### Media Generators
- Input: text prompts, configuration parameters
- Output: images, videos, audio files

### Data Generators
- Input: raw data files (.csv, .json)
- Output: processed data, visualizations, reports

## Notes

- Generator is the **default implementation** — if `implementation:` is omitted, generator is assumed
- Output artifacts are **variable** — defined by the requirement doc, not fixed
- The standard AGB pipeline handles all generator workflows uniformly
