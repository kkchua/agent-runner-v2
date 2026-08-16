---
template_id: SYS-03-MM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Memory/Lessons-Learned documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Memory / Lessons Learned Document (MEM-DOC)

## Purpose

This template defines the structure for approved memory/lessons-learned
documents produced by the sdlc_80_review_v1 workflow. A memory document
(MEM-DOC) captures the knowledge, insights, and lessons learned during
the initiative for use by future initiatives and workflows.

The MEM-DOC is the ninth formal artifact in the SDLC delivery chain. It
represents the institutional memory of the initiative and feeds into the
knowledge base for continuous improvement.

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
scan_reason: "Approved memory/lessons-learned document in SDLC delivery chain"
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

The workflow MUST add `source_document` referencing the initiative doc:

```
source_document: "INIT-{YYYYMMDD}-{NN}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this memory document. Should reference the
initiative being documented.

### 2. Memory Summary

A concise summary of the knowledge captured:

- Initiative reference.
- Knowledge domains covered.
- Importance level (Critical, Important, Informational).
- Recommended retention period.

### 3. Lessons Learned

A detailed list of lessons learned during the initiative. Each lesson
MUST include:

- **Lesson ID**: Unique identifier (LL-001, LL-002, etc.).
- **Category**: Process, Technical, Communication, Tooling, etc.
- **Situation**: What happened or what was observed.
- **Impact**: What effect this had on the initiative.
- **Root Cause**: Why it happened (if known).
- **Recommendation**: What to do differently in the future.
- **Applicability**: Which future workflows or roles this applies to.

### 4. Knowledge Artifacts

Knowledge artifacts produced or discovered:

- **Patterns**: Reusable patterns or approaches discovered.
- **Code Snippets**: Useful code patterns or configurations.
- **Configuration Examples**: Environment or tool configurations.
- **Reference Links**: Links to documentation, issues, or resources.

### 5. Process Improvements

Suggestions for process improvement:

| ID | Current Process | Proposed Improvement | Benefit |
|---|---|---|---|
| PI-001 | Current approach | Proposed change | Expected benefit |

### 6. Common Pitfalls

Common pitfalls or traps encountered:

- **Pitfall**: Description of the pitfall.
- **Signs**: How to recognize it.
- **Avoidance**: How to avoid it in the future.
- **Recovery**: How to recover if encountered.

### 7. Knowledge Gaps

Identified gaps in knowledge or documentation:

- **Gap**: What is missing or unclear.
- **Impact**: How this gap affected the initiative.
- **Remediation**: How to fill the gap.
- **Priority**: High, Medium, Low.

### 8. Reusable Assets

List of reusable assets created during the initiative:

- **Asset**: Templates, scripts, configurations, etc.
- **Location**: Where the asset is stored.
- **Description**: What the asset does.
- **Dependencies**: What is needed to use it.

### 9. Recommendations for Future Initiatives

Actionable recommendations for future initiatives:

- Top 3 recommendations.
- Expected impact of each recommendation.
- Prerequisites for implementing each recommendation.

## Content Guidelines

### Honesty

Lessons learned should be honest and candid. The value of the memory
document comes from its accuracy, not from making the initiative look
successful.

### Actionability

Each lesson should include a specific recommendation that can be acted
upon. Lessons without actionable recommendations have limited value.

### Reusability

Structure knowledge so it can be easily discovered and reused by future
initiatives. Use consistent categories and tags.

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
| YYYYMMDD | Date of memory document approval |
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

- **08_VALID_template.md** (SYS-03-VL): Input document.
- **09_REV_template.md** (SYS-03-RV): Companion review document.
- **11_CLOSE_template.md** (SYS-03-CL): Companion closure document.

### Related Agent Contracts

- AGENT-memory-manager: Used by sdlc_80 to generate this memory
  document.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document along with REV-DOC and
  CLOSE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
