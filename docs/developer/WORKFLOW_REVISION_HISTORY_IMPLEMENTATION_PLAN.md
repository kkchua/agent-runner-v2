# Workflow Revision History — Implementation Plan

**Date:** 2026-01-09  
**Spec:** `docs/developer/WORKFLOW_REVISION_HISTORY_SPEC.md`  
**Status:** PLANNING

---

## Overview

This document outlines the step-by-step implementation plan for adding workflow definition revision history to both the backend and agent-runner-v2 client.

---

## Phase 1: Backend Implementation

### 1.1 Database Schema Changes

**Location:** Backend repo (agent-runner-backend)

**Tasks:**
- [ ] Create migration `0002_add_workflow_revision_history.py`
- [ ] Add `current_revision_number` column to `workflow_definitions` table
- [ ] Create `workflow_definition_revisions` table
- [ ] Add indexes for performance
- [ ] Write data migration to create revision 1 for existing workflows
- [ ] Test migration on staging database

**Files to Create/Modify:**
```
backend/
├── migrations/
│   └── 0002_add_workflow_revision_history.py  (NEW)
├── models.py
│   └── Add WorkflowDefinitionRevision model
│   └── Add current_revision_number field to WorkflowDefinition
└── admin.py
    └── Register WorkflowDefinitionRevision
```

**Estimated Time:** 2-3 hours

---

### 1.2 API Endpoint Updates

**Location:** Backend repo

**Tasks:**
- [ ] Modify `POST /api/admin/workflows/sync` to always create revisions
- [ ] Add `GET /api/admin/workflows/{name}/revisions` endpoint
- [ ] Add `GET /api/admin/workflows/{name}/revisions/{num}` endpoint
- [ ] Add `POST /api/admin/workflows/{name}/rollback` endpoint
- [ ] Add `GET /api/admin/workflows/{name}/revisions/compare` endpoint (optional)
- [ ] Update serializers for new fields
- [ ] Add comprehensive error handling

**Files to Create/Modify:**
```
backend/
├── views.py (or views/workflows.py)
│   └── Modify sync_workflow()
│   └── Add list_revisions()
│   └── Add get_revision()
│   └── Add rollback_workflow()
│   └── Add compare_revisions()
├── serializers.py
│   └── Add WorkflowDefinitionRevisionSerializer
│   └── Update WorkflowDefinitionSerializer
└── urls.py
    └── Add new URL patterns
```

**Estimated Time:** 4-5 hours

---

### 1.3 Backend Testing

**Tasks:**
- [ ] Unit tests for revision creation on sync
- [ ] Unit tests for rollback functionality
- [ ] Unit tests for revision listing
- [ ] Integration tests for full workflow
- [ ] Migration tests on existing data
- [ ] Performance tests with large revision counts

**Files to Create:**
```
backend/tests/
├── test_models.py
│   └── Test WorkflowDefinitionRevision model
├── test_views.py
│   └── Test all new endpoints
├── test_migrations.py
│   └── Test data migration
└── test_integration.py
    └── End-to-end workflow tests
```

**Estimated Time:** 3-4 hours

---

### 1.4 Backend Deployment

**Tasks:**
- [ ] Deploy to staging environment
- [ ] Run migration on staging
- [ ] Verify existing workflows have revision 1
- [ ] Test sync creates revisions
- [ ] Test rollback works
- [ ] Monitor for issues
- [ ] Deploy to production
- [ ] Run migration on production
- [ ] Verify production data

**Estimated Time:** 2-3 hours (including monitoring)

---

## Phase 2: Client-Side Implementation (agent-runner-v2)

### 2.1 Sync Script Updates

**Location:** `agent_runner_v2/sync_workflows.py`

**Tasks:**
- [ ] Add `--changed-by` CLI argument (default: "sync_script")
- [ ] Add `--change-reason` CLI argument (default: "")
- [ ] Update `_post_sync()` to include new fields in payload
- [ ] Update response parsing to handle new response format
- [ ] Display revision number in output
- [ ] Test with updated backend

