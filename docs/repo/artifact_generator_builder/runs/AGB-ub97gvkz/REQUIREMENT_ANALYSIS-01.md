---
doc_type: "requirement_analysis"
identity_locked: true
source: "codebase_intelligence.md"
generator_name: "Codebase Intelligence Generator"
codename: "codebase_intelligence"
version: "1.0"
analyzed_at: "2026-08-10"
---

# Requirement Analysis: Codebase Intelligence Generator

## Generator Identity

| Field            | Value                                                        |
|------------------|--------------------------------------------------------------|
| generator_name   | Codebase Intelligence Generator                              |
| codename         | codebase_intelligence                                        |
| input_type       | Codebase documentation (Rich Markdown) + source code (Python)|
| output_type      | Multiple intelligence reports (audience-specific meta content, structural health analysis, security audit findings) |
| version          | 1.0                                                          |

The generator consumes a complete codebase (documentation and Python source code) and produces at least three categories of intelligence reports from a single scan. The LLM infers the specific output artifact types based on the codebase content and structure.

## Input Specification

### IN-001: Source Codebase

- **Artifact key:** SOURCE_CODEBASE (inferred from requirement)
- **Type:** Composite (documentation files + Python source files)
- **Accepted formats:** Rich Markdown (.md) for documentation, Python (.py) for source code
- **Location:** Target repository (e.g., docs/repo/codebase/current/ for docs, agent_runner_v2/ for source)
- **Expected structure:**
  - Documentation files organized by category
  - Python package hierarchy with modules, imports, functions, and classes
  - Technical documentation, module docs, API references
  - Implementation code with imports, functions, and classes
- **Encoding:** UTF-8
- **Validation requirements:**
  - V-IN-001: All documentation and source files must be readable (UTF-8 encoding).
  - V-IN-002: Python source files must be syntactically valid (parseable by Python AST).
  - V-IN-003: Documentation files must be non-empty Markdown content.
  - V-IN-004: The codebase must contain at least one Python package directory and one documentation directory.

### Missing Information (Explicit Assumptions)

- The requirement document does not specify a maximum codebase size or file count limit.
- The requirement document does not specify how non-Python, non-Markdown files should be handled (ignored, partially parsed, etc.).
- The requirement document does not specify whether binary files, assets, or generated code should be excluded.
- The requirement document does not specify an artifact key name for the input.
- The requirement document does not specify minimum viable codebase size for analysis.

## Output Specification

### OUT-001: Audience-Specific Meta Content

- **Artifact key:** AUDIENCE_META_CONTENT (inferred from requirement)
- **Type:** Structured Markdown reports (multiple per run, one per audience)
- **Format/Structure:**
  - Different views of the codebase for different stakeholders (developers, architects, executives).
  - Content tailored by audience needs: technical depth, focus areas, tone.
  - Each audience definition specifies: focus_areas, section_structure, and tone.
  - Follows the audience-specific section_structure.
- **Quality requirements:**
  - Q-OUT-001: Content tone, focus, and structure must match the audience definition (audience fidelity constraint).
  - Q-OUT-002: Each audience report must be self-contained and readable without reference to source files.
  - Q-OUT-003: Content must be derived only from actual codebase content (no hallucination).

### OUT-002: Structural Health Analysis

- **Artifact key:** STRUCTURAL_HEALTH_REPORT (inferred from requirement)
- **Type:** Structured findings report with severity ratings
- **Format/Structure:**
  - Technical debt findings across 5 dimensions:
    - Dimension 1: Circular dependencies
    - Dimension 2: Coupling metrics
    - Dimension 3: Dead code identification
    - Dimension 4: Complexity analysis
    - Dimension 5: Import discipline
  - Each finding includes: severity, evidence (file paths, line numbers, code snippets), impact, and recommendations.
  - Each dimension is self-contained and can run independently.
  - Analysis scope (which dimensions to run) is controlled by JSON config.
- **Quality requirements:**
  - Q-OUT-004: All findings must cite specific file paths, line numbers, and code snippets (evidence-backed constraint).
  - Q-OUT-005: Import analysis must use Python AST, not regex (accuracy constraint).
  - Q-OUT-006: All findings must use consistent severity criteria: critical, high, medium, low, info.
  - Q-OUT-007: Each dimension finding must be self-contained (dimension independence constraint).

### OUT-003: Security Audit Findings

