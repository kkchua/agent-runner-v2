---
codename: "codebase_intelligence"
title: "Codebase Intelligence Generator"
version: "1.0"
author: "kengk"
date: "2026-08-10"
description: "Generates multiple intelligence reports from codebase — audience-specific meta content, structural health analysis, and security audit findings."
---

# Codebase Intelligence Generator

## Overview

The Codebase Intelligence Generator transforms raw codebase documentation and source code into multiple types of intelligence reports. It produces three categories of outputs from a single codebase scan:

1. **Audience-Specific Meta Content** — Different views of the codebase for different stakeholders (developers, architects, executives)
2. **Structural Health Analysis** — Technical debt findings across 5 dimensions (circular dependencies, coupling, dead code, complexity, import discipline)
3. **Security Audit Findings** — Security issues across 5 phases (secrets, dependencies, code patterns, auth, infrastructure)

This generator is designed for teams who need comprehensive codebase intelligence but want to consume it in different ways — some need documentation, some need health metrics, some need security findings. The generator produces all three categories, and the consumer selects which reports to use.

**Target user:** Development teams, architects, security engineers, and executives who need different views of the same codebase.

**High-level workflow:** Scan codebase → Analyze structure → Generate audience-specific content → Generate health findings → Generate security findings → Publish reports

## Input Artifacts

### Source Codebase
- Format: Codebase documentation (Rich Markdown) + source code (Python)
- Location: Target repository (e.g., `docs/repo/codebase/current/` for docs, `agent_runner_v2/` for source)
- Structure: Documentation files organized by category + Python package hierarchy
- Content: Technical documentation, module docs, API references, implementation code with imports/functions/classes
- Encoding: UTF-8

The generator reads the entire codebase — both documentation and source code — and produces all intelligence reports from this single input.

## Output Artifacts

The generator MUST produce **at least 3 different types of output artifacts** from the codebase analysis. The LLM infers what these output types should be based on the codebase content and structure.

**Sample examples** of output types the generator can produce:

### Example Type 1: Audience-Specific Content
- Different views of the codebase for different stakeholders
- Content tailored by audience needs (technical depth, focus areas, tone)

### Example Type 2: Structural Analysis
- Code structure findings (dependencies, coupling, complexity)
- Technical debt identification with evidence and metrics

### Example Type 3: Security/Risk Analysis
- Security vulnerabilities and risk findings
- Compliance issues and remediation recommendations

The LLM decides the actual output artifact types, their names, structure, and content based on what it discovers in the codebase. The examples above are guidance, not requirements.

## Transformation Logic

The transformation process involves:

1. **Scan codebase** — Discover all documentation files and source code files, build inventory
2. **Build import graph** — Parse Python AST to extract all imports, build directed dependency graph, resolve relative imports
3. **Analyze per audience** — For each audience definition, read codebase docs filtered by focus_areas, generate audience-tailored meta content following section_structure
4. **Analyze health dimensions** — For each enabled dimension, run structural analysis (cycle detection, coupling metrics, dead code scan, complexity computation, import pattern analysis)
5. **Analyze security phases** — For each enabled phase, run security analysis (secret pattern scan, dependency audit, code pattern scan, auth review, infrastructure check)
6. **Generate findings reports** — Produce structured findings with severity, evidence, impact, recommendations
7. **Validate outputs** — Ensure all reports are self-contained, evidence-backed, properly formatted

## Constraints

- **Self-contained outputs** — Each report must be readable without reference to source files
- **Evidence-backed** — All findings must cite specific file paths, line numbers, code snippets
- **No hallucination** — Only report what exists in the codebase, no invented issues
- **Secret redaction** — Security findings must redact actual secret values
- **Audience fidelity** — Meta content tone, focus, and structure must match audience definition
- **Dimension independence** — Each health dimension and security phase is self-contained, can run independently
- **Plugin extensibility** — Audience definitions are pluggable (drop .md file in audiences/ directory)
- **Configurable scope** — Analysis scope (which dimensions/phases to run) is controlled by JSON config
- **AST-based analysis** — Import analysis uses Python AST, not regex, for accuracy
- **Severity consistency** — All findings use consistent severity criteria (critical/high/medium/low/info)

## Extension Points

The generator should support:
- **Custom audience definitions** — Add new audience types by dropping .md files in audiences/ directory
- **Custom health dimensions** — Add new analysis dimensions by extending dimension definitions
- **Custom security phases** — Add new security check phases by extending phase definitions
- **Configurable thresholds** — Adjust complexity thresholds, coupling limits, severity criteria
- **Multiple output formats** — Markdown (default), JSON (for programmatic consumption), HTML (for web rendering)
- **Incremental analysis** — Re-analyze only changed files since last run
