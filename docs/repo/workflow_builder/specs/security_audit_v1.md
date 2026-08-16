# Workflow Specification: Security Audit v1

> Save to `docs/repo/workflow_builder/specs/security_audit_v1.md`.
> The workflow builder reads this document and generates the complete
> workflow package (workflow.toml, context_extensions.py, prompts, actions.py).
>
> **Key principle:** Describe WHAT the workflow does (domain problem, inputs,
> outputs, constraints). The builder infers HOW to structure it (step sequence,
> routing, role policies, gatekeepers, self-validation).

## Overview

**Workflow name:** `security_audit_v1`
**Label:** Security Audit v1
**Job prefix:** `SECAUD`
**Description:** Modular security audit of an agent-runner-v2 enabled repo. Runs one focused phase per execution — secrets scan, dependency audit, code pattern analysis, auth/access review, or infrastructure check. Produces a phase-specific findings report and remediation proposal.

## Purpose

Security audits are broad. Running a full audit at once produces overwhelming output and makes it hard to focus. This workflow splits security auditing into 5 independent phases, each targeting a specific attack surface. The user selects one phase per run, gets a deep focused analysis, and acts on the findings before running the next phase.

**Trigger:** Manual — user selects a phase and runs the workflow against a target repo.

**Outcome (per phase run):**
1. **Findings report** — specific issues found in the selected phase scope, with severity ratings and evidence
2. **Remediation proposal** — prioritized recommendations to fix findings

**Phases:**

| Phase | Name | Scope |
|-------|------|-------|
| 1 | Secrets & Credentials | Hardcoded API keys, tokens, passwords, secrets in source code; .env file exposure; credential handling patterns; git history leaks |
| 2 | Dependencies | Outdated packages with known CVEs; unpinned versions; unnecessary dependencies; supply chain risks |
| 3 | Code Patterns | Injection risks (SQL, command, path traversal); insecure deserialization; unsafe eval/exec; regex DoS; race conditions |
| 4 | Auth & Access | Token handling and storage; API key rotation; permission checks; auth flow weaknesses; session management |
| 5 | Infrastructure | File permission issues; network exposure; debug flags in production config; sensitive data in logs; insecure TLS/SSL settings |

## Workflow Type

**Mixed** — Action-driven scanning for deterministic checks (phase 1 secret patterns, phase 2 dependency versions), plus prompt-driven semantic analysis for all phases.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `AUDIT_SCOPE_FILE` | JSON config specifying which phase to run and target repo | Yes |

**AUDIT_SCOPE_FILE format:**

```json
{
  "phase": 1,
  "phase_name": "secrets_credentials",
  "target_repo_root": "D:\\MyProjectSpace\\01_Workflows\\agent-runner-v2",
  "exclude_patterns": [
    "tests/**",
    "docs/**",
    "*.md"
  ],
  "include_patterns": [
    "**/*.py",
    "**/*.toml",
    "**/*.json",
    "**/*.env*",
    "**/*.yaml",
    "**/*.yml"
  ]
}
```

**Phase values:** 1 (secrets), 2 (dependencies), 3 (code_patterns), 4 (auth), 5 (infrastructure)

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `TEST_CRITERIA_FILE` | `TEST_CRITERIA-{date}-{seq}_{slug}.md` | Acceptance criteria for the audit |
| `SCAN_INDEX_FILE` | `SCAN_INDEX-{date}-{seq}_{slug}.md` | Files scanned, scope coverage, exclusions applied |
| `FINDINGS_REPORT_FILE` | `SEC_FINDINGS_P{phase}-{date}-{seq}_{slug}.md` | Phase-specific findings with severity and evidence |
| `REMEDIATION_PROPOSAL_FILE` | `SEC_REMEDIATION_P{phase}-{date}-{seq}_{slug}.md` | Prioritized remediation recommendations |
| `REVIEW_FILE_SUGGESTED` | `SECAUD-REV-{date}-{seq}_{slug}.md` | Review of generated documents |
| `VALIDATION_REPORT_FILE` | `SECAUD-VALIDATION-{date}-{seq}_{slug}.md` | Structural validation report |

**Granularity rule:** One artifact key per logical file.

## Context Variables

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `TARGET_REPO_ROOT` | From AUDIT_SCOPE_FILE | Root of the repo to audit |
| `PHASE_DEFINITIONS_DIR` | `{workflow_package}/phases/` | Directory containing phase scope definition files |

## Quality Requirements

### Findings Report Must Include

- **Phase header** — which phase was run, scope description
- **Executive summary** — total findings by severity (critical/high/medium/low/info)
- **Per-finding entries:**
  - Severity: critical / high / medium / low / info
  - File path and line number(s)
  - Code snippet showing the issue
  - Description: what the issue is and why it's a security risk
  - Exploit scenario: how an attacker could leverage this
  - Recommended fix: specific code change or configuration update
- **Scope summary** — files scanned, files excluded, coverage percentage
- **Phase-specific metrics:**
  - Phase 1: secret pattern matches, .env files found, git history checks
  - Phase 2: total dependencies, outdated count, CVE count, unpinned count
  - Phase 3: pattern categories scanned, matches per category
  - Phase 4: auth endpoints found, token handling patterns, permission gaps
  - Phase 5: config files reviewed, permission issues, debug flag occurrences

