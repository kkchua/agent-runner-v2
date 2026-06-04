# Template Registry Review — 2026-06-03

## Metadata

| Field | Value |
|---|---|
| Doc Type | 04_review |
| Template Version | v1 |
| Review ID | `REV-260603-02_rtempl_R-0000-00_template-registry` |
| Related Doc Type | template_registry.md |
| Related Doc ID | N/A (SOP artifact) |
| Title | Template Registry and All Delivery Templates Review |
| Reviewer | Template Reviewer |
| Status | Final |
| Review Date | 2026-06-03 |

## Review Objective

Validate that all 8 delivery templates (initiative, plan, task graph, task, implementation plan, review, validation, memory) and the template registry are complete, follow SOP/status rules alignment, have consistent metadata, and support the documented workflow phases and state transitions.

## Summary of Reviewed Content

Reviewed all artifacts:
- `template_registry.md` — Template index and flow definition
- `01_initiative.template.md` — Initiative template
- `02_plan.template.md` — Plan template
- `02b_task_graph.template.md` — Task graph template
- `03_task.template.md` — Task template
- `04_implementation_plan.template.md` — Implementation plan template
- `04_review.template.md` — Review template
- `05_validation.template.md` — Validation template
- `06_memory.template.md` — Memory template

Against governing documents:
- WORKFLOW_SOP_v1.md (workflow phases, agent roles, sidecar contract)
- DELIVERY_STATUS_RULES_v1.md (artifact lifecycle, allowed state transitions, naming discipline)
- project_analysis.json (project complexity, scope, delivery structure)

## Strengths

- All templates present and accessible in correct folders per SOP
- All templates have proper metadata blocks with Doc Type, Template Version fields
- All templates follow consistent `{{PLACEHOLDER}}` variable naming convention
- Templates cover all required workflow phases: Initiative, Plan, Task Graph, Task, Implementation Plan, Review, Validation, Memory
- Placeholder documentation is comprehensive and contextual (references to SOP modules, runner architecture, delivery folder structure)
- Memory template properly captures durable context and architecture notes
- Implementation Plan template includes mandatory File Plan section with [NEW]/[MODIFY] tags
- Review template includes structured Issues/Findings section with severity levels

## Issues Identified

### CRITICAL

| Issue | Severity | Location | Description |
|---|---|---|---|
| Template Registry omits validation phase | **CRITICAL** | template_registry.md | Registry lists only 7 artifacts (missing 05_validation). Flow diagram shows "Initiative → Plan → Task → Implementation → Code → Review → Memory" but omits Task Graph and Validation. Per SOP, workflow is 8 phases: Initiative → Plan → Task Graph → Task → Implementation Plan → Review → Validation → Completion. |
| Task Graph template Doc Type mismatch | **CRITICAL** | 02b_task_graph.template.md line 7 | Lists "Doc Type: 02_plan_artifact" but per SOP naming discipline (DELIVERY_STATUS_RULES_v1.md §Naming) should be "02b_task_graph". Template filename and sidecar references will be inconsistent. |
| Validation template ID format incorrect | **CRITICAL** | 05_validation.template.md line 10 | Uses "Validation ID: VALIDATION-{{YYYYMMDD}}-{{NN}}" but SOP status rules (DELIVERY_STATUS_RULES_v1.md §Naming) specifies "VAL-YYYYMMDD-NN" format. |
| Review template status values misaligned with SOP | **CRITICAL** | 04_review.template.md line 14 | Lists status as `in_progress | approved | rejected` but SOP (DELIVERY_STATUS_RULES_v1.md §Review) specifies status transitions "Draft → Final" only. Decisions (APPROVED/REJECTED/CHANGES_REQUIRED) belong in decision field, not status field. |
| Validation template status values non-standard | **CRITICAL** | 05_validation.template.md line 24 | Lists status as "VALIDATION_IN_PROGRESS / VALIDATED / FAILED / Superseded" but SOP requires standard lifecycle: "Draft → Final". Decision field should contain APPROVED/REJECTED. |

### HIGH