- **Artifact key:** SECURITY_AUDIT_REPORT (inferred from requirement)
- **Type:** Structured findings report with severity ratings
- **Format/Structure:**
  - Security issues across 5 phases:
    - Phase 1: Secrets detection (pattern scan for hardcoded secrets)
    - Phase 2: Dependencies audit (known vulnerable dependencies)
    - Phase 3: Code patterns scan (insecure coding patterns)
    - Phase 4: Authentication review (auth implementation issues)
    - Phase 5: Infrastructure check (deployment/configuration issues)
  - Each finding includes: severity, evidence, impact, and remediation recommendations.
  - Each phase is self-contained and can run independently.
  - Analysis scope (which phases to run) is controlled by JSON config.
- **Quality requirements:**
  - Q-OUT-008: All security findings must cite specific file paths, line numbers, and code snippets.
  - Q-OUT-009: Actual secret values must be redacted in findings (secret redaction constraint).
  - Q-OUT-010: All findings must use consistent severity criteria: critical, high, medium, low, info.
  - Q-OUT-011: Each phase finding must be self-contained (dimension independence constraint).

### Missing Information (Explicit Assumptions)

- The requirement document states the LLM infers output types from codebase content. The three output categories above are described as "sample examples" and "guidance, not requirements" in the spec. The actual output types are LLM-determined at runtime.
- The requirement document does not specify exact structure for audience definitions (focus_areas, section_structure, tone) beyond naming them.
- The requirement document does not specify exact metrics for each health dimension (e.g., what coupling threshold triggers a finding).
- The requirement document does not specify how severity is determined for each finding (criteria for critical vs. high vs. medium, etc.).
- The requirement document does not specify the output file format for each artifact (e.g., .md, .json, .html).
- The requirement document does not specify artifact key names; these are inferred.
- The requirement document does not specify how many audience definitions should be produced or what audiences are required.

## Transformation Requirements

### TR-001: Codebase Scan

Discover all documentation files and source code files in the target repository. Build a complete inventory of files by type, location, and category. This is the foundational step that feeds all subsequent transformations.

### TR-002: Import Graph Construction

Parse Python source files using AST (Abstract Syntax Tree) to extract all import statements. Build a directed dependency graph from the extracted imports. Resolve relative imports to absolute module paths. The resulting graph is the basis for structural health analysis (specifically circular dependency detection and coupling metrics).

### TR-003: Audience-Specific Content Generation

For each audience definition, read the codebase documentation filtered by the audience's focus_areas. Generate audience-tailored meta content following the audience's section_structure. Apply the audience's specified tone throughout the content. This produces OUT-001.

### TR-004: Health Dimension Analysis

For each enabled health dimension (controlled by JSON config), run structural analysis:
- Circular dependencies: Detect cycles in the import graph.
- Coupling: Compute coupling metrics between modules/packages.
- Dead code: Identify unused functions, classes, and modules.
- Complexity: Compute complexity metrics for functions/modules.
- Import discipline: Analyze import patterns for violations.

This produces OUT-002.

### TR-005: Security Phase Analysis

For each enabled security phase (controlled by JSON config), run security analysis:
- Secrets: Scan for hardcoded secrets, API keys, tokens, passwords.
- Dependencies: Audit dependencies for known vulnerabilities.
- Code patterns: Scan for insecure coding patterns.
- Authentication: Review authentication implementations.
- Infrastructure: Check deployment and configuration for security issues.

This produces OUT-003.

### TR-006: Findings Report Generation

Produce structured findings reports from the health and security analyses. Each finding must include:
- Severity rating (critical, high, medium, low, info).
- Evidence (specific file paths, line numbers, code snippets).
- Impact assessment.
- Remediation recommendations.

### TR-007: Output Validation

Ensure all generated reports are:
- Self-contained (readable without reference to source files).
- Evidence-backed (all findings cite specific evidence).
- Properly formatted (following audience definition or findings structure).
- Free of hallucinated content (only report what exists in the codebase).

### Assembly Steps (Inferred Pipeline)

1. Scan the codebase to discover all documentation and source files. Build file inventory.
2. Parse Python source files using AST. Extract all imports. Build directed dependency graph. Resolve relative imports.
3. Load audience definitions (from audiences/ directory or config). For each audience: filter codebase docs by focus_areas, generate content following section_structure and tone.
4. Load health dimension config (JSON). For each enabled dimension: run structural analysis against the import graph and codebase.
5. Load security phase config (JSON). For each enabled phase: run security analysis against the codebase.
6. Generate structured findings for health and security outputs. Apply consistent severity ratings. Cite evidence.
7. Validate all outputs against self-containment, evidence-backed, and formatting constraints.

## Constraints

### Performance Requirements

- C-PERF-001: No explicit latency or throughput requirements are stated in the requirement document.
- Note: Incremental analysis (re-analyzing only changed files) is listed as an extension point, not a current requirement.

