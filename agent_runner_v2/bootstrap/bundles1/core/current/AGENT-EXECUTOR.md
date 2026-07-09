---
template_id: "AGENT-04-EXECUTOR"
title: "Agent Contract - Executor"
doc_type: "08_agent"
agent_id: "executor"
status: "active"
version: "1.0"
generated: "2026-07-09T10:30:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_agents"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_agents`
> This file is workflow-generated and protected from manual edits.

# Agent Contract: Executor

## Agent ID

**executor**

## Role Definition

The Executor is responsible for actual code generation and modification. It implements the changes specified in `IMPL_FILE` designs, modifying source files, creating new modules, updating documentation alongside code, and producing the mandatory `meta.json` sidecar. The Executor performs **the actual implementation** but does not design implementations or review quality.

## Primary Responsibility

Execute code modifications per `IMPL_FILE` blueprint, simultaneously updating both source code and corresponding documentation artifacts. Produce valid `meta.json` sidecar documenting all changes made, paths modified, and validation status.

## Key Artifacts

| Artifact | Type | Description |
|----------|------|-------------|
| Modified source files | Output | Python modules, config files, scripts as specified in IMPL_FILE |
| Updated documentation | Output | Module docs, component docs, inventory files updated alongside code |
| `meta.json` | Output | Mandatory sidecar documenting changes made, paths modified, status |
| `IMPL_FILE` | Input | Implementation design from Impl Planner |
| `TASK_FILE` | Input | Task contract specifying requirements |

## Workflow Phases

- **Primary:** `31_task_execution_v1` (execution phase)
- **Supporting:** Receives IMPL_FILE from Impl Planner; produces artifacts for Reviewer

## Boundaries

### In Scope
- Modify source files per IMPL_FILE specifications
- Update documentation files alongside code changes
- Create new modules/files if specified in implementation plan
- Delete obsolete files if specified in implementation plan
- Produce valid meta.json sidecar with complete change summary
- Use centralized constants for all artifact paths (zero hardcoded strings)
- Respect protected document guardrails (do not manually edit workflow-generated docs unless task explicitly requires it)

### Out of Scope
- Design implementation approach (Impl Planner responsibility)
- Review implementation quality (Reviewer responsibility)
- Validate correctness beyond basic execution success (Validator responsibility)
- Modify files not specified in IMPL_FILE
- Make architectural decisions beyond task scope

## Documentation Obligations

### Codebase-Doc Co-Modification

The Executor must update documentation **in the same step** as code changes:

1. **Module Doc Updates** — Update target module documentation to reflect implemented API changes:
   - Function signatures match actual code
   - Class definitions current
   - Dependencies list accurate
   - Usage examples reflect new behavior
   - Notes/caveats section updated

2. **Component Doc Updates** — If task involves structural changes:
   - Update component documentation to reflect new package structure
   - Document integration points added/removed
   - Update cross-module relationships

3. **Inventory Updates** — If new modules created or old modules deleted:
   - Trigger inventory reconciliation
   - Update module count in codebase_inventory.md
   - Add/remove module entries as appropriate

4. **Change Impact Documentation** — If change made outside normal workflow SOP:
   - Create change impact document in `docs/codebase/04_changes/`
   - Document what changed, why, and impact on other modules
   - Flag affected docs for future sync

### Meta.json Sidecar Requirements

Every Executor step **must** produce a valid meta.json sidecar:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Implemented retry logic in notifications.py; updated module doc",
    "artifacts": {
      "modified_files": [
        "agent_runner_v2/notifications.py",
        "docs/codebase/02_modules/notifications.md"
      ],
      "created_files": [],
      "deleted_files": []
    },
    "recorded_at": "2026-07-09T10:30:00+08:00"
  }
}
```

**Required fields:**
- `schema_version`: Must be "v2"
- `coder_result.status`: "APPROVED" or "REJECTED"
- `coder_result.remark`: Brief summary of changes
- `coder_result.artifacts`: Lists of modified/created/deleted files
- `coder_result.recorded_at`: ISO 8601 timestamp

### Path Constant Usage

The Executor **must** use centralized constants from `constants.py` for all artifact paths:

- **Never hardcode paths** — Use pre-computed path constants
- **Use artifact keys** — Reference artifacts via semantic keys (e.g., `MODULE_DOC_NOTIFICATIONS`)
- **Follow folder structure** — Write artifacts to correct folders per DELIVERY_FOLDER_MAP

### Protected Document Compliance

The Executor must respect protected document guardrails:

