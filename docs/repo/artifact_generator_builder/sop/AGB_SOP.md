# AGB Standard Operating Procedure

> **Purpose:** Step-by-step guide for using the Artifact Generator Builder (AGB)
> to create artifact generators from requirement documents.

---

## 1. Purpose

AGB builds artifact generators that transform input content into output artifacts
following a consistent pattern: input → composition spec → runtime implementation → output.

**When to use AGB:**
- You need a new workflow that transforms content
- You have a clear understanding of inputs and outputs
- You want a standardized, reusable generator

---

## 2. Prerequisites

Before running AGB, ensure:

- [ ] AGB workflow is installed: `ukbe-run-agent init` (if not already done)
- [ ] Requirement doc is written (see Section 3)
- [ ] Daemon is running (for daemon mode) or use manual mode

---

## 3. Writing the Requirement Doc

### 3.1 Use the Template

Copy the template from:
```
docs/repo/artifact_generator_builder/templates/REQUIREMENT_DOC_TEMPLATE.md
```

### 3.2 Follow the Authoring Guide

Read the authoring guide for detailed instructions:
```
docs/repo/artifact_generator_builder/REQUIREMENT_DOC_AUTHORING_GUIDE.md
```

### 3.3 Key Requirements

Every requirement doc MUST have:

1. **YAML frontmatter** with `codename`, `title`, `version`
2. **Overview** — what problem does the generator solve
3. **Input artifacts** — describe CONTENT, not artifact keys
4. **Output artifacts** — describe CONTENT, at least 2 different outputs
5. **Codename** — lowercase letters, numbers, underscores only (e.g., `text_summarizer`)

### 3.4 Save the Requirement Doc

Save to:
```
workflows/artifact_generator_builder/Specs/{codename}.md
```

Example:
```
workflows/artifact_generator_builder/Specs/text_summarizer.md
```

---

## 4. Submitting the Job

### 4.1 Via Operator Console (Preferred)

1. Open operator console
2. Select workflow: `artifact_generator_builder`
3. Upload or select requirement doc
4. Submit job

### 4.2 Via CLI

```bash
ukbe-run-agent submit \
  --workflow artifact_generator_builder \
  --artifact REQUIREMENT_DOC={filename}.md
```

Example:
```bash
ukbe-run-agent submit \
  --workflow artifact_generator_builder \
  --artifact REQUIREMENT_DOC=text_summarizer.md
```

---

## 5. Monitoring the Job

AGB has 7 phases:

1. **Analyze Requirement** — understand input/output specs
2. **Design Composition Spec** — define transformation rules
3. **Design Runtime Implementation** — design default executor
4. **Define Artifacts** — specify artifact keys and paths
5. **Design Steps** — define workflow steps and routing
6. **Generate Package** — produce workflow files + composition standard
7. **Promote Package** — package deliverables to `workflows/{codename}/`

**Monitor via:**
- Operator console (real-time updates)
- CLI: `ukbe-run-agent status --job {job_id}`

**Watch for:**
- Rejections (review/gatekeep steps) — normal, will auto-retry
- Interventions — requires human action (check error message)

---

## 6. Verifying the Output

After AGB completes, verify the output:

### 6.1 Check Directory Structure

```bash
ls workflows/{codename}/
```

Expected structure:
```
workflows/{codename}/
├── workflow.toml
├── context_extensions.py
├── actions.py
├── README.md
├── standards/
│   └── COMPOSITION_STANDARD.md
└── impls/
    └── default.impl.md
```

### 6.2 Verify Deliverables

**1. Workflow Package:**
- `workflow.toml` — valid TOML, correct codename
- `context_extensions.py` — valid Python, correct class name
- `actions.py` — valid Python (if present)
- `prompts/` — one .txt file per prompt-driven step
- `README.md` — accurate documentation

**2. Composition Standard:**
- `standards/COMPOSITION_STANDARD.md` — self-contained, uses codename

**3. Default Runtime Impl:**
- `impls/default.impl.md` — self-contained, covers all transformation stages

### 6.3 Test the Generated Workflow

```bash
ukbe-run-agent run --template-group {codename}
```

Verify the workflow executes correctly with test inputs.

---

## 7. Troubleshooting

### 7.1 Common Failures

**Missing codename:**
- Error: "Codename not found in requirement doc"
- Fix: Add `codename: "..."` to YAML frontmatter

**Vague requirement doc:**
- Error: Review/gatekeep steps reject repeatedly
- Fix: Add more detail to input/output descriptions, be specific about content

**Builder identity leakage:**
- Error: Generated files reference `artifact_generator_builder` instead of codename
- Fix: This is a bug in AGB — report it

**File not found:**
- Error: "REQUIREMENT_DOC artifact not found"
- Fix: Ensure requirement doc is in `workflows/artifact_generator_builder/Specs/`

### 7.2 Retrying Failed Jobs

**Via operator console:**
- Select failed job
- Click "Retry" or "Resume" (depending on failure type)

**Via CLI:**
```bash
ukbe-run-agent retry --job {job_id}
```

### 7.3 Getting Help

- Check AGB design doc: `docs/repo/artifact_generator_builder/AGB_V2_DESIGN.md`
- Check base standard: `docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md`
- Review job logs in: `docs/repo/artifact_generator_builder/runs/{job_id}/`

---

## 8. References

- [AGB Design Document](AGB_V2_DESIGN.md)
- [Requirement Doc Authoring Guide](REQUIREMENT_DOC_AUTHORING_GUIDE.md)
- [Requirement Doc Template](templates/REQUIREMENT_DOC_TEMPLATE.md)
- [Base Composition Standard](../../../system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md)
- [AGB Workflow](../../../workflows/artifact_generator_builder/)
