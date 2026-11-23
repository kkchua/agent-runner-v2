# Baseline transaction: CLI and recovery behavior

Phase B makes `change-requirements` an atomic, recoverable baseline transaction.
All callers (`change_requirements`, `complete_baseline_transaction`, adapters and
the CLI) delegate to the single locked entry point
`job_state.execute_baseline_transaction`.

## CLI

```
agent-runner change-requirements \
  --job-id <job> \
  --new-requirements-file <path> \
  --reason "<why>" \
  [--request-id <stable-id>]
```

The CLI performs **no second save**. On success it prints `status`, `new_baseline`,
`request_id`, `operation_id` and `transaction_status`.

Supply `--request-id` to make retries safe. Reusing the same id lets the shared
flow validate committed replay or recover a published-but-uncommitted final
instead of creating another baseline. Without it, the transaction generates a
`req_*` identity; capture it from the response if you need to retry.

## Transaction sequence

Under an exclusive job lock:

1. Reload authoritative state from disk. Every production caller (including the
   `complete_baseline_transaction` compatibility wrapper) reloads; the supplied
   caller state is never authority. A stale caller transition is rejected against
   the authoritative baseline before mutation.
2. Recognise committed replay from the request-keyed commit ledger **before** the
   archived guard, so an identical historical retry on a `STOPPED_ARCHIVED` job
   returns the saved result unchanged while new archived work still rejects.
3. Reject new work for `STOPPED_ARCHIVED` jobs.
4. Discover all staging/final candidates before mutating; conflicting or
   incomplete evidence blocks.
5. Freeze the untouched ending snapshot (the pre-transition baseline, e.g. baseline 1).
6. Write the complete immutable evidence (request, operation, ending snapshot,
   hashes, semantic ending identity) into `.staging_<operation_id>`. This happens
   only on the new-operation path.
7. Publish by renaming staging to `baseline_<new_baseline:02d>`.
8. Commit state exactly once (`requirements_baseline`, artifact routing, change
   history, full reset, commit ledger) and then write the derived `receipt.json`.

## Full reset matrix

On a successful transition the committed state resets together: `completed_steps`
(to `prepare_request` when present), approvals/intervention, review state, failure
fields, retry/reject counters, plan revision and loop/replan contexts, plus
`step_usage`, `usage_summary`, `step_coders` and `revision_completions`. Declared
history is retained: `change_history`, `baseline_commits` and prior published
baseline directories.

## Evidence contract

The final directory holds four canonical artefacts, all required:

| Artefact | Canonical path |
|---|---|
| request | `baseline_XX/request.md` |
| operation | `baseline_XX/operation.json` |
| ending snapshot | `baseline_XX/ending_snapshot.json` |
| receipt | `baseline_XX/receipt.json` |

`request.md` keeps the same filename in staging and final phases (directory rename
preserves it). Required operation fields include `manifest_hash`,
`ending_snapshot_hash` and `ending_state_identity`; the receipt is derived and is
never authored independently.

## Replay and repair

Committed replay runs the **same phase-aware immutable validator** used by
resume and adoption, then enforces the required ledger/envelope/result schema:

- three-way identity (ledger key == envelope `request_id` == operation `request_id`);
- envelope `operation_id`/`manifest_hash` bound to the embedded operation;
- required field **types/schema**: `operation_id`, `request_id`, `group_name`,
  `job_id` are nonempty strings; `ending_baseline`/`new_baseline` and
  `result.baseline` are exact positive integers (bool/float rejected) with the
  transition formula;
- full embedded/disk operation equality;
- actual request/snapshot bytes, digests, semantic identity and all four paths;
- result schema and baseline binding;
- parsed ISO-8601 `committed_at` present in both envelope and result and equal.

Historical replay does not apply current eligibility or current ending-state
comparisons. Only after all checks may `repair_derived_receipt` atomically
replace a missing, truncated, invalid-encoding or mismatched receipt. Replay
never performs another state save, timestamp or side effect. Actual I/O errors
while reading/writing the receipt still propagate.

A ledger key that is **present but empty/null/malformed** is corruption of the
idempotency authority: it fails closed and never creates another operation. Only
an absent key enters the new/uncommitted flow.

## Discovery before decision

Both the staging set and the target final directory are inspected before any
branch is chosen. Multiple staging directories, incomplete staging, or a final
that coexists with staging are ambiguous and rejected before mutation.

## Failure modes

- **Published final, state commit failed (B06):** the next attempt adopts the
  final only if the incoming bytes/hash, all four canonical paths, manifest,
  snapshot digest/identity and the current semantic ending state match the frozen
  snapshot; otherwise it conflicts.
- **Resumed staging:** complete immutable evidence is validated exactly as
  replay/adoption would. Corrupt manifest/identity/digest or changed bytes is a
  conflict and is **not** repaired or normalized; only genuinely new staging is
  written.
- **Changed ending state:** adoption/resume conflicts rather than overwriting the
  frozen ending snapshot.
- **Multiple/incomplete staging or conflicting final:** blocks for operator
  intervention.
- **Archived job:** identical committed replay returns the saved result; new or
  uncommitted work rejects.

## Error transport

On failure, the raised exception carries `request_id`, `operation_id` (when
allocated) and `phase` attributes so a caller can retry with the same identity.
The identity/error boundary also covers lock acquisition: a lock timeout/open
error still exposes the generated retry id and phase. The original exception type
and message are preserved (a persistence error is never reported as success),
and an invocation releases only a lock it actually acquired. The CLI includes
these fields in its JSON error.

## Frozen ending state

The untouched authoritative raw ending state is deep-copied immediately after
reload, before `baseline_commits` or any other default/transition initialization.
Jobs that initially lack `baseline_commits` therefore do not gain that field in
the frozen ending snapshot; the isolated working state still initializes it for
the commit.

## Locking and limitations

- Unix uses `fcntl.flock`, released automatically on process exit.
- The no-`fcntl` fallback (Windows) uses atomic `O_CREAT|O_EXCL` creation, records
  the owner PID, reclaims files whose owner is provably dead (POSIX only), and
  waits at most 30 s before raising `TransactionConflictError`. On Windows a
  stale lock cannot be auto-reclaimed without a liveness probe, so the operator
  must remove the stale `.lockfile` manually. Windows behavior is not executed by
  this repository's CI.