**Files to Modify:**
```
agent_runner_v2/
└── sync_workflows.py
    └── Add CLI arguments
    └── Update payload construction
    └── Update response handling
```

**Estimated Time:** 1-2 hours

---

### 2.2 Batch Script Updates

**Location:** `sync-workflows-to-backend.bat`

**Tasks:**
- [ ] Add `--changed-by` parameter support
- [ ] Add `--change-reason` parameter support
- [ ] Update help text
- [ ] Test batch script

**Files to Modify:**
```
Root directory:
└── sync-workflows-to-backend.bat
    └── Add parameter handling
```

**Estimated Time:** 30 minutes

---

### 2.3 Client Testing

**Tasks:**
- [ ] Test sync creates revisions in backend
- [ ] Test `--changed-by` parameter works
- [ ] Test `--change-reason` parameter works
- [ ] Test response parsing
- [ ] Test error handling
- [ ] Test with multiple workflows

**Estimated Time:** 1-2 hours

---

## Phase 3: Operator Console Updates

### 3.1 Backend Service Updates

**Location:** `agent_runner_v2/operator_console/services/backend_service.py`

**Tasks:**
- [ ] Add `list_revisions(workflow_name)` method
- [ ] Add `get_revision(workflow_name, revision_number)` method
- [ ] Add `rollback_workflow(workflow_name, revision_number, changed_by, change_reason)` method
- [ ] Add `compare_revisions(workflow_name, from_rev, to_rev)` method (optional)
- [ ] Update `get_workflow_detail()` to include current_revision_number

**Files to Modify:**
```
agent_runner_v2/operator_console/services/
└── backend_service.py
    └── Add revision-related methods
```

**Estimated Time:** 2-3 hours

---

### 3.2 UI Components

**Location:** `agent_runner_v2/operator_console/ui/`

**Tasks:**
- [ ] Add revision info to workflow detail view
- [ ] Create "View History" dialog
- [ ] Create revision list component
- [ ] Create "Rollback" dialog with revision selector
- [ ] Add confirmation dialog for rollback
- [ ] Display revision number prominently
- [ ] Add visual indicator for current revision

**Files to Create/Modify:**
```
agent_runner_v2/operator_console/ui/
├── dialogs/
│   ├── revision_history_dialog.py  (NEW)
│   └── rollback_dialog.py  (NEW)
├── components/
│   └── revision_info.py  (NEW)
└── views/
    └── workflow_detail_view.py
        └── Add revision info section
        └── Add "View History" button
        └── Add "Rollback" button
```

**Estimated Time:** 4-5 hours

---

### 3.3 Console Testing

**Tasks:**
- [ ] Test revision history display
- [ ] Test rollback workflow
- [ ] Test error handling
- [ ] Test with multiple workflows
- [ ] Test UI responsiveness
- [ ] User acceptance testing

**Estimated Time:** 2-3 hours

---

## Phase 4: Documentation & Training

### 4.1 Documentation Updates

**Tasks:**
- [ ] Update README.md to reference new spec
- [ ] Update QWEN.md with revision history info
- [ ] Create user guide for revision history
- [ ] Create rollback procedure guide
- [ ] Update API documentation
- [ ] Add examples to spec document

**Files to Create/Modify:**
```
docs/
├── developer/
│   ├── WORKFLOW_REVISION_HISTORY_SPEC.md  (UPDATE)
│   └── WORKFLOW_REVISION_HISTORY_USER_GUIDE.md  (NEW)
└── README.md  (UPDATE)
```

**Estimated Time:** 2-3 hours

---

### 4.2 Training

**Tasks:**
- [ ] Create demo video/showcase
- [ ] Write quick reference guide
- [ ] Prepare FAQ document
- [ ] Train users on new features

**Estimated Time:** 2-3 hours

---

## Phase 5: Integration Testing & Rollout

### 5.1 End-to-End Testing

