---
doc_type: "review_test_criteria"
lifecycle_status: "reviewed"
source_artifact: "TEST_CRITERIA-20260809-001.md"
job_id: "AMB-zlk6p8rh"
reviewed_at: "2026-08-09"
verdict: "APPROVED"
---

# Review: Test Criteria Document

## Decision: APPROVED

The test criteria document is APPROVED with 6 findings (0 critical, 3 major, 3 minor). All findings are corrections to the summary table or clarifications to criterion anchors -- none invalidate the test criteria as a whole.

---

## Review Summary

| Check | Result | Notes |
|---|---|---|
| Coverage (8 phases) | PASS | All 8 phases (P1-P8) have dedicated criteria sections |
| Specificity | PASS (with caveats) | 4 criteria have vague anchors requiring interpretation |
| Traceability | PASS | SV-CS section maps all spec sections to criteria |
| Meta-test-criteria (4 invariants) | PASS | INV-1 through INV-4 present, propagated via SV-MP |
| Negative criteria | PASS | 6 categories, 25 negative criteria total |
| Self-validation | PASS | 21 self-validation criteria across 3 sub-sections |

---

## Findings

### Major Findings

#### M-1: Summary Table Count Error -- Negative Criteria

- Location: Line 497, Summary of Criteria Counts table
- Actual value: Table claims "Negative Criteria | 23"
- Expected value: The actual count is 25 (NC-BIL: 8 + NC-NA: 3 + NC-SI: 4 + NC-HT: 4 + NC-VC: 2 + NC-SL: 4 = 25)
- Fix: Change "23" to "25" in the Negative Criteria row

#### M-2: Summary Table Count Error -- Self-Validation

- Location: Line 498, Summary of Criteria Counts table
- Actual value: Table claims "Self-Validation | 18"
- Expected value: The actual count is 21 (SV-CS: 13 + SV-VG: 5 + SV-MP: 3 = 21)
- Fix: Change "18" to "21" in the Self-Validation row

#### M-3: Summary Table Total Is Incorrect

- Location: Line 499, Summary of Criteria Counts table
- Actual value: Table claims "**Total** | **257**"
- Expected value: Correct total is 262 (22+33+28+34+18+26+28+27+25+21 = 262)
- Fix: Change "257" to "262" in the Total row

---

### Minor Findings

#### N-1: Vague Anchor in TC-P1-019

- Location: Line 69, TC-P1-019
- Actual text: "The natural_phases list accounts for all major stages described in the runtime spec."
- Issue: The phrase "all major stages" is subjective. A gatekeeper must decide what counts as a "major" stage.
- Fix: Anchor to a verifiable reference, e.g., "The natural_phases list includes at least one entry for each distinct phase or stage explicitly named in the spec domain overview section."

#### N-2: Vague Anchors in TC-P2-029 and TC-P2-030

- Location: Lines 122-123
- TC-P2-029 actual text: "VR-007 checks structural validity constraints applicable to the target domain."
- TC-P2-030 actual text: "VR-008 checks semantic validity constraints (cross-property constraints, value ranges, referential integrity) applicable to the target domain."
- Issue: "applicable to the target domain" is open-ended. A gatekeeper cannot deterministically verify whether a rule is or is not "applicable."
- Fix: Anchor to the spec. E.g., "VR-007 checks at least one structural constraint explicitly stated or implied in the spec Constraints section" and "VR-008 checks at least one semantic constraint explicitly stated or implied in the spec domain description."

#### N-3: Hardcoded Builder Job-ID in NC-BIL-003

- Location: Line 401, NC-BIL-003
- Actual text: "The string 'AMB-zlk6p8rh' (or any job-specific builder identifier) must NOT appear in any generated artifact."
- Issue: The literal string "AMB-zlk6p8rh" is a builder-specific job identifier. While the intent is correct, embedding a specific job-id in the test criteria makes the criteria job-specific rather than reusable. The parenthetical "(or any job-specific builder identifier)" does provide the generalization, but the hardcoded value should not be the primary assertion.
- Fix: Rewrite as: "NC-BIL-003: No job-specific builder identifier (job-id, run-id, or session token from the builder execution context) must appear in any generated artifact. For this job, the prohibited value is 'AMB-zlk6p8rh'."

---

## Verified Strengths

1. Coverage is comprehensive. All 8 spec sections (Purpose, Input, Output, Constraints x6, Knowledge Requirements, Success Criteria, What NOT to Specify) are mapped in SV-CS-001 through SV-CS-013.

2. The 4 meta-test-criteria are well-defined in the Introduction (lines 28-32) and elaborated in Phase 1 (TC-P1-011 through TC-P1-016). Propagation rules are explicitly stated in SV-MP-001 through SV-MP-003.

3. Negative criteria are thorough. Six categories cover builder identity leakage, non-ASCII content, scope invention, hardcoded types, vague criteria, and structural leakage. Each category has specific, string-searchable prohibitions.

4. Specificity is generally strong. Out of 262 criteria, only 4 have vague anchors (TC-P1-019, TC-P2-029, TC-P2-030, and arguably NC-BIL-003). The remaining 258 are deterministic and gatekeeper-verifiable.

5. The self-validation section provides explicit traceability from spec sections to criterion identifiers, enabling independent verification of coverage.

---

## Conclusion

The test criteria document is fit for purpose. The 3 major findings are all corrections to the summary table counts -- they do not affect the validity of any individual criterion. The 3 minor findings are anchor-clarification recommendations that improve gatekeeper determinism but do not invalidate the criteria as written. The document is APPROVED.

---

**End of Review**
