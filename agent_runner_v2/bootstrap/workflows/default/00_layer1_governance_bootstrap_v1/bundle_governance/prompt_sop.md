# Layer 1 Prompt SOP

## Purpose

This SOP defines how prompts in `00_layer1_governance_bootstrap_v1` must be
structured, reviewed, and validated.

The goal is to reduce prompt drift, make review criteria explicit, and ensure
deterministic validators can reject weak prompt edits before runtime.

## Authoring Rules

1. Prompts must be ASCII-only.
2. Prompts must be imperative, not advisory.
3. Prompts must define ownership boundaries explicitly.
4. Prompts must restate the exact file or artifact scope they govern.
5. Prompts must define both required behavior and forbidden behavior.
6. Prompts must end with explicit pre-return verification requirements.
7. Review and audit prompts must require citation of offending text when
   rejecting.

## Canonical Layout

Every Layer 1 prompt should follow this block order:

1. Purpose or role line
2. Read-first or inputs block
3. Scope or ownership rules
4. Required content or acceptance rules
5. Forbidden content or rejection rules
6. Pre-return verification checklist
7. Output contract or JSON schema

Not every prompt uses the same headings, but the logical order must remain
stable.

## Step Intent

- `01_generate_layer1_governance_docs.txt`
  Generates the four permanent Layer 1 documents and must define the target
  contract precisely.
- `02_review_layer1_governance_docs.txt`
  Performs scope and structure review and must reject with specific findings.
- `03_refine_layer1_governance_docs.txt`
  Applies direct corrections and must preserve scope while removing defects.
- `04_audit_layer1_governance_accuracy.txt`
  Performs final semantic audit against the Layer 1 model.

## Runtime Policy Guardrail

The Layer 1 prompt set must enforce this runtime policy consistently:

- The published bundle copy in the global runtime home is the canonical runtime
  source.
- Layer 1 docs must not define repo-local workflow fallback or dual-path
  workflow resolution.

## Quality Guardrail

The prompt set must reject:

- mojibake
- non-ASCII punctuation drift
- repo-local output ownership leakage into Layer 1
- repo-local workflow fallback language
- concrete workflow identifiers in document body text

## Validation Model

Prompt quality is enforced by `bundle_governance/prompt_contract.json` through
the shared workflow bundle validator.
