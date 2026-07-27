# Workflow Definition Revision History — Backend Specification

**Date:** 2026-01-09  
**Status:** PROPOSED  
**Priority:** HIGH

---

## Executive Summary

Implement a revision history system for workflow definitions to provide:
1. Full audit trail of all workflow definition changes
2. Ability to rollback to any previous revision
3. Elimination of hash comparison bugs that cause stale data issues
4. Clear visibility into current revision number

---

## Problem Statement

### Current Issues

1. **Stale Data Bug:** The current sync mechanism uses hash comparison to determine if an update is needed. This has caused issues where:
   - Sync reports "successful" but backend doesn't update
   - Daemon/CLI uses stale workflow definitions
   - Placeholders don't resolve correctly
   - Debugging is difficult and time-consuming

2. **No Audit Trail:** No way to track:
   - Who changed the workflow definition
   - When it was changed
   - What the previous version was
   - Why it was changed

3. **No Rollback Capability:** If a bad workflow definition is synced, there's no way to revert to a previous working version except manual database intervention.

### Root Cause

The hash comparison logic is flawed:
- Hash is calculated from `workflow.toml` only
- Doesn't include `context_extensions.py` or other Python files
- Backend may skip updates even when content has changed
- Creates confusion and wasted debugging time

---

## Solution Overview

Implement a revision-based system where:
1. Every sync creates a new revision (no hash comparison)
2. Full history is maintained in a separate table
3. Current revision number is tracked in the main table
4. Rollback capability is provided via API

---

## Database Schema

### Table: `workflow_definitions` (Modified)

```sql
ALTER TABLE workflow_definitions 
ADD COLUMN current_revision_number INTEGER NOT NULL DEFAULT 1;

-- Add index for faster lookups
CREATE INDEX idx_workflow_definitions_current_revision 
ON workflow_definitions(current_revision_number);
```

**Schema:**
```sql
workflow_definitions
- id (PK)
- workflow_name (UNIQUE, VARCHAR)
- definition (JSONB)
- source_hash (VARCHAR)
- current_revision_number (INTEGER, DEFAULT 1)  -- NEW
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Table: `workflow_definition_revisions` (New)

```sql
CREATE TABLE workflow_definition_revisions (
    id SERIAL PRIMARY KEY,
    workflow_definition_id INTEGER NOT NULL REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    definition JSONB NOT NULL,
    source_hash VARCHAR NOT NULL,
    changed_by VARCHAR NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    change_reason TEXT,
    
    -- Ensure unique revision number per workflow
    UNIQUE(workflow_definition_id, revision_number)
);

-- Indexes for performance
CREATE INDEX idx_revisions_workflow_id 
ON workflow_definition_revisions(workflow_definition_id);

CREATE INDEX idx_revisions_changed_at 
ON workflow_definition_revisions(changed_at DESC);

