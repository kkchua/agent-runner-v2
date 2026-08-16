# AGB Requirement Doc Authoring Guide

> **Purpose:** How to write a requirement document that produces high-quality
> artifact generators via `artifact_generator_builder` (AGB).
>
> **Audience:** Human developers and AI agents (e.g., `/requirement_doc_builder` skill).
>
> **Companion documents:**
> - [templates/REQUIREMENT_DOC_TEMPLATE.md](templates/REQUIREMENT_DOC_TEMPLATE.md) — the blank template
> - [BASE_COMPOSITION_STANDARD_v1.0.md](../../../system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md) — the base standard (Section 10)
> - [AGB_V2_DESIGN.md](AGB_V2_DESIGN.md) — AGB design document

---

## Table of Contents

- [1: What is a Requirement Doc](#1-what-is-a-requirement-doc)
- [2: Before You Start](#2-before-you-start)
- [3: Section-by-Section Authoring](#3-section-by-section-authoring)
- [4: Worked Examples](#4-worked-examples)
- [5: Common Pitfalls](#5-common-pitfalls)
- [6: Quality Checklist](#6-quality-checklist)

---

## 1: What is a Requirement Doc

A requirement doc is a **single markdown document** that describes what an
artifact generator should do — its domain problem, inputs, outputs, and constraints.
It is the **sole input** to `artifact_generator_builder`, which reads the doc and
generates a complete workflow package plus three deliverables:

```
requirement.md  -->  artifact_generator_builder  -->  workflow package
                                                       ├── workflow.toml
                                                       ├── context_extensions.py
                                                       ├── actions.py
                                                       ├── prompts/*.txt
                                                       └── README.md
                                                   -->  master spec
                                                   -->  composition standard
                                                   -->  default runtime impl
```

The requirement doc is the **single source of truth** for domain requirements.
If the doc does not mention something, the builder will not generate it. If the
doc is vague, the builder will guess — and may guess wrong.

**Key principle:** The requirement doc describes **WHAT** the generator does,
not **HOW** the builder should implement it. The builder automatically infers:
- Artifact key names
- Implementation approach
- Transformation algorithms
- Step sequence

---

## 2: Before You Start

### 2.1 Understand the Domain

Before writing, answer these questions:
- What problem does this generator solve?
- What are the inputs? (format, structure, content type)
- What are the outputs? (format, structure, content type)
- What transformations occur between input and output?
- Are there any constraints or quality requirements?

### 2.2 Choose a Codename

The codename is a **short, unique identifier** for the generator. It will be used
for:
- File naming: `{codename}_MASTER_SPEC.md`, `{codename}_COMPOSITION_STANDARD.md`
- Workflow identity: `workflows/{codename}/`
- All generated artifacts

**Codename rules:**
- Lowercase letters, numbers, underscores only
- No spaces or special characters
- Should be descriptive but concise (e.g., `text_summarizer`, `code_reviewer`, `data_transformer`)
- Must be unique across all generators

### 2.3 Review the Base Standard

Read [BASE_COMPOSITION_STANDARD_v1.0.md Section 10](../../../system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md)
to understand what AGB will produce. This helps you write a requirement doc that
aligns with the expected output structure.

---

## 3: Section-by-Section Authoring

### 3.1 YAML Frontmatter (Required)

Every requirement doc MUST start with YAML frontmatter:

```yaml
---
codename: "text_summarizer"
title: "Simple Text Summarizer"
version: "1.0"
---
```

**Required fields:**
- `codename` — Unique identifier (see rules above)
- `title` — Human-readable name
- `version` — Version string (e.g., "1.0", "2.0")

**Optional fields:**
- `author` — Author name or team
- `date` — Creation date
- `description` — Brief description (one sentence)

### 3.2 Overview Section

Describe the generator's purpose in 2-3 paragraphs:
- What problem does it solve?
- Who is the target user?
- What is the high-level workflow?

**Example:**
```markdown
## Overview

The Simple Text Summarizer condenses long documents into concise summaries while
preserving key information. It is designed for content creators, researchers, and
business analysts who need to quickly understand large volumes of text.

The generator accepts plain text or markdown documents and produces two outputs:
a condensed summary (10-20% of original length) and a bullet-point list of key
points. The summarization algorithm extracts the most important sentences based
on frequency analysis and positional weighting.
```

### 3.3 Input Artifacts Section

Describe the **content** of inputs, NOT artifact keys or file paths. The LLM will
decide the artifact keys.

**Correct:**
```markdown
## Input Artifacts

### Source Document
- Format: Plain text or markdown
- Size: 1,000 to 100,000 words
- Structure: May contain headings, paragraphs, lists, code blocks
- Encoding: UTF-8
```

**Incorrect:**
```markdown
## Input Artifacts

### INPUT_TEXT_FILE
- Path: `inputs/source.txt`
- Artifact Key: `INPUT_TEXT_FILE`
```

**Why:** The requirement doc describes WHAT the input contains, not HOW it's
tracked. The LLM decides artifact keys based on the domain.

### 3.4 Output Artifacts Section

Describe the **content** of outputs, NOT artifact keys or file paths. Describe
at least 2 different output artifacts to give the generator clear deliverables.

**Correct:**
```markdown
## Output Artifacts

### Condensed Summary
- Format: Plain text or markdown
- Length: 10-20% of original document
- Structure: Paragraphs preserving logical flow
- Content: Most important sentences extracted and condensed

### Key Points List
- Format: Bullet-point list
- Length: 5-15 key points
- Structure: One sentence per point, ordered by importance
- Content: Critical facts, conclusions, and action items
```

**Incorrect:**
```markdown
## Output Artifacts

### SUMMARY_FILE
- Path: `outputs/summary.txt`
- Artifact Key: `SUMMARY_FILE`

### KEY_POINTS_FILE
- Path: `outputs/key_points.md`
- Artifact Key: `KEY_POINTS_FILE`
```

### 3.5 Transformation Logic Section (Optional)

Describe the high-level transformation approach. Do NOT prescribe specific
algorithms or implementation details — let the LLM decide the best approach.

**Correct:**
```markdown
## Transformation Logic

The summarization process involves:
1. Parsing the input document into sentences
2. Scoring sentences based on importance (frequency, position, keywords)
3. Selecting top-scoring sentences until target length is reached
4. Preserving logical order and coherence
5. Extracting key points as a separate list
```

**Incorrect:**
```markdown
## Transformation Logic

Use TF-IDF algorithm with the following parameters:
- window_size = 3
- decay_factor = 0.8
- min_score_threshold = 0.5

Implementation: HTML → PDF conversion using wkhtmltopdf
```

**Why:** Do not prescribe implementation details. The LLM may find a better
approach. Only describe WHAT needs to happen, not HOW.

### 3.6 Constraints Section (Optional)

List any hard constraints the generator must satisfy:
- Performance requirements (e.g., "must process 10,000 words in < 5 seconds")
- Quality requirements (e.g., "summary must retain at least 80% of key information")
- Format requirements (e.g., "output must be valid markdown")
- Compatibility requirements (e.g., "must work with Python 3.12+")

**Example:**
```markdown
## Constraints

- Input size: Must handle documents up to 100,000 words
- Output quality: Summary must retain at least 80% of key information (measured by keyword overlap)
- Performance: Must process 10,000 words in under 5 seconds on modern hardware
- Format: Output must be valid markdown that renders correctly in GitHub
- Encoding: Must support UTF-8 input and output
```

### 3.7 Extension Points Section (Optional)

Describe how the generator can be extended or customized. This helps the LLM
design a flexible architecture.

**Example:**
```markdown
## Extension Points

The generator should support:
- Custom scoring algorithms (replace default frequency-based scoring)
- Configurable summary length (percentage or absolute word count)
- Domain-specific stop words and keywords
- Output format variations (plain text, markdown, HTML)
```

---

## 4: Worked Examples

### 4.1 Example: Text Summarizer

See [Specs/simple_text_summarizer.md](../../../workflows/artifact_generator_builder/Specs/simple_text_summarizer.md)
for a complete example of a requirement doc for a text summarization generator.

### 4.2 Example: Code Reviewer

A requirement doc for a code review generator might describe:
- **Inputs:** Source code files (multiple languages), coding standards document
- **Outputs:** Review report (issues found), suggested fixes (patch format)
- **Transformation:** Parse code → analyze against standards → generate report
- **Constraints:** Must support Python, JavaScript, TypeScript; must not modify original code

### 4.3 Example: Data Transformer

A requirement doc for a data transformation generator might describe:
- **Inputs:** CSV or JSON data files, transformation rules document
- **Outputs:** Transformed data files, transformation log
- **Transformation:** Parse input → apply rules → validate output → write result
- **Constraints:** Must handle files up to 1GB; must preserve data types

---

## 5: Common Pitfalls

### 5.1 Prescribing Implementation Details

**Bad:** "Use HTML → PDF conversion using wkhtmltopdf"
**Good:** "Output must be a PDF document"

**Why:** The LLM may find a better approach. Don't limit it.

### 5.2 Defining Artifact Keys

**Bad:** "INPUT_TEXT_FILE: path to input text"
**Good:** "Source text document (plain text or markdown)"

**Why:** Artifact keys are the LLM's scope. The requirement doc describes content.

### 5.3 Missing Codename

**Bad:** No `codename` field in frontmatter
**Good:** `codename: "text_summarizer"`

**Why:** The codename is required for identity locking and file naming.

### 5.4 Vague Output Descriptions

**Bad:** "Output file"
**Good:** "Condensed summary (10-20% of original length) in markdown format"

**Why:** Vague descriptions lead to vague outputs. Be specific about content.

### 5.5 Single Output Artifact

**Bad:** Only one output described
**Good:** At least 2 different output artifacts

**Why:** Multiple outputs give the generator clear deliverables and help the LLM
understand the domain better.

---

## 6: Quality Checklist

Before submitting the requirement doc to AGB, verify:

- [ ] YAML frontmatter present with `codename`, `title`, `version`
- [ ] Codename follows rules (lowercase, underscores, unique)
- [ ] Overview section clearly describes the problem and solution
- [ ] Input artifacts describe CONTENT, not artifact keys or paths
- [ ] Output artifacts describe CONTENT, with at least 2 different outputs
- [ ] Transformation logic (if present) describes WHAT, not HOW
- [ ] Constraints (if present) are specific and measurable
- [ ] No implementation details prescribed (no "use X library" or "HTML → PDF")
- [ ] No artifact keys defined (no "INPUT_TEXT_FILE" or "SUMMARY_FILE")
- [ ] Document is self-contained (no external references that LLM can't access)

---

## 7: Next Steps

After writing the requirement doc:

1. Save it to `workflows/artifact_generator_builder/Specs/{codename}.md`
2. Submit it to AGB via operator console or CLI
3. AGB will produce 4 deliverables:
   - Workflow package (workflow.toml, context_extensions.py, actions.py, prompts/, README.md)
   - Master spec (`{codename}_MASTER_SPEC.md`)
   - Composition standard (`{codename}_COMPOSITION_STANDARD.md`)
   - Default runtime impl (`default.impl.md`)
4. AGB will promote the package to `workflows/{codename}/`

---

## References

- [AGB Design Document](AGB_V2_DESIGN.md)
- [Base Composition Standard Section 10](../../../system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md)
- [Requirement Doc Template](templates/REQUIREMENT_DOC_TEMPLATE.md)
- [AGB Workflow](../../../workflows/artifact_generator_builder/)
