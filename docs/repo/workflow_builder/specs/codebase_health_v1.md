# Workflow Specification: Codebase Health v1

> Save to `docs/repo/workflow_builder/specs/codebase_health_v1.md`.
> The workflow builder reads this document and generates the complete
> workflow package (workflow.toml, context_extensions.py, prompts, actions.py).
>
> **Key principle:** Describe WHAT the workflow does (domain problem, inputs,
> outputs, constraints). The builder infers HOW to structure it (step sequence,
> routing, role policies, gatekeepers, self-validation).

## Overview

**Workflow name:** `codebase_health_v1`
**Label:** Codebase Health v1
**Job prefix:** `CBHEAL`
**Description:** Modular structural health audit of an agent-runner-v2 enabled codebase. Runs one focused dimension per execution — circular dependencies, module coupling, dead code detection, complexity analysis, or import discipline. Produces a dimension-specific findings report and improvement proposal.

## Purpose

Codebases degrade structurally over time. Circular imports creep in. Modules become tightly coupled. Dead code accumulates. Complexity grows unnoticed. These structural problems don't break builds but make the codebase harder to understand, test, and change.

This workflow splits structural health analysis into 5 independent dimensions, each targeting a specific category of technical debt. The user selects one dimension per run, gets a focused analysis with concrete evidence, and addresses findings before running the next dimension.

**Trigger:** Manual — user selects one dimension and runs the workflow against a single target repo.

**Scope:** One repo per run, one dimension per run. The user runs a focused analysis, addresses findings, then runs the next dimension.

**Outcome (per run):**
1. **Findings report** — specific structural issues found, with severity ratings and evidence
2. **Improvement proposal** — prioritized recommendations to fix findings

**Dimensions:**

| Dimension | Name | Scope |
|-----------|------|-------|
| 1 | Circular Dependencies | Import cycles between modules/packages; dependency direction violations; layered architecture breaches |
| 2 | Module Coupling | Fan-in/fan-out analysis; modules with too many dependents or dependencies; god modules; feature envy patterns |
| 3 | Dead Code | Unreachable functions/classes; unused imports; commented-out code blocks; orphan modules (no inbound references) |
| 4 | Complexity | Functions/classes exceeding complexity thresholds; deeply nested logic; oversized modules; duplicated patterns |
| 5 | Import Discipline | Wildcard imports; relative vs absolute consistency; bootstrap/generated boundary violations; cross-layer imports |

## Workflow Type

**Mixed** — Action-driven static analysis (import graph construction, dead code detection, complexity metrics), plus prompt-driven semantic analysis for coupling assessment and improvement recommendations.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `HEALTH_SCOPE_FILE` | JSON config specifying which dimension to run and target repo | Yes |

**HEALTH_SCOPE_FILE format:**

```json
{
  "dimension": 1,
  "dimension_name": "circular_dependencies",
  "target_repo_root": "D:\\MyProjectSpace\\01_Workflows\\agent-runner-v2",
  "source_dirs": [
    "agent_runner_v2"
  ],
  "exclude_patterns": [
    "tests/**",
    "docs/**",
    "bootstrap/**",
    "generated/**",
    "*.md"
  ],
  "include_patterns": [
    "**/*.py"
  ]
}
```

**Dimension values:** 1 (circular_deps), 2 (coupling), 3 (dead_code), 4 (complexity), 5 (import_discipline)

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `TEST_CRITERIA_FILE` | `TEST_CRITERIA-{date}-{seq}_{slug}.md` | Acceptance criteria for the health check |
| `SCAN_INDEX_FILE` | `SCAN_INDEX-{date}-{seq}_{slug}.md` | Files scanned, scope coverage, exclusions applied |
| `FINDINGS_REPORT_FILE` | `CBH_FINDINGS_D{dimension}-{date}-{seq}_{slug}.md` | Dimension-specific findings with severity and evidence |
| `IMPROVEMENT_PROPOSAL_FILE` | `CBH_IMPROVEMENT_D{dimension}-{date}-{seq}_{slug}.md` | Prioritized improvement recommendations |
| `REVIEW_FILE_SUGGESTED` | `CBHEAL-REV-{date}-{seq}_{slug}.md` | Review of generated documents |
| `VALIDATION_REPORT_FILE` | `CBHEAL-VALIDATION-{date}-{seq}_{slug}.md` | Structural validation report |