CREATE INDEX idx_revisions_revision_number 
ON workflow_definition_revisions(revision_number DESC);
```

---

## API Endpoints

### 1. Sync Workflow Definition (Modified)

**Endpoint:** `POST /api/admin/workflows/sync`

**Request:**
```json
{
  "workflow_name": "sdlc_00_init_doc_v1",
  "definition": { ... },
  "preserve_history": true,
  "changed_by": "sync_script",
  "change_reason": "Updated prompt templates"
}
```

**Response (New Workflow):**
```json
{
  "status": "created",
  "workflow": {
    "id": 1,
    "workflow_name": "sdlc_00_init_doc_v1",
    "current_revision_number": 1,
    "source_hash": "abc123...",
    "created_at": "2026-01-09T10:00:00Z",
    "updated_at": "2026-01-09T10:00:00Z"
  },
  "revision": {
    "id": 1,
    "revision_number": 1,
    "changed_by": "sync_script",
    "changed_at": "2026-01-09T10:00:00Z",
    "change_reason": "Initial workflow creation"
  }
}
```

**Response (Update):**
```json
{
  "status": "updated",
  "workflow": {
    "id": 1,
    "workflow_name": "sdlc_00_init_doc_v1",
    "current_revision_number": 5,
    "source_hash": "def456...",
    "created_at": "2026-01-09T10:00:00Z",
    "updated_at": "2026-01-09T14:30:00Z"
  },
  "revision": {
    "id": 5,
    "revision_number": 5,
    "changed_by": "sync_script",
    "changed_at": "2026-01-09T14:30:00Z",
    "change_reason": "Updated prompt templates"
  },
  "previous_revision": 4
}
```

**Implementation:**
```python
def sync_workflow(request):
    workflow_name = request.data['workflow_name']
    new_definition = request.data['definition']
    changed_by = request.data.get('changed_by', 'unknown')
    change_reason = request.data.get('change_reason', '')
    
    new_hash = calculate_hash(new_definition)
    
    # Get or create workflow definition
    workflow_def, created = WorkflowDefinition.objects.get_or_create(
        workflow_name=workflow_name,
        defaults={
            'definition': new_definition,
            'source_hash': new_hash,
            'current_revision_number': 1
        }
    )
    
    if created:
        # First revision
        revision = WorkflowDefinitionRevision.objects.create(
            workflow_definition=workflow_def,
            revision_number=1,
            definition=new_definition,
            source_hash=new_hash,
            changed_by=changed_by,
            changed_at=now(),
            change_reason=change_reason or "Initial workflow creation"
        )
        return Response({
            "status": "created",
            "workflow": workflow_def.to_dict(),
            "revision": revision.to_dict()
        }, status=201)
    else:
        # Update existing - always create new revision
        new_revision_number = workflow_def.current_revision_number + 1
        
        revision = WorkflowDefinitionRevision.objects.create(
            workflow_definition=workflow_def,
            revision_number=new_revision_number,
            definition=new_definition,
            source_hash=new_hash,
            changed_by=changed_by,
            changed_at=now(),
            change_reason=change_reason or "Workflow sync"
        )
        
        # Update current version
        previous_revision = workflow_def.current_revision_number
        workflow_def.definition = new_definition
        workflow_def.source_hash = new_hash
        workflow_def.current_revision_number = new_revision_number
        workflow_def.save()
        
        return Response({
            "status": "updated",
            "workflow": workflow_def.to_dict(),
            "revision": revision.to_dict(),
            "previous_revision": previous_revision
        })
```

---

### 2. List Workflow Revisions (New)

**Endpoint:** `GET /api/admin/workflows/{workflow_name}/revisions`

**Query Parameters:**
- `limit` (optional, default 50): Number of revisions to return
- `offset` (optional, default 0): Pagination offset

**Response:**
```json
{
  "workflow_name": "sdlc_00_init_doc_v1",
  "current_revision_number": 5,
  "total_revisions": 5,
  "revisions": [
    {
      "id": 5,
      "revision_number": 5,
      "source_hash": "def456...",
      "changed_by": "sync_script",
      "changed_at": "2026-01-09T14:30:00Z",
      "change_reason": "Updated prompt templates"
    },
    {
      "id": 4,
      "revision_number": 4,
      "source_hash": "ghi789...",
      "changed_by": "sync_script",
      "changed_at": "2026-01-08T10:15:00Z",
      "change_reason": "Added new step"
    }
  ]
}
```

**Implementation:**
```python
def list_revisions(request, workflow_name):
    workflow_def = get_object_or_404(WorkflowDefinition, workflow_name=workflow_name)
    
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    
    revisions = WorkflowDefinitionRevision.objects.filter(
        workflow_definition=workflow_def
    ).order_by('-revision_number')[offset:offset+limit]
    
    total = WorkflowDefinitionRevision.objects.filter(
        workflow_definition=workflow_def
    ).count()
    
    return Response({
        "workflow_name": workflow_name,
        "current_revision_number": workflow_def.current_revision_number,
        "total_revisions": total,
        "revisions": [r.to_dict() for r in revisions]
    })
```

---

### 3. Get Specific Revision (New)

**Endpoint:** `GET /api/admin/workflows/{workflow_name}/revisions/{revision_number}`

**Response:**
```json
{
  "id": 3,
  "workflow_name": "sdlc_00_init_doc_v1",
  "revision_number": 3,
  "definition": { ... },
  "source_hash": "abc123...",
  "changed_by": "sync_script",
  "changed_at": "2026-01-07T16:45:00Z",
  "change_reason": "Updated prompt templates"
}
```

**Implementation:**
```python
def get_revision(request, workflow_name, revision_number):
    workflow_def = get_object_or_404(WorkflowDefinition, workflow_name=workflow_name)
    revision = get_object_or_404(
        WorkflowDefinitionRevision,
        workflow_definition=workflow_def,
        revision_number=revision_number
    )
    
    result = revision.to_dict()
    result['workflow_name'] = workflow_name
    result['definition'] = revision.definition  # Include full definition
    
    return Response(result)