**Tasks:**
- [ ] Test full workflow: sync → view history → rollback
- [ ] Test with real workflows (sdlc_00, etc.)
- [ ] Test concurrent sync operations
- [ ] Test rollback during active daemon execution
- [ ] Test large revision counts (100+ revisions)
- [ ] Performance testing
- [ ] Load testing

**Estimated Time:** 4-5 hours

---

### 5.2 Staging Rollout

**Tasks:**
- [ ] Deploy backend to staging
- [ ] Deploy agent-runner-v2 to staging
- [ ] Run full test suite
- [ ] Monitor for 24-48 hours
- [ ] Collect feedback
- [ ] Fix any issues

**Estimated Time:** 2-3 days (including monitoring)

---

### 5.3 Production Rollout

**Tasks:**
- [ ] Schedule maintenance window (if needed)
- [ ] Deploy backend to production
- [ ] Run migration
- [ ] Verify migration success
- [ ] Deploy agent-runner-v2 to production
- [ ] Monitor for issues
- [ ] Communicate to users
- [ ] Provide support for first week

**Estimated Time:** 1-2 days

---

## Risk Assessment

### High Risk
- **Data Migration:** Could fail on existing data
  - *Mitigation:* Test on staging first, backup database
- **Backward Compatibility:** Old clients might break
  - *Mitigation:* Make new fields optional, test with old clients

### Medium Risk
- **Performance:** Large revision counts could slow queries
  - *Mitigation:* Add pagination, indexes, monitor performance
- **Concurrent Sync:** Multiple syncs at same time
  - *Mitigation:* Add database locks, test concurrent operations

### Low Risk
- **UI Changes:** Users might find new UI confusing
  - *Mitigation:* Good documentation, training, familiar design patterns

---

## Rollback Plan

If issues are discovered after deployment:

### Backend Rollback
1. Revert backend code to previous version
2. Run reverse migration (if needed)
3. Verify system stability

### Client Rollback
1. Revert agent-runner-v2 to previous version
2. Users can continue using old sync script
3. Revision history will still work (backend is backward compatible)

---

## Success Criteria

- [ ] All workflows have revision history
- [ ] Sync always creates revisions
- [ ] Rollback works correctly
- [ ] No stale data bugs
- [ ] Users can view history in console
- [ ] Performance is acceptable (< 1s response time)
- [ ] Zero data loss during migration
- [ ] Backward compatible with old clients

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Backend | 2-3 days | None |
| Phase 2: Client | 1-2 days | Phase 1 complete |
| Phase 3: Console | 2-3 days | Phase 1 complete |
| Phase 4: Documentation | 1-2 days | Phase 2 & 3 complete |
| Phase 5: Testing & Rollout | 3-5 days | All phases complete |
| **Total** | **9-15 days** | |

---

## Resource Requirements

- **Backend Developer:** 1 person (Phases 1, 5)
- **Client Developer:** 1 person (Phases 2, 3, 5)
- **QA Tester:** 1 person (Phase 5)
- **Technical Writer:** 1 person (Phase 4)

---

## Next Steps

1. **Review and approve this plan**
2. **Set up development environment**
3. **Start Phase 1: Backend implementation**
4. **Daily standups to track progress**
5. **Weekly demos to stakeholders**

---

## Questions & Decisions Needed

1. **Should we implement the compare endpoint in Phase 1 or defer?**
   - Recommendation: Defer to Phase 6 (future enhancement)

2. **Do we need to support branching/merging?**
   - Recommendation: No, keep it simple for now

3. **Should revisions be immutable?**
   - Recommendation: Yes, once created, revisions cannot be modified

4. **What's the retention policy for old revisions?**
   - Recommendation: Keep all revisions indefinitely (storage is cheap)

5. **Should we add revision tags (stable, beta, etc.)?**
   - Recommendation: Defer to future enhancement

---

**Prepared by:** Qwen Code  
**Review Status:** Pending  
**Approval Status:** Pending
