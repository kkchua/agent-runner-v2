---
template_id: "SYS-03-CR"
version: "1.0.0"
doc_type: "review_artifact"
authority: "workflow-generated"
scan_policy: "conditional"
scan_reason: "Technical critique of initiative document INIT-20260723-001"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "SDLC00INIT-20260723-8831adbd"
source_document: "INIT-20260723-001_console-sdlc10-support.md"
---

# Technical Critique: INIT-20260723-001

## Decision: APPROVED WITH FINDINGS

## Summary

The initiative document INIT-20260723-001 (Operator Console SDLC Phase 1 - Initiative
Intake Support) is technically sound and implementable. However, the scope description
is imprecise because a file picker UI component already exists in the codebase. The
actual implementation work is narrower than stated: adding conditional visibility logic
and modifying the submit_job method to accept input artifact paths. The initiative is
approved with recommendations to clarify the scope to accurately reflect existing
infrastructure.

## Technical Findings

### Finding 1: File Picker UI Component Already Exists (Major)

**Severity:** Major

**Location:** Scope section, lines 73-77

**Observation:**

The initiative states as "In Scope":
"File picker UI component (Flet FilePicker + TextField + Browse button)."

However, the operator console already implements this component in app.py:
- ft.FilePicker instance at line 164
- ft.TextField for file path display at line 165
- Browse button at line 176 with on_browse handler
- file_picker_row component at line 551

The existing implementation uses the correct Flet API:
```python
file_picker = ft.FilePicker()
file_path_tf = ft.TextField(label="Input File", read_only=True, expand=True)
browse_btn = ft.ElevatedButton("Browse", on_click=on_browse)
```

The on_browse handler (lines 167-174) correctly invokes:
```python
files = await file_picker.pick_files(
    file_type=ft.FilePickerFileType.CUSTOM,
    allowed_extensions=["md"],
)
```

**Impact:**

The scope description is misleading. The actual work required is:
1. Modify visibility logic for file_picker_row (not create from scratch)
2. Add conditional visibility based on SDLC workflow selection
3. Connect the selected file path to submit_job

**Recommendation:**

Update the In Scope section to read:
"Enhance existing file picker UI component with conditional visibility logic for
SDLC workflows. Connect selected file path to submit_job as input artifact."

---

### Finding 2: runner_service.submit_job Missing Input Artifact Parameter (Major)

**Severity:** Major

**Location:** Scope section, line 78-79

**Observation:**

The initiative states:
"Update runner_service.submit_job() to accept and forward input artifact
paths to the backend."

This is accurate. The current implementation in runner_service.py (lines 25-43)
does not accept input artifact paths. The submit_job method signature is:

```python
def submit_job(
    self,
    *,
    repo_path: str,
    workflow: WorkflowEntry,
    initiative_id: str = "",
    coder: str = "",
) -> str:
```

The method builds args but has no parameter for --input arguments.

**Verification:**

submit_commands.py supports --input KEY=VALUE via:
```python
p.add_argument("--input", action="append", default=[], metavar="KEY=VALUE",
               help="input_payload key=value (repeatable).")
```

The _parse_kv function (lines 25-33) correctly parses KEY=VALUE pairs.

**Impact:**

This is a required change that matches the scope description. The implementation
should add an input_artifacts: dict[str, str] | None parameter to submit_job.

**Recommendation:**

This finding confirms the scope is correct. No change needed.

---

### Finding 3: Conditional Visibility Logic Not Implemented (Major)

**Severity:** Major

**Location:** Scope section, line 74-75

**Observation:**

The initiative states:
"Conditional visibility logic: show the file picker only when the action is
'submit job' AND the selected workflow name starts with 'sdlc_'."

The update_visibility function (lines 427-436 in app.py) handles visibility for
workflow_dd and cleanup_dry_run_cb but does NOT control file_picker_row visibility.

Current implementation:
```python
def update_visibility(_event=None) -> None:
    action = action_dd.value or ""
    needs_run = action in {"approval", "cancel job", "reset step"}
    workflow_dd.visible = action in {"submit job", ...}
    cleanup_dry_run_cb.visible = action == "cleanup"
```

The file_picker_row is created with visible=True at line 551 and never changes.

**Impact:**

This is a required implementation that matches the scope description. The conditional
logic must:
1. Check if action_dd.value == "submit job"
2. Check if workflow_dd.value starts with "sdlc_"
3. Set file_picker_row.visible based on both conditions