```

---

### 4. Rollback to Revision (New)

**Endpoint:** `POST /api/admin/workflows/{workflow_name}/rollback`

**Request:**
```json
{
  "target_revision_number": 3,
  "changed_by": "operator",
  "change_reason": "Rolling back due to broken prompts"
}
```

**Response:**
```json
{
  "status": "rolled_back",
  "workflow": {
    "id": 1,
    "workflow_name": "sdlc_00_init_doc_v1",
    "current_revision_number": 6,
    "source_hash": "abc123...",
    "updated_at": "2026-01-09T15:00:00Z"
  },
  "revision": {
    "id": 6,
    "revision_number": 6,
    "changed_by": "operator",
    "changed_at": "2026-01-09T15:00:00Z",
    "change_reason": "Rollback to revision 3"
  },
  "restored_from_revision": 3
}
```

**Implementation:**
```python
def rollback_workflow(request, workflow_name):
    workflow_def = get_object_or_404(WorkflowDefinition, workflow_name=workflow_name)
    
    target_revision_number = request.data.get('target_revision_number')
    if not target_revision_number:
        return Response({"error": "target_revision_number is required"}, status=400)
    
    target_revision = get_object_or_404(
        WorkflowDefinitionRevision,
        workflow_definition=workflow_def,
        revision_number=target_revision_number
    )
    
    changed_by = request.data.get('changed_by', 'unknown')
    change_reason = request.data.get('change_reason', f'Rollback to revision {target_revision_number}')
    
    # Create new revision for the rollback
    new_revision_number = workflow_def.current_revision_number + 1
    
    revision = WorkflowDefinitionRevision.objects.create(
        workflow_definition=workflow_def,
        revision_number=new_revision_number,
        definition=target_revision.definition,
        source_hash=target_revision.source_hash,
        changed_by=changed_by,
        changed_at=now(),
        change_reason=change_reason
    )
    
    # Update current version
    workflow_def.definition = target_revision.definition
    workflow_def.source_hash = target_revision.source_hash
    workflow_def.current_revision_number = new_revision_number
    workflow_def.save()
    
    return Response({
        "status": "rolled_back",
        "workflow": workflow_def.to_dict(),
        "revision": revision.to_dict(),
        "restored_from_revision": target_revision_number
    })
```

---

### 5. Compare Revisions (New, Optional)

**Endpoint:** `GET /api/admin/workflows/{workflow_name}/revisions/compare`

**Query Parameters:**
- `from_revision` (required): Source revision number
- `to_revision` (required): Target revision number

**Response:**
```json
{
  "workflow_name": "sdlc_00_init_doc_v1",
  "from_revision": {
    "revision_number": 3,
    "changed_at": "2026-01-07T16:45:00Z",
    "changed_by": "sync_script"
  },
  "to_revision": {
    "revision_number": 5,
    "changed_at": "2026-01-09T14:30:00Z",
    "changed_by": "sync_script"
  },
  "diff": {
    "added_steps": ["step_03_new_validation"],
    "removed_steps": [],
    "modified_steps": ["step_01_generate"],
    "added_artifacts": ["NEW_ARTIFACT_KEY"],
    "removed_artifacts": [],
    "modified_artifacts": ["EXISTING_ARTIFACT_KEY"]
  }
}
```

**Implementation:**
```python
def compare_revisions(request, workflow_name):
    workflow_def = get_object_or_404(WorkflowDefinition, workflow_name=workflow_name)
    
    from_revision_num = request.query_params.get('from_revision')
    to_revision_num = request.query_params.get('to_revision')
    
    if not from_revision_num or not to_revision_num:
        return Response({"error": "Both from_revision and to_revision are required"}, status=400)
    
    from_revision = get_object_or_404(
        WorkflowDefinitionRevision,
        workflow_definition=workflow_def,
        revision_number=from_revision_num
    )
    to_revision = get_object_or_404(
        WorkflowDefinitionRevision,
        workflow_definition=workflow_def,
        revision_number=to_revision_num
    )
    
    # Calculate diff (simplified example)
    diff = calculate_definition_diff(from_revision.definition, to_revision.definition)
    
    return Response({
        "workflow_name": workflow_name,
        "from_revision": {
            "revision_number": from_revision.revision_number,
            "changed_at": from_revision.changed_at,
            "changed_by": from_revision.changed_by
        },
        "to_revision": {
            "revision_number": to_revision.revision_number,
            "changed_at": to_revision.changed_at,
            "changed_by": to_revision.changed_by
        },
        "diff": diff
    })
