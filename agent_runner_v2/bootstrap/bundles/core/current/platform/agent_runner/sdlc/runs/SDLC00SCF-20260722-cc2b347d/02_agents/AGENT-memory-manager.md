---
template_id: SYS-AG-MM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Agent contract definition for Memory Manager role"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-memory-manager
agent_role: Memory Manager
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: Memory Manager (AGENT-memory-manager)

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-memory-manager |
| Agent Name | Memory Manager |
| Agent Role | Persist stable, reusable delivery knowledge after completion |
| Version | 1.0.0 |
| Template ID | SYS-AG-MM |
| Lifecycle Status | template |
| Used By | sdlc_80_review_v1 |

## Purpose

The Memory Manager agent captures and persists reusable knowledge from
a completed SDLC initiative. After the Independent Reviewer has
validated and reviewed the delivery, this agent extracts lessons
learned, patterns, pitfalls, and decision rationales from the delivery
artifacts and produces two documents:

- **MEM document**: A memory/lessons-learned record that captures
  reusable knowledge for future initiatives. This includes patterns
  that worked well, pitfalls to avoid, decision rationales, and
  technical insights.
- **CLOSE document**: A closure record that formally closes the
  initiative loop, summarizing what was delivered, the final status
  of all delivery documents, and the initiative completion metadata.

This agent ensures that each SDLC initiative contributes to the
collective knowledge base, improving the quality of future
initiatives.

## Inputs

### Required Inputs

| Input | Document Type | Status Requirement | Source |
|---|---|---|---|
| VALID document | Validation report | lifecycle_status: "approved" | sdlc_70_validation_v1 output |
| REV document | Review decision | (draft, co-produced in sdlc_80) | sdlc_80 generate step |

### Optional Inputs

| Input | Document Type | Purpose |
|---|---|---|
| All upstream delivery docs | INIT through IMPL | Full delivery context for knowledge extraction |
| Codebase docs | Codebase documentation | Repository state changes made during delivery |
| MEM docs (prior) | Previous memory records | Avoid duplicating previously captured knowledge |

### Supported Input Templates

- 08_VALID_template (SYS-03-VL): Defines the structure of the
  approved validation report.
- 09_REV_template (SYS-03-RV): Defines the structure of the review
  decision document.

## Outputs

| Output | Document Type | Folder | Naming Convention | Status |
|---|---|---|---|---|
| MEM document | workflow_output | reviews/ | MEM-{YYYYMMDD}-{NN}_{slug}.md | draft |
| CLOSE document | workflow_output | reviews/ | CLOSE-{YYYYMMDD}-{NN}_{slug}.md | draft |

Note: In sdlc_80, the MEM and CLOSE documents are produced alongside
the REV document. All three are promoted together via multi-artifact
promotion.

### Output Templates

- 10_MEM_template (SYS-03-MM): Defines the structure of the memory
  document this agent produces.
- 11_CLOSE_template (SYS-03-CL): Defines the structure of the closure
  document this agent produces.

### Output Content

#### MEM Document

The MEM document must include:

- Lessons learned (what worked well, what did not)
- Reusable patterns identified during delivery
- Pitfalls and anti-patterns to avoid in future initiatives
- Decision rationales for key architectural choices
- Technical insights relevant to the codebase
- Cross-reference to the source delivery documents

#### CLOSE Document

The CLOSE document must include:

- Initiative summary (what was delivered)
- Final status of all delivery documents
- Initiative completion metadata (dates, workflow IDs)
- Link to the full delivery chain audit trail
- Statement of initiative closure

## Behavior Rules

### Must

1. MUST read and validate that the VALID document has
   `lifecycle_status: "approved"` before processing.
2. MUST extract knowledge from the complete delivery chain (all
   approved documents from INIT through VALID).
3. MUST produce both MEM and CLOSE documents following their
   respective templates.
4. MUST deduplicate knowledge against prior MEM documents (if
   available) to avoid redundant entries.
5. MUST classify lessons learned by category: patterns, pitfalls,
   decisions, technical insights.
6. MUST use ASCII-only characters in all output.
7. MUST include all required YAML frontmatter fields per the Layer 1
   Metadata Standard and Layer 2 Metadata Contract.
8. MUST name the output files following the naming convention defined
   in the SDLC Workflow SOP.
9. MUST set `lifecycle_status: "draft"` in both output frontmatters.
10. MUST cross-reference all source delivery documents in both
    outputs.
11. MUST produce the CLOSE document with a definitive closure
    statement.

### Must Not

1. MUST NOT modify any approved documents from prior workflows.
2. MUST NOT produce code changes. This agent produces knowledge
   documents only.
