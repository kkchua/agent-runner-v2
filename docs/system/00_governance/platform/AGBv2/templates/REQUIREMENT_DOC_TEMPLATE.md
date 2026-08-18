# Requirement Document Template

> Copy this template to `input/requirement.md` and fill in each section.

---

```yaml
---
codename: "your_codename_here"
title: "Your Generator Title"
version: "1.0"
---
```

**Replace with your values:**
- `codename`: Unique identifier (lowercase, underscores, no spaces)
- `title`: Human-readable name
- `version`: Version string

---

## Overview

**Purpose:** What problem does this generator solve?

**Target Users:** Who will use this generator?

**High-Level Workflow:** Briefly describe the transformation process.

**Example:**
```markdown
## Overview

The Text Summarizer condenses long documents into concise summaries while
preserving key information. It is designed for content creators, researchers, and
business analysts who need to quickly understand large volumes of text.

The generator accepts plain text or markdown documents and produces two outputs:
a condensed summary and a bullet-point list of key points.
```

---

## Input Artifacts

**Describe what content the generator accepts.**

Do NOT define artifact keys (like `INPUT_FILE`). Describe the content.

### Input 1: [Name]

- **Format:** (e.g., plain text, markdown, JSON, CSV)
- **Size:** (e.g., 1K-100K words, up to 1GB)
- **Structure:** (e.g., headings, paragraphs, lists, code blocks)
- **Encoding:** (e.g., UTF-8)
- **Content:** What kind of content does it contain?

### Input 2: [Name] (if applicable)

- **Format:**
- **Size:**
- **Structure:**
- **Content:**

**Example:**
```markdown
## Input Artifacts

### Source Document
- Format: Plain text or markdown
- Size: 1,000 to 100,000 words
- Structure: May contain headings, paragraphs, lists, code blocks
- Encoding: UTF-8
- Content: Long-form text content
```

---

## Output Artifacts

**Describe what the generator produces.**

Do NOT define artifact keys. Describe the content.

**Best practice:** Define at least 2 different outputs.

### Output 1: [Name]

- **Format:** (e.g., plain text, markdown, JSON, PDF)
- **Size/Length:** (e.g., 10-20% of input, 5-15 items)
- **Structure:** (e.g., paragraphs, bullet points, table)
- **Content:** What does it contain?

### Output 2: [Name]

- **Format:**
- **Size/Length:**
- **Structure:**
- **Content:**

**Example:**
```markdown
## Output Artifacts

### Condensed Summary
- Format: Markdown
- Length: 10-20% of original document
- Structure: Paragraphs preserving logical flow
- Content: Most important sentences extracted and condensed

### Key Points List
- Format: Bullet-point list
- Length: 5-15 key points
- Structure: One sentence per point, ordered by importance
- Content: Critical facts, conclusions, and action items
```

---

## Transformation Requirements

**Describe how input becomes output.**

Describe WHAT happens, not HOW. Do not prescribe:
- Specific algorithms
- Libraries or tools
- Implementation details

**Example:**
```markdown
## Transformation Requirements

The summarization process involves:
1. Parsing the input document into sentences
2. Scoring sentences based on importance (frequency, position, keywords)
3. Selecting top-scoring sentences until target length is reached
4. Preserving logical order and coherence
5. Extracting key points as a separate list
```

---

## Constraints (Optional)

**Hard requirements the generator must satisfy.**

Include constraints that are:
- Measurable (can be verified)
- Specific (not vague)
- Important (must be enforced)

**Example:**
```markdown
## Constraints

- Input size: Must handle documents up to 100,000 words
- Output quality: Summary must retain at least 80% of key information
- Performance: Must process 10,000 words in under 5 seconds
- Format: Output must be valid markdown
- Encoding: Must support UTF-8 input and output
```

---

## Extension Points (Optional)

**How the generator can be extended or customized.**

**Example:**
```markdown
## Extension Points

The generator should support:
- Custom scoring algorithms
- Configurable summary length
- Domain-specific stop words and keywords
- Output format variations
```

---

## Quality Checklist

Before submitting, verify:

- [ ] YAML frontmatter present with `codename`, `title`, `version`
- [ ] Codename follows rules (lowercase, underscores, unique)
- [ ] Overview clearly describes the problem and solution
- [ ] Input artifacts describe CONTENT (not artifact keys)
- [ ] Output artifacts describe CONTENT (at least 2 outputs)
- [ ] Transformation requirements describe WHAT (not HOW)
- [ ] Constraints are specific and measurable (if included)
- [ ] No implementation details prescribed
- [ ] No artifact keys defined
- [ ] Document is self-contained

---

## Next Steps

1. Save this file to `input/requirement.md` in your workspace
2. Run AGBv2:
   ```bash
   ukbe-run-agent run --template-group artifact_generator_builder
   ```
3. Collect output from `output/{job_id}/` and `workflows/{codename}/`

---

## See Also

- [03_REQUIREMENT_DOC_GUIDE.md](../03_REQUIREMENT_DOC_GUIDE.md) — Detailed authoring guide
- [README.md](../README.md) — AGBv2 quick start