| Issue | Severity | Location | Description |
|---|---|---|---|
| Task template status options include non-existent states | **HIGH** | 03_task.template.md line 12 | Lists status as `pending | in_progress | in_review | approved | rejected | completed` but SOP (DELIVERY_STATUS_RULES_v1.md §Task) specifies "Pending → In Progress → Implemented → Approved". Template includes "in_review", "rejected", "completed" which are not valid task states; should have "Implemented" instead of "in_review". |
| Implementation Plan folder naming inconsistency | **HIGH** | 04_implementation_plan.template.md title, template_registry.md, DELIVERY_STATUS_RULES_v1.md | Template references "04_implementation_plans/" (plural) in some places but SOP status rules (§Naming) and folder structure definition (WORKFLOW_SOP_v1.md §Folder Structure) specify "04_implementation/" (singular). Inconsistent naming will cause path mismatches and validation failures. |
| Review template missing doc type options | **HIGH** | 04_review.template.md line 10 | Lists "Related Doc Type" options as "01_initiative / 02_plan / 02b_task_graph / 03_task / 04_implementation_plan" but per SOP workflow phases, reviews can be conducted on plan, task graph, implementation plan, AND upstream artifacts. Missing coverage of what gets reviewed. Should clarify review applies to any approved artifact in workflow. |
| Task Graph template folder consistency | **HIGH** | 02b_task_graph.template.md line 10, template_registry.md line 9 | Metadata shows "Plan ID" field but references folder "02_plans/artifacts/". Per SOP naming (§Naming), Task Graph artifact should live in "02_plans/artifacts/" ✓ but metadata linkage to Plan should be explicit. Current metadata links to Plan correctly in lines 9-10, but folder path in registry should clarify artifacts/ subdirectory. |

### MEDIUM

| Issue | Severity | Location | Description |
|---|---|---|---|
| Implementation Plan metadata uses wrong ID type | **MEDIUM** | 04_implementation_plan.template.md line 9 | Metadata lists "Plan ID: PLAN-{{YYYYMMDD}}-{{NN}}_{{SLUG}}" but this artifact is an implementation plan, should use "IMPL-{{YYYYMMDD}}-{{NN}}_{{SLUG}}" per SOP naming. Also line 10 correctly includes "Task ID" but line 9 is misleading. |
| Validation template metadata bloated | **MEDIUM** | 05_validation.template.md lines 11-27 | Includes extensive upstream references (Initiative, Plan, Task Graph, Task, Impl Plan, Review IDs and paths) but per SOP (DELIVERY_STATUS_RULES_v1.md), traceability should be captured in meta.json `upstream_refs` field, not duplicated in artifact body. Metadata block is 17 lines when could be 8-10. |
| Task Graph template metadata repeats linkage | **MEDIUM** | 02b_task_graph.template.md lines 9-11 | Includes Initiative ID and Plan ID in metadata but per SOP (§Traceability), task graph only depends on Plan; Initiative linkage is implicit via Plan. Creates redundancy in metadata. |
| Memory template ID format uses MEM- | **MEDIUM** | 06_memory.template.md line 9 | Uses "Memory ID: MEM-{{YYYYMMDD}}-{{NN}}_{{SLUG}}" but per SOP (DELIVERY_STATUS_RULES_v1.md §Naming), should be "MEMORY-{{YYYYMMDD}}-{{NN}}" to align with other artifact types (no underscores after NN in registry example). |

### LOW

| Issue | Severity | Location | Description |
|---|---|---|---|
| Template registry flow diagram incomplete | **LOW** | template_registry.md lines 18-19 | Flow shows linear path but doesn't indicate parallelization or rejection routing. Per SOP, tasks can execute in parallel and reviews/validation can reject. Flow should include: "Review [reject → back to execution], Validation [reject → back to execution]". |
| Initiative template approval block outdated format | **LOW** | 01_initiative.template.md lines 99-104 | Uses markdown table format for approval signatures, but per SOP (§Sidecar Contract), approval decisions belong in meta.json sidecars (status + decision fields), not in artifact body approval tables. Table is advisory only; execution decision is sidecar-driven. Should clarify this distinction. |

## Validation Against Acceptance Criteria