```

---

## Migration Strategy

### Step 1: Database Migration

```python
# migrations/0002_add_revision_history.py

def migrate(apps, schema_editor):
    WorkflowDefinition = apps.get_model('workflows', 'WorkflowDefinition')
    WorkflowDefinitionRevision = apps.get_model('workflows', 'WorkflowDefinitionRevision')
    
    # Add current_revision_number column
    # (handled by schema_editor automatically)
    
    # Create initial revisions for existing workflows
    for workflow_def in WorkflowDefinition.objects.all():
        WorkflowDefinitionRevision.objects.create(
            workflow_definition=workflow_def,
            revision_number=1,
            definition=workflow_def.definition,
            source_hash=workflow_def.source_hash,
            changed_by="migration",
            changed_at=workflow_def.created_at,
            change_reason="Initial revision created by migration"
        )
        workflow_def.current_revision_number = 1
        workflow_def.save()
```

### Step 2: Backward Compatibility

The sync endpoint remains backward compatible:
- Old clients that don't send `changed_by` or `change_reason` will use defaults
- Response format is extended, not changed (old fields still present)

### Step 3: Testing

1. **Unit Tests:**
   - Test initial workflow creation
   - Test workflow update creates revision
   - Test rollback creates new revision
   - Test revision listing and pagination
   - Test revision comparison

2. **Integration Tests:**
   - Test sync script with new backend
   - Test operator console revision history display
   - Test rollback via operator console

3. **Migration Tests:**
   - Test migration on existing data
   - Verify all existing workflows get revision 1
   - Verify current_revision_number is set correctly

---

## Client-Side Changes

### Sync Script (`sync_workflows.py`)

Add optional parameters:
```python
parser.add_argument("--changed-by", default="sync_script", help="Who is making this change")
parser.add_argument("--change-reason", default="", help="Reason for the change")

# In _post_sync():
payload = {
    "workflow_name": workflow_name,
    "definition": definition,
    "preserve_history": preserve_history,
    "changed_by": args.changed_by,
    "change_reason": args.change_reason
}
```

### Operator Console

Add to workflow detail view:
- Display current revision number
- "View History" button → shows revision list
- "Rollback" button → shows revision selector

---

## Benefits

1. **No More Stale Data Bugs:** Always update, no hash comparison
2. **Full Audit Trail:** Track who, when, why for every change
3. **Rollback Capability:** Revert to any previous version
4. **Better Debugging:** Can inspect any historical version
5. **Compliance:** Meets audit requirements for configuration management
6. **User Confidence:** Users can see change history and rollback if needed

---

## Implementation Checklist

- [ ] Create database migration for `current_revision_number` column
- [ ] Create `workflow_definition_revisions` table
- [ ] Modify sync endpoint to always create revisions
- [ ] Add `/revisions` endpoint
- [ ] Add `/revisions/{revision_number}` endpoint
- [ ] Add `/rollback` endpoint
- [ ] Add `/revisions/compare` endpoint (optional)
- [ ] Update sync script to send `changed_by` and `change_reason`
- [ ] Update operator console to display revision info
- [ ] Add rollback UI to operator console
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test migration on existing data
- [ ] Update API documentation
- [ ] Deploy to staging and test
- [ ] Deploy to production

---

## Future Enhancements

1. **Revision Tags:** Allow tagging revisions (e.g., "stable", "beta", "release-v1.0")
2. **Branching:** Support multiple branches (like git) for parallel development
3. **Approval Workflow:** Require approval before syncing to production
4. **Automated Rollback:** Auto-rollback if workflow execution fails after sync
5. **Diff Viewer:** Visual diff viewer in operator console
6. **Export/Import:** Export revision history for backup or migration

---

## References

- **Related Issue:** Stale backend data breaks context extension placeholder resolution
- **Related Spec:** ARCHITECTURAL_REFACTOR.md (CLI-only architecture)
- **Related Code:** `agent_runner_v2/sync_workflows.py`

---

**Author:** Qwen Code  
**Reviewers:** [Pending]  
**Approval:** [Pending]
