---
template_id: "SYS-00-DS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-15T23:45:00+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "refine_layer1_governance_docs"
change_id: "00L1-20260715-c2f96104"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `refine_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation authority, structure rules, and update triggers for the four Layer 1 governance documents. It ensures these documents remain reusable across ecosystems and repositories without embedding repository-specific details.

## Audience Model

Layer 1 governance documents serve four audiences:

**Ecosystem Architects** — Define and maintain the reusable governance contract. They ensure Layer 1 docs remain generic and do not name concrete workflows or repository-specific artifacts.

**Repository Maintainers** — Implement Layer 1 governance within their repository via Layer 2 master-doc structures. They follow but do not modify Layer 1.

**Plugin Authors** — Create workflow bundles that conform to Layer 1 bundle taxonomy and runtime governance rules.

**Operators** — Manage steady-state runtime through the registry control plane, enforcing validation gates and change control.

## Document Set

The Layer 1 document set consists of exactly four documents:

| Document | Template ID | Ownership |
|----------|-------------|-----------|
| README.md | SYS-00-IDX | Ecosystem governance index |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Documentation authority and structure rules |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Bundle classes and packaging rules |
| RUNTIME_GOVERNANCE.md | SYS-00-RG | Steady-state runtime operating model |

No other documents belong to Layer 1. Repository-specific analysis, delivery scaffolds, codebase inventories, SDLC processes, and plugin workflow outputs are outside Layer 1 ownership.

## Architecture Baseline

Layer 1 documents define a three-layer model:

1. **Layer 1** — Ecosystem governance (these four documents)
2. **Layer 2** — Repository master-doc structure and operating model
3. **Layer 3** — Plugin workflow families and repo-local outputs

Layer 1 must remain generic. It must not name concrete workflow identifiers, repository-specific artifact names, or repository-specific scaffold names. All repo-derived outputs live under `docs/repo/` and are owned by Layer 2 or Layer 3.

## Conditional Standards

Layer 1 documents must satisfy the following standards:

**Frontmatter Requirements**
Every Layer 1 document must include YAML frontmatter with these exact fields: `template_id`, `version: "1.0.0"`, `doc_type`, `managed_by: "workflow-generated"`, `generated_at`, `workflow`, `step`, and `change_id`. The `workflow` and `step` fields identify which workflow generated the document.

**Workflow-Managed Banner**
Every Layer 1 document must include a banner immediately after frontmatter identifying the generating workflow and step, followed by a protection notice stating the file is workflow-generated and protected from manual edits.

**Required Sections**  
Each document must contain its required sections as defined in the validation action. Missing sections cause validation failure.

**Scope Purity**
Layer 1 documents must not contain concrete workflow identifiers in body text (beyond frontmatter and banner). They must not enumerate repo-derived artifact names.

**Forbidden Literals**  
Layer 1 documents must not contain unresolved placeholder token patterns or references to legacy delivery scaffold identifiers.

## Update Triggers

Layer 1 documents are updated when:

1. The ecosystem governance model changes at the architectural level
2. New bundle classes or ownership boundaries are introduced
3. Runtime governance contracts require revision
4. Validation rules are tightened or relaxed

Updates must preserve backward compatibility where possible. Breaking changes require a bundle migration plan.

## Validation

Layer 1 documents are validated by the `validate_layer1_governance_docs` action, which checks:

- Required section presence in each document
- Absence of concrete workflow identifiers in body text
- Absence of forbidden literals
- Explicit mention of `docs/repo/` as the repo-local output boundary in README.md
- Generic definition of plugin workflow bundles in BUNDLE_TAXONOMY.md and RUNTIME_GOVERNANCE.md
- Recognition of both single-workflow and multi-workflow plugin bundles in RUNTIME_GOVERNANCE.md

Validation failures produce a deterministic report listing each failed check with its path and detail.
