---
template_id: SYS-03-RV
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Review documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Review Document (REV-DOC)

## Purpose

This template defines the structure for approved review documents
produced by the sdlc_80_review_v1 workflow. A review document (REV-DOC)
captures the comprehensive review of the completed initiative, evaluating
the quality of all artifacts produced, the process followed, and the
outcomes achieved.

The REV-DOC is the eighth formal artifact in the SDLC delivery chain. It
represents the final quality gate before initiative closure and the
lessons learned process.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-RV
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved review document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-RV | Fixed identifier for this template |
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

A clear title that identifies this review document. Should reference the
initiative and be consistent with prior documents.

### 2. Review Summary

A concise summary of the review:

- Initiative title and objective.
- Review scope and approach.
- Overall assessment (Pass, Pass with Recommendations, Fail).
- Key findings summary.

### 3. Artifact Review

A review of each delivery artifact produced during the initiative:

| Artifact | File Path | Quality | Findings |
|---|---|---|---|
| INIT-DOC | Path to file | Satisfactory/Needs Improvement | Key observations |
| REQ-DOC | Path to file | Satisfactory/Needs Improvement | Key observations |
| PLAN-DOC | Path to file | Satisfactory/Needs Improvement | Key observations |
| BACKLOG-DOC | Path to file | Satisfactory/Needs Improvement | Key observations |
| TASK-DOC(s) | Path to file | Satisfactory/Needs Improvement | Key observations |
| IMPL-DOC(s) | Path to file | Satisfactory/Needs Improvement | Key observations |
| VALID-DOC | Path to file | Satisfactory/Needs Improvement | Key observations |

### 4. Process Review

An evaluation of the process followed:

- Adherence to the SDLC workflow sequence.
- Quality of approval gate outcomes.
- Completeness of the audit trail.
- Effectiveness of the refine loop process.
- Any process deviations or improvements needed.

### 5. Quality Assessment

An assessment of overall quality:

- **Documentation Quality**: Clarity, completeness, consistency of all
  artifacts.
- **Code Quality**: Adherence to standards, test coverage, maintainability
  (if code was produced).
- **Validation Quality**: Thoroughness of validation, evidence quality.
- **Traceability**: Ability to trace from initiative through requirements
  to implementation and validation.

### 6. Findings and Recommendations

Detailed findings from the review:

| Finding ID | Category | Severity | Description | Recommendation |
|---|---|---|---|---|
| REV-F-001 | Documentation | Major/Minor/Info | Description | Recommended action |
| REV-F-002 | Process | Major/Minor/Info | Description | Recommended action |

### 7. Compliance Check

Verification of governance compliance:

- Layer 1 metadata requirements satisfied: Yes/No/Partial.
- Layer 2 platform contract satisfied: Yes/No/Partial.
- Layer 3 SOP followed: Yes/No/Partial.
- Naming conventions followed: Yes/No.
- Storage locations correct: Yes/No.

### 8. Closure Recommendation

A recommendation for initiative closure:

- **Recommend Closure**: All criteria met, initiative complete.
- **Recommend Closure with Conditions**: Minor items to address after
  closure.
- **Do Not Recommend Closure**: Significant issues remain.

### 9. Lessons Learned Summary

A summary of lessons learned (detailed in companion MEM-DOC):

- Top lessons from this initiative.
- Process improvement suggestions.
- Knowledge gaps identified.

## Content Guidelines

### Objectivity

Reviews should be objective and evidence-based. Each finding must be
supported by specific examples or references.

### Constructiveness

Findings should be constructive, with clear recommendations for
improvement. The goal is to improve future initiatives, not to assign
blame.

### Completeness

The review should cover all artifacts and all stages of the initiative.
If certain artifacts were not produced, explain why.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
REV-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| REV | Fixed prefix |
| YYYYMMDD | Date of review approval |
| NN | Two-digit initiative sequence number |
| slug | Short hyphenated description (same as initiative) |

### Example

```
REV-20260722-001_add-user-authentication.md
```

### Storage Location

Review documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **08_VALID_template.md** (SYS-03-VL): Input document.
- **10_MEM_template.md** (SYS-03-MM): Companion memory document.
- **11_CLOSE_template.md** (SYS-03-CL): Companion closure document.

### Related Agent Contracts

- AGENT-reviewer: Used by sdlc_80 to generate this review document.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document along with MEM-DOC and
  CLOSE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
