# Builder Input Artifacts

Builder-type workflows take a **requirement document** that describes the workflow to be built.

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
   - `implementation`: MUST be `builder` (or omitted for default generator)
   - `subtype`: optional domain specialization (e.g., `jimeng`)
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

## Subtype-Specific Inputs

Subtypes may require additional inputs. For example:

### JiMeng Subtype
| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `JIMENG_WORKFLOW_FILE` | `input/JiMeng-workflows/*.md` | JiMeng/Dreamai agentic workflow markdown |
| `JIMENG_WORKFLOW_DIR` | `input/JiMeng-workflows/` | Directory containing JiMeng markdown files |

## Notes

- The requirement document is the **primary input** for all builder workflows
- Subtype-specific inputs are defined by the subtype specialization
- All inputs MUST be declared in the requirement document's frontmatter or input section
