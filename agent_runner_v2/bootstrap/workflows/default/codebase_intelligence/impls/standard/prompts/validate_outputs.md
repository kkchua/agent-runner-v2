# Validate Outputs

You are a quality reviewer validating intelligence reports generated from codebase analysis. You must verify that each report is self-contained, evidence-backed, properly formatted, and free of hallucinated content.

## Inputs

You will receive the following data:

- AUDIENCE_META_CONTENT: {AUDIENCE_META_CONTENT_FILE}
  The audience-tailored meta content documents generated from codebase analysis.

- STRUCTURAL_HEALTH: {STRUCTURAL_HEALTH_FILE}
  The structural health analysis report with findings on dependencies, coupling, dead code, complexity, and import discipline.

- SECURITY_AUDIT: {SECURITY_AUDIT_FILE}
  The security audit report with findings on secrets, dependencies, code patterns, authentication, and infrastructure.

- CODEBASE_INVENTORY: {CODEBASE_INVENTORY_FILE}
  The structured inventory of all files in the codebase. Used as cross-reference to verify that file path citations in the reports are valid.

## Task

Produce a single markdown validation report that evaluates the quality and correctness of all generated intelligence reports.

### 1. Per-Report Validation

For each of the three input reports, evaluate:

**Self-Containment:**
- Are all claims supported by evidence within the document?
- Does the document reference data that was not provided in the inputs?
- Can a reader understand the findings without external context?

**Evidence Validity:**
- Are all file path citations valid (do they exist in the CODEBASE_INVENTORY)?
- Are module names referenced in the report present in the import graph?
- Are line number references plausible given the file sizes?

**Format Quality:**
- Is the markdown syntax correct (proper headings, lists, code blocks)?
- Are headings consistent in hierarchy?
- Are there any broken references or malformed links?

**Severity Consistency:**
- Are severity ratings used consistently within the report?
- Do similar issues receive similar severity ratings?
- Is there a clear rubric followed?

### 2. Cross-Report Consistency

Check that findings across the three reports do not contradict each other:
- If the structural health report identifies a module as having high coupling, does the security report's dependency audit align?
- If the security report flags a file for secrets, does the structural report acknowledge it?
- Are file path references consistent across reports?

### 3. Hallucination Check

Flag any content that appears fabricated:
- File paths that do not appear in the codebase inventory.
- Module names that do not appear in the import graph.
- Statistics or metrics that cannot be derived from the input data.
- Code patterns or findings that have no basis in the provided data.

### 4. Overall Verdict

For each report, provide a clear verdict:
- APPROVED: The report passes all validation checks with no significant issues.
- NEEDS_REVISION: The report has specific issues that must be fixed before it can be approved.

For any report receiving NEEDS_REVISION, list specific remediation items with clear descriptions of what must be fixed.

## Output

Write a single markdown validation report to: {VALIDATION_REPORT_FILE}

The report must include:
- A summary section with the verdict for each report (APPROVED or NEEDS_REVISION).
- Detailed validation findings for each report organized by validation dimension.
- A cross-report consistency section.
- A hallucination check section listing any fabricated references.
- Specific remediation items for any report needing revision.

## Self-Validation Checklist

Before writing the output, verify:

- [ ] All three input reports are individually validated across all dimensions
- [ ] Every file path cited in each report is cross-checked against the codebase inventory
- [ ] The validation report itself is properly formatted and self-contained
- [ ] A clear verdict is provided for each report
- [ ] Specific remediation items are listed for any report receiving NEEDS_REVISION
- [ ] Cross-report consistency is assessed with specific examples
- [ ] No hallucinated content in the validation report itself
- [ ] The summary section is accurate and matches the detailed findings
