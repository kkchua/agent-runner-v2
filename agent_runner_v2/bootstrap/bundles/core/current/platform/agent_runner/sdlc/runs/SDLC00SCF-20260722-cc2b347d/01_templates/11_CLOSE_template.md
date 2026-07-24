---
template_id: SYS-03-CL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Closure documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Closure Document (CLOSE-DOC)

## Purpose

This template defines the structure for approved initiative closure
documents produced by the sdlc_80_review_v1 workflow. A closure document
(CLOSE-DOC) formally concludes the initiative, documenting completion
status, outcomes achieved, outstanding items, final artifact inventory,
and the lessons learned handoff.

The CLOSE-DOC is the tenth and final formal artifact in the SDLC delivery
chain. It represents the authoritative record that an initiative has been
completed, reviewed, and closed.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-CL
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved closure document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-CL | Fixed identifier for this template |
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

A clear title that identifies this closure document. Should reference
the initiative being closed.

### 2. Closure Summary

A concise summary of the initiative closure:

- Initiative title and objective.
- Closure date.
- Overall status (Completed, Completed with Exceptions, Not Completed).
- Brief statement of what was accomplished.

### 3. Initiative Completion Status

The completion status of the initiative:

- **Status**: Completed / Completed with Exceptions / Not Completed.
- **Completion Date**: Date of final approval.
- **Workflow Run**: The sdlc_80 workflow run that produced this closure.
- **Duration**: Total time from draft initiative to closure.

### 4. Outcomes Achieved

A list of the outcomes defined in the INIT-DOC and whether each was
achieved:

| Outcome | Status | Evidence |
|---|---|---|
| Outcome 1 from INIT-DOC | Achieved/Partially/Not Achieved | Evidence reference |
| Outcome 2 from INIT-DOC | Achieved/Partially/Not Achieved | Evidence reference |

### 5. Success Criteria Evaluation

Evaluation of each success criterion from the INIT-DOC:

| Criterion | Met? | Evidence |
|---|---|---|
| Criterion 1 from INIT-DOC | Yes/No | How it was verified |
| Criterion 2 from INIT-DOC | Yes/No | How it was verified |

### 6. Delivery Artifact Inventory

A complete inventory of all delivery artifacts produced during the
initiative:

| Artifact Type | File Path | Status |
|---|---|---|
| Initiative | INIT-{date}-{seq}_{slug}.md | Approved |
| Requirement | REQ-{date}-{seq}_{slug}.md | Approved |
| Plan | PLAN-{date}-{seq}_{slug}.md | Approved |
| Backlog | BACKLOG-{date}-{seq}_{slug}.md | Approved |
| Task | TASK-{date}-{seq}-{tt}_{slug}.md | Approved |
| Implementation | IMPL-{date}-{seq}-{tt}_{slug}.md | Approved |
| Validation | VALID-{date}-{seq}_{slug}.md | Approved |
| Review | REV-{date}-{seq}_{slug}.md | Approved |
| Memory | MEM-{date}-{seq}_{slug}.md | Approved |
| Closure | CLOSE-{date}-{seq}_{slug}.md | Approved |

### 7. Code Changes Summary

A summary of code changes made during the initiative:

- Repositories and branches affected.
- Files created (count and types).
- Files modified (count and types).
- Files deleted (count and types).
- Total lines of code added/changed/deleted.

### 8. Outstanding Items

Any items that remain open or incomplete:

- Known issues or bugs not resolved.
- Future enhancements or follow-up work.
- Documentation gaps to be addressed.
- Technical debt to be acknowledged.

### 9. Lessons Learned Handoff

A reference to the companion memory document and a summary of the most
important lessons:

- Link to MEM-DOC.
- Top 3 lessons for future initiatives.
- Key recommendations for the next initiative.

### 10. Closing Statement

A formal closing statement that concludes the initiative:

- Acknowledgement of completion.
- Sign-off statement.
- Next steps (archiving, future work, etc.).

## Content Guidelines

### Completeness

The closure document should account for all delivery artifacts produced
during the initiative. If an artifact type was not produced (e.g., no
task decomposition was needed), explain why.

### Honesty

If outcomes were not achieved or criteria were not fully met, document
this honestly. The closure document is an audit record, not a marketing
statement.

### Traceability

Every outcome and criterion should be traceable back to the original
INIT-DOC. This enables verification that the initiative delivered what
was promised.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
CLOSE-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| CLOSE | Fixed prefix |
| YYYYMMDD | Date of closure approval |
| NN | Two-digit initiative sequence number |
| slug | Short hyphenated description (same as initiative) |

### Example

```
CLOSE-20260722-001_add-user-authentication.md
```

### Storage Location

Closure documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **02_INIT_template.md** (SYS-03-IN): The initiative being closed.
- **09_REV_template.md** (SYS-03-RV): Companion review document.
- **10_MEM_template.md** (SYS-03-MM): Companion memory document.

### Related Agent Contracts

- AGENT-memory-manager: Used by sdlc_80 to generate the closure
  document.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document along with REV-DOC and
  MEM-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
