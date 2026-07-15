Review and audit steps must compare the generated governance docs against both the workflow prompt requirements and the actual repository structure.

When a reviewer rejects the docs, refinement must update only the owned core governance files and then return to the deterministic review path.

Validation is deterministic and should fail fast on ownership drift, stale mixed-doc assumptions, or bundle taxonomy mistakes before the final audit approves accuracy.