**Granularity rule:** One artifact key per logical file.

## Context Variables

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `TARGET_REPO_ROOT` | From HEALTH_SCOPE_FILE | Root of the repo to audit |
| `DIMENSION_DEFINITIONS_DIR` | `{workflow_package}/dimensions/` | Directory containing dimension scope definition files |

## Quality Requirements

### Findings Report Must Include

- **Dimension header** — which dimension was run, scope description
- **Executive summary** — total findings by severity (critical/high/medium/low/info)
- **Per-finding entries:**
  - Severity: critical / high / medium / low / info
  - File path and line number(s) (where applicable)
  - Evidence: code snippet, import chain, metric value
  - Description: what the issue is and why it's a structural problem
  - Impact: how this affects maintainability, testability, or reliability
  - Recommended fix: specific refactoring or reorganization
- **Scope summary** — files scanned, files excluded, total modules analyzed
- **Dimension-specific metrics:**
  - Dimension 1: cycle count, cycle length, packages involved, cycle paths
  - Dimension 2: top-10 highest fan-out modules, top-10 highest fan-in modules, coupling hotspots
  - Dimension 3: unused functions count, orphan modules, dead imports, estimated dead LOC
  - Dimension 4: functions over complexity threshold, average complexity, most complex modules
  - Dimension 5: wildcard import count, relative import inconsistencies, cross-layer violations

### Improvement Proposal Must Include

- Prioritized by severity (critical first)
- Each item: finding reference, specific fix, effort estimate (S/M/L)
- Quick wins section: high-impact, low-effort fixes
- Architectural observations: patterns that suggest deeper structural issues
- Dependency direction recommendations: what should depend on what

### Scanning Rules

- Respect `exclude_patterns` and `include_patterns` from HEALTH_SCOPE_FILE
- Always exclude: `.git/`, `__pycache__/`, `*.pyc`, `node_modules/`, `.venv/`, `bootstrap/`, `generated/`
- Only scan `.py` files (Python codebase)
- Parse imports using AST (not regex) for accuracy
- Follow relative imports to resolve actual module targets
- Handle both package imports (`from agent_runner_v2.x import y`) and relative imports (`from . import z`)

## Custom Actions

### Action: build_import_graph

**Purpose:** Read the HEALTH_SCOPE_FILE config. Walk the target source directories. For each `.py` file, parse the AST and extract all import statements (import, from...import, relative imports). Build a directed graph of module dependencies. Resolve relative imports to absolute module paths. Detect:
- Direct circular imports (A imports B, B imports A)
- Transitive circular imports (A→B→C→A)
- Import chains exceeding depth threshold
- Modules importing from layers they shouldn't (e.g., core importing from workflows)

Record for each module: imports list, imported_by list, package membership.

**Returns:** APPROVED with import graph as structured data (adjacency list + cycle report). REJECTED only if source directory doesn't exist.

### Action: scan_dead_code

**Purpose:** Dimension 3 only. Using the import graph from build_import_graph, identify:
- Functions/classes defined but never imported or referenced by any other module
- Within-module: functions/classes defined but never called within the same file (excluding public API exports)
- Unused imports (imported but never used in the file)
- Orphan modules: modules that no other module imports (and are not entry points)
- Commented-out code blocks (lines starting with `#` that contain valid Python syntax — heuristic)

Exclude from dead code detection:
- `__init__.py` re-exports (intentional public API surface)
- Entry points (run_agent.py, daemon_v2.py, etc.)
- Test files
- Files listed in HEALTH_SCOPE_FILE exclusions

**Returns:** APPROVED with dead code findings list. REJECTED only if no files to scan.