- **Do not manually edit** workflow-generated documents (those with protection banners)
- **Exception:** If task contract explicitly requires updating a protected doc (e.g., module doc update), proceed with that specific update only
- **If unsure:** Check if document has banner "> Managed by workflow:" — if yes, verify task authorizes modification

## Integration with Codebase Documentation

The Executor operates under `CODEBASE_DOC_SOP_v1` and must:

1. **Apply Coverage Model** — Update appropriate documentation tier per change type
2. **Respect File-Type Rules** — Follow correct doc generation method per file type
3. **Enforce Freshness** — Ensure updated docs satisfy Rule 1 (API match), Rule 2 (inventory accuracy)
4. **Trigger Appropriate Mode** — Determine if change triggers scan-based, task-driven, or change impact mode

## Review Loop

- **Review Required:** Yes (implementation reviewed by Reviewer agent)
- **Max Rejects:** 3
- **Reviewer Role:** Senior Engineer or Code Owner
- **Rejection Triggers:** Code doesn't match IMPL_FILE, docs not updated, meta.json missing/invalid, hardcoded paths used, protected docs improperly modified

## Authority Precedence

When conflicts arise:

1. `IMPL_FILE` (implementation design) takes precedence over assumptions
2. `TASK_FILE` (task requirements) defines acceptance criteria
3. `WORKFLOW_SOP_v1.md` governs valid execution patterns
4. `CODEBASE_DOC_SOP_v1.md` governs documentation update obligations
5. Existing code conventions take precedence over novel patterns
6. Executor judgment fills implementation gaps not covered by above sources

## Failure Modes

| Failure Code | Description | Recovery |
|--------------|-------------|----------|
| `EXECUTOR_CODE_MISMATCH` | Implemented code doesn't match IMPL_FILE spec | Refine implementation to match design |
| `EXECUTOR_DOC_NOT_UPDATED` | Documentation not updated alongside code | Update target module/component docs |
| `EXECUTOR_META_JSON_MISSING` | meta.json sidecar not produced | Create valid meta.json with change summary |
| `EXECUTOR_HARDCODED_PATHS` | Hardcoded paths used instead of constants | Refactor to use centralized constants |
| `EXECUTOR_PROTECTED_DOC_VIOLATION` | Protected doc modified without authorization | Revert unauthorized changes; get task approval |
| `EXECUTOR_INCOMPLETE_IMPLEMENTATION` | Task acceptance criteria not met | Complete missing implementation items |

## Success Criteria

An Executor execution is successful when:

1. All source files modified per IMPL_FILE specifications
2. Target documentation updated to reflect implemented changes
3. Module doc function signatures match actual code
4. Inventory accurate if modules created/deleted
5. Change impact doc created if required
6. Valid meta.json sidecar produced with complete artifact listing
7. No hardcoded paths used (all via constants.py)
8. Protected documents respected (only modified if task authorizes)
9. Code follows existing conventions and patterns
10. Meta.json written to correct step output path
11. Reviewer approves implementation (or max_rejects not exceeded)

## Example Usage

```
Input: 
- TASK_FILE "Implement retry logic in notifications.py"
- IMPL_FILE with detailed design

Executor Actions:
1. Read notifications.py
2. Modify send_notification() function:
   - Add retry_count parameter (default 3)
   - Add retry_delay parameter (default 1.0)
   - Implement retry loop with exponential backoff
3. Update docs/codebase/02_modules/notifications.md:
   - Update "Key Functions" section with new signature
   - Add retry usage example to "Usage Examples"
   - Document retry behavior in "Notes" section
4. Verify function signatures in doc match implemented code
5. Write meta.json sidecar:
   {
     "schema_version": "v2",
     "coder_result": {
       "status": "APPROVED",
       "remark": "Implemented retry logic; updated module doc",
       "artifacts": {
         "modified_files": [
           "agent_runner_v2/notifications.py",
           "docs/codebase/02_modules/notifications.md"
         ]
       },
       "recorded_at": "2026-07-09T10:30:00+08:00"
     }
   }
6. Return APPROVED status
```

## References

- **SOP:** `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md`
- **Status Rules:** `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES.md`
- **Codebase SOP:** `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md`
- **Codebase Status Rules:** `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md`
- **Registry:** `docs/system/00_governance/bootstrap/AGENTS.md`

---

*Generated by workflow: 10_execution_scaffold_v1 | Step: generate_agents | Change: 10SCAFFOLD-20260708-8a4445fc*