### Remediation Proposal Must Include

- Prioritized by severity (critical first)
- Each item: finding reference, specific fix, effort estimate (S/M/L)
- Quick wins section: high-impact, low-effort fixes
- Long-term improvements: architectural changes needed

### Scanning Rules

- Respect `exclude_patterns` and `include_patterns` from AUDIT_SCOPE_FILE
- Always exclude: `.git/`, `__pycache__/`, `*.pyc`, `node_modules/`, `.venv/`
- Binary files: skip (don't try to scan images, compiled files)
- Large files (>1MB): skip with warning in scan index

## Custom Actions

### Action: scan_target_files

**Purpose:** Read the AUDIT_SCOPE_FILE config. Walk the target repo directory tree. Apply include/exclude patterns. Build a list of files to audit. For each file, record: path, size, extension, last modified. Classify files by relevance to the selected phase (e.g., phase 1 prioritizes .py, .env, .yaml, .json files; phase 2 focuses on requirements.txt, pyproject.toml, Pipfile).

**Phase 2 special:** Parse dependency files (requirements.txt, pyproject.toml) and extract package name + version pairs. Cross-reference with known vulnerability databases if available (or flag for LLM analysis).

**Returns:** APPROVED with file list and phase-relevant classification. REJECTED only if target repo doesn't exist.

### Action: pattern_scan_secrets

**Purpose:** Phase 1 only. Scan all target files for hardcoded secret patterns:
- API key patterns: `api_key = "..."`, `API_KEY = "..."`, `apikey: "..."`
- Token patterns: `token = "..."`, `Bearer ...`, `sk-...`, `ghp_...`, `gho_...`
- Password patterns: `password = "..."`, `passwd = "..."`, `pwd = "..."`
- Connection strings with embedded credentials
- Private key blocks: `-----BEGIN RSA PRIVATE KEY-----`
- .env files not in .gitignore
- Secrets in git history (if git repo): search committed files for above patterns

Exclude: test fixtures with obviously fake values (`test_key`, `dummy_*`, `example_*`), documentation examples clearly marked as examples.

**Returns:** APPROVED with list of potential secret matches (file, line, pattern type, matched text redacted). REJECTED only if no files to scan.

## Builder Instructions

**Domain phases:**

1. **TDD loop** — Generate test criteria for the audit, review, refine
2. **Scan** — Action-driven: discover target files, classify by phase relevance
3. **Phase-specific scan** — Action-driven (phase 1: secret pattern scan; phase 2: dependency extraction; phases 3-5: file collection only)
4. **Semantic analysis** — LLM reads scanned files in context of the selected phase's scope definition, identifies security issues, produces findings report
5. **Review findings** — Validate completeness and severity ratings
6. **Generate remediation proposal** — LLM produces prioritized fix recommendations
7. **Validate documents** — Structural validation
8. **Final review** — Human review

**Domain constraints:**

- Each phase is self-contained — running phase 1 does not require or produce data from other phases
- The phase scope definition (what to check, what patterns to look for) is injected into the LLM prompt context so the analysis is focused
- Findings must cite specific evidence (file path, line number, code snippet)
- Severity ratings must follow consistent criteria:
  - **Critical:** Immediate exploit risk, active danger (hardcoded production secrets, known CVE with public exploit)
  - **High:** Exploitable with some effort (missing auth checks, predictable tokens)
  - **Medium:** Potential risk if combined with other issues (overly broad permissions, missing rate limiting)
  - **Low:** Best practice violation (verbose error messages, missing security headers)
  - **Info:** Observation, not necessarily a vulnerability (dependency version, config pattern)

**Phase scope definitions:**

Each phase has a scope definition file that describes what to look for. These are injected into the LLM prompt context:

| Phase | Scope Definition Content |
|-------|--------------------------|
| 1 | Secret patterns (regex), credential handling best practices, .env security rules |
| 2 | Vulnerability check methodology, dependency risk categories, pinning rules |
| 3 | Injection pattern catalog, unsafe function list, path traversal patterns |
| 4 | Auth best practices checklist, token handling rules, permission model expectations |
| 5 | Infrastructure security checklist, debug flag patterns, logging rules, TLS requirements |

## Notes

- **One phase per run** — The workflow is designed for focused, incremental security auditing. User runs phase 1, fixes findings, then runs phase 2, etc.
- **Phase definitions are pluggable** — The scope definition files in `phases/` directory can be updated without changing the workflow. New patterns, new checks, new focus areas.
- **Not a replacement for specialized tools** — This workflow complements tools like `pip-audit`, `bandit`, `trivy`, `git-secrets`. It adds semantic understanding (why this is a problem, how to exploit it, how to fix it) that static tools don't provide.
- **Redaction** — Secret pattern matches in findings must redact the actual secret value. Show `api_key = "sk-****...****"` not the real key.
- **False positive management** — The LLM analysis step should filter false positives from the pattern scan (test fixtures, documentation examples, commented-out code).