### Action: compute_complexity_metrics

**Purpose:** Dimension 4 only. For each `.py` file, parse AST and compute:
- Cyclomatic complexity per function/method (count branches: if, elif, for, while, except, and, or, with)
- Function length (line count)
- Class size (method count + total line count)
- Module size (total line count, function count, class count)
- Maximum nesting depth

Flag items exceeding thresholds:
- Function cyclomatic complexity > 10
- Function length > 50 lines
- Class with > 10 methods or > 200 lines
- Module with > 500 lines
- Nesting depth > 4

**Returns:** APPROVED with complexity metrics per module. REJECTED only if no files to scan.

## Builder Instructions

**Domain phases:**

1. **TDD loop** — Generate test criteria for the health check, review, refine
2. **Scan** — Action-driven: discover target files, build import graph (all dimensions need the graph)
3. **Dimension-specific scan** — Action-driven analysis:
   - Dimension 1: cycle detection on import graph
   - Dimension 2: fan-in/fan-out computation from import graph
   - Dimension 3: dead code scan (uses import graph for cross-module reference checking)
   - Dimension 4: complexity metric computation (AST-based)
   - Dimension 5: import pattern analysis (wildcard, relative, cross-layer)
4. **Semantic analysis** — LLM reads scan results in context of the selected dimension's scope definition, interprets findings, assesses impact, produces findings report
5. **Review findings** — Validate completeness and severity ratings
6. **Generate improvement proposal** — LLM produces prioritized recommendations
7. **Validate documents** — Structural validation
8. **Final review** — Human review

**Domain constraints:**

- Each dimension is self-contained — running dimension 1 does not require or produce data from other dimensions
- The import graph is built once per run and reused for dimensions that need it (1, 2, 3)
- Findings must cite specific evidence (file paths, line numbers, import chains, metric values)
- Severity ratings must follow consistent criteria:
  - **Critical:** Breaks or severely impedes development (import cycle causing runtime failures, god module blocking all changes)
  - **High:** Significant maintainability burden (long import chains, high coupling hotspots, large dead code clusters)
  - **Medium:** Moderate technical debt (occasional wildcard imports, functions slightly over complexity threshold)
  - **Low:** Best practice violation (unused imports, minor style inconsistencies)
  - **Info:** Observation, not necessarily a problem (module size within acceptable range, coupling within norms)

**Dimension scope definitions:**

Each dimension has a scope definition file describing what to analyze and thresholds to apply:

| Dimension | Scope Definition Content |
|-----------|--------------------------|
| 1 | Cycle detection rules, layer hierarchy definition, acceptable dependency directions |
| 2 | Coupling thresholds (fan-in/fan-out limits), hotspot identification rules, god module criteria |
| 3 | Dead code heuristics, exclusion rules, orphan detection criteria, commented-code detection patterns |
| 4 | Complexity thresholds per metric, module size limits, nesting depth rules |
| 5 | Import style rules (absolute vs relative), wildcard policy, cross-layer import rules |

## Notes

- **One dimension per run, one repo per run** — Designed for focused, incremental structural improvement. User runs dimension 1, fixes cycles, then runs dimension 2, etc.
- **Dimension definitions are pluggable** — Scope definition files in `dimensions/` directory can be updated without changing the workflow. New thresholds, new rules, new focus areas.
- **Complements TDD audit** — `tdd_audit_v1` checks test quality; this checks code structure. Together they cover "is the code well-tested?" and "is the code well-structured?"
- **AST-based, not regex** — Import analysis uses Python's `ast` module for accurate parsing. Regex-based import detection misses relative imports, conditional imports, and dynamic imports.
- **Not a linter replacement** — This complements tools like `pylint`, `flake8`, `mypy`. It adds structural analysis (import graphs, coupling metrics, dead code across modules) that linters don't provide.
- **Entry point awareness** — The scan must recognize entry points (CLI commands, daemon main loops) that are legitimately not imported by other modules.
