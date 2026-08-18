# Requirement Document Authoring Guide

> **Purpose:** How to write a requirement document that produces high-quality artifact generators via AGBv2  
> **Audience:** Human developers and AI agents writing requirement docs

---

## What is a Requirement Document?

A requirement document is a **single markdown file** that describes what an artifact generator should do — its domain problem, inputs, outputs, and constraints. It is the **sole input** to AGBv2.

```
input/requirement.md  →  [AGBv2]  →  workflows/{codename}/
```

**Key principle:** The requirement doc describes **WHAT** the generator does, not **HOW** AGB should implement it.

---

## Document Structure

```markdown
---
codename: "text_summarizer"
title: "Text Summarizer"
version: "1.0"
---

## Overview
What problem does this generator solve?

## Input Artifacts
What content does it accept?

## Output Artifacts
What does it produce?

## Transformation Requirements
How does input become output?

## Constraints
Hard requirements (optional).
```

---

## Section-by-Section Guide

### 1. YAML Frontmatter (Required)

Every requirement doc MUST start with YAML frontmatter:

```yaml
---
codename: "text_summarizer"
title: "Text Summarizer"
version: "1.0"
---
```

**Required fields:**

| Field | Type | Description | Rules |
|-------|------|-------------|-------|
| `codename` | string | Unique identifier | Lowercase, underscores, no spaces, unique |
| `title` | string | Human-readable name | Any readable string |
| `version` | string | Version | Any format (e.g., "1.0", "1.0.0") |

**Example codenames:**
- ✅ `text_summarizer` — good
- ✅ `code_reviewer_v2` — good
- ❌ `Text Summarizer` — spaces not allowed
- ❌ `my-generator` — hyphens not preferred (use underscores)

---

### 2. Overview Section

Describe the generator's purpose in 2-3 paragraphs:

- What problem does it solve?
- Who is the target user?
- What is the high-level workflow?

**Example:**
```markdown
## Overview

The Text Summarizer condenses long documents into concise summaries while
preserving key information. It is designed for content creators, researchers, and
business analysts who need to quickly understand large volumes of text.

The generator accepts plain text or markdown documents and produces two outputs:
a condensed summary (10-20% of original length) and a bullet-point list of key
points. The summarization algorithm extracts the most important sentences based
on frequency analysis and positional weighting.
```

---

### 3. Input Artifacts Section

Describe the **content** of inputs, NOT artifact keys or file paths.

**✅ Correct:**
```markdown
## Input Artifacts

### Source Document
- Format: Plain text or markdown
- Size: 1,000 to 100,000 words
- Structure: May contain headings, paragraphs, lists, code blocks
- Encoding: UTF-8
```

**❌ Incorrect:**
```markdown
## Input Artifacts

### INPUT_TEXT_FILE
- Path: `inputs/source.txt`
- Artifact Key: `INPUT_TEXT_FILE`
```

**Why:** The LLM decides artifact keys. You describe content.

---

### 4. Output Artifacts Section

Describe the **content** of outputs, NOT artifact keys or paths.

**✅ Correct:**
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

**❌ Incorrect:**
```markdown
## Output Artifacts

### SUMMARY_FILE
- Path: `outputs/summary.txt`
- Artifact Key: `SUMMARY_FILE`
```

**Best practice:** Describe at least 2 different outputs. Multiple outputs help the LLM understand the domain better.

---

### 5. Transformation Requirements Section

Describe the high-level transformation approach.

**✅ Correct (WHAT not HOW):**
```markdown
## Transformation Requirements

The summarization process involves:
1. Parsing the input document into sentences
2. Scoring sentences based on importance (frequency, position, keywords)
3. Selecting top-scoring sentences until target length is reached
4. Preserving logical order and coherence
5. Extracting key points as a separate list
```

**❌ Incorrect (prescribing implementation):**
```markdown
## Transformation Requirements

Use TF-IDF algorithm with the following parameters:
- window_size = 3
- decay_factor = 0.8
- min_score_threshold = 0.5

Implementation: Use scikit-learn TfidfVectorizer
```

**Why:** Let the LLM decide the best approach. Describe WHAT needs to happen.

---

### 6. Constraints Section (Optional)

List any hard constraints the generator must satisfy:

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

## Common Pitfalls

### Pitfall 1: Defining Artifact Keys

**Bad:**
```markdown
Input: INPUT_TEXT_FILE — path to input text
```

**Good:**
```markdown
Input: Source text document (plain text or markdown, 1K-100K words)
```

### Pitfall 2: Prescribing Implementation

**Bad:**
```markdown
Use HTML → PDF conversion using wkhtmltopdf
```

**Good:**
```markdown
Output must be a PDF document
```

### Pitfall 3: Missing Codename

**Bad:** No `codename` field in frontmatter

**Good:**
```yaml
---
codename: "text_summarizer"
---
```

### Pitfall 4: Vague Output Descriptions

**Bad:**
```markdown
Output: A file
```

**Good:**
```markdown
Output: Condensed summary (10-20% of original length) in markdown format
```

### Pitfall 5: Single Output Artifact

**Bad:** Only one output described

**Good:** At least 2 different outputs described

---

## Quality Checklist

Before submitting to AGBv2, verify:

- [ ] YAML frontmatter present with `codename`, `title`, `version`
- [ ] Codename follows rules (lowercase, underscores, unique)
- [ ] Overview section clearly describes the problem and solution
- [ ] Input artifacts describe CONTENT, not artifact keys or paths
- [ ] Output artifacts describe CONTENT, with at least 2 different outputs
- [ ] Transformation requirements describe WHAT, not HOW
- [ ] Constraints (if present) are specific and measurable
- [ ] No implementation details prescribed (no "use X library")
- [ ] No artifact keys defined (no `INPUT_TEXT_FILE` or `SUMMARY_FILE`)
- [ ] Document is self-contained

---

## Next Steps

After writing the requirement doc:

1. **Save it:** `input/requirement.md` in your workspace
2. **Run AGBv2:**
   ```bash
   ukbe-run-agent run --template-group artifact_generator_builder
   ```
3. **Collect output:**
   - `output/{job_id}/` — All intermediate artifacts
   - `workflows/{codename}/` — Final workflow package

---

## See Also

- [templates/REQUIREMENT_DOC_TEMPLATE.md](./templates/REQUIREMENT_DOC_TEMPLATE.md) — Blank template
- [README.md](./README.md) — AGBv2 quick start
- [BCS_v2.0.md](./BCS_v2.0.md) — Base Composition Standard
