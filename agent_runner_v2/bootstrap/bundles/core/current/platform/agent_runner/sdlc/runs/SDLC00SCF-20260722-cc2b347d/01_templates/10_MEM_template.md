---
template_id: SYS-03-MM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Memory documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Memory Document (MEM-DOC)

## Purpose

This template defines the structure for approved initiative memory
documents produced by the sdlc_80_review_v1 workflow. A memory document
(MEM-DOC) captures lessons learned, reusable patterns, pitfalls and
anti-patterns, decision rationales, and technical insights from a
completed SDLC initiative.

The MEM-DOC is the ninth formal artifact in the SDLC delivery chain. It
serves as the institutional memory for the platform, enabling future
initiatives to build on prior experience rather than rediscovering
solutions or repeating mistakes.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-MM
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved memory document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-MM | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_80 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_80 workflow |
| scan_policy | include | Permanent delivery document |
| scan_reason | Auto-assigned | Describe purpose for scanning |
| managed_by | workflow-generated | Workflow-generated document |
| layer | layer3 | SDLC delivery layer |
| platform | agent-runner-v2 | Platform identifier |
| lifecycle_status | draft/approved | "draft" during generation, "approved" after gate |

### Additional Field: effective_version

The workflow MUST add `effective_version` when promoting to `approved`:

```
effective_version: "<workflow-run-id>"
```

### Additional Field: source_document

The workflow MUST add `source_document` referencing the validation doc:

```
source_document: "VALID-{YYYYMMDD}-{NN}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this memory document. Should reference the
initiative from which lessons were drawn and be consistent with prior
documents in the chain.

### 2. Memory Summary

A concise summary of the initiative memory:

- Initiative title and objective.
- Initiative reference (INIT-DOC filename).
- Workflow run that produced this memory document.
- Total count of lessons captured in this document.
- Total count of lessons added to platform memory (after deduplication).
- Brief statement of the memory document purpose.

### 3. Lessons Learned

Lessons learned from the initiative, organized by category. Each lesson
MUST include:

- Lesson ID (sequential, e.g., LL-001).
- Category (Process, Technical, Documentation, Coordination, Other).
- Description: What happened and why it matters.
- Evidence: Reference to artifact(s) or event(s) that support this
  lesson.
- Impact: High / Medium / Low.

| Lesson ID | Category | Description | Evidence | Impact |
|---|---|---|---|---|
| LL-001 | Process | What worked well and why | Reference | High/Med/Low |
| LL-002 | Technical | What worked well and why | Reference | High/Med/Low |

### 4. Reusable Patterns

Patterns discovered or validated during the initiative that should be
reused in future work. Each pattern MUST include:

- Pattern ID (sequential, e.g., RP-001).
- Pattern Name: A short, descriptive name.
- Context: When this pattern is applicable.
- Solution: What the pattern prescribes.
- Evidence: Where this pattern was successfully applied.
- Applicability: Broad / Narrow / Situational.

| Pattern ID | Pattern Name | Context | Solution | Applicability |
|---|---|---|---|---|
| RP-001 | Name | When to use | What to do | Broad/Narrow/Situational |

### 5. Pitfalls and Anti-Patterns

Approaches that should be avoided in future initiatives. Each pitfall
MUST include:

- Pitfall ID (sequential, e.g., PA-001).
- Pitfall Name: A short, descriptive name.
- Description: What went wrong and why.
- Root Cause: Underlying reason the pitfall occurred.
- Avoidance Strategy: What to do instead.
- Severity: Critical / Major / Minor.

| Pitfall ID | Pitfall Name | Root Cause | Avoidance Strategy | Severity |
|---|---|---|---|---|
| PA-001 | Name | Why it happened | What to do instead | Critical/Major/Minor |

### 6. Decision Rationales

Key decisions made during the initiative and their rationale. Each
decision entry MUST include:

- Decision ID (sequential, e.g., DR-001).
- Decision: What was decided.
- Alternatives Considered: Other options evaluated.
- Rationale: Why this option was chosen.
- Trade-offs: What was gained and what was sacrificed.
- Outcome: Whether the decision proved correct in hindsight.

| Decision ID | Decision | Alternatives | Rationale | Outcome |
|---|---|---|---|---|
| DR-001 | What was decided | Options considered | Why chosen | Correct/Partial/Incorrect |

### 7. Technical Insights

Codebase-specific or technology-specific knowledge gained during the
initiative. Each insight MUST include:

- Insight ID (sequential, e.g., TI-001).
- Area: Codebase module, library, framework, or infrastructure.
- Description: The technical knowledge gained.
- Applicability: Which future initiatives this applies to.
- Reference: Artifact(s) or code location(s) that informed this
  insight.

| Insight ID | Area | Description | Applicability | Reference |
|---|---|---|---|---|
| TI-001 | Module/tech | Knowledge gained | Where it applies | Reference |

### 8. Related Initiatives

Links to related past or future initiatives that may benefit from or
build upon this memory:

| Related Initiative | Relationship | Relevance |
|---|---|---|
| INIT-{date}-{seq}_{slug} | Predecessor/Successor/Related | How it relates |

## Content Guidelines

### Evidence-Based Lessons

Every lesson, pattern, pitfall, decision rationale, and insight MUST be
grounded in specific evidence from the initiative. Unsupported
assertions should not be recorded as memory entries. Reference the
specific artifact, code change, or event that supports each entry.

### Deduplication Against Prior Memories

Before adding entries, the workflow MUST check existing MEM-DOC
documents in the platform memory store. Entries that duplicate existing
platform knowledge should be skipped or merged. The Memory Summary
section MUST report how many entries were added after deduplication.

### Categorization

Lessons MUST be categorized by type (Process, Technical, Documentation,
Coordination, Other). Correct categorization enables efficient retrieval
when future initiatives search for relevant lessons.

### Actionability

Reusable patterns and avoidance strategies MUST be actionable. Vague
statements like "be more careful" or "test more thoroughly" are not
useful memories. State specific actions that future initiatives can
follow.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
MEM-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| MEM | Fixed prefix |
| YYYYMMDD | Date of memory approval |
| NN | Two-digit initiative sequence number |
| slug | Short hyphenated description (same as initiative) |

### Example

```
MEM-20260722-001_add-user-authentication.md
```

### Storage Location

Memory documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **09_REV_template.md** (SYS-03-RV): Companion review document. The
  REV-DOC identifies lessons that this MEM-DOC formalizes.
- **11_CLOSE_template.md** (SYS-03-CL): Companion closure document. The
  CLOSE-DOC references this MEM-DOC in its lessons learned handoff.

### Related Agent Contracts

- AGENT-memory-manager: Used by sdlc_80 to generate the memory document
  from the review findings and initiative artifacts.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document along with REV-DOC and
  CLOSE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