### Format Requirements

- C-FMT-001: Input documentation must be Rich Markdown format.
- C-FMT-002: Input source code must be Python.
- C-FMT-003: Input encoding must be UTF-8.
- C-FMT-004: Import analysis must use Python AST, not regex (accuracy constraint).
- C-FMT-005: All findings must use consistent severity criteria: critical, high, medium, low, info (severity consistency constraint).
- C-FMT-006: Each report must be self-contained (readable without reference to source files).
- C-FMT-007: All findings must cite specific file paths, line numbers, and code snippets (evidence-backed constraint).

### Compatibility Requirements

- C-CMP-001: Only report what exists in the codebase; no invented issues (no hallucination constraint).
- C-CMP-002: Security findings must redact actual secret values (secret redaction constraint).
- C-CMP-003: Meta content tone, focus, and structure must match audience definition (audience fidelity constraint).
- C-CMP-004: Each health dimension and security phase is self-contained and can run independently (dimension independence constraint).
- C-CMP-005: Audience definitions are pluggable (drop .md file in audiences/ directory) (plugin extensibility constraint).
- C-CMP-006: Analysis scope (which dimensions/phases to run) is controlled by JSON config (configurable scope constraint).

## Extension Points

The following extension points are explicitly stated in the requirement document. They represent planned variations the generator architecture should accommodate.

### EP-001: Custom Audience Definitions

Add new audience types by dropping .md files in the audiences/ directory. The generator discovers audience definitions dynamically from this directory.

### EP-002: Custom Health Dimensions

Add new analysis dimensions by extending dimension definitions. Currently 5 dimensions are specified (circular dependencies, coupling, dead code, complexity, import discipline). The architecture should support adding more.

### EP-003: Custom Security Phases

Add new security check phases by extending phase definitions. Currently 5 phases are specified (secrets, dependencies, code patterns, auth, infrastructure). The architecture should support adding more.

### EP-004: Configurable Thresholds

Adjust complexity thresholds, coupling limits, and severity criteria. These are currently described as fixed but the generator should support configuration.

### EP-005: Multiple Output Formats

Support Markdown (default), JSON (for programmatic consumption), and HTML (for web rendering). Currently Markdown is the implied format.

### EP-006: Incremental Analysis

Re-analyze only changed files since last run. This would improve performance for large codebases where full re-analysis is costly.

## Self-Validation

| Check | Status | Notes |
|-------|--------|-------|
| Generator identity extracted | PASS | Name, codename, version, input/output types captured from frontmatter and body. |
| All input artifacts captured | PASS | Single composite input: codebase (Markdown docs + Python source). Missing details recorded as explicit assumptions. |
| All output artifacts captured | PASS | Three output categories: audience meta content, structural health analysis, security audit findings. Note that the spec says LLM infers output types; these are guidance examples. |
| Transformation requirements clear | PASS | Seven transformations identified: scan, import graph, audience analysis, health analysis, security analysis, findings generation, validation. |
| Constraints identified | PASS | Three categories: performance (none stated), format (7 constraints), compatibility (6 constraints). |
| Extension points identified | PASS | Six extension points: custom audiences, custom dimensions, custom phases, configurable thresholds, multiple formats, incremental analysis. All are stated in the requirement document. |
| No scope invention | PASS | All content traces to the requirement document or is explicitly labeled as an assumption. |
| ASCII-only | PASS | No em-dashes, curly quotes, or Unicode characters used. |

### Ambiguities and Gaps

The following items are ambiguous or missing from the requirement document and should be resolved before implementation:

1. Output types are LLM-inferred; the three categories listed in the spec are "guidance, not requirements." It is unclear what validation determines that the LLM has produced "at least 3 different types."
2. Audience definition structure (focus_areas, section_structure, tone) is mentioned but not formally specified.
3. Severity criteria (what qualifies as critical vs. high vs. medium vs. low vs. info) are not defined for any finding type.
4. Health dimension analysis details (specific metrics, thresholds, detection algorithms) are not specified beyond naming the five dimensions.
5. Security phase analysis details (specific patterns, tools, databases for dependency audit) are not specified beyond naming the five phases.
6. Output file formats are not specified (only Markdown is implied as default in extension points).
7. JSON config structure for controlling analysis scope is not defined.
8. The audiences/ directory structure and .md file format for audience definitions are not specified.
9. How relative Python imports are resolved in the import graph is not specified.
10. No minimum or maximum bounds on codebase size are stated.
11. Artifact key names are not declared; they are inferred from context.