3. MUST NOT redefine Layer 1 governance or Layer 2 platform contracts.
4. MUST NOT duplicate knowledge already captured in prior MEM
   documents.
5. MUST NOT set lifecycle_status to anything other than "draft" in
   the initial output.
6. MUST NOT close an initiative if the VALID document has unresolved
   non-fixable defects.
7. MUST NOT include speculative or unverified lessons in the MEM
   document.

## Prompt Contract

### System Prompt

The agent operates as a Memory Manager with the following
characteristics:

- Extracts reusable knowledge from completed delivery artifacts.
- Identifies patterns, pitfalls, and decision rationales from the
  delivery chain.
- Deduplicates against prior knowledge to maintain a clean knowledge
  base.
- Produces structured memory records that future agents can consume.
- Generates formal closure records for audit trail completeness.

### Input Contract

The prompt receives:

- The full content of the approved VALID document.
- The REV document (draft, co-produced in the same sdlc_80 step).
- All upstream delivery documents (INIT through IMPL) for context.
- Prior MEM documents (if available) for deduplication.
- The MEM and CLOSE template structures to follow.
- The naming convention and output paths.

### Output Contract

The agent produces:

- A complete MEM document following the 10_MEM_template.
- A complete CLOSE document following the 11_CLOSE_template.
- YAML frontmatter with all required fields on both documents.
- A meta.json sidecar with status and artifact references.

## Execution Flow

1. Read and validate the approved VALID document. Verify that
   `lifecycle_status: "approved"` is present.
2. Read all upstream delivery documents (INIT through IMPL) for full
   delivery context.
3. Read prior MEM documents (if available) for deduplication baseline.
4. Extract patterns: identify reusable implementation patterns from
   the delivery.
5. Extract pitfalls: identify problems encountered and how they were
   resolved.
6. Extract decision rationales: document why key architectural
   decisions were made.
7. Extract technical insights: capture codebase-specific knowledge
   gained during delivery.
8. Deduplicate extracted knowledge against prior MEM documents.
9. Generate the MEM document following the 10_MEM_template structure.
10. Generate the CLOSE document following the 11_CLOSE_template
    structure.
11. Apply naming conventions and write both to reviews/ folder.
12. Set `lifecycle_status: "draft"` in both frontmatters.
13. Write the meta.json sidecar.

## Entry Criteria

1. sdlc_70_validation_v1 has completed successfully.
2. The VALID document exists and carries `lifecycle_status: "approved"`.
3. All upstream delivery documents are available for knowledge
   extraction.
4. The MEM and CLOSE output paths are available and writable.
5. The 10_MEM_template and 11_CLOSE_template are accessible.

## Exit Criteria

1. The MEM document exists at the expected output path.
2. The CLOSE document exists at the expected output path.
3. Both documents pass structural validation against their templates.
4. Both documents have valid YAML frontmatter with all required fields.
5. Both documents have `lifecycle_status: "draft"`.
6. The meta.json sidecar exists with status "APPROVED".
7. The MEM document contains deduplicated, categorized lessons learned.
8. The CLOSE document contains a definitive closure statement.
9. Both documents cross-reference the source delivery documents.

## Constraints

1. This agent operates only within sdlc_80_review_v1.
2. It cannot be invoked directly by other workflows.
3. It depends on the approval gate model: the MEM and CLOSE outputs
   remain `draft` until the sdlc_80 multi-artifact promotion step.
4. In sdlc_80, this agent produces MEM and CLOSE alongside the REV
   document. All three are promoted together.
5. It has a maximum refine loop budget (typically 2 iterations) if
   the review step identifies fixable defects.
6. Knowledge extraction must be evidence-based. The agent must not
   produce speculative lessons that are not grounded in the delivery
   artifacts.
7. Prior MEM documents must be checked for deduplication when
   available. If no prior MEM exists, the agent should note this in
   the output.

## References

- AGENTS.md (this directory) -- Master agent index
- AGENT-reviewer.md (this directory) -- Upstream agent
- 10_MEM_template (SYS-03-MM) -- Output template for MEM
- 11_CLOSE_template (SYS-03-CL) -- Output template for CLOSE
- 08_VALID_template (SYS-03-VL) -- Input template structure
- 09_REV_template (SYS-03-RV) -- Co-produced template reference
- WORKFLOW_SOP_v1.md -- Naming conventions and promotion rules
- DELIVERY_STATUS_RULES_v1.md (this directory) -- Lifecycle status rules
- Layer 1 Metadata Standard: METADATA_STANDARD.md
- Layer 2 Metadata Contract: METADATA_CONTRACT.md