| Criterion | Result | Notes |
|---|---|---|
| All templates exist in correct folders | **PASS** | All 8 templates present in `docs/delivery/00_templates/`. |
| All templates have proper metadata blocks | **PASS** | All have Doc Type, Template Version, artifact ID templates. |
| Metadata blocks include Doc Type field | **PASS** | Consistent across all templates. |
| Metadata blocks include Template Version field | **PASS** | All set to v1. |
| Placeholder variables are consistent | **PASS** | All use `{{VARIABLE}}` format consistently. |
| Templates align with SOP workflow phases | **FAIL** | Template registry omits validation phase; task graph template Doc Type mismatch; review and validation status values don't align with SOP state machine. |
| Artifact ID formats match SOP naming discipline | **FAIL** | Validation ID uses VALIDATION- not VAL-; Implementation Plan uses PLAN- not IMPL-; Memory uses MEM- not MEMORY-. |
| Status options match SOP allowed transitions | **FAIL** | Review template status is not Draft→Final; Validation status is non-standard; Task status includes invalid states (in_review, rejected, completed). |
| Folder paths consistent with SOP | **FAIL** | Implementation plan folder referenced as both "04_implementation_plans/" (plural) and "04_implementation/" (singular). |
| Registry reflects all templates | **FAIL** | Registry omits 05_validation from table and flow diagram. |

## Suggested Improvements

Non-blocking suggestions:

1. **Enhance template registry flow diagram** to show rejection loops and parallelization: add annotations for "Review can reject → back to execution" and "Tasks can run in parallel".

2. **Add sidecar contract guidance** to each template's metadata section: brief note that status decisions belong in meta.json, not artifact body.

3. **Clarify upward linkage requirements** in metadata: each template should document which upstream artifact IDs must be referenced in its own meta.json `upstream_refs` field.

4. **Add example meta.json sidecars** in a separate section of each template to illustrate correct sidecar structure for that artifact type (optional but helpful).

5. **Include "Sidecar Path" reference** in each template metadata section to make explicit where the .meta.json sidecar should live.

## Final Decision

| Field | Value |
|---|---|
| Decision | **REJECTED** |
| Rationale | Templates have critical structural misalignments with SOP: (1) Registry omits validation phase and task graph from flow; (2) Status field values in Review/Validation/Task templates do not match SOP state machine; (3) Artifact ID formats (Validation, Implementation Plan, Memory) don't follow SOP naming discipline; (4) Folder path naming inconsistent (04_implementation vs 04_implementation_plans); (5) Task Graph doc type metadata incorrect. These are required artifacts for workflow enforcement; misalignment prevents runner from correctly validating artifact sidecars and enforcing state transitions. |
| Required Next Action | **Fix all CRITICAL and HIGH severity issues.** Specifically: (1) Update template_registry.md to include 05_validation and correct flow diagram; (2) Fix Task Graph template Doc Type to "02b_task_graph"; (3) Correct Review/Validation status options to match SOP (Draft → Final); (4) Fix Task template status options to match SOP (Pending → In Progress → Implemented → Approved); (5) Correct artifact ID formats in metadata (VAL-, IMPL-, MEMORY-); (6) Standardize folder paths to 04_implementation/ (singular). After corrections, all templates must be re-reviewed before approval. |

## References

| Reference | Link | Purpose |
|---|---|---|
| Workflow SOP | `docs/delivery/00_templates/WORKFLOW_SOP_v1.md` | Workflow phases, agent roles, state machine definition |
| Status Rules | `docs/delivery/00_templates/DELIVERY_STATUS_RULES_v1.md` | Artifact lifecycle, allowed transitions, naming discipline, authority model |
| Project Analysis | `delivery_scaffold_v1/SCAFFOLD-GEN-20260603-005/00_project_analysis/project_analysis.json` | Project complexity, scope, delivery structure |

## Notes

The templates are well-structured and comprehensive in their placeholder documentation. However, they must be corrected to align with the SOP state machine and naming discipline before they can be used for artifact generation. The runner will reject artifacts with non-conforming status values and ID formats. These are not editorial issues — they are functional requirements for workflow enforcement.

Critical issue: The template registry is the source of truth for artifact types. It must be updated to include all 8 templates in the correct order (Initiative → Plan → Task Graph → Task → Implementation Plan → Review → Validation → Memory) and the flow diagram must reflect the complete workflow including validation and rejection loops.
