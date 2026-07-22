# Validation Record: {TASK_ID} — {Title}

---

## Preflight Gate

| Check | Result |
| ----- | ------ |
| IMPL_FILE read | {✅/❌} |
| Task ID extracted | {✅/❌} `{Task ID}` |
| Plan Status extracted | {✅/❌} `{raw}` → normalized: `{normalized}` |
| Status in allowed set (draft, in_review, approved) | {✅/❌} |
| Preflight result | ✅ PASSED / ❌ FAILED |

---

## Files Reviewed

| File | Purpose |
| ---- | ------- |
| `{file}` | {purpose} |

---

## Findings

### Scope & Alignment

| Criterion | Status | Details |
| --------- | ------ | ------- |
| {criterion} | {✅ PASS / ❌ FAIL} | {details} |

### Deliverables Completeness

| Deliverable | Status |
| ----------- | ------ |
| `{file_path}` — {description} | {✅ Present / ❌ Missing} |

### Pattern Reuse

| Component | Follows Existing Pattern | Details |
| --------- | ----------------------- | ------- |
| {component} | {✅ Yes / ❌ No} | {details} |

---

## Test Execution Results

### Command Executed

```bash
pytest {test_file} -v --tb=short
```

### Raw pytest Output

```
{paste raw pytest output here}
```

### Summary

| Metric | Value |
| ------ | ----- |
| Tests collected | {N} |
| Tests passed | {N} |
| Tests failed | {N} |
| Errors | {N} |
| Exit code | {N} |

---

## Pass/Fail Criteria

| # | Criterion | Result |
| - | --------- | ------ |
| 1 | {criterion} | {✅ PASS / ❌ FAIL} |

---

## Final Decision

**APPROVED / REJECTED**

{Summary paragraph — if APPROVED: all checks pass, no blocking findings. If REJECTED: list concrete blocking findings and required corrections.}