**Recommendation:**

This finding confirms the scope is correct. No change needed.

---

### Finding 4: Draft Document Used DRAFT_INIT_DOC, Initiative Uses DRAFT_INIT_FILE (Minor)

**Severity:** Minor (Informational)

**Location:** Comparison between draft and initiative

**Observation:**

The draft document (DRAFT-INIT-20260722-001) referenced DRAFT_INIT_DOC:
- Line 35: "Users must know the exact artifact key names (DRAFT_INIT_DOC)"
- Line 72: "--input DRAFT_INIT_DOC=<path>"

The initiative document correctly uses DRAFT_INIT_FILE:
- Line 36: "Users must know the exact artifact key name (DRAFT_INIT_FILE)"
- Line 77: "Pass the selected file path as --input DRAFT_INIT_FILE=<path>"

The review artifact (console-sdlc10-support-REV-00-init.md) confirms this is an
expected translation per the _FILE naming convention.

**Impact:**

This is a correct correction. The initiative uses the proper artifact key suffix.

**Recommendation:**

No change needed. The artifact key naming is correct.

---

### Finding 5: Flet Dependency Not Version-Pinned (Minor)

**Severity:** Minor

**Location:** pyproject.toml, line 18

**Observation:**

The pyproject.toml specifies:
```toml
console = [
    "flet",
]
```

The Flet dependency is not version-pinned. This could lead to API drift if
Flet releases breaking changes.

**Verification:**

The Flet FilePicker API used in app.py (pick_files with file_type and
allowed_extensions) is consistent with Flet's documented API.

**Impact:**

Low risk for Phase 1 development. However, as the console application grows,
version pinning becomes more important for reproducibility.

**Recommendation:**

Consider adding a version constraint (e.g., flet>=0.21.0) for reproducibility.
This is not blocking for approval.

---

## Design Quality Assessment

### Is This the Right Approach?

Yes. The initiative correctly identifies the need to integrate SDLC workflow
input handling into the operator console. The approach of:

1. Adding conditional UI visibility based on workflow type
2. Extending submit_job to pass input artifacts
3. Keeping changes isolated to the console layer

...is architecturally sound and consistent with the Layer 2 platform contract.

### Are There Better Alternatives?

One alternative would be to define a workflow input schema that the console
reads dynamically, rather than hardcoding "sdlc_" prefix checks. However,
this would add complexity that is not justified for Phase 1. The masterplan
indicates this is the first of 8 phases, so a hardcoded approach for Phase 1
is acceptable with a note about future generalization.

### Is the Initiative Implementable as Described?

Yes, with the clarification that the file picker component exists and needs
enhancement rather than creation from scratch. The technical path is clear:

1. Modify update_visibility() to conditionally show file_picker_row
2. Add input_artifacts parameter to runner_service.submit_job()
3. Pass the selected file path as --input DRAFT_INIT_FILE=<path>
4. Test the complete flow

---

## Recommendations

### Must Do Before Implementation

1. **Update Scope Description:** Clarify that the file picker component exists
   and the work is to add conditional visibility and input artifact handling.

### Should Consider

2. **Add Version Constraint for Flet:** Consider pinning the Flet version in
   pyproject.toml to prevent API drift.

3. **Document Existing File Picker Usage:** Add comments in app.py explaining
   that the file picker is reused for SDLC workflow input handling.

### Good to Know

4. **The existing file picker uses allowed_extensions=["md"]:** This is correct
   for draft initiative files. Ensure future phases update this if different
   file types are needed.

---

## Governance Compliance

### Layer 1 Compliance

The initiative does not redefine Layer 1 governance concepts. It correctly
references Layer 1 as read-only authority in constraints (lines 109-111).

### Layer 2 Compliance

The initiative acknowledges the Layer 2 METADATA_CONTRACT.md constraint
(line 108) without altering or extending it. The initiative operates within
Layer 3 bounds.

### Layer 3 Scope

The initiative correctly stays within Layer 3 -- defining concrete delivery
work for the operator console within the agent-runner-v2 platform context.

---

## Conclusion

The initiative is approved for progression to the planning phase. The technical
findings identify that the file picker component already exists and the actual
implementation work is narrower than stated. The recommendations should be
addressed to improve clarity for implementers